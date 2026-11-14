"""Routes /v1 et permissions explicites, manuel V1.1."""

import json
import logging
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from api.model import SEUIL_ABSTENTION, Prediction, SentimentClassifier
from api.schemas import ErreurV1, HealthResponse, ModeleResponse, PredictRequest, PredictResponse
from api.securite import exiger

logger = logging.getLogger("sentiment_api")
METRIQUES = Path(__file__).resolve().parents[1] / "models/metrics.json"
ERREURS: dict[int | str, dict[str, Any]] = {
    code: {"model": ErreurV1} for code in (401, 403, 422, 500, 503)
}
router = APIRouter(prefix="/v1", tags=["v1"], responses=ERREURS)


def classifier(request: Request) -> SentimentClassifier:
    clf: SentimentClassifier | None = getattr(request.app.state, "classifier", None)
    if clf is None:
        raise HTTPException(503, "Modèle non chargé")
    return clf


Classifier = Annotated[SentimentClassifier, Depends(classifier)]


@router.get("/health", response_model=HealthResponse, summary="Santé (public)")
def sante(clf: Classifier) -> dict[str, str]:
    return {"status": "OK", "model": clf.model_name}


@router.post(
    "/predict", response_model=PredictResponse, summary="Classer un avis (client, admin)",
    dependencies=[Depends(exiger("client", "admin"))],
)
def predire(corps: PredictRequest, clf: Classifier) -> Prediction:
    try:
        resultat = clf.predict(corps.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(500, "Erreur interne du serveur") from None
    logger.info("v1 predict -> %s (%.2f)", resultat["label"], resultat["score"])
    return resultat


@router.get(
    "/modele", response_model=ModeleResponse, dependencies=[Depends(exiger("admin"))]
)
def modele(clf: Classifier) -> ModeleResponse:
    try:
        metriques = json.loads(METRIQUES.read_text(encoding="utf-8"))
        if not isinstance(metriques, dict):
            raise ValueError("métriques invalides")
    except (OSError, ValueError):
        raise HTTPException(503, "Métriques indisponibles") from None
    return ModeleResponse(
        model=clf.model_name, seuil_abstention=SEUIL_ABSTENTION, metriques=metriques
    )
