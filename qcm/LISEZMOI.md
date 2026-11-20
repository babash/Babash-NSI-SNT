# QCM Pronote

Les QCM de NSI et de SNT, au format XML Moodle, que Pronote importe et exporte. Auteur : Babash - NSI Tani Malandi, licence CC BY-SA 4.0 (le code des outils : MIT).

Chaque quiz suit la règle 22 de la philosophie éducative :
- des QCU à 4 options, une seule juste, et trois distracteurs tirés d'erreurs typiques ;
- un feedback bienveillant et explicatif pour chaque option, au tutoiement ;
- l'objectif affiché au début de chaque question, et un nom « [Thème] … » ;
- du code coloré, exécuté et vérifié ;
- une bonne réponse jamais mise en avant, placée sans motif.

## Les quiz

16 quiz, 296 questions. Chaque quiz a trois fichiers, dans `qcm/<niveau>/` :
- `<id>.xml` : le fichier à importer dans Pronote ;
- `<id>.html` : l'aperçu **élève**, avec les questions et les options dans l'ordre du fichier, sans aucune marque de la bonne réponse et sans les retours ;
- `<id>-corrige.html` : le **corrigé enseignant·e**, où chaque bonne réponse est écrite en toutes lettres (« Bonne réponse : C »), avec tous les retours. Il ne se donne pas aux élèves.

| Niveau | Notion | Questions | Fichier à importer | Aperçu élève | Corrigé |
|---|---|---|---|---|---|
| Seconde (SNT) | Photographie numérique : pixels, couleurs RVB, traitement d'image | 19 | [`snt/snt-pixels-couleurs.xml`](snt/snt-pixels-couleurs.xml) | [aperçu](snt/snt-pixels-couleurs.html) | [corrigé](snt/snt-pixels-couleurs-corrige.html) |
| Première | Écriture binaire, texte en ASCII, transistor et mémoires | 12 | [`nsi-premiere/nsi1-binaire-architecture.xml`](nsi-premiere/nsi1-binaire-architecture.xml) | [aperçu](nsi-premiere/nsi1-binaire-architecture.html) | [corrigé](nsi-premiere/nsi1-binaire-architecture-corrige.html) |
| Première | Écriture d'un entier en base 2 et en base 16 | 21 (QCU, choix multiples, réponses courtes et numériques, textes à trous, appariements) | [`nsi-premiere/nsi1-bases-2-et-16.xml`](nsi-premiere/nsi1-bases-2-et-16.xml) | [aperçu](nsi-premiere/nsi1-bases-2-et-16.html) | [corrigé](nsi-premiere/nsi1-bases-2-et-16-corrige.html) |
| Première | Types, expressions et affectations | 20 (dont 1 appariement, 1 réponse numérique) | [`nsi-premiere/nsi1-types-expressions.xml`](nsi-premiere/nsi1-types-expressions.xml) | [aperçu](nsi-premiere/nsi1-types-expressions.html) | [corrigé](nsi-premiere/nsi1-types-expressions-corrige.html) |
| Première | Conditions : if, elif, else | 21 | [`nsi-premiere/nsi1-conditions-1.xml`](nsi-premiere/nsi1-conditions-1.xml) | [aperçu](nsi-premiere/nsi1-conditions-1.html) | [corrigé](nsi-premiere/nsi1-conditions-1-corrige.html) |
| Première | Conditions : blocs imbriqués et erreurs | 17 | [`nsi-premiere/nsi1-conditions-2.xml`](nsi-premiere/nsi1-conditions-2.xml) | [aperçu](nsi-premiere/nsi1-conditions-2.html) | [corrigé](nsi-premiere/nsi1-conditions-2-corrige.html) |
| Première | Listes Python | 16 (dont 1 choix multiple) | [`nsi-premiere/nsi1-listes.xml`](nsi-premiere/nsi1-listes.xml) | [aperçu](nsi-premiere/nsi1-listes.html) | [corrigé](nsi-premiere/nsi1-listes-corrige.html) |
| Première | Dictionnaires Python | 20 | [`nsi-premiere/nsi1-dictionnaires.xml`](nsi-premiere/nsi1-dictionnaires.xml) | [aperçu](nsi-premiere/nsi1-dictionnaires.html) | [corrigé](nsi-premiere/nsi1-dictionnaires-corrige.html) |
| Première | Lire les erreurs de Python (sans fonctions) | 15 | [`nsi-premiere/nsi1-erreurs-python-1.xml`](nsi-premiere/nsi1-erreurs-python-1.xml) | [aperçu](nsi-premiere/nsi1-erreurs-python-1.html) | [corrigé](nsi-premiere/nsi1-erreurs-python-1-corrige.html) |
| Première | Lire les erreurs de Python (avec des fonctions) | 15 | [`nsi-premiere/nsi1-erreurs-python-2.xml`](nsi-premiere/nsi1-erreurs-python-2.xml) | [aperçu](nsi-premiere/nsi1-erreurs-python-2.html) | [corrigé](nsi-premiere/nsi1-erreurs-python-2-corrige.html) |
| Première | Coût d'un algorithme : compter les opérations | 20 | [`nsi-premiere/nsi1-cout-1-compter.xml`](nsi-premiere/nsi1-cout-1-compter.xml) | [aperçu](nsi-premiere/nsi1-cout-1-compter.html) | [corrigé](nsi-premiere/nsi1-cout-1-compter-corrige.html) |
| Première | Coût d'un algorithme : ordres de grandeur | 20 | [`nsi-premiere/nsi1-cout-2-ordres-de-grandeur.xml`](nsi-premiere/nsi1-cout-2-ordres-de-grandeur.xml) | [aperçu](nsi-premiere/nsi1-cout-2-ordres-de-grandeur.html) | [corrigé](nsi-premiere/nsi1-cout-2-ordres-de-grandeur-corrige.html) |
| Première | Ligne de commande (Linux) | 20 (dont 1 appariement, 3 textes à trous) | [`nsi-premiere/nsi1-ligne-de-commande.xml`](nsi-premiere/nsi1-ligne-de-commande.xml) | [aperçu](nsi-premiere/nsi1-ligne-de-commande.html) | [corrigé](nsi-premiere/nsi1-ligne-de-commande-corrige.html) |
| Terminale | Programmation orientée objet | 20 | [`nsi-terminale/nsit-poo-1.xml`](nsi-terminale/nsit-poo-1.xml) | [aperçu](nsi-terminale/nsit-poo-1.html) | [corrigé](nsi-terminale/nsit-poo-1-corrige.html) |
| Terminale | SQL : modèle relationnel et requêtes | 20 | [`nsi-terminale/nsit-sql-1-requetes.xml`](nsi-terminale/nsit-sql-1-requetes.xml) | [aperçu](nsi-terminale/nsit-sql-1-requetes.html) | [corrigé](nsi-terminale/nsit-sql-1-requetes-corrige.html) |
| Terminale | SQL : jointures et mises à jour | 20 | [`nsi-terminale/nsit-sql-2-jointures-mises-a-jour.xml`](nsi-terminale/nsit-sql-2-jointures-mises-a-jour.xml) | [aperçu](nsi-terminale/nsit-sql-2-jointures-mises-a-jour.html) | [corrigé](nsi-terminale/nsit-sql-2-jointures-mises-a-jour-corrige.html) |

Les deux quiz de conditions conviennent aussi en seconde (SNT, partie programmation), comme « Types, expressions et affectations ».

Le coût des algorithmes est rangé en première : c'est là qu'il est au programme (parcours séquentiel, tris, dichotomie). Les deux quiz servent aussi de rappel en terminale.

« Binaire et architecture » réunit les 12 questions retirées du quiz SNT (le binaire, le texte et l'architecture sont au programme de NSI 1re). Il est plus court que les autres : il se prête à une séance de 15 minutes.

**Les fichiers XML restent dans ce dépôt public**, même s'ils contiennent les réponses (Pronote en a besoin à l'import) : l'enseignant a décidé le 20/11/2026 que la fuite d'un corrigé ne l'inquiète pas à ce stade.

## Importer un quiz dans Pronote
1. Télécharger le fichier `.xml` du quiz (et non un des aperçus `.html`) : sur GitHub, ouvrir le fichier, puis « Download raw file » (télécharger le fichier brut).
2. Dans Pronote, ouvrir l'espace des QCM, puis choisir l'import d'un QCM au format **Moodle XML**.
3. Choisir le fichier. Pronote crée les questions, avec le titre du quiz (par exemple « NSI 1re · Les listes Python »), le niveau et la matière indiqués dans le fichier.
4. Relire le QCM dans Pronote avant de le donner, surtout la première fois : le code doit être coloré et bien indenté, et chaque option doit avoir son retour. Le corrigé `…-corrige.html` aide à cette relecture.
5. Le donner aux élèves comme un devoir ou une évaluation, avec la correction et les retours affichés après la réponse : ce sont des quiz formatifs.

La bonne réponse est déjà placée dans un ordre équilibré et sans motif : le mélange des réponses n'est pas nécessaire. S'il est activé dans Pronote, il reste sans danger.

## Ce qui reste à essayer à l'import
Les fichiers reprennent les balises que Pronote exporte lui-même : `name`, `questiontext`, `externallink`, `usecase`, `defaultgrade`, `single`, `answer` et `feedback`. On y ajoute `shuffleanswers` sur les QCU et `tolerance` sur les réponses numériques. Le fichier `essais/essai-import.xml` sert à essayer, dans un QCM de test, ce qui n'est pas encore sûr :

| Essai | Question à se poser | Si ça marche | Sinon |
|---|---|---|---|
| 1 | Pronote accepte-t-il `<penalty>`, `<hidden>` et `<generalfeedback>` ? Le texte « À retenir » s'affiche-t-il ? | on pourra ajouter un « À retenir » à chaque question | on ne les ajoute pas : ils manquent déjà aux fichiers actuels, sans gêner l'import |
| 2 | Les options qui contiennent `<` (par exemple `<__main__.Segment object at 0x…>`, `profondeur < 20`, `a<b`) s'affichent-elles en entier ? Les espaces multiples sont-ils gardés ? | rien à changer | signaler les options concernées à l'Atelier des quiz : elles seront réécrites |
| 3 | L'appariement affiche-t-il son explication générale ? | on l'ajoutera aux appariements (pour l'instant, elle n'est que dans l'aperçu) | l'explication reste dans l'aperçu |
| 4 | La réponse numérique avec `<tolerance>` est-elle acceptée ? | rien à changer | retirer `tolerance` dans `construire_qcm.py` |

Il faut aussi vérifier que les textes à trous (`cloze`, avec `{:SHORTANSWER:…}` et `{:MULTICHOICE:…}`) s'affichent bien à l'intérieur d'un bloc de code.

## Le code affiché
D'après la décision de l'enseignant du 20/11/2026, le code se lit aussi imprimé en noir et blanc :
- fond clair, contraste d'au moins 7:1 pour chaque couleur ;
- mots-clés en gras, fonctions soulignées, chaînes en italique, commentaires en gris italique ;
- un filet par niveau d'indentation, sur une bande grise ;
- consoles compactes : une ligne de console par ligne de texte ; le message d'erreur est en couleur, et son type (par exemple `TypeError`) en gras ;
- « trouve l'erreur » : toujours le message réel et complet de Python 3.13, ou de SQLite pour le SQL, vérifié par exécution.

## Les retours et les noms
- Un retour qui dit « tu as fait telle erreur » n'est écrit que si le calcul ou l'exécution montre que cette erreur mène bien à l'option. Sinon, le retour explique seulement la bonne démarche.
- Le nom et l'objectif d'une question disent la compétence travaillée, jamais la réponse : aucun mot de la seule bonne option n'y figure.
- Les choix d'une liste déroulante (texte à trous) et les lignes d'un appariement sont mélangés de façon stable : leur ordre ne donne pas la solution.

## Construire et vérifier
Les quiz s'écrivent dans `sources/<niveau>/<id>.json`. Les fichiers XML, les aperçus élève et les corrigés sont produits par un outil : on ne les modifie jamais à la main.

```bash
python3 -I qcm/outils/construire_qcm.py   # écrit qcm/<niveau>/<id>.xml, <id>.html et <id>-corrige.html
python3 -I qcm/outils/verifier_qcm.py     # contrôle tout ; code de sortie 1 en cas d'erreur
```

`verifier_qcm.py` contrôle :
- la structure : XML bien formé et à jour, balises obligatoires ;
- les QCU : 4 options, une seule juste, des options toutes différentes ;
- les feedbacks : au moins 40 caractères, au tutoiement, sans formule sèche ;
- l'objectif affiché au début, et le nom de chaque question ;
- les positions de la bonne réponse : équilibrées, sans série, sans motif ;
- la longueur de la bonne réponse : elle ne doit pas la faire repérer (erreur si elle est nettement la plus longue dans plus de 40 % des QCU ; avertissement si elle est simplement la plus longue dans plus de 40 % des QCU) ;
- les aperçus : l'aperçu élève ne marque jamais la bonne réponse, ne montre aucun retour et garde l'ordre du XML ; le corrigé écrit « Bonne réponse : X » pour chaque QCU ;
- les contrastes des couleurs du code (7:1 au moins), et une coloration qui se lit aussi en noir et blanc ;
- les consoles : chaque message d'erreur est coloré, et une console SQL affiche le vrai message de SQLite ;
- l'ordre : la bonne réponse d'une liste déroulante ne suit pas le numéro du trou, et un appariement n'est pas rangé dans l'ordre de la solution ;
- les noms et les objectifs : un avertissement signale un mot de la seule bonne option ;
- les caractères invisibles ;
- les doublons, dans un quiz ou entre deux quiz ;
- l'exécution :
  - chaque extrait Python est lancé avec `python3 -I` (Python 3.13 est la référence pour les messages d'erreur) ;
  - chaque requête SQL est lancée dans SQLite, en mémoire, sur la petite base décrite dans la source.

Le reste se relit à la main : les distracteurs viennent-ils d'erreurs typiques ? Les énoncés sont-ils impersonnels et courts, le vocabulaire anglais traduit, le contexte de Mayotte sans cliché ?

### Le format d'une source
Un quiz est un fichier JSON, proche du format des cours-quiz de QuizzNSI. Ses champs :
- `id`, `titre`, `niveau`, `programme`, `notions`, `objectifs`, `sources`, `auteur` ;
- `forme` et `retirees`, pour l'avant/après ;
- `prelude_python` et `schema_sql`, pour les vérifications ;
- `questions`.

Chaque question a :
- `nom`, `objectif`, `enonce`, `code` (avec `langage` : `python`, `sql` ou `bash`), `console`, `question` ;
- selon son `type` :
  - `qcu`, par défaut, ou `qcm` : des `options` avec `texte`, `feedback` et `juste` ;
  - `appariement` : des `paires` ;
  - `numerique` : `reponse` et `tolerance` ;
  - `reponse_courte` : `reponses` et `casse` ;
  - `trous` : des `lignes` avec `[[réponse|variante]]`, ou `[[*juste|faux]]` pour une liste déroulante ;
- des `verifications` exécutées (`sortie`, `message`, `erreur`, `sql` avec `resultat` ou `erreur_sql`), ou une `note_verification` ;
- `origine` et `fond`, pour la trace des corrections de fond : avant, après, raison.

## Les règles de révision
- La révision d'un quiz existant ne change que la forme. Le fond (ce qui est demandé, la bonne réponse, les distracteurs, le barème) ne change qu'avec l'accord de l'enseignant.
- Chaque changement de fond est tracé dans le champ `fond` de la question, et repris dans l'avant/après.
- Aucune donnée d'élève : les prénoms des énoncés sont fictifs, sans nom de famille. Un export de Pronote peut contenir des noms : on n'en garde que les questions.
