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
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "Professeur principal",
  court: "PP",
  couleur: "vert",
  presentation: "Pour le suivi de la classe : orientation, conseils de classe, vie de classe.",
});


theme("Orientation");


theme("Conseils de classe");


theme("Vie de classe et suivi des élèves", { court: "Vie de classe" });
