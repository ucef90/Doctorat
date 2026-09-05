import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_article1_extension import build_manifest


def test_extension_cells_are_paired_and_use_common_observation_loss():
    manifest=build_manifest('robustness',[11,22])
    assert len(manifest['cells'])==40
    for cell in manifest['cells']:
        assert cell['config']['observations']['loss']=='mse'
        assert cell['config']['problem']['reference_method']=='cole_hopf'
    assert manifest==build_manifest('robustness',[11,22])


def test_budget_doubles_every_problem_without_changing_model():
    manifest=build_manifest('budget',[11])
    expected={'burgers':5000,'allen_cahn':1200,'helmholtz':3000,'wave':1200}
    assert len(manifest['cells'])==20
    for cell in manifest['cells']:
        assert cell['config']['training']['steps']==expected[cell['problem']]
