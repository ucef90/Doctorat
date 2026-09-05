from __future__ import annotations

import numpy as np
import torch

from .base import (
    PointSets,
    attach_observations,
    component_losses_from_residuals,
)


class BurgersProblem:
    """Burgers 1D: u_t + u u_x - nu u_xx = 0, u(0,x)=-sin(pi x), u(t,±1)=0."""

    base_loss_names = ("physics", "initial", "boundary")

    def __init__(self, config: dict, device: torch.device, dtype: torch.dtype) -> None:
        self.x_min = float(config["x_min"])
        self.x_max = float(config["x_max"])
        self.t_min = float(config["t_min"])
        self.t_max = float(config["t_max"])
        self.viscosity = float(config["viscosity"])
        self.reference_method = config.get("reference_method", "rusanov")
        if self.reference_method not in {"rusanov", "cole_hopf"}:
            raise ValueError("Unknown Burgers reference method")
        if self.reference_method == "cole_hopf" and (
            self.x_min != -1 or self.x_max != 1 or self.t_min != 0
        ):
            raise ValueError("Cole-Hopf reference requires x in [-1,1] and t_min=0")
        self.device = device
        self.dtype = dtype
        self.domain_lower = (self.t_min, self.x_min)
        self.domain_upper = (self.t_max, self.x_max)
        self.observation_config: dict = {}
        self._reference_cache: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None
        self._reference_cache_key: tuple[int, float] | None = None

    def sample_collocation(self, n: int, generator: torch.Generator) -> torch.Tensor:
        raw = torch.rand((n, 2), generator=generator, device=self.device, dtype=self.dtype)
        t = self.t_min + (self.t_max - self.t_min) * raw[:, :1]
        x = self.x_min + (self.x_max - self.x_min) * raw[:, 1:]
        return torch.cat((t, x), dim=1)

    def sample_initial(self, n: int, generator: torch.Generator) -> torch.Tensor:
        x = torch.rand((n, 1), generator=generator, device=self.device, dtype=self.dtype)
        x = self.x_min + (self.x_max - self.x_min) * x
        t = torch.full_like(x, self.t_min)
        return torch.cat((t, x), dim=1)

    def sample_boundary(self, n: int, generator: torch.Generator) -> torch.Tensor:
        t = torch.rand((n, 1), generator=generator, device=self.device, dtype=self.dtype)
        t = self.t_min + (self.t_max - self.t_min) * t
        side = torch.randint(0, 2, (n, 1), generator=generator, device=self.device)
        x = torch.where(side == 0, torch.full_like(t, self.x_min), torch.full_like(t, self.x_max))
        return torch.cat((t, x), dim=1)

    def sample_sets(
        self, n_r: int, n_i: int, n_b: int, generator: torch.Generator,
        n_observations: int = 0, noise_generator: torch.Generator | None = None,
        observation_config: dict | None = None,
    ) -> PointSets:
        self.observation_config = observation_config or {}
        sets = PointSets(
            collocation=self.sample_collocation(n_r, generator),
            initial=self.sample_initial(n_i, generator),
            boundary=self.sample_boundary(n_b, generator),
        )
        return attach_observations(
            self, sets, n_observations, generator, noise_generator, observation_config
        )

    @staticmethod
    def initial_target(points: torch.Tensor) -> torch.Tensor:
        return -torch.sin(torch.pi * points[:, 1:2])

    @staticmethod
    def boundary_target(points: torch.Tensor) -> torch.Tensor:
        return torch.zeros_like(points[:, :1])

    def residual(self, model: torch.nn.Module, points: torch.Tensor, create_graph: bool = True) -> torch.Tensor:
        tx = points.detach().clone().requires_grad_(True)
        u = model(tx)
        grad_u = torch.autograd.grad(
            u, tx, grad_outputs=torch.ones_like(u), create_graph=True, retain_graph=True
        )[0]
        u_t = grad_u[:, :1]
        u_x = grad_u[:, 1:2]
        grad_ux = torch.autograd.grad(
            u_x, tx, grad_outputs=torch.ones_like(u_x), create_graph=create_graph, retain_graph=True
        )[0]
        u_xx = grad_ux[:, 1:2]
        return u_t + u * u_x - self.viscosity * u_xx

    def component_residuals(
        self, model: torch.nn.Module, sets: PointSets
    ) -> dict[str, torch.Tensor]:
        residuals = {
            "physics": self.residual(model, sets.collocation, create_graph=True),
            "initial": model(sets.initial) - self.initial_target(sets.initial),
            "boundary": model(sets.boundary) - self.boundary_target(sets.boundary),
        }
        if sets.observations is not None and sets.observation_targets is not None:
            residuals["data"] = model(sets.observations) - sets.observation_targets
        return residuals

    def component_losses(
        self,
        model: torch.nn.Module,
        sets: PointSets,
        physics_weights: torch.Tensor | None = None,
        component_multipliers: dict[str, torch.Tensor] | None = None,
    ) -> dict[str, torch.Tensor]:
        return component_losses_from_residuals(
            self.component_residuals(model, sets),
            self.observation_config,
            physics_weights,
            component_multipliers,
        )

    def evaluation_grid(self, nx: int, nt: int) -> torch.Tensor:
        t = torch.linspace(self.t_min, self.t_max, nt, device=self.device, dtype=self.dtype)
        x = torch.linspace(self.x_min, self.x_max, nx, device=self.device, dtype=self.dtype)
        tt, xx = torch.meshgrid(t, x, indexing="ij")
        return torch.stack((tt.reshape(-1), xx.reshape(-1)), dim=1)

    def _solve_reference(self, nx: int, dt_requested: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = np.linspace(self.x_min, self.x_max, nx, dtype=np.float64)
        dx = x[1] - x[0]
        # CFL conservatif pour le flux de Rusanov et la diffusion explicite.
        stable_dt = min(dt_requested, 0.20 * dx, 0.20 * dx * dx / max(self.viscosity, 1e-12))
        n_steps = int(np.ceil((self.t_max - self.t_min) / stable_dt))
        dt = (self.t_max - self.t_min) / n_steps
        u = -np.sin(np.pi * x)
        times = np.linspace(self.t_min, self.t_max, n_steps + 1)
        history = np.empty((n_steps + 1, nx), dtype=np.float64)
        history[0] = u

        def rhs(values: np.ndarray) -> np.ndarray:
            derivative = np.zeros_like(values)
            left = values[:-1]
            right = values[1:]
            wave_speed = np.maximum(np.abs(left), np.abs(right))
            flux = 0.25 * (left * left + right * right) - 0.5 * wave_speed * (right - left)
            uxx = (values[2:] - 2.0 * values[1:-1] + values[:-2]) / (dx * dx)
            derivative[1:-1] = -(flux[1:] - flux[:-1]) / dx + self.viscosity * uxx
            return derivative

        for index in range(n_steps):
            k1 = rhs(u)
            k2 = rhs(u + 0.5 * dt * k1)
            k3 = rhs(u + 0.5 * dt * k2)
            k4 = rhs(u + dt * k3)
            u = u + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            u[0] = 0.0
            u[-1] = 0.0
            history[index + 1] = u
        if not np.isfinite(history).all():
            raise FloatingPointError("Le solveur de référence de Burgers a produit une valeur non finie.")
        return times, x, history

    def reference_at(self, points: torch.Tensor, nx: int, dt: float) -> torch.Tensor:
        if self.reference_method == "cole_hopf":
            from ..burgers_reference import cole_hopf
            values = cole_hopf(points.detach().cpu().numpy(), self.viscosity, order=128)
            return torch.as_tensor(values, device=self.device, dtype=self.dtype)
        cache_key = (int(nx), float(dt))
        if self._reference_cache is None or self._reference_cache_key != cache_key:
            self._reference_cache = self._solve_reference(nx, dt)
            self._reference_cache_key = cache_key
        times, x_grid, values = self._reference_cache
        query = points.detach().cpu().numpy()
        t_idx = np.clip(np.searchsorted(times, query[:, 0], side="right") - 1, 0, len(times) - 2)
        x_idx = np.clip(np.searchsorted(x_grid, query[:, 1], side="right") - 1, 0, len(x_grid) - 2)
        wt = (query[:, 0] - times[t_idx]) / (times[t_idx + 1] - times[t_idx])
        wx = (query[:, 1] - x_grid[x_idx]) / (x_grid[x_idx + 1] - x_grid[x_idx])
        v00 = values[t_idx, x_idx]
        v01 = values[t_idx, x_idx + 1]
        v10 = values[t_idx + 1, x_idx]
        v11 = values[t_idx + 1, x_idx + 1]
        interpolated = (
            (1 - wt) * ((1 - wx) * v00 + wx * v01)
            + wt * ((1 - wx) * v10 + wx * v11)
        )
        return torch.as_tensor(interpolated[:, None], device=self.device, dtype=self.dtype)
