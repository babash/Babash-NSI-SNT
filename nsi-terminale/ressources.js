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


theme("Bases de données");


theme("Architectures matérielles, systèmes d'exploitation et réseaux", { court: "Architecture, OS et réseaux" });


theme("Langages et programmation", { court: "Programmation" });


theme("Algorithmique");


theme("Préparer le bac", "jaune");


theme("Sites ressources", "gris");
