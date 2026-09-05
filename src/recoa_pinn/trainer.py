from __future__ import annotations

import csv
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .adaptation import (
    LossController,
    ResidualSampler,
    VRBAAttention,
    VRBAGlobalController,
    component_gradient_norms,
    distribution_total_variation,
    importance_statistics,
    kde_volume_physics_weights,
    weighted_total,
)
from .config import dump_config, resolved_config
from .model import MLP
from .problems import make_problem
from .problems.base import component_losses_from_residuals, sample_domain_design
from .reproducibility import (
    configure_reproducibility,
    make_generator,
    resolve_device,
    resolve_dtype,
    save_environment,
    tensor_fingerprint,
)


LOSS_NAMES = ("physics", "initial", "boundary", "data")
METRIC_FIELDS = [
    "step", "elapsed_seconds", "total_loss",
    *(f"{name}_loss" for name in LOSS_NAMES),
    *(f"weight_{name}" for name in LOSS_NAMES),
    "controller_weight_step_l1", "controller_weight_tv", "controller_updates",
    "gradient_distribution_tv", "loss_distribution_tv", "physics_gradient_log_gap",
    "sampler_effective_sample_fraction", "sampler_entropy_fraction",
    "sampler_max_probability", "optimization_residual_evaluations",
    "importance_effective_sample_fraction", "importance_weight_mean",
    "importance_weight_min", "importance_weight_max",
    "vrba_attention_effective_sample_fraction", "vrba_multiplier_mean",
    "vrba_multiplier_min", "vrba_multiplier_max", "vrba_temperature",
    "vrba_local_updates",
    "kde_pairwise_distance_evaluations",
    "controller_residual_evaluations", "sampler_residual_evaluations",
    "diagnostic_residual_evaluations", "residual_evaluations", "relative_l2",
    "max_abs_error",
]


def _run_directory(config: dict[str, Any], method: str, seed: int) -> Path:
    root = Path(config["experiment"]["output_dir"])
    return root / config["experiment"]["name"] / method / f"seed_{seed:05d}"


def _evaluate(model: torch.nn.Module, problem, config: dict) -> dict[str, float]:
    evaluation = config["evaluation"]
    points = problem.evaluation_grid(int(evaluation["nx"]), int(evaluation["nt"]))
    reference = problem.reference_at(
        points, int(evaluation["reference_nx"]), float(evaluation["reference_dt"])
    )
    with torch.no_grad():
        prediction = model(points)
    difference = prediction - reference
    denominator = torch.linalg.vector_norm(reference).clamp_min(torch.finfo(reference.dtype).eps)
    relative_l2 = torch.linalg.vector_norm(difference) / denominator
    return {
        "relative_l2": float(relative_l2),
        "max_abs_error": float(difference.abs().max()),
    }


def _diagnose_distribution_shift(
    model,
    problem,
    training_sets,
    audit_sets,
    training_physics_weights: torch.Tensor | None = None,
    training_component_multipliers: dict[str, torch.Tensor] | None = None,
) -> dict[str, float]:
    training_losses = problem.component_losses(
        model,
        training_sets,
        physics_weights=training_physics_weights,
        component_multipliers=training_component_multipliers,
    )
    audit_losses = problem.component_losses(model, audit_sets)
    training_loss_values = {name: float(value.detach()) for name, value in training_losses.items()}
    audit_loss_values = {name: float(value.detach()) for name, value in audit_losses.items()}
    training_gradients = component_gradient_norms(training_losses, model)
    audit_gradients = component_gradient_norms(audit_losses, model)
    return {
        "gradient_distribution_tv": distribution_total_variation(
            training_gradients, audit_gradients
        ),
        "loss_distribution_tv": distribution_total_variation(
            training_loss_values, audit_loss_values
        ),
        "physics_gradient_log_gap": abs(
            math.log(training_gradients["physics"] / audit_gradients["physics"])
        ),
    }


def _effective_observation_count(observation_config: dict) -> int:
    base = int(observation_config["n_observations"])
    fraction = float(observation_config["fraction"])
    return max(1, round(base * fraction)) if base > 0 and fraction > 0.0 else 0


def _make_audit_sets(
    problem, training_sets, adaptation, ablation, generator, observations, audit_seed
):
    multiplier = float(ablation["audit_size_multiplier"])
    sets = problem.sample_sets(
        max(1, round(int(adaptation["audit_collocation"]) * multiplier)),
        max(0, round(int(adaptation["audit_initial"]) * multiplier)),
        max(1, round(int(adaptation["audit_boundary"]) * multiplier)),
        generator, 0, None, observations,
    )
    sets.collocation = sample_domain_design(
        problem, sets.collocation.shape[0], str(ablation.get("audit_design", "random")),
        audit_seed, generator,
    )
    # No extra labelled measurements are given to M6. Both methods reuse the
    # same sensors; only physics and known-condition quadrature are decoupled.
    sets.observations = training_sets.observations
    sets.observation_targets = training_sets.observation_targets
    return sets


def _safe_correlation(first: list[float], second: list[float]) -> float | None:
    if len(first) < 3 or len(first) != len(second):
        return None
    x, y = np.asarray(first), np.asarray(second)
    if np.std(x) == 0.0 or np.std(y) == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def train(config: dict[str, Any], method: str, seed: int) -> dict[str, Any]:
    resolved = resolved_config(config, method, seed)
    experiment = resolved["experiment"]
    training = resolved["training"]
    adaptation = resolved["adaptation"]
    observations = resolved["observations"]
    ablation = resolved["ablation"]
    configure_reproducibility(seed, bool(experiment["deterministic"]))
    if "num_threads" in training:
        torch.set_num_threads(int(training["num_threads"]))
    device = resolve_device(str(experiment["device"]))
    dtype = resolve_dtype(str(experiment["dtype"]))
    torch.set_default_dtype(dtype)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    run_dir = _run_directory(resolved, method, seed)
    run_dir.mkdir(parents=True, exist_ok=True)
    dump_config(resolved, run_dir / "config.resolved.yaml")
    save_environment(run_dir / "environment.json")

    generators = {
        "train": make_generator(seed + 101, str(device)),
        "audit": make_generator(seed + 202, str(device)),
        "sampler": make_generator(seed + 303, str(device)),
        "noise": make_generator(seed + 404, str(device)),
    }
    problem = make_problem(resolved["problem"], device, dtype)
    model = MLP(**resolved["model"]).to(device=device, dtype=dtype)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(training["learning_rate"]))
    n_observations = _effective_observation_count(observations)
    sets = problem.sample_sets(
        int(training["n_collocation"]), int(training.get("n_initial", 0)),
        int(training["n_boundary"]), generators["train"], n_observations,
        generators["noise"], observations,
    )
    n_observations = (
        int(sets.observations.shape[0]) if sets.observations is not None else 0
    )
    physics_importance_weights = torch.ones(
        sets.collocation.shape[0], device=device, dtype=dtype
    )
    kde_pairwise_distance_evaluations = 0
    if method in {"vw", "vwca"}:
        physics_importance_weights = kde_volume_physics_weights(
            sets.collocation,
            problem.domain_lower,
            problem.domain_upper,
            bandwidth=adaptation.get("vw_bandwidth"),
            bandwidth_scale=float(adaptation.get("vw_bandwidth_scale", 1.0)),
        )
        kde_pairwise_distance_evaluations += sets.collocation.shape[0] ** 2
    audit_sets = _make_audit_sets(
        problem, sets, adaptation, ablation, generators["audit"], observations, seed + 202
    )
    names = list(problem.base_loss_names) + (["data"] if n_observations else [])
    initial_fingerprints = {
        "model": tensor_fingerprint(dict(model.state_dict())),
        "training_sets": tensor_fingerprint(vars(sets)),
        "audit_sets": tensor_fingerprint(vars(audit_sets)),
    }
    controller_config = dict(adaptation)
    if bool(ablation.get("disable_smoothing", False)):
        controller_config["ema_beta"] = 0.0
    if bool(ablation.get("disable_bounds", False)):
        controller_config["weight_min"] = 1e-12
        controller_config["weight_max"] = 1e12
    controller = LossController(names, controller_config)
    sampler_config = dict(adaptation)
    if bool(ablation.get("disable_uniform_floor", False)):
        sampler_config["residual_mix"] = 1.0
    sampler = ResidualSampler(sampler_config)
    vrba_local_enabled = method == "vrba" and adaptation.get("vrba_local_enabled", True)
    vrba_global_enabled = method == "vrba" and adaptation.get("vrba_global_enabled", True)
    vrba_attention = VRBAAttention(names, adaptation) if vrba_local_enabled else None
    vrba_global_controller = (
        VRBAGlobalController(names, adaptation) if vrba_global_enabled else None
    )
    component_multipliers: dict[str, torch.Tensor] | None = None
    weights = {name: 1.0 for name in names}
    start = time.perf_counter()
    failed = False
    failure_reason: str | None = None
    last_eval = {"relative_l2": math.nan, "max_abs_error": math.nan}
    diagnostics = {
        "gradient_distribution_tv": math.nan,
        "loss_distribution_tv": math.nan,
        "physics_gradient_log_gap": math.nan,
    }
    controller_weight_tv = 0.0
    controller_weight_step_l1 = 0.0
    controller_updates = 0
    budget = {"optimization": 0, "controller": 0, "sampler": 0, "diagnostic": 0}
    concentration_history: list[float] = []
    gradient_gap_history: list[float] = []
    gradient_tv_history: list[float] = []
    loss_tv_history: list[float] = []
    weight_jump_history: list[float] = []

    with (run_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=METRIC_FIELDS)
        writer.writeheader()
        for step in range(1, int(training["steps"]) + 1):
            rotation_every = int(ablation.get("audit_rotation_every", 0))
            if method == "m6" and rotation_every > 0 and step > 1 and step % rotation_every == 0:
                audit_sets = _make_audit_sets(
                    problem, sets, adaptation, ablation, generators["audit"], observations,
                    seed + 202 + step,
                )

            sampler_due = (
                method in {"m3", "m5", "m6", "m7u", "m7", "vw", "vwca"}
                and step > 1
                and step % int(adaptation["sampler_every"]) == 0
            )
            if sampler_due:
                if method in {"m7u", "m7"}:
                    sets.collocation, physics_importance_weights = (
                        sampler.update_measure_corrected(
                            problem,
                            model,
                            sets.collocation,
                            physics_importance_weights,
                            generators["sampler"],
                        )
                    )
                else:
                    sets.collocation = sampler.update(
                        problem, model, sets.collocation, generators["sampler"]
                    )
                    if method in {"vw", "vwca"}:
                        physics_importance_weights = kde_volume_physics_weights(
                            sets.collocation,
                            problem.domain_lower,
                            problem.domain_upper,
                            bandwidth=adaptation.get("vw_bandwidth"),
                            bandwidth_scale=float(
                                adaptation.get("vw_bandwidth_scale", 1.0)
                            ),
                        )
                        kde_pairwise_distance_evaluations += (
                            sets.collocation.shape[0] ** 2
                        )
                budget["sampler"] += int(adaptation["candidate_size"])

            controller_due = (
                method in {"m1", "m5", "m6", "m7u", "m7", "vwca"}
                and (step == 1 or step % int(adaptation["controller_every"]) == 0)
            )
            if controller_due:
                controller_sets = (
                    sets
                    if method in {"m1", "m5", "m7u", "m7", "vwca"}
                    else audit_sets
                )
                controller_losses = problem.component_losses(
                    model,
                    controller_sets,
                    physics_weights=(
                        physics_importance_weights
                        if method in {"m7", "vwca"}
                        else None
                    ),
                )
                budget["controller"] += int(controller_sets.collocation.shape[0])
                previous_weights = weights.copy()
                weights = controller.update(controller_losses, model)
                controller_weight_step_l1 = sum(
                    abs(weights[name] - previous_weights[name]) for name in names
                )
                controller_weight_tv += controller_weight_step_l1
                controller_updates += 1
                weight_jump_history.append(controller_weight_step_l1)
            else:
                controller_weight_step_l1 = 0.0

            optimizer.zero_grad(set_to_none=True)
            if method == "vrba":
                residuals = problem.component_residuals(model, sets)
                local_due = (
                    step == 1
                    or step % int(adaptation.get("vrba_local_every", 1)) == 0
                )
                if local_due and vrba_attention is not None:
                    component_multipliers = vrba_attention.update(residuals, step)
                losses = component_losses_from_residuals(
                    residuals,
                    observations,
                    component_multipliers=component_multipliers,
                )
                global_due = (
                    step == 1
                    or step % int(adaptation.get("vrba_global_every", 1)) == 0
                )
                if global_due and vrba_global_controller is not None:
                    previous_weights = weights.copy()
                    weights = vrba_global_controller.update(losses, model)
                    controller_weight_step_l1 = sum(
                        abs(weights[name] - previous_weights[name]) for name in names
                    )
                    controller_weight_tv += controller_weight_step_l1
                    controller_updates += 1
                    weight_jump_history.append(controller_weight_step_l1)
            else:
                losses = problem.component_losses(
                    model,
                    sets,
                    physics_weights=(
                        physics_importance_weights
                        if method in {"m7", "vw", "vwca"}
                        else None
                    ),
                )
            budget["optimization"] += int(sets.collocation.shape[0])
            total = weighted_total(losses, weights)
            if not torch.isfinite(total):
                failed = True
                failure_reason = f"Perte non finie à l'étape {step}"
                break
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), float(training["grad_clip"]))
            optimizer.step()

            if (
                step == 1 or step % int(adaptation["diagnostic_every"]) == 0
                or step == int(training["steps"])
            ):
                diagnostics = _diagnose_distribution_shift(
                    model,
                    problem,
                    sets,
                    audit_sets,
                    training_physics_weights=(
                        physics_importance_weights
                        if method in {"m7", "vw", "vwca"}
                        else None
                    ),
                    training_component_multipliers=(
                        component_multipliers if method == "vrba" else None
                    ),
                )
                budget["diagnostic"] += int(
                    sets.collocation.shape[0] + audit_sets.collocation.shape[0]
                )
                concentration_history.append(
                    1.0
                    - (
                        vrba_attention.statistics()["effective_sample_fraction"]
                        if vrba_attention is not None
                        else sampler.last_stats["effective_sample_fraction"]
                    )
                )
                gradient_gap_history.append(diagnostics["physics_gradient_log_gap"])
                gradient_tv_history.append(diagnostics["gradient_distribution_tv"])
                loss_tv_history.append(diagnostics["loss_distribution_tv"])

            should_log = (
                step == 1 or step % int(training["log_every"]) == 0
                or step == int(training["steps"])
            )
            should_eval = (
                step % int(training["eval_every"]) == 0
                or step == int(training["steps"])
            )
            if should_eval:
                last_eval = _evaluate(model, problem, resolved)
            if should_log:
                importance = importance_statistics(physics_importance_weights)
                vrba_stats = (
                    vrba_attention.statistics()
                    if vrba_attention is not None
                    else {
                        "effective_sample_fraction": 1.0,
                        "multiplier_mean": math.nan,
                        "multiplier_minimum": math.nan,
                        "multiplier_maximum": math.nan,
                        "temperature": math.nan,
                    }
                )
                row = {
                    "step": step,
                    "elapsed_seconds": time.perf_counter() - start,
                    "total_loss": float(total.detach()),
                    **{
                        f"{name}_loss": (
                            float(losses[name].detach()) if name in losses else math.nan
                        ) for name in LOSS_NAMES
                    },
                    **{f"weight_{name}": weights.get(name, math.nan) for name in LOSS_NAMES},
                    "controller_weight_step_l1": controller_weight_step_l1,
                    "controller_weight_tv": controller_weight_tv,
                    "controller_updates": controller_updates,
                    **diagnostics,
                    "sampler_effective_sample_fraction": sampler.last_stats[
                        "effective_sample_fraction"
                    ],
                    "sampler_entropy_fraction": sampler.last_stats["entropy_fraction"],
                    "sampler_max_probability": sampler.last_stats["max_probability"],
                    "importance_effective_sample_fraction": importance[
                        "effective_sample_fraction"
                    ],
                    "importance_weight_mean": importance["mean"],
                    "importance_weight_min": importance["minimum"],
                    "importance_weight_max": importance["maximum"],
                    "vrba_attention_effective_sample_fraction": vrba_stats[
                        "effective_sample_fraction"
                    ],
                    "vrba_multiplier_mean": vrba_stats["multiplier_mean"],
                    "vrba_multiplier_min": vrba_stats["multiplier_minimum"],
                    "vrba_multiplier_max": vrba_stats["multiplier_maximum"],
                    "vrba_temperature": vrba_stats["temperature"],
                    "vrba_local_updates": (
                        vrba_attention.updates if vrba_attention is not None else 0
                    ),
                    "kde_pairwise_distance_evaluations": (
                        kde_pairwise_distance_evaluations
                    ),
                    "optimization_residual_evaluations": budget["optimization"],
                    "controller_residual_evaluations": budget["controller"],
                    "sampler_residual_evaluations": budget["sampler"],
                    "diagnostic_residual_evaluations": budget["diagnostic"],
                    "residual_evaluations": sum(budget.values()),
                    **last_eval,
                }
                writer.writerow(row)
                stream.flush()
            if step % int(training["checkpoint_every"]) == 0:
                torch.save(model.state_dict(), run_dir / f"checkpoint_{step:07d}.pt")

    elapsed = time.perf_counter() - start
    if not failed and math.isnan(last_eval["relative_l2"]):
        last_eval = _evaluate(model, problem, resolved)
    torch.save(model.state_dict(), run_dir / "model.pt")
    controller_cardinality = (
        int(sets.collocation.shape[0])
        if method in {"m1", "m5", "m7u", "m7", "vwca", "vrba"}
        else int(audit_sets.collocation.shape[0])
    )
    importance = importance_statistics(physics_importance_weights)
    vrba_stats = (
        vrba_attention.statistics()
        if vrba_attention is not None
        else {
            "effective_sample_fraction": 1.0,
            "mean": 1.0,
            "minimum": 1.0,
            "maximum": 1.0,
            "multiplier_mean": None,
            "multiplier_minimum": None,
            "multiplier_maximum": None,
            "temperature": None,
        }
    )
    summary = {
        "status": "failed" if failed else "succeeded",
        "failure_reason": failure_reason,
        "method": method,
        "problem": str(resolved["problem"]["name"]),
        "controller_source": (
            "adaptive_training_sets" if method == "m5"
            else "adaptive_training_sets_matched_resampling" if method == "m7u"
            else "measure_corrected_adaptive_training_sets" if method == "m7"
            else "volume_weighted_adaptive_training_sets" if method == "vwca"
            else ("vrba_local_attention_and_global_self_scaling" if vrba_local_enabled
                  else "vrba_global_self_scaling") if vrba_global_enabled
            else "fixed_component_weights" if method == "vrba"
            else "fixed_component_weights" if method == "vw"
            else "uniform_training_sets" if method == "m1"
            else "fixed_audit_sets" if method == "m6" else "fixed_weights"
        ),
        "seed": seed,
        "steps_requested": int(training["steps"]),
        "steps_completed": step if not failed else step - 1,
        "initial_fingerprints": initial_fingerprints,
        "elapsed_seconds": elapsed,
        "controller_weight_tv": controller_weight_tv,
        "controller_updates": controller_updates,
        "controller_weight_tv_per_update": controller_weight_tv / max(controller_updates, 1),
        "mean_controller_weight_jump": (
            float(np.mean(weight_jump_history)) if weight_jump_history else 0.0
        ),
        "bias_concentration_correlation": _safe_correlation(
            concentration_history, gradient_gap_history
        ),
        "temporal_mean_gradient_distribution_tv": float(np.mean(gradient_tv_history)),
        "temporal_mean_loss_distribution_tv": float(np.mean(loss_tv_history)),
        "temporal_mean_physics_gradient_log_gap": float(np.mean(gradient_gap_history)),
        **diagnostics,
        "sampler_statistics": sampler.last_stats,
        "importance_statistics": importance,
        "importance_effective_sample_fraction": importance[
            "effective_sample_fraction"
        ],
        "importance_weight_mean": importance["mean"],
        "importance_weight_max": importance["maximum"],
        "vrba_attention_statistics": vrba_stats,
        "vrba_attention_effective_sample_fraction": vrba_stats[
            "effective_sample_fraction"
        ],
        "vrba_multiplier_mean": vrba_stats["multiplier_mean"],
        "vrba_multiplier_max": vrba_stats["multiplier_maximum"],
        "kde_pairwise_distance_evaluations": kde_pairwise_distance_evaluations,
        "measure_correction": {
            "enabled": method in {"m7", "vw", "vwca"},
            "exact_proposal_correction": method == "m7",
            "kde_volume_weighting": method in {"vw", "vwca"},
            "matched_uncorrected_control": method == "m7u",
            "estimator": (
                "hansen_hurwitz_finite_candidate" if method == "m7"
                else "gaussian_kde_inverse_density_volume_squared"
                if method in {"vw", "vwca"}
                else "none"
            ),
            "sampling_with_replacement": method in {"m7u", "m7"},
            "kde_bandwidth": adaptation.get("vw_bandwidth"),
            "kde_bandwidth_scale": float(
                adaptation.get("vw_bandwidth_scale", 1.0)
            ),
        },
        "adaptive_objective": {
            "enabled": method == "vrba",
            "method": "vrba_common_backbone_weighting" if method == "vrba" else "none",
            "potential": adaptation.get("vrba_potential") if method == "vrba" else None,
            "importance_weighting": bool(vrba_local_enabled),
            "local_enabled": bool(vrba_local_enabled),
            "global_enabled": bool(vrba_global_enabled),
            "importance_sampling": False,
            "local_updates": vrba_attention.updates if vrba_attention is not None else 0,
            "eta": float(adaptation.get("vrba_eta", 0.01)),
            "phi": float(adaptation.get("vrba_phi", 0.8)),
            "lambda_max_initial": float(
                adaptation.get("vrba_lambda_max_initial", 10.0)
            ),
            "lambda_cap": float(adaptation.get("vrba_lambda_cap", 20.0)),
            "temperature_scale": float(
                adaptation.get("vrba_temperature_scale", 1.0)
            ),
        },
        "budget": {
            **budget,
            "total_residual_evaluations": sum(budget.values()),
            "training_collocation_cardinality": int(sets.collocation.shape[0]),
            "audit_collocation_cardinality": int(audit_sets.collocation.shape[0]),
            "controller_collocation_cardinality": controller_cardinality,
            "equal_controller_cardinality": (
                int(sets.collocation.shape[0]) == int(audit_sets.collocation.shape[0])
            ),
        },
        "residual_evaluations": sum(budget.values()),
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "observations": {**observations, "effective_count": n_observations},
        "ablation": ablation,
        "peak_gpu_memory_bytes": (
            torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None
        ),
        **last_eval,
        "final_weights": weights,
        "run_dir": str(run_dir.resolve()),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _bootstrap_median_difference(
    first: list[float], second: list[float], repeats: int = 10_000
) -> list[float]:
    differences = np.asarray(second, dtype=np.float64) - np.asarray(first, dtype=np.float64)
    generator = np.random.default_rng(20260904)
    indices = generator.integers(0, len(differences), size=(repeats, len(differences)))
    medians = np.median(differences[indices], axis=1)
    return [float(value) for value in np.quantile(medians, [0.025, 0.975])]


def _two_sided_sign_test(differences: np.ndarray) -> float | None:
    nonzero = differences[differences != 0.0]
    n = len(nonzero)
    if n == 0:
        return None
    wins = min(int(np.sum(nonzero < 0.0)), int(np.sum(nonzero > 0.0)))
    probability = 2.0 * sum(math.comb(n, k) for k in range(wins + 1)) / (2**n)
    return min(1.0, probability)


def _paired_block(
    indexed: dict[tuple[str, int], dict], first: str, second: str,
    seeds: list[int], field: str,
) -> dict[str, Any] | None:
    paired = [seed for seed in seeds if (first, seed) in indexed and (second, seed) in indexed]
    if not paired:
        return None
    first_values = [indexed[(first, seed)][field] for seed in paired]
    second_values = [indexed[(second, seed)][field] for seed in paired]
    differences = np.asarray(second_values) - np.asarray(first_values)
    return {
        "paired_seeds": paired,
        "field": field,
        "contrast": f"{second}_minus_{first}",
        "median_difference": float(np.median(differences)),
        "difference_ci95": _bootstrap_median_difference(first_values, second_values),
        "second_win_fraction": float(np.mean(differences < 0.0)),
        "two_sided_sign_test_p": _two_sided_sign_test(differences),
        "differences_by_seed": {
            str(seed): float(value) for seed, value in zip(paired, differences)
        },
    }


def aggregate_summaries(
    config: dict[str, Any], methods: list[str], seeds: list[int],
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    successful = [item for item in summaries if item["status"] == "succeeded"]
    aggregate: dict[str, Any] = {"runs": summaries, "methods": {}, "paired_analysis": {}}
    for method in methods:
        group = [item for item in successful if item["method"] == method]

        def median(field: str):
            values = [item[field] for item in group if item.get(field) is not None]
            return float(np.median(values)) if values else None

        aggregate["methods"][method] = {
            "n_success": len(group),
            "n_total": len(seeds),
            "median_relative_l2": median("relative_l2"),
            "median_elapsed_seconds": median("elapsed_seconds"),
            "median_controller_weight_tv": median("controller_weight_tv"),
            "median_controller_weight_tv_per_update": median(
                "controller_weight_tv_per_update"
            ),
            "median_gradient_distribution_tv": median("gradient_distribution_tv"),
            "median_temporal_mean_gradient_distribution_tv": median(
                "temporal_mean_gradient_distribution_tv"
            ),
            "median_temporal_mean_physics_gradient_log_gap": median(
                "temporal_mean_physics_gradient_log_gap"
            ),
            "median_bias_concentration_correlation": median(
                "bias_concentration_correlation"
            ),
            "median_residual_evaluations": median("residual_evaluations"),
        }

    indexed = {(item["method"], item["seed"]): item for item in successful}
    contrasts = (
        ("m1", "m5", "gradient_distribution_tv"),
        ("m1", "m5", "controller_weight_tv_per_update"),
        ("m5", "m6", "relative_l2"),
        ("m5", "m6", "controller_weight_tv_per_update"),
        ("m5", "m6", "elapsed_seconds"),
        ("m5", "m7", "relative_l2"),
        ("m6", "m7", "relative_l2"),
        ("m7u", "m7", "relative_l2"),
        ("m7u", "m7", "controller_weight_tv_per_update"),
        ("vw", "m7", "relative_l2"),
        ("vwca", "m7", "relative_l2"),
        ("vw", "vwca", "relative_l2"),
        ("vrba", "m7", "relative_l2"),
        ("vw", "vrba", "relative_l2"),
        ("m0", "vrba", "relative_l2"),
        ("m0", "vrba", "max_abs_error"),
    )
    for first, second, field in contrasts:
        if first in methods and second in methods:
            result = _paired_block(indexed, first, second, seeds, field)
            if result:
                aggregate["paired_analysis"][f"{second}_minus_{first}_{field}"] = result

    output = (
        Path(config["experiment"]["output_dir"])
        / config["experiment"]["name"] / "comparison.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    aggregate["comparison_path"] = str(output.resolve())
    return aggregate


def compare(config: dict[str, Any], methods: list[str], seeds: list[int]) -> dict[str, Any]:
    summaries = [train(config, method, seed) for seed in seeds for method in methods]
    return aggregate_summaries(config, methods, seeds, summaries)


def analyze_existing(config: dict[str, Any], methods: list[str], seeds: list[int]) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    for method in methods:
        for seed in seeds:
            path = _run_directory(config, method, seed) / "summary.json"
            if path.exists():
                summary = json.loads(path.read_text(encoding="utf-8"))
                metrics_path = path.parent / "metrics.csv"
                if metrics_path.exists():
                    with metrics_path.open(newline="", encoding="utf-8") as stream:
                        rows = list(csv.DictReader(stream))

                    def finite_values(field: str) -> list[float]:
                        values = []
                        for row in rows:
                            try:
                                value = float(row[field])
                            except (KeyError, TypeError, ValueError):
                                continue
                            if math.isfinite(value):
                                values.append(value)
                        return values

                    mapping = {
                        "temporal_mean_gradient_distribution_tv": "gradient_distribution_tv",
                        "temporal_mean_loss_distribution_tv": "loss_distribution_tv",
                        "temporal_mean_physics_gradient_log_gap": "physics_gradient_log_gap",
                    }
                    for target, source in mapping.items():
                        values = finite_values(source)
                        summary[target] = float(np.mean(values)) if values else None
                summaries.append(summary)
    return aggregate_summaries(config, methods, seeds, summaries)
