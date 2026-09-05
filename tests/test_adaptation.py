import math

import pytest
import torch

from recoa_pinn.adaptation import (
    LossController,
    ResidualSampler,
    VRBAAttention,
    VRBAGlobalController,
    importance_statistics,
    importance_weighted_mean,
    importance_weights_from_probability,
    kde_volume_physics_weights,
)
from recoa_pinn.model import MLP
from recoa_pinn.problems.burgers import BurgersProblem
from recoa_pinn.reproducibility import make_generator


PROBLEM = {
    "x_min": -1.0, "x_max": 1.0, "t_min": 0.0, "t_max": 1.0,
    "viscosity": 0.01 / math.pi,
}
ADAPTATION = {
    "candidate_size": 64, "residual_power": 1.0, "residual_mix": 0.8,
    "replace_fraction": 0.5, "ema_beta": 0.9, "progress_alpha": 0.5,
    "weight_min": 0.1, "weight_max": 10.0,
}


def test_residual_sampler_preserves_size_and_domain():
    torch.set_default_dtype(torch.float64)
    problem = BurgersProblem(PROBLEM, torch.device("cpu"), torch.float64)
    model = MLP(2, 8).double()
    generator = make_generator(10)
    current = problem.sample_collocation(32, generator)
    updated = ResidualSampler(ADAPTATION).update(problem, model, current, generator)
    assert updated.shape == current.shape
    assert torch.all((updated[:, 0] >= 0) & (updated[:, 0] <= 1))
    assert torch.all((updated[:, 1] >= -1) & (updated[:, 1] <= 1))


def test_controller_returns_positive_normalized_weights():
    torch.set_default_dtype(torch.float64)
    problem = BurgersProblem(PROBLEM, torch.device("cpu"), torch.float64)
    model = MLP(2, 8).double()
    sets = problem.sample_sets(16, 8, 8, make_generator(11))
    losses = problem.component_losses(model, sets)
    weights = LossController(list(losses), ADAPTATION).update(losses, model)
    assert all(value > 0 for value in weights.values())
    assert abs(sum(weights.values()) / len(weights) - 1.0) < 1e-12


def test_hansen_hurwitz_weights_recover_uniform_candidate_mean_exactly():
    probability = torch.tensor([0.1, 0.2, 0.3, 0.4], dtype=torch.float64)
    values = torch.tensor([1.0, 4.0, 9.0, 16.0], dtype=torch.float64)
    selected = torch.arange(probability.numel())
    weights = importance_weights_from_probability(probability, selected)
    expectation = torch.sum(probability * weights * values)
    assert expectation == torch.mean(values)


def test_measure_corrected_sampler_preserves_weights_and_cardinality():
    torch.set_default_dtype(torch.float64)
    problem = BurgersProblem(PROBLEM, torch.device("cpu"), torch.float64)
    model = MLP(2, 8).double()
    generator = make_generator(12)
    current = problem.sample_collocation(32, generator)
    initial_weights = torch.ones(32, dtype=torch.float64)
    updated, weights = ResidualSampler(ADAPTATION).update_measure_corrected(
        problem, model, current, initial_weights, generator
    )
    assert updated.shape == current.shape
    assert weights.shape == (current.shape[0],)
    assert torch.isfinite(weights).all()
    assert torch.all(weights > 0)
    assert torch.isfinite(importance_weighted_mean(torch.ones(32), weights))
    statistics = importance_statistics(weights)
    assert 0.0 < statistics["effective_sample_fraction"] <= 1.0


def test_kde_volume_weights_match_vw_loss_normalization():
    points = torch.tensor(
        [[0.50, 0.50], [0.50, 0.50], [0.51, 0.50], [0.00, 0.00]],
        dtype=torch.float64,
    )
    weights = kde_volume_physics_weights(points, (0.0, 0.0), (1.0, 1.0), 0.1)
    assert weights.shape == (4,)
    assert torch.isclose(weights.mean(), torch.tensor(1.0, dtype=torch.float64))
    # The isolated point represents a larger local volume than the dense cluster.
    assert weights[-1] > weights[0]

    residual_squared = torch.tensor([1.0, 4.0, 9.0, 16.0], dtype=torch.float64)
    density = torch.exp(
        -0.5 * torch.cdist(points, points).square() / (0.1**2)
    ).mean(dim=1)
    volume = density.reciprocal()
    expected = torch.sum(volume.square() * residual_squared) / torch.sum(volume.square())
    assert torch.isclose(importance_weighted_mean(residual_squared, weights), expected)


def test_vrba_exponential_attention_is_finite_and_focuses_on_largest_residual():
    config = {
        "vrba_potential": "exponential",
        "vrba_eta": 0.01,
        "vrba_phi": 0.8,
        "vrba_temperature_scale": 1.0,
        "vrba_lambda_max_initial": 10.0,
        "vrba_lambda_cap": 20.0,
        "vrba_stage_steps": 50_000,
        "vrba_initial_fraction": 0.1,
    }
    residuals = {
        "physics": torch.tensor([0.0, 1.0, 3.0], dtype=torch.float64)
    }
    attention = VRBAAttention(["physics"], config)
    multipliers = attention.update(residuals, step=1)["physics"]
    assert torch.isfinite(multipliers).all()
    assert multipliers[-1] > multipliers[1] > multipliers[0]
    assert attention.decay(1) == pytest.approx(0.999)
    statistics = attention.statistics()
    assert 0.0 < statistics["effective_sample_fraction"] <= 1.0
    assert statistics["temperature"] > 0.0


def test_vrba_quadratic_attention_handles_zero_residuals():
    attention = VRBAAttention(
        ["physics"],
        {
            "vrba_potential": "quadratic",
            "vrba_eta": 0.01,
            "vrba_phi": 1.0,
            "vrba_lambda_max_initial": 10.0,
            "vrba_lambda_cap": 20.0,
            "vrba_stage_steps": 50_000,
            "vrba_initial_fraction": 0.1,
        },
    )
    values = attention.update(
        {"physics": torch.zeros(4, dtype=torch.float64)}, step=1
    )["physics"]
    assert torch.allclose(values, torch.full_like(values, 1.009))


def test_vrba_global_controller_fixes_physics_weight_and_balances_other_terms():
    torch.set_default_dtype(torch.float64)
    problem = BurgersProblem(PROBLEM, torch.device("cpu"), torch.float64)
    model = MLP(2, 8).double()
    sets = problem.sample_sets(16, 8, 8, make_generator(21))
    losses = problem.component_losses(model, sets)
    controller = VRBAGlobalController(
        list(losses),
        {
            "vrba_gradient_ema": 0.0,
            "vrba_global_ema": 0.0,
            "vrba_global_weight_min": 1e-6,
            "vrba_global_weight_max": 1e6,
        },
    )
    weights = controller.update(losses, model)
    assert weights["physics"] == 1.0
    assert all(math.isfinite(value) and value > 0.0 for value in weights.values())
