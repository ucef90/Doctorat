import torch
from torch import nn

from recoa_pinn.problems import AllenCahnProblem, HelmholtzProblem, WaveProblem
from recoa_pinn.problems.base import PointSets, attach_observations, corrupt_targets
from recoa_pinn.reproducibility import make_generator


class ExactModel(nn.Module):
    def __init__(self, exact):
        super().__init__()
        self.exact = exact

    def forward(self, points):
        return self.exact(points)


def test_manufactured_allen_cahn_solution_has_zero_residual():
    problem = AllenCahnProblem(
        {"diffusion": 0.001, "reaction": 5.0}, torch.device("cpu"), torch.float64
    )
    points = problem.sample_collocation(17, make_generator(1))
    residual = problem.residual(ExactModel(problem.exact), points, create_graph=False)
    assert torch.allclose(residual, torch.zeros_like(residual), atol=1e-10)


def test_exact_wave_solution_has_zero_residual():
    problem = WaveProblem({"wave_speed": 1.5}, torch.device("cpu"), torch.float64)
    points = problem.sample_collocation(17, make_generator(2))
    residual = problem.residual(ExactModel(problem.exact), points, create_graph=False)
    assert torch.allclose(residual, torch.zeros_like(residual), atol=1e-10)


def test_manufactured_helmholtz_solution_has_zero_residual():
    problem = HelmholtzProblem(
        {"wavenumber": 10.0, "mode_x": 2, "mode_y": 3},
        torch.device("cpu"), torch.float64,
    )
    points = problem.sample_collocation(17, make_generator(3))
    residual = problem.residual(ExactModel(problem.exact), points, create_graph=False)
    assert torch.allclose(residual, torch.zeros_like(residual), atol=1e-9)


def test_corruption_is_reproducible_and_does_not_modify_clean_target():
    clean = torch.linspace(-1.0, 1.0, 31, dtype=torch.float64)[:, None]
    snapshot = clean.clone()
    config = {"noise_kind": "gaussian", "noise_level": 0.1, "outlier_fraction": 0.1}
    first = corrupt_targets(clean, config, make_generator(91))
    second = corrupt_targets(clean, config, make_generator(91))
    assert torch.equal(clean, snapshot)
    assert torch.equal(first, second)
    assert not torch.equal(first, clean)


def test_block_missingness_removes_a_contiguous_sensor_region():
    problem = WaveProblem({"wave_speed": 1.0}, torch.device("cpu"), torch.float64)
    empty = torch.empty((0, 2), dtype=torch.float64)
    sets = PointSets(empty, empty, empty)
    result = attach_observations(
        problem, sets, 20, make_generator(7), make_generator(8),
        {"missing_pattern": "time_block", "missing_fraction": 0.5},
    )
    assert result.observations.shape[0] == 10
    assert result.observation_targets.shape[0] == 10
