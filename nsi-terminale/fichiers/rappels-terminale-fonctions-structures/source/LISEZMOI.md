# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-rappels-morpion.tex main-rappels-fonctions.tex` (pdfLaTeX).

Le morpion (T125, nouveau style) : **la page HTML est désormais la référence**, en deux feuilles, `../rappels-morpion/index.html` puis `../rappels-morpion/feuille-2.html` (en ligne, auto-correctives, corrigé compris) ; les réponses sont obtenues par exécution, `../rappels-morpion/source/verifier.py`. Le PDF `../rappels-morpion.pdf` sera refait depuis les deux feuilles (`charte/imprimer-td.py`, puis les deux PDF l'un après l'autre) quand le moteur connaîtra les questions ouvertes sur papier (`data-type="libre"`) ; d'ici là, c'est l'ancien PDF. La source LaTeX `chap-rappels-morpion.tex` reste pour mémoire.
