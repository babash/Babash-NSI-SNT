# Les listes de ressources

*Ajouter, ranger et régler les ressources du site, et que faire si la page affiche une erreur. Retour au [README](../README.md).*

Le site a cinq rubriques : SNT, NSI Première, NSI Terminale, Professeur principal et Autres.
Chaque rubrique a **sa propre liste de ressources**, dans un petit fichier texte que tu modifies
directement sur GitHub. Une ressource peut être un lien vers un site, ou un fichier déposé
sur le site (PDF, fiche HTML, diaporama…).

## La règle des liens

Le lien principal d'une ressource mène **directement** à la ressource
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
[la vérification automatique](VERIFICATION.md)).
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
valeur mal écrite affiche une erreur sur la page (voir [Si la page affiche une erreur](#si-la-page-affiche-une-erreur)). Dans
ce cas, comme quand le réglage manque,
les liens « Modifier la liste », « Déposer un fichier » et « Mode d'emploi » disparaissent, et
le lien « Code source sur GitHub » mène au dépôt du site, écrit dans `assets/site.js`.

## Le pied de page : auteur, licences et IA

En bas de l'accueil et de chaque rubrique, un pied de page rappelle :

- qui conçoit les ressources, et la place de l'IA : « Ces ressources sont conçues par
  Babash - NSI Tani Malandi ; beaucoup le sont avec l'aide de l'IA. » ;
- les licences : les documents sous licence CC BY-SA 4.0 et le code des applications sous
  licence MIT, chacune avec un lien vers son texte officiel, puis le lien « Code source sur
  GitHub » vers le dépôt du site (réglage `depot`, voir [Réglages généraux](#réglages-généraux)) ;
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
  `depot` mal écrit (voir [Réglages généraux](#réglages-généraux)) ; le message dit ce qu'il faut écrire ;
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

Pour essayer une modification sur ton ordinateur avant de l'envoyer : [Tester sur ton ordinateur](REUTILISER.md#tester-sur-ton-ordinateur).
