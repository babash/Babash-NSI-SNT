# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-variables.tex main-e-conditions.tex main-e-boucles.tex main-c-exb.tex main-e-fonctions.tex main-fonc-exo.tex` (pdfLaTeX).

Pages en ligne (T125) : pour les feuilles converties au style « Signal pirate », la page HTML est désormais la référence (`exercices-parcours-listes/index.html`, `exercices-variables/index.html`), et le PDF de même nom (`exercices-parcours-listes.pdf`, `exercices-variables.pdf`) est imprimé depuis elle avec `charte/imprimer-td.py`. Les valeurs du corrigé sont obtenues par exécution (`corrige-exercices-variables.py`) ; les corrections des programmes à écrire sont testées par exécution : `tester-codes.py` (avec `codes-faux-parcours-listes.json`, des programmes faux qui doivent être refusés).
