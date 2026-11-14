"""Contrôles du contrat /v1, de l'authentification et des rôles (manuel V1.1)."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.securite import charger_cles, identifier

AVIS = {"text": "Livraison rapide, produit conforme, très satisfait"}


def test_sante_publique(v1_client):
    response = v1_client.get("/v1/health", headers={"X-API-Key": ""})
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


@pytest.mark.parametrize("role", ["client", "admin"])
def test_prediction_autorisee(v1_client, api_keys, role):
    response = v1_client.post("/v1/predict", json=AVIS, headers={"X-API-Key": api_keys[role]})
    assert response.status_code == 200
    assert response.json()["label"] == "POSITIVE"


@pytest.mark.parametrize("cle", ["", "cle-inconnue-0123456789"])
def test_authentification_refusee(v1_client, cle):
    response = v1_client.post("/v1/predict", json=AVIS, headers={"X-API-Key": cle})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "ApiKey"
    assert response.json()["erreur"]["code"] == "NON_AUTHENTIFIE"
    assert cle not in response.text if cle else True


@pytest.mark.parametrize("body", [{"text": ""}, {"text": "   "}, {}, {"text": 42}])
def test_entree_invalide(v1_client, body):
    response = v1_client.post("/v1/predict", json=body)
    assert response.status_code == 422
    error = response.json()["erreur"]
    assert error["code"] == "ENTREE_INVALIDE"
    assert error["champs"][0]["champ"] == "body.text"


def test_admin_lit_modele(v1_client, api_keys):
    response = v1_client.get("/v1/modele", headers={"X-API-Key": api_keys["admin"]})
    assert response.status_code == 200
    data = response.json()
    assert data["seuil_abstention"] == .60
    assert data["metriques"]["f1_macro"] >= .85


def test_client_refuse_sur_modele(v1_client):
    response = v1_client.get("/v1/modele")
    assert response.status_code == 403
    assert response.json()["erreur"]["code"] == "ACCES_REFUSE"


def test_ancienne_route_compatible_et_depreciee(v1_client):
    response = v1_client.post("/predict", json=AVIS, headers={"X-API-Key": ""})
    assert response.status_code == 200
    assert response.json()["label"] == "POSITIVE"
    assert response.headers["Deprecation"] == "true"
    assert response.headers["Link"] == '</v1/predict>; rel="successor-version"'


def test_route_inconnue(v1_client):
    response = v1_client.get("/v1/inconnue")
    assert response.status_code == 404
    assert response.json()["erreur"]["code"] == "INTROUVABLE"
    assert "detail" in v1_client.get("/v10/inconnue").json()


def test_methode_incorrecte(v1_client):
    response = v1_client.get("/v1/predict")
    assert response.status_code == 405
    assert response.json()["erreur"]["code"] == "METHODE_NON_AUTORISEE"


def test_openapi_decrit_securite_erreurs_et_migration(v1_client):
    schema = v1_client.get("/openapi.json").json()
    assert schema["components"]["securitySchemes"]["APIKeyHeader"]["name"] == "X-API-Key"
    assert schema["paths"]["/predict"]["post"]["deprecated"] is True
    responses = schema["paths"]["/v1/predict"]["post"]["responses"]
    assert {"401", "403", "422", "500", "503"} <= set(responses)


def test_aucune_cle_ferme_acces(v1_client, monkeypatch):
    monkeypatch.setenv("API_KEYS", "")
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.post("/v1/predict", json=AVIS).status_code == 401


@pytest.mark.parametrize("configuration", [
    "courte:client", "sans-separateur-cle-longue", "cle-assez-longue-123:autre",
    ":client", "cle-assez-longue-123:client,cle-assez-longue-123:admin", " : ",
])
def test_configuration_invalide_sans_divulgation(configuration):
    with pytest.raises(ValueError) as caught:
        charger_cles(configuration)
    candidate = configuration.rpartition(":")[0].strip()
    if len(candidate) >= 16:
        assert candidate not in str(caught.value)
    assert "API_KEYS" in str(caught.value)


def test_parseur_cles_vides_et_caracteres(monkeypatch):
    assert charger_cles(" , ") == {}
    key = "clé:avec:deux-points-12345"
    assert charger_cles(f" {key}:client, ") == {key: "client"}
    monkeypatch.setenv("API_KEYS", f"{key}:client")
    assert identifier(key) == "client"


def test_configuration_invalide_empeche_demarrage(monkeypatch):
    monkeypatch.setenv("API_KEYS", "trop-courte:client")
    with pytest.raises(ValueError, match="clé trop courte"), TestClient(app):
        pass


@pytest.mark.parametrize("exception", [ValueError, RuntimeError])
def test_erreurs_modele_restent_des_500(v1_client, monkeypatch, exception):
    def panne(text):
        raise exception("information interne à ne pas exposer")

    monkeypatch.setattr(app.state, "classifier", SimpleNamespace(predict=panne))
    response = v1_client.post("/v1/predict", json=AVIS)
    assert response.status_code == 500
    assert response.json()["erreur"]["code"] == "ERREUR_INTERNE"
    assert "information interne" not in response.text


@pytest.mark.parametrize("etat", ["absent", "invalide"])
def test_metriques_indisponibles(v1_client, api_keys, monkeypatch, tmp_path, etat):
    import api.v1 as v1

    path = tmp_path / "metriques.json"
    monkeypatch.setattr(v1, "METRIQUES", path)
    contenus = [None] if etat == "absent" else ["non-json", "[]"]
    for contenu in contenus:
        if contenu is not None:
            path.write_text(contenu, encoding="utf-8")
        response = v1_client.get("/v1/modele", headers={"X-API-Key": api_keys["admin"]})
        assert response.status_code == 503
        assert response.json()["erreur"]["code"] == "MODELE_INDISPONIBLE"
