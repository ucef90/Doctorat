# Protocole figé avant les calculs v0.9

Date : 2026-09-05. Extension du protocole v0.8, après connaissance du pilote.
Étude exploratoire à comparaisons planifiées ; aucun enregistrement public.

## Population expérimentale

200 cellules, cinq variantes × dix germes × quatre problèmes. Germes :
11,22,33,44,55,66,77,88,99,111. Les trois germes pilotes restent inclus :
ils ne sont pas un jeu indépendant de sélection. Aucun réglage sur le pilote.

| Problème | Configuration | Pas | Particularité |
|---|---|---:|---|
| Burgers | burgers_confirmatory_long.yaml | 2500 | viscosité 0.01/pi, référence numérique |
| Allen–Cahn | allen_cahn_screen.yaml | 600 | solution manufacturée forcée, pas le benchmark standard |
| Helmholtz | helmholtz_calibrated.yaml | 1500 | k=1, solution manufacturée, pas haute fréquence |
| Ondes | wave_screen.yaml | 600 | cas analytique simple |

Cinq bras : full_exp, local_only, global_only, full_quad, neither.
Le potentiel quadratique conserve phi=0.8 pour isoler le seul potentiel.
Les auteurs utilisaient phi=1 dans leurs essais quadratiques : notre bras
est donc une ablation contrôlée, pas une réplication de leur configuration.
Les paramètres restent ceux de v0.8, y compris la mémoire globale 0.99975.
Sa constante de temps approximative de 4000 pas dépasse certains budgets :
une absence de gain global ne prouverait pas son inutilité à long terme.

## Exécution et contrôle

Architecture et données fixes pour une paire problème-germe ; empreintes
des vrais tenseurs initiaux enregistrées par le trainer. Un processus neuf
par cellule, un thread numérique, six processus simultanés. Ordre des bras
randomisé indépendamment des générateurs d'entraînement. Pas d'arrêt anticipé
sur le score, ni élimination des échecs. Les échecs terminés restent terminés.
La reprise vérifie code, protocole, configuration et environnement ; seules
les cellules interrompues sans résultat final peuvent repartir dans une
nouvelle tentative, en conservant l'ancienne. Reprise au niveau cellule,
pas de restauration de l'état de l'optimiseur en milieu d'entraînement.

## Analyse planifiée

Principal : L2 relative sur grille historique indépendante des points
d'entraînement. Secondaire prioritaire : maximum absolu sur cette grille.
Autres : q95/q99 spatiaux, résidu physique RMS sur 4096 points indépendants
avec germe d'évaluation fixe 9092026, variation des poids, échecs, coût CPU.
Quantiles spatiaux et répétitions entre germes sont deux objets distincts.

Quatre contrastes par EDP : full_exp-local_only, full_exp-global_only,
full_exp-full_quad et full_exp-local_only-global_only+neither (interaction).
Différences appariées, médiane et IC bootstrap percentile 95 %, 10000 tirages,
graine d'analyse 9092026. Test exact bilatéral des signes, zéros exclus.
Holm sur les 16 tests L2 pris ensemble ; famille distincte de 16 tests pour
le maximum. Les IC restent marginaux, non simultanés. Avec n=10, interpréter
les tailles d'effet et l'incertitude, sans transformer p>0.05 en équivalence.
Si échecs : dénominateurs explicites ; analyses de scores sur paires complètes
signalées comme conditionnelles aux réussites. Ne pas imputer des scores.

Vérification des extrêmes : grille deux fois plus fine dans chaque direction
sur les modèles finaux, sans réentraînement. Pour Burgers, vérifier séparément
la sensibilité de la référence numérique (résolution doublée, pas divisé par
deux), avant d'interpréter les pics comme une propriété du modèle.

## Limites et livrables

Le temps mural sous calculs concurrents décrit le débit ; il n'est pas un
profilage isolé. CPU par processus et pic RSS (incluant Python/PyTorch) sont
descriptifs. Pas de résultat GPU si aucun GPU disponible. Les données rares
et bruitées et les budgets de temps égaux nécessitent des campagnes distinctes.
Livrer résultats individuels, audit d'appariement, statistiques, figures,
code, environnement et conclusion bornée aux configurations testées.

Référence primaire vérifiée le 2026-09-05 : Toscano et al.,
[A variational framework for residual-based adaptivity in neural PDE solvers and operator learning](https://www.nature.com/articles/s44387-026-00084-4),
[prépublication v2, annexe D.1](https://arxiv.org/html/2509.14198v2).
Cette source décrit vRBA, ses potentiels et ses réglages ; nos expériences
utilisent une adaptation PyTorch avec architecture commune. Les résultats
futurs ne prouveront ni nouveauté de vRBA, ni contrôle fiable d'un tokamak.
