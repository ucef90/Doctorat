#!/usr/bin/env python3
"""Paired cross-campaign comparison of M7 and VW bandwidth variants."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


SEEDS = [11, 22, 33, 44, 55, 66, 77, 88, 99, 111]
CASES = {
    "burgers_sparse_noisy": {
        "label": "Burgers — 13 observations bruitées",
        "m7_experiment": "burgers_data_sparse_noisy_v1",
        "vw_prefix": "vw_bandwidth_sparse_noisy_h",
    },
    "wave": {
        "label": "Équation des ondes",
        "m7_experiment": "wave_screen_v1",
        "vw_prefix": "vw_bandwidth_wave_h",
    },
}
SCALES = {"05": 0.5, "10": 1.0, "20": 2.0}


def _load_error(path: Path) -> float:
    summary = json.loads(path.read_text(encoding="utf-8"))
    if summary.get("status") != "succeeded":
        raise RuntimeError(f"Run non réussi : {path}")
    return float(summary["relative_l2"])


def _bootstrap_ci(differences: np.ndarray, key: str) -> tuple[float, float]:
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "little")
    generator = np.random.default_rng(seed)
    indices = generator.integers(0, differences.size, size=(10_000, differences.size))
    medians = np.median(differences[indices], axis=1)
    return tuple(float(value) for value in np.quantile(medians, [0.025, 0.975]))


def _sign_test(differences: np.ndarray) -> float | None:
    nonzero = differences[differences != 0.0]
    if nonzero.size == 0:
        return None
    smaller = min(int(np.sum(nonzero < 0.0)), int(np.sum(nonzero > 0.0)))
    return min(
        1.0,
        2.0 * sum(math.comb(int(nonzero.size), k) for k in range(smaller + 1))
        / (2 ** int(nonzero.size)),
    )


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    output_root = project / "outputs"
    report_dir = output_root / "reports" / "article1_vw_bandwidth_sensitivity"
    rows: list[dict[str, object]] = []

    for case_id, case in CASES.items():
        m7_values = np.asarray(
            [
                _load_error(
                    output_root
                    / str(case["m7_experiment"])
                    / "m7"
                    / f"seed_{seed:05d}"
                    / "summary.json"
                )
                for seed in SEEDS
            ]
        )
        for scale_code, scale in SCALES.items():
            experiment = f"{case['vw_prefix']}{scale_code}_v1"
            for method in ("vw", "vwca"):
                candidate = np.asarray(
                    [
                        _load_error(
                            output_root
                            / experiment
                            / method
                            / f"seed_{seed:05d}"
                            / "summary.json"
                        )
                        for seed in SEEDS
                    ]
                )
                difference = m7_values - candidate
                low, high = _bootstrap_ci(difference, f"{case_id}:{scale}:{method}")
                rows.append(
                    {
                        "case": case_id,
                        "label": case["label"],
                        "bandwidth_scale": scale,
                        "candidate_method": method,
                        "n_pairs": len(SEEDS),
                        "median_m7": float(np.median(m7_values)),
                        "median_candidate": float(np.median(candidate)),
                        "median_m7_minus_candidate": float(np.median(difference)),
                        "ci95_low": low,
                        "ci95_high": high,
                        "m7_win_fraction": float(np.mean(difference < 0.0)),
                        "two_sided_sign_test_p": _sign_test(difference),
                    }
                )

    csv_path = report_dir / "tables" / "m7_vs_vw_bandwidth.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path = report_dir / "m7_vs_vw_bandwidth.json"
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Comparaison appariée M7–VW selon la largeur de bande",
        "",
        "Une différence négative indique une erreur L2 plus faible pour M7.",
        "",
        "| Cas | h/Scott | Méthode | Médiane M7 | Médiane candidate | Δ M7−candidate | IC 95 % | Victoires M7 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['label']} | {float(row['bandwidth_scale']):.1f} | "
            f"{str(row['candidate_method']).upper()} | {float(row['median_m7']):.4f} | "
            f"{float(row['median_candidate']):.4f} | "
            f"{float(row['median_m7_minus_candidate']):+.4f} | "
            f"[{float(row['ci95_low']):+.4f}, {float(row['ci95_high']):+.4f}] | "
            f"{100 * float(row['m7_win_fraction']):.0f} % |"
        )
    lines.extend(
        [
            "",
            "Règle : aucune supériorité n'est déclarée lorsque l'intervalle traverse zéro.",
        ]
    )
    (report_dir / "M7_VS_VW_BANDWIDTH.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
