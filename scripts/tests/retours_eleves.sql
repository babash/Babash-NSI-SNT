-- Les 60 essais SQL de 0013 (T163), sur une base LOCALE (jamais la base réelle) : la base du 25/11 reconstruite
-- (socle, 0007, 0008), puis 0013, puis : psql -d <base> -f scripts/tests/retours_eleves.sql. Données inventées.
-- Essais fonctionnels de 0013 sur la base locale (données inventées). Lancé par essais.sh.
\set ON_ERROR_STOP 1
\pset format unaligned
\pset tuples_only on
select set_config('request.headers', '{"cf-connecting-ip":"10.1.1.1"}', false) \g /dev/null
create temp table res (n serial, libelle text, obtenu text, attendu text);
grant all on res to anon; grant all on sequence res_n_seq to anon;
create function pg_temp.ok(l text, o text, a text) returns void language sql as $$ insert into res (libelle, obtenu, attendu) values (l, o, a) $$;
grant execute on function pg_temp.ok(text, text, text) to anon;

-- 1. L'API ne voit pas la table
set role anon;
do $$ begin perform 1 from commun.retours; raise exception 'lu !'; exception when insufficient_privilege then insert into res (libelle, obtenu, attendu) values ('anon ne lit pas commun.retours', 'refusé', 'refusé'); end $$;
reset role;

-- 2. Un espace enseignant·e et une classe (par les fonctions, en anon)
set role anon;
select public.commun_prof_creer_espace('Mme Essai', null)->>'code_affiche' as prof \gset
select (public.commun_prof_creer_classe(:'prof', 'TNSI essai', '{}'))->>'id' as classe_id, (public.commun_prof_creer_classe(:'prof', 'TNSI bis', '{}'))->>'id' as classe2 \gset
reset role;
select code as classe_code from commun.classes where id = :'classe_id' \gset
select public.commun_prof_creer_espace('M. Autre', null)->>'code_affiche' as prof2 \gset

set role anon;
-- 3. Des avis : 6 avec la classe, dont des mots
select pg_temp.ok('avis 1 (classe, mot)', (r->>'ok') || '/' || (r->>'classe') || '/' || (r->>'mot_garde'), 'true/true/true')
  from (select public.commun_retour_donner('cle-eleve-numero-0001-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 4, 'bien', 'oui', 'presque', array['exemples','bug','inconnu'], 'Les arbres c''est cool') r) x;
reset role;
select pg_temp.ok('remarque inconnue ignorée', array_to_string(remarques, ','), 'bug,exemples') from commun.retours where partie = 'tle-td-bac-abr-1' limit 1;
set role anon;
select pg_temp.ok('avis ' || i, public.commun_retour_donner('cle-eleve-numero-000' || i || '-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', lower(:'classe_code'), 2 + i % 4, 'trop_dur', 'a_peu_pres', 'non', '{}', case when i = 3 then 'Trop long pour une heure' end)->>'ok', 'true')
  from generate_series(2, 6) i;
-- 4. Changer son avis (même clé) : pas de nouvelle ligne
select pg_temp.ok('changer son avis', (public.commun_retour_donner('cle-eleve-numero-0002-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 5, 'bien', 'oui', 'oui', '{}', null))->>'modifie', 'true');
-- 5. La même clé sur une autre ressource : refusé
select pg_temp.ok('même clé, autre ressource', (public.commun_retour_donner('cle-eleve-numero-0002-aaaa', 'td-bac-arbres', '', null, 3, null, null, null, '{}', null))->>'fige', 'true');
-- 6. Sans classe : le mot n'est pas gardé
select pg_temp.ok('sans classe : mot non gardé', (r->>'ok') || '/' || (r->>'mot_garde'), 'true/false')
  from (select public.commun_retour_donner('cle-sans-classe-0001-bbbb', 'td-bac-abr', 'tle-td-bac-abr-1', null, 3, null, null, null, '{}', 'Un mot sans classe') r) x;
-- 7. Classe inconnue : gardé sans classe, et dit
select pg_temp.ok('classe inconnue', (r->>'ok') || '/' || (r->>'classe_inconnue'), 'true/true')
  from (select public.commun_retour_donner('cle-classe-faus-0001-bbbb', 'td-bac-abr', 'tle-td-bac-abr-1', 'ZZZZ', 3, null, null, null, '{}', null) r) x;
-- 8. Mots refusés
select pg_temp.ok('mot avec numéro', (public.commun_retour_donner('cle-eleve-numero-0007-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 3, null, null, null, '{}', 'appelle 0639 12 34 56'))->>'ok', 'false');
select pg_temp.ok('mot avec adresse', (public.commun_retour_donner('cle-eleve-numero-0007-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 3, null, null, null, '{}', 'ecris moi a x@y.fr'))->>'ok', 'false');
select pg_temp.ok('mot avec lien', (public.commun_retour_donner('cle-eleve-numero-0007-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 3, null, null, null, '{}', 'va sur tiktok.com'))->>'ok', 'false');
select pg_temp.ok('mot trop long', (public.commun_retour_donner('cle-eleve-numero-0007-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 3, null, null, null, '{}', repeat('a', 141)))->>'ok', 'false');
select pg_temp.ok('mot invisible refusé', (public.commun_retour_donner('cle-eleve-numero-0007-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 3, null, null, null, '{}', 'abc' || chr(8203) || 'def'))->>'ok', 'false');
select pg_temp.ok('2 x 3 = 6 accepté (pas un numéro)', (public.commun_retour_donner('cle-eleve-numero-0008-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', null, null, null, null, '{}', 'la question 2 et la 3 sont dures'))->>'ok', 'true');
-- 9. Entrées refusées
select pg_temp.ok('rien choisi', (public.commun_retour_donner('cle-eleve-numero-0009-aaaa', 'td-bac-abr', '', null, null, 'nimporte', null, null, '{}', null))->>'ok', 'false');
select pg_temp.ok('ressource mal formée', (public.commun_retour_donner('cle-eleve-numero-0009-aaaa', '../etc', '', null, 3, null, null, null, '{}', null))->>'ok', 'false');
select pg_temp.ok('clé trop courte', (public.commun_retour_donner('court', 'td-bac-abr', '', null, 3, null, null, null, '{}', null))->>'ok', 'false');
select pg_temp.ok('étoiles hors de 1 à 5 ignorées', (public.commun_retour_donner('cle-eleve-numero-0009-aaaa', 'td-bac-abr', '', null, 9, null, null, null, '{}', null))->>'ok', 'false');
select pg_temp.ok('séquence acceptée', (public.commun_retour_donner('cle-sequence-0001-cccccccc', 'sequence:tle-piles-files', '', null, 4, null, null, null, '{}', null))->>'ok', 'true');
-- 10. Retirer son avis
select pg_temp.ok('retirer (élève 8)', (public.commun_retour_effacer('cle-eleve-numero-0008-aaaa'))->>'ok', 'true');
select pg_temp.ok('retirer deux fois', (public.commun_retour_effacer('cle-eleve-numero-0008-aaaa'))->>'ok', 'false');
-- 11. L'enseignant·e ne voit rien de la semaine en cours
select pg_temp.ok('semaine en cours : rien', jsonb_array_length(public.commun_prof_retours(:'prof', :'classe_id'::uuid)->'ressources')::text, '0');
select pg_temp.ok('autre enseignant·e : refusé', public.commun_prof_retours(:'prof2', :'classe_id'::uuid)->>'message', 'Cette classe n''est pas à toi.');
select pg_temp.ok('mauvais code : refusé', public.commun_prof_retours('FAUX-FAUX-FAUX-0000', null)->>'ok', 'false');
reset role;

-- 12. Une semaine passe (on recule les dates des lignes inventées)
update commun.retours set semaine = semaine - 7, lot_classe = lot_classe - 7, lot_tous = lot_tous - 7;
set role anon;
select public.commun_prof_retours(:'prof', :'classe_id'::uuid) as vue \gset
select pg_temp.ok('classe : un paquet de 6', (:'vue'::jsonb #>> '{ressources,0,lots,0,n}'), '6');
select pg_temp.ok('classe : 2 mots', jsonb_array_length(:'vue'::jsonb #> '{ressources,0,mots}')::text, '2');
select pg_temp.ok('classe : répartition « trop dur »', (:'vue'::jsonb #>> '{ressources,0,lots,0,difficulte,trop_dur}'), '4');
select pg_temp.ok('classe : séquence absente (sans classe)', jsonb_array_length(:'vue'::jsonb -> 'ressources')::text, '1');
select public.commun_prof_retours(:'prof', null) as tous \gset
select pg_temp.ok('tous : 8 retours de la feuille (6 + sans classe + classe inconnue)', (select e #>> '{lots,0,n}' from jsonb_array_elements(:'tous'::jsonb -> 'ressources') e where e->>'partie' = 'tle-td-bac-abr-1'), '8');
select pg_temp.ok('tous : aucun mot', (select string_agg(jsonb_array_length(e->'mots')::text, ',') from jsonb_array_elements(:'tous'::jsonb -> 'ressources') e), '0');
select pg_temp.ok('tous : la séquence (1 avis) attend', (select count(*)::text from jsonb_array_elements(:'tous'::jsonb -> 'ressources') e where e->>'ressource' like 'sequence:%'), '0');
select pg_temp.ok('après la semaine, la clé n''est plus reconnue', (public.commun_retour_donner('cle-eleve-numero-0003-aaaa', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 1, null, null, null, '{}', null))->>'modifie', 'false');
reset role;
select pg_temp.ok('clés effacées après la semaine', count(*)::text, '0') from commun.retours where cle_empreinte is not null and semaine < commun.retour_semaine();
select pg_temp.ok('mot sans classe effacé', count(*)::text, '0') from commun.retours where classe_id is null and mot is not null;
select pg_temp.ok('aucune colonne d''heure', count(*)::text, '0') from pg_attribute where attrelid = 'commun.retours'::regclass and atttypid in ('timestamptz'::regtype, 'timestamp'::regtype, 'inet'::regtype);

-- 13. Trois avis la semaine suivante : ils attendent ; puis deux de plus : un nouveau paquet de 5
set role anon;
select pg_temp.ok('nouvel avis ' || i, public.commun_retour_donner('cle-semaine-deux-000' || i || '-dddd', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 1, 'trop_facile', null, null, '{}', null)->>'ok', 'true') from generate_series(1, 3) i;
reset role;
update commun.retours set semaine = semaine - 7, lot_classe = lot_classe - 7, lot_tous = lot_tous - 7;
set role anon;
select pg_temp.ok('3 avis de plus : toujours un seul paquet de 6', (select string_agg(l->>'n', ',') from jsonb_array_elements(public.commun_prof_retours(:'prof', :'classe_id'::uuid) #> '{ressources,0,lots}') l), '6');
select pg_temp.ok('nouvel avis ' || i, public.commun_retour_donner('cle-semaine-deux-000' || i || '-dddd', 'td-bac-abr', 'tle-td-bac-abr-1', :'classe_code', 5, 'trop_facile', null, null, '{}', null)->>'ok', 'true') from generate_series(4, 5) i;
reset role;
update commun.retours set semaine = semaine - 7, lot_classe = lot_classe - 7, lot_tous = lot_tous - 7;
set role anon;
select public.commun_prof_retours(:'prof', :'classe_id'::uuid) as vue2 \gset
select pg_temp.ok('deuxième paquet : 6 (l''avis redonné au n° 36, puis 3 + 2)', (:'vue2'::jsonb #>> '{ressources,0,lots,1,n}'), '6');
select pg_temp.ok('premier paquet inchangé (hors date)', ((:'vue2'::jsonb #> '{ressources,0,lots,0}') - 'semaine')::text, ((:'vue'::jsonb #> '{ressources,0,lots,0}') - 'semaine')::text);
select pg_temp.ok('deux paquets, deux semaines', (select string_agg(l->>'semaine', ',') from jsonb_array_elements(:'vue2'::jsonb #> '{ressources,0,lots}') l), (date_trunc('week', now() at time zone 'Indian/Mayotte')::date - 21)::text || ',' || (date_trunc('week', now() at time zone 'Indian/Mayotte')::date - 7)::text);
-- 14. L'enseignant·e efface un mot
select (:'vue2'::jsonb #>> '{ressources,0,mots,0,id}') as mot_id \gset
select pg_temp.ok('autre enseignant·e n''efface pas le mot', public.commun_prof_retour_effacer_mot(:'prof2', :'mot_id'::uuid)->>'ok', 'false');
select pg_temp.ok('effacer un mot', public.commun_prof_retour_effacer_mot(:'prof', :'mot_id'::uuid)->>'ok', 'true');
select pg_temp.ok('plus qu''un mot', jsonb_array_length(public.commun_prof_retours(:'prof', :'classe_id'::uuid) #> '{ressources,0,mots}')::text, '1');
-- 15. Plafond par réseau : 300 envois par heure
select set_config('request.headers', '{"cf-connecting-ip":"10.9.9.9"}', false) \g /dev/null
select pg_temp.ok('300 envois du même réseau', count(*) filter (where (public.commun_retour_donner('cle-plafond-' || lpad(i::text, 6, '0') || '-eeeeeeee', 'td-bac-arbres', '', null, 3, null, null, null, '{}', null))->>'ok' = 'true')::text, '300') from generate_series(1, 300) i;
select pg_temp.ok('le 301e attend', (public.commun_retour_donner('cle-plafond-000301-eeeeeeee', 'td-bac-arbres', '', null, 3, null, null, null, '{}', null))->>'plus_tard', 'true');
select set_config('request.headers', '{"cf-connecting-ip":"10.9.9.10"}', false) \g /dev/null
select pg_temp.ok('un autre réseau passe', (public.commun_retour_donner('cle-plafond-000301-eeeeeeee', 'td-bac-arbres', '', null, 3, null, null, null, '{}', null))->>'ok', 'true');
-- 16. La classe supprimée : ses avis restent pour « tout le monde », ses mots partent
select pg_temp.ok('supprimer la classe', public.commun_prof_supprimer_classe(:'prof', :'classe_id'::uuid, 'SUPPRIMER')->>'ok', 'true');
reset role;
select pg_temp.ok('avis gardés sans classe', count(*)::text, '14') from commun.retours where ressource = 'td-bac-abr' and classe_id is null;
select commun.retours_publier() \g /dev/null
select pg_temp.ok('mots de la classe supprimée effacés', count(*)::text, '0') from commun.retours where mot is not null;
-- 17. Deux ans après : effacé
insert into commun.retours (ressource, semaine, plu) values ('td-vieux', commun.retour_semaine() - 735, 3);
select commun.retours_publier() \g /dev/null
select pg_temp.ok('avis de plus de deux ans effacé', count(*)::text, '0') from commun.retours where ressource = 'td-vieux';
-- 18. Le registre range la table
select pg_temp.ok('registre : données d''élèves oui', donnees_eleves, 'oui') from commun.registre where schema_nom = 'commun' and table_nom = 'retours';
-- 19. Le compteur des avis est à part de celui du compte commun
select pg_temp.ok('compteur à part : celui du compte commun n''a que les 2 espaces créés', sum(echecs)::text, '2') from commun.essais where application = 'commun' and type = 'creation';

select n || '. ' || libelle || ' | ' || coalesce(obtenu, 'null') || ' | ' || case when obtenu is not distinct from attendu then 'ok' else 'ÉCHEC (attendu ' || coalesce(attendu, 'null') || ')' end from res order by n;
