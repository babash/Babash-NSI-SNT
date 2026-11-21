# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-dm-premiers-pas.tex main-dm-boucles-imbriquees.tex main-dm-boucles-while.tex main-dm-DM_noel.tex main-dm-cryptographie.tex` (pdfLaTeX).

## Pages en ligne du lot L3 (T125)

- « Boucle while : la pyramide » (`main-dm-boucles-while.tex`) : la page HTML auto-corrective `../dm-boucles-while-pyramide/index.html` est désormais la référence ; le PDF `../dm-boucles-while-pyramide.pdf` en est l'impression vierge (`charte/imprimer-td.py`). Corrigé calculé par `corrige-dm-boucles-while.py`.
- « DM de Noël » (`main-dm-DM_noel.tex`) : la page HTML auto-corrective `../dm-noel/index.html` est désormais la référence ; le PDF `../dm-noel.pdf` en est l'impression vierge. Corrigé calculé par `corrige-dm-noel.py`.
- « La science du secret et la machine Enigma » (`main-dm-cryptographie.tex`) : deux pages HTML auto-correctives, `../dm-cryptographie/index.html` (feuille 1 : César) et `../dm-cryptographie/feuille-2.html` (feuille 2 : Vigenère et Enigma), sont désormais la référence ; le PDF `../dm-cryptographie.pdf` réunit leurs deux impressions vierges (`charte/imprimer-td.py`, puis `pdfunite`). Corrigé calculé par `corrige-dm-cryptographie.py`.
