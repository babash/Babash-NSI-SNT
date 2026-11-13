/* ═══════════════════════════════════════════════════════════════
   La bibliothèque : toutes les ressources visibles de l'extérieur,
   avec une recherche par mots-clés et par notions, des filtres sur
   tous les classements, deux vues (liste, cartes) et la fiche
   complète de chaque ressource (?r=identifiant).

   Données : donnees/bibliotheque.json, construit à chaque
   publication à partir des fiches (scripts/construire_bibliotheque.py),
   et donnees/bibliotheque-textes.json (texte des documents hébergés),
   chargé à la première recherche.
   L'adresse garde la recherche, les filtres, le tri et la vue :
   elle se partage telle quelle.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var R = window.Recherche;
  var O = null;               // les outils de site.js (el, barreHaut, piedDePage…)
  var bib = null;             // bibliotheque.json
  var refs = null;            // les référentiels, par identifiant
  var index = null;           // l'index de recherche
  var fiches = [], parId = {};
  var derive = {};            // id → valeurs de chaque filtre (calculées une fois)
  var textes = { etat: 'absent' };
  var PAR_PAGE = 30;
  var COULEUR = '#22D3EE';

  var etat = { q: '', filtres: {}, tri: '', vue: 'liste', r: '', nombre: PAR_PAGE };
  var ui = {};                // éléments de la page
  var ouverts = {};           // branches dépliées des filtres en arbre
  var minuterie = null;

  /* ── Outils ─────────────────────────────────────────────────── */

  function el(tag, attrs, enfants) { return O.el(tag, attrs, enfants); }

  function libelle(liste, id) {
    var v = refs.valeurs[liste] && refs.valeurs[liste][id];
    return v ? v.libelle : id;
  }

  function court(liste, id) {
    var v = refs.valeurs[liste] && refs.valeurs[liste][id];
    return v ? (v.court || v.libelle) : id;
  }

  function unique(t) {
    return t.filter(function (x, i) { return x != null && t.indexOf(x) === i; });
  }

  /* Un texte avec ses mots trouvés surlignés (<mark>), sans jamais passer par du HTML */
  function surligne(texte, trouves) {
    if (!trouves || !trouves.length) return document.createTextNode(texte || '');
    var f = document.createDocumentFragment();
    R.surligner(texte, trouves).forEach(function (m) {
      f.appendChild(m.marque ? el('mark', null, m.texte) : document.createTextNode(m.texte));
    });
    return f;
  }

  /* Un texte long de fiche : `code`, **gras** et retours à la ligne, plus le surlignage */
  function texteRiche(texte, trouves) {
    var f = document.createDocumentFragment();
    String(texte || '').split('\n').forEach(function (ligne, i) {
      if (i) f.appendChild(el('br'));
      ligne.split(/(`[^`]+`|\*\*[^*]+\*\*)/).forEach(function (m) {
        if (!m) return;
        if (/^`[^`]+`$/.test(m)) f.appendChild(el('code', null, m.slice(1, -1)));
        else if (/^\*\*[^*]+\*\*$/.test(m)) { var s = el('strong'); s.appendChild(surligne(m.slice(2, -2), trouves)); f.appendChild(s); }
        else f.appendChild(surligne(m, trouves));
      });
    });
    return f;
  }

  function urlFichier(chemin) {
    return O.racine + chemin;
  }

  /* L'adresse d'un document : un fichier du site ou un lien externe */
  function infoDocument(d) {
    return O.analyser(d.url || urlFichier(d.fichier), O.racine);
  }

  /* La couleur d'une ressource : celle de sa rubrique */
  function couleurDe(f) {
    var ens = f.enseignements || [], niv = f.niveaux || [];
    if (ens.indexOf('snt') >= 0) return O.couleur('bleu');
    if (ens.indexOf('nsi') >= 0) return O.couleur(niv.indexOf('premiere') >= 0 && niv.indexOf('terminale') < 0 ? 'violet' : 'orange');
    if (ens.indexOf('pp') >= 0) return O.couleur('vert');
    return O.couleur('jaune');
  }

  /* ── Les durées ─────────────────────────────────────────────── */

  var DUREES = [
    { id: 'courte', libelle: '30 min ou moins', min: 0, max: 30 },
    { id: 'seance', libelle: 'De 30 min à 1 h', min: 31, max: 60 },
    { id: 'longue', libelle: 'De 1 h à 2 h', min: 61, max: 120 },
    { id: 'plusieurs', libelle: 'Plus de 2 h', min: 121, max: Infinity },
    { id: 'inconnue', libelle: 'Non précisée' }
  ];

  /* « 1 h 30 » → [90, 90] ; « 15 min à 45 min » → [15, 45] ; « 2 séances » → [110, 110] (55 min la séance) */
  function minutes(texte) {
    var t = R.normaliser(texte), out = [], m;
    var motif = /(\d+)\s*(?:h|heures?)(?:\s*(\d+))?|(\d+)\s*min(?:utes?)?|(\d+)\s*seances?/g;
    while ((m = motif.exec(t))) {
      if (m[1]) out.push(60 * +m[1] + (m[2] ? +m[2] : 0));
      else if (m[3]) out.push(+m[3]);
      else if (m[4]) out.push(55 * +m[4]);
    }
    return out.length ? [Math.min.apply(null, out), Math.max.apply(null, out)] : null;
  }

  function dureesDe(f) {
    var m = f.duree ? minutes(f.duree) : null;
    if (!m) return ['inconnue'];
    return DUREES.filter(function (d) { return d.min !== undefined && d.min <= m[1] && m[0] <= d.max; })
      .map(function (d) { return d.id; });
  }

  /* ── Les filtres ────────────────────────────────────────────── */

  /* Chaque filtre : son nom dans l'adresse, son titre, les valeurs d'une ressource, leur libellé et leur ordre */
  function ordreReferentiel(liste) {
    var ids = Object.keys(refs.valeurs[liste] || {});
    return function (a, b) { return ids.indexOf(a) - ids.indexOf(b); };
  }

  function famille(id) {
    var u = refs.valeurs.usages[id];
    return u ? u.famille : '';
  }

  var FILTRES = [];

  function definirFiltres() {
    FILTRES = [
      { id: 'ens', titre: 'Enseignement', ouvert: true, valeurs: function (f) { return f.enseignements || []; },
        libelle: function (v) { return libelle('enseignements', v); }, ordre: ordreReferentiel('enseignements') },
      { id: 'niv', titre: 'Niveau', ouvert: true, valeurs: function (f) { return f.niveaux || []; },
        libelle: function (v) { return libelle('niveaux', v); }, ordre: ordreReferentiel('niveaux') },
      { id: 'prog', titre: 'Programme officiel', arbre: 'programme', valeurs: function (f) { return derive[f.id].programme; } },
      { id: 'notion', titre: 'Notions travaillées', arbre: 'notions', valeurs: function (f) { return derive[f.id].notions; },
        aide: 'Les fiches ne sont pas encore classées par notion.' },
      { id: 'type', titre: 'Type', ouvert: true, valeurs: function (f) { return f.types || []; },
        libelle: function (v) { return libelle('types', v); }, ordre: ordreReferentiel('types') },
      { id: 'usage', titre: 'Modalités', valeurs: function (f) { return (f.usages || []).filter(function (u) { return famille(u) === 'modalite'; }); },
        libelle: function (v) { return libelle('usages', v); }, ordre: ordreReferentiel('usages') },
      { id: 'prerequis', titre: 'Prérequis', valeurs: function (f) {
          var p = (f.usages || []).filter(function (u) { return famille(u) === 'prerequis'; });
          return p.length ? p : ['aucun'];
        },
        libelle: function (v) { return v === 'aucun' ? 'Aucun prérequis' : libelle('usages', v); },
        ordre: function (a, b) { return a === 'aucun' ? -1 : b === 'aucun' ? 1 : ordreReferentiel('usages')(a, b); } },
      { id: 'duree', titre: 'Durée', valeurs: function (f) { return derive[f.id].durees; },
        libelle: function (v) { return (DUREES.filter(function (d) { return d.id === v; })[0] || {}).libelle || v; },
        ordre: function (a, b) { return DUREES.map(function (d) { return d.id; }).indexOf(a) - DUREES.map(function (d) { return d.id; }).indexOf(b); } },
      { id: 'doc', titre: 'Documents', valeurs: function (f) { return unique(f.documents.map(function (d) { return d.role; })); },
        libelle: function (v) { return libelle('roles', v); }, ordre: ordreReferentiel('roles') },
      { id: 'format', titre: 'Formats', valeurs: function (f) { return unique(f.documents.map(function (d) { return d.format; })); },
        libelle: function (v) { return libelle('formats', v); }, ordre: ordreReferentiel('formats') },
      { id: 'lang', titre: 'Langages', valeurs: function (f) { return f.langages || []; },
        libelle: function (v) { return libelle('langages', v); }, ordre: ordreReferentiel('langages') },
      { id: 'donnees', titre: 'Données d\'élèves', valeurs: function (f) {
          var d = f.donnees_eleves || {};
          return [d.collecte ? (d.facultative ? 'facultative' : 'collecte') : 'aucune'];
        },
        libelle: function (v) { return { aucune: 'Aucune collecte', facultative: 'Collecte facultative', collecte: 'Collecte de données' }[v]; },
        ordre: function (a, b) { var o = ['aucune', 'facultative', 'collecte']; return o.indexOf(a) - o.indexOf(b); } },
      { id: 'orig', titre: 'Origine', valeurs: function (f) { return f.origine ? [f.origine] : []; },
        libelle: function (v) { return libelle('origines', v); }, ordre: ordreReferentiel('origines') },
      { id: 'auteur', titre: 'Autrices et auteurs', valeurs: function (f) { return unique((f.auteurs || []).map(function (a) { return a.nom; })); },
        libelle: function (v) { return v; }, ordre: null, limite: 12 },
      { id: 'pix', titre: 'Compétences Pix', valeurs: function (f) { return f.competences_pix || []; },
        libelle: function (v) { return refs.pix[v] ? refs.pix[v].libelle : v; },
        ordre: function (a, b) { return String((refs.pix[a] || {}).numero).localeCompare(String((refs.pix[b] || {}).numero)); } },
      { id: 'statut', titre: 'Statut de la fiche', valeurs: function (f) { return f.statut ? [f.statut] : []; },
        libelle: function (v) { return libelle('statuts', v); }, ordre: ordreReferentiel('statuts') }
    ];
  }

  /* Ce qu'on calcule une fois par ressource : programme et notions avec leurs ancêtres, durées */
  function deriver(f) {
    var prog = [];
    (f.programme || []).forEach(function (id) {
      var n = refs.noeuds[id];
      while (n) { prog.push(n.id); n = n.parent ? refs.noeuds[n.parent] : null; }
    });
    /* Le filtre « Notions travaillées » porte sur la liste des notions travaillées et leurs notions plus larges ;
       une notion prérequise est seulement citée (elle compte un peu dans la recherche, et dans « classée sous ») */
    var notions = [], cites = {};
    ['travaillees', 'prerequises'].forEach(function (role) {
      ((f.notions || {})[role] || []).forEach(function (nid) {
        cites[nid] = cites[nid] || role;
        if (role === 'travaillees') index.thesaurus.ascendance(nid).forEach(function (a) { notions.push(a); });
      });
    });
    derive[f.id] = { programme: unique(prog), notions: unique(notions), durees: dureesDe(f), cites: cites };
  }

  function filtreActif(id) {
    return (etat.filtres[id] || []).length > 0;
  }

  /* Les ressources qui passent la recherche et tous les filtres, sauf celui qu'on excepte */
  function passe(f, sauf) {
    return FILTRES.every(function (F) {
      if (F.id === sauf || !filtreActif(F.id)) return true;
      var vals = F.valeurs(f);
      return etat.filtres[F.id].some(function (v) { return vals.indexOf(v) >= 0; });
    });
  }

  /* ── L'état et l'adresse ────────────────────────────────────── */

  var TRIS = [
    { id: 'pertinence', libelle: 'Pertinence' },
    { id: 'titre', libelle: 'Titre (A à Z)' },
    { id: 'recent', libelle: 'Ajout le plus récent' },
    { id: 'niveau', libelle: 'Niveau' }
  ];

  function lireAdresse() {
    var p;
    try { p = new URLSearchParams(location.search); } catch (e) { p = { get: function () { return null; } }; }
    etat.q = p.get('q') || '';
    etat.r = p.get('r') || '';
    etat.vue = p.get('vue') === 'cartes' ? 'cartes' : 'liste';
    etat.tri = TRIS.some(function (t) { return t.id === p.get('tri'); }) ? p.get('tri') : '';
    etat.filtres = {};
    FILTRES.forEach(function (F) {
      var v = p.get(F.id);
      if (v) etat.filtres[F.id] = unique(v.split(',').filter(Boolean));
    });
    etat.nombre = PAR_PAGE;
  }

  function requeteAdresse(sans) {
    var p = new URLSearchParams();
    if (etat.q) p.set('q', etat.q);
    FILTRES.forEach(function (F) { if (filtreActif(F.id)) p.set(F.id, etat.filtres[F.id].join(',')); });
    if (etat.tri) p.set('tri', etat.tri);
    if (etat.vue !== 'liste') p.set('vue', etat.vue);
    if (etat.r && sans !== 'r') p.set('r', etat.r);
    var s = p.toString();
    return s ? '?' + s : '';
  }

  function ecrireAdresse(nouvelle) {
    try {
      var url = location.pathname + requeteAdresse();
      if (nouvelle) history.pushState(null, '', url); else history.replaceState(null, '', url);
    } catch (e) { /* adresse inchangée : sans importance */ }
  }

  function adresseFiche(id) {
    var garde = etat.r;
    etat.r = id;
    var s = requeteAdresse();
    etat.r = garde;
    return location.pathname + s;
  }

  /* ── La recherche ───────────────────────────────────────────── */

  var resultat = null; // le dernier résultat de recherche { parId: {id: r}, brut }

  function chercher() {
    if (!etat.q.trim()) { resultat = null; return; }
    var brut = index.chercher(etat.q);
    var par = {};
    brut.resultats.forEach(function (r, i) { r.rang = i; par[r.id] = r; });
    resultat = { brut: brut, parId: par };
    if (textes.etat === 'absent') chargerTextes();
  }

  function chargerTextes() {
    textes.etat = 'en cours';
    fetch(O.racine + 'donnees/bibliotheque-textes.json').then(function (r) {
      if (!r.ok) throw new Error('code ' + r.status);
      return r.json();
    }).then(function (t) {
      index.ajouterTextes(t.documents || []);
      index.preparer();
      textes.etat = 'charge';
      textes.nombre = (t.documents || []).length;
      if (etat.q) { chercher(); rendre(); }
    }).catch(function (e) {
      textes.etat = 'erreur';
      textes.erreur = String(e && e.message || e);
      if (etat.q) rendre();
    });
  }

  /* Les ressources à afficher, dans l'ordre */
  function selection() {
    var liste = fiches.filter(function (f) {
      return (!resultat || resultat.parId[f.id]) && passe(f, null);
    });
    var tri = etat.tri || (resultat ? 'pertinence' : 'titre');
    var cmp = {
      pertinence: function (a, b) { return resultat ? resultat.parId[a.id].rang - resultat.parId[b.id].rang : 0; },
      titre: function (a, b) { return R.normaliser(a.titre).localeCompare(R.normaliser(b.titre)); },
      recent: function (a, b) { return String((b.dates || {}).ajout || '').localeCompare(String((a.dates || {}).ajout || '')) || cmp.titre(a, b); },
      niveau: function (a, b) {
        var o = ['seconde', 'premiere', 'terminale'];
        function rang(f) { var n = (f.niveaux || []).map(function (x) { return o.indexOf(x); }); return n.length ? Math.min.apply(null, n) : 9; }
        return rang(a) - rang(b) || cmp.titre(a, b);
      }
    };
    return liste.sort(cmp[tri === 'pertinence' && !resultat ? 'titre' : tri]);
  }

  /* ── La page ────────────────────────────────────────────────── */

  function champRecherche() {
    var input = el('input', {
      type: 'search', id: 'recherche', class: 'recherche', placeholder: 'Chercher : boucle, SQL, réseau, débranché…',
      autocomplete: 'off', spellcheck: 'false', enterkeyhint: 'search', 'aria-describedby': 'recherche-aide'
    });
    input.value = etat.q;
    input.addEventListener('input', function () {
      clearTimeout(minuterie);
      minuterie = setTimeout(function () {
        etat.q = input.value.trim();
        etat.nombre = PAR_PAGE;
        if (etat.r) { etat.r = ''; }
        ecrireAdresse(false);
        chercher();
        rendre();
      }, 140);
    });
    document.addEventListener('keydown', function (e) {
      var cible = e.target.tagName;
      if (e.key === '/' && cible !== 'INPUT' && cible !== 'TEXTAREA' && cible !== 'SELECT' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        input.focus();
        input.select();
      }
      if (e.key === 'Escape' && e.target === input && input.value) {
        input.value = '';
        etat.q = '';
        ecrireAdresse(false);
        chercher();
        rendre();
      }
    });
    ui.input = input;
    ui.statut = el('p', { class: 'statut', id: 'recherche-statut', 'aria-live': 'polite' });
    return el('div', { class: 'cherche', role: 'search' }, [
      el('label', { for: 'recherche', class: 'invisible' }, 'Chercher dans la bibliothèque'),
      el('span', { class: 'cherche-ico', 'aria-hidden': 'true', html: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="7" cy="7" r="4.6"/><path d="m10.5 10.5 3.6 3.6"/></svg>' }),
      input,
      el('p', { class: 'invisible', id: 'recherche-aide' }, 'La recherche tient compte des synonymes, des notions et des fautes de frappe. Touche « / » pour revenir ici.'),
      ui.statut
    ]);
  }

  function construire(racine) {
    racine.appendChild(O.barreHaut('bibliotheque'));
    var page = el('div', { class: 'page bibliotheque' });
    racine.appendChild(page);
    var bandeau = el('header', { class: 'hero hero-rubrique', style: '--hl:' + COULEUR, html: O.scene(COULEUR, 7) });
    ui.chapo = el('p', { class: 'chapo' });
    bandeau.appendChild(el('div', { class: 'hero-contenu' }, [
      el('p', { class: 'invite', 'aria-hidden': 'true' }, '~/bibliotheque'),
      el('h1', null, 'Bibliothèque'),
      ui.chapo,
      champRecherche()
    ]));
    page.appendChild(bandeau);
    ui.alerte = el('div');
    page.appendChild(ui.alerte);

    var corps = el('div', { class: 'rub-corps' });
    ui.filtres = el('div', { class: 'filtres-liste' });
    ui.nbFiltres = el('span', { class: 'nb' });
    ui.panneau = el('details', { class: 'filtres' }, [
      el('summary', null, ['Filtres ', ui.nbFiltres]),
      ui.filtres
    ]);
    var large = window.matchMedia ? window.matchMedia('(min-width: 1080px)') : null;
    function ajuster() { ui.panneau.open = !!(large && large.matches); }
    ajuster();
    if (large) {
      if (large.addEventListener) large.addEventListener('change', ajuster);
      else if (large.addListener) large.addListener(ajuster);
    }
    corps.appendChild(el('aside', { class: 'cote', 'aria-label': 'Filtres' }, ui.panneau));
    ui.main = el('main', { id: 'contenu', tabindex: '-1' });
    corps.appendChild(ui.main);
    page.appendChild(corps);
    page.appendChild(O.piedDePage());
  }

  /* ── Les filtres : rendu ────────────────────────────────────── */

  function basculer(F, v, coche) {
    var t = (etat.filtres[F.id] || []).filter(function (x) { return x !== v; });
    if (coche) t.push(v);
    if (t.length) etat.filtres[F.id] = t; else delete etat.filtres[F.id];
    etat.nombre = PAR_PAGE;
    etat.r = '';
    ecrireAdresse(false);
    rendre();
  }

  function caseFiltre(F, v, texte, n) {
    var id = 'f-' + F.id + '-' + O.slug(v);
    var coche = (etat.filtres[F.id] || []).indexOf(v) >= 0;
    var input = el('input', { type: 'checkbox', id: id, checked: coche ? true : null });
    input.addEventListener('change', function () {
      var focus = id;
      basculer(F, v, input.checked);
      var x = document.getElementById(focus);
      if (x) x.focus();
    });
    return el('label', { class: 'filtre-case' + (n || coche ? '' : ' est-vide'), for: id }, [
      input, el('span', { class: 'filtre-nom' }, texte), el('span', { class: 'nb' }, String(n))
    ]);
  }

  /* Les nombres d'un filtre : pour chaque valeur, les ressources qui passent la recherche et les autres filtres */
  function compter(F) {
    var n = {};
    fiches.forEach(function (f) {
      if (resultat && !resultat.parId[f.id]) return;
      if (!passe(f, F.id)) return;
      F.valeurs(f).forEach(function (v) { n[v] = (n[v] || 0) + 1; });
    });
    return n;
  }

  function filtreSimple(F, n) {
    var choisis = etat.filtres[F.id] || [];
    var vals = Object.keys(n).concat(choisis.filter(function (v) { return !n[v]; }));
    vals = unique(vals);
    if (F.ordre) vals.sort(F.ordre);
    else vals.sort(function (a, b) { return (n[b] || 0) - (n[a] || 0) || a.localeCompare(b); });
    if (!vals.length) return null;
    var ul = el('ul', { class: 'filtre-valeurs' });
    var limite = F.limite && !ouverts['tout-' + F.id] ? F.limite : Infinity;
    vals.forEach(function (v, i) {
      if (i >= limite && choisis.indexOf(v) < 0) return;
      ul.appendChild(el('li', null, caseFiltre(F, v, F.libelle(v), n[v] || 0)));
    });
    var bloc = [ul];
    if (vals.length > limite) {
      var b = el('button', { type: 'button', class: 'lien-bouton' }, 'Voir les ' + vals.length);
      b.addEventListener('click', function () { ouverts['tout-' + F.id] = true; rendre(); });
      bloc.push(b);
    }
    return bloc;
  }

  /* Un arbre : programme officiel (programme › thème › contenu) ou notions (domaine › … ) */
  function filtreArbre(F, n) {
    var choisis = etat.filtres[F.id] || [];
    var racines, enfants, nom;
    if (F.arbre === 'programme') {
      racines = bib.referentiels.programmes.map(function (p) { return p.id; });
      enfants = function (id) { return refs.noeuds[id] ? refs.noeuds[id].enfants : []; };
      nom = function (id) { var x = refs.noeuds[id]; return x.niveau === 'programme' ? x.intitule : (x.court || x.intitule); };
    } else {
      racines = bib.referentiels.notions.domaines || [];
      enfants = function (id) { return index.thesaurus.etroites[id] || []; };
      nom = function (id) { return refs.notions[id] ? refs.notions[id].libelle : id; };
    }
    function visible(id) { return n[id] || choisis.indexOf(id) >= 0; }
    function branche(ids, profondeur) {
      var ul = el('ul', { class: 'filtre-valeurs' + (profondeur ? ' filtre-sous' : '') });
      ids.filter(visible).forEach(function (id) {
        var sous = enfants(id).filter(visible);
        var cle = F.id + ':' + id;
        var deplie = ouverts[cle] || sous.some(function (s) { return choisis.indexOf(s) >= 0 || descendChoisi(s); });
        var li = el('li', { class: 'filtre-noeud' });
        var ligne = el('div', { class: 'filtre-ligne' });
        if (sous.length) {
          var b = el('button', { type: 'button', class: 'deplier', 'aria-expanded': deplie ? 'true' : 'false',
                                 'aria-label': (deplie ? 'Replier ' : 'Déplier ') + nom(id) }, deplie ? '−' : '+');
          b.addEventListener('click', function () {
            ouverts[cle] = !deplie;
            rendre();
            var x = document.querySelector('[data-cle="' + cle + '"] .deplier');
            if (x) x.focus();
          });
          ligne.appendChild(b);
        } else {
          ligne.appendChild(el('span', { class: 'deplier-vide', 'aria-hidden': 'true' }));
        }
        ligne.appendChild(caseFiltre(F, id, nom(id), n[id] || 0));
        li.setAttribute('data-cle', cle);
        li.appendChild(ligne);
        if (sous.length && deplie) li.appendChild(branche(sous, profondeur + 1));
        ul.appendChild(li);
      });
      return ul;
    }
    function descendChoisi(id) {
      return enfants(id).some(function (s) { return choisis.indexOf(s) >= 0 || descendChoisi(s); });
    }
    var arbre = branche(racines, 0);
    return arbre.childNodes.length ? [arbre] : null;
  }

  function rendreFiltres() {
    O.vider(ui.filtres);
    var actifs = 0;
    FILTRES.forEach(function (F) {
      var n = compter(F);
      var contenu = F.arbre ? filtreArbre(F, n) : filtreSimple(F, n);
      var nbActifs = (etat.filtres[F.id] || []).length;
      actifs += nbActifs;
      if (!contenu && !F.aide) return;
      var cle = 'facette:' + F.id;
      var ouvert = ouverts[cle] !== undefined ? ouverts[cle] : (F.ouvert || nbActifs > 0);
      var d = el('details', { class: 'facette', open: ouvert ? true : null }, [
        el('summary', null, [F.titre, nbActifs ? el('span', { class: 'nb' }, ' (' + nbActifs + ')') : null])
      ]);
      d.addEventListener('toggle', function () { ouverts[cle] = d.open; });
      if (contenu) contenu.forEach(function (c) { d.appendChild(c); });
      else d.appendChild(el('p', { class: 'filtre-aide' }, F.aide));
      ui.filtres.appendChild(d);
    });
    ui.nbFiltres.textContent = actifs ? '(' + actifs + ' actif' + (actifs > 1 ? 's' : '') + ')' : '';
  }

  /* ── Les résultats ──────────────────────────────────────────── */

  function puces() {
    var out = [];
    FILTRES.forEach(function (F) {
      (etat.filtres[F.id] || []).forEach(function (v) {
        var texte = F.arbre === 'programme' ? (refs.noeuds[v] ? (refs.noeuds[v].court || refs.noeuds[v].intitule) : v)
          : F.arbre === 'notions' ? (refs.notions[v] ? refs.notions[v].libelle : v) : F.libelle(v);
        var b = el('button', { type: 'button', class: 'puce', 'aria-label': 'Retirer le filtre ' + F.titre + ' : ' + texte }, [
          el('span', { class: 'puce-quoi' }, F.titre + ' : '), texte, el('span', { 'aria-hidden': 'true' }, ' ×')
        ]);
        b.addEventListener('click', function () { basculer(F, v, false); ui.main.focus(); });
        out.push(b);
      });
    });
    if (out.length > 1) {
      var tout = el('button', { type: 'button', class: 'lien-bouton' }, 'Retirer tous les filtres');
      tout.addEventListener('click', function () { etat.filtres = {}; ecrireAdresse(false); rendre(); ui.main.focus(); });
      out.push(tout);
    }
    return out.length ? el('div', { class: 'puces' }, out) : null;
  }

  function outilsResultats(n) {
    var tri = el('select', { id: 'tri' });
    TRIS.forEach(function (t) {
      if (t.id === 'pertinence' && !resultat) return;
      var choisi = (etat.tri || (resultat ? 'pertinence' : 'titre')) === t.id;
      tri.appendChild(el('option', { value: t.id, selected: choisi ? true : null }, t.libelle));
    });
    tri.addEventListener('change', function () { etat.tri = tri.value; ecrireAdresse(false); rendre(); document.getElementById('tri').focus(); });
    var vue = el('div', { class: 'mode', role: 'group', 'aria-label': 'Vue' });
    [['liste', 'Liste'], ['cartes', 'Cartes']].forEach(function (v) {
      var b = el('button', { type: 'button', class: 'mode-btn', 'aria-pressed': etat.vue === v[0] ? 'true' : 'false' }, v[1]);
      b.addEventListener('click', function () { etat.vue = v[0]; ecrireAdresse(false); rendre(); });
      vue.appendChild(b);
    });
    return el('div', { class: 'outils-resultats' }, [
      el('p', { class: 'compte' }, O.pluriel(n, 'ressource', 'ressources')),
      el('div', { class: 'tri' }, [el('label', { for: 'tri' }, 'Trier par '), tri]),
      vue
    ]);
  }

  /* Pourquoi une ressource est trouvée : les champs, les notions, un extrait du document */
  var CHAMPS = { titre: 'titre', mots: 'mots-clés et classements', resume: 'résumé', bo: 'programme officiel',
                 docs: 'documents et autrices ou auteurs', presentation: 'présentation', texte: 'texte d\'un document' };

  function raison(f, r) {
    if (!r) return null;
    var morceaux = [];
    var champs = r.champs.filter(function (c) { return c !== 'titre'; }).map(function (c) { return CHAMPS[c]; });
    if (champs.length) morceaux.push('Trouvée dans : ' + champs.join(', '));
    var cites = derive[f.id].cites;
    var notions = r.notions.filter(function (nid) { return cites[nid]; }).map(function (nid) { return refs.notions[nid].libelle; });
    if (notions.length) morceaux.push('classée sous ' + notions.map(function (x) { return '« ' + x + ' »'; }).join(', '));
    var p = el('p', { class: 'raison' }, morceaux.join(' ; ') + (morceaux.length ? '.' : ''));
    if (r.champs.indexOf('texte') >= 0) {
      var doc = (index.docs[index.parId[f.id]].textes || []).map(function (t) {
        return { t: t, x: R.extrait(t.texte, r.trouves, 80) };
      }).filter(function (o) { return o.x; })[0];
      if (doc) {
        var d = f.documents[doc.t.document] || {};
        var q = el('q', null, surligne(doc.x, r.trouves));
        p.appendChild(el('span', { class: 'extrait' }, [' Dans « ' + (d.titre || libelle('roles', d.role)) + ' » : ', q]));
      }
    }
    return morceaux.length || r.champs.indexOf('texte') >= 0 ? p : null;
  }

  function principal(f) {
    return f.documents.filter(function (d) { return d.principal; })[0] || f.documents[0];
  }

  function lienPrincipal(f, r, classe) {
    var d = principal(f);
    var info = infoDocument(d);
    var a = info ? O.lienVers(info, '', classe) : el('span', { class: classe });
    a.appendChild(surligne(f.titre, r && r.trouves));
    return a;
  }

  function lienFiche(f, texte) {
    var a = el('a', { class: 'lien-fiche', href: adresseFiche(f.id) }, texte || 'Fiche complète');
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
      e.preventDefault();
      ouvrirFiche(f.id);
    });
    return a;
  }

  function meta(f) {
    return [
      (f.enseignements || []).map(function (x) { return libelle('enseignements', x); }).join(', '),
      (f.niveaux || []).map(function (x) { return court('niveaux', x); }).join(', '),
      (f.types || []).map(function (x) { return libelle('types', x); }).join(', ')
    ].filter(Boolean).join(' · ');
  }

  function etiquettes(f) {
    var p = el('p', { class: 'tags' });
    (f.usages || []).filter(function (u) { return famille(u) === 'modalite'; }).slice(0, 4)
      .forEach(function (u) { p.appendChild(el('span', null, libelle('usages', u))); });
    (f.langages || []).forEach(function (l) { p.appendChild(el('span', null, libelle('langages', l))); });
    if (f.duree) p.appendChild(el('span', null, f.duree));
    if (f.donnees_eleves && f.donnees_eleves.collecte) {
      p.appendChild(el('span', null, f.donnees_eleves.facultative ? 'Données d\'élèves : facultatif' : 'Données d\'élèves'));
    }
    var info = infoDocument(principal(f));
    if (info) p.appendChild(el('span', { class: 'site' }, info.type));
    return p;
  }

  function blocListe(f) {
    var r = resultat && resultat.parId[f.id];
    var li = el('li', { class: 'res', style: '--hl:' + couleurDe(f) });
    li.appendChild(lienPrincipal(f, r, 'titre'));
    li.appendChild(el('p', { class: 'chemin' }, meta(f)));
    var res = el('p');
    res.appendChild(surligne(f.resume, r && r.trouves));
    li.appendChild(res);
    var pq = raison(f, r);
    if (pq) li.appendChild(pq);
    li.appendChild(etiquettes(f));
    var autres = f.documents.length - 1;
    li.appendChild(el('p', { class: 'actions-fiche' }, [
      lienFiche(f, 'Fiche complète'),
      autres > 0 ? el('span', { class: 'nb' }, ' · ' + O.pluriel(autres, 'autre document', 'autres documents')) : null
    ]));
    return li;
  }

  function blocCarte(f) {
    var r = resultat && resultat.parId[f.id];
    var c = el('li', { class: 'noeud carte', style: '--hl:' + couleurDe(f) });
    c.appendChild(el('p', { class: 'noeud-meta' }, meta(f)));
    var h = el('h3');
    h.appendChild(lienPrincipal(f, r, 'titre'));
    c.appendChild(h);
    var p = el('p', { class: 'noeud-texte' });
    p.appendChild(surligne(f.resume, r && r.trouves));
    c.appendChild(p);
    var pq = raison(f, r);
    if (pq) c.appendChild(pq);
    c.appendChild(el('p', { class: 'actions-fiche' }, lienFiche(f, 'Fiche complète')));
    return c;
  }

  function lienRequete(texte, q) {
    var a = el('a', { href: location.pathname + '?q=' + encodeURIComponent(q) }, texte);
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
      e.preventDefault();
      etat.q = q;
      ui.input.value = q;
      etat.nombre = PAR_PAGE;
      ecrireAdresse(false);
      chercher();
      rendre();
      ui.input.focus();
    });
    return a;
  }

  /* Rien trouvé : correction, notion connue sans ressource, suggestions, filtres à retirer */
  function blocVide(sansFiltres) {
    var out = el('div', { class: 'vide-bloc' });
    var brut = resultat && resultat.brut;
    out.appendChild(el('p', { class: 'vide' }, etat.q ? 'Aucune ressource ne correspond à « ' + etat.q + ' »' +
      (Object.keys(etat.filtres).length ? ' avec ces filtres.' : '.') : 'Aucune ressource ne correspond à ces filtres.'));
    if (brut && brut.suggestion) {
      out.appendChild(el('p', null, ['Vouliez-vous dire ', lienRequete(brut.suggestion, brut.suggestion), ' ?']));
    }
    if (brut) {
      brut.clauses.filter(function (c) { return c.notions.length; }).forEach(function (c) {
        var n = refs.notions[c.notions[0]];
        if (n) out.appendChild(el('p', null, '« ' + n.libelle + ' » est une notion du thésaurus, mais aucune ressource de la bibliothèque ne la travaille encore.'));
      });
      var sugg = index.suggestions(etat.q, 4).filter(function (s) { return R.normaliser(s) !== R.normaliser(brut.suggestion || ''); });
      if (sugg.length) {
        var p = el('p', null, 'Suggestions : ');
        sugg.forEach(function (s, i) { if (i) p.appendChild(document.createTextNode(', ')); p.appendChild(lienRequete(s, s)); });
        out.appendChild(p);
      }
    }
    if (sansFiltres) {
      var b = el('button', { type: 'button', class: 'lien-bouton' }, 'Retirer les filtres (' + O.pluriel(sansFiltres, 'ressource', 'ressources') + ' sans eux)');
      b.addEventListener('click', function () { etat.filtres = {}; ecrireAdresse(false); rendre(); ui.main.focus(); });
      out.appendChild(el('p', null, b));
    }
    return out;
  }

  function rendreResultats() {
    var liste = selection();
    var main = ui.main;
    O.vider(main);
    main.appendChild(el('h2', { class: 'invisible' }, 'Résultats'));
    main.appendChild(outilsResultats(liste.length));
    var p = puces();
    if (p) main.appendChild(p);
    var brut = resultat && resultat.brut;
    if (brut && brut.corrections.length && liste.length) {
      main.appendChild(el('p', { class: 'note' }, brut.corrections.map(function (c) {
        return 'Mot introuvable : « ' + c.de + ' » ; résultats pour « ' + c.vers + ' ».';
      }).join(' ')));
    }
    if (brut && brut.partiel && liste.length) {
      main.appendChild(el('p', { class: 'note' }, 'Aucune ressource ne contient tous les mots : voici celles qui en contiennent une partie.'));
    }
    if (etat.q && textes.etat === 'erreur') {
      main.appendChild(el('p', { class: 'note' }, 'La recherche dans le texte des documents n\'est pas disponible pour le moment (' + textes.erreur + ').'));
    }
    if (!liste.length) {
      var sans = Object.keys(etat.filtres).length ? fiches.filter(function (f) { return !resultat || resultat.parId[f.id]; }).length : 0;
      main.appendChild(blocVide(sans));
    } else {
      var montrees = liste.slice(0, etat.nombre);
      if (etat.vue === 'cartes') {
        main.appendChild(el('ul', { class: 'noeuds cartes' }, montrees.map(blocCarte)));
      } else {
        main.appendChild(el('ul', { class: 'ressources resultats' }, montrees.map(blocListe)));
      }
      if (liste.length > montrees.length) {
        var reste = liste.length - montrees.length;
        var b = el('button', { type: 'button', class: 'plus' }, 'Afficher ' + Math.min(PAR_PAGE, reste) + ' de plus (' + reste + ' restantes)');
        b.addEventListener('click', function () {
          etat.nombre += PAR_PAGE;
          rendre();
          var items = ui.main.querySelectorAll('.res > .titre, .carte .titre');
          if (items[montrees.length]) items[montrees.length].focus();
        });
        main.appendChild(b);
      }
    }
    ui.statut.textContent = etat.q ? O.pluriel(liste.length, 'ressource trouvée', 'ressources trouvées') : '';
  }

  /* ── La fiche complète ──────────────────────────────────────── */

  function ouvrirFiche(id) {
    etat.r = id;
    ecrireAdresse(true);
    rendre();
    window.scrollTo(0, 0);
    if (ui.main) ui.main.focus();
  }

  function fermerFiche() {
    etat.r = '';
    ecrireAdresse(true);
    rendre();
    if (ui.main) ui.main.focus();
  }

  function ligne(dl, terme, valeur) {
    if (valeur == null || valeur === '' || (Array.isArray(valeur) && !valeur.length)) return;
    var dd = el('dd');
    (Array.isArray(valeur) ? valeur : [valeur]).forEach(function (v, i) {
      if (i) dd.appendChild(document.createTextNode(', '));
      dd.appendChild(typeof v === 'object' ? v : document.createTextNode(v));
    });
    dl.appendChild(el('div', { class: 'synthese-ligne' }, [el('dt', null, terme), dd]));
  }

  /* Un lien qui applique un filtre (programme, notion…) */
  function lienFiltre(F, v, texte) {
    var garde = { filtres: etat.filtres, r: etat.r, q: etat.q };
    etat.filtres = {}; etat.filtres[F] = [v]; etat.r = ''; etat.q = '';
    var href = location.pathname + requeteAdresse();
    etat.filtres = garde.filtres; etat.r = garde.r; etat.q = garde.q;
    var a = el('a', { href: href }, texte);
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
      e.preventDefault();
      etat.filtres = {}; etat.filtres[F] = [v]; etat.r = ''; etat.q = ''; ui.input.value = '';
      chercher();
      ecrireAdresse(true);
      rendre();
      ui.main.focus();
    });
    return a;
  }

  function placements(id) {
    var out = [];
    var v = bib.vitrine;
    if (!v) return out;
    (v.rubriques || []).forEach(function (rub) {
      (rub.sections || []).forEach(function (s) {
        var ici = (s.ressources || []).indexOf(id) >= 0 ||
          (s.sous_sections || []).some(function (ss) { return (ss.ressources || []).indexOf(id) >= 0; });
        if (!ici) return;
        var titre = s.titre || (refs.noeuds[s.programme] ? refs.noeuds[s.programme].intitule : s.id || '');
        var r = O.ordreRubriques().filter(function (x) { return x.id === rub.id; })[0];
        out.push(el('a', { href: r ? O.urlRubrique(r) : O.racine + rub.id + '/' }, (r ? r.nom : rub.id) + ', ' + titre));
      });
    });
    if ((v.a_la_une || []).some(function (u) { return u.ressource === id; })) out.unshift(el('a', { href: O.urlAccueil() }, 'À la une de l\'accueil'));
    return out;
  }

  function criteres(objet, liste, valeur, champ) {
    var entree = refs.valeurs[liste] && refs.valeurs[liste][valeur];
    var crit = (entree && entree[champ]) || [];
    var ul = el('ul', { class: 'criteres' });
    crit.forEach(function (c) {
      var ok = objet[c.id] === true;
      ul.appendChild(el('li', { class: ok ? 'oui' : 'non' }, [
        el('span', { class: 'marque-critere', 'aria-hidden': 'true' }, ok ? '✓' : '✗'),
        el('span', { class: 'invisible' }, ok ? 'Oui : ' : 'Non : '),
        c.libelle
      ]));
    });
    return ul;
  }

  function sourcesDe(ids) {
    var srcs = (bib.referentiels.notions.sources || []);
    return ids.map(function (sid) {
      var s = srcs.filter(function (x) { return x.id === sid; })[0];
      if (!s) return sid;
      var ref = s.reference.split('.')[0];
      return s.url ? el('a', { href: s.url, rel: 'noopener', target: '_blank' }, ref) : ref;
    });
  }

  function rendreFiche() {
    var f = parId[etat.r];
    var main = ui.main;
    O.vider(main);
    var retour = el('a', { class: 'retour', href: location.pathname + requeteAdresse('r') }, '← Retour aux résultats');
    retour.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
      e.preventDefault();
      fermerFiche();
    });
    main.appendChild(retour);
    if (!f) {
      document.title = 'Ressource introuvable – Bibliothèque – ' + O.titreSite();
      main.appendChild(el('h2', null, 'Ressource introuvable'));
      main.appendChild(el('p', { class: 'vide' }, 'Aucune ressource « ' + etat.r + ' » dans la bibliothèque : elle a peut-être été renommée, retirée ou cachée.'));
      return;
    }
    document.title = f.titre + ' – Bibliothèque – ' + O.titreSite();
    var r = resultat && resultat.parId[f.id];
    var t = r && r.trouves;
    var art = el('article', { class: 'fiche-complete', style: '--hl:' + couleurDe(f) });
    var h = el('h2', { class: 'fiche-titre' });
    h.appendChild(surligne(f.titre, t));
    art.appendChild(h);
    if (f.accroche) { var acc = el('p', { class: 'chapo' }); acc.appendChild(surligne(f.accroche, t)); art.appendChild(acc); }
    var d = principal(f), info = infoDocument(d);
    if (info) art.appendChild(el('p', { class: 'ouvrir' }, O.lienVers(info, 'Ouvrir : ' + (d.titre || libelle('roles', d.role)), 'bouton-ouvrir')));

    // Synthèse
    var dl = el('dl', { class: 'synthese' });
    ligne(dl, 'Enseignement', (f.enseignements || []).map(function (x) { return lienFiltre('ens', x, libelle('enseignements', x)); }));
    ligne(dl, 'Niveau', (f.niveaux || []).map(function (x) { return lienFiltre('niv', x, libelle('niveaux', x)); }));
    ligne(dl, 'Programme officiel', (f.programme || []).map(function (id) {
      var n = refs.noeuds[id];
      if (!n) return id;
      var p = refs.noeuds[n.programme];
      var th = n.niveau === 'contenu' ? refs.noeuds[n.parent] : null;
      return lienFiltre('prog', id, (p ? (p.court || p.intitule) + ' › ' : '') + (th ? (th.court || th.intitule) + ' › ' : '') + n.intitule);
    }));
    var notions = f.notions || {};
    [['travaillees', 'Notions travaillées'], ['prerequises', 'Notions prérequises']].forEach(function (x) {
      ligne(dl, x[1], (notions[x[0]] || []).map(function (nid) { return lienFiltre('notion', nid, refs.notions[nid] ? refs.notions[nid].libelle : nid); }));
    });
    ligne(dl, 'Type', (f.types || []).map(function (x) { return lienFiltre('type', x, libelle('types', x)); }));
    ligne(dl, 'Modalités', (f.usages || []).filter(function (u) { return famille(u) === 'modalite'; }).map(function (x) { return libelle('usages', x); }));
    var pre = (f.usages || []).filter(function (u) { return famille(u) === 'prerequis'; });
    ligne(dl, 'Prérequis', pre.length ? pre.map(function (x) { return libelle('usages', x); }) : 'aucun');
    ligne(dl, 'Durée', f.duree);
    ligne(dl, 'Langages', (f.langages || []).map(function (x) { return libelle('langages', x); }));
    ligne(dl, 'Compétences Pix', (f.competences_pix || []).map(function (x) { return refs.pix[x] ? refs.pix[x].numero + ' ' + refs.pix[x].libelle : x; }));
    ligne(dl, 'Origine', f.origine ? libelle('origines', f.origine) : '');
    ligne(dl, 'Autrices et auteurs', (f.auteurs || []).map(function (a) {
      var t2 = a.nom + (a.role ? ' (' + a.role + ')' : '');
      return a.lien ? el('a', { href: a.lien, rel: 'noopener', target: '_blank' }, t2) : t2;
    }));
    ligne(dl, 'Licence', f.licence);
    var de = f.donnees_eleves || {};
    ligne(dl, 'Données d\'élèves', de.collecte ? (de.facultative ? 'collecte facultative' : 'oui') + (de.detail ? ' : ' + de.detail : '') :
      'aucune collecte' + (de.detail ? ' : ' + de.detail : ''));
    ligne(dl, 'Statut de la fiche', f.statut ? libelle('statuts', f.statut) : '');
    ligne(dl, 'Ajoutée le', (f.dates || {}).ajout ? new Date(f.dates.ajout + 'T12:00:00').toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '');
    ligne(dl, 'Sur le site', placements(f.id));
    art.appendChild(el('h3', null, 'En bref'));
    art.appendChild(dl);

    // Documents
    art.appendChild(el('h3', null, f.documents.length > 1 ? 'Les ' + f.documents.length + ' documents' : 'Le document'));
    var ul = el('ul', { class: 'documents' });
    f.documents.forEach(function (doc) {
      var i2 = infoDocument(doc);
      var titre = doc.titre || libelle('roles', doc.role);
      ul.appendChild(el('li', null, [
        i2 ? O.lienVers(i2, titre) : titre,
        ' ', el('span', { class: 'type' }, '(' + [libelle('roles', doc.role), libelle('formats', doc.format), i2 && !i2.interne ? i2.type : null]
          .filter(function (x, k, a) { return x && a.indexOf(x) === k; }).join(', ') + (doc.principal ? ', document principal' : '') + ')')
      ]));
    });
    art.appendChild(ul);

    if (f.presentation) { art.appendChild(el('h3', null, 'Présentation')); var pr = el('p'); pr.appendChild(texteRiche(f.presentation, t)); art.appendChild(pr); }
    if (f.objectif) { art.appendChild(el('h3', null, 'Objectif')); art.appendChild(el('p', null, texteRiche(f.objectif, t))); }
    if ((f.criteres_reussite || []).length) {
      art.appendChild(el('h3', null, 'Critères de réussite'));
      art.appendChild(el('ol', null, f.criteres_reussite.map(function (c) { return el('li', null, texteRiche(c, t)); })));
    }
    if (f.editeur_code) {
      art.appendChild(el('h3', null, 'L\'éditeur de code'));
      art.appendChild(criteres(f.editeur_code, 'usages', 'editeur-de-code', 'criteres'));
      if (f.editeur_code.remarque) art.appendChild(el('p', { class: 'petit' }, f.editeur_code.remarque));
    }
    if (f.td_en_ligne) {
      art.appendChild(el('h3', null, 'La page en ligne du TD'));
      art.appendChild(criteres(f.td_en_ligne, 'types', 'td', 'criteres_en_ligne'));
      if (f.td_en_ligne.remarque) art.appendChild(el('p', { class: 'petit' }, f.td_en_ligne.remarque));
    }

    // Difficultés connues des élèves, pour les notions travaillées (thésaurus)
    var diff = [];
    (notions.travaillees || []).forEach(function (nid) {
      var n = refs.notions[nid];
      (n && n.difficultes || []).forEach(function (x) { diff.push({ notion: n.libelle, d: x }); });
    });
    if (diff.length) {
      art.appendChild(el('h3', null, 'Difficultés connues des élèves'));
      art.appendChild(el('ul', { class: 'difficultes' }, diff.map(function (x) {
        return el('li', null, [el('strong', null, x.notion + ' : '), x.d.texte, x.d.precision ? ' (' + x.d.precision + ')' : '',
          el('span', { class: 'source' }, [' Source : '].concat(sourcesDe(x.d.sources).reduce(function (acc, s, i) {
            return acc.concat(i ? ['; ', s] : [s]);
          }, [])).concat(['.']))]);
      })));
    }

    if ((f.liees || []).length) {
      art.appendChild(el('h3', null, 'Ressources liées'));
      art.appendChild(el('ul', null, f.liees.map(function (l) {
        var g = parId[l.ressource];
        if (!g) return null;
        return el('li', null, [l.relation === 'suite-de' ? 'Fait suite à : ' : 'Voir aussi : ', lienFiche(g, g.titre)]);
      })));
    }
    if (f.credits) { art.appendChild(el('h3', null, 'Crédits')); art.appendChild(el('p', null, f.credits)); }
    if ((f.mots_cles || []).length) {
      art.appendChild(el('p', { class: 'tags' }, f.mots_cles.map(function (m) { return el('span', null, m); })));
    }
    main.appendChild(art);
  }

  /* ── Ensemble ───────────────────────────────────────────────── */

  function rendre() {
    if (!bib) return;
    rendreFiltres();
    if (etat.r) {
      rendreFiche();
    } else {
      document.title = (etat.q ? '« ' + etat.q + ' » – ' : '') + 'Bibliothèque – ' + O.titreSite();
      rendreResultats();
    }
  }

  function alerte(titre, texte) {
    O.vider(ui.alerte);
    ui.alerte.appendChild(el('div', { class: 'alerte', role: 'alert' }, [
      el('p', null, el('strong', null, titre)), el('p', { class: 'petit' }, texte)
    ]));
  }

  function demarrer(donnees) {
    bib = donnees;
    refs = R.references(bib.referentiels);
    index = new R.Index({ notions: bib.referentiels.notions });
    index.ajouterSynonymes(R.groupesSynonymes(bib.referentiels));
    fiches = bib.ressources || [];
    parId = {};
    fiches.forEach(function (f) {
      parId[f.id] = f;
      index.ajouter(f.id, R.champsFiche(f, refs), f.notions);
    });
    index.preparer();
    fiches.forEach(deriver);
    definirFiltres();
    lireAdresse();
    ui.input.value = etat.q;
    ui.chapo.textContent = O.pluriel(fiches.length, 'ressource', 'ressources') + ' de SNT, de NSI et pour la classe, avec leurs documents. '
      + 'Cherchez un mot ou une notion (« boucle » trouve aussi for et while), puis affinez avec les filtres.';
    chercher();
    rendre();
    window.addEventListener('popstate', function () {
      lireAdresse();
      ui.input.value = etat.q;
      chercher();
      rendre();
    });
  }

  window.pageBibliotheque = function (racine, outils) {
    O = outils;
    try {
      construire(racine);
    } catch (e) {
      if (window.console) console.error(e);
      return;
    }
    if (O.surDisque) {
      alerte('La bibliothèque a besoin d\'un petit serveur', 'Ouverte depuis le disque, la page ne peut pas lire ses données. '
        + 'Lancer « python3 scripts/construire_bibliotheque.py » puis « python3 -m http.server » à la racine du dépôt, '
        + 'et ouvrir http://localhost:8000/bibliotheque/.');
      return;
    }
    ui.main.appendChild(el('p', { class: 'vide' }, 'Chargement de la bibliothèque…'));
    fetch(O.racine + 'donnees/bibliotheque.json').then(function (r) {
      if (!r.ok) throw new Error(r.status === 404 ? 'fichier introuvable' : 'code ' + r.status);
      return r.json();
    }).then(function (donnees) {
      if (!donnees || !Array.isArray(donnees.ressources) || !donnees.referentiels) throw new Error('contenu inattendu');
      demarrer(donnees);
    }).catch(function (e) {
      O.vider(ui.main);
      alerte('La bibliothèque n\'a pas pu se charger', 'Le fichier donnees/bibliotheque.json n\'a pas pu être lu ('
        + (e && e.message || e) + '). Il est construit à chaque publication par le workflow « Publier le site » ; '
        + 'sur un ordinateur, lancer « python3 scripts/construire_bibliotheque.py » à la racine du dépôt.');
      if (window.console) console.error(e);
    });
  };
})();
