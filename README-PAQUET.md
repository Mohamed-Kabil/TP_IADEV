# sentiment-app 1.0.0

Classifie des avis français en `positive` ou `negative`, avec un score de confiance. Le modèle TF-IDF/régression logistique est inclus : aucun serveur API ni clonage du dépôt n'est nécessaire.

## Installation

Python 3.11 ou supérieur et pip sont nécessaires. Télécharger la roue de la release GitHub `v1.0.0`, puis :

```powershell
python -m pip install sentiment_app-1.0.0-py3-none-any.whl
sentiment "Produit cassé et service injoignable, à fuir" --json
sentiment --version
```

Depuis Python :

```python
from sentiment_app import predict
print(predict("Livraison rapide, produit conforme, très satisfait"))
# {'label': 'positive', 'score': 0.777}
```

La roue fonctionne hors du dépôt. La distribution source permet de la reconstruire avec `python -m build`. Le point d'entrée `sentiment` est installé dans le dossier des exécutables de l'environnement Python.

## Limites et compatibilité

Le modèle de cette version est entraîné sur 290 avis de démonstration, avec 232 avis d'entraînement et 58 de test ; F1 macro 0,879. Il ne représente pas la diversité des avis réels. Négations, ironie, avis mitigés et mots inconnus peuvent produire une mauvaise réponse. Le score n'est pas une probabilité de justesse calibrée.

Le paquet suit le contrat du TP4 : étiquettes minuscules et score brut, sans abstention. L'API `/v1` conserve son propre contrat avec abstention sous 0,60 et étiquettes majuscules. Aucun changement de l'API n'est nécessaire pour installer ce paquet.

Construction et essais : Python 3.11, NumPy 1.26.4, scikit-learn 1.5.x et Joblib 1.4.x. Ces dépendances sont déclarées dans les métadonnées pour respecter la compatibilité du modèle sérialisé. Installer uniquement les distributions de confiance de cette release : charger un fichier Joblib inconnu peut exécuter du code. La commande ne lit aucun chemin de modèle fourni par l'utilisateur.
