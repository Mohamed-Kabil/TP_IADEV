"""Lecture CSV et données des graphiques, indépendantes du rendu Streamlit."""

from io import BytesIO

import pandas as pd

TRANCHES = ["< 0,60", "0,60 à < 0,70", "0,70 à < 0,80", "0,80 à < 0,90", "0,90 à 1,00"]


def charger_csv(contenu: bytes) -> pd.DataFrame:
    try:
        avis = pd.read_csv(
            BytesIO(contenu), encoding="utf-8-sig", keep_default_na=False, skip_blank_lines=False
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise ValueError("CSV illisible : utilisez un fichier UTF-8 séparé par des virgules.") from exc
    if "text" not in avis.columns:
        raise ValueError("Colonne text absente du fichier.")
    if avis.empty:
        raise ValueError("Le fichier ne contient aucun avis.")
    avis["text"] = avis["text"].astype(str)
    return avis


def tranches_confiance(scores: pd.Series) -> pd.Series:
    valeurs = pd.to_numeric(scores, errors="coerce").dropna()
    # Intervalles fermés à gauche : 0,60 n'est pas une abstention ; 1,00 est inclus.
    tranches = pd.cut(
        valeurs, bins=[0, .6, .7, .8, .9, float("inf")],
        labels=TRANCHES, right=False, include_lowest=True,
    )
    return tranches.value_counts(sort=False).rename("Nombre")


def exporter_csv(avis: pd.DataFrame) -> bytes:
    return avis.to_csv(index=False).encode("utf-8-sig")
