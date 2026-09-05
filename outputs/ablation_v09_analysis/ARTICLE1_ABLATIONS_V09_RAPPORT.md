# Article 1 — étude des mécanismes de vRBA

**Rapport expérimental v0.9 · 5 septembre 2026 · Youssef EL MOUTEE**

Statut : étude exploratoire avec protocole figé avant les nouveaux calculs. Ce document est un rapport de recherche et ne constitue pas un article accepté ou évalué par les pairs.

## Résultat et périmètre

La campagne comprend 200/200 entraînements terminés, dont 0 échec(s), et 60 fenêtres de chronométrage CPU enregistrées (59 essais complets et un essai interrompu après sa fenêtre de mesure). Les 40 blocs problème-germe ont des empreintes initiales concordantes. Les scores finaux ont été recalculés à partir des modèles sauvegardés.

La question est précise : quels effets produisent l'attention locale, l'équilibrage global et le choix du potentiel dans notre adaptation PyTorch de vRBA ? L'étude ne teste pas encore des données de tokamak, une boucle de contrôle ou une garantie de sûreté.

## 1. Position dans le projet doctoral

Titre doctoral de travail : **Trustworthy Physics-Informed Artificial Intelligence for Prediction and Control of Complex Dynamical Systems: Application to Tokamak Plasma Instabilities**.

Traduction : **Intelligence artificielle informée par la physique pour la prédiction et le contrôle fiables des systèmes dynamiques complexes : application aux instabilités du plasma dans les tokamaks**. La fiabilité constitue un objectif de recherche. L'explicabilité et le contrôle restent à définir et à valider dans leurs protocoles propres.

L'hypothèse initiale de supériorité d'une référence fixe M6 n'ayant pas reçu de soutien systématique dans le socle précédent, l'article s'oriente vers une étude contrôlée des mesures d'entraînement et de leurs compromis. Cette nouvelle campagne examine les composantes du comparateur externe vRBA ; elle ne rebaptise pas vRBA comme une invention du projet.

Référence externe : Toscano et al., [A variational framework for residual-based adaptivity in neural PDE solvers and operator learning](https://www.nature.com/articles/s44387-026-00084-4), et [annexe de la prépublication v2](https://arxiv.org/html/2509.14198v2). Les auteurs décrivent les potentiels et l'équilibrage ; notre architecture, nos budgets et nos problèmes manufacturés diffèrent de leurs expériences.

## 2. Plan expérimental et équité

| Variante | Attention locale | Équilibrage global | Potentiel |
|---|---|---|---|
| Sans adaptation | Non | Non, poids 1 | Inactif |
| Global seul | Non | Oui | Inactif |
| Local seul | Oui | Non, poids 1 | Exponentiel |
| Complet exp. | Oui | Oui | Exponentiel |
| Complet quad. | Oui | Oui | Quadratique |

Les quatre premiers bras forment un plan factoriel local × global. Le cinquième isole le potentiel. Dans tous les bras, les points restent fixes : cette ablation porte sur les poids et non sur un changement d'échantillonneur.

| Problème | Pas | Réseau caché | Collocation | Référence |
|---|---:|---|---:|---|
| Burgers | 2500 | 4 × 48, tanh | 512 | Rusanov + RK4, puis raffinement |
| Allen–Cahn forcée | 600 | 3 × 32, tanh | 256 | Solution manufacturée analytique |
| Helmholtz, k=1 | 1500 | 4 × 48, tanh | 512 | Solution manufacturée analytique |
| Ondes | 600 | 3 × 32, tanh | 256 | Onde stationnaire analytique |

Germes : 11, 22, 33, 44, 55, 66, 77, 88, 99, 111. Optimiseur Adam, pas 0,001, float64, un thread numérique par entraînement. Six processus servent au débit de la campagne. Les paramètres, points de conditions et points d'audit initiaux sont hachés depuis leurs tenseurs réels. Aucun score ne déclenche un arrêt anticipé ou l'exclusion d'un bras. Aucune donnée observée supplémentaire n'est utilisée.

La mémoire globale reste 0,99975 et la mémoire des gradients 0,99. Le potentiel quadratique conserve le même lissage phi=0,8 pour isoler le potentiel ; les auteurs utilisaient phi=1 dans leur configuration quadratique. Ces choix permettent une ablation contrôlée mais ne reproduisent pas exactement les recettes publiées.

## 3. Mesures et inférence

L2 relative = norme de l'erreur divisée par norme de la référence sur la grille. Ce nombre n'est pas une précision de classification. Le maximum est le plus grand écart absolu observé sur la grille ; ce n'est pas un maximum continu certifié. q95 et q99 désignent les percentiles de l'erreur dans le domaine, pas des intervalles de confiance. Le résidu physique RMS est évalué sur 4096 points indépendants.

Pour chaque EDP, les quatre contrastes prévus sont complet−local, complet−global, exponentiel−quadratique et interaction (complet−local−global+sans adaptation). Les différences sont calculées par germe avant agrégation. Pour l'interaction, une valeur négative indique un effet combiné inférieur à la somme additive des effets sur cette échelle d'erreur ; son interprétation dépend de l'échelle.

IC percentile bootstrap 95 % de la médiane des différences, 10000 tirages. Test exact bilatéral des signes, zéros exclus ; correction Holm sur 16 tests L2, puis une famille secondaire distincte de 16 tests pour le maximum. Les IC sont marginaux et ne sont pas simultanés. Un p non significatif ne prouve pas l'équivalence. Dix germes documentent la variabilité d'optimisation de ces cas ; ils ne représentent pas dix distributions physiques indépendantes.

## 4. Résultats sur les grilles historiques

### Erreur relative L2 médiane

| Problème | Sans adaptation | Global seul | Local seul | Complet exp. | Complet quad. |
|---|---:|---:|---:|---:|---:|
| Burgers · 2 500 pas | 0.29469 | 0.25149 | 0.20907 | 0.25075 | 0.24898 |
| Allen–Cahn forcée · 600 pas | 0.07197 | 0.06147 | 0.03875 | 0.04008 | 0.03812 |
| Helmholtz k=1 · 1 500 pas | 0.11228 | 0.09348 | 0.10469 | 0.03877 | 0.03377 |
| Ondes · 600 pas | 0.27737 | 0.27979 | 0.17097 | 0.17447 | 0.15107 |

### Maximum absolu médian

| Problème | Sans adaptation | Global seul | Local seul | Complet exp. | Complet quad. |
|---|---:|---:|---:|---:|---:|
| Burgers · 2 500 pas | 1.51370 | 1.42454 | 1.55079 | 1.72089 | 1.69886 |
| Allen–Cahn forcée · 600 pas | 0.13609 | 0.12642 | 0.06878 | 0.06905 | 0.06505 |
| Helmholtz k=1 · 1 500 pas | 0.23486 | 0.18810 | 0.13929 | 0.05237 | 0.05080 |
| Ondes · 600 pas | 0.51119 | 0.52005 | 0.24286 | 0.24276 | 0.21452 |

Les valeurs ci-dessus sont des médianes de scores. La différence de deux médianes n'est pas nécessairement la médiane des différences appariées utilisée ci-dessous.

### Contrastes L2 planifiés

| EDP | Contraste | Différence médiane | IC 95 % marginal | p Holm | Signes −/0/+ |
|---|---|---:|---|---:|---|
| burgers | full_exp-local_only | +0.01692 | [-0.02954 ; +0.08987] | 1.0000 | 4/0/6 |
| burgers | full_exp-global_only | -0.03756 | [-0.10079 ; +0.16523] | 1.0000 | 6/0/4 |
| burgers | full_exp-full_quad | +0.01337 | [-0.04886 ; +0.10203] | 1.0000 | 4/0/6 |
| burgers | interaction | +0.03203 | [-0.01012 ; +0.14315] | 1.0000 | 4/0/6 |
| allen_cahn | full_exp-local_only | -0.00146 | [-0.00355 ; +0.00403] | 1.0000 | 6/0/4 |
| allen_cahn | full_exp-global_only | -0.02535 | [-0.04054 ; -0.01203] | 0.2363 | 9/0/1 |
| allen_cahn | full_exp-full_quad | -0.00010 | [-0.00299 ; +0.00738] | 1.0000 | 6/0/4 |
| allen_cahn | interaction | +0.01163 | [+0.00332 ; +0.02119] | 0.2363 | 1/0/9 |
| helmholtz | full_exp-local_only | -0.06626 | [-0.07501 ; -0.05677] | 0.0312 | 10/0/0 |
| helmholtz | full_exp-global_only | -0.06179 | [-0.07324 ; -0.04424] | 0.0312 | 10/0/0 |
| helmholtz | full_exp-full_quad | +0.01069 | [-0.00835 ; +0.02312] | 1.0000 | 5/0/5 |
| helmholtz | interaction | -0.04704 | [-0.05941 ; -0.03654] | 0.0312 | 10/0/0 |
| wave | full_exp-local_only | +0.00739 | [+0.00072 ; +0.01142] | 0.9844 | 2/0/8 |
| wave | full_exp-global_only | -0.10973 | [-0.15761 ; -0.07640] | 0.0312 | 10/0/0 |
| wave | full_exp-full_quad | +0.02751 | [+0.01838 ; +0.03960] | 0.0312 | 0/0/10 |
| wave | interaction | +0.00398 | [-0.00180 ; +0.00666] | 1.0000 | 3/0/7 |

Les statistiques du maximum, les résultats individuels, q95/q99 et les résidus sont fournis dans paired_statistics.csv et evaluation.csv. Toutes les paires complètes sont conservées. Aucun germe favorable n'est choisi pour les tableaux.

## 5. Sensibilité de l'évaluation

La grille est raffinée de 161×81 à 321×161 pour Burgers, de 101×51 à 201×101 pour Allen–Cahn et les ondes, et de 101×101 à 201×201 pour Helmholtz. Aucun modèle n'est réentraîné pour cette vérification.

Pour Burgers, deux références numériques (257 puis 513 points, pas demandé 10⁻⁴ puis 5×10⁻⁵) diffèrent de 0.01825 en L2 relative et de 0.13207 au maximum sur la grille fine. Cette différence mesure la sensibilité numérique ; elle ne certifie pas l'erreur exacte de la référence la plus fine.

| Variante Burgers | Maximum historique | Grille fine, même référence | Grille et référence affinées |
|---|---:|---:|---:|
| Sans adaptation | 1.51370 | 1.55281 | 1.61296 |
| Global seul | 1.42454 | 1.42863 | 1.45499 |
| Local seul | 1.55079 | 1.57065 | 1.66843 |
| Complet exp. | 1.72089 | 1.72102 | 1.76623 |
| Complet quad. | 1.69886 | 1.69907 | 1.73995 |

Les cartes représentent la médiane ponctuelle des erreurs absolues entre germes. Elles ne sont ni la trajectoire d'un modèle médian ni une borne d'erreur.

## 6. Coût CPU mesuré séparément

60 essais supplémentaires : cinq variantes × trois germes × quatre EDP. Chaque processus exécute 200 pas. La mesure couvre les pas 51 à 150, après 50 pas d'échauffement, et inclut l'optimisation, les diagnostics et la journalisation. L'initialisation, la résolution finale de référence et les sauvegardes de fin sont exclues de cet intervalle. Les essais sont séquentiels et intercalés. Cette mesure décrit le coût local par pas, pas le temps pour atteindre une précision donnée.

| EDP | Variante | ms/pas médian | Ratio apparié au témoin | Pic RSS médian, MiB |
|---|---|---:|---:|---:|
| allen_cahn | Complet exp. | 5.967 | 1.774 | 801.7 |
| allen_cahn | Complet quad. | 5.452 | 1.565 | 803.3 |
| allen_cahn | Global seul | 5.336 | 1.516 | 803.5 |
| allen_cahn | Local seul | 3.620 | 1.039 | 803.8 |
| allen_cahn | Sans adaptation | 3.483 | 1.000 | 801.4 |
| burgers | Complet exp. | 13.316 | 1.864 | 843.5 |
| burgers | Complet quad. | 13.591 | 1.801 | 841.7 |
| burgers | Global seul | 12.635 | 1.704 | 840.0 |
| burgers | Local seul | 8.217 | 1.119 | 842.4 |
| burgers | Sans adaptation | 7.345 | 1.000 | 841.5 |
| helmholtz | Complet exp. | 19.468 | 1.821 | 834.4 |
| helmholtz | Complet quad. | 17.734 | 1.659 | 833.2 |
| helmholtz | Global seul | 17.579 | 1.685 | 833.5 |
| helmholtz | Local seul | 10.595 | 1.009 | 834.0 |
| helmholtz | Sans adaptation | 10.690 | 1.000 | 834.9 |
| wave | Complet exp. | 7.554 | 1.706 | 805.8 |
| wave | Complet quad. | 7.235 | 1.663 | 805.2 |
| wave | Global seul | 7.340 | 1.647 | 805.6 |
| wave | Local seul | 5.058 | 1.118 | 804.3 |
| wave | Sans adaptation | 4.471 | 1.000 | 806.1 |

Le dernier essai CPU (Helmholtz, local seul, germe 33) a été interrompu après le pas 150. Les pas 50 et 150 sont enregistrés : la fenêtre prévue est mesurée sans extrapolation. Son RSS final est indisponible ; la médiane mémoire de cette variante utilise deux mesures. Cet essai n'est pas compté comme terminé. Le RSS inclut Python, PyTorch et les données. Trois répétitions sont une mesure descriptive, sans garantie de précision fine du ratio. Aucun GPU CUDA n'était disponible ; aucun temps GPU ni consommation énergétique ne sont extrapolés.

## 7. Interprétation des résultats

**Helmholtz : l'association locale + globale est utile dans ce cas.** Le modèle complet exponentiel améliore L2 face à chacune des deux composantes seules sur les dix germes. L'interaction sur L2 est également négative sur les dix germes. Les trois contrastes restent significatifs après Holm (p=0,03125). Cela documente une interaction favorable dans cette configuration k=1 ; ce résultat ne se généralise pas automatiquement aux autres EDP.

**Ondes : le potentiel quadratique améliore L2 face à l'exponentiel.** Les dix différences appariées sont favorables au quadratique, avec p Holm=0,03125. L'avantage sur le maximum n'est pas confirmé après la correction des tests secondaires. Il faut donc conserver la distinction entre précision globale et erreur extrême.

**Burgers : les ablations ne désignent pas un gagnant statistiquement établi.** Le local seul obtient une médiane L2 inférieure au complet, mais les signes varient entre germes et aucun des contrastes planifiés ne passe Holm. Les médianes élevées des maxima persistent après raffinement. La référence numérique elle-même influe sur leur valeur : l'écart entre deux références atteint environ 0,132 localement. Un classement fin fondé sur de petits écarts de maximum doit donc rester prudent.

**Allen–Cahn forcée : pas de bénéfice supplémentaire établi du global face au local seul sur L2.** Le complet et le local seul ont des scores proches ; cela ne prouve pas une équivalence. Le complet améliore le maximum face au global seul sur dix germes (p Holm=0,03125, famille secondaire).

Ces résultats permettent d'affiner la question scientifique : pourquoi le couplage des pondérations aide-t-il Helmholtz, tandis que son intérêt est moins net dans les autres cas ? Ils ne justifient pas de sélectionner rétrospectivement une méthode unique puis de la présenter comme gagnante universelle.

## 8. Limites et décisions scientifiques

1. Cette campagne est exploratoire après observation de v0.7 et du pilote ; elle ne devient pas confirmatoire simplement parce que son lancement est figé.
2. Allen–Cahn est forcée/manufacturée et Helmholtz utilise k=1. La généralisation aux fronts raides, hautes fréquences et instabilités plasma n'est pas établie.
3. Les budgets sont hétérogènes entre EDP et restent courts par rapport à certaines dynamiques de pondération. Les comparaisons sont valides à budget égal au sein de chaque EDP ; elles ne prouvent pas une convergence asymptotique.
4. Une faible erreur L2 peut coexister avec un pic local. Un petit résidu physique n'est pas, sans analyse de stabilité de l'EDP, une garantie sur l'erreur de solution.
5. La comparaison à temps total égal, les données rares/bruitées pour ces ablations et une validation sur machine indépendante restent à réaliser.
6. Cette étude n'établit pas une nouvelle invention de vRBA. Une contribution scientifique possible est la caractérisation reproductible de ses interactions et de ses domaines d'échec, avec limites explicites.

## 9. Reproduction et audit

Les résultats individuels utilisent des chemins relatifs à la campagne ; les champs run_dir des anciens summary.json sont des traces du poste d'origine. Pour analyser une archive déplacée, utiliser scripts/analyze_vrba_campaign.py.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]' torch==2.14.0 numpy==2.3.5
PYTHONPATH=src python -m pytest
PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python scripts/run_vrba_campaign.py --output outputs/new_campaign --workers 6
# Reprise : même commande avec --resume, sans changement des sources ou réglages.
PYTHONPATH=src python scripts/analyze_vrba_campaign.py outputs/new_campaign --output outputs/new_analysis
# Profilage après la fin des autres calculs sur la machine :
PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python scripts/profile_vrba_cpu.py --output outputs/new_cpu_profile
```

La campagne archive le protocole, les configurations, les empreintes des sources, les versions et un pip freeze complet. Ce dernier décrit la machine de calcul ; ce n'est pas un verrou portable universel. PyTorch et NumPy sont explicitement épinglés dans la commande ci-dessus. La version de base du paquet reste 0.7.0 ; v0.9 identifie cette campagne et ses sources par empreintes.

Validation : 43 tests du socle et du lanceur réussis, puis trois tests statistiques réussis. La désactivation retrouve M0 sur les quatre EDP à tolérance 10⁻¹². Les scores sauvegardés ont été recalculés à tolérance relative 10⁻¹¹ / absolue 10⁻¹². Les tableaux et figures sont produits par scripts.

## 10. Livrables

- results.json et cells/ : les 200 trajectoires et états finaux de la campagne.
- evaluation.csv : erreurs historiques, grilles affinées, résidus et coûts par germe.
- pairing_audit.csv : concordance des conditions initiales des 40 blocs.
- paired_statistics.csv : les 32 contrastes avec IC, signes et correction Holm.
- reference_sensitivity.json : sensibilité de la référence Burgers.
- figures PNG/SVG et champs NPZ : données visualisables et exportables.
- dossier CPU : les 60 essais de profilage et leurs configurations.
- protocoles et scripts : reproduction et poursuite de l'étude.
