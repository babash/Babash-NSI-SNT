/* Alien Python : exécuter le programme de l'élève avec Python (T145).

   - Python 3.13 (Pyodide 0.29.3, la version des TD en ligne du site), chargé à la demande
     dans un Worker (on peut l'arrêter), depuis jsDelivr comme les TD ; rien n'est envoyé.
   - L'alien suit le programme : chaque haut(), bas(), gauche(), droite() est noté avec
     la ligne qui l'a demandé ; colonne() et ligne() donnent sa position.
   - Le message d'erreur est celui de Python, tel quel (seules les lignes du programme de
     l'élève sont gardées dans la trace) ; « Explique-moi cette erreur » le dit en français.
   - Une boucle qui ne s'arrête pas est arrêtée au bout de 20 000 lignes exécutées
     (ou de 5 000 déplacements, ou de 8 secondes), avec un message.
   - Le programme de l'élève ne peut importer ni js, ni pyodide, ni ce qui y mène (sys, gc,
     importlib…), et un message qu'il enverrait n'est pas pris pour un résultat (le secret du
     Worker) : il ne peut pas se déclarer juste lui-même (le README dit ce qui reste ouvert).
   - Un programme juste écrit autrement est accepté : on compare le trajet de l'alien
     case par case, pas le texte.

   Babash - NSI Tani Malandi · code sous licence MIT */
(function (racine) {
  'use strict';

  var PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js';   // Python 3.13, comme assets/td-en-ligne.js
  var DELAI = 8000;            // au-delà, le Worker est arrêté (filet de sécurité : Python s'arrête de lui-même avant)
  var DELAI_CHARGEMENT = 240000;
  var NOM = 'mon_programme.py';

  /* ── Le lanceur, côté Python ── */
  var PY = [
    'import sys, traceback, linecache',
    'class AlienHorsGrille(Exception):',
    '    pass',
    'class ProgrammeTropLong(Exception):',
    '    pass',
    // les modules que le programme de l'élève ne peut pas importer (T145, Gardien 42) : ceux qui mènent à JavaScript
    // (js, pyodide…) et ceux qui permettent d'aller les chercher (sys, gc, importlib, inspect, ctypes…)
    '_ALIEN_BLOQUES = {"js", "pyodide", "pyodide_js", "_pyodide", "_pyodide_core", "micropip", "sys", "gc", "importlib",',
    '                  "_imp", "_frozen_importlib", "_frozen_importlib_external", "builtins", "inspect", "ctypes", "_ctypes",',
    '                  "os", "posix", "subprocess", "types", "code", "codeop", "runpy", "pickle", "marshal", "__main__"}',
    'import builtins as _alien_b',
    'def _alien_garde(name, globals=None, locals=None, fromlist=(), level=0):',
    '    if level == 0 and str(name).split(".")[0] in _ALIEN_BLOQUES:',
    '        raise ImportError("module \'%s\' is not available in Alien Python" % name, name=name)',
    '    return _alien_b.__import__(name, globals, locals, fromlist, level)',
    '_ALIEN_BUILTINS = dict(vars(_alien_b), __import__=_alien_garde)',
    // pendant l’exécution, ces modules sont aussi ôtés de sys.modules (gardés côté JavaScript, rendus après)
    'def _alien_cacher():',
    '    return {k: sys.modules.pop(k) for k in list(sys.modules) if k.split(".")[0] in _ALIEN_BLOQUES - {"sys", "builtins", "os", "posix", "types"}}',
    'def _alien_rendre(pris):',
    '    sys.modules.update(pris)',
    'def _alien_lancer(src, nom, x0=8, y0=8, max_lignes=20000, max_pas=5000):',
    '    linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)',
    '    pos = [x0, y0]',
    '    pas = []',
    '    sortie = []',
    '    compte = [0]',
    '    res = {"etat": "ok", "detail": "", "ligne": 0, "hors": None}',
    '    def ligne_appel():',
    '        f = sys._getframe(1)',
    '        while f is not None and f.f_code.co_filename != nom:',
    '            f = f.f_back',
    '        return f.f_lineno if f is not None else 0',
    '    def bouger(dx, dy, n, quoi):',
    '        if not isinstance(n, int):',
    '            raise TypeError("\'%s\' object cannot be interpreted as an integer" % type(n).__name__)',
    '        l = ligne_appel()',
    '        nx, ny = pos[0] + dx * n, pos[1] + dy * n',
    '        if not (1 <= nx <= 15 and 1 <= ny <= 15):',
    '            res["hors"] = [l, quoi, int(n), pos[0], pos[1], nx, ny]',
    '            raise AlienHorsGrille(quoi)',
    '        pos[0], pos[1] = nx, ny',
    '        if n:',
    '            pas.append([l, nx, ny])',
    '        if len(pas) > max_pas:',
    '            raise ProgrammeTropLong(l)',
    '    def haut(n=1):',
    '        bouger(0, -1, n, "haut")',
    '    def bas(n=1):',
    '        bouger(0, 1, n, "bas")',
    '    def gauche(n=1):',
    '        bouger(-1, 0, n, "gauche")',
    '    def droite(n=1):',
    '        bouger(1, 0, n, "droite")',
    '    def colonne():',
    '        return pos[0]',
    '    def ligne():',
    '        return pos[1]',
    '    class Flux:',
    '        encoding = "utf-8"',
    '        def write(self, t):',
    '            sortie.append(str(t))',
    '            return len(t)',
    '        def flush(self):',
    '            pass',
    '        def isatty(self):',
    '            return False',
    '    def suivre(frame, event, arg):',
    '        if frame.f_code.co_filename != nom:',
    '            return None',
    '        if event == "line":',
    '            compte[0] += 1',
    '            if compte[0] > max_lignes:',
    '                raise ProgrammeTropLong(frame.f_lineno)',
    '        return suivre',
    '    def rapport(e):',
    '        te = traceback.TracebackException(type(e), e, e.__traceback__)',
    '        te.stack = traceback.StackSummary.from_list([f for f in te.stack if f.filename == nom])',
    '        return "".join(te.format())',
    '    g = {"__name__": "__main__", "__builtins__": _ALIEN_BUILTINS, "haut": haut, "bas": bas, "gauche": gauche, "droite": droite, "colonne": colonne, "ligne": ligne}',
    '    vrais = (sys.stdout, sys.stderr)',
    '    sys.stdout = sys.stderr = Flux()',
    '    try:',
    '        code = compile(src, nom, "exec")',
    '        sys.settrace(suivre)',
    '        try:',
    '            exec(code, g)',
    '        finally:',
    '            sys.settrace(None)',
    '    except AlienHorsGrille:',
    '        res["etat"] = "hors"',
    '        res["ligne"] = res["hors"][0]',
    '    except ProgrammeTropLong as e:',
    '        res["etat"] = "trop-long"',
    '        res["ligne"] = int(e.args[0]) if e.args else 0',
    '    except SystemExit:',
    '        pass',
    '    except BaseException as e:',
    '        res["etat"] = "erreur"',
    '        res["detail"] = rapport(e)',
    '        if isinstance(e, SyntaxError) and e.filename == nom:',
    '            res["ligne"] = e.lineno or 0',
    '        else:',
    '            t = e.__traceback__',
    '            while t is not None:',
    '                if t.tb_frame.f_code.co_filename == nom:',
    '                    res["ligne"] = t.tb_lineno',
    '                t = t.tb_next',
    '    finally:',
    '        sys.settrace(None)',
    '        sys.stdout, sys.stderr = vrais',
    '    res["pas"] = pas',
    '    res["sortie"] = "".join(sortie)[:4000]',
    '    res["x"], res["y"] = pos[0], pos[1]',
    '    return res'
  ].join('\n');

  /* Le Worker. Son tout premier message, envoyé dès sa création (avant qu'un programme d'élève ait pu tourner), lui
     donne un secret qu'il garde dans sa fermeture et ne renvoie qu'avec ses résultats ; la page ignore tout message
     qui ne le porte pas. Un programme qui atteindrait JavaScript (en remontant les cadres de Python, par exemple)
     peut écouter les messages suivants, mais n'y trouve jamais le secret : il ne peut pas fabriquer un résultat. */
  function sourceWorker(url) {
    return [
      'var envoyer = self.postMessage.bind(self), secret = null;',
      'importScripts(' + JSON.stringify(url) + ');',
      'var py = loadPyodide({ indexURL: ' + JSON.stringify(url.replace(/[^/]*$/, '')) + ' }).then(function (p) {',
      '  p.runPython(' + JSON.stringify(PY) + ');',
      '  p.setStdin({ error: true });',
      '  return p;',
      '});',
      'function executer(d) {',
      '  var id = d.id;',
      '  py.then(function (p) {',
      '    var f = p.globals.get("_alien_lancer"), cacher = p.globals.get("_alien_cacher"), rendre = p.globals.get("_alien_rendre");',
      '    var pris = cacher(), r;',
      '    try { r = f(String(d.code), ' + JSON.stringify(NOM) + '); } finally { rendre(pris); pris.destroy(); cacher.destroy(); rendre.destroy(); f.destroy(); }',
      '    var o = r.toJs({ dict_converter: Object.fromEntries }); r.destroy();',
      '    o.id = id; o.secret = secret; envoyer(o);',
      '  }).catch(function (err) { envoyer({ id: id, secret: secret, etat: "indisponible", detail: String(err) }); });',
      '}',
      // le premier message (le secret) arrive avant tout programme : les messages ne sont lus qu'une fois ce script fini
      'self.onmessage = function (e) { e.stopImmediatePropagation(); if (secret === null) secret = String(e.data && e.data.secret); else executer(e.data); };',
      'Object.defineProperty(self, "onmessage", { writable: false, configurable: false });'
    ].join('\n');
  }

  var python = { worker: null, attente: {}, n: 0, charge: false, enCharge: false };
  function demarrer(url) {
    var blob = new Blob([sourceWorker(url)], { type: 'text/javascript' });
    python.worker = new Worker(URL.createObjectURL(blob));
    python.secret = Array.prototype.map.call(crypto.getRandomValues(new Uint32Array(4)), function (v) { return v.toString(36); }).join('-');
    python.worker.postMessage({ secret: python.secret });
    python.worker.onmessage = function (e) {
      var d = e.data || {}, a = python.attente[d.id];
      if (!a || d.secret !== python.secret) return;      // un message sans le secret du Worker n'est pas un résultat
      delete d.secret; delete python.attente[d.id]; a.f(d);
    };
    python.worker.onerror = function (e) {
      if (e && e.preventDefault) e.preventDefault();
      Object.keys(python.attente).forEach(function (k) { python.attente[k].f({ etat: 'indisponible' }); });
      python.attente = {}; python.worker = null; python.charge = false;
    };
  }
  // lance le programme ; rend toujours une promesse résolue : { etat: ok | erreur | hors | trop-long | indisponible, … }
  function lancer(code) {
    var url = racine.TD_PYODIDE || PYODIDE;
    return new Promise(function (resoudre) {
      try { if (!python.worker) demarrer(url); } catch (e) { resoudre({ etat: 'indisponible', detail: String(e) }); return; }
      var id = ++python.n, premier = !python.charge;
      python.enCharge = premier;
      var limite = setTimeout(function () {
        if (!python.attente[id]) return;
        delete python.attente[id];
        try { python.worker.terminate(); } catch (e) { }
        python.worker = null; python.charge = false; python.enCharge = false;
        resoudre({ etat: premier ? 'indisponible' : 'trop-long', ligne: 0, pas: [], delai: !premier });
      }, premier ? DELAI_CHARGEMENT : DELAI);
      python.attente[id] = { f: function (r) {
        clearTimeout(limite); python.enCharge = false;
        if (r.etat !== 'indisponible') python.charge = true;
        r.pas = r.pas || [];
        resoudre(r);
      } };
      python.worker.postMessage({ id: id, code: String(code) });
    });
  }

  /* ── Le trajet, case par case ── */

  // la suite des cases traversées (une par pas d'une case), depuis (x0, y0), et la ligne qui a fait chaque pas
  function cases(pas, x0, y0) {
    var out = [], lignes = [], x = x0, y = y0;
    pas.forEach(function (p) {
      var tx = p[1], ty = p[2];
      while (x !== tx || y !== ty) {
        if (x !== tx) x += tx > x ? 1 : -1; else y += ty > y ? 1 : -1;
        out.push([x, y]); lignes.push(p[0]);
      }
    });
    return { cases: out, lignes: lignes };
  }
  // le trajet attendu d'un exercice (liste plate x, y, x, y… des arrêts de l'alien)
  function pasAttendus(p) { var out = []; for (var i = 0; i < p.length; i += 2) out.push([0, p[i], p[i + 1]]); return out; }

  /* Les niveaux de décalage, calculés comme CPython (tokenizer.c) : une tabulation compte jusqu'au multiple de 8
     suivant (« col ») et aussi pour 1 (« altcol ») ; si les deux mesures ne disent pas la même chose, Python
     refuse le programme (TabError), et ici aussi. Rend [{t: texte sans les blancs du début, n: niveau}] pour les
     lignes non vides qui ne sont pas un commentaire seul, ou null quand Python refuserait le décalage (retrait sur un niveau jamais ouvert, mélange
     de tabulations et d'espaces ambigu, ligne décalée au tout début). */
  function niveaux(code) {
    var pile = [[0, 0]], out = [], ok = true;
    String(code).split('\n').forEach(function (l) {
      if (!ok || !l.trim() || /^[ \t]*#/.test(l)) return;   // Python ne mesure pas le décalage d'une ligne vide ou d'un commentaire seul
      var col = 0, alt = 0, i = 0;
      for (; i < l.length && (l[i] === ' ' || l[i] === '\t'); i++) {
        if (l[i] === ' ') { col++; alt++; } else { col = (Math.floor(col / 8) + 1) * 8; alt++; }
      }
      var h = pile[pile.length - 1];
      if (col === h[0]) { if (alt !== h[1]) ok = false; }
      else if (col > h[0]) { if (alt <= h[1] || !out.length) ok = false; else pile.push([col, alt]); }
      else {
        while (pile.length > 1 && col < pile[pile.length - 1][0]) pile.pop();
        h = pile[pile.length - 1];
        if (col !== h[0] || alt !== h[1]) ok = false;
      }
      out.push({ t: l.slice(i), n: pile.length - 1 });
    });
    return ok ? out : null;
  }

  /* Les lignes données par l'énoncé (non vides, sans « .. ») doivent rester, dans le même ordre, au même niveau
     de bloc et dans le même bloc (T145, après le Gardien 42). Règle exacte :
       modèle M (lignes non vides, avec leur niveau), programme P (idem) ;
       texte(l) = la ligne sans aucun blanc ;
       parent(l) = la ligne la plus proche AU-DESSUS de l, dans le même texte, de niveau plus petit (ou aucune) ;
       k = 0 ; image = {} ;
       pour chaque ligne m de M, dans l'ordre, si texte(m) ne contient pas « .. » :
         j = le plus petit indice >= k de P tel que
               texte(P[j]) = texte(m)  et  niveau(P[j]) = niveau(m)
               et, si parent(m) existe et est une ligne donnée : parent(P[j]) = image[parent(m)] ;
         si aucun j : m manque ; sinon image[m] = j ; k = j + 1.
     Le programme est accepté si aucune ligne ne manque (et si son trajet est le bon). Si Python refuserait le
     décalage du programme, toutes les lignes données « manquent » (le programme est de toute façon refusé). */
  function parents(L) {
    return L.map(function (l, i) { for (var j = i - 1; j >= 0; j--) if (L[j].n < l.n) return j; return -1; });
  }
  function sansBlancs(s) { return s.replace(/\s+/g, ''); }
  function lignesManquantes(modele, programme) {
    var M = niveaux(modele) || [], P = niveaux(programme), manque = [];
    var donnees = M.map(function (l) { return sansBlancs(l.t).indexOf('..') < 0; });
    if (!P) return M.filter(function (l, i) { return donnees[i]; }).map(function (l) { return sansBlancs(l.t); });
    var pM = parents(M), pP = parents(P), image = {}, k = 0;
    M.forEach(function (m, i) {
      if (!donnees[i]) return;
      var tm = sansBlancs(m.t), pere = pM[i] >= 0 && donnees[pM[i]] ? pM[i] : -1, j;
      for (j = k; j < P.length; j++) {
        if (sansBlancs(P[j].t) !== tm || P[j].n !== m.n) continue;
        if (pere >= 0 && pP[j] !== image[pere]) continue;
        break;
      }
      if (j >= P.length) manque.push(tm); else { image[i] = j; k = j + 1; }
    });
    return manque;
  }

  /* Le programme ramené à sa forme (sans Python) : niveaux de décalage calculés comme CPython, et chaque ligne
     sans les espaces qui touchent un signe, sauf l'espace entre deux signes qui, collés, feraient un autre
     opérateur de Python (« = = » n'est pas « == », mais « ) : » est bien « ): »). Deux programmes de
     même forme font la même chose ; une forme vaut null si Python refuserait le programme (décalage, ou un
     caractère hors ASCII : espace insécable, guillemet typographique…), et null n'est égal à rien. */
  var SIGNES = '():,=<>!+\\-*/%';
  // les couples de signes qui, collés, forment un opérateur de Python (les opérateurs de 3 signes, « **= », « //= »,
  // « <<= », « >>= », sont faits de ces couples) : l'espace entre eux est gardé
  var COLLES = ['==', '!=', '<=', '>=', '**', '//', '->', '+=', '-=', '*=', '/=', '%=', ':=', '<<', '>>'];
  function forme(code) {
    if (/[^\x20-\x7e\t\r\n]/.test(code)) return null;
    var L = niveaux(String(code).replace(/\r/g, ''));
    if (!L) return null;
    var sg = new RegExp('[' + SIGNES + ']');
    return L.map(function (l) {
      var s = l.t.trim().replace(/[ \t]+/g, ' '), o = '';
      for (var i = 0; i < s.length; i++) {        // un espace s'ôte s'il touche un signe, sauf entre deux signes de COLLES
        if (s[i] === ' ') {
          var a = s[i - 1] || '', b = s[i + 1] || '', g = sg.test(a), d = sg.test(b);
          if ((g || d) && !(g && d && COLLES.indexOf(a + b) >= 0)) continue;
        }
        o += s[i];
      }
      return l.n + '|' + o;
    }).join('\n');
  }
  function memeForme(a, b) { var fa = forme(a); return fa !== null && fa === forme(b); }

  var SENS = { '1,0': 'vers la droite', '-1,0': 'vers la gauche', '0,-1': 'vers le haut', '0,1': 'vers le bas' };
  function nomCase(c) { return String.fromCharCode(64 + c[0]) + c[1]; }

  // compare ce qu'a fait le programme au parcours demandé.
  // ex : { p, c (le programme à compléter), s (la solution) } ; r : le résultat de lancer()
  // rend { juste, message (texte), ligne (la ligne du programme en cause, ou 0), remarque }
  function comparer(ex, programme, r) {
    var att = cases(pasAttendus(ex.p), 8, 8).cases, fait = cases(r.pas, 8, 8), f = fait.cases;
    var n = Math.min(att.length, f.length), k = 0;
    while (k < n && att[k][0] === f[k][0] && att[k][1] === f[k][1]) k++;
    var memeTrajet = k === att.length && k === f.length;
    if (memeTrajet && r.etat === 'ok') {
      var manque = ex.c ? lignesManquantes(ex.c, programme) : [];
      if (manque.length) return { juste: false, ligne: 0, message: 'Le trajet est bon, mais une ligne donnée a changé, a disparu ou a changé de bloc : « ' + manque[0] + ' ». Garde les lignes données, avec leur décalage, et remplace seulement les points.' };
      // la remarque n'est dite que si elle est vraie : la correction a une boucle for, le programme n'a aucune boucle,
      // et il a plus de lignes que la correction
      var remarque = '', nl = function (s) { return String(s).split('\n').filter(function (l) { return l.trim(); }).length; };
      if (ex.s && /\bfor\b/.test(ex.s) && !/\b(for|while)\b/.test(programme) && nl(programme) > nl(ex.s)) remarque = 'Ton programme est juste. La correction est plus courte : elle répète le motif avec une boucle for.';
      return { juste: true, ligne: 0, message: '', remarque: remarque };
    }
    var depart = k ? nomCase(f[k - 1]) : 'H8';
    if (r.etat !== 'ok') {          // le programme s'est arrêté (erreur, sortie de la grille, boucle sans fin) : la page dit pourquoi
      return { juste: false, ligne: r.ligne || 0, message: k && k === f.length ? 'Jusque-là, ton alien suivait bien le parcours (jusqu’en ' + depart + ').' : '' };
    }
    if (k === f.length && k < att.length) {
      return { juste: false, ligne: 0, message: f.length ? 'Ton alien suit le parcours jusqu’en ' + depart + ', puis il s’arrête : il manque la fin du trajet.' : 'Ton alien ne bouge pas : il reste en H8.' };
    }
    var ligneFaute = fait.lignes[k] || 0;
    var d = [f[k][0] - (k ? f[k - 1][0] : 8), f[k][1] - (k ? f[k - 1][1] : 8)].join(',');
    if (k === att.length) return { juste: false, ligne: ligneFaute, message: 'Ton alien fait tout le parcours, puis il continue ' + SENS[d] + (ligneFaute ? ' (ligne ' + ligneFaute + ' de ton programme)' : '') + '.' };
    return { juste: false, ligne: ligneFaute, message: 'Ton alien suit le parcours ' + (k ? 'jusqu’en ' + depart : 'depuis H8') + ', puis il s’en écarte : il part ' + SENS[d] + (ligneFaute ? ' (ligne ' + ligneFaute + ' de ton programme)' : '') + '.' };
  }

  /* ── Les erreurs, expliquées en français (les mêmes mots que les TD en ligne, et ceux d'Alien Python) ── */
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  var ERREURS = [
    [/ImportError: module '[^']*' is not available in Alien Python/, 'Ce module n’est pas disponible dans Alien Python : ton programme guide l’alien avec <code>haut()</code>, <code>bas()</code>, <code>gauche()</code> et <code>droite()</code>, et peut utiliser des modules comme <code>math</code>, <code>random</code> ou <code>time</code>.'],
    [/SyntaxError: expected ':'/, 'Il manque les <b>deux-points</b> <code>:</code> à la fin de la ligne. Ils sont obligatoires après <code>for</code>, <code>while</code>, <code>if</code>, <code>else</code> et <code>def</code>.'],
    [/SyntaxError: '(\(|\[|\{)' was never closed/, 'Une <b>parenthèse</b> est ouverte mais jamais fermée : chaque <code>(</code> a besoin de sa <code>)</code>, sur la même ligne.'],
    [/SyntaxError: unmatched '(.)'/, 'Il y a une parenthèse <b>fermante en trop</b>.'],
    [/SyntaxError: invalid syntax\. Maybe you meant '==' or ':=' instead of '='/, 'Pour <b>comparer</b>, on écrit <code>==</code> (ou <code>&lt;</code>, <code>&gt;</code>…). Un seul <code>=</code> sert à donner une valeur à une variable.'],
    [/SyntaxError: cannot assign to/, 'À gauche du signe <code>=</code>, il faut un <b>nom de variable</b>. Pour comparer, on écrit <code>==</code>.'],
    [/SyntaxError: invalid syntax/, 'Python ne comprend pas cette ligne : un mot, un signe ou une parenthèse est mal placé. Regarde l’endroit montré par les <code>^</code>. Une instruction s’écrit avec ses parenthèses, par exemple <code>haut(2)</code>, et les mots de Python en minuscules (<code>for</code>, <code>if</code>, <code>else</code>).'],
    [/IndentationError: expected an indented block/, 'Après une ligne qui finit par <code>:</code>, la ligne suivante doit être <b>décalée</b> (4 espaces, ou la touche Tab) : c’est le bloc qui est répété ou exécuté.'],
    [/IndentationError: unexpected indent/, 'Cette ligne est <b>décalée sans raison</b> : elle ne suit pas une ligne qui finit par <code>:</code>. Retire les espaces du début de la ligne.'],
    [/IndentationError: unindent does not match/, 'Ce décalage ne correspond à <b>aucun bloc</b> au-dessus : aligne la ligne avec le bloc auquel elle appartient (même nombre d’espaces).'],
    [/NameError: name '(\w+)' is not defined\. Did you mean: '(\w+)'/, 'Python ne connaît pas le nom <code>$1</code>. Il te propose <code>$2</code> : sans doute une <b>faute de frappe</b> (Python fait la différence entre majuscules et minuscules).'],
    [/NameError: name '(\w+)' is not defined/, 'Python ne connaît pas le nom <code>$1</code> : la variable n’a pas encore reçu de valeur à ce moment-là, ou son nom est mal écrit. Les instructions de l’alien sont <code>haut</code>, <code>bas</code>, <code>gauche</code> et <code>droite</code>.'],
    [/TypeError: 'ellipsis' object cannot be interpreted as an integer/, 'Une variable vaut encore <code>...</code> (des points) : remplace les points par un <b>nombre</b>.'],
    [/TypeError: '(\w+)' object cannot be interpreted as an integer/, 'Entre les parenthèses, il faut un <b>nombre entier</b> (par exemple <code>3</code>), pas un <code>$1</code>.'],
    [/TypeError: (\w+)\(\) takes from 0 to 1 positional arguments but (\d+) were given/, '<code>$1()</code> prend <b>un seul nombre</b> entre ses parenthèses (le nombre de cases), mais elle en a reçu $2.'],
    [/TypeError: (\w+)\(\) takes 0 positional arguments but (\d+) (were|was) given/, '<code>$1()</code> s’écrit avec des parenthèses <b>vides</b> : elle donne une position, elle ne prend pas de nombre.'],
    [/TypeError: (\w+)\(\) takes (\d+) positional arguments? but (\d+) (were|was) given/, 'La fonction <code>$1</code> attend $2 valeur(s) entre parenthèses, mais elle en a reçu $3.'],
    [/TypeError: (\w+)\(\) missing/, 'Il manque une valeur entre les parenthèses de <code>$1</code>.'],
    [/TypeError: '(\w+)' object is not callable/, 'Des parenthèses suivent un <code>$1</code>, comme si c’était une fonction. Une variable porte peut-être le nom d’une fonction.'],
    [/TypeError: unsupported operand type\(s\) for (\S+): '(\w+)' and '(\w+)'/, 'L’opération <code>$1</code> n’est pas possible entre un <code>$2</code> et un <code>$3</code>.'],
    [/ZeroDivisionError/, 'Une <b>division par zéro</b> : c’est impossible, en Python comme en maths.'],
    [/RecursionError/, 'La fonction s’appelle elle-même <b>sans jamais s’arrêter</b>.']
  ];
  var VOCABULAIRE = [
    ['Traceback (most recent call last)', 'trace des appels (le plus récent en dernier)'],
    ['File "…", line N', 'fichier « … », ligne N : là où Python s’est arrêté'],
    ['^^^^', 'l’endroit précis de l’erreur'],
    ['Did you mean', 'voulais-tu dire'],
    ['is not defined', 'n’est pas défini']
  ];
  function expliquer(texte, programme, ligne) {
    var derniere = String(texte).replace(/\s+$/, '').split('\n').pop();
    var l = ligne ? (String(programme || '').split('\n')[ligne - 1] || '') : '';
    if (/SyntaxError/.test(derniere) && /\.\./.test(l)) return 'La ligne ' + ligne + ' contient encore des <b>points</b> : remplace-les par ce qui manque (un nombre, une instruction, un mot de Python).';
    for (var i = 0; i < ERREURS.length; i++) {
      var m = derniere.match(ERREURS[i][0]);
      if (m) return ERREURS[i][1].replace(/\$(\d)/g, function (_, n) { return esc(m[+n] || ''); });
    }
    return 'Lis la dernière ligne : elle donne le <b>type</b> de l’erreur. La ligne <code>File …, line N</code> dit où Python s’est arrêté.';
  }
  function vocabulaire() { return VOCABULAIRE.map(function (v) { return '<span><code>' + esc(v[0]) + '</code> : ' + esc(v[1]) + '</span>'; }).join(' · '); }
  // le message d'erreur, coloré (gras, souligné : lisible en noir et blanc)
  function colorerErreur(texte) {
    return String(texte).replace(/\s+$/, '').split('\n').map(function (l) {
      var m;
      if (/^Traceback/.test(l)) l = '<span class="er-entete">' + esc(l) + '</span>';
      else if ((m = l.match(/^(\s*File )(".*?")(, line )(\d+)(.*)$/))) l = esc(m[1]) + '<span class="er-fichier">' + esc(m[2]) + '</span>' + esc(m[3]) + '<b class="er-ligne">' + m[4] + '</b>' + esc(m[5]);
      else if (/^\s*[\^~]+\s*$/.test(l)) l = '<b class="er-fleche">' + esc(l) + '</b>';
      else if ((m = l.match(/^(\w*(?:Error|Exception|Warning|Interrupt|Exit))(:?)(.*)$/))) l = '<b class="er-type">' + esc(m[1]) + '</b>' + esc(m[2]) + '<span class="er-msg">' + esc(m[3]) + '</span>';
      else l = esc(l);
      return '<span class="al-l">' + (l || ' ') + '</span>';
    }).join('');
  }

  var api = {
    lancer: lancer, cases: cases, pasAttendus: pasAttendus, comparer: comparer, lignesManquantes: lignesManquantes,
    expliquer: expliquer, forme: forme, memeForme: memeForme, vocabulaire: vocabulaire, colorerErreur: colorerErreur, nomCase: nomCase,
    etat: function () { return { charge: python.charge, enCharge: python.enCharge }; }, PY: PY, NOM: NOM
  };
  racine.AlienPython = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
