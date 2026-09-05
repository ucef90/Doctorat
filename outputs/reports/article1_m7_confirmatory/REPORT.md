# Rapport automatique — article1_m7_confirmatory

## Complétude

- Exécutions réussies : **160/160**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — confirmation M7 | m5 | 10/10 | 0.5007 [0.4325, 0.5448] | 0.0498 | 26.26 |
| Burgers — confirmation M7 | m6 | 10/10 | 0.4706 [0.4386, 0.5370] | 0.0487 | 25.24 |
| Burgers — confirmation M7 | m7u | 10/10 | 0.3814 [0.3285, 0.4747] | 0.0514 | 14.93 |
| Burgers — confirmation M7 | m7 | 10/10 | 0.4410 [0.3981, 0.5041] | 0.0542 | 15.14 |
| Allen–Cahn — confirmation M7 | m5 | 10/10 | 0.0963 [0.0792, 0.1124] | 0.0670 | 2.56 |
| Allen–Cahn — confirmation M7 | m6 | 10/10 | 0.0980 [0.0747, 0.1140] | 0.0659 | 2.28 |
| Allen–Cahn — confirmation M7 | m7u | 10/10 | 0.1020 [0.0776, 0.1134] | 0.0668 | 1.95 |
| Allen–Cahn — confirmation M7 | m7 | 10/10 | 0.1081 [0.0901, 0.1131] | 0.0681 | 1.95 |
| Helmholtz — confirmation M7 | m5 | 10/10 | 1.1521 [1.1399, 1.1637] | 0.0523 | 3.03 |
| Helmholtz — confirmation M7 | m6 | 10/10 | 1.1418 [1.1325, 1.1669] | 0.0523 | 2.80 |
| Helmholtz — confirmation M7 | m7u | 10/10 | 1.1455 [1.1203, 1.1753] | 0.0523 | 2.20 |
| Helmholtz — confirmation M7 | m7 | 10/10 | 1.1264 [1.1126, 1.1601] | 0.0523 | 2.25 |
| Ondes — confirmation M7 | m5 | 10/10 | 0.3088 [0.3059, 0.3324] | 0.0729 | 3.93 |
| Ondes — confirmation M7 | m6 | 10/10 | 0.3093 [0.3013, 0.3348] | 0.0674 | 3.35 |
| Ondes — confirmation M7 | m7u | 10/10 | 0.3085 [0.3027, 0.3308] | 0.0720 | 2.45 |
| Ondes — confirmation M7 | m7 | 10/10 | 0.3057 [0.2997, 0.3235] | 0.0733 | 2.51 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — confirmation M7 | m6_minus_m5 | 10 | -0.0291 | [-0.1208, 0.1678] | 60 % | 0.754 |
| Burgers — confirmation M7 | m7_minus_m5 | 10 | -0.0848 | [-0.2085, 0.1816] | 70 % | 0.344 |
| Burgers — confirmation M7 | m7_minus_m6 | 10 | -0.0533 | [-0.2249, 0.0743] | 70 % | 0.344 |
| Burgers — confirmation M7 | m7_minus_m7u | 10 | 0.0643 | [-0.0687, 0.1726] | 40 % | 0.754 |
| Allen–Cahn — confirmation M7 | m6_minus_m5 | 10 | 0.0019 | [-0.0027, 0.0030] | 30 % | 0.344 |
| Allen–Cahn — confirmation M7 | m7_minus_m5 | 10 | 0.0088 | [0.0046, 0.0159] | 10 % | 0.021 |
| Allen–Cahn — confirmation M7 | m7_minus_m6 | 10 | 0.0100 | [0.0052, 0.0142] | 10 % | 0.021 |
| Allen–Cahn — confirmation M7 | m7_minus_m7u | 10 | 0.0097 | [2.33e-04, 0.0160] | 20 % | 0.109 |
| Helmholtz — confirmation M7 | m6_minus_m5 | 10 | -0.0058 | [-0.0284, 0.0144] | 70 % | 0.344 |
| Helmholtz — confirmation M7 | m7_minus_m5 | 10 | -0.0261 | [-0.0355, 0.0158] | 60 % | 0.754 |
| Helmholtz — confirmation M7 | m7_minus_m6 | 10 | -0.0125 | [-0.0314, 0.0128] | 60 % | 0.754 |
| Helmholtz — confirmation M7 | m7_minus_m7u | 10 | -0.0327 | [-0.0437, 0.0178] | 70 % | 0.344 |
| Ondes — confirmation M7 | m6_minus_m5 | 10 | -0.0015 | [-0.0059, 0.0018] | 60 % | 0.754 |
| Ondes — confirmation M7 | m7_minus_m5 | 10 | -0.0035 | [-0.0107, -4.69e-04] | 80 % | 0.109 |
| Ondes — confirmation M7 | m7_minus_m6 | 10 | -0.0034 | [-0.0099, 0.0027] | 70 % | 0.344 |
| Ondes — confirmation M7 | m7_minus_m7u | 10 | -0.0022 | [-0.0088, 0.0032] | 70 % | 0.344 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **18 fichiers** (PNG et PDF).
