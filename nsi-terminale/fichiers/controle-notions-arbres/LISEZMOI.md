# Contrôle de notions : arbres binaires (NSI, terminale)

Premier « contrôle de notions » du site (T108) : un contrôle formatif court, en milieu de chapitre, sur les bases. Modèle de niveau et de forme : l'évaluation formative sur les arbres binaires de recherche (`../cc-term-abr-formative/`), dont il reprend les questions de base et la convention.

- **20 minutes, 12 questions, 1 point chacune** (note sur 20 = points × 20 / 12) ; deux sujets de difficulté voisine (1 et 2).
- Types de questions : valeur courte (racine, taille, hauteur, profondeur), ensemble de valeurs (feuilles), choix unique (ABR ou non), suite de valeurs (parcours en largeur, préfixe, infixe), sortie d'un programme (`print(a.droit.droit.gauche.valeur)`), compléter une ligne (fonction `taille`), schéma à étiqueter (insertion dans un ABR).
- Convention toujours rappelée : la profondeur de la racine est 0 ; un arbre réduit à un seul nœud a une hauteur de 0.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `index.html`, `eleve.js` | Page élève : l'élève compose, puis obtient un code de copie et son QR code. **La clé n'est pas chargée** : aucune correction n'est visible. `?sujet=1` ou `?sujet=2` impose le sujet. |
| `prof.html`, `prof.js` | Page enseignant·e : liens et QR des sujets à projeter, lecture des codes (collés, caméra ou photo), notes, erreurs par question, copies très proches, export CSV. |
| `controle.js` | Énoncés, arbres, dessin SVG, codage des copies (sans les réponses). |
| `cle.js` | Clé de correction et diagnostics des erreurs fréquentes (chargée par `prof.html` et `corrige.html` seulement). |
| `sujet.html` → `sujet.pdf` | Version papier : une page A4 par sujet, noir et blanc. |
| `corrige.html` → `corrige.pdf` | Corrigé : une page A4 par sujet, avec une erreur fréquente par question. |
| `verification/verifier.py` | Recalcule toute la clé par exécution (classe `Noeud`, `print`, ligne complétée, insertion dans un ABR). |
| `verification/generer-pdf.py`, `verification/essai-navigateur.py` | Régénèrent les PDF et rejouent un essai complet (élèves, puis page prof) avec Playwright. |
| `vendor/` | Bibliothèques QR hébergées ici (MIT et Apache 2.0). |

## Le code de copie
JSON `[version, pseudo, classe, sujet, début, durée, graine, réponses]`, en UTF-8, en base 32 de Crockford (QR en mode alphanumérique), suivi d'une somme de contrôle de 4 caractères : `ARB1-…-XXXX`. La somme de contrôle repère un code tronqué ou mal recopié ; ce n'est pas une protection.

**Ce que vaut la protection** : la page élève ne contient pas la clé, donc l'élève ne voit pas sa correction pendant qu'il ou elle compose. Mais `cle.js`, `prof.html` et le corrigé sont publics : un·e élève qui les ouvre trouve les réponses. Pour un contrôle formatif, surveillé en classe, c'est suffisant.

## Données
Rien n'est envoyé : le brouillon reste dans le navigateur de l'élève (`localStorage`), les copies lues dans celui de l'enseignant·e. Le code contient le prénom ou pseudo choisi par l'élève et sa classe facultative.

## Vérifier après une modification
```
python3 -I verification/verifier.py
python3 -m http.server 8765   # à la racine du dépôt
python3 -I verification/generer-pdf.py nsi-terminale/fichiers/controle-notions-arbres
```
Changer une question ou un arbre : incrémenter `version` dans `controle.js` (les anciens codes sont alors refusés avec un message clair).

Babash - NSI Tani Malandi · contenus CC BY-SA 4.0, code MIT.
