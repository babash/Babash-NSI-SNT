#!/usr/bin/env node
/* Tests de assets/donnees.js (T51) : la validation et l'écriture des fichiers dans l'admin.

   Usage (depuis la racine du dépôt) :  node scripts/tests/test_admin_donnees.js [--sans-python]

   1. Écriture : chaque fiche et la vitrine, relues puis réécrites sans changement, donnent exactement le même
      texte ; un changement ne déplace que ses lignes.
   2. Validation : 0 erreur sur toutes les fiches et sur la vitrine du dépôt, comme scripts/valider_donnees.py.
   3. Parité avec le script : des fautes sont introduites dans une copie des données (une par fiche, et dans la
      vitrine) ; le script et l'admin doivent trouver une erreur dans les mêmes fichiers. Sans --sans-python,
      le script est lancé une fois sur la copie (python3 dans le PATH).
   Code de retour : 0 si tous les cas passent, 1 sinon. Node 18 ou plus, sans dépendance. */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const RACINE = path.resolve(__dirname, '..', '..');
const D = require(path.join(RACINE, 'assets', 'donnees.js'));
const SANS_PYTHON = process.argv.includes('--sans-python');

let echecs = 0, cas = 0;
function verifier(titre, ok, detail) {
  cas++;
  if (ok) console.log('  ok     ' + titre);
  else { echecs++; console.log('  ÉCHEC  ' + titre + (detail ? '\n         ' + String(detail).replace(/\n/g, '\n         ') : '')); }
}

const lire = (...p) => fs.readFileSync(path.join(RACINE, ...p), 'utf8');
const dossier = path.join(RACINE, 'donnees', 'ressources');
const noms = fs.readdirSync(dossier).filter((n) => n.endsWith('.json')).sort();

/* Les référentiels, sous la forme de bibliotheque-complete.json */
function referentiels(racine) {
  const l = (...p) => JSON.parse(fs.readFileSync(path.join(racine, 'donnees', 'referentiels', ...p), 'utf8'));
  return { valeurs: l('valeurs.json'), programmes: l('programmes.json').programmes, notions: l('notions.json'), competences_pix: l('competences-pix.json') };
}
function validation(racine, ids) {
  return new D.Validation({
    schemas: {
      ressource: JSON.parse(fs.readFileSync(path.join(racine, 'donnees', 'schema', 'ressource.schema.json'), 'utf8')),
      vitrine: JSON.parse(fs.readFileSync(path.join(racine, 'donnees', 'schema', 'vitrine.schema.json'), 'utf8'))
    },
    refs: referentiels(racine),
    ids: ids,
    fichiers: (c) => {
      const p = path.join(racine, ...c.replace(/\/$/, '').split('/'));
      if (!fs.existsSync(p)) return false;
      return fs.statSync(p).isDirectory() ? fs.existsSync(path.join(p, 'index.html')) : true;
    }
  });
}

console.log('Écriture');
let identiques = 0, differents = [];
for (const n of noms.concat(['../vitrine.json'])) {
  const t = fs.readFileSync(path.join(dossier, n), 'utf8');
  if (D.ecrire(JSON.parse(t), t) === t) identiques++; else differents.push(n);
}
verifier(`relu puis réécrit sans changement : ${identiques} fichiers sur ${noms.length + 1} identiques`, !differents.length, differents.join(', '));

const tTd = lire('donnees', 'ressources', 'td1-poo.json');
const o = JSON.parse(tTd);
o.statut = 'prete';
o.mots_cles = (o.mots_cles || []).concat(['objet']);
o.notes = (o.notes || []).concat([{ date: '2026-11-17', texte: 'Essai en classe : très bien.' }]);
const nouveau = D.ecrire(o, tTd);
const avant = tTd.split('\n'), apres = nouveau.split('\n');
const retirees = avant.filter((l) => !apres.includes(l));
verifier('un changement de statut, de mots-clés et une note : 2 lignes remplacées, la note ajoutée à la fin',
  retirees.length === 2 && JSON.stringify(JSON.parse(nouveau)) === JSON.stringify(o) && /"notes": \[\n    \{ "date": "2026-11-17"/.test(nouveau),
  retirees.join('\n'));
const v = JSON.parse(lire('donnees', 'vitrine.json'));
const tv = lire('donnees', 'vitrine.json');
const rub = v.rubriques[0];
const sec = rub.sections.find((s) => s.ressources.length > 1);
sec.ressources.reverse();
const nv = D.ecrire(v, tv);
const changees = tv.split('\n').filter((l, i) => nv.split('\n')[i] !== l).length;
verifier(`vitrine : deux ressources inversées dans une section : ${changees} lignes changent, le reste est gardé`,
  changees > 0 && changees <= sec.ressources.length + 1 && nv.split('\n').length === tv.split('\n').length);
verifier('nouveau fichier : indentation de deux espaces, petites listes sur une ligne',
  D.ecrire({ a: ['x', 'y'], b: { c: 1, d: 'e' }, f: [{ g: 1 }] }) === '{\n  "a": ["x", "y"],\n  "b": { "c": 1, "d": "e" },\n  "f": [\n    {\n      "g": 1\n    }\n  ]\n}\n');

console.log('Format des documents : la page (assets/site.js) et le script (deduire_format)');
{
  // site.js dans un bac à sable : il prête deduireFormatDocument (repli de l'aperçu de l'admin, T85)
  const vm = require('vm');
  const bac = { window: { addEventListener() {} }, document: { currentScript: { src: 'http://localhost/assets/site.js' }, readyState: 'complete',
    getElementById() { return null; }, addEventListener() {} }, location: { protocol: 'http:', href: 'http://localhost/', search: '' }, URL, console };
  bac.window.document = bac.document;
  vm.runInNewContext(fs.readFileSync(path.join(RACINE, 'assets', 'site.js'), 'utf8'), bac);
  const deduire = bac.window.deduireFormatDocument;
  const formats = JSON.parse(lire('donnees', 'referentiels', 'valeurs.json')).formats;
  const script = execFileSync('python3', ['-B', '-c', [
    'import json, os, sys',
    'sys.path.insert(0, os.path.join(sys.argv[1], "scripts"))',
    'import valider_donnees as vd',
    'v = vd.Validation(sys.argv[1])',
    'v.charger_referentiels()',
    'out = []',
    'd = os.path.join(sys.argv[1], "donnees", "ressources")',
    'for n in sorted(os.listdir(d)):',
    '    for doc in json.load(open(os.path.join(d, n), encoding="utf-8")).get("documents", []):',
    '        doc = {k: x for k, x in doc.items() if k != "format"}',
    '        out.append([n, doc.get("url") or doc.get("fichier"), doc.get("url") is not None, v.deduire_format(doc)])',
    'print(json.dumps(out))'].join('\n'), RACINE], { encoding: 'utf8' });
  const docs = JSON.parse(script);
  const ecarts = docs.filter(([, adresse, estUrl, attendu]) => deduire(estUrl ? { url: adresse } : { fichier: adresse }, formats) !== attendu);
  verifier(`les ${docs.length} documents des fiches : même format pour la page et pour le script`, docs.length > 0 && !ecarts.length,
    ecarts.slice(0, 5).map((e) => e[0] + ' ' + e[1] + ' : page ' + deduire(e[2] ? { url: e[1] } : { fichier: e[1] }, formats) + ', script ' + e[3]).join('\n'));
  verifier('Capytale Basthon : notebook (motif du référentiel)',
    deduire({ url: 'https://capytale2.ac-paris.fr/p/basthon/n/?kernel=python3&id=1' }, formats) === 'notebook');
}

console.log('Validation des données du dépôt');
const ids = noms.map((n) => n.replace(/\.json$/, ''));
const V = validation(RACINE, ids);
const enErreur = noms.filter((n) => V.fiche(JSON.parse(lire('donnees', 'ressources', n)), n).length);
verifier(`les ${noms.length} fiches : aucune erreur`, !enErreur.length, enErreur.slice(0, 5).map((n) => n + ' : ' + JSON.stringify(V.fiche(JSON.parse(lire('donnees', 'ressources', n)), n)[0])).join('\n'));
const ev = V.vitrine(JSON.parse(lire('donnees', 'vitrine.json')));
verifier('la vitrine : aucune erreur', !ev.length, JSON.stringify(ev.slice(0, 3)));

console.log('Parité avec scripts/valider_donnees.py');
/* Une faute par fiche (fiches prises dans l'ordre) ; chacune doit être une ERREUR pour le script et pour l'admin */
const FAUTES = [
  ['titre vide', (f) => { f.titre = ''; }],
  ['champ inconnu', (f) => { f.couleur_preferee = 'bleu'; }],
  ['statut hors du référentiel', (f) => { f.statut = 'termine'; }],
  ['type hors du référentiel', (f) => { f.types = ['tutoriel-video']; }],
  ['usage en double', (f) => { f.usages = [f.usages[0] || 'en-ligne', f.usages[0] || 'en-ligne']; }],
  ['thème du programme inconnu', (f) => { f.programme = ['snt-2019.cuisine']; }],
  ['programme entier cité', (f) => { f.programme = ['snt-2019']; f.enseignements = ['snt']; }],
  ['programme d\'un autre enseignement', (f) => { f.enseignements = ['snt']; f.programme = ['nsi-tle-2019.structures-de-donnees.poo']; }],
  ['fiche liée absente', (f) => { f.liees = [{ ressource: 'fiche-qui-n-existe-pas', relation: 'voir-aussi' }]; }],
  ['notion absente du thésaurus', (f) => { f.notions = { travaillees: ['prog.cuisine-moleculaire'] }; }],
  ['aucun document principal', (f) => { f.documents.forEach((d) => { delete d.principal; }); }],
  ['deux documents principaux', (f) => { f.documents.push({ role: 'complement', url: 'https://example.org/', principal: true, visible: { exterieur: true, eleve: true } }); }],
  ['lien principal vers GitHub', (f) => { f.documents.forEach((d) => { delete d.principal; }); f.documents.unshift({ role: 'enonce', url: 'https://github.com/babash/Babash-NSI-SNT', principal: true, visible: { exterieur: true, eleve: true } }); }],
  ['fichier du site introuvable', (f) => { f.documents.push({ role: 'complement', fichier: 'snt/fichiers/n-existe-pas.pdf', visible: { exterieur: true, eleve: true } }); }],
  ['visibilité incomplète', (f) => { f.documents[0].visible = { exterieur: true }; }],
  ['url et fichier ensemble', (f) => { f.documents[0].url = 'https://example.org/'; f.documents[0].fichier = 'snt/index.html'; }],
  ['adresse en http mal formée', (f) => { f.documents[0].url = 'https://exa mple.org'; delete f.documents[0].fichier; }],
  ['date impossible', (f) => { f.dates = Object.assign({}, f.dates, { ajout: '2026-02-30' }); }],
  ['note sans texte', (f) => { f.notes = [{ date: '2026-11-17' }]; }],
  ['note avec un mot de passe', (f) => { f.notes = [{ date: '2026-11-17', texte: 'Compte de la salle : mot de passe : Lagon2026' }]; }],
  ['jeton GitHub dans une note', (f) => { f.notes = [{ texte: 'github_pat_' + 'A1b2C3d4E5'.repeat(4) }]; }],
  ['facultative sans collecte', (f) => { f.donnees_eleves = { collecte: false, facultative: true }; }],
  ['identifiant différent du fichier', (f) => { f.id = f.id + '-bis'; }],
  ['mot-clé trop long', (f) => { f.mots_cles = ['x'.repeat(41)]; }],
  ['« Rien à installer » et « installation » ensemble', (f) => { f.usages = ['en-ligne', 'sans-installation', 'installation']; }]
];
const FAUTES_VITRINE = [
  ['ressource inconnue dans une section', (v) => { v.rubriques[0].sections[0].ressources.push('fiche-qui-n-existe-pas'); }],
  ['thème en double', (v) => { const r = v.rubriques[0]; const s = r.sections.find((x) => x.programme); r.sections.push({ programme: s.programme, ressources: [] }); }],
  ['section libre sans titre', (v) => { v.rubriques[1].sections.push({ id: 'sans-titre', ressources: [] }); }],
  ['à la une : fiche inconnue', (v) => { v.a_la_une.push({ ressource: 'fiche-qui-n-existe-pas' }); }],
  // T162 : une entrée d'essai, sans dépendre du contenu réel de « à la une » (vide depuis T155) ; une fiche
  // placée et pas encore à la une, pour que la seule faute soit celle des dates
  ['à la une : début après la fin', (v) => {
    const deja = new Set(v.a_la_une.map((u) => u.ressource));
    const rid = v.rubriques.flatMap((r) => r.sections).flatMap((s) => s.ressources).find((x) => !deja.has(x));
    v.a_la_une.push({ ressource: rid, debut: '2026-12-01', fin: '2026-11-01' });
  }],
  ['contenu d\'un autre thème', (v) => { const r = v.rubriques[0]; const s = r.sections.filter((x) => x.programme); s[1].sous_sections = (s[1].sous_sections || []).concat([{ programme: s[0].programme + '.x', ressources: [] }]); }],
  ['ressource en double dans une section', (v) => { const s = v.rubriques[0].sections.find((x) => x.ressources.length); s.ressources.push(s.ressources[0]); }]
];

const copie = fs.mkdtempSync(path.join(os.tmpdir(), 'test-admin-donnees-'));
try {
  for (const n of fs.readdirSync(RACINE)) {
    if (n === '.git' || n === 'donnees') continue;
    fs.symlinkSync(path.join(RACINE, n), path.join(copie, n));
  }
  fs.cpSync(path.join(RACINE, 'donnees'), path.join(copie, 'donnees'), { recursive: true });
  for (const f of ['bibliotheque.json', 'bibliotheque-complete.json', 'bibliotheque-textes.json']) {
    fs.rmSync(path.join(copie, 'donnees', f), { force: true });
  }
  /* Les fiches qui reçoivent une faute : jamais une fiche citée dans les « liees » d'une autre fiche, pour qu'une
     faute ne touche qu'elle. Une fiche dont l'identifiant change casse sinon le lien de l'autre fiche, que le
     script signale et que l'admin, qui contrôle la fiche qu'on modifie, ne voit pas (T51c). La vitrine peut les
     citer : ses erreurs sont rangées sous donnees/vitrine.json, hors de cette comparaison des fiches.
     Une fiche par faute, réparties sur la liste : le test ne dépend ni du nombre ni de l'ordre des fiches. */
  const citees = new Set();
  for (const n of noms) {
    for (const l of JSON.parse(lire('donnees', 'ressources', n)).liees || []) if (l && l.ressource) citees.add(l.ressource);
  }
  const libres = noms.filter((n) => !citees.has(n.replace(/\.json$/, '')));
  verifier(`assez de fiches citées par aucune autre pour les ${FAUTES.length} fautes (${libres.length})`, libres.length >= FAUTES.length);
  const touchees = {};
  FAUTES.forEach(([nom, faute], i) => {
    const n = libres[Math.floor(i * libres.length / FAUTES.length)];
    const p = path.join(copie, 'donnees', 'ressources', n);
    const f = JSON.parse(fs.readFileSync(p, 'utf8'));
    faute(f);
    fs.writeFileSync(p, JSON.stringify(f, null, 2) + '\n');
    touchees[n] = nom;
  });
  const Vc = validation(copie, ids);
  const js = {};
  for (const n of Object.keys(touchees)) {
    js[n] = Vc.fiche(JSON.parse(fs.readFileSync(path.join(copie, 'donnees', 'ressources', n), 'utf8')), n);
  }
  for (const [n, nom] of Object.entries(touchees)) {
    verifier(`admin, ${nom} (${n}) : erreur trouvée`, js[n].length > 0, '');
  }
  // La vitrine, faute par faute (une vitrine fausse arrête le contrôle de ses références au premier écart de schéma)
  const vOrig = JSON.parse(lire('donnees', 'vitrine.json'));
  // Le témoin (T162) : la vitrine telle quelle, et avec une entrée d'essai « à la une » aux dates en ordre, est
  // sans erreur ; une erreur trouvée plus bas vient donc de la faute
  {
    const vt = JSON.parse(JSON.stringify(vOrig));
    verifier('admin, vitrine telle quelle : aucune erreur', Vc.vitrine(vt).length === 0, JSON.stringify(Vc.vitrine(vt)));
    const deja = new Set(vt.a_la_une.map((u) => u.ressource));
    const rid = vt.rubriques.flatMap((r) => r.sections).flatMap((s) => s.ressources).find((x) => !deja.has(x));
    vt.a_la_une.push({ ressource: rid, debut: '2026-11-01', fin: '2026-12-01' });
    verifier('admin, vitrine : une entrée « à la une » aux dates en ordre : aucune erreur', Vc.vitrine(vt).length === 0, JSON.stringify(Vc.vitrine(vt)));
  }
  for (const [nom, faute] of FAUTES_VITRINE) {
    const vv = JSON.parse(JSON.stringify(vOrig));
    faute(vv);
    verifier(`admin, vitrine : ${nom} : erreur trouvée`, Vc.vitrine(vv).length > 0, '');
  }

  if (!SANS_PYTHON) {
    let sortie = '';
    try {
      sortie = execFileSync('python3', ['-B', path.join(RACINE, 'scripts', 'valider_donnees.py'), '--racine', copie], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    } catch (e) { sortie = (e.stdout || '') + (e.stderr || ''); }
    const py = new Set();
    for (const l of sortie.split('\n')) {
      const m = /^ERREUR\s+donnees\/ressources\/([^ ]+\.json)/.exec(l);
      if (m) py.add(m[1]);
    }
    const jsSet = new Set(Object.keys(js).filter((n) => js[n].length));
    const seulPy = [...py].filter((n) => !jsSet.has(n));
    const seulJs = [...jsSet].filter((n) => !py.has(n));
    verifier(`script et admin trouvent des erreurs dans les mêmes fiches (${py.size} pour le script, ${jsSet.size} pour l'admin)`,
      !seulPy.length && !seulJs.length,
      'seulement le script : ' + seulPy.map((n) => n + ' (' + touchees[n] + ')').join(', ') + '\nseulement l\'admin : ' + seulJs.join(', '));
    // Chaque faute de vitrine, une à une, avec le script
    for (const [nom, faute] of FAUTES_VITRINE) {
      const vv = JSON.parse(JSON.stringify(vOrig));
      faute(vv);
      fs.writeFileSync(path.join(copie, 'donnees', 'vitrine.json'), JSON.stringify(vv, null, 2) + '\n');
      let s2 = '';
      try { s2 = execFileSync('python3', ['-B', path.join(RACINE, 'scripts', 'valider_donnees.py'), '--racine', copie], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }); } catch (e) { s2 = (e.stdout || '') + (e.stderr || ''); }
      verifier(`script, vitrine : ${nom} : erreur trouvée aussi`, /^ERREUR\s+donnees\/vitrine\.json/m.test(s2), '');
    }
  }
} finally {
  fs.rmSync(copie, { recursive: true, force: true });
}

console.log(`\n${cas} cas, ${echecs} échec(s)`);
process.exit(echecs ? 1 : 0);
