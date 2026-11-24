begin;
-- =============================================================================
--  Base unique : l'espace commun des enseignant·e·s et les classes communes
--  (version 2, après les décisions du 20/11, 14:41 et 14:45)
--  Projet Supabase cukahpyqkljiddmimpyi (« Babash - applications »)
--  Nom de migration : base_unique_0008_enseignants_communs
--  Fichier proposé : supabase/0008-enseignants-communs.sql du dépôt du site (T101)
-- =============================================================================
--  PROPOSITION : rien n'est appliqué. À montrer à l'enseignant (règle M4).
--  Suppose 0007 appliqué.
--
--  Pourquoi :
--   - un·e enseignant·e a un seul code pour toutes les applications, ouvert à
--     tout·e collègue (aucune liste, aucun mot de passe, aucune adresse) ;
--   - ses classes sont communes : une page par classe réunit les élèves, leur
--     avatar, leurs hauts faits, leur XP et leurs crédits, et renvoie vers le
--     tableau de bord de chaque application de la classe ;
--   - il ou elle attribue de l'XP, avec un motif court, inscrit au journal ;
--   - un·e élève voit les avatars et les hauts faits de ses camarades de
--     classe, et seulement d'elles et d'eux ; jamais leur XP ni leurs crédits.
--
--  Ce que ce fichier crée :
--   - 5 tables dans commun (RLS, aucun droit) : enseignants,
--     enseignants_liens, classes, inscriptions, classes_liens ;
--   - 2 colonnes de connecteurs dans commun.applications, et le lien du
--     journal de l'XP vers l'enseignant·e qui attribue ;
--   - 8 fonctions internes ; 18 fonctions d'entrée enseignant·e
--     (commun_prof_…) et 3 fonctions d'entrée élève, appelables par anon seul.
--  Ce qu'il ne change pas : les espaces enseignant·e·s des applications et
--  leurs codes, qui restent valables. Chaque application se branche ensuite.
--
--  Retour en arrière : 0008-enseignants-communs-inverse.sql.
-- =============================================================================

do $$
begin
  if current_user <> 'postgres' then
    raise exception 'À lancer en postgres, pas en % : arrêt, rien n''a été modifié.', current_user;
  end if;
  if to_regclass('commun.comptes') is null or to_regclass('commun.xp_journal') is null then
    raise exception 'Le compte commun (0007, version 2) manque : l''appliquer d''abord. Arrêt, rien n''a été modifié.';
  end if;
  if to_regclass('commun.enseignants') is not null or to_regclass('commun.classes') is not null then
    raise exception 'Les tables des enseignant·e·s ou des classes existent déjà : arrêt, rien n''a été modifié.';
  end if;
end $$;

-- -----------------------------------------------------------------------------
-- 1. Les tables
-- -----------------------------------------------------------------------------
create table commun.enseignants (
  id              uuid primary key default gen_random_uuid(),
  code_empreinte  text not null unique check (code_empreinte ~ '^[0-9a-f]{64}$'),
  nom             text not null check (char_length(nom) between 2 and 40),
  etablissement   text check (char_length(etablissement) between 2 and 80),
  cree_le         timestamptz not null default now(),
  vu_le           timestamptz not null default now()
);
alter table commun.enseignants enable row level security;
revoke all on commun.enseignants from public, anon, authenticated;
comment on table commun.enseignants is
  'Commun. Un espace par enseignant·e, pour toutes les applications : le nom affiché aux élèves, l''établissement (facultatif) et l''empreinte de son code (3 mots et 4 chiffres, montré une seule fois, gardé nulle part en clair). Ouvert à tout·e collègue. Supprimé seulement par l''enseignant·e. Données d''élèves : non.';
comment on column commun.enseignants.id is 'L''identifiant de l''espace, tiré au hasard.';
comment on column commun.enseignants.code_empreinte is 'L''empreinte SHA-256 de la forme canonique du code : on retrouve l''espace à partir du code, jamais le code à partir de l''empreinte.';
comment on column commun.enseignants.nom is 'Le nom affiché aux élèves (« Mme Ali », « M. B. »), choisi par l''enseignant·e.';
comment on column commun.enseignants.etablissement is 'L''établissement, facultatif.';
comment on column commun.enseignants.cree_le is 'La date de création de l''espace.';
comment on column commun.enseignants.vu_le is 'La date de la dernière ouverture de l''espace.';

create table commun.enseignants_liens (
  application        text not null references commun.applications (id),
  enseignant_app_id  uuid not null,
  enseignant_id      uuid not null references commun.enseignants (id) on delete cascade,
  depuis             timestamptz not null default now(),
  primary key (application, enseignant_app_id)
);
create index enseignants_liens_enseignant on commun.enseignants_liens (enseignant_id);
alter table commun.enseignants_liens enable row level security;
revoke all on commun.enseignants_liens from public, anon, authenticated;
comment on table commun.enseignants_liens is
  'Commun. Les espaces enseignant·e·s des applications reliés à chaque espace commun : le code commun ouvre l''espace de chaque application, et l''ancien code de l''application reste valable. Données d''élèves : non.';
comment on column commun.enseignants_liens.application is 'L''application.';
comment on column commun.enseignants_liens.enseignant_app_id is 'L''identifiant de l''espace dans cette application (grand_oral.enseignants.id, gb_profs.id…).';
comment on column commun.enseignants_liens.enseignant_id is 'L''espace commun relié.';
comment on column commun.enseignants_liens.depuis is 'La date du lien.';

create table commun.classes (
  id             uuid primary key default gen_random_uuid(),
  enseignant_id  uuid not null references commun.enseignants (id) on delete cascade,
  nom            text not null check (char_length(nom) between 2 and 40),
  code           text not null unique check (code ~ '^[A-HJ-NP-Z]{4}$'),
  ouverte        boolean not null default true,
  applications   text[] not null default '{}'::text[] check (cardinality(applications) <= 20),
  cree_le        timestamptz not null default now()
);
create index classes_enseignant on commun.classes (enseignant_id);
alter table commun.classes enable row level security;
revoke all on commun.classes from public, anon, authenticated;
comment on table commun.classes is
  'Commun. Les classes communes de chaque enseignant·e : nom, code de classe public (4 lettres, dans le lien et le QR code), inscriptions ouvertes ou fermées, applications de la classe. Aucun plafond du nombre d''élèves. Supprimée seulement par l''enseignant·e ; les comptes des élèves restent. Données d''élèves : non.';
comment on column commun.classes.id is 'L''identifiant de la classe, tiré au hasard.';
comment on column commun.classes.enseignant_id is 'L''espace de l''enseignant·e de la classe.';
comment on column commun.classes.nom is 'Le nom de la classe (« TNSI 2 »).';
comment on column commun.classes.code is 'Le code de classe, public : 4 lettres sans I ni O (spécification des codes, § 1.1). Lien : …/eleve/?classe=CODE.';
comment on column commun.classes.ouverte is 'Vrai si l''on peut encore rejoindre la classe par son lien.';
comment on column commun.classes.applications is 'Les applications de la classe (identifiants de commun.applications) : la page de l''élève montre leurs hauts faits à gagner.';
comment on column commun.classes.cree_le is 'La date de création de la classe.';

create table commun.inscriptions (
  classe_id  uuid not null references commun.classes (id) on delete cascade,
  compte_id  uuid not null references commun.comptes (id) on delete cascade,
  depuis     timestamptz not null default now(),
  primary key (classe_id, compte_id)
);
create index inscriptions_compte on commun.inscriptions (compte_id);
alter table commun.inscriptions enable row level security;
revoke all on commun.inscriptions from public, anon, authenticated;
comment on table commun.inscriptions is
  'Commun. Les élèves de chaque classe commune (un·e élève peut être dans plusieurs classes) : c''est ce qui borne ce que voit un·e élève de ses camarades, et ce que voit l''enseignant·e. Effacée avec la classe ou le compte. Données d''élèves : oui (l''appartenance à une classe).';
comment on column commun.inscriptions.classe_id is 'La classe.';
comment on column commun.inscriptions.compte_id is 'Le compte de l''élève.';
comment on column commun.inscriptions.depuis is 'La date d''arrivée dans la classe.';

create table commun.classes_liens (
  classe_id    uuid not null references commun.classes (id) on delete cascade,
  application  text not null references commun.applications (id),
  reference    text not null check (reference ~ '^[A-Za-z0-9_-]{1,64}$'),
  primary key (classe_id, application, reference)
);
alter table commun.classes_liens enable row level security;
revoke all on commun.classes_liens from public, anon, authenticated;
comment on table commun.classes_liens is
  'Commun. Les classes ou salles des applications rattachées à une classe commune : la page de la classe renvoie vers le tableau de bord de chacune (adresse_prof de l''application, puis #classe=référence). Données d''élèves : non.';
comment on column commun.classes_liens.classe_id is 'La classe commune.';
comment on column commun.classes_liens.application is 'L''application.';
comment on column commun.classes_liens.reference is 'La classe dans l''application : son code (ABC123 pour Gombessa, ABCD pour une salle de Lagon Arena) ou son identifiant.';

alter table commun.applications
  add column fn_prof_par_code regprocedure,
  add column fn_prof_eleves   regprocedure;
comment on column commun.applications.fn_prof_par_code is 'Connecteur facultatif (p_code text) returns table(enseignant_app_id uuid, nom text) : l''espace enseignant·e de l''application qui a ce code (tel que tapé), s''il existe.';
comment on column commun.applications.fn_prof_eleves is 'Connecteur facultatif (p_enseignant_app uuid) returns table(eleve_id uuid, pseudo text, classe text) : les élèves des classes de cet espace, dans l''application.';

alter table commun.xp_journal
  add constraint xp_journal_enseignant_fkey foreign key (enseignant_id) references commun.enseignants (id) on delete set null;

-- -----------------------------------------------------------------------------
-- 2. Les fonctions internes : aucun droit pour personne
-- -----------------------------------------------------------------------------

-- Un code d'enseignant·e neuf : 3 mots et 4 chiffres de la liste du site.
create function commun.nouveau_code_enseignant(out code text, out code_affiche text)
language plpgsql volatile set search_path = '' as $$
declare b bytea; v integer; w text[]; d text;
begin
  loop
    b := extensions.gen_random_bytes(5);
    v := get_byte(b, 3) * 256 + get_byte(b, 4);
    continue when v >= 60000;
    select array_agg(m.mot order by k.i) into w
      from generate_series(0, 2) k(i) join commun.mots m on m.application = 'commun' and m.rang = get_byte(b, k.i) % 64;
    d := lpad((v % 10000)::text, 4, '0');
    code := w[1] || w[2] || w[3] || d;
    code_affiche := w[1] || '-' || w[2] || '-' || w[3] || '-' || d;
    exit when not exists (select 1 from commun.enseignants e
                           where e.code_empreinte = encode(sha256(convert_to(nouveau_code_enseignant.code, 'UTF8')), 'hex'));
  end loop;
end $$;

create function commun.empreinte_enseignant(p_code text)
returns text language sql immutable set search_path = '' as $$
  select encode(sha256(convert_to(commun.normaliser_code(p_code), 'UTF8')), 'hex')
$$;

-- Un code de classe neuf : 4 lettres sans I ni O, tirées sans biais.
create function commun.nouveau_code_classe()
returns text language plpgsql volatile set search_path = '' as $$
declare lettres constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZ'; b bytea; c text; i integer;
begin
  loop
    c := '';
    while char_length(c) < 4 loop
      b := extensions.gen_random_bytes(1);
      i := get_byte(b, 0);
      continue when i >= 240;
      c := c || substr(lettres, 1 + i % 24, 1);
    end loop;
    exit when not exists (select 1 from commun.classes x where x.code = c);
  end loop;
  return c;
end $$;

-- L'espace commun qu'ouvre un code : le code commun, sinon le code d'un
-- espace d'application (par son connecteur), qui est alors relié (et l'espace
-- commun créé, au nom de l'espace de l'application). Null si inconnu.
create function commun.enseignant_par_code(p_code text)
returns uuid language plpgsql volatile set search_path = '' as $$
declare v uuid; a record; v_app uuid; v_nom text;
begin
  select e.id into v from commun.enseignants e where e.code_empreinte = commun.empreinte_enseignant(p_code);
  if v is not null then return v; end if;
  for a in select x.id, x.fn_prof_par_code from commun.applications x
            where x.active and x.fn_prof_par_code is not null order by x.id loop
    begin
      execute format('select t.enseignant_app_id, t.nom from %s($1) t limit 1', a.fn_prof_par_code::oid::regproc)
        into v_app, v_nom using left(coalesce(p_code, ''), 80);
    exception when others then
      raise warning 'commun.enseignant_par_code : le connecteur de % a échoué (%)', a.id, sqlerrm;
      v_app := null;
    end;
    if v_app is not null then
      select l.enseignant_id into v from commun.enseignants_liens l where l.application = a.id and l.enseignant_app_id = v_app;
      if v is null then
        -- Un espace commun sans code commun (empreinte au hasard) : l'ancien
        -- code de l'application l'ouvre ; « Nouveau code » en donne un.
        insert into commun.enseignants (code_empreinte, nom)
        values (encode(extensions.gen_random_bytes(32), 'hex'), coalesce(commun.nettoyer_texte(v_nom, 2, 40), 'Enseignant·e'))
        returning id into v;
        insert into commun.enseignants_liens (application, enseignant_app_id, enseignant_id) values (a.id, v_app, v);
      end if;
      return v;
    end if;
  end loop;
  return null;
end $$;

-- Vérifie un code d'enseignant·e avec le compteur d'essais (10 échecs par
-- heure et par réseau). Renvoie l'espace, ou null et un message.
create function commun.verifier_enseignant(p_code text, out prof uuid, out message text)
language plpgsql volatile set search_path = '' as $$
begin
  if not commun.essai_permis('commun', 'enseignant', 10) then
    message := 'Trop d''essais depuis ce réseau. Attends la fin de l''heure.';
    return;
  end if;
  prof := commun.enseignant_par_code(p_code);
  if prof is null then
    perform commun.noter_echec('commun', 'enseignant');
    perform pg_sleep(0.3);
    message := 'Ce code d''enseignant·e n''existe pas.';
    return;
  end if;
  update commun.enseignants e set vu_le = now() where e.id = prof;
end $$;

-- Les élèves des espaces d'application reliés à un espace commun, avec leur
-- compte commun s'il existe (applications rattachées).
create function commun.eleves_de(p_prof uuid)
returns table (application text, eleve_app_id uuid, pseudo text, classe text, compte_id uuid)
language plpgsql volatile set search_path = '' as $$
declare l record;
begin
  for l in select li.application, li.enseignant_app_id, a.fn_prof_eleves
             from commun.enseignants_liens li join commun.applications a on a.id = li.application
            where li.enseignant_id = p_prof and a.active and a.fn_prof_eleves is not null loop
    begin
      return query execute format(
        'select $1::text, t.eleve_id, t.pseudo, t.classe, (select k.compte_id from commun.liens k where k.application = $1 and k.eleve_app_id = t.eleve_id)
           from %s($2) t', l.fn_prof_eleves::oid::regproc)
        using l.application, l.enseignant_app_id;
    exception when others then
      raise warning 'commun.eleves_de : le connecteur de % a échoué (%)', l.application, sqlerrm;
    end;
  end loop;
end $$;

-- Vrai si la classe est à cet·te enseignant·e.
create function commun.classe_du_prof(p_prof uuid, p_classe uuid)
returns boolean language sql stable set search_path = '' as $$
  select exists (select 1 from commun.classes c where c.id = p_classe and c.enseignant_id = p_prof)
$$;

-- Vrai si l'élève est dans une classe commune de cet·te enseignant·e, ou
-- dans une classe d'un de ses espaces d'application reliés.
create function commun.eleve_visible(p_prof uuid, p_compte uuid)
returns boolean language plpgsql volatile set search_path = '' as $$
begin
  if p_compte is null then return false; end if;
  if exists (select 1 from commun.inscriptions i join commun.classes c on c.id = i.classe_id
              where i.compte_id = p_compte and c.enseignant_id = p_prof) then
    return true;
  end if;
  return exists (select 1 from commun.eleves_de(p_prof) x where x.compte_id = p_compte);
end $$;

revoke all on function commun.nouveau_code_enseignant(), commun.empreinte_enseignant(text), commun.nouveau_code_classe(),
  commun.enseignant_par_code(text), commun.verifier_enseignant(text), commun.eleves_de(uuid),
  commun.classe_du_prof(uuid, uuid), commun.eleve_visible(uuid, uuid) from public, anon, authenticated;
comment on function commun.nouveau_code_enseignant() is 'Commun, interne. Un code d''enseignant·e neuf : 3 mots de la liste du site et 4 chiffres, tirés sans biais, dont l''empreinte est libre.';
comment on function commun.empreinte_enseignant(text) is 'Commun, interne. L''empreinte SHA-256 de la forme canonique d''un code d''enseignant·e.';
comment on function commun.nouveau_code_classe() is 'Commun, interne. Un code de classe neuf : 4 lettres sans I ni O, tirées sans biais, libre.';
comment on function commun.enseignant_par_code(text) is 'Commun, interne. L''espace commun qu''ouvre un code : le code commun, ou celui d''un espace d''application relié (créé et relié à la première ouverture).';
comment on function commun.verifier_enseignant(text) is 'Commun, interne. Vérifie un code d''enseignant·e avec le compteur d''essais (10 échecs par heure et par réseau).';
comment on function commun.eleves_de(uuid) is 'Commun, interne. Les élèves des classes des espaces d''application reliés à un espace commun, avec leur compte commun s''il existe.';
comment on function commun.classe_du_prof(uuid, uuid) is 'Commun, interne. Vrai si la classe commune appartient à cet·te enseignant·e.';
comment on function commun.eleve_visible(uuid, uuid) is 'Commun, interne. Vrai si l''élève est dans une classe commune de cet·te enseignant·e ou dans une classe d''un de ses espaces d''application reliés.';

-- -----------------------------------------------------------------------------
-- 3. Les fonctions d'entrée de l'enseignant·e : anon seul
-- -----------------------------------------------------------------------------

create function public.commun_prof_creer_espace(p_nom text, p_etablissement text default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v_nom text := commun.nettoyer_texte(p_nom, 2, 40);
        v_etab text := commun.nettoyer_texte(p_etablissement, 2, 80);
        n record;
begin
  if not commun.essai_permis('commun', 'creation', 60) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''espaces créés depuis ce réseau en une heure. Attends un peu.');
  end if;
  if v_nom is null then
    return jsonb_build_object('ok', false, 'message', 'Donne un nom affiché de 2 à 40 caractères (« Mme Ali », « M. B. »).');
  end if;
  if v_etab is null and nullif(btrim(coalesce(p_etablissement, '')), '') is not null then
    return jsonb_build_object('ok', false, 'message', 'L''établissement a de 2 à 80 caractères.');
  end if;
  perform commun.noter_echec('commun', 'creation');
  select * into n from commun.nouveau_code_enseignant();
  insert into commun.enseignants (code_empreinte, nom, etablissement)
  values (commun.empreinte_enseignant(n.code), v_nom, v_etab);
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche,
    'message', 'Voici ton code. Il n''est montré qu''une fois : note-le ou imprime-le.');
end $$;

-- Ouvrir son espace : son nom, ses classes, ses applications reliées.
create function public.commun_prof_ouvrir(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; e commun.enseignants;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  select * into e from commun.enseignants x where x.id = v.prof;
  return jsonb_build_object('ok', true, 'nom', e.nom, 'etablissement', e.etablissement,
    'classes', coalesce((select jsonb_agg(jsonb_build_object('id', c.id, 'nom', c.nom, 'code', c.code, 'ouverte', c.ouverte,
                                 'applications', to_jsonb(c.applications),
                                 'eleves', (select count(*) from commun.inscriptions i where i.classe_id = c.id)) order by c.nom)
                           from commun.classes c where c.enseignant_id = e.id), '[]'::jsonb),
    'applications', coalesce((select jsonb_agg(jsonb_build_object('id', a.id, 'nom', a.nom, 'adresse_prof', a.adresse_prof) order by a.nom)
                                from commun.applications a
                               where exists (select 1 from commun.enseignants_liens l where l.enseignant_id = e.id and l.application = a.id)), '[]'::jsonb),
    'alarme', commun.echecs_heure('commun') > 200);
end $$;

-- Relier à son espace commun l'espace d'une application (son ancien code),
-- ou réunir deux espaces communs. Rien n'est perdu.
create function public.commun_prof_lier_code(p_code text, p_autre_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; autre uuid;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  autre := commun.enseignant_par_code(p_autre_code);
  if autre is null then
    perform commun.noter_echec('commun', 'enseignant');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Cet autre code n''existe pas.');
  end if;
  if autre <> v.prof then
    update commun.enseignants_liens set enseignant_id = v.prof where enseignant_id = autre;
    update commun.classes set enseignant_id = v.prof where enseignant_id = autre;
    update commun.xp_journal set enseignant_id = v.prof where enseignant_id = autre;
    delete from commun.enseignants where id = autre;
  end if;
  return jsonb_build_object('ok', true, 'message', 'Ton code commun ouvre aussi cet espace. L''autre code reste valable dans son application.');
end $$;

create function public.commun_prof_creer_classe(p_code text, p_nom text, p_applications text[] default '{}')
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n text := commun.nettoyer_texte(p_nom, 2, 40); c commun.classes;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if n is null then return jsonb_build_object('ok', false, 'message', 'Donne un nom de classe de 2 à 40 caractères.'); end if;
  insert into commun.classes (enseignant_id, nom, code, applications)
  values (v.prof, n, commun.nouveau_code_classe(),
          coalesce((select array_agg(a.id order by a.id) from commun.applications a where a.id = any(p_applications[1:20])), '{}'::text[]))
  returning * into c;
  return jsonb_build_object('ok', true, 'id', c.id, 'code', c.code,
    'lien', 'https://babash.github.io/Babash-NSI-SNT/eleve/?classe=' || c.code);
end $$;

create function public.commun_prof_modifier_classe(p_code text, p_classe uuid, p_nom text, p_ouverte boolean, p_applications text[])
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n text := commun.nettoyer_texte(p_nom, 2, 40);
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  if n is null then return jsonb_build_object('ok', false, 'message', 'Donne un nom de classe de 2 à 40 caractères.'); end if;
  update commun.classes c set nom = n, ouverte = coalesce(p_ouverte, c.ouverte),
         applications = coalesce((select array_agg(a.id order by a.id) from commun.applications a where a.id = any(p_applications[1:20])), '{}'::text[])
   where c.id = p_classe;
  return jsonb_build_object('ok', true);
end $$;

create function public.commun_prof_supprimer_classe(p_code text, p_classe uuid, p_confirmation text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  if coalesce(upper(btrim(p_confirmation)), '') <> 'SUPPRIMER' then
    return jsonb_build_object('ok', false, 'message', 'Écris SUPPRIMER pour confirmer.');
  end if;
  delete from commun.classes c where c.id = p_classe;
  return jsonb_build_object('ok', true, 'message', 'La classe est supprimée. Les comptes des élèves restent, avec tout ce qu''ils ont gagné.');
end $$;

-- Relier à une classe commune la classe d'une application (ou retirer ce
-- lien avec p_retirer).
create function public.commun_prof_lier_classe(p_code text, p_classe uuid, p_application text, p_reference text, p_retirer boolean default false)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  if not exists (select 1 from commun.applications a where a.id = left(p_application, 30))
     or coalesce(p_reference, '') !~ '^[A-Za-z0-9_-]{1,64}$' then
    return jsonb_build_object('ok', false, 'message', 'Application ou classe de l''application inconnue.');
  end if;
  if p_retirer then
    delete from commun.classes_liens l where l.classe_id = p_classe and l.application = p_application and l.reference = p_reference;
  else
    insert into commun.classes_liens (classe_id, application, reference) values (p_classe, p_application, p_reference) on conflict do nothing;
  end if;
  return jsonb_build_object('ok', true);
end $$;

-- La page d'une classe : les élèves (pseudo, avatar, codes nés sur le site,
-- hauts faits, XP, crédits, dernière visite) et les tableaux de bord des
-- applications de la classe. Un seul objet JSON (règle P7). Rangé par pseudo.
create function public.commun_prof_classe(p_code text, p_classe uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; c commun.classes;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  select * into c from commun.classes x where x.id = p_classe and x.enseignant_id = v.prof;
  if c.id is null then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  return jsonb_build_object('ok', true,
    'classe', jsonb_build_object('id', c.id, 'nom', c.nom, 'code', c.code, 'ouverte', c.ouverte, 'applications', to_jsonb(c.applications),
      'lien', 'https://babash.github.io/Babash-NSI-SNT/eleve/?classe=' || c.code,
      'tableaux', coalesce((select jsonb_agg(jsonb_build_object('application', a.id, 'nom', a.nom, 'reference', l.reference,
                                     'adresse', case when a.adresse_prof is not null then a.adresse_prof || '#classe=' || l.reference end)
                                     order by a.nom, l.reference)
                              from commun.classes_liens l join commun.applications a on a.id = l.application where l.classe_id = c.id), '[]'::jsonb)),
    'eleves', coalesce((select jsonb_agg(jsonb_build_object(
                 'compte', k.id, 'pseudo', k.pseudo, 'avatar', k.avatar, 'xp', k.xp, 'credits', k.credits, 'vu_le', k.vu_le,
                 'codes', coalesce((select jsonb_agg(x.code_affiche order by x.principal desc) from commun.codes x where x.compte_id = k.id), '[]'::jsonb),
                 'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait, 'gagne_le', g.gagne_le)
                                                           order by g.gagne_le) from commun.hauts_faits_gagnes g where g.compte_id = k.id), '[]'::jsonb))
               order by lower(k.pseudo))
             from commun.inscriptions i join commun.comptes k on k.id = i.compte_id where i.classe_id = c.id), '[]'::jsonb));
end $$;

-- Les élèves des espaces d'application reliés (applications rattachées), et
-- leurs hauts faits de cette application. Aucun total, aucun classement.
create function public.commun_prof_eleves(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  return jsonb_build_object('ok', true, 'eleves', coalesce((
    select jsonb_agg(jsonb_build_object(
             'application', x.application, 'eleve_app_id', x.eleve_app_id, 'pseudo', x.pseudo, 'classe', x.classe, 'compte', x.compte_id,
             'avatar', (select k.avatar from commun.comptes k where k.id = x.compte_id),
             'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait, 'gagne_le', g.gagne_le)
                                                       order by g.gagne_le)
                                        from commun.hauts_faits_gagnes g where g.compte_id = x.compte_id), '[]'::jsonb))
           order by x.application, x.classe, lower(x.pseudo))
      from commun.eleves_de(v.prof) x), '[]'::jsonb));
end $$;

-- Attribuer de l'XP (donc des crédits) à un·e élève de ses classes, avec un
-- motif court, inscrit au journal (1 à 50 par attribution).
create function public.commun_prof_attribuer_xp(p_code text, p_compte uuid, p_xp integer, p_motif text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; m text := commun.nettoyer_texte(p_motif, 3, 80); g integer;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if p_xp is null or p_xp not between 1 and 50 then
    return jsonb_build_object('ok', false, 'message', 'Une attribution va de 1 à 50.');
  end if;
  if m is null then return jsonb_build_object('ok', false, 'message', 'Donne un motif de 3 à 80 caractères.'); end if;
  if not commun.eleve_visible(v.prof, p_compte) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes.');
  end if;
  g := commun.crediter(p_compte, 'commun', 'attribution', null, p_xp, 'enseignant', m, v.prof);
  return jsonb_build_object('ok', true, 'xp', g);
end $$;

-- Le journal de l'XP des élèves d'une classe (500 dernières lignes) : gains,
-- attributions (avec leur motif et leur auteur·e) et achats.
create function public.commun_prof_journal_xp(p_code text, p_classe uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  return jsonb_build_object('ok', true, 'journal', coalesce((
    select jsonb_agg(jsonb_build_object('le', j.cree_le, 'compte', j.compte_id, 'pseudo', k.pseudo, 'application', j.application,
                                        'evenement', j.evenement, 'xp', j.xp, 'motif', j.motif,
                                        'par', (select e.nom from commun.enseignants e where e.id = j.enseignant_id)) order by j.cree_le desc)
      from (select x.* from commun.xp_journal x join commun.inscriptions i on i.compte_id = x.compte_id and i.classe_id = p_classe
             order by x.cree_le desc limit 500) j
      join commun.comptes k on k.id = j.compte_id), '[]'::jsonb));
end $$;

-- Accorder un haut fait de genre « enseignant » (l'entraide, par exemple).
create function public.commun_prof_accorder(p_code text, p_compte uuid, p_application text, p_haut_fait text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.eleve_visible(v.prof, p_compte) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes, ou n''a pas encore de compte commun.');
  end if;
  return jsonb_build_object('ok', true, 'nouveautes', commun.accorder(p_compte, left(p_application, 30), array[left(p_haut_fait, 40)], 'enseignant'));
end $$;

create function public.commun_prof_retirer_eleve(p_code text, p_classe uuid, p_compte uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not commun.classe_du_prof(v.prof, p_classe) then return jsonb_build_object('ok', false, 'message', 'Cette classe n''est pas à toi.'); end if;
  delete from commun.inscriptions i where i.classe_id = p_classe and i.compte_id = p_compte;
  return jsonb_build_object('ok', true, 'message', 'L''élève n''est plus dans la classe ; son compte reste.');
end $$;

create function public.commun_prof_renommer_eleve(p_code text, p_compte uuid, p_pseudo text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; p text := commun.nettoyer_pseudo(p_pseudo);
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if p is null then return jsonb_build_object('ok', false, 'message', 'Un prénom ou un pseudo de 2 à 24 caractères.'); end if;
  if not exists (select 1 from commun.inscriptions i join commun.classes c on c.id = i.classe_id
                  where i.compte_id = p_compte and c.enseignant_id = v.prof) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes communes.');
  end if;
  update commun.comptes k set pseudo = p, pseudo_provisoire = false where k.id = p_compte;
  return jsonb_build_object('ok', true, 'pseudo', p);
end $$;

-- Un nouveau code pour un·e élève dont le code est né sur le site (code
-- perdu ou divulgué) : l'ancien cesse de marcher, ses sessions sont fermées.
-- Pour un code d'une application rattachée, c'est l'application qui le donne.
create function public.commun_prof_nouveau_code_eleve(p_code text, p_compte uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if not exists (select 1 from commun.inscriptions i join commun.classes c on c.id = i.classe_id
                  where i.compte_id = p_compte and c.enseignant_id = v.prof) then
    return jsonb_build_object('ok', false, 'message', 'Cet·te élève n''est dans aucune de tes classes communes.');
  end if;
  if not exists (select 1 from commun.codes x where x.compte_id = p_compte and x.application = 'commun') then
    return jsonb_build_object('ok', false, 'message', 'Son code vient d''une application : donne-lui un nouveau code depuis cette application.');
  end if;
  delete from commun.codes x where x.compte_id = p_compte and x.application = 'commun';
  select * into n from commun.nouveau_code('commun');
  insert into commun.codes (code, code_affiche, compte_id, application, principal)
  values (n.code, n.code_affiche, p_compte, 'commun', not exists (select 1 from commun.codes y where y.compte_id = p_compte and y.principal));
  delete from commun.sessions s where s.compte_id = p_compte;
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche);
end $$;

create function public.commun_prof_nouveau_code(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record; n record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  select * into n from commun.nouveau_code_enseignant();
  update commun.enseignants e set code_empreinte = commun.empreinte_enseignant(n.code) where e.id = v.prof;
  return jsonb_build_object('ok', true, 'code_affiche', n.code_affiche,
    'message', 'Voici ton nouveau code commun ; l''ancien ne marche plus. Les codes de tes applications restent valables.');
end $$;

create function public.commun_prof_debloquer_reseau(p_code text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  return jsonb_build_object('ok', true, 'effaces', commun.debloquer_reseau('commun'));
end $$;

create function public.commun_prof_supprimer_espace(p_code text, p_confirmation text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v record;
begin
  select * into v from commun.verifier_enseignant(p_code);
  if v.prof is null then return jsonb_build_object('ok', false, 'message', v.message); end if;
  if coalesce(upper(btrim(p_confirmation)), '') <> 'SUPPRIMER' then
    return jsonb_build_object('ok', false, 'message', 'Écris SUPPRIMER pour confirmer.');
  end if;
  delete from commun.enseignants e where e.id = v.prof;
  return jsonb_build_object('ok', true, 'message', 'Ton espace commun et tes classes communes sont supprimés. Les comptes des élèves restent, ainsi que tes espaces dans chaque application.');
end $$;

-- -----------------------------------------------------------------------------
-- 4. Les fonctions d'entrée de l'élève pour les classes : anon seul
-- -----------------------------------------------------------------------------

-- La classe derrière un lien : son nom et l'enseignant·e, sans aucun élève.
create function public.commun_classe_par_code(p_code_classe text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare c record;
begin
  if not commun.essai_permis('commun', 'classe', 30) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  select x.nom, x.ouverte, e.nom as enseignant into c
    from commun.classes x join commun.enseignants e on e.id = x.enseignant_id
   where x.code = commun.normaliser_code(left(coalesce(p_code_classe, ''), 20));
  if c.nom is null then
    perform commun.noter_echec('commun', 'classe');
    perform pg_sleep(0.3);
    return jsonb_build_object('ok', false, 'message', 'Ce code de classe n''existe pas.');
  end if;
  return jsonb_build_object('ok', true, 'nom', c.nom, 'enseignant', c.enseignant, 'ouverte', c.ouverte);
end $$;

-- Rejoindre une classe avec son compte (après commun_creer ou commun_entrer).
create function public.commun_rejoindre(p_jeton uuid, p_code_classe text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton); c commun.classes; p text;
begin
  if v is null then return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.'); end if;
  if not commun.essai_permis('commun', 'classe', 30) then
    return jsonb_build_object('ok', false, 'message', 'Trop d''essais depuis ce réseau. Attends un peu.');
  end if;
  select * into c from commun.classes x where x.code = commun.normaliser_code(left(coalesce(p_code_classe, ''), 20));
  if c.id is null then
    perform commun.noter_echec('commun', 'classe');
    return jsonb_build_object('ok', false, 'message', 'Ce code de classe n''existe pas.');
  end if;
  if exists (select 1 from commun.inscriptions i where i.classe_id = c.id and i.compte_id = v) then
    return jsonb_build_object('ok', true, 'message', 'Tu es déjà dans cette classe.', 'classe', c.nom);
  end if;
  if not c.ouverte then
    return jsonb_build_object('ok', false, 'message', 'Les inscriptions de cette classe sont fermées. Demande à ton enseignant·e.');
  end if;
  select k.pseudo into p from commun.comptes k where k.id = v;
  if exists (select 1 from commun.inscriptions i join commun.comptes k on k.id = i.compte_id
              where i.classe_id = c.id and lower(k.pseudo) = lower(p)) then
    return jsonb_build_object('ok', false, 'message', 'Ce pseudo est déjà pris dans la classe. Si c''est toi, entre avec ton code ; sinon, change de pseudo.');
  end if;
  insert into commun.inscriptions (classe_id, compte_id) values (c.id, v);
  return jsonb_build_object('ok', true, 'message', 'Bienvenue dans la classe.', 'classe', c.nom);
end $$;

-- Ce que l'élève voit de ses classes : pour chacune, son nom, ses
-- applications, et ses camarades (pseudo, avatar, hauts faits), rangé·e·s par
-- pseudo. Jamais l'XP, les crédits, les codes ni l'identifiant d'un compte.
create function public.commun_ma_classe(p_jeton uuid)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare v uuid := commun.compte_par_jeton(p_jeton);
begin
  if v is null then return jsonb_build_object('ok', false, 'message', 'Ta session a expiré : entre de nouveau ton code.'); end if;
  return jsonb_build_object('ok', true, 'classes', coalesce((
    select jsonb_agg(jsonb_build_object('nom', c.nom, 'enseignant', e.nom, 'applications', to_jsonb(c.applications),
             'camarades', (select jsonb_agg(jsonb_build_object('pseudo', k.pseudo, 'avatar', k.avatar, 'moi', k.id = v,
                                     'hauts_faits', coalesce((select jsonb_agg(jsonb_build_object('application', g.application, 'id', g.haut_fait)
                                                                               order by g.gagne_le)
                                                                from commun.hauts_faits_gagnes g where g.compte_id = k.id), '[]'::jsonb))
                                   order by lower(k.pseudo))
                             from commun.inscriptions j join commun.comptes k on k.id = j.compte_id where j.classe_id = c.id))
           order by c.nom)
      from commun.inscriptions i join commun.classes c on c.id = i.classe_id join commun.enseignants e on e.id = c.enseignant_id
     where i.compte_id = v), '[]'::jsonb));
end $$;

revoke all on function public.commun_prof_creer_espace(text, text), public.commun_prof_ouvrir(text),
  public.commun_prof_lier_code(text, text), public.commun_prof_creer_classe(text, text, text[]),
  public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]), public.commun_prof_supprimer_classe(text, uuid, text),
  public.commun_prof_lier_classe(text, uuid, text, text, boolean), public.commun_prof_classe(text, uuid),
  public.commun_prof_eleves(text), public.commun_prof_attribuer_xp(text, uuid, integer, text),
  public.commun_prof_journal_xp(text, uuid), public.commun_prof_accorder(text, uuid, text, text),
  public.commun_prof_retirer_eleve(text, uuid, uuid), public.commun_prof_renommer_eleve(text, uuid, text),
  public.commun_prof_nouveau_code_eleve(text, uuid), public.commun_prof_nouveau_code(text),
  public.commun_prof_debloquer_reseau(text), public.commun_prof_supprimer_espace(text, text),
  public.commun_classe_par_code(text), public.commun_rejoindre(uuid, text), public.commun_ma_classe(uuid)
  from public, anon, authenticated;
grant execute on function public.commun_prof_creer_espace(text, text), public.commun_prof_ouvrir(text),
  public.commun_prof_lier_code(text, text), public.commun_prof_creer_classe(text, text, text[]),
  public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]), public.commun_prof_supprimer_classe(text, uuid, text),
  public.commun_prof_lier_classe(text, uuid, text, text, boolean), public.commun_prof_classe(text, uuid),
  public.commun_prof_eleves(text), public.commun_prof_attribuer_xp(text, uuid, integer, text),
  public.commun_prof_journal_xp(text, uuid), public.commun_prof_accorder(text, uuid, text, text),
  public.commun_prof_retirer_eleve(text, uuid, uuid), public.commun_prof_renommer_eleve(text, uuid, text),
  public.commun_prof_nouveau_code_eleve(text, uuid), public.commun_prof_nouveau_code(text),
  public.commun_prof_debloquer_reseau(text), public.commun_prof_supprimer_espace(text, text),
  public.commun_classe_par_code(text), public.commun_rejoindre(uuid, text), public.commun_ma_classe(uuid)
  to anon;

comment on function public.commun_prof_creer_espace(text, text) is 'Compte commun, entrée enseignant·e. Crée un espace commun et renvoie son code (3 mots, 4 chiffres), montré une seule fois. Ouvert à tout·e collègue ; 60 créations par heure et par réseau.';
comment on function public.commun_prof_ouvrir(text) is 'Compte commun, entrée enseignant·e. Ouvre l''espace avec le code commun ou le code d''un espace d''application : nom, classes communes, applications reliées. 10 échecs par heure et par réseau.';
comment on function public.commun_prof_lier_code(text, text) is 'Compte commun, entrée enseignant·e. Relie à l''espace commun l''espace d''une application (son code), ou réunit deux espaces communs.';
comment on function public.commun_prof_creer_classe(text, text, text[]) is 'Compte commun, entrée enseignant·e. Crée une classe commune et renvoie son code et son lien.';
comment on function public.commun_prof_modifier_classe(text, uuid, text, boolean, text[]) is 'Compte commun, entrée enseignant·e. Renomme une classe, ouvre ou ferme ses inscriptions, change ses applications.';
comment on function public.commun_prof_supprimer_classe(text, uuid, text) is 'Compte commun, entrée enseignant·e. Supprime une classe commune (confirmation : SUPPRIMER) ; les comptes des élèves restent.';
comment on function public.commun_prof_lier_classe(text, uuid, text, text, boolean) is 'Compte commun, entrée enseignant·e. Relie à une classe commune la classe d''une application (ou retire ce lien), pour le renvoi vers son tableau de bord.';
comment on function public.commun_prof_classe(text, uuid) is 'Compte commun, entrée enseignant·e. La page d''une classe : élèves (pseudo, avatar, codes, hauts faits, XP, crédits) et tableaux de bord des applications, en un objet JSON, rangés par pseudo.';
comment on function public.commun_prof_eleves(text) is 'Compte commun, entrée enseignant·e. Les élèves des espaces d''application reliés et leurs hauts faits, en un objet JSON ; aucun total, aucun classement.';
comment on function public.commun_prof_attribuer_xp(text, uuid, integer, text) is 'Compte commun, entrée enseignant·e. Attribue de 1 à 50 XP (et autant de crédits) à un·e élève de ses classes, avec un motif court, inscrit au journal.';
comment on function public.commun_prof_journal_xp(text, uuid) is 'Compte commun, entrée enseignant·e. Le journal de l''XP des élèves d''une classe (500 dernières lignes), avec les motifs et les auteur·e·s des attributions.';
comment on function public.commun_prof_accorder(text, uuid, text, text) is 'Compte commun, entrée enseignant·e. Accorde un haut fait de genre enseignant à un·e élève de ses classes.';
comment on function public.commun_prof_retirer_eleve(text, uuid, uuid) is 'Compte commun, entrée enseignant·e. Retire un·e élève d''une classe commune ; son compte reste.';
comment on function public.commun_prof_renommer_eleve(text, uuid, text) is 'Compte commun, entrée enseignant·e. Renomme le compte commun d''un·e élève de ses classes communes.';
comment on function public.commun_prof_nouveau_code_eleve(text, uuid) is 'Compte commun, entrée enseignant·e. Donne un nouveau code (né sur le site) à un·e élève de ses classes communes ; l''ancien cesse de marcher.';
comment on function public.commun_prof_nouveau_code(text) is 'Compte commun, entrée enseignant·e. Remplace le code commun (il faut donner l''ancien) ; les codes des applications restent valables.';
comment on function public.commun_prof_debloquer_reseau(text) is 'Compte commun, entrée enseignant·e. Remet à zéro le compteur d''essais du réseau de la salle, pour le compte commun.';
comment on function public.commun_prof_supprimer_espace(text, text) is 'Compte commun, entrée enseignant·e. Supprime l''espace commun et ses classes communes (confirmation : SUPPRIMER) ; les comptes des élèves et les espaces des applications restent.';
comment on function public.commun_classe_par_code(text) is 'Compte commun, entrée élève. La classe derrière un lien : son nom, l''enseignant·e, inscriptions ouvertes ou non ; aucun élève. 30 échecs par heure et par réseau.';
comment on function public.commun_rejoindre(uuid, text) is 'Compte commun, entrée élève. Rejoint une classe commune avec son compte ; refuse un pseudo déjà pris dans la classe.';
comment on function public.commun_ma_classe(uuid) is 'Compte commun, entrée élève. Les camarades de ses classes seulement : pseudo, avatar et hauts faits ; jamais l''XP, les crédits ni les codes.';

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
end $$;

commit;
