# ReCoA-PINN — étude PyTorch reproductible multi-EDP

Ce dépôt implémente l’étude contrôlée proposée pour l’article :

> **Does a Fixed Reference Set Stabilize Co-Adaptive Physics-Informed Neural Networks? A Controlled Multi-Seed and Multi-PDE Study**

Il compare les méthodes suivantes sur Burgers, Allen–Cahn, Helmholtz et l’équation des ondes :

- **M0** : PINN standard, poids fixes et collocation uniforme ;
- **M1** : pondération adaptative et collocation uniforme ;
- **M3** : poids fixes et collocation résiduelle adaptative ;
- **M5** : pondération et échantillonnage adaptatifs utilisant le même lot adaptatif ;
- **M6 / ReCoA-PINN** : même adaptation que M5, mais le contrôleur des poids utilise des ensembles d’audit fixes.
- **M7U** : témoin utilisant exactement le tirage avec remise de M7, sans correction de mesure ;
- **M7** : entraînement co-adaptatif avec correction d'importance de la perte physique.
- **VW** : volume local estimé par KDE et poids de composantes fixes ;
- **VW-CA** : même correction de volume avec le contrôleur co-adaptatif, utilisée
  comme contrôle mécanistique de M7.
- **vRBA** : importance weighting local issu d'un potentiel variationnel
  exponentiel, combiné à l'auto-équilibrage global des composantes, sur le même
  backbone PyTorch et les mêmes points fixes.

La formulation mathématique, les hypothèses et les limites de M7 sont décrites
dans [`M7_MEASURE_CORRECTION.md`](M7_MEASURE_CORRECTION.md).
Le périmètre exact du baseline externe est consigné dans
[`VW_BASELINE_IMPLEMENTATION.md`](VW_BASELINE_IMPLEMENTATION.md).
Le protocole vRBA gelé avant les calculs se trouve dans
[`VRBA_BASELINE_PREREGISTRATION.md`](VRBA_BASELINE_PREREGISTRATION.md), et ses
résultats dans [`VRBA_RESULTS_REPORT.md`](VRBA_RESULTS_REPORT.md).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Vérification

```bash
python -m pytest
```

## Lancer une expérience

```bash
recoa-pinn train --config configs/pilot_quick.yaml --method m0 --seed 42
recoa-pinn train --config configs/pilot_quick.yaml --method m5 --seed 42
recoa-pinn train --config configs/pilot_quick.yaml --method m6 --seed 42
recoa-pinn train --config configs/pilot_quick.yaml --method m7 --seed 42
recoa-pinn train --config configs/pilot_quick.yaml --method vwca --seed 42
recoa-pinn train --config configs/pilot_quick.yaml --method vrba --seed 42
```

## Comparaison pilote appariée

```bash
recoa-pinn compare --config configs/pilot_quick.yaml --methods m5 m6 --seeds 11 22 33
```

Agrégation d’exécutions déjà produites :

```bash
recoa-pinn analyze --config configs/burgers_confirmatory_long.yaml \
  --methods m1 m5 m6 --seeds 11 22 33 44 55 66 77 88 99 111
```

Pour une campagne plus sérieuse :

```bash
recoa-pinn compare --config configs/pilot_full.yaml --methods m0 m1 m3 m5 m6 --seeds 11 22 33 44 55 66 77 88 99 111
```

Chaque exécution crée un dossier contenant :

- `config.resolved.yaml` : configuration exacte ;
- `environment.json` : versions Python, PyTorch, CUDA et plateforme ;
- `metrics.csv` : trajectoires des pertes, poids et diagnostics ;
- `summary.json` : métriques finales et statut ;
- `model.pt` : paramètres entraînés.

## Campagne automatique : entraînements, tableaux et graphiques

Le manifeste décrit les EDP, méthodes, germes et contrastes appariés. Une seule
commande exécute les runs absents, réutilise les runs réussis et génère le dossier
de résultats de l’article :

```bash
recoa-pinn campaign --manifest configs/article1_pilot_campaign.yaml --workers 1
```

Pilote apparié de la correction de mesure :

```bash
recoa-pinn campaign --manifest configs/m7_pilot_campaign.yaml --workers 1
```

Comparaison pilote M7–VW, puis campagnes à dix germes :

```bash
recoa-pinn campaign --manifest configs/vw_pilot_campaign.yaml --workers 1
recoa-pinn campaign --manifest configs/vw_confirmatory_campaign.yaml --workers 1
recoa-pinn campaign --manifest configs/vw_robustness_campaign.yaml --workers 1
recoa-pinn campaign --manifest configs/vw_bandwidth_sensitivity_campaign.yaml --workers 1
recoa-pinn campaign --manifest configs/helmholtz_calibrated_campaign.yaml --workers 4
```

Baseline vRBA pré-enregistré, puis validation à dix germes :

```bash
recoa-pinn campaign --manifest configs/vrba_pilot_campaign.yaml --workers 1
recoa-pinn campaign --manifest configs/vrba_confirmatory_campaign.yaml --workers 1
recoa-pinn campaign --manifest configs/vrba_robustness_campaign.yaml --workers 1
```

Analyse spatiale du compromis L2–erreur maximale sur Burgers :

```bash
python scripts/analyze_vrba_burgers_spatial.py
```

Pour reconstruire les tableaux et figures sans relancer les entraînements :

```bash
recoa-pinn campaign --manifest configs/article1_results_campaign.yaml --report-only
```

Le rapport automatique contient :

- `data/runs.csv` : données brutes aplaties, une ligne par germe et méthode ;
- `tables/method_summary.csv` : médiane, quartiles et IC bootstrap à 95 % ;
- `tables/paired_summary.csv` : différences appariées, taux de victoire et test des signes ;
- `tables/*.tex` : tables LaTeX prêtes pour le manuscrit ;
- `figures/*.png` et `figures/*.pdf` : boîtes à moustaches, forêt des contrastes,
  compromis coût–précision et courbes de convergence ;
- `REPORT.md` : synthèse lisible et contrôle de complétude.

L’option `--force` réexécute tous les runs. Sans cette option, une campagne
interrompue reprend uniquement les cellules manquantes. `--report-only` ne lance
aucun entraînement et laisse visibles les runs manquants.

## Garanties de reproductibilité

- germes Python, NumPy, PyTorch et CUDA fixés ;
- algorithmes PyTorch déterministes demandés ;
- générateurs distincts pour entraînement, audit, évaluation et échantillonnage ;
- cardinalité des points de collocation constante ;
- mêmes budgets et mêmes germes pour les comparaisons appariées ;
- environnement et configuration sauvegardés automatiquement.

Sur un matériel différent, PyTorch peut conserver une légère variabilité numérique. Les conclusions de l’article devront donc être fondées sur plusieurs germes appariés et des intervalles de confiance, pas sur une seule exécution.

## Données rares, bruit et ablations

Les configurations `burgers_data_*.yaml` couvrent données propres rares, bruit gaussien, bruit hétéroscédastique, valeurs aberrantes, bruit corrélé et bloc de capteurs manquant. Les observations sont identiques dans chaque paire M5–M6 et les cibles d’évaluation restent propres.

La matrice d’ablation s’exécute avec :

```bash
python scripts/run_ablation_matrix.py --workers 4
```

Elle couvre la source adaptative, quatre tailles d’audit, plans aléatoire/Latin-hypercube/Sobol, rotation lente, suppression du lissage, du bornage et du plancher uniforme, ainsi que des fréquences différentes.

## Statut scientifique

Ce dépôt contient désormais une campagne multi-germes et multi-EDP. Les résultats ne valident pas une supériorité générale de M6 : le dépôt doit être présenté comme une étude contrôlée, avec résultats positifs, nuls et défavorables.

Les résultats du contrôle technique initial sont consignés dans [`PILOT_RESULTS.md`](PILOT_RESULTS.md). Ils ne doivent pas être repris comme résultats définitifs dans l’article.

La formulation et les résultats de la correction de mesure sont documentés dans
[`M7_MEASURE_CORRECTION.md`](M7_MEASURE_CORRECTION.md) et
[`M7_RESULTS_REPORT.md`](M7_RESULTS_REPORT.md). M7 montre un signal robuste sur
les régimes Burgers à données rares/bruitées, mais pas de supériorité générale
sur toutes les EDP.

La synthèse actuelle, intégrant VW/VW-CA, la sensibilité KDE, Helmholtz
recalibrée et vRBA, se trouve dans
[`ARTICLE1_EVIDENCE_REPORT_V07.md`](ARTICLE1_EVIDENCE_REPORT_V07.md). La
campagne contient 973 entraînements réussis et 32 tests automatisés. vRBA
améliore l'erreur L2 sur les quatre EDP et les quatre régimes de données
difficiles, mais ne domine ni l'erreur maximale de Burgers ni le coût ; la
conclusion reste donc conditionnelle.

Le plan expérimental détaillé et les critères de réfutation sont définis dans [`SCIENTIFIC_VALIDATION_PROTOCOL.md`](SCIENTIFIC_VALIDATION_PROTOCOL.md). Les décisions chiffrées sont dans [`SCIENTIFIC_RESULTS_REPORT.md`](SCIENTIFIC_RESULTS_REPORT.md). La revue ciblée se trouve dans [`SYSTEMATIC_LITERATURE_REVIEW_2025_2026.md`](SYSTEMATIC_LITERATURE_REVIEW_2025_2026.md), complétée par [`NOVELTY_MATRIX.md`](NOVELTY_MATRIX.md).
