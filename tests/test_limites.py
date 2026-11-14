"""Bornes du contrat, blancs Unicode et seuil strict d'abstention."""

from types import SimpleNamespace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from api import model
from api.schemas import PredictRequest


@pytest.mark.parametrize("texte", ["", " ", "\t\n", "\x85", "\u00a0"])
def test_blancs_refuses(v1_client, texte):
    response = v1_client.post("/v1/predict", json={"text": texte})
    assert response.status_code == 422
    assert response.json()["erreur"]["champs"][0]["champ"] == "body.text"


@given(st.text(alphabet=" \t\n\r\x85\u00a0", min_size=1, max_size=40))
@settings(max_examples=30, deadline=None)
def test_toute_chaine_blanche_est_refusee(texte):
    with pytest.raises(ValueError):
        PredictRequest(text=texte)


def test_longueurs_autorisees(v1_client):
    for taille in [1, 2000]:
        response = v1_client.post("/v1/predict", json={"text": "a" * taille})
        assert response.status_code == 200
        assert len(response.json()["text"]) <= 100


def test_texte_trop_long(v1_client):
    assert v1_client.post("/v1/predict", json={"text": "a" * 2001}).status_code == 422


def test_aperçu_et_texte_preserves(v1_client):
    texte = "  Livraison rapide, très satisfait. " * 5
    response = v1_client.post("/v1/predict", json={"text": texte})
    assert response.status_code == 200
    assert response.json()["text"] == texte[:100]


def test_seuil_strict_et_classes_valides(monkeypatch):
    monkeypatch.setattr(model, "charger_modele", lambda: SimpleNamespace(classes_=["neutre"]))
    with pytest.raises(ValueError, match="classes inconnues"):
        model.SentimentClassifier()
    monkeypatch.setattr(model, "charger_modele", lambda: SimpleNamespace(classes_=["positive", "negative"]))
    clf = model.SentimentClassifier()
    for score, attendu in [(0.5999, "INDETERMINE"), (0.60, "POSITIVE")]:
        monkeypatch.setattr(model, "_predict", lambda texte, s=score: {"label": "positive", "score": s})
        assert clf.predict("Texte")["label"] == attendu
