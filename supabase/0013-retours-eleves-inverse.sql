begin;
-- =============================================================================
--  SQL inverse de 0013-retours-eleves.sql
--  Nom de migration : base_unique_0013_retours_eleves_inverse
-- =============================================================================
--  Retire la table des avis des élèves et ses 7 fonctions. Rien d'autre ne
--  change. À lancer avant l'inverse de 0008 (la table pointe vers les classes).
--
--  S'arrête s'il reste des avis : les exporter d'abord (espace enseignant·e,
--  « Exporter »), puis, si l'enseignant le décide, les effacer en collant
--  d'abord la seule ligne :
--      delete from commun.retours;
--  Pour couper les avis sans rien effacer, il suffit de remettre
--  RETOURS_ELEVES à false dans reglages.js : aucune page n'en envoie plus.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.retours') is null then
    raise exception 'La migration 0013 n''est pas là : il n''y a rien à défaire.';
  end if;
  if exists (select 1 from commun.retours) then
    raise exception 'Il reste des avis d''élèves dans commun.retours : les exporter, puis coller « delete from commun.retours; » si l''enseignant le décide. Arrêt, rien n''a été modifié.';
  end if;
end $$;

drop function public.commun_prof_retour_effacer_mot(text, uuid);
drop function public.commun_prof_retours(text, uuid);
drop function public.commun_retour_effacer(text);
drop function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text);
drop function commun.retours_publier();
drop function commun.retour_cle(text);
drop function commun.retour_semaine();
drop table commun.retours;
-- Les compteurs d'envois des avis (commun.essais, application « retours ») partent avec eux.
delete from commun.essais where application = 'retours';

commit;
