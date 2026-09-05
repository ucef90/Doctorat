# Rapport automatique — article1_vw_sparse_noisy

## Complétude

- Exécutions réussies : **240/240**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — 13 observations propres | m5 | 10/10 | 0.5736 [0.5378, 0.6136] | 0.0686 | 2.96 |
| Burgers — 13 observations propres | m6 | 10/10 | 0.5629 [0.5354, 0.6076] | 0.0661 | 2.52 |
| Burgers — 13 observations propres | m7u | 10/10 | 0.5927 [0.5346, 0.6099] | 0.0682 | 1.90 |
| Burgers — 13 observations propres | m7 | 10/10 | 0.5281 [0.5004, 0.5730] | 0.0728 | 1.98 |
| Burgers — 13 observations propres | vw | 10/10 | 0.5066 [0.4894, 0.5303] | 0 | 2.16 |
| Burgers — 13 observations propres | vwca | 10/10 | 0.5717 [0.5269, 0.6317] | 0.0715 | 2.30 |
| Burgers — 13 observations bruitées | m5 | 10/10 | 0.5904 [0.5512, 0.6142] | 0.0736 | 2.45 |
| Burgers — 13 observations bruitées | m6 | 10/10 | 0.5871 [0.5356, 0.6024] | 0.0760 | 2.33 |
| Burgers — 13 observations bruitées | m7u | 10/10 | 0.5905 [0.5451, 0.6195] | 0.0738 | 1.90 |
| Burgers — 13 observations bruitées | m7 | 10/10 | 0.5527 [0.4910, 0.5660] | 0.0745 | 1.99 |
| Burgers — 13 observations bruitées | vw | 10/10 | 0.5229 [0.5154, 0.5407] | 0 | 2.11 |
| Burgers — 13 observations bruitées | vwca | 10/10 | 0.5740 [0.5311, 0.6035] | 0.0738 | 2.17 |
| Burgers — une observation et bruit fort | m5 | 10/10 | 0.5997 [0.5763, 0.6703] | 0.0680 | 2.75 |
| Burgers — une observation et bruit fort | m6 | 10/10 | 0.5973 [0.5830, 0.6686] | 0.0684 | 2.40 |
| Burgers — une observation et bruit fort | m7u | 10/10 | 0.6050 [0.5790, 0.6512] | 0.0672 | 1.96 |
| Burgers — une observation et bruit fort | m7 | 10/10 | 0.5776 [0.5563, 0.6405] | 0.0721 | 1.97 |
| Burgers — une observation et bruit fort | vw | 10/10 | 0.5457 [0.5289, 0.6585] | 0 | 2.12 |
| Burgers — une observation et bruit fort | vwca | 10/10 | 0.6097 [0.5758, 0.6890] | 0.0699 | 2.18 |
| Burgers — bloc de capteurs manquant | m5 | 10/10 | 0.5571 [0.5276, 0.5858] | 0.0629 | 2.23 |
| Burgers — bloc de capteurs manquant | m6 | 10/10 | 0.5542 [0.5321, 0.5659] | 0.0625 | 2.35 |
| Burgers — bloc de capteurs manquant | m7u | 10/10 | 0.5616 [0.5430, 0.5786] | 0.0625 | 1.94 |
| Burgers — bloc de capteurs manquant | m7 | 10/10 | 0.5287 [0.4959, 0.5422] | 0.0641 | 2.52 |
| Burgers — bloc de capteurs manquant | vw | 10/10 | 0.4924 [0.4853, 0.5007] | 0 | 2.13 |
| Burgers — bloc de capteurs manquant | vwca | 10/10 | 0.5391 [0.5300, 0.5798] | 0.0631 | 2.20 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — 13 observations propres | m7_minus_m5 | 10 | -0.0410 | [-0.0568, -0.0310] | 90 % | 0.021 |
| Burgers — 13 observations propres | m7_minus_m7u | 10 | -0.0483 | [-0.0662, -0.0300] | 100 % | 0.002 |
| Burgers — 13 observations propres | m7_minus_vw | 10 | 0.0229 | [-0.0099, 0.0693] | 30 % | 0.344 |
| Burgers — 13 observations propres | m7_minus_vwca | 10 | -0.0324 | [-0.0685, -0.0121] | 100 % | 0.002 |
| Burgers — 13 observations propres | vwca_minus_vw | 10 | 0.0497 | [0.0180, 0.1208] | 10 % | 0.021 |
| Burgers — 13 observations bruitées | m7_minus_m5 | 10 | -0.0464 | [-0.0749, -0.0262] | 100 % | 0.002 |
| Burgers — 13 observations bruitées | m7_minus_m7u | 10 | -0.0482 | [-0.0812, -0.0247] | 90 % | 0.021 |
| Burgers — 13 observations bruitées | m7_minus_vw | 10 | 0.0090 | [-0.0255, 0.0522] | 50 % | 1.000 |
| Burgers — 13 observations bruitées | m7_minus_vwca | 10 | -0.0285 | [-0.0562, -0.0078] | 90 % | 0.021 |
| Burgers — 13 observations bruitées | vwca_minus_vw | 10 | 0.0441 | [0.0058, 0.0777] | 20 % | 0.109 |
| Burgers — une observation et bruit fort | m7_minus_m5 | 10 | -0.0217 | [-0.0461, -0.0151] | 100 % | 0.002 |
| Burgers — une observation et bruit fort | m7_minus_m7u | 10 | -0.0229 | [-0.0338, -0.0073] | 90 % | 0.021 |
| Burgers — une observation et bruit fort | m7_minus_vw | 10 | 0.0284 | [-0.0295, 0.0433] | 40 % | 0.754 |
| Burgers — une observation et bruit fort | m7_minus_vwca | 10 | -0.0316 | [-0.0481, -0.0182] | 90 % | 0.021 |
| Burgers — une observation et bruit fort | vwca_minus_vw | 10 | 0.0358 | [2.54e-04, 0.0674] | 20 % | 0.109 |
| Burgers — bloc de capteurs manquant | m7_minus_m5 | 10 | -0.0310 | [-0.0477, -0.0184] | 100 % | 0.002 |
| Burgers — bloc de capteurs manquant | m7_minus_m7u | 10 | -0.0360 | [-0.0503, -0.0268] | 100 % | 0.002 |
| Burgers — bloc de capteurs manquant | m7_minus_vw | 10 | 0.0363 | [-0.0031, 0.0903] | 30 % | 0.344 |
| Burgers — bloc de capteurs manquant | m7_minus_vwca | 10 | -0.0245 | [-0.0367, -0.0146] | 100 % | 0.002 |
| Burgers — bloc de capteurs manquant | vwca_minus_vw | 10 | 0.0641 | [0.0112, 0.1016] | 10 % | 0.021 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **18 fichiers** (PNG et PDF).
