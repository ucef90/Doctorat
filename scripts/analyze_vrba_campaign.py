"""Independent evaluation, paired inference and exportable research figures."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from recoa_pinn.config import load_config
from recoa_pinn.model import MLP
from recoa_pinn.problems import make_problem
from recoa_pinn.reproducibility import make_generator, resolve_dtype
from vrba_statistics import holm, paired_summary

VARIANTS = ["neither", "global_only", "local_only", "full_exp", "full_quad"]
LABELS = {"neither": "Sans adaptation", "global_only": "Global seul",
          "local_only": "Local seul", "full_exp": "Complet exp.", "full_quad": "Complet quad."}
PROBLEMS = ["burgers", "allen_cahn", "helmholtz", "wave"]
P_LABELS = {"burgers": "Burgers · 2 500 pas", "allen_cahn": "Allen–Cahn forcée · 600 pas",
            "helmholtz": "Helmholtz k=1 · 1 500 pas", "wave": "Ondes · 600 pas"}
CONTRASTS = {
    "full_exp-local_only": {"full_exp": 1, "local_only": -1},
    "full_exp-global_only": {"full_exp": 1, "global_only": -1},
    "full_exp-full_quad": {"full_exp": 1, "full_quad": -1},
    "interaction": {"full_exp": 1, "local_only": -1, "global_only": -1, "neither": 1},
}
COLORS = ["#6B7280", "#CC7A00", "#0072B2", "#009E73", "#9B59B6"]


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def metrics(prediction, reference):
    error = (prediction-reference).abs().flatten()
    return {"relative_l2": float(torch.linalg.vector_norm(prediction-reference) / torch.linalg.vector_norm(reference)),
            "max_abs_error": float(error.max()),
            "q95_abs_error": float(torch.quantile(error, 0.95)),
            "q99_abs_error": float(torch.quantile(error, 0.99))}


def predict(model, points):
    with torch.no_grad():
        return torch.cat([model(chunk) for chunk in points.split(2048)])


def independent_evaluation(campaign, records, report):
    torch.set_num_threads(1)
    audit, reference_checks, evaluated = [], {}, []
    for p_name in PROBLEMS:
        group = [r for r in records if r["problem"] == p_name and r["status"] == "succeeded"]
        if not group:
            continue
        example = load_config(campaign / group[0]["run_dir"] / "config.resolved.yaml")
        dtype = resolve_dtype(example["experiment"]["dtype"])
        torch.set_default_dtype(dtype)
        problem = make_problem(example["problem"], torch.device("cpu"), dtype)
        ev = example["evaluation"]
        coarse = problem.evaluation_grid(ev["nx"], ev["nt"])
        dense = problem.evaluation_grid(2*ev["nx"]-1, 2*ev["nt"]-1)
        reference = problem.reference_at(coarse, ev["reference_nx"], ev["reference_dt"])
        dense_reference = problem.reference_at(dense, ev["reference_nx"], ev["reference_dt"])
        independent = problem.sample_collocation(4096, make_generator(9092026))
        fine_reference = dense_reference
        if p_name == "burgers":
            fine_problem = make_problem(example["problem"], torch.device("cpu"), dtype)
            fine_reference = fine_problem.reference_at(dense, 2*ev["reference_nx"]-1, ev["reference_dt"]/2)
            reference_checks[p_name] = {**metrics(dense_reference, fine_reference),
                "coarse_reference_nx": ev["reference_nx"], "fine_reference_nx": 2*ev["reference_nx"]-1,
                "interpretation": "Discrepancy between two numerical references, not a certified error bound"}
        fields = {v: [] for v in VARIANTS}
        for seed in sorted({r["seed"] for r in group}):
            pair = [r for r in group if r["seed"] == seed]
            same = all(r["initial_fingerprints"] == pair[0]["initial_fingerprints"] for r in pair)
            audit.append(dict(problem=p_name, seed=seed, n_variants=len(pair), initial_hashes_match=same))
            if not same:
                raise RuntimeError(f"Unpaired initial conditions: {p_name}, {seed}")
        for row in group:
            run_dir = campaign / row["run_dir"]
            cfg = load_config(run_dir / "config.resolved.yaml")
            model = MLP(**cfg["model"]).to(dtype=dtype)
            model.load_state_dict(torch.load(run_dir / "model.pt", map_location="cpu", weights_only=True))
            model.eval()
            coarse_pred, dense_pred = predict(model, coarse), predict(model, dense)
            out = {k: row[k] for k in ("id", "problem", "variant", "seed", "status")}
            out.update(metrics(coarse_pred, reference))
            for k in ("relative_l2", "max_abs_error"):
                if not np.isclose(out[k], row[k], rtol=1e-11, atol=1e-12):
                    raise RuntimeError(f"Stored score mismatch: {row['id']} {k}")
            out.update({"dense_"+k: v for k, v in metrics(dense_pred, dense_reference).items()})
            out.update({"refined_"+k: v for k, v in metrics(dense_pred, fine_reference).items()})
            residual = torch.cat([problem.residual(model, chunk, create_graph=False).detach()
                                  for chunk in independent.split(512)])
            out["physics_rms_independent"] = float(residual.square().mean().sqrt())
            out["physics_max_independent"] = float(residual.abs().max())
            error = (dense_pred-fine_reference).abs().flatten()
            location = dense[int(error.argmax())].tolist()
            out.update(peak_coord_0=location[0], peak_coord_1=location[1])
            out.update({k: row[k] for k in ("elapsed_seconds", "process_cpu_seconds", "process_peak_rss_bytes",
                                           "controller_weight_tv", "controller_updates")})
            fields[row["variant"]].append(error.numpy())
            evaluated.append(out)
        shape = (2*ev["nt"]-1, 2*ev["nx"]-1)
        medians = {v: np.median(np.stack(f), axis=0).reshape(shape) for v,f in fields.items() if f}
        np.savez_compressed(report / f"{p_name}_median_error_fields.npz", points=dense.numpy(), **medians)
        if p_name == "burgers":
            fig, axes = plt.subplots(1, 5, figsize=(15, 3.8), constrained_layout=True)
            maximum = max(float(x.max()) for x in medians.values())
            for ax, variant in zip(axes, VARIANTS):
                if variant not in medians:
                    continue
                mesh = ax.imshow(medians[variant], extent=[-1,1,0,1], origin="lower", aspect="auto",
                                 cmap="magma", vmin=0, vmax=maximum)
                ax.set(title=LABELS[variant], xlabel="x")
            axes[0].set_ylabel("t")
            fig.colorbar(mesh, ax=axes, label="Médiane ponctuelle de |u − u réf.|", shrink=.8)
            fig.suptitle("Burgers — erreurs sur grille affinée, référence numérique affinée", fontsize=13)
            save_figure(fig, report, "burgers_error_maps")
        print(f"Independent evaluation: {p_name} {len(group)} models", flush=True)
    (report / "reference_sensitivity.json").write_text(json.dumps(reference_checks, indent=2))
    write_csv(report / "pairing_audit.csv", audit)
    write_csv(report / "evaluation.csv", evaluated)
    (report / "evaluation.json").write_text(json.dumps(evaluated, indent=2))
    return evaluated, audit, reference_checks


def statistics(rows):
    stats = []
    for metric in ("relative_l2", "max_abs_error"):
        family = []
        for problem in PROBLEMS:
            indexed = {(r["variant"], r["seed"]): r for r in rows if r["problem"] == problem}
            for contrast, coefficients in CONTRASTS.items():
                seeds = [s for s in sorted({s for _,s in indexed}) if all((v,s) in indexed for v in coefficients)]
                diffs = [sum(c*indexed[v,s][metric] for v,c in coefficients.items()) for s in seeds]
                entry = dict(problem=problem, metric=metric, contrast=contrast)
                if diffs:
                    entry.update(paired_summary(diffs))
                else:
                    entry.update(n_pairs=0, median_difference=None, mean_difference=None,
                                 ci95_low=None, ci95_high=None, n_negative=0, n_zero=0, n_positive=0, p_sign=1.0)
                family.append(entry)
        for entry, adjusted in zip(family, holm([r["p_sign"] for r in family])):
            entry["p_holm_16"] = adjusted
        stats.extend(family)
    return stats


def save_figure(fig, output, name):
    fig.savefig(output / (name+".png"), dpi=200)
    fig.savefig(output / (name+".svg"))
    plt.close(fig)


def figures(rows, contrasts, report):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    for metric, label, filename in [("relative_l2", "Erreur relative L2", "l2_by_seed"),
                                   ("max_abs_error", "Maximum absolu sur grille historique", "maximum_by_seed")]:
        fig, axes = plt.subplots(2,2,figsize=(12,8), constrained_layout=True)
        for ax, problem in zip(axes.flat, PROBLEMS):
            for i,variant in enumerate(VARIANTS):
                group = sorted([r for r in rows if r["problem"]==problem and r["variant"]==variant], key=lambda r:r["seed"])
                values = [r[metric] for r in group]
                if not values:
                    continue
                ax.scatter(np.linspace(i-.15, i+.15,len(values)),values, color=COLORS[i],s=25,alpha=.75)
                ax.hlines(np.median(values), i-.28,i+.28,color=COLORS[i],lw=3)
            ax.set_xticks(range(5), [LABELS[v] for v in VARIANTS], rotation=15, ha="right")
            ax.set(title=P_LABELS[problem], ylabel=label)
            ax.grid(axis="y", alpha=.2)
        fig.suptitle("Chaque point représente un germe ; trait horizontal = médiane", fontsize=13)
        save_figure(fig, report, filename)
    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    for ax,problem in zip(axes.flat,PROBLEMS):
        subset=[r for r in contrasts if r["problem"]==problem and r["metric"]=="relative_l2"]
        for i,r in enumerate(subset):
            if r["median_difference"] is None:
                continue
            color="#0072B2" if r["p_holm_16"]<.05 else "#667085"
            ax.plot([r["ci95_low"],r["ci95_high"]],[i,i],color=color,lw=2)
            ax.scatter(r["median_difference"],i,color=color,s=35)
        ax.axvline(0,color="black",lw=.8,ls="--")
        ax.set_yticks(range(4),["Complet − local", "Complet − global", "Exp. − quad.", "Interaction"])
        ax.set(title=P_LABELS[problem],xlabel="Différence L2 appariée")
        ax.grid(axis="x",alpha=.2)
    fig.suptitle("Médianes et IC bootstrap marginaux 95 % · bleu : p Holm < 0,05",fontsize=13)
    save_figure(fig,report,"paired_l2_effects")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    campaign=Path(args.campaign).resolve()
    report=Path(args.output).resolve()
    report.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((campaign/"manifest.json").read_text())
    records=[]
    for cell in manifest["cells"]:
        path=campaign/"cells"/cell["id"]/"result.json"
        if not path.exists():
            raise RuntimeError(f"Campaign incomplete: {cell['id']}")
        records.append(json.loads(path.read_text()))
    rows,audit,reference=independent_evaluation(campaign,records,report)
    contrasts=statistics(rows)
    write_csv(report/"paired_statistics.csv",contrasts)
    (report/"paired_statistics.json").write_text(json.dumps(contrasts,indent=2))
    figures(rows,contrasts,report)
    failures=[{k:r.get(k) for k in ("id","status","failure_reason")} for r in records if r["status"]!="succeeded"]
    (report/"failures.json").write_text(json.dumps(failures,indent=2))
    summary=[]
    keys=["relative_l2","max_abs_error","q95_abs_error","q99_abs_error","dense_max_abs_error",
          "refined_max_abs_error","refined_relative_l2","physics_rms_independent","process_cpu_seconds","process_peak_rss_bytes"]
    for problem in PROBLEMS:
        for variant in VARIANTS:
            subset=[r for r in rows if r["problem"]==problem and r["variant"]==variant]
            out=dict(problem=problem,variant=variant,n_success=len(subset),n_expected=10)
            out.update({"median_"+k:float(np.median([r[k] for r in subset])) if subset else None for k in keys})
            summary.append(out)
    write_csv(report/"summary.csv",summary)
    (report/"summary.json").write_text(json.dumps(summary,indent=2))
    scripts=[Path(__file__),Path(__file__).with_name("vrba_statistics.py")]
    (report/"analysis_provenance.json").write_text(json.dumps({
        "source_hashes":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in scripts},
        "evaluated":len(rows),"expected":len(records),"failures":len(failures),
        "paired_blocks":len(audit),"all_initial_hashes_match":all(a["initial_hashes_match"] for a in audit),
        "bootstrap_repeats":10000,"analysis_seed":9092026,
    },indent=2))
    print(f"Analysis complete: {len(rows)} models; {len(contrasts)} contrasts; {len(failures)} failures")


if __name__=="__main__":
    main()
