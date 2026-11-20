# Contrôle de notions : piles et files (NSI, terminale)

Contrôle formatif court, en milieu de chapitre, sur le modèle du contrôle de notions sur les arbres binaires (T108). Sources : la fiche « Les piles et les files » (FichesNSI) et le cours-quiz `cours/piles-files.json` (QuizzNSI), dont il reprend les conventions (pile écrite du sommet vers le bas, file de la tête vers la queue, primitives en méthodes du module `pile_file`).

Questions : règle LIFO ou FIFO, pile ou file dans une situation, `sommet` ou `depiler`, état d'une pile, état d'une file, sortie d'un programme ; « trouve l'erreur » (`IndexError: pop from empty list`) : le message, puis la condition de boucle corrigée ; pile ou file avec une liste Python ; exercice de type bac (`compter` sur une pile, `maximum` sur une file : valeur renvoyée, structure auxiliaire, ligne à compléter).

## Les fichiers

| Fichier | Rôle |
|---|---|
| `index.html`, `eleve.js` | Page élève : l'élève compose, puis obtient un code de copie et son QR code. **La clé n'est pas chargée** : aucune correction n'est visible. `?sujet=1` ou `?sujet=2` impose le sujet. |
| `prof.html`, `prof.js` | Page enseignant·e : liens et QR des sujets à projeter, lecture des codes (collés, caméra ou photo), notes, erreurs par question, copies très proches, export CSV. |
| `controle.js` | Énoncés, programmes et consoles (sans les réponses), en JSON entre deux marqueurs. |
| `cle.js` | Clé de correction, écritures acceptées des lignes de code, diagnostics des erreurs fréquentes (chargée par `prof.html` et `corrige.html` seulement). |
| `moteur.js`, `zone-code.js`, `commun.css`, `papier.css` | Moteur commun aux contrôles de notions à programmes (identique dans `controle-notions-piles-files/` et `controle-notions-poo/`) : coloration, numéros de ligne, filets d'indentation, consoles compactes, codage des copies, zone de code. |
| `sujet.html` → `sujet.pdf` | Version papier : une feuille A4 recto verso par sujet, noir et blanc, 10 pt au moins. |
| `corrige.html` → `corrige.pdf` | Corrigé, texte à 11 pt : une erreur fréquente par question. |
| `verification/verifier.py` | Recalcule toute la clé **par exécution avec Python 3.13** et compare chaque console affichée à la sortie réelle. |
| `verification/generer-pdf.py`, `verification/essai-navigateur.py`, `verification/essai-horloge.py` | Régénèrent les PDF, rejouent un essai complet (élèves, zone de code, page prof, captures 320, 768, 1440 px en clair et obscur) et l'effacement à un jour, avec Playwright. |
| `vendor/` | Bibliothèques QR hébergées ici (MIT et Apache 2.0). |

## Forme (comme le contrôle sur les arbres binaires, T108)
- 20 minutes, 12 questions, 1 point chacune, tout ou rien (note sur 20 = points × 20 / 12) ; deux sujets de même forme.
- En ligne, l'ordre des questions et des options est mélangé ; les questions d'un même programme restent ensemble et dans l'ordre.
- « Trouve l'erreur » : le message d'erreur est **celui de Python 3.13**, tel quel ; seul le dossier est retiré des chemins (`File "programme.py"`).
- Code affiché : numéros de ligne, un filet et une bande grise par niveau d'indentation, mots-clés en gras, fonctions soulignées, chaînes en italique, commentaires en gris (contrastes d'au moins 7:1, lisible en noir et blanc). Consoles compactes.
- Réponse en code : une zone de plusieurs lignes, police à chasse fixe, Tab qui indente, Maj + Tab qui désindente, Entrée qui garde l'indentation (un niveau de plus après « : ») ; Échap puis Tab pour sortir. **Il manque encore, par rapport à la règle 20** : la coloration dans la zone, les guides d'indentation dans la zone et l'autocomplétion. Il n'y a pas d'exécution (la réponse est comparée à une liste d'écritures acceptées, toutes vérifiées par exécution).

## Le code de copie et les données
Comme pour le contrôle sur les arbres : JSON `[version, pseudo, classe, sujet, début, durée, graine, réponses]`, UTF-8, base 32 de Crockford, somme de contrôle de 4 caractères (`PIL1-…-XXXX`). Rien n'est envoyé sur Internet ; brouillon de l'élève et copies lues par l'enseignant·e gardés **un jour au plus** dans le navigateur ; une copie commencée ne s'ouvre jamais d'office sur un poste partagé. Copies nominatives réunies par l'enseignant·e : fiche `collecte: true`.

La page élève ne contient pas la clé ; mais `cle.js`, `prof.html` et le corrigé sont publics (décision de l'enseignant du 20/11). Pour un contrôle formatif surveillé, c'est suffisant.

## Vérifier après une modification
```
python3.13 -I verification/verifier.py
python3 -m http.server 8765   # à la racine du dépôt
python3 -I nsi-terminale/fichiers/controle-notions-piles-files/verification/generer-pdf.py
python3 -I nsi-terminale/fichiers/controle-notions-piles-files/verification/essai-navigateur.py <dossier des captures>
python3 -I nsi-terminale/fichiers/controle-notions-piles-files/verification/essai-horloge.py
```
Changer une question : incrémenter `version` dans `controle.js` (les anciens codes sont alors refusés avec un message clair).

Babash - NSI Tani Malandi · contenus CC BY-SA 4.0, code MIT.
