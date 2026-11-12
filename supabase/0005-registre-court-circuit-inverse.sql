begin;
-- =============================================================================
--  SQL inverse de 0005-registre-court-circuit.sql
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0005_registre_court_circuit_inverse
-- =============================================================================
--  Rend la vue commun.registre et les deux commentaires exactement comme la
--  migration 0003 les a créés : le registre ne range plus le schéma
--  court_circuit ni le préfixe cc_.
--
--  Il n'efface rien : aucune table, aucune ligne, aucune donnée d'élève. Les
--  tables de Court-circuit restent en place, simplement absentes du registre.
--  Pour défaire aussi 0003, ce fichier n'est pas nécessaire avant
--  0003-schema-commun-inverse.sql, qui supprime la vue.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null and to_regclass('snt_premier_jour.reponses') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi (la table des réponses de SNT 1er jour manque) : arrêt, rien n''a été modifié.';
  end if;
  if to_regclass('commun.registre') is null
     or coalesce(obj_description(to_regclass('commun.registre'), 'pg_class'), '') not like 'Commun.%' then
    raise exception 'La vue commun.registre manque : il n''y a rien à défaire. Arrêt, rien n''a été modifié.';
  end if;
end $$;

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
comment on column commun.registre.application is 'L''application : le schéma de la table, ou, pour une table encore dans public, l''application de son préfixe (snt_, gb_, alien_, lagon_).';
comment on column commun.essais.application is 'L''application qui compte : son schéma (gombessa, alien, lagon, snt_premier_jour).';

commit;
