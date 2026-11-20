/* ═══════════════════════════════════════════════════════════════
   Réglages généraux du site
   ═══════════════════════════════════════════════════════════════ */

reglages({
  titre: "Ressources NSI et SNT",
  presentation: "Cours, activités et outils pour la classe, rangés par niveau et par thème.",

  // Le dépôt GitHub du site, sous la forme "propriétaire/nom" : sert au lien « Code source sur GitHub »
  // en bas de chaque page, et aux liens « Modifier la liste », « Déposer un fichier » et « Mode d'emploi »
  depot: "babash/Babash-NSI-SNT",

  // En bas de chaque page, avec les licences (CC BY-SA 4.0 pour les documents, MIT pour le code).
  // {auteur} est remplacé par le nom ci-dessous. Un texte vide ("") retire la phrase.
  auteur: "Babash - NSI Tani Malandi",
  mention_ia: "Ces ressources sont conçues par {auteur} ; beaucoup le sont avec l'aide de l'IA.",
  reutilisation: "Tu peux les réutiliser et les modifier en mentionnant {auteur} et la licence ; un document modifié se partage sous la même licence.",
  // Une invitation, pas une obligation : la licence CC BY-SA 4.0 ne permet pas d'ajouter de condition.
  invitation_ia: "Si tu utilises l'IA pour les modifier, merci de le préciser.",

  // Le compte commun (pages eleve/ et enseignant/, T101b). Tant que COMPTE_COMMUN_EN_LIGNE vaut false,
  // les deux pages sont en démonstration : données fictives en mémoire, rien n'est envoyé ni gardé.
  // Pour la mise en service (après l'application des SQL 0007 et 0008, validée par l'enseignant) :
  // true, l'adresse du projet Supabase et sa clé publique (« anon » ou « publishable », jamais une autre).
  COMPTE_COMMUN_EN_LIGNE: false,
  compte_commun: {
    url: "",
    cle_publique: "",
  },

  // Les rubriques. Depuis T51b, le site prend la liste et l'ordre des rubriques dans la vitrine
  // (donnees/vitrine.json, réglée dans l'admin) : cette liste n'est plus lue par les pages.
  // Elle reste pour les outils qui la citent encore ; à garder identique à la vitrine.
  rubriques: [
    "snt",
    "nsi-premiere",
    "nsi-terminale",
    "pp",
    "autres",
  ],
});
