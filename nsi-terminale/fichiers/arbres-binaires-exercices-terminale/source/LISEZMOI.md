# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-abr.tex main-arbre.tex` (pdfLaTeX).

## Pages en ligne (T125, lot L7)

Pour les sujets ci-dessous, **la page HTML est désormais la référence** (en ligne, auto-corrective, corrigé compris). Les arbres TikZ y sont redessinés en SVG. Les PDF à la même adresse sont faits depuis les pages (`charte/imprimer-td.py`, feuille vierge). Réponses obtenues par exécution : `source/verifier.py` dans le dossier de chaque page ; les chemins partent de ce dossier `source/`.

- Algorithmes et arbres binaires de recherche : `../abr/index.html` (PDF : `../abr.pdf`).
- Algorithmes des parcours d'arbres binaires : `../arbre/index.html` et `../arbre/feuille-2.html` (deux feuilles, réunies dans un seul PDF : `../arbre.pdf`).

Corrections du contenu d'origine (décisions de l'enseignant du 21/11, vérifiées par exécution dans `../abr/source/verifier.py`) :
- l'arbre d'exemple de l'introduction n'était pas un arbre binaire de recherche (5 dans le sous-arbre droit de 7) : 5 devient 17, enfant droit de 15 ;
- `insertionABRnr` tournait sans fin sur une valeur déjà présente : la boucle a maintenant `elif` et `else: return`.
