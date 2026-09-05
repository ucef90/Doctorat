"""Sequential interleaved CPU probes, separate from the accuracy campaign."""
from concurrent.futures import ProcessPoolExecutor
import argparse
import csv
import hashlib
import json
import multiprocessing
from pathlib import Path
import random

import numpy as np
from run_vrba_campaign import build_manifest, worker, atomic_json, CONFIGS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = build_manifest([11,22,33], list(CONFIGS))
    for cell in manifest["cells"]:
        cell["config"]["training"].update(steps=200, eval_every=200,
                                            log_every=50, checkpoint_every=200)
    manifest["profile"] = dict(warmup_steps=50, measured_steps=[51,150],
        repeats=3, sequential=True, includes="optimizer + diagnostics + logging",
        excludes="initialization, first 50 steps, final reference solve, checkpoints",
        accuracy_claim=False,
        cuda="not_available; no GPU measurement inferred")
    manifest["profile_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    atomic_json(output/"manifest.json", manifest)
    results=[]
    with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"),
                             max_tasks_per_child=1) as executor:
        # Submit one at a time; no overlap with other profiling runs.
        for cell in manifest["cells"]:
            result = executor.submit(worker, cell, str(output)).result()
            if result["status"] == "succeeded":
                with (output/result["run_dir"]/"metrics.csv").open() as stream:
                    rows = {int(r["step"]):r for r in csv.DictReader(stream)}
                result["seconds_per_step_warm"]=(float(rows[150]["elapsed_seconds"])-float(rows[50]["elapsed_seconds"]))/100
            results.append(result)
            atomic_json(output/"results.json", results)
            print(f"CPU profile {len(results)}/60 {cell['id']} {result['status']}",flush=True)
    summary=[]
    for problem in CONFIGS:
        p_rows=[r for r in results if r["problem"]==problem and r["status"]=="succeeded"]
        reference={r["seed"]:r for r in p_rows if r["variant"]=="neither"}
        for variant in sorted({r["variant"] for r in p_rows}):
            rows=[r for r in p_rows if r["variant"]==variant]
            ratios=[r["seconds_per_step_warm"]/reference[r["seed"]]["seconds_per_step_warm"]
                    for r in rows if r["seed"] in reference]
            summary.append(dict(problem=problem,variant=variant,n_success=len(rows),
                median_ms_per_step=1000*float(np.median([r["seconds_per_step_warm"] for r in rows])),
                median_paired_ratio_to_neither=float(np.median(ratios)),
                median_peak_rss_mib=float(np.median([r["process_peak_rss_bytes"] for r in rows]))/1024**2))
    atomic_json(output/"summary.json",summary)
    with (output/"summary.csv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    failed=sum(r["status"]!="succeeded" for r in results)
    atomic_json(output/"completion.json",dict(completed=len(results),expected=60,failed=failed))
    if failed:
        raise SystemExit(1)


if __name__=="__main__":
    main()
