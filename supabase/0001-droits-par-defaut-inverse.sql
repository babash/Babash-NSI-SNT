begin;
-- =============================================================================
--  SQL inverse de 0001-droits-par-defaut.sql
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0001_droits_par_defaut_inverse
-- =============================================================================
--  Rend au rôle postgres les droits par défaut d'avant 0001 : dans « public »,
--  tous les droits pour anon et authenticated sur les nouvelles tables,
--  séquences et fonctions ; partout, le droit d'exécution de public sur les
--  nouvelles fonctions (le réglage d'origine de Postgres).
--  Ne touche à aucun objet existant. Les objets créés entre-temps gardent les
--  droits qu'ils ont reçus.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null and to_regclass('snt_premier_jour.reponses') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi (la table des réponses de SNT 1er jour manque) : arrêt, rien n''a été modifié.';
  end if;
end $$;

alter default privileges for role postgres in schema public
  grant all on tables to anon, authenticated;
alter default privileges for role postgres in schema public
  grant all on sequences to anon, authenticated;
alter default privileges for role postgres in schema public
  grant all on functions to anon, authenticated;
alter default privileges for role postgres
  grant execute on functions to public;

commit;
