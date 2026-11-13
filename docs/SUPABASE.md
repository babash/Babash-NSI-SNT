# Les bases Supabase

*Les applications du site qui utilisent une base, et le socle commun de la base. Retour au [README](../README.md).*

Deux ressources passent par **Supabase** : Alien Python y enregistre la progression des élèves ;
Court-circuit y garde le code élève et les programmes des élèves qui le veulent (« Mes codes »), et
passe par son temps réel pour les duels, qui ne sont pas enregistrés.

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « SNT-1er Jour », la base commune des applications (à renommer « Babash - applications ») | `alien_classes`, `alien_students`, `alien_progress` |
| Court-circuit (SNT, Programmation ; NSI Première, Constructions élémentaires) | `snt/fichiers/court-circuit/` | la même base commune | le schéma `court_circuit` du code élève, depuis le 13 novembre 2026 : `eleves` et `programmes` (données d'élèves), `mots` et `menage` ; les duels passent par les canaux temps réel (diffusion et présence), sans table |

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
  ordinateur. Sans code élève, rien n'est enregistré en ligne.
  - **Ce qui est enregistré**, dans le schéma `court_circuit` : le prénom ou le pseudo (2 à
    24 caractères, jamais le nom de famille), le code, un jeton de session, les programmes gardés
    (30 au plus, de 4 000 caractères au plus, avec leur nom) et les dates de création et de
    dernière visite.
  - **L'effacement** : un compte et ses programmes sont effacés 12 mois après la dernière visite.
    Le ménage passe au plus une fois par heure, quand un·e élève crée son code, entre avec lui ou
    ouvre « Mes codes » : si personne ne se sert du code élève pendant un temps, l'effacement
    attend la visite suivante. L'élève peut tout effacer avant, avec « Effacer mes données ».
  - **L'accès** : les tables sont fermées, et la page passe seulement par les six fonctions `cc_`.
    Elles vérifient le jeton (chaque entrée avec le code en tire un nouveau) et comptent les essais
    par réseau : 60 créations de code et 20 codes faux par heure au plus. Dans le jeu, seul·e
    l'élève voit ses programmes, avec son code ; il n'y a pas encore de code enseignant·e.
  - **Pour effacer le compte d'un·e élève** (un nom de famille écrit à la place du pseudo, par
    exemple) : Supabase, *Table Editor*, schéma `court_circuit`, table `eleves` ; ses programmes
    partent avec lui.
  - **Les migrations**, appliquées le 13 novembre 2026 après l'accord de l'enseignant sur le SQL :
    `snt/fichiers/court-circuit/supabase/0001-codes-eleves.sql` (le schéma et les fonctions) et
    `supabase/0005-registre-court-circuit.sql` du site (le registre des tables). Le mode d'emploi
    (vérifier, revenir en arrière) est dans [`snt/fichiers/court-circuit/supabase/LISEZMOI.md`](../snt/fichiers/court-circuit/supabase/LISEZMOI.md).
- Le temps réel des duels est une exception voulue par l'enseignant (10 novembre 2026) aux
  règles des bases, qui ne s'en servaient pas. La clé de `snt/fichiers/court-circuit/config.js`
  est l'ancienne clé publique « anon » de la même base.
- Pour ta propre copie : mets l'adresse et la clé publique de ton projet Supabase dans
  `config.js` (la clé « publishable », ou l'ancienne clé « anon public »), avec `COMPTES: false`
  tant que ta base n'a pas le code élève. Ou laisse l'adresse vide : le jeu passe en mode démo, où
  une salle passe entre les onglets d'un même navigateur (comme avec `?demo` à la fin de
  l'adresse), et où le code élève est imité sur l'appareil (oublié un jour après sa création).
  Pour le vrai code élève : lance `snt/fichiers/court-circuit/supabase/schema.sql` dans
  *SQL Editor*, après le socle commun du site, puis mets `COMPTES: true` dans `config.js`.
- Sur l'appareil, le pseudo, le programme en cours, les étoiles, le niveau de Zéro et le jeton de
  session du code élève restent un jour au plus.

**Le socle commun de la base (dossier `supabase/`)**

- La base commune porte SNT 1er jour, Expédition Gombessa, Alien Python et Court-circuit (son
  code élève et son temps réel). Le dossier `supabase/` du site garde les migrations qui ne
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
SQL exact, et les agents n'en lisent que les métadonnées, jamais les données des élèves. Ils ne
font aucun essai sur une table d'élèves de la base en ligne : les essais d'écriture se font sur
une reproduction locale, avec des données inventées.
