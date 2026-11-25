# La base unique : le socle commun

Ce dossier contient les migrations qui ne relèvent d'aucune application : les préalables de la base unique (n° 2 de l'ordre d'ensemble, `architecture/base-unique.md`, § 3) et le schéma `commun`. Les migrations d'une application restent dans son propre dépôt (règle M1).

- **Le projet cible :** `cukahpyqkljiddmimpyi`, nom affiché « SNT-1er Jour », à renommer « Babash - applications ». Il porte SNT 1er jour, Expédition Gombessa, Alien Python et le temps réel de Court-circuit et son schéma `court_circuit` (depuis le 13/11/2026).
- **Une exception :** `0004` vise l'ancien projet de Lagon Arena, `gkyvaugipddjqjvvpopw`. Il n'y touche à aucun objet `guilde_*`.
- **Les règles suivies :** `architecture/regles-supabase.md` (P2, P4, P8 corrigée, M1 à M8) et la spécification des codes, `architecture/codes-acces.md` (§ 1.10).

## Où en est la base (24/11/2026) : le compte commun est en place

**Le compte commun (`0007` v2.3, puis `0008`) est en base depuis le 24/11, vers 11:20 (heure de Mayotte).** L'enseignant a collé lui-même, dans l'éditeur SQL du projet `cukahpyqkljiddmimpyi`, dans cet ordre :

| Fichier collé | md5 du fichier | Ce qu'il a fait |
|---|---|---|
| `2026-11-24-retour-avant-socle.sql` | `70531585ed1af164648b81513dbd4199` | a retiré la **version 1** du compte commun (voir ci-dessous) |
| `0007-compte-commun.sql` (v2.3) | `f4e939976f3dc72bcdb0649b3de12912` | les élèves : comptes, codes (64 mots « pirates »), avatar, hauts faits, XP cachée, crédits |
| `0008-enseignants-communs.sql` | `5e49dbf387d4b9bfb80478b4ab7c61c7` | l'espace commun des enseignant·e·s, les classes communes |

- **Le contrôle du chef d'orchestre** (`verification.sql`, en lecture) : 24 contrôles sur 24 « ok » : 23 tables dans `commun`, 33 fonctions `public.commun_…`, 33 fonctions internes, RLS partout et aucune règle, aucun droit d'`anon` ni d'`authenticated` sur les tables ni sur le schéma, 64 mots, 9 applications, 9 emplacements, le margouillat, 9 barèmes, 0 ligne d'élève ou d'enseignant·e.
- **La preuve de fidélité (T132d)** : la base réelle et une base locale construite avec les fichiers de ce dossier (socle, puis `0007`, puis `0008`) ont été comparées **objet par objet**, par les métadonnées : définition de chaque fonction (`pg_get_functiondef`, fins de ligne normalisées), droits et commentaires des fonctions, colonnes (type, défaut, nullabilité, commentaire), contraintes, index, vue, droits et RLS des tables, commentaires, droits du schéma, contenu des tables de référence (applications, mots, emplacements, éléments, barèmes, hauts faits, récompenses, activités, ménage). **550 objets de chaque côté, 550 identiques.** Le seul écart attendu : sur la base réelle, `service_role` a aussi le droit d'exécuter les 33 fonctions `commun_` (droits par défaut de la plateforme, que `0001` laisse à `service_role`) ; une fois `service_role` mis à part, les droits sont identiques. La requête : `scripts/supabase_empreinte_commun.sql`.
- **Le même jour, à 13:30**, le chef d'orchestre a appliqué `vacances_0002_index_resultats` (`calendrier/supabase/0002-index-resultats.sql`, version 20261124103014) : l'index `vacances.resultats_case`, qui couvre la clé étrangère signalée par le conseiller. Le `schema.sql` du Calendrier le contenait déjà.
- **Rien n'est inscrit dans l'historique des migrations** (collage à la main). La requête qui l'inscrirait est plus bas (« Inscrire le collage à l'historique ») : c'est une écriture en base, à montrer d'abord à l'enseignant.
- **Les conseillers, après le collage** (24/11, 11:28) : « RLS sans règle » (INFO) pour les 23 tables de `commun` et « security definer appelable par anon » (WARN) pour les 33 fonctions `commun_` : attendus. **Nouveaux** : « reg* non pris en charge » (WARN, 7 colonnes `regprocedure` des connecteurs dans `commun.applications`, qui gêneraient un `pg_upgrade`) ; 9 clés étrangères sans index et 9 index pas encore servis (INFO, tables vides). À reprendre dans une prochaine migration (connecteurs en `text` vérifié par `to_regprocedure`, index des clés étrangères).

### Le retour avant le socle (pièce du 24/11)

`2026-11-24-retour-avant-socle.sql` n'est pas une migration à rejouer : c'est la pièce de ce qui a été fait le 24/11. La base contenait alors la **toute première version** du compte commun (`0007` et `0008` du 20/11, commit `a33a640` de la branche `archi/t101-compte-commun`, jamais publiée : ni XP, ni crédits, ni classes), et non la version 2.2 approuvée. Ce fichier a retiré, objet par objet et sans `cascade` : 18 fonctions `public.commun_…`, 22 fonctions internes et 15 tables du schéma `commun` (avec leurs 24 index ; les 7 applications, 64 mots, 17 emplacements et la ligne de ménage partaient avec leurs tables, aucune donnée d'élève). Il a gardé le socle (`0003`, `0009`) : `commun.secret`, `commun.essais`, la vue `commun.registre` et ses 6 fonctions. Il refusait de tourner si une table d'élèves ou d'enseignant·e·s avait une ligne, si un objet inconnu était dans `commun`, ou si un objet d'application dépendait du compte commun. Essayé en local avant d'être collé (base v1 reconstruite, empreinte identique à la base réelle).

## Où en est la base (13/11/2026)

**`0005` est appliqué**, après l'accord de l'enseignant sur le SQL exact (« Ok base Court-circuit », 13/11 à 06:45, heure de Mayotte ; règle M4) : `base_unique_0005_registre_court_circuit`, le 13/11 à 06:49 (version 20261113034900), par le chef d'orchestre, sans les lignes `begin;` et `commit;`, juste après la migration de Court-circuit (`court_circuit_0001_codes_eleves`, 06:48). Le texte enregistré a la même empreinte que le fichier (md5 sans commentaires, espaces ni `;` : `22e6c1b4…`). Vérifié par les métadonnées seulement : la vue lit `court_circuit`, elle reste fermée à `anon` et à `authenticated`, et elle range les 4 tables de Court-circuit (`eleves` et `programmes` : données d'élèves ; `mots` et `menage` : non), sur 15 lignes en tout. Il ne change que la vue `commun.registre` et deux commentaires (voir « 0005 » plus bas).

**Les quatre premières migrations sont appliquées**, après l'accord de l'enseignant (« Ok base 2 », 11/11 à 16:29, heure de Mayotte).
- Le chef d'orchestre les a appliquées par `apply_migration`, sans leurs lignes `begin;` et `commit;`.
- Chaque texte enregistré a la même empreinte que le fichier du commit `cff652e` (le même texte qu'en `88c4cd7` et `d113879`, ses identifiants avant les rebases ; md5 sans commentaires, espaces ni `;`) : **les fichiers `0001` à `0004` de ce dossier sont exactement ceux qui ont été appliqués**, et ne se modifient plus.
- **L'ordre recommandé a été suivi :** l'étape 0 de Gombessa (`gombessa_0001_espaces`, version 20261110161938) était déjà appliquée. Il n'y a donc pas de `0002` à relancer.

| Fichier | Projet | Migration | Version | Heure (Mayotte) |
|---|---|---|---|---|
| `0001` | `cukahpyqkljiddmimpyi` | `base_unique_0001_droits_par_defaut` | 20261111133048 | 11/11, 16:30 |
| `0002` | `cukahpyqkljiddmimpyi` | `base_unique_0002_retrait_authenticated_et_sequences` | 20261111133115 | 11/11, 16:31 |
| `0003` | `cukahpyqkljiddmimpyi` | `base_unique_0003_schema_commun` | 20261111133240 | 11/11, 16:32 |
| `0004` | `gkyvaugipddjqjvvpopw` | `base_unique_0004_ancien_projet_sequence_pantheon` | 20261111133334 | 11/11, 16:33 |

**Les contrôles après l'application**, par les métadonnées seulement :
- **0001 :** les droits par défaut de `postgres` ne donnent plus rien qu'à `postgres` et `service_role`, dans `public` comme pour toutes les fonctions. Ceux du schéma `storage`, qui viennent de la plateforme, sont inchangés.
- **0002, les fonctions :** 33 fonctions de `public` restent appelables par `anon`, comme avant. Pour `authenticated`, il ne reste que `snt_taille_max`, comme prévu.
- **0002, les séquences et les tables :** les deux séquences sont fermées à `anon` et à `authenticated`. Sur les tables, il reste seulement INSERT sur `snt_responses`, pour `anon` et pour `authenticated`.
- **0002, les ajouts sans droit sur les séquences :** les deux séquences sont celles de colonnes d'identité (`pg_depend`, `deptype = 'i'`, ce que vérifie aussi le garde-fou), et Postgres remplit une colonne d'identité sans vérifier de droit sur sa séquence. Les ajouts de Gombessa et de Lagon Arena passent par des fonctions `security definer`, propriété de `postgres`.
- **0003, le schéma commun :** `essais` et `secret` ont la RLS ; `secret` a une ligne et `essais` aucune. Les 6 fonctions ne sont ouvertes à personne, et `anon` n'a pas l'usage du schéma.
- **0003, le registre :** la vue liste 11 tables. La colonne `donnees_eleves` reste vide pour les tables d'application qui n'ont pas encore de commentaire : elles en recevront un à leur déplacement dans leur schéma.
- **0004 :** `anon` n'a plus de droit sur `pantheon_id_seq` ; `authenticated` garde le sien ; les objets `guilde_*` sont intacts. Seules des fonctions `security definer` ajoutent au Panthéon.
- **Les conseillers :** seulement « RLS sans règle » (INFO, 9 tables) et « security definer appelable par anon » (WARN, 31 : les fonctions d'entrée des pages). L'avertissement sur `authenticated` (0029) a disparu.

On ne fait jamais d'essai sur une table de données d'élèves de la base en ligne, même dans une transaction annulée : les essais d'écriture se font sur la reproduction locale, avec des données inventées (voir « L'essai local »).

**Reste à confirmer au premier essai en ligne :** l'en-tête qui donne l'adresse du réseau dans `commun.reseau()`, `cf-connecting-ip` ou, à défaut, le premier élément de `x-forwarded-for`. Aucune application ne se sert encore du compteur ; la première qui s'en servira (SNT 1er jour, `snt_repondre()`, au n° 3) le vérifiera.
- **Le risque :** si l'API ne transmettait aucun des deux en-têtes, l'adresse vaudrait « inconnu » pour tout le monde. Tous les élèves partageraient alors le même compteur.
- **La vérification**, sans lire aucune valeur : après une première réponse envoyée depuis une page, et le même jour, on lance la requête ci-dessous dans l'éditeur SQL. Il n'y a pas d'en-tête : `commun.reseau()` y donne l'empreinte de « inconnu », et on compte les lignes qui la portent.

  ```sql
  -- attendu : 0 (l'empreinte enregistrée vient d'une vraie adresse)
  select count(*) from commun.essais where application = 'snt_premier_jour' and reseau = commun.reseau();
  ```

## Les fichiers

| Fichier | Projet | Nom de migration (`apply_migration`) | Ce qu'il fait |
|---|---|---|---|
| `0001-droits-par-defaut.sql` | cible | `base_unique_0001_droits_par_defaut` | Ferme les droits par défaut : un objet créé plus tard n'est ouvert à personne sans un droit exprès. |
| `0002-retrait-authenticated-et-sequences.sql` | cible | `base_unique_0002_retrait_authenticated_et_sequences` | Retire `authenticated` (et `public`) des fonctions de `public`, et ferme les deux séquences. Les droits d'`anon` ne changent pas. |
| `0003-schema-commun.sql` | cible | `base_unique_0003_schema_commun` | Crée le schéma `commun` : le compteur d'essais, le sel secret, six fonctions internes et le registre des tables. |
| `0004-ancien-projet-sequence-pantheon.sql` | **ancien projet de Lagon Arena** | `base_unique_0004_ancien_projet_sequence_pantheon` | Retire à `anon` ses droits sur `pantheon_id_seq`. |
| `0005-registre-court-circuit.sql` | cible | `base_unique_0005_registre_court_circuit` | Range le schéma `court_circuit` et le préfixe `cc_` dans le registre des tables. |
| `0009-registre-vacances.sql` (et son inverse) | cible | `base_unique_0009_registre_vacances` | Range le schéma `vacances` et le préfixe `cv_` (Calendrier des vacances, T105) dans le registre. Il reprend la vue de `0006` (Hello GO, appliquée le 17/11 ; ses fichiers sont sur la branche `gardien/t73-registre`). Les numéros `0007` et `0008` sont pris par le compte commun (T101), qui ne touche pas au registre. **Appliqué le 20/11 (15:33).** Mode d'emploi : `calendrier/supabase/LISEZMOI.md`. Le `schema.sql` du socle le contient depuis T132d (le 24/11). |
| `0007-compte-commun.sql` (v2.3, et son inverse) | cible | `base_unique_0007_compte_commun` | Le compte commun des élèves : 16 tables, 19 fonctions internes, 12 fonctions `commun_` pour `anon`. **En base depuis le 24/11** (collé à la main). L'inverse refuse si `0008` est là, ou si une application s'est branchée. |
| `0008-enseignants-communs.sql` (et son inverse) | cible | `base_unique_0008_enseignants_communs` | L'espace commun des enseignant·e·s (code de 3 mots et 4 chiffres, gardé en empreinte), les classes communes (code de 4 lettres, lien, QR code) : 5 tables, 8 fonctions internes, 21 fonctions `commun_`. **En base depuis le 24/11.** Inverse : avant celui de `0007`. |
| `2026-11-24-retour-avant-socle.sql` | cible | (aucun : pièce du 24/11) | Retrait de la version 1 du compte commun avant `0007` v2.3 (voir plus haut). Ne se relance pas : il s'arrête sans rien modifier sur la base d'aujourd'hui. |
| `0013-retours-eleves.sql` (son inverse et sa vérification) | cible | `base_unique_0013_retours_eleves` | Les avis anonymes des élèves à la fin d'une ressource en ligne (T163) : 1 table, 3 fonctions internes, 4 fonctions `commun_` pour `anon`. **Proposé, pas collé** (voir « 0013 » plus bas). Suppose `0007` et `0008` ; indépendant de `0010`, `0011` et `0012`. Inverse : avant celui de `0008`. |
| `NNNN-…-inverse.sql` | le même | `…_inverse` | Le SQL inverse de chaque migration. |
| `schema.sql` | un projet neuf | — | Le script complet du socle (0001, 0003, 0005, 0009, puis le compte commun 0007 et 0008, et les avis des élèves 0013), pour la copie d'un·e collègue. Fabriqué par `scripts/supabase_schema.py`. |

Chaque fichier commence par `begin;` et finit par `commit;`, chacun sur sa ligne. Il se colle d'un bloc dans l'éditeur SQL. Par `apply_migration`, on retire seulement ces deux lignes : le reste est appliqué tel quel.

## L'ordre

1. **Recommandé : après l'étape 0 de Gombessa** (n° 1 du plan, `0001-espaces.sql` du dépôt `gombessa`, ex-`Rappel-1er`).
   - Si le n° 2 passe avant l'étape 0, tout marche aussi, mais l'étape 0 redonne le droit à `authenticated` sur ses 25 fonctions (elle les ouvre « à anon, authenticated »).
   - Il suffit alors de relancer `0002` juste après l'étape 0, sous le nom `base_unique_0002_retrait_authenticated_et_sequences_bis`. Le fichier se relance sans risque.
2. **Puis `0001`, `0002` et `0003`, dans cet ordre.** Chacun passe aussi seul.
3. **`0004`, quand on veut**, sur l'autre projet.
4. **`0005`, quand on veut, avant ou après la migration de Court-circuit** (`court_circuit_0001_codes_eleves`, dossier `snt/fichiers/court-circuit/supabase/`). Tant que le schéma `court_circuit` n'existe pas, le registre donne les mêmes lignes qu'avant.

**Aucune page n'est touchée, et il n'y a aucune interruption.** Aucune ligne n'est modifiée : l'export des tables (règle M8) n'est pas nécessaire.

## Ce que fait chaque fichier

### 0001 : les droits par défaut (règle P8, forme corrigée)

- **Il modifie** seulement les droits par défaut du rôle `postgres` (`pg_default_acl`) :
  - dans `public`, `anon` et `authenticated` ne reçoivent plus rien sur les nouvelles tables (MAINTAIN compris, nouveau dans Postgres 17), séquences et fonctions ;
  - dans tous les schémas, `public` ne reçoit plus le droit d'exécution des nouvelles fonctions. Ce droit est global : la ligne n'a pas de `in schema`.
- **Il ne change** aucun objet existant. `postgres` et `service_role` gardent leurs droits par défaut. Ceux du rôle `supabase_admin` (la plateforme) restent : `postgres` ne peut pas les changer.
- **La conséquence pour les migrations suivantes :** une nouvelle fonction d'entrée doit recevoir `grant execute on function public.<app>_…(…) to anon;` dans sa migration. Sinon, la page reçoit « permission denied for function ». C'est voulu (règle P4).
- **Une correction de la règle P8 :** le texte de la règle énumère les droits des tables sans MAINTAIN. Le fichier écrit `revoke all`, qui le comprend.

### 0002 : authenticated retiré, séquences fermées (règles P2 et P4)

- **Les séquences :** `public.gb_evenements_id_seq` et `public.snt_responses_id_seq` perdent tout droit pour `anon` et `authenticated`.
  - Ce sont les séquences de deux colonnes d'identité : Postgres les remplit sans vérifier de droit, et l'essai local le confirme (ajout d'une réponse de SNT 1er jour en `anon`, journal de Gombessa).
  - Le garde-fou s'arrête si l'une n'est pas une séquence d'identité.
- **Les fonctions de `public` qui appartiennent à `postgres` :**
  - chaque fonction qu'`anon` peut appeler reçoit d'abord un droit exprès pour `anon`, qu'il avait déjà ;
  - puis `authenticated` et `public` perdent le droit d'exécution ;
  - un contrôle, fonction par fonction, arrête tout si le droit d'`anon` a bougé ou si `authenticated` peut encore appeler la fonction.
- **Combien :** 28 fonctions perdent le droit d'`authenticated` avant l'étape 0 de Gombessa, 32 après. Les 6 fonctions d'Alien Python perdent aussi celui de `public`.
- **Ce qui reste, et pourquoi :**
  - les fonctions d'une extension ;
  - les fonctions dont une table se sert (contrainte, valeur par défaut, index, règle d'accès, vue), qui s'exécutent avec les droits de qui écrit. Aujourd'hui, c'est seulement `public.snt_taille_max`, la contrainte de taille des mots-clés de SNT 1er jour. Elle part avec sa table au n° 3 ;
  - le droit d'ajout d'`authenticated` sur `public.snt_responses` et la règle « Ajout d'une réponse » : c'est l'état accepté avec T36. Ils disparaissent au n° 3 (déplacement de SNT 1er jour).

### 0003 : le schéma commun (spécification des codes, § 1.10)

**Il crée, et ne modifie rien d'autre :**

| Objet | Ce que c'est |
|---|---|
| schéma `commun` | Ce qui sert à toutes les applications. Il n'est pas exposé à l'API, et `anon` comme `authenticated` n'y ont aucun droit. |
| table `commun.secret` | Une ligne : un sel de 32 octets, tiré une fois au hasard. **Ne se lit jamais** : ni par un agent, ni dans un message. On compte ses lignes, sans plus. |
| table `commun.essais` | Les échecs de saisie de code, par application, réseau, type (`eleve`, `enseignant`, `classe`, `creation`) et heure. Le réseau est une empreinte, jamais l'adresse. Les lignes de plus de 24 h sont effacées. |
| `commun.reseau()` | L'empreinte du réseau de la requête : SHA-256 de l'adresse (`cf-connecting-ip`, sinon le premier élément de `x-forwarded-for`), du sel et de la date du jour (UTC). Sans en-tête, par exemple dans l'éditeur SQL, l'adresse vaut « inconnu ». L'en-tête est à confirmer au premier essai en ligne. |
| `commun.essai_permis(app, type, max)` | Vrai si ce réseau a fait moins de `max` échecs de ce type dans l'heure. |
| `commun.noter_echec(app, type)` | Compte un échec (ou une création), fait le ménage des compteurs de plus de 24 h, et renvoie le nombre de l'heure. |
| `commun.debloquer_reseau(app)` | Remet à zéro les compteurs de ce réseau pour une application : c'est « débloquer le réseau » depuis l'espace enseignant·e. |
| `commun.echecs_heure(app)` | Le nombre d'échecs de l'heure dans une application, tous réseaux confondus, sans les créations : au-delà de 200, l'alarme. |
| `commun.menage_essais()` | Efface les compteurs de plus de 24 h. |
| vue `commun.registre` | La liste des tables de toutes les applications, avec leur description, l'indication « données d'élèves » et un nombre de lignes approché. Une table encore dans `public` est rangée selon son préfixe. |

- **Les fonctions internes :** toutes `security definer`, avec `set search_path = ''` et des noms complets. Personne n'a le droit de les appeler, sauf leur propriétaire `postgres`. Les fonctions d'entrée des applications, qui appartiennent aussi à `postgres`, s'en servent.
- **Les commentaires :** tout a son commentaire, que le tableau de bord affiche. Le contrôle c4 ne trouve rien à redire.
- **Un contrôle à la fin** arrête tout si quelque chose est ouvert à `anon` ou à `authenticated`, si une table n'a pas la RLS, ou si le sel n'a pas exactement une ligne.
- **Le fichier peut être relancé :** il ne crée que ce qui manque, et ne tire jamais un second sel.
- **Le registre dans le tableau de bord :** Table Editor, le schéma `commun`, puis `registre`.

### 0004 : l'ancien projet de Lagon Arena

- **Il retire** `usage`, `select` et `update` à `anon` sur `public.pantheon_id_seq`, la séquence de la colonne d'identité du Panthéon.
- **Rien d'autre ne change** : aucun objet `guilde_*`, aucune table, aucune fonction, aucun droit par défaut.
- **Ce qui reste :** les droits d'`authenticated` sur cette séquence, parce que la consigne de T42 se limite à `anon` pour ce projet.

### 0005 : Court-circuit dans le registre (12/11)

- **Pourquoi :** Court-circuit prend le schéma `court_circuit` et le préfixe `cc_` (inscrits au registre des applications, `architecture/regles-supabase.md`, § 2). La vue `commun.registre` de `0003` ne lit que les schémas qu'elle nomme : sans `0005`, les tables de Court-circuit n'y apparaîtraient pas.
- **Il modifie** seulement :
  - la vue `commun.registre` (`create or replace view`) : `court_circuit` dans la liste des schémas, et `cc_` → `court_circuit` pour une table encore dans `public`. Les colonnes, leur ordre, `security_invoker`, le propriétaire, les droits et le commentaire de la vue ne changent pas ;
  - deux commentaires de colonne, qui nomment maintenant Court-circuit : `commun.registre.application` et `commun.essais.application`.
- **Il ne change** aucune table, aucune ligne, aucune fonction, aucun droit, aucune page.
- **Un contrôle à la fin** arrête tout si la vue s'ouvre à `anon` ou à `authenticated`, si elle perd `security_invoker`, ou si une table de `court_circuit` n'y est pas rangée.
- **L'inverse** rend la vue et les deux commentaires exactement comme `0003` les a créés. Il n'efface rien : les tables de Court-circuit restent, simplement absentes du registre.
- **Pour la prochaine application :** la même petite migration, avec son schéma et son préfixe (voir « Pour une application » plus bas).

### 0013 : les avis anonymes des élèves (T163, 25/11, proposé)

**La demande de l'enseignant (25/11)** : à la fin d'une ressource en ligne, des « petits trucs » rapides et le plus anonymes possible (« ce que j'en ai pensé », des étoiles), pour voir « ce qui marche en pratique ». Il l'a permis sans autorisation pour la page ; le SQL reste soumis à la règle M4 (il voit le fichier avant de le coller).

**Ce que voit l'élève** (`assets/retour-eleve.js`, activé par `<section data-retour="<id de la fiche>">`, éteint tant que `RETOURS_ELEVES` vaut `false` dans `reglages.js`) : « Ça t'a plu ? » (1 à 5 étoiles), « C'était… » (trop facile, bien pour moi, trop dur), « J'ai compris ? » (oui, à peu près, non), « J'ai fini ? » (oui, presque, non) ; repliés, des remarques à cocher (consignes pas claires, trop de texte à lire, il me faut plus d'exemples, quelque chose ne marchait pas, pas pratique sur téléphone, j'en veux d'autres comme ça) et, **seulement avec le lien de la classe**, un mot de 140 caractères pour l'enseignant·e. Tout est facultatif ; un avis par appareil et par ressource, modifiable ou retirable pendant la semaine ; « Un·e autre élève sur cet appareil ? » pour les postes partagés.

**Ce qui est gardé** (table `commun.retours`), colonne par colonne :

| Colonne | Ce que c'est |
|---|---|
| `id` | tiré au hasard ; sert seulement à effacer un mot |
| `ressource`, `partie` | l'identifiant de la fiche (ou `sequence:<id>`), et la feuille de TD (`data-td`) |
| `classe_id` | la classe commune dont le lien portait le code (`?classe=ABCD`), sinon vide ; vidé si la classe est supprimée |
| `semaine` | le lundi de la semaine (heure de Mayotte) : **aucune heure, aucune date plus fine** |
| `plu`, `difficulte`, `compris`, `fini`, `remarques` | les réponses, valeurs d'une liste fermée |
| `mot` | le mot libre (140 caractères, ni adresse, ni lien, ni numéro), seulement avec une classe |
| `cle_empreinte` | l'empreinte de la clé tirée au hasard par l'appareil pour cette ressource ; **effacée dès la semaine finie** |
| `lot_classe`, `lot_tous` | le paquet où l'avis est montré, une fois publié |

**Ce qui n'est jamais gardé** : ni compte, ni code, ni pseudo, ni jeton du compte commun (la page ne le lit pas), ni adresse IP, ni heure. Le plafond par réseau passe par `commun.essais` (application `retours`, empreinte du réseau qui change chaque jour, effacée après 24 h, sans lien avec l'avis).

**L'anonymat, même pour l'enseignant·e** : rien de la semaine en cours n'est montré ; les avis d'une semaine finie sont publiés **par paquets d'au moins 5** (par classe et ressource ; et par ressource pour « tout le monde ») ; un paquet publié ne change plus, ce qui reste sous 5 attend les semaines suivantes. Ainsi aucune différence entre deux lectures ne porte sur moins de 5 avis. Les mots sont rendus dans un ordre mélangé, et seulement à l'enseignant·e de la classe ; la vue « tout le monde » n'a aucun mot.

**Limites assumées** : un mot peut se reconnaître à son contenu ou à son style (d'où le rappel « n'écris aucun nom » et l'effacement par l'enseignant·e) ; les journaux techniques de Supabase (adresse et heure de chaque appel, gardés 1 jour sur l'offre gratuite) ne contiennent pas le contenu des avis, mais l'administrateur·rice du projet qui les fouillerait le jour même pourrait rapprocher un appel d'avis d'un autre appel du même réseau ; un appareil peut donner un avis par semaine et par ressource (la clé est oubliée de la base à la fin de la semaine) : la page, elle, ne repropose rien après un envoi, sauf « Un·e autre élève sur cet appareil ? ».

**Contre les abus** : 300 envois par heure et par réseau (une classe de 35 derrière la même box passe largement), 1 500 avis par ressource et par semaine, 20 000 par semaine, 300 000 en tout ; 30 codes de classe inconnus par heure et par réseau. Au-delà, l'avis attend sur l'appareil, sans message inquiétant.

**Effacement** : chaque avis part deux ans après sa semaine (au ménage que fait chaque lecture de l'enseignant·e) ; l'élève retire le sien pendant la semaine ; l'enseignant·e efface un mot ; une classe supprimée laisse ses avis à « tout le monde » et efface ses mots.

**Les fonctions** (anon seul, `security definer`, `search_path` vide) : `commun_retour_donner(p_cle, p_ressource, p_partie, p_classe, p_plu, p_difficulte, p_compris, p_fini, p_remarques, p_mot)`, `commun_retour_effacer(p_cle)`, `commun_prof_retours(p_code, p_classe)` (une classe, ou `null` pour tout le monde), `commun_prof_retour_effacer_mot(p_code, p_retour)`. L'espace enseignant·e (`enseignant/`) montre les répartitions, l'évolution paquet par paquet, les remarques et les mots, et exporte en CSV ou JSON (sans les mots) ; il fabrique aussi le lien d'une ressource pour la classe (`…?classe=ABCD`, avec son QR code).

**Après le collage** : `0013-retours-eleves-verification.sql` (lecture seule, 16 contrôles « ok »), puis `RETOURS_ELEVES: true` dans `reglages.js` (publication de la page). Pour couper sans rien effacer : `RETOURS_ELEVES: false`. Retour en arrière : `0013-retours-eleves-inverse.sql`, qui s'arrête s'il reste des avis (les exporter, puis `delete from commun.retours;` si l'enseignant le décide), et qui passe **avant** l'inverse de `0008` (sinon celui-ci s'arrête sur une erreur de dépendance, sans rien modifier).

**Essayé** sur une base locale Postgres 17.11 reconstruite comme la base réelle du 25/11 (socle, `0007`, `0008`) : 60 essais SQL (`scripts/tests/retours_eleves.sql`), 23 essais de la page avec la base imitée, et `scripts/tests/test_retours_eleves.py` pour le parcours de bout en bout dans le navigateur, 22 contrôles) ; `0013` passe avant et après `0010`, `0012`, `0011` ; relancé, il s'arrête ; sans `0008`, il s'arrête ; l'inverse refuse tant qu'il reste des avis, puis retire tout, et `0013` se réapplique.

## Avant

*Cette section et la suivante décrivent la marche suivie le 11/11 ; elles restent comme modèle pour une relance ou pour une copie.*

1. **L'enseignant lit le SQL exact** des quatre fichiers et donne son accord.
2. Rien d'autre : aucune donnée n'est modifiée.

## Appliquer

1. **Le chef d'orchestre** applique chaque fichier avec `apply_migration` : le bon projet, le nom de migration du tableau, et le contenu du fichier sans sa première ligne (`begin;`) ni sa dernière (`commit;`).
2. **Supabase demande une confirmation** avant d'appliquer : l'enseignant l'accepte.
3. **Une ligne va au journal** : date, projet, migration, résultat de la vérification (règle M5).

Dans l'éditeur SQL de Supabase, on colle le fichier tel quel, puis Run.

## Vérifier (métadonnées seulement)

Les requêtes du § 6 des règles. Les résultats attendus, après `0001` à `0003` sur le projet cible :

| Requête | Attendu |
|---|---|
| a. tables sans RLS | aucune |
| b. règles d'accès | une seule : « Ajout d'une réponse » sur `public.snt_responses` |
| c. droits directs | seulement INSERT sur `public.snt_responses`, pour `anon` et `authenticated` |
| c2. séquences | aucune ouverte à `anon` ni à `authenticated` |
| c3. schémas des applications | `commun` : `false` (les autres schémas n'existent pas encore) |
| c4. commentaires | aucune table ni colonne sans commentaire |
| d. fonctions appelables par `anon` | **inchangées** : 29 avant l'étape 0 de Gombessa, 33 après |
| f. droits par défaut de `public` | plus rien pour `anon` ni `authenticated` |

**Pour le schéma commun :**

```sql
-- le sel existe, sans le lire (attendu : 1)
select count(*) from commun.secret;
-- personne d'autre que postgres ne peut appeler une fonction de commun (attendu : 0)
select count(*) from pg_proc p where p.pronamespace = 'commun'::regnamespace
  and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute')
       or exists (select 1 from aclexplode(p.proacl) a where a.grantee = 0));
```

**Pour 0005** (attendu : `true`, `true`, puis 4 lignes `court_circuit` une fois la migration de Court-circuit appliquée, 0 avant) :

```sql
select pg_get_viewdef('commun.registre') like '%court_circuit%' as schema_lu,
       not has_table_privilege('anon', 'commun.registre', 'select') as ferme;
select application, schema_nom, table_nom, donnees_eleves from commun.registre where application = 'court_circuit';
```

**Pour 0004, sur l'autre projet** (attendu : `false`) :

```sql
select has_sequence_privilege('anon', 'public.pantheon_id_seq', 'usage, select, update');
```

**Les conseillers (`get_advisors`) :**
- 0029 (fonction `security definer` appelable par `authenticated`) disparaît ;
- 0028 reste pour les fonctions d'entrée des pages : 27 avant l'étape 0 de Gombessa, 31 après ;
- 0008 (RLS sans règle) compte `commun.essais` et `commun.secret` en plus : c'est voulu ;
- aucun 0010 : la vue `commun.registre` est `security_invoker`.

## Les fonctions des pages, qui restent appelables par anon (règle M7)

| Page | Ce qu'elle appelle | Après le n° 2 |
|---|---|---|
| SNT 1er jour (`SNT-1er-Jour`, `7242eb7`) | `snt_nuage()`, et l'ajout direct dans `snt_responses`, qui passe par la contrainte `snt_taille_max` | inchangé |
| Expédition Gombessa (`Rappel-1er`, `646c38a`), après l'étape 0 | `gb_classe_par_code`, `gb_connexion`, `gb_equipage`, `gb_inscription`, `gb_journal`, `gb_presence`, `gb_prof_classes`, `gb_prof_creer_classe`, `gb_prof_creer_espace`, `gb_prof_eleves`, `gb_prof_evenements`, `gb_prof_flux`, `gb_prof_modifier_classe`, `gb_prof_modifier_espace`, `gb_prof_nouveau_code`, `gb_prof_nouveau_code_classe`, `gb_prof_nouvelle_cle`, `gb_prof_ouvrir`, `gb_prof_renommer_eleve`, `gb_prof_supprimer_classe`, `gb_prof_supprimer_eleve`, `gb_prof_supprimer_espace`, `gb_reprise`, `gb_sauvegarde` (24) | les 24 restent appelables |
| Alien Python (`snt/fichiers/alien-python/`) | `alien_class_view`, `alien_create_class`, `alien_join_class`, `alien_save_progress`, `alien_student_login`, `alien_teacher_overview` | inchangé |
| Lagon Arena (`lagon-arena`, `c3d8acd`), ancien projet | 26 fonctions, dont `pantheon_classe`, et la lecture directe de `salles`, `joueurs`, `tortues` et `scores`. La migration du Panthéon automatique est appliquée depuis le 10/11 à 23:09 (`lagon_0001_pantheon_automatique`, version 20261110200903) : `pantheon_classe` est en ligne, `security definer`, appelable par `anon` (métadonnées du 11/11). | inchangé : les 26 restent appelables par `anon` |

Le contrôle, nom par nom (attendu : `true` partout) :

```sql
select f, exists (select 1 from pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname = f
                  and has_function_privilege('anon', p.oid, 'execute')) as appelable
from unnest(array['snt_nuage', 'alien_join_class', 'gb_connexion' /* … la liste du tableau */]) f;
```

## Revenir en arrière

- **Dans l'ordre inverse :** `0005-…-inverse.sql`, `0003-schema-commun-inverse.sql`, puis `0002-…-inverse.sql`, puis `0001-…-inverse.sql`. Chacun passe aussi seul : `0003-…-inverse.sql` supprime la vue, il n'a pas besoin de `0005-…-inverse.sql` avant lui. Pour l'autre projet : `0004-…-inverse.sql`.
- **`0005-registre-court-circuit-inverse.sql` n'efface rien** : il rend la vue de `0003`.
- **`0003-schema-commun-inverse.sql` efface le sel et les compteurs d'essais.** Ce ne sont pas des données d'élèves : les compteurs repartent de zéro.
  - Il s'arrête, sans rien modifier, si le schéma contient un objet d'une autre migration, ou si une fonction d'application se sert déjà de `commun`. Il faut alors d'abord défaire la migration de cette application.
- **Les inverses rendent exactement l'état d'avant :** métadonnées, droits d'`anon` et d'`authenticated`, droits par défaut (voir l'essai local).

## Le script complet `schema.sql` (règle M2)

- **Pour qui :** un·e collègue qui installe sa copie. On le lance dans un projet neuf, avant le script complet d'une application.
- **Ce qu'il contient :** le texte de `0001`, de `0003` et de `0005` (parties A, B et C), sans le contrôle du projet de l'enseignant ; pour `0005`, sans son garde-fou, puisque celui de `0003`, en tête, vérifie déjà le rôle et l'origine du registre. La vue est donc créée par B, puis remplacée par C, dans la même transaction. `0002` n'y est pas : il corrige des objets qui existaient déjà.
- **Il ne se modifie pas à la main :**
  - on le fabrique avec `python3 scripts/supabase_schema.py` ;
  - `python3 scripts/supabase_schema.py --verifier` dit s'il est à jour ;
  - il change dans le même commit que les migrations.

## Pour une application : se servir du compteur

Une fonction d'entrée qui vérifie un code (spécification des codes, § 1.10) :
- elle est `security definer`, appartient à `postgres` et a `set search_path = ''` ;
- elle ne lève pas d'exception sur un échec, qui annulerait le compteur : elle répond `{ "ok": false }`.

```sql
if not commun.essai_permis('gombessa', 'eleve', 20) then
  return json_build_object('ok', false, 'message',
    'Trop d''essais depuis ce réseau. Attends un peu, ou demande ton code à ton enseignant·e.');
end if;
select … into e from gombessa.eleves where code = v_code;
if not found then
  perform commun.noter_echec('gombessa', 'eleve');
  return json_build_object('ok', false, 'message', 'Code inconnu.');
end if;
```

- **Les seuils, par heure et par réseau :** 20 pour un code d'élève, 10 pour un code d'enseignant·e, 30 pour un code de classe, 60 créations.
- **Débloquer le réseau :** la fonction `<app>_prof_debloquer_reseau(code)` vérifie le code de l'enseignant·e, puis appelle `commun.debloquer_reseau('<app>')`.
- **L'alarme :** l'espace enseignant·e affiche un bandeau si `commun.echecs_heure('<app>')` dépasse 200.
- **Ne jamais** faire `grant usage on schema commun`, ni donner un droit sur un objet de `commun`.
- **Le registre :** une nouvelle application, inscrite au registre des applications (préfixe, schéma, liste de mots), demande une petite migration du socle, sur le modèle de `0005`, pour que `commun.registre` lise son schéma et son préfixe.

## Ce que fait l'enseignant

1. **Lire et accepter le SQL** des quatre fichiers : fait le 11/11 à 16:29.
2. **Accepter la confirmation de Supabase** au moment où le chef d'orchestre applique : fait le 11/11.
3. **Renommer le projet, quand il veut :** dans le tableau de bord, Project Settings, puis General, puis Project name : « Babash - applications », puis Save. L'adresse et l'identifiant du projet ne changent pas : aucune page n'est touchée.

## L'essai local (10/11/2026)

- **Sur un PostgreSQL 17.11, comme en ligne**, avec les rôles et les droits par défaut de Supabase et le chemin de recherche relevé en ligne.
- **Les deux projets reproduits :**
  - structure, fonctions (avec leur code), droits, règles et droits par défaut, à partir des scripts des dépôts, complétés par les métadonnées en ligne ;
  - l'empreinte des métadonnées locales est identique à celle relevée en ligne, catégorie par catégorie ;
  - aucune donnée réelle : les données sont inventées et ajoutées en `anon`, comme les pages.
- **Les essais :**
  - application dans les deux ordres avec l'étape 0 de Gombessa, comme dans l'éditeur SQL et comme `apply_migration` ;
  - contrôles des règles et des droits, scénario de chaque page en `anon`, scénario du schéma commun ;
  - relance sans effet ;
  - inverses : retour exact à l'état d'avant ;
  - nouvelle application ;
  - garde-fous : mauvais projet, mauvais rôle, schéma `commun` venu d'ailleurs, retour refusé quand une application se sert de `commun` ;
  - `schema.sql` dans un projet neuf : le même socle que les migrations.
- **Le résultat :** 343 contrôles, 0 échec.

## L'essai local de 0005 (12/11/2026)

- **Sur un PostgreSQL 16 local**, avec les rôles de Supabase (`anon`, `authenticated`, `service_role`), `pgcrypto` dans `extensions`, `0001` et `0003` appliqués, et des données inventées. Pour Postgres 16, qui ne connaît pas le droit MAINTAIN, le mot est retiré de la copie d'essai seulement.
- **Les essais :**
  - `0005` avant, puis après la migration de Court-circuit : les 4 tables de `court_circuit` sont rangées (avec « données d'élèves » oui ou non), une table `cc_…` de `public` aussi, et les autres lignes ne changent pas ;
  - la vue reste fermée à `anon` et à `authenticated`, `security_invoker`, avec le même propriétaire, les mêmes droits et le même commentaire ;
  - relance sans effet ; l'inverse rend exactement la vue et les commentaires de `0003`, et se relance ; `0003-schema-commun-inverse.sql` marche encore après `0005` ;
  - garde-fous : mauvais rôle, mauvais projet, registre venu d'ailleurs, `0003` absent ;
  - `schema.sql` dans un projet neuf : le même registre et les mêmes droits que `0001`, `0003` et `0005` ; puis le script complet de Court-circuit et son scénario en `anon`.
- **Le résultat :** 34 contrôles, 0 échec, et 78 pour le scénario de Court-circuit.

## Inscrire le collage à l'historique (proposition, non exécutée)

Le collage du 24/11 n'a laissé aucune trace dans `supabase_migrations.schema_migrations`. Cette requête l'y inscrirait, **sans rien rejouer** : c'est une écriture en base, à montrer à l'enseignant avant que le chef d'orchestre ne la lance (`execute_sql`). Les versions sont l'heure du collage (11:20 à Mayotte, 08:20 UTC) ; le texte enregistré est une note qui renvoie au fichier et à son md5, pas le fichier lui-même.

```sql
insert into supabase_migrations.schema_migrations (version, name, statements, created_by)
values
  ('20261124082000', 'base_unique_0007_0008_retour_version_1',
   array['-- Collé à la main le 24/11/2026 dans l''éditeur SQL : supabase/2026-11-24-retour-avant-socle.sql du dépôt du site, md5 70531585ed1af164648b81513dbd4199.'],
   'enseignant (éditeur SQL)'),
  ('20261124082100', 'base_unique_0007_compte_commun',
   array['-- Collé à la main le 24/11/2026 dans l''éditeur SQL : supabase/0007-compte-commun.sql (version 2.3) du dépôt du site, md5 f4e939976f3dc72bcdb0649b3de12912.'],
   'enseignant (éditeur SQL)'),
  ('20261124082200', 'base_unique_0008_enseignants_communs',
   array['-- Collé à la main le 24/11/2026 dans l''éditeur SQL : supabase/0008-enseignants-communs.sql du dépôt du site, md5 5e49dbf387d4b9bfb80478b4ab7c61c7.'],
   'enseignant (éditeur SQL)')
on conflict (version) do nothing;
```
