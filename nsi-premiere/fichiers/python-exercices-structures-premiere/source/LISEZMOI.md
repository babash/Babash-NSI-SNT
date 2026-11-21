# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-rappel_listes.tex main-e-listes.tex main-e-listes-de-listes.tex main-e-liste-et-dict.tex` (pdfLaTeX).

## Pages en ligne (T125)

Pour `main-e-liste-et-dict.tex`, la page HTML `../exercices-liste-ou-dictionnaire/index.html` est désormais la référence : elle se corrige en ligne et s'imprime en PDF (`../exercices-liste-ou-dictionnaire.pdf`, fait par `charte/imprimer-td.py`). Corrigé exécuté : `corrige-liste-ou-dictionnaire.py`.

Pour `main-e-rappel_listes.tex`, la page HTML `../exercices-listes-fonctions/index.html` est désormais la référence (PDF : `../exercices-listes-fonctions.pdf`). Les corrections, les exemples et les tests de la page sont produits et vérifiés par `corrige-listes-fonctions.py` (`--html` écrit les questions).
