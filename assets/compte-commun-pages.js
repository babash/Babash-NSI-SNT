/* ═══════════════════════════════════════════════════════════════
   Les morceaux communs aux deux pages du compte commun (T101b) :
   eleve/ (assets/planque.js) et enseignant/ (assets/espace-enseignant.js).
   Le bandeau du haut, le bandeau de démonstration, les champs de
   formulaire, les messages et les annonces. Architecte ; l'apparence
   (eleve/compte-commun.css) est provisoire, à reprendre par le Designer.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var O = null;
  var annonces = null;
  var compteur = 0;

  function el() { return O.el.apply(null, arguments); }
  function idUnique(prefixe) { compteur += 1; return (prefixe || 'cc') + '-' + compteur; }

  /* La date en français, sans heure : « 12 novembre » (et l'année si elle diffère) */
  function date(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d)) return '';
    var o = { day: 'numeric', month: 'long' };
    if (d.getFullYear() !== new Date().getFullYear()) o.year = 'numeric';
    return d.toLocaleDateString('fr-FR', o);
  }

  /* « il y a 3 jours », pour la dernière visite (vue par l'enseignant·e seulement) */
  function depuis(iso) {
    if (!iso) return '';
    var j = Math.floor((Date.now() - new Date(iso).getTime()) / 864e5);
    if (j <= 0) return 'aujourd\'hui';
    if (j === 1) return 'hier';
    return 'il y a ' + j + ' jours';
  }

  var CATEGORIES = [
    ['premiers_pas', 'Premiers pas'], ['exploration', 'Exploration'], ['perseverance', 'Persévérance'],
    ['creation', 'Création'], ['entraide', 'Entraide'], ['maitrise', 'Maîtrise']
  ];

  /* Le bandeau de démonstration, ou celui d'un réglage incomplet */
  function bandeauMode(vous) {
    var probleme = window.CompteCommun.probleme();
    if (window.CompteCommun.mode() !== 'demo') return null;
    return el('div', { class: 'cc-demo', role: 'note', 'aria-label': 'Démonstration' }, [
      el('p', null, [el('strong', null, 'Démonstration : rien n\'est enregistré.'),
        vous ? ' Les comptes, les codes et les classes de cette page sont fictifs ; ils disparaissent quand vous rechargez ou fermez la page.'
          : ' Les comptes, les codes et les classes de cette page sont fictifs ; ils disparaissent quand tu recharges ou fermes la page.']),
      probleme ? el('p', { class: 'petit' }, probleme) : null
    ]);
  }

  /* Le haut de page : barre, bandeau de démonstration, titre sur le décor */
  function entete(racine, options) {
    racine.appendChild(O.barreHaut(options.page));
    var b = bandeauMode(options.vous);
    var page = el('div', { class: 'page cc-page' });
    if (b) page.appendChild(b);
    var hero = el('section', { class: 'hero hero-rubrique cc-hero', style: '--hl:' + options.couleur }, [
      el('div', { html: O.scene(options.couleur, options.graine || 7) }).firstChild,
      el('div', { class: 'hero-contenu' }, [
        el('p', { class: 'invite', 'aria-hidden': 'true' }, options.invite),
        el('h1', null, options.titre),
        el('p', { class: 'chapo' }, options.chapo)
      ])
    ]);
    page.appendChild(hero);
    var main = el('main', { id: 'contenu', class: 'cc-main', tabindex: '-1' });
    page.appendChild(main);
    annonces = el('div', { class: 'cc-annonces', role: 'status', 'aria-live': 'polite' });
    page.appendChild(annonces);
    page.appendChild(O.piedDePage());
    racine.appendChild(page);
    return main;
  }

  /* Une annonce brève (« Haut fait : Premier circuit », « +20 crédits »), lue par les lecteurs d'écran */
  function annoncer(texte, genre) {
    if (!annonces || !texte) return;
    var a = el('p', { class: 'cc-annonce' + (genre ? ' cc-annonce-' + genre : '') }, texte);
    annonces.appendChild(a);
    setTimeout(function () { if (a.parentNode) a.parentNode.removeChild(a); }, 6000);
  }

  function annoncerNouveautes(n, catalogue) {
    if (!n) return;
    (n.hauts_faits || []).forEach(function (h) { annoncer('Haut fait : ' + (h.nom || 'haut fait secret'), 'fier'); });
    (n.elements || []).forEach(function (e) { annoncer('Débloqué : ' + (e.nom || e.id), 'fier'); });
    if (n.credits > 0) annoncer('+' + n.credits + ' crédits', 'fier');
  }

  /* Un message sous un formulaire : erreur ou réussite, toujours en clair */
  function message(zone, texte, genre) {
    O.vider(zone);
    if (!texte) return;
    zone.className = 'cc-message' + (genre ? ' cc-' + genre : '');
    zone.appendChild(document.createTextNode(texte));
  }
  function zoneMessage() { return el('p', { class: 'cc-message', role: 'alert', 'aria-live': 'assertive' }); }

  /* Un champ avec son étiquette et son aide */
  function champ(options) {
    var id = idUnique('champ');
    var aide = options.aide ? el('span', { class: 'cc-aide', id: id + '-aide' }, options.aide) : null;
    var attrs = { id: id, name: options.nom || id, type: options.type || 'text', class: 'cc-saisie' + (options.classe ? ' ' + options.classe : ''),
      autocomplete: options.autocomplete || 'off', spellcheck: 'false', 'aria-describedby': aide ? id + '-aide' : null,
      placeholder: options.exemple || null, required: options.requis ? true : null, maxlength: options.max || null,
      minlength: options.min || null, inputmode: options.inputmode || null, autocapitalize: options.capitales ? 'characters' : null,
      value: options.valeur || null };
    if (options.type === 'number') { attrs.min = options.mini; attrs.max = options.maxi; attrs.step = 1; delete attrs.maxlength; }
    var input = el('input', attrs);
    var bloc = el('div', { class: 'cc-champ' }, [el('label', { for: id }, options.etiquette), aide, input]);
    bloc.input = input;
    return bloc;
  }

  function caseACocher(etiquette, aide) {
    var id = idUnique('case');
    var input = el('input', { type: 'checkbox', id: id });
    var bloc = el('div', { class: 'cc-case' }, [input, el('label', { for: id }, [etiquette, aide ? el('span', { class: 'cc-aide' }, ' ' + aide) : null])]);
    bloc.input = input;
    return bloc;
  }

  function bouton(texte, options) {
    options = options || {};
    return el('button', { type: options.type || 'button', class: 'cc-bouton' + (options.classe ? ' ' + options.classe : ''),
      'aria-describedby': options.decrit || null, disabled: options.inactif ? true : null }, texte);
  }

  /* Pendant un appel : le bouton est inactif et dit « … » */
  function occupe(btn, vrai) {
    if (!btn) return;
    if (vrai) { btn.disabled = true; btn.setAttribute('aria-busy', 'true'); }
    else { btn.disabled = false; btn.removeAttribute('aria-busy'); }
  }

  /* Un formulaire : soumission au clavier comme à la souris, sans recharger la page */
  function formulaire(enfants, quandEnvoye, options) {
    var f = el('form', { class: 'cc-form' + (options && options.classe ? ' ' + options.classe : ''), novalidate: true }, enfants);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      quandEnvoye(f);
    });
    return f;
  }

  function carte(titre, enfants, options) {
    options = options || {};
    var h = el(options.niveau || 'h2', { class: 'cc-carte-titre', id: options.id || null, tabindex: options.focusable ? '-1' : null }, titre);
    return el('section', { class: 'cc-carte' + (options.classe ? ' ' + options.classe : ''), 'aria-labelledby': options.id || null }, [h].concat(enfants));
  }

  /* Des onglets accessibles : flèches gauche et droite, Début et Fin ; l'onglet choisi va dans l'adresse (#…) */
  function onglets(liste, options) {
    var barre = el('div', { class: 'cc-onglets', role: 'tablist', 'aria-label': options.etiquette });
    var panneaux = el('div', { class: 'cc-panneaux' });
    var boutons = [];
    liste.forEach(function (o) {
      var bid = 'onglet-' + o.id, pid = 'panneau-' + o.id;
      var b = el('button', { type: 'button', role: 'tab', id: bid, 'aria-controls': pid, 'aria-selected': 'false', tabindex: '-1', class: 'cc-onglet' }, o.nom);
      var p = el('section', { role: 'tabpanel', id: pid, 'aria-labelledby': bid, class: 'cc-panneau', hidden: true, tabindex: '0' });
      b.addEventListener('click', function () { choisir(o.id, true); });
      b.addEventListener('keydown', function (e) {
        var i = boutons.indexOf(b), n = boutons.length, j = null;
        if (e.key === 'ArrowRight') j = (i + 1) % n;
        else if (e.key === 'ArrowLeft') j = (i - 1 + n) % n;
        else if (e.key === 'Home') j = 0;
        else if (e.key === 'End') j = n - 1;
        if (j === null) return;
        e.preventDefault();
        choisir(liste[j].id, true);
        boutons[j].focus();
      });
      boutons.push(b);
      barre.appendChild(b);
      panneaux.appendChild(p);
      o.bouton = b;
      o.panneau = p;
    });
    function choisir(id, ecrire) {
      var trouve = liste.filter(function (o) { return o.id === id; })[0] || liste[0];
      liste.forEach(function (o) {
        var oui = o === trouve;
        o.bouton.setAttribute('aria-selected', oui ? 'true' : 'false');
        o.bouton.tabIndex = oui ? 0 : -1;
        o.panneau.hidden = !oui;
      });
      if (ecrire) {
        try { history.replaceState(null, '', location.pathname + location.search + '#' + trouve.id); } catch (e) { /* sans importance */ }
      }
      if (trouve.quandChoisi) trouve.quandChoisi(trouve.panneau);
    }
    var depart = (location.hash || '').slice(1);
    return { barre: barre, panneaux: panneaux, choisir: choisir, depart: depart, liste: liste };
  }

  /* Le nom lisible d'un haut fait, d'une application, d'un élément */
  function outilsCatalogue(cat) {
    cat = cat || {};
    function app(id) { return (cat.applications || []).filter(function (a) { return a.id === id; })[0] || { id: id, nom: id }; }
    function hf(appId, id) { return (cat.hauts_faits || []).filter(function (h) { return h.application === appId && h.id === id; })[0] || null; }
    function elt(id) { return (cat.elements || []).filter(function (e) { return e.id === id; })[0] || null; }
    function nomHf(appId, id) { var h = hf(appId, id); return h && h.nom ? h.nom : 'Haut fait secret'; }
    return { app: app, hf: hf, elt: elt, nomHf: nomHf };
  }

  window.PagesCompte = {
    initialiser: function (outils) { O = outils; },
    entete: entete, annoncer: annoncer, annoncerNouveautes: annoncerNouveautes,
    message: message, zoneMessage: zoneMessage, champ: champ, caseACocher: caseACocher, bouton: bouton, occupe: occupe,
    formulaire: formulaire, carte: carte, onglets: onglets, date: date, depuis: depuis, CATEGORIES: CATEGORIES,
    outilsCatalogue: outilsCatalogue, idUnique: idUnique
  };
})();
