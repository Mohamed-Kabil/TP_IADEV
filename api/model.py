"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de src/predict.py, qui charge models/sentiment.joblib une seule fois.
"""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from predict import MODELE, charger_modele, predict as _predict  # noqa: E402  (fonctions du TP2)

# Seuil décrit dans le manuel V1.1, p. 22 : les scores inférieurs à 0,60
# sont orientés vers une vérification humaine. Mesure : docs/controles/tp1-v11-seuil.txt.
SEUIL_ABSTENTION = 0.60


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        charger_modele()  # échoue immédiatement si le joblib manque : on ne démarre pas sans modèle

    def predict(self, text: str) -> dict:
        """Renvoie un verdict, ou INDETERMINE sous le seuil de confiance."""
        r = _predict(text)  # lève ValueError si le texte est vide
        label = "INDETERMINE" if r["score"] < SEUIL_ABSTENTION else r["label"].upper()
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans src/predict.py)."""
    return SentimentClassifier()
