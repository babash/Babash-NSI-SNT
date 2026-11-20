# Le moteur d'avatars `Equipage`

Module JavaScript sans dépendance : `assets/equipage.js`. Il dessine en pixel art (grille de 48 × 64, gabarit « tout rond », contour automatique) l'avatar d'un·e élève décrit par un petit objet JSON, et le margouillat vert à turbine. Démonstration : `charte/avatars.html`.

Rien n'est envoyé, rien n'est gardé par le module : c'est l'application qui garde la description.

## Charger le module

```html
<script src="../assets/equipage.js"></script>
```

Il crée `window.Equipage` (ou `module.exports` sous Node, pour des essais). Il injecte une seule feuille de style (`<style id="equipage-css">`).

## La description (ce que la base garde)

Un objet JSON d’environ 400 octets (moins de 500). Tout champ absent ou inconnu prend sa valeur par défaut : `Equipage.normaliser(d)` renvoie toujours une description valide (à appeler avant d'enregistrer).

```json
{
  "v": 1,
  "lignee": "humain",
  "teint": 5,
  "corps": "moyenne",
  "coiffure": "court",
  "cheveux": "noirs",
  "haut": "tshirt",
  "bas": "pantalon",
  "chaussures": "baskets",
  "objets": { "tete": "aucun", "visage": "aucun", "dos": "aucun", "main": "aucun", "epaule": "aucun", "autour": "aucun" },
  "fauteuil": false,
  "compagnon": "margouillat",
  "couleurs": { "haut": "canard", "bas": "anthracite", "accent": "cyan", "chaussures": "blanches", "yeux": "bruns" }
}
```

| Champ | Valeurs |
|---|---|
| `lignee` | `humain`, `cyber`, `nuee`, `mutant`, `lagon`, `esprit`, `greffe` |
| `teint` | entier de 1 à 8 (sans effet pour Nuée et Esprit) |
| `corps` | `fine`, `moyenne`, `ronde` |
| `coiffure` | 16 coiffures (`court`, `rase`, `lisses`, `boucles`, `tresses`, `afro_pixel`, `capuche`…) |
| `cheveux` | un nom de la palette `cheveux`, ou `#rrggbb` |
| `haut`, `bas`, `chaussures` | 10, 7 et 6 pièces ; `haut: "aucun"` n'existe que pour Nuée et Esprit |
| `objets` | un objet par emplacement, cumulables : 9 pour la tête, 7 pour le visage, 6 pour le dos, 8 pour la main, 3 pour les épaules, 6 autour (39 en tout) |
| `fauteuil` | `true` ou `false` : une aide technique, jamais à gagner |
| `compagnon` | `aucun`, `margouillat` (de départ), `maki`, `robot`, `tortue`, `roussette` (marqués `gagne: true` dans le catalogue) |
| `couleurs.*` | un nom de palette (`tissu`, `neon`, `chaussures`, `yeux`) ou `#rrggbb` |

Les listes exactes, avec les noms à afficher : `Equipage.catalogue`, recopié dans `assets/equipage/catalogue.json` (à régénérer quand le module change). Une base de données peut s'en servir pour vérifier une description, mais le plus simple est de garder le JSON tel quel (`jsonb`) et de le normaliser à l'affichage.

Aucune pièce n'est liée à un genre. Les anciennes clés `accessoire`, `tete` et `visage` (version d'essai) sont reprises dans leur emplacement par `normaliser`.

## Afficher un avatar

```js
var a = Equipage.creer(element, description, { taille: 96, etat: 'content' });
a.etat('triste');        // change d'état
a.maj(nouvelleDescription);
a.options({ taille: 48 });
a.description;           // copie normalisée
a.detruire();
```

Options :

| Option | Défaut | Rôle |
|---|---|---|
| `taille` | 96 | hauteur en pixels CSS |
| `etat` | `repos` | `repos`, `content`, `tres_content`, `triste`, `concentre`, `salue`, `dort` |
| `cadre` | `auto` | `pastille` (visage, sous 32 px), `buste` (32 à 63 px), `entier` (64 px et plus) |
| `compagnon` | `true` | `false` pour cacher le compagnon (il n'apparaît qu'en cadre entier) |
| `anime` | `true` | `false` pour l'image fixe |
| `alt` | texte généré | `''` pour un avatar décoratif (`aria-hidden`) |
| `fond` | selon le thème | `obscur` ou `clair` pour forcer le liseré de lecture |
| `net` | `false` | `true` arrondit la taille à un multiple entier de la grille |

`Equipage.svg(description, options)` renvoie la même image en chaîne SVG. `Equipage.texte(description, etat)` renvoie le texte alternatif.

Netteté : 24 px (pastille 24 × 24), 32 px (buste 32 × 32), 56, 112, 168 ou 224 px (entier) tombent sur des pixels entiers ; les autres tailles restent nettes, avec des pixels de largeur inégale.

## Les états

Sept états, chacun une suite de 3 à 5 images (CSS, sans script) : au repos (respire, cligne), content·e (sautille), très content·e (bras levés, étincelles : pour la réussite), triste (nuage et larme : après une erreur), concentré·e (tablette, langue tirée), salue, dort (Zzz : salon d'attente). Avec `prefers-reduced-motion`, à l'impression ou avec `anime: false`, seule la première image reste.

## Le margouillat

```js
Equipage.margouillat(encadre, { bord: 'haut', position: '80%', taille: 24, etat: 'neutre' });
```

- `bord` : `haut` (il marche dessus), `bas` (au plafond), `gauche` (il monte), `droite` (il descend). L'encadré passe en `position: relative` s'il était statique.
- `taille` : longueur en px, ou une longueur CSS comme `'9mm'` pour le papier.
- `etat` : `neutre`, `content`, `triste` ; `sens` et `miroir` pour forcer l'orientation.
- `encre` : `couleur` (défaut), `noir`, ou `auto` (couleur à l'écran, noir à l'impression).
- `Equipage.margouillatSVG(options)` renvoie la chaîne SVG.

## Compagnon seul

`Equipage.compagnonSVG('maki', { etat: 'content', taille: 48 })`.

## Ce qui reste à l'application

- Garder la description (une par élève), et la liste de ce que l'élève a débloqué (le module dessine tout, il ne sait pas ce qui est gagné).
- Ne montrer les avatars qu'aux camarades de la classe ; aucun classement, aucun score à côté d'un avatar.

Dessins originaux, CC BY-SA 4.0 ; code sous licence MIT. Auteur : Babash - NSI Tani Malandi.
