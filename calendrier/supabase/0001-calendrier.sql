begin;
-- =============================================================================
--  Calendrier des vacances, migration 0001 : comptes, calendriers, résultats
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : vacances_0001_calendrier
--  T105, version de Noël 2026 (20/11/2026). L'enseignant a vu le fichier et
--  délégué (20/11, 14:55) ; relecture du Gardien avant application par le
--  chef d'orchestre (apply_migration, sans les lignes begin et commit).
--  Fichier : calendrier/supabase/0001-calendrier.sql du dépôt du site.
-- =============================================================================
--  Pourquoi : pendant les vacances, chaque élève ouvre une case par jour :
--  un mini-jeu de 10 minutes au plus, sur un des thèmes choisis par son
--  enseignant·e (demande de l'enseignant du 19/11). La règle 21 s'applique :
--  un code en mots et chiffres, qui suffit pour revenir ; un prénom ou un
--  pseudo, jamais le nom de famille ; aucun plafond du nombre d'élèves.
--
--  Ce que ce fichier crée, et rien d'autre :
--   - le schéma vacances, que l'API n'expose pas, sans aucun droit pour anon
--     ni pour authenticated ;
--   - neuf tables, toutes avec la RLS, sans règle et sans droit :
--       vacances.mots          les 64 mots des codes (thème : les jeux et les loisirs) ;
--       vacances.enseignants   un espace par enseignant·e (empreinte du code) ;
--       vacances.calendriers   les calendriers : dates, thèmes, réglages, code du lien ;
--       vacances.cases         les cases de chaque calendrier : jour, thème, rang de l'exercice ;
--       vacances.eleves        un compte par élève : prénom ou pseudo, code ;
--       vacances.sessions      les jetons de session (5 appareils au plus) ;
--       vacances.inscriptions  qui est dans quel calendrier ;
--       vacances.resultats     un résultat par élève, case et niveau (jamais les réponses) ;
--  Aucun classement, aucun rang, aucune « série » : le score compte les étoiles,
--  les cases faites et les jours différents où l'élève a joué.
--       vacances.menage        la date du dernier ménage (une ligne) ;
--   - des fonctions internes, appelables par aucun rôle de l'API ;
--   - 22 fonctions d'entrée dans public (préfixe cv_), appelables par anon seulement :
--       10 pour les élèves, 12 pour les enseignant·e·s (liste dans LISEZMOI.md).
--  Il se sert du compteur d'essais du schéma commun (commun.essai_permis,
--  commun.noter_echec, commun.debloquer_reseau), sans le modifier.
--
--  Les données d'élèves : un prénom ou un pseudo (2 à 24 caractères, jamais le
--  nom de famille), le code, les jetons de session, et pour chaque case jouée :
--  le niveau, la réussite, les étoiles, le nombre d'essais et de coups de pouce,
--  la durée et la date. Jamais les réponses tapées.
--  Conservation (le ménage passe au premier usage de l'application après
--  l'échéance) : un compte, 12 mois après la dernière visite ; un calendrier,
--  avec ses résultats, 12 mois après sa date de fin ; un espace d'enseignant·e,
--  24 mois après sa dernière ouverture ; une session, 30 jours sans usage. L'élève peut effacer son compte avant
--  (« Effacer mes données »), l'enseignant·e un calendrier ou un·e élève.
--
--  Ce que ce fichier ne change pas : aucun objet existant, aucune autre
--  application, aucun réglage de l'API.
--
--  Le fichier peut être relancé : il ne crée que ce qui manque, et remplace
--  les fonctions par leur version de ce fichier.
--  Le registre des tables (commun.registre) lit ce schéma avec la migration
--  du socle supabase/0009-registre-vacances.sql, avant ou après celle-ci.
--  Retour en arrière : 0001-calendrier-inverse.sql. Mode d'emploi : LISEZMOI.md.
-- =============================================================================

-- Garde-fou : le bon rôle, le schéma commun et pgcrypto présents, et aucun
-- objet du même nom venu d'ailleurs. Sinon, arrêt avant toute modification.
do $$
declare o text;
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres (éditeur SQL de Supabase ou apply_migration), pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regprocedure('commun.essai_permis(text, text, integer)') is null
     or to_regprocedure('commun.noter_echec(text, text)') is null
     or to_regprocedure('commun.debloquer_reseau(text)') is null then
    raise exception 'Le schéma commun manque (migration base_unique_0003_schema_commun) : arrêt, rien n''a été modifié.';
  end if;
  if to_regprocedure('extensions.gen_random_bytes(integer)') is null or to_regprocedure('extensions.digest(text, text)') is null then
    raise exception 'L''extension pgcrypto manque dans le schéma extensions : arrêt, rien n''a été modifié.';
  end if;
  if to_regnamespace('vacances') is not null
     and coalesce(obj_description(to_regnamespace('vacances'), 'pg_namespace'), '') not like 'Calendrier des vacances%' then
    raise exception 'Un schéma vacances existe déjà et ne vient pas de cette migration : arrêt, rien n''a été modifié.';
  end if;
  foreach o in array array['vacances.mots', 'vacances.enseignants', 'vacances.calendriers', 'vacances.cases',
                           'vacances.eleves', 'vacances.sessions', 'vacances.inscriptions', 'vacances.resultats',
                           'vacances.menage'] loop
    if to_regclass(o) is not null and coalesce(obj_description(to_regclass(o), 'pg_class'), '') not like 'Calendrier des vacances.%' then
      raise exception '% existe déjà et ne vient pas de cette migration : arrêt, rien n''a été modifié.', o;
    end if;
  end loop;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'cv\_%'
             and coalesce(obj_description(p.oid, 'pg_proc'), '') not like 'Calendrier des vacances%') then
    raise exception 'Une fonction public.cv_… existe déjà et ne vient pas de cette migration : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- 1. Le schéma
-- -----------------------------------------------------------------------------
create schema if not exists vacances authorization postgres;
revoke all on schema vacances from public, anon, authenticated;
comment on schema vacances is
  'Calendrier des vacances : un mini-jeu par jour pendant les vacances, réglé par l''enseignant·e. Jamais exposé à l''API ; aucun droit pour anon ni pour authenticated.';

-- -----------------------------------------------------------------------------
-- 2. Les tables
-- -----------------------------------------------------------------------------
create table if not exists vacances.mots (
  rang smallint primary key check (rang between 0 and 63),
  mot  text not null unique check (mot ~ '^[A-Z]{4,8}$')
);
alter table vacances.mots enable row level security;
revoke all on vacances.mots from public, anon, authenticated;
comment on table vacances.mots is
  'Calendrier des vacances. Les 64 mots des codes des élèves et des enseignant·e·s (thème : les jeux et les loisirs). Aucun n''est dans la liste d''une autre application (compte commun T101 compris), ni le début d''un autre mot. Données d''élèves : non.';
comment on column vacances.mots.rang is 'La place du mot dans la liste, de 0 à 63 : le tirage d''un octet modulo 64 donne le rang.';
comment on column vacances.mots.mot is 'Le mot, en majuscules sans accent, de 4 à 8 lettres.';
insert into vacances.mots (rang, mot)
select (o - 1)::smallint, m from unnest(array[
  'DOMINO', 'PUZZLE', 'DAMIER', 'TOUPIE', 'MARELLE', 'YOYO', 'ECHECS', 'CARTE',
  'JOKER', 'ATOUT', 'QUILLE', 'BALLON', 'RAQUETTE', 'FILET', 'FRISBEE', 'CERCEAU',
  'SCORE', 'BONUS', 'COMBO', 'QUETE', 'TRESOR', 'ENIGME', 'REBUS', 'CHARADE',
  'SUDOKU', 'MEMORY', 'BINGO', 'KARTING', 'MIKADO', 'TANGRAM', 'CARROM', 'TOBOGGAN',
  'HAMAC', 'PARASOL', 'SORBET', 'DIABOLO', 'DEDALE', 'PION', 'ARCADE', 'AVATAR',
  'FINALE', 'MATCH', 'SPRINT', 'ORIGAMI', 'CUBE', 'TOTEM', 'DEFI', 'JONGLAGE',
  'BOWLING', 'TENNIS', 'JUDO', 'FANION', 'PLONGEON', 'SURF', 'RUGBY', 'BASKET',
  'FLIPPER', 'BILLARD', 'SLALOM', 'GOLF', 'TAQUIN', 'RALLYE', 'HOCKEY', 'SQUASH'
]) with ordinality as l(m, o)
on conflict (rang) do nothing;

create table if not exists vacances.enseignants (
  id             uuid primary key default gen_random_uuid(),
  nom            text not null check (char_length(nom) between 2 and 40),
  code_empreinte text not null unique check (code_empreinte ~ '^[0-9a-f]{64}$'),
  cree_le        timestamptz not null default now(),
  vu_le          timestamptz not null default now()
);
alter table vacances.enseignants enable row level security;
revoke all on vacances.enseignants from public, anon, authenticated;
comment on table vacances.enseignants is
  'Calendrier des vacances. Un espace par enseignant·e : le nom affiché aux élèves et l''empreinte SHA-256 de son code (3 mots et 4 chiffres, montré une seule fois, gardé nulle part en clair). Effacé, avec ses calendriers, au premier usage de l''application après 24 mois sans ouverture. Données d''élèves : non.';
comment on column vacances.enseignants.id is 'L''identifiant de l''espace ; il ne change jamais (il deviendra celui de commun.enseignants, T101).';
comment on column vacances.enseignants.nom is 'Le nom affiché aux élèves (« Mme N. », « M. K. »), de 2 à 40 caractères.';
comment on column vacances.enseignants.code_empreinte is 'L''empreinte SHA-256 de la forme canonique du code : personne ne peut relire le code.';
comment on column vacances.enseignants.cree_le is 'La date de création de l''espace.';
comment on column vacances.enseignants.vu_le is 'La date de la dernière ouverture de l''espace : il est effacé 24 mois après.';

create table if not exists vacances.calendriers (
  id                    uuid primary key default gen_random_uuid(),
  enseignant_id         uuid not null references vacances.enseignants (id) on delete cascade,
  nom                   text not null check (char_length(nom) between 2 and 60),
  code                  text not null unique check (code ~ '^[A-HJ-NP-Z]{4}$'),
  debut                 date not null,
  fin                   date not null,
  themes                text[] not null check (cardinality(themes) between 1 and 20),
  mode                  text not null default 'alternance' check (mode in ('alternance', 'chaque_theme')),
  ouvertes_max          smallint not null default 3 check (ouvertes_max between 1 and 10),
  delai_correction      smallint not null default 3 check (delai_correction between 0 and 7),
  affichage_classe      text not null default 'jauge' check (affichage_classe in ('jauge', 'aucun')),
  inscriptions_ouvertes boolean not null default true,
  cree_le               timestamptz not null default now(),
  check (fin >= debut and fin - debut <= 29)
);
create index if not exists calendriers_enseignant on vacances.calendriers (enseignant_id);
create index if not exists calendriers_fin on vacances.calendriers (fin);
alter table vacances.calendriers enable row level security;
revoke all on vacances.calendriers from public, anon, authenticated;
comment on table vacances.calendriers is
  'Calendrier des vacances. Les calendriers des enseignant·e·s : nom, dates (30 jours au plus), thèmes, réglages et code public du lien d''inscription. Effacé, avec ses cases et ses résultats, 12 mois après sa date de fin. Données d''élèves : non.';
comment on column vacances.calendriers.id is 'L''identifiant du calendrier.';
comment on column vacances.calendriers.enseignant_id is 'L''espace de l''enseignant·e (vacances.enseignants).';
comment on column vacances.calendriers.nom is 'Le nom montré aux élèves (« 1NSI : vacances de décembre »), de 2 à 60 caractères.';
comment on column vacances.calendriers.code is 'Le code public du lien et du QR code : 4 lettres sans I ni O.';
comment on column vacances.calendriers.debut is 'Le premier jour, à l''heure de Mayotte.';
comment on column vacances.calendriers.fin is 'Le dernier jour, à l''heure de Mayotte : 30 jours au plus, début compris.';
comment on column vacances.calendriers.themes is 'Les identifiants des thèmes (un chapitre ou une notion : boucles, binaire…), dans l''ordre choisi, de 1 à 20 (catalogue calendrier/exercices/catalogue.json). Aucun lien avec le niveau de la classe : une terminale peut recevoir des thèmes de première.';
comment on column vacances.calendriers.mode is 'alternance : une case par jour, les thèmes à tour de rôle (le réglage par défaut) ; chaque_theme : une case par jour et par thème.';
comment on column vacances.calendriers.ouvertes_max is 'Le nombre de cases à faire montrées à la fois (3) : les plus récentes attendent leur tour.';
comment on column vacances.calendriers.delai_correction is 'Le nombre de jours avant que le corrigé d''une case soit visible (3) : il s''ouvre à J + 3.';
comment on column vacances.calendriers.affichage_classe is 'Ce que voient les élèves de leur classe : jauge (des nombres de toute la classe, sans aucun nom) ou aucun.';
comment on column vacances.calendriers.inscriptions_ouvertes is 'Faux : le lien n''inscrit plus de nouvel·le élève (les inscrit·e·s continuent).';
comment on column vacances.calendriers.cree_le is 'La date de création du calendrier.';

create table if not exists vacances.cases (
  calendrier_id uuid not null references vacances.calendriers (id) on delete cascade,
  numero        smallint not null check (numero between 1 and 600),
  jour          date not null,
  theme         text not null check (theme ~ '^[a-z0-9]+(-[a-z0-9]+)*$' and char_length(theme) <= 60),
  rang          smallint not null check (rang between 1 and 99),
  primary key (calendrier_id, numero)
);
create index if not exists cases_jour on vacances.cases (calendrier_id, jour);
alter table vacances.cases enable row level security;
revoke all on vacances.cases from public, anon, authenticated;
comment on table vacances.cases is
  'Calendrier des vacances. Les cases de chaque calendrier : le jour d''ouverture, le thème et le rang de l''exercice dans la banque du thème. Une case qui a des résultats ne peut pas être effacée, sauf avec son calendrier. Données d''élèves : non.';
comment on column vacances.cases.calendrier_id is 'Le calendrier (vacances.calendriers).';
comment on column vacances.cases.numero is 'Le numéro de la case dans le calendrier ; il ne change jamais.';
comment on column vacances.cases.jour is 'Le jour où la case s''ouvre, à 0 h à l''heure de Mayotte.';
comment on column vacances.cases.theme is 'L''identifiant du thème.';
comment on column vacances.cases.rang is 'Le rang de l''exercice dans la banque du thème (1 pour le premier).';

create table if not exists vacances.eleves (
  id             uuid primary key default gen_random_uuid(),
  pseudo         text not null check (char_length(pseudo) between 2 and 24),
  code           text not null unique check (code ~ '^[A-Z]{8,16}[0-9]{3,4}$'),
  code_affiche   text not null check (code_affiche ~ '^[A-Z]{4,8}-[A-Z]{4,8}-[0-9]{3,4}$'),
  compte_commun  uuid,
  cree_le        timestamptz not null default now(),
  vu_le          timestamptz not null default now()
);
create index if not exists eleves_vu_le on vacances.eleves (vu_le);
alter table vacances.eleves enable row level security;
revoke all on vacances.eleves from public, anon, authenticated;
comment on table vacances.eleves is
  'Calendrier des vacances. Un compte par élève : son prénom ou son pseudo et son code (2 mots et 3 chiffres). Effacé 12 mois après la dernière visite. Données d''élèves : oui.';
comment on column vacances.eleves.id is 'L''identifiant du compte, tiré au hasard ; il ne change jamais.';
comment on column vacances.eleves.pseudo is 'Le prénom ou le pseudo choisi par l''élève, de 2 à 24 caractères. Jamais le nom de famille.';
comment on column vacances.eleves.code is 'Le code sous sa forme canonique (DOMINOJOKER482). Secret : seules la fonction de l''élève et celles de ses enseignant·e·s le renvoient.';
comment on column vacances.eleves.code_affiche is 'Le même code tel qu''on l''affiche (DOMINO-JOKER-482).';
comment on column vacances.eleves.compte_commun is 'Vide aujourd''hui : le compte commun à toutes les applications (T101), quand il existera.';
comment on column vacances.eleves.cree_le is 'La date de création du compte.';
comment on column vacances.eleves.vu_le is 'La date de la dernière visite : le compte est effacé 12 mois après.';

create table if not exists vacances.sessions (
  jeton     uuid primary key default gen_random_uuid(),
  eleve_id  uuid not null references vacances.eleves (id) on delete cascade,
  cree_le   timestamptz not null default now(),
  vu_le     timestamptz not null default now()
);
create index if not exists sessions_eleve on vacances.sessions (eleve_id, vu_le desc);
alter table vacances.sessions enable row level security;
revoke all on vacances.sessions from public, anon, authenticated;
comment on table vacances.sessions is
  'Calendrier des vacances. Les jetons de session : un par appareil où l''élève est entré·e avec son code, 5 au plus (le plus ancien part). Effacé après 30 jours sans usage ; un nouveau code les efface tous. Données d''élèves : oui (un jeton au hasard et deux dates, liés au compte).';
comment on column vacances.sessions.jeton is 'Le jeton, tiré au hasard : la page le garde et l''envoie à chaque appel.';
comment on column vacances.sessions.eleve_id is 'Le compte de l''élève (vacances.eleves).';
comment on column vacances.sessions.cree_le is 'La date d''ouverture de la session.';
comment on column vacances.sessions.vu_le is 'La date du dernier usage : la session est effacée 30 jours après.';

create table if not exists vacances.inscriptions (
  eleve_id      uuid not null references vacances.eleves (id) on delete cascade,
  calendrier_id uuid not null references vacances.calendriers (id) on delete cascade,
  depuis        timestamptz not null default now(),
  primary key (eleve_id, calendrier_id)
);
create index if not exists inscriptions_calendrier on vacances.inscriptions (calendrier_id);
alter table vacances.inscriptions enable row level security;
revoke all on vacances.inscriptions from public, anon, authenticated;
comment on table vacances.inscriptions is
  'Calendrier des vacances. Les élèves de chaque calendrier : un·e élève peut être dans plusieurs calendriers avec le même code. Données d''élèves : oui (le lien entre un compte et un calendrier).';
comment on column vacances.inscriptions.eleve_id is 'Le compte de l''élève.';
comment on column vacances.inscriptions.calendrier_id is 'Le calendrier.';
comment on column vacances.inscriptions.depuis is 'La date d''inscription.';

create table if not exists vacances.resultats (
  eleve_id       uuid not null,
  calendrier_id  uuid not null,
  numero         smallint not null,
  niveau         smallint not null check (niveau between 1 and 3),
  reussi         boolean not null,
  etoiles        smallint not null check (etoiles between 0 and 3 and etoiles <= niveau),
  essais         smallint not null check (essais between 0 and 500),
  coups_de_pouce smallint not null check (coups_de_pouce between 0 and 100),
  duree_s        integer not null check (duree_s between 0 and 86400),
  dans_les_temps boolean not null,
  fait_le        timestamptz not null default now(),
  primary key (eleve_id, calendrier_id, numero, niveau),
  foreign key (eleve_id, calendrier_id) references vacances.inscriptions (eleve_id, calendrier_id) on delete cascade,
  foreign key (calendrier_id, numero) references vacances.cases (calendrier_id, numero) on delete restrict
);
create index if not exists resultats_calendrier on vacances.resultats (calendrier_id, fait_le);
alter table vacances.resultats enable row level security;
revoke all on vacances.resultats from public, anon, authenticated;
comment on table vacances.resultats is
  'Calendrier des vacances. Le meilleur résultat de chaque élève pour chaque case et chaque niveau : réussite, étoiles, essais, coups de pouce, durée, date, et s''il a été obtenu avant le corrigé. Jamais les réponses tapées. Données d''élèves : oui.';
comment on column vacances.resultats.eleve_id is 'Le compte de l''élève.';
comment on column vacances.resultats.calendrier_id is 'Le calendrier.';
comment on column vacances.resultats.numero is 'Le numéro de la case.';
comment on column vacances.resultats.niveau is 'Le niveau joué : 1 (facile), 2 (moyen) ou 3 (costaud).';
comment on column vacances.resultats.reussi is 'Vrai si toutes les questions du niveau ont fini par être justes.';
comment on column vacances.resultats.etoiles is 'Les étoiles gagnées, de 0 au niveau joué.';
comment on column vacances.resultats.essais is 'Le nombre de réponses données, justes ou non (essais illimités).';
comment on column vacances.resultats.coups_de_pouce is 'Le nombre de coups de pouce ouverts.';
comment on column vacances.resultats.duree_s is 'La durée de la partie, en secondes.';
comment on column vacances.resultats.dans_les_temps is 'Vrai si la case a été jouée avant l''ouverture de son corrigé ; faux pour un rattrapage.';
comment on column vacances.resultats.fait_le is 'La date du résultat gardé.';

create table if not exists vacances.menage (
  seule_ligne boolean primary key default true check (seule_ligne),
  fait_le     timestamptz not null default now()
);
alter table vacances.menage enable row level security;
revoke all on vacances.menage from public, anon, authenticated;
insert into vacances.menage (fait_le) values (now()) on conflict (seule_ligne) do nothing;
comment on table vacances.menage is
  'Calendrier des vacances. La date du dernier ménage (une seule ligne) : il se fait au plus une fois par heure. Données d''élèves : non.';
comment on column vacances.menage.seule_ligne is 'Toujours vrai : garantit que la table n''a qu''une ligne.';
comment on column vacances.menage.fait_le is 'La date du dernier ménage.';

-- -----------------------------------------------------------------------------
-- 3. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- Le jour à Mayotte (UTC+3, sans heure d'été) : c'est la seule horloge qui compte.
create or replace function vacances.jour()
returns date language sql stable set search_path = '' as $$
  select (now() at time zone 'Indian/Mayotte')::date
$$;

-- La forme canonique d'un code : majuscules, sans accent, sans séparateur.
create or replace function vacances.normaliser_code(p_code text)
returns text language sql immutable set search_path = '' as $$
  select regexp_replace(upper(translate(replace(replace(coalesce(p_code, ''), 'œ', 'oe'), 'Œ', 'OE'),
    'àâäáãåçéèêëíìîïñóòôöõúùûüýÿÀÂÄÁÃÅÇÉÈÊËÍÌÎÏÑÓÒÔÖÕÚÙÛÜÝ',
    'aaaaaaceeeeiiiinooooouuuuyyAAAAAACEEEEIIIINOOOOOUUUUY')), '[^A-Z0-9]', '', 'g')
$$;

-- L'empreinte d'un code d'enseignant·e (forme canonique).
create or replace function vacances.empreinte(p_code text)
returns text language sql immutable set search_path = '' as $$
  select encode(extensions.digest(vacances.normaliser_code(p_code), 'sha256'), 'hex')
$$;

-- Un prénom ou un pseudo propre (espaces réduits), ou null s'il ne convient pas :
-- longueur, caractères de contrôle et caractères invisibles (écrits par leur code).
create or replace function vacances.nettoyer(p_texte text, p_min integer, p_max integer)
returns text language plpgsql immutable set search_path = '' as $$
declare t text := btrim(regexp_replace(left(coalesce(p_texte, ''), 200), '\s+', ' ', 'g'));
begin
  if char_length(t) < p_min or char_length(t) > p_max
     or t ~ ('[' || chr(1) || '-' || chr(31) || chr(127) || '-' || chr(159) || chr(173) || chr(8203) || '-' || chr(8207)
             || chr(8232) || '-' || chr(8238) || chr(8288) || '-' || chr(8303) || chr(65279) || ']') then
    return null;
  end if;
  return t;
end $$;

-- Un code d'élève neuf : 2 mots (un octet modulo 64, sans biais) et 3 chiffres
-- (tirés par rejet, sans biais), jamais un code déjà pris.
create or replace function vacances.nouveau_code_eleve(out code text, out code_affiche text)
language plpgsql volatile set search_path = '' as $$
declare b bytea; v integer; w1 text; w2 text; d text;
begin
  loop
    b := extensions.gen_random_bytes(4);
    v := get_byte(b, 2) * 256 + get_byte(b, 3);
    continue when v >= 64000;
    select m.mot into w1 from vacances.mots m where m.rang = get_byte(b, 0) % 64;
    select m.mot into w2 from vacances.mots m where m.rang = get_byte(b, 1) % 64;
    d := lpad((v % 1000)::text, 3, '0');
    code := w1 || w2 || d;
    code_affiche := w1 || '-' || w2 || '-' || d;
    exit when not exists (select 1 from vacances.eleves e where e.code = nouveau_code_eleve.code);
  end loop;
end $$;

-- Un code d'enseignant·e neuf : 3 mots et 4 chiffres. Seule son empreinte est gardée.
create or replace function vacances.nouveau_code_enseignant(out code text, out code_affiche text)
language plpgsql volatile set search_path = '' as $$
declare b bytea; v integer; w1 text; w2 text; w3 text; d text;
begin
  loop
    b := extensions.gen_random_bytes(5);
    v := get_byte(b, 3) * 256 + get_byte(b, 4);
    continue when v >= 60000;
    select m.mot into w1 from vacances.mots m where m.rang = get_byte(b, 0) % 64;
    select m.mot into w2 from vacances.mots m where m.rang = get_byte(b, 1) % 64;
    select m.mot into w3 from vacances.mots m where m.rang = get_byte(b, 2) % 64;
    d := lpad((v % 10000)::text, 4, '0');
    code := w1 || w2 || w3 || d;
    code_affiche := w1 || '-' || w2 || '-' || w3 || '-' || d;
    exit when not exists (select 1 from vacances.enseignants x where x.code_empreinte = vacances.empreinte(nouveau_code_enseignant.code));
  end loop;
end $$;

-- Un code de calendrier neuf : 4 lettres sans I ni O (24 lettres, un octet par
-- rejet, sans biais), jamais un code déjà pris.
create or replace function vacances.nouveau_code_calendrier()
returns text language plpgsql volatile set search_path = '' as $$
declare a text := 'ABCDEFGHJKLMNPQRSTUVWXYZ'; b bytea; c text; i integer;
begin
  loop
    b := extensions.gen_random_bytes(8);
    c := '';
    for i in 0..7 loop
      if get_byte(b, i) < 240 and char_length(c) < 4 then
        c := c || substr(a, get_byte(b, i) % 24 + 1, 1);
      end if;
    end loop;
    continue when char_length(c) < 4;
    exit when not exists (select 1 from vacances.calendriers x where x.code = c);
  end loop;
  return c;
end $$;

-- Le compte qui porte ce jeton (et la visite du jour), ou null.
create or replace function vacances.eleve_par_jeton(p_jeton uuid)
returns uuid language plpgsql volatile set search_path = '' as $$
declare v uuid;
begin
  update vacances.sessions s set vu_le = now()
   where s.jeton = p_jeton and s.vu_le > now() - interval '30 days'
  returning s.eleve_id into v;
  if v is not null then
    update vacances.eleves e set vu_le = now() where e.id = v and e.vu_le < now() - interval '1 hour';
  end if;
  return v;
end $$;

-- Ouvre une session pour ce compte : 5 au plus, la plus ancienne part.
create or replace function vacances.ouvrir_session(p_eleve uuid)
returns uuid language plpgsql volatile set search_path = '' as $$
declare j uuid;
begin
  insert into vacances.sessions (eleve_id) values (p_eleve) returning jeton into j;
  delete from vacances.sessions s where s.eleve_id = p_eleve and s.jeton not in
    (select x.jeton from vacances.sessions x where x.eleve_id = p_eleve order by x.vu_le desc limit 5);
  update vacances.eleves e set vu_le = now() where e.id = p_eleve;
  return j;
end $$;

-- L'espace qui porte ce code, ou null ; compte les échecs (10 par heure et par réseau).
create or replace function vacances.verifier_enseignant(p_code text, out prof uuid, out message text)
language plpgsql volatile set search_path = '' as $$
begin
  if not commun.essai_permis('vacances', 'enseignant', 10) then
    message := 'Trop d''essais depuis ce réseau. Attends un peu avant de recommencer.';
    return;
  end if;
  update vacances.enseignants x set vu_le = now()
   where x.code_empreinte = vacances.empreinte(left(coalesce(p_code, ''), 80))
  returning x.id into prof;
  if prof is null then
    perform commun.noter_echec('vacances', 'enseignant');
    perform pg_sleep(0.3);
    message := 'Ce code d''enseignant·e n''existe pas.';
  end if;
end $$;

-- (Re)fabrique les cases d'un calendrier à partir du jour p_depuis : efface
-- les cases de ce jour et des suivants, puis les recrée jusqu'à la fin, en
-- continuant la rotation des thèmes et le rang des exercices. Une case qui
-- a des résultats ne peut pas être effacée (clé étrangère « restrict ») : les
-- appelants ne touchent jamais à une case déjà ouverte.
create or replace function vacances.generer_cases(p_cal uuid, p_depuis date)
returns void language plpgsql volatile set search_path = '' as $$
declare c vacances.calendriers; d date; k integer; num integer; ch text; n integer;
begin
  select * into c from vacances.calendriers x where x.id = p_cal;
  delete from vacances.cases x where x.calendrier_id = p_cal and x.jour >= p_depuis;
  select count(*), coalesce(max(x.numero), 0) into k, num from vacances.cases x where x.calendrier_id = p_cal;
  n := cardinality(c.themes);
  for d in select g::date from generate_series(greatest(p_depuis, c.debut), c.fin, interval '1 day') g loop
    if c.mode = 'alternance' then
      ch := c.themes[(k % n) + 1];
      num := num + 1; k := k + 1;
      insert into vacances.cases (calendrier_id, numero, jour, theme, rang)
      values (p_cal, num, d, ch,
              1 + coalesce((select max(x.rang) from vacances.cases x where x.calendrier_id = p_cal and x.theme = ch), 0));
    else
      foreach ch in array c.themes loop
        num := num + 1; k := k + 1;
        insert into vacances.cases (calendrier_id, numero, jour, theme, rang)
        values (p_cal, num, d, ch,
                1 + coalesce((select max(x.rang) from vacances.cases x where x.calendrier_id = p_cal and x.theme = ch), 0));
      end loop;
    end if;
  end loop;
end $$;

-- Ce que voient les élèves de leur classe : des nombres de toute la classe,
-- jamais un nom ni un classement (réglage « jauge »).
create or replace function vacances.classe(p_cal uuid)
returns json language sql stable set search_path = '' as $$
  select case when c.affichage_classe = 'aucun' then json_build_object('affichage', 'aucun')
  else json_build_object(
    'affichage', 'jauge',
    'eleves', (select count(*) from vacances.inscriptions i where i.calendrier_id = c.id),
    'cases_du_calendrier', (select count(*) from vacances.cases x where x.calendrier_id = c.id),
    'cases_faites', (select count(distinct (r.eleve_id, r.numero)) from vacances.resultats r where r.calendrier_id = c.id and r.reussi),
    'cases_faites_aujourdhui', (select count(distinct (r.eleve_id, r.numero)) from vacances.resultats r
                                 where r.calendrier_id = c.id and r.reussi
                                   and (r.fait_le at time zone 'Indian/Mayotte')::date = vacances.jour()),
    'etoiles', (select coalesce(sum(m.e), 0) from (select max(r.etoiles) as e from vacances.resultats r
                 where r.calendrier_id = c.id and r.dans_les_temps group by r.eleve_id, r.numero) m),
    'derniere_reussite', (select max(r.fait_le) from vacances.resultats r where r.calendrier_id = c.id and r.reussi))
  end
  from vacances.calendriers c where c.id = p_cal
$$;

-- L'état d'un calendrier pour un·e élève : ses cases, l'état de chacune, ses
-- résultats et son score. États d'une case, le jour j (heure de Mayotte) :
--   a_venir    j < jour : seul le jour est connu ;
--   ouverte    jour <= j < jour + délai, pas encore réussie : à faire ;
--   en_attente ouverte, mais au-delà des « ouvertes_max » plus anciennes ;
--   faite      réussie avant le corrigé ;
--   corrigee   j >= jour + délai : le corrigé est visible ; elle se rejoue
--              (rattrapage), sans jamais rien effacer.
create or replace function vacances.etat(p_eleve uuid, p_cal uuid)
returns json language sql stable set search_path = '' as $$
  with c as (select * from vacances.calendriers x where x.id = p_cal),
  r as (select x.numero, json_agg(json_build_object('niveau', x.niveau, 'reussi', x.reussi, 'etoiles', x.etoiles,
                 'dans_les_temps', x.dans_les_temps, 'fait_le', x.fait_le) order by x.niveau) as liste,
               bool_or(x.reussi and x.dans_les_temps) as faite,
               max(case when x.dans_les_temps then x.etoiles else 0 end) as etoiles,
               bool_or(x.reussi and not x.dans_les_temps) as rattrapee
          from vacances.resultats x where x.eleve_id = p_eleve and x.calendrier_id = p_cal group by x.numero),
  k as (select s.*, r.liste, coalesce(r.faite, false) as faite, coalesce(r.etoiles, 0) as etoiles,
               coalesce(r.rattrapee, false) as rattrapee,
               case when vacances.jour() < s.jour then 'a_venir'
                    when vacances.jour() >= s.jour + (select c.delai_correction from c) then 'corrigee'
                    when coalesce(r.faite, false) then 'faite'
                    else 'ouverte' end as base
          from vacances.cases s left join r on r.numero = s.numero where s.calendrier_id = p_cal),
  o as (select k.numero, row_number() over (order by k.jour, k.numero) as place from k where k.base = 'ouverte')
  select json_build_object(
    'aujourdhui', vacances.jour(),
    'calendrier', (select json_build_object('id', c.id, 'nom', c.nom, 'debut', c.debut, 'fin', c.fin, 'themes', c.themes,
                   'mode', c.mode, 'ouvertes_max', c.ouvertes_max, 'delai_correction', c.delai_correction,
                   'enseignant', (select e.nom from vacances.enseignants e where e.id = c.enseignant_id)) from c),
    'cases', coalesce((select json_agg(json_build_object(
                 'numero', k.numero, 'jour', k.jour,
                 'theme', case when k.base = 'a_venir' then null else k.theme end,
                 'rang', case when k.base = 'a_venir' then null else k.rang end,
                 'etat', case when k.base = 'ouverte' and o.place > (select c.ouvertes_max from c) then 'en_attente' else k.base end,
                 'corrige_le', k.jour + (select c.delai_correction from c),
                 'resultats', coalesce(k.liste, '[]'::json)) order by k.jour, k.numero)
               from k left join o on o.numero = k.numero), '[]'::json),
    'score', json_build_object(
      'etoiles', (select coalesce(sum(k.etoiles), 0) from k),
      'faites', (select count(*) from k where k.faite),
      'rattrapees', (select count(*) from k where k.rattrapee and not k.faite),
      -- les jours différents où l'élève a réussi au moins une case (jamais une « série » : un jour manqué ne fait rien perdre)
      'jours_differents', (select count(distinct (x.fait_le at time zone 'Indian/Mayotte')::date) from vacances.resultats x
                            where x.eleve_id = p_eleve and x.calendrier_id = p_cal and x.reussi)),
    'classe', vacances.classe(p_cal))
$$;

-- Au plus une fois par heure, au premier appel d'une fonction d'entrée qui le
-- lance : efface les comptes sans visite depuis 12 mois, les calendriers finis
-- depuis 12 mois (avec leurs cases et leurs résultats), les espaces
-- d'enseignant·e·s sans ouverture depuis 24 mois (avec leurs calendriers), et
-- les sessions sans usage depuis 30 jours.
create or replace function vacances.menage_si_besoin()
returns integer language plpgsql volatile set search_path = '' as $$
declare n integer := 0;
begin
  update vacances.menage set fait_le = now() where fait_le < now() - interval '1 hour';
  if found then
    delete from vacances.resultats r using vacances.calendriers c
     where r.calendrier_id = c.id and c.fin < vacances.jour() - interval '12 months';
    delete from vacances.calendriers c where c.fin < vacances.jour() - interval '12 months';
    -- les espaces sans ouverture depuis 24 mois, avec leurs calendriers et leurs résultats
    delete from vacances.resultats r using vacances.calendriers c, vacances.enseignants e
     where r.calendrier_id = c.id and c.enseignant_id = e.id and e.vu_le < now() - interval '24 months';
    delete from vacances.enseignants e where e.vu_le < now() - interval '24 months';
    with efface as (delete from vacances.eleves e where e.vu_le < now() - interval '12 months' returning 1)
    select count(*)::integer into n from efface;
    delete from vacances.sessions s where s.vu_le < now() - interval '30 days';
  end if;
  return n;
end $$;

-- Le résumé d'un compte, pour le compte commun et ses hauts faits (T101) :
-- appelé plus tard par commun, jamais par l'API.
create or replace function vacances.resume_eleve(p_eleve uuid)
returns json language sql stable set search_path = '' as $$
  select json_build_object(
    'application', 'vacances',
    'calendriers', (select count(*) from vacances.inscriptions i where i.eleve_id = p_eleve),
    'cases_faites', (select count(distinct (r.calendrier_id, r.numero)) from vacances.resultats r where r.eleve_id = p_eleve and r.reussi),
    'etoiles', (select coalesce(sum(m.e), 0) from (select max(r.etoiles) e from vacances.resultats r
                 where r.eleve_id = p_eleve and r.dans_les_temps group by r.calendrier_id, r.numero) m),
    'cases_costaudes', (select count(distinct (r.calendrier_id, r.numero)) from vacances.resultats r
                         where r.eleve_id = p_eleve and r.reussi and r.niveau = 3),
    'jours_differents', (select count(distinct (r.fait_le at time zone 'Indian/Mayotte')::date) from vacances.resultats r
                          where r.eleve_id = p_eleve and r.reussi))
$$;

revoke all on function vacances.jour(), vacances.normaliser_code(text), vacances.empreinte(text),
  vacances.nettoyer(text, integer, integer), vacances.nouveau_code_eleve(), vacances.nouveau_code_enseignant(),
  vacances.nouveau_code_calendrier(), vacances.eleve_par_jeton(uuid), vacances.ouvrir_session(uuid),
  vacances.verifier_enseignant(text), vacances.generer_cases(uuid, date), vacances.classe(uuid),
  vacances.etat(uuid, uuid), vacances.menage_si_besoin(), vacances.resume_eleve(uuid)
  from public, anon, authenticated;
comment on function vacances.jour() is 'Calendrier des vacances, interne. Le jour à l''heure de Mayotte.';
comment on function vacances.normaliser_code(text) is 'Calendrier des vacances, interne. La forme canonique d''un code.';
comment on function vacances.empreinte(text) is 'Calendrier des vacances, interne. L''empreinte SHA-256 d''un code d''enseignant·e.';
comment on function vacances.nettoyer(text, integer, integer) is 'Calendrier des vacances, interne. Un texte court nettoyé, ou null s''il ne convient pas.';
comment on function vacances.nouveau_code_eleve() is 'Calendrier des vacances, interne. Tire un code d''élève neuf (2 mots et 3 chiffres, sans biais).';
comment on function vacances.nouveau_code_enseignant() is 'Calendrier des vacances, interne. Tire un code d''enseignant·e neuf (3 mots et 4 chiffres, sans biais).';
comment on function vacances.nouveau_code_calendrier() is 'Calendrier des vacances, interne. Tire un code de calendrier neuf (4 lettres sans I ni O).';
comment on function vacances.eleve_par_jeton(uuid) is 'Calendrier des vacances, interne. Le compte qui porte ce jeton, ou null.';
comment on function vacances.ouvrir_session(uuid) is 'Calendrier des vacances, interne. Ouvre une session (5 au plus par compte).';
comment on function vacances.verifier_enseignant(text) is 'Calendrier des vacances, interne. L''espace qui porte ce code ; 10 échecs au plus par heure et par réseau.';
comment on function vacances.generer_cases(uuid, date) is 'Calendrier des vacances, interne. Refait les cases d''un calendrier à partir d''un jour, sans jamais toucher une case qui a des résultats.';
comment on function vacances.classe(uuid) is 'Calendrier des vacances, interne. Les nombres de toute la classe, sans aucun nom.';
comment on function vacances.etat(uuid, uuid) is 'Calendrier des vacances, interne. L''état d''un calendrier pour un·e élève : cases, résultats, score (étoiles, cases faites, rattrapages, jours différents ; aucun rang).';
comment on function vacances.menage_si_besoin() is 'Calendrier des vacances, interne. Le ménage, au premier usage après l''échéance : comptes (12 mois), calendriers (12 mois après la fin), espaces enseignant·e·s (24 mois), sessions (30 jours).';
comment on function vacances.resume_eleve(uuid) is 'Calendrier des vacances, interne. Le résumé d''un compte, pour le compte commun (T101).';

-- -----------------------------------------------------------------------------
-- 4. Les fonctions d'entrée des élèves : public, security definer, anon seul.
--    Elles bornent chaque paramètre et répondent { "ok": false, "message" }
--    plutôt que de lever une exception (qui annulerait le compteur d'essais).
-- -----------------------------------------------------------------------------

-- Le calendrier derrière un lien : son nom, l'enseignant·e, les dates.
create or replace function public.cv_calendrier_par_code(p_code_calendrier text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare c vacances.calendriers; k text := vacances.normaliser_code(left(coalesce(p_code_calendrier, ''), 20));
begin
  if not commun.essai_permis('vacances', 'classe', 30) then
    return json_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu, ou demande le lien à ton enseignant·e.');
  end if;
  select * into c from vacances.calendriers x where x.code = k;
  if c.id is null then
    perform commun.noter_echec('vacances', 'classe');
    return json_build_object('ok', false, 'message', 'Ce lien ne mène à aucun calendrier. Vérifie-le avec ton enseignant·e.');
  end if;
  return json_build_object('ok', true, 'nom', c.nom, 'debut', c.debut, 'fin', c.fin,
    'enseignant', (select e.nom from vacances.enseignants e where e.id = c.enseignant_id),
    'inscriptions_ouvertes', c.inscriptions_ouvertes);
end $$;

-- S'inscrire par le lien : crée le compte, renvoie le code (montré une fois en
-- gros) et un jeton. 60 créations au plus par heure et par réseau.
create or replace function public.cv_inscription(p_code_calendrier text, p_pseudo text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare c vacances.calendriers; ps text := vacances.nettoyer(p_pseudo, 2, 24); n record; e vacances.eleves;
        k text := vacances.normaliser_code(left(coalesce(p_code_calendrier, ''), 20));
begin
  if ps is null then
    return json_build_object('ok', false, 'message', 'Écris un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).');
  end if;
  if not commun.essai_permis('vacances', 'creation', 60) then
    return json_build_object('ok', false, 'message', 'Trop de codes créés depuis ce réseau : attends un peu, ou demande de l''aide à ton enseignant·e.');
  end if;
  select * into c from vacances.calendriers x where x.code = k;
  if c.id is null then
    perform commun.noter_echec('vacances', 'classe');
    return json_build_object('ok', false, 'message', 'Ce lien ne mène à aucun calendrier. Vérifie-le avec ton enseignant·e.');
  end if;
  if not c.inscriptions_ouvertes then
    return json_build_object('ok', false, 'message', 'Les inscriptions à ce calendrier sont fermées. Si tu as déjà un code, utilise-le.');
  end if;
  -- un prénom déjà pris compte comme un essai « classe » : on ne peut pas tester les prénoms sans limite
  if not commun.essai_permis('vacances', 'classe', 30) then
    return json_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu, ou demande de l''aide à ton enseignant·e.');
  end if;
  if exists (select 1 from vacances.inscriptions i join vacances.eleves x on x.id = i.eleve_id
             where i.calendrier_id = c.id and lower(x.pseudo) = lower(ps)) then
    perform commun.noter_echec('vacances', 'classe');
    return json_build_object('ok', false, 'message', 'Ce prénom est déjà pris dans ce calendrier. Si c''est toi, utilise ton code ; sinon, ajoute une initiale.');
  end if;
  perform commun.noter_echec('vacances', 'creation');
  perform vacances.menage_si_besoin();
  select * into n from vacances.nouveau_code_eleve();
  insert into vacances.eleves (pseudo, code, code_affiche) values (ps, n.code, n.code_affiche) returning * into e;
  insert into vacances.inscriptions (eleve_id, calendrier_id) values (e.id, c.id);
  return json_build_object('ok', true, 'pseudo', e.pseudo, 'code_affiche', e.code_affiche,
    'jeton', vacances.ouvrir_session(e.id), 'calendrier', c.id);
end $$;

-- Entrer avec son code, depuis n'importe quel appareil : 20 échecs au plus par
-- heure et par réseau. Renvoie un jeton et la liste de ses calendriers.
create or replace function public.cv_connexion(p_code text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare k text := vacances.normaliser_code(left(coalesce(p_code, ''), 60)); e vacances.eleves;
begin
  if not commun.essai_permis('vacances', 'eleve', 20) then
    return json_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu, ou demande ton code à ton enseignant·e.');
  end if;
  select * into e from vacances.eleves x where x.code = k;
  if e.id is null then
    perform commun.noter_echec('vacances', 'eleve');
    perform pg_sleep(0.3);
    return json_build_object('ok', false, 'message', 'Ce code n''existe pas. Vérifie-le dans ton cahier.');
  end if;
  perform vacances.menage_si_besoin();
  return json_build_object('ok', true, 'pseudo', e.pseudo, 'code_affiche', e.code_affiche, 'jeton', vacances.ouvrir_session(e.id),
    'calendriers', coalesce((select json_agg(json_build_object('id', c.id, 'nom', c.nom, 'debut', c.debut, 'fin', c.fin) order by c.debut desc)
                             from vacances.inscriptions i join vacances.calendriers c on c.id = i.calendrier_id
                            where i.eleve_id = e.id), '[]'::json));
end $$;

-- Rejoindre un autre calendrier avec son code (« J'ai déjà un code »).
create or replace function public.cv_rejoindre(p_jeton uuid, p_code_calendrier text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := vacances.eleve_par_jeton(p_jeton); c vacances.calendriers;
        k text := vacances.normaliser_code(left(coalesce(p_code_calendrier, ''), 20));
begin
  if v is null then
    return json_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if not commun.essai_permis('vacances', 'classe', 30) then
    return json_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  select * into c from vacances.calendriers x where x.code = k;
  if c.id is null then
    perform commun.noter_echec('vacances', 'classe');
    return json_build_object('ok', false, 'message', 'Ce lien ne mène à aucun calendrier.');
  end if;
  if not exists (select 1 from vacances.inscriptions i where i.eleve_id = v and i.calendrier_id = c.id) then
    if not c.inscriptions_ouvertes then
      return json_build_object('ok', false, 'message', 'Les inscriptions à ce calendrier sont fermées.');
    end if;
    insert into vacances.inscriptions (eleve_id, calendrier_id) values (v, c.id);
  end if;
  return json_build_object('ok', true, 'calendrier', c.id, 'nom', c.nom);
end $$;

-- Reprendre sa session : pseudo, code et calendriers.
create or replace function public.cv_reprise(p_jeton uuid)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := vacances.eleve_par_jeton(p_jeton); e vacances.eleves;
begin
  if v is null then
    return json_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  select * into e from vacances.eleves x where x.id = v;
  return json_build_object('ok', true, 'pseudo', e.pseudo, 'code_affiche', e.code_affiche,
    'calendriers', coalesce((select json_agg(json_build_object('id', c.id, 'nom', c.nom, 'debut', c.debut, 'fin', c.fin) order by c.debut desc)
                             from vacances.inscriptions i join vacances.calendriers c on c.id = i.calendrier_id
                            where i.eleve_id = v), '[]'::json));
end $$;

-- L'état d'un de ses calendriers : cases, résultats, score, jauge de la classe.
create or replace function public.cv_calendrier(p_jeton uuid, p_calendrier uuid)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := vacances.eleve_par_jeton(p_jeton);
begin
  if v is null then
    return json_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  if not exists (select 1 from vacances.inscriptions i where i.eleve_id = v and i.calendrier_id = p_calendrier) then
    return json_build_object('ok', false, 'message', 'Tu n''es pas dans ce calendrier.');
  end if;
  return json_build_object('ok', true, 'etat', vacances.etat(v, p_calendrier));
end $$;

-- Garder le résultat d'une partie (le meilleur reste). La case doit être
-- ouverte ou corrigée (jamais à venir) ; « dans les temps » se décide ici,
-- à l'heure de Mayotte, pas à celle du téléphone. Renvoie l'état à jour.
create or replace function public.cv_resultat(p_jeton uuid, p_calendrier uuid, p_numero integer, p_niveau integer,
  p_reussi boolean, p_etoiles integer, p_essais integer, p_coups_de_pouce integer, p_duree_s integer)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := vacances.eleve_par_jeton(p_jeton); s vacances.cases; dl smallint; t boolean;
begin
  if v is null then
    return json_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code. Ta partie est gardée sur ce téléphone.');
  end if;
  if p_niveau is null or p_niveau not between 1 and 3 or p_reussi is null
     or p_etoiles is null or p_etoiles not between 0 and p_niveau
     or p_essais is null or p_essais not between 0 and 500
     or p_coups_de_pouce is null or p_coups_de_pouce not between 0 and 100
     or p_duree_s is null or p_duree_s not between 0 and 86400 then
    return json_build_object('ok', false, 'message', 'Résultat illisible : il n''a pas été gardé.');
  end if;
  if not exists (select 1 from vacances.inscriptions i where i.eleve_id = v and i.calendrier_id = p_calendrier) then
    return json_build_object('ok', false, 'message', 'Tu n''es pas dans ce calendrier.');
  end if;
  select * into s from vacances.cases x where x.calendrier_id = p_calendrier and x.numero = p_numero;
  if s.numero is null or s.jour > vacances.jour() then
    return json_build_object('ok', false, 'message', 'Cette case n''est pas encore ouverte.');
  end if;
  select c.delai_correction into dl from vacances.calendriers c where c.id = p_calendrier;
  t := vacances.jour() < s.jour + dl;
  insert into vacances.resultats as r (eleve_id, calendrier_id, numero, niveau, reussi, etoiles, essais, coups_de_pouce, duree_s, dans_les_temps)
  values (v, p_calendrier, p_numero, p_niveau, p_reussi, case when p_reussi then p_etoiles else 0 end,
          p_essais, p_coups_de_pouce, p_duree_s, t)
  on conflict (eleve_id, calendrier_id, numero, niveau) do update set
    reussi = excluded.reussi, etoiles = excluded.etoiles, essais = excluded.essais,
    coups_de_pouce = excluded.coups_de_pouce, duree_s = excluded.duree_s,
    dans_les_temps = excluded.dans_les_temps, fait_le = now()
  -- on ne remplace un résultat que par un meilleur : rien ne se perd
  where (excluded.reussi and not r.reussi)
     or (excluded.reussi = r.reussi and excluded.dans_les_temps >= r.dans_les_temps and excluded.etoiles > r.etoiles)
     or (excluded.dans_les_temps and not r.dans_les_temps and excluded.reussi);
  return json_build_object('ok', true, 'etat', vacances.etat(v, p_calendrier));
end $$;

-- La jauge de la classe, pour le score en direct (appelée toutes les 30 s au
-- plus, et seulement quand la page est à l'écran).
create or replace function public.cv_classe(p_jeton uuid, p_calendrier uuid)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := vacances.eleve_par_jeton(p_jeton);
begin
  if v is null or not exists (select 1 from vacances.inscriptions i where i.eleve_id = v and i.calendrier_id = p_calendrier) then
    return json_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  return json_build_object('ok', true, 'aujourdhui', vacances.jour(), 'classe', vacances.classe(p_calendrier));
end $$;

-- Fermer la session de cet appareil (« Ce n'est pas moi », « Quitter »).
create or replace function public.cv_deconnexion(p_jeton uuid)
returns json language sql volatile security definer set search_path = '' as $$
  with d as (delete from vacances.sessions s where s.jeton = p_jeton returning 1)
  select json_build_object('ok', exists (select 1 from d))
$$;

-- Effacer son compte, ses inscriptions et tous ses résultats (« Effacer mes données »).
create or replace function public.cv_effacer_moi(p_jeton uuid)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := vacances.eleve_par_jeton(p_jeton);
begin
  if v is null then
    return json_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.');
  end if;
  delete from vacances.eleves e where e.id = v;
  return json_build_object('ok', true);
end $$;

-- -----------------------------------------------------------------------------
-- 5. Les fonctions d'entrée des enseignant·e·s : le code (3 mots et 4 chiffres)
--    à chaque appel, 10 échecs au plus par heure et par réseau.
-- -----------------------------------------------------------------------------

-- Créer son espace : le code est renvoyé une seule fois.
create or replace function public.cv_prof_creer_espace(p_nom text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare nm text := vacances.nettoyer(p_nom, 2, 40); n record;
begin
  if nm is null then
    return json_build_object('ok', false, 'message', 'Donne un nom affiché de 2 à 40 caractères (« Mme N. », « M. K. »).');
  end if;
  if not commun.essai_permis('vacances', 'creation', 60) then
    return json_build_object('ok', false, 'message', 'Trop d''espaces créés depuis ce réseau : attends un peu.');
  end if;
  perform commun.noter_echec('vacances', 'creation');
  select * into n from vacances.nouveau_code_enseignant();
  insert into vacances.enseignants (nom, code_empreinte) values (nm, vacances.empreinte(n.code));
  return json_build_object('ok', true, 'nom', nm, 'code_affiche', n.code_affiche);
end $$;

-- Ouvrir son espace : son nom et ses calendriers.
create or replace function public.cv_prof_ouvrir(p_code text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  perform vacances.menage_si_besoin();
  return json_build_object('ok', true, 'aujourdhui', vacances.jour(),
    'nom', (select e.nom from vacances.enseignants e where e.id = p.prof),
    'calendriers', coalesce((select json_agg(json_build_object('id', c.id, 'nom', c.nom, 'code', c.code, 'debut', c.debut, 'fin', c.fin,
                    'themes', c.themes, 'mode', c.mode, 'affichage_classe', c.affichage_classe,
                    'inscriptions_ouvertes', c.inscriptions_ouvertes,
                    'eleves', (select count(*) from vacances.inscriptions i where i.calendrier_id = c.id)) order by c.debut desc)
                   from vacances.calendriers c where c.enseignant_id = p.prof), '[]'::json));
end $$;

-- Créer un calendrier : dates (30 jours au plus, à partir d'aujourd'hui),
-- thèmes dans l'ordre (chapitres ou notions, de tout niveau), mode et affichage de la classe.
create or replace function public.cv_prof_creer_calendrier(p_code text, p_nom text, p_debut date, p_fin date,
  p_themes text[], p_mode text default 'alternance', p_affichage_classe text default 'jauge')
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record; nm text := vacances.nettoyer(p_nom, 2, 60); cal uuid; ch text;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  if nm is null then return json_build_object('ok', false, 'message', 'Donne au calendrier un nom de 2 à 60 caractères.'); end if;
  if p_debut is null or p_fin is null or p_fin < p_debut or p_fin - p_debut > 29 then
    return json_build_object('ok', false, 'message', 'Les dates ne vont pas : la fin suit le début, et le calendrier dure 30 jours au plus.');
  end if;
  if p_debut < vacances.jour() or p_debut > vacances.jour() + 366 then
    return json_build_object('ok', false, 'message', 'Le premier jour est aujourd''hui au plus tôt, et dans un an au plus tard.');
  end if;
  if p_themes is null or cardinality(p_themes) not between 1 and 20 then
    return json_build_object('ok', false, 'message', 'Choisis de 1 à 20 thèmes.');
  end if;
  foreach ch in array p_themes loop
    if ch is null or ch !~ '^[a-z0-9]+(-[a-z0-9]+)*$' or char_length(ch) > 60 then
      return json_build_object('ok', false, 'message', 'Un identifiant de thème est illisible.');
    end if;
  end loop;
  if (select count(distinct x) from unnest(p_themes) x) <> cardinality(p_themes) then
    return json_build_object('ok', false, 'message', 'Un thème est choisi deux fois.');
  end if;
  if coalesce(p_mode, '') not in ('alternance', 'chaque_theme') or coalesce(p_affichage_classe, '') not in ('jauge', 'aucun') then
    return json_build_object('ok', false, 'message', 'Réglage illisible.');
  end if;
  insert into vacances.calendriers (enseignant_id, nom, code, debut, fin, themes, mode, affichage_classe)
  values (p.prof, nm, vacances.nouveau_code_calendrier(), p_debut, p_fin, p_themes, p_mode, p_affichage_classe)
  returning id into cal;
  perform vacances.generer_cases(cal, p_debut);
  return json_build_object('ok', true, 'id', cal, 'code', (select c.code from vacances.calendriers c where c.id = cal),
    'cases', (select count(*) from vacances.cases x where x.calendrier_id = cal));
end $$;

-- Modifier un calendrier. Avant le premier jour : tout change. Ensuite : le
-- premier jour reste, et seules les cases de demain et des jours suivants sont
-- refaites ; une case déjà ouverte, et ses résultats, ne bougent jamais.
create or replace function public.cv_prof_modifier_calendrier(p_code text, p_calendrier uuid, p_nom text, p_debut date, p_fin date,
  p_themes text[], p_mode text, p_affichage_classe text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record; c vacances.calendriers; nm text := vacances.nettoyer(p_nom, 2, 60); ch text; commence boolean;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  select * into c from vacances.calendriers x where x.id = p_calendrier and x.enseignant_id = p.prof;
  if c.id is null then return json_build_object('ok', false, 'message', 'Ce calendrier n''est pas dans ton espace.'); end if;
  if nm is null then return json_build_object('ok', false, 'message', 'Donne au calendrier un nom de 2 à 60 caractères.'); end if;
  commence := vacances.jour() >= c.debut;
  if commence and p_debut is distinct from c.debut then
    return json_build_object('ok', false, 'message', 'Le calendrier a commencé : son premier jour ne change plus.');
  end if;
  if p_debut is null or p_fin is null or p_fin < p_debut or p_fin - p_debut > 29 then
    return json_build_object('ok', false, 'message', 'Les dates ne vont pas : la fin suit le début, et le calendrier dure 30 jours au plus.');
  end if;
  if not commence and p_debut < vacances.jour() then
    return json_build_object('ok', false, 'message', 'Le premier jour est aujourd''hui au plus tôt.');
  end if;
  if commence and p_fin < vacances.jour() and p_fin <> c.fin then
    return json_build_object('ok', false, 'message', 'La fin ne peut pas être avant aujourd''hui : les cases déjà ouvertes restent.');
  end if;
  if p_themes is null or cardinality(p_themes) not between 1 and 20
     or (select count(distinct x) from unnest(p_themes) x) <> cardinality(p_themes) then
    return json_build_object('ok', false, 'message', 'Choisis de 1 à 20 thèmes, chacun une fois.');
  end if;
  foreach ch in array p_themes loop
    if ch is null or ch !~ '^[a-z0-9]+(-[a-z0-9]+)*$' or char_length(ch) > 60 then
      return json_build_object('ok', false, 'message', 'Un identifiant de thème est illisible.');
    end if;
  end loop;
  if coalesce(p_mode, '') not in ('alternance', 'chaque_theme') or coalesce(p_affichage_classe, '') not in ('jauge', 'aucun') then
    return json_build_object('ok', false, 'message', 'Réglage illisible.');
  end if;
  update vacances.calendriers x set nom = nm, debut = p_debut, fin = p_fin, themes = p_themes,
    mode = p_mode, affichage_classe = p_affichage_classe where x.id = c.id;
  perform vacances.generer_cases(c.id, case when commence then vacances.jour() + 1 else least(c.debut, p_debut) end);
  return json_build_object('ok', true, 'cases', (select count(*) from vacances.cases x where x.calendrier_id = c.id));
end $$;

-- Le tableau d'un calendrier : chaque élève (pseudo, code, résultats) et les
-- cases, en un seul objet JSON (aucune coupure à 1 000 lignes).
create or replace function public.cv_prof_tableau(p_code text, p_calendrier uuid)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  if not exists (select 1 from vacances.calendriers c where c.id = p_calendrier and c.enseignant_id = p.prof) then
    return json_build_object('ok', false, 'message', 'Ce calendrier n''est pas dans ton espace.');
  end if;
  return json_build_object('ok', true, 'aujourdhui', vacances.jour(),
    'cases', coalesce((select json_agg(json_build_object('numero', x.numero, 'jour', x.jour, 'theme', x.theme, 'rang', x.rang)
                        order by x.jour, x.numero) from vacances.cases x where x.calendrier_id = p_calendrier), '[]'::json),
    'eleves', coalesce((select json_agg(json_build_object('id', e.id, 'pseudo', e.pseudo, 'code_affiche', e.code_affiche,
                         'vu_le', e.vu_le, 'depuis', i.depuis,
                         'resultats', coalesce((select json_agg(json_build_object('numero', r.numero, 'niveau', r.niveau, 'reussi', r.reussi,
                                        'etoiles', r.etoiles, 'essais', r.essais, 'coups_de_pouce', r.coups_de_pouce, 'duree_s', r.duree_s,
                                        'dans_les_temps', r.dans_les_temps, 'fait_le', r.fait_le) order by r.numero, r.niveau)
                                      from vacances.resultats r where r.eleve_id = e.id and r.calendrier_id = p_calendrier), '[]'::json))
                        order by lower(e.pseudo))
                       from vacances.inscriptions i join vacances.eleves e on e.id = i.eleve_id
                      where i.calendrier_id = p_calendrier), '[]'::json));
end $$;

-- Ouvrir ou fermer les inscriptions par le lien.
create or replace function public.cv_prof_inscriptions(p_code text, p_calendrier uuid, p_ouvertes boolean)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  update vacances.calendriers c set inscriptions_ouvertes = coalesce(p_ouvertes, false)
   where c.id = p_calendrier and c.enseignant_id = p.prof;
  return json_build_object('ok', found);
end $$;

-- Un nouveau code pour un·e élève de ses calendriers (code perdu ou divulgué) :
-- l'ancien cesse de marcher, et ses sessions sont fermées. Les résultats restent.
create or replace function public.cv_prof_nouveau_code_eleve(p_code text, p_calendrier uuid, p_eleve uuid)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record; n record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  if not exists (select 1 from vacances.inscriptions i join vacances.calendriers c on c.id = i.calendrier_id
                  where i.eleve_id = p_eleve and c.id = p_calendrier and c.enseignant_id = p.prof) then
    return json_build_object('ok', false, 'message', 'Cet·te élève n''est pas dans ce calendrier.');
  end if;
  select * into n from vacances.nouveau_code_eleve();
  update vacances.eleves e set code = n.code, code_affiche = n.code_affiche where e.id = p_eleve;
  delete from vacances.sessions s where s.eleve_id = p_eleve;
  return json_build_object('ok', true, 'code_affiche', n.code_affiche);
end $$;

-- Renommer un·e élève (un nom de famille écrit par erreur, un pseudo déplacé).
create or replace function public.cv_prof_renommer_eleve(p_code text, p_calendrier uuid, p_eleve uuid, p_pseudo text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record; ps text := vacances.nettoyer(p_pseudo, 2, 24);
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  if ps is null then return json_build_object('ok', false, 'message', 'Un prénom ou un pseudo de 2 à 24 caractères.'); end if;
  if not exists (select 1 from vacances.inscriptions i join vacances.calendriers c on c.id = i.calendrier_id
                  where i.eleve_id = p_eleve and c.id = p_calendrier and c.enseignant_id = p.prof) then
    return json_build_object('ok', false, 'message', 'Cet·te élève n''est pas dans ce calendrier.');
  end if;
  update vacances.eleves e set pseudo = ps where e.id = p_eleve;
  return json_build_object('ok', true);
end $$;

-- Retirer un·e élève d'un calendrier : son inscription et ses résultats dans ce
-- calendrier partent ; son compte reste (il ou elle garde ses autres calendriers).
-- Il faut écrire « RETIRER » : c'est définitif.
create or replace function public.cv_prof_retirer_eleve(p_code text, p_calendrier uuid, p_eleve uuid, p_confirmation text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  if coalesce(p_confirmation, '') <> 'RETIRER' then
    return json_build_object('ok', false, 'message', 'Écris RETIRER pour confirmer : ses résultats dans ce calendrier seront effacés.');
  end if;
  delete from vacances.inscriptions i using vacances.calendriers c
   where i.calendrier_id = c.id and c.id = p_calendrier and c.enseignant_id = p.prof and i.eleve_id = p_eleve;
  return json_build_object('ok', found);
end $$;

-- Supprimer un calendrier, ses cases et tous ses résultats. Il faut écrire son
-- code : c'est définitif. Les comptes des élèves restent.
create or replace function public.cv_prof_supprimer_calendrier(p_code text, p_calendrier uuid, p_confirmation text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record; c vacances.calendriers;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  select * into c from vacances.calendriers x where x.id = p_calendrier and x.enseignant_id = p.prof;
  if c.id is null then return json_build_object('ok', false, 'message', 'Ce calendrier n''est pas dans ton espace.'); end if;
  if vacances.normaliser_code(coalesce(p_confirmation, '')) <> c.code then
    return json_build_object('ok', false, 'message', 'Écris le code du calendrier (' || c.code || ') pour confirmer : tous ses résultats seront effacés.');
  end if;
  delete from vacances.resultats r where r.calendrier_id = c.id;
  delete from vacances.calendriers x where x.id = c.id;
  return json_build_object('ok', true);
end $$;

-- Débloquer le réseau de la salle (trop d'échecs de codes depuis le lycée).
create or replace function public.cv_prof_debloquer_reseau(p_code text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  perform commun.debloquer_reseau('vacances');
  return json_build_object('ok', true);
end $$;

-- Changer son propre code (il faut donner l'ancien) : le nouveau est montré une fois.
create or replace function public.cv_prof_nouveau_code(p_code text)
returns json language plpgsql volatile security definer set search_path = '' as $$
declare p record; n record;
begin
  select * into p from vacances.verifier_enseignant(p_code);
  if p.prof is null then return json_build_object('ok', false, 'message', p.message); end if;
  select * into n from vacances.nouveau_code_enseignant();
  update vacances.enseignants e set code_empreinte = vacances.empreinte(n.code) where e.id = p.prof;
  return json_build_object('ok', true, 'code_affiche', n.code_affiche);
end $$;

revoke all on function
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
  public.cv_prof_debloquer_reseau(text), public.cv_prof_nouveau_code(text)
  from public, anon, authenticated;
grant execute on function
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
  public.cv_prof_debloquer_reseau(text), public.cv_prof_nouveau_code(text)
  to anon;

comment on function public.cv_calendrier_par_code(text) is 'Calendrier des vacances, entrée. Le calendrier derrière un lien : nom, enseignant·e, dates, inscriptions ouvertes. 30 échecs au plus par heure et par réseau.';
comment on function public.cv_inscription(text, text) is 'Calendrier des vacances, entrée. Inscrit un·e élève par le lien (prénom ou pseudo) ; renvoie son code et un jeton. 60 créations au plus par heure et par réseau.';
comment on function public.cv_connexion(text) is 'Calendrier des vacances, entrée. Entre avec son code ; renvoie un jeton et ses calendriers. 20 échecs au plus par heure et par réseau.';
comment on function public.cv_rejoindre(uuid, text) is 'Calendrier des vacances, entrée. Avec le jeton : rejoint un autre calendrier par son code.';
comment on function public.cv_reprise(uuid) is 'Calendrier des vacances, entrée. Avec le jeton : pseudo, code et calendriers.';
comment on function public.cv_calendrier(uuid, uuid) is 'Calendrier des vacances, entrée. Avec le jeton : l''état d''un calendrier (cases, résultats, score, jauge de la classe).';
comment on function public.cv_resultat(uuid, uuid, integer, integer, boolean, integer, integer, integer, integer) is 'Calendrier des vacances, entrée. Avec le jeton : garde le résultat d''une partie (le meilleur reste) et renvoie l''état à jour.';
comment on function public.cv_classe(uuid, uuid) is 'Calendrier des vacances, entrée. Avec le jeton : la jauge de la classe (des nombres, aucun nom).';
comment on function public.cv_deconnexion(uuid) is 'Calendrier des vacances, entrée. Ferme la session de cet appareil.';
comment on function public.cv_effacer_moi(uuid) is 'Calendrier des vacances, entrée. Avec le jeton : efface le compte, ses inscriptions et ses résultats.';
comment on function public.cv_prof_creer_espace(text) is 'Calendrier des vacances, entrée. Crée un espace enseignant·e ; le code est renvoyé une seule fois.';
comment on function public.cv_prof_ouvrir(text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : le nom et les calendriers.';
comment on function public.cv_prof_creer_calendrier(text, text, date, date, text[], text, text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : crée un calendrier (30 jours au plus) et ses cases.';
comment on function public.cv_prof_modifier_calendrier(text, uuid, text, date, date, text[], text, text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : modifie un calendrier sans toucher aux cases déjà ouvertes.';
comment on function public.cv_prof_tableau(text, uuid) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : élèves, codes et résultats d''un calendrier, en un seul objet JSON.';
comment on function public.cv_prof_inscriptions(text, uuid, boolean) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : ouvre ou ferme les inscriptions.';
comment on function public.cv_prof_nouveau_code_eleve(text, uuid, uuid) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : un nouveau code pour un·e élève ; ses résultats restent.';
comment on function public.cv_prof_renommer_eleve(text, uuid, uuid, text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : renomme un·e élève.';
comment on function public.cv_prof_retirer_eleve(text, uuid, uuid, text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e et « RETIRER » : retire un·e élève d''un calendrier, avec ses résultats dans ce calendrier.';
comment on function public.cv_prof_supprimer_calendrier(text, uuid, text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e et le code du calendrier : supprime le calendrier, ses cases et ses résultats.';
comment on function public.cv_prof_debloquer_reseau(text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : débloque le réseau de la salle pour cette application.';
comment on function public.cv_prof_nouveau_code(text) is 'Calendrier des vacances, entrée. Avec le code enseignant·e : le remplace par un nouveau, montré une seule fois.';

-- -----------------------------------------------------------------------------
-- 6. Contrôle : rien d'ouvert à l'API, sauf les 22 fonctions d'entrée.
--    Sinon, arrêt : rien n'est appliqué.
-- -----------------------------------------------------------------------------
do $$
begin
  if has_schema_privilege('anon', 'vacances', 'usage') or has_schema_privilege('authenticated', 'vacances', 'usage') then
    raise exception 'Le schéma vacances est ouvert à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'vacances'::regnamespace and c.relkind = 'r'
             and (not c.relrowsecurity
                  or has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de vacances est ouverte, ou sans RLS : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'vacances'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction interne de vacances est appelable par l''API : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'cv\_%'
      and p.prosecdef and has_function_privilege('anon', p.oid, 'execute') and not has_function_privilege('authenticated', p.oid, 'execute')) <> 22 then
    raise exception 'Les 22 fonctions d''entrée cv_… ne sont pas appelables par anon seul : arrêt, rien n''a été modifié.';
  end if;
  if (select count(*) from vacances.mots) <> 64 then
    raise exception 'vacances.mots doit avoir 64 mots : arrêt, rien n''a été modifié.';
  end if;
end $$;

commit;
