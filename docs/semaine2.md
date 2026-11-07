# Semaine 2 : le modèle de sentiment

## Mesures observées sur le jeu de démonstration

Le jeu contient 290 avis équilibrés : 145 positifs et 145 négatifs, dont 100 avis mitigés et 30 neutres. Le découpage reproductible réserve 232 avis à l'entraînement et 58 au test ; le vocabulaire appris contient 316 termes.

- F1 macro : 0,879, supérieur au seuil de 0,85.
- Rappel de la classe négative : 93,10 %.
- Matrice de confusion (lignes : vérité ; colonnes : prédiction) :

```text
            negative  positive
negative          27         2
positive           5        24
```

## Analyse des erreurs

L'évaluation du modèle de démonstration montre 7 erreurs sur 58 avis : 2 avis négatifs classés positifs et 5 avis positifs classés négatifs, tous sur des avis mitigés.

Par exemple, « Commande jamais reçue et remboursement en attente au début, sauf que ensuite je recommande sans hésiter. » est positif selon sa conclusion, mais prédit négatif. Le modèle TF-IDF utilise des mots et des groupes de deux mots, mais représente mal le retournement du sentiment dans l'ensemble de la phrase.

Des représentations contextuelles pourraient mieux prendre en compte ces retournements ; leur apport devrait être mesuré sur un jeu de test indépendant.

## Résultats Allociné

- Source : Allociné, 20 000 avis, dont 10 204 négatifs.
- Entraînement : 16 000 avis ; test : 4 000 avis.
- Vocabulaire : 149 529 termes.
- F1 macro : 0,9205.
- Exactitude : 92,05 %.
- Rappel de la classe négative : 91,13 %.
- Les objectifs de F1 macro ≥ 0,85 et de rappel négatif ≥ 0,90 sont atteints sur ce jeu de test.
- Tests locaux exécutés par le membre A : `42 passed in 3.49s`.
- [CI réussie du commit TP2 68b316b](https://github.com/Mohamed-Kabil/TP_IADEV/actions/runs/42369544357).

Les deux jeux représentent des tâches différentes : le score supérieur sur Allociné ne suffit pas à démontrer une amélioration sur les avis e-commerce. Lors d'un essai local du modèle Allociné, « Livraison rapide, produit conforme, très satisfait » a été classé négatif avec un score de 0,5008, ce qui illustre cette différence de domaine.

## Reproductibilité et artefacts

Le découpage précède la vectorisation et utilise `random_state=42` ; le vectoriseur et le classifieur sont sauvegardés dans un même pipeline. `models/metrics.json` est versionné pour conserver les mesures ; `models/sentiment.joblib` et `data/demo_reviews.csv` restent exclus de Git et se régénèrent avec les scripts du TP.
