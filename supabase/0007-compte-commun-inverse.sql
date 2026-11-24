begin;
-- =============================================================================
--  SQL inverse de 0007-compte-commun.sql (versions 2, 2.2 et 2.3 : mêmes objets)
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0007_compte_commun_inverse
-- =============================================================================
--  **Ce retour efface les comptes communs, leurs codes nés sur le site,
--  leurs avatars, leurs hauts faits, leur XP, leurs crédits et leurs achats.**
--  Les comptes des applications (Hello GO, et ceux créés après la remise à
--  zéro) ne sont pas touchés.
--
--  S'il y a déjà des comptes communs, il faut d'abord les sauvegarder
--  (règle M8, export par le tableau de bord), et prévenir les élèves dont
--  le code est né sur le site : ce code cessera de marcher.
--
--  S'arrête, sans rien modifier, si une application s'est déjà branchée
--  (un connecteur déclaré, ou une fonction d'une application qui se sert du
--  compte commun), ou si 0008 est appliqué : il faut d'abord les défaire.
-- =============================================================================

do $$
declare f text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.comptes') is null then
    raise exception 'commun.comptes n''existe pas : 0007 n''est pas appliqué, il n''y a rien à défaire.';
  end if;
  if to_regclass('commun.enseignants') is not null then
    raise exception 'La migration 0008 (enseignant·e·s et classes) est appliquée : la défaire d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from commun.applications a
             where a.fn_par_code is not null or a.fn_par_id is not null or a.fn_hauts_faits is not null
                or a.fn_effacer is not null or a.fn_fusion is not null) then
    raise exception 'Une application a déclaré ses connecteurs : défaire d''abord sa migration. Arrêt, rien n''a été modifié.';
  end if;
  select string_agg(p.oid::regprocedure::text, ', ') into f
  from pg_catalog.pg_proc p join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where n.nspname not in ('commun', 'pg_catalog', 'information_schema')
    and p.proname not like 'commun\_%'
    and p.prosrc ~ '\mcommun\.(accorder|accorder_app|visite_app|gagner_xp|crediter|compte_par_code|compte_par_eleve_app|reprise_ids|compte_par_jeton|fiche|comptes|codes|liens|hauts_faits|elements|xp_journal)\M';
  if f is not null then
    raise exception 'Des fonctions d''applications se servent du compte commun (%) : défaire d''abord leur migration. Arrêt, rien n''a été modifié.', f;
  end if;
end $$;

drop function public.commun_effacer_moi(uuid, text, boolean);
drop function public.commun_quitter(uuid);
drop function public.commun_haut_fait_page(uuid, text, text);
drop function public.commun_evenement_page(uuid, text, text, text);
drop function public.commun_lier_code(uuid, text);
drop function public.commun_renommer(uuid, text);
drop function public.commun_acheter(uuid, text);
drop function public.commun_porter(uuid, jsonb);
drop function public.commun_catalogue();
drop function public.commun_reprise(uuid);
drop function public.commun_entrer(text, integer);
drop function public.commun_creer(text, integer);

drop function commun.menage_si_besoin();
drop function commun.fusionner(uuid, uuid);
drop function commun.fiche(uuid);
drop function commun.verifier_avatar(uuid, jsonb);
drop function commun.accorder_app(text, uuid, text[], jsonb);
drop function commun.visite_app(text, uuid);
drop function commun.compte_par_code(text);
drop function commun.compte_par_eleve_app(text, uuid, boolean);
drop function commun.reprise_ids(text, uuid);
drop function commun.accorder(uuid, text, text[], text);
drop function commun.gagner_xp(uuid, text, text, text, text);
drop function commun.crediter(uuid, text, text, text, integer, text, text, uuid);
drop function commun.creer_compte(text, text, boolean);
drop function commun.compte_par_jeton(uuid);
drop function commun.ouvrir_session(uuid, integer);
drop function commun.nouveau_code(text);
drop function commun.nettoyer_pseudo(text);
drop function commun.nettoyer_texte(text, integer, integer);
drop function commun.normaliser_code(text);

drop table commun.menage;
drop table commun.xp_journal;
drop table commun.activites;
drop table commun.baremes;
drop table commun.elements_debloques;
drop table commun.hauts_faits_gagnes;
drop table commun.recompenses;
drop table commun.hauts_faits;
drop table commun.elements;
drop table commun.emplacements;
drop table commun.sessions;
drop table commun.liens;
drop table commun.codes;
drop table commun.comptes;
drop table commun.mots;
drop table commun.applications;

commit;
