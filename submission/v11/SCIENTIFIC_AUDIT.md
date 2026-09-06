# Audit scientifique interne - Article 1 V11

6 septembre 2026. Relecture technique assistée par IA ; elle ne constitue pas une relecture externe par un chercheur ni une validation de l'encadrant.

## Périmètre conservé

Le sujet doctoral, l'orientation physique déjà choisie et le plan des articles sont conservés. Le titre original de l'Article 1 est rétabli : **Reference-Set Decoupled Co-Adaptive Training for Physics-Informed Neural Networks**. Le manuscrit teste cette proposition, y compris lorsque les résultats sont nuls ou défavorables. Aucun changement vers une thèse thermique n'est effectué.

## Corrections apportées au manuscrit

1. **Correction d'importance M7.** L'identité de Hansen-Hurwitz est précisée pour un tirage frais, conditionnellement au modèle et au bassin candidat figés. Les points conservés proviennent de propositions antérieures ; le modèle dépend des données utilisées pour l'entraîner. L'identité ne démontre donc pas une absence de biais conditionnel de tous les gradients successifs ni la convergence du réseau.
2. **Appariement M7/M7U.** Même architecture, graine, protocole et flux aléatoires ne signifient pas mêmes points adaptatifs à toutes les étapes. Les propositions dépendent des réseaux, dont les trajectoires divergent. La formulation « same draws » est corrigée.
3. **Ensemble de référence.** Il est indépendant du tirage initial de collocation, mais intervient dans le contrôleur. Ce n'est pas un jeu de test indépendant du modèle final. Les capteurs et cibles d'observation sont partagés ; M6 ne reçoit pas de mesures supplémentaires.
4. **Bornes du contrôleur.** Dans le code V10, les cibles sont écrêtées puis renormalisées. Les paramètres `weight_min` et `weight_max` ne sont pas des bornes strictes des poids après cette renormalisation. La V11 décrit la séquence réellement exécutée ; aucun entraînement historique n'est modifié.
5. **Formulation des EDP.** Les équations, domaines, solutions manufacturées et conditions initiales sont explicités. Le cas Allen-Cahn est forcé et manufacturé ; il ne représente pas la résolution du benchmark non forcé difficile souvent utilisé dans la littérature.
6. **Séparation des campagnes.** Les 200 ablations V09 et 560 nouveaux entraînements V10 restent distincts. Les 40 modèles vRBA réutilisés ne sont pas comptés comme des répétitions indépendantes.
7. **Portée des statistiques.** Les familles Holm contiennent 16 contrastes par métrique et par campagne. Les intervalles bootstrap sont marginaux. Les tests portent sur des graines appariées, pas sur 560 systèmes physiques indépendants. L'inférence est exploratoire.
8. **Comparateurs modernes.** Les prépublications de Chen et al. (2025) et Singh et al. (2026) sont citées explicitement. M5 ne devient pas, par similarité, une reproduction fidèle de Singh et al. Les méthodes PINNACLE, QR-DEIM et PACMANN sont discutées sans prétendre avoir été exécutées.
9. **Bibliographie.** Les métadonnées de six DOI centraux sont contrôlées via Crossref, en complément des pages primaires. VW-PINNs a une mise en ligne en 2024 et un volume imprimé en 2025. La revue de Torres et al. concerne surtout transfert et méta-apprentissage ; son rôle dans l'ancien état de l'art était trop large. PINNACLE est accepté à ICLR 2024.
10. **Performance et temps.** Les tableaux conservent les résultats favorables et défavorables. Aucun gain de vitesse global ni domination de M6 n'est revendiqué. Les temps historiques ne sont pas réunis avec les temps V10 sous parallélisme pour construire une comparaison artificielle.
11. **Assistance IA.** Son utilisation pour le code, l'analyse, la recherche bibliographique et la rédaction est décrite. La validation humaine reste explicitement à réaliser ; le texte n'affirme pas qu'elle a déjà eu lieu.

## Avis technique préparé pour l'encadrant

La question de recherche est testable et les résultats disponibles justifient une étude critique du découplage par ensemble de référence. Ils ne démontrent pas que ReCoA-PINN/M6 soit universellement plus précis ou plus stable. La contribution défendable combine un protocole contrôlé, une analyse des mesures d'entraînement, l'audit d'une référence numérique et des expériences de sensibilité. Le titre original décrit la méthode étudiée ; le résumé doit annoncer honnêtement ses limites.

Le manuscrit V11 apporte une description scientifique plus précise et des annexes vérifiables. Une validation par l'encadrant reste nécessaire sur la nouveauté suffisante pour la revue, l'interprétation des diagnostics de stabilité et le niveau d'approfondissement des comparateurs contemporains.

## Points que la préparation technique ne peut pas approuver

- Accord scientifique de l'encadrant et relecture par une personne extérieure au travail automatisé.
- Liste et ordre des auteurs, affiliations, rôles CRediT et auteur correspondant.
- Déclarations individuelles de financement, conflits d'intérêts et approbation finale.
- Date du dépôt et engagement des auteurs à soumettre à la revue retenue.

## Compléments dépendant des revendications

Une comparaison à temps égal est requise avant une affirmation de meilleure efficacité temporelle. Une reproduction fidèle d'un concurrent et une baseline moderne de placement deviennent particulièrement importantes si une supériorité vis-à-vis de l'état de l'art est revendiquée. La présente version limite ses conclusions aux mécanismes comparés sur le même socle. Elle ne revendique aucune validation expérimentale de plasma.

## Résultat de la reproduction indépendante

Les 560 scores, 96 contrastes et erreurs finales des 12 réentraînements sont reproduits aux tolérances préfixées. Le critère conjoint strict reste à 8/12 à cause d'empreintes initiales différentes pour les quatre cas bruités. Cette limite est exposée dans le manuscrit et dans `reproduction/interpretation.json`, sans effacer l'échec original. Leurs erreurs finales diffèrent au plus de 1,40 × 10⁻⁸ ; une explication exacte de la différence d'empreinte n'est pas établie.
