/* ─────────────────────────────────────────────
   Ressources NSI et SNT : moteur des TD en ligne (T115)

   Transforme une page de TD écrite simplement (des attributs data-…)
   en feuille auto-corrective. Mode d'emploi : design/td-en-ligne.md.

   - Tout se corrige dans le navigateur : rien n'est envoyé.
   - L'avancement sert 24 heures, sur l'appareil seulement. Ensuite il est
     effacé : à l'échéance si la page est ouverte, sinon à la prochaine
     ouverture d'un TD en ligne sur cet appareil.
   - Pas de note, pas de score : une jauge d'avancement, puis
     « Feuille validée ». L'événement td:feuille-validee (identifiant
     de la feuille seulement) est prévu pour le compte commun.
   - Aucune dépendance obligatoire. Python (Pyodide) ne se charge
     qu'à la demande, pour les questions « code ».

   Babash - NSI Tani Malandi · code sous licence MIT
   ───────────────────────────────────────────── */
(function () {
  'use strict';

  var VERSION = '1.1.0';
  var DUREE = 24 * 3600 * 1000;           // un jour au plus (ordinateurs partagés)
  var PREFIXE = 'td:';
  var PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js';   // Python 3.13
  var DELAI_PYTHON = 6000;                // au-delà : boucle infinie probable
  var ESSAIS_AVANT_CORRECTION = 2;

  /* ── Petits outils ─────────────────────────── */

  function el(tag, attrs, enfants) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') e.className = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k === 'text') e.textContent = v;
      else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? '' : v);
    });
    (enfants || []).forEach(function (c) { if (c) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return e;
  }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function sansAccents(s) { return s.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function hasard(graine) {                // tirage reproductible (même mélange à chaque visite)
    var h = 2166136261;
    for (var i = 0; i < graine.length; i++) { h ^= graine.charCodeAt(i); h = Math.imul(h, 16777619); }
    return function () { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 100000) / 100000; };
  }
  function choisir(liste, n) { return liste[n % liste.length]; }
  var compteur = 0;
  function nouvelId(p) { return (p || 'td') + '-' + (++compteur); }

  /* ── Stockage sur l'appareil (24 h au plus) ── */

  var stock = {
    lire: function (cle) {
      try {
        var v = JSON.parse(localStorage.getItem(cle) || 'null');
        if (v && v.cree && Date.now() - v.cree > DUREE) { localStorage.removeItem(cle); return null; }
        return v;
      } catch (e) { return null; }
    },
    ecrire: function (cle, v) { try { localStorage.setItem(cle, JSON.stringify(v)); } catch (e) { /* stockage bloqué : la feuille marche quand même */ } },
    effacer: function (cle) { try { localStorage.removeItem(cle); } catch (e) { } },
    purger: function () {           // efface les feuilles de plus d'un jour, sur tout le site
      try {
        for (var i = localStorage.length - 1; i >= 0; i--) {
          var k = localStorage.key(i);
          if (k && k.indexOf(PREFIXE) === 0) stock.lire(k);
        }
      } catch (e) { }
    }
  };

  /* ── Comparer des réponses avec tolérance ──── */

  function normTexte(s) {
    return sansAccents(String(s)).toLowerCase()
      .replace(/[\u2018\u2019\u201c\u201d\u00ab\u00bb"]/g, "'")
      .replace(/[\u00a0\u202f\t]/g, ' ')
      .replace(/\s+/g, ' ').trim()
      .replace(/[.!]$/, '').trim();
  }
  function normCode(s) {             // espaces ignorés hors des chaînes, guillemets équivalents
    s = String(s).replace(/[\u2018\u2019\u201c\u201d]/g, "'").replace(/"/g, "'").trim();
    var out = '', dans = false;
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (c === "'") dans = !dans;
      if (!dans && /\s/.test(c)) continue;
      out += c;
    }
    return out;
  }
  function nombre(s) {
    var t = String(s).trim().replace(/\s/g, '').replace(',', '.');
    return /^[-+]?(\d+\.?\d*|\.\d+)$/.test(t) ? parseFloat(t) : null;
  }
  function egal(reponse, attendu, mode) {
    if (mode === 'code') return normCode(reponse) === normCode(attendu);
    var a = nombre(reponse), b = nombre(attendu);
    if (a !== null && b !== null) return Math.abs(a - b) < 1e-9;
    if (mode === 'exact') return String(reponse).trim() === String(attendu).trim();
    return normTexte(reponse) === normTexte(attendu);
  }
  function unParmi(reponse, liste, mode) { return liste.some(function (x) { return egal(reponse, x, mode); }); }
  function alternatives(s) { return String(s || '').split('|'); }
  // garderDebut (data-espaces="exact") : les espaces de début de ligne comptent (motifs centrés, pyramides)
  function normSortie(s, garderDebut) {
    return String(s).replace(/\r/g, '').split('\n').map(function (l) {
      if (!garderDebut || !l.trim()) return normTexte(l);
      return l.replace(/\t/g, '    ').match(/^ */)[0] + normTexte(l);
    }).filter(function (l) { return l !== ''; }).join('\n');
  }
  // [[réponse]] dans une ligne : la case se ferme au premier « ]] » où les crochets de la réponse sont équilibrés
  // (t[0] dans [[t[0]]] reste entier). Renvoie [texte, réponse, texte, réponse, …, texte].
  function decouperTrous(l) {
    var out = [], debut = 0, k;
    while ((k = l.indexOf('[[', debut)) >= 0) {
      // « t[[[i]]] » : après un nom, une parenthèse ou un crochet, le premier « [ » est celui du code (t[ + case + ]) ;
      // ailleurs (« = [[[1, 2]]] »), la case contient une liste (T123c)
      if (l[k + 2] === '[' && k > 0 && /[\w)\]]/.test(l[k - 1])) k++;
      var p = 0, fin = -1;
      for (var j = k + 2; j < l.length; j++) {
        var c = l[j];
        if (c === ']' && p === 0 && l[j + 1] === ']') { fin = j; break; }
        if (c === '[') p++; else if (c === ']' && p > 0) p--;
      }
      if (fin < 0) break;
      out.push(l.slice(debut, k), l.slice(k + 2, fin)); debut = fin + 2;
    }
    out.push(l.slice(debut));
    return out;
  }
  // code à trous (T123c) : des commentaires alignés en fin de ligne restent alignés malgré les cases.
  // Un groupe = des lignes avec un commentaire précédé de 2 espaces au moins, qui se suivent ou dont le commentaire
  // commence à la même colonne dans la source ; l'une au moins a une case avant son commentaire, une au moins
  // 3 espaces devant le sien (alignement voulu) ; pas déjà alignées. Chaque ligne garde au moins ses
  // espaces ; le commentaire commence à la même colonne sur tout le groupe (calcul en CSS : les cases n'ont pas la
  // même largeur à l'écran et sur papier). Renvoie { ligne: { coupe, largeur } }.
  var BORDS_IND = [1.6, 1.6, 2.6, 1];
  function commentairesAlignes(lignes, largeurDe) {
    var infos = lignes.map(function (l) {
      var morceaux = decouperTrous(l), brut = 0, dans = null, cases = [], texte = 0;
      for (var k = 0; k < morceaux.length; k++) {
        var m = morceaux[k];
        if (k % 2) { cases.push(largeurDe(m)); brut += m.length + 4; continue; }
        for (var i = 0; i < m.length; i++) {
          var c = m[i];
          if (dans) { if (c === dans) dans = null; }
          else if (c === '"' || c === "'") dans = c;
          else if (c === '#') {
            var av = m.slice(0, i), esp = av.match(/ *$/)[0].length;
            var code = morceaux.slice(0, k).join('') + av;
            if (esp < 2 || !code.trim()) return null;
            var niv = Math.floor(decalage(l) / 4), bords = 0;
            for (var j = 0; j < niv; j++) bords += BORDS_IND[j % 4];
            return { coupe: brut + i - esp, esp: esp, cases: cases.slice(), texte: texte + i - esp, bords: bords };
          }
        }
        brut += m.length; texte += m.length;
      }
      return null;
    });
    // groupes : des lignes qui se suivent, ou dont le commentaire commence à la même colonne dans la source
    var chef = infos.map(function (_, i) { return i; });
    function racine(i) { while (chef[i] !== i) i = chef[i] = chef[chef[i]]; return i; }
    var parCol = {};
    infos.forEach(function (x, i) {
      if (!x) return;
      if (i > 0 && infos[i - 1]) chef[racine(i)] = racine(i - 1);
      var c = x.coupe + x.esp;
      if (parCol[c] !== undefined) chef[racine(i)] = racine(parCol[c]); else parCol[c] = i;
    });
    var groupes = {};
    infos.forEach(function (x, i) { if (x) { x.n = i; (groupes[racine(i)] = groupes[racine(i)] || []).push(x); } });
    var out = {};
    Object.keys(groupes).forEach(function (cle) {
      var groupe = groupes[cle];
      // un alignement voulu : 3 espaces au moins devant un des commentaires (2 espaces seuls : un commentaire ordinaire)
      if (groupe.length < 2 || !groupe.some(function (x) { return x.cases.length; }) || !groupe.some(function (x) { return x.esp >= 3; })) return;
      var sig = function (x) { return [x.texte, x.cases.reduce(function (a, b) { return a + b; }, 0), x.cases.length, x.esp, x.bords].join('|'); };
      if (groupe.every(function (x) { return sig(x) === sig(groupe[0]); })) return;
      var exprs = groupe.map(function (x) {
        return 'calc(' + (x.texte + x.esp) + 'ch' + x.cases.map(function (w) { return ' + max(' + (w + 1) + 'ch, var(--td-trou-min, 0px))'; }).join('') +
          (x.cases.length ? ' + ' + x.cases.length + ' * var(--td-trou-marge, .2em)' : '') + ' + ' + x.bords + 'px)';
      });
      var largeur = 'max(' + exprs.join(', ') + ')';
      groupe.forEach(function (x) { out[x.n] = { coupe: x.coupe, largeur: largeur }; });
    });
    return out;
  }

  /* ── Coloration de Python ──────────────────── */

  var MOTS = ('False None True and as assert async await break class continue def del elif else except finally for from ' +
    'global if import in is lambda nonlocal not or pass raise return try while with yield').split(' ');
  var FONCTIONS = ('print input range len int float str list dict set tuple abs min max sum round sorted reversed ' +
    'enumerate zip type bool isinstance chr ord map filter open help').split(' ');
  // chaînes : triples (docstrings, ouvertes jusqu'en fin de ligne), puis simples ; un « ' » dans "…" reste dans la chaîne
  var RE_TOKEN = /([rRbBfFuU]{0,2}(?:"""(?:[^"\\]|\\.|"(?!""))*(?:"""|$)|'''(?:[^'\\]|\\.|'(?!''))*(?:'''|$))|[rRbBfFuU]{0,2}"(?:[^"\\]|\\.)*"?|[rRbBfFuU]{0,2}'(?:[^'\\]|\\.)*'?)|(#.*$)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_\u00c0-\u024f][\w\u00c0-\u024f]*)|(==|!=|<=|>=|\/\/|\*\*|[-+*\/%<>=])/g;

  var MOTS_SQL = ('SELECT FROM WHERE AND OR NOT INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE PRIMARY KEY FOREIGN REFERENCES ' +
    'JOIN INNER LEFT RIGHT OUTER ON AS ORDER BY GROUP HAVING ASC DESC DISTINCT LIMIT OFFSET NULL IS IN LIKE BETWEEN ' +
    'INTEGER INT TEXT REAL FLOAT DATE BOOLEAN VARCHAR CHAR DROP ALTER ADD UNIQUE CHECK DEFAULT CASCADE UNION EXISTS').split(' ');
  var FONCTIONS_SQL = 'COUNT SUM AVG MIN MAX UPPER LOWER LENGTH ROUND ABS'.split(' ');
  var RE_SQL = /('(?:[^']|'')*'?)|(--.*$)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_\u00c0-\u024f][\w\u00c0-\u024f]*)|(<>|!=|<=|>=|[-+*\/%<>=])/g;
  // le langage d'un code : data-langage sur le pre, la question ou la page (python par défaut ; sql ; texte = sans coloration)
  function langue(e) { var x = e && e.closest ? e.closest('[data-langage]') : null; return x ? x.getAttribute('data-langage') : 'python'; }
  function colorerSql(code) {
    var out = '', i = 0, m;
    RE_SQL.lastIndex = 0;
    while ((m = RE_SQL.exec(code))) {
      out += esc(code.slice(i, m.index)); i = RE_SQL.lastIndex;
      if (m[1]) out += '<span class="tk-ch">' + esc(m[1]) + '</span>';
      else if (m[2]) out += '<span class="tk-com">' + esc(m[2]) + '</span>';
      else if (m[3]) out += '<span class="tk-nb">' + m[3] + '</span>';
      else if (m[4]) {
        var u = m[4].toUpperCase();
        if (MOTS_SQL.indexOf(u) >= 0) out += '<span class="tk-mot">' + esc(m[4]) + '</span>';
        else if (FONCTIONS_SQL.indexOf(u) >= 0 && /^\s*\(/.test(code.slice(i))) out += '<span class="tk-fn">' + esc(m[4]) + '</span>';
        else out += esc(m[4]);
      } else out += '<span class="tk-op">' + esc(m[5]) + '</span>';
      if (m[0] === '') RE_SQL.lastIndex++;
    }
    return out + esc(code.slice(i));
  }
  // etat (facultatif) : { dans: '"""' ou "'''" } quand la ligne commence dans une chaîne triple ; mis à jour pour la ligne suivante
  function colorerMots(code, lang, etat) {        // un morceau de ligne, sans l'indentation
    if (lang === 'texte') return esc(code);
    if (lang === 'sql') return colorerSql(code);
    var out = '', i = 0, m;
    if (etat && etat.dans) {
      var f = code.indexOf(etat.dans);
      if (f < 0) return '<span class="tk-ch">' + esc(code) + '</span>';
      out = '<span class="tk-ch">' + esc(code.slice(0, f + 3)) + '</span>';
      code = code.slice(f + 3); etat.dans = null;
    }
    RE_TOKEN.lastIndex = 0;
    while ((m = RE_TOKEN.exec(code))) {
      out += esc(code.slice(i, m.index)); i = RE_TOKEN.lastIndex;
      if (m[1]) {
        out += '<span class="tk-ch">' + esc(m[1]) + '</span>';
        var tq = m[1].match(/^[rRbBfFuU]{0,2}("""|''')/);
        if (etat && tq && (m[1].length - tq[0].length < 3 || m[1].slice(-3) !== tq[1])) etat.dans = tq[1];
      }
      else if (m[2]) out += '<span class="tk-com">' + esc(m[2]) + '</span>';
      else if (m[3]) out += '<span class="tk-nb">' + m[3] + '</span>';
      else if (m[4]) {
        var w = m[4];
        if (MOTS.indexOf(w) >= 0) out += '<span class="tk-mot">' + w + '</span>';
        else if (FONCTIONS.indexOf(w) >= 0 && /^\s*\(/.test(code.slice(i))) out += '<span class="tk-fn">' + w + '</span>';
        else out += esc(w);
      } else out += '<span class="tk-op">' + esc(m[5]) + '</span>';
      if (m[0] === '') RE_TOKEN.lastIndex++;
    }
    return out + esc(code.slice(i));
  }
  function decalage(l) { return l.match(/^ */)[0].length; }
  // décalage « virtuel » des lignes vides : celui du bloc qui les entoure
  function decalages(lignes) {
    var d = lignes.map(function (l) { return l.trim() ? decalage(l) : -1; });
    for (var i = 0; i < d.length; i++) if (d[i] < 0) {
      var a = 0, b = 0, j;
      for (j = i - 1; j >= 0; j--) if (d[j] >= 0) { a = d[j]; break; }
      for (j = i + 1; j < d.length; j++) if (lignes[j].trim()) { b = decalage(lignes[j]); break; }
      d[i] = -Math.min(a, b) - 1;      // négatif : ligne vide (à dessiner sans texte)
    }
    return d;
  }
  // bloc qui contient la ligne c : sa ligne d'en-tête (… :) et sa fin
  function blocDe(lignes, c) {
    var d = decalages(lignes), dc = d[c] < 0 ? -d[c] - 1 : d[c];
    if (lignes[c] && /:\s*(#.*)?$/.test(lignes[c]) && c + 1 < lignes.length) {
      var dn = d[c + 1] < 0 ? -d[c + 1] - 1 : d[c + 1];
      if (dn > dc) return finBloc(lignes, d, c);              // le curseur est sur l'en-tête
    }
    for (var j = c - 1; j >= 0; j--) {
      if (d[j] >= 0 && d[j] < dc && /:\s*(#.*)?$/.test(lignes[j])) return finBloc(lignes, d, j);
    }
    return null;
  }
  function finBloc(lignes, d, h) {
    var fin = h;
    for (var k = h + 1; k < lignes.length; k++) {
      if (d[k] >= 0 && d[k] <= d[h]) break;
      if (d[k] >= 0) fin = k;
    }
    return { entete: h, fin: fin, niveau: Math.floor(d[h] / 4), mot: (lignes[h].match(/^\s*(\w+)/) || [])[1] || '' };
  }
  // une ligne colorée, avec un filet et une bande grise par niveau d'indentation
  function colorerLigne(ligne, dVirtuel, actif, num, lang, etat) {
    var vide = dVirtuel < 0, lead = vide ? -dVirtuel - 1 : decalage(ligne);
    var niv = Math.floor(lead / 4), out = '';
    for (var k = 0; k < niv; k++) {
      var on = actif && num > actif.entete && num <= actif.fin && k === actif.niveau;
      out += '<span class="td-ind n' + (k % 4) + (on ? ' actif' : '') + '">    </span>';
    }
    if (vide) return out;
    out += esc(ligne.slice(niv * 4, lead));
    return out + colorerMots(ligne.slice(lead), lang, etat);
  }
  function colorer(code, actif, lang) {
    var lignes = code.split('\n'), d = decalages(lignes), etat = { dans: null };
    return lignes.map(function (l, i) {
      if (etat.dans && lang !== 'sql' && lang !== 'texte') {         // ligne dans une chaîne triple : les bandes d'indentation, puis la chaîne
        var lead = Math.min(decalage(l), Math.max(0, d[i] < 0 ? -d[i] - 1 : d[i])), bandes = colorerLigne(l.slice(0, Math.floor(lead / 4) * 4), -Math.floor(lead / 4) * 4 - 1, actif, i);
        return bandes + colorerMots(l.slice(Math.floor(lead / 4) * 4), lang, etat);
      }
      return colorerLigne(l, d[i], actif, i, lang, etat);
    });
  }

  // une ligne de code plus large que la page (80 caractères) passe à la ligne : coupée après « , » ou à une espace,
  // hors d'une chaîne ; la suite est décalée de 4 espaces de plus (T123c). Renvoie { texte, suites: {indice: true} }
  var LARGEUR_PAPIER = 80;
  function couperLongues(code, max) {
    var out = [], suites = {};
    code.split('\n').forEach(function (l) {
      var reste = l, premiere = true, dec = l.match(/^ */)[0] + '    ';
      while (reste.length > max) {
        var dans = null, coupe = -1;
        for (var i = 0; i < reste.length && i < max; i++) {
          var c = reste[i];
          if (dans) { if (c === dans && reste[i - 1] !== '\\') dans = null; continue; }
          if (c === '"' || c === "'") dans = c;
          else if (c === '#') break;
          else if (c === ' ' && i > 20) coupe = reste[i - 1] === ',' ? i : (coupe >= 0 && reste[coupe - 1] === ',' ? coupe : i);
        }
        if (coupe < 0) break;
        if (!premiere) suites[out.length] = true;
        out.push(reste.slice(0, coupe).replace(/ +$/, ''));
        reste = dec + reste.slice(coupe).replace(/^ +/, '');
        premiere = false;
      }
      if (!premiere) suites[out.length] = true;
      out.push(reste);
    });
    return { texte: out.join('\n'), suites: suites };
  }
  var CODE_LONG = 40;       // au-delà (en lignes), un code peut être coupé entre deux lignes sur papier (T123c)
  // code affiché (non modifiable), avec numéros de ligne
  function afficherCode(pre, opts) {
    opts = opts || {};
    if (pre.classList.contains('td-code-pret')) return pre.getAttribute('data-source');
    var code = (pre.textContent || '').replace(/^\n/, '').replace(/\s+$/, '');
    pre.setAttribute('data-source', code);
    var lignes = colorer(code, null, langue(pre)), suites = opts.suites || {}, num = 0;
    pre.innerHTML = lignes.map(function (l, i) {
      // une ligne trop large coupée (squelette imprimé) : sa suite porte « → » au lieu d'un numéro
      if (suites[i]) return '<span class="td-l td-l-suite"><span class="td-num" aria-hidden="true">→</span>' + (l || ' ') + '</span>';
      return '<span class="td-l"><span class="td-num" aria-hidden="true">' + (++num) + '</span>' + (l || ' ') + '</span>';
    }).join('');
    pre.classList.add('td-code-pret');
    if (lignes.length < 2 || opts.sansNumeros) pre.classList.add('td-sans-num');
    if (lignes.length > CODE_LONG) pre.classList.add('td-code-long');     // sur papier : peut passer à la page suivante
    return code;
  }

  // message d'erreur de Python, coloré (gras, souligné : lisible en noir et blanc)
  function colorerErreur(texte) {
    return texte.replace(/\s+$/, '').split('\n').map(function (l) {
      var m;
      if (/^Traceback/.test(l)) return '<span class="er-entete">' + esc(l) + '</span>';
      if ((m = l.match(/^(\s*File )(".*?")(, line )(\d+)(.*)$/))) return esc(m[1]) + '<span class="er-fichier">' + esc(m[2]) + '</span>' + esc(m[3]) + '<b class="er-ligne">' + m[4] + '</b>' + esc(m[5]);
      if (/^\s*[\^~]+\s*$/.test(l)) return '<b class="er-fleche">' + esc(l) + '</b>';
      if ((m = l.match(/^(\w*(?:Error|Exception|Warning|Interrupt|Exit))(:?)(.*)$/))) return '<b class="er-type">' + esc(m[1]) + '</b>' + esc(m[2]) + '<span class="er-msg">' + esc(m[3]) + '</span>';
      if (/^\s{4}\S/.test(l)) return '<span class="er-code">' + colorerMots(l) + '</span>';
      return esc(l);
    }).map(function (l) { return '<span class="td-l">' + (l || ' ') + '</span>'; }).join('');
  }

  /* ── Les erreurs de Python, expliquées en français ── */

  var ERREURS = [
    [/SyntaxError: expected ':'/, 'Il manque les <b>deux-points</b> <code>:</code> à la fin de la ligne. Ils sont obligatoires après <code>for</code>, <code>while</code>, <code>if</code>, <code>elif</code>, <code>else</code> et <code>def</code>.'],
    [/SyntaxError: unterminated string literal/, 'Une <b>chaîne de caractères</b> n\'est pas fermée : il manque un guillemet à la fin du texte.'],
    [/SyntaxError: '(\(|\[|\{)' was never closed/, 'Une <b>parenthèse</b> (ou un crochet) est ouverte mais jamais fermée.'],
    [/SyntaxError: unmatched '(.)'/, 'Il y a une parenthèse (ou un crochet) <b>fermante en trop</b>.'],
    [/SyntaxError: invalid syntax\. Maybe you meant '==' or ':=' instead of '='/, 'Pour <b>comparer</b>, on écrit <code>==</code>. Un seul <code>=</code> sert à donner une valeur à une variable.'],
    [/SyntaxError: cannot assign to/, 'À gauche du signe <code>=</code>, il faut un <b>nom de variable</b>. Pour comparer, on écrit <code>==</code>.'],
    [/SyntaxError: invalid syntax/, 'Python ne comprend pas cette ligne : un mot, un signe ou une parenthèse est mal placé. Regarde l\'endroit montré par les <code>^</code>.'],
    [/IndentationError: expected an indented block/, 'Après une ligne qui finit par <code>:</code>, la ligne suivante doit être <b>décalée</b> (4 espaces) : c\'est le bloc qui est répété ou exécuté.'],
    [/IndentationError: unexpected indent/, 'Cette ligne est <b>décalée sans raison</b> : elle ne suit pas une ligne qui finit par <code>:</code>.'],
    [/IndentationError: unindent does not match/, 'Ce décalage ne correspond à <b>aucun bloc</b> au-dessus : aligne la ligne avec le bloc auquel elle appartient.'],
    [/NameError: name '(\w+)' is not defined\. Did you mean: '(\w+)'/, 'Python ne connaît pas le nom <code>$1</code>. Il te propose <code>$2</code> : sans doute une <b>faute de frappe</b>.'],
    [/NameError: name '(\w+)' is not defined/, 'Python ne connaît pas le nom <code>$1</code> : la variable n\'a pas encore reçu de valeur à ce moment-là, ou son nom est mal écrit. S\'il s\'agit d\'un texte, il faut des guillemets.'],
    [/TypeError: can only concatenate str \(not "(\w+)"\) to str/, 'On ne peut pas coller (<code>+</code>) un texte et un nombre. Transforme le nombre en texte avec <code>str()</code>, ou utilise une virgule dans <code>print</code>.'],
    [/TypeError: unsupported operand type\(s\) for (\S+): '(\w+)' and '(\w+)'/, 'L\'opération <code>$1</code> n\'est pas possible entre un <code>$2</code> et un <code>$3</code>. Vérifie le type de chaque valeur (un nombre lu avec <code>input</code> est un texte : <code>int()</code> le transforme en nombre).'],
    [/TypeError: '(\w+)' object cannot be interpreted as an integer/, '<code>range</code> attend des <b>nombres entiers</b>, pas un <code>$1</code>.'],
    [/TypeError: '(\w+)' object is not iterable/, 'On ne peut pas parcourir un <code>$1</code> avec <code>for</code>. Pour répéter n fois, écris <code>for i in range(n):</code>.'],
    [/TypeError: '(\w+)' object is not callable/, 'Des parenthèses suivent un <code>$1</code>, comme si c\'était une fonction. Une variable porte peut-être le nom d\'une fonction.'],
    [/TypeError: (\w+)\(\) takes (\d+) positional arguments? but (\d+) (were|was) given/, 'La fonction <code>$1</code> attend $2 valeur(s) entre parenthèses, mais elle en a reçu $3.'],
    [/TypeError: (\w+)\(\) missing/, 'Il manque une valeur entre les parenthèses de <code>$1</code>.'],
    [/ValueError: invalid literal for int\(\) with base 10: '(.*)'/, '<code>int()</code> ne peut pas transformer <code>\'$1\'</code> en nombre entier.'],
    [/ZeroDivisionError/, 'Une <b>division par zéro</b> : c\'est impossible, en Python comme en maths.'],
    [/IndexError: (\w+) index out of range/, 'L\'indice demandé est <b>trop grand</b> : il n\'y a pas d\'élément à cette place. Le premier indice est 0, le dernier est <code>len(…) - 1</code>.'],
    [/KeyError: (.*)/, 'La clé <code>$1</code> n\'existe pas dans le dictionnaire.'],
    [/AttributeError: '(\w+)' object has no attribute '(\w+)'/, 'Un <code>$1</code> n\'a pas de méthode ou d\'attribut <code>$2</code>.'],
    [/RecursionError/, 'La fonction s\'appelle elle-même <b>sans jamais s\'arrêter</b> : il manque un cas de base.'],
    [/EOFError/, 'Le programme demande une saisie (<code>input</code>) de plus que ce que la page fournit : chaque <code>input()</code> lit une ligne, et il n\'y en a plus.'],
    [/ModuleNotFoundError: No module named '(\w+)'/, 'Le module <code>$1</code> n\'existe pas ici (ou son nom est mal écrit).']
  ];
  var VOCABULAIRE = [
    ['Traceback (most recent call last)', 'trace des appels (le plus récent en dernier)'],
    ['File "…", line N', 'fichier « … », ligne N : là où Python s\'est arrêté'],
    ['^^^^', 'l\'endroit précis de l\'erreur'],
    ['Did you mean', 'voulais-tu dire'],
    ['is not defined', 'n\'est pas défini']
  ];
  function expliquerErreur(texte) {
    var derniere = texte.replace(/\s+$/, '').split('\n').pop();
    for (var i = 0; i < ERREURS.length; i++) {
      var m = derniere.match(ERREURS[i][0]);
      if (m) return ERREURS[i][1].replace(/\$(\d)/g, function (_, n) { return esc(m[+n] || ''); });
    }
    return 'Lis la dernière ligne : elle donne le <b>type</b> de l\'erreur. La ligne <code>File …, line N</code> dit où Python s\'est arrêté.';
  }
  function ligneErreur(texte) {
    var m = texte.match(/line (\d+)(?![\s\S]*line \d+)/);
    return m ? +m[1] : null;
  }
  // bloc « message d'erreur » + bouton « Expliquer en français »
  function blocErreur(texte, parent) {
    var box = el('div', { class: 'td-erreur-bloc' });
    var pre = el('pre', { class: 'td-erreur td-code-pret', html: colorerErreur(texte) });
    var idExp = nouvelId('exp');
    var exp = el('div', { class: 'td-explication', id: idExp, hidden: true });
    exp.innerHTML = '<p><b>En français :</b> ' + expliquerErreur(texte) + '</p>' +
      '<p class="td-vocab">' + VOCABULAIRE.map(function (v) { return '<span><code>' + esc(v[0]) + '</code> : ' + esc(v[1]) + '</span>'; }).join(' · ') + '</p>';
    var bouton = el('button', { type: 'button', class: 'td-bouton td-petit', 'aria-expanded': 'false', 'aria-controls': idExp, text: 'Expliquer en français' });
    bouton.addEventListener('click', function () {
      var ouvert = exp.hidden;
      exp.hidden = !ouvert; bouton.setAttribute('aria-expanded', String(ouvert));
      bouton.textContent = ouvert ? 'Masquer l\'explication' : 'Expliquer en français';
    });
    box.appendChild(el('p', { class: 'td-etiquette-console', text: 'erreur' }));
    box.appendChild(pre); box.appendChild(bouton); box.appendChild(exp);
    if (parent) parent.appendChild(box);
    return box;
  }
  // console compacte : une ligne de sortie par ligne de texte
  function console_(texte, classe) {
    var lignes = String(texte).replace(/\s+$/, '').split('\n');
    return el('pre', { class: 'td-console ' + (classe || ''), html: lignes.map(function (l) { return '<span class="td-l">' + (esc(l) || ' ') + '</span>'; }).join('') });
  }

  /* ── Python à la demande, dans un Worker (on peut l'arrêter) ── */

  var python = { worker: null, pret: null, attente: {}, n: 0 };
  // le lanceur Python du Worker (T123c) : la sortie comparée ne contient que ce qu'affiche le programme ;
  // l'invite d'input() et la saisie (écrites comme dans un terminal) et les print des tests cachés ne sont
  // qu'affichés. Les cadres de la fonction de saisie ne figurent pas dans le message d'erreur.
  var PY_LANCEUR = [
    'import sys, traceback, linecache, builtins',
    'class _TdFlux:',
    '    encoding = "utf-8"',
    '    def __init__(self, seg, genre):',
    '        self.seg, self.genre = seg, genre',
    '    def write(self, t):',
    '        self.seg.append((self.genre, str(t)))',
    '        return len(t)',
    '    def flush(self):',
    '        pass',
    '    def isatty(self):',
    '        return False',
    'def _td_lancer(src, tests, nom, pre="", graine="", saisies=False):',
    '    linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)',
    '    g = {"__name__": "__main__"}',
    '    seg = []',
    '    vrais = (sys.stdout, sys.stderr, builtins.input)',
    '    def saisir(invite=""):',
    '        seg.append(("invite", str(invite)))',
    '        l = sys.stdin.readline()',
    '        if not l:',
    '            raise EOFError("EOF when reading a line")',
    '        l = l[:-1] if l.endswith("\\n") else l',
    '        seg.append(("invite", l + "\\n"))',
    '        return l',
    '    def rapport(e):',
    '        tb = e.__traceback__.tb_next if e.__traceback__ else None',
    '        t = tb',
    '        while t is not None and t.tb_next is not None:',
    '            if t.tb_next.tb_frame.f_code is saisir.__code__:',
    '                t.tb_next = None',
    '                break',
    '            t = t.tb_next',
    '        return "".join(traceback.format_exception(type(e), e, tb))',
    '    def fin(etat, detail):',
    '        sys.stdout, sys.stderr, builtins.input = vrais',
    '        return [etat, detail, "".join(t for k, t in seg if k == "prog"), "".join(t for k, t in seg)]',
    '    sys.stdout = sys.stderr = _TdFlux(seg, "prog")',
    '    if saisies:',
    '        builtins.input = saisir',
    '    try:',
    '        if pre:',
    '            try:',
    '                exec(compile(pre, "preambule.py", "exec"), g)',
    '            except BaseException as e:',
    '                return fin("erreur", rapport(e))',
    '        if graine != "":',
    '            import random',
    '            random.seed(int(graine) if graine.lstrip("-").isdigit() else graine)',
    '        try:',
    '            exec(compile(src, nom, "exec"), g)',
    '        except SystemExit:',
    '            pass',
    '        except BaseException as e:',
    '            return fin("erreur", rapport(e))',
    '        if tests:',
    '            sys.stdout = sys.stderr = _TdFlux(seg, "test")',
    '            try:',
    '                exec(compile(tests, "tests.py", "exec"), g)',
    '            except AssertionError as e:',
    '                return fin("test", str(e))',
    '            except BaseException as e:',
    '                return fin("test", rapport(e))',
    '        return fin("ok", "")',
    '    finally:',
    '        sys.stdout, sys.stderr, builtins.input = vrais'
  ].join('\n');
  function sourceWorker(url) {
    return [
      'importScripts(' + JSON.stringify(url) + ');',
      'var py = loadPyodide({ indexURL: ' + JSON.stringify(url.replace(/[^/]*$/, '')) + ' }).then(function (p) {',
      '  p.runPython(' + JSON.stringify(PY_LANCEUR) + ');',
      '  p.setStdin({ error: true });',
      '  return p;',
      '});',
      'self.onmessage = function (e) {',
      '  var d = e.data, autre = [];',
      '  py.then(function (p) {',
      '    p.setStdout({ batched: function (s) { autre.push(s); } });',
      '    p.setStderr({ batched: function (s) { autre.push(s); } });',
      '    var saisies = typeof d.entrees === "string";',
      '    if (saisies) { var L = d.entrees.split("\\n"), k = 0; p.setStdin({ stdin: function () { return k < L.length ? L[k++] : undefined; } }); }',
      '    else p.setStdin({ error: true });',
      '    var r = p.globals.get("_td_lancer")(d.code, d.tests || "", d.fichier || "mon_code.py", d.pre || "", d.graine || "", saisies).toJs();',
      '    var plus = autre.length ? "\\n" + autre.join("\\n") : "";',
      '    self.postMessage({ id: d.id, etat: r[0], detail: r[1], sortie: r[2] + plus, vue: r[3] + plus });',
      '  }).catch(function (err) { self.postMessage({ id: d.id, etat: "indisponible", detail: String(err) }); });',
      '};'
    ].join('\n');
  }
  function demarrerPython(url) {
    var blob = new Blob([sourceWorker(url)], { type: 'text/javascript' });
    python.worker = new Worker(URL.createObjectURL(blob));
    python.worker.onmessage = function (e) {
      var f = python.attente[e.data.id]; delete python.attente[e.data.id];
      if (f) f(e.data);
    };
    python.worker.onerror = function (e) {
      if (e && e.preventDefault) e.preventDefault();      // erreur traitée : rien dans la console
      Object.keys(python.attente).forEach(function (k) { python.attente[k]({ etat: 'indisponible' }); });
      python.attente = {}; python.worker = null; python.charge = false;
    };
  }
  function lancerPython(url, code, tests, fichier, premier, extra) {
    return new Promise(function (resoudre) {
      try { if (!python.worker) demarrerPython(url); } catch (e) { resoudre({ etat: 'indisponible' }); return; }
      var id = ++python.n;
      // le premier lancement charge Python : on lui laisse plus de temps
      var limite = setTimeout(function () {
        if (!python.attente[id]) return;
        delete python.attente[id];
        python.worker.terminate(); python.worker = null; python.charge = false;   // il faudra recharger Python
        resoudre({ etat: premier ? 'indisponible' : 'trop-long' });
      }, premier ? 240000 : DELAI_PYTHON);
      python.attente[id] = function (r) { clearTimeout(limite); resoudre(r); };
      extra = extra || {};
      python.worker.postMessage({ id: id, code: code, tests: tests, fichier: fichier, pre: extra.pre || '', graine: extra.graine || '', entrees: extra.entrees === undefined || extra.entrees === null ? null : extra.entrees });
    });
  }

  /* ── L'éditeur de code (modèle : Lagon Arena) ── */

  var AIDE_MOTS = {
    'for': ['pour', 'répète pour chaque valeur'], 'while': ['tant que', 'répète tant que la condition est vraie'],
    'if': ['si', 'teste une condition'], 'elif': ['sinon si', 'autre condition'], 'else': ['sinon', 'tous les autres cas'],
    'in': ['dans', 'parcourt les valeurs de…'], 'range': ['intervalle', 'les entiers de début à fin (exclue)'],
    'print': ['afficher', 'affiche des valeurs'], 'input': ['saisir', 'demande un texte'], 'len': ['longueur', 'nombre d\'éléments'],
    'def': ['définir', 'crée une fonction'], 'return': ['renvoyer', 'renvoie le résultat'], 'and': ['et', 'les deux vraies'],
    'or': ['ou', 'au moins une vraie'], 'not': ['non', 'le contraire'], 'True': ['vrai', ''], 'False': ['faux', ''],
    'break': ['sortir', 'quitte la boucle'], 'int': ['entier', 'transforme en entier'], 'str': ['texte', 'transforme en texte'],
    'float': ['décimal', 'transforme en nombre à virgule'], 'abs': ['valeur absolue', ''], 'min': ['minimum', ''], 'max': ['maximum', ''],
    'sum': ['somme', ''], 'round': ['arrondir', ''], 'None': ['rien', '']
  };
  var METHODES = {
    str: ['upper', 'lower', 'replace', 'split', 'strip', 'count', 'find', 'startswith', 'endswith', 'join'],
    list: ['append', 'pop', 'insert', 'remove', 'sort', 'reverse', 'index', 'count']
  };
  var DEBUT_LIGNE = ['for', 'while', 'if', 'elif', 'else', 'def', 'return', 'print', 'break', 'continue', 'pass'];

  function Editeur(conteneur, valeur, etiquette, surChange) {
    var self = this;
    this.surChange = surChange || function () { };
    this.echap = false; this.choix = []; this.sel = 0;
    var idAide = nouvelId('aide'), idListe = nouvelId('ac');
    this.racine = el('div', { class: 'td-editeur' });
    this.gouttiere = el('div', { class: 'td-gouttiere', 'aria-hidden': 'true' });
    this.zone = el('div', { class: 'td-ed-zone' });
    this.pre = el('pre', { class: 'td-ed-rendu', 'aria-hidden': 'true' });
    this.ta = el('textarea', {
      class: 'td-ed-texte', spellcheck: 'false', autocomplete: 'off', autocapitalize: 'off', autocorrect: 'off', wrap: 'off',
      'aria-label': etiquette || 'Ton code Python', 'aria-describedby': idAide, 'aria-autocomplete': 'list',
      'aria-controls': idListe, 'aria-expanded': 'false', rows: '6'
    });
    this.zone.appendChild(this.pre); this.zone.appendChild(this.ta);
    this.racine.appendChild(this.gouttiere); this.racine.appendChild(this.zone);
    this.liste = el('ul', { class: 'td-ac', id: idListe, role: 'listbox', 'aria-label': 'Propositions', hidden: true });
    this.info = el('p', { class: 'td-ed-info', 'aria-live': 'polite' });
    this.aide = el('p', { class: 'td-ed-aide', id: idAide, text: 'Tab indente. Ctrl+Espace propose la suite du mot. Échap puis Tab pour sortir de l\'éditeur.' });
    conteneur.appendChild(this.racine); conteneur.appendChild(this.liste); conteneur.appendChild(this.info); conteneur.appendChild(this.aide);
    this.ta.value = valeur || '';
    this.ta.addEventListener('input', function (e) {
      self.rendre(); self.surChange(self.ta.value);
      if (e.inputType === 'insertText' && e.data && /[\w.\u00c0-\u024f]/.test(e.data)) self.proposer(false);
      else if (e.inputType === 'deleteContentBackward' && self.ouvert()) self.proposer(false);
      else self.fermer();
    });
    this.ta.addEventListener('keydown', function (e) { self.touche(e); });
    this.ta.addEventListener('blur', function () { self.echap = false; setTimeout(function () { self.fermer(); self.rendre(); }, 150); });
    ['click', 'keyup', 'focus'].forEach(function (ev) {
      self.ta.addEventListener(ev, function (e) { if (!(e.key && /Arrow(Up|Down)/.test(e.key) && self.ouvert())) self.rendre(); });
    });
    this.zone.addEventListener('scroll', function () { self.fermer(); });
    this.rendre();
  }
  Editeur.prototype.valeur = function (v) { if (v === undefined) return this.ta.value; this.ta.value = v; this.rendre(); };
  Editeur.prototype.rendre = function (ligneErr) {
    var v = this.ta.value, lignes = v.split('\n');
    var focus = document.activeElement === this.ta;
    var c = v.slice(0, this.ta.selectionStart).split('\n').length - 1;
    var bloc = focus ? blocDe(lignes, c) : null;
    if (ligneErr !== undefined) this.err = ligneErr;
    var err = this.err, rendu = colorer(v, bloc);
    this.pre.innerHTML = rendu.map(function (l, i) {
      var cls = i + 1 === err ? ' td-l-err' : bloc && i === bloc.entete ? ' td-l-entete' : '';
      return '<span class="td-l' + cls + '">' + (l || ' ') + '</span>';
    }).join('');
    this.gouttiere.innerHTML = lignes.map(function (_, i) {
      var cls = i + 1 === err ? 'err' : bloc && i >= bloc.entete && i <= bloc.fin ? 'bloc' : '';
      return '<span class="' + cls + '">' + (i + 1) + '</span>';
    }).join('');
    var large = Math.max.apply(null, lignes.map(function (l) { return l.length; }).concat([24]));
    this.ta.style.minWidth = this.pre.style.minWidth = 'calc(' + (large + 2) + 'ch + 1.2rem)';
    this.ta.style.height = 'auto'; this.ta.style.height = this.ta.scrollHeight + 'px';
    if (focus && !this.ouvert()) {
      if (bloc) {
        var nom = { 'for': 'la boucle for', 'while': 'la boucle while', 'if': 'le if', 'elif': 'le elif', 'else': 'le else', 'def': 'la fonction' }[bloc.mot] || 'le bloc';
        this.info.innerHTML = c === bloc.entete
          ? 'Ligne ' + (c + 1) + ' : en-tête de <b>' + nom + '</b>, son bloc va jusqu\'à la ligne ' + (bloc.fin + 1) + '.'
          : 'Ligne ' + (c + 1) + ' : dans <b>' + nom + '</b> de la ligne ' + (bloc.entete + 1) + '.';
      } else this.info.textContent = 'Ligne ' + (c + 1) + ' : hors de tout bloc.';
    }
  };
  Editeur.prototype.inserer = function (txt, debut, fin, curseur) {
    this.ta.setRangeText(txt, debut, fin, 'end');
    if (curseur !== undefined) this.ta.selectionStart = this.ta.selectionEnd = debut + curseur;
    this.ta.dispatchEvent(new Event('input'));
  };
  // ce qui a du sens à cet endroit : mots-clés, variables déjà définies, méthodes du type
  Editeur.prototype.suggestions = function (mot, avant) {
    var v = this.ta.value, out = [], vus = {};
    var m0 = sansAccents(mot).toLowerCase();
    function ajouter(nom, genre, role) {
      if (vus[nom] || nom === mot) return;
      var fr = AIDE_MOTS[nom] ? sansAccents(AIDE_MOTS[nom][0]).replace(/\s/g, '') : '';
      var n = nom.toLowerCase(), s = null;
      if (n.indexOf(m0) === 0) s = 0; else if (fr && fr.indexOf(m0.replace(/\s/g, '')) === 0) s = 1; else if (m0.length > 1 && n.indexOf(m0) > 0) s = 2;
      if (s === null) return;
      vus[nom] = 1; out.push({ nom: nom, genre: genre, role: role || (AIDE_MOTS[nom] ? AIDE_MOTS[nom][0] : ''), s: s });
    }
    var pt = avant.match(/([A-Za-z_]\w*|["')\]])\.$/);
    if (pt) {                      // après un point : les méthodes
      var t = null, nomVar = pt[1];
      if (/["']/.test(nomVar)) t = 'str';
      else if (nomVar === ']') t = 'list';
      else {
        var aff = v.match(new RegExp('\\b' + nomVar + '\\s*=\\s*(.)'));
        if (aff) t = aff[1] === '[' ? 'list' : /["'i]/.test(aff[1]) ? 'str' : null;
      }
      (t ? METHODES[t] : METHODES.str.concat(METHODES.list)).forEach(function (n) { ajouter(n, 'méthode', t ? 'de ' + t : ''); });
    } else {
      var debut = avant.trim() === '';
      var noms = {}, re = /^\s*(?:for\s+(\w+)\s+in|def\s+(\w+)|(\w+)\s*=[^=])/gm, r;
      while ((r = re.exec(v))) noms[r[1] || r[2] || r[3]] = r[2] ? 'fonction' : 'variable';
      var param = /def\s+\w+\s*\(([^)]*)\)/g;
      while ((r = param.exec(v))) r[1].split(',').forEach(function (p) { p = p.trim().split('=')[0].trim(); if (p) noms[p] = 'variable'; });
      Object.keys(noms).forEach(function (n) { ajouter(n, noms[n], noms[n]); });
      if (debut) DEBUT_LIGNE.forEach(function (n) { ajouter(n, 'mot-clé'); });
      else {
        if (/\bfor\s+\w+\s+in\s+\w*$/.test(avant)) ajouter('range', 'fonction');
        ['in', 'and', 'or', 'not', 'True', 'False', 'None', 'range', 'len', 'int', 'str', 'float', 'input', 'abs', 'min', 'max', 'sum', 'round'].forEach(function (n) { ajouter(n, MOTS.indexOf(n) >= 0 ? 'mot-clé' : 'fonction'); });
      }
    }
    out.sort(function (a, b) { return a.s - b.s || (a.genre === 'variable' ? -1 : 0) - (b.genre === 'variable' ? -1 : 0) || a.nom.length - b.nom.length; });
    return out.slice(0, 7);
  };
  Editeur.prototype.proposer = function (force) {
    var v = this.ta.value, s = this.ta.selectionStart;
    var deb = v.lastIndexOf('\n', s - 1) + 1, avant = v.slice(deb, s);
    if (/#/.test(avant) || (avant.split(/["']/).length % 2 === 0)) return this.fermer();   // dans un commentaire ou une chaîne
    var m = avant.match(/[A-Za-z_\u00c0-\u024f][\w\u00c0-\u024f]*$/) || (/\.$/.test(avant) ? [''] : null);
    if (!m || (!force && m[0] === '' && !/\.$/.test(avant))) return this.fermer();
    if (/^[\w(]/.test(v.slice(s))) return this.fermer();
    this.mot = { debut: s - m[0].length, mot: m[0] };
    this.choix = this.suggestions(m[0], avant.slice(0, avant.length - m[0].length));
    if (!this.choix.length) return this.fermer();
    this.sel = 0; this.dessiner();
  };
  Editeur.prototype.dessiner = function () {
    var self = this;
    this.liste.innerHTML = '';
    this.choix.forEach(function (c, k) {
      var li = el('li', { role: 'option', id: self.liste.id + '-' + k, 'aria-selected': String(k === self.sel), class: k === self.sel ? 'on' : '' }, [
        el('code', { text: c.nom + (c.genre === 'fonction' || c.genre === 'méthode' ? '()' : '') }),
        el('span', { class: 'td-ac-role', text: c.genre + (c.role && c.role !== c.genre ? ' · ' + c.role : '') })
      ]);
      li.addEventListener('mousedown', function (e) { e.preventDefault(); self.sel = k; self.accepter(); });
      self.liste.appendChild(li);
    });
    this.liste.hidden = false;
    this.ta.setAttribute('aria-expanded', 'true');
    this.ta.setAttribute('aria-activedescendant', this.liste.id + '-' + this.sel);
    // position : sous le mot (police à chasse fixe)
    var cs = getComputedStyle(this.ta), v = this.ta.value, s = this.mot.debut;
    var ligne = v.slice(0, s).split('\n').length - 1, col = s - (v.lastIndexOf('\n', s - 1) + 1);
    var lh = parseFloat(cs.lineHeight) || 20, cw = this.largeurCar();
    var zr = this.zone.getBoundingClientRect(), pr = this.liste.parentNode.getBoundingClientRect();
    var x = zr.left - pr.left + parseFloat(cs.paddingLeft) + col * cw - this.zone.scrollLeft;
    var y = zr.top - pr.top + parseFloat(cs.paddingTop) + (ligne + 1) * lh + 2;
    this.liste.style.left = Math.max(0, Math.min(x, pr.width - this.liste.offsetWidth)) + 'px';
    this.liste.style.top = y + 'px';
    var c = this.choix[this.sel];
    this.info.textContent = c.nom + ' : ' + c.genre + (c.role && c.role !== c.genre ? ', ' + c.role : '') + '. Entrée pour choisir.';
  };
  Editeur.prototype.largeurCar = function () {
    if (this.cw) return this.cw;
    var cs = getComputedStyle(this.ta), m = el('span', { text: 'MMMMMMMMMM' });
    m.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;font-family:' + cs.fontFamily + ';font-size:' + cs.fontSize;
    document.body.appendChild(m); this.cw = m.getBoundingClientRect().width / 10; m.remove();
    return this.cw;
  };
  Editeur.prototype.fermer = function () {
    this.liste.hidden = true; this.choix = [];
    this.ta.setAttribute('aria-expanded', 'false'); this.ta.removeAttribute('aria-activedescendant');
  };
  Editeur.prototype.ouvert = function () { return !this.liste.hidden && this.choix.length > 0; };
  Editeur.prototype.accepter = function () {
    var c = this.choix[this.sel]; if (!c) return;
    var s = this.ta.selectionStart, txt = c.nom, cur;
    if (c.genre === 'fonction' || c.genre === 'méthode') { txt += '()'; cur = txt.length - 1; }
    else if (['for', 'while', 'if', 'elif', 'in', 'and', 'or', 'not', 'return'].indexOf(c.nom) >= 0) txt += ' ';
    else if (c.nom === 'else') txt += ':';
    this.fermer();
    this.inserer(txt, this.mot.debut, s, cur);
  };
  Editeur.prototype.touche = function (e) {
    var ta = this.ta, v = ta.value, s = ta.selectionStart, f = ta.selectionEnd;
    if (this.echap && e.key === 'Tab') { this.echap = false; return; }       // sortir de l'éditeur (WCAG 2.1.2)
    if (['Shift', 'Control', 'Alt', 'Meta'].indexOf(e.key) < 0) this.echap = false;
    if (this.ouvert()) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); this.sel = (this.sel + (e.key === 'ArrowDown' ? 1 : -1) + this.choix.length) % this.choix.length; this.dessiner(); return;
      }
      if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); this.accepter(); return; }
      if (e.key === 'Escape') { e.preventDefault(); this.fermer(); return; }
    }
    if (e.key === 'Escape') { this.echap = true; this.info.textContent = 'Appuie sur Tab pour sortir de l\'éditeur.'; return; }
    if (e.key === ' ' && e.ctrlKey) { e.preventDefault(); this.proposer(true); return; }
    var deb = v.lastIndexOf('\n', s - 1) + 1;
    if (e.key === 'Tab') {
      e.preventDefault();
      if (s === f && !e.shiftKey) { this.inserer('    ', s, f); return; }
      var finL = v.indexOf('\n', f - (f > s && v[f - 1] === '\n' ? 1 : 0)), fin = finL < 0 ? v.length : finL;
      var bloc = v.slice(deb, fin).split('\n').map(function (l) { return e.shiftKey ? l.replace(/^ {1,4}/, '') : '    ' + l; }).join('\n');
      ta.setRangeText(bloc, deb, fin, 'select'); ta.dispatchEvent(new Event('input'));
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      var ligne = v.slice(deb, s), ind = ligne.match(/^ */)[0];
      if (/:\s*(#.*)?$/.test(ligne)) ind += '    ';
      else if (/^\s*(return|break|continue|pass)\b/.test(ligne)) ind = ind.slice(4);
      this.inserer('\n' + ind, s, f);
    } else if (e.key === 'Backspace' && s === f) {
      var av = v.slice(deb, s);
      if (av.length >= 4 && /^ +$/.test(av)) { e.preventDefault(); this.inserer('', s - (av.length % 4 || 4), s); }
    }
  };

  /* ── Retours bienveillants ─────────────────── */

  var BRAVO = ['Juste. Bien raisonné !', 'C\'est ça : tu as bien suivi le programme.', 'Exact. Tu peux passer à la suite.', 'Juste ! Ton raisonnement tient la route.'];
  var ENCORE = ['Pas encore. Relis la consigne, puis réessaie.', 'Ce n\'est pas tout à fait ça. Suis le programme ligne par ligne.', 'Pas encore : c\'est en se trompant qu\'on apprend. Un coup de pouce peut t\'aider.', 'Presque ? Vérifie chaque ligne, une par une.'];

  /* ── Une question ──────────────────────────── */

  function Question(feuille, section, rang, index) {
    this.f = feuille; this.s = section; this.rang = rang;
    this.type = section.getAttribute('data-type');
    this.id = section.id || ('q' + (index || rang));
    section.id = this.id;
    // data-support="papier" : imprimée seulement, jamais comptée ; data-support="ecran" : à l'écran seulement
    this.support = section.getAttribute('data-support') || '';
    // « Écris le programme » : obligatoire si la page porte data-code="obligatoire" (défaut de nouveau-td.py, 21/11)
    // ou si la question porte data-obligatoire ; data-bonus en fait toujours un bonus
    var codeObligatoire = section.hasAttribute('data-obligatoire') || !!section.closest('[data-code="obligatoire"]');
    this.bonus = section.hasAttribute('data-bonus') || (this.type === 'code' && !codeObligatoire);
    this.compte = this.support !== 'papier' && this.type !== 'libre';
    this.etat = feuille.memoire.q[this.id] || { essais: 0, aides: 0 };
    this.juste = !!this.etat.juste;
  }
  Question.prototype.enregistrer = function () {
    this.etat.juste = this.juste;
    this.f.memoire.q[this.id] = this.etat;
    this.f.sauver();
  };
  Question.prototype.monter = function () {
    var q = this, s = this.s, idTitre = nouvelId('titre');
    s.classList.add('td-q-prete');
    s.setAttribute('aria-labelledby', idTitre);
    // une question des deux supports peut avoir un autre numéro sur papier (après des questions d'un seul support)
    var num = this.numPapier !== null && this.numPapier !== undefined && this.numPapier !== this.rang
      ? el('span', { class: 'td-q-num' }, [el('span', { class: 'td-num-ecran', text: 'Question ' + this.rang }), el('span', { class: 'td-num-papier', 'aria-hidden': 'true', text: 'Question ' + this.numPapier })])
      : el('span', { class: 'td-q-num', text: 'Question ' + this.rang });
    var titre = el('h3', { class: 'td-q-titre', id: idTitre }, [
      num,
      this.type === 'libre' && this.support !== 'papier' ? el('span', { class: 'td-q-bonus td-ecran-seul', text: 'non corrigée en ligne' }) : null,
      this.bonus ? el('span', { class: 'td-q-bonus', text: '★ bonus' }) : null,
      el('span', { class: 'td-q-etat', 'aria-hidden': 'true' })
    ]);
    s.insertBefore(titre, s.firstChild);
    this.titre = titre;
    s.querySelectorAll('pre.td-code').forEach(function (p) { if (q.type !== 'trous' && !p.closest('.td-options')) afficherCode(p); });
    s.querySelectorAll('pre.td-erreur').forEach(function (p) {
      var b = blocErreur(p.textContent.replace(/^\n/, ''));
      p.parentNode.replaceChild(b, p);
    });
    this.zone = el('div', { class: 'td-reponse' });
    var apres = s.querySelector('.td-aide, .td-correction');
    s.insertBefore(this.zone, apres || null);
    this['monter_' + this.type].call(this);
    this.monterActions();
    this.afficherEtat(false);
  };

  // actions communes : vérifier, coup de pouce, correction, retour
  Question.prototype.monterActions = function () {
    var q = this, s = this.s;
    this.aides = Array.prototype.slice.call(s.querySelectorAll('.td-aide'));
    this.correction = s.querySelector('.td-correction');
    this.retours = Array.prototype.slice.call(s.querySelectorAll('.td-retour'));
    this.aides.forEach(function (a, i) {
      a.hidden = i >= q.etat.aides;
      a.insertBefore(el('b', { class: 'td-aide-num', text: 'Coup de pouce ' + (i + 1) + ' : ' }), a.firstChild);
    });
    this.retours.forEach(function (r) { r.hidden = true; });
    if (this.correction) {
      this.correction.hidden = !this.etat.vu;
      this.correction.insertBefore(el('p', { class: 'td-corr-titre', text: 'Correction' }), this.correction.firstChild);
      this.correction.querySelectorAll('pre.td-code').forEach(function (p) { if (!p.classList.contains('td-code-pret')) afficherCode(p); });
    }
    this.retour = el('div', { class: 'td-retour-zone', role: 'status', 'aria-live': 'polite' });
    var barre = el('div', { class: 'td-actions' });
    if (this.type !== 'code' && this.type !== 'libre') {
      this.bVerifier = el('button', { type: 'button', class: 'td-bouton td-principal', text: 'Vérifier' });
      this.bVerifier.addEventListener('click', function () { q.verifier(); });
      barre.appendChild(this.bVerifier);
    }
    if (this.aides.length) {
      this.bAide = el('button', { type: 'button', class: 'td-bouton', text: '' });
      this.bAide.addEventListener('click', function () { q.aider(); });
      barre.appendChild(this.bAide);
    }
    this.bCorr = el('button', { type: 'button', class: 'td-bouton', text: 'Voir la correction', hidden: true, 'aria-expanded': 'false' });
    if (this.correction) { this.correction.id = this.correction.id || nouvelId('corr'); this.bCorr.setAttribute('aria-controls', this.correction.id); }
    this.bCorr.addEventListener('click', function () { q.voirCorrection(); });
    barre.appendChild(this.bCorr);
    this.zone.appendChild(barre);
    this.zone.appendChild(this.retour);
    this.majBoutons();
  };
  Question.prototype.majBoutons = function () {
    if (this.bAide) {
      var reste = this.aides.length - this.etat.aides;
      this.bAide.hidden = reste <= 0;
      this.bAide.textContent = this.etat.aides ? 'Un autre coup de pouce (' + reste + ')' : 'Un coup de pouce';
    }
    this.bCorr.hidden = this.type === 'libre' ? !(this.correction && !this.etat.vu) : !(this.etat.essais >= ESSAIS_AVANT_CORRECTION && !this.etat.vu);
  };
  Question.prototype.aider = function () {
    var a = this.aides[this.etat.aides]; if (!a) return;
    a.hidden = false; this.etat.aides++;
    a.setAttribute('tabindex', '-1'); a.focus();
    this.majBoutons(); this.enregistrer();
  };
  Question.prototype.voirCorrection = function () {
    this.etat.vu = true;
    if (this.correction) { this.correction.hidden = false; this.correction.setAttribute('tabindex', '-1'); this.correction.focus(); }
    else this.dire('La bonne réponse : ' + this.attenduTexte(), 'info');
    this.bCorr.setAttribute('aria-expanded', 'true');
    this.majBoutons(); this.enregistrer();
  };
  Question.prototype.dire = function (html, genre) {
    this.retour.className = 'td-retour-zone ' + (genre || '');
    this.retour.innerHTML = '';
    if (html) this.retour.appendChild(el('p', { html: html }));
  };
  Question.prototype.conclure = function (juste, cible) {
    this.etat.essais++;
    this.juste = juste;
    var n = this.etat.essais + this.rang;
    this.retours.forEach(function (r) { r.hidden = true; });
    if (juste) {
      this.dire('<b>✓ ' + choisir(BRAVO, n) + '</b>', 'juste');
      if (this.surJuste) this.surJuste();
    } else {
      this.dire('<b>' + choisir(ENCORE, n) + '</b>', 'encore');
      if (cible) { cible.hidden = false; this.retour.appendChild(cible.cloneNode(true)).hidden = false; cible.hidden = true; }
    }
    this.afficherEtat(true);
    this.majBoutons(); this.enregistrer();
    this.f.maj(true);
  };
  Question.prototype.afficherEtat = function () {
    this.s.classList.toggle('td-est-juste', this.juste);
    this.s.classList.toggle('td-est-encore', !this.juste && this.etat.essais > 0);
    var e = this.titre.querySelector('.td-q-etat');
    e.textContent = this.juste ? '✓ réussie' : this.etat.essais ? 'à reprendre' : '';
    this.titre.setAttribute('aria-label', 'Question ' + this.rang + (this.bonus ? ', bonus' : '') + (this.juste ? ', réussie' : ''));
  };
  Question.prototype.retourPour = function (valeur, mode) {
    for (var i = 0; i < this.retours.length; i++) {
      if (unParmi(valeur, alternatives(this.retours[i].getAttribute('data-si')), mode)) return this.retours[i];
    }
    return null;
  };
  Question.prototype.attenduTexte = function () { return esc(alternatives(this.s.getAttribute('data-reponse'))[0]); };

  /* réponse courte */
  Question.prototype.monter_courte = function () {
    var q = this, id = nouvelId('rep');
    this.mode = this.s.getAttribute('data-comparer') || 'texte';
    this.champ = el('input', { type: 'text', id: id, class: 'td-champ', autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off' });
    if (this.mode === 'code') this.champ.classList.add('td-mono');
    this.champ.value = this.etat.valeur || '';
    this.champ.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); q.verifier(); } });
    this.champ.addEventListener('input', function () { q.etat.valeur = q.champ.value; q.enregistrer(); });
    var etiq = this.s.getAttribute('data-etiquette');
    this.zone.appendChild(el('div', { class: 'td-ligne-champ' }, [el('label', { for: id, class: etiq ? null : 'td-etiquette-defaut', text: etiq || 'Ta réponse :' }), this.champ]));
    this.mettreDeCote();
  };
  // sur papier, une réponse courte simple (une consigne, une ligne à remplir, ni code ni tableau ni figure) tient
  // sur une seule ligne : la consigne, puis la ligne à remplir (T123c, « Resserrer »). Écran inchangé.
  var IMPRIME_SANS = /^(td-aide|td-correction|td-retour|td-attendu|td-q-titre|td-consigne|td-reponse)$/;
  Question.prototype.courteSimple = function () {
    if (this.type !== 'courte' || this.s.classList.contains('td-cote')) return false;
    var consignes = 0, ok = true;
    Array.prototype.forEach.call(this.s.children, function (c) {
      if (c.matches('script, [data-support="ecran"], .td-plus-loin:not([data-support="papier"])')) return;
      if (c.matches('p.td-consigne')) { consignes++; if (c.querySelector('pre, table, svg, img, figure, ul, ol, br') || c.textContent.replace(/\s+/g, ' ').trim().length > 150) ok = false; return; }
      if (!Array.prototype.some.call(c.classList, function (k) { return IMPRIME_SANS.test(k); })) ok = false;
    });
    return ok && consignes === 1;
  };
  Question.prototype.verifier_courte = function () {
    var v = this.champ.value;
    if (!v.trim()) return this.dire('Écris ta réponse dans la case, puis vérifie.', 'info');
    var ok = unParmi(v, alternatives(this.s.getAttribute('data-reponse')), this.mode);
    this.conclure(ok, ok ? null : this.retourPour(v, this.mode));
  };

  /* QCU et cases à cocher */
  Question.prototype.monter_qcu = function () { this.monterOptions('radio'); };
  Question.prototype.monter_cases = function () { this.monterOptions('checkbox'); };
  Question.prototype.monterOptions = function (genre) {
    var q = this, ul = this.s.querySelector('.td-options'), nom = nouvelId('opt');
    var fs = el('fieldset', { class: 'td-choix' }, [el('legend', { class: 'td-invisible', text: genre === 'radio' ? 'Choisis une réponse' : 'Coche toutes les bonnes réponses' })]);
    if (genre === 'checkbox') fs.appendChild(el('p', { class: 'td-indic', 'aria-hidden': 'true', text: 'Plusieurs réponses possibles.' }));
    this.options = [];
    var lis = Array.prototype.slice.call(ul.children).map(function (li, i) { return { li: li, i: i }; });
    // data-ordre="melange" (question ou page) : options mélangées, toujours de la même façon pour cette question ;
    // data-ordre="fixe" sur la question garde l'ordre écrit. Sans attribut : l'ordre écrit (pages d'avant le 21/11).
    var ordre = (this.s.closest('[data-ordre]') || { getAttribute: function () { return 'fixe'; } }).getAttribute('data-ordre');
    if (ordre === 'melange' && lis.length > 1) {
      var r = hasard(this.f.id + '/' + this.id + '/options'), essai = 0, sur;
      do {
        sur = lis.slice();
        for (var a = sur.length - 1; a > 0; a--) { var b = Math.floor(r() * (a + 1)), t = sur[a]; sur[a] = sur[b]; sur[b] = t; }
      } while (sur.every(function (x, k) { return x.i === k; }) && ++essai < 10);
      lis = sur;
    }
    lis.forEach(function (x, pos) {
      var li = x.li, i = x.i;
      var idc = nom + '-' + i;
      var input = el('input', { type: genre, name: nom, id: idc, value: String(i) });
      input.checked = (q.etat.valeur || []).indexOf(i) >= 0;
      input.addEventListener('change', function () { q.etat.valeur = q.options.filter(function (o) { return o.input.checked; }).map(function (o) { return o.i; }); q.enregistrer(); });
      var lab = el('label', { for: idc, class: 'td-option' });
      while (li.firstChild) lab.appendChild(li.firstChild);
      lab.querySelectorAll('pre.td-code').forEach(function (p) { afficherCode(p, { sansNumeros: true }); });
      fs.appendChild(el('div', { class: 'td-opt' }, [input, lab]));
      q.options.push({ i: i, pos: pos, input: input, juste: li.hasAttribute('data-juste'), retour: li.getAttribute('data-retour') });
    });
    ul.parentNode.removeChild(ul);
    // sur papier, des options courtes passent sur trois ou quatre colonnes
    if (!fs.querySelector('pre') && this.options.length >= 3) {
      var plus = Math.max.apply(null, this.options.map(function (o) { return o.input.parentNode.textContent.trim().length; }));
      if (plus <= 12 && this.options.length >= 4) fs.classList.add('td-choix-4'); else if (plus <= 26) fs.classList.add('td-choix-3');
    }
    this.zone.appendChild(fs);
    this.mettreDeCote();
  };
  // sur papier, un code étroit (34 caractères au plus : la moitié de la ligne, numéros compris) se met à gauche et la réponse à droite (sortie, qcu, cases) ;
  // data-cote="non" l'empêche, data-cote="oui" le force
  Question.prototype.mettreDeCote = function () {
    var codes = Array.prototype.filter.call(this.s.children, function (c) { return c.matches('pre.td-code'); });
    var cote = this.s.getAttribute('data-cote');
    if (cote === 'non' || codes.length !== 1 || this.s.querySelector(':scope > table, :scope > .td-table')) return;
    if (this.options && this.options.some(function (o) { return o.input.parentNode.querySelector('pre'); })) return;
    var source = this.sourceTrous || codes[0].getAttribute('data-source') || codes[0].textContent;
    var large = Math.max.apply(null, source.split('\n').map(function (l) { return l.length; }));
    if (cote === 'oui' || large <= 34) this.s.classList.add('td-cote');
  };
  Question.prototype.verifier_qcu = function () {
    var coche = this.options.filter(function (o) { return o.input.checked; });
    if (!coche.length) return this.dire('Choisis une réponse, puis vérifie.', 'info');
    var o = coche[0], ok = o.juste;
    this.conclure(ok, null);
    if (!ok && o.retour) this.retour.appendChild(el('p', { text: o.retour }));
  };
  Question.prototype.verifier_cases = function () {
    var q = this, coche = this.options.filter(function (o) { return o.input.checked; });
    if (!coche.length) return this.dire('Coche au moins une case, puis vérifie.', 'info');
    var ok = this.options.every(function (o) { return o.juste === o.input.checked; });
    this.conclure(ok, null);
    if (!ok) {
      coche.filter(function (o) { return !o.juste && o.retour; }).forEach(function (o) { q.retour.appendChild(el('p', { text: o.retour })); });
      if (this.options.some(function (o) { return o.juste && !o.input.checked; })) this.retour.appendChild(el('p', { text: 'Il manque au moins une bonne réponse.' }));
    }
  };
  Question.prototype.attenduTexte_options = function () {
    return this.options.filter(function (o) { return o.juste; }).map(function (o) { return 'choix ' + (o.pos + 1); }).join(', ');
  };

  /* compléter un code : [[réponse|autre réponse]] dans le pre.td-code */
  Question.prototype.monter_trous = function () {
    var q = this, pre = this.s.querySelector('pre.td-code');
    var texte = pre.textContent.replace(/^\n/, '').replace(/\s+$/, '');
    this.trous = [];
    var lignes = texte.split('\n'), d = decalages(lignes.map(function (l) { return decouperTrous(l).map(function (m, k) { return k % 2 ? 'x' : m; }).join(''); }));
    var lang = langue(pre);
    // largeur commune à toutes les cases de la question (elle ne trahit pas la réponse) : data-largeur (en caractères)
    // sur la question ou la page ; sinon la plus longue réponse, arrondie au palier supérieur (6, 10, 16, 24, 32, 48)
    var reglee = parseInt((this.s.closest('[data-largeur]') || { getAttribute: function () { return ''; } }).getAttribute('data-largeur'), 10);
    var plusLongue = 0;
    lignes.forEach(function (l) { decouperTrous(l).forEach(function (m, k) { if (k % 2) alternatives(m).forEach(function (r) { plusLongue = Math.max(plusLongue, r.trim().length); }); }); });
    var largeurCommune = reglee > 0 ? reglee : [6, 10, 16, 24, 32, 48].filter(function (x) { return x >= plusLongue; })[0] || plusLongue;
    // une ligne qui a plusieurs cases doit tenir sur la page (80 caractères, numéros compris) : la largeur commune
    // est réduite s'il le faut, sans descendre sous la plus longue réponse de cette ligne
    var parTrou = false;      // ligne trop chargée : chaque case garde sa propre largeur (comme avant le 21/11)
    if (!(reglee > 0)) lignes.forEach(function (l) {
      var m = decouperTrous(l), n = (m.length - 1) / 2;
      if (!n) return;
      var texte = m.filter(function (_, k) { return k % 2 === 0; }).join('').length;
      var propre = Math.max.apply(null, m.filter(function (_, k) { return k % 2; }).map(function (x) { return Math.max.apply(null, alternatives(x).map(function (r) { return r.trim().length; })); }));
      var place = Math.floor((72 - texte) / n) - 4;
      if (place < largeurCommune) largeurCommune = Math.max(place, propre, 4);
      if (texte + n * (largeurCommune + 5) > 76) parTrou = true;
    });
    pre.innerHTML = '';
    function largeurDe(m) { return parTrou ? Math.max.apply(null, alternatives(m).map(function (r) { return r.length; })) + 2 : largeurCommune + 2; }
    var alignes = lang === 'python' ? commentairesAlignes(lignes, largeurDe) : {};
    lignes.forEach(function (l, n) {
      var span = el('span', { class: 'td-l' });
      span.appendChild(el('span', { class: 'td-num', 'aria-hidden': 'true', text: String(n + 1) }));
      var al = alignes[n];
      if (al) {
        // commentaire aligné (T123c) : le code avant le commentaire prend la même largeur sur toutes les lignes
        // du groupe, cases comprises (à l'écran comme sur papier, où les cases sont plus larges)
        var avant = el('span', { class: 'td-avant-com' });
        avant.style.minWidth = al.largeur;
        span.appendChild(avant);
        ajouter(avant, decouperTrous(l.slice(0, al.coupe)), n, false);
        ajouter(span, decouperTrous(l.slice(al.coupe).replace(/^ +/, '')), n, true);
      } else ajouter(span, decouperTrous(l), n, false);
      pre.appendChild(span);
    });
    function ajouter(cible, morceaux, n, commentaire) {
      morceaux.forEach(function (m, k) {
        if (k % 2 === 0) {
          var h = el('span');
          if (commentaire) h.innerHTML = k === 0 ? colorerMots(m, lang) : (m ? '<span class="tk-com">' + esc(m) + '</span>' : '');
          else h.innerHTML = k === 0 ? colorerLigne(m, m.trim() ? decalage(m) : d[n], null, n, lang) : colorerMots(m, lang);
          cible.appendChild(h);
        } else {
          var rep = alternatives(m), num = q.trous.length;
          var largeur = largeurDe(m);
          var input = el('input', {
            type: 'text', class: 'td-trou', size: String(largeur), autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off',
            'aria-label': 'Case ' + (num + 1) + ', ligne ' + (n + 1)
          });
          input.style.width = (largeur + 1) + 'ch';
          input.value = (q.etat.valeur || [])[num] || '';
          input.addEventListener('input', function () { q.etat.valeur = q.trous.map(function (t) { return t.input.value; }); q.enregistrer(); });
          input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); q.verifier(); } });
          q.trous.push({ input: input, rep: rep });
          cible.appendChild(input);
        }
      });
    }
    pre.classList.add('td-code-pret', 'td-code-trous');
    if (lignes.length > CODE_LONG) pre.classList.add('td-code-long');
    // largeur du code sur papier (chaque case compte pour sa largeur) : code étroit = réponse à côté
    this.sourceTrous = lignes.map(function (l) { return decouperTrous(l).map(function (m, k) { return k % 2 ? new Array((parTrou ? Math.max.apply(null, alternatives(m).map(function (r) { return r.length; })) : largeurCommune) + 6).join('x') : m; }).join(''); }).join('\n');
    this.mettreDeCote();
  };
  Question.prototype.verifier_trous = function () {
    var vides = this.trous.filter(function (t) { return !t.input.value.trim(); }).length;
    if (vides === this.trous.length) return this.dire('Remplis les cases du code, puis vérifie.', 'info');
    var faux = this.trous.filter(function (t) { return !unParmi(t.input.value, t.rep, 'code'); });
    this.trous.forEach(function (t) { t.input.setAttribute('aria-invalid', String(faux.indexOf(t) >= 0)); });
    this.conclure(!faux.length, null);
    if (faux.length) this.retour.appendChild(el('p', { text: faux.length === 1 ? 'Une case est à revoir (elle est marquée d\'un trait épais).' : faux.length + ' cases sont à revoir (elles sont marquées d\'un trait épais).' }));
  };
  Question.prototype.attenduTexte_trous = function () { return this.trous.map(function (t) { return '<code>' + esc(t.rep[0]) + '</code>'; }).join(', '); };

  /* prévoir la sortie */
  Question.prototype.monter_sortie = function () {
    var q = this, id = nouvelId('sortie'), att = this.s.querySelector('pre.td-attendu');
    this.attendu = att ? att.textContent.replace(/^\n/, '').replace(/\s+$/, '') : '';
    if (att) att.parentNode.removeChild(att);
    var n = this.attendu.split('\n').length;
    this.champ = el('textarea', { id: id, class: 'td-champ td-mono td-sortie', rows: String(Math.max(2, n + 1)), spellcheck: 'false', autocapitalize: 'off', autocomplete: 'off' });
    // sur papier : data-lignes lignes à remplir (sinon, autant que de lignes attendues)
    this.champ.style.setProperty('--td-lignes', String(+this.s.getAttribute('data-lignes') || n));
    this.champ.value = this.etat.valeur || '';
    this.champ.addEventListener('input', function () { q.etat.valeur = q.champ.value; q.enregistrer(); });
    this.zone.appendChild(el('div', { class: 'td-ligne-champ td-bloc-champ' }, [
      el('label', { for: id, text: this.s.getAttribute('data-etiquette') || 'Ce que le programme affiche (une ligne par ligne d\'affichage) :' }), this.champ]));
    this.mettreDeCote();
    this.surJuste = function () {
      this.retour.appendChild(el('p', { class: 'td-etiquette-console', text: 'sortie' }));
      this.retour.appendChild(console_(this.attendu));
    };
  };
  Question.prototype.verifier_sortie = function () {
    var v = this.champ.value;
    if (!v.trim()) return this.dire('Écris ce que le programme affiche, puis vérifie.', 'info');
    var ex = this.s.getAttribute('data-espaces') === 'exact';
    var ok = normSortie(v, ex) === normSortie(this.attendu, ex);
    var cible = ok ? null : this.retourPour(v, 'texte');
    this.conclure(ok, cible);
    if (!ok) {
      var a = normSortie(v, ex).split('\n'), b = normSortie(this.attendu, ex).split('\n');
      if (a.length !== b.length) this.retour.appendChild(el('p', { text: 'Compte les lignes : le programme en affiche ' + (a.length < b.length ? 'plus' : 'moins') + ' que toi.' }));
      else for (var i = 0; i < b.length; i++) if (a[i] !== b[i]) { this.retour.appendChild(el('p', { text: 'Le bon nombre de lignes. Regarde à partir de ta ligne ' + (i + 1) + '.' })); break; }
    }
  };
  Question.prototype.attenduTexte_sortie = function () { return '<br>' + esc(this.attendu).replace(/\n/g, '<br>'); };

  /* réponse libre (data-type="libre", data-lignes="4") : des lignes à remplir sur papier ; à l'écran, une zone
     de brouillon non corrigée (la question ne compte jamais dans l'avancement) */
  Question.prototype.monter_libre = function () {
    // data-lignes="0" : aucune ligne sur papier (réponse dans un tableau, « entoure sur le code ») ; sans attribut : 3 (T123c)
    var q = this, id = nouvelId('libre'), a = this.s.getAttribute('data-lignes'), n = a !== null && a.trim() !== '' && !isNaN(+a) ? Math.max(0, Math.round(+a)) : 3;
    this.champ = el('textarea', { id: id, class: 'td-champ td-libre' + (n ? '' : ' td-sans-ligne'), rows: String(Math.max(1, n)), spellcheck: 'true' });
    this.champ.style.setProperty('--td-lignes', String(n));
    this.champ.value = this.etat.valeur || '';
    this.champ.addEventListener('input', function () { q.etat.valeur = q.champ.value; q.enregistrer(); });
    this.zone.appendChild(el('div', { class: 'td-ligne-champ td-bloc-champ' }, [
      el('label', { for: id, class: this.support === 'papier' ? 'td-invisible' : (this.s.getAttribute('data-etiquette') ? null : 'td-etiquette-defaut'), text: this.s.getAttribute('data-etiquette') || 'Ta réponse (rédigée, non corrigée ici : compare avec la correction) :' }), this.champ]));
    this.mettreDeCote();       // data-cote : le code à gauche, les lignes à droite (T123c)
  };
  Question.prototype.verifier_libre = function () { };

  /* remettre des lignes dans l'ordre */
  Question.prototype.monter_ordre = function () {
    var q = this, ol = this.s.querySelector('.td-lignes');
    this.lignesJustes = Array.prototype.slice.call(ol.children).map(function (li) { return li.textContent.replace(/\s+$/, ''); });
    ol.parentNode.removeChild(ol);
    var n = this.lignesJustes.length, ordre, r = hasard(this.f.id + this.id), essai = 0;
    // l'ordre mélangé de départ (toujours le même) : c'est lui qui s'imprime
    do {
      ordre = this.lignesJustes.map(function (_, i) { return i; });
      for (var i = n - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)), t = ordre[i]; ordre[i] = ordre[j]; ordre[j] = t; }
    } while (this.estDansOrdre(ordre) && ++essai < 20);
    this.ordreDepart = ordre.slice();
    var garde = this.etat.valeur;
    this.ordre = garde && garde.length === n ? garde.slice() : ordre;
    this.liste = el('ol', { class: 'td-ordre', 'aria-label': 'Lignes à remettre dans l\'ordre' });
    this.annonce = el('p', { class: 'td-invisible', 'aria-live': 'assertive' });
    this.zone.appendChild(el('p', { class: 'td-indic', text: 'Utilise les flèches ▲ ▼ (ou Alt + flèche haut ou bas) pour déplacer une ligne.' }));
    this.zone.appendChild(this.liste); this.zone.appendChild(this.annonce);
    this.dessinerOrdre();
    this.mettreDeCote();
  };
  Question.prototype.estDansOrdre = function (ordre) {
    var L = this.lignesJustes;
    return ordre.every(function (k, i) { return L[k] === L[i]; });   // deux lignes identiques peuvent s'échanger
  };
  Question.prototype.dessinerOrdre = function (focusSur, sens) {
    var q = this, n = this.ordre.length;
    this.liste.innerHTML = '';
    this.ordre.forEach(function (k, pos) {
      var texte = q.lignesJustes[k];
      var code = el('pre', { class: 'td-code td-code-pret td-sans-num td-ordre-code', html: '<span class="td-l">' + colorerLigne(texte, decalage(texte), null, 0, langue(q.s)) + '</span>' });
      var court = texte.trim();
      var haut = el('button', { type: 'button', class: 'td-bouton td-fleche', 'aria-label': 'Monter la ligne « ' + court + ' »', text: '▲', disabled: pos === 0 });
      var bas = el('button', { type: 'button', class: 'td-bouton td-fleche', 'aria-label': 'Descendre la ligne « ' + court + ' »', text: '▼', disabled: pos === n - 1 });
      haut.addEventListener('click', function () { q.deplacer(pos, -1, 'haut'); });
      bas.addEventListener('click', function () { q.deplacer(pos, 1, 'bas'); });
      var li = el('li', { class: 'td-ordre-ligne', tabindex: '-1' }, [el('span', { class: 'td-ordre-num', 'aria-hidden': 'true', text: String(pos + 1) }), code, el('span', { class: 'td-ordre-btn' }, [haut, bas])]);
      li.addEventListener('keydown', function (e) {
        if (e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) { e.preventDefault(); q.deplacer(pos, e.key === 'ArrowUp' ? -1 : 1, e.key === 'ArrowUp' ? 'haut' : 'bas'); }
      });
      q.liste.appendChild(li);
    });
    if (focusSur !== undefined) {
      var li = this.liste.children[focusSur], b = li.querySelectorAll('button')[sens === 'haut' ? 0 : 1];
      (b && !b.disabled ? b : li.querySelector('button:not([disabled])')).focus();
    }
  };
  Question.prototype.deplacer = function (pos, d, sens) {
    var p2 = pos + d; if (p2 < 0 || p2 >= this.ordre.length) return;
    var t = this.ordre[pos]; this.ordre[pos] = this.ordre[p2]; this.ordre[p2] = t;
    this.etat.valeur = this.ordre.slice(); this.enregistrer();
    this.dessinerOrdre(p2, sens);
    this.annonce.textContent = 'Ligne « ' + this.lignesJustes[t].trim() + ' » en position ' + (p2 + 1) + ' sur ' + this.ordre.length + '.';
  };
  Question.prototype.verifier_ordre = function () {
    var ok = this.estDansOrdre(this.ordre), q = this;
    this.conclure(ok, null);
    if (!ok) {
      var bien = this.ordre.filter(function (k, i) { return q.lignesJustes[k] === q.lignesJustes[i]; }).length;
      this.retour.appendChild(el('p', { text: bien + ' ligne(s) sur ' + this.ordre.length + ' déjà à leur place. Demande-toi : que faut-il préparer avant la boucle ? que doit-elle répéter ? que faire après ?' }));
    }
  };
  Question.prototype.attenduTexte_ordre = function () { return '<br><code>' + this.lignesJustes.map(esc).join('<br>') + '</code>'; };

  /* trouve l'erreur : choisir la ligne, puis écrire la ligne corrigée */
  Question.prototype.monter_erreur = function () {
    var q = this, pre = this.s.querySelector('pre.td-code-pret');
    var source = pre.getAttribute('data-source').split('\n'), nom = nouvelId('ligne');
    this.ligneJuste = +this.s.getAttribute('data-ligne');
    this.repLigne = this.s.getAttribute('data-reponse');
    var fs = el('fieldset', { class: 'td-choix td-choix-lignes' }, [el('legend', { text: 'Quelle ligne faut-il corriger ?' })]);
    var choix = el('div', { class: 'td-lignes-choix' });
    this.radios = source.map(function (_, i) {
      var idr = nom + '-' + i, r = el('input', { type: 'radio', name: nom, id: idr, value: String(i + 1) });
      r.checked = q.etat.ligne === i + 1;
      r.addEventListener('change', function () { q.etat.ligne = i + 1; q.enregistrer(); });
      choix.appendChild(el('span', { class: 'td-ligne-radio' }, [r, el('label', { for: idr, text: 'ligne ' + (i + 1) })]));
      return r;
    });
    fs.appendChild(choix);
    this.zone.appendChild(fs);
    if (this.repLigne) {
      var id = nouvelId('corr');
      this.champ = el('input', { type: 'text', id: id, class: 'td-champ td-mono', autocomplete: 'off', spellcheck: 'false', autocapitalize: 'off' });
      this.champ.value = this.etat.valeur || '';
      this.champ.addEventListener('input', function () { q.etat.valeur = q.champ.value; q.enregistrer(); });
      this.champ.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); q.verifier(); } });
      this.zone.appendChild(el('div', { class: 'td-ligne-champ' }, [el('label', { for: id, text: 'Écris cette ligne corrigée :' }), this.champ]));
    }
    if (this.s.getAttribute('data-cote') === 'oui') this.mettreDeCote();     // « trouve l'erreur » : sur demande seulement (T123c)
  };
  Question.prototype.verifier_erreur = function () {
    var choisie = this.radios.filter(function (r) { return r.checked; })[0];
    if (!choisie) return this.dire('Choisis d\'abord la ligne à corriger.', 'info');
    var bonneLigne = +choisie.value === this.ligneJuste;
    var bonneCorr = !this.repLigne || unParmi(this.champ.value, alternatives(this.repLigne), 'code');
    this.conclure(bonneLigne && bonneCorr, null);
    if (!bonneLigne) this.retour.appendChild(el('p', { html: 'Ce n\'est pas cette ligne. Le message de Python donne un indice : cherche <code>line …</code>, puis le type d\'erreur sur la dernière ligne.' }));
    else if (!bonneCorr) this.retour.appendChild(el('p', { text: this.champ.value.trim() ? 'C\'est bien la bonne ligne ! Ta correction n\'est pas encore juste : relis le message d\'erreur.' : 'C\'est bien la bonne ligne ! Écris maintenant la ligne corrigée.' }));
  };
  Question.prototype.attenduTexte_erreur = function () { return 'ligne ' + this.ligneJuste + (this.repLigne ? ' : <code>' + esc(alternatives(this.repLigne)[0]) + '</code>' : ''); };

  /* écrire et lancer du code (Python à la demande) */
  Question.prototype.monter_code = function () {
    var q = this, s = this.s, dep = s.querySelector('.td-depart'), tests = s.querySelector('script.td-tests');
    var depart = dep ? dep.textContent.replace(/^\n/, '') : '';
    if (dep) dep.parentNode.removeChild(dep);
    // un ou plusieurs essais : chaque pre.td-attendu peut porter ses data-entrees (une ligne par input()) et sa data-graine
    var attr = function (e, n) { return e && e.hasAttribute(n) ? e.getAttribute(n) : (s.hasAttribute(n) ? s.getAttribute(n) : null); };
    var atts = Array.prototype.slice.call(s.querySelectorAll('pre.td-attendu'));
    this.essais = (atts.length ? atts : [null]).map(function (a) {
      return { attendu: a ? a.textContent.replace(/^\n/, '').replace(/\s+$/, '') : null, entrees: attr(a, 'data-entrees'), graine: attr(a, 'data-graine') };
    });
    atts.forEach(function (a) { a.parentNode.removeChild(a); });
    this.attendu = this.essais[0].attendu;
    // préambule : du Python exécuté avant le programme (le robot, des données…), sur la question ou pour toute la page
    var pre = s.querySelector('script.td-preambule') || (s.closest('[data-td]') || document).querySelector('script.td-preambule:not(.td-q script)');
    this.preambule = pre ? pre.textContent : '';
    this.tests = tests ? tests.textContent : '';
    this.fichier = this.s.getAttribute('data-fichier') || 'mon_code.py';
    // sur papier, le code de départ (le squelette à compléter) est imprimé en haut du cadre à remplir, en code de
    // 10 pt (T123c), sauf s'il est déjà affiché dans la question ; dessous, les lignes d'écriture de 7 mm. data-lignes
    // donne alors la hauteur de tout le cadre (en lignes de 7 mm, squelette compris), avec 2 lignes d'écriture au
    // moins ; sans data-lignes : le squelette et 3 lignes d'écriture.
    var lignesDepart = 0;
    if (depart.trim()) {
      var dejaVu = Array.prototype.some.call(s.querySelectorAll('pre.td-code'), function (p) {
        return !p.closest('.td-correction') && (p.getAttribute('data-source') || p.textContent).trim() === depart.trim();
      });
      if (!dejaVu) {
        var coupe = couperLongues(depart.replace(/\s+$/, ''), LARGEUR_PAPIER);
        var imp = el('pre', { class: 'td-code td-depart-papier td-papier-seul', 'aria-hidden': 'true', text: coupe.texte });
        this.zone.appendChild(imp);
        afficherCode(imp, { suites: coupe.suites });
        lignesDepart = imp.querySelectorAll('.td-l').length;
      }
    }
    var box = el('div', { class: 'td-ed-boite' });
    this.zone.appendChild(box);
    this.ed = new Editeur(box, this.etat.valeur !== undefined ? this.etat.valeur : depart, 'Ton programme Python, question ' + this.rang, function (v) { q.etat.valeur = v; q.enregistrer(); });
    if (lignesDepart) {
      // une ligne de code imprimée (10 pt × 1,32) vaut 0,665 ligne d'écriture (7 mm)
      var reste = s.hasAttribute('data-lignes') ? Math.max(2, +s.getAttribute('data-lignes') - lignesDepart * 0.665) : 3;
      this.ed.racine.style.setProperty('--td-lignes-papier', String(Math.round(reste * 100) / 100));
    } else if (s.hasAttribute('data-lignes')) this.ed.racine.style.setProperty('--td-lignes-papier', String(+s.getAttribute('data-lignes')));
    this.depart = depart;
    var barre = el('div', { class: 'td-actions' });
    this.bLancer = el('button', { type: 'button', class: 'td-bouton td-principal', text: 'Lancer et vérifier' });
    this.bLancer.addEventListener('click', function () { q.lancer(); });
    var bRaz = el('button', { type: 'button', class: 'td-bouton', text: 'Repartir du code de départ' });
    bRaz.addEventListener('click', function () { q.ed.valeur(q.depart); q.etat.valeur = q.depart; q.enregistrer(); q.ed.ta.focus(); });
    barre.appendChild(this.bLancer); barre.appendChild(bRaz);
    this.zone.appendChild(barre);
    var saisies = this.essais.filter(function (e) { return e.entrees !== null; });
    if (saisies.length) this.zone.appendChild(el('p', { class: 'td-indic', text: 'Les saisies (input) sont fournies par la page, une ligne par input() : ' + saisies.map(function (e) { return e.entrees.split('\n').join(', '); }).join(' ; puis ') + '.' }));
    this.zone.appendChild(el('p', { class: 'td-indic td-py-note', text: 'Python se charge au premier lancement (une seule fois, environ 10 Mo). Sans connexion, compare ton programme avec la correction.' }));
  };
  Question.prototype.lancer = function () {
    var q = this, code = this.ed.valeur();
    if (!code.trim()) return this.dire('Écris ton programme, puis lance-le.', 'info');
    var premier = !python.charge;
    this.bLancer.disabled = true;
    this.dire(premier ? 'Python se charge… (la première fois, cela peut prendre quelques secondes)' : 'Ton programme tourne…', 'info');
    var lent = premier ? setTimeout(function () { q.dire('Python se charge encore : la connexion est lente. Patiente un peu…', 'info'); }, 15000) : null;
    var essais = this.essais, k = 0, ex = this.s.getAttribute('data-espaces') === 'exact';
    function suivant() {
      var e = essais[k];
      return lancerPython(q.f.pyodide, code, q.tests, q.fichier, premier && k === 0, { pre: q.preambule, entrees: e.entrees, graine: e.graine }).then(function (r) {
        r.essai = e;
        r.ok = r.etat === 'ok' && (e.attendu === null || normSortie(r.sortie, ex) === normSortie(e.attendu, ex));
        if (r.ok && ++k < essais.length) return suivant();
        return r;
      });
    }
    suivant().then(function (r) {
      clearTimeout(lent);
      q.bLancer.disabled = false;
      if (r.etat === 'indisponible') {
        if (window.console) console.warn('TD en ligne : Python indisponible.', r.detail || '');
        q.dire('Python n\'a pas pu se charger (pas de connexion, ou connexion trop lente). Tu peux comparer ton programme avec la correction.', 'info');
        q.etat.essais = Math.max(q.etat.essais, ESSAIS_AVANT_CORRECTION); q.majBoutons(); q.enregistrer();
        return;
      }
      if (r.etat !== 'trop-long') python.charge = true;
      if (r.etat === 'trop-long') {
        q.conclure(false, null);
        q.retour.appendChild(el('p', { html: 'Ton programme tourne encore après ' + DELAI_PYTHON / 1000 + ' secondes : c\'est sans doute une <b>boucle infinie</b>. Vérifie que la condition du <code>while</code> finit par devenir fausse.' }));
        return;
      }
      var ok = r.ok, att = r.essai.attendu;
      q.ed.rendre(r.etat === 'erreur' ? ligneErreur(r.detail) : null);
      q.conclure(ok, null);
      if (essais.length > 1 || r.essai.entrees !== null) q.retour.appendChild(el('p', { text: (essais.length > 1 ? 'Essai ' + (k + 1) + ' sur ' + essais.length : 'Essai') + (r.essai.entrees !== null ? ', avec les saisies : ' + r.essai.entrees.split('\n').join(' ; ') : '') }));
      var vue = r.vue !== undefined ? r.vue : r.sortie;      // ce qui s'affiche : invites et saisies comprises
      if (vue && vue.trim()) { q.retour.appendChild(el('p', { class: 'td-etiquette-console', text: 'ta sortie' })); q.retour.appendChild(console_(vue)); }
      // « n'affiche rien » : seulement si c'est la cause probable (pas après un programme juste vérifié par des tests)
      else if (r.etat === 'ok' && (!ok || (!q.tests.trim() && att === null))) q.retour.appendChild(el('p', { text: 'Ton programme n\'affiche rien. As-tu utilisé print ?' }));
      if (r.etat === 'erreur') blocErreur(r.detail, q.retour);
      else if (r.etat === 'test') q.retour.appendChild(el('p', { text: r.detail || 'Un test ne passe pas.' }));
      else if (!ok && att !== null) {
        q.retour.appendChild(el('p', { class: 'td-etiquette-console', text: 'sortie attendue' }));
        q.retour.appendChild(console_(att, 'td-console-attendu'));
      }
    });
  };
  Question.prototype.attenduTexte_code = function () { return 'voir la correction'; };

  Question.prototype.verifier = function () { this['verifier_' + this.type].call(this); };
  ['qcu', 'cases'].forEach(function (t) { Question.prototype['attenduTexte_' + t] = Question.prototype.attenduTexte_options; });
  var attenduBase = Question.prototype.attenduTexte;
  Question.prototype.attenduTexte = function () { var f = this['attenduTexte_' + this.type]; return f ? f.call(this) : attenduBase.call(this); };

  /* ── La feuille ────────────────────────────── */

  function Feuille(racine) {
    this.r = racine;
    this.id = racine.getAttribute('data-td') || location.pathname;
    this.version = racine.getAttribute('data-td-version') || '1';
    this.cle = PREFIXE + this.id;
    this.pyodide = racine.getAttribute('data-pyodide') || window.TD_PYODIDE || PYODIDE;
    this.memoire = stock.lire(this.cle);
    if (!this.memoire || this.memoire.version !== this.version) this.memoire = { cree: 0, version: this.version, q: {}, validee: false };
  }
  Feuille.prototype.sauver = function () {
    if (!this.memoire.cree) this.memoire.cree = Date.now();
    stock.ecrire(this.cle, this.memoire);
    this.majExpiration();
  };
  Feuille.prototype.monter = function () {
    var f = this;
    this.r.classList.add('td-pret');
    // titre long : réduction mesurée (26 caractères tiennent à la taille normale, 31 à la taille réduite)
    var h1 = this.r.querySelector('.td-bandeau h1');
    if (h1) { var lg = h1.textContent.replace(/\s+/g, ' ').trim().length; if (lg > 31) h1.classList.add('td-titre-tres-long'); else if (lg > 26) h1.classList.add('td-titre-long'); }
    // numérotation (T123c) : une suite de numéros pour l'écran, une pour le papier. Une question data-support="ecran"
    // ne compte que sur l'écran, une data-support="papier" que sur le papier : les deux variantes d'une question qui
    // se suivent portent le même numéro, et aucun support ne saute de numéro (5 questions à l'écran pour un tableau
    // sur papier : 5 numéros à l'écran, 1 sur papier). Feuille 2, 3… d'un TD : data-premiere-question sur <main>
    // (et data-premiere-question-papier s'il diffère), posés par charte/numeroter-feuilles.py.
    var depart = parseInt(this.r.getAttribute('data-premiere-question'), 10) || 1;
    var departP = parseInt(this.r.getAttribute('data-premiere-question-papier'), 10) || depart;
    var ne = depart - 1, np = departP - 1;
    this.questions = Array.prototype.slice.call(this.r.querySelectorAll('.td-q[data-type]')).map(function (s, i) {
      var sup = s.getAttribute('data-support') || '';
      var e = sup !== 'papier' ? ++ne : null, p = sup !== 'ecran' ? ++np : null;
      var q = new Question(f, s, e !== null ? e : p, i + 1);
      q.numPapier = p;
      return q;
    });
    this.auteurs();
    this.questions.forEach(function (q) {
      try { q.monter(); } catch (e) { q.s.classList.add('td-q-cassee'); if (window.console) console.error('Question ' + q.id + ' :', e); }
    });
    this.questions.forEach(function (q) { if (q.courteSimple()) q.s.classList.add('td-courte-ligne'); });
    this.tableauxARemplir();
    // le code affiché hors des questions (mémo, exemples)
    this.r.querySelectorAll('pre.td-code:not(.td-code-pret)').forEach(function (p) { afficherCode(p); });
    this.r.querySelectorAll('pre.td-erreur:not(.td-code-pret)').forEach(function (p) { p.parentNode.replaceChild(blocErreur(p.textContent.replace(/^\n/, '')), p); });
    this.r.querySelectorAll('pre.td-sortie-exemple').forEach(function (p) { p.parentNode.replaceChild(console_(p.textContent.replace(/^\n/, '')), p); });
    this.monterBarre();
    this.maj(false);
    this.ajusterCodes();
  };
  // à l'écran, un code qui ne dépasse que de quelques pixels (8 % au plus) est un peu réduit au lieu de défiler
  // (T123c) ; un code bien plus large garde son défilement (téléphone). Le papier a ses propres tailles.
  Feuille.prototype.ajusterCodes = function () {
    var r = this.r, minuterie = null;
    function ajuster() {
      r.querySelectorAll('pre.td-code').forEach(function (p) {
        p.classList.remove('td-ajuste'); p.style.removeProperty('--td-reduc');
        if (!p.getClientRects().length) return;
        var w = p.clientWidth, sw = p.scrollWidth;
        if (sw > w + 0.5 && sw - w <= 0.08 * w) {
          p.style.setProperty('--td-reduc', String(Math.floor((w - 2) / sw * 1000) / 1000));
          p.classList.add('td-ajuste');
        }
      });
    }
    var f = this;
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(ajuster);
    window.addEventListener('resize', function () { clearTimeout(minuterie); minuterie = setTimeout(ajuster, 150); });
  };
  // tableau à remplir (T123c) : data-case-largeur (mm) et data-case-hauteur (lignes d'écriture) sur <table>,
  // data-case-largeur sur un <th> pour sa colonne ; les cellules vides deviennent des cases à remplir
  Feuille.prototype.tableauxARemplir = function () {
    this.r.querySelectorAll('table[data-case-largeur], table[data-case-hauteur], table[data-pleine-largeur]').forEach(function (t) {
      var l = parseFloat(t.getAttribute('data-case-largeur')), h = parseFloat(t.getAttribute('data-case-hauteur'));
      if (l > 0) t.style.setProperty('--td-case-l', l + 'mm');
      if (h > 0) t.style.setProperty('--td-case-h', String(h));
      t.classList.add('td-a-remplir');
      t.querySelectorAll('td').forEach(function (c) { if (!c.textContent.trim() && !c.children.length) c.classList.add('td-vide'); });
      t.querySelectorAll('th[data-case-largeur]').forEach(function (c) {
        var x = parseFloat(c.getAttribute('data-case-largeur'));
        if (x > 0) { c.style.width = x + 'mm'; c.style.minWidth = x + 'mm'; }
      });
    });
  };
  // data-auteurs sur <main> : tous les noms dans le pied de chaque page imprimée (décision du 21/11)
  var AUTEUR_DEFAUT = 'Babash - NSI Tani Malandi';
  Feuille.prototype.auteurs = function () {
    var a = this.r.getAttribute('data-auteurs'), noms = (a || AUTEUR_DEFAUT).replace(/\s+/g, ' ').trim();
    // le pied de la page (dans le flux) redit les mêmes noms : sur papier, il est réduit à son trait (T123c)
    var pied = this.r.querySelector('.td-pied');
    if (pied) {
      var tete = (pied.textContent || '').replace(/\s+/g, ' ').trim().split(' · ')[0];
      var memes = function (x) { return x.replace(/\s*(;|,| et )\s*/g, '|').toLowerCase(); };     // « ; » ou « et » : mêmes noms
      if (memes(tete) === memes(noms)) pied.classList.add('td-pied-redondant');
      // sur papier, une ligne en fin de feuille : « Code source sur GitHub : » et l'adresse lisible (T123c)
      var lien = Array.prototype.filter.call(pied.querySelectorAll('a[href*="github.com"]'), function (a) { return /code source/i.test(a.textContent); })[0];
      if (lien && !pied.querySelector('.td-source-papier')) {
        var adresse = lien.getAttribute('href').replace(/^https?:\/\//, '').replace(/\/$/, '');
        pied.insertBefore(el('p', { class: 'td-source-papier td-papier-seul', 'aria-hidden': 'true' }, [el('span', { text: 'Code source sur GitHub : ' }), el('span', { class: 'td-adresse', text: adresse })]), pied.querySelector('.td-margouillat'));
        lien.classList.add('td-lien-source');
      }
    }
    if (!a || document.getElementById('td-pied-auteurs')) return;
    var txt = noms.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
    var st = document.createElement('style');
    st.id = 'td-pied-auteurs';
    // un pied long tient sur une ligne : police du texte (plus étroite que la police du code), séparateurs simples (T123c)
    var long = noms.length > 46;
    var sep = long ? ' · ' : '  ·  ';
    st.textContent = '@page { @bottom-center { content: "' + txt + sep + 'CC BY-SA 4.0' + sep + 'conçu avec l\'aide de l\'IA' + sep + '" counter(page) " / " counter(pages);' +
      (long ? ' font-family: "Atkinson Hyperlegible", "TD Symboles", sans-serif;' : '') + ' } }';
    document.head.appendChild(st);
  };
  Feuille.prototype.monterBarre = function () {
    var f = this;
    var requises = this.questions.filter(function (q) { return q.compte && !q.bonus; }).length;
    this.jauge = el('div', { class: 'td-jauge', role: 'progressbar', 'aria-valuemin': '0', 'aria-valuemax': String(requises), 'aria-label': 'Avancement de la feuille' }, [el('span', { class: 'td-jauge-plein' })]);
    this.texteJauge = el('p', { class: 'td-jauge-texte' });
    this.validee = el('p', { class: 'td-validee', role: 'status', 'aria-live': 'polite' });
    this.expire = el('p', { class: 'td-expire' });
    var confirmer = el('span', { class: 'td-confirmer', hidden: true }, [
      el('span', { text: 'Effacer tes réponses à cette feuille, sur cet appareil ? ' }),
      el('button', { type: 'button', class: 'td-bouton td-petit', text: 'Oui, effacer', onclick: function () { f.effacer(); } }),
      el('button', { type: 'button', class: 'td-bouton td-petit', text: 'Annuler', onclick: function () { confirmer.hidden = true; bEff.hidden = false; bEff.focus(); } })
    ]);
    var bEff = el('button', { type: 'button', class: 'td-bouton td-petit', text: 'Effacer mes réponses', onclick: function () { bEff.hidden = true; confirmer.hidden = false; confirmer.querySelector('button').focus(); } });
    var bTheme = el('button', { type: 'button', class: 'td-bouton td-petit td-theme', onclick: function () { f.basculerTheme(bTheme); } });
    this.majTheme(bTheme);
    var bImp = el('button', { type: 'button', class: 'td-bouton td-petit', text: 'Imprimer la feuille', onclick: function () { window.print(); } });   // beforeprint vide la feuille
    // la barre collée en haut ne garde que la jauge (une ligne) ; les outils restent dans la page
    var barre = el('div', { class: 'td-barre', role: 'region', 'aria-label': 'Avancement' }, [
      el('div', { class: 'td-barre-jauge' }, [this.texteJauge, this.jauge])
    ]);
    var outils = el('div', { class: 'td-barre-outils' }, [bTheme, bImp, bEff, confirmer]);
    var entete = this.r.querySelector('.td-entete');
    var apres = entete ? entete.nextSibling : this.r.firstChild;
    this.r.insertBefore(outils, apres); this.r.insertBefore(barre, outils);
    this.barre = barre;
    this.garderFocusVisible();
    var fin = el('div', { class: 'td-fin' }, [this.validee, el('p', { class: 'td-vie-privee', text: 'Rien n\'est envoyé : tout se corrige sur cet appareil. Tes réponses servent 24 heures, sur cet appareil seulement. Ensuite, elles sont effacées : à cette heure-là si la page est encore ouverte, sinon à la prochaine ouverture d\'un TD en ligne sur cet appareil.' }), this.expire]);
    var pied = this.r.querySelector('.td-pied');
    this.r.insertBefore(fin, pied || null);
  };
  Feuille.prototype.maj = function (annoncer) {
    var req = this.questions.filter(function (q) { return q.compte && !q.bonus; });
    var faites = req.filter(function (q) { return q.juste; }).length;
    var bonus = this.questions.filter(function (q) { return q.compte && q.bonus; });
    var bf = bonus.filter(function (q) { return q.juste; }).length;
    var pc = req.length ? Math.round(100 * faites / req.length) : 100;
    this.jauge.firstChild.style.width = pc + '%';
    this.jauge.setAttribute('aria-valuenow', String(faites));
    var txt = faites + ' question' + (faites > 1 ? 's' : '') + ' réussie' + (faites > 1 ? 's' : '') + ' sur ' + req.length;
    if (bonus.length) txt += ' · bonus : ' + bf + ' sur ' + bonus.length;
    this.texteJauge.textContent = 'Avancement : ' + faites + ' sur ' + req.length + (bonus.length ? ' · bonus ' + bf + ' sur ' + bonus.length : '');
    // une feuille sans question corrigée en ligne (réponses rédigées, papier) n'est jamais « validée » d'office (T123c)
    if (!req.length) {
      txt = 'Aucune question corrigée en ligne sur cette feuille' + (bonus.length ? ' · bonus : ' + bf + ' sur ' + bonus.length : '');
      this.texteJauge.textContent = txt;
      this.jauge.firstChild.style.width = '0%';
    }
    this.texteJauge.title = txt;
    this.jauge.setAttribute('aria-valuetext', txt);
    var toutes = req.length > 0 && faites === req.length;
    this.r.classList.toggle('td-feuille-validee', toutes);
    this.validee.textContent = toutes ? '✓ Feuille validée : tu as réussi toutes les questions. Tu peux être fier·e de ce que tu as appris !' : '';
    if (toutes && !this.memoire.validee) {
      this.memoire.validee = true; if (this.memoire.cree) this.sauver();
      if (annoncer) {
        // point d'accroche pour le compte commun : l'identifiant de la feuille, jamais les réponses
        document.dispatchEvent(new CustomEvent('td:feuille-validee', { detail: { feuille: this.id, version: this.version } }));
      }
    } else if (!toutes && this.memoire.validee) { this.memoire.validee = false; this.sauver(); }
    this.majExpiration();
  };
  Feuille.prototype.majExpiration = function () {
    if (!this.expire) return;
    if (!this.memoire.cree) { this.expire.textContent = ''; return; }
    var d = new Date(this.memoire.cree + DUREE);
    this.expire.textContent = 'Gardées jusqu\'au ' + d.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }) + ' à ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) + ' ; ensuite, elles sont effacées (aussitôt si la page est ouverte, sinon à la prochaine ouverture d\'un TD en ligne).';
    this.programmerEffacement();
  };
  // impression : la feuille vierge. Les réponses sont vraiment retirées de la page
  // (elles ne sont pas dans le PDF), puis remises après l'impression, sans toucher au stockage.
  Feuille.prototype.viderPourImpression = function () {
    if (this.sauvegarde) return;
    var s = this.sauvegarde = { champs: [], editeurs: [] };
    this.r.querySelectorAll('input, textarea').forEach(function (c) {
      if (c.classList.contains('td-ed-texte')) return;
      s.champs.push([c, c.value, c.checked]);
      if (c.type === 'radio' || c.type === 'checkbox') c.checked = false; else c.value = '';
    });
    this.questions.forEach(function (q) { if (q.ed) { s.editeurs.push([q.ed, q.ed.valeur()]); q.ed.valeur(''); } });
    // un état qui n'est pas un champ : l'ordre des lignes reprend l'ordre mélangé de départ
    s.ordres = [];
    this.questions.forEach(function (q) {
      if (q.ordreDepart) { s.ordres.push([q, q.ordre]); q.ordre = q.ordreDepart.slice(); q.dessinerOrdre(); }
    });
  };
  Feuille.prototype.restaurerApresImpression = function () {
    var s = this.sauvegarde; if (!s) return;
    s.champs.forEach(function (x) { if (x[0].type === 'radio' || x[0].type === 'checkbox') x[0].checked = x[2]; else x[0].value = x[1]; });
    s.editeurs.forEach(function (x) { x[0].valeur(x[1]); });
    s.ordres.forEach(function (x) { x[0].ordre = x[1]; x[0].dessinerOrdre(); });
    this.sauvegarde = null;
  };
  // échéance atteinte, page ouverte : on efface vraiment (et on recharge la feuille vide)
  Feuille.prototype.programmerEffacement = function () {
    var f = this;
    clearTimeout(this.minuteur);
    if (!this.memoire.cree) return;
    var reste = this.memoire.cree + DUREE - Date.now();
    this.minuteur = setTimeout(function () { f.echeance(); }, Math.max(0, Math.min(reste, 2147483000)));
    if (!this.surVisible) {
      this.surVisible = function () { if (!document.hidden) f.echeance(); };
      document.addEventListener('visibilitychange', this.surVisible);    // minuteurs ralentis en arrière-plan
      setInterval(function () { f.echeance(); }, 60000);                // et après une mise en veille : l'heure est vérifiée chaque minute
    }
  };
  Feuille.prototype.echeance = function () {
    if (!this.memoire.cree) return;
    if (Date.now() - this.memoire.cree < DUREE) { this.programmerEffacement(); return; }
    stock.effacer(this.cle);
    location.reload();
  };
  // la barre collée en haut ne doit jamais cacher l'élément qui a le focus (WCAG 2.4.11)
  Feuille.prototype.garderFocusVisible = function () {
    var barre = this.barre, html = document.documentElement;
    function hauteur() { return barre.getBoundingClientRect().height; }
    function regler() { html.style.scrollPaddingTop = Math.ceil(hauteur() + 8) + 'px'; }
    regler();
    if (window.ResizeObserver) new ResizeObserver(regler).observe(barre); else window.addEventListener('resize', regler);
    document.addEventListener('focusin', function (e) {
      var t = e.target; if (!t || barre.contains(t) || !t.getBoundingClientRect) return;
      var r = t.getBoundingClientRect(), bas = barre.getBoundingClientRect().bottom;
      if (getComputedStyle(barre).position === 'sticky' && r.top < bas + 4 && r.bottom > 0) window.scrollBy(0, r.top - bas - 8);
    });
  };
  Feuille.prototype.effacer = function () {
    stock.effacer(this.cle);
    location.reload();
  };
  Feuille.prototype.majTheme = function (b) {
    var t = document.documentElement.getAttribute('data-theme');
    var obscur = t ? t === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    b.textContent = 'Affichage obscur';            // libellé fixe ; l'état est dans aria-pressed (WCAG 2.5.3)
    b.setAttribute('aria-pressed', String(obscur));
  };
  Feuille.prototype.basculerTheme = function (b) {
    var obscur = b.getAttribute('aria-pressed') === 'true';
    var m = obscur ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', m);
    try { localStorage.setItem('theme', m); } catch (e) { }     // même réglage que le site
    this.majTheme(b);
  };

  /* ── Démarrage ─────────────────────────────── */

  function appliquerTheme() {
    try {
      var t = localStorage.getItem('theme');
      if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
    } catch (e) { }
  }
  appliquerTheme();
  function demarrer() {
    stock.purger();
    var feuilles = [];
    document.querySelectorAll('[data-td]').forEach(function (r) { var f = new Feuille(r); f.monter(); r.tdFeuille = f; feuilles.push(f); });
    window.addEventListener('beforeprint', function () { feuilles.forEach(function (f) { f.viderPourImpression(); }); });
    window.addEventListener('afterprint', function () { feuilles.forEach(function (f) { f.restaurerApresImpression(); }); });
  }
  window.TDenLigne = { version: VERSION, colorer: colorer, expliquerErreur: expliquerErreur, egal: egal, normSortie: normSortie, decouperTrous: decouperTrous };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', demarrer); else demarrer();
})();
