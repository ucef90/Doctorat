# Validation indépendante de Burgers — V10

## Résultat

Les 50 modèles Burgers de V09 ont été réévalués sans réentraînement, sur une
grille de 161 temps × 321 positions. Une quadrature Cole–Hopf indépendante
remplace la solution Rusanov pour cette analyse supplémentaire.

| Référence Rusanov | Pas demandé | Écart L2 relatif à Cole–Hopf | Écart maximal |
|---|---:|---:|---:|
| 257 points | 0,0001 | 0,0340964 | 0,285781 |
| 513 points | 0,00005 | 0,0161954 | 0,153759 |
| 1025 points | 0,000025 | 0,0073316 | 0,0696893 |

Ces écarts décroissants documentent la convergence de la référence historique.
Le niveau 257 sous-résout localement le front. L'écart entre seulement deux
résolutions V09 ne constituait donc pas une borne de l'erreur de référence.

Cole–Hopf à 128 et 256 nœuds diffère d'au plus 9,11 × 10⁻¹⁵ sur cette grille.
Vingt points supplémentaires, incluant le voisinage du choc et des temps
précoces, ont été vérifiés par une quadrature adaptative distincte : écart
maximal 4,44 × 10⁻¹⁶. Cela valide numériquement ce domaine de test ; il ne
s'agit pas d'une certification de toute viscosité ni d'une borne continue.

| Variante | L2 médiane V09 | L2 Cole–Hopf, grille fine | Maximum Cole–Hopf |
|---|---:|---:|---:|
| Sans adaptation | 0,29469 | 0,30724 | 1,66270 |
| Global seul | 0,25149 | 0,26523 | 1,48517 |
| Local seul | 0,20907 | 0,22496 | 1,74063 |
| Complet exponentiel | 0,25075 | 0,26369 | 1,80005 |
| Complet quadratique | 0,24898 | 0,26370 | 1,76993 |

Le changement des scores combine une grille d'évaluation plus fine et une
meilleure référence. Aucun des quatre contrastes L2 n'est significatif après
Holm, et aucun des quatre contrastes de maximum non plus. Ce recalcul ne
désigne pas un nouveau gagnant ; il consolide la prudence de V09.

## Formule et implémentation

Pour u(0,x) = −sin(πx), ν > 0 et x dans [−1,1], poser
φ₀(x) = exp[−cos(πx)/(2πν)]. La transformation u = −2ν ∂x log φ
ramène Burgers à l'équation de la chaleur. Les symétries de la solution
périodique imposent les conditions u(t,−1) = u(t,1) = 0.

Après changement de variable dans le noyau de chaleur, avec
y = x − 2√(νt) z, le champ est le rapport

u(t,x) = − ∫ exp(−z²) sin(πy) exp[−cos(πy)/(2πν)] dz
          / ∫ exp(−z²) exp[−cos(πy)/(2πν)] dz.

Le module NumPy `src/recoa_pinn/burgers_reference.py` évalue ce rapport par
Gauss–Hermite. Les masses sont normalisées dans le domaine logarithmique.
La condition initiale est évaluée directement. L'implémentation est écrite
dans ce dépôt ; elle n'est pas une nouvelle solution analytique revendiquée.
La représentation intégrale de ce problème et son calcul par Hermite sont
documentés par [Burkardt, burgers_exact](https://people.sc.fsu.edu/~jburkardt/f77_src/burgers_exact/burgers_exact.html),
qui renvoie à Basdevant et al., *Computers & Fluids* 14(1), 23–41 (1986).

## Correction du cache

Le cache de `BurgersProblem.reference_at` utilisait seulement le nombre de
points. Un appel ultérieur au même objet avec un nouveau dt conservait donc
l'ancienne référence. Il utilise maintenant le couple (nx, dt). Un test
spécifique vérifie qu'un changement de dt relance effectivement le solveur.
V09 utilisait un nouvel objet et une nouvelle résolution pour son raffinement :
ce défaut n'invalide pas son contrôle 257/513, mais gênait les futures études
de convergence temporelle à résolution spatiale fixe.

Le choix Cole–Hopf est explicite (`problem.reference_method: cole_hopf`).
Le défaut historique Rusanov reste disponible pour reproduire les archives.
Le module refuse Cole–Hopf si le domaine spatial ou le temps initial ne
correspond pas au problème dérivé. Avec ce choix, les observations synthétiques
et l'évaluation utilisent la même solution Cole–Hopf.

## Audit des pertes bruitées

Dans `component_losses_from_residuals`, une composante portant un multiplicateur
local reçoit mean((λr)²), alors qu'une composante data sans ce multiplicateur
utilise la perte configurée, éventuellement Huber. Ainsi, les anciens essais
vRBA sous bruit et leurs comparateurs Huber ne permettaient pas d'attribuer
le gain à la seule attention. Même dans sa partie quadratique, Huber inclut
un facteur 1/2 qui change l'échelle relative des composantes.

La nouvelle campagne fixe **MSE dans tous les bras** et utilise Cole–Hopf
pour les cibles. Les résultats historiques sont conservés et signalés comme
comparaisons de recettes complètes, avec ce facteur de confusion. Les
ablations V09 sans observations ne sont pas affectées par ce point.

## Reproduction

```bash
python -m pip install -e '.[dev]' scipy
PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/validate_burgers_reference.py --output outputs/reference_v10_reproduction
```

Le script refuse un dossier de sortie existant. Il sauvegarde erreurs par
germe, statistiques, empreintes des modèles, environnement, champs numériques
et figures. Le résultat V10 est dans `outputs/reference_v10_analysis/`.
