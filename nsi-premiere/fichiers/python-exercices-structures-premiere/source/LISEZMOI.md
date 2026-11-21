# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-rappel_listes.tex main-e-listes.tex main-e-listes-de-listes.tex main-e-liste-et-dict.tex` (pdfLaTeX).

## « CSV et listes de listes » en ligne (T125)

Pour `main-e-listes-de-listes.tex` (`chap-e-listes-de-listes.tex`), **la page HTML est désormais la référence** : trois feuilles
auto-correctives, `../exercices-csv-listes-de-listes/index.html` (le fichier, comprendre et manipuler), `feuille-2.html`
(filtrer, tranches) et `feuille-3.html` (listes par compréhension). Imprimées, elles sont la feuille papier ; le PDF
`../exercices-csv-listes-de-listes.pdf` (même adresse qu'avant) réunit les trois feuilles vierges, fait par `charte/imprimer-td.py`.

Les données (Insee, réutilisation libre en citant la source) sont le fichier `../exercices-csv-listes-de-listes/comparaisons-communes-mayotte.csv`,
reconstitué à l'identique depuis le `Verbatim` du `.tex`, affiché en entier sur la feuille 1 et téléchargeable. Dans la page, les tests
des questions « Écris le programme » reconstruisent `tab` depuis une chaîne : `csv.reader(io.StringIO(DONNEES))`.
Corrigé vérifié par exécution : `tester-csv-listes-de-listes.py` (ce dossier).
