# Protocole de transformation de ReCoA-PINN en recherche scientifique

Version : 0.3 — 4 septembre 2026

## Principe général

L’affirmation scientifique centrale est la suivante :

> Lorsque l’échantillonneur résiduel modifie la distribution des points d’entraînement, un contrôleur global calculé sur ces mêmes points peut confondre difficulté physique globale et concentration locale de l’échantillonnage. Calculer les diagnostics du contrôleur sur un ensemble fixe et indépendant devrait réduire ce biais de rétroaction.

Cette affirmation doit pouvoir être réfutée. ReCoA-PINN ne sera déclaré utile que si le découplage améliore simultanément la stabilité ou la reproductibilité du contrôleur et la qualité de la solution, à budget comparable.

## Plan factoriel minimal

| Méthode | Pondération adaptative | Échantillonnage adaptatif | Source du contrôleur |
|---|---:|---:|---|
| M0 | Non | Non | Poids fixes |
| M1 | Oui | Non | Points uniformes d’entraînement |
| M3 | Non | Oui | Poids fixes |
| M5 | Oui | Oui | Lot adaptatif courant |
| M6 | Oui | Oui | Ensemble d’audit fixe |

M1 contre M5 mesure l’effet ajouté de l’échantillonnage sur un même type de contrôleur. M5 contre M6 isole le découplage. M3 vérifie que les gains ne viennent pas seulement du rééchantillonnage.

## 1. Démontrer le biais ou les oscillations de M5

### Hypothèse H1

À modèle comparable, les diagnostics calculés sur le lot adaptatif s’écartent des diagnostics calculés sur une mesure fixe du domaine. Cet écart augmente lorsque l’échantillonneur se concentre.

### Expérience

1. Exécuter M1 et M5 avec les mêmes architectures, budgets et germes.
2. À chaque mise à jour du contrôleur, calculer les pertes et normes de gradient sur le lot d’entraînement et sur l’ensemble fixe.
3. Journaliser ces diagnostics sans utiliser l’ensemble fixe pour mettre à jour M5.
4. Relier chaque saut des poids à l’événement de rééchantillonnage précédent.

### Métriques

- variation totale des poids : `controller_weight_tv` ;
- variation moyenne par mise à jour : `controller_weight_tv_per_update` ;
- distance en variation totale entre les distributions normalisées des gradients : `gradient_distribution_tv` ;
- distance analogue entre les pertes : `loss_distribution_tv` ;
- écart logarithmique du gradient physique : `physics_gradient_log_gap` ;
- taille effective et entropie de l’échantillonneur.

### Critère de validation

H1 est soutenue si M5 présente, sur la majorité des problèmes, un écart entraînement–audit et une variation des poids supérieurs à M1, avec des augmentations temporelles après les rééchantillonnages. Une simple courbe visuellement agitée ne suffit pas : les différences appariées et leurs intervalles de confiance doivent être rapportés.

### Résultat qui réfuterait H1

Si M1 et M5 ont une stabilité similaire, ou si la concentration de l’échantillonneur n’est pas associée aux écarts de gradients, l’explication par biais d’échantillonnage devra être abandonnée ou reformulée.

## 2. Démontrer que M6 réduit le phénomène

### Hypothèse H2

M6 réduit la variation des poids et la dispersion entre germes par rapport à M5, sans détériorer la précision.

### Expérience

- comparer M5 et M6 par paires, avec le même germe, la même initialisation, les mêmes ensembles candidats et les mêmes fréquences de mise à jour ;
- ne modifier qu’une variable : la source des diagnostics du contrôleur ;
- conserver séparément les trajectoires des trois poids.

### Critères principaux

- différence appariée de variation totale par mise à jour : M6 − M5 < 0 ;
- dispersion interquartile des poids finaux plus faible pour M6 ;
- taux d’échec numérique de M6 inférieur ou égal à celui de M5 ;
- erreur L2 de M6 non supérieure au-delà d’une marge de non-infériorité pré-enregistrée, puis test de supériorité si la non-infériorité est établie.

### Conclusion autorisée

On pourra parler de stabilisation uniquement si les trajectoires deviennent plus reproductibles et si ce changement ne se limite pas à un lissage artificiel sans bénéfice sur la solution.

## 3. Exclure l’explication par un nombre supplémentaire de points

### Risque

M6 possède un ensemble fixe supplémentaire en mémoire. Un évaluateur pourrait attribuer son avantage à davantage d’information ou de calcul.

### Contrôles

1. Imposer la même cardinalité au lot servant au contrôleur M5 et à l’ensemble d’audit M6.
2. Donner à M5 le même ensemble d’audit pour les diagnostics contrefactuels, mais interdire son utilisation dans la mise à jour des poids.
3. Compter séparément les évaluations de résidu pour l’optimisation, le contrôleur, l’échantillonneur et le diagnostic.
4. Comparer à nombre d’étapes identique, à nombre d’évaluations identique et à temps identique.

### Critère

La contribution est attribuable au découplage seulement si M5 et M6 ont les mêmes cardinalités et le même budget utile, et que leur seule différence opérationnelle reste la distribution utilisée par le contrôleur.

Le dépôt enregistre cette vérification sous `budget.equal_controller_cardinality` et détaille les quatre catégories d’évaluations.

## 4. Vérifier la persistance sur dix germes et plusieurs EDP

### Campagne confirmatoire

Utiliser dix germes fixés avant l’expérience : `11, 22, 33, 44, 55, 66, 77, 88, 99, 111`.

Suite recommandée :

| Problème | Difficulté testée |
|---|---|
| Burgers 1D | Gradient raide et concentration locale |
| Allen–Cahn 1D | Réaction-diffusion raide et interfaces |
| Helmholtz 2D | Biais spectral et oscillations spatiales |
| Ondes 1D | Causalité et propagation temporelle |
| Oscillateur amorti inverse | Identification sous données limitées |

### Analyse statistique

- statistique principale : médiane de l’erreur L2 relative ;
- différences appariées M6 − M5 ;
- intervalle bootstrap à 95 % ;
- proportion de germes gagnés ;
- correction de Holm entre les problèmes ;
- tailles d’effet et taux d’échec, sans supprimer les exécutions défavorables.

### Critère pré-enregistré proposé

M6 doit améliorer la stabilité sur au moins trois des quatre EDP et ne pas dégrader matériellement l’erreur médiane. Tout seuil de gain numérique doit être justifié par une phase pilote séparée des résultats confirmatoires.

## 5. Tester les données rares et bruitées

### Régimes de données

- données conservées : 100 %, 10 %, 5 % et 1 % ;
- bruit gaussien : 1 %, 5 %, 10 % et 20 % de l’écart-type du signal ;
- bruit hétéroscédastique dépendant de l’amplitude ;
- bruit spatialement ou temporellement corrélé ;
- 5 % de valeurs aberrantes ;
- perte aléatoire et perte en blocs de capteurs.

### Contrôles indispensables

- même masque de capteurs et même réalisation de bruit pour toutes les méthodes d’une paire ;
- cible de test toujours propre et indépendante ;
- comparaison erreur quadratique moyenne contre perte de Huber ;
- séparation entre robustesse due à Huber et robustesse due au découplage.

### Critère

Le gain est robuste si M6 conserve une meilleure stabilité ou précision dans plusieurs familles de corruption, et pas uniquement pour un bruit gaussien choisi favorablement.

## 6. Vérifier que le surcoût reste raisonnable

### Mesures

- temps mural total et temps par étape ;
- évaluations du résidu par catégorie ;
- mémoire GPU maximale ;
- nombre de paramètres ;
- erreur en fonction du temps et en fonction des évaluations du résidu.

### Trois comparaisons obligatoires

1. même nombre d’étapes ;
2. même nombre total d’évaluations ;
3. même temps mural.

### Règle proposée

Un surcoût médian inférieur ou égal à 15 % peut être retenu comme objectif, mais pas comme vérité préalable. Si M6 coûte davantage, il faudra montrer une courbe précision–coût favorable ou réduire la fréquence des diagnostics.

## 7. Réaliser l’ablation supprimant le découplage

L’ablation principale est déjà définie exactement :

- A0 : M6 complet, contrôleur sur ensemble fixe ;
- A1 : M5, même algorithme, mais contrôleur sur lot adaptatif.

### Logique causale

Si A0 est meilleur et que le bénéfice disparaît avec A1, le résultat soutient le rôle du découplage. Si A0 et A1 sont équivalents, l’ensemble fixe n’est pas la cause du gain. Si A1 est meilleur, ReCoA-PINN doit être rejeté ou limité aux régimes où A0 apporte un avantage démontré.

### Ablations secondaires

- taille de l’ensemble d’audit : 0,25×, 0,5×, 1× et 2× ;
- audit uniforme, stratifié et quasi-Monte-Carlo ;
- audit fixe contre rotation lente préprogrammée ;
- sans lissage, sans bornage et sans plancher uniforme ;
- fréquences différentes du contrôleur et de l’échantillonneur.

## 8. Documenter la différence avec les travaux 2025–2026

La nouveauté ne doit jamais être formulée comme la simple combinaison de pondération et d’échantillonnage adaptatifs. Cette combinaison existe déjà.

La revendication candidate est plus précise :

> ReCoA-PINN sépare la distribution utilisée pour optimiser les paramètres de celle utilisée pour estimer les diagnostics d’un contrôleur global des composantes de perte, afin de tester et réduire un biais de rétroaction induit par l’échantillonnage adaptatif.

La matrice détaillée se trouve dans `NOVELTY_MATRIX.md` et la recherche publique structurée dans `SYSTEMATIC_LITERATURE_REVIEW_2025_2026.md`. Avant soumission, une vérification complémentaire dans Scopus ou Web of Science et l’examen des codes associés restent recommandés.

## Ordre d’exécution recommandé

1. Burgers : M0, M1, M3, M5 et M6 sur trois germes pour vérifier les instruments.
2. Burgers : dix germes et budget long pour tester H1–H3.
3. Ablation A0–A1 et sensibilité à la taille de l’audit.
4. Ajout d’Allen–Cahn, puis Helmholtz et ondes.
5. Ajout de l’oscillateur inverse et des régimes bruités.
6. Gel du protocole, lancement confirmatoire et génération automatique des tableaux.
7. Rédaction des résultats, y compris résultats négatifs et cas d’échec.

## État actuel

| Élément | État |
|---|---|
| M0, M1, M3, M5, M6 | Implémentés |
| Diagnostics entraînement–audit | Implémentés |
| Comptabilité du coût | Implémentée |
| Analyse appariée et bootstrap | Implémentée |
| Burgers long, dix germes | Exécuté : tendance M6 favorable mais non significative |
| Allen–Cahn, Helmholtz, ondes | Implémentés et criblés sur dix germes |
| Données rares et bruitées | Implémentées et criblées sur quatre régimes |
| Ablations | Treize variantes exécutées sur cinq germes |
| Revue 2025–2026 | Revue publique structurée terminée ; Scopus/WoS reste souhaitable |
| Validation tokamak | Prévue dans les articles suivants |

Les décisions chiffrées et les résultats négatifs sont consignés dans `SCIENTIFIC_RESULTS_REPORT.md`.
