from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


VALID_METHODS = {
    "m0", "m1", "m3", "m5", "m6", "m7u", "m7", "vw", "vwca", "vrba"
}
VALID_PROBLEMS = {"burgers", "allen_cahn", "helmholtz", "wave"}


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    required = {"experiment", "problem", "model", "training", "adaptation", "evaluation"}
    missing = required.difference(config)
    if missing:
        raise ValueError(f"Sections de configuration manquantes : {sorted(missing)}")
    if config["problem"].get("name") not in VALID_PROBLEMS:
        raise ValueError(f"problem.name doit appartenir à {sorted(VALID_PROBLEMS)}.")
    if int(config["training"]["steps"]) <= 0:
        raise ValueError("training.steps doit être strictement positif.")
    for key in ("n_collocation", "n_boundary"):
        if int(config["training"][key]) <= 0:
            raise ValueError(f"training.{key} doit être strictement positif.")
    if int(config["training"].get("n_initial", 0)) < 0:
        raise ValueError("training.n_initial doit être positif ou nul.")
    observations = config.get("observations", {})
    fraction = float(observations.get("fraction", 1.0))
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("observations.fraction doit être comprise entre 0 et 1.")
    if float(observations.get("noise_level", 0.0)) < 0.0:
        raise ValueError("observations.noise_level doit être positif ou nul.")
    adaptation = config["adaptation"]
    for key in ("vrba_local_enabled", "vrba_global_enabled"):
        if key in adaptation and not isinstance(adaptation[key], bool):
            raise ValueError(f"adaptation.{key} doit être un booléen YAML.")
    if adaptation.get("vw_bandwidth") is not None:
        if float(adaptation["vw_bandwidth"]) <= 0.0:
            raise ValueError("adaptation.vw_bandwidth doit être strictement positif.")
    if float(adaptation.get("vw_bandwidth_scale", 1.0)) <= 0.0:
        raise ValueError("adaptation.vw_bandwidth_scale doit être strictement positif.")
    if str(adaptation.get("vrba_potential", "exponential")).lower() not in {
        "exponential", "quadratic"
    }:
        raise ValueError("adaptation.vrba_potential doit valoir exponential ou quadratic.")
    if float(adaptation.get("vrba_eta", 0.01)) <= 0.0:
        raise ValueError("adaptation.vrba_eta doit être strictement positif.")
    if not 0.0 <= float(adaptation.get("vrba_phi", 0.8)) <= 1.0:
        raise ValueError("adaptation.vrba_phi doit être compris entre 0 et 1.")
    if float(adaptation.get("vrba_temperature_scale", 1.0)) <= 0.0:
        raise ValueError("adaptation.vrba_temperature_scale doit être positif.")
    lambda_initial = float(adaptation.get("vrba_lambda_max_initial", 10.0))
    lambda_cap = float(adaptation.get("vrba_lambda_cap", 20.0))
    if lambda_initial <= 0.0 or lambda_cap < lambda_initial:
        raise ValueError("Les bornes lambda vRBA sont incohérentes.")
    if int(adaptation.get("vrba_stage_steps", 50_000)) <= 0:
        raise ValueError("adaptation.vrba_stage_steps doit être strictement positif.")
    if float(adaptation.get("vrba_initial_fraction", 0.1)) <= 0.0:
        raise ValueError("adaptation.vrba_initial_fraction doit être positif.")
    for key, default in (("vrba_gradient_ema", 0.99), ("vrba_global_ema", 0.99975)):
        value = float(adaptation.get(key, default))
        if not 0.0 <= value < 1.0:
            raise ValueError(f"adaptation.{key} doit être compris dans [0, 1).")
    if int(adaptation.get("vrba_local_every", 1)) <= 0:
        raise ValueError("adaptation.vrba_local_every doit être strictement positif.")
    if int(adaptation.get("vrba_global_every", 1)) <= 0:
        raise ValueError("adaptation.vrba_global_every doit être strictement positif.")


def resolved_config(config: dict[str, Any], method: str, seed: int) -> dict[str, Any]:
    method = method.lower()
    if method not in VALID_METHODS:
        raise ValueError(f"Méthode inconnue {method!r}; choix possibles : {sorted(VALID_METHODS)}")
    result = deepcopy(config)
    result.setdefault("observations", {})
    result["observations"].setdefault("n_observations", 0)
    result["observations"].setdefault("fraction", 1.0)
    result["observations"].setdefault("noise_kind", "none")
    result["observations"].setdefault("noise_level", 0.0)
    result["observations"].setdefault("outlier_fraction", 0.0)
    result["observations"].setdefault("outlier_scale", 5.0)
    result["observations"].setdefault("loss", "mse")
    result["observations"].setdefault("missing_pattern", "none")
    result["observations"].setdefault("missing_fraction", 0.0)
    result.setdefault("ablation", {})
    result["ablation"].setdefault("audit_size_multiplier", 1.0)
    result["ablation"].setdefault("audit_design", "random")
    result["ablation"].setdefault("audit_rotation_every", 0)
    result["ablation"].setdefault("disable_smoothing", False)
    result["ablation"].setdefault("disable_bounds", False)
    result["ablation"].setdefault("disable_uniform_floor", False)
    result["adaptation"].setdefault("vw_bandwidth", None)
    result["adaptation"].setdefault("vw_bandwidth_scale", 1.0)
    result["adaptation"].setdefault("vrba_potential", "exponential")
    result["adaptation"].setdefault("vrba_local_enabled", True)
    result["adaptation"].setdefault("vrba_global_enabled", True)
    result["adaptation"].setdefault("vrba_eta", 0.01)
    result["adaptation"].setdefault("vrba_phi", 0.8)
    result["adaptation"].setdefault("vrba_temperature_scale", 1.0)
    result["adaptation"].setdefault("vrba_lambda_max_initial", 10.0)
    result["adaptation"].setdefault("vrba_lambda_cap", 20.0)
    result["adaptation"].setdefault("vrba_stage_steps", 50_000)
    result["adaptation"].setdefault("vrba_initial_fraction", 0.1)
    result["adaptation"].setdefault("vrba_gradient_ema", 0.99)
    result["adaptation"].setdefault("vrba_global_ema", 0.99975)
    result["adaptation"].setdefault("vrba_global_weight_min", 1e-6)
    result["adaptation"].setdefault("vrba_global_weight_max", 1e6)
    result["adaptation"].setdefault("vrba_local_every", 1)
    result["adaptation"].setdefault("vrba_global_every", 1)
    result["run"] = {"method": method, "seed": int(seed)}
    return result


def dump_config(config: dict[str, Any], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as stream:
        yaml.safe_dump(config, stream, sort_keys=False, allow_unicode=True)
