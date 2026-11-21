# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-e-variables.tex main-e-conditions.tex main-e-boucles.tex main-c-exb.tex main-e-fonctions.tex main-fonc-exo.tex` (pdfLaTeX).

## Mission « interception des pirates » en ligne (T125)

Pour `main-fonc-exo.tex` (`chap-fonc-exo.tex`), **la page HTML est désormais la référence** : cinq feuilles auto-correctives,
`../mission-fonctions/index.html` puis `feuille-2.html` à `feuille-5.html` (une partie de la mission par feuille, 3 pages A4 chacune).
Imprimées, elles sont la feuille papier ; le PDF `../mission-fonctions.pdf` (même adresse qu'avant) réunit les cinq feuilles vierges,
fait par `charte/imprimer-td.py`. Le corrigé est vérifié par exécution : `tester-mission-fonctions.py` (ce dossier) recalcule
chaque réponse, passe chaque correction de « Écris le programme » dans ses tests, et vérifie que des versions fausses sont refusées.

## Feuilles d'exercices en ligne (T125)

Pour les feuilles « les boucles » et « les conditions », **la page HTML est désormais la référence** :
`exercices-boucles.html` et `exercices-conditions.html` (avec ses feuilles suivantes), auto-correctives en ligne ;
imprimées, elles sont la feuille papier, et leur PDF (`exercices-boucles.pdf`, `exercices-conditions.pdf`) est fait
depuis elles par `charte/imprimer-td.py`. Les sources LaTeX (`chap-e-boucles.tex`, `chap-e-conditions.tex`) restent ici.

Vérifications (à la racine du dépôt) : `nsi-premiere/fichiers/bases-python/source/verifier.py` sur chaque page, puis
`exercices-boucles-calculs.py` et `exercices-conditions-calculs.py` (ce dossier) pour les autres réponses calculées.

Pages en ligne (T125) : pour les feuilles converties au style « Signal pirate », la page HTML est désormais la référence (`exercices-parcours-listes/index.html`, `exercices-variables/index.html`, et `exercices-fonctions/` en trois feuilles : `index.html`, `feuille-2.html`, `feuille-3.html`), et le PDF de même nom (`exercices-parcours-listes.pdf`, `exercices-variables.pdf`, `exercices-fonctions.pdf`, qui réunit les trois feuilles) est imprimé depuis elle avec `charte/imprimer-td.py`. Les valeurs du corrigé sont obtenues par exécution (`corrige-exercices-variables.py`, `corrige-exercices-fonctions.py`) ; les corrections des programmes à écrire sont testées par exécution : `tester-codes.py` (avec `codes-faux-parcours-listes.json` et `codes-faux-fonctions.json`, des programmes faux qui doivent être refusés).

Corrections (T125b, 21/11) : sur ces feuilles, la bonne option d'un choix unique ne se repère plus à sa longueur (distracteurs précisés, chacun avec son retour) ; les variantes papier de « les boucles » citent le bon programme (1, 2, 3) ; la feuille 3 de « les fonctions » a son propre identifiant (`nsi1-exercices-fonctions-3`) ; le papier est resserré (moins de lignes, rappels répétés à l'écran seulement).
