begin;
-- =============================================================================
--  Base unique, préalable 1 : les droits par défaut
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0001_droits_par_defaut
-- =============================================================================
--  Pourquoi : aujourd'hui, toute nouvelle table, séquence ou fonction créée
--  dans « public » par le rôle postgres (l'éditeur SQL, apply_migration) est
--  ouverte d'office à anon et à authenticated, et toute nouvelle fonction,
--  dans n'importe quel schéma, est appelable par tout le monde (public).
--  Une table oubliée serait donc lisible par l'API. Après ce fichier, un objet
--  neuf n'est ouvert à personne tant qu'on ne lui donne pas un droit exprès
--  (« grant execute … to anon » pour une fonction d'entrée).
--  Règles des bases : P8 (forme corrigée) et P4.
--
--  Ce que ce fichier change : seulement les droits par défaut du rôle postgres
--  (pg_default_acl), c'est-à-dire les droits des objets créés plus tard.
--   - dans le schéma public : plus aucun droit pour anon ni authenticated sur
--     les nouvelles tables (y compris MAINTAIN, nouveau dans Postgres 17),
--     séquences et fonctions ; postgres et service_role gardent les leurs ;
--   - dans tous les schémas : plus de droit d'exécution pour public sur les
--     nouvelles fonctions. Ce droit est global dans Postgres : un droit par
--     défaut déclaré « in schema » ne peut que s'ajouter aux droits globaux,
--     d'où cette ligne sans « in schema » (constat de l'Atelier de Gombessa).
--
--  Ce que ce fichier ne change pas : aucun objet existant (table, séquence,
--  fonction), aucune ligne, aucune page. Les droits par défaut du rôle
--  supabase_admin (la plateforme) restent : postgres n'a pas le droit de les
--  changer, et seuls les objets créés par la plateforme en relèvent.
--
--  Retour en arrière : 0001-droits-par-defaut-inverse.sql.
--  Mode d'emploi : LISEZMOI.md.
-- =============================================================================

-- Garde-fou : le bon rôle et le bon projet, sinon arrêt avant toute modification.
do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null and to_regclass('snt_premier_jour.reponses') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi (la table des réponses de SNT 1er jour manque) : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- 1. Schéma public : anon et authenticated ne reçoivent plus rien d'office.
alter default privileges for role postgres in schema public
  revoke all on tables from anon, authenticated;
alter default privileges for role postgres in schema public
  revoke all on sequences from anon, authenticated;
alter default privileges for role postgres in schema public
  revoke all on functions from anon, authenticated;

-- 2. Tous les schémas : public ne reçoit plus le droit d'exécution d'office.
--    Pas de « in schema » ici : ce droit est global.
alter default privileges for role postgres
  revoke execute on functions from public;

commit;
