# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-variables.tex main-e-conditions.tex main-e-boucles.tex main-c-exb.tex main-e-fonctions.tex main-fonc-exo.tex` (pdfLaTeX).

## Mission « interception des pirates » en ligne (T125)

Pour `main-fonc-exo.tex` (`chap-fonc-exo.tex`), **la page HTML est désormais la référence** : cinq feuilles auto-correctives,
`../mission-fonctions/index.html` puis `feuille-2.html` à `feuille-5.html` (une partie de la mission par feuille, 3 pages A4 chacune).
Imprimées, elles sont la feuille papier ; le PDF `../mission-fonctions.pdf` (même adresse qu'avant) réunit les cinq feuilles vierges,
fait par `charte/imprimer-td.py`. Le corrigé est vérifié par exécution : `tester-mission-fonctions.py` (ce dossier) recalcule
chaque réponse, passe chaque correction de « Écris le programme » dans ses tests, et vérifie que des versions fausses sont refusées.
