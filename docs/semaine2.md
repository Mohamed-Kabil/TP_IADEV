\# Semaine 2 : le modèle de sentiment



\## Mesures observées



Sur le jeu de démonstration : 290 avis, dont 232 pour

l'entraînement et 58 pour le test.

Le F1 macro obtenu est de 0,879, au-dessus du seuil de 0,85.



\## Analyse des erreurs



L'évaluation du modèle de démonstration montre 7 erreurs

sur 58 avis : 2 avis négatifs classés positifs et 5 avis

positifs classés négatifs.



Ces erreurs concernent des avis mitigés : une première

opinion est suivie d'un retournement, par exemple

« sauf que ensuite ». Le modèle TF-IDF utilise des mots

et des groupes de deux mots, mais représente mal

l'évolution du sentiment dans la phrase.



Des représentations contextuelles pourraient mieux

prendre en compte ces retournements ; il faudrait

mesurer leur apport sur un jeu de test indépendant.



\## Résultats Allociné



À compléter avec les résultats réellement obtenus après :

python src/train.py --allocine



\- F1 macro :

\- Rappel de la classe négative :

\- Résultat de pytest :
## Résultats Allociné



\- Données : 20 000 avis, dont 16 000 pour l'entraînement

&#x20; et 4 000 pour le test.

\- F1 macro : 0,9205.

\- Exactitude : 92,05 %.

\- Rappel de la classe négative : 91,13 %.

\- Les objectifs de F1 macro ≥ 0,85 et de rappel négatif

&#x20; ≥ 0,90 sont atteints sur ce jeu de test.

