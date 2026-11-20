# L'organisation du dépôt

*Les dossiers et les fichiers du site. Retour au [README](../README.md).*

Le site est publié par GitHub Pages à partir de la branche `main`, par le workflow « Publier le site » ([la mise en ligne](VERIFICATION.md#la-mise-en-ligne)) : les pages et les fichiers déposés sont en ligne à la même place, sous `https://babash.github.io/Babash-NSI-SNT/`, avec les fichiers de la bibliothèque, construits à la publication et jamais commités ([Activer GitHub Pages](REUTILISER.md#activer-github-pages-une-seule-fois)).

```
README.md                   la présentation du site
CONTRIBUTING.md             les règles du travail sur GitHub
docs/                       la documentation : ce fichier et les autres (sommaire : docs/README.md)
  pedagogie/                la pédagogie : philosophie, règles universelles, types de ressources
LICENSE                     la licence MIT du code
CLAUDE.md                   les règles communes de l'équipe d'agents
.claude/agents/             la fiche de chaque rôle
index.html                  l'accueil (ne pas toucher)
reglages.js                 titre du site, liste des rubriques, textes du pied de page
snt/
  ressources.js             l'ancienne liste de la rubrique SNT, plus lue depuis le 17/11/2026
  fichiers/                 ← les PDF et fiches de la rubrique SNT
    capytale/<id>/          les activités Capytale : notebook (.ipynb), page de lecture, fichiers à joindre
  index.html                (ne pas toucher)
nsi-premiere/   …           même organisation pour chaque rubrique
nsi-terminale/  …
pp/             …
autres/         …
bibliotheque/               l'onglet Bibliothèque (ne pas toucher)
  annales/                  la page des annales du bac NSI par notion (assets/annales.js), liée
                            depuis la bibliothèque
admin/                      l'espace administrateur (ADMIN.md ; ne pas toucher)
eleve/                      le compte commun, côté élève (« Ma planque » : l'avatar, les hauts faits, la
                            classe), en démonstration depuis le 20/11/2026 : sans lien depuis le site, non
                            indexé ; données fictives, rien n'est envoyé ni gardé (assets/planque.js,
                            assets/compte-commun.js)
enseignant/                 l'espace enseignant·e du compte commun, en démonstration de la même façon
                            (assets/espace-enseignant.js)
calendrier/                 le Calendrier des vacances, en service depuis le 20/11/2026 : la page des élèves
                            (index.html), l'espace enseignant·e (prof.html), les banques d'exercices
                            (exercices/, contrôlées à chaque publication) et les migrations de sa base
                            (supabase/, voir SUPABASE.md)
assets/                     mise en page et fonctionnement (ne pas toucher)
  td-en-ligne.js, .css      le moteur des TD en ligne auto-correctifs (Python, avec Pyodide, chargé
                            à la demande depuis jsDelivr, jamais copié dans le dépôt)
charte/                     les pages de démonstration du Designer, sans lien depuis le site et non
                            indexées : le TD pilote du moteur des TD en ligne (td-pilote/, avec son
                            PDF) et le vérificateur de ses réponses (verifier-td.py)
donnees/                    les fiches et les référentiels de la bibliothèque (BIBLIOTHEQUE.md) ;
                            ses fichiers bibliotheque*.json sont construits à la publication
  annales/                  l'inventaire des sujets du bac de NSI, mis à jour chaque 1er janvier et
                            1er août (annales/LISEZMOI.md), et le classement de leurs exercices par
                            chapitre (notions-par-exercice.json, construit par
                            scripts/annales_notions.py) ; la page bibliotheque/annales/ les lit
  compte-commun/            les apparences de l'avatar du compte commun (apparences.json, construit par
                            scripts/apparences_compte_commun.py depuis le catalogue du moteur d'avatars)
                            et les tableaux de bord des applications (tableaux-de-bord.json)
.github/                    publication et vérification automatique (VERIFICATION.md), outils du Gardien (GARDIEN.md)
scripts/                    vérification automatique, validation des données, construction de la
                            bibliothèque, script complet de la base
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
[Licence](../README.md#licence)). La bibliothèque les montre toutes ; les rubriques, celles que la
vitrine place (le sapin des fonctions et le Pokédex, pour l'instant).

## Le décor

La ville, sa liaison montante et le sol quadrillé du bandeau sont un dessin original, généré
par `assets/site.js` (fonction `scene`) dans la couleur de chaque rubrique. Les couleurs
générales des deux affichages sont en haut de `assets/style.css`.
