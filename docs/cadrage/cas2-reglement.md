# Fiche de cadrage : Questions sur le règlement intérieur

## Besoin en une phrase (obligatoire)

Répondre aux questions des étudiants sur le règlement intérieur de l'école en citant le passage et la version du document utilisés, ou orienter vers l'administration lorsque les sources ne suffisent pas.

## Utilisateur final (obligatoire)

Les étudiants cherchent une réponse sur les règles de vie scolaire, les absences ou les procédures ; le personnel administratif vérifie les réponses signalées et maintient les documents de référence.

## Approche retenue (obligatoire)

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Le RAG recherche dans le règlement fourni puis construit une réponse accompagnée d'une référence que l'étudiant peut vérifier. (a) Il exploite les documents existants sans exiger un grand corpus de questions-réponses étiquetées pour entraîner un modèle. (d) Une réponse erronée peut faire manquer une démarche : en cas de source absente, contradictoire ou ambiguë, l'assistant s'abstient et renvoie vers l'administration.

## Données nécessaires et leur origine (obligatoire)

Importer le règlement officiel en vigueur et ses annexes depuis les documents transmis par l'administration, en conservant la version, la date et les numéros de page ou d'article. Constituer avec le personnel un jeu de questions de validation et de réponses attendues, comprenant des questions sans réponse dans le corpus, et réindexer les textes lors de chaque mise à jour.

## Métrique de succès et seuil d'acceptation (obligatoire)

Sur au moins 50 questions réservées à l'évaluation, viser au moins 90 % de réponses jugées correctes par l'administration et une citation pertinente pour chaque réponse affirmative. Exiger l'abstention sur tous les cas du jeu de test dont la réponse est absente des sources ; ces seuils sont des objectifs à mesurer, pas des résultats déjà obtenus.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une mauvaise réponse peut induire un étudiant en erreur sur une procédure ou une échéance. L'administration valide le jeu d'évaluation et les nouvelles versions du corpus ; les demandes de dérogation, les cas individuels et les réponses incertaines lui sont transférés pour décision.

## Risques éthiques ou de confidentialité (obligatoire)

Ne pas demander de nom, de numéro d'étudiant ou de dossier disciplinaire pour une question générale, et limiter les données conservées dans les journaux. Indexer uniquement les documents autorisés pour les utilisateurs concernés, et traiter les textes récupérés comme des sources à citer, sans exécuter leurs éventuelles instructions.

## Approche écartée et pourquoi (facultatif)

Un modèle génératif seul peut fournir une réponse plausible mais absente du règlement ou fondée sur une ancienne version. Une FAQ à règles fixes serait facile à vérifier, mais demanderait davantage de maintenance pour couvrir les formulations variées des étudiants.
