# Notes de version 0.7.0

Date : 5 septembre 2026

## Ajouts

- baseline `vrba` PyTorch sur backbone commun ;
- potentiel exponentiel principal et potentiel quadratique disponible pour les
  sensibilités exploratoires ;
- multiplicateurs locaux persistants et auto-équilibrage global ;
- protocole vRBA pré-enregistré ;
- campagnes pilote, multi-EDP et données rares/bruitées ;
- métriques ESS, multiplicateurs, température et traçabilité de l'objectif ;
- contrastes automatiques M7–vRBA, VW–vRBA et M0–vRBA ;
- analyse spatiale Burgers avec cartes, profils, quantiles et coordonnées des
  maxima sur dix germes ;
- cinq nouveaux tests, portant le total à 32.

## Validation

- 18/18 runs pilotes réussis ;
- 200/200 cellules confirmatoires disponibles ;
- 200/200 cellules sous données difficiles disponibles ;
- 973/973 résumés du dépôt au statut `succeeded` ;
- 32/32 tests réussis ;
- environnement aligné sur les campagnes v0.6 : NumPy 2.3.5.

## Résultat principal

vRBA améliore l'erreur L2 sur quatre EDP et quatre régimes Burgers difficiles,
mais dégrade l'erreur maximale de Burgers face à M5/M6 et présente un surcoût
variable. La version 0.7 interdit donc toute revendication de domination
universelle.
