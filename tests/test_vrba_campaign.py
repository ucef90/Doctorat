import json
from scripts.run_vrba_campaign import CONFIGS, SEEDS, VARIANTS, atomic_json, build_manifest


def test_manifest_complete_and_paired():
    manifest = build_manifest(SEEDS, list(CONFIGS))
    assert len(manifest["cells"]) == 200
    assert len({c["id"] for c in manifest["cells"]}) == 200
    for problem in CONFIGS:
        for seed in SEEDS:
            group = [c for c in manifest["cells"] if c["problem"] == problem and c["seed"] == seed]
            assert {c["variant"] for c in group} == set(VARIANTS)
            # All non-adaptation parameters are identical in each paired block.
            configs = [{k: v for k, v in c["config"].items() if k != "adaptation"} for c in group]
            assert all(c == configs[0] for c in configs)


def test_atomic_result_replacement(tmp_path):
    target = tmp_path / "result.json"
    atomic_json(target, {"status": "failed"})
    atomic_json(target, {"status": "succeeded"})
    assert json.loads(target.read_text()) == {"status": "succeeded"}
    assert not target.with_suffix(".json.tmp").exists()
