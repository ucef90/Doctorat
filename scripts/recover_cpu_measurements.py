"""Recover recorded windows without inferring missing terminal data."""
import csv
import json
from pathlib import Path
from statistics import median

root=Path(__file__).resolve().parents[1]/"outputs/ablation_v09_cpu"
manifest=json.loads((root/"manifest.json").read_text())
records=json.loads((root/"results.json").read_text())
indexed={r["id"]:r for r in records}
windows=[]
for cell in manifest["cells"]:
    row=indexed.get(cell["id"])
    if row is not None:
        windows.append({**row,"window_status":"measured","terminal_complete":True})
        continue
    logs=list((root/"cells"/cell["id"]).glob("attempt_*/*/vrba/seed_*/metrics.csv"))
    if len(logs)!=1:
        raise RuntimeError("Ambiguous interrupted logs")
    with logs[0].open() as handle:
        steps={int(r["step"]):r for r in csv.DictReader(handle)}
    assert 50 in steps and 150 in steps
    windows.append({k:cell[k] for k in ("id","problem","variant","seed")}|{
        "window_status":"measured_from_interrupted_run","terminal_complete":False,
        "seconds_per_step_warm":(float(steps[150]["elapsed_seconds"])-float(steps[50]["elapsed_seconds"]))/100,
        "process_peak_rss_bytes":None,"source_log":str(logs[0].relative_to(root))})
summary=[]
for problem in sorted({r["problem"] for r in windows}):
    group=[r for r in windows if r["problem"]==problem]
    baseline={r["seed"]:r for r in group if r["variant"]=="neither"}
    for variant in sorted({r["variant"] for r in group}):
        rows=[r for r in group if r["variant"]==variant]
        rss=[r["process_peak_rss_bytes"] for r in rows if r["process_peak_rss_bytes"] is not None]
        summary.append(dict(problem=problem,variant=variant,n_windows=len(rows),
            n_completed=sum(r["terminal_complete"] for r in rows),n_memory_measurements=len(rss),
            median_ms_per_step=1000*median(r["seconds_per_step_warm"] for r in rows),
            median_paired_ratio_to_neither=median(r["seconds_per_step_warm"]/baseline[r["seed"]]["seconds_per_step_warm"] for r in rows),
            median_peak_rss_mib=median(rss)/1024**2))
for name,data in [("measured_windows.json",windows),("summary.json",summary),
                  ("completion.json",dict(completed=len(records),expected=60,failed=0,interrupted=60-len(records),
                    valid_timing_windows=len(windows),note="Final run interrupted after step 150; timing window fully recorded; terminal RSS unavailable"))]:
    (root/name).write_text(json.dumps(data,indent=2))
with (root/"summary.csv").open("w",newline="") as handle:
    writer=csv.DictWriter(handle,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
print("60 timing windows; 59 terminal runs; 1 explicitly interrupted")
