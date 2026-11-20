begin;
-- =============================================================================
--  Remise à zéro des comptes des applications, sauf Hello GO (T101)
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration proposé : base_unique_remise_a_zero_2026_11
-- =============================================================================
--  PROPOSITION : rien n'est appliqué. Décision de l'enseignant du 20/11 à
--  14:41 (« on vire tous les comptes sauf ceux de Hello GO et on repart sur du
--  propre ») ; le SQL exact est à lui montrer avant (règle M4).
--
--  **IRRÉVERSIBLE.** Il n'y a pas de SQL inverse : les lignes effacées ne
--  reviennent que par une sauvegarde (l'offre gratuite n'en fait aucune).
--  Une sauvegarde par le tableau de bord (export CSV de chaque table, gardé
--  hors du dépôt, qui est public) est possible avant ; elle n'est pas
--  nécessaire si l'enseignant renonce vraiment à ces données.
--
--  Ce qui est effacé (comptés le 20/11 vers 14:50, par count(*) seulement) :
--    Court-circuit   court_circuit.programmes      3   (programmes des élèves)
--                    court_circuit.eleves          4   (comptes, codes, challenges)
--    Gombessa        public.gb_evenements      2 840   (journal des essais)
--                    public.gb_eleves             25   (comptes, codes, progression)
--                    public.gb_classes             1   (classe et son code)        [partie B]
--                    public.gb_profs               1   (espace enseignant·e, clé)  [partie B]
--    Lagon Arena     lagon.scores, lagon.programmes, lagon.joueurs_jetons,
--                    lagon.joueurs, lagon.salles_secrets, lagon.salles,
--                    lagon.pantheon                0   chacune (rien à effacer
--                                                      aujourd'hui ; effacé si
--                                                      des parties ont eu lieu d'ici là)
--    Alien Python    public.alien_progress, public.alien_students,
--                    public.alien_classes          0   chacune
--
--  Ce qui n'est pas touché :
--    - Hello GO (grand_oral) : 1 espace, 1 classe, 9 élèves, 9 sessions,
--      vérifiés inchangés à la fin ;
--    - SNT 1er jour (public.snt_responses, 45 réponses) : ce ne sont pas des
--      comptes (un questionnaire, sans code ni jeton) ;
--    - les listes de mots (court_circuit.mots, 64), les compteurs de l'accueil
--      de Lagon Arena (lagon.compteurs, 4), le mot de passe du Panthéon
--      (lagon.pantheon_admin, 0), le ménage de Court-circuit, le schéma commun
--      (essais, secret, registre) ;
--    - les objets guilde_* (dans l'autre projet, jamais touchés) ;
--    - l'ancien projet de Lagon Arena : fichier séparé
--      remise-a-zero-ancien-projet-lagon.sql.
--
--  Partie B (gb_classes et gb_profs) : l'espace enseignant·e de Gombessa (la
--  clé PROF-… de l'enseignant) et sa classe (le code ABC-123 distribué). Elle
--  est incluse ici ; pour les garder, supprimer les deux lignes marquées
--  [partie B] avant de lancer le fichier.
--
--  L'ordre est sûr pour les clés étrangères : les tables qui renvoient à une
--  autre sont vidées d'abord (toutes ont aussi on delete cascade, mais on
--  ne s'y fie pas, pour que chaque nombre soit compté). Aucune table n'a de
--  déclencheur (vérifié le 20/11).
--
--  À faire juste après : prévenir que les anciens codes ne marchent plus
--  (pages de Gombessa et de Court-circuit : un code gardé sur l'appareil
--  donnera « Ce code n'existe pas ») ; puis appliquer 0007.
-- =============================================================================

do $$
declare deja boolean := false;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null or to_regclass('grand_oral.eleves') is null
     or to_regclass('court_circuit.eleves') is null or to_regclass('public.gb_eleves') is null
     or to_regclass('lagon.joueurs') is null or to_regclass('public.alien_students') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi, dans son état du 20/11 : une table attendue manque. Arrêt, rien n''a été modifié.';
  end if;
  if to_regclass('commun.liens') is not null then
    execute 'select exists (select 1 from commun.liens)' into deja;
  end if;
  if deja then
    raise exception 'Des comptes communs sont déjà reliés aux applications : cette remise à zéro devait passer avant 0007. Arrêt, rien n''a été modifié.';
  end if;
end $$;

-- Les nombres avant, gardés le temps de la transaction.
create temporary table remise_avant on commit drop as
select 'grand_oral.enseignants' as t, count(*) as n from grand_oral.enseignants union all
select 'grand_oral.classes', count(*) from grand_oral.classes union all
select 'grand_oral.eleves', count(*) from grand_oral.eleves union all
select 'grand_oral.sessions', count(*) from grand_oral.sessions union all
select 'public.snt_responses', count(*) from public.snt_responses union all
select 'court_circuit.mots', count(*) from court_circuit.mots union all
select 'lagon.compteurs', count(*) from lagon.compteurs union all
select 'court_circuit.programmes', count(*) from court_circuit.programmes union all
select 'court_circuit.eleves', count(*) from court_circuit.eleves union all
select 'public.gb_evenements', count(*) from public.gb_evenements union all
select 'public.gb_eleves', count(*) from public.gb_eleves union all
select 'public.gb_classes', count(*) from public.gb_classes union all
select 'public.gb_profs', count(*) from public.gb_profs union all
select 'lagon.scores', count(*) from lagon.scores union all
select 'lagon.programmes', count(*) from lagon.programmes union all
select 'lagon.joueurs_jetons', count(*) from lagon.joueurs_jetons union all
select 'lagon.joueurs', count(*) from lagon.joueurs union all
select 'lagon.salles_secrets', count(*) from lagon.salles_secrets union all
select 'lagon.salles', count(*) from lagon.salles union all
select 'lagon.pantheon', count(*) from lagon.pantheon union all
select 'public.alien_progress', count(*) from public.alien_progress union all
select 'public.alien_students', count(*) from public.alien_students union all
select 'public.alien_classes', count(*) from public.alien_classes;

-- Court-circuit
delete from court_circuit.programmes;
delete from court_circuit.eleves;

-- Expédition Gombessa
delete from public.gb_evenements;
delete from public.gb_eleves;
delete from public.gb_classes;   -- [partie B]
delete from public.gb_profs;     -- [partie B]

-- Lagon Arena (dans la base unique depuis le 19/11)
delete from lagon.scores;
delete from lagon.programmes;
delete from lagon.joueurs_jetons;
delete from lagon.joueurs;
delete from lagon.salles_secrets;
delete from lagon.salles;
delete from lagon.pantheon;

-- Alien Python
delete from public.alien_progress;
delete from public.alien_students;
delete from public.alien_classes;

-- Contrôle : les tables vidées sont vides, et ce qui devait rester est intact.
-- Sinon, arrêt : toute la transaction est annulée, rien n'est effacé.
do $$
declare r record; n bigint; bilan text := '';
begin
  for r in select * from remise_avant loop
    execute format('select count(*) from %s', r.t) into n;
    bilan := bilan || r.t || ' : ' || r.n || ' -> ' || n || E'\n';
    if r.t in ('grand_oral.enseignants', 'grand_oral.classes', 'grand_oral.eleves', 'grand_oral.sessions',
               'public.snt_responses', 'court_circuit.mots', 'lagon.compteurs') then
      if n <> r.n then raise exception 'La table % a changé (% -> %) : arrêt, rien n''a été effacé.', r.t, r.n, n; end if;
    elsif r.t in ('public.gb_classes', 'public.gb_profs') then
      -- partie B : vidée, ou gardée telle quelle si ses deux lignes ont été retirées
      if n <> 0 and n <> r.n then raise exception 'La table % a changé à moitié : arrêt, rien n''a été effacé.', r.t; end if;
    elsif n <> 0 then
      raise exception 'La table % n''est pas vide (% lignes) : arrêt, rien n''a été effacé.', r.t, n;
    end if;
  end loop;
  raise notice E'Remise à zéro, avant -> après :\n%', bilan;
end $$;

commit;
