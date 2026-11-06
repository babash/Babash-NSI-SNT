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
       annexes: { "Corrigé": "fichiers/corrige.pdf", "Version Capytale": "https://…" },

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
  texte: "Frise interactive de 68 événements, de l'Antiquité à nos jours, filtrable par catégorie (algorithmique, cryptographie, matériel, réseaux…). Chaque événement existe aussi en carte A5 à imprimer, pour construire une fresque en classe.",
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
  lien: "https://github.com/babash/FichesNSI/blob/main/content/chaines-de-caracteres.md",
  texte: "Création, indexation, saisie et traitement, parcours, immuabilité des chaînes.",
  tags: ["À imprimer", "Python"],
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
  lien: "https://github.com/babash/FichesNSI/blob/main/content/tuple.md",
  texte: "Création, indexation, immuabilité, parcours, test d'appartenance et affectation multiple.",
  tags: ["À imprimer", "Python"],
});

groupe("Tableau indexé, tableau donné en compréhension");

ressource({
  titre: "Fiche : les listes en Python",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/liste.md",
  texte: "Création, indexation positive et négative, tranches, modification, parcours et copie d'une liste.",
  tags: ["À imprimer", "Python"],
});

groupe("Dictionnaires par clés et valeurs");

ressource({
  titre: "Fiche : les dictionnaires en Python",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/dict.md",
  texte: "Création, accès, modification, parcours, copie et test de présence d'une clé.",
  tags: ["À imprimer", "Python"],
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
  lien: "https://github.com/babash/TP-commandes-hacker#readme",
  texte: "Quinze missions d'infiltration dans un terminal Linux qui tourne dans le navigateur : se déplacer dans l'arborescence, manipuler des fichiers, gérer les droits, puis arrêter un processus. Correction automatique et indices progressifs. Conçu pour la terminale, il couvre les commandes et les droits du programme de première.",
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
  lien: "https://github.com/babash/FichesNSI/blob/main/content/variable.md",
  texte: "Créer une variable, règles de nommage, types de base, opérateurs arithmétiques, de comparaison et d'affectation combinée.",
  tags: ["À imprimer", "Python"],
});

ressource({
  titre: "Fiche : les structures de contrôle en Python",
  lien: "https://github.com/babash/FichesNSI/blob/main/content/ficheSNT.md",
  texte: "Conditions `if` / `elif` / `else`, boucles `for` et `while`, opérateurs logiques `not`, `and`, `or`.",
  tags: ["À imprimer", "Python"],
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
  lien: "https://github.com/babash/FichesNSI/blob/main/content/fonction-usuelles.md",
  texte: "Calculs sur une liste (maximum, moyenne), recherche d'un élément et filtrage.",
  tags: ["À imprimer", "Python"],
});


theme("Projets", "gris");


theme("Sites ressources", "gris");

ressource({
  titre: "Éduscol : sciences du numérique",
  lien: "https://eduscol.education.gouv.fr/4545/sciences-du-numerique",
  texte: "Les programmes officiels de NSI et de SNT et leurs ressources d'accompagnement.",
});
