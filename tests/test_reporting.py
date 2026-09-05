import csv
import json
from pathlib import Path

import pytest

from recoa_pinn.campaign import _load_summary
from recoa_pinn.reporting import generate_campaign_report


def _summary(run_dir: Path, method: str, seed: int, error: float) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["step", "relative_l2"])
        writer.writeheader()
        writer.writerows([
            {"step": 1, "relative_l2": error * 2.0},
            {"step": 2, "relative_l2": error},
        ])
    return {
        "status": "succeeded", "method": method, "seed": seed, "problem": "burgers",
        "relative_l2": error, "max_abs_error": error * 2.0,
        "controller_weight_tv_per_update": error / 10.0,
        "temporal_mean_gradient_distribution_tv": error / 20.0,
        "temporal_mean_physics_gradient_log_gap": error / 5.0,
        "elapsed_seconds": 1.0 + seed, "residual_evaluations": 100 + seed,
        "observations": {
            "effective_count": 0, "noise_kind": "none", "noise_level": 0.0,
        },
        "run_dir": str(run_dir),
    }


def test_report_writes_tables_figures_and_paired_statistics(tmp_path: Path):
    summaries = []
    for seed, first, second in [(1, 0.5, 0.4), (2, 0.6, 0.45), (3, 0.55, 0.5)]:
        summaries.append(_summary(tmp_path / f"m5_{seed}", "m5", seed, first))
        summaries.append(_summary(tmp_path / f"m6_{seed}", "m6", seed, second))
    experiments = [{
        "id": "pilot", "label": "Pilote", "problem": "burgers",
        "methods": ["m5", "m6"], "seeds": [1, 2, 3],
        "contrasts": [["m5", "m6"]], "summaries": summaries,
    }]
    report = generate_campaign_report(
        "test", tmp_path / "report", experiments, bootstrap_repeats=200
    )
    assert report["successful_runs"] == 6
    assert (tmp_path / "report" / "REPORT.md").exists()
    assert (tmp_path / "report" / "tables" / "method_summary.csv").exists()
    assert (tmp_path / "report" / "tables" / "paired_summary.csv").exists()
    assert (tmp_path / "report" / "tables" / "table_main_results.tex").exists()
    assert (tmp_path / "report" / "figures" / "relative_l2_boxplot.png").exists()
    assert (tmp_path / "report" / "figures" / "paired_relative_l2_forest.pdf").exists()

    with (tmp_path / "report" / "tables" / "paired_summary.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    error_row = next(row for row in rows if row["metric"] == "relative_l2")
    assert int(error_row["n_pairs"]) == 3
    assert float(error_row["median_difference"]) < 0.0
    assert float(error_row["second_win_fraction"]) == 1.0


def test_legacy_summary_is_enriched_from_metrics_csv(tmp_path: Path):
    run_dir = tmp_path / "legacy"
    run_dir.mkdir()
    summary_path = run_dir / "summary.json"
    summary_path.write_text(
        json.dumps({"status": "succeeded", "method": "m5", "seed": 1}),
        encoding="utf-8",
    )
    with (run_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "gradient_distribution_tv", "loss_distribution_tv",
            "physics_gradient_log_gap",
        ])
        writer.writeheader()
        writer.writerows([
            {"gradient_distribution_tv": 0.2, "loss_distribution_tv": 0.4,
             "physics_gradient_log_gap": 0.6},
            {"gradient_distribution_tv": 0.4, "loss_distribution_tv": 0.6,
             "physics_gradient_log_gap": 0.8},
        ])
    summary = _load_summary(summary_path)
    assert summary is not None
    assert summary["temporal_mean_gradient_distribution_tv"] == pytest.approx(0.3)
    assert summary["temporal_mean_loss_distribution_tv"] == pytest.approx(0.5)
    assert summary["temporal_mean_physics_gradient_log_gap"] == pytest.approx(0.7)
