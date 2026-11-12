begin;
-- =============================================================================
--  Base unique, socle commun 5 : Court-circuit dans le registre des tables
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0005_registre_court_circuit
-- =============================================================================
--  Pourquoi : Court-circuit (jeu de duel de robots en Python) prend son schéma,
--  court_circuit, et le préfixe cc_ pour ses fonctions d'entrée (migration
--  court_circuit_0001_codes_eleves de son dossier). La vue commun.registre
--  (migration 0003) ne range que les schémas qu'elle nomme : sans ce fichier,
--  les tables de Court-circuit n'y apparaîtraient pas.
--
--  Ce que ce fichier change, et rien d'autre :
--   - la vue commun.registre : le schéma court_circuit dans la liste des
--     schémas lus, et le préfixe cc_ pour une table encore dans public ;
--     les colonnes, l'ordre, security_invoker et les droits ne changent pas ;
--   - deux commentaires, pour nommer Court-circuit : celui de la colonne
--     commun.registre.application et celui de commun.essais.application.
--
--  Ce que ce fichier ne change pas : aucune table, aucune ligne, aucune
--  fonction, aucun droit, aucune page. Il passe avant ou après la migration
--  de Court-circuit : tant que le schéma court_circuit n'existe pas, la vue
--  donne les mêmes lignes qu'avant.
--
--  Le fichier peut être relancé sans effet.
--  Retour en arrière : 0005-registre-court-circuit-inverse.sql.
--  Mode d'emploi : LISEZMOI.md.
-- =============================================================================

-- Garde-fou : le bon rôle, le bon projet, et le registre de la migration 0003.
-- Sinon, arrêt avant toute modification.
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
    raise exception 'La vue commun.registre de la migration 0003 manque (base_unique_0003_schema_commun) : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- 1. Le registre : la liste des tables de toutes les applications, Court-circuit
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
-- 2. Contrôle : la vue reste fermée à l'API et security_invoker, et elle range
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

commit;
