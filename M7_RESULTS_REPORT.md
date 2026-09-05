# Rapport scientifique M7 — correction de mesure adaptative

Date : 4 septembre 2026

> Mise à jour : ce rapport conserve l'analyse M7 antérieure à l'ajout du
> baseline VW. La synthèse actuelle, incluant VW/VW-CA, vRBA, la sensibilité
> KDE et Helmholtz recalibrée, est `ARTICLE1_EVIDENCE_REPORT_V07.md`.

## Décision principale

M7 est techniquement valide et son mécanisme agit réellement sur la mesure de
la perte : sur Burgers, la correction réduit fortement l'écart entre les
gradients calculés sur le lot adaptatif et ceux calculés sur l'ensemble d'audit.

Cependant, **M7 n'est pas supérieure de manière générale sur toutes les EDP**.
Elle produit son signal le plus net lorsque les observations de Burgers sont
rares, bruitées ou incomplètes. Ce résultat conditionnel est plus crédible et
plus utile qu'une revendication universelle non soutenue.

## 1. Travail exécuté

- implémentation PyTorch de l'estimateur de Hansen–Hurwitz `1/(N q_i)` ;
- ajout de M7U, témoin avec le même tirage avec remise mais sans correction ;
- conservation du poids de chaque point lors des remplacements partiels ;
- diagnostics ESS, moyenne et extrêmes des poids ;
- 24 tests unitaires et d'intégration réussis ;
- pilote : 12/12 exécutions réussies ;
- campagne multi-EDP : 160/160 résultats disponibles ;
- campagne données rares/bruitées : 160/160 résultats disponibles ;
- profilage CPU séquentiel : 20/20 exécutions réussies.

Les quatre campagnes totalisent 352 résultats analysés, dont 192 nouveaux
entraînements M7/M7U ou de profilage produits pendant cette étape.

## 2. Résultats sur quatre EDP

Une différence négative signifie que M7 obtient une erreur plus faible.

| EDP | Δ erreur M7−M5, médiane [IC 95 %] | Δ erreur M7−M7U [IC 95 %] | Lecture |
|---|---:|---:|---|
| Burgers | −0,0848 [−0,2085 ; +0,1816] | +0,0643 [−0,0687 ; +0,1726] | tendance favorable face à M5, mais M7U reste meilleur en médiane |
| Allen–Cahn | +0,0088 [+0,0046 ; +0,0159] | +0,0097 [+0,0002 ; +0,0160] | dégradation reproductible |
| Helmholtz | −0,0261 [−0,0355 ; +0,0158] | −0,0327 [−0,0437 ; +0,0178] | non concluant ; benchmark encore sous-entraîné |
| Ondes | −0,0035 [−0,0107 ; −0,0005] | −0,0022 [−0,0088 ; +0,0032] | petit gain face à M5, non établi face à M7U |

### Diagnostic de mécanisme

Sur Burgers long, M7 réduit le décalage logarithmique moyen du gradient
physique face à M7U de `−0,4351`, IC 95 %
`[−0,6182 ; −0,2520]`, avec 10/10 germes favorables et un test des signes
`p=0,00195`. Le décalage de distribution des gradients diminue également de
`−0,0644`, IC 95 % `[−0,1404 ; −0,0216]`.

Ce mécanisme n'est pas universel : sur Helmholtz et sur l'équation des ondes,
certaines mesures de décalage augmentent. M7 corrige bien l'objectif discret
défini, mais cela ne garantit pas une meilleure dynamique d'optimisation sur
toutes les EDP.

## 3. Données rares, bruitées et incomplètes

| Régime Burgers | Δ M7−M5 [IC 95 %] | Δ M7−M6 [IC 95 %] | Δ M7−M7U [IC 95 %] |
|---|---:|---:|---:|
| 13 observations propres | −0,0410 [−0,0568 ; −0,0310] | −0,0343 [−0,0652 ; −0,0217] | −0,0483 [−0,0662 ; −0,0300] |
| 13 observations bruitées + aberrants | −0,0464 [−0,0749 ; −0,0262] | −0,0286 [−0,0589 ; −0,0239] | −0,0482 [−0,0812 ; −0,0247] |
| Une observation + bruit fort | −0,0217 [−0,0461 ; −0,0151] | −0,0268 [−0,0424 ; −0,0159] | −0,0229 [−0,0338 ; −0,0073] |
| Bloc temporel manquant | −0,0310 [−0,0477 ; −0,0184] | −0,0258 [−0,0368 ; −0,0194] | −0,0360 [−0,0503 ; −0,0268] |

Les douze intervalles du tableau excluent zéro. M7 gagne entre 9/10 et 10/10
germes face au témoin M7U. Il ne s'agit donc pas seulement d'un effet du tirage
avec remise.

Dans les quatre régimes, M7 réduit aussi le décalage du gradient physique face
à M7U sur 10/10 germes. En revanche, elle augmente légèrement la variation des
poids du contrôleur. L'amélioration de précision semble donc provenir de
l'alignement de la mesure physique, et non d'une trajectoire de poids plus
lisse.

## 4. Stabilité des poids d'importance

La fraction ESS médiane de M7 vaut environ :

| Régime | ESS/n médiane | Étendue |
|---|---:|---:|
| Burgers long | 0,474 | [0,415 ; 0,531] |
| 13 observations propres | 0,595 | [0,546 ; 0,646] |
| 13 observations bruitées | 0,594 | [0,562 ; 0,640] |
| Une observation + bruit fort | 0,596 | [0,546 ; 0,658] |
| Bloc manquant | 0,608 | [0,483 ; 0,677] |

Aucune exécution ne franchit le seuil d'alerte pré-enregistré `ESS/n < 0,30`.
Les poids maximaux observés restent inférieurs à la borne théorique `5` donnée
par le mélange uniforme `rho=0,8`.

## 5. Coût

Le profilage CPU a été exécuté séquentiellement sur cinq germes :

| Méthode | Temps médian | Évaluations du résidu |
|---|---:|---:|
| M5 | 2,065 s | 197 376 |
| M6 | 2,129 s | 197 376 |
| M7U | 2,175 s | 197 376 |
| M7 | 2,282 s | 197 376 |

Le surcoût médian de M7 vaut `+10,5 %` face à M5, `+7,2 %` face à M6 et
`+4,9 %` face à M7U. Il reste sous l'objectif de 15 %, mais cinq répétitions CPU
ne suffisent pas pour une revendication générale de performance. Un profilage
GPU et un intervalle plus précis restent nécessaires.

## 6. Ce que les résultats démontrent

1. La distribution adaptative modifie effectivement le diagnostic de la perte.
2. Une correction explicite peut fortement réaligner les gradients sur Burgers.
3. L'effet positif ne vient pas seulement du tirage avec remise, grâce au témoin M7U.
4. Le gain de précision est robuste dans quatre régimes de données difficiles.
5. Le coût en évaluations du résidu est strictement identique.

## 7. Ce qu'ils ne démontrent pas

1. M7 n'est pas universellement meilleure : Allen–Cahn est défavorable.
2. Réduire le décalage des gradients ne garantit pas automatiquement une erreur plus faible.
3. Helmholtz doit être recalibrée avant une conclusion méthodologique.
4. La nouveauté du principe d'importance n'est pas acquise ; VW-PINNs,
   l'importance sampling historique et vRBA doivent être comparés explicitement.
5. Aucune conclusion sur les plasmas ou les tokamaks ne peut encore être tirée.

## 8. Positionnement recommandé de l'article

Le résultat défendable devient une étude sur les trois réponses possibles à la
collocation non uniforme :

- laisser le contrôleur couplé à la distribution adaptative (M5) ;
- découpler le contrôleur avec une référence fixe (M6) ;
- corriger explicitement la mesure de la perte (M7).

Titre de travail recommandé :

> **Coupling, Decoupling, or Measure Correction? A Controlled Study of Co-Adaptive Physics-Informed Neural Networks under Sparse and Noisy Data**

En français :

> **Couplage, découplage ou correction de mesure ? Étude contrôlée des PINNs co-adaptatifs avec des données rares et bruitées**

La contribution principale n'est pas « M7 gagne partout », mais l'identification
expérimentale des conditions dans lesquelles chaque mécanisme fonctionne ou
échoue.
