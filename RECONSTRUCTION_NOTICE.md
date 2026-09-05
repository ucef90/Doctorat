# Notice de reconstruction

Cet historique est une reconstruction documentaire et expérimentale créée maintenant,
à partir d'un ZIP V09 et du commit local de sauvegarde antérieur. Les commits ne sont
pas antidatés. Le commit distant initial est conservé comme parent.

Les quatre groupes V06, V07, V08 et V09 suivent l'organisation demandée par le
propriétaire. Ils ne prétendent pas reproduire les versions exactes à leurs dates
d'origine. Par exemple, le rapport V06 contient déjà des résultats M7 et VW, et le
manuscrit disponible contient vRBA ainsi que des révisions postérieures. Nous conservons
ces octets tels quels ; il ne s'agit pas du tout premier brouillon récupéré.

Les fichiers source disponibles correspondent à l'état courant. Aucun instantané
complet et authentifié du code V06/V07/V08 n'a été retrouvé dans ces deux sources.
Le code est donc introduit en V09 uniquement. Les tags antérieurs permettent de
consulter des documents et résultats ; ils ne garantissent pas un logiciel installable.
Le tag demandé `v0.7.0` désigne ici l'étape V07 reconstruite, pas une release source
0.7.0 authentifiée. Le paquet final déclare encore 0.7.0 malgré les extensions V08/V09.
Le nom de version du paquet n'est pas une preuve de provenance historique.

Le ZIP livré précédemment omettait les anciens dossiers de résultats et les schémas
explicatifs. Ils sont récupérés depuis le commit local indiqué dans `INPUT_AUDIT.json`.
`INVENTORY.csv` distingue chaque origine, empreinte, destination et justification.
L'archive elle-même reste inchangée. Six fichiers d'installation `.egg-info` sont
inventoriés et exclus de Git ; aucun résultat scientifique n'est exclu.

Le README original de l'archive est préservé dans
`docs/history/archive-originals/`. Le .gitignore local (absent du ZIP) est conservé
dans `docs/history/local-originals/`. Les nouveaux fichiers de navigation sont
clairement des ajouts de reconstruction. Le CSV inventorie les entrées des sources,
pas sa propre empreinte (auto-référence impossible) ni les autres fichiers générés.
Les entrées de répertoire vides du ZIP sont listées séparément : Git ne les versionne pas.

Les chemins absolus contenus dans les anciens rapports et manifestes restent inchangés
pour préserver la provenance ; certains liens historiques ne s'ouvrent pas ailleurs.
Aucun entraînement n'est relancé et aucun poids de modèle n'est exécuté pendant cet audit.
Le contrôle vérifie l'archivage, pas la validité physique ou statistique des résultats.
vRBA reste une méthode externe ; cette sauvegarde n'établit aucune nouveauté scientifique.
La dernière synthèse V09 documente 200 entraînements, ainsi que 60 fenêtres CPU,
59 essais CPU terminés et un essai interrompu après sa fenêtre de mesure.
