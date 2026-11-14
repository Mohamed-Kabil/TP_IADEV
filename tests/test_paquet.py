"""Six contrôles du paquet installé, exécutables hors des sources."""

import importlib
import importlib.util
import json
import os
import subprocess
import sys
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path

import pytest

spec = importlib.util.find_spec("sentiment_app")
if not (spec and "site-packages" in (spec.origin or "")) and not os.getenv("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : python scripts/verifier_livrable.py", allow_module_level=True)

paquet = importlib.import_module("sentiment_app")


def test_version():
    assert paquet.__version__ == version("sentiment-app") == "1.0.0"


def test_ressource_et_import_installes():
    origine = Path(paquet.__file__).resolve()
    assert "site-packages" in origine.parts
    assert origine.is_relative_to(Path(sys.prefix).resolve())
    assert files("sentiment_app").joinpath("modele/sentiment.joblib").is_file()


def test_positif():
    resultat = paquet.predict("Livraison rapide, produit conforme, très satisfait")
    assert resultat == {"label": "positive", "score": .777}


def test_negatif():
    resultat = paquet.predict("Produit cassé et service injoignable, à fuir")
    assert resultat == {"label": "negative", "score": .7465}


def test_entrees_invalides_et_confiance():
    for texte in ["", "   ", None, 42]:
        with pytest.raises(ValueError):
            paquet.predict(texte)
    resultat = paquet.predict("xqzvb wlkptr grombu")
    assert resultat["label"] in {"positive", "negative"}
    assert 0 <= resultat["score"] < .60


def test_commande_installee():
    executable = Path(sys.executable).parent / ("sentiment.exe" if os.name == "nt" else "sentiment")
    resultat = subprocess.run([str(executable), "Produit cassé et service injoignable, à fuir", "--json"],
                              capture_output=True, text=True, check=True)
    assert json.loads(resultat.stdout) == {"label": "negative", "score": .7465}
    version_cli = subprocess.run([str(executable), "--version"], capture_output=True, text=True, check=True)
    assert version_cli.stdout.strip() == "sentiment 1.0.0"
    refus = subprocess.run([str(executable), "   "], capture_output=True, text=True)
    assert refus.returncode == 2 and "erreur" in refus.stderr
