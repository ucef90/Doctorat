# Rapport automatique — article1_vw_confirmatory

## Complétude

- Exécutions réussies : **240/240**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — M7 contre VW | m5 | 10/10 | 0.5007 [0.4325, 0.5448] | 0.0498 | 26.26 |
| Burgers — M7 contre VW | m6 | 10/10 | 0.4706 [0.4386, 0.5370] | 0.0487 | 25.24 |
| Burgers — M7 contre VW | m7u | 10/10 | 0.3814 [0.3285, 0.4747] | 0.0514 | 14.93 |
| Burgers — M7 contre VW | m7 | 10/10 | 0.4410 [0.3981, 0.5041] | 0.0542 | 15.14 |
| Burgers — M7 contre VW | vw | 10/10 | 0.4350 [0.3793, 0.5064] | 0 | 14.93 |
| Burgers — M7 contre VW | vwca | 10/10 | 0.5313 [0.4917, 0.5723] | 0.0521 | 14.94 |
| Allen–Cahn — M7 contre VW | m5 | 10/10 | 0.0963 [0.0792, 0.1124] | 0.0670 | 2.56 |
| Allen–Cahn — M7 contre VW | m6 | 10/10 | 0.0980 [0.0747, 0.1140] | 0.0659 | 2.28 |
| Allen–Cahn — M7 contre VW | m7u | 10/10 | 0.1020 [0.0776, 0.1134] | 0.0668 | 1.95 |
| Allen–Cahn — M7 contre VW | m7 | 10/10 | 0.1081 [0.0901, 0.1131] | 0.0681 | 1.95 |
| Allen–Cahn — M7 contre VW | vw | 10/10 | 0.0912 [0.0753, 0.1065] | 0 | 1.88 |
| Allen–Cahn — M7 contre VW | vwca | 10/10 | 0.0994 [0.0851, 0.1250] | 0.0670 | 1.93 |
| Helmholtz — M7 contre VW | m5 | 10/10 | 1.1521 [1.1399, 1.1637] | 0.0523 | 3.03 |
| Helmholtz — M7 contre VW | m6 | 10/10 | 1.1418 [1.1325, 1.1669] | 0.0523 | 2.80 |
| Helmholtz — M7 contre VW | m7u | 10/10 | 1.1455 [1.1203, 1.1753] | 0.0523 | 2.20 |
| Helmholtz — M7 contre VW | m7 | 10/10 | 1.1264 [1.1126, 1.1601] | 0.0523 | 2.25 |
| Helmholtz — M7 contre VW | vw | 10/10 | 1.1303 [1.1160, 1.1536] | 0 | 2.20 |
| Helmholtz — M7 contre VW | vwca | 10/10 | 1.1309 [1.1018, 1.1439] | 0.0523 | 2.25 |
| Ondes — M7 contre VW | m5 | 10/10 | 0.3088 [0.3059, 0.3324] | 0.0729 | 3.93 |
| Ondes — M7 contre VW | m6 | 10/10 | 0.3093 [0.3013, 0.3348] | 0.0674 | 3.35 |
| Ondes — M7 contre VW | m7u | 10/10 | 0.3085 [0.3027, 0.3308] | 0.0720 | 2.45 |
| Ondes — M7 contre VW | m7 | 10/10 | 0.3057 [0.2997, 0.3235] | 0.0733 | 2.51 |
| Ondes — M7 contre VW | vw | 10/10 | 0.2825 [0.2735, 0.2886] | 0 | 2.76 |
| Ondes — M7 contre VW | vwca | 10/10 | 0.3146 [0.2994, 0.3323] | 0.0728 | 2.88 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — M7 contre VW | m7_minus_m5 | 10 | -0.0848 | [-0.2085, 0.1816] | 70 % | 0.344 |
| Burgers — M7 contre VW | m7_minus_m7u | 10 | 0.0643 | [-0.0687, 0.1726] | 40 % | 0.754 |
| Burgers — M7 contre VW | m7_minus_vw | 10 | 0.0291 | [-0.0884, 0.0941] | 40 % | 0.754 |
| Burgers — M7 contre VW | m7_minus_vwca | 10 | -0.1414 | [-0.2757, 0.0144] | 70 % | 0.344 |
| Burgers — M7 contre VW | vwca_minus_vw | 10 | 0.1186 | [0.0319, 0.3151] | 20 % | 0.109 |
| Allen–Cahn — M7 contre VW | m7_minus_m5 | 10 | 0.0088 | [0.0046, 0.0159] | 10 % | 0.021 |
| Allen–Cahn — M7 contre VW | m7_minus_m7u | 10 | 0.0097 | [2.33e-04, 0.0160] | 20 % | 0.109 |
| Allen–Cahn — M7 contre VW | m7_minus_vw | 10 | 5.84e-04 | [-0.0419, 0.0309] | 50 % | 1.000 |
| Allen–Cahn — M7 contre VW | m7_minus_vwca | 10 | -7.03e-04 | [-0.0422, 0.0146] | 50 % | 1.000 |
| Allen–Cahn — M7 contre VW | vwca_minus_vw | 10 | 0.0066 | [-0.0105, 0.0325] | 30 % | 0.344 |
| Helmholtz — M7 contre VW | m7_minus_m5 | 10 | -0.0261 | [-0.0355, 0.0158] | 60 % | 0.754 |
| Helmholtz — M7 contre VW | m7_minus_m7u | 10 | -0.0327 | [-0.0437, 0.0178] | 70 % | 0.344 |
| Helmholtz — M7 contre VW | m7_minus_vw | 10 | 0.0083 | [-0.0100, 0.0230] | 20 % | 0.109 |
| Helmholtz — M7 contre VW | m7_minus_vwca | 10 | 0.0229 | [-0.0153, 0.0459] | 40 % | 0.754 |
| Helmholtz — M7 contre VW | vwca_minus_vw | 10 | -0.0137 | [-0.0303, 0.0011] | 70 % | 0.344 |
| Ondes — M7 contre VW | m7_minus_m5 | 10 | -0.0035 | [-0.0107, -4.69e-04] | 80 % | 0.109 |
| Ondes — M7 contre VW | m7_minus_m7u | 10 | -0.0022 | [-0.0088, 0.0032] | 70 % | 0.344 |
| Ondes — M7 contre VW | m7_minus_vw | 10 | 0.0280 | [0.0199, 0.0483] | 0 % | 0.002 |
| Ondes — M7 contre VW | m7_minus_vwca | 10 | -0.0026 | [-0.0154, 0.0037] | 60 % | 0.754 |
| Ondes — M7 contre VW | vwca_minus_vw | 10 | 0.0355 | [0.0178, 0.0517] | 0 % | 0.002 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **18 fichiers** (PNG et PDF).
