-- Alien Python – élèves : à coller dans Supabase > SQL Editor > Run
-- (tables et fonctions préfixées « alien_ » pour cohabiter avec d'autres applications dans le même projet)
-- Principe : les tables sont verrouillées (RLS sans aucune politique). Le site n'y accède
-- que par les fonctions ci-dessous, qui vérifient le code classe / code élève / code enseignant.

create extension if not exists pgcrypto with schema extensions;

create table if not exists alien_classes (
  code text primary key,
  name text not null,
  teacher_code text not null,            -- stocké haché (bcrypt)
  created_at timestamptz not null default now()
);
create table if not exists alien_students (
  id uuid primary key default gen_random_uuid(),
  class_code text not null references alien_classes(code) on delete cascade,
  name text not null,
  code text not null,                    -- code personnel à 4 chiffres, unique dans la classe
  created_at timestamptz not null default now(),
  unique (class_code, code)
);
create table if not exists alien_progress (
  student_id uuid not null references alien_students(id) on delete cascade,
  ex text not null,
  solved boolean not null default false,
  attempts int not null default 0,
  hints int not null default 0,
  peeked boolean not null default false, -- correction consultée
  updated_at timestamptz not null default now(),
  primary key (student_id, ex)
);
alter table alien_classes  enable row level security;
alter table alien_students enable row level security;
alter table alien_progress enable row level security;
revoke all on alien_classes, alien_students, alien_progress from anon, authenticated;

-- Création d'une classe (l'enseignant choisit son code secret) -> renvoie le code classe
create or replace function alien_create_class(p_name text, p_teacher text) returns text
language plpgsql security definer set search_path = public, extensions as $$
declare c text;
begin
  if length(trim(p_name)) < 2 or length(p_teacher) < 4 then
    raise exception 'Nom de classe ou code enseignant trop court (4 caractères minimum)';
  end if;
  loop
    c := upper(substr(md5(random()::text || clock_timestamp()::text), 1, 6));
    exit when not exists (select 1 from alien_classes where code = c);
  end loop;
  insert into alien_classes(code, name, teacher_code) values (c, left(trim(p_name), 60), crypt(p_teacher, gen_salt('bf')));
  return c;
end $$;

-- Un élève rejoint une classe avec son prénom -> reçoit son code personnel
create or replace function alien_join_class(p_class text, p_name text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare cc text := upper(trim(p_class)); sc text; nm text := left(trim(p_name), 30);
begin
  if not exists (select 1 from alien_classes where code = cc) then raise exception 'Code classe inconnu'; end if;
  if length(nm) < 1 then raise exception 'Prénom manquant'; end if;
  loop
    sc := lpad((floor(random() * 10000))::int::text, 4, '0');
    exit when not exists (select 1 from alien_students where class_code = cc and code = sc);
  end loop;
  insert into alien_students(class_code, name, code) values (cc, nm, sc);
  return json_build_object('code', sc, 'name', nm);
end $$;

-- Connexion d'un élève (reprise de sa progression)
create or replace function alien_student_login(p_class text, p_code text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare s alien_students;
begin
  select * into s from alien_students where class_code = upper(trim(p_class)) and code = trim(p_code);
  if not found then raise exception 'Code classe ou code personnel incorrect'; end if;
  return json_build_object('name', s.name, 'progress', coalesce((
    select json_agg(json_build_object('ex', ex, 'solved', solved, 'attempts', attempts, 'hints', hints, 'peeked', peeked))
    from alien_progress where student_id = s.id), '[]'::json));
end $$;

-- Enregistrement de la progression (tentative, aide, correction, réussite)
create or replace function alien_save_progress(p_class text, p_code text, p_ex text, p_solved boolean,
  p_attempt boolean, p_hints int, p_peeked boolean) returns void
language plpgsql security definer set search_path = public, extensions as $$
declare sid uuid;
begin
  select id into sid from alien_students where class_code = upper(trim(p_class)) and code = trim(p_code);
  if sid is null then raise exception 'Accès refusé'; end if;
  insert into alien_progress(student_id, ex, solved, attempts, hints, peeked)
  values (sid, left(p_ex, 4), p_solved, case when p_attempt then 1 else 0 end, greatest(p_hints, 0), p_peeked)
  on conflict (student_id, ex) do update set
    solved = alien_progress.solved or excluded.solved,
    attempts = alien_progress.attempts + excluded.attempts,
    hints = greatest(alien_progress.hints, excluded.hints),
    peeked = alien_progress.peeked or excluded.peeked,
    updated_at = now();
end $$;

-- Avancement de la classe vu par un élève (prénoms + nombre d'exercices réussis, par ordre alphabétique)
create or replace function alien_class_view(p_class text, p_code text) returns json
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform 1 from alien_students where class_code = upper(trim(p_class)) and code = trim(p_code);
  if not found then raise exception 'Accès refusé'; end if;
  return coalesce((select json_agg(json_build_object('name', s.name,
    'solved', (select count(*) from alien_progress p where p.student_id = s.id and p.solved)) order by s.name)
    from alien_students s where s.class_code = upper(trim(p_class))), '[]'::json);
end $$;

-- Tableau de bord enseignant
create or replace function alien_teacher_overview(p_class text, p_teacher text) returns json
language plpgsql security definer set search_path = public, extensions as $$
declare c alien_classes;
begin
  select * into c from alien_classes where code = upper(trim(p_class));
  if not found or c.teacher_code <> crypt(p_teacher, c.teacher_code) then
    raise exception 'Code classe ou code enseignant incorrect';
  end if;
  return json_build_object('name', c.name, 'students', coalesce((
    select json_agg(json_build_object('name', s.name, 'code', s.code,
      'last', (select max(updated_at) from alien_progress p where p.student_id = s.id),
      'ex', coalesce((select json_agg(json_build_object('ex', p.ex, 'solved', p.solved, 'attempts', p.attempts,
        'hints', p.hints, 'peeked', p.peeked)) from alien_progress p where p.student_id = s.id), '[]'::json))
      order by s.name) from alien_students s where s.class_code = c.code), '[]'::json));
end $$;

grant execute on function alien_create_class(text, text), alien_join_class(text, text), alien_student_login(text, text),
  alien_save_progress(text, text, text, boolean, boolean, int, boolean), alien_class_view(text, text),
  alien_teacher_overview(text, text) to anon;
