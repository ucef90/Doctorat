# Article 1 — bilan scientifique V10

**Youssef EL MOUTEE · 5 septembre 2026 · version de recherche**

## Ce qui a été réalisé

Le dépôt de départ est `ucef90/Doctorat`, branche main, commit V09
`0142311a08c9cd72d05494b6f24dd8949ebe6cd6`. L'historique V06–V09 est conservé.
Cette extension ajoute 560 entraînements terminés sans échec : 200 pour les données difficiles, 200 pour un nombre de pas doublé et 160 pour les baselines sous perte commune. Les 560 modèles finaux ont été rechargés pour recalculer leurs scores. Les paramètres et données de départ sont vérifiés par empreintes ; les 40 modèles vRBA réutilisés dans la comparaison des baselines ne sont pas comptés deux fois.
La suite automatisée a passé 55 tests dans cette session.

## 1. Référence Burgers et contrôle des scores

Une solution Cole–Hopf indépendante a été ajoutée. Les ordres de quadrature
128 et 256 concordent à environ 9,11 × 10⁻¹⁵ sur la grille examinée ; un autre
algorithme de quadrature confirme 20 points à 4,44 × 10⁻¹⁶.
L'ancienne référence Rusanov à 257 points diffère de 3,41 % en L2 relative
et d'au plus 0,28578 localement. À 1025 points, ces écarts baissent à 0,73 %
et 0,06969. Il ne faut donc pas considérer les anciens maxima comme exacts.

Les 50 modèles Burgers V09 ont été réévalués sur une grille fine avec Cole–Hopf.
Le classement des ablations demeure incertain après correction de multiplicité.
Le cache de référence a également été corrigé pour tenir compte du pas de temps.
La validation détaillée est dans `BURGERS_REFERENCE_VALIDATION_V10.md`.

## 2. Données rares, bruitées ou manquantes

Les cinq bras utilisent maintenant la même perte MSE pour les observations.
Cette décision corrige un facteur de confusion des anciennes recettes : avec
une attention locale, vRBA utilisait une perte quadratique pondérée, tandis que
plusieurs comparateurs utilisaient Huber. Les observations et les évaluations
de la nouvelle campagne Burgers reposent sur Cole–Hopf.

Les lignes ci-dessous sont des médianes entre dix germes ; L2 n'est pas un
pourcentage de bonne classification. Les labels désignent respectivement
absence d'adaptation, global seul, local seul, complet exponentiel et complet
quadratique.

| Case | Neither | Global only | Local only | Full exp. | Full quad. |
|---|---:|---:|---:|---:|---:|
| extreme | 0.53812 | 0.53812 | 0.44694 | 0.45883 | 0.47695 |
| sparse_noisy | 0.46306 | 0.46373 | 0.37333 | 0.37603 | 0.41816 |
| sparse_clean | 0.46061 | 0.45779 | 0.38439 | 0.36866 | 0.40329 |
| block_missing | 0.44003 | 0.43793 | 0.34951 | 0.34398 | 0.34288 |

Contrastes passant Holm à 5 %, sur 16 tests L2 et une famille séparée de
16 tests de maximum :

| Case | Metric | Contrast | Paired median difference | Marginal 95% CI | Holm p |
|---|---|---|---:|---|---:|
| block_missing | relative_l2 | full_exp-global_only | -0.06999 | [-0.09386, -0.03466] | 0.03125 |
| extreme | max_abs_error | full_exp-full_quad | -0.06696 | [-0.12910, -0.00587] | 0.03125 |

Le bénéfice du complet face au global seul est établi pour L2 dans le cas
du bloc manquant. Dans le régime extrême, l'exponentiel améliore le maximum
face au quadratique. Les autres contrastes planifiés ne franchissent pas
ce seuil corrigé. Cette absence de preuve n'établit aucune équivalence.

### Comparaisons corrigées avec M5, M6, M7 et VW

160 nouveaux entraînements emploient exactement les configurations de la
campagne de robustesse, avec MSE et cibles Cole–Hopf. Les 40 modèles full_exp
de cette campagne sont réutilisés comme vRBA ; il s'agit de 200 cellules
comparées, dont seulement 160 entraînements supplémentaires.

| Case | M5 | M6 | M7 | VW | vRBA |
|---|---:|---:|---:|---:|---:|
| block_missing | 0.56166 | 0.55393 | 0.53397 | 0.48595 | 0.34398 |
| sparse_clean | 0.58673 | 0.55823 | 0.55471 | 0.49238 | 0.36866 |
| sparse_noisy | 0.57248 | 0.55808 | 0.54189 | 0.50375 | 0.37603 |
| extreme | 0.61185 | 0.60330 | 0.59146 | 0.56037 | 0.45883 |

Contrastes passant Holm dans cette comparaison complémentaire :

| Case | Metric | Contrast | Paired median difference | Marginal 95% CI | Holm p |
|---|---|---|---:|---|---:|
| block_missing | relative_l2 | vrba-m5 | -0.19580 | [-0.24059, -0.18515] | 0.03125 |
| block_missing | relative_l2 | vrba-m6 | -0.19318 | [-0.24042, -0.18069] | 0.03125 |
| block_missing | relative_l2 | vrba-m7 | -0.17172 | [-0.20840, -0.12736] | 0.03125 |
| block_missing | relative_l2 | vrba-vw | -0.13158 | [-0.15465, -0.09959] | 0.03125 |
| sparse_clean | relative_l2 | vrba-m5 | -0.22439 | [-0.32713, -0.15273] | 0.03125 |
| sparse_clean | relative_l2 | vrba-m6 | -0.21344 | [-0.32406, -0.15757] | 0.03125 |
| sparse_clean | relative_l2 | vrba-m7 | -0.17495 | [-0.24497, -0.13279] | 0.03125 |
| sparse_noisy | relative_l2 | vrba-m5 | -0.19789 | [-0.30269, -0.17423] | 0.03125 |
| extreme | relative_l2 | vrba-m5 | -0.13299 | [-0.20818, -0.06938] | 0.03125 |
| extreme | relative_l2 | vrba-m6 | -0.13806 | [-0.20866, -0.11213] | 0.03125 |
| extreme | relative_l2 | vrba-m7 | -0.13349 | [-0.15551, -0.06411] | 0.03125 |

vRBA obtient la plus faible médiane L2 dans les quatre régimes de cette comparaison. Onze contrastes L2 sur seize passent Holm ; aucun contraste de maximum ne passe la correction. Ce résultat étaye un bénéfice global dans les cas testés, sans établir une domination sur les erreurs extrêmes.

Tous les autres contrastes, ainsi que les erreurs maximales, sont conservés
dans `outputs/common_loss_v10_analysis/paired_statistics.csv`. Cette nouvelle
comparaison traite le facteur de confusion Huber/MSE dans les cas testés ;
elle ne transforme pas les résultats antérieurs en confirmations indépendantes.

## 3. Sensibilité au nombre de pas

Les budgets sont doublés : Burgers 5000 pas, Allen–Cahn 1200, Helmholtz
3000, ondes 1200. Aucun autre hyperparamètre d'entraînement n'est ajusté
selon les scores. La comparaison historique à budget initial emploie les
mêmes tenseurs de départ et la même référence d'évaluation, vérifiés par script.

| Case | Neither | Global only | Local only | Full exp. | Full quad. |
|---|---:|---:|---:|---:|---:|
| helmholtz | 0.08717 | 0.01917 | 0.03245 | 0.00523 | 0.02076 |
| allen_cahn | 0.02859 | 0.02873 | 0.02573 | 0.02785 | 0.02291 |
| burgers | 0.30754 | 0.24549 | 0.20305 | 0.25680 | 0.26014 |
| wave | 0.12374 | 0.13976 | 0.02578 | 0.02747 | 0.02652 |

Contrastes passant Holm dans cette campagne :

| Case | Metric | Contrast | Paired median difference | Marginal 95% CI | Holm p |
|---|---|---|---:|---|---:|
| wave | relative_l2 | full_exp-global_only | -0.10001 | [-0.14629, -0.08958] | 0.03125 |
| helmholtz | max_abs_error | interaction | +0.11349 | [+0.08393, +0.13949] | 0.03125 |
| wave | max_abs_error | full_exp-global_only | -0.19593 | [-0.30415, -0.14881] | 0.03125 |

Sur les ondes, le complet reste favorable au global seul pour L2 et le maximum. L'avantage quadratique sur L2 observé à 600 pas en V09 n'est plus établi après Holm à 1200 pas. Pour Helmholtz, le complet exponentiel atteint une médiane L2 de 0,00523, mais les contrastes L2 planifiés ne passent pas Holm. L'interaction positive sur le maximum est un contraste additif ; elle ne signifie pas que le modèle complet est le moins précis.

Les résultats individuels à budget initial et doublé sont fournis dans
`outputs/budget_v10_analysis/budget_changes.csv`. Doubler les pas ne signifie
pas égaliser le temps de calcul entre méthodes. Les temps recueillis sous
parallélisme décrivent le débit de cette campagne, pas une efficacité isolée.

## 4. Ce que devient le premier article

Le titre de travail est : **Adaptive PINNs under Competing Training Measures:
A Controlled Study of Fixed References, Exact Reweighting, KDE Volume
Weighting, and Variational Residual Attention**.

La contribution proposée est une étude contrôlée des interactions et limites,
avec résultats positifs, nuls et défavorables. La supériorité générale de M6
n'est pas démontrée. vRBA reste attribuée à ses auteurs ; ce projet ne revendique
pas son invention. Les campagnes V09–V10 sont exploratoires après connaissance
des résultats antérieurs, même si leurs paramètres ont été figés avant calcul.

Le manuscrit anglais V10 intègre les ablations V09, la validation indépendante,
les campagnes de robustesse et de budget, ainsi que la réserve sur Huber/MSE.
Les résultats historiques restent identifiables et les métriques ne sont pas
mélangées entre références. Le domaine étudié reste synthétique ; aucun résultat
ne valide encore une prédiction ou un contrôle de plasma de tokamak.

## 5. Ce qui reste avant soumission

| Travail | État et condition |
|---|---|
| Référence Burgers indépendante | Réalisé et testé sur le domaine de cette étude |
| Ablations sous données difficiles | 200/200 réalisées et réévaluées |
| Sensibilité au nombre de pas | 200/200 réalisées et réévaluées |
| Tableaux et manuscrit V10 | Produits à partir des sorties vérifiées |
| Comparaison M5/M6/M7/VW sous bruit avec perte commune | 160 nouveaux entraînements et 40 comparateurs vRBA réutilisés, appariement et scores vérifiés |
| Budget de temps égal | À réaliser avant toute revendication d'efficacité en temps ; le budget de pas doublé ne le remplace pas |
| Vérification sur machine indépendante | À réaliser pour consolider la reproductibilité entre machines |
| Relecture scientifique externe | À organiser avec l'encadrement et les coauteurs |
| Revue, auteurs, affiliations et déclarations | À fixer avant mise en forme et soumission |

Une réplication exacte du protocole JAX officiel et un transfert au plasma
sont des extensions distinctes ; ils ne sont pas présentés comme accomplis.
Une publication reste soumise à l'appréciation des évaluateurs scientifiques.

## 6. Références et reproduction

La formulation vRBA et son attribution ont été revérifiées dans
[Toscano et al. (2026)](https://www.nature.com/articles/s44387-026-00084-4).
La référence intégrale de Burgers est documentée par
[Burkardt, burgers_exact](https://people.sc.fsu.edu/~jburkardt/f77_src/burgers_exact/burgers_exact.html).
La bibliographie principale du manuscrit conserve les sources PINN, gradient
balancing, importance sampling, RAD et VW avec leurs liens primaires.

Les nouvelles campagnes sont archivées avec leurs manifestes, configurations,
trajectoires, environnements et modèles finaux. Les commandes d'extraction et
de reproduction sont dans `START_HERE_V10.md`. Les dossiers d'analyse contiennent
les scores par germe, audits d'appariement, IC marginaux, tests des signes,
corrections Holm et figures exportables. Les analyses ne sélectionnent aucun
germe favorable. Les différences appariées sont calculées avant agrégation.
