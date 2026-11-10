/* ═══════════════════════════════════════════════════════════════
   TD EN LIGNE — mini-site auto-correctif d'un TD (règle 19)
   Charte « Réseau la nuit », modèle de fiche et de TD (T38).

   La correction se fait dans le navigateur : rien n'est envoyé,
   aucun compte. Les réponses et les cases du bilan restent sur
   l'appareil (localStorage), effaçables par « Recommencer ».

   Les réponses attendues ne sont pas écrites en clair dans la page :
   chaque champ porte des empreintes (data-e), calculées par
   design/build/td_en_ligne.py à partir de la source. C'est contre la
   lecture d'un coup d'œil, pas contre un·e élève qui cherche vraiment :
   ce mini-site sert à s'entraîner, pas à noter.

   Types de champs (attribut data-champ = identifiant unique) :
     input.tl-saisie   valeur, mot ou nombre (data-norm : souple, exact, nombre, code)
     input.tl-trou     trou dans un code (data-norm="code")
     fieldset.tl-choix choix unique (radio) ou multiple (checkbox)
     ol.tl-ordre       éléments à remettre dans l'ordre (boutons monter / descendre)
   Une question (form.tl-q) peut avoir plusieurs champs ; elle est
   réussie quand tous sont justes. Coups de pouce gradués : ol.tl-pouces.
   Correction : div.tl-correction[data-c] (HTML en base64).
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var html = document.documentElement;
  var corps = document.body;
  var SEL = corps.getAttribute('data-sel') || '';
  var CLE = 'td-en-ligne:' + (corps.getAttribute('data-td') || location.pathname);

  /* ── Affichage clair / obscur : même réglage que le site ───── */
  function lireTheme() { try { return localStorage.getItem('theme') || 'auto'; } catch (e) { return 'auto'; } }
  function appliquerTheme(m) {
    if (m === 'light' || m === 'dark') html.setAttribute('data-theme', m);
    else html.removeAttribute('data-theme');
    var b = document.querySelector('[data-action="theme"]');
    if (b) {
      var obscur = m === 'dark' || (m === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
      b.setAttribute('aria-pressed', obscur ? 'true' : 'false');
      var t = b.querySelector('.libelle');
      if (t) t.textContent = obscur ? 'Affichage clair' : 'Affichage obscur';
    }
  }
  appliquerTheme(lireTheme());

  /* ── Normalisation et empreinte (identiques à td_en_ligne.py) ── */
  var GUILLEMETS_SIMPLES = /[’‘`´]/g;
  var GUILLEMETS_DOUBLES = /[“”«»]/g;
  var DIACRITIQUES = /\p{M}/gu;

  function normaliser(s, mode) {
    s = String(s);
    if (mode === 'exact' || mode === 'liste') return s.trim();
    if (mode === 'nombre') {
      var t = s.replace(/\s/g, '').replace(',', '.').replace(/^\+/, '');
      var m = /^(-?)(\d*)(?:\.(\d*))?$/.exec(t);
      if (!m || (m[2] === '' && (m[3] || '') === '')) return t.toLowerCase();
      var ent = m[2].replace(/^0+(?=\d)/, '') || '0';
      var dec = (m[3] || '').replace(/0+$/, '');
      var r = ent + (dec ? '.' + dec : '');
      return r === '0' ? '0' : m[1] + r;
    }
    s = s.normalize('NFC').replace(GUILLEMETS_SIMPLES, "'").replace(GUILLEMETS_DOUBLES, '"');
    if (mode === 'code') return s.replace(/'/g, '"').replace(/\s+/g, '');
    return s.normalize('NFD').replace(DIACRITIQUES, '').toLowerCase()
      .replace(/\s+/g, ' ').trim().replace(/\.$/, '');
  }

  function fnv(octets, h) {
    for (var i = 0; i < octets.length; i++) h = Math.imul(h ^ octets[i], 0x01000193) >>> 0;
    return h;
  }
  function hex8(h) { return ('0000000' + h.toString(16)).slice(-8); }
  function empreinte(champ, valeur, mode) {
    var o = new TextEncoder().encode(SEL + '|' + champ + '|' + normaliser(valeur, mode));
    var inv = Array.prototype.slice.call(o).reverse();
    return hex8(fnv(o, 0x811c9dc5)) + hex8(fnv(inv, 0x050c5d1f));
  }

  function decoder64(b64) {
    var bin = atob(b64), o = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) o[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(o);
  }

  /* ── Mémoire locale (facultative : la page marche sans) ─────── */
  var etat = { rep: {}, q: {}, bilan: {} };
  try { etat = JSON.parse(localStorage.getItem(CLE)) || etat; } catch (e) { /* navigation privée */ }
  etat.rep = etat.rep || {}; etat.q = etat.q || {}; etat.bilan = etat.bilan || {};
  function sauver() { try { localStorage.setItem(CLE, JSON.stringify(etat)); } catch (e) { /* sans mémoire */ } }

  /* ── Lecture et écriture d'un champ ─────────────────────────── */
  function valeur(ch) {
    if (ch.matches('fieldset.tl-choix')) {
      return Array.prototype.filter.call(ch.querySelectorAll('input'), function (i) { return i.checked; })
        .map(function (i) { return i.value; }).sort().join(',');
    }
    if (ch.matches('ol.tl-ordre')) {
      return Array.prototype.map.call(ch.children, function (li) { return li.getAttribute('data-v'); }).join(',');
    }
    return ch.value;
  }
  function remplir(ch, v) {
    if (v == null) return;
    if (ch.matches('fieldset.tl-choix')) {
      var liste = String(v).split(',');
      Array.prototype.forEach.call(ch.querySelectorAll('input'), function (i) { i.checked = liste.indexOf(i.value) >= 0; });
    } else if (ch.matches('ol.tl-ordre')) {
      String(v).split(',').forEach(function (id) {
        var li = ch.querySelector('[data-v="' + id + '"]');
        if (li) ch.appendChild(li);
      });
    } else ch.value = v;
  }
  function vide(ch) {
    if (ch.matches('ol.tl-ordre')) return false;
    return valeur(ch).trim() === '';
  }
  function mode(ch) {
    if (ch.matches('fieldset.tl-choix, ol.tl-ordre')) return 'liste';
    return ch.getAttribute('data-norm') || (ch.matches('.tl-trou') ? 'code' : 'souple');
  }
  function juste(ch) {
    var attendu = (ch.getAttribute('data-e') || '').split(/\s+/);
    return attendu.indexOf(empreinte(ch.getAttribute('data-champ'), valeur(ch), mode(ch))) >= 0;
  }

  /* Marque d'un champ : une icône et un mot, jamais la couleur seule */
  function marquer(ch, ok) {
    ch.classList.toggle('juste', ok === true);
    ch.classList.toggle('faux', ok === false);
    var m = ch.nextElementSibling && ch.nextElementSibling.classList.contains('tl-marque') ? ch.nextElementSibling : null;
    if (ok == null) { if (m) m.remove(); return; }
    if (!m) {
      m = document.createElement('span');
      m.className = 'tl-marque';
      ch.insertAdjacentElement('afterend', m);
    }
    var mot = ok ? 'juste' : 'à revoir';
    if (ch.matches('.tl-trou')) m.innerHTML = '<span aria-hidden="true">' + (ok ? '✓' : '✗') + '</span><span class="tl-vh"> ' + mot + '</span>';
    else m.textContent = (ok ? '✓ ' : '✗ ') + mot;
    m.className = 'tl-marque ' + (ok ? 'juste' : 'faux');
  }

  /* ── Remise en ordre : boutons monter / descendre (doigt et clavier) ── */
  function preparerOrdre(ol) {
    Array.prototype.forEach.call(ol.children, function (li) {
      var txt = li.textContent.trim();
      var b = document.createElement('span');
      b.className = 'tl-fleches';
      b.innerHTML = '<button type="button" data-sens="-1" aria-label="Monter : ' + txt.replace(/"/g, '&quot;') + '">↑</button>' +
        '<button type="button" data-sens="1" aria-label="Descendre : ' + txt.replace(/"/g, '&quot;') + '">↓</button>';
      li.appendChild(b);
    });
    ol.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-sens]');
      if (!b) return;
      var li = b.closest('li'), sens = +b.getAttribute('data-sens');
      if (sens < 0 && li.previousElementSibling) ol.insertBefore(li, li.previousElementSibling);
      if (sens > 0 && li.nextElementSibling) ol.insertBefore(li.nextElementSibling, li);
      b.focus();
      changement(ol);
    });
  }

  /* ── Les questions ──────────────────────────────────────────── */
  var questions = Array.prototype.slice.call(document.querySelectorAll('form.tl-q'));

  function champs(q) { return Array.prototype.slice.call(q.querySelectorAll('[data-champ]')); }

  function retour(q, classe, texte) {
    var r = q.querySelector('.tl-retour');
    r.className = 'tl-retour ' + classe;
    r.textContent = texte;
  }

  function afficherPouces(q, n) {
    var ol = q.querySelector('.tl-pouces');
    if (!ol) return;
    var items = ol.children;
    for (var i = 0; i < items.length; i++) items[i].hidden = i >= n;
    ol.hidden = n === 0;
  }

  function afficherCorrection(q, titre) {
    var c = q.querySelector('.tl-correction');
    if (!c) return;
    if (!c.hasAttribute('data-ouverte')) {
      c.innerHTML = '<p class="tl-correction-titre">' + titre + '</p>' + decoder64(c.getAttribute('data-c'));
      c.setAttribute('data-ouverte', '');
    } else c.querySelector('.tl-correction-titre').textContent = titre;
    c.hidden = false;
  }

  function boutonCorrection(q, visible) {
    var b = q.querySelector('[data-action="corriger"]');
    if (b) b.hidden = !visible;
  }

  function majQuestion(q) {
    var id = q.getAttribute('data-q');
    var s = etat.q[id] || {};
    var apres = +(q.getAttribute('data-correction-apres') || 1);
    afficherPouces(q, Math.min(s.erreurs || 0, (q.querySelector('.tl-pouces') || { children: [] }).children.length));
    boutonCorrection(q, !s.reussie && (s.erreurs || 0) >= apres);
    if (s.reussie) {
      retour(q, 'juste', '✓ Juste ! ' + (s.erreurs ? 'Réussi après ' + s.erreurs + (s.erreurs > 1 ? ' essais.' : ' essai.') : 'Du premier coup.'));
      afficherCorrection(q, 'Pourquoi c\'est juste');
    } else if (s.vue) {
      afficherCorrection(q, 'Correction');
    }
    q.classList.toggle('reussie', !!s.reussie);
  }

  function verifier(q) {
    var id = q.getAttribute('data-q');
    var s = etat.q[id] = etat.q[id] || {};
    var cs = champs(q);
    if (cs.some(vide)) {
      cs.forEach(function (ch) { if (vide(ch)) marquer(ch, false); });
      retour(q, 'info', 'Il manque au moins une réponse : chaque case marquée « à revoir » attend quelque chose.');
      return;
    }
    var resultats = cs.map(juste);
    cs.forEach(function (ch, i) { marquer(ch, resultats[i]); });
    var faux = resultats.filter(function (r) { return !r; }).length;
    if (!faux) {
      s.reussie = true;
    } else {
      s.erreurs = (s.erreurs || 0) + 1;
      var nb = q.querySelector('.tl-pouces') ? q.querySelector('.tl-pouces').children.length : 0;
      retour(q, 'faux', '✗ Pas encore : ' + (cs.length > 1 ? faux + ' réponse' + (faux > 1 ? 's' : '') + ' à revoir. ' : '') +
        (nb ? (s.erreurs <= nb ? 'Lis le coup de pouce ' + s.erreurs + ' ci-dessous, puis réessaie.' : 'Relis les coups de pouce, ou affiche la correction.') : 'Essaie encore.'));
    }
    sauver();
    majQuestion(q);
    majProgression();
  }

  function changement(ch) {
    marquer(ch, null);
    etat.rep[ch.getAttribute('data-champ')] = valeur(ch);
    sauver();
  }

  questions.forEach(function (q) {
    q.setAttribute('novalidate', '');
    champs(q).forEach(function (ch) {
      if (ch.matches('ol.tl-ordre')) preparerOrdre(ch);
      remplir(ch, etat.rep[ch.getAttribute('data-champ')]);
      ch.addEventListener('input', function () { changement(ch); });
      ch.addEventListener('change', function () { changement(ch); });
    });
    q.addEventListener('submit', function (e) { e.preventDefault(); verifier(q); });
    q.addEventListener('click', function (e) {
      var b = e.target.closest('[data-action="corriger"]');
      if (!b) return;
      var s = etat.q[q.getAttribute('data-q')] = etat.q[q.getAttribute('data-q')] || {};
      s.vue = true;
      sauver();
      afficherCorrection(q, 'Correction');
      b.hidden = true;
      majProgression();
    });
    majQuestion(q);
  });

  /* ── Progression (en-tête) ──────────────────────────────────── */
  function majProgression() {
    var reussies = questions.filter(function (q) { return (etat.q[q.getAttribute('data-q')] || {}).reussie; }).length;
    Array.prototype.forEach.call(document.querySelectorAll('.tl-progression'), function (p) {
      p.querySelector('b').textContent = reussies + ' / ' + questions.length;
      var barre = p.querySelector('i');
      if (barre) barre.style.setProperty('--fait', questions.length ? reussies / questions.length : 0);
    });
  }
  majProgression();

  /* ── Bilan « Je sais… » : auto-évaluation gardée sur l'appareil ── */
  Array.prototype.forEach.call(document.querySelectorAll('.tl-bilan input[type="checkbox"]'), function (c, i) {
    var id = c.id || ('bilan-' + i);
    c.checked = !!etat.bilan[id];
    c.addEventListener('change', function () { etat.bilan[id] = c.checked; sauver(); });
  });

  /* ── Barre : thème, recommencer ─────────────────────────────── */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-action]');
    if (!b) return;
    var a = b.getAttribute('data-action');
    if (a === 'theme') {
      var obscur = html.getAttribute('data-theme') === 'dark' ||
        (!html.hasAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
      var m = obscur ? 'light' : 'dark';
      try { localStorage.setItem('theme', m); } catch (err) { /* sans mémoire */ }
      appliquerTheme(m);
    }
    if (a === 'recommencer' && confirm('Effacer tes réponses et ta progression sur cet appareil ?')) {
      try { localStorage.removeItem(CLE); } catch (err) { /* sans mémoire */ }
      location.reload();
    }
  });
})();
