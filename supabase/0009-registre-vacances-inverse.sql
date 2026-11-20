begin;
-- =============================================================================
--  Base unique, retour en arrière du socle 9 : la vue commun.registre redevient
--  celle de base_unique_0006_registre_grand_oral (sans le schéma vacances).
--  Nom de migration : base_unique_0009_registre_vacances_inverse
--  Aucune donnée n'est effacée : seule la définition de la vue change.
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
  and n.nspname in ('public', 'snt_premier_jour', 'gombessa', 'alien', 'lagon', 'court_circuit', 'grand_oral', 'commun')
order by 1, 2, 3;
revoke all on commun.registre from public, anon, authenticated;
comment on column commun.registre.application is 'L''application : le schéma de la table, ou, pour une table encore dans public, l''application de son préfixe (snt_, gb_, alien_, lagon_, cc_, go_).';
comment on column commun.essais.application is 'L''application qui compte : son schéma (snt_premier_jour, gombessa, alien, lagon, court_circuit, grand_oral).';

commit;
