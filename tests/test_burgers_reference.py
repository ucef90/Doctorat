import numpy as np
import pytest
import torch

from recoa_pinn.burgers_reference import cole_hopf
from recoa_pinn.problems.burgers import BurgersProblem
from test_burgers import CONFIG


def test_cole_hopf_initial_boundary_symmetry_and_convergence():
    x = np.linspace(-1, 1, 161)
    initial = np.column_stack([np.zeros(len(x)), x])
    np.testing.assert_allclose(cole_hopf(initial)[:, 0], -np.sin(np.pi*x), atol=1e-14)
    t, x = np.meshgrid(np.linspace(0, 1, 41), x, indexing="ij")
    points = np.column_stack([t.ravel(), x.ravel()])
    a, b = cole_hopf(points, order=128), cole_hopf(points, order=256)
    np.testing.assert_allclose(a, b, atol=1e-10, rtol=1e-10)
    grid = b.reshape(t.shape)
    np.testing.assert_allclose(grid, -grid[:, ::-1], atol=1e-12)
    np.testing.assert_allclose(grid[:, [0, -1]], 0, atol=1e-12)
    assert np.max(np.abs(grid)) <= 1 + 1e-12


def test_cole_hopf_satisfies_pde_away_from_shock():
    # Independent centered finite differences of the integral solution.
    pts = np.array([[.1, -.4], [.2, .3], [.6, -.5], [.9, .6]])
    h = 1e-4
    u = cole_hopf(pts)
    ut = (cole_hopf(pts + [h, 0]) - cole_hopf(pts - [h, 0]))/(2*h)
    up, um = cole_hopf(pts + [0, h]), cole_hopf(pts - [0, h])
    residual = ut + u*(up-um)/(2*h) - CONFIG['viscosity']*(up - 2*u + um)/h**2
    assert np.max(np.abs(residual)) < 2e-6


def test_reference_cache_accounts_for_time_step(monkeypatch):
    problem = BurgersProblem(CONFIG, torch.device('cpu'), torch.float64)
    calls = []
    original = problem._solve_reference
    def counted(nx, dt):
        calls.append((nx, dt))
        return original(nx, dt)
    monkeypatch.setattr(problem, '_solve_reference', counted)
    points = torch.tensor([[.1, .2]], dtype=torch.float64)
    problem.reference_at(points, 17, .01)
    problem.reference_at(points, 17, .01)
    problem.reference_at(points, 17, .005)
    assert calls == [(17, .01), (17, .005)]


def test_cole_hopf_opt_in_routes_observations_and_evaluation():
    cfg = dict(CONFIG, reference_method='cole_hopf')
    problem = BurgersProblem(cfg, torch.device('cpu'), torch.float64)
    points = torch.tensor([[.2, .3], [.9, -.02]], dtype=torch.float64)
    expected = cole_hopf(points.numpy())
    np.testing.assert_allclose(problem.reference_at(points, 17, .01).numpy(), expected)


@pytest.mark.parametrize('points', [[[0, 0, 0]], [[-1, 0]], [[0, np.nan]]])
def test_invalid_points_rejected(points):
    with pytest.raises(ValueError):
        cole_hopf(points)
