# Article 1 — reprise après le push V09

## Lire en premier

- `ARTICLE1_STATUS_V10.md` et `output/pdf/ARTICLE1_STATUS_V10.pdf` : bilan français.
- `ARTICLE1_MANUSCRIPT_V10.md` : manuscrit anglais consolidé, version de recherche.
- `BURGERS_REFERENCE_VALIDATION_V10.md` : référence indépendante et audit Huber/MSE.

La V10 ajoute 560 entraînements : 200 ablations sous données difficiles,
200 à nombre de pas doublé, puis 160 baselines sous perte commune. Les
40 comparateurs vRBA réutilisés dans la dernière comparaison ne sont pas
comptés comme de nouveaux entraînements. Les 560 modèles finaux sont
réévalués depuis leurs checkpoints, avec contrôle de l'appariement.
Les résultats sont exploratoires et ne prouvent pas une supériorité universelle.

Les versions V06–V09 demeurent historiques. Le manuscrit V10 est le point
d'entrée actuel ; l'ancien `ARTICLE1_MANUSCRIPT_DRAFT.md` n'intègre pas cette
extension. La version 0.7.0 du paquet Python reste celle du socle, distincte
du numéro de campagne V10.

## Résultats consultables

| Analyse | Dossier |
|---|---|
| Référence indépendante et 50 modèles Burgers V09 | `outputs/reference_v10_analysis/` |
| 200 ablations sous données difficiles | `outputs/robustness_v10_verified/` |
| 200 ablations à budget doublé, avec comparaison V09 | `outputs/budget_v10_analysis/` |
| M5/M6/M7/VW à perte commune, vRBA réutilisée | `outputs/common_loss_v10_analysis/` |

Les analyses fournissent les scores par germe, tests appariés et audits.
Les IC sont marginaux ; Holm est appliqué séparément aux familles L2 et
maximum. Les maxima restent des maxima sur grille.

## Archives brutes

Les modèles, trajectoires, configurations et manifestes complets des nouveaux
entraînements sont archivés sous `outputs/campaign_archives/`. L'inventaire
et les SHA-256 figurent dans `V10_RAW_ARCHIVES.json`. Tous les membres sont
comparés octet par octet aux originaux lors de la création. Les dossiers
extraits sont ignorés par Git pour éviter de stocker deux fois les modèles.

Depuis la racine du dépôt après récupération de la branche V10 :

```bash
python scripts/restore_article1_v10.py
```

Cette commande vérifie les SHA-256, réassemble les quatre parties de l'archive
de budget et reconstitue `outputs/*_v10_campaign/` pour les analyses. Les
archives logiques sont trois, mais celle de budget est stockée en quatre
parties pour permettre leur transfert. Aucune nouvelle clé n'est nécessaire.
Il n'est pas nécessaire d'importer un ZIP dans une conversation.

## Reproduction

PyTorch 2.14.0+cpu, NumPy 2.3.5, float64 et un thread numérique par processus.
Les six processus de campagne mesurent un débit parallèle, pas une efficacité
isolée. Les configurations, versions et empreintes exactes sont archivées.

```bash
python -m venv .venv
# Activer .venv suivant le système utilisé.
python -m pip install torch==2.14.0+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e '.[dev]' numpy==2.3.5 scipy reportlab
PYTHONPATH=src python -m pytest
PYTHONPATH=src python scripts/validate_burgers_reference.py --output outputs/reference_reproduction
PYTHONPATH=src python scripts/analyze_article1_extension.py outputs/robustness_v10_campaign --output outputs/robustness_reproduction
PYTHONPATH=src python scripts/analyze_article1_extension.py outputs/budget_v10_campaign --output outputs/budget_reproduction
PYTHONPATH=src python scripts/analyze_article1_baselines.py --output outputs/common_loss_reproduction
```

Choisir une destination neuve pour chaque analyse. `PYTHONPATH=src` utilise
une syntaxe POSIX ; en PowerShell, définir `$env:PYTHONPATH='src'` puis lancer
Python sans ce préfixe. L'installation éditable rend aussi le paquet importable.

Pour réentraîner : `run_article1_extension.py --suite robustness` ou `--suite
budget`, avec `--output` neuf. Le lanceur refuse une reprise si les sources
ou l'environnement ont changé. `run_article1_baselines.py` reprend les
configurations du manifeste de robustesse au chemin historique V10 : extraire
l'archive correspondante avant de l'utiliser. Un essai interrompu sans résultat
est conservé et nécessite une nouvelle destination dans ce lanceur complémentaire.

## Avant soumission

Une comparaison à temps égal reste nécessaire avant une revendication
d'efficacité temporelle. Une vérification sur machine indépendante et une
relecture scientifique externe restent à réaliser. Il faut également fixer
la revue, les auteurs, affiliations et déclarations avant mise en forme et
soumission. La réplication exacte du protocole JAX et la validation plasma
sont des extensions distinctes, non annoncées comme achevées.
