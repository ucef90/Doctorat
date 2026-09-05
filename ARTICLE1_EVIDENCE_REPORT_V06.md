# Article 1 — état consolidé des preuves, version 0.6

> Archive historique : la synthèse courante, incluant le baseline vRBA et ses
> campagnes à dix germes, est `ARTICLE1_EVIDENCE_REPORT_V07.md`.

Date : 4 septembre 2026

## Décision scientifique

Les expériences ne soutiennent ni le titre affirmatif initial
*Reference-Set Decoupled Co-Adaptive Training...*, ni une revendication selon
laquelle M6 ou M7 serait universellement supérieure.

Elles soutiennent en revanche une contribution empirique plus solide :

> **La collocation résiduelle modifie la mesure utilisée par le contrôleur ;
> une correction explicite peut réduire ce décalage, mais son effet sur la
> précision dépend de l'EDP, des données, du contrôleur et de la manière dont la
> densité est corrigée.**

Le dépôt contient actuellement **875 entraînements réussis**, sans run échoué,
et **27 tests automatisés réussis**. Les nombres incluent les pilotes,
criblages, ablations, campagnes confirmatoires et profils de coût ; toutes les
cellules ne doivent donc pas être assimilées à des réplications confirmatoires.

## 1. Méthodes effectivement comparées

| Méthode | Échantillonnage | Perte physique | Poids des composantes |
|---|---|---|---|
| M0 | uniforme | moyenne standard | fixes |
| M1 | uniforme | moyenne standard | adaptatifs |
| M3 | résiduel | moyenne empirique adaptative | fixes |
| M5 | résiduel | moyenne empirique adaptative | adaptatifs sur le même lot |
| M6 | résiduel | moyenne empirique adaptative | adaptatifs sur une référence fixe |
| M7U | résiduel avec remise | non corrigée | adaptatifs |
| M7 | résiduel avec remise | Hansen–Hurwitz `1/(Nq_i)` | adaptatifs |
| VW | résiduel | volume inverse KDE au carré | fixes |
| VW-CA | résiduel | volume inverse KDE au carré | adaptatifs |

VW est une implémentation du mécanisme central de
[Song et al.](https://doi.org/10.1007/s10409-024-24140-x) sur notre backbone
commun. Elle ne reproduit pas exactement leur architecture, leurs contraintes
dures ni leur séquence Adam–L-BFGS. VW-CA est notre contrôle mécanistique ; ce
n'est pas une méthode attribuée à Song et al.

## 2. Résultat M5–M6 : le découplage fixe ne suffit pas

Sur Burgers long, la concentration de l'échantillonneur et l'écart du gradient
physique sont corrélés positivement dans les dix germes. Le couplage est donc
mesurable. En revanche, M5 n'est pas plus oscillante que le contrôle uniforme de
manière reproductible et M6 ne réduit significativement ni l'erreur ni les
oscillations.

La différence M6−M5 d'erreur L2 vaut `−0,0291`, IC bootstrap 95 %
`[−0,1208 ; +0,1678]`. Les cardinalités et les évaluations du résidu sont
identiques. L'hypothèse « une référence fixe stabilise généralement M5 » est
donc réfutée dans le domaine testé.

## 3. Résultat M7–M7U : la correction agit réellement

Sur Burgers long, M7 réduit face à M7U l'écart logarithmique moyen du gradient
physique de `−0,4351`, IC 95 % `[−0,6182 ; −0,2520]`, avec 10/10 germes
favorables. Ce contrôle élimine l'explication « le bénéfice vient seulement du
tirage avec remise ».

Dans les quatre régimes Burgers à données difficiles, M7 réduit l'erreur face à
M7U :

| Régime | Δ M7−M7U, médiane [IC 95 %] |
|---|---:|
| 13 observations propres | −0,0483 [−0,0662 ; −0,0300] |
| 13 observations bruitées et aberrantes | −0,0482 [−0,0812 ; −0,0247] |
| Une observation, bruit hétéroscédastique fort | −0,0229 [−0,0338 ; −0,0073] |
| Bloc de capteurs manquant | −0,0360 [−0,0503 ; −0,0268] |

## 4. Comparaison externe M7–VW sur plusieurs EDP

Une différence négative favorise M7.

| EDP | L2 M7 | L2 VW | L2 VW-CA | Δ M7−VW [IC 95 %] | Δ M7−VW-CA [IC 95 %] |
|---|---:|---:|---:|---:|---:|
| Burgers long | 0,4410 | 0,4350 | 0,5313 | +0,0291 [−0,0884 ; +0,0941] | −0,1414 [−0,2757 ; +0,0144] |
| Allen–Cahn | 0,1081 | 0,0912 | 0,0994 | +0,0006 [−0,0419 ; +0,0309] | −0,0007 [−0,0422 ; +0,0146] |
| Ondes | 0,3057 | 0,2825 | 0,3146 | +0,0280 [+0,0199 ; +0,0483] | −0,0026 [−0,0154 ; +0,0037] |
| Helmholtz calibrée | 0,1006 | 0,1096 | 0,0941 | −0,0181 [−0,0235 ; −0,0112] | −0,0003 [−0,0044 ; +0,0031] |

Le premier criblage Helmholtz, où toutes les erreurs dépassaient 1, a été
écarté de cette synthèse. Une configuration solvable a été définie sans regarder
les méthodes adaptatives : mode `(1,1)`, nombre d'onde `k=1`, réseau 4×48,
1 500 étapes. M0 y atteint une erreur médiane de `0,1120` sur dix germes.

Lecture : M7 bat VW sur Helmholtz calibrée ; VW bat M7 sur l'équation des ondes ;
Burgers et Allen–Cahn ne permettent pas de les départager. Il n'existe donc pas
de classement universel.

## 5. Données rares et bruitées face à VW

| Régime Burgers | L2 M7 | L2 VW | L2 VW-CA | Δ M7−VW [IC 95 %] | Δ M7−VW-CA [IC 95 %] |
|---|---:|---:|---:|---:|---:|
| 13 mesures propres | 0,5281 | 0,5066 | 0,5717 | +0,0229 [−0,0099 ; +0,0693] | −0,0324 [−0,0685 ; −0,0121] |
| 13 mesures bruitées | 0,5527 | 0,5229 | 0,5740 | +0,0090 [−0,0255 ; +0,0522] | −0,0285 [−0,0562 ; −0,0078] |
| Une mesure, bruit fort | 0,5776 | 0,5457 | 0,6097 | +0,0284 [−0,0295 ; +0,0433] | −0,0316 [−0,0481 ; −0,0182] |
| Bloc manquant | 0,5287 | 0,4924 | 0,5391 | +0,0363 [−0,0031 ; +0,0903] | −0,0245 [−0,0367 ; −0,0146] |

Au réglage KDE par défaut, M7 bat VW-CA dans les quatre régimes, mais ne bat
jamais VW à poids fixes. Le contrôleur co-adaptatif semble donc interagir
défavorablement avec la pondération volumique KDE. C'est une hypothèse issue des
résultats, pas encore une preuve causale complète.

## 6. Sensibilité du baseline VW

Le choix de largeur KDE est déterminant sur Burgers bruité :

| h/Scott | L2 VW | L2 VW-CA | Δ M7−VW [IC 95 %] | Δ M7−VW-CA [IC 95 %] |
|---:|---:|---:|---:|---:|
| 0,5 | 0,4742 | 0,5412 | +0,0710 [+0,0161 ; +0,1165] | −0,0102 [−0,0323 ; +0,0364] |
| 1,0 | 0,5229 | 0,5740 | +0,0090 [−0,0255 ; +0,0522] | −0,0285 [−0,0562 ; −0,0078] |
| 2,0 | 0,5282 | 0,5716 | +0,0150 [−0,0478 ; +0,0669] | −0,0330 [−0,0568 ; −0,0043] |

À `0,5×Scott`, VW bat significativement M7 et M7 ne bat plus VW-CA. Sur les
ondes, VW bat M7 aux trois largeurs tandis que M7 et VW-CA restent
indistinguables. Toute conclusion qui ne montrerait que `1×Scott` serait donc
fragile.

## 7. Coût

Le profilage CPU séquentiel dédié donne pour M7 un surcoût médian de `+10,5 %`
face à M5, `+7,2 %` face à M6 et `+4,9 %` face à M7U, à budget égal en
évaluations du résidu.

Pour `N=256`, chaque run VW de 600 étapes réalise `1 638 400` distances KDE
deux-à-deux, en plus des évaluations du résidu. La correction M7 est linéaire
après calcul de la proposition connue, alors que la KDE dense est quadratique
en `N`. Les temps observés à petite taille restent proches ; un profilage
séquentiel par taille et sur GPU est nécessaire avant toute revendication de
scalabilité.

## 8. Revendications permises et interdites

Revendications soutenues :

1. M5 présente un couplage distribution–diagnostic mesurable.
2. M6 ne produit pas de stabilisation générale dans le protocole étudié.
3. M7 réaligne fortement le gradient physique sur Burgers.
4. M7 améliore M7U dans quatre régimes de données difficiles.
5. Le choix exact de correction et son interaction avec le contrôleur comptent.
6. VW, M7 et VW-CA ont chacun des domaines favorables et défavorables.

Revendications interdites :

1. M6 ou M7 est universellement meilleure.
2. L'importance sampling ou la correction d'une collocation non uniforme est
   une invention de ce projet.
3. M7 bat l'état de l'art : VW à poids fixes l'égale ou la dépasse souvent.
4. Les résultats actuels démontrent quoi que ce soit sur les plasmas de tokamak.
5. La campagne publique équivaut à une revue exhaustive Scopus/Web of Science.

## 9. Positionnement recommandé de l'article

Titre anglais :

> **When Does Measure Correction Help Co-Adaptive Physics-Informed Neural Networks? A Controlled Study of Fixed References, Exact Proposal Reweighting, and KDE Volume Weighting**

Titre français :

> **Quand la correction de mesure améliore-t-elle les réseaux de neurones informés par la physique co-adaptatifs ? Étude contrôlée des références fixes, de la repondération exacte et de la pondération volumique par KDE**

La contribution centrale est une **étude causale et comparative des
interactions**, avec résultats positifs, nuls et négatifs. C'est moins
spectaculaire qu'une prétendue nouvelle méthode universelle, mais beaucoup plus
défendable scientifiquement.

## 10. Travail restant avant soumission

1. reproduire le protocole VW original avec contraintes dures et Adam–L-BFGS,
   ou déclarer explicitement que seule la variante common-backbone est comparée ;
2. ajouter au moins un second baseline moderne indépendant, idéalement vRBA ou
   BRDR/joint weighting-sampling ;
3. profiler M5/M7/VW/VW-CA séquentiellement pour plusieurs `N` et sur GPU ;
4. pré-enregistrer les hypothèses finales avant tout nouveau benchmark ;
5. faire relire la formulation de nouveauté par un spécialiste PINN ;
6. rédiger le manuscrit en séparant résultats confirmatoires et exploratoires.
