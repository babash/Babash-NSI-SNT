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
reglages.js                 titre du site et liste des rubriques
snt/
  ressources.js             ← la liste de la rubrique SNT
  fichiers/                 ← les PDF et fiches de la rubrique SNT
  index.html                (ne pas toucher)
nsi-premiere/   …           même organisation pour chaque rubrique
nsi-terminale/  …
pp/             …
autres/         …
assets/                     mise en page et fonctionnement (ne pas toucher)
.github/                    vérification automatique des liens et des pages (voir plus bas)
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
(pour les liens « Modifier ») et l'ordre des rubriques.

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

## Vérification automatique

Le fichier `.github/workflows/verifier.yml` lance deux contrôles, visibles dans l'onglet
**Actions** du dépôt (coche verte : tout va bien ; croix rouge : cliquer pour voir le détail) :

- **Liens des ressources**, à chaque modification et chaque lundi : tous les liens des
  fichiers `ressources.js` sont testés. Le résumé liste les liens morts, fichier et ligne.
  Ne sont pas testés : les pages qui demandent une connexion (Capytale, claude.ai) et
  algorea.org, qui refuse les robots. Les sites qui répondent « accès refusé » (403) aux
  robots sont comptés comme valides.
- **Site en ligne**, après chaque modification de `main` : le contrôle attend que GitHub Pages
  serve la nouvelle version, puis affiche chaque rubrique dans Chrome et vérifie qu'aucune
  erreur n'apparaît et que le nombre de ressources affichées est celui de `ressources.js`.

Le même contrôle des pages se lance sur son ordinateur, depuis le dossier du site :
`python3 -m http.server 8000`, puis dans un autre terminal
`python3 .github/verifier-site.py http://localhost:8000`.

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
