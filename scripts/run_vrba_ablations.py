"""Run all prespecified ablations without selecting or overwriting results."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from recoa_pinn.config import load_config
from recoa_pinn.trainer import train

VARIANTS = {
    "full_exp": (True, True, "exponential"),
    "local_only": (True, False, "exponential"),
    "global_only": (False, True, "exponential"),
    "full_quad": (True, True, "quadratic"),
    "neither": (False, False, "exponential"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/pilot_quick.yaml")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[11, 22, 33])
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((root / "src").rglob("*.py"))}
    hashes["config"] = hashlib.sha256(Path(args.config).read_bytes()).hexdigest()
    (output / "source_hashes.json").write_text(json.dumps(hashes, indent=2))
    records = []
    for seed in args.seeds:
        order = list(VARIANTS)
        random.Random(seed + 8000).shuffle(order)
        for variant in order:
            config = load_config(args.config)
            local, global_, potential = VARIANTS[variant]
            config["adaptation"].update(vrba_local_enabled=local,
                vrba_global_enabled=global_, vrba_potential=potential)
            config["experiment"]["output_dir"] = str(output / variant)
            try:
                summary = train(config, "vrba", seed)
                record = {"variant": variant, "seed": seed, **summary}
            except Exception as exc:
                record = {"variant": variant, "seed": seed,
                          "status": "failed", "error": repr(exc)}
            records.append(record)
            (output / "ablation_results.json").write_text(json.dumps(records, indent=2))
            print(variant, seed, record["status"], record.get("relative_l2"), flush=True)
    failures = sum(r["status"] != "succeeded" for r in records)
    print(f"Completed {len(records)} runs; failures={failures}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
