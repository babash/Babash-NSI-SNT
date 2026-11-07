# Atelier de design : sources et outils de la charte « Réseau la nuit »

Travail de la conversation « Agent de design » (6 novembre 2026). **Statut : proposition, en attente de validation de l'enseignant.**
La charte elle-même est décrite dans le document de projet `design/charte.md` et dans `charte/index.html`.

Ce dossier ne sert pas au site : il contient de quoi reprendre et régénérer le travail.

## Ce qui est en place hors de ce dossier
| Fichier | Rôle |
|---|---|
| `assets/charte.css` | Polices auto-hébergées, couleurs (néon / encre), carte de runner |
| `assets/fiche.css`, `assets/fiche.js` | Documents A4 : encadrés, exercices, code, barre Retour / Projeter / Imprimer |
| `assets/fonts/` | Chakra Petch, Atkinson Hyperlegible, JetBrains Mono (woff2, licence SIL OFL) |
| `assets/equipage/`, `assets/equipage.js` | Portraits des 9 runners (nuit et trait), section « L'équipage » de l'accueil |
| `charte/` | Page de référence, planche des 9 cartes, « Ma carte de runner » |
| `snt/fichiers/python-compute-it.html`, `nsi-terminale/fichiers/td1-…`, `td2-…` | Documents convertis à la charte (texte inchangé) |
| `assets/style.css`, `*/index.html`, `assets/site.js` (2 lignes) | Site : polices locales, couleurs lisibles en clair, section équipage |

## Contenu de ce dossier
| Dossier | Contenu |
|---|---|
| `equipage/` | `runners.py` (les 9 runners : données et dessin SVG, fonction `portrait(r, mode)`), `equipage.py` (première version : icônes au trait), pages d'aperçu HTML, `apercus/` (captures) |
| `build/` | Générateurs : `equipage_assets.py` (SVG + `assets/equipage.js`, gabarit `equipage.tpl.js`), `cartes.py` (planches à imprimer), `charte_page.py` (`charte/index.html`), `python_fiche.py` (fiche Python), `td.py` (conversion des TD) |
| `sources/` | Les TD de POO avant conversion, lus par `build/td.py` |
| `outils/` | `capture.py` (captures et PDF avec Chrome, polices et CDN servis en local), `contrast.py` (contrastes WCAG), `debord.py` et `hauteurs.py` (débordement des feuilles A4), fichiers de travail CSS, `jobs/` (listes de captures) |
| `revue/` | La page avant / après présentée à l'enseignant, avec ses images |

## Reprendre le travail
Les scripts ont été écrits avec des chemins absolus. Avant de les lancer, recréer cette correspondance (ou adapter les chemins) :
- `/tmp/design/equipage/` ← `design/equipage/`
- `/tmp/design/build/` ← `design/build/`
- `/tmp/design/tools/` ← `design/outils/`
- `/tmp/design/td1-avant.html`, `td2-avant.html` ← `design/sources/`
- `/home/claude/babash-nsi-snt/` ← la racine du dépôt
- `/home/claude/revue/` ← `design/revue/`

Dépendances : Python 3 avec `playwright` et `Pillow`, Google Chrome (`/usr/bin/google-chrome`), `pdftoppm` (poppler).
`outils/fontmap.json` pointe vers les polices des paquets npm `@fontsource/*` (et `@fontsource/inter`, `@fontsource/fira-code`, `@fortawesome/fontawesome-free@6.4.0`, `tailwindcss@3` pour capturer l'ancienne fiche Python) : `npm pack` puis décompresser dans `/tmp/fonts` et `/tmp/vendor`.

Exemples :
```
python3 outils/capture.py outils/jobs/jobs-docs-after.json      # PDF des documents après
python3 outils/debord.py http://localhost:8800/nsi-terminale/fichiers/td1-poo-premiers-pas.html
python3 build/equipage_assets.py && python3 build/cartes.py && python3 build/charte_page.py
```
(servir la racine du dépôt avec `python3 -m http.server 8800`).

## À faire après validation
- Régénérer les PDF figés des TD 1 et 2.
- Reprendre les 2 lignes de `assets/site.js` (section équipage) si le moteur est réécrit pour la bibliothèque.
