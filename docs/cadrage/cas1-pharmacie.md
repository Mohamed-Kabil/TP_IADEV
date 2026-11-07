# Fiche de cadrage : Ordonnances incomplètes en pharmacie

## Besoin en une phrase (obligatoire)

Signaler au pharmacien les informations manquantes dans une ordonnance avant sa vérification et sa prise en charge, sans décider automatiquement de la délivrance.

## Utilisateur final (obligatoire)

Le pharmacien consulte la liste des champs manquants et vérifie le document original ; le personnel de préparation peut utiliser ces alertes pour orienter les dossiers à compléter.

## Approche retenue (obligatoire)

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Une liste de champs attendus, définie et validée par le pharmacien, permet de relier chaque alerte à une règle précise et vérifiable. (a) Aucun corpus étiqueté n'est nécessaire pour contrôler la présence de ces champs ; (c) ces vérifications ont un faible coût par requête. (d) Une omission non détectée pouvant affecter la prise en charge, le système reste une aide au contrôle et chaque ordonnance est validée par le pharmacien.

## Données nécessaires et leur origine (obligatoire)

Utiliser une liste de champs et de conditions d'application fournie par le pharmacien, ainsi que des ordonnances fictives structurées pour les essais. Le premier périmètre porte sur des champs saisis dans un formulaire ; les scans et l'OCR demanderaient une validation distincte de l'extraction avant d'appliquer les règles.

## Métrique de succès et seuil d'acceptation (obligatoire)

Objectifs proposés avant mise en service : détecter 100 % des omissions prévues dans un jeu de validation synthétique couvrant chaque règle, et obtenir au plus 5 % de fausses alertes sur les cas complets validés par le pharmacien. Mesurer séparément les omissions manquées et les fausses alertes ; ces seuils restent à évaluer et ne garantissent pas la sécurité sur des documents réels.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un faux négatif laisse passer un document incomplet, tandis qu'un faux positif retarde son traitement. Le pharmacien contrôle systématiquement l'original, traite les alertes et garde la décision finale ; un champ illisible ou incertain doit être signalé comme à vérifier plutôt que considéré comme présent.

## Risques éthiques ou de confidentialité (obligatoire)

Les ordonnances peuvent contenir des données personnelles et de santé : limiter les accès au personnel autorisé, utiliser des données fictives pour le TP et éviter toute donnée réelle dans Git ou les journaux. Pour un usage réel, prévoir un stockage protégé et une durée de conservation définie avec la pharmacie.

## Approche écartée et pourquoi (facultatif)

Un modèle génératif seul pourrait inventer une information manquante ou produire une validation difficile à reproduire. Des règles explicites suffisent au contrôle de complétude dans ce périmètre et permettent d'expliquer chaque alerte.
