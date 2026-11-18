# L'espace administrateur

*Annoter et modifier les fiches, composer les onglets, voir l'aperçu, puis enregistrer d'un clic ou télécharger les fichiers. Retour au [README](../README.md).*

L'espace administrateur est à l'adresse
[babash.github.io/Babash-NSI-SNT/admin/](https://babash.github.io/Babash-NSI-SNT/admin/), depuis le
17 novembre 2026. Aucune page publique n'y mène et les moteurs de recherche ne l'indexent pas
(`noindex`), mais la page n'est pas secrète : comme tout le dépôt, elle est publique. Elle écrit
les fiches de la bibliothèque et la vitrine (voir [les données de la bibliothèque](BIBLIOTHEQUE.md)),
jamais le contenu des ressources (décision du 6 novembre 2026).

## Ce qu'on y fait

| Vue | Contenu |
|---|---|
| **Ressources** | toutes les fiches, avec une recherche et des filtres (statut, visibilité, enseignement, « Avec des notes ») ; des étiquettes signalent ce qui est caché, le statut, les notes et les fiches modifiées |
| **Fiche** | le statut et les notes personnelles ; le titre, l'accroche, le résumé, la présentation, l'objectif et la durée ; les classements et les mots-clés ; les thèmes du programme ; les documents (libellé, rôle, adresse, document principal, visibilité pour l'extérieur et pour les élèves, ordre). Les autres champs (auteurs et autrices, licence, crédits, notions…) sont montrés et gardés tels quels |
| **Onglets du site** | pour chaque rubrique : le titre, le nom court, la ligne sous le titre et le texte d'introduction ; les sections, leur ordre et leurs titres ; dans chaque section, les ressources montrées, dans l'ordre (boutons « Monter » et « Descendre », glisser-déposer, ou cases à cocher avec une recherche). La sélection « À la une » se règle de la même façon, avec une étiquette et des dates facultatives : l'étiquette (« Ressource du mois ») s'affiche en tête des étiquettes de la ressource, et la recherche de l'accueil la retrouve. Depuis le 17 novembre 2026, les rubriques et l'accueil montrent la vitrine telle quelle : ce qu'on compose ici change vraiment les pages |
| **Aperçu** | l'onglet tel qu'il sera, dessiné par le site lui-même avec les changements en attente, à la largeur d'un téléphone, d'une tablette ou d'un ordinateur |
| **Changements** | les fichiers modifiés et, pour chacun, ce qui change ; chaque changement s'annule. C'est là qu'on enregistre ou qu'on télécharge |
| **Mot de passe** | le jeton GitHub et le mot de passe administrateur (ci-dessous) |

Les changements en attente sont gardés dans le navigateur : ils survivent à un rechargement de la
page, jusqu'à ce qu'on les enregistre ou qu'on les annule. Avant tout enregistrement, ils sont
validés dans la page (`assets/donnees.js`), avec les mêmes erreurs que `scripts/valider_donnees.py` :
une erreur bloque l'enregistrement, qui ne peut donc pas arrêter « Publier le site ».

**Les notes personnelles et les documents cachés restent lisibles dans le dépôt public** : la
bibliothèque publique ne les montre pas, mais les fiches sont publiques. Jamais de mot de passe,
d'identifiant ni de nom d'élève dans une note.

## Enregistrer ou télécharger

- **Enregistrer** (admin déverrouillé) : un seul commit sur `main`, au nom du compte du jeton, avec
  le message « [admin] … ». Le site en ligne suit quelques minutes plus tard, après « Publier le
  site » ([la mise en ligne](VERIFICATION.md#la-mise-en-ligne)). Si un fichier a changé sur `main`
  depuis son ouverture dans l'admin (un autre appareil, un agent…), rien n'est écrit : l'admin le
  dit, propose de télécharger vos versions, puis recharge les fichiers.
- **Télécharger** (sans mot de passe) : une archive .zip des fichiers modifiés, avec leurs chemins.
  Pour l'enregistrer : sur GitHub, **Add file → Upload files**, déposer le contenu de l'archive à
  la racine du dépôt (les dossiers `donnees/…` sont gardés), puis **Commit changes**.

L'admin n'écrit que deux sortes de fichiers : les fiches `donnees/ressources/<identifiant>.json` et
`donnees/vitrine.json`. Un changement gardé dans le navigateur qui viserait un autre fichier est
ignoré, signalé et effacé.

## Le mot de passe administrateur et le jeton

Pour enregistrer d'un clic, la page a besoin d'un **jeton GitHub**, une clé qui lui permet
d'écrire dans le dépôt. Le **mot de passe administrateur** protège ce jeton sur chaque appareil
(décision de l'enseignant du 17 novembre 2026).

**La première fois sur un appareil** (ordinateur, téléphone) :

1. Sur GitHub, connecté·e au compte du dépôt :
   [Settings › Developer settings › Personal access tokens › Fine-grained tokens › Generate new token](https://github.com/settings/personal-access-tokens/new).
2. Un nom (« Admin du site Ressources ») et une **date d'expiration** (90 jours, par exemple).
3. **Repository access** : « Only select repositories », puis ce dépôt seulement.
4. **Permissions** › Repository permissions › **Contents : Read and write**, rien d'autre.
5. « Generate token », puis copier le jeton (il commence par `github_pat_`) : GitHub ne le montre
   qu'une fois.
6. Dans l'admin, vue **Mot de passe** : coller le jeton, choisir un mot de passe d'au moins
   10 caractères (une phrase de quatre ou cinq mots, facile à retenir), le confirmer, puis
   « Chiffrer et garder le jeton sur cet appareil ».

**Les visites suivantes** : le mot de passe seul déverrouille l'admin pour la visite. Sans lui,
tout reste possible en lecture : modifier, voir l'aperçu, télécharger les fichiers.

- **Verrouiller** oublie le jeton déchiffré ; le mot de passe le déverrouillera de nouveau.
- **Oublier cet appareil** efface le jeton chiffré de l'appareil. C'est aussi ce qu'on fait après
  un mot de passe oublié, avant de recoller un jeton avec un nouveau mot de passe.
- En cas de perte d'un appareil, ou quand le jeton ne sert plus : le révoquer sur la même page de
  GitHub.

**Ce que protège le mot de passe** : le jeton est gardé chiffré dans le navigateur, jamais en
clair (PBKDF2-SHA-256 avec 600 000 itérations et un sel aléatoire, puis AES-GCM avec un vecteur
aléatoire). Déchiffré, il reste en mémoire le temps de la visite. Le jeton n'est envoyé qu'à
GitHub (`api.github.com`), jamais mis dans une adresse ni dans le dépôt. Le mot de passe n'est
gardé nulle part et n'est envoyé à personne.

**Ce qu'il ne protège pas** : il ne rend pas l'admin secret. La page, les fiches, les notes et les
documents cachés restent publics, et quiconque peut ouvrir l'admin, tout modifier et télécharger
des fichiers : seul le jeton permet d'écrire dans le dépôt.

## Les tests

- `scripts/tests/test_admin_donnees.js` (Node.js) : la validation de l'admin, comparée à
  `scripts/valider_donnees.py` sur toutes les fiches et sur des fiches fautives. Il tourne dans le
  contrôle « Données de la bibliothèque » ([la vérification automatique](VERIFICATION.md)).
- `scripts/tests/test_admin.py` (Python, Playwright et Chromium) : l'admin dans le navigateur, avec
  une API GitHub simulée, un faux jeton et un faux mot de passe (aucune écriture sur le vrai dépôt) :
  modifier et télécharger, ranger au clavier, l'aperçu, le chiffrement et le déverrouillage, un seul
  commit, le conflit, les chemins refusés, le rendu de 320 à 1440 pixels, en clair et en obscur.
  Depuis la racine du dépôt : `python3 -I -B scripts/tests/test_admin.py`.
