# Ressources NSI et SNT

Cours, activités et outils pour la classe, rangés par niveau et par thème.

**Le site : https://babash.github.io/Babash-NSI-SNT/**

Le site a cinq rubriques : SNT, NSI Première, NSI Terminale, Professeur principal et Autres.
Chaque rubrique a **sa propre liste de ressources**, dans un petit fichier texte qu'on modifie
directement sur GitHub. Une ressource peut être un lien vers un site, ou un fichier déposé
sur le site (PDF, fiche HTML, diaporama…).

Les rubriques suivent les **textes officiels** :

| Rubrique | Texte de référence | Thèmes du site |
|---|---|---|
| SNT | Programme de SNT, BO spécial n° 1 du 22 janvier 2019 | Les 7 thèmes et les notions transversales de programmation |
| NSI Première | Programme de NSI de première, BO spécial n° 1 du 22 janvier 2019 | Les 8 rubriques, avec la colonne « Contenus » |
| NSI Terminale | Programme de NSI de terminale, BO spécial n° 8 du 25 juillet 2019 | Les 6 rubriques, avec la colonne « Contenus » |
| Professeur principal | Circulaire n° 2018-108 du 10 octobre 2018 | Les missions du professeur principal |

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
scripts/                    vérification automatique et validation des données
```

**Règle des liens** : le lien principal d'une ressource mène **directement** à la ressource
(la page de l'activité, la fiche, le PDF), jamais à un dépôt GitHub ou à un fichier affiché
par GitHub. Le dépôt peut figurer discrètement en annexe, sous le nom « Code source ».
Quand une activité n'a pas de page en ligne, ses fichiers sont déposés dans le dossier
`fichiers` de la rubrique (c'est le cas de `nsi-terminale/fichiers/os-humain/`).

---

## Ajouter une ressource en ligne

1. En bas de la page de la rubrique, cliquer sur **Modifier la liste**.
   Ou bien, sur GitHub : ouvrir le fichier `ressources.js` de la rubrique, puis le crayon.
2. Repérer le bon thème (les lignes `theme("…");`) et coller ce bloc en dessous :

```js
ressource({
  titre: "Nom de la ressource",
  lien: "https://adresse-de-la-ressource",
  texte: "Ce que font les élèves, en une ou deux phrases.",
  tags: ["En ligne"],
});
```

3. Cliquer sur **Commit changes**. Le site se met à jour en une minute environ.

L'ordre dans le fichier est l'ordre sur la page. Le compteur du thème, le nom du site
affiché sous la ressource et l'ouverture dans un nouvel onglet se font tout seuls.

## Ajouter un PDF (ou n'importe quel fichier)

1. En bas de la page de la rubrique, cliquer sur **Déposer un fichier** : le fichier va
   directement dans le dossier `fichiers` de la rubrique. Valider avec **Commit changes**.
2. L'ajouter à la liste comme une ressource en ligne, avec le nom du fichier :

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
sont téléchargés quand on clique dessus.

> Conseil : des noms de fichiers sans espaces ni accents (`tp-graphes.pdf` plutôt que `TP Graphes é.pdf`).

## Une ressource avec plusieurs liens (sujet, corrigé, version en ligne…)

Ajouter `annexes`. Chaque ligne donne le texte du lien, puis son adresse ou son fichier :

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
| `texte` | non | La description. On peut écrire du `code` entre accents graves et du **gras** entre doubles étoiles |
| `tags` | non | Des étiquettes entre crochets : `["En ligne", "Python"]` |
| `annexes` | non | Des liens en plus (voir ci-dessus) |

Étiquettes déjà utilisées : `En ligne`, `À imprimer`, `Débranché`, `Python`, `SQL`, `Jeu`,
`Cours`, `Notebook`, `Connexion ENT`, `Rien à installer`, `À adapter`, `Pour aller plus loin`,
`Ressource du mois`. On peut en inventer d'autres.

L'étiquette `Ressource du mois` met en avant une ressource (en ce moment : CyberCase, en SNT
et en NSI Terminale). Chercher « ressource du mois » sur l'accueil la retrouve ; il suffit
d'enlever l'étiquette le mois suivant.

La recherche de la page d'accueil fouille les titres, textes, étiquettes et thèmes de
toutes les rubriques. On peut partager une recherche : `…/Babash-NSI-SNT/?q=débranché`.

---

## Organiser une rubrique

Dans `ressources.js` :

- `theme("Algorithmique");` commence un nouveau thème. Les ressources en dessous lui appartiennent.
- Nom long : `theme("Représentation des données : types construits", { court: "Types construits" });`
  Le nom court sert dans le sommaire et dans l'adresse (`…/nsi-premiere/#types-construits`).
- Couleur : `theme("Sites ressources", "gris");` Couleurs possibles : bleu, vert, violet, rose,
  orange, citron, cyan, jaune, lavande, corail, gris. Sans couleur, le site en choisit une.
- `groupe("Pour aller plus loin");` ajoute un sous-titre à l'intérieur d'un thème.
- Un thème sans ressource affiche « Rien ici pour l'instant » : on peut le laisser en attendant.

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

1. Créer un dossier, par exemple `mathematiques`, avec une copie de `autres/index.html`
   et de `autres/ressources.js`. Changer le nom dans `rubrique({ … })`.
2. Dans `reglages.js`, ajouter `"mathematiques",` à la liste des rubriques.

Une rubrique absente de `reglages.js` reste visible à son adresse, mais n'apparaît ni sur
l'accueil ni dans le menu : pratique pour une page réservée à une classe.

## Réglages généraux

`reglages.js` contient le titre du site, sa phrase de présentation, le nom du dépôt GitHub
(pour les liens « Modifier »), l'ordre des rubriques et les textes du pied de page (voir
ci-dessous).

## Le pied de page : auteur, licences et IA

En bas de l'accueil et de chaque rubrique, un pied de page rappelle :

- qui conçoit les ressources, et la place de l'IA : « Ces ressources sont conçues par
  Babash - NSI Tani Malandi ; beaucoup le sont avec l'aide de l'IA. » ;
- les licences : les documents sous licence CC BY-SA 4.0 et le code des applications sous
  licence MIT, chacune avec un lien vers son texte officiel ;
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

---

## Si la page affiche « Une liste de ressources contient une erreur »

Le message indique le fichier et la ligne. Presque toujours, juste avant cette ligne :

- une **virgule oubliée** à la fin d'une ligne `titre: "…"` ;
- un **guillemet** pas refermé, ou un guillemet `"` à l'intérieur d'un texte
  (écrire plutôt les guillemets français « … » ou une apostrophe) ;
- une **accolade** `}` ou une **parenthèse** `)` pas refermée à la fin du bloc `});`.

Les virgules en trop, elles, ne gênent pas : on peut en laisser une après chaque ligne.

## Tester sur son ordinateur

Télécharger le dépôt (**Code → Download ZIP**), le décompresser et ouvrir `index.html`
dans le navigateur. Tout fonctionne sans connexion, sauf les polices et les liens externes.

## Applications avec une base de données

Certaines ressources enregistrent la progression des élèves dans **Supabase** :

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « SNT-1er Jour » | `alien_classes`, `alien_students`, `alien_progress` |

- L'adresse du projet et sa clé publique (« anon ») sont dans `config.js`. Cette clé est publique
  par conception : les tables sont verrouillées et le site ne passe que par les fonctions
  `alien_*`, qui vérifient les codes (code enseignant haché).
- N'importe qui connaissant l'adresse peut créer une classe : les classes des collègues
  arrivent dans la même base. Surveiller la table `alien_classes` dans Supabase si besoin.
- Ne faire saisir que des prénoms. Supprimer un élève se fait dans Supabase (*Table Editor*).
- Pour une base à soi : coller `supabase.sql` dans *SQL Editor* de son projet Supabase,
  puis mettre son adresse et sa clé « anon public » dans `config.js`.
- Les exercices d'Alien Python sont d'Alien-Python (© 2021 Mathieu Degrange, licence MIT) :
  la notice est dans `snt/fichiers/alien-python/LICENCE.txt`, à garder en cas de copie.

## La future bibliothèque (dossier `donnees/`)

Le site va réunir toutes les ressources dans une bibliothèque unique. Son format a été validé
par l'enseignant le 7 novembre 2026, mais **le site ne le lit pas encore** : les pages
continuent d'utiliser les listes `ressources.js` décrites plus haut.

```
donnees/
  README.md                     le format en détail, pour l'enseignant et pour les agents
  ressources/<id>.json          une fiche par ressource (6 fiches d'exemple pour l'instant)
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
**Actions** du dépôt (coche verte : tout va bien ; croix rouge : cliquer pour voir le détail) :

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
  les fichiers du site que le commit ajoute ou modifie et vérifie qu'ils sont identiques à
  ceux du dépôt. Ensuite, il affiche chaque rubrique dans Chrome et vérifie qu'aucune erreur
  n'apparaît et que le nombre de ressources affichées est celui de `ressources.js`. Il ouvre
  aussi chaque page déposée dans un dossier `fichiers/` (TD, fiches, diaporamas,
  applications) et vérifie qu'elle s'affiche avec un vrai contenu. Le résumé donne l'heure de
  chaque étape. Si un commit plus récent est mis en ligne entre-temps, c'est son propre
  contrôle qui vérifie le site. Lancé à la main (**Run workflow** dans l'onglet Actions), ce
  contrôle vérifie le site tel que `main` l'a mis en ligne.

Le même contrôle des pages se lance sur son ordinateur, depuis le dossier du site :
`python3 -m http.server 8000`, puis dans un autre terminal
`python3 .github/verifier-site.py http://localhost:8000`.

Avant chaque publication, le Gardien pré-valide la branche avec ses outils, rangés dans
`.github/gardien/` : `python3 -I .github/gardien/controler.py --branche origin/<branche>`
vérifie que la branche part du dernier `main`, puis contrôle les données sensibles, les liens
internes, le rendu avant et après (320, 768 et 1440 px, clair et obscur), les contrastes, la
navigation au clavier et l'impression A4 des documents touchés ; il lance aussi le contrôle
des pages décrit ci-dessus. La conformité, elle, se vérifie à la lecture : cahier des charges,
décisions de l'enseignant et règles de conception (voir « L'équipe d'agents »). Après la
publication, `bash .github/gardien/attendre_actions.sh <commit>` suit la mise en ligne et lit
les résultats des contrôles automatiques. Il faut Python avec Playwright et Pillow, Chrome ou
Chromium, et l'outil `gh` de GitHub pour suivre la mise en ligne.

---

## L'équipe d'agents

Le site est entretenu par une équipe d'agents Claude (Gardien, Architecte, Bibliothécaire,
Designer, Atelier et Vigie), coordonnés par un chef d'orchestre. Leurs règles communes sont
dans `CLAUDE.md`, à la racine du dépôt, et la fiche de chaque rôle dans `.claude/agents/`.
Chaque tâche se fait sur sa propre branche ; seul le Gardien publie sur `main`, après ses contrôles.

Chaque fichier a un rôle propriétaire, indiqué dans le tableau « Qui possède quoi » de
`CLAUDE.md` : par exemple, les listes `ressources.js` au Bibliothécaire, le moteur
(`assets/site.js`) et les pages `index.html` à l'Architecte, la feuille de style et l'icône
du site (`assets/favicon.svg`) au Designer, ce README, le fichier de licence du dépôt
(`LICENSE`, à venir) et les outils de `.github/gardien/` au Gardien. Le dossier `donnees/` de
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
chaque fois que c'est possible… Deux règles s'appliquent toujours aux créations de
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
  à la ressource, sans service commercial.

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

- Bouton de retour vers la rubrique SNT (non imprimé).
- Cases rouges réellement hachurées, couleurs imprimées sans réglage du navigateur.
- **Exercice 3 : départ déplacé de A1 à A2.** Depuis A1, le personnage restait sur la ligne 1
  et ne passait jamais sur une case rouge, donc le `if` n'était jamais vrai.
- Sur téléphone, la feuille A4 est réduite pour tenir dans l'écran.
