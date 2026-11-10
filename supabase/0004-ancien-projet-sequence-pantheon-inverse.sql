begin;
-- =============================================================================
--  SQL inverse de 0004-ancien-projet-sequence-pantheon.sql
--  Projet Supabase gkyvaugipddjqjvvpopw (« Lagon Arena »), PAS le projet cible
--  Nom de migration : base_unique_0004_ancien_projet_sequence_pantheon_inverse
-- =============================================================================
--  Rend à anon usage, select et update sur public.pantheon_id_seq.
--  Ne touche à rien d'autre.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.pantheon_id_seq') is null or to_regclass('public.snt_responses') is not null then
    raise exception 'Ce fichier est pour le projet gkyvaugipddjqjvvpopw (Lagon Arena), pas pour celui-ci : arrêt, rien n''a été modifié.';
  end if;
end $$;

grant usage, select, update on sequence public.pantheon_id_seq to anon;

commit;
