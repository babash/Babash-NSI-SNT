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
       annexes: { "Corrigé": "fichiers/corrige.pdf", "Version Capytale": "https://capytale2.ac-paris.fr/p/basthon/…" },

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
  lien: "https://nbviewer.org/github/babash/NSI-Terminale/blob/main/tp-poo-pokemons/tp-poo-pokemons.ipynb",
  texte: "Notebook Jupyter : créer une classe `Pokemon`, instancier des pokémons avec leurs attributs et les faire interagir. Les données des pokémons sont fournies en JSON.",
  tags: ["Python", "Notebook"],
  annexes: {
    "Notebook à télécharger (.ipynb)": "https://raw.githubusercontent.com/babash/NSI-Terminale/main/tp-poo-pokemons/tp-poo-pokemons.ipynb",
    "Données des pokémons (JSON)": "https://raw.githubusercontent.com/babash/NSI-Terminale/main/tp-poo-pokemons/pokemon_data_light.json",
    "Code source": "https://github.com/babash/NSI-Terminale/tree/main/tp-poo-pokemons",
  },
});

ressource({
  titre: "Fiche : la programmation orientée objet",
  lien: "https://babash.github.io/FichesNSI/fiches/poo/",
  texte: "Classe, constructeur, instanciation, attributs, méthodes et rôle de `self`.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/poo.pdf",
  },
});

ressource({
  titre: "Programmation orientée objet, cours en ligne (pgdg.frama.io)",
  lien: "https://pgdg.frama.io/tnsi/s_donnees/poo/",
  texte: "Un cours de terminale sur la POO, avec des exercices progressifs.",
  tags: ["En ligne", "Python"],
});

groupe("Listes, piles, files, dictionnaires");

ressource({
  titre: "Fiche : piles et files",
  lien: "https://babash.github.io/FichesNSI/fiches/piles-files/",
  texte: "Pile (LIFO), file (FIFO) et leurs opérations usuelles.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/piles-files.pdf",
  },
});

ressource({
  titre: "TP : une file avec deux piles (CodEx)",
  lien: "https://codex.forge.apps.education.fr/en_travaux/file_deux_piles/",
  texte: "Implémenter une file à l'aide de deux piles, avec des tests automatiques dans le navigateur.",
  tags: ["En ligne", "Python"],
});

ressource({
  titre: "Quiz piles et files (lyceum.fr)",
  lien: "https://www.lyceum.fr/tg/nsi/1-structures-de-donnees/3-structures-lineaires-piles-files/quiz/",
  texte: "Un QCM en ligne pour vérifier les notions de pile et de file.",
  tags: ["En ligne"],
  annexes: {
    "Version Quizizz (compte enseignant)": "https://quizizz.com/admin/quiz/6383e4a28ed520001dba57a9/pile-et-file",
  },
});

groupe("Arbres");

ressource({
  titre: "Fiche : les arbres",
  lien: "https://babash.github.io/FichesNSI/fiches/arbres/",
  texte: "Vocabulaire (taille, hauteur…), implémentation d'un arbre binaire, parcours préfixe, infixe, suffixe et en largeur.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/arbres.pdf",
  },
});

groupe("Graphes");

ressource({
  titre: "Fiche : les graphes",
  lien: "https://babash.github.io/FichesNSI/fiches/graphes/",
  texte: "Vocabulaire, représentations (matrice d'adjacence…), parcours en largeur et en profondeur.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/graphes.pdf",
  },
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
  titre: "CyberCase : apprendre SQL en menant l'enquête",
  lien: "https://exomorphisme.fr/cybercase/",
  texte: "Une photo truquée circule sur le réseau social du lycée. Pour remonter jusqu'au commanditaire, l'élève n'a qu'un outil : des requêtes SQL sur la base du réseau. Huit affaires, déverrouillées au fil de l'XP (recrue, analyste, expert), mènent du simple `SELECT` à la sous-requête en passant par `WHERE`, `AND` / `OR`, `DISTINCT`, `COUNT`, `LIKE` et `ORDER BY`. Le Journal du détective tient lieu de cours entre deux enquêtes.\n**Terminale NSI, 1 h 30, en ligne, sans installation.** Deux suites dans le même univers : CounterCase pour `UPDATE`, `INSERT` et `DELETE`, et CrossCase pour les jointures.\nComptes élèves sur demande : aucun nom ne quitte le lycée et l'avancement est conservé d'une séance à l'autre. D'après une idée de Marion Dufour ; moteur dérivé de SQL Noir de Hristo Bogoev (licence MIT).",
  tags: ["Ressource du mois", "En ligne", "SQL", "Jeu"],
});

ressource({
  titre: "The SQL Murder Mystery",
  lien: "https://mystery.knightlab.com/",
  texte: "Une enquête policière en anglais à résoudre en interrogeant une base de données en SQL, directement dans le navigateur. Une bonne suite à CyberCase pour les plus rapides.",
  tags: ["En ligne", "SQL", "Pour aller plus loin"],
});

ressource({
  titre: "Requêtez une base de données avec SQL (OpenClassrooms)",
  lien: "https://openclassrooms.com/fr/courses/7818671-requetez-une-base-de-donnees-avec-sql",
  texte: "Cours gratuit en ligne : modèle relationnel et requêtes SQL, pour revoir les bases en autonomie.",
  tags: ["En ligne", "SQL"],
});

ressource({
  titre: "Fiche : le langage SQL",
  lien: "https://babash.github.io/FichesNSI/fiches/sql/",
  texte: "Consultation avec `SELECT`, mise à jour avec `INSERT`, `UPDATE` et `DELETE`, agrégation avec `COUNT` et jointures.",
  tags: ["À imprimer", "SQL"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/sql.pdf",
  },
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
  lien: "fichiers/os-humain/diaporama.html",
  texte: "Activité débranchée : la classe devient un ordinateur. Chaque élève est un processus, avec un PID et une priorité, qui exécute une fiche d'instructions (prendre, poser, dessiner). Le professeur joue l'ordonnanceur. Trois activités : tourniquet sur un cœur, priorités, puis interblocage. Le lien ouvre le diaporama à projeter ; les fiches processus à imprimer sont en dessous.",
  tags: ["Débranché", "À imprimer"],
  annexes: {
    "Guide de l'activité": "fichiers/os-humain/guide.html",
    "Fiches processus, activité 1": "fichiers/os-humain/fiches-activite-1.pdf",
    "Fiches processus, activité 2": "fichiers/os-humain/fiches-activite-2.pdf",
    "Fiches processus, activité 3": "fichiers/os-humain/fiches-activite-3.pdf",
    "Code source": "https://github.com/babash/Ex-cution-d-branch-e",
  },
});

ressource({
  titre: "Opération MIRAGE : TP de commandes Linux",
  lien: "https://babash.github.io/TP-commandes-hacker/fiche_eleve_mirage.html",
  texte: "Quinze missions d'infiltration dans un terminal Linux qui tourne dans le navigateur : arborescence, fichiers, droits, puis repérer un processus espion avec `ps` et l'arrêter avec `kill`. Correction automatique et indices progressifs.",
  tags: ["En ligne", "Rien à installer"],
  annexes: {
    "Fiche professeur": "https://babash.github.io/TP-commandes-hacker/fiche_prof_mirage.html",
    "Terminal JSLinux": "https://bellard.org/jslinux/vm.html?url=alpine-x86.cfg&mem=192",
    "Code source": "https://github.com/babash/TP-commandes-hacker",
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

groupe("Algorithmes sur les arbres binaires et les arbres binaires de recherche");

ressource({
  titre: "Visualiser un arbre binaire de recherche",
  lien: "https://www.cs.usfca.edu/~galles/visualization/BST.html",
  texte: "Animation pas à pas de l'insertion, de la recherche et de la suppression dans un ABR (université de San Francisco). Pratique au tableau pour dérouler un algorithme.",
  tags: ["En ligne"],
  annexes: {
    "VisuAlgo, autre visualisation": "https://visualgo.net/en/bst",
  },
});


theme("Préparer le bac", "jaune");

groupe("Épreuve écrite");

ressource({
  titre: "Sujets de l'écrit de NSI (kxs.fr)",
  lien: "https://kxs.fr/sujets/terminale-ecrit",
  texte: "Les sujets de l'épreuve écrite de terminale, session par session.",
  tags: ["En ligne", "À imprimer"],
});

ressource({
  titre: "Sujets du bac 2023 en LaTeX (eval-nsi)",
  lien: "https://jcottin.forge.apps.education.fr/eval-nsi/nsi23_tex/nsi23_tex/",
  texte: "Les sujets de 2023 retranscrits en LaTeX : pratique pour reprendre un exercice dans un devoir.",
  tags: ["À adapter"],
});

ressource({
  titre: "Sujets 2025 (AEIF)",
  lien: "https://aeif.fr/index.php/annee-2025/",
  texte: "Les sujets de la session 2025 rassemblés par l'Association des enseignantes et enseignants d'informatique de France.",
  tags: ["À imprimer"],
});

groupe("Épreuve pratique");

ressource({
  titre: "Banque de sujets de l'épreuve pratique (ECEBac)",
  lien: "https://ecebac.fr/listaca.php?mat=94",
  texte: "Les sujets de l'épreuve pratique de NSI de la session 2025, sujet par sujet.",
  tags: ["En ligne", "Python"],
});

groupe("Grand oral");

ressource({
  titre: "Présentation du Grand oral (Éduscol)",
  lien: "https://eduscol.education.fr/729/presentation-du-grand-oral",
  texte: "Le déroulement de l'épreuve, la grille d'évaluation indicative et les ressources officielles pour s'y préparer.",
});

ressource({
  titre: "10 exercices pour améliorer sa prise de parole (France Travail)",
  lien: "https://www.francetravail.fr/candidat/vos-recherches/preparer-votre-candidature/entretien/10-exercices-pour-ameliorer-votr.html",
  texte: "Respiration, voix, posture, débit : des exercices simples à faire en classe ou à la maison avant l'oral.",
});


theme("Sites ressources", "gris");

ressource({
  titre: "Éduscol : sciences du numérique",
  lien: "https://eduscol.education.gouv.fr/4545/sciences-du-numerique",
  texte: "Les programmes officiels de NSI et de SNT et leurs ressources d'accompagnement.",
  annexes: {
    "Programme de terminale (PDF)": "https://cache.media.education.gouv.fr/file/SPE8_MENJ_25_7_2019/93/3/spe247_annexe_1158933.pdf",
  },
});

ressource({
  titre: "NSI Terminale (jerome.courtois2.free.fr)",
  lien: "http://jerome.courtois2.free.fr/NSI_Terminale.html",
  texte: "Cours et activités de terminale NSI d'un collègue, par thème.",
  tags: ["En ligne"],
});

ressource({
  titre: "NSI Terminale (nsi.ymougenel.com)",
  lien: "http://nsi.ymougenel.com/nsi_term",
  texte: "Cours et exercices de terminale NSI, par chapitre.",
  tags: ["En ligne"],
});

ressource({
  titre: "CodEx : exercices de Python corrigés en ligne",
  lien: "https://codex.forge.apps.education.fr/",
  texte: "Plusieurs centaines d'exercices testés automatiquement, dont beaucoup au niveau de l'épreuve pratique.",
  tags: ["En ligne", "Python"],
});
