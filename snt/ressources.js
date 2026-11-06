/* ═══════════════════════════════════════════════════════════════
   SNT : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon theme(…) ou
   groupe(…), puis changer les valeurs entre guillemets.

     ressource({
       titre: "Nom de la ressource",
       lien: "https://adresse-de-la-ressource",
       texte: "Ce que font les élèves, en une ou deux phrases.",
       tags: ["En ligne"],
     });

   Pour un fichier du site (PDF, fiche…) : le déposer dans le dossier
   snt/fichiers, puis écrire  lien: "fichiers/nom-du-fichier.pdf"

   Champs facultatifs : texte, tags, et annexes pour des liens en plus :
       annexes: { "Corrigé": "fichiers/corrige.pdf", "Version Capytale": "https://capytale2.ac-paris.fr/p/basthon/…" },

   Les thèmes suivent le programme officiel. La liste « programme »
   d'un thème reprend la colonne « Contenus » du BO : une ressource
   placée sous groupe("…") avec le même intitulé y est reliée.

   Étiquettes déjà utilisées : En ligne, À imprimer, Débranché, Python,
   Connexion ENT, Pour aller plus loin, À adapter.
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "SNT",
  niveau: "Seconde",
  couleur: "bleu",
  presentation: "Sciences numériques et technologie : les sept thèmes du programme et les notions transversales de programmation en Python. Une révision du programme, avec une place pour l'intelligence artificielle, est annoncée pour la rentrée 2027.",
  programme: {
    texte: "Programme de SNT, BO spécial n° 1 du 22 janvier 2019",
    lien: "https://eduscol.education.gouv.fr/5841/programmes-et-ressources-en-sciences-numeriques-et-technologie-voie-gt",
  },
});


theme("Première séance", { couleur: "gris" });

ressource({
  titre: "SNT 1er jour : brise-glace et découverte",
  lien: "https://babash.github.io/SNT-1er-Jour/",
  texte: "Formulaire de première séance : les élèves se présentent (mots-clés, goûts culturels, citation d'informaticien, question au professeur) et voient le nuage de mots de leur classe se construire. Jeu de frappe au clavier en bonus pour ceux qui finissent en avance.\n**À adapter** : la page est réglée pour les classes 209 à 212 et envoie les réponses dans la base de données de son auteur. La dupliquer et la brancher sur sa propre base avant de l'utiliser.",
  tags: ["En ligne", "À adapter"],
  annexes: {
    "Code source, à dupliquer": "https://github.com/babash/SNT-1er-Jour",
  },
});


theme("Notions transversales de programmation", {
  court: "Programmation",
  programme: [
    "Affectations, variables",
    "Séquences",
    "Instructions conditionnelles",
    "Boucles bornées et non bornées",
    "Définitions et appels de fonctions",
  ],
});

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

ressource({
  titre: "Pyrates",
  lien: "https://py-rates.fr/",
  texte: "Jeu de plateforme : on guide un pirate jusqu'au trésor en écrivant de vrais programmes Python. Les niveaux introduisent pas à pas les déplacements, les variables, les boucles et les conditions. Issu d'une thèse en didactique de l'informatique, il assure la transition des blocs (Scratch) vers le texte.",
  tags: ["En ligne", "Python", "Jeu"],
  annexes: {
    "Guide pédagogique": "https://py-rates.fr/guide/FR/index.html",
  },
});

ressource({
  titre: "SNT, programmation Python (info-mounier.fr)",
  lien: "https://info-mounier.fr/snt/python/",
  texte: "Cours de Python pour la seconde, chapitre par chapitre, avec des exercices pour s'entraîner.",
  tags: ["En ligne", "Python"],
});

groupe("Affectations, variables");

ressource({
  titre: "Fiche : les variables et opérateurs en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/variable/",
  texte: "Créer une variable, règles de nommage, types de base, opérateurs arithmétiques, de comparaison et d'affectation combinée.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/variable.pdf",
  },
});

groupe("Instructions conditionnelles");

ressource({
  titre: "Fiche : les structures de contrôle en Python",
  lien: "https://babash.github.io/FichesNSI/fiches/ficheSNT/",
  texte: "Conditions `if` / `elif` / `else`, boucles `for` et `while`, opérateurs logiques `not`, `and`, `or`, avec des exemples commentés.",
  tags: ["À imprimer", "Python"],
  annexes: {
    "Version PDF": "https://babash.github.io/FichesNSI/fiches/ficheSNT.pdf",
  },
});

groupe("Pour occuper les plus fort·e·s");

ressource({
  titre: "Algoréa, se préparer au concours",
  lien: "https://algorea.org/#/preparation",
  texte: "Les épreuves d'entraînement du concours Algoréa (France-ioi), au format actuel du concours : des défis d'algorithmique de difficulté croissante.",
  tags: ["En ligne", "Pour aller plus loin"],
});

ressource({
  titre: "Défis Python du lycée en Forêt",
  lien: "https://www.lycee-en-foret.fr/defis-python/",
  texte: "Une série de défis de programmation Python, proposée par le lycée en Forêt de Montargis, à résoudre en autonomie.",
  tags: ["En ligne", "Python", "Pour aller plus loin"],
});


theme("Internet");


theme("Le Web");


theme("Les réseaux sociaux", { court: "Réseaux sociaux" });


theme("Les données structurées et leur traitement", { court: "Données structurées" });

ressource({
  titre: "CyberCase : apprendre SQL en menant l'enquête",
  lien: "https://exomorphisme.fr/cybercase/",
  texte: "Une photo truquée circule sur le réseau social du lycée. Pour remonter jusqu'au commanditaire, l'élève interroge la base de données du réseau avec des requêtes SQL : il sélectionne, filtre, compte et trie des données structurées pour faire avancer l'enquête. Huit affaires, déverrouillées au fil de l'XP (recrue, analyste, expert), vont du simple `SELECT` à la sous-requête ; le Journal du détective tient lieu de cours.\n**En ligne, sans installation, environ 1 h 30.** Conçue pour la terminale NSI : en seconde, les premières affaires (`SELECT`, `WHERE`, `ORDER BY`, `COUNT`) suffisent pour le thème des données structurées.\nComptes élèves sur demande : aucun nom ne quitte le lycée et l'avancement est conservé d'une séance à l'autre. D'après une idée de Marion Dufour ; moteur dérivé de SQL Noir de Hristo Bogoev (licence MIT).",
  tags: ["Ressource du mois", "En ligne", "Jeu"],
});


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

ressource({
  titre: "Faites vos premiers pas sur ordinateur (OpenClassrooms)",
  lien: "https://openclassrooms.com/fr/courses/5737801-faites-vos-premiers-pas-sur-ordinateur",
  texte: "Cours gratuit de 6 h, niveau facile : utiliser le clavier et la souris, se repérer sur le bureau, ranger ses fichiers, créer un premier document. Une vidéo et un quiz par partie. Utile pour les élèves peu à l'aise avec l'ordinateur.",
  tags: ["En ligne"],
});


theme("Sites ressources", "gris");

ressource({
  titre: "Éduscol : programme et ressources de SNT",
  lien: "https://eduscol.education.gouv.fr/5841/programmes-et-ressources-en-sciences-numeriques-et-technologie-voie-gt",
  texte: "Le programme officiel et les ressources d'accompagnement de chaque thème.",
});

ressource({
  titre: "Kit starter SNT, académie d'Aix-Marseille",
  lien: "https://www.pedagogie.ac-aix-marseille.fr/jcms/c_11025463/fr/le-kit-starter-snt-propose-par-l-academie-d-aix-marseille#Id_intro_debranchee",
  texte: "Un kit de démarrage proposé par l'académie, avec notamment des activités d'introduction débranchées.",
});

groupe("Informatique sans ordinateur");

ressource({
  titre: "Activités de médiation de Marie Duflot-Kremer",
  lien: "https://members.loria.fr/MDuflot/files/med/index.html",
  texte: "Des activités débranchées décrites pas à pas par une enseignante-chercheuse de l'université de Lorraine, dont le « crêpier psychorigide » pour aborder les algorithmes de tri.",
  tags: ["Débranché"],
  annexes: {
    "Les vidéos « Comprendre l'informatique en jouant »": "https://www.youtube.com/playlist?list=PLWvGMqXvyJAPSMFgCiy6qVHW9bAPu93X5",
  },
});

ressource({
  titre: "L'informatique sans ordinateur (CS Unplugged)",
  lien: "https://interstices.info/app/uploads/2018/01/csunplugged2014-fr-comp.pdf",
  texte: "La traduction française du livre « Computer Science Unplugged », coordonnée par Interstices (Inria) : une vingtaine d'activités avec cartes, ficelle et crayons pour découvrir le binaire, la compression, la détection d'erreurs, les tris ou les graphes.",
  tags: ["Débranché", "À imprimer"],
});

ressource({
  titre: "Activités débranchées de Pixees",
  lien: "https://pixees.fr/category/support-pedagogique/activite/activite-debranchee/",
  texte: "Les fiches d'activités débranchées recensées par Pixees (Inria), dont le classique « robot idiot » pour introduire la notion d'algorithme.",
  tags: ["Débranché"],
});

groupe("Vulgarisation");

ressource({
  titre: "TensorFlow Playground",
  lien: "https://playground.tensorflow.org/",
  texte: "Un petit réseau de neurones qui apprend sous les yeux des élèves : on change le nombre de couches et de neurones, on lance l'apprentissage et on voit la frontière de décision se dessiner. Pour montrer ce qu'est l'apprentissage profond sans une ligne de code.",
  tags: ["En ligne"],
});

ressource({
  titre: "Les explorables de Nicky Case",
  lien: "https://ncase.me/",
  texte: "Des jeux-explications interactifs (en anglais, certains traduits) sur la confiance, les préjugés ou les épidémies : de bons supports pour le thème des réseaux sociaux.",
  tags: ["En ligne"],
});
