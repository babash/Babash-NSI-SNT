// QuizzNSI : tests du barème et des outils communs, sans navigateur.
// Lancement, depuis la racine de QuizzNSI : node tests/test_moteur.js
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
globalThis.location = { search: '' };
require(path.join(__dirname, '..', 'js', 'commun.js'));
const B = require(path.join(__dirname, '..', 'js', 'bareme.js'));
const Q = globalThis.QuizzNSI;
let n = 0;
const essai = (nom, f) => { f(); n++; console.log('ok  ' + nom); };

essai('barème : une réponse fausse rapporte la participation seule', () => {
  assert.deepEqual(B.points({ juste: false, ms: 1000 }, { duree: 30, precedente: 'faux' }).total, 10);
});
essai('barème : pas de réponse, pas de point', () => assert.equal(B.points(null, {}).total, 0));
essai('barème : bonne réponse sans minuterie, sans bonus de rapidité', () => {
  const p = B.points({ juste: true, ms: 10 }, { duree: 0, precedente: 'juste' });
  assert.equal(p.total, 110); assert.equal(p.detail.rapidite, 0);
});
essai('barème : rapidité de 20 à 0 sur la durée de la minuterie', () => {
  assert.equal(B.points({ juste: true, ms: 0 }, { duree: 30 }).detail.rapidite, 20);
  assert.equal(B.points({ juste: true, ms: 15000 }, { duree: 30 }).detail.rapidite, 10);
  assert.equal(B.points({ juste: true, ms: 45000 }, { duree: 30 }).detail.rapidite, 0);
});
essai('barème : le rebond après une erreur', () => {
  const p = B.points({ juste: true, ms: 30000 }, { duree: 30, precedente: 'faux' });
  assert.equal(p.detail.rebond, 30); assert.equal(p.total, 140);
  assert.equal(B.points({ juste: true }, { precedente: null }).detail.rebond, 0); // sans réponse avant : pas de rebond
});
essai('barème : réfléchir rapporte plus que se presser', () => {
  assert.ok(B.points({ juste: true, ms: 29000 }, { duree: 30 }).total > B.points({ juste: false, ms: 0 }, { duree: 30 }).total + 80);
});
essai('classement : ex aequo à la même place', () => {
  const l = B.classer([{ pseudo: 'b', total: 200, justes: 2 }, { pseudo: 'a', total: 200, justes: 2 }, { pseudo: 'c', total: 300, justes: 2 }, { pseudo: 'd', total: 10, justes: 0 }]);
  assert.deepEqual(l.map(j => j.pseudo + j.place), ['c1', 'a2', 'b2', 'd4']);
});
essai('répartition des réponses', () => assert.deepEqual(B.repartition([0, 1, 1, 3, null, 7, -1, 1.5]), [1, 2, 0, 1]));
essai('progression : séries et rebonds', () => {
  const p = B.progression(['juste', 'faux', 'juste', 'juste', null, 'juste']);
  assert.deepEqual([p.justes, p.repondues, p.serie, p.meilleure, p.rebonds], [4, 5, 1, 2, 1]);
});

essai('pseudo : prénoms et pseudos acceptés', () => {
  for (const p of ['Kobalt', 'Zéphyr', 'Ixo', 'Pixel-42', "L'Orque", 'kiki_976', 'Néon M.', 'Кобальт', 'Ζέφυρος', 'نجمة']) assert.ok(Q.filtrerPseudo(p).ok, p);
  assert.equal(Q.filtrerPseudo('  Ixo   Neo  ').pseudo, 'Ixo Neo');
});
essai('pseudo : longueur bornée', () => {
  assert.equal(Q.filtrerPseudo('A').ok, false);
  assert.equal(Q.filtrerPseudo('Abcdefghijklmnopq').ok, false);
  assert.equal(Q.filtrerPseudo('Abcdefghijklmnop').ok, true);
});
essai('pseudo : caractères invisibles refusés', () => {
  for (const c of [0x200B, 0x200D, 0x202E, 0x2066, 0xFEFF, 0x00AD, 0x0007]) assert.equal(Q.filtrerPseudo('Ko' + String.fromCharCode(c) + 'balt').ok, false, c.toString(16));
});
essai('pseudo : rien d\'injectable', () => {
  for (const p of ['<b>Ixo</b>', 'Ixo"><img', '{{x}}', 'a&b', 'Ixo;drop', '../x', '😀😀']) assert.equal(Q.filtrerPseudo(p).ok, false, p);
});
essai('pseudo : la clé de comparaison ignore accents et casse', () => assert.equal(Q.clePseudo('Zéphyr'), Q.clePseudo('ZEPHYR')));
essai('pseudo : les autres écritures gardent une clé propre (jamais vide)', () => {
  assert.notEqual(Q.clePseudo('Кобальт'), ''); assert.notEqual(Q.clePseudo('Ζέφυρος'), ''); assert.notEqual(Q.clePseudo('نجمة'), '');
  assert.notEqual(Q.clePseudo('Кобальт'), Q.clePseudo('Ζέφυρος')); assert.notEqual(Q.clePseudo('نجمة'), Q.clePseudo('نور'));
});
essai('pseudo : mélange d\'écritures refusé, sosies ramenés à la même clé', () => {
  const a = String.fromCharCode(0x430), o = String.fromCharCode(0x43E); // а et о cyrilliques
  assert.equal(Q.filtrerPseudo('Kob' + a + 'lt').ok, false);           // un double visuel de « Kobalt »
  assert.equal(Q.clePseudo(String.fromCharCode(0x410, 0x412, 0x421)), Q.clePseudo('ABC')); // « АВС » tout cyrillique
  assert.equal(Q.clePseudo(String.fromCharCode(0x391, 0x392, 0x395)), Q.clePseudo('abe')); // « ΑΒΕ » tout grec
  assert.equal(Q.clePseudo('c' + o + 'l'), Q.clePseudo('col'));
});
essai('stockage : une entrée « eleve » périmée ou mal formée est effacée', () => {
  const m = new Map();
  globalThis.localStorage = { getItem: k => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: k => m.delete(k),
    key: i => [...m.keys()][i] ?? null, get length() { return m.size; } };
  const t = Date.now();
  m.set('quizz-nsi:eleve', JSON.stringify({ id: '0123456789abcdef', pseudo: 'Ixo', code: 'ABCD', jusqua: t - 1 }));
  assert.equal(Q.menage(t), true); assert.equal(m.has('quizz-nsi:eleve'), false);
  m.set('quizz-nsi:eleve', '{pas du json'); Q.menage(t); assert.equal(m.has('quizz-nsi:eleve'), false);
  m.set('quizz-nsi:eleve', JSON.stringify({ jusqua: t + 400 * 24 * 3600 * 1000 })); Q.menage(t); assert.equal(m.has('quizz-nsi:eleve'), false); // plus de 12 h : impossible
  m.set('quizz-nsi:eleve', JSON.stringify({ jusqua: t + 3600 * 1000 })); assert.equal(Q.menage(t), false); assert.equal(m.has('quizz-nsi:eleve'), true);
  // l'historique de séance suit les mêmes règles
  m.set('quizz-nsi:hist:0123456789abcdef', JSON.stringify({ id: '0123456789abcdef', jusqua: t - 1, ordre: [] })); Q.menage(t); assert.equal(m.has('quizz-nsi:hist:0123456789abcdef'), false);
  m.set('quizz-nsi:hist:0123456789abcdef', JSON.stringify({ id: 'autre', jusqua: t + 1000 })); Q.menage(t); assert.equal(m.has('quizz-nsi:hist:0123456789abcdef'), false);
  m.set('quizz-nsi:hist:0123456789abcdef', JSON.stringify({ id: '0123456789abcdef', jusqua: t + 1000 })); Q.menage(t); assert.equal(m.has('quizz-nsi:hist:0123456789abcdef'), true);
  m.set('quizz-nsi:theme', '"dark"'); Q.menage(t); assert.equal(m.has('quizz-nsi:theme'), true); // les réglages ne sont pas concernés
  delete globalThis.localStorage;
});
essai('code de séance : lecture tolérante', () => {
  assert.equal(Q.lireCode(' abcd '), 'ABCD'); assert.equal(Q.lireCode('ab-cd'), 'ABCD');
  assert.equal(Q.lireCode('ABIO'), null); assert.equal(Q.lireCode('ABC'), null);
  for (let i = 0; i < 50; i++) assert.ok(Q.lireCode(Q.nouveauCode()));
});
essai('texte : tout est échappé', () => {
  assert.equal(Q.texte('<img src=x onerror=alert(1)>'), '&lt;img src=x onerror=alert(1)&gt;');
  assert.ok(!Q.texte('`<script>`').includes('<script>'));
  assert.equal(Q.texte('**gras** et *it*'), '<strong>gras</strong> et <em>it</em>');
});
essai('coloration : mots-clés, chaînes, nombres, échappement', () => {
  const h = Q.colorerLigne('if x == "<b>": return 3 # fin');
  assert.ok(h.includes('<span class="c-mot">if</span>'));
  assert.ok(h.includes('<span class="c-ch">&quot;&lt;b&gt;&quot;</span>'));
  assert.ok(h.includes('<span class="c-nb">3</span>'));
  assert.ok(h.includes('<span class="c-com"># fin</span>'));
});
essai('schéma svg brut : script refusé', () => {
  assert.ok(!Q.schema({ type: 'svg', code: '<svg onload="alert(1)"></svg>' }).includes('onload'));
  assert.ok(Q.schema({ type: 'pile', elements: ['<a>'] }).includes('&lt;a&gt;'));
});
essai('schémas Python : les valeurs comme repr', () => {
  assert.equal(Q.enPython([1, 'chat', 2.36, 'a', true, false, null]), '[1, "chat", 2.36, "a", True, False, None]');
  const h = Q.schema({ type: 'liste', elements: ['a', true] });
  assert.ok(h.includes('&quot;a&quot;') && h.includes('True') && !h.includes('>true<'));
  assert.ok(Q.schema({ type: 'pile', elements: ['copie 1'] }).includes('>copie 1<')); // une étiquette reste sans guillemets
});
essai('contrôle léger d\'un cours', () => {
  const c = JSON.parse(require('node:fs').readFileSync(path.join(__dirname, '..', 'cours', 'piles-files.json'), 'utf8'));
  assert.deepEqual(Q.controlerCours(c), []);
  c.diapositives.find(d => d.type === 'question').options[0].juste = true;
  assert.equal(Q.controlerCours(c).length, 1);
});
console.log(n + ' tests réussis');
