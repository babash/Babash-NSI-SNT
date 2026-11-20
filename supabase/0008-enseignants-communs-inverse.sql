begin;
-- =============================================================================
--  SQL inverse de 0008-enseignants-communs.sql (version 2)
--  Nom de migration : base_unique_0008_enseignants_communs_inverse
-- =============================================================================
--  Efface les espaces communs des enseignant·e·s, les classes communes, les
--  inscriptions des élèves et les liens vers les classes des applications.
--  Les comptes des élèves, leur XP, leurs crédits et leurs hauts faits restent
--  (0007) ; les attributions d'XP perdent seulement le nom de leur auteur·e.
--  Les espaces des applications et leurs codes ne sont pas touchés. Les codes
--  communs d'enseignant·e·s et les liens de classe cessent de marcher.
--  S'arrête si une application a déclaré ses connecteurs d'enseignant·e·s, ou
--  si une de ses fonctions se sert de ces tables.
-- =============================================================================

do $$
declare f text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.enseignants') is null then
    raise exception '0008 n''est pas appliqué : il n''y a rien à défaire.';
  end if;
  if exists (select 1 from commun.applications a where a.fn_prof_par_code is not null or a.fn_prof_eleves is not null) then
    raise exception 'Une application a déclaré ses connecteurs d''enseignant·e·s : défaire d''abord sa migration. Arrêt, rien n''a été modifié.';
  end if;
  select string_agg(p.oid::regprocedure::text, ', ') into f
  from pg_catalog.pg_proc p join pg_catalog.pg_namespace n on n.oid = p.pronamespace
  where n.nspname not in ('commun', 'pg_catalog', 'information_schema') and p.proname not like 'commun\_%'
    and p.prosrc ~ '\mcommun\.(enseignant_par_code|verifier_enseignant|eleve_visible|enseignants|enseignants_liens|classes|inscriptions|classes_liens)\M';
  if f is not null then
    raise exception 'Des fonctions d''applications s''en servent (%) : défaire d''abord leur migration. Arrêt, rien n''a été modifié.', f;
  end if;
end $$;

drop function public.commun_ma_classe(uuid);
drop function public.commun_rejoindre(uuid, text);
drop function public.commun_classe_par_code(text);
drop function public.commun_prof_supprimer_espace(text, text);
drop function public.commun_prof_debloquer_reseau(text);
drop function public.commun_prof_nouveau_code(text);
drop function public.commun_prof_nouveau_code_eleve(text, uuid);
drop function public.commun_prof_renommer_eleve(text, uuid, text);
drop function public.commun_prof_retirer_eleve(text, uuid, uuid);
drop function public.commun_prof_accorder(text, uuid, text, text);
drop function public.commun_prof_journal_xp(text, uuid);
drop function public.commun_prof_attribuer_xp(text, uuid, integer, text);
drop function public.commun_prof_eleves(text);
drop function public.commun_prof_classe(text, uuid);
drop function public.commun_prof_lier_classe(text, uuid, text, text, boolean);
drop function public.commun_prof_supprimer_classe(text, uuid, text);
drop function public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]);
drop function public.commun_prof_creer_classe(text, text, text[]);
drop function public.commun_prof_lier_code(text, text);
drop function public.commun_prof_ouvrir(text);
drop function public.commun_prof_creer_espace(text, text);
drop function commun.eleve_visible(uuid, uuid);
drop function commun.classe_du_prof(uuid, uuid);
drop function commun.eleves_de(uuid);
drop function commun.verifier_enseignant(text);
drop function commun.enseignant_par_code(text);
drop function commun.nouveau_code_classe();
drop function commun.empreinte_enseignant(text);
drop function commun.nouveau_code_enseignant();
alter table commun.xp_journal drop constraint xp_journal_enseignant_fkey;
update commun.xp_journal set enseignant_id = null where enseignant_id is not null;
alter table commun.applications drop column fn_prof_eleves, drop column fn_prof_par_code;
drop table commun.classes_liens;
drop table commun.inscriptions;
drop table commun.classes;
drop table commun.enseignants_liens;
drop table commun.enseignants;

commit;
