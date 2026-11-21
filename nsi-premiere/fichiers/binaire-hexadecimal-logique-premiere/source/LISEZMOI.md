# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-b2.tex main-b3.tex main-b-act.tex main-b-ex.tex main-b-conv.tex` (pdfLaTeX).

## Pages en ligne (T125)

- « Exercices de conversions » (`main-b-ex.tex`) : la page HTML `../exercices-conversions/index.html` est désormais la référence : elle se corrige en ligne et s'imprime en PDF (`../exercices-conversions.pdf`, fait par `charte/imprimer-td.py`). Les 24 réponses sont calculées par `corrige-conversions.py` (qui écrit aussi les questions : `--html`).
- « Défi de conversions » (`main-b-conv.tex`) : la page HTML auto-corrective `../defi-conversions/index.html` est désormais la référence ; le PDF `../defi-conversions.pdf` en est l'impression vierge (`charte/imprimer-td.py`). Corrigé calculé par `corrige-defi-conversions.py`.
- « Activités logiques » (`main-b-act.tex`) : la page HTML auto-corrective `../activites-logique/index.html` est désormais la référence ; le PDF `../activites-logique.pdf` en est l'impression vierge. Tables de vérité, énigme de Wason et trajets du robot vérifiés par `corrige-activites-logique.py`.

Corrections (T125b, 21/11) : « Activités logiques » reprend la notation de l'original (∧, ∨, ¬, → ou ⇒, ⇔ ; les mots ET, OU, NON à côté à la première occurrence) et les « connecteurs logiques clés » de l'exercice 3, à l'écran et sur papier.
