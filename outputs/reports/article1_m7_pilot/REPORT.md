# Rapport automatique — article1_m7_pilot

## Complétude

- Exécutions réussies : **12/12**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — pilote M7 | m5 | 3/3 | 0.7394 [0.6801, 0.8191] | 0.0922 | 1.45 |
| Burgers — pilote M7 | m6 | 3/3 | 0.7325 [0.6848, 0.8214] | 0.0946 | 1.60 |
| Burgers — pilote M7 | m7u | 3/3 | 0.7389 [0.6729, 0.8197] | 0.0916 | 1.66 |
| Burgers — pilote M7 | m7 | 3/3 | 0.6923 [0.6380, 0.7977] | 0.0930 | 1.73 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — pilote M7 | m6_minus_m5 | 3 | 0.0115 | [-0.0069, 0.0162] | 33 % | 1.000 |
| Burgers — pilote M7 | m7_minus_m5 | 3 | -0.0372 | [-0.0470, 0.0042] | 67 % | 1.000 |
| Burgers — pilote M7 | m7_minus_m6 | 3 | -0.0401 | [-0.0534, -0.0073] | 100 % | 0.250 |
| Burgers — pilote M7 | m7_minus_m7u | 3 | -0.0232 | [-0.0465, 0.0026] | 67 % | 1.000 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **12 fichiers** (PNG et PDF).
