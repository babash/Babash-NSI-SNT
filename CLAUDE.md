# Ressources NSI et SNT : règles communes des agents

Ce fichier s'applique à **toute session Claude qui travaille dans ce dépôt**. Les fiches de rôle sont dans `.claude/agents/`.

## Le contexte
- Site publié par GitHub Pages : https://babash.github.io/Babash-NSI-SNT/ (dépôt public `babash/Babash-NSI-SNT`).
- Une refonte est en cours : une bibliothèque unique de ressources et trois parties (l'extérieur, qui comprend la bibliothèque ; l'admin ; l'élève). La référence est le cahier des charges, dans le projet claude.ai « Site SNT-NSI ».
- Documents du projet à lire **avant tout travail** (outil Projects) :
  - `coordination/philosophie-educative.md` : le public, la pédagogie et les valeurs de l'enseignant ; **ses règles de conception (§ 14) s'appliquent à toute ressource** ;
  - `coordination/cahier-des-charges.md` : ce qu'on construit ;
  - `coordination/organisation-des-agents.md` : qui fait quoi ;
  - `coordination/decisions.md` : ce que l'enseignant a décidé ; la décision la plus récente l'emporte ;
  - `coordination/taches.md` : le tableau des tâches ;
  - `design/charte.md` : la charte graphique ;
  - `claude/etat-du-site.md` : l'état laissé par l'ancienne collecte ;
  - `gardien/rapport.md` et `coordination/journal.md` : les contrôles et les publications.
- **Si l'outil Projects n'est pas disponible** (c'est le cas dans les copies isolées des agents) :
  - le chef d'orchestre exporte ces documents dans le dossier d'échange de la copie principale du dépôt, `.claude/echanges/projet/` (un fichier par document, `/` remplacé par `-` : `coordination-decisions.md`…) ;
  - un agent écrit ses livrables destinés au projet dans `.claude/echanges/livrables/` **de sa propre copie** (même chemin relatif) et donne leur chemin complet dans son rapport ; le chef d'orchestre les publie ;
  - ce dossier est exclu de Git : ne jamais le commiter.

## L'organisation
- **Le chef d'orchestre** est le seul interlocuteur de l'enseignant. Il lance les agents, leur écrit et reçoit leurs rapports. Un agent ne pose pas de question à l'enseignant : il la met dans son rapport.
- **Chaque agent ne modifie que les fichiers de son rôle** (voir sa fiche). Pour un autre fichier, il le signale dans son rapport.
- **Le Gardien est le seul à publier sur `main`.**

## Les règles Git
- Une branche par tâche, partant de `origin/main` à jour. Préfixes : `biblio/`, `archi/`, `design/`, `atelier/`, `gardien/`, `orga/`, suivis du numéro de la tâche.
  Exemple : `archi/t02-format-donnees`.
- Avant de commencer et avant de pousser : `git fetch origin '+refs/heads/*:refs/remotes/origin/*'` (un simple `git fetch origin` ne met pas `origin/main` à jour dans les copies des agents), puis `git rebase origin/main` si `main` a avancé.
- Messages de commit : `[T02][archi] Format des données : schéma et référentiels`.
- Auteur des commits : `git config user.name Claude` et `git config user.email noreply@anthropic.com`.
- **Jamais d'envoi forcé** sur `main`. Sur sa propre branche, seulement `--force-with-lease`.
- **Pousser sa branche avant de rendre son rapport** : les espaces de travail sont effacés après un temps d'inactivité.
- Ne jamais supprimer une branche qui n'est pas la sienne. Seule exception : le Gardien peut supprimer une branche déjà fusionnée ou obsolète, après vérification et avec l'accord du chef d'orchestre (décision du 07/11).

## Les règles de contenu
- **Le lien principal** d'une ressource pointe directement vers elle (page, fiche, PDF), jamais vers une page GitHub. Le dépôt peut apparaître en document « code source ».
- **Aucune donnée sensible dans le dépôt**, qui est public : ni mot de passe, ni identifiant (par exemple ceux de démonstration de CyberCase), ni clé secrète, ni nom d'élève. Une clé Supabase « anon » ou « publishable » est publique par conception ; une clé « service_role » ou « secret », jamais.
- **Toute ressource qui collecte des données d'élèves** est signalée : dans le champ `donnees_eleves` de sa fiche (nouveau format), ou dans le rapport tant que l'ancien format est en place (un champ inconnu des listes `*/ressources.js` y provoque une erreur). Toute nouvelle collecte est soumise à l'enseignant. Règle par défaut : un pseudo ou un prénom, au choix de l'élève, jamais de nom de famille (exceptions décidées : Alien Python, SNT 1er jour).
- **La structure suit les textes officiels** : programmes de SNT et de NSI de 2019. La rubrique Professeur principal garde ses thèmes actuels (décision du 07/11) ; la circulaire n° 2018-108 sert de référence. Les thèmes hors programme sont des sections de la vitrine. Tout autre écart est soumis à l'enseignant.
- **Licences et auteur** : documents pédagogiques de l'enseignant en CC BY-SA 4.0, code de ses applications en MIT, auteur affiché « Babash - NSI Tani Malandi ». Une ressource externe est créditée à son site d'origine. Une ressource reprise et modifiée crédite toute la chaîne de ses auteurs et autrices (exemple : CyberCase, d'Etienne Clave sur exomorphisme.fr, d'après une idée de Marion Dufour et le moteur SQL Noir de Hristo Bogoev).
- **TD et éditeurs de code** (philosophie éducative, § 14, règles 19 et 20) : un TD existe toujours en PDF imprimable et en page HTML responsive, auto-corrective par formulaire, corrigée dans le navigateur ; un éditeur de code a toujours la coloration syntaxique, l'indentation automatique, des guides d'indentation qui montrent les blocs (modèle : Lagon Arena), l'autocomplétion contextualisée, et l'erreur affichée telle quelle, puis traduite ou expliquée en français à la demande. Ces deux règles s'appliquent aux créations de l'enseignant ; une ressource externe ne se modifie pas, mais sa fiche signale ce qui lui manque.
- **Applications de jeu** (philosophie éducative, § 14, règle 21 ; Lagon Arena, Gombessa, Alien Python et les suivantes) : chaque élève a un code unique en mots et chiffres (comme `CORAIL-MANTA-482`), qui suffit pour revenir depuis n'importe où ; l'enseignant·e a aussi un code unique et voit ceux de ses élèves ; un lien de classe (et son QR code) ; aucun plafond du nombre d'élèves ; le travail sans enseignant·e est gardé en ligne avec le code. Spécification : `architecture/codes-acces.md` du projet. Les mini-sites des TD restent sans compte ni envoi de données.
- **Écriture** : français clair, et **langage inclusif complet chaque fois que c'est pertinent** : formulations épicènes, double flexion, féminisation des fonctions et point médian (« enseignant·e·s », « fort·e·s »), dans les pages du site comme dans les documents pour les élèves. Décision de l'enseignant du 07/11, prise en connaissance de la circulaire du 5 mai 2021 : elle remplace la règle « pas de point médian ». Un point médian n'est donc jamais une faute à corriger.
- **Design** : la charte « Réseau la nuit » (`design/charte.md`). Tant qu'elle n'est pas validée et publiée, ses fichiers n'existent que sur la branche `design/charte-v1` : une ressource suit alors le style actuel du site. Dessin original : aucun personnage, logo ou illustration d'Android: Netrunner.
- **Caractères spéciaux** : les outils d'écriture de fichiers remplacent une séquence `\uXXXX` par le caractère lui-même (un `\u202e` devient un vrai caractère invisible de contrôle). Un caractère invisible ou spécial s'écrit donc par son code : `chr(0x…)` en Python, `String.fromCharCode(0x…)` en JavaScript, `&#x…;` en HTML, jamais par `\u`. Pour relire une branche : `python3 -I .github/gardien/caracteres.py --diff origin/main...origin/<branche>`.

## Les bases Supabase
- Deux projets, organisation « babash », offre gratuite (2 projets au plus, **aucune sauvegarde**) : `cukahpyqkljiddmimpyi` (SNT 1er jour, Gombessa, Alien Python) et `gkyvaugipddjqjvvpopw` (Lagon Arena). Règles complètes : `architecture/regles-supabase.md` du projet.
- Les agents lisent les **métadonnées seulement** (tables, colonnes, fonctions, règles d'accès, droits, conseillers, `count(*)`), jamais une valeur d'une colonne de données d'élèves, même une ligne, même pour essayer.
- **Aucune modification de base sans que l'enseignant ait vu le SQL exact.** Le chef d'orchestre l'applique (`apply_migration`, au nom du fichier) ; le Gardien vérifie (métadonnées et conseillers) et l'inscrit au journal. Modèle : T36 (SNT 1er jour).
- Une migration est un fichier du dépôt de l'application (`supabase/NNNN-….sql`), avec son SQL inverse et `LISEZMOI.md` ; le script complet (`schema.sql`) change dans le même commit ; un retrait se fait en deux temps (ajouter, publier la page, retirer).
- Chaque objet porte le préfixe de son application (`snt_`, `gb_`, `alien_`, `lagon_`) ; `commun` est réservé à l'identité commune future. Une nouvelle application va dans le projet partagé, après inscription au registre des préfixes.
- Tables : RLS partout, aucun droit direct d'`anon`, accès par des fonctions `security definer` à `search_path` fixé ; les exceptions sont listées dans les règles.
- Jamais de clé `service_role` ou « secret » dans un dépôt, une page ou un message.

## Qui possède quoi
| Fichiers | Rôle |
|---|---|
| `CLAUDE.md`, `.claude/agents/` | Chef d'orchestre |
| `README.md`, `LICENSE`, `.github/gardien/`, la fusion dans `main` | Gardien |
| `assets/*.js` (sauf `assets/fiche.js`, `assets/decor.js`, `assets/equipage.js`, `assets/td-en-ligne.js`), `index.html`, `*/index.html`, `reglages.js`, `.nojekyll`, `.gitignore`, `admin/`, `bibliotheque/`, `eleve/`, `donnees/` (sauf `donnees/ressources/` et `donnees/vitrine.json`), `scripts/`, `.github/workflows/` et `.github/verifier-site.py` (avec l'accord du Gardien) | Architecte |
| `*/ressources.js` (anciennes listes, jusqu'à leur conversion), `donnees/ressources/`, `donnees/vitrine.json`, `<rubrique>/fichiers/` | Bibliothécaire |
| `assets/charte.css`, `assets/style.css`, `assets/fiche.css`, `assets/fiche.js`, `assets/decor.js`, `assets/equipage.js`, `assets/equipage/`, `assets/td-en-ligne.css`, `assets/td-en-ligne.js`, `assets/fonts/`, `assets/favicon.svg`, `charte/`, `design/`, la mise en forme des documents internes | Designer |
| Les fichiers d'une ressource en cours de création (`<rubrique>/fichiers/<nom>/`) | l'Atelier chargé de cette ressource |

Le décor du bandeau est encore dans `assets/site.js` (fonction `scene`) : il passera dans `assets/decor.js` quand la charte sera publiée. D'ici là, toute modification du décor est demandée à l'Architecte dans un rapport.

## Vérifier
- Le dossier temporaire de la session est partagé entre les agents : chacun travaille dans **son propre sous-dossier** (par exemple `<dossier temporaire>/<rôle>-<tâche>/`) et ne réécrit jamais le fichier d'un autre.
- `babash.github.io` est inaccessible depuis les sessions. Pour vérifier le site en ligne, on passe par GitHub Actions : le workflow `.github/workflows/verifier.yml` contrôle les liens et le rendu des pages en ligne, et on lit ses résultats avec `gh api repos/babash/Babash-NSI-SNT/actions/runs` (puis les jobs et les logs).
- En local : `python3 -m http.server` à la racine, puis Playwright (Chromium est préinstallé) pour le rendu à 320, 768 et 1440 px, en clair et en obscur.
- Le README est mis à jour à chaque publication.

## Le rapport de fin de tâche
Chaque agent termine par un rapport au chef d'orchestre, dans cet ordre :
1. **Fait** : ce qui a été fait, en quelques lignes.
2. **Branche** : son nom et le dernier commit poussé.
3. **À valider par l'enseignant** : les choix structurels, avec les options.
4. **Questions** : ce qui bloque ou reste incertain.
5. **Hors de mon domaine** : les fichiers d'un autre rôle à modifier, et pourquoi.
6. **Reste à faire.**
