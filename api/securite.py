"""Clés d'API et rôles : authentifier avant d'autoriser."""

import os
import secrets
from collections.abc import Callable
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

Role = Literal["client", "admin"]
LONGUEUR_MIN = 16
NON_AUTHENTIFIE = {"WWW-Authenticate": "ApiKey"}
EN_TETE = APIKeyHeader(name="X-API-Key", auto_error=False)


def charger_cles(brut: str | None = None) -> dict[str, Role]:
    brut = os.environ.get("API_KEYS", "") if brut is None else brut
    cles: dict[str, Role] = {}
    for entree in filter(None, (morceau.strip() for morceau in brut.split(","))):
        cle, separateur, role = entree.rpartition(":")
        if not separateur:
            raise ValueError("API_KEYS : format attendu clé:rôle")
        if role == "client":
            role_valide: Role = "client"
        elif role == "admin":
            role_valide = "admin"
        else:
            raise ValueError("API_KEYS : rôle inconnu (attendu : client ou admin)")
        if len(cle) < LONGUEUR_MIN:
            raise ValueError(f"API_KEYS : clé trop courte (minimum {LONGUEUR_MIN} caractères)")
        if cle in cles:
            raise ValueError("API_KEYS : clé dupliquée")
        cles[cle] = role_valide
    return cles


def identifier(cle: Annotated[str | None, Security(EN_TETE)]) -> Role:
    if not cle:
        raise HTTPException(
            401, "Clé d'API manquante : en-tête X-API-Key", headers=NON_AUTHENTIFIE
        )
    for connue, role in charger_cles().items():
        if secrets.compare_digest(cle.encode(), connue.encode()):
            return role
    raise HTTPException(401, "Clé d'API invalide", headers=NON_AUTHENTIFIE)


def exiger(*autorises: Role) -> Callable[[Role], Role]:
    def verifier(role: Annotated[Role, Depends(identifier)]) -> Role:
        if role not in autorises:
            raise HTTPException(403, f"Accès refusé au rôle « {role} »")
        return role

    return verifier
