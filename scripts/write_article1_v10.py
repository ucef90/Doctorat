"""Generate the V10 evidence report and an updated manuscript from verified tables."""
from pathlib import Path
import csv
import json
import re

ROOT=Path(__file__).resolve().parents[1]
VARIANTS=['neither','global_only','local_only','full_exp','full_quad']


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def table(data,metric='relative_l2',variants=None):
    variants=variants or VARIANTS
    labels='Neither | Global only | Local only | Full exp. | Full quad.' if variants==VARIANTS else 'M5 | M6 | M7 | VW | vRBA'
    out=['| Case | '+labels+' |',
         '|---|---:|---:|---:|---:|---:|']
    for problem in dict.fromkeys(r['problem'] for r in data):
        ix={r['variant']:r for r in data if r['problem']==problem}
        out.append('| '+problem+' | '+' | '.join(f"{float(ix[v][metric]):.5f}" for v in variants)+' |')
    return '\n'.join(out)


def significant(data):
    out=['| Case | Metric | Contrast | Paired median difference | Marginal 95% CI | Holm p |',
         '|---|---|---|---:|---|---:|']
    for r in data:
        if float(r['p_holm_16'])<.05:
            out.append(f"| {r['problem']} | {r['metric']} | {r['contrast']} | {float(r['median_difference']):+.5f} | "
                       f"[{float(r['ci95_low']):+.5f}, {float(r['ci95_high']):+.5f}] | {float(r['p_holm_16']):.5f} |")
    return '\n'.join(out)


def main():
    paths={suite:ROOT/'outputs'/folder for suite,folder in
           [('robustness','robustness_v10_verified'),('budget','budget_v10_analysis')]}
    data={};stats={}
    for suite,path in paths.items():
        valid=json.loads((path/'validation.json').read_text())
        if valid['evaluated']!=200 or valid['failed'] or not valid['all_initial_hashes_match']:
            raise RuntimeError('Incomplete or unverified evidence')
        data[suite]=rows(path/'method_summary.csv');stats[suite]=rows(path/'paired_statistics.csv')
    report='''# Article 1 — bilan scientifique V10

**Youssef EL MOUTEE · 5 septembre 2026 · version de recherche**

## Ce qui a été réalisé

Le dépôt de départ est `ucef90/Doctorat`, branche main, commit V09
`0142311a08c9cd72d05494b6f24dd8949ebe6cd6`. L'historique V06–V09 est conservé.
Cette extension ajoute 400 entraînements terminés sans échec : 200 pour les
données difficiles et 200 pour un nombre de pas doublé. Les 400 modèles finaux
ont été rechargés pour recalculer leurs scores, et 80 blocs problème/régime-germe
ont été vérifiés par empreintes des paramètres et des données initiales.
La suite automatisée a passé 55 tests dans cette session.

## 1. Référence Burgers et contrôle des scores

Une solution Cole–Hopf indépendante a été ajoutée. Les ordres de quadrature
128 et 256 concordent à environ 9,11 × 10⁻¹⁵ sur la grille examinée ; un autre
algorithme de quadrature confirme 20 points à 4,44 × 10⁻¹⁶.
L'ancienne référence Rusanov à 257 points diffère de 3,41 % en L2 relative
et d'au plus 0,28578 localement. À 1025 points, ces écarts baissent à 0,73 %
et 0,06969. Il ne faut donc pas considérer les anciens maxima comme exacts.

Les 50 modèles Burgers V09 ont été réévalués sur une grille fine avec Cole–Hopf.
Le classement des ablations demeure incertain après correction de multiplicité.
Le cache de référence a également été corrigé pour tenir compte du pas de temps.
La validation détaillée est dans `BURGERS_REFERENCE_VALIDATION_V10.md`.

## 2. Données rares, bruitées ou manquantes

Les cinq bras utilisent maintenant la même perte MSE pour les observations.
Cette décision corrige un facteur de confusion des anciennes recettes : avec
une attention locale, vRBA utilisait une perte quadratique pondérée, tandis que
plusieurs comparateurs utilisaient Huber. Les observations et les évaluations
de la nouvelle campagne Burgers reposent sur Cole–Hopf.

Les lignes ci-dessous sont des médianes entre dix germes ; L2 n'est pas un
pourcentage de bonne classification. Les labels désignent respectivement
absence d'adaptation, global seul, local seul, complet exponentiel et complet
quadratique.

'''+table(data['robustness'])+'''

Contrastes passant Holm à 5 %, sur 16 tests L2 et une famille séparée de
16 tests de maximum :

'''+significant(stats['robustness'])+'''

Le bénéfice du complet face au global seul est établi pour L2 dans le cas
du bloc manquant. Dans le régime extrême, l'exponentiel améliore le maximum
face au quadratique. Les autres contrastes planifiés ne franchissent pas
ce seuil corrigé. Cette absence de preuve n'établit aucune équivalence.

## 3. Sensibilité au nombre de pas

Les budgets sont doublés : Burgers 5000 pas, Allen–Cahn 1200, Helmholtz
3000, ondes 1200. Aucun autre hyperparamètre d'entraînement n'est ajusté
selon les scores. La comparaison historique à budget initial emploie les
mêmes tenseurs de départ et la même référence d'évaluation, vérifiés par script.

'''+table(data['budget'])+'''

Contrastes passant Holm dans cette campagne :

'''+significant(stats['budget'])+'''

Les résultats individuels à budget initial et doublé sont fournis dans
`outputs/budget_v10_analysis/budget_changes.csv`. Doubler les pas ne signifie
pas égaliser le temps de calcul entre méthodes. Les temps recueillis sous
parallélisme décrivent le débit de cette campagne, pas une efficacité isolée.

## 4. Ce que devient le premier article

Le titre de travail est : **Adaptive PINNs under Competing Training Measures:
A Controlled Study of Fixed References, Exact Reweighting, KDE Volume
Weighting, and Variational Residual Attention**.

La contribution proposée est une étude contrôlée des interactions et limites,
avec résultats positifs, nuls et défavorables. La supériorité générale de M6
n'est pas démontrée. vRBA reste attribuée à ses auteurs ; ce projet ne revendique
pas son invention. Les campagnes V09–V10 sont exploratoires après connaissance
des résultats antérieurs, même si leurs paramètres ont été figés avant calcul.

Le manuscrit anglais V10 intègre les ablations V09, la validation indépendante,
les campagnes de robustesse et de budget, ainsi que la réserve sur Huber/MSE.
Les résultats historiques restent identifiables et les métriques ne sont pas
mélangées entre références. Le domaine étudié reste synthétique ; aucun résultat
ne valide encore une prédiction ou un contrôle de plasma de tokamak.

## 5. Ce qui reste avant soumission

| Travail | État et condition |
|---|---|
| Référence Burgers indépendante | Réalisé et testé sur le domaine de cette étude |
| Ablations sous données difficiles | 200/200 réalisées et réévaluées |
| Sensibilité au nombre de pas | 200/200 réalisées et réévaluées |
| Tableaux et manuscrit V10 | Produits à partir des sorties vérifiées |
| Comparaison M5/M6/M7/VW sous bruit avec perte commune | À refaire si l'article conserve une revendication de supériorité bruitée face à ces baselines ; les nouvelles ablations seules ne la prouvent pas |
| Budget de temps égal | À réaliser avant toute revendication d'efficacité en temps ; le budget de pas doublé ne le remplace pas |
| Vérification sur machine indépendante | À réaliser pour consolider la reproductibilité entre machines |
| Relecture scientifique externe | À organiser avec l'encadrement et les coauteurs |
| Revue, auteurs, affiliations et déclarations | À fixer avant mise en forme et soumission |

Une réplication exacte du protocole JAX officiel et un transfert au plasma
sont des extensions distinctes ; ils ne sont pas présentés comme accomplis.
Une publication reste soumise à l'appréciation des évaluateurs scientifiques.

## 6. Références et reproduction

La formulation vRBA et son attribution ont été revérifiées dans
[Toscano et al. (2026)](https://www.nature.com/articles/s44387-026-00084-4).
La référence intégrale de Burgers est documentée par
[Burkardt, burgers_exact](https://people.sc.fsu.edu/~jburkardt/f77_src/burgers_exact/burgers_exact.html).
La bibliographie principale du manuscrit conserve les sources PINN, gradient
balancing, importance sampling, RAD et VW avec leurs liens primaires.

Les nouvelles campagnes sont archivées avec leurs manifestes, configurations,
trajectoires, environnements et modèles finaux. Les commandes d'extraction et
de reproduction sont dans `START_HERE_V10.md`. Les dossiers d'analyse contiennent
les scores par germe, audits d'appariement, IC marginaux, tests des signes,
corrections Holm et figures exportables. Les analyses ne sélectionnent aucun
germe favorable. Les différences appariées sont calculées avant agrégation.
'''
    common=ROOT/'outputs/common_loss_v10_analysis'
    valid=json.loads((common/'validation.json').read_text())
    if valid['evaluated_new']!=160 or valid['evaluated_reused']!=40 or valid['failed'] or not valid['all_initial_hashes_match']:
        raise RuntimeError('Common-loss comparison not verified')
    common_data=rows(common/'method_summary.csv');common_stats=rows(common/'paired_statistics.csv')
    common_table=table(common_data,variants=['m5','m6','m7','vw','vrba'])
    common_sig=significant(common_stats)
    report=report.replace('400 entraînements terminés sans échec : 200 pour les\ndonnées difficiles et 200 pour un nombre de pas doublé. Les 400 modèles finaux\nont été rechargés pour recalculer leurs scores, et 80 blocs problème/régime-germe\nont été vérifiés par empreintes des paramètres et des données initiales.',
        '560 entraînements terminés sans échec : 200 pour les données difficiles, 200 pour un nombre de pas doublé et 160 pour les baselines sous perte commune. Les 560 modèles finaux ont été rechargés pour recalculer leurs scores. Les paramètres et données de départ sont vérifiés par empreintes ; les 40 modèles vRBA réutilisés dans la comparaison des baselines ne sont pas comptés deux fois.')
    common_text='''### Comparaisons corrigées avec M5, M6, M7 et VW

160 nouveaux entraînements emploient exactement les configurations de la
campagne de robustesse, avec MSE et cibles Cole–Hopf. Les 40 modèles full_exp
de cette campagne sont réutilisés comme vRBA ; il s'agit de 200 cellules
comparées, dont seulement 160 entraînements supplémentaires.

'''+common_table+'\n\nContrastes passant Holm dans cette comparaison complémentaire :\n\n'+common_sig+'''

Tous les autres contrastes, ainsi que les erreurs maximales, sont conservés
dans `outputs/common_loss_v10_analysis/paired_statistics.csv`. Cette nouvelle
comparaison traite le facteur de confusion Huber/MSE dans les cas testés ;
elle ne transforme pas les résultats antérieurs en confirmations indépendantes.

'''
    report=report.replace('## 3. Sensibilité au nombre de pas',common_text+'## 3. Sensibilité au nombre de pas')
    report=report.replace('| Comparaison M5/M6/M7/VW sous bruit avec perte commune | À refaire si l\'article conserve une revendication de supériorité bruitée face à ces baselines ; les nouvelles ablations seules ne la prouvent pas |',
        '| Comparaison M5/M6/M7/VW sous bruit avec perte commune | 160 nouveaux entraînements et 40 comparateurs vRBA réutilisés, appariement et scores vérifiés |')
    report=report.replace('Les résultats individuels à budget initial et doublé sont fournis dans',
        "Sur les ondes, le complet reste favorable au global seul pour L2 et le maximum. L'avantage quadratique sur L2 observé à 600 pas en V09 n'est plus établi après Holm à 1200 pas. Pour Helmholtz, le complet exponentiel atteint une médiane L2 de 0,00523, mais les contrastes L2 planifiés ne passent pas Holm. L'interaction positive sur le maximum est un contraste additif ; elle ne signifie pas que le modèle complet est le moins précis.\n\nLes résultats individuels à budget initial et doublé sont fournis dans")
    report=report.replace('Tous les autres contrastes, ainsi que les erreurs maximales, sont conservés',
        'vRBA obtient la plus faible médiane L2 dans les quatre régimes de cette comparaison. Onze contrastes L2 sur seize passent Holm ; aucun contraste de maximum ne passe la correction. Ce résultat étaye un bénéfice global dans les cas testés, sans établir une domination sur les erreurs extrêmes.\n\nTous les autres contrastes, ainsi que les erreurs maximales, sont conservés')
    (ROOT/'ARTICLE1_STATUS_V10.md').write_text(report)
    old=(ROOT/'ARTICLE1_MANUSCRIPT_DRAFT.md').read_text()
    old=old.replace('# Manuscript draft — Article 1',
        '# Manuscript V10 — Article 1\n\nResearch draft, 5 September 2026. Historical comparisons and the V09–V10 exploratory extensions are explicitly separated. Not submitted or peer reviewed.')
    old=old.replace('vRBA obtains the lowest median relative L2 error on all four PDEs and all four\ndifficult-data regimes.',
        'The historical vRBA recipe has the lowest median relative L2 error in that benchmark. Its difficult-data comparisons used different observation-loss recipes and therefore do not isolate an attention effect. The V10 extension removes this confound in the local/global ablations.')
    old=old.replace('vRBA obtient la plus faible erreur L2 sur quatre EDP et\nquatre régimes de données rares ou bruitées.',
        'Le gain L2 historique de vRBA doit être interprété en tenant compte des recettes de perte différentes sous bruit. La V10 utilise une perte commune pour ses nouvelles ablations.')
    old=old.replace('vRBA dominates relative L2 error in the tested\nsuite, but not maximum error or cost.',
        'vRBA performs favorably in historical relative-L2 comparisons, but a common-loss audit qualifies the noisy-data claim; maximum error and cost do not show universal dominance.')
    old=old.replace('a\npaired causal design','a\npaired controlled design')
    old=old.replace('Confirmatory comparisons use ten paired seeds',
        'The historical ten-seed comparisons and the exploratory V09–V10 campaigns use ten paired seeds')
    note='''
### 3.5 V09–V10 extensions and common-loss audit

V09 consists of 200 runs: four PDE configurations, five local/global/potential
variants and ten seeds. V10 adds 200 Burgers observation-regime runs and 200
doubled-step runs. Each suite freezes its manifest before training but follows
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
all 400 V10 checkpoints are re-evaluated independently, including a denser grid.

'''
    old=old.replace('## 4. Results',note+'## 4. Results\n\nSections 4.1–4.6 report historical configurations and references. New V09–V10 evidence follows in Sections 4.7–4.10. Historical noisy-data rankings are recipe comparisons subject to the loss confound described in Section 3.5.')
    new='''
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

'''+table(data['robustness'])+'''

After correction, full_exp improves L2 over global_only for the missing-block
case (paired median difference -0.06999, marginal 95% CI [-0.09386,-0.03466],
Holm p=0.03125). For extreme data, full_exp improves the maximum error over
full_quad (difference -0.06696, CI [-0.12910,-0.00587], Holm p=0.03125).
Other planned contrasts do not pass Holm. These ablations do not retest the
historical M5/M6/M7/VW comparisons with a common observation loss.

### 4.10 Doubled optimization budgets

The 200 additional runs use 5000 Burgers, 1200 Allen–Cahn, 3000 Helmholtz and
1200 wave steps. The following median relative L2 values come from independent
checkpoint evaluations. Initial tensors match both within each five-arm block
and against the historical V09 counterparts. No model selection is based on
the evaluation scores.

'''+table(data['budget'])+'''

Planned contrasts passing Holm in the doubled-step suite are listed below;
the complete table, including null and adverse contrasts, accompanies the code.

'''+significant(stats['budget'])+'''

The doubled-step comparison measures sensitivity to optimization duration.
It is not an equal-compute or equal-time experiment, and historical and V10
wall times must not be pooled as a controlled timing comparison.

'''
    old=old.replace('## 5. Discussion',new+'## 5. Discussion')
    old=old.replace('this remains an inference until spatial error\nmaps and local/global ablations are completed.',
        'spatial maps and V09–V10 ablations now document this tradeoff, while its causal optimization mechanism remains unproven.')
    old=old.replace('8. The vRBA potential and its local/global components have not yet been\n   ablated; the conflict between relative L2 and maximum error needs spatial\n   analysis.',
        '8. Local/global and potential ablations, spatial maps and doubled-step sensitivity are available. Equal-time comparisons, independent-machine replication, and common-loss reruns of the historical noisy M5/M6/M7/VW comparisons remain open.')
    old=old.replace('The current archive contains 973 successful run summaries and 32 passing tests;\ncampaign-level counts distinguish confirmatory cells from pilots and ablations.',
        'V09 supplies 200 ablation runs and V10 adds 400 verified runs, in addition to the historical baseline campaigns. The V10 numerical suite passed 55 tests. Raw campaign counts distinguish completed training, repeated profiling and reused historical evidence; they must not be summed as independent physical experiments.')
    old=old.replace('A common-backbone vRBA baseline is\nsubstantially better in relative L2 throughout this benchmark, yet worse in\nmaximum Burgers error and more expensive.',
        'The common-backbone vRBA recipe shows strong historical relative-L2 performance, qualified by a noisy-data loss confound and substantial maximum-error and cost tradeoffs. The new common-loss ablations and doubled budgets identify conditional rather than universal benefits.')
    common_section='''### 4.11 Re-running the historical baselines with a common observation loss

An additional 160 runs cover M5, M6, M7 and VW across the same four observation
regimes and ten seeds, using the exact V10 MSE/Cole–Hopf configurations.
Forty full_exp checkpoints from Section 4.9 are reused as vRBA comparators;
they are not new or independent training runs. Initial parameter and observation
tensors match across all five compared methods. The table gives median L2.

'''+common_table+'''

All newly trained checkpoints have been independently re-evaluated. The
following contrasts pass Holm in the separately declared family of 16 per
metric. All contrasts, including null and unfavorable effects, are retained
in the accompanying paired_statistics.csv.

'''+common_sig+'''

This targeted rerun removes the observation-loss mismatch in these cases.
Its protocol followed the V10 audit and remains exploratory. It does not
establish performance on unseen physical systems or a general robustness guarantee.

'''
    old=old.replace('## 5. Discussion',common_section+'## 5. Discussion')
    old=old.replace('These ablations do not retest the\nhistorical M5/M6/M7/VW comparisons with a common observation loss.',
        'Section 4.11 separately retests the historical M5/M6/M7/VW comparisons with a common observation loss.')
    old=old.replace('Equal-time comparisons, independent-machine replication, and common-loss reruns of the historical noisy M5/M6/M7/VW comparisons remain open.',
        'Common-loss noisy baseline reruns are also available. Equal-time comparisons and independent-machine replication remain open.')
    old=old.replace('V10 adds 400 verified runs','V10 adds 560 verified runs')
    old=old.replace('V10 adds 200 Burgers observation-regime runs and 200\ndoubled-step runs.',
        'V10 adds 200 Burgers observation-regime runs, 200 doubled-step runs and 160 common-loss baseline runs. The latter reuse 40 existing V10 vRBA checkpoints for comparison.')
    abstract='''Physics-informed neural networks often combine adaptive loss balancing and
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
interpreting adaptive PINN comparisons.'''
    french='''Nous étudions les interactions entre pondération des pertes et collocation
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
supériorité universelle ni de validation sur des données de tokamak.'''
    old=re.sub(r'## Abstract\n.*?\n## Résumé français',
        '## Abstract\n\n'+abstract+'\n\n## Résumé français',old,flags=re.S)
    old=re.sub(r'## Résumé français\n.*?\n\*\*Keywords:',
        '## Résumé français\n\n'+french+'\n\n**Keywords:',old,flags=re.S)
    old=old.replace('all 400 V10 checkpoints are re-evaluated independently, including a denser grid.',
        'the 400 factorial/budget V10 checkpoints are re-evaluated independently, including a denser grid; the 160 additional baseline checkpoints are independently checked on the original scoring grid.')
    old=old.replace('The doubled-step comparison measures sensitivity to optimization duration.',
        'The quadratic-potential L2 advantage established for the V09 wave configuration does not pass Holm at the doubled horizon. Full_exp still improves both L2 and maximum error over global_only for waves. A positive Helmholtz maximum-error interaction reflects the additive contrast and does not imply that full_exp is the least accurate model.\n\nThe doubled-step comparison measures sensitivity to optimization duration.')
    old=old.replace('This targeted rerun removes the observation-loss mismatch in these cases.',
        'vRBA has the lowest median L2 in all four regimes, with 11 of 16 L2 contrasts passing Holm; no maximum-error contrast passes its separate correction. This targeted rerun removes the observation-loss mismatch in these cases.')
    old += '\n7. Burkardt, J. burgers_exact: integral solution and Hermite quadrature for the sine Burgers benchmark. https://people.sc.fsu.edu/~jburkardt/f77_src/burgers_exact/burgers_exact.html (accessed 5 September 2026).\n'
    (ROOT/'ARTICLE1_MANUSCRIPT_V10.md').write_text(old)
    print('Generated ARTICLE1_STATUS_V10.md and ARTICLE1_MANUSCRIPT_V10.md')


if __name__=='__main__':main()
