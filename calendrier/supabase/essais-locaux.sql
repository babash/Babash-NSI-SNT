-- Essais locaux de vacances_0001 (base Postgres locale, jamais la base réelle).
-- Mode d'emploi : LISEZMOI.md, « L'essai local ».
\set ON_ERROR_STOP 1
\pset pager off
create temp table t(k text primary key, v json);
grant all on t to anon;

set role anon;
-- 1. espace et calendrier
insert into t select 'prof', public.cv_prof_creer_espace('M. Essai');
select (v->>'ok') as ok_espace, v->>'code_affiche' ~ '^[A-Z]+-[A-Z]+-[A-Z]+-[0-9]{4}$' as forme_code_prof from t where k='prof';
select (public.cv_prof_ouvrir('mauvais code')->>'ok') as ouvrir_mauvais;
select (public.cv_prof_ouvrir(lower((select v->>'code_affiche' from t where k='prof')))->>'ok') as ouvrir_minuscules;
insert into t select 'cal', public.cv_prof_creer_calendrier((select v->>'code_affiche' from t where k='prof'), '1NSI vacances',
  (now() at time zone 'Indian/Mayotte')::date, (now() at time zone 'Indian/Mayotte')::date + 13,
  array['nsi1-boucles', 'nsi1-conditions'], 'alternance', 'jauge');
select v->>'ok' ok, v->>'cases' cases, v->>'code' ~ '^[A-HJ-NP-Z]{4}$' forme_code_cal from t where k='cal';
select public.cv_prof_creer_calendrier((select v->>'code_affiche' from t where k='prof'), 'trop long',
  current_date, current_date + 30, array['a'])->>'message' as refus_31_jours;
-- 2. élève
select public.cv_calendrier_par_code(lower((select v->>'code' from t where k='cal'))) as par_lien;
insert into t select 'el', public.cv_inscription((select v->>'code' from t where k='cal'), '  Kenza  ');
select v->>'pseudo' pseudo, v->>'code_affiche' ~ '^[A-Z]+-[A-Z]+-[0-9]{3}$' forme from t where k='el';
select public.cv_inscription((select v->>'code' from t where k='cal'), 'kenza')->>'message' as doublon;
select public.cv_inscription((select v->>'code' from t where k='cal'), 'K')->>'message' as trop_court;
select public.cv_inscription((select v->>'code' from t where k='cal'), 'Ab' || chr(8203) || 'c')->>'message' as invisible;
select public.cv_connexion('pas un code')->>'message' as mauvais_code;
insert into t select 'cx', public.cv_connexion(replace(lower((select v->>'code_affiche' from t where k='el')), '-', ' '));
select v->>'ok' connexion_tolerante, json_array_length(v->'calendriers') nb_cal from t where k='cx';
-- anon ne lit aucune table
do $$ begin perform 1 from vacances.eleves; raise exception 'ANON LIT LA TABLE'; exception when insufficient_privilege then raise notice 'anon : lecture refusée (attendu)'; end $$;
reset role;

-- 3. on fait comme si le calendrier avait commencé il y a 4 jours (jour 5)
update vacances.cases set jour = jour - 4;
update vacances.calendriers set debut = debut - 4, fin = fin - 4;

set role anon;
select x->>'numero' n, x->>'jour' jour, x->>'theme' theme, x->>'rang' rang, x->>'etat' etat
from t, json_array_elements((public.cv_calendrier((t.v->>'jeton')::uuid, (select (v->>'id')::uuid from t where k='cal'))->'etat'->'cases')) x
where t.k='cx' and (x->>'numero')::int <= 7;
-- 4. résultats : case 3 (ouverte), case 1 (corrigée : rattrapage), case 7 (à venir : refus)
select public.cv_resultat((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal'), 3, 2, true, 2, 6, 1, 240)->'etat'->'score' as score_apres_case3;
select public.cv_resultat((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal'), 1, 1, true, 1, 4, 0, 120)->'etat'->'score' as score_apres_rattrapage;
select public.cv_resultat((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal'), 7, 1, true, 1, 4, 0, 120)->>'message' as futur;
select public.cv_resultat((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal'), 3, 2, true, 3, 6, 1, 240)->>'message' as etoiles_trop;
-- un moins bon résultat ne remplace pas le meilleur
select public.cv_resultat((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal'), 3, 2, false, 0, 9, 3, 500)->'etat'->'score' as score_apres_moins_bon;
select public.cv_classe((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal'))->'classe' as jauge;
-- 5. le tableau de l'enseignant·e
select json_array_length(v->'eleves') eleves, v->'eleves'->0->>'pseudo' pseudo, json_array_length(v->'eleves'->0->'resultats') resultats
from (select public.cv_prof_tableau((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal')) v) z;
-- 6. modifier après le début : la fin raccourcit, un thème s'ajoute ; les cases ouvertes restent
select public.cv_prof_modifier_calendrier((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal'),
  '1NSI vacances', (now() at time zone 'Indian/Mayotte')::date - 4, (now() at time zone 'Indian/Mayotte')::date + 3,
  array['nsi1-boucles', 'nsi1-conditions', 'nsi1-fonctions'], 'alternance', 'jauge') as modif;
select public.cv_prof_modifier_calendrier((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal'),
  '1NSI vacances', (now() at time zone 'Indian/Mayotte')::date - 3, (now() at time zone 'Indian/Mayotte')::date + 3,
  array['nsi1-boucles'], 'alternance', 'jauge')->>'message' as debut_bouge;
reset role;
select numero, jour - (now() at time zone 'Indian/Mayotte')::date as decalage, theme, rang from vacances.cases order by numero;
select count(*) as resultats_gardes from vacances.resultats;

-- 7. mode chaque_theme : 3 thèmes par jour, 3 cases à faire montrées au plus
set role anon;
insert into t select 'cal2', public.cv_prof_creer_calendrier((select v->>'code_affiche' from t where k='prof'), 'SNT tous',
  (now() at time zone 'Indian/Mayotte')::date, (now() at time zone 'Indian/Mayotte')::date + 5,
  array['snt-internet', 'snt-web', 'snt-photo'], 'chaque_theme', 'aucun');
select public.cv_rejoindre((select (v->>'jeton')::uuid from t where k='cx'), (select v->>'code' from t where k='cal2'))->>'ok' as rejoint;
reset role;
update vacances.cases set jour = jour - 1 where calendrier_id = (select (v->>'id')::uuid from t where k='cal2');
set role anon;
select string_agg(x->>'etat', ' ' order by (x->>'numero')::int) etats
from json_array_elements((public.cv_calendrier((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal2'))->'etat'->'cases')) x;
select public.cv_calendrier((select (v->>'jeton')::uuid from t where k='cx'), (select (v->>'id')::uuid from t where k='cal2'))->'etat'->'classe' as classe_aucun;
-- 8. nouveau code d'élève : l'ancien jeton ne marche plus, les résultats restent
select public.cv_prof_nouveau_code_eleve((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal'),
  (select (z.v->'eleves'->0->>'id')::uuid from (select public.cv_prof_tableau((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal')) v) z))->>'ok' as nouveau_code;
select public.cv_reprise((select (v->>'jeton')::uuid from t where k='cx'))->>'ok' as ancien_jeton;
-- 9. supprimer : confirmation exigée
select public.cv_prof_supprimer_calendrier((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal'), 'non')->>'ok' as sans_confirmation;
select public.cv_prof_supprimer_calendrier((select v->>'code_affiche' from t where k='prof'), (select (v->>'id')::uuid from t where k='cal'), (select v->>'code' from t where k='cal'))->>'ok' as supprime;
reset role;
select (select count(*) from vacances.calendriers) calendriers, (select count(*) from vacances.resultats) resultats, (select count(*) from vacances.eleves) comptes;
