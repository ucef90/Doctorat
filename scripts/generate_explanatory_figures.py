from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch


BLUE = "#277DA1"
TEAL = "#43AA8B"
GREEN = "#4D908E"
ORANGE = "#F8961E"
RED = "#E85D75"
PURPLE = "#7B61A8"
GOLD = "#F9C74F"
INK = "#183153"
MUTED = "#5D6B7A"
LIGHT = "#F4F7FA"
PALE_BLUE = "#E8F3F8"
PALE_RED = "#FCECEF"
PALE_GREEN = "#EAF6F2"
PALE_PURPLE = "#F0ECF7"
WHITE = "#FFFFFF"


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.titlesize": 20,
        "axes.titleweight": "bold",
        "axes.labelsize": 13,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })


def canvas(title: str, subtitle: str | None = None, figsize=(14, 8)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.suptitle(title, x=0.06, y=0.965, ha="left", color=INK)
    if subtitle:
        fig.text(0.06, 0.905, subtitle, ha="left", va="top", color=MUTED, fontsize=12)
    return fig, ax


def rounded_box(
    ax, x: float, y: float, width: float, height: float, text: str,
    facecolor: str = LIGHT, edgecolor: str = BLUE, fontsize: float = 12,
    color: str = INK, linewidth: float = 1.8, radius: float = 0.02,
    weight: str = "normal", wrap: int | None = None,
):
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        linewidth=linewidth, edgecolor=edgecolor, facecolor=facecolor,
    )
    ax.add_patch(patch)
    label = textwrap.fill(text, wrap) if wrap else text
    ax.text(
        x + width / 2, y + height / 2, label,
        ha="center", va="center", fontsize=fontsize, color=color, weight=weight,
    )
    return patch


def arrow(
    ax, start, end, color: str = MUTED, linewidth: float = 2.0,
    connectionstyle: str = "arc3", mutation_scale: float = 15,
):
    patch = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=mutation_scale,
        linewidth=linewidth, color=color, connectionstyle=connectionstyle,
        shrinkA=3, shrinkB=3,
    )
    ax.add_patch(patch)
    return patch


def save_figure(fig, output_dir: Path, stem: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("png", "pdf", "svg"):
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=WHITE)
        paths.append(path)
    plt.close(fig)
    return paths


def figure_thesis_roadmap(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Trajectoire scientifique de la thèse",
        "Des fondations méthodologiques des PINNs jusqu’au contrôle des instabilités du plasma",
    )
    stages = [
        ("Article 1", "PINNs robustes\nPondération\n+ échantillonnage", BLUE, PALE_BLUE),
        ("Article 2", "Fiabilité\nDonnées rares\nBruit et incertitude", TEAL, PALE_GREEN),
        ("Article 3", "Prédiction\nInstabilités\ndu plasma", PURPLE, PALE_PURPLE),
        ("Application", "Contrôle\nen temps réel\nd’un tokamak", ORANGE, "#FFF3E5"),
    ]
    xs = [0.05, 0.29, 0.53, 0.77]
    for index, ((header, body, color, pale), x) in enumerate(zip(stages, xs)):
        rounded_box(ax, x, 0.43, 0.18, 0.23, body, pale, color, fontsize=11.5, weight="bold")
        ax.text(x + 0.09, 0.70, header, ha="center", color=color, weight="bold", fontsize=14)
        ax.text(x + 0.09, 0.37, str(index + 1), ha="center", va="center", color=WHITE,
                bbox={"boxstyle": "circle,pad=0.35", "facecolor": color, "edgecolor": color})
        if index < len(stages) - 1:
            arrow(ax, (x + 0.19, 0.545), (xs[index + 1] - 0.01, 0.545), color=MUTED)
    ax.annotate(
        "Position actuelle", xy=(0.14, 0.42), xytext=(0.14, 0.23),
        ha="center", color=RED, weight="bold",
        arrowprops={"arrowstyle": "-|>", "color": RED, "lw": 2},
    )
    ax.text(
        0.50, 0.10,
        "Fil conducteur : une IA informée par la physique, fiable, explicable et utilisable pour la décision",
        ha="center", color=INK, fontsize=14, weight="bold",
    )
    return save_figure(fig, output_dir, "01_thesis_roadmap")


def figure_pinn_principle(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Comment fonctionne un Physics-Informed Neural Network ?",
        "Le réseau apprend à partir des observations, mais aussi directement à partir des lois physiques.",
    )
    rounded_box(ax, 0.05, 0.60, 0.19, 0.15, "Coordonnées\n$(t, x)$", PALE_BLUE, BLUE, fontsize=16, weight="bold")
    rounded_box(ax, 0.35, 0.57, 0.24, 0.21, "Réseau neuronal\n$u_\\theta(t,x)$", PALE_PURPLE, PURPLE, fontsize=17, weight="bold")
    rounded_box(ax, 0.73, 0.60, 0.22, 0.15, "Prédiction physique\n$\\hat{u}(t,x)$", PALE_GREEN, TEAL, fontsize=16, weight="bold")
    arrow(ax, (0.25, 0.675), (0.34, 0.675), color=BLUE)
    arrow(ax, (0.60, 0.675), (0.72, 0.675), color=PURPLE)

    rounded_box(ax, 0.04, 0.24, 0.20, 0.16, "Mesures\nrares ou bruitées", "#FFF3E5", ORANGE, fontsize=14, weight="bold")
    rounded_box(ax, 0.28, 0.24, 0.20, 0.16, "Équation physique\n$u_t + \\mathcal{N}(u)=0$", PALE_BLUE, BLUE, fontsize=14, weight="bold")
    rounded_box(ax, 0.52, 0.24, 0.20, 0.16, "Conditions initiales\net aux limites", PALE_GREEN, TEAL, fontsize=14, weight="bold")
    rounded_box(ax, 0.76, 0.21, 0.20, 0.22,
                "$\\mathcal{L}=\\lambda_d\\mathcal{L}_d$\n$+\\lambda_f\\mathcal{L}_f$\n$+\\lambda_i\\mathcal{L}_i+\\lambda_b\\mathcal{L}_b$",
                PALE_RED, RED, fontsize=14, weight="bold")
    for x in (0.26, 0.50, 0.74):
        ax.text(x, 0.32, "+", ha="center", va="center", color=MUTED, fontsize=22, weight="bold")
    arrow(ax, (0.75, 0.32), (0.755, 0.32), color=MUTED, linewidth=1.6)
    arrow(ax, (0.85, 0.44), (0.59, 0.57), color=RED, linewidth=2.3)
    ax.text(0.70, 0.50, "rétropropagation", ha="center", color=RED, fontsize=11, rotation=20)
    ax.text(
        0.50, 0.08,
        "Différence avec un réseau classique : la physique devient une contrainte d’apprentissage.",
        ha="center", fontsize=14, color=INK, weight="bold",
    )
    return save_figure(fig, output_dir, "02_pinn_principle")


def figure_m5_problem(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Problématique scientifique : la boucle co-adaptative de M5",
        "Hypothèse étudiée : utiliser le même lot adaptatif pour échantillonner et régler les poids peut introduire un biais.",
    )
    nodes = [
        (0.38, 0.69, "1. Résidu physique\nélevé dans une zone", PALE_RED, RED),
        (0.68, 0.55, "2. Plus de points\ndans cette zone", "#FFF3E5", ORANGE),
        (0.60, 0.22, "3. Le contrôleur lit\nce même lot", PALE_PURPLE, PURPLE),
        (0.22, 0.22, "4. Les poids des\npertes changent", PALE_BLUE, BLUE),
        (0.08, 0.55, "5. Le modèle et le\nrésidu changent", PALE_GREEN, TEAL),
    ]
    for x, y, label, pale, color in nodes:
        rounded_box(ax, x, y, 0.24, 0.14, label, pale, color, fontsize=13, weight="bold")
    arrow(ax, (0.62, 0.74), (0.70, 0.66), color=RED, connectionstyle="arc3,rad=-0.18")
    arrow(ax, (0.79, 0.54), (0.75, 0.37), color=ORANGE, connectionstyle="arc3,rad=-0.18")
    arrow(ax, (0.59, 0.27), (0.47, 0.27), color=PURPLE)
    arrow(ax, (0.22, 0.29), (0.17, 0.54), color=BLUE, connectionstyle="arc3,rad=-0.18")
    arrow(ax, (0.29, 0.64), (0.39, 0.70), color=TEAL, connectionstyle="arc3,rad=-0.18")
    circle = Circle((0.50, 0.49), 0.115, facecolor=PALE_RED, edgecolor=RED, linewidth=2.5)
    ax.add_patch(circle)
    ax.text(0.50, 0.49, "RISQUE\nBiais de sélection\nOscillations\nSur-importance locale",
            ha="center", va="center", fontsize=12, weight="bold", color=RED)
    ax.text(
        0.50, 0.075,
        "Point essentiel : nos expériences confirment le couplage, mais pas encore un effet nuisible systématique.",
        ha="center", color=INK, fontsize=13, weight="bold",
    )
    return save_figure(fig, output_dir, "03_m5_feedback_problem")


def figure_m6_solution(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Solution M6 : découpler l’entraînement et le pilotage",
        "Le réseau conserve les points adaptatifs, tandis que le contrôleur observe un ensemble fixe et indépendant.",
    )
    ax.text(0.05, 0.75, "BRANCHE D’ENTRAÎNEMENT", color=ORANGE, weight="bold", fontsize=13)
    rounded_box(ax, 0.05, 0.53, 0.20, 0.15, "Points adaptatifs\nzones difficiles", "#FFF3E5", ORANGE, 13, weight="bold")
    rounded_box(ax, 0.35, 0.53, 0.20, 0.15, "Pertes physiques\net données", PALE_RED, RED, 13, weight="bold")
    rounded_box(ax, 0.70, 0.47, 0.24, 0.26, "Mise à jour du PINN\n$u_\\theta(t,x)$", PALE_PURPLE, PURPLE, 16, weight="bold")
    arrow(ax, (0.26, 0.605), (0.34, 0.605), color=ORANGE)
    arrow(ax, (0.56, 0.605), (0.69, 0.605), color=RED)

    ax.text(0.05, 0.37, "BRANCHE DE CONTRÔLE INDÉPENDANTE", color=BLUE, weight="bold", fontsize=13)
    rounded_box(ax, 0.05, 0.13, 0.20, 0.16, "Ensemble fixe\nde référence", PALE_BLUE, BLUE, 13, weight="bold")
    rounded_box(ax, 0.35, 0.13, 0.20, 0.16, "Mesure des pertes\net gradients", PALE_GREEN, TEAL, 13, weight="bold")
    rounded_box(ax, 0.64, 0.13, 0.20, 0.16, "Poids adaptatifs\n$\\lambda_f,\\lambda_i,\\lambda_b,\\lambda_d$", PALE_BLUE, BLUE, 13, weight="bold")
    arrow(ax, (0.26, 0.21), (0.34, 0.21), color=BLUE)
    arrow(ax, (0.56, 0.21), (0.63, 0.21), color=TEAL)
    arrow(ax, (0.74, 0.30), (0.48, 0.52), color=BLUE, connectionstyle="arc3,rad=-0.18")
    ax.text(0.61, 0.41, "poids transmis", color=BLUE, fontsize=11, rotation=25)
    ax.text(0.91, 0.25, "Découplage", color=BLUE, weight="bold", fontsize=13, ha="center")
    ax.plot([0.91, 0.91], [0.30, 0.46], color=BLUE, linewidth=2, linestyle="--")
    return save_figure(fig, output_dir, "04_m6_decoupled_solution")


def figure_experimental_protocol(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Protocole de recherche contrôlé",
        "Même architecture, mêmes germes et mêmes budgets : seule la stratégie étudiée doit changer.",
    )
    columns = ["M0", "M1", "M3", "M5", "M6"]
    rows = [
        ("Poids adaptatifs", ["—", "✓", "—", "✓", "✓"]),
        ("Échantillonnage adaptatif", ["—", "—", "✓", "✓", "✓"]),
        ("Référence fixe", ["—", "—", "—", "—", "✓"]),
    ]
    table = ax.table(
        cellText=[values for _, values in rows],
        rowLabels=[label for label, _ in rows], colLabels=columns,
        bbox=[0.12, 0.52, 0.76, 0.30], cellLoc="center", rowLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#C7D2DE")
        if row == 0:
            cell.set_facecolor(PALE_BLUE)
            cell.set_text_props(weight="bold", color=BLUE)
        elif col == -1:
            cell.set_facecolor(LIGHT)
            cell.set_text_props(weight="bold", color=INK)
        else:
            cell.set_facecolor(WHITE)

    blocks = [
        (0.04, "4 EDP", "Burgers\nAllen–Cahn\nHelmholtz\nOndes", BLUE, PALE_BLUE),
        (0.245, "10 germes", "Comparaisons\nappariées", TEAL, PALE_GREEN),
        (0.45, "Données", "Rares, bruitées\nincomplètes", ORANGE, "#FFF3E5"),
        (0.655, "Ablations", "Audit, lissage\nfréquences", PURPLE, PALE_PURPLE),
        (0.84, "Métriques", "$L_2$, stabilité\ncoût, résidus", RED, PALE_RED),
    ]
    widths = [0.14, 0.14, 0.14, 0.14, 0.115]
    for index, ((x, header, body, color, pale), width) in enumerate(zip(blocks, widths)):
        rounded_box(ax, x, 0.13, width, 0.20, body, pale, color, 12, weight="bold")
        ax.text(x + width / 2, 0.37, header, ha="center", color=color, weight="bold", fontsize=12)
        if index < len(blocks) - 1:
            next_x = blocks[index + 1][0]
            arrow(ax, (x + width + 0.005, 0.23), (next_x - 0.008, 0.23), color=MUTED, linewidth=1.5)
    ax.text(0.50, 0.06, "Sortie automatique : CSV + IC 95 % + LaTeX + figures PNG/PDF",
            ha="center", color=INK, weight="bold", fontsize=13)
    return save_figure(fig, output_dir, "05_controlled_experimental_protocol")


def read_m6_m5_results(path: Path) -> list[dict[str, float | str]]:
    labels = {
        "burgers_long": "Burgers — long",
        "allen_cahn": "Allen–Cahn",
        "helmholtz": "Helmholtz",
        "wave": "Ondes",
        "sparse_clean": "Données rares propres",
        "sparse_noisy": "Données rares bruitées",
        "extreme_noise": "Un capteur + bruit fort",
        "block_missing": "Bloc de capteurs manquant",
    }
    results = []
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["contrast"] != "m6_minus_m5" or row["metric"] != "relative_l2":
                continue
            results.append({
                "label": labels.get(row["experiment"], row["experiment"]),
                "estimate": float(row["median_difference"]),
                "low": float(row["ci_low"]),
                "high": float(row["ci_high"]),
            })
    if not results:
        raise ValueError(f"Aucun contraste M6-M5 trouvé dans {path}")
    return results


def figure_results(output_dir: Path, paired_results: Path) -> list[Path]:
    data = read_m6_m5_results(paired_results)
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    y = np.arange(len(data))
    estimates = np.asarray([row["estimate"] for row in data], dtype=float)
    lows = np.asarray([row["low"] for row in data], dtype=float)
    highs = np.asarray([row["high"] for row in data], dtype=float)
    colors = [
        TEAL if high < 0 else RED if low > 0 else BLUE
        for low, high in zip(lows, highs)
    ]
    for index, (estimate, low, high, color) in enumerate(zip(estimates, lows, highs, colors)):
        ax.errorbar(
            estimate, index, xerr=[[estimate - low], [high - estimate]],
            fmt="o", markersize=8, color=color, ecolor=color,
            linewidth=2.2, capsize=4,
        )
    ax.axvline(0.0, color=INK, linestyle="--", linewidth=1.5)
    ax.set_yticks(y, [row["label"] for row in data])
    ax.invert_yaxis()
    ax.set_xlabel("Différence médiane d’erreur L2 : M6 − M5")
    ax.set_title("Résultat principal : pas de supériorité générale démontrée", loc="left", pad=24)
    ax.text(
        0.0, 1.02,
        "Une valeur négative favorise M6. Les barres représentent les intervalles de confiance bootstrap à 95 %.",
        transform=ax.transAxes, color=MUTED, fontsize=12, va="bottom",
    )
    ax.grid(axis="x", alpha=0.22)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(
        0.985, 0.035,
        "Tous les IC traversent zéro → résultat statistiquement non concluant.",
        transform=ax.transAxes, ha="right", va="bottom",
        color=RED, weight="bold", fontsize=11.5,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": PALE_RED,
              "edgecolor": RED, "linewidth": 1.2},
    )
    return save_figure(fig, output_dir, "06_current_results_forest")


def figure_m7_next(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Étape suivante : M7 corrige le biais de mesure",
        "L’échantillonnage adaptatif est conservé, mais chaque point reçoit un poids compensant sa probabilité de sélection.",
    )
    ax.plot([0.50, 0.50], [0.16, 0.80], color="#D9E1E8", linewidth=2)
    ax.text(0.25, 0.78, "M5 — perte non corrigée", ha="center", color=RED, weight="bold", fontsize=15)
    ax.text(0.75, 0.78, "M7 — perte corrigée", ha="center", color=TEAL, weight="bold", fontsize=15)

    rng = np.random.default_rng(7)
    left_uniform = rng.uniform([0.07, 0.25], [0.43, 0.65], size=(22, 2))
    left_cluster = rng.normal([0.33, 0.48], [0.035, 0.055], size=(30, 2))
    left_cluster = np.clip(left_cluster, [0.07, 0.25], [0.43, 0.65])
    ax.scatter(left_uniform[:, 0], left_uniform[:, 1], s=25, color=BLUE, alpha=0.50)
    ax.scatter(left_cluster[:, 0], left_cluster[:, 1], s=31, color=RED, alpha=0.75)
    ax.add_patch(Ellipse((0.33, 0.48), 0.18, 0.26, fill=False, edgecolor=RED, linewidth=2))
    ax.text(0.25, 0.19, "Beaucoup de points ⇒ zone dominante", ha="center", color=RED, fontsize=12, weight="bold")

    right_uniform = rng.uniform([0.57, 0.25], [0.93, 0.65], size=(22, 2))
    right_cluster = rng.normal([0.83, 0.48], [0.035, 0.055], size=(30, 2))
    right_cluster = np.clip(right_cluster, [0.57, 0.25], [0.93, 0.65])
    ax.scatter(right_uniform[:, 0], right_uniform[:, 1], s=38, color=BLUE, alpha=0.65)
    cluster_sizes = np.linspace(9, 22, len(right_cluster))
    ax.scatter(right_cluster[:, 0], right_cluster[:, 1], s=cluster_sizes, color=TEAL, alpha=0.55)
    ax.add_patch(Ellipse((0.83, 0.48), 0.18, 0.26, fill=False, edgecolor=TEAL, linewidth=2))
    ax.text(0.75, 0.19, "Points fréquents ⇒ poids individuels réduits", ha="center", color=TEAL, fontsize=12, weight="bold")

    ax.text(
        0.50, 0.08,
        r"$\mathcal{L}_{f}^{M7}=\frac{1}{N}\sum_i\frac{p_{cible}(x_i)}{p_{adaptatif}(x_i)}\,r_\theta(x_i)^2$",
        ha="center", fontsize=18, color=INK,
    )
    return save_figure(fig, output_dir, "07_m7_measure_correction")


def figure_tokamak_application(output_dir: Path) -> list[Path]:
    fig, ax = canvas(
        "Application finale : anticiper et contrôler une instabilité du plasma",
        "Vision de la thèse : relier les capteurs du tokamak, les lois de la physique et une décision de contrôle fiable.",
    )
    center = (0.13, 0.53)
    for width, height, color, linewidth in (
        (0.20, 0.40, BLUE, 5.0), (0.155, 0.30, ORANGE, 3.0), (0.105, 0.20, PURPLE, 2.0),
    ):
        ax.add_patch(Ellipse(center, width, height, fill=False, edgecolor=color, linewidth=linewidth, alpha=0.9))
    ax.add_patch(Ellipse(center, 0.07, 0.13, facecolor=PALE_RED, edgecolor=RED, linewidth=2.5))
    ax.text(center[0], center[1], "PLASMA", ha="center", va="center", color=RED, weight="bold", fontsize=11)
    ax.text(0.13, 0.28, "Tokamak + capteurs", ha="center", color=INK, weight="bold", fontsize=13)

    stages = [
        (0.27, 0.17, "Signaux temporels", "Température\nDensité\nChamp magnétique", BLUE, PALE_BLUE),
        (0.50, 0.18, "Physics-Informed AI", "Prédiction\n+ incertitude\n+ explication", PURPLE, PALE_PURPLE),
        (0.74, 0.18, "Décision", "Probabilité\nd’instabilité\n+ alerte précoce", RED, PALE_RED),
    ]
    for x, width, header, body, color, pale in stages:
        ax.text(x + width / 2, 0.73, header, ha="center", color=color, weight="bold", fontsize=12)
        rounded_box(ax, x, 0.40, width, 0.27, body, pale, color, 11.5, weight="bold")
    arrow(ax, (0.23, 0.53), (0.26, 0.53), color=BLUE)
    arrow(ax, (0.45, 0.53), (0.49, 0.53), color=PURPLE)
    arrow(ax, (0.68, 0.53), (0.73, 0.53), color=RED)
    rounded_box(ax, 0.75, 0.16, 0.17, 0.12, "Actionneurs\ncontrôle du plasma", "#FFF3E5", ORANGE, 11.5, weight="bold")
    arrow(ax, (0.83, 0.39), (0.84, 0.29), color=ORANGE)
    arrow(ax, (0.75, 0.18), (0.23, 0.30), color=ORANGE, connectionstyle="arc3,rad=-0.20", linewidth=2.3)
    ax.text(0.49, 0.13, "boucle de contrôle en temps réel", ha="center", color=ORANGE, weight="bold", fontsize=11.5)
    ax.text(0.50, 0.045, "Objectif : prévoir suffisamment tôt pour agir avant la perte de stabilité.",
            ha="center", color=INK, weight="bold", fontsize=14)
    return save_figure(fig, output_dir, "08_tokamak_instability_pipeline")


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère les schémas explicatifs du projet ReCoA-PINN.")
    parser.add_argument(
        "--output-dir", default="docs/figures/explanatory",
        help="Dossier de sortie PNG/PDF/SVG.",
    )
    parser.add_argument(
        "--paired-results",
        default="outputs/reports/article1_current_evidence/tables/paired_summary.csv",
        help="Table des contrastes appariés utilisée pour la figure des résultats.",
    )
    args = parser.parse_args()
    configure_style()
    output_dir = Path(args.output_dir)
    paired_results = Path(args.paired_results)
    paths = []
    paths.extend(figure_thesis_roadmap(output_dir))
    paths.extend(figure_pinn_principle(output_dir))
    paths.extend(figure_m5_problem(output_dir))
    paths.extend(figure_m6_solution(output_dir))
    paths.extend(figure_experimental_protocol(output_dir))
    paths.extend(figure_results(output_dir, paired_results))
    paths.extend(figure_m7_next(output_dir))
    paths.extend(figure_tokamak_application(output_dir))
    print(f"{len(paths)} fichiers générés dans {output_dir.resolve()}")


if __name__ == "__main__":
    main()
