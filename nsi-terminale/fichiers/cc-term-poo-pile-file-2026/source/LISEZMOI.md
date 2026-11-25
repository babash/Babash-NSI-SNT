# Sources LaTeX

Contrôle de Terminale NSI de novembre 2026 (2 h, 20 points) : POO, pile, file et rappels de 1re, par Babash - NSI Tani Malandi (CC BY-SA 4.0).

## Deux versions
- **La version du site** (révisée le 25/11/2026, T142, puis corrigée après la relecture du ou de la Critique, T158) : `controle.tex` → `../sujet.pdf`, `corrige.tex` → `../corrige.pdf`, `verifier.py`. Elle sert pour les années suivantes et suit la règle des contrôles (`charte/gabarit-controle/LISEZMOI.md`).
- **La version donnée en classe le 25/11/2026** (T130, T130b) : `version-donnee-2026-11-25/` (sources, PDF et script de vérification), gardée telle quelle. L'enseignant l'a jugée trop longue (« beaucoup de fonctions à écrire ») et à questions multiples (« 5 questions en une »).

## Forme : « mode bac », sur copie
C'est un gros contrôle de terminale : sujet court, réponses sur copie, comme à l'épreuve (choix de l'enseignant du 25/11, G35 et G41). Le QCM, les vrai ou faux et l'association se répondent par lettres ; les codes à trous se complètent en écrivant sur la copie les seules lignes complétées ; la pile se dessine sur la copie, l'orientation étant dite dans la consigne. 10 points de questions type TD (dont 4 de cours), puis 10 points d'exercice de bac (Tle-2).

## Ce qui change par rapport à la version donnée (mêmes notions)

| | Version donnée | Version du site |
|---|---|---|
| Début | POO : lire une classe | **Questions de cours** (4 points) : LIFO, QCM sur `self`, quatre vrai ou faux sur des savoirs différents, associer situations et pile ou file |
| Questions à tiroirs | 9 | aucune hors de l'énoncé officiel |
| Fonctions entières | 6 : `duree_totale`, `cout`, `compte_ouvrante`, `compte_fermante`, `bon_compte`, `est_bien_parenthesee` | 2, en fin de sujet, **avec leur en-tête donné** (signature, docstring, exemple) : `compte_ouvrante`, `est_bien_parenthesee` ; `bon_compte` n'a qu'une ligne à écrire |
| Exercice « playlist » | 2 points (une méthode à écrire) | **retiré** : ses deux gestes (`append` sur un attribut, accumulateur) sont notés dans l'exercice de bac (un savoir, une fois) |
| Dictionnaire | affichage + fonction `cout` à écrire | « trouver l'erreur » : la ligne 5 corrigée et une phrase d'explication, ½ + ½, avec le vrai message `KeyError: 'bananes'` |
| Pile et file | dessins de `p` et `f`, valeurs de `a` et `c`, affichage, en tiroirs | la pile dessinée sur la copie, l'affichage, les lignes de `inverser`, et « que contient `f` après l'appel ? » |
| Exercice de bac (24-NSIJ2JA1, exercice 2) | 8 questions, 10 points | 6 questions, **10 points** : la question 3 (`compte_fermante`, copie de la question 2) est remplacée par une phrase de l'énoncé ; la question 7 (nombre de comparaisons, ambiguë) est retirée ; l'adaptation est dite en tête du sujet |
| Barème | des tiers et des trois-quarts de point cachés | points entiers ou demi-points à côté de chaque question, total 20 (vérifié par `verifier.py`) ; le corrigé dit qu'une fonction juste a tous ses points et qu'une erreur de syntaxe mineure coûte peu ou rien |
| Temps | outil 160 min, à la main environ 140 min pour 2 h | outil 80 min, à la main environ 90 min (copie comprise) |
| Pages | sujet 6, corrigé 9 | sujet 6, corrigé 8 |

## D'où vient chaque exercice
- **Exercices 1 à 4** : écrits pour ce contrôle.
- **Exercice 5** (10 points) : exercice 2 du sujet **24-NSIJ2JA1** (baccalauréat NSI 2024, Asie, jour 2 ; parenthèses et pile, 6 points au bac), questions 1, 2, 4, 5, 6 et 8 reprises telles quelles ; une phrase ajoutée à la place de la question 3 ; l'en-tête des deux fonctions à écrire donné. Sujet officiel : https://kxs.fr/files/sujets/2024/ecrit/terminale-2024-asie-jour-2.pdf. Le barème par question est celui de ce contrôle.
- **Corrigé** : rédigé pour ce contrôle ; pour l'exercice 5, comparé au corrigé publié par l'AEIF : https://aeif.fr/wp-content/uploads/2025/07/corr_Asie_2024_2.pdf.

## Vérifier
- `python3.13 -I verifier.py` (depuis ce dossier) : le total du sujet (20), le partage 4 + 6 + 10, les points annoncés par le corrigé question par question ; les programmes du sujet exécutés tels quels ; les codes à trous remplis avec le corrigé aux lignes annoncées ; le message d'erreur comparé à celui de Python 3.13 (et qui ne donne pas la correction) ; les exemples des en-têtes, qui ne donnent la réponse d'aucune autre question ; les variantes acceptées et les erreurs fréquentes citées.
- `python3 -I charte/gabarit-controle/verifier-controle.py --detail nsi-terminale/fichiers/cc-term-poo-pile-file-2026/source/controle.tex` (depuis la racine du dépôt) : questions à tiroirs, fonctions, barème, savoirs notés deux fois (annotations `%! savoir=`), temps.

Compilation : `pdflatex` deux passes (`\numpages`), classe `exam` et paquets standard de TeX Live (Overleaf). Les demi-points s'écrivent `\half` (`\question[1\half]`).
