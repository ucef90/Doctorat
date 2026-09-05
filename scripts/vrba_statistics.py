"""Paired seed-level statistics; no dependency on training or plotting."""
from __future__ import annotations

import math
import numpy as np


def sign_test(differences):
    values = np.asarray(differences, dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite paired differences")
    nonzero = values[values != 0]
    n = len(nonzero)
    if not n:
        return 1.0
    tail = min(int((nonzero > 0).sum()), int((nonzero < 0).sum()))
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(tail + 1)) / 2**n)


def holm(pvalues):
    pvalues = np.asarray(pvalues, dtype=float)
    if not np.isfinite(pvalues).all() or ((pvalues < 0) | (pvalues > 1)).any():
        raise ValueError("Invalid p-values")
    order = np.argsort(pvalues, kind="stable")
    adjusted = np.empty(len(order))
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(order) - rank) * pvalues[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def paired_summary(differences, repeats=10000, seed=9092026):
    values = np.asarray(differences, dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("Need finite paired differences")
    rng = np.random.default_rng(seed)
    medians = np.median(values[rng.integers(0, len(values), (repeats, len(values)))], axis=1)
    return {
        "n_pairs": len(values), "median_difference": float(np.median(values)),
        "mean_difference": float(values.mean()),
        "ci95_low": float(np.quantile(medians, 0.025)),
        "ci95_high": float(np.quantile(medians, 0.975)),
        "n_negative": int((values < 0).sum()), "n_zero": int((values == 0).sum()),
        "n_positive": int((values > 0).sum()), "p_sign": sign_test(values),
    }
