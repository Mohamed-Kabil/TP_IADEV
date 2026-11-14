# TP4 du manuel V1.1 — paquet Python installable

Travail du 14 novembre 2026, suivant les pages 45 à 54 du manuel. Le nouveau kit TP4 n'étant pas disponible dans les ressources fournies, `scripts/verifier_livrable.py` et `tests/test_paquet.py` sont une implémentation locale des contrôles décrits, pas une copie du vérificateur officiel. Le code du paquet reprend le contrat donné dans le manuel.

## Contenu de la version 1.0.0

`src/sentiment_app` expose `predict(texte)` et `__version__`. La commande installée `sentiment` propose une sortie lisible, `--json` et `--version`. `importlib.resources` permet de lire le modèle embarqué quel que soit le dossier courant ; son chargement est mis en cache. Le paquet n'importe ni FastAPI ni Streamlit.

Le contrat du TP4 retourne `positive` ou `negative` et un score, sans abstention. L'API `/v1` garde son contrat distinct et son seuil 0,60. Cette différence est expliquée dans [README-PAQUET.md](../README-PAQUET.md).

Le modèle a été réentraîné avant le commit de version : 290 avis de démonstration, 232 pour l'entraînement, 58 pour le test, F1 macro **0,879**, exactitude **0,8793**, rappel négatif **0,931**. La date des métriques est le 14 novembre 2026. NumPy 1.26.4, scikit-learn 1.5.x et Joblib 1.4.x sont déclarés comme dépendances du paquet pour respecter la sérialisation utilisée.

Le modèle est copié dans `src/sentiment_app/modele/` avant construction, inclus dans les deux distributions et ignoré par Git. La roue ne contient aucun test ni serveur web. La distribution source inclut les sources nécessaires à sa reconstruction. Une distribution Python ne rend pas l'API accessible sur Internet.

## Contrôles

La [suite du dépôt](controles/tp4-v11-tests.txt) donne **125 passed, 1 skipped, 1 xfailed**, couverture API **100 %**. L'unique module ignoré vise le paquet installé : il doit être exécuté dans le nouvel environnement de vérification. Ruff et mypy passent.

Les six tests du paquet contrôlent sa version, son origine dans le `site-packages` du nouvel environnement, le modèle embarqué, les verdicts positif et négatif, les entrées invalides, un texte de faible confiance et la commande installée, y compris son code de refus. Le vérificateur copie ce seul fichier de tests hors du dépôt, retire `PYTHONPATH`/`PYTHONHOME`, crée un venv neuf et exécute Python avec `-I`. Aucun test ignoré n'est accepté pendant cette vérification.

Le vérificateur contrôle aussi le contenu de `dist/`, l'identité du modèle dans la roue et l'archive source, le point d'entrée, le journal des versions, la propreté du dépôt et l'égalité entre le tag et HEAD. Le rapport `docs/livrable-tp4.txt` est ignoré par Git et doit être joint à la release avec la roue et l'archive source. Il contient les empreintes SHA256 des artefacts.

## Refaire la construction et la vérification

Dans le dépôt, environnement activé :

```powershell
python src/make_demo.py
python src/train.py
New-Item -ItemType Directory -Force src/sentiment_app/modele
Copy-Item models/sentiment.joblib src/sentiment_app/modele/
python -m pytest -q
# Enregistrer les changements et poser le tag de version AVANT la construction finale.
python -m pip install build
python -m build
python -m zipfile -l dist/sentiment_app-1.0.0-py3-none-any.whl
python scripts/verifier_livrable.py
```

Utiliser un dossier `dist/` vide pour une nouvelle construction ; le vérificateur refuse les fichiers supplémentaires. Le tag `v1.0.0` reste attaché au commit de version : ne pas le déplacer pour une modification ultérieure.

La CI construit également la roue puis l'installe dans un environnement neuf, hors des sources, et exécute les six tests. La validation finale du rapport, la release et leur CI seront enregistrées après les contrôles.

## Limites

Les limites du petit jeu de démonstration et l'erreur TF-IDF connue demeurent. Seuls les fichiers Joblib de confiance doivent être chargés. Les essais locaux utilisent Python 3.11 sous Windows ; la CI vérifie également Linux. Le complément Spring Boot de la page 51 est une activité séparée et n'est pas inclus dans cette livraison du paquet Python.
