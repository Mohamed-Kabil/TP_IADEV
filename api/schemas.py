"""Contrats HTTP de l'API de sentiment, manuel V1.1."""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]


class PredictRequest(BaseModel):
    """Un avis de 1 à 2000 caractères, comportant du texte."""

    text: str = Field(
        ..., min_length=1, max_length=2000,
        examples=["Livraison rapide, produit conforme, très satisfait"],
    )

    @field_validator("text")
    @classmethod
    def refuser_texte_blanc(cls, valeur: str) -> str:
        if not valeur.strip():
            raise ValueError("texte vide une fois les blancs retirés")
        return valeur


class PredictResponse(BaseModel):
    label: Label
    score: float = Field(..., ge=0, le=1)
    text: str = Field(..., max_length=100)


class HealthResponse(BaseModel):
    status: str
    model: str


class ModeleResponse(BaseModel):
    model: str
    seuil_abstention: float
    metriques: dict[str, Any]


class ChampInvalide(BaseModel):
    champ: str
    message: str


class DetailErreur(BaseModel):
    code: str
    message: str
    champs: list[ChampInvalide] = Field(default_factory=list)


class ErreurV1(BaseModel):
    erreur: DetailErreur


class ErrorResponse(BaseModel):
    """Format historique, conservé hors /v1."""

    detail: str
