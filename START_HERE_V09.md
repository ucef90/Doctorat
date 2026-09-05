# Livraison v0.9 — lire en premier

Cette livraison clôt la campagne de décomposition de vRBA : 200/200
entraînements réussis sur quatre EDP et dix germes. Le protocole reste
exploratoire, avec paramètres figés avant calcul. Les documents v0.7/v0.8
inclus sont des archives historiques ; leur liste des tâches restantes
n'est pas l'état actuel du projet.

## Lire les résultats

- `output/pdf/ARTICLE1_ABLATIONS_V09_RAPPORT.pdf` : rapport français, 11 pages.
- `outputs/ablation_v09_analysis/ARTICLE1_ABLATIONS_V09_RAPPORT.md` : texte éditable.
- `outputs/ablation_v09_analysis/paired_statistics.csv` : 32 contrastes.
- `outputs/ablation_v09_analysis/evaluation.csv` : 200 évaluations indépendantes.
- `outputs/ablation_v09_analysis/pairing_audit.csv` : 40 blocs appariés vérifiés.
- `outputs/ablation_v09_analysis/` : figures PNG/SVG et champs NPZ.

## Profilage CPU : distinction indispensable

60 fenêtres de chronométrage sont réellement enregistrées. 59 essais ont
atteint leur fin ; le dernier (Helmholtz/local seul/germe 33) a été interrompu
après le pas 150. La fenêtre prévue, entre les pas 50 et 150, est complète.
Son RSS final et son modèle terminal ne sont pas disponibles. Il n'est pas
compté comme un entraînement terminé. Les originaux sont conservés ; le
fichier `measured_windows.json` distingue la récupération de journal.
Le script `recover_cpu_measurements.py` reproduit cette agrégation sans
extrapolation. Il ne relance pas le calcul et ne nécessite pas PyTorch.

## Conclusions bornées aux cas testés

Helmholtz k=1 : association locale/globale favorable face aux deux composantes
isolées. Ondes : potentiel quadratique favorable à L2 face à l'exponentiel.
Ces contrastes passent Holm à 5 %. Burgers : pas de gagnant établi parmi les
contrastes planifiés ; les erreurs extrêmes restent sensibles à la référence.
La méthode vRBA est externe ; aucune invention de cette méthode n'est revendiquée.

## Reproduction

Consulter les commandes du rapport. Les sources exactes de l'entraînement
sont identifiées par `outputs/ablation_v09_campaign/manifest.json`. Les scripts
d'analyse produisent leurs propres empreintes. Le code a passé 43 tests
puis trois tests statistiques supplémentaires avant l'interruption de session.
Les 200 scores ont été recalculés depuis les états finaux sauvegardés.
Pour reconstruire le PDF, installer aussi `reportlab` et lancer
`scripts/render_vrba_report_pdf.py` sur le rapport Markdown.

La suite scientifique concerne les données rares/bruitées pour ces ablations,
la sensibilité aux budgets d'entraînement et une référence Burgers davantage
validée. La validation tokamak et le contrôle restent des travaux futurs.
