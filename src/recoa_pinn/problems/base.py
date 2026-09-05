from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import torch


@dataclass
class PointSets:
    """Points used by the physics, condition and optional observation losses."""

    collocation: torch.Tensor
    initial: torch.Tensor
    boundary: torch.Tensor
    observations: torch.Tensor | None = None
    observation_targets: torch.Tensor | None = None


class Problem(Protocol):
    device: torch.device
    dtype: torch.dtype

    def sample_collocation(self, n: int, generator: torch.Generator) -> torch.Tensor: ...

    def sample_sets(
        self,
        n_r: int,
        n_i: int,
        n_b: int,
        generator: torch.Generator,
        n_observations: int = 0,
        noise_generator: torch.Generator | None = None,
        observation_config: dict | None = None,
    ) -> PointSets: ...

    def component_losses(
        self,
        model: torch.nn.Module,
        sets: PointSets,
        physics_weights: torch.Tensor | None = None,
        component_multipliers: dict[str, torch.Tensor] | None = None,
    ) -> dict[str, torch.Tensor]: ...

    def component_residuals(
        self, model: torch.nn.Module, sets: PointSets
    ) -> dict[str, torch.Tensor]: ...

    def residual(
        self, model: torch.nn.Module, points: torch.Tensor, create_graph: bool = True
    ) -> torch.Tensor: ...

    def evaluation_grid(self, nx: int, nt: int) -> torch.Tensor: ...

    def reference_at(self, points: torch.Tensor, nx: int, dt: float) -> torch.Tensor: ...


def empty_points(device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    return torch.empty((0, 2), device=device, dtype=dtype)


def physics_residual_loss(
    residual: torch.Tensor, physics_weights: torch.Tensor | None = None
) -> torch.Tensor:
    """Compute the usual or measure-corrected mean squared PDE residual."""

    squared = residual.square().reshape(-1)
    if physics_weights is None:
        return squared.mean()
    # Local import avoids making the base problem module own adaptation logic.
    from ..adaptation import importance_weighted_mean

    return importance_weighted_mean(squared, physics_weights)


def multiplier_weighted_residual_loss(
    residual: torch.Tensor, multiplier: torch.Tensor
) -> torch.Tensor:
    """Return ``mean((lambda_i * r_i)**2)`` for local attention weights."""

    flattened = residual.reshape(-1)
    if multiplier.ndim != 1 or multiplier.shape[0] != flattened.shape[0]:
        raise ValueError("Un multiplicateur local est requis par résidu.")
    if not torch.isfinite(multiplier).all() or torch.any(multiplier < 0):
        raise ValueError("Les multiplicateurs locaux doivent être finis et positifs.")
    return torch.mean((flattened * multiplier.detach()).square())


def component_losses_from_residuals(
    residuals: dict[str, torch.Tensor],
    observation_config: dict | None = None,
    physics_weights: torch.Tensor | None = None,
    component_multipliers: dict[str, torch.Tensor] | None = None,
) -> dict[str, torch.Tensor]:
    """Build component losses without recomputing predictions or PDE residuals."""

    if component_multipliers and physics_weights is not None:
        raise ValueError(
            "La correction de mesure et les multiplicateurs vRBA ne peuvent pas "
            "pondérer simultanément le résidu physique."
        )
    losses: dict[str, torch.Tensor] = {}
    for name, residual in residuals.items():
        if component_multipliers is not None and name in component_multipliers:
            losses[name] = multiplier_weighted_residual_loss(
                residual, component_multipliers[name]
            )
        elif name == "physics":
            losses[name] = physics_residual_loss(residual, physics_weights)
        elif name == "data":
            kind = str((observation_config or {}).get("loss", "mse")).lower()
            losses[name] = observation_residual_loss(residual, kind)
        else:
            losses[name] = residual.square().mean()
    return losses


def sample_domain_design(
    problem,
    n: int,
    design: str,
    seed: int,
    generator: torch.Generator,
) -> torch.Tensor:
    """Generate random, Latin-hypercube or scrambled Sobol audit points."""

    design = design.lower()
    if design == "random":
        return problem.sample_collocation(n, generator)
    if design == "latin_hypercube":
        columns = []
        for _ in range(2):
            permutation = torch.randperm(n, generator=generator, device=problem.device)
            jitter = torch.rand(
                n, generator=generator, device=problem.device, dtype=problem.dtype
            )
            columns.append((permutation.to(problem.dtype) + jitter) / n)
        unit = torch.stack(columns, dim=1)
    elif design == "sobol":
        engine = torch.quasirandom.SobolEngine(2, scramble=True, seed=int(seed))
        unit = engine.draw(n).to(device=problem.device, dtype=problem.dtype)
    else:
        raise ValueError(f"Plan d'audit inconnu : {design}")
    lower = torch.tensor(problem.domain_lower, device=problem.device, dtype=problem.dtype)
    upper = torch.tensor(problem.domain_upper, device=problem.device, dtype=problem.dtype)
    return lower + (upper - lower) * unit


def corrupt_targets(
    clean: torch.Tensor,
    config: dict | None,
    generator: torch.Generator | None,
) -> torch.Tensor:
    """Apply a pre-registered corruption without touching the clean test target."""

    if not config or generator is None or clean.numel() == 0:
        return clean.detach().clone()
    kind = str(config.get("noise_kind", "none")).lower()
    level = float(config.get("noise_level", 0.0))
    target = clean.detach().clone()
    scale = max(
        float(clean.detach().std(unbiased=False)),
        float(clean.detach().abs().mean()),
        1e-12,
    )
    if kind == "gaussian" and level > 0.0:
        target += level * scale * torch.randn(
            target.shape, generator=generator, device=target.device, dtype=target.dtype
        )
    elif kind == "heteroscedastic" and level > 0.0:
        local_scale = scale + clean.detach().abs()
        target += level * local_scale * torch.randn(
            target.shape, generator=generator, device=target.device, dtype=target.dtype
        )
    elif kind == "correlated" and level > 0.0:
        raw = torch.randn(
            target.shape, generator=generator, device=target.device, dtype=target.dtype
        )
        ordered = raw.flatten()
        for index in range(1, ordered.numel()):
            ordered[index] = 0.8 * ordered[index - 1] + 0.6 * ordered[index]
        target += level * scale * ordered.reshape_as(target)
    elif kind not in {"none", "gaussian", "heteroscedastic", "correlated"}:
        raise ValueError(f"Type de bruit inconnu : {kind}")

    outlier_fraction = float(config.get("outlier_fraction", 0.0))
    if outlier_fraction > 0.0:
        count = min(target.numel(), max(1, round(outlier_fraction * target.numel())))
        indices = torch.randperm(
            target.numel(), generator=generator, device=target.device
        )[:count]
        flattened = target.flatten()
        signs = torch.where(
            torch.rand(count, generator=generator, device=target.device) < 0.5,
            -torch.ones(count, device=target.device, dtype=target.dtype),
            torch.ones(count, device=target.device, dtype=target.dtype),
        )
        flattened[indices] += (
            float(config.get("outlier_scale", 5.0)) * max(level, 0.01) * scale * signs
        )
    return target


def observation_loss(prediction: torch.Tensor, target: torch.Tensor, kind: str) -> torch.Tensor:
    return observation_residual_loss(prediction - target, kind)


def observation_residual_loss(error: torch.Tensor, kind: str) -> torch.Tensor:
    if kind == "mse":
        return error.square().mean()
    if kind == "huber":
        return torch.nn.functional.huber_loss(error, torch.zeros_like(error))
    raise ValueError(f"Perte d'observation inconnue : {kind}")


def attach_observations(
    problem,
    sets: PointSets,
    n: int,
    generator: torch.Generator,
    noise_generator: torch.Generator | None,
    config: dict | None,
) -> PointSets:
    if n <= 0:
        return sets
    points = problem.sample_collocation(n, generator)
    clean = problem.reference_at(points, nx=257, dt=1e-4)
    missing_pattern = str((config or {}).get("missing_pattern", "none")).lower()
    missing_fraction = float((config or {}).get("missing_fraction", 0.0))
    if missing_fraction > 0.0 and missing_pattern != "none":
        keep_count = max(1, round((1.0 - missing_fraction) * n))
        if missing_pattern == "random":
            keep = torch.randperm(n, generator=generator, device=points.device)[:keep_count]
        elif missing_pattern in {"first_coordinate_block", "time_block"}:
            order = torch.argsort(points[:, 0])
            remove_count = n - keep_count
            start = max(0, (n - remove_count) // 2)
            remove = order[start:start + remove_count]
            mask = torch.ones(n, dtype=torch.bool, device=points.device)
            mask[remove] = False
            keep = torch.where(mask)[0]
        elif missing_pattern == "space_block":
            order = torch.argsort(points[:, 1])
            remove_count = n - keep_count
            start = max(0, (n - remove_count) // 2)
            remove = order[start:start + remove_count]
            mask = torch.ones(n, dtype=torch.bool, device=points.device)
            mask[remove] = False
            keep = torch.where(mask)[0]
        else:
            raise ValueError(f"Motif de données manquantes inconnu : {missing_pattern}")
        points = points[keep]
        clean = clean[keep]
    sets.observations = points
    sets.observation_targets = corrupt_targets(clean, config, noise_generator)
    return sets


def add_observation_component(
    losses: dict[str, torch.Tensor],
    model: torch.nn.Module,
    sets: PointSets,
    observation_config: dict | None,
) -> dict[str, torch.Tensor]:
    if sets.observations is not None and sets.observation_targets is not None:
        kind = str((observation_config or {}).get("loss", "mse")).lower()
        losses["data"] = observation_loss(
            model(sets.observations), sets.observation_targets, kind
        )
    return losses
