# Les bases Supabase

*Les applications du site qui utilisent une base, et le socle commun de la base. Retour au [README](../README.md).*

Trois ressources passent par **Supabase** :
- Alien Python y enregistre la progression des élèves ;
- Court-circuit y garde le code élève, les programmes (« Mes codes ») et la liste des challenges
  réussis à l'entraînement des élèves qui le veulent, et passe par son temps réel pour les duels,
  qui ne sont pas enregistrés ;
- QuizzNSI, dans son propre dépôt depuis le 19 novembre 2026, ne passe que par son temps réel,
  pour les séances en classe, qui ne sont pas enregistrées.

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « SNT-1er Jour », la base commune des applications (à renommer « Babash - applications ») | `alien_classes`, `alien_students`, `alien_progress` |
| Court-circuit (SNT, Programmation ; NSI Première, Constructions élémentaires) | `snt/fichiers/court-circuit/` | la même base commune | le schéma `court_circuit` du code élève, depuis le 13 novembre 2026 : `eleves` (avec, depuis le 19 novembre 2026, la liste des challenges réussis) et `programmes` (données d'élèves), `mots` et `menage` ; les duels passent par les canaux temps réel (diffusion et présence), sans table |
| QuizzNSI (NSI Terminale, Structures de données : le cours-quiz « Piles et files ») | le dépôt [babash/QuizzNSI](https://github.com/babash/QuizzNSI) (l'ancien dossier `nsi-terminale/fichiers/quizz-nsi/` redirige vers [babash.github.io/QuizzNSI](https://babash.github.io/QuizzNSI/)) | la même base commune | aucune : les séances passent par les canaux temps réel (diffusion et présence), sans table ni fonction |

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
- Sur l'appareil, le pseudo, le programme en cours, la progression de l'entraînement (les
  challenges réussis et le dernier code de chacun), la vitesse du robot, le niveau de Zéro et le
  jeton de session du code élève restent un jour au plus.

**QuizzNSI**

- **Les séances ne sont pas enregistrées.** La page projetée et les téléphones passent par les
  canaux temps réel de la base commune (diffusion et présence), avec la clé « publishable » de
  son [`config.js`](https://github.com/babash/QuizzNSI/blob/main/config.js), sans aucune table ni
  fonction. L'essai du 19 novembre 2026 sur la vraie base, par GitHub Actions, l'a vérifié : une
  seule connexion, la websocket du temps réel, et aucun appel à une table ou à une fonction. Il a
  été refait le même jour depuis la nouvelle adresse, `https://babash.github.io/QuizzNSI/`.
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
  une demande de l'enseignant (décision P10, à confirmer).
- **Sur l'appareil de l'élève** : le code de séance, le pseudo, l'identifiant et l'historique de la
  séance, pour revenir après une coupure. Ils sont effacés à la fin de la séance, au départ, au
  retrait du pseudo, et sinon au premier chargement d'une page de QuizzNSI après 12 heures.
- Un navigateur qui ne sait pas chiffrer les réponses (page en http, navigateur trop ancien) le
  dit dès l'entrée, et propose le mode autonome, qui marche sans réseau, comme la version
  imprimable.
- Pour ta propre copie : mets l'adresse et la clé publique de ton projet Supabase dans
  `config.js`, ou laisse l'adresse vide pour le mode démo (entre les onglets d'un même navigateur).
  Le [README de QuizzNSI](https://github.com/babash/QuizzNSI#readme) donne le détail.

**Le socle commun de la base (dossier `supabase/`)**

- La base commune porte SNT 1er jour, Expédition Gombessa, Alien Python, Court-circuit (son
  code élève, sa progression et son temps réel) et le temps réel de QuizzNSI. Le dossier `supabase/` du site garde les migrations qui ne
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
    préfixe, `cc_`, pour une table qui serait dans `public`.
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
la progression de Court-circuit, le 19 novembre 2026), et les agents n'en lisent que les
métadonnées, jamais les données des élèves. Ils ne font aucun essai sur une table d'élèves de la
base en ligne : les essais d'écriture se font sur une reproduction locale, avec des données
inventées.
