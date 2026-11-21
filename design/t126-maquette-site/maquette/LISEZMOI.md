# Maquette T126 : le site au style des TD (« Signal pirate »)

Proposition à montrer à l'enseignant **avant** toute application. Rien n'est publié ; les pages réelles du site ne sont pas modifiées.

## Ouvrir
```
cd maquette && python3 -m http.server 8762
```
puis http://localhost:8762/. Six pages, autonomes (aucune requête vers un autre site) :

| Page de la maquette | Page du site | Contenu |
|---|---|---|
| `index.html` | `/` | accueil, direction A (bandeau en haut, en rotation ; `?bandeau=1` à `4` pour en forcer un) |
| `accueil-b.html` | `/` | accueil, direction B (un paysage par carte de rubrique) |
| `nsi-terminale/index.html` | `/nsi-terminale/` | rubrique, ses thèmes, les cours-quiz en tête |
| `bibliotheque/index.html` | `/bibliotheque/` | les 221 ressources, recherche, filtres, tri, liste ou cartes |
| `bibliotheque/fiche.html` | `/bibliotheque/?r=annales-bac-nsi-par-notion` | fiche d'une ressource |
| `bibliotheque/annales/index.html` | `/bibliotheque/annales/` | page d'application : 315 exercices, filtre par chapitre |

Le contenu est le HTML que `assets/site.js` produit sur `origin/main` (0386228), capturé tel quel (`../dom/`), puis réécrit par `../outils/generer.py` : nouvel en-tête, nouveau pied, couleurs par rubrique retirées, étiquette « Cours-quiz ». Les liens vers les pages absentes de la maquette mènent au site en ligne. `assets/maquette.js` remplace le moteur du site pour la démonstration seulement (affichage, filtres, tri, rotation du bandeau) : il n'est pas à publier.

## Les feuilles de style
- `assets/signal-commun.css` : polices et palette, **copie exacte** des lignes 19 à 134 de `assets/td-en-ligne.css` (branche `design/t123-style-td`, 225d802), plus trois mesures du site. Une seule palette pour les TD et le site : à l'application, `td-en-ligne.css` charge ce fichier au lieu de répéter ses variables.
- `assets/site.css` : le site, en 14 parties (page, barre du haut, bandeau, intro et recherche, accueil, rubrique, ressource, bibliothèque, fiche, annales, pied, petits écrans, mouvement, impression). Il vise les classes que `site.js` produit déjà ; il remplace `assets/style.css`, `bibliotheque/bibliotheque.css` et `bibliotheque/annales/annales.css`.
- Images : `assets/td/` (les quatre bandeaux, leurs versions réduites et obscures, le margouillat, les marges) et `assets/fonts/`, repris de la branche des TD sans modification ; `assets/favicon.svg` est nouveau.

## Contrôles
- `../outils/verifier.py` : 320, 768, 1440 px, clair et obscur, aucun défilement horizontal, aucune requête externe, aucune erreur JavaScript ; filtres (SNT : 52, comme le site), recherche, clic sur un chapitre des annales, tabulation (contour de 3 px), choix de l'affichage gardé au rechargement.
- `../outils/contrastes.py` : tous les couples de couleurs du site, clair et obscur (texte 18,9:1 et 16,1:1 ; liens 8,2:1 et 13,2:1 ; petit texte 9,9:1 et 11,3:1 ; traits 3,5:1 et 4,3:1).

## Pour appliquer au site réel
**Designer** : `assets/signal-commun.css` (nouveau), `assets/style.css` (remplacé par `site.css`), `bibliotheque/bibliotheque.css` et `bibliotheque/annales/annales.css` (vidés, puis retirés en deux temps), `assets/td/` et `assets/fonts/` (déjà sur `design/t123-style-td`), `assets/favicon.svg`, `assets/td-en-ligne.css` (charger le socle).

**Architecte** (`assets/site.js`, `reglages.js`, pages) :
1. la fonction `scene` (le décor de la ville) devient le bandeau : `<header class="bandeau" data-bandeau="N">`, `.bandeau-decor` avec `.margouillat` (places : `assets/td/places-margouillat.json`), `.bandeau-texte` (`.sur-titre` avec `.puce`, `h1 > span`), `.bandeau-repere` facultatif ; `.bandeau.compact` pour la fiche ; le chapo et la recherche sortent du bandeau, dans `.intro` ;
2. retirer les couleurs `--hl` (rubriques, thèmes, ressources) et la carte de couleurs des réglages ;
3. accueil : une `.puce` de niveau en tête de `.noeud-meta` (SNT, 1re, Tle, PP, Tous) ; un thème vide garde `est-vide` et reçoit le texte caché « (pas encore de ressource) » ;
4. ressource dont le type est cours-quiz : classe `res-cours-quiz` et `<span class="etiquette-signal">Cours-quiz</span>` avant le titre (à déduire d'un champ de la fiche plutôt que du titre) ;
5. fiche (`?r=`) : sans la colonne des filtres, `rub-corps lecture` ;
6. barre du haut : marque `>_`, boutons d'affichage avec `data-theme` ; pied de page : la ligne courte (auteur, licences, Code source sur GitHub, « conçu avec l'aide de l'IA ») puis les mentions actuelles ;
7. retirer le lien Google Fonts (et les `preconnect`) des 13 pages qui le chargent (hors documents de `fichiers/`) : `index.html`, `snt/`, `nsi-premiere/`, `nsi-terminale/`, `pp/`, `autres/`, `bibliotheque/`, `bibliotheque/annales/`, `admin/`, `eleve/`, `enseignant/`, et `charte/` (à moi) ; `theme-color` clair et obscur.

**Ensuite** : admin, espace élève, espace enseignant (formulaires) ; Calendrier ; puis les applications des autres dépôts (QuizzNSI, Gombessa, Lagon Arena, Court-circuit), qui gardent leur univers.
