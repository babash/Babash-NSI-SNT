begin;
-- =============================================================================
--  SQL inverse de 0003-schema-commun.sql
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0003_schema_commun_inverse
-- =============================================================================
--  **Ce retour efface le sel secret et les compteurs d'essais.** Ce ne sont
--  pas des données d'élèves : les compteurs repartent simplement de zéro, et
--  un nouveau sel sera tiré si 0003 est appliqué de nouveau. Aucune sauvegarde
--  n'est nécessaire.
--
--  Supprime le schéma commun et tout ce que 0003 y a créé : la vue registre,
--  les six fonctions internes, les tables essais et secret.
--  S'arrête, sans rien modifier, si le schéma contient autre chose, ou si une
--  fonction d'une application s'en sert déjà : il faut alors d'abord défaire
--  la migration de cette application.
-- =============================================================================

do $$
declare f text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null and to_regclass('snt_premier_jour.reponses') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi (la table des réponses de SNT 1er jour manque) : arrêt, rien n''a été modifié.';
  end if;
  if to_regnamespace('commun') is null then
    raise exception 'Le schéma commun n''existe pas : 0003 n''est pas appliqué, il n''y a rien à défaire.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace
             and c.relkind in ('r', 'p', 'v', 'm', 'f', 'S') and c.relname not in ('secret', 'essais', 'registre'))
     or exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
                and p.proname not in ('reseau', 'essai_permis', 'menage_essais', 'noter_echec', 'debloquer_reseau', 'echecs_heure')) then
    raise exception 'Le schéma commun contient d''autres objets que ceux de 0003 : une migration plus récente s''en sert. La défaire d''abord. Arrêt, rien n''a été modifié.';
  end if;
  select string_agg(p.oid::regprocedure::text, ', ') into f
  from pg_catalog.pg_proc p join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where n.nspname not in ('commun', 'pg_catalog', 'information_schema') and p.prosrc ~ '\mcommun\.[a-z_]';
  if f is not null then
    raise exception 'Des fonctions se servent du schéma commun (%) : défaire d''abord leur migration. Arrêt, rien n''a été modifié.', f;
  end if;
end $$;

drop view commun.registre;
drop function commun.echecs_heure(text);
drop function commun.debloquer_reseau(text);
drop function commun.noter_echec(text, text);
drop function commun.menage_essais();
drop function commun.essai_permis(text, text, integer);
drop function commun.reseau();
drop table commun.essais;
drop table commun.secret;
drop schema commun;

commit;
