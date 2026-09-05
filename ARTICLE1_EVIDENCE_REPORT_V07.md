# Article 1 — état consolidé des preuves, version 0.7

Date : 5 septembre 2026

## Décision scientifique

Le résultat central reste une étude comparative des mesures d'entraînement,
et non la validation d'une méthode maison universellement supérieure.

La nouvelle campagne ajoute vRBA, un baseline variationnel moderne. Sur le
backbone commun, vRBA obtient la meilleure erreur relative L2 médiane sur les
quatre EDP et les quatre régimes de données difficiles. Ce résultat renforce la
valeur du benchmark mais affaiblit toute revendication de supériorité de M6 ou
M7. Il révèle aussi un compromis important : sur Burgers long, vRBA réduit L2
tout en augmentant l'erreur maximale face à M5 et M6.

Le dépôt contient **973 entraînements réussis**, aucun échec enregistré et
**32 tests automatisés réussis**. Les 973 cellules incluent des pilotes,
criblages et ablations ; seules les campagnes explicitement marquées
confirmatoires doivent être interprétées comme telles.

## 1. Méthodes comparées

| Méthode | Mesure / adaptation locale | Poids globaux |
|---|---|---|
| M0 | uniforme | fixes |
| M1 | uniforme | adaptatifs |
| M3 | collocation résiduelle | fixes |
| M5 | collocation résiduelle | adaptatifs sur le même lot |
| M6 / ReCoA | collocation résiduelle | adaptatifs sur audit fixe |
| M7U | proposition résiduelle, non corrigée | adaptatifs |
| M7 | correction exacte Hansen–Hurwitz | adaptatifs |
| VW | volume inverse KDE au carré | fixes |
| VW-CA | volume inverse KDE au carré | adaptatifs |
| vRBA | multiplicateurs variationnels locaux exponentiels | auto-équilibrage, physique fixée à 1 |

vRBA et VW sont des implémentations **common-backbone** de mécanismes publiés,
pas des réplications exactes de leurs protocoles logiciels complets.

## 2. Hypothèse initiale M5–M6

Le couplage entre concentration des points et décalage du gradient est
mesurable, mais M5 ne présente pas des oscillations reproductibles suffisantes
pour que M6 apporte une stabilisation générale. Sur Burgers long, la différence
M6−M5 en L2 vaut `−0,0291`, IC 95 % `[−0,1208 ; +0,1678]`, à cardinalité et
budget appariés. La revendication initiale forte sur M6 est donc réfutée.

## 3. Correction exacte M7 et pondération volumique VW

M7 réduit le décalage du gradient physique face à son contrôle M7U sur Burgers
et améliore M7U dans quatre régimes de données difficiles. Elle ne domine pas
VW : VW est meilleure sur les ondes et à certains réglages KDE, tandis que M7
est meilleure sur Helmholtz calibrée. La largeur de bande KDE peut changer le
classement.

## 4. Baseline vRBA sur quatre EDP

| EDP | M5 | M6 | M7 | VW | vRBA |
|---|---:|---:|---:|---:|---:|
| Burgers long | 0,5007 | 0,4706 | 0,4410 | 0,4350 | **0,2507** |
| Allen–Cahn | 0,0963 | 0,0980 | 0,1081 | 0,0912 | **0,0401** |
| Helmholtz calibrée | 0,1041 | 0,1043 | 0,1006 | 0,1096 | **0,0388** |
| Ondes | 0,3088 | 0,3093 | 0,3057 | 0,2825 | **0,1745** |

Tous les contrastes vRBA contre M5, M6, M7 et VW ont un IC bootstrap apparié
à 95 % sous zéro. Sur Allen–Cahn, Helmholtz et les ondes, vRBA gagne 10/10
germes contre chacune de ces méthodes. Burgers est plus hétérogène : vRBA gagne
8/10 face à M7 et 9/10 face aux autres principaux contrôles.

## 5. Données rares et bruitées

| Régime Burgers | M5 | M6 | M7 | VW | vRBA |
|---|---:|---:|---:|---:|---:|
| 13 observations propres | 0,5736 | 0,5629 | 0,5281 | 0,5066 | **0,3693** |
| 13 observations bruitées | 0,5904 | 0,5871 | 0,5527 | 0,5229 | **0,3562** |
| Une observation, bruit fort | 0,5997 | 0,5973 | 0,5776 | 0,5457 | **0,4469** |
| Bloc de capteurs manquant | 0,5571 | 0,5542 | 0,5287 | 0,4924 | **0,3322** |

Les intervalles bootstrap vRBA contre les quatre baselines sont sous zéro dans
les quatre régimes. Dans le cas extrême, le test des signes reste toutefois
non concluant (`8/10`, `p=0,109`) : ce point doit accompagner l'intervalle
favorable.

## 6. Compromis L2–erreur maximale

Sur Burgers long, vRBA a une erreur maximale médiane de `1,7209`, contre
`1,3429` pour M5 et `1,2993` pour M6. Les différences vRBA−M5 et vRBA−M6 sont
respectivement `+0,3336 [0,0265 ; 0,5694]` et
`+0,4011 [0,2067 ; 0,5759]`.

La performance L2 de vRBA ne doit donc pas être interprétée comme une
supériorité uniforme dans l'espace. L'analyse des dix champs d'erreur montre
cependant que vRBA réduit le quantile spatial 95 % médian à `0,1027`, contre
`0,6698` pour M5 et `0,6907` pour M6. Le pic défavorable est très localisé près
du choc, vers `t=0,975`, `x=−0,025` sur la carte médiane. Cette localisation
explique comment L2 et le maximum peuvent évoluer en sens opposé.

## 7. Coût et stabilité

L'ESS finale de l'attention vRBA reste comprise entre `0,785` et `0,990` dans
les 83 runs vRBA, sans valeur non finie. Le surcoût médian face à M5 varie de
`+10,4 %` à `+81,8 %` selon l'EDP. Burgers long respecte un ordre de grandeur
raisonnable (`+13,5 %`), mais Helmholtz ne permet pas de revendiquer un coût
faible général.

Les anciennes baselines et les nouveaux runs partagent Python 3.12.13,
PyTorch 2.14.0, NumPy 2.3.5 et la même plateforme CPU. Un test de non-régression
sur Allen–Cahn reproduit exactement M5 et M6 ; les écarts M7/VW sont au plus de
l'ordre de `2,22×10⁻¹⁶`.

## 8. Réponse aux huit exigences scientifiques

| Exigence | État | Conclusion |
|---|---|---|
| Biais/oscillations de M5 | traité | couplage mesurable, oscillation générale non démontrée |
| Réduction par M6 | traité | pas de bénéfice général |
| Pas un simple ajout de points | traité | cardinalités et budgets appariés |
| Dix germes, plusieurs EDP | traité | 10 germes et 4 EDP |
| Données rares/bruitées | traité | 4 régimes, signal vRBA persistant en L2 |
| Surcoût raisonnable | partiel | raisonnable sur Burgers/ondes face à M5, élevé ailleurs |
| Ablation référence fixe → lot adaptatif | traité | M6 contre M5 supprime le découplage sans révéler le bénéfice annoncé |
| Différence avec 2025–2026 | traité | revue, matrice, VW et vRBA common-backbone |

## 9. Revendications permises

1. La mesure observée par le contrôleur change avec la collocation adaptative.
2. Une référence fixe seule ne stabilise pas généralement le système testé.
3. La correction exacte et la correction KDE ont des domaines favorables
   différents.
4. L'objectif variationnel incliné de vRBA est très compétitif en erreur L2 sur
   ce benchmark commun.
5. Le classement dépend de la métrique : L2 et maximum peuvent mener à des
   conclusions opposées.

## 10. Revendications interdites

1. M6, M7 ou vRBA est universellement supérieure.
2. vRBA, importance weighting ou volume weighting est une invention du projet.
3. L'implémentation common-backbone est une reproduction exacte des dépôts
   officiels.
4. Les résultats prouvent une applicabilité au plasma de tokamak.
5. La revue publique remplace une revue exhaustive Scopus/Web of Science.

## 11. Positionnement recommandé de l'article

Titre anglais :

> **Adaptive PINNs under Competing Training Measures: A Controlled Study of Fixed References, Exact Reweighting, KDE Volume Weighting, and Variational Residual Attention**

Titre français :

> **PINNs adaptatifs sous mesures d'entraînement concurrentes : étude contrôlée des références fixes, de la repondération exacte, de la pondération volumique KDE et de l'attention variationnelle aux résidus**

La contribution est un benchmark causal et reproductible qui montre pourquoi
une seule métrique, une seule EDP ou un seul mécanisme ne suffit pas pour
conclure.

## 12. Travail restant avant soumission

1. ablater le potentiel vRBA et son auto-équilibrage global ;
2. profiler les méthodes de façon intercalée sur CPU et GPU ;
3. réaliser au moins une reproduction officielle séparée de VW ou vRBA ;
4. ajouter un baseline de placement moderne distinct, par exemple PACMANN ou
   QR-DEIM ;
5. faire relire le positionnement de nouveauté par un spécialiste PINN ;
6. conserver la transition vers le plasma dans un article ultérieur.
