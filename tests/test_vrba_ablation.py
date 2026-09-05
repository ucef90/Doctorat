from copy import deepcopy
from pathlib import Path

import pytest
import torch

from recoa_pinn.config import load_config, validate_config
from recoa_pinn.trainer import train


def small_config(tmp_path):
    config = load_config(Path(__file__).parents[1] / "configs/pilot_quick.yaml")
    config["experiment"]["output_dir"] = str(tmp_path)
    config["training"].update(steps=2, eval_every=2, checkpoint_every=2)
    config["evaluation"].update(nx=9, nt=5, reference_nx=65, reference_dt=0.001)
    return config


@pytest.mark.parametrize("local,global_", [(True, True), (True, False), (False, True), (False, False)])
def test_switches(tmp_path, local, global_):
    config = small_config(tmp_path)
    config["adaptation"].update(vrba_local_enabled=local, vrba_global_enabled=global_)
    result = train(config, "vrba", 23)
    assert result["status"] == "succeeded"
    assert result["adaptive_objective"]["local_enabled"] is local
    assert result["adaptive_objective"]["global_enabled"] is global_
    assert (result["adaptive_objective"]["local_updates"] > 0) is local
    assert (result["controller_updates"] > 0) is global_
    if not global_:
        assert all(v == 1.0 for v in result["final_weights"].values())


@pytest.mark.parametrize("filename", ["pilot_quick.yaml", "allen_cahn_screen.yaml", "helmholtz_calibrated.yaml", "wave_screen.yaml"])
def test_neither_matches_m0(tmp_path, filename):
    config = load_config(Path(__file__).parents[1] / "configs" / filename)
    config["experiment"]["output_dir"] = str(tmp_path)
    config["training"].update(steps=2, eval_every=2, checkpoint_every=2)
    config["evaluation"].update(nx=9, nt=5, reference_nx=65, reference_dt=0.001)
    baseline = train(config, "m0", 23)
    config["adaptation"].update(vrba_local_enabled=False, vrba_global_enabled=False)
    ablated = train(config, "vrba", 23)
    assert baseline["initial_fingerprints"] == ablated["initial_fingerprints"]
    a = torch.load(Path(baseline["run_dir"]) / "model.pt", weights_only=True)
    b = torch.load(Path(ablated["run_dir"]) / "model.pt", weights_only=True)
    for key in a:
        torch.testing.assert_close(a[key], b[key], atol=1e-12, rtol=1e-12)


def test_reject_string_boolean(tmp_path):
    config = small_config(tmp_path)
    config["adaptation"]["vrba_local_enabled"] = "false"
    with pytest.raises(ValueError):
        validate_config(config)
