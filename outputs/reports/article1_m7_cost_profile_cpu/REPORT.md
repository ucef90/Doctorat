# Rapport automatique — article1_m7_cost_profile_cpu

## Complétude

- Exécutions réussies : **20/20**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers bruité — profilage CPU séquentiel | m5 | 5/5 | 0.6073 [0.6065, 0.6089] | 0.0925 | 2.07 |
| Burgers bruité — profilage CPU séquentiel | m6 | 5/5 | 0.6003 [0.5931, 0.6111] | 0.0943 | 2.13 |
| Burgers bruité — profilage CPU séquentiel | m7u | 5/5 | 0.6179 [0.6075, 0.6236] | 0.0927 | 2.17 |
| Burgers bruité — profilage CPU séquentiel | m7 | 5/5 | 0.5828 [0.5724, 0.5833] | 0.0973 | 2.28 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers bruité — profilage CPU séquentiel | m6_minus_m5 | 5 | -0.0061 | [-0.0142, 0.0022] | 60 % | 1.000 |
| Burgers bruité — profilage CPU séquentiel | m7_minus_m5 | 5 | -0.0261 | [-0.0395, 0.0022] | 80 % | 0.375 |
| Burgers bruité — profilage CPU séquentiel | m7_minus_m6 | 5 | -0.0170 | [-0.0412, 0.0164] | 80 % | 0.375 |
| Burgers bruité — profilage CPU séquentiel | m7_minus_m7u | 5 | -0.0351 | [-0.0403, -0.0172] | 100 % | 0.062 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **12 fichiers** (PNG et PDF).
