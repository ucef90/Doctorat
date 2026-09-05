from __future__ import annotations

import torch

from .base import (
    PointSets,
    attach_observations,
    component_losses_from_residuals,
)


class WaveProblem:
    """Wave equation u_tt-c²u_xx=0 with an analytical standing-wave solution."""

    base_loss_names = ("physics", "initial", "boundary")

    def __init__(self, config: dict, device: torch.device, dtype: torch.dtype) -> None:
        self.x_min = float(config.get("x_min", 0.0))
        self.x_max = float(config.get("x_max", 1.0))
        self.t_min = float(config.get("t_min", 0.0))
        self.t_max = float(config.get("t_max", 1.0))
        self.wave_speed = float(config.get("wave_speed", 1.0))
        self.device = device
        self.dtype = dtype
        self.domain_lower = (self.t_min, self.x_min)
        self.domain_upper = (self.t_max, self.x_max)
        self.observation_config: dict = {}

    def sample_collocation(self, n: int, generator: torch.Generator) -> torch.Tensor:
        raw = torch.rand((n, 2), generator=generator, device=self.device, dtype=self.dtype)
        t = self.t_min + (self.t_max - self.t_min) * raw[:, :1]
        x = self.x_min + (self.x_max - self.x_min) * raw[:, 1:]
        return torch.cat((t, x), dim=1)

    def sample_initial(self, n: int, generator: torch.Generator) -> torch.Tensor:
        x = self.x_min + (self.x_max - self.x_min) * torch.rand(
            (n, 1), generator=generator, device=self.device, dtype=self.dtype
        )
        return torch.cat((torch.full_like(x, self.t_min), x), dim=1)

    def sample_boundary(self, n: int, generator: torch.Generator) -> torch.Tensor:
        t = self.t_min + (self.t_max - self.t_min) * torch.rand(
            (n, 1), generator=generator, device=self.device, dtype=self.dtype
        )
        side = torch.randint(0, 2, (n, 1), generator=generator, device=self.device)
        x = torch.where(side == 0, torch.full_like(t, self.x_min), torch.full_like(t, self.x_max))
        return torch.cat((t, x), dim=1)

    def exact(self, points: torch.Tensor) -> torch.Tensor:
        t, x = points[:, :1], points[:, 1:2]
        length = self.x_max - self.x_min
        phase = torch.pi * (x - self.x_min) / length
        frequency = torch.pi * self.wave_speed / length
        return torch.sin(phase) * torch.cos(frequency * (t - self.t_min))

    def sample_sets(
        self, n_r: int, n_i: int, n_b: int, generator: torch.Generator,
        n_observations: int = 0, noise_generator: torch.Generator | None = None,
        observation_config: dict | None = None,
    ) -> PointSets:
        self.observation_config = observation_config or {}
        sets = PointSets(
            self.sample_collocation(n_r, generator),
            self.sample_initial(n_i, generator),
            self.sample_boundary(n_b, generator),
        )
        return attach_observations(
            self, sets, n_observations, generator, noise_generator, observation_config
        )

    def residual(self, model, points: torch.Tensor, create_graph: bool = True) -> torch.Tensor:
        tx = points.detach().clone().requires_grad_(True)
        u = model(tx)
        gradient = torch.autograd.grad(
            u, tx, torch.ones_like(u), create_graph=True, retain_graph=True
        )[0]
        u_t, u_x = gradient[:, :1], gradient[:, 1:2]
        u_tt = torch.autograd.grad(
            u_t, tx, torch.ones_like(u_t), create_graph=create_graph, retain_graph=True
        )[0][:, :1]
        u_xx = torch.autograd.grad(
            u_x, tx, torch.ones_like(u_x), create_graph=create_graph, retain_graph=True
        )[0][:, 1:2]
        return u_tt - self.wave_speed**2 * u_xx

    def component_residuals(
        self, model, sets: PointSets
    ) -> dict[str, torch.Tensor]:
        initial = sets.initial.detach().clone().requires_grad_(True)
        initial_u = model(initial)
        initial_ut = torch.autograd.grad(
            initial_u, initial, torch.ones_like(initial_u),
            create_graph=True, retain_graph=True,
        )[0][:, :1]
        # Scaling by sqrt(2) preserves the historical sum of the displacement
        # and velocity MSEs when the two vectors are concatenated.
        scale = 2.0**0.5
        residuals = {
            "physics": self.residual(model, sets.collocation),
            "initial": torch.cat(
                (scale * (initial_u - self.exact(initial)), scale * initial_ut), dim=0
            ),
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
        t = torch.linspace(self.t_min, self.t_max, nt, device=self.device, dtype=self.dtype)
        x = torch.linspace(self.x_min, self.x_max, nx, device=self.device, dtype=self.dtype)
        tt, xx = torch.meshgrid(t, x, indexing="ij")
        return torch.stack((tt.flatten(), xx.flatten()), dim=1)

    def reference_at(self, points: torch.Tensor, nx: int, dt: float) -> torch.Tensor:
        del nx, dt
        return self.exact(points)
