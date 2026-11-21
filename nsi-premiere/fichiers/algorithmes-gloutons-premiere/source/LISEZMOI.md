# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-sac-a-dos.tex main-e-gloutonneries.tex main-e-tuple-et-voyageur-de-commerce.tex` (pdfLaTeX).

## Pages en ligne (T125)

Les pages HTML sont désormais la référence ; elles se corrigent en ligne et s'impriment en PDF (fait par `charte/imprimer-td.py`, à la même adresse que l'ancien PDF) :
- `main-e-gloutonneries.tex` : `../casse-du-siecle/index.html` (PDF `../casse-du-siecle.pdf`), corrigé calculé par `corrige-casse-du-siecle.py`.
- `main-e-sac-a-dos.tex` : deux feuilles, `../golden-sac/index.html` et `../golden-sac/feuille-2.html` ; le PDF `../golden-sac.pdf` réunit les deux feuilles (4 + 4 pages). Corrigé calculé par `corrige-golden-sac.py`.
- `main-e-tuple-et-voyageur-de-commerce.tex` : deux feuilles, `../odyssee-du-livreur/index.html` (les tuples) et `../odyssee-du-livreur/feuille-2.html` (le défi du drone) ; le PDF `../odyssee-du-livreur.pdf` réunit les deux feuilles. Corrigé calculé par `corrige-odyssee-du-livreur.py`. Correction : dans l'analyse de la tournée, Mzouazia est remplacée par Choungui (avec Mzouazia, le glouton était déjà le meilleur trajet et le « défi » n'avait pas de réponse).

Corrections T125b (21/11) : la question 12 de la feuille 1 n'accepte plus `20 in data == True` (comparaison enchaînée, `20 in data and data == True`, qui vaut `False` : vérifié dans `corrige-odyssee-du-livreur.py`) ; un retour explique le piège. Les choix uniques ne trahissent plus la bonne réponse par leur longueur (`qcu_forme.py`). Moins de papier : sur la feuille 2, les questions 5 à 7, puis 9 et 10, s'impriment en tableau comme dans l'original ; l'Odyssée tient en 5 pages (6 avant, 4 pour l'original).
