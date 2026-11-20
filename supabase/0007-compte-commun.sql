begin;
-- =============================================================================
--  Base unique : le compte commun des élèves, leur avatar, leurs hauts faits
--  et leurs crédits (version 2, après les décisions du 20/11, 14:41 et 14:45)
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0007_compte_commun
--  Fichier proposé : supabase/0007-compte-commun.sql du dépôt du site (T101)
-- =============================================================================
--  PROPOSITION : rien n'est appliqué. À montrer à l'enseignant (règle M4).
--  À appliquer après la remise à zéro des comptes (remise-a-zero-*.sql).
--
--  Pourquoi : un·e élève a un seul code, un seul compte et un seul avatar
--  pour toutes les applications. Ses hauts faits sont réunis ; ils débloquent
--  des éléments d'avatar et rapportent de l'XP. L'XP se dépense en crédits
--  pour des apparences ; elle n'est jamais montrée aux autres élèves, ni
--  comparée, ni classée. Spécification : architecture/compte-commun.md (v2).
--
--  Ce que ce fichier crée, dans le schéma commun (jamais exposé à l'API) :
--   - 16 tables, toutes sous RLS, sans aucune règle ni aucun droit :
--       applications, mots, comptes, codes, liens, sessions, emplacements,
--       elements, hauts_faits, recompenses, hauts_faits_gagnes,
--       elements_debloques, baremes, activites, xp_journal, menage ;
--   - les 64 mots des codes nés sur le site, les 9 applications connues,
--     les 18 emplacements de l'avatar et le barème proposé de l'XP ;
--   - 19 fonctions internes, appelables par aucun rôle de l'API ;
--   - 12 fonctions d'entrée dans public (préfixe commun_), pour anon seul.
--
--  Ce que ce fichier ne change pas : aucune table ni aucune fonction d'une
--  application, aucune ligne existante, aucune page. Les applications se
--  branchent ensuite, chacune par sa propre migration (ses connecteurs).
--  Le catalogue (lignées, éléments, hauts faits, activités) arrive par des
--  migrations séparées (0009 pour l'avatar, une par application).
--
--  Les classes communes et l'espace enseignant·e sont dans 0008.
--  Retour en arrière : 0007-compte-commun-inverse.sql.
-- =============================================================================

-- Garde-fou : le bon rôle, le bon projet, le socle 0003, pgcrypto, et aucun
-- objet de même nom venu d'ailleurs. Sinon, arrêt avant toute modification.
do $$
declare o text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('public.snt_responses') is null and to_regclass('snt_premier_jour.reponses') is null then
    raise exception 'Ce fichier est pour le projet cukahpyqkljiddmimpyi : arrêt, rien n''a été modifié.';
  end if;
  if to_regprocedure('commun.essai_permis(text, text, integer)') is null or to_regprocedure('commun.noter_echec(text, text)') is null then
    raise exception 'Le socle commun (0003) manque : l''appliquer d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if to_regprocedure('extensions.gen_random_bytes(integer)') is null then
    raise exception 'L''extension pgcrypto manque dans le schéma extensions : arrêt, rien n''a été modifié.';
  end if;
  foreach o in array array['commun.applications', 'commun.mots', 'commun.comptes', 'commun.codes', 'commun.liens',
                           'commun.sessions', 'commun.emplacements', 'commun.elements', 'commun.hauts_faits',
                           'commun.recompenses', 'commun.hauts_faits_gagnes', 'commun.elements_debloques',
                           'commun.baremes', 'commun.activites', 'commun.xp_journal', 'commun.menage'] loop
    if to_regclass(o) is not null then
      raise exception '% existe déjà : arrêt, rien n''a été modifié.', o;
    end if;
  end loop;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%') then
    raise exception 'Une fonction public.commun_… existe déjà : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- 1. Les applications et leurs connecteurs
-- -----------------------------------------------------------------------------
create table commun.applications (
  id                 text primary key check (id ~ '^[a-z][a-z_]{1,29}$'),
  nom                text not null check (char_length(nom) between 2 and 60),
  adresse            text check (adresse ~ '^https://babash\.github\.io/[A-Za-z0-9._/-]*$'),
  adresse_prof       text check (adresse_prof ~ '^https://babash\.github\.io/[A-Za-z0-9._/-]*$'),
  mode               text not null check (mode in ('site', 'rattachee', 'native', 'sans_compte')),
  fn_par_code        regprocedure,
  fn_par_id          regprocedure,
  fn_hauts_faits     regprocedure,
  fn_effacer         regprocedure,
  fn_fusion          regprocedure,
  accord_par_page    boolean not null default false,
  pseudo_a_confirmer boolean not null default false,
  plafond_xp_jour    integer not null default 150 check (plafond_xp_jour between 0 and 1000),
  active             boolean not null default true,
  cree_le            timestamptz not null default now()
);
alter table commun.applications enable row level security;
revoke all on commun.applications from public, anon, authenticated;
comment on table commun.applications is
  'Commun. Les applications qui partagent le compte commun, et leurs connecteurs : les fonctions internes de chaque application que le compte commun appelle. Écrite seulement par les migrations. Données d''élèves : non.';
comment on column commun.applications.id is 'L''identifiant de l''application : son schéma (court_circuit, gombessa…), commun pour le site, td pour les feuilles de TD en ligne.';
comment on column commun.applications.nom is 'Le nom affiché aux élèves (« Expédition Gombessa »).';
comment on column commun.applications.adresse is 'L''adresse publique de l''application, sur babash.github.io.';
comment on column commun.applications.adresse_prof is 'L''adresse du tableau de bord enseignant·e de l''application, vers lequel renvoie la page d''une classe commune.';
comment on column commun.applications.mode is 'site : le site lui-même ; rattachee : l''application garde ses comptes et les relie au compte commun ; native : l''application se sert directement du compte commun ; sans_compte : aucune table d''élève (feuilles de TD, QuizzNSI, calendrier).';
comment on column commun.applications.fn_par_code is 'Connecteur facultatif (p_code text) returns table(eleve_id uuid, pseudo text, code_affiche text) : le compte de l''application qui a ce code (forme canonique), s''il existe.';
comment on column commun.applications.fn_par_id is 'Connecteur facultatif (p_eleve uuid) returns table(eleve_id uuid, pseudo text, code_affiche text) : le pseudo et le code d''un compte de l''application.';
comment on column commun.applications.fn_hauts_faits is 'Connecteur facultatif (p_eleve uuid) returns text[] : les hauts faits que la progression déjà enregistrée dans l''application permet d''accorder.';
comment on column commun.applications.fn_effacer is 'Connecteur facultatif (p_eleve uuid) returns void : efface le compte de l''application, quand l''élève demande « Effacer partout ».';
comment on column commun.applications.fn_fusion is 'Connecteur facultatif (p_garder uuid, p_absorber uuid) returns void, pour une application native : reporte ses lignes d''un compte commun sur l''autre avant une fusion.';
comment on column commun.applications.accord_par_page is 'Vrai si la page de l''application, sans fonction de serveur, peut déclarer ses événements et ses hauts faits de genre page (feuilles de TD, QuizzNSI, calendrier).';
comment on column commun.applications.pseudo_a_confirmer is 'Vrai si le pseudo copié de cette application doit être confirmé par l''élève à sa première entrée sur le site (Hello GO : prénom et initiale du nom, qui ne sont plus nécessaires).';
comment on column commun.applications.plafond_xp_jour is 'L''XP qu''un compte peut gagner au plus par jour dans cette application, hauts faits et attributions de l''enseignant·e non compris (anti-abus).';
comment on column commun.applications.active is 'Faux pour une application retirée : ce qui a été gagné reste, elle n''accorde plus rien.';
comment on column commun.applications.cree_le is 'La date de l''inscription de l''application.';

insert into commun.applications (id, nom, adresse, adresse_prof, mode, accord_par_page, pseudo_a_confirmer) values
  ('commun',        'Ressources NSI et SNT',  'https://babash.github.io/Babash-NSI-SNT/eleve/', 'https://babash.github.io/Babash-NSI-SNT/enseignant/', 'site', false, false),
  ('td',            'Feuilles de TD en ligne', 'https://babash.github.io/Babash-NSI-SNT/', null, 'sans_compte', true, false),
  ('calendrier',    'Calendrier des vacances', null, null, 'sans_compte', true, false),
  ('quizz_nsi',     'QuizzNSI',               'https://babash.github.io/QuizzNSI/', null, 'sans_compte', true, false),
  ('gombessa',      'Expédition Gombessa',    'https://babash.github.io/Rappel-1er/', 'https://babash.github.io/Rappel-1er/prof.html', 'rattachee', false, false),
  ('court_circuit', 'Court-circuit',          'https://babash.github.io/court-circuit/', null, 'rattachee', false, false),
  ('grand_oral',    'Hello GO',               null, null, 'rattachee', false, true),
  ('lagon',         'Lagon Arena',            'https://babash.github.io/lagon-arena/', 'https://babash.github.io/lagon-arena/prof.html', 'native', false, false),
  ('alien',         'Alien Python',           'https://babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python/', null, 'native', false, false);

-- -----------------------------------------------------------------------------
-- 2. Les mots des codes nés dans le compte commun
-- -----------------------------------------------------------------------------
create table commun.mots (
  application text not null references commun.applications (id),
  rang        smallint not null check (rang between 0 and 63),
  mot         text not null unique check (mot ~ '^[A-Z]{4,8}$'),
  primary key (application, rang)
);
alter table commun.mots enable row level security;
revoke all on commun.mots from public, anon, authenticated;
comment on table commun.mots is
  'Commun. Les 64 mots des codes tirés par le compte commun, par application : ceux du site (thème : la ville et le réseau), puis ceux de chaque application native. Aucun mot n''est dans la liste d''une autre application, ni le début d''un autre mot (scripts/verifier_listes_mots.py). Données d''élèves : non.';
comment on column commun.mots.application is 'L''application dont la liste contient ce mot (commun pour le site).';
comment on column commun.mots.rang is 'Le rang du mot dans sa liste, de 0 à 63 : un octet tiré au hasard, modulo 64, le choisit sans biais.';
comment on column commun.mots.mot is 'Le mot, en majuscules sans accent, de 4 à 8 lettres.';

insert into commun.mots (application, rang, mot) values
('commun', 0, 'TROTTOIR'), ('commun', 1, 'VENELLE'), ('commun', 2, 'IMPASSE'), ('commun', 3, 'ESCALIER'),
('commun', 4, 'TOITURE'), ('commun', 5, 'VERANDA'), ('commun', 6, 'PYLONE'), ('commun', 7, 'LAMPION'),
('commun', 8, 'FRESQUE'), ('commun', 9, 'POCHOIR'), ('commun', 10, 'GRAFFITI'), ('commun', 11, 'SKATE'),
('commun', 12, 'ROLLER'), ('commun', 13, 'SCOOTER'), ('commun', 14, 'VELO'), ('commun', 15, 'TAXI'),
('commun', 16, 'METRO'), ('commun', 17, 'TRAM'), ('commun', 18, 'PONT'), ('commun', 19, 'TUNNEL'),
('commun', 20, 'QUAI'), ('commun', 21, 'PARKING'), ('commun', 22, 'GARAGE'), ('commun', 23, 'KIOSQUE'),
('commun', 24, 'MARCHE'), ('commun', 25, 'ENSEIGNE'), ('commun', 26, 'VITRINE'), ('commun', 27, 'BITUME'),
('commun', 28, 'BETON'), ('commun', 29, 'BRIQUE'), ('commun', 30, 'GRILLE'), ('commun', 31, 'CLOTURE'),
('commun', 32, 'PORTAIL'), ('commun', 33, 'PARABOLE'), ('commun', 34, 'ROUTEUR'), ('commun', 35, 'MODEM'),
('commun', 36, 'BOITIER'), ('commun', 37, 'WIFI'), ('commun', 38, 'RESEAU'), ('commun', 39, 'FIBRE'),
('commun', 40, 'PAQUET'), ('commun', 41, 'OCTET'), ('commun', 42, 'CLAVIER'), ('commun', 43, 'ECRAN'),
('commun', 44, 'MANETTE'), ('commun', 45, 'BONNET'), ('commun', 46, 'AMPLI'), ('commun', 47, 'SIRENE'),
('commun', 48, 'ROCADE'), ('commun', 49, 'AVENUE'), ('commun', 50, 'FANAL'), ('commun', 51, 'VIADUC'),
('commun', 52, 'PERRON'), ('commun', 53, 'HANGAR'), ('commun', 54, 'ENTREPOT'), ('commun', 55, 'DOCK'),
('commun', 56, 'DEPOT'), ('commun', 57, 'CARGO'), ('commun', 58, 'GRUE'), ('commun', 59, 'CHANTIER'),
('commun', 60, 'GOUDRON'), ('commun', 61, 'AEROSOL'), ('commun', 62, 'RADIO'), ('commun', 63, 'BALADEUR');

-- -----------------------------------------------------------------------------
-- 3. Les comptes, leurs codes, leurs liens et leurs sessions
-- -----------------------------------------------------------------------------
create table commun.comptes (
  id                 uuid primary key default gen_random_uuid(),
  pseudo             text not null check (char_length(pseudo) between 2 and 24),
  pseudo_provisoire  boolean not null default false,
  origine            text not null references commun.applications (id),
  avatar             jsonb not null default '{"v": 1, "porte": {}, "teintes": {}}'::jsonb
                     check (jsonb_typeof(avatar) = 'object' and octet_length(avatar::text) <= 4000),
  xp                 integer not null default 0 check (xp >= 0),
  credits            integer not null default 0 check (credits >= 0),
  cree_le            timestamptz not null default now(),
  vu_le              timestamptz not null default now()
);
create index comptes_vu_le on commun.comptes (vu_le);
alter table commun.comptes enable row level security;
revoke all on commun.comptes from public, anon, authenticated;
comment on table commun.comptes is
  'Commun. Un compte par élève, pour toutes les applications : son prénom ou son pseudo (jamais le nom de famille), l''avatar porté, son XP et ses crédits. L''XP n''est montrée à aucun·e élève ; les crédits seulement à l''élève, comme un solde à dépenser. Effacé 12 mois après la dernière visite, ou à la demande de l''élève. Données d''élèves : oui.';
comment on column commun.comptes.id is 'L''identifiant du compte, tiré au hasard. Pour une application native, c''est aussi l''identifiant de l''élève dans ses tables.';
comment on column commun.comptes.pseudo is 'Le prénom ou le pseudo choisi par l''élève, de 2 à 24 caractères, jamais le nom de famille ni son initiale.';
comment on column commun.comptes.pseudo_provisoire is 'Vrai si le pseudo a été copié d''une application qui demande une confirmation (Hello GO) : la page demande à l''élève de choisir son pseudo.';
comment on column commun.comptes.origine is 'L''application où le compte est né : le site (commun) ou l''application du premier code.';
comment on column commun.comptes.avatar is 'L''avatar porté, au format 1 de la spécification : {"v": 1, "porte": {emplacement: élément}, "teintes": {emplacement: teinte}}, dont la lignée (emplacement lignee). Vérifié par commun.verifier_avatar. 4 000 octets au plus.';
comment on column commun.comptes.xp is 'L''XP gagnée depuis la création du compte : elle ne baisse jamais (les achats n''y touchent pas). Somme des gains du journal. Cachée à tous les élèves ; vue par l''enseignant·e de ses classes.';
comment on column commun.comptes.credits is 'Les crédits à dépenser en apparences : l''XP gagnée moins les achats. Jamais négatifs. Montrés à l''élève seul·e, comme un solde.';
comment on column commun.comptes.cree_le is 'La date de création du compte commun.';
comment on column commun.comptes.vu_le is 'La date de la dernière visite, sur le site ou dans une application branchée. Sert au ménage des 12 mois.';

create table commun.codes (
  code          text primary key check (code ~ '^[A-Z]{8,32}[0-9]{3,4}$'),
  code_affiche  text not null check (code_affiche ~ '^[A-Z]{4,8}(-[A-Z]{4,8}){1,2}-[0-9]{3,4}$'),
  compte_id     uuid not null references commun.comptes (id) on delete cascade,
  application   text not null references commun.applications (id),
  principal     boolean not null default true,
  cree_le       timestamptz not null default now()
);
create index codes_compte on commun.codes (compte_id);
create unique index codes_un_principal on commun.codes (compte_id) where principal;
alter table commun.codes enable row level security;
revoke all on commun.codes from public, anon, authenticated;
comment on table commun.codes is
  'Commun. Les codes tirés par le compte commun (codes nés sur le site ou dans une application native) : 2 mots et 3 chiffres. Les codes des applications rattachées restent dans leurs tables et sont lus par leurs connecteurs. Secret. Données d''élèves : oui.';
comment on column commun.codes.code is 'Le code sous sa forme canonique (majuscules, sans séparateur) : CLAVIERFRESQUE482. Unique dans tout le projet, grâce aux listes de mots disjointes.';
comment on column commun.codes.code_affiche is 'Le code tel qu''on l''affiche et l''imprime : CLAVIER-FRESQUE-482.';
comment on column commun.codes.compte_id is 'Le compte que ce code ouvre.';
comment on column commun.codes.application is 'L''application dont la liste de mots a servi au tirage.';
comment on column commun.codes.principal is 'Vrai pour le code à donner en premier à l''élève ; faux pour un code gagné par une fusion, qui reste valable.';
comment on column commun.codes.cree_le is 'La date du tirage.';

create table commun.liens (
  application   text not null references commun.applications (id),
  eleve_app_id  uuid not null,
  compte_id     uuid not null references commun.comptes (id) on delete cascade,
  depuis        timestamptz not null default now(),
  primary key (application, eleve_app_id)
);
create index liens_compte on commun.liens (compte_id);
alter table commun.liens enable row level security;
revoke all on commun.liens from public, anon, authenticated;
comment on table commun.liens is
  'Commun. Les comptes des applications rattachées reliés à chaque compte commun : un code de Gombessa, de Court-circuit ou de Hello GO ouvre le compte commun qui lui est relié. Effacés avec le compte commun ; le compte de l''application, lui, reste. Données d''élèves : oui (un lien entre deux comptes).';
comment on column commun.liens.application is 'L''application rattachée.';
comment on column commun.liens.eleve_app_id is 'L''identifiant de l''élève dans cette application (gb_eleves.id, court_circuit.eleves.id…).';
comment on column commun.liens.compte_id is 'Le compte commun relié.';
comment on column commun.liens.depuis is 'La date du lien.';

create table commun.sessions (
  jeton        uuid primary key default gen_random_uuid(),
  compte_id    uuid not null references commun.comptes (id) on delete cascade,
  garde_jours  smallint not null default 1 check (garde_jours in (1, 30)),
  cree_le      timestamptz not null default now(),
  vu_le        timestamptz not null default now()
);
create index sessions_compte on commun.sessions (compte_id);
alter table commun.sessions enable row level security;
revoke all on commun.sessions from public, anon, authenticated;
comment on table commun.sessions is
  'Commun. Les jetons de session du compte commun : un par appareil où l''élève est entré·e avec son code, 5 au plus (le plus ancien part). Un jeton vaut 1 jour (poste partagé, par défaut) ou 30 jours depuis son dernier usage (« mon appareil »). Données d''élèves : oui (un jeton au hasard et deux dates).';
comment on column commun.sessions.jeton is 'Le jeton, tiré au hasard, que la page garde et renvoie à chaque appel. Secret.';
comment on column commun.sessions.compte_id is 'Le compte ouvert par ce jeton.';
comment on column commun.sessions.garde_jours is '1 : le jeton expire un jour après sa création (poste partagé) ; 30 : il expire 30 jours après son dernier usage (appareil personnel).';
comment on column commun.sessions.cree_le is 'La date de l''entrée avec le code.';
comment on column commun.sessions.vu_le is 'La date du dernier usage du jeton.';

-- -----------------------------------------------------------------------------
-- 4. L'avatar : les emplacements et les éléments
-- -----------------------------------------------------------------------------
create table commun.emplacements (
  id           text primary key check (id ~ '^[a-z_]{2,20}$'),
  nom          text not null,
  genre        text not null check (genre in ('identite', 'tenue', 'compagnon', 'geste', 'decor')),
  plan         smallint check (plan between 0 and 100),
  obligatoire  boolean not null default false
);
alter table commun.emplacements enable row level security;
revoke all on commun.emplacements from public, anon, authenticated;
comment on table commun.emplacements is
  'Commun. Les emplacements de l''avatar (la lignée, le corps, la coiffure, la tête, la main, le familier, l''attitude…), avec leur plan de dessin par défaut. Le format ne dépend pas du dessin : chaque élément est une référence, que la page dessine avec sa planche. Données d''élèves : non.';
comment on column commun.emplacements.id is 'L''identifiant de l''emplacement, qui ouvre l''identifiant de ses éléments (tete:…).';
comment on column commun.emplacements.nom is 'Le nom affiché dans la loge de l''avatar.';
comment on column commun.emplacements.genre is 'identite : toujours gratuit (lignée, corps, visage, coiffure, marques) : tout ce qui sert à se reconnaître ; tenue : vêtements et accessoires ; compagnon : le familier ; geste : une animation (attitude, réussite, erreur) ; decor : le fond et les effets.';
comment on column commun.emplacements.plan is 'L''ordre de dessin par défaut, du fond (0) vers l''avant (100) ; vide pour la lignée (elle choisit les dessins du corps) et pour un geste. Un élément peut avoir des parties devant et derrière : c''est sa planche qui le dit.';
comment on column commun.emplacements.obligatoire is 'Vrai si l''avatar a toujours un élément à cet emplacement (lignée, corps, visage) : la page prend l''élément libre par défaut s''il manque.';

insert into commun.emplacements (id, nom, genre, plan, obligatoire) values
  ('lignee',    'Lignée',              'identite',  null, true),
  ('fond',      'Décor',               'decor',     0,    false),
  ('dos',       'Dos',                 'tenue',     10,   false),
  ('corps',     'Corps',               'identite',  30,   true),
  ('marque',    'Marques et implants', 'identite',  32,   false),
  ('bas',       'Bas',                 'tenue',     40,   false),
  ('pieds',     'Chaussures',          'tenue',     42,   false),
  ('haut',      'Haut',                'tenue',     50,   false),
  ('visage',    'Visage',              'identite',  60,   true),
  ('coiffure',  'Coiffure',            'identite',  65,   false),
  ('yeux',      'Lunettes et masques', 'tenue',     70,   false),
  ('tete',      'Tête',                'tenue',     75,   false),
  ('main',      'Dans la main',        'tenue',     80,   false),
  ('familier',  'Familier',            'compagnon', 90,   false),
  ('effet',     'Effet',               'decor',     95,   false),
  ('attitude',  'Attitude',            'geste',     null, false),
  ('succes',    'Réussite',            'geste',     null, false),
  ('erreur',    'Erreur',              'geste',     null, false);

create table commun.elements (
  id           text primary key check (id ~ '^[a-z_]{2,20}:[a-z0-9-]{1,40}$'),
  emplacement  text not null references commun.emplacements (id),
  nom          text not null check (char_length(nom) between 2 and 40),
  description  text not null default '' check (char_length(description) <= 200),
  acces        text not null check (acces in ('libre', 'haut_fait', 'credits')),
  prix         integer check (prix between 1 and 2000),
  lignees      text[] check (lignees is null or cardinality(lignees) between 1 and 20),
  teintable    boolean not null default false,
  ordre        smallint not null default 0,
  actif        boolean not null default true,
  ajoute_le    timestamptz not null default now(),
  check (split_part(id, ':', 1) = emplacement),
  check ((acces = 'credits') = (prix is not null))
);
alter table commun.elements enable row level security;
revoke all on commun.elements from public, anon, authenticated;
comment on table commun.elements is
  'Commun. Le catalogue des éléments d''avatar : un identifiant, un nom, une description et la façon de l''obtenir (libre, gagné par un haut fait, ou acheté avec des crédits). Le dessin n''est pas ici : la page le trouve dans sa planche, par l''identifiant. Un élément n''est jamais supprimé : retiré du catalogue, il reste à qui l''a. Données d''élèves : non.';
comment on column commun.elements.id is 'L''identifiant : l''emplacement, deux-points, un nom court (tete:casque-led, lignee:cyber). Ne change jamais : il sert de clé à la planche.';
comment on column commun.elements.emplacement is 'L''emplacement de l''élément (le début de son identifiant).';
comment on column commun.elements.nom is 'Le nom affiché (« Casque à diodes »).';
comment on column commun.elements.description is 'Une phrase de description, 200 caractères au plus.';
comment on column commun.elements.acces is 'libre : à tout le monde dès le début (toujours le cas pour l''identité) ; haut_fait : débloqué par un haut fait (table recompenses), ne s''achète pas ; credits : s''achète avec des crédits.';
comment on column commun.elements.prix is 'Le prix en crédits, pour un élément de genre credits seulement.';
comment on column commun.elements.lignees is 'Les lignées (identifiants lignee:…) avec lesquelles l''élément va, quand il ne va pas avec toutes ; vide : toutes.';
comment on column commun.elements.teintable is 'Vrai si l''élève peut choisir sa teinte (le champ teintes de l''avatar).';
comment on column commun.elements.ordre is 'L''ordre d''affichage dans la loge.';
comment on column commun.elements.actif is 'Faux pour un élément retiré du catalogue : il n''est plus proposé, mais qui l''a le garde et peut le porter.';
comment on column commun.elements.ajoute_le is 'La date de l''ajout au catalogue.';

-- -----------------------------------------------------------------------------
-- 5. Les hauts faits : le catalogue, les récompenses, ce qui est gagné
-- -----------------------------------------------------------------------------
create table commun.hauts_faits (
  application  text not null references commun.applications (id),
  id           text not null check (id ~ '^[a-z0-9-]{2,40}$'),
  nom          text not null check (char_length(nom) between 2 and 40),
  description  text not null check (char_length(description) between 5 and 200),
  categorie    text not null check (categorie in ('premiers_pas', 'exploration', 'perseverance', 'creation', 'entraide', 'maitrise')),
  secret       boolean not null default false,
  indice       text check (char_length(indice) <= 120),
  accord       text not null default 'serveur' check (accord in ('serveur', 'page', 'enseignant')),
  xp           smallint not null default 20 check (xp between 0 and 200),
  ordre        smallint not null default 0,
  actif        boolean not null default true,
  ajoute_le    timestamptz not null default now(),
  primary key (application, id),
  check (not secret or indice is not null)
);
alter table commun.hauts_faits enable row level security;
revoke all on commun.hauts_faits from public, anon, authenticated;
comment on table commun.hauts_faits is
  'Commun. Le catalogue des hauts faits de chaque application : ce qu''il faut faire, en une phrase. Ni rang, ni série de jours, ni comparaison entre élèves : un haut fait se gagne une fois et ne se perd jamais. Écrit par les migrations des applications. Données d''élèves : non.';
comment on column commun.hauts_faits.application is 'L''application qui accorde ce haut fait (commun pour ceux de l''enseignant·e).';
comment on column commun.hauts_faits.id is 'L''identifiant court, unique dans l''application (premier-circuit). Ne change jamais.';
comment on column commun.hauts_faits.nom is 'Le nom affiché (« Premier circuit »), 40 caractères au plus.';
comment on column commun.hauts_faits.description is 'Ce qu''il faut faire, en une phrase de 200 caractères au plus.';
comment on column commun.hauts_faits.categorie is 'Le genre de haut fait, pour ranger la collection : premiers_pas, exploration, perseverance, creation, entraide, maitrise.';
comment on column commun.hauts_faits.secret is 'Vrai pour une surprise : avant qu''il soit gagné, on n''en montre que l''indice.';
comment on column commun.hauts_faits.indice is 'L''indice montré à la place du nom et de la description d''un haut fait secret.';
comment on column commun.hauts_faits.accord is 'Qui l''accorde : serveur (une fonction de l''application), page (la page d''une application sans serveur), enseignant (l''enseignant·e).';
comment on column commun.hauts_faits.xp is 'L''XP rapportée une fois, quand le haut fait est gagné (20 par défaut). Hors du plafond journalier.';
comment on column commun.hauts_faits.ordre is 'L''ordre d''affichage dans la collection de l''application.';
comment on column commun.hauts_faits.actif is 'Faux pour un haut fait retiré : il ne s''accorde plus, mais qui l''a le garde.';
comment on column commun.hauts_faits.ajoute_le is 'La date de l''ajout au catalogue.';

create table commun.recompenses (
  application  text not null,
  haut_fait    text not null,
  element_id   text not null references commun.elements (id),
  primary key (application, haut_fait, element_id),
  foreign key (application, haut_fait) references commun.hauts_faits (application, id)
);
create index recompenses_element on commun.recompenses (element_id);
alter table commun.recompenses enable row level security;
revoke all on commun.recompenses from public, anon, authenticated;
comment on table commun.recompenses is
  'Commun. Les éléments d''avatar que débloque chaque haut fait. Un élément peut être débloqué par plusieurs hauts faits, d''applications différentes. Données d''élèves : non.';
comment on column commun.recompenses.application is 'L''application du haut fait.';
comment on column commun.recompenses.haut_fait is 'L''identifiant du haut fait.';
comment on column commun.recompenses.element_id is 'L''élément débloqué.';

create table commun.hauts_faits_gagnes (
  compte_id    uuid not null references commun.comptes (id) on delete cascade,
  application  text not null,
  haut_fait    text not null,
  gagne_le     timestamptz not null default now(),
  par          text not null check (par in ('application', 'reprise', 'page', 'enseignant')),
  primary key (compte_id, application, haut_fait),
  foreign key (application, haut_fait) references commun.hauts_faits (application, id)
);
alter table commun.hauts_faits_gagnes enable row level security;
revoke all on commun.hauts_faits_gagnes from public, anon, authenticated;
comment on table commun.hauts_faits_gagnes is
  'Commun. Les hauts faits gagnés par chaque élève, toutes applications réunies : une ligne par haut fait, sans nombre ni score. Vus par l''élève, ses camarades de classe et ses enseignant·e·s. Jamais effacés, sauf avec le compte. Données d''élèves : oui.';
comment on column commun.hauts_faits_gagnes.compte_id is 'Le compte de l''élève.';
comment on column commun.hauts_faits_gagnes.application is 'L''application du haut fait.';
comment on column commun.hauts_faits_gagnes.haut_fait is 'L''identifiant du haut fait.';
comment on column commun.hauts_faits_gagnes.gagne_le is 'La date où il a été gagné (la plus ancienne, après une fusion).';
comment on column commun.hauts_faits_gagnes.par is 'Comment il a été accordé : application, reprise (progression déjà enregistrée), page, enseignant.';

create table commun.elements_debloques (
  compte_id   uuid not null references commun.comptes (id) on delete cascade,
  element_id  text not null references commun.elements (id),
  origine     text not null default 'haut_fait' check (origine in ('haut_fait', 'achat')),
  depuis      timestamptz not null default now(),
  primary key (compte_id, element_id)
);
alter table commun.elements_debloques enable row level security;
revoke all on commun.elements_debloques from public, anon, authenticated;
comment on table commun.elements_debloques is
  'Commun. Les éléments d''avatar débloqués par chaque élève, par un haut fait ou par un achat. Gardés même si le catalogue change : on ne perd jamais ce qu''on a gagné ou acheté. Les éléments libres n''y sont pas. Données d''élèves : oui.';
comment on column commun.elements_debloques.compte_id is 'Le compte de l''élève.';
comment on column commun.elements_debloques.element_id is 'L''élément débloqué.';
comment on column commun.elements_debloques.origine is 'haut_fait : une récompense ; achat : acheté avec des crédits.';
comment on column commun.elements_debloques.depuis is 'La date du déblocage.';

-- -----------------------------------------------------------------------------
-- 6. L'XP : le barème, les activités reconnues, le journal
-- -----------------------------------------------------------------------------
create table commun.baremes (
  application      text not null references commun.applications (id),
  evenement        text not null check (evenement ~ '^[a-z_]{2,30}$'),
  nom              text not null check (char_length(nom) between 2 and 60),
  xp               smallint not null check (xp between 1 and 200),
  activite_connue  boolean not null default false,
  primary key (application, evenement)
);
alter table commun.baremes enable row level security;
revoke all on commun.baremes from public, anon, authenticated;
comment on table commun.baremes is
  'Commun. Le barème de l''XP : ce que rapporte chaque genre d''événement de chaque application. La page ne choisit jamais le montant. Écrit par les migrations. Données d''élèves : non.';
comment on column commun.baremes.application is 'L''application de l''événement.';
comment on column commun.baremes.evenement is 'Le genre d''événement (feuille_validee, quiz_termine, mission_reussie…).';
comment on column commun.baremes.nom is 'Le nom affiché dans le journal (« Feuille de TD validée en ligne »).';
comment on column commun.baremes.xp is 'L''XP rapportée par un événement, de 1 à 200.';
comment on column commun.baremes.activite_connue is 'Vrai si l''événement doit porter la clé d''une activité inscrite (table activites) : c''est le cas de tout ce qu''une page déclare elle-même.';

insert into commun.baremes (application, evenement, nom, xp, activite_connue) values
  ('td',            'feuille_validee',  'Feuille de TD validée en ligne',            30, true),
  ('td',            'exercice_valide',  'Exercice de TD validé en ligne',             5, true),
  ('quizz_nsi',     'cours_quiz_suivi', 'Cours-quiz suivi jusqu''au bout',            15, true),
  ('calendrier',    'mini_jeu_fait',    'Mini-jeu du calendrier des vacances',        5, true),
  ('gombessa',      'mission_reussie',  'Mission réussie dans Expédition Gombessa',  10, false),
  ('court_circuit', 'challenge_reussi', 'Challenge réussi dans Court-circuit',       10, false),
  ('grand_oral',    'etape_dossier',    'Étape du dossier de Grand oral',            15, false),
  ('lagon',         'manche_jouee',     'Manche jouée dans Lagon Arena',              5, false),
  ('alien',         'exercice_reussi',  'Exercice réussi dans Alien Python',          5, false);

create table commun.activites (
  application  text not null,
  evenement    text not null,
  cle          text not null check (cle ~ '^[a-z0-9][a-z0-9:/_.-]{0,79}$'),
  nom          text not null check (char_length(nom) between 2 and 80),
  actif        boolean not null default true,
  primary key (application, cle),
  foreign key (application, evenement) references commun.baremes (application, evenement)
);
alter table commun.activites enable row level security;
revoke all on commun.activites from public, anon, authenticated;
comment on table commun.activites is
  'Commun. Les activités reconnues (une feuille de TD, un cours-quiz, un mini-jeu du calendrier) : une page ne peut déclarer que ces clés, une seule fois par élève. Générée depuis la bibliothèque du site par un script. Données d''élèves : non.';
comment on column commun.activites.application is 'L''application de l''activité.';
comment on column commun.activites.evenement is 'Le genre d''événement qu''elle déclenche (son barème).';
comment on column commun.activites.cle is 'La clé de l''activité, unique dans l''application (td:poo-td1, quiz:piles-files, cal:2026-12-21:memoire).';
comment on column commun.activites.nom is 'Le nom affiché dans le journal.';
comment on column commun.activites.actif is 'Faux pour une activité retirée : elle ne rapporte plus rien.';

create table commun.xp_journal (
  id             uuid primary key default gen_random_uuid(),
  compte_id      uuid not null references commun.comptes (id) on delete cascade,
  application    text not null references commun.applications (id),
  evenement      text not null check (evenement ~ '^[a-z_]{2,30}$'),
  cle            text check (cle ~ '^[a-z0-9][a-z0-9:/_.-]{0,79}$'),
  xp             integer not null check (xp between -2000 and 200 and xp <> 0),
  motif          text check (char_length(motif) between 3 and 80),
  enseignant_id  uuid,
  par            text not null check (par in ('application', 'page', 'haut_fait', 'enseignant', 'achat')),
  cree_le        timestamptz not null default now()
);
create unique index xp_journal_une_fois on commun.xp_journal (compte_id, application, cle) where cle is not null;
create index xp_journal_compte on commun.xp_journal (compte_id, cree_le);
alter table commun.xp_journal enable row level security;
revoke all on commun.xp_journal from public, anon, authenticated;
comment on table commun.xp_journal is
  'Commun. Le journal de l''XP de chaque élève : chaque gain (événement, haut fait, attribution d''un·e enseignant·e, avec son motif) et chaque achat (montant négatif). Une même activité ne rapporte qu''une fois. Vu par l''élève (sans total d''XP) et par ses enseignant·e·s. Données d''élèves : oui.';
comment on column commun.xp_journal.id is 'L''identifiant de la ligne, tiré au hasard.';
comment on column commun.xp_journal.compte_id is 'Le compte de l''élève.';
comment on column commun.xp_journal.application is 'L''application de l''événement (commun pour une attribution de l''enseignant·e ou un achat).';
comment on column commun.xp_journal.evenement is 'Le genre d''événement : celui du barème, ou haut_fait, attribution, achat.';
comment on column commun.xp_journal.cle is 'La clé qui empêche de gagner deux fois la même chose (td:poo-td1, hf:premier-circuit, achat:tete:casque-led) ; vide pour une attribution.';
comment on column commun.xp_journal.xp is 'L''XP gagnée (positive) ou les crédits dépensés (négatifs).';
comment on column commun.xp_journal.motif is 'Le motif court d''une attribution par l''enseignant·e (« Aide à un camarade »), 80 caractères au plus.';
comment on column commun.xp_journal.enseignant_id is 'L''enseignant·e qui a attribué l''XP (commun.enseignants, avec 0008) ; vide sinon.';
comment on column commun.xp_journal.par is 'D''où vient la ligne : application, page, haut_fait, enseignant, achat.';
comment on column commun.xp_journal.cree_le is 'La date de la ligne.';

create table commun.menage (
  seule_ligne  boolean primary key default true check (seule_ligne),
  fait_le      timestamptz not null default now()
);
alter table commun.menage enable row level security;
revoke all on commun.menage from public, anon, authenticated;
insert into commun.menage default values;
comment on table commun.menage is
  'Commun. La date du dernier ménage des comptes communs et des sessions (une seule ligne) : il se fait au plus une fois par heure. Données d''élèves : non.';
comment on column commun.menage.seule_ligne is 'Toujours vrai : garantit que la table n''a qu''une ligne.';
comment on column commun.menage.fait_le is 'La date du dernier ménage.';

-- -----------------------------------------------------------------------------
-- 7. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- La forme canonique d'un code : majuscules, sans accent ni séparateur.
create function commun.normaliser_code(p_code text)
returns text language sql immutable set search_path = '' as $$
  select regexp_replace(upper(translate(replace(replace(left(coalesce(p_code, ''), 80), 'œ', 'oe'), 'Œ', 'OE'),
    'àâäáãåçéèêëíìîïñóòôöõúùûüýÿÀÂÄÁÃÅÇÉÈÊËÍÌÎÏÑÓÒÔÖÕÚÙÛÜÝ',
    'aaaaaaceeeeiiiinooooouuuuyyAAAAAACEEEEIIIINOOOOOUUUUY')), '[^A-Z0-9]', '', 'g')
$$;

-- Un texte propre (espaces réduits, sans caractère de contrôle ni invisible),
-- de p_min à p_max caractères, sinon null.
create function commun.nettoyer_texte(p_texte text, p_min integer, p_max integer)
returns text language sql immutable set search_path = '' as $$
  select case when char_length(x.t) between p_min and p_max
               and x.t !~ ('[' || chr(1) || '-' || chr(31) || chr(127) || '-' || chr(159) || chr(173) || chr(8203) || '-' || chr(8207)
                           || chr(8232) || '-' || chr(8238) || chr(8288) || '-' || chr(8303) || chr(65279) || ']')
              then x.t end
  from (select btrim(regexp_replace(left(coalesce(p_texte, ''), 200), '\s+', ' ', 'g')) as t) x
$$;

-- Un prénom ou un pseudo propre (2 à 24 caractères), sinon null.
create function commun.nettoyer_pseudo(p_texte text)
returns text language sql immutable set search_path = '' as $$
  select commun.nettoyer_texte(p_texte, 2, 24)
$$;

-- Un code neuf de 2 mots et 3 chiffres, tiré sans biais dans la liste d'une
-- application (64 mots : un octet modulo 64 ; les chiffres par rejet).
create function commun.nouveau_code(p_app text, out code text, out code_affiche text)
language plpgsql volatile set search_path = '' as $$
declare b bytea; v integer; w1 text; w2 text; d text; essai integer := 0;
begin
  if (select count(*) from commun.mots m where m.application = p_app) <> 64 then
    raise exception 'La liste de mots de % n''a pas 64 mots.', p_app;
  end if;
  loop
    essai := essai + 1;
    if essai > 200 then raise exception 'Impossible de tirer un code libre.'; end if;
    b := extensions.gen_random_bytes(4);
    v := get_byte(b, 2) * 256 + get_byte(b, 3);
    continue when v >= 64000;
    select m.mot into w1 from commun.mots m where m.application = p_app and m.rang = get_byte(b, 0) % 64;
    select m.mot into w2 from commun.mots m where m.application = p_app and m.rang = get_byte(b, 1) % 64;
    d := lpad((v % 1000)::text, 3, '0');
    code := w1 || w2 || d;
    code_affiche := w1 || '-' || w2 || '-' || d;
    exit when not exists (select 1 from commun.codes c where c.code = nouveau_code.code);
  end loop;
end $$;

-- Ouvre une session : un nouveau jeton, 5 au plus par compte.
create function commun.ouvrir_session(p_compte uuid, p_garde_jours integer)
returns uuid language plpgsql volatile set search_path = '' as $$
declare j uuid;
begin
  insert into commun.sessions (compte_id, garde_jours)
  values (p_compte, case when p_garde_jours = 30 then 30 else 1 end)
  returning jeton into j;
  delete from commun.sessions s
   where s.compte_id = p_compte
     and s.jeton not in (select x.jeton from commun.sessions x where x.compte_id = p_compte order by x.vu_le desc limit 5);
  update commun.comptes c set vu_le = now() where c.id = p_compte;
  return j;
end $$;

-- Le compte d'un jeton valable (et la visite notée), sinon null.
create function commun.compte_par_jeton(p_jeton uuid)
returns uuid language plpgsql volatile set search_path = '' as $$
declare v uuid;
begin
  update commun.sessions s set vu_le = now()
   where s.jeton = p_jeton
     and ((s.garde_jours = 1 and s.cree_le > now() - interval '1 day')
          or (s.garde_jours = 30 and s.vu_le > now() - interval '30 days'))
  returning s.compte_id into v;
  if v is not null then
    update commun.comptes c set vu_le = now() where c.id = v and c.vu_le < now() - interval '10 minutes';
  end if;
  return v;
end $$;

-- Crée un compte commun (pseudo déjà nettoyé).
create function commun.creer_compte(p_pseudo text, p_origine text, p_provisoire boolean default false)
returns uuid language sql volatile set search_path = '' as $$
  insert into commun.comptes (pseudo, origine, pseudo_provisoire) values (p_pseudo, p_origine, p_provisoire) returning id
$$;

-- Ajoute une ligne au journal de l'XP et met à jour l'XP et les crédits.
-- Renvoie l'XP gagnée (0 si la clé a déjà rapporté, ou si le plafond du jour
-- est atteint). Seule cette fonction et commun.acheter écrivent le journal.
create function commun.crediter(p_compte uuid, p_app text, p_evenement text, p_cle text, p_xp integer,
                                p_par text, p_motif text default null, p_enseignant uuid default null)
returns integer language plpgsql volatile set search_path = '' as $$
declare v integer := p_xp; deja integer;
begin
  if p_compte is null or v is null or v <= 0 then return 0; end if;
  if p_par in ('application', 'page') then
    -- Le plafond du jour, par application (hors hauts faits et attributions).
    select coalesce(sum(j.xp), 0) into deja from commun.xp_journal j
     where j.compte_id = p_compte and j.application = p_app and j.par in ('application', 'page')
       and j.cree_le >= date_trunc('day', now(), 'Indian/Mayotte');
    v := least(v, greatest(0, (select a.plafond_xp_jour from commun.applications a where a.id = p_app) - deja));
    if v <= 0 then return 0; end if;
  end if;
  insert into commun.xp_journal (compte_id, application, evenement, cle, xp, motif, enseignant_id, par)
  values (p_compte, p_app, p_evenement, p_cle, v, p_motif, p_enseignant, p_par)
  on conflict (compte_id, application, cle) where cle is not null do nothing;
  if not found then return 0; end if;
  update commun.comptes c set xp = c.xp + v, credits = c.credits + v, vu_le = now() where c.id = p_compte;
  return v;
end $$;

-- Un événement d'une application : l'XP de son barème, une fois par clé.
create function commun.gagner_xp(p_compte uuid, p_app text, p_evenement text, p_cle text, p_par text)
returns integer language plpgsql volatile set search_path = '' as $$
declare b commun.baremes;
begin
  select x.* into b from commun.baremes x join commun.applications a on a.id = x.application and a.active
   where x.application = p_app and x.evenement = p_evenement;
  if b.application is null then return 0; end if;
  if b.activite_connue and not exists (select 1 from commun.activites t where t.application = p_app and t.cle = p_cle
                                         and t.evenement = p_evenement and t.actif) then
    return 0;
  end if;
  return commun.crediter(p_compte, p_app, p_evenement, p_cle, b.xp, p_par);
end $$;

-- Accorde des hauts faits à un compte, débloque leurs récompenses et
-- rapporte leur XP. p_par : application, reprise, page ou enseignant.
-- Seuls les hauts faits actifs, de l'application donnée et du bon genre
-- d'accord, sont accordés ; les autres identifiants sont ignorés. Renvoie
-- les nouveautés : {"hauts_faits": [...], "elements": [...], "credits": n}.
create function commun.accorder(p_compte uuid, p_app text, p_ids text[], p_par text)
returns jsonb language plpgsql volatile set search_path = '' as $$
declare r jsonb; h record; gain integer := 0; nouveaux text[];
begin
  if p_compte is null or p_ids is null or cardinality(p_ids) = 0 then
    return jsonb_build_object('hauts_faits', '[]'::jsonb, 'elements', '[]'::jsonb, 'credits', 0);
  end if;
  with n as (
    insert into commun.hauts_faits_gagnes (compte_id, application, haut_fait, par)
    select p_compte, x.application, x.id, p_par
      from commun.hauts_faits x
      join commun.applications a on a.id = x.application and a.active
     where x.application = p_app and x.id = any(p_ids[1:100]) and x.actif
       and x.accord = case p_par when 'enseignant' then 'enseignant' when 'page' then 'page' else 'serveur' end
    on conflict do nothing
    returning haut_fait
  )
  select coalesce(array_agg(n.haut_fait), '{}'::text[]) into nouveaux from n;
  if cardinality(nouveaux) = 0 then
    return jsonb_build_object('hauts_faits', '[]'::jsonb, 'elements', '[]'::jsonb, 'credits', 0);
  end if;
  insert into commun.elements_debloques (compte_id, element_id, origine)
  select distinct p_compte, r.element_id, 'haut_fait'
    from commun.recompenses r where r.application = p_app and r.haut_fait = any(nouveaux)
  on conflict do nothing;
  for h in select x.id, x.xp from commun.hauts_faits x where x.application = p_app and x.id = any(nouveaux) loop
    gain := gain + commun.crediter(p_compte, p_app, 'haut_fait', 'hf:' || h.id, h.xp, 'haut_fait');
  end loop;
  select jsonb_build_object(
    'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', x.application, 'id', x.id, 'nom', x.nom))
                               from commun.hauts_faits x where x.application = p_app and x.id = any(nouveaux)), '[]'::jsonb),
    'elements', coalesce((select jsonb_agg(distinct jsonb_build_object('id', e.id, 'nom', e.nom))
                            from commun.recompenses r join commun.elements e on e.id = r.element_id
                           where r.application = p_app and r.haut_fait = any(nouveaux)), '[]'::jsonb),
    'credits', gain)
  into r;
  update commun.comptes c set vu_le = now() where c.id = p_compte;
  return r;
end $$;

-- Les hauts faits que la progression déjà enregistrée dans une application
-- permet d'accorder (son connecteur fn_hauts_faits), ou une liste vide.
create function commun.reprise_ids(p_app text, p_eleve uuid)
returns text[] language plpgsql volatile set search_path = '' as $$
declare f regprocedure; v text[];
begin
  select a.fn_hauts_faits into f from commun.applications a where a.id = p_app and a.active;
  if f is null then return '{}'::text[]; end if;
  begin
    execute format('select %s($1)', f::oid::regproc) into v using p_eleve;
  exception when others then
    raise warning 'commun.reprise_ids : le connecteur de % a échoué (%)', p_app, sqlerrm;
  end;
  return coalesce(v, '{}'::text[]);
end $$;

-- Le compte commun relié au compte d'une application rattachée. S'il
-- n'existe pas, il est créé (pseudo du compte de l'application, provisoire si
-- l'application le demande) et relié ; avec p_reprise, la progression déjà
-- enregistrée est reprise aussitôt. Null si l'application n'a pas ce compte.
create function commun.compte_par_eleve_app(p_app text, p_eleve uuid, p_reprise boolean default true)
returns uuid language plpgsql volatile set search_path = '' as $$
declare a commun.applications; v uuid; v_pseudo text;
begin
  select l.compte_id into v from commun.liens l where l.application = p_app and l.eleve_app_id = p_eleve;
  if v is not null then return v; end if;
  select * into a from commun.applications x where x.id = p_app and x.active and x.mode = 'rattachee';
  if a.id is null or a.fn_par_id is null then return null; end if;
  execute format('select t.pseudo from %s($1) t limit 1', a.fn_par_id::oid::regproc) into v_pseudo using p_eleve;
  if v_pseudo is null then return null; end if;
  v := commun.creer_compte(coalesce(commun.nettoyer_pseudo(v_pseudo), 'Élève'), p_app, a.pseudo_a_confirmer);
  insert into commun.liens (application, eleve_app_id, compte_id) values (p_app, p_eleve, v);
  if p_reprise then
    perform commun.accorder(v, p_app, commun.reprise_ids(p_app, p_eleve), 'reprise');
  end if;
  return v;
end $$;

-- Le compte commun qu'ouvre un code, quelle que soit l'application qui l'a
-- donné : d'abord les codes du compte commun, puis les connecteurs des
-- applications rattachées. Null pour un code inconnu.
create function commun.compte_par_code(p_code text)
returns uuid language plpgsql volatile set search_path = '' as $$
declare c text := commun.normaliser_code(p_code); a record; v_eleve uuid; v uuid;
begin
  if c !~ '^[A-Z]{8,32}[0-9]{3,4}$' then return null; end if;
  select x.compte_id into v from commun.codes x where x.code = c;
  if v is not null then return v; end if;
  for a in select x.id, x.fn_par_code from commun.applications x
            where x.active and x.mode = 'rattachee' and x.fn_par_code is not null order by x.id loop
    -- Un connecteur en panne ne bloque pas les autres applications : il est
    -- sauté, et l'erreur part dans le journal de la base (avertissement).
    begin
      execute format('select t.eleve_id from %s($1) t limit 1', a.fn_par_code::oid::regproc) into v_eleve using c;
    exception when others then
      raise warning 'commun.compte_par_code : le connecteur de % a échoué (%)', a.id, sqlerrm;
      v_eleve := null;
    end;
    if v_eleve is not null then
      return commun.compte_par_eleve_app(a.id, v_eleve);
    end if;
  end loop;
  return null;
end $$;

-- L'application rattachée signale une visite de son élève : le compte
-- commun relié, s'il existe, reste vivant (ménage des 12 mois).
create function commun.visite_app(p_app text, p_eleve uuid)
returns void language sql volatile set search_path = '' as $$
  update commun.comptes c set vu_le = now()
    from commun.liens l
   where l.application = p_app and l.eleve_app_id = p_eleve and c.id = l.compte_id
     and c.vu_le < now() - interval '10 minutes'
$$;

-- L'application rattachée accorde des hauts faits à son élève (et, au
-- premier lien, ceux de sa progression déjà enregistrée), et lui fait gagner
-- l'XP de ses événements (p_evenements : [{"evenement": …, "cle": …}]).
-- Renvoie les nouveautés, pour que sa page les annonce.
create function commun.accorder_app(p_app text, p_eleve uuid, p_ids text[], p_evenements jsonb default null)
returns jsonb language plpgsql volatile set search_path = '' as $$
declare v uuid := commun.compte_par_eleve_app(p_app, p_eleve, false); r jsonb; e jsonb; gain integer := 0;
begin
  if v is null then return null; end if;
  r := commun.accorder(v, p_app, coalesce(p_ids, '{}'::text[]) || commun.reprise_ids(p_app, p_eleve), 'application');
  if jsonb_typeof(p_evenements) = 'array' then
    for e in select * from jsonb_array_elements(p_evenements) limit 50 loop
      gain := gain + commun.gagner_xp(v, p_app, left(e ->> 'evenement', 30), left(e ->> 'cle', 80), 'application');
    end loop;
  end if;
  return jsonb_set(r, '{credits}', to_jsonb((r ->> 'credits')::integer + gain));
end $$;

-- Vérifie un avatar pour un compte. Renvoie l'avatar propre, ou null.
create function commun.verifier_avatar(p_compte uuid, p_avatar jsonb)
returns jsonb language plpgsql stable set search_path = '' as $$
declare k text; v jsonb; porte jsonb := '{}'::jsonb; teintes jsonb := '{}'::jsonb; lig text;
begin
  if p_avatar is null or jsonb_typeof(p_avatar) <> 'object' or octet_length(p_avatar::text) > 4000
     or (p_avatar ->> 'v') is distinct from '1'
     or exists (select 1 from jsonb_object_keys(p_avatar) x where x not in ('v', 'porte', 'teintes')) then
    return null;
  end if;
  if p_avatar ? 'porte' then
    if jsonb_typeof(p_avatar -> 'porte') <> 'object' then return null; end if;
    lig := p_avatar -> 'porte' ->> 'lignee';
    for k, v in select * from jsonb_each(p_avatar -> 'porte') loop
      if jsonb_typeof(v) <> 'string' then return null; end if;
      if not exists (select 1 from commun.elements e
                      where e.id = v #>> '{}' and e.emplacement = k
                        and (e.lignees is null or lig = any(e.lignees))
                        and ((e.acces = 'libre' and e.actif)
                             or exists (select 1 from commun.elements_debloques d where d.compte_id = p_compte and d.element_id = e.id))) then
        return null;
      end if;
      porte := porte || jsonb_build_object(k, v);
    end loop;
  end if;
  if p_avatar ? 'teintes' then
    if jsonb_typeof(p_avatar -> 'teintes') <> 'object' then return null; end if;
    for k, v in select * from jsonb_each(p_avatar -> 'teintes') loop
      if jsonb_typeof(v) <> 'string' or (v #>> '{}') !~ '^[a-z0-9-]{1,24}$'
         or not exists (select 1 from commun.emplacements m where m.id = k) then
        return null;
      end if;
      teintes := teintes || jsonb_build_object(k, v);
    end loop;
  end if;
  return jsonb_build_object('v', 1, 'porte', porte, 'teintes', teintes);
end $$;

-- La fiche d'un compte, pour l'élève lui-même ou elle-même : pseudo, avatar,
-- ses codes, ses applications, ses hauts faits, ses éléments, son solde de
-- crédits et son journal (les 100 dernières lignes). Jamais le total d'XP.
create function commun.fiche(p_compte uuid)
returns jsonb language plpgsql stable set search_path = '' as $$
declare c commun.comptes; codes jsonb := '[]'::jsonb; l record; v_code text;
begin
  select * into c from commun.comptes x where x.id = p_compte;
  if c.id is null then return null; end if;
  select coalesce(jsonb_agg(jsonb_build_object('application', x.application, 'code_affiche', x.code_affiche, 'principal', x.principal)
                            order by x.principal desc, x.cree_le), '[]'::jsonb)
    into codes from commun.codes x where x.compte_id = p_compte;
  for l in select li.application, li.eleve_app_id, a.fn_par_id
             from commun.liens li join commun.applications a on a.id = li.application
            where li.compte_id = p_compte and a.fn_par_id is not null order by li.depuis loop
    v_code := null;
    begin
      execute format('select t.code_affiche from %s($1) t limit 1', l.fn_par_id::oid::regproc) into v_code using l.eleve_app_id;
    exception when others then
      raise warning 'commun.fiche : le connecteur de % a échoué (%)', l.application, sqlerrm;
    end;
    if v_code is not null then
      codes := codes || jsonb_build_array(jsonb_build_object('application', l.application, 'code_affiche', v_code, 'principal', false));
    end if;
  end loop;
  return jsonb_build_object(
    'pseudo', c.pseudo,
    'pseudo_provisoire', c.pseudo_provisoire,
    'avatar', c.avatar,
    'credits', c.credits,
    'codes', codes,
    'applications', coalesce((select jsonb_agg(distinct li.application) from commun.liens li where li.compte_id = p_compte), '[]'::jsonb),
    'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait, 'gagne_le', g.gagne_le)
                                              order by g.gagne_le) from commun.hauts_faits_gagnes g where g.compte_id = p_compte), '[]'::jsonb),
    'elements', coalesce((select jsonb_agg(d.element_id order by d.depuis) from commun.elements_debloques d where d.compte_id = p_compte), '[]'::jsonb),
    'journal', coalesce((select jsonb_agg(jsonb_build_object('le', j.cree_le, 'application', j.application, 'evenement', j.evenement,
                                                            'nom', coalesce(t.nom, b.nom), 'credits', j.xp, 'motif', j.motif) order by j.cree_le desc)
                           from (select * from commun.xp_journal x where x.compte_id = p_compte order by x.cree_le desc limit 100) j
                           left join commun.baremes b on b.application = j.application and b.evenement = j.evenement
                           left join commun.activites t on t.application = j.application and t.cle = j.cle), '[]'::jsonb),
    'cree_le', c.cree_le);
end $$;

-- Fusionne deux comptes : p_absorber rejoint p_garder. Rien n'est perdu : les
-- liens, les codes (qui restent valables), les hauts faits, les éléments et le
-- journal passent sur le compte gardé ; une activité comptée deux fois ne
-- l'est plus qu'une ; l'XP et les crédits sont recalculés depuis le journal.
create function commun.fusionner(p_garder uuid, p_absorber uuid)
returns void language plpgsql volatile set search_path = '' as $$
declare a record;
begin
  if p_garder is null or p_absorber is null or p_garder = p_absorber then return; end if;
  for a in select x.fn_fusion from commun.applications x where x.mode = 'native' and x.fn_fusion is not null loop
    execute format('select %s($1, $2)', a.fn_fusion::oid::regproc) using p_garder, p_absorber;
  end loop;
  update commun.liens set compte_id = p_garder where compte_id = p_absorber;
  update commun.codes set compte_id = p_garder, principal = false where compte_id = p_absorber;
  insert into commun.hauts_faits_gagnes (compte_id, application, haut_fait, gagne_le, par)
  select p_garder, g.application, g.haut_fait, g.gagne_le, g.par from commun.hauts_faits_gagnes g where g.compte_id = p_absorber
  on conflict (compte_id, application, haut_fait) do update set gagne_le = least(commun.hauts_faits_gagnes.gagne_le, excluded.gagne_le);
  insert into commun.elements_debloques (compte_id, element_id, origine, depuis)
  select p_garder, d.element_id, d.origine, d.depuis from commun.elements_debloques d where d.compte_id = p_absorber
  on conflict (compte_id, element_id) do update set depuis = least(commun.elements_debloques.depuis, excluded.depuis);
  update commun.xp_journal j set compte_id = p_garder
   where j.compte_id = p_absorber
     and (j.cle is null or not exists (select 1 from commun.xp_journal k where k.compte_id = p_garder
                                         and k.application = j.application and k.cle = j.cle));
  delete from commun.comptes where id = p_absorber;
  update commun.comptes c set
    xp = coalesce((select sum(j.xp) from commun.xp_journal j where j.compte_id = p_garder and j.xp > 0), 0),
    credits = greatest(0, coalesce((select sum(j.xp) from commun.xp_journal j where j.compte_id = p_garder), 0)),
    vu_le = now()
  where c.id = p_garder;
end $$;

-- Le ménage, au plus une fois par heure : les sessions expirées, et les
-- comptes sans visite depuis 12 mois (avec tout ce qui leur appartient).
create function commun.menage_si_besoin()
returns void language plpgsql volatile set search_path = '' as $$
begin
  update commun.menage set fait_le = now() where fait_le < now() - interval '1 hour';
  if not found then return; end if;
  delete from commun.sessions s
   where (s.garde_jours = 1 and s.cree_le < now() - interval '1 day')
      or (s.garde_jours = 30 and s.vu_le < now() - interval '30 days');
  delete from commun.comptes c where c.vu_le < now() - interval '12 months';
end $$;

revoke all on function commun.normaliser_code(text), commun.nettoyer_texte(text, integer, integer), commun.nettoyer_pseudo(text),
  commun.nouveau_code(text), commun.ouvrir_session(uuid, integer), commun.compte_par_jeton(uuid),
  commun.creer_compte(text, text, boolean), commun.crediter(uuid, text, text, text, integer, text, text, uuid),
  commun.gagner_xp(uuid, text, text, text, text), commun.accorder(uuid, text, text[], text), commun.reprise_ids(text, uuid),
  commun.compte_par_eleve_app(text, uuid, boolean), commun.compte_par_code(text), commun.visite_app(text, uuid),
  commun.accorder_app(text, uuid, text[], jsonb), commun.verifier_avatar(uuid, jsonb), commun.fiche(uuid),
  commun.fusionner(uuid, uuid), commun.menage_si_besoin()
  from public, anon, authenticated;

comment on function commun.normaliser_code(text) is 'Commun, interne. La forme canonique d''un code : majuscules, accents et séparateurs retirés (spécification des codes, § 1.2).';
comment on function commun.nettoyer_texte(text, integer, integer) is 'Commun, interne. Un texte de p_min à p_max caractères, espaces réduits, sans caractère de contrôle ni invisible ; sinon null.';
comment on function commun.nettoyer_pseudo(text) is 'Commun, interne. Un prénom ou un pseudo de 2 à 24 caractères (commun.nettoyer_texte) ; sinon null.';
comment on function commun.nouveau_code(text) is 'Commun, interne. Un code neuf de 2 mots et 3 chiffres, tiré sans biais dans la liste de mots d''une application, libre dans commun.codes.';
comment on function commun.ouvrir_session(uuid, integer) is 'Commun, interne. Un nouveau jeton de session (1 ou 30 jours) ; 5 jetons au plus par compte, le plus ancien part.';
comment on function commun.compte_par_jeton(uuid) is 'Commun, interne. Le compte d''un jeton encore valable, sinon null ; note l''usage du jeton et la visite.';
comment on function commun.creer_compte(text, text, boolean) is 'Commun, interne. Crée un compte commun avec un pseudo déjà nettoyé, son application d''origine, et un pseudo provisoire ou non.';
comment on function commun.crediter(uuid, text, text, text, integer, text, text, uuid) is 'Commun, interne. Écrit un gain au journal de l''XP (une fois par clé, dans le plafond du jour pour les événements) et augmente l''XP et les crédits ; renvoie l''XP gagnée.';
comment on function commun.gagner_xp(uuid, text, text, text, text) is 'Commun, interne. L''XP d''un événement d''après le barème, une fois par clé ; une page ne peut déclarer qu''une activité inscrite.';
comment on function commun.accorder(uuid, text, text[], text) is 'Commun, interne. Accorde des hauts faits (selon leur genre d''accord), débloque leurs récompenses, rapporte leur XP, et renvoie les nouveautés.';
comment on function commun.reprise_ids(text, uuid) is 'Commun, interne. Les hauts faits que la progression déjà enregistrée dans une application permet d''accorder (connecteur fn_hauts_faits).';
comment on function commun.compte_par_eleve_app(text, uuid, boolean) is 'Commun, interne. Le compte commun relié au compte d''une application rattachée ; le crée et le relie s''il manque, et reprend alors la progression déjà enregistrée (p_reprise).';
comment on function commun.compte_par_code(text) is 'Commun, interne. Le compte commun qu''ouvre un code, né sur le site, dans une application native ou dans une application rattachée (par son connecteur) ; null si inconnu.';
comment on function commun.visite_app(text, uuid) is 'Commun, interne. Appelée par une application rattachée quand son élève entre : le compte commun relié reste vivant.';
comment on function commun.accorder_app(text, uuid, text[], jsonb) is 'Commun, interne. Appelée par une fonction d''une application rattachée, après sa propre vérification : hauts faits, reprise au premier lien, et XP de ses événements.';
comment on function commun.verifier_avatar(uuid, jsonb) is 'Commun, interne. L''avatar propre (format 1) si chaque élément porté est libre ou débloqué pour ce compte, à son emplacement et compatible avec sa lignée ; sinon null.';
comment on function commun.fiche(uuid) is 'Commun, interne. La fiche d''un compte pour l''élève : pseudo, avatar, codes, applications, hauts faits, éléments, solde de crédits et journal ; jamais le total d''XP.';
comment on function commun.fusionner(uuid, uuid) is 'Commun, interne. Réunit deux comptes de la même personne : tout passe sur le compte gardé, les codes restent valables, une activité n''est comptée qu''une fois.';
comment on function commun.menage_si_besoin() is 'Commun, interne. Au plus une fois par heure : efface les sessions expirées et les comptes sans visite depuis 12 mois.';

-- -----------------------------------------------------------------------------
-- 8. Les fonctions d'entrée, appelées par la page élève du site et par les
--    pages des applications : anon seul. Un échec répond { ok: false,
--    message }, jamais par une exception.
-- -----------------------------------------------------------------------------

-- Créer son code sur le site.
create function public.commun_creer(p_pseudo text, p_garde_jours integer default 1)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v_pseudo text := commun.nettoyer_pseudo(p_pseudo); v uuid; n record; j uuid;
begin
  if not commun.essai_permis('commun', 'creation', 60) then
    return jsonb_build_object('ok', false, 'message', 'Trop de comptes créés depuis ce réseau en une heure. Attends un peu.');
  end if;
  if v_pseudo is null then
    return jsonb_build_object('ok', false, 'message', 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).');
  end if;
  perform commun.menage_si_besoin();
  perform commun.noter_echec('commun', 'creation');
  v := commun.creer_compte(v_pseudo, 'commun');
  select * into n from commun.nouveau_code('commun');
  insert into commun.codes (code, code_affiche, compte_id, application) values (n.code, n.code_affiche, v, 'commun');
  j := commun.ouvrir_session(v, p_garde_jours);
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche, 'jeton', j, 'fiche', commun.fiche(v));
end $$;

-- Entrer avec n'importe lequel de ses codes.
create function public.commun_entrer(p_code text, p_garde_jours integer default 1)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid;
begin
  if not commun.essai_permis('commun', 'eleve', 20) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu, ou demande ton code à ton enseignant·e.');
  end if;
  v := commun.compte_par_code(left(coalesce(p_code, ''), 80));
  if v is null then
    perform commun.noter_echec('commun', 'eleve');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Ce code n''existe pas. Vérifie-le dans ton cahier.');
  end if;
  perform commun.menage_si_besoin();
  return jsonb_build_object('ok', true, 'jeton', commun.ouvrir_session(v, p_garde_jours), 'fiche', commun.fiche(v));
end $$;

-- Reprendre avec son jeton.
create function public.commun_reprise(p_jeton uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton);
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  perform commun.menage_si_besoin();
  return jsonb_build_object('ok', true, 'fiche', commun.fiche(v));
end $$;

-- Le catalogue public : applications, emplacements, éléments (et leurs
-- prix), hauts faits, récompenses et barème. Aucune donnée d'élève.
create function public.commun_catalogue()
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object(
    'version', 1,
    'applications', coalesce((select jsonb_agg(jsonb_build_object('id', a.id, 'nom', a.nom, 'adresse', a.adresse) order by a.id)
                                from commun.applications a where a.active), '[]'::jsonb),
    'emplacements', (select jsonb_agg(jsonb_build_object('id', m.id, 'nom', m.nom, 'genre', m.genre, 'plan', m.plan, 'obligatoire', m.obligatoire)
                                      order by m.plan nulls first, m.id) from commun.emplacements m),
    'elements', coalesce((select jsonb_agg(jsonb_build_object('id', e.id, 'emplacement', e.emplacement, 'nom', e.nom,
                                   'description', e.description, 'acces', e.acces, 'prix', e.prix, 'lignees', e.lignees,
                                   'teintable', e.teintable, 'actif', e.actif)
                                   order by e.emplacement, e.ordre, e.id) from commun.elements e), '[]'::jsonb),
    'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', h.application, 'id', h.id,
                                   'nom', case when h.secret then null else h.nom end,
                                   'description', case when h.secret then null else h.description end,
                                   'indice', h.indice, 'categorie', h.categorie, 'secret', h.secret, 'actif', h.actif,
                                   'recompenses', coalesce((select jsonb_agg(r.element_id order by r.element_id) from commun.recompenses r
                                                             where r.application = h.application and r.haut_fait = h.id and not h.secret), '[]'::jsonb))
                                   order by h.application, h.ordre, h.id) from commun.hauts_faits h), '[]'::jsonb),
    'bareme', coalesce((select jsonb_agg(jsonb_build_object('application', b.application, 'evenement', b.evenement, 'nom', b.nom, 'credits', b.xp)
                               order by b.application, b.evenement) from commun.baremes b), '[]'::jsonb))
$$;

-- Porter un avatar.
create function public.commun_porter(p_jeton uuid, p_avatar jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); a jsonb;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if p_avatar is null or octet_length(p_avatar::text) > 4000 then
    return jsonb_build_object('ok', false, 'message', 'Cet avatar est trop lourd.');
  end if;
  a := commun.verifier_avatar(v, p_avatar);
  if a is null then
    return jsonb_build_object('ok', false, 'message', 'Un élément n''est pas encore débloqué, ne va pas avec cette lignée, ou n''est pas à sa place : l''avatar n''a pas changé.');
  end if;
  update commun.comptes c set avatar = a where c.id = v;
  return jsonb_build_object('ok', true, 'avatar', a);
end $$;

-- Acheter une apparence avec ses crédits. Un achat ne se rembourse pas, et
-- ce qui est acheté ne se perd jamais.
create function public.commun_acheter(p_jeton uuid, p_element text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); e commun.elements; reste integer;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  select * into e from commun.elements x where x.id = left(p_element, 62) and x.acces = 'credits' and x.actif;
  if e.id is null then
    return jsonb_build_object('ok', false, 'message', 'Cet élément ne s''achète pas.');
  end if;
  if exists (select 1 from commun.elements_debloques d where d.compte_id = v and d.element_id = e.id) then
    return jsonb_build_object('ok', false, 'message', 'Tu l''as déjà.');
  end if;
  update commun.comptes c set credits = c.credits - e.prix where c.id = v and c.credits >= e.prix returning c.credits into reste;
  if reste is null then
    return jsonb_build_object('ok', false, 'message', 'Pas encore assez de crédits pour celui-ci.');
  end if;
  insert into commun.elements_debloques (compte_id, element_id, origine) values (v, e.id, 'achat');
  insert into commun.xp_journal (compte_id, application, evenement, cle, xp, par)
  values (v, 'commun', 'achat', 'achat:' || e.id, -e.prix, 'achat');
  return jsonb_build_object('ok', true, 'element', e.id, 'credits', reste);
end $$;

-- Changer de prénom ou de pseudo (et confirmer un pseudo provisoire).
create function public.commun_renommer(p_jeton uuid, p_pseudo text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); p text := commun.nettoyer_pseudo(p_pseudo);
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if p is null then
    return jsonb_build_object('ok', false, 'message', 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).');
  end if;
  update commun.comptes c set pseudo = p, pseudo_provisoire = false where c.id = v;
  return jsonb_build_object('ok', true, 'pseudo', p);
end $$;

-- Réunir un autre de ses codes (d'une autre application) à ce compte.
create function public.commun_lier_code(p_jeton uuid, p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); autre uuid;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if not commun.essai_permis('commun', 'eleve', 20) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  autre := commun.compte_par_code(left(coalesce(p_code, ''), 80));
  if autre is null then
    perform commun.noter_echec('commun', 'eleve');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Ce code n''existe pas. Vérifie-le dans ton cahier.');
  end if;
  if autre = v then
    return jsonb_build_object('ok', true, 'message', 'Ce code ouvre déjà ton compte.', 'fiche', commun.fiche(v));
  end if;
  perform commun.fusionner(v, autre);
  return jsonb_build_object('ok', true, 'message', 'Tes deux codes ouvrent maintenant le même compte, avec tout ce que tu as gagné.', 'fiche', commun.fiche(v));
end $$;

-- Une page sans serveur (feuille de TD, QuizzNSI, calendrier) déclare une
-- activité faite : l'XP de son barème, une fois par activité inscrite.
create function public.commun_evenement_page(p_jeton uuid, p_application text, p_evenement text, p_cle text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); a text := left(p_application, 30); g integer;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Entre ton code pour garder tes crédits.');
  end if;
  if not exists (select 1 from commun.applications x where x.id = a and x.active and x.accord_par_page) then
    return jsonb_build_object('ok', false, 'message', 'Cette page ne donne pas de crédits.');
  end if;
  g := commun.gagner_xp(v, a, left(p_evenement, 30), left(p_cle, 80), 'page');
  return jsonb_build_object('ok', true, 'credits_gagnes', g,
    'message', case when g > 0 then 'Bien joué : c''est gardé.' else 'C''est déjà gardé (une activité ne compte qu''une fois).' end);
end $$;

-- Une page sans serveur accorde l'un de ses hauts faits de genre « page ».
create function public.commun_haut_fait_page(p_jeton uuid, p_application text, p_haut_fait text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton);
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if not exists (select 1 from commun.applications a where a.id = left(p_application, 30) and a.active and a.accord_par_page) then
    return jsonb_build_object('ok', false, 'message', 'Cette application n''accorde pas de haut fait depuis sa page.');
  end if;
  return jsonb_build_object('ok', true, 'nouveautes', commun.accorder(v, left(p_application, 30), array[left(p_haut_fait, 40)], 'page'));
end $$;

-- « Ce n'est pas moi » ou « Me déconnecter » : le jeton de cet appareil disparaît.
create function public.commun_quitter(p_jeton uuid)
returns jsonb language sql volatile security definer set search_path = '' as $$
  with d as (delete from commun.sessions s where s.jeton = p_jeton returning 1)
  select jsonb_build_object('ok', true)
$$;

-- Effacer son compte commun (et, si demandé, ses comptes dans les
-- applications qui le permettent). La confirmation est le mot EFFACER.
create function public.commun_effacer_moi(p_jeton uuid, p_confirmation text, p_partout boolean default false)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); l record; restent jsonb := '[]'::jsonb;
begin
  if v is null then
    return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if coalesce(upper(btrim(p_confirmation)), '') <> 'EFFACER' then
    return jsonb_build_object('ok', false, 'message', 'Écris EFFACER pour confirmer.');
  end if;
  for l in select li.application, li.eleve_app_id, a.fn_effacer, a.nom
             from commun.liens li join commun.applications a on a.id = li.application where li.compte_id = v loop
    if p_partout and l.fn_effacer is not null then
      execute format('select %s($1)', l.fn_effacer::oid::regproc) using l.eleve_app_id;
    else
      restent := restent || to_jsonb(l.nom);
    end if;
  end loop;
  delete from commun.comptes c where c.id = v;
  return jsonb_build_object('ok', true, 'restent', restent,
    'message', case when jsonb_array_length(restent) = 0 then 'Ton compte commun est effacé.'
                    else 'Ton compte commun est effacé. Tes comptes de ces applications restent : efface-les depuis chacune.' end);
end $$;

revoke all on function public.commun_creer(text, integer), public.commun_entrer(text, integer), public.commun_reprise(uuid),
  public.commun_catalogue(), public.commun_porter(uuid, jsonb), public.commun_acheter(uuid, text), public.commun_renommer(uuid, text),
  public.commun_lier_code(uuid, text), public.commun_evenement_page(uuid, text, text, text),
  public.commun_haut_fait_page(uuid, text, text), public.commun_quitter(uuid), public.commun_effacer_moi(uuid, text, boolean)
  from public, anon, authenticated;
grant execute on function public.commun_creer(text, integer), public.commun_entrer(text, integer), public.commun_reprise(uuid),
  public.commun_catalogue(), public.commun_porter(uuid, jsonb), public.commun_acheter(uuid, text), public.commun_renommer(uuid, text),
  public.commun_lier_code(uuid, text), public.commun_evenement_page(uuid, text, text, text),
  public.commun_haut_fait_page(uuid, text, text), public.commun_quitter(uuid), public.commun_effacer_moi(uuid, text, boolean)
  to anon;

comment on function public.commun_creer(text, integer) is 'Compte commun, entrée. Crée un compte avec un prénom ou un pseudo et renvoie son code (2 mots, 3 chiffres), un jeton et la fiche. 60 créations par heure et par réseau.';
comment on function public.commun_entrer(text, integer) is 'Compte commun, entrée. Entre avec n''importe quel code de l''élève (site, Gombessa, Court-circuit, Hello GO…) ; renvoie un jeton et la fiche. 20 échecs par heure et par réseau.';
comment on function public.commun_reprise(uuid) is 'Compte commun, entrée. La fiche de l''élève, avec son jeton.';
comment on function public.commun_catalogue() is 'Compte commun, entrée. Le catalogue public des applications, emplacements, éléments, hauts faits et du barème ; aucune donnée d''élève.';
comment on function public.commun_porter(uuid, jsonb) is 'Compte commun, entrée. Change l''avatar porté, après vérification de chaque élément.';
comment on function public.commun_acheter(uuid, text) is 'Compte commun, entrée. Achète une apparence avec ses crédits ; sans remboursement, et jamais perdue.';
comment on function public.commun_renommer(uuid, text) is 'Compte commun, entrée. Change le prénom ou le pseudo du compte commun (et confirme un pseudo provisoire).';
comment on function public.commun_lier_code(uuid, text) is 'Compte commun, entrée. Réunit au compte un autre code de l''élève : les deux comptes fusionnent, rien n''est perdu.';
comment on function public.commun_evenement_page(uuid, text, text, text) is 'Compte commun, entrée. Une page sans serveur déclare une activité inscrite faite (feuille de TD, cours-quiz, mini-jeu) : les crédits du barème, une fois, dans le plafond du jour.';
comment on function public.commun_haut_fait_page(uuid, text, text) is 'Compte commun, entrée. Une page sans serveur (accord_par_page) accorde l''un de ses hauts faits de genre page.';
comment on function public.commun_quitter(uuid) is 'Compte commun, entrée. Supprime le jeton de cet appareil (« Ce n''est pas moi », « Me déconnecter »).';
comment on function public.commun_effacer_moi(uuid, text, boolean) is 'Compte commun, entrée. Efface le compte commun, ses hauts faits, son avatar et son journal ; avec p_partout, aussi les comptes des applications qui le permettent.';

-- -----------------------------------------------------------------------------
-- 9. Contrôle : rien d'ouvert à l'API. Sinon, arrêt : rien n'est appliqué.
-- -----------------------------------------------------------------------------
do $$
begin
  if has_schema_privilege('anon', 'commun', 'usage') or has_schema_privilege('authenticated', 'commun', 'usage') then
    raise exception 'Le schéma commun est ouvert à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction de commun est appelable par anon ou par authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'v')
             and (has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de commun est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r' and not c.relrowsecurity) then
    raise exception 'Une table de commun n''a pas la RLS : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%'
             and (has_function_privilege('authenticated', p.oid, 'execute') or not has_function_privilege('anon', p.oid, 'execute')
                  or not p.prosecdef or p.proconfig is null)) then
    raise exception 'Une fonction commun_ n''a pas les bons droits ou son search_path : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from commun.mots where application = 'commun') <> 64 then
    raise exception 'La liste des mots du site doit avoir 64 mots : arrêt, rien n''a été modifié.';
  end if;
end $$;

commit;
