/* ═══════════════════════════════════════════════════════════════
   NSI Première : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon groupe(…),
   puis changer les valeurs entre guillemets.

     ressource({
       titre: "Nom de la ressource",
       lien: "https://adresse-de-la-ressource",
       texte: "Ce que font les élèves, en une ou deux phrases.",
       tags: ["En ligne"],
     });

   Pour un fichier du site (PDF, fiche…) : le déposer dans le dossier
   nsi-premiere/fichiers, puis écrire  lien: "fichiers/nom-du-fichier.pdf"

   Champs facultatifs : texte, tags, et annexes pour des liens en plus :
       annexes: { "Corrigé": "fichiers/corrige.pdf", "Version Capytale": "https://capytale2.ac-paris.fr/p/basthon/…" },

   Les thèmes sont les rubriques du programme officiel. La liste
   « programme » de chaque thème reprend la colonne « Contenus » du BO.
   Pour ranger une ressource sous un contenu, écrire groupe("…") avec
   exactement le même intitulé, puis la ressource en dessous.
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "NSI Première",
  court: "NSI 1re",
  niveau: "Première, spécialité",
  couleur: "violet",
  presentation: "Numérique et sciences informatiques : les huit rubriques du programme de première, et les projets.",
  programme: {
    texte: "Programme de NSI de première, BO spécial n° 1 du 22 janvier 2019",
    lien: "https://eduscol.education.gouv.fr/4545/sciences-du-numerique",
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
  texte: "Frise interactive de l'histoire de l'informatique, de l'Antiquité à nos jours, filtrable par catégorie (algorithmique, cryptographie, matériel, réseaux…), par période et par date. Chaque événement existe aussi en carte A5 illustrée, à imprimer pour construire une fresque en classe.",
  tags: ["En ligne", "À imprimer"],
  annexes: {
    "Code source et générateur de cartes": "https://github.com/babash/TimelineNSI",
  },
});


theme("Représentation des données : types et valeurs de base", {
  court: "Types de base",
  programme: [
    "Écriture d'un entier positif dans une base b ⩾ 2",
    "Représentation binaire d'un entier relatif",
    "Représentation approximative des nombres réels",
    "Valeurs et opérateurs booléens",
    "Représentation d'un texte en machine",
  ],
});

ressource({
  titre: "Fiche : les chaînes de caractères en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/chaines-de-caracteres/",
  texte: "Création, indexation, saisie et traitement, parcours, immuabilité des chaînes.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/chaines-de-caracteres.pdf",
  },
});

groupe("Écriture d'un entier positif dans une base b ⩾ 2");

ressource({
  titre: "Introduction débranchée au binaire",
  lien: "https://www.pedagogie.ac-aix-marseille.fr/upload/docs/application/pdf/2022-06/ks_intro_binaire_debranche_el.pdf",
  texte: "Fiche élève du kit starter de l'académie d'Aix-Marseille pour découvrir l'écriture binaire sans ordinateur, avant de passer aux conversions.",
  tags: ["Débranché", "À imprimer"],
});


theme("Représentation des données : types construits", {
  court: "Types construits",
  programme: [
    "p-uplets, p-uplets nommés",
    "Tableau indexé, tableau donné en compréhension",
    "Dictionnaires par clés et valeurs",
  ],
});

groupe("p-uplets, p-uplets nommés");

ressource({
  titre: "Fiche : les tuples en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/tuple/",
  texte: "Création, indexation, immuabilité, parcours, test d'appartenance et affectation multiple.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/tuple.pdf",
  },
});

groupe("Tableau indexé, tableau donné en compréhension");

ressource({
  titre: "Fiche : les listes en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/liste/",
  texte: "Création, indexation positive et négative, tranches, modification, parcours et copie d'une liste.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/liste.pdf",
  },
});

groupe("Dictionnaires par clés et valeurs");

ressource({
  titre: "Fiche : les dictionnaires en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/dict/",
  texte: "Création, accès, modification, parcours, copie et test de présence d'une clé.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/dict.pdf",
  },
});


theme("Traitement de données en tables", {
  court: "Données en tables",
  programme: [
    "Indexation de tables",
    "Recherche dans une table",
    "Tri d'une table",
    "Fusion de tables",
  ],
});


theme("Interactions entre l'homme et la machine sur le Web", {
  court: "IHM sur le Web",
  programme: [
    "Modalités de l'interaction entre l'homme et la machine, événements",
    "Interaction avec l'utilisateur dans une page Web",
    "Interaction client-serveur, requêtes HTTP",
    "Formulaire d'une page Web",
  ],
});


theme("Architectures matérielles et systèmes d'exploitation", {
  court: "Architecture et OS",
  programme: [
    "Modèle d'architecture séquentielle (von Neumann)",
    "Transmission de données dans un réseau",
    "Systèmes d'exploitation",
    "Périphériques d'entrée et de sortie",
  ],
});

groupe("Systèmes d'exploitation");

ressource({
  titre: "Opération MIRAGE : TP de commandes Linux",
  lien: "https://babash.github.io/TP-commandes-hacker/fiche_eleve_mirage.html",
  texte: "Quinze missions d'infiltration dans un terminal Linux qui tourne dans le navigateur : se déplacer dans l'arborescence, manipuler des fichiers, gérer les droits, puis arrêter un processus. Correction automatique et indices progressifs. Conçu pour la terminale, il couvre les commandes et les droits du programme de première.",
  tags: ["En ligne", "Rien à installer"],
  annexes: {
    "Fiche professeur": "https://babash.github.io/TP-commandes-hacker/fiche_prof_mirage.html",
    "Terminal JSLinux": "https://bellard.org/jslinux/vm.html?url=alpine-x86.cfg&mem=192",
    "Code source": "https://github.com/babash/TP-commandes-hacker",
  },
});

ressource({
  titre: "Terminus",
  lien: "https://luffah.xyz/bidules/Terminus/",
  texte: "Jeu d'aventure en français dans un faux terminal : pour avancer, on explore le monde avec de vraies commandes (`ls`, `cd`, `cat`, `mv`…). Une bonne entrée en matière avant un TP sur un vrai terminal.",
  tags: ["En ligne", "Jeu", "Rien à installer"],
});

ressource({
  titre: "Apprenez à utiliser la ligne de commande dans un terminal (OpenClassrooms)",
  lien: "https://openclassrooms.com/fr/courses/6173491-apprenez-a-utiliser-la-ligne-de-commande-dans-un-terminal",
  texte: "Cours gratuit en ligne pour apprendre à écrire des commandes et naviguer dans ses fichiers depuis un terminal.",
  tags: ["En ligne", "Pour aller plus loin"],
});


theme("Langages et programmation", {
  court: "Programmation",
  programme: [
    "Constructions élémentaires",
    "Diversité et unité des langages de programmation",
    "Spécification",
    "Mise au point de programmes",
    "Utilisation de bibliothèques",
  ],
});

groupe("Constructions élémentaires");

ressource({
  titre: "Lagon Arena",
  lien: "https://babash.github.io/lagon-arena/",
  texte: "Le chapitre des conditions transformé en tournoi : chaque élève programme le cerveau d'une tortue de mer avec `if`, `elif` et `else`, puis toutes les tortues de la classe s'affrontent dans le même lagon, projeté au tableau. Après le match, l'élève revoit ce que sa tortue a « pensé » tour par tour et la corrige. Gratuit, sans compte, avec un tutoriel de 15 minutes.",
  tags: ["En ligne", "Python", "Jeu"],
  annexes: {
    "Espace enseignant": "https://babash.github.io/lagon-arena/prof.html",
    "Essayer en mode démo": "https://babash.github.io/lagon-arena/prof.html?demo",
  },
});

ressource({
  titre: "Fiche : les variables et opérateurs en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/variable/",
  texte: "Créer une variable, règles de nommage, types de base, opérateurs arithmétiques, de comparaison et d'affectation combinée.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/variable.pdf",
  },
});

ressource({
  titre: "Fiche : les structures de contrôle en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/ficheSNT/",
  texte: "Conditions `if` / `elif` / `else`, boucles `for` et `while`, opérateurs logiques `not`, `and`, `or`.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/ficheSNT.pdf",
  },
});

ressource({
  titre: "Code Puzzle",
  lien: "https://www.codepuzzle.io/",
  texte: "Des puzzles de Parsons : les lignes d'un programme Python sont mélangées, l'élève les remet dans l'ordre et les indente. Le professeur crée ses propres puzzles et défis et les partage par un simple lien.",
  tags: ["En ligne", "Python"],
});

ressource({
  // À compléter : préciser ce que font les élèves
  titre: "Fonctions : un petit tour en Python pour décorer un sapin",
  lien: "https://capytale2.ac-paris.fr/p/basthon/n/?kernel=python3&id=2461019&extensions=admonition,linenumbers,romd",
  texte: "Notebook Capytale pour découvrir les fonctions en dessinant et en décorant un sapin.",
  tags: ["Connexion ENT", "Python"],
});

ressource({
  // À compléter : préciser ce que font les élèves
  titre: "Python : les fonctions",
  lien: "https://capytale2.ac-paris.fr/p/basthon/n/?kernel=python3-old&id=1749716",
  texte: "Notebook Capytale d'exercices sur la définition et l'appel de fonctions.",
  tags: ["Connexion ENT", "Python"],
});


theme("Algorithmique", {
  programme: [
    "Parcours séquentiel d'un tableau",
    "Tris par insertion, par sélection",
    "Algorithme des k plus proches voisins",
    "Recherche dichotomique dans un tableau trié",
    "Algorithmes gloutons",
  ],
});

groupe("Parcours séquentiel d'un tableau");

ressource({
  titre: "Fiche : les algorithmes usuels",
  lien: "https://babash.github.io/FichesNSI/fiches/fonction-usuelles/",
  texte: "Calculs sur une liste (maximum, moyenne), recherche d'un élément et filtrage.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/fonction-usuelles.pdf",
  },
});


theme("Projets", "gris");


theme("Sites ressources", "gris");

ressource({
  titre: "Éduscol : sciences du numérique",
  lien: "https://eduscol.education.gouv.fr/4545/sciences-du-numerique",
  texte: "Les programmes officiels de NSI et de SNT et leurs ressources d'accompagnement.",
  annexes: {
    "Programme de première (PDF)": "https://cache.media.education.gouv.fr/file/SP1-MEN-22-1-2019/26/8/spe633_annexe_1063268.pdf",
  },
});

groupe("Cours en ligne");

ressource({
  titre: "Première NSI, lycée François Mauriac (Bordeaux)",
  lien: "https://glassus.github.io/premiere_nsi/",
  texte: "Le cours complet de première d'un collègue, rangé par thème du programme, avec de nombreux exercices.",
  tags: ["En ligne"],
});

ressource({
  titre: "Première NSI (info-mounier.fr)",
  lien: "https://info-mounier.fr/premiere_nsi/",
  texte: "Cours et activités de première, par chapitre du programme.",
  tags: ["En ligne"],
});

ressource({
  titre: "Informatique au lycée (Pixees)",
  lien: "https://pixees.fr/informatiquelycee/",
  texte: "Cours et activités de SNT, de NSI première et de NSI terminale, hébergés par Pixees.",
  tags: ["En ligne"],
});

groupe("S'entraîner en autonomie");

ressource({
  titre: "CodEx : exercices de Python corrigés en ligne",
  lien: "https://codex.forge.apps.education.fr/",
  texte: "Plusieurs centaines d'exercices de programmation, du plus simple aux sujets d'épreuve pratique, testés automatiquement dans le navigateur. Le site a pris la suite de e-nsi.",
  tags: ["En ligne", "Python"],
});

ressource({
  titre: "futurecoder",
  lien: "https://futurecoder.forge.apps.education.fr/",
  texte: "Cours interactif de Python pour grands débutants, traduit en français : chaque notion se teste aussitôt dans l'éditeur, avec des indices et un assistant de débogage.",
  tags: ["En ligne", "Python"],
});

ressource({
  titre: "HackInScience",
  lien: "https://www.hackinscience.org/exercises/",
  texte: "Exercices de Python corrigés automatiquement, classés par difficulté. Un compte gratuit permet de garder sa progression.",
  tags: ["En ligne", "Python"],
});

ressource({
  titre: "France-IOI : cours et problèmes",
  lien: "https://www.france-ioi.org/algo/chapters.php",
  texte: "Parcours progressif d'algorithmique et de programmation avec correction automatique, jusqu'au niveau des Olympiades.",
  tags: ["En ligne", "Python"],
});

ressource({
  titre: "Python au lycée (Exo7)",
  lien: "https://exo7math.github.io/python1-exo7/livre-python1.pdf",
  texte: "Deux livres gratuits d'Arnaud Bodin : des activités Python progressives, de la mise en route jusqu'aux projets. Les vidéos des cours et des activités sont sur la chaîne YouTube du même nom.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Tome 2": "https://exo7math.github.io/python2-exo7/livre-python2.pdf",
    "Chaîne YouTube « Python au lycée »": "https://www.youtube.com/@Pythonaulycee",
  },
});

ressource({
  titre: "Cours gratuits OpenClassrooms",
  lien: "https://openclassrooms.com/fr/courses/7168871-apprenez-les-bases-du-langage-python",
  texte: "« Apprenez les bases du langage Python » : un cours en libre accès, avec vidéos et quiz, pour revoir les bases en autonomie.",
  tags: ["En ligne", "Python"],
  annexes: {
    "Découvrez le fonctionnement des algorithmes": "https://openclassrooms.com/fr/courses/7527306-decouvrez-le-fonctionnement-des-algorithmes",
  },
});
