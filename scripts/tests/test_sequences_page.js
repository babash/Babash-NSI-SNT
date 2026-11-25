#!/usr/bin/env node
/* Tests du rendu des séquences (assets/sequences.js, T153), sans navigateur : un petit DOM imité suffit.
   Usage (depuis la racine du dépôt) : node scripts/tests/test_sequences_page.js
   - « Pour la classe » : pour une séquence publiée, « le QR code ouvre cette page » ; pour un brouillon, le texte dit
     que le QR code ne mènera à la page qu'une fois la séquence publiée (le lien donné n'a jamais ?brouillons) ;
   - une étape sans ressource visible des élèves est « À venir. », sans lien ;
   - un document caché aux élèves (cache_eleves) n'est jamais le lien principal ;
   - « avant » et « après » sur la fiche d'une ressource ; la séquence principale d'abord.
   Code de retour : 0 si tous les cas passent, 1 sinon. */
'use strict';
const path = require('path');
const vm = require('vm');
const fs = require('fs');

/* ── Un DOM imité : des nœuds avec leurs enfants, leurs attributs et leur texte ── */
function Noeud(tag) { this.tag = tag; this.attrs = {}; this.children = []; this.hidden = false; this.textContent = ''; }
Noeud.prototype.appendChild = function (n) {
  if (n && n.tag === '#fragment') n.children.forEach((c) => this.children.push(c));
  else this.children.push(n);
  return n;
};
Noeud.prototype.setAttribute = function (k, v) { this.attrs[k] = v; };
Noeud.prototype.getAttribute = function (k) { return this.attrs[k]; };
Noeud.prototype.addEventListener = function () {};
Object.defineProperty(Noeud.prototype, 'innerHTML', { set(v) { this._html = v; }, get() { return this._html || ''; } });
function texte(n) {
  if (n == null) return '';
  if (typeof n === 'string') return n;
  if (n.tag === '#texte') return n.textContent;
  return n.children.map(texte).join('');
}
function tous(n, f, out) {
  out = out || [];
  if (n && typeof n === 'object') { if (f(n)) out.push(n); (n.children || []).forEach((c) => tous(c, f, out)); }
  return out;
}
const document = {
  head: new Noeud('head'),
  createElement: (t) => new Noeud(t),
  createTextNode: (s) => { const n = new Noeud('#texte'); n.textContent = s; return n; },
  createDocumentFragment: () => new Noeud('#fragment'),
  getElementById: () => null
};
function el(tag, attrs, enfants) {
  const n = new Noeud(tag);
  Object.keys(attrs || {}).forEach((k) => { if (attrs[k] != null && attrs[k] !== false) n.attrs[k] = attrs[k]; });
  [].concat(enfants == null ? [] : enfants).forEach((c) => {
    if (c == null || c === false) return;
    n.appendChild(typeof c === 'object' ? c : document.createTextNode(String(c)));
  });
  return n;
}
const RACINE = 'https://exemple.test/site/';
const O = {
  el, racine: RACINE, surDisque: false,
  urlBibliotheque: (q) => RACINE + 'bibliotheque/' + (q || ''),
  urlRubrique: (r) => r.base,
  analyser: (lien) => ({ href: new URL(lien, RACINE).href, interne: lien.indexOf(RACINE) === 0, type: lien.indexOf(RACINE) === 0 ? 'Sur ce site' : 'ailleurs.test' }),
  lienVers: (info, t, classe) => el('a', { href: info.href, class: classe }, t)
};
const fenetre = { document, location: { href: RACINE + 'nsi-terminale/?sequence=s1', search: '?sequence=s1' }, URL, URLSearchParams, navigator: {}, Promise, console };
fenetre.window = fenetre;
vm.createContext(fenetre);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', '..', 'assets', 'sequences.js'), 'utf8'), fenetre);
const S = fenetre.Sequences;

/* ── Les données d'essai ── */
function fiche(id, docs) { return { id, titre: 'Titre ' + id, documents: docs }; }
const doc = (f, extra) => Object.assign({ role: 'enonce', fichier: f, format: 'page-web' }, extra || {});
const bib = {
  referentiels: {
    valeurs: { niveaux: [{ id: 'terminale', libelle: 'Terminale' }], roles: [{ id: 'enonce', libelle: 'Énoncé' }, { id: 'corrige', libelle: 'Corrigé' }] },
    sequences: { etapes: [{ id: 'td', libelle: 'TD' }, { id: 'tp-activites', libelle: 'TP et activités' }, { id: 'controle', libelle: 'Contrôle' }] }
  },
  ressources: [
    fiche('a', [doc('a.html', { principal: true })]),
    fiche('b', [doc('b-corrige.pdf', { principal: true, role: 'corrige', cache_eleves: true }), doc('b.html')]),
    fiche('c', [doc('c.html', { principal: true, cache_eleves: true })])
  ],
  sequences: [
    { id: 's1', niveau: 'terminale', titre: 'Publiée', objectif: 'Objectif', rang: 10, statut: 'publiee', rubrique: 'nsi-terminale',
      etapes: [{ type: 'td', ressources: [{ ressource: 'a' }] }, { type: 'tp-activites', ressources: [{ ressource: 'c' }] },
        { type: 'controle', ressources: [{ ressource: 'b' }] }] },
    { id: 's2', niveau: 'terminale', titre: 'Brouillon', objectif: 'Objectif', rang: 20, statut: 'brouillon', rubrique: 'nsi-terminale',
      etapes: [{ type: 'td', ressources: [{ ressource: 'a', secondaire: true }] }] }
  ]
};

let echecs = 0, n = 0;
function cas(titre, ok, detail) {
  n++;
  console.log((ok ? '  ok     ' : '  ÉCHEC  ') + titre + (ok ? '' : ' : ' + (detail || '')));
  if (!ok) echecs++;
}

const m = new S.Modele(bib, { brouillons: true });
const R = new S.Rendu(m, O);
const rub = { nom: 'NSI Terminale', base: RACINE + 'nsi-terminale/' };

const pub = R.partage(m.parId.s1);
const aidePub = texte(tous(pub, (x) => (x.attrs.class || '').indexOf('sequence-partage-aide') >= 0)[0]);
cas('publiée : « le QR code ouvre cette page »', /QR code ouvre cette page/.test(aidePub), aidePub);
const brou = R.partage(m.parId.s2);
const aideBrou = texte(tous(brou, (x) => (x.attrs.class || '').indexOf('sequence-partage-aide') >= 0)[0]);
cas('brouillon : le QR code ne mènera à la page qu\'une fois publiée', /^Brouillon : ce QR code mènera à cette page quand la séquence sera publiée\.$/.test(aideBrou), aideBrou);
const liens = tous(brou, (x) => x.tag === 'a').map((a) => a.attrs.href);
cas('brouillon : le lien pour la classe n\'a pas ?brouillons', liens.length === 1 && !/brouillons/.test(liens[0]) && /sequence=s2$/.test(liens[0]), liens.join(' '));

const page = R.page(m.parId.s1, rub);
const etapes = tous(page, (x) => (x.attrs.class || '').split(' ').indexOf('etape') >= 0);
const tp = etapes.filter((e) => e.attrs['data-etape'] === 'tp-activites')[0];
cas('étape dont la seule ressource est cachée aux élèves : « À venir. », sans lien',
  /À venir\./.test(texte(tp)) && tous(tp, (x) => x.tag === 'a').length === 0, texte(tp));
const controle = etapes.filter((e) => e.attrs['data-etape'] === 'controle')[0];
const titreB = tous(controle, (x) => x.tag === 'a' && x.attrs.class === 'titre')[0];
cas('document principal caché aux élèves : le premier visible s\'ouvre', titreB && /b\.html$/.test(titreB.attrs.href), titreB && titreB.attrs.href);
cas('un document caché aux élèves n\'est jamais montré', !tous(page, (x) => x.tag === 'a' && /corrige/.test(x.attrs.href || '')).length);

const vs = m.voisins('a');
cas('voisins : la séquence principale d\'abord', vs.length === 2 && vs[0].sequence.id === 's1' && vs[0].principale && !vs[1].principale,
  vs.map((v) => v.sequence.id + ':' + v.principale).join(' '));
cas('voisins : « après » saute la ressource cachée aux élèves', vs[0].apres && vs[0].apres.vue.fiche.id === 'b' && !vs[0].avant,
  vs[0].apres && vs[0].apres.vue.fiche.id);

const public_ = new S.Modele(bib, { brouillons: false });
cas('sans ?brouillons : seulement les séquences publiées', public_.liste.length === 1 && public_.liste[0].id === 's1');

console.log('\n' + n + ' cas, ' + echecs + ' échec(s)');
process.exit(echecs ? 1 : 0);
