"""Frozen V10 score/table reconstruction and a predeclared 12-run portability check.

Run on a separate host. A local execution never constitutes another-machine
replication. Numerical thresholds are declared here before the external run.
"""
import argparse
from copy import deepcopy
import csv
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import torch
from analyze_article1_extension import evaluate
from analyze_vrba_campaign import CONTRASTS, write_csv
from vrba_statistics import paired_summary, holm
from recoa_pinn.reproducibility import environment_manifest

ROOT=Path(__file__).resolve().parents[1]
SCORE_RTOL, SCORE_ATOL=1e-8,1e-10
TRAIN_RTOL, TRAIN_ATOL=1e-3,1e-5
ANALYSES={'robustness':'robustness_v10_verified','budget':'budget_v10_analysis',
          'common_loss':'common_loss_v10_analysis'}

def read(path):
    return json.loads(path.read_text())

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def selection():
    chosen=[]
    for problem in ('burgers','allen_cahn','helmholtz','wave'):
        for variant in ('global_only','full_exp'):
            chosen.append(('budget',f'{problem}__{variant}__11'))
    for variant in ('m5','m6','m7'):
        chosen.append(('common_loss',f'sparse_noisy__{variant}__11'))
    chosen.append(('robustness','sparse_noisy__full_exp__11'))
    return chosen

def get_cell(suite,identifier):
    base=ROOT/'outputs'/f'{suite}_v10_campaign'
    cells=read(base/'manifest.json')['cells']
    return base,next(c for c in cells if c['id']==identifier)

def reconstruct(output):
    evaluated={}; all_ok=True
    for suite,count in [('robustness',200),('budget',200),('common_loss',160)]:
        base=ROOT/'outputs'/f'{suite}_v10_campaign'
        cells=read(base/'manifest.json')['cells']; assert len(cells)==count
        rows=[]
        for i,c in enumerate(cells):
            record=read(base/'cells'/c['id']/'result.json')
            assert record['status']=='succeeded'
            run=base/record['run_dir']; scores=evaluate(run)
            row={k:c[k] for k in ('id','problem','variant','seed')}
            row.update(scores)
            row['scores_match']=all(np.isclose(scores[k],record[k],rtol=SCORE_RTOL,atol=SCORE_ATOL)
                                    for k in ('relative_l2','max_abs_error'))
            row['model_sha256']=hashlib.sha256((run/'model.pt').read_bytes()).hexdigest()
            rows.append(row); all_ok=all_ok and row['scores_match']
            if (i+1)%50==0: print(f'{suite}: {i+1}/{count} frozen scores',flush=True)
        evaluated[suite]=rows
        write_csv(output/f'{suite}_evaluation.csv',rows)
    tables=[]
    for suite,rows0 in evaluated.items():
        rows=deepcopy(rows0)
        if suite=='common_loss':
            for r in evaluated['robustness']:
                if r['variant']=='full_exp':
                    r=deepcopy(r);r['variant']='vrba';rows.append(r)
            contrasts={f'vrba-{m}':{'vrba':1,m:-1} for m in ('m5','m6','m7','vw')}
        else: contrasts=CONTRASTS
        published=list(csv.DictReader((ROOT/'outputs'/ANALYSES[suite]/'paired_statistics.csv').open()))
        stats=[]
        for metric in ('relative_l2','max_abs_error'):
            family=[]
            for problem in sorted({r['problem'] for r in rows}):
                ix={(r['variant'],int(r['seed'])):r for r in rows if r['problem']==problem}
                for contrast,coeff in contrasts.items():
                    seeds=sorted({s for _,s in ix}); assert len(seeds)==10
                    d=[sum(w*ix[v,s][metric] for v,w in coeff.items()) for s in seeds]
                    family.append(dict(problem=problem,metric=metric,contrast=contrast,**paired_summary(d)))
            assert len(family)==16
            for r,p in zip(family,holm([r['p_sign'] for r in family])): r['p_holm_16']=p
            stats+=family
        match=True
        for r in stats:
            old=next(x for x in published if all(x[k]==r[k] for k in ('problem','metric','contrast')))
            match=match and all(np.isclose(r[k],float(old[k]),rtol=SCORE_RTOL,atol=SCORE_ATOL)
                for k in ('median_difference','mean_difference','ci95_low','ci95_high','p_sign','p_holm_16'))
        write_csv(output/f'{suite}_paired_statistics.csv',stats)
        tables.append(dict(suite=suite,contrasts=len(stats),all_statistics_match=bool(match)))
        all_ok=all_ok and match
    save(output/'score_validation.json',dict(frozen_models=560,tables=tables,passed=bool(all_ok),
        score_rtol=SCORE_RTOL,score_atol=SCORE_ATOL))
    return bool(all_ok)

def train_one(args):
    suite,identifier,output=args
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    from recoa_pinn.trainer import train
    base,c=get_cell(suite,identifier)
    cfg=deepcopy(c['config'])
    cfg['experiment']['output_dir']=str(Path(output)/suite/identifier)
    method=c['variant'] if suite=='common_loss' else 'vrba'
    new=train(cfg,method,c['seed'])
    old=read(base/'cells'/identifier/'result.json')
    same_inputs=new['initial_fingerprints']==old['initial_fingerprints']
    row=dict(suite=suite,id=identifier,status=new['status'],same_initial_tensors=same_inputs,
             steps=new['steps_completed'],steps_expected=old['steps_completed'])
    for metric in ('relative_l2','max_abs_error'):
        row[metric]=new[metric];row['old_'+metric]=old[metric]
        row['delta_'+metric]=new[metric]-old[metric]
        row['match_'+metric]=bool(np.isclose(new[metric],old[metric],rtol=TRAIN_RTOL,atol=TRAIN_ATOL))
    row['passed']=bool(same_inputs and row['status']=='succeeded' and row['steps']==row['steps_expected']
                       and row['match_relative_l2'] and row['match_max_abs_error'])
    return row

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='outputs/v11_reproduction')
    parser.add_argument('--audit-only',action='store_true')
    parser.add_argument('--scores-only',action='store_true')
    a=parser.parse_args();output=Path(a.output).resolve();output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    chosen=selection()
    for suite,identifier in chosen: get_cell(suite,identifier)
    save(output/'predeclared_plan.json',dict(selection=chosen,seed_selection='lowest declared seed, no score selection',
         score_rtol=SCORE_RTOL,score_atol=SCORE_ATOL,training_rtol=TRAIN_RTOL,training_atol=TRAIN_ATOL,
         same_initial_tensor_hashes_required=True,interpretation='portability check, not new inferential evidence'))
    env=environment_manifest()
    env.update(github_actions=os.environ.get('GITHUB_ACTIONS')=='true',
               runner_os=os.environ.get('RUNNER_OS'),github_sha=os.environ.get('GITHUB_SHA'),
               github_run_id=os.environ.get('GITHUB_RUN_ID'),machine=platform.machine())
    save(output/'environment.json',env)
    (output/'packages.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
    if a.audit_only: print('12-cell plan and all references resolved');return
    scores_ok=reconstruct(output)
    rows=[]
    if not a.scores_only:
        with multiprocessing.get_context('spawn').Pool(1,maxtasksperchild=1) as pool:
            for row in pool.imap(train_one,[(s,i,str(output/'retraining')) for s,i in chosen]):
                rows.append(row);save(output/'retraining_comparison.json',rows)
                print(f"Retraining {len(rows)}/12 {row['id']}: passed={row['passed']}",flush=True)
        write_csv(output/'retraining_comparison.csv',rows)
    passed=scores_ok and (a.scores_only or (len(rows)==12 and all(r['passed'] for r in rows)))
    save(output/'validation.json',dict(passed=bool(passed),score_reproduction=scores_ok,
        retrainings=len(rows),retrainings_passed=sum(r['passed'] for r in rows),
        independent_github_runner=env['github_actions']))
    if not passed: raise SystemExit('Preserved discrepancies: review the evidence; do not relax thresholds.')

if __name__=='__main__':main()
