from __future__ import annotations

import csv
import json
import math
import traceback
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .config import VALID_METHODS, load_config
from .reporting import generate_campaign_report
from .trainer import aggregate_summaries, train


def _apply_overrides(config: dict[str, Any], overrides: dict[str, Any]) -> None:
    for dotted_key, value in overrides.items():
        keys = dotted_key.split(".")
        target = config
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value


def _resolve_project_path(path: str | Path, manifest_path: Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    beside_manifest = manifest_path.parent / candidate
    if beside_manifest.exists():
        return beside_manifest
    return manifest_path.parent.parent / candidate


def load_campaign_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path).resolve()
    with manifest_path.open(encoding="utf-8") as stream:
        manifest = yaml.safe_load(stream)
    if not isinstance(manifest, dict) or "campaign" not in manifest:
        raise ValueError("Le manifeste doit contenir une section campaign.")
    campaign = manifest["campaign"]
    required = {"name", "methods", "seeds", "experiments"}
    missing = required.difference(campaign)
    if missing:
        raise ValueError(f"Champs campaign manquants : {sorted(missing)}")
    if not campaign["experiments"]:
        raise ValueError("La campagne doit contenir au moins une expérience.")
    campaign.setdefault("contrasts", [["m5", "m6"]])
    campaign.setdefault("report_dir", f"outputs/reports/{campaign['name']}")
    campaign.setdefault("bootstrap_repeats", 10_000)
    campaign.setdefault("confidence", 0.95)
    manifest["_manifest_path"] = str(manifest_path)
    return manifest


def _experiment_contexts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    manifest_path = Path(manifest["_manifest_path"])
    campaign = manifest["campaign"]
    contexts = []
    seen_ids: set[str] = set()
    for specification in campaign["experiments"]:
        experiment_id = str(specification["id"])
        if experiment_id in seen_ids:
            raise ValueError(f"Identifiant d’expérience dupliqué : {experiment_id}")
        seen_ids.add(experiment_id)
        config_path = _resolve_project_path(specification["config"], manifest_path)
        config = deepcopy(load_config(config_path))
        _apply_overrides(config, specification.get("overrides", {}))
        if "experiment_name" in specification:
            config["experiment"]["name"] = str(specification["experiment_name"])
        else:
            config["experiment"]["name"] = f"{campaign['name']}/{experiment_id}"
        if "output_dir" in campaign:
            config["experiment"]["output_dir"] = str(
                _resolve_project_path(campaign["output_dir"], manifest_path)
            )
        else:
            config["experiment"]["output_dir"] = str(
                _resolve_project_path(config["experiment"]["output_dir"], manifest_path)
            )
        methods = [
            str(method).lower()
            for method in specification.get("methods", campaign["methods"])
        ]
        invalid_methods = set(methods).difference(VALID_METHODS)
        if invalid_methods:
            raise ValueError(
                f"Méthodes inconnues dans {experiment_id} : {sorted(invalid_methods)}"
            )
        seeds = [int(seed) for seed in specification.get("seeds", campaign["seeds"])]
        contrasts = [
            [str(pair[0]).lower(), str(pair[1]).lower()]
            for pair in specification.get("contrasts", campaign["contrasts"])
        ]
        unknown = {
            method for pair in contrasts for method in pair if method not in methods
        }
        if unknown:
            raise ValueError(
                f"Contraste de {experiment_id} utilisant une méthode absente : {sorted(unknown)}"
            )
        contexts.append({
            "id": experiment_id,
            "label": specification.get("label", experiment_id),
            "problem": config["problem"]["name"],
            "config_path": str(config_path),
            "config": config,
            "methods": methods,
            "seeds": seeds,
            "contrasts": contrasts,
            "summaries": [],
        })
    return contexts


def _summary_path(config: dict[str, Any], method: str, seed: int) -> Path:
    return (
        Path(config["experiment"]["output_dir"])
        / config["experiment"]["name"] / method / f"seed_{seed:05d}" / "summary.json"
    )


def _load_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        summary = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    metrics_path = path.parent / "metrics.csv"
    if not metrics_path.exists():
        return summary
    mapping = {
        "temporal_mean_gradient_distribution_tv": "gradient_distribution_tv",
        "temporal_mean_loss_distribution_tv": "loss_distribution_tv",
        "temporal_mean_physics_gradient_log_gap": "physics_gradient_log_gap",
    }
    missing = {target: source for target, source in mapping.items() if summary.get(target) is None}
    if not missing:
        return summary
    values: dict[str, list[float]] = {source: [] for source in missing.values()}
    try:
        with metrics_path.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                for source in values:
                    try:
                        number = float(row[source])
                    except (KeyError, TypeError, ValueError):
                        continue
                    if math.isfinite(number):
                        values[source].append(number)
    except OSError:
        return summary
    for target, source in missing.items():
        if values[source]:
            summary[target] = sum(values[source]) / len(values[source])
    return summary


def _execute_task(task: tuple[str, dict[str, Any], str, int]) -> dict[str, Any]:
    experiment_id, config, method, seed = task
    try:
        return {"experiment_id": experiment_id, "summary": train(config, method, seed)}
    except Exception as error:  # conserver la campagne et rendre l'échec visible
        return {
            "experiment_id": experiment_id,
            "summary": {
                "status": "failed",
                "failure_reason": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "method": method,
                "problem": config["problem"]["name"],
                "seed": seed,
                "run_dir": str(_summary_path(config, method, seed).parent.resolve()),
            },
        }


def run_campaign(
    manifest_path: str | Path,
    workers: int = 1,
    report_only: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    if workers <= 0:
        raise ValueError("workers doit être strictement positif.")
    manifest = load_campaign_manifest(manifest_path)
    campaign = manifest["campaign"]
    contexts = _experiment_contexts(manifest)
    tasks: list[tuple[str, dict[str, Any], str, int]] = []
    reused_successes = 0

    for context in contexts:
        for seed in context["seeds"]:
            for method in context["methods"]:
                existing = None if force else _load_summary(
                    _summary_path(context["config"], method, seed)
                )
                if existing is not None and existing.get("status") == "succeeded":
                    context["summaries"].append(existing)
                    reused_successes += 1
                elif existing is not None and report_only:
                    context["summaries"].append(existing)
                elif not report_only:
                    tasks.append((context["id"], context["config"], method, seed))

    results: list[dict[str, Any]] = []
    if tasks:
        if workers == 1:
            results = [_execute_task(task) for task in tasks]
        else:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                results = list(executor.map(_execute_task, tasks, chunksize=1))
        by_id = {context["id"]: context for context in contexts}
        for result in results:
            by_id[result["experiment_id"]]["summaries"].append(result["summary"])

    for context in contexts:
        context["summaries"].sort(
            key=lambda summary: (str(summary.get("method")), int(summary.get("seed", -1)))
        )
        aggregate_summaries(
            context["config"], context["methods"], context["seeds"], context["summaries"]
        )

    report_dir = _resolve_project_path(
        campaign["report_dir"], Path(manifest["_manifest_path"])
    )
    report = generate_campaign_report(
        str(campaign["name"]), report_dir, contexts,
        bootstrap_repeats=int(campaign["bootstrap_repeats"]),
        confidence=float(campaign["confidence"]),
    )
    resolved_manifest = deepcopy(manifest)
    resolved_manifest.pop("_manifest_path", None)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "campaign.resolved.yaml").write_text(
        yaml.safe_dump(resolved_manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    failures = [
        {
            "experiment": context["id"],
            "method": summary.get("method"),
            "seed": summary.get("seed"),
            "reason": summary.get("failure_reason"),
        }
        for context in contexts for summary in context["summaries"]
        if summary.get("status") != "succeeded"
    ]
    missing = []
    for context in contexts:
        present = {
            (summary.get("method"), summary.get("seed")) for summary in context["summaries"]
        }
        missing.extend(
            {"experiment": context["id"], "method": method, "seed": seed}
            for method in context["methods"] for seed in context["seeds"]
            if (method, seed) not in present
        )
    result = {
        **report,
        "new_runs": len(tasks),
        "reused_runs": int(reused_successes),
        "failures": failures,
        "missing_runs": missing,
    }
    (report_dir / "campaign_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result
