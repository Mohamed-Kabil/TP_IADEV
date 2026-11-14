# TP3 du manuel V1.1 — Interface Streamlit

Réalisé localement le 14 novembre 2026, suivant les pages 38 à 40 du manuel V1.1. Le kit officiel du nouveau TP3 n'étant pas fourni, le client du kit historique `tp5-interface-kit.zip` a été adapté au contrat `/v1`. Les composants et tests sont versionnés dans ce dépôt ; ils ne sont pas présentés comme le nouveau kit officiel.

## Lancement sous PowerShell

Depuis la racine du dépôt, avec `.venv` activé et le modèle entraîné :

```powershell
# À faire une fois si le fichier .env local est absent.
python scripts/configurer_tp2.py

# Terminal 1
python -m uvicorn api.main:app --reload

# Terminal 2
python -m streamlit run ui/app.py
```

Ouvrir http://127.0.0.1:8501. `ui/client.py` charge le `.env` local : `API_URL` désigne l'API et `API_KEY` sa clé client. Les variables d'environnement existantes ont priorité. Aucune clé n'est affichée dans la page ni enregistrée dans les preuves. Le client appelle `/v1/health` et `/v1/predict`, ajoute `X-API-Key`, reconnaît les erreurs par leur code stable et ne charge jamais le modèle.

## Parcours exécutés dans le navigateur

| Essai réel | Résultat |
| --- | --- |
| Avis satisfait | Avis positif, 78 % |
| Produit cassé, service injoignable | Avis négatif, 75 % |
| Texte inconnu `xqzvb wlkptr grombu` | Abstention, 52 %, vérification humaine |
| Trois espaces | Avertissement de refus, sans plantage |
| Fichier `data/avis_exemple.csv` | Six lignes : trois positives, deux négatives, une abstention |
| Téléchargement des résultats | CSV réellement téléchargé et conservé dans les preuves |
| Arrêt de l'API, puis rechargement | Message « API injoignable » ; API relancée et interface rétablie ensuite |

Les six captures : [positif](captures/tp3-v11-positif.jpg), [négatif](captures/tp3-v11-negatif.jpg), [abstention](captures/tp3-v11-abstention.jpg), [refus](captures/tp3-v11-refus.jpg), [graphique du fichier](captures/tp3-v11-csv-graphiques.jpg), [API arrêtée](captures/tp3-v11-api-injoignable.jpg).

Le [CSV téléchargé](controles/tp3-v11-resultats.csv) contient les colonnes `text`, `verdict`, `confiance`, `message`, avec un encodage UTF-8 avec BOM pour faciliter son ouverture sous Windows. Les scores observés sont 0,777 ; 0,7465 ; 0,7142 ; 0,8002 ; 0,5162 ; 0,618. Ces scores décrivent la confiance du modèle, pas une garantie de justesse.

## Fichiers et graphiques

L'envoi des avis nécessite le bouton « Analyser le fichier ». Le tableau et le résumé restent dans la session Streamlit ; télécharger le CSV ne déclenche pas une nouvelle analyse. Un changement de fichier masque les anciens résultats. Une colonne `text` absente, un fichier vide, un encodage incorrect ou un CSV mal formé produit un message lisible. Les lignes vides sont conservées et soumises au refus normal de l'API.

Le premier graphique compte les verdicts. Le second compte les confiances dans des tranches croissantes : `< 0,60`, `[0,60 ; 0,70[`, `[0,70 ; 0,80[`, `[0,80 ; 0,90[`, `[0,90 ; 1,00]`. La borne 0,60 appartient à la deuxième tranche et 1,00 est inclus ; les refus et erreurs sans score sont exclus. Pour les six avis, les effectifs sont **1, 1, 2, 1, 1**. Cette convention explicite corrige les ambiguïtés des bornes du fragment `pd.cut` proposé dans le manuel.

Le navigateur a révélé une erreur JavaScript que les tests AppTest ne détectaient pas : l'apostrophe dans le nom de série `Nombre d'avis` empêchait Vega d'afficher les graphiques avec cette version de Streamlit. Le nom a été changé en `Nombre`, puis les deux graphiques ont été vérifiés visuellement dans le navigateur. AppTest confirme les éléments et les données, mais ne remplace pas cette vérification du rendu JavaScript.

## Validation

```powershell
python -m pytest tests/test_client.py tests/test_interface.py -q
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
python -m ruff check .
python -m mypy api
```

Les deux nouveaux fichiers contiennent **13 tests**. La suite complète après correction des graphiques donne **125 passed, 1 xfailed, 2 warnings in 20.64s**, couverture API **100 %** (217 instructions). Ruff et mypy passent ; mypy vérifie les six modules de l'API. [Sortie complète de pytest](controles/tp3-v11-tests.txt).

L'échec attendu du jeu d'or reste la limite TF-IDF déjà déclarée au TP1. Les deux avertissements proviennent de Starlette/AnyIO et de Streamlit/Altair. Le test d'upload AppTest fournit un flux en mémoire car AppTest 1.39 ne pilote pas `file_uploader` ; le chargement réel et le téléchargement ont donc aussi été exécutés dans le navigateur.

La CI installe désormais Streamlit et rejoue les tests Python, Ruff, mypy et les tests du client web. État de la CI : vérification après publication.

## Démonstration distante

Le déploiement Streamlit Community Cloud reste une procédure, comme dans le manuel ; aucune démonstration distante n'a été publiée. Une interface hébergée aurait besoin d'une API accessible depuis son hébergement : `127.0.0.1` désignerait ce serveur distant. Le travail suivant du manuel est le TP4, consacré au paquet réutilisable.
