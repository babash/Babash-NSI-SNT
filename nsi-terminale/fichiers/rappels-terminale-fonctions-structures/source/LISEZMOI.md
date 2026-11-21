# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-rappels-morpion.tex main-rappels-fonctions.tex` (pdfLaTeX).

Le morpion (T125, nouveau style) : **la page HTML est désormais la référence**, en deux feuilles, `../rappels-morpion/index.html` puis `../rappels-morpion/feuille-2.html` (en ligne, auto-correctives, corrigé compris) ; les réponses sont obtenues par exécution, `../rappels-morpion/source/verifier.py`. Le PDF `../rappels-morpion.pdf` est fait depuis les deux feuilles, d'un seul tenant (`charte/imprimer-td.py`). La source LaTeX `chap-rappels-morpion.tex` reste pour mémoire.

Les fonctions (T125, nouveau style) : **la page HTML est désormais la référence**, en trois feuilles, `../rappels-fonctions/index.html` (lire des fonctions), `../rappels-fonctions/feuille-2.html` (comprendre un algorithme) puis `../rappels-fonctions/feuille-3.html` (écrire des fonctions) ; réponses obtenues par exécution, `../rappels-fonctions/source/verifier.py` ; l'extrait de la bibliothèque « openai » (openai-python 0.x, © OpenAI, licence MIT) est repris tel quel. Le PDF `../rappels-fonctions.pdf` est fait depuis les trois feuilles, d'un seul tenant (`charte/imprimer-td.py`). La source LaTeX `chap-rappels-fonctions.tex` reste pour mémoire.
