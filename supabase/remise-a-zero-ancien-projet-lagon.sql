begin;
-- =============================================================================
--  Remise à zéro des comptes de l'ancienne base de Lagon Arena (T101)
--  Projet Supabase gkyvaugipddjqjvvpopw (l'ancien projet de Lagon Arena)
--  Nom de migration proposé : lagon_ancien_projet_remise_a_zero_2026_11
-- =============================================================================
--  PROPOSITION : rien n'est appliqué. À montrer à l'enseignant (règle M4).
--  Facultatif : Lagon Arena tourne dans la base unique depuis le 19/11, et
--  ses objets de l'ancien projet devaient de toute façon être retirés vers
--  le 19/12 (n° 9 du plan de la base unique). Ce fichier efface leurs lignes
--  dès maintenant, sans supprimer les tables.
--
--  **IRRÉVERSIBLE**, sans SQL inverse.
--
--  Ce qui est effacé (comptés le 20/11 vers 14:50, par count(*) seulement) :
--    public.tortues 67, public.scores 110, public.joueurs_secret 70,
--    public.joueurs 70, public.salles_secret 7, public.salles 7,
--    public.pantheon 4 (déjà importé, vide, dans la base unique le 19/11).
--  Ce qui n'est pas touché : public.compteurs (4), public.admin_secret (0),
--  et les objets guilde_* : ce fichier ne les nomme dans aucune requête,
--  pas même pour les compter (on n'y touche jamais).
--  Ordre sûr : tortues et joueurs_secret renvoient à joueurs ; joueurs,
--  scores et salles_secret renvoient à salles. Aucun déclencheur.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.tortues') is null or to_regclass('public.joueurs_secret') is null or to_regclass('public.salles_secret') is null then
    raise exception 'Ce fichier est pour l''ancien projet de Lagon Arena (gkyvaugipddjqjvvpopw) : arrêt, rien n''a été modifié.';
  end if;
end $$;

create temporary table remise_avant on commit drop as
select 'public.compteurs' as t, count(*) as n from public.compteurs union all
select 'public.tortues', count(*) from public.tortues union all
select 'public.scores', count(*) from public.scores union all
select 'public.joueurs_secret', count(*) from public.joueurs_secret union all
select 'public.joueurs', count(*) from public.joueurs union all
select 'public.salles_secret', count(*) from public.salles_secret union all
select 'public.salles', count(*) from public.salles union all
select 'public.pantheon', count(*) from public.pantheon;

delete from public.tortues;
delete from public.joueurs_secret;
delete from public.scores;
delete from public.joueurs;
delete from public.salles_secret;
delete from public.salles;
delete from public.pantheon;

do $$
declare r record; n bigint; bilan text := '';
begin
  for r in select * from remise_avant loop
    execute format('select count(*) from %s', r.t) into n;
    bilan := bilan || r.t || ' : ' || r.n || ' -> ' || n || E'\n';
    if r.t = 'public.compteurs' then
      if n <> r.n then raise exception 'La table % a changé : arrêt, rien n''a été effacé.', r.t; end if;
    elsif n <> 0 then
      raise exception 'La table % n''est pas vide : arrêt, rien n''a été effacé.', r.t;
    end if;
  end loop;
  raise notice E'Remise à zéro de l''ancien projet, avant -> après :\n%', bilan;
end $$;

commit;
