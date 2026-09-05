from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path

import numpy as np

from recoa_pinn.config import load_config
from recoa_pinn.trainer import train


SEEDS = [11, 22, 33, 44, 55]
VARIANTS = {
    "a0_fixed_reference": ("m6", {}),
    "a1_adaptive_batch": ("m5", {}),
    "audit_size_025": ("m6", {"ablation.audit_size_multiplier": 0.25}),
    "audit_size_050": ("m6", {"ablation.audit_size_multiplier": 0.5}),
    "audit_size_200": ("m6", {"ablation.audit_size_multiplier": 2.0}),
    "audit_latin_hypercube": ("m6", {"ablation.audit_design": "latin_hypercube"}),
    "audit_sobol": ("m6", {"ablation.audit_design": "sobol"}),
    "audit_slow_rotation": ("m6", {"ablation.audit_rotation_every": 100}),
    "without_smoothing": ("m6", {"ablation.disable_smoothing": True}),
    "without_bounds": ("m6", {"ablation.disable_bounds": True}),
    "without_uniform_floor": ("m6", {"ablation.disable_uniform_floor": True}),
    "controller_slower": ("m6", {"adaptation.controller_every": 50}),
    "sampler_slower": ("m6", {"adaptation.sampler_every": 50}),
}


def apply_overrides(config, overrides):
    for dotted, value in overrides.items():
        section, key = dotted.split(".", 1)
        config[section][key] = value


def execute(task):
    config, method, seed, variant = task
    result = train(config, method, seed)
    result["variant"] = variant
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/burgers_ablation_screen.yaml")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    base = load_config(args.config)
    tasks = []
    for variant, (method, overrides) in VARIANTS.items():
        for seed in SEEDS:
            config = deepcopy(base)
            config["experiment"]["name"] = f"burgers_ablation_screen_v1/{variant}"
            apply_overrides(config, overrides)
            tasks.append((config, method, seed, variant))
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(execute, tasks))
    summary = {"seeds": SEEDS, "variants": {}, "runs": results}
    for variant in VARIANTS:
        group = [run for run in results if run["variant"] == variant]
        summary["variants"][variant] = {
            "method": group[0]["method"],
            "n_success": sum(run["status"] == "succeeded" for run in group),
            "median_relative_l2": float(np.median([run["relative_l2"] for run in group])),
            "median_weight_tv_per_update": float(np.median([
                run["controller_weight_tv_per_update"] for run in group
            ])),
            "median_elapsed_seconds": float(np.median([run["elapsed_seconds"] for run in group])),
            "median_residual_evaluations": float(np.median([
                run["residual_evaluations"] for run in group
            ])),
        }
    output = Path(base["experiment"]["output_dir"]) / "burgers_ablation_screen_v1" / "ablation_summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output.resolve()), "variants": summary["variants"]}, indent=2))


if __name__ == "__main__":
    main()
