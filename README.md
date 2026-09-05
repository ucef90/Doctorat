# Doctorat — ReCoA-PINN

État de cette étape : **V06**, historique reconstitué.

Projet doctoral : *Trustworthy Physics-Informed Artificial Intelligence for Prediction
and Control of Complex Dynamical Systems: Application to Tokamak Plasma Instabilities*.

| Étape | Contenu ajouté | Repère |
| --- | --- | --- |
| V06 | Socle documentaire, premières expériences disponibles et schémas | Commit V06 |
| V07 | Travaux M7/VW/vRBA, configurations et résultats consolidés | v0.7.0 (reconstruit) |
| V08 | Pilote vRBA : cinq variantes, trois germes, 15 entraînements | article1-v0.8 |
| V09 | Code courant, 200 entraînements, analyses, CPU et rapport final | article1-v0.9 |

Chaque étape conserve les fichiers précédents. Les anciens tags sont documentaires,
sans garantie de code installable. Les dates de commit sont celles de la reconstruction.
Lire la [notice](RECONSTRUCTION_NOTICE.md), la [liste exacte](docs/history/README.md)
et l'[inventaire des sources](INVENTORY.csv). Les artefacts scientifiques sont conservés
octet pour octet ; README et .gitignore originaux sont archivés séparément.

À partir de V09, lire [START_HERE_V09.md](START_HERE_V09.md) puis le
[rapport français PDF](output/pdf/ARTICLE1_ABLATIONS_V09_RAPPORT.pdf).
Les liens vers V09 ne sont pas disponibles dans les commits documentaires antérieurs.
Les résultats demeurent limités aux cas testés, sans validation tokamak.

## Navigation Git

```bash
git log --oneline --decorate --reverse
git show article1-v0.8:START_HERE_V08.md
git ls-tree -r --name-only article1-v0.9
```

Pour examiner une ancienne étape sans toucher à votre dossier de travail :
`git worktree add --detach ../Doctorat-V08 article1-v0.8`.

## Code et résultats

Le code actuel est dans `src/`, les configurations dans `configs/`, les tests dans
`tests/`, les scripts dans `scripts/`. Les documents historiques restent à leurs
chemins initiaux, afin de préserver autant que possible les liens existants.
Les figures pédagogiques sont dans `docs/figures/explanatory/`.
Tous les résultats archivés sont dans `outputs/`, y compris poids `.pt`, journaux,
tableaux, figures et manifestes. Les PDF/MD sont déjà versionnés ; aucune nouvelle
conversion des anciens rapports n'a été inventée.

En V09 : `python -m pip install -e '.[dev]'` puis `python -m pytest`.
Pour la provenance exacte des entraînements, utiliser les manifestes et fichiers
environment.json plutôt que les seules contraintes larges de pyproject.toml.
Aucun test PyTorch n'est relancé par la reconstruction.

Pour de nouveaux calculs, utiliser `outputs/new_experiments/` (ignoré par Git), puis
archiver volontairement les résultats validés. Ne pas réécrire les campagnes archivées.

## Sources et contrôle

Archive : `ReCoA_PINN_V09_Research_Package.zip` ; SHA-256 :
`89120068c9ca51b607c0be9b38df83b9730adf52227bf73ff3dc1b6189072885`.
Complément : commit local `656050cae337f96fdab3b47ec862ccae4f1c9601`. Les fichiers communs identiques ne sont
pas dupliqués. Le commit GitHub initial `59498a9fde0662dabc0c407300b4d6c89f40f64f` est conservé.
Le contrôle autonome `python scripts/reconstruct_history.py verify --repo .`
vérifie les fichiers inventoriés et les quatre commits sans PyTorch ni accès réseau.
