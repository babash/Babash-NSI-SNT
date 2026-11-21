# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-tp-boucles.tex main-tp-ramasse-objets.tex` (pdfLaTeX).

## Page en ligne (T125)

- « TP : les boucles (sapin, juste prix, dés bloqués) » (`main-tp-boucles.tex`) : la page HTML auto-corrective `../tp-boucles/index.html` est désormais la référence ; le PDF `../tp-boucles-sapin-juste-prix-des.pdf` en est l'impression vierge (`charte/imprimer-td.py`). En ligne, `input()` et `randint()` sont remplacés par des valeurs fixées ; les corrections sont exécutées par `charte/verifier-td.py` (Python 3.13).
- « TP : crée ton jeu Attrape les objets (Pygame) » (`main-tp-ramasse-objets.tex`) : la page HTML auto-corrective `../tp-pygame/index.html` (2 feuilles : `index.html`, `feuille-2.html`) est désormais la référence ; le PDF `../tp-pygame-attrape-objets.pdf` en est l'impression vierge (`charte/imprimer-td.py`). Le programme du jeu, `../tp-pygame/tp-ramasse-objet.py`, est celui de l'archive ; les réponses sont vérifiées par `../tp-pygame/source/verifier-tp-pygame.py` (Python 3.13).
