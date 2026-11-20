/* Contrôles de notions : moteur commun (page élève, page prof, papier, corrigé)
   Babash - NSI Tani Malandi · code MIT

   Même fichier dans chaque dossier de contrôle de notions à programmes
   (piles et files, programmation objet). Les énoncés sont dans controle.js
   (window.CN_DONNEES), JAMAIS les réponses : la clé est dans cle.js, que
   seules la page prof et le corrigé chargent.

   D'après le moteur du contrôle sur les arbres binaires (T108), avec :
   - des programmes Python affichés avec numéros de ligne, filets
     d'indentation, coloration lisible aussi en noir et blanc (mots-clés en
     gras, fonctions soulignées, chaînes en italique, commentaires en gris) ;
   - des consoles compactes (une ligne de console par ligne de texte) pour
     les sorties et les messages d'erreur réels de Python 3.13 ;
   - des questions groupées (un programme commun à plusieurs questions),
     qui restent ensemble et dans l'ordre quand la copie est mélangée. */

(function () {
  'use strict';

  var D = window.CN_DONNEES;

  function echapper(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* Texte court : `code` entre accents graves → <code>, espaces fines avant ? : ; ! */
  function texte(t) {
    var s = echapper(t).replace(/ ([?:;!])/g, String.fromCharCode(0xA0) + '$1');
    return s.replace(/`([^`]+)`/g, function (m, c) { return '<code>' + c + '</code>'; });
  }

  /* ── Coloration Python ──────────────────────────────────── */

  var MOTS = ['and', 'as', 'class', 'def', 'elif', 'else', 'False', 'for', 'from', 'if', 'import', 'in', 'is',
    'None', 'not', 'or', 'pass', 'return', 'True', 'while'];

  function colorerLigne(l) {
    var out = '', i = 0, n = l.length;
    while (i < n) {
      var c = l[i];
      if (c === '#') { out += '<span class="cm">' + echapper(l.slice(i)) + '</span>'; break; }
      if (c === '"' || c === "'") {
        var j = i + 1;
        while (j < n && l[j] !== c) j++;
        out += '<span class="ch">' + echapper(l.slice(i, j + 1)) + '</span>';
        i = j + 1; continue;
      }
      if (c === '.' && l.slice(i, i + 3) === '...') {
        var k = i; while (k < n && l[k] === '.') k++;
        out += '<span class="trou" aria-label="à compléter">' + l.slice(i, k) + '</span>';
        i = k; continue;
      }
      if (/[A-Za-z_]/.test(c)) {
        var m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(l.slice(i))[0];
        var suite = l.slice(i + m.length);
        if (MOTS.indexOf(m) >= 0) out += '<span class="kw">' + m + '</span>';
        else if (/^\(/.test(suite)) out += '<span class="fn">' + m + '</span>';
        else out += m;
        i += m.length; continue;
      }
      out += echapper(c); i++;
    }
    return out;
  }

  /* Un programme : une ligne par <span class="l">, numéro à part (non copié),
     un filet et une bande grise par niveau d'indentation (4 espaces). */
  function codeHTML(code, options) {
    options = options || {};
    var debut = options.debut || 1;
    var lignes = String(code).split('\n');
    var h = lignes.map(function (l, k) {
      var m = /^( {4})*/.exec(l)[0], niv = m.length / 4, ind = '';
      for (var x = 0; x < niv; x++) ind += '<span class="ind">    </span>';
      return '<span class="l"><span class="no" aria-hidden="true">' + (debut + k) + '</span>' + ind + colorerLigne(l.slice(m.length)) + '</span>';
    }).join('\n');
    return '<pre class="code"' + (options.titre ? ' aria-label="' + echapper(options.titre) + '"' : '') + '><code>' + h + '</code></pre>';
  }

  /* Une console : texte brut, une ligne de console par ligne. La dernière
     ligne d'un message d'erreur (Exception: …) est en gras. */
  function consoleHTML(texteConsole, titre) {
    var lignes = String(texteConsole).replace(/\n$/, '').split('\n');
    return '<div class="console" role="group" aria-label="' + echapper(titre || 'Console') + '">' +
      '<div class="console-titre">' + echapper(titre || 'Console') + '</div><pre>' + lignes.map(function (l) {
        var erreur = /^[A-Z][A-Za-z]*(Error|Exception)\b/.test(l);
        return erreur ? '<b>' + echapper(l) + '</b>' : echapper(l);
      }).join('\n') + '</pre></div>';
  }

  function programmeHTML(sujet, nom) {
    var p = D.sujets[sujet].programmes[nom];
    if (!p) return '';
    var h = '';
    if (p.titre) h += '<p class="prog-titre"><strong>' + texte(p.titre) + '</strong></p>';
    var c = codeHTML(p.code, { debut: p.debut, titre: p.titre ? p.titre.replace(/`/g, '') : 'Programme' });
    /* Programme et console côte à côte sur papier, l'un sous l'autre à l'écran */
    if (p.console) c = '<div class="prog-console">' + c + consoleHTML(p.console, p.titre_console || 'Console (Python 3.13)') + '</div>';
    return h + c;
  }

  /* ── Questions ─────────────────────────────────────────── */

  function qs(sujet, q) { return D.sujets[sujet].q[q.id]; }

  /* Unités de mélange : une question seule, ou un groupe gardé dans l'ordre. */
  function unites() {
    var u = [], vu = {};
    D.questions.forEach(function (q, i) {
      if (q.groupe) {
        if (vu[q.groupe] === undefined) { vu[q.groupe] = u.length; u.push([]); }
        u[vu[q.groupe]].push(i);
      } else u.push([i]);
    });
    return u;
  }

  /* ── Normalisation des réponses (pour la correction) ────── */

  /* Signes diacritiques combinants (U+0300 à U+036F), écrits par leur code. */
  var DIACRITIQUES = new RegExp('[' + String.fromCharCode(0x300) + '-' + String.fromCharCode(0x36F) + ']', 'g');
  function sansAccents(s) {
    return String(s).normalize('NFD').replace(DIACRITIQUES, '');
  }
  /* Une suite de valeurs : séparées par des espaces, virgules ou points-virgules ;
     guillemets retirés ; casse et accents ignorés ; « self. » retiré. */
  function jetons(t) {
    return sansAccents(String(t || '')).toLowerCase()
      .replace(/self\./g, '').replace(/\(\)/g, '')
      .split(/[\s,;|]+/).map(function (x) { return x.replace(/^["'«»]+|["'«»]+$/g, ''); })
      .filter(function (x) { return x !== ''; });
  }
  /* Une ligne de code : espaces retirés, guillemets simples → doubles ;
     le début et la fin déjà imprimés (« while », « : ») retirés s'ils sont recopiés. */
  function ligneCode(t, avant, apres) {
    var s = String(t || '').replace(/\s+/g, '').replace(/'/g, '"');
    var a = (avant || '').replace(/\s+/g, ''), b = (apres || '').replace(/\s+/g, '');
    if (a && s.indexOf(a) === 0 && s.length > a.length) {
      s = s.slice(a.length);
      if (b && s.slice(-b.length) === b && s.length > b.length) s = s.slice(0, -b.length);
    } else if (b === ':' && s.slice(-1) === ':' && s.length > 1) s = s.slice(0, -1);
    return s;
  }

  function formeNormale(q, sujet, r) {
    var t = q.type;
    if (t === 'qcu') return r ? String(r) : null;
    if (t === 'ligne') { var x = qs(sujet, q); return ligneCode(r, x.avant, x.apres); }
    var j = jetons(r);
    if (t === 'valeur') return j.length === 1 ? j[0] : (j.length ? j : null);
    if (t === 'ensemble') return j.filter(function (v, i, a) { return a.indexOf(v) === i; }).sort();
    return j; /* liste, sortie */
  }
  function vide(r) { return r === null || r === undefined || String(r).trim() === ''; }

  /* ── Code de la copie (identique au contrôle sur les arbres) ─────
     Copie = [version, pseudo, classe, sujet, début (minutes depuis 1970),
              durée (secondes), graine du mélange, [réponses]]
     JSON → UTF-8 → base 32 de Crockford (QR en mode alphanumérique),
     puis une somme de contrôle de 4 caractères. Ce n'est PAS une protection. */

  var B32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

  function versBase32(octets) {
    var bits = 0, val = 0, out = '';
    for (var i = 0; i < octets.length; i++) {
      val = (val << 8) | octets[i]; bits += 8;
      while (bits >= 5) { out += B32[(val >>> (bits - 5)) & 31]; bits -= 5; }
      val &= (1 << bits) - 1;
    }
    if (bits > 0) out += B32[(val << (5 - bits)) & 31];
    return out;
  }
  function depuisBase32(t) {
    var bits = 0, val = 0, out = [];
    for (var i = 0; i < t.length; i++) {
      var c = t[i];
      if (c === 'O') c = '0';
      if (c === 'I' || c === 'L') c = '1';
      var k = B32.indexOf(c);
      if (k < 0) throw new Error('caractère inattendu');
      val = (val << 5) | k; bits += 5;
      if (bits >= 8) { out.push((val >>> (bits - 8)) & 255); bits -= 8; val &= (1 << bits) - 1; }
    }
    return new Uint8Array(out);
  }
  function crc32(octets) {
    var c, crc = 0xFFFFFFFF;
    for (var i = 0; i < octets.length; i++) {
      c = (crc ^ octets[i]) & 0xFF;
      for (var k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      crc = (crc >>> 8) ^ c;
    }
    return (crc ^ 0xFFFFFFFF) >>> 0;
  }
  function controle4(octets) {
    var n = crc32(octets) >>> 12, s = '';
    for (var i = 0; i < 4; i++) { s = B32[n & 31] + s; n >>>= 5; }
    return s;
  }
  function encoder(copie) {
    var octets = new TextEncoder().encode(JSON.stringify(copie));
    return D.prefixe + D.version + '-' + versBase32(octets) + '-' + controle4(octets);
  }
  function extraireCodes(t) {
    var propre = String(t || '').toUpperCase().replace(/\s+/g, '');
    var re = new RegExp(D.prefixe + '(\\d+)-([0-9A-Z]+)-([0-9A-Z]{4})', 'g');
    var m, trouves = [];
    while ((m = re.exec(propre))) trouves.push(m[0]);
    return trouves;
  }
  function decoder(code) {
    var propre = String(code || '').toUpperCase().replace(/\s+/g, '');
    var m = new RegExp('^' + D.prefixe + '(\\d+)-([0-9A-Z]+)-([0-9A-Z]{4})$').exec(propre);
    if (!m) throw new Error("Ce n'est pas un code de ce contrôle.");
    if (Number(m[1]) !== D.version) throw new Error('Code d\'une autre version du contrôle (' + m[1] + ').');
    var octets = depuisBase32(m[2]);
    if (controle4(octets) !== m[3]) throw new Error('Code incomplet ou mal recopié (somme de contrôle fausse).');
    var c = JSON.parse(new TextDecoder().decode(octets));
    if (!Array.isArray(c) || c.length < 8 || !Array.isArray(c[7]) || !D.sujets[String(c[3])]) throw new Error('Code illisible.');
    return {
      code: propre, version: c[0], pseudo: String(c[1] || ''), classe: String(c[2] || ''),
      sujet: String(c[3]), debut: c[4], duree: c[5], graine: c[6], reponses: c[7]
    };
  }

  /* ── Mélange reproductible (graine) ─────────────────────── */

  function aleatoire(graine) {
    var a = graine >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function melanger(liste, hasard) {
    var t = liste.slice();
    for (var i = t.length - 1; i > 0; i--) {
      var j = Math.floor(hasard() * (i + 1)), x = t[i]; t[i] = t[j]; t[j] = x;
    }
    return t;
  }

  /* Thème clair ou obscur : même réglage que le site (barre du haut). */
  function appliquerTheme() {
    try {
      var m = localStorage.getItem('theme');
      if (m === 'light' || m === 'dark') document.documentElement.setAttribute('data-theme', m);
    } catch (e) { /* stockage indisponible : réglage de l'appareil */ }
  }

  window.CN = {
    DONNEES: D, echapper: echapper, texte: texte,
    codeHTML: codeHTML, consoleHTML: consoleHTML, programmeHTML: programmeHTML,
    qs: qs, unites: unites, jetons: jetons, ligneCode: ligneCode, formeNormale: formeNormale, vide: vide,
    encoder: encoder, decoder: decoder, extraireCodes: extraireCodes,
    aleatoire: aleatoire, melanger: melanger, appliquerTheme: appliquerTheme
  };
})();
