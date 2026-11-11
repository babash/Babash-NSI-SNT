begin;
-- =============================================================================
--  Base unique : le socle commun, script complet
-- =============================================================================
--  À quoi il sert : installer le socle commun dans un projet Supabase neuf
--  (la copie d'un·e collègue), avant le script complet d'une application.
--  Il réunit, dans une seule transaction :
--   A. les droits par défaut fermés (migration 0001) ;
--   B. le schéma commun : compteur d'essais, sel secret, fonctions internes
--      et registre des tables (migration 0003).
--  La migration 0002 n'y est pas : elle corrige les droits d'objets qui
--  existaient déjà dans le projet de l'enseignant.
--
--  Mode d'emploi : dans le tableau de bord de Supabase, SQL Editor, coller
--  tout le fichier, puis Run. Il peut être relancé sans risque : il ne crée
--  que ce qui manque, et ne tire jamais un second sel.
--
--  NE PAS MODIFIER À LA MAIN : ce fichier est fabriqué à partir de 0001 et
--  de 0003 par scripts/supabase_schema.py (même texte, sans le contrôle du
--  projet de l'enseignant). Il change dans le même commit qu'eux (règle M2).
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

commit;
