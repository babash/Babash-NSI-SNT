/* ─────────────────────────────────────────────
   Equipage : le moteur d'avatars des runners (T112b)

   Module sans dépendance. Il dessine en pixel art (grille de 48 x 64,
   gabarit A « tout rond », contour automatique de 1 px) un avatar
   décrit par un petit objet JSON, dans l'un des sept états, et le
   margouillat vert à turbine, posable partout.

     Equipage.creer(element, description, options)  -> poignée
     Equipage.svg(description, options)             -> chaîne SVG
     Equipage.margouillat(element, options)         -> poignée
     Equipage.normaliser(description)               -> description propre
     Equipage.aleatoire(graine)                     -> description
     Equipage.texte(description, etat)              -> texte alternatif
     Equipage.catalogue, Equipage.ETATS, Equipage.version

   Contrat complet : assets/equipage/LISEZMOI.md.
   Dessins originaux ; style de personnage repris du jeu de révision
   de l'enseignant. Aucun envoi de données, rien n'est gardé.
   Auteur : Babash - NSI Tani Malandi. Code sous licence MIT.
   ───────────────────────────────────────────── */
(function (racine) {
  'use strict';

  var VERSION = '1.0.0';
  var CONTOUR = '#1b1530', NOIR = '#2b2143';
  var NC = '#3ff0ff', NR = '#ff4fb8', NJ = '#e8ff3a', NV = '#8a5bff', NO = '#ff9a3a', NG = '#5dff8a';

  /* ── couleurs ─────────────────────────────── */
  var _rgb = {};
  function rgb(c) {
    var v = _rgb[c];
    if (!v) {
      var h = c.charAt(0) === '#' ? c.slice(1) : c;
      v = _rgb[c] = [parseInt(h.substr(0, 2), 16), parseInt(h.substr(2, 2), 16), parseInt(h.substr(4, 2), 16)];
    }
    return v;
  }
  function h2(v) { v = Math.max(0, Math.min(255, Math.round(v))); return (v < 16 ? '0' : '') + v.toString(16); }
  function mix(a, b, t) { var A = rgb(a), B = rgb(b); return '#' + h2(A[0] + (B[0] - A[0]) * t) + h2(A[1] + (B[1] - A[1]) * t) + h2(A[2] + (B[2] - A[2]) * t); }
  function fonce(c, t) { return mix(c, CONTOUR, t === undefined ? 0.22 : t); }
  function clair(c, t) { return mix(c, '#ffffff', t === undefined ? 0.25 : t); }

  /* arrondi « au pair », comme le dessin d'origine */
  function rnd(v) { var f = Math.floor(v), d = v - f; if (d > 0.5) return f + 1; if (d < 0.5) return f; return f % 2 === 0 ? f : f + 1; }
  function fdiv(a, b) { return Math.floor(a / b); }
  function mod(a, n) { return ((a % n) + n) % n; }

  /* générateur pseudo-aléatoire reproductible */
  function hasard(graine) {
    var s = (graine >>> 0) || 1;
    return function () {
      s = (s + 0x6D2B79F5) >>> 0;
      var t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ── calque de pixels ─────────────────────── */
  function Calque(w, h) { this.w = w; this.h = h; this.p = new Map(); this.m = new Set(); }
  var K = 1024;
  Calque.prototype.px = function (x, y, c, solide, a) {
    if (c === null || c === undefined) return;
    if (solide === undefined) solide = true;
    if (a === undefined) a = 1;
    x = rnd(x); y = rnd(y);
    if (x < 0 || y < 0 || x >= this.w || y >= this.h) return;
    var k = y * K + x;
    if (a < 1 && this.p.has(k)) {
      var o = this.p.get(k);
      c = mix(o[0], c, a);
      a = o[1] >= 1 ? 1 : Math.max(o[1], a);
    }
    this.p.set(k, [c, a]);
    if (solide) this.m.add(k);
  };
  Calque.prototype.ote = function (x, y) { this.p.delete(y * K + x); };
  Calque.prototype.rect = function (x, y, w, h, c, solide, a) {
    for (var j = 0; j < h; j++) for (var i = 0; i < w; i++) this.px(x + i, y + j, c, solide, a);
  };
  Calque.prototype.hline = function (x0, x1, y, c, solide, a) {
    for (var x = Math.min(x0, x1); x <= Math.max(x0, x1); x++) this.px(x, y, c, solide, a);
  };
  Calque.prototype.carte = function (x, y, rows, pal, solide) {
    for (var j = 0; j < rows.length; j++) for (var i = 0; i < rows[j].length; i++) {
      var ch = rows[j].charAt(i);
      if (ch !== '.' && pal[ch]) this.px(x + i, y + j, pal[ch], solide);
    }
  };
  Calque.prototype.ellipse = function (cx, cy, rx, ry, c, solide, f) {
    for (var y = Math.trunc(cy - ry) - 1; y < Math.trunc(cy + ry) + 2; y++) {
      for (var x = Math.trunc(cx - rx) - 1; x < Math.trunc(cx + rx) + 2; x++) {
        var dx = (x + 0.5 - cx) / rx, dy = (y + 0.5 - cy) / ry;
        if (dx * dx + dy * dy <= 1) this.px(x, y, f ? f(x, y) : c, solide);
      }
    }
  };
  Calque.prototype.plein = function (x, y) { return this.m.has(y * K + x); };
  Calque.prototype.contour = function (c) {
    var aj = [], self = this;
    this.m.forEach(function (k) {
      var x = k % K, y = (k - x) / K;
      [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
        var X = x + d[0], Y = y + d[1];
        if (X >= 0 && Y >= 0 && X < self.w && Y < self.h && !self.m.has(Y * K + X)) aj.push(Y * K + X);
      });
    });
    aj.forEach(function (k) { self.p.set(k, [c || CONTOUR, 1]); self.m.add(k); });
  };
  Calque.prototype.sur = function (o, dx, dy, solide) {
    dx = dx || 0; dy = dy || 0; if (solide === undefined) solide = true;
    var self = this;
    o.p.forEach(function (v, k) {
      var x = k % K, y = (k - x) / K, X = x + dx, Y = y + dy;
      if (X >= 0 && Y >= 0 && X < self.w && Y < self.h) self.px(X, Y, v[0], solide && o.m.has(k), v[1]);
    });
  };
  /* décale de dy les rangées au-dessus de yLim (tête qui respire, qui s'écrase) */
  Calque.prototype.decaler = function (yLim, dy) {
    var p = new Map(), m = new Set(), self = this;
    this.p.forEach(function (v, k) { var y = Math.floor(k / K); if (y >= yLim) p.set(k, v); });
    this.m.forEach(function (k) { var y = Math.floor(k / K); if (y >= yLim) m.add(k); });
    this.p.forEach(function (v, k) {
      var x = k % K, y = (k - x) / K;
      if (y < yLim && y + dy >= 0 && y + dy < self.h) { p.set((y + dy) * K + x, v); if (self.m.has(k)) m.add((y + dy) * K + x); }
    });
    this.p = p; this.m = m;
  };
  Calque.prototype.anneau = function () {
    var r = new Set(), self = this;
    this.m.forEach(function (k) {
      var x = k % K, y = (k - x) / K;
      [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
        var X = x + d[0], Y = y + d[1], q = Y * K + X;
        if (X >= 0 && Y >= 0 && X < self.w && Y < self.h && !self.m.has(q) && !self.p.has(q)) r.add(q);
      });
    });
    return r;
  };
  Calque.prototype.transformer = function (fn, w, h) {
    var R = new Calque(w || this.w, h || this.h);
    this.p.forEach(function (v, k) { var x = k % K, y = (k - x) / K, q = fn(x, y); R.p.set(q[1] * K + q[0], v); });
    this.m.forEach(function (k) { var x = k % K, y = (k - x) / K, q = fn(x, y); R.m.add(q[1] * K + q[0]); });
    return R;
  };

  /* pixels -> chemins SVG (rangées fusionnées) */
  function chemins(cal) {
    var rows = {};
    cal.p.forEach(function (v, k) { var x = k % K, y = (k - x) / K; (rows[y] = rows[y] || {})[x] = v; });
    var par = {};
    Object.keys(rows).forEach(function (ys) {
      var y = +ys, r = rows[ys], xs = Object.keys(r).map(Number).sort(function (a, b) { return a - b; });
      var i = 0;
      while (i < xs.length) {
        var x0 = xs[i], v = r[x0], j = i;
        while (j + 1 < xs.length && xs[j + 1] === xs[j] + 1 && r[xs[j + 1]][0] === v[0] && r[xs[j + 1]][1] === v[1]) j++;
        var cle = v[0] + '|' + (v[1] >= 1 ? 1 : v[1].toFixed(2));
        (par[cle] = par[cle] || []).push([x0, y, xs[j] - x0 + 1]);
        i = j + 1;
      }
    });
    var out = '';
    Object.keys(par).forEach(function (cle) {
      var c = cle.split('|'), plein = c[1] === '1', d = '';
      par[cle].forEach(function (t) {
        d += plein ? 'M' + t[0] + ' ' + t[1] + 'h' + t[2] + '.06v1.06h-' + t[2] + '.06z' : 'M' + t[0] + ' ' + t[1] + 'h' + t[2] + 'v1h-' + t[2] + 'z';
      });
      out += '<path fill="' + c[0] + '"' + (plein ? '' : ' fill-opacity="' + c[1] + '"') + ' d="' + d + '"/>';
    });
    return out;
  }
  function cheminsSet(set, cls) {
    var rows = {};
    set.forEach(function (k) { var x = k % K, y = (k - x) / K; (rows[y] = rows[y] || []).push(x); });
    var d = '';
    Object.keys(rows).forEach(function (ys) {
      var xs = rows[ys].sort(function (a, b) { return a - b; }), i = 0;
      while (i < xs.length) { var j = i; while (j + 1 < xs.length && xs[j + 1] === xs[j] + 1) j++; d += 'M' + xs[i] + ' ' + ys + 'h' + (xs[j] - xs[i] + 1) + 'v1h-' + (xs[j] - xs[i] + 1) + 'z'; i = j + 1; }
    });
    return d ? '<path class="' + cls + '" d="' + d + '"/>' : '';
  }

  /* ════════════════════════════════════════════
     LE CATALOGUE
     Toute pièce va sur tout avatar : aucune n'est liée à un genre.
     ════════════════════════════════════════════ */
  var TEINTS = ['#f2d0b0', '#e0ac80', '#c68a5e', '#a86b45', '#8a5236', '#6b3f28', '#5a3422', '#4a2c1d'];
  var PALETTES = {
    cheveux: { noirs: '#1f1a24', bruns: '#2a1a14', chatains: '#4a2e1e', auburn: '#7a4e2d', roux: '#a8482a', blonds: '#c89a4a', gris: '#8a8a96', blancs: '#e8e4dc', bleus: '#3a5ad8', roses: '#d84a9a', verts: '#2f9a5a', violets: '#6a3fc8' },
    tissu: { canard: '#2f6f8f', violet: '#6a3fc8', vert: '#1f9a6a', sarcelle: '#1f8a8a', marine: '#2a3a5a', nuit: '#24263a', kaki: '#4a6a3a', blanc: '#f2f0ea', jaune: '#f2c14e', orange: '#f08a2a', rouge: '#c8453d', rose: '#d84a6a', gris: '#5a5f7a', anthracite: '#33364a', jean: '#4a6fa5', brun: '#6b4a2e', prune: '#5a3a7a', beige: '#c8b48a' },
    neon: { cyan: NC, rose: NR, jaune: NJ, violet: NV, orange: NO, vert: NG },
    chaussures: { blanches: '#f2f0ea', noires: '#2f2f3f', rouges: '#e8404a', jaunes: '#e8b830', brunes: '#6b4a2e', bleues: '#3f6ad8', vertes: '#1f9a6a' },
    yeux: { bruns: '#5a3a22', noirs: '#3a2a1a', verts: '#3f6a4a', bleus: '#3f6a8a', turquoise: '#3a8ab8', ambre: '#c8902a', violets: '#8a5bff' }
  };

  function liste(pairs) { return pairs.map(function (p) { return { id: p[0], nom: p[1] }; }); }
  var CATALOGUE = {
    lignee: liste([['humain', 'Humain·e'], ['cyber', 'Cyber'], ['nuee', 'Nuée'], ['mutant', 'Mutant·e'], ['lagon', 'Peuple du lagon'], ['esprit', 'Esprit'], ['greffe', 'Greffé·e']]),
    corps: liste([['fine', 'Fin'], ['moyenne', 'Moyen'], ['ronde', 'Rond']]),
    coiffure: liste([['court', 'Courts'], ['rase', 'Rasés'], ['lisses', 'Lisses mi-longs'], ['boucles', 'Boucles'], ['degrade_circuit', 'Dégradé circuit'], ['tresses', 'Tresses'], ['tresses_fibre', 'Tresses fibre optique'], ['locks_cables', 'Locks câblées'], ['afro_pixel', 'Afro pixel'], ['puffs', 'Deux puffs'], ['chignon_antenne', 'Chignon antenne'], ['crete_graffiti', 'Crête graffiti'], ['capuche', 'Capuche réseau'], ['feuilles', 'Couronne de feuilles'], ['volute', 'Volute'], ['glitch', 'Pixels flottants']]),
    haut: liste([['tshirt', 'Tee-shirt'], ['veste', 'Veste runner'], ['maillot', 'Maillot de quartier libre'], ['tunique', 'Tunique fleurs-circuits'], ['sweat', 'Sweat'], ['gilet', 'Gilet de bricole'], ['debardeur', 'Débardeur de battle'], ['chemise', 'Chemise à bugs'], ['combinaison', 'Combinaison de course'], ['aucun', 'Sans haut (Nuée, Esprit)']]),
    bas: liste([['pantalon', 'Pantalon'], ['cargo', 'Cargo à câble'], ['short', 'Short de terrain'], ['jogging', 'Jogging fluo'], ['jupe_longue', 'Jupe longue fleurs-circuits'], ['sarouel', 'Sarouel de danse'], ['patchwork', 'Pantalon rapiécé']]),
    chaussures: liste([['baskets', 'Baskets'], ['montantes', 'Baskets montantes'], ['savates', 'Savates néon'], ['bottes', 'Bottes de pont'], ['crampons', 'Crampons de sable'], ['pieds_nus', 'Pieds nus et chevillère']]),
    emplacements: liste([['tete', 'Sur la tête'], ['visage', 'Sur le visage'], ['dos', 'Dans le dos'], ['main', 'Dans la main'], ['epaule', 'Sur les épaules'], ['autour', 'Autour']]),
    objets: {
      tete: liste([['aucun', 'Rien'], ['casque_audio', 'Casque audio'], ['frontale', 'Lampe frontale'], ['bandeau', 'Bandeau'], ['soudure', 'Lunettes de soudure'], ['chapeau_paille', 'Chapeau de paille'], ['bonnet', 'Bonnet à pompon'], ['couronne_fleurs', 'Couronne de fleurs'], ['antennes', 'Antennes à ressort'], ['casquette', 'Casquette sans marque']]),
      visage: liste([['aucun', 'Rien'], ['lunettes', 'Lunettes de vue'], ['lunettes_ecran', 'Lunettes-écran'], ['visiere', 'Visière à un œil'], ['masque', 'Masque de fête souriant'], ['implant', 'Implant neural'], ['peinture', 'Peinture néon'], ['pansement', 'Pansement']]),
      dos: liste([['aucun', 'Rien'], ['sac_antenne', 'Sac-antenne'], ['turbine_dos', 'Turbine'], ['ailes_fee', 'Ailes de fée'], ['cape', 'Cape'], ['jetpack', 'Réacteurs à vapeur'], ['drapeau', 'Drapeau au margouillat']]),
      main: liste([['aucun', 'Rien'], ['pneu', 'Pneu et bâton'], ['bombe', 'Bombe de peinture'], ['enceinte', 'Enceinte bricolée'], ['ballon', 'Ballon rapiécé'], ['mangue', 'Mangue'], ['cle', 'Clé à molette'], ['baton_lumineux', 'Bâton lumineux'], ['lanterne', 'Lanterne']]),
      epaule: liste([['aucun', 'Rien'], ['chale', 'Châle'], ['echarpe', 'Écharpe'], ['drone', 'Drone libellule']]),
      autour: liste([['aucun', 'Rien'], ['aura', 'Aura néon'], ['lucioles', 'Lucioles de données'], ['bulles', 'Bulles du lagon'], ['petales', 'Pétales d\'ylang'], ['notes', 'Notes de musique'], ['pixels', 'Pluie de pixels']])
    },
    compagnon: [{ id: 'aucun', nom: 'Aucun' }, { id: 'margouillat', nom: 'Margouillat vert', depart: true }, { id: 'maki', nom: 'Maki', gagne: true }, { id: 'robot', nom: 'Petit robot', gagne: true }, { id: 'tortue', nom: 'Tortue serveur', gagne: true }, { id: 'roussette', nom: 'Roussette', gagne: true }],
    teint: TEINTS.map(function (c, i) { return { id: i + 1, nom: 'Teint ' + (i + 1), couleur: c }; }),
    couleurs: {}
  };
  Object.keys(PALETTES).forEach(function (k) {
    CATALOGUE.couleurs[k] = Object.keys(PALETTES[k]).map(function (id) { return { id: id, couleur: PALETTES[k][id] }; });
  });
  /* palette de chaque champ de couleur de la description */
  var CHAMP_PALETTE = { cheveux: 'cheveux', haut: 'tissu', bas: 'tissu', accent: 'neon', chaussures: 'chaussures', yeux: 'yeux' };

  var MANCHES = { veste: 'longues', maillot: 'courtes', tunique: 'courtes', sweat: 'longues', gilet: 'aucune', debardeur: 'aucune', chemise: 'longues', combinaison: 'longues', tshirt: 'courtes', aucun: 'aucune' };
  var SANS_CORPS = { nuee: 1, esprit: 1 };

  var DEFAUT = {
    v: 1, lignee: 'humain', teint: 5, corps: 'moyenne', coiffure: 'court', cheveux: 'noirs',
    haut: 'tshirt', bas: 'pantalon', chaussures: 'baskets',
    objets: { tete: 'aucun', visage: 'aucun', dos: 'aucun', main: 'aucun', epaule: 'aucun', autour: 'aucun' },
    fauteuil: false, compagnon: 'margouillat',
    couleurs: { haut: 'canard', bas: 'anthracite', accent: 'cyan', chaussures: 'blanches', yeux: 'bruns' }
  };

  var EMPLACEMENTS = ['tete', 'visage', 'dos', 'main', 'epaule', 'autour'];
  function objetDans(e, v) { return CATALOGUE.objets[e].some(function (x) { return x.id === v; }); }
  function dans(champ, v) { return CATALOGUE[champ].some(function (e) { return e.id === v; }); }
  function copie(o) { return JSON.parse(JSON.stringify(o)); }

  function normaliser(d) {
    d = d && typeof d === 'object' ? d : {};
    var r = copie(DEFAUT);
    ['lignee', 'corps', 'coiffure', 'haut', 'bas', 'chaussures', 'compagnon'].forEach(function (k) {
      if (dans(k, d[k])) r[k] = d[k];
    });
    var ob = d.objets && typeof d.objets === 'object' ? d.objets : {};
    /* anciens champs (accessoire, tete, visage) : repris dans leur emplacement */
    if (typeof d.accessoire === 'string') EMPLACEMENTS.forEach(function (e) { if (ob[e] === undefined && objetDans(e, d.accessoire)) ob[e] = d.accessoire; });
    if (ob.tete === undefined) ob.tete = d.tete;
    if (ob.visage === undefined) ob.visage = d.visage;
    EMPLACEMENTS.forEach(function (e) { if (objetDans(e, ob[e])) r.objets[e] = ob[e]; });
    var t = parseInt(d.teint, 10);
    if (t >= 1 && t <= TEINTS.length) r.teint = t;
    r.fauteuil = d.fauteuil === true;
    if (typeof d.cheveux === 'string' && (PALETTES.cheveux[d.cheveux] || /^#[0-9a-fA-F]{6}$/.test(d.cheveux))) r.cheveux = d.cheveux;
    var c = d.couleurs && typeof d.couleurs === 'object' ? d.couleurs : {};
    ['haut', 'bas', 'accent', 'chaussures', 'yeux'].forEach(function (k) {
      var v = c[k];
      if (typeof v === 'string' && (PALETTES[CHAMP_PALETTE[k]][v] || /^#[0-9a-fA-F]{6}$/.test(v))) r.couleurs[k] = v;
    });
    if (r.haut === 'aucun' && !SANS_CORPS[r.lignee]) r.haut = 'tshirt';
    return r;
  }
  function couleur(champ, v) { return PALETTES[CHAMP_PALETTE[champ]][v] || v; }

  /* description -> réglages de dessin */
  function reglages(d) {
    var acc = couleur('accent', d.couleurs.accent);
    var autres = [NC, NR, NJ, NV, NO, NG].filter(function (x) { return x !== acc; });
    var acc2 = autres[(d.teint + d.coiffure.length) % autres.length];
    var haut = couleur('haut', d.couleurs.haut), bas = couleur('bas', d.couleurs.bas);
    return {
      lignee: d.lignee, corps: d.corps, peau: TEINTS[d.teint - 1], cheveux: couleur('cheveux', d.cheveux),
      coiffure: d.coiffure, tenue: d.haut, haut: haut, accent: acc, accent2: acc2, manches: MANCHES[d.haut],
      embleme: fonce(haut, 0.6), dessous: '#ece4d4', motif_c: acc, bug: acc2, motif: NOIR,
      bas_style: d.bas, bas: bas, bande: acc, cable: acc2, piece1: fonce(haut, 0.05), piece2: '#e8b84a',
      chaussure_style: d.chaussures, chaussure: couleur('chaussures', d.couleurs.chaussures), lacet: acc,
      o: d.objets, acc: d.objets.main, chale: mix(acc2, '#ff6a3a', 0.55), ecran: d.objets.visage === 'lunettes_ecran', lunettes: d.objets.visage === 'lunettes',
      fauteuil: d.fauteuil, rayons: acc, gants: d.haut === 'combinaison' ? '#3a3f58' : null,
      poignet: d.haut === 'debardeur' ? acc2 : null, capuche: haut, circuit: acc, bandeau: acc,
      iris: couleur('yeux', d.couleurs.yeux), taches: '#5ff2c8', compagnon: d.compagnon,
      pix: ['#7a5bf0', '#5a7cf0', '#46c8f0']
    };
  }

  /* ════════════════════════════════════════════
     LE CORPS (gabarit A, 48 x 64)
     ════════════════════════════════════════════ */
  var W = 48, H = 64, CX = 24;
  var G = 60, SY0 = 58, LEGTOP = 54, TY = 46, HY = 28, EY = 37;
  var X0 = CX - 9, X1 = CX + 8, RR = [4, 2, 1, 1], LEGW = { 10: 3, 12: 4, 14: 5 };

  function Ctx(cfg, pose) {
    this.cfg = cfg; this.pose = pose;
    this.L = new Calque(W, H); this.F = new Calque(W, H);
    this.tw = { fine: 10, moyenne: 12, ronde: 14 }[cfg.corps] || 12;
    this.tx0 = CX - this.tw / 2; this.tx1 = CX + this.tw / 2 - 1;
    this.legW = LEGW[this.tw]; this.lx0 = CX - 1 - this.legW; this.rx0 = CX + 1;
    this.sk = cfg.peau; this.hc = cfg.cheveux; this.lig = cfg.lignee;
    this.hdy = pose.tete === 'baisse' ? 1 : 0; this.assis = !!cfg.fauteuil;
  }
  Ctx.prototype.px = function (x, y, c, a) { this.L.px(x, y, c, true, a); };
  Ctx.prototype.fx = function (x, y, c, a) { this.F.px(x, y, c, false, a); };
  Ctx.prototype.glow = function (x, y, c, r, a) {
    r = r || 2; a = a === undefined ? 0.35 : a;
    for (var dy = -r; dy <= r; dy++) for (var dx = -r; dx <= r; dx++) {
      var d = Math.hypot(dx, dy);
      if (d > 0 && d <= r) this.fx(x + dx, y + dy, c, a * (1 - d / (r + 0.5)));
    }
  };

  /* bras : suite de cellules 2 x 1 */
  function chemin(x, y, s, moves) {
    var c = [[x, y], [x + 1, y]];
    for (var i = 0; i < moves.length; i++) {
      var mv = moves.charAt(i);
      if (mv === 'd') y += 1; else if (mv === 'u') y -= 1;
      else if (mv === 'o') { x += s; y -= 1; } else if (mv === 'O') { x += s; y += 1; }
      else if (mv === 'i') x -= s; else if (mv === 'I') { x -= s; y += 1; } else if (mv === 'e') x += s;
      c.push([x, y], [x + 1, y]);
    }
    return c;
  }
  var POSES_BRAS = {
    repos: ['dddddd', 'dddddd'], haut: ['ooooou', 'ooooou'], salut: ['dddddd', 'ooooouu'], salut2: ['dddddd', 'oooouuu'],
    tenir: ['dddddd', 'dOdOdd'], ouvert: ['dOdOdd', 'dOdOdd'], assis: ['dOdOdd', 'dOdOdd'], triste: ['dddddd', 'dddddd'],
    clavier: ['ddddiii', 'ddddiii'], clavier2: ['dddiiii', 'ddddiii'], clavier3: ['ddddiii', 'dddiiii']
  };
  var TIENT = { pneu: 1, bombe: 1, cle: 1, mangue: 1, baton_lumineux: 1, lanterne: 1 };
  function bras(c, pose) {
    if (c.assis && (pose === 'repos' || pose === 'triste' || pose === 'ouvert' || pose === 'tenir')) pose = 'assis';
    var mv = (POSES_BRAS[pose] || POSES_BRAS.repos).slice();
    if (pose === 'repos' && TIENT[c.cfg.acc]) mv[1] = POSES_BRAS.tenir[1];
    var l = c.tx0 - 2, r = c.tx1 + 1;
    if (pose === 'triste') { l += 1; r -= 1; }
    return [chemin(l, TY + 1, -1, mv[0]), chemin(r, TY + 1, 1, mv[1]), pose];
  }

  function dessiner(cfg, pose) {
    pose = pose || {};
    var c = new Ctx(cfg, pose);
    objetsDerriere(c);
    arriere(c); jambes(c); torse(c);
    var b = bras(c, pose.bras || 'repos');
    c.BL = b[0]; c.BR = b[1]; c.brasPose = b[2];
    peindreBras(c, c.BL, 0); peindreBras(c, c.BR, 1);
    objetsEpaule(c);
    tete(c); cheveuxDevant(c); accessoiresDevant(c); objetsVisage(c); objetsTete(c); tenu(c); objetsAutour(c);
    if (pose.souffle) { c.L.decaler(TY, pose.souffle); c.F.decaler(TY, pose.souffle); }
    c.L.contour(c.lig === 'esprit' ? '#5a4a98' : CONTOUR);
    if (c.cfg.o.autour === 'aura') aura(c);
    var R = new Calque(W, H);
    R.sur(c.L); R.sur(c.F, 0, 0, false);
    R.main = c.BR[c.BR.length - 1];
    return R;
  }

  /* ---------- arrière */
  function arriere(c) {
    var cfg = c.cfg, L = c.L, coif = cfg.coiffure, hy = HY + c.hdy, hc = c.hc, x, y, i, k;
    if (cfg.fauteuil) fauteuilArriere(c);
    if (cfg.o.dos === 'sac_antenne') {
      L.rect(c.tx0 - 1, TY - 1, c.tw + 2, 7, '#3a3f58');
      x = c.tx1 + 4;
      for (y = HY - 3; y < TY; y++) c.px(x, y, '#9aa3b8');
      c.px(x - 1, HY + 4, '#9aa3b8'); c.px(x + 1, HY + 4, '#9aa3b8');
      L.rect(x - 1, HY - 5, 3, 2, cfg.accent2); c.glow(x, HY - 5, cfg.accent2, 3, 0.45);
    }
    if (cfg.o.dos === 'turbine_dos') {
      var cx = c.tx0 - 3.5, cy = TY - 5.5, r = 4.8;
      for (y = Math.trunc(cy - r) - 1; y < Math.trunc(cy + r) + 2; y++) for (x = Math.trunc(cx - r) - 1; x < Math.trunc(cx + r) + 2; x++) {
        var d = Math.hypot(x + 0.5 - cx, y + 0.5 - cy);
        if (d >= r - 1.2 && d <= r) c.px(x, y, (x + y) % 2 ? '#c8963b' : '#e8b84a');
        else if (d < r - 1.2) c.px(x, y, '#2a2f44');
      }
      var rot = (c.pose.turbine || 0) * 0.7;
      for (k = 0; k < 3; k++) {
        var a = -Math.PI / 2 + k * 2.094 + 0.3 + rot;
        for (var t = 1; t <= 3; t++) c.px(cx - 0.5 + Math.cos(a) * t, cy - 0.5 + Math.sin(a) * t, NC);
      }
      c.px(cx - 0.5, cy - 0.5, NJ);
      [[0, -7, 0.6], [-1, -8, 0.5], [1, -9, 0.4], [0, -10, 0.3], [-2, -10, 0.25]].forEach(function (v) { c.fx(cx + v[0], cy + v[1], '#f4f6ff', v[2]); });
      c.glow(Math.trunc(cx), Math.trunc(cy), NC, 4, 0.2);
    }
    if (coif === 'tresses_fibre') {
      var cols = [NC, NR, NJ, NV];
      [X0 - 2, X0 - 1, X0, X1, X1 + 1, X1 + 2].forEach(function (x, i) {
        var bot = TY + 5 + (i % 3);
        for (var y = hy + 6; y < bot; y++) c.px(x, y, (y + i) % 2 ? hc : fonce(hc, 0.3));
        var tip = cols[i % 4];
        c.px(x, bot, tip); c.px(x, bot + 1, clair(tip, 0.4)); c.glow(x, bot + 1, tip, 2, 0.4);
      });
    }
    if (coif === 'tresses') {
      [X0 - 1, X0, X1, X1 + 1].forEach(function (x) {
        for (var y = hy + 6; y < TY + 7; y++) c.px(x, y, y % 2 ? hc : fonce(hc, 0.25));
        c.px(x, TY + 7, cfg.accent);
      });
    }
    if (coif === 'locks_cables') {
      [X0 - 2, X0 - 1, X0 + 1, X1 - 1, X1 + 1, X1 + 2].forEach(function (x, i) {
        var cable = i === 1 || i === 4, col = cable ? (i === 1 ? cfg.accent : cfg.accent2) : hc;
        var bot = TY + 3 + (i * 2) % 3;
        for (var y = hy + 4; y < bot; y++) c.px(x, y, cable ? col : ((fdiv(y, 2) + i) % 2 ? hc : fonce(hc, 0.3)));
        if (cable) { c.L.rect(x, bot, 1, 2, '#9aa3b8'); c.px(x, bot + 2, '#5a5f7a'); c.glow(x, bot, col, 2, 0.3); }
      });
    }
    if (coif === 'lisses') {
      for (y = hy + 4; y < TY + 3; y++) for (x = X0 - 1; x <= X1 + 1; x++) c.px(x, y, (x === X0 - 1 || x === X1 + 1) && y > TY ? fonce(hc, 0.2) : hc);
    }
    if (coif === 'afro_pixel') {
      var acx = CX - 0.5, acy = hy + 6, ar = 13;
      for (y = Math.trunc(acy - ar); y < Math.trunc(acy + ar) + 1; y++) for (x = Math.trunc(acx - ar); x < Math.trunc(acx + ar) + 1; x++) {
        if (Math.hypot(x + 0.5 - acx, y + 0.5 - acy) <= ar && y < hy + 15) c.px(x, y, (fdiv(x, 2) + fdiv(y, 2)) % 3 === 0 ? fonce(hc, 0.2) : hc);
      }
      for (k = 0; k < 44; k++) {
        var an = k / 44 * 2 * Math.PI, ax = acx + Math.cos(an) * (ar + 1.3), ay = acy + Math.sin(an) * (ar + 1.3);
        if (ay < hy + 14) c.fx(ax - 0.5, ay - 0.5, k % 2 ? cfg.accent2 : cfg.accent, k % 4 < 2 ? 0.9 : 0.5);
      }
    }
    if (coif === 'puffs') {
      [X0 - 1, X1 + 2].forEach(function (pcx) {
        c.L.ellipse(pcx, hy + 3, 4.5, 4.5, hc, true, function (x, y) { return (x * 7 + y * 3) % 5 === 0 ? fonce(hc, 0.2) : hc; });
      });
    }
    if (coif === 'capuche') {
      var hcol = cfg.capuche;
      c.L.ellipse(CX - 0.5, hy + 8.5, 12, 11.5, hcol, true, function (x, y) { return y < TY + 1 ? hcol : null; });
    }
    if (c.lig === 'esprit') espritCorps(c);
    if (c.lig === 'nuee') nueeCorps(c);
  }

  function fauteuilArriere(c) {
    var ray = c.cfg.rayons;
    [c.tx0 - 6.5, c.tx1 + 7.5].forEach(function (cx) {
      var cy = LEGTOP + 1, r = 6.2, x, y, k, t;
      for (y = Math.trunc(cy - r) - 1; y < Math.trunc(cy + r) + 2; y++) for (x = Math.trunc(cx - r) - 1; x < Math.trunc(cx + r) + 2; x++) {
        var d = Math.hypot(x + 0.5 - cx, y + 0.5 - cy);
        if (d >= r - 1.3 && d <= r) c.px(x, y, '#2a2a35');
        else if (d >= r - 2.2 && d < r - 1.3) c.px(x, y, '#9aa3b8');
        else if (d < r - 2.2) c.px(x, y, '#1b1f33');
      }
      var rot = (c.pose.roue || 0) * 0.35;
      for (k = 0; k < 6; k++) { var a = k * Math.PI / 3 + 0.2 + rot; for (t = 1; t < 4; t++) c.px(cx - 0.5 + Math.cos(a) * t, cy - 0.5 + Math.sin(a) * t, ray); }
      c.px(cx - 0.5, cy - 0.5, '#ffffff');
      c.glow(Math.trunc(cx), Math.trunc(cy), ray, 6, 0.18);
    });
    c.L.rect(c.tx0 - 6, LEGTOP, c.tw + 12, 2, '#5a5f7a');
    c.L.hline(c.tx0 - 6, c.tx1 + 6, LEGTOP, '#9aa3b8');
  }

  /* ---------- jambes */
  function jambes(c) {
    var cfg = c.cfg;
    if (SANS_CORPS[c.lig]) return;
    var bas = cfg.bas, sk = c.sk, style = cfg.bas_style, x, y, k;
    if (c.assis) {
      c.L.rect(c.lx0 - 1, LEGTOP, c.legW * 2 + 4, 2, bas);
      c.L.hline(c.lx0 - 1, c.rx0 + c.legW, LEGTOP, clair(bas, 0.2));
      [c.lx0 + 1, c.rx0].forEach(function (lx) { c.L.rect(lx, LEGTOP + 2, c.legW - 1, 3, style === 'short' ? sk : bas); });
      c.px(c.lx0 + 1, LEGTOP + 3, cfg.bande); c.px(c.rx0 + c.legW - 2, LEGTOP + 3, cfg.bande);
      c.L.rect(c.lx0, SY0 + 1, c.legW * 2 + 2, 2, cfg.chaussure_style === 'pieds_nus' ? sk : cfg.chaussure);
      c.L.hline(c.lx0 - 2, c.rx0 + c.legW + 1, G, '#5a5f7a');
      c.L.ellipse(CX - 0.5, G + 2, 1.6, 1.6, '#2a2a35');
      c.px(CX - 1, G + 2, cfg.rayons);
      return;
    }
    if (style === 'jupe_longue') {
      for (y = TY + 6; y < SY0; y++) {
        k = y - TY - 6;
        var a = c.tx0 - 1 - fdiv(k, 2), b = c.tx1 + 1 + fdiv(k, 2);
        for (x = a; x <= b; x++) c.px(x, y, bas);
        c.px(b, y, fonce(bas, 0.2));
      }
      motif(c, c.tx0 - 4, TY + 7, c.tx1 + 4, SY0 - 1, cfg.motif_c, 3);
      c.L.hline(c.tx0 - 5, c.tx1 + 5, SY0 - 1, fonce(bas, 0.3));
    } else if (style === 'sarouel') {
      c.L.rect(c.tx0, LEGTOP, c.tw, 3, bas);
      c.px(CX - 1, LEGTOP + 2, fonce(bas, 0.3)); c.px(CX, LEGTOP + 2, fonce(bas, 0.3));
      [c.lx0, c.rx0].forEach(function (lx) { c.L.rect(lx, LEGTOP + 3, c.legW, 1, fonce(bas, 0.25)); });
      c.L.hline(c.tx0, c.tx1, LEGTOP + 1, cfg.bande);
    } else {
      [c.lx0, c.rx0].forEach(function (lx, i) {
        for (var y = LEGTOP; y < SY0; y++) {
          var court = style === 'short' && y >= LEGTOP + 2, col = court ? sk : bas;
          if (style === 'patchwork' && !court) {
            if ((lx + y) % 5 === 0) col = cfg.piece1; else if ((lx * 3 + y) % 7 === 1) col = cfg.piece2;
          }
          c.L.rect(lx, y, c.legW, 1, col);
          c.px(i === 0 ? lx + c.legW - 1 : lx, y, fonce(col, 0.15));
        }
        if (style === 'short') c.L.hline(lx, lx + c.legW - 1, LEGTOP + 1, cfg.bande);
        if (style === 'jogging') for (y = LEGTOP; y < SY0; y++) c.px(i === 0 ? lx : lx + c.legW - 1, y, cfg.bande);
        if (style === 'cargo') c.px(i === 0 ? lx : lx + c.legW - 1, LEGTOP + 1, clair(bas, 0.3));
      });
      if (style === 'cargo') [[c.tx0 - 1, LEGTOP], [c.tx0 - 2, LEGTOP + 1], [c.tx0 - 2, LEGTOP + 2], [c.tx0 - 1, LEGTOP + 3]].forEach(function (p) { c.px(p[0], p[1], cfg.cable); });
    }
    chaussures(c);
    if (c.lig === 'greffe') {
      [[c.lx0 - 1, -1], [c.rx0 + c.legW, 1]].forEach(function (v) { for (var k = 1; k < 5; k++) c.px(v[0] + v[1] * k, G - (k === 2 ? 1 : 0), '#6b4a2e'); });
      x = c.rx0 + c.legW + 5;
      c.px(x, G, NJ); c.px(x, G - 1, '#9aa3b8'); c.glow(x, G, NJ, 2, 0.3);
    }
  }

  function chaussures(c) {
    var cfg = c.cfg, st = cfg.chaussure_style, sh = cfg.chaussure, lace = cfg.lacet;
    [c.lx0, c.rx0].forEach(function (lx, i) {
      var a = i === 0 ? lx - 1 : lx, w = c.legW + 1;
      if (c.lig === 'lagon') {
        c.L.rect(a - (i === 0 ? 1 : 0), SY0 + 1, w + 1, 2, '#3fb8b0');
        c.px(a + (i === 0 ? 0 : w), G, '#2a8a86');
        c.L.rect(lx, SY0, c.legW, 1, c.sk);
        return;
      }
      if (st === 'pieds_nus') {
        c.L.rect(lx, SY0, c.legW, 2, c.sk);
        c.L.hline(lx, lx + c.legW - 1, SY0, lace);
        c.L.rect(a, G - 1, w, 2, c.sk);
        c.L.hline(a, a + w - 1, G, fonce(c.sk, 0.2));
        return;
      }
      if (st === 'savates') {
        c.L.rect(lx, SY0, c.legW, 2, c.sk);
        c.L.hline(lx, lx + c.legW - 1, SY0, lace);
        c.L.hline(a, a + w - 1, G, sh);
        c.L.hline(a, a + w - 1, G - 1, lace);
        return;
      }
      if (st === 'bottes') {
        c.L.rect(a, LEGTOP + 2, w, G - LEGTOP - 2, sh);
        c.L.hline(a, a + w - 1, LEGTOP + 2, clair(sh, 0.3));
        c.L.hline(a, a + w - 1, G, fonce(sh, 0.4));
        return;
      }
      var top = SY0 - (st === 'montantes' ? 1 : 0);
      c.L.rect(a, top, w, G - top, sh);
      c.L.hline(a, a + w - 1, G, st !== 'crampons' ? '#4a4a5e' : '#1b1530');
      c.px(a + (i === 0 ? w - 2 : 1), SY0, lace);
      if (st === 'montantes') { c.px(a + (i === 0 ? w - 2 : 1), SY0 - 1, lace); c.L.hline(a, a + w - 1, top, cfg.accent2); }
      if (st === 'crampons') for (var k = 0; k < w; k += 2) c.px(a + k, G + 1, '#9aa3b8');
    });
  }

  function motif(c, x0, y0, x1, y1, col, dense) {
    var r = hasard(x0 * 7 + y0);
    for (var y = y0; y <= y1; y++) for (var x = x0; x <= x1; x++) {
      if (c.L.plein(x, y) && (x * 3 + y * 5) % (dense * 3 + 1) === 0) {
        c.px(x, y, col);
        if (c.L.plein(x + 1, y) && r() < 0.5) c.px(x + 1, y, col);
        c.glow(x, y, col, 1, 0.18);
      }
    }
  }

  /* ---------- torse */
  function torse(c) {
    var cfg = c.cfg, L = c.L;
    var st = cfg.tenue;
    if (SANS_CORPS[c.lig] && st === 'aucun') return;
    var top = cfg.haut, S = fonce(top, 0.25), Hh = clair(top, 0.2);
    var tx0 = c.tx0, tx1 = c.tx1, x, y;
    var bot = TY + 8 + (st === 'tunique' ? 3 : 0);
    for (y = TY; y < bot; y++) {
      var ext = st === 'tunique' && y >= TY + 7 ? fdiv(y - TY - 6, 2) : 0;
      for (x = tx0 - Math.max(0, ext); x < tx1 + 1 + Math.max(0, ext); x++) c.px(x, y, top);
      c.px(tx1 + Math.max(0, ext), y, S);
    }
    c.px(tx0, TY, Hh);
    var acc = cfg.accent;
    if (st === 'veste') {
      [tx0, tx0 + 1, tx1 - 1, tx1].forEach(function (x) { c.px(x, TY - 1, S); });
      for (y = TY + 1; y < TY + 7; y++) { c.px(CX - 1, y, '#d8dce8'); c.px(tx0 + 1, y, acc); c.px(tx1 - 1, y, acc); }
      L.hline(tx0, tx1, TY + 7, acc); c.glow(CX, TY + 7, acc, 2, 0.2);
    } else if (st === 'maillot') {
      c.px(CX - 2, TY, acc); c.px(CX + 1, TY, acc); c.px(CX - 1, TY + 1, acc); c.px(CX, TY + 1, acc);
      L.carte(tx0 + 2, TY + 3, ['x.x', '.x.', 'x.x'], { x: cfg.embleme });
      for (y = TY + 1; y < TY + 8; y++) { c.px(tx0, y, acc); c.px(tx1, y, acc); }
    } else if (st === 'tunique') {
      L.rect(CX - 2, TY, 4, 1, c.sk); L.rect(CX - 1, TY + 1, 2, 1, c.sk);
      L.hline(CX - 2, CX + 1, TY + 2, cfg.motif_c);
      motif(c, tx0 - 2, TY + 3, tx1 + 2, bot - 1, cfg.motif_c, 3);
    } else if (st === 'sweat') {
      L.rect(CX - 3, TY + 4, 6, 3, S);
      c.px(CX - 2, TY + 1, '#f2f0ea'); c.px(CX - 2, TY + 2, '#f2f0ea'); c.px(CX + 1, TY + 1, '#f2f0ea'); c.px(CX + 1, TY + 2, '#f2f0ea');
      L.hline(tx0, tx1, TY + 7, S);
    } else if (st === 'gilet') {
      L.rect(CX - 2, TY, 4, 8, cfg.dessous);
      [[tx0 + 1, TY + 3], [tx0 + 2, TY + 3], [tx1 - 2, TY + 3], [tx1 - 1, TY + 3], [tx0 + 1, TY + 6], [tx0 + 2, TY + 6], [tx1 - 1, TY + 6], [tx1 - 2, TY + 6]].forEach(function (p) { c.px(p[0], p[1], S); });
      c.px(tx0 + 1, TY + 2, '#e8b84a'); c.px(tx0 + 1, TY + 1, '#9aa3b8');
      c.px(tx1 - 1, TY + 2, cfg.accent2); c.px(tx1 - 2, TY + 2, cfg.accent2);
      c.px(tx1 - 1, TY + 5, acc);
    } else if (st === 'debardeur') {
      L.rect(CX - 3, TY, 6, 2, c.sk);
      L.hline(tx0, tx1, TY + 4, acc); L.hline(tx0, tx1, TY + 5, cfg.accent2);
      L.hline(tx0, tx1, TY + 7, S);
    } else if (st === 'chemise') {
      L.rect(CX - 2, TY, 4, 8, cfg.dessous);
      c.px(CX - 3, TY, S); c.px(CX + 2, TY, S);
      [[tx0 + 1, TY + 2], [tx1 - 1, TY + 4], [tx0 + 2, TY + 6], [tx1 - 2, TY + 1]].forEach(function (p) { c.px(p[0], p[1], cfg.bug); });
      c.px(CX - 1, TY + 4, NOIR); c.px(CX, TY + 4, NOIR);
    } else if (st === 'combinaison') {
      L.rect(CX - 1, TY, 2, 8, acc);
      L.hline(tx0, tx1, TY + 2, '#f2f0ea');
    } else if (st === 'tshirt' || st === 'aucun') {
      L.rect(CX - 2, TY, 4, 1, SANS_CORPS[c.lig] ? top : c.sk);
      L.hline(tx0 + 1, tx1 - 1, TY + 3, cfg.motif === top ? acc : (rgb(top)[0] + rgb(top)[1] < 160 ? acc : cfg.motif));
      L.hline(tx0 + 1, tx1 - 1, TY + 5, rgb(top)[0] + rgb(top)[1] < 160 ? acc : cfg.motif);
    }
    if (cfg.o.dos === 'sac_antenne') {
      for (y = TY; y < TY + 6; y++) { c.px(tx0 + 2, y, '#3a3f58'); c.px(tx1 - 2, y, '#3a3f58'); }
      c.px(tx1 - 2, TY + 3, cfg.accent2);
    }
    if (cfg.o.epaule === 'chale') {
      var ch = cfg.chale;
      L.hline(tx0 - 2, tx1 + 2, TY, ch); L.hline(tx0 - 3, tx1 + 3, TY + 1, ch); L.hline(tx0 - 3, tx1 + 3, TY + 2, fonce(ch, 0.15));
      for (y = TY + 3; y < TY + 9; y++) { c.px(tx0 + 1, y, ch); c.px(tx0 + 2, y, y < TY + 8 ? ch : fonce(ch, 0.2)); }
      [tx0 + 1, tx0 + 2].forEach(function (x) { c.px(x, TY + 9, cfg.motif_c); });
      for (x = tx0 - 2; x < tx1 + 3; x += 3) c.px(x, TY + 1, cfg.motif_c);
    }
  }

  function peindreBras(c, cells, side) {
    var cfg = c.cfg, n = cells.length;
    var man = { longues: n - 2, courtes: 4, aucune: 0 }[cfg.manches];
    var habille = !(SANS_CORPS[c.lig] && cfg.tenue === 'aucun');
    cells.forEach(function (p, i) {
      var x = p[0], y = p[1], col;
      if (habille && i < man && !(c.lig === 'cyber' && side === 1)) {
        col = i % 2 === 0 ? cfg.haut : fonce(cfg.haut, 0.16);
        if (cfg.tenue === 'veste' && (i === man - 2 || i === man - 1)) col = cfg.accent;
      } else if (c.lig === 'esprit') { c.px(x, y, espritCouleur(y), 0.95); return; }
      else if (c.lig === 'nuee') col = nueeCouleur(c, x, y);
      else if (c.lig === 'cyber' && side === 1) {
        col = i % 2 ? '#9aa3b8' : '#b8c0d4';
        if (i === fdiv(n, 2) || i === fdiv(n, 2) + 1) col = NC;
        if (i >= n - 2) col = '#7a8296';
      } else {
        col = i % 2 === 0 ? c.sk : fonce(c.sk, 0.18);
        if (i >= n - 2 && cfg.gants) col = cfg.gants;
        if (cfg.poignet && (i === n - 4 || i === n - 3)) col = cfg.poignet;
        if (c.lig === 'lagon' && (i === n - 6 || i === n - 5) && i % 2 === 0) col = fonce(c.sk, 0.3);
        if (c.lig === 'mutant' && (i === n - 7 || i === n - 5)) col = cfg.taches;
        if (c.lig === 'greffe' && side === 0 && i >= 2 && i < n - 2) col = i % 3 ? '#7a5232' : '#5a3a22';
      }
      c.px(x, y, col);
    });
    var h = cells[cells.length - 1], hx = h[0], hy = h[1];
    if (c.lig === 'lagon') c.px(hx + (side === 0 ? -1 : 2), hy, '#3fb8b0');
    if (c.lig === 'mutant' && side === 0) { c.L.rect(hx - 1, hy, 3, 2, c.sk); c.px(hx - 1, hy + 2, c.sk); c.px(hx + 1, hy + 2, c.sk); }
  }

  /* ---------- lignées sans jambes */
  var ESPRIT = ['#ffc4e8', '#e4c8ff', '#c8d4ff', '#b4ecf4', '#c8f4e0'];
  function espritCouleur(y) { return ESPRIT[Math.max(0, Math.min(4, fdiv(y - 40, 5)))]; }
  function espritCorps(c) {
    for (var y = TY - 1; y < G + 2; y++) {
      var k = y - TY;
      var half = k < 8 ? 6 - (k === 0 ? 1 : 0) : Math.max(1, 5 - fdiv(k - 8, 2));
      var sw = k >= 8 ? [0, 1, 1, 0, -1, -1][mod(fdiv(k, 2), 6)] : 0;
      var a = k < 9 ? 1 : Math.max(0.25, 1 - (k - 8) * 0.09);
      for (var x = CX - half + sw; x < CX + half + sw; x++) {
        if (k < 11) c.px(x, y, espritCouleur(y + mod(x, 3)), a); else c.fx(x, y, espritCouleur(y), a);
      }
    }
    [[-6.5, 2, 2.6], [6, 3, 2.6], [-5, 7, 2.3], [5.5, 8, 2.2], [0, -0.5, 3]].forEach(function (e) {
      c.L.ellipse(CX + e[0], TY + e[1], e[2], e[2], null, true, function (x, y) { return espritCouleur(y + 2); });
    });
    [[-7, 6, '#ffc4e8'], [-8, 5, '#ffc4e8'], [-8, 4, '#e4c8ff'], [7, 9, '#b4ecf4'], [8, 8, '#b4ecf4'], [8, 7, '#c8d4ff'], [-5, 15, '#c8f4e0'], [-6, 14, '#c8f4e0'], [5, 16, '#e4c8ff']].forEach(function (v) {
      c.fx(CX + v[0], TY + v[1], v[2], 0.8);
    });
    c.L.hline(CX - 3, CX + 2, TY + 3, '#ffffff', true, 0.35);
  }
  function nueeCouleur(c, x, y) { var p = c.cfg.pix; return p[mod(fdiv(x, 2) + fdiv(y, 2) * 2, p.length)]; }
  function nueeCorps(c) {
    var r = hasard(3 + (c.pose.nuee || 0) * 17);
    for (var by = TY - 1; by < G + 2; by += 2) for (var bx = CX - 6; bx < CX + 6; bx += 2) {
      var k = by - TY, p = k < 9 ? 1 : Math.max(0, 1 - (k - 8) * 0.14);
      if (r() < p) {
        var col = nueeCouleur(c, bx, by), dx = k < 9 ? 0 : [-1, 0, 0, 1][Math.floor(r() * 4)];
        if (k < 9) c.L.rect(bx + dx, by, 2, 2, col); else c.F.rect(bx + dx, by, 2, 2, col, false, 0.85);
      }
    }
    [[CX - 8, TY + 12], [CX + 7, TY + 10], [CX + 9, TY + 14]].forEach(function (p) { c.F.rect(p[0], p[1], 2, 2, nueeCouleur(c, p[0], p[1]), false, 0.6); });
  }

  /* ---------- tête */
  function tete(c) {
    var cfg = c.cfg, hy = HY + c.hdy, ey = EY + c.hdy, sk = c.sk, x, y, j, i;
    var skS = fonce(sk, 0.18), skH = clair(sk, 0.18);
    for (y = hy; y < hy + 17; y++) {
      var k = y - hy, inset = k < 4 ? RR[k] : (16 - k < 4 ? RR[16 - k] : 0);
      var a = X0 + inset, b = X1 - inset;
      for (x = a; x <= b; x++) {
        var col;
        if (c.lig === 'nuee') col = mix(nueeCouleur(c, x, y), '#ffffff', 0.35);
        else if (c.lig === 'esprit') col = mix(espritCouleur(30 + fdiv(y - hy, 2)), '#ffffff', 0.25);
        else col = (x === b || (k >= 14 && x >= b - 1)) ? skS : (k === 2 && x <= a + 3 ? skH : sk);
        c.px(x, y, col);
      }
    }
    if (!SANS_CORPS[c.lig]) c.L.rect(CX - 2, TY - 1, 4, 1, skS);
    if (!SANS_CORPS[c.lig] && c.lig !== 'lagon' && cfg.coiffure !== 'capuche') {
      [X0 - 1, X1 + 1].forEach(function (xo) { c.px(xo, ey, sk); c.px(xo, ey + 1, skS); c.px(xo, ey + 2, sk); });
    }
    if (c.lig === 'lagon') {
      [[X0 - 1, -1], [X1 + 1, 1]].forEach(function (v) {
        for (var j = 0; j < 5; j++) for (var i = 0; i < 1 + (j % 3); i++) c.px(v[0] + v[1] * i, ey - 1 + j, (i + j) % 2 ? '#3fb8b0' : '#5fd8d0');
      });
      for (j = 0; j < 3; j++) { c.px(X0 + 2, ey + 4 + j, fonce(sk, 0.35)); c.px(X1 - 2, ey + 4 + j, fonce(sk, 0.35)); }
    }
    if (c.lig === 'mutant') {
      [[X0 + 2, ey + 3], [X0 + 3, ey + 4], [X1 - 2, ey + 4], [X1 - 3, ey + 3], [CX - 2, hy + 3], [CX + 1, hy + 4]].forEach(function (p) { c.px(p[0], p[1], cfg.taches); c.glow(p[0], p[1], cfg.taches, 1, 0.3); });
    }
    visage(c, ey);
  }

  function visage(c, ey) {
    var cfg = c.cfg, pose = c.pose, yeux = pose.yeux || 'ouverts';
    if (c.lig === 'esprit' && yeux === 'ouverts') yeux = 'doux';
    var eyes = [[CX - 5, -1], [CX + 3, 1]];
    var col = c.lig !== 'esprit' ? NOIR : '#5a4a98';
    eyes.forEach(function (e, idx) {
      var ex = e[0], s = e[1];
      var iris = cfg.iris;
      if (c.lig === 'mutant' && idx === 1) iris = cfg.taches;
      var lueur = c.lig === 'nuee' || (c.lig === 'mutant' && idx === 1);
      var inner = s < 0 ? ex + 1 : ex, outer = s < 0 ? ex : ex + 1;
      var cIn = s < 0 ? ex + 2 : ex - 1, cOut = s < 0 ? ex - 1 : ex + 2;
      if (yeux === 'rieurs') {
        var yb = ey + 1;
        c.px(inner, yb, col); c.px(outer, yb, col); c.px(cOut, yb + 1, col); c.px(cIn, yb + 1, col);
      } else if (yeux === 'doux') {
        c.px(cOut, ey + 2, col); c.px(cIn, ey + 2, col); c.px(inner, ey + 3, col); c.px(outer, ey + 3, col);
      } else if (yeux === 'fermes') {
        c.L.rect(ex, ey + 2, 2, 1, col);
      } else if (yeux === 'concentres') {
        c.L.rect(ex, ey + 1, 2, 1, NOIR); c.L.rect(ex, ey + 2, 2, 1, iris);
      } else if (yeux === 'grands') {
        c.L.rect(ex - (s < 0 ? 1 : 0), ey - 1, 3, 4, NOIR);
        c.L.rect(ex - (s < 0 ? 1 : 0), ey + 2, 3, 1, iris);
        c.px(inner, ey - 1, '#ffffff'); c.px(inner + (s < 0 ? 0 : 1), ey, '#ffffff');
      } else {
        c.L.rect(ex, ey, 2, 3, NOIR);
        if (lueur) { c.L.rect(ex, ey, 2, 3, clair(iris, 0.3)); c.glow(ex, ey + 1, iris, 2, 0.35); }
        else {
          c.L.rect(ex, ey + 2, 2, 1, iris);
          c.px(inner, ey, '#ffffff');
          if (yeux === 'tristes') c.px(outer, ey + 2, '#bdefff');
        }
      }
      if (c.lig === 'cyber' && idx === 1) {
        for (var x = ex - 1; x < ex + 3; x++) for (var y = ey - 1; y < ey + 4; y++) {
          if ((x === ex - 1 || x === ex + 2 || y === ey - 1 || y === ey + 3) && !(x === ex - 1 && y === ey - 1) && !(x === ex + 2 && y === ey + 3)) c.px(x, y, NC);
        }
        c.glow(ex + 2, ey + 3, NC, 1, 0.3);
      }
    });
    if (c.lig === 'cyber') [[X0 + 2, ey + 4], [X0 + 2, ey + 5], [X0 + 3, ey + 5], [X0 + 4, ey + 5]].forEach(function (p) { c.px(p[0], p[1], NC); });
    if (c.lig !== 'nuee' && !cfg.ecran) {
      var bc = c.lig !== 'esprit' ? fonce(c.hc, 0.1) : '#9a8ad8';
      eyes.forEach(function (e) {
        var ex = e[0], s = e[1], inner = s < 0 ? ex + 1 : ex, outer = s < 0 ? ex : ex + 1;
        if (yeux === 'tristes') { c.px(inner, ey - 3, bc); c.px(outer, ey - 2, bc); }
        else if (yeux === 'concentres') c.L.rect(ex, ey - 1, 2, 1, bc);
        else if (yeux === 'grands') c.L.rect(ex - (s < 0 ? 1 : 0), ey - 3, 3, 1, bc);
        else c.L.rect(ex, ey - 2, 2, 1, bc);
      });
    }
    if (c.lig !== 'nuee') [CX - 8, CX - 7, CX + 6, CX + 7].forEach(function (xj) { c.px(xj, ey + 3, '#ff7fa0', (xj === CX - 7 || xj === CX + 6) ? (pose.joues ? 0.85 : 0.6) : (pose.joues ? 0.6 : 0.4)); });
    if (pose.larme) {
      var ly = ey + 2 + pose.larme;
      c.fx(CX + 5, ly, '#7ad8ff'); c.fx(CX + 5, ly + 1, '#bdefff');
    }
    var my = ey + 4;
    var BM = { sourire: ['d..d', '.dd.'], rire: ['dddd', 'drrd', '.dd.'], triste: ['.dd.', 'd..d'], langue: ['ddd.', '..p.'], neutre: ['....', '.dd.'], o: ['.dd.', 'd..d', '.dd.'], petit: ['....', '.d..'] };
    var pal = { d: SANS_CORPS[c.lig] ? '#5a4a98' : '#5a2a35', r: '#e8606a', p: '#ff8fb0' };
    c.L.carte(CX - 2, my, BM[pose.bouche || 'sourire'] || BM.sourire, pal);
  }

  /* ---------- cheveux devant */
  function cheveuxDevant(c) {
    var cfg = c.cfg, coif = cfg.coiffure, hy = HY + c.hdy, hc = c.hc, sk = c.sk, x, y, k;
    function Hp(x, y, col) { c.px(x, y, col || hc); }
    function HR(a, b, y, col) { for (var x = a; x <= b; x++) Hp(x, y, col); }
    function casque(fr) {
      HR(X0 + 4, X1 - 4, hy - 1); HR(X0 + 2, X1 - 2, hy); HR(X0 + 1, X1 - 1, hy + 1);
      HR(X0, X1, hy + 2); HR(X0, X1, hy + 3);
      if (fr !== false) HR(X0, X1, hy + 4);
      HR(X0 + 4, X0 + 8, hy, clair(hc, 0.25));
    }
    var stub;
    if (coif === 'tresses_fibre' || coif === 'tresses') {
      casque();
      for (y = hy + 1; y < hy + 4; y++) Hp(CX - 1, y, fonce(hc, 0.35));
      for (y = hy + 5; y < hy + 9; y++) { Hp(X0, y); Hp(X1, y); }
    } else if (coif === 'degrade_circuit') {
      HR(X0 + 3, X1 - 3, hy - 2); HR(X0 + 2, X1 - 2, hy - 1); HR(X0 + 1, X1 - 1, hy); HR(X0 + 1, X1 - 1, hy + 1);
      HR(X0 + 3, X0 + 7, hy - 2, clair(hc, 0.25));
      stub = mix(sk, hc, 0.45);
      for (y = hy + 2; y < hy + 8; y++) {
        Hp(X0, y, stub); if (y < hy + 5) Hp(X0 + 1, y, stub);
        Hp(X1, y, stub); if (y < hy + 5) Hp(X1 - 1, y, stub);
      }
      [[X1 - 1, hy + 3], [X1 - 1, hy + 4], [X1 - 2, hy + 4], [X1 - 3, hy + 4], [X1 - 3, hy + 3], [X1, hy + 6]].forEach(function (p) { c.px(p[0], p[1], cfg.circuit); });
      c.glow(X1 - 2, hy + 4, cfg.circuit, 2, 0.3);
    } else if (coif === 'chignon_antenne') {
      casque();
      c.L.ellipse(CX - 0.5, hy - 3, 4, 3.2, hc);
      for (k = 1; k < 6; k++) { c.px(CX - 3 - fdiv(k, 2), hy - 4 - k, '#9aa3b8'); c.px(CX + 2 + fdiv(k, 2), hy - 4 - k, '#9aa3b8'); }
      c.px(CX - 6, hy - 10, cfg.accent); c.px(CX + 5, hy - 10, cfg.accent2);
      c.glow(CX - 6, hy - 10, cfg.accent, 2, 0.45); c.glow(CX + 5, hy - 10, cfg.accent2, 2, 0.45);
    } else if (coif === 'capuche') {
      var hcol = cfg.capuche;
      for (y = hy - 2; y < hy + 4; y++) {
        k = y - hy + 2;
        var a = X0 - 2 + Math.max(0, 3 - k), b = X1 + 2 - Math.max(0, 3 - k);
        for (x = a; x <= b; x++) c.px(x, y, hcol);
      }
      for (y = hy + 4; y < TY + 1; y++) [X0 - 2, X0 - 1, X1 + 1, X1 + 2].forEach(function (x) { c.px(x, y, hcol); });
      var bord = [];
      for (y = hy + 4; y < TY; y++) bord.push([X0 - 1, y]);
      for (x = X0; x <= X1; x++) bord.push([x, hy + 3]);
      for (y = hy + 4; y < TY; y++) bord.push([X1 + 1, y]);
      bord.forEach(function (p, i) {
        c.px(p[0], p[1], i % 5 === 0 ? cfg.accent : fonce(cfg.accent, 0.55));
        if (i % 5 === 0) c.glow(p[0], p[1], cfg.accent, 1, 0.35);
      });
    } else if (coif === 'afro_pixel') {
      casque();
    } else if (coif === 'locks_cables') {
      casque();
      for (y = hy + 5; y < hy + 9; y++) { Hp(X0, y); Hp(X1, y); }
    } else if (coif === 'lisses') {
      casque();
      HR(X0 + 1, CX - 2, hy + 5, hc);
      for (y = hy + 5; y < hy + 13; y++) { Hp(X0, y); Hp(X1, y); if (y < hy + 8) Hp(X1 - 1, y); }
    } else if (coif === 'crete_graffiti') {
      stub = mix(sk, hc, 0.4);
      HR(X0 + 4, X1 - 4, hy, stub); HR(X0 + 2, X1 - 2, hy + 1, stub);
      var cols = [NR, NR, NO, NO, NJ, NJ];
      for (y = hy - 7; y < hy + 3; y++) {
        var w = y < hy - 5 ? 2 : 3;
        for (x = CX - w + 1 - (w === 3 ? 1 : 0); x < CX + w - (w === 3 ? 1 : 0); x++) c.px(x, y, cols[Math.min(5, fdiv(y - hy + 7, 2))]);
      }
      [[CX - 3, hy + 2, NJ], [CX - 3, hy + 3, NJ], [CX + 2, hy + 2, NR], [CX + 2, hy + 3, NR], [CX + 2, hy + 4, NR]].forEach(function (p) { c.px(p[0], p[1], p[2]); });
    } else if (coif === 'boucles') {
      casque();
      for (x = X0 + 1; x < X1; x += 2) Hp(x, hy - 2, fonce(hc, 0.2));
      for (y = hy + 5; y < hy + 9; y += 2) { Hp(X0, y); Hp(X1, y); Hp(X0 - 1, y + 1); Hp(X1 + 1, y + 1); }
    } else if (coif === 'court') {
      casque();
      for (x = X0 + 1; x < X1; x += 2) Hp(x, hy - 2);
      [hy + 5, hy + 6].forEach(function (y) { Hp(X0, y); Hp(X1, y); });
    } else if (coif === 'puffs') {
      casque();
      for (y = hy + 5; y < hy + 7; y++) { Hp(X0, y); Hp(X1, y); }
    } else if (coif === 'rase') {
      stub = mix(sk, hc, 0.5);
      HR(X0 + 4, X1 - 4, hy, stub); HR(X0 + 2, X1 - 2, hy + 1, stub);
    } else if (coif === 'feuilles') {
      casque(false);
      var FE = ['#4fae5a', '#3a8a48', '#7fd06a'], kk = 0;
      for (x = X0 - 1; x < X1 + 2; x += 3, kk++) {
        var fc = FE[kk % 3];
        c.px(x, hy - 1, fc); c.px(x + 1, hy - 2, fc); c.px(x + 1, hy - 1, fc); c.px(x + 2, hy - 3, fc); c.px(x, hy, fc);
      }
      c.L.carte(X1 - 5, hy - 5, ['.j.', 'jcj', '.j.'], { j: '#f2d14b', c: '#c88a1f' });
    } else if (coif === 'volute') {
      var vc = ['#ffc4e8', '#e4c8ff', '#b4ecf4'];
      [[0, -1], [1, -2], [1, -3], [0, -4], [-1, -4], [-2, -3], [-2, -2], [-1, -6], [0, -7], [1, -7]].forEach(function (d, i) { c.px(CX + d[0], hy + d[1], vc[i % 3], i < 7 ? 0.95 : 0.7); });
    } else if (coif === 'glitch') {
      var o = c.pose.nuee || 0;
      [[X0 + 2, hy - 3 - o], [X1 - 3, hy - 4 + o], [CX - 1, hy - 5 - o], [X1 + 1, hy - 2]].forEach(function (p) { c.F.rect(p[0], p[1], 2, 2, nueeCouleur(c, p[0], p[1]), false, 0.8); });
    }
    if (c.lig === 'lagon') {
      for (k = 0, y = hy - 5; y < hy + 2; y++, k++) {
        var wf = Math.min(k + 1, 3);
        for (x = CX - 1 - fdiv(wf, 2); x < CX - 1 + fdiv(wf + 1, 2) + 1; x++) c.px(x, y, (x + y) % 2 ? '#3fb8b0' : '#5fd8d0');
      }
    }
    var gy;
    if (cfg.o.tete === 'frontale') {
      gy = hy + 4;
      HR(X0, X1, gy, '#3a3f58');
      c.L.rect(CX - 2, gy - 2, 4, 3, '#e8b84a'); c.px(CX - 1, gy - 1, '#fff6c8'); c.px(CX, gy - 1, '#fff6c8');
      c.px(CX + 1, gy - 2, '#c8ccd8');
      c.glow(CX - 1, gy - 3, '#fff6c8', 3, 0.35);
    } else if (cfg.o.tete === 'bandeau') {
      HR(X0, X1, hy + 4, cfg.bandeau);
      c.px(X0 - 1, hy + 5, cfg.bandeau); c.px(X0 - 2, hy + 6, cfg.bandeau);
    } else if (cfg.o.tete === 'soudure') {
      HR(X0, X1, hy + 1, '#3a2a1a');
      [CX - 6, CX + 2].forEach(function (ex) {
        c.L.rect(ex, hy, 4, 3, '#c8963b'); c.L.rect(ex + 1, hy + 1, 2, 1, '#ffb648'); c.px(ex + 1, hy + 1, '#fff6c8');
      });
    } else if (cfg.o.tete === 'casque_audio') {
      var cc = cfg.accent2, ey = EY + c.hdy;
      [X0 - 2, X1 + 1].forEach(function (xo) { c.L.rect(xo, ey - 1, 2, 5, cc); c.L.rect(xo, ey + 4, 2, 1, fonce(cc, 0.3)); });
      for (y = hy + 2; y < ey - 1; y++) { c.px(X0 - 1, y, '#3a3f58'); c.px(X1 + 1, y, '#3a3f58'); }
      HR(X0 + 1, X1 - 1, hy - 1, '#3a3f58');
      c.px(X0 + 1, hy, '#3a3f58'); c.px(X1 - 1, hy, '#3a3f58');
    }
  }

  /* ---------- lunettes */
  function accessoiresDevant(c) {
    var cfg = c.cfg, ey = EY + c.hdy, yeux = c.pose.yeux || 'ouverts';
    if (cfg.lunettes) {
      var mont = '#3a3f58';
      [CX - 5, CX + 3].forEach(function (ex) {
        for (var x = ex - 1; x < ex + 3; x++) for (var y = ey - 1; y < ey + 4; y++) {
          if (x === ex - 1 || x === ex + 2 || y === ey - 1 || y === ey + 3) c.px(x, y, mont);
        }
        c.px(ex + 1, ey, '#e8f6ff', 0.55);
      });
      c.px(CX - 2, ey, mont); c.px(CX - 1, ey, mont); c.px(CX, ey, mont);
      c.px(X0 - 1, ey, mont); c.px(X1 + 1, ey, mont);
    }
    if (cfg.ecran) {
      var y0 = ey - 2;
      c.L.rect(X0 - 1, y0, X1 - X0 + 3, 6, '#121a33');
      c.L.hline(X0 - 1, X1 + 1, y0, NV); c.L.hline(X0 - 1, X1 + 1, y0 + 5, NV);
      [CX - 5, CX + 3].forEach(function (ex) {
        if (yeux === 'rieurs' || yeux === 'doux') c.L.carte(ex - 1, y0 + 2, ['.xx.', 'x..x'], { x: NC });
        else if (yeux === 'tristes') c.L.carte(ex - 1, y0 + 2, ['x..x', '.xx.'], { x: NC });
        else if (yeux === 'fermes' || yeux === 'concentres') c.L.rect(ex, y0 + 3, 2, 1, NC);
        else c.L.rect(ex, y0 + 2, 2, 2, NC);
      });
      for (var x = X0; x < X1 + 1; x += 3) c.px(x, y0 + 4, fonce(NV, 0.3));
      c.glow(CX, y0 + 3, NC, 4, 0.12);
    }
  }

  /* ---------- objets tenus et posés */
  function tenu(c) {
    var cfg = c.cfg, acc = cfg.acc, h = c.BR[c.BR.length - 1], hx = h[0], hy = h[1], pose = c.brasPose, k, x, y;
    if (acc === 'pneu') {
      var cx = CX + 15.5, cy = G - 5, r = 5.8, rot = (c.pose.roue || 0) * 0.5;
      for (y = Math.trunc(cy - r) - 1; y < Math.trunc(cy + r) + 2; y++) for (x = Math.trunc(cx - r) - 1; x < Math.trunc(cx + r) + 2; x++) {
        var d = Math.hypot(x + 0.5 - cx, y + 0.5 - cy);
        if (d > 3.0 && d <= r) c.px(x, y, mod(Math.trunc(Math.atan2(y - cy, x - cx) * 4 + rot * 4), 2) ? '#2a2a35' : '#3a3a48');
        else if (d > 2.2 && d <= 3.0) c.px(x, y, cfg.accent);
      }
      c.glow(Math.trunc(cx), Math.trunc(cy), cfg.accent, 5, 0.15);
      if (pose === 'tenir') for (k = 0; k < 7; k++) c.px(hx + 1 + k * 0.55, hy - 1 + k * 0.25, '#c89a5a');
      else for (k = 0; k < 8; k++) c.px(cx - 4 + k * 0.2, cy - 4 - k, '#c89a5a');
    }
    var levee = pose === 'tenir' || pose === 'haut' || pose === 'salut' || pose === 'salut2' || pose === 'ouvert';
    objetsMain(c, acc, hx, hy, levee);
    if (acc === 'cle' && levee) {
      for (k = 0; k < 5; k++) c.px(hx + 1, hy - 1 - k, '#9aa3b8');
      c.px(hx, hy - 6, '#9aa3b8'); c.px(hx + 2, hy - 6, '#9aa3b8'); c.px(hx, hy - 7, '#9aa3b8'); c.px(hx + 2, hy - 7, '#9aa3b8');
      c.px(hx + 1, hy - 2, cfg.accent2);
    }
    if (acc === 'enceinte') {
      var x0 = c.tx0 - 13, y0 = G - 6;
      c.L.rect(x0, y0, 10, 7, '#3a3f58');
      c.L.hline(x0 + 2, x0 + 7, y0 - 1, '#9aa3b8'); c.px(x0 + 2, y0 - 2, '#9aa3b8'); c.px(x0 + 7, y0 - 2, '#9aa3b8'); c.L.hline(x0 + 2, x0 + 7, y0 - 3, '#9aa3b8');
      [x0 + 2.5, x0 + 7.5].forEach(function (cxx) { c.L.ellipse(cxx, y0 + 3.5, 2, 2, '#1b1f33'); c.px(cxx - 0.5, y0 + 3, cfg.accent2); });
      var base = [2, 4, 3, 5, 2], dec = c.pose.egaliseur || 0;
      var hs = base.map(function (v, i) { return 1 + mod(v + dec * (i + 2), 5); });
      var cols = [NC, NV, NR, NJ, NC];
      hs.forEach(function (hh, i) { for (var k = 0; k < hh; k++) c.fx(x0 + 1 + i * 2, y0 - 5 - k, cols[i], 0.9 - k * 0.12); });
    }
    if (acc === 'bombe' && (pose === 'tenir' || pose === 'haut' || pose === 'salut' || pose === 'salut2' || pose === 'ouvert')) {
      x = hx + 1; y = hy - 4;
      c.L.rect(x, y, 2, 4, '#e8e0d0'); c.L.rect(x, y - 1, 2, 1, cfg.accent); c.px(x, y + 1, cfg.accent);
      for (k = 0; k < 14; k++) {
        var rr = hasard(k + 1 + (c.pose.brume || 0) * 31);
        c.fx(x + 3 + Math.floor(rr() * 6), y - 2 + Math.floor(rr() * 6) - 2, [NR, NJ, NC][Math.floor(rr() * 3)], 0.4 + rr() * 0.4);
      }
    }
    if (c.pose.tablette) {
      var tx = CX - 5, ty = TY + 3;
      c.L.rect(tx, ty, 10, 6, '#3a3f58');
      c.L.rect(tx + 1, ty + 1, 8, 4, '#121a33');
      var lignes = [[3, 5, 2], [5, 2, 4], [2, 6, 3]][(c.pose.tablette - 1) % 3];
      lignes.forEach(function (l, i) { c.L.hline(tx + 2, tx + 1 + l, ty + 2 + i, i === 1 ? cfg.accent2 : cfg.accent); });
      c.glow(CX, ty + 2, cfg.accent, 3, 0.15);
      [c.BL, c.BR].forEach(function (cells) {
        for (var i = cells.length - 2; i < cells.length; i++) c.px(cells[i][0], cells[i][1], SANS_CORPS[c.lig] ? (c.lig === 'esprit' ? espritCouleur(cells[i][1]) : nueeCouleur(c, cells[i][0], cells[i][1])) : (cfg.gants || c.sk));
      });
    }
  }

  /* ════════════════════════════════════════════
     LES OBJETS, PAR EMPLACEMENTS
     tête, visage, dos, main, épaules, autour : un objet par emplacement,
     cumulables, portables par tous les avatars. Dessins originaux.
     ════════════════════════════════════════════ */
  Calque.prototype.ellipseA = function (cx, cy, rx, ry, c, a) {
    for (var y = Math.trunc(cy - ry) - 1; y < Math.trunc(cy + ry) + 2; y++) for (var x = Math.trunc(cx - rx) - 1; x < Math.trunc(cx + rx) + 2; x++) {
      var dx = (x + 0.5 - cx) / rx, dy = (y + 0.5 - cy) / ry;
      if (dx * dx + dy * dy <= 1) this.px(x, y, typeof c === 'function' ? c(x, y) : c, true, a);
    }
  };
  var GECKO = ['..g..', '.ggg.', 'g.g.g', '..g..', 'g.g.g', '...gg'];

  function objetsDerriere(c) {
    var o = c.cfg.o, cfg = c.cfg, n = c.pose.n || 0, x, y, k, r;
    if (o.autour === 'pixels') {
      r = hasard(7);
      for (k = 0; k < 10; k++) {
        var px_ = 4 + Math.floor(r() * 40), py = 12 + mod(Math.floor(r() * 44) + n * 3, 46);
        for (var t = 0; t < 3; t++) c.fx(px_, py - t * 2, t ? '#2fbf5a' : NG, 1 - t * 0.3);
      }
    }
    if (o.dos === 'ailes_fee') {
      var f = n % 2 ? 1 : 0, wc = '#d4f4ff';
      [[c.tx0 - 4, -1], [c.tx1 + 5, 1]].forEach(function (w) {
        c.L.ellipseA(w[0] + w[1], TY - 6 + f * 0.5, 3.8, 5.4 - f, wc, 0.75);
        c.L.ellipseA(w[0], TY + 2, 2.6, 2.8 - f * 0.5, wc, 0.75);
        for (k = 0; k < 4; k++) c.px(w[0] + w[1] * (k - 2) * 0.5, TY - 2 - k * 2, '#a8e0ff');
        c.px(w[0] + w[1] * 1.5, TY - 10 + f, cfg.accent); c.glow(rnd(w[0] + w[1] * 1.5), TY - 10 + f, cfg.accent, 2, 0.35);
      });
    }
    if (o.dos === 'cape') {
      var cape = fonce(cfg.accent2, 0.5);
      for (y = TY - 1; y < SY0; y++) {
        k = y - TY + 1;
        var half = c.tw / 2 + 1 + fdiv(k, 3), flot = y > LEGTOP && n % 2 ? 1 : 0;
        for (x = CX - half - flot; x < CX + half + flot; x++) c.px(x, y, (x === CX - half - flot || x === CX + half + flot - 1) ? fonce(cape, 0.25) : cape);
      }
    }
    if (o.dos === 'jetpack') {
      [c.tx0 - 4, c.tx1 + 2].forEach(function (x0) {
        c.L.rect(x0, TY - 3, 3, 9, '#c8963b');
        c.L.rect(x0, TY - 3, 1, 9, '#e8b84a');
        c.L.rect(x0, TY - 4, 3, 1, '#9aa3b8'); c.L.rect(x0, TY + 6, 3, 1, '#5a5f7a');
        for (var j = 0; j < 3; j++) c.fx(x0 + 1 + (j % 2 ? (n % 2 ? 1 : -1) : 0), TY + 8 + j * 2 + (n % 2), '#f4f6ff', 0.65 - j * 0.18);
      });
    }
    if (o.dos === 'drapeau') {
      var pole = c.tx1 + 3, haut = HY - 10;
      for (y = haut; y < TY + 6; y++) c.px(pole, y, '#9a7a52');
      c.px(pole, haut - 1, cfg.accent);
      for (var i = 0; i < 12; i++) {
        var dy = mod(i + n * 2, 6) < 3 ? 0 : 1;
        for (y = 0; y < 8; y++) c.px(pole + 1 + i, haut + y + dy, '#1f1a24');
      }
      GECKO.forEach(function (row, j) {
        for (var i = 0; i < 5; i++) if (row.charAt(i) === 'g') { var X = pole + 4 + i; c.px(X, haut + 1 + j + (mod(X - pole - 1 + n * 2, 6) < 3 ? 0 : 1), '#5fd06a'); }
      });
    }
  }

  function objetsEpaule(c) {
    var o = c.cfg.o, cfg = c.cfg, n = c.pose.n || 0, y;
    if (o.epaule === 'echarpe') {
      var e = mix(cfg.accent2, '#c8453d', 0.45);
      c.L.hline(c.tx0 - 1, c.tx1 + 1, TY - 1, e); c.L.hline(c.tx0 - 1, c.tx1 + 1, TY, fonce(e, 0.2));
      for (y = TY + 1; y < TY + 7; y++) { c.px(c.tx1 - 3, y, y % 2 ? e : cfg.accent); c.px(c.tx1 - 2, y, y % 2 ? fonce(e, 0.2) : cfg.accent); }
    }
    if (o.epaule === 'drone') {
      var dx = c.tx0 - 9, dy = TY - 12 + (n % 2);
      c.L.rect(dx, dy, 5, 2, '#3a3f58'); c.px(dx + 2, dy, cfg.accent);
      c.px(dx - 1, dy - 1, '#5a5f7a'); c.px(dx + 5, dy - 1, '#5a5f7a');
      c.L.hline(dx - 2 - (n % 2), dx, dy - 2, '#e8f0ff'); c.L.hline(dx + 4, dx + 6 + (n % 2), dy - 2, '#e8f0ff');
      c.px(dx + 1, dy + 2, '#5a5f7a'); c.px(dx + 3, dy + 2, '#5a5f7a');
      c.glow(dx + 2, dy, cfg.accent, 2, 0.3);
    }
  }

  function objetsTete(c) {
    var o = c.cfg.o, cfg = c.cfg, hy = HY + c.hdy, n = c.pose.n || 0, x, y, k;
    if (o.tete === 'chapeau_paille' || o.tete === 'bonnet' || o.tete === 'casquette') {
      /* le chapeau remplace ce qui dépasse du crâne */
      for (y = hy - 14; y < hy; y++) for (x = X0 - 4; x <= X1 + 4; x++) { c.L.ote(x, y); c.L.m.delete(y * K + x); c.F.ote(x, y); }
    }
    if (o.tete === 'chapeau_paille') {
      for (y = hy - 5; y < hy + 1; y++) {
        var ins = y === hy - 5 ? 1 : 0;
        for (x = X0 + 3 + ins; x <= X1 - 3 - ins; x++) c.px(x, y, (x + y) % 2 ? '#e8c86a' : '#d8b450');
      }
      c.L.hline(X0 + 3, X1 - 3, hy - 1, '#c8453d');
      for (x = X0 - 3; x <= X1 + 3; x++) c.px(x, hy + 1, (x + hy) % 2 ? '#e8c86a' : '#d8b450');
      for (x = X0 - 4; x <= X1 + 4; x++) c.px(x, hy + 2, '#c89a3a');
    }
    if (o.tete === 'bonnet') {
      var tri = mix(cfg.accent2, '#2a2f4a', 0.4), W = [5, 7, 8, 9, 9, 9, 9];
      for (k = 0; k < 7; k++) { y = hy - 3 + k; for (x = CX - W[k]; x < CX + W[k]; x++) c.px(x, y, k >= 5 ? (x % 2 ? fonce(tri, 0.25) : tri) : tri); }
      c.L.ellipse(CX - 0.5, hy - 5, 2.4, 2.4, '#f2f0ea');
      c.px(CX - 1, hy - 6, '#ffffff');
    }
    if (o.tete === 'couronne_fleurs') {
      c.L.hline(X0, X1, hy + 1, '#3a8a48'); c.L.hline(X0 + 1, X1 - 1, hy, '#4fae5a');
      var FL = [['#f2d14b', '#c88a1f'], ['#fff4d8', '#f2b84b'], ['#ff9ac8', '#f2d14b']];
      [X0 - 1, X0 + 4, CX - 1, X1 - 5, X1 - 1].forEach(function (fx_, i) {
        var p = FL[i % 3];
        c.L.carte(fx_, hy - 1, ['.p.', 'pcp', '.p.'], { p: p[0], c: p[1] });
      });
    }
    if (o.tete === 'antennes') {
      c.L.hline(X0 + 2, X1 - 2, hy - 1, '#3a3f58');
      [[-1, CX - 5, cfg.accent], [1, CX + 4, cfg.accent2]].forEach(function (a) {
        var bx = a[1], b = (n + (a[0] > 0 ? 1 : 0)) % 2;
        for (var k = 0; k < 6; k++) c.px(bx + a[0] * fdiv(k, 2), hy - 2 - k, k % 2 ? '#9aa3b8' : '#5a5f7a');
        var tx = bx + a[0] * 3, ty = hy - 10 + b;
        c.L.rect(tx - (a[0] < 0 ? 1 : 0), ty, 2, 2, a[2]); c.glow(tx, ty, a[2], 2, 0.4);
      });
    }
    if (o.tete === 'casquette') {
      var cq = cfg.haut;
      [[X0 + 3, X1 - 3], [X0 + 1, X1 - 1], [X0, X1], [X0, X1], [X0, X1]].forEach(function (r, k) { c.L.hline(r[0], r[1], hy - 2 + k, k === 0 ? clair(cq, 0.2) : cq); });
      c.L.hline(X0 - 1, X1 + 1, hy + 3, fonce(cq, 0.35));
      c.L.hline(X0 - 2, X1 + 2, hy + 4, fonce(cq, 0.5));
      c.L.carte(CX - 2, hy - 1, ['x.x', '.x.', 'x.x'], { x: cfg.accent });
    }
  }

  function objetsVisage(c) {
    var o = c.cfg.o, cfg = c.cfg, ey = EY + c.hdy, n = c.pose.n || 0, x, y;
    if (o.visage === 'visiere') {
      c.L.hline(X0 - 1, CX, ey - 2, '#3a3f58');
      for (y = ey - 1; y < ey + 3; y++) for (x = CX + 1; x <= X1 + 1; x++) c.px(x, y, cfg.accent, 0.45);
      c.L.hline(CX + 1, X1 + 1, ey - 2, cfg.accent);
      c.L.hline(CX + 1, X1 + 1, ey + 3, fonce(cfg.accent, 0.45));
      c.glow(X1, ey, cfg.accent, 3, 0.25);
    }
    if (o.visage === 'masque') {
      var mc = mix(cfg.accent2, '#ffffff', 0.25), bord = fonce(cfg.accent2, 0.35);
      for (y = ey - 1; y < ey + 4; y++) for (x = X0 + 1; x <= X1 - 1; x++) {
        var oeil = (x === CX - 5 || x === CX - 4 || x === CX + 3 || x === CX + 4) && y >= ey && y <= ey + 2;
        if (oeil || (x >= CX - 2 && x <= CX + 1 && y >= ey + 2)) continue;
        if ((y === ey + 3) && (x <= X0 + 3 || x >= X1 - 3)) continue;
        c.px(x, y, (y === ey + 3 || y === ey - 1) ? bord : mc);
      }
      c.px(X0, ey - 2, mc); c.px(X0 - 1, ey - 3, bord); c.px(X1, ey - 2, mc); c.px(X1 + 1, ey - 3, bord);
      c.px(CX - 1, ey - 1, cfg.accent); c.px(CX, ey - 1, cfg.accent);
    }
    if (o.visage === 'implant') {
      c.L.rect(X0 + 1, ey - 5, 3, 2, '#5a5f7a');
      c.px(X0 + 2, ey - 5, n % 2 ? cfg.accent2 : cfg.accent);
      c.glow(X0 + 2, ey - 5, n % 2 ? cfg.accent2 : cfg.accent, 2, 0.35);
      c.px(X0, ey - 3, '#9aa3b8'); c.px(X0, ey - 2, '#9aa3b8'); c.px(X0 - 1, ey - 1, '#9aa3b8');
    }
    if (o.visage === 'peinture') {
      [[X0 + 1, X0 + 3], [X1 - 3, X1 - 1]].forEach(function (r) { c.L.hline(r[0], r[1], ey + 3, cfg.accent); c.L.hline(r[0], r[1], ey + 5, cfg.accent2); });
      c.px(CX - 1, ey - 4, cfg.accent); c.px(CX, ey - 4, cfg.accent);
    }
    if (o.visage === 'pansement') {
      c.L.rect(X1 - 4, ey + 3, 4, 2, '#f0c89a'); c.px(X1 - 3, ey + 3, '#d8a878'); c.px(X1 - 2, ey + 4, '#d8a878');
    }
  }

  function objetsMain(c, acc, hx, hy, levee) {
    var cfg = c.cfg, n = c.pose.n || 0;
    if (acc === 'ballon') {
      var bx = c.tx0 - 5.5, by = G - 2.5;
      c.L.ellipse(bx, by, 3.3, 3.3, '#f2f0ea');
      c.L.carte(Math.round(bx) - 2, Math.round(by) - 2, ['.a..', 'aa.b', '..bb', '.b..'], { a: cfg.accent, b: cfg.accent2 });
    }
    if (!levee) return;
    if (acc === 'mangue') {
      c.L.ellipse(hx + 1.5, hy - 2, 2.2, 2.8, null, true, function (x, y) { return y < hy - 3 ? '#e8503a' : (y < hy - 1 ? '#f2802a' : '#f2b02a'); });
      c.px(hx + 2, hy - 5, '#3fae4a'); c.px(hx + 3, hy - 6, '#3fae4a');
    }
    if (acc === 'baton_lumineux') {
      c.L.rect(hx, hy - 7, 2, 7, cfg.accent); c.L.rect(hx, hy - 6, 1, 5, clair(cfg.accent, 0.6));
      c.glow(hx, hy - 4, cfg.accent, 3, n % 2 ? 0.5 : 0.3);
    }
    if (acc === 'lanterne') {
      c.px(hx + 1, hy + 1, '#9aa3b8');
      c.L.rect(hx, hy + 2, 3, 1, '#3a3f58'); c.L.rect(hx, hy + 3, 3, 3, '#ffd86a'); c.px(hx + 1, hy + 4, '#fff6c8'); c.L.rect(hx, hy + 6, 3, 1, '#3a3f58');
      c.glow(hx + 1, hy + 4, '#ffd86a', 4, n % 2 ? 0.35 : 0.25);
    }
  }

  function objetsAutour(c) {
    var o = c.cfg.o, cfg = c.cfg, n = c.pose.n || 0, i;
    if (o.autour === 'lucioles') {
      for (i = 0; i < 5; i++) {
        var a = i * 1.2566 + n * 0.45, x = CX + Math.cos(a) * 20, y = 38 + Math.sin(a) * 15;
        c.px(x, y, '#fff27a'); c.px(x + 1, y, '#fff27a'); c.glow(rnd(x), rnd(y), NJ, 3, 0.4);
      }
    }
    if (o.autour === 'bulles') {
      [[5, 0], [40, 11], [8, 23], [38, 30]].forEach(function (b) {
        var y = 56 - mod(n * 4 + b[1], 40);
        [[1, 0], [0, 1], [2, 1], [1, 2]].forEach(function (d) { c.px(b[0] + d[0], y + d[1], '#7ad8ff'); });
        c.fx(b[0] + 1, y + 1, '#e8f8ff', 0.8);
      });
    }
    if (o.autour === 'petales') {
      [[6, 0], [40, 9], [12, 18], [35, 27], [3, 35], [43, 4]].forEach(function (p, k) {
        var y = 12 + mod(n * 5 + p[1], 46), x = p[0] + (mod(fdiv(y, 4), 2) ? 1 : 0);
        c.px(x, y, k % 2 ? '#f2d14b' : '#fff1b0'); c.px(x + 1, y, '#f2d14b');
      });
    }
    if (o.autour === 'notes') {
      [[5, 30], [39, 22], [9, 16]].forEach(function (p, k) {
        var y = p[1] - mod(n * 2 + k * 3, 8);
        c.L.carte(p[0], y, ['.xx', '.x.', '.x.', 'xx.'], { x: k % 2 ? cfg.accent2 : cfg.accent });
      });
    }
  }

  function aura(c) {
    var n = c.pose.n || 0, L = c.L, r1 = L.anneau(), r2 = new Set();
    r1.forEach(function (k) { [1, -1, K, -K].forEach(function (d) { var q = k + d; if (!L.m.has(q) && !r1.has(q)) r2.add(q); }); });
    r1.forEach(function (k) { c.F.px(k % K, Math.floor(k / K), c.cfg.accent, false, n % 2 ? 0.55 : 0.4); });
    r2.forEach(function (k) { var x = k % K; if (x > 0 && x < W - 1) c.F.px(x, Math.floor(k / K), c.cfg.accent, false, 0.18); });
  }

  /* ---------- effets (au-dessus, avec contour) */
  var ZP = ['xxx', '..x', '.x.', 'xxx'], ZG = ['xxxx', '...x', '..x.', '.x..', 'xxxx'];
  function effets(fx, main) {
    var E = new Calque(72, 64);
    (fx || []).forEach(function (f) {
      var n = f[1] || 0;
      if (f[0] === 'zzz') {
        if (n >= 1) E.carte(CX + 9, 22, ZP, { x: '#d8ecff' });
        if (n >= 2) E.carte(CX + 13, 16, ZG, { x: '#d8ecff' });
        if (n >= 3) E.carte(CX + 18, 10, ZG, { x: '#d8ecff' });
      } else if (f[0] === 'nuage') {
        var nf = function (x, y) { return y > 14 ? '#9aa3b8' : '#c8d0e0'; };
        E.ellipse(CX - 3.5, 13, 3.6, 2.8, null, true, nf); E.ellipse(CX + 0.5, 11.5, 4, 3.4, null, true, nf); E.ellipse(CX + 4.5, 13.5, 3.2, 2.4, null, true, nf);
        [[CX - 4, 0], [CX, 1], [CX + 4, 2]].forEach(function (g) {
          var y = 18 + mod(n + g[1] * 2, 6);
          if (y < 23) { E.px(g[0], y, '#7ad8ff'); E.px(g[0], y + 1, '#7ad8ff'); }
        });
      } else if (f[0] === 'etincelles') {
        var pts = n % 2 ? [[7, 20, NJ], [40, 16, NR], [12, 11, NC], [36, 30, NJ]] : [[9, 14, NC], [38, 22, NJ], [17, 10, NR], [4, 30, NR]];
        pts.forEach(function (p) { E.px(p[0], p[1], p[2]); E.px(p[0] - 1, p[1], p[2]); E.px(p[0] + 1, p[1], p[2]); E.px(p[0], p[1] - 1, p[2]); E.px(p[0], p[1] + 1, p[2]); E.px(p[0], p[1], '#ffffff'); });
      } else if (f[0] === 'bulle') {
        [[CX + 9, 24], [CX + 12, 21], [CX + 15, 18]].forEach(function (p, i) { if (i < n) E.rect(p[0], p[1], 2, 2, '#e8f0ff'); });
      } else if (f[0] === 'vent' && main) {
        var hx = main[0] + 3, hy = main[1];
        var dx = n % 2 ? 1 : 0;
        E.px(hx + dx, hy - 2, '#e8f0ff'); E.px(hx + dx, hy - 1, '#e8f0ff');
        E.px(hx + 2 + dx, hy, '#e8f0ff'); E.px(hx + 2 + dx, hy + 1, '#e8f0ff');
      }
    });
    E.contour(CONTOUR);
    return E;
  }

  /* ════════════════════════════════════════════
     LE MARGOUILLAT VERT À TURBINE
     Rastérisé par couverture (sur-échantillonnage), à 16, 24, 32 ou 48 px.
     ════════════════════════════════════════════ */
  var M_VERT = '#3fbf4a', M_VERT_S = '#2a8a3a', M_VENTRE = '#c8f0a0', M_ROUGE = '#e8403a', M_DOIGT = '#9af07a';
  var M_ANNEAU = '#7a8296', M_PALE = '#3ff0ff', M_MOYEU = '#e8ff3a';

  function distSeg(px, py, ax, ay, bx, by) {
    var vx = bx - ax, vy = by - ay, l = vx * vx + vy * vy, t = l ? ((px - ax) * vx + (py - ay) * vy) / l : 0;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(px - ax - t * vx, py - ay - t * vy);
  }
  function dedans(f, u, v) {
    if (f[0] === 'e') { var dx = (u - f[1]) / f[3], dy = (v - f[2]) / f[4]; return dx * dx + dy * dy <= 1; }
    var pts = f[1], r = f[2] / 2;
    for (var i = 0; i + 1 < pts.length; i++) if (distSeg(u, v, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) <= r) return true;
    return pts.length === 1 && Math.hypot(u - pts[0][0], v - pts[0][1]) <= r;
  }
  function couverture(S, Wb, Hb, formes) {
    var set = new Set(), SS = 6;
    for (var y = 0; y < Hb; y++) for (var x = 0; x < Wb; x++) {
      var n = 0;
      for (var j = 0; j < SS; j++) for (var i = 0; i < SS; i++) {
        var u = (x + (i + 0.5) / SS) / S, v = (y + (j + 0.5) / SS) / S;
        for (var f = 0; f < formes.length; f++) if (dedans(formes[f], u, v)) { n++; break; }
      }
      if (n / (SS * SS) > 0.45) set.add(y * K + x);
    }
    return set;
  }
  function modeleDessus(etat) {
    var tail = etat !== 'triste' ? [[0.5, 0.58], [0.5, 0.66], [0.53, 0.72], [0.6, 0.76]] : [[0.5, 0.58], [0.5, 0.68], [0.5, 0.76], [0.5, 0.8]];
    return {
      W: 1, H: 1, tc: etat !== 'triste' ? [0.66, 0.84] : [0.5, 0.9], tr: 0.085,
      corps: [['e', 0.5, 0.15, 0.11, 0.12], ['e', 0.5, 0.4, 0.1, 0.21], ['l', tail, 0.07],
        ['l', [[0.45, 0.3], [0.33, 0.27], [0.28, 0.19]], 0.055], ['l', [[0.55, 0.3], [0.67, 0.27], [0.72, 0.19]], 0.055],
        ['l', [[0.45, 0.52], [0.33, 0.56], [0.29, 0.65]], 0.06], ['l', [[0.55, 0.52], [0.67, 0.56], [0.71, 0.65]], 0.06]],
      doigts: [[[0.28, 0.19], -1, -1], [[0.72, 0.19], 1, -1], [[0.29, 0.65], -1, 1], [[0.71, 0.65], 1, 1]],
      yeux: [[0.43, 0.12], [0.57, 0.12]], taches: [[0.5, 0.32], [0.47, 0.41], [0.53, 0.47], [0.5, 0.24]]
    };
  }
  function modeleProfil(etat) {
    var tail = etat === 'triste' ? [[0.34, 0.63], [0.24, 0.67], [0.17, 0.71]] : [[0.34, 0.6], [0.24, 0.58], [0.17, 0.5], [0.15, 0.4]];
    return {
      W: 1, H: 0.8, tc: etat === 'triste' ? [0.1, 0.72] : [0.14, 0.3], tr: 0.1, ventre: 0.61,
      corps: [['e', 0.53, 0.57, 0.2, 0.07], ['e', 0.8, 0.52, 0.1, 0.085], ['e', 0.87, 0.55, 0.06, 0.05], ['l', tail, 0.065],
        ['l', [[0.66, 0.6], [0.7, 0.67], [0.74, 0.72]], 0.05], ['l', [[0.4, 0.6], [0.36, 0.67], [0.32, 0.72]], 0.05]],
      doigts: [[[0.74, 0.72], 1, 1], [[0.32, 0.72], -1, 1]],
      yeux: [[0.82, 0.48]], taches: [[0.47, 0.52], [0.55, 0.515], [0.62, 0.53]]
    };
  }
  var _cacheCouv = {};
  function margSprite(vue, S, etat, rot) {
    var M = vue === 'dessus' ? modeleDessus(etat) : modeleProfil(etat);
    var Wb = Math.max(4, Math.round(M.W * S)), Hb = Math.max(4, Math.round(M.H * S));
    var C = new Calque(Wb, Hb), F = new Calque(Wb, Hb);
    var cle = vue + S + etat;
    var corps = _cacheCouv[cle] || (_cacheCouv[cle] = couverture(S, Wb, Hb, M.corps));
    var tc = M.tc, tr = M.tr;
    var turb = _cacheCouv[cle + 't'] || (_cacheCouv[cle + 't'] = couverture(S, Wb, Hb, [['e', tc[0], tc[1], tr + 0.015, tr + 0.015]]));
    corps.forEach(function (k) { var x = k % K, y = (k - x) / K; C.px(x, y, vue === 'profil' && y >= M.ventre * S ? M_VENTRE : M_VERT); });
    corps.forEach(function (k) { var x = k % K, y = (k - x) / K; if (!corps.has(k + 1)) C.px(x, y, M_VERT_S); });
    M.doigts.forEach(function (dg) {
      var x = rnd(dg[0][0] * S - 0.5), y = rnd(dg[0][1] * S - 0.5), sx = dg[1], sy = dg[2];
      C.px(x + sx, y + (S >= 32 ? sy : 0), M_DOIGT);
    });
    var cx = tc[0] * S, cy = tc[1] * S, r = tr * S + 0.2;
    turb.forEach(function (k) { var x = k % K, y = (k - x) / K; C.px(x, y, Math.hypot(x + 0.5 - cx, y + 0.5 - cy) > r - 1.1 ? M_ANNEAU : '#1f2a44'); });
    var pal = etat !== 'triste' ? M_PALE : '#9aa3b8', hub = etat !== 'triste' ? M_MOYEU : '#c8ccd8';
    if (S >= 32) {
      for (var kk = 0; kk < 3; kk++) {
        var a = (rot || 0) - Math.PI / 2 + kk * 2.094;
        (S < 48 ? [1.2] : [1.2, 2.2]).forEach(function (t) { C.px(cx - 0.5 + Math.cos(a) * t, cy - 0.5 + Math.sin(a) * t, pal); });
      }
    }
    C.px(cx - 0.5, cy - 0.5, hub);
    M.yeux.forEach(function (e) {
      var x = rnd(e[0] * S - 0.5), y = rnd(e[1] * S - 0.5);
      if (etat === 'content' && S >= 24) { C.px(x - 1, y + 1, NOIR); C.px(x, y, NOIR); C.px(x + 1, y + 1, NOIR); }
      else if (S >= 32 && vue === 'profil') { C.rect(x, y, 2, 2, NOIR); C.px(x, y, '#ffffff'); }
      else C.px(x, y, NOIR);
      if (etat === 'triste' && S >= 24) F.px(x + 1, y + 2, '#7ad8ff', false);
    });
    if (vue === 'profil' && S >= 24) {
      var mx = rnd(0.9 * S - 0.5), my = rnd(0.565 * S - 0.5);
      if (etat === 'triste') { C.px(mx - 1, my, NOIR); C.px(mx - 2, my + 1, NOIR); }
      else { C.px(mx - 2, my, NOIR); C.px(mx - 1, my + (etat === 'content' ? 1 : 0), NOIR); C.px(mx, my, NOIR); }
    }
    C.contour(CONTOUR);
    var xa = 1e9, xb = -1, ya = 1e9, yb = -1;
    [C, F].forEach(function (L) { L.p.forEach(function (v, k) { var x = k % K, y = (k - x) / K; xa = Math.min(xa, x); xb = Math.max(xb, x); ya = Math.min(ya, y); yb = Math.max(yb, y); }); });
    var R = new Calque(xb - xa + 3, yb - ya + 3);
    R.sur(C, 1 - xa, 1 - ya); R.sur(F, 1 - xa, 1 - ya, false);
    return R;
  }
  function orienter(C, sens, miroir) {
    var w = C.w, h = C.h, R = C;
    if (sens === 'descendant') R = C.transformer(function (x, y) { return [w - 1 - x, h - 1 - y]; });
    else if (sens === 'plafond') R = C.transformer(function (x, y) { return [x, h - 1 - y]; });
    if (miroir) { var w2 = R.w; R = R.transformer(function (x, y) { return [w2 - 1 - x, y]; }); }
    return R;
  }
  function encreNoire(C) {
    var R = new Calque(C.w, C.h);
    C.p.forEach(function (v, k) {
      if (v[1] < 1) return;
      R.p.set(k, [(v[0] === NOIR || v[0] === '#ffffff' || v[0] === M_PALE || v[0] === M_MOYEU) ? '#ffffff' : '#000000', 1]);
      R.m.add(k);
    });
    return R;
  }

  /* ════════════════════════════════════════════
     LES COMPAGNONS (gabarit compact 26 x 24)
     ════════════════════════════════════════════ */
  var CW = 26, CH = 24;
  function finComp(C, F, etat, n) {
    C.contour(CONTOUR);
    var R = new Calque(CW, CH);
    var dy = etat === 'content' ? -1 : (etat === 'triste' ? 1 : 0);
    R.sur(C, 0, dy); R.sur(F, 0, dy, false);
    if (etat === 'content') {
      (n % 2 ? [[1, 3, NJ], [2, 2, NJ], [24, 5, NR], [23, 4, NR], [3, 6, NC]] : [[2, 5, NJ], [3, 4, NJ], [23, 2, NR], [24, 3, NR], [22, 7, NC]]).forEach(function (p) { R.px(p[0], p[1], p[2], false); });
    }
    return R;
  }
  function yeuxComp(C, F, pts, etat, taille) {
    pts.forEach(function (p) {
      var x = p[0], y = p[1];
      if (etat === 'content') { C.px(x - 1, y + 1, NOIR); C.px(x, y, NOIR); C.px(x + 1, y, NOIR); C.px(x + 2, y + 1, NOIR); }
      else if (etat === 'dort') { C.rect(x, y + 1, 2, 1, NOIR); }
      else { C.rect(x, y, 2, taille, NOIR); C.px(x, y, '#ffffff'); }
    });
    if (etat === 'triste') { var l = pts[pts.length - 1]; F.px(l[0] + 2, l[1] + taille, '#7ad8ff', false); F.px(l[0] + 2, l[1] + taille + 1, '#bdefff', false); }
  }
  function maki(etat, n) {
    var C = new Calque(CW, CH), F = new Calque(CW, CH);
    var br = '#8a6a4a', brC = '#a8845e', joue = '#e8d8b8', masque = '#3a2a2a', tr = etat === 'triste';
    var queue = tr ? [[17, 21], [19, 22], [21, 22], [23, 22]] : (n % 2 ? [[17, 21], [19, 20], [21, 18], [22, 15], [23, 12], [22, 9], [20, 8]] : [[17, 21], [19, 20], [21, 18], [22, 15], [22, 12], [21, 9], [19, 8]]);
    queue.forEach(function (p) { C.ellipse(p[0], p[1], 1.8, 1.8, brC); });
    C.ellipse(11.5, 17.5, 6.2, 5.2, br); C.ellipse(11.5, 18.5, 3.5, 3.2, joue);
    C.ellipse(11.5, 9, 7.2, 5.8, '#9a8a7a');
    (tr ? [[4, 6], [5, 5], [18, 6], [17, 5]] : [[4, 4], [5, 3], [18, 4], [17, 3]]).forEach(function (p) { C.px(p[0], p[1], '#9a8a7a'); });
    C.ellipse(5, 11, 2.4, 2.4, joue); C.ellipse(18, 11, 2.4, 2.4, joue);
    C.ellipse(11.5, 9.6, 4.8, 3.9, masque);
    [8, 13].forEach(function (ex) {
      if (etat === 'content') { C.px(ex, 9, '#f0a030'); C.px(ex + 1, 8, '#f0a030'); C.px(ex + 2, 9, '#f0a030'); }
      else if (etat === 'dort') C.hline(ex, ex + 2, 9, '#f0a030');
      else {
        C.rect(ex, 7 + (tr ? 1 : 0), 3, 3 - (tr ? 1 : 0), '#f0a030');
        C.rect(ex + 1, 8, 1, 2, '#1b1530');
        C.px(ex, 7 + (tr ? 1 : 0), '#fff6c8');
      }
    });
    if (tr) { F.px(16, 10, '#7ad8ff', false); F.px(16, 11, '#bdefff', false); }
    C.rect(11, 11, 2, 1, '#1b1530');
    if (etat === 'content') { C.px(11, 12, '#e8606a'); C.px(12, 12, '#e8606a'); }
    C.hline(6, 17, 14, NC); C.hline(7, 16, 15, fonce(NC, 0.3)); C.px(9, 14, NJ);
    C.rect(7, 19, 2, 2, '#3a2a2a'); C.rect(14, 19, 2, 2, '#3a2a2a');
    C.rect(7, 22, 3, 1, '#3a2a2a'); C.rect(13, 22, 3, 1, '#3a2a2a');
    return finComp(C, F, etat, n);
  }
  /* le petit robot des fiches du site (tête carrée bleu nuit, antenne à boule rouge, yeux blancs) */
  function petitRobot(etat, n) {
    var C = new Calque(CW, CH), F = new Calque(CW, CH), bleu = '#1a2a6c', blanc = '#ffffff';
    C.rect(5, 6, 16, 13, bleu);
    [[5, 6], [20, 6], [5, 18], [20, 18]].forEach(function (p) { C.ote(p[0], p[1]); C.m.delete(p[1] * K + p[0]); });
    C.hline(7, 12, 7, '#2e4296');
    for (var y = 7; y < 18; y++) C.px(20, y, '#142057');
    C.rect(12, 3, 2, 3, bleu);
    var boule = etat === 'triste' || etat === 'dort' ? '#9aa3b8' : '#b21f1f';
    C.ellipse(13, 2, 1.8, 1.8, boule); C.px(12, 1, clair(boule, 0.5));
    if (etat === 'content') { C.carte(8, 10, ['.ww.', 'w..w'], { w: blanc }); C.carte(14, 10, ['.ww.', 'w..w'], { w: blanc }); }
    else if (etat === 'dort') { C.hline(8, 11, 12, blanc); C.hline(14, 17, 12, blanc); }
    else {
      C.ellipse(10, 11.5, 2, 2, blanc); C.ellipse(16, 11.5, 2, 2, blanc);
      if (etat === 'triste') { C.hline(8, 11, 10, bleu); C.hline(14, 17, 10, bleu); F.px(17, 14, '#7ad8ff', false); F.px(17, 15, '#bdefff', false); }
      else if (n % 2) { C.hline(8, 11, 11, bleu); C.hline(14, 17, 11, bleu); }
    }
    if (etat === 'content') C.carte(9, 14, ['w......w', '.wwwwww.'], { w: blanc });
    else if (etat === 'triste') C.carte(9, 15, ['.wwwwww.', 'w......w'], { w: blanc });
    else if (etat === 'dort') C.rect(11, 15, 4, 1, blanc);
    else C.rect(9, 15, 8, 1, blanc);
    C.rect(7, 19, 3, 3, bleu); C.rect(16, 19, 3, 3, bleu);
    return finComp(C, F, etat, n);
  }
  function tortue(etat, n) {
    var C = new Calque(CW, CH), F = new Calque(CW, CH), peau = '#5aa07a';
    var hy = etat === 'content' ? 10 : (etat === 'triste' || etat === 'dort' ? 15 : 12);
    C.ellipse(21, hy, 3.8, 3.2, peau);
    [[6, 19], [16, 19]].forEach(function (p) { C.rect(p[0], p[1], 3, 3, peau); });
    C.rect(2, 16, 3, 2, peau);
    C.ellipse(11.5, 14, 9.5, 7.5, '#3a3f58', true, function (x, y) { return y < 19 ? '#3a3f58' : null; });
    C.hline(3, 20, 18, '#5a5f7a');
    [10, 13, 16].forEach(function (y, i) {
      C.hline(6, 17, y, '#24283a');
      for (var k = 0, x = 7; x < 17; x += 3, k++) {
        var on = (etat !== 'triste' && etat !== 'dort') || (k + i) % 3 === 0;
        C.px(x, y - 1, on ? [NG, NC, NJ][(k + i + n) % 3] : '#5a5f7a');
      }
    });
    if (etat === 'content') { C.px(21, hy - 1, NOIR); C.px(22, hy - 2, NOIR); C.px(23, hy - 1, NOIR); }
    else if (etat === 'dort') C.rect(22, hy, 2, 1, NOIR);
    else C.rect(22, hy - 1, 1, 2, NOIR);
    C.px(23, hy + 1, '#2a5a3a');
    if (etat === 'triste') F.px(23, hy + 1, '#7ad8ff', false);
    return finComp(C, F, etat, n);
  }
  function roussette(etat, n) {
    var C = new Calque(CW, CH), F = new Calque(CW, CH), aile = '#3a2a22', ailC = '#5a4034', corps = '#5a3a2a', teteC = '#c8702a';
    if (etat === 'content') {
      [-1, 1].forEach(function (s) {
        var cx = 12.5 + s * (7.5 - (n % 2));
        C.ellipse(cx, 13 - (n % 2), 5.5, 6.5, aile);
        for (var k = 0; k < 3; k++) C.px(cx + s * (k * 1.6 - 1), 9 + k * 3, ailC);
      });
    } else { C.ellipse(12.5, 15, 8, 7.5, aile); C.hline(7, 18, etat === 'neutre' ? 14 : 16, ailC); }
    C.ellipse(12.5, 16, 4, 5, corps);
    var oy = etat === 'triste' ? 1 : 0;
    [-1, 1].forEach(function (s) {
      var ex = 12.5 + s * 4.5;
      for (var k = 0; k < 4; k++) C.px(ex + s * (etat !== 'triste' ? fdiv(k, 2) : fdiv(k, 2) + 1) - 0.5, 2 + k + oy * (k === 0 ? 2 : 1), teteC);
    });
    C.ellipse(12.5, 8, 5.5, 4.6, teteC); C.ellipse(12.5, 10.5, 2.4, 1.6, '#e8a060');
    C.px(12, 10, '#1b1530'); C.px(13, 10, '#1b1530');
    yeuxComp(C, F, [[9, 6], [14, 6]], etat, 2);
    C.rect(10, 21, 2, 1, '#2a1f1a'); C.rect(14, 21, 2, 1, '#2a1f1a');
    return finComp(C, F, etat, n);
  }
  function margComp(etat, n) {
    var M = margSprite('profil', 24, etat === 'dort' ? 'neutre' : etat, etat === 'triste' ? 0 : n * 0.7);
    var R = new Calque(CW, CH);
    R.sur(M, fdiv(CW - M.w, 2), CH - M.h - 1);
    return R;
  }
  var COMPAGNONS = { maki: maki, robot: petitRobot, tortue: tortue, roussette: roussette, margouillat: margComp };
  var COMP_MIROIR = { margouillat: 1, tortue: 1 };
  function compagnon(id, etat, n) {
    var f = COMPAGNONS[id];
    if (!f) return null;
    var C = f(etat || 'neutre', n || 0);
    if (COMP_MIROIR[id]) C = C.transformer(function (x, y) { return [CW - 1 - x, y]; });
    return C;
  }

  /* ════════════════════════════════════════════
     LES SEPT ÉTATS
     Chaque état est une suite d'images ; la première est l'image fixe
     (mouvement réduit, impression, anime: false).
     ════════════════════════════════════════════ */
  function I(d, pose, extra) { var o = { d: d, pose: pose || {} }; for (var k in extra) o[k] = extra[k]; return o; }
  var ETATS = {
    repos: { nom: 'au repos', comp: 'neutre', images: [
      I(1700, { bras: 'repos', yeux: 'ouverts', bouche: 'sourire' }),
      I(900, { bras: 'repos', yeux: 'ouverts', bouche: 'sourire', souffle: 1, turbine: 1, egaliseur: 1, nuee: 1 }, { cn: 1 }),
      I(1500, { bras: 'repos', yeux: 'ouverts', bouche: 'sourire', turbine: 2, egaliseur: 2 }),
      I(140, { bras: 'repos', yeux: 'fermes', bouche: 'sourire' })] },
    content: { nom: 'content·e', comp: 'content', images: [
      I(1100, { bras: 'ouvert', yeux: 'rieurs', bouche: 'sourire', joues: 1 }),
      I(160, { bras: 'ouvert', yeux: 'rieurs', bouche: 'rire', joues: 1, turbine: 1, egaliseur: 1 }, { dy: -1, cn: 1 }),
      I(140, { bras: 'ouvert', yeux: 'rieurs', bouche: 'rire', joues: 1, souffle: 1, turbine: 2 }),
      I(160, { bras: 'ouvert', yeux: 'rieurs', bouche: 'rire', joues: 1, egaliseur: 2 }, { dy: -1, cn: 1 }),
      I(900, { bras: 'ouvert', yeux: 'rieurs', bouche: 'sourire', joues: 1, souffle: 1 })] },
    tres_content: { nom: 'très content·e', comp: 'content', images: [
      I(260, { bras: 'haut', yeux: 'rieurs', bouche: 'rire', joues: 1, souffle: 1, roue: 1 }, { fx: [['etincelles', 0]] }),
      I(220, { bras: 'haut', yeux: 'rieurs', bouche: 'rire', joues: 1, turbine: 1, egaliseur: 1, roue: 2, brume: 1 }, { dy: -2, fx: [['etincelles', 1]], cn: 1 }),
      I(220, { bras: 'haut', yeux: 'rieurs', bouche: 'rire', joues: 1, turbine: 2, egaliseur: 2, roue: 3, brume: 2 }, { dy: -3, fx: [['etincelles', 0]], cn: 1 }),
      I(200, { bras: 'haut', yeux: 'rieurs', bouche: 'rire', joues: 1, turbine: 3, egaliseur: 3 }, { dy: -1, fx: [['etincelles', 1]] })] },
    triste: { nom: 'triste', comp: 'triste', images: [
      I(900, { bras: 'triste', yeux: 'tristes', bouche: 'triste', tete: 'baisse', larme: 1 }, { fx: [['nuage', 0]] }),
      I(900, { bras: 'triste', yeux: 'tristes', bouche: 'triste', tete: 'baisse', larme: 2 }, { fx: [['nuage', 2]] }),
      I(1200, { bras: 'triste', yeux: 'tristes', bouche: 'triste', tete: 'baisse', souffle: 1 }, { fx: [['nuage', 4]] })] },
    concentre: { nom: 'concentré·e', comp: 'neutre', images: [
      I(520, { bras: 'clavier', yeux: 'concentres', bouche: 'langue', tablette: 1 }, { fx: [['bulle', 3]] }),
      I(420, { bras: 'clavier3', yeux: 'concentres', bouche: 'langue', tablette: 3 }, { fx: [['bulle', 1]] }),
      I(420, { bras: 'clavier2', yeux: 'concentres', bouche: 'langue', tablette: 2 }, { fx: [['bulle', 2]] }),
      I(420, { bras: 'clavier3', yeux: 'concentres', bouche: 'neutre', tablette: 3 }, { fx: [['bulle', 3]], cn: 1 }),
      I(520, { bras: 'clavier', yeux: 'concentres', bouche: 'langue', tablette: 1, souffle: 1 }, { fx: [['bulle', 3]] })] },
    salue: { nom: 'salue', comp: 'content', images: [
      I(320, { bras: 'salut', yeux: 'ouverts', bouche: 'rire', joues: 1 }, { fx: [['vent', 0]] }),
      I(280, { bras: 'salut2', yeux: 'ouverts', bouche: 'rire', joues: 1, turbine: 1 }, { fx: [['vent', 1]], cn: 1 }),
      I(280, { bras: 'salut', yeux: 'ouverts', bouche: 'rire', joues: 1, turbine: 2 }, { fx: [['vent', 0]] }),
      I(280, { bras: 'salut2', yeux: 'ouverts', bouche: 'rire', joues: 1 }, { fx: [['vent', 1]], cn: 1 }),
      I(1100, { bras: 'salut', yeux: 'ouverts', bouche: 'sourire', joues: 1 })] },
    dort: { nom: 'dort', comp: 'dort', images: [
      I(1100, { bras: 'repos', yeux: 'doux', bouche: 'neutre', tete: 'baisse' }, { fx: [['zzz', 3]] }),
      I(1100, { bras: 'repos', yeux: 'doux', bouche: 'petit', tete: 'baisse', souffle: 1 }, { fx: [['zzz', 1]] }),
      I(1100, { bras: 'repos', yeux: 'doux', bouche: 'neutre', tete: 'baisse' }, { fx: [['zzz', 2]] })] }
  };
  var LISTE_ETATS = Object.keys(ETATS);

  /* ════════════════════════════════════════════
     RENDU SVG
     ════════════════════════════════════════════ */
  var CADRES = {
    entier: [0, 8, 48, 56], entier_compagnon: [0, 8, 74, 56],
    buste: [8, 18, 32, 32], pastille: [12, 22, 24, 24]
  };
  var _id = 0;

  function imageAvatar(cfg, img, etat, avecComp, i) {
    var pose = { n: i || 0 }; for (var k in img.pose) pose[k] = img.pose[k];
    var R = dessiner(cfg, pose);
    var S = new Calque(avecComp ? 74 : 48, 64);
    var dy = img.dy || 0;
    S.sur(R, 0, dy);
    if (avecComp) {
      var C = compagnon(cfg.compagnon, ETATS[etat].comp, img.cn || 0);
      if (C) S.sur(C, 47, 40 + (img.cn && ETATS[etat].comp === 'content' ? -1 : 0));
    }
    if (img.fx) {
      var main = R.main ? [R.main[0], R.main[1] + dy] : null;
      S.sur(effets(img.fx, main), 0, dy);
    }
    return S;
  }

  /* feuille de style commune, injectée une fois */
  var _style = null, _anims = {};
  function feuille() {
    if (_style || typeof document === 'undefined') return _style;
    _style = document.createElement('style');
    _style.id = 'equipage-css';
    _style.textContent = [
      '.eq{display:inline-block;line-height:0;vertical-align:middle}',
      '.eq svg{display:block;overflow:hidden}',
      '.eq-pastille svg{border-radius:50%;overflow:hidden;background:var(--eq-fond-pastille,#dfe6f2)}',
      '.eq-img{opacity:0}.eq-img.eq-i0{opacity:1}',
      '.eq-halo{fill:transparent}',
      '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .eq-halo{fill:var(--eq-halo,#dfe8ff);fill-opacity:.8}:root:not([data-theme="light"]) .eq-pastille svg{background:var(--eq-fond-pastille,#1c2744)}}',
      ':root[data-theme="dark"] .eq-halo{fill:var(--eq-halo,#dfe8ff);fill-opacity:.8}:root[data-theme="dark"] .eq-pastille svg{background:var(--eq-fond-pastille,#1c2744)}',
      '.eq.eq-obscur .eq-halo{fill:var(--eq-halo,#dfe8ff);fill-opacity:.8}.eq.eq-clair .eq-halo{fill:transparent}',
      '.eq-marg{position:absolute;z-index:1;pointer-events:none;line-height:0}',
      '.eq-papier{display:none}',
      '@media print{.eq-img{animation:none!important;opacity:0!important}.eq-img.eq-i0{opacity:1!important}.eq-halo{fill:transparent!important}.eq-encre-noire .eq-ecran{display:none}.eq-encre-noire .eq-papier{display:inline}}',
      '@media (prefers-reduced-motion:reduce){.eq-img{animation:none!important}}'
    ].join('\n');
    (document.head || document.documentElement).appendChild(_style);
    return _style;
  }
  function animation(durees) {
    var cle = durees.join('-');
    if (_anims[cle]) return _anims[cle];
    var T = durees.reduce(function (a, b) { return a + b; }, 0), t = 0, noms = [], css = '';
    durees.forEach(function (d, i) {
      var s = (t / T * 100).toFixed(3), e = ((t + d) / T * 100).toFixed(3), nom = 'eqk' + cle.replace(/[^0-9-]/g, '') + '_' + i;
      var k = '@keyframes ' + nom + '{';
      if (t > 0) k += '0%{opacity:0}';
      k += s + '%{opacity:1}';
      k += (t + d < T) ? e + '%{opacity:0}100%{opacity:0}' : '100%{opacity:1}';
      css += k + '}\n';
      noms.push(nom); t += d;
    });
    var st = feuille();
    if (st) st.textContent += '\n' + css;
    _anims[cle] = { T: T, noms: noms };
    return _anims[cle];
  }

  function texte(d, etat) {
    d = normaliser(d);
    function nom(champ, v) { var e = CATALOGUE[champ].filter(function (x) { return x.id === v; })[0]; return e ? e.nom.toLowerCase() : v; }
    var morceaux = ['Avatar, lignée ' + nom('lignee', d.lignee).replace(/^./, function (c) { return c.toUpperCase(); })];
    if (!SANS_CORPS[d.lignee]) morceaux.push('teint ' + d.teint);
    morceaux.push('coiffure ' + nom('coiffure', d.coiffure));
    if (d.haut !== 'aucun') morceaux.push(nom('haut', d.haut));
    if (!SANS_CORPS[d.lignee]) { morceaux.push(nom('bas', d.bas)); morceaux.push(nom('chaussures', d.chaussures)); }
    EMPLACEMENTS.forEach(function (e) {
      var v = d.objets[e]; if (v === 'aucun') return;
      var x = CATALOGUE.objets[e].filter(function (y) { return y.id === v; })[0];
      morceaux.push(x.nom.toLowerCase());
    });
    if (d.fauteuil) morceaux.push('en fauteuil de course');
    if (d.compagnon !== 'aucun') morceaux.push('avec ' + (d.compagnon === 'robot' ? 'un petit robot' : d.compagnon === 'tortue' ? 'une tortue serveur' : d.compagnon === 'roussette' ? 'une roussette' : 'un ' + nom('compagnon', d.compagnon)));
    var e = ETATS[etat] ? ETATS[etat].nom : ETATS.repos.nom;
    return morceaux.join(', ') + ' ; ' + e + '.';
  }

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  /* options : taille (hauteur en px, 96), etat ('repos'), cadre ('auto' | 'entier' | 'buste' | 'pastille'),
     compagnon (true), anime (true), alt (texte, ou '' pour décoratif), net (false : taille exacte ;
     true : arrondie à un multiple entier de la grille), decalage (ms, au hasard sinon) */
  function svg(desc, options) {
    var o = options || {}, d = normaliser(desc), cfg = reglages(d);
    var etat = ETATS[o.etat] ? o.etat : 'repos';
    var taille = +o.taille > 0 ? +o.taille : 96;
    var cadre = o.cadre && o.cadre !== 'auto' ? o.cadre : (taille < 32 ? 'pastille' : (taille < 64 ? 'buste' : 'entier'));
    if (!CADRES[cadre]) cadre = 'entier';
    var avecComp = cadre === 'entier' && d.compagnon !== 'aucun' && o.compagnon !== false;
    var vb = CADRES[avecComp ? 'entier_compagnon' : cadre];
    if (o.net) taille = Math.max(vb[3], Math.floor(taille / vb[3]) * vb[3]);
    var largeur = Math.round(taille * vb[2] / vb[3] * 100) / 100;
    var images = ETATS[etat].images;
    var anime = o.anime !== false && images.length > 1;
    if (!anime) images = [images[0]];
    var anim = anime ? animation(images.map(function (i) { return i.d; })) : null;
    if (!anime) feuille();
    var dec = o.decalage !== undefined ? +o.decalage : Math.floor(Math.random() * (anim ? anim.T : 1));
    var alt = o.alt !== undefined ? o.alt : texte(d, etat);
    var corps = '';
    images.forEach(function (img, i) {
      var S = imageAvatar(cfg, img, etat, avecComp, i);
      var st = anim ? ' style="animation:' + anim.noms[i] + ' ' + anim.T + 'ms step-end ' + (-dec) + 'ms infinite"' : '';
      corps += '<g class="eq-img eq-i' + i + '"' + st + '>' + cheminsSet(S.anneau(), 'eq-halo') + chemins(S) + '</g>';
    });
    var aria = alt === '' ? ' aria-hidden="true" focusable="false"' : ' role="img" aria-label="' + esc(alt) + '"';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="' + vb.join(' ') + '" width="' + largeur + '" height="' + taille + '" shape-rendering="crispEdges"' + aria + '>' + (alt ? '<title>' + esc(alt) + '</title>' : '') + corps + '</svg>';
  }

  function classes(o, cadre) {
    var c = 'eq eq-' + cadre;
    if (o.fond === 'obscur') c += ' eq-obscur'; else if (o.fond === 'clair') c += ' eq-clair';
    return c;
  }

  function creer(element, desc, options) {
    var o = {}, k;
    for (k in options || {}) o[k] = options[k];
    var etatDesc = normaliser(desc);
    if (o.decalage === undefined) o.decalage = Math.floor(Math.random() * 4000);
    function rendre() {
      var taille = +o.taille > 0 ? +o.taille : 96;
      var cadre = o.cadre && o.cadre !== 'auto' ? o.cadre : (taille < 32 ? 'pastille' : (taille < 64 ? 'buste' : 'entier'));
      element.className = (element.className.replace(/(^|\s)eq(-[a-z]+)?(?=\s|$)/g, '').trim() + ' ' + classes(o, cadre)).trim();
      element.innerHTML = svg(etatDesc, o);
    }
    rendre();
    return {
      element: element,
      get description() { return copie(etatDesc); },
      maj: function (d) { etatDesc = normaliser(d); rendre(); return this; },
      etat: function (e) { o.etat = e; rendre(); return this; },
      options: function (p) { for (var k in p) o[k] = p[k]; rendre(); return this; },
      detruire: function () { element.innerHTML = ''; }
    };
  }

  /* ── le margouillat ──
     options : taille (longueur en px, ou chaîne CSS « 9mm »), etat ('neutre' | 'content' | 'triste'),
     sens ('montant' | 'descendant' | 'sol' | 'plafond'), miroir, bord ('haut' | 'bas' | 'gauche' | 'droite'),
     position (le long du bord, '75%'), encre ('couleur' | 'noir' | 'auto' : noir à l'impression), anime, alt */
  function margouillatSVG(options) {
    var o = options || {};
    var etat = { content: 1, triste: 1 }[o.etat] ? o.etat : 'neutre';
    var sens = o.sens || ({ haut: 'sol', bas: 'plafond', gauche: 'montant', droite: 'descendant' }[o.bord]) || 'sol';
    var vue = sens === 'sol' || sens === 'plafond' ? 'profil' : 'dessus';
    var css = typeof o.taille === 'string' && /[a-z%]$/.test(o.taille) ? o.taille : null;
    var px = css ? (/mm$/.test(css) ? parseFloat(css) * 3.78 : 24) : (+o.taille > 0 ? +o.taille : 32);
    var S = px <= 20 ? 16 : (px <= 28 ? 24 : (px <= 44 ? 32 : 48));
    var nb = o.anime === false || etat === 'triste' || S < 32 ? 1 : 3;
    var anim = nb > 1 ? animation(etat === 'content' ? [140, 140, 140] : [420, 420, 420]) : null;
    if (!anim) feuille();
    var dec = Math.floor(Math.random() * 1000);
    var corps = '', w = 0, h = 0;
    for (var i = 0; i < nb; i++) {
      var C = orienter(margSprite(vue, S, etat, i * 2.094 / 3), sens, o.miroir);
      w = Math.max(w, C.w); h = Math.max(h, C.h);
      var st = anim ? ' style="animation:' + anim.noms[i] + ' ' + anim.T + 'ms step-end ' + (-dec) + 'ms infinite"' : '';
      var noir = o.encre === 'noir' || o.encre === 'auto' ? encreNoire(C) : null;
      var contenu = o.encre === 'noir' ? chemins(noir) : (o.encre === 'auto' ? '<g class="eq-ecran">' + cheminsSet(C.anneau(), 'eq-halo') + chemins(C) + '</g><g class="eq-papier">' + chemins(noir) + '</g>' : cheminsSet(C.anneau(), 'eq-halo') + chemins(C));
      corps += '<g class="eq-img eq-i' + i + '"' + st + '>' + contenu + '</g>';
    }
    var long = Math.max(w, h), unite = px / long;
    var W_ = css ? (w >= h ? css : 'calc(' + css + ' * ' + (w / h).toFixed(3) + ')') : Math.round(w * unite * 100) / 100;
    var H_ = css ? (h >= w ? css : 'calc(' + css + ' * ' + (h / w).toFixed(3) + ')') : Math.round(h * unite * 100) / 100;
    var alt = o.alt !== undefined ? o.alt : '';
    var aria = alt === '' ? ' aria-hidden="true" focusable="false"' : ' role="img" aria-label="' + esc(alt) + '"';
    var dim = css ? ' style="width:' + W_ + ';height:' + H_ + '"' : ' width="' + W_ + '" height="' + H_ + '"';
    return { svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + w + ' ' + h + '"' + dim + ' shape-rendering="crispEdges"' + aria + '>' + (alt ? '<title>' + esc(alt) + '</title>' : '') + corps + '</svg>', unite: css ? null : unite, sens: sens };
  }

  function margouillat(element, options) {
    var o = options || {};
    var r = margouillatSVG(o);
    var cible = element, porteur = null;
    if (o.bord && element) {
      if (typeof getComputedStyle === 'function' && getComputedStyle(element).position === 'static') element.style.position = 'relative';
      porteur = document.createElement('span');
      porteur.className = 'eq-marg';
      var pos = o.position || '80%', u = r.unite ? Math.max(1, Math.round(r.unite)) : 2;
      var st = porteur.style;
      if (o.bord === 'haut') { st.top = '0'; st.left = pos; st.transform = 'translate(-50%, calc(-100% + ' + (2 * u) + 'px))'; }
      else if (o.bord === 'bas') { st.top = '100%'; st.left = pos; st.transform = 'translate(-50%, ' + (-2 * u) + 'px)'; }
      else if (o.bord === 'gauche') { st.left = '0'; st.top = pos; st.transform = 'translate(-50%, -50%)'; }
      else { st.left = '100%'; st.top = pos; st.transform = 'translate(-50%, -50%)'; }
      element.appendChild(porteur);
      cible = porteur;
    }
    var cls = 'eq' + (o.encre === 'auto' ? ' eq-encre-noire' : '') + (o.fond === 'obscur' ? ' eq-obscur' : o.fond === 'clair' ? ' eq-clair' : '');
    if (cible) {
      if (porteur) { porteur.className += ' ' + cls; porteur.innerHTML = r.svg; }
      else { cible.classList.add.apply(cible.classList, cls.split(' ')); cible.innerHTML = r.svg; }
    }
    return { element: porteur || cible, svg: r.svg, detruire: function () { if (porteur && porteur.parentNode) porteur.parentNode.removeChild(porteur); else if (cible) cible.innerHTML = ''; } };
  }

  /* compagnon seul (choix dans un menu, par exemple) */
  function compagnonSVG(id, options) {
    var o = options || {}, etat = { content: 1, triste: 1, dort: 1 }[o.etat] ? o.etat : 'neutre';
    var nb = o.anime === false ? 1 : 2, anim = nb > 1 ? animation([600, 600]) : null, corps = '';
    if (!anim) feuille();
    for (var i = 0; i < nb; i++) {
      var C = compagnon(id, etat, i);
      if (!C) return '';
      var st = anim ? ' style="animation:' + anim.noms[i] + ' ' + anim.T + 'ms step-end infinite"' : '';
      corps += '<g class="eq-img eq-i' + i + '"' + st + '>' + cheminsSet(C.anneau(), 'eq-halo') + chemins(C) + '</g>';
    }
    var t = +o.taille > 0 ? +o.taille : 48, alt = o.alt !== undefined ? o.alt : '';
    var aria = alt === '' ? ' aria-hidden="true" focusable="false"' : ' role="img" aria-label="' + esc(alt) + '"';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + CW + ' ' + CH + '" width="' + Math.round(t * CW / CH) + '" height="' + t + '" shape-rendering="crispEdges"' + aria + '>' + (alt ? '<title>' + esc(alt) + '</title>' : '') + corps + '</svg>';
  }

  /* avatar au hasard, reproductible */
  function aleatoire(graine) {
    var r = hasard(graine === undefined ? Math.floor(Math.random() * 1e9) : graine);
    function un(champ) { var l = CATALOGUE[champ]; return l[Math.floor(r() * l.length)].id; }
    function cle(p) { var l = Object.keys(PALETTES[p]); return l[Math.floor(r() * l.length)]; }
    var lig = r() < 0.55 ? 'humain' : un('lignee');
    var coifs = CATALOGUE.coiffure.map(function (e) { return e.id; }).filter(function (id) { return ['volute', 'glitch', 'feuilles'].indexOf(id) < 0; });
    var d = {
      v: 1, lignee: lig, teint: 1 + Math.floor(r() * 8), corps: un('corps'),
      coiffure: lig === 'esprit' && r() < 0.6 ? 'volute' : lig === 'nuee' && r() < 0.6 ? 'glitch' : lig === 'greffe' && r() < 0.6 ? 'feuilles' : coifs[Math.floor(r() * coifs.length)],
      cheveux: r() < 0.75 ? ['noirs', 'bruns', 'chatains', 'auburn'][Math.floor(r() * 4)] : cle('cheveux'),
      haut: SANS_CORPS[lig] && r() < 0.6 ? 'aucun' : CATALOGUE.haut.filter(function (e) { return e.id !== 'aucun'; })[Math.floor(r() * 9)].id,
      bas: un('bas'), chaussures: un('chaussures'),
      objets: {}, fauteuil: r() < 0.08, compagnon: r() < 0.5 ? 'margouillat' : un('compagnon'),
      couleurs: { haut: cle('tissu'), bas: cle('tissu'), accent: cle('neon'), chaussures: cle('chaussures'), yeux: cle('yeux') }
    };
    var proba = { tete: 0.45, visage: 0.3, dos: 0.3, main: 0.45, epaule: 0.2, autour: 0.2 };
    EMPLACEMENTS.forEach(function (e) { var l = CATALOGUE.objets[e]; d.objets[e] = r() < proba[e] ? l[1 + Math.floor(r() * (l.length - 1))].id : 'aucun'; });
    if (d.couleurs.bas === d.couleurs.haut) d.couleurs.bas = 'anthracite';
    return normaliser(d);
  }

  /* modèles : les huit tenues de la planche v2 et les sept lignées */
  function M(o) { var d = copie(DEFAUT); for (var k in o) if (k === 'couleurs' || k === 'objets') { for (var c in o[k]) d[k][c] = o[k][c]; } else d[k] = o[k]; return normaliser(d); }
  var MODELES = {
    fibre: { nom: 'Fibre optique', etat: 'salue', description: M({ teint: 8, coiffure: 'tresses_fibre', haut: 'veste', bas: 'cargo', chaussures: 'montantes', objets: { dos: 'sac_antenne' }, couleurs: { haut: 'violet', bas: 'anthracite', accent: 'cyan', chaussures: 'blanches' } }) },
    pneu: { nom: 'Course de pneus', etat: 'content', description: M({ teint: 5, corps: 'fine', coiffure: 'degrade_circuit', haut: 'maillot', bas: 'short', chaussures: 'crampons', objets: { main: 'pneu' }, compagnon: 'robot', couleurs: { haut: 'vert', bas: 'nuit', accent: 'jaune', chaussures: 'noires' } }) },
    fleurs: { nom: 'Fleurs-circuits', etat: 'repos', description: M({ teint: 6, corps: 'ronde', coiffure: 'chignon_antenne', cheveux: 'bruns', haut: 'tunique', bas: 'jupe_longue', chaussures: 'savates', objets: { epaule: 'chale', autour: 'petales' }, compagnon: 'roussette', couleurs: { haut: 'sarcelle', bas: 'rose', accent: 'jaune', chaussures: 'noires', yeux: 'noirs' } }) },
    capuche: { nom: 'Capuche réseau', etat: 'concentre', description: M({ teint: 3, coiffure: 'capuche', cheveux: 'chatains', haut: 'sweat', bas: 'patchwork', chaussures: 'baskets', objets: { tete: 'casque_audio', autour: 'notes' }, couleurs: { haut: 'marine', bas: 'gris', accent: 'cyan', chaussures: 'rouges', yeux: 'verts' } }) },
    fauteuil: { nom: 'Fauteuil de course', etat: 'tres_content', description: M({ teint: 2, coiffure: 'court', cheveux: 'auburn', haut: 'combinaison', bas: 'pantalon', objets: { tete: 'bandeau' }, fauteuil: true, couleurs: { haut: 'nuit', bas: 'nuit', accent: 'rose', chaussures: 'blanches', yeux: 'bleus' } }) },
    mecano: { nom: 'Mécano de la Flottille', etat: 'repos', description: M({ teint: 4, corps: 'ronde', coiffure: 'boucles', cheveux: 'bruns', haut: 'gilet', bas: 'patchwork', chaussures: 'bottes', objets: { dos: 'turbine_dos', tete: 'soudure', main: 'cle' }, compagnon: 'tortue', couleurs: { haut: 'kaki', bas: 'jean', accent: 'orange', chaussures: 'jaunes' } }) },
    battle: { nom: 'Battle', etat: 'tres_content', description: M({ teint: 7, coiffure: 'afro_pixel', haut: 'debardeur', bas: 'sarouel', chaussures: 'montantes', objets: { main: 'enceinte', autour: 'aura' }, couleurs: { haut: 'blanc', bas: 'nuit', accent: 'violet', chaussures: 'noires' } }) },
    pochoir: { nom: 'Pochoir', etat: 'salue', description: M({ teint: 1, corps: 'fine', coiffure: 'crete_graffiti', cheveux: 'bruns', haut: 'chemise', bas: 'jogging', chaussures: 'baskets', objets: { main: 'bombe', visage: 'lunettes_ecran' }, compagnon: 'maki', couleurs: { haut: 'anthracite', bas: 'anthracite', accent: 'vert', chaussures: 'blanches', yeux: 'bleus' } }) },
    pirate: { nom: 'Pirate du lagon', etat: 'content', description: M({ teint: 6, coiffure: 'locks_cables', haut: 'chemise', bas: 'sarouel', chaussures: 'pieds_nus', objets: { tete: 'chapeau_paille', dos: 'drapeau', main: 'mangue', autour: 'bulles' }, couleurs: { haut: 'rouge', bas: 'beige', accent: 'cyan' } }) },
    fete: { nom: 'Soir de fête', etat: 'salue', description: M({ lignee: 'esprit', coiffure: 'lisses', cheveux: 'roses', haut: 'tunique', objets: { visage: 'masque', dos: 'ailes_fee', main: 'lanterne', autour: 'lucioles' }, couleurs: { haut: 'prune', accent: 'jaune' } }) },
    reseau: { nom: 'Implant et visière', etat: 'concentre', description: M({ lignee: 'cyber', teint: 3, coiffure: 'rase', haut: 'combinaison', bas: 'jogging', objets: { visage: 'visiere', epaule: 'drone', dos: 'jetpack' }, couleurs: { haut: 'marine', bas: 'nuit', accent: 'rose' } }) },
    humain: { nom: 'Humain·e', lignee: 1, description: M({ lignee: 'humain', teint: 2, coiffure: 'court', cheveux: 'chatains', haut: 'tshirt', objets: { tete: 'frontale' }, couleurs: { haut: 'jaune', bas: 'jean', accent: 'cyan', chaussures: 'rouges', yeux: 'verts' } }) },
    cyber: { nom: 'Cyber', lignee: 1, description: M({ lignee: 'cyber', teint: 8, coiffure: 'tresses', haut: 'veste', couleurs: { haut: 'violet', bas: 'anthracite', accent: 'rose', chaussures: 'noires' } }) },
    nuee: { nom: 'Nuée', lignee: 1, description: M({ lignee: 'nuee', coiffure: 'glitch', haut: 'aucun', couleurs: { accent: 'cyan' } }) },
    mutant: { nom: 'Mutant·e', lignee: 1, description: M({ lignee: 'mutant', teint: 5, coiffure: 'puffs', cheveux: 'bruns', haut: 'debardeur', couleurs: { haut: 'vert', bas: 'prune', accent: 'vert', chaussures: 'blanches', yeux: 'ambre' } }) },
    lagon: { nom: 'Peuple du lagon', lignee: 1, description: M({ lignee: 'lagon', teint: 6, coiffure: 'rase', haut: 'debardeur', bas: 'short', couleurs: { haut: 'orange', bas: 'canard', accent: 'cyan', yeux: 'turquoise' } }) },
    esprit: { nom: 'Esprit', lignee: 1, description: M({ lignee: 'esprit', coiffure: 'volute', cheveux: 'violets', haut: 'aucun', couleurs: { yeux: 'violets' } }) },
    greffe: { nom: 'Greffé·e', lignee: 1, description: M({ lignee: 'greffe', teint: 4, coiffure: 'feuilles', cheveux: 'bruns', haut: 'gilet', bas: 'pantalon', couleurs: { haut: 'vert', bas: 'brun', accent: 'jaune', chaussures: 'brunes', yeux: 'verts' } }) }
  };

  var API = {
    version: VERSION,
    creer: creer, svg: svg, texte: texte, normaliser: normaliser, aleatoire: aleatoire,
    margouillat: margouillat, margouillatSVG: function (o) { return margouillatSVG(o).svg; },
    compagnonSVG: compagnonSVG,
    catalogue: CATALOGUE, palettes: PALETTES, modeles: MODELES,
    ETATS: LISTE_ETATS.map(function (k) { return { id: k, nom: ETATS[k].nom }; }),
    defaut: function () { return copie(DEFAUT); }
  };
  if (typeof module === 'object' && module.exports) module.exports = API;
  else racine.Equipage = API;
})(typeof window !== 'undefined' ? window : this);
