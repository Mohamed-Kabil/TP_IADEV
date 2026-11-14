# Journal des versions

## [1.0.0] - 2026-11-14

- Paquet `sentiment_app` autonome : `predict(texte)` retourne une étiquette et un score.
- Modèle TF-IDF/régression logistique de démonstration inclus dans la roue et l'archive source.
- Commande `sentiment`, options `--json` et `--version`.
- Dépendances de sérialisation déclarées ; six tests sur le paquet installé hors des sources.
- Vérificateur du livrable : archives, modèle, métadonnées, tag et installation dans un environnement neuf.
- Limites : jeu de démonstration restreint, erreurs possibles sur les avis difficiles ; pas d'abstention dans le contrat du paquet TP4. L'API `/v1` conserve son abstention.
