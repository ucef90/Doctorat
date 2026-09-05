from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

from recoa_pinn.config import load_config
from recoa_pinn.model import MLP
from recoa_pinn.problems import make_problem
from recoa_pinn.reproducibility import resolve_dtype


DEFAULT_SEEDS = (11, 22, 33, 44, 55, 66, 77, 88, 99, 111)
DEFAULT_METHODS = ("m5", "m6", "vrba")
COLORS = {"m5": "#F8961E", "m6": "#277DA1", "vrba": "#7B61A8"}
LABELS = {"m5": "M5 couplé", "m6": "M6 référence fixe", "vrba": "vRBA"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Localise le compromis L2–erreur maximale de vRBA sur Burgers."
    )
    parser.add_argument("--config", default="configs/burgers_confirmatory_long.yaml")
    parser.add_argument("--runs-root", default="outputs/burgers_confirmatory_long_v1")
    parser.add_argument(
        "--output-dir", default="outputs/reports/article1_vrba_spatial"
    )
    parser.add_argument("--methods", nargs="+", default=list(DEFAULT_METHODS))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    return parser.parse_args()


def load_error_fields(
    config: dict,
    runs_root: Path,
    methods: list[str],
    seeds: list[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    device = torch.device("cpu")
    dtype = resolve_dtype(str(config["experiment"]["dtype"]))
    torch.set_default_dtype(dtype)
    problem = make_problem(config["problem"], device, dtype)
    evaluation = config["evaluation"]
    nx = int(evaluation["nx"])
    nt = int(evaluation["nt"])
    points = problem.evaluation_grid(nx, nt)
    reference = problem.reference_at(
        points,
        int(evaluation["reference_nx"]),
        float(evaluation["reference_dt"]),
    ).reshape(nt, nx)
    t = points[:, 0].reshape(nt, nx)[:, 0].detach().cpu().numpy()
    x = points[:, 1].reshape(nt, nx)[0].detach().cpu().numpy()
    reference_np = reference.detach().cpu().numpy()

    errors: dict[str, np.ndarray] = {}
    for method in methods:
        fields = []
        for seed in seeds:
            model_path = runs_root / method / f"seed_{seed:05d}" / "model.pt"
            if not model_path.exists():
                raise FileNotFoundError(f"Modèle manquant : {model_path}")
            model = MLP(**config["model"]).to(device=device, dtype=dtype)
            model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
            model.eval()
            with torch.no_grad():
                prediction = model(points).reshape(nt, nx)
            fields.append((prediction - reference).abs().cpu().numpy())
        errors[method] = np.stack(fields, axis=0)
    return t, x, reference_np, errors


def summarize_fields(
    t: np.ndarray,
    x: np.ndarray,
    reference: np.ndarray,
    errors: dict[str, np.ndarray],
    seeds: list[int],
) -> tuple[list[dict[str, float | int | str]], list[dict[str, float | int | str]]]:
    denominator = np.linalg.norm(reference.ravel())
    summary_rows: list[dict[str, float | int | str]] = []
    seed_rows: list[dict[str, float | int | str]] = []
    for method, stack in errors.items():
        relative_l2 = np.linalg.norm(stack.reshape(stack.shape[0], -1), axis=1) / denominator
        maxima = stack.reshape(stack.shape[0], -1).max(axis=1)
        q95 = np.quantile(stack.reshape(stack.shape[0], -1), 0.95, axis=1)
        q99 = np.quantile(stack.reshape(stack.shape[0], -1), 0.99, axis=1)
        median_field = np.median(stack, axis=0)
        median_max_index = np.unravel_index(np.argmax(median_field), median_field.shape)
        summary_rows.append(
            {
                "method": method,
                "n_seeds": stack.shape[0],
                "relative_l2_median": float(np.median(relative_l2)),
                "pointwise_abs_q95_median": float(np.median(q95)),
                "pointwise_abs_q99_median": float(np.median(q99)),
                "max_abs_error_median": float(np.median(maxima)),
                "median_field_peak": float(median_field[median_max_index]),
                "median_field_peak_t": float(t[median_max_index[0]]),
                "median_field_peak_x": float(x[median_max_index[1]]),
            }
        )
        for index, seed in enumerate(seeds):
            peak_index = np.unravel_index(np.argmax(stack[index]), stack[index].shape)
            seed_rows.append(
                {
                    "method": method,
                    "seed": seed,
                    "relative_l2": float(relative_l2[index]),
                    "pointwise_abs_q95": float(q95[index]),
                    "pointwise_abs_q99": float(q99[index]),
                    "max_abs_error": float(maxima[index]),
                    "peak_t": float(t[peak_index[0]]),
                    "peak_x": float(x[peak_index[1]]),
                }
            )
    return summary_rows, seed_rows


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_maps(
    output_dir: Path,
    t: np.ndarray,
    x: np.ndarray,
    reference: np.ndarray,
    errors: dict[str, np.ndarray],
) -> None:
    median = {method: np.median(stack, axis=0) for method, stack in errors.items()}
    common_max = max(np.quantile(field, 0.995) for field in median.values())
    difference_max = max(
        np.abs(median["vrba"] - median[other]).max() for other in ("m5", "m6")
    )
    extent = [float(x.min()), float(x.max()), float(t.min()), float(t.max())]
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    ref_image = axes[0, 0].imshow(
        reference, origin="lower", aspect="auto", extent=extent, cmap="coolwarm"
    )
    axes[0, 0].set_title("Solution de référence")
    fig.colorbar(ref_image, ax=axes[0, 0], label="u(t,x)")
    for axis, method in zip((axes[0, 1], axes[0, 2], axes[1, 0]), DEFAULT_METHODS):
        image = axis.imshow(
            median[method], origin="lower", aspect="auto", extent=extent,
            cmap="magma", vmin=0.0, vmax=common_max,
        )
        axis.set_title(f"Erreur absolue médiane — {LABELS[method]}")
        fig.colorbar(image, ax=axis, label="|erreur|")
    for axis, other in zip((axes[1, 1], axes[1, 2]), ("m5", "m6")):
        difference = median["vrba"] - median[other]
        image = axis.imshow(
            difference, origin="lower", aspect="auto", extent=extent,
            cmap="RdBu_r", vmin=-difference_max, vmax=difference_max,
        )
        axis.set_title(f"Erreur vRBA − {other.upper()}")
        fig.colorbar(image, ax=axis, label="différence d'erreur absolue")
    for axis in axes.flat:
        axis.set_xlabel("x")
        axis.set_ylabel("t")
    fig.suptitle(
        "Burgers : vRBA réduit l'erreur globale mais conserve une zone de pic",
        fontsize=17,
        fontweight="bold",
    )
    for suffix in ("png", "pdf"):
        fig.savefig(output_dir / f"burgers_spatial_error_maps.{suffix}", dpi=300)
    plt.close(fig)


def plot_profiles(
    output_dir: Path,
    t: np.ndarray,
    x: np.ndarray,
    errors: dict[str, np.ndarray],
) -> None:
    requested_times = (0.25, 0.50, 0.75, 1.00)
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    for axis, requested in zip(axes.flat, requested_times):
        time_index = int(np.argmin(np.abs(t - requested)))
        for method, stack in errors.items():
            values = stack[:, time_index, :]
            median = np.median(values, axis=0)
            low, high = np.quantile(values, (0.25, 0.75), axis=0)
            axis.plot(x, median, color=COLORS[method], label=LABELS[method], linewidth=2)
            axis.fill_between(x, low, high, color=COLORS[method], alpha=0.14)
        axis.set_title(f"t = {t[time_index]:.3f}")
        axis.set_ylabel("Erreur absolue")
        axis.grid(alpha=0.2)
    axes[-1, 0].set_xlabel("x")
    axes[-1, 1].set_xlabel("x")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.925),
        ncol=3, frameon=False,
    )
    fig.suptitle(
        "Profils spatiaux d'erreur Burgers — médiane et intervalle interquartile",
        y=0.985, fontsize=17,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.88))
    for suffix in ("png", "pdf"):
        fig.savefig(output_dir / f"burgers_spatial_error_profiles.{suffix}", dpi=300)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    t, x, reference, errors = load_error_fields(
        config, Path(args.runs_root), list(args.methods), list(args.seeds)
    )
    summary_rows, seed_rows = summarize_fields(
        t, x, reference, errors, list(args.seeds)
    )
    write_csv(output_dir / "spatial_summary.csv", summary_rows)
    write_csv(output_dir / "spatial_by_seed.csv", seed_rows)
    plot_maps(output_dir, t, x, reference, errors)
    plot_profiles(output_dir, t, x, errors)
    manifest = {
        "config": str(Path(args.config)),
        "runs_root": str(Path(args.runs_root)),
        "methods": list(args.methods),
        "seeds": list(args.seeds),
        "grid": {"nt": len(t), "nx": len(x)},
        "outputs": [
            "spatial_summary.csv",
            "spatial_by_seed.csv",
            "burgers_spatial_error_maps.png",
            "burgers_spatial_error_maps.pdf",
            "burgers_spatial_error_profiles.png",
            "burgers_spatial_error_profiles.pdf",
        ],
    }
    (output_dir / "analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"output_dir": str(output_dir), "summary": summary_rows}, indent=2))


if __name__ == "__main__":
    main()
