"""Frozen V10 robustness and doubled-step campaigns (200 cells per suite)."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import random
import subprocess
import time

from recoa_pinn.config import load_config
from recoa_pinn.reproducibility import environment_manifest
from run_vrba_campaign import ROOT, CONFIGS, SEEDS, VARIANTS, atomic_json, worker

ROBUSTNESS = {k: f'burgers_data_{k}.yaml' for k in
              ('sparse_clean','sparse_noisy','extreme','block_missing')}


def build_manifest(suite, seeds):
    configs = ROBUSTNESS if suite == 'robustness' else CONFIGS
    paths = sorted((ROOT/'src').rglob('*.py'))
    paths += [Path(__file__), ROOT/'scripts/run_vrba_campaign.py',
              ROOT/'ARTICLE1_EXTENSION_PROTOCOL_V10.md']
    paths += [ROOT/'configs'/f for f in configs.values()]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    cells=[]
    for seed in seeds:
        block=[(p,v) for p in configs for v in VARIANTS]
        random.Random(10000+seed).shuffle(block)
        for problem, variant in block:
            cfg=load_config(ROOT/'configs'/configs[problem])
            local, global_, potential=VARIANTS[variant]
            cfg['adaptation'].update(vrba_local_enabled=local,vrba_global_enabled=global_,vrba_potential=potential)
            if cfg['problem']['name']=='burgers':
                cfg['problem']['reference_method']='cole_hopf'
            cfg.setdefault('observations',{})['loss']='mse'
            if suite=='budget':
                cfg['training']['steps'] *= 2
                cfg['training']['checkpoint_every']=cfg['training']['steps']
            cells.append(dict(id=f'{problem}__{variant}__{seed}',problem=problem,
                              variant=variant,seed=seed,config=cfg))
    return dict(protocol='v10-exploratory',suite=suite,hashes=hashes,cells=cells)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--suite',choices=['robustness','budget'],required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--workers',type=int,default=6)
    p.add_argument('--seeds',type=int,nargs='+',default=SEEDS)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args()
    if a.workers<1 or len(set(a.seeds))!=len(a.seeds): p.error('Invalid workers or duplicated seeds')
    output=Path(a.output).resolve()
    manifest=build_manifest(a.suite,a.seeds)
    env=environment_manifest()
    if a.resume:
        old=json.loads((output/'manifest.json').read_text())
        if old!=manifest: raise RuntimeError('Resume refused: code or protocol changed')
        old_env=json.loads((output/'launch_environment.json').read_text())
        if any(old_env[k]!=env[k] for k in ('python','torch','numpy','platform')):
            raise RuntimeError('Resume refused: environment changed')
    else:
        output.mkdir(parents=True,exist_ok=False)
        atomic_json(output/'manifest.json',manifest)
        atomic_json(output/'launch_environment.json',env)
        (output/'environment-freeze.txt').write_text(subprocess.check_output(
            [os.sys.executable,'-m','pip','freeze'],text=True))
    done=[]; pending=[]
    for cell in manifest['cells']:
        path=output/'cells'/cell['id']/'result.json'
        if path.exists(): done.append(json.loads(path.read_text()))
        else: pending.append(cell)
    print(f"Suite={a.suite}; frozen={len(manifest['cells'])}; pending={len(pending)}",flush=True)
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('spawn'),
                             max_tasks_per_child=1) as executor:
        jobs=[executor.submit(worker,c,str(output)) for c in pending]
        for future in as_completed(jobs):
            row=future.result(); done.append(row)
            atomic_json(output/'results.json',sorted(done,key=lambda r:r['id']))
            print(f"{len(done)}/{len(manifest['cells'])} {row['id']} {row['status']}",flush=True)
    atomic_json(output/'completion.json',dict(completed=len(done),expected=len(manifest['cells']),
        failed=sum(r['status']!='succeeded' for r in done),workers=a.workers,
        invocation_wall_seconds=time.perf_counter()-start))
    if any(r['status']!='succeeded' for r in done): raise SystemExit(1)


if __name__=='__main__': main()
