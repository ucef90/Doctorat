# Rapport automatique — article1_vrba_confirmatory

## Complétude

- Exécutions réussies : **200/200**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — vRBA confirmatoire | m5 | 10/10 | 0.5007 [0.4325, 0.5448] | 0.0498 | 26.26 |
| Burgers — vRBA confirmatoire | m6 | 10/10 | 0.4706 [0.4386, 0.5370] | 0.0487 | 25.24 |
| Burgers — vRBA confirmatoire | m7 | 10/10 | 0.4410 [0.3981, 0.5041] | 0.0542 | 15.14 |
| Burgers — vRBA confirmatoire | vw | 10/10 | 0.4350 [0.3793, 0.5064] | 0 | 14.93 |
| Burgers — vRBA confirmatoire | vrba | 10/10 | 0.2507 [0.1881, 0.3660] | 0.0022 | 29.80 |
| Allen–Cahn — vRBA confirmatoire | m5 | 10/10 | 0.0963 [0.0792, 0.1124] | 0.0670 | 2.56 |
| Allen–Cahn — vRBA confirmatoire | m6 | 10/10 | 0.0980 [0.0747, 0.1140] | 0.0659 | 2.28 |
| Allen–Cahn — vRBA confirmatoire | m7 | 10/10 | 0.1081 [0.0901, 0.1131] | 0.0681 | 1.95 |
| Allen–Cahn — vRBA confirmatoire | vw | 10/10 | 0.0912 [0.0753, 0.1065] | 0 | 1.88 |
| Allen–Cahn — vRBA confirmatoire | vrba | 10/10 | 0.0401 [0.0332, 0.0456] | 0.0012 | 3.25 |
| Helmholtz calibrée — vRBA confirmatoire | m5 | 10/10 | 0.1041 [0.0962, 0.1113] | 0.0284 | 13.42 |
| Helmholtz calibrée — vRBA confirmatoire | m6 | 10/10 | 0.1043 [0.0959, 0.1118] | 0.0284 | 13.38 |
| Helmholtz calibrée — vRBA confirmatoire | m7 | 10/10 | 0.1006 [0.0846, 0.1078] | 0.0284 | 13.32 |
| Helmholtz calibrée — vRBA confirmatoire | vw | 10/10 | 0.1096 [0.1064, 0.1200] | 0 | 16.87 |
| Helmholtz calibrée — vRBA confirmatoire | vrba | 10/10 | 0.0388 [0.0219, 0.0534] | 0.0026 | 24.40 |
| Ondes — vRBA confirmatoire | m5 | 10/10 | 0.3088 [0.3059, 0.3324] | 0.0729 | 3.93 |
| Ondes — vRBA confirmatoire | m6 | 10/10 | 0.3093 [0.3013, 0.3348] | 0.0674 | 3.35 |
| Ondes — vRBA confirmatoire | m7 | 10/10 | 0.3057 [0.2997, 0.3235] | 0.0733 | 2.51 |
| Ondes — vRBA confirmatoire | vw | 10/10 | 0.2825 [0.2735, 0.2886] | 0 | 2.76 |
| Ondes — vRBA confirmatoire | vrba | 10/10 | 0.1745 [0.1545, 0.1993] | 3.35e-04 | 4.34 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — vRBA confirmatoire | vrba_minus_m5 | 10 | -0.2066 | [-0.2891, -0.1010] | 90 % | 0.021 |
| Burgers — vRBA confirmatoire | vrba_minus_m6 | 10 | -0.2577 | [-0.3230, -0.1292] | 90 % | 0.021 |
| Burgers — vRBA confirmatoire | vrba_minus_m7 | 10 | -0.1770 | [-0.2339, -0.0114] | 80 % | 0.109 |
| Burgers — vRBA confirmatoire | vrba_minus_vw | 10 | -0.1236 | [-0.2566, -0.0283] | 90 % | 0.021 |
| Allen–Cahn — vRBA confirmatoire | vrba_minus_m5 | 10 | -0.0605 | [-0.0830, -0.0357] | 100 % | 0.002 |
| Allen–Cahn — vRBA confirmatoire | vrba_minus_m6 | 10 | -0.0601 | [-0.0807, -0.0380] | 100 % | 0.002 |
| Allen–Cahn — vRBA confirmatoire | vrba_minus_m7 | 10 | -0.0648 | [-0.0903, -0.0509] | 100 % | 0.002 |
| Allen–Cahn — vRBA confirmatoire | vrba_minus_vw | 10 | -0.0617 | [-0.1269, -0.0267] | 100 % | 0.002 |
| Helmholtz calibrée — vRBA confirmatoire | vrba_minus_m5 | 10 | -0.0743 | [-0.0814, -0.0536] | 100 % | 0.002 |
| Helmholtz calibrée — vRBA confirmatoire | vrba_minus_m6 | 10 | -0.0742 | [-0.0811, -0.0544] | 100 % | 0.002 |
| Helmholtz calibrée — vRBA confirmatoire | vrba_minus_m7 | 10 | -0.0611 | [-0.0690, -0.0496] | 100 % | 0.002 |
| Helmholtz calibrée — vRBA confirmatoire | vrba_minus_vw | 10 | -0.0844 | [-0.0891, -0.0608] | 100 % | 0.002 |
| Ondes — vRBA confirmatoire | vrba_minus_m5 | 10 | -0.1384 | [-0.2160, -0.1223] | 100 % | 0.002 |
| Ondes — vRBA confirmatoire | vrba_minus_m6 | 10 | -0.1389 | [-0.2178, -0.1249] | 100 % | 0.002 |
| Ondes — vRBA confirmatoire | vrba_minus_m7 | 10 | -0.1322 | [-0.2163, -0.1190] | 100 % | 0.002 |
| Ondes — vRBA confirmatoire | vrba_minus_vw | 10 | -0.1061 | [-0.1502, -0.0836] | 100 % | 0.002 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **18 fichiers** (PNG et PDF).
