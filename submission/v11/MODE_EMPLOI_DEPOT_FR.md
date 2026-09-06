# Article 1 — quoi partager, avec qui et comment ?

6 septembre 2026. Revue cible de préparation : **Journal of Computational Science**. Le sujet doctoral et le titre original de l'Article 1 sont conservés. La copie V11 est destinée à la relecture ; aucune soumission en revue n'est effectuée par ce document ou par le push GitHub.

## 1. D'abord, faire relire par l'encadrant

Youssef peut envoyer un mail à son encadrant avec les trois PDF V11 : manuscrit, annexes et dossier français de validation. Ajouter le lien de la branche GitHub pour consulter le code et les résultats. Le dossier français explique la contribution proposée et les points de validation ; il est destiné au travail avec l'encadrement.

Demander l'avis scientifique, les corrections, le choix de revue et la composition de l'équipe d'auteurs. La qualité d'encadrant ne suffit pas à déterminer automatiquement l'ordre des auteurs ou l'auteur correspondant. Aucun mail n'a été envoyé dans cette préparation.

## 2. Le dépôt officiel se fait sur la plateforme de la revue

Ouvrir la [page officielle du Journal of Computational Science](https://www.sciencedirect.com/journal/journal-of-computational-science), puis **Submit your article**. Utiliser le portail désigné par la revue et y créer un compte auteur. L'auteur correspondant peut être Youssef ou un autre coauteur désigné par l'équipe.

La procédure Elsevier Editorial Manager comprend le choix du type d'article, la saisie des informations, l'ajout des fichiers, la vérification du PDF assemblé et l'approbation finale. Les étapes et champs peuvent varier selon la revue et le type d'article. Un mail contenant les pièces ne remplace pas ce dépôt en ligne. Les mails servent notamment aux échanges, notifications et demandes de révision.

Sources officielles : [soumettre dans Editorial Manager](https://www.elsevier.support/publishing/answer/how-do-i-submit-a-manuscript-in-editorial-manager), [approuver le dépôt après vérification du PDF](https://www.elsevier.support/publishing/answer/how-can-i-approve-my-submission).

## 3. Les pièces à préparer pour notre article

| Pièce | Contenu à fournir | État / emplacement du projet |
|---|---|---|
| Manuscrit | Article anglais final, titre, résumé, mots-clés, méthodes, résultats, discussion et références | Copie de relecture : `output/pdf/ARTICLE1_MANUSCRIPT_V11.pdf` ; source `submission/v11/ARTICLE1_MANUSCRIPT_V11.tex` |
| Sources modifiables | LaTeX, fichiers bibliographiques et éléments nécessaires à la compilation | `submission/v11/`, avec les figures du projet et `scripts/prepare_article1_v11.py` ; à adapter aux fichiers attendus par le portail |
| Figures et tableaux | Versions lisibles et numérotées, fichiers séparés lorsque demandés | Figures intégrées au manuscrit ; fichiers et données d'origine conservés dans le dépôt |
| Annexes scientifiques | Détails des protocoles, statistiques complètes et limites de reproductibilité | `output/pdf/ARTICLE1_SUPPLEMENT_V11.pdf` et source LaTeX correspondante |
| Highlights | 3 à 5 points, au plus 85 caractères chacun, fichier modifiable séparé | Les 5 points de `submission/v11/HIGHLIGHTS.txt` sont préparés |
| Lettre à la rédaction | Présentation courte du travail, de sa contribution et de son adéquation à la revue | `submission/v11/COVER_LETTER_DRAFT.md` ; à finaliser après accord des auteurs, idéalement en une page |
| Informations des auteurs | Noms, ordre, affiliations, contact du correspondant, ORCID si disponible, contributions | À confirmer et à saisir dans les champs du portail ; le dossier français contient la grille |
| Déclarations | Financement, conflits d'intérêts, disponibilité du code et des données, approbation des auteurs | À confirmer ; le texte ne doit pas attribuer un accord qui n'a pas encore été obtenu |
| Code et données | Lien vers une version précise, instructions d'installation, configurations, scripts, résultats et archives de modèles utiles | Dépôt `ucef90/Doctorat`, manifestes et archives ; citer le commit figé retenu au dépôt |

Le [guide officiel de la revue](https://www.sciencedirect.com/journal/journal-of-computational-science/publish/guide-for-authors) demande des sources modifiables et précise les highlights. Son ouverture intégrale est indisponible dans cette session : ces points sont vérifiés via les extraits officiels indexés. Les exigences complètes, formats, tailles limites et éventuels champs supplémentaires devront être contrôlés sur le portail avant l'approbation finale. Une copie PDF seule ne doit pas être supposée suffisante pour toutes les étapes.

La [fiche Elsevier sur la lettre](https://www.elsevier.support/publishing/answer/what-should-be-included-in-a-cover-letter) recommande une lettre courte et place les informations administratives demandées dans les champs séparés. Le brouillon existant contient encore un paragraphe de travail sur les validations à obtenir : le retirer de la lettre définitive et compléter les rubriques appropriées après confirmation des auteurs.

## 4. Comment partager le code et les résultats

Le manuscrit doit donner un accès précis au code et aux données qui permettent de vérifier les résultats. Pour notre projet : lien vers la version GitHub figée, `START_HERE_V11.md`, scripts de restauration et de reproduction, tableaux, configurations et archives de modèles. Le dépôt actuel est public : il reste accessible même si le compte est peu connu.

Il n'est pas nécessaire d'envoyer les 560 modèles en pièces jointes à chaque mail. Les déposer ou les référencer dans l'espace prévu pour les données et annexes, conformément aux exigences finales de la revue. Un dépôt d'archive avec identifiant pérenne peut compléter GitHub si les auteurs ou la revue le demandent ; aucun DOI n'a été créé ici. Le portail doit recevoir le manuscrit lui-même : un lien GitHub seul ne constitue pas une soumission.

Les fichiers historiques V06–V10 et la thèse entière ne sont pas à joindre automatiquement au dossier éditorial de l'Article 1. Le dossier français de validation reste un document interne à l'équipe ; les annexes scientifiques en anglais sont le complément destiné à l'évaluation.

## 5. Dernière vérification avant de cliquer sur la validation finale

1. Intégrer les retours scientifiques et obtenir l'accord des auteurs.
2. Confirmer revue, auteurs, affiliations, déclarations et correspondant.
3. Vérifier le guide complet et préparer la version finale des fichiers demandés.
4. Renseigner les informations, téléverser les pièces et associer les liens code/données.
5. Ouvrir le PDF assemblé par le portail et vérifier texte, équations, figures et auteurs.
6. Approuver le dépôt seulement après cette vérification et les accords requis.

Après le dépôt, la rédaction peut demander une correction technique, refuser l'article ou organiser une évaluation scientifique. Les révisions et réponses aux évaluateurs se déposent ensuite dans le même dossier. Aucun délai d'acceptation ni acceptation n'est garanti.
