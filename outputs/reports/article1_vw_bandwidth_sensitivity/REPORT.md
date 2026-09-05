# Rapport automatique — article1_vw_bandwidth_sensitivity

## Complétude

- Exécutions réussies : **120/120**.
- Intervalles : bootstrap apparié/non apparié à **95 %**.
- Une différence négative signifie que la seconde méthode a une valeur plus faible.

## Résultats principaux

| Expérience | Méthode | n | Erreur L2 médiane [Q1, Q3] | Stabilité médiane | Temps médian (s) |
|---|---:|---:|---:|---:|---:|
| Burgers bruité — KDE 0,5×Scott | vw | 10/10 | 0.4742 [0.4564, 0.4950] | 0 | 2.13 |
| Burgers bruité — KDE 0,5×Scott | vwca | 10/10 | 0.5412 [0.5040, 0.5944] | 0.0750 | 2.20 |
| Burgers bruité — KDE 1×Scott | vw | 10/10 | 0.5229 [0.5154, 0.5407] | 0 | 2.14 |
| Burgers bruité — KDE 1×Scott | vwca | 10/10 | 0.5740 [0.5311, 0.6035] | 0.0738 | 2.27 |
| Burgers bruité — KDE 2×Scott | vw | 10/10 | 0.5282 [0.5116, 0.5505] | 0 | 2.13 |
| Burgers bruité — KDE 2×Scott | vwca | 10/10 | 0.5716 [0.5356, 0.6058] | 0.0739 | 2.20 |
| Ondes — KDE 0,5×Scott | vw | 10/10 | 0.2793 [0.2720, 0.2855] | 0 | 2.65 |
| Ondes — KDE 0,5×Scott | vwca | 10/10 | 0.3148 [0.3014, 0.3254] | 0.0742 | 2.73 |
| Ondes — KDE 1×Scott | vw | 10/10 | 0.2825 [0.2735, 0.2886] | 0 | 2.66 |
| Ondes — KDE 1×Scott | vwca | 10/10 | 0.3146 [0.2994, 0.3323] | 0.0728 | 2.65 |
| Ondes — KDE 2×Scott | vw | 10/10 | 0.2833 [0.2753, 0.2870] | 0 | 2.64 |
| Ondes — KDE 2×Scott | vwca | 10/10 | 0.3140 [0.2991, 0.3311] | 0.0729 | 2.68 |

## Contrastes appariés principaux

| Expérience | Contraste | n | Δ erreur L2 médian | IC 95 % | Victoires seconde méthode | p (signe) |
|---|---:|---:|---:|---:|---:|---:|
| Burgers bruité — KDE 0,5×Scott | vwca_minus_vw | 10 | 0.0688 | [0.0153, 0.1072] | 20 % | 0.109 |
| Burgers bruité — KDE 1×Scott | vwca_minus_vw | 10 | 0.0441 | [0.0058, 0.0777] | 20 % | 0.109 |
| Burgers bruité — KDE 2×Scott | vwca_minus_vw | 10 | 0.0505 | [-0.0016, 0.0816] | 20 % | 0.109 |
| Ondes — KDE 0,5×Scott | vwca_minus_vw | 10 | 0.0368 | [0.0223, 0.0501] | 0 % | 0.002 |
| Ondes — KDE 1×Scott | vwca_minus_vw | 10 | 0.0355 | [0.0178, 0.0517] | 0 % | 0.002 |
| Ondes — KDE 2×Scott | vwca_minus_vw | 10 | 0.0330 | [0.0195, 0.0551] | 0 % | 0.002 |

## Fichiers produits

- `data/runs.csv` : une ligne par entraînement ;
- `tables/method_summary.csv` : statistiques par méthode ;
- `tables/paired_summary.csv` : contrastes appariés par germe ;
- `tables/*.tex` : tableaux prêts à intégrer dans l’article ;
- `figures/*.png` et `figures/*.pdf` : figures raster et vectorielles.

## Règle d’interprétation

Un avantage n’est pas déclaré sur la seule base de la médiane. Il faut au minimum un intervalle du contraste ne traversant pas zéro, une majorité de germes cohérente, l’absence de runs manquants et un coût comparable.

Figures créées : **22 fichiers** (PNG et PDF).
