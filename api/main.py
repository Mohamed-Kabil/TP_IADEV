"""API de sentiment : /v1 protégé et routes historiques compatibles."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.model import Prediction, SentimentClassifier, load_model
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.securite import charger_cles
from api.v1 import router

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sentiment_api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    nb_cles = len(charger_cles())
    if nb_cles == 0:
        logger.warning("Aucune clé dans API_KEYS : les routes /v1 protégées répondront 401")
    app.state.classifier = load_model()
    logger.info("Modèle chargé : %s ; %d clé(s) d'API", app.state.classifier.model_name, nb_cles)
    yield
    logger.info("Arrêt de l'API")


app = FastAPI(
    title="Sentiment Analysis API",
    description="Classifie un avis en français. Utilisez /v1 avec une clé d'API.",
    version="1.2.0", lifespan=lifespan,
)
origines = os.environ.get("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origine.strip() for origine in origines.split(",") if origine.strip()],
    allow_credentials=False, allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"], expose_headers=["Deprecation", "Link"],
)

CODES = {
    400: "REQUETE_INVALIDE", 401: "NON_AUTHENTIFIE", 403: "ACCES_REFUSE",
    404: "INTROUVABLE", 405: "METHODE_NON_AUTORISEE", 422: "ENTREE_INVALIDE",
    500: "ERREUR_INTERNE", 503: "MODELE_INDISPONIBLE",
}


def _erreur_v1(
    statut: int, message: str, champs: list[dict[str, str]] | None = None,
    en_tetes: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        {"erreur": {"code": CODES.get(statut, f"HTTP_{statut}"), "message": message,
                    "champs": champs or []}},
        status_code=statut, headers=en_tetes,
    )


def _est_v1(request: Request) -> bool:
    return request.url.path == "/v1" or request.url.path.startswith("/v1/")


@app.exception_handler(StarletteHTTPException)
async def erreur_http(request: Request, exc: StarletteHTTPException) -> Response:
    if _est_v1(request):
        return _erreur_v1(
            exc.status_code, str(exc.detail), en_tetes=dict(exc.headers) if exc.headers else None
        )
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def erreur_validation(request: Request, exc: RequestValidationError) -> Response:
    if _est_v1(request):
        champs = [
            {"champ": ".".join(str(x) for x in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _erreur_v1(422, "Entrée refusée par le contrat de l'API", champs)
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def erreur_interne(request: Request, exc: Exception) -> Response:
    logger.error("Erreur inattendue : %s", type(exc).__name__)
    if _est_v1(request):
        return _erreur_v1(500, "Erreur interne du serveur")
    return JSONResponse({"detail": "Erreur interne du serveur"}, status_code=500)


def _classifier() -> SentimentClassifier:
    clf: SentimentClassifier | None = getattr(app.state, "classifier", None)
    if clf is None:
        raise HTTPException(503, "Modèle non chargé")
    return clf


@app.get("/", summary="Accueil")
async def root() -> dict[str, str]:
    return {"message": "Sentiment Analysis API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse, summary="Santé de l'API")
async def health_check() -> dict[str, str]:
    return {"status": "OK", "model": _classifier().model_name}


@app.post("/predict", response_model=PredictResponse, deprecated=True)
async def predict(request: PredictRequest, response: Response) -> Prediction:
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = '</v1/predict>; rel="successor-version"'
    clf = _classifier()
    try:
        result = clf.predict(request.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(500, "Erreur interne du serveur") from None
    logger.info("predict -> %s (%.2f)", result["label"], result["score"])
    return result


app.include_router(router)
