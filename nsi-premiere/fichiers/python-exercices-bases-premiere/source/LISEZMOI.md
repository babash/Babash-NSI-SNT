# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-variables.tex main-e-conditions.tex main-e-boucles.tex main-c-exb.tex main-e-fonctions.tex main-fonc-exo.tex` (pdfLaTeX).

## Pages en ligne (T125)

Pour les feuilles « les boucles » et « les conditions », **la page HTML est désormais la référence** :
`exercices-boucles.html` et `exercices-conditions.html` (avec ses feuilles suivantes), auto-correctives en ligne ;
imprimées, elles sont la feuille papier, et leur PDF (`exercices-boucles.pdf`, `exercices-conditions.pdf`) est fait
depuis elles par `charte/imprimer-td.py`. Les sources LaTeX (`chap-e-boucles.tex`, `chap-e-conditions.tex`) restent ici.

Vérifications (à la racine du dépôt) : `nsi-premiere/fichiers/bases-python/source/verifier.py` sur chaque page, puis
`exercices-boucles-calculs.py` et `exercices-conditions-calculs.py` (ce dossier) pour les autres réponses calculées.
