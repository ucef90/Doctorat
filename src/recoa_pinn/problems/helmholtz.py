from __future__ import annotations

import torch

from .base import (
    PointSets,
    attach_observations,
    component_losses_from_residuals,
    empty_points,
)


class HelmholtzProblem:
    """2D manufactured Helmholtz equation Δu+k²u=f on a unit square."""

    base_loss_names = ("physics", "boundary")

    def __init__(self, config: dict, device: torch.device, dtype: torch.dtype) -> None:
        self.x_min = float(config.get("x_min", 0.0))
        self.x_max = float(config.get("x_max", 1.0))
        self.y_min = float(config.get("y_min", 0.0))
        self.y_max = float(config.get("y_max", 1.0))
        self.wavenumber = float(config.get("wavenumber", 10.0))
        self.mode_x = int(config.get("mode_x", 1))
        self.mode_y = int(config.get("mode_y", 1))
        self.device = device
        self.dtype = dtype
        self.domain_lower = (self.x_min, self.y_min)
        self.domain_upper = (self.x_max, self.y_max)
        self.observation_config: dict = {}

    def sample_collocation(self, n: int, generator: torch.Generator) -> torch.Tensor:
        raw = torch.rand((n, 2), generator=generator, device=self.device, dtype=self.dtype)
        x = self.x_min + (self.x_max - self.x_min) * raw[:, :1]
        y = self.y_min + (self.y_max - self.y_min) * raw[:, 1:]
        return torch.cat((x, y), dim=1)

    def sample_boundary(self, n: int, generator: torch.Generator) -> torch.Tensor:
        raw = torch.rand((n, 2), generator=generator, device=self.device, dtype=self.dtype)
        side = torch.randint(0, 4, (n, 1), generator=generator, device=self.device)
        x = self.x_min + (self.x_max - self.x_min) * raw[:, :1]
        y = self.y_min + (self.y_max - self.y_min) * raw[:, 1:]
        x = torch.where(side == 0, torch.full_like(x, self.x_min), x)
        x = torch.where(side == 1, torch.full_like(x, self.x_max), x)
        y = torch.where(side == 2, torch.full_like(y, self.y_min), y)
        y = torch.where(side == 3, torch.full_like(y, self.y_max), y)
        return torch.cat((x, y), dim=1)

    def exact(self, points: torch.Tensor) -> torch.Tensor:
        x, y = points[:, :1], points[:, 1:2]
        px = self.mode_x * torch.pi * (x - self.x_min) / (self.x_max - self.x_min)
        py = self.mode_y * torch.pi * (y - self.y_min) / (self.y_max - self.y_min)
        return torch.sin(px) * torch.sin(py)

    def forcing(self, points: torch.Tensor) -> torch.Tensor:
        eigenvalue = (
            (self.mode_x * torch.pi / (self.x_max - self.x_min)) ** 2
            + (self.mode_y * torch.pi / (self.y_max - self.y_min)) ** 2
        )
        return (self.wavenumber**2 - eigenvalue) * self.exact(points)

    def sample_sets(
        self, n_r: int, n_i: int, n_b: int, generator: torch.Generator,
        n_observations: int = 0, noise_generator: torch.Generator | None = None,
        observation_config: dict | None = None,
    ) -> PointSets:
        del n_i
        self.observation_config = observation_config or {}
        sets = PointSets(
            self.sample_collocation(n_r, generator),
            empty_points(self.device, self.dtype),
            self.sample_boundary(n_b, generator),
        )
        return attach_observations(
            self, sets, n_observations, generator, noise_generator, observation_config
        )

    def residual(self, model, points: torch.Tensor, create_graph: bool = True) -> torch.Tensor:
        xy = points.detach().clone().requires_grad_(True)
        u = model(xy)
        gradient = torch.autograd.grad(
            u, xy, torch.ones_like(u), create_graph=True, retain_graph=True
        )[0]
        u_x, u_y = gradient[:, :1], gradient[:, 1:2]
        u_xx = torch.autograd.grad(
            u_x, xy, torch.ones_like(u_x), create_graph=create_graph, retain_graph=True
        )[0][:, :1]
        u_yy = torch.autograd.grad(
            u_y, xy, torch.ones_like(u_y), create_graph=create_graph, retain_graph=True
        )[0][:, 1:2]
        return u_xx + u_yy + self.wavenumber**2 * u - self.forcing(xy)

    def component_residuals(
        self, model, sets: PointSets
    ) -> dict[str, torch.Tensor]:
        residuals = {
            "physics": self.residual(model, sets.collocation),
            "boundary": model(sets.boundary) - self.exact(sets.boundary),
        }
        if sets.observations is not None and sets.observation_targets is not None:
            residuals["data"] = model(sets.observations) - sets.observation_targets
        return residuals

    def component_losses(
        self,
        model,
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
        x = torch.linspace(self.x_min, self.x_max, nx, device=self.device, dtype=self.dtype)
        y = torch.linspace(self.y_min, self.y_max, nt, device=self.device, dtype=self.dtype)
        xx, yy = torch.meshgrid(x, y, indexing="ij")
        return torch.stack((xx.flatten(), yy.flatten()), dim=1)

    def reference_at(self, points: torch.Tensor, nx: int, dt: float) -> torch.Tensor:
        del nx, dt
        return self.exact(points)
