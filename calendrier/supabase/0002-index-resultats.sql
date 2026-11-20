begin;
-- =============================================================================
--  Calendrier des vacances, migration 0002 : un index pour la clé étrangère
--  des résultats vers les cases
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : vacances_0002_index_resultats
-- =============================================================================
--  Pourquoi : le conseiller de performance (0001, « clé étrangère sans index
--  couvrant ») signale vacances.resultats_calendrier_id_numero_fkey, sur les
--  colonnes (calendrier_id, numero). Sans index, chaque effacement de case
--  (vacances.generer_cases, quand un calendrier est modifié) parcourt toute la
--  table des résultats pour vérifier qu'aucun résultat ne s'y rattache.
--
--  Ce que ce fichier crée, et rien d'autre : l'index vacances.resultats_case.
--  Il ne touche à aucune ligne, aucun droit, aucune fonction.
--  Le fichier peut être relancé sans effet.
--  Retour en arrière : 0002-index-resultats-inverse.sql (n'efface aucune donnée).
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('vacances.resultats') is null
     or coalesce(obj_description(to_regclass('vacances.resultats'), 'pg_class'), '') not like 'Calendrier des vacances.%' then
    raise exception 'La table vacances.resultats de la migration 0001 manque : arrêt, rien n''a été modifié.';
  end if;
end $$;

create index if not exists resultats_case on vacances.resultats (calendrier_id, numero);
comment on index vacances.resultats_case is
  'Calendrier des vacances. Couvre la clé étrangère des résultats vers les cases (calendrier_id, numero).';

commit;
