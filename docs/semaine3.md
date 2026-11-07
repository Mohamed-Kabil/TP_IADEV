# Semaine 3 : l'API, notes de l'équipe

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

Le chargement du modèle se fait dans le `lifespan`, avant que le serveur accepte des requêtes. Lors du contrôle T20, un lancement distinct sur le port 8001, modèle temporairement déplacé, a échoué avec `FileNotFoundError`, puis `Application startup failed` et un code de sortie 3 : le service n'annonce donc pas un démarrage réussi sans sa dépendance principale.

Le code 503 sert à une autre situation : une requête arrive sur une application déjà démarrée, mais aucun classifieur n'est disponible dans son état. Le contrôle T20 n'atteint pas ce stade ; le modèle a été restauré dans un bloc `finally`, puis la santé de l'API initiale a été revérifiée.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Les deux validations protègent deux points d'entrée différents : Pydantic contrôle le contrat HTTP, tandis que la fonction `predict()` du TP2 reste utilisable directement, sans l'API. Pour `{"text":""}`, l'essai HTTP a donné 422 avec `string_too_short` : Pydantic rejette cette requête avant l'appel au modèle, il ne s'agit pas de deux refus successifs pour le même appel.

Le champ absent a donné 422 avec `missing`, et `{"text":42}` a donné 422 avec `string_type`. La validation interne du prédicteur conserve son utilité pour les appels Python directs et pour les chaînes faites d'espaces.

## Résultats observés

| Contrôle | Résultat |
| --- | --- |
| T14 | 48 passed, 1 warning in 4.47s |
| T15 | GET /health : 200, status OK |
| T16 | POST /predict : 200, POSITIVE, 0.777 |
| T17 | POST /predict : 200, NEGATIVE, 0.7465 |
| T18 | Texte vide, champ absent, nombre : 422 dans les trois cas |
| T19 | [CI réussie du commit TP3](https://github.com/Mohamed-Kabil/TP_IADEV/actions/runs/42370509197) |
| T20 | Démarrage sans modèle refusé ; modèle ensuite restauré |

L'avertissement de dépréciation AnyIO vient de Starlette/TestClient et n'empêche pas les tests de passer. Le modèle actif est celui de démonstration, réentraîné comme demandé au TP3 ; les mesures Allociné du TP2 restent consignées dans `semaine2.md`.

Les [réponses HTTP](controles/tp3-t15-t18-reponses.json), la [sortie des tests](controles/tp3-t14-pytest.txt) et la [trace du démarrage sans modèle](controles/tp3-t20-sans-modele.txt) sont conservées comme preuves textuelles. Les neuf captures du TP3 sont intégrées au [journal T14 à T20](journal-tp1-tp6.md#tp3--exposer-le-modèle-par-une-api). Les images T14 et T20 affichent les sorties enregistrées sur GitHub ; celles de T15 à T18 montrent les requêtes réexécutées dans Swagger, et T19 le run CI réussi.
