-- Après base_unique_0013_retours_eleves : vérification en lecture seule (métadonnées et count(*), aucune valeur lue).
-- Se colle dans l'éditeur SQL, ou se lance par l'outil execute_sql. Tout doit être « ok ».
with fn(nom) as (values ('commun_retour_donner'), ('commun_retour_effacer'), ('commun_prof_retours'), ('commun_prof_retour_effacer_mot')),
fp as (select p.oid, p.proname, p.prosecdef, p.proconfig from pg_proc p join fn on fn.nom = p.proname where p.pronamespace = 'public'::regnamespace),
fi as (select p.oid from pg_proc p where p.pronamespace = 'commun'::regnamespace and p.proname in ('retour_semaine', 'retour_cle', 'retours_publier')),
r(controle, attendu, trouve) as (
  select 'table commun.retours', 'oui', case when to_regclass('commun.retours') is null then 'non' else 'oui' end
  union all select 'RLS de commun.retours', 'oui', (select case when c.relrowsecurity then 'oui' else 'non' end from pg_class c where c.oid = 'commun.retours'::regclass)
  union all select 'règles d''accès (policies) sur commun.retours', '0', (select count(*) from pg_policy where polrelid = 'commun.retours'::regclass)::text
  union all select 'droits d''anon ou d''authenticated sur commun.retours', '0', (select count(*) from (values ('anon'), ('authenticated')) x(r)
       where has_table_privilege(x.r, 'commun.retours', 'select, insert, update, delete, truncate, references, trigger, maintain'))::text
  union all select 'colonnes (14), toutes commentées', '14/14', (select count(*) || '/' || count(col_description(a.attrelid, a.attnum)) from pg_attribute a
       where a.attrelid = 'commun.retours'::regclass and a.attnum > 0 and not a.attisdropped)
  union all select 'aucune colonne d''heure ni d''adresse', '0', (select count(*) from pg_attribute a where a.attrelid = 'commun.retours'::regclass
       and a.attnum > 0 and not a.attisdropped and a.atttypid in ('timestamptz'::regtype, 'timestamp'::regtype, 'inet'::regtype, 'cidr'::regtype))::text
  union all select 'commentaire de la table (registre : données d''élèves oui)', 'oui', (select donnees_eleves from commun.registre where schema_nom = 'commun' and table_nom = 'retours')
  union all select 'index de commun.retours (clé, unique de la clé d''appareil, 4 index)', '6', (select count(*) from pg_index where indrelid = 'commun.retours'::regclass)::text
  union all select 'clé étrangère vers les classes (on delete set null)', 'n', (select string_agg(c.confdeltype::text, ',') from pg_constraint c where c.conrelid = 'commun.retours'::regclass and c.contype = 'f')
  union all select 'fonctions d''entrée (4)', '4', (select count(*) from fp)::text
  union all select 'fonctions d''entrée : anon seul, security definer, search_path fixé', '0',
       (select count(*) from fp where not has_function_privilege('anon', fp.oid, 'execute') or has_function_privilege('authenticated', fp.oid, 'execute')
          or not fp.prosecdef or fp.proconfig is distinct from array['search_path=""'])::text
  union all select 'fonctions internes (3), fermées à l''API', '3/0', (select count(*) || '/' || count(*) filter (where has_function_privilege('anon', fi.oid, 'execute')
       or has_function_privilege('authenticated', fi.oid, 'execute') or has_function_privilege('public', fi.oid, 'execute')) from fi)
  union all select 'fonctions commentées (7)', '7', (select count(obj_description(x.oid, 'pg_proc')) from (select oid from fp union all select oid from fi) x)::text
  union all select 'fuseau Indian/Mayotte connu', 'oui', case when exists (select 1 from pg_timezone_names where name = 'Indian/Mayotte') then 'oui' else 'non' end
  union all select 'tables de commun sans RLS ou ouvertes', '0', (select count(*) from pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r'
       and (not c.relrowsecurity or has_table_privilege('anon', c.oid, 'select,insert,update,delete')))::text
  union all select 'avis gardés (juste après le collage)', '0', (select count(*) from commun.retours)::text
)
select controle, attendu, trouve, case when attendu = trouve then 'ok' else 'ÉCART' end as verdict from r;
