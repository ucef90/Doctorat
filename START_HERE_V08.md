# Extension v0.8 — ablations vRBA

## Livré et vérifié le 5 septembre 2026

Socle v0.7 conservé ; deux interrupteurs booléens d'ablation ajoutés sans
changer les défauts. 38 tests réussis (dont six nouveaux cas), 15 expériences
Burgers réussies : cinq variantes, trois germes, 120 pas. La première collecte
des tests a échoué car l'installation de PyTorch n'était pas encore terminée ;
la suite complète relancée après installation est passée en 7,58 secondes.

Le pilote utilise PyTorch 2.14.0 et NumPy 2.3.5 ; chaque entraînement possède
son environment.json. Les fichiers source sont identifiés par SHA-256.
Le nom de version du paquet de base reste 0.7.0 : cette livraison est une
extension expérimentale, pas une version stable finale.

## Résultat pilote

L2 médiane : full_exp 0,542375 ; local_only 0,540148 ; global_only 0,619423 ;
full_quad 0,548454 ; neither 0,618803. Les résultats suggèrent une contribution
précoce de l'attention locale sur ce pilote uniquement. Ils ne démontrent pas
l'inutilité de l'équilibrage global, dont la dynamique peut être lente.
Aucune variante n'est retirée de la suite prévue. Les tableaux détaillés,
quantiles et résultats par germe sont dans outputs/ablation_v08_pilot.

## Reproduire depuis le dossier du projet

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]' torch==2.14.0 numpy==2.3.5
PYTHONPATH=src python -m pytest
PYTHONPATH=src python scripts/run_vrba_ablations.py --output outputs/new_pilot
PYTHONPATH=src python scripts/summarize_vrba_ablations.py outputs/new_pilot
```

Le lanceur refuse un dossier existant : utiliser un nouveau nom. Les autres
dépendances restent sous les contraintes du pyproject ; consulter les fichiers
environment.json pour la provenance exacte. Ce n'est pas encore une image
conteneur verrouillée de manière bit-à-bit.

## Suite longue, non exécutée dans cette livraison

```bash
PYTHONPATH=src python scripts/run_vrba_ablations.py --config configs/burgers_confirmatory_long.yaml --output outputs/ablation_long_burgers --seeds 11 22 33 44 55 66 77 88 99 111
```

Répéter avec allen_cahn_screen.yaml, helmholtz_calibrated.yaml et
wave_screen.yaml, en utilisant des dossiers distincts. Cela représente
200 entraînements. Le résumé fourni reste descriptif : l'analyse appariée,
les intervalles bootstrap et les contrôles de multiplicité restent à produire
pour cette campagne, ainsi que le profilage matériel et les essais bruités.

## Position scientifique

Lire VRBA_ABLATION_PROTOCOL.md avant de modifier les paramètres. Les références
et attributions historiques sont dans les documents du socle v0.7. Cette
extension ne constitue pas une nouvelle revue bibliographique. vRBA appartient
à ses auteurs ; notre contribution possible est l'étude contrôlée de ses
mécanismes et de ses limites, à étayer par les prochains résultats.

La thèse conserve son titre de travail : « Intelligence artificielle informée
par la physique pour la prédiction et le contrôle fiables des systèmes
dynamiques complexes : application aux instabilités du plasma dans les
tokamaks ». La fiabilité et le contrôle sont des objectifs de recherche,
pas des propriétés déjà démontrées par le pilote Burgers.
