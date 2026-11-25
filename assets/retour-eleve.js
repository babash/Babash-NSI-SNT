/* ═══════════════════════════════════════════════════════════════
   L'avis anonyme des élèves, à la fin d'une ressource en ligne (T163).
   Architecte. Style provisoire, à reprendre par le Designer.

   Une page l'active par un emplacement, à la fin de la ressource :
     <section data-retour="td-bac-abr" data-retour-partie="tle-td-bac-abr-1"></section>
     <script src="../../../assets/retour-eleve.js" defer></script>
   - data-retour : l'identifiant de la fiche (donnees/ressources/<id>.json),
     ou « sequence:<id> » pour la page d'une séquence ;
   - data-retour-partie (facultatif) : la partie ; par défaut, l'identifiant de
     la feuille de TD en ligne (data-td du <main class="td">) s'il y en a un ;
   - data-retour-nom (facultatif) : « cette feuille », « cette séquence »…
   Sur une page du site qui charge site.js, ce script se place entre site.js et
   reglages.js. Ailleurs (feuilles de TD), il lit reglages.js lui-même.

   Éteint par défaut : rien ne s'affiche tant que reglages.js ne dit pas
   RETOURS_ELEVES: true (après le collage de la migration 0013). Pour voir le
   bloc sans rien envoyer : ajouter ?retour=essai à l'adresse.

   L'anonymat (supabase/LISEZMOI.md, « 0013 ») :
   - rien n'identifie l'élève : ni compte, ni code, ni pseudo ; le jeton du
     compte commun n'est jamais lu ni envoyé ; requête sans cookie ni référent ;
   - l'appareil tire une clé au hasard par ressource, pour changer son avis
     pendant la semaine ; la base n'en garde que l'empreinte, une semaine ;
   - la classe n'est connue que par le lien de la ressource (…?classe=ABCD),
     gardée dans l'onglet seulement (postes partagés) ;
   - sans réseau, ou si la base ne répond pas, l'avis attend sur l'appareil
     (dans la semaine) et part à la visite suivante ; aucune alerte.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  if (typeof document === 'undefined' || !document.querySelector) return;

  var SCRIPT = document.currentScript;
  var RACINE = (function () { try { return new URL('..', SCRIPT.src).href; } catch (e) { return ''; } })();
  var PREFIXE = 'retour-eleve:';
  var CLE_CLASSE = 'retour-eleve:classe';
  var RE_RESSOURCE = /^(sequence:)?[a-z0-9][a-z0-9-]{1,79}$/;
  var RE_PARTIE = /^[a-z0-9][a-z0-9._-]{0,79}$/;
  var RE_CLASSE = /^[A-HJ-NP-Z]{4}$/;
  var RE_MOT_INTERDIT = /@|https?:|www\.|\.(com|fr|net|org|yt|re|io)\b|[0-9]([ .-]?[0-9]){5,}/i;

  /* Le contenu du retour : les mêmes valeurs que la base (supabase/0013-retours-eleves.sql) */
  var QUESTIONS = [
    { id: 'difficulte', titre: 'C\'était…', choix: [['trop_facile', 'Trop facile'], ['bien', 'Bien pour moi'], ['trop_dur', 'Trop dur']] },
    { id: 'compris', titre: 'J\'ai compris ?', choix: [['oui', 'Oui'], ['a_peu_pres', 'À peu près'], ['non', 'Non']] },
    { id: 'fini', titre: 'J\'ai fini ?', choix: [['oui', 'Oui'], ['presque', 'Presque'], ['non', 'Non']] }
  ];
  var REMARQUES = [
    ['consignes', 'Consignes pas claires'],
    ['trop_de_texte', 'Trop de texte à lire'],
    ['exemples', 'Il me faut plus d\'exemples'],
    ['bug', 'Quelque chose ne marchait pas'],
    ['telephone', 'Pas pratique sur téléphone'],
    ['encore', 'J\'en veux d\'autres comme ça']
  ];

  /* ── Les réglages (reglages.js) ─────────────────────────────── */
  var reglages = null, enAttente = [];
  function recevoir(r) {
    if (reglages) return;
    reglages = r || {};
    var l = enAttente; enAttente = [];
    l.forEach(function (f) { try { f(reglages); } catch (e) { if (window.console) console.warn('[avis] ' + e); } });
  }
  function quandReglages(f) { if (reglages) f(reglages); else enAttente.push(f); }
  /* Page du site : site.js a défini window.reglages, reglages.js vient après ce script */
  if (typeof window.reglages === 'function') {
    var origine = window.reglages;
    window.reglages = function (r) { try { recevoir(r); } catch (e) { /* rien */ } return origine.apply(this, arguments); };
  }
  /* Page à part (feuille de TD) : on lit reglages.js nous-mêmes */
  function chargerReglages() {
    if (reglages) return;
    if (typeof window.reglages === 'function' && !window.reglages.retourEleve) return; // site.js : reglages.js arrive
    window.reglages = recevoir;
    window.reglages.retourEleve = true;
    var s = document.createElement('script');
    s.src = RACINE + 'reglages.js';
    s.async = true;
    s.onerror = function () { recevoir({}); };
    (document.head || document.documentElement).appendChild(s);
  }

  /* ── Le stockage sur l'appareil (jamais une erreur visible) ── */
  function magasin(nom) { try { var m = window[nom]; m.getItem('x'); return m; } catch (e) { return null; } }
  function lire(nom, cle) { var m = magasin(nom); if (!m) return null; try { return JSON.parse(m.getItem(cle) || 'null'); } catch (e) { return null; } }
  function ecrire(nom, cle, v) {
    var m = magasin(nom); if (!m) return;
    try { if (v == null) m.removeItem(cle); else m.setItem(cle, JSON.stringify(v)); } catch (e) { /* plein ou interdit : tant pis */ }
  }

  /* Le lundi de la semaine, heure de Mayotte (UTC+3, sans heure d'été), comme la base */
  function semaine(d) {
    var t = new Date((d ? d.getTime() : Date.now()) + 3 * 3600e3);
    var j = (t.getUTCDay() + 6) % 7;
    var l = new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() - j));
    return l.toISOString().slice(0, 10);
  }
  function nouvelleCle() {
    var b = new Uint8Array(18);
    try { window.crypto.getRandomValues(b); } catch (e) { for (var i = 0; i < b.length; i++) b[i] = Math.floor(Math.random() * 256); }
    var s = '';
    for (var k = 0; k < b.length; k++) s += String.fromCharCode(b[k]);
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  /* Le ménage : un avis envoyé est gardé un an (« déjà donné ») ; un avis en attente, sa semaine seulement */
  function menage() {
    var m = magasin('localStorage'); if (!m) return;
    var s = semaine(), limite = new Date(Date.now() - 365 * 864e5).toISOString().slice(0, 10);
    try {
      for (var i = m.length - 1; i >= 0; i--) {
        var k = m.key(i);
        if (!k || k.indexOf(PREFIXE) !== 0 || k === CLE_CLASSE) continue;
        var v = lire('localStorage', k);
        if (!v || !v.semaine || v.semaine < limite || (v.etat === 'en_attente' && v.semaine !== s)) m.removeItem(k);
      }
    } catch (e) { /* rien */ }
  }

  /* Le code de classe : celui de l'adresse (…?classe=ABCD), sinon celui de l'onglet */
  function codeClasse() {
    var c = null;
    try { c = (new URL(location.href).searchParams.get('classe') || '').trim().toUpperCase(); } catch (e) { c = ''; }
    if (RE_CLASSE.test(c)) { ecrire('sessionStorage', CLE_CLASSE, c); return c; }
    c = lire('sessionStorage', CLE_CLASSE);
    return typeof c === 'string' && RE_CLASSE.test(c) ? c : null;
  }

  /* ── L'envoi ─────────────────────────────────────────────────── */
  function appeler(cfg, fonction, params) {
    if (cfg.essai) return new Promise(function (ok) { setTimeout(function () { ok({ ok: true, essai: true, modifie: false, classe: !!params.p_classe, mot_garde: !!params.p_mot }); }, 250); });
    if (typeof fetch !== 'function' || (navigator && navigator.onLine === false)) return Promise.resolve({ ok: false, plus_tard: true });
    var arret = typeof AbortController === 'function' ? new AbortController() : null;
    var minuteur = arret ? setTimeout(function () { arret.abort(); }, 15000) : null;
    return fetch(cfg.url + '/rest/v1/rpc/' + fonction, {
      method: 'POST', headers: { 'Content-Type': 'application/json', apikey: cfg.cle },
      body: JSON.stringify(params), credentials: 'omit', referrerPolicy: 'no-referrer', cache: 'no-store',
      signal: arret ? arret.signal : undefined
    }).then(function (r) {
      if (r.ok) return r.json();
      if (window.console) console.info('[avis] ' + fonction + ' : code ' + r.status + ' ; l\'avis attend sur l\'appareil.');
      return { ok: false, plus_tard: true };
    }).then(function (rep) { return rep && typeof rep === 'object' ? rep : { ok: false, plus_tard: true }; },
      function () { return { ok: false, plus_tard: true }; })
      .then(function (rep) { if (minuteur) clearTimeout(minuteur); return rep; });
  }

  function parametres(etat) {
    var r = etat.reponses || {};
    return { p_cle: etat.cle, p_ressource: etat.ressource, p_partie: etat.partie, p_classe: etat.classe || null,
      p_plu: r.plu || null, p_difficulte: r.difficulte || null, p_compris: r.compris || null, p_fini: r.fini || null,
      p_remarques: r.remarques || [], p_mot: r.mot || null };
  }

  /* ── L'affichage ─────────────────────────────────────────────── */
  var STYLE = [
    '.retour-eleve{--re-fond:#F5F7FB;--re-encre:#161A24;--re-doux:#4A5368;--re-trait:#B9C3D6;--re-accent:#0B5E73;--re-choisi:#DDF1F6;--re-etoile:#9A6200;',
    'box-sizing:border-box;max-width:44rem;margin:2.5rem auto 1rem;padding:1rem 1rem 1.1rem;border:1px solid var(--re-trait);border-radius:8px;',
    'background:var(--re-fond);color:var(--re-encre);font:inherit;line-height:1.45}',
    '@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .retour-eleve{--re-fond:#151926;--re-encre:#E9EDF6;--re-doux:#AEB8CC;--re-trait:#3A4560;--re-accent:#6FE0F2;--re-choisi:#173543;--re-etoile:#FFC857}}',
    ':root[data-theme=dark] .retour-eleve{--re-fond:#151926;--re-encre:#E9EDF6;--re-doux:#AEB8CC;--re-trait:#3A4560;--re-accent:#6FE0F2;--re-choisi:#173543;--re-etoile:#FFC857}',
    '.retour-eleve *{box-sizing:border-box}',
    '.retour-eleve h2{font-size:1.15rem;margin:0 0 .2rem;line-height:1.25}',
    '.retour-eleve .re-chapo{margin:0 0 .8rem;color:var(--re-doux);font-size:.95rem}',
    '.retour-eleve fieldset{border:0;margin:0 0 .75rem;padding:0;min-width:0}',
    '.retour-eleve legend{font-weight:700;padding:0;margin:0 0 .3rem}',
    '.retour-eleve .re-choix{display:flex;flex-wrap:wrap;gap:.4rem}',
    '.retour-eleve .re-choix label{position:relative;display:inline-flex;align-items:center;min-height:2.75rem;padding:.35rem .8rem;border:1px solid var(--re-trait);border-radius:999px;cursor:pointer;background:transparent}',
    '.retour-eleve .re-choix input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}',
    '.retour-eleve .re-choix label:has(input:checked){background:var(--re-choisi);border-color:var(--re-accent);font-weight:700}',
    '.retour-eleve .re-choix label.re-coche{background:var(--re-choisi);border-color:var(--re-accent);font-weight:700}',
    '.retour-eleve .re-choix label.re-coche::before{content:"✓ ";white-space:pre}',
    '.retour-eleve .re-choix label:focus-within{outline:3px solid var(--re-accent);outline-offset:2px}',
    '.retour-eleve .re-etoiles{display:flex;gap:.15rem}',
    '.retour-eleve .re-etoiles label{position:relative;display:inline-flex;align-items:center;justify-content:center;width:2.75rem;height:2.75rem;font-size:1.9rem;line-height:1;color:var(--re-doux);cursor:pointer;border-radius:6px}',
    '.retour-eleve .re-etoiles input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}',
    '.retour-eleve .re-etoiles label.re-allume{color:var(--re-etoile)}',
    '.retour-eleve .re-etoiles label:focus-within{outline:3px solid var(--re-accent);outline-offset:1px}',
    '.retour-eleve .re-cache{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}',
    '.retour-eleve textarea{display:block;width:100%;min-height:3.6rem;font:inherit;color:var(--re-encre);background:transparent;border:1px solid var(--re-trait);border-radius:6px;padding:.45rem .55rem;resize:vertical}',
    '.retour-eleve textarea:focus-visible{outline:3px solid var(--re-accent);outline-offset:1px}',
    '.retour-eleve .re-trio{display:flex;flex-wrap:wrap;gap:0 1.6rem}',
    '.retour-eleve .re-trio .re-choix{flex-wrap:nowrap}',
    '@media (max-width:22rem){.retour-eleve .re-trio .re-choix{flex-wrap:wrap}}',
    '.retour-eleve .re-plus{margin:0 0 .5rem}',
    '.retour-eleve .re-plus summary{cursor:pointer;color:var(--re-accent);padding:.6rem 0;width:max-content;max-width:100%}',
    '.retour-eleve .re-plus summary:focus-visible{outline:3px solid var(--re-accent);outline-offset:2px}',
    '.retour-eleve .re-plus[open] summary{margin-bottom:.4rem}',
    '.retour-eleve .re-aide{font-size:.9rem;color:var(--re-doux);margin:.25rem 0 0}',
    '.retour-eleve .re-actions{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin-top:.6rem}',
    '.retour-eleve button{font:inherit;min-height:2.75rem;padding:.4rem 1rem;border-radius:6px;border:1px solid var(--re-accent);background:var(--re-accent);color:var(--re-fond);font-weight:700;cursor:pointer}',
    '.retour-eleve button.re-discret{background:transparent;color:var(--re-accent);font-weight:400}',
    '.retour-eleve button:focus-visible{outline:3px solid var(--re-encre);outline-offset:2px}',
    '.retour-eleve button[disabled]{opacity:.6;cursor:wait}',
    '.retour-eleve .re-etat{margin:.5rem 0 0;min-height:1.4em}',
    '.retour-eleve .re-essai{font-size:.85rem;border:1px dashed var(--re-trait);border-radius:4px;padding:.2rem .5rem;display:inline-block;margin:0 0 .6rem}',
    '@media print{.retour-eleve{display:none!important}}'
  ].join('');

  function el(tag, attrs, enfants) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (attrs[k] == null || attrs[k] === false) return;
      if (k === 'texte') e.textContent = attrs[k]; else e.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    });
    (enfants || []).forEach(function (x) { if (x) e.appendChild(typeof x === 'string' ? document.createTextNode(x) : x); });
    return e;
  }
  var compteur = 0;
  function idu(p) { compteur += 1; return 're-' + p + '-' + compteur; }

  function monter(zone, cfg) {
    var ressource = (zone.getAttribute('data-retour') || '').trim();
    var td = zone.closest('[data-td]') || document.querySelector('main[data-td]');
    var partie = (zone.getAttribute('data-retour-partie') || (td && td.getAttribute('data-td')) || '').trim();
    if (!RE_RESSOURCE.test(ressource) || (partie && !RE_PARTIE.test(partie))) {
      if (window.console) console.warn('[avis] data-retour ou data-retour-partie mal écrit : « ' + ressource + ' », « ' + partie + ' ». Rien n\'est affiché.');
      return;
    }
    var nom = zone.getAttribute('data-retour-nom') || (ressource.indexOf('sequence:') === 0 ? 'cette séquence' : partie ? 'cette feuille' : 'cette activité');
    var cleStock = PREFIXE + ressource + '|' + partie;
    var classe = codeClasse();
    var etat = lire('localStorage', cleStock);
    if (!etat || typeof etat !== 'object' || !etat.cle) etat = null;

    zone.classList.add('retour-eleve');
    zone.setAttribute('aria-labelledby', idu('titre'));
    var idTitre = zone.getAttribute('aria-labelledby');
    var motPermis = !!classe && cfg.mot !== false;

    function garder(e) { etat = e; ecrire('localStorage', cleStock, e); }

    function envoyer(e, ligne, bouton) {
      if (bouton) bouton.disabled = true;
      return appeler(cfg, 'commun_retour_donner', parametres(e)).then(function (rep) {
        if (bouton) bouton.disabled = false;
        if (rep.ok) {
          e.etat = 'envoye'; e.classe_ok = !!rep.classe;
          if (!cfg.essai) garder(e); else etat = e;
          return { ok: true, rep: rep };
        }
        if (rep.plus_tard) { e.etat = 'en_attente'; if (!cfg.essai) garder(e); else etat = e; return { ok: true, attente: true }; }
        if (rep.fige) { e.etat = 'envoye'; e.fige = true; garder(e); return { ok: true, fige: true }; }
        if (ligne) ligne.textContent = rep.message || 'Ton avis n\'est pas parti. Réessaie.';
        return { ok: false };
      });
    }

    function formulaire(depart) {
      zone.textContent = '';
      var r = (depart && depart.reponses) || {};
      var titre = el('h2', { id: idTitre, tabindex: '-1', texte: 'Ton avis sur ' + nom });
      var chapo = el('p', { class: 're-chapo', texte: 'Anonyme : ni nom, ni code. Réponds à ce que tu veux, en 10 secondes. Ça sert à améliorer ' + nom + '.' });
      var bloc = [titre];
      if (cfg.essai) bloc.push(el('p', { class: 're-essai', texte: 'Essai : rien n\'est envoyé.' }));
      bloc.push(chapo);

      /* Les étoiles */
      var fsE = el('fieldset', { class: 're-q' }, [el('legend', { texte: 'Ça t\'a plu ?' })]);
      var etoiles = el('div', { class: 're-etoiles' });
      var nomE = idu('plu'), labels = [];
      function allumer(v) { labels.forEach(function (l, i) { l.classList.toggle('re-allume', i < v); l.firstChild.textContent = i < v ? '★' : '☆'; }); }
      for (var i = 1; i <= 5; i++) {
        var inp = el('input', { type: 'radio', name: nomE, value: String(i) });
        if (r.plu === i) inp.checked = true;
        var lab = el('label', null, [el('span', { 'aria-hidden': 'true', texte: '☆' }), el('span', { class: 're-cache', texte: i + (i > 1 ? ' étoiles' : ' étoile') + ' sur 5' }), inp]);
        labels.push(lab);
        etoiles.appendChild(lab);
      }
      etoiles.addEventListener('change', function () { var c = etoiles.querySelector('input:checked'); allumer(c ? +c.value : 0); });
      fsE.appendChild(etoiles);
      bloc.push(fsE);
      allumer(r.plu || 0);

      /* Les trois questions (côte à côte sur grand écran) */
      var groupes = {}, trio = el('div', { class: 're-trio' });
      bloc.push(trio);
      QUESTIONS.forEach(function (q) {
        var fs = el('fieldset', { class: 're-q' }, [el('legend', { texte: q.titre })]);
        var d = el('div', { class: 're-choix' }), n = idu(q.id);
        q.choix.forEach(function (c) {
          var input = el('input', { type: 'radio', name: n, value: c[0] });
          if (r[q.id] === c[0]) input.checked = true;
          d.appendChild(el('label', null, [c[1], input]));
        });
        d.addEventListener('change', function () { marquer(d); });
        fs.appendChild(d);
        groupes[q.id] = d;
        trio.appendChild(fs);
      });

      /* Les remarques (liste fermée) et le mot : repliés, pour que l'essentiel tienne en un écran */
      var plus = el('details', { class: 're-plus' }, [el('summary', { texte: 'Ajouter une remarque (facultatif)' })]);
      if ((r.remarques && r.remarques.length) || r.mot) plus.open = true;
      bloc.push(plus);
      var fsR = el('fieldset', { class: 're-q' }, [el('legend', { class: 're-cache', texte: 'Remarques' })]);
      var dR = el('div', { class: 're-choix' });
      REMARQUES.forEach(function (c) {
        var input = el('input', { type: 'checkbox', value: c[0] });
        if ((r.remarques || []).indexOf(c[0]) >= 0) input.checked = true;
        dR.appendChild(el('label', null, [c[1], input]));
      });
      dR.addEventListener('change', function () { marquer(dR); });
      fsR.appendChild(dR);
      plus.appendChild(fsR);

      /* Le mot libre : seulement avec une classe (lien de la classe) */
      var zoneMot = null;
      if (motPermis) {
        var idMot = idu('mot'), idAide = idu('aide');
        zoneMot = el('textarea', { id: idMot, maxlength: '140', rows: '2', 'aria-describedby': idAide, autocomplete: 'off', spellcheck: 'true' });
        zoneMot.value = r.mot || '';
        var reste = el('span', { 'aria-live': 'polite' });
        var majReste = function () { var n = 140 - Array.from(zoneMot.value).length; reste.textContent = ' ' + n + (n > 1 ? ' caractères restants.' : ' caractère restant.'); };
        zoneMot.addEventListener('input', majReste);
        majReste();
        plus.appendChild(el('div', { class: 're-q' }, [
          el('label', { for: idMot, texte: 'Un mot pour ton enseignant·e (facultatif)' }),
          zoneMot,
          el('p', { id: idAide, class: 're-aide' }, ['Seul·e ton enseignant·e le lit. N\'écris aucun nom, pas même le tien.', reste])
        ]));
      }

      var ligne = el('p', { class: 're-etat', role: 'status', 'aria-live': 'polite' });
      var bouton = el('button', { type: 'submit', texte: depart ? 'Changer mon avis' : 'Envoyer mon avis' });
      var actions = el('div', { class: 're-actions' }, [bouton]);
      if (depart) {
        var annuler = el('button', { type: 'button', class: 're-discret', texte: 'Garder mon avis' });
        annuler.addEventListener('click', function () { merci(etat, null, true); });
        actions.appendChild(annuler);
      }
      bloc.push(actions, ligne);
      var form = el('form', { novalidate: true }, bloc.slice(1));
      zone.appendChild(titre);
      zone.appendChild(form);
      [groupes.difficulte, groupes.compris, groupes.fini, dR].forEach(marquer);

      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var rep = {};
        var c = etoiles.querySelector('input:checked'); if (c) rep.plu = +c.value;
        QUESTIONS.forEach(function (q) { var x = groupes[q.id].querySelector('input:checked'); if (x) rep[q.id] = x.value; });
        rep.remarques = Array.prototype.map.call(dR.querySelectorAll('input:checked'), function (x) { return x.value; });
        var mot = zoneMot ? zoneMot.value.replace(/\s+/g, ' ').trim() : '';
        if (mot) {
          if (RE_MOT_INTERDIT.test(mot)) { ligne.textContent = 'Ton mot ne doit contenir ni adresse, ni lien, ni numéro de téléphone.'; zoneMot.focus(); return; }
          rep.mot = mot;
        }
        if (!rep.plu && !rep.difficulte && !rep.compris && !rep.fini && !rep.remarques.length && !rep.mot) {
          ligne.textContent = 'Choisis au moins une réponse (ou laisse ce cadre de côté : c\'est facultatif).';
          return;
        }
        var e = { cle: (etat && etat.cle) || nouvelleCle(), ressource: ressource, partie: partie, classe: classe,
          semaine: (etat && etat.semaine === semaine() && etat.cle) ? etat.semaine : semaine(), reponses: rep, etat: 'a_envoyer' };
        if (etat && etat.semaine !== semaine()) e.cle = nouvelleCle();
        ligne.textContent = 'Envoi…';
        envoyer(e, ligne, bouton).then(function (x) { if (x.ok) merci(e, x); });
      });
      if (depart) titre.focus();
    }

    function marquer(groupe) {
      Array.prototype.forEach.call(groupe.querySelectorAll('label'), function (l) {
        var i = l.querySelector('input'); l.classList.toggle('re-coche', !!(i && i.checked));
      });
    }

    function merci(e, x, sansFocus) {
      zone.textContent = '';
      var titre = el('h2', { id: idTitre, tabindex: '-1', texte: 'Merci pour ton avis !' });
      var texte;
      if (e.fige) texte = 'Ton avis sur ' + nom + ' est déjà gardé, sans ton nom.';
      else if (e.etat === 'en_attente') texte = 'Il est gardé sur cet appareil et partira tout seul à ta prochaine visite, sans ton nom.';
      else texte = 'Il est envoyé, sans ton nom.' + (e.classe_ok ? ' Ton enseignant·e verra les avis de la classe ensemble, à partir de 5.' : '');
      var enfants = [titre];
      if (cfg.essai) enfants.push(el('p', { class: 're-essai', texte: 'Essai : rien n\'est envoyé.' }));
      enfants.push(el('p', { class: 're-chapo', texte: texte }));
      var actions = el('div', { class: 're-actions' });
      var ligne = el('p', { class: 're-etat', role: 'status', 'aria-live': 'polite' });
      if (!e.fige && e.semaine === semaine()) {
        var changer = el('button', { type: 'button', class: 're-discret', texte: 'Changer mon avis' });
        changer.addEventListener('click', function () { formulaire(e); });
        actions.appendChild(changer);
        if (e.etat === 'envoye') {
          var retirer = el('button', { type: 'button', class: 're-discret', texte: 'Retirer mon avis' });
          retirer.addEventListener('click', function () {
            retirer.disabled = true;
            appeler(cfg, 'commun_retour_effacer', { p_cle: e.cle }).then(function (rep) {
              retirer.disabled = false;
              if (rep.ok || cfg.essai) { ecrire('localStorage', cleStock, null); etat = null; formulaire(null); var l = zone.querySelector('.re-etat'); if (l) l.textContent = 'Ton avis est retiré.'; return; }
              ligne.textContent = rep.message || 'Ton avis n\'a pas pu être retiré pour l\'instant. Réessaie plus tard.';
            });
          });
          actions.appendChild(retirer);
        }
      }
      /* Poste partagé (salle informatique) : un·e autre élève peut donner son propre avis */
      var autre = el('button', { type: 'button', class: 're-discret', texte: 'Un·e autre élève sur cet appareil ?' });
      autre.addEventListener('click', function () { ecrire('localStorage', cleStock, null); etat = null; formulaire(null); });
      actions.appendChild(autre);
      enfants.push(actions, ligne);
      enfants.forEach(function (x) { zone.appendChild(x); });
      if (!sansFocus && x) titre.focus();
    }

    /* Au chargement : un avis en attente part (sa semaine seulement), un avis envoyé dit merci */
    if (etat && etat.etat === 'en_attente' && etat.semaine === semaine()) {
      merci(etat, null, true);
      envoyer(etat, null, null).then(function () { merci(etat, null, true); });
    } else if (etat && etat.etat === 'envoye') merci(etat, null, true);
    else formulaire(null);
  }

  function demarrer() {
    var zones = document.querySelectorAll('[data-retour]');
    if (!zones.length) return;
    var essai = false;
    try { essai = new URL(location.href).searchParams.get('retour') === 'essai'; } catch (e) { /* rien */ }
    chargerReglages();
    quandReglages(function (r) {
      var cc = r.compte_commun || {};
      var url = String(cc.url || '').replace(/\/+$/, ''), cle = cc.cle_publique || '';
      var enLigne = r.RETOURS_ELEVES === true && /^https:\/\/[a-z0-9]+\.supabase\.co$/.test(url) && !!cle
        && !/service_role|sb_secret_/.test(cle);
      if (!enLigne && !essai) return; // éteint : rien ne s'affiche
      var cfg = { essai: essai || !enLigne, url: url, cle: cle, mot: r.RETOURS_ELEVES_MOT !== false };
      if (!document.getElementById('retour-eleve-style')) {
        var st = el('style', { id: 'retour-eleve-style' });
        st.textContent = STYLE;
        (document.head || document.documentElement).appendChild(st);
      }
      menage();
      Array.prototype.forEach.call(zones, function (z) { try { monter(z, cfg); } catch (e) { if (window.console) console.warn('[avis] ' + (e && e.message || e)); } });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', demarrer);
  else demarrer();

  /* Pour les essais (scripts/tests) */
  window.RetourEleve = { version: 1, semaine: semaine, questions: QUESTIONS, remarques: REMARQUES };
})();
