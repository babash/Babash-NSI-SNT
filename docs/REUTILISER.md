# Réutiliser le site pour tes classes

*Ta propre copie du site : la copier, la mettre en ligne, l'adapter, l'essayer, et ce qu'il faut garder. Retour au [README](../README.md).*

Le site lui-même n'a ni compte ni base de données : tout tient dans le dépôt. Tu peux le copier tel quel, puis y mettre tes rubriques et tes ressources.

## Copier le dépôt

Sur GitHub, le bouton **Fork** copie le dépôt dans ton compte. Pour une simple copie sur ton ordinateur : **Code → Download ZIP** (voir [Tester sur ton ordinateur](#tester-sur-ton-ordinateur)).

## Activer GitHub Pages (une seule fois)

**Settings → Pages**, puis *Build and deployment* : **Deploy from a branch**,
**Branch : main**, dossier **/ (root)**, et **Save**.

Le site est alors en ligne à l'adresse `https://<ton-compte>.github.io/<nom-du-dépôt>/`, et chaque envoi sur `main` le met à jour en une minute environ.

## Adapter les réglages

- Dans `reglages.js`, écris le nom de **ton** dépôt dans `depot` (`"ton-compte/nom-du-dépôt"`) : les liens « Modifier la liste », « Déposer un fichier » et « Code source sur GitHub » mèneront alors à ta copie. Le titre, la présentation, l'ordre des rubriques et les textes du pied de page se règlent dans le même fichier : voir [Réglages généraux](LISTES.md#réglages-généraux) et [Le pied de page](LISTES.md#le-pied-de-page--auteur-licences-et-ia).
- Pour tes rubriques : [Ajouter une rubrique](LISTES.md#ajouter-une-rubrique) ; pour tes ressources : [les listes de ressources](LISTES.md).

## Tester sur ton ordinateur

Télécharge le dépôt (**Code → Download ZIP**), décompresse-le et ouvre `index.html`
dans ton navigateur. Tout fonctionne sans connexion, sauf les polices et les liens externes.

## Les applications qui utilisent une base

Alien Python et Court-circuit passent par Supabase. Pour leur donner ta propre base, ou faire tourner Court-circuit en mode démo, sans base : [SUPABASE.md](SUPABASE.md).

## Ce que tu dois garder

- **La licence** : le code reste sous licence MIT (garde le fichier [`LICENSE`](../LICENSE)), les documents sous licence CC BY-SA 4.0, en mentionnant Babash - NSI Tani Malandi ; un document modifié se partage sous la même licence (la section [Licence](../README.md#licence) du README).
- **Ce qui vient d'ailleurs**, avec sa licence et sa notice : les exercices d'Alien Python (la notice `snt/fichiers/alien-python/LICENCE.txt`, à garder avec `data.js`), les bibliothèques et les polices de Court-circuit (`snt/fichiers/court-circuit/vendor/LICENCES-BIBLIOTHEQUES.txt` et `snt/fichiers/court-circuit/LICENCE.txt`).
- **Les crédits en chaîne** d'une ressource reprise, comme la fiche Python de SNT, ci-dessous.

## Fiche Python (SNT) : modifications par rapport à l'original

L'original est la fiche Compute-it d'Etienne Clave, sur le site exomorphisme.fr (lycée de Sada).

- Bouton de retour vers la rubrique SNT (non imprimé).
- Cases rouges réellement hachurées, couleurs imprimées sans réglage du navigateur.
- **Exercice 3 : départ déplacé de A1 à A2.** Depuis A1, le personnage restait sur la ligne 1
  et ne passait jamais sur une case rouge, donc le `if` n'était jamais vrai.
- Sur téléphone, la feuille A4 est réduite pour tenir dans l'écran.
