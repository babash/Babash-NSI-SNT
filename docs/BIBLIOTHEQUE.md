# Les données de la bibliothèque (dossier `donnees/`)

*L'onglet Bibliothèque, le format des fiches des ressources, leur validation et leur construction à chaque publication. Retour au [README](../README.md).*

Le site réunit toutes les ressources dans une bibliothèque unique : l'**onglet Bibliothèque**
(`bibliotheque/`), depuis le 17 novembre 2026. Son format a été validé par l'enseignant le
7 novembre 2026. Les pages des rubriques, elles, continuent d'utiliser les listes `ressources.js`
([LISTES.md](LISTES.md)), jusqu'à leur conversion.

## L'onglet Bibliothèque

La page `bibliotheque/` montre les ressources qui ont au moins un document visible de
l'extérieur (aujourd'hui toutes, puisque rien n'est caché), avec ces documents seulement :

- une **recherche** par mots-clés et par notions : elle comprend les synonymes du thésaurus,
  tolère les fautes de frappe et fouille aussi le texte des documents hébergés sur le site
  (chargé à la première recherche) ;
- des **filtres** sur tous les classements : enseignement, niveau, programme officiel, notions
  travaillées, type, modalités, prérequis, durée, documents, formats, langages, données d'élèves,
  origine, autrices et auteurs, compétences Pix, statut de la fiche ;
- un tri, deux vues (liste ou cartes) et la **fiche complète** de chaque ressource
  (`?r=identifiant`), avec ses documents et sa place dans les rubriques ;
- une adresse qui garde la recherche, les filtres, le tri et la vue : elle se partage telle quelle.

Elle ne lit pas les fiches une à une : `scripts/construire_bibliotheque.py` les rassemble en
trois fichiers, à chaque publication, dans le workflow « Publier le site » (voir
[la mise en ligne](VERIFICATION.md#la-mise-en-ligne)) :

- `donnees/bibliotheque.json`, la vue de l'extérieur, avec les référentiels et la vitrine, que la
  page lit ;
- `donnees/bibliotheque-complete.json`, tout, avec ce que voit chaque public, pour
  l'[espace administrateur](ADMIN.md), qui modifie les fiches et la vitrine ;
- `donnees/bibliotheque-textes.json`, le texte des documents hébergés (pages HTML, textes, PDF),
  pour la recherche dans le contenu.

Ces fichiers ne sont **jamais commités** (`.gitignore` les écarte) : les fiches restent la seule
source, et une fiche modifiée suffit à mettre la bibliothèque à jour à la publication suivante.
La construction commence par la validation complète : une seule erreur l'arrête, et rien n'est
publié. Pour essayer la bibliothèque sur ton ordinateur, à la racine du dépôt :
`python3 scripts/construire_bibliotheque.py`, puis `python3 -m http.server`, et
`http://localhost:8000/bibliotheque/`. Ses tests : `python3 -I -B scripts/tests/test_bibliotheque.py`
et `node scripts/tests/test_recherche.js`. Le contrôle du site en ligne vérifie la bibliothèque
publiée après chaque envoi sur `main` ([VERIFICATION.md](VERIFICATION.md)).

## Les fichiers

```
donnees/
  README.md                     le format en détail, pour l'enseignant et pour les agents
  ressources/<id>.json          une fiche par ressource : 119 fiches, dont 82 pour les 90 entrées des
                                listes (une ressource placée dans deux rubriques n'a qu'une fiche),
                                8 pour des fichiers récupérés des conversations de l'enseignant,
                                19 pour des activités Capytale, 4 pour des ressources tirées d'une
                                archive de projets de l'enseignant, 1 pour un site externe demandé
                                par l'enseignant (l'entraînement à l'épreuve pratique d'exomorphisme.fr)
                                et 5 pour des cours, TD et devoirs de NSI faits avec Johanne Bakalara
                                (projets Overleaf, PDF et sources LaTeX)
  vitrine.json                  la mise en avant de la partie extérieure : ce que le site affiche
                                aujourd'hui, plus la section « Intelligence artificielle » de SNT
                                et la grille d'évaluation du Grand oral
  vitrine.exemple.json          l'exemple de mise en avant qui a servi à valider le format
  referentiels/                 l'arbre des programmes, le thésaurus des notions, les listes de valeurs,
                                les compétences Pix
  schema/                       la description exacte du format (JSON Schema)
  correspondance-etiquettes.md  comment les listes actuelles seront converties
  bibliotheque*.json            construits à chaque publication, jamais commités (ci-dessus)
scripts/valider_donnees.py      la validation des données
scripts/tests/test_notions.py   ses tests pour le thésaurus, les notions des fiches et la visibilité
scripts/construire_bibliotheque.py  la construction des fichiers de l'onglet Bibliothèque
bibliotheque/                   la page de l'onglet ; son programme est assets/bibliotheque.js,
                                et sa recherche assets/recherche.js
```

## Les fiches

Une fiche décrit une ressource et ses documents (activité, version PDF, corrigé, code
source…). Chaque document a deux réglages de visibilité, pour l'extérieur et pour les élèves.
Pour l'instant, on ne cache rien : tous les documents sont visibles de l'extérieur comme des
élèves, et l'enseignant réglera lui-même la visibilité, à la main (consigne du 12 novembre 2026).
La fiche signale aussi si la ressource collecte des données d'élèves (`donnees_eleves`).
Elle crédite ses auteurs et autrices (`auteurs`, `credits`) ; une ressource reprise et
modifiée crédite toute la chaîne. Par exemple, la fiche de CyberCase cite Etienne Clave
(exomorphisme.fr, lycée de Sada), l'idée de Marion Dufour, le moteur SQL Noir de Hristo
Bogoev, puis la reprise par Babash - NSI Tani Malandi.

Une fiche range aussi la ressource selon ce qu'elle fait apprendre, plus finement que le
programme : ses **notions** (`notions`), tirées du thésaurus `referentiels/notions.json`, avec
leur rôle : travaillées (`travaillees`) ou prérequises (`prerequises`). Les notions travaillées
réunissent ce que la ressource fait apprendre et ce qu'elle évalue (les propriétés `teaches` et
`assesses` que schema.org a reprises de LRMI pour les ressources pédagogiques) ; les prérequises
correspondent à `competencyRequired`. Qu'une ressource évalue se lit à son type pédagogique
(évaluation, quiz) et à ses usages (auto-correctif) : séparer les notions enseignées et les
notions évaluées était, pour l'enseignant, une mauvaise nomenclature (décision du 13 novembre
2026). Le thésaurus suit le modèle de SKOS (W3C) et de la norme ISO 25964 : 177 notions en
12 domaines, de la plus large à la plus précise (programmation › structures de contrôle ›
boucle › boucle bornée), avec leurs synonymes, leurs termes anglais, les mots du code, les
thèmes du programme où elles sont enseignées, leurs correspondances avec le *K–12 Computer
Science Framework*, l'*Informatics Reference Framework for School* et CS2023, et, pour 36
d'entre elles, 57 difficultés connues des élèves, avec leurs sources : des études, et des
relevés d'enseignant·e·s, dont le constat de l'enseignant dans ses classes (la trace
d'exécution, la modélisation d'un problème et la compréhension globale d'un programme). Un
historique dit ce que chaque version a ajouté ou modifié. Il sert à la recherche et aux filtres
de l'onglet Bibliothèque. Proposé par l'Architecte, publié le 12 novembre 2026 et complété le
même jour, il a été validé le 13 novembre 2026 par l'enseignant, qui peut toujours revenir sur
une notion. Un identifiant de notion publié ne disparaît jamais : une notion abandonnée
reste, marquée obsolète. Les mots-clés libres (`mots_cles`) restent.

Quand c'est utile, la fiche note aussi :

- les **compétences Pix** d'une ressource de SNT (`competences_pix`), choisies parmi les 16 de
  `referentiels/competences-pix.json`. Les intitulés affichés sont ceux de la plateforme Pix,
  que voient les élèves. Quand le décret de 2019 (cadre de référence des compétences
  numériques) les écrit autrement, son texte est gardé dans `libelle_decret` : c'est le cas
  de « Création de contenu » (« de contenus » dans le décret) et de « Construire un
  environnement numérique » (« Évoluer dans un environnement numérique ») ;
- pour une ressource où l'élève écrit du code : l'usage `editeur-de-code`, qui servira de
  filtre dans la bibliothèque, et le champ `editeur_code`. Ce champ note les cinq critères de
  la règle 20, chacun par `true` ou `false` : `coloration` (coloration syntaxique),
  `indentation` (la touche Tab indente), `guides_indentation` (les blocs visibles, sur le
  modèle de Lagon Arena), `autocompletion` (contextualisée) et `erreurs_expliquees` (l'erreur
  telle quelle, puis traduite ou expliquée en français), avec une `remarque` facultative ;
- pour un TD, le champ facultatif `td_en_ligne` (règle 19) : la page en ligne est-elle
  `responsive` (du téléphone au grand écran) et `auto_corrective` (un formulaire corrigé dans
  le navigateur) ? La version PDF et la page HTML, elles, se lisent dans les documents ;
- les critères de réussite (`criteres_reussite`), au cas par cas.

Pour une création de l'enseignant, un critère à `false`, ou un éditeur de code dont les
critères ne sont pas notés, donne un avertissement du script de validation ; pour une
ressource externe, qui ne se modifie pas, c'est une simple information. Quinze fiches ont un
avertissement, car ce sont des écarts réels : l'éditeur d'Alien Python, une zone de texte
simple, ne remplit aucun des cinq critères ; les pages des TD 1 et 2 de POO ne sont ni
responsives ni auto-correctives ; la licence de la fiche Python de SNT, faite d'après la fiche
Compute-it, n'est pas connue ; deux sites de collègues ne sont qu'en `http://` ; les critères de
l'éditeur de neuf notebooks Capytale de l'enseignant (l'éditeur de Capytale) restent à noter. Ces
écarts seront repris lors de la revue des ressources publiées ; d'ici là, la validation avec
`--strict` (ci-dessous) échoue sur ces quinze avertissements.

Les fiches écrites le 12 novembre 2026 ont le statut « à revoir » : l'enseignant les relira. Le
Système d'exploitation humain, jamais essayé en classe et pas fini, a le statut « brouillon ».
L'onglet « Bibliothèque » les affiche toutes, avec leur statut ; la vitrine, elle, ne change pas
encore les pages des rubriques. Les huit ressources récupérées des conversations (quatre fiches de
réseaux de terminale, les commandes Linux de première et leur corrigé, la fiche des erreurs
Python, le diaporama sur l'IA en SNT, la grille du Grand oral) sont en ligne dans les dossiers
`fichiers/` des rubriques et dans la bibliothèque, mais les listes `ressources.js` ne les montrent
pas encore.

Il en va de même pour les 21 activités Capytale ajoutées le 16 novembre 2026, à partir des
exports de l'enseignant : 19 fiches nouvelles et deux fiches complétées (le sapin des fonctions
et le Pokédex), au statut « à revoir ». Leurs fichiers sont dans les dossiers `fichiers/capytale/`
des rubriques (voir [L'organisation du dépôt](ORGANISATION.md#les-activités-capytale)) : le
notebook, sorties vidées, sans donnée d'élève, une page de lecture et les fichiers à joindre ; leur
lien principal est la page de lecture. Les activités qui ne nomment pas d'autre auteur·rice sont
attribuées à l'enseignant, à confirmer. Celles de collègues sont hébergées avec toute la chaîne de
leurs crédits, seulement quand leur licence permet de les diffuser, et gardent cette licence : la
fiche le dit (`licence`, `credits`), et trois d'entre elles sont sous licence non commerciale
(voir [Licence](../README.md#licence)). Quand un original public existe, la fiche le donne aussi en
« Code source ». Les activités sans auteur nommé ou sans licence connue sont restées de côté.

De même pour quatre ressources tirées, le 16 novembre 2026, d'une archive de projets de
l'enseignant, au statut « à revoir » : la découverte des listes (sujet et corrigé, notebooks,
`nsi-terminale/fichiers/decouverte-listes/`), l'Opération GHOST, la version de première de MIRAGE
(`nsi-premiere/fichiers/operation-ghost/`), le TP de SNT « le reboucheur de donuts », une page web
en 20 défis (`snt/fichiers/web-interview-donuts/`), et le voyageur de commerce à Mayotte, une page
sans connexion (`nsi-terminale/fichiers/voyageur-de-commerce-mayotte/`). Les bibliothèques que le
TP des donuts emploie (Bootstrap, reveal.js) sont copiées dans son dossier, avec leur licence : la
page ne charge rien d'un autre site.

Pour valider les données, depuis le dossier du site : `python3 scripts/valider_donnees.py`
(Python 3 seul, rien à installer ; avec `--strict`, les avertissements bloquent aussi). Chaque
message donne le fichier et le champ. Le script signale comme erreur, entre autres, un lien
principal vers GitHub, un identifiant en double, une référence inexistante (une notion absente
du thésaurus comprise), un document sans réglage de visibilité, et tout ce qui ressemble à un
mot de passe, un identifiant ou une clé secrète. Il vérifie aussi le thésaurus lui-même :
notions plus larges et associées existantes, hiérarchie sans cycle, libellés préférés uniques
(la recherche compare les racines des mots : « test » et « Tests » se confondraient), historique
cohérent. Les anciens rôles des notions (`enseignees`, `evaluees`) sont refusés depuis la
conversion des fiches du 13 novembre 2026 (`scripts/convertir_notions_t64.py`) ; l'option
`--anciens-roles signaler` les tolère encore, pour vérifier une copie pas encore convertie. Avec `--avant F`, il compare le thésaurus à une version précédente `F` (celle de
`main`, par exemple : `git show origin/main:donnees/referentiels/notions.json > F`) : une notion
de `F` qui a disparu est une erreur. Ses tests : `python3 -I -B scripts/tests/test_notions.py`.

Le format en détail, pour l'enseignant et pour les agents : [`donnees/README.md`](../donnees/README.md).
