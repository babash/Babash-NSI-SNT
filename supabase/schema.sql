begin;
-- =============================================================================
--  Base unique : le socle commun, script complet
-- =============================================================================
--  À quoi il sert : installer le socle commun dans un projet Supabase neuf
--  (la copie d'un·e collègue), avant le script complet d'une application.
--  Il réunit, dans une seule transaction :
--   A. les droits par défaut fermés (migration 0001) ;
--   B. le schéma commun : compteur d'essais, sel secret, fonctions internes
--      et registre des tables (migration 0003) ;
--   C. le registre mis à jour : Court-circuit en plus (migration 0005) ;
--   D. le registre mis à jour : le Calendrier des vacances (migration 0009) ;
--   E. le compte commun des élèves : codes, avatar, hauts faits, XP et
--      crédits (migration 0007, version 2.3) ;
--   F. l'espace commun des enseignant·e·s et les classes communes
--      (migration 0008) ;
--   G. les avis anonymes des élèves sur les ressources (migration 0013).
--  La migration 0002 n'y est pas : elle corrige les droits d'objets qui
--  existaient déjà dans le projet de l'enseignant.
--
--  Mode d'emploi : dans le tableau de bord de Supabase, SQL Editor, coller
--  tout le fichier, puis Run. Relancé sur un projet déjà installé, il
--  s'arrête au garde-fou du compte commun (E) sans rien modifier : tout est
--  dans une seule transaction, et le sel n'est jamais tiré deux fois.
--
--  NE PAS MODIFIER À LA MAIN : ce fichier est fabriqué à partir de 0001,
--  0003, 0005, 0009, 0007, 0008 et 0013 par scripts/supabase_schema.py (même texte, sans le
--  contrôle du projet de l'enseignant). Il change dans le même commit qu'eux
--  (règle M2).
--  Détails : LISEZMOI.md.
-- =============================================================================

-- Garde-fou : le bon rôle, pgcrypto, et aucun objet « commun » venu d'ailleurs. Sinon, arrêt avant toute modification.
do $$
declare o text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regprocedure('extensions.gen_random_bytes(integer)') is null then
    raise exception 'L''extension pgcrypto manque dans le schéma extensions : arrêt, rien n''a été modifié.';
  end if;
  if to_regnamespace('commun') is not null
     and (pg_catalog.pg_get_userbyid((select nspowner from pg_catalog.pg_namespace where nspname = 'commun')) <> 'postgres'
          or coalesce(obj_description(to_regnamespace('commun'), 'pg_namespace'), '') not like 'Commun%') then
    raise exception 'Un schéma commun existe déjà et ne vient pas de cette migration : arrêt, rien n''a été modifié.';
  end if;
  foreach o in array array['commun.secret', 'commun.essais', 'commun.registre'] loop
    if to_regclass(o) is not null and coalesce(obj_description(to_regclass(o), 'pg_class'), '') not like 'Commun.%' then
      raise exception '% existe déjà et ne vient pas de cette migration : arrêt, rien n''a été modifié.', o;
    end if;
  end loop;
end $$;

-- =============================================================================
-- A. Les droits par défaut (migration 0001)
-- =============================================================================
-- A1. Schéma public : anon et authenticated ne reçoivent plus rien d'office.
alter default privileges for role postgres in schema public
  revoke all on tables from anon, authenticated;
alter default privileges for role postgres in schema public
  revoke all on sequences from anon, authenticated;
alter default privileges for role postgres in schema public
  revoke all on functions from anon, authenticated;

-- A2. Tous les schémas : public ne reçoit plus le droit d'exécution d'office.
--    Pas de « in schema » ici : ce droit est global.
alter default privileges for role postgres
  revoke execute on functions from public;

-- =============================================================================
-- B. Le schéma commun (migration 0003)
-- =============================================================================
-- -----------------------------------------------------------------------------
-- B1. Le schéma
-- -----------------------------------------------------------------------------
create schema if not exists commun authorization postgres;
revoke all on schema commun from public, anon, authenticated;
comment on schema commun is
  'Commun : ce qui sert à toutes les applications (le compteur d''essais, le sel secret, le registre des tables ; plus tard, l''identité commune). Jamais exposé à l''API ; aucun droit pour anon ni pour authenticated.';

-- -----------------------------------------------------------------------------
-- B2. Le sel secret : une seule ligne, tirée une fois
-- -----------------------------------------------------------------------------
create table if not exists commun.secret (
  seule_ligne boolean primary key default true check (seule_ligne),
  sel         text not null check (sel ~ '^[0-9a-f]{64}$'),
  cree_le     timestamptz not null default now()
);
alter table commun.secret enable row level security;
revoke all on commun.secret from public, anon, authenticated;
insert into commun.secret (sel) values (encode(extensions.gen_random_bytes(32), 'hex'))
  on conflict (seule_ligne) do nothing;
comment on table commun.secret is
  'Commun. Le sel secret du projet, tiré une fois au hasard, qui rend les empreintes de réseau impossibles à retrouver (commun.reseau). Une seule ligne. Ne se lit, ne se copie et ne se montre jamais. Données d''élèves : non.';
comment on column commun.secret.seule_ligne is 'Toujours vrai : garantit que la table n''a qu''une ligne.';
comment on column commun.secret.sel is 'Le sel : 32 octets tirés au hasard, en hexadécimal. Secret.';
comment on column commun.secret.cree_le is 'La date du tirage du sel.';

-- -----------------------------------------------------------------------------
-- B3. Le compteur d'essais (spécification des codes, § 1.10)
-- -----------------------------------------------------------------------------
create table if not exists commun.essais (
  application text not null check (application ~ '^[a-z][a-z_]{1,29}$'),
  reseau      text not null check (reseau ~ '^[0-9a-f]{64}$'),
  type        text not null check (type in ('eleve', 'enseignant', 'classe', 'creation')),
  heure       timestamptz not null,
  echecs      integer not null default 0 check (echecs >= 0),
  primary key (application, reseau, type, heure)
);
create index if not exists essais_heure on commun.essais (heure);
alter table commun.essais enable row level security;
revoke all on commun.essais from public, anon, authenticated;
comment on table commun.essais is
  'Commun. Les échecs de saisie de code, par application, réseau (empreinte du jour, jamais l''adresse), type d''essai et heure. Effacés après 24 h. Données d''élèves : non.';
comment on column commun.essais.application is 'L''application qui compte : son schéma (gombessa, alien, lagon, snt_premier_jour).';
comment on column commun.essais.reseau is 'L''empreinte du réseau de la requête (commun.reseau) : SHA-256 de l''adresse, du sel secret et de la date du jour. Jamais l''adresse elle-même.';
comment on column commun.essais.type is 'Le type d''essai : eleve (code d''élève), enseignant (code d''enseignant·e), classe (code de classe) ou creation (création de compte ou de réponse).';
comment on column commun.essais.heure is 'Le début de l''heure (UTC) où les échecs ont eu lieu.';
comment on column commun.essais.echecs is 'Le nombre d''échecs dans l''heure ; pour le type creation, le nombre de créations.';

-- -----------------------------------------------------------------------------
-- B4. Les fonctions internes : aucun droit pour personne. Seules les fonctions
--    d'entrée des applications (security definer, propriété de postgres)
--    les appellent.
-- -----------------------------------------------------------------------------

-- Le réseau de la requête, en empreinte qui change chaque jour.
-- L'adresse vient de l'en-tête cf-connecting-ip, sinon du premier élément
-- de x-forwarded-for (à confirmer au premier essai en ligne).
create or replace function commun.reseau()
returns text
language sql stable security definer
set search_path = ''
as $$
  select encode(sha256(convert_to(
           coalesce(nullif(btrim(e.h ->> 'cf-connecting-ip'), ''),
                    nullif(btrim(split_part(e.h ->> 'x-forwarded-for', ',', 1)), ''),
                    'inconnu')
           || '|' || s.sel || '|' || to_char(now() at time zone 'UTC', 'YYYY-MM-DD'),
           'UTF8')), 'hex')
  from (select nullif(current_setting('request.headers', true), '')::json as h) e,
       commun.secret s
$$;

-- Vrai si ce réseau a encore droit à un essai dans l'heure.
create or replace function commun.essai_permis(p_app text, p_type text, p_max integer)
returns boolean
language sql stable security definer
set search_path = ''
as $$
  select coalesce((select e.echecs from commun.essais e
                   where e.application = p_app and e.reseau = commun.reseau() and e.type = p_type
                     and e.heure = date_trunc('hour', now(), 'UTC')), 0) < p_max
$$;

-- Efface les compteurs de plus de 24 h. Renvoie le nombre de lignes effacées.
create or replace function commun.menage_essais()
returns integer
language sql volatile security definer
set search_path = ''
as $$
  with efface as (delete from commun.essais where heure < now() - interval '24 hours' returning 1)
  select count(*)::integer from efface
$$;

-- Compte un échec pour ce réseau. Renvoie le nombre d'échecs de l'heure.
create or replace function commun.noter_echec(p_app text, p_type text)
returns integer
language sql volatile security definer
set search_path = ''
as $$
  select commun.menage_essais();
  insert into commun.essais as e (application, reseau, type, heure, echecs)
  values (p_app, commun.reseau(), p_type, date_trunc('hour', now(), 'UTC'), 1)
  on conflict (application, reseau, type, heure) do update set echecs = e.echecs + 1
  returning e.echecs
$$;

-- Remet à zéro les compteurs de ce réseau pour une application (l'enseignant·e
-- « débloque son réseau »). Renvoie le nombre de lignes effacées.
create or replace function commun.debloquer_reseau(p_app text)
returns integer
language sql volatile security definer
set search_path = ''
as $$
  select commun.menage_essais();
  with efface as (delete from commun.essais where application = p_app and reseau = commun.reseau() returning 1)
  select count(*)::integer from efface
$$;

-- Le nombre d'échecs de l'heure dans une application, tous réseaux confondus
-- (sans les créations) : au-delà de 200, l'espace enseignant·e affiche une alarme.
create or replace function commun.echecs_heure(p_app text)
returns integer
language sql stable security definer
set search_path = ''
as $$
  select coalesce(sum(e.echecs), 0)::integer from commun.essais e
  where e.application = p_app and e.type <> 'creation' and e.heure = date_trunc('hour', now(), 'UTC')
$$;

revoke all on function commun.reseau(), commun.essai_permis(text, text, integer), commun.menage_essais(),
  commun.noter_echec(text, text), commun.debloquer_reseau(text), commun.echecs_heure(text)
  from public, anon, authenticated;

comment on function commun.reseau() is
  'Commun, interne. L''empreinte du réseau de la requête : SHA-256 de l''adresse (cf-connecting-ip, sinon x-forwarded-for), du sel secret et de la date du jour (UTC). Jamais l''adresse elle-même.';
comment on function commun.essai_permis(text, text, integer) is
  'Commun, interne. Vrai si ce réseau a fait moins de p_max échecs de ce type dans l''heure, pour cette application. Appelée avant de chercher un code.';
comment on function commun.menage_essais() is
  'Commun, interne. Efface les compteurs d''essais de plus de 24 h. Renvoie le nombre de lignes effacées.';
comment on function commun.noter_echec(text, text) is
  'Commun, interne. Compte un échec (ou une création) pour ce réseau, cette application et ce type, puis renvoie le nombre de l''heure. Fait aussi le ménage des compteurs de plus de 24 h.';
comment on function commun.debloquer_reseau(text) is
  'Commun, interne. Remet à zéro les compteurs de ce réseau pour une application : appelée par la fonction « débloquer le réseau » de l''espace enseignant·e, après vérification de son code. Renvoie le nombre de lignes effacées.';
comment on function commun.echecs_heure(text) is
  'Commun, interne. Le nombre d''échecs de l''heure dans une application, tous réseaux confondus, sans les créations : au-delà de 200, l''espace enseignant·e affiche une alarme.';

-- -----------------------------------------------------------------------------
-- B5. Le registre : la liste des tables de toutes les applications
--    (tableau de bord : Table Editor, schéma commun, puis registre).
--    Tant qu'une table est dans public, son application se lit à son préfixe.
-- -----------------------------------------------------------------------------
create or replace view commun.registre with (security_invoker = true) as
select
  case
    when n.nspname <> 'public' then n.nspname::text
    when c.relname like 'snt\_%' then 'snt_premier_jour'
    when c.relname like 'gb\_%' then 'gombessa'
    when c.relname like 'alien\_%' then 'alien'
    when c.relname like 'lagon\_%' then 'lagon'
    else 'à identifier'
  end as application,
  n.nspname::text as schema_nom,
  c.relname::text as table_nom,
  case c.relkind when 'v' then 'vue' when 'm' then 'vue matérialisée' when 'p' then 'table partitionnée' else 'table' end as genre,
  case
    when obj_description(c.oid, 'pg_class') like '%Données d''élèves : oui%' then 'oui'
    when obj_description(c.oid, 'pg_class') like '%Données d''élèves : non%' then 'non'
  end as donnees_eleves,
  obj_description(c.oid, 'pg_class') as description,
  case when c.relkind in ('r', 'p', 'm') then greatest(c.reltuples, 0)::bigint end as lignes_environ
from pg_catalog.pg_class c
join pg_catalog.pg_namespace n on n.oid = c.relnamespace
where c.relkind in ('r', 'p', 'v', 'm')
  and n.nspname in ('public', 'snt_premier_jour', 'gombessa', 'alien', 'lagon', 'commun')
order by 1, 2, 3;
revoke all on commun.registre from public, anon, authenticated;
comment on view commun.registre is
  'Commun. La liste des tables de toutes les applications, avec leur description, tirée des commentaires des tables. Données d''élèves : non.';
comment on column commun.registre.application is 'L''application : le schéma de la table, ou, pour une table encore dans public, l''application de son préfixe (snt_, gb_, alien_, lagon_).';
comment on column commun.registre.schema_nom is 'Le schéma où se trouve la table.';
comment on column commun.registre.table_nom is 'Le nom de la table.';
comment on column commun.registre.genre is 'Table, table partitionnée, vue ou vue matérialisée.';
comment on column commun.registre.donnees_eleves is 'oui ou non, d''après la description de la table ; vide si la table n''a pas encore de description.';
comment on column commun.registre.description is 'Le commentaire de la table : « Application. Ce que contient la table. Données d''élèves : oui ou non. »';
comment on column commun.registre.lignes_environ is 'Le nombre de lignes, environ (statistiques de Postgres, sans compter) ; vide pour une vue.';

-- -----------------------------------------------------------------------------
-- B6. Contrôle : rien d'ouvert à l'API. Sinon, arrêt : rien n'est appliqué.
-- -----------------------------------------------------------------------------
do $$
begin
  if has_schema_privilege('anon', 'commun', 'usage') or has_schema_privilege('authenticated', 'commun', 'usage') then
    raise exception 'Le schéma commun est ouvert à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction de commun est appelable par anon ou par authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'v')
             and (has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de commun est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r' and not c.relrowsecurity) then
    raise exception 'Une table de commun n''a pas la RLS : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from commun.secret) <> 1 then
    raise exception 'commun.secret doit avoir exactement une ligne : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- =============================================================================
-- C. Le registre : Court-circuit en plus (migration 0005)
-- =============================================================================
-- -----------------------------------------------------------------------------
-- C1. Le registre : la liste des tables de toutes les applications, Court-circuit
--    compris (tableau de bord : Table Editor, schéma commun, puis registre).
--    Tant qu'une table est dans public, son application se lit à son préfixe.
-- -----------------------------------------------------------------------------
create or replace view commun.registre with (security_invoker = true) as
select
  case
    when n.nspname <> 'public' then n.nspname::text
    when c.relname like 'snt\_%' then 'snt_premier_jour'
    when c.relname like 'gb\_%' then 'gombessa'
    when c.relname like 'alien\_%' then 'alien'
    when c.relname like 'lagon\_%' then 'lagon'
    when c.relname like 'cc\_%' then 'court_circuit'
    else 'à identifier'
  end as application,
  n.nspname::text as schema_nom,
  c.relname::text as table_nom,
  case c.relkind when 'v' then 'vue' when 'm' then 'vue matérialisée' when 'p' then 'table partitionnée' else 'table' end as genre,
  case
    when obj_description(c.oid, 'pg_class') like '%Données d''élèves : oui%' then 'oui'
    when obj_description(c.oid, 'pg_class') like '%Données d''élèves : non%' then 'non'
  end as donnees_eleves,
  obj_description(c.oid, 'pg_class') as description,
  case when c.relkind in ('r', 'p', 'm') then greatest(c.reltuples, 0)::bigint end as lignes_environ
from pg_catalog.pg_class c
join pg_catalog.pg_namespace n on n.oid = c.relnamespace
where c.relkind in ('r', 'p', 'v', 'm')
  and n.nspname in ('public', 'snt_premier_jour', 'gombessa', 'alien', 'lagon', 'court_circuit', 'commun')
order by 1, 2, 3;
revoke all on commun.registre from public, anon, authenticated;
comment on column commun.registre.application is 'L''application : le schéma de la table, ou, pour une table encore dans public, l''application de son préfixe (snt_, gb_, alien_, lagon_, cc_).';
comment on column commun.essais.application is 'L''application qui compte : son schéma (snt_premier_jour, gombessa, alien, lagon, court_circuit).';

-- -----------------------------------------------------------------------------
-- C2. Contrôle : la vue reste fermée à l'API et security_invoker, et elle range
--    chaque table de court_circuit. Sinon, arrêt : rien n'est appliqué.
-- -----------------------------------------------------------------------------
do $$
begin
  if has_table_privilege('anon', 'commun.registre', 'select, insert, update, delete, truncate, references, trigger, maintain')
     or has_table_privilege('authenticated', 'commun.registre', 'select, insert, update, delete, truncate, references, trigger, maintain') then
    raise exception 'La vue commun.registre est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if not exists (select 1 from pg_catalog.pg_class c where c.oid = 'commun.registre'::regclass
                 and 'security_invoker=true' = any(c.reloptions)) then
    raise exception 'La vue commun.registre n''est plus security_invoker : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from commun.registre r where r.schema_nom = 'court_circuit' and r.application = 'court_circuit')
     <> (select count(*) from pg_catalog.pg_class c where c.relnamespace = to_regnamespace('court_circuit') and c.relkind in ('r', 'p', 'v', 'm')) then
    raise exception 'Le registre ne range pas toutes les tables de court_circuit : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- =============================================================================
-- D. Le registre : le Calendrier des vacances (migration 0009)
-- =============================================================================
create or replace view commun.registre with (security_invoker = true) as
select
  case
    when n.nspname <> 'public' then n.nspname::text
    when c.relname like 'snt\_%' then 'snt_premier_jour'
    when c.relname like 'gb\_%' then 'gombessa'
    when c.relname like 'alien\_%' then 'alien'
    when c.relname like 'lagon\_%' then 'lagon'
    when c.relname like 'cc\_%' then 'court_circuit'
    when c.relname like 'go\_%' then 'grand_oral'
    when c.relname like 'cv\_%' then 'vacances'
    else 'à identifier'
  end as application,
  n.nspname::text as schema_nom,
  c.relname::text as table_nom,
  case c.relkind when 'v' then 'vue' when 'm' then 'vue matérialisée' when 'p' then 'table partitionnée' else 'table' end as genre,
  case
    when obj_description(c.oid, 'pg_class') like '%Données d''élèves : oui%' then 'oui'
    when obj_description(c.oid, 'pg_class') like '%Données d''élèves : non%' then 'non'
  end as donnees_eleves,
  obj_description(c.oid, 'pg_class') as description,
  case when c.relkind in ('r', 'p', 'm') then greatest(c.reltuples, 0)::bigint end as lignes_environ
from pg_catalog.pg_class c
join pg_catalog.pg_namespace n on n.oid = c.relnamespace
where c.relkind in ('r', 'p', 'v', 'm')
  and n.nspname in ('public', 'snt_premier_jour', 'gombessa', 'alien', 'lagon', 'court_circuit', 'grand_oral', 'vacances', 'commun')
order by 1, 2, 3;
revoke all on commun.registre from public, anon, authenticated;
comment on column commun.registre.application is 'L''application : le schéma de la table, ou, pour une table encore dans public, l''application de son préfixe (snt_, gb_, alien_, lagon_, cc_, go_, cv_).';
comment on column commun.essais.application is 'L''application qui compte : son schéma (snt_premier_jour, gombessa, alien, lagon, court_circuit, grand_oral, vacances).';

-- =============================================================================
-- E. Le compte commun des élèves (migration 0007, version 2.3)
-- =============================================================================
-- Garde-fou : le bon rôle, le socle 0003, pgcrypto, et aucun
-- objet de même nom venu d'ailleurs. Sinon, arrêt avant toute modification.
do $$
declare o text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regprocedure('commun.essai_permis(text, text, integer)') is null or to_regprocedure('commun.noter_echec(text, text)') is null then
    raise exception 'Le socle commun (0003) manque : l''appliquer d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if to_regprocedure('extensions.gen_random_bytes(integer)') is null then
    raise exception 'L''extension pgcrypto manque dans le schéma extensions : arrêt, rien n''a été modifié.';
  end if;
  foreach o in array array['commun.applications', 'commun.mots', 'commun.comptes', 'commun.codes', 'commun.liens',
                           'commun.sessions', 'commun.emplacements', 'commun.elements', 'commun.hauts_faits',
                           'commun.recompenses', 'commun.hauts_faits_gagnes', 'commun.elements_debloques',
                           'commun.baremes', 'commun.activites', 'commun.xp_journal', 'commun.menage'] loop
    if to_regclass(o) is not null then
      raise exception '% existe déjà : arrêt, rien n''a été modifié.', o;
    end if;
  end loop;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%') then
    raise exception 'Une fonction public.commun_… existe déjà : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- E1. Les applications et leurs connecteurs
-- -----------------------------------------------------------------------------
create table commun.applications (
  id                 text primary key check (id ~ '^[a-z][a-z_]{1,29}$'),
  nom                text not null check (char_length(nom) between 2 and 60),
  adresse            text check (adresse ~ '^https://babash\.github\.io/[A-Za-z0-9._/-]*$'),
  adresse_prof       text check (adresse_prof ~ '^https://babash\.github\.io/[A-Za-z0-9._/-]*$'),
  mode               text not null check (mode in ('site', 'rattachee', 'native', 'sans_compte')),
  fn_par_code        regprocedure,
  fn_par_id          regprocedure,
  fn_hauts_faits     regprocedure,
  fn_effacer         regprocedure,
  fn_fusion          regprocedure,
  accord_par_page    boolean not null default false,
  pseudo_a_confirmer boolean not null default false,
  plafond_xp_jour    integer not null default 150 check (plafond_xp_jour between 0 and 1000),
  active             boolean not null default true,
  cree_le            timestamptz not null default now()
);
alter table commun.applications enable row level security;
revoke all on commun.applications from public, anon, authenticated;
comment on table commun.applications is
  'Commun. Les applications qui partagent le compte commun, et leurs connecteurs : les fonctions internes de chaque application que le compte commun appelle. Écrite seulement par les migrations. Données d''élèves : non.';
comment on column commun.applications.id is 'L''identifiant de l''application : son schéma (court_circuit, gombessa…), commun pour le site, td pour les feuilles de TD en ligne.';
comment on column commun.applications.nom is 'Le nom affiché aux élèves (« Expédition Gombessa »).';
comment on column commun.applications.adresse is 'L''adresse publique de l''application, sur babash.github.io.';
comment on column commun.applications.adresse_prof is 'L''adresse du tableau de bord enseignant·e de l''application, vers lequel renvoie la page d''une classe commune.';
comment on column commun.applications.mode is 'site : le site lui-même ; rattachee : l''application garde ses comptes et les relie au compte commun ; native : l''application se sert directement du compte commun ; sans_compte : aucune table d''élève (feuilles de TD, QuizzNSI).';
comment on column commun.applications.fn_par_code is 'Connecteur facultatif (p_code text) returns table(eleve_id uuid, pseudo text, code_affiche text) : le compte de l''application qui a ce code (forme canonique), s''il existe.';
comment on column commun.applications.fn_par_id is 'Connecteur facultatif (p_eleve uuid) returns table(eleve_id uuid, pseudo text, code_affiche text) : le pseudo et le code d''un compte de l''application.';
comment on column commun.applications.fn_hauts_faits is 'Connecteur facultatif (p_eleve uuid) returns text[] : les hauts faits que la progression déjà enregistrée dans l''application permet d''accorder.';
comment on column commun.applications.fn_effacer is 'Connecteur facultatif (p_eleve uuid) returns void : efface le compte de l''application, quand l''élève demande « Effacer partout ».';
comment on column commun.applications.fn_fusion is 'Connecteur facultatif (p_garder uuid, p_absorber uuid) returns void, pour une application native : reporte ses lignes d''un compte commun sur l''autre avant une fusion.';
comment on column commun.applications.accord_par_page is 'Vrai si la page de l''application, sans fonction de serveur, peut déclarer ses événements et ses hauts faits de genre page (feuilles de TD, QuizzNSI).';
comment on column commun.applications.pseudo_a_confirmer is 'Vrai si le pseudo copié de cette application doit être confirmé par l''élève à sa première entrée sur le site (Hello GO : prénom et initiale du nom, qui ne sont plus nécessaires).';
comment on column commun.applications.plafond_xp_jour is 'L''XP qu''un compte peut gagner au plus par jour dans cette application, hauts faits et attributions de l''enseignant·e non compris (anti-abus).';
comment on column commun.applications.active is 'Faux pour une application retirée : ce qui a été gagné reste, elle n''accorde plus rien.';
comment on column commun.applications.cree_le is 'La date de l''inscription de l''application.';

insert into commun.applications (id, nom, adresse, adresse_prof, mode, accord_par_page, pseudo_a_confirmer) values
  ('commun',        'Ressources NSI et SNT',  'https://babash.github.io/Babash-NSI-SNT/eleve/', 'https://babash.github.io/Babash-NSI-SNT/enseignant/', 'site', false, false),
  ('td',            'Feuilles de TD en ligne', 'https://babash.github.io/Babash-NSI-SNT/', null, 'sans_compte', true, false),
  ('vacances',      'Calendrier des vacances', 'https://babash.github.io/Babash-NSI-SNT/calendrier/', 'https://babash.github.io/Babash-NSI-SNT/calendrier/', 'rattachee', false, false),
  ('quizz_nsi',     'QuizzNSI',               'https://babash.github.io/quizz-nsi/', 'https://babash.github.io/quizz-nsi/', 'sans_compte', false, false),
  ('gombessa',      'Expédition Gombessa',    'https://babash.github.io/gombessa/', 'https://babash.github.io/gombessa/prof.html', 'rattachee', false, false),
  ('court_circuit', 'Court-circuit',          'https://babash.github.io/court-circuit/', 'https://babash.github.io/court-circuit/prof.html', 'rattachee', false, false),
  ('grand_oral',    'Hello GO',               null, null, 'rattachee', false, true),
  ('lagon',         'Lagon Arena',            'https://babash.github.io/lagon-arena/', 'https://babash.github.io/lagon-arena/prof.html', 'native', false, false),
  ('alien',         'Alien Python',           'https://babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python/', null, 'native', false, false);

-- -----------------------------------------------------------------------------
-- E2. Les mots des codes nés dans le compte commun
-- -----------------------------------------------------------------------------
create table commun.mots (
  application text not null references commun.applications (id),
  rang        smallint not null check (rang between 0 and 63),
  mot         text not null unique check (mot ~ '^[A-Z]{4,8}$'),
  primary key (application, rang)
);
alter table commun.mots enable row level security;
revoke all on commun.mots from public, anon, authenticated;
comment on table commun.mots is
  'Commun. Les 64 mots des codes tirés par le compte commun, par application : ceux du site (thème : les pirates informatiques et la flibuste), puis ceux de chaque application native. Aucun mot n''est dans la liste d''une autre application, ni le début d''un autre mot (scripts/verifier_listes_mots.py). Données d''élèves : non.';
comment on column commun.mots.application is 'L''application dont la liste contient ce mot (commun pour le site).';
comment on column commun.mots.rang is 'Le rang du mot dans sa liste, de 0 à 63 : un octet tiré au hasard, modulo 64, le choisit sans biais.';
comment on column commun.mots.mot is 'Le mot, en majuscules sans accent, de 4 à 8 lettres.';

insert into commun.mots (application, rang, mot) values
('commun', 0, 'PIRATE'), ('commun', 1, 'CORSAIRE'), ('commun', 2, 'FLIBUSTE'), ('commun', 3, 'GALION'),
('commun', 4, 'BRICK'), ('commun', 5, 'GOELETTE'), ('commun', 6, 'JONQUE'), ('commun', 7, 'BARQUE'),
('commun', 8, 'CHALOUPE'), ('commun', 9, 'BABORD'), ('commun', 10, 'TRIBORD'), ('commun', 11, 'ETRAVE'),
('commun', 12, 'CABESTAN'), ('commun', 13, 'COFFRE'), ('commun', 14, 'DOUBLON'), ('commun', 15, 'PIASTRE'),
('commun', 16, 'LINGOT'), ('commun', 17, 'RUBIS'), ('commun', 18, 'SAPHIR'), ('commun', 19, 'EMERAUDE'),
('commun', 20, 'BUTIN'), ('commun', 21, 'REPAIRE'), ('commun', 22, 'CAVERNE'), ('commun', 23, 'ETENDARD'),
('commun', 24, 'DRAPEAU'), ('commun', 25, 'TONNEAU'), ('commun', 26, 'BARIL'), ('commun', 27, 'VIGIE'),
('commun', 28, 'OURAGAN'), ('commun', 29, 'ALIZE'), ('commun', 30, 'ESTUAIRE'), ('commun', 31, 'TOUCAN'),
('commun', 32, 'ADMIN'), ('commun', 33, 'KERNEL'), ('commun', 34, 'GLITCH'), ('commun', 35, 'PROXY'),
('commun', 36, 'BINAIRE'), ('commun', 37, 'TERMINAL'), ('commun', 38, 'SERVEUR'), ('commun', 39, 'PAREFEU'),
('commun', 40, 'JETON'), ('commun', 41, 'CACHE'), ('commun', 42, 'PING'), ('commun', 43, 'HEXA'),
('commun', 44, 'ALGO'), ('commun', 45, 'MATRICE'), ('commun', 46, 'VECTEUR'), ('commun', 47, 'OCTET'),
('commun', 48, 'ARCHIVE'), ('commun', 49, 'DOMAINE'), ('commun', 50, 'BOUCLE'), ('commun', 51, 'CURSEUR'),
('commun', 52, 'PROMPT'), ('commun', 53, 'UNICODE'), ('commun', 54, 'CODEX'), ('commun', 55, 'CRYPTO'),
('commun', 56, 'LOGIN'), ('commun', 57, 'FORMAT'), ('commun', 58, 'NOYAU'), ('commun', 59, 'FLUX'),
('commun', 60, 'CLEF'), ('commun', 61, 'NUAGE'), ('commun', 62, 'MEMOIRE'), ('commun', 63, 'FLOTTE');

-- -----------------------------------------------------------------------------
-- E3. Les comptes, leurs codes, leurs liens et leurs sessions
-- -----------------------------------------------------------------------------
create table commun.comptes (
  id                 uuid primary key default gen_random_uuid(),
  pseudo             text not null check (char_length(pseudo) between 2 and 24),
  pseudo_provisoire  boolean not null default false,
  origine            text not null references commun.applications (id),
  avatar             jsonb not null default '{"v": 1, "lignee": "humain", "teint": 5, "corps": "moyenne", "coiffure": "court", "cheveux": "noirs", "haut": "tshirt", "bas": "pantalon", "chaussures": "baskets", "objets": {"tete": "aucun", "visage": "aucun", "cou": "aucun", "dos": "aucun", "main": "aucun", "epaule": "aucun", "pieds": "aucun", "autour": "aucun"}, "fauteuil": false, "compagnon": "margouillat", "couleurs": {"haut": "canard", "bas": "anthracite", "accent": "cyan", "chaussures": "blanches", "yeux": "bruns"}}'::jsonb
                     check (jsonb_typeof(avatar) = 'object' and octet_length(avatar::text) <= 600),
  xp                 integer not null default 0 check (xp >= 0),
  credits            integer not null default 0 check (credits >= 0),
  cree_le            timestamptz not null default now(),
  vu_le              timestamptz not null default now()
);
create index comptes_vu_le on commun.comptes (vu_le);
alter table commun.comptes enable row level security;
revoke all on commun.comptes from public, anon, authenticated;
comment on table commun.comptes is
  'Commun. Un compte par élève, pour toutes les applications : son prénom ou son pseudo (jamais le nom de famille), l''avatar porté, son XP et ses crédits. L''XP n''est montrée à aucun·e élève ; les crédits seulement à l''élève, comme un solde à dépenser. Effacé 12 mois après la dernière visite, ou à la demande de l''élève. Données d''élèves : oui.';
comment on column commun.comptes.id is 'L''identifiant du compte, tiré au hasard. Pour une application native, c''est aussi l''identifiant de l''élève dans ses tables.';
comment on column commun.comptes.pseudo is 'Le prénom ou le pseudo choisi par l''élève, de 2 à 24 caractères, jamais le nom de famille ni son initiale.';
comment on column commun.comptes.pseudo_provisoire is 'Vrai si le pseudo a été copié d''une application qui demande une confirmation (Hello GO) : la page demande à l''élève de choisir son pseudo.';
comment on column commun.comptes.origine is 'L''application où le compte est né : le site (commun) ou l''application du premier code.';
comment on column commun.comptes.avatar is 'L''avatar porté : la description du moteur d''avatars du site (assets/equipage.js, version 1) : lignée, teint, corps, coiffure, cheveux, haut, bas, chaussures, fauteuil, couleurs (gratuits, pour tout avatar), objets (8 emplacements) et compagnon (libres, gagnés ou achetés). Que des identifiants, jamais de texte libre. Vérifié par commun.verifier_avatar. 600 octets au plus.';
comment on column commun.comptes.xp is 'L''XP gagnée depuis la création du compte : elle ne baisse jamais (les achats n''y touchent pas). Somme des gains du journal. Cachée à tous les élèves ; vue par l''enseignant·e de ses classes.';
comment on column commun.comptes.credits is 'Les crédits à dépenser en apparences : l''XP gagnée moins les achats. Jamais négatifs. Montrés à l''élève seul·e, comme un solde.';
comment on column commun.comptes.cree_le is 'La date de création du compte commun.';
comment on column commun.comptes.vu_le is 'La date de la dernière visite, sur le site ou dans une application branchée. Sert au ménage des 12 mois.';

create table commun.codes (
  code          text primary key check (code ~ '^[A-Z]{8,32}[0-9]{3,4}$'),
  code_affiche  text not null check (code_affiche ~ '^[A-Z]{4,8}(-[A-Z]{4,8}){1,2}-[0-9]{3,4}$'),
  compte_id     uuid not null references commun.comptes (id) on delete cascade,
  application   text not null references commun.applications (id),
  principal     boolean not null default true,
  cree_le       timestamptz not null default now()
);
create index codes_compte on commun.codes (compte_id);
create unique index codes_un_principal on commun.codes (compte_id) where principal;
alter table commun.codes enable row level security;
revoke all on commun.codes from public, anon, authenticated;
comment on table commun.codes is
  'Commun. Les codes tirés par le compte commun (codes nés sur le site ou dans une application native) : 2 mots et 3 chiffres. Les codes des applications rattachées restent dans leurs tables et sont lus par leurs connecteurs. Secret. Données d''élèves : oui.';
comment on column commun.codes.code is 'Le code sous sa forme canonique (majuscules, sans séparateur) : CLAVIERFRESQUE482. Unique dans tout le projet, grâce aux listes de mots disjointes.';
comment on column commun.codes.code_affiche is 'Le code tel qu''on l''affiche et l''imprime : PROXY-CORSAIRE-482.';
comment on column commun.codes.compte_id is 'Le compte que ce code ouvre.';
comment on column commun.codes.application is 'L''application dont la liste de mots a servi au tirage.';
comment on column commun.codes.principal is 'Vrai pour le code à donner en premier à l''élève ; faux pour un code gagné par une fusion, qui reste valable.';
comment on column commun.codes.cree_le is 'La date du tirage.';

create table commun.liens (
  application   text not null references commun.applications (id),
  eleve_app_id  uuid not null,
  compte_id     uuid not null references commun.comptes (id) on delete cascade,
  depuis        timestamptz not null default now(),
  primary key (application, eleve_app_id)
);
create index liens_compte on commun.liens (compte_id);
alter table commun.liens enable row level security;
revoke all on commun.liens from public, anon, authenticated;
comment on table commun.liens is
  'Commun. Les comptes des applications rattachées reliés à chaque compte commun : un code de Gombessa, de Court-circuit ou de Hello GO ouvre le compte commun qui lui est relié. Effacés avec le compte commun ; le compte de l''application, lui, reste. Données d''élèves : oui (un lien entre deux comptes).';
comment on column commun.liens.application is 'L''application rattachée.';
comment on column commun.liens.eleve_app_id is 'L''identifiant de l''élève dans cette application (gb_eleves.id, court_circuit.eleves.id…).';
comment on column commun.liens.compte_id is 'Le compte commun relié.';
comment on column commun.liens.depuis is 'La date du lien.';

create table commun.sessions (
  jeton        uuid primary key default gen_random_uuid(),
  compte_id    uuid not null references commun.comptes (id) on delete cascade,
  garde_jours  smallint not null default 1 check (garde_jours in (1, 30)),
  cree_le      timestamptz not null default now(),
  vu_le        timestamptz not null default now()
);
create index sessions_compte on commun.sessions (compte_id);
alter table commun.sessions enable row level security;
revoke all on commun.sessions from public, anon, authenticated;
comment on table commun.sessions is
  'Commun. Les jetons de session du compte commun : un par appareil où l''élève est entré·e avec son code, 5 au plus (le plus ancien part). Un jeton vaut 1 jour (poste partagé, par défaut) ou 30 jours depuis son dernier usage (« mon appareil »). Données d''élèves : oui (un jeton au hasard et deux dates).';
comment on column commun.sessions.jeton is 'Le jeton, tiré au hasard, que la page garde et renvoie à chaque appel. Secret.';
comment on column commun.sessions.compte_id is 'Le compte ouvert par ce jeton.';
comment on column commun.sessions.garde_jours is '1 : le jeton expire un jour après sa création (poste partagé) ; 30 : il expire 30 jours après son dernier usage (appareil personnel).';
comment on column commun.sessions.cree_le is 'La date de l''entrée avec le code.';
comment on column commun.sessions.vu_le is 'La date du dernier usage du jeton.';

-- -----------------------------------------------------------------------------
-- E4. L'avatar : les emplacements et les éléments
-- -----------------------------------------------------------------------------
create table commun.emplacements (
  id           text primary key check (id ~ '^[a-z_]{2,20}$'),
  nom          text not null check (char_length(nom) between 2 and 40),
  genre        text not null check (genre in ('objet', 'compagnon')),
  ordre        smallint not null default 0
);
alter table commun.emplacements enable row level security;
revoke all on commun.emplacements from public, anon, authenticated;
comment on table commun.emplacements is
  'Commun. Les emplacements des objets de l''avatar (sur la tête, dans la main…) et celui du compagnon, ceux du moteur d''avatars du site. L''identité et les tenues (lignée, teint, corps, coiffure, haut, bas, chaussures, couleurs) ne sont pas des emplacements : elles sont gratuites pour tout avatar. Le dessin n''est pas ici : la page le fait avec le moteur. Données d''élèves : non.';
comment on column commun.emplacements.id is 'L''identifiant de l''emplacement, qui ouvre l''identifiant de ses éléments (tete:…, compagnon:…), et la clé de l''objet dans la description de l''avatar.';
comment on column commun.emplacements.nom is 'Le nom affiché dans la loge de l''avatar (« Sur la tête »).';
comment on column commun.emplacements.genre is 'objet : un objet porté, un seul par emplacement ; compagnon : l''animal ou le robot qui accompagne l''avatar.';
comment on column commun.emplacements.ordre is 'L''ordre d''affichage dans la loge.';

insert into commun.emplacements (id, nom, genre, ordre) values
  ('tete',      'Sur la tête',            'objet',     1),
  ('visage',    'Sur le visage',          'objet',     2),
  ('cou',       'Au cou et à la taille',  'objet',     3),
  ('dos',       'Dans le dos',            'objet',     4),
  ('main',      'Dans la main',           'objet',     5),
  ('epaule',    'Sur les épaules',        'objet',     6),
  ('pieds',     'Aux pieds',              'objet',     7),
  ('autour',    'Autour',                 'objet',     8),
  ('compagnon', 'Compagnon',              'compagnon', 9);

create table commun.elements (
  id           text primary key check (id ~ '^[a-z_]{2,20}:[a-z0-9_]{1,40}$'),
  emplacement  text not null references commun.emplacements (id),
  famille      text check (famille ~ '^[a-z_]{2,20}$'),
  nom          text not null check (char_length(nom) between 2 and 60),
  description  text not null default '' check (char_length(description) <= 200),
  acces        text not null check (acces in ('libre', 'haut_fait', 'credits')),
  prix         integer check (prix between 1 and 2000),
  ordre        smallint not null default 0,
  actif        boolean not null default true,
  ajoute_le    timestamptz not null default now(),
  check (split_part(id, ':', 1) = emplacement),
  check ((acces = 'credits') = (prix is not null))
);
alter table commun.elements enable row level security;
revoke all on commun.elements from public, anon, authenticated;
comment on table commun.elements is
  'Commun. Le catalogue des objets et des compagnons de l''avatar : un identifiant, un nom, une famille et la façon de l''obtenir (libre, gagné par un haut fait, ou acheté avec des crédits). Aucun n''est réservé à une lignée ni à un genre. Le dessin n''est pas ici : le moteur d''avatars le trouve par l''identifiant. Un élément n''est jamais supprimé : retiré du catalogue, il reste à qui l''a. Rempli par la migration du catalogue (0010), sauf le margouillat. Données d''élèves : non.';

insert into commun.elements (id, emplacement, nom, description, acces, ordre) values
  ('compagnon:margouillat', 'compagnon', 'Le margouillat', 'Le compagnon de départ de tout le monde.', 'libre', 0);
comment on column commun.elements.id is 'L''identifiant : l''emplacement, deux-points, l''identifiant de l''objet dans le moteur d''avatars (tete:passoire_pensee, compagnon:maki). Ne change jamais.';
comment on column commun.elements.famille is 'La famille du catalogue du moteur (clin, classe, heros…), pour ranger la boutique ; vide pour un compagnon. Son nom affiché vient du catalogue, jamais de la base.';
comment on column commun.elements.emplacement is 'L''emplacement de l''élément (le début de son identifiant).';
comment on column commun.elements.nom is 'Le nom affiché (« La passoire à lire les pensées »), 60 caractères au plus.';
comment on column commun.elements.description is 'Une phrase de description, 200 caractères au plus.';
comment on column commun.elements.acces is 'libre : à tout le monde dès le début (le margouillat) ; haut_fait : un trophée, gagné par un haut fait (table recompenses), qui ne s''achète pas ; credits : s''achète avec des crédits.';
comment on column commun.elements.prix is 'Le prix en crédits, pour un élément de genre credits seulement.';
comment on column commun.elements.ordre is 'L''ordre d''affichage dans la loge.';
comment on column commun.elements.actif is 'Faux pour un élément retiré du catalogue : il n''est plus proposé, mais qui l''a le garde et peut le porter.';
comment on column commun.elements.ajoute_le is 'La date de l''ajout au catalogue.';

-- -----------------------------------------------------------------------------
-- E5. Les hauts faits : le catalogue, les récompenses, ce qui est gagné
-- -----------------------------------------------------------------------------
create table commun.hauts_faits (
  application  text not null references commun.applications (id),
  id           text not null check (id ~ '^[a-z0-9-]{2,40}$'),
  nom          text not null check (char_length(nom) between 2 and 40),
  description  text not null check (char_length(description) between 5 and 200),
  categorie    text not null check (categorie in ('premiers_pas', 'exploration', 'perseverance', 'creation', 'entraide', 'maitrise')),
  secret       boolean not null default false,
  indice       text check (char_length(indice) <= 120),
  accord       text not null default 'serveur' check (accord in ('serveur', 'page', 'enseignant', 'seance')),
  xp           smallint not null default 20 check (xp between 0 and 200),
  ordre        smallint not null default 0,
  actif        boolean not null default true,
  ajoute_le    timestamptz not null default now(),
  primary key (application, id),
  check (not secret or indice is not null)
);
alter table commun.hauts_faits enable row level security;
revoke all on commun.hauts_faits from public, anon, authenticated;
comment on table commun.hauts_faits is
  'Commun. Le catalogue des hauts faits de chaque application : ce qu''il faut faire, en une phrase. Ni rang, ni série de jours, ni comparaison entre élèves : un haut fait se gagne une fois et ne se perd jamais. Écrit par les migrations des applications. Données d''élèves : non.';
comment on column commun.hauts_faits.application is 'L''application qui accorde ce haut fait (commun pour ceux de l''enseignant·e).';
comment on column commun.hauts_faits.id is 'L''identifiant court, unique dans l''application (premier-circuit). Ne change jamais.';
comment on column commun.hauts_faits.nom is 'Le nom affiché (« Premier circuit »), 40 caractères au plus.';
comment on column commun.hauts_faits.description is 'Ce qu''il faut faire, en une phrase de 200 caractères au plus.';
comment on column commun.hauts_faits.categorie is 'Le genre de haut fait, pour ranger la collection : premiers_pas, exploration, perseverance, creation, entraide, maitrise.';
comment on column commun.hauts_faits.secret is 'Vrai pour une surprise : avant qu''il soit gagné, on n''en montre que l''indice.';
comment on column commun.hauts_faits.indice is 'L''indice montré à la place du nom et de la description d''un haut fait secret.';
comment on column commun.hauts_faits.accord is 'Qui l''accorde : serveur (une fonction de l''application), page (la page d''une application sans serveur), enseignant (l''enseignant·e), seance (la page projetée d''une séance, avec le code de l''enseignant·e : QuizzNSI, migration 0011).';
comment on column commun.hauts_faits.xp is 'L''XP rapportée une fois, quand le haut fait est gagné (20 par défaut). Hors du plafond journalier.';
comment on column commun.hauts_faits.ordre is 'L''ordre d''affichage dans la collection de l''application.';
comment on column commun.hauts_faits.actif is 'Faux pour un haut fait retiré : il ne s''accorde plus, mais qui l''a le garde.';
comment on column commun.hauts_faits.ajoute_le is 'La date de l''ajout au catalogue.';

create table commun.recompenses (
  application  text not null,
  haut_fait    text not null,
  element_id   text not null references commun.elements (id),
  primary key (application, haut_fait, element_id),
  foreign key (application, haut_fait) references commun.hauts_faits (application, id)
);
create index recompenses_element on commun.recompenses (element_id);
alter table commun.recompenses enable row level security;
revoke all on commun.recompenses from public, anon, authenticated;
comment on table commun.recompenses is
  'Commun. Les éléments d''avatar que débloque chaque haut fait. Un élément peut être débloqué par plusieurs hauts faits, d''applications différentes. Données d''élèves : non.';
comment on column commun.recompenses.application is 'L''application du haut fait.';
comment on column commun.recompenses.haut_fait is 'L''identifiant du haut fait.';
comment on column commun.recompenses.element_id is 'L''élément débloqué.';

create table commun.hauts_faits_gagnes (
  compte_id    uuid not null references commun.comptes (id) on delete cascade,
  application  text not null,
  haut_fait    text not null,
  gagne_le     timestamptz not null default now(),
  par          text not null check (par in ('application', 'reprise', 'page', 'enseignant', 'seance')),
  primary key (compte_id, application, haut_fait),
  foreign key (application, haut_fait) references commun.hauts_faits (application, id)
);
alter table commun.hauts_faits_gagnes enable row level security;
revoke all on commun.hauts_faits_gagnes from public, anon, authenticated;
comment on table commun.hauts_faits_gagnes is
  'Commun. Les hauts faits gagnés par chaque élève, toutes applications réunies : une ligne par haut fait, sans nombre ni score. Vus par l''élève, ses camarades de classe et ses enseignant·e·s. Jamais effacés, sauf avec le compte. Données d''élèves : oui.';
comment on column commun.hauts_faits_gagnes.compte_id is 'Le compte de l''élève.';
comment on column commun.hauts_faits_gagnes.application is 'L''application du haut fait.';
comment on column commun.hauts_faits_gagnes.haut_fait is 'L''identifiant du haut fait.';
comment on column commun.hauts_faits_gagnes.gagne_le is 'La date où il a été gagné (la plus ancienne, après une fusion).';
comment on column commun.hauts_faits_gagnes.par is 'Comment il a été accordé : application, reprise (progression déjà enregistrée), page, enseignant, seance (la page projetée d''une séance).';

create table commun.elements_debloques (
  compte_id   uuid not null references commun.comptes (id) on delete cascade,
  element_id  text not null references commun.elements (id),
  origine     text not null default 'haut_fait' check (origine in ('haut_fait', 'achat')),
  depuis      timestamptz not null default now(),
  primary key (compte_id, element_id)
);
alter table commun.elements_debloques enable row level security;
revoke all on commun.elements_debloques from public, anon, authenticated;
comment on table commun.elements_debloques is
  'Commun. Les éléments d''avatar débloqués par chaque élève, par un haut fait ou par un achat. Gardés même si le catalogue change : on ne perd jamais ce qu''on a gagné ou acheté. Les éléments libres n''y sont pas. Données d''élèves : oui.';
comment on column commun.elements_debloques.compte_id is 'Le compte de l''élève.';
comment on column commun.elements_debloques.element_id is 'L''élément débloqué.';
comment on column commun.elements_debloques.origine is 'haut_fait : une récompense ; achat : acheté avec des crédits.';
comment on column commun.elements_debloques.depuis is 'La date du déblocage.';

-- -----------------------------------------------------------------------------
-- E6. L'XP : le barème, les activités reconnues, le journal
-- -----------------------------------------------------------------------------
create table commun.baremes (
  application      text not null references commun.applications (id),
  evenement        text not null check (evenement ~ '^[a-z_]{2,30}$'),
  nom              text not null check (char_length(nom) between 2 and 60),
  xp               smallint not null check (xp between 1 and 200),
  activite_connue  boolean not null default false,
  primary key (application, evenement)
);
alter table commun.baremes enable row level security;
revoke all on commun.baremes from public, anon, authenticated;
comment on table commun.baremes is
  'Commun. Le barème de l''XP : ce que rapporte chaque genre d''événement de chaque application. La page ne choisit jamais le montant. Écrit par les migrations. Données d''élèves : non.';
comment on column commun.baremes.application is 'L''application de l''événement.';
comment on column commun.baremes.evenement is 'Le genre d''événement (feuille_validee, quiz_termine, mission_reussie…).';
comment on column commun.baremes.nom is 'Le nom affiché dans le journal (« Feuille de TD validée en ligne »).';
comment on column commun.baremes.xp is 'L''XP rapportée par un événement, de 1 à 200.';
comment on column commun.baremes.activite_connue is 'Vrai si l''événement doit porter la clé d''une activité inscrite (table activites) : c''est le cas de tout ce qu''une page déclare elle-même.';

insert into commun.baremes (application, evenement, nom, xp, activite_connue) values
  ('td',            'feuille_validee',  'Feuille de TD validée en ligne',            30, true),
  ('td',            'exercice_valide',  'Exercice de TD validé en ligne',             5, true),
  ('quizz_nsi',     'cours_quiz_suivi', 'Cours-quiz suivi jusqu''au bout',            15, true),
  ('vacances',      'mini_jeu_fait',    'Mini-jeu du calendrier des vacances',        5, false),
  ('gombessa',      'mission_reussie',  'Mission réussie dans Expédition Gombessa',  10, false),
  ('court_circuit', 'challenge_reussi', 'Challenge réussi dans Court-circuit',       10, false),
  ('grand_oral',    'etape_dossier',    'Étape du dossier de Grand oral',            15, false),
  ('lagon',         'manche_jouee',     'Manche jouée dans Lagon Arena',              5, false),
  ('alien',         'exercice_reussi',  'Exercice réussi dans Alien Python',          5, false);

create table commun.activites (
  application  text not null,
  evenement    text not null,
  cle          text not null check (cle ~ '^[a-z0-9][a-z0-9:/_.-]{0,79}$'),
  nom          text not null check (char_length(nom) between 2 and 80),
  actif        boolean not null default true,
  primary key (application, cle),
  foreign key (application, evenement) references commun.baremes (application, evenement)
);
alter table commun.activites enable row level security;
revoke all on commun.activites from public, anon, authenticated;
comment on table commun.activites is
  'Commun. Les activités reconnues (une feuille de TD, un cours-quiz) : une page ne peut déclarer que ces clés, une seule fois par élève. Générée depuis la bibliothèque du site par un script. Données d''élèves : non.';
comment on column commun.activites.application is 'L''application de l''activité.';
comment on column commun.activites.evenement is 'Le genre d''événement qu''elle déclenche (son barème).';
comment on column commun.activites.cle is 'La clé de l''activité, unique dans l''application (td:poo-td1, quiz:piles-files).';
comment on column commun.activites.nom is 'Le nom affiché dans le journal.';
comment on column commun.activites.actif is 'Faux pour une activité retirée : elle ne rapporte plus rien.';

create table commun.xp_journal (
  id             uuid primary key default gen_random_uuid(),
  compte_id      uuid not null references commun.comptes (id) on delete cascade,
  application    text not null references commun.applications (id),
  evenement      text not null check (evenement ~ '^[a-z_]{2,30}$'),
  cle            text check (cle ~ '^[a-z0-9][a-z0-9:/_.-]{0,79}$'),
  xp             integer not null check (xp between -2000 and 200 and xp <> 0),
  motif          text check (char_length(motif) between 3 and 80),
  enseignant_id  uuid,
  par            text not null check (par in ('application', 'page', 'seance', 'haut_fait', 'enseignant', 'achat')),
  cree_le        timestamptz not null default now()
);
create unique index xp_journal_une_fois on commun.xp_journal (compte_id, application, cle) where cle is not null;
create index xp_journal_compte on commun.xp_journal (compte_id, cree_le);
alter table commun.xp_journal enable row level security;
revoke all on commun.xp_journal from public, anon, authenticated;
comment on table commun.xp_journal is
  'Commun. Le journal de l''XP de chaque élève : chaque gain (événement, haut fait, attribution d''un·e enseignant·e, avec son motif) et chaque achat (montant négatif). Une même activité ne rapporte qu''une fois. Vu par l''élève (sans total d''XP) et par ses enseignant·e·s. Données d''élèves : oui.';
comment on column commun.xp_journal.id is 'L''identifiant de la ligne, tiré au hasard.';
comment on column commun.xp_journal.compte_id is 'Le compte de l''élève.';
comment on column commun.xp_journal.application is 'L''application de l''événement (commun pour une attribution de l''enseignant·e ou un achat).';
comment on column commun.xp_journal.evenement is 'Le genre d''événement : celui du barème, ou haut_fait, attribution, achat.';
comment on column commun.xp_journal.cle is 'La clé qui empêche de gagner deux fois la même chose (td:poo-td1, hf:premier-circuit, achat:tete:casque-led) ; vide pour une attribution.';
comment on column commun.xp_journal.xp is 'L''XP gagnée (positive) ou les crédits dépensés (négatifs).';
comment on column commun.xp_journal.motif is 'Le motif court d''une attribution par l''enseignant·e (« Aide à un camarade »), 80 caractères au plus.';
comment on column commun.xp_journal.enseignant_id is 'L''enseignant·e qui a attribué l''XP (commun.enseignants, avec 0008) ; vide sinon.';
comment on column commun.xp_journal.par is 'D''où vient la ligne : application, page, seance (la page projetée d''une séance), haut_fait, enseignant, achat.';
comment on column commun.xp_journal.cree_le is 'La date de la ligne.';

create table commun.menage (
  seule_ligne  boolean primary key default true check (seule_ligne),
  fait_le      timestamptz not null default now()
);
alter table commun.menage enable row level security;
revoke all on commun.menage from public, anon, authenticated;
insert into commun.menage default values;
comment on table commun.menage is
  'Commun. La date du dernier ménage des comptes communs et des sessions (une seule ligne) : il se fait au plus une fois par heure. Données d''élèves : non.';
comment on column commun.menage.seule_ligne is 'Toujours vrai : garantit que la table n''a qu''une ligne.';
comment on column commun.menage.fait_le is 'La date du dernier ménage.';

-- -----------------------------------------------------------------------------
-- E7. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- La forme canonique d'un code : majuscules, sans accent ni séparateur.
create function commun.normaliser_code(p_code text)
returns text language sql immutable set search_path = '' as $$
  select regexp_replace(upper(translate(replace(replace(left(coalesce(p_code, ''), 80), 'œ', 'oe'), 'Œ', 'OE'),
    'àâäáãåçéèêëíìîïñóòôöõúùûüýÿÀÂÄÁÃÅÇÉÈÊËÍÌÎÏÑÓÒÔÖÕÚÙÛÜÝ',
    'aaaaaaceeeeiiiinooooouuuuyyAAAAAACEEEEIIIINOOOOOUUUUY')), '[^A-Z0-9]', '', 'g')
$$;

-- Un texte propre (espaces réduits, sans caractère de contrôle ni invisible),
-- de p_min à p_max caractères, sinon null.
create function commun.nettoyer_texte(p_texte text, p_min integer, p_max integer)
returns text language sql immutable set search_path = '' as $$
  select case when char_length(x.t) between p_min and p_max
               and x.t !~ ('[' || chr(1) || '-' || chr(31) || chr(127) || '-' || chr(159) || chr(173) || chr(8203) || '-' || chr(8207)
                           || chr(8232) || '-' || chr(8238) || chr(8288) || '-' || chr(8303) || chr(65279) || ']')
              then x.t end
  from (select btrim(regexp_replace(left(coalesce(p_texte, ''), 200), '\s+', ' ', 'g')) as t) x
$$;

-- Un prénom ou un pseudo propre (2 à 24 caractères), sinon null.
create function commun.nettoyer_pseudo(p_texte text)
returns text language sql immutable set search_path = '' as $$
  select commun.nettoyer_texte(p_texte, 2, 24)
$$;

-- Un code neuf de 2 mots et 3 chiffres, tiré sans biais dans la liste d'une
-- application (64 mots : un octet modulo 64 ; les chiffres par rejet).
create function commun.nouveau_code(p_app text, out code text, out code_affiche text)
language plpgsql volatile set search_path = '' as $$
declare b bytea; v integer; w1 text; w2 text; d text; essai integer := 0;
begin
  if (select count(*) from commun.mots m where m.application = p_app) <> 64 then
    raise exception 'La liste de mots de % n''a pas 64 mots.', p_app;
  end if;
  loop
    essai := essai + 1;
    if essai > 200 then raise exception 'Impossible de tirer un code libre.'; end if;
    b := extensions.gen_random_bytes(4);
    v := get_byte(b, 2) * 256 + get_byte(b, 3);
    continue when v >= 64000;
    select m.mot into w1 from commun.mots m where m.application = p_app and m.rang = get_byte(b, 0) % 64;
    select m.mot into w2 from commun.mots m where m.application = p_app and m.rang = get_byte(b, 1) % 64;
    d := lpad((v % 1000)::text, 3, '0');
    code := w1 || w2 || d;
    code_affiche := w1 || '-' || w2 || '-' || d;
    exit when not exists (select 1 from commun.codes c where c.code = nouveau_code.code);
  end loop;
end $$;

-- Ouvre une session : un nouveau jeton, 5 au plus par compte.
create function commun.ouvrir_session(p_compte uuid, p_garde_jours integer)
returns uuid language plpgsql volatile set search_path = '' as $$
declare j uuid;
begin
  insert into commun.sessions (compte_id, garde_jours)
  values (p_compte, case when p_garde_jours = 30 then 30 else 1 end)
  returning jeton into j;
  delete from commun.sessions s
   where s.compte_id = p_compte
     and s.jeton not in (select x.jeton from commun.sessions x where x.compte_id = p_compte order by x.vu_le desc limit 5);
  update commun.comptes c set vu_le = now() where c.id = p_compte;
  return j;
end $$;

-- Le compte d'un jeton valable (et la visite notée), sinon null.
create function commun.compte_par_jeton(p_jeton uuid)
returns uuid language plpgsql volatile set search_path = '' as $$
declare v uuid;
begin
  update commun.sessions s set vu_le = now()
   where s.jeton = p_jeton
     and ((s.garde_jours = 1 and s.cree_le > now() - interval '1 day')
          or (s.garde_jours = 30 and s.vu_le > now() - interval '30 days'))
  returning s.compte_id into v;
  if v is not null then
    update commun.comptes c set vu_le = now() where c.id = v and c.vu_le < now() - interval '10 minutes';
  end if;
  return v;
end $$;

-- Crée un compte commun (pseudo déjà nettoyé).
create function commun.creer_compte(p_pseudo text, p_origine text, p_provisoire boolean default false)
returns uuid language sql volatile set search_path = '' as $$
  insert into commun.comptes (pseudo, origine, pseudo_provisoire) values (p_pseudo, p_origine, p_provisoire) returning id
$$;

-- Ajoute une ligne au journal de l'XP et met à jour l'XP et les crédits.
-- Renvoie l'XP gagnée (0 si la clé a déjà rapporté, ou si le plafond du jour
-- est atteint). Seule cette fonction et commun.acheter écrivent le journal.
create function commun.crediter(p_compte uuid, p_app text, p_evenement text, p_cle text, p_xp integer,
                                p_par text, p_motif text default null, p_enseignant uuid default null)
returns integer language plpgsql volatile set search_path = '' as $$
declare v integer := p_xp; deja integer;
begin
  if p_compte is null or v is null or v <= 0 then return 0; end if;
  if p_par in ('application', 'page', 'seance') then
    -- Le plafond du jour, par application (hors hauts faits et attributions).
    select coalesce(sum(j.xp), 0) into deja from commun.xp_journal j
     where j.compte_id = p_compte and j.application = p_app and j.par in ('application', 'page', 'seance')
       and j.cree_le >= date_trunc('day', now(), 'Indian/Mayotte');
    v := least(v, greatest(0, (select a.plafond_xp_jour from commun.applications a where a.id = p_app) - deja));
    if v <= 0 then return 0; end if;
  end if;
  insert into commun.xp_journal (compte_id, application, evenement, cle, xp, motif, enseignant_id, par)
  values (p_compte, p_app, p_evenement, p_cle, v, p_motif, p_enseignant, p_par)
  on conflict (compte_id, application, cle) where cle is not null do nothing;
  if not found then return 0; end if;
  update commun.comptes c set xp = c.xp + v, credits = c.credits + v, vu_le = now() where c.id = p_compte;
  return v;
end $$;

-- Un événement d'une application : l'XP de son barème, une fois par clé.
create function commun.gagner_xp(p_compte uuid, p_app text, p_evenement text, p_cle text, p_par text)
returns integer language plpgsql volatile set search_path = '' as $$
declare b commun.baremes;
begin
  select x.* into b from commun.baremes x join commun.applications a on a.id = x.application and a.active
   where x.application = p_app and x.evenement = p_evenement;
  if b.application is null then return 0; end if;
  if b.activite_connue and not exists (select 1 from commun.activites t where t.application = p_app and t.cle = p_cle
                                         and t.evenement = p_evenement and t.actif) then
    return 0;
  end if;
  return commun.crediter(p_compte, p_app, p_evenement, p_cle, b.xp, p_par);
end $$;

-- Accorde des hauts faits à un compte, débloque leurs récompenses et
-- rapporte leur XP. p_par : application, reprise, page ou enseignant.
-- Seuls les hauts faits actifs, de l'application donnée et du bon genre
-- d'accord, sont accordés ; les autres identifiants sont ignorés. Renvoie
-- les nouveautés : {"hauts_faits": [...], "elements": [...], "credits": n}.
create function commun.accorder(p_compte uuid, p_app text, p_ids text[], p_par text)
returns jsonb language plpgsql volatile set search_path = '' as $$
declare r jsonb; h record; gain integer := 0; nouveaux text[];
begin
  if p_compte is null or p_ids is null or cardinality(p_ids) = 0 then
    return jsonb_build_object('hauts_faits', '[]'::jsonb, 'elements', '[]'::jsonb, 'credits', 0);
  end if;
  with n as (
    insert into commun.hauts_faits_gagnes (compte_id, application, haut_fait, par)
    select p_compte, x.application, x.id, p_par
      from commun.hauts_faits x
      join commun.applications a on a.id = x.application and a.active
     where x.application = p_app and x.id = any(p_ids[1:100]) and x.actif
       and x.accord = case p_par when 'enseignant' then 'enseignant' when 'page' then 'page' when 'seance' then 'seance' else 'serveur' end
    on conflict do nothing
    returning haut_fait
  )
  select coalesce(array_agg(n.haut_fait), '{}'::text[]) into nouveaux from n;
  if cardinality(nouveaux) = 0 then
    return jsonb_build_object('hauts_faits', '[]'::jsonb, 'elements', '[]'::jsonb, 'credits', 0);
  end if;
  insert into commun.elements_debloques (compte_id, element_id, origine)
  select distinct p_compte, r.element_id, 'haut_fait'
    from commun.recompenses r where r.application = p_app and r.haut_fait = any(nouveaux)
  on conflict do nothing;
  for h in select x.id, x.xp from commun.hauts_faits x where x.application = p_app and x.id = any(nouveaux) loop
    gain := gain + commun.crediter(p_compte, p_app, 'haut_fait', 'hf:' || h.id, h.xp, 'haut_fait');
  end loop;
  select jsonb_build_object(
    'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', x.application, 'id', x.id, 'nom', x.nom))
                               from commun.hauts_faits x where x.application = p_app and x.id = any(nouveaux)), '[]'::jsonb),
    'elements', coalesce((select jsonb_agg(distinct jsonb_build_object('id', e.id, 'nom', e.nom))
                            from commun.recompenses r join commun.elements e on e.id = r.element_id
                           where r.application = p_app and r.haut_fait = any(nouveaux)), '[]'::jsonb),
    'credits', gain)
  into r;
  update commun.comptes c set vu_le = now() where c.id = p_compte;
  return r;
end $$;

-- Les hauts faits que la progression déjà enregistrée dans une application
-- permet d'accorder (son connecteur fn_hauts_faits), ou une liste vide.
create function commun.reprise_ids(p_app text, p_eleve uuid)
returns text[] language plpgsql volatile set search_path = '' as $$
declare f regprocedure; v text[];
begin
  select a.fn_hauts_faits into f from commun.applications a where a.id = p_app and a.active;
  if f is null then return '{}'::text[]; end if;
  begin
    execute format('select %s($1)', f::oid::regproc) into v using p_eleve;
  exception when others then
    raise warning 'commun.reprise_ids : le connecteur de % a échoué (%)', p_app, sqlerrm;
  end;
  return coalesce(v, '{}'::text[]);
end $$;

-- Le compte commun relié au compte d'une application rattachée. S'il
-- n'existe pas, il est créé (pseudo du compte de l'application, provisoire si
-- l'application le demande) et relié ; avec p_reprise, la progression déjà
-- enregistrée est reprise aussitôt. Null si l'application n'a pas ce compte.
create function commun.compte_par_eleve_app(p_app text, p_eleve uuid, p_reprise boolean default true)
returns uuid language plpgsql volatile set search_path = '' as $$
declare a commun.applications; v uuid; v_pseudo text;
begin
  select l.compte_id into v from commun.liens l where l.application = p_app and l.eleve_app_id = p_eleve;
  if v is not null then return v; end if;
  select * into a from commun.applications x where x.id = p_app and x.active and x.mode = 'rattachee';
  if a.id is null or a.fn_par_id is null then return null; end if;
  execute format('select t.pseudo from %s($1) t limit 1', a.fn_par_id::oid::regproc) into v_pseudo using p_eleve;
  if v_pseudo is null then return null; end if;
  v := commun.creer_compte(coalesce(commun.nettoyer_pseudo(v_pseudo), 'Élève'), p_app, a.pseudo_a_confirmer);
  insert into commun.liens (application, eleve_app_id, compte_id) values (p_app, p_eleve, v);
  if p_reprise then
    perform commun.accorder(v, p_app, commun.reprise_ids(p_app, p_eleve), 'reprise');
  end if;
  return v;
end $$;

-- Le compte commun qu'ouvre un code, quelle que soit l'application qui l'a
-- donné : d'abord les codes du compte commun, puis les connecteurs des
-- applications rattachées. Null pour un code inconnu.
create function commun.compte_par_code(p_code text)
returns uuid language plpgsql volatile set search_path = '' as $$
declare c text := commun.normaliser_code(p_code); a record; v_eleve uuid; v uuid;
begin
  if c !~ '^[A-Z]{8,32}[0-9]{3,4}$' then return null; end if;
  select x.compte_id into v from commun.codes x where x.code = c;
  if v is not null then return v; end if;
  for a in select x.id, x.fn_par_code from commun.applications x
            where x.active and x.mode = 'rattachee' and x.fn_par_code is not null order by x.id loop
    -- Un connecteur en panne ne bloque pas les autres applications : il est
    -- sauté, et l'erreur part dans le journal de la base (avertissement).
    begin
      execute format('select t.eleve_id from %s($1) t limit 1', a.fn_par_code::oid::regproc) into v_eleve using c;
    exception when others then
      raise warning 'commun.compte_par_code : le connecteur de % a échoué (%)', a.id, sqlerrm;
      v_eleve := null;
    end;
    if v_eleve is not null then
      return commun.compte_par_eleve_app(a.id, v_eleve);
    end if;
  end loop;
  return null;
end $$;

-- L'application rattachée signale une visite de son élève : le compte
-- commun relié, s'il existe, reste vivant (ménage des 12 mois).
create function commun.visite_app(p_app text, p_eleve uuid)
returns void language sql volatile set search_path = '' as $$
  update commun.comptes c set vu_le = now()
    from commun.liens l
   where l.application = p_app and l.eleve_app_id = p_eleve and c.id = l.compte_id
     and c.vu_le < now() - interval '10 minutes'
$$;

-- L'application rattachée accorde des hauts faits à son élève (et, au
-- premier lien, ceux de sa progression déjà enregistrée), et lui fait gagner
-- l'XP de ses événements (p_evenements : [{"evenement": …, "cle": …}]).
-- Renvoie les nouveautés, pour que sa page les annonce.
create function commun.accorder_app(p_app text, p_eleve uuid, p_ids text[], p_evenements jsonb default null)
returns jsonb language plpgsql volatile set search_path = '' as $$
declare v uuid := commun.compte_par_eleve_app(p_app, p_eleve, false); r jsonb; e jsonb; gain integer := 0;
begin
  if v is null then return null; end if;
  r := commun.accorder(v, p_app, coalesce(p_ids, '{}'::text[]) || commun.reprise_ids(p_app, p_eleve), 'application');
  if jsonb_typeof(p_evenements) = 'array' then
    for e in select * from jsonb_array_elements(p_evenements) limit 50 loop
      gain := gain + commun.gagner_xp(v, p_app, left(e ->> 'evenement', 30), left(e ->> 'cle', 80), 'application');
    end loop;
  end if;
  return jsonb_set(r, '{credits}', to_jsonb((r ->> 'credits')::integer + gain));
end $$;

-- Vérifie un avatar (la description du moteur d'avatars) pour un compte.
-- Renvoie l'avatar propre, ou null. L'identité et les tenues sont libres pour
-- tout avatar : seule leur forme est vérifiée (un identifiant court, une
-- couleur), et une valeur que le moteur ne connaît pas n'est pas dessinée.
-- Un objet ou un compagnon doit être libre, gagné ou acheté par ce compte.
create function commun.verifier_avatar(p_compte uuid, p_avatar jsonb)
returns jsonb language plpgsql stable set search_path = '' as $$
declare k text; v jsonb;
begin
  if p_avatar is null or jsonb_typeof(p_avatar) <> 'object' or octet_length(p_avatar::text) > 600
     or (p_avatar ->> 'v') is distinct from '1'
     or exists (select 1 from jsonb_object_keys(p_avatar) x
                where x not in ('v', 'lignee', 'teint', 'corps', 'coiffure', 'cheveux', 'haut', 'bas', 'chaussures',
                                'objets', 'fauteuil', 'compagnon', 'couleurs')) then
    return null;
  end if;
  -- L'identité et les tenues : un identifiant court (ou, pour les cheveux, une couleur).
  for k, v in select * from jsonb_each(p_avatar - array['v', 'teint', 'objets', 'fauteuil', 'couleurs']) loop
    if jsonb_typeof(v) <> 'string' or (v #>> '{}') !~ '^([a-z0-9_]{1,30}|#[0-9a-fA-F]{6})$' then return null; end if;
  end loop;
  if p_avatar ? 'teint' and ((p_avatar ->> 'teint') !~ '^[1-8]$' or jsonb_typeof(p_avatar -> 'teint') <> 'number') then
    return null;
  end if;
  if p_avatar ? 'fauteuil' and jsonb_typeof(p_avatar -> 'fauteuil') <> 'boolean' then return null; end if;
  if p_avatar ? 'couleurs' then
    if jsonb_typeof(p_avatar -> 'couleurs') <> 'object' then return null; end if;
    for k, v in select * from jsonb_each(p_avatar -> 'couleurs') loop
      if k !~ '^[a-z_]{1,20}$' or jsonb_typeof(v) <> 'string'
         or (v #>> '{}') !~ '^([a-z0-9_]{1,30}|#[0-9a-fA-F]{6})$' then
        return null;
      end if;
    end loop;
  end if;
  -- Les objets : un par emplacement, aucun, ou un objet libre, gagné ou acheté.
  if p_avatar ? 'objets' then
    if jsonb_typeof(p_avatar -> 'objets') <> 'object' then return null; end if;
    for k, v in select * from jsonb_each(p_avatar -> 'objets') loop
      if jsonb_typeof(v) <> 'string'
         or not exists (select 1 from commun.emplacements m where m.id = k and m.genre = 'objet') then
        return null;
      end if;
      continue when (v #>> '{}') = 'aucun';
      if not exists (select 1 from commun.elements x
                      where x.id = k || ':' || (v #>> '{}')
                        and ((x.acces = 'libre' and x.actif)
                             or exists (select 1 from commun.elements_debloques d where d.compte_id = p_compte and d.element_id = x.id))) then
        return null;
      end if;
    end loop;
  end if;
  -- Le compagnon : aucun, ou un compagnon libre (le margouillat), gagné ou offert.
  if p_avatar ? 'compagnon' and (p_avatar ->> 'compagnon') is distinct from 'aucun' then
    if jsonb_typeof(p_avatar -> 'compagnon') <> 'string'
       or not exists (select 1 from commun.elements x
                       where x.id = 'compagnon:' || (p_avatar ->> 'compagnon')
                         and ((x.acces = 'libre' and x.actif)
                              or exists (select 1 from commun.elements_debloques d where d.compte_id = p_compte and d.element_id = x.id))) then
      return null;
    end if;
  end if;
  return p_avatar;
end $$;

-- La fiche d'un compte, pour l'élève lui-même ou elle-même : pseudo, avatar,
-- ses codes, ses applications, ses hauts faits, ses éléments, son solde de
-- crédits et son journal (les 100 dernières lignes). Jamais le total d'XP.
create function commun.fiche(p_compte uuid)
returns jsonb language plpgsql stable set search_path = '' as $$
declare c commun.comptes; codes jsonb := '[]'::jsonb; l record; v_code text;
begin
  select * into c from commun.comptes x where x.id = p_compte;
  if c.id is null then return null; end if;
  select coalesce(jsonb_agg(jsonb_build_object('application', x.application, 'code_affiche', x.code_affiche, 'principal', x.principal)
                            order by x.principal desc, x.cree_le), '[]'::jsonb)
    into codes from commun.codes x where x.compte_id = p_compte;
  for l in select li.application, li.eleve_app_id, a.fn_par_id
             from commun.liens li join commun.applications a on a.id = li.application
            where li.compte_id = p_compte and a.fn_par_id is not null order by li.depuis loop
    v_code := null;
    begin
      execute format('select t.code_affiche from %s($1) t limit 1', l.fn_par_id::oid::regproc) into v_code using l.eleve_app_id;
    exception when others then
      raise warning 'commun.fiche : le connecteur de % a échoué (%)', l.application, sqlerrm;
    end;
    if v_code is not null then
      codes := codes || jsonb_build_array(jsonb_build_object('application', l.application, 'code_affiche', v_code, 'principal', false));
    end if;
  end loop;
  return jsonb_build_object(
    'pseudo', c.pseudo,
    'pseudo_provisoire', c.pseudo_provisoire,
    'avatar', c.avatar,
    'credits', c.credits,
    'codes', codes,
    'applications', coalesce((select jsonb_agg(distinct li.application) from commun.liens li where li.compte_id = p_compte), '[]'::jsonb),
    'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait, 'nom', h.nom,
                                                                 'description', h.description, 'gagne_le', g.gagne_le)
                                              order by g.gagne_le)
                               from commun.hauts_faits_gagnes g
                               join commun.hauts_faits h on h.application = g.application and h.id = g.haut_fait
                              where g.compte_id = p_compte), '[]'::jsonb),
    'elements', coalesce((select jsonb_agg(d.element_id order by d.depuis) from commun.elements_debloques d where d.compte_id = p_compte), '[]'::jsonb),
    'trophees', coalesce((select jsonb_agg(jsonb_build_object('element', d.element_id, 'origine', d.origine, 'depuis', d.depuis) order by d.depuis)
                            from commun.elements_debloques d where d.compte_id = p_compte and d.origine <> 'achat'), '[]'::jsonb),
    'journal', coalesce((select jsonb_agg(jsonb_build_object('le', j.cree_le, 'application', j.application, 'evenement', j.evenement,
                                                            'nom', coalesce(t.nom, b.nom), 'credits', j.xp, 'motif', j.motif) order by j.cree_le desc)
                           from (select * from commun.xp_journal x where x.compte_id = p_compte order by x.cree_le desc limit 100) j
                           left join commun.baremes b on b.application = j.application and b.evenement = j.evenement
                           left join commun.activites t on t.application = j.application and t.cle = j.cle), '[]'::jsonb),
    'cree_le', c.cree_le);
end $$;

-- Fusionne deux comptes : p_absorber rejoint p_garder. Rien n'est perdu : les
-- liens, les codes (qui restent valables), les hauts faits, les éléments et le
-- journal passent sur le compte gardé ; une activité comptée deux fois ne
-- l'est plus qu'une ; l'XP et les crédits sont recalculés depuis le journal.
create function commun.fusionner(p_garder uuid, p_absorber uuid)
returns void language plpgsql volatile set search_path = '' as $$
declare a record;
begin
  if p_garder is null or p_absorber is null or p_garder = p_absorber then return; end if;
  for a in select x.fn_fusion from commun.applications x where x.mode = 'native' and x.fn_fusion is not null loop
    execute format('select %s($1, $2)', a.fn_fusion::oid::regproc) using p_garder, p_absorber;
  end loop;
  update commun.liens set compte_id = p_garder where compte_id = p_absorber;
  update commun.codes set compte_id = p_garder, principal = false where compte_id = p_absorber;
  insert into commun.hauts_faits_gagnes (compte_id, application, haut_fait, gagne_le, par)
  select p_garder, g.application, g.haut_fait, g.gagne_le, g.par from commun.hauts_faits_gagnes g where g.compte_id = p_absorber
  on conflict (compte_id, application, haut_fait) do update set gagne_le = least(commun.hauts_faits_gagnes.gagne_le, excluded.gagne_le);
  insert into commun.elements_debloques (compte_id, element_id, origine, depuis)
  select p_garder, d.element_id, d.origine, d.depuis from commun.elements_debloques d where d.compte_id = p_absorber
  on conflict (compte_id, element_id) do update set depuis = least(commun.elements_debloques.depuis, excluded.depuis);
  update commun.xp_journal j set compte_id = p_garder
   where j.compte_id = p_absorber
     and (j.cle is null or not exists (select 1 from commun.xp_journal k where k.compte_id = p_garder
                                         and k.application = j.application and k.cle = j.cle));
  delete from commun.comptes where id = p_absorber;
  update commun.comptes c set
    xp = coalesce((select sum(j.xp) from commun.xp_journal j where j.compte_id = p_garder and j.xp > 0), 0),
    credits = greatest(0, coalesce((select sum(j.xp) from commun.xp_journal j where j.compte_id = p_garder), 0)),
    vu_le = now()
  where c.id = p_garder;
end $$;

-- Le ménage, au plus une fois par heure : les sessions expirées, et les
-- comptes sans visite depuis 12 mois (avec tout ce qui leur appartient).
create function commun.menage_si_besoin()
returns void language plpgsql volatile set search_path = '' as $$
begin
  update commun.menage set fait_le = now() where fait_le < now() - interval '1 hour';
  if not found then return; end if;
  delete from commun.sessions s
   where (s.garde_jours = 1 and s.cree_le < now() - interval '1 day')
      or (s.garde_jours = 30 and s.vu_le < now() - interval '30 days');
  delete from commun.comptes c where c.vu_le < now() - interval '12 months';
end $$;

revoke all on function commun.normaliser_code(text), commun.nettoyer_texte(text, integer, integer), commun.nettoyer_pseudo(text),
  commun.nouveau_code(text), commun.ouvrir_session(uuid, integer), commun.compte_par_jeton(uuid),
  commun.creer_compte(text, text, boolean), commun.crediter(uuid, text, text, text, integer, text, text, uuid),
  commun.gagner_xp(uuid, text, text, text, text), commun.accorder(uuid, text, text[], text), commun.reprise_ids(text, uuid),
  commun.compte_par_eleve_app(text, uuid, boolean), commun.compte_par_code(text), commun.visite_app(text, uuid),
  commun.accorder_app(text, uuid, text[], jsonb), commun.verifier_avatar(uuid, jsonb), commun.fiche(uuid),
  commun.fusionner(uuid, uuid), commun.menage_si_besoin()
  from public, anon, authenticated;

comment on function commun.normaliser_code(text) is 'Commun, interne. La forme canonique d''un code : majuscules, accents et séparateurs retirés (spécification des codes, § 1.2).';
comment on function commun.nettoyer_texte(text, integer, integer) is 'Commun, interne. Un texte de p_min à p_max caractères, espaces réduits, sans caractère de contrôle ni invisible ; sinon null.';
comment on function commun.nettoyer_pseudo(text) is 'Commun, interne. Un prénom ou un pseudo de 2 à 24 caractères (commun.nettoyer_texte) ; sinon null.';
comment on function commun.nouveau_code(text) is 'Commun, interne. Un code neuf de 2 mots et 3 chiffres, tiré sans biais dans la liste de mots d''une application, libre dans commun.codes.';
comment on function commun.ouvrir_session(uuid, integer) is 'Commun, interne. Un nouveau jeton de session (1 ou 30 jours) ; 5 jetons au plus par compte, le plus ancien part.';
comment on function commun.compte_par_jeton(uuid) is 'Commun, interne. Le compte d''un jeton encore valable, sinon null ; note l''usage du jeton et la visite.';
comment on function commun.creer_compte(text, text, boolean) is 'Commun, interne. Crée un compte commun avec un pseudo déjà nettoyé, son application d''origine, et un pseudo provisoire ou non.';
comment on function commun.crediter(uuid, text, text, text, integer, text, text, uuid) is 'Commun, interne. Écrit un gain au journal de l''XP (une fois par clé, dans le plafond du jour pour les événements) et augmente l''XP et les crédits ; renvoie l''XP gagnée.';
comment on function commun.gagner_xp(uuid, text, text, text, text) is 'Commun, interne. L''XP d''un événement d''après le barème, une fois par clé ; une page ne peut déclarer qu''une activité inscrite.';
comment on function commun.accorder(uuid, text, text[], text) is 'Commun, interne. Accorde des hauts faits (selon leur genre d''accord), débloque leurs récompenses, rapporte leur XP, et renvoie les nouveautés.';
comment on function commun.reprise_ids(text, uuid) is 'Commun, interne. Les hauts faits que la progression déjà enregistrée dans une application permet d''accorder (connecteur fn_hauts_faits).';
comment on function commun.compte_par_eleve_app(text, uuid, boolean) is 'Commun, interne. Le compte commun relié au compte d''une application rattachée ; le crée et le relie s''il manque, et reprend alors la progression déjà enregistrée (p_reprise).';
comment on function commun.compte_par_code(text) is 'Commun, interne. Le compte commun qu''ouvre un code, né sur le site, dans une application native ou dans une application rattachée (par son connecteur) ; null si inconnu.';
comment on function commun.visite_app(text, uuid) is 'Commun, interne. Appelée par une application rattachée quand son élève entre : le compte commun relié reste vivant.';
comment on function commun.accorder_app(text, uuid, text[], jsonb) is 'Commun, interne. Appelée par une fonction d''une application rattachée, après sa propre vérification : hauts faits, reprise au premier lien, et XP de ses événements.';
comment on function commun.verifier_avatar(uuid, jsonb) is 'Commun, interne. L''avatar (description du moteur d''avatars, 600 octets au plus) si ses clés sont connues, ses valeurs bien formées, et chaque objet et le compagnon libres ou débloqués pour ce compte ; sinon null. Aucune vérification de lignée ni de genre.';
comment on function commun.fiche(uuid) is 'Commun, interne. La fiche d''un compte pour l''élève : pseudo, avatar, codes, applications, hauts faits (avec leur nom, secrets gagnés compris), éléments, trophées, solde de crédits et journal ; jamais le total d''XP.';
comment on function commun.fusionner(uuid, uuid) is 'Commun, interne. Réunit deux comptes de la même personne : tout passe sur le compte gardé, les codes restent valables, une activité n''est comptée qu''une fois.';
comment on function commun.menage_si_besoin() is 'Commun, interne. Au plus une fois par heure : efface les sessions expirées et les comptes sans visite depuis 12 mois.';

-- -----------------------------------------------------------------------------
-- E8. Les fonctions d'entrée, appelées par la page élève du site et par les
--    pages des applications : anon seul. Un échec répond { ok: false,
--    message }, jamais par une exception.
-- -----------------------------------------------------------------------------

-- Créer son code sur le site.
create function public.commun_creer(p_pseudo text, p_garde_jours integer default 1)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v_pseudo text := commun.nettoyer_pseudo(p_pseudo); v uuid; n record; j uuid;
begin
  if not commun.essai_permis('commun', 'creation', 60) then
    return jsonb_build_object('ok', false, 'message', 'Trop de comptes créés depuis ce réseau en une heure. Attends un peu.');
  end if;
  if v_pseudo is null then
    return jsonb_build_object('ok', false, 'message', 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).');
  end if;
  perform commun.menage_si_besoin();
  perform commun.noter_echec('commun', 'creation');
  v := commun.creer_compte(v_pseudo, 'commun');
  select * into n from commun.nouveau_code('commun');
  insert into commun.codes (code, code_affiche, compte_id, application) values (n.code, n.code_affiche, v, 'commun');
  j := commun.ouvrir_session(v, p_garde_jours);
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche, 'jeton', j, 'fiche', commun.fiche(v));
end $$;

-- Entrer avec n'importe lequel de ses codes.
create function public.commun_entrer(p_code text, p_garde_jours integer default 1)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid;
begin
  if not commun.essai_permis('commun', 'eleve', 20) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu, ou demande ton code à ton enseignant·e.');
  end if;
  v := commun.compte_par_code(left(coalesce(p_code, ''), 80));
  if v is null then
    perform commun.noter_echec('commun', 'eleve');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Ce code n''existe pas. Vérifie-le dans ton cahier.');
  end if;
  perform commun.menage_si_besoin();
  return jsonb_build_object('ok', true, 'jeton', commun.ouvrir_session(v, p_garde_jours), 'fiche', commun.fiche(v));
end $$;

-- Reprendre avec son jeton.
create function public.commun_reprise(p_jeton uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton);
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  perform commun.menage_si_besoin();
  return jsonb_build_object('ok', true, 'fiche', commun.fiche(v));
end $$;

-- Le catalogue public : applications, emplacements, éléments (et leurs
-- prix), hauts faits, récompenses et barème. Aucune donnée d'élève.
create function public.commun_catalogue()
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object(
    'version', 1,
    'applications', coalesce((select jsonb_agg(jsonb_build_object('id', a.id, 'nom', a.nom, 'adresse', a.adresse) order by a.id)
                                from commun.applications a where a.active), '[]'::jsonb),
    'emplacements', (select jsonb_agg(jsonb_build_object('id', m.id, 'nom', m.nom, 'genre', m.genre)
                                      order by m.ordre, m.id) from commun.emplacements m),
    'elements', coalesce((select jsonb_agg(jsonb_build_object('id', e.id, 'emplacement', e.emplacement, 'famille', e.famille, 'nom', e.nom,
                                   'description', e.description, 'acces', e.acces, 'prix', e.prix, 'actif', e.actif)
                                   order by e.emplacement, e.ordre, e.id) from commun.elements e), '[]'::jsonb),
    'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', h.application, 'id', h.id,
                                   'nom', case when h.secret then null else h.nom end,
                                   'description', case when h.secret then null else h.description end,
                                   'indice', h.indice, 'categorie', h.categorie, 'secret', h.secret, 'accord', h.accord,
                                   'xp', h.xp, 'actif', h.actif,
                                   'recompenses', coalesce((select jsonb_agg(r.element_id order by r.element_id) from commun.recompenses r
                                                             where r.application = h.application and r.haut_fait = h.id and not h.secret), '[]'::jsonb))
                                   order by h.application, h.ordre, h.id) from commun.hauts_faits h), '[]'::jsonb),
    'bareme', coalesce((select jsonb_agg(jsonb_build_object('application', b.application, 'evenement', b.evenement, 'nom', b.nom, 'credits', b.xp)
                               order by b.application, b.evenement) from commun.baremes b), '[]'::jsonb))
$$;

-- Porter un avatar.
create function public.commun_porter(p_jeton uuid, p_avatar jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); a jsonb;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if p_avatar is null or octet_length(p_avatar::text) > 600 then
    return jsonb_build_object('ok', false, 'message', 'Cet avatar est trop lourd.');
  end if;
  a := commun.verifier_avatar(v, p_avatar);
  if a is null then
    return jsonb_build_object('ok', false, 'message', 'Un objet ou un compagnon n''est pas encore à toi, ou n''est pas à sa place : ton avatar n''a pas changé.');
  end if;
  update commun.comptes c set avatar = a where c.id = v;
  return jsonb_build_object('ok', true, 'avatar', a);
end $$;

-- Acheter une apparence avec ses crédits. Un achat ne se rembourse pas, et
-- ce qui est acheté ne se perd jamais.
create function public.commun_acheter(p_jeton uuid, p_element text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); e commun.elements; reste integer;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  select * into e from commun.elements x where x.id = left(p_element, 62) and x.acces = 'credits' and x.actif;
  if e.id is null then
    return jsonb_build_object('ok', false, 'message', 'Cet élément ne s''achète pas.');
  end if;
  if exists (select 1 from commun.elements_debloques d where d.compte_id = v and d.element_id = e.id) then
    return jsonb_build_object('ok', false, 'message', 'Tu l''as déjà.');
  end if;
  update commun.comptes c set credits = c.credits - e.prix where c.id = v and c.credits >= e.prix returning c.credits into reste;
  if reste is null then
    return jsonb_build_object('ok', false, 'message', 'Pas encore assez de crédits pour celui-ci.');
  end if;
  insert into commun.elements_debloques (compte_id, element_id, origine) values (v, e.id, 'achat');
  insert into commun.xp_journal (compte_id, application, evenement, cle, xp, par)
  values (v, 'commun', 'achat', 'achat:' || e.id, -e.prix, 'achat');
  return jsonb_build_object('ok', true, 'element', e.id, 'credits', reste);
end $$;

-- Changer de prénom ou de pseudo (et confirmer un pseudo provisoire).
create function public.commun_renommer(p_jeton uuid, p_pseudo text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); p text := commun.nettoyer_pseudo(p_pseudo);
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if p is null then
    return jsonb_build_object('ok', false, 'message', 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).');
  end if;
  update commun.comptes c set pseudo = p, pseudo_provisoire = false where c.id = v;
  return jsonb_build_object('ok', true, 'pseudo', p);
end $$;

-- Réunir un autre de ses codes (d'une autre application) à ce compte.
create function public.commun_lier_code(p_jeton uuid, p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); autre uuid;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if not commun.essai_permis('commun', 'eleve', 20) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  autre := commun.compte_par_code(left(coalesce(p_code, ''), 80));
  if autre is null then
    perform commun.noter_echec('commun', 'eleve');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Ce code n''existe pas. Vérifie-le dans ton cahier.');
  end if;
  if autre = v then
    return jsonb_build_object('ok', true, 'message', 'Ce code ouvre déjà ton compte.', 'fiche', commun.fiche(v));
  end if;
  perform commun.fusionner(v, autre);
  return jsonb_build_object('ok', true, 'message', 'Tes deux codes ouvrent maintenant le même compte, avec tout ce que tu as gagné.', 'fiche', commun.fiche(v));
end $$;

-- Une page sans serveur (feuille de TD, QuizzNSI, calendrier) déclare une
-- activité faite : l'XP de son barème, une fois par activité inscrite.
create function public.commun_evenement_page(p_jeton uuid, p_application text, p_evenement text, p_cle text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); a text := left(p_application, 30); g integer;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Entre ton code pour garder tes crédits.');
  end if;
  if not exists (select 1 from commun.applications x where x.id = a and x.active and x.accord_par_page) then
    return jsonb_build_object('ok', false, 'message', 'Cette page ne donne pas de crédits.');
  end if;
  g := commun.gagner_xp(v, a, left(p_evenement, 30), left(p_cle, 80), 'page');
  return jsonb_build_object('ok', true, 'credits_gagnes', g,
    'message', case when g > 0 then 'Bien joué : c''est gardé.' else 'C''est déjà gardé (une activité ne compte qu''une fois).' end);
end $$;

-- Une page sans serveur accorde l'un de ses hauts faits de genre « page ».
create function public.commun_haut_fait_page(p_jeton uuid, p_application text, p_haut_fait text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton);
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if not exists (select 1 from commun.applications a where a.id = left(p_application, 30) and a.active and a.accord_par_page) then
    return jsonb_build_object('ok', false, 'message', 'Cette application n''accorde pas de haut fait depuis sa page.');
  end if;
  return jsonb_build_object('ok', true, 'nouveautes', commun.accorder(v, left(p_application, 30), array[left(p_haut_fait, 40)], 'page'));
end $$;

-- « Ce n'est pas moi » ou « Me déconnecter » : le jeton de cet appareil disparaît.
create function public.commun_quitter(p_jeton uuid)
returns jsonb language sql volatile security definer set search_path = '' as $$
  with d as (delete from commun.sessions s where s.jeton = p_jeton returning 1)
  select jsonb_build_object('ok', true)
$$;

-- Effacer son compte commun (et, si demandé, ses comptes dans les
-- applications qui le permettent). La confirmation est le mot EFFACER.
create function public.commun_effacer_moi(p_jeton uuid, p_confirmation text, p_partout boolean default false)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); l record; restent jsonb := '[]'::jsonb;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if coalesce(upper(btrim(p_confirmation)), '') <> 'EFFACER' then
    return jsonb_build_object('ok', false, 'message', 'Écris EFFACER pour confirmer.');
  end if;
  for l in select li.application, li.eleve_app_id, a.fn_effacer, a.nom
             from commun.liens li join commun.applications a on a.id = li.application where li.compte_id = v loop
    if p_partout and l.fn_effacer is not null then
      execute format('select %s($1)', l.fn_effacer::oid::regproc) using l.eleve_app_id;
    else
      restent := restent || to_jsonb(l.nom);
    end if;
  end loop;
  delete from commun.comptes c where c.id = v;
  return jsonb_build_object('ok', true, 'restent', restent,
    'message', case when jsonb_array_length(restent) = 0 then 'Ton compte commun est effacé.'
                    else 'Ton compte commun est effacé. Tes comptes de ces applications restent : efface-les depuis chacune.' end);
end $$;

revoke all on function public.commun_creer(text, integer), public.commun_entrer(text, integer), public.commun_reprise(uuid),
  public.commun_catalogue(), public.commun_porter(uuid, jsonb), public.commun_acheter(uuid, text), public.commun_renommer(uuid, text),
  public.commun_lier_code(uuid, text), public.commun_evenement_page(uuid, text, text, text),
  public.commun_haut_fait_page(uuid, text, text), public.commun_quitter(uuid), public.commun_effacer_moi(uuid, text, boolean)
  from public, anon, authenticated;
grant execute on function public.commun_creer(text, integer), public.commun_entrer(text, integer), public.commun_reprise(uuid),
  public.commun_catalogue(), public.commun_porter(uuid, jsonb), public.commun_acheter(uuid, text), public.commun_renommer(uuid, text),
  public.commun_lier_code(uuid, text), public.commun_evenement_page(uuid, text, text, text),
  public.commun_haut_fait_page(uuid, text, text), public.commun_quitter(uuid), public.commun_effacer_moi(uuid, text, boolean)
  to anon;

comment on function public.commun_creer(text, integer) is 'Compte commun, entrée. Crée un compte avec un prénom ou un pseudo et renvoie son code (2 mots, 3 chiffres), un jeton et la fiche. 60 créations par heure et par réseau.';
comment on function public.commun_entrer(text, integer) is 'Compte commun, entrée. Entre avec un code né sur le site, ou avec le code d''une application branchée (son connecteur) ; renvoie un jeton et la fiche. 20 échecs par heure et par réseau.';
comment on function public.commun_reprise(uuid) is 'Compte commun, entrée. La fiche de l''élève, avec son jeton.';
comment on function public.commun_catalogue() is 'Compte commun, entrée. Le catalogue public des applications, emplacements, éléments, hauts faits et du barème ; aucune donnée d''élève.';
comment on function public.commun_porter(uuid, jsonb) is 'Compte commun, entrée. Change l''avatar porté, après vérification de chaque élément.';
comment on function public.commun_acheter(uuid, text) is 'Compte commun, entrée. Achète une apparence avec ses crédits ; sans remboursement, et jamais perdue.';
comment on function public.commun_renommer(uuid, text) is 'Compte commun, entrée. Change le prénom ou le pseudo du compte commun (et confirme un pseudo provisoire).';
comment on function public.commun_lier_code(uuid, text) is 'Compte commun, entrée. Réunit au compte un autre code de l''élève : les deux comptes fusionnent, rien n''est perdu.';
comment on function public.commun_evenement_page(uuid, text, text, text) is 'Compte commun, entrée. Une page sans serveur déclare une activité inscrite faite (feuille de TD, cours-quiz, mini-jeu) : les crédits du barème, une fois, dans le plafond du jour.';
comment on function public.commun_haut_fait_page(uuid, text, text) is 'Compte commun, entrée. Une page sans serveur (accord_par_page) accorde l''un de ses hauts faits de genre page.';
comment on function public.commun_quitter(uuid) is 'Compte commun, entrée. Supprime le jeton de cet appareil (« Ce n''est pas moi », « Me déconnecter »).';
comment on function public.commun_effacer_moi(uuid, text, boolean) is 'Compte commun, entrée. Efface le compte commun, ses hauts faits, son avatar et son journal ; avec p_partout, aussi les comptes des applications qui le permettent.';

-- -----------------------------------------------------------------------------
-- E9. Contrôle : rien d'ouvert à l'API. Sinon, arrêt : rien n'est appliqué.
-- -----------------------------------------------------------------------------
do $$
begin
  if has_schema_privilege('anon', 'commun', 'usage') or has_schema_privilege('authenticated', 'commun', 'usage') then
    raise exception 'Le schéma commun est ouvert à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction de commun est appelable par anon ou par authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'v')
             and (has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de commun est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r' and not c.relrowsecurity) then
    raise exception 'Une table de commun n''a pas la RLS : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%'
             and (has_function_privilege('authenticated', p.oid, 'execute') or not has_function_privilege('anon', p.oid, 'execute')
                  or not p.prosecdef or p.proconfig is null)) then
    raise exception 'Une fonction commun_ n''a pas les bons droits ou son search_path : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from commun.emplacements) <> 9 or not exists (select 1 from commun.elements where id = 'compagnon:margouillat' and acces = 'libre') then
    raise exception 'Les 9 emplacements et le margouillat de départ sont attendus : arrêt, rien n''a été modifié.';
  end if;
  if commun.verifier_avatar(gen_random_uuid(), '{"v": 1, "lignee": "humain", "teint": 5, "corps": "moyenne", "coiffure": "court", "cheveux": "noirs", "haut": "tshirt", "bas": "pantalon", "chaussures": "baskets", "objets": {"tete": "aucun", "visage": "aucun", "cou": "aucun", "dos": "aucun", "main": "aucun", "epaule": "aucun", "pieds": "aucun", "autour": "aucun"}, "fauteuil": false, "compagnon": "margouillat", "couleurs": {"haut": "canard", "bas": "anthracite", "accent": "cyan", "chaussures": "blanches", "yeux": "bruns"}}'::jsonb) is null then
    raise exception 'L''avatar de départ est refusé par commun.verifier_avatar : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from commun.mots where application = 'commun') <> 64 then
    raise exception 'La liste des mots du site doit avoir 64 mots : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- =============================================================================
-- F. L'espace commun des enseignant·e·s et les classes communes (migration 0008)
-- =============================================================================
do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.comptes') is null or to_regclass('commun.xp_journal') is null then
    raise exception 'Le compte commun (0007, version 2) manque : l''appliquer d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if to_regclass('commun.enseignants') is not null or to_regclass('commun.classes') is not null then
    raise exception 'Les tables des enseignant·e·s ou des classes existent déjà : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- F1. Les tables
-- -----------------------------------------------------------------------------
create table commun.enseignants (
  id              uuid primary key default gen_random_uuid(),
  code_empreinte  text not null unique check (code_empreinte ~ '^[0-9a-f]{64}$'),
  nom             text not null check (char_length(nom) between 2 and 40),
  etablissement   text check (char_length(etablissement) between 2 and 80),
  cree_le         timestamptz not null default now(),
  vu_le           timestamptz not null default now()
);
alter table commun.enseignants enable row level security;
revoke all on commun.enseignants from public, anon, authenticated;
comment on table commun.enseignants is
  'Commun. Un espace par enseignant·e, pour toutes les applications : le nom affiché aux élèves, l''établissement (facultatif) et l''empreinte de son code (3 mots et 4 chiffres, montré une seule fois, gardé nulle part en clair). Ouvert à tout·e collègue. Supprimé seulement par l''enseignant·e. Données d''élèves : non.';
comment on column commun.enseignants.id is 'L''identifiant de l''espace, tiré au hasard.';
comment on column commun.enseignants.code_empreinte is 'L''empreinte SHA-256 de la forme canonique du code : on retrouve l''espace à partir du code, jamais le code à partir de l''empreinte.';
comment on column commun.enseignants.nom is 'Le nom affiché aux élèves (« Mme Ali », « M. B. »), choisi par l''enseignant·e.';
comment on column commun.enseignants.etablissement is 'L''établissement, facultatif.';
comment on column commun.enseignants.cree_le is 'La date de création de l''espace.';
comment on column commun.enseignants.vu_le is 'La date de la dernière ouverture de l''espace.';

create table commun.enseignants_liens (
  application        text not null references commun.applications (id),
  enseignant_app_id  uuid not null,
  enseignant_id      uuid not null references commun.enseignants (id) on delete cascade,
  depuis             timestamptz not null default now(),
  primary key (application, enseignant_app_id)
);
create index enseignants_liens_enseignant on commun.enseignants_liens (enseignant_id);
alter table commun.enseignants_liens enable row level security;
revoke all on commun.enseignants_liens from public, anon, authenticated;
comment on table commun.enseignants_liens is
  'Commun. Les espaces enseignant·e·s des applications reliés à chaque espace commun : le code commun ouvre l''espace de chaque application, et l''ancien code de l''application reste valable. Données d''élèves : non.';
comment on column commun.enseignants_liens.application is 'L''application.';
comment on column commun.enseignants_liens.enseignant_app_id is 'L''identifiant de l''espace dans cette application (grand_oral.enseignants.id, gb_profs.id…).';
comment on column commun.enseignants_liens.enseignant_id is 'L''espace commun relié.';
comment on column commun.enseignants_liens.depuis is 'La date du lien.';

create table commun.classes (
  id             uuid primary key default gen_random_uuid(),
  enseignant_id  uuid not null references commun.enseignants (id) on delete cascade,
  nom            text not null check (char_length(nom) between 2 and 40),
  code           text not null unique check (code ~ '^[A-HJ-NP-Z]{4}$'),
  ouverte        boolean not null default true,
  applications   text[] not null default '{}'::text[] check (cardinality(applications) <= 20),
  cree_le        timestamptz not null default now()
);
create index classes_enseignant on commun.classes (enseignant_id);
alter table commun.classes enable row level security;
revoke all on commun.classes from public, anon, authenticated;
comment on table commun.classes is
  'Commun. Les classes communes de chaque enseignant·e : nom, code de classe public (4 lettres, dans le lien et le QR code), inscriptions ouvertes ou fermées, applications de la classe. Aucun plafond du nombre d''élèves. Supprimée seulement par l''enseignant·e ; les comptes des élèves restent. Données d''élèves : non.';
comment on column commun.classes.id is 'L''identifiant de la classe, tiré au hasard.';
comment on column commun.classes.enseignant_id is 'L''espace de l''enseignant·e de la classe.';
comment on column commun.classes.nom is 'Le nom de la classe (« TNSI 2 »).';
comment on column commun.classes.code is 'Le code de classe, public : 4 lettres sans I ni O (spécification des codes, § 1.1). Lien : …/eleve/?classe=CODE.';
comment on column commun.classes.ouverte is 'Vrai si l''on peut encore rejoindre la classe par son lien.';
comment on column commun.classes.applications is 'Les applications de la classe (identifiants de commun.applications) : la page de l''élève montre leurs hauts faits à gagner.';
comment on column commun.classes.cree_le is 'La date de création de la classe.';

create table commun.inscriptions (
  classe_id  uuid not null references commun.classes (id) on delete cascade,
  compte_id  uuid not null references commun.comptes (id) on delete cascade,
  depuis     timestamptz not null default now(),
  primary key (classe_id, compte_id)
);
create index inscriptions_compte on commun.inscriptions (compte_id);
alter table commun.inscriptions enable row level security;
revoke all on commun.inscriptions from public, anon, authenticated;
comment on table commun.inscriptions is
  'Commun. Les élèves de chaque classe commune (un·e élève peut être dans plusieurs classes) : c''est ce qui borne ce que voit un·e élève de ses camarades, et ce que voit l''enseignant·e. Effacée avec la classe ou le compte. Données d''élèves : oui (l''appartenance à une classe).';
comment on column commun.inscriptions.classe_id is 'La classe.';
comment on column commun.inscriptions.compte_id is 'Le compte de l''élève.';
comment on column commun.inscriptions.depuis is 'La date d''arrivée dans la classe.';

create table commun.classes_liens (
  classe_id    uuid not null references commun.classes (id) on delete cascade,
  application  text not null references commun.applications (id),
  reference    text not null check (reference ~ '^[A-Za-z0-9_-]{1,64}$'),
  primary key (classe_id, application, reference)
);
alter table commun.classes_liens enable row level security;
revoke all on commun.classes_liens from public, anon, authenticated;
comment on table commun.classes_liens is
  'Commun. Les classes ou salles des applications rattachées à une classe commune : la page de la classe renvoie vers le tableau de bord de chacune (adresse_prof de l''application, puis #classe=référence). Données d''élèves : non.';
comment on column commun.classes_liens.classe_id is 'La classe commune.';
comment on column commun.classes_liens.application is 'L''application.';
comment on column commun.classes_liens.reference is 'La classe dans l''application : son code (ABC123 pour Gombessa, ABCD pour une salle de Lagon Arena) ou son identifiant.';

alter table commun.applications
  add column fn_prof_par_code regprocedure,
  add column fn_prof_eleves   regprocedure;
comment on column commun.applications.fn_prof_par_code is 'Connecteur facultatif (p_code text) returns table(enseignant_app_id uuid, nom text) : l''espace enseignant·e de l''application qui a ce code (tel que tapé), s''il existe.';
comment on column commun.applications.fn_prof_eleves is 'Connecteur facultatif (p_enseignant_app uuid) returns table(eleve_id uuid, pseudo text, classe text) : les élèves des classes de cet espace, dans l''application.';

alter table commun.xp_journal
  add constraint xp_journal_enseignant_fkey foreign key (enseignant_id) references commun.enseignants (id) on delete set null;

-- -----------------------------------------------------------------------------
-- F2. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- Un code d'enseignant·e neuf : 3 mots et 4 chiffres de la liste du site.
create function commun.nouveau_code_enseignant(out code text, out code_affiche text)
language plpgsql volatile set search_path = '' as $$
declare b bytea; v integer; w text[]; d text;
begin
  loop
    b := extensions.gen_random_bytes(5);
    v := get_byte(b, 3) * 256 + get_byte(b, 4);
    continue when v >= 60000;
    select array_agg(m.mot order by k.i) into w
      from generate_series(0, 2) k(i) join commun.mots m on m.application = 'commun' and m.rang = get_byte(b, k.i) % 64;
    d := lpad((v % 10000)::text, 4, '0');
    code := w[1] || w[2] || w[3] || d;
    code_affiche := w[1] || '-' || w[2] || '-' || w[3] || '-' || d;
    exit when not exists (select 1 from commun.enseignants e
                           where e.code_empreinte = encode(sha256(convert_to(nouveau_code_enseignant.code, 'UTF8')), 'hex'));
  end loop;
end $$;

create function commun.empreinte_enseignant(p_code text)
returns text language sql immutable set search_path = '' as $$
  select encode(sha256(convert_to(commun.normaliser_code(p_code), 'UTF8')), 'hex')
$$;

-- Un code de classe neuf : 4 lettres sans I ni O, tirées sans biais.
create function commun.nouveau_code_classe()
returns text language plpgsql volatile set search_path = '' as $$
declare lettres constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZ'; b bytea; c text; i integer;
begin
  loop
    c := '';
    while char_length(c) < 4 loop
      b := extensions.gen_random_bytes(1);
      i := get_byte(b, 0);
      continue when i >= 240;
      c := c || substr(lettres, 1 + i % 24, 1);
    end loop;
    exit when not exists (select 1 from commun.classes x where x.code = c);
  end loop;
  return c;
end $$;

-- L'espace commun qu'ouvre un code : le code commun, sinon le code d'un
-- espace d'application (par son connecteur), qui est alors relié (et l'espace
-- commun créé, au nom de l'espace de l'application). Null si inconnu.
create function commun.enseignant_par_code(p_code text)
returns uuid language plpgsql volatile set search_path = '' as $$
declare v uuid; a record; v_app uuid; v_nom text;
begin
  select e.id into v from commun.enseignants e where e.code_empreinte = commun.empreinte_enseignant(p_code);
  if v is not null then return v; end if;
  for a in select x.id, x.fn_prof_par_code from commun.applications x
            where x.active and x.fn_prof_par_code is not null order by x.id loop
    begin
      execute format('select t.enseignant_app_id, t.nom from %s($1) t limit 1', a.fn_prof_par_code::oid::regproc)
        into v_app, v_nom using left(coalesce(p_code, ''), 80);
    exception when others then
      raise warning 'commun.enseignant_par_code : le connecteur de % a échoué (%)', a.id, sqlerrm;
      v_app := null;
    end;
    if v_app is not null then
      select l.enseignant_id into v from commun.enseignants_liens l where l.application = a.id and l.enseignant_app_id = v_app;
      if v is null then
        -- Un espace commun sans code commun (empreinte au hasard) : l'ancien
        -- code de l'application l'ouvre ; « Nouveau code » en donne un.
        insert into commun.enseignants (code_empreinte, nom)
        values (encode(extensions.gen_random_bytes(32), 'hex'), coalesce(commun.nettoyer_texte(v_nom, 2, 40), 'Enseignant·e'))
        returning id into v;
        insert into commun.enseignants_liens (application, enseignant_app_id, enseignant_id) values (a.id, v_app, v);
      end if;
      return v;
    end if;
  end loop;
  return null;
end $$;

-- Vérifie un code d'enseignant·e avec le compteur d'essais (10 échecs par
-- heure et par réseau). Renvoie l'espace, ou null et un message.
create function commun.verifier_enseignant(p_code text, out prof uuid, out message text)
language plpgsql volatile set search_path = '' as $$
begin
  if not commun.essai_permis('commun', 'enseignant', 10) then
    message := 'Trop d''essais depuis ce réseau. Attends la fin de l''heure.';
    return;
  end if;
  prof := commun.enseignant_par_code(p_code);
  if prof is null then
    perform commun.noter_echec('commun', 'enseignant');
    perform pg_sleep(0.3);
    message := 'Ce code d''enseignant·e n''existe pas.';
    return;
  end if;
  update commun.enseignants e set vu_le = now() where e.id = prof;
end $$;

-- Les élèves des espaces d'application reliés à un espace commun, avec leur
-- compte commun s'il existe (applications rattachées).
create function commun.eleves_de(p_prof uuid)
returns table (application text, eleve_app_id uuid, pseudo text, classe text, compte_id uuid)
language plpgsql volatile set search_path = '' as $$
declare l record;
begin
  for l in select li.application, li.enseignant_app_id, a.fn_prof_eleves
             from commun.enseignants_liens li join commun.applications a on a.id = li.application
            where li.enseignant_id = p_prof and a.active and a.fn_prof_eleves is not null loop
    begin
      return query execute format(
        'select $1::text, t.eleve_id, t.pseudo, t.classe, (select k.compte_id from commun.liens k where k.application = $1 and k.eleve_app_id = t.eleve_id)
           from %s($2) t', l.fn_prof_eleves::oid::regproc)
        using l.application, l.enseignant_app_id;
    exception when others then
      raise warning 'commun.eleves_de : le connecteur de % a échoué (%)', l.application, sqlerrm;
    end;
  end loop;
end $$;

-- Vrai si la classe est à cet·te enseignant·e.
create function commun.classe_du_prof(p_prof uuid, p_classe uuid)
returns boolean language sql stable set search_path = '' as $$
  select exists (select 1 from commun.classes c where c.id = p_classe and c.enseignant_id = p_prof)
$$;

-- Vrai si l'élève est dans une classe commune de cet·te enseignant·e, ou
-- dans une classe d'un de ses espaces d'application reliés.
create function commun.eleve_visible(p_prof uuid, p_compte uuid)
returns boolean language plpgsql volatile set search_path = '' as $$
begin
  if p_compte is null then return false; end if;
  if exists (select 1 from commun.inscriptions i join commun.classes c on c.id = i.classe_id
              where i.compte_id = p_compte and c.enseignant_id = p_prof) then
    return true;
  end if;
  return exists (select 1 from commun.eleves_de(p_prof) x where x.compte_id = p_compte);
end $$;

revoke all on function commun.nouveau_code_enseignant(), commun.empreinte_enseignant(text), commun.nouveau_code_classe(),
  commun.enseignant_par_code(text), commun.verifier_enseignant(text), commun.eleves_de(uuid),
  commun.classe_du_prof(uuid, uuid), commun.eleve_visible(uuid, uuid) from public, anon, authenticated;
comment on function commun.nouveau_code_enseignant() is 'Commun, interne. Un code d''enseignant·e neuf : 3 mots de la liste du site et 4 chiffres, tirés sans biais, dont l''empreinte est libre.';
comment on function commun.empreinte_enseignant(text) is 'Commun, interne. L''empreinte SHA-256 de la forme canonique d''un code d''enseignant·e.';
comment on function commun.nouveau_code_classe() is 'Commun, interne. Un code de classe neuf : 4 lettres sans I ni O, tirées sans biais, libre.';
comment on function commun.enseignant_par_code(text) is 'Commun, interne. L''espace commun qu''ouvre un code : le code commun, ou celui d''un espace d''application relié (créé et relié à la première ouverture).';
comment on function commun.verifier_enseignant(text) is 'Commun, interne. Vérifie un code d''enseignant·e avec le compteur d''essais (10 échecs par heure et par réseau).';
comment on function commun.eleves_de(uuid) is 'Commun, interne. Les élèves des classes des espaces d''application reliés à un espace commun, avec leur compte commun s''il existe.';
comment on function commun.classe_du_prof(uuid, uuid) is 'Commun, interne. Vrai si la classe commune appartient à cet·te enseignant·e.';
comment on function commun.eleve_visible(uuid, uuid) is 'Commun, interne. Vrai si l''élève est dans une classe commune de cet·te enseignant·e ou dans une classe d''un de ses espaces d''application reliés.';

-- -----------------------------------------------------------------------------
-- F3. Les fonctions d'entrée de l'enseignant·e : anon seul
-- -----------------------------------------------------------------------------

create function public.commun_prof_creer_espace(p_nom text, p_etablissement text default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v_nom text := commun.nettoyer_texte(p_nom, 2, 40);
        v_etab text := commun.nettoyer_texte(p_etablissement, 2, 80);
        n record;
begin
  if not commun.essai_permis('commun', 'creation', 60) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''espaces créés depuis ce réseau en une heure. Attends un peu.');
  end if;
  if v_nom is null then
    return jsonb_build_object('ok', false, 'message', 'Donne un nom affiché de 2 à 40 caractères (« Mme Ali », « M. B. »).');
  end if;
  if v_etab is null and nullif(btrim(coalesce(p_etablissement, '')), '') is not null then
    return jsonb_build_object('ok', false, 'message', 'L''établissement a de 2 à 80 caractères.');
  end if;
  perform commun.noter_echec('commun', 'creation');
  select * into n from commun.nouveau_code_enseignant();
  insert into commun.enseignants (code_empreinte, nom, etablissement)
  values (commun.empreinte_enseignant(n.code), v_nom, v_etab);
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche,
    'message', 'Voici ton code. Il n''est montré qu''une fois : note-le ou imprime-le.');
end $$;

-- Ouvrir son espace : son nom, ses classes, ses applications reliées.
create function public.commun_prof_ouvrir(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; e commun.enseignants;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  select * into e from commun.enseignants x where x.id = v.prof;
  return jsonb_build_object('ok', true, 'nom', e.nom, 'etablissement', e.etablissement,
    'classes', coalesce((select jsonb_agg(jsonb_build_object('id', c.id, 'nom', c.nom, 'code', c.code, 'ouverte', c.ouverte,
                                 'applications', to_jsonb(c.applications),
                                 'eleves', (select count(*) from commun.inscriptions i where i.classe_id = c.id)) order by c.nom)
                           from commun.classes c where c.enseignant_id = e.id), '[]'::jsonb),
    'applications', coalesce((select jsonb_agg(jsonb_build_object('id', a.id, 'nom', a.nom, 'adresse_prof', a.adresse_prof) order by a.nom)
                                from commun.applications a
                               where exists (select 1 from commun.enseignants_liens l where l.enseignant_id = e.id and l.application = a.id)), '[]'::jsonb),
    'alarme', commun.echecs_heure('commun') > 200);
end $$;

-- Relier à son espace commun l'espace d'une application (son ancien code),
-- ou réunir deux espaces communs. Rien n'est perdu.
create function public.commun_prof_lier_code(p_code text, p_autre_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; autre uuid;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  autre := commun.enseignant_par_code(p_autre_code);
  if autre is null then
    perform commun.noter_echec('commun', 'enseignant');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Cet autre code n''existe pas.');
  end if;
  if autre <> v.prof then
    update commun.enseignants_liens set enseignant_id = v.prof where enseignant_id = autre;
    update commun.classes set enseignant_id = v.prof where enseignant_id = autre;
    update commun.xp_journal set enseignant_id = v.prof where enseignant_id = autre;
    delete from commun.enseignants where id = autre;
  end if;
  return jsonb_build_object('ok', true, 'message', 'Ton code commun ouvre aussi cet espace. L''autre code reste valable dans son application.');
end $$;

create function public.commun_prof_creer_classe(p_code text, p_nom text, p_applications text[] default '{}')
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n text := commun.nettoyer_texte(p_nom, 2, 40); c commun.classes;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if n is null then return jsonb_build_object('ok', false, 'message', 'Donne un nom de classe de 2 à 40 caractères.'); end if;
  insert into commun.classes (enseignant_id, nom, code, applications)
  values (v.prof, n, commun.nouveau_code_classe(),
          coalesce((select array_agg(a.id order by a.id) from commun.applications a where a.id = any(p_applications[1:20])), '{}'::text[]))
  returning * into c;
  return jsonb_build_object('ok', true, 'id', c.id, 'code', c.code,
    'lien', 'https://babash.github.io/Babash-NSI-SNT/eleve/?classe=' || c.code);
end $$;

create function public.commun_prof_modifier_classe(p_code text, p_classe uuid, p_nom text, p_ouverte boolean, p_applications text[])
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n text := commun.nettoyer_texte(p_nom, 2, 40);
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  if n is null then return jsonb_build_object('ok', false, 'message', 'Donne un nom de classe de 2 à 40 caractères.'); end if;
  update commun.classes c set nom = n, ouverte = coalesce(p_ouverte, c.ouverte),
         applications = coalesce((select array_agg(a.id order by a.id) from commun.applications a where a.id = any(p_applications[1:20])), '{}'::text[])
   where c.id = p_classe;
  return jsonb_build_object('ok', true);
end $$;

create function public.commun_prof_supprimer_classe(p_code text, p_classe uuid, p_confirmation text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  if coalesce(upper(btrim(p_confirmation)), '') <> 'SUPPRIMER' then
    return jsonb_build_object('ok', false, 'message', 'Écris SUPPRIMER pour confirmer.');
  end if;
  delete from commun.classes c where c.id = p_classe;
  return jsonb_build_object('ok', true, 'message', 'La classe est supprimée. Les comptes des élèves restent, avec tout ce qu''ils ont gagné.');
end $$;

-- Relier à une classe commune la classe d'une application (ou retirer ce
-- lien avec p_retirer).
create function public.commun_prof_lier_classe(p_code text, p_classe uuid, p_application text, p_reference text, p_retirer boolean default false)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  if not exists (select 1 from commun.applications a where a.id = left(p_application, 30))
     or coalesce(p_reference, '') !~ '^[A-Za-z0-9_-]{1,64}$' then
    return jsonb_build_object('ok', false, 'message', 'Application ou classe de l''application inconnue.');
  end if;
  if p_retirer then
    delete from commun.classes_liens l where l.classe_id = p_classe and l.application = p_application and l.reference = p_reference;
  else
    insert into commun.classes_liens (classe_id, application, reference) values (p_classe, p_application, p_reference) on conflict do nothing;
  end if;
  return jsonb_build_object('ok', true);
end $$;

-- La page d'une classe : les élèves (pseudo, avatar, codes nés sur le site,
-- hauts faits, XP, crédits, dernière visite) et les tableaux de bord des
-- applications de la classe. Un seul objet JSON (règle P7). Rangé par pseudo.
create function public.commun_prof_classe(p_code text, p_classe uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; c commun.classes;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  select * into c from commun.classes x where x.id = p_classe and x.enseignant_id = v.prof;
  if c.id is null then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  return jsonb_build_object('ok', true,
    'classe', jsonb_build_object('id', c.id, 'nom', c.nom, 'code', c.code, 'ouverte', c.ouverte, 'applications', to_jsonb(c.applications),
      'lien', 'https://babash.github.io/Babash-NSI-SNT/eleve/?classe=' || c.code,
      'tableaux', coalesce((select jsonb_agg(jsonb_build_object('application', a.id, 'nom', a.nom, 'reference', l.reference,
                                     'adresse', case when a.adresse_prof is not null then a.adresse_prof || '#classe=' || l.reference end)
                                     order by a.nom, l.reference)
                              from commun.classes_liens l join commun.applications a on a.id = l.application where l.classe_id = c.id), '[]'::jsonb)),
    'eleves', coalesce((select jsonb_agg(jsonb_build_object(
                 'compte', k.id, 'pseudo', k.pseudo, 'avatar', k.avatar, 'xp', k.xp, 'credits', k.credits, 'vu_le', k.vu_le,
                 'codes', coalesce((select jsonb_agg(x.code_affiche order by x.principal desc) from commun.codes x where x.compte_id = k.id), '[]'::jsonb),
                 'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait, 'gagne_le', g.gagne_le)
                                                           order by g.gagne_le) from commun.hauts_faits_gagnes g where g.compte_id = k.id), '[]'::jsonb))
               order by lower(k.pseudo))
             from commun.inscriptions i join commun.comptes k on k.id = i.compte_id where i.classe_id = c.id), '[]'::jsonb));
end $$;

-- Les élèves des espaces d'application reliés (applications rattachées), et
-- leurs hauts faits de cette application. Aucun total, aucun classement.
create function public.commun_prof_eleves(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  return jsonb_build_object('ok', true, 'eleves', coalesce((
    select jsonb_agg(jsonb_build_object(
             'application', x.application, 'eleve_app_id', x.eleve_app_id, 'pseudo', x.pseudo, 'classe', x.classe, 'compte', x.compte_id,
             'avatar', (select k.avatar from commun.comptes k where k.id = x.compte_id),
             'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait, 'gagne_le', g.gagne_le)
                                                       order by g.gagne_le)
                                        from commun.hauts_faits_gagnes g where g.compte_id = x.compte_id), '[]'::jsonb))
           order by x.application, x.classe, lower(x.pseudo))
      from commun.eleves_de(v.prof) x), '[]'::jsonb));
end $$;

-- Attribuer de l'XP (donc des crédits) à un·e élève de ses classes, avec un
-- motif court, inscrit au journal (1 à 50 par attribution).
create function public.commun_prof_attribuer_xp(p_code text, p_compte uuid, p_xp integer, p_motif text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; m text := commun.nettoyer_texte(p_motif, 3, 80); g integer;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if p_xp is null or p_xp not between 1 and 50 then
    return jsonb_build_object('ok', false, 'message', 'Une attribution va de 1 à 50.');
  end if;
  if m is null then return jsonb_build_object('ok', false, 'message', 'Donne un motif de 3 à 80 caractères.'); end if;
  if not commun.eleve_visible(v.prof, p_compte) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes.');
  end if;
  g := commun.crediter(p_compte, 'commun', 'attribution', null, p_xp, 'enseignant', m, v.prof);
  return jsonb_build_object('ok', true, 'xp', g);
end $$;

-- Le journal de l'XP des élèves d'une classe (500 dernières lignes) : gains,
-- attributions (avec leur motif et leur auteur·e) et achats.
create function public.commun_prof_journal_xp(p_code text, p_classe uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  return jsonb_build_object('ok', true, 'journal', coalesce((
    select jsonb_agg(jsonb_build_object('le', j.cree_le, 'compte', j.compte_id, 'pseudo', k.pseudo, 'application', j.application,
                                        'evenement', j.evenement, 'xp', j.xp, 'motif', j.motif,
                                        'par', (select e.nom from commun.enseignants e where e.id = j.enseignant_id)) order by j.cree_le desc)
      from (select x.* from commun.xp_journal x join commun.inscriptions i on i.compte_id = x.compte_id and i.classe_id = p_classe
             order by x.cree_le desc limit 500) j
      join commun.comptes k on k.id = j.compte_id), '[]'::jsonb));
end $$;

-- Accorder un haut fait de genre « enseignant » (l'entraide, par exemple).
create function public.commun_prof_accorder(p_code text, p_compte uuid, p_application text, p_haut_fait text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.eleve_visible(v.prof, p_compte) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes, ou n''a pas encore de compte commun.');
  end if;
  return jsonb_build_object('ok', true, 'nouveautes', commun.accorder(p_compte, left(p_application, 30), array[left(p_haut_fait, 40)], 'enseignant'));
end $$;

create function public.commun_prof_retirer_eleve(p_code text, p_classe uuid, p_compte uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  delete from commun.inscriptions i where i.classe_id = p_classe and i.compte_id = p_compte;
  return jsonb_build_object('ok', true, 'message', 'L''élève n''est plus dans la classe ; son compte reste.');
end $$;

create function public.commun_prof_renommer_eleve(p_code text, p_compte uuid, p_pseudo text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; p text := commun.nettoyer_pseudo(p_pseudo);
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if p is null then return jsonb_build_object('ok', false, 'message', 'Un prénom ou un pseudo de 2 à 24 caractères.'); end if;
  if not exists (select 1 from commun.inscriptions i join commun.classes c on c.id = i.classe_id
                  where i.compte_id = p_compte and c.enseignant_id = v.prof) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes communes.');
  end if;
  update commun.comptes k set pseudo = p, pseudo_provisoire = false where k.id = p_compte;
  return jsonb_build_object('ok', true, 'pseudo', p);
end $$;

-- Un nouveau code pour un·e élève dont le code est né sur le site (code
-- perdu ou divulgué) : l'ancien cesse de marcher, ses sessions sont fermées.
-- Pour un code d'une application rattachée, c'est l'application qui le donne.
create function public.commun_prof_nouveau_code_eleve(p_code text, p_compte uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not exists (select 1 from commun.inscriptions i join commun.classes c on c.id = i.classe_id
                  where i.compte_id = p_compte and c.enseignant_id = v.prof) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes communes.');
  end if;
  if not exists (select 1 from commun.codes x where x.compte_id = p_compte and x.application = 'commun') then
    return jsonb_build_object('ok', false, 'message', 'Son code vient d''une application : donne-lui un nouveau code depuis cette application.');
  end if;
  delete from commun.codes x where x.compte_id = p_compte and x.application = 'commun';
  select * into n from commun.nouveau_code('commun');
  insert into commun.codes (code, code_affiche, compte_id, application, principal)
  values (n.code, n.code_affiche, p_compte, 'commun', not exists (select 1 from commun.codes y where y.compte_id = p_compte and y.principal));
  delete from commun.sessions s where s.compte_id = p_compte;
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche);
end $$;

create function public.commun_prof_nouveau_code(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  select * into n from commun.nouveau_code_enseignant();
  update commun.enseignants e set code_empreinte = commun.empreinte_enseignant(n.code) where e.id = v.prof;
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche,
    'message', 'Voici ton nouveau code commun ; l''ancien ne marche plus. Les codes de tes applications restent valables.');
end $$;

create function public.commun_prof_debloquer_reseau(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  return jsonb_build_object('ok', true, 'effaces', commun.debloquer_reseau('commun'));
end $$;

create function public.commun_prof_supprimer_espace(p_code text, p_confirmation text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if coalesce(upper(btrim(p_confirmation)), '') <> 'SUPPRIMER' then
    return jsonb_build_object('ok', false, 'message', 'Écris SUPPRIMER pour confirmer.');
  end if;
  delete from commun.enseignants e where e.id = v.prof;
  return jsonb_build_object('ok', true, 'message', 'Ton espace commun et tes classes communes sont supprimés. Les comptes des élèves restent, ainsi que tes espaces dans chaque application.');
end $$;

-- -----------------------------------------------------------------------------
-- F4. Les fonctions d'entrée de l'élève pour les classes : anon seul
-- -----------------------------------------------------------------------------

-- La classe derrière un lien : son nom et l'enseignant·e, sans aucun élève.
create function public.commun_classe_par_code(p_code_classe text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare c record;
begin
  if not commun.essai_permis('commun', 'classe', 30) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  select x.nom, x.ouverte, e.nom as enseignant into c
    from commun.classes x join commun.enseignants e on e.id = x.enseignant_id
   where x.code = commun.normaliser_code(left(coalesce(p_code_classe, ''), 20));
  if c.nom is null then
    perform commun.noter_echec('commun', 'classe');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Ce code de classe n''existe pas.');
  end if;
  return jsonb_build_object('ok', true, 'nom', c.nom, 'enseignant', c.enseignant, 'ouverte', c.ouverte);
end $$;

-- Rejoindre une classe avec son compte (après commun_creer ou commun_entrer).
create function public.commun_rejoindre(p_jeton uuid, p_code_classe text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); c commun.classes; p text;
begin
  if v is null then return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.'); end if;
  if not commun.essai_permis('commun', 'classe', 30) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  select * into c from commun.classes x where x.code = commun.normaliser_code(left(coalesce(p_code_classe, ''), 20));
  if c.id is null then
    perform commun.noter_echec('commun', 'classe');
    return jsonb_build_object('ok', false, 'message', 'Ce code de classe n''existe pas.');
  end if;
  if exists (select 1 from commun.inscriptions i where i.classe_id = c.id and i.compte_id = v) then
    return jsonb_build_object('ok', true, 'message', 'Tu es déjà dans cette classe.', 'classe', c.nom);
  end if;
  if not c.ouverte then
    return jsonb_build_object('ok', false, 'message', 'Les inscriptions de cette classe sont fermées. Demande à ton enseignant·e.');
  end if;
  select k.pseudo into p from commun.comptes k where k.id = v;
  if exists (select 1 from commun.inscriptions i join commun.comptes k on k.id = i.compte_id
              where i.classe_id = c.id and lower(k.pseudo) = lower(p)) then
    return jsonb_build_object('ok', false, 'message', 'Ce pseudo est déjà pris dans la classe. Si c''est toi, entre avec ton code ; sinon, change de pseudo.');
  end if;
  insert into commun.inscriptions (classe_id, compte_id) values (c.id, v);
  return jsonb_build_object('ok', true, 'message', 'Bienvenue dans la classe.', 'classe', c.nom);
end $$;

-- Ce que l'élève voit de ses classes : pour chacune, son nom, ses
-- applications, et ses camarades (pseudo, avatar, hauts faits), rangé·e·s par
-- pseudo. Jamais l'XP, les crédits, les codes ni l'identifiant d'un compte.
create function public.commun_ma_classe(p_jeton uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton);
begin
  if v is null then return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.'); end if;
  return jsonb_build_object('ok', true, 'classes', coalesce((
    select jsonb_agg(jsonb_build_object('nom', c.nom, 'enseignant', e.nom, 'applications', to_jsonb(c.applications),
             'camarades', (select jsonb_agg(jsonb_build_object('pseudo', k.pseudo, 'avatar', k.avatar, 'moi', k.id = v,
                                     'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait)
                                                                               order by g.gagne_le)
                                                                from commun.hauts_faits_gagnes g where g.compte_id = k.id), '[]'::jsonb))
                                   order by lower(k.pseudo))
                             from commun.inscriptions j join commun.comptes k on k.id = j.compte_id where j.classe_id = c.id))
           order by c.nom)
      from commun.inscriptions i join commun.classes c on c.id = i.classe_id join commun.enseignants e on e.id = c.enseignant_id
     where i.compte_id = v), '[]'::jsonb));
end $$;

revoke all on function public.commun_prof_creer_espace(text, text), public.commun_prof_ouvrir(text),
  public.commun_prof_lier_code(text, text), public.commun_prof_creer_classe(text, text, text[]),
  public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]), public.commun_prof_supprimer_classe(text, uuid, text),
  public.commun_prof_lier_classe(text, uuid, text, text, boolean), public.commun_prof_classe(text, uuid),
  public.commun_prof_eleves(text), public.commun_prof_attribuer_xp(text, uuid, integer, text),
  public.commun_prof_journal_xp(text, uuid), public.commun_prof_accorder(text, uuid, text, text),
  public.commun_prof_retirer_eleve(text, uuid, uuid), public.commun_prof_renommer_eleve(text, uuid, text),
  public.commun_prof_nouveau_code_eleve(text, uuid), public.commun_prof_nouveau_code(text),
  public.commun_prof_debloquer_reseau(text), public.commun_prof_supprimer_espace(text, text),
  public.commun_classe_par_code(text), public.commun_rejoindre(uuid, text), public.commun_ma_classe(uuid)
  from public, anon, authenticated;
grant execute on function public.commun_prof_creer_espace(text, text), public.commun_prof_ouvrir(text),
  public.commun_prof_lier_code(text, text), public.commun_prof_creer_classe(text, text, text[]),
  public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]), public.commun_prof_supprimer_classe(text, uuid, text),
  public.commun_prof_lier_classe(text, uuid, text, text, boolean), public.commun_prof_classe(text, uuid),
  public.commun_prof_eleves(text), public.commun_prof_attribuer_xp(text, uuid, integer, text),
  public.commun_prof_journal_xp(text, uuid), public.commun_prof_accorder(text, uuid, text, text),
  public.commun_prof_retirer_eleve(text, uuid, uuid), public.commun_prof_renommer_eleve(text, uuid, text),
  public.commun_prof_nouveau_code_eleve(text, uuid), public.commun_prof_nouveau_code(text),
  public.commun_prof_debloquer_reseau(text), public.commun_prof_supprimer_espace(text, text),
  public.commun_classe_par_code(text), public.commun_rejoindre(uuid, text), public.commun_ma_classe(uuid)
  to anon;

comment on function public.commun_prof_creer_espace(text, text) is 'Compte commun, entrée enseignant·e. Crée un espace commun et renvoie son code (3 mots, 4 chiffres), montré une seule fois. Ouvert à tout·e collègue ; 60 créations par heure et par réseau.';
comment on function public.commun_prof_ouvrir(text) is 'Compte commun, entrée enseignant·e. Ouvre l''espace avec le code commun ou le code d''un espace d''application : nom, classes communes, applications reliées. 10 échecs par heure et par réseau.';
comment on function public.commun_prof_lier_code(text, text) is 'Compte commun, entrée enseignant·e. Relie à l''espace commun l''espace d''une application (son code), ou réunit deux espaces communs.';
comment on function public.commun_prof_creer_classe(text, text, text[]) is 'Compte commun, entrée enseignant·e. Crée une classe commune et renvoie son code et son lien.';
comment on function public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]) is 'Compte commun, entrée enseignant·e. Renomme une classe, ouvre ou ferme ses inscriptions, change ses applications.';
comment on function public.commun_prof_supprimer_classe(text, uuid, text) is 'Compte commun, entrée enseignant·e. Supprime une classe commune (confirmation : SUPPRIMER) ; les comptes des élèves restent.';
comment on function public.commun_prof_lier_classe(text, uuid, text, text, boolean) is 'Compte commun, entrée enseignant·e. Relie à une classe commune la classe d''une application (ou retire ce lien), pour le renvoi vers son tableau de bord.';
comment on function public.commun_prof_classe(text, uuid) is 'Compte commun, entrée enseignant·e. La page d''une classe : élèves (pseudo, avatar, codes, hauts faits, XP, crédits) et tableaux de bord des applications, en un objet JSON, rangés par pseudo.';
comment on function public.commun_prof_eleves(text) is 'Compte commun, entrée enseignant·e. Les élèves des espaces d''application reliés et leurs hauts faits, en un objet JSON ; aucun total, aucun classement.';
comment on function public.commun_prof_attribuer_xp(text, uuid, integer, text) is 'Compte commun, entrée enseignant·e. Attribue de 1 à 50 XP (et autant de crédits) à un·e élève de ses classes, avec un motif court, inscrit au journal.';
comment on function public.commun_prof_journal_xp(text, uuid) is 'Compte commun, entrée enseignant·e. Le journal de l''XP des élèves d''une classe (500 dernières lignes), avec les motifs et les auteur·e·s des attributions.';
comment on function public.commun_prof_accorder(text, uuid, text, text) is 'Compte commun, entrée enseignant·e. Accorde un haut fait de genre enseignant à un·e élève de ses classes.';
comment on function public.commun_prof_retirer_eleve(text, uuid, uuid) is 'Compte commun, entrée enseignant·e. Retire un·e élève d''une classe commune ; son compte reste.';
comment on function public.commun_prof_renommer_eleve(text, uuid, text) is 'Compte commun, entrée enseignant·e. Renomme le compte commun d''un·e élève de ses classes communes.';
comment on function public.commun_prof_nouveau_code_eleve(text, uuid) is 'Compte commun, entrée enseignant·e. Donne un nouveau code (né sur le site) à un·e élève de ses classes communes ; l''ancien cesse de marcher.';
comment on function public.commun_prof_nouveau_code(text) is 'Compte commun, entrée enseignant·e. Remplace le code commun (il faut donner l''ancien) ; les codes des applications restent valables.';
comment on function public.commun_prof_debloquer_reseau(text) is 'Compte commun, entrée enseignant·e. Remet à zéro le compteur d''essais du réseau de la salle, pour le compte commun.';
comment on function public.commun_prof_supprimer_espace(text, text) is 'Compte commun, entrée enseignant·e. Supprime l''espace commun et ses classes communes (confirmation : SUPPRIMER) ; les comptes des élèves et les espaces des applications restent.';
comment on function public.commun_classe_par_code(text) is 'Compte commun, entrée élève. La classe derrière un lien : son nom, l''enseignant·e, inscriptions ouvertes ou non ; aucun élève. 30 échecs par heure et par réseau.';
comment on function public.commun_rejoindre(uuid, text) is 'Compte commun, entrée élève. Rejoint une classe commune avec son compte ; refuse un pseudo déjà pris dans la classe.';
comment on function public.commun_ma_classe(uuid) is 'Compte commun, entrée élève. Les camarades de ses classes seulement : pseudo, avatar et hauts faits ; jamais l''XP, les crédits ni les codes.';

-- -----------------------------------------------------------------------------
-- F5. Contrôle
-- -----------------------------------------------------------------------------
do $$
begin
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction de commun est appelable par anon ou par authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r' and not c.relrowsecurity) then
    raise exception 'Une table de commun n''a pas la RLS : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'v')
             and (has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de commun est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%'
             and (has_function_privilege('authenticated', p.oid, 'execute') or not has_function_privilege('anon', p.oid, 'execute')
                  or not p.prosecdef or p.proconfig is null)) then
    raise exception 'Une fonction commun_ n''a pas les bons droits : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- =============================================================================
-- G. Les avis anonymes des élèves sur les ressources (migration 0013)
-- =============================================================================
do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.classes') is null or to_regprocedure('commun.verifier_enseignant(text)') is null
     or to_regprocedure('commun.nettoyer_texte(text, integer, integer)') is null or to_regprocedure('commun.essai_permis(text, text, integer)') is null then
    raise exception 'Le compte commun (0003, 0007 et 0008) manque : l''appliquer d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if to_regclass('commun.retours') is not null
     or exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace
                 and (p.proname like 'commun\_retour%' or p.proname like 'commun\_prof\_retour%')) then
    raise exception 'Les retours des élèves (0013) sont déjà là : arrêt, rien n''a été modifié.';
  end if;
  if not exists (select 1 from pg_catalog.pg_timezone_names where name = 'Indian/Mayotte') then
    raise exception 'Le fuseau Indian/Mayotte est inconnu de la base : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- G1. La table
-- -----------------------------------------------------------------------------
create table commun.retours (
  id             uuid primary key default gen_random_uuid(),
  ressource      text not null check (ressource ~ '^(sequence:)?[a-z0-9][a-z0-9-]{1,79}$'),
  partie         text not null default '' check (partie = '' or partie ~ '^[a-z0-9][a-z0-9._-]{0,79}$'),
  classe_id      uuid references commun.classes (id) on delete set null,
  semaine        date not null check (extract(isodow from semaine) = 1),
  plu            smallint check (plu between 1 and 5),
  difficulte     text check (difficulte in ('trop_facile', 'bien', 'trop_dur')),
  compris        text check (compris in ('oui', 'a_peu_pres', 'non')),
  fini           text check (fini in ('oui', 'presque', 'non')),
  remarques      text[] not null default '{}'::text[]
                 check (remarques <@ array['consignes', 'trop_de_texte', 'exemples', 'bug', 'telephone', 'encore']::text[]),
  mot            text check (char_length(mot) between 1 and 140),
  cle_empreinte  text unique check (cle_empreinte ~ '^[0-9a-f]{64}$'),
  lot_classe     date,
  lot_tous       date,
  check (plu is not null or difficulte is not null or compris is not null or fini is not null
         or cardinality(remarques) > 0 or mot is not null)
);
create index retours_ressource on commun.retours (ressource, partie, semaine);
create index retours_classe on commun.retours (classe_id, ressource, partie) where classe_id is not null;
create index retours_semaine on commun.retours (semaine);
create index retours_a_publier on commun.retours (ressource, partie) where lot_tous is null or lot_classe is null;
alter table commun.retours enable row level security;
revoke all on commun.retours from public, anon, authenticated;
comment on table commun.retours is
  'Commun. Les avis anonymes des élèves à la fin d''une ressource en ligne (T163) : ni compte, ni code, ni pseudo, ni adresse, ni heure ; la semaine seulement, et la classe commune si la page la connaît. Montrés à l''enseignant·e par paquets d''au moins 5, jamais pendant la semaine en cours. Effacés deux ans après leur semaine. Données d''élèves : oui (des avis anonymes, et un mot libre facultatif lu par l''enseignant·e de la classe seulement).';
comment on column commun.retours.id is 'L''identifiant du retour, tiré au hasard (sert seulement à effacer un mot).';
comment on column commun.retours.ressource is 'La ressource : l''identifiant de sa fiche (donnees/ressources/<id>.json), ou sequence:<id> pour la page d''une séquence.';
comment on column commun.retours.partie is 'La partie de la ressource (l''identifiant d''une feuille de TD en ligne, data-td), ou vide.';
comment on column commun.retours.classe_id is 'La classe commune dont la page connaissait le code (lien ?classe=ABCD), sinon vide. Jamais l''élève. Vidé si la classe est supprimée (son mot part alors au ménage suivant).';
comment on column commun.retours.semaine is 'Le lundi de la semaine du retour (heure de Mayotte) : aucune date plus fine n''est gardée.';
comment on column commun.retours.plu is '« Ça t''a plu ? » : de 1 à 5 étoiles, ou vide.';
comment on column commun.retours.difficulte is '« C''était… » : trop_facile, bien ou trop_dur, ou vide.';
comment on column commun.retours.compris is '« J''ai compris » : oui, a_peu_pres ou non, ou vide.';
comment on column commun.retours.fini is '« J''ai fini » : oui, presque ou non, ou vide.';
comment on column commun.retours.remarques is 'Les remarques choisies dans une liste fermée : consignes (pas claires), trop_de_texte, exemples (il en faudrait plus), bug (quelque chose ne marchait pas), telephone (pas pratique sur téléphone), encore (j''en veux d''autres comme ça).';
comment on column commun.retours.mot is 'Le mot libre facultatif (140 caractères au plus, ni adresse, ni lien, ni numéro) : gardé seulement si la classe est connue, lu seulement par l''enseignant·e de la classe, jamais affiché aux élèves ; effaçable par l''élève pendant la semaine et par l''enseignant·e.';
comment on column commun.retours.cle_empreinte is 'L''empreinte SHA-256 de la clé tirée au hasard par l''appareil pour cette ressource : elle permet de changer ou retirer son avis pendant la semaine. Effacée dès la semaine finie : le retour n''est alors plus rattaché à rien.';
comment on column commun.retours.lot_classe is 'Le paquet de la classe où ce retour est montré (le lundi de la dernière semaine du paquet) ; vide tant qu''il attend que sa classe ait au moins 5 retours non montrés pour cette ressource.';
comment on column commun.retours.lot_tous is 'Le paquet « tout le monde » où ce retour est montré (le lundi de la dernière semaine du paquet) ; vide tant qu''il attend au moins 5 retours non montrés pour cette ressource.';

-- -----------------------------------------------------------------------------
-- G2. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- Le lundi de la semaine en cours, heure de Mayotte.
create function commun.retour_semaine()
returns date language sql stable set search_path = '' as $$
  select date_trunc('week', now() at time zone 'Indian/Mayotte')::date
$$;

-- L'empreinte d'une clé d'appareil bien formée (22 à 64 caractères base64url), sinon null.
create function commun.retour_cle(p_cle text)
returns text language sql immutable set search_path = '' as $$
  select case when coalesce(p_cle, '') ~ '^[A-Za-z0-9_-]{22,64}$'
              then encode(sha256(convert_to('retour|' || p_cle, 'UTF8')), 'hex') end
$$;

-- Avant toute lecture : les clés des semaines finies sont effacées, les mots
-- sans classe (classe inconnue ou supprimée) aussi, les retours de plus de deux ans partent, puis les
-- retours des semaines finies sont rangés en paquets d'au moins 5 (par classe
-- et ressource, et par ressource pour « tout le monde »). Un paquet rangé ne
-- change plus. Renvoie le nombre de retours rangés.
create function commun.retours_publier()
returns integer language plpgsql volatile set search_path = '' as $$
declare s date := commun.retour_semaine(); n1 integer; n2 integer;
begin
  delete from commun.retours r where r.semaine < s - 728;
  update commun.retours r set cle_empreinte = null where r.cle_empreinte is not null and r.semaine < s;
  update commun.retours r set mot = null where r.mot is not null and r.classe_id is null;
  update commun.retours r set lot_classe = g.lot
    from (select x.classe_id, x.ressource, x.partie, max(x.semaine) as lot
            from commun.retours x
           where x.lot_classe is null and x.classe_id is not null and x.semaine < s
           group by 1, 2, 3 having count(*) >= 5) g
   where r.lot_classe is null and r.classe_id = g.classe_id and r.ressource = g.ressource and r.partie = g.partie and r.semaine < s;
  get diagnostics n1 = row_count;
  update commun.retours r set lot_tous = g.lot
    from (select x.ressource, x.partie, max(x.semaine) as lot
            from commun.retours x
           where x.lot_tous is null and x.semaine < s
           group by 1, 2 having count(*) >= 5) g
   where r.lot_tous is null and r.ressource = g.ressource and r.partie = g.partie and r.semaine < s;
  get diagnostics n2 = row_count;
  return n1 + n2;
end $$;

revoke all on function commun.retour_semaine(), commun.retour_cle(text), commun.retours_publier() from public, anon, authenticated;
comment on function commun.retour_semaine() is 'Commun, interne. Le lundi de la semaine en cours, heure de Mayotte : la seule date gardée avec un retour.';
comment on function commun.retour_cle(text) is 'Commun, interne. L''empreinte SHA-256 d''une clé d''appareil bien formée (22 à 64 caractères base64url), sinon null.';
comment on function commun.retours_publier() is 'Commun, interne. Efface les clés des semaines finies, les mots sans classe et les retours de plus de deux ans, puis range les retours des semaines finies en paquets d''au moins 5 (par classe et ressource, et par ressource pour tout le monde). Un paquet rangé ne change plus.';

-- -----------------------------------------------------------------------------
-- G3. Les fonctions d'entrée de l'élève : anon seul
-- -----------------------------------------------------------------------------

-- Donner son avis, ou le changer pendant la semaine (même clé d'appareil).
create function public.commun_retour_donner(p_cle text, p_ressource text, p_partie text default '',
  p_classe text default null, p_plu integer default null, p_difficulte text default null, p_compris text default null,
  p_fini text default null, p_remarques text[] default '{}', p_mot text default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  s date := commun.retour_semaine();
  v_cle text := commun.retour_cle(p_cle);
  v_ressource text := left(coalesce(p_ressource, ''), 90);
  v_partie text := left(coalesce(p_partie, ''), 90);
  v_classe uuid;
  v_classe_donnee boolean := coalesce(btrim(p_classe), '') <> '';
  v_remarques text[];
  v_mot text;
  v_mot_brut text := nullif(btrim(coalesce(p_mot, '')), '');
  ancien commun.retours;
  v_modifie boolean := false;
begin
  if v_cle is null then
    return jsonb_build_object('ok', false, 'message', 'La page n''a pas pu préparer ton avis. Recharge-la, puis réessaie.');
  end if;
  if v_ressource !~ '^(sequence:)?[a-z0-9][a-z0-9-]{1,79}$' or (v_partie <> '' and v_partie !~ '^[a-z0-9][a-z0-9._-]{0,79}$') then
    return jsonb_build_object('ok', false, 'message', 'Cette page n''est pas prévue pour les avis.');
  end if;
  if not commun.essai_permis('retours', 'creation', 300) then
    return jsonb_build_object('ok', false, 'plus_tard', true, 'message', 'Beaucoup d''avis depuis ce réseau en une heure : ton avis attend sur ton appareil.');
  end if;
  -- Les réponses : seulement des valeurs prévues ; le reste est ignoré.
  if p_plu is not null and p_plu not between 1 and 5 then p_plu := null; end if;
  if p_difficulte not in ('trop_facile', 'bien', 'trop_dur') then p_difficulte := null; end if;
  if p_compris not in ('oui', 'a_peu_pres', 'non') then p_compris := null; end if;
  if p_fini not in ('oui', 'presque', 'non') then p_fini := null; end if;
  select coalesce(array_agg(distinct x order by x), '{}'::text[]) into v_remarques
    from unnest(coalesce(p_remarques[1:12], '{}'::text[])) x
   where x = any(array['consignes', 'trop_de_texte', 'exemples', 'bug', 'telephone', 'encore']);
  -- La classe : seulement un code de classe commune qui existe (30 codes inconnus par heure et par réseau).
  if v_classe_donnee and upper(btrim(p_classe)) ~ '^[A-HJ-NP-Z]{4}$' and commun.essai_permis('retours', 'classe', 30) then
    select c.id into v_classe from commun.classes c where c.code = upper(btrim(p_classe));
    if v_classe is null then perform commun.noter_echec('retours', 'classe'); end if;
  end if;
  -- Le mot : seulement avec une classe ; ni adresse, ni lien, ni numéro.
  if v_mot_brut is not null then
    v_mot := commun.nettoyer_texte(v_mot_brut, 1, 140);
    if v_mot is null then
      return jsonb_build_object('ok', false, 'message', 'Ton mot fait 140 caractères au plus, sans caractère spécial.');
    end if;
    if v_mot ~* '@|https?:|www\.|\.(com|fr|net|org|yt|re|io)\M|[0-9]([ .-]?[0-9]){5,}' then
      return jsonb_build_object('ok', false, 'message', 'Ton mot ne doit contenir ni adresse, ni lien, ni numéro de téléphone.');
    end if;
    if v_classe is null then v_mot := null; end if;
  end if;
  if p_plu is null and p_difficulte is null and p_compris is null and p_fini is null and cardinality(v_remarques) = 0 and v_mot is null then
    return jsonb_build_object('ok', false, 'message', 'Choisis au moins une réponse.');
  end if;

  select * into ancien from commun.retours r where r.cle_empreinte = v_cle;
  if found then
    if ancien.ressource <> v_ressource or ancien.partie <> v_partie or ancien.semaine <> s then
      return jsonb_build_object('ok', false, 'fige', true, 'message', 'Ton avis est déjà gardé ; il ne se change plus.');
    end if;
    update commun.retours r set classe_id = v_classe, plu = p_plu, difficulte = p_difficulte, compris = p_compris,
           fini = p_fini, remarques = v_remarques, mot = v_mot
     where r.id = ancien.id;
    v_modifie := true;
  else
    if (select count(*) from commun.retours r where r.ressource = v_ressource and r.partie = v_partie and r.semaine = s) >= 1500
       or (select count(*) from commun.retours r where r.semaine = s) >= 20000
       or (select count(*) from commun.retours) >= 300000 then
      return jsonb_build_object('ok', false, 'plus_tard', true, 'message', 'Beaucoup d''avis en ce moment : ton avis attend sur ton appareil.');
    end if;
    insert into commun.retours (ressource, partie, classe_id, semaine, plu, difficulte, compris, fini, remarques, mot, cle_empreinte)
    values (v_ressource, v_partie, v_classe, s, p_plu, p_difficulte, p_compris, p_fini, v_remarques, v_mot, v_cle);
  end if;
  perform commun.noter_echec('retours', 'creation');
  return jsonb_build_object('ok', true, 'modifie', v_modifie, 'classe', v_classe is not null,
    'classe_inconnue', v_classe_donnee and v_classe is null, 'mot_garde', v_mot is not null,
    'jusqu_au', s + 6);
end $$;

-- Retirer son avis de la semaine (même clé d'appareil).
create function public.commun_retour_effacer(p_cle text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v_cle text := commun.retour_cle(p_cle); n integer;
begin
  if v_cle is null then return jsonb_build_object('ok', false, 'message', 'Rien à retirer depuis cet appareil.'); end if;
  delete from commun.retours r where r.cle_empreinte = v_cle and r.semaine = commun.retour_semaine();
  get diagnostics n = row_count;
  if n = 0 then
    return jsonb_build_object('ok', false, 'message', 'Ton avis ne se retire plus : la semaine est finie, et il n''est plus rattaché à ton appareil.');
  end if;
  return jsonb_build_object('ok', true, 'message', 'Ton avis est retiré.');
end $$;

-- -----------------------------------------------------------------------------
-- G4. Les fonctions d'entrée de l'enseignant·e : anon seul
-- -----------------------------------------------------------------------------

-- Les paquets publiés : ceux d'une de ses classes (p_classe), ou ceux de tout
-- le monde (p_classe vide, sans aucun mot). Par ressource et partie, puis par
-- paquet : le nombre de retours et la répartition de chaque réponse.
create function public.commun_prof_retours(p_code text, p_classe uuid default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; res jsonb;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if p_classe is not null and not commun.classe_du_prof(v.prof, p_classe) then
    return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.');
  end if;
  perform commun.retours_publier();
  with r as (
    select x.*, case when p_classe is null then x.lot_tous else x.lot_classe end as lot
      from commun.retours x
     where (p_classe is null and x.lot_tous is not null)
        or (p_classe is not null and x.classe_id = p_classe and x.lot_classe is not null)
  ), lots as (
    select r.ressource, r.partie, r.lot, count(*) as n,
      jsonb_build_object('1', count(*) filter (where r.plu = 1), '2', count(*) filter (where r.plu = 2),
        '3', count(*) filter (where r.plu = 3), '4', count(*) filter (where r.plu = 4), '5', count(*) filter (where r.plu = 5)) as plu,
      jsonb_build_object('trop_facile', count(*) filter (where r.difficulte = 'trop_facile'),
        'bien', count(*) filter (where r.difficulte = 'bien'), 'trop_dur', count(*) filter (where r.difficulte = 'trop_dur')) as difficulte,
      jsonb_build_object('oui', count(*) filter (where r.compris = 'oui'),
        'a_peu_pres', count(*) filter (where r.compris = 'a_peu_pres'), 'non', count(*) filter (where r.compris = 'non')) as compris,
      jsonb_build_object('oui', count(*) filter (where r.fini = 'oui'),
        'presque', count(*) filter (where r.fini = 'presque'), 'non', count(*) filter (where r.fini = 'non')) as fini,
      jsonb_build_object('consignes', count(*) filter (where 'consignes' = any(r.remarques)),
        'trop_de_texte', count(*) filter (where 'trop_de_texte' = any(r.remarques)),
        'exemples', count(*) filter (where 'exemples' = any(r.remarques)),
        'bug', count(*) filter (where 'bug' = any(r.remarques)),
        'telephone', count(*) filter (where 'telephone' = any(r.remarques)),
        'encore', count(*) filter (where 'encore' = any(r.remarques))) as remarques
      from r group by 1, 2, 3
  ), groupes as (
    select l.ressource, l.partie,
      jsonb_agg(jsonb_build_object('semaine', l.lot, 'n', l.n, 'plu', l.plu, 'difficulte', l.difficulte,
        'compris', l.compris, 'fini', l.fini, 'remarques', l.remarques) order by l.lot) as lots
      from lots l group by 1, 2
  )
  select coalesce(jsonb_agg(jsonb_build_object('ressource', g.ressource, 'partie', g.partie, 'lots', g.lots,
           'mots', case when p_classe is null then '[]'::jsonb else coalesce((
             select jsonb_agg(jsonb_build_object('id', r.id, 'mot', r.mot) order by md5(r.id::text))
               from r where r.ressource = g.ressource and r.partie = g.partie and r.mot is not null), '[]'::jsonb) end)
         order by g.ressource, g.partie), '[]'::jsonb)
    into res from groupes g;
  return jsonb_build_object('ok', true, 'portee', case when p_classe is null then 'tous' else 'classe' end,
    'semaine', commun.retour_semaine(), 'seuil', 5, 'ressources', res);
end $$;

-- Effacer un mot (une insulte, un nom) d'un retour de ses classes.
create function public.commun_prof_retour_effacer_mot(p_code text, p_retour uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n integer;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  update commun.retours r set mot = null
   where r.id = p_retour and r.mot is not null and r.lot_classe is not null
     and r.classe_id in (select c.id from commun.classes c where c.enseignant_id = v.prof);
  get diagnostics n = row_count;
  if n = 0 then return jsonb_build_object('ok', false, 'message', 'Ce mot n''est pas dans tes classes, ou il est déjà effacé.'); end if;
  return jsonb_build_object('ok', true, 'message', 'Le mot est effacé.');
end $$;

revoke all on function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text),
  public.commun_retour_effacer(text), public.commun_prof_retours(text, uuid), public.commun_prof_retour_effacer_mot(text, uuid)
  from public, anon, authenticated;
grant execute on function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text),
  public.commun_retour_effacer(text), public.commun_prof_retours(text, uuid), public.commun_prof_retour_effacer_mot(text, uuid)
  to anon;
comment on function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text) is
  'Compte commun, entrée élève, sans compte. Donne ou change (même clé d''appareil, pendant la semaine) un avis anonyme sur une ressource : étoiles, difficulté, compréhension, fini ou non, remarques d''une liste fermée, mot libre (avec une classe seulement). 300 envois par heure et par réseau.';
comment on function public.commun_retour_effacer(text) is
  'Compte commun, entrée élève, sans compte. Retire l''avis de la semaine donné depuis cet appareil (sa clé).';
comment on function public.commun_prof_retours(text, uuid) is
  'Compte commun, entrée enseignant·e. Les avis publiés, par paquets d''au moins 5, des semaines finies : d''une de ses classes (avec les mots), ou de tout le monde (sans aucun mot).';
comment on function public.commun_prof_retour_effacer_mot(text, uuid) is
  'Compte commun, entrée enseignant·e. Efface le mot libre d''un avis de ses classes.';

-- -----------------------------------------------------------------------------
-- G5. Contrôle
-- -----------------------------------------------------------------------------
do $$
begin
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction de commun est appelable par anon ou par authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r' and not c.relrowsecurity) then
    raise exception 'Une table de commun n''a pas la RLS : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'v')
             and (has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de commun est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%'
             and (has_function_privilege('authenticated', p.oid, 'execute') or not has_function_privilege('anon', p.oid, 'execute')
                  or not p.prosecdef or p.proconfig is null)) then
    raise exception 'Une fonction commun_ n''a pas les bons droits : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_attribute a where a.attrelid = 'commun.retours'::regclass and a.attnum > 0
             and not a.attisdropped and col_description(a.attrelid, a.attnum) is null) then
    raise exception 'Une colonne de commun.retours n''a pas de commentaire : arrêt, rien n''a été modifié.';
  end if;
end $$;

commit;
