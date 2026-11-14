"""Client Streamlit : appels /v1, clé et erreurs stables."""

import httpx
from fastapi.testclient import TestClient

from api.main import app
from ui import client


def test_sante_et_configuration(v1_client, api_keys, monkeypatch):
    etat = client.sante(v1_client)
    assert etat.ok and "TP2" in etat.message
    monkeypatch.setenv("API_URL", "http://127.0.0.1:8123")
    monkeypatch.setenv("API_KEY", api_keys["client"])
    with client.creer_session() as session:
        assert str(session.base_url) == "http://127.0.0.1:8123"
        assert session.headers["X-API-Key"] == api_keys["client"]


def test_avis_positif(v1_client):
    r = client.predire(v1_client, "Livraison rapide, produit conforme, très satisfait")
    assert r.ok and r.label == "POSITIVE" and r.score == .777


def test_texte_inconnu(v1_client):
    r = client.predire(v1_client, "xqzvb wlkptr grombu")
    assert r.ok and r.label == "INDETERMINE" and r.score < .60


def test_refus_et_codes_stables(v1_client):
    assert client.predire(v1_client, "   ").message == client.REFUS
    for code, attendu in client.MESSAGES.items():
        transport = httpx.MockTransport(lambda request, c=code: httpx.Response(
            400, json={"erreur": {"code": c, "message": "message qui peut changer", "champs": []}}
        ))
        with httpx.Client(transport=transport, base_url="http://test") as session:
            assert client.predire(session, "Texte").message == attendu


def test_modele_non_charge(v1_client, monkeypatch):
    monkeypatch.setattr(app.state, "classifier", None)
    assert client.predire(v1_client, "Très bien").message == client.SANS_MODELE
    assert client.sante(v1_client).message == client.SANS_MODELE


def test_api_injoignable():
    def hors_ligne(request):
        raise httpx.ConnectError("Serveur absent", request=request)

    with httpx.Client(transport=httpx.MockTransport(hors_ligne), base_url="http://test") as session:
        assert client.predire(session, "Très bien").message == client.INJOIGNABLE
        assert client.sante(session).message == client.INJOIGNABLE


def test_lot_resume_et_reponses_invalides(v1_client):
    reponses = client.predire_lot(v1_client, [
        "Livraison rapide, produit conforme, très satisfait",
        "Produit cassé et service injoignable, à fuir", "   ",
    ])
    assert client.resumer(reponses) == {"NEGATIVE": 1, "POSITIVE": 1, "REFUS OU ERREUR": 1}
    for corps in [{}, {"label": "AUTRE", "score": .8}, {"label": "POSITIVE", "score": True},
                  {"label": "POSITIVE", "score": 2}, {"label": "POSITIVE", "score": "0.8"}]:
        transport = httpx.MockTransport(lambda request, body=corps: httpx.Response(200, json=body))
        with httpx.Client(transport=transport, base_url="http://test") as session:
            assert client.predire(session, "Avis").message == client.REPONSE_INVALIDE
            assert client.sante(session).message == client.REPONSE_INVALIDE
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(502, text="erreur")),
                      base_url="http://test") as session:
        assert client.predire(session, "Avis").message == "Erreur de l'API (502)."


def test_session_sans_cle_message_explicite(api_keys, monkeypatch):
    monkeypatch.setenv("API_KEY", "")
    with client.creer_session() as session:
        assert "X-API-Key" not in session.headers
    with TestClient(app) as session:
        r = client.predire(session, "Livraison rapide")
        assert not r.ok and r.message == client.CLE_REFUSEE
