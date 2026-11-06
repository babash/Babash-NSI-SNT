/* ═══════════════════════════════════════════════════════════════
   NSI Terminale : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon groupe(…),
   puis changer les valeurs entre guillemets.

     ressource({
       titre: "Nom de la ressource",
       lien: "https://adresse-de-la-ressource",
       texte: "Ce que font les élèves, en une ou deux phrases.",
       tags: ["En ligne"],
     });

   Pour un fichier du site (PDF, fiche…) : le déposer dans le dossier
   nsi-terminale/fichiers, puis écrire  lien: "fichiers/nom-du-fichier.pdf"

   Champs facultatifs : texte, tags, et annexes pour des liens en plus :
       annexes: { "Corrigé": "fichiers/corrige.pdf", "Version Capytale": "https://…" },

   Les thèmes sont les rubriques du programme officiel. La liste
   « programme » de chaque thème reprend la colonne « Contenus » du BO.
   Pour ranger une ressource sous un contenu, écrire groupe("…") avec
   exactement le même intitulé, puis la ressource en dessous.
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "NSI Terminale",
  court: "NSI Tle",
  niveau: "Terminale, spécialité",
  couleur: "orange",
  presentation: "Les six rubriques du programme de terminale, la reprise des notions de première à la rentrée, et la préparation des épreuves du bac.",
  programme: {
    texte: "Programme de NSI de terminale, BO spécial n° 8 du 25 juillet 2019",
    lien: "https://eduscol.education.gouv.fr/4545/sciences-du-numerique",
  },
});


theme("Rentrée : reprendre la première", { court: "Rentrée", couleur: "gris" });

ressource({
  titre: "Expédition Gombessa",
  lien: "https://babash.github.io/Rappel-1er/",
  texte: "Une plongée en Python à la recherche du cœlacanthe, racontée comme un manga, pour réviser les listes, les dictionnaires et les algorithmes de base de première. Parcours principal de 13 missions (environ 1 h 15), puis 5 expéditions bonus. Activités variées, souvent sans coder, et suivi de 7 compétences.",
  tags: ["En ligne", "Python", "Jeu"],
  annexes: {
    "Tableau de bord du professeur": "https://babash.github.io/Rappel-1er/prof.html",
  },
});


theme("Histoire de l'informatique", {
  court: "Histoire",
  programme: ["Événements clés de l'histoire de l'informatique"],
});

groupe("Événements clés de l'histoire de l'informatique");

ressource({
  titre: "Timeline de l'histoire de l'informatique",
  lien: "https://babash.github.io/TimelineNSI/",
  texte: "Frise interactive de 68 événements, de l'Antiquité à nos jours, filtrable par catégorie. Chaque événement existe aussi en carte A5 à imprimer, pour construire une fresque en classe.",
  tags: ["En ligne", "À imprimer"],
  annexes: {
    "Code source et générateur de cartes": "https://github.com/babash/TimelineNSI",
  },
});


theme("Structures de données", {
  programme: [
    "Structures de données, interface et implémentation",
    "Vocabulaire de la programmation objet",
    "Listes, piles, files, dictionnaires",
    "Arbres",
    "Graphes",
  ],
});

groupe("Structures de données, interface et implémentation");

ressource({
  titre: "Chapitre 1 : interface et implémentation",
  lien: "fichiers/chapitre1-interface-et-implementation.pdf",
  texte: "Cours complet du premier chapitre du thème « Structures de données ».",
  tags: ["À imprimer", "Cours"],
  annexes: {
    "Sources LaTeX": "https://github.com/babash/NSI-Terminale/tree/main/Th%C3%A8me%201%20%E2%80%93%20Structures%20de%20donn%C3%A9es",
  },
});

groupe("Vocabulaire de la programmation objet");

ressource({
  titre: "POO, TD 1 : premiers pas en objets",
  lien: "fichiers/td1-poo-premiers-pas.html",
  texte: "Séance de 30 min en cours inversé. Trois encadrés « L'essentiel » (classe et objet, attributs et méthodes, `__init__` et `self`, le point) suivis de quatre exercices courts avec Lovelace, Pascal, Hopper et Turing. 4 pages A4.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "fichiers/td1-poo-premiers-pas.pdf",
  },
});

ressource({
  titre: "POO, TD 2 : vers le bac",
  lien: "fichiers/td2-poo-vers-le-bac.html",
  texte: "TD dirigé type bac : l'ENIAC et la loi de Moore, les microprocesseurs, ARPANET, TCP/IP. Simuler un programme, compléter puis écrire des classes qui interagissent, avec rappels de cours et coups de pouce. 7 pages A4.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "fichiers/td2-poo-vers-le-bac.pdf",
  },
});

ressource({
  titre: "TP de programmation objet : le Pokédex",
  lien: "https://github.com/babash/NSI-Terminale/tree/main/tp-poo-pokemons",
  texte: "Notebook Jupyter : créer une classe `Pokemon`, instancier des pokémons avec leurs attributs et les faire interagir. Les données des pokémons sont fournies en JSON.",
  tags: ["Python", "Notebook"],
  annexes: {
    "Ouvrir le notebook": "https://github.com/babash/NSI-Terminale/blob/main/tp-poo-pokemons/tp-poo-pokemons.ipynb",
  },
});

ressource({
  titre: "Fiche : la programmation orientée objet",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/poo.md",
  texte: "Classe, constructeur, instanciation, attributs, méthodes et rôle de `self`.",
  tags: ["À imprimer", "Python"],
});

groupe("Listes, piles, files, dictionnaires");

ressource({
  titre: "Fiche : piles et files",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/piles-files.md",
  texte: "Pile (LIFO), file (FIFO) et leurs opérations usuelles.",
  tags: ["À imprimer", "Python"],
});

groupe("Arbres");

ressource({
  titre: "Fiche : les arbres",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/arbres.md",
  texte: "Vocabulaire (taille, hauteur…), implémentation d'un arbre binaire, parcours préfixe, infixe, suffixe et en largeur.",
  tags: ["À imprimer", "Python"],
});

groupe("Graphes");

ressource({
  titre: "Fiche : les graphes",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/graphes.md",
  texte: "Vocabulaire, représentations (matrice d'adjacence…), parcours en largeur et en profondeur.",
  tags: ["À imprimer", "Python"],
});


theme("Bases de données", {
  programme: [
    "Modèle relationnel",
    "Base de données relationnelle",
    "Système de gestion de bases de données relationnelles",
    "Langage SQL : requêtes d'interrogation et de mise à jour",
  ],
});

groupe("Langage SQL : requêtes d'interrogation et de mise à jour");

ressource({
  titre: "Fiche : le langage SQL",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/sql.md",
  texte: "Consultation avec `SELECT`, mise à jour avec `INSERT`, `UPDATE` et `DELETE`, agrégation avec `COUNT` et jointures.",
  tags: ["À imprimer", "SQL"],
});


theme("Architectures matérielles, systèmes d'exploitation et réseaux", {
  court: "Architecture, OS et réseaux",
  programme: [
    "Composants intégrés d'un système sur puce",
    "Gestion des processus et des ressources par un système d'exploitation",
    "Protocoles de routage",
    "Sécurisation des communications",
  ],
});

groupe("Gestion des processus et des ressources par un système d'exploitation");

ressource({
  titre: "Système d'exploitation humain",
  lien: "https://github.com/babash/Ex-cution-d-branch-e",
  texte: "Activité débranchée : la classe devient un ordinateur. Chaque élève est un processus, avec un PID et une priorité, qui exécute une fiche d'instructions (prendre, poser, dessiner). Le professeur joue l'ordonnanceur. Trois activités : tourniquet sur un cœur, priorités, puis interblocage.",
  tags: ["Débranché"],
  annexes: {
    "Guide complet de l'activité": "https://github.com/babash/Ex-cution-d-branch-e/blob/main/specifications.txt",
  },
});

ressource({
  titre: "Opération MIRAGE : TP de commandes Linux",
  lien: "https://github.com/babash/TP-commandes-hacker#readme",
  texte: "Quinze missions d'infiltration dans un terminal Linux qui tourne dans le navigateur : arborescence, fichiers, droits, puis repérer un processus espion avec `ps` et l'arrêter avec `kill`. Correction automatique et indices progressifs.",
  tags: ["En ligne", "Rien à installer"],
  annexes: {
    "Fiche élève": "https://babash.github.io/TP-commandes-hacker/fiche_eleve_mirage.html",
    "Fiche professeur": "https://babash.github.io/TP-commandes-hacker/fiche_prof_mirage.html",
    "Terminal JSLinux": "https://bellard.org/jslinux/vm.html?url=alpine-x86.cfg&mem=192",
  },
});


theme("Langages et programmation", {
  court: "Programmation",
  programme: [
    "Notion de programme en tant que donnée, calculabilité, décidabilité",
    "Récursivité",
    "Modularité",
    "Paradigmes de programmation",
    "Mise au point des programmes, gestion des bugs",
  ],
});


theme("Algorithmique", {
  programme: [
    "Algorithmes sur les arbres binaires et les arbres binaires de recherche",
    "Algorithmes sur les graphes",
    "Méthode « diviser pour régner »",
    "Programmation dynamique",
    "Recherche textuelle",
  ],
});


theme("Préparer le bac", "jaune");


theme("Sites ressources", "gris");

ressource({
  titre: "Éduscol : sciences du numérique",
  lien: "https://eduscol.education.gouv.fr/4545/sciences-du-numerique",
  texte: "Les programmes officiels de NSI et de SNT et leurs ressources d'accompagnement.",
});
