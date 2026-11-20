begin;
-- =============================================================================
--  Calendrier des vacances, retour en arrière de la migration 0001
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : vacances_0001_calendrier_inverse
-- =============================================================================
--  **CE RETOUR EFFACE DES DONNÉES : tous les comptes des élèves, leurs
--  inscriptions, leurs résultats, les espaces des enseignant·e·s et les
--  calendriers. On ne peut pas les retrouver ensuite.** Si un·e élève a déjà
--  joué, l'enseignant exporte d'abord les tables vacances.eleves,
--  vacances.inscriptions et vacances.resultats depuis le tableau de bord
--  (règles des bases, M8). Les agents ne manipulent jamais un export.
--
--  Ce fichier retire : les 22 fonctions public.cv_…, puis le schéma vacances
--  et tout ce qu'il contient (9 tables, fonctions internes). Il ne touche ni au
--  schéma commun ni à une autre application. Les lignes de commun.essais de
--  l'application « vacances » s'effacent seules en 24 h.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regnamespace('vacances') is not null
     and coalesce(obj_description(to_regnamespace('vacances'), 'pg_namespace'), '') not like 'Calendrier des vacances%' then
    raise exception 'Le schéma vacances ne vient pas de la migration 0001 : arrêt, rien n''a été modifié.';
  end if;
end $$;

drop function if exists
  public.cv_calendrier_par_code(text), public.cv_inscription(text, text), public.cv_connexion(text),
  public.cv_rejoindre(uuid, text), public.cv_reprise(uuid), public.cv_calendrier(uuid, uuid),
  public.cv_resultat(uuid, uuid, integer, integer, boolean, integer, integer, integer, integer),
  public.cv_classe(uuid, uuid), public.cv_deconnexion(uuid), public.cv_effacer_moi(uuid),
  public.cv_prof_creer_espace(text), public.cv_prof_ouvrir(text),
  public.cv_prof_creer_calendrier(text, text, date, date, text[], text, text),
  public.cv_prof_modifier_calendrier(text, uuid, text, date, date, text[], text, text),
  public.cv_prof_tableau(text, uuid), public.cv_prof_inscriptions(text, uuid, boolean),
  public.cv_prof_nouveau_code_eleve(text, uuid, uuid), public.cv_prof_renommer_eleve(text, uuid, uuid, text),
  public.cv_prof_retirer_eleve(text, uuid, uuid, text), public.cv_prof_supprimer_calendrier(text, uuid, text),
  public.cv_prof_debloquer_reseau(text), public.cv_prof_nouveau_code(text);

drop schema if exists vacances cascade;

do $$
begin
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'cv\_%') then
    raise exception 'Une fonction public.cv_… reste : arrêt, rien n''a été modifié.';
  end if;
end $$;

commit;
