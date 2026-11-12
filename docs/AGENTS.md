# L'équipe d'agents

*Qui entretient le site, qui possède quels fichiers, et les règles de conception que suit chaque ressource. Retour au [README](../README.md).*

Le site est entretenu par une équipe d'agents Claude (Gardien, Architecte, Bibliothécaire,
Designer, Atelier et Vigie), coordonnés par un chef d'orchestre. Leurs règles communes sont
dans `CLAUDE.md`, à la racine du dépôt, et la fiche de chaque rôle dans `.claude/agents/`.
Chaque tâche se fait sur sa propre branche ; seul le Gardien publie sur `main`, après ses contrôles,
et dès que c'est sûr : un point d'écriture mineur ne bloque pas, il part dans une branche de suite.
Les règles du travail sur GitHub sont détaillées dans [CONTRIBUTING.md](../CONTRIBUTING.md).

Chaque fichier a un rôle propriétaire, indiqué dans le tableau « Qui possède quoi » de
`CLAUDE.md` : par exemple, les listes `ressources.js` au Bibliothécaire, le moteur
(`assets/site.js`) et les pages `index.html` à l'Architecte, la feuille de style et l'icône
du site (`assets/favicon.svg`) au Designer, le README, la documentation (`CONTRIBUTING.md` et `docs/`), le
fichier de licence du dépôt (`LICENSE`) et les outils de `.github/gardien/` au Gardien. Le dossier `donnees/` de
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
