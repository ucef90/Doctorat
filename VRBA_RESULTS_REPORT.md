# Rapport scientifique vRBA — baseline common-backbone

Date : 5 septembre 2026

## Décision principale

L'implémentation PyTorch common-backbone de vRBA est fonctionnelle,
reproductible et produit un signal fort en erreur relative L2. Elle ne doit
cependant pas être présentée comme une réplication exacte du protocole JAX
publié, ni comme une méthode dominante sur tous les critères.

Dans notre protocole, vRBA réduit l'erreur L2 face à M5, M6, M7 et VW sur les
quatre EDP et les quatre régimes Burgers à données difficiles. En revanche, sur
Burgers long, son erreur maximale est significativement plus élevée que celle
de M5 et M6. Son temps d'entraînement est également plus élevé, avec un surcoût
qui dépend fortement de l'EDP.

## 1. Protocole et traçabilité

- protocole gelé avant les runs dans `VRBA_BASELINE_PREREGISTRATION.md` ;
- potentiel principal : exponentiel ;
- multiplicateurs locaux persistants sur physique, conditions et données ;
- auto-équilibrage global avec poids physique fixé à 1 ;
- même MLP, précision, optimiseur, cardinalités, germes et grilles de test que
  les méthodes comparées ;
- Python 3.12.13, PyTorch 2.14.0 et NumPy 2.3.5 ;
- 18/18 runs pilotes, 200/200 cellules multi-EDP et 200/200 cellules sous
  données difficiles ;
- 83 résumés vRBA au total, tous finis ;
- 32/32 tests automatisés réussis, dont une reproduction bit à bit sur un même
  germe.

Le dépôt complet contient désormais 973 résumés d'entraînement réussis et
aucun échec. Ce total inclut pilotes, criblages, ablations et campagnes
confirmatoires ; il ne correspond pas à 973 répétitions confirmatoires.

## 2. Résultats confirmatoires sur quatre EDP

Une différence négative favorise vRBA. Les intervalles sont des IC bootstrap
appariés à 95 %.

| EDP | L2 vRBA | L2 M7 | L2 VW | Δ vRBA−M7 [IC 95 %] | Δ vRBA−VW [IC 95 %] |
|---|---:|---:|---:|---:|---:|
| Burgers long | 0,2507 | 0,4410 | 0,4350 | −0,1770 [−0,2339 ; −0,0114] | −0,1236 [−0,2566 ; −0,0283] |
| Allen–Cahn | 0,0401 | 0,1081 | 0,0912 | −0,0648 [−0,0903 ; −0,0509] | −0,0617 [−0,1269 ; −0,0267] |
| Helmholtz calibrée | 0,0388 | 0,1006 | 0,1096 | −0,0611 [−0,0690 ; −0,0496] | −0,0844 [−0,0891 ; −0,0608] |
| Ondes | 0,1745 | 0,3057 | 0,2825 | −0,1322 [−0,2163 ; −0,1190] | −0,1061 [−0,1502 ; −0,0836] |

Sur Allen–Cahn, Helmholtz et les ondes, vRBA gagne les dix germes contre M7 et
VW, avec un test des signes `p=0,00195`. Sur Burgers, elle gagne 8/10 germes
contre M7 (`p=0,109`) et 9/10 contre VW (`p=0,0215`). Le signal Burgers est donc
plus variable, même si les deux intervalles bootstrap restent sous zéro.

## 3. Données rares, bruitées et incomplètes

| Régime Burgers | L2 vRBA | L2 M7 | L2 VW | Δ vRBA−M7 [IC 95 %] | Δ vRBA−VW [IC 95 %] |
|---|---:|---:|---:|---:|---:|
| 13 observations propres | 0,3693 | 0,5281 | 0,5066 | −0,1883 [−0,2607 ; −0,1158] | −0,1393 [−0,2442 ; −0,0980] |
| 13 observations bruitées | 0,3562 | 0,5527 | 0,5229 | −0,1667 [−0,2670 ; −0,1332] | −0,1583 [−0,2509 ; −0,1243] |
| Une observation, bruit fort | 0,4469 | 0,5776 | 0,5457 | −0,1290 [−0,1772 ; −0,0015] | −0,1126 [−0,1260 ; −0,0116] |
| Bloc de capteurs manquant | 0,3322 | 0,5287 | 0,4924 | −0,1762 [−0,2152 ; −0,1402] | −0,1471 [−0,1681 ; −0,1003] |

Dans le régime extrême, vRBA gagne 8/10 germes et le test des signes reste
`p=0,109`. Ce résultat est encourageant mais moins fort que les trois autres
régimes, où vRBA gagne 9/10 ou 10/10 selon le contraste.

## 4. Résultat contradictoire sur l'erreur maximale

Sur Burgers long, les médianes d'erreur maximale sont :

| Méthode | Erreur maximale médiane |
|---|---:|
| M5 | 1,3429 |
| M6 | 1,2993 |
| M7 | 1,4972 |
| VW | 1,5836 |
| vRBA | 1,7209 |

La différence vRBA−M5 vaut `+0,3336` avec IC 95 %
`[+0,0265 ; +0,5694]`, et vRBA−M6 vaut `+0,4011`
`[+0,2067 ; +0,5759]`. vRBA est défavorable dans 9/10 germes face à chacun de
ces deux contrôles. Les contrastes face à M7 et VW sont inconclusifs.

Ainsi, la baisse de L2 ne signifie pas une meilleure approximation du pic
d'erreur près des zones difficiles. Cette divergence entre métriques doit être
conservée dans l'article.

L'analyse spatiale des dix modèles localise ce compromis. Le quantile 95 % de
l'erreur absolue, calculé sur la grille puis résumé par sa médiane entre germes,
vaut `0,1027` pour vRBA contre `0,6698` pour M5 et `0,6907` pour M6. À 99 %,
vRBA reste meilleure (`0,8588` contre `1,1470` et `1,0516`). Son maximum plus
élevé provient donc d'une zone extrêmement étroite autour du choc, culminant
sur la carte médiane vers `t=0,975`, `x=−0,025`. Les cartes et profils sont dans
`outputs/reports/article1_vrba_spatial/`.

## 5. Attention locale et stabilité numérique

- fraction ESS finale observée : de 0,785 à 0,990 ;
- multiplicateurs locaux observés : de 1,174 à 5,412 ;
- aucune valeur non finie ;
- cardinalités de collocation constantes ;
- budget d'optimisation identique à méthode et configuration égales ;
- les 32 tests unitaires, d'intégration et de reproductibilité passent.

L'attention est donc réellement non uniforme sans effondrement de l'ESS dans
le domaine testé.

## 6. Coût observé

Face à M5, le surcoût médian vRBA est de `+13,5 %` sur Burgers long,
`+26,9 %` sur Allen–Cahn, `+81,8 %` sur Helmholtz et `+10,4 %` sur les ondes.
Face à M7 et VW, il peut approcher un facteur deux. Ce coût vient principalement
du calcul des normes de gradient pour l'auto-équilibrage global à chaque étape.

Ces temps ont été obtenus séquentiellement sur la même plateforme et le même
environnement, mais les baselines et vRBA n'ont pas toutes été exécutées dans
la même session temporelle. Une campagne de profilage intercalée CPU/GPU reste
nécessaire avant toute revendication forte sur l'efficacité.

## 7. Ce que les résultats permettent d'affirmer

1. Le baseline vRBA common-backbone est techniquement reproductible.
2. Son attention locale devient non uniforme sans instabilité numérique.
3. Il améliore fortement l'erreur L2 dans le domaine synthétique testé.
4. Le signal persiste sous observations rares, bruitées ou manquantes.
5. L'objectif adaptativement incliné peut être plus efficace que la restauration
   explicite de la mesure uniforme pour l'erreur globale.

## 8. Ce qu'ils ne permettent pas d'affirmer

1. Il ne s'agit pas d'une réplication exacte des expériences officielles JAX.
2. vRBA ne domine pas l'erreur maximale de Burgers.
3. Son surcoût n'est pas toujours faible.
4. Les résultats ne couvrent que quatre EDP synthétiques et dix germes.
5. Ils ne démontrent rien encore sur des données de tokamak.
6. vRBA est un travail antérieur de Toscano et al., pas une innovation de ce
   projet ; notre apport est la comparaison contrôlée et l'analyse des
   interactions avec M5, M6, M7 et VW.

## 9. Suite scientifique requise

1. exécuter une sensibilité exploratoire du potentiel quadratique contre le
   potentiel exponentiel gelé ;
2. ablater attention locale et auto-équilibrage global ;
3. effectuer un profilage CPU/GPU intercalé ;
4. reproduire séparément le protocole officiel JAX avec ses architectures,
   contraintes dures et optimisation longue ;
5. seulement ensuite transférer la méthode au premier cas plasma/tokamak.

## Sources primaires

- Toscano et al., *A Variational Framework for Residual-Based Adaptivity in
  Neural PDE Solvers and Operator Learning*, npj Artificial Intelligence 2, 32
  (2026), DOI `10.1038/s44387-026-00084-4`.
- Dépôt officiel `jdtoscano94/NABLA-SciML`, dossier vRBA.
