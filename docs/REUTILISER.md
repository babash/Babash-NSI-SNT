# Réutiliser le site pour tes classes

*Ta propre copie du site : la copier, la mettre en ligne, l'adapter, l'essayer, et ce qu'il faut garder. Retour au [README](../README.md).*

Le site lui-même n'a ni compte ni base de données : tout tient dans le dépôt. Tu peux le copier tel quel, puis y mettre tes rubriques et tes ressources.

## Copier le dépôt

Sur GitHub, le bouton **Fork** copie le dépôt dans ton compte. Pour une simple copie sur ton ordinateur : **Code → Download ZIP** (voir [Tester sur ton ordinateur](#tester-sur-ton-ordinateur)).

## Activer GitHub Pages (une seule fois)

**Settings → Pages**, puis *Build and deployment* : **Source : GitHub Actions**. Dans une copie
faite avec **Fork**, autorise aussi les workflows, que GitHub y désactive au départ : onglet
**Actions**, puis le bouton qui les active.

Chaque envoi sur `main` lance alors le workflow « Publier le site » (`.github/workflows/publier.yml`) :
il valide les données, construit la bibliothèque et met le site en ligne, en quelques minutes, à
l'adresse `https://<ton-compte>.github.io/<nom-du-dépôt>/`. Pour une première mise en ligne sans
rien modifier : onglet **Actions**, « Publier le site », **Run workflow** sur `main`. Avec la
source « Deploy from a branch », GitHub publierait la branche telle quelle, sans les fichiers de
la bibliothèque, qui ne sont jamais commités : l'onglet Bibliothèque afficherait une erreur (voir
[la mise en ligne](VERIFICATION.md#la-mise-en-ligne)).

## Adapter les réglages

- Dans `reglages.js`, écris le nom de **ton** dépôt dans `depot` (`"ton-compte/nom-du-dépôt"`) : le lien « Code source sur GitHub » mènera alors à ta copie, et l'[espace administrateur](ADMIN.md) (`…/admin/`) écrira dans ton dépôt, avec ton propre jeton. Le titre, la présentation, l'ordre des rubriques et les textes du pied de page se règlent dans le même fichier : voir [Réglages généraux](LISTES.md#réglages-généraux) et [Le pied de page](LISTES.md#le-pied-de-page--auteur-licences-et-ia).
- Pour tes rubriques : [Ajouter une rubrique](LISTES.md#ajouter-une-rubrique) ; pour tes ressources : leurs fiches et la vitrine ([les rubriques et les ressources](LISTES.md), [l'espace administrateur](ADMIN.md)).

## Tester sur ton ordinateur

Télécharge le dépôt (**Code → Download ZIP**), décompresse-le et ouvre `index.html`
dans ton navigateur. Tout fonctionne sans connexion, sauf les polices, les liens externes et
l'onglet Bibliothèque. Celui-ci a besoin de ses fichiers, construits à la publication, et d'un
petit serveur : à la racine du dossier, lance `python3 scripts/construire_bibliotheque.py`, puis
`python3 -m http.server`, et ouvre `http://localhost:8000/bibliotheque/`.

## Les applications qui utilisent une base

Alien Python et Court-circuit passent par Supabase. Pour leur donner ta propre base, ou faire tourner Court-circuit en mode démo, sans base : [SUPABASE.md](SUPABASE.md).

## Ce que tu dois garder

- **La licence** : le code reste sous licence MIT (garde le fichier [`LICENSE`](../LICENSE)), les documents sous licence CC BY-SA 4.0, en mentionnant Babash - NSI Tani Malandi ; un document modifié se partage sous la même licence (la section [Licence](../README.md#licence) du README).
- **Ce qui vient d'ailleurs**, avec sa licence et sa notice : les exercices d'Alien Python (la notice `snt/fichiers/alien-python/LICENCE.txt`, à garder avec `data.js`), les bibliothèques et les polices de Court-circuit (`snt/fichiers/court-circuit/vendor/LICENCES-BIBLIOTHEQUES.txt` et `snt/fichiers/court-circuit/LICENCE.txt`), la page modèle de CodePen et les bibliothèques du TP des donuts (`LICENSE-modele-codepen.txt` et les notices des dossiers `vendor/` de `snt/fichiers/web-interview-donuts/`), les polices des TD (`assets/fonts/`, décrites dans `assets/fonts/LISEZMOI.md` : Atkinson Hyperlegible, JetBrains Mono, Anton et VT323 sous SIL Open Font License 1.1, et « TD Symboles », tirée de DejaVu Sans, sous la licence de DejaVu ; à garder avec leurs fichiers `assets/fonts/LICENCE-*.txt`), le crédit de Natural Earth et de GeoNames au pied du voyageur de commerce.
- **Les activités Capytale** (les dossiers `fichiers/capytale/`) : chacune garde sa licence et ses crédits, donnés au pied de sa page de lecture et dans sa fiche (`donnees/ressources/`). Trois activités (Internet de David Landry, les gloutons de Germain Becker et Sébastien Point, l'escape game de Laura Fléron) et les modules `alien_python.py` et `pixel_art.py` sont sous licence non commerciale (CC BY-NC-SA) : pas d'usage commercial, et une version modifiée se partage sous la même licence. La section [Licence](../README.md#licence) du README les détaille.
- **Les crédits en chaîne** d'une ressource reprise, comme la fiche Python de SNT, ci-dessous.

## Fiche Python (SNT) : modifications par rapport à l'original

L'original est la fiche Compute-it d'Etienne Clave, sur le site exomorphisme.fr (lycée de Sada).

- Bouton de retour vers la rubrique SNT (non imprimé).
- Cases rouges réellement hachurées, couleurs imprimées sans réglage du navigateur.
- **Exercice 3 : départ déplacé de A1 à A2.** Depuis A1, le personnage restait sur la ligne 1
  et ne passait jamais sur une case rouge, donc le `if` n'était jamais vrai.
- Sur téléphone, la feuille A4 est réduite pour tenir dans l'écran.
