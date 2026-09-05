# Rapport automatique — article1_current_evidence

## Complétude

- Exécutions réussies : **170/170**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — entraînement long | m1 | 10/10 | 0.3379 [0.2274, 0.3953] | 0.0484 | 23.90 |
| Burgers — entraînement long | m5 | 10/10 | 0.5007 [0.4325, 0.5448] | 0.0498 | 26.26 |
| Burgers — entraînement long | m6 | 10/10 | 0.4706 [0.4386, 0.5370] | 0.0487 | 25.24 |
| Allen–Cahn | m5 | 10/10 | 0.0963 [0.0792, 0.1124] | 0.0670 | 2.56 |
| Allen–Cahn | m6 | 10/10 | 0.0980 [0.0747, 0.1140] | 0.0659 | 2.28 |
| Helmholtz | m5 | 10/10 | 1.1521 [1.1399, 1.1637] | 0.0523 | 3.03 |
| Helmholtz | m6 | 10/10 | 1.1418 [1.1325, 1.1669] | 0.0523 | 2.80 |
| Équation des ondes | m5 | 10/10 | 0.3088 [0.3059, 0.3324] | 0.0729 | 3.93 |
| Équation des ondes | m6 | 10/10 | 0.3093 [0.3013, 0.3348] | 0.0674 | 3.35 |
| Burgers — données rares propres | m5 | 10/10 | 0.5736 [0.5378, 0.6136] | 0.0686 | 2.96 |
| Burgers — données rares propres | m6 | 10/10 | 0.5629 [0.5354, 0.6076] | 0.0661 | 2.52 |
| Burgers — données rares bruitées | m5 | 10/10 | 0.5904 [0.5512, 0.6142] | 0.0736 | 2.45 |
| Burgers — données rares bruitées | m6 | 10/10 | 0.5871 [0.5356, 0.6024] | 0.0760 | 2.33 |
| Burgers — un capteur et bruit fort | m5 | 10/10 | 0.5997 [0.5763, 0.6703] | 0.0680 | 2.75 |
| Burgers — un capteur et bruit fort | m6 | 10/10 | 0.5973 [0.5830, 0.6686] | 0.0684 | 2.40 |
| Burgers — bloc de capteurs manquant | m5 | 10/10 | 0.5571 [0.5276, 0.5858] | 0.0629 | 2.23 |
| Burgers — bloc de capteurs manquant | m6 | 10/10 | 0.5542 [0.5321, 0.5659] | 0.0625 | 2.35 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — entraînement long | m5_minus_m1 | 10 | 0.1415 | [0.0629, 0.2900] | 10 % | 0.021 |
| Burgers — entraînement long | m6_minus_m5 | 10 | -0.0291 | [-0.1208, 0.1678] | 60 % | 0.754 |
| Allen–Cahn | m6_minus_m5 | 10 | 0.0019 | [-0.0027, 0.0030] | 30 % | 0.344 |
| Helmholtz | m6_minus_m5 | 10 | -0.0058 | [-0.0284, 0.0144] | 70 % | 0.344 |
| Équation des ondes | m6_minus_m5 | 10 | -0.0015 | [-0.0059, 0.0018] | 60 % | 0.754 |
| Burgers — données rares propres | m6_minus_m5 | 10 | -0.0054 | [-0.0106, 0.0173] | 60 % | 0.754 |
| Burgers — données rares bruitées | m6_minus_m5 | 10 | -0.0044 | [-0.0208, 0.0078] | 50 % | 1.000 |
| Burgers — un capteur et bruit fort | m6_minus_m5 | 10 | 0.0023 | [-0.0140, 0.0149] | 40 % | 0.754 |
| Burgers — bloc de capteurs manquant | m6_minus_m5 | 10 | -0.0018 | [-0.0058, 0.0044] | 60 % | 0.754 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **26 fichiers** (PNG et PDF).
