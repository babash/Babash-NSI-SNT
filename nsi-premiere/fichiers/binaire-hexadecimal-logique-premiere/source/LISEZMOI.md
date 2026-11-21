# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-b2.tex main-b3.tex main-b-act.tex main-b-ex.tex main-b-conv.tex` (pdfLaTeX).

## Pages en ligne (T125)

Pour `main-b-ex.tex`, la page HTML `../exercices-conversions/index.html` est désormais la référence : elle se corrige en ligne et s'imprime en PDF (`../exercices-conversions.pdf`, fait par `charte/imprimer-td.py`). Les 24 réponses sont calculées par `corrige-conversions.py` (qui écrit aussi les questions : `--html`).
