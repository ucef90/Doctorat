from __future__ import annotations

from dataclasses import dataclass
from math import log as math_log

import torch

from .problems.base import PointSets, Problem


@dataclass
class ControllerState:
    weights: dict[str, float]
    initial_losses: dict[str, float] | None = None
    smoothed_gradients: dict[str, float] | None = None


class LossController:
    def __init__(self, names: list[str], config: dict) -> None:
        self.names = names
        self.beta = float(config["ema_beta"])
        self.alpha = float(config["progress_alpha"])
        self.minimum = float(config["weight_min"])
        self.maximum = float(config["weight_max"])
        self.state = ControllerState(weights={name: 1.0 for name in names})

    @staticmethod
    def gradient_norm(loss: torch.Tensor, model: torch.nn.Module) -> torch.Tensor:
        gradients = torch.autograd.grad(
            loss,
            tuple(model.parameters()),
            retain_graph=True,
            create_graph=False,
            allow_unused=True,
        )
        squares = [gradient.detach().square().sum() for gradient in gradients if gradient is not None]
        return torch.sqrt(torch.stack(squares).sum() + torch.finfo(loss.dtype).eps)

    def update(self, losses: dict[str, torch.Tensor], model: torch.nn.Module) -> dict[str, float]:
        current = {name: max(float(losses[name].detach()), 1e-30) for name in self.names}
        gradients = {name: max(float(self.gradient_norm(losses[name], model)), 1e-30) for name in self.names}
        if self.state.initial_losses is None:
            self.state.initial_losses = current.copy()
        if self.state.smoothed_gradients is None:
            smoothed = gradients.copy()
        else:
            smoothed = {
                name: self.beta * self.state.smoothed_gradients[name] + (1.0 - self.beta) * gradients[name]
                for name in self.names
            }
        progress = {name: current[name] / self.state.initial_losses[name] for name in self.names}
        mean_gradient = sum(smoothed.values()) / len(smoothed)
        raw = {
            name: (mean_gradient / smoothed[name]) * (progress[name] ** self.alpha)
            for name in self.names
        }
        raw_mean = sum(raw.values()) / len(raw)
        targets = {name: min(self.maximum, max(self.minimum, raw[name] / raw_mean)) for name in self.names}
        target_mean = sum(targets.values()) / len(targets)
        targets = {name: value / target_mean for name, value in targets.items()}
        self.state.weights = {
            name: self.beta * self.state.weights[name] + (1.0 - self.beta) * targets[name]
            for name in self.names
        }
        self.state.smoothed_gradients = smoothed
        return self.state.weights.copy()


class VRBAAttention:
    """Persistent local vRBA multipliers for a fixed common-backbone design.

    The implementation follows the exponential and quadratic updates in
    Toscano et al.  Multipliers are detached state: gradients flow through the
    residuals, not through the adaptive update itself.
    """

    def __init__(self, names: list[str], config: dict) -> None:
        self.names = names
        self.potential = str(config.get("vrba_potential", "exponential")).lower()
        self.eta = float(config.get("vrba_eta", 0.01))
        self.phi = float(config.get("vrba_phi", 0.8))
        self.temperature_scale = float(config.get("vrba_temperature_scale", 1.0))
        self.lambda_max_initial = float(config.get("vrba_lambda_max_initial", 10.0))
        self.lambda_cap = float(config.get("vrba_lambda_cap", 20.0))
        self.stage_steps = int(config.get("vrba_stage_steps", 50_000))
        self.initial_fraction = float(config.get("vrba_initial_fraction", 0.1))
        self.multipliers: dict[str, torch.Tensor] = {}
        self.last_temperature: dict[str, float] = {}
        self.updates = 0

    def _lambda_max(self, step: int) -> float:
        return min(
            self.lambda_cap,
            self.lambda_max_initial + max(step - 1, 0) / self.stage_steps,
        )

    def decay(self, step: int) -> float:
        return 1.0 - self.eta / self._lambda_max(step)

    def initialize(self, residuals: dict[str, torch.Tensor]) -> None:
        initial = self.initial_fraction * self.lambda_max_initial
        self.multipliers = {
            name: torch.full(
                (residuals[name].numel(),),
                initial,
                device=residuals[name].device,
                dtype=residuals[name].dtype,
            )
            for name in self.names
        }

    def _normalized_target(
        self, residual: torch.Tensor, step: int
    ) -> tuple[torch.Tensor, float]:
        magnitude = residual.detach().abs().reshape(-1)
        maximum = magnitude.max()
        tiny = torch.finfo(magnitude.dtype).tiny
        if float(maximum) <= tiny:
            return torch.ones_like(magnitude), 0.0
        if self.potential == "exponential":
            temperature = self.temperature_scale * maximum / math_log(step + 2.0)
            safe_temperature = temperature.clamp_min(tiny)
            # q/max(q), evaluated without constructing an overflowing exp(r/eps).
            normalized = torch.exp((magnitude - maximum) / safe_temperature)
            return normalized, float(temperature)
        if self.potential == "quadratic":
            return magnitude / maximum, float(magnitude.mean())
        raise ValueError(f"Potentiel vRBA inconnu : {self.potential}")

    def update(
        self, residuals: dict[str, torch.Tensor], step: int
    ) -> dict[str, torch.Tensor]:
        if not self.multipliers:
            self.initialize(residuals)
        decay = self.decay(step)
        updated: dict[str, torch.Tensor] = {}
        temperatures: dict[str, float] = {}
        for name in self.names:
            current = self.multipliers[name]
            if current.numel() != residuals[name].numel():
                raise ValueError(
                    "vRBA importance weighting exige des ensembles fixes de cardinalité constante."
                )
            normalized, temperature = self._normalized_target(residuals[name], step)
            target = self.phi * normalized + (1.0 - self.phi)
            updated[name] = (decay * current + self.eta * target).detach()
            temperatures[name] = temperature
        self.multipliers = updated
        self.last_temperature = temperatures
        self.updates += 1
        return {name: value for name, value in updated.items()}

    def statistics(self, name: str = "physics") -> dict[str, float]:
        if name not in self.multipliers:
            return {
                "effective_sample_fraction": 1.0,
                "mean": 1.0,
                "minimum": 1.0,
                "maximum": 1.0,
                "multiplier_mean": 1.0,
                "multiplier_minimum": 1.0,
                "multiplier_maximum": 1.0,
                "temperature": 0.0,
            }
        multiplier = self.multipliers[name]
        # The loss contains lambda squared; ESS is therefore computed for the
        # effective loss weights lambda^2.
        stats = importance_statistics(multiplier.square())
        return {
            **stats,
            "multiplier_mean": float(multiplier.mean()),
            "multiplier_minimum": float(multiplier.min()),
            "multiplier_maximum": float(multiplier.max()),
            "temperature": float(self.last_temperature.get(name, 0.0)),
        }


class VRBAGlobalController:
    """Self-scaling of PINN loss components used by the vRBA paper."""

    def __init__(self, names: list[str], config: dict) -> None:
        if "physics" not in names:
            raise ValueError("Le contrôleur global vRBA requiert une perte physique.")
        self.names = names
        self.gradient_beta = float(config.get("vrba_gradient_ema", 0.99))
        self.weight_beta = float(config.get("vrba_global_ema", 0.99975))
        self.minimum = float(config.get("vrba_global_weight_min", 1e-6))
        self.maximum = float(config.get("vrba_global_weight_max", 1e6))
        self.weights = {name: 1.0 for name in names}
        self.smoothed_gradients: dict[str, float] | None = None

    def update(
        self, losses: dict[str, torch.Tensor], model: torch.nn.Module
    ) -> dict[str, float]:
        gradients = {
            name: max(float(LossController.gradient_norm(losses[name], model)), 1e-30)
            for name in self.names
        }
        if self.smoothed_gradients is None:
            smoothed = gradients
        else:
            smoothed = {
                name: self.gradient_beta * self.smoothed_gradients[name]
                + (1.0 - self.gradient_beta) * gradients[name]
                for name in self.names
            }
        physics_gradient = smoothed["physics"]
        self.weights["physics"] = 1.0
        for name in self.names:
            if name == "physics":
                continue
            target = physics_gradient / smoothed[name]
            target = min(self.maximum, max(self.minimum, target))
            self.weights[name] = (
                self.weight_beta * self.weights[name]
                + (1.0 - self.weight_beta) * target
            )
        self.smoothed_gradients = smoothed
        return self.weights.copy()


class ResidualSampler:
    def __init__(self, config: dict) -> None:
        self.candidate_size = int(config["candidate_size"])
        self.power = float(config["residual_power"])
        self.mix = float(config["residual_mix"])
        self.replace_fraction = float(config["replace_fraction"])
        self.last_stats = {
            "effective_sample_fraction": 1.0,
            "entropy_fraction": 1.0,
            "max_probability": 1.0 / self.candidate_size,
        }

    def _proposal(
        self,
        problem: Problem,
        model: torch.nn.Module,
        generator: torch.Generator,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Build the residual-based proposal on a fresh uniform candidate pool."""

        candidates = problem.sample_collocation(self.candidate_size, generator)
        with torch.enable_grad():
            score = problem.residual(model, candidates, create_graph=False).detach().abs().flatten()
        score = (score + torch.finfo(score.dtype).eps).pow(self.power)
        adaptive_probability = score / score.sum()
        probability = (1.0 - self.mix) / self.candidate_size + self.mix * adaptive_probability
        effective_sample_size = 1.0 / probability.square().sum()
        entropy = -(probability * torch.log(probability.clamp_min(torch.finfo(probability.dtype).tiny))).sum()
        self.last_stats = {
            "effective_sample_fraction": float(effective_sample_size / self.candidate_size),
            "entropy_fraction": float(
                entropy / torch.log(torch.tensor(float(self.candidate_size), device=entropy.device))
            ),
            "max_probability": float(probability.max()),
        }
        return candidates, probability

    @staticmethod
    def _replacement_count(current: torch.Tensor, fraction: float) -> int:
        return min(current.shape[0], max(1, round(fraction * current.shape[0])))

    def update(
        self,
        problem: Problem,
        model: torch.nn.Module,
        current: torch.Tensor,
        generator: torch.Generator,
    ) -> torch.Tensor:
        candidates, probability = self._proposal(problem, model, generator)
        n_replace = self._replacement_count(current, self.replace_fraction)
        selected = torch.multinomial(probability, n_replace, replacement=False, generator=generator)
        keep_count = current.shape[0] - n_replace
        if keep_count:
            keep = torch.randperm(current.shape[0], generator=generator, device=current.device)[:keep_count]
            return torch.cat((current[keep], candidates[selected]), dim=0).detach()
        return candidates[selected].detach()

    def update_measure_corrected(
        self,
        problem: Problem,
        model: torch.nn.Module,
        current: torch.Tensor,
        current_importance_weights: torch.Tensor,
        generator: torch.Generator,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Refresh points and retain their target/proposal importance weights.

        Candidates are drawn uniformly. New points are sampled *with replacement*
        from the residual proposal so that their Hansen--Hurwitz weight is exactly
        ``p_i / q_i = 1 / (N q_i)`` on the finite candidate population. Points
        retained from earlier refreshes keep the weight attached when they were
        drawn.
        """

        if current_importance_weights.ndim != 1:
            raise ValueError("Les poids d'importance doivent former un vecteur.")
        if current_importance_weights.shape[0] != current.shape[0]:
            raise ValueError("Un poids d'importance est requis par point de collocation.")
        candidates, probability = self._proposal(problem, model, generator)
        n_replace = self._replacement_count(current, self.replace_fraction)
        selected = torch.multinomial(
            probability, n_replace, replacement=True, generator=generator
        )
        selected_weights = importance_weights_from_probability(probability, selected)
        keep_count = current.shape[0] - n_replace
        if keep_count:
            keep = torch.randperm(
                current.shape[0], generator=generator, device=current.device
            )[:keep_count]
            points = torch.cat((current[keep], candidates[selected]), dim=0)
            importance_weights = torch.cat(
                (current_importance_weights[keep], selected_weights), dim=0
            )
        else:
            points = candidates[selected]
            importance_weights = selected_weights
        return points.detach(), importance_weights.detach()


def importance_weights_from_probability(
    probability: torch.Tensor, selected: torch.Tensor
) -> torch.Tensor:
    """Return target/proposal weights for a uniform finite target measure."""

    if probability.ndim != 1 or probability.numel() == 0:
        raise ValueError("La probabilité de proposition doit être un vecteur non vide.")
    if not torch.isfinite(probability).all() or torch.any(probability <= 0):
        raise ValueError("Les probabilités de proposition doivent être finies et positives.")
    normalizer = probability.sum()
    if not torch.isclose(
        normalizer,
        torch.ones((), device=probability.device, dtype=probability.dtype),
        rtol=1e-6,
        atol=1e-8,
    ):
        raise ValueError("Les probabilités de proposition doivent sommer à un.")
    return (1.0 / (probability.numel() * probability[selected])).detach()


def importance_weighted_mean(values: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
    """Hansen--Hurwitz estimate of a uniform mean from proposal samples."""

    flattened = values.reshape(-1)
    if weights.ndim != 1 or weights.shape[0] != flattened.shape[0]:
        raise ValueError("Le nombre de poids doit correspondre au nombre de valeurs.")
    if not torch.isfinite(weights).all() or torch.any(weights <= 0):
        raise ValueError("Les poids d'importance doivent être finis et positifs.")
    return torch.mean(flattened * weights.detach())


def importance_statistics(weights: torch.Tensor) -> dict[str, float]:
    """Diagnostics of the current importance-weighted collocation batch."""

    if weights.ndim != 1 or weights.numel() == 0:
        raise ValueError("Les poids d'importance doivent former un vecteur non vide.")
    detached = weights.detach()
    effective_size = detached.sum().square() / detached.square().sum().clamp_min(
        torch.finfo(detached.dtype).eps
    )
    return {
        "effective_sample_fraction": float(effective_size / detached.numel()),
        "mean": float(detached.mean()),
        "minimum": float(detached.min()),
        "maximum": float(detached.max()),
    }


def kde_volume_physics_weights(
    points: torch.Tensor,
    domain_lower: tuple[float, ...],
    domain_upper: tuple[float, ...],
    bandwidth: float | None = None,
    bandwidth_scale: float = 1.0,
) -> torch.Tensor:
    """Estimate VW-PINN residual weights from the collocation-point density.

    Coordinates are first mapped to the unit hypercube so that time and space
    have comparable scales. A Gaussian KDE estimates the sampling density at
    every collocation point. Its reciprocal is the local volume proxy ``V_i``.
    VW-PINNs minimize ``sum((V_i r_i)^2) / sum(V_i^2)``; the returned vector is
    therefore normalized so that ``mean(weight_i * r_i^2)`` is exactly that
    expression.

    When no bandwidth is supplied, Scott's isotropic rule
    ``h = n**(-1 / (d + 4))`` is used. This is a documented reproducible choice
    for the common-backbone baseline, not a claim of reproducing every training
    detail of the original VW-PINN experiments.
    """

    if points.ndim != 2 or points.shape[0] == 0:
        raise ValueError("Les points KDE doivent former une matrice non vide.")
    dimension = points.shape[1]
    if len(domain_lower) != dimension or len(domain_upper) != dimension:
        raise ValueError("Les bornes du domaine doivent correspondre aux coordonnées.")
    if bandwidth is not None and bandwidth <= 0.0:
        raise ValueError("La largeur de bande KDE doit être strictement positive.")
    if bandwidth_scale <= 0.0:
        raise ValueError("Le facteur de largeur de bande doit être strictement positif.")

    lower = torch.as_tensor(domain_lower, device=points.device, dtype=points.dtype)
    upper = torch.as_tensor(domain_upper, device=points.device, dtype=points.dtype)
    span = upper - lower
    if torch.any(span <= 0):
        raise ValueError("Chaque borne supérieure doit dépasser la borne inférieure.")
    normalized = (points.detach() - lower) / span
    n_points = normalized.shape[0]
    selected_bandwidth = (
        float(bandwidth)
        if bandwidth is not None
        else n_points ** (-1.0 / (dimension + 4.0))
    )
    selected_bandwidth *= float(bandwidth_scale)

    squared_distance = torch.cdist(normalized, normalized).square()
    kernel = torch.exp(-0.5 * squared_distance / (selected_bandwidth**2))
    # The Gaussian normalizing constant cancels after reciprocal-volume
    # normalization; retaining only the kernel improves numerical clarity.
    density = kernel.mean(dim=1).clamp_min(torch.finfo(points.dtype).tiny)
    volume = density.reciprocal()
    squared_volume = volume.square()
    weights = n_points * squared_volume / squared_volume.sum()
    return weights.detach()


def weighted_total(losses: dict[str, torch.Tensor], weights: dict[str, float]) -> torch.Tensor:
    return sum(losses[name] * weights[name] for name in losses)


def component_gradient_norms(
    losses: dict[str, torch.Tensor], model: torch.nn.Module
) -> dict[str, float]:
    return {
        name: max(float(LossController.gradient_norm(loss, model)), 1e-30)
        for name, loss in losses.items()
    }


def normalized_distribution(values: dict[str, float]) -> dict[str, float]:
    total = sum(max(value, 0.0) for value in values.values())
    if total <= 0.0:
        return {name: 1.0 / len(values) for name in values}
    return {name: max(value, 0.0) / total for name, value in values.items()}


def distribution_total_variation(first: dict[str, float], second: dict[str, float]) -> float:
    first_normalized = normalized_distribution(first)
    second_normalized = normalized_distribution(second)
    return 0.5 * sum(
        abs(first_normalized[name] - second_normalized[name]) for name in first_normalized
    )


def clone_sets(sets: PointSets) -> PointSets:
    return PointSets(
        collocation=sets.collocation.detach().clone(),
        initial=sets.initial.detach().clone(),
        boundary=sets.boundary.detach().clone(),
        observations=(
            sets.observations.detach().clone() if sets.observations is not None else None
        ),
        observation_targets=(
            sets.observation_targets.detach().clone()
            if sets.observation_targets is not None else None
        ),
    )
