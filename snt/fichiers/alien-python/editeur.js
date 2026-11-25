/* Alien Python : l'éditeur des séries inversées (T145), sur le modèle de Lagon Arena et des TD en ligne.

   Il s'accroche au champ existant (textarea#txt, devant son miroir coloré) sans changer sa géométrie :
   - Entrée garde le décalage de la ligne, et décale de 4 espaces de plus après « : » ;
   - Tab décale la ligne (ou les lignes choisies), Maj+Tab la recule ; Retour arrière dans le décalage
     recule d'un cran ; Échap puis Tab sort du champ (le clavier n'est jamais piégé) ;
   - l'autocomplétion propose les mots de l'exercice (les instructions de l'alien, for, range, if…
     et les variables du programme), selon l'endroit où l'on écrit ; flèches et Entrée (ou Tab)
     au clavier, un appui du doigt sur l'écran, Échap pour fermer ; Ctrl+Espace pour la demander ;
   - Ctrl+Z annule comme d'habitude (le texte est inséré par le navigateur).

   Babash - NSI Tani Malandi · code sous licence MIT */
(function (racine) {
  'use strict';

  // les mots, avec leur rôle (en français, court) ; « genre » décide de ce qui est inséré
  var MOTS = {
    haut: ['fonction', 'déplace l’alien vers le haut'],
    bas: ['fonction', 'déplace l’alien vers le bas'],
    gauche: ['fonction', 'déplace l’alien vers la gauche'],
    droite: ['fonction', 'déplace l’alien vers la droite'],
    colonne: ['fonction', 'numéro de colonne de l’alien'],
    ligne: ['fonction', 'numéro de ligne de l’alien'],
    'for': ['mot-clé', 'pour : répète un bloc'],
    'in': ['mot-clé', 'dans'],
    range: ['fonction', 'les entiers de 0 à n (exclu)'],
    'if': ['mot-clé', 'si : teste une condition'],
    'else': ['mot-clé', 'sinon'],
    'while': ['mot-clé', 'tant que : répète un bloc'],
    'def': ['mot-clé', 'définit une fonction'],
    loop: ['variable', 'compteur de la boucle']
  };
  // le vocabulaire de chaque série : ce que les fiches précédentes ont présenté (rien de plus)
  var SERIES = {
    A: ['haut', 'bas', 'gauche', 'droite', 'for', 'in', 'range', 'loop'],
    B: ['haut', 'bas', 'gauche', 'droite', 'for', 'in', 'range', 'loop', 'if', 'else', 'colonne', 'ligne']
  };
  var ACTIONS = ['haut', 'bas', 'gauche', 'droite'], QUESTIONS = ['colonne', 'ligne'];

  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  // le bloc qui contient la ligne c : sa ligne d'en-tête (… :) et sa fin
  function decalage(l) { return (l.match(/^ */) || [''])[0].length; }
  function blocDe(lignes, c) {
    if (!lignes[c] || !lignes[c].trim()) return null;
    var dc = decalage(lignes[c]);
    for (var j = c - 1; j >= 0; j--) {
      if (!lignes[j].trim()) continue;
      var dj = decalage(lignes[j]);
      if (dj < dc && /:\s*(#.*)?$/.test(lignes[j])) {
        var fin = j;
        for (var k = j + 1; k < lignes.length; k++) { if (!lignes[k].trim()) continue; if (decalage(lignes[k]) <= dj) break; fin = k; }
        return { entete: j, fin: fin, mot: (lignes[j].match(/^\s*(\w+)/) || [])[1] || '' };
      }
      if (dj < dc) return null;
      if (dj === 0 && dc === 0) return null;
    }
    return null;
  }

  function Editeur(ta, opts) {
    var self = this;
    this.ta = ta; this.opts = opts || {};
    this.boite = ta.parentNode;
    this.vocab = SERIES[this.opts.serie] || SERIES.B;
    this.liste = document.getElementById(ta.getAttribute('aria-controls'));
    this.info = document.getElementById(this.opts.info);
    this.choix = []; this.sel = 0; this.echap = false; this.interne = false;
    ta.addEventListener('keydown', function (e) { self.touche(e); });
    ta.addEventListener('input', function (e) { self.saisie(e); });
    ta.addEventListener('blur', function () { self.echap = false; setTimeout(function () { if (document.activeElement !== self.ta) self.fermer(); }, 120); });
    ta.addEventListener('scroll', function () { if (self.ouvert()) self.placer(); });     // le champ défile (nouvelle ligne) : la liste suit le mot
    ['click', 'keyup'].forEach(function (n) {
      ta.addEventListener(n, function (e) {
        if (e.key && (/^(Escape|Tab|Shift|Control|Alt|Meta)$/.test(e.key) || (/^(Arrow(Up|Down)|Enter)$/.test(e.key) && self.ouvert()))) return;
        self.direBloc();
      });
    });
    this.liste.addEventListener('mousedown', function (e) { e.preventDefault(); });     // le curseur reste dans le champ
    this.liste.addEventListener('click', function (e) {
      var li = e.target.closest('li[data-k]'); if (!li) return;
      self.sel = +li.getAttribute('data-k'); self.accepter();
    });
  }

  // remplace [debut, fin[ par txt, comme une frappe (Ctrl+Z l'annule), puis place le curseur
  Editeur.prototype.remplacer = function (debut, fin, txt, curseur, selFin) {
    var ta = this.ta;
    this.interne = true;
    ta.focus();
    ta.setSelectionRange(debut, fin);
    var fait = false;
    try { fait = txt ? document.execCommand('insertText', false, txt) : (debut === fin || document.execCommand('delete')); } catch (e) { fait = false; }
    if (!fait) { ta.setRangeText(txt, debut, fin, 'end'); ta.dispatchEvent(new Event('input', { bubbles: true })); }
    this.interne = false;
    if (curseur !== undefined) ta.setSelectionRange(debut + curseur, selFin !== undefined ? debut + selFin : debut + curseur);
  };

  Editeur.prototype.touche = function (e) {
    var ta = this.ta, v = ta.value, s = ta.selectionStart, f = ta.selectionEnd;
    if (e.isComposing || e.keyCode === 229) return;
    // après Échap, Tab (ou Maj+Tab) n'indente pas : le navigateur passe à l'élément suivant (WCAG 2.1.2)
    if (this.echap && e.key === 'Tab' && !e.ctrlKey && !e.altKey && !e.metaKey) { this.echap = false; this.fermer(); return; }
    if (['Shift', 'Control', 'Alt', 'Meta'].indexOf(e.key) < 0) this.echap = false;
    if (this.ouvert()) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); this.sel = (this.sel + (e.key === 'ArrowDown' ? 1 : -1) + this.choix.length) % this.choix.length; this.dessiner(); return; }
      if ((e.key === 'Enter' || e.key === 'Tab') && !e.shiftKey) { e.preventDefault(); this.accepter(); return; }
      if (e.key === 'Escape') { e.preventDefault(); this.fermer(); this.dire('Propositions fermées. Échap encore, puis Tab : sortir du champ.'); return; }
    }
    if (e.key === 'Escape') { this.echap = true; this.dire('Appuie sur Tab pour sortir du champ (Maj+Tab pour revenir en arrière).'); return; }
    if (e.key === ' ' && e.ctrlKey) { e.preventDefault(); this.proposer(true); return; }
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    var deb = v.lastIndexOf('\n', s - 1) + 1;
    if (e.key === 'Tab') {
      e.preventDefault();
      // au début de la ligne (dans le décalage) : jusqu'au cran suivant ; ailleurs, Tab décale toute la ligne
      if (s === f && !e.shiftKey && /^ *$/.test(v.slice(deb, s))) { this.remplacer(s, f, '    '.slice((s - deb) % 4)); this.direBloc(); return; }
      var finSel = f > s && v[f - 1] === '\n' ? f - 1 : f, finL = v.indexOf('\n', finSel), fin = finL < 0 ? v.length : finL;
      var avant = v.slice(deb, fin), lignes = avant.split('\n');
      var apres = lignes.map(function (l) { return e.shiftKey ? l.replace(/^ {1,4}/, '') : (l.trim() ? '    ' + l : l); }).join('\n');
      if (apres === avant) return;
      if (s === f) {                     // sans sélection : la ligne bouge, le curseur la suit
        var ote = avant.length - apres.length;
        this.remplacer(deb, fin, apres, Math.max(0, s - deb - ote));
      } else this.remplacer(deb, fin, apres, 0, apres.length);
      this.direBloc();
    } else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      var ligne = v.slice(deb, s), ind = ligne.match(/^ */)[0];
      if (/:\s*(#.*)?$/.test(ligne)) ind += '    ';
      this.remplacer(s, f, '\n' + ind);
      this.direBloc();
    } else if (e.key === 'Backspace' && s === f) {
      var av = v.slice(deb, s);
      if (av.length >= 1 && /^ +$/.test(av)) { e.preventDefault(); this.remplacer(s - (av.length % 4 || 4), s, ''); }
    }
  };

  // une saisie : propositions ; et le décalage après un retour à la ligne venu d'un clavier d'écran
  Editeur.prototype.saisie = function (e) {
    if (this.interne) return;
    var t = e.inputType || '';
    if (t === 'insertLineBreak' || (t === 'insertText' && e.data === null && this.ta.value[this.ta.selectionStart - 1] === '\n')) {
      var v = this.ta.value, s = this.ta.selectionStart, debPrec = v.lastIndexOf('\n', s - 2) + 1, prec = v.slice(debPrec, s - 1);
      var ind = prec.match(/^ */)[0] + (/:\s*(#.*)?$/.test(prec) ? '    ' : '');
      if (ind && !/^ /.test(v.slice(s))) this.remplacer(s, s, ind);
      this.fermer(); return;
    }
    if ((t === 'insertText' || t === 'insertCompositionText') && e.data && /[A-Za-z_]$/.test(e.data)) this.proposer(false);
    else if (t === 'deleteContentBackward' && this.ouvert()) this.proposer(false);
    else this.fermer();
  };

  // ce qui a du sens à cet endroit
  Editeur.prototype.suggestions = function (mot, avant) {
    var v = this.ta.value, vocab = this.vocab, out = [], vus = {};
    var m0 = mot.toLowerCase();
    var noms = {}, re = /^\s*(?:for\s+([A-Za-z_]\w*)\s+in|([A-Za-z_]\w*)\s*=[^=])/gm, r;
    while ((r = re.exec(v))) { var n = r[1] || r[2]; if (!MOTS[n] && n !== mot) noms[n] = 1; }
    var t = avant.replace(/\s+$/, ''), debut = avant.trim() === '';
    var ctx = debut ? 'debut'
      : /\bfor\s+[A-Za-z_]\w*$/.test(t) ? 'apres-variable'
      : /\bfor$/.test(t) ? 'variable-boucle'
      : /\bin$/.test(t) ? 'apres-in'
      : 'valeur';
    function ajouter(nom, genre, role) {
      if (vus[nom] || nom === mot) return;
      var nn = nom.toLowerCase(), score = null;
      if (nn.indexOf(m0) === 0) score = 0; else if (m0.length > 1 && nn.indexOf(m0) > 0) score = 2;
      if (score === null) return;
      vus[nom] = 1; out.push({ nom: nom, genre: genre, role: role, s: score });
    }
    function mot_(nom) { if (vocab.indexOf(nom) >= 0) ajouter(nom, MOTS[nom][0], MOTS[nom][1]); }
    if (ctx === 'debut') {
      ACTIONS.forEach(mot_); ['for', 'if', 'else'].forEach(mot_);
      Object.keys(noms).forEach(function (n) { ajouter(n, 'variable', 'variable du programme'); });
    } else if (ctx === 'variable-boucle') { mot_('loop'); }
    else if (ctx === 'apres-variable') { mot_('in'); }
    else if (ctx === 'apres-in') { mot_('range'); }
    else {
      Object.keys(noms).forEach(function (n) { ajouter(n, 'variable', 'variable du programme'); });
      QUESTIONS.forEach(mot_);
    }
    out.sort(function (a, b) { return a.s - b.s || (a.genre === 'variable' ? -1 : 0) - (b.genre === 'variable' ? -1 : 0) || a.nom.length - b.nom.length || (a.nom < b.nom ? -1 : 1); });
    return out.slice(0, 5);
  };

  Editeur.prototype.proposer = function (force) {
    var v = this.ta.value, s = this.ta.selectionStart;
    if (s !== this.ta.selectionEnd) return this.fermer();
    var deb = v.lastIndexOf('\n', s - 1) + 1, avant = v.slice(deb, s);
    if (/#/.test(avant) || avant.split(/["']/).length % 2 === 0) return this.fermer();   // dans un commentaire ou une chaîne
    var m = avant.match(/[A-Za-z_]\w*$/);
    if (!m && !force) return this.fermer();
    m = m || [''];
    if (/^\w/.test(v.slice(s))) return this.fermer();                                     // au milieu d'un mot
    this.mot = { debut: s - m[0].length, mot: m[0] };
    this.choix = this.suggestions(m[0], avant.slice(0, avant.length - m[0].length));
    if (!this.choix.length) { if (force) this.dire('Aucune proposition ici.'); return this.fermer(); }
    this.sel = 0; this.dessiner();
  };

  Editeur.prototype.largeurCar = function () {
    if (this.cw) return this.cw;
    var cs = getComputedStyle(this.ta), cv = document.createElement('canvas').getContext('2d');
    cv.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
    this.cw = cv.measureText('MMMMMMMMMM').width / 10;
    return this.cw;
  };
  Editeur.prototype.dessiner = function () {
    var self = this, id = this.liste.id;
    this.liste.innerHTML = this.choix.map(function (c, k) {
      var f = c.genre === 'fonction';
      return '<li role="option" id="' + id + '-' + k + '" data-k="' + k + '" aria-selected="' + (k === self.sel) + '"' + (k === self.sel ? ' class="on"' : '') + '>' +
        '<code>' + esc(c.nom) + (f ? '()' : '') + '</code><span class="al-ac-role">' + esc(c.role) + '</span></li>';
    }).join('');
    this.liste.hidden = false;
    this.ta.setAttribute('aria-expanded', 'true');
    this.ta.setAttribute('aria-activedescendant', id + '-' + this.sel);
    this.placer();
    var c = this.choix[this.sel];
    this.dire(c.nom + (c.genre === 'fonction' ? '()' : '') + ' : ' + c.role + '. ' + (this.choix.length > 1 ? this.choix.length + ' propositions, flèches pour choisir, ' : '') + 'Entrée pour l’écrire, Échap pour continuer sans.');
  };
  // sous le mot (police à chasse fixe), sans sortir du cadre de l'éditeur
  Editeur.prototype.placer = function () {
    var ta = this.ta, cs = getComputedStyle(ta), v = ta.value, s = this.mot.debut;
    var ligne = v.slice(0, s).split('\n').length - 1, col = s - (v.lastIndexOf('\n', s - 1) + 1);
    var lh = parseFloat(cs.lineHeight) || 24, cw = this.largeurCar();
    var x = ta.offsetLeft + ta.clientLeft + parseFloat(cs.paddingLeft) + col * cw - ta.scrollLeft - 6;
    var y = ta.offsetTop + ta.clientTop + parseFloat(cs.paddingTop) + (ligne + 1) * lh - ta.scrollTop + 2;
    var large = this.boite.clientWidth, w = this.liste.offsetWidth;
    this.liste.style.left = Math.max(0, Math.min(x, large - w)) + 'px';
    this.liste.style.top = Math.max(0, y) + 'px';
  };
  Editeur.prototype.fermer = function () {
    if (!this.liste || this.liste.hidden) { this.choix = []; return; }
    this.liste.hidden = true; this.choix = [];
    this.ta.setAttribute('aria-expanded', 'false'); this.ta.removeAttribute('aria-activedescendant');
  };
  Editeur.prototype.ouvert = function () { return !this.liste.hidden && this.choix.length > 0; };
  Editeur.prototype.accepter = function () {
    var c = this.choix[this.sel]; if (!c) return;
    var s = this.ta.selectionStart, txt = c.nom, cur;
    if (c.genre === 'fonction') { txt += '()'; cur = txt.length - (QUESTIONS.indexOf(c.nom) >= 0 ? 0 : 1); }
    else if (c.nom === 'else') { txt += ' :'; }
    else if (c.genre === 'mot-clé') txt += ' ';
    this.fermer();
    this.remplacer(this.mot.debut, s, txt, cur);
    this.dire(c.nom + (c.genre === 'fonction' ? '()' : '') + ' : ' + c.role + '.');
  };
  Editeur.prototype.dire = function (t) { if (this.info) this.info.textContent = t; };
  // où est le curseur : dans quel bloc
  Editeur.prototype.direBloc = function () {
    if (this.ouvert() || document.activeElement !== this.ta) return;
    var v = this.ta.value, c = v.slice(0, this.ta.selectionStart).split('\n').length - 1, lignes = v.split('\n');
    var b = blocDe(lignes, c);
    var nom = b ? ({ 'for': 'la boucle for', 'while': 'la boucle while', 'if': 'le if', 'else': 'le else', 'def': 'la fonction' }[b.mot] || 'le bloc') : '';
    this.dire('Ligne ' + (c + 1) + (b ? ' : dans ' + nom + ' de la ligne ' + (b.entete + 1) + '.' : /:\s*(#.*)?$/.test(lignes[c] || '') ? ' : en-tête d’un bloc (les lignes décalées qui suivent).' : ' : hors de tout bloc.'));
  };

  racine.AlienEditeur = { monter: function (ta, opts) { if (!ta || ta.alienEditeur) return ta && ta.alienEditeur; ta.alienEditeur = new Editeur(ta, opts); return ta.alienEditeur; }, SERIES: SERIES, blocDe: blocDe };
})(window);
