# Les banques d'exercices du Calendrier des vacances

Cette page est pour l'Atelier qui écrit la banque d'un **thème**. Un thème est un chapitre (« Listes et dictionnaires ») ou une notion plus fine (« Les boucles », « Le binaire »). L'enseignant·e coche librement plusieurs thèmes pour un calendrier, quel que soit le niveau de sa classe (une terminale peut recevoir des thèmes de première), et les cases alternent entre eux, tour à tour. Une case du calendrier est un exercice : un mini-jeu de **10 minutes au plus**, en **3 niveaux** (Facile, Moyen, Costaud). L'élève choisit son niveau, et un niveau suffit pour valider la case.

**État au 24/11/2026 :** 9 banques de 30 exercices (dont `snt-internet-web`, la première sans programme : `langage` « aucun »), **270 exercices** (le contrôle complet : 0 erreur). **Le moteur joue 12 types de mini-jeux** depuis le 24/11 (T135). Les arbres s'écrivent de deux façons, que les élèves doivent connaître toutes les deux (décision de l'enseignant du 20/11) : la classe courte `Noeud(v, g, d)` et la classe du cours `ArbreBinaire(valeur, gauche, droit)` ; un thème qui parle d'arbres les fait alterner.

## Les fichiers

| Fichier | Rôle | Qui le modifie |
|---|---|---|
| `exercice.schema.json` | Le format (JSON Schema) | Architecte |
| `catalogue.json` | La liste des thèmes, leur nature (chapitre ou notion), leurs niveaux indicatifs et leur statut (`prevu`, `en_cours`, `pret`) | Architecte |
| `<thème>.json` | La banque d'un thème | l'Atelier de ce thème, sur sa branche `atelier/t105-<thème>` |
| `<thème>.js` | La même banque, fabriquée par `--bundle` | personne à la main |
| `../../scripts/tests/calendrier/exemple-boucles.json` | **Le gabarit des six premiers types** : 6 exercices justes, un de chaque type, en 3 niveaux | Architecte |
| `../../scripts/tests/calendrier/exemple-nouveaux-types.json` | **Le gabarit des six types ajoutés le 24/11** (trace, combien, paniers, intrus, memo, bits) : 6 exercices justes, en 3 niveaux | Architecte |

Un Atelier ne touche **qu'à son fichier**. Il ne modifie ni `catalogue.json` ni le schéma : il demande dans son rapport.

## Le contrôle, à lancer avant chaque envoi

```sh
python3 scripts/calendrier_exercices.py --fichier calendrier/exercices/<thème>.json
```

- **Il exécute chaque programme** et compare ce qu'il affiche à ce que l'exercice annonce :
  - une seule option juste en « prévoir la sortie » ;
  - en « trouver l'erreur », les mauvaises corrections sont vraiment fausses, et le programme fautif ne donne pas déjà le bon résultat ;
  - en « compléter », chaque mauvaise pièce change le résultat.
- **Il refuse** :
  - les caractères invisibles et les tabulations ;
  - `input`, `random` et les fichiers, car le résultat doit être le même à chaque exécution ;
  - en SQL, une requête qui renvoie plusieurs lignes sans `ORDER BY`.
- **Zéro erreur avant d'envoyer.** Un avertissement se relit, mais ne bloque pas.

## L'en-tête du fichier

```json
{
  "$schema": "./exercice.schema.json",
  "theme": { "id": "py-boucles", "titre": "Les boucles", "nature": "notion", "niveaux": ["nsi-1re"],
             "langage": "python", "programme": ["nsi-1re-2019.langages.constructions-elementaires"], "notions": ["prog.boucle"] },
  "exercices": [ … ]
}
```

L'ancienne forme (`"chapitre"` à la place de `"theme"`, `"niveau"` à la place de `"niveaux"`) est encore acceptée, avec un avertissement : il suffit de renommer les deux clés et d'ajouter `"nature"`.

## Les libellés : ceux des référentiels du site

**« Le même choix de libellé partout »** (enseignant·e, 24/11). Un thème reprend les identifiants et les libellés des référentiels du site (`donnees/referentiels/`) :
- `programme` : des identifiants de `programmes.json`, et le titre d'un chapitre suit l'intitulé du programme (« Structures de données », « Internet », « Le Web ») ;
- `notions` : des identifiants de `notions.json` (le contrôle du site les connaît), et le titre d'une notion suit son libellé (`libelle`) ;
- l'**identifiant** d'un thème (`py-boucles`, `snt-internet-web`…) ne change jamais, même si son titre change : la base le garde dans chaque case (`vacances.cases.theme`). Seul le `titre` peut se rapprocher d'un libellé.
- Un nouveau thème choisit d'abord son titre dans les référentiels ; un écart se justifie dans le rapport de l'Atelier.

## Les règles d'un thème

1. **De 8 à 30 exercices** (le compte de `catalogue.json` se remet à jour avec `python3 scripts/calendrier_exercices.py --catalogue`), numérotés `<thème>-001`, `-002`… dans l'ordre : **30 de préférence**, notion comme chapitre, pour qu'un thème coché seul remplisse les 30 jours des vacances de Noël sans révision ; une notion peut commencer à 8, un chapitre à 15, et l'on complète ensuite jusqu'à 30. Les thèmes alternent : un calendrier de 30 jours avec 3 thèmes demande 10 exercices à chacun. C'est l'ordre des cases : l'exercice 1 sert à la première case du thème. Si un calendrier demande plus d'exercices que la banque n'en a, la page enseignant·e le signale en rouge avant d'enregistrer et demande confirmation ; les exercices reviennent alors dans l'ordre, en révision (l'élève voit « Révision »), et aucune case ne reste vide.
   - Un exercice publié ne change jamais de rang ni d'identifiant.
   - On peut corriger un exercice, et on ajoute toujours à la fin.
2. **Les types tournent.** Le moteur sait jouer **12 types** (voir plus bas). Deux exercices de suite n'ont jamais le même type, et six exercices de suite en couvrent au moins cinq. Ordre conseillé, à adapter au thème : vraifaux, sortie, associer, erreur, completer, ordre, puis un des nouveaux (trace pour une boucle, combien pour un nombre de tours, paniers pour classer, intrus pour une notion d'ensemble, memo pour du vocabulaire, bits pour le binaire).
3. **La difficulté monte doucement** : le cœur du thème d'abord, puis les combinaisons et les révisions. L'exercice 1 se réussit au niveau Facile en 2 minutes.
   - **Pas de pièges, même au niveau Costaud** (règle de l'enseignant du 24/11) : rien qui repose sur une bizarrerie du langage ou un détail hors programme, non pertinent pour le bac ; le but est de mettre les élèves en confiance. Costaud = un programme un peu plus long ou une réponse à taper.
4. **Les trois niveaux d'un exercice portent sur la même notion :**

   | Niveau | Durée | Questions | Forme |
   |---|---|---|---|
   | Facile | 2 à 3 min | 3 à 4 | 4 propositions, programmes de 1 à 3 lignes, coups de pouce directs |
   | Moyen | 3 à 5 min | 3 à 4 | programmes de 3 à 6 lignes |
   | Costaud | 4 à 8 min | 3 à 4 | « sortie » à taper, distracteurs proches, programmes à plusieurs blocs |

   Pour un « associer », une question compte de 3 à 6 paires. Pour un « vraifaux », un niveau compte 5 ou 6 affirmations. Pour un « ordre », 2 programmes par niveau.
5. **Les distracteurs viennent d'erreurs réelles.**
   - Prendre les difficultés recensées dans le thésaurus des notions (`donnees/referentiels/notions.json`, champ `difficultes`) et les erreurs typiques : `range` qui commence à 1, l'oubli du dernier tour, `=` et `==`, un indice hors de la liste, un `return` dans la boucle, une jointure sans condition…
   - Jamais un distracteur absurde.
6. **Chaque retour explique, sans donner la réponse.**
   - Une mauvaise option : l'erreur de raisonnement qu'elle trahit (« range s'arrête juste avant la fin »).
   - Une bonne option : pourquoi elle est juste.
   - Les coups de pouce vont du plus léger au plus fort, sans jamais être la réponse. **Ils n'apparaissent qu'après deux essais faux** sur la question (l'échelle d'aide de l'enseignant, 25/11 : essayer d'abord, seul·e ou à deux, puis un indice, puis la correction) : un coup de pouce dit ce qui n'a pas marché ou où regarder, pas quoi répondre.
   - Après trois essais faux, la page propose « Voir la réponse » pour `sortie` (à taper), `erreur`, `completer`, `ordre`, `associer`, `trace`, `combien` et `bits` : elle montre la réponse et l'`explication`, puis la question revient une fois à la fin de la partie. L'`explication` doit donc se lire seule, à côté de la réponse (réglage : `CV.ECHELLE` dans `calendrier/jeux.js`).
   - Une réponse à taper (`reponse`) s'écrit exactement comme `print` l'affiche. La page accepte la même valeur écrite autrement : les espaces autour des virgules, des crochets, des parenthèses et des accolades, les guillemets simples ou doubles, une virgule finale dans une liste. Elle refuse une autre casse (`true` pour `True`), des guillemets autour d'un texte affiché, une espace retirée entre deux mots ou deux nombres ; pour la casse et les guillemets, elle le dit à l'élève (« Presque : … »). Inutile, donc, de prévoir des variantes ; mais une réponse qui peut s'écrire de deux façons vraiment différentes (« 2 1 » ou « 2, 1 ») est à éviter.
7. **L'explication est le corrigé**, montré à J + 3 : une ou deux phrases, le raisonnement plutôt que le résultat.
8. **L'écriture.**
   - **On tutoie l'élève partout** : consignes, retours, coups de pouce (décision de l'enseignant, 25/11). Le « But : » d'un `erreur`, d'un `completer` ou d'un `ordre` décrit ce que fait le programme, à l'infinitif (« But : Afficher la moyenne »).
   - Les phrases sont courtes, et le mot technique anglais est expliqué.
   - Le langage inclusif est complet.
   - Les prénoms dans les programmes sont variés et épicènes (Kenza, Ibrahim, Soilihi, Naïma, Lou, Sam…) ; jamais un nom d'élève réel.
   - Le contexte de Mayotte se met par petites touches, sans cliché : le taxi-brousse, la barge, le marché de Mamoudzou, la météo, un club de football.
9. **Le code.**
   - Python 3, indentation de 4 espaces, des noms de variables en français sans accent.
   - Des programmes courts : 12 lignes au plus. **Une ligne de 28 caractères au plus (indentation comprise) tient sur un téléphone de 320 px** (33 à 360 px, 59 sur une tablette). Au-delà, la page replie la ligne sans rien cacher : la suite est décalée et marquée d'une flèche ↳, les guides d'indentation descendent avec elle, et une chaîne courte n'est jamais coupée. Le repli reste plus lent à lire : on coupe soi-même une ligne longue quand le langage le permet (`JOIN … ON …` sur deux lignes, une condition SQL par ligne avec `AND` en tête), et on évite qu'un trou ou ce que la question enseigne tombe au milieu d'un repli. Le script `scripts/calendrier_affichage.py` affiche chaque question à 320 px, à chaque étape, et liste ce qui serait caché.
   - SQL : SQLite, avec la base d'exemple du thème (`base_sql`, 3 tables, 30 lignes au plus), des mots-clés en majuscules et `ORDER BY` dès qu'il peut y avoir plusieurs lignes.
   - En « ordre », une seule disposition doit être juste : deux lignes indépendantes (`a = 5` et `b = 8`) se réunissent sur une seule (`a, b = 5, 8`).
10. **`relu`** reste `false`. L'enseignant·e passe à `true` après relecture, et la page enseignant·e signale un calendrier qui contient des exercices non relus.

## Les douze types

Les six premiers ont un exemple juste dans `exemple-boucles.json`, les six suivants dans `exemple-nouveaux-types.json`. Tous se jouent au doigt à 320 px (on touche, jamais de glisser-déposer obligatoire) et au clavier, les retours sont annoncés aux lecteurs d'écran, et aucun chrono ne fait perdre.

### Les six premiers

| Type | Champs d'une question | Ce que le contrôle vérifie |
|---|---|---|
| `vraifaux` | `texte`, `reponse` (true ou false), `explication`, et au besoin `code` et `verifier` : en Python, une expression qui doit valoir `reponse` (`s == 10`) ; en SQL, une requête d'une seule valeur, vraie si elle ne vaut ni 0 ni NULL (`SELECT COUNT(*) = 3 FROM tortue`) | `verifier` après le code |
| `sortie` | `code`, puis soit `options` (4, « / » sépare les lignes), `bonne` et `retours` (4), soit `reponse` (à taper) et `explication` ; `aides` | une seule option juste, ou la réponse exacte |
| `associer` | `consigne`, `paires` [[gauche, droite]…], `explication`, `executer: true` si la gauche est un programme | avec `executer`, ce que chaque programme affiche (lignes jointes par « , ») |
| `erreur` | `but` (sans le message), `lignes`, `ligne` (indice de la ligne fausse, à partir de 0), `corrections` (3), `bonne`, `affiche` (sortie du programme corrigé), `explication`, `aides`, et **un seul** champ pour ce que montre le programme fautif : `message` (le message réel : « IndexError: list index out of range », « Error: near "plage": syntax error »), `affiche_fautif` (sa sortie, pour une erreur de logique ; vide s'il n'affiche rien) ou `boucle_infinie: true` | la correction juste donne `affiche` ; les autres et le programme fautif, non ; le programme fautif donne bien `message`, `affiche_fautif` ou ne s'arrête pas |
| `ordre` | `but`, `lignes` dans le bon ordre (toutes différentes), `affiche`, `aides` | le programme dans l'ordre donne `affiche`, et **aucune autre disposition** ne le donne (toutes les permutations sont essayées jusqu'à 8 lignes) |
| `completer` | `but`, `lignes` avec `{0}`, `{1}`…, `trous` [{`options`, `bonne`}], `affiche`, `explication`, `aides` | les bonnes pièces donnent `affiche` ; chaque mauvaise le change |

### Les six types ajoutés le 24/11 (T135)

| Type | Comment on joue | Champs d'une question | Ce que le contrôle vérifie |
|---|---|---|---|
| `trace` | Remplir un petit tableau : la valeur des variables à la fin de chaque tour | `code`, `colonnes` (3 variables au plus), `tours` (une ligne par tour, une valeur par colonne, écrite comme `print` l'affiche), `visibles` (cases déjà remplies, `[ligne, colonne]`), `depart` (vrai : une première ligne « Avant la boucle »), `boucle` (indice de la ligne suivie ; par défaut la première `for` ou `while`), `explication`, `aides` | il exécute le code et relève les variables **à chaque retour sur la ligne de la boucle** : le tableau doit être exactement celui-là |
| `combien` | Un compteur − et + (et −10, +10 si l'écart min-max atteint 20), au doigt ou avec les flèches | `texte`, `code` (facultatif), `reponse` (entier), `min`, `max`, `depart` (jamais la réponse), `verifier`, `explication`, `aides` | avec `verifier` : l'expression, évaluée après le code, vaut `reponse` ; la variable `sortie` contient ce que le code a affiché (`sortie.count("*")`) |
| `paniers` | Chaque carte a deux boutons, un par panier ; une erreur est dite tout de suite | `consigne`, `paniers` (2 noms courts), `cartes` [{`texte`, `panier` (0 ou 1), `retour`}], `code_cartes` (vrai : les cartes sont du code), `explication` | 4 à 8 cartes toutes différentes, les deux paniers servent |
| `intrus` | Toucher l'intrus, puis choisir pourquoi (QCU) | `consigne`, `elements` (3 à 5), `intrus` (indice), `executer`, `retours` (facultatif : un par élément), `pourquoi` {`options`, `bonne`, `retours`}, `explication` | avec `executer` : tous les programmes affichent la même chose, sauf l'intrus |
| `memo` | Retourner deux cartes ; une paire trouvée reste visible ; le nombre de coups est montré, sans chrono | `consigne`, `paires` (3 à 6, textes courts : une carte fait le tiers de 320 px), `executer`, `explication` | les 2 × n textes sont tous différents ; avec `executer`, chaque programme affiche sa carte |
| `bits` | Toucher les ampoules d'un nombre binaire (poids écrits au-dessus, groupés par 4) | `texte`, `cible` (« 13 », « 2F », « #FF8000 »), `base` (`10`, `16` ou `rvb`), `reponse` (les bits, 4 à 24), `poids` (faux : poids cachés, niveau Costaud), `valeur` (vrai : la valeur s'affiche en direct, niveau Facile), `explication`, `aides` | les bits valent la cible ; jamais tous éteints (la page commence ainsi) |

Une question de chaque, juste (le contrôle passe) :

```json
{ "code": "s = 0\nfor i in range(3):\n    s = s + i", "colonnes": ["i", "s"],
  "tours": [["0", "0"], ["1", "1"], ["2", "3"]], "visibles": [[0, 0]],
  "aides": ["Au premier tour, i vaut 0 : s devient 0 + 0."],
  "explication": "s accumule 0, puis 1, puis 2 : il vaut 0, 1, puis 3." }
```

```json
{ "texte": "Combien d'étoiles ce programme affiche-t-il ?",
  "code": "for i in range(3):\n    for j in range(4):\n        print(\"*\", end=\"\")\n    print()",
  "reponse": 12, "min": 0, "max": 30, "verifier": "sortie.count(\"*\")",
  "aides": ["La boucle intérieure fait 4 tours à chaque tour de la boucle extérieure."],
  "explication": "3 tours dehors × 4 tours dedans : 12 étoiles, sur 3 lignes." }
```

```json
{ "consigne": "Range chaque boucle dans le bon panier.", "paniers": ["Bornée", "Non bornée"], "code_cartes": true,
  "cartes": [ { "texte": "for i in range(5):", "panier": 0 },
              { "texte": "while n > 0:", "panier": 1 },
              { "texte": "for c in \"barge\":", "panier": 0, "retour": "Une chaîne a un nombre fixe de caractères." },
              { "texte": "while reponse != \"oui\":", "panier": 1 } ],
  "explication": "for parcourt une suite connue ; while répète tant qu'une condition est vraie." }
```

```json
{ "consigne": "Trois programmes affichent la même chose. Lequel est l'intrus ?", "executer": true,
  "elements": ["for i in range(3):\n    print(i)", "for i in range(0, 3):\n    print(i)",
               "for i in range(1, 4):\n    print(i)", "i = 0\nwhile i < 3:\n    print(i)\n    i = i + 1"],
  "intrus": 2,
  "pourquoi": { "options": ["Il commence à 1 au lieu de 0.", "Il utilise une boucle while.", "Il affiche 4 nombres."], "bonne": 0,
                "retours": ["Juste : range(1, 4) donne 1, 2, 3.", "Le while affiche bien 0, 1, 2.", "range(1, 4) donne 3 nombres."] },
  "explication": "Les trois autres affichent 0, 1, 2." }
```

```json
{ "consigne": "Retrouve chaque range et ses valeurs.", "executer": true,
  "paires": [["print(*range(3))", "0 1 2"], ["print(*range(1, 3))", "1 2"], ["print(*range(2))", "0 1"]],
  "explication": "range(n) commence à 0 ; range(a, b) commence à a ; les deux s'arrêtent avant la fin." }
```

```json
{ "texte": "Allume les bits de la couleur #FF8000 (orange) : rouge, vert, bleu.", "cible": "#FF8000", "base": "rvb",
  "reponse": "111111111000000000000000", "poids": false,
  "aides": ["Chaque couleur a 8 bits : FF, puis 80, puis 00."],
  "explication": "FF = 11111111, 80 = 10000000, 00 = 00000000." }
```

**L'essai dans le navigateur.** `python3 -I -B scripts/tests/test_calendrier_jeux.py` joue chaque niveau des deux gabarits avec le vrai moteur, dans Chromium : une erreur volontaire (le retour doit être annoncé), puis la bonne réponse au doigt et au clavier, le corrigé, la reprise d'une partie gardée, 320 px en clair et en obscur, et l'animation coupée si l'appareil demande moins de mouvement. Un Atelier peut y ajouter sa banque pour la jouer d'un bout à l'autre.

## Les compléments

- **Le message, toujours.** Une « trouver l'erreur » montre sous le code ce que fait le programme fautif (règle de l'enseignant du 20/11) : le message réel, sa sortie, ou « ne s'arrête jamais ». Le `but` dit seulement ce que doit faire le programme. `scripts/calendrier_migrer_erreurs.py --ecrire` range ces champs à partir de l'exécution.
- **SQL.** Chaque programme s'exécute sur une base neuve : `PRAGMA foreign_keys = ON`, puis `base_sql` en entier. Un programme peut enchaîner des mises à jour (`INSERT`, `UPDATE`, `DELETE`) puis un `SELECT` : on affiche le résultat de la dernière instruction. La page montre les tables de `base_sql`, repliables, au-dessus de chaque question : après toute modification de `base_sql`, relancer `python3 scripts/calendrier_exercices.py --tables` (le contrôle refuse un fichier `<thème>.tables.json` pas à jour).
- **Un arbre binaire.** Une question (sauf « associer ») peut porter un champ `arbre` : `{"v": 8, "g": {"v": 3}, "d": {"v": 10, "d": {"v": 14}}}` (`v` : étiquette de 6 caractères au plus ; `g` et `d` : sous-arbres). La page le dessine au-dessus de la question, lisible à 320 px jusqu'à 31 nœuds.
- **Les places.** Le contrôle avertit quand la bonne réponse est toujours au même endroit : la ligne fausse toujours la dernière, la bonne proposition toujours la première, toutes les affirmations vraies. La page mélange les propositions, mais le corrigé et la relecture les lisent dans l'ordre.

## La méthode conseillée

1. **Écrire d'abord le plan des exercices**, dans le rapport ou en tête du travail. Pour chacun : le rang, le type, la notion, et l'idée des trois niveaux.
2. **Écrire la banque en Python**, avec de petites fonctions qui fabriquent les questions. On peut faire exécuter un programme pour obtenir sa sortie exacte, mais **on écrit les distracteurs et les retours à la main**. Puis on écrit le JSON. Le script de fabrication reste dans le dossier temporaire de l'Atelier : seul le JSON va dans le dépôt.
3. **Lancer le contrôle** jusqu'à zéro erreur.
4. **Relire à voix haute trois exercices au hasard**, comme un·e élève de seconde dont le français est une langue seconde.
5. **Pousser `atelier/t105-<thème>`.** Le rapport donne le nombre d'exercices et de questions, la sortie du contrôle, et les points à relire par l'enseignant·e.
