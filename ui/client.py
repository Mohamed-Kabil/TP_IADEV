"""Client /v1 du TP3 : l'interface ne charge jamais le modèle."""

import math
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
API_URL = "http://127.0.0.1:8000"
VERDICTS = {
    "POSITIVE": "Avis positif",
    "NEGATIVE": "Avis négatif",
    "INDETERMINE": "Je ne sais pas : à faire vérifier par un humain",
}
INJOIGNABLE = "API injoignable : lancez d'abord python -m uvicorn api.main:app."
REFUS = "Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères."
SANS_MODELE = "Modèle non chargé : python src/train.py, puis relancer l'API."
CLE_REFUSEE = "Clé absente ou invalide : vérifiez API_KEY dans le fichier .env local."
ROLE_REFUSE = "Cette clé ne dispose pas du rôle nécessaire."
REPONSE_INVALIDE = "Réponse inattendue de l'API."
MESSAGES = {
    "ENTREE_INVALIDE": REFUS,
    "NON_AUTHENTIFIE": CLE_REFUSEE,
    "ACCES_REFUSE": ROLE_REFUSE,
    "MODELE_INDISPONIBLE": SANS_MODELE,
    "ERREUR_INTERNE": "Erreur interne de l'API. Réessayez plus tard.",
}


@dataclass
class Reponse:
    ok: bool
    label: str | None = None
    score: float | None = None
    message: str = ""


def creer_session() -> httpx.Client:
    cle = os.environ.get("API_KEY", "").strip()
    return httpx.Client(
        base_url=os.environ.get("API_URL", API_URL),
        headers={"X-API-Key": cle} if cle else {},
        timeout=10,
        trust_env=False,
    )


def _code(response: httpx.Response) -> str:
    try:
        code = response.json()["erreur"]["code"]
        return code if isinstance(code, str) else ""
    except (ValueError, KeyError, TypeError):
        return ""


def _erreur(response: httpx.Response) -> Reponse:
    return Reponse(False, message=MESSAGES.get(_code(response), f"Erreur de l'API ({response.status_code})."))


def sante(session: httpx.Client) -> Reponse:
    try:
        response = session.get("/v1/health")
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if response.status_code != 200:
        return _erreur(response)
    try:
        corps = response.json()
        if corps["status"] != "OK" or not isinstance(corps["model"], str):
            return Reponse(False, message=REPONSE_INVALIDE)
        return Reponse(True, message=corps["model"])
    except (ValueError, KeyError, TypeError):
        return Reponse(False, message=REPONSE_INVALIDE)


def predire(session: httpx.Client, texte: str) -> Reponse:
    try:
        response = session.post("/v1/predict", json={"text": texte})
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if response.status_code != 200:
        return _erreur(response)
    try:
        corps = response.json()
        label, score = corps["label"], corps["score"]
        if (label not in VERDICTS or isinstance(score, bool)
                or not isinstance(score, (int, float)) or not math.isfinite(score)
                or not 0 <= score <= 1):
            return Reponse(False, message=REPONSE_INVALIDE)
        return Reponse(True, label=label, score=float(score))
    except (ValueError, KeyError, TypeError):
        return Reponse(False, message=REPONSE_INVALIDE)


def predire_lot(session: httpx.Client, textes: list[str]) -> list[Reponse]:
    return [predire(session, texte) for texte in textes]


def resumer(reponses: list[Reponse]) -> dict[str, int]:
    compte = Counter(r.label if r.ok and r.label else "REFUS OU ERREUR" for r in reponses)
    return dict(sorted(compte.items()))
