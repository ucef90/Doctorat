# Extension V10 — protocole figé avant nouveaux entraînements

Point de départ : commit V09 `0142311a08c9cd72d05494b6f24dd8949ebe6cd6`.
Statut : exploration structurée après connaissance des résultats V09.

## Deux campagnes, 400 nouveaux entraînements

Chaque campagne conserve les cinq variantes V09 : neither, global_only,
local_only, full_exp, full_quad. Germes 11,22,33,44,55,66,77,88,99,111.
Architecture, Adam, cardinalités et hyperparamètres d'adaptation restent ceux
des fichiers source ; aucun arrêt fondé sur un score, aucun bras exclu.

1. Robustesse : quatre configurations Burgers `burgers_data_sparse_clean`,
   `burgers_data_sparse_noisy`, `burgers_data_extreme`,
   `burgers_data_block_missing` ; 5 bras × 10 germes = 200 cellules.
   **MSE pour toutes les observations et tous les bras**, y compris les bras
   sans attention locale. Les anciennes configurations Huber n'étaient pas
   un contrôle à perte identique : l'attention locale vRBA utilisait une perte
   quadratique pondérée. Ne pas assimiler cette campagne à une reproduction
   bit à bit des expériences bruitées V07.
2. Sensibilité au nombre de pas : quatre configurations V09, budget doublé
   (Burgers 5000, Allen–Cahn 1200, Helmholtz 3000, ondes 1200), 200 cellules.
   Comparaisons entre bras à nombre de pas égal. Le point V09 à budget initial
   est historique ; aucun gain temporel ne sera déduit de sessions différentes.

La référence Burgers des nouvelles observations et évaluations est la
quadrature Cole–Hopf (128 nœuds) après contrôle 128/256 et quadrature adaptative
indépendante. Les anciens modèles et scores restent intacts. Les métriques
de V09 sont réévaluables sur cette même référence, sans changer l'entraînement.

## Analyse et provenance

Primaire : erreur L2 relative. Secondaire : maximum absolu **sur la grille**.
Quatre contrastes par problème/régime : full_exp−local_only,
full_exp−global_only, full_exp−full_quad, interaction
full_exp−local_only−global_only+neither. Différences par germe, médiane,
IC bootstrap marginal 95 % (10000 tirages, germe 9092026), test exact des
signes. Holm sur les 16 tests L2 de chaque campagne ; famille séparée de
16 tests maximum. Les familles ne sont pas combinées a posteriori.

Appariement vérifié sur les empreintes des paramètres et ensembles initiaux,
y compris les cibles d'observation. Manifeste immuable de chaque cellule,
hashes des sources et du protocole, environnement et résultats d'échec conservés.
Le lanceur refuse une reprise si le manifeste ou l'environnement numérique change.
L'évaluation indépendante relit les modèles finaux et contrôle les scores.

Le parallélisme sert au débit. Les temps ainsi collectés ne constituent pas
une expérience à temps CPU égal. Restent distincts : budget temporel égal,
réplication sur machine indépendante, protocole JAX officiel et cas plasma.
Une réduction d'erreur sur ces synthèses ne démontre ni nouveauté de vRBA
ni garantie de stabilité/contrôle d'un tokamak.
