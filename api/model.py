"""Adaptateur HTTP du modèle ; aucune opération d'entraînement."""

import sys
from pathlib import Path
from typing import TypedDict

from api.schemas import Label

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from predict import charger_modele  # noqa: E402
from predict import predict as _predict  # noqa: E402

# Manuel V1.1, p. 22 ; mesure : docs/controles/tp1-v11-seuil.txt.
SEUIL_ABSTENTION = 0.60
CORRESPONDANCE: dict[str, Label] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


class Prediction(TypedDict):
    label: Label
    score: float
    text: str


class SentimentClassifier:
    # Nom historique stable pour les clients et les tests déjà fournis.
    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        modele = charger_modele()
        inconnues = {str(c) for c in modele.classes_} - set(CORRESPONDANCE)
        if inconnues:
            raise ValueError(f"classes inconnues du contrat : {sorted(inconnues)}")

    def predict(self, text: str) -> Prediction:
        resultat = _predict(text)
        label: Label = (
            "INDETERMINE" if resultat["score"] < SEUIL_ABSTENTION
            else CORRESPONDANCE[resultat["label"]]
        )
        return {"label": label, "score": resultat["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    return SentimentClassifier()
