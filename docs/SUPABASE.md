# Les bases Supabase

*Les applications du site qui utilisent une base, et le socle commun de la base. Retour au [README](../README.md).*

Deux ressources passent par **Supabase** : Alien Python y enregistre la progression des élèves ;
Court-circuit n'y enregistre rien et n'en utilise que le temps réel.

| Application | Dossier | Projet Supabase | Tables |
|---|---|---|---|
| Alien Python (SNT, Programmation) | `snt/fichiers/alien-python/` | « SNT-1er Jour », la base commune des applications (à renommer « Babash - applications ») | `alien_classes`, `alien_students`, `alien_progress` |
| Court-circuit (SNT, Programmation ; NSI Première, Constructions élémentaires) | `snt/fichiers/court-circuit/` | la même base commune | aucune : seulement les canaux temps réel (diffusion et présence) |

**Alien Python**

- L'adresse du projet et sa clé publique (« anon ») sont dans `config.js`. Cette clé est publique
  par conception : les tables sont verrouillées et le site ne passe que par les fonctions
  `alien_*`, qui vérifient les codes (code enseignant haché).
- N'importe qui connaissant l'adresse peut créer une classe : les classes des collègues
  arrivent dans la même base. Surveille la table `alien_classes` dans Supabase si besoin.
- Ne fais saisir que des prénoms. Pour supprimer un·e élève : Supabase, *Table Editor*.
- Pour ta propre base : colle `supabase.sql` dans *SQL Editor* de ton projet Supabase,
  puis mets son adresse et sa clé « anon public » dans `config.js`.
- Les exercices d'Alien Python sont d'Alien-Python (© 2021 Mathieu Degrange, licence MIT) :
  la notice est dans `snt/fichiers/alien-python/LICENCE.txt`, à garder en cas de copie.

**Court-circuit**

- Rien n'est enregistré en ligne : le duel en direct passe par les canaux temps réel de
  Supabase (diffusion et présence), sans table ni fonction. Le prénom ou le pseudo et le code de
  chaque élève ne vont qu'aux élèves de sa salle, pendant la séance. Seules la page de la salle
  (`prof.html`) et l'entrée d'un·e élève dans une salle se connectent à Supabase ; l'entraînement
  et le défi contre Zéro marchent sans réseau.
- C'est une exception voulue par l'enseignant (10 novembre 2026) aux règles des bases, qui
  n'utilisaient pas le temps réel. La clé de `snt/fichiers/court-circuit/config.js` est la même
  clé publique « anon ».
- Pour ta propre copie : mets l'adresse et la clé « anon public » de ton projet Supabase dans
  `config.js`, ou laisse l'adresse vide : le jeu passe en mode démo, où une salle passe entre
  les onglets d'un même navigateur (comme avec `?demo` à la fin de l'adresse).
- Les codes d'élèves des applications de jeu viendront plus tard : pour l'instant, rien n'est
  gardé en ligne, et les étoiles et le niveau de Zéro restent un jour au plus sur l'appareil.

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
