# Annales du baccalauréat de NSI

Inventaire (tâche T104, 20/11/2026) des sujets de l'épreuve écrite de terminale depuis 2021 et de l'épreuve pratique. **On lie, on n'héberge pas.**

- `annales-bac-nsi.json` : les données. Une entrée par sujet (87 sujets de 2021 à 2026), avec session, centre, jour, code officiel, pages, exercices
  (points, pages, énoncé résumé, notions du thésaurus, thèmes du programme), liens vers le sujet et le corrigé avec leur état et leur date de vérification.
  `epreuve_ecrite.index_par_notion` donne, pour une notion, la liste des exercices (`<id du sujet>#<n° de l'exercice>`) : c'est l'entrée pour construire une feuille « comme au bac ».
- `outils/` : `donnees_brutes.py` (la saisie), `construire_annales.py` (produit le JSON), `verifier_liens.py` (teste les liens).
- `MISE-A-JOUR.md` : la procédure de chaque 1er août et 1er janvier.

Les notions sont celles de `donnees/referentiels/notions.json` ; les thèmes du programme sont `nsi-tle-2019.<thème>`. Ce dossier n'est lu par aucun script du site :
`scripts/valider_donnees.py` ne le contrôle pas.

Points à connaître avant d'imprimer : les pages et les points viennent d'une relecture automatique des PDF (à contrôler sur le PDF) ; la pagination des PDF de l'AEIF
est celle d'une recomposition, pas celle du sujet officiel ; les corrigés de kxs ne sont pas officiels ; seule l'AEIF indique une licence (CC BY-SA 4.0).
