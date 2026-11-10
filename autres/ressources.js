/* ═══════════════════════════════════════════════════════════════
   Autres ressources : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc et changer les valeurs
   entre guillemets.

     ressource({
       titre: "Nom de la ressource",
       lien: "https://adresse-de-la-ressource",
       texte: "À quoi elle sert, en une ou deux phrases.",
       tags: ["En ligne"],
     });

   Pour un fichier du site (PDF…) : le déposer dans le dossier
   autres/fichiers, puis écrire  lien: "fichiers/nom-du-fichier.pdf"

   Pour ranger par thèmes, ajouter une ligne  theme("Nom du thème");
   avant les ressources concernées.
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "Autres ressources",
  court: "Autres",
  couleur: "jaune",
  presentation: "Les outils de la classe, les concours et de quoi se former : ce qui sert à tous les niveaux.",
});


theme("Outils pour la classe", { court: "Outils" });

ressource({
  titre: "Capytale",
  lien: "https://capytale2.ac-paris.fr/web/my",
  texte: "La plateforme de notebooks Python et d'activités de programmation accessible par l'ENT : l'enseignant·e crée ou copie une activité, la distribue par un code et récupère le travail des élèves.",
  tags: ["Connexion ENT", "Python"],
  annexes: {
    "Wiki Capytale": "https://capytale2.ac-paris.fr/wiki/doku.php?id=start",
    "Bibliothèque partagée entre enseignant·e·s": "https://capytale2.ac-paris.fr/web/bibliotheque_pr",
    "Auto-évaluation des notebooks": "https://capytale.forge.apps.education.fr/basthon/basthon-capytale/parts/auto-evaluation.html",
  },
});

ressource({
  titre: "QCMCam",
  lien: "https://qcmcam.net/",
  texte: "QCM et sondages en classe sans équipement pour les élèves : chaque élève lève un carton imprimé, la webcam ou le smartphone de l'enseignant·e lit toutes les réponses d'un coup.",
  tags: ["En ligne", "À imprimer"],
});

ressource({
  titre: "Bibliothèque de QCM Pronote",
  lien: "https://www.index-education.com/fr/qcm-liste.php",
  texte: "Des QCM partagés par des enseignantes et enseignants, à importer dans Pronote.",
});


theme("Concours et défis", { court: "Concours" });

ressource({
  titre: "Concours Castor informatique",
  lien: "https://concours.castor-informatique.fr/",
  texte: "45 minutes de défis interactifs, sans prérequis en programmation, de la seconde à la terminale. Le concours a lieu chaque année en novembre et décembre, en classe ; la plateforme permet aussi de s'entraîner sur les sujets des années passées.",
  tags: ["En ligne"],
});

ressource({
  titre: "La Nuit du Code",
  lien: "https://www.nuitducode.net/",
  texte: "Un marathon de programmation de six heures en équipe : créer un petit jeu avec Scratch ou Python (Pyxel).",
  tags: ["Python", "Jeu"],
  annexes: {
    "Se préparer avec Pyxel (cahier numérique)": "https://www.cahiernum.net/g=aHR0cHM6Ly8yNGpkcHAuZm9yZ2UuYXBwcy5lZHVjYXRpb24uZnIvam91ci5odG1sP2o9MQ&d=pyxel",
  },
});

ressource({
  titre: "Les Trophées NSI",
  lien: "https://trophees-nsi.fr/",
  texte: "Le concours national de projets des élèves de NSI, en première et en terminale.",
  tags: ["Pour aller plus loin"],
});

ressource({
  titre: "Passe ton hack d'abord",
  lien: "https://www.ac-paris.fr/passe-ton-hack-d-abord-128309",
  texte: "Un concours de cybersécurité en équipe, sous forme de défis à résoudre (« capture the flag »).",
  tags: ["Pour aller plus loin"],
  annexes: {
    "S'entraîner : Challenges Kids": "https://www.challenges-kids.fr/index.php",
    "S'entraîner : Root Me": "https://www.root-me.org/",
  },
});


theme("Se former et échanger", { court: "Se former", couleur: "gris" });

ressource({
  titre: "Portail des formations NSI et SNT",
  lien: "https://mooc-nsi-snt.gitlab.io/portail/0_Accueil.html",
  texte: "Le point d'entrée des MOOC pour se former à l'enseignement de l'informatique au lycée (SNT et NSI).",
});

ressource({
  titre: "Forum des enseignant·e·s NSI",
  lien: "https://mooc-forums.inria.fr/moocnsi/",
  texte: "Le forum de la communauté : questions sur le programme, partage d'activités, entraide.",
});
