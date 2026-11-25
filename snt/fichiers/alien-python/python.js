/* Alien Python : exécuter le programme de l'élève avec Python (T145).

   - Python 3.13 (Pyodide 0.29.3, la version des TD en ligne du site), chargé à la demande
     dans un Worker (on peut l'arrêter), depuis jsDelivr comme les TD ; rien n'est envoyé.
   - L'alien suit le programme : chaque haut(), bas(), gauche(), droite() est noté avec
     la ligne qui l'a demandé ; colonne() et ligne() donnent sa position.
   - Le message d'erreur est celui de Python, tel quel (seules les lignes du programme de
     l'élève sont gardées dans la trace) ; « Explique-moi cette erreur » le dit en français.
   - Une boucle qui ne s'arrête pas est arrêtée au bout de 20 000 lignes exécutées
     (ou de 5 000 déplacements), avec un message.
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
    '    g = {"__name__": "__main__", "haut": haut, "bas": bas, "gauche": gauche, "droite": droite, "colonne": colonne, "ligne": ligne}',
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

  function sourceWorker(url) {
    return [
      'importScripts(' + JSON.stringify(url) + ');',
      'var py = loadPyodide({ indexURL: ' + JSON.stringify(url.replace(/[^/]*$/, '')) + ' }).then(function (p) {',
      '  p.runPython(' + JSON.stringify(PY) + ');',
      '  p.setStdin({ error: true });',
      '  return p;',
      '});',
      'self.onmessage = function (e) {',
      '  var d = e.data;',
      '  py.then(function (p) {',
      '    var f = p.globals.get("_alien_lancer"), r = f(d.code, ' + JSON.stringify(NOM) + ');',
      '    var o = r.toJs({ dict_converter: Object.fromEntries }); r.destroy(); f.destroy();',
      '    o.id = d.id; self.postMessage(o);',
      '  }).catch(function (err) { self.postMessage({ id: d.id, etat: "indisponible", detail: String(err) }); });',
      '};'
    ].join('\n');
  }

  var python = { worker: null, attente: {}, n: 0, charge: false, enCharge: false };
  function demarrer(url) {
    var blob = new Blob([sourceWorker(url)], { type: 'text/javascript' });
    python.worker = new Worker(URL.createObjectURL(blob));
    python.worker.onmessage = function (e) {
      var f = python.attente[e.data.id]; delete python.attente[e.data.id];
      if (f) f(e.data);
    };
    python.worker.onerror = function (e) {
      if (e && e.preventDefault) e.preventDefault();
      Object.keys(python.attente).forEach(function (k) { python.attente[k]({ etat: 'indisponible' }); });
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
        resoudre({ etat: premier ? 'indisponible' : 'trop-long', ligne: 0, pas: [] });
      }, premier ? DELAI_CHARGEMENT : DELAI);
      python.attente[id] = function (r) {
        clearTimeout(limite); python.enCharge = false;
        if (r.etat !== 'indisponible') python.charge = true;
        r.pas = r.pas || [];
        resoudre(r);
      };
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

  // les lignes données par l'énoncé (sans « .. ») doivent rester, dans le même ordre (espaces ignorés)
  function lignesDonnees(modele) {
    return String(modele).split('\n').map(function (l) { return l.replace(/\s+/g, ''); })
      .filter(function (l) { return l && l.indexOf('..') < 0; });
  }
  function lignesManquantes(modele, programme) {
    var donnees = lignesDonnees(modele), lp = String(programme).split('\n').map(function (l) { return l.replace(/\s+/g, ''); });
    var k = 0, manque = [];
    donnees.forEach(function (d) {
      var j = lp.indexOf(d, k);
      if (j < 0) manque.push(d); else k = j + 1;
    });
    return manque;
  }

  // le programme ramené à sa forme (sans Python) : les niveaux de décalage (et non le nombre d'espaces),
  // et chaque ligne sans espaces autour des signes. Deux programmes de même forme font la même chose ;
  // l'ancienne comparaison ôtait tous les blancs, décalages compris, et acceptait un bloc mal décalé.
  function forme(code) {
    var pile = [0], out = [];
    String(code).split('\n').forEach(function (l) {
      if (!l.trim()) return;
      var d = l.match(/^[ \t]*/)[0].replace(/\t/g, '    ').length;
      var haut_ = pile[pile.length - 1], niveau;
      if (d > haut_) { pile.push(d); niveau = pile.length - 1; }
      else if (d === haut_) niveau = pile.length - 1;
      else {                       // on recule : il faut retomber sur un décalage déjà ouvert, sinon Python refuse
        while (pile.length > 1 && d < pile[pile.length - 1]) pile.pop();
        if (d === pile[pile.length - 1]) niveau = pile.length - 1; else { niveau = '!'; pile.push(d); }
      }
      out.push(niveau + '|' + l.trim().replace(/\s*([():,=<>+\-*\/%])\s*/g, '$1').replace(/\s+/g, ' '));
    });
    return out.join('\n');
  }
  function memeForme(a, b) { return forme(a) === forme(b); }

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
      if (manque.length) return { juste: false, ligne: 0, message: 'Le trajet est bon, mais une ligne donnée a changé ou disparu : « ' + manque[0] + ' » (espaces non comptés). Garde les lignes données et remplace seulement les points.' };
      var remarque = '';
      if (ex.s && /\bfor\b/.test(ex.s) && !/\bfor\b/.test(programme)) remarque = 'Ton programme est juste. La correction est plus courte : elle répète le motif avec une boucle for.';
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
