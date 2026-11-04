# Ressources SNT

Petit site de ressources de SNT pour l'équipe, rangées par thème du programme de seconde.
Aucun outil à installer : ce sont des fichiers HTML que GitHub Pages met en ligne tels quels.

**Le site en ligne : https://babash.github.io/Babash-NSI-SNT/**

```
index.html                  la page d'accueil (c'est ici qu'on ajoute les ressources)
fiches/
  python-compute-it.html    fiche de révision Python + TD débranché (A4 recto-verso)
assets/
  style.css                 la mise en page et les couleurs des thèmes
  site.js                   compteurs, nom des sites, lien vers ce dépôt
  favicon.svg               l'icône de l'onglet
.nojekyll                   fichier vide : dit à GitHub de ne rien transformer
```

---

## Remettre le site en ligne ailleurs (copie sur un autre compte)

Le site est déjà en ligne à l'adresse ci-dessus. Ces étapes servent seulement à en faire
une copie sur un autre compte GitHub.

1. Sur [github.com](https://github.com), cliquer sur **New repository**.
   Choisir un nom (par exemple `ressources-snt`) et le laisser en **Public**
   (GitHub Pages gratuit ne fonctionne qu'avec un dépôt public).
2. Dans le dépôt vide, cliquer sur **uploading an existing file**.
   Glisser **le contenu** du dossier (le fichier `index.html`, les dossiers `assets` et `fiches`…),
   pas le dossier lui-même. Valider avec **Commit changes**.
   Le fichier `.nojekyll` est caché sur certains ordinateurs : s'il ne part pas, ce n'est pas grave.
3. Aller dans **Settings → Pages**. Dans *Build and deployment*, choisir
   **Source : Deploy from a branch**, puis **Branch : main** et **/ (root)**. Cliquer sur **Save**.
4. Attendre une à deux minutes. Le site est à l'adresse :
   `https://<votre-identifiant>.github.io/ressources-snt/`

---

## Ajouter une ressource

Directement sur GitHub, sans rien installer :

1. Ouvrir `index.html` dans le dépôt, puis cliquer sur le crayon (**Edit this file**).
2. Repérer le thème (chaque thème commence par un commentaire comme `<!-- ───── INTERNET ───── -->`).
3. Coller ce bloc entre `<ul class="ressources">` et `</ul>` :

```html
<li class="res">
  <a class="titre" href="https://adresse-de-la-ressource">Nom de la ressource</a>
  <p>Ce que font les élèves, en une ou deux phrases.</p>
  <p class="tags"><span>En ligne</span></p>
</li>
```

4. Cliquer sur **Commit changes**. Le site se met à jour en une minute environ.

Le reste se fait tout seul : le compteur du thème dans le sommaire, le nom du site affiché
sous la ressource, l'ouverture dans un nouvel onglet, et la disparition du message
« Rien ici pour l'instant ».

**Étiquettes déjà utilisées** (on peut en mettre plusieurs, une par `<span>`) :
`En ligne`, `À imprimer`, `Débranché`, `Python`, `Connexion ENT`, `Pour aller plus loin`.

**Dans une adresse**, remplacer chaque `&` par `&amp;` (voir le lien Capytale dans `index.html`).
Le lien fonctionne même sans, mais c'est plus propre.

---

## Ajouter une fiche HTML

1. Déposer le fichier dans le dossier `fiches/` (bouton **Add file → Upload files** dans ce dossier).
2. Dans `index.html`, faire pointer la ressource vers lui avec un lien relatif :
   `href="fiches/nom-du-fichier.html"`.
3. Pour avoir un lien de retour sur la fiche, copier cette ligne juste après `<body>` :

```html
<a href="../index.html">← Ressources SNT</a>
```

---

## Ajouter un thème

1. Dans `assets/style.css`, ajouter une couleur de surligneur à la liste des thèmes, par exemple
   `.t-algo { --hl: #FFC078; }`.
2. Dans `index.html`, ajouter un lien dans le sommaire :
   `<li><a class="t-algo" href="#algo">Algorithmique<span class="nb" aria-hidden="true"></span></a></li>`
3. Copier une section vide existante (par exemple *Internet*), changer son `id="algo"`,
   sa classe `t-algo` et son titre.

---

## Modifications apportées à la fiche Python

- Bouton « Ressources SNT » en haut à gauche pour revenir au site (non imprimé).
- Les cases rouges sont réellement hachurées, et les couleurs s'impriment sans avoir à cocher
  « Graphiques d'arrière-plan » dans le navigateur : la fiche reste lisible en noir et blanc.
- **Exercice 3 : départ déplacé de A1 à A2.** Depuis A1, le personnage restait sur la ligne 1
  et ne passait jamais sur une case rouge, donc le `if` n'était jamais vrai.
  Pour revenir à l'original : remettre `Départ en <strong>A1</strong>` et déplacer
  la classe `ci-cell-start` sur la première case de la ligne 1.
- Sur téléphone, la feuille A4 est réduite pour tenir dans l'écran (aucun effet à l'impression).
