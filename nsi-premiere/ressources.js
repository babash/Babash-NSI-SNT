/* ═══════════════════════════════════════════════════════════════
   NSI Première : la liste des ressources de la page

   AJOUTER UNE RESSOURCE : copier ce bloc sous le bon theme(…),
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
   ═══════════════════════════════════════════════════════════════ */

rubrique({
  nom: "NSI Première",
  court: "NSI 1re",
  niveau: "Première, spécialité",
  couleur: "violet",
  presentation: "Numérique et sciences informatiques : les thèmes du programme de première, et les projets.",
});


theme("Histoire de l'informatique", { court: "Histoire" });


theme("Représentation des données : types et valeurs de base", { court: "Types de base" });


theme("Représentation des données : types construits", { court: "Types construits" });


theme("Traitement de données en tables", { court: "Données en tables" });


theme("Interactions entre l'homme et la machine sur le Web", { court: "IHM sur le Web" });


theme("Architectures matérielles et systèmes d'exploitation", { court: "Architecture et OS" });


theme("Langages et programmation", { court: "Programmation" });


theme("Algorithmique");


theme("Projets", "gris");


theme("Sites ressources", "gris");
