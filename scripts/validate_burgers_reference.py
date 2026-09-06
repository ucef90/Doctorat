"""Validate an independent reference and re-evaluate frozen V09 Burgers models."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
import torch

from recoa_pinn.burgers_reference import cole_hopf
from recoa_pinn.config import load_config
from recoa_pinn.model import MLP
from recoa_pinn.problems import make_problem
from recoa_pinn.reproducibility import environment_manifest
from analyze_vrba_campaign import metrics, predict, write_csv, CONTRASTS, VARIANTS
from vrba_statistics import paired_summary, holm

ROOT = Path(__file__).resolve().parents[1]


def adaptive_reference(t, x, nu):
    # Different integration rule; the scaling avoids tiny absolute integrals.
    z = np.linspace(-16, 16, 8193)
    logs = -z*z - np.cos(np.pi*(x-2*np.sqrt(nu*t)*z))/(2*np.pi*nu)
    offset = logs.max()
    def mass(v):
        phase = np.pi*(x-2*np.sqrt(nu*t)*v)
        return np.exp(-v*v-np.cos(phase)/(2*np.pi*nu)-offset)
    denominator = quad(mass, -16, 16, epsabs=1e-12, epsrel=1e-12, limit=300)[0]
    numerator = quad(lambda v: -np.sin(np.pi*(x-2*np.sqrt(nu*t)*v))*mass(v),
                     -16, 16, epsabs=1e-12, epsrel=1e-12, limit=300)[0]
    return numerator/denominator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='outputs/reference_v10_analysis')
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    torch.set_default_dtype(torch.float64)
    cfg = load_config(ROOT/'configs/burgers_confirmatory_long.yaml')
    problem = make_problem(cfg['problem'], torch.device('cpu'), torch.float64)
    dense = problem.evaluation_grid(321, 161)
    points = dense.numpy()
    refs = {n: cole_hopf(points, order=n) for n in (64, 128, 256)}
    truth = torch.from_numpy(refs[256])
    checks = {'quadrature_64_128_max': float(np.max(np.abs(refs[64]-refs[128]))),
              'quadrature_128_256_max': float(np.max(np.abs(refs[128]-refs[256])))}
    independent_points = np.array([(t,x) for t in (.01,.2,.5,1.)
                                  for x in (-.7,-.025,0.,.0125,.3)])
    independent = np.array([adaptive_reference(t,x,problem.viscosity) for t,x in independent_points])
    checks['adaptive_quad_max_discrepancy_20_points'] = float(np.max(
        np.abs(independent-cole_hopf(independent_points, order=256).ravel())))
    if checks['quadrature_128_256_max'] > 1e-10 or checks['adaptive_quad_max_discrepancy_20_points'] > 1e-10:
        raise RuntimeError('Independent reference convergence gate failed')
    checks['finite_volume'] = []
    fv_refs = {}
    for nx, dt in [(257,1e-4),(513,5e-5),(1025,2.5e-5)]:
        ref = problem.reference_at(dense, nx, dt)
        fv_refs[nx] = ref.numpy()
        checks['finite_volume'].append(dict(nx=nx,dt=dt,**metrics(ref,truth)))
        print('Finite-volume comparison', checks['finite_volume'][-1], flush=True)
    rows = []
    campaign = ROOT/'outputs/ablation_v09_campaign'
    records = json.loads((campaign/'results.json').read_text())
    for record in records:
        if record['problem'] != 'burgers' or record['status'] != 'succeeded':
            continue
        run = campaign/record['run_dir']
        config = load_config(run/'config.resolved.yaml')
        model = MLP(**config['model']).to(dtype=torch.float64)
        state_path = run/'model.pt'
        model.load_state_dict(torch.load(state_path, map_location='cpu',weights_only=True))
        model.eval()
        pred = predict(model,dense)
        row = {k:record[k] for k in ('id','variant','seed')}
        row.update(metrics(pred, truth), historical_l2=record['relative_l2'],
                   historical_maximum=record['max_abs_error'],
                   model_sha256=hashlib.sha256(state_path.read_bytes()).hexdigest())
        rows.append(row)
    write_csv(output/'evaluation.csv',rows)
    stats=[]
    for metric in ('relative_l2','max_abs_error'):
        family=[]
        indexed={(r['variant'],r['seed']):r for r in rows}
        for name, coeff in CONTRASTS.items():
            seeds=sorted({r['seed'] for r in rows})
            diffs=[sum(c*indexed[v,s][metric] for v,c in coeff.items()) for s in seeds]
            family.append(dict(metric=metric,contrast=name,**paired_summary(diffs)))
        for row,p in zip(family,holm([r['p_sign'] for r in family])):
            row['p_holm_4']=p
        stats.extend(family)
    write_csv(output/'paired_statistics.csv', stats)
    summary=[]
    for v in VARIANTS:
        part=[r for r in rows if r['variant']==v]
        summary.append(dict(variant=v,n=len(part),**{k:float(np.median([r[k] for r in part]))
            for k in ('relative_l2','max_abs_error','historical_l2','historical_maximum')}))
    write_csv(output/'method_summary.csv',summary)
    checks.update(evaluated_models=len(rows),evaluation_grid=[161,321],
                  interpretation='Quadrature convergence and cross-rule checks; no certified continuum error bound',
                  inference='Exploratory reanalysis; Holm family of four contrasts separately for each metric')
    (output/'validation.json').write_text(json.dumps(checks,indent=2))
    (output/'environment.json').write_text(json.dumps(environment_manifest(),indent=2))
    np.savez_compressed(output/'reference_fields.npz',points=points,cole_hopf=refs[256],
                        **{f'rusanov_{n}':r for n,r in fv_refs.items()})
    fig, axes=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True)
    mask=points[:,0]==1.
    for n,r in fv_refs.items():
        axes[0].plot(points[mask,1],r[mask,0],label=f'Rusanov {n}',lw=1.3)
    axes[0].plot(points[mask,1],refs[256][mask,0],label='Cole–Hopf 256',color='black',ls='--')
    axes[0].set(xlim=(-.12,.12),xlabel='x',ylabel='u(1,x)',title='Independent shock reference')
    axes[0].legend(fontsize=8)
    x=np.arange(len(summary))
    axes[1].plot(x,[r['historical_maximum'] for r in summary],'o-',label='V09 grid and reference')
    axes[1].plot(x,[r['max_abs_error'] for r in summary],'s-',label='Dense grid and Cole–Hopf')
    axes[1].set(xticks=x,xticklabels=[r['variant'] for r in summary],ylabel='Median maximum absolute error',
                title='50 frozen models · no retraining')
    axes[1].tick_params(axis='x',rotation=20)
    axes[1].legend(fontsize=8)
    for ax in axes: ax.grid(alpha=.15)
    for ext in ('png','svg'): fig.savefig(output/f'reference_validation.{ext}',dpi=180)
    print(json.dumps({'validation':checks,'summary':summary},indent=2),flush=True)


if __name__ == '__main__':
    main()
