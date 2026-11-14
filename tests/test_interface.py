"""AppTest exécute la vraie page avec l'API en mémoire, sans serveur."""

from io import BytesIO
from pathlib import Path

import httpx
import pandas as pd
import pytest
import streamlit as st
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from api.main import app
from ui import client
from ui.donnees import charger_csv, exporter_csv, tranches_confiance

ROOT = Path(__file__).resolve().parents[1]
PAGE = str(ROOT / "ui/app.py")


@pytest.fixture
def page(api_keys, monkeypatch):
    monkeypatch.setattr(client, "creer_session", lambda: TestClient(
        app, headers={"X-API-Key": api_keys["client"]}
    ))
    return AppTest.from_file(PAGE, default_timeout=30).run()


def analyser(page, texte):
    page.text_area[0].input(texte).run()
    page.button[0].click().run()
    assert not page.exception
    return page


def test_page_et_parcours_csv(page, monkeypatch):
    assert any("API prête" in element.value for element in page.caption)
    contenu = {"csv": (ROOT / "data/avis_exemple.csv").read_bytes()}
    # AppTest 1.39 ne pilote pas file_uploader : fournir son flux de sortie.
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: BytesIO(contenu["csv"]))
    page.run()
    next(button for button in page.button if button.key == "analyser_lot").click().run()
    assert not page.exception
    tableau = page.dataframe[0].value
    assert len(tableau) == 6
    assert tableau["verdict"].value_counts().to_dict() == {
        "Avis positif": 3, "Avis négatif": 2,
        "Je ne sais pas : à faire vérifier par un humain": 1,
    }
    assert len(page.get("arrow_vega_lite_chart")) == 2
    assert len(page.get("download_button")) == 1
    export = pd.read_csv(BytesIO(exporter_csv(tableau)))
    assert len(export) == 6 and list(export.columns) == list(tableau.columns)
    page.run()
    assert len(page.dataframe[0].value) == 6  # Résultats conservés après réexécution.
    tranches = tranches_confiance(pd.Series([0, .5, .6, .7, .8, .9, 1, None]))
    assert tranches.tolist() == [2, 1, 1, 1, 2]  # Bornes 0,60 et 1,00 comptées correctement.
    assert charger_csv(b"text\n\n")["text"].tolist() == [""]
    for data, message in [
        (b"autre\nbonjour\n", "Colonne text absente"), (b"text\n", "aucun avis"),
        (b"", "CSV illisible"), (b'text\n"non termine', "CSV illisible"),
        (b"text\n\xff\n", "CSV illisible"),
    ]:
        contenu["csv"] = data
        page.run()
        assert not page.exception
        assert any(message in element.value for element in page.error)


def test_avis_positif(page):
    resultat = analyser(page, "Livraison rapide, produit conforme, très satisfait")
    assert resultat.metric[0].label == "Avis positif"
    assert resultat.metric[0].value == "78%"


def test_texte_inconnu(page):
    resultat = analyser(page, "xqzvb wlkptr grombu")
    assert resultat.metric[0].label.startswith("Je ne sais pas")
    assert any("seuil d'abstention" in element.value for element in resultat.info)


def test_espaces_refuses(page):
    assert analyser(page, "   ").warning[0].value == client.REFUS


def test_api_injoignable(monkeypatch):
    def hors_ligne(request):
        raise httpx.ConnectError("serveur absent", request=request)

    monkeypatch.setattr(client, "creer_session", lambda: httpx.Client(
        base_url="http://test", transport=httpx.MockTransport(hors_ligne)
    ))
    page = AppTest.from_file(PAGE, default_timeout=30).run()
    assert not page.exception
    assert page.error[0].value == client.INJOIGNABLE
