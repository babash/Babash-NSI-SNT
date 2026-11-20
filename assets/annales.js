/* ═══════════════════════════════════════════════════════════════
   Les annales du bac NSI par notion (T116) : pour chaque chapitre
   des fiches de révision, les exercices de bac qui le travaillent,
   avec le lien direct vers le sujet officiel (PDF) et le corrigé.
   Filtres par chapitre, année, centre et corrigé ; une vue
   imprimable (?vue=imprimer), avec un QR code par sujet, pour
   préparer un TD « type bac ».

   Données (aucune n'est écrite ici) :
   - donnees/annales/annales-bac-nsi.json : les sujets, leurs
     exercices et leurs liens (le Bibliothécaire, T104) ;
   - donnees/annales/notions-par-exercice.json : le classement des
     exercices dans les 22 chapitres, proposé par
     scripts/annales_notions.py (non vérifié tant que « verifie »
     vaut false) ;
   - donnees/referentiels/notions.json : les libellés des notions.
   L'adresse garde les filtres, la recherche et la vue : elle se
   partage telle quelle.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var O = null;
  var COULEUR = '#22D3EE';
  var A_CLASSER = 'a-classer';
  var PAR_PAGE = 40;

  var exercices = [];        // un objet par exercice, tout prêt pour l'affichage
  var chapitres = [];        // les 22 chapitres, dans l'ordre des fiches
  var chapitreParId = {};
  var libelles = {};         // notion → libellé
  var classement = null;     // notions-par-exercice.json
  var annales = null;

  var etat = { q: '', chapitre: [], annee: [], centre: [], corrige: false, tri: 'recent', vue: 'liste', nombre: PAR_PAGE };
  var ui = {};

  var TRIS = [
    { id: 'recent', nom: 'les plus récents d\'abord' },
    { id: 'ancien', nom: 'les plus anciens d\'abord' },
    { id: 'points', nom: 'les plus longs d\'abord (points)' }
  ];

  /* ── Outils ─────────────────────────────────────────────────── */

  function el(tag, attrs, enfants) { return O.el(tag, attrs, enfants); }

  function normal(s) { return O.sansAccents(String(s || '')).toLowerCase(); }

  function unique(t) {
    return t.filter(function (x, i) { return x != null && t.indexOf(x) === i; });
  }

  function texteFiltre(id) {
    if (id === A_CLASSER) return 'À classer';
    var c = chapitreParId[id];
    return c ? c.titre : id;
  }

  /* Une adresse sûre (https seulement), encodée pour le QR code (é → %C3%A9) */
  function adresseSure(u) {
    try {
      var x = new URL(u);
      return x.protocol === 'https:' ? x.href : null;
    } catch (e) { return null; }
  }

  function domaine(u) {
    try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; }
  }

  /* ── Les données : lecture et contrôle ─────────────────────── */

  function lireJson(chemin) {
    return fetch(O.racine + chemin).then(function (r) {
      if (!r.ok) throw new Error(chemin + ' : ' + (r.status === 404 ? 'fichier introuvable' : 'code ' + r.status));
      return r.json();
    });
  }

  /* Le lien du sujet : le « principal » de la fiche du sujet, sinon le premier sujet connu */
  function lienSujet(s) {
    var l = s.liens || {};
    var cles = [s.principal, 'sujet_aeif', 'sujet_kxs'];
    for (var i = 0; i < cles.length; i++) {
      var x = cles[i] && l[cles[i]];
      if (x && adresseSure(x.url)) return { url: adresseSure(x.url), source: x.source || domaine(x.url), etat: x.etat || '' };
    }
    var autre = O.liste(l.autres).filter(function (a) { return a.role === 'sujet' && adresseSure(a.url); })[0];
    return autre ? { url: adresseSure(autre.url), source: autre.source || domaine(autre.url), etat: autre.etat || '' } : null;
  }

  /* Les autres versions du sujet (une autre mise en page, une autre source) */
  function autresSujets(s, principal) {
    var l = s.liens || {};
    var t = [];
    ['sujet_aeif', 'sujet_kxs'].forEach(function (k) {
      if (l[k] && adresseSure(l[k].url) && (!principal || adresseSure(l[k].url) !== principal.url)) {
        t.push({ url: adresseSure(l[k].url), source: l[k].source || domaine(l[k].url), etat: l[k].etat || '' });
      }
    });
    O.liste(l.autres).forEach(function (a) {
      if (a.role === 'sujet' && adresseSure(a.url) && (!principal || adresseSure(a.url) !== principal.url)) {
        t.push({ url: adresseSure(a.url), source: a.source || domaine(a.url), etat: a.etat || '' });
      }
    });
    return t;
  }

  /* Les corrigés : l'AEIF d'abord (licence connue), puis kxs (non officiel), puis les autres */
  function corriges(s) {
    var l = s.liens || {};
    var t = [];
    ['corrige_aeif', 'corrige_kxs'].forEach(function (k) {
      if (l[k] && adresseSure(l[k].url)) t.push({ url: adresseSure(l[k].url), source: l[k].source || domaine(l[k].url), etat: l[k].etat || '' });
    });
    O.liste(l.autres).forEach(function (a) {
      if (/^corrig/.test(a.role || '') && adresseSure(a.url)) t.push({ url: adresseSure(a.url), source: a.source || domaine(a.url), etat: a.etat || '' });
    });
    return t;
  }

  function nomSujet(s) {
    var t = s.centre || 'Sujet';
    if (s.session && !/sujet 0/i.test(s.session) && String(s.session) !== String(s.annee)) t += ', ' + s.session;
    if (s.jour) t += ', jour ' + s.jour;
    else if (/bis$/.test(s.id)) t += ', sujet de secours';
    else if (/-0-([a-z])$/.test(s.id)) t += ' ' + s.id.slice(-1).toUpperCase();
    return t;
  }

  function preparer(donnees, notionsJson, classes) {
    var problemes = [];
    annales = donnees;
    classement = classes;
    O.liste(notionsJson && notionsJson.notions).forEach(function (n) { if (n && n.id) libelles[n.id] = n.libelle || n.id; });

    chapitres = O.liste(classes && classes.chapitres).filter(function (c) { return c && c.id && c.titre; });
    chapitres.forEach(function (c) { chapitreParId[c.id] = c; });
    if (!chapitres.length) problemes.push('donnees/annales/notions-par-exercice.json : aucun chapitre (le classement par chapitre est absent).');
    var parExercice = (classes && classes.exercices) || {};

    var sujets = O.liste(donnees && donnees.epreuve_ecrite && donnees.epreuve_ecrite.sujets);
    if (!sujets.length) throw new Error('donnees/annales/annales-bac-nsi.json : aucun sujet dans epreuve_ecrite.sujets');
    sujets.forEach(function (s) {
      if (!s || !s.id) { problemes.push('Un sujet sans identifiant est ignoré.'); return; }
      var principal = lienSujet(s);
      if (!principal) problemes.push(s.id + ' : aucun lien de sujet en https.');
      var cor = corriges(s);
      var autres = autresSujets(s, principal);
      O.liste(s.exercices).forEach(function (x) {
        var id = s.id + '#' + x.n;
        var c = parExercice[id];
        if (chapitres.length && !c) problemes.push(id + ' : absent du classement (relancer scripts/annales_notions.py).');
        var chaps = c ? O.liste(c.chapitres).map(function (k) { return k.chapitre; }).filter(function (k) {
          if (chapitreParId[k]) return true;
          problemes.push(id + ' : chapitre inconnu « ' + k + ' ».');
          return false;
        }) : [];
        exercices.push({
          id: id,
          ancre: 'ex-' + O.slug(s.id) + '-' + x.n,
          sujet: s,
          n: x.n,
          points: typeof x.points === 'number' ? x.points : null,
          pages: Array.isArray(x.pages) && x.pages.length === 2 ? x.pages : null,
          resume: x.resume || '',
          notions: O.liste(x.notions),
          chapitres: chaps,
          indices: c ? O.liste(c.chapitres) : [],
          aVerifier: c ? O.liste(c.a_verifier) : [],
          verifie: !!(c && c.verifie === true),
          lien: principal,
          autres: autres,
          corriges: cor,
          texte: normal([x.resume, s.centre, s.annee, s.session, s.code_officiel].concat(O.liste(x.notions).map(function (n) { return libelles[n] || n; })).join(' '))
        });
      });
    });
    return problemes;
  }

  /* ── L'adresse ──────────────────────────────────────────────── */

  function lireAdresse() {
    var p;
    try { p = new URLSearchParams(location.search); } catch (e) { return; }
    function plusieurs(nom) { return (p.get(nom) || '').split(',').map(function (x) { return x.trim(); }).filter(Boolean); }
    etat.q = p.get('q') || '';
    etat.chapitre = plusieurs('chapitre');
    etat.annee = plusieurs('annee');
    etat.centre = plusieurs('centre');
    etat.corrige = p.get('corrige') === '1';
    etat.tri = TRIS.some(function (t) { return t.id === p.get('tri'); }) ? p.get('tri') : 'recent';
    etat.vue = p.get('vue') === 'imprimer' ? 'imprimer' : 'liste';
  }

  function ecrireAdresse() {
    try {
      var u = new URL(location.href);
      ['q', 'chapitre', 'annee', 'centre', 'corrige', 'tri', 'vue'].forEach(function (k) { u.searchParams.delete(k); });
      if (etat.q) u.searchParams.set('q', etat.q);
      if (etat.chapitre.length) u.searchParams.set('chapitre', etat.chapitre.join(','));
      if (etat.annee.length) u.searchParams.set('annee', etat.annee.join(','));
      if (etat.centre.length) u.searchParams.set('centre', etat.centre.join(','));
      if (etat.corrige) u.searchParams.set('corrige', '1');
      if (etat.tri !== 'recent') u.searchParams.set('tri', etat.tri);
      if (etat.vue === 'imprimer') u.searchParams.set('vue', 'imprimer');
      history.replaceState(null, '', u.href);
    } catch (e) { /* sans importance */ }
  }

  /* ── Les filtres ────────────────────────────────────────────── */

  var FACETTES = [
    {
      id: 'chapitre', nom: 'Chapitre (fiche de révision)',
      valeurs: function (x) { return x.chapitres.length ? x.chapitres : [A_CLASSER]; },
      liste: function () { return chapitres.map(function (c) { return c.id; }).concat(A_CLASSER); },
      texte: texteFiltre,
      aide: 'Un exercice coché dans plusieurs chapitres apparaît dans chacun. Classement automatique, à vérifier.'
    },
    {
      id: 'annee', nom: 'Année',
      valeurs: function (x) { return [String(x.sujet.annee)]; },
      liste: function () {
        return unique(exercices.map(function (x) { return String(x.sujet.annee); })).sort().reverse();
      },
      texte: function (v) { return v; }
    },
    {
      id: 'centre', nom: 'Centre d\'examen',
      valeurs: function (x) { return [x.sujet.centre || '?']; },
      liste: function () {
        return unique(exercices.map(function (x) { return x.sujet.centre || '?'; }))
          .sort(function (a, b) { return normal(a).localeCompare(normal(b), 'fr'); });
      },
      texte: function (v) { return v; }
    }
  ];

  function passe(x, sauf) {
    if (etat.q) {
      var mots = normal(etat.q).split(/\s+/).filter(Boolean);
      if (!mots.every(function (m) { return x.texte.indexOf(m) >= 0; })) return false;
    }
    if (etat.corrige && sauf !== 'corrige' && !x.corriges.length) return false;
    return FACETTES.every(function (F) {
      if (F.id === sauf || !etat[F.id].length) return true;
      var v = F.valeurs(x);
      return etat[F.id].some(function (c) { return v.indexOf(c) >= 0; });
    });
  }

  function basculer(F, v, coche) {
    var t = etat[F.id].filter(function (x) { return x !== v; });
    if (coche) t.push(v);
    etat[F.id] = t;
    etat.nombre = PAR_PAGE;
    ecrireAdresse();
    rendre();
  }

  function caseFiltre(idFacette, v, texte, n, coche, quand) {
    var id = 'f-' + idFacette + '-' + O.slug(v);
    var input = el('input', { type: 'checkbox', id: id, checked: coche ? true : null });
    input.addEventListener('change', function () {
      quand(input.checked);
      var x = document.getElementById(id);
      if (x) x.focus();
    });
    return el('label', { class: 'filtre-case' + (n || coche ? '' : ' est-vide'), for: id }, [
      input, el('span', { class: 'filtre-nom' }, texte), el('span', { class: 'nb' }, String(n))
    ]);
  }

  function rendreFiltres() {
    O.vider(ui.filtres);
    FACETTES.forEach(function (F) {
      var n = {};
      exercices.forEach(function (x) {
        if (!passe(x, F.id)) return;
        F.valeurs(x).forEach(function (v) { n[v] = (n[v] || 0) + 1; });
      });
      var ul = el('ul', { class: 'filtre-valeurs' });
      F.liste().forEach(function (v) {
        var coche = etat[F.id].indexOf(v) >= 0;
        ul.appendChild(el('li', null, caseFiltre(F.id, v, F.texte(v), n[v] || 0, coche, function (c) { basculer(F, v, c); })));
      });
      var d = el('details', { class: 'facette', open: F.id === 'chapitre' || etat[F.id].length ? true : null }, [
        el('summary', null, F.nom + (etat[F.id].length ? ' (' + etat[F.id].length + ')' : '')),
        F.aide ? el('p', { class: 'filtre-aide' }, F.aide) : null,
        ul
      ]);
      ui.filtres.appendChild(d);
    });
    var nc = exercices.filter(function (x) { return passe(x, 'corrige') && x.corriges.length; }).length;
    ui.filtres.appendChild(el('details', { class: 'facette', open: true }, [
      el('summary', null, 'Corrigé'),
      el('ul', { class: 'filtre-valeurs' }, el('li', null, caseFiltre('corrige', 'oui', 'Avec un corrigé en ligne', nc, etat.corrige, function (c) {
        etat.corrige = c;
        etat.nombre = PAR_PAGE;
        ecrireAdresse();
        rendre();
      })))
    ]));
    var actifs = etat.chapitre.length + etat.annee.length + etat.centre.length + (etat.corrige ? 1 : 0);
    ui.nbFiltres.textContent = actifs ? '(' + actifs + ')' : '';
  }

  /* ── La liste ───────────────────────────────────────────────── */

  function trier(t) {
    function cle(x) { return [x.sujet.annee || 0, normal(x.sujet.centre), x.sujet.jour || 0, x.n || 0]; }
    return t.slice().sort(function (a, b) {
      if (etat.tri === 'points' && (b.points || 0) !== (a.points || 0)) return (b.points || 0) - (a.points || 0);
      var ka = cle(a), kb = cle(b);
      var sens = etat.tri === 'ancien' ? 1 : -1;
      if (ka[0] !== kb[0]) return sens * (ka[0] - kb[0]);
      if (ka[1] !== kb[1]) return ka[1] < kb[1] ? -1 : 1;
      if (ka[2] !== kb[2]) return ka[2] - kb[2];
      return ka[3] - kb[3];
    });
  }

  function lienExterne(url, texte, classe) {
    return el('a', { class: classe, href: url, target: '_blank', rel: 'noopener' }, texte);
  }

  function petitEtat(etatLien) {
    return /non test/.test(etatLien || '') ? ' (lien non testé)' : '';
  }

  function blocExercice(x) {
    var s = x.sujet;
    var li = el('li', { class: 'res exercice', id: x.ancre, style: '--hl:' + COULEUR });
    var titre = s.annee + ' · ' + nomSujet(s) + ' · exercice ' + x.n;
    li.appendChild(x.lien ? lienExterne(x.lien.url, titre, 'titre') : el('span', { class: 'titre sans-lien' }, titre));

    var meta = [];
    if (x.points != null) meta.push(x.points + ' points');
    else meta.push('points non indiqués');
    if (x.pages) meta.push('pages ' + x.pages[0] + ' à ' + x.pages[1] + (s.mise_en_page_des_pages ? ' (mise en page ' + s.mise_en_page_des_pages + ')' : ''));
    if (s.code_officiel) meta.push(s.code_officiel);
    li.appendChild(el('p', { class: 'chemin' }, meta.join(' · ')));

    if (x.resume) li.appendChild(el('p', null, x.resume));

    var chaps = el('p', { class: 'puces-exercice' });
    if (x.chapitres.length) {
      chaps.appendChild(el('span', { class: 'puce-quoi' }, 'Chapitres : '));
      x.chapitres.forEach(function (c) {
        var b = el('button', { type: 'button', class: 'puce', title: 'Voir tous les exercices de ce chapitre' }, texteFiltre(c));
        b.addEventListener('click', function () {
          etat.chapitre = [c];
          etat.nombre = PAR_PAGE;
          ecrireAdresse();
          rendre();
          ui.main.focus();
        });
        chaps.appendChild(b);
      });
    } else {
      chaps.appendChild(el('span', { class: 'puce-quoi' }, 'À classer : aucun indice dans l\'en-tête de l\'exercice.'));
    }
    li.appendChild(chaps);

    if (x.notions.length) {
      var tags = el('p', { class: 'tags' });
      x.notions.forEach(function (n) { tags.appendChild(el('span', null, libelles[n] || n)); });
      tags.appendChild(el('span', { class: 'site' }, x.verifie ? 'classement vérifié' : 'classement automatique, à vérifier'));
      li.appendChild(tags);
    }

    var liens = el('p', { class: 'annexes' });
    if (x.lien) {
      liens.appendChild(el('span', { class: 'annexe' }, [
        lienExterne(x.lien.url, 'Sujet'), ' ', el('span', { class: 'type' }, '(PDF, ' + x.lien.source + petitEtat(x.lien.etat) + ')')
      ]));
    }
    x.corriges.forEach(function (c, i) {
      liens.appendChild(el('span', { class: 'annexe' }, [
        lienExterne(c.url, i ? 'Autre corrigé' : 'Corrigé'), ' ', el('span', { class: 'type' }, '(PDF, ' + c.source + petitEtat(c.etat) + ')')
      ]));
    });
    x.autres.forEach(function (a) {
      liens.appendChild(el('span', { class: 'annexe' }, [
        lienExterne(a.url, 'Autre version du sujet'), ' ', el('span', { class: 'type' }, '(' + a.source + petitEtat(a.etat) + ')')
      ]));
    });
    if (!x.corriges.length) liens.appendChild(el('span', { class: 'annexe sans-corrige' }, 'Pas de corrigé trouvé'));
    li.appendChild(liens);
    if (x.aVerifier.length) {
      li.appendChild(el('p', { class: 'raison' }, 'À vérifier : ' + x.aVerifier.map(function (v) {
        return texteFiltre(v.chapitre) + ' (' + v.raison + ')';
      }).join(' ; ') + '.'));
    }
    return li;
  }

  function puces() {
    var p = el('div', { class: 'puces', 'aria-label': 'Filtres actifs' });
    function puce(quoi, texte, retirer) {
      var b = el('button', { type: 'button', class: 'puce', title: 'Retirer ce filtre' }, [
        el('span', { class: 'puce-quoi' }, quoi + ' : '), texte, el('span', { 'aria-hidden': 'true' }, ' ×')
      ]);
      b.addEventListener('click', function () { retirer(); etat.nombre = PAR_PAGE; ecrireAdresse(); rendre(); });
      p.appendChild(b);
    }
    if (etat.q) puce('Recherche', etat.q, function () { etat.q = ''; if (ui.recherche) ui.recherche.input.value = ''; });
    FACETTES.forEach(function (F) {
      etat[F.id].forEach(function (v) {
        puce(F.nom.replace(/ \(.*\)$/, ''), F.texte(v), function () { etat[F.id] = etat[F.id].filter(function (x) { return x !== v; }); });
      });
    });
    if (etat.corrige) puce('Corrigé', 'avec un corrigé', function () { etat.corrige = false; });
    if (p.childNodes.length > 1) {
      var tout = el('button', { type: 'button', class: 'lien-bouton' }, 'Tout effacer');
      tout.addEventListener('click', function () {
        etat.q = ''; etat.chapitre = []; etat.annee = []; etat.centre = []; etat.corrige = false; etat.nombre = PAR_PAGE;
        if (ui.recherche) ui.recherche.input.value = '';
        ecrireAdresse(); rendre();
      });
      p.appendChild(tout);
    }
    return p.childNodes.length ? p : null;
  }

  function barreOutils(n) {
    var barre = el('div', { class: 'outils-resultats' });
    barre.appendChild(el('p', { class: 'compte', 'aria-live': 'polite' }, O.pluriel(n, 'exercice', 'exercices')));
    var sel = el('select', { id: 'tri' });
    TRIS.forEach(function (t) { sel.appendChild(el('option', { value: t.id, selected: t.id === etat.tri ? true : null }, t.nom)); });
    sel.addEventListener('change', function () { etat.tri = sel.value; ecrireAdresse(); rendre(); });
    barre.appendChild(el('div', { class: 'tri' }, [el('label', { for: 'tri' }, 'Trier :'), sel]));
    var imp = el('button', { type: 'button', class: 'bouton-annales' }, 'Version imprimable');
    imp.addEventListener('click', function () { etat.vue = 'imprimer'; ecrireAdresse(); rendre(); window.scrollTo(0, 0); });
    barre.appendChild(imp);
    return barre;
  }

  function note() {
    var src = (annales && annales.verifie_le) ? ' Liens vérifiés le ' + dateFr(annales.verifie_le) + '.' : '';
    return el('div', { class: 'note' }, [
      el('p', null, [
        'Les exercices de l\'épreuve écrite de terminale depuis 2021, rangés dans les chapitres des ',
        el('a', { href: 'https://babash.github.io/FichesNSI/' }, 'fiches de révision'),
        '. Le classement est déduit de l\'en-tête de chaque exercice (« Cet exercice porte sur… ») : il reste à vérifier. '
          + 'Les en-têtes ne nomment presque jamais les variables, les boucles ou les fonctions, que tous les exercices utilisent.'
      ]),
      el('p', { class: 'petit' }, 'On lie, on n\'héberge pas : chaque lien mène au PDF sur le site qui le publie (AEIF, kxs, Math93…). '
        + 'Les sujets restent ceux du ministère ; les corrigés de kxs ne sont pas officiels ; seule l\'AEIF indique une licence (CC BY-SA 4.0). '
        + 'Les pages d\'un exercice sont celles de la mise en page indiquée.' + src)
    ]);
  }

  function dateFr(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    return m ? m[3] + '/' + m[2] + '/' + m[1] : iso;
  }

  /* ── La vue imprimable ──────────────────────────────────────── */

  function qr(url) {
    if (typeof window.qrcode !== 'function' || !url) return null;
    try {
      var q = window.qrcode(0, 'M');
      q.addData(url);
      q.make();
      return el('span', { class: 'qr', 'aria-hidden': 'true', html: q.createSvgTag({ cellSize: 2, margin: 2, scalable: true }) });
    } catch (e) {
      if (window.console) console.warn('[annales] QR code impossible pour ' + url, e);
      return null;
    }
  }

  function titreFeuille() {
    var morceaux = [];
    if (etat.chapitre.length) morceaux.push(etat.chapitre.map(texteFiltre).join(', '));
    if (etat.annee.length) morceaux.push(etat.annee.join(', '));
    if (etat.centre.length) morceaux.push(etat.centre.join(', '));
    if (etat.q) morceaux.push('« ' + etat.q + ' »');
    return morceaux.length ? morceaux.join(' · ') : 'tous les chapitres';
  }

  function vueImprimable(liste) {
    var feuille = el('section', { class: 'feuille-annales', 'aria-label': 'Version imprimable' });
    var boutons = el('p', { class: 'actions-feuille' });
    var imprimer = el('button', { type: 'button', class: 'bouton-annales' }, 'Imprimer');
    imprimer.addEventListener('click', function () { window.print(); });
    var retour = el('button', { type: 'button', class: 'lien-bouton' }, 'Revenir à la liste');
    retour.addEventListener('click', function () { etat.vue = 'liste'; ecrireAdresse(); rendre(); });
    boutons.appendChild(imprimer);
    boutons.appendChild(retour);
    feuille.appendChild(boutons);

    feuille.appendChild(el('h2', null, 'Exercices de bac NSI : ' + titreFeuille()));
    feuille.appendChild(el('p', { class: 'petit' }, O.pluriel(liste.length, 'exercice', 'exercices')
      + ' de l\'épreuve écrite de terminale. Classement automatique par chapitre, à vérifier sur le sujet. '
      + 'Chaque QR code ouvre le sujet (PDF) sur le site qui le publie.'));

    if (!liste.length) {
      feuille.appendChild(el('p', { class: 'vide' }, 'Aucun exercice avec ces filtres.'));
      return feuille;
    }
    var table = el('table', { class: 'table-annales' });
    table.appendChild(el('thead', null, el('tr', null, [
      el('th', { scope: 'col' }, 'Sujet'), el('th', { scope: 'col' }, 'Ex.'), el('th', { scope: 'col' }, 'Points'),
      el('th', { scope: 'col' }, 'Ce que l\'exercice travaille'), el('th', { scope: 'col' }, 'Sujet en ligne')
    ])));
    var tb = el('tbody');
    liste.forEach(function (x) {
      var s = x.sujet;
      var cor = x.corriges[0];
      tb.appendChild(el('tr', null, [
        el('td', null, [el('strong', null, String(s.annee)), el('br'), nomSujet(s),
          s.code_officiel ? el('span', { class: 'code' }, s.code_officiel) : null]),
        el('td', { class: 'nombre' }, String(x.n)),
        el('td', { class: 'nombre' }, x.points != null ? String(x.points) : '?'),
        el('td', null, [x.resume || '',
          x.pages ? el('span', { class: 'petit bloc' }, 'Pages ' + x.pages[0] + ' à ' + x.pages[1]
            + (s.mise_en_page_des_pages ? ' (' + s.mise_en_page_des_pages + ')' : '')) : null,
          el('span', { class: 'petit bloc' }, cor ? 'Corrigé : ' + cor.source : 'Pas de corrigé trouvé')]),
        el('td', { class: 'lien-qr' }, x.lien ? [qr(x.lien.url), lienExterne(x.lien.url, x.lien.url, 'url')] : '?')
      ]));
    });
    table.appendChild(tb);
    feuille.appendChild(table);
    feuille.appendChild(el('p', { class: 'petit pied-feuille' }, 'Sources : ' + (location.href.split('#')[0]) + ' · '
      + 'inventaire des annales vérifié le ' + dateFr(annales && annales.verifie_le) + '.'));
    return feuille;
  }

  /* ── Rendu ──────────────────────────────────────────────────── */

  function rendre() {
    document.body.classList.toggle('vue-imprimer', etat.vue === 'imprimer');
    rendreFiltres();
    O.vider(ui.main);
    var liste = trier(exercices.filter(function (x) { return passe(x); }));
    if (etat.vue === 'imprimer') {
      ui.main.appendChild(vueImprimable(liste));
      return;
    }
    ui.main.appendChild(barreOutils(liste.length));
    var p = puces();
    if (p) ui.main.appendChild(p);
    ui.main.appendChild(note());
    if (etat.chapitre.length === 1 && chapitreParId[etat.chapitre[0]]) {
      var c = chapitreParId[etat.chapitre[0]];
      ui.main.appendChild(el('p', { class: 'petit' }, [
        'Fiche de révision : ', el('a', { href: c.fiche }, c.titre), ' (' + c.niveau + ').'
      ]));
    }
    if (!liste.length) {
      ui.main.appendChild(el('p', { class: 'vide' }, 'Aucun exercice avec ces filtres.'));
      return;
    }
    var ul = el('ul', { class: 'ressources resultats liste-exercices' });
    liste.slice(0, etat.nombre).forEach(function (x) { ul.appendChild(blocExercice(x)); });
    ui.main.appendChild(ul);
    if (liste.length > etat.nombre) {
      var plus = el('button', { type: 'button', class: 'bouton-annales plus' }, 'Afficher ' + Math.min(PAR_PAGE, liste.length - etat.nombre) + ' exercices de plus');
      plus.addEventListener('click', function () { etat.nombre += PAR_PAGE; rendre(); });
      ui.main.appendChild(plus);
    }
  }

  function alerte(titre, lignes) {
    ui.alerte.appendChild(el('div', { class: 'alerte', role: 'alert' }, [
      el('p', null, el('strong', null, titre)),
      el('ul', { class: 'petit' }, lignes.slice(0, 12).map(function (l) { return el('li', null, l); }).concat(
        lignes.length > 12 ? [el('li', null, 'et ' + (lignes.length - 12) + ' autres.')] : []))
    ]));
  }

  function construire(racine) {
    racine.appendChild(O.barreHaut('bibliotheque'));
    var page = el('div', { class: 'page bibliotheque annales' });
    racine.appendChild(page);
    var bandeau = el('header', { class: 'hero hero-rubrique', style: '--hl:' + COULEUR, html: O.scene(COULEUR, 11) });
    ui.chapo = el('p', { class: 'chapo' }, 'Pour chaque chapitre, les exercices de bac qui le travaillent, avec le sujet officiel et son corrigé.');
    ui.recherche = O.champRecherche('Chercher dans les énoncés (ex. Huffman, RIP, pile)', function (q) {
      etat.q = q;
      etat.nombre = PAR_PAGE;
      ecrireAdresse();
      rendre();
    });
    bandeau.appendChild(el('div', { class: 'hero-contenu' }, [
      el('p', { class: 'invite', 'aria-hidden': 'true' }, '~/bibliotheque/annales'),
      el('h1', null, 'Annales du bac NSI par notion'),
      ui.chapo,
      ui.recherche.bloc
    ]));
    page.appendChild(bandeau);
    ui.alerte = el('div');
    page.appendChild(ui.alerte);

    var corps = el('div', { class: 'rub-corps' });
    ui.filtres = el('div', { class: 'filtres-liste' });
    ui.nbFiltres = el('span', { class: 'nb' });
    ui.panneau = el('details', { class: 'filtres' }, [el('summary', null, ['Filtres ', ui.nbFiltres]), ui.filtres]);
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

  window.pageAnnales = function (racine, outils) {
    O = outils;
    construire(racine);
    if (O.surDisque) {
      alerte('La page a besoin d\'un petit serveur', ['Ouverte depuis le disque, elle ne peut pas lire ses données : '
        + 'lancer « python3 -m http.server » à la racine du dépôt, puis ouvrir http://localhost:8000/bibliotheque/annales/.']);
      return;
    }
    lireAdresse();
    if (ui.recherche) ui.recherche.input.value = etat.q;
    ui.main.appendChild(el('p', { class: 'vide' }, 'Chargement des annales…'));
    Promise.all([
      lireJson('donnees/annales/annales-bac-nsi.json'),
      lireJson('donnees/annales/notions-par-exercice.json').catch(function (e) { return { erreur: e }; }),
      lireJson('donnees/referentiels/notions.json').catch(function (e) { return { erreur: e }; })
    ]).then(function (r) {
      var problemes = [];
      if (r[1].erreur) problemes.push('Le classement par chapitre n\'a pas pu être lu (' + r[1].erreur.message + ') : tous les exercices sont « à classer ».');
      if (r[2].erreur) problemes.push('Les libellés des notions n\'ont pas pu être lus (' + r[2].erreur.message + ') : les identifiants s\'affichent à leur place.');
      problemes = problemes.concat(preparer(r[0], r[2].erreur ? null : r[2], r[1].erreur ? null : r[1]));
      etat.chapitre = etat.chapitre.filter(function (c) { return c === A_CLASSER || chapitreParId[c]; });
      if (problemes.length) {
        problemes.forEach(function (p) { if (window.console) console.warn('[annales] ' + p); });
        alerte('Des données des annales sont incomplètes', problemes);
      }
      var nSujets = O.liste(r[0].epreuve_ecrite.sujets).length;
      var annees = unique(exercices.map(function (x) { return x.sujet.annee; })).sort();
      ui.chapo.textContent = O.pluriel(exercices.length, 'exercice', 'exercices') + ' de ' + O.pluriel(nSujets, 'sujet', 'sujets')
        + ' (' + annees[0] + '-' + annees[annees.length - 1] + ') : pour chaque chapitre, les exercices de bac qui le travaillent, '
        + 'avec le sujet officiel et son corrigé.';
      ecrireAdresse();
      rendre();
    }).catch(function (e) {
      O.vider(ui.main);
      alerte('Les annales n\'ont pas pu se charger', ['Le fichier donnees/annales/annales-bac-nsi.json n\'a pas pu être lu ('
        + (e && e.message || e) + ').']);
      if (window.console) console.error(e);
    });
  };
})();
