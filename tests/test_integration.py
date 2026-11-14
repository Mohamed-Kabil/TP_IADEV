"""Démarrage réel, pannes, absence du modèle et CORS."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

from api.main import app
from api.v1 import classifier

ROOT = Path(__file__).resolve().parents[1]


def test_serveur_reel_repond(api_keys):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            try:
                response = httpx.get(f"http://127.0.0.1:{port}/v1/health", timeout=1, trust_env=False)
                break
            except httpx.TransportError:
                assert process.poll() is None, "Le serveur s'est arrêté au démarrage"
                time.sleep(.1)
        else:
            raise AssertionError("Serveur non prêt dans le délai prévu")
        assert response.status_code == 200
        result = httpx.post(f"http://127.0.0.1:{port}/v1/predict",
                            headers={"X-API-Key": api_keys["client"]}, json={"text": "Service impeccable"},
                            trust_env=False)
        assert result.status_code == 200
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def test_absence_modele_refuse_demarrage(api_keys, tmp_path):
    code = (
        "import sys; from pathlib import Path; sys.path.insert(0,'src'); import predict; "
        f"predict.MODELE=Path({str(tmp_path/'absent.joblib')!r}); "
        "import uvicorn; uvicorn.run('api.main:app',host='127.0.0.1',port=0)"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"}, timeout=30)
    assert result.returncode != 0
    assert "FileNotFoundError" in result.stderr
    assert "Application startup failed" in result.stderr


def test_etat_modele_absent_donne_503(v1_client, monkeypatch):
    monkeypatch.setattr(app.state, "classifier", None)
    for route in ["/health", "/v1/health"]:
        response = v1_client.get(route)
        assert response.status_code == 503
    for route in ["/predict", "/v1/predict"]:
        response = v1_client.post(route, json={"text": "Texte"})
        assert response.status_code == 503
    assert response.json()["erreur"]["code"] == "MODELE_INDISPONIBLE"


def test_panne_ancienne_route_reste_500(v1_client, monkeypatch):
    for exception in [RuntimeError, ValueError]:
        def panne(text, erreur=exception):
            raise erreur("détail interne")

        monkeypatch.setattr(app.state, "classifier", SimpleNamespace(predict=panne))
        response = v1_client.post("/predict", json={"text": "Texte"})
        assert response.status_code == 500
        assert response.json() == {"detail": "Erreur interne du serveur"}


def test_erreurs_inattendues_masquees(api_keys):
    def panne():
        raise RuntimeError("ne pas exposer")

    with TestClient(app, raise_server_exceptions=False) as client:
        app.dependency_overrides[classifier] = panne
        try:
            response = client.get("/v1/health")
            assert response.status_code == 500
            assert response.json()["erreur"]["code"] == "ERREUR_INTERNE"
        finally:
            app.dependency_overrides.clear()
        app.state.classifier = SimpleNamespace(model_name="invalide", predict=lambda text: {})
        response = client.post("/predict", json={"text": "Texte"})
        assert response.status_code == 500
        assert "ne pas exposer" not in response.text


def test_cors_origine_autorisee_et_refusee(v1_client):
    headers = {"Access-Control-Request-Method": "POST",
               "Access-Control-Request-Headers": "content-type,x-api-key"}
    accepted = v1_client.options("/v1/predict", headers={**headers, "Origin": "http://localhost:5500"})
    assert accepted.status_code == 200
    assert accepted.headers["Access-Control-Allow-Origin"] == "http://localhost:5500"
    refused = v1_client.options("/v1/predict", headers={**headers, "Origin": "http://localhost:5600"})
    assert refused.status_code == 400
    assert "Access-Control-Allow-Origin" not in refused.headers
