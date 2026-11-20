begin;
-- =============================================================================
--  Calendrier des vacances, retour en arrière de la migration 0002
--  Nom de migration : vacances_0002_index_resultats_inverse
--  Retire l'index vacances.resultats_case. N'efface aucune donnée.
-- =============================================================================
drop index if exists vacances.resultats_case;
commit;
