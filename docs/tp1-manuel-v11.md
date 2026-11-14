# TP1 — Manuel V1.1 : modèle, API et jeu d'or

Mise à jour du 14 novembre 2026. Ce TP1 regroupe l'entraînement et l'API que l'ancien guide appelait TP2 et TP3 ; les comptes rendus historiques `semaine2.md` et `semaine3.md` restent conservés.

## Jeu de référence et provenance

Le fichier [data/jeu_or.csv](../data/jeu_or.csv) contient 20 avis : 10 positifs et 10 négatifs, dont 8 cas difficiles identifiés (négations, concessions, avis mitigés et vocabulaire peu représenté). Les textes et leurs étiquettes sémantiques ont été définis avant le premier passage du modèle ; ils n'ont pas été modifiés après lecture des prédictions.

Ce jeu a été proposé par l'assistant pour compléter le TP à la demande de l'équipe : il ne représente pas des avis recueillis auprès de vrais clients ni une annotation indépendante par les membres. Les membres doivent relire les cas et pouvoir expliquer leurs étiquettes ; ce jeu pédagogique ne suffit pas à mesurer la performance en production. Aucun texte n'est repris à l'identique du CSV de démonstration.

Le test `tests/test_jeu_or.py` et les scripts `src/bilan_jeu_or.py` et `src/courbe_seuil.py` proviennent, sans modification, du kit étudiant `tp4-tests-qualite-kit.zip` déjà fourni. Leur numérotation correspond à l'ancien parcours ; leur utilisation ici répond à la vérification du jeu d'or demandée par le TP1 du nouveau manuel.

## Erreurs observées et abstention

Avant l'ajout du seuil, deux avis négatifs étaient prédits positifs : « Le service semblait impeccable, mais finalement la notice est incompréhensible et des pièces sont manquantes. » à environ 0,52, et « Colis abîmé, je suis déçu » à environ 0,67. Le second est l'erreur annoncée page 18 du manuel ; son étiquette NEGATIVE est conservée et sa raison est écrite dans la colonne `erreur_connue`.

L'API applique désormais le seuil 0,60 décrit page 22 du manuel : un score strictement inférieur donne `INDETERMINE`, avec le score d'origine et le même aperçu du texte. La fonction de prédiction du modèle conserve ses deux classes ; l'abstention est une décision de l'enveloppe API, pas une troisième classe entraînée.

La [courbe réellement exécutée](controles/tp1-v11-seuil.txt) donne, sur les 58 avis de test du jeu de démonstration :

| Seuil | Décisions automatiques | Erreurs parmi ces décisions | Vers un humain |
| --- | --- | --- | --- |
| 0,50 | 58 | 7 | 0 |
| 0,60 | 42 | 2 | 16 |
| 0,70 | 37 | 0 | 21 |

Le seuil 0,60 est repris du manuel, pas ajusté pour faire passer les nouveaux avis. Comme la courbe est calculée sur les 58 exemples de test déjà analysés, cette comparaison est pédagogique : une évaluation finale du réglage demanderait une validation séparée et un autre jeu de test indépendant.

## Résultats du jeu d'or

Le [bilan enregistré](controles/tp1-v11-jeu-or.txt) contient 16 réponses justes, 3 abstentions et 1 erreur franche déclarée sur 20 avis. L'avis mitigé prédit à 0,52 est maintenant orienté vers une vérification humaine ; l'erreur connue à 0,67 reste une erreur malgré le seuil.

Les tests paramétrés contrôlent chaque avis via `POST /predict`. L'erreur connue utilise `xfail(strict=True)` : une correction future inattendue produira un XPASS strict et imposera de revoir la déclaration, plutôt que de conserver une exception devenue inutile.

## Contrôles du manuel

| Contrôle | Résultat local observé |
| --- | --- |
| Modèle + jeu d'or | 24 passed, 1 xfailed, 1 warning in 9.00s |
| API (tests déjà existants, inclus dans la suite) | 6 tests réussis |
| Suite complète | 68 passed, 1 xfailed, 1 warning in 10.17s |

Preuves : [tests modèle et jeu d'or](controles/tp1-v11-modele-tests.txt), [suite complète](controles/tp1-v11-pytest.txt). Le seul avertissement observé est la dépréciation AnyIO issue de Starlette/TestClient.

La CI entraîne son propre modèle avant de lancer les tests. Les familles de versions utilisées pour pandas, scikit-learn, Joblib, pytest et NumPy sont alignées sur l'environnement du projet. Son nouveau résultat sera ajouté après publication et observation.

## Artefacts et commandes

Le jeu d'or est versionné explicitement dans `.gitignore` ; `models/sentiment.joblib`, `.venv` et le CSV de démonstration restent exclus.

```powershell
python src/make_demo.py
python src/train.py
python src/courbe_seuil.py
python src/bilan_jeu_or.py
python -m pytest tests/test_model.py tests/test_jeu_or.py -q
python -m pytest -q
```

Le contrôle de clone neuf de l'Atelier 0 et les contributions ou captures sur les autres postes restent distincts de ces résultats locaux. Les routes `/v1`, les clés et rôles et le client web relèvent du TP2 et ne sont pas ajoutés dans cette étape.
