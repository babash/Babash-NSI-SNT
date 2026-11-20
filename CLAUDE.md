# Ressources NSI et SNT : règles communes des agents

Ce fichier s'applique à **toute session Claude qui travaille dans ce dépôt**. Les fiches de rôle sont dans `.claude/agents/`.

## 1. Le contexte et les documents
- Site publié par GitHub Pages : https://babash.github.io/Babash-NSI-SNT/ (dépôt public `babash/Babash-NSI-SNT`).
- Une refonte est en cours : une bibliothèque unique de ressources et trois parties (l'extérieur, qui comprend la bibliothèque ; l'admin ; l'élève). La référence est le cahier des charges, dans le projet claude.ai « Site SNT-NSI ».
- Documents du projet à lire **avant tout travail** (outil Projects) :
  - `coordination/philosophie-educative.md` : le public, la pédagogie et les valeurs de l'enseignant, et ses règles de conception (§ 5 ci-dessous) ;
  - `coordination/cahier-des-charges.md` : ce qu'on construit ;
  - `coordination/organisation-des-agents.md` : qui fait quoi ;
  - `coordination/decisions.md` : ce que l'enseignant a décidé ; la décision la plus récente l'emporte ;
  - `coordination/taches.md` : le tableau des tâches ;
  - `design/charte.md` : la charte graphique ;
  - `claude/etat-du-site.md` : l'état laissé par l'ancienne collecte ;
  - `gardien/rapport.md` et `coordination/journal.md` : les contrôles et les publications ;
  - selon la tâche : `design/univers.md` (l'univers « Mamoudzou 2046 »), `architecture/compte-commun.md` (compte, XP, hauts faits, avatars) et `architecture/calendrier-vacances.md`.
- **Sans l'outil Projects** (c'est le cas dans les copies isolées des agents), on passe par le dossier d'échange, exclu de Git : ne jamais le commiter.
  - Le chef d'orchestre exporte ces documents, et ceux que cite la fiche de l'agent ou sa tâche, dans `.claude/echanges/projet/` de la copie principale du dépôt, ou dans un sous-dossier du dossier temporaire de la session : un fichier par document, `/` remplacé par `-` (`coordination-decisions.md`…).
  - Un agent écrit ses livrables destinés au projet dans `.claude/echanges/livrables/` **de sa propre copie** (même chemin relatif) et donne leur chemin complet dans son rapport ; le chef d'orchestre les publie.

## 2. L'organisation
- **Le chef d'orchestre** est le seul interlocuteur de l'enseignant. Il lance les agents, leur écrit et reçoit leurs rapports. Un agent ne pose pas de question à l'enseignant : il la met dans son rapport.
- **Toute question à l'enseignant est une question fermée, à cliquer** (règle du 20/11, 14:42) : 2 à 4 options courtes, et il répond au clic. Cela vaut aussi pour les questions des rapports d'agents (§ 9), que le chef d'orchestre transmet.
- **Chaque agent ne modifie que les fichiers de son rôle** (§ 7). Pour un autre fichier, il le signale dans son rapport.
- **L'enseignant valide les changements structurels** : le format des données, les référentiels, les adresses, les rubriques ou thèmes, la charte, une nouvelle partie du site, et tout ce qui touche aux données d'élèves.
- **Un choix fait par délégation vaut l'accord de l'enseignant** (« avance le plus possible sans moi », 10/11, 11:48 ; règle écrite le 12/11) : le Gardien peut publier un changement structurel que le chef d'orchestre a choisi par délégation et inscrit au registre des décisions. **Exception : les bases** (et donc les données d'élèves qu'elles contiennent) : leur SQL exact est toujours montré à l'enseignant avant d'être appliqué (§ 6). Une seule délégation a été donnée pour une base : la migration du Calendrier des vacances (§ 6).
- **Le chef d'orchestre ne modifie pas le site.** Il possède `CLAUDE.md` et `.claude/agents/`, applique les migrations de base que l'enseignant a vues (§ 6) et publie dans le projet les livrables des agents.
- **Les sessions de développement** d'une application, lancées par l'enseignant hors de l'orchestre, suivent **toutes** ces règles, y compris la publication par le Gardien (décision du 12/11) ; le chef d'orchestre les leur transmet.
- **Le Gardien est le seul à publier sur `main`.** On met en ligne **dès que c'est sûr** (consigne de l'enseignant du 10/11, 17:48) : une branche conforme est publiée sans attendre, et un point d'écriture mineur ne bloque pas, il part dans une branche de suite (verdict « publié avec suites » de la fiche du Gardien).

## 3. Le travail sur Git
- Une branche par tâche, partant de `origin/main` à jour. Préfixes : `biblio/`, `archi/`, `design/`, `atelier/`, `qcm/`, `gardien/`, `orga/`, suivis du numéro de la tâche. Exemple : `archi/t02-format-donnees`.
- Avant de commencer et avant de pousser : `git fetch origin '+refs/heads/*:refs/remotes/origin/*'` (un simple `git fetch origin` ne met pas `origin/main` à jour dans les copies des agents), puis `git rebase origin/main` si `main` a avancé.
- Messages de commit : `[T02][archi] Format des données : schéma et référentiels`. Auteur des commits : `git config user.name Claude` et `git config user.email noreply@anthropic.com`.
- **Jamais d'envoi forcé** sur `main`. Sur sa propre branche, seulement `--force-with-lease`.
- **Pousser sa branche avant de rendre son rapport** : les espaces de travail sont effacés après un temps d'inactivité.
- Ne jamais supprimer une branche qui n'est pas la sienne. Seule exception : le Gardien peut supprimer une branche déjà fusionnée ou obsolète, après vérification et avec l'accord du chef d'orchestre (décision du 07/11). En pratique, la session est refusée (403) : le Gardien prépare la liste, et l'enseignant supprime depuis GitHub.

## 4. Les règles de contenu
- **Liens.** Le lien principal d'une ressource pointe directement vers elle (page, fiche, PDF), jamais vers une page GitHub. Le lien vers le dépôt GitHub apparaît sur tous les sites (décision de l'enseignant du 10/11, 22:58), toujours comme lien secondaire : chaque page publiée (le site Ressources, les applications, les mini-sites des TD) porte en pied de page un lien « Code source sur GitHub » vers son dépôt, à côté de l'auteur et de la licence ; la fiche de chaque ressource qui a un dépôt le donne en document « Code source ». Pour une ressource externe, on ne modifie pas son site, mais sa fiche donne son dépôt s'il est public.
- **Données sensibles.** Aucune donnée sensible dans le dépôt, qui est public : ni mot de passe, ni identifiant (ceux de démonstration de CyberCase ne sont jamais écrits, même dans un rapport ou une note), ni clé secrète, ni nom d'élève. Une clé Supabase « anon » ou « publishable » est publique par conception ; une clé « service_role » ou « secret », jamais, ni dans un dépôt, ni dans une page, ni dans un message. De même : aucun code de classe réel, aucune clé d'enseignant·e, aucun pseudo d'élève, et jamais le vrai nom de l'enseignant (rappel du 20/11).
- **Données d'élèves.** Toute ressource qui collecte des données d'élèves est signalée : dans le champ `donnees_eleves` de sa fiche (nouveau format), ou dans le rapport tant que l'ancien format est en place (un champ inconnu des listes `*/ressources.js` y provoque une erreur). Toute nouvelle collecte est soumise à l'enseignant. Règle par défaut : un pseudo ou un prénom, au choix de l'élève, jamais de nom de famille. Exception décidée : SNT 1er jour (prénom et nom). Alien Python passe à « prénom ou pseudo » avec T39 (décision du 10/11, vers 18:00) ; d'ici là, il enregistre encore des prénoms.
- **Visibilité.** Pour le moment, **rien n'est caché** : tous les documents sont visibles de l'extérieur et des élèves, corrigés, guides, espaces professeur et code source compris ; l'enseignant réglera lui-même la visibilité dans l'admin (décision du 12/11, 08:36).
- **Programmes.** La structure suit les textes officiels : programmes de SNT et de NSI de 2019. La rubrique Professeur principal garde ses thèmes actuels (décision du 07/11) ; la circulaire n° 2018-108 sert de référence. Les thèmes hors programme sont des sections de la vitrine. Tout autre écart est soumis à l'enseignant.
- **Licences et auteur.** Documents pédagogiques de l'enseignant en CC BY-SA 4.0, code de ses applications en MIT, auteur affiché « Babash - NSI Tani Malandi ». Une ressource externe est créditée à son site d'origine. Une ressource reprise et modifiée crédite toute la chaîne de ses auteurs et autrices (exemple : CyberCase, d'Etienne Clave sur exomorphisme.fr, d'après une idée de Marion Dufour et le moteur SQL Noir de Hristo Bogoev).
- **Écriture.** Français clair, et langage inclusif complet chaque fois que c'est pertinent : formulations épicènes, double flexion, féminisation des fonctions et point médian (« enseignant·e·s », « fort·e·s »), dans les pages du site comme dans les documents pour les élèves. Décision de l'enseignant du 07/11, prise en connaissance de la circulaire du 5 mai 2021 : elle remplace la règle « pas de point médian ». Un point médian n'est donc jamais une faute à corriger.
- **Exemples de Mayotte** (consigne du 19/11, reprise le 20/11). Les cours, les TD et les quiz s'ancrent dans des exemples connus des élèves : la barge, le bouchon jusqu'à Mamoudzou, le taxi, le marché, le doukabé, la boîte de chips (sans nom de marque), les mangues, le lagon, les marées. Prénoms variés d'ici et d'ailleurs, jamais de nom de famille ; aucune marque, aucun objet religieux, aucune arme, aucun cliché.
- **Design.** La charte « Réseau la nuit » (`design/charte.md`). Tant qu'elle n'est pas validée et publiée, ses fichiers n'existent que sur la branche `design/charte-v1` : une ressource suit alors le style actuel du site. Dessin original : aucun personnage, logo, illustration ou cadre de carte d'Android: Netrunner. Contrastes : au moins 4,5:1 pour le texte ; une fois la charte publiée, ses seuils : texte courant ≥ 7:1, petit texte ≥ 4,5:1, traits utiles ≥ 3:1.
- **Univers et nouveau style** (décisions du 20/11 ; `design/univers.md`).
  - L'univers « Mamoudzou 2046 » (la Flottille, l'équipage, les lignées) : son histoire ne sert que dans les jeux et les avatars.
  - Les feuilles (TD, contrôles, fiches, cours-quiz) prendront le design « Signal pirate » (trait fin, trame, néons en débordement, fond blanc, aucun grand aplat sombre, rien d'essentiel par la couleur, 10 pt au moins) et des clins d'œil cachés (un margouillat vert, avec une petite turbine au bout de la queue), **sans personnage ni récit**.
  - **Ce style n'est pas encore appliqué aux vrais documents** (« pas encore ») : d'ici là, la charte « Réseau la nuit » reste en place, et une ressource livrée suit le style actuel du site.
  - Arriveront avec le nouveau style, pas avant : les polices hébergées sur le site, et la mention « conçu avec l'aide de l'IA » sur toutes les pages.
- **Adresses.** Le renommage des dépôts publiés est décidé (20/11) : minuscules et tirets, avec des dépôts de redirection. Tant qu'il n'est pas fait, on garde les adresses actuelles.
- **Caractères spéciaux.** Les outils d'écriture de fichiers remplacent une séquence `\uXXXX` par le caractère lui-même (un `\u202e` devient un vrai caractère invisible de contrôle). Un caractère invisible ou spécial s'écrit donc par son code : `chr(0x…)` en Python, `String.fromCharCode(0x…)` en JavaScript, `&#x…;` en HTML, jamais par `\u`. Pour relire une branche : `python3 -I .github/gardien/caracteres.py --diff origin/main...origin/<branche>`.

## 5. Les règles de conception
**Toute ressource suit les règles de conception de la philosophie éducative (§ 14).** Les règles 19 à 22 en bref :
- **TD** (règle 19) : toujours en PDF imprimable et en page HTML responsive, auto-corrective par formulaire, corrigée dans le navigateur. Ce mini-site reste sans compte ni envoi de données.
- **Éditeurs de code** (règle 20) : toujours la coloration syntaxique, l'indentation automatique, des guides d'indentation qui montrent les blocs (modèle : Lagon Arena), l'autocomplétion contextualisée, et l'erreur affichée telle quelle, puis traduite ou expliquée en français à la demande.
- **Applications de jeu** (règle 21 ; Lagon Arena, Gombessa, Alien Python et les suivantes) : chaque élève a un code unique en mots et chiffres (comme `CORAIL-MANTA-482`), qui suffit pour revenir depuis n'importe où ; l'enseignant·e a aussi un code unique et voit ceux de ses élèves ; un lien de classe (et son QR code) ; aucun plafond du nombre d'élèves ; le travail sans enseignant·e est gardé en ligne avec le code. Chaque application tire ses mots de sa propre liste du registre. Spécification T39 : `architecture/codes-acces.md`. Court-circuit y entre avec sa deuxième version (T58, décision du 12/11 vers 07:55) : un code élève de 2 mots et 3 chiffres (liste « l'atelier »), et les codes gardés en ligne (« Mes codes »), en service depuis le 13/11 (SQL accepté par l'enseignant à 06:45, migrations appliquées à 06:48 et 06:49).
- **Quiz** (règle 22) : une note de cadrage validée avant toute génération ; des QCU à 4 options, un feedback par option ; le format XML Moodle de Pronote ; la révision d'un quiz existant ne touche que la forme, jamais le fond. Détail : fiche `.claude/agents/quiz.md`. Pour les QCM Pronote, l'enseignant a délégué la correction et la validation (« corrige et valide sans moi », 20/11, 14:45) : le chef d'orchestre valide la note de cadrage et les corrections.
- Les règles 19 à 22 s'appliquent aux créations de l'enseignant. Une ressource externe ne se modifie pas, mais sa fiche signale ce qui lui manque.

**Décisions du 20/11, qui amendent la philosophie éducative :**
- **« On ne se compare pas, mais on peut être fier·e de ce qu'on a appris. »** Aucun classement, aucun rang, aucun score visible, aucune « série de jours » (on dit « jours différents »). L'XP existe mais reste **cachée** : elle se dépense en apparences d'avatar. Les avatars et les hauts faits ne sont visibles que des camarades de la classe. L'enseignant·e voit tout pour ses classes et peut attribuer de l'XP. Spécification : `architecture/compte-commun.md`.
- **Genre** (15:10) : on ne demande jamais son genre à un·e élève ; aucune étiquette ni norme de genre ; toute personnalisation va sur tout avatar.
- **« Trouve l'erreur »** (15:04) : on donne toujours le message d'erreur réel (Python 3.13, ou SQLite pour le SQL), avec la coloration syntaxique.
- **Code affiché** (15:00) :
  - une indentation très visible : un filet par niveau et une bande grise ;
  - une coloration qui se lit aussi en noir et blanc : mots-clés en gras, fonctions soulignées, chaînes en italique, commentaires gris, contrastes d'au moins 7:1 ;
  - des consoles compactes : une ligne de console par ligne de texte, pas de grande boîte pour une sortie.
- **Cours-quiz** (dépôt `babash/QuizzNSI`) : il vient **en tête de séquence**, avant le cours ou le TD, les TP, le TD type bac et la fiche de révision. Deux gabarits : `introduction` (15 minutes, 12 questions dont 2 au plus de type relier, puzzle ou ligne fautive, pas de nuage de mots ; 8 écrans de cours au plus, 25 mots par écran au plus) et `revision` (un bilan avant un contrôle, 20 questions à choix).

## 6. Les bases Supabase
- Une seule base pour toutes les applications (T42) : `cukahpyqkljiddmimpyi` (nommé « SNT-1er Jour », à renommer « Babash - applications » par l'enseignant), organisation « babash », offre gratuite (2 projets au plus, aucune sauvegarde). Lagon Arena y déménage depuis `gkyvaugipddjqjvvpopw`, qui ne garde que les objets `guilde_*`, auxquels on ne touche pas. Règles : `architecture/regles-supabase.md` ; plan : `architecture/base-unique.md` ; liste des tables : `architecture/registre-tables.md`.
- Les agents lisent les **métadonnées seulement** (tables, colonnes, fonctions, règles d'accès, droits, conseillers, `count(*)`), jamais une valeur d'une colonne de données d'élèves, même une ligne, même pour essayer.
- Aucune modification de base sans que l'enseignant ait vu le SQL exact (seule exception : le Calendrier des vacances, ci-dessous). Le chef d'orchestre l'applique (`apply_migration`, au nom du fichier) ; le Gardien vérifie (métadonnées et conseillers) et l'inscrit au journal. Modèle : T36 (SNT 1er jour).
- Une migration est un fichier du dépôt de l'application (`supabase/NNNN-….sql`, avec `begin;` et `commit;`), avec son inverse `NNNN-…-inverse.sql` et `LISEZMOI.md` ; le script complet (`schema.sql`) change dans le même commit ; un retrait se fait en deux temps (ajouter, publier la page, retirer). Par `apply_migration`, on retire seulement `begin` et `commit`.
- Un schéma par application (`snt_premier_jour`, `gombessa`, `alien`, `lagon`, `court_circuit`, `vacances`, `commun`), jamais exposé à l'API, avec des tables en français et un commentaire sur chaque table et chaque colonne ; seules les fonctions d'entrée sont dans `public`, avec le préfixe de l'application (`snt_`, `gb_`, `alien_`, `lagon_`, `cc_`, `cv_`, `commun_`). Une nouvelle application y prend son schéma, après inscription au registre.
- **Calendrier des vacances** (T105 ; schéma `vacances`, préfixe `cv_`) : l'enseignant a délégué sa migration (« procède sans ma validation pour l'essentiel », 20/11). Le chef d'orchestre relit le SQL et l'applique ; le Gardien le contrôle avant et après. **Cette délégation ne vaut que pour le Calendrier** : toute autre modification de base reste soumise à l'enseignant.
- **Remise à zéro des comptes** (tous, sauf ceux de Hello GO) : « pas encore » (20/11, 15:10). Le SQL est prêt, il n'est pas appliqué ; elle est irréversible.
- Tables : RLS partout, aucun droit direct d'`anon`, accès par des fonctions `security definer` à `search_path` fixé ; les exceptions sont listées dans les règles.
- **Clés** : une page utilise la clé « publishable » du projet (`sb_publishable_…`), envoyée dans l'en-tête `apikey`, jamais en `Authorization: Bearer` quand on écrit l'appel soi-même (supabase-js s'en charge seul). Les anciennes clés « anon » au format JWT disparaissent fin 2026 (annonce de Supabase, date à confirmer ; T57).
- Les essais d'écriture se font sur une reproduction locale de la base, avec des données inventées : jamais d'essai sur une table d'élèves de la base en ligne.

## 7. Qui possède quoi
| Fichiers | Rôle |
|---|---|
| `CLAUDE.md`, `.claude/agents/` | Chef d'orchestre |
| `README.md`, `CONTRIBUTING.md`, `docs/` (la documentation du README), `LICENSE`, `.github/gardien/`, la fusion dans `main` | Gardien |
| `assets/*.js` (sauf `assets/fiche.js`, `assets/decor.js`, `assets/equipage.js`, `assets/td-en-ligne.js`), `index.html`, `*/index.html`, `reglages.js`, `.nojekyll`, `.gitignore`, `admin/`, `bibliotheque/`, `eleve/`, `enseignant/`, `calendrier/` (sauf le contenu des exercices), `donnees/` (sauf `donnees/ressources/` et `donnees/vitrine.json`), `scripts/`, `.github/workflows/` et `.github/verifier-site.py` (avec l'accord du Gardien) | Architecte |
| `*/ressources.js` (anciennes listes, jusqu'à leur conversion), `donnees/ressources/` (sauf les brouillons des Ateliers), `donnees/vitrine.json`, `<rubrique>/fichiers/` | Bibliothécaire |
| `assets/charte.css`, `assets/style.css`, `assets/fiche.css`, `assets/fiche.js`, `assets/decor.js`, `assets/equipage.js`, `assets/equipage/`, `assets/td-en-ligne.css`, `assets/td-en-ligne.js`, `assets/fonts/`, `assets/favicon.svg`, `charte/`, `design/`, la mise en forme des documents internes | Designer |
| Les fichiers d'une ressource en cours de création (`<rubrique>/fichiers/<nom>/`) et sa fiche en brouillon ; le contenu des exercices du Calendrier des vacances (`calendrier/exercices/<thème>.json`) | l'Atelier chargé de cette ressource |
| `qcm/` (les sources XML des quiz Pronote, leurs aperçus et leurs outils) et les fiches en brouillon de ces quiz | Atelier des quiz |

Le décor du bandeau est encore dans `assets/site.js` (fonction `scene`) : il passera dans `assets/decor.js` quand la charte sera publiée. D'ici là, toute modification du décor est demandée à l'Architecte dans un rapport.

## 8. Vérifier
- Le dossier temporaire de la session est partagé entre les agents : chacun travaille dans **son propre sous-dossier** (par exemple `<dossier temporaire>/<rôle>-<tâche>/`) et ne réécrit jamais le fichier d'un autre.
- `babash.github.io` est inaccessible depuis les sessions. Pour vérifier le site en ligne, on passe par GitHub Actions : le workflow `.github/workflows/verifier.yml` contrôle les liens et le rendu des pages en ligne, et on lit ses résultats avec `gh api repos/babash/Babash-NSI-SNT/actions/runs` (puis les jobs et les logs).
- En local : `python3 -m http.server` à la racine, puis Playwright (Chromium est préinstallé) pour le rendu à 320, 768 et 1440 px, en clair et en obscur.
- Le README est mis à jour à chaque publication.

## 9. Le rapport de fin de tâche
Chaque agent termine par un rapport au chef d'orchestre, dans cet ordre :
1. **Fait** : ce qui a été fait, en quelques lignes.
2. **Branche** : son nom et le dernier commit poussé.
3. **À valider par l'enseignant** : les choix structurels (§ 2), avec les options.
4. **Questions** : ce qui bloque ou reste incertain, en questions fermées de 2 à 4 options courtes (§ 2).
5. **Hors de mon domaine** : les fichiers d'un autre rôle à modifier, et pourquoi.
6. **Reste à faire.**
