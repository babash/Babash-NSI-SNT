/* ═══════════════════════════════════════════════════════════════
   Réglages généraux du site
   ═══════════════════════════════════════════════════════════════ */

reglages({
  titre: "Ressources NSI et SNT",
  presentation: "Cours, activités et outils pour la classe, rangés par niveau et par thème.",

  // Le dépôt GitHub du site : sert aux liens « Modifier la liste » et « Déposer un fichier »
  depot: "babash/Babash-NSI-SNT",

  // En bas de chaque page : l'auteur des ressources (licences CC BY-SA 4.0 et MIT),
  // puis la mention générale sur l'IA (formulation à valider par l'enseignant).
  auteur: "Babash - NSI Tani Malandi",
  mention_ia: "Beaucoup de ressources de ce site sont créées avec l'aide de l'IA.",

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
