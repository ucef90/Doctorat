# Baseline VW-PINN sur backbone commun

## Objectif scientifique

Ce baseline répond à une objection essentielle : l'amélioration de M7 pourrait
simplement reproduire une correction de densité déjà couverte par les
**Volume-Weighted PINNs (VW-PINNs)**. Il faut donc comparer les mécanismes dans
le même code, avec les mêmes réseaux, points initiaux, budgets, germes et
métriques.

La référence primaire est : J. Song, W. Cao, F. Liao et W. Zhang,
*VW-PINNs: A volume weighting method for PDE residuals in physics-informed
neural networks*, Acta Mechanica Sinica 41, 324140 (2025),
DOI: 10.1007/s10409-024-24140-x ; prépublication arXiv:2401.06196.

## Formulation implémentée

Soient les points de collocation non uniformes

\[
z_i \in \Omega, \qquad i=1,\ldots,N.
\]

Les coordonnées sont ramenées dans l'hypercube unité. La densité empirique est
estimée par un noyau gaussien isotrope :

\[
\widehat p_h(z_i)
=\frac{1}{N}\sum_{j=1}^{N}
\exp\!\left(-\frac{\|z_i-z_j\|_2^2}{2h^2}\right).
\]

Le facteur constant du noyau est omis car il s'annule lors de la normalisation.
Le volume local est approché par :

\[
V_i \propto \frac{1}{\widehat p_h(z_i)}.
\]

La perte VW est :

\[
\mathcal L_{f,\mathrm{VW}}
=\frac{\sum_i V_i^2 r_\theta(z_i)^2}{\sum_i V_i^2}.
\]

Dans le code, le vecteur transmis à la moyenne pondérée vaut donc :

\[
w_i=\frac{N V_i^2}{\sum_j V_j^2},
\qquad \frac{1}{N}\sum_i w_i r_i^2
=\mathcal L_{f,\mathrm{VW}}.
\]

Sans largeur de bande explicite, le baseline adopte la règle reproductible de
Scott :

\[
h=N^{-1/(d+4)}.
\]

La largeur peut être fixée par `adaptation.vw_bandwidth` ou multipliée par
`adaptation.vw_bandwidth_scale`. Une analyse de sensibilité est requise avant
publication.

## Deux variantes nécessaires

| Code | Résidu physique | Poids entre composantes | Rôle |
|---|---|---|---|
| `vw` | volume KDE | fixes | baseline externe conceptuel |
| `vwca` | volume KDE | contrôleur adaptatif M5/M7 | comparaison mécanistique avec M7 |

`vwca` ne correspond pas à une méthode revendiquée par l'article original. Elle
sert uniquement de contrôle : M7 et VW-CA ont le même contrôleur global, mais
M7 utilise la probabilité de proposition connue tandis que VW-CA ré-estime la
densité sur le lot réalisé.

## Ce qui est fidèle et ce qui ne l'est pas

Éléments reproduits :

- prise en compte de toutes les coordonnées du domaine ;
- estimation KDE de la densité des points ;
- volume inverse de la densité ;
- carré du volume dans la perte quadratique ;
- association à un échantillonnage résiduel adaptatif.

Éléments volontairement harmonisés pour la comparaison contrôlée :

- architecture du réseau ;
- conditions imposées par pénalisation, et non par transformation dure ;
- optimiseur Adam sans phase L-BFGS ;
- stratégie exacte de rééchantillonnage ;
- largeur de bande par défaut ;
- nombre de points et budget d'entraînement.

Les résultats doivent donc être présentés comme une **implémentation
common-backbone du mécanisme VW**, et non comme une reproduction numérique
exacte des tableaux de Song et al.

## Différence conceptuelle avec M7

M7 connaît la proposition discrète `q` utilisée pour tirer les nouveaux points
et applique le rapport cible/proposition exact `1/(Nq_i)` au moment du tirage.
VW estime après coup la densité géométrique du lot par KDE. M7 est exact pour la
population candidate finie, mais utilise un tirage avec remise et conserve des
poids historiques lors d'un rafraîchissement partiel. VW fonctionne avec un lot
quelconque, mais introduit un biais et une sensibilité dus à l'estimation de
densité et à la largeur de bande.

## Critères d'interprétation

Une conclusion favorable à M7 exige au minimum :

1. une différence appariée M7–VW-CA dont l'IC bootstrap à 95 % exclut zéro ;
2. un résultat cohérent sur dix germes, pas un seul meilleur run ;
3. une sensibilité raisonnable à la largeur de bande VW ;
4. un coût supplémentaire déclaré ;
5. aucune revendication de nouveauté pour l'idée générale de corriger une
   densité de collocation non uniforme.

Si VW ou VW-CA égale M7, le résultat est scientifiquement utile : il montre que
le mécanisme déterminant est la correction de mesure, et non le choix particulier
de l'estimateur M7.
