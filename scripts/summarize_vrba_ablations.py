"""Produce a descriptive table; no significance claim from the pilot."""
import argparse
import json
from pathlib import Path
from statistics import median

import torch

from recoa_pinn.config import load_config
from recoa_pinn.model import MLP
from recoa_pinn.problems import make_problem
from recoa_pinn.reproducibility import resolve_dtype


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    args = parser.parse_args()
    root = Path(args.output)
    records = json.loads((root / "ablation_results.json").read_text())
    for row in records:
        if row["status"] != "succeeded":
            continue
        run = Path(row["run_dir"])
        config = load_config(run / "config.resolved.yaml")
        dtype = resolve_dtype(config["experiment"]["dtype"])
        model = MLP(**config["model"]).to(dtype=dtype)
        model.load_state_dict(torch.load(run / "model.pt", map_location="cpu", weights_only=True))
        model.eval()
        problem = make_problem(config["problem"], torch.device("cpu"), dtype)
        ev = config["evaluation"]
        points = problem.evaluation_grid(ev["nx"], ev["nt"])
        reference = problem.reference_at(points, ev["reference_nx"], ev["reference_dt"])
        with torch.no_grad():
            error = (model(points) - reference).abs().flatten()
        row["q95_abs_error"] = float(torch.quantile(error, 0.95))
        row["q99_abs_error"] = float(torch.quantile(error, 0.99))
    (root / "analysis.json").write_text(json.dumps(records, indent=2))
    lines = ["# Ablations vRBA — bilan descriptif", "",
        "Pilote exploratoire : aucune conclusion confirmatoire ni sélection de variante.", "",
        "| Variante | Réussites/total | L2 médiane | Maximum médian | q95 médian | q99 médian | Temps médian (s) |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    for variant in sorted({r["variant"] for r in records}):
        group = [r for r in records if r["variant"] == variant]
        ok = [r for r in group if r["status"] == "succeeded"]
        values = [f"{median(r[k] for r in ok):.6f}" if ok else "NA"
                  for k in ("relative_l2", "max_abs_error", "q95_abs_error", "q99_abs_error", "elapsed_seconds")]
        lines.append(f"| {variant} | {len(ok)}/{len(group)} | " + " | ".join(values) + " |")
    lines += ["", "Les quantiles décrivent les points de grille, pas l'incertitude entre germes.",
              "Les temps pilotes ne constituent pas un profilage CPU/GPU contrôlé."]
    (root / "REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
