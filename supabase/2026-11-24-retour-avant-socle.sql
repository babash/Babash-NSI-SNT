begin;
-- =============================================================================
--  Retour avant le compte commun : retire la version 1 de 0007 et 0008
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0007_0008_retour_version_1
--  T132c, 24/11/2026. Écrit d'après les métadonnées de la base relues le 24/11.
-- =============================================================================
--  Pourquoi : la base contient la toute première version du compte commun
--  (0007 et 0008 du 20/11, 14:21, commit a33a640 jamais publié de la branche
--  archi/t101-compte-commun : ni XP, ni crédits, ni classes), et non la
--  version 2.2 approuvée. Ce fichier ramène la base à l'état d'avant, pour
--  coller ensuite 0007 v2.3, puis 0008.
--
--  Ce qu'il retire, objet par objet, et rien d'autre :
--   - 18 fonctions d'entrée public.commun_… ;
--   - 22 fonctions internes du schéma commun (celles du socle restent) ;
--   - 15 tables du schéma commun, avec ce qui leur appartient en propre :
--     leurs 24 index, leurs contraintes et leurs types de ligne (Postgres
--     les retire avec la table, sans cascade).
--  Les 7 lignes de commun.applications, les 64 mots, les 17 emplacements et
--  la ligne de commun.menage partent avec leurs tables : ce ne sont pas des
--  données d'élèves, et 0007 v2.3 les recrée.
--
--  Ce qu'il garde (le socle, fichiers supabase/0003-schema-commun.sql et
--  0009-registre-vacances.sql) : le schéma commun, les tables commun.secret
--  et commun.essais avec leurs lignes, la vue commun.registre, et les
--  6 fonctions reseau, essai_permis, menage_essais, noter_echec,
--  debloquer_reseau, echecs_heure. Aucune autre application n'est touchée.
--
--  Aucun « cascade », aucun « drop schema ». S'arrête sans rien modifier si :
--   - ce n'est pas le bon projet, ou pas le rôle postgres ;
--   - une table d'élèves ou d'enseignant·e·s a une ligne ;
--   - le schéma commun contient un objet que ce fichier ne connaît pas
--     (par exemple la version 2, avec ses classes ou ses barèmes) ;
--   - un objet hors du schéma commun dépend d'un objet à retirer, ou une
--     fonction d'application se sert d'autre chose que du socle.
--  À la fin, il vérifie qu'il reste exactement le socle ; sinon tout est
--  annulé.
-- =============================================================================

-- Garde-fou. Sinon, arrêt avant toute modification.
do $$
declare
  t text;
  n bigint;
  f text;
  socle_tables constant text[] := array['essais', 'secret'];
  socle_fonctions constant text[] := array['commun.reseau()', 'commun.essai_permis(text,text,integer)',
    'commun.menage_essais()', 'commun.noter_echec(text,text)', 'commun.debloquer_reseau(text)',
    'commun.echecs_heure(text)'];
  v1_tables constant text[] := array['applications', 'mots', 'comptes', 'codes', 'liens', 'sessions',
    'emplacements', 'elements', 'hauts_faits', 'recompenses', 'hauts_faits_gagnes', 'elements_debloques',
    'menage', 'enseignants', 'enseignants_liens'];
  eleves constant text[] := array['comptes', 'codes', 'liens', 'sessions', 'hauts_faits_gagnes',
    'elements_debloques', 'enseignants', 'enseignants_liens'];
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null or to_regclass('public.gb_eleves') is null
     or to_regnamespace('grand_oral') is null or to_regnamespace('vacances') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi : arrêt, rien n''a été modifié.';
  end if;
  -- le socle est là
  foreach t in array socle_tables loop
    if to_regclass('commun.' || t) is null then
      raise exception 'Le socle manque (commun.%) : arrêt, rien n''a été modifié.', t;
    end if;
  end loop;
  foreach f in array socle_fonctions loop
    if to_regprocedure(f) is null then
      raise exception 'Le socle manque (%) : arrêt, rien n''a été modifié.', f;
    end if;
  end loop;
  if to_regclass('commun.registre') is null then
    raise exception 'La vue commun.registre manque : arrêt, rien n''a été modifié.';
  end if;
  -- c'est bien la version 1, entière
  foreach t in array v1_tables loop
    if to_regclass('commun.' || t) is null then
      raise exception 'commun.% manque : la base n''est pas dans l''état relevé le 24/11. Arrêt, rien n''a été modifié.', t;
    end if;
  end loop;
  -- aucune ligne d'élève ni d'enseignant·e
  foreach t in array eleves loop
    execute format('select count(*) from commun.%I', t) into n;
    if n > 0 then
      raise exception 'commun.% contient % ligne(s) : des élèves ou des enseignant·e·s s''en servent déjà. Arrêt, rien n''a été modifié.', t, n;
    end if;
  end loop;
  -- aucun objet inconnu dans le schéma commun
  select string_agg(c.relname, ', ') into f
  from pg_catalog.pg_class c
  where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')
    and c.relname <> all (socle_tables || v1_tables || array['registre']);
  if f is not null then
    raise exception 'Objets inconnus dans le schéma commun (%) : ce n''est pas l''état relevé le 24/11. Arrêt, rien n''a été modifié.', f;
  end if;
  select string_agg(p.oid::regprocedure::text, ', ') into f
  from pg_catalog.pg_proc p
  where (p.pronamespace = 'commun'::regnamespace
         and p.proname not in ('reseau', 'essai_permis', 'menage_essais', 'noter_echec', 'debloquer_reseau', 'echecs_heure',
                               'accorder', 'accorder_app', 'compte_par_code', 'compte_par_eleve_app', 'compte_par_jeton',
                               'creer_compte', 'eleves_de', 'empreinte_enseignant', 'enseignant_par_code', 'fiche',
                               'fusionner', 'menage_si_besoin', 'nettoyer_pseudo', 'nettoyer_texte', 'normaliser_code',
                               'nouveau_code', 'nouveau_code_enseignant', 'ouvrir_session', 'reprise_ids',
                               'verifier_avatar', 'verifier_enseignant', 'visite_app'))
     or (p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%'
         and p.proname not in ('commun_catalogue', 'commun_creer', 'commun_effacer_moi', 'commun_entrer',
                               'commun_haut_fait_page', 'commun_lier_code', 'commun_porter', 'commun_prof_accorder',
                               'commun_prof_creer_espace', 'commun_prof_debloquer_reseau', 'commun_prof_eleves',
                               'commun_prof_lier_code', 'commun_prof_nouveau_code', 'commun_prof_ouvrir',
                               'commun_prof_supprimer_espace', 'commun_quitter', 'commun_renommer', 'commun_reprise'));
  if f is not null then
    raise exception 'Fonctions inconnues (%) : ce n''est pas l''état relevé le 24/11. Arrêt, rien n''a été modifié.', f;
  end if;
  if exists (select 1 from pg_catalog.pg_type ty where ty.typnamespace = 'commun'::regnamespace and ty.typrelid = 0
             and ty.typelem = 0 and ty.typtype <> 'b') then
    raise exception 'Un type défini à part existe dans le schéma commun : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_policy po join pg_catalog.pg_class c on c.oid = po.polrelid
             where c.relnamespace = 'commun'::regnamespace)
     or exists (select 1 from pg_catalog.pg_trigger tg join pg_catalog.pg_class c on c.oid = tg.tgrelid
                where c.relnamespace = 'commun'::regnamespace and not tg.tgisinternal) then
    raise exception 'Une règle d''accès ou un déclencheur existe sur le schéma commun : arrêt, rien n''a été modifié.';
  end if;
  -- rien hors du schéma commun n'en dépend
  select string_agg(distinct pg_catalog.pg_describe_object(d.classid, d.objid, d.objsubid), ', ') into f
  from pg_catalog.pg_depend d
  join pg_catalog.pg_class c on d.refclassid = 'pg_catalog.pg_class'::regclass and d.refobjid = c.oid
  where c.relnamespace = 'commun'::regnamespace and c.relname = any (v1_tables)
    and d.deptype = 'n'
    and not (d.classid = 'pg_catalog.pg_class'::regclass
             and exists (select 1 from pg_catalog.pg_class x where x.oid = d.objid and x.relnamespace = 'commun'::regnamespace))
    and not (d.classid = 'pg_catalog.pg_constraint'::regclass
             and exists (select 1 from pg_catalog.pg_constraint k join pg_catalog.pg_class x on x.oid = k.conrelid
                         where k.oid = d.objid and x.relnamespace = 'commun'::regnamespace))
    and not (d.classid = 'pg_catalog.pg_type'::regclass
             and exists (select 1 from pg_catalog.pg_type ty where ty.oid = d.objid and ty.typnamespace = 'commun'::regnamespace))
    and not (d.classid = 'pg_catalog.pg_proc'::regclass
             and exists (select 1 from pg_catalog.pg_proc x where x.oid = d.objid
                         and (x.pronamespace = 'commun'::regnamespace
                              or (x.pronamespace = 'public'::regnamespace and x.proname like 'commun\_%'))));
  if f is not null then
    raise exception 'Des objets hors du compte commun dépendent de ses tables (%) : arrêt, rien n''a été modifié.', f;
  end if;
  select string_agg(p.oid::regprocedure::text, ', ') into f
  from pg_catalog.pg_proc p join pg_catalog.pg_namespace s on s.oid = p.pronamespace
  where s.nspname not in ('commun', 'pg_catalog', 'information_schema')
    and not (s.nspname = 'public' and p.proname like 'commun\_%')
    and p.prosrc ~ '\mcommun\.(applications|mots|comptes|codes|liens|sessions|emplacements|elements|hauts_faits|recompenses|hauts_faits_gagnes|elements_debloques|menage|enseignants|enseignants_liens|accorder|accorder_app|compte_par_code|compte_par_eleve_app|compte_par_jeton|creer_compte|eleves_de|empreinte_enseignant|enseignant_par_code|fiche|fusionner|menage_si_besoin|nettoyer_pseudo|nettoyer_texte|normaliser_code|nouveau_code|nouveau_code_enseignant|ouvrir_session|reprise_ids|verifier_avatar|verifier_enseignant|visite_app)\M';
  if f is not null then
    raise exception 'Des fonctions d''applications se servent du compte commun (%) : arrêt, rien n''a été modifié.', f;
  end if;
end $$;

-- 1. Les 18 fonctions d'entrée (version 1 de 0007 : 10 ; de 0008 : 8)
drop function
  public.commun_catalogue(),
  public.commun_creer(text, integer),
  public.commun_effacer_moi(uuid, text, boolean),
  public.commun_entrer(text, integer),
  public.commun_haut_fait_page(uuid, text, text),
  public.commun_lier_code(uuid, text),
  public.commun_porter(uuid, jsonb),
  public.commun_quitter(uuid),
  public.commun_renommer(uuid, text),
  public.commun_reprise(uuid),
  public.commun_prof_accorder(text, uuid, text, text),
  public.commun_prof_creer_espace(text, text),
  public.commun_prof_debloquer_reseau(text),
  public.commun_prof_eleves(text),
  public.commun_prof_lier_code(text, text),
  public.commun_prof_nouveau_code(text),
  public.commun_prof_ouvrir(text),
  public.commun_prof_supprimer_espace(text, text);

-- 2. Les 22 fonctions internes (0007 v1 : 17 ; 0008 v1 : 5). Le socle reste.
drop function
  commun.accorder(uuid, text, text[], text),
  commun.accorder_app(text, uuid, text[]),
  commun.compte_par_code(text),
  commun.compte_par_eleve_app(text, uuid, boolean),
  commun.compte_par_jeton(uuid),
  commun.creer_compte(text, text),
  commun.fiche(uuid),
  commun.fusionner(uuid, uuid),
  commun.menage_si_besoin(),
  commun.nettoyer_pseudo(text),
  commun.nettoyer_texte(text, integer, integer),
  commun.normaliser_code(text),
  commun.nouveau_code(text),
  commun.ouvrir_session(uuid, integer),
  commun.reprise_ids(text, uuid),
  commun.verifier_avatar(uuid, jsonb),
  commun.visite_app(text, uuid),
  commun.eleves_de(uuid),
  commun.empreinte_enseignant(text),
  commun.enseignant_par_code(text),
  commun.nouveau_code_enseignant(),
  commun.verifier_enseignant(text);

-- 3. Les 15 tables, en une instruction : les clés étrangères entre elles ne
--    demandent pas de cascade. Leurs index, contraintes et types de ligne
--    partent avec elles.
drop table
  commun.enseignants_liens,
  commun.enseignants,
  commun.menage,
  commun.elements_debloques,
  commun.hauts_faits_gagnes,
  commun.recompenses,
  commun.hauts_faits,
  commun.elements,
  commun.emplacements,
  commun.sessions,
  commun.liens,
  commun.codes,
  commun.comptes,
  commun.mots,
  commun.applications;

-- Contrôle final : il reste exactement le socle. Sinon, tout est annulé.
do $$
declare f text;
begin
  select string_agg(c.relname || ' (' || c.relkind::text || ')', ', ' order by c.relname) into f
  from pg_catalog.pg_class c
  where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'p', 'v', 'm', 'S', 'f');
  if f is distinct from 'essais (r), registre (v), secret (r)' then
    raise exception 'Contrôle final : le schéma commun contient « % » au lieu de essais, registre, secret. Tout est annulé.', f;
  end if;
  select string_agg(p.proname, ', ' order by p.proname) into f
  from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace;
  if f is distinct from 'debloquer_reseau, echecs_heure, essai_permis, menage_essais, noter_echec, reseau' then
    raise exception 'Contrôle final : les fonctions du schéma commun sont « % » au lieu des 6 du socle. Tout est annulé.', f;
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%') then
    raise exception 'Contrôle final : il reste une fonction public.commun_… : tout est annulé.';
  end if;
  if exists (select 1 from pg_catalog.pg_type ty where ty.typnamespace = 'commun'::regnamespace
             and ty.typname not in ('essais', '_essais', 'secret', '_secret', 'registre', '_registre')) then
    raise exception 'Contrôle final : il reste un type dans le schéma commun : tout est annulé.';
  end if;
  if not (select c.relrowsecurity from pg_catalog.pg_class c where c.oid = 'commun.essais'::regclass)
     or not (select c.relrowsecurity from pg_catalog.pg_class c where c.oid = 'commun.secret'::regclass)
     or (select count(*) from commun.secret) <> 1 then
    raise exception 'Contrôle final : le socle (commun.essais, commun.secret) n''est plus intact : tout est annulé.';
  end if;
  if has_table_privilege('anon', 'commun.essais', 'select') or has_table_privilege('anon', 'commun.secret', 'select')
     or has_schema_privilege('anon', 'commun', 'usage') then
    raise exception 'Contrôle final : anon a un droit sur le schéma commun : tout est annulé.';
  end if;
  perform count(*) from commun.registre;
  raise notice 'Retour fait : il reste le socle (commun.essais, commun.secret, commun.registre, 6 fonctions). Colle maintenant 0007 v2.3, puis 0008.';
end $$;

commit;
