# Sources LaTeX

Par Babash - NSI Tani Malandi et Johanne Bakalara (CC BY-SA 4.0).

Compilation : `latexmk -pdf -shell-escape main-dm-premiers-pas.tex main-dm-boucles-imbriquees.tex main-dm-boucles-while.tex main-dm-DM_noel.tex main-dm-cryptographie.tex` (pdfLaTeX).

Pages en ligne (T125) : pour les DM convertis au style « Signal pirate », la page HTML est désormais la référence (`dm-premiers-pas/index.html`, `dm-boucles-imbriquees/index.html`), et chaque PDF (`dm-premiers-pas.pdf`, `dm-boucles-imbriquees.pdf`) est imprimé depuis elle avec `charte/imprimer-td.py`. Les réponses du corrigé sont obtenues par exécution : `corrige-dm-premiers-pas.py`, `corrige-dm-boucles-imbriquees.py`.

## Pages en ligne du lot L3 (T125)

- « Boucle while : la pyramide » (`main-dm-boucles-while.tex`) : la page HTML auto-corrective `../dm-boucles-while-pyramide/index.html` est désormais la référence ; le PDF `../dm-boucles-while-pyramide.pdf` en est l'impression vierge (`charte/imprimer-td.py`). Corrigé calculé par `corrige-dm-boucles-while.py`.
- « DM de Noël » (`main-dm-DM_noel.tex`) : la page HTML auto-corrective `../dm-noel/index.html` est désormais la référence ; le PDF `../dm-noel.pdf` en est l'impression vierge. Corrigé calculé par `corrige-dm-noel.py`.
- « La science du secret et la machine Enigma » (`main-dm-cryptographie.tex`) : deux pages HTML auto-correctives, `../dm-cryptographie/index.html` (feuille 1 : César) et `../dm-cryptographie/feuille-2.html` (feuille 2 : Vigenère et Enigma), sont désormais la référence ; le PDF `../dm-cryptographie.pdf` réunit leurs deux impressions vierges (`charte/imprimer-td.py`, qui réunit les deux feuilles). Corrigé calculé par `corrige-dm-cryptographie.py`.

Erreur de l'original corrigée (T125b, 21/11) : « La science du secret » disait « les autres lettres : moins de 1 % » sous le tableau des fréquences. C'est faux : les dix lettres du tableau font 75,4 %, donc les 16 autres se partagent 24,6 % (1,5 % en moyenne). La page dit désormais « les 16 autres lettres se partagent les 24,6 % qui restent (environ 1,5 % en moyenne) » : seulement ce qui se calcule sur le tableau de l'énoncé (T125c, 22/11 : « moins de 4 % chacune » est retiré, faute de source ; la valeur de S, 7,1 %, est une question posée à l'enseignant·e) ; le calcul est à la fin de `corrige-dm-cryptographie.py`.

Passe finale (T125c, 22/11) : « Boucle while : la pyramide », question 5 : comme dans l'original, le nombre d'étages est saisi avec `input` (en ligne, la page saisit 7 puis 3 : 140 et 14 billes, `data-entrees`) ; « Boucles imbriquées » : la question d'origine « Donne les variables et leurs types » est imprimée avec ses lignes (les deux choix restent à l'écran) ; « DM de Noël », question 9 : la question d'origine, sans choix, est imprimée avec ses lignes (le choix reste à l'écran).
