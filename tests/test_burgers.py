import math

import torch
from torch import nn

from recoa_pinn.problems.burgers import BurgersProblem
from recoa_pinn.reproducibility import make_generator


CONFIG = {
    "x_min": -1.0, "x_max": 1.0, "t_min": 0.0, "t_max": 1.0,
    "viscosity": 0.01 / math.pi,
}


class PolynomialModel(nn.Module):
    def forward(self, tx):
        t, x = tx[:, :1], tx[:, 1:2]
        return t + x.square()


def test_autograd_burgers_residual_matches_closed_form():
    problem = BurgersProblem(CONFIG, torch.device("cpu"), torch.float64)
    points = torch.tensor([[0.2, -0.4], [0.7, 0.3]], dtype=torch.float64)
    residual = problem.residual(PolynomialModel(), points, create_graph=False)
    x = points[:, 1:2]
    u = points[:, :1] + x.square()
    expected = 1.0 + u * (2.0 * x) - problem.viscosity * 2.0
    assert torch.allclose(residual, expected, atol=1e-12, rtol=1e-12)


def test_samples_respect_domain_and_cardinality():
    problem = BurgersProblem(CONFIG, torch.device("cpu"), torch.float64)
    sets = problem.sample_sets(31, 17, 19, make_generator(7))
    assert sets.collocation.shape == (31, 2)
    assert sets.initial.shape == (17, 2)
    assert sets.boundary.shape == (19, 2)
    assert torch.all((sets.collocation[:, 0] >= 0) & (sets.collocation[:, 0] <= 1))
    assert torch.all((sets.collocation[:, 1] >= -1) & (sets.collocation[:, 1] <= 1))
    assert torch.all(sets.initial[:, 0] == 0)
    assert torch.all(sets.boundary[:, 1].abs() == 1)


def test_reference_solver_is_finite_and_respects_boundary_conditions():
    problem = BurgersProblem(CONFIG, torch.device("cpu"), torch.float64)
    points = problem.evaluation_grid(nx=17, nt=9)
    reference = problem.reference_at(points, nx=65, dt=0.001)
    assert torch.isfinite(reference).all()
    grid = reference.reshape(9, 17)
    assert torch.allclose(grid[:, 0], torch.zeros(9, dtype=torch.float64), atol=1e-12)
    assert torch.allclose(grid[:, -1], torch.zeros(9, dtype=torch.float64), atol=1e-12)
