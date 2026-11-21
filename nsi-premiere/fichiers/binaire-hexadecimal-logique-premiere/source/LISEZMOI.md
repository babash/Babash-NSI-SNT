# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-b2.tex main-b3.tex main-b-act.tex main-b-ex.tex main-b-conv.tex` (pdfLaTeX).

## Pages en ligne (T125)

- « Défi de conversions » (`main-b-conv.tex`) : la page HTML auto-corrective `../defi-conversions/index.html` est désormais la référence ; le PDF `../defi-conversions.pdf` en est l'impression vierge (`charte/imprimer-td.py`). Corrigé calculé par `corrige-defi-conversions.py`.
- « Activités logiques » (`main-b-act.tex`) : la page HTML auto-corrective `../activites-logique/index.html` est désormais la référence ; le PDF `../activites-logique.pdf` en est l'impression vierge. Tables de vérité, énigme de Wason et trajets du robot vérifiés par `corrige-activites-logique.py`.
