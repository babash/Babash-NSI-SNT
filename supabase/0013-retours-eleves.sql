begin;
-- =============================================================================
--  Base unique : les retours anonymes des élèves sur les ressources (T163)
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0013_retours_eleves
--  Fichier : supabase/0013-retours-eleves.sql du dépôt du site
-- =============================================================================
--  PROPOSITION : rien n'est appliqué. À relire par un Gardien, puis à montrer
--  à l'enseignant (règle M4), qui le colle lui-même dans l'éditeur SQL.
--  Suppose 0003, 0007 et 0008 appliqués (en base depuis le 24/11/2026).
--  Ne dépend pas de 0010, 0011 ni 0012 (ni eux de lui) : il se colle avant
--  ou après eux.
--
--  Pourquoi (l'enseignant, 25/11/2026) : à la fin d'une ressource en ligne,
--  un·e élève donne son avis en dix secondes, sans compte et sans obligation ;
--  l'enseignant·e voit « ce qui marche en pratique ».
--
--  L'anonymat, tel que ce fichier le construit :
--   - un retour ne garde ni compte, ni code, ni pseudo, ni adresse, ni heure :
--     seulement la semaine (le lundi, heure de Mayotte), la ressource, et la
--     classe commune si la page en connaît le code (lien …?classe=ABCD) ;
--   - pour pouvoir changer son avis pendant la semaine, l'appareil garde une
--     clé tirée au hasard pour cette ressource ; la base n'en garde que
--     l'empreinte, effacée dès la semaine finie : le retour n'est alors plus
--     rattaché à rien ;
--   - on ne voit rien de la semaine en cours, et les retours ne se montrent
--     que par paquets d'au moins 5 (par classe et par ressource, et pour
--     « tout le monde » par ressource) : un paquet, une fois montré, ne
--     change plus ; ce qui reste sous 5 attend les semaines suivantes ;
--   - le mot libre (140 caractères) n'est gardé que si la classe est connue,
--     n'est lu que par l'enseignant·e de cette classe, jamais affiché aux
--     élèves, et peut être effacé par l'élève (pendant la semaine) et par
--     l'enseignant·e ; ni adresse, ni lien, ni numéro de téléphone.
--  Contre les abus, sans identifier : 300 envois par heure et par réseau
--  (empreinte du jour dans commun.essais, jamais l'adresse, effacée après
--  24 h ; une classe de 35 derrière la même box passe largement), 1 500
--  retours par ressource et par semaine, 20 000 par semaine, 300 000 en tout.
--  Effacement : chaque retour part deux ans après sa semaine.
--
--  Ce que ce fichier crée :
--   - la table commun.retours (RLS, aucun droit pour l'API) ;
--   - 3 fonctions internes (aucun droit) : commun.retour_semaine(),
--     commun.retour_cle(text), commun.retours_publier() ;
--   - 4 fonctions d'entrée, appelables par anon seul (security definer,
--     search_path vide) :
--       commun_retour_donner (l'élève donne ou change son avis),
--       commun_retour_effacer (l'élève retire son avis de la semaine),
--       commun_prof_retours (l'enseignant·e lit les paquets publiés),
--       commun_prof_retour_effacer_mot (l'enseignant·e efface un mot).
--  Ce qu'il ne change pas : aucune table, aucune fonction ni aucune ligne
--  existantes. Le registre des tables (vue commun.registre) range la
--  nouvelle table de lui-même (schéma commun, d'après son commentaire).
--
--  Retour en arrière : 0013-retours-eleves-inverse.sql (avant l'inverse de
--  0008, à cause du lien vers les classes).
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.classes') is null or to_regprocedure('commun.verifier_enseignant(text)') is null
     or to_regprocedure('commun.nettoyer_texte(text, integer, integer)') is null or to_regprocedure('commun.essai_permis(text, text, integer)') is null then
    raise exception 'Le compte commun (0003, 0007 et 0008) manque : l''appliquer d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if to_regclass('commun.retours') is not null
     or exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace
                 and (p.proname like 'commun\_retour%' or p.proname like 'commun\_prof\_retour%')) then
    raise exception 'Les retours des élèves (0013) sont déjà là : arrêt, rien n''a été modifié.';
  end if;
  if not exists (select 1 from pg_catalog.pg_timezone_names where name = 'Indian/Mayotte') then
    raise exception 'Le fuseau Indian/Mayotte est inconnu de la base : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- 1. La table
-- -----------------------------------------------------------------------------
create table commun.retours (
  id             uuid primary key default gen_random_uuid(),
  ressource      text not null check (ressource ~ '^(sequence:)?[a-z0-9][a-z0-9-]{1,79}$'),
  partie         text not null default '' check (partie = '' or partie ~ '^[a-z0-9][a-z0-9._-]{0,79}$'),
  classe_id      uuid references commun.classes (id) on delete set null,
  semaine        date not null check (extract(isodow from semaine) = 1),
  plu            smallint check (plu between 1 and 5),
  difficulte     text check (difficulte in ('trop_facile', 'bien', 'trop_dur')),
  compris        text check (compris in ('oui', 'a_peu_pres', 'non')),
  fini           text check (fini in ('oui', 'presque', 'non')),
  remarques      text[] not null default '{}'::text[]
                 check (remarques <@ array['consignes', 'trop_de_texte', 'exemples', 'bug', 'telephone', 'encore']::text[]),
  mot            text check (char_length(mot) between 1 and 140),
  cle_empreinte  text unique check (cle_empreinte ~ '^[0-9a-f]{64}$'),
  lot_classe     date,
  lot_tous       date,
  check (plu is not null or difficulte is not null or compris is not null or fini is not null
         or cardinality(remarques) > 0 or mot is not null)
);
create index retours_ressource on commun.retours (ressource, partie, semaine);
create index retours_classe on commun.retours (classe_id, ressource, partie) where classe_id is not null;
create index retours_semaine on commun.retours (semaine);
create index retours_a_publier on commun.retours (ressource, partie) where lot_tous is null or lot_classe is null;
alter table commun.retours enable row level security;
revoke all on commun.retours from public, anon, authenticated;
comment on table commun.retours is
  'Commun. Les avis anonymes des élèves à la fin d''une ressource en ligne (T163) : ni compte, ni code, ni pseudo, ni adresse, ni heure ; la semaine seulement, et la classe commune si la page la connaît. Montrés à l''enseignant·e par paquets d''au moins 5, jamais pendant la semaine en cours. Effacés deux ans après leur semaine. Données d''élèves : oui (des avis anonymes, et un mot libre facultatif lu par l''enseignant·e de la classe seulement).';
comment on column commun.retours.id is 'L''identifiant du retour, tiré au hasard (sert seulement à effacer un mot).';
comment on column commun.retours.ressource is 'La ressource : l''identifiant de sa fiche (donnees/ressources/<id>.json), ou sequence:<id> pour la page d''une séquence.';
comment on column commun.retours.partie is 'La partie de la ressource (l''identifiant d''une feuille de TD en ligne, data-td), ou vide.';
comment on column commun.retours.classe_id is 'La classe commune dont la page connaissait le code (lien ?classe=ABCD), sinon vide. Jamais l''élève. Vidé si la classe est supprimée (son mot part alors au ménage suivant).';
comment on column commun.retours.semaine is 'Le lundi de la semaine du retour (heure de Mayotte) : aucune date plus fine n''est gardée.';
comment on column commun.retours.plu is '« Ça t''a plu ? » : de 1 à 5 étoiles, ou vide.';
comment on column commun.retours.difficulte is '« C''était… » : trop_facile, bien ou trop_dur, ou vide.';
comment on column commun.retours.compris is '« J''ai compris » : oui, a_peu_pres ou non, ou vide.';
comment on column commun.retours.fini is '« J''ai fini » : oui, presque ou non, ou vide.';
comment on column commun.retours.remarques is 'Les remarques choisies dans une liste fermée : consignes (pas claires), trop_de_texte, exemples (il en faudrait plus), bug (quelque chose ne marchait pas), telephone (pas pratique sur téléphone), encore (j''en veux d''autres comme ça).';
comment on column commun.retours.mot is 'Le mot libre facultatif (140 caractères au plus, ni adresse, ni lien, ni numéro) : gardé seulement si la classe est connue, lu seulement par l''enseignant·e de la classe, jamais affiché aux élèves ; effaçable par l''élève pendant la semaine et par l''enseignant·e.';
comment on column commun.retours.cle_empreinte is 'L''empreinte SHA-256 de la clé tirée au hasard par l''appareil pour cette ressource : elle permet de changer ou retirer son avis pendant la semaine. Effacée dès la semaine finie : le retour n''est alors plus rattaché à rien.';
comment on column commun.retours.lot_classe is 'Le paquet de la classe où ce retour est montré (le lundi de la dernière semaine du paquet) ; vide tant qu''il attend que sa classe ait au moins 5 retours non montrés pour cette ressource.';
comment on column commun.retours.lot_tous is 'Le paquet « tout le monde » où ce retour est montré (le lundi de la dernière semaine du paquet) ; vide tant qu''il attend au moins 5 retours non montrés pour cette ressource.';

-- -----------------------------------------------------------------------------
-- 2. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- Le lundi de la semaine en cours, heure de Mayotte.
create function commun.retour_semaine()
returns date language sql stable set search_path = '' as $$
  select date_trunc('week', now() at time zone 'Indian/Mayotte')::date
$$;

-- L'empreinte d'une clé d'appareil bien formée (22 à 64 caractères base64url), sinon null.
create function commun.retour_cle(p_cle text)
returns text language sql immutable set search_path = '' as $$
  select case when coalesce(p_cle, '') ~ '^[A-Za-z0-9_-]{22,64}$'
              then encode(sha256(convert_to('retour|' || p_cle, 'UTF8')), 'hex') end
$$;

-- Avant toute lecture : les clés des semaines finies sont effacées, les mots
-- sans classe (classe inconnue ou supprimée) aussi, les retours de plus de deux ans partent, puis les
-- retours des semaines finies sont rangés en paquets d'au moins 5 (par classe
-- et ressource, et par ressource pour « tout le monde »). Un paquet rangé ne
-- change plus. Renvoie le nombre de retours rangés.
create function commun.retours_publier()
returns integer language plpgsql volatile set search_path = '' as $$
declare s date := commun.retour_semaine(); n1 integer; n2 integer;
begin
  delete from commun.retours r where r.semaine < s - 728;
  update commun.retours r set cle_empreinte = null where r.cle_empreinte is not null and r.semaine < s;
  update commun.retours r set mot = null where r.mot is not null and r.classe_id is null;
  update commun.retours r set lot_classe = g.lot
    from (select x.classe_id, x.ressource, x.partie, max(x.semaine) as lot
            from commun.retours x
           where x.lot_classe is null and x.classe_id is not null and x.semaine < s
           group by 1, 2, 3 having count(*) >= 5) g
   where r.lot_classe is null and r.classe_id = g.classe_id and r.ressource = g.ressource and r.partie = g.partie and r.semaine < s;
  get diagnostics n1 = row_count;
  update commun.retours r set lot_tous = g.lot
    from (select x.ressource, x.partie, max(x.semaine) as lot
            from commun.retours x
           where x.lot_tous is null and x.semaine < s
           group by 1, 2 having count(*) >= 5) g
   where r.lot_tous is null and r.ressource = g.ressource and r.partie = g.partie and r.semaine < s;
  get diagnostics n2 = row_count;
  return n1 + n2;
end $$;

revoke all on function commun.retour_semaine(), commun.retour_cle(text), commun.retours_publier() from public, anon, authenticated;
comment on function commun.retour_semaine() is 'Commun, interne. Le lundi de la semaine en cours, heure de Mayotte : la seule date gardée avec un retour.';
comment on function commun.retour_cle(text) is 'Commun, interne. L''empreinte SHA-256 d''une clé d''appareil bien formée (22 à 64 caractères base64url), sinon null.';
comment on function commun.retours_publier() is 'Commun, interne. Efface les clés des semaines finies, les mots sans classe et les retours de plus de deux ans, puis range les retours des semaines finies en paquets d''au moins 5 (par classe et ressource, et par ressource pour tout le monde). Un paquet rangé ne change plus.';

-- -----------------------------------------------------------------------------
-- 3. Les fonctions d'entrée de l'élève : anon seul
-- -----------------------------------------------------------------------------

-- Donner son avis, ou le changer pendant la semaine (même clé d'appareil).
create function public.commun_retour_donner(p_cle text, p_ressource text, p_partie text default '',
  p_classe text default null, p_plu integer default null, p_difficulte text default null, p_compris text default null,
  p_fini text default null, p_remarques text[] default '{}', p_mot text default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  s date := commun.retour_semaine();
  v_cle text := commun.retour_cle(p_cle);
  v_ressource text := left(coalesce(p_ressource, ''), 90);
  v_partie text := left(coalesce(p_partie, ''), 90);
  v_classe uuid;
  v_classe_donnee boolean := coalesce(btrim(p_classe), '') <> '';
  v_remarques text[];
  v_mot text;
  v_mot_brut text := nullif(btrim(coalesce(p_mot, '')), '');
  ancien commun.retours;
  v_modifie boolean := false;
begin
  if v_cle is null then
    return jsonb_build_object('ok', false, 'message', 'La page n''a pas pu préparer ton avis. Recharge-la, puis réessaie.');
  end if;
  if v_ressource !~ '^(sequence:)?[a-z0-9][a-z0-9-]{1,79}$' or (v_partie <> '' and v_partie !~ '^[a-z0-9][a-z0-9._-]{0,79}$') then
    return jsonb_build_object('ok', false, 'message', 'Cette page n''est pas prévue pour les avis.');
  end if;
  if not commun.essai_permis('retours', 'creation', 300) then
    return jsonb_build_object('ok', false, 'plus_tard', true, 'message', 'Beaucoup d''avis depuis ce réseau en une heure : ton avis attend sur ton appareil.');
  end if;
  -- Les réponses : seulement des valeurs prévues ; le reste est ignoré.
  if p_plu is not null and p_plu not between 1 and 5 then p_plu := null; end if;
  if p_difficulte not in ('trop_facile', 'bien', 'trop_dur') then p_difficulte := null; end if;
  if p_compris not in ('oui', 'a_peu_pres', 'non') then p_compris := null; end if;
  if p_fini not in ('oui', 'presque', 'non') then p_fini := null; end if;
  select coalesce(array_agg(distinct x order by x), '{}'::text[]) into v_remarques
    from unnest(coalesce(p_remarques[1:12], '{}'::text[])) x
   where x = any(array['consignes', 'trop_de_texte', 'exemples', 'bug', 'telephone', 'encore']);
  -- La classe : seulement un code de classe commune qui existe (30 codes inconnus par heure et par réseau).
  if v_classe_donnee and upper(btrim(p_classe)) ~ '^[A-HJ-NP-Z]{4}$' and commun.essai_permis('retours', 'classe', 30) then
    select c.id into v_classe from commun.classes c where c.code = upper(btrim(p_classe));
    if v_classe is null then perform commun.noter_echec('retours', 'classe'); end if;
  end if;
  -- Le mot : seulement avec une classe ; ni adresse, ni lien, ni numéro.
  if v_mot_brut is not null then
    v_mot := commun.nettoyer_texte(v_mot_brut, 1, 140);
    if v_mot is null then
      return jsonb_build_object('ok', false, 'message', 'Ton mot fait 140 caractères au plus, sans caractère spécial.');
    end if;
    if v_mot ~* '@|https?:|www\.|\.(com|fr|net|org|yt|re|io)\M|[0-9]([ .-]?[0-9]){5,}' then
      return jsonb_build_object('ok', false, 'message', 'Ton mot ne doit contenir ni adresse, ni lien, ni numéro de téléphone.');
    end if;
    if v_classe is null then v_mot := null; end if;
  end if;
  if p_plu is null and p_difficulte is null and p_compris is null and p_fini is null and cardinality(v_remarques) = 0 and v_mot is null then
    return jsonb_build_object('ok', false, 'message', 'Choisis au moins une réponse.');
  end if;

  select * into ancien from commun.retours r where r.cle_empreinte = v_cle;
  if found then
    if ancien.ressource <> v_ressource or ancien.partie <> v_partie or ancien.semaine <> s then
      return jsonb_build_object('ok', false, 'fige', true, 'message', 'Ton avis est déjà gardé ; il ne se change plus.');
    end if;
    update commun.retours r set classe_id = v_classe, plu = p_plu, difficulte = p_difficulte, compris = p_compris,
           fini = p_fini, remarques = v_remarques, mot = v_mot
     where r.id = ancien.id;
    v_modifie := true;
  else
    if (select count(*) from commun.retours r where r.ressource = v_ressource and r.partie = v_partie and r.semaine = s) >= 1500
       or (select count(*) from commun.retours r where r.semaine = s) >= 20000
       or (select count(*) from commun.retours) >= 300000 then
      return jsonb_build_object('ok', false, 'plus_tard', true, 'message', 'Beaucoup d''avis en ce moment : ton avis attend sur ton appareil.');
    end if;
    insert into commun.retours (ressource, partie, classe_id, semaine, plu, difficulte, compris, fini, remarques, mot, cle_empreinte)
    values (v_ressource, v_partie, v_classe, s, p_plu, p_difficulte, p_compris, p_fini, v_remarques, v_mot, v_cle);
  end if;
  perform commun.noter_echec('retours', 'creation');
  return jsonb_build_object('ok', true, 'modifie', v_modifie, 'classe', v_classe is not null,
    'classe_inconnue', v_classe_donnee and v_classe is null, 'mot_garde', v_mot is not null,
    'jusqu_au', s + 6);
end $$;

-- Retirer son avis de la semaine (même clé d'appareil).
create function public.commun_retour_effacer(p_cle text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v_cle text := commun.retour_cle(p_cle); n integer;
begin
  if v_cle is null then return jsonb_build_object('ok', false, 'message', 'Rien à retirer depuis cet appareil.'); end if;
  delete from commun.retours r where r.cle_empreinte = v_cle and r.semaine = commun.retour_semaine();
  get diagnostics n = row_count;
  if n = 0 then
    return jsonb_build_object('ok', false, 'message', 'Ton avis ne se retire plus : la semaine est finie, et il n''est plus rattaché à ton appareil.');
  end if;
  return jsonb_build_object('ok', true, 'message', 'Ton avis est retiré.');
end $$;

-- -----------------------------------------------------------------------------
-- 4. Les fonctions d'entrée de l'enseignant·e : anon seul
-- -----------------------------------------------------------------------------

-- Les paquets publiés : ceux d'une de ses classes (p_classe), ou ceux de tout
-- le monde (p_classe vide, sans aucun mot). Par ressource et partie, puis par
-- paquet : le nombre de retours et la répartition de chaque réponse.
create function public.commun_prof_retours(p_code text, p_classe uuid default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; res jsonb;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if p_classe is not null and not commun.classe_du_prof(v.prof, p_classe) then
    return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.');
  end if;
  perform commun.retours_publier();
  with r as (
    select x.*, case when p_classe is null then x.lot_tous else x.lot_classe end as lot
      from commun.retours x
     where (p_classe is null and x.lot_tous is not null)
        or (p_classe is not null and x.classe_id = p_classe and x.lot_classe is not null)
  ), lots as (
    select r.ressource, r.partie, r.lot, count(*) as n,
      jsonb_build_object('1', count(*) filter (where r.plu = 1), '2', count(*) filter (where r.plu = 2),
        '3', count(*) filter (where r.plu = 3), '4', count(*) filter (where r.plu = 4), '5', count(*) filter (where r.plu = 5)) as plu,
      jsonb_build_object('trop_facile', count(*) filter (where r.difficulte = 'trop_facile'),
        'bien', count(*) filter (where r.difficulte = 'bien'), 'trop_dur', count(*) filter (where r.difficulte = 'trop_dur')) as difficulte,
      jsonb_build_object('oui', count(*) filter (where r.compris = 'oui'),
        'a_peu_pres', count(*) filter (where r.compris = 'a_peu_pres'), 'non', count(*) filter (where r.compris = 'non')) as compris,
      jsonb_build_object('oui', count(*) filter (where r.fini = 'oui'),
        'presque', count(*) filter (where r.fini = 'presque'), 'non', count(*) filter (where r.fini = 'non')) as fini,
      jsonb_build_object('consignes', count(*) filter (where 'consignes' = any(r.remarques)),
        'trop_de_texte', count(*) filter (where 'trop_de_texte' = any(r.remarques)),
        'exemples', count(*) filter (where 'exemples' = any(r.remarques)),
        'bug', count(*) filter (where 'bug' = any(r.remarques)),
        'telephone', count(*) filter (where 'telephone' = any(r.remarques)),
        'encore', count(*) filter (where 'encore' = any(r.remarques))) as remarques
      from r group by 1, 2, 3
  ), groupes as (
    select l.ressource, l.partie,
      jsonb_agg(jsonb_build_object('semaine', l.lot, 'n', l.n, 'plu', l.plu, 'difficulte', l.difficulte,
        'compris', l.compris, 'fini', l.fini, 'remarques', l.remarques) order by l.lot) as lots
      from lots l group by 1, 2
  )
  select coalesce(jsonb_agg(jsonb_build_object('ressource', g.ressource, 'partie', g.partie, 'lots', g.lots,
           'mots', case when p_classe is null then '[]'::jsonb else coalesce((
             select jsonb_agg(jsonb_build_object('id', r.id, 'mot', r.mot) order by md5(r.id::text))
               from r where r.ressource = g.ressource and r.partie = g.partie and r.mot is not null), '[]'::jsonb) end)
         order by g.ressource, g.partie), '[]'::jsonb)
    into res from groupes g;
  return jsonb_build_object('ok', true, 'portee', case when p_classe is null then 'tous' else 'classe' end,
    'semaine', commun.retour_semaine(), 'seuil', 5, 'ressources', res);
end $$;

-- Effacer un mot (une insulte, un nom) d'un retour de ses classes.
create function public.commun_prof_retour_effacer_mot(p_code text, p_retour uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n integer;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  update commun.retours r set mot = null
   where r.id = p_retour and r.mot is not null and r.lot_classe is not null
     and r.classe_id in (select c.id from commun.classes c where c.enseignant_id = v.prof);
  get diagnostics n = row_count;
  if n = 0 then return jsonb_build_object('ok', false, 'message', 'Ce mot n''est pas dans tes classes, ou il est déjà effacé.'); end if;
  return jsonb_build_object('ok', true, 'message', 'Le mot est effacé.');
end $$;

revoke all on function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text),
  public.commun_retour_effacer(text), public.commun_prof_retours(text, uuid), public.commun_prof_retour_effacer_mot(text, uuid)
  from public, anon, authenticated;
grant execute on function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text),
  public.commun_retour_effacer(text), public.commun_prof_retours(text, uuid), public.commun_prof_retour_effacer_mot(text, uuid)
  to anon;
comment on function public.commun_retour_donner(text, text, text, text, integer, text, text, text, text[], text) is
  'Compte commun, entrée élève, sans compte. Donne ou change (même clé d''appareil, pendant la semaine) un avis anonyme sur une ressource : étoiles, difficulté, compréhension, fini ou non, remarques d''une liste fermée, mot libre (avec une classe seulement). 300 envois par heure et par réseau.';
comment on function public.commun_retour_effacer(text) is
  'Compte commun, entrée élève, sans compte. Retire l''avis de la semaine donné depuis cet appareil (sa clé).';
comment on function public.commun_prof_retours(text, uuid) is
  'Compte commun, entrée enseignant·e. Les avis publiés, par paquets d''au moins 5, des semaines finies : d''une de ses classes (avec les mots), ou de tout le monde (sans aucun mot).';
comment on function public.commun_prof_retour_effacer_mot(text, uuid) is
  'Compte commun, entrée enseignant·e. Efface le mot libre d''un avis de ses classes.';

-- -----------------------------------------------------------------------------
-- 5. Contrôle
-- -----------------------------------------------------------------------------
do $$
begin
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'commun'::regnamespace
             and (has_function_privilege('anon', p.oid, 'execute') or has_function_privilege('authenticated', p.oid, 'execute'))) then
    raise exception 'Une fonction de commun est appelable par anon ou par authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind = 'r' and not c.relrowsecurity) then
    raise exception 'Une table de commun n''a pas la RLS : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_class c where c.relnamespace = 'commun'::regnamespace and c.relkind in ('r', 'v')
             and (has_table_privilege('anon', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain')
                  or has_table_privilege('authenticated', c.oid, 'select, insert, update, delete, truncate, references, trigger, maintain'))) then
    raise exception 'Une table de commun est ouverte à anon ou à authenticated : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_proc p where p.pronamespace = 'public'::regnamespace and p.proname like 'commun\_%'
             and (has_function_privilege('authenticated', p.oid, 'execute') or not has_function_privilege('anon', p.oid, 'execute')
                  or not p.prosecdef or p.proconfig is null)) then
    raise exception 'Une fonction commun_ n''a pas les bons droits : arrêt, rien n''a été modifié.';
  end if;
  if exists (select 1 from pg_catalog.pg_attribute a where a.attrelid = 'commun.retours'::regclass and a.attnum > 0
             and not a.attisdropped and col_description(a.attrelid, a.attnum) is null) then
    raise exception 'Une colonne de commun.retours n''a pas de commentaire : arrêt, rien n''a été modifié.';
  end if;
end $$;

commit;
