# QCM Pronote

Les QCM de NSI et de SNT, au format XML Moodle, que Pronote importe et exporte. Auteur : Babash - NSI Tani Malandi, licence CC BY-SA 4.0 (le code des outils : MIT).

Chaque quiz suit la règle 22 de la philosophie éducative :
- des QCU à 4 options, une seule juste, et trois distracteurs tirés d'erreurs typiques ;
- un feedback bienveillant et explicatif pour chaque option, au tutoiement ;
- l'objectif affiché au début de chaque question, et un nom « [Thème] … » ;
- du code coloré, exécuté et vérifié ;
- une bonne réponse jamais mise en avant, placée sans motif.

## Les quiz

| Niveau | Fichier à importer | Questions | Aperçu de relecture |
|---|---|---|---|
| Seconde (SNT) | `snt/snt-pixels-couleurs.xml` | 19 | `snt-pixels-couleurs.html` |
| Première | `nsi-premiere/nsi1-bases-2-et-16.xml` | 21 (QCU, choix multiples, réponses courtes et numériques, textes à trous, appariements) | `nsi1-bases-2-et-16.html` |
| Première | `nsi-premiere/nsi1-conditions-1.xml` (if, elif, else) | 21 | `nsi1-conditions-1.html` |
| Première | `nsi-premiere/nsi1-conditions-2.xml` (blocs imbriqués et erreurs) | 17 | `nsi1-conditions-2.html` |
| Première | `nsi-premiere/nsi1-cout-1-compter.xml` | 20 | `nsi1-cout-1-compter.html` |
| Première | `nsi-premiere/nsi1-cout-2-ordres-de-grandeur.xml` | 20 | `nsi1-cout-2-ordres-de-grandeur.html` |
| Première | `nsi-premiere/nsi1-dictionnaires.xml` | 20 | `nsi1-dictionnaires.html` |
| Première | `nsi-premiere/nsi1-erreurs-python-1.xml` (sans fonctions) | 15 | `nsi1-erreurs-python-1.html` |
| Première | `nsi-premiere/nsi1-erreurs-python-2.xml` (avec des fonctions) | 15 | `nsi1-erreurs-python-2.html` |
| Première | `nsi-premiere/nsi1-ligne-de-commande.xml` | 20 (dont 1 appariement, 3 textes à trous) | `nsi1-ligne-de-commande.html` |
| Première | `nsi-premiere/nsi1-listes.xml` | 16 (dont 1 choix multiple) | `nsi1-listes.html` |
| Première | `nsi-premiere/nsi1-types-expressions.xml` | 20 (dont 1 appariement, 1 réponse numérique) | `nsi1-types-expressions.html` |
| Terminale | `nsi-terminale/nsit-poo-1.xml` | 20 | `nsit-poo-1.html` |
| Terminale | `nsi-terminale/nsit-sql-1-requetes.xml` | 20 | `nsit-sql-1-requetes.html` |
| Terminale | `nsi-terminale/nsit-sql-2-jointures-mises-a-jour.xml` | 20 | `nsit-sql-2-jointures-mises-a-jour.html` |

Les deux quiz de conditions conviennent aussi en seconde (SNT, partie programmation), comme « Types, expressions et affectations ».

Le coût des algorithmes est rangé en première : c'est là qu'il est au programme (parcours séquentiel, tris, dichotomie). Les deux quiz servent aussi de rappel en terminale.

## Importer un quiz dans Pronote
1. Télécharger le fichier `.xml` du quiz (et non l'aperçu `.html`).
2. Dans Pronote, ouvrir l'espace des QCM, puis choisir l'import d'un QCM au format **Moodle XML**.
3. Choisir le fichier. Pronote crée un QCM qui porte le titre du quiz (par exemple « NSI 1re · Les listes Python ») et le niveau indiqué.
4. Relire le QCM dans Pronote avant de le donner, en particulier la première fois : le code doit être coloré et bien indenté, et chaque option doit avoir son feedback.

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
- consoles compactes : une ligne de console par ligne de texte ;
- « trouve l'erreur » : toujours le message réel de Python 3.13, vérifié par exécution.

## Construire et vérifier
Les quiz s'écrivent dans `sources/<niveau>/<id>.json`. Les fichiers XML et les aperçus sont produits par un outil : on ne les modifie jamais à la main.

```bash
python3 -I qcm/outils/construire_qcm.py   # écrit qcm/<niveau>/<id>.xml et .html
python3 -I qcm/outils/verifier_qcm.py     # contrôle tout ; code de sortie 1 en cas d'erreur
```

`verifier_qcm.py` contrôle :
- la structure : XML bien formé et à jour, balises obligatoires ;
- les QCU : 4 options, une seule juste, des options toutes différentes ;
- les feedbacks : au moins 40 caractères, au tutoiement, sans formule sèche ;
- l'objectif affiché au début, et le nom de chaque question ;
- les positions de la bonne réponse : équilibrées, sans série, sans motif ;
- la longueur de la bonne réponse : elle ne doit pas la faire repérer ;
- les contrastes des couleurs du code (7:1 au moins), et une coloration qui se lit aussi en noir et blanc ;
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
- Aucune donnée d'élève : les prénoms des énoncés sont fictifs.
