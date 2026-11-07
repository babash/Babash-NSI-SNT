/* ═══════════════════════════════════════════════════════════════
   Réglages généraux du site
   ═══════════════════════════════════════════════════════════════ */

reglages({
  titre: "Ressources NSI et SNT",
  presentation: "Cours, activités et outils pour la classe, rangés par niveau et par thème.",

  // Le dépôt GitHub du site : sert aux liens « Modifier la liste » et « Déposer un fichier »
  depot: "babash/Babash-NSI-SNT",

  // En bas de chaque page, avec les licences (CC BY-SA 4.0 pour les documents, MIT pour le code).
  // {auteur} est remplacé par le nom ci-dessous. Un texte vide ("") retire la phrase.
  auteur: "Babash - NSI Tani Malandi",
  mention_ia: "Ces ressources sont conçues par {auteur} ; beaucoup le sont avec l'aide de l'IA.",
  reutilisation: "Tu peux les réutiliser et les modifier en mentionnant {auteur} et la licence ; un document modifié se partage sous la même licence.",
  // Une invitation, pas une obligation : la licence CC BY-SA 4.0 ne permet pas d'ajouter de condition.
  invitation_ia: "Si tu utilises l'IA pour les modifier, merci de le préciser.",

  // Les rubriques, dans l'ordre de la page d'accueil.
  // Chaque nom est un dossier qui contient index.html et ressources.js.
  rubriques: [
    "snt",
    "nsi-premiere",
    "nsi-terminale",
    "pp",
    "autres",
  ],
});
