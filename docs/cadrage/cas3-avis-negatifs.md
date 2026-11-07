# Fiche de cadrage : Priorisation des avis négatifs

## Besoin en une phrase (obligatoire)

Repérer les avis négatifs parmi les avis clients du site e-commerce et les placer en priorité dans la file du service client, en conservant une file de vérification pour les avis ambigus.

## Utilisateur final (obligatoire)

Les agents du service client consultent les avis prioritaires, confirment leur catégorie et décident de la réponse ; le responsable suit les erreurs de classement et les délais de traitement.

## Approche retenue (obligatoire)

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(a) Un échantillon d'avis historiques peut être étiqueté par les agents pour entraîner et évaluer un classifieur supervisé ; cette annotation reste à réaliser avant de valider le choix. (c) Un modèle TF-IDF avec régression logistique traite des milliers d'avis à faible coût par requête. (d) Un avis négatif manqué retarde sa prise en charge, ce qui justifie de privilégier le rappel de cette classe et de faire vérifier les prédictions incertaines.

## Données nécessaires et leur origine (obligatoire)

Exporter avec autorisation les textes d'avis du site, retirer les identifiants et faire annoter un échantillon représentatif comme positif ou négatif, avec arbitrage des avis mixtes. Dédupliquer les avis avant une séparation chronologique entre entraînement, validation et test, et ne pas utiliser la note comme une étiquette parfaite sans vérification humaine.

## Métrique de succès et seuil d'acceptation (obligatoire)

Sur un jeu de test jamais utilisé pour régler le modèle, viser un F1 macro d'au moins 0,85 et un rappel d'au moins 0,90 pour les avis négatifs. Fixer le seuil d'abstention sur la validation, puis publier sur le test la couverture des décisions automatiques et leurs erreurs, en comptant séparément les abstentions ; ces valeurs sont des objectifs, pas des performances mesurées.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un faux négatif retarde le traitement d'une insatisfaction ; un faux positif mobilise inutilement un agent. Les avis incertains sont envoyés en vérification, un échantillon des avis non prioritaires est contrôlé régulièrement et aucune réponse au client ni suppression d'avis n'est automatisée.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent révéler des noms, des coordonnées ou des informations de commande : les retirer des données d'entraînement et restreindre l'accès aux exports. Comparer les erreurs sur des formulations variées, notamment les négations, l'ironie et les variantes de langue suffisamment représentées, afin de détecter les groupes d'avis moins bien reconnus.

## Approche écartée et pourquoi (facultatif)

Des règles par mots-clés risquent de mal interpréter les négations et les avis mêlant compliments et critiques. Le RAG sert surtout à retrouver des informations dans des documents et n'est pas nécessaire pour cette classification ; un modèle génératif ajouterait un coût par appel à comparer à la solution simple avant toute adoption.
