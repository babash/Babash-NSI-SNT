#!/usr/bin/env node
/* Calendrier des vacances (T165) : la comparaison des réponses tapées (CV.normReponse, calendrier/jeux.js).
   Une réponse juste écrite autrement (espaces autour des virgules et des crochets, guillemets simples ou
   doubles, virgule finale d'une liste) est acceptée ; une réponse fausse ne l'est jamais. Éprouvé sur des
   cas écrits à la main et sur CHAQUE réponse à taper des banques (calendrier/exercices/*.json) : ses
   variantes justes passent, ses variantes fausses (autre casse, guillemets autour, espace retirée entre
   deux mots, un chiffre changé, une autre réponse de la banque) ne passent pas.

   Usage (depuis la racine du dépôt) :  node scripts/tests/test_calendrier_reponses.js [DOSSIER_DES_BANQUES]
   Code de retour : 0 si tous les cas passent, 1 sinon. Node seul, sans dépendance. */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const racine = path.join(__dirname, '..', '..');
const dossier = path.resolve(process.argv[2] || path.join(racine, 'calendrier', 'exercices'));
const fenetre = { CV_CONFIG: {} };
const ctx = vm.createContext({ window: fenetre, Intl, Date, Math, JSON, String, Array, Object, RegExp, Promise });
for (const f of ['commun.js', 'jeux.js']) vm.runInContext(fs.readFileSync(path.join(racine, 'calendrier', f), 'utf8'), ctx, { filename: f });
const CV = fenetre.CV;
const ok = (tape, attendu) => CV.normReponse(tape) === CV.normReponse(attendu);

let n = 0, echecs = 0;
function cas(titre, bon, detail) {
  n++;
  if (!bon) { echecs++; console.log('  ÉCHEC  ' + titre + (detail ? '\n         ' + detail : '')); }
}

/* 1. Les cas écrits à la main */
const ACCEPTES = [
  ['[4,5,3,2,1]', '[4, 5, 3, 2, 1]'], ['[ 4 , 5 ]', '[4, 5]'], ['[4, 5,]', '[4, 5]'], ['  12  ', '12'],
  ['["a", "b"]', "['a', 'b']"], ["{'x':1,'y':2}", "{'x': 1, 'y': 2}"], ['(1, 2)', '(1,2)'], ['True  False', 'True False'],
  ['[[1,2],[3]]', '[[1, 2], [3]]'], ["['Kenza','Lou']", "['Kenza', 'Lou']"], ['{1: [2, 3],}', '{1: [2, 3]}'],
];
const REFUSES = [
  ['[4, 5, 3, 1, 2]', '[4, 5, 3, 2, 1]'], ['true False', 'True False'], ['TrueFalse', 'True False'], ['zawadi', 'Zawadi'],
  ['"Kenza"', 'Kenza'], ["'Kenza'", 'Kenza'], ['7-5', '7 -5'], ['75', '7 5'], ['(1)', '(1,)'], ['12', '12.0'],
  ["['a b']", "['ab']"], ["['A']", "['a']"], ['[4, 5]', '[4, 5, 6]'], ['4, 5', '[4, 5]'], ['a : 1', 'a: 1'], ['2 1', '2, 1'],
  ['', '0'], ['l * g * n', 'l*g*n'],
];
for (const [t, a] of ACCEPTES) cas(`accepté : « ${t} » pour « ${a} »`, ok(t, a), `${CV.normReponse(t)} / ${CV.normReponse(a)}`);
for (const [t, a] of REFUSES) cas(`refusé : « ${t} » pour « ${a} »`, !ok(t, a), `${CV.normReponse(t)} / ${CV.normReponse(a)}`);
cas('presque : la casse est signalée', /majuscules/.test(CV.presque('true false', 'True False')));
cas('presque : les guillemets sont signalés', /guillemets/.test(CV.presque('"Kenza"', 'Kenza')));
cas('presque : rien pour une réponse fausse', CV.presque('8', '9') === '');

/* 2. Chaque réponse à taper des banques */
const reponses = [];
for (const nom of fs.readdirSync(dossier).sort()) {
  if (!nom.endsWith('.json') || nom.split('.').length > 2 || nom === 'catalogue.json' || nom === 'exercice.schema.json') continue;
  const b = JSON.parse(fs.readFileSync(path.join(dossier, nom), 'utf8'));
  for (const ex of b.exercices) {
    if (ex.type !== 'sortie') continue;
    ex.niveaux.forEach((nv, i) => nv.items.forEach((it, k) => {
      if (!it.options) reponses.push({ ou: `${ex.id} N${i + 1} Q${k + 1}`, r: String(it.reponse) });
    }));
  }
}
const distinctes = [...new Set(reponses.map(x => x.r))];
let variantes = 0;
const confondues = new Set();
for (const { ou, r } of reponses) {
  const justes = new Set([r, ' ' + r + ' ', r.replace(/ /g, '  '),
    r.replace(/\s*([,[\](){}])\s*/g, '$1'), r.replace(/,\s*/g, ', ').replace(/\[/g, '[ ').replace(/\]/g, ' ]'),
    r.replace(/'/g, '"'), r.replace(/\]$/, ',]')]);
  for (const v of justes) { variantes++; cas(`${ou} : « ${v} » accepté pour « ${r} »`, ok(v, r)); }
  const fausses = new Set();
  if (r.toLowerCase() !== r) fausses.add(r.toLowerCase());
  if (r.toUpperCase() !== r) fausses.add(r.toUpperCase());
  fausses.add('"' + r + '"');
  if (/\w \S|\S \w/.test(r) && !/[,[\](){}]/.test(r)) fausses.add(r.replace(/ /g, ''));
  const chiffre = r.replace(/\d/, d => String((+d + 1) % 10));
  if (chiffre !== r) fausses.add(chiffre);
  // deux réponses différentes de la banque ne se confondent jamais (sauf si elles ne diffèrent que par l'écriture : listées)
  for (const autre of distinctes) if (autre !== r) { if (ok(autre, r)) confondues.add([r, autre].sort().join(' = ')); else fausses.add(autre); }
  for (const v of fausses) { variantes++; cas(`${ou} : « ${v} » refusé pour « ${r} »`, !ok(v, r)); }
}
for (const c of confondues) console.log('  même valeur, écrite autrement dans deux questions : ' + c);
console.log(`${reponses.length} réponses à taper, ${distinctes.length} distinctes, ${variantes} variantes éprouvées, ${n} cas, ${echecs} échec(s)`);
process.exit(echecs ? 1 : 0);
