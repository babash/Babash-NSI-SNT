begin;
-- =============================================================================
--  Base unique, préalable 4 : l'ancien projet de Lagon Arena
--  Projet Supabase gkyvaugipddjqjvvpopw (« Lagon Arena »), PAS le projet cible
--  Nom de migration : base_unique_0004_ancien_projet_sequence_pantheon
-- =============================================================================
--  Pourquoi : anon a usage, select et update sur la séquence de la colonne
--  d'identité du Panthéon, public.pantheon_id_seq (règle P2). Il n'en a pas
--  besoin : seules des fonctions security definer ajoutent des tortues au
--  Panthéon, et Postgres remplit une colonne d'identité sans vérifier de
--  droit sur sa séquence.
--
--  Ce que ce fichier change : anon perd tout droit sur public.pantheon_id_seq.
--
--  Ce que ce fichier ne change pas : tout le reste. Aucun objet guilde_*,
--  aucune table, aucune fonction, aucun droit par défaut, aucune ligne,
--  aucune page. Les droits d'authenticated sur la séquence restent (la
--  consigne de T42 se limite à anon pour ce projet).
--
--  Retour en arrière : 0004-ancien-projet-sequence-pantheon-inverse.sql.
--  Mode d'emploi : LISEZMOI.md.
-- =============================================================================

-- Garde-fou : le bon rôle, le bon projet, et une séquence d'identité.
do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.pantheon') is null or to_regclass('public.snt_responses') is not null then
    raise exception 'Ce fichier est pour le projet gkyvaugipddjqjvvpopw (Lagon Arena), pas pour celui-ci : arrêt, rien n''a été modifié.';
  end if;
  if not exists (select 1 from pg_catalog.pg_depend d
                 where d.classid = 'pg_catalog.pg_class'::regclass and d.objid = to_regclass('public.pantheon_id_seq')
                   and d.refclassid = 'pg_catalog.pg_class'::regclass and d.refobjid = 'public.pantheon'::regclass
                   and d.deptype = 'i') then
    raise exception 'public.pantheon_id_seq n''est pas la séquence de la colonne d''identité de public.pantheon : arrêt, rien n''a été modifié.';
  end if;
end $$;

revoke all on sequence public.pantheon_id_seq from anon;

-- Contrôle
do $$
begin
  if has_sequence_privilege('anon', 'public.pantheon_id_seq', 'usage, select, update') then
    raise exception 'anon a encore un droit sur public.pantheon_id_seq : arrêt, rien n''a été modifié.';
  end if;
end $$;

commit;
