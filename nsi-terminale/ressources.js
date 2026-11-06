/* ═══════════════════════════════════════════════════════════════
   NSI Terminale : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon theme(…),
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
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "NSI Terminale",
  court: "NSI Tle",
  niveau: "Terminale, spécialité",
  couleur: "orange",
  presentation: "Les thèmes du programme de terminale et la préparation des épreuves du bac.",
});


theme("Histoire de l'informatique", { court: "Histoire" });


theme("Structures de données");

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


theme("Bases de données");


theme("Architectures matérielles, systèmes d'exploitation et réseaux", { court: "Architecture, OS et réseaux" });


theme("Langages et programmation", { court: "Programmation" });


theme("Algorithmique");


theme("Préparer le bac", "jaune");


theme("Sites ressources", "gris");
