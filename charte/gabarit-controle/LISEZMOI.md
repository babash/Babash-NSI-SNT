# Écrire un contrôle (mode d'emploi pour les Ateliers)

Un contrôle se fait **dans le temps annoncé par un·e élève moyen·ne**, se corrige **vite et pareil d'une copie à l'autre**, cherche les points que l'élève a montrés et ne paie ni ne sanctionne deux fois la même chose. Cette page dit comment, avec un outil qui le vérifie : `verifier-controle.py`.

Elle met en œuvre les critiques de l'enseignant du 25/11/2026 (registre, C7 et C8 : « tu as tendance à poser 5 questions en une : cela complexifie la correction et pénalise les élèves. Ils sont aussi trop longs, généralement beaucoup de fonctions à écrire. ») et ses choix du même jour : G1 à G4 et leur détail par niveau, G22, G23 et G29 (la notation), G35 et G41 (où l'on répond), G36 (l'exercice de bac adapté et dit), G37 (« trouve l'erreur »), Tle-2 (le partage 10 + 10 en terminale), ainsi que les cinq règles proposées par le ou la Critique (T158). Modèles :
- terminale, gros contrôle en mode bac : `nsi-terminale/fichiers/cc-term-poo-pile-file-2026/source/controle.tex` (sa version donnée en classe, pour comparer : `source/version-donnee-2026-11-25/`) ;
- première, réponses sur le sujet : `nsi-premiere/fichiers/cc-prem-conditions-boucles-fonctions/source/generer.py` (HTML et PDF).

Ce dossier appartient au Designer (`charte/`, CLAUDE.md) ; la règle y est rangée à côté du gabarit des TD.

## La règle en douze points

1. **Une question = une seule chose demandée = une seule réponse attendue.** « Écris, explique, donne la complexité et teste » devient a), b), c), d), chacune avec ses points. Les tiroirs discrets comptent aussi : « Donner les valeurs de a et de c », « entourer… et souligner… », « Indiquer la ligne fautive ; la réécrire ».
2. **Exception voulue : « trouve l'erreur » est une seule question, « trouver et expliquer »**, aux points partagés moitié-moitié (G37) : la correction, puis l'explication en quelques mots. Ce n'est pas un tiroir.
3. **Le début : des questions de cours courtes**, 4 ou 5 points que tout le monde peut prendre : vocabulaire, vrai ou faux, QCM, relier (G3). Jamais un exercice type bac ni un « prévoir » en premier.
4. **Faire écrire du code selon le niveau** (tableau ci-dessous) : surtout **compléter**, **corriger**, **prévoir une sortie**, **dérouler une trace**. Les fonctions entières sont rares, courtes et **cadrées** : la signature, une docstring **en mots** et un exemple sont donnés (dans le cadre de réponse sur le sujet, ou dans l'énoncé en mode bac).
5. **Un savoir, une fois** (G29 ; règle 1 du Critique). À côté de chaque question, on écrit le savoir qu'elle note (`%! savoir=…` dans le `.tex`) ; deux questions sur le même savoir, ou qu'une même erreur fait perdre ensemble, sont fusionnées ou l'une est remplacée. Exemples relevés : « pile = dernier entré, premier sorti » noté quatre fois ; la borne de fin de `range` notée quatre fois ; deux programmes à trous aux trous identiques.
6. **L'énoncé ne donne aucune réponse** (règle 2 du Critique). Une docstring, un exemple, une phrase de contexte ou un message d'erreur ne contient la réponse d'aucune question notée, la sienne comprise : la docstring dit en mots ce que fait la fonction, pas la condition Python (« Renvoie le prix de la livraison… », et non « 0 si montant >= 30 ») ; l'exemple d'une fonction n'est pas la réponse d'une autre question (un contre-exemple demandé ailleurs) . Une réponse attendue n'est jamais imprimée ailleurs dans le sujet (par exemple dans la table d'une interface). **Le message d'erreur**, lui, est toujours le vrai message de Python : s'il donne la correction (« Maybe you meant '==' », « expected ':' »), la question demande aussi l'explication (G37), et l'on ne prend pas que des erreurs de ce genre (les TD font lire et expliquer ces messages).
7. **Le temps** : l'estimation de l'outil et ta propre passe (tu fais le contrôle à la main, comme un·e élève, et tu comptes **3 fois ton temps**, relecture comprise) restent **sous le temps annoncé**. Vise 75 à 90 %.
8. **Le barème** (G4, G22, G23, G29) : points entiers ou demi-points **à côté de chaque question**, total **exactement 20**, sans grille de compétences ; un·e élève fragile atteint au moins 5 (les questions de cours y suffisent presque). Le corrigé le dit en tête : **toute fonction qui fait ce qui est demandé a tous les points, même maladroite** ; **une erreur de syntaxe mineure** dans un raisonnement juste coûte 0 ou 0,25 ; **une erreur ne se paie qu'une fois** (une réponse juste à partir d'une erreur précédente a ses points). Le détail du corrigé peut descendre au quart de point entre les trous d'une même question : on cherche les points que la copie montre.
9. **Des questions indépendantes** : une erreur en 2 ne fait pas perdre la 3. Si une question s'appuie sur une autre, l'énoncé donne ce qu'il faut (« on dispose de la fonction… », « l'énoncé dit ce que fait la fonction »).
10. **Pas de piège** propre au langage ni hors programme (C1) : on évalue ce qui a été travaillé ; une formulation qui fait douter un·e élève qui sait (« au plus un des blocs ») est un piège. Dans un QCM, la bonne option ne se repère jamais à sa forme (longueur, place, précision).
11. **Où l'on répond** (G35, G41). **Sur le sujet**, à tous les niveaux (certains élèves n'ont ni feuille ni stylo), à une place qui a **la taille de la réponse écrite à la main, plus une ligne** (règle 5 du Critique : une sortie de deux lignes a deux lignes). **Sauf les gros contrôles de terminale, en mode bac** : sujet court sans zones de réponse, réponses sur copie ; le QCM, les vrai ou faux et le « relier » se répondent par lettres (« 2 : b » ; l'exemple d'une consigne prend une lettre hors de la liste : « e : pile ») ; un code à trous se complète en écrivant **les seules lignes complétées** (« Écrire sur la copie les lignes 4, 6, 7 et 8 complétées »), sans recopier le code ; un dessin se fait sur la copie, l'orientation dite dans la consigne (« verticalement, le sommet en haut »).
12. **Le corrigé se recalcule et tout ce qui annonce le contrôle change avec lui** (règles 3 et 4 du Critique). La somme du détail de chaque question égale ses points ; chaque « erreur fréquente » est possible sur la forme actuelle de la question ; un script le vérifie comme il vérifie les réponses (`verifier.py`, ou `verifier()` du générateur), en exécutant chaque réponse, chaque variante acceptée, chaque erreur citée, et les codes à trous remplis avec le corrigé. La fiche, la séance de révision et tout document qui cite la structure ou le barème du contrôle changent dans la même publication.

## Par niveau (choix de l'enseignant du 25/11, 10:20)

| | Seconde (SNT) | Première | Terminale |
|---|---|---|---|
| Où l'on répond | sur le sujet | sur le sujet | sur le sujet ; **les gros contrôles (1 h 30, 2 h) en mode bac, sur copie** |
| Écrire du code | **jamais** : lire et prévoir un programme très court ; pas de trous | compléter, corriger, prévoir ; **une seule fonction courte cadrée** (4 à 6 lignes) par contrôle ; très guidé, mais pas dicté | surtout compléter ; **1 ou 2 fonctions cadrées, en fin de sujet** |
| Partage des points | — | — | gros contrôle : **10 points de questions type TD (dont 4 ou 5 de cours) et 10 points d'un exercice de bac** (Tle-2) |
| Contextes | le moins de texte possible ; proches des élèves | proches des élèves en début d'année, puis peu à peu ceux du bac | comme au bac |
| Exercice type bac | non | possible en fin d'année | oui |
| Partout | début par des questions de cours courtes (4 ou 5 points) ; points par question, total 20 | | |

**L'exercice de bac** (G36) : on choisit le sujet le mieux adapté et on peut l'adapter un peu ; on le **dit toujours en tête** du sujet et du corrigé (questions retirées, phrase ajoutée, en-têtes donnés). Le texte des questions gardées reste celui de l'énoncé officiel. Une question retirée dont une autre dépend est remplacée par **une phrase de l'énoncé** (« On dispose aussi d'une fonction… »). Quand un énoncé repose sur un contexte culturel peu familier aux élèves, une phrase l'explique (G52), sans changer l'énoncé.

## Les types de questions à préférer

| Type | Exemple de consigne | Temps élève (ordre de grandeur) |
|---|---|---|
| Vocabulaire | « Que signifie le sigle LIFO ? » | 1 à 2 min |
| Vrai ou faux | « Une même pile peut être programmée de plusieurs façons sans changer son interface. » V / F | 1 min |
| QCM (4 options de même forme) | « Dans une méthode, que désigne `self` ? » | 1 min |
| Relier ou associer | situations → pile ou file ; mots-clés → rôles | 2 min |
| Prévoir | « Qu'affiche la ligne 7 ? » | 2 à 3 min |
| Dérouler | « Dessiner la pile après la boucle (verticalement, le sommet en haut). » | 3 à 4 min |
| Compléter | code à trous, un trou par élément de réponse, des trous différents d'un programme à l'autre | 2 à 4 min |
| Trouver l'erreur | message réel qui ne donne pas la correction ; « Corriger, puis expliquer en quelques mots » (½ + ½) | 3 à 4 min |
| Choisir et justifier en une phrase | « Pile ou file ? Justifier en une phrase. » (une ligne) | 2 à 3 min |
| Fonction entière cadrée | en-tête donné : `def …(…):`, docstring en mots, exemples | 8 à 10 min |

À éviter : « Recopier et compléter » (sur le sujet on complète sur place ; en mode bac on écrit les seules lignes complétées), « Justifier chaque ligne », « pour chaque situation, dire… et justifier », « Écrire un programme… Quel nombre est affiché ? » (deux demandes), la question qui enchaîne trois verbes, un `print` qui fait dépendre la réponse de l'ordre d'évaluation de ses arguments (`print(b.embarquer(80), b.passagers)`).

## Avant / après : une question à tiroirs découpée

Avant (contrôle du 25/11/2026, question 8 b, ½ point) :

> Donner les valeurs de *a* et de *c*, dessiner *p* et *f* à la fin du programme, et donner ce qu'affiche la dernière ligne.

Quatre demandes pour ½ point, chacune dépendant de la précédente, et une copie qui écrit tout cela en vrac : la correction est longue et un seul faux pas (dépiler le premier élément) fait tout perdre.

Après (version du site, question 8, mode bac) :

> (a) (½ point) Dessiner sur la copie la pile *p* juste après la boucle *for* (ligne 5) : verticalement, le sommet en haut.
> (b) (½ point) Qu'affiche la ligne 10 ?

Deux réponses, deux blocs de points ; l'orientation est dite ; les valeurs de *a* et *c* et l'état final passent au corrigé comme explication. Les dessins de la file et de l'état final, qui notaient le même savoir, sont retirés (un savoir, une fois).

Autre exemple, les questions de cours : « Que signifient les sigles LIFO et FIFO ? Lequel caractérise une pile ? » (trois demandes) devient « Que signifie le sigle LIFO ? » (½ point) ; les vrai ou faux portent sur d'autres savoirs (interface et implémentation, une classe donne plusieurs objets…), dont la réponse n'est imprimée nulle part dans le sujet.

## Le calibrage du temps

L'outil additionne, pour chaque question : la lecture (100 mots par minute, 0,15 min par ligne de code), le travail selon le type de demande (fonction 8 min, programme 6, recopier puis compléter 6, tracer 4, calculer 4, compléter 2,5, prévoir 2,5, expliquer 3, phrase 1,5, corriger 2, trouver et expliquer 3,5, instruction 1,5, donner 1,5, cocher 1), puis 10 % de relecture. Il ne compte pas le temps d'écrire sur une copie en mode bac (numéros, lignes complétées, dessins) : ajoute 5 à 10 min. Réglage, sur le contrôle de terminale de novembre 2026 refait à la main (temps de l'enseignant·e × 3) :

| Contrôle (2 h) | À la main, × 3 | Outil |
|---|---|---|
| Version donnée le 25/11/2026 (6 fonctions, 9 questions à tiroirs) | environ 140 min | 160 min (133 %) |
| Version du site (mode bac, 2 fonctions cadrées, 10 + 10) | environ 90 min, copie comprise | 80 min (67 %) |

Sur les contrôles d'origine de l'enseignant, l'outil donne de 50 à 90 % du temps annoncé pour la plupart, et signale deux sujets un peu longs (piles et files 2025 : 103 min pour 1 h 30, 4 fonctions ; rattrapage 2025 : 50 min pour 45). La dernière décision reste ta passe à la main : **fais toujours le contrôle toi-même**.

## La mise en page (classe `exam`, format Overleaf de l'enseignant)

- Classe `exam`, 12 pt, `noanswers`, `addpoints` ; titre, auteur « Babash - NSI Tani Malandi », date avec « Durée : 2h » ; ligne des sources en italique sous le titre ; consignes et tableau des points et durées ; pied « Babash - NSI Tani Malandi · CC BY-SA 4.0 · page n / N ». Le vrai nom de l'enseignant n'apparaît jamais. Rien pour l'enseignant·e dans le sujet élève (« version révisée », « phrase ajoutée… ») : cela va en tête du corrigé et dans le `LISEZMOI` des sources.
- Points : `\question[1]`, `\part[\half]`, `\question[1\half]`. La classe de TeX Live 2023 ne sait pas faire les quarts de point ni `[0.5]` : on découpe autrement.
- Une seule `questions`, ouverte après le titre du premier exercice (en rouvrir une remet la numérotation à 1) ; les titres d'exercice sont des `\section` à l'intérieur.
- Mode bac : aucune zone de réponse ; les options d'un QCM en liste `a) b) c) d)` ; l'en-tête d'une fonction à écrire dans un cadre (`lstlisting` de style `entete`) juste sous la question, avec la phrase « on écrit sur la copie la ligne `def` puis le corps de la fonction (la docstring n'est pas à recopier) » ; la table d'une interface sur la même page que les questions qui s'en servent.
- Réponses sur le sujet en LaTeX : le préambule de la première révision du contrôle de terminale en donne les outils (`git show 0ad51b3:nsi-terminale/fichiers/cc-term-poo-pile-file-2026/source/controle.tex` : `\court`, `\rep`, `\trou`, le style `trous`, `cadre`, `\case`, `\pilevide`) ; en HTML, le générateur du contrôle de première.
- Deux colonnes (`gauche`, `droite`) : le code à gauche (`\footnotesize`, 10 pt), les questions courtes à droite.
- `\needspace{n\baselineskip}` avant chaque question longue et chaque titre d'exercice : jamais une question séparée de son code ou de son en-tête, jamais un titre seul en bas de page.
- Regarde **chaque page** rendue en image (`pdftoppm -r 70`) avant de rendre ; corrige les `Overfull \hbox` du journal.

## L'outil

```
python3 -I charte/gabarit-controle/verifier-controle.py <sujet>.tex [--detail] [--niveau premiere] [--duree 1h30] [--strict]
```

Il lit le sujet (classe `exam`) et signale :
- les **demandes multiples** : verbes de consigne en tête de phrase ou après « et », « puis », une virgule, « ; » (pronom compris : « la réécrire », « l'expliquer ») ; tournures interrogatives partout ; deux objets dans une phrase (« les valeurs de a et de c », « puis celle de b ») ; deux verbes de marquage différents (« entourer… et souligner… »). Comptent pour **une** réponse : « choisir et justifier en une phrase », un QCM ou un vrai ou faux (options et listes ignorées), « trouver et expliquer » (G37), « écrire sur la copie… » (mode bac : dit où répondre) ;
- les **fonctions entières** : leur nombre selon le niveau (seconde 0, première 1, terminale 2), leur **cadrage** (signature, docstring et exemple donnés), leur place en fin de sujet en terminale ;
- le **barème** : questions sans points, points non répartis, **total différent de 20**, et en terminale (1 h 30 ou plus) un exercice de bac qui ne fait pas **10 points** ;
- le **début** : un premier exercice de questions de cours de 4 ou 5 points ;
- les **savoirs notés deux fois**, d'après les annotations `%! savoir=…` (et les questions qui n'en ont pas, dès qu'on en met une) ;
- les **dépendances** annoncées, les questions **peu payées** pour leur temps, et le **temps** estimé.

Le niveau vient du dossier (`snt/`, `nsi-premiere/`, `nsi-terminale/`). Annotations dans le `.tex` (commentaires, invisibles dans le PDF), à l'intérieur de la question : `%! savoir=pile-lifo`, `%! bac` (énoncé officiel : alertes affichées, sans compter dans `--strict`), `%! fonction`, `%! pas-fonction (raison)`, `%! min=6`, `%! une-demande (raison)`. `une-demande` est **contrôlée** : sans raison entre parenthèses, ou posée sur trois demandes ou plus, ou sur une fonction avec autre chose, elle est refusée et signalée.

Ce que l'outil ne sait pas faire, et que ta passe à la main puis le ou la Critique doivent voir :
1. lire les contrôles en HTML (le contrôle de première, les contrôles de notions en ligne) : leur générateur vérifie lui-même son barème ;
2. reconnaître un savoir noté deux fois sans annotation, ou sous deux annotations `savoir=` différentes (`pile-lifo` et `pile-ordre`, par exemple : choisir un nom par savoir et s'y tenir), ni une réponse donnée ailleurs dans le sujet (une docstring, un exemple, la table d'une interface) ;
3. mesurer la place laissée pour répondre, compter les trous, additionner le barème détaillé du corrigé (c'est le rôle de `verifier.py`) ;
4. juger une formulation (piège, double lecture, phrase trop longue), la clarté ou l'utilité d'une question ;
5. tous les tiroirs : il reconnaît les tournures courantes, pas toutes ; une phrase descriptive peut, rarement, compter pour une demande (vérifie avec `--detail`).

## Les contrôles mesurés le 25/11/2026 (T142, T158)

| Contrôle | Auteur | Questions à tiroirs | Fonctions entières | Temps estimé / annoncé |
|---|---|---|---|---|
| Terminale, POO, piles, files, novembre 2026 : version donnée | agent (T130) | 9 | 6 (dont 2 dans l'exercice de bac) | outil 160, à la main environ 140 / 120 min |
| Terminale, même contrôle, version du site (mode bac, 10 + 10) | agent (T142) | 0 (1 dans l'énoncé officiel) | 2, cadrées, en fin de sujet | outil 80, à la main environ 90 / 120 min |
| Première, conditions, boucles, fonctions (HTML), version du 20/11 | agent (T98b) | 2 trajets du robot à deux réponses (les six « entoure, corrige et explique » ne sont pas des tiroirs selon G37, mais valaient 0,25 point) | 4 (2 fonctions, 2 programmes du robot) | à la main : environ 100 / 90 min |
| Première, même contrôle, version du site | agent (T142) | 0 | 1, cadrée (4 lignes) | à la main : environ 65 / 90 min |
| Contrôles de notions (arbres, piles et files, POO ; en ligne) | agents (T108, T108b) | 0 | 0 | 20 min, 12 questions d'un point : conformes |
