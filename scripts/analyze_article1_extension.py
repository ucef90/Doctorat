"""Independent checkpoint evaluation and fixed-family inference for V10."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch

from recoa_pinn.config import load_config
from recoa_pinn.model import MLP
from recoa_pinn.problems import make_problem
from analyze_vrba_campaign import metrics, predict, write_csv, CONTRASTS, VARIANTS
from vrba_statistics import paired_summary, holm

ROOT=Path(__file__).resolve().parents[1]


def evaluate(run, dense=False, cole=True):
    cfg=load_config(run/'config.resolved.yaml')
    if cole and cfg['problem']['name']=='burgers': cfg['problem']['reference_method']='cole_hopf'
    problem=make_problem(cfg['problem'],torch.device('cpu'),torch.float64)
    model=MLP(**cfg['model']).to(dtype=torch.float64)
    model.load_state_dict(torch.load(run/'model.pt',map_location='cpu',weights_only=True))
    model.eval()
    ev=cfg['evaluation']; factor=2 if dense else 1
    points=problem.evaluation_grid(factor*(ev['nx']-1)+1,factor*(ev['nt']-1)+1)
    reference=problem.reference_at(points,ev['reference_nx'],ev['reference_dt'])
    return metrics(predict(model,points),reference)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('campaign');p.add_argument('--output',required=True)
    a=p.parse_args();campaign=Path(a.campaign); output=Path(a.output)
    output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    manifest=json.loads((campaign/'manifest.json').read_text())
    records=[]
    for cell in manifest['cells']:
        path=campaign/'cells'/cell['id']/'result.json'
        if not path.exists(): raise RuntimeError(f"Incomplete campaign: {cell['id']}")
        record=json.loads(path.read_text())
        # Trainer summaries use the PDE name ('burgers'), while the frozen
        # robustness cells use the observation regime. Recover the grouping
        # from the manifest, never from a score or a mutable absolute path.
        if any(record[k]!=cell[k] for k in ('id','variant','seed')):
            raise RuntimeError('Cell identity mismatch')
        record['problem']=cell['problem']
        records.append(record)
    successful=[r for r in records if r['status']=='succeeded']
    if len({r['id'] for r in records})!=len(records):
        raise RuntimeError('Duplicate cell identities')
    problems=list(dict.fromkeys(c['problem'] for c in manifest['cells']))
    audit=[]
    for problem in problems:
        for seed in sorted({r['seed'] for r in records}):
            group=[r for r in successful if r['problem']==problem and r['seed']==seed]
            same=bool(group) and all(r['initial_fingerprints']==group[0]['initial_fingerprints'] for r in group)
            audit.append(dict(problem=problem,seed=seed,n_success=len(group),initial_hashes_match=same))
            if group and not same: raise RuntimeError('Pairing failure')
    rows=[]
    for i,r in enumerate(successful):
        run=campaign/r['run_dir']; scores=evaluate(run)
        for key in ('relative_l2','max_abs_error'):
            if not np.isclose(scores[key],r[key],rtol=1e-10,atol=1e-12):
                raise RuntimeError(f"Stored score mismatch: {r['id']} {key}")
        row={k:r[k] for k in ('id','problem','variant','seed')}
        row.update(scores,**{'dense_'+k:v for k,v in evaluate(run,dense=True).items()},
                   steps=r['steps_completed'],elapsed_seconds=r['elapsed_seconds'],
                   model_sha256=hashlib.sha256((run/'model.pt').read_bytes()).hexdigest())
        rows.append(row)
        if (i+1)%25==0: print(f'Evaluated {i+1}/{len(successful)}',flush=True)
    write_csv(output/'evaluation.csv',rows);write_csv(output/'pairing_audit.csv',audit)
    stats=[]
    for metric in ('relative_l2','max_abs_error'):
        family=[]
        for problem in problems:
            indexed={(r['variant'],r['seed']):r for r in rows if r['problem']==problem}
            for contrast, coeff in CONTRASTS.items():
                seeds=[s for s in sorted({s for _,s in indexed}) if all((v,s) in indexed for v in coeff)]
                diffs=[sum(c*indexed[v,s][metric] for v,c in coeff.items()) for s in seeds]
                row=dict(problem=problem,metric=metric,contrast=contrast)
                if diffs: row.update(paired_summary(diffs))
                else: row.update(n_pairs=0,median_difference=None,mean_difference=None,ci95_low=None,
                    ci95_high=None,n_negative=0,n_zero=0,n_positive=0,p_sign=1.)
                family.append(row)
        for r,pvalue in zip(family,holm([r['p_sign'] for r in family])): r['p_holm_16']=pvalue
        stats.extend(family)
    write_csv(output/'paired_statistics.csv',stats)
    summaries=[]
    for problem in problems:
        for variant in VARIANTS:
            part=[r for r in rows if r['problem']==problem and r['variant']==variant]
            if not part: continue
            summaries.append(dict(problem=problem,variant=variant,n=len(part),
                **{k:float(np.median([r[k] for r in part])) for k in
                   ('relative_l2','max_abs_error','q95_abs_error','q99_abs_error','dense_max_abs_error')}))
    write_csv(output/'method_summary.csv',summaries)
    if manifest['suite']=='budget':
        old_base=ROOT/'outputs/ablation_v09_campaign'
        old={r['id']:r for r in json.loads((old_base/'results.json').read_text())}
        changes=[]
        for row in rows:
            old_record=old[row['id']]
            new_record=next(r for r in successful if r['id']==row['id'])
            if old_record['initial_fingerprints']!=new_record['initial_fingerprints']:
                raise RuntimeError('Historical budget initial tensors mismatch')
            baseline=evaluate(old_base/old_record['run_dir'])
            changes.append(dict(id=row['id'],problem=row['problem'],variant=row['variant'],seed=row['seed'],
                l2_original_budget=baseline['relative_l2'],l2_double_budget=row['relative_l2'],
                l2_difference=row['relative_l2']-baseline['relative_l2'],
                maximum_original_budget=baseline['max_abs_error'],maximum_double_budget=row['max_abs_error']))
        write_csv(output/'budget_changes.csv',changes)
    failures=[r for r in records if r['status']!='succeeded']
    (output/'validation.json').write_text(json.dumps(dict(expected=len(records),evaluated=len(rows),
        failed=len(failures),paired_blocks=len(audit),all_initial_hashes_match=all(r['initial_hashes_match'] for r in audit),
        stored_scores_verified=True,dense_grid_evaluated=True,analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2))
    (output/'failures.json').write_text(json.dumps(failures,indent=2))
    fig,axes=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for ax,problem in zip(axes.flat,problems):
        for i,variant in enumerate(VARIANTS):
            part=[r['relative_l2'] for r in rows if r['problem']==problem and r['variant']==variant]
            ax.scatter(np.linspace(i-.12,i+.12,len(part)),part,s=15,alpha=.7)
            ax.hlines(np.median(part),i-.23,i+.23,color='black',lw=2)
        ax.set(xticks=range(5),xticklabels=VARIANTS,title=problem,ylabel='Relative L2 error')
        ax.tick_params(axis='x',rotation=20);ax.grid(axis='y',alpha=.15)
    fig.suptitle(f"V10 {manifest['suite']} · paired seeds · independent evaluation")
    for ext in ('png','svg'): fig.savefig(output/f'l2_by_seed.{ext}',dpi=180)
    print(f'Complete: {len(rows)} independent evaluations',flush=True)


if __name__=='__main__': main()
