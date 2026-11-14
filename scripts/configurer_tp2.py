"""Crée .env avec deux clés locales, sans les afficher et sans écraser l'existant."""

import secrets
from pathlib import Path


def main() -> None:
    path = Path(__file__).resolve().parents[1] / ".env"
    if path.exists():
        print(".env existe déjà : conservé. Vérifiez API_KEYS et API_KEY localement.")
        return
    client, admin = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    contenu = (
        f"API_KEYS={client}:client,{admin}:admin\nAPI_KEY={client}\n"
        "API_URL=http://127.0.0.1:8000\n"
        "CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500\n"
    )
    with path.open("x", encoding="utf-8") as stream:
        stream.write(contenu)
    print(".env créé avec une clé client et une clé admin ; aucune clé affichée.")


if __name__ == "__main__":
    main()
