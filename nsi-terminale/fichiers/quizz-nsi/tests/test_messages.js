// QuizzNSI : tests de la validation des messages du canal (js/messages.js), sans navigateur.
// Pour chaque type de message et chaque champ, y compris les champs imbriqués, une valeur forgée
// (balise, nombre énorme, négatif, décimal, objet, liste, chaîne très longue, booléen) fait rejeter
// le message entier. Lancement : node tests/test_messages.js
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
globalThis.location = { search: '' };
require(path.join(__dirname, '..', 'js', 'commun.js'));
const M = require(path.join(__dirname, '..', 'js', 'messages.js'));

const MOI = '0123456789abcdef', AUTRE = 'fedcba9876543210';
const BALISE = '<img src=x onerror="globalThis.__pwned=1">XSSMARK';
const FORGES = [BALISE, 1e300, -1, 2.5, Number.NaN, {}, { a: '<b>' }, [BALISE], 'x'.repeat(100000), true, undefined];
const bilan = () => ({ justes: 2, repondues: 3, serie: 1, meilleure: 2, rebonds: 1, suite: ['juste', 'faux', null] });

const VERS_ELEVE = {
  attente: { t: 'attente' },
  notion: { t: 'notion', cours: 'piles-files', n: 3 },
  question: { t: 'question', cours: 'piles-files', qid: 'q01', reste: 30000, ferme: false },
  fermee: { t: 'fermee', qid: 'q01' },
  recus: { t: 'recus', qid: 'q01', ids: [MOI, AUTRE] },
  retire: { t: 'retire', id: MOI },
  refus: { t: 'refus', id: MOI, raison: 'pris' },
  correction: { t: 'correction', cours: 'piles-files', qid: 'q01', rep: [1, 2, 0, 0],
    res: { [MOI]: { c: 1, gain: 140, detail: { participation: 10, juste: 100, rapidite: 0, rebond: 30 }, total: 400, bilan: bilan() } },
    podium: [{ pseudo: 'Nadia', total: 400, place: 1 }] },
  fin: { t: 'fin', cours: 'piles-files', res: { [MOI]: { total: 400, place: 2, bilan: bilan(), arevoir: [2, 5] } }, podium: [{ pseudo: 'Ali', total: 500, place: 1 }] },
};
const VERS_HOTE = { bonjour: { t: 'bonjour', id: MOI }, rep: { t: 'rep', id: MOI, qid: 'q03', c: 2 } };

// tous les chemins des feuilles d'un objet (les champs à forger)
function chemins(o, base = []) {
  if (o === null || typeof o !== 'object') return [base];
  const l = [];
  for (const k of Object.keys(o)) l.push(...chemins(o[k], base.concat(k)));
  return l.length ? l : [base];
}
const copie = o => JSON.parse(JSON.stringify(o));
function remplacer(o, chemin, v) { const c = copie(o); let x = c; for (const k of chemin.slice(0, -1)) x = x[k]; x[chemin[chemin.length - 1]] = v; return c; }
// toutes les chaînes d'une sortie validée : elles doivent venir de listes permises ou de formats stricts
function chaines(o, l = []) { if (typeof o === 'string') l.push(o); else if (o && typeof o === 'object') Object.values(o).forEach(v => chaines(v, l)); return l; }

let n = 0;
for (const [type, m] of Object.entries(VERS_ELEVE)) {
  const ok = M.versEleve(copie(m), MOI);
  assert.ok(ok, 'message valide refusé : ' + type);
  for (const s of chaines(ok)) assert.ok(/^[a-z0-9-]{1,60}$/.test(s) || ['juste', 'faux', 'pris', 'invalide'].includes(s) || s === 'Nadia' || s === 'Ali', 'chaîne inattendue : ' + s);
  for (const ch of chemins(m)) {
    if (ch.length === 1 && ch[0] === 't') continue;
    const lire = (o, c) => c.reduce((x, k) => x[k], o);
    for (const v of typeof lire(m, ch) === 'number' ? FORGES.concat(['3']) : FORGES) {
      if (typeof v === 'boolean' && typeof lire(m, ch) === 'boolean') continue; // un booléen reste un booléen permis
      const forge = remplacer(m, ch, v);
      const r = M.versEleve(forge, MOI);
      // un champ facultatif retiré (undefined) peut rester valide s'il est permis absent : jamais ici
      assert.equal(r, null, `${type}.${ch.join('.')} = ${String(v).slice(0, 30)} accepté`);
      n++;
    }
  }
  // une clé inconnue fait rejeter le message
  assert.equal(M.versEleve(Object.assign(copie(m), { html: BALISE }), MOI), null, type + ' avec une clé en plus');
  n++;
}
for (const [type, m] of Object.entries(VERS_HOTE)) {
  assert.ok(M.versHote(copie(m)), 'message valide refusé : ' + type);
  for (const ch of chemins(m)) {
    if (ch[0] === 't') continue;
    for (const v of FORGES) { assert.equal(M.versHote(remplacer(m, ch, v)), null, `${type}.${ch.join('.')} accepté`); n++; }
  }
}
// une seule entrée forgée dans res, même celle d'un·e autre élève, fait rejeter tout le message
assert.equal(M.versEleve(Object.assign(copie(VERS_ELEVE.correction), { res: { [AUTRE]: { c: BALISE } } }), MOI), null);
assert.equal(M.versEleve(Object.assign(copie(VERS_ELEVE.correction), { res: { '<b>': VERS_ELEVE.correction.res[MOI] } }), MOI), null);
// une correction valide sans entrée pour cet·te élève : rien à lui afficher sur ses points
assert.equal(M.versEleve(Object.assign(copie(VERS_ELEVE.correction), { res: {} }), MOI).moi, null);
n += 3;
// types inconnus, prototypes, valeurs non objets
for (const v of [null, 3, 'attente', [], { t: 'inconnu' }, { t: { toString: () => 'attente' } }, JSON.parse('{"t":"attente","__proto__":{"x":1}}')]) {
  assert.equal(M.versEleve(v, MOI), null, JSON.stringify(v)); assert.equal(M.versHote(v), null); n++;
}
// présence : pseudo filtré, rôle permis, clés permises
assert.deepEqual(M.presence({ id: MOI, pseudo: 'Zaïna', role: 'eleve', presence_ref: 'x' }), { id: MOI, role: 'eleve', pseudo: 'Zaïna' });
assert.equal(M.presence({ id: MOI, pseudo: BALISE, role: 'eleve' }).pseudo, null);
assert.equal(M.presence({ id: MOI, pseudo: 'x'.repeat(100000), role: 'eleve' }), null);
assert.equal(M.presence({ id: '<b>', pseudo: 'Ali', role: 'eleve' }), null);
assert.equal(M.presence({ id: MOI, pseudo: 'Ali', role: 'admin' }), null);
assert.equal(M.presence({ id: MOI, pseudo: 'Ali', role: 'eleve', html: '<b>' }), null);
assert.equal(M.presence({ id: MOI, pseudo: {}, role: 'eleve' }), null);
n += 7;
assert.equal(globalThis.__pwned, undefined);
console.log(n + ' messages forgés rejetés, aucun accepté');
