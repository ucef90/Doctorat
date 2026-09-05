# V10 — contrôles historiques sous perte d'observation commune

Extension figée après l'audit Huber/MSE et les résultats d'ablation V10.
Statut exploratoire. La campagne ajoute 160 entraînements : M5, M6, M7, VW,
quatre configurations Burgers à données difficiles, dix germes appariés.
Les 40 modèles full_exp de la nouvelle campagne de robustesse sont réutilisés
comme comparateur vRBA ; ils ne sont pas comptés comme de nouveaux entraînements.

Tous utilisent MSE et les mêmes observations issues de Cole–Hopf, le même
MLP, Adam, 600 pas, précision float64 et cardinalités. Le manifeste reprend
exactement les configurations résolues des cellules full_exp de robustesse,
à l'exception de l'identifiant de méthode et du dossier de sortie.
Les réglages vRBA présents dans le YAML sont sans effet sur les autres méthodes.

Primaire : L2 relative. Secondaire : maximum absolu sur la grille.
Quatre contrastes vRBA−M5/M6/M7/VW par régime, soit une famille Holm de
16 tests par métrique. Médianes de différences par germe, 10000 bootstrap
percentile (germe 9092026), IC marginaux 95 %, test exact des signes.
Les initialisations et cibles sont vérifiées par empreintes entre méthodes
et avec les modèles vRBA réutilisés. Les 160 états finaux sont réévalués.
Les échecs sont conservés, sans imputation de scores. Aucun germe n'est choisi
selon son résultat. Les temps de sessions/concurrences distinctes ne fondent
pas de comparaison d'efficacité.
