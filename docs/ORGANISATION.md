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
    <dossier>/<td>/         un TD au style « Signal pirate » : sa page en ligne (index.html, feuille-2.html…) ;
                            son PDF, à côté (<td>.pdf), est sa feuille vierge ; source/ garde le LaTeX
                            d'origine et le script qui calcule les réponses
  index.html                (ne pas toucher)
nsi-premiere/   …           même organisation pour chaque rubrique
nsi-terminale/  …
pp/             …
autres/         …
bibliotheque/               l'onglet Bibliothèque (ne pas toucher)
  annales/                  la page des annales du bac NSI par notion (assets/annales.js), liée
                            depuis la bibliothèque
admin/                      l'espace administrateur (ADMIN.md ; ne pas toucher)
eleve/                      le compte commun, côté élève (« Ma planque » : l'avatar, la boutique, les
                            trophées, les hauts faits, la classe), en service depuis le 24/11/2026 sur
                            la base (fonctions commun_…) : sans lien depuis le site, non indexé
                            (assets/planque.js, assets/compte-commun.js ; docs/COMPTE-COMMUN.md)
enseignant/                 l'espace enseignant·e du compte commun, en service de la même façon
                            (assets/espace-enseignant.js ; QR codes : assets/qrcode-generator.js) ;
                            COMPTE_COMMUN_EN_LIGNE: false dans reglages.js les remet en démonstration
calendrier/                 le Calendrier des vacances, en service depuis le 20/11/2026 : la page des élèves
                            (index.html), l'espace enseignant·e (prof.html), les banques d'exercices
                            (exercices/, contrôlées à chaque envoi et à chaque publication) et les migrations de sa base
                            (supabase/, voir SUPABASE.md)
assets/                     mise en page et fonctionnement (ne pas toucher)
  signal-commun.css         la palette et les polices communes au site et aux TD (style « Signal
                            pirate », 21/11/2026), leur seule source depuis le 24/11/2026 ;
                            style.css, chargé après lui : la mise en page du site
  td-en-ligne.js, .css      le moteur des TD en ligne auto-correctifs (Python, avec Pyodide, chargé
                            à la demande depuis jsDelivr, jamais copié dans le dépôt) et leur style
                            « Signal pirate » : une seule feuille de style pour l'écran clair,
                            l'écran obscur et le papier, qui charge signal-commun.css (@import)
  td/                       les dessins des TD, repris par le bandeau du site : les 4 bandeaux qui
                            tournent (avec leurs variantes de 20 mm pour les contrôles et leurs
                            versions obscures), la marge et le margouillat caché
                            (places-margouillat.json : ses cachettes) ; refaits par
                            charte/bandeaux-td.py
  fonts/                    les polices des TD et du site, hébergées sur le site (aucun appel à un
                            serveur de polices), avec leurs licences (LISEZMOI.md)
  equipage.js, equipage/    le moteur d'avatars (pixel art, sans dépendance ; version 2.1, avec
                            l'interface des applications de jeu) ; equipage/ : son contrat
                            (LISEZMOI.md), son catalogue (catalogue.json) et le fichier des
                            applications (applis.json : les phrases de la liste fermée, les gestes,
                            les objets de trophée et leurs hauts faits), générés depuis le module par
                            charte/equipage-donnees.js : ne pas les modifier à la main
  applis.css                le socle d'habillage des applications de jeu (le design du site et une
                            touche propre à chacune, data-appli), chargé après signal-commun.css ;
                            mode d'emploi : charte/applis.md
charte/                     les pages de démonstration du Designer, sans lien depuis le site et non
                            indexées, et les outils des TD : le gabarit (gabarit-td/ : le modèle
                            commenté, un exemple rendu et LISEZMOI.md, le mode d'emploi des
                            Ateliers), le TD pilote (td-pilote/, avec son PDF), le script qui crée
                            le squelette d'un TD (nouveau-td.py), le vérificateur de ses réponses
                            (verifier-td.py), le script qui fait le PDF depuis la feuille vierge et
                            contrôle sa mise en page (imprimer-td.py, qui réunit aussi les
                            feuilles d'un TD en un seul PDF), celui qui dessine les bandeaux
                            (bandeaux-td.py), celui qui les répartit entre tous les TD
                            (reattribuer-bandeaux.py), celui qui refait la police « TD Symboles »
                            (symboles-td.py), celui qui fait continuer les numéros des questions
                            d'une feuille à l'autre (numeroter-feuilles.py), celui qui essaie les
                            outils des TD sur des témoins de fuite (tester-outils.py), la
                            démonstration du moteur d'avatars (avatars.html), celle du socle des
                            applications (applis.html, avec son mode d'emploi applis.md) et les
                            essais du moteur (tester-equipage.js, joué à chaque envoi par
                            « Vérifier le site », et tester-applis.py, dans Chromium), et celui
                            du miroir coloré de l'éditeur d'Alien Python (tester-alien-miroir.py)
qcm/                        les QCM Pronote (qcm/LISEZMOI.md) : par niveau (snt/, nsi-premiere/,
                            nsi-terminale/), le fichier XML Moodle à importer dans Pronote, l'aperçu
                            élève et le corrigé enseignant·e de chaque quiz, liés depuis sa fiche de la
                            bibliothèque (pas depuis les onglets) ;
                            sources/ (les sources JSON, d'où tout est construit) et outils/
                            (construire_qcm.py, verifier_qcm.py)
donnees/                    les fiches et les référentiels de la bibliothèque (BIBLIOTHEQUE.md) ;
                            ses fichiers bibliotheque*.json sont construits à la publication
  annales/                  l'inventaire des sujets du bac de NSI, mis à jour chaque 1er janvier et
                            1er août (annales/LISEZMOI.md), et le classement de leurs exercices par
                            chapitre (notions-par-exercice.json, construit par
                            scripts/annales_notions.py) ; la page bibliotheque/annales/ les lit
  compte-commun/            les apparences de l'avatar du compte commun (apparences.json, construit par
                            scripts/apparences_compte_commun.py depuis assets/equipage/catalogue.json,
                            à relancer quand le catalogue change ; pas encore relancé pour la
                            version 2.1 du moteur : la famille « applis », des trophées, est d'abord
                            à ajouter aux familles de trophées du script) et les tableaux de bord
                            des applications (tableaux-de-bord.json)
.github/                    publication et vérification automatique (VERIFICATION.md), outils du Gardien (GARDIEN.md)
scripts/                    vérification automatique, validation des données, construction de la
                            bibliothèque, script complet de la base, et les dépôts renommés
                            (depots-renommes/, avec l'outil renommer_depots.py)
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

Depuis le 21 novembre 2026, le site a le style des TD, « Signal pirate » (maquette validée par
l'enseignant). Le bandeau de chaque page est l'un des quatre paysages de Mayotte des TD
(`assets/td/`, dessins originaux), tiré à chaque page par `assets/site.js` (fonction `bandeau`),
jamais deux fois de suite le même ; `?bandeau=1` à `?bandeau=4`, ajouté à l'adresse, en force un.
Le margouillat vert s'y cache à l'une des places prévues pour ce paysage
(`assets/td/places-margouillat.json`). Aucune couleur n'est propre à une rubrique : le niveau est
écrit dans une puce (SNT, 1re, Tle, PP, Tous). La palette et les polices, en clair et en obscur,
sont dans `assets/signal-commun.css`, commune au site et aux TD ; la mise en page du site est dans
`assets/style.css`. Depuis le 24 novembre 2026 (T123d), `assets/td-en-ligne.css` charge
`signal-commun.css` par `@import` (sa première règle) : la palette n'a plus qu'une source, et la règle
« les lignes 18 à 133 de `signal-commun.css` sont les lignes 19 à 134 de `td-en-ligne.css` » n'a plus
cours (il n'y a plus de copie à garder identique). Une couleur ou une police se change donc dans
`signal-commun.css` seulement, et le changement vaut à la fois pour le site, les TD et le Calendrier
des vacances, qui la charge aussi depuis le 24 novembre 2026 : sa feuille (`calendrier/calendrier.css`)
ne garde que la mise en page de ses écrans, sans couleur propre.
