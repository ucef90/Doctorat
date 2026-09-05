from copy import deepcopy
from pathlib import Path

import torch
import pytest

from recoa_pinn.config import load_config
from recoa_pinn.trainer import train


def test_m0_training_writes_reproducible_artifacts(tmp_path: Path):
    root = Path(__file__).parents[1]
    config = deepcopy(load_config(root / "configs" / "pilot_quick.yaml"))
    config["experiment"]["output_dir"] = str(tmp_path)
    config["training"]["steps"] = 2
    config["training"]["eval_every"] = 2
    config["training"]["checkpoint_every"] = 2
    config["evaluation"]["nx"] = 11
    config["evaluation"]["nt"] = 5
    config["evaluation"]["reference_nx"] = 65
    config["evaluation"]["reference_dt"] = 0.001
    summary = train(config, "m0", 5)
    run_dir = Path(summary["run_dir"])
    assert summary["status"] == "succeeded"
    assert (run_dir / "config.resolved.yaml").exists()
    assert (run_dir / "environment.json").exists()
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "model.pt").exists()
    assert summary["budget"]["optimization"] == 2 * config["training"]["n_collocation"]
    assert summary["residual_evaluations"] == sum(
        summary["budget"][name] for name in ("optimization", "controller", "sampler", "diagnostic")
    )


def test_complete_training_is_reproducible_for_same_seed(tmp_path: Path):
    root = Path(__file__).parents[1]
    base = deepcopy(load_config(root / "configs" / "pilot_quick.yaml"))
    base["training"]["steps"] = 2
    base["training"]["eval_every"] = 2
    base["training"]["checkpoint_every"] = 2
    base["evaluation"].update({"nx": 11, "nt": 5, "reference_nx": 65, "reference_dt": 0.001})

    first_config = deepcopy(base)
    first_config["experiment"]["output_dir"] = str(tmp_path / "first")
    second_config = deepcopy(base)
    second_config["experiment"]["output_dir"] = str(tmp_path / "second")
    first = train(first_config, "m0", 17)
    second = train(second_config, "m0", 17)

    assert first["relative_l2"] == second["relative_l2"]
    assert first["max_abs_error"] == second["max_abs_error"]
    first_state = torch.load(Path(first["run_dir"]) / "model.pt", weights_only=True)
    second_state = torch.load(Path(second["run_dir"]) / "model.pt", weights_only=True)
    assert first_state.keys() == second_state.keys()
    assert all(torch.equal(first_state[key], second_state[key]) for key in first_state)


@pytest.mark.parametrize(
    "method", ["m0", "m1", "m3", "m5", "m6", "m7u", "m7", "vw", "vwca", "vrba"]
)
def test_every_method_completes_one_step(tmp_path: Path, method: str):
    root = Path(__file__).parents[1]
    config = deepcopy(load_config(root / "configs" / "pilot_quick.yaml"))
    config["experiment"]["output_dir"] = str(tmp_path / method)
    config["training"].update({"steps": 1, "eval_every": 1, "checkpoint_every": 1})
    config["evaluation"].update({"nx": 9, "nt": 5, "reference_nx": 65, "reference_dt": 0.001})
    summary = train(config, method, 23)
    assert summary["status"] == "succeeded"
    assert summary["budget"]["equal_controller_cardinality"]
    assert summary["measure_correction"]["enabled"] is (
        method in {"m7", "vw", "vwca"}
    )
    assert summary["adaptive_objective"]["enabled"] is (method == "vrba")


def test_vrba_training_is_reproducible_for_same_seed(tmp_path: Path):
    root = Path(__file__).parents[1]
    base = deepcopy(load_config(root / "configs" / "pilot_quick.yaml"))
    base["training"].update({
        "steps": 3, "eval_every": 3, "checkpoint_every": 3, "log_every": 1,
    })
    base["evaluation"].update({
        "nx": 11, "nt": 5, "reference_nx": 65, "reference_dt": 0.001,
    })

    first_config = deepcopy(base)
    first_config["experiment"]["output_dir"] = str(tmp_path / "first")
    second_config = deepcopy(base)
    second_config["experiment"]["output_dir"] = str(tmp_path / "second")
    first = train(first_config, "vrba", 29)
    second = train(second_config, "vrba", 29)

    assert first["relative_l2"] == second["relative_l2"]
    assert first["final_weights"] == second["final_weights"]
    assert first["vrba_attention_statistics"] == second["vrba_attention_statistics"]
    first_state = torch.load(Path(first["run_dir"]) / "model.pt", weights_only=True)
    second_state = torch.load(Path(second["run_dir"]) / "model.pt", weights_only=True)
    assert all(torch.equal(first_state[key], second_state[key]) for key in first_state)
