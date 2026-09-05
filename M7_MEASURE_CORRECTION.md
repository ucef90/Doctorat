# M7 — PINN co-adaptatif avec correction de mesure

## 1. Pourquoi M7 est nécessaire

L'échantillonneur adaptatif place davantage de points là où le résidu de l'EDP
est élevé. Cette concentration peut accélérer l'apprentissage local, mais elle
change également la mesure numérique minimisée par le PINN.

Si `p(z)` désigne la mesure uniforme visée sur le domaine et `q_t(z)` la
proposition adaptative à l'étape `t`, M5 minimise empiriquement :

\[
\mathbb{E}_{z\sim q_t}\!\left[r_\theta(z)^2\right],
\]

alors que l'objectif physique uniforme est :

\[
\mathcal L_f(\theta)
=\mathbb{E}_{z\sim p}\!\left[r_\theta(z)^2\right].
\]

M6 découple le contrôleur des poids grâce à un ensemble fixe, mais son pas
d'optimisation reste calculé sur la distribution adaptative. M7 traite donc un
problème différent : il conserve les points informatifs tout en corrigeant la
mesure utilisée dans la perte physique.

## 2. Proposition discrète utilisée par le code

À chaque rafraîchissement, on tire uniformément un ensemble candidat
`C={z_1,…,z_N}`. Pour chaque candidat, le score est :

\[
s_i=(|r_\theta(z_i)|+\varepsilon)^\gamma.
\]

La probabilité adaptative inclut un plancher uniforme :

\[
q_i=\frac{1-\rho}{N}+\rho\frac{s_i}{\sum_{k=1}^{N}s_k},
\qquad 0\leq\rho<1.
\]

La cible discrète sur les candidats est `p_i=1/N`. Le poids de correction
attaché au point sélectionné est donc :

\[
w_i=\frac{p_i}{q_i}=\frac{1}{Nq_i}.
\]

La perte physique de M7 devient :

\[
\widehat{\mathcal L}^{M7}_f
=\frac{1}{n}\sum_{j=1}^{n}w_jr_\theta(z_j)^2.
\]

Conditionnellement au bassin candidat, un tirage avec remise vérifie :

\[
\mathbb E_{i\sim q}\left[w_i h(z_i)\mid C\right]
=\sum_i q_i\frac{1/N}{q_i}h(z_i)
=\frac{1}{N}\sum_i h(z_i).
\]

Le code emploie donc un estimateur de Hansen–Hurwitz. Le tirage avec remise est
nécessaire ici : avec un tirage pondéré sans remise, `q_i` n'est pas en général
la probabilité d'inclusion et la correction `1/(Nq_i)` ne serait pas exacte.

## 3. Gestion du remplacement partiel

Seule une fraction du lot est renouvelée à chaque adaptation. Chaque nouveau
point reçoit le poids correspondant à sa proposition au moment de son tirage.
Les points conservés gardent leur ancien poids. Le lot courant peut ainsi être
vu comme un ensemble provenant de plusieurs propositions successives.

Le plancher uniforme garantit :

\[
q_i\geq\frac{1-\rho}{N}
\quad\Longrightarrow\quad
w_i\leq\frac{1}{1-\rho}.
\]

Avec `rho=0,8`, le poids maximal théorique vaut donc `5`. Cela contrôle la
variance sans introduire de troncature arbitraire des poids.

## 4. Méthodes nécessaires pour identifier l'effet causal

| Méthode | Échantillonnage | Contrôleur | Correction de mesure | Rôle |
|---|---|---|---|---|
| M5 | adaptatif sans remise | lot adaptatif | non | méthode couplée historique |
| M6 | adaptatif sans remise | référence fixe | non | découplage du contrôleur |
| M7U | adaptatif avec remise | lot adaptatif | non | témoin apparié du mécanisme de tirage |
| M7 | adaptatif avec remise | lot adaptatif | oui | méthode corrigée proposée |

Le contraste **M7−M7U** isole mieux l'effet des poids d'importance que le seul
contraste M7−M5. Le contraste M7−M6 permet ensuite de comparer correction de
mesure et découplage par référence fixe.

## 5. Diagnostics enregistrés

Chaque exécution sauvegarde :

- moyenne, minimum et maximum des poids d'importance ;
- fraction de taille effective de l'échantillon pondéré ;
- concentration de la proposition adaptative ;
- décalage entre gradients d'entraînement et d'audit ;
- variation des poids du contrôleur ;
- erreur relative `L2`, erreur maximale, temps et évaluations du résidu.

## 6. Hypothèses réfutables du pilote

1. **Correction de mesure** : M7 doit réduire le décalage entraînement–audit par
   rapport à M7U.
2. **Utilité prédictive** : cette réduction doit améliorer ou préserver
   l'erreur `L2`, et pas seulement lisser les poids.
3. **Variance acceptable** : la taille effective pondérée ne doit pas
   s'effondrer ; le seuil d'alerte pré-enregistré est `ESS/n < 0,30`.
4. **Budget équitable** : M7 et M7U doivent employer les mêmes cardinalités,
   fréquences et nombres d'évaluations du résidu.
5. **Robustesse** : un pilote favorable ne suffit pas ; le résultat devra être
   confirmé sur dix germes, quatre EDP et les régimes rares/bruités.

## 7. Limites à déclarer

- La correction est exacte conditionnellement à la population candidate, pas
  une preuve de convergence globale du réseau non convexe.
- Le modèle courant dépend de l'historique des échantillons ; la dynamique
  complète reste adaptative et corrélée dans le temps.
- Réutiliser des points réduit le coût mais augmente la dépendance temporelle.
- M7 est proche de la famille des corrections de quadrature/volume ; sa
  nouveauté ne devra être revendiquée qu'après comparaison formelle à VW-PINNs
  et aux méthodes adaptatives récentes.
- Un succès sur le pilote Burgers ne constitue pas une validation scientifique
  définitive.

## 8. Décision scientifique attendue

M7 sera retenu pour la campagne confirmatoire uniquement si :

- toutes les exécutions sont finies et reproductibles ;
- les poids restent finis et l'ESS reste acceptable ;
- M7 ne dégrade pas fortement l'erreur par rapport à M7U ;
- un signal cohérent apparaît sur le décalage de gradients ou la précision.

Sinon, le résultat négatif sera conservé et documenté : il indiquerait que la
correction de la mesure seule ne suffit pas à résoudre les difficultés de
l'entraînement co-adaptatif.
