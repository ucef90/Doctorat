# Article 1 — V11, préparation à la validation

6 septembre 2026. Sujet doctoral et plan des articles maintenus. Titre original conservé : **Reference-Set Decoupled Co-Adaptive Training for Physics-Informed Neural Networks**.

## PDF et archive de contrôle

- [Manuscrit de relecture](output/pdf/ARTICLE1_MANUSCRIPT_V11.pdf).
- [Annexes et statistiques complètes](output/pdf/ARTICLE1_SUPPLEMENT_V11.pdf).
- [Dossier de validation et lettre](output/pdf/ARTICLE1_DOSSIER_VALIDATION_V11.pdf).
- [Archive complète du contrôle indépendant](outputs/campaign_archives/v11_independent_reproduction.zip) : 12 modèles, trajectoires, configurations et sorties originales. SHA-256 : `f0ea2da69b46dea7244318efef055a658da6d61a15372689283946c4ad005f17`.

Voir aussi le [mode d’emploi du dépôt en revue](submission/v11/MODE_EMPLOI_DEPOT_FR.md) : pièces à fournir, rôle du mail et étapes du portail.

## Lire et relire

- `submission/v11/MANUSCRIPT.md` et `ARTICLE1_MANUSCRIPT_V11.tex` : manuscrit révisé, affirmations scientifiques resserrées.
- `submission/v11/SUPPLEMENT.md` et `ARTICLE1_SUPPLEMENT_V11.tex` : protocole, 96 contrastes complets et reproduction indépendante.
- `submission/v11/EDITORIAL_DOSSIER.md` et `ARTICLE1_DOSSIER_VALIDATION_V11.tex` : explication du dépôt, revue cible, grille de validation, auteurs et lettre.
- `submission/v11/SCIENTIFIC_AUDIT.md` : relecture technique interne ; la validation humaine reste requise.
- `submission/v11/LITERATURE_UPDATE.md`, `references.json` : sources actualisées et métadonnées bibliographiques.
- `submission/v11/HIGHLIGHTS.txt`, `COVER_LETTER_DRAFT.md` : éléments éditoriaux modifiables.

## Ce qui a été réellement vérifié

[Exécution sur un serveur Ubuntu indépendant](https://github.com/ucef90/Doctorat/actions/runs/34021530276), commit de protocole `9d805e223d795a86852d5dc9ebc3e7d843aab51e` :

- 55 tests automatisés réussis.
- 560 modèles V10 restaurés, scores recalculés et conformes aux tolérances préfixées.
- 96 contrastes statistiques reconstruits et conformes.
- 12 réentraînements choisis avant exécution, tous terminés et numériquement conformes.
- Critère conjoint strict : 8/12, échec global conservé. Les quatre cas bruités ont des empreintes de jeux initiaux différentes. Les empreintes des modèles initiaux concordent dans les douze cas.

Les écarts absolus maximaux après réentraînement sont 9,53e-9 pour L2 et 1,40e-8 pour l'erreur maximale. Les tolérances et l'échec original n'ont pas été modifiés. L'identité exacte des entrées n'est pas revendiquée. `submission/v11/reproduction/` conserve le protocole, les environnements, les tableaux complets, les résumés des 12 modèles et l'interprétation explicite. Le test porte sur un changement de machine **et** de version PyTorch, pas sur une pile logicielle identique.

## Construire les trois PDF

Le dossier utilise LaTeX générique pour une copie de relecture, sans prétendre avoir vérifié chaque champ du guide éditorial complet. Depuis la racine du dépôt, avec Python, matplotlib, Pandoc, XeLaTeX et les polices Latin Modern Roman / DejaVu Sans Mono installés :

```bash
python scripts/restore_article1_v10.py
python scripts/prepare_article1_v11.py --output outputs/article1_v11_pdf
```

Le script régénère les sources LaTeX et la figure à partir des données archivées. Les anciens PNG et le nouveau PDF vectoriel des figures sont conservés dans le dépôt. Les PDF finaux ont été rendus et inspectés séparément pour la livraison. Le code numérique V10 et ses résultats historiques sont inchangés.

## Reproduire les expériences

La procédure et les versions publiques figées sont dans `.github/workflows/article1-independent-reproduction.yml`. Le workflow peut être lancé manuellement sur GitHub. Il conserve une sortie en échec si les empreintes ne concordent pas, même lorsque les erreurs finales respectent les tolérances. Un lancement local ne constitue pas une reproduction sur une autre machine. Le répertoire de sortie doit être nouveau.

```bash
python scripts/restore_article1_v10.py
python -m pytest
python scripts/reproduce_article1_v11.py --output outputs/v11_reproduction
```

## Ce qui reste avant un dépôt

1. Avis de l'encadrant sur la contribution et le choix de revue ; relecture scientifique humaine.
2. Confirmation de la liste et de l'ordre des auteurs, affiliations, auteur correspondant, coordonnées, contributions, financement et conflits d'intérêts.
3. Intégration des retours, vérification du guide complet et des champs de dépôt, approbation finale de tous les auteurs.
4. Une campagne archivant les tenseurs initiaux sera nécessaire si une identité bit à bit est exigée ; la reproduction numérique actuelle est documentée avec sa limite.
5. Une comparaison à temps égal sera nécessaire **avant toute revendication de gain de temps**, absente de la présente version.

La revue cible de préparation est **Journal of Computational Science**. Aucun article n'est soumis, aucune date de dépôt n'est fixée. L'auteur correspondant désigné soumettra l'Article 1 après accord des auteurs. Le rappel du 7 septembre est un point d'avancement.
