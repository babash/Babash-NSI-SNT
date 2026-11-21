# Écrire un TD en ligne, style « Signal pirate » (mode d'emploi pour les Ateliers)

Un TD est **une seule page HTML** : à l'écran, elle se corrige toute seule ; imprimée, elle **est** la feuille papier (A4, bandeau de 28 mm, code, consoles, lignes de réponse, margouillat, pied de page). On n'écrit jamais de PDF à part.

- Moteur : `assets/td-en-ligne.js` (ne pas le réécrire) ; style : `assets/td-en-ligne.css` (écran clair, écran obscur, papier).
- Modèle : `charte/gabarit-td/modele.html` (commenté) ; exemple rendu : `charte/gabarit-td/index.html` ; TD complet : `charte/td-pilote/`.
- Outils : `charte/nouveau-td.py` (le squelette), `charte/verifier-td.py` (le code exécuté pour de vrai), `charte/imprimer-td.py` (le PDF vierge et les contrôles de mise en page).

## 1. Créer le squelette

À la racine du dépôt :

```
python3 -I charte/nouveau-td.py nsi1/fichiers/boucles-td1 \
  --id nsi1-boucles-td1 --titre "Les boucles \`for\` et \`while\`" \
  --niveau "1re NSI" --chapitre "Programmer en Python" --bandeau 1 \
  --quiz "https://babash.github.io/QuizzNSI/revision.html?cours=conditions-boucles" \
  --accroche "Répéter des instructions"
```

| Option | Ce qu'elle fait |
|---|---|
| `--id` | identifiant **unique et stable** (minuscules, chiffres, tirets). Il sert au stockage sur l'appareil, au futur compte commun et à la cachette du margouillat. Ne le changez plus ensuite. |
| `--titre` | le titre ; un mot entre accents graves devient du code (`` `while` ``). Court : il tient sur une ligne du bandeau (26 caractères environ, en capitales). |
| `--niveau`, `--chapitre` | la ligne au-dessus du titre. Ensemble, **40 caractères au plus** (elle ne passe pas à la ligne sur papier). |
| `--bandeau` | le paysage, choisi selon le chapitre (voir § 2). |
| `--quiz` | l'adresse du cours-quiz du chapitre : le QR code est calculé **hors ligne** (avec `assets/qrcode-generator.js`). **Sans `--quiz`, pas de QR code** : c'est le cas d'un chapitre sans cours-quiz. |
| `--accroche` | une ligne sous le titre, facultative (25 caractères environ). |
| `--controle` | variante de contrôle : bandeau de 20 mm, puce « Contrôle ». |
| `--remplacer`, `--cachette` | écraser une page existante ; forcer la cachette du margouillat (`b1` à `b4`, `memo`, `pied`). |

Le script écrit `index.html` dans le dossier, avec les bons chemins vers `assets/`, le lien « Code source sur GitHub » et le pied de page complet.

## 2. Choisir le bandeau

Les quatre bandeaux tournent selon les chapitres (un chapitre garde le même bandeau pour tous ses TD) :

| N° | Paysage (aucun nom de lieu : les élèves devinent) | Chapitres conseillés |
|---|---|---|
| 1 | le cône vu de la baie, et son téléphérique de pirogues | programmer en Python : variables, conditions, boucles, fonctions |
| 2 | l'îlot de sable blanc, et le feu rouge dans le lagon | données : représentation, tables, bases de données, SQL |
| 3 | la ville, le mont et la barge-drone | réseaux, Internet, web, architecture, systèmes |
| 4 | le baobab de plage, ses paraboles et ses lampions | algorithmes, structures (listes, piles, arbres, graphes) |

En SNT, on suit le thème : 1 (Python, photo numérique), 2 (données structurées, localisation), 3 (Internet, web, réseaux sociaux), 4 (objets connectés). Les fichiers : `assets/td/bandeau-N.svg` (28 mm), `bandeau-N-controle.svg` (20 mm) et leurs versions `-obscur`. Ils se refont avec `python3 -I charte/bandeaux-td.py`.

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
| `code` | `<pre class="td-depart">` + `pre.td-attendu` et/ou `<script type="text/x-python" class="td-tests">` + `<pre class="td-code" data-verifier="correction">` | exécuté par Python 3.13, chargé au clic ; **bonus** par défaut, `data-obligatoire` pour le compter |

« Trouve l'erreur » : **toujours le vrai message de Python 3.13**, en entier (« Did you mean » compris). Pour l'obtenir : écrire le programme dans un fichier du nom de `data-fichier`, puis `python3 -I charte/verifier-td.py --erreur taxi.py`, et copier la sortie telle quelle dans `pre.td-erreur`. Le moteur la colore et l'étiquette « erreur ».

Le contenu : exemples variés de la vie réelle des élèves (la barge, le bouchon, le marché, les marées… et d'ailleurs), prénoms variés sans nom de famille, aucune marque, aucune arme ; aucune question de genre ; on ne promeut aucune religion, sans en faire un problème ; **ni personnage ni récit** sur une feuille. Jamais de note ni de score : le moteur affiche une jauge d'avancement, puis « Feuille validée ».

## 4. Vérifier et faire le PDF

```
python3 -I charte/verifier-td.py nsi1/fichiers/boucles-td1/index.html
python3 -m http.server 8000            # à la racine du dépôt, dans un autre terminal
python3 -I charte/imprimer-td.py http://localhost:8000/nsi1/fichiers/boucles-td1/index.html nsi1/fichiers/boucles-td1/td.pdf
```

`verifier-td.py` exécute chaque programme et compare (sorties, messages d'erreur mot pour mot, corrections). `imprimer-td.py` imprime **la feuille vierge** (il remplit tout, déclenche l'impression et vérifie qu'aucune réponse, aucun coup de pouce ni aucune correction n'est dans le PDF), puis contrôle la mise en page : 4 pages au plus, aucun texte sous 10 pt, aucune ligne de code coupée, rien hors de la page, aucune requête hors du site, seules les polices du site dans le PDF.

## 5. Liste de contrôle avant de livrer

- [ ] `verifier-td.py` : « tout est juste ».
- [ ] `imprimer-td.py` : « PDF vierge : oui », **4 pages A4 au plus** (une fiche : 2 pages).
- [ ] **10 pt au moins** partout sur papier (contrôlé par le script).
- [ ] **Code : 80 caractères au plus par ligne** dans une question (mesuré : 80 colonnes de JetBrains Mono à 10 pt sur A4) ; **35 au plus** dans une option de `qcu` ou `cases` (les options s'impriment sur deux colonnes). Visez 70 pour garder de la marge ; une ligne trop longue est signalée (« ligne de code coupée »).
- [ ] Pas de débordement : la page à **320 px** sans défilement horizontal, en clair et en obscur ; puis 768 et 1440 px.
- [ ] Contraste : ne changez aucune couleur dans la page ; tout est dans `assets/td-en-ligne.css` (7:1 pour le texte et le code, vérifié).
- [ ] Rien d'essentiel par la couleur seule (une consigne ne dit jamais « la ligne rouge »).
- [ ] Le **margouillat** est présent (`data-cachette`), le **bandeau** est le bon pour le chapitre, le **QR code** pointe vers le bon cours-quiz (ou il n'y en a pas).
- [ ] Le **pied de page** : auteur, licence CC BY-SA 4.0, « conçu avec l'aide de l'IA », « Code source sur GitHub ».
- [ ] La **feuille imprimée est vierge** : ouvrez le PDF et regardez-le.
- [ ] `python3 -I .github/gardien/caracteres.py --diff origin/main...HEAD` : aucun caractère invisible.
