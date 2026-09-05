"""Common-loss baseline comparison, with 40 reused V10 full-vRBA checkpoints."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import torch

from analyze_article1_extension import evaluate, ROOT
from analyze_vrba_campaign import write_csv
from vrba_statistics import paired_summary, holm


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',default='outputs/common_loss_v10_analysis')
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
    new=ROOT/'outputs/common_loss_v10_campaign';rob=ROOT/'outputs/robustness_v10_campaign'
    rows=[];records=[]
    for base,reused in [(new,False),(rob,True)]:
        manifest=json.loads((base/'manifest.json').read_text())
        cells=[c for c in manifest['cells'] if not reused or c['variant']=='full_exp']
        for cell in cells:
            result_path=base/'cells'/cell['id']/'result.json'
            if not result_path.exists():raise RuntimeError('Incomplete baseline campaign')
            record=json.loads(result_path.read_text())
            if record['id']!=cell['id']:raise RuntimeError('Cell identity mismatch')
            record.update(problem=cell['problem'],variant='vrba' if reused else cell['variant'],reused=reused)
            records.append(record)
            if record['status']!='succeeded':continue
            scores=evaluate(base/record['run_dir'])
            for key in ('relative_l2','max_abs_error'):
                if not np.isclose(scores[key],record[key],rtol=1e-10,atol=1e-12):raise RuntimeError('Stored score mismatch')
            rows.append({**{k:record[k] for k in ('id','problem','variant','seed','reused')},**scores,
                'model_sha256':hashlib.sha256((base/record['run_dir']/'model.pt').read_bytes()).hexdigest()})
    audit=[]
    for problem in dict.fromkeys(r['problem'] for r in records):
        for seed in sorted({r['seed'] for r in records}):
            group=[r for r in records if r['problem']==problem and r['seed']==seed and r['status']=='succeeded']
            same=bool(group) and all(r['initial_fingerprints']==group[0]['initial_fingerprints'] for r in group)
            audit.append(dict(problem=problem,seed=seed,n_success=len(group),initial_hashes_match=same))
            if group and not same:raise RuntimeError('Initial tensors differ across compared methods')
    stats=[]
    for metric in ('relative_l2','max_abs_error'):
        family=[]
        for problem in dict.fromkeys(r['problem'] for r in records):
            ix={(r['variant'],r['seed']):r for r in rows if r['problem']==problem}
            for method in ('m5','m6','m7','vw'):
                seeds=[s for s in sorted({s for _,s in ix}) if ('vrba',s) in ix and (method,s) in ix]
                if not seeds:raise RuntimeError('No complete pairs')
                diffs=[ix['vrba',s][metric]-ix[method,s][metric] for s in seeds]
                family.append(dict(problem=problem,metric=metric,contrast='vrba-'+method,**paired_summary(diffs)))
        for r,pvalue in zip(family,holm([r['p_sign'] for r in family])):r['p_holm_16']=pvalue
        stats.extend(family)
    summary=[]
    for problem in dict.fromkeys(r['problem'] for r in records):
        for method in ('m5','m6','m7','vw','vrba'):
            group=[r for r in rows if r['problem']==problem and r['variant']==method]
            summary.append(dict(problem=problem,variant=method,n=len(group),**{key:float(np.median([r[key] for r in group]))
                for key in ('relative_l2','max_abs_error','q95_abs_error','q99_abs_error')}))
    write_csv(out/'evaluation.csv',rows);write_csv(out/'method_summary.csv',summary)
    write_csv(out/'paired_statistics.csv',stats);write_csv(out/'pairing_audit.csv',audit)
    failures=[r for r in records if r['status']!='succeeded']
    (out/'failures.json').write_text(json.dumps(failures,indent=2))
    (out/'validation.json').write_text(json.dumps(dict(expected_new=160,expected_reused=40,
        evaluated_new=sum(not r['reused'] for r in rows),evaluated_reused=sum(r['reused'] for r in rows),
        failed=len(failures),paired_blocks=len(audit),all_initial_hashes_match=all(r['initial_hashes_match'] for r in audit),
        stored_scores_verified=True,analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2))
    print('Common-loss comparison independently verified',flush=True)


if __name__=='__main__':main()
