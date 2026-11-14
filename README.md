# sentiment-app : dépôt du binôme

Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.
Ce dépôt grandit chaque semaine ; la semaine 1 met en place le cadrage et l'environnement.

## Installation (3 commandes)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Vérifier son installation

```bash
python scripts/check_setup.py    # diagnostic lisible : versions, dossiers, Git
pytest -q                        # mêmes vérifications sous forme de tests
```

La démarche complète de test, étape par étape, est dans `TESTS.md`.

## Structure

```text
sentiment-app/
├── README.md
├── TP1-ENONCE.md    # énoncé du TP de la semaine 1
├── TESTS.md         # démarche à suivre pour le test
├── requirements.txt
├── .gitignore
├── data/            # jeux de données (versionnés par DVC à partir de la semaine 7)
├── models/          # modèles entraînés (jamais dans Git)
├── app/             # API FastAPI (semaine 3)
├── ui/              # Streamlit (semaine 5)
├── tests/           # pytest (semaine 1 : tests d'environnement)
├── scripts/         # utilitaires (check_setup, nouveau cas de cadrage)
└── docs/cadrage/    # fiches de cadrage du TP1
```

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travail de la semaine 1 |
| --- | --- | --- | --- |
| Membre A | KABIL Mohamed | @Mohamed-Kabil | |
| Membre B | ELGHARBAOUI Youssef| @YoussefElGharbaouiDevs | |
| Membre C | ELWAFI Ahmed Ziad | @elwafiZiad | |

## Journal de bord

Dépôt de travail : [Mohamed-Kabil/TP_IADEV](https://github.com/Mohamed-Kabil/TP_IADEV).
Le suivi des contrôles et les résultats observés sont dans [le journal TP1 à TP6](docs/journal-tp1-tp6.md). Les captures seront placées dans `docs/captures/`.

## Avancement — manuel V1.1

Le complément du TP1 (modèle, API, jeu d’or et abstention) est décrit dans [le compte rendu V1.1](docs/tp1-manuel-v11.md). Bilan local : **68 passed, 1 xfailed**. Le journal historique conserve l’ancienne numérotation et contient la table de correspondance.

Le [TP2 V1.1 — API protégée et client web](docs/tp2-manuel-v11.md) est implémenté : `/v1`, rôles, erreurs uniformes, client HTML/JavaScript. Vérification locale : **112 passed, 1 xfailed**, couverture API **100 %**, **12 tests Node réussis**, Ruff et mypy conformes. Le compte rendu contient les commandes de lancement et les captures.

Le [TP3 V1.1 — interface Streamlit](docs/tp3-manuel-v11.md) ajoute les onglets avis et CSV, les deux graphiques et le téléchargement des résultats. Démarrer l'API, puis `python -m streamlit run ui/app.py`. La suite compte désormais **125 passed, 1 xfailed**, avec **100 %** de couverture API. Les parcours ont aussi été vérifiés dans le navigateur, y compris l'arrêt de l'API. Le compte rendu et le journal contiennent les preuves.

Le [TP4 V1.1 — paquet installable](docs/tp4-manuel-v11.md) fournit `sentiment_app.predict`, la commande `sentiment`, un modèle embarqué et un vérificateur qui installe la roue hors du dépôt dans un environnement neuf. Voir [l'installation du paquet](README-PAQUET.md) et [le journal des versions](CHANGELOG.md).

La [release v1.0.0](https://github.com/Mohamed-Kabil/TP_IADEV/releases/tag/v1.0.0) contient les deux distributions et le rapport **CONFORME**. Les six tests du paquet installé passent sous Windows et en CI Linux.
