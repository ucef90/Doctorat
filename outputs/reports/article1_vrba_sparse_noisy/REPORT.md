# Rapport automatique — article1_vrba_sparse_noisy

## Complétude

- Exécutions réussies : **200/200**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — vRBA, 13 observations propres | m5 | 10/10 | 0.5736 [0.5378, 0.6136] | 0.0686 | 2.96 |
| Burgers — vRBA, 13 observations propres | m6 | 10/10 | 0.5629 [0.5354, 0.6076] | 0.0661 | 2.52 |
| Burgers — vRBA, 13 observations propres | m7 | 10/10 | 0.5281 [0.5004, 0.5730] | 0.0728 | 1.98 |
| Burgers — vRBA, 13 observations propres | vw | 10/10 | 0.5066 [0.4894, 0.5303] | 0 | 2.16 |
| Burgers — vRBA, 13 observations propres | vrba | 10/10 | 0.3693 [0.2992, 0.4081] | 0.0011 | 3.40 |
| Burgers — vRBA, 13 observations bruitées | m5 | 10/10 | 0.5904 [0.5512, 0.6142] | 0.0736 | 2.45 |
| Burgers — vRBA, 13 observations bruitées | m6 | 10/10 | 0.5871 [0.5356, 0.6024] | 0.0760 | 2.33 |
| Burgers — vRBA, 13 observations bruitées | m7 | 10/10 | 0.5527 [0.4910, 0.5660] | 0.0745 | 1.99 |
| Burgers — vRBA, 13 observations bruitées | vw | 10/10 | 0.5229 [0.5154, 0.5407] | 0 | 2.11 |
| Burgers — vRBA, 13 observations bruitées | vrba | 10/10 | 0.3562 [0.2850, 0.4124] | 9.63e-04 | 3.57 |
| Burgers — vRBA, une observation et bruit fort | m5 | 10/10 | 0.5997 [0.5763, 0.6703] | 0.0680 | 2.75 |
| Burgers — vRBA, une observation et bruit fort | m6 | 10/10 | 0.5973 [0.5830, 0.6686] | 0.0684 | 2.40 |
| Burgers — vRBA, une observation et bruit fort | m7 | 10/10 | 0.5776 [0.5563, 0.6405] | 0.0721 | 1.97 |
| Burgers — vRBA, une observation et bruit fort | vw | 10/10 | 0.5457 [0.5289, 0.6585] | 0 | 2.12 |
| Burgers — vRBA, une observation et bruit fort | vrba | 10/10 | 0.4469 [0.4187, 0.4873] | 9.64e-04 | 3.54 |
| Burgers — vRBA, bloc de capteurs manquant | m5 | 10/10 | 0.5571 [0.5276, 0.5858] | 0.0629 | 2.23 |
| Burgers — vRBA, bloc de capteurs manquant | m6 | 10/10 | 0.5542 [0.5321, 0.5659] | 0.0625 | 2.35 |
| Burgers — vRBA, bloc de capteurs manquant | m7 | 10/10 | 0.5287 [0.4959, 0.5422] | 0.0641 | 2.52 |
| Burgers — vRBA, bloc de capteurs manquant | vw | 10/10 | 0.4924 [0.4853, 0.5007] | 0 | 2.13 |
| Burgers — vRBA, bloc de capteurs manquant | vrba | 10/10 | 0.3322 [0.3236, 0.3900] | 9.73e-04 | 3.66 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — vRBA, 13 observations propres | vrba_minus_m5 | 10 | -0.2252 | [-0.2876, -0.1660] | 100 % | 0.002 |
| Burgers — vRBA, 13 observations propres | vrba_minus_m6 | 10 | -0.2276 | [-0.2982, -0.1643] | 100 % | 0.002 |
| Burgers — vRBA, 13 observations propres | vrba_minus_m7 | 10 | -0.1883 | [-0.2607, -0.1158] | 100 % | 0.002 |
| Burgers — vRBA, 13 observations propres | vrba_minus_vw | 10 | -0.1393 | [-0.2442, -0.0980] | 90 % | 0.021 |
| Burgers — vRBA, 13 observations bruitées | vrba_minus_m5 | 10 | -0.1940 | [-0.3254, -0.1798] | 100 % | 0.002 |
| Burgers — vRBA, 13 observations bruitées | vrba_minus_m6 | 10 | -0.2083 | [-0.3093, -0.1761] | 100 % | 0.002 |
| Burgers — vRBA, 13 observations bruitées | vrba_minus_m7 | 10 | -0.1667 | [-0.2670, -0.1332] | 100 % | 0.002 |
| Burgers — vRBA, 13 observations bruitées | vrba_minus_vw | 10 | -0.1583 | [-0.2509, -0.1243] | 100 % | 0.002 |
| Burgers — vRBA, une observation et bruit fort | vrba_minus_m5 | 10 | -0.1546 | [-0.1930, -0.0253] | 80 % | 0.109 |
| Burgers — vRBA, une observation et bruit fort | vrba_minus_m6 | 10 | -0.1449 | [-0.2000, -0.0517] | 80 % | 0.109 |
| Burgers — vRBA, une observation et bruit fort | vrba_minus_m7 | 10 | -0.1290 | [-0.1772, -0.0015] | 80 % | 0.109 |
| Burgers — vRBA, une observation et bruit fort | vrba_minus_vw | 10 | -0.1126 | [-0.1260, -0.0116] | 80 % | 0.109 |
| Burgers — vRBA, bloc de capteurs manquant | vrba_minus_m5 | 10 | -0.2017 | [-0.2347, -0.1887] | 100 % | 0.002 |
| Burgers — vRBA, bloc de capteurs manquant | vrba_minus_m6 | 10 | -0.2015 | [-0.2392, -0.1742] | 100 % | 0.002 |
| Burgers — vRBA, bloc de capteurs manquant | vrba_minus_m7 | 10 | -0.1762 | [-0.2152, -0.1402] | 100 % | 0.002 |
| Burgers — vRBA, bloc de capteurs manquant | vrba_minus_vw | 10 | -0.1471 | [-0.1681, -0.1003] | 100 % | 0.002 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **18 fichiers** (PNG et PDF).
