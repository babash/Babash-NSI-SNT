# L'équipe d'agents

*Qui entretient le site, qui possède quels fichiers, et les règles de conception que suit chaque ressource. Retour au [README](../README.md).*

Le site est entretenu par une équipe d'agents Claude (Gardien, Architecte, Bibliothécaire,
Designer, Atelier, Atelier des quiz et Vigie), coordonnés par un chef d'orchestre. Leurs règles communes sont
dans `CLAUDE.md`, à la racine du dépôt, et la fiche de chaque rôle dans `.claude/agents/`.
Chaque tâche se fait sur sa propre branche ; seul le Gardien publie sur `main`, après ses contrôles,
et dès que c'est sûr : un point d'écriture mineur ne bloque pas, il part dans une branche de suite.
Les règles du travail sur GitHub sont détaillées dans [CONTRIBUTING.md](../CONTRIBUTING.md).

Chaque fichier a un rôle propriétaire, indiqué dans le tableau « Qui possède quoi » de
`CLAUDE.md` : par exemple, les anciennes listes `ressources.js` (plus lues depuis le 17 novembre 2026) au Bibliothécaire, le moteur
(`assets/site.js`) et les pages `index.html` à l'Architecte, la feuille de style et l'icône
du site (`assets/favicon.svg`) au Designer, le README, la documentation (`CONTRIBUTING.md` et `docs/`), le
fichier de licence du dépôt (`LICENSE`) et les outils de `.github/gardien/` au Gardien. Le dossier `donnees/` de
la bibliothèque est à l'Architecte (notamment le format des données et les
référentiels), sauf les fiches des ressources (`donnees/ressources/`) et la vitrine
(`donnees/vitrine.json`), qui sont au Bibliothécaire ; l'Architecte peut y créer des fiches
d'exemple pour illustrer le format, et un Atelier ou l'Atelier des quiz y écrit la fiche en
brouillon de la ressource qu'il crée. Le dossier `qcm/` (les sources XML des quiz Pronote,
leurs aperçus et leurs outils) est à l'Atelier des quiz. Depuis le 20 novembre 2026, le
Calendrier des vacances (`calendrier/`) et le futur espace `enseignant/` sont à l'Architecte, sauf
le contenu des exercices du Calendrier (`calendrier/exercices/<thème>.json`), écrit par les Ateliers.
Un agent ne modifie que ses fichiers ; pour les autres, il le signale dans son rapport.
Une session Claude que l'enseignant lance lui-même pour développer une application suit
toutes ces règles, publication par le Gardien comprise.
Le Gardien peut supprimer une branche déjà fusionnée ou devenue inutile, après avoir vérifié
qu'il n'y a rien à récupérer et avec l'accord du chef d'orchestre ; en pratique, les sessions
des agents n'en ont pas le droit sur GitHub : le Gardien prépare la liste, et l'enseignant
supprime les branches.

Toute ressource produite ou retravaillée suit les règles de conception de la philosophie
éducative de l'enseignant : une version en ligne utilisable sur téléphone et une version
papier A4 en noir et blanc, peu de texte, des erreurs expliquées, la correction automatique
chaque fois que c'est possible… Quatre règles s'appliquent toujours aux créations de
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
  restent sans compte ni envoi de données ;
- un **quiz** (un QCM pour Pronote) part d'une note de cadrage validée avant toute génération :
  depuis le 20 novembre 2026, l'enseignant a délégué au chef d'orchestre la validation et la
  correction des QCM Pronote. Ses questions sont des QCU à 4 options : une juste et trois distracteurs
  tirés des erreurs typiques des élèves, avec pour chaque option un feedback bienveillant qui
  explique, et l'objectif affiché au début de chaque question ; on y analyse du code et on y
  cherche des erreurs. Le fichier suit le format XML Moodle que lit Pronote, avec toutes ses
  balises obligatoires et le code coloré ; la bonne réponse n'est jamais mise en avant ni placée
  selon un motif. La révision d'un quiz existant ne touche que la forme, jamais le fond.

Une ressource externe ne se modifie pas : sa fiche peut signaler ce qui lui manque. Le Gardien
vérifie ces règles avant de publier une ressource. Les ressources déjà en ligne n'ont pas
encore été revues sous cet angle.

Les décisions de l'enseignant du 20 novembre 2026 s'y ajoutent (`CLAUDE.md`, § 4 à § 6) :
- « On ne se compare pas, mais on peut être fier·e de ce qu'on a appris » : aucun classement,
  aucun rang, aucun score visible, aucune « série de jours » (on dit « jours différents ») ;
  l'XP reste cachée et se dépense en apparences d'avatar ;
- on ne demande jamais son genre à un·e élève, et toute personnalisation va sur tout avatar ;
- dans un exercice « trouve l'erreur », le message d'erreur réel est toujours donné (Python 3.13,
  ou SQLite pour le SQL), avec la coloration syntaxique ; le code affiché a une indentation très
  visible et une coloration qui se lit aussi en noir et blanc, et les consoles sont compactes ;
- les exemples viennent du quotidien des élèves à Mayotte (la barge, le taxi, le marché, le
  lagon…), et aussi d'ailleurs, avec des prénoms variés, sans nom de famille ni marque ; aucun
  mot n'est interdit, mais une ressource ou une série ne ramène pas toujours Mayotte aux mêmes
  images (précision du 21 novembre : la présence d'un mot n'est pas un motif de refus) ;
- l'univers « Mamoudzou 2046 » ne sert qu'aux jeux et aux avatars ; le nouveau style des
  feuilles, « Signal pirate », s'applique aux TD depuis le 21 novembre (gabarit
  `charte/gabarit-td/`, conversion des TD en cours), pas encore aux autres documents ;
- le cours-quiz (dépôt QuizzNSI) vient en tête de séquence, avant le cours ou le TD ;
- le soir : « on ne promeut aucune religion, mais on ne fait pas comme si c'était problématique
  qu'elles existent ou d'en avoir une » (un emblème national, comme le croissant et les étoiles du
  drapeau des Comores sur un maillot, est admis) ; un clin d'œil à une œuvre connue passe par le
  nom et l'idée, jamais par la forme ; « Imprimer la feuille », dans un TD en ligne, imprime la
  feuille vierge.

Règle d'écriture : les pages du site et les documents pour les élèves s'écrivent en langage
inclusif chaque fois que c'est pertinent (formulations épicènes, double flexion, féminisation
des fonctions et point médian, comme « enseignant·e·s »), selon la décision de l'enseignant du
7 novembre 2026.

Les documents de coordination (cahier des charges, philosophie éducative, registre des
décisions, organisation des agents, tableau des tâches, journal des publications, rapport du
Gardien) sont dans le projet claude.ai « Site SNT-NSI ». Leur partie pédagogique, la
philosophie, les règles universelles et les types de ressources, est publiée dans
[La pédagogie du site](pedagogie/README.md).
