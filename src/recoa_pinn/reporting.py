from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METHOD_LABELS = {
    "m0": "M0 — PINN",
    "m1": "M1 — poids adaptatifs",
    "m3": "M3 — échantillonnage adaptatif",
    "m5": "M5 — co-adaptatif couplé",
    "m6": "M6 — référence fixe",
    "m7u": "M7U — rééchantillonnage témoin",
    "m7": "M7 — correction de mesure",
    "vw": "VW — volume KDE",
    "vwca": "VW-CA — volume KDE co-adaptatif",
    "vrba": "vRBA — attention variationnelle",
}
METHOD_COLORS = {
    "m0": "#4C78A8",
    "m1": "#F58518",
    "m3": "#54A24B",
    "m5": "#E45756",
    "m6": "#7A5195",
    "m7u": "#B279A2",
    "m7": "#009E73",
    "vw": "#56B4E9",
    "vwca": "#D55E00",
    "vrba": "#CC79A7",
}
METRICS = {
    "relative_l2": "Erreur relative L2",
    "max_abs_error": "Erreur absolue maximale",
    "controller_weight_tv_per_update": "Variation des poids / mise à jour",
    "temporal_mean_gradient_distribution_tv": "Décalage moyen des gradients",
    "temporal_mean_physics_gradient_log_gap": "Écart logarithmique du gradient physique",
    "elapsed_seconds": "Temps (s)",
    "residual_evaluations": "Évaluations du résidu",
    "importance_effective_sample_fraction": "Fraction ESS des poids d'importance",
    "importance_weight_mean": "Poids d'importance moyen",
    "importance_weight_max": "Poids d'importance maximal",
    "kde_pairwise_distance_evaluations": "Distances deux-à-deux KDE",
    "vrba_attention_effective_sample_fraction": "Fraction ESS de l'attention vRBA",
    "vrba_multiplier_mean": "Multiplicateur vRBA moyen",
    "vrba_multiplier_max": "Multiplicateur vRBA maximal",
}


def _metric_value(summary: dict[str, Any], metric: str) -> Any:
    value = summary.get(metric)
    if value is not None:
        return value
    importance_mapping = {
        "importance_effective_sample_fraction": "effective_sample_fraction",
        "importance_weight_mean": "mean",
        "importance_weight_max": "maximum",
    }
    nested_key = importance_mapping.get(metric)
    if nested_key is not None:
        return summary.get("importance_statistics", {}).get(nested_key)
    return None


def _finite(values: Iterable[Any]) -> np.ndarray:
    result: list[float] = []
    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            result.append(number)
    return np.asarray(result, dtype=np.float64)


def _stable_seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "little")


def _bootstrap_median_ci(
    values: np.ndarray, repeats: int, confidence: float, key: str
) -> tuple[float | None, float | None]:
    if values.size == 0:
        return None, None
    if values.size == 1:
        value = float(values[0])
        return value, value
    generator = np.random.default_rng(_stable_seed(key))
    indices = generator.integers(0, values.size, size=(repeats, values.size))
    medians = np.median(values[indices], axis=1)
    alpha = 1.0 - confidence
    low, high = np.quantile(medians, [alpha / 2.0, 1.0 - alpha / 2.0])
    return float(low), float(high)


def _two_sided_sign_test(differences: np.ndarray) -> float | None:
    nonzero = differences[differences != 0.0]
    n = int(nonzero.size)
    if n == 0:
        return None
    smaller_side = min(int(np.sum(nonzero < 0.0)), int(np.sum(nonzero > 0.0)))
    probability = 2.0 * sum(math.comb(n, k) for k in range(smaller_side + 1)) / (2**n)
    return min(1.0, probability)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _format_number(value: Any, digits: int = 4) -> str:
    if value is None:
        return "—"
    number = float(value)
    if not math.isfinite(number):
        return "—"
    if number == 0.0:
        return "0"
    if abs(number) < 1e-3 or abs(number) >= 1e4:
        return f"{number:.2e}"
    return f"{number:.{digits}f}"


def _latex_escape(value: Any) -> str:
    text = str(value)
    for source, replacement in (
        ("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"),
        ("&", r"\&"), ("#", r"\#"), ("{", r"\{"), ("}", r"\}"),
    ):
        text = text.replace(source, replacement)
    return text


def _flatten_run(experiment: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    observations = summary.get("observations", {})
    return {
        "experiment": experiment["id"],
        "label": experiment.get("label", experiment["id"]),
        "problem": summary.get("problem", experiment.get("problem")),
        "method": summary.get("method"),
        "seed": summary.get("seed"),
        "status": summary.get("status"),
        "failure_reason": summary.get("failure_reason"),
        **{metric: _metric_value(summary, metric) for metric in METRICS},
        "bias_concentration_correlation": summary.get("bias_concentration_correlation"),
        "n_observations": observations.get("effective_count", 0),
        "noise_kind": observations.get("noise_kind", "none"),
        "noise_level": observations.get("noise_level", 0.0),
        "run_dir": summary.get("run_dir"),
    }


def _method_summary_rows(
    experiments: list[dict[str, Any]], repeats: int, confidence: float
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experiment in experiments:
        successful = [
            summary for summary in experiment["summaries"]
            if summary.get("status") == "succeeded"
        ]
        for method in experiment["methods"]:
            group = [summary for summary in successful if summary.get("method") == method]
            row: dict[str, Any] = {
                "experiment": experiment["id"],
                "label": experiment.get("label", experiment["id"]),
                "problem": experiment.get("problem"),
                "method": method,
                "n_success": len(group),
                "n_expected": len(experiment["seeds"]),
            }
            for metric in METRICS:
                values = _finite(_metric_value(summary, metric) for summary in group)
                low, high = _bootstrap_median_ci(
                    values, repeats, confidence, f"{experiment['id']}:{method}:{metric}"
                )
                row[f"{metric}_median"] = float(np.median(values)) if values.size else None
                row[f"{metric}_q1"] = float(np.quantile(values, 0.25)) if values.size else None
                row[f"{metric}_q3"] = float(np.quantile(values, 0.75)) if values.size else None
                row[f"{metric}_ci_low"] = low
                row[f"{metric}_ci_high"] = high
            rows.append(row)
    return rows


def _paired_summary_rows(
    experiments: list[dict[str, Any]], repeats: int, confidence: float
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experiment in experiments:
        successful = [
            summary for summary in experiment["summaries"]
            if summary.get("status") == "succeeded"
        ]
        indexed = {
            (summary.get("method"), int(summary["seed"])): summary
            for summary in successful if summary.get("seed") is not None
        }
        for first, second in experiment["contrasts"]:
            paired_seeds = [
                seed for seed in experiment["seeds"]
                if (first, seed) in indexed and (second, seed) in indexed
            ]
            for metric in METRICS:
                pairs = []
                for seed in paired_seeds:
                    first_value = _metric_value(indexed[(first, seed)], metric)
                    second_value = _metric_value(indexed[(second, seed)], metric)
                    values = _finite([first_value, second_value])
                    if values.size == 2:
                        pairs.append((seed, float(first_value), float(second_value)))
                differences = np.asarray(
                    [second_value - first_value for _, first_value, second_value in pairs],
                    dtype=np.float64,
                )
                low, high = _bootstrap_median_ci(
                    differences, repeats, confidence,
                    f"{experiment['id']}:{first}:{second}:{metric}",
                )
                rows.append({
                    "experiment": experiment["id"],
                    "label": experiment.get("label", experiment["id"]),
                    "problem": experiment.get("problem"),
                    "first_method": first,
                    "second_method": second,
                    "contrast": f"{second}_minus_{first}",
                    "metric": metric,
                    "n_pairs": len(pairs),
                    "median_difference": (
                        float(np.median(differences)) if differences.size else None
                    ),
                    "ci_low": low,
                    "ci_high": high,
                    "second_win_fraction": (
                        float(np.mean(differences < 0.0)) if differences.size else None
                    ),
                    "two_sided_sign_test_p": _two_sided_sign_test(differences),
                    "differences_by_seed": json.dumps(
                        {str(seed): second_value - first_value
                         for seed, first_value, second_value in pairs},
                        sort_keys=True,
                    ),
                })
    return rows


def _write_latex_tables(
    table_dir: Path, method_rows: list[dict[str, Any]], paired_rows: list[dict[str, Any]]
) -> None:
    table_dir.mkdir(parents=True, exist_ok=True)
    main_lines = [
        r"\begin{tabular}{lllrrrr}", r"\toprule",
        r"Expérience & Méthode & $n$ & Erreur $L_2$ & Stabilité & Temps (s) & Résidus \\",
        r"\midrule",
    ]
    for row in method_rows:
        error = (
            f"{_format_number(row['relative_l2_median'])} "
            f"[{_format_number(row['relative_l2_q1'])}, {_format_number(row['relative_l2_q3'])}]"
        )
        main_lines.append(
            " & ".join([
                _latex_escape(row["label"]), _latex_escape(row["method"]),
                f"{row['n_success']}/{row['n_expected']}", error,
                _format_number(row["controller_weight_tv_per_update_median"]),
                _format_number(row["elapsed_seconds_median"], 2),
                _format_number(row["residual_evaluations_median"], 0),
            ]) + r" \\"
        )
    main_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (table_dir / "table_main_results.tex").write_text(
        "\n".join(main_lines) + "\n", encoding="utf-8"
    )

    contrast_lines = [
        r"\begin{tabular}{llllrrrr}", r"\toprule",
        r"Expérience & Contraste & Métrique & $n$ & Médiane $\Delta$ & IC 95\% & Victoires & $p$ \\",
        r"\midrule",
    ]
    for row in paired_rows:
        if row["metric"] not in {"relative_l2", "controller_weight_tv_per_update"}:
            continue
        interval = f"[{_format_number(row['ci_low'])}, {_format_number(row['ci_high'])}]"
        wins = (
            "—" if row["second_win_fraction"] is None
            else f"{100.0 * row['second_win_fraction']:.0f}\\%"
        )
        contrast_lines.append(
            " & ".join([
                _latex_escape(row["label"]), _latex_escape(row["contrast"]),
                _latex_escape(row["metric"]), str(row["n_pairs"]),
                _format_number(row["median_difference"]), interval, wins,
                _format_number(row["two_sided_sign_test_p"], 3),
            ]) + r" \\"
        )
    contrast_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (table_dir / "table_paired_contrasts.tex").write_text(
        "\n".join(contrast_lines) + "\n", encoding="utf-8"
    )


def _method_color(method: str) -> str:
    return METHOD_COLORS.get(method, "#777777")


def _save_figure(fig: plt.Figure, base_path: Path) -> list[str]:
    base_path.parent.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in (".png", ".pdf"):
        path = base_path.with_suffix(suffix)
        fig.savefig(path, dpi=300, bbox_inches="tight")
        paths.append(str(path.resolve()))
    plt.close(fig)
    return paths


def _boxplot(
    experiments: list[dict[str, Any]], metric: str, output: Path
) -> list[str] | None:
    groups: list[np.ndarray] = []
    positions: list[float] = []
    colors: list[str] = []
    centers: list[float] = []
    labels: list[str] = []
    position = 1.0
    for experiment in experiments:
        start = position
        for method in experiment["methods"]:
            values = _finite(
                _metric_value(summary, metric) for summary in experiment["summaries"]
                if summary.get("status") == "succeeded" and summary.get("method") == method
            )
            if values.size:
                groups.append(values)
                positions.append(position)
                colors.append(_method_color(method))
                position += 1.0
        if position > start:
            centers.append((start + position - 1.0) / 2.0)
            labels.append(experiment.get("label", experiment["id"]))
            position += 0.8
    if not groups:
        return None
    fig, ax = plt.subplots(figsize=(max(8.0, 1.0 + 0.65 * len(groups)), 5.2))
    artists = ax.boxplot(
        groups, positions=positions, patch_artist=True, widths=0.68,
        medianprops={"color": "black", "linewidth": 1.4},
        whiskerprops={"linewidth": 1.0}, capprops={"linewidth": 1.0},
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.45},
    )
    for patch, color in zip(artists["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.72)
    ax.set_xticks(centers, labels, rotation=20, ha="right")
    ax.set_ylabel(METRICS[metric])
    ax.grid(axis="y", alpha=0.25)
    if metric in {"relative_l2", "elapsed_seconds", "residual_evaluations"} and all(
        np.all(group > 0.0) for group in groups
    ):
        ax.set_yscale("log")
    handles = [
        plt.Line2D([0], [0], marker="s", linestyle="", color=_method_color(method),
                   label=METHOD_LABELS.get(method, method), markersize=8)
        for method in sorted({method for experiment in experiments for method in experiment["methods"]})
    ]
    ax.legend(handles=handles, loc="best", fontsize=8, frameon=False)
    return _save_figure(fig, output)


def _forest_plot(paired_rows: list[dict[str, Any]], output: Path) -> list[str] | None:
    rows = [
        row for row in paired_rows
        if row["metric"] == "relative_l2" and row["median_difference"] is not None
    ]
    if not rows:
        return None
    labels = [f"{row['label']} · {row['contrast']}" for row in rows]
    estimates = np.asarray([row["median_difference"] for row in rows])
    lows = np.asarray([row["ci_low"] for row in rows])
    highs = np.asarray([row["ci_high"] for row in rows])
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.5, max(3.5, 0.48 * len(rows) + 1.2)))
    ax.errorbar(
        estimates, y, xerr=np.vstack((estimates - lows, highs - estimates)),
        fmt="o", color="#334E68", ecolor="#829AB1", capsize=3,
    )
    ax.axvline(0.0, color="black", linewidth=1.0, linestyle="--")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel(r"Médiane appariée $\Delta L_2$ (seconde − première)")
    ax.grid(axis="x", alpha=0.25)
    return _save_figure(fig, output)


def _cost_accuracy_plot(method_rows: list[dict[str, Any]], output: Path) -> list[str] | None:
    rows = [
        row for row in method_rows
        if row["relative_l2_median"] is not None and row["residual_evaluations_median"] is not None
    ]
    if not rows:
        return None
    fig, ax = plt.subplots(figsize=(8.0, 5.5))
    for row in rows:
        x = row["residual_evaluations_median"]
        y = row["relative_l2_median"]
        ax.scatter(x, y, s=48, color=_method_color(row["method"]), alpha=0.85)
        ax.annotate(
            f"{row['experiment']}:{row['method']}", (x, y), xytext=(4, 4),
            textcoords="offset points", fontsize=7,
        )
    if all(float(row["residual_evaluations_median"]) > 0.0 for row in rows):
        ax.set_xscale("log")
    if all(float(row["relative_l2_median"]) > 0.0 for row in rows):
        ax.set_yscale("log")
    ax.set_xlabel(METRICS["residual_evaluations"])
    ax.set_ylabel(METRICS["relative_l2"])
    ax.grid(alpha=0.25)
    return _save_figure(fig, output)


def _read_metric_trajectory(path: Path, field: str) -> dict[int, float]:
    trajectory: dict[int, float] = {}
    if not path.exists():
        return trajectory
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            try:
                step, value = int(row["step"]), float(row[field])
            except (KeyError, TypeError, ValueError):
                continue
            if math.isfinite(value):
                trajectory[step] = value
    return trajectory


def _convergence_plot(experiment: dict[str, Any], output: Path) -> list[str] | None:
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    plotted = False
    for method in experiment["methods"]:
        trajectories = []
        for summary in experiment["summaries"]:
            if summary.get("status") != "succeeded" or summary.get("method") != method:
                continue
            run_dir = summary.get("run_dir")
            if run_dir:
                trajectory = _read_metric_trajectory(Path(run_dir) / "metrics.csv", "relative_l2")
                if trajectory:
                    trajectories.append(trajectory)
        steps = sorted({step for trajectory in trajectories for step in trajectory})
        if not steps:
            continue
        medians, lows, highs, kept_steps = [], [], [], []
        for step in steps:
            values = _finite(trajectory.get(step) for trajectory in trajectories)
            if values.size:
                kept_steps.append(step)
                medians.append(float(np.median(values)))
                lows.append(float(np.quantile(values, 0.25)))
                highs.append(float(np.quantile(values, 0.75)))
        color = _method_color(method)
        ax.plot(kept_steps, medians, label=METHOD_LABELS.get(method, method), color=color)
        ax.fill_between(kept_steps, lows, highs, color=color, alpha=0.16)
        plotted = True
    if not plotted:
        plt.close(fig)
        return None
    ax.set_xlabel("Étape d’entraînement")
    ax.set_ylabel(METRICS["relative_l2"])
    ax.set_yscale("log")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, frameon=False)
    ax.set_title(experiment.get("label", experiment["id"]))
    return _save_figure(fig, output)


def _write_markdown_report(
    path: Path, campaign_name: str, experiments: list[dict[str, Any]],
    method_rows: list[dict[str, Any]], paired_rows: list[dict[str, Any]],
    generated_figures: list[str], confidence: float,
) -> None:
    expected = sum(len(exp["methods"]) * len(exp["seeds"]) for exp in experiments)
    succeeded = sum(
        summary.get("status") == "succeeded"
        for exp in experiments for summary in exp["summaries"]
    )
    lines = [
        f"# Rapport automatique — {campaign_name}", "",
        "## Complétude", "",
        f"- Exécutions réussies : **{succeeded}/{expected}**.",
        f"- Intervalles : bootstrap apparié/non apparié à **{100 * confidence:.0f} %**.",
        "- Une différence négative signifie que la seconde méthode a une valeur plus faible.",
        "",
        "## Résultats principaux", "",
        "| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in method_rows:
        error = (
            f"{_format_number(row['relative_l2_median'])} "
            f"[{_format_number(row['relative_l2_q1'])}, {_format_number(row['relative_l2_q3'])}]"
        )
        lines.append(
            f"| {row['label']} | {row['method']} | {row['n_success']}/{row['n_expected']} "
            f"| {error} | {_format_number(row['controller_weight_tv_per_update_median'])} "
            f"| {_format_number(row['elapsed_seconds_median'], 2)} |"
        )
    lines.extend([
        "", "## Contrastes appariés principaux", "",
        "| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in paired_rows:
        if row["metric"] != "relative_l2":
            continue
        interval = f"[{_format_number(row['ci_low'])}, {_format_number(row['ci_high'])}]"
        wins = (
            "—" if row["second_win_fraction"] is None
            else f"{100.0 * row['second_win_fraction']:.0f} %"
        )
        lines.append(
            f"| {row['label']} | {row['contrast']} | {row['n_pairs']} "
            f"| {_format_number(row['median_difference'])} | {interval} | {wins} "
            f"| {_format_number(row['two_sided_sign_test_p'], 3)} |"
        )
    lines.extend([
        "", "## Fichiers produits", "",
        "- `data/runs.csv` : une ligne par entraînement ;",
        "- `tables/method_summary.csv` : statistiques par méthode ;",
        "- `tables/paired_summary.csv` : contrastes appariés par germe ;",
        "- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;",
        "- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.",
        "", "## Règle d’interprétation", "",
        "Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum "
        "un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, "
        "l’absence de runs manquants et un coût comparable.", "",
        f"Figures créées : **{len(generated_figures)} fichiers** (PNG et PDF).", "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_campaign_report(
    campaign_name: str,
    report_dir: str | Path,
    experiments: list[dict[str, Any]],
    bootstrap_repeats: int = 10_000,
    confidence: float = 0.95,
) -> dict[str, Any]:
    if bootstrap_repeats <= 0:
        raise ValueError("bootstrap_repeats doit être strictement positif.")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence doit être compris strictement entre 0 et 1.")
    root = Path(report_dir)
    data_dir, table_dir, figure_dir = root / "data", root / "tables", root / "figures"
    root.mkdir(parents=True, exist_ok=True)

    run_rows = [
        _flatten_run(experiment, summary)
        for experiment in experiments for summary in experiment["summaries"]
    ]
    method_rows = _method_summary_rows(experiments, bootstrap_repeats, confidence)
    paired_rows = _paired_summary_rows(experiments, bootstrap_repeats, confidence)
    _write_csv(data_dir / "runs.csv", run_rows)
    _write_csv(table_dir / "method_summary.csv", method_rows)
    _write_csv(table_dir / "paired_summary.csv", paired_rows)
    _write_latex_tables(table_dir, method_rows, paired_rows)

    generated_figures: list[str] = []
    for metric, name in (
        ("relative_l2", "relative_l2_boxplot"),
        ("controller_weight_tv_per_update", "stability_boxplot"),
        ("elapsed_seconds", "training_time_boxplot"),
    ):
        paths = _boxplot(experiments, metric, figure_dir / name)
        if paths:
            generated_figures.extend(paths)
    paths = _forest_plot(paired_rows, figure_dir / "paired_relative_l2_forest")
    if paths:
        generated_figures.extend(paths)
    paths = _cost_accuracy_plot(method_rows, figure_dir / "cost_accuracy")
    if paths:
        generated_figures.extend(paths)
    for experiment in experiments:
        paths = _convergence_plot(
            experiment, figure_dir / f"convergence_{experiment['id']}"
        )
        if paths:
            generated_figures.extend(paths)

    report_path = root / "REPORT.md"
    _write_markdown_report(
        report_path, campaign_name, experiments, method_rows, paired_rows,
        generated_figures, confidence,
    )
    report = {
        "campaign": campaign_name,
        "report_dir": str(root.resolve()),
        "n_experiments": len(experiments),
        "expected_runs": sum(
            len(experiment["methods"]) * len(experiment["seeds"])
            for experiment in experiments
        ),
        "successful_runs": sum(
            summary.get("status") == "succeeded"
            for experiment in experiments for summary in experiment["summaries"]
        ),
        "files": {
            "report": str(report_path.resolve()),
            "runs_csv": str((data_dir / "runs.csv").resolve()),
            "method_summary_csv": str((table_dir / "method_summary.csv").resolve()),
            "paired_summary_csv": str((table_dir / "paired_summary.csv").resolve()),
            "figures": generated_figures,
        },
    }
    (root / "report_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report
