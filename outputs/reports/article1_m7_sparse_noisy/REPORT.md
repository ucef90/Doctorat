# Rapport automatique — article1_m7_sparse_noisy

## Complétude

- Exécutions réussies : **160/160**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — 13 observations propres | m5 | 10/10 | 0.5736 [0.5378, 0.6136] | 0.0686 | 2.96 |
| Burgers — 13 observations propres | m6 | 10/10 | 0.5629 [0.5354, 0.6076] | 0.0661 | 2.52 |
| Burgers — 13 observations propres | m7u | 10/10 | 0.5927 [0.5346, 0.6099] | 0.0682 | 1.90 |
| Burgers — 13 observations propres | m7 | 10/10 | 0.5281 [0.5004, 0.5730] | 0.0728 | 1.98 |
| Burgers — 13 observations bruitées | m5 | 10/10 | 0.5904 [0.5512, 0.6142] | 0.0736 | 2.45 |
| Burgers — 13 observations bruitées | m6 | 10/10 | 0.5871 [0.5356, 0.6024] | 0.0760 | 2.33 |
| Burgers — 13 observations bruitées | m7u | 10/10 | 0.5905 [0.5451, 0.6195] | 0.0738 | 1.90 |
| Burgers — 13 observations bruitées | m7 | 10/10 | 0.5527 [0.4910, 0.5660] | 0.0745 | 1.99 |
| Burgers — une observation et bruit fort | m5 | 10/10 | 0.5997 [0.5763, 0.6703] | 0.0680 | 2.75 |
| Burgers — une observation et bruit fort | m6 | 10/10 | 0.5973 [0.5830, 0.6686] | 0.0684 | 2.40 |
| Burgers — une observation et bruit fort | m7u | 10/10 | 0.6050 [0.5790, 0.6512] | 0.0672 | 1.96 |
| Burgers — une observation et bruit fort | m7 | 10/10 | 0.5776 [0.5563, 0.6405] | 0.0721 | 1.97 |
| Burgers — bloc de capteurs manquant | m5 | 10/10 | 0.5571 [0.5276, 0.5858] | 0.0629 | 2.23 |
| Burgers — bloc de capteurs manquant | m6 | 10/10 | 0.5542 [0.5321, 0.5659] | 0.0625 | 2.35 |
| Burgers — bloc de capteurs manquant | m7u | 10/10 | 0.5616 [0.5430, 0.5786] | 0.0625 | 1.94 |
| Burgers — bloc de capteurs manquant | m7 | 10/10 | 0.5287 [0.4959, 0.5422] | 0.0641 | 2.52 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — 13 observations propres | m6_minus_m5 | 10 | -0.0054 | [-0.0106, 0.0173] | 60 % | 0.754 |
| Burgers — 13 observations propres | m7_minus_m5 | 10 | -0.0410 | [-0.0568, -0.0310] | 90 % | 0.021 |
| Burgers — 13 observations propres | m7_minus_m6 | 10 | -0.0343 | [-0.0652, -0.0217] | 100 % | 0.002 |
| Burgers — 13 observations propres | m7_minus_m7u | 10 | -0.0483 | [-0.0662, -0.0300] | 100 % | 0.002 |
| Burgers — 13 observations bruitées | m6_minus_m5 | 10 | -0.0044 | [-0.0208, 0.0078] | 50 % | 1.000 |
| Burgers — 13 observations bruitées | m7_minus_m5 | 10 | -0.0464 | [-0.0749, -0.0262] | 100 % | 0.002 |
| Burgers — 13 observations bruitées | m7_minus_m6 | 10 | -0.0286 | [-0.0589, -0.0239] | 100 % | 0.002 |
| Burgers — 13 observations bruitées | m7_minus_m7u | 10 | -0.0482 | [-0.0812, -0.0247] | 90 % | 0.021 |
| Burgers — une observation et bruit fort | m6_minus_m5 | 10 | 0.0023 | [-0.0140, 0.0149] | 40 % | 0.754 |
| Burgers — une observation et bruit fort | m7_minus_m5 | 10 | -0.0217 | [-0.0461, -0.0151] | 100 % | 0.002 |
| Burgers — une observation et bruit fort | m7_minus_m6 | 10 | -0.0268 | [-0.0424, -0.0159] | 90 % | 0.021 |
| Burgers — une observation et bruit fort | m7_minus_m7u | 10 | -0.0229 | [-0.0338, -0.0073] | 90 % | 0.021 |
| Burgers — bloc de capteurs manquant | m6_minus_m5 | 10 | -0.0018 | [-0.0058, 0.0044] | 60 % | 0.754 |
| Burgers — bloc de capteurs manquant | m7_minus_m5 | 10 | -0.0310 | [-0.0477, -0.0184] | 100 % | 0.002 |
| Burgers — bloc de capteurs manquant | m7_minus_m6 | 10 | -0.0258 | [-0.0368, -0.0194] | 100 % | 0.002 |
| Burgers — bloc de capteurs manquant | m7_minus_m7u | 10 | -0.0360 | [-0.0503, -0.0268] | 100 % | 0.002 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **18 fichiers** (PNG et PDF).
