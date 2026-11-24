-- Empreinte du compte commun, par genre d'objet (T132d) : à lancer en lecture sur la base réelle et sur une base locale
-- construite avec supabase/ (socle, 0007, 0008) ; les deux résultats doivent être identiques, sauf « fonction_droits »
-- (service_role, droits par défaut de la plateforme : remplacer postgres= par postgres=|service_role= pour le retirer).
with
ns as (select 'commun'::regnamespace::oid as o),
fn as (select p.oid, n.nspname||'.'||p.proname||'('||pg_get_function_identity_arguments(p.oid)||')' as nom
       from pg_proc p join pg_namespace n on n.oid=p.pronamespace
       where n.nspname='commun' or (n.nspname='public' and p.proname like 'commun\_%')),
rel as (select c.oid, c.relname, c.relkind from pg_class c where c.relnamespace=(select o from ns) and c.relkind in ('r','v','i')),
lignes(genre, nom, valeur) as (
  select 'fonction', nom, md5(replace(pg_get_functiondef(oid), chr(13), '')) from fn
  union all select 'fonction_droits', f.nom, coalesce((select string_agg(x, ',' order by x collate "C") from unnest(p.proacl::text[]) x where x !~ '^(supabase_|postgres=)'),'')
    from fn f join pg_proc p on p.oid=f.oid
  union all select 'fonction_commentaire', f.nom, md5(coalesce(obj_description(f.oid,'pg_proc'),'')) from fn f
  union all select 'table', r.relname, r.relkind::text||'|rls='||c.relrowsecurity||'|'||coalesce((select string_agg(x, ',' order by x collate "C") from unnest(c.relacl::text[]) x where x !~ '^(supabase_|postgres=)'),'')
    from rel r join pg_class c on c.oid=r.oid where r.relkind<>'i'
  union all select 'table_commentaire', r.relname, md5(coalesce(obj_description(r.oid,'pg_class'),'')) from rel r where r.relkind<>'i'
  union all select 'colonne', r.relname||'.'||a.attname, md5(format_type(a.atttypid,a.atttypmod)||'|'||a.attnotnull||'|'||coalesce(pg_get_expr(d.adbin,d.adrelid),'')||'|'||coalesce(col_description(r.oid,a.attnum),''))
    from rel r join pg_attribute a on a.attrelid=r.oid and a.attnum>0 and not a.attisdropped left join pg_attrdef d on d.adrelid=r.oid and d.adnum=a.attnum where r.relkind in ('r','v')
  union all select 'contrainte', r.relname||'.'||co.conname, md5(pg_get_constraintdef(co.oid)) from rel r join pg_constraint co on co.conrelid=r.oid
  union all select 'index', r.relname, md5(pg_get_indexdef(r.oid)) from rel r where r.relkind='i'
  union all select 'vue', r.relname, md5(pg_get_viewdef(r.oid)) from rel r where r.relkind='v'
  union all select 'schema', 'commun', coalesce((select string_agg(x, ',' order by x collate "C") from unnest(n.nspacl::text[]) x where x !~ '^(supabase_|postgres=)'),'')||'|'||md5(coalesce(obj_description(n.oid,'pg_namespace'),'')) from pg_namespace n where n.nspname='commun'
  union all select 'donnees', 'applications', md5(coalesce((select string_agg(row(id,nom,adresse,adresse_prof,mode,accord_par_page,pseudo_a_confirmer,plafond_xp_jour,active,fn_par_code,fn_par_id,fn_effacer,fn_fusion,fn_hauts_faits,fn_prof_par_code,fn_prof_eleves)::text, ';' order by id collate "C") from commun.applications),''))
  union all select 'donnees', 'mots', md5((select string_agg(application||':'||rang||':'||mot, ';' order by application collate "C", rang) from commun.mots))
  union all select 'donnees', 'emplacements', md5((select string_agg(row(id,nom,genre,ordre)::text, ';' order by id collate "C") from commun.emplacements))
  union all select 'donnees', 'elements', md5((select string_agg(row(id,emplacement,famille,nom,description,acces,prix,ordre,actif)::text, ';' order by id collate "C") from commun.elements))
  union all select 'donnees', 'baremes', md5((select string_agg((to_jsonb(b))::text, ';' order by application collate "C", evenement collate "C") from commun.baremes b))
  union all select 'donnees', 'hauts_faits', md5(coalesce((select string_agg((to_jsonb(h)-'ajoute_le'-'cree_le')::text, ';' order by application collate "C", id collate "C") from commun.hauts_faits h),''))
  union all select 'donnees', 'recompenses', md5(coalesce((select string_agg((to_jsonb(h))::text, ';' order by 1) from commun.recompenses h),''))
  union all select 'donnees', 'activites', (select count(*)::text from commun.activites)
  union all select 'donnees', 'menage', (select count(*)::text from commun.menage)
)
select genre, count(*) as n, md5(string_agg(nom||' '||valeur, chr(10) order by (nom||' '||valeur) collate "C")) as empreinte from lignes group by genre order by genre;