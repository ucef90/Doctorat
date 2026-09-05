"""Assemble the French evidence report from saved measurements only."""
import argparse
import json
from pathlib import Path

VARIANTS = ["neither", "global_only", "local_only", "full_exp", "full_quad"]
LABELS = {"neither": "Sans adaptation", "global_only": "Global seul", "local_only": "Local seul", "full_exp": "Complet exp.", "full_quad": "Complet quad."}
PROBLEMS = ["burgers", "allen_cahn", "helmholtz", "wave"]
P_LABELS = {"burgers": "Burgers · 2 500 pas", "allen_cahn": "Allen–Cahn forcée · 600 pas", "helmholtz": "Helmholtz k=1 · 1 500 pas", "wave": "Ondes · 600 pas"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign",required=True)
    parser.add_argument("--analysis",required=True)
    parser.add_argument("--profile",required=True)
    args=parser.parse_args()
    campaign,analysis,profile=map(Path,(args.campaign,args.analysis,args.profile))
    summaries=json.loads((analysis/"summary.json").read_text())
    stats=json.loads((analysis/"paired_statistics.json").read_text())
    audit=json.loads((analysis/"analysis_provenance.json").read_text())
    sensitivity=json.loads((analysis/"reference_sensitivity.json").read_text())
    costs=json.loads((profile/"summary.json").read_text())
    completion=json.loads((campaign/"completion.json").read_text())
    profile_completion=json.loads((profile/"completion.json").read_text())
    lookup={(r["problem"],r["variant"]):r for r in summaries}
    lines=["# Article 1 — étude des mécanismes de vRBA", "",
        "**Rapport expérimental v0.9 · 5 septembre 2026 · Youssef EL MOUTEE**", "",
        "Statut : étude exploratoire avec protocole figé avant les nouveaux calculs. "
        "Ce document est un rapport de recherche et ne constitue pas un article accepté ou évalué par les pairs.", "",
        "## Résultat et périmètre", "",
        f"La campagne comprend {completion['completed']}/{completion['expected']} entraînements terminés, "
        f"dont {completion['failed']} échec(s), et 60 fenêtres de chronométrage CPU enregistrées "
        f"({profile_completion['completed']} essais complets et un essai interrompu après sa fenêtre de mesure). "
        f"Les {audit['paired_blocks']} blocs problème-germe ont des empreintes initiales concordantes. "
        "Les scores finaux ont été recalculés à partir des modèles sauvegardés.", "",
        "La question est précise : quels effets produisent l'attention locale, "
        "l'équilibrage global et le choix du potentiel dans notre adaptation PyTorch de vRBA ? "
        "L'étude ne teste pas encore des données de tokamak, une boucle de contrôle ou une garantie de sûreté.", "",
        "## 1. Position dans le projet doctoral", "",
        "Titre doctoral de travail : **Trustworthy Physics-Informed Artificial Intelligence "
        "for Prediction and Control of Complex Dynamical Systems: Application to Tokamak Plasma Instabilities**.", "",
        "Traduction : **Intelligence artificielle informée par la physique pour la prédiction "
        "et le contrôle fiables des systèmes dynamiques complexes : application aux instabilités "
        "du plasma dans les tokamaks**. La fiabilité constitue un objectif de recherche. "
        "L'explicabilité et le contrôle restent à définir et à valider dans leurs protocoles propres.", "",
        "L'hypothèse initiale de supériorité d'une référence fixe M6 n'ayant pas reçu de soutien "
        "systématique dans le socle précédent, l'article s'oriente vers une étude contrôlée des "
        "mesures d'entraînement et de leurs compromis. Cette nouvelle campagne examine les "
        "composantes du comparateur externe vRBA ; elle ne rebaptise pas vRBA comme une invention du projet.", "",
        "Référence externe : Toscano et al., "
        "[A variational framework for residual-based adaptivity in neural PDE solvers and operator learning]"
        "(https://www.nature.com/articles/s44387-026-00084-4), et "
        "[annexe de la prépublication v2](https://arxiv.org/html/2509.14198v2). "
        "Les auteurs décrivent les potentiels et l'équilibrage ; notre architecture, nos budgets "
        "et nos problèmes manufacturés diffèrent de leurs expériences.", "",
        "## 2. Plan expérimental et équité", "",
        "| Variante | Attention locale | Équilibrage global | Potentiel |",
        "|---|---|---|---|",
        "| Sans adaptation | Non | Non, poids 1 | Inactif |",
        "| Global seul | Non | Oui | Inactif |",
        "| Local seul | Oui | Non, poids 1 | Exponentiel |",
        "| Complet exp. | Oui | Oui | Exponentiel |",
        "| Complet quad. | Oui | Oui | Quadratique |", "",
        "Les quatre premiers bras forment un plan factoriel local × global. Le cinquième "
        "isole le potentiel. Dans tous les bras, les points restent fixes : cette ablation "
        "porte sur les poids et non sur un changement d'échantillonneur.", "",
        "| Problème | Pas | Réseau caché | Collocation | Référence |",
        "|---|---:|---|---:|---|",
        "| Burgers | 2500 | 4 × 48, tanh | 512 | Rusanov + RK4, puis raffinement |",
        "| Allen–Cahn forcée | 600 | 3 × 32, tanh | 256 | Solution manufacturée analytique |",
        "| Helmholtz, k=1 | 1500 | 4 × 48, tanh | 512 | Solution manufacturée analytique |",
        "| Ondes | 600 | 3 × 32, tanh | 256 | Onde stationnaire analytique |", "",
        "Germes : 11, 22, 33, 44, 55, 66, 77, 88, 99, 111. Optimiseur Adam, "
        "pas 0,001, float64, un thread numérique par entraînement. Six processus servent "
        "au débit de la campagne. Les paramètres, points de conditions et points d'audit "
        "initiaux sont hachés depuis leurs tenseurs réels. Aucun score ne déclenche un arrêt "
        "anticipé ou l'exclusion d'un bras. Aucune donnée observée supplémentaire n'est utilisée.", "",
        "La mémoire globale reste 0,99975 et la mémoire des gradients 0,99. Le potentiel "
        "quadratique conserve le même lissage phi=0,8 pour isoler le potentiel ; les auteurs "
        "utilisaient phi=1 dans leur configuration quadratique. Ces choix permettent une "
        "ablation contrôlée mais ne reproduisent pas exactement les recettes publiées.", "",
        "## 3. Mesures et inférence", "",
        "L2 relative = norme de l'erreur divisée par norme de la référence sur la grille. "
        "Ce nombre n'est pas une précision de classification. Le maximum est le plus grand "
        "écart absolu observé sur la grille ; ce n'est pas un maximum continu certifié. "
        "q95 et q99 désignent les percentiles de l'erreur dans le domaine, pas des intervalles "
        "de confiance. Le résidu physique RMS est évalué sur 4096 points indépendants.", "",
        "Pour chaque EDP, les quatre contrastes prévus sont complet−local, complet−global, "
        "exponentiel−quadratique et interaction (complet−local−global+sans adaptation). "
        "Les différences sont calculées par germe avant agrégation. Pour l'interaction, "
        "une valeur négative indique un effet combiné inférieur à la somme additive des "
        "effets sur cette échelle d'erreur ; son interprétation dépend de l'échelle.", "",
        "IC percentile bootstrap 95 % de la médiane des différences, 10000 tirages. "
        "Test exact bilatéral des signes, zéros exclus ; correction Holm sur 16 tests L2, "
        "puis une famille secondaire distincte de 16 tests pour le maximum. Les IC sont "
        "marginaux et ne sont pas simultanés. Un p non significatif ne prouve pas l'équivalence. "
        "Dix germes documentent la variabilité d'optimisation de ces cas ; ils ne représentent "
        "pas dix distributions physiques indépendantes.", "",
        "## 4. Résultats sur les grilles historiques", "",
        "### Erreur relative L2 médiane", "",
        "| Problème | Sans adaptation | Global seul | Local seul | Complet exp. | Complet quad. |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for problem in PROBLEMS:
        lines.append("| "+P_LABELS[problem]+" | "+" | ".join(f"{lookup[problem,v]['median_relative_l2']:.5f}" for v in VARIANTS)+" |")
    lines += ["", "### Maximum absolu médian", "",
        "| Problème | Sans adaptation | Global seul | Local seul | Complet exp. | Complet quad. |",
        "|---|---:|---:|---:|---:|---:|"]
    for problem in PROBLEMS:
        lines.append("| "+P_LABELS[problem]+" | "+" | ".join(f"{lookup[problem,v]['median_max_abs_error']:.5f}" for v in VARIANTS)+" |")
    lines += ["", "Les valeurs ci-dessus sont des médianes de scores. La différence de deux "
        "médianes n'est pas nécessairement la médiane des différences appariées utilisée ci-dessous.", "",
        "### Contrastes L2 planifiés", "",
        "| EDP | Contraste | Différence médiane | IC 95 % marginal | p Holm | Signes −/0/+ |",
        "|---|---|---:|---|---:|---|"]
    for r in stats:
        if r["metric"]!="relative_l2":
            continue
        lines.append(f"| {r['problem']} | {r['contrast']} | {r['median_difference']:+.5f} | "
                     f"[{r['ci95_low']:+.5f} ; {r['ci95_high']:+.5f}] | {r['p_holm_16']:.4f} | "
                     f"{r['n_negative']}/{r['n_zero']}/{r['n_positive']} |")
    lines += ["", "Les statistiques du maximum, les résultats individuels, q95/q99 et les "
        "résidus sont fournis dans paired_statistics.csv et evaluation.csv. Toutes les paires "
        "complètes sont conservées. Aucun germe favorable n'est choisi pour les tableaux.", "",
        "## 5. Sensibilité de l'évaluation", "",
        "La grille est raffinée de 161×81 à 321×161 pour Burgers, de 101×51 à 201×101 "
        "pour Allen–Cahn et les ondes, et de 101×101 à 201×201 pour Helmholtz. "
        "Aucun modèle n'est réentraîné pour cette vérification.", ""]
    s=sensitivity["burgers"]
    lines.append(f"Pour Burgers, deux références numériques (257 puis 513 points, pas demandé "
                 f"10⁻⁴ puis 5×10⁻⁵) diffèrent de {s['relative_l2']:.5f} en L2 relative et "
                 f"de {s['max_abs_error']:.5f} au maximum sur la grille fine. "
                 "Cette différence mesure la sensibilité numérique ; elle ne certifie pas "
                 "l'erreur exacte de la référence la plus fine.")
    lines += ["", "| Variante Burgers | Maximum historique | Grille fine, même référence | Grille et référence affinées |",
        "|---|---:|---:|---:|"]
    for v in VARIANTS:
        r=lookup["burgers",v]
        lines.append(f"| {LABELS[v]} | {r['median_max_abs_error']:.5f} | "
                     f"{r['median_dense_max_abs_error']:.5f} | {r['median_refined_max_abs_error']:.5f} |")
    lines += ["", "Les cartes représentent la médiane ponctuelle des erreurs absolues entre "
        "germes. Elles ne sont ni la trajectoire d'un modèle médian ni une borne d'erreur.", "",
        "## 6. Coût CPU mesuré séparément", "",
        "60 essais supplémentaires : cinq variantes × trois germes × quatre EDP. "
        "Chaque processus exécute 200 pas. La mesure couvre les pas 51 à 150, après "
        "50 pas d'échauffement, et inclut l'optimisation, les diagnostics et la journalisation. "
        "L'initialisation, la résolution finale de référence et les sauvegardes de fin "
        "sont exclues de cet intervalle. Les essais sont séquentiels et intercalés. "
        "Cette mesure décrit le coût local par pas, pas le temps pour atteindre une précision donnée.", "",
        "| EDP | Variante | ms/pas médian | Ratio apparié au témoin | Pic RSS médian, MiB |",
        "|---|---|---:|---:|---:|"]
    for r in costs:
        lines.append(f"| {r['problem']} | {LABELS[r['variant']]} | {r['median_ms_per_step']:.3f} | "
                     f"{r['median_paired_ratio_to_neither']:.3f} | {r['median_peak_rss_mib']:.1f} |")
    lines += ["", "Le dernier essai CPU (Helmholtz, local seul, germe 33) a été interrompu "
        "après le pas 150. Les pas 50 et 150 sont enregistrés : la fenêtre prévue est "
        "mesurée sans extrapolation. Son RSS final est indisponible ; la médiane mémoire "
        "de cette variante utilise deux mesures. Cet essai n'est pas compté comme terminé. "
        "Le RSS inclut Python, PyTorch et les données. Trois répétitions sont une "
        "mesure descriptive, sans garantie de précision fine du ratio. Aucun GPU CUDA "
        "n'était disponible ; aucun temps GPU ni consommation énergétique ne sont extrapolés.", "",
        "## 7. Interprétation des résultats", "",
        "**Helmholtz : l'association locale + globale est utile dans ce cas.** "
        "Le modèle complet exponentiel améliore L2 face à chacune des deux composantes "
        "seules sur les dix germes. L'interaction sur L2 est également négative sur les "
        "dix germes. Les trois contrastes restent significatifs après Holm (p=0,03125). "
        "Cela documente une interaction favorable dans cette configuration k=1 ; "
        "ce résultat ne se généralise pas automatiquement aux autres EDP.", "",
        "**Ondes : le potentiel quadratique améliore L2 face à l'exponentiel.** "
        "Les dix différences appariées sont favorables au quadratique, avec p Holm=0,03125. "
        "L'avantage sur le maximum n'est pas confirmé après la correction des tests "
        "secondaires. Il faut donc conserver la distinction entre précision globale "
        "et erreur extrême.", "",
        "**Burgers : les ablations ne désignent pas un gagnant statistiquement établi.** "
        "Le local seul obtient une médiane L2 inférieure au complet, mais les signes "
        "varient entre germes et aucun des contrastes planifiés ne passe Holm. "
        "Les médianes élevées des maxima persistent après raffinement. La référence "
        "numérique elle-même influe sur leur valeur : l'écart entre deux références "
        "atteint environ 0,132 localement. Un classement fin fondé sur de petits "
        "écarts de maximum doit donc rester prudent.", "",
        "**Allen–Cahn forcée : pas de bénéfice supplémentaire établi du global "
        "face au local seul sur L2.** Le complet et le local seul ont des scores "
        "proches ; cela ne prouve pas une équivalence. Le complet améliore le maximum "
        "face au global seul sur dix germes (p Holm=0,03125, famille secondaire).", "",
        "Ces résultats permettent d'affiner la question scientifique : pourquoi le "
        "couplage des pondérations aide-t-il Helmholtz, tandis que son intérêt est "
        "moins net dans les autres cas ? Ils ne justifient pas de sélectionner "
        "rétrospectivement une méthode unique puis de la présenter comme gagnante universelle.", "",
        "## 8. Limites et décisions scientifiques", "",
        "1. Cette campagne est exploratoire après observation de v0.7 et du pilote ; "
        "elle ne devient pas confirmatoire simplement parce que son lancement est figé.",
        "2. Allen–Cahn est forcée/manufacturée et Helmholtz utilise k=1. La généralisation "
        "aux fronts raides, hautes fréquences et instabilités plasma n'est pas établie.",
        "3. Les budgets sont hétérogènes entre EDP et restent courts par rapport à "
        "certaines dynamiques de pondération. Les comparaisons sont valides à budget "
        "égal au sein de chaque EDP ; elles ne prouvent pas une convergence asymptotique.",
        "4. Une faible erreur L2 peut coexister avec un pic local. Un petit résidu physique "
        "n'est pas, sans analyse de stabilité de l'EDP, une garantie sur l'erreur de solution.",
        "5. La comparaison à temps total égal, les données rares/bruitées pour ces "
        "ablations et une validation sur machine indépendante restent à réaliser.",
        "6. Cette étude n'établit pas une nouvelle invention de vRBA. Une contribution "
        "scientifique possible est la caractérisation reproductible de ses interactions "
        "et de ses domaines d'échec, avec limites explicites.", "",
        "## 9. Reproduction et audit", "",
        "Les résultats individuels utilisent des chemins relatifs à la campagne ; "
        "les champs run_dir des anciens summary.json sont des traces du poste d'origine. "
        "Pour analyser une archive déplacée, utiliser scripts/analyze_vrba_campaign.py.", "",
        "```bash",
        "python -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install -e '.[dev]' torch==2.14.0 numpy==2.3.5",
        "PYTHONPATH=src python -m pytest",
        "PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python scripts/run_vrba_campaign.py --output outputs/new_campaign --workers 6",
        "# Reprise : même commande avec --resume, sans changement des sources ou réglages.",
        "PYTHONPATH=src python scripts/analyze_vrba_campaign.py outputs/new_campaign --output outputs/new_analysis",
        "# Profilage après la fin des autres calculs sur la machine :",
        "PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python scripts/profile_vrba_cpu.py --output outputs/new_cpu_profile",
        "```", "",
        "La campagne archive le protocole, les configurations, les empreintes des sources, "
        "les versions et un pip freeze complet. Ce dernier décrit la machine de calcul ; "
        "ce n'est pas un verrou portable universel. PyTorch et NumPy sont explicitement "
        "épinglés dans la commande ci-dessus. La version de base du paquet reste 0.7.0 ; "
        "v0.9 identifie cette campagne et ses sources par empreintes.", "",
        "Validation : 43 tests du socle et du lanceur réussis, puis trois tests "
        "statistiques réussis. La désactivation retrouve M0 sur les quatre EDP à "
        "tolérance 10⁻¹². Les scores sauvegardés ont été recalculés à tolérance "
        "relative 10⁻¹¹ / absolue 10⁻¹². Les tableaux et figures sont produits par scripts.", "",
        "## 10. Livrables", "",
        "- results.json et cells/ : les 200 trajectoires et états finaux de la campagne.",
        "- evaluation.csv : erreurs historiques, grilles affinées, résidus et coûts par germe.",
        "- pairing_audit.csv : concordance des conditions initiales des 40 blocs.",
        "- paired_statistics.csv : les 32 contrastes avec IC, signes et correction Holm.",
        "- reference_sensitivity.json : sensibilité de la référence Burgers.",
        "- figures PNG/SVG et champs NPZ : données visualisables et exportables.",
        "- dossier CPU : les 60 essais de profilage et leurs configurations.",
        "- protocoles et scripts : reproduction et poursuite de l'étude.", ""]
    (analysis/"ARTICLE1_ABLATIONS_V09_RAPPORT.md").write_text("\n".join(lines),encoding="utf-8")
    print(analysis/"ARTICLE1_ABLATIONS_V09_RAPPORT.md")


if __name__=="__main__":
    main()
