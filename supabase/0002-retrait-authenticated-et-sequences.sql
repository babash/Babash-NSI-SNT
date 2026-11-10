begin;
-- =============================================================================
--  Base unique, préalable 2 : authenticated retiré, séquences fermées
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0002_retrait_authenticated_et_sequences
-- =============================================================================
--  Pourquoi : aucune application n'utilise l'authentification de Supabase.
--  Le rôle authenticated n'a donc rien à faire dans la base (règle P4), et
--  anon n'a besoin d'aucun droit sur une séquence (règle P2) : les deux
--  colonnes concernées sont des identités, que Postgres remplit sans
--  vérifier de droit sur leur séquence.
--
--  Ce que ce fichier change :
--   1. Les séquences public.gb_evenements_id_seq et public.snt_responses_id_seq :
--      anon et authenticated perdent usage, select et update.
--   2. Les fonctions du schéma public qui appartiennent à postgres :
--      authenticated et public perdent le droit d'exécution. Avant cela,
--      chaque fonction qu'anon peut appeler reçoit un droit exprès pour anon,
--      qu'il avait déjà : la liste des fonctions appelables par anon (les
--      pages) ne change pas. Au 10/11, avant l'étape 0 de Gombessa,
--      28 fonctions perdent le droit d'authenticated (27 security definer et
--      gb_normaliser_code) ; après l'étape 0, 32. Les 6 fonctions d'Alien
--      Python perdent aussi le droit de public.
--
--  Ce que ce fichier ne change pas :
--   - les droits d'anon (aucune fonction appelable par anon n'est retirée, et
--     aucune n'est ajoutée) ; aucune table, aucune ligne, aucune page ;
--   - les fonctions d'une extension ;
--   - les fonctions dont une table se sert (contrainte, valeur par défaut,
--     index, règle d'accès ou vue) : elles s'exécutent avec les droits de qui
--     écrit dans la table. Aujourd'hui, c'est seulement public.snt_taille_max,
--     qui borne la taille des mots-clés de SNT 1er jour : elle part avec sa
--     table au déplacement de SNT 1er jour (n° 3 du plan) ;
--   - le droit d'ajout d'authenticated sur public.snt_responses et la règle
--     « Ajout d'une réponse » (état accepté avec T36) : ils disparaissent au
--     déplacement de SNT 1er jour (n° 3 du plan).
--
--  Le fichier peut être relancé : il ne refait que ce qui manque. À relancer
--  si une migration d'application redonne un droit à authenticated (par
--  exemple 0001-espaces.sql de Gombessa, s'il est appliqué après ce fichier).
--
--  Retour en arrière : 0002-retrait-authenticated-et-sequences-inverse.sql.
--  Mode d'emploi : LISEZMOI.md.
-- =============================================================================

-- Garde-fou : le bon rôle, le bon projet, et deux séquences d'identité.
do $$
declare s text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null or to_regclass('public.gb_evenements') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi (public.snt_responses ou public.gb_evenements manque) : arrêt, rien n''a été modifié.';
  end if;
  foreach s in array array['public.gb_evenements_id_seq', 'public.snt_responses_id_seq'] loop
    if not exists (select 1 from pg_catalog.pg_depend d
                   where d.classid = 'pg_catalog.pg_class'::regclass and d.objid = to_regclass(s)
                     and d.refclassid = 'pg_catalog.pg_class'::regclass and d.deptype = 'i') then
      raise exception 'La séquence % n''est pas celle d''une colonne d''identité : la fermer pourrait empêcher des ajouts. Arrêt, rien n''a été modifié.', s;
    end if;
  end loop;
end $$;

-- 1. Les séquences : plus aucun droit pour anon ni authenticated.
revoke all on sequence public.gb_evenements_id_seq, public.snt_responses_id_seq from anon, authenticated;

-- 2. Les fonctions de public : authenticated et public retirés, anon inchangé.
do $$
declare
  r record;
  n integer := 0;
begin
  for r in
    select p.oid::regprocedure as fonction,
           pg_catalog.has_function_privilege('anon', p.oid, 'execute') as pour_anon
    from pg_catalog.pg_proc p
    where p.pronamespace = 'public'::regnamespace
      and p.proowner = 'postgres'::regrole
      and p.prokind in ('f', 'p')
      -- pas les fonctions d'une extension
      and not exists (select 1 from pg_catalog.pg_depend d
                      where d.classid = 'pg_catalog.pg_proc'::regclass and d.objid = p.oid and d.deptype = 'e')
      -- pas les fonctions dont une table se sert
      and not exists (select 1 from pg_catalog.pg_depend d
                      where d.refclassid = 'pg_catalog.pg_proc'::regclass and d.refobjid = p.oid
                        and d.classid in ('pg_catalog.pg_constraint'::regclass, 'pg_catalog.pg_attrdef'::regclass,
                                          'pg_catalog.pg_policy'::regclass, 'pg_catalog.pg_class'::regclass,
                                          'pg_catalog.pg_rewrite'::regclass))
    order by 1
  loop
    if r.pour_anon then
      execute format('grant execute on routine %s to anon', r.fonction);
    end if;
    execute format('revoke execute on routine %s from public, authenticated', r.fonction);
    -- contrôle, fonction par fonction : anon inchangé, authenticated sans accès
    if pg_catalog.has_function_privilege('anon', r.fonction, 'execute') is distinct from r.pour_anon
       or pg_catalog.has_function_privilege('authenticated', r.fonction, 'execute') then
      raise exception 'Droits inattendus sur % après le retrait : arrêt, rien n''a été modifié.', r.fonction;
    end if;
    n := n + 1;
  end loop;
  raise notice 'Fonctions de public traitées : %', n;
end $$;

-- 3. Contrôle : aucune séquence de public ne reste ouverte à anon ou à authenticated.
do $$
begin
  if exists (select 1 from pg_catalog.pg_class c
             where c.relnamespace = 'public'::regnamespace and c.relkind = 'S'
               and (pg_catalog.has_sequence_privilege('anon', c.oid, 'usage, select, update')
                    or pg_catalog.has_sequence_privilege('authenticated', c.oid, 'usage, select, update'))) then
    raise exception 'Une séquence de public reste ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- Demande à l'API de recharger sa liste des fonctions.
notify pgrst, 'reload schema';

commit;
