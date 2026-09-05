# Revue bibliographique structurée — adaptation des PINNs, 2025–2026

Date de dernière recherche et mise à jour expérimentale : 5 septembre 2026

## Périmètre et méthode

Question : les travaux 2025–2026 combinent-ils pondération adaptative, collocation adaptative ou découplage des distributions, et isolent-ils le biais produit lorsqu’un contrôleur global et un échantillonneur utilisent les mêmes points ?

Familles de requêtes utilisées :

1. `physics-informed neural networks adaptive loss weighting adaptive sampling 2025` ;
2. `fixed reference set physics-informed neural networks` ;
3. `decoupled adaptive sampling loss weighting PINN` ;
4. `residual-based adaptive gradient loss weighting PINN 2026` ;
5. `PINN adaptive loss weights fixed validation set collocation residual` ;
6. `PINN loss weighting held-out collocation points adaptive sampling` ;
7. `physics informed neural network bilevel loss weights validation set` ;
8. recherches exactes des titres et recherche arrière dans les bibliographies.

Critères d’inclusion : PINNs, article ou prépublication scientifique, pondération/collocation adaptative ou effet d’une distribution non uniforme, publication 2025–2026 ou antécédent directement indispensable.

Critères d’exclusion : billets de blog, pages d’agrégation sans texte primaire, méthodes sans PINN, applications ne modifiant ni pondération ni échantillonnage, doublons. L’article OS-ARL annoncé dans un volume 2027 est signalé mais exclu de la fenêtre principale.

Limite : la recherche publique ne donne pas accès à l’exhaustivité de Scopus et Web of Science. Il s’agit donc d’une revue systématique ciblée et reproductible du corpus public, pas d’une garantie d’exhaustivité mondiale.

## Corpus directement pertinent

| Travail | Année | Apport pertinent | Conséquence pour ReCoA-PINN |
|---|---:|---|---|
| [Nabian, Gladstone et Meidani, importance sampling](https://arxiv.org/abs/2104.12325) | 2021 | Introduit l'échantillonnage d'importance pour accélérer l'entraînement des PINNs | Antécédent fondamental : ni l'importance sampling ni l'usage d'une proposition guidée par la perte ne sont nouveaux |
| [Song et al., VW-PINNs](https://arxiv.org/abs/2401.06196) | 2024/2025 | Analyse l'ill-conditionnement de la perte sous collocation non uniforme et applique une pondération volumique | Antécédent majeur : le biais de quadrature non uniforme est déjà identifié et corrigé autrement |
| [Torres, Schiefer et Niepert, Adaptive PINNs](https://arxiv.org/abs/2503.18181) | 2025 | Revue des PINNs adaptatifs, benchmarks et efficacité | Confirme la nécessité d’un protocole coût–précision et multi-EDP |
| [Chen, Howard et Stinis, BRDR](https://doi.org/10.1016/j.jcp.2025.114226) | 2025 | Pondération selon la décroissance équilibrée des résidus | La pondération adaptative seule n’est pas nouvelle |
| [Chen, Howard et Stinis, joint weighting and sampling](https://arxiv.org/abs/2511.05452) | 2025 | Combine explicitement pondération et échantillonnage adaptatifs sur quatre benchmarks | Rend impossible une revendication fondée sur la seule combinaison des deux mécanismes |
| [Lin et Chen, causal adaptive sampling](https://doi.org/10.1016/j.physd.2025.134878) | 2025 | Utilise des résidus pondérés pour guider l’échantillonnage causal | Montre que poids et sélection des points sont déjà conçus conjointement |
| [Celaya et al., QR-DEIM](https://arxiv.org/abs/2501.07700) | 2025 | Sélection adaptative de collocation par réduction de modèle | Baseline moderne pour la sélection de points |
| [Lau et al., PINNACLE](https://arxiv.org/abs/2404.07662) | 2024/2025 | Optimise conjointement points de collocation et points expérimentaux | Important pour les expériences à données rares |
| [Visser, PACMANN](https://arxiv.org/abs/2411.19632) | 2026 | Déplace les points de collocation à coût maîtrisé | Baseline d’efficacité et d’adaptation de la géométrie des points |
| [Singh et al., stabilized adaptive loss + collocation](https://arxiv.org/abs/2603.03224) | 2026 | Combine normes de gradient lissées et collocation résiduelle sur Burgers et Allen–Cahn | Très proche de M5 et de notre contrôleur ; comparaison obligatoire |
| [Wu et al., adaptive weighting and collocation](https://doi.org/10.1021/acs.iecr.6c00048) | 2026 | Adaptation jointe pour la modélisation de procédés chimiques | Confirme que l’espace méthodologique est déjà occupé dans les applications |
| [Toscano et al., vRBA](https://www.nature.com/articles/s44387-026-00084-4) | 2026 | Cadre variationnel unifiant plusieurs schémas résiduels adaptatifs | Offre un cadre théorique plus fort pour analyser la mesure effectivement minimisée |
| [Zhao, Xie et Chen, causal attention](https://doi.org/10.1016/j.jcp.2026.115071) | 2026 | Découple une attention causale de l’arrangement des points | Découplage apparenté, mais local et temporel plutôt que contrôleur global sur audit fixe |
| [Yan et al., GW-RAR-PINN](https://doi.org/10.1080/19942060.2026.2679804) | 2026 | Combine modulation par gradient et raffinement résiduel pour les ruptures de barrage | Autre combinaison directe poids–RAR, dans un régime discontinu |

## Réponse à la question de nouveauté

1. **Non nouveau** : utiliser un PINN, équilibrer ses pertes, échantillonner par résidu ou combiner pondération et échantillonnage.
2. **Déjà traité sous une autre forme** : le fait qu’une distribution non uniforme modifie la perte physique, notamment par VW-PINNs.
3. **Candidat distinct dans le corpus examiné** : calculer un contrôleur global des composantes sur une mesure fixe indépendante tout en entraînant les paramètres sur une distribution adaptative.
4. **Mais non validé par nos résultats** : ce découplage fixe n'apporte pas de gain général sur les quatre EDP et les régimes bruités testés.

## Mise à jour après l'implémentation de M7

M7 applique un poids inverse `p_i/q_i=1/(Nq_i)` aux points tirés avec remise
depuis une proposition résiduelle connue. Ce choix restaure, conditionnellement
au bassin candidat, la moyenne uniforme par un estimateur de Hansen–Hurwitz.

Cette idée ne doit pas être présentée comme une invention autonome :

- l'échantillonnage d'importance des PINNs existe au moins depuis Nabian et al. ;
- VW-PINNs corrige déjà les effets d'une collocation non uniforme par des
  volumes estimés avec une densité à noyau ;
- vRBA formalise un objectif adaptatif variationnel et traite explicitement
  l'importance sampling et l'importance weighting ;
- Chen et al. combinent déjà pondération et échantillonnage adaptatifs ;
- Singh et al. combinent normes de gradients lissées et collocation résiduelle,
  soit une configuration très proche de M5.

La différence technique encore défendable de notre protocole est la combinaison
suivante : proposition discrète connue, correction inverse exacte sur le bassin
candidat, renouvellement partiel avec poids mémorisés, contrôleur global des
composantes, témoin M7U apparié, dix germes et tests rares/bruités. La nouveauté
potentielle réside donc surtout dans **l'étude causale contrôlée des interactions**
entre ces mécanismes, pas dans chacun des mécanismes pris séparément.

## Mise à jour après l'implémentation common-backbone de vRBA

Le mécanisme d'importance weighting vRBA a été ajouté sous PyTorch avec les
hyperparamètres de premier ordre publiés, sur les mêmes architectures, germes,
points et budgets d'optimisation que M5, M6, M7 et VW. Cette expérience ne
constitue ni une invention ni une réplication exacte du code JAX officiel :
elle isole le mécanisme sur un backbone commun.

Le résultat modifie fortement le positionnement. vRBA est meilleure en erreur
L2 sur les quatre EDP et les quatre régimes Burgers difficiles, mais elle est
moins bonne en erreur maximale sur Burgers long face à M5/M6 et plus coûteuse.
L'article doit donc distinguer explicitement :

- la restauration d'une mesure cible par M7 ou VW ;
- le découplage du diagnostic global par M6 ;
- l'optimisation volontaire d'une mesure inclinée par vRBA.

Cette comparaison interdit désormais de présenter M6 ou M7 comme état de l'art.
La nouveauté défendable est le dessin expérimental apparié et l'analyse du
classement dépendant de la métrique.

Les nouveaux résultats renforcent ce positionnement : M7 améliore les quatre
régimes Burgers à données difficiles, mais dégrade Allen–Cahn et n'est pas
généralement supérieure sur toutes les EDP. Cette hétérogénéité justifie une
question « quand et pourquoi ? » plutôt qu'une annonce de supériorité universelle.

## Vérification expérimentale face à VW-PINNs

Une implémentation common-backbone du mécanisme VW-PINN a maintenant été ajoutée :
KDE gaussienne sur toutes les coordonnées, volume inverse de la densité et carré
du volume dans la perte physique. Une variante VW-CA utilise en plus le même
contrôleur global que M7. Les différences avec la reproduction originale sont
documentées dans `VW_BASELINE_IMPLEMENTATION.md`.

Les campagnes à dix germes montrent que M7 bat VW sur Helmholtz calibrée, que
VW bat M7 sur l'équation des ondes, et que leurs différences ne sont pas
concluantes sur Burgers long et Allen–Cahn. Dans quatre régimes Burgers à données
difficiles, M7 bat VW-CA au réglage KDE par défaut mais ne bat pas VW à poids
fixes. À `0,5×Scott`, VW bat même M7 sur Burgers bruité. Ces résultats réfutent
une supériorité générale de M7 et confirment que le positionnement doit porter
sur l'interaction entre mesure et contrôleur.

## Positionnement recommandé

La contribution défendable n’est plus « une nouvelle méthode supérieure », mais une étude contrôlée de la question suivante :

> Dans quels régimes un ensemble fixe modifie-t-il réellement la stabilité d’un contrôleur co-adaptatif, et cette stabilité améliore-t-elle la solution plutôt que seulement la trajectoire des poids ?

Pour rendre l'étude publiable, il reste à compléter les baselines VW et vRBA
common-backbone par au moins une reproduction fidèle d'un protocole original,
puis à inclure une stratégie moderne de placement distincte comme PINNACLE,
QR-DEIM ou PACMANN. M7 et vRBA ne doivent pas servir de substituts à tous les
baselines contemporains.
