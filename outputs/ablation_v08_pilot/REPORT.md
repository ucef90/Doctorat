# Ablations vRBA — bilan descriptif

Pilote exploratoire : aucune conclusion confirmatoire ni sélection de variante.

| Variante | Réussites/total | L2 médiane | Maximum médian | q95 médian | q99 médian | Temps médian (s) |
|---|---:|---:|---:|---:|---:|---:|
| full_exp | 3/3 | 0.542375 | 0.919053 | 0.682318 | 0.827950 | 2.133970 |
| full_quad | 3/3 | 0.548454 | 0.959835 | 0.691665 | 0.867861 | 1.973053 |
| global_only | 3/3 | 0.619423 | 1.037063 | 0.800641 | 0.998341 | 2.020798 |
| local_only | 3/3 | 0.540148 | 0.918927 | 0.680457 | 0.827828 | 1.804224 |
| neither | 3/3 | 0.618803 | 1.036582 | 0.800133 | 0.997878 | 1.619480 |

Les quantiles décrivent les points de grille, pas l'incertitude entre germes.
Les temps pilotes ne constituent pas un profilage CPU/GPU contrôlé.
