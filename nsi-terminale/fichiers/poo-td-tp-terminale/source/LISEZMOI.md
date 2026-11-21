# Sources LaTeX

**TD de POO (T125)** : `main-poo-td.tex` (le TD « Initiation à la POO », 9 exercices, PDF `../poo-td.pdf` gardé tel quel à son adresse) est désormais fondu dans les deux TD en ligne, qui en sont la référence : `../../td1-poo-premiers-pas.html` (+ `-2.html`, exercices 1 à 4) et `../../td2-poo-vers-le-bac.html` (+ `-2.html`, exercices 5 à 9), auto-correctifs, corrigé compris ; leurs PDF sont imprimés depuis ces pages par `charte/imprimer-td.py`. Réponses et tests vérifiés par exécution : `tester-td-poo.py`.

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-poo-td.tex main-poo-bataille.tex main-poo-tp.tex` (pdfLaTeX).

La page HTML est désormais la référence pour l'exercice préparatoire « La classe CarteBataille » (T125) : `../poo-bataille/index.html`. Le PDF `../poo-bataille.pdf` est imprimé depuis cette page par `charte/imprimer-td.py` ; le corrigé est vérifié par `../poo-bataille/source/verifier.py`. La source LaTeX `chap-poo-bataille.tex` reste pour mémoire.
