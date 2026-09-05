# Matrice de positionnement scientifique de ReCoA-PINN

État de la vérification : 5 septembre 2026. Cette matrice soutient le positionnement du projet, mais ne permet pas d’affirmer qu’aucun travail mondial n’utilise une idée similaire.

| Travail | Pondération | Échantillonnage | Découplage pertinent | Différence avec ReCoA-PINN |
|---|---|---|---|---|
| Raissi et al. (2019), PINNs | Poids généralement fixés | Collocation standard | Non | Cadre fondateur, sans contrôleur co-adaptatif |
| Wang et al. (2021), gradient pathologies | Équilibrage par gradients | Non central | Non | Traite le déséquilibre des gradients, pas le biais créé par un échantillonneur adaptatif |
| Wu et al. (2023), RAD/RAR-D | Poids globaux non centraux | Résiduel adaptatif | Non | Étudie principalement la sélection des points |
| Hou et al. (2023) | Adaptative | Mouvement adaptatif des points | Couplage | Combine les mécanismes sans utiliser l’ensemble fixe proposé pour le contrôleur global |
| Song et al., VW-PINNs (2024/2025) | Pondération volumique du résidu | Compatible avec des points non uniformes | Corrige explicitement la mesure modifiée | Antécédent critique : le biais des distributions non uniformes est déjà analysé |
| PINNACLE (ICLR 2025) | Allocation adaptative entre types de points | Collocation et données expérimentales | Optimisation conjointe | Plus large sur le budget des points, sans notre audit fixe global |
| Chen, Howard et Stinis (2025) | Adaptative, principalement locale | Adaptatif | Cadre conjoint | Montre que la combinaison existe déjà ; ne constitue donc pas notre nouveauté |
| Singh et al. (2026) | Normes de gradient lissées | Collocation résiduelle | Non identifié comme audit fixe global | Très proche de M5 ; renforce la nécessité de centrer l’article sur M5 contre M6 |
| PACMANN (2026) | Non central | Mouvement adaptatif | Non | Baseline moderne de coût et de placement adaptatif |
| vRBA (2026) | Résidus pondérés par potentiel | Adaptation résiduelle | Cadre variationnel | Explique la mesure adaptative avec un formalisme plus général |
| Zhao, Xie et Chen (2026), Causal Attention | Pondération ponctuelle causale | Compatible avec rééchantillonnage | Poids découplés de la disposition des points | Découplage apparenté, mais objectif temporel et poids locaux différents du contrôleur global par composantes évalué sur audit fixe |
| ReCoA-PINN | Poids globaux des composantes, lissés et bornés | Résiduel avec plancher de couverture | Oui : diagnostics sur ensemble fixe, optimisation sur ensemble adaptatif | Étudie explicitement le biais de rétroaction et mesure simultanément diagnostics adaptatifs et fixes |
| M7 (ce dépôt) | Poids globaux adaptatifs + correction Hansen–Hurwitz | Proposition résiduelle connue, tirage avec remise | Corrige la mesure du même lot au lieu d'utiliser une référence fixe | Distinction technique contrôlée, mais importance sampling et correction de mesure sont antérieurs |
| VW common-backbone (ce dépôt) | Volume KDE du résidu, avec ou sans contrôleur global | Résiduel sans remise | Corrige a posteriori la densité du lot | Baseline mécanistique ; ni nouvelle méthode ni reproduction exacte du protocole publié |
| vRBA common-backbone (ce dépôt) | Multiplicateurs locaux par potentiel + auto-équilibrage global | Points fixes, objectif adaptativement incliné | N'a pas pour but de restaurer la mesure uniforme | Baseline publié réimplémenté en PyTorch à environnement égal ; son principe n'est pas notre nouveauté |

## Sources primaires prioritaires

1. Raissi, Perdikaris et Karniadakis (2019), *Physics-informed neural networks*, Journal of Computational Physics. https://doi.org/10.1016/j.jcp.2018.10.045
2. Wang, Teng et Perdikaris (2021), *Understanding and mitigating gradient flow pathologies in physics-informed neural networks*. https://doi.org/10.1137/20M1318043
3. Wu et al. (2023), *A comprehensive study of non-adaptive and residual-based adaptive sampling for physics-informed neural networks*. https://doi.org/10.1016/j.cma.2022.115671
4. Hou, Li et Ying (2023), *Enhancing PINNs for solving PDEs via adaptive collocation point movement and adaptive loss weighting*. https://doi.org/10.1007/s11071-023-08654-w
5. Chen, Howard et Stinis (2025), *Self-adaptive weighting and sampling for physics-informed neural networks*. https://arxiv.org/abs/2511.05452
6. Singh et al. (2026), *Stabilized Adaptive Loss and Residual-Based Collocation for Physics-Informed Neural Networks*. https://arxiv.org/abs/2603.03224
7. Zhao, Xie et Chen (2026), *Causal attention: Adaptive enforcement of causality in physics-informed neural networks*. https://doi.org/10.1016/j.jcp.2026.115071

## Résultat de la campagne v0.3

Le découplage fixe n’a pas apporté de gain robuste sur Burgers, Allen–Cahn, Helmholtz, les ondes et les régimes de données corrompues. La nouveauté algorithmique candidate n’est donc pas soutenue comme amélioration générale. Le positionnement recommandé devient une étude empirique contrôlée et potentiellement négative.

## Résultat de la campagne v0.6

La comparaison externe réfute toute supériorité générale de M7. M7 bat VW sur
Helmholtz calibrée, tandis que VW bat M7 sur l'équation des ondes et sur Burgers
bruité avec une largeur KDE de `0,5×Scott`. Le signal original de M7 persiste
face au contrôle co-adaptatif VW-CA dans plusieurs régimes, mais il dépend de la
largeur de bande. La nouveauté candidate est donc l'analyse contrôlée de ces
interactions, non une nouvelle famille universellement supérieure.

## Résultat de la campagne v0.7

La variante vRBA common-backbone obtient la meilleure erreur L2 médiane sur les
quatre EDP et quatre régimes de données difficiles, avec des intervalles
appariés favorables face à M5, M6, M7 et VW. Elle dégrade toutefois l'erreur
maximale de Burgers face à M5/M6 et peut coûter jusqu'à environ 82 % de plus que
M5 selon l'EDP. Ce résultat confirme que la contribution propre du projet n'est
pas une domination algorithmique de ReCoA-PINN, mais un protocole contrôlé qui
distingue restauration d'une mesure, estimation géométrique et objectif
variationnel volontairement incliné.

## Formulation prudente de la contribution

Formulation acceptable dans l'état actuel de la revue publique :

> Dans le périmètre public examiné, nous étudions de manière contrôlée comment
> un ensemble de référence fixe, une correction exacte de proposition et une
> pondération volumique KDE se comparent à une attention variationnelle aux
> résidus sur un même backbone. Les résultats montrent des régimes favorables,
> nuls et défavorables selon la métrique, sans supériorité universelle.

Formulation interdite à ce stade :

> Nous sommes les premiers à combiner pondération adaptative et échantillonnage adaptatif.
