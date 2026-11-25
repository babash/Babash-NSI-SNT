# Les bases Supabase

*Les applications du site qui utilisent une base, et le socle commun de la base. Retour au [README](../README.md).*

Quatre ressources passent par **Supabase** :
- Alien Python y enregistre la progression des élèves ;
- Court-circuit y garde le code élève, les programmes (« Mes codes ») et la liste des challenges
  réussis à l'entraînement des élèves qui le veulent, et passe par son temps réel pour les duels,
  qui ne sont pas enregistrés ;
- QuizzNSI, dans son propre dépôt depuis le 19 novembre 2026, ne passe que par son temps réel,
  pour les séances en classe, qui ne sont pas enregistrées ;
- le Calendrier des vacances, en service depuis le 20 novembre 2026, y garde le compte de l'élève
  (un prénom ou un pseudo, et son code) et ses résultats, case par case.

Depuis le 24 novembre 2026, le **compte commun** du site (pages `eleve/` et `enseignant/`) y garde
aussi ses comptes, ses espaces enseignant·e et ses classes communes (voir plus bas).

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « Babash - applications », la base commune des applications (nommée « SNT-1er Jour » jusqu'au 20 novembre 2026) | `alien_classes`, `alien_students`, `alien_progress` |
| Court-circuit (SNT, Programmation ; NSI Première, Constructions élémentaires) | `snt/fichiers/court-circuit/` | la même base commune | le schéma `court_circuit` du code élève, depuis le 13 novembre 2026 : `eleves` (avec, depuis le 19 novembre 2026, la liste des challenges réussis) et `programmes` (données d'élèves), `mots` et `menage` ; les duels passent par les canaux temps réel (diffusion et présence), sans table |
| QuizzNSI (NSI Première et Terminale : 22 cours-quiz d'introduction depuis le 20 novembre 2026, et 3 quiz de révision, dont « POO, piles, files et rappels » depuis le 24 novembre 2026) | le dépôt [babash/quizz-nsi](https://github.com/babash/quizz-nsi) (l'ancien dossier `nsi-terminale/fichiers/quizz-nsi/` redirige vers [babash.github.io/quizz-nsi](https://babash.github.io/quizz-nsi/)) | la même base commune | aucune : les séances passent par les canaux temps réel (diffusion et présence), sans table ni fonction |
| Calendrier des vacances (NSI et SNT : des thèmes cochés par l'enseignant·e) | `calendrier/` | la même base commune | le schéma `vacances` depuis le 20 novembre 2026 : `eleves`, `inscriptions`, `resultats` et `sessions` (données d'élèves), `enseignants`, `calendriers`, `cases`, `mots` et `menage` |

**Alien Python**

- L'adresse du projet et sa clé publique (une clé « publishable », depuis le 12 novembre 2026)
  sont dans `config.js`. Cette clé est publique par conception : les tables sont verrouillées et
  le site ne passe que par les fonctions `alien_*`, qui vérifient les codes (code enseignant
  haché).
- N'importe qui connaissant l'adresse peut créer une classe : les classes des collègues
  arrivent dans la même base. Surveille la table `alien_classes` dans Supabase si besoin.
- Ne fais saisir que des prénoms. Pour supprimer un·e élève : Supabase, *Table Editor*.
- Pour ta propre base : colle `supabase.sql` dans *SQL Editor* de ton projet Supabase,
  puis mets son adresse et sa clé « publishable » dans `config.js` (l'ancienne clé
  « anon public » marche aussi).
- Les exercices d'Alien Python sont d'Alien-Python (© 2021 Mathieu Degrange, licence MIT) :
  la notice est dans `snt/fichiers/alien-python/LICENCE.txt`, à garder en cas de copie.

**Court-circuit**

- **Les duels ne sont pas enregistrés** : le duel en direct et le mini-championnat passent par les
  canaux temps réel de Supabase (diffusion et présence), sans table ni fonction. Le prénom ou le
  pseudo de chaque élève et le code de son robot ne vont qu'aux élèves de sa salle, pendant la
  séance ; le classement vit tant que la page de la salle est ouverte. L'entraînement et le défi
  contre Zéro marchent sans réseau.
- **Le code élève est en service depuis le 13 novembre 2026, et il est facultatif.** L'élève qui
  veut garder ses programmes en ligne (« Mes codes », règle 21) crée un code de 2 mots et
  3 chiffres (par exemple `PINCE-DIODE-482`), qui suffit pour les retrouver sur n'importe quel
  ordinateur. Depuis le 19 novembre 2026, ce code garde aussi sa progression à l'entraînement
  (les 10 challenges) : un challenge réussi sur un appareil compte partout. Sans code élève, rien
  n'est enregistré en ligne, et la progression reste sur l'appareil.
  - **Ce qui est enregistré**, dans le schéma `court_circuit` : le prénom ou le pseudo (2 à
    24 caractères, jamais le nom de famille), le code, un jeton de session, les programmes gardés
    (30 au plus, de 4 000 caractères au plus, avec leur nom), la liste des challenges et des
    hauts-faits réussis à l'entraînement (depuis le 19 novembre 2026 : leurs identifiants
    seulement, 10 au plus, sans date ni code) et les dates de création et de dernière visite.
  - **L'effacement** : un compte, ses programmes et sa progression sont effacés 12 mois après la
    dernière visite. Le ménage passe au plus une fois par heure, quand un·e élève crée son code,
    entre avec lui ou ouvre « Mes codes » : si personne ne se sert du code élève pendant un temps,
    l'effacement attend la visite suivante. L'élève peut tout effacer avant, avec « Effacer mes
    données ».
  - **L'accès** : les tables sont fermées, et la page passe seulement par les sept fonctions `cc_` :
    `cc_solo`, `cc_connexion`, `cc_reprise`, `cc_enregistrer`, `cc_supprimer`, `cc_effacer_moi`
    et, depuis le 19 novembre 2026, `cc_progression`, qui n'accepte que les identifiants des
    10 challenges et ne retire jamais un challenge réussi. Elles vérifient le jeton (chaque entrée
    avec le code en tire un nouveau) et comptent les essais par réseau : 60 créations de code et
    20 codes faux par heure au plus. Dans le jeu, seul·e l'élève voit ses programmes et sa
    progression, avec son code ; il n'y a pas encore de code enseignant·e.
  - **Pour effacer le compte d'un·e élève** (un nom de famille écrit à la place du pseudo, par
    exemple) : Supabase, *Table Editor*, schéma `court_circuit`, table `eleves` ; ses programmes
    et sa progression partent avec lui.
  - **Les migrations** : `snt/fichiers/court-circuit/supabase/0001-codes-eleves.sql` (le schéma et
    les fonctions) et `supabase/0005-registre-court-circuit.sql` du site (le registre des tables),
    appliquées le 13 novembre 2026 après l'accord de l'enseignant sur le SQL ; puis
    `snt/fichiers/court-circuit/supabase/0002-progression.sql` (la progression : la colonne
    `challenges_reussis` de la table `eleves` et la fonction `cc_progression`), appliquée le
    19 novembre 2026 après la relecture de l'Architecte. Pour cette migration seulement,
    l'enseignant a permis qu'elle soit appliquée sans qu'il valide le SQL. Le Gardien a vérifié la
    base, par ses métadonnées seulement, avant de publier la page qui s'en sert. Le mode d'emploi
    (vérifier, revenir en arrière) est dans [`snt/fichiers/court-circuit/supabase/LISEZMOI.md`](../snt/fichiers/court-circuit/supabase/LISEZMOI.md).
- Le temps réel des duels est une exception voulue par l'enseignant (10 novembre 2026) aux
  règles des bases, qui ne s'en servaient pas. La clé de `snt/fichiers/court-circuit/config.js`
  est l'ancienne clé publique « anon » de la même base.
- Pour ta propre copie : mets l'adresse et la clé publique de ton projet Supabase dans
  `config.js` (la clé « publishable », ou l'ancienne clé « anon public »), avec `COMPTES: false`
  et `PROGRESSION_EN_LIGNE: false` tant que ta base n'a pas le code élève. Ou laisse l'adresse
  vide : le jeu passe en mode démo, où une salle passe entre les onglets d'un même navigateur
  (comme avec `?demo` à la fin de l'adresse), et où le code élève et la progression en ligne sont
  imités sur l'appareil (oubliés un jour après leur création). Pour le vrai code élève : lance
  `snt/fichiers/court-circuit/supabase/schema.sql` dans *SQL Editor*, après le socle commun du
  site, puis mets `COMPTES: true` et `PROGRESSION_EN_LIGNE: true` dans `config.js`.
- Sur l'appareil, la progression de l'entraînement (les challenges réussis et le dernier code de
  chacun) reste 30 jours après le dernier entraînement (décision de l'enseignant du 19 novembre
  2026) ; le pseudo, le programme en cours, la vitesse du robot, le niveau de Zéro et le jeton de
  session du code élève, un jour après leur dernière écriture. Passé ce délai, la page les efface
  du navigateur au premier chargement de Court-circuit sur ce poste (la page des élèves ou celle
  de la salle). Le bouton « Effacer ma progression sur cet appareil », sous la liste des
  challenges de l'entraînement, efface tout cela aussitôt et déconnecte l'appareil du code élève,
  sans rien effacer en ligne.

**QuizzNSI**

- **Les séances ne sont pas enregistrées.** La page projetée et les téléphones passent par les
  canaux temps réel de la base commune (diffusion et présence), avec la clé « publishable » de
  son [`config.js`](https://github.com/babash/quizz-nsi/blob/main/config.js), sans aucune table ni
  fonction. L'essai du 19 novembre 2026 sur la vraie base, par GitHub Actions, l'a vérifié : une
  seule connexion, la websocket du temps réel, et aucun appel à une table ou à une fonction. Il a
  été refait le même jour depuis la nouvelle adresse, `https://babash.github.io/quizz-nsi/`.
- **Ce qui circule** pendant la séance :
  - dans la présence : le prénom ou le pseudo et un identifiant tiré au hasard de chaque élève, et
    la clé publique de la page projetée ;
  - dans la diffusion : ce que montre l'écran projeté (la notion, la question, la bonne réponse, la
    répartition des réponses en nombres, le podium quand il est affiché).
- **Ce qui est protégé** :
  - la réponse de chaque élève part chiffrée pour la page projetée (ECDH P-256 et AES-GCM, dans le
    navigateur) ;
  - les points et la place d'un·e élève ne sont envoyés à personne : chaque téléphone calcule ses
    points, et la page projetée fait foi pour le podium ;
  - chaque message reçu est contrôlé par un schéma strict, et aucune valeur reçue ne passe par du
    HTML.
- **Les risques acceptés** pour une séance de classe sans compte : quiconque connaît le code de
  séance peut ouvrir une fausse page projetée, qui reçoit aussi les réponses (la vraie page le
  signale) ; il peut aussi faire sortir un·e élève, répondre à sa place ou lui afficher de faux
  points ; les bonnes réponses se lisent dans le fichier du cours, public. Le mode temps réel est
  une demande de l'enseignant (décision P10, donnée le 19 novembre 2026, avec ces risques acceptés).
- **Sur l'appareil de l'élève** : le code de séance, le pseudo, l'identifiant et l'historique de la
  séance, pour revenir après une coupure. Ils sont effacés à la fin de la séance, au départ, au
  retrait du pseudo, et sinon au premier chargement d'une page de QuizzNSI après 12 heures.
- **En mode autonome**, rien n'est envoyé. Depuis le 20 novembre 2026, la progression de l'élève
  (ses réponses et la diapositive où il ou elle en est) reste sur l'appareil. Elle est effacée au
  premier chargement d'une page de QuizzNSI plus d'un jour après sa dernière réponse ou son
  dernier changement de diapositive, ou par « Recommencer à zéro » ([les données de QuizzNSI](https://github.com/babash/quizz-nsi/blob/main/docs/DONNEES.md)).
- Un navigateur qui ne sait pas chiffrer les réponses (page en http, navigateur trop ancien) le
  dit dès l'entrée, et propose le mode autonome, qui marche sans réseau, comme la version
  imprimable.
- Pour ta propre copie : mets l'adresse et la clé publique de ton projet Supabase dans
  `config.js`, ou laisse l'adresse vide pour le mode démo (entre les onglets d'un même navigateur).
  Le [README de QuizzNSI](https://github.com/babash/quizz-nsi#readme) donne le détail.

**Le Calendrier des vacances** (dossier `calendrier/`)

- **La base** : le schéma `vacances`, avec 9 tables et 22 fonctions d'entrée `cv_`, créé par la
  migration `vacances_0001_calendrier` (20 novembre 2026, 15:31), puis inscrit au registre des
  tables par `base_unique_0009_registre_vacances` (15:33), toutes deux appliquées sur délégation
  de l'enseignant, limitée au Calendrier. La migration `vacances_0002_index_resultats` (un index,
  sans effacer aucune donnée) est appliquée depuis le 24 novembre 2026 (13:30) : c'est la dernière
  de l'historique des migrations du projet.
- **Ce qui est gardé en ligne** : le prénom ou le pseudo choisi par l'élève (jamais le nom de
  famille), son code et, pour chaque case jouée, le niveau, la réussite, les étoiles, le nombre
  d'essais et de coups de pouce, la durée et la date. Les réponses tapées ne sont jamais
  envoyées. Un compte est effacé au premier usage de l'application après 12 mois sans visite ;
  un calendrier et ses résultats, au premier usage après 12 mois suivant sa fin.
- **Sur l'appareil de l'élève** (le stockage du navigateur) : la session, la partie en cours et
  les résultats pas encore reçus par la base (quand le réseau manque), rattachés à l'élève par
  une empreinte de son code. Un résultat n'est envoyé qu'avec la session de l'élève qui l'a
  produit. Ces données ne sont plus lues après 1 jour, ou 30 jours si l'élève a coché « C'est mon
  téléphone », et elles sont effacées à l'ouverture suivante de la page sur cet appareil.
  « Ce n'est pas moi » ferme la session et ne laisse que les résultats en attente de cet·te
  élève, jusqu'à leur échéance.
- **Effacer** : l'élève, avec « Effacer mes données », en ligne et sur l'appareil ;
  l'enseignant·e, en retirant un·e élève ou en supprimant un calendrier.
- **Aucun classement** : la classe ne voit que des nombres, sans aucun nom, et seulement si
  l'enseignant·e a choisi de les montrer. Chaque élève voit ses propres étoiles, ses cases faites
  et ses jours différents.
- Le détail, les fonctions et les contrôles après application : `calendrier/supabase/LISEZMOI.md`.

**Le compte commun** (pages `eleve/` et `enseignant/`, module `assets/compte-commun.js`)

- **La base** : le schéma `commun` (23 tables, toutes fermées, sans aucune règle d'accès) et
  33 fonctions d'entrée `commun_…`, les seules qu'appelle la page, avec la clé publique
  (« publishable ») du projet. Le SQL (`supabase/0007-compte-commun.sql`, version 2.3, et
  `supabase/0008-enseignants-communs.sql`) a été collé par l'enseignant lui-même dans l'éditeur
  SQL, le 24 novembre 2026 vers 11:20, après un fichier qui retirait une première version collée
  par erreur ; il n'est pas inscrit dans l'historique des migrations du projet (la requête qui l'y
  inscrirait est dans `supabase/LISEZMOI.md`). La base a été comparée aux fichiers, objet par objet.
- **Ce qui est gardé en ligne** : pour l'élève, le prénom ou le pseudo qu'il ou elle choisit (jamais
  le nom de famille), son code (2 mots et 3 chiffres), son avatar, ses classes et ses sessions ;
  pour l'enseignant·e, son nom affiché, son établissement (facultatif) et l'empreinte de son code
  (3 mots et 4 chiffres), jamais le code lui-même ; pour une classe, son nom et son code de 4
  lettres, public. L'XP qu'attribue l'enseignant·e, avec un motif, est gardée dans un journal ;
  l'élève n'en voit que son solde de crédits. Les hauts faits et les objets gagnés ont leurs
  tables, vides tant que leur catalogue et les applications n'y sont pas branchés.
- **Sur l'appareil** : le jeton de session de l'élève, dans l'onglet (1 jour au plus), ou 30 jours
  avec « C'est mon téléphone » ; tous les sites de `babash.github.io` partagent ce stockage, pour
  que les applications reconnaissent l'élève quand elles seront branchées. Le code de l'élève n'y
  est jamais gardé. Le code de l'enseignant·e reste dans la page, ou dans l'onglet avec « Rester
  ouvert dans cet onglet », jamais dans le navigateur.
- **Les essais de code** sont comptés par réseau (une empreinte du jour, jamais l'adresse) : au-delà
  de 20 codes d'élève faux en une heure (10 pour un code d'enseignant·e, 30 pour un code de classe),
  ce réseau attend la fin de l'heure, même avec le bon code ; l'enseignant·e, sur le même réseau,
  le débloque dans « Réglages de mon espace » (« Débloquer le réseau de la salle »).
- **Effacer** : l'élève, avec « Effacer mes données » ; l'enseignant·e retire un·e élève d'une
  classe, supprime une classe ou tout son espace (les comptes des élèves restent). Un compte est
  effacé au premier usage du compte commun après 12 mois sans visite, et une session après 1 jour,
  ou 30 jours sans usage.
- **Pas encore** : aucune application ne lit encore ce compte ; chacune garde ses propres codes.
  Le détail : [docs/COMPTE-COMMUN.md](COMPTE-COMMUN.md) et `supabase/LISEZMOI.md`.

**Le socle commun de la base (dossier `supabase/`)**

- La base commune porte SNT 1er jour, Expédition Gombessa, Alien Python, Court-circuit (son
  code élève, sa progression et son temps réel), le temps réel de QuizzNSI et, depuis le
  19 novembre 2026, Lagon Arena (schéma `lagon`, fonctions `public.lagon_…` ; son dépôt
  [babash/lagon-arena](https://github.com/babash/lagon-arena) garde ses migrations et la page
  publiée l'utilise depuis le 20 novembre 2026), et, depuis le 20 novembre 2026, le Calendrier des
  vacances (schéma `vacances`, fonctions `public.cv_…`) ; elle porte aussi Hello GO (schéma
  `grand_oral`, fonctions `public.go_…`), suivi par une autre session. SNT 1er jour, Gombessa et
  Alien Python ont encore leurs tables dans `public`, sans commentaire. L'ancien projet de Lagon
  Arena garde encore ses tables de Lagon Arena : l'enseignant a approuvé leur retrait (SQL vu le
  20 novembre 2026), qui est à coller par lui-même, sans toucher aux objets `guilde_*`. Le dossier `supabase/` du site garde les migrations qui ne
  relèvent d'aucune application, chacune appliquée après l'accord de l'enseignant sur le SQL :
  `0001` à `0004` (n° 2 du plan de la base unique) le 11 novembre 2026, et `0005` le
  13 novembre 2026 :
  - `0001` ferme les droits par défaut : un objet créé plus tard n'est ouvert à personne sans un
    droit exprès ;
  - `0002` retire à `authenticated` le droit d'appeler les fonctions de `public` (sauf
    `snt_taille_max`, dont se sert une contrainte de SNT 1er jour) et ferme les séquences ; les
    droits d'`anon` ne changent pas ;
  - `0003` crée le schéma `commun` : le compteur des essais de saisie de code (par empreinte du
    réseau, jamais l'adresse), son sel secret, et le registre des tables de toutes les
    applications (dans Supabase : *Table Editor*, schéma `commun`, vue `registre`) ;
  - `0004` retire à `anon` ses droits sur la séquence du Panthéon, dans l'ancien projet de
    Lagon Arena ;
  - `0005` ajoute Court-circuit au registre des tables : son schéma, `court_circuit`, et son
    préfixe, `cc_`, pour une table qui serait dans `public` ;
  - `0009` (le 20 novembre 2026, sur la délégation de l'enseignant pour le Calendrier) ajoute au
    registre le Calendrier des vacances : son schéma, `vacances`, et son préfixe, `cv_`. Sa vue
    reprend celle de `0006` (Hello GO, appliquée le 17 novembre 2026), dont les fichiers ne sont
    pas encore sur `main` ;
  - `0007` (version 2.3) et `0008` créent le compte commun (voir plus haut) : collés par
    l'enseignant dans l'éditeur SQL le 24 novembre 2026, hors de l'historique des migrations,
    après `2026-11-24-retour-avant-socle.sql`, qui a retiré une première version collée par
    erreur. Ses pages, `eleve/` et `enseignant/`, en démonstration depuis le 20 novembre 2026,
    sont branchées sur la base depuis le 24 novembre (`COMPTE_COMMUN_EN_LIGNE: true` dans
    `reglages.js`, avec l'adresse du projet et sa clé publique).
- Chaque migration a son fichier inverse. [`supabase/LISEZMOI.md`](../supabase/LISEZMOI.md) donne l'ordre, les contrôles
  et le retour en arrière. Les migrations d'une application restent dans son propre dépôt.
- Pour ta propre copie : lance `supabase/schema.sql` dans *SQL Editor* d'un projet neuf, avant le
  script d'une application. Il ne se modifie pas à la main : `python3 scripts/supabase_schema.py`
  le fabrique à partir des migrations, et `python3 scripts/supabase_schema.py --verifier` dit
  s'il est à jour.

Les règles communes des bases sont dans `CLAUDE.md`, § 6, « Les bases Supabase » : une seule
base pour toutes les applications, un schéma par application, l'accès par des fonctions, des
migrations avec leur fichier inverse. Aucune base n'est modifiée sans que l'enseignant ait vu le
SQL exact, sauf quand il en donne lui-même la permission pour une migration précise (comme pour
la progression de Court-circuit, le 19 novembre 2026, et pour le Calendrier des vacances, le
20 novembre 2026), et les agents n'en lisent que les
métadonnées, jamais les données des élèves. Ils ne font aucun essai sur une table d'élèves de la
base en ligne : les essais d'écriture se font sur une reproduction locale, avec des données
inventées.

**Comment une migration s'applique aujourd'hui** (constat des 20 et 24 novembre 2026 : l'outil
d'application de la session annule de lui-même toute demande de confirmation de Supabase, et
rien ne tourne) :

1. l'Architecte écrit le fichier (avec `begin;` et `commit;`), son inverse, sa vérification en
   lecture et un résumé exact pour l'enseignant, risques acceptés compris ;
2. un Gardien relit le SQL avant qu'il soit montré à l'enseignant ; un fichier régénéré ensuite
   est comparé à la version relue ;
3. le chef d'orchestre envoie à l'enseignant des fichiers numérotés, dans l'ordre, un par un, et
   l'enseignant colle lui-même chaque fichier, tel quel, dans l'éditeur SQL de Supabase (*SQL
   Editor*, puis *Run*) ;
4. après chaque collage, le chef d'orchestre lance la vérification en lecture, et un Gardien
   contrôle les métadonnées et les conseillers, puis l'inscrit au journal.

Seul un fichier sans instruction à confirmer, comme un simple index, passe par l'outil
(`apply_migration`, au nom du fichier, sans `begin;` ni `commit;`). Un collage ne laisse aucune
trace dans l'historique des migrations du projet : l'y inscrire est une écriture en base, à
montrer aussi à l'enseignant.

**L'état au 25 novembre 2026** (métadonnées lues ce jour-là) : le compte commun (`0007` v2.3 et
`0008`) est en base, sans aucun compte d'élève ni d'enseignant·e ; son catalogue n'a encore que
le margouillat. Relus par un Gardien et pas encore collés, dans cet ordre : Alien Python `0002`
(son schéma `alien`), `0010` (le catalogue, les hauts faits, les trophées), `0012` (le niveau),
`0011` (les séances de QuizzNSI), `vacances_0003` (le Calendrier relié au compte commun), puis
Alien Python `0003` et `0004`. La remise à zéro des comptes (tous, sauf ceux de Hello GO) n'est
pas appliquée : « pas encore » (20 novembre 2026).
