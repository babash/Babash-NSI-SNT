# 🗂️ Ressources NSI et SNT

**Cours, activités et outils pour la classe, rangés par niveau et par thème.** Pour la SNT, la NSI de 1re et de terminale, et le rôle de professeur·e principal·e.

> Pour chaque thème du programme, les collègues trouvent des ressources prêtes pour la classe : des jeux et des applications où les élèves programment, des TD à imprimer, des activités débranchées, et une sélection de sites ressources. Chaque ressource dit ce que font les élèves, sur ordinateur, sur téléphone ou sur papier.

## 👉 [Ouvrir le site : babash.github.io/Babash-NSI-SNT](https://babash.github.io/Babash-NSI-SNT/)

**Gratuit · sans compte · rien à installer · le site n'enregistre rien sur les élèves ; les ressources qui le font le signalent**

Le site a cinq rubriques : SNT, NSI Première, NSI Terminale, Professeur principal et Autres.
Chaque rubrique a **sa propre liste de ressources**, dans un petit fichier texte que tu modifies
directement sur GitHub. Une ressource peut être un lien vers un site, ou un fichier déposé
sur le site (PDF, fiche HTML, diaporama…).

Les rubriques suivent les **textes officiels** :

| Rubrique | Texte de référence | Thèmes du site |
|---|---|---|
| SNT | Programme de SNT, BO spécial n° 1 du 22 janvier 2019 | Les 7 thèmes et les notions transversales de programmation |
| NSI Première | Programme de NSI de première, BO spécial n° 1 du 22 janvier 2019 | Les 8 rubriques, avec la colonne « Contenus » |
| NSI Terminale | Programme de NSI de terminale, BO spécial n° 8 du 25 juillet 2019 | Les 6 rubriques, avec la colonne « Contenus » |
| Professeur principal | Circulaire n° 2018-108 du 10 octobre 2018 | Les missions de professeur·e principal·e |

Le site s'affiche en clair ou en obscur : par défaut il suit le réglage de l'appareil, et le
choix fait dans la barre du haut (Auto, Clair, Obscur) est retenu par le navigateur.

```
reglages.js                 titre du site, liste des rubriques, textes du pied de page
snt/
  ressources.js             ← la liste de la rubrique SNT
  fichiers/                 ← les PDF et fiches de la rubrique SNT
  index.html                (ne pas toucher)
nsi-premiere/   …           même organisation pour chaque rubrique
nsi-terminale/  …
pp/             …
autres/         …
assets/                     mise en page et fonctionnement (ne pas toucher)
donnees/                    le format de la future bibliothèque (voir plus bas)
.github/                    vérification automatique et outils du Gardien (voir plus bas)
scripts/                    vérification automatique, validation des données, script complet de la base
supabase/                   le socle commun de la base des applications (voir « Applications qui utilisent Supabase »)
```

**Règle des liens** : le lien principal d'une ressource mène **directement** à la ressource
(la page de l'activité, la fiche, le PDF), jamais à un dépôt GitHub ou à un fichier affiché
par GitHub. Le dépôt, lui, doit toujours être indiqué, en lien secondaire (décision de
l'enseignant du 10 novembre 2026) : une ressource qui a un dépôt le donne en annexe, sous le
nom « Code source », et chaque page publiée (ce site, les applications, les pages en ligne des
TD) porte en pied de page un lien « Code source sur GitHub » vers son dépôt, à côté de l'auteur
et de la licence. Pour une ressource externe, qu'on ne modifie pas, on donne son dépôt en
annexe s'il est public. Depuis le 11 novembre 2026, toutes les ressources des listes conçues
par Babash - NSI Tani Malandi qui ont un dépôt le donnent en annexe, et le lien « Code source
sur GitHub » est en bas des pages de ce site, de ses pages déposées dans les dossiers `fichiers`
et des applications. Pour ce site, le contrôle du site en ligne le vérifie (voir
« Vérification automatique »).
Quand une activité n'a pas de page en ligne, ses fichiers sont déposés dans le dossier
`fichiers` de la rubrique (c'est le cas de `nsi-terminale/fichiers/os-humain/`).

---

## Ajouter une ressource en ligne

1. En bas de la page de la rubrique, clique sur **Modifier la liste**.
   Ou bien, sur GitHub : ouvre le fichier `ressources.js` de la rubrique, puis clique sur le crayon.
2. Repère le bon thème (les lignes `theme("…");`) et colle ce bloc en dessous :

```js
ressource({
  titre: "Nom de la ressource",
  lien: "https://adresse-de-la-ressource",
  texte: "Ce que font les élèves, en une ou deux phrases.",
  tags: ["En ligne"],
});
```

3. Clique sur **Commit changes**. Le site se met à jour en une minute environ.

L'ordre dans le fichier est l'ordre sur la page. Le compteur du thème, le nom du site
affiché sous la ressource et l'ouverture dans un nouvel onglet se font tout seuls.

## Ajouter un PDF (ou n'importe quel fichier)

1. En bas de la page de la rubrique, clique sur **Déposer un fichier** : le fichier va
   directement dans le dossier `fichiers` de la rubrique. Valide avec **Commit changes**.
2. Ajoute-le à la liste comme une ressource en ligne, avec le nom du fichier :

```js
ressource({
  titre: "TP parcours de graphes",
  lien: "fichiers/tp-graphes.pdf",
  texte: "Parcours en largeur et en profondeur.",
  tags: ["À imprimer"],
});
```

Le site affiche « PDF » sous la ressource et l'ouvre dans un nouvel onglet.
Les fichiers que le navigateur ne sait pas afficher (`.py`, `.odt`, `.docx`, `.zip`…)
sont téléchargés quand tu cliques dessus.

> Conseil : des noms de fichiers sans espaces ni accents (`tp-graphes.pdf` plutôt que `TP Graphes é.pdf`).

## Une ressource avec plusieurs liens (sujet, corrigé, version en ligne…)

Ajoute `annexes`. Chaque ligne donne le texte du lien, puis son adresse ou son fichier :

```js
ressource({
  titre: "TP parcours de graphes",
  lien: "fichiers/tp-graphes.pdf",
  texte: "Parcours en largeur et en profondeur.",
  annexes: {
    "Corrigé": "fichiers/tp-graphes-corrige.pdf",
    "Code de départ": "fichiers/graphes.py",
    "Version Capytale": "https://capytale2.ac-paris.fr/…",
  },
});
```

## Les champs d'une ressource

| Champ | Obligatoire | Contenu |
|---|---|---|
| `titre` | oui | Le nom affiché, en gros |
| `lien` | non | Une adresse `https://…` ou un fichier `fichiers/…` |
| `texte` | non | La description. Tu peux écrire du `code` entre accents graves et du **gras** entre doubles étoiles |
| `tags` | non | Des étiquettes entre crochets : `["En ligne", "Python"]` |
| `annexes` | non | Des liens en plus (voir ci-dessus) |

Étiquettes déjà utilisées : `En ligne`, `À imprimer`, `Débranché`, `Python`, `SQL`, `Jeu`,
`Cours`, `Notebook`, `Connexion ENT`, `Rien à installer`, `À adapter`, `Pour aller plus loin`,
`Ressource du mois`. Tu peux en inventer d'autres.

L'étiquette `Ressource du mois` met en avant une ressource (en ce moment : CyberCase, en SNT
et en NSI Terminale). Chercher « ressource du mois » sur l'accueil la retrouve ; il suffit
d'enlever l'étiquette le mois suivant.

La recherche de la page d'accueil fouille les titres, textes, étiquettes et thèmes de
toutes les rubriques. Tu peux partager une recherche : `…/Babash-NSI-SNT/?q=débranché`.

---

## Organiser une rubrique

Dans `ressources.js` :

- `theme("Algorithmique");` commence un nouveau thème. Les ressources en dessous lui appartiennent.
- Nom long : `theme("Représentation des données : types construits", { court: "Types construits" });`
  Le nom court sert dans le sommaire et dans l'adresse (`…/nsi-premiere/#types-construits`).
- Couleur : `theme("Sites ressources", "gris");` Couleurs possibles : bleu, vert, violet, rose,
  orange, citron, cyan, jaune, lavande, corail, gris. Sans couleur, le site en choisit une.
- `groupe("Pour aller plus loin");` ajoute un sous-titre à l'intérieur d'un thème.
- Un thème sans ressource affiche « Rien ici pour l'instant » : tu peux le laisser en attendant.

### Ranger selon le programme officiel

Chaque thème de NSI et de SNT liste les contenus du BO dans `programme` :

```js
theme("Structures de données", {
  programme: [
    "Structures de données, interface et implémentation",
    "Vocabulaire de la programmation objet",
    "Arbres",
  ],
});

groupe("Arbres");          // exactement le même intitulé que dans la liste

ressource({ titre: "Fiche : les arbres", lien: "…" });
```

Sur la page, la ligne « Au programme » affiche tous les contenus. Ceux qui ont au moins une
ressource deviennent des liens vers leur sous-section ; les autres restent en pointillés,
ce qui montre d'un coup d'œil ce qui reste à couvrir.

La référence du texte officiel s'affiche sous la présentation de la rubrique. Elle se règle
dans `rubrique({ … })` :

```js
programme: {
  texte: "Programme de NSI de terminale, BO spécial n° 8 du 25 juillet 2019",
  lien: "https://…",
},
```

## Ajouter une rubrique

1. Crée un dossier, par exemple `mathematiques`, avec une copie de `autres/index.html`
   et de `autres/ressources.js`. Change le nom dans `rubrique({ … })`.
2. Dans `reglages.js`, ajoute `"mathematiques",` à la liste des rubriques.

Une rubrique absente de `reglages.js` reste visible à son adresse, mais n'apparaît ni sur
l'accueil ni dans le menu : pratique pour une page réservée à une classe.

## Réglages généraux

`reglages.js` contient le titre du site, sa phrase de présentation, le nom du dépôt GitHub
(pour le lien « Code source sur GitHub » et les liens « Modifier »), l'ordre des rubriques et
les textes du pied de page (voir ci-dessous). Le dépôt s'écrit `"propriétaire/nom"`, par
exemple `"babash/Babash-NSI-SNT"` ; une adresse `https://github.com/…` est aussi acceptée. Une
valeur mal écrite affiche une erreur sur la page (voir « Si la page affiche une erreur »). Dans
ce cas, comme quand le réglage manque,
les liens « Modifier la liste », « Déposer un fichier » et « Mode d'emploi » disparaissent, et
le lien « Code source sur GitHub » mène au dépôt du site, écrit dans `assets/site.js`.

## Le pied de page : auteur, licences et IA

En bas de l'accueil et de chaque rubrique, un pied de page rappelle :

- qui conçoit les ressources, et la place de l'IA : « Ces ressources sont conçues par
  Babash - NSI Tani Malandi ; beaucoup le sont avec l'aide de l'IA. » ;
- les licences : les documents sous licence CC BY-SA 4.0 et le code des applications sous
  licence MIT, chacune avec un lien vers son texte officiel, puis le lien « Code source sur
  GitHub » vers le dépôt du site (réglage `depot`, voir « Réglages généraux ») ;
- la réutilisation : « Tu peux les réutiliser et les modifier en mentionnant Babash - NSI
  Tani Malandi et la licence ; un document modifié se partage sous la même licence. », suivie
  d'une invitation : « Si tu utilises l'IA pour les modifier, merci de le préciser. » C'est
  une invitation, et non une condition, car la licence CC BY-SA 4.0 ne permet pas d'en ajouter ;
- que les ressources externes restent la propriété de leurs auteurs et autrices (leur site
  d'origine est indiqué sur chaque ressource), et que le décor du site est un dessin original.

Quatre réglages de `reglages.js` changent ces textes sans toucher au code :

| Réglage | Contenu |
|---|---|
| `auteur` | le nom affiché, « Babash - NSI Tani Malandi » ; il remplace `{auteur}` dans les trois textes suivants |
| `mention_ia` | la phrase sur l'auteur et l'IA |
| `reutilisation` | la phrase sur la réutilisation |
| `invitation_ia` | l'invitation à préciser l'usage de l'IA |

Pour `mention_ia`, `reutilisation` et `invitation_ia`, un texte vide (`""`) retire la phrase ;
un réglage absent reprend le texte validé par l'enseignant, écrit dans `assets/site.js`. Les
deux licences, elles, sont fixées dans `assets/site.js`.

Sans JavaScript, chaque page affiche un message (« Ce site a besoin de JavaScript pour afficher
les ressources. ») et, dessous, l'auteur, les deux licences et le lien « Code source sur
GitHub ». Ces textes-là sont écrits directement dans chaque page `index.html` : ils ne suivent
pas `reglages.js`.

---

## Si la page affiche une erreur

L'encadré d'erreur dit, dans son titre, quel fichier est en cause :

- « **Une liste de ressources contient une erreur** » : un fichier `ressources.js` ;
- « **Les réglages du site contiennent une erreur** » : `reglages.js`, par exemple le réglage
  `depot` mal écrit (voir « Réglages généraux ») ; le message dit ce qu'il faut écrire ;
- « **Les réglages du site et une liste de ressources contiennent des erreurs** » : les deux.

Pour une erreur d'écriture, le message indique le fichier et la ligne, et l'encadré rappelle
les causes les plus fréquentes. Presque toujours, juste avant la ligne indiquée :

- une **virgule oubliée** à la fin d'une ligne `titre: "…"` ;
- un **guillemet** pas refermé, ou un guillemet `"` à l'intérieur d'un texte
  (écris plutôt les guillemets français « … » ou une apostrophe) ;
- une **accolade** `}` ou une **parenthèse** `)` pas refermée à la fin du bloc `});`.

Les virgules en trop, elles, ne gênent pas : tu peux en laisser une après chaque ligne.

Les autres erreurs n'ont pas de numéro de ligne : un champ inconnu, une ressource sans titre, un
fichier introuvable, le réglage `depot` mal écrit… Le message dit alors ce qui ne va pas.

## Tester sur ton ordinateur

Télécharge le dépôt (**Code → Download ZIP**), décompresse-le et ouvre `index.html`
dans ton navigateur. Tout fonctionne sans connexion, sauf les polices et les liens externes.

## Applications qui utilisent Supabase

Deux ressources passent par **Supabase** : Alien Python y enregistre la progression des élèves ;
Court-circuit n'y enregistre rien et n'en utilise que le temps réel.

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « SNT-1er Jour », la base commune des applications (à renommer « Babash - applications ») | `alien_classes`, `alien_students`, `alien_progress` |
| Court-circuit (SNT, Programmation ; NSI Première, Constructions élémentaires) | `snt/fichiers/court-circuit/` | la même base commune | aucune : seulement les canaux temps réel (diffusion et présence) |

**Alien Python**

- L'adresse du projet et sa clé publique (« anon ») sont dans `config.js`. Cette clé est publique
  par conception : les tables sont verrouillées et le site ne passe que par les fonctions
  `alien_*`, qui vérifient les codes (code enseignant haché).
- N'importe qui connaissant l'adresse peut créer une classe : les classes des collègues
  arrivent dans la même base. Surveille la table `alien_classes` dans Supabase si besoin.
- Ne fais saisir que des prénoms. Pour supprimer un·e élève : Supabase, *Table Editor*.
- Pour ta propre base : colle `supabase.sql` dans *SQL Editor* de ton projet Supabase,
  puis mets son adresse et sa clé « anon public » dans `config.js`.
- Les exercices d'Alien Python sont d'Alien-Python (© 2021 Mathieu Degrange, licence MIT) :
  la notice est dans `snt/fichiers/alien-python/LICENCE.txt`, à garder en cas de copie.

**Court-circuit**

- Rien n'est enregistré en ligne : le duel en direct passe par les canaux temps réel de
  Supabase (diffusion et présence), sans table ni fonction. Le prénom ou le pseudo et le code de
  chaque élève ne vont qu'aux élèves de sa salle, pendant la séance. Seules la page de la salle
  (`prof.html`) et l'entrée d'un·e élève dans une salle se connectent à Supabase ; l'entraînement
  et le défi contre Zéro marchent sans réseau.
- C'est une exception voulue par l'enseignant (10 novembre 2026) aux règles des bases, qui
  n'utilisaient pas le temps réel. La clé de `snt/fichiers/court-circuit/config.js` est la même
  clé publique « anon ».
- Pour ta propre copie : mets l'adresse et la clé « anon public » de ton projet Supabase dans
  `config.js`, ou laisse l'adresse vide : le jeu passe en mode démo, où une salle passe entre
  les onglets d'un même navigateur (comme avec `?demo` à la fin de l'adresse).
- Les codes d'élèves des applications de jeu viendront plus tard : pour l'instant, rien n'est
  gardé en ligne, et les étoiles et le niveau de Zéro restent un jour au plus sur l'appareil.

**Le socle commun de la base (dossier `supabase/`)**

- La base commune porte SNT 1er jour, Expédition Gombessa, Alien Python et le temps réel de
  Court-circuit. Le dossier `supabase/` du site garde les migrations qui ne relèvent d'aucune
  application (n° 2 du plan de la base unique), appliquées le 11 novembre 2026 après l'accord
  de l'enseignant :
  - `0001` ferme les droits par défaut : un objet créé plus tard n'est ouvert à personne sans un
    droit exprès ;
  - `0002` retire à `authenticated` le droit d'appeler les fonctions de `public` (sauf
    `snt_taille_max`, dont se sert une contrainte de SNT 1er jour) et ferme les séquences ; les
    droits d'`anon` ne changent pas ;
  - `0003` crée le schéma `commun` : le compteur des essais de saisie de code (par empreinte du
    réseau, jamais l'adresse), son sel secret, et le registre des tables de toutes les
    applications (dans Supabase : *Table Editor*, schéma `commun`, vue `registre`) ;
  - `0004` retire à `anon` ses droits sur la séquence du Panthéon, dans l'ancien projet de
    Lagon Arena.
- Chaque migration a son fichier inverse. `supabase/LISEZMOI.md` donne l'ordre, les contrôles
  et le retour en arrière. Les migrations d'une application restent dans son propre dépôt.
- Pour ta propre copie : lance `supabase/schema.sql` dans *SQL Editor* d'un projet neuf, avant le
  script d'une application. Il ne se modifie pas à la main : `python3 scripts/supabase_schema.py`
  le fabrique à partir des migrations, et `python3 scripts/supabase_schema.py --verifier` dit
  s'il est à jour.

Les règles communes des bases sont dans `CLAUDE.md`, section « Les bases Supabase » : une seule
base pour toutes les applications, un schéma par application, l'accès par des fonctions, des
migrations avec leur fichier inverse. Aucune base n'est modifiée sans que l'enseignant ait vu le
SQL exact, et les agents n'en lisent que les métadonnées, jamais les données des élèves. Ils ne
font aucun essai sur une table d'élèves de la base en ligne : les essais d'écriture se font sur
une reproduction locale, avec des données inventées.

## La future bibliothèque (dossier `donnees/`)

Le site va réunir toutes les ressources dans une bibliothèque unique. Son format a été validé
par l'enseignant le 7 novembre 2026, mais **le site ne le lit pas encore** : les pages
continuent d'utiliser les listes `ressources.js` décrites plus haut.

```
donnees/
  README.md                     le format en détail, pour l'enseignant et pour les agents
  ressources/<id>.json          une fiche par ressource (7 pour l'instant : 6 d'exemple et Court-circuit)
  vitrine.exemple.json          un exemple de mise en avant pour la partie extérieure
  referentiels/                 l'arbre des programmes, les listes de valeurs, les compétences Pix
  schema/                       la description exacte du format (JSON Schema)
  correspondance-etiquettes.md  comment les listes actuelles seront converties
scripts/valider_donnees.py      la validation des données
```

Une fiche décrit une ressource et ses documents (activité, version PDF, corrigé, code
source…). Chaque document a deux réglages de visibilité, pour l'extérieur et pour les élèves.
La fiche signale aussi si la ressource collecte des données d'élèves (`donnees_eleves`).
Elle crédite ses auteurs et autrices (`auteurs`, `credits`) ; une ressource reprise et
modifiée crédite toute la chaîne. Par exemple, la fiche de CyberCase cite Etienne Clave
(exomorphisme.fr, lycée de Sada), l'idée de Marion Dufour, le moteur SQL Noir de Hristo
Bogoev, puis la reprise par Babash - NSI Tani Malandi.

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
ressource externe, qui ne se modifie pas, c'est une simple information. Deux fiches d'exemple
ont un avertissement voulu, car ce sont des écarts réels : l'éditeur d'Alien Python, une zone
de texte simple, ne remplit aucun des cinq critères, et la page du TD 1 de POO n'est ni
responsive ni auto-corrective. Ces écarts seront repris lors de la revue des ressources
publiées ; d'ici là, la validation avec `--strict` (ci-dessous) échoue sur ces deux
avertissements.

Pour valider les données, depuis le dossier du site : `python3 scripts/valider_donnees.py`
(Python 3 seul, rien à installer ; avec `--strict`, les avertissements bloquent aussi). Chaque
message donne le fichier et le champ. Le script signale comme erreur, entre autres, un lien
principal vers GitHub, un identifiant en double, une référence inexistante, un document sans
réglage de visibilité, et tout ce qui ressemble à un mot de passe, un identifiant ou une clé
secrète.

## Vérification automatique

Le fichier `.github/workflows/verifier.yml` lance trois contrôles, visibles dans l'onglet
**Actions** du dépôt (coche verte : tout va bien ; croix rouge : clique pour voir le détail) :

- **Données de la bibliothèque**, à chaque modification, sur toutes les branches, et à la
  demande : `scripts/valider_donnees.py --github` vérifie les fiches, la vitrine et les
  référentiels du dossier `donnees/` (voir « La future bibliothèque »). Une erreur fait
  échouer le contrôle (croix rouge). Les avertissements et les informations sont dans le
  résumé du run, sans échec, et les erreurs et avertissements apparaissent aussi en
  annotations sur les fichiers concernés. Les deux avertissements voulus des fiches d'exemple
  (Alien Python, TD 1 de POO) y figurent donc à chaque run.
- **Liens des ressources**, à chaque modification et chaque lundi : tous les liens des
  fichiers `ressources.js` sont testés. Un lien en échec est revérifié par un second job,
  « Liens en échec, seconde passe », donc sur une autre machine de GitHub, une à deux minutes
  plus tard : il n'est déclaré mort que s'il échoue aux deux passes, ce qui écarte les pannes
  passagères. Un lien qui ne répond pas à temps aux deux passes compte aussi comme mort.
  Le résumé liste les liens morts, avec le fichier et la ligne, et les pannes passagères.
  Ne sont pas testés : les pages qui demandent une connexion (Capytale, claude.ai) et
  algorea.org, qui refuse les robots. Les sites qui répondent « accès refusé » (403) ou
  « trop de requêtes » (429) aux robots sont comptés comme valides.
- **Site en ligne**, après chaque modification de `main` : le contrôle attend que GitHub Pages
  ait réellement mis en ligne ce commit (`scripts/attendre_deploiement.py`), puis télécharge
  les fichiers du site que l'envoi ajoute ou modifie, sur tous ses commits (par exemple la
  fusion d'une branche et le commit du README envoyés ensemble), et vérifie qu'ils sont
  identiques à ceux du dépôt. Les fichiers du site qui ne sont pas comparés (plus de 5 Mo, ou
  au-delà des 200 premiers) sont signalés dans le résumé. Ensuite, il affiche chaque rubrique
  dans Chrome et vérifie qu'aucune erreur n'apparaît et que le nombre de ressources affichées
  est celui de `ressources.js`. Il ouvre aussi chaque page déposée dans un dossier `fichiers/`
  (TD, fiches, diaporamas, applications) et vérifie qu'elle s'affiche avec un vrai contenu. Il
  vérifie enfin le lien « Code source sur GitHub » : l'accueil et chaque rubrique doivent l'avoir,
  vers le dépôt du réglage `depot`, sinon le contrôle échoue ; une page déposée qui ne l'a pas
  encore est seulement signalée dans le résumé, sans échec (la liste `CODE_SOURCE_EXCEPTIONS` de
  `.github/verifier-site.py` peut en dispenser une page, avec sa raison ; elle est vide). Le
  résumé donne l'heure de chaque étape. Si un commit plus récent est mis en ligne entre-temps,
  c'est son propre contrôle qui vérifie le site, en ne comparant que les fichiers de son envoi ;
  pour comparer aussi ceux de l'envoi précédent, relance le contrôle à la main avec le champ
  « depuis ». Lancé à la main (**Run workflow** dans l'onglet Actions), ce contrôle vérifie le
  site tel que `main` l'a mis en ligne ; la comparaison porte sur le dernier commit de `main`,
  ou sur tous les commits qui suivent celui que tu indiques dans le champ « depuis ».

Le même contrôle des pages se lance sur ton ordinateur, depuis le dossier du site :
`python3 -m http.server 8000`, puis dans un autre terminal
`python3 .github/verifier-site.py http://localhost:8000`.

Avant chaque publication, le Gardien pré-valide la branche avec ses outils, rangés dans
`.github/gardien/` : `python3 -I .github/gardien/controler.py --branche origin/<branche>`
vérifie que la branche part du dernier `main`, puis contrôle les données sensibles, les liens
internes, le rendu avant et après (320, 768 et 1440 px, clair et obscur), les contrastes, la
navigation au clavier et l'impression A4 des documents touchés ; il lance aussi le contrôle
des pages décrit ci-dessus. La conformité, elle, se vérifie à la lecture : cahier des charges,
décisions de l'enseignant et règles de conception (voir « L'équipe d'agents »). Il vérifie de
même les liens vers les dépôts (voir « Règle des liens ») : chaque ressource que la branche
ajoute ou modifie et qui a un dépôt le donne en « Code source », et chaque page touchée porte en
pied de page le lien « Code source sur GitHub » ; si l'un de ces liens manque, il est ajouté
dans une branche de suite, sans bloquer la publication. Après la publication,
`bash .github/gardien/attendre_actions.sh <commit>` suit la mise en ligne et lit les résultats
des contrôles automatiques. Il faut Python avec Playwright et Pillow, Chrome ou Chromium, et
l'outil `gh` de GitHub pour suivre la mise en ligne.

D'autres outils du même dossier servent au cas par cas : `caracteres.py` relève, dans les lignes
qu'ajoute une branche, les caractères invisibles et les points qui imitent le point médian (le
vrai point médian, lui, est permis) ; `zones.py` situe les différences de rendu entre avant et
après, pour vérifier par exemple qu'un changement se limite au pied de page ; `contraste_zone.py`
donne le contraste le plus faible d'une zone de la page, le pied de page par défaut ;
`chemins_readme.py` vérifie que les chemins cités dans un README existent. Les tests de
non-régression du Gardien se lancent d'un coup :
`python3 -I .github/gardien/tests/lancer.py --ref origin/<branche>`. Ils vérifient notamment que
la validation des données détecte toujours les fautes graves, applique les règles 19 et 20 et
accepte le point médian dans les textes, que les scripts du contrôle en ligne décident juste, et
que le pied de page suit ses réglages. L'en-tête de chaque fichier en décrit l'usage.

---

## L'équipe d'agents

Le site est entretenu par une équipe d'agents Claude (Gardien, Architecte, Bibliothécaire,
Designer, Atelier et Vigie), coordonnés par un chef d'orchestre. Leurs règles communes sont
dans `CLAUDE.md`, à la racine du dépôt, et la fiche de chaque rôle dans `.claude/agents/`.
Chaque tâche se fait sur sa propre branche ; seul le Gardien publie sur `main`, après ses contrôles,
et dès que c'est sûr : un point d'écriture mineur ne bloque pas, il part dans une branche de suite.

Chaque fichier a un rôle propriétaire, indiqué dans le tableau « Qui possède quoi » de
`CLAUDE.md` : par exemple, les listes `ressources.js` au Bibliothécaire, le moteur
(`assets/site.js`) et les pages `index.html` à l'Architecte, la feuille de style et l'icône
du site (`assets/favicon.svg`) au Designer, ce README, le fichier de licence du dépôt
(`LICENSE`) et les outils de `.github/gardien/` au Gardien. Le dossier `donnees/` de
la future bibliothèque est à l'Architecte (notamment le format des données et les
référentiels), sauf les fiches des ressources (`donnees/ressources/`) et la vitrine
(`donnees/vitrine.json`), qui sont au Bibliothécaire ; l'Architecte peut y créer des fiches
d'exemple pour illustrer le format.
Un agent ne modifie que ses fichiers ; pour les autres, il le signale dans son rapport.
Le Gardien peut supprimer une branche déjà fusionnée ou devenue inutile, après avoir vérifié
qu'il n'y a rien à récupérer et avec l'accord du chef d'orchestre.

Toute ressource produite ou retravaillée suit les règles de conception de la philosophie
éducative de l'enseignant : une version en ligne utilisable sur téléphone et une version
papier A4 en noir et blanc, peu de texte, des erreurs expliquées, la correction automatique
chaque fois que c'est possible… Trois règles s'appliquent toujours aux créations de
l'enseignant :

- un **TD** existe en deux versions : un PDF imprimable (A4, noir et blanc) et une page HTML
  qui s'adapte à l'écran, du téléphone au grand écran, et se corrige seule : l'élève répond
  dans un formulaire et la correction s'affiche aussitôt. La correction se fait dans le
  navigateur, sans envoyer les réponses ailleurs (ce serait une collecte de données, soumise
  à l'enseignant) ;
- un **éditeur de code** (toute ressource où l'élève écrit du code) a la coloration
  syntaxique ; l'indentation automatique (la touche Tab indente) ; des guides d'indentation
  qui montrent les blocs (quel `if`, quelle boucle contient quelle ligne), sur le modèle de
  l'éditeur de Lagon Arena ; l'autocomplétion contextualisée, qui propose ce qui a du sens à
  cet endroit (mots-clés, variables et fonctions déjà définies, méthodes du type en cours) ;
  et des erreurs lisibles : l'erreur s'affiche d'abord telle que le langage la donne, puis
  l'élève peut la faire traduire ou expliquer en français, grâce à des explications intégrées
  à la ressource, sans service commercial ;
- une **application de jeu** (Lagon Arena, Expédition Gombessa, Alien Python…) donne à chaque
  élève un code unique en mots et chiffres (comme `CORAIL-MANTA-482`), qui suffit pour revenir
  depuis n'importe où ; l'enseignant·e a aussi un code et voit ceux de ses élèves, et un lien
  de classe, avec son QR code, permet de rejoindre la classe. Les pages en ligne des TD, elles,
  restent sans compte ni envoi de données.

Une ressource externe ne se modifie pas : sa fiche peut signaler ce qui lui manque. Le Gardien
vérifie ces règles avant de publier une ressource. Les ressources déjà en ligne n'ont pas
encore été revues sous cet angle.

Règle d'écriture : les pages du site et les documents pour les élèves s'écrivent en langage
inclusif chaque fois que c'est pertinent (formulations épicènes, double flexion, féminisation
des fonctions et point médian, comme « enseignant·e·s »), selon la décision de l'enseignant du
7 novembre 2026.

Les documents de coordination (cahier des charges, philosophie éducative, registre des
décisions, organisation des agents, tableau des tâches, journal des publications, rapport du
Gardien) sont dans le projet claude.ai « Site SNT-NSI ».

---

## Activer GitHub Pages (une seule fois)

**Settings → Pages**, puis *Build and deployment* : **Deploy from a branch**,
**Branch : main**, dossier **/ (root)**, et **Save**.

---

## Le décor

La ville, sa liaison montante et le sol quadrillé du bandeau sont un dessin original, généré
par `assets/site.js` (fonction `scene`) dans la couleur de chaque rubrique. Les couleurs
générales des deux affichages sont en haut de `assets/style.css`.

---

## Fiche Python (SNT) : modifications par rapport à l'original

L'original est la fiche Compute-it d'Etienne Clave, sur le site exomorphisme.fr (lycée de Sada).

- Bouton de retour vers la rubrique SNT (non imprimé).
- Cases rouges réellement hachurées, couleurs imprimées sans réglage du navigateur.
- **Exercice 3 : départ déplacé de A1 à A2.** Depuis A1, le personnage restait sur la ligne 1
  et ne passait jamais sur une case rouge, donc le `if` n'était jamais vrai.
- Sur téléphone, la feuille A4 est réduite pour tenir dans l'écran.

---

## Contact

Conçu par Babash - NSI Tani Malandi pour les classes de SNT et de NSI de l'académie de Mayotte ; beaucoup de ressources le sont avec l'aide de l'IA, et le site est entretenu par une équipe d'agents Claude (voir « L'équipe d'agents »).
Une question, une idée, un lien cassé ? Les [issues GitHub](https://github.com/babash/Babash-NSI-SNT/issues) du dépôt.

## Licence

- **Le code du site** (`assets/*.js`, `assets/*.css`, les pages `index.html`, `reglages.js`, `scripts/`, `supabase/`, `.github/`) est sous licence [MIT](LICENSE).
- **Les documents** (les fiches, TD, cours, guides et diaporamas des dossiers `fichiers/`, les textes des listes de ressources, le décor du bandeau) sont sous licence [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr).
- **Alien Python** (`snt/fichiers/alien-python/`) : d'après [Alien-Python](https://forge.apps.education.fr/DegrangeM/alien-python), de Mathieu Degrange (MIT) ; la notice est dans `snt/fichiers/alien-python/LICENCE.txt`, à garder avec `data.js` en cas de copie.
- **Court-circuit** (`snt/fichiers/court-circuit/`) : code MIT et documents CC BY-SA 4.0 de Babash - NSI Tani Malandi ; les bibliothèques incluses (CodeMirror 6, client temps réel de Supabase, QR Code Generator) gardent leur licence MIT, avec leur notice dans `snt/fichiers/court-circuit/vendor/LICENCES-BIBLIOTHEQUES.txt`, et les polices intégrées (Chakra Petch, JetBrains Mono, Atkinson Hyperlegible) la leur, la SIL Open Font License 1.1, avec leurs copyrights et son texte dans `snt/fichiers/court-circuit/LICENCE.txt`.
- **La fiche Python de SNT** (`snt/fichiers/python-compute-it.html`) : d'après la fiche Compute-it d'Etienne Clave, sur le site exomorphisme.fr (lycée de Sada).
- **Les ressources externes** restent la propriété de leurs auteurs et autrices : leur site d'origine est indiqué sur chaque ressource.

Tu peux les réutiliser et les modifier, y compris pour tes classes, en mentionnant Babash - NSI Tani Malandi et la licence ; un document modifié se partage sous la même licence. Si tu utilises l'IA pour les modifier, merci de le préciser.
