/* ═══════════════════════════════════════════════════════════════
   SNT : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon theme(…),
   puis changer les valeurs entre guillemets.

     ressource({
       titre: "Nom de la ressource",
       lien: "https://adresse-de-la-ressource",
       texte: "Ce que font les élèves, en une ou deux phrases.",
       tags: ["En ligne"],
     });

   Pour un fichier du site (PDF, fiche…) : le déposer dans le dossier
   snt/fichiers, puis écrire  lien: "fichiers/nom-du-fichier.pdf"

   Champs facultatifs : texte, tags, et annexes pour des liens en plus :
       annexes: { "Corrigé": "fichiers/corrige.pdf", "Version Capytale": "https://…" },

   Étiquettes déjà utilisées : En ligne, À imprimer, Débranché, Python,
   Connexion ENT, Pour aller plus loin.
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "SNT",
  niveau: "Seconde",
  couleur: "bleu",
  presentation: "Sciences numériques et technologie : les sept thèmes du programme, plus la prise en main de Python et de la bureautique.",
});


theme("Programmation");

ressource({
  titre: "Compute-it, progression Python",
  lien: "https://compute-it.toxicode.fr/?progression=python",
  texte: "Les élèves jouent l'ordinateur : ils lisent un programme Python et l'exécutent eux-mêmes avec les flèches du clavier. On avance des instructions simples jusqu'aux boucles et aux conditions.",
  tags: ["En ligne", "Python"],
});

ressource({
  titre: "Fiche de révision et TD débranché",
  lien: "fichiers/python-compute-it.html",
  texte: "Recto : indentation, `if` / `elif` / `else`, opérateurs logiques, `while` et `for`. Verso : cinq exercices papier dans l'esprit de Compute-it, avec des grilles à suivre case par case. Format A4 recto-verso.",
  tags: ["À imprimer", "Débranché"],
});

ressource({
  // À compléter : préciser ce que font les élèves
  titre: "Activité interactive",
  lien: "https://claude.ai/artifact/3zvYLmqgkXk1T8BxDCs4q8",
  texte: "Activité en ligne pour accompagner la séquence de programmation.",
  tags: ["En ligne"],
});

ressource({
  titre: "Execubot",
  lien: "https://execubot.fr",
  texte: "Jeu de lecture de code : à partir d'un programme Python, les élèves prévoient le déplacement d'un robot sur une grille de couleurs. Conçu par des enseignants d'informatique de lycée.",
  tags: ["En ligne", "Python"],
});

groupe("Pour occuper les plus fort·e·s");

ressource({
  titre: "Algoréa, se préparer au concours",
  lien: "https://algorea.org/#/preparation",
  texte: "Les épreuves d'entraînement du concours Algoréa (France-ioi), au format actuel du concours : des défis d'algorithmique de difficulté croissante.",
  tags: ["En ligne", "Pour aller plus loin"],
});


theme("Internet");


theme("Le Web");


theme("Les réseaux sociaux", { court: "Réseaux sociaux" });


theme("Les données structurées et leur traitement", { court: "Données structurées" });


theme("Localisation, cartographie et mobilité", { court: "Localisation" });


theme("Informatique embarquée et objets connectés", { court: "Objets connectés" });


theme("La photographie numérique", { court: "Photographie numérique", couleur: "jaune" });

ressource({
  // À compléter : préciser ce que font les élèves
  titre: "Notebook Python sur l'image numérique",
  lien: "https://capytale2.ac-paris.fr/p/basthon/n/?kernel=python3-legacy&mode=create&id=8199772&extensions=linenumbers",
  texte: "Activité Python à ouvrir dans Capytale (notebook Basthon).",
  tags: ["Connexion ENT", "Python"],
});


theme("Bureautique", "gris");


theme("Sites ressources", "gris");

ressource({
  titre: "Kit starter SNT, académie d'Aix-Marseille",
  lien: "https://www.pedagogie.ac-aix-marseille.fr/jcms/c_11025463/fr/le-kit-starter-snt-propose-par-l-academie-d-aix-marseille#Id_intro_debranchee",
  texte: "Un kit de démarrage proposé par l'académie, avec notamment des activités d'introduction débranchées.",
});
