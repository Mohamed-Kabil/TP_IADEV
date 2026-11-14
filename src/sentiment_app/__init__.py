"""Classer un avis français avec le modèle embarqué, sans serveur."""

from importlib.metadata import version

from sentiment_app.predict import predict

__version__ = version("sentiment-app")
__all__ = ["__version__", "predict"]
