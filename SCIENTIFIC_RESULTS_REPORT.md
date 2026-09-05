# Rapport de résultats scientifiques — campagne v0.3

Date : 4 septembre 2026

## Décision principale

La campagne met en évidence un **couplage mesurable** entre concentration de l’échantillonnage et écart des gradients, mais elle ne démontre pas que ce couplage produit généralement des oscillations nuisibles, ni que l’ensemble fixe de M6 améliore de façon robuste la précision et la stabilité.

La version actuelle de ReCoA-PINN doit donc être considérée comme une hypothèse expérimentale, pas comme une méthode supérieure validée.

## 1. Burgers long sur dix germes

Configuration : 2 500 étapes, 512 points de collocation, réseau 4×48, germes `11, 22, 33, 44, 55, 66, 77, 88, 99, 111`.

| Méthode | Succès | Erreur L2 médiane | TV des poids / mise à jour | Temps médian | Évaluations du résidu |
|---|---:|---:|---:|---:|---:|
| M1 | 10/10 | 0,3379 | 0,04841 | 23,90 s | 1 319 936 |
| M5 | 10/10 | 0,5007 | 0,04980 | 26,26 s | 1 371 136 |
| M6 | 10/10 | 0,4706 | 0,04872 | 25,24 s | 1 371 136 |

M6 − M5 :

- erreur L2 : médiane `−0,02909`, IC bootstrap 95 % `[−0,12079 ; +0,16783]`, M6 gagne 6/10 ;
- variation des poids : médiane `−0,00109`, IC 95 % `[−0,00374 ; +0,00160]`, M6 gagne 6/10 ;
- aucune des deux différences n’exclut zéro.

Conclusion : M6 présente une tendance médiane favorable, mais aucune supériorité n’est établie.

## 2. Le biais annoncé de M5 existe-t-il ?

Chez M5, la corrélation médiane entre concentration de l’échantillonneur et écart logarithmique du gradient physique vaut `0,497`. Elle est positive dans les dix germes. Le couplage distribution–diagnostic est donc observable.

En revanche :

- la variation des poids M5 − M1 vaut `−0,00076` par mise à jour ;
- son IC 95 % est `[−0,00383 ; +0,00246]` ;
- M5 n’est pas plus oscillant que M1 de manière reproductible ;
- l’écart temporel moyen entraînement–audit est même inférieur pour M5 dans cette configuration.

Conclusion : **le couplage existe, mais son caractère nuisible n’est pas démontré**. L’hypothèse H1, telle qu’elle était formulée, n’est pas confirmée.

## 3. M6 réduit-il le phénomène ?

Sur Burgers long, M6 ne réduit significativement ni l’erreur ni les oscillations. Son mécanisme ne peut donc pas encore être qualifié de stabilisateur robuste.

M5 et M6 ont la même cardinalité de contrôleur et exactement le même nombre d’évaluations du résidu. Le résultat ne peut pas être expliqué par un nombre supplémentaire de points utilisés par M6.

## 4. Persistance sur plusieurs EDP

| EDP | Δ erreur M6−M5, médiane [IC 95 %] | M6 gagne | Δ stabilité M6−M5 [IC 95 %] | Décision |
|---|---:|---:|---:|---|
| Burgers | −0,02909 [−0,12079 ; +0,16783] | 6/10 | −0,00109 [−0,00374 ; +0,00160] | Non concluant |
| Allen–Cahn | +0,00195 [−0,00221 ; +0,00302] | 3/10 | −0,00021 [−0,00130 ; +0,00305] | Non concluant |
| Helmholtz | −0,00581 [−0,02844 ; +0,01441] | 7/10 | ≈ 0 [−0,000000007 ; +0,000000169] | Non concluant |
| Ondes | −0,00149 [−0,00590 ; +0,00226] | 6/10 | −0,00407 [−0,00539 ; −0,00131] | Stabilité favorable uniquement |

La seule amélioration dont l’IC bootstrap n’inclut pas zéro concerne la stabilité sur l’équation des ondes. Le test des signes reste toutefois à `p=0,109` avec dix germes. Le bénéfice n’est donc pas général aux EDP.

Allen–Cahn, Helmholtz et les ondes utilisent des solutions manufacturées ou analytiques. Helmholtz reste sous-entraîné dans ce criblage (`L2 > 1`) ; ce cas doit être recalibré avant toute conclusion définitive sur cette EDP.

## 5. Données rares et bruitées

| Régime Burgers | Observations effectives | Δ erreur M6−M5 [IC 95 %] | Δ stabilité [IC 95 %] | Décision |
|---|---:|---:|---:|---|
| 10 % propres | 13 | −0,00544 [−0,01056 ; +0,01727] | +0,00153 [−0,00215 ; +0,00396] | Non concluant |
| 10 % + bruit 10 % + 5 % aberrants | 13 | −0,00440 [−0,02079 ; +0,00778] | +0,00172 [−0,00268 ; +0,00232] | Non concluant |
| 1 % + bruit hétéroscédastique 20 % | 1 | +0,00230 [−0,01399 ; +0,01488] | −0,00143 [−0,00380 ; +0,00392] | Non concluant |
| Bloc temporel manquant 50 % + bruit corrélé | 64 | −0,00184 [−0,00584 ; +0,00438] | +0,00029 [−0,00317 ; +0,00305] | Non concluant |

Le gain de M6 ne persiste pas de manière statistiquement établie avec des données rares et bruitées.

## 6. Coût

M5 et M6 ont les mêmes budgets de résidu dans toutes les comparaisons principales. Sur Burgers long, M6 prend 25,24 s contre 26,26 s pour M5. Aucun surcoût supérieur à l’objectif de 15 % n’est observé.

Les processus ayant été exécutés en parallèle sur CPU, les différences de temps faibles ne doivent pas être interprétées comme une accélération intrinsèque. Une mesure séquentielle dédiée ou un profilage GPU reste nécessaire pour publier un résultat de performance.

## 7. Ablations

Criblage sur cinq germes, 600 étapes :

| Variante | Erreur L2 médiane | TV poids / mise à jour | Temps médian |
|---|---:|---:|---:|
| A0 — M6, ensemble fixe | 0,6281 | 0,04426 | 2,95 s |
| A1 — M5, lot adaptatif | 0,5986 | 0,04664 | 3,13 s |
| Audit 0,5× | 0,5848 | 0,04267 | 2,87 s |
| Audit Sobol | 0,5864 | 0,04549 | 2,82 s |
| Audit en rotation lente | 0,5943 | 0,04629 | 2,76 s |
| Sans lissage | 0,6758 | 0,21167 | 2,86 s |
| Échantillonneur plus lent | 0,5727 | 0,04405 | 2,89 s |

L’ablation A0–A1 ne soutient pas la causalité prévue : M6 est légèrement plus stable, mais moins précis. Le lissage est en revanche clairement important ; sa suppression multiplie fortement la variation des poids.

## 8. Conséquence pour l’article

Le titre affirmatif initial n’est plus recommandé. Un positionnement scientifiquement honnête serait :

> **Does a Fixed Reference Set Stabilize Co-Adaptive Physics-Informed Neural Networks? A Controlled Multi-Seed and Multi-PDE Study**

En français :

> **Un ensemble de référence fixe stabilise-t-il l’entraînement co-adaptatif des PINNs ? Une étude contrôlée multi-germes et multi-EDP**

Cette reformulation transforme un résultat négatif ou conditionnel en
contribution empirique utile. Le baseline VW-PINN common-backbone et une mesure
de coût M7 ont depuis été ajoutés. Les résultats consolidés et les nouvelles
limites sont décrits dans `ARTICLE1_EVIDENCE_REPORT_V06.md`.
