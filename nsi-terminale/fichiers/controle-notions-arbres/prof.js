/* Contrôle de notions : page enseignant·e
   Lit les codes (collés ou scannés), corrige avec cle.js, exporte en CSV.
   Les copies lues sont gardées dans ce navigateur seulement (localStorage),
   UN JOUR au plus après leur lecture, puis effacées (au chargement et pendant
   que la page est ouverte). L'export CSV est rappelé avant l'effacement.
   Babash - NSI Tani Malandi · MIT */

(function () {
  'use strict';
  var CN = window.CN, CLE = window.CLE, D = CN.DONNEES, $ = function (id) { return document.getElementById(id); };
  var STOCK = 'controle-' + D.id + '-v' + D.version + '-prof';
  var UN_JOUR = 24 * 60 * 60 * 1000;
  var codes = [];      /* les codes lus, tels quels */
  var lus = {};        /* code -> date de lecture (ms) */

  CN.appliquerTheme();

  function sauver() {
    try {
      if (codes.length) localStorage.setItem(STOCK, JSON.stringify(codes.map(function (c) { return { c: c, t: lus[c] }; })));
      else localStorage.removeItem(STOCK);
    } catch (e) { /* rien */ }
  }
  /* Relit les copies gardées et efface celles lues il y a un jour ou plus. Renvoie le nombre effacé. */
  function purger() {
    var garde = [], effacees = 0;
    try { garde = JSON.parse(localStorage.getItem(STOCK) || '[]'); } catch (e) { garde = []; }
    if (!Array.isArray(garde)) garde = [];
    codes = []; lus = {};
    garde.forEach(function (x) {
      if (x && typeof x.c === 'string' && typeof x.t === 'number' && Date.now() - x.t < UN_JOUR && x.t <= Date.now() + 60000) {
        codes.push(x.c); lus[x.c] = x.t;
      } else effacees++;
    });
    if (effacees) sauver();
    return effacees;
  }
  var effaceesAuChargement = purger();

  function message(texte, type) {
    var li = document.createElement('li');
    li.textContent = texte;
    if (type) li.className = type;
    $('messages').prepend(li);
    while ($('messages').children.length > 8) $('messages').lastChild.remove();
  }

  /* ── 1. Liens des sujets ── */
  var base = location.href.replace(/[^/]*([?#].*)?$/, '');
  Object.keys(D.sujets).forEach(function (s) {
    var url = base + 'index.html?sujet=' + s;
    var qr = qrcode(0, 'M'); qr.addData(url); qr.make();
    var div = document.createElement('div');
    div.className = 'lien-sujet';
    div.innerHTML = '<h3>Sujet ' + s + '</h3><div class="qr" role="img" aria-label="QR code du lien du sujet ' + s + '">' +
      qr.createSvgTag({ cellSize: 4, margin: 3, scalable: true }) + '</div><p><a href="' + CN.echapper(url) + '">' + CN.echapper(url) + '</a></p>';
    $('liens').appendChild(div);
  });

  /* ── 2. Ajouter des codes ── */
  function ajouter(liste, source) {
    var nouveaux = 0, erreurs = 0;
    liste.forEach(function (code) {
      try {
        var c = CN.decoder(code);
        if (codes.indexOf(c.code) >= 0) { message('Déjà lue : copie de ' + c.pseudo + '.'); return; }
        codes.push(c.code); lus[c.code] = Date.now(); nouveaux++;
        message('Copie de ' + c.pseudo + ' (sujet ' + c.sujet + ') ajoutée' + (source ? ' (' + source + ')' : '') + '.', 'ok');
      } catch (e) { erreurs++; message('Code refusé : ' + e.message, 'ko'); }
    });
    if (nouveaux) { sauver(); afficher(); }
    return nouveaux;
  }

  $('lire-codes').addEventListener('click', function () {
    var trouves = CN.extraireCodes($('codes').value);
    if (!trouves.length) { message('Aucun code trouvé : un code commence par ' + D.prefixe + D.version + '-.', 'ko'); return; }
    ajouter(trouves, 'collé');
    $('codes').value = '';
  });

  /* Lecture d'un QR code dans une image : BarcodeDetector si le navigateur l'a, sinon jsQR. */
  var detecteur = null;
  try { if ('BarcodeDetector' in window) detecteur = new window.BarcodeDetector({ formats: ['qr_code'] }); } catch (e) { detecteur = null; }

  function lireImage(source, l, h) {
    var toile = $('toile'), ctx = toile.getContext('2d', { willReadFrequently: true });
    toile.width = l; toile.height = h;
    ctx.drawImage(source, 0, 0, l, h);
    var img = ctx.getImageData(0, 0, l, h);
    var r = window.jsQR(img.data, l, h, { inversionAttempts: 'attemptBoth' });
    return r ? r.data : null;
  }

  function lireQR(source, l, h) {
    if (detecteur) {
      return detecteur.detect(source).then(function (t) { return t.length ? t[0].rawValue : lireImage(source, l, h); })
        .catch(function () { return lireImage(source, l, h); });
    }
    return Promise.resolve(lireImage(source, l, h));
  }

  var flux = null, enCours = false, dernier = '';
  $('camera').addEventListener('click', function () {
    if (flux) { arreter(); return; }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { message('Caméra indisponible dans ce navigateur : collez les codes.', 'ko'); return; }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false }).then(function (f) {
      flux = f;
      var v = $('video');
      v.srcObject = f; v.hidden = false; v.play();
      $('camera').textContent = 'Éteindre la caméra';
      boucle();
    }).catch(function () { message('Caméra refusée ou absente : collez les codes, ou lisez une photo.', 'ko'); });
  });
  function arreter() {
    if (flux) flux.getTracks().forEach(function (t) { t.stop(); });
    flux = null; $('video').hidden = true; $('camera').textContent = 'Allumer la caméra';
  }
  function boucle() {
    if (!flux) return;
    var v = $('video');
    if (!enCours && v.readyState >= 2 && v.videoWidth) {
      enCours = true;
      var l = Math.min(v.videoWidth, 960), h = Math.round(v.videoHeight * l / v.videoWidth);
      lireQR(v, l, h).then(function (texte) {
        enCours = false;
        if (texte && texte !== dernier) {
          dernier = texte;
          var t = CN.extraireCodes(texte);
          if (t.length) ajouter(t, 'scanné'); else message('Ce QR code n\'est pas une copie de ce contrôle.', 'ko');
        }
      });
    }
    setTimeout(boucle, 250);
  }

  $('photo').addEventListener('change', function () {
    var f = this.files && this.files[0];
    if (!f) return;
    var img = new Image();
    img.onload = function () {
      var l = Math.min(img.naturalWidth, 1600), h = Math.round(img.naturalHeight * l / img.naturalWidth);
      lireQR(img, l, h).then(function (texte) {
        var t = CN.extraireCodes(texte || '');
        if (t.length) ajouter(t, 'photo'); else message('Aucun QR code de copie trouvé sur la photo.', 'ko');
        URL.revokeObjectURL(img.src);
      });
    };
    img.src = URL.createObjectURL(f);
    this.value = '';
  });

  /* ── 3. Correction et affichage ── */
  function cleEleve(c) { return [c.pseudo.toLowerCase(), c.classe.toLowerCase(), c.sujet].join('|'); }

  function copies() {
    /* Une copie par élève et par sujet : la plus récente (un élève qui revient à ses réponses produit un nouveau code). */
    var parEleve = {}, remplacees = 0;
    codes.forEach(function (code) {
      var c; try { c = CN.decoder(code); } catch (e) { return; }
      c.fin = c.debut * 60 + c.duree;
      var k = cleEleve(c);
      if (parEleve[k]) { remplacees++; if (parEleve[k].fin > c.fin) return; }
      parEleve[k] = c;
    });
    var liste = Object.keys(parEleve).map(function (k) {
      var c = parEleve[k]; c.correction = CLE.corrigerCopie(c); return c;
    });
    liste.sort(function (a, b) { return (a.classe + a.pseudo).localeCompare(b.classe + b.pseudo, 'fr'); });
    return { liste: liste, remplacees: remplacees };
  }

  function montrer(r) {
    if (r === null || r === undefined || r === '' || (Array.isArray(r) && !r.some(function (v) { return v !== '' && v !== null; }))) return '(pas de réponse)';
    if (Array.isArray(r)) return r.map(function (v) { return v === '' || v === null ? '…' : v; }).join(', ');
    return String(r);
  }
  function montrerAttendu(q, sujet, a) {
    if (q.type === 'qcu') return a + ' : ' + optionTexte(sujet, a);
    return Array.isArray(a) ? a.join(', ') : String(a);
  }
  function optionTexte(sujet, id) {
    var o = D.sujets[sujet].abr_options.filter(function (x) { return x[0] === id; })[0];
    return o ? o[1] : '';
  }
  function montrerDonne(q, sujet, r) {
    if (q.type === 'qcu' && r) return r + ' : ' + optionTexte(sujet, r);
    if (q.type === 'schema' && Array.isArray(r) && r.length) {
      var l = CN.lettresSquelette(D.sujets[sujet].squelette);
      return l.map(function (x, i) { return x + ' = ' + (r[i] === '' || r[i] === undefined ? '…' : r[i]); }).join(', ');
    }
    return montrer(r);
  }
  function minutes(s) { return Math.round(s / 6) / 10; }

  function afficher() {
    majExpiration();
    var res = copies(), liste = res.liste, Q = D.questions;
    var aucune = !liste.length;
    ['csv', 'imprimer', 'vider'].forEach(function (id) { $(id).disabled = aucune; });
    ['cadre-table', 't-stats', 'cadre-stats', 't-details'].forEach(function (id) { $(id).hidden = aucune; });
    if (aucune) { $('resume').textContent = 'Aucune copie pour l\'instant.'; $('table').innerHTML = ''; $('stats').innerHTML = ''; $('details').innerHTML = ''; $('alertes').innerHTML = ''; return; }

    var moyenne = liste.reduce(function (s, c) { return s + c.correction.sur20; }, 0) / liste.length;
    $('resume').textContent = liste.length + ' copie' + (liste.length > 1 ? 's' : '') + ' · moyenne ' + (Math.round(moyenne * 10) / 10).toString().replace('.', ',') + ' / 20' +
      (res.remplacees ? ' · ' + res.remplacees + ' ancienne' + (res.remplacees > 1 ? 's' : '') + ' version' + (res.remplacees > 1 ? 's' : '') + ' remplacée' + (res.remplacees > 1 ? 's' : '') + ' par la plus récente' : '');

    /* Tableau des notes */
    var h = '<caption class="note" style="text-align:left;padding:.4rem .5rem">✓ juste · ✗ faux · – sans réponse</caption><thead><tr><th scope="col">Élève</th><th scope="col">Classe</th><th scope="col">Sujet</th><th scope="col">Points</th><th scope="col">/ 20</th><th scope="col">Durée</th>' +
      Q.map(function (q, i) { return '<th scope="col" title="' + CN.echapper(q.nom) + '">Q' + (i + 1) + '</th>'; }).join('') + '</tr></thead><tbody>';
    liste.forEach(function (c, n) {
      h += '<tr><th scope="row"><a href="#copie-' + n + '">' + CN.echapper(c.pseudo) + '</a></th><td>' + CN.echapper(c.classe) + '</td><td>' + c.sujet + '</td>' +
        '<td class="n">' + c.correction.points + ' / ' + c.correction.total + '</td><td class="n">' + String(c.correction.sur20).replace('.', ',') + '</td>' +
        '<td class="n">' + String(minutes(c.duree)).replace('.', ',') + ' min</td>' +
        c.correction.details.map(function (d) {
          return d.juste ? '<td class="ok" aria-label="juste">✓</td>' : (d.vide ? '<td class="vide" aria-label="sans réponse">–</td>' : '<td class="ko" aria-label="faux">✗</td>');
        }).join('') + '</tr>';
    });
    $('table').innerHTML = h + '</tbody>';

    /* Réussite par question et erreur la plus fréquente */
    var s = '<thead><tr><th scope="col">Question</th><th scope="col">Réussite</th><th scope="col"></th><th scope="col">Réponse fausse la plus fréquente</th></tr></thead><tbody>';
    Q.forEach(function (q, i) {
      var justes = 0, faux = {};
      liste.forEach(function (c) {
        var d = c.correction.details[i];
        if (d.juste) justes++;
        else if (!d.vide) { var k = 'Sujet ' + c.sujet + ' : ' + montrerDonne(q, c.sujet, c.reponses[i]); faux[k] = (faux[k] || 0) + 1; }
      });
      var pct = Math.round(100 * justes / liste.length), pire = Object.keys(faux).sort(function (a, b) { return faux[b] - faux[a]; })[0];
      s += '<tr><th scope="row">Q' + (i + 1) + ' · ' + CN.echapper(q.nom) + '</th><td class="n">' + pct + ' %</td><td><div class="stat-barre" aria-hidden="true"><span style="width:' + pct + '%"></span></div></td><td style="white-space:normal">' +
        (pire ? CN.echapper(pire) + ' (' + faux[pire] + ')' : '') + '</td></tr>';
    });
    $('stats').innerHTML = s + '</tbody>';

    /* Alertes : copies très proches (mêmes réponses fausses, même sujet) */
    var alertes = [];
    for (var a = 0; a < liste.length; a++) for (var b = a + 1; b < liste.length; b++) {
      var A = liste[a], B = liste[b];
      if (A.sujet !== B.sujet) continue;
      var communes = [];
      Q.forEach(function (q, i) {
        var da = A.correction.details[i], db = B.correction.details[i];
        if (!da.juste && !db.juste && !da.vide && JSON.stringify(CLE.formeNormale(q.type, A.reponses[i])) === JSON.stringify(CLE.formeNormale(q.type, B.reponses[i]))) communes.push('Q' + (i + 1));
      });
      if (communes.length >= 3) alertes.push(A.pseudo + ' et ' + B.pseudo + ' : mêmes réponses fausses à ' + communes.join(', '));
    }
    $('alertes').innerHTML = alertes.length ? '<div class="alerte"><strong>Copies très proches, à regarder</strong> (ce n\'est pas une preuve) :<ul>' +
      alertes.map(function (t) { return '<li>' + CN.echapper(t) + '</li>'; }).join('') + '</ul></div>' : '';

    /* Détail de chaque copie */
    $('details').innerHTML = liste.map(function (c, n) {
      return '<details class="copie" id="copie-' + n + '"><summary>' + CN.echapper(c.pseudo) + (c.classe ? ' (' + CN.echapper(c.classe) + ')' : '') +
        ' · sujet ' + c.sujet + ' · ' + c.correction.points + ' / ' + c.correction.total + '</summary>' +
        c.correction.details.map(function (d, i) {
          var q = d.question, marque = d.juste ? '<span class="ok">✓ juste</span>' : (d.vide ? '<span class="vide">– sans réponse</span>' : '<span class="ko">✗ faux</span>');
          return '<div class="rep"><span class="etiquette">Q' + (i + 1) + ' · ' + CN.echapper(q.nom) + '</span> · ' + marque +
            '<br>Réponse : <code>' + CN.echapper(montrerDonne(q, c.sujet, d.donne)) + '</code>' +
            (d.juste ? '' : '<br>Attendu : <code>' + CN.echapper(montrerAttendu(q, c.sujet, d.attendu)) + '</code><p class="texte">' + CN.echapper(d.texte) + '</p>') + '</div>';
        }).join('') + '</details>';
    }).join('');
  }

  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href^="#copie-"]');
    if (a) { var d = document.querySelector(a.getAttribute('href')); if (d) d.open = true; }
  });

  /* ── Export CSV (séparateur « ; », UTF-8 avec BOM : s'ouvre tel quel dans un tableur) ── */
  function champ(v) {
    v = String(v === undefined || v === null ? '' : v);
    return /[;"\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }
  $('csv').addEventListener('click', function () {
    var liste = copies().liste, Q = D.questions;
    var entete = ['Élève', 'Classe', 'Sujet', 'Points', 'Sur', 'Note sur 20', 'Durée (min)']
      .concat(Q.map(function (q, i) { return 'Q' + (i + 1) + ' ' + q.nom; }))
      .concat(Q.map(function (q, i) { return 'Réponse Q' + (i + 1); }));
    var lignes = [entete.map(champ).join(';')];
    liste.forEach(function (c) {
      lignes.push([c.pseudo, c.classe, c.sujet, c.correction.points, c.correction.total, String(c.correction.sur20).replace('.', ','), String(minutes(c.duree)).replace('.', ',')]
        .concat(c.correction.details.map(function (d) { return d.juste ? 1 : 0; }))
        .concat(Q.map(function (q, i) { return montrerDonne(q, c.sujet, c.reponses[i]); }))
        .map(champ).join(';'));
    });
    var blob = new Blob([String.fromCharCode(0xFEFF) + lignes.join('\r\n') + '\r\n'], { type: 'text/csv;charset=utf-8' });
    var lien = document.createElement('a');
    lien.href = URL.createObjectURL(blob);
    lien.download = 'controle-notions-arbres-' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(lien); lien.click(); lien.remove();
    setTimeout(function () { URL.revokeObjectURL(lien.href); }, 1000);
  });

  $('imprimer').addEventListener('click', function () {
    document.querySelectorAll('details.copie').forEach(function (d) { d.open = true; });
    window.print();
  });
  $('vider').addEventListener('click', function () {
    if (!confirm('Effacer toutes les copies lues de ce navigateur ? Pensez à exporter en CSV avant.')) return;
    codes = []; lus = {}; sauver(); afficher(); message('Copies effacées.');
  });

  /* Rappel d'export : la date d'effacement de la copie la plus ancienne. */
  function majExpiration() {
    var el = $('expiration');
    if (!codes.length) { el.hidden = true; return; }
    var plusAncienne = Math.min.apply(null, codes.map(function (c) { return lus[c]; }));
    var d = new Date(plusAncienne + UN_JOUR);
    el.hidden = false;
    el.innerHTML = '<strong>Exportez en CSV avant le ' + d.toLocaleDateString('fr-FR') + ' à ' +
      d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) + '.</strong> Les copies lues restent un jour dans ce navigateur, puis sont effacées.';
  }

  setInterval(function () {
    var n = purger();
    if (n) { message(n + ' copie' + (n > 1 ? 's lues il y a plus d\'un jour effacées' : ' lue il y a plus d\'un jour effacée') + ' de ce navigateur.', 'ko'); afficher(); }
  }, 60000);

  afficher();
  if (effaceesAuChargement) message(effaceesAuChargement + ' copie' + (effaceesAuChargement > 1 ? 's lues il y a plus d\'un jour effacées' : ' lue il y a plus d\'un jour effacée') + ' de ce navigateur.', 'ko');
  window.CN_PROF = { ajouter: ajouter, copies: copies };
})();
