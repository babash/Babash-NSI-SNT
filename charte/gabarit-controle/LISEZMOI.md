# Écrire un contrôle (mode d'emploi pour les Ateliers)

Un contrôle se fait **dans le temps annoncé par un·e élève moyen·ne**, se corrige **vite et pareil d'une copie à l'autre**, et ne pénalise jamais deux fois la même erreur. Cette page dit comment, avec un outil qui le vérifie : `verifier-controle.py`.

Elle répond aux critiques de l'enseignant du 25/11/2026 (registre, C7 et C8 : « tu as tendance à poser 5 questions en une : cela complexifie la correction et pénalise les élèves. Ils sont aussi trop longs, généralement beaucoup de fonctions à écrire. ») et à ses choix du même jour (G1 à G4, détaillés par niveau à 10:20). Modèle complet : le contrôle de terminale de novembre 2026, version révisée, `nsi-terminale/fichiers/cc-term-poo-pile-file-2026/source/controle.tex` (et sa version donnée en classe, gardée pour comparer, dans `source/version-donnee-2026-11-25/`).

## La règle en dix points

1. **Une question = une seule chose demandée = une seule réponse attendue**, notée d'un bloc. « Écris, explique, donne la complexité et teste » devient a), b), c), d), chacune avec ses points.
2. **Le début : des questions de cours courtes**, 4 ou 5 points que tout le monde peut prendre : vocabulaire, vrai ou faux, QCM, relier. Jamais un exercice type bac ni un « prévoir » en premier.
3. **Faire écrire du code selon le niveau** (tableau ci-dessous) : surtout **compléter**, **corriger une ligne**, **prévoir une sortie**, **dérouler une trace** ; les fonctions entières sont rares, courtes et **cadrées** : la signature, la docstring et un exemple sont donnés dans le cadre de réponse.
4. **Le temps** : l'estimation de l'outil et ta propre passe (tu fais le contrôle à la main, comme un·e élève, et tu comptes **3 fois ton temps**, relecture comprise) restent **sous le temps annoncé**. Vise 75 à 90 %.
5. **Le barème** : points entiers ou demi-points **à côté de chaque question**, total sur 20, sans grille de compétences. Le tableau du début donne les points et la durée conseillée de chaque exercice.
6. **Des questions indépendantes** : une erreur en 2 ne fait pas perdre la 3. Si une question s'appuie sur une autre, l'énoncé donne ce qu'il faut (« on dispose de la fonction… », « l'énoncé dit ce que fait la fonction ») et le corrigé note l'erreur reportée comme juste.
7. **Pas de piège** propre au langage ni hors programme (C1) : on évalue ce qui a été travaillé. Dans un QCM, la bonne option ne se repère jamais à sa forme (longueur, place, précision).
8. **« Trouve l'erreur »** : le message d'erreur réel de Python 3.13 est montré, tel quel (seul le dossier est retiré du chemin), et vérifié par un script ; on demande **la ligne corrigée**, une seule chose.
9. **On répond sur le sujet**, à la place prévue, qui est celle de la réponse attendue écrite à la main ; une question n'est jamais séparée de sa zone de réponse ; pas de titre en bas de page ; le code et les questions qui en parlent sont côte à côte quand ils tiennent.
10. **Le corrigé** : pour chaque question, la réponse encadrée, les variantes acceptées, le barème détaillé (au quart de point quand il y a plusieurs trous), l'erreur fréquente ; chaque réponse et chaque erreur citée est **exécutée** par un script (`verifier.py`), y compris les codes à trous du sujet remplis avec le corrigé.

## Par niveau (choix de l'enseignant du 25/11, 10:20)

| | Seconde (SNT) | Première | Terminale |
|---|---|---|---|
| Écrire du code | **jamais** : lire et prévoir un programme très court ; pas de trous | à compléter, corriger, prévoir ; **une seule fonction courte cadrée** (4 à 6 lignes) par contrôle | surtout à compléter ; **1 ou 2 fonctions cadrées, en fin de sujet** |
| Contextes | le moins de texte possible ; proches des élèves | proches des élèves en début d'année, puis peu à peu ceux du bac | comme au bac |
| Exercice type bac | non | possible en fin d'année | oui, tel quel (on peut n'en garder qu'une partie, dite en tête du sujet) |
| Partout | début par des questions de cours courtes (4 ou 5 points) ; points par question, total sur 20 | | |

Un exercice officiel du bac reste tel quel. On peut en retirer des questions (le dire en tête du sujet et du corrigé) ; une question retirée dont une autre dépend est remplacée par **une phrase de l'énoncé** (« On dispose aussi d'une fonction… », marquée « ajoutée au sujet d'origine »). Le cadre de réponse peut donner la signature et la docstring : c'est de la mise en page, pas une retouche de l'énoncé.

## Les types de questions à préférer

| Type | Exemple de consigne | Temps élève (ordre de grandeur) |
|---|---|---|
| Vocabulaire | « Que signifie le sigle LIFO ? » | 1 à 2 min |
| Vrai ou faux | « Dans une file, l'élément retiré en premier est le dernier ajouté. » ☐ V ☐ F | 1 min |
| QCM (4 options de même forme) | « Dans une méthode, que désigne `self` ? Cocher la bonne réponse. » | 1 min |
| Relier | situations → pile ou file | 2 min |
| Prévoir | « Qu'affiche la ligne 6 ? » | 2 à 3 min |
| Dérouler | « Compléter le dessin de la pile après la boucle (sommet en haut). » (cases dessinées) | 3 à 4 min |
| Compléter | code à trous sur le sujet, un trou par élément de réponse | 2 à 4 min |
| Corriger | message d'erreur réel, « Corriger la ligne 5. » | 2 à 3 min |
| Choisir et justifier en une phrase | « Pile ou file ? Justifier en une phrase. » (une réponse : une ligne) | 2 à 3 min |
| Fonction entière cadrée | cadre qui commence par `def …(…):`, la docstring et un exemple | 8 à 10 min |

À éviter : « Recopier et compléter » (on complète sur le sujet), « Justifier chaque ligne », « pour chaque situation, dire… et justifier » (une partie par situation, ou un « relier »), « Écrire un programme… Quel nombre est affiché ? » (deux demandes), la question qui enchaîne trois verbes.

## Avant / après : une question à tiroirs découpée

Avant (contrôle du 25/11/2026, question 8 b, ½ point) :

> Donner les valeurs de *a* et de *c*, dessiner *p* et *f* à la fin du programme, et donner ce qu'affiche la dernière ligne.

Quatre demandes pour ½ point, chacune dépendant de la précédente, et une copie qui écrit tout cela en vrac : la correction est longue et un seul faux pas (dépiler le premier élément) fait tout perdre.

Après (version révisée, question 10) :

> (a) (½ point) Compléter le dessin de la pile *p* ci-dessous, juste après la boucle *for*.
> (b) (½ point) Compléter le dessin de la file *f* ci-dessous, juste après la boucle *for*.
> (c) (½ point) Qu'affiche la ligne 10 ?

avec, sous le code, une pile de cinq cases (« ← sommet ») et une file de six cases (« tête », « queue ») à remplir. Trois réponses, trois blocs de points ; l'orientation est donnée par le dessin, plus de doute sur « dessiner verticalement, sommet en haut » ; l'état final et les valeurs de *a* et *c* passent au corrigé comme explication.

Autre exemple, les questions de cours : « Que signifient les sigles LIFO et FIFO ? Lequel caractérise une pile ? » (trois demandes) devient « Que signifie le sigle LIFO ? » (½ point) et le vrai ou faux « Dans une pile, l'élément retiré en premier est le dernier ajouté » (½ point).

## Le calibrage du temps

L'outil additionne, pour chaque question : la lecture (100 mots par minute, 0,15 min par ligne de code), le travail selon le type de demande (fonction 8 min, programme 6, recopier puis compléter 6, tracer 4, calculer 4, compléter 2,5, prévoir 2,5, expliquer 3, phrase 1,5, corriger 2, instruction 1,5, donner 1,5, cocher 1), puis 10 % de relecture. Ces valeurs ont été réglées en refaisant à la main le contrôle du 25/11/2026 et sa version révisée (temps de l'enseignant·e × 3) :

| Contrôle (2 h) | À la main, × 3 | Outil |
|---|---|---|
| Version donnée le 25/11/2026 (6 fonctions, 9 questions à tiroirs) | 44 min × 3 = 132 min, plus la relecture : environ 140 min | 157 min (131 %) |
| Version révisée (2 fonctions cadrées, aucune question à tiroirs hors bac) | 24 min × 3 = 72 min, plus la relecture : environ 85 min | 90 min (75 %) |

L'outil estime un peu large : c'est voulu. Sur les contrôles d'origine de l'enseignant, il donne de 50 à 90 % du temps annoncé pour la plupart, et signale deux sujets un peu longs (piles et files 2025 : 103 min pour 1 h 30, 4 fonctions ; rattrapage 2025 : 45 min annoncées). La dernière décision reste ta passe à la main : **fais toujours le contrôle toi-même**.

## La mise en page (classe `exam`, format Overleaf de l'enseignant)

- Classe `exam`, 12 pt, `noanswers`, `addpoints` ; titre, auteur « Babash - NSI Tani Malandi », date avec « Durée : 2h » ; pied « Babash - NSI Tani Malandi · CC BY-SA 4.0 · page n / N ». Le vrai nom de l'enseignant n'apparaît jamais.
- Points : `\question[1]`, `\part[\half]`, `\question[1\half]`. La classe de TeX Live 2023 ne sait pas faire les quarts de point ni `[0.5]` : on découpe autrement.
- Une seule `questions` du début à la fin (en rouvrir une remet la numérotation à 1) ; les titres d'exercice sont des `\section` à l'intérieur.
- Zones de réponse (voir le préambule du modèle) : `\court` (une ligne pleine), `\finligne` (la fin de la ligne de la consigne), `\rep{1.7cm}` (lignes pointillées), `\trou{4cm}` (dans le texte ou, avec `escapeinside`, dans le code : `(*@\trou{4cm}@*)`), le style `trous` (interligne large pour écrire dans le code), l'environnement `cadre` (cadre de réponse qui commence par la signature d'une fonction), `\case` (case à cocher), `\pilevide` et `\filevide`.
- Deux colonnes avec les environnements `gauche` et `droite` du modèle : le code à gauche (`\footnotesize`, soit 10 pt), les questions courtes à droite.
- `\needspace{n\baselineskip}` avant chaque question longue et chaque titre d'exercice : jamais une question coupée, jamais un titre seul en bas de page. Un exercice type bac commence sur une nouvelle page.
- Regarde **chaque page** rendue en image (`pdftoppm -r 70`) avant de rendre ; corrige les `Overfull \hbox` du journal.

## L'outil

```
python3 -I charte/gabarit-controle/verifier-controle.py <sujet>.tex [--detail] [--niveau premiere] [--duree 1h30] [--strict]
```

Il lit le sujet (classe `exam`) et signale, question par question : les **demandes multiples** (verbes de consigne en tête de phrase ou après « et », « puis », une virgule ; tournures interrogatives partout ; « choisir et justifier en une phrase » et un QCM comptent pour une réponse), les **fonctions entières** (nombre selon le niveau, cadrage, place en fin de sujet en terminale), les **points** manquants ou non répartis, les **dépendances** annoncées (« en utilisant la fonction précédente »), le **début** (questions de cours, 4 ou 5 points), le **temps** estimé. Le niveau vient du dossier (`snt/`, `nsi-premiere/`, `nsi-terminale/`).

Annotations dans le `.tex` (commentaires, invisibles dans le PDF), à l'intérieur de la question : `%! bac` (énoncé officiel : alertes affichées, sans compter dans `--strict`), `%! fonction`, `%! pas-fonction` (dire pourquoi), `%! min=6`, `%! une-demande` (dire pourquoi).

Ce que l'outil ne sait pas faire : lire les contrôles en HTML (le contrôle de première « Conditions, boucles et fonctions », les contrôles de notions en ligne) ; juger si une question est claire, juste ou utile ; mesurer la place laissée pour répondre. Pour cela : ta passe à la main, puis le ou la Critique.

## Les contrôles mesurés le 25/11/2026 (T142)

| Contrôle | Auteur | Questions à tiroirs | Fonctions entières | Temps estimé / annoncé |
|---|---|---|---|---|
| Terminale, POO, piles, files, novembre 2026 : version donnée | agent (T130) | 9 | 6 (dont 2 dans l'exercice de bac) | 157 / 120 min |
| Terminale, même contrôle, version révisée | agent (T142) | 0 (1 dans l'énoncé officiel) | 2, cadrées, en fin de sujet | 90 / 120 min |
| Première, conditions, boucles, fonctions (HTML), version du 20/11 | agent (T98b) | 6 (« entoure, corrige et explique » pour 0,25 point) et 2 trajets à deux réponses | 4 (2 fonctions, 2 programmes du robot) | à la main : environ 100 / 90 min |
| Première, même contrôle, version révisée | agent (T142) | 0 | 1, cadrée (4 lignes) | à la main : environ 65 / 90 min |
| Contrôles de notions (arbres, piles et files, POO ; en ligne) | agents (T108, T108b) | 0 | 0 | 20 min, 12 questions d'un point : conformes |
