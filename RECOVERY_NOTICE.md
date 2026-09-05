# Récupération du paquet Git — 5 septembre 2026

Le fichier `Doctorat_Historique_V06_V09.zip` disponible au moment de cette
récupération est tronqué : aucun répertoire central ZIP, flux Deflate interrompu,
88 390 499 octets de bundle récupérables pour 100 498 934 octets annoncés.
Il ne peut donc pas être utilisé comme archive complète.

Les objets Git complets ont été extraits du flux disponible. Les 563 blobs
manquants récupérables ont été restaurés à partir des archives originales
ReCoA-PINN V06 et V09, en exigeant une correspondance exacte de leur identifiant
Git SHA-1. Les archives V07 et V08 ont aussi été contrôlées. Les quatre archives
scientifiques passent le contrôle CRC ZIP.

Les commits suivants sont conservés à l'identique :

| Étape | Commit |
| --- | --- |
| Initial | `59498a9fde0662dabc0c407300b4d6c89f40f64f` |
| V06 | `9fb664d4289e0da91daaf2ffbdfaca65670466fb` |
| V07 | `8d580f48785ac08c11e04afd0ed92f4156cda1ef` |
| V08 | `cff642afc39602c1bdbcda56aed9328b11271dde` |

Un seul blob reste introuvable :
`fff917ef13f8b104a3a2b871e644b5a1fa89b040`, correspondant à l'ancien
`scripts/reconstruct_history.py`. Il s'agit d'un outil ajouté pour la
reconstruction, et non d'un fichier scientifique inventorié.

Ce script est remplacé explicitement par un nouveau vérificateur en lecture seule.
Il prend en charge `python scripts/reconstruct_history.py verify --repo .`.
Il contrôle les tailles et SHA-256 des 8 281 fichiers scientifiques conservés,
leur présence aux quatre étapes, l'ordre des parents, les tags et l'intégrité Git.
Il ne reproduit pas les éventuelles anciennes commandes de reconstruction.

Le commit V09 doit donc être recréé à partir du même parent V08, avec le même
contenu récupéré, ce script remplacé et cette notice ajoutée. Son identifiant
diffère de l'ancien `af154a85e331b9f8e306f531f03983306a8504ad`.
Le tag `article1-v0.9` est recréé pour désigner ce nouveau commit. Les identifiants
de V06/V07/V08 et les tags V07/V08 sont inchangés. L'auteur et la date d'auteur de
V09 sont conservés ; l'identité et la date du nouveau committer indiquent la réparation.

Les autres fichiers du snapshot V09 sont conservés octet pour octet. Les anciennes
notices décrivent les sources disponibles lors de la première reconstruction ;
cette notice décrit uniquement la récupération du paquet de transfert.

Le bundle final est autonome : il contient l'historique, les branches `main`,
`archive/v06`, `archive/v07`, `archive/v08`, `archive/v09` et les trois tags.
Il s'importe avec Git, sans utiliser les pièces jointes de Codex et sans ZIP.
Le contrôle d'archivage ne constitue pas une validation des résultats scientifiques.
