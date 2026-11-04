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
  presentation: "Ce qui ne rentre dans aucune autre rubrique.",
});
