# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-tp-boucles.tex main-tp-ramasse-objets.tex` (pdfLaTeX).

## Page en ligne (T125)

- « TP : les boucles (sapin, juste prix, dés bloqués) » (`main-tp-boucles.tex`) : la page HTML auto-corrective `../tp-boucles/index.html` est désormais la référence ; le PDF `../tp-boucles-sapin-juste-prix-des.pdf` en est l'impression vierge (`charte/imprimer-td.py`). En ligne, `input()` et `randint()` sont remplacés par des valeurs fixées ; les corrections sont exécutées par `charte/verifier-td.py` (Python 3.13).
