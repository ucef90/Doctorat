# Rapport automatique — article1_pilot_automatic

## Complétude

- Exécutions réussies : **15/15**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — pilote automatique | m0 | 3/3 | 0.6188 [0.5962, 0.7441] | 0 | 1.77 |
| Burgers — pilote automatique | m1 | 3/3 | 0.6861 [0.6401, 0.7956] | 0.0932 | 1.98 |
| Burgers — pilote automatique | m3 | 3/3 | 0.6494 [0.6381, 0.7538] | 0 | 1.73 |
| Burgers — pilote automatique | m5 | 3/3 | 0.7394 [0.6801, 0.8191] | 0.0922 | 1.72 |
| Burgers — pilote automatique | m6 | 3/3 | 0.7325 [0.6848, 0.8214] | 0.0946 | 1.67 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — pilote automatique | m1_minus_m0 | 3 | 0.0358 | [-0.0247, 0.1126] | 33 % | 1.000 |
| Burgers — pilote automatique | m3_minus_m0 | 3 | 0.0306 | [-0.0111, 0.0532] | 33 % | 1.000 |
| Burgers — pilote automatique | m6_minus_m5 | 3 | 0.0115 | [-0.0069, 0.0162] | 33 % | 1.000 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **12 fichiers** (PNG et PDF).
