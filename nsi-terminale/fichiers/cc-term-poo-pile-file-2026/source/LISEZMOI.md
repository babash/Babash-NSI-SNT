# Sources LaTeX

Contrôle de Terminale NSI de novembre 2026 (2 h, 20 points) : POO, pile, file et rappels de 1re, par Babash - NSI Tani Malandi (CC BY-SA 4.0).

## D'où vient chaque exercice
- **Exercices 1 à 4** (10 points : classe `Barge`, classe `Playlist`, pile et file avec l'interface du cours, dictionnaire des prix du marché) : écrits pour ce contrôle.
- **Exercice 5** (10 points) : exercice 2 du sujet **24-NSIJ2JA1** (baccalauréat NSI 2024, Asie, jour 2 ; parenthèses et pile, 6 points au bac), repris tel quel ; seule la numérotation des questions change (questions 12 à 19). Sujet officiel : https://kxs.fr/files/sujets/2024/ecrit/terminale-2024-asie-jour-2.pdf. Le barème par question (ramené à 10 points) est celui de ce contrôle : le sujet officiel ne donne que le total.
- **Corrigé** : rédigé pour ce contrôle ; pour l'exercice 5, comparé au corrigé publié par l'AEIF (Association des enseignantes et enseignants d'informatique de France) : https://aeif.fr/wp-content/uploads/2025/07/corr_Asie_2024_2.pdf (décompte des comparaisons de la question 18 suivant sa convention).

## Fichiers
- `controle.tex` : le sujet (`sujet.pdf`) ; `corrige.tex` : le corrigé (`corrige.pdf`). Aucun fichier de style à part : classe `exam` et paquets standard de TeX Live (Overleaf).
- `verifier.py` : toutes les réponses calculées du corrigé, obtenues en l'exécutant (`python3 verifier.py`, Python 3.13).

Compilation : `pdflatex` deux ou trois passes (le tableau du barème a besoin d'une seconde passe). Les PDF du dossier sont compilés par pdfLaTeX (TeX Live 2023, classe `exam` 2.704).
Les demi-points s'écrivent `\half` (`\question[1\half]`) : les points décimaux (`[0.5]`) ne s'affichent pas correctement avec cette version de la classe `exam`.
