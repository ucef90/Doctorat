# Rapport automatique — article1_helmholtz_calibrated

## Complétude

- Exécutions réussies : **90/90**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Helmholtz calibrée — mode (1,1), k=1 | m0 | 10/10 | 0.1120 [0.1091, 0.1235] | 0 | 13.13 |
| Helmholtz calibrée — mode (1,1), k=1 | m1 | 10/10 | 0.1018 [0.0904, 0.1072] | 0.0284 | 12.77 |
| Helmholtz calibrée — mode (1,1), k=1 | m3 | 10/10 | 0.1160 [0.1123, 0.1215] | 0 | 12.52 |
| Helmholtz calibrée — mode (1,1), k=1 | m5 | 10/10 | 0.1041 [0.0962, 0.1113] | 0.0284 | 13.42 |
| Helmholtz calibrée — mode (1,1), k=1 | m6 | 10/10 | 0.1043 [0.0959, 0.1118] | 0.0284 | 13.38 |
| Helmholtz calibrée — mode (1,1), k=1 | m7u | 10/10 | 0.1076 [0.1010, 0.1231] | 0.0284 | 23.33 |
| Helmholtz calibrée — mode (1,1), k=1 | m7 | 10/10 | 0.1006 [0.0846, 0.1078] | 0.0284 | 13.32 |
| Helmholtz calibrée — mode (1,1), k=1 | vw | 10/10 | 0.1096 [0.1064, 0.1200] | 0 | 16.87 |
| Helmholtz calibrée — mode (1,1), k=1 | vwca | 10/10 | 0.0941 [0.0888, 0.1012] | 0.0284 | 13.59 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Helmholtz calibrée — mode (1,1), k=1 | m5_minus_m0 | 10 | -0.0109 | [-0.0138, -0.0048] | 90 % | 0.021 |
| Helmholtz calibrée — mode (1,1), k=1 | m6_minus_m5 | 10 | 2.80e-04 | [-7.60e-04, 8.20e-04] | 40 % | 0.754 |
| Helmholtz calibrée — mode (1,1), k=1 | m7_minus_m5 | 10 | -0.0101 | [-0.0135, -0.0045] | 90 % | 0.021 |
| Helmholtz calibrée — mode (1,1), k=1 | m7_minus_m7u | 10 | -0.0132 | [-0.0209, -0.0061] | 90 % | 0.021 |
| Helmholtz calibrée — mode (1,1), k=1 | m7_minus_vw | 10 | -0.0181 | [-0.0235, -0.0112] | 100 % | 0.002 |
| Helmholtz calibrée — mode (1,1), k=1 | m7_minus_vwca | 10 | -2.91e-04 | [-0.0044, 0.0031] | 50 % | 1.000 |
| Helmholtz calibrée — mode (1,1), k=1 | vwca_minus_vw | 10 | -0.0179 | [-0.0216, -0.0149] | 100 % | 0.002 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **12 fichiers** (PNG et PDF).
