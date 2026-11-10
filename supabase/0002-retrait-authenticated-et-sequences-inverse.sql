begin;
-- =============================================================================
--  SQL inverse de 0002-retrait-authenticated-et-sequences.sql
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0002_retrait_authenticated_et_sequences_inverse
-- =============================================================================
--  Rend les droits d'avant 0002 :
--   1. usage, select et update sur les deux séquences, pour anon et authenticated ;
--   2. le droit d'exécution d'authenticated sur chaque fonction de public
--      qu'anon peut appeler (avant 0002, c'étaient exactement les mêmes) ;
--   3. le droit d'exécution de public sur les 6 fonctions d'Alien Python,
--      les seules qui l'avaient (si elles existent encore).
--  Ne touche ni aux droits d'anon, ni aux tables, ni aux lignes.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null or to_regclass('public.gb_evenements') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi (public.snt_responses ou public.gb_evenements manque) : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- 1. Les séquences
grant usage, select, update on sequence public.gb_evenements_id_seq, public.snt_responses_id_seq to anon, authenticated;

-- 2. authenticated, sur les fonctions qu'anon peut appeler (même choix de fonctions que 0002)
do $$
declare r record;
begin
  for r in
    select p.oid::regprocedure as fonction
    from pg_catalog.pg_proc p
    where p.pronamespace = 'public'::regnamespace
      and p.proowner = 'postgres'::regrole
      and p.prokind in ('f', 'p')
      and not exists (select 1 from pg_catalog.pg_depend d
                      where d.classid = 'pg_catalog.pg_proc'::regclass and d.objid = p.oid and d.deptype = 'e')
      and not exists (select 1 from pg_catalog.pg_depend d
                      where d.refclassid = 'pg_catalog.pg_proc'::regclass and d.refobjid = p.oid
                        and d.classid in ('pg_catalog.pg_constraint'::regclass, 'pg_catalog.pg_attrdef'::regclass,
                                          'pg_catalog.pg_policy'::regclass, 'pg_catalog.pg_class'::regclass,
                                          'pg_catalog.pg_rewrite'::regclass))
      and pg_catalog.has_function_privilege('anon', p.oid, 'execute')
    order by 1
  loop
    execute format('grant execute on routine %s to authenticated', r.fonction);
  end loop;
end $$;

-- 3. public, sur les 6 fonctions d'Alien Python
do $$
declare f text;
begin
  foreach f in array array[
    'public.alien_class_view(text, text)',
    'public.alien_create_class(text, text)',
    'public.alien_join_class(text, text)',
    'public.alien_save_progress(text, text, text, boolean, boolean, integer, boolean)',
    'public.alien_student_login(text, text)',
    'public.alien_teacher_overview(text, text)'
  ] loop
    if to_regprocedure(f) is not null then
      execute format('grant execute on function %s to public', f);
    end if;
  end loop;
end $$;

notify pgrst, 'reload schema';

commit;
