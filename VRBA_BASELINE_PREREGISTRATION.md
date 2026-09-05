# Pré-enregistrement du baseline vRBA sur backbone commun

Date de gel du protocole : **5 septembre 2026**, avant toute exécution vRBA.

## 1. Objectif

Ajouter un baseline moderne indépendant afin de comparer M7 à une méthode qui
assume explicitement un objectif adaptativement biaisé, au lieu de corriger
l'échantillonnage pour retrouver la mesure uniforme.

La méthode est enregistrée sous le nom `vrba` dans le dépôt. Elle constitue une
**implémentation PyTorch sur backbone commun** de la pondération vRBA, et non une
réplication exacte des expériences JAX publiées.

Sources primaires gelées :

- Toscano et al., *A Variational Framework for Residual-Based Adaptivity in
  Neural PDE Solvers and Operator Learning*, npj Artificial Intelligence, 2026,
  DOI `10.1038/s44387-026-00084-4` ;
- dépôt officiel `jdtoscano94/NABLA-SciML`, dossier
  `vRBA_variational_residual_based_attention_PINNs_Operator_learning`.

## 2. Variante retenue avant expérimentation

La variante principale utilise :

- le potentiel exponentiel `Phi(r)=exp(r)` ;
- l'importance weighting, adapté à l'optimiseur Adam ;
- des multiplicateurs locaux persistants pour chaque composante disponible
  (`physics`, `initial`, `boundary`, `data`) ;
- le mécanisme d'auto-équilibrage global décrit dans l'annexe B de l'article ;
- des ensembles d'entraînement fixes, de même cardinalité que les autres
  méthodes du backbone commun.

Pour un vecteur de résidus absolus `r` à l'itération `k`, la température est

```math
epsilon_k = c\,\max_i r_i / \log(k+2).
```

Le score exponentiel est calculé sous une forme numériquement stable :

```math
q_i / \max_j q_j = \exp((r_i-\max_j r_j)/epsilon_k).
```

La cible locale et le multiplicateur sont ensuite

```math
a_i^k = phi\,(q_i/\max q) + (1-phi),
```

```math
lambda_i^{k+1}=gamma_k lambda_i^k + eta\,a_i^k,
\qquad
gamma_k=1-eta/lambda_{max,k}.
```

La perte locale d'une composante est

```math
L_alpha = mean[(lambda_{alpha,i} r_{alpha,i})^2].
```

Le poids global de la physique reste fixé à `m_physics=1`. Pour les autres
composantes, les normes de gradients sont lissées puis les poids sont ajustés
vers le rapport `||grad L_physics|| / ||grad L_alpha||`.

## 3. Hyperparamètres gelés

| Paramètre | Valeur principale | Origine |
|---|---:|---|
| potentiel | `exponential` | expérience vRBA publiée |
| `eta` | `0.01` | Table 5 / code officiel |
| `phi` | `0.8` | Table 5, potentiel exponentiel |
| `c` température | `1.0` | code officiel |
| `lambda_max0` | `10` | Table 5 |
| `lambda_cap` | `20` | Table 5 |
| itérations par palier | `50000` | Table 5 |
| mémoire EMA gradients | `0.99` | Table 5 |
| mémoire EMA poids globaux | `0.99975` | Table 5 |
| multiplicateur local initial | `0.1*lambda_max0 = 1` | Algorithme 1 |

Les garde-fous numériques `1e-12` et les bornes globales `[1e-6, 1e6]` ne
modifient pas le mécanisme théorique ; ils empêchent uniquement les divisions
par zéro et les valeurs non finies.

## 4. Ce qui est contrôlé

Pour comparer `vrba` à M0, M5, M6, M7 et VW :

- même initialisation pour un même germe ;
- même MLP, activation, précision et optimiseur ;
- même nombre d'étapes et même taux d'apprentissage ;
- mêmes points initiaux, de bord et de collocation ;
- même nombre de résidus physiques utilisés par mise à jour ;
- même grille de test, jamais utilisée pour l'entraînement ;
- ensembles d'audit fixes et disjoints ;
- résultats exploratoires et confirmatoires séparés.

## 5. Écarts avec la reproduction officielle

Cette comparaison contrôlée n'utilise pas :

- JAX/Flax ;
- les Fourier features et l'imposition dure des conditions ;
- le grand réservoir de 25 600 à 200 000 points des démonstrations officielles ;
- SSBroyden après Adam ;
- les durées de 300 000 itérations des expériences originales.

Elle teste donc le **mécanisme vRBA à environnement égal**. Une réplication
officielle séparée devra être étiquetée comme telle et ne pourra pas être
confondue avec ce benchmark.

## 6. Hypothèses pré-enregistrées

1. `vrba` doit terminer sans valeur non finie et produire des multiplicateurs
   locaux non uniformes sur les problèmes non triviaux.
2. L'objectif exponentiel devrait davantage réduire l'erreur maximale que M0,
   mais aucune supériorité universelle en erreur relative L2 n'est postulée.
3. M7 et vRBA devraient présenter des domaines favorables différents : M7 vise
   l'objectif uniforme corrigé, vRBA vise volontairement un objectif incliné.
4. Le surcoût temporel vRBA sera rapporté, sans modifier le budget pour favoriser
   une méthode.

## 7. Pilote bloquant

Le pilote comporte trois germes (`11`, `22`, `33`) sur Burgers rapide, avec
`m0`, `m5`, `m6`, `m7`, `vw` et `vrba`, soit 18 exécutions.

Critères pour autoriser la campagne longue :

- 18/18 exécutions réussies ;
- pertes, gradients, multiplicateurs et métriques finaux tous finis ;
- cardinalités et budget d'optimisation inchangés ;
- même germe donnant exactement les mêmes métriques et paramètres ;
- génération automatique du rapport et des contrastes appariés.

Une modification des hyperparamètres après ce pilote sera traitée comme une
analyse de sensibilité exploratoire, jamais comme un remplacement silencieux du
réglage principal.

