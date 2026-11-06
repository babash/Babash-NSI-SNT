/* ═══════════════════════════════════════════════════════════════
   Professeur principal : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon theme(…),
   puis changer les valeurs entre guillemets.

     ressource({
       titre: "Nom de la ressource",
       lien: "https://adresse-de-la-ressource",
       texte: "À quoi elle sert, en une ou deux phrases.",
       tags: ["En ligne"],
     });

   Pour un fichier du site (PDF, modèle…) : le déposer dans le dossier
   pp/fichiers, puis écrire  lien: "fichiers/nom-du-fichier.pdf"

   Champs facultatifs : texte, tags, et annexes pour des liens en plus :
       annexes: { "Version modifiable": "fichiers/modele.odt" },

   Les thèmes suivent les missions décrites par la circulaire
   n° 2018-108 du 10 octobre 2018 sur le rôle du professeur principal.
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "Professeur principal",
  court: "PP",
  couleur: "vert",
  presentation: "Les missions du professeur principal au lycée : coordonner l'équipe, suivre chaque élève, accompagner l'orientation, faire le lien avec les familles.",
  programme: {
    texte: "Circulaire n° 2018-108 du 10 octobre 2018, BO n° 37 du 11 octobre 2018",
    lien: "https://www.education.gouv.fr/bo/18/Hebdo33/MENE1823888C.htm",
  },
});


theme("Coordination de l'équipe et conseils de classe", { court: "Conseils de classe" });


theme("Suivi des élèves");

ressource({
  titre: "Simulateur de note au bac général, session 2027",
  lien: "https://babash.github.io/simulateur-bac/",
  texte: "L'élève saisit ses moyennes par semestre et voit ses points, ce qu'il lui reste à obtenir pour le bac et pour chaque mention, et la note nécessaire à l'oral de rattrapage. Coefficients de la session 2027, rien n'est envoyé : les notes restent dans le navigateur.",
  tags: ["En ligne", "Terminale"],
  annexes: {
    "Code source": "https://github.com/babash/simulateur-bac",
  },
});


theme("Orientation", {
  programme: [
    "Seconde : choix des enseignements de spécialité",
    "Première : choix des spécialités et des options",
    "Terminale : Parcoursup",
  ],
});


theme("Lien avec les familles", { court: "Familles" });


theme("Vie de classe");


theme("Textes officiels", "gris");

ressource({
  titre: "Circulaire sur le rôle du professeur principal",
  lien: "https://www.education.gouv.fr/bo/18/Hebdo33/MENE1823888C.htm",
  texte: "Circulaire n° 2018-108 du 10 octobre 2018 : missions du professeur principal au collège et au lycée.",
});
