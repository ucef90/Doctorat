# Manuscript V10 — Article 1

Research draft, 5 September 2026. Historical comparisons and the V09–V10 exploratory extensions are explicitly separated. Not submitted or peer reviewed.

## Proposed title

**Adaptive PINNs under Competing Training Measures: A Controlled Study of Fixed
References, Exact Reweighting, KDE Volume Weighting, and Variational Residual
Attention**

French translation:

**PINNs adaptatifs sous mesures d'entraînement concurrentes : étude contrôlée
des références fixes, de la repondération exacte, de la pondération volumique
KDE et de l'attention variationnelle aux résidus**

## Abstract

Physics-informed neural networks often combine adaptive loss balancing and
residual-based collocation, coupling the training distribution to the gradients
used by the controller. We study this interaction on a common PyTorch backbone
using fixed references, finite-candidate proposal correction, KDE volume
weighting, and variational residual-based attention (vRBA). Historical paired
experiments across four PDE families show measurable distribution–gradient
discrepancies without general stabilization from a fixed reference. We extend
that study with 200 local/global/potential ablations and 560 further runs
covering difficult observations, doubled optimization budgets and common-loss
baseline comparisons. An independent Cole–Hopf reference reveals a maximum
discrepancy of 0.28578 in the historical coarse Burgers reference and enables
re-evaluation of the frozen models. A loss audit identifies a Huber-versus-MSE
confound in historical noisy comparisons; new MSE-matched runs address it.
In the corrected comparison, vRBA has the lowest median relative L2 in all
four observation regimes, with 11 of 16 paired contrasts passing Holm at 5%,
while no maximum-error contrast passes the separate correction. The factorial
results depend on PDE and training horizon: the wave-equation quadratic-potential
advantage at 600 steps is not established after correction at 1200 steps.
These exploratory results support conditional performance benefits rather
than universal superiority. They distinguish restoring a sampling measure
from tilting an objective and show why reference validation, common-loss
controls, multiple error metrics and budget sensitivity are necessary for
interpreting adaptive PINN comparisons.

## Résumé français

Nous étudions les interactions entre pondération des pertes et collocation
adaptative sur une architecture PyTorch commune. L'étude historique est
complétée par 200 ablations V09 et 560 nouveaux entraînements V10, avec données
difficiles, budgets doublés et comparateurs sous perte commune. Une référence
Cole–Hopf indépendante met en évidence un écart local de 0,28578 dans l'ancienne
référence Burgers. L'audit révèle aussi une différence Huber/MSE, corrigée dans
les nouvelles comparaisons bruitées. vRBA obtient alors la meilleure médiane
L2 dans les quatre régimes et 11 contrastes L2 sur 16 passent Holm à 5 %, sans
avantage établi sur le maximum après correction. Les effets des ablations
dépendent de l'équation et de la durée d'entraînement. La contribution est une
étude contrôlée et reproductible de ces compromis, sans revendication de
supériorité universelle ni de validation sur des données de tokamak.

**Keywords:** physics-informed neural networks; adaptive sampling; loss
balancing; importance weighting; variational residual attention; collocation
bias; sparse data; reproducibility

## 1. Introduction

Physics-informed neural networks (PINNs) approximate a physical field while
penalizing the residual of its governing differential equation. Their training
objective generally combines the physics residual, initial and boundary
conditions, and, when available, observations. Because these components can
have different scales and convergence rates, adaptive global loss balancing is
frequently used. Residual-based adaptive sampling is also used to allocate more
collocation points to poorly resolved regions.

Each mechanism is reasonable in isolation, but their joint use raises a subtle
question. If the global loss controller estimates the importance of the physics
term on the same nonuniform points selected by the residual sampler, it no
longer observes the original uniform-domain objective. The controller and the
sampler may therefore reinforce one another. This interaction is distinct from
the well-known imbalance between loss components: it concerns the measure under
which a component is evaluated.

Previous work has already established adaptive loss balancing, residual-based
sampling, importance sampling, volume correction and variational residual
attention. Therefore, our aim is not to claim the invention of these individual
mechanisms. We conduct a controlled study of competing training measures:
retaining the coupled controller, estimating global weights on a fixed
reference set, correcting a known discrete proposal, estimating local volume
by KDE, or deliberately tilting the objective through vRBA.

The study asks five questions:

1. Does residual sampling measurably alter the component losses and gradients
   observed by a global controller?
2. Does a fixed, independent reference set improve training stability or
   solution accuracy?
3. Does exact proposal correction improve a matched uncorrected adaptive
   sampler under sparse and noisy data?
4. Are the conclusions robust to PDE family and to an established alternative,
   KDE volume weighting?
5. Does a deliberately tilted variational objective improve global and local
   errors consistently on the same backbone?

Our principal finding is conditional. The feedback is measurable and exact
correction can be beneficial. vRBA performs favorably in historical relative-L2 comparisons, but a common-loss audit qualifies the noisy-data claim; maximum error and cost do not show universal dominance. This mixture of positive, null and
negative results identifies the controls required before an adaptive PINN
method can credibly claim robustness.

## 2. Related work and positioning

Raissi, Perdikaris and Karniadakis established the modern PINN formulation for
forward and inverse differential-equation problems. Gradient-flow pathologies
and adaptive balancing were subsequently analyzed by Wang, Teng and Perdikaris
and by several self-adaptive weighting methods. Wu et al. provided a broad
comparison of nonadaptive and residual-based adaptive collocation. Nabian,
Gladstone and Meidani introduced importance sampling for more efficient PINN
training.

The closest antecedent to the measure question is VW-PINNs by Song et al. They
show that nonuniform collocation can make the standard empirical PDE loss
ill-conditioned and propose weighting residuals by local volumes estimated via
kernel density estimation. Recent work has gone further: joint weighting and
sampling methods explicitly combine the two mechanisms, while the vRBA
framework of Toscano et al. interprets residual adaptivity through convex
potentials and variational objectives.

These studies prevent two overly broad claims: combining loss weighting and
adaptive sampling is not new, and correcting the effect of a nonuniform
collocation measure is not new. The potentially useful contribution here is a
paired controlled design that contrasts a fixed controller reference, a known-
proposal correction, KDE volume correction, a variational tilted objective and
matched controls under exactly the same PyTorch backbone.

## 3. Methods

### 3.1 Base objective

For model parameters \(\theta\), the total objective is

\[
\mathcal L(\theta)=
\sum_{j\in\{f,i,b,d\}}\lambda_j\mathcal L_j(\theta),
\]

where \(f\), \(i\), \(b\), and \(d\) denote the physics, initial-condition,
boundary-condition and observation terms. The standard physics term on
collocation points \(z_i\) is

\[
\mathcal L_f=\frac1N\sum_{i=1}^{N}r_\theta(z_i)^2.
\]

### 3.2 Controlled variants

M0 uses uniform collocation and fixed component weights. M1 adds adaptive
component weights. M3 adds residual sampling but retains fixed component
weights. M5 combines both mechanisms and computes the controller update on the
adaptive training set. M6 uses the same adaptive training set as M5 but computes
the controller update on a fixed independent audit set of equal cardinality.

M7U samples with replacement from a finite candidate pool according to the
residual proposal \(q\), but leaves the physics loss uncorrected. M7 uses the
same draws and attaches the Hansen–Hurwitz weight

\[
w_i=\frac{1}{N_c q_i},
\qquad
\widehat{\mathcal L}_{f,\mathrm{M7}}
=\frac1N\sum_iw_i r_\theta(z_i)^2,
\]

where \(N_c\) is the candidate-pool size. Retained points keep the proposal
weight assigned when they were sampled. A uniform proposal floor bounds the
largest possible importance weight.

For VW and VW-CA, a Gaussian KDE estimates the density of the realized
collocation set after mapping all coordinates to the unit hypercube. With
\(V_i\propto1/\widehat p_h(z_i)\), the physics loss is

\[
\mathcal L_{f,\mathrm{VW}}
=\frac{\sum_iV_i^2r_\theta(z_i)^2}{\sum_iV_i^2}.
\]

VW uses fixed global component weights. VW-CA uses the same adaptive global
controller as M5 and M7. The default KDE bandwidth follows Scott's rule;
separate runs use 0.5, 1 and 2 times this bandwidth.

For vRBA, fixed point sets receive persistent local multipliers. With the
exponential potential, the numerically stable normalized attention target is

\[
\widehat q_i^k=
\exp\!\left(\frac{|r_i|-\max_j|r_j|}{\epsilon_k}\right),
\qquad
\epsilon_k=\frac{c\max_j|r_j|}{\log(k+2)}.
\]

The local update and component loss are

\[
\lambda_i^{k+1}=\gamma_k\lambda_i^k+
\eta\left(\phi\widehat q_i^k+1-\phi\right),
\qquad
\mathcal L_j^{\mathrm{vRBA}}=
\frac1{N_j}\sum_i(\lambda_{j,i}r_{j,i})^2.
\]

The physics component keeps global weight one; other component weights track
ratios of exponentially smoothed gradient norms. We use the published
first-order defaults (`eta=0.01`, `phi=0.8`, local cap schedule, gradient EMA
`0.99`, global-weight EMA `0.99975`). This is a controlled PyTorch
common-backbone implementation of the vRBA mechanism, not an exact reproduction
of the authors' JAX architecture, hard constraints, optimizer sequence or
training horizon.

### 3.3 Problems

The benchmark suite contains viscous Burgers, a manufactured Allen–Cahn
problem, a standing-wave equation and a manufactured two-dimensional Helmholtz
problem. An initial high-frequency Helmholtz screen was not used for method
ranking because every method had relative error above one. We calibrated a
solvable configuration using only M0 and a predetermined criterion
\(L_2<0.2\), then froze it before comparing adaptive methods.

Four Burgers observation regimes assess robustness: thirteen clean
observations; thirteen observations with Gaussian noise and outliers; one
observation with strong heteroscedastic noise; and a missing sensor block with
correlated noise.

### 3.4 Experimental controls

The historical ten-seed comparisons and the exploratory V09–V10 campaigns use ten paired seeds
`11, 22, 33, 44, 55, 66, 77, 88, 99, 111`. Methods share architecture,
initialization seed, observation realization, collocation cardinality and clean
evaluation target. All configurations and environment metadata are stored with
each run. Failed runs are retained and reported rather than silently discarded.

The primary metric is relative \(L_2\) error. Secondary metrics include maximum
absolute error, component-weight total variation, the total-variation distance
between component-gradient distributions on training and audit points, the
logarithmic physics-gradient gap, wall time, residual evaluations, importance-
weight effective sample size, and KDE pairwise-distance counts.

We report medians, quartiles, paired median differences, 95% bootstrap
intervals and two-sided sign tests. A method is not called superior when only
its point estimate improves or when the paired interval crosses zero.


### 3.5 V09–V10 extensions and common-loss audit

V09 consists of 200 runs: four PDE configurations, five local/global/potential
variants and ten seeds. V10 adds 200 Burgers observation-regime runs, 200 doubled-step runs and 160 common-loss baseline runs. The latter reuse 40 existing V10 vRBA checkpoints for comparison. Each suite freezes its manifest before training but follows
earlier empirical findings; these suites are exploratory, not independent
confirmations of hypotheses selected using V07 or V09.

The four factorial arms are neither, global_only, local_only and full_exp;
full_quad changes only the potential relative to full_exp. V10 uses MSE for
observations in every arm. In historical noisy-data comparisons, local vRBA
multipliers triggered a squared residual loss while several non-vRBA methods
used Huber. Consequently, those comparisons contrast complete recipes and do
not identify an effect of attention alone. V10 synthetic Burgers observations
and evaluation targets use the independent Cole–Hopf solution.

For each suite, four predeclared contrasts per case form a family of 16 tests
for relative L2, with a separate family for maximum absolute error. We use
two-sided exact sign tests, Holm correction, and 10000-resample percentile
bootstrap intervals for the paired median difference. Intervals are marginal,
not simultaneous. Initialization and observation tensors are fingerprinted;
the 400 factorial/budget V10 checkpoints are re-evaluated independently, including a denser grid; the 160 additional baseline checkpoints are independently checked on the original scoring grid.

## 4. Results

Sections 4.1–4.6 report historical configurations and references. New V09–V10 evidence follows in Sections 4.7–4.10. Historical noisy-data rankings are recipe comparisons subject to the loss confound described in Section 3.5.

### 4.1 Fixed-reference decoupling

On long Burgers runs, M5 shows a positive concentration–gradient-gap
correlation in all ten seeds. Nevertheless, M6 does not significantly improve
accuracy: the paired median difference M6−M5 is \(-0.0291\), with 95% interval
\([-0.1208,0.1678]\). Nor does it consistently reduce weight variation.
Because controller cardinality and residual-evaluation counts are matched, this
null result cannot be attributed to additional reference points.

### 4.2 Exact correction and its matched control

M7 substantially reduces the mean physics-gradient log-gap relative to M7U on
Burgers: paired median difference \(-0.4351\), 95% interval
\([-0.6182,-0.2520]\), favorable in all ten seeds. Across the four difficult
observation regimes, M7 also improves relative \(L_2\) error over M7U by
\(-0.0483\), \(-0.0482\), \(-0.0229\), and \(-0.0360\), respectively; every
bootstrap interval excludes zero.

This effect is not universal. On Allen–Cahn, M7 is worse than M7U by a paired
median of \(+0.0097\), with a 95% interval just above zero. Thus, restoring the
chosen target measure may improve diagnostic alignment while worsening the
optimization trajectory for a particular PDE.

### 4.3 Comparison with KDE volume weighting

On the standing-wave problem, fixed-weight VW is better than M7 in all ten
seeds: M7−VW is \(+0.0280\), 95% interval \([0.0199,0.0483]\). On calibrated
Helmholtz, the ranking reverses: M7−VW is \(-0.0181\), 95% interval
\([-0.0235,-0.0112]\), favorable to M7 in all ten seeds. Burgers long and
Allen–Cahn show no conclusive difference between M7 and VW.

At the default KDE bandwidth, M7 outperforms VW-CA in each of the four difficult
Burgers observation regimes, with paired intervals excluding zero. However, M7
does not outperform the simpler fixed-weight VW in any of those four regimes.
The addition of a global adaptive controller therefore does not automatically
improve a locally corrected loss.

### 4.4 Bandwidth sensitivity

The KDE choice changes the conclusion. On noisy Burgers, reducing the bandwidth
to 0.5 times Scott's rule yields median errors 0.4742 for VW and 0.5527 for M7.
The paired M7−VW difference is \(+0.0710\), 95% interval
\([0.0161,0.1165]\). At that bandwidth, the previously favorable M7−VW-CA
contrast also becomes inconclusive. On the wave equation, VW remains better
than M7 at all three tested bandwidth scales.

### 4.5 Computational cost

In a dedicated sequential CPU profile, M7 adds a median 10.5% wall-time cost
relative to M5, 7.2% relative to M6 and 4.9% relative to M7U, while retaining
the same number of residual evaluations. For 256 collocation points and 600
steps, the dense VW correction additionally evaluates 1,638,400 pairwise KDE
distances per run. The correction part of M7 is linear after the proposal is
known, whereas dense KDE is quadratic in the number of collocation points.
This theoretical advantage has not yet been verified by a dedicated multi-size
CPU/GPU profile.

### 4.6 Variational residual-based attention

The preregistered common-backbone vRBA baseline completes all runs without
non-finite values. Its final attention effective-sample fraction ranges from
0.785 to 0.990, confirming non-uniform but non-collapsed local weighting.

vRBA obtains median relative L2 errors of 0.2507 on Burgers, 0.0401 on
Allen–Cahn, 0.0388 on calibrated Helmholtz, and 0.1745 on the wave equation.
Against M7, paired median differences are respectively -0.1770
[-0.2339, -0.0114], -0.0648 [-0.0903, -0.0509], -0.0611
[-0.0690, -0.0496], and -0.1322 [-0.2163, -0.1190]. Against fixed-weight VW,
they are -0.1236 [-0.2566, -0.0283], -0.0617 [-0.1269, -0.0267], -0.0844
[-0.0891, -0.0608], and -0.1061 [-0.1502, -0.0836].

The same L2 signal persists across clean sparse data, noisy and outlier-
contaminated data, one strongly corrupted observation, and a missing sensor
block. However, the extreme one-observation regime has only eight favorable
seeds out of ten against M7 and VW, yielding a two-sided sign-test p-value of
0.109 despite bootstrap intervals below zero.

The maximum-error result contradicts a universal robustness interpretation.
On long Burgers runs, vRBA's median maximum error is 1.7209, compared with
1.3429 for M5 and 1.2993 for M6. The paired vRBA-M5 difference is +0.3336
[0.0265, 0.5694], and vRBA-M6 is +0.4011 [0.2067, 0.5759]. Thus, vRBA improves
the global L2 norm while worsening the largest localized error. Observed
runtime overhead relative to M5 ranges from 10.4% to 81.8% across PDEs.

Spatial analysis resolves this apparent contradiction. The median across seeds
of the gridwise 95th absolute-error percentile is 0.1027 for vRBA, versus
0.6698 for M5 and 0.6907 for M6; the corresponding 99th percentiles are 0.8588,
1.1470 and 1.0516. vRBA therefore improves almost the entire domain while
leaving a very narrow late-time error spike near the shock. In the median error
field, this spike peaks around \(t=0.975\), \(x=-0.025\).


### 4.7 Local/global decomposition at the V09 budgets

The 200-run V09 campaign found that full exponential vRBA improves relative
L2 against both local-only and global-only variants for the calibrated
Helmholtz case (k=1). Both contrasts and the additive-scale interaction pass
Holm at p=0.03125. For the wave case, the quadratic potential improves L2
against the exponential potential (Holm p=0.03125). No planned Burgers
contrast passes the multiplicity correction. These are configuration-specific
findings, not evidence of a universally optimal potential or controller.

V09 separately measured 60 CPU windows using three seeds, five variants and
four PDEs. Fifty-nine profiling trials completed; the last trial ended after
the prespecified timing window. The full exponential variant has median
paired per-step cost ratios of about 1.71–1.86 relative to neither. These are
local per-step measurements, not time-to-accuracy or equal-time rankings.

### 4.8 Independent Burgers reference

Cole–Hopf quadrature at orders 128 and 256 agrees within 9.11e-15 on the tested
161-by-321 grid. Adaptive quadrature independently verifies 20 selected points
within 4.44e-16. The historical Rusanov reference with 257 spatial points differs
from this solution by 0.03410 in relative L2 and 0.28578 in maximum error;
at 1025 points these discrepancies fall to 0.00733 and 0.06969.

Re-evaluating all 50 frozen V09 Burgers models on the dense grid with Cole–Hopf
gives median L2 values 0.30724, 0.26523, 0.22496, 0.26369 and 0.26370 for
neither, global_only, local_only, full_exp and full_quad respectively.
No planned contrast passes Holm in this exploratory four-contrast reanalysis.
The numerical-reference discrepancy does not explain away the observed large
model errors, but it prevents treating historical maximum errors as exact.

### 4.9 Sparse and corrupted observations under a common loss

All 200 runs finish successfully and all 40 five-arm initialization blocks
match. The table reports median relative L2 on clean Cole–Hopf targets.

| Case | Neither | Global only | Local only | Full exp. | Full quad. |
|---|---:|---:|---:|---:|---:|
| extreme | 0.53812 | 0.53812 | 0.44694 | 0.45883 | 0.47695 |
| sparse_noisy | 0.46306 | 0.46373 | 0.37333 | 0.37603 | 0.41816 |
| sparse_clean | 0.46061 | 0.45779 | 0.38439 | 0.36866 | 0.40329 |
| block_missing | 0.44003 | 0.43793 | 0.34951 | 0.34398 | 0.34288 |

After correction, full_exp improves L2 over global_only for the missing-block
case (paired median difference -0.06999, marginal 95% CI [-0.09386,-0.03466],
Holm p=0.03125). For extreme data, full_exp improves the maximum error over
full_quad (difference -0.06696, CI [-0.12910,-0.00587], Holm p=0.03125).
Other planned contrasts do not pass Holm. Section 4.11 separately retests the historical M5/M6/M7/VW comparisons with a common observation loss.

### 4.10 Doubled optimization budgets

The 200 additional runs use 5000 Burgers, 1200 Allen–Cahn, 3000 Helmholtz and
1200 wave steps. The following median relative L2 values come from independent
checkpoint evaluations. Initial tensors match both within each five-arm block
and against the historical V09 counterparts. No model selection is based on
the evaluation scores.

| Case | Neither | Global only | Local only | Full exp. | Full quad. |
|---|---:|---:|---:|---:|---:|
| helmholtz | 0.08717 | 0.01917 | 0.03245 | 0.00523 | 0.02076 |
| allen_cahn | 0.02859 | 0.02873 | 0.02573 | 0.02785 | 0.02291 |
| burgers | 0.30754 | 0.24549 | 0.20305 | 0.25680 | 0.26014 |
| wave | 0.12374 | 0.13976 | 0.02578 | 0.02747 | 0.02652 |

Planned contrasts passing Holm in the doubled-step suite are listed below;
the complete table, including null and adverse contrasts, accompanies the code.

| Case | Metric | Contrast | Paired median difference | Marginal 95% CI | Holm p |
|---|---|---|---:|---|---:|
| wave | relative_l2 | full_exp-global_only | -0.10001 | [-0.14629, -0.08958] | 0.03125 |
| helmholtz | max_abs_error | interaction | +0.11349 | [+0.08393, +0.13949] | 0.03125 |
| wave | max_abs_error | full_exp-global_only | -0.19593 | [-0.30415, -0.14881] | 0.03125 |

The quadratic-potential L2 advantage established for the V09 wave configuration does not pass Holm at the doubled horizon. Full_exp still improves both L2 and maximum error over global_only for waves. A positive Helmholtz maximum-error interaction reflects the additive contrast and does not imply that full_exp is the least accurate model.

The doubled-step comparison measures sensitivity to optimization duration.
It is not an equal-compute or equal-time experiment, and historical and V10
wall times must not be pooled as a controlled timing comparison.

### 4.11 Re-running the historical baselines with a common observation loss

An additional 160 runs cover M5, M6, M7 and VW across the same four observation
regimes and ten seeds, using the exact V10 MSE/Cole–Hopf configurations.
Forty full_exp checkpoints from Section 4.9 are reused as vRBA comparators;
they are not new or independent training runs. Initial parameter and observation
tensors match across all five compared methods. The table gives median L2.

| Case | M5 | M6 | M7 | VW | vRBA |
|---|---:|---:|---:|---:|---:|
| block_missing | 0.56166 | 0.55393 | 0.53397 | 0.48595 | 0.34398 |
| sparse_clean | 0.58673 | 0.55823 | 0.55471 | 0.49238 | 0.36866 |
| sparse_noisy | 0.57248 | 0.55808 | 0.54189 | 0.50375 | 0.37603 |
| extreme | 0.61185 | 0.60330 | 0.59146 | 0.56037 | 0.45883 |

All newly trained checkpoints have been independently re-evaluated. The
following contrasts pass Holm in the separately declared family of 16 per
metric. All contrasts, including null and unfavorable effects, are retained
in the accompanying paired_statistics.csv.

| Case | Metric | Contrast | Paired median difference | Marginal 95% CI | Holm p |
|---|---|---|---:|---|---:|
| block_missing | relative_l2 | vrba-m5 | -0.19580 | [-0.24059, -0.18515] | 0.03125 |
| block_missing | relative_l2 | vrba-m6 | -0.19318 | [-0.24042, -0.18069] | 0.03125 |
| block_missing | relative_l2 | vrba-m7 | -0.17172 | [-0.20840, -0.12736] | 0.03125 |
| block_missing | relative_l2 | vrba-vw | -0.13158 | [-0.15465, -0.09959] | 0.03125 |
| sparse_clean | relative_l2 | vrba-m5 | -0.22439 | [-0.32713, -0.15273] | 0.03125 |
| sparse_clean | relative_l2 | vrba-m6 | -0.21344 | [-0.32406, -0.15757] | 0.03125 |
| sparse_clean | relative_l2 | vrba-m7 | -0.17495 | [-0.24497, -0.13279] | 0.03125 |
| sparse_noisy | relative_l2 | vrba-m5 | -0.19789 | [-0.30269, -0.17423] | 0.03125 |
| extreme | relative_l2 | vrba-m5 | -0.13299 | [-0.20818, -0.06938] | 0.03125 |
| extreme | relative_l2 | vrba-m6 | -0.13806 | [-0.20866, -0.11213] | 0.03125 |
| extreme | relative_l2 | vrba-m7 | -0.13349 | [-0.15551, -0.06411] | 0.03125 |

vRBA has the lowest median L2 in all four regimes, with 11 of 16 L2 contrasts passing Holm; no maximum-error contrast passes its separate correction. This targeted rerun removes the observation-loss mismatch in these cases.
Its protocol followed the V10 audit and remains exploratory. It does not
establish performance on unseen physical systems or a general robustness guarantee.

## 5. Discussion

The experiments separate three statements that are often conflated. First,
adaptive collocation can change what a loss controller observes. Second,
removing this change can alter gradients. Third, neither fact guarantees lower
solution error. M6 demonstrates that an independent reference set can change
the controller without producing a robust benefit. M7 demonstrates that exact
proposal correction can restore a target finite-population mean and improve a
matched control in data-poor Burgers regimes. VW demonstrates that an estimated
geometric correction can be equally or more effective, especially when its
bandwidth is favorable and global component weights remain fixed.

The poor behavior of VW-CA relative to VW in several cases suggests an
interaction between local volume weights and global component balancing. One
possible explanation is that squared local volume weights change the magnitude
and variance of the physics gradient, after which the global controller reacts
to a signal that is already strongly rescaled. This interpretation is an
inference, not yet a demonstrated mechanism. A factorial experiment varying
local correction, global controller and update frequency is needed.

The vRBA comparison sharpens the distinction between restoring a target
measure and deliberately changing the training objective. In this benchmark,
the tilted objective is much more effective in global L2 error than either
exact or KDE-based correction. Yet the Burgers maximum-error result shows that
this benefit is not uniform over the domain. A plausible interpretation is
that local attention sacrifices a narrow difficult region while improving a
larger portion of the solution; spatial maps and V09–V10 ablations now document this tradeoff, while its causal optimization mechanism remains unproven.

The practical conclusion is not that one correction should replace every
other. When the proposal probability is exactly available, M7 avoids density
estimation and has favorable asymptotic correction cost. When only a realized
nonuniform point cloud is available, volume weighting remains applicable. If
the objective is deliberately tilted toward high residuals rather than restored
to a uniform measure, a variational adaptive method such as vRBA may be more
appropriate.

## 6. Limitations

1. The VW implementation reproduces its core weighting mechanism on a common
   backbone, not the complete published architecture and Adam–L-BFGS schedule.
2. vRBA is implemented on the common backbone, but the complete official JAX
   architecture, hard constraints and long optimizer schedule have not been
   reproduced.
3. The original high-frequency Helmholtz case remains unsolved; the calibrated
   case answers a different, easier question and is reported separately.
4. Ten seeds provide useful paired evidence but limited power for small effects.
5. KDE bandwidth sensitivity was tested on two problems, not the full suite.
6. Timing conclusions are CPU-specific, and the KDE scaling claim still needs
   controlled multi-size and GPU measurements.
7. The PDE suite is synthetic. No conclusion currently transfers to tokamak
   plasma data or real-time instability control.
8. Local/global and potential ablations, spatial maps and doubled-step sensitivity are available. Common-loss noisy baseline reruns are also available. Equal-time comparisons and independent-machine replication remain open.
9. The public literature review is reproducible but not exhaustive across
   subscription databases.

## 7. Conclusion

Residual sampling and adaptive loss balancing form a feedback system whose
behavior depends on the measure used to estimate each loss component. A fixed
reference set alone does not provide general stabilization. Exact proposal
reweighting can reduce distribution-induced gradient discrepancies and improve
matched controls in sparse/noisy Burgers regimes, but it does not dominate KDE
volume weighting across PDEs or bandwidths. The common-backbone vRBA recipe shows strong historical relative-L2 performance, qualified by a noisy-data loss confound and substantial maximum-error and cost tradeoffs. The new common-loss ablations and doubled budgets identify conditional rather than universal benefits. Robust claims about adaptive PINNs
therefore require matched controls, several PDEs and seeds, multiple error
metrics, sensitivity analyses, and explicit separation between restoring a
measure and optimizing a deliberately tilted objective.

## Data, code and reproducibility statement

The PyTorch implementation stores resolved YAML configurations, software and
hardware metadata, metric trajectories, model checkpoints and final summaries
for every run. Campaign manifests regenerate paired tables and figures while
resuming only missing cells. The repository contains automated unit and smoke
tests for samplers, corrections, PDE residuals, reproducibility and reporting.
V09 supplies 200 ablation runs and V10 adds 560 verified runs, in addition to the historical baseline campaigns. The V10 numerical suite passed 55 tests. Raw campaign counts distinguish completed training, repeated profiling and reused historical evidence; they must not be summed as independent physical experiments.

## Core references

1. Raissi, M., Perdikaris, P. & Karniadakis, G. E. Physics-informed neural
   networks. *Journal of Computational Physics* 378, 686–707 (2019).
   https://doi.org/10.1016/j.jcp.2018.10.045
2. Wang, S., Teng, Y. & Perdikaris, P. Understanding and mitigating gradient
   flow pathologies in physics-informed neural networks. *SIAM Journal on
   Scientific Computing* 43, A3055–A3081 (2021).
   https://doi.org/10.1137/20M1318043
3. Nabian, M. A., Gladstone, R. J. & Meidani, H. Efficient training of
   physics-informed neural networks via importance sampling. *Computer-Aided
   Civil and Infrastructure Engineering* 36, 962–977 (2021).
   https://arxiv.org/abs/2104.12325
4. Wu, C., Zhu, M., Tan, Q., Kartha, Y. & Lu, L. A comprehensive study of
   non-adaptive and residual-based adaptive sampling for PINNs. *Computer
   Methods in Applied Mechanics and Engineering* 403, 115671 (2023).
   https://doi.org/10.1016/j.cma.2022.115671
5. Song, J., Cao, W., Liao, F. & Zhang, W. VW-PINNs: A volume weighting method
   for PDE residuals in physics-informed neural networks. *Acta Mechanica
   Sinica* 41, 324140 (2025).
   https://doi.org/10.1007/s10409-024-24140-x
6. Toscano, J. D. et al. A variational framework for residual-based adaptivity
   in neural PDE solvers and operator learning. *npj Artificial Intelligence*
   2, 32 (2026). https://doi.org/10.1038/s44387-026-00084-4

7. Burkardt, J. burgers_exact: integral solution and Hermite quadrature for the sine Burgers benchmark. https://people.sc.fsu.edu/~jburkardt/f77_src/burgers_exact/burgers_exact.html (accessed 5 September 2026).
