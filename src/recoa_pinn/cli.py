from __future__ import annotations

import argparse
import json

from .campaign import run_campaign
from .config import VALID_METHODS, load_config
from .trainer import analyze_existing, compare, train


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Expériences reproductibles ReCoA-PINN")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Entraîner une méthode")
    train_parser.add_argument("--config", required=True)
    train_parser.add_argument(
        "--method", required=True, choices=sorted(VALID_METHODS)
    )
    train_parser.add_argument("--seed", required=True, type=int)

    compare_parser = subparsers.add_parser("compare", help="Lancer une comparaison appariée")
    compare_parser.add_argument("--config", required=True)
    compare_parser.add_argument(
        "--methods", nargs="+", default=["m5", "m6"],
        choices=sorted(VALID_METHODS)
    )
    compare_parser.add_argument("--seeds", nargs="+", required=True, type=int)

    analyze_parser = subparsers.add_parser(
        "analyze", help="Agréger des exécutions déjà terminées"
    )
    analyze_parser.add_argument("--config", required=True)
    analyze_parser.add_argument(
        "--methods", nargs="+", default=["m5", "m6"],
        choices=sorted(VALID_METHODS)
    )
    analyze_parser.add_argument("--seeds", nargs="+", required=True, type=int)

    campaign_parser = subparsers.add_parser(
        "campaign", help="Exécuter/reprendre une campagne et générer tableaux et figures"
    )
    campaign_parser.add_argument("--manifest", required=True)
    campaign_parser.add_argument("--workers", type=int, default=1)
    campaign_parser.add_argument(
        "--report-only", action="store_true",
        help="Ne pas entraîner; produire le rapport avec les runs présents",
    )
    campaign_parser.add_argument(
        "--force", action="store_true",
        help="Réexécuter même les runs déjà terminés",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "campaign":
        result = run_campaign(
            args.manifest, workers=args.workers,
            report_only=args.report_only, force=args.force,
        )
    else:
        config = load_config(args.config)
    if args.command == "train":
        result = train(config, args.method, args.seed)
    elif args.command == "compare":
        result = compare(config, args.methods, args.seeds)
    elif args.command == "analyze":
        result = analyze_existing(config, args.methods, args.seeds)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
