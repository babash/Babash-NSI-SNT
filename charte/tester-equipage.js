#!/usr/bin/env node
/* Essais du moteur d'avatars (assets/equipage.js), sans navigateur (T133b, Designer).

   Usage (à la racine du dépôt) :  node charte/tester-equipage.js [--reference FICHIER]

   1. Rien ne change pour l'existant : mêmes images (au caractère près) que le moteur de
      référence (main avant T133b, commit 0b44455, lu par git ; ou --reference) pour les modèles,
      300 avatars au hasard, tous les états et les trois cadres ; mêmes tirages au hasard.
   2. Les 15 objets des applications : famille « applis », haut fait, dessin visible, accroché
      au corps (l'objet tenu suit la main, le chapeau suit la tête qui se baisse).
   3. Les états d'usage, les gestes, les 20 phrases (liste fermée, gelée), l'avatar neutre.
   4. Les fichiers de données (catalogue.json, applis.json) sont à jour.
   L'interface dans une page (bulles, marques, plafond, calme, pause) : charte/tester-applis.py. */
'use strict';
var fs = require('fs'), path = require('path'), os = require('os'), cp = require('child_process');
var racine = path.resolve(__dirname, '..');
var E = require(path.join(racine, 'assets', 'equipage.js'));
var REF_COMMIT = '0b44455';
var echecs = 0, essais = 0;
function ok(cond, msg) { essais += 1; if (!cond) { echecs += 1; console.error('ÉCHEC : ' + msg); } }

/* ── 1. l'existant ── */
var refChemin = null, i = process.argv.indexOf('--reference');
if (i > 0) refChemin = path.resolve(process.argv[i + 1]);
else {
  try {
    var src = cp.execSync('git show ' + REF_COMMIT + ':assets/equipage.js', { cwd: racine, stdio: ['ignore', 'pipe', 'ignore'] });
    refChemin = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'equipage-ref-')), 'equipage.js');
    fs.writeFileSync(refChemin, src);
  } catch (e) { console.log('(référence ' + REF_COMMIT + ' introuvable : comparaison à l\'existant sautée)'); }
}
if (refChemin) {
  var R = require(refChemin);
  var etats = R.ETATS.map(function (e) { return e.id; });
  /* objets retirés à la demande de l'enseignant (24/11) : une description qui les porte les perd */
  var RETIRES = { 'main:perche_extensible': 1, 'tete:bouchon_mamoudzou': 1 };
  function sansRetires(d) { d = JSON.parse(JSON.stringify(d)); Object.keys(d.objets || {}).forEach(function (e) { if (RETIRES[e + ':' + d.objets[e]]) d.objets[e] = 'aucun'; }); return d; }
  function porteRetire(d) { return Object.keys(d.objets).some(function (e) { return RETIRES[e + ':' + d.objets[e]]; }); }
  var descs = Object.keys(R.modeles).map(function (k) { return R.modeles[k].description; });
  for (var g = 0; g < 300; g++) descs.push(R.aleatoire(g * 7919 + 13));
  var nRet = descs.filter(porteRetire).length;
  descs = descs.filter(function (d) { return !porteRetire(d); });
  console.log('(' + nRet + ' avatars de référence portaient un objet retiré : écartés de la comparaison au caractère près)');
  var diff = 0, n = 0;
  descs.forEach(function (d, k) {
    ok(JSON.stringify(E.normaliser(d)) === JSON.stringify(R.normaliser(d)), 'normaliser change la description ' + k);
    var tailles = k < 40 ? [24, 48, 112] : [112];
    var et = k < 60 ? etats : [etats[k % etats.length]];
    tailles.forEach(function (t) {
      et.forEach(function (e) {
        var o = { taille: t, etat: e, decalage: 0 };
        n += 1; if (E.svg(d, o) !== R.svg(d, o)) diff += 1;
      });
    });
  });
  ok(diff === 0, diff + ' images sur ' + n + ' diffèrent du moteur de référence');
  console.log('Existant : ' + n + ' images comparées, ' + diff + ' différence(s).');
  for (g = 0; g < 500; g++) ok(JSON.stringify(E.aleatoire(g)) === JSON.stringify(R.normaliser(sansRetires(R.aleatoire(g)))), 'aleatoire(' + g + ') a changé');
  ok(E.normaliser({ objets: { main: 'perche_extensible', tete: 'bouchon_mamoudzou' } }).objets.main === 'aucun', 'objets retirés refusés');
  ok(E.texte(descs[0], 'repos') === R.texte(descs[0], 'repos'), 'texte a changé');
  ['tete', 'visage', 'cou', 'dos', 'main', 'epaule', 'pieds', 'autour'].forEach(function (e) {
    var avant = R.catalogue.objets[e].map(function (o) { return o.id; }).join();
    var apres = E.catalogue.objets[e].filter(function (o) { return o.famille !== 'applis' && o.famille !== 'fidelite' && o.id !== 'bouteille_percee' && o.id !== 'dessin_karim'; }).map(function (o) { return o.id; }).join();
    avant = R.catalogue.objets[e].filter(function (o) { return !RETIRES[e + ':' + o.id]; }).map(function (o) { return o.id; }).join();
    ok(avant === apres, 'les objets « ' + e + ' » existants ont changé');
  });
}

/* ── 2. les 15 objets des applications ── */
var nu = E.normaliser({ teint: 5, coiffure: 'puffs', haut: 'veste' });
function avec(emp, id) { var d = JSON.parse(JSON.stringify(nu)); d.objets[emp] = id; return E.normaliser(d); }
function image(d, etat) { return E.svg(d, { taille: 112, etat: etat, anime: false, compagnon: false, alt: '' }); }
ok(E.applis.length === 15, '15 objets attendus, ' + E.applis.length + ' trouvés');
var parAppli = {};
E.applis.forEach(function (a) {
  parAppli[a.application] = (parAppli[a.application] || 0) + 1;
  ok(/^[a-z0-9_]{1,40}$/.test(a.id), 'identifiant illisible : ' + a.id);
  ok(/^[a-z0-9-]{1,60}$/.test(a.haut_fait), 'haut fait illisible : ' + a.haut_fait);
  var c = E.catalogue.objets[a.emplacement].filter(function (o) { return o.id === a.id; })[0];
  ok(c && c.famille === 'applis' && c.application === a.application && c.haut_fait === a.haut_fait, a.id + ' absent du catalogue ou mal rangé');
  ok(E.normaliser(avec(a.emplacement, a.id)).objets[a.emplacement] === a.id, 'normaliser refuse ' + a.id);
  ['repos', 'tres_content', 'salue', 'concentre', 'dort'].forEach(function (e) {
    /* concentré·e : les deux mains tiennent la tablette, l'objet tenu est rangé (comme tous les objets tenus) */
    if (a.emplacement === 'main' && e === 'concentre') return;
    ok(image(avec(a.emplacement, a.id), e) !== image(nu, e), a.id + ' invisible dans l\'état ' + e);
  });
});
ok(Object.keys(parAppli).sort().join() === 'calendrier,gombessa,grand_oral,lagon,quizz_nsi' &&
  Object.keys(parAppli).every(function (k) { return parAppli[k] === 3; }), 'il faut 3 objets par application : ' + JSON.stringify(parAppli));
/* l'objet tenu suit la main : sa position change quand le bras se lève */
E.applis.filter(function (a) { return a.emplacement === 'main'; }).forEach(function (a) {
  var bas = image(avec('main', a.id), 'repos').replace(image(nu, 'repos'), '');
  ok(image(avec('main', a.id), 'repos') !== image(avec('main', a.id), 'tres_content'), a.id + ' ne suit pas le bras');
  ok(bas !== '', a.id + ' ne change rien');
});
/* aucun objet des applications ne sort au hasard */
for (var s = 0; s < 400; s++) {
  var d = E.aleatoire(s);
  E.applis.concat(E.fidelite, [{ id: 'bouteille_percee', emplacement: 'main' }, { id: 'dessin_karim', emplacement: 'main' }]).forEach(function (a) { ok(d.objets[a.emplacement] !== a.id, 'aleatoire(' + s + ') donne ' + a.id); });
}

/* ── 3. états d'usage, gestes, phrases, neutre ── */
var ref = E.normaliser({ teint: 3 });
[['lobby', 'repos'], ['attente', 'concentre'], ['repondu', 'repos'], ['fete', 'tres_content'], ['applaudit', 'content']].forEach(function (p) {
  ok(E.svg(ref, { etat: p[0], decalage: 0, alt: '' }) === E.svg(ref, { etat: p[1], decalage: 0, alt: '' }), 'l\'état ' + p[0] + ' n\'est pas ' + p[1]);
});
ok(E.gestes.map(function (g) { return g.id; }).join() === 'salue,saute,rit,sieste,tempete', 'les cinq gestes');

/* T133c : la bouteille d'eau percée, le geste « tempête », les objets de fidélité */
var bt = avec('main', 'bouteille_percee');
var cb = E.catalogue.objets.main.filter(function (o) { return o.id === 'bouteille_percee'; })[0];
ok(cb && cb.famille === 'lycee' && E.normaliser(bt).objets.main === 'bouteille_percee', 'bouteille_percee au catalogue (famille lycee)');
ok(image(bt, 'repos').indexOf('#4ab8f0') < 0, 'bouteille : pas de jet au repos');
['salue', 'tres_content', 'content'].forEach(function (e) { ok(image(bt, e).indexOf('#4ab8f0') > 0, 'bouteille : un jet pendant le geste ' + e); });
ok(E.gestes[4].etat === 'tempete' && E.gestes[4].duree >= 1500 && E.gestes[4].duree <= 2000, 'tempête : 1,5 à 2 s');
var tp = E.svg(nu, { etat: 'tempete', decalage: 0, alt: '' }), nimg = (tp.match(/class="eq-img/g) || []).length;
ok(nimg >= 4, 'tempête : au moins 4 images (' + nimg + ')');
ok(E.svg(nu, { etat: 'tempete', anime: false, alt: '' }) !== E.svg(nu, { etat: 'repos', anime: false, alt: '' }), 'tempête : l\'image fixe garde le tourbillon');
ok(/tourbillonne/.test(E.texte(nu, 'tempete')), 'tempête : texte alternatif');
ok(E.fidelite.length === 4 && E.fidelite.map(function (f) { return f.emplacement + ':' + f.id; }).join() === 'autour:aura_etincelle,autour:aura_halo,autour:aura_supernova,dos:ailes_circuit', 'les 4 objets de fidélité');
var auras = ['aura_etincelle', 'aura_halo', 'aura_supernova'].map(function (id) { var im = image(avec('autour', id), 'repos'); ok(E.catalogue.objets.autour.some(function (o) { return o.id === id && o.famille === 'fidelite'; }), id + ' au catalogue'); return im; });
ok(auras[0] !== auras[1] && auras[1] !== auras[2] && auras[0].length < auras[1].length && auras[1].length < auras[2].length, 'les trois auras grandissent d\'un palier à l\'autre');
ok(image(avec('dos', 'ailes_circuit'), 'repos') !== image(nu, 'repos'), 'ailes de circuit visibles');
ok(E.catalogue.objets.main.some(function (o) { return o.id === 'dessin_karim' && o.famille === 'classe'; }), 'dessin_karim : trophée de la famille classe');
ok(image(avec('main', 'dessin_karim'), 'repos') !== image(nu, 'repos') && image(avec('main', 'dessin_karim'), 'fete') !== image(nu, 'fete'), 'dessin_karim visible');
ok(E.phrases.length === 21 && Object.isFrozen(E.phrases), '21 phrases gelées');
ok(!E.phrases.some(function (p) { return /bouchon/i.test(p); }), 'plus de bouchon dans les phrases');
E.adresse('madame'); ok(E.phrase(19) === 'Ne vous inquiétez pas, Madame.', 'variante Madame');
E.adresse('monsieur'); ok(E.phrase(19) === 'Ne vous inquiétez pas, Monsieur.' && E.phrase(99) === null, 'variante Monsieur, numéro inconnu');
ok(E.phrases.every(function (p) { return typeof p === 'string' && p.length > 0 && p.length <= 48 && !/[<>&]/.test(p); }), 'phrases courtes, sans balise');
var N = E.neutre();
ok(N.lignee === 'esprit' && N.coiffure === 'capuche' && JSON.stringify(N) === JSON.stringify(E.neutre()), 'l\'Esprit en capuche, le même pour tous');
N.teint = 1; ok(E.neutre().teint !== 1 || E.neutre().lignee === 'esprit', 'neutre() renvoie une copie');
var t0 = Date.now(); for (var r = 0; r < 200; r++) E.svg(ref, { etat: 'repos', taille: 96 }); var t1 = Date.now() - t0;
ok(t1 < 2000, 'le cache des dessins ne sert pas (' + t1 + ' ms)');

/* clés héritées : jamais acceptées */
['constructor', 'toString', '__proto__', 'hasOwnProperty', 'valueOf'].forEach(function (k) {
  var d = E.normaliser({ couleurs: { haut: k, accent: k, yeux: k }, cheveux: k, objets: { main: k, tete: k }, compagnon: k, lignee: k });
  ok(d.couleurs.haut === 'canard' && d.couleurs.accent === 'cyan' && d.cheveux === 'noirs' && d.objets.main === 'aucun' && d.compagnon === 'margouillat' && d.lignee === 'humain', 'normaliser accepte la clé héritée ' + k);
  E.adresse(k); ok(E.adresse() === 'monsieur' && E.phrase(19) === 'Ne vous inquiétez pas, Monsieur.', 'adresse accepte ' + k);
  ok(E.svg(ref, { etat: k, decalage: 0, alt: '' }) === E.svg(ref, { etat: 'repos', decalage: 0, alt: '' }), 'état ' + k + ' : repos attendu');
  ok(E.svg(ref, { cadre: k, decalage: 0, alt: '' }) === E.svg(ref, { decalage: 0, alt: '' }), 'cadre ' + k);
  ok(E.compagnonSVG(k) === '' && E.phrase(k) === null, 'compagnon ou phrase ' + k);
  ok(E.margouillatSVG({ bord: k, etat: k, anime: false }).indexOf('<svg') === 0, 'margouillat ' + k);
});

/* ── 4. fichiers de données ── */
try { cp.execFileSync(process.execPath, [path.join(__dirname, 'equipage-donnees.js'), '--verifier'], { stdio: 'pipe' }); ok(true, ''); }
catch (e) { ok(false, String(e.stderr || e.message).trim()); }
var J = JSON.parse(fs.readFileSync(path.join(racine, 'assets', 'equipage', 'applis.json'), 'utf8'));
ok(J.phrases.map(function (p) { return p.texte; }).join('|') === E.phrases.join('|'), 'applis.json : phrases');

console.log(essais + ' essais, ' + echecs + ' échec(s).');
process.exit(echecs ? 1 : 0);
