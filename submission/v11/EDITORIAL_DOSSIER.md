---
title: "Article 1 - dossier de validation et de soumission"
author: "Youssef EL MOUTEE - document de travail"
date: "6 septembre 2026 - V11"
lang: fr-FR
---

# Sujet et plan conservés

Le sujet de thèse et le plan des articles restent ceux déjà engagés. L'Article 1 conserve son titre original : **Reference-Set Decoupled Co-Adaptive Training for Physics-Informed Neural Networks**. Les corrections portent sur la précision des affirmations, la bibliographie et la présentation du dossier.

# De quelle soumission parle-t-on ?

Il s'agit de proposer **un article scientifique** à une revue. Cela se distingue de l'inscription au doctorat, du dépôt de la thèse et de la soutenance. Le dépôt sur GitHub conserve le travail ; il ne soumet pas l'article à une revue.

L'auteur correspondant, désigné par l'équipe d'auteurs, ouvre le dossier sur la plateforme de la revue, renseigne les auteurs et joint manuscrit, figures, annexes et déclarations. Youssef peut tenir ce rôle s'il est désigné ; l'encadrant peut aussi le tenir. La qualité d'encadrant ne suffit pas, à elle seule, à fixer la liste ou l'ordre des auteurs.

Aucune date n'a été fixée. Le rappel prévu le 7 septembre est un point d'avancement, pas une échéance de dépôt. La soumission pourra avoir lieu après validation scientifique, informations d'auteurs complètes et approbation finale. Aucune revue n'a reçu ce manuscrit dans ce travail.

Après le dépôt, la rédaction peut rejeter l'article d'emblée ou le transmettre à des évaluateurs. Ceux-ci peuvent demander des révisions. L'auteur correspondant transmet ensuite une version révisée et une réponse point par point. L'acceptation éventuelle précède les épreuves et la publication. Les délais dépendent de la revue et des révisions ; aucune durée n'est promise.

# Revue retenue pour préparer le dossier

**Cible de travail : Journal of Computational Science, Elsevier, ISSN 1877-7503.** Mon appréciation est que l'étude comparative, ses contrôles numériques et sa reproductibilité correspondent au périmètre de recherche par simulation affiché par la revue. Cette adéquation ne préjuge pas de l'acceptation.

| Critère | Décision de préparation |
|---|---|
| Type de travail | Article de recherche numérique ; évaluation de ReCoA-PINN et de mécanismes concurrents |
| Format | Source LaTeX modifiable et PDF de lecture ; tableaux et figures numérotés |
| Évaluation | Le guide officiel indexé indique une évaluation en simple anonymat |
| Highlights | Cinq points, chacun inférieur ou égal à 85 caractères |
| Accès | Voie par abonnement envisagée : le site indique l'absence de frais de publication pour les auteurs sur cette voie |
| Accès ouvert | Option distincte ; aucun coût ni engagement n'est accepté dans cette préparation |
| Décision finale | À valider avec l'encadrant et les auteurs avant dépôt |

Alternative : **Journal of Computational Physics** si les auteurs jugent la contribution méthodologique suffisamment forte. La revue cible reste unique lors d'une soumission ; aucun dépôt simultané n'est préparé.

Sources consultées le 6 septembre 2026 : [périmètre de Journal of Computational Science](https://www.sciencedirect.com/journal/journal-of-computational-science), [guide des auteurs](https://www.sciencedirect.com/journal/journal-of-computational-science/publish/guide-for-authors), [options de publication](https://www.sciencedirect.com/journal/journal-of-computational-science/about/insights). Le guide complet a refusé l'ouverture directe ; les exigences ci-dessus proviennent des extraits officiels indexés. L'ensemble des champs de la plateforme devra être revérifié au moment du dépôt. Le résumé est volontairement limité à moins de 250 mots comme choix de préparation, sans présenter ce seuil comme vérifié pour cette revue.

# Auteurs et déclarations à confirmer

| Élément | Information disponible / validation requise |
|---|---|
| Auteur identifié dans le projet | Youssef EL MOUTEE |
| Encadrant identifié par Youssef | Professeur Adil Echchelh |
| Coauteurs et ordre | Non confirmés ; ne pas ajouter automatiquement l'encadrant |
| Affiliation de Youssef | À confirmer ; aucune affiliation universitaire déduite |
| Auteur correspondant et adresse | À désigner et à confirmer |
| ORCID | À renseigner si disponible ; aucun identifiant inventé |
| Contributions CRediT | À attribuer selon les contributions effectivement réalisées |
| Financement | À confirmer ; « aucun financement » n'est pas présumé |
| Conflits d'intérêts | Déclaration de chaque auteur à recueillir |
| Validation du contenu et du dépôt | Accord explicite de tous les auteurs à obtenir |

Le manuscrit de lecture identifie Youssef comme auteur de travail et signale les métadonnées non finalisées. Il ne contient ni signature, ni accord attribué à un coauteur.

# Résultat de la vérification sur une autre machine

L'exécution du 6 septembre 2026 sur un serveur Ubuntu GitHub indépendant a restauré les trois campagnes et passé **55 tests automatisés**. Les **560 scores** et les **96 contrastes statistiques** sont reproduits aux tolérances fixées avant l'exécution. Les **12 réentraînements** sont terminés ; leurs erreurs L2 et maximales respectent toutes les tolérances numériques prévues. L'écart absolu le plus élevé vaut $9{,}53\times10^{-9}$ en L2 et $1{,}40\times10^{-8}$ en erreur maximale.

Le contrôle strict comprenant l'identité binaire des données initiales reste à **8 réussites sur 12**. Les modèles initiaux sont identiques dans les douze cas ; les empreintes des jeux d'entraînement et de référence diffèrent pour les quatre essais bruités. L'environnement original utilisait PyTorch 2.14.0+cpu ; l'environnement public utilise 2.8.0+cpu. Les tableaux de données initiaux originaux n'ayant pas été archivés, les octets différents ne peuvent pas être localisés rétrospectivement. Un effet numérique de version ou d'environnement est plausible, sans preuve permettant de l'attribuer à une opération précise.

La conclusion retenue est donc une **reproduction numérique réussie, avec une limite documentée sur l'identité exacte des entrées**. Le fichier d'échec initial et les seuils restent inchangés. On ne remplace pas le résultat par un succès artificiel. Si une identité bit à bit est exigée, il faudra une campagne prospective archivant directement les tenseurs initiaux dans un environnement figé ; ce résultat n'est pas revendiqué dans le manuscrit.

Preuves : [exécution indépendante](https://github.com/ucef90/Doctorat/actions/runs/34021530276), résumés et CSV conservés dans `submission/v11/reproduction/`.

# Contribution proposée à la validation scientifique

La question de recherche reste celle du projet : l'utilisation d'un ensemble de référence fixe pour contrôler l'apprentissage coadaptatif des PINNs. Les expériences permettent une étude comparative contrôlée, mais ne démontrent ni une supériorité générale de M6, ni un gain de temps. Le titre original est conservé, avec un résumé qui annonce ces limites.

La relecture interne a précisé l'identité d'importance M7, la dépendance des trajectoires adaptatives, le rôle du jeu de référence, l'écrêtage suivi de renormalisation, les équations manufacturées et les familles statistiques. La bibliographie a été actualisée à partir des publications ou prépublications primaires, avec douze références dans le manuscrit. La nouveauté suffisante pour publication et l'interprétation finale doivent encore être examinées par l'encadrant et un lecteur scientifique humain.

# Avancement des cinq demandes

| Demande | Travail réalisé | Validation encore attendue |
|---|---|---|
| Contribution scientifique | Audit technique, positionnement et cinq questions de validation préparés | Avis de l'encadrant sur la contribution et la nouveauté |
| Autre machine | 560 modèles recalculés, 96 contrastes reconstruits, 12 réentraînements terminés | Accepter la limite d'identité des entrées ou demander une étude prospective plus stricte |
| Relecture et bibliographie | Relecture interne, corrections et références actualisées | Relecture scientifique humaine indépendante |
| Revue et auteurs | Journal of Computational Science retenu comme cible de préparation ; formulaire auteurs complet | Accord sur la revue, noms, ordre, affiliations, contact et déclarations |
| Dossier éditorial | Manuscrit, figures, annexes, sources LaTeX, highlights et lettre préparés | Guide complet au dépôt, intégration des retours et accord final des auteurs |

# Documents prêts pour la relecture

- `ARTICLE1_MANUSCRIPT_V11.pdf` : manuscrit anglais révisé, titre original conservé.
- `ARTICLE1_SUPPLEMENT_V11.pdf` : détails de protocole et ensemble des 96 contrastes V10, y compris résultats non significatifs.
- `SCIENTIFIC_AUDIT.md` : corrections et points à examiner par l'encadrant.
- `LITERATURE_UPDATE.md` et `references.json` : actualisation et bibliographie modifiable.
- `HIGHLIGHTS.txt` et `COVER_LETTER_DRAFT.md` : documents éditoriaux préparés.
- `reproduce_article1_v11.py` et workflow GitHub : reproduction et sous-ensemble de 12 entraînements fixés avant exécution.

# Grille de validation pour l'encadrant

1. Le titre et la question scientifique reflètent-ils correctement le projet doctoral maintenu ?
2. Les limites de M6 et de l'identité de correction M7 sont-elles correctement interprétées ?
3. La distinction entre résultats historiques et V09-V10 exploratoires est-elle suffisante ?
4. La contribution est-elle assez forte pour la revue retenue ? Une reproduction fidèle d'un concurrent ou une autre baseline de placement est-elle nécessaire pour les revendications maintenues ?
5. Les auteurs acceptent-ils le choix de la revue, leur contribution, leur affiliation et les déclarations ?

Une réponse écrite à ces points permettra d'intégrer les corrections avant la validation finale du manuscrit.

# Lettre de soumission préparée - à valider

Le brouillon ci-dessous n'est pas envoyé. Son ouverture au futur reflète l'absence actuelle d'approbation finale. Après validation des auteurs, l'auteur correspondant pourra adapter l'ouverture au dépôt effectif et ajouter les déclarations confirmées.

Dear Editors of the Journal of Computational Science,

We intend to submit the research manuscript entitled “Reference-Set Decoupled Co-Adaptive Training for Physics-Informed Neural Networks” for consideration as a research article, subject to final author approval.

The study examines whether evaluating a global loss controller on a fixed reference set improves co-adaptive PINN training. It compares this mechanism with coupled control, proposal correction, kernel-density volume weighting and variational residual attention on a common computational backbone. The results do not establish universal superiority of the fixed-reference method. Instead, the manuscript reports configuration-dependent benefits and limitations, supported by paired experiments, reference-solution validation and an explicit audit of observation-loss comparability.

The experimental package includes 200 V09 ablations and 560 additional V10 training runs. Frozen checkpoints, configurations, evaluation tables and analysis scripts accompany the study. The manuscript distinguishes exploratory findings, reused comparisons and computational timing limitations. Its emphasis on controlled numerical evidence and reproducible simulation motivates our selection of the Journal of Computational Science.

Before submission, the corresponding author will confirm the final author list and affiliations, originality and exclusive consideration, funding and competing-interest declarations, and approval of the final manuscript by all authors.

Sincerely,

Youssef EL MOUTEE

Corresponding-author designation, affiliation and contact details: pending confirmation.
