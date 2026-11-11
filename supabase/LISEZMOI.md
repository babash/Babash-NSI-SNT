# La base unique : le socle commun

Ce dossier contient les migrations qui ne relèvent d'aucune application : les préalables de la base unique (n° 2 de l'ordre d'ensemble, `architecture/base-unique.md`, § 3) et le schéma `commun`. Les migrations d'une application restent dans son propre dépôt (règle M1).

- **Le projet cible :** `cukahpyqkljiddmimpyi`, nom affiché « SNT-1er Jour », à renommer « Babash - applications ». Il porte SNT 1er jour, Expédition Gombessa et Alien Python.
- **Une exception :** `0004` vise l'ancien projet de Lagon Arena, `gkyvaugipddjqjvvpopw`. Il n'y touche à aucun objet `guilde_*`.
- **Les règles suivies :** `architecture/regles-supabase.md` (P2, P4, P8 corrigée, M1 à M8) et la spécification des codes, `architecture/codes-acces.md` (§ 1.10).

## Où en est la base (11/11/2026)

**Les quatre migrations sont appliquées**, après l'accord de l'enseignant (« Ok base 2 », 11/11 à 16:29, heure de Mayotte).
- Le chef d'orchestre les a appliquées par `apply_migration`, sans leurs lignes `begin;` et `commit;`.
- Chaque texte enregistré a la même empreinte que le fichier du commit `cff652e` (le même texte qu'en `88c4cd7` et `d113879`, ses identifiants avant les rebases ; md5 sans commentaires, espaces ni `;`) : **les fichiers SQL de ce dossier sont exactement ceux qui ont été appliqués**, et ne se modifient plus.
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

## Les fichiers

| Fichier | Projet | Nom de migration (`apply_migration`) | Ce qu'il fait |
|---|---|---|---|
| `0001-droits-par-defaut.sql` | cible | `base_unique_0001_droits_par_defaut` | Ferme les droits par défaut : un objet créé plus tard n'est ouvert à personne sans un droit exprès. |
| `0002-retrait-authenticated-et-sequences.sql` | cible | `base_unique_0002_retrait_authenticated_et_sequences` | Retire `authenticated` (et `public`) des fonctions de `public`, et ferme les deux séquences. Les droits d'`anon` ne changent pas. |
| `0003-schema-commun.sql` | cible | `base_unique_0003_schema_commun` | Crée le schéma `commun` : le compteur d'essais, le sel secret, six fonctions internes et le registre des tables. |
| `0004-ancien-projet-sequence-pantheon.sql` | **ancien projet de Lagon Arena** | `base_unique_0004_ancien_projet_sequence_pantheon` | Retire à `anon` ses droits sur `pantheon_id_seq`. |
| `NNNN-…-inverse.sql` | le même | `…_inverse` | Le SQL inverse de chaque migration. |
| `schema.sql` | un projet neuf | — | Le script complet du socle (0001 et 0003), pour la copie d'un·e collègue. |

Chaque fichier commence par `begin;` et finit par `commit;`, chacun sur sa ligne. Il se colle d'un bloc dans l'éditeur SQL. Par `apply_migration`, on retire seulement ces deux lignes : le reste est appliqué tel quel.

## L'ordre

1. **Recommandé : après l'étape 0 de Gombessa** (n° 1 du plan, `0001-espaces.sql` du dépôt `Rappel-1er`).
   - Si le n° 2 passe avant l'étape 0, tout marche aussi, mais l'étape 0 redonne le droit à `authenticated` sur ses 25 fonctions (elle les ouvre « à anon, authenticated »).
   - Il suffit alors de relancer `0002` juste après l'étape 0, sous le nom `base_unique_0002_retrait_authenticated_et_sequences_bis`. Le fichier se relance sans risque.
2. **Puis `0001`, `0002` et `0003`, dans cet ordre.** Chacun passe aussi seul.
3. **`0004`, quand on veut**, sur l'autre projet.

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
  - Ce sont les séquences de deux colonnes d'identité : Postgres les remplit sans vérifier de droit, et l'essai le confirme (ajout d'une réponse de SNT 1er jour en `anon`, journal de Gombessa).
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

- **Dans l'ordre inverse :** `0003-schema-commun-inverse.sql`, puis `0002-…-inverse.sql`, puis `0001-…-inverse.sql`. Chacun passe aussi seul. Pour l'autre projet : `0004-…-inverse.sql`.
- **`0003-schema-commun-inverse.sql` efface le sel et les compteurs d'essais.** Ce ne sont pas des données d'élèves : les compteurs repartent de zéro.
  - Il s'arrête, sans rien modifier, si le schéma contient un objet d'une autre migration, ou si une fonction d'application se sert déjà de `commun`. Il faut alors d'abord défaire la migration de cette application.
- **Les inverses rendent exactement l'état d'avant :** métadonnées, droits d'`anon` et d'`authenticated`, droits par défaut (voir l'essai local).

## Le script complet `schema.sql` (règle M2)

- **Pour qui :** un·e collègue qui installe sa copie. On le lance dans un projet neuf, avant le script complet d'une application.
- **Ce qu'il contient :** le texte de `0001` et de `0003`, sans le contrôle du projet de l'enseignant. `0002` n'y est pas : il corrige des objets qui existaient déjà.
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
