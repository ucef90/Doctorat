# Rapport automatique — article1_vrba_pilot

## Complétude

- Exécutions réussies : **18/18**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers — pilote vRBA sur backbone commun | m0 | 3/3 | 0.6188 [0.5962, 0.7441] | 0 | 1.77 |
| Burgers — pilote vRBA sur backbone commun | m5 | 3/3 | 0.7394 [0.6801, 0.8191] | 0.0922 | 1.83 |
| Burgers — pilote vRBA sur backbone commun | m6 | 3/3 | 0.7325 [0.6848, 0.8214] | 0.0946 | 1.80 |
| Burgers — pilote vRBA sur backbone commun | m7 | 3/3 | 0.6923 [0.6380, 0.7977] | 0.0930 | 1.81 |
| Burgers — pilote vRBA sur backbone commun | vw | 3/3 | 0.6432 [0.6290, 0.7495] | 0 | 1.77 |
| Burgers — pilote vRBA sur backbone commun | vrba | 3/3 | 0.5424 [0.5404, 0.6519] | 1.80e-04 | 2.05 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers — pilote vRBA sur backbone commun | vrba_minus_m0 | 3 | -0.0804 | [-0.1078, -0.0312] | 100 % | 0.250 |
| Burgers — pilote vRBA sur backbone commun | vrba_minus_m5 | 3 | -0.1373 | [-0.1970, -0.0825] | 100 % | 0.250 |
| Burgers — pilote vRBA sur backbone commun | vrba_minus_m6 | 3 | -0.1488 | [-0.1901, -0.0986] | 100 % | 0.250 |
| Burgers — pilote vRBA sur backbone commun | vrba_minus_m7 | 3 | -0.1416 | [-0.1500, -0.0453] | 100 % | 0.250 |
| Burgers — pilote vRBA sur backbone commun | vrba_minus_vw | 3 | -0.0943 | [-0.1047, -0.0725] | 100 % | 0.250 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **12 fichiers** (PNG et PDF).
