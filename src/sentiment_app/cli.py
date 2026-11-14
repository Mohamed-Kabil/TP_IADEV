"""Commande sentiment : un avis, une réponse lisible ou JSON."""

import argparse
import json
import sys

from sentiment_app import __version__, predict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentiment", description="Classe un avis en français.")
    parser.add_argument("texte", nargs="+", help="l'avis à classer")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)
    try:
        resultat = predict(" ".join(args.texte))
    except ValueError as exc:
        print(f"erreur : {exc}", file=sys.stderr)
        return 2
    print(json.dumps(resultat, ensure_ascii=False) if args.json else
          f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0
