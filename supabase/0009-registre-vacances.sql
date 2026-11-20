begin;
-- =============================================================================
--  Base unique, socle commun 9 : le Calendrier des vacances dans le registre
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0009_registre_vacances
--  T105, 20/11/2026. Numéro 0009 : 0006 est appliqué (Hello GO), 0007 et 0008
--  sont écrits par le compte commun (T101, branche archi/t101-compte-commun) et
--  pas encore appliqués. Ce fichier ne dépend ni de 0007 ni de 0008, et ne
--  touche à rien de ce qu'ils créent : il passe avant ou après eux.
-- =============================================================================
--  Pourquoi : le Calendrier des vacances prend son schéma, vacances, et le
--  préfixe cv_ (migration vacances_0001_calendrier, calendrier/supabase/). La vue
--  commun.registre ne range que les schémas qu'elle nomme.
--
--  Ce que ce fichier change, et rien d'autre : la vue commun.registre (le
--  schéma vacances dans la liste, le préfixe cv_ pour une table encore dans
--  public) et deux commentaires. Les colonnes, l'ordre, security_invoker et
--  les droits ne changent pas. La définition reprend celle de la base au
--  20/11 (base_unique_0006_registre_grand_oral), lue dans les métadonnées.
--
--  Il passe avant ou après la migration de l'application. Il peut être relancé.
--  Retour en arrière : 0009-registre-vacances-inverse.sql (la définition de 0006).
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.registre') is null
     or coalesce(obj_description(to_regclass('commun.registre'), 'pg_class'), '') not like 'Commun.%' then
    raise exception 'La vue commun.registre manque (base_unique_0003_schema_commun) : arrêt, rien n''a été modifié.';
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

commit;
