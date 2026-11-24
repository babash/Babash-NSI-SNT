/* ═══════════════════════════════════════════════════════════════
   Réglages généraux du site
   ═══════════════════════════════════════════════════════════════ */

reglages({
  titre: "Ressources NSI et SNT",
  presentation: "Cours, activités et outils pour la classe, rangés par niveau et par thème.",
  // Le bandeau de l'accueil (T126b) : la puce et la ligne au-dessus du titre
  puce: "SNT · NSI",
  sur_titre: "Seconde · Première · Terminale",

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
  // La mention courte de la ligne du pied de page, après « Code source sur GitHub » (décision du 20/11)
  pied_ia: "conçu avec l'aide de l'IA",

  // Le compte commun (pages eleve/ et enseignant/, T101b, T132d ; module assets/compte-commun.js).
  // false : les deux pages sont en démonstration (données fictives en mémoire, rien n'est envoyé ni gardé).
  // true : elles appellent les fonctions commun_… de la base (SQL 0007 v2.3 et 0008, en base depuis le 24/11/2026).
  // La clé est la clé publique (« publishable ») du projet : publique par conception, comme celle du
  // calendrier (calendrier/config.js). Jamais une clé « secret » ou « service_role » : le module la refuse.
  COMPTE_COMMUN_EN_LIGNE: true,
  compte_commun: {
    url: "https://cukahpyqkljiddmimpyi.supabase.co",
    cle_publique: "sb_publishable_dYwCrwaqiDOm8knczJu3Kw_5InHwyPB",
  },
  // Le niveau de l'élève (Seconde · SNT, Première · NSI, Terminale · NSI) : choisi à la création du code,
  // changé ensuite par l'enseignant·e seulement. À mettre à true après l'application de sa migration (T132e).
  COMPTE_COMMUN_NIVEAU: false,
  // Vrai quand au moins une application (QuizzNSI, le calendrier…) lit le compte commun : les pages parlent
  // alors des codes des applications, du lien d'un espace d'application et des crédits qu'elles donnent.
  COMPTE_COMMUN_APPLICATIONS: false,

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
