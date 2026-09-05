"""Re-run M5/M6/M7/VW with the common-loss V10 robustness configurations."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
import multiprocessing
from pathlib import Path
import time
import traceback

from recoa_pinn.reproducibility import environment_manifest
from run_vrba_campaign import ROOT, atomic_json


def worker(cell,campaign):
    import torch
    from recoa_pinn.trainer import train
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    base=Path(campaign)/'cells'/cell['id'];base.mkdir(parents=True,exist_ok=False)
    cfg=deepcopy(cell['config']);cfg['experiment']['output_dir']=str(base)
    try:
        record=train(cfg,cell['variant'],cell['seed'])
        record['run_dir']=str(Path(record['run_dir']).relative_to(campaign))
    except Exception:
        record=dict(status='failed',failure_reason=traceback.format_exc())
    record.update({k:cell[k] for k in ('id','problem','variant','seed')})
    atomic_json(base/'result.json',record)
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',default='outputs/common_loss_v10_campaign')
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args()
    if a.workers<1:p.error('workers must be positive')
    source=ROOT/'outputs/robustness_v10_campaign/manifest.json'
    original=json.loads(source.read_text())
    cells=[]
    for c in original['cells']:
        if c['variant']!='full_exp':continue
        for method in ('m5','m6','m7','vw'):
            new=deepcopy(c);new.update(id=f"{c['problem']}__{method}__{c['seed']}",variant=method)
            assert new['config']['observations']['loss']=='mse'
            assert new['config']['problem']['reference_method']=='cole_hopf'
            cells.append(new)
    paths=list((ROOT/'src').rglob('*.py'))+[Path(__file__),ROOT/'scripts/run_vrba_campaign.py',
        ROOT/'ARTICLE1_COMMON_LOSS_BASELINES_V10.md',source]
    manifest=dict(protocol='v10-common-loss-exploratory',hashes={str(p.relative_to(ROOT)):
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},cells=cells)
    out=Path(a.output).resolve();env=environment_manifest()
    if a.resume:
        if json.loads((out/'manifest.json').read_text())!=manifest:raise RuntimeError('Changed manifest')
        old=json.loads((out/'environment.json').read_text())
        if any(old[k]!=env[k] for k in ('python','torch','numpy','platform')):raise RuntimeError('Changed environment')
    else:
        out.mkdir(parents=True,exist_ok=False);atomic_json(out/'manifest.json',manifest)
        atomic_json(out/'environment.json',env)
    done=[];pending=[]
    for c in cells:
        path=out/'cells'/c['id']/'result.json'
        if path.exists():done.append(json.loads(path.read_text()))
        elif path.parent.exists():raise RuntimeError('Incomplete attempt preserved; use a fresh campaign output')
        else:pending.append(c)
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('spawn'),
                             max_tasks_per_child=1) as executor:
        jobs=[executor.submit(worker,c,str(out)) for c in pending]
        for future in as_completed(jobs):
            record=future.result();done.append(record)
            atomic_json(out/'results.json',sorted(done,key=lambda r:r['id']))
            print(f"{len(done)}/{len(cells)} {record['id']} {record['status']}",flush=True)
    atomic_json(out/'completion.json',dict(completed=len(done),expected=len(cells),
        failed=sum(r['status']!='succeeded' for r in done),wall_seconds=time.perf_counter()-start))
    if any(r['status']!='succeeded' for r in done):raise SystemExit(1)


if __name__=='__main__':main()
