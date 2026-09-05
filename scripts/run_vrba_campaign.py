"""Frozen, resumable multi-PDE ablations; completed failures are retained."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import random
import resource
import subprocess
import time
import traceback

from recoa_pinn.config import load_config
from recoa_pinn.reproducibility import environment_manifest

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    "burgers": "burgers_confirmatory_long.yaml",
    "allen_cahn": "allen_cahn_screen.yaml",
    "helmholtz": "helmholtz_calibrated.yaml",
    "wave": "wave_screen.yaml",
}
VARIANTS = {
    "full_exp": (True, True, "exponential"),
    "local_only": (True, False, "exponential"),
    "global_only": (False, True, "exponential"),
    "full_quad": (True, True, "quadratic"),
    "neither": (False, False, "exponential"),
}
SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 111]


def atomic_json(path: Path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def build_manifest(seeds, problems):
    paths = list((ROOT / "src").rglob("*.py")) + [Path(__file__)]
    paths += [ROOT / "configs" / CONFIGS[p] for p in problems]
    paths += [ROOT / "VRBA_CAMPAIGN_PROTOCOL_V09.md"]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(paths)}
    cells = []
    for seed in seeds:
        block = [(p, v) for p in problems for v in VARIANTS]
        random.Random(9000 + seed).shuffle(block)
        for problem, variant in block:
            config = load_config(ROOT / "configs" / CONFIGS[problem])
            local, global_, potential = VARIANTS[variant]
            config["adaptation"].update(vrba_local_enabled=local,
                vrba_global_enabled=global_, vrba_potential=potential)
            cells.append(dict(id=f"{problem}__{variant}__{seed}", problem=problem,
                              variant=variant, seed=seed, config=config))
    return {"protocol": "v0.9-exploratory-frozen", "hashes": hashes, "cells": cells}


def worker(cell, campaign_dir):
    # One fresh process per cell: RNG state and peak RSS are not inherited
    # from an earlier model. Numerical thread count is held at one.
    import torch
    from recoa_pinn.trainer import train
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    base = Path(campaign_dir) / "cells" / cell["id"]
    base.mkdir(parents=True, exist_ok=True)
    attempt_number = 1
    while (base / f"attempt_{attempt_number:03d}").exists():
        attempt_number += 1
    attempt = base / f"attempt_{attempt_number:03d}"
    attempt.mkdir()
    config = deepcopy(cell["config"])
    config["experiment"]["output_dir"] = str(attempt)
    wall_start, cpu_start = time.perf_counter(), time.process_time()
    record = {k: cell[k] for k in ("id", "problem", "variant", "seed")}
    record["started_at"] = datetime.now(timezone.utc).isoformat()
    try:
        summary = train(config, "vrba", cell["seed"])
        record.update(summary)
        state = torch.load(Path(summary["run_dir"]) / "model.pt", weights_only=True)
        finite = all(torch.isfinite(v).all().item() for v in state.values())
        finite = finite and all(math.isfinite(summary[k]) for k in ("relative_l2", "max_abs_error"))
        record["finite_validation"] = finite
        if not finite or summary["steps_completed"] != summary["steps_requested"]:
            record.update(status="failed", failure_reason="Nonfinite or incomplete terminal state")
        record["run_dir"] = str(Path(summary["run_dir"]).relative_to(Path(campaign_dir)))
    except Exception:
        record.update(status="failed", failure_reason=traceback.format_exc())
    record.update(wall_seconds_with_setup=time.perf_counter() - wall_start,
                  process_cpu_seconds=time.process_time() - cpu_start,
                  process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                  attempt_number=attempt_number,
                  completed_at=datetime.now(timezone.utc).isoformat())
    atomic_json(base / "result.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    parser.add_argument("--problems", nargs="+", choices=list(CONFIGS), default=list(CONFIGS))
    args = parser.parse_args()
    if args.workers < 1 or len(args.seeds) != len(set(args.seeds)):
        parser.error("workers must be positive; seeds must be unique")
    output = Path(args.output).resolve()
    manifest = build_manifest(args.seeds, args.problems)
    if args.resume:
        old = json.loads((output / "manifest.json").read_text())
        if old != manifest:
            raise RuntimeError("Resume refused: protocol, code or configuration differs")
        old_env = json.loads((output / "launch_environment.json").read_text())
        current_env = environment_manifest()
        if any(old_env[k] != current_env[k] for k in ("python", "torch", "numpy", "platform")):
            raise RuntimeError("Resume refused: numerical environment differs")
    else:
        output.mkdir(parents=True, exist_ok=False)
        atomic_json(output / "manifest.json", manifest)
        atomic_json(output / "launch_environment.json", environment_manifest())
        packages = subprocess.check_output([os.sys.executable, "-m", "pip", "freeze"], text=True)
        (output / "environment-freeze.txt").write_text(packages)
    completed = []
    pending = []
    for cell in manifest["cells"]:
        result_path = output / "cells" / cell["id"] / "result.json"
        if result_path.exists():
            completed.append(json.loads(result_path.read_text()))
        else:
            pending.append(cell)
    print(f"Frozen cells={len(manifest['cells'])}; retained={len(completed)}; pending={len(pending)}", flush=True)
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers,
                             mp_context=multiprocessing.get_context("spawn"),
                             max_tasks_per_child=1) as executor:
        futures = {executor.submit(worker, cell, str(output)): cell for cell in pending}
        for future in as_completed(futures):
            record = future.result()
            completed.append(record)
            atomic_json(output / "results.json", sorted(completed, key=lambda r: r["id"]))
            print(f"{len(completed)}/{len(manifest['cells'])} {record['id']} {record['status']} "
                  f"L2={record.get('relative_l2', float('nan')):.6f}", flush=True)
    atomic_json(output / "completion.json", dict(
        completed=len(completed), expected=len(manifest["cells"]),
        failed=sum(r["status"] != "succeeded" for r in completed),
        invocation_wall_seconds=time.perf_counter()-start, workers=args.workers,
        time_comparisons="Parallel throughput campaign, not isolated wall-time profiling"))
    if any(r["status"] != "succeeded" for r in completed):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
