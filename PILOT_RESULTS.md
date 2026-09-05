# Résultats du pilote diagnostique v0.2

Date d’exécution : 4 septembre 2026  
Configuration : `configs/pilot_quick.yaml`  
Problème : Burgers 1D, viscosité `0.01 / pi`  
Méthodes : M0, M1, M3, M5 et M6  
Germes appariés : 11, 22 et 33  
Budget : 120 étapes par exécution

| Méthode | Succès | Erreur L2 relative médiane | Temps médian | TV médiane des poids / mise à jour | TV médiane des gradients entraînement–audit | Évaluations du résidu |
|---|---:|---:|---:|---:|---:|---:|
| M0 | 3/3 | 0,6188 | 1,543 s | 0 | 0,0329 | 28 032 |
| M1 | 3/3 | 0,6850 | 1,555 s | 0,0962 | 0,0296 | 30 528 |
| M3 | 3/3 | 0,6494 | 1,653 s | 0 | 0,1191 | 37 248 |
| M5 | 3/3 | 0,7394 | 1,668 s | 0,0922 | 0,0537 | 39 744 |
| M6 / ReCoA-PINN | 3/3 | 0,7257 | 1,653 s | 0,0952 | 0,0705 | 39 744 |

Analyse appariée M6 − M5 :

- différence médiane d’erreur L2 relative : `+0,01224` ;
- intervalle bootstrap à 95 % : `[-0,01370 ; +0,01786]` ;
- proportion de germes où M6 réduit l’erreur : `1/3` ;
- différence médiane de variation des poids par mise à jour : `+0,00351` ;
- proportion de germes où M6 réduit cette variation : `1/3`.

## Interprétation correcte

Le pipeline est fonctionnel : les quinze exécutions réussissent et les sorties reproductibles sont produites. M5 et M6 ont exactement les mêmes cardinalités et le même budget d’évaluations du résidu, ce qui contrôle l’explication « M6 utilise simplement plus de points ».

Après seulement 120 étapes, l’intervalle de confiance de la différence M6–M5 contient zéro. M6 ne réduit ni l’erreur ni l’oscillation des poids de manière régulière. Ce pilote **ne valide donc ni l’hypothèse de stabilité ni une supériorité de M6**. Trois germes et 120 étapes sont insuffisants pour une conclusion scientifique ; les hyperparamètres proposés peuvent également nécessiter une calibration effectuée sans regarder les germes de test.

La prochaine expérience confirmatoire devra utiliser la configuration complète, dix germes appariés, des intervalles de confiance et une analyse des trajectoires temporelles des poids. Si le résultat reste nul, l’hypothèse devra être rejetée ou reformulée, et non sélectionnée a posteriori sur une EDP favorable.
