# Les banques d'exercices du Calendrier des vacances

Cette page est pour l'Atelier qui écrit la banque d'un **thème**. Un thème est un chapitre (« Listes et dictionnaires ») ou une notion plus fine (« Les boucles », « Le binaire »). L'enseignant·e coche librement plusieurs thèmes pour un calendrier, quel que soit le niveau de sa classe (une terminale peut recevoir des thèmes de première), et les cases alternent entre eux, tour à tour. Une case du calendrier est un exercice : un mini-jeu de **10 minutes au plus**, en **3 niveaux** (Facile, Moyen, Costaud). L'élève choisit son niveau, et un niveau suffit pour valider la case.

## Les fichiers

| Fichier | Rôle | Qui le modifie |
|---|---|---|
| `exercice.schema.json` | Le format (JSON Schema) | Architecte |
| `catalogue.json` | La liste des thèmes, leur nature (chapitre ou notion), leurs niveaux indicatifs et leur statut (`prevu`, `en_cours`, `pret`) | Architecte |
| `<thème>.json` | La banque d'un thème | l'Atelier de ce thème, sur sa branche `atelier/t105-<thème>` |
| `<thème>.js` | La même banque, fabriquée par `--bundle` | personne à la main |
| `../../scripts/tests/calendrier/exemple-boucles.json` | **Le gabarit** : 6 exercices justes, un de chaque type | Architecte |

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

## Les règles d'un thème

1. **De 8 à 30 exercices**, numérotés `<thème>-001`, `-002`… dans l'ordre : une notion en a de 8 à 12, un chapitre de 15 à 30. Les thèmes alternent : un calendrier de 30 jours avec 3 thèmes demande 10 exercices à chacun. C'est l'ordre des cases : l'exercice 1 sert à la première case du thème. Si un calendrier demande plus d'exercices que la banque n'en a, la page enseignant·e le signale avant la création.
   - Un exercice publié ne change jamais de rang ni d'identifiant.
   - On peut corriger un exercice, et on ajoute toujours à la fin.
2. **Les types tournent.** Six exercices de suite couvrent les 6 types. Ordre conseillé, répété : vraifaux, sortie, associer, erreur, completer, ordre.
3. **La difficulté monte doucement** : le cœur du thème d'abord, puis les combinaisons et les révisions. L'exercice 1 se réussit au niveau Facile en 2 minutes.
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
   - Les coups de pouce vont du plus léger au plus fort, sans jamais être la réponse.
7. **L'explication est le corrigé**, montré à J + 3 : une ou deux phrases, le raisonnement plutôt que le résultat.
8. **L'écriture.**
   - Les consignes sont impersonnelles, comme au bac ; les retours tutoient.
   - Les phrases sont courtes, et le mot technique anglais est expliqué.
   - Le langage inclusif est complet.
   - Les prénoms dans les programmes sont variés et épicènes (Kenza, Ibrahim, Soilihi, Naïma, Lou, Sam…) ; jamais un nom d'élève réel.
   - Le contexte de Mayotte se met par petites touches, sans cliché : le taxi-brousse, la barge, le marché de Mamoudzou, la météo, un club de football.
9. **Le code.**
   - Python 3, indentation de 4 espaces, des noms de variables en français sans accent.
   - Des programmes courts : 12 lignes au plus, 50 caractères par ligne de préférence, car la page sert au téléphone.
   - SQL : SQLite, avec la base d'exemple du thème (`base_sql`, 3 tables, 30 lignes au plus), des mots-clés en majuscules et `ORDER BY` dès qu'il peut y avoir plusieurs lignes.
   - En « ordre », une seule disposition doit être juste : deux lignes indépendantes (`a = 5` et `b = 8`) se réunissent sur une seule (`a, b = 5, 8`).
10. **`relu`** reste `false`. L'enseignant·e passe à `true` après relecture, et la page enseignant·e signale un calendrier qui contient des exercices non relus.

## Les six types (voir le gabarit pour un exemple juste de chacun)

| Type | Champs d'une question | Ce que le contrôle vérifie |
|---|---|---|
| `vraifaux` | `texte`, `reponse` (true ou false), `explication`, et au besoin `code` et `verifier` : en Python, une expression qui doit valoir `reponse` (`s == 10`) ; en SQL, une requête d'une seule valeur, vraie si elle ne vaut ni 0 ni NULL (`SELECT COUNT(*) = 3 FROM tortue`) | `verifier` après le code |
| `sortie` | `code`, puis soit `options` (4, « / » sépare les lignes), `bonne` et `retours` (4), soit `reponse` (à taper) et `explication` ; `aides` | une seule option juste, ou la réponse exacte |
| `associer` | `consigne`, `paires` [[gauche, droite]…], `explication`, `executer: true` si la gauche est un programme | avec `executer`, ce que chaque programme affiche (lignes jointes par « , ») |
| `erreur` | `but` (sans le message), `lignes`, `ligne` (indice de la ligne fausse, à partir de 0), `corrections` (3), `bonne`, `affiche` (sortie du programme corrigé), `explication`, `aides`, et **un seul** champ pour ce que montre le programme fautif : `message` (le message réel : « IndexError: list index out of range », « Error: near "plage": syntax error »), `affiche_fautif` (sa sortie, pour une erreur de logique ; vide s'il n'affiche rien) ou `boucle_infinie: true` | la correction juste donne `affiche` ; les autres et le programme fautif, non ; le programme fautif donne bien `message`, `affiche_fautif` ou ne s'arrête pas |
| `ordre` | `but`, `lignes` dans le bon ordre (toutes différentes), `affiche`, `aides` | le programme dans l'ordre donne `affiche`, et **aucune autre disposition** ne le donne (toutes les permutations sont essayées jusqu'à 8 lignes) |
| `completer` | `but`, `lignes` avec `{0}`, `{1}`…, `trous` [{`options`, `bonne`}], `affiche`, `explication`, `aides` | les bonnes pièces donnent `affiche` ; chaque mauvaise le change |

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
