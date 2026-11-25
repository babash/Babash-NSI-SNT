# Écrire un TD en ligne, style « Signal pirate » (mode d'emploi pour les Ateliers)

Un TD est **une seule page HTML** : à l'écran, elle se corrige toute seule ; imprimée, elle **est** la feuille papier (A4, bandeau de 28 mm, code, consoles, lignes de réponse, margouillat, pied de page). On n'écrit jamais de PDF à part.

- Moteur : `assets/td-en-ligne.js` (ne pas le réécrire) ; style : `assets/td-en-ligne.css` (écran clair, écran obscur, papier).
- Modèle : `charte/gabarit-td/modele.html` (commenté) ; exemple rendu : `charte/gabarit-td/index.html` ; TD complet : `charte/td-pilote/`.
- Outils : `charte/nouveau-td.py` (le squelette), `charte/verifier-td.py` (le code exécuté pour de vrai), `charte/imprimer-td.py` (le PDF vierge et les contrôles de mise en page).

## Corrections justes (25/11, T140b) : à lire d'abord

Deux défauts de correction en ligne, trouvés par la Critique T150, corrigés dans le moteur (aucune page à retoucher) :

- **« Trouve l'erreur » d'indentation** (le message réel est une `IndentationError` ou une `TabError`) : le décalage de la ligne corrigée compte. Le code, avec la ligne de l'élève à sa place, doit avoir des blocs justes (comme les lit Python) ; et si `data-reponse` porte un décalage (`    nord()`), le même (une tabulation vaut 4 espaces). La ligne fautive recopiée telle quelle est refusée. À l'écran, l'étiquette devient « Écris cette ligne corrigée, avec ses espaces de début de ligne : » ; la feuille imprimée garde « Écris cette ligne corrigée : » (identique à avant). Les autres « Trouve l'erreur » ne changent pas.
- **Cases liées** d'une question `trous` qui a sa sortie attendue (`pre.td-attendu`, en Python) : le code rempli est **exécuté** (Python, comme dans `verifier-td.py`) quand la correction case par case ne suffit pas : une case refusée seule (le programme rempli est essayé : `while n != 0` est accepté s'il donne la sortie) ; deux cases sur une même ligne dont l'une a plusieurs réponses permises (`while n >= 0` accepté seul alors que le programme affiche 0 de trop : refusé) ; deux cases aux mêmes réponses permises remplies de la même façon (la même ligne écrite deux fois : refusé si la sortie est fausse). Sinon rien ne change (Python n'est pas chargé). Sans connexion, la correction case par case reprend. `data-execution="non"` sur la question l'empêche ; `data-execution="oui"` l'impose.

Reste au contenu des pages (Ateliers) : « Écris le programme » validé par une seule sortie fixe (`print(5050)` passe) ; il faut un second essai (`pre.td-attendu` avec d'autres `data-entrees`) ou des tests cachés (`script.td-tests`).

## Nouveautés du 24/11 (T123e)

Rien ne change **à l'écran** (comparé au pixel sur toutes les pages de TD, à 320, 768 et 1440 px, en clair et en obscur). Ce qui change : **l'impression** des questions courtes regroupées (T123d), où beaucoup de réponses n'avaient plus la place d'être écrites, et deux outils.

### Chaque réponse a la place d'être écrite à la main (le moteur la mesure)

| Mesure | Règle |
|---|---|
| **Place demandée** par une réponse | **2,5 mm par caractère** de la réponse modèle (écriture d'un·e élève, prévue large), **20 mm au moins**. Réponse modèle : pour une `courte`, la variante acceptée **la plus longue** de `data-reponse` ; pour une `libre`, sa jumelle d'écran (la question `data-support="ecran"` qui la précède : `data-reponse`, options justes ou correction), sinon sa propre correction. Une `libre` sans réponse modèle n'entre jamais dans un tableau. |
| Place d'une **étiquette** imprimée (10 pt) | 1,9 mm par caractère, plus 1 mm. |
| **Tableau** « N° \| Consigne \| Réponse » | Une question n'y entre que si sa réponse tient dans la case. La case fait 58 mm (64 mm avec une réponse rédigée) et **s'élargit jusqu'à 100 mm** pour la plus longue réponse du tableau ; une question qui ne tiendrait pas dans 100 mm reste hors tableau, et coupe le groupe. |
| **Étiquette** dans une case | sur la ligne d'écriture si elle en prend **un tiers au plus** et laisse la place de la réponse ; sinon **au-dessus**, avec une ligne d'écriture entière dessous. |
| **Deux colonnes** de questions | à partir de 4 questions à consigne de 48 caractères au plus, et seulement si **chaque réponse tient** dans une case de 30 mm (40 mm avec une réponse rédigée), élargie jusqu'à 44 mm, l'étiquette tenant sur une ligne. Sinon une colonne. |
| `libre` à `data-lignes="1"` **seule** | **jamais sur la rangée de sa consigne** : elle garde sa ligne pleine (186 mm), comme avant T123d. |
| `courte` **seule** | sur la rangée de sa consigne si sa réponse (et son étiquette) tiennent dans la ligne, de 64 mm, allongée jusqu'à 110 mm ; sinon sa ligne pleine. Hors rangée, sa ligne fait au moins la place de la réponse, et passe sous l'étiquette s'il le faut. |
| **Code dans une case** | il ne se coupe qu'à une espace, jamais au milieu d'une expression (`pokemons[1]["types"]` reste entier). |

Ce que le moteur ne peut pas régler : une réponse plus longue qu'une **ligne pleine** (74 caractères environ). `imprimer-td.py` la signale (« Attention : réponse à l'étroit … ligne pleine : data-lignes="2" ») : dans la page, `data-lignes="2"` sur la `libre`. Une alerte « à signaler au Designer » (dans un tableau ou sur une rangée) ne doit jamais apparaître : c'est un défaut du moteur.

`data-regrouper="non"` et `data-lignes="2"` gardent leur effet (T123d). Les PDF publiés ne changent pas tant qu'ils ne sont pas régénérés (passe des Ateliers) : régénérez-les avec `imprimer-td.py` et lisez ses « Attention ».

### Les outils

- `imprimer-td.py` signale, sans bloquer, chaque **réponse à l'étroit** (réponse modèle plus longue que sa place, à 2,5 mm par caractère) : dans un tableau, sur une rangée ou sur une ligne pleine.
- `verifier-td.py` : quand une correction partielle **posée sur le code de départ** échoue, le message est celui de la correction posée (celui que verrait l'élève, par exemple l'assertion des tests cachés) ; celui de la correction seule (souvent un `NameError`) vient en second, après « la correction seule ».
- `tester-outils.py` : deux essais de plus (la correction posée fausse ; les réponses à l'étroit, avec un témoin aux cases de 15 mm).
- `symboles-td.py` : la liste des symboles se reporte dans l'`unicode-range` de « TD Symboles » de `assets/signal-commun.css` (et non plus de `td-en-ligne.css`).

## Nouveautés du 22/11 (T123d)

Rien ne change **à l'écran** (comparé au pixel sur toutes les pages de TD, à 320, 768 et 1440 px, en clair et en obscur). Ce qui change : **l'impression** de toutes les pages (plus courte, sans rien écrire), un outil corrigé et deux options.

### Moins de papier (décision du 22/11 « Regrouper les questions courtes »)

Sans rien changer aux pages :

| Quoi | Sur papier |
|---|---|
| **Questions courtes qui se suivent** : `courte` sur une rangée, et `libre` à `data-lignes="1"` à consigne courte (150 caractères au plus, sans code ni tableau) | **automatique** à partir de 2 : un tableau « N° \| Consigne \| Réponse » (numéros de la suite papier, `data-etiquette` dans la case de réponse, ★ pour un bonus) ; **deux colonnes de questions** à partir de 4 si chaque consigne a 48 caractères au plus. Case de réponse : 58 mm (64 mm s'il y a une réponse rédigée), une ligne de 7 mm. **Depuis T123e** : seulement si la réponse tient dans la case (voir plus haut). Le tableau peut passer d'une page à l'autre entre deux rangées (l'en-tête est répété). Les questions `data-support="ecran"` placées entre elles ne coupent pas le groupe. |
| `libre` à `data-lignes="1"` et consigne courte, seule | ~~sur une rangée~~ : **retiré en T123e**, elle garde sa ligne pleine |
| Code de **plus de 15 lignes**, code à trous de **plus de 10 lignes** (plus d'un tiers de page avec la consigne) | il peut se couper **entre deux lignes**, 3 lignes au moins de chaque côté (avant : 40 lignes) |
| « Écris le programme » avec **une grille ou un schéma** (le robot), code de départ de 48 caractères au plus | la figure **à droite**, le cadre à remplir à sa gauche, la question entière |
| « Trouve l'erreur » au code étroit (`data-cote`) | « Ligne n° » et la ligne corrigée **sous le code, à gauche**, à côté du message d'erreur |
| Question à code étroit (`data-cote`, dont `data-cote-reponse="gauche"`) | reste **entière** : coupée, elle renvoyait tout le reste à la page suivante |
| Titre de partie suivi de son paragraphe ; bande de titre d'une feuille 2, 3… | restent avec ce qui les suit (jamais seuls en bas de page) |

Pourquoi automatique : la règle vaut pour tous les TD (cohérence), elle ne demande aucune retouche des 64 TD en ligne, et elle ne touche que le papier. Pour l'empêcher : **`data-regrouper="non"`** sur `<main>`, sur un bloc qui contient les questions, ou sur une question (elle reste seule et coupe le groupe) ; une question qui ne doit pas être dans un tableau (une consigne qui s'appuie sur la ligne de réponse) : `data-regrouper="non"`. `data-cote="non"` sur une question « Écris le programme » garde la figure au-dessus du cadre.

Défaut corrigé (T123c) : une question sur une rangée (`courte`) restait collée à la question suivante (le `break-after` de sa consigne passait à toute la rangée) et partait avec elle à la page suivante, en laissant du blanc.

**À faire par les Ateliers** : rien dans les pages. Dans la passe finale, **régénérez le PDF** (`imprimer-td.py`) et relisez-le : un tableau de questions courtes se lit-il bien ? une case de réponse suffit-elle ? Sinon, `data-regrouper="non"` ou `data-lignes="2"` (une question à deux lignes n'est jamais regroupée). Une feuille déjà au plus court peut, rarement, prendre une page de plus ou de moins : `imprimer-td.py` dit le nombre de pages.

`numeroter-feuilles.py` : inchangé. Faire commencer la numérotation papier après un tableau numéroté à la main n'est plus utile : le regroupement remplace ces tableaux (une question courte par numéro, `data-support` inutile).

### `verifier-td.py` : correction partielle posée comme le fait l'élève

Une correction qui ne donne que la fonction ou la méthode à écrire est posée sur le code de départ **à sa place** : une fonction du départ est remplacée là où elle est (avant les instructions qui l'appellent) ; une méthode (même nom qu'une méthode du départ, ou premier paramètre `self`) va **dans sa classe** ; une fonction nouvelle va avant la première instruction de premier niveau ; une correction écrite en retrait est d'abord ramenée à gauche. Dix cas des TD type bac (abr, arbres, POO, récursivité) et quatre cas écrits sont dans les essais (`charte/tester-outils.py`, `charte/essais/corrections-partielles.json`).

### `reattribuer-bandeaux.py` : limité à des pages ou à un dossier

```
python3 -I charte/reattribuer-bandeaux.py nsi-premiere/fichiers/bases-python                  # montre, pour ce dossier
python3 -I charte/reattribuer-bandeaux.py --appliquer nsi-terminale/fichiers/td-bac-poo/index.html
```

La répartition est toujours calculée sur tous les TD du dépôt (le bandeau d'une page est celui d'un passage complet) ; seules les pages choisies sont rendues, montrées et écrites.

### Une seule palette

`assets/td-en-ligne.css` charge la palette et les polices par `@import url("signal-commun.css");` (sa première règle) : elles ne sont plus que dans `assets/signal-commun.css`, commun au site et aux TD. Rendu identique (comparé au pixel, écran et papier). Une copie de `td-en-ligne.css` hors du dossier `assets/` doit emporter `signal-commun.css`.

## Nouveautés du 21/11 après-midi (T123c)

Comme pour T123b : une page sans les nouveaux attributs garde son rendu à l'écran. Ce qui change pour toutes les pages : **l'impression** (plus courte, voir « Moins de papier »), et les défauts corrigés (liste à la fin).

### Les numéros continuent d'une feuille à l'autre (décision du 21/11)

La feuille 2 d'un TD ne recommence plus à « Question 1 ». Sur `<main>` :

| Attribut | Effet |
|---|---|
| `data-premiere-question="13"` | la première question de la feuille porte le numéro 13 (à l'écran et sur papier) |
| `data-premiere-question-papier="11"` | seulement si le premier numéro **sur papier** est différent (des questions d'un seul support sur les feuilles d'avant) |

**Ne les écrivez pas à la main** : `charte/numeroter-feuilles.py` les calcule et les pose, dans la **passe finale** d'un lot (après le dernier ajout ou retrait de question) :

```
python3 -I charte/numeroter-feuilles.py nsi-premiere/fichiers/…/mission-fonctions     # un TD (son dossier)
python3 -I charte/numeroter-feuilles.py --tout                                       # tous les TD à plusieurs feuilles
python3 -I charte/numeroter-feuilles.py --tout --verifier                            # contrôle seul (sortie 1 si à refaire)
```

Les feuilles d'un TD sont reconnues dans **les deux rangements** : un dossier (`index.html`, `feuille-2.html`, `feuille-3.html`…) ou des pages de même nom (`td-for.html`, `td-for-2.html`, `td-for-3.html`…) ; un dossier peut contenir plusieurs TD. L'ordre : `data-feuille` s'il est écrit, sinon le nom (`index.html` et `td-for.html` sont la feuille 1). Un TD mal rangé (deux feuilles au même rang) est signalé sans arrêter les autres. Le script ne touche qu'à ces deux attributs.

**Une suite de numéros par support.** Une question `data-support="ecran"` ne compte qu'à l'écran, une `data-support="papier"` que sur papier : sur papier, les numéros ne sautent plus. Une paire écran/papier garde un seul numéro. Exemple : 5 questions à l'écran (`data-support="ecran"`, numéros 5 à 9) pour un seul tableau sur papier (`data-support="papier"`, numéro 5) : la question suivante est la 10 à l'écran et la 6 sur papier (le moteur écrit les deux numéros, un seul se voit).

### Moins de papier (décision « Resserrer »)

Sans rien changer aux pages :
- **Réponses courtes** (`courte` avec une seule consigne, sans code, tableau ni figure, 150 caractères au plus) : sur papier, la consigne et la ligne à remplir tiennent **sur une seule ligne** ; à la suite, elles se resserrent. L'étiquette par défaut « Ta réponse : » n'est pas imprimée ; une `data-etiquette` l'est.
- **Lignes d'écriture** : 7 mm, le minimum lisible à la main (inchangé).
- **Le pied de la page** : les noms, la licence et l'IA sont déjà au pied de chaque page A4 ; sur papier, il ne reste du pied de la feuille qu'**une ligne en fin de feuille**, « Code source sur GitHub : github.com/babash/Babash-NSI-SNT/tree/main/… » (l'adresse lisible), avec son trait et le margouillat s'il s'y cache. Elle reste avec la fin de la dernière question : **aucune page ne porte que cette ligne** (`imprimer-td.py` le refuse). Si le pied nomme d'autres personnes que `data-auteurs`, il reste imprimé en entier, l'adresse après « Code source sur GitHub ».
- **Pied long** (`data-auteurs` de plus de 46 caractères) : police du texte et séparateurs simples, **sur une ligne** (jusqu'à 72 caractères de noms environ).
- **Code de plus de 40 lignes** : il peut passer à la page suivante, coupé entre deux lignes, au lieu d'être poussé entier.
- **Grandes questions** (un code, un tableau ou une figure, et des lignes à remplir) : elles peuvent passer d'une page à l'autre **entre leurs blocs**, qui restent entiers (moins de blanc en bas de page).
- **PDF réuni** (plusieurs feuilles) : les objectifs ne sont imprimés qu'une fois, sur la première feuille.
- **`data-nouvelle-page`** sur `<main>` d'une feuille 2, 3… : dans le PDF réuni, elle commence une nouvelle page, avec « Nom et prénom » et « Classe » (un mini-contrôle que les élèves s'échangent).
- **`data-cote`** marche aussi sur une question `libre` (le code à gauche, les lignes à droite ; automatique pour un code de 34 caractères au plus) et, avec `data-cote="oui"` seulement, sur `erreur`.
- **`data-cote-reponse="gauche"`** (avec `data-cote`) : la ligne à remplir passe **sous le code, à gauche**, et la grille ou le schéma reste à droite (question robot : « Case d'arrivée »).
- **`data-lignes="0"`** sur une question `libre` : **aucune ligne** sur papier (réponse dans un tableau, « entoure sur le code »). Sans `data-lignes` : 3 lignes.
- **Une mention imprimée dans une phrase** : `<span class="td-papier-seul">(sur ta feuille)</span>` reste dans la ligne (aussi `b`, `i`, `em`, `strong`, `code`, `a`, `small`) ; un bloc (`p`, `div`) reste un bloc.

### Le code de départ est imprimé

Le squelette d'une question `code` (`pre.td-depart`) est imprimé en haut du cadre à remplir, en code de 10 pt avec ses numéros de ligne ; dessous, les lignes d'écriture de 7 mm. Avec un squelette, `data-lignes` donne la **hauteur de tout le cadre** (en lignes de 7 mm, squelette compris ; une ligne de code vaut 2/3 de ligne d'écriture), avec 2 lignes d'écriture au moins ; sans `data-lignes` : le squelette et 3 lignes d'écriture. Il n'est pas imprimé s'il est déjà affiché dans la question (même `pre.td-code`). Un long squelette coûte de la place : `imprimer-td.py` dit si la feuille dépasse ses pages. **Un squelette de plus de 20 lignes n'est pas imprimé** (il coûterait une page) : une ligne le dit à sa place (« Code de départ : N lignes, dans la page en ligne. Écris ici ce que tu ajoutes. »). `data-depart-papier="oui"` sur la question l'imprime quand même ; `data-depart-papier="non"` ne l'imprime jamais. **Une ligne du squelette de plus de 80 caractères passe à la ligne** sur papier (après une virgule ou à une espace, jamais dans une chaîne) : la suite est décalée de 4 espaces et porte « → » à la place du numéro de ligne. La page ne change pas.

### Tableau à remplir

```html
<div class="td-table"><table data-case-largeur="25" data-case-hauteur="2">
  <thead><tr><th>Mot</th><th data-case-largeur="40">En binaire</th></tr></thead>
  <tbody><tr><td>A</td><td></td></tr></tbody>
</table></div>
```

| Attribut | Où | Effet |
|---|---|---|
| `data-case-largeur="25"` | `<table>` | chaque cellule **vide** fait 25 mm de large (écran et papier) |
| `data-case-hauteur="2"` | `<table>` | chaque cellule vide a la hauteur de 2 lignes d'écriture (7 mm chacune sur papier) |
| `data-case-largeur="40"` | `<th>` | la largeur de cette colonne (mm) |
| `data-pleine-largeur` | `<table>` | le tableau prend toute la largeur (les colonnes sans largeur se partagent le reste) |

Dans un tableau qui porte l'un de ces attributs, le texte passe à la ligne (les autres tableaux restent sur une ligne par cellule). Aucun `style` dans la page, ni `width`, ni `<col width>`, ni espaces cadratins : retirez-les au passage, le moteur pose les mesures. Trait noir plein (contrôlé par `imprimer-td.py`).

### Le margouillat ne touche jamais le texte du bandeau

`reattribuer-bandeaux.py` rend chaque page (Chromium) à 681, 768, 1024, 1440, 1920 px et en A4 : si le margouillat touche le niveau, le titre ou l'accroche, il prend une autre place du même bandeau. `nouveau-td.py` fait de même à la création. `imprimer-td.py` le signale (« Attention »). **Ne lancez pas `reattribuer-bandeaux.py --appliquer` sur vos pages** : une branche à part le fera après les lots.

### Défauts corrigés

- `input("Ton âge ? ")` : l'invite n'entre plus dans la sortie comparée (moteur et `verifier-td.py`) ; à l'écran, la console montre l'invite et la saisie, comme un terminal. `pre.td-attendu` ne contient que ce qu'affiche `print`.
- Les `print` des tests cachés (`script.td-tests`) sont affichés, mais n'entrent plus dans la sortie comparée.
- `verifier-td.py` lit `data-langage` sur le `<pre>` du code, puis sur la question et la page.
- `imprimer-td.py` : plus de faux « texte caché imprimé » quand la consigne cite la sortie attendue ; le motif de « PDF vierge : NON » est toujours écrit (feuille trop longue comprise).
- Une feuille sans question corrigée en ligne n'affiche plus « Feuille validée » d'office.
- Code à trous : des commentaires alignés en fin de ligne restent alignés malgré les cases.
- « Je sais » sur papier : un espace entre les deux colonnes.
- Une figure à plusieurs SVG les met côte à côte.
- À l'écran (769 px et plus), un code qui dépassait de quelques pixels (8 % au plus de sa largeur) est un peu réduit au lieu de défiler.
- Cases à trous : `t[[[i]]]` (après un nom, une parenthèse ou un crochet) est « `t[` + case `i` + `]` » ; `= [[[1, 2]]]` reste une case qui contient la liste `[1, 2]` (moteur et `verifier-td.py`).
- `verifier-td.py` exécute aussi les **tests cachés** (`script.td-tests`) après chaque correction d'une question « code » ; une correction qui ne donne que la partie à compléter est posée sur le code de départ (sans les blocs qu'elle réécrit), comme le fait l'élève.
- `imprimer-td.py` voit une correction, un coup de pouce ou un retour imprimé : il les lit dans la source de la page, ligne par ligne, et contrôle qu'aucun n'est rendu sur papier. Une question « ordre » `data-support="ecran"` n'est plus cherchée dans le PDF.
- Un mot insécable trop long du titre passe à la ligne ; `nouveau-td.py` prévient (mot de plus de 18 caractères, accroche dans un contrôle).

## Nouveautés du 21/11 (T123b)

Tout ajout passe par un **attribut nouveau** : une page écrite avant le 21/11, sans ces attributs, garde son comportement à l'écran (les options restent dans l'ordre écrit, le code reste en bonus…). Seules changent pour toutes les pages : **l'impression, plus serrée** (voir plus bas), la largeur des cases à trous, et les corrections de défauts (case `[[t[0]]]`, coloration, « n'affiche rien »).

### Décisions de l'enseignant (21/11)

**1. Deux supports pour une question ouverte.** En ligne, un choix auto-corrigé ; sur papier, la question ouverte avec des lignes. Les deux variantes **se suivent** et portent le même numéro (depuis T123c : une suite de numéros par support, voir plus haut).

```html
<section class="td-q" data-type="qcu" id="q4" data-support="ecran"> … </section>
<section class="td-q" data-type="libre" id="q4-papier" data-support="papier" data-lignes="4">
  <p class="td-consigne">Explique pourquoi la boucle ne s'arrête pas.</p>
</section>
```

| Attribut | Effet |
|---|---|
| `data-support="papier"` | n'apparaît qu'à l'impression (et dans le PDF) ; ne compte ni dans l'avancement ni dans « Feuille validée » |
| `data-support="ecran"` | n'apparaît qu'à l'écran |
| `data-type="libre"` + `data-lignes="4"` | réponse rédigée : 4 lignes noires à remplir sur papier ; à l'écran (si elle n'est pas `papier`), une zone de brouillon non corrigée, avec « Voir la correction » ; jamais comptée |

Les attributs `data-support` valent aussi pour tout autre élément (un paragraphe, une figure).

**2. « Écris le programme » est obligatoire** pour valider la feuille : `nouveau-td.py` écrit `data-code="obligatoire"` sur `<main>`. Une question `code` marquée `data-bonus` reste un bonus. (Une page sans `data-code` garde l'ancien défaut : code en bonus, sauf `data-obligatoire`.)

```html
<main class="td" data-td="nsi1-boucles-td1" data-td-version="1" data-ordre="melange" data-code="obligatoire">
```

**3. Tous les noms sur chaque page imprimée** (forme fixée le 21/11, T123c : les noms **séparés par « ; »** ; « et » reste accepté, mais ne l'écrivez plus) : `data-auteurs` sur `<main>` (rempli par `nouveau-td.py --auteurs`). Le pied de chaque page A4 devient « Noms · CC BY-SA 4.0 · conçu avec l'aide de l'IA · page / pages » (sans l'attribut : « Babash - NSI Tani Malandi »). Mettez les mêmes noms dans le pied de la page (`footer.td-pied`) : `nouveau-td.py` le fait.

```html
<main class="td" … data-auteurs="Babash - NSI Tani Malandi ; Etienne Clave ; Marion Dufour">
```

### Nouveaux attributs, un exemple chacun

| Attribut | Où | Exemple et effet |
|---|---|---|
| `data-ordre="melange"` | `<main>` ou question `qcu`/`cases` | options mélangées, toujours de la même façon pour cette question (défaut de `nouveau-td.py`) |
| `data-ordre="fixe"` | question | `<section class="td-q" data-type="qcu" data-ordre="fixe">` : l'ordre écrit est gardé (options « 1, 2, 3, 4 ») |
| `data-lignes` | question `sortie`, `code`, `libre` | `data-lignes="6"` : 6 lignes de 7 mm sur papier (cadre de l'éditeur compris ; sans lui : 30 mm pour le code, autant de lignes que de lignes attendues pour une sortie) |
| `data-largeur` | question `trous` ou `<main>` | `data-largeur="12"` : toutes les cases font 12 caractères. Sans lui, toutes les cases d'une question ont **la même largeur** (la plus longue réponse, arrondie à 6, 10, 16, 24, 32 ou 48) : la largeur ne trahit plus la réponse |
| `data-espaces="exact"` | question `sortie` ou `code` | `data-espaces="exact"` : les espaces de début de ligne comptent (motifs centrés, pyramides) |
| `data-entrees` | question `code`, ou chaque `pre.td-attendu` | `<pre class="td-attendu" data-entrees="4">8</pre>` : chaque `input()` lit une ligne ; plusieurs `pre.td-attendu` = plusieurs essais (tous doivent passer). Plusieurs saisies : une par ligne (`data-entrees="12&#10;5"`) |
| `data-graine` | question `code`, ou `pre.td-attendu` | `data-graine="7"` : `random` donne toujours les mêmes tirages (même résultat dans le moteur et dans `verifier-td.py`) |
| `script.td-preambule` | dans la question, ou dans `<main>` pour toute la page | `<script type="text/x-python" class="td-preambule">def est(): …</script>` : du Python exécuté avant le programme de l'élève (le robot, des données, une classe) ; les numéros de ligne des erreurs restent ceux de l'élève |
| `data-langage` | `<pre>`, question ou `<main>` | `data-langage="sql"` : coloration SQL, et `verifier-td.py` exécute la requête avec SQLite sur les tables de la page ; `data-langage="texte"` : aucune coloration, rien à exécuter (lignes d'un résultat dans une question `ordre`) |
| `script.td-tables` | question ou `<main>` | `<script type="text/x-sql" class="td-tables">CREATE TABLE … ; INSERT …</script>` : les tables pour vérifier le SQL |
| `data-cote` | question | sur papier, un code étroit (34 caractères au plus) se met à gauche et la réponse (lignes, choix, grille) à droite ; `data-cote="non"` l'empêche, `data-cote="oui"` le force |
| `data-pages-max` | `<main>` | `data-pages-max="5"` : 5 pages admises par `imprimer-td.py` (exercice de bac de 6 points) ; 4 par défaut |
| `data-feuille` | `<main>` | `data-feuille="2"` : deuxième feuille d'un TD ; sur papier, une bande de titre fine au lieu du bandeau (`nouveau-td.py --feuille 2`) |
| `class="td-plus-loin"` | un bloc | « Pour aller plus loin » : à l'écran seulement (comme le mémo) ; `data-support="papier"` pour l'imprimer |

### Tableaux, schémas, symboles

```html
<div class="td-table"><table>
  <caption>Table eleve</caption>
  <thead><tr><th>id</th><th>prenom</th></tr></thead>
  <tbody><tr><td class="td-nb">1</td><td>Anli</td></tr></tbody>
</table></div>

<figure class="td-schema">
  <svg viewBox="0 0 200 60" role="img" aria-label="Deux nœuds reliés"> … tracé en currentColor … </svg>
  <figcaption>Le graphe.</figcaption>
</figure>
```

- Tableau : trait noir, en-tête grisé, 10 pt sur papier, défilement dans son cadre sur téléphone (jamais la page) ; `td-nb` aligne un nombre à droite.
- Schéma SVG : `max-width: 100%`, hauteur proportionnelle ; tracez en `currentColor`, il suit l'encre (claire en obscur, noire sur papier). Un dessin aux couleurs fixes : `<figure class="td-schema" data-couleurs="fixes">` (fond blanc en obscur). Le texte d'un SVG est mesuré **à sa taille imprimée réelle** (échelle comprise) : 10 pt au moins.
- `<sup>` et `<sub>` : 10 pt au moins sur papier. Un `<code>` long sans espace passe à la ligne (plus de défilement à 320 px).
- Police « TD Symboles » : ← ↑ → ↓ ↔ ⇒ ⇔ ∧ ∨ ¬ × ≠ ≤ ≥ ≈ ≡ Δ Σ π λ √ ∞ ∑ ∈ ∉ ∅ ∩ ∪ ■ □ ▲ ▼ ◆ ★ ☆ ✓ ✗ (refaite par `python3 -I charte/symboles-td.py`).

### Le bandeau et sa puce

- `--genre TD|DM|TP|Activité|Séance` : la puce du bandeau (et le titre de l'onglet).
- **Le bandeau est tiré de l'identifiant** (SHA-256 modulo 4) : même identifiant, même bandeau, sur toutes les branches, sans regarder le dépôt. Des lots convertis en parallèle ne prennent donc plus tous les mêmes bandeaux.
- `python3 -I charte/reattribuer-bandeaux.py` montre la répartition exacte de tous les TD du dépôt (1, 2, 3, 4, 1…, les feuilles d'un même dossier sur des bandeaux différents) ; `--appliquer` l'écrit (data-bandeau et place du margouillat). À lancer une fois, après les fusions.
- Un titre, une accroche ou un chapitre trop longs ne sont plus coupés : le titre rapetisse, puis passe sur deux lignes, et le bandeau grandit. `nouveau-td.py` prévient, `imprimer-td.py` le signale.

### L'impression, resserrée (toutes les pages)

Objectif : le PDF d'un TD converti ne dépasse pas l'original de plus d'une page, sans descendre sous 10 pt.
- Marges et espacements réduits ; texte à 10 pt, code à 10 pt plus serré ; le numéro de la question sur la ligne de la consigne.
- Une question courte reste entière ; une longue (message d'erreur, schéma, tableau, éditeur) peut passer à la page suivante, mais un code, une console, un tableau, un schéma ou une liste de choix restent entiers, et le titre reste avec sa consigne.
- Code étroit : la réponse à côté (voir `data-cote`). Options courtes : 3 ou 4 colonnes.
- Lignes de réponse : autant que de lignes attendues (`data-lignes` pour régler). L'étiquette « Ce que le programme affiche… » n'est pas imprimée (la consigne le dit).
- Le mémo et « pour aller plus loin » : à l'écran seulement (`data-support="papier"` pour les imprimer).
- Un message d'erreur ou une console trop longs passent à la ligne au lieu d'être refusés.
- **TD à plusieurs feuilles : un seul PDF continu.** Donnez toutes les adresses à `imprimer-td.py`, dans l'ordre :
  ```
  python3 -I charte/imprimer-td.py http://localhost:8000/…/td-for.html http://localhost:8000/…/td-for-2.html http://localhost:8000/…/td-for-3.html …/td-for.pdf
  ```
  Chaque feuille est contrôlée seule (et doit tenir en 4 pages, ou `data-pages-max`), puis le PDF est fait d'un seul tenant : pas de saut de page entre les feuilles, une bande de titre fine pour la deuxième et les suivantes, « Nom et prénom » et le pied une seule fois.

### Vérifier : `verifier-td.py`

- Préambule, `data-entrees`, `data-graine`, plusieurs essais, `data-espaces` : comme dans le moteur.
- SQL (`data-langage="sql"`) : exécuté avec SQLite sur `script.td-tables` ; sans tables, la question est notée « SQL non vérifié » (sans erreur). `data-langage="texte"` : rien à exécuter.
- « Trouve l'erreur » d'indentation : si la ligne corrigée garde le décalage fautif, le bon décalage est cherché (0, 4, 8… espaces).
- Les cases `[[…]]` sont découpées comme dans le moteur (`[[t[0]]]` reste entier).

### Essayer sans connexion : Python local

Le moteur charge Python 3.13 (Pyodide 0.29.3) depuis jsDelivr au premier clic. Pour les essais hors ligne, servez une copie locale de Pyodide et déclarez-la **avant** le moteur, ou sur `<main>` :

```html
<script>window.TD_PYODIDE = 'http://localhost:8000/pyodide/pyodide.js';</script>
<!-- ou --> <main class="td" data-pyodide="http://localhost:8000/pyodide/pyodide.js" …>
```

Avec Playwright : `context.add_init_script("window.TD_PYODIDE='http://localhost:8000/pyodide/pyodide.js'")`. Ne laissez jamais cette ligne dans une page publiée.

## 1. Créer le squelette

À la racine du dépôt :

```
python3 -I charte/nouveau-td.py nsi1/fichiers/boucles-td1 \
  --id nsi1-boucles-td1 --titre "Les boucles \`for\` et \`while\`" \
  --niveau "1re NSI" --chapitre "Programmer en Python" \
  --quiz "https://babash.github.io/quizz-nsi/revision.html?cours=conditions-boucles" \
  --accroche "Répéter des instructions"
```

| Option | Ce qu'elle fait |
|---|---|
| `--id` | identifiant **unique et stable** (minuscules, chiffres, tirets). Il sert au stockage sur l'appareil, au futur compte commun et à la cachette du margouillat. Ne le changez plus ensuite. |
| `--titre` | le titre ; un mot entre accents graves devient du code (`` `while` ``). Court : il tient sur une ligne du bandeau (26 caractères environ, en capitales). |
| `--niveau`, `--chapitre` | la ligne au-dessus du titre. Ensemble, **40 caractères au plus** (au-delà, elle passe à la ligne et le bandeau grandit, sur papier aussi). |
| `--bandeau` | facultatif : force le paysage. Sans lui, le bandeau est **tiré de l'identifiant** (le même sur toutes les branches ; voir § 2). |
| `--quiz` | l'adresse du cours-quiz du chapitre : le QR code est calculé **hors ligne** (avec `assets/qrcode-generator.js`). **Sans `--quiz`, pas de QR code** : c'est le cas d'un chapitre sans cours-quiz. |
| `--accroche` | une ligne sous le titre, facultative (25 caractères environ). |

| `--controle` | variante de contrôle : bandeau de 20 mm, puce « Contrôle ». |
| `--genre` | la puce du bandeau : `TD` (défaut), `DM`, `TP`, `Activité`, `Séance`. |
| `--auteurs` | tous les noms, séparés par « ; » (pied de page et pied de chaque page imprimée). |
| `--feuille`, `--pages-max` | numéro de la feuille (2, 3… : bande de titre fine sur papier) ; pages A4 admises (4 par défaut). |
| `--remplacer`, `--cachette` | écraser une page existante ; forcer la cachette du margouillat (`b1` à `b4`, `memo`, `pied`). |

**Textes trop longs.** Au-delà de ces longueurs, rien n'est coupé ni recouvert : le titre est imprimé plus petit (au-delà de 26 caractères), puis passe sur deux lignes (au-delà de 31), la ligne du niveau et du chapitre passe à la ligne, et **le bandeau grandit** (sur papier aussi). `nouveau-td.py` prévient (« Attention : … ») et `imprimer-td.py` signale un bandeau de plus de 28 mm (20 mm pour un contrôle) ; il refuse un texte coupé, sorti du bandeau (un mot insécable trop long compris : son étendue réelle est mesurée) ou qui recouvre le QR code, « Nom et prénom » ou les objectifs. Raccourcissez plutôt.

Le script écrit `index.html` dans le dossier, avec les bons chemins vers `assets/`, le lien « Code source sur GitHub » et le pied de page complet.

## 2. Le bandeau : il tourne

**Aucune correspondance entre bandeau et chapitre** : les quatre bandeaux tournent. Sans `--bandeau`, `nouveau-td.py` tire le bandeau **de l'identifiant** (le même sur toutes les branches, sans regarder le dépôt) ; une page qui existe déjà garde le sien. Après les fusions, `charte/reattribuer-bandeaux.py --appliquer` rééquilibre exactement tous les TD. `--bandeau N` le force, si besoin.

| N° | Paysage (aucun nom de lieu : les élèves devinent) | Fichiers |
|---|---|---|
| 1 | le cône vu de la baie, et son téléphérique de pirogues | `assets/td/bandeau-1.svg` |
| 2 | l'îlot de sable blanc, et le feu rouge dans le lagon | `assets/td/bandeau-2.svg` |
| 3 | la ville, le mont et la barge-drone | `assets/td/bandeau-3.svg` |
| 4 | le baobab de plage, ses paraboles et ses lampions | `assets/td/bandeau-4.svg` |

Chaque bandeau a sa variante de 20 mm pour les contrôles (`bandeau-N-controle.svg`) et ses versions `-obscur` pour l'écran obscur. Ils se refont avec `python3 -I charte/bandeaux-td.py`.

**Le margouillat** (vert, petite turbine au bout de la queue) se cache tout seul : dans le bandeau, sur le cadre du mémo ou sur le trait du pied de page, à une place tirée de l'identifiant ; le script évite une cachette déjà prise par un autre TD du même bandeau. Il n'entre jamais dans un exercice. Ne le supprimez pas.

## 3. Écrire le TD, pas à pas

1. **L'objectif** : une phrase, un verbe d'action (« lire et écrire une boucle… »).
2. **Les critères de réussite** : 3 à 5 « Je sais… », vérifiables par l'élève.
3. **La durée** et le nombre de questions (`45 minutes · 11 questions et 1 bonus ★`).
4. **Les parties** : `<h2 class="td-partie">1. …</h2>`, du plus simple au plus dur. Le moteur numérote les questions.
5. **Les questions** : remplacez les exemples du squelette. Chaque question est une `<section class="td-q" data-type="…" id="qN">`, avec :
   - `<p class="td-consigne">` : la consigne, courte (tutoiement, langage inclusif) ;
   - `<pre class="td-code">` : le code affiché (écrire `&lt;` et `&gt;`) ;
   - `<p class="td-aide">` : **les coups de pouce**, du plus léger au plus précis (1 à 3), montrés un par un ;
   - `<div class="td-correction">` : **la correction**, qui explique (proposée après deux essais) ;
   - `<p class="td-retour" data-si="72">` : un retour ciblé sur une erreur typique.
6. **Le mémo** : l'essentiel en 3 lignes au plus.

Les types de questions du moteur (`data-type`) :

| Type | Ce qu'on écrit | Correction |
|---|---|---|
| `sortie` | `pre.td-code` + `<pre class="td-attendu">` (la sortie exacte) | ligne par ligne, casse et espaces tolérés |
| `courte` | `data-reponse="60\|soixante"` ; `data-comparer="code"` pour du code ; `data-verifier="sortie"` si la réponse est ce qu'affiche le programme | casse, accents, espaces, guillemets, `5` = `5.0` = `5,0` |
| `qcu` | `<ul class="td-options">` : un `<li data-juste>`, les autres avec `data-retour="pourquoi c'est faux"` | une seule bonne réponse |
| `cases` | la même liste, plusieurs `data-juste` | toutes les bonnes, aucune fausse |
| `trous` | dans le code : `range([[1]], [[11]])` ; plusieurs réponses : `[[i\|k]]` | seules les cases fausses sont marquées |
| `ordre` | `<ol class="td-lignes">` **dans l'ordre juste** (4 espaces par niveau) | le moteur mélange, toujours de la même façon |
| `erreur` | `pre.td-code` + `pre.td-erreur` + `data-fichier="taxi.py" data-ligne="3" data-reponse="ligne corrigée"` | la bonne ligne, puis la ligne corrigée |
| `code` | `<pre class="td-depart">` + `pre.td-attendu` (un ou plusieurs, avec `data-entrees`) et/ou `<script type="text/x-python" class="td-tests">` + `<pre class="td-code" data-verifier="correction">` | exécuté par Python 3.13, chargé au clic ; **obligatoire** avec `data-code="obligatoire"` sur `<main>` (défaut des nouvelles pages), `data-bonus` pour un bonus |
| `libre` | `data-lignes="4"` (souvent avec `data-support="papier"`) | jamais corrigée ni comptée : des lignes sur papier, un brouillon et la correction à l'écran |

« Trouve l'erreur » : **toujours le vrai message de Python 3.13**, en entier (« Did you mean » compris). Pour l'obtenir : écrire le programme dans un fichier du nom de `data-fichier`, puis `python3 -I charte/verifier-td.py --erreur taxi.py`, et copier la sortie telle quelle dans `pre.td-erreur`. Le moteur la colore et l'étiquette « erreur ».

Le contenu : exemples variés de la vie réelle des élèves (la barge, le bouchon, le marché, les marées… et d'ailleurs), prénoms variés sans nom de famille, aucune marque, aucune arme ; aucune question de genre ; on ne promeut aucune religion, sans en faire un problème ; **ni personnage ni récit** sur une feuille. Jamais de note ni de score : le moteur affiche une jauge d'avancement, puis « Feuille validée ».

## 4. Vérifier et faire le PDF

```
python3 -I charte/verifier-td.py nsi1/fichiers/boucles-td1/index.html
python3 -m http.server 8000            # à la racine du dépôt, dans un autre terminal
python3 -I charte/imprimer-td.py http://localhost:8000/nsi1/fichiers/boucles-td1/index.html nsi1/fichiers/boucles-td1/td.pdf
```

`verifier-td.py` exécute chaque programme et compare (sorties, messages d'erreur mot pour mot, corrections). `imprimer-td.py` imprime **la feuille vierge** (il remplit tout, déclenche l'impression et vérifie qu'aucune réponse, aucun coup de pouce ni aucune correction n'est dans le PDF), puis contrôle la mise en page : 4 pages au plus, aucun texte sous 10 pt, aucune ligne de code coupée, rien hors de la page, aucune requête hors du site, seules les polices du site dans le PDF, et chaque élément à remplir tracé d'un trait plein d'au moins 0,5 pt et 7:1.

Sur papier, l'en-tête demande **« Nom et prénom » et « Classe »** (la feuille se rend à l'enseignant·e). La page en ligne ne demande rien.

## 5. Liste de contrôle avant de livrer

- [ ] `verifier-td.py` : « tout est juste ».
- [ ] TD à plusieurs feuilles : `python3 -I charte/numeroter-feuilles.py <dossier>` (passe finale), puis `--verifier` : « Numéros à jour ».
- [ ] `imprimer-td.py` : « PDF vierge : oui », **4 pages A4 au plus par feuille** (une fiche : 2 pages ; `data-pages-max` pour un exercice de bac) ; un TD à plusieurs feuilles : toutes les adresses, un seul PDF.
- [ ] **10 pt au moins** partout sur papier (contrôlé par le script).
- [ ] **Code : 80 caractères au plus par ligne** dans une question (mesuré : 80 colonnes de JetBrains Mono à 10 pt sur A4) ; **35 au plus** dans une option de `qcu` ou `cases` (les options s'impriment sur deux colonnes). Visez 70 pour garder de la marge ; une ligne trop longue est signalée (« ligne de code coupée »).
- [ ] Pas de débordement : la page à **320 px** sans défilement horizontal, en clair et en obscur ; puis 768 et 1440 px.
- [ ] Contraste : ne changez aucune couleur dans la page ; tout est dans `assets/td-en-ligne.css` (7:1 pour le texte et le code, vérifié).
- [ ] Rien d'essentiel par la couleur seule (une consigne ne dit jamais « la ligne rouge »).
- [ ] Le **margouillat** est présent (`data-cachette`) ; le **QR code** pointe vers le bon cours-quiz (ou il n'y en a pas).
- [ ] **Sur papier, tout ce que l'élève remplit se voit nettement**, même en noir et blanc sur une imprimante fatiguée : lignes de réponse, cases du code, cases à cocher et ronds, cadre de l'éditeur, « Nom et prénom » et « Classe » ont un trait **plein, noir, de 0,5 pt au moins** (contrôlé par `imprimer-td.py`). Le rose et le cyan ne servent qu'au décor, jamais à une case à remplir ni à une information.
- [ ] Le **pied de page** : auteur, licence CC BY-SA 4.0, « conçu avec l'aide de l'IA », « Code source sur GitHub ».
- [ ] La **feuille imprimée est vierge** : ouvrez le PDF et regardez-le.
- [ ] `python3 -I .github/gardien/caracteres.py --diff origin/main...HEAD` : aucun caractère invisible.
