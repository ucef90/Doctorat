# Rapport automatique — article1_vw_pilot

## Complétude

- Exécutions réussies : **18/18**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — pilote M7 contre VW | m5 | 3/3 | 0.7394 [0.6801, 0.8191] | 0.0922 | 1.39 |
| Burgers — pilote M7 contre VW | m6 | 3/3 | 0.7325 [0.6848, 0.8214] | 0.0946 | 1.70 |
| Burgers — pilote M7 contre VW | m7u | 3/3 | 0.7389 [0.6729, 0.8197] | 0.0916 | 1.42 |
| Burgers — pilote M7 contre VW | m7 | 3/3 | 0.6923 [0.6380, 0.7977] | 0.0930 | 2.00 |
| Burgers — pilote M7 contre VW | vw | 3/3 | 0.6432 [0.6290, 0.7495] | 0 | 2.07 |
| Burgers — pilote M7 contre VW | vwca | 3/3 | 0.7094 [0.6631, 0.8024] | 0.0952 | 1.82 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — pilote M7 contre VW | m7_minus_m5 | 3 | -0.0372 | [-0.0470, 0.0042] | 67 % | 1.000 |
| Burgers — pilote M7 contre VW | m7_minus_m7u | 3 | -0.0232 | [-0.0465, 0.0026] | 67 % | 1.000 |
| Burgers — pilote M7 contre VW | m7_minus_vw | 3 | 0.0472 | [-0.0595, 0.0775] | 33 % | 1.000 |
| Burgers — pilote M7 contre VW | m7_minus_vwca | 3 | -0.0170 | [-0.0332, 0.0077] | 67 % | 1.000 |
| Burgers — pilote M7 contre VW | vwca_minus_vw | 3 | 0.0395 | [-0.0263, 0.0945] | 33 % | 1.000 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **12 fichiers** (PNG et PDF).
