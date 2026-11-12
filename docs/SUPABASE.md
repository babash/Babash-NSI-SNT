# Les bases Supabase

*Les applications du site qui utilisent une base, et le socle commun de la base. Retour au [README](../README.md).*

Deux ressources passent par **Supabase** : Alien Python y enregistre la progression des élèves ;
Court-circuit n'y enregistre rien pour l'instant et n'en utilise que le temps réel (son code
élève est préparé, mais pas encore en service).

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « SNT-1er Jour », la base commune des applications (à renommer « Babash - applications ») | `alien_classes`, `alien_students`, `alien_progress` |
| Court-circuit (SNT, Programmation ; NSI Première, Constructions élémentaires) | `snt/fichiers/court-circuit/` | la même base commune | aucune pour l'instant : seulement les canaux temps réel (diffusion et présence) ; le schéma `court_circuit` du code élève est préparé, pas appliqué |

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

- Rien n'est enregistré en ligne pour l'instant : le duel en direct et le mini-championnat
  passent par les canaux temps réel de Supabase (diffusion et présence), sans table ni fonction.
  Le prénom ou le pseudo et le code de chaque élève ne vont qu'aux élèves de sa salle, pendant la
  séance ; le classement vit tant que la page de la salle est ouverte. Seules la page de la salle
  (`prof.html`) et l'entrée d'un·e élève dans une salle se connectent à Supabase ; l'entraînement
  et le défi contre Zéro marchent sans réseau.
- **Le code élève est préparé, mais pas appliqué** (12 novembre 2026). Pour garder ses
  programmes en ligne (« Mes codes », règle 21), un·e élève recevra un code de 2 mots et
  3 chiffres. La migration `snt/fichiers/court-circuit/supabase/0001-codes-eleves.sql` crée le
  schéma `court_circuit` (le prénom ou le pseudo, le code et les programmes, 30 au plus, effacés
  12 mois après la dernière visite) et les fonctions `cc_`. Elle attend l'accord de l'enseignant
  sur le SQL ; d'ici là, `COMPTES: false` dans `config.js` cache le code élève et « Mes codes », et
  la page n'appelle aucune de ces fonctions. Le registre des tables du socle commun la rangera
  avec la migration `0005` du site, qui attend elle aussi. Le mode d'emploi (appliquer, vérifier,
  revenir en arrière) est dans [`snt/fichiers/court-circuit/supabase/LISEZMOI.md`](../snt/fichiers/court-circuit/supabase/LISEZMOI.md).
- C'est une exception voulue par l'enseignant (10 novembre 2026) aux règles des bases, qui
  n'utilisaient pas le temps réel. La clé de `snt/fichiers/court-circuit/config.js` est
  l'ancienne clé publique « anon » de la même base.
- Pour ta propre copie : mets l'adresse et la clé « anon public » de ton projet Supabase dans
  `config.js`, ou laisse l'adresse vide : le jeu passe en mode démo, où une salle passe entre
  les onglets d'un même navigateur (comme avec `?demo` à la fin de l'adresse), et où le code élève
  est imité sur l'appareil (oublié un jour après sa création). Pour le vrai code élève : lance
  `snt/fichiers/court-circuit/supabase/schema.sql` dans *SQL Editor*, après le socle commun du
  site, puis mets `COMPTES: true` dans `config.js`.
- Sur l'appareil, les étoiles et le niveau de Zéro restent un jour au plus.

**Le socle commun de la base (dossier `supabase/`)**

- La base commune porte SNT 1er jour, Expédition Gombessa, Alien Python et le temps réel de
  Court-circuit. Le dossier `supabase/` du site garde les migrations qui ne relèvent d'aucune
  application (n° 2 du plan de la base unique), appliquées le 11 novembre 2026 après l'accord
  de l'enseignant :
  - `0001` ferme les droits par défaut : un objet créé plus tard n'est ouvert à personne sans un
    droit exprès ;
  - `0002` retire à `authenticated` le droit d'appeler les fonctions de `public` (sauf
    `snt_taille_max`, dont se sert une contrainte de SNT 1er jour) et ferme les séquences ; les
    droits d'`anon` ne changent pas ;
  - `0003` crée le schéma `commun` : le compteur des essais de saisie de code (par empreinte du
    réseau, jamais l'adresse), son sel secret, et le registre des tables de toutes les
    applications (dans Supabase : *Table Editor*, schéma `commun`, vue `registre`) ;
  - `0004` retire à `anon` ses droits sur la séquence du Panthéon, dans l'ancien projet de
    Lagon Arena.
- Chaque migration a son fichier inverse. [`supabase/LISEZMOI.md`](../supabase/LISEZMOI.md) donne l'ordre, les contrôles
  et le retour en arrière. Les migrations d'une application restent dans son propre dépôt.
- Pour ta propre copie : lance `supabase/schema.sql` dans *SQL Editor* d'un projet neuf, avant le
  script d'une application. Il ne se modifie pas à la main : `python3 scripts/supabase_schema.py`
  le fabrique à partir des migrations, et `python3 scripts/supabase_schema.py --verifier` dit
  s'il est à jour.

Les règles communes des bases sont dans `CLAUDE.md`, section « Les bases Supabase » : une seule
base pour toutes les applications, un schéma par application, l'accès par des fonctions, des
migrations avec leur fichier inverse. Aucune base n'est modifiée sans que l'enseignant ait vu le
SQL exact, et les agents n'en lisent que les métadonnées, jamais les données des élèves. Ils ne
font aucun essai sur une table d'élèves de la base en ligne : les essais d'écriture se font sur
une reproduction locale, avec des données inventées.
