-- Le complément de scripts/supabase_empreinte_commun.sql (Gardien, T132d) : ce que cette empreinte ne regarde pas
-- (types, séquences, déclencheurs, règles RLS, RLS forcée, droits de colonnes, propriétaires, security definer et
-- volatilité des fonctions, fonctions « commun » ailleurs, dépendances d'autres schémas, publications, droits par défaut).
-- Métadonnées seulement, aucune donnée. À lancer en lecture sur la base réelle et sur une base locale construite avec
-- supabase/ : les lignes « resume » doivent être identiques ; les lignes « detail » décrivent ce qui diffère par nature
-- (droits par défaut de la plateforme).
with
cr as (select c.oid, c.relname, c.relkind from pg_class c where c.relnamespace = 'commun'::regnamespace),
l(genre, nom, valeur) as (
  select 'relkind_autre', relname, relkind::text from cr where relkind not in ('r','v','i')
  union all select 'type', t.typname, t.typtype::text from pg_type t
    where t.typnamespace = 'commun'::regnamespace and t.typtype not in ('c') and t.typelem = 0 and t.typrelid = 0
  union all select 'type_composite_libre', t.typname, '' from pg_type t join pg_class c on c.oid = t.typrelid
    where t.typnamespace = 'commun'::regnamespace and c.relkind = 'c'
  union all select 'sequence', c.relname, coalesce(array_to_string(c.relacl, ','), '') from pg_class c join cr on cr.oid = c.oid where cr.relkind = 'S'
  union all select 'declencheur', c.relname || '.' || tg.tgname, md5(pg_get_triggerdef(tg.oid)) from pg_trigger tg join cr c on c.oid = tg.tgrelid where not tg.tgisinternal
  union all select 'regle_rls', c.relname || '.' || po.polname, po.polcmd::text from pg_policy po join cr c on c.oid = po.polrelid
  union all select 'rls_forcee', c.relname, c.relforcerowsecurity::text from pg_class c join cr on cr.oid = c.oid where cr.relkind = 'r'
  union all select 'droit_colonne', c.relname || '.' || a.attname, array_to_string(a.attacl, ',') from pg_attribute a join cr c on c.oid = a.attrelid where a.attacl is not null
  union all select 'proprietaire_table', c.relname, pg_get_userbyid(c.relowner) from pg_class c join cr on cr.oid = c.oid where cr.relkind in ('r','v')
  union all select 'proprietaire_fonction', n.nspname || '.' || p.proname, pg_get_userbyid(p.proowner) || '|secdef=' || p.prosecdef || '|vol=' || p.provolatile::text
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'commun' or (n.nspname = 'public' and p.proname like 'commun\_%')
  union all select 'fonction_ailleurs', n.nspname || '.' || p.proname, '' from pg_proc p join pg_namespace n on n.oid = p.pronamespace
    where p.proname ilike '%commun%' and not (n.nspname = 'commun' or (n.nspname = 'public' and p.proname like 'commun\_%'))
  union all select 'dependance_externe', n.nspname || '.' || dc.relname, c.relname from pg_depend d
    join pg_rewrite rw on rw.oid = d.objid join pg_class dc on dc.oid = rw.ev_class join pg_namespace n on n.oid = dc.relnamespace
    join cr c on c.oid = d.refobjid where n.nspname <> 'commun'
  union all select 'publication', pb.pubname, c.relname from pg_publication_rel pr join pg_publication pb on pb.oid = pr.prpubid join cr c on c.oid = pr.prrelid
  union all select 'droit_par_defaut', pg_get_userbyid(d.defaclrole) || '|' || coalesce(n.nspname, '(global)') || '|' || d.defaclobjtype::text, array_to_string(d.defaclacl, ',')
    from pg_default_acl d left join pg_namespace n on n.oid = d.defaclnamespace where coalesce(n.nspname, '') in ('', 'commun', 'public')
  union all select 'schema_proprietaire', 'commun', pg_get_userbyid(nspowner) from pg_namespace where nspname = 'commun'
)
,
agg as (select genre, count(*) n, md5(string_agg(nom || '|' || valeur, chr(10) order by nom collate "C", valeur collate "C")) e from l where genre not in ('droit_par_defaut') group by genre)
select 'resume' as quoi, genre, n::text, e from agg
union all select 'detail', genre, nom, valeur from l where genre in ('droit_par_defaut','relkind_autre','type','type_composite_libre','sequence','declencheur','regle_rls','droit_colonne','fonction_ailleurs','dependance_externe','publication','schema_proprietaire')
order by 1 desc, 2, 3;
