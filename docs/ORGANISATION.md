# L'organisation du dépôt

*Les dossiers et les fichiers du site. Retour au [README](../README.md).*

Le site est publié par GitHub Pages depuis la branche `main`, dossier racine : les pages et les fichiers déposés sont en ligne à la même place, sous `https://babash.github.io/Babash-NSI-SNT/` ([Activer GitHub Pages](REUTILISER.md#activer-github-pages-une-seule-fois)).

```
README.md                   la présentation du site
CONTRIBUTING.md             les règles du travail sur GitHub
docs/                       la documentation : ce fichier et les autres
LICENSE                     la licence MIT du code
CLAUDE.md                   les règles communes de l'équipe d'agents
.claude/agents/             la fiche de chaque rôle
index.html                  l'accueil (ne pas toucher)
reglages.js                 titre du site, liste des rubriques, textes du pied de page
snt/
  ressources.js             ← la liste de la rubrique SNT
  fichiers/                 ← les PDF et fiches de la rubrique SNT
    capytale/<id>/          les activités Capytale : notebook (.ipynb), page de lecture, fichiers à joindre
  index.html                (ne pas toucher)
nsi-premiere/   …           même organisation pour chaque rubrique
nsi-terminale/  …
pp/             …
autres/         …
assets/                     mise en page et fonctionnement (ne pas toucher)
donnees/                    le format de la future bibliothèque (BIBLIOTHEQUE.md)
.github/                    vérification automatique (VERIFICATION.md) et outils du Gardien (GARDIEN.md)
scripts/                    vérification automatique, validation des données, script complet de la base
supabase/                   le socle commun de la base des applications (SUPABASE.md)
```

Chaque fichier a un rôle propriétaire : voir [L'équipe d'agents](AGENTS.md).

## Les activités Capytale

Les dossiers `fichiers/capytale/<id>/` de SNT, de NSI Première et de NSI Terminale réunissent
21 activités Capytale de l'enseignant et de collègues (novembre 2026), une par dossier, nommé
d'après l'identifiant de sa fiche (`donnees/ressources/<id>.json`). Chaque dossier contient le
notebook à importer dans Capytale ou Basthon (`.ipynb`, sorties vidées), une page de lecture
(`lecture.html`, qui affiche le notebook sans compte et ne l'exécute pas) et les fichiers à
joindre (modules Python, images, données). Chaque activité garde sa licence, donnée au pied de
sa page et dans sa fiche ; trois d'entre elles sont sous licence non commerciale (voir
[Licence](../README.md#licence)). Les listes `ressources.js` ne les montrent pas encore :
l'onglet « Bibliothèque » les lira.

## Le décor

La ville, sa liaison montante et le sol quadrillé du bandeau sont un dessin original, généré
par `assets/site.js` (fonction `scene`) dans la couleur de chaque rubrique. Les couleurs
générales des deux affichages sont en haut de `assets/style.css`.
