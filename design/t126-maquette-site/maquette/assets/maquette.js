/* Maquette T126 : le strict nécessaire pour que les cinq écrans fonctionnent sans le moteur du site.
   Affichage clair/obscur, bandeau et margouillat en rotation, recherche et filtres de la bibliothèque,
   des annales et de la rubrique, vue liste ou cartes. Le vrai site garde son moteur (assets/site.js). */
(function () {
  'use strict';
  var racine = document.documentElement;

  /* ── Affichage : Auto, Clair, Obscur (même clé « theme » que le site) ── */
  function lireTheme() { try { return localStorage.getItem('theme') || 'auto'; } catch (e) { return 'auto'; } }
  function ecrireTheme(t) { try { if (t === 'auto') localStorage.removeItem('theme'); else localStorage.setItem('theme', t); } catch (e) {} }
  function appliquer(t) {
    if (t === 'light' || t === 'dark') racine.setAttribute('data-theme', t); else racine.removeAttribute('data-theme');
    document.querySelectorAll('.barre-haut .mode-btn').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.theme === t)); });
  }
  document.querySelectorAll('.barre-haut .mode-btn').forEach(function (b) {
    b.addEventListener('click', function () { ecrireTheme(b.dataset.theme); appliquer(b.dataset.theme); });
  });
  appliquer(lireTheme());

  /* ── Bandeau en rotation (accueil, bibliothèque) et cachette du margouillat ── */
  var jour = Math.floor(Date.now() / 86400000);
  var params = new URLSearchParams(location.search);
  document.querySelectorAll('.bandeau[data-rotation]').forEach(function (b) {
    var n = params.get('bandeau') || String(jour % 4 + 1);
    b.setAttribute('data-bandeau', n);
  });
  var PLACES = window.PLACES_MARGOUILLAT || {};
  document.querySelectorAll('.bandeau .margouillat').forEach(function (m) {
    var n = m.closest('.bandeau').getAttribute('data-bandeau') || '1';
    var liste = PLACES[n] || [];
    if (!liste.length) return;
    var p = liste[(jour + n.charCodeAt(0)) % liste.length];
    m.style.setProperty('--x', p.x + '%'); m.style.setProperty('--y', p.y + '%');
    m.style.setProperty('--r', p.r + 'deg'); m.style.setProperty('--l', p.l + '%');
    if (p.s) m.style.setProperty('--s', p.s);
  });

  /* ── Normaliser pour chercher : sans accents ni majuscules ── */
  var DIACR = new RegExp('[' + String.fromCharCode(0x300) + '-' + String.fromCharCode(0x36f) + ']', 'g');
  function norm(s) { return (s || '').normalize('NFD').replace(DIACR, '').toLowerCase(); }

  /* ── Filtres (bibliothèque, annales) : cases à cocher + recherche ── */
  var liste = document.querySelector('.resultats');
  var champ = document.getElementById('recherche');
  var compte = document.querySelector('.compte');
  var nomCompte = compte ? compte.textContent.replace(/^[\d\s]+/, '') : '';
  function filtrer() {
    var items = liste ? liste.querySelectorAll('.res') : document.querySelectorAll('.zone .res');
    var mots = norm(champ && champ.value).split(/\s+/).filter(Boolean);
    var coches = {};
    document.querySelectorAll('.filtre-case input:checked').forEach(function (c) {
      var m = /^f-([a-z]+)-(.+)$/.exec(c.id); if (!m) return;
      (coches[m[1]] = coches[m[1]] || []).push({ v: m[2], nom: norm(c.closest('label').querySelector('.filtre-nom').textContent) });
    });
    var n = 0;
    items.forEach(function (li) {
      var ok = mots.every(function (w) { return norm(li.textContent).indexOf(w) >= 0; });
      Object.keys(coches).forEach(function (cle) {
        if (!ok) return;
        if (cle === 'chapitre') { // annales : le chapitre est écrit sur l'exercice
          var puces = Array.prototype.map.call(li.querySelectorAll('.puces-exercice .puce'), function (p) { return norm(p.textContent); });
          ok = coches[cle].some(function (c) { return puces.indexOf(c.nom) >= 0; });
          return;
        }
        var d = li.getAttribute('data-' + cle);
        if (d === null) return; // facette que la maquette ne sait pas filtrer
        var vals = d.split(' ');
        ok = coches[cle].some(function (c) {
          return vals.some(function (v) { return v === c.v || v.indexOf(c.v + '.') === 0; });
        });
      });
      li.hidden = !ok; if (ok) n++;
    });
    if (compte) compte.textContent = n + ' ' + nomCompte.trim().replace(/^ressources?$/, n > 1 ? 'ressources' : 'ressource');
    var st = document.querySelector('.cherche .statut');
    if (st) st.textContent = (mots.length || Object.keys(coches).length) ? n + ' résultat' + (n > 1 ? 's' : '') : '';
    // rubrique : cacher les thèmes et sous-thèmes devenus vides
    document.querySelectorAll('.zone .theme').forEach(function (t) {
      t.hidden = mots.length > 0 && !t.querySelector('.res:not([hidden])');
    });
  }
  document.querySelectorAll('.filtre-case input').forEach(function (c) { c.addEventListener('change', filtrer); });
  if (champ) champ.addEventListener('input', filtrer);
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && champ && document.activeElement !== champ && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); champ.focus(); }
  });
  // annales : un clic sur un chapitre coche son filtre
  document.querySelectorAll('.puces-exercice .puce').forEach(function (p) {
    p.addEventListener('click', function () {
      document.querySelectorAll('.filtre-case').forEach(function (l) {
        if (norm(l.querySelector('.filtre-nom').textContent) === norm(p.textContent)) { l.querySelector('input').checked = true; }
      });
      filtrer(); window.scrollTo({ top: liste.offsetTop - 16 });
    });
  });

  /* ── Vue liste ou cartes ── */
  document.querySelectorAll('.outils-resultats .mode-btn').forEach(function (b, i, tous) {
    b.addEventListener('click', function () {
      tous.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      if (liste) liste.classList.toggle('en-cartes', i === 1);
    });
  });

  /* ── Tri (bibliothèque : titre ou niveau ; annales : date ou points) ── */
  var tri = document.getElementById('tri');
  if (tri && liste) tri.addEventListener('change', function () {
    var items = Array.prototype.slice.call(liste.children);
    var cle = function (li) {
      var t = li.querySelector('.titre').textContent;
      if (tri.value === 'points') return -parseFloat((li.querySelector('.chemin') || {}).textContent) || 0;
      if (tri.value === 'ancien') return t;
      if (tri.value === 'recent') return -parseInt(t, 10) || 0;
      if (tri.value === 'niveau') return li.getAttribute('data-niv') || '';
      return norm(t);
    };
    items.sort(function (a, b) { var x = cle(a), y = cle(b); return x < y ? -1 : x > y ? 1 : 0; });
    items.forEach(function (li) { liste.appendChild(li); });
  });

  /* ── Filtres repliés sur téléphone ── */
  if (window.matchMedia('(max-width: 900px)').matches) {
    document.querySelectorAll('details.filtres, details.sommaire').forEach(function (d) { d.open = false; });
  }

  /* ── Sommaire de la rubrique : le thème lu est marqué ── */
  var liens = document.querySelectorAll('.sommaire a[href^="#"]');
  if (liens.length && 'IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (en) {
        if (!en.isIntersecting) return;
        liens.forEach(function (a) { if (a.getAttribute('href') === '#' + en.target.id) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
      });
    }, { rootMargin: '0px 0px -70% 0px' });
    document.querySelectorAll('.zone .theme').forEach(function (t) { obs.observe(t); });
  }
})();
