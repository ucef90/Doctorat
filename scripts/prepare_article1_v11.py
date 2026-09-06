"""Build the V11 editorial sources from frozen V10 evidence; never change scores."""
import argparse
import csv
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'submission/v11'
TITLE='Reference-Set Decoupled Co-Adaptive Training for Physics-Informed Neural Networks'

def write(name,text):
    (DEST/name).write_text(text,encoding='utf-8')

def bibliography():
    names=['raissi2019','wang2021','nabian2021','wu2023','song2025','toscano2026']
    refs=[]
    for key,r in zip(names,json.loads((DEST/'crossref_metadata.json').read_text())):
        refs.append(dict(id=key,type='article-journal',title=r['title'][0],
            author=[{k:a[k] for k in ('given','family') if k in a} for a in r['author']],
            issued=r.get('published-print',r['published']),DOI=r['DOI'],URL='https://doi.org/'+r['DOI'],
            volume=r.get('volume',''),page=r.get('page',r.get('article-number','')),
            **{'container-title':r['container-title'][0]}))
    extra=[
      ('chen2025','Self-adaptive weighting and sampling for physics-informed neural networks',
       [('Wenqian','Chen'),('Amanda','Howard'),('Panos','Stinis')],2025,'2511.05452v2'),
      ('singh2026','Stabilized Adaptive Loss and Residual-Based Collocation for Physics-Informed Neural Networks',
       [('Divyavardhan','Singh'),('Shubham','Kamble'),('Dimple','Sonone'),('Kishor','Upla')],2026,'2603.03224'),
      ('lau2024','PINNACLE: PINN Adaptive ColLocation and Experimental points selection',
       [('Gregory Kang Ruey','Lau'),('Apivich','Hemachandra'),('See-Kiong','Ng'),('Bryan Kian Hsiang','Low')],2024,'2404.07662'),
      ('celaya2025','Adaptive Collocation Point Strategies For Physics Informed Neural Networks via the QR Discrete Empirical Interpolation Method',
       [('Adrian','Celaya'),('David','Fuentes'),('Beatrice','Riviere')],2025,'2501.07700v4'),
      ('visser2025','PACMANN: Point Adaptive Collocation Method for Artificial Neural Networks',
       [('Coen','Visser'),('Alexander','Heinlein'),('Bianca','Giovanardi')],2025,'2411.19632v2'),
    ]
    for key,title,authors,year,identifier in extra:
        refs.append(dict(id=key,type='article',title=title,author=[dict(given=g,family=f) for g,f in authors],
            issued={'date-parts':[[year]]},URL='https://arxiv.org/abs/'+identifier,
            publisher='arXiv preprint' if key!='lau2024' else 'ICLR 2024; arXiv version'))
    refs.append(dict(id='burkardt',type='webpage',title='burgers_exact: Integral solution of the Burgers equation',
        author=[dict(given='John',family='Burkardt')],
        URL='https://people.sc.fsu.edu/~jburkardt/f77_src/burgers_exact/burgers_exact.html',
        accessed={'date-parts':[[2026,9,6]]}))
    write('references.json',json.dumps(refs,indent=2,ensure_ascii=False)+'\n')

def manuscript():
    old=(ROOT/'ARTICLE1_MANUSCRIPT_V10.md').read_text()
    text=old[old.index('## 1. Introduction'):old.index('## Core references')]
    replacements={
      'same draws and attaches the Hansen–Hurwitz weight':
       'same sampling mechanism and random-number streams, and attaches the Hansen–Hurwitz weight',
      'The preregistered common-backbone vRBA baseline':'The protocol-frozen common-backbone vRBA baseline',
      'New V09–V10 evidence follows in Sections 4.7–4.10.':'New V09–V10 evidence follows in Sections 4.7–4.11.',
      'M6 uses the same adaptive training set as M5 but computes':
       'ReCoA-PINN (M6) uses the same adaptive-sampling protocol as M5 but computes',
      'does not significantly improve\naccuracy':'does not show a conclusive improvement in\naccuracy under the reported paired interval',
      'The experiments separate three statements that are often conflated.':
       'The experiments evaluate the original fixed-reference hypothesis and separate three statements that are often conflated.',
      'A plausible interpretation is\nthat local attention sacrifices a narrow difficult region while improving a\nlarger portion of the solution; spatial maps and V09–V10 ablations now document this tradeoff, while its causal optimization mechanism remains unproven.':
       'The spatial maps document localized error patterns alongside lower global error. They do not establish that attention causes the localized spike. The V09–V10 ablations vary local/global mechanisms under fixed point sets, while the historical recipe comparisons also differ in sampling and controller details.',
      'A fixed\nreference set alone does not provide general stabilization.':
       'The tested fixed-reference ReCoA-PINN implementation does not establish general stabilization across the evaluated configurations.',
      'Equal-time comparisons and independent-machine replication remain open.':
       'Equal-time comparisons remain outside the claims of this paper. A separate-host portability protocol is supplied; its execution status is reported in the supplement.',
    }
    for a,b in replacements.items():
        assert a in text,a
        text=text.replace(a,b)
    text=text.replace('forward and inverse differential-equation problems.',
        'forward and inverse differential-equation problems [@raissi2019].',1)
    text=text.replace('and by several self-adaptive weighting methods.',
        'and by several self-adaptive weighting methods [@wang2021].',1)
    text=text.replace('comparison of nonadaptive and residual-based adaptive collocation.',
        'comparison of nonadaptive and residual-based adaptive collocation [@wu2023].',1)
    text=text.replace('training.\n\nThe closest antecedent',
        'training [@nabian2021].\n\nThe closest antecedent',1)
    text=text.replace('kernel density estimation. Recent work',
        'kernel density estimation [@song2025]. Recent work',1)
    text=text.replace('potentials and variational objectives.',
        'potentials and variational objectives [@toscano2026].',1)
    related='''
Chen, Howard and Stinis combine residual-decay weighting with adaptive sampling
[@chen2025]. Singh et al. combine smoothed gradient balancing and residual-based
collocation on Burgers and Allen–Cahn [@singh2026]. These are direct antecedents
to a broad co-adaptation claim. Our M5 comparator is not a faithful reproduction
of either full published protocol. The present contribution is the explicit
test of a fixed controller reference together with matched mechanism controls
and documented limitations.

Modern point-placement alternatives include PINNACLE, which selects collocation
and experimental points jointly [@lau2024], QR-DEIM-based collocation selection
[@celaya2025], and gradient-based point movement in PACMANN [@visser2025]. They
are discussed but not evaluated here. Consequently this study does not establish
state-of-the-art superiority over contemporary placement methods.

'''
    text=text.replace('## 3. Methods',related+'## 3. Methods')
    controller=r'''
### 3.2.1 Fixed-reference controller and interpretation

Let $R$ be the fixed reference set and $S_k$ the adaptive collocation set.
ReCoA-PINN computes controller losses and gradient norms on $R$ while updating
the network using $S_k$. M5 uses $S_k$ for both. The physics and known-condition
reference points are drawn independently at initialization; observed sensors
and their targets are shared. The reference set is used repeatedly to control
training and is therefore not an independent test set for the trained model.
Adaptive trajectories can subsequently diverge even with identical random seeds.

For component $j$, controller updates implement

\[
g_{j,k}=\|\nabla_\theta L_j\|_2,\quad
\bar g_{j,k}=\beta\bar g_{j,k-1}+(1-\beta)g_{j,k},\quad
a_{j,k}=\frac{\operatorname{mean}_\ell\bar g_{\ell,k}}{\bar g_{j,k}}
\left(\frac{L_{j,k}}{L_{j,0}}\right)^\alpha.
\]

The implementation normalizes $a_{j,k}$ to unit mean, clips it between
$w_{\min}$ and $w_{\max}$, renormalizes the clipped targets to unit mean and
then applies an EMA to the component weights. Here $\beta=0.95$,
$\alpha=0.5$, $w_{\min}=0.1$ and $w_{\max}=10$. Clipping occurs before the
second normalization: these settings are not strict final-weight bounds.
Positive numerical floors prevent division by zero. This paper evaluates the
implemented rule; it does not claim a convergence theorem for the controller.

At each iteration, the algorithm (i) refreshes the scheduled fraction of
collocation points if due, (ii) updates global component weights from the
method-specific reference if due, (iii) constructs the weighted training loss,
and (iv) takes one Adam step with gradient clipping. Evaluation points are never
used for these updates. For vRBA, local attention and its global controller are
updated on fixed point sets; its ablations are not ablations of adaptive point
placement or of the M6 reference mechanism.

### 3.2.2 Scope of exact proposal correction

For a frozen model $\theta$ and candidate population $C$, a fresh with-replacement
draw $I\sim q$ satisfies

\[
\mathbb E_{I\sim q}\left[\frac{r_\theta(z_I)^2}{N_c q_I}\;\middle|\;\theta,C,q\right]
=\frac{1}{N_c}\sum_{i=1}^{N_c}r_\theta(z_i)^2.
\]

This is a finite-population quadrature identity, not a guarantee for the full
adaptive optimization path. Retained points carry weights from earlier
candidate populations, and later model parameters depend on earlier samples.
The identity does not prove conditional unbiasedness of every later gradient
or elimination of continuous-domain discretization error. M7 and M7U share the
sampling algorithm and seeded random streams, but their model-dependent
proposals and realized point sets need not remain identical after training
diverges. The corrected-versus-uncorrected contrast concerns the full paired
training trajectories.

'''
    text=text.replace('### 3.3 Problems',controller+'### 3.3 Problems')
    problems=r'''
The governing equations and exact or independent targets are:

- **Burgers:** $u_t+u u_x-\nu u_{xx}=0$, with $\nu=0.01/\pi$,
  $x\in[-1,1]$, $t\in[0,1]$, $u(0,x)=-\sin(\pi x)$ and zero Dirichlet
  boundaries. V10 uses the Cole–Hopf integral solution [@burkardt].
- **Manufactured Allen–Cahn:** $u_t-Du_{xx}-\rho(u-u^3)=f$, with $D=10^{-3}$,
  $\rho=5$, the same space-time domain and $u=e^{-t}\sin(\pi x)$.
  The forcing is $f=-u+D\pi^2u-\rho(u-u^3)$; exact initial and boundary values
  are imposed softly. This is not the difficult unforced benchmark.
- **Wave:** $u_{tt}-c^2u_{xx}=0$, with $c=1$ on $[0,1]^2$,
  $u=\sin(\pi x)\cos(\pi t)$, zero boundary values, initial displacement
  $\sin(\pi x)$ and zero initial velocity. Displacement and velocity MSEs
  are summed in the initial-condition component.
- **Manufactured Helmholtz:** $\Delta u+k^2u=f$ on $[0,1]^2$, with $k=1$,
  $u=\sin(\pi x)\sin(\pi y)$ and $f=(1-2\pi^2)u$, with zero boundaries.

All final V09–V10 evaluations concern these four PDE families. The damped
oscillator mentioned in the original research blueprint is not included in
the reported experimental suite. All physical parameters above are prescribed;
the present experiments do not identify unknown PDE coefficients from data.

'''
    text=text.replace('### 3.4 Experimental controls',problems+'### 3.4 Experimental controls')
    text=text.replace('## 4. Results',r'''
### 3.6 Architecture, budgets and observation counts

All networks use tanh activations, Adam with learning rate $10^{-3}$,
float64 arithmetic, gradient clipping at 100 and one numerical CPU thread per
process. Table 1 summarizes the four base configurations. Architectures and
point cardinalities are matched between methods within each configuration,
not globally across all PDEs.

| Configuration | Hidden layers x width | Physics / initial / boundary points | V09 steps | V10 doubled steps |
|---|---|---|---:|---:|
| Burgers long | 4 x 48 | 512 / 128 / 128 | 2500 | 5000 |
| Allen–Cahn | 3 x 32 | 256 / 64 / 64 | 600 | 1200 |
| Helmholtz | 4 x 48 | 512 / 0 / 128 | 1500 | 3000 |
| Wave | 3 x 32 | 256 / 64 / 64 | 600 | 1200 |

: Base architectures and optimization budgets. The full resolved configurations are archived.

The four difficult-observation Burgers cases use 3 x 32 networks, 256 physics,
64 initial and 64 boundary points, and 600 steps. Their realized observation
counts are 13 (sparse clean), 13 (sparse noisy), 1 (extreme) and 64 (missing
block). The common-loss extension uses MSE throughout. Detailed noise settings
and all paired contrasts are supplied in the supplement.

### 3.7 Use of AI assistance and computational provenance

OpenAI's ChatGPT/Codex assisted code preparation, experimental and analysis
scripts, literature retrieval and manuscript drafting. Numerical results are
derived from the archived executable workflows and saved outputs; no figure is
generated by inventing experimental values. The assistant is distinct from the
PINN models being evaluated. Human author review, responsibility for the final
claims and final approval are pending in this author-review copy. The precise
assistant version should be recorded by the authors if available.

## 4. Results''')
    text=text.replace('## 5. Discussion','''
The following figures are generated from the stored numerical analyses.
Figure 1 documents the Burgers reference discrepancy; Figure 2 displays every
paired seed in the common-loss comparison; Figure 3 shows doubled-step
ablations. They must be interpreted together with the corrected statistics.

![Burgers reference validation and re-evaluation of frozen V09 models. The second panel also changes the evaluation grid; it does not isolate the reference change alone.](outputs/reference_v10_analysis/reference_validation.png){width=95%}

![Common-MSE Burgers comparisons. Points represent the ten individual seeds and black bars show medians. No inference is based solely on these visual rankings.](submission/v11/common_loss_by_seed.pdf){width=80%}

![Doubled-step ablations across four PDE configurations. Budgets match optimization steps within each PDE and do not equalize wall time.](outputs/budget_v10_analysis/l2_by_seed.png){width=80%}

## 5. Discussion''')
    text += '''
## Independent-host verification

On 6 September 2026, a separate GitHub-hosted Ubuntu runner reconstructed
the scores of all 560 frozen V10 models and all 96 paired contrasts within
the predeclared tolerance (relative $10^{-8}$, absolute $10^{-10}$).
The 55 automated tests passed. All 12 preselected retrainings completed and
their L2 and maximum errors met the predeclared numerical tolerance
(relative $10^{-3}$, absolute $10^{-5}$). The largest absolute differences
were $9.53\\times10^{-9}$ in L2 and $1.40\\times10^{-8}$ in maximum error.

The stricter joint gate nevertheless failed: initial model fingerprints
matched in all 12 cases, but training/reference-set fingerprints differed in
the four noisy-observation cases. Only 8/12 satisfied every declared condition.
The environments differ in host and PyTorch version (2.14.0+cpu versus
2.8.0+cpu). The original raw initial tensors were not retained, so the differing
bytes cannot be located retrospectively. A floating-point or library-version
effect is plausible but not established by these hashes. This is successful
numerical reconstruction with a documented input-identity limitation, not
bitwise reproduction of the complete experiment. The failed gate and its
thresholds are preserved in the repository and supplement.

## Author metadata and declarations

This is an author-review copy. Youssef EL MOUTEE is the identified working
author. The final author list and order, affiliations, corresponding-author
details, contributions, funding and competing-interest statements require
author confirmation before submission. No unconfirmed affiliation or consent
has been assigned to the supervisor. The code and archived evidence are in
the public repository [ucef90/Doctorat](https://github.com/ucef90/Doctorat),
with frozen V10 evidence at commit `4161ed57f232ea7b796480b38201502b3cabbf67`.
The AI-assistance description is provided in Methods; a final author-approved
declaration must accompany the submitted version.

## References {.unnumbered}
'''
    # Retain cross-reference numbers in prose; transform headings for Pandoc numbering.
    text=re.sub(r'^## \d+\. ', '# ',text,flags=re.M)
    text=re.sub(r'^### \d+\.\d+\.\d+ ', '### ',text,flags=re.M)
    text=re.sub(r'^### \d+\.\d+ ', '## ',text,flags=re.M)
    text=text.replace('## Data, code and reproducibility statement','# Data, code and reproducibility statement')
    text=text.replace('## Author metadata and declarations','# Author metadata and declarations')
    text=text.replace('## Independent-host verification','# Independent-host verification')
    text=text.replace('## References','# References')
    abstract='''Adaptive collocation changes the training measure observed by global loss
controllers in physics-informed neural networks (PINNs). We introduce and
evaluate reference-set decoupled co-adaptive training (ReCoA-PINN), which
estimates global component weights on a fixed reference set while optimizing
the network on adaptive collocation points. A controlled study compares this
mechanism with coupled control, proposal correction, kernel-density volume
weighting and variational residual attention on a common PyTorch backbone.
Historical paired experiments do not establish general stabilization or
accuracy gains from the fixed reference. We extend the evaluation with 200
V09 ablations and 560 V10 runs covering difficult observations, doubled
optimization budgets and common-loss comparisons. Independent Cole–Hopf
validation identifies a maximum discrepancy of 0.28578 in the historical
coarse Burgers reference. A Huber-versus-MSE confound is addressed through
new MSE-matched experiments. In the corrected comparison, variational residual
attention has the lowest median relative L2 error in four observation regimes;
11 of 16 paired L2 contrasts pass Holm correction, while no maximum-error
contrast passes its separate correction. These exploratory findings support
configuration-dependent conclusions. We distinguish the finite-population
identity of fresh importance-weighted samples from claims about the complete
adaptive training trajectory, and document the controls needed to assess
reference-set decoupling without assuming its superiority.'''
    assert len(abstract.split())<=250
    header=f'''---
title: "{TITLE}"
author: "Youssef EL MOUTEE"
date: "6 September 2026 - V11 author-review copy"
lang: en-US
---

*Original article title retained. Author metadata and final human approval are pending.*

# Abstract {{.unnumbered}}

{abstract}

**Keywords:** physics-informed neural networks; adaptive collocation; loss balancing;
reference sets; importance weighting; reproducibility.

'''
    combined=header+text
    # Number displayed equations, retaining all existing mathematical content.
    combined=re.sub(r'\\\[\s*\n(.*?)\n\\\]',lambda m:'\\begin{equation}\n'+m[1]+'\n\\end{equation}',combined,flags=re.S)
    # Give every table a caption, so it is numbered consistently in LaTeX.
    chunks=combined.split('\n'); result=[]; in_table=False; number=0
    captions=['Base architectures and optimization budgets.',
      'Median relative L2 error under difficult observations.',
      'Median relative L2 error at doubled optimization budgets.',
      'Planned doubled-budget contrasts passing Holm correction.',
      'Common-loss baseline median relative L2 errors.',
      'Common-loss paired contrasts passing Holm correction.']
    for i,line in enumerate(chunks):
        if line.startswith('|') and not in_table:
            result.extend(['\\begingroup\\small','']);in_table=True;number+=1
        if in_table and not line.startswith('|'):
            result.extend(['',': '+captions[number-1],'','\\endgroup','']);in_table=False
        if line.startswith(': Base architectures'): continue
        result.append(line)
    write('MANUSCRIPT.md','\n'.join(result))
    write('abstract_word_count.txt',str(len(abstract.split()))+'\n')

def supplement():
    noise_note='For clean sensor values y, the scale is the maximum of their population standard deviation, mean absolute value and 1e-12. Gaussian corruption adds noise level times scale times independent standard-normal draws. Correlated corruption first applies z[j] = 0.8 z[j-1] + 0.6 e[j], initialized with z[0] = e[0]. This correlation follows sensor-array order; it is not a prescribed physical time-covariance model. Outliers add random signed shifts of 5 times max(noise level, 0.01) times scale to the configured fraction of entries. The missing-block case removes the middle 50 percent of 128 sensors ranked by time, retaining 64; the removed interval depends on the seed rather than a fixed pair of endpoints.'
    text=['---',f'title: "Supplement - {TITLE}"','author: "Youssef EL MOUTEE"',
      'date: "V11 - 6 September 2026"','lang: en-US','---','',
      '# Scope and evidence', '',
      'The supplement preserves the complete V10 paired-contrast families. It introduces no new method-ranking evidence. Original V10 data are frozen at commit `4161ed57f232ea7b796480b38201502b3cabbf67`.', '',
      '# Observation regimes', '',
      '| Case | Sensors | Noise | Noise level | Outlier fraction | Missing pattern |',
      '|---|---:|---|---:|---:|---|']
    for case in ['sparse_clean','sparse_noisy','extreme','block_missing']:
        r=json.loads((ROOT/f'outputs/robustness_v10_campaign/cells/{case}__full_exp__11/result.json').read_text())
        o=r['observations'];text.append(f"| {case.replace('_',' ')} | {o['effective_count']} | {o['noise_kind']} | {o['noise_level']} | {o['outlier_fraction']} | {o['missing_pattern']} |")
    text+=['', 'Counts above are checked against stored run summaries. The code defines noise scaling and the missing-time-block construction in `src/recoa_pinn/problems/base.py`. All V10 comparisons use MSE for observations; the historical Huber recipes remain separately identified.', '',
      '# Inference and notation', '',
      'Ten paired seeds are used: 11, 22, 33, 44, 55, 66, 77, 88, 99, 111. The exact two-sided sign test ignores zero differences. Percentile intervals use 10,000 paired bootstrap resamples and seed 9092026. Holm correction is applied to 16 contrasts separately for each metric and campaign. Intervals are marginal, not simultaneous. A nonsignificant difference does not establish equivalence.', '',
      'Notation: F = full exponential; Q = full quadratic; G = global only; L = local only; N = neither; V = vRBA. Interaction = F - G - L + N on the additive error scale. L2 is relative solution error; max is the maximum absolute error on the declared grid, not a certified continuous-domain bound. Negative F-G and V-M contrasts favor F and V, respectively.', '']
    labels={'full_exp-local_only':'F-L','full_exp-global_only':'F-G','full_exp-full_quad':'F-Q','interaction':'F-G-L+N',
       'vrba-m5':'V-M5','vrba-m6':'V-M6','vrba-m7':'V-M7','vrba-vw':'V-VW'}
    for name,directory in [('Difficult-observation ablations','robustness_v10_verified'),('Doubled-step ablations','budget_v10_analysis'),('Common-loss baselines','common_loss_v10_analysis')]:
        rows=list(csv.DictReader((ROOT/'outputs'/directory/'paired_statistics.csv').open()))
        for metric in ['relative_l2','max_abs_error']:
            text+=['\\newpage','',f'# {name}: {"L2" if metric=="relative_l2" else "maximum error"}', '',
                '\\begingroup\\small','', '| Case | Contrast | Median difference | Marginal 95% CI | Sign p | Holm p |',
                '|---|---|---:|---|---:|---:|']
            for r in rows:
                if r['metric']!=metric:continue
                fmt=lambda key:f'{float(r[key]):.5f}'
                text.append(f"| {r['problem'].replace('_',' ')} | {labels[r['contrast']]} | {fmt('median_difference')} | [{fmt('ci95_low')}, {fmt('ci95_high')}] | {fmt('p_sign')} | {fmt('p_holm_16')} |")
            text+=['', '\\endgroup', '', 'All 16 planned contrasts are retained. The corresponding CSV contains full numerical precision, sign counts, sample size and mean differences.']
    text+=['\\newpage','', '\\begingroup\\small','', '# Independent-host reproduction protocol', '',
      'The protocol reconstructs scores of all 560 archived V10 models and all 96 paired contrasts, then retrains 12 cases chosen before execution: seed 11, global-only and full-exponential for all four doubled-budget PDEs; noisy Burgers M5, M6, M7 and full-exponential at the V10 robustness budget. Selection uses the lowest declared seed, not favorable outcomes.', '',
      'Frozen-score/table tolerance: relative 1e-8, absolute 1e-10. Retraining tolerance: relative 1e-3, absolute 1e-5 for L2 and maximum error, with exact matching initial tensor fingerprints and completed step counts. Discrepancies are retained and thresholds are not relaxed after observation.', '',
      'The original runtime reports Python 3.12.13, PyTorch 2.14.0+cpu and NumPy 2.3.5. The portable public environment pins Python 3.12, PyTorch 2.8.0+cpu and NumPy 2.3.5, with SciPy 1.16.1 and Matplotlib 3.10.5. It therefore tests portability across both host and PyTorch version, not bitwise replication of an identical software stack.', '']
    validation=DEST/'reproduction/validation.json'
    if validation.exists():
        v=json.loads(validation.read_text())
        text+=['Execution evidence is included in `submission/v11/reproduction/`.', '',
          'The independent Ubuntu execution reproduced all 560 frozen scores and all 96 contrast statistics. The 55 automated tests passed. All 12 retrainings met the original numerical tolerances and completed the prescribed steps.', '',
          f"The complete predeclared gate passed for {v.get('retrainings_passed')}/{v.get('retrainings')} cases; overall gate = {v.get('passed')}. Initial model fingerprints match in all 12 cases. Training/reference-set fingerprints differ in the four noisy-observation cases, so their strict gate remains failed.", '',
          'The maximum absolute differences in final errors are 9.5275e-9 for L2 and 1.3997e-8 for maximum error. The original raw initial tensor arrays were not archived; hashes alone cannot identify the differing entries or establish the cause. A cross-version numerical effect is plausible but unproven. The original validation file remains unchanged.', '',
          '[Independent workflow and preserved failure](https://github.com/ucef90/Doctorat/actions/runs/34021530276). The complete 12-case comparison and original/new fingerprints are archived with this submission package.']
    else:text+=['Execution status: the workflow has been launched; final evidence is pending. This draft does not claim that the independent-host gate has passed.']
    text+=['', '# Observation model details','',noise_note,'', '# Limitations of the independent check','',
      'These 12 retrainings are numerical portability checks, not 12 new independent physical cases or a new confirmatory statistical campaign. They do not establish portability across all GPUs, compilers and accelerators. All scientific conclusions remain tied to the original controlled experiments and stated limitations.']
    text+=['','\\endgroup','']
    write('SUPPLEMENT.md','\n'.join(text).rstrip()+'\n')

def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=list(csv.DictReader((ROOT/'outputs/common_loss_v10_analysis/evaluation.csv').open()))
    fig,axes=plt.subplots(2,2,figsize=(9,6),constrained_layout=True)
    methods=['m5','m6','m7','vw','vrba']
    for ax,case in zip(axes.flat,['sparse_clean','sparse_noisy','extreme','block_missing']):
        for i,m in enumerate(methods):
            vals=[float(r['relative_l2']) for r in rows if r['problem']==case and r['variant']==m]
            assert len(vals)==10
            ax.scatter([i+(j-4.5)*.025 for j in range(10)],vals,s=20,color=['#71808c','#176b87','#36967e','#c0952b','#bc4564'][i])
            ax.hlines(sorted(vals)[4]*.5+sorted(vals)[5]*.5,i-.2,i+.2,color='black',lw=1.4)
        ax.set_xticks(range(5),['M5','M6','M7','VW','vRBA']);ax.set_title(case.replace('_',' '))
        ax.set_ylabel('Relative L2 error');ax.grid(axis='y',alpha=.2)
    fig.savefig(DEST/'common_loss_by_seed.pdf');plt.close(fig)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--sources-only',action='store_true')
    a=parser.parse_args();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    bibliography();manuscript();supplement();figure()
    highlights=[
      'Fixed-reference control is tested without assuming universal stabilization.',
      'An independent Burgers reference changes the interpretation of local errors.',
      'Common-loss experiments address a Huber-versus-MSE comparison confound.',
      'Paired ablations reveal effects that depend on PDE and training horizon.',
      'Frozen checkpoints and protocols support independent numerical verification.']
    assert all(len(s)<=85 for s in highlights)
    write('HIGHLIGHTS.txt','\n'.join(highlights)+'\n')
    dossier=(DEST/'EDITORIAL_DOSSIER.md').read_text()
    write('COVER_LETTER_DRAFT.md',dossier[dossier.index('Dear Editors'):])
    header=r'''\usepackage{float}
\usepackage{fvextra}
\usepackage{microtype}
\usepackage{etoolbox}
\usepackage{fancyhdr}
\AtBeginEnvironment{CSLReferences}{\small\setstretch{1.0}\interlinepenalty=10000}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\small Article 1 / V11 / Author-review copy \quad \thepage}
\renewcommand{\headrulewidth}{0pt}
\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{4pt}
\floatplacement{figure}{H}
'''
    write('layout.tex',header)
    for source,name in [('MANUSCRIPT.md','ARTICLE1_MANUSCRIPT_V11'),('SUPPLEMENT.md','ARTICLE1_SUPPLEMENT_V11'),('EDITORIAL_DOSSIER.md','ARTICLE1_DOSSIER_VALIDATION_V11')]:
        common=['pandoc',str(DEST/source),'-f','markdown+tex_math_single_backslash','--standalone','--number-sections',
          '--citeproc','--bibliography',str(DEST/'references.json'),'-V','documentclass=article','-V','fontsize=11pt',
          '-V','geometry:margin=2.2cm','-V','mainfont=Latin Modern Roman','-V','monofont=DejaVu Sans Mono',
          '-V','linestretch=1.12','-V','colorlinks=true','-V','urlcolor=teal','-H',str(DEST/'layout.tex')]
        subprocess.run(common+['-o',str(DEST/(name+'.tex'))],cwd=ROOT,check=True)
        if not a.sources_only:
            subprocess.run(common+['--pdf-engine=xelatex','-o',str(out/(name+'.pdf'))],cwd=ROOT,check=True)
    print(out)

if __name__=='__main__':main()
