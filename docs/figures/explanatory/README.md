# Schémas explicatifs du projet ReCoA-PINN

Ces figures utilisent un même vocabulaire visuel et peuvent être intégrées au
rapport de thèse, à l’article ou à une présentation. Chaque figure est fournie
en PNG, PDF vectoriel et SVG éditable.

1. **Trajectoire de la thèse** — situe l’article méthodologique actuel par
   rapport à l’application finale au tokamak.
2. **Principe d’un PINN** — explique comment les données et les équations
   physiques entrent ensemble dans la fonction de coût.
3. **Problématique M5** — représente la boucle co-adaptative susceptible de
   produire un biais de sélection. Le risque reste une hypothèse testée, pas un
   fait général démontré.
4. **Solution M6** — montre le découplage entre les points adaptatifs
   d’entraînement et l’ensemble fixe utilisé par le contrôleur des pertes.
5. **Protocole contrôlé** — résume les méthodes, les quatre EDP, les dix germes,
   le bruit, les ablations et les métriques.
6. **Résultats actuels** — présente les contrastes appariés M6−M5 et leurs
   intervalles de confiance. Les intervalles traversent zéro : la supériorité
   générale de M6 n’est pas démontrée.
7. **Prochaine méthode M7** — illustre la correction par importance destinée à
   compenser la probabilité d’échantillonnage non uniforme.
8. **Application tokamak** — présente la future boucle capteurs, Physics-Informed
   AI, alerte d’instabilité et action de contrôle.

Régénération :

```bash
python scripts/generate_explanatory_figures.py
```
