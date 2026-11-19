# Écrire un cours-quiz : le format `quizz-nsi/1`

Un cours-quiz est **un seul fichier JSON**, `cours/<id>.json`. Le moteur (les pages HTML et `js/`) ne change pas : pour un nouveau cours, on écrit ce fichier, on l'ajoute à `cours/catalogue.json`, et on lance le vérificateur.

```bash
python3 -I outils/verifier_cours.py cours/<id>.json   # forme, règle 22, répartition, exécution du code
```

Le modèle complet est [`piles-files.json`](piles-files.json).

## Le cours

| Champ | Obligatoire | Contenu |
|---|---|---|
| `format` | oui | toujours `"quizz-nsi/1"` |
| `id` | oui | le nom du fichier, sans `.json` : minuscules, chiffres et tirets (`piles-files`) |
| `titre`, `sous_titre` | `titre` | le titre de la diapositive d'ouverture |
| `niveau` | oui | `"Terminale NSI"`, `"Première NSI"`, `"Seconde SNT"` |
| `programme` | oui | la ligne du programme officiel (BO de 2019) |
| `fiche` | non | le lien de la fiche de cours correspondante (FichesNSI) |
| `auteur`, `licence` | oui | `"Babash - NSI Tani Malandi"`, `"CC BY-SA 4.0"` |
| `duree_minutes` | non | 45 au plus |
| `sources` | non | les supports dont le cours s'inspire (contrôles, sujets de bac cités) |
| `criteres` | oui | les critères de réussite, par niveau (apprentissage visible) |
| `conventions` | oui | les conventions rappelées au début et sur la feuille imprimée (sens d'écriture d'une pile, hauteur d'un arbre réduit à un nœud…) |
| `prelude_python` | non | des lignes Python exécutées avant chaque vérification (par exemple les classes `Pile` et `File`) |
| `diapositives` | oui | la suite des diapositives, dans l'ordre du cours |

## La règle des exemples (pour tous les cours)

Chaque notion s'ancre **d'abord dans un exemple du quotidien à Mayotte**, connu de tous les élèves, **puis dans son usage informatique** (consigne de l'enseignant, 19/11). Pour les piles et les files : la boîte de chips en tube (la pile), la file au doukabé et le bouchon jusqu'à Mamoudzou (la file), puis le bouton « Annuler » et l'imprimante de la salle info. Des scènes du quotidien, sans cliché ni moquerie, sans nom de marque ; les schémas sont des SVG originaux et sobres, sans personnage. Tout mot d'une langue locale est signalé à l'enseignant pour vérification et n'est jamais nécessaire pour comprendre.

## Les diapositives

Chaque diapositive a un `type` :

- **`titre`** : la première. Champs : `titre`, `texte` (une liste de phrases). Les critères et les conventions s'y affichent seuls. `"conventions": false` cache les conventions (rappelées alors sur la feuille imprimée).
- **`notion`** : une idée par diapositive. Champs : `titre` ; `surtitre` (facultatif, « Notion » par défaut : « Essayons avec ce qu'on connaît », « La solution »…) ; `texte`, **3 phrases courtes au plus** ; `schema` (facultatif) ; `code` (facultatif, une liste de lignes) ; `vocabulaire` (facultatif : les mots anglais et leur traduction) ; `progressif: true` (les phrases apparaissent une à une) ; `code_cache: true` (le code apparaît au clic suivant) ; `consigne` (des consignes d'observation sur le code : « Précise ce qui est affiché », « Repère… ») ; `chute` (une phrase finale, comme « C'est un peu compliqué, non ? »).

**Les apparitions progressives.** Sur la page projetée et en révision, « Suite » montre l'élément suivant de la diapositive avant de passer à la suivante ; les téléphones suivent l'écran projeté (le message de séance porte le nombre d'éléments montrés, `f`). En revenant en arrière, tout est montré.
- **`question`** : voir plus bas.
- **`partie`** : un titre de partie, en grand. Champs : `numero` (facultatif), `titre`, `sous_titre`.
- **`classe`** : une question ouverte à la classe, sans réponse à cocher (« Et si on programmait… ? »). Champs : `question`, `texte` (facultatif), `pistes` (des pistes qui apparaissent une à une), `schema`, `code`.
- **`humour`** : la diapositive qui dramatise (« Bon, si on continue… »). Champs : `titre`, `lignes` (elles apparaissent une à une), `chute` (la dernière phrase, « Il nous faut agir ! »).
- **`bilan`** : la dernière. Champs : `titre`, `tableau` (`colonnes` et `lignes`), `ticket` (les questions du ticket de sortie).

## Les questions (règle 22 de la philosophie éducative)

| Champ | Contenu |
|---|---|
| `id` | `q01` à `q20`, unique |
| `nom` | `[Thème] Ce que la question fait travailler`, comme dans Pronote |
| `objectif` | une phrase, affichée au début de la question |
| `enonce` | une liste de paragraphes **impersonnels**, comme au bac |
| `code` | facultatif : une liste de lignes Python, affichée numérotée et colorée |
| `schema` | facultatif : un schéma (voir plus bas) |
| `options` | **exactement 4** : `{ "texte": "…", "feedback": "…" }`, ou `"code": [lignes]` à la place de `texte` ; **une seule** porte `"juste": true` |
| `explication` | une phrase « À retenir », montrée après la réponse |
| `trace` | facultatif : `{ "colonnes": [...], "lignes": [[...], ...] }`, le pas à pas montré après la réponse |
| `verifications` | obligatoire dès qu'il y a du code : voir plus bas |
| `note_verification` | si la question n'a pas de code à exécuter : comment le fait a été vérifié (une mesure, une source) |

Les règles que le vérificateur contrôle :
- 4 options, une seule juste ; un feedback d'au moins 40 caractères pour **chaque** option, au tutoiement : il explique l'erreur (bienveillant) ou consolide l'automatisme ;
- aucun gras dans une option ; la bonne réponse n'est la plus longue que rarement (au plus 40 % des questions) ;
- la bonne réponse répartie entre A, B, C et D (pour 20 questions : 4 à 6 fois chacune), jamais 3 fois de suite la même lettre, aucun motif périodique ;
- aucun caractère invisible ou de contrôle ;
- 20 questions par cours.

Ce qu'il faut relire à la main : les distracteurs viennent d'erreurs typiques d'élèves ; les énoncés sont impersonnels et courts ; le vocabulaire anglais est traduit ; le langage inclusif ; les contextes de Mayotte, sans cliché.

## Le texte

Dans tous les textes : `` `code` `` (coloré comme du Python), `==mot-clé==` (en couleur, et aussi en gras souligné : la couleur ne porte jamais seule l'information), `**gras**` (ni gras ni mot-clé dans les options), `*italique*`. Tout le reste est affiché tel quel : aucune balise HTML. Un caractère spécial s'écrit lui-même (é, ·, →) ; un caractère invisible est refusé.

## Les schémas

Les schémas sont dessinés par le moteur, en SVG, à partir des données ; ils suivent le thème clair ou obscur et s'impriment en noir et blanc.

| `type` | Champs | Dessin |
|---|---|---|
| `pile` | `elements` : **du bas vers le haut** | une pile verticale, sommet repéré |
| `file` | `elements` : de la tête vers la queue | une file horizontale, tête (sortie) à gauche |
| `etapes` | `structure` (`pile` ou `file`), `etapes` : `[{ "op": "p.empiler(4)", "elements": [4] }, …]` (6 au plus) | l'état après chaque opération |
| `deux-piles` | `gauche` et `droite` : `{ "nom": "entree", "elements": [...] }`, `fleche` | deux piles côte à côte |
| `liste` | `elements` : des valeurs Python (`1`, `"chat"`, `true` en JSON) | une liste Python avec ses indices ; les valeurs s'affichent comme Python les écrit : `True`, `None`, `"chat"` |
| `decalage` | `elements` | le décalage provoqué par `pop(0)` |
| `svg` | `code` : un SVG écrit à la main (sans script ni attribut `on…`) | pour les autres cours (arbres, graphes) ; pas envoyé aux téléphones |

Chaque schéma accepte une `legende`. Un schéma « Python » (`liste`, ou tout schéma avec `variable`, `code` ou `"python": true`) affiche ses valeurs comme Python (`True`, `None`, chaînes entre guillemets) ; les autres affichent des étiquettes (« copie 1 », « taxi »).

**Un schéma qui se déduit d'un code est vérifié par exécution** (contrôle du vérificateur) :
- `etapes` avec `"variable": "p"` (ou `"f"`) : chaque `op` est du Python (`p.empiler(4)`) ; `p.depiler() → 1` vérifie aussi la valeur renvoyée ; après chaque étape, le contenu de la variable doit être exactement `elements` ;
- `pile`, `file`, `liste` ou `deux-piles` avec `"code": [lignes]` : après ce code, chaque variable dessinée (`variable`, ou le `nom` de chaque pile pour `deux-piles`) doit contenir exactement `elements`.

Rappel : pour une pile, `elements` va **du bas vers le haut** ; pour une file, de la tête vers la queue. Pour un nouveau type récurrent (un arbre binaire, un graphe), mieux vaut l'ajouter au moteur (`js/commun.js`, fonction `Q.schema`) qu'écrire du SVG à la main.

## Les vérifications

Chaque vérification exécute, dans un Python isolé (`python3 -I`) : `prelude_python`, puis le `code` de la question (sauf `"reprendre_code": false`), puis le `code` de la vérification. Elle compare :
- `sortie` : ce qui est affiché, exactement ;
- `erreur` : le nom de l'exception attendue (`"IndexError"`, `"RecursionError"`).

```json
"verifications": [
  { "code": ["print(haut_vers_bas(p))"], "sortie": "[3, 1, 4]" },
  { "code": [], "erreur": "IndexError" }
]
```

On vérifie la bonne réponse, et aussi ce qu'affirment les feedbacks des distracteurs quand c'est possible (le champ `option` dit lequel, pour la relecture).

## Ajouter le cours au catalogue

```json
{ "id": "arbres-binaires", "titre": "Arbres binaires", "niveau": "Terminale NSI", "questions": 20 }
```

Les liens : `revision.html?cours=<id>`, `animer.html?cours=<id>`, `imprimer.html?cours=<id>` et `imprimer.html?cours=<id>&corrige`.
