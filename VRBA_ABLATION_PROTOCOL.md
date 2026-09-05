# Protocole v0.8 — décomposition de vRBA

Date : 2026-09-05. Statut : protocole prospectif pour de nouveaux calculs,
mais étude exploratoire après observation des résultats v0.7. Ce document
n'est pas un pré-enregistrement public indépendant.

## Question et attribution

Quelle part du comportement de notre adaptation PyTorch de vRBA provient de
l'attention locale, de l'équilibrage global et du potentiel choisi ? vRBA est
une méthode externe, non une invention de ce projet. Nous étudions une
implémentation à architecture commune ; ce n'est pas une reproduction exacte
du logiciel et du protocole des auteurs.

## Plan expérimental

| Identifiant | Local | Global | Potentiel |
|---|---|---|---|
| full_exp | oui | oui | exponentiel |
| local_only | oui | non | exponentiel |
| global_only | non | oui | inactif |
| full_quad | oui | oui | quadratique |
| neither | non | non | inactif |

Le cinquième bras ferme le plan factoriel local × global. Il doit reproduire
M0 à arrondi près sur le même germe. Sans contrôle neither, une interaction
local-global ne serait pas isolée. Les poids globaux désactivés valent 1 ;
l'attention locale désactivée est absente, donc équivalente à des poids 1.

Pilote : Burgers, configuration pilot_quick, germes 11, 22, 33, 120 pas.
Ce pilote vérifie le fonctionnement ; il ne sélectionne pas les gagnants.
Suite prévue : cinq bras × dix germes × quatre EDP = 200 entraînements,
avec configurations longues ou calibrées historiques inchangées.
Toutes les variantes restent dans l'analyse, y compris les échecs numériques.
Si une correction de code est nécessaire, elle sera consignée et tous les
bras concernés seront réexécutés sous une même version.

## Contrôles et provenance

Apparier initialisation, données, points, architecture, optimiseur, précision
et nombre de pas. Les points de vRBA restent fixes ; ne pas ajouter un
échantillonneur adaptatif pendant cette ablation. Comparer séparément à
budget de pas fixé et à budget de temps fixé : ils ne sont pas équivalents.
Archiver configuration résolue, environnement, état final, historique et
empreinte SHA-256 du code. Ne pas mélanger silencieusement les environnements.
Le lanceur refuse un dossier de sortie existant pour éviter les écrasements.
L'ordre des variantes est randomisé par germe avec un générateur indépendant.

## Critères et analyse à venir

Critère principal : erreur relative L2 sur une grille indépendante fixe.
Critère secondaire prioritaire : maximum de l'erreur absolue sur cette grille
(ce n'est pas un maximum continu garanti). Ajouter q95 et q99, erreur du
résidu physique sur points indépendants, variation des poids et taux d'échec.
Vérifier la résolution de grille près des pics : le pic observé en v0.7
n'est pas une région de validation indépendante.

Contrastes planifiés : full_exp-local_only, full_exp-global_only,
full_exp-full_quad et interaction full_exp-local_only-global_only+neither.
Sur dix germes : différences appariées, médiane, dispersion et intervalles
bootstrap appariés ; rapporter tous les contrastes, avec correction Holm si
des tests multiples sont utilisés. Ne pas traiter les points de grille
comme des répétitions indépendantes. Les trois germes pilotes ne permettent
pas une conclusion confirmatoire.

Coût : temps complet et entraînement seul, matériel, nombre de threads,
mémoire CPU et pic GPU si disponible. Profilage séquentiel intercalé avec
échauffement ; synchronisation CUDA avant/après chronométrage. Ne pas
comparer des temps pris sur matériels différents comme un effet de méthode.

## Critères de clôture scientifique

Tests de désactivation et de reproductibilité réussis ; tous les bras et
échecs recensés ; analyse dix germes et quatre EDP ; données rares/bruitées
sur protocole distinct ; figures issues uniquement des mesures ; attribution
bibliographique ; limites et résultats négatifs dans le manuscrit.
Une meilleure erreur moyenne ne démontre ni sécurité, ni contrôle plasma,
ni robustesse hors distribution. L'application tokamak reste une étape future.
