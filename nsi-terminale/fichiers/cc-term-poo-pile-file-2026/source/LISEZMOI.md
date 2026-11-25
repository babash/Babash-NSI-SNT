# Sources LaTeX

Contrôle de Terminale NSI de novembre 2026 (2 h, 20 points) : POO, pile, file et rappels de 1re, par Babash - NSI Tani Malandi (CC BY-SA 4.0).

## Deux versions
- **La version révisée** (25/11/2026, T142) : `controle.tex` → `../sujet.pdf`, `corrige.tex` → `../corrige.pdf`, `verifier.py`. C'est celle du site, pour les années suivantes. Elle suit la règle des contrôles (`charte/gabarit-controle/LISEZMOI.md`).
- **La version donnée en classe le 25/11/2026** (T130, T130b) : `version-donnee-2026-11-25/` (sources, PDF et script de vérification), gardée telle quelle. L'enseignant l'a jugée trop longue (« beaucoup de fonctions à écrire ») et à questions multiples (« 5 questions en une »).

## Ce qui change dans la version révisée (mêmes notions, mêmes exercices)

| | Version donnée | Version révisée |
|---|---|---|
| Début | POO : lire une classe | **Questions de cours** (4 points) : LIFO, QCM sur `self`, vrai ou faux (`__init__`, attribut, pile, file), relier situations et pile ou file |
| Réponses | sur feuille libre (« Recopier et compléter ») | sur le sujet, place prévue ; codes à trous complétés sur place |
| Questions à tiroirs | 9 (attributs et méthodes, `__init__` et `self`, LIFO et FIFO et laquelle, affichage et justification de chaque ligne, programme et valeur, valeurs de `a` et `c` + dessins + affichage, contenu de `g` + de `f` + explication…) | aucune hors de l'énoncé officiel |
| Fonctions entières | 6 : `duree_totale`, `cout`, `compte_ouvrante`, `compte_fermante`, `bon_compte`, `est_bien_parenthesee` | 2, en fin de sujet, **cadrées** (signature, docstring, exemple dans le cadre) : `compte_ouvrante`, `est_bien_parenthesee` ; `bon_compte` n'a qu'une ligne à écrire ; `duree_totale` devient à compléter ; `cout` devient « corriger la ligne 5 » avec le vrai message `KeyError: 'bananes'` |
| Exercice de bac (24-NSIJ2JA1, exercice 2) | 8 questions, 10 points | questions 1, 2, 4, 5, 6 et 8, 7,5 points ; la question 3 (`compte_fermante`, copie de la question 2) est remplacée par une phrase de l'énoncé ; la question 7 (nombre de comparaisons, ambiguë au point qu'il avait fallu ajouter une précision) est retirée |
| Retirés | « Après des travaux, la capacité passe à 350 » ; « Écrire un programme qui crée la playlist… et l'affiche » ; « Que contient `f` après l'appel ? » (gardé comme explication au corrigé) | |
| Barème | 25 questions, des tiers et des trois-quarts de point cachés dans les parties | 27 réponses, chacune ½, 1, 1½ ou 3 points affichés à côté d'elle ; tableau des points et durées au début |
| Temps estimé (outil / à la main × 3) | 157 min / environ 140 min pour 2 h | 90 min / environ 95 min pour 2 h |
| Pages | 6 (+ copies) | 8 (on répond sur le sujet) ; corrigé 9 |

## D'où vient chaque exercice
- **Exercices 1 à 5** : écrits pour ce contrôle (contextes : la barge, une playlist, un commerçant).
- **Exercice 6** (7,5 points) : exercice 2 du sujet **24-NSIJ2JA1** (baccalauréat NSI 2024, Asie, jour 2 ; parenthèses et pile, 6 points au bac), questions 1, 2, 4, 5, 6 et 8 reprises telles quelles ; une phrase ajoutée à la place de la question 3, marquée « ajoutée au sujet d'origine ». Sujet officiel : https://kxs.fr/files/sujets/2024/ecrit/terminale-2024-asie-jour-2.pdf. Le barème par question est celui de ce contrôle : le sujet officiel ne donne que le total.
- **Corrigé** : rédigé pour ce contrôle ; pour l'exercice 6, comparé au corrigé publié par l'AEIF (Association des enseignantes et enseignants d'informatique de France) : https://aeif.fr/wp-content/uploads/2025/07/corr_Asie_2024_2.pdf.

## Vérifier
- `python3.13 -I verifier.py` (depuis ce dossier) : toutes les réponses du corrigé, ses variantes acceptées et les erreurs fréquentes citées, **exécutées** ; le message d'erreur de la question 13 comparé à celui de Python 3.13 ; les codes à trous du sujet (questions 8, 9, 11 et 18) remplis avec le corrigé, numéros de ligne contrôlés, puis exécutés.
- `python3 -I charte/gabarit-controle/verifier-controle.py --detail nsi-terminale/fichiers/cc-term-poo-pile-file-2026/source/controle.tex` (depuis la racine du dépôt) : questions à tiroirs, fonctions, barème, temps.

Compilation : `pdflatex` deux passes (`\numpages`), classe `exam` et paquets standard de TeX Live (Overleaf). Les demi-points s'écrivent `\half` (`\question[1\half]`) : la classe `exam` de TeX Live 2023 n'affiche pas les points décimaux ni les quarts.
