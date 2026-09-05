import numpy as np
import pytest
from scripts.vrba_statistics import holm, paired_summary, sign_test


def test_exact_sign_test_small_samples():
    assert sign_test([1] * 10) == 2 / 1024
    assert sign_test([-1] * 5 + [1] * 5) == 1
    assert sign_test([0, 0]) == 1
    assert sign_test([0, 1, 1, 1]) == 0.25


def test_holm_known_example():
    np.testing.assert_allclose(holm([0.04, 0.001, 0.02]), [0.04, 0.003, 0.04])
    assert holm([1, 1]) == [1, 1]


def test_degenerate_paired_effect_and_reproducibility():
    stats = paired_summary([-0.2] * 10)
    assert stats["median_difference"] == stats["ci95_low"] == stats["ci95_high"] == -0.2
    assert paired_summary(range(10)) == paired_summary(range(10))
    with pytest.raises(ValueError):
        sign_test([np.nan])
