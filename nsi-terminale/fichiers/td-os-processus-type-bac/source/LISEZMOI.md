# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-td.tex` (pdfLaTeX).

**La page HTML est désormais la référence** (T125, nouveau style) : `../td-os-processus/index.html`, en ligne et auto-corrective, corrigé compris. Les réponses sont obtenues par exécution réelle (bash dans un dossier jetable, `ps -ef | grep` sur un vrai processus, Python 3.13) : `../td-os-processus/source/verifier.py` ; les deux arbres sont dessinés en SVG par `../td-os-processus/source/arbre-svg.py`. Le PDF `../td-os-processus.pdf` est fait depuis la page par `charte/imprimer-td.py`. La source LaTeX `chap-td.tex` reste pour mémoire.
