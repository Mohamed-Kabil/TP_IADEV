from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def cadrage_dir(root: Path) -> Path:
    return root / "docs" / "cadrage"


@pytest.fixture
def api_keys(monkeypatch):
    """Clés fictives propres aux tests ; jamais les clés du .env local."""
    keys = {"client": "client-test-key-0123456789", "admin": "admin-test-key-0123456789"}
    monkeypatch.setenv("API_KEYS", f"{keys['client']}:client,{keys['admin']}:admin")
    return keys


@pytest.fixture
def v1_client(api_keys):
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app, headers={"X-API-Key": api_keys["client"]}) as client:
        yield client
