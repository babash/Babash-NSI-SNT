# Les banques d'exercices du Calendrier des vacances

Cette page est pour l'Atelier qui écrit la banque d'un chapitre. Une case du calendrier est un exercice : un mini-jeu de **10 minutes au plus**, en **3 niveaux** (Facile, Moyen, Costaud). L'élève choisit son niveau, et un niveau suffit pour valider la case.

## Les fichiers

| Fichier | Rôle | Qui le modifie |
|---|---|---|
| `exercice.schema.json` | Le format (JSON Schema) | Architecte |
| `catalogue.json` | La liste des chapitres et leur statut (`prevu`, `en_cours`, `pret`) | Architecte |
| `<chapitre>.json` | La banque d'un chapitre | l'Atelier de ce chapitre, sur sa branche `atelier/t105-<chapitre>` |
| `<chapitre>.js` | La même banque, fabriquée par `--bundle` | personne à la main |
| `../../scripts/tests/calendrier/exemple-boucles.json` | **Le gabarit** : 6 exercices justes, un de chaque type | Architecte |

Un Atelier ne touche **qu'à son fichier**. Il ne modifie ni `catalogue.json` ni le schéma : il demande dans son rapport.

## Le contrôle, à lancer avant chaque envoi

```sh
python3 scripts/calendrier_exercices.py --fichier calendrier/exercices/<chapitre>.json
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

## Les règles d'un chapitre

1. **30 exercices au moins**, numérotés `<chapitre>-001`, `-002`… dans l'ordre. C'est l'ordre des cases : l'exercice 1 sert le premier jour.
   - Un exercice publié ne change jamais de rang ni d'identifiant.
   - On peut corriger un exercice, et on ajoute toujours à la fin.
2. **Les types tournent.** Six exercices de suite couvrent les 6 types, et deux jours de suite n'ont jamais le même type. Ordre conseillé, répété : vraifaux, sortie, associer, erreur, completer, ordre.
3. **La difficulté monte doucement.** Les exercices 1 à 10 portent sur le cœur du chapitre, 11 à 20 sur les combinaisons, 21 à 30 sur les révisions mélangées. L'exercice 1 se réussit au niveau Facile en 2 minutes.
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
   - SQL : SQLite, avec la base d'exemple du chapitre (`base_sql`, 3 tables, 30 lignes au plus), des mots-clés en majuscules et `ORDER BY` dès qu'il peut y avoir plusieurs lignes.
10. **`relu`** reste `false`. L'enseignant·e passe à `true` après relecture, et la page enseignant·e signale un calendrier qui contient des exercices non relus.

## Les six types (voir le gabarit pour un exemple juste de chacun)

| Type | Champs d'une question | Ce que le contrôle vérifie |
|---|---|---|
| `vraifaux` | `texte`, `reponse` (true ou false), `explication`, et au besoin `code` et `verifier` (expression Python qui doit valoir `reponse`, par exemple `s == 10`) | `verifier` après le code |
| `sortie` | `code`, puis soit `options` (4, « / » sépare les lignes), `bonne` et `retours` (4), soit `reponse` (à taper) et `explication` ; `aides` | une seule option juste, ou la réponse exacte |
| `associer` | `consigne`, `paires` [[gauche, droite]…], `explication`, `executer: true` si la gauche est un programme | avec `executer`, ce que chaque programme affiche (lignes jointes par « , ») |
| `erreur` | `but`, `lignes`, `ligne` (indice de la ligne fausse, à partir de 0), `corrections` (3), `bonne`, `affiche` (sortie du programme corrigé), `explication`, `aides` | la correction juste donne `affiche` ; les autres et le programme fautif, non |
| `ordre` | `but`, `lignes` dans le bon ordre (toutes différentes), `affiche`, `aides` | le programme dans l'ordre donne `affiche` |
| `completer` | `but`, `lignes` avec `{0}`, `{1}`…, `trous` [{`options`, `bonne`}], `affiche`, `explication`, `aides` | les bonnes pièces donnent `affiche` ; chaque mauvaise le change |

## La méthode conseillée

1. **Écrire d'abord le plan des 30 exercices**, dans le rapport ou en tête du travail. Pour chacun : le rang, le type, la notion, et l'idée des trois niveaux.
2. **Écrire la banque en Python**, avec de petites fonctions qui fabriquent les questions. On peut faire exécuter un programme pour obtenir sa sortie exacte, mais **on écrit les distracteurs et les retours à la main**. Puis on écrit le JSON. Le script de fabrication reste dans le dossier temporaire de l'Atelier : seul le JSON va dans le dépôt.
3. **Lancer le contrôle** jusqu'à zéro erreur.
4. **Relire à voix haute trois exercices au hasard**, comme un·e élève de seconde dont le français est une langue seconde.
5. **Pousser `atelier/t105-<chapitre>`.** Le rapport donne le nombre d'exercices et de questions, la sortie du contrôle, et les points à relire par l'enseignant·e.
