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
   Pour les applications (T133b) : états d'usage, poignee.geste / bulle /
   marque / serie, Equipage.calme / plafond / pause / neutre / phrases /
   gestes / applis (mode d'emploi : charte/applis.md).

   Contrat complet : assets/equipage/LISEZMOI.md.
   Dessins originaux ; style de personnage repris du jeu de révision
   de l'enseignant. Aucun envoi de données, rien n'est gardé.
   Auteur : Babash - NSI Tani Malandi. Code sous licence MIT.
   ───────────────────────────────────────────── */
(function (racine) {
  'use strict';

  var VERSION = '2.1.0';
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
    haut: liste([['tshirt', 'Tee-shirt'], ['veste', 'Veste runner'], ['maillot', 'Maillot de quartier libre'], ['maillot_mada', 'Maillot aux couleurs de Madagascar'], ['maillot_comores', 'Maillot des Comores (croissant et quatre étoiles)'], ['tunique', 'Tunique fleurs-circuits'], ['sweat', 'Sweat'], ['gilet', 'Gilet de bricole'], ['debardeur', 'Débardeur de battle'], ['chemise', 'Chemise à bugs'], ['combinaison', 'Combinaison de course'], ['aucun', 'Sans haut (Nuée, Esprit)']]),
    bas: liste([['pantalon', 'Pantalon'], ['cargo', 'Cargo à câble'], ['short', 'Short de terrain'], ['jogging', 'Jogging fluo'], ['jupe_longue', 'Jupe longue fleurs-circuits'], ['sarouel', 'Sarouel de danse'], ['patchwork', 'Pantalon rapiécé'], ['salouva', 'Salouva']]),
    chaussures: liste([['baskets', 'Baskets'], ['montantes', 'Baskets montantes'], ['savates', 'Savates néon'], ['bottes', 'Bottes de pont'], ['crampons', 'Crampons de sable'], ['pieds_nus', 'Pieds nus et chevillère']]),
    emplacements: liste([['tete', 'Sur la tête'], ['visage', 'Sur le visage'], ['cou', 'Au cou et à la taille'], ['dos', 'Dans le dos'], ['main', 'Dans la main'], ['epaule', 'Sur les épaules'], ['pieds', 'Aux pieds'], ['autour', 'Autour']]),
    familles: liste([['clin', 'Clins d\'œil'], ['classe', 'Les gimmicks de la classe'], ['heros', 'Héros et héroïnes de BD'], ['pirate', 'Pirates et aventure'], ['lycee', 'Le style du lycée'], ['punk', 'Punk et rue'], ['cyber', 'Cyber et Flottille'], ['nature', 'Fées, esprits, nature'], ['classique', 'Classiques'], ['applis', 'Objets des applications']]),
    objets: {},
    compagnon: [{ id: 'aucun', nom: 'Aucun' }, { id: 'margouillat', nom: 'Margouillat vert', depart: true }, { id: 'maki', nom: 'Maki', gagne: true }, { id: 'robot', nom: 'Petit robot', gagne: true }, { id: 'tortue', nom: 'Tortue serveur', gagne: true }, { id: 'roussette', nom: 'Roussette', gagne: true }],
    teint: TEINTS.map(function (c, i) { return { id: i + 1, nom: 'Teint ' + (i + 1), couleur: c }; }),
    couleurs: {}
  };
  /* les objets : [id, nom, emplacement, famille]. Codes de genres (BD, aventure, punk…),
     jamais un objet reconnaissable d'une œuvre ; ni arme, ni crâne, ni objet religieux. */
  var OBJETS = [
    ['manique_infini', 'La manique de l\'infini', 'main', 'clin'], ['louche_tonnerre', 'La louche du tonnerre', 'main', 'clin'],
    ['couvercle_liberte', 'Le couvercle de la liberté', 'main', 'clin'], ['passoire_pensee', 'La passoire à lire les pensées', 'tete', 'clin'],
    ['cape_serviette', 'La cape-serviette de plage', 'dos', 'clin'], ['lunettes_rayons', 'Les lunettes à rayons… de soleil', 'visage', 'clin'],
    ['pelote_voisinage', 'La pelote du gentil voisinage', 'main', 'clin'], ['coeur_capsule', 'Le cœur en capsule', 'cou', 'clin'],
    ['ceinture_tout_ranger', 'La ceinture à tout ranger', 'cou', 'clin'], ['corde_franchise', 'La corde à sauter de la franchise', 'main', 'clin'],
    ['eclairs_chocolat', 'Les éclairs au chocolat', 'pieds', 'clin'], ['casque_mabawa', 'Le bonnet à mabawa', 'tete', 'clin'],
    ['cornes_zebu', 'Le serre-tête cornes de zébu', 'tete', 'clin'], ['baladeur_galaxie', 'Le baladeur intergalactique', 'cou', 'clin'],
    ['mangue_etoiles', 'La mangue de cristal à quatre étoiles', 'main', 'clin'], ['nuage_taxi', 'Le nuage-taxi', 'pieds', 'clin'],
    ['calculette_9000', 'La calculette de puissance (plus de 9 000)', 'cou', 'clin'],
    ['grenouille_porte_monnaie', 'La grenouille porte-monnaie', 'cou', 'clin'], ['style_trois_baguettes', 'Le style à trois baguettes', 'main', 'clin'],
    ['bateau_mouton', 'Le bateau-mouton', 'main', 'clin'], ['tresor_une_piece', 'Le trésor en une seule pièce', 'main', 'clin'],
    ['boussole_gouter', 'La boussole qui montre le goûter', 'cou', 'clin'], ['crochet_tricot', 'Le crochet… à tricoter', 'main', 'clin'],
    ['perle_noire', 'La perle noire du lagon', 'cou', 'clin'], ['kraken_peluche', 'Le kraken en peluche', 'epaule', 'clin'],
    ['maki_sushi', 'Le maki… sushi', 'main', 'clin'],
    ['barges_pieds', 'Les barges aux pieds', 'pieds', 'clin'], ['doukabe_dos', 'Le doukabé à dos', 'dos', 'clin'],
    ['crete_recurer', 'La crête à récurer', 'tete', 'clin'], ['pinces_linge', 'Les pinces à linge rebelles', 'epaule', 'clin'],
    ['bottes_conserve', 'Les bottes en conserve', 'pieds', 'clin'],

    ['chaise_accoudoirs', 'La chaise à accoudoirs (trône de la salle)', 'dos', 'classe'], ['ventilateur', 'Le ventilateur qui marche encore', 'main', 'classe'],
    ['multiprise', 'La multiprise en sautoir', 'cou', 'classe'], ['souris_marche', 'La souris qui marche', 'epaule', 'classe'],
    ['cle_usb', 'La clé USB retrouvée', 'cou', 'classe'], ['feutre', 'Le feutre qui écrit encore', 'main', 'classe'],
    ['telecommande', 'La télécommande du projecteur', 'main', 'classe'],

    ['meches_vives', 'Mèches électriques', 'tete', 'heros'], ['bandeau_noue', 'Bandeau noué au vent', 'tete', 'heros'],
    ['loup', 'Loup de justicier·e', 'visage', 'heros'], ['monocle_pixels', 'Le monocle à pixels', 'visage', 'heros'],
    ['ceinture_boucle', 'Ceinture à grosse boucle', 'cou', 'heros'], ['cape', 'Cape au vent', 'dos', 'heros'],
    ['gants_geants', 'Gants géants', 'main', 'heros'], ['bottes_heros', 'Bottes à revers', 'pieds', 'heros'],
    ['aura_energie', 'Aura d\'énergie', 'autour', 'heros'], ['eclairs', 'Éclairs', 'autour', 'heros'], ['onomatopee', 'Étoile « ! » de BD', 'autour', 'heros'],

    ['tricorne', 'Tricorne à plume', 'tete', 'pirate'], ['bandana', 'Bandana à pois', 'tete', 'pirate'], ['chapeau_paille', 'Chapeau de pêcheur tressé', 'tete', 'pirate'],
    ['cache_oeil', 'Cache-œil', 'visage', 'pirate'], ['boussole', 'Boussole en pendentif', 'cou', 'pirate'], ['drapeau', 'Drapeau noir au margouillat', 'dos', 'pirate'],
    ['longue_vue', 'Longue-vue', 'main', 'pirate'], ['carte_tresor', 'Carte au trésor', 'main', 'pirate'], ['bouteille_message', 'Bouteille à la mer', 'main', 'pirate'],
    ['perroquet_robot', 'Perroquet-robot', 'epaule', 'pirate'], ['bottes_pirate', 'Bottes à boucle', 'pieds', 'pirate'], ['pieces_or', 'Pièces d\'or qui tournent', 'autour', 'pirate'],

    ['casquette_mabawa', 'Casquette « PLATA O MABAWA »', 'tete', 'lycee', 'PLATA O MABAWA'], ['ski_front', 'Lunettes de ski sur le front', 'tete', 'lycee'],
    ['peigne', 'Peigne planté dans les cheveux', 'tete', 'lycee'], ['ski_yeux', 'Lunettes de ski sur les yeux', 'visage', 'lycee'],
    ['coelacanthe', 'Cœlacanthe en peluche', 'epaule', 'lycee'],
    /* dessinés mais hors catalogue pour l'instant (T112d) : casquette_barge, casquette_pilaou, bob, perles, ecouteurs, sacoche,
       sac_devant, telephone, bouteille_glacee, bracelet, claquettes, et le haut maillot_foot */

    ['crete_pics', 'Crête à pics', 'tete', 'punk'], ['casque_audio', 'Casque audio', 'tete', 'punk'], ['epingles', 'Épingles à nourrice', 'visage', 'punk'],
    ['badges', 'Badges', 'cou', 'punk'], ['guitare', 'Guitare bricolée', 'dos', 'punk'], ['megaphone', 'Mégaphone', 'main', 'punk'],
    ['bombe', 'Bombe de peinture', 'main', 'punk'], ['enceinte', 'Enceinte bricolée', 'main', 'punk'], ['veste_ecussons', 'Veste à écussons', 'epaule', 'punk'],
    ['rangers', 'Grosses chaussures', 'pieds', 'punk'], ['skate', 'Skate', 'pieds', 'punk'], ['notes', 'Notes de musique', 'autour', 'punk'],

    ['antennes', 'Antennes à ressort', 'tete', 'cyber'], ['antenne_parabole', 'Antenne parabole', 'tete', 'cyber'], ['soudure', 'Lunettes de soudure', 'tete', 'cyber'],
    ['implant', 'Implant neural', 'visage', 'cyber'], ['visiere', 'Visière holo', 'visage', 'cyber'], ['lunettes_ecran', 'Lunettes-écran', 'visage', 'cyber'],
    ['cable_prise', 'Câble à prise', 'cou', 'cyber'], ['turbine_dos', 'Turbine dorsale', 'dos', 'cyber'], ['sac_recup', 'Sac à dos de récupération', 'dos', 'cyber'],
    ['sac_antenne', 'Sac-antenne', 'dos', 'cyber'], ['jetpack', 'Réacteurs à vapeur', 'dos', 'cyber'], ['bras_meca', 'Bras mécanique à pince', 'main', 'cyber'],
    ['cle', 'Clé à molette', 'main', 'cyber'], ['baton_lumineux', 'Bâton lumineux', 'main', 'cyber'], ['drone', 'Drone de poche', 'epaule', 'cyber'],
    ['ressorts', 'Ressorts sous les pieds', 'pieds', 'cyber'], ['aura', 'Aura néon', 'autour', 'cyber'], ['pixels', 'Pluie de pixels', 'autour', 'cyber'],

    ['couronne_feuilles', 'Couronne de feuilles', 'tete', 'nature'], ['couronne_fleurs', 'Couronne de fleurs', 'tete', 'nature'], ['fleur_oreille', 'Fleur de frangipanier à l\'oreille', 'visage', 'nature'],
    ['collier_coquillages', 'Collier de coquillages', 'cou', 'nature'], ['ailes_fee', 'Ailes de fée', 'dos', 'nature'], ['ailes_libellule', 'Ailes de libellule', 'dos', 'nature'],
    ['ailes_roussette', 'Ailes de roussette', 'dos', 'nature'], ['baton_bourgeon', 'Bâton qui bourgeonne', 'main', 'nature'], ['lanterne', 'Lanterne', 'main', 'nature'],
    ['souimanga', 'Souimanga sur l\'épaule', 'epaule', 'nature'], ['lucioles', 'Lucioles', 'autour', 'nature'], ['papillons', 'Papillons', 'autour', 'nature'], ['bulles', 'Bulles du lagon', 'autour', 'nature'],

    ['bonnet', 'Bonnet à pompon', 'tete', 'classique'], ['casquette', 'Casquette sans marque', 'tete', 'classique'], ['frontale', 'Lampe frontale', 'tete', 'classique'],
    ['bandeau', 'Bandeau de sport', 'tete', 'classique'], ['lunettes', 'Lunettes de vue', 'visage', 'classique'], ['pansement', 'Pansement', 'visage', 'classique'],
    ['peinture', 'Peinture néon', 'visage', 'classique'], ['echarpe', 'Écharpe', 'epaule', 'classique'],
    ['kishali', 'Kishali sur les épaules', 'epaule', 'classique'], ['parapluie', 'Parapluie de la saison des pluies', 'main', 'classique'], ['ballon_foot', 'Ballon de foot', 'pieds', 'classique']
  ];
  /* les objets des applications (T133b, famille « applis ») : trois par application, chacun donné par
     un haut fait (jamais acheté). [id, nom, emplacement, application, haut fait, nom du haut fait,
     catégorie, condition]. Les identifiants d'application et de haut fait suivent le compte commun. */
  var APPLIS = [
    ['de_flottille', 'Le dé de la Flottille', 'main', 'quizz_nsi', 'premier-pas', 'Premier pas', 'premiers_pas', 'Suivre ton premier cours-quiz jusqu\'au bout, en classe.'],
    ['chapeau_pion', 'Le chapeau-pion', 'tete', 'quizz_nsi', 'tour-du-plateau', 'Tour du plateau', 'exploration', 'Suivre des cours-quiz de trois thèmes différents du programme.'],
    ['flamme_apprivoisee', 'La flamme apprivoisée', 'autour', 'quizz_nsi', 'rebond', 'Rebond', 'perseverance', 'Trouver la bonne réponse juste après une erreur.'],
    ['micro_paillettes', 'Le micro à paillettes', 'main', 'grand_oral', 'premier-passage', 'Premier passage', 'premiers_pas', 'T\'évaluer après ton premier oral blanc.'],
    ['noeud_chrono', 'Le nœud pap\' à chrono', 'cou', 'grand_oral', 'ni-trop-ni-trop-peu', 'Ni trop ni trop peu', 'maitrise', 'Avoir un plan qui tient en dix minutes (30 à 50 points).'],
    ['projecteur_poursuite', 'Le projecteur de poursuite', 'autour', 'grand_oral', 'vous-avez-un-sujet', 'Vous avez un sujet !', 'creation', 'Avoir une question validée par ton enseignant·e.'],
    ['case_surprise', 'La case-surprise', 'main', 'calendrier', 'premiere-case', 'Première case', 'premiers_pas', 'Ouvrir et valider ta première case du calendrier.'],
    ['bob_fanion', 'Le bob à fanion', 'tete', 'calendrier', 'costaud', 'Costaud', 'maitrise', 'Valider une case au niveau « Costaud ».'],
    ['guirlande_cases', 'La guirlande de cases', 'autour', 'calendrier', 'tous-les-themes', 'Tous les thèmes', 'exploration', 'Valider des cases de trois thèmes différents.'],
    ['monocle_hublot', 'Le monocle-hublot', 'visage', 'gombessa', 'la-luciole-avance', 'La Luciole avance', 'premiers_pas', 'Faire avancer la Luciole avec ton premier programme juste.'],
    ['collier_sonar', 'Le collier-sonar', 'cou', 'gombessa', 'les-grottes-du-gombessa', 'Les grottes du gombessa', 'exploration', 'Atteindre les grottes, à 250 m : finir l\'expédition.'],
    ['bulle_luci', 'La bulle de LUCI', 'epaule', 'gombessa', 'debogage', 'Débogage', 'perseverance', 'Corriger un programme après une erreur, jusqu\'à ce qu\'il marche.'],
    ['casque_carapace', 'Le casque-carapace', 'tete', 'lagon', 'ponte-reussie', 'Ponte réussie', 'premiers_pas', 'Écrire une tortue qui pond sur la plage pendant un match.'],
    ['bebe_tortue', 'Le bébé tortue', 'epaule', 'lagon', 'rematch', 'Rematch', 'perseverance', 'Corriger ta tortue après un match, puis la relancer.'],
    ['palmes_lagon', 'Les palmes du lagon', 'pieds', 'lagon', 'le-parcours', 'Le parcours', 'exploration', 'Finir le parcours des quatre missions.']
  ];
  APPLIS.forEach(function (a) { OBJETS.push([a[0], a[1], a[2], 'applis']); });
  var APPLI_DE = {};
  APPLIS.forEach(function (a) { APPLI_DE[a[0]] = { application: a[3], haut_fait: a[4] }; });
  /* objets retirés à la demande de l'enseignant (24/11) : [emplacement, id, place d'origine dans la liste].
     Une description qui les porte les perd (« aucun ») ; aleatoire garde leur place pour que les tirages ne changent pas. */
  var RETIRES = [['main', 'perche_extensible', 7], ['tete', 'bouchon_mamoudzou', 4]];
  /* anciens identifiants (v3) : repris dans leur nouvel emplacement */
  var COMPAT = { masque: ['visage', 'loup'], chale: ['epaule', 'kishali'], ballon: ['pieds', 'ballon_foot'], monocle_visee: ['visage', 'monocle_pixels'] };
  CATALOGUE.emplacements.forEach(function (e) { CATALOGUE.objets[e.id] = [{ id: 'aucun', nom: 'Rien' }]; });
  OBJETS.forEach(function (o) {
    var e = { id: o[0], nom: o[1], famille: o[3] }; if (o[4]) e.texte = o[4];
    if (APPLI_DE[o[0]]) { e.application = APPLI_DE[o[0]].application; e.haut_fait = APPLI_DE[o[0]].haut_fait; }
    CATALOGUE.objets[o[2]].push(e);
  });
  Object.keys(PALETTES).forEach(function (k) {
    CATALOGUE.couleurs[k] = Object.keys(PALETTES[k]).map(function (id) { return { id: id, couleur: PALETTES[k][id] }; });
  });
  /* palette de chaque champ de couleur de la description */
  var CHAMP_PALETTE = { cheveux: 'cheveux', haut: 'tissu', bas: 'tissu', accent: 'neon', chaussures: 'chaussures', yeux: 'yeux' };

  var MANCHES = { veste: 'longues', maillot: 'courtes', maillot_foot: 'courtes', maillot_mada: 'courtes', maillot_comores: 'courtes', tunique: 'courtes', sweat: 'longues', gilet: 'aucune', debardeur: 'aucune', chemise: 'longues', combinaison: 'longues', tshirt: 'courtes', aucun: 'aucune' };
  var SANS_CORPS = { nuee: 1, esprit: 1 };
  var MAILLOT_PAYS = { maillot_mada: '#d8303a', maillot_comores: '#2f9a4a' };

  var DEFAUT = {
    v: 1, lignee: 'humain', teint: 5, corps: 'moyenne', coiffure: 'court', cheveux: 'noirs',
    haut: 'tshirt', bas: 'pantalon', chaussures: 'baskets',
    objets: { tete: 'aucun', visage: 'aucun', cou: 'aucun', dos: 'aucun', main: 'aucun', epaule: 'aucun', pieds: 'aucun', autour: 'aucun' },
    fauteuil: false, compagnon: 'margouillat',
    couleurs: { haut: 'canard', bas: 'anthracite', accent: 'cyan', chaussures: 'blanches', yeux: 'bruns' }
  };

  var EMPLACEMENTS = CATALOGUE.emplacements.map(function (e) { return e.id; });
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
    EMPLACEMENTS.forEach(function (e) { var v = COMPAT[ob[e]]; if (v && r.objets[v[0]] === 'aucun') r.objets[v[0]] = v[1]; });
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
    /* les maillots aux couleurs d'un pays : le drapeau, sans écusson de fédération, sans marque, sans numéro */
    var haut = MAILLOT_PAYS[d.haut] || couleur('haut', d.couleurs.haut), bas = couleur('bas', d.couleurs.bas);
    return {
      lignee: d.lignee, corps: d.corps, peau: TEINTS[d.teint - 1], cheveux: couleur('cheveux', d.cheveux),
      coiffure: d.coiffure, tenue: d.haut, haut: haut, accent: acc, accent2: acc2, manches: MANCHES[d.haut],
      embleme: fonce(haut, 0.6), dessous: '#ece4d4', motif_c: acc, bug: acc2, motif: NOIR,
      bas_style: d.bas, bas: bas, bande: acc, cable: acc2, piece1: fonce(haut, 0.05), piece2: '#e8b84a',
      chaussure_style: d.chaussures, chaussure: couleur('chaussures', d.couleurs.chaussures), lacet: acc,
      o: d.objets, acc: d.objets.main, chale: mix(acc2, '#e8403a', 0.55), ecran: d.objets.visage === 'lunettes_ecran', lunettes: d.objets.visage === 'lunettes',
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
    arriere(c); jambes(c); objetsPieds(c); torse(c);
    var b = bras(c, pose.bras || 'repos');
    c.BL = b[0]; c.BR = b[1]; c.brasPose = b[2];
    peindreBras(c, c.BL, 0); peindreBras(c, c.BR, 1);
    objetsEpaule(c); objetsCou(c);
    tete(c); cheveuxDevant(c); accessoiresDevant(c); objetsVisage(c); objetsTete(c); tenu(c); objetsAutour(c);
    if (pose.souffle) { c.L.decaler(TY, pose.souffle); c.F.decaler(TY, pose.souffle); }
    c.L.contour(c.lig === 'esprit' ? '#5a4a98' : CONTOUR);
    if (c.cfg.o.autour === 'aura') aura(c);
    if (c.cfg.o.autour === 'aura_energie') auraEnergie(c);
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
    if (style === 'salouva') {
      /* salouva noué à la taille, imprimé d'aujourd'hui : bandes de losanges et de chevrons, ourlet à liseré */
      var s1 = cfg.accent, s2 = clair(bas, 0.55);
      for (y = TY + 6; y < SY0 + 1; y++) {
        k = y - TY - 6;
        for (x = c.tx0 - 1; x <= c.tx1 + 1; x++) {
          var co = bas, u = mod(x - c.tx0 + 1, 6), r5 = mod(k, 6);
          if (y >= SY0 - 1) co = mod(x, 3) ? s1 : '#ffffff';
          else if (r5 === 0) co = mod(x + k, 2) ? s2 : bas;
          else if (r5 === 2 || r5 === 4) co = (u === 2 || u === 3) ? '#ffffff' : bas;
          else if (r5 === 3) co = (u === 1 || u === 4) ? '#ffffff' : (u === 2 || u === 3 ? s1 : bas);
          c.px(x, y, co);
        }
        c.px(c.tx1 + 1, y, fonce(bas, 0.25));
      }
      c.L.hline(c.tx0 - 1, c.tx1 + 1, TY + 6, fonce(bas, 0.3));
      c.px(c.tx1 - 1, TY + 6, s1); c.px(c.tx1, TY + 7, s1); c.px(c.tx1 - 1, TY + 8, fonce(bas, 0.35)); c.px(c.tx1, TY + 9, fonce(bas, 0.35));
      [c.lx0, c.rx0].forEach(function (lx) { c.L.rect(lx + 1, SY0 + 1, c.legW - 1, 1, c.sk); });
    } else if (style === 'jupe_longue') {
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
    } else if (st === 'maillot_foot') {
      /* maillot de foot : col et bandes de côté, un numéro, ni écusson ni marque */
      var clairT = rgb(top)[0] + rgb(top)[1] + rgb(top)[2] > 480, num = clairT ? NOIR : '#ffffff';
      L.hline(CX - 2, CX + 1, TY, acc); c.px(CX - 1, TY + 1, acc); c.px(CX, TY + 1, acc);
      for (y = TY + 1; y < TY + 8; y++) { c.px(tx0, y, acc); c.px(tx0 + 1, y, fonce(acc, 0.2)); c.px(tx1, y, acc); c.px(tx1 - 1, y, fonce(acc, 0.2)); }
      L.carte(CX - 3, TY + 2, ['.x.xxx', 'xx.x.x', '.x.x.x', '.x.xxx'], { x: num });
    } else if (st === 'maillot_mada') {
      /* Madagascar : blanc, rouge, vert, en bandes ; ni écusson, ni marque, ni numéro */
      for (y = TY + 4; y < TY + 8; y++) for (x = tx0; x <= tx1; x++) c.px(x, y, x === tx1 ? '#1f6a3a' : '#2f9a4a');
      L.hline(tx0, tx1, TY + 4, '#ffffff');
      for (y = TY; y < TY + 8; y++) { c.px(tx0, y, '#ffffff'); c.px(tx0 + 1, y, '#ffffff'); }
      L.hline(CX - 2, CX + 1, TY, '#ffffff'); c.px(CX - 1, TY + 1, '#ffffff'); c.px(CX, TY + 1, '#ffffff');
    } else if (st === 'maillot_comores') {
      /* Comores : vert, croissant blanc et quatre étoiles sur la poitrine (emblème du drapeau), liserés jaune, blanc, rouge, bleu ;
         ni écusson de fédération, ni marque, ni numéro */
      L.hline(CX - 2, CX + 1, TY, '#ffffff'); c.px(CX - 1, TY + 1, '#ffffff'); c.px(CX, TY + 1, '#ffffff');
      L.carte(CX - 4, TY + 2, ['.ww..x.', 'w......', 'w...x.x', 'w......', '.ww..x.'], { w: '#ffffff', x: '#ffffff' });
      var LIS = ['#f2c83a', '#ffffff', '#d8303a', '#2a5ad8'];
      for (x = tx0; x <= tx1; x++) c.px(x, TY + 7, LIS[mod(fdiv(x - tx0, 3), 4)]);
      for (y = TY + 1; y < TY + 7; y++) { c.px(tx0, y, LIS[mod(y, 4)]); c.px(tx1, y, LIS[mod(y + 2, 4)]); }
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
      for (y = TY + 1; y < TY + 8; y++) { c.px(tx0, y, '#f2f0ea'); c.px(tx1, y, '#f2f0ea'); }
    } else if (st === 'tshirt' || st === 'aucun') {
      L.rect(CX - 2, TY, 4, 1, SANS_CORPS[c.lig] ? top : c.sk);
      L.hline(tx0 + 1, tx1 - 1, TY + 3, cfg.motif === top ? acc : (rgb(top)[0] + rgb(top)[1] < 160 ? acc : cfg.motif));
      L.hline(tx0 + 1, tx1 - 1, TY + 5, rgb(top)[0] + rgb(top)[1] < 160 ? acc : cfg.motif);
    }
    if (cfg.o.dos === 'sac_antenne' || cfg.o.dos === 'sac_recup' || cfg.o.dos === 'doukabe_dos') {
      for (y = TY; y < TY + 6; y++) { c.px(tx0 + 2, y, '#3a3f58'); c.px(tx1 - 2, y, '#3a3f58'); }
      c.px(tx1 - 2, TY + 3, cfg.accent2);
    }
    if (cfg.o.epaule === 'kishali') {
      var ch = cfg.chale;
      L.hline(tx0 - 2, tx1 + 2, TY, ch); L.hline(tx0 - 3, tx1 + 3, TY + 1, ch); L.hline(tx0 - 3, tx1 + 3, TY + 2, fonce(ch, 0.15));
      for (y = TY + 3; y < TY + 9; y++) { c.px(tx0 + 1, y, ch); c.px(tx0 + 2, y, y < TY + 8 ? ch : fonce(ch, 0.2)); }
      [tx0 + 1, tx0 + 2].forEach(function (x) { c.px(x, TY + 9, NJ); c.px(x, TY + 10, x % 2 ? NJ : ch); });
      for (x = tx0 - 2; x < tx1 + 3; x += 3) { c.px(x, TY + 1, NJ); c.px(x + 1, TY + 2, '#ffffff'); }
      for (y = TY + 4; y < TY + 8; y += 2) c.px(tx0 + 1, y, NJ);
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
        if (side === 1 && cfg.o.main === 'bras_meca') { col = i % 2 ? MET : '#b8c0d4'; if (i === fdiv(n, 2) || i === fdiv(n, 2) + 1) col = NG; c.px(x, y, col); return; }
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
    var cfg = c.cfg, pose = c.pose, yeux0 = pose.yeux || 'ouverts', hy = ey - (EY - HY);
    if (c.lig === 'esprit' && yeux0 === 'ouverts') yeux0 = 'doux';
    var rg = (yeux0 === 'ouverts' || yeux0 === 'grands') ? (pose.regard || 0) : 0;
    var eyes = [[CX - 5 + rg, -1], [CX + 3 + rg, 1]];
    var col = c.lig !== 'esprit' ? NOIR : '#5a4a98';
    eyes.forEach(function (e, idx) {
      var ex = e[0], s = e[1], yeux = pose.clin && idx === 1 ? 'rieurs' : yeux0;
      var iris = cfg.iris;
      if (c.lig === 'mutant' && idx === 1) iris = cfg.taches;
      var lueur = c.lig === 'nuee' || (c.lig === 'mutant' && idx === 1);
      var inner = s < 0 ? ex + 1 : ex, outer = s < 0 ? ex : ex + 1;
      var cIn = s < 0 ? ex + 2 : ex - 1, cOut = s < 0 ? ex - 1 : ex + 2;
      if (yeux === 'rieurs') {
        var yb = ey + 1;
        c.px(inner, yb, col); c.px(outer, yb, col); c.px(cOut, yb + 1, col); c.px(cIn, yb + 1, col);
      } else if (yeux === 'etoiles') {
        var sx = s < 0 ? ex + 1 : ex;
        [[0, 0], [-1, 1], [1, 1], [0, 2]].forEach(function (d) { c.px(sx + d[0], ey + d[1], '#ff9a1a'); });
        [[0, -1], [-2, 1], [2, 1], [0, 3]].forEach(function (d) { c.px(sx + d[0], ey + d[1], '#ffc81a'); });
        c.px(sx, ey + 1, '#ffffff');
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
          c.px(rg > 0 ? ex + 1 : (rg < 0 ? ex : inner), ey, '#ffffff');
          if (yeux === 'tristes') { c.px(outer, ey + 2, '#bdefff'); c.px(inner, ey + 2, '#bdefff'); }
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
      eyes.forEach(function (e, idx) {
        var ex = e[0] - rg, s = e[1], inner = s < 0 ? ex + 1 : ex, outer = s < 0 ? ex : ex + 1;
        if (yeux0 === 'tristes') { c.px(inner, ey - 3, bc); c.px(outer, ey - 2, bc); }
        else if (yeux0 === 'concentres') { c.px(inner, ey - 1, bc); c.px(outer, ey - 2, bc); }
        else if (yeux0 === 'grands' || yeux0 === 'etoiles') c.L.rect(ex - (s < 0 ? 1 : 0), ey - 3, 3, 1, bc);
        else if (pose.clin && idx === 1) c.L.rect(ex, ey - 1, 2, 1, bc);
        else c.L.rect(ex, ey - 2, 2, 1, bc);
      });
    }
    if (c.lig !== 'nuee') [CX - 8, CX - 7, CX + 6, CX + 7].forEach(function (xj) { c.px(xj, ey + 3, '#ff7fa0', (xj === CX - 7 || xj === CX + 6) ? (pose.joues ? 0.9 : 0.6) : (pose.joues ? 0.65 : 0.4)); });
    /* larmes en cascade (triste) */
    if (pose.cascade !== undefined) {
      [CX - 5, CX + 4].forEach(function (x) {
        for (var y = ey + 3; y < ey + 6; y++) c.fx(x, y, '#5ac8ff', 0.95);
        c.fx(x, ey + 6 + pose.cascade, '#5ac8ff', 0.9); c.fx(x, ey + 8 + pose.cascade, '#bdefff', 0.8);
      });
    }
    /* traits d'abattement sur le front (code des mangas) */
    if (pose.ombre) [CX - 4, CX - 1, CX + 2].forEach(function (x) { for (var y = hy + 3; y < hy + 7; y++) c.fx(x, y, '#3a4aa8', 0.6); });
    var my = ey + 4;
    var BM = { sourire: ['d..d', '.dd.'], rire: ['dddd', 'drrd', '.dd.'], grand_rire: ['dddddd', 'drrrrd', '.drrd.', '..dd..'], triste: ['.dd.', 'd..d'], langue: ['ddd.', '..p.', '..p.'], neutre: ['....', '.dd.'], o: ['.dd.', 'd..d', '.dd.'], petit: ['....', '.d..'], vague: ['....', 'd.d.', '.d.d'] };
    var pal = { d: SANS_CORPS[c.lig] ? '#5a4a98' : '#5a2a35', r: '#e8606a', p: '#ff8fb0' };
    var bo = pose.bouche || 'sourire';
    c.L.carte(bo === 'grand_rire' ? CX - 3 : CX - 2, my, BM[bo] || BM.sourire, pal);
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

  /* ════════════════════════════════════════════
     LES OBJETS, PAR EMPLACEMENTS
     tête, visage, cou, dos, main, épaules, pieds, autour : un objet par
     emplacement, cumulables, portables par tous les avatars.
     Dessins originaux : on reprend les codes d'un genre, jamais l'objet
     d'une œuvre. Les « clins d'œil » passent par le nom, pas par la forme.
     ════════════════════════════════════════════ */
  Calque.prototype.ellipseA = function (cx, cy, rx, ry, c, a) {
    for (var y = Math.trunc(cy - ry) - 1; y < Math.trunc(cy + ry) + 2; y++) for (var x = Math.trunc(cx - rx) - 1; x < Math.trunc(cx + rx) + 2; x++) {
      var dx = (x + 0.5 - cx) / rx, dy = (y + 0.5 - cy) / ry;
      if (dx * dx + dy * dy <= 1) this.px(x, y, typeof c === 'function' ? c(x, y) : c, true, a);
    }
  };
  var GECKO = ['..g..', '.ggg.', 'g.g.g', '..g..', 'g.g.g', '...gg'];

  /* couleurs symboliques des cartes : A, B les néons, H le haut, S la peau, C les cheveux */
  function teinte(c, v) {
    if (v === 'A') return c.cfg.accent; if (v === 'B') return c.cfg.accent2; if (v === 'H') return c.cfg.haut;
    if (v === 'S') return c.sk; if (v === 'C') return c.hc; return v;
  }
  /* pose une carte de pixels ; « . » est transparent ; une couleur [c, a] va sur le calque des lueurs */
  function poser(c, rows, pal, AX, AY, a, miroir) {
    for (var j = 0; j < rows.length; j++) for (var i = 0; i < rows[j].length; i++) {
      var ch = rows[j].charAt(i);
      if (ch === '.' || !Object.prototype.hasOwnProperty.call(pal, ch)) continue;
      var v = pal[ch], x = miroir ? AX + a[0] - i : AX - a[0] + i, y = AY - a[1] + j;
      if (Array.isArray(v)) c.fx(x, y, teinte(c, v[0]), v[1]); else c.px(x, y, teinte(c, v));
    }
  }
  function ligne(c, x0, y0, x1, y1, col, ep) {
    var n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)) || 1;
    for (var k = 0; k <= n; k++) {
      var x = Math.round(x0 + (x1 - x0) * k / n), y = Math.round(y0 + (y1 - y0) * k / n);
      c.px(x, y, typeof col === 'function' ? col(k, n) : col);
      if (ep > 1) c.px(x + 1, y, typeof col === 'function' ? col(k, n) : col);
    }
  }
  function oterDessus(c, hy) {
    for (var y = hy - 16; y < hy; y++) for (var x = X0 - 5; x <= X1 + 5; x++) { c.L.ote(x, y); c.L.m.delete(y * K + x); c.F.ote(x, y); }
  }
  /* largeur du crâne, rangée par rangée (comme la coiffure « casque ») */
  function crane(hy, y) {
    var k = y - hy;
    if (k < -1) return null; if (k === -1) return [X0 + 4, X1 - 4]; if (k === 0) return [X0 + 2, X1 - 2]; if (k === 1) return [X0 + 1, X1 - 1];
    return [X0, X1];
  }
  function raser(c, hy) {
    var st = mix(c.sk, c.hc, 0.45);
    for (var y = hy - 1; y <= hy + 3; y++) { var r = crane(hy, y); for (var x = r[0]; x <= r[1]; x++) c.px(x, y, st); }
  }
  function pointe(c, ax, ay, by, bx0, bx1, col, tip) {
    for (var y = ay; y <= by; y++) {
      var t = (y - ay) / Math.max(1, by - ay), a = Math.round(ax + (bx0 - ax) * t), b = Math.round(ax + (bx1 - ax) * t);
      for (var x = Math.min(a, b); x <= Math.max(a, b); x++) c.px(x, y, y - ay < 2 ? tip : col);
    }
  }
  function collier(c, col1, col2, special) {
    var half = c.tw / 2 - 1;
    for (var x = c.tx0 + 1; x <= c.tx1 - 1; x++) {
      var u = (x - CX + 0.5) / half, y = TY - 1 + Math.round(5 * (1 - u * u));
      c.px(x, y, (x % 3 === 0) ? col2 : col1); c.px(x, y + 1, (x % 3 === 1) ? col2 : fonce(col1, 0.12));
    }
    if (special) poser(c, special.r, special.p, CX, TY + 5, special.a);
  }

  /* ── les cartes de pixels (objets simples) ──
     ou : main (dans la main), tete, visage, cou, dos, epg / epd (épaule gauche / droite),
     pieds (une carte par pied, en miroir à gauche) ; a : point d'accroche dans la carte ;
     f : plusieurs images (animation) ; clair : le chapeau remplace le haut du crâne ;
     chaine : couleur du cordon qui monte au cou ; lueur : [col, rang, couleur]. */
  var OR = '#c8902a', OR2 = '#f2c14e', MET = '#9aa3b8', MET2 = '#d8dce8', BOIS = '#a8784a', BOIS2 = '#6b4a2e', BLANC = '#f8f6f0';
  /* une manique matelassée : « m » devient des carreaux de 2 px, puis les coquillages cousus en désordre */
  function damier(rows, coquillages) {
    var r = rows.map(function (l, y) { return l.replace(/m/g, function (ch, x) { return (fdiv(x, 2) + fdiv(y, 2)) % 2 ? 'w' : 'r'; }); });
    coquillages.forEach(function (q) {
      [q[2], q[3]].forEach(function (motif, j) { var l = r[q[1] + j]; r[q[1] + j] = l.slice(0, q[0]) + motif + l.slice(q[0] + motif.length); });
    });
    return r;
  }
  var SPR = {
    /* ─ héros ─ */
    bottes_heros: { ou: 'pieds', a: [1, 5], r: ['BBBBB.', '.AAAA.', '.AAAA.', '.AAAAA', '.AAAAAA', '.kkkkkk'], p: { A: 'A', B: 'B', k: '#2a2a35' } },
    /* ─ pirates ─ */
    tricorne: { ou: 'tete', clair: 1, a: [11, 7], r: [
      '...............BB.....', '..............BB......', '........kkkkkB........', '.......kkkkkkkk.......',
      'k.....kkkkkkkkkk.....k', 'kk...kkkkkkkkkkkk...kk', 'gkk.kkkkkAAkkkkkkk.kkg', '.gkkkkkkkAAkkkkkkkkkg.',
      '..ggkkkkkkkkkkkkkkgg..', '....gggggkkkkggggg....', '........gkkg..........'], p: { k: '#2a2440', g: OR2, A: 'A', B: 'B' } },
    cache_oeil: { ou: 'visage', a: [7, 1], r: ['.kkkk.', 'kkAkkk', 'kkkkkk', '.kkkk.'], p: { k: '#1f1a24', A: 'A' } },
    boussole: { ou: 'cou', a: [3, -3], chaine: OR, f: [
      ['..ggg..', '.gwLwg.', 'gwwOwwg', 'gwwOwwg', 'gwwkwwg', '.gwwwg.', '..ggg..'],
      ['..ggg..', '.gwwLg.', 'gwwwOwg', 'gwwOwwg', 'gwkwwwg', '.gwwwg.', '..ggg..']],
      p: { g: OR, w: BLANC, O: '#f08a2a', L: '#4fae5a', k: '#2a2a35' } },
    longue_vue: { ou: 'main', a: [1, 7], r: ['......gg.', '.....gGGg', '....bbgg.', '...bbbb..', '..kbbk...', '.bbbb....', 'bbbb.....', 'kbb......'],
      p: { g: OR2, G: '#3ff0ff', b: '#c8963b', k: '#5a3a1a' } },
    carte_tresor: { ou: 'main', gros: 1, a: [3, 6], r: ['RpppppR', 'RppxpxR', 'RpppxpR', 'RppxpxR', 'RrprppR', 'RpppppR'], p: { p: '#f2dca0', R: '#b0783a', x: '#c8302a', r: '#c8302a' } },
    bouteille_message: { ou: 'main', gros: 1, a: [1, 6], r: ['.k.', '.g.', 'ggg', 'gpg', 'gpg', 'gpg', 'GGG'], p: { k: '#8a5a3a', g: '#6ad8a0', G: '#3a9a6a', p: '#f2dca0' } },
    perroquet_robot: { ou: 'epd', a: [-3, 11], f: [
      ['..rr....', '...rr...', '..tttt..', '.ttwcmm.', '.ttttmmm', '.tttMtm.', '.tTTTtt.', '.tTTTt..', '..tTTt..', '..tttV..', '..gg.VV.', '......V.'],
      ['.r..r...', '..rr....', '..tttt..', '.ttwcmm.', '.tttt..m', '.tttMmm.', '.tTTTtt.', '.tTTTt..', '..tTTt..', '..tttV..', '..gg.VV.', '......V.']],
      p: { r: '#ff4fb8', t: '#3fb8a0', w: BLANC, c: '#2a8ad8', m: MET2, M: MET, T: '#ffd23a', V: '#8a5bff', g: '#5a5f7a' } },
    bottes_pirate: { ou: 'pieds', a: [1, 5], r: ['bBBBBb', '.bbbb.', '.bgbb.', '.bbbbb', '.bbbbbb', '.kkkkkk'], p: { b: '#6b4a2e', B: '#9a7a52', g: OR2, k: '#2a1a10' } },
    /* ─ le style du lycée : ce que portent les élèves, sans marque ni logo ─ */
    telephone: { ou: 'main', a: [1, 7], lueur: [2, 3, '#ffffff'], f: [
      ['.kkkk.', 'kKwGgk', 'kKKgGk', 'kGgwgk', 'kgGgGk', 'kGgGgk', 'kgGgwk', 'kGgGgk', '.kkkk.'],
      ['.kkkk.', 'kKKGgk', 'kKKgGk', 'kGgGgk', 'kgwgGk', 'kGgGgk', 'kgGgGk', 'kGwGgk', '.kkkk.']],
      p: { k: '#2a2f44', K: '#5a5f7a', g: 'A', G: '#ffffff', w: '#fff6c8' } },
    bouteille_glacee: { ou: 'main', a: [2, 9], f: [
      ['.bbb.', '.bbb.', '.lll.', 'llwll', 'lwiil', 'lliwl', 'lwiil', 'llill', 'lwlll', 'lllll', '.lll.'],
      ['.bbb.', '.bbb.', '.lll.', 'llwll', 'lwiil', 'lliwl', 'lwiil', 'llill', 'lwlll', 'lllll', '.lll.']],
      p: { b: '#3f6ad8', l: '#9ad8f0', w: '#e8f8ff', i: '#ffffff' } },
    coelacanthe: { ou: 'epg', a: [10, 7], f: [
      ['.....bb.....', '..bbbbbb..bb', '.bwwbbsbbbbb', 'bbwkbbbbsbb.', 'bbbbbsbbbbbb', '.brbbbbsbb.b', '..bbfb.fb...', '...f....f...'],
      ['.....bb.....', '..bbbbbb...b', '.bwwbbsbbbbb', 'bbwkbbbbsbbb', 'bbbbbsbbbbb.', '.brbbbbsbbbb', '..bbfb.fb...', '..f......f..']],
      p: { b: '#3a5ab8', s: '#c8dcf8', w: '#ffffff', k: '#1b1530', r: '#ff9ab8', f: '#2a3a8a' } },
    claquettes: { ou: 'pieds', a: [1, 5], r: ['.wwww.', '.AAAA.', '.wwww.', '.wwwww.', 'kkkkkkk', 'sssssss'], p: { w: BLANC, A: 'A', k: '#2a2f44', s: '#c8ccd8' } },
    /* ─ punk ─ */
    badges: { ou: 'cou', a: [4, -1], r: ['.y......', 'yky..r..', '.y..rwr.', '.....r..', '...c....', '..ckc...', '...c....'],
      p: { y: '#f2d14b', r: '#ff4fb8', c: '#3ff0ff', k: '#1b1530', w: '#ffffff' } },
    rangers: { ou: 'pieds', a: [1, 5], r: ['.kkkk.', '.kAkk.', '.kkAk.', '.kAkkk', 'kkkkkkk', 'ggggggg', 'g.g.g.g'], p: { k: '#2a2a35', A: 'A', g: '#5a5f7a' } },
    megaphone: { ou: 'main', a: [2, 6], f: [
      ['......RR....', '....RRwR.v..', 'kkRRwwwR..v.', 'kkRRwwwR..v.', '....RRwR.v..', '......RR....', '..k.........'],
      ['......RR....', '....RRwR..v.', 'kkRRwwwR.v.v', 'kkRRwwwR.v.v', '....RRwR..v.', '......RR....', '..k.........']],
      p: { R: '#e8403a', w: BLANC, k: '#3a3f58', v: ['A', 0.9] } },
    /* ─ cyber ─ */
    antenne_parabole: { ou: 'tete', a: [-2, 8], f: [
      ['..A.....', '..k.....', 'd.k..d..', '.dDDDd..', '..ddd...', '...s....', '...s....', '..sss...'],
      ['.v.v.v..', '..k.....', 'd.k..d..', '.dDDDd..', '..ddd...', '...s....', '...s....', '..sss...']],
      p: { A: 'A', v: ['A', 0.7], k: '#5a5f7a', d: '#c8ccd8', D: '#eef0f6', s: MET } },
    cable_prise: { ou: 'cou', a: [5, 0], f: [
      ['.cccccccc..', '.c......c..', '.c......c..', 'ooo.....c..', 'oKo....ppp.', 'ooo....ppp.', '.......y.y.', '........z..'],
      ['.cccccccc..', '.c......c..', '.c......c..', 'ooo.....c..', 'oKo....ppp.', 'ooo....ppp.', '.......y.y.', '...........']],
      p: { c: '#2a2f44', o: '#f08a2a', K: '#2a2a35', p: '#e8e0d0', y: OR2, z: ['#e8ff3a', 0.95] } },
    ressorts: { ou: 'pieds', a: [1, -1], f: [['.sss.', 's...s', '.sss.', 's...s'], ['sssss', '.sss.']], p: { s: '#c8ccd8' } },
    /* ─ nature ─ */
    souimanga: { ou: 'epg', a: [9, 6], f: [
      ['...gg..', '..gGgg.', 'bbgkgg.', 'b.gggg.', '..rrrgg', '..yyyyt', '...ff.t'],
      ['..gg...', '.gGgg..', 'bgkgg..', '.bgggg.', '..rrrgg', '..yyyyt', '...ff.t']],
      p: { g: '#2a9a6a', G: '#5fe0c0', b: '#2a2a35', k: '#1b1530', r: '#e8503a', y: '#f2d14b', t: '#2a6a5a', f: MET } },
    fleur_oreille: { ou: 'visage', a: [12, 3], r: ['.ww..', 'wwyww', '.yoy.', 'wwyww', '.w.w.'], p: { w: '#ffffff', y: '#f8e08a', o: '#f2b030' } },
    baton_bourgeon: { ou: 'main', a: [2, 8], lueur: [2, 0, '#fff27a'], f: [
      ['..y..', 'gg.gg', '.gwg.', '..w..', '..W..', '..w..', '..w..', '..W..', '..w..', '..w..'],
      ['y.y.y', 'gg.gg', '.gwg.', '..w..', '..W..', '..w..', '..w..', '..W..', '..w..', '..w..']],
      p: { y: '#fff27a', g: '#5fd06a', w: BOIS, W: BOIS2 } },


    /* ─ les gimmicks de la classe ─ */
    ventilateur: { ou: 'main', a: [3, 9], f: [
      ['..ggg..', '.g.b.g.', 'g.bbb.g', 'gbbkbbg', 'g.bbb.g', '.g.b.g.', '..ggg..', '...h...', '...h...', '...h...'],
      ['..ggg..', '.gb.bg.', 'g.bbb.g', 'g.bkb.g', 'g.bbb.g', '.gb.bg.', '..ggg..', '...h...', '...h...', '...h...']],
      p: { g: '#c8ccd8', b: '#7ad8ff', k: '#3a3f58', h: '#3a3f58' } },
    multiprise: { ou: 'cou', a: [4, -4], chaine: '#2a2f44', r: ['ppppppppp', 'pkpkpkpRp', 'ppppppppp'], p: { p: '#f4f4ee', k: '#2a2a35', R: '#e8403a' } },
    souris_marche: { ou: 'epd', a: [-3, 5], f: [
      ['....mmm.', '..mmmmmm', '.mmmlmmk', 'cmmmmmmm', 'c.f..f..', '.c......'],
      ['....mmm.', '..mmmmmm', '.mmmlmmk', 'cmmmmmmm', 'c..f..f.', 'c.......']],
      p: { m: '#e4e8f0', l: '#3ff0ff', k: '#1b1530', c: '#3a3f58', f: '#ff9ac8' } },
    cle_usb: { ou: 'cou', a: [2, -3], chaine: '#3a3f58', lueur: [2, 3, '#ffffff'], r: ['.kk.', '.oo.', 'bbbb', 'bAAb', 'bAAb', 'bbbb'], p: { k: '#c8ccd8', o: '#5a5f7a', b: '#2a2f44', A: 'A' } },
    feutre: { ou: 'main', gros: 1, a: [1, 6], lueur: [1, 0, '#3ff0ff'], f: [['.A.', 'www', 'www', 'www', 'www', 'AAA', 'AAA'], ['vA.', 'www', 'www', 'www', 'www', 'AAA', 'AAA']], p: { A: 'A', w: BLANC, v: ['A', 0.8] } },
    telecommande: { ou: 'main', gros: 1, a: [1, 6], f: [['.r.', 'kkk', 'kwk', 'kAk', 'kkk', 'kAk', 'kkk'], ['...', 'kkk', 'kwk', 'kAk', 'kkk', 'kAk', 'kkk']], p: { r: '#ff3a3a', k: '#2a2f44', w: '#c8ccd8', A: 'A' } },
    /* ─ clins d'œil : le nom fait le clin d'œil, la forme est à nous ─ */
    manique_infini: { ou: 'main', a: [6, 10], r: damier([
      '.....ll.....', '....l..l....', '...mmmmmm...', '..mmmmmmmm..', '..mmmmmmmmm.', 'mm.mmmmmmmm.',
      'mmm.mmmmmmm.', 'mmmmmmmmmmm.', '.mmmmmmmmmm.', '..mmmmmmmm..', '..dddddddd..', '..dddddddd..'],
      [[5, 4, 'sS', 'Ss'], [8, 7, 'sS', 'SS'], [3, 8, 'Ss', 'ss']]),
      p: { r: '#d8503a', w: '#f8f0e0', l: '#a8382a', d: '#a8382a', s: '#f4e2c8', S: '#c8a078' } },
    louche_tonnerre: { ou: 'main', a: [4, 11], f: [
      ['..cccc...', '.cccccc..', '.CCCCCC..', '..y..y...', '..bbbb...', '.bBBBBb..', '..bBBb...', '....h....', '....h....', '....h....', '....h....', '....h....'],
      ['..cccc...', '.cccccc..', '.CCCCCC..', '...y..y..', '..bbbb...', '.bBBBBb..', '..bBBb...', '....h....', '....h....', '....h....', '....h....', '....h....']],
      p: { c: '#eef2fa', C: '#b8c4d8', y: '#e8ff3a', b: '#c8ccd8', B: '#8a92a8', h: MET } },
    couvercle_liberte: { ou: 'main', a: [5, 6], r: [
      '....kk.....', '...kkkk....', '..llwllll..', '.lDLLLLgLl.', 'lLLLLLLLgLl', 'llllllllll.', '.tTtT......', '.TtTt......', '..tTt......', '..T.t......'],
      p: { k: '#3a3f58', l: '#c8ccd8', L: '#a8b0c4', w: '#f4f6fa', D: '#7a8298', g: '#3fbf4a', t: '#f2f0ea', T: '#3f6ad8' } },
    passoire_pensee: { ou: 'tete', clair: 1, a: [9, 4], r: [
      '...A..........A...', '....m........m....', '.....m......m.....', '......llllll......', '....llLoLLoLll....',
      '...lLLLLoLLLLLl...', '..lLoLLLLLLoLLLl..', '..lLLLLoLLLLLLLl..', 'hRRRRRRRRRRRRRRRRh'],
      p: { A: 'A', m: MET, l: '#e4e8f0', L: '#b8c0d4', o: '#5a5f7a', R: '#8a92a8', h: '#5a5f7a' } },
    lunettes_rayons: { ou: 'visage', a: [10, 2], r: [
      '....y..y....y..y....', '....ffff....ffff....', 'ffffkwkkffffkwkkffff', '...fkkkkf..fkkkkf...', '....ffff....ffff....', '...y....y..y....y...'],
      p: { y: '#ffd23a', f: '#ffb21a', k: '#2a2440', w: '#7a6ab8' } },
    pelote_voisinage: { ou: 'main', a: [2, 9], r: ['....wwwww', '....w.w.w', '....wwwww', '....w.w.w', '....wwwww', '...w.....', '..w......', '.ppp.....', 'pPpPp....', 'ppppp....', '.ppp.....'],
      p: { w: BLANC, p: '#ff9ac8', P: '#d8608a' } },
    coeur_capsule: { ou: 'cou', a: [3, -1], lueur: [3, 3, '#ffd23a'], r: ['tr.r.rt', 'rRRRRRr', '.RyYyR.', 'rRYwYRr', '.RyYyR.', 'rRRRRRr', 'tr.r.rt'],
      p: { t: '#e8e0c8', r: '#c8402a', R: '#e8603a', y: '#ffd23a', Y: '#fff08a', w: '#ffffff' } },
    ceinture_tout_ranger: { ou: 'cou', a: [7, -2], r: ['..y.......P...', '..yy......L...', '...yy.....L.o.', '.DDDD....DDoOo', 'bbbbbbGGGbbbbb', 'bDDDDbGkGbDDDb', '.DDDD.GGG.DDD.'],
      p: { y: '#5fbf8a', P: '#ff9ac8', L: OR2, o: MET2, O: '#5a5f7a', D: '#8a6a42', b: '#3a2a1a', G: OR2, k: '#8a5a1a' } },
    corde_franchise: { ou: 'main', a: [0, 1], f: [
      ['W.......', 'W.......', 'g.......', 'g......W', 'g......W', '.g.....g', '.g....g.', '..gggg..'],
      ['W.......', 'W.......', 'g.....W.', 'g.....W.', 'g.....g.', '.g....g.', '.g...g..', '..ggg...']],
      p: { W: BOIS, g: OR2 } },
    eclairs_chocolat: { ou: 'pieds', a: [2, 2], r: ['.cwcwcc', 'ppppppp', '.PPPPP.'], p: { c: '#5a3420', w: '#f8f0e0', p: '#d8a058', P: '#b07838' } },
    cornes_zebu: { ou: 'tete', a: [10, 6], r: ['k..................k', 'c..................c', 'c..................c', '.c................c.', '..cc............cc..', '...cc..........cc...', '....rAAAAAAAAAAr....'],
      p: { k: '#4a3a2a', c: '#f2e6c8', r: '#ff7fa0', A: 'A' } },
    mangue_etoiles: { ou: 'main', a: [3, 9], r: [
      '...ncwwwwwww', '...n.ywywywy', '..ggg.wwwwwww', '.gggGG', 'ggggGGG', 'gggGGYY', 'ggGGYYY', '.gGYYYY', '..GYYYo', '...YYo.'],
      p: { n: '#6b4a2e', c: '#c8ccd8', w: '#ffffff', y: '#c87a10', g: '#4fae4a', G: '#a8d040', Y: '#f2c83a', o: '#f08a2a' } },
    calculette_9000: { ou: 'cou', a: [3, -3], chaine: '#3a3f58', r: ['kkkkkkk', 'ksdsdsk', 'ksdsdsk', 'kkkkkkk', 'kbAbAbk', 'kbbbbbk', 'kkkkkkk'],
      p: { k: '#2a2f44', s: '#b8f8a0', d: '#1f5a2a', b: '#c8ccd8', A: 'A' } },
    grenouille_porte_monnaie: { ou: 'cou', a: [7, -4], chaine: '#c8453d', r: ['....gg..gg', '....gwkggwk', '....gggggggg', '....ggrrrrgg', '....gGGyGGGg', '.....gggggg.'],
      p: { g: '#5fbf4a', G: '#8ad87a', w: '#ffffff', k: '#1b1530', r: '#2a5a2a', y: OR2 } },
    bateau_mouton: { ou: 'main', a: [4, 6], r: ['......ww.', '.....wwww', '..p..wkkw', '.ppp..kk.', 'ppppppppp', '.PPPPPPP.', '..PPPPP..'],
      p: { w: '#ffffff', k: '#3a2a2a', p: BLANC, P: '#c8d0e0' } },
    tresor_une_piece: { ou: 'main', gros: 1, a: [3, 7], lueur: [2, 2, '#ffe680'], r: ['..ggg..', '.gGGGg.', 'gwGkGGg', 'gGkkGGg', 'gGGkGGg', '.gGkGg.', '..ggg..'],
      p: { g: OR, G: OR2, k: '#a8781a', w: '#fff6c8' } },
    boussole_gouter: { ou: 'cou', a: [3, -3], chaine: BOIS2, f: [
      ['..ggg..', '.gwLwg.', 'gwwOwwg', 'gwwOwwg', 'gwwkwwg', '.gwwwg.', '..ggg..'],
      ['..ggg..', '.gwwLg.', 'gwwwOwg', 'gwwOwwg', 'gwkwwwg', '.gwwwg.', '..ggg..']],
      p: { g: '#4a6fa5', w: BLANC, O: '#f08a2a', L: '#4fae5a', k: '#e8403a' } },
    crochet_tricot: { ou: 'main', a: [1, 9], r: ['hn......', '.n......', '.ny.....', '.n.y....', '.n..y...', '.n...y..', '.n..BBB.', '.n.BbBbB', '.n.BBbBB', '.n..BBB.'],
      p: { h: MET, n: MET2, y: '#ff9ac8', B: 'B', b: '#ffffff' } },
    perle_noire: { ou: 'cou', a: [3, -3], chaine: '#e8e0f0', r: ['.sssss.', 'sNNkwNs', 'sNNkkNs', 'sSSSSSs', '.sssss.'],
      p: { s: '#a898c8', N: '#f0e8ff', k: '#1b1530', w: '#9a8ad8', S: '#c8b8e8' } },
    kraken_peluche: { ou: 'epg', a: [10, 6], f: [
      ['..pppp..', '.pPPPPp.', 'pPPPPPPp', 'pPwkPwkp', 'pRPPPPRp', '.pPmmPp.', 'p.p.p.p.', 'p.p..p.p', '.p.p.p..'],
      ['..pppp..', '.pPPPPp.', 'pPPPPPPp', 'pPwkPwkp', 'pRPPPPRp', '.pPmmPp.', '.p.p.p.p', 'p.p.p..p', 'p..p.p..']],
      p: { p: '#9a4ab8', P: '#c87ae8', w: '#ffffff', k: '#1b1530', R: '#ff7fa0', m: '#6a2a5a' } },
    maki_sushi: { ou: 'main', gros: 1, a: [3, 7], r: ['..kkk..', '.kwwwk.', 'kwbbbwk', 'kwobowk', 'kwbdbwk', '.kwwwk.', '..kkk..'],
      p: { k: '#1f2a24', w: BLANC, b: '#8a6a4a', o: '#f0a030', d: '#3a2a2a' } },
    barges_pieds: { ou: 'pieds', a: [2, 3], r: ['...rr..', 'wwwwwww', 'bbbbbbb', '.wwwww.'], p: { r: '#e8403a', w: '#eef2fa', b: '#3f6ad8' } },
    bottes_conserve: { ou: 'pieds', a: [1, 5], r: ['lllll', 'sSsSs', 'AAAAA', 'AwAwA', 'sSsSs', 'lllll'], p: { l: '#eef0f6', s: '#b8c0d4', S: MET, A: 'A', w: '#ffffff' } },

    /* ─ les objets des applications (T133b) : accrochés au corps, ils suivent la main, la tête et les épaules ─ */
    de_flottille: { ou: 'main', a: [1, 5], f: [
      ['wwwwwwg', 'wkwwwwg', 'wwwwwwg', 'wwwkwwg', 'wwwwwwg', 'wwwwwkg', 'ggggggg'],
      ['wwwwwwg', 'wkwwwkg', 'wwwwwwg', 'wwwkwwg', 'wwwwwwg', 'wkwwwkg', 'ggggggg']], p: { w: '#f4f1ff', k: '#1b1530', g: '#b9b3d6' } },
    chapeau_pion: { ou: 'tete', clair: 1, a: [7, 12], r: [
      '......ccc......', '.....cCCwc.....', '.....cCCCc.....', '.....cCCCc.....', '......ccc......', '......cCc......', '.....cCCCc.....',
      '....cCCCCCc....', '...cCCCCCCCc...', '..cCCCCCCCCCc..', '.cCCCCCCCCCCCc.', 'ccccccccccccccc', '.kkkkkkkkkkkkk.'], p: { c: '#1f9ab0', C: '#8ae8f0', w: '#ffffff', k: '#13607a' } },
    micro_paillettes: { ou: 'main', gros: 1, a: [2, 5], f: [
      ['.mMm.', 'mMwMm', 'mMMMm', '.mMm.', '..k..', '..k..', '..k..', '..k..'],
      ['.mwm.', 'mMMMm', 'mMMwm', '.mMm.', '..k..', '..k..', '..k..', '..k..']], p: { m: '#c8ccd8', M: '#8a90a8', w: '#ffe14a', k: '#2a2440' } },
    noeud_chrono: { ou: 'cou', a: [5, 1], r: ['pp.......pp', 'ppppwwwpppp', 'pppwwkwwppp', 'ppppwwwpppp', 'pp.......pp'], p: { p: '#8a5bff', w: '#f4f1ff', k: '#1b1530' } },
    case_surprise: { ou: 'main', a: [1, 6], f: [
      ['y.....y', '.y.y.y.', 'bbbbbbb', 'bBBBBBb', 'bBnnBBb', 'bBBBBBb', 'bbbbbbb'],
      ['.y.y.y.', 'y.....y', 'bbbbbbb', 'bBBBBBb', 'bBnnBBb', 'bBBBBBb', 'bbbbbbb']], p: { y: '#ffe14a', b: '#c8302a', B: '#f4f1ff', n: '#1b1530' } },
    bob_fanion: { ou: 'tete', clair: 1, a: [10, 9], r: [
      '..............fFF...', '..............fFFFF.', '..............f.....', '.....bbbbbbbbbf.....', '....bbbbbbbbbbbb....', '...bbbbbbbbbbbbbb...',
      '...BBBBBBBBBBBBBB...', '..bbbbbbbbbbbbbbbb..', 'bbbbbbbbbbbbbbbbbbbb', 'b..................b'], p: { b: '#3fb8a0', B: '#ff4fb8', f: '#5a3a1a', F: '#ffe14a' } },
    monocle_hublot: { ou: 'visage', a: [8, 3], r: ['..ggg..', '.gcccg.', 'gcCcccg', 'gcccccg', 'gcccccg', '.gcccg.', '..ggg..'], p: { g: '#c8963b', c: ['#7ad8ff', 0.45], C: ['#ffffff', 0.9] } },
    collier_sonar: { ou: 'cou', a: [2, -3], chaine: '#1f8a8a', f: [
      ['.ttt.', 'tTTTt', 'tTkTt', 'tTTTt', '.ttt.'], ['.ttt.', 'tTTTt', 'tTkTt', 'tTTTt', '.ttt.']], p: { t: '#1f8a8a', T: '#8ae8f0', k: '#1b1530' } },
    bulle_luci: { ou: 'epd', a: [-4, 13], f: [
      ['..ii..', '.bbbb.', 'bBBBBb', 'bBkkBb', 'bBBBBb', '.bbbb.', '......'], ['......', '..ii..', '.bbbb.', 'bBBBBb', 'bBkkBb', 'bBBBBb', '.bbbb.']], p: { b: '#3a9ad8', B: '#bdefff', k: '#1b1530', i: '#ffe14a' } },
    casque_carapace: { ou: 'tete', clair: 1, a: [9, 7], r: [
      '.......ggggg.......', '.....ggGgggGgg.....', '...ggGgggGgggGgg...', '..gGgggGgggGgggGg..', '.ggggGgggGgggGgggg.', 'gGgggGgggGgggGggggg', 'bbbbbbbbbbbbbbbbbbb', '.b...............b.'], p: { g: '#3f7a35', G: '#8ac85a', b: '#c8a060' } },
    bebe_tortue: { ou: 'epg', a: [12, 5], f: [
      ['hh..sss..', 'kh.sSsSs.', 'hhsSsSsSs', '...sssss.', '...f...f.'], ['.........', 'hh..sss..', 'kh.sSsSs.', 'hhsSsSsSs', '...sssss.']], p: { s: '#3f7a35', S: '#8ac85a', h: '#9ad07a', k: '#1b1530', f: '#9ad07a' } },
    palmes_lagon: { ou: 'pieds', a: [1, 2], r: ['......pP..', '...ppPpPp.', 'pppPpPpPpp'], p: { p: '#ff9a3a', P: '#ffd28a' } }
  };
  /* objets tenus : le bras se lève pour les porter */
  var TIENT = { bombe: 1, cle: 1, baton_lumineux: 1, lanterne: 1, parapluie: 1, style_trois_baguettes: 1 };
  Object.keys(SPR).forEach(function (k) { if (SPR[k].ou === 'main') TIENT[k] = 1; });
  var CHAPEAUX = { chapeau_paille: 1, bonnet: 1, casquette: 1, bandana: 1, casque_mabawa: 1, casquette_mabawa: 1, casquette_barge: 1, casquette_pilaou: 1, bob: 1 };
  var CRETES = { meches_vives: 1, crete_pics: 1, crete_recurer: 1 };

  /* agrandit une carte par deux (algorithme Scale2x) : contours arrondis, même taille de pixel */
  function double(rows) {
    var h = rows.length, w = 0, out = [], x, y;
    rows.forEach(function (r) { w = Math.max(w, r.length); });
    function g(x, y) { return y < 0 || y >= h || x < 0 ? '.' : (rows[y].charAt(x) || '.'); }
    for (y = 0; y < h; y++) {
      var l0 = '', l1 = '';
      for (x = 0; x < w; x++) {
        var P = g(x, y), A = g(x, y - 1), B = g(x + 1, y), C = g(x - 1, y), D = g(x, y + 1);
        l0 += (C === A && C !== D && A !== B ? A : P) + (A === B && A !== C && B !== D ? B : P);
        l1 += (D === C && D !== B && C !== A ? C : P) + (B === D && B !== A && D !== C ? D : P);
      }
      out.push(l0, l1);
    }
    return out;
  }
  Object.keys(SPR).forEach(function (k) {
    var s = SPR[k];
    if (!s.gros) return;
    if (s.r) s.r = double(s.r); if (s.f) s.f = s.f.map(double);
    s.a = [Math.min(s.a[0] * 2, 3), s.a[1] * 2 + 1];
    if (s.lueur) s.lueur = [s.lueur[0] * 2, s.lueur[1] * 2, s.lueur[2]];
  });
  function ancres(c, s) {
    var hy = HY + c.hdy, ey = EY + c.hdy;
    switch (s.ou) {
      case 'main': return [[c.mainX, c.mainY]];
      case 'tete': return [[CX, hy]];
      case 'visage': return [[CX, ey]];
      case 'cou': case 'dos': return [[CX, TY]];
      case 'epg': return [[c.tx0, TY]];
      case 'epd': return [[c.tx1 + 1, TY]];
      case 'pieds': return [[c.rx0, G, false], [c.lx0 + c.legW - 1, G, true]];
    }
    return [];
  }
  function sprite(c, id) {
    var s = SPR[id];
    if (!s) return false;
    var n = c.pose.n || 0, rows = s.f ? s.f[n % s.f.length] : s.r;
    if (s.clair) oterDessus(c, HY + c.hdy);
    ancres(c, s).forEach(function (A) {
      if (s.chaine) {
        var top = A[1] - s.a[1], x0 = A[0] - s.a[0], x1 = x0 + rows[0].length - 1;
        ligne(c, CX - 3, TY, x0 + 1, top - 1, s.chaine); ligne(c, CX + 2, TY, x1 - 1, top - 1, s.chaine);
      }
      poser(c, rows, s.p, A[0], A[1], s.a, A[2]);
      if (s.lueur) c.glow(A[2] ? A[0] + s.a[0] - s.lueur[0] : A[0] - s.a[0] + s.lueur[0], A[1] - s.a[1] + s.lueur[1], s.lueur[2], 3, (c.pose.n || 0) % 2 ? 0.45 : 0.3);
    });
    return true;
  }

  /* ── dans le dos (derrière le corps) ── */
  function cape(c, serviette) {
    var cfg = c.cfg, n = c.pose.n || 0, x, y;
    var col = serviette ? cfg.accent : mix(cfg.accent2, '#c8203a', 0.4), doublure = clair(col, 0.4);
    for (y = TY - 1; y < G; y++) {
      var k = y - TY + 1;
      var vague = k > 3 && mod(fdiv(y + n * 2, 3), 2) ? 1 : 0;
      var g = c.tx0 - 1 - Math.floor(k * (serviette ? 0.45 : 0.95)) - vague, d = c.tx1 + 1 + Math.floor(k * (serviette ? 0.45 : 0.4));
      for (x = g; x <= d; x++) {
        if (!serviette && y >= G - 2 && mod(x + n + (y === G - 1 ? 0 : 1), 3) === 0) continue;
        var co;
        if (serviette) {
          co = mod(fdiv(y, 3), 2) ? cfg.accent : BLANC;
          if (co === BLANC && mod(x * 3 + y, 5) === 0) co = '#f08a2a';
        } else co = x <= g + 1 ? doublure : col;
        c.px(x, y, co);
      }
      if (serviette && y === G - 1) for (x = g; x <= d; x += 2) c.px(x, G, BLANC);
    }
  }
  function ailesLibellule(c) {
    var n = c.pose.n || 0, f = n % 2;
    [[-1, c.tx0 - 1], [1, c.tx1 + 1]].forEach(function (s) {
      [[-14, -9 + f, 2.2], [-12, 3 - f, 1.8]].forEach(function (w, i) {
        var bx = s[1], by = TY - 2 + i * 3, tx = bx + s[0] * -w[0] * -1, ty = by + w[1];
        tx = bx + s[0] * Math.abs(w[0]);
        for (var y = Math.min(by, ty) - 3; y <= Math.max(by, ty) + 3; y++) for (var x = Math.min(bx, tx) - 3; x <= Math.max(bx, tx) + 3; x++) {
          var vx = tx - bx, vy = ty - by, l = vx * vx + vy * vy, t = Math.max(0, Math.min(1, ((x - bx) * vx + (y - by) * vy) / l));
          var dd = Math.hypot(x - bx - t * vx, y - by - t * vy), lg = w[2] * Math.sqrt(Math.sin(Math.PI * Math.min(0.98, t + 0.05)));
          if (dd <= lg) c.L.px(x, y, dd > lg - 0.9 ? '#7ad8e8' : (t > 0.85 ? c.cfg.accent : '#d4f6ff'), true, 0.8);
        }
      });
    });
  }
  function dansPoly(x, y, P) {
    var dedans = false;
    for (var i = 0, j = P.length - 1; i < P.length; j = i++) {
      if ((P[i][1] > y) !== (P[j][1] > y) && x < (P[j][0] - P[i][0]) * (y - P[i][1]) / (P[j][1] - P[i][1]) + P[i][0]) dedans = !dedans;
    }
    return dedans;
  }
  function ailesRoussette(c) {
    var n = c.pose.n || 0, f = n % 2 ? -2 : 0;
    [[-1, c.tx0], [1, c.tx1]].forEach(function (s) {
      var b = [s[1], TY], t1 = [s[1] + s[0] * 10, TY - 9 + f], t2 = [s[1] + s[0] * 14, TY - 3 + f], t3 = [s[1] + s[0] * 12, TY + 4 + f / 2];
      var P = [b, t1, t2, [s[1] + s[0] * 11, TY + 0 + f], t3, [s[1] + s[0] * 7, TY + 3], [s[1] + s[0] * 3, TY + 6]];
      for (var y = TY - 12; y < TY + 9; y++) for (var x = Math.min(b[0], t2[0]) - 1; x <= Math.max(b[0], t2[0]) + 1; x++) {
        if (dansPoly(x + 0.5, y + 0.5, P)) c.px(x, y, '#6a4232');
      }
      [t1, t2, t3].forEach(function (t) { ligne(c, b[0], b[1], t[0], t[1], '#a8784a'); });
      c.px(t1[0], t1[1] - 1, '#3a2a22');
    });
  }
  function guitare(c) {
    var x0 = c.tx1 - 1, y0 = TY + 4;
    c.L.ellipse(c.tx0 - 1.5, TY + 6.5, 3.6, 3, '#c8453d');
    c.px(c.tx0 - 3, TY + 5, '#f2c14e'); c.px(c.tx0 - 2, TY + 6, '#2a1a10');
    ligne(c, c.tx0 - 1, TY + 6, x0 + 7, HY + 2, function (k) { return k % 3 ? BOIS2 : '#c8a070'; }, 2);
    c.L.rect(x0 + 7, HY - 1, 3, 3, '#2a2a35'); c.px(x0 + 6, HY, MET2); c.px(x0 + 10, HY + 1, MET2); c.px(x0 + 8, HY - 2, MET2);
  }
  function sacRecup(c) {
    var x0 = c.tx0 - 3, x1 = c.tx1 + 3, y, x;
    for (y = TY - 4; y < TY + 8; y++) for (x = x0; x <= x1; x++) c.px(x, y, (x + y * 2) % 7 === 0 ? '#8a6a42' : '#6a7a4a');
    c.L.hline(x0, x1, TY - 5, '#4a5a32');
    c.L.rect(x0 - 3, TY - 8, 6, 3, '#2a4aa8'); c.L.hline(x0 - 3, x0 + 2, TY - 7, '#7a9ad8'); c.px(x0 - 1, TY - 8, '#7a9ad8'); c.px(x0 + 1, TY - 6, '#7a9ad8');
    c.L.rect(x1 + 1, TY + 3, 4, 3, '#8a92a8'); c.L.hline(x1 + 1, x1 + 4, TY + 3, MET2); c.px(x1 + 5, TY + 3, '#5a5f7a'); c.px(x1 + 6, TY + 3, '#5a5f7a');
    c.L.rect(x0 - 2, TY + 2, 2, 4, '#6ad8a0'); c.px(x0 - 2, TY + 1, '#8a5a3a');
    c.px(x1 + 1, TY - 2, c.cfg.accent); c.px(x1 + 2, TY - 1, c.cfg.accent); c.px(x1 + 2, TY, c.cfg.accent);
  }
  function doukabe(c) {
    var x0 = c.tx0 - 5, x1 = c.tx1 + 5, y, x;
    for (y = TY - 2; y < TY + 9; y++) for (x = x0; x <= x1; x++) c.px(x, y, '#a8784a');
    [TY + 1, TY + 5].forEach(function (yy) { c.L.hline(x0, x1, yy, BOIS2); });
    [[x0 + 1, TY, '#e8403a'], [x0 + 2, TY, '#f2c14e'], [x1 - 1, TY, '#3f6ad8'], [x1 - 2, TY - 1, '#6ad8a0'], [x1 - 2, TY, '#6ad8a0'], [x0 + 1, TY + 4, '#f08a2a'], [x0 + 2, TY + 3, BLANC], [x0 + 2, TY + 4, BLANC], [x1 - 1, TY + 4, '#c8453d'], [x1 - 2, TY + 4, '#f2c14e']].forEach(function (p) { c.px(p[0], p[1], p[2]); });
    for (x = x0 - 1; x <= x1 + 1; x++) { c.px(x, TY - 4, mod(fdiv(x, 2), 2) ? c.cfg.accent : BLANC); c.px(x, TY - 3, mod(fdiv(x, 2), 2) ? c.cfg.accent : BLANC); if (x % 2 === 0) c.px(x, TY - 2, mod(fdiv(x, 2), 2) ? c.cfg.accent : BLANC); }
  }
  /* la chaise à accoudoirs de la salle, devenue trône */
  function chaise(c) {
    var x, y, dos = '#2a2f44', bd = '#4a5070';
    for (y = HY - 4; y < TY + 6; y++) {
      var ins = y === HY - 4 ? 2 : (y === HY - 3 ? 1 : 0);
      for (x = CX - 9 + ins; x <= CX + 8 - ins; x++) c.px(x, y, x === CX - 9 + ins || x === CX + 8 - ins ? bd : dos);
    }
    poser(c, ['g.g.g', 'ggggg'], { g: OR2 }, CX, HY - 5, [2, 1]);
    [[c.tx0 - 6, -1], [c.tx1 + 3, 1]].forEach(function (a) {
      c.L.rect(a[0], TY + 4, 4, 2, '#3a3f58'); c.L.hline(a[0], a[0] + 3, TY + 4, '#5a5f7a');
      c.L.rect(a[0] + (a[1] < 0 ? 2 : 1), TY + 6, 1, LEGTOP - TY - 5, MET);
    });
    c.L.rect(c.tx0 - 3, LEGTOP + 1, c.tw + 6, 2, '#3a3f58');
    c.L.rect(CX - 1, LEGTOP + 3, 2, G - LEGTOP - 3, MET);
    c.L.hline(CX - 7, CX + 6, G, '#5a5f7a');
    [CX - 7, CX - 1, CX + 5].forEach(function (wx) { c.L.rect(wx, G + 1, 2, 2, '#2a2a35'); });
  }
  function objetsDerriere(c) {
    var o = c.cfg.o, cfg = c.cfg, n = c.pose.n || 0, x, y, k, r;
    if (o.autour === 'pixels') {
      r = hasard(7);
      for (k = 0; k < 10; k++) {
        var px_ = 4 + Math.floor(r() * 40), py = 12 + mod(Math.floor(r() * 44) + n * 3, 46);
        for (var t = 0; t < 3; t++) c.fx(px_, py - t * 2, t ? '#2fbf5a' : NG, 1 - t * 0.3);
      }
    }
    var d = o.dos;
    if (d === 'ailes_fee') {
      var f = n % 2 ? 1 : 0, wc = '#d4f4ff';
      [[c.tx0 - 5, -1], [c.tx1 + 6, 1]].forEach(function (w) {
        c.L.ellipseA(w[0] + w[1], TY - 7 + f * 0.5, 4.6, 6.4 - f, wc, 0.8);
        c.L.ellipseA(w[0], TY + 2, 3.2, 3.2 - f * 0.5, wc, 0.8);
        for (k = 0; k < 5; k++) c.px(w[0] + w[1] * (k - 2) * 0.5, TY - 2 - k * 2, '#a8e0ff');
        c.px(w[0] + w[1] * 1.5, TY - 11 + f, cfg.accent); c.glow(rnd(w[0] + w[1] * 1.5), TY - 11 + f, cfg.accent, 2, 0.4);
        c.px(w[0] - w[1], TY + 3, cfg.accent2);
      });
    }
    if (d === 'ailes_libellule') ailesLibellule(c);
    if (d === 'ailes_roussette') ailesRoussette(c);
    if (d === 'cape') cape(c, false);
    if (d === 'cape_serviette') cape(c, true);
    if (d === 'guitare') guitare(c);
    if (d === 'sac_recup') sacRecup(c);
    if (d === 'doukabe_dos') doukabe(c);
    if (d === 'chaise_accoudoirs') chaise(c);
    if (d === 'jetpack') {
      [c.tx0 - 4, c.tx1 + 2].forEach(function (x0) {
        c.L.rect(x0, TY - 3, 3, 9, '#c8963b');
        c.L.rect(x0, TY - 3, 1, 9, '#e8b84a');
        c.L.rect(x0, TY - 4, 3, 1, MET); c.L.rect(x0, TY + 6, 3, 1, '#5a5f7a');
        for (var j = 0; j < 4; j++) c.fx(x0 + 1 + (j % 2 ? (n % 2 ? 1 : -1) : 0), TY + 8 + j * 2 + (n % 2), j < 1 ? '#ffb648' : '#f4f6ff', 0.75 - j * 0.15);
      });
    }
    if (d === 'drapeau') {
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

  /* ── aux pieds (après les jambes) ── */
  function objetsPieds(c) {
    var p = c.cfg.o.pieds, n = c.pose.n || 0, x, k;
    if (p === 'aucun' || c.assis) return;
    if (SANS_CORPS[c.lig] && p !== 'skate' && p !== 'nuage_taxi') return;
    if (sprite(c, p)) return;
    var g = c.lx0 - 4, d = c.rx0 + c.legW + 3;
    if (p === 'skate') {
      for (x = g; x <= d; x++) c.px(x, G + 1, x === g || x === d ? fonce(c.cfg.accent, 0.3) : c.cfg.accent);
      c.px(g - 1, G, c.cfg.accent); c.px(d + 1, G, c.cfg.accent);
      [g + 2, d - 3].forEach(function (wx) { c.L.rect(wx, G + 2, 2, 2, '#e8e0d0'); c.px(wx + (n % 2), G + 2 + (n % 2), '#9aa3b8'); });
      for (k = 0; k < 3; k++) c.fx(g - 3 - k * 2, G - k, '#c8d0e0', 0.7 - k * 0.2);
    }
    if (p === 'nuage_taxi') {
      var nf = function (x, y) { return y > G + 1 ? '#c8d4e8' : '#f4f8ff'; };
      c.L.ellipse(CX - 4.5, G + 0.5, 4.5, 2.6, null, true, nf); c.L.ellipse(CX + 0.5, G - 0.5, 5, 3, null, true, nf); c.L.ellipse(CX + 5, G + 0.5, 4.2, 2.6, null, true, nf);
      [CX - 6, CX + 5].forEach(function (wx) { c.L.rect(wx, G + 3, 2, 1, '#2a2a35'); c.px(wx + (n % 2), G + 3, '#9aa3b8'); });
      for (k = 0; k < 3; k++) c.fx(CX - 11 - k * 2, G - 1 + (k % 2), '#f4f8ff', 0.8 - k * 0.2);
    }
    if (p === 'ballon_foot') {
      var bx = c.lx0 - 4.5, by = G - 2.5 - (n % 2);
      c.L.ellipse(bx, by, 3.3, 3.3, BLANC);
      c.L.carte(Math.round(bx) - 2, Math.round(by) - 2, ['k..k', '.kk.', '.kk.', 'k..k'], { k: '#2a2a35' });
    }
  }

  /* ── au cou et à la taille ── */
  function objetsCou(c) {
    var o = c.cfg.o, n = c.pose.n || 0;
    if (o.dos === 'cape' || o.dos === 'cape_serviette') { var cc = o.dos === 'cape' ? mix(c.cfg.accent2, '#c8203a', 0.4) : c.cfg.accent; c.px(CX - 2, TY, cc); c.px(CX + 1, TY, cc); c.px(CX - 1, TY + 1, OR2); c.px(CX, TY + 1, OR2); }
    var v = o.cou;
    if (v === 'aucun' || sprite(c, v)) return;
    if (v === 'sacoche') {
      ligne(c, c.tx1 - 1, TY - 1, c.tx0 + 1, TY + 6, '#2a2f44');
      var sx = c.tx0 - 3, sy = TY + 5;
      c.L.rect(sx, sy, 6, 4, '#2a2f44'); c.L.hline(sx, sx + 5, sy, '#3a3f58'); c.L.hline(sx + 1, sx + 4, sy + 1, c.cfg.accent);
      c.px(sx + 4, sy + 2, MET2);
    }
    if (v === 'sac_devant') {
      var sc = mix(c.cfg.accent2, '#2a2f4a', 0.45), sp = clair(sc, 0.25);
      c.L.rect(c.tx0 + 1, TY + 1, c.tw - 2, 8, sc);
      c.L.rect(c.tx0 + 2, TY + 5, c.tw - 4, 4, sp); c.L.hline(c.tx0 + 2, c.tx1 - 2, TY + 5, c.cfg.accent);
      c.L.hline(c.tx0 + 2, c.tx1 - 2, TY + 1, fonce(sc, 0.3));
      [c.tx0 + 1, c.tx1 - 1].forEach(function (x) { c.px(x, TY - 1, fonce(sc, 0.2)); c.px(x, TY, fonce(sc, 0.2)); });
      c.px(c.tx1 - 3, TY + 6, MET2);
    }
    if (v === 'collier_coquillages') collier(c, '#f4e2c8', '#f2a8b8', { a: [1, 0], r: ['.c.', 'cdc', 'cdc', '.c.'], p: { c: '#f4e2c8', d: '#c8a078' } });
    if (v === 'ceinture_boucle') {
      c.L.hline(c.tx0, c.tx1, TY + 6, '#2a2f44'); c.L.hline(c.tx0, c.tx1, TY + 7, '#3a3f58');
      c.L.rect(CX - 2, TY + 5, 4, 4, OR2); c.L.rect(CX - 1, TY + 6, 2, 2, c.cfg.accent); c.px(CX - 2, TY + 5, '#fff6c8');
      c.L.rect(c.tx0 + 1, TY + 5, 2, 3, '#8a6a42');
    }
    if (v === 'baladeur_galaxie') {
      ligne(c, c.tx0 + 1, TY, c.tx1 - 2, TY + 5, '#3a3f58');
      poser(c, ['kkkkkk', 'kwowok', 'kwwwwk', 'kAkAkk'], { k: '#3a3f58', w: '#c8ccd8', o: '#2a2a35', A: 'A' }, c.tx1 - 3, TY + 4, [0, 0]);
      c.L.rect(CX - 5, TY - 1, 2, 2, c.cfg.accent2); c.L.rect(CX + 3, TY - 1, 2, 2, c.cfg.accent2); c.L.hline(CX - 3, CX + 2, TY, '#3a3f58');
      if (n % 2) c.fx(CX + 6, TY - 3, c.cfg.accent, 0.9);
    }
  }

  /* ── sur les épaules (avant la tête) ── */
  function veste(c, pinces) {
    var tx0 = c.tx0, tx1 = c.tx1, y, col = pinces ? '#4a6fa5' : '#2b2f45', pq = fonce(col, 0.3);
    for (y = TY; y < TY + 8; y++) { for (var x = tx0; x <= CX - 3; x++) c.px(x, y, col); for (x = CX + 2; x <= tx1; x++) c.px(x, y, col); c.px(CX - 3, y, pq); c.px(CX + 2, y, pq); }
    [c.BL, c.BR].forEach(function (b) { for (var i = 0; i < 4; i++) c.px(b[i][0], b[i][1], i % 2 ? pq : col); });
    c.px(tx0 - 1, TY - 1, col); c.px(tx1 + 1, TY - 1, col); c.px(CX - 3, TY - 1, col); c.px(CX + 2, TY - 1, col);
    if (pinces) {
      [[tx0 + 1, TY + 1, NR], [tx0 + 3, TY + 4, NJ], [tx1 - 1, TY + 2, NC], [tx1 - 3, TY + 5, NG], [c.BL[1][0], c.BL[1][1] - 1, NO], [c.BR[1][0], c.BR[1][1] - 1, NV]].forEach(function (p) {
        c.L.rect(p[0], p[1], 1, 3, p[2]); c.px(p[0], p[1] + 1, MET2);
      });
    } else {
      c.L.rect(tx0 + 1, TY + 3, 2, 2, NR); c.L.carte(tx1 - 3, TY + 5, ['jk', 'kj'], { j: NJ, k: '#2a2a35' });
      [[tx0, TY], [tx0 + 2, TY], [tx1, TY], [tx1 - 2, TY], [c.BL[0][0], c.BL[0][1]], [c.BR[1][0], c.BR[1][1]]].forEach(function (p) { c.px(p[0], p[1], MET2); });
    }
  }
  function objetsEpaule(c) {
    var o = c.cfg.o, cfg = c.cfg, n = c.pose.n || 0, y, v = o.epaule;
    if (v === 'veste_ecussons') veste(c, false);
    if (v === 'pinces_linge') veste(c, true);
    if (v === 'echarpe') {
      var e = mix(cfg.accent2, '#c8453d', 0.45);
      c.L.hline(c.tx0 - 1, c.tx1 + 1, TY - 1, e); c.L.hline(c.tx0 - 1, c.tx1 + 1, TY, fonce(e, 0.2));
      for (y = TY + 1; y < TY + 7; y++) { c.px(c.tx1 - 3, y, y % 2 ? e : cfg.accent); c.px(c.tx1 - 2, y, y % 2 ? fonce(e, 0.2) : cfg.accent); }
    }
    if (v === 'drone') {
      var dx = c.tx0 - 9, dy = TY - 12 + (n % 2);
      c.L.rect(dx, dy, 5, 2, '#3a3f58'); c.px(dx + 2, dy, cfg.accent);
      c.px(dx - 1, dy - 1, '#5a5f7a'); c.px(dx + 5, dy - 1, '#5a5f7a');
      c.L.hline(dx - 2 - (n % 2), dx, dy - 2, '#e8f0ff'); c.L.hline(dx + 4, dx + 6 + (n % 2), dy - 2, '#e8f0ff');
      c.px(dx + 1, dy + 2, '#5a5f7a'); c.px(dx + 3, dy + 2, '#5a5f7a');
      c.glow(dx + 2, dy, cfg.accent, 2, 0.3);
    }
    sprite(c, v);
  }

  /* lunettes de ski : grand écran irisé, cadre sombre (sur les yeux, ou relevées sur le front) */
  function skiMasque(c, y0, yeux) {
    var cfg = c.cfg, n = c.pose.n || 0, x, y, a = X0 + (yeux ? 0 : 1), b = X1 - (yeux ? 0 : 1);
    if (yeux) { c.L.hline(X0 - 2, X0 - 1, y0 + 2, cfg.accent2); c.L.hline(X1 + 1, X1 + 2, y0 + 2, cfg.accent2); }
    for (y = y0; y < y0 + 5; y++) for (x = a; x <= b; x++) {
      var bord = y === y0 || y === y0 + 4 || x === a || x === b, nez = yeux && y === y0 + 4 && x >= CX - 2 && x <= CX + 1;
      if (nez) continue;
      c.px(x, y, bord ? '#2a2f44' : mix(cfg.accent, cfg.accent2, (x - a) / (b - a)));
    }
    c.px(a + 2 + (n % 2), y0 + 1, '#ffffff'); c.px(a + 3 + (n % 2), y0 + 1, '#ffffff'); c.px(a + 2 + (n % 2), y0 + 2, '#ffffff');
  }
  /* ── sur la tête (après les cheveux) ── */
  function objetsTete(c) {
    var o = c.cfg.o, cfg = c.cfg, hy = HY + c.hdy, n = c.pose.n || 0, x, y, k, v = o.tete;
    if (CHAPEAUX[v] || CRETES[v]) oterDessus(c, hy);
    if (v === 'chapeau_paille') {
      var P1 = '#d8b468', P2 = '#b8904a', P3 = '#8a6a32';
      [[X0 + 2, X1 - 2, hy - 4], [X0 + 1, X1 - 1, hy - 3], [X0 + 1, X1 - 1, hy - 2], [X0, X1, hy - 1], [X0, X1, hy]].forEach(function (r) {
        for (x = r[0]; x <= r[1]; x++) c.px(x, r[2], mod(x + r[2] * 2, 3) === 0 ? P2 : P1);
      });
      c.px(CX - 1, hy - 4, P3); c.px(CX, hy - 4, P3); c.px(CX - 1, hy - 3, P2);
      for (x = X0 - 4; x <= X1 + 4; x++) {
        var bossé = (x < X0 - 1 ? 1 : 0) - (x > X1 + 1 ? 1 : 0);
        c.px(x, hy + 1 + bossé, mod(x, 2) ? P1 : P2);
        if (x > X0 - 3 && x < X1 + 3) c.px(x, hy + 2, mod(x, 3) ? P2 : P3);
      }
      c.px(X0 - 4, hy + 1, P3); c.px(X1 + 4, hy + 1, P3);
    }
    if (v === 'bonnet' || v === 'casque_mabawa') {
      var tri = mix(cfg.accent2, '#2a2f4a', 0.4), Wb = [5, 7, 8, 9, 9, 9, 9];
      for (k = 0; k < 7; k++) { y = hy - 3 + k; for (x = CX - Wb[k]; x < CX + Wb[k]; x++) c.px(x, y, k >= 5 ? (x % 2 ? fonce(tri, 0.25) : tri) : tri); }
      if (v === 'bonnet') { c.L.ellipse(CX - 0.5, hy - 5, 2.4, 2.4, '#f2f0ea'); c.px(CX - 1, hy - 6, '#ffffff'); }
      else {
        var aile = ['bb...', 'bBb..', '.bbBb', '..bBb', '...bb'], pal = { b: '#c8752e', B: '#7a3a1a' };
        poser(c, aile, pal, X0 + 1, hy - 1, [4, 4 + (n % 2)], false); poser(c, aile, pal, X1 - 1, hy - 1, [4, 4 + (n % 2)], true);
      }
    }
    if (v === 'casquette') {
      var cq = cfg.haut;
      [[X0 + 3, X1 - 3], [X0 + 1, X1 - 1], [X0, X1], [X0, X1], [X0, X1]].forEach(function (r, k) { c.L.hline(r[0], r[1], hy - 2 + k, k === 0 ? clair(cq, 0.2) : cq); });
      c.L.hline(X0 - 1, X1 + 1, hy + 3, fonce(cq, 0.35));
      c.L.hline(X0 - 2, X1 + 2, hy + 4, fonce(cq, 0.5));
      c.L.carte(CX - 2, hy - 1, ['x.x', '.x.', 'x.x'], { x: cfg.accent });
    }
    if (v === 'casquette_mabawa' || v === 'casquette_barge' || v === 'casquette_pilaou') {
      /* casquette noire à visière plate, slogan en lettres blanches (lisible en grand dans l'éditeur), pastille dorée laissée sur la visière */
      var cn = '#1f1a24', cl = '#3a3448';
      [[X0 + 3, X1 - 3], [X0 + 1, X1 - 1], [X0, X1], [X0, X1], [X0, X1]].forEach(function (r, k) { c.L.hline(r[0], r[1], hy - 2 + k, k === 0 ? cl : cn); });
      var LET = { casquette_mabawa: 'x.xx.x.x.xx.x', casquette_barge: 'xx.x.xx..x.xx', casquette_pilaou: 'x.xx.x..xx.xx' }[v];
      for (k = 0; k < LET.length; k++) if (LET.charAt(k) === 'x') { c.px(CX - 6 + k, hy, '#ffffff'); if (k % 3 !== 1) c.px(CX - 6 + k, hy + 1, '#ffffff'); }
      c.L.hline(X0 - 3, X1 + 3, hy + 3, cn); c.L.hline(X0 - 3, X1 + 3, hy + 4, cl);
      c.L.rect(X1 - 2, hy + 3, 2, 1, n % 2 ? '#fff0a0' : OR2);
    }
    if (v === 'bob') {
      var bb = mix(cfg.accent2, '#2a2f4a', 0.35), bc = clair(bb, 0.3);
      [[X0 + 3, X1 - 3], [X0 + 1, X1 - 1], [X0 + 1, X1 - 1], [X0, X1], [X0, X1]].forEach(function (r, k) { c.L.hline(r[0], r[1], hy - 3 + k, k === 0 ? bc : bb); });
      c.L.hline(X0, X1, hy, fonce(bb, 0.3));
      c.L.hline(X0 - 2, X1 + 2, hy + 2, bb); c.L.hline(X0 - 3, X1 + 3, hy + 3, fonce(bb, 0.2));
      for (x = X0 - 2; x <= X1 + 2; x += 2) c.px(x, hy + 2, bc);
    }
    if (v === 'ski_front') {
      c.L.hline(X0 - 1, X1 + 1, hy + 2, cfg.accent2); c.L.hline(X0 - 1, X1 + 1, hy + 3, fonce(cfg.accent2, 0.3));
      skiMasque(c, hy, false);
    }
    if (v === 'peigne') {
      /* peigne à longues dents planté dans les cheveux : on cherche le haut de la coiffure */
      var px0 = X1 - 5, haut = hy + 2;
      for (y = 0; y < hy + 3; y++) if (c.L.plein(px0, y) || c.L.plein(px0 + 2, y)) { haut = y; break; }
      var pc = cfg.accent, pf = fonce(pc, 0.35);
      c.L.rect(px0 - 1, haut - 4, 5, 2, pc); c.L.hline(px0 - 1, px0 + 3, haut - 4, clair(pc, 0.4));
      c.px(px0 + 1, haut - 6, pc); c.px(px0 + 1, haut - 5, pc); c.px(px0, haut - 7, pc); c.px(px0 + 1, haut - 7, pc); c.px(px0 + 2, haut - 7, pc);
      [px0 - 1, px0 + 1, px0 + 3].forEach(function (tx) { c.px(tx, haut - 2, pf); c.px(tx, haut - 1, pf); });
    }
    if (v === 'perles') {
      var PC = [cfg.accent, '#ffffff', '#f2c14e', cfg.accent2];
      [X0 - 2, X0 - 1, X1 + 1, X1 + 2].forEach(function (tx, j) {
        var y0 = hy + 9 + (j % 2) * 2;
        for (y = y0; y < y0 + 6; y++) c.px(tx, y, (y - y0) % 2 ? PC[(j + y) % 4] : c.hc);
      });
    }
    if (v === 'bandana') {
      var bd = '#d8403a';
      for (y = hy - 1; y <= hy + 4; y++) { var r = crane(hy, y); for (x = r[0]; x <= r[1]; x++) c.px(x, y, (x + y * 2) % 4 === 0 ? BLANC : (y === hy + 4 ? fonce(bd, 0.2) : bd)); }
      c.L.rect(X1 + 1, hy + 3, 2, 2, bd);
      for (k = 0; k < 4; k++) { c.px(X1 + 2 + (k + n) % 2, hy + 5 + k, bd); c.px(X1 + 3, hy + 5 + k - (n % 2), fonce(bd, 0.2)); }
    }
    if (v === 'bandeau_noue') {
      var bn = cfg.accent2;
      c.L.hline(X0, X1, hy + 3, bn); c.L.hline(X0, X1, hy + 4, fonce(bn, 0.2));
      c.L.rect(X0 - 2, hy + 3, 2, 2, bn);
      var VG = [0, 0, 1, 1, 2, 2, 1, 1];
      for (k = 1; k < 11; k++) { y = hy + 3 + VG[mod(k + n * 2, 8)] + fdiv(k, 3); c.px(X0 - 2 - k, y, bn); c.px(X0 - 2 - k, y + 1, fonce(bn, 0.2)); }
      for (k = 1; k < 8; k++) { y = hy + 6 + VG[mod(k + 3 + n * 2, 8)] + fdiv(k, 2); c.px(X0 - 2 - k, y, bn); }
    }
    if (v === 'meches_vives') {
      var a = cfg.accent, b = cfg.accent2;
      for (y = hy - 1; y <= hy + 3; y++) { var rr = crane(hy, y); for (x = rr[0]; x <= rr[1]; x++) c.px(x, y, a); }
      [[X0 - 3, hy + 2, X0, X0 + 3], [CX - 7, hy - 7, X0 + 1, CX - 2], [CX - 1, hy - 11, CX - 4, CX + 2], [CX + 5, hy - 8, CX, X1 - 1], [X1 + 3, hy - 1, X1 - 3, X1]].forEach(function (s, i) {
        pointe(c, s[0], s[1], hy + 1, s[2], s[3], i % 2 ? b : a, clair(i % 2 ? b : a, 0.55));
      });
      for (x = X0; x <= X1; x++) if (x % 3) c.px(x, hy + 4, a);
      c.fx(CX - 1, hy - 12 - (n % 2), '#ffffff', 0.9); c.glow(CX - 1, hy - 11, a, 3, 0.3);
    }
    if (v === 'crete_pics') {
      raser(c, hy);
      [[CX - 6, hy - 5], [CX - 3, hy - 10], [CX, hy - 13], [CX + 3, hy - 10], [CX + 5, hy - 5]].forEach(function (p, i) {
        var col = i % 2 ? cfg.accent2 : cfg.accent; pointe(c, p[0], p[1], hy + 1, CX - 2, CX + 1, col, clair(col, 0.55));
      });
    }
    if (v === 'crete_recurer') {
      raser(c, hy);
      for (x = CX - 4; x <= CX + 3; x++) { var hh = 6 + mod(x * 5, 3); for (y = hy - 2 - hh; y < hy - 2; y++) c.px(x, y, x % 2 ? '#f2d14b' : '#7fd06a'); }
      c.L.rect(CX - 5, hy - 2, 10, 2, '#c8a070'); c.L.hline(CX - 5, CX + 4, hy - 1, '#a8784a');
      ligne(c, CX + 5, hy - 2, CX + 10, hy - 5, '#c8a070', 2);
      c.fx(CX + 7, hy - 10 - (n % 2), '#bfe8ff', 0.9); c.fx(CX + 9, hy - 13 + (n % 2), '#bfe8ff', 0.8);
    }
    if (v === 'couronne_fleurs') {
      c.L.hline(X0, X1, hy + 1, '#3a8a48'); c.L.hline(X0 + 1, X1 - 1, hy, '#4fae5a');
      var FL = [['#f2d14b', '#c88a1f'], ['#fff4d8', '#f2b84b'], ['#ff9ac8', '#f2d14b']];
      [X0 - 1, X0 + 4, CX - 1, X1 - 5, X1 - 1].forEach(function (fx_, i) { var p = FL[i % 3]; c.L.carte(fx_, hy - 1, ['.p.', 'pcp', '.p.'], { p: p[0], c: p[1] }); });
    }
    if (v === 'couronne_feuilles') {
      c.L.hline(X0, X1, hy + 2, '#2f7a3a');
      for (x = X0 - 1, k = 0; x <= X1; x += 3, k++) {
        var fc = ['#4fae5a', '#7fd06a', '#3a8a48'][k % 3];
        c.L.carte(x, hy - 3 + (k % 2), ['..f', '.ff', 'ff.', 'f..'], { f: fc });
      }
      c.px(CX + 3, hy - 1, '#e8403a'); c.px(CX - 5, hy, '#e8403a');
    }
    if (v === 'antennes') {
      c.L.hline(X0 + 2, X1 - 2, hy - 1, '#3a3f58');
      [[-1, CX - 5, cfg.accent], [1, CX + 4, cfg.accent2]].forEach(function (a) {
        var bx = a[1], b = (n + (a[0] > 0 ? 1 : 0)) % 2;
        for (var k = 0; k < 6; k++) c.px(bx + a[0] * fdiv(k, 2), hy - 2 - k, k % 2 ? MET : '#5a5f7a');
        var tx = bx + a[0] * 3, ty = hy - 10 + b;
        c.L.rect(tx - (a[0] < 0 ? 1 : 0), ty, 2, 2, a[2]); c.glow(tx, ty, a[2], 2, 0.4);
      });
    }
    if (v === 'cornes_zebu') sprite(c, v);
    else sprite(c, v);
  }

  /* ── sur le visage ── */
  function objetsVisage(c) {
    var o = c.cfg.o, cfg = c.cfg, ey = EY + c.hdy, hy = HY + c.hdy, n = c.pose.n || 0, x, y, v = o.visage;
    if (v === 'visiere') {
      c.L.hline(X0 - 1, CX, ey - 2, '#3a3f58');
      for (y = ey - 1; y < ey + 3; y++) for (x = CX + 1; x <= X1 + 1; x++) c.px(x, y, cfg.accent, 0.45);
      c.L.hline(CX + 1, X1 + 1, ey - 2, cfg.accent); c.L.hline(CX + 1, X1 + 1, ey + 3, fonce(cfg.accent, 0.45));
      c.L.hline(CX + 2, CX + 4 + (n % 3), ey + 1, '#ffffff');
      c.glow(X1, ey, cfg.accent, 3, 0.25);
    }
    if (v === 'loup') {
      var mc = mix(cfg.accent2, '#2a1f4a', 0.3), bord = fonce(mc, 0.4);
      for (y = ey - 1; y <= ey + 2; y++) for (x = X0 + 1; x <= X1 - 1; x++) {
        var trou = ((x >= CX - 6 && x <= CX - 3) || (x >= CX + 2 && x <= CX + 5)) && y >= ey && y <= ey + 1;
        if (trou) continue;
        if (y === ey + 2 && x >= CX - 2 && x <= CX + 1) continue;
        c.px(x, y, y === ey - 1 || y === ey + 2 ? bord : mc);
      }
      [CX - 6, CX - 5, CX - 4, CX + 3, CX + 4, CX + 5].forEach(function (xx) { c.px(xx, ey - 2, mc); });
      c.px(X0, ey, mc); c.px(X0 - 1, ey + (n % 2), mc); c.px(X0 - 2, ey + 1, mc); c.px(X1, ey, mc); c.px(X1 + 1, ey + 1 - (n % 2), mc);
    }
    if (v === 'monocle_pixels') {
      /* un monocle carré à verre en damier de pixels, pendu à une chaînette : rien d'un viseur */
      var mx = CX + 1, my = ey - 2;
      c.L.hline(mx, mx + 5, my, OR2); c.L.hline(mx, mx + 5, my + 5, OR); for (y = my + 1; y < my + 5; y++) { c.px(mx, y, OR2); c.px(mx + 5, y, OR); }
      for (y = my + 1; y < my + 5; y++) for (x = mx + 1; x < mx + 5; x++) c.fx(x, y, mod(fdiv(x - mx - 1 + (n % 2), 2) + fdiv(y - my - 1, 2), 2) ? NC : NR, 0.45);
      for (y = my + 6; y < TY; y++) c.px(mx + 5 + (y % 2), y, y % 2 ? OR : OR2);
    }
    if (v === 'cache_oeil') { ligne(c, CX - 7, ey - 1, X0 - 1, ey - 1, '#1f1a24'); ligne(c, CX - 2, ey - 1, X1, hy + 4, '#1f1a24'); }
    if (v === 'ski_yeux') skiMasque(c, ey - 2, true);
    if (v === 'ecouteurs') {
      [[X0 - 2, 1], [X1 + 1, -1]].forEach(function (p) {
        c.L.rect(p[0], ey + 1, 2, 2, BLANC); c.px(p[0] + (p[1] > 0 ? 1 : 0), ey + 3, BLANC); c.px(p[0] + (p[1] > 0 ? 1 : 0), ey + 4, '#d8dce8');
      });
      if (n % 2) c.fx(X1 + 4, ey - 1, cfg.accent, 0.8); else c.fx(X0 - 4, ey, cfg.accent, 0.8);
    }
    if (v === 'epingles') {
      [[X0 - 1, ey + 2], [X1 + 1, ey + 2]].forEach(function (p) { c.px(p[0], p[1], MET2); c.px(p[0], p[1] + 1, MET2); c.px(p[0], p[1] + 2, '#5a5f7a'); });
      [[CX - 4, TY], [CX + 3, TY]].forEach(function (p) { c.L.rect(p[0], p[1], 1, 3, MET2); c.px(p[0], p[1], '#5a5f7a'); });
    }
    if (v === 'implant') {
      c.L.rect(X0 + 1, ey - 6, 4, 3, '#5a5f7a'); c.L.rect(X0 + 2, ey - 5, 2, 1, n % 2 ? cfg.accent2 : cfg.accent);
      c.glow(X0 + 2, ey - 5, n % 2 ? cfg.accent2 : cfg.accent, 3, 0.45);
      c.px(X0, ey - 3, MET); c.px(X0, ey - 2, MET); c.px(X0 - 1, ey - 1, MET); c.px(X0 - 1, ey, cfg.accent);
    }
    if (v === 'peinture') {
      [[X0 + 1, X0 + 3], [X1 - 3, X1 - 1]].forEach(function (r) { c.L.hline(r[0], r[1], ey + 3, cfg.accent); c.L.hline(r[0], r[1], ey + 5, cfg.accent2); });
      c.px(CX - 1, ey - 4, cfg.accent); c.px(CX, ey - 4, cfg.accent);
    }
    if (v === 'pansement') { c.L.rect(X1 - 4, ey + 3, 4, 2, '#f0c89a'); c.px(X1 - 3, ey + 3, '#d8a878'); c.px(X1 - 2, ey + 4, '#d8a878'); }
    sprite(c, v);
  }

  /* ── dans la main ── */
  function parapluie(c, hx, hy) {
    var n = c.pose.n || 0, cx = Math.min(W - 11, Math.max(11, hx)), by = Math.min(HY - 8, hy - 12), x, y, k;
    ligne(c, hx, hy - 1, cx, by + 1, '#3a3f58');
    c.px(hx - 1, hy, '#3a3f58'); c.px(hx - 1, hy - 1, '#3a3f58');
    var demi = [2, 5, 7, 9, 10, 10];
    for (k = 0; k < 6; k++) {
      y = by - 5 + k;
      for (x = cx - demi[k]; x <= cx + demi[k]; x++) {
        if (k === 5 && mod(x - cx, 4) === 2) continue;
        c.px(x, y, mod(fdiv(x - cx + 20, 4), 2) ? c.cfg.accent : BLANC);
      }
    }
    c.px(cx, by - 6, '#3a3f58');
    [[cx - 12, 0], [cx + 12, 2], [cx - 9, 4], [cx + 9, 1]].forEach(function (g) {
      var yy = by + 2 + mod(n * 3 + g[1] * 2, 8);
      c.fx(g[0], yy, '#4aa8e8', 0.9); c.fx(g[0], yy + 1, '#7ad8ff', 0.8);
    });
  }
  function tenu(c) {
    var cfg = c.cfg, acc = cfg.acc, h = c.BR[c.BR.length - 1], hx = h[0], hy = h[1], pose = c.brasPose, k, x, y;
    c.mainX = hx; c.mainY = hy;
    var n = c.pose.n || 0;
    if (acc === 'gants_geants') {
      var gant = ['.AAAAA.', 'AAAAAAA', 'wwwwwww', 'wwwwwwW', 'wwwwwwW', 'wwwwwwW', '.wwwwW.'], gp = { A: 'A', w: BLANC, W: '#c8ccd8' };
      var hl = c.BL[c.BL.length - 1];
      poser(c, gant, gp, hx, hy, [4, 2], false); poser(c, gant, gp, hl[0] - 1, hl[1], [4, 2], true);
    }
    if (acc === 'bras_meca') {
      var ferme = n % 2;
      (ferme ? [[-1, 1], [0, 1], [-1, 2], [0, 2]] : [[-2, 1], [-2, 2], [1, 1], [1, 2], [-1, 1], [0, 1]]).forEach(function (p) { c.px(hx + p[0], hy + p[1], MET2); });
      c.px(c.tx1 + 1, TY, '#5a5f7a');
    }
    if (acc === 'bracelet') {
      [c.BR, c.BL].forEach(function (b, j) {
        var cols = [c.cfg.accent, '#f2c14e', '#e8403a', c.cfg.accent2];
        [2, 3].forEach(function (r) { var p = b[b.length - r]; for (var i = -1; i <= 1; i++) if (c.L.plein(p[0] + i, p[1])) c.px(p[0] + i, p[1], cols[(j + r + i + 3) % 4]); });
      });
    }
    if (c.pose.tablette && acc !== 'gants_geants' && acc !== 'bras_meca' && acc !== 'parapluie') { tablette(c); return; }
    if (acc === 'parapluie') parapluie(c, hx, hy);
    if (acc === 'style_trois_baguettes') {
      [[-2, -10], [2, -11], [6, -9]].forEach(function (b) { ligne(c, hx, hy, hx + b[0], hy + b[1], function (k) { return k % 3 === 1 ? '#f2d090' : '#d89a48'; }, 2); });
    }
    if (acc === 'enceinte') {
      var x0 = c.tx0 - 13, y0 = G - 6;
      c.L.rect(x0, y0, 10, 7, '#3a3f58');
      c.L.hline(x0 + 2, x0 + 7, y0 - 1, MET); c.px(x0 + 2, y0 - 2, MET); c.px(x0 + 7, y0 - 2, MET); c.L.hline(x0 + 2, x0 + 7, y0 - 3, MET);
      [x0 + 2.5, x0 + 7.5].forEach(function (cxx) { c.L.ellipse(cxx, y0 + 3.5, 2, 2, '#1b1f33'); c.px(cxx - 0.5, y0 + 3, cfg.accent2); });
      var base = [2, 4, 3, 5, 2], dec = c.pose.egaliseur || 0;
      var cols = [NC, NV, NR, NJ, NC];
      base.map(function (v, i) { return 1 + mod(v + dec * (i + 2), 5); }).forEach(function (hh, i) { for (var k = 0; k < hh; k++) c.fx(x0 + 1 + i * 2, y0 - 5 - k, cols[i], 0.9 - k * 0.12); });
    }
    var levee = pose === 'tenir' || pose === 'haut' || pose === 'salut' || pose === 'salut2' || pose === 'ouvert';
    if (sprite(c, acc)) return;
    if (!levee) return;
    if (acc === 'baton_lumineux') { c.L.rect(hx, hy - 7, 2, 7, cfg.accent); c.L.rect(hx, hy - 6, 1, 5, clair(cfg.accent, 0.6)); c.glow(hx, hy - 4, cfg.accent, 3, n % 2 ? 0.5 : 0.3); }
    if (acc === 'lanterne') {
      c.px(hx + 1, hy + 1, MET);
      c.L.rect(hx, hy + 2, 3, 1, '#3a3f58'); c.L.rect(hx, hy + 3, 3, 3, '#ffd86a'); c.px(hx + 1, hy + 4, '#fff6c8'); c.L.rect(hx, hy + 6, 3, 1, '#3a3f58');
      c.glow(hx + 1, hy + 4, '#ffd86a', 4, n % 2 ? 0.35 : 0.25);
    }
    if (acc === 'cle') {
      for (k = 0; k < 5; k++) c.px(hx + 1, hy - 1 - k, MET);
      c.px(hx, hy - 6, MET); c.px(hx + 2, hy - 6, MET); c.px(hx, hy - 7, MET); c.px(hx + 2, hy - 7, MET);
      c.px(hx + 1, hy - 2, cfg.accent2);
    }
    if (acc === 'bombe') {
      x = hx + 1; y = hy - 4;
      c.L.rect(x, y, 2, 4, '#e8e0d0'); c.L.rect(x, y - 1, 2, 1, cfg.accent); c.px(x, y + 1, cfg.accent);
      for (k = 0; k < 14; k++) { var rr = hasard(k + 1 + (c.pose.brume || 0) * 31); c.fx(x + 3 + Math.floor(rr() * 6), y - 2 + Math.floor(rr() * 6) - 2, [NR, NJ, NC][Math.floor(rr() * 3)], 0.4 + rr() * 0.4); }
    }
  }
  function tablette(c) {
    var cfg = c.cfg, tx = CX - 5, ty = TY + 3;
    c.L.rect(tx, ty, 10, 6, '#3a3f58');
    c.L.rect(tx + 1, ty + 1, 8, 4, '#121a33');
    var lignes = [[3, 5, 2], [5, 2, 4], [2, 6, 3]][(c.pose.tablette - 1) % 3];
    lignes.forEach(function (l, i) { c.L.hline(tx + 2, tx + 1 + l, ty + 2 + i, i === 1 ? cfg.accent2 : cfg.accent); });
    c.glow(CX, ty + 2, cfg.accent, 3, 0.15);
    [c.BL, c.BR].forEach(function (cells) {
      for (var i = cells.length - 2; i < cells.length; i++) c.px(cells[i][0], cells[i][1], SANS_CORPS[c.lig] ? (c.lig === 'esprit' ? espritCouleur(cells[i][1]) : nueeCouleur(c, cells[i][0], cells[i][1])) : (cfg.gants || c.sk));
    });
  }

  /* ── autour ── */
  var BOLT = ['..xx', '.xx.', 'xxxx', '.xx.', 'xx..'];
  var FLAMME = [['...r...', '..rr...', '..ror..', '.rooor.', '.royor.', 'rokyoko', 'royyyor', '.ryyyr.', '..rrr..'],
    ['....r..', '...rr..', '..ror..', '.rooor.', '.royor.', 'rokyoko', 'royyyor', '.ryyyr.', '..rrr..']];
  var GUIRLANDE = ['#ff4fb8', '#3ff0ff', '#ffe14a', '#5dff8a', '#8a5bff', '#ff9a3a'];
  function objetsApplisAutour(c, v, n) {
    var x, y;
    if (v === 'flamme_apprivoisee') poser(c, FLAMME[n % 2], { r: '#e8402a', o: '#ff9a3a', y: '#ffe14a', k: '#1b1530' }, 5, 28 - (n % 2), [0, 0]);
    if (v === 'projecteur_poursuite') {
      /* le faisceau : une trame légère, jamais sur l'avatar (calque des lueurs, hors des pixels pleins) */
      for (y = 17; y <= 60; y++) for (x = 4; x <= 44; x++) {
        var t = (y - 17) / 43, a = 7 + t * 4, b = 9 + t * 34;
        if (x >= a && x <= b && (x + y) % 2 === 0 && !c.L.plein(x, y) && !c.L.plein(x + 1, y) && !c.L.plein(x - 1, y) && !c.L.plein(x, y + 1) && !c.L.plein(x, y - 1)) c.fx(x, y, '#f2c400', (n % 2) ? 0.7 : 0.85);
      }
      poser(c, ['.kkk.', 'kgggk', 'kgYgk', 'kgggk', '.kkk.', '..k..', '.kkk.'], { k: '#2a2440', g: '#8a90a8', Y: '#ffe14a' }, 3, 11, [0, 0]);
    }
    if (v === 'guirlande_cases') {
      for (x = 3; x <= 45; x++) c.px(x, Math.round(15 + 5 * Math.sin(Math.PI * (x - 3) / 42)), '#8a90a8');
      for (var i = 0; i < 6; i++) {
        var px = 6 + i * 7, py = Math.round(15 + 5 * Math.sin(Math.PI * (px - 3) / 42)) + 1, col = GUIRLANDE[(i + n) % 6];
        poser(c, ['ccc', 'ccc', '.c.'], { c: col }, px, py, [0, 0]);
      }
    }
  }
  function objetsAutour(c) {
    var o = c.cfg.o, cfg = c.cfg, n = c.pose.n || 0, i, v = o.autour;
    objetsApplisAutour(c, v, n);
    if (v === 'lucioles') {
      for (i = 0; i < 5; i++) { var a = i * 1.2566 + n * 0.45, x = CX + Math.cos(a) * 20, y = 38 + Math.sin(a) * 15; c.px(x, y, '#fff27a'); c.px(x + 1, y, '#fff27a'); c.glow(rnd(x), rnd(y), NJ, 3, 0.45); }
    }
    if (v === 'bulles') {
      [[5, 0], [40, 11], [8, 23], [38, 30]].forEach(function (b) {
        var y = 56 - mod(n * 4 + b[1], 40);
        [[1, 0], [0, 1], [2, 1], [1, 2]].forEach(function (d) { c.px(b[0] + d[0], y + d[1], '#7ad8ff'); });
        c.fx(b[0] + 1, y + 1, '#e8f8ff', 0.8);
      });
    }
    if (v === 'notes') {
      [[5, 30], [39, 22], [9, 16]].forEach(function (p, k) { c.L.carte(p[0], p[1] - mod(n * 2 + k * 3, 8), ['.xx', '.x.', '.x.', 'xx.'], { x: k % 2 ? cfg.accent2 : cfg.accent }); });
    }
    if (v === 'eclairs') {
      (n % 2 ? [[41, 20], [3, 34], [40, 46]] : [[3, 24], [40, 30], [6, 44]]).forEach(function (p) { c.L.carte(p[0], p[1], BOLT, { x: NJ }); c.px(p[0] + 1, p[1] + 2, '#ffffff'); });
    }
    if (v === 'onomatopee') {
      var r = 4 + (n % 2) * 0.6;
      for (i = 0; i < 8; i++) { var an = i * Math.PI / 4 + (n % 2) * Math.PI / 8; for (var t = r - 0.5; t < r + 2.8; t += 0.5) c.px(7.5 + Math.cos(an) * t, 16.5 + Math.sin(an) * t * 0.85, '#ff6a3a'); }
      c.L.ellipse(7.5, 16.5, r, r * 0.85, '#ffd23a');
      c.L.rect(7, 13, 1, 4, '#2a1a3a'); c.px(7, 18, '#2a1a3a');
    }
    if (v === 'pieces_or') {
      var COIN = [['.gg.', 'gGGg', 'gGGg', '.gg.'], ['.g.', 'gGg', 'gGg', '.g.'], ['g', 'G', 'G', 'g']];
      [[4, 26], [41, 20], [3, 42], [43, 38], [38, 12]].forEach(function (p, k) { c.L.carte(p[0], p[1] + ((n + k) % 2), COIN[(n + k) % 3], { g: OR, G: OR2 }); });
    }
    if (v === 'papillons') {
      var OUV = ['ww.ww', 'wwbww', '.w.w.'], FER = ['.wbw.', '.wbw.', '..b..'];
      [[4, 22, NR], [39, 28, NJ], [8, 46, NC]].forEach(function (p, k) { c.L.carte(p[0], p[1] - ((n + k) % 2), (n + k) % 2 ? FER : OUV, { w: p[2], b: '#2a2a35' }); });
    }
  }

  function aura(c) {
    var n = c.pose.n || 0, L = c.L, r1 = L.anneau(), r2 = new Set();
    r1.forEach(function (k) { [1, -1, K, -K].forEach(function (d) { var q = k + d; if (!L.m.has(q) && !r1.has(q)) r2.add(q); }); });
    r1.forEach(function (k) { c.F.px(k % K, Math.floor(k / K), c.cfg.accent, false, n % 2 ? 0.55 : 0.4); });
    r2.forEach(function (k) { var x = k % K; if (x > 0 && x < W - 1) c.F.px(x, Math.floor(k / K), c.cfg.accent, false, 0.18); });
  }
  /* aura d'énergie : des flammes qui montent depuis le haut de la silhouette */
  function auraEnergie(c) {
    var n = c.pose.n || 0, L = c.L, acc = c.cfg.accent;
    L.anneau().forEach(function (k) {
      var x = k % K, y = Math.floor(k / K);
      c.F.px(x, y, acc, false, 0.55);
      if (!L.m.has(k + K)) return;
      var h = 1 + mod(x * 7 + n * 3, 4) + (y < 36 ? 2 : 0);
      for (var t = 1; t <= h; t++) c.F.px(x, y - t, t === h ? '#ffffff' : acc, false, Math.max(0.2, 0.8 - t * 0.12));
    });
  }

  /* ---------- effets de dessin animé (au-dessus, avec contour) */
  var ZP = ['xxx', '..x', '.x.', 'xxx'], ZG = ['xxxx', '...x', '..x.', '.x..', 'xxxx'];
  var COEUR = ['x.x', 'xxx', '.x.'];
  var GEAR = [['.x.x.', 'xxxxx', '.xox.', 'xxxxx', '.x.x.'], ['x.x.x', '.xxx.', 'xxoxx', '.xxx.', 'x.x.x']];
  function effets(fx, main, dy) {
    var E = new Calque(72, 72), sol = G + 2 - (dy || 0);
    (fx || []).forEach(function (f) {
      var n = f[1] || 0, k;
      if (f[0] === 'zzz') {
        if (n >= 1) E.carte(CX + 9, 22, ZP, { x: '#bfe0ff' });
        if (n >= 2) E.carte(CX + 13, 16, ZG, { x: '#bfe0ff' });
        if (n >= 3) E.carte(CX + 18, 9, ZG, { x: '#bfe0ff' });
      } else if (f[0] === 'bulle_nez') {
        var ey = EY + 1;
        if (n >= 4) { E.carte(CX + 2, ey + 1, ['x.x', '.x.', 'x.x'], { x: '#bfe8ff' }); return; }
        var r = [0, 1.3, 2.1, 2.9][n];
        E.ellipse(CX + 1.5 + r, ey + 2.5, r, r, '#cfeeff'); E.px(CX + 1 + r, ey + 1 + (r > 2 ? 0 : 1), '#ffffff');
      } else if (f[0] === 'nuage') {
        var nf = function (x, y) { return y > 13 ? '#7a8296' : '#aab4c8'; };
        E.ellipse(CX - 4.5, 13, 4.2, 3, null, true, nf); E.ellipse(CX + 0.5, 11, 4.8, 3.8, null, true, nf); E.ellipse(CX + 5.5, 13.5, 3.8, 2.6, null, true, nf);
        [[CX - 5, 0], [CX - 1, 1], [CX + 3, 2], [CX + 6, 0]].forEach(function (g) {
          var y = 18 + mod(n * 2 + g[1] * 3, 9);
          E.px(g[0], y, '#4aa8e8'); E.px(g[0], y + 1, '#7ad8ff');
        });
        if (n === 4) E.carte(CX - 1, 15, ['.x', 'x.', '.x'], { x: '#ffe14a' });
      } else if (f[0] === 'etincelles') {
        var pts = n % 2 ? [[7, 20, NJ], [40, 16, NR], [12, 11, NC], [36, 30, NJ]] : [[9, 14, NC], [38, 22, NJ], [17, 10, NR], [4, 30, NR]];
        pts.forEach(function (p) { E.px(p[0], p[1], p[2]); E.px(p[0] - 1, p[1], p[2]); E.px(p[0] + 1, p[1], p[2]); E.px(p[0], p[1] - 1, p[2]); E.px(p[0], p[1] + 1, p[2]); E.px(p[0], p[1], '#ffffff'); });
      } else if (f[0] === 'confettis') {
        var r2 = hasard(11 + n * 7), cols = [NR, NJ, NC, NV, NO, NG];
        for (k = 0; k < 12; k++) {
          var x = 2 + Math.floor(r2() * 44), y = 9 + Math.floor(r2() * 30);
          if (x > 13 && x < 34 && y > 18) continue;
          E.rect(x, y, r2() < 0.5 ? 2 : 1, r2() < 0.5 ? 1 : 2, cols[k % 6]);
        }
      } else if (f[0] === 'coeurs') {
        [[5, 32, NR], [40, 26, '#ff7fa0'], [9, 20, NR]].forEach(function (p, i) { var y = p[1] - mod(n * 3 + i * 4, 10); if (i <= n) E.carte(p[0], y, COEUR, { x: p[2] }); });
      } else if (f[0] === 'saut') {
        [[CX - 9, 0], [CX + 6, 1]].forEach(function (p) { E.hline(p[0], p[0] + 2, sol, '#c8d0e0'); if (n) E.px(p[0] + (p[1] ? 3 : -1), sol - 1, '#c8d0e0'); });
      } else if (f[0] === 'goutte') {
        E.carte(X1 + 2, HY + 3 + n, ['.x.', 'xxx', 'xwx', '.x.'], { x: '#7ad8ff', w: '#ffffff' });
      } else if (f[0] === 'pensee') {
        E.px(CX + 9, 25, '#ffffff'); E.rect(CX + 10, 21, 2, 2, '#ffffff');
        E.ellipse(CX + 15.5, 14.5, 5, 4.2, '#ffffff');
        E.carte(CX + 13, 12, GEAR[n % 2], { x: '#5a5f7a', o: '#ffffff' });
      } else if (f[0] === 'ampoule') {
        E.carte(CX + 12, 8, ['.yyy.', 'yywyy', 'yyyyy', 'yyyyy', '.yyy.', '.ggg.', '.ggg.'], { y: '#ffe14a', w: '#ffffff', g: '#9aa3b8' });
        [[CX + 9, 9], [CX + 18, 9], [CX + 10, 5], [CX + 17, 5], [CX + 14, 4]].forEach(function (p) { E.px(p[0], p[1], '#ffe14a'); });
      } else if (f[0] === 'vent' && main) {
        var hx = main[0] + 3, hy = main[1], dx = n % 2;
        [[0, -2], [1, -1], [1, 0], [0, 1]].forEach(function (d) { E.px(hx + dx + d[0], hy + d[1], '#e8f0ff'); });
        [[0, -3], [1, -2], [2, -1], [2, 0], [1, 1], [0, 2]].forEach(function (d) { E.px(hx + 3 + dx + d[0], hy + d[1], '#e8f0ff'); });
      }
    });
    E.contour(CONTOUR);
    return E;
  }

  /* ════════════════════════════════════════════
     LE MARGOUILLAT VERT À TURBINE
     Rastérisé par couverture (sur-échantillonnage), à 16, 24, 32 ou 48 px.
     ════════════════════════════════════════════ */
  var M_VERT = '#3fbf4a', M_VERT_S = '#2a8a3a';
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
      yeux: [[0.43, 0.12], [0.57, 0.12]]
    };
  }
  function modeleProfil(etat) {
    var tail = etat === 'triste' ? [[0.34, 0.63], [0.24, 0.67], [0.17, 0.71]] : [[0.34, 0.6], [0.24, 0.58], [0.17, 0.5], [0.15, 0.4]];
    return {
      W: 1, H: 0.8, tc: etat === 'triste' ? [0.1, 0.72] : [0.14, 0.3], tr: 0.1, ventre: 0.61,
      corps: [['e', 0.52, 0.57, 0.2, 0.075], ['e', 0.8, 0.5, 0.115, 0.1], ['l', tail, 0.065],
        ['l', [[0.66, 0.6], [0.7, 0.67], [0.74, 0.72]], 0.05], ['l', [[0.4, 0.6], [0.36, 0.67], [0.32, 0.72]], 0.05]],
      doigts: [[[0.74, 0.72], 1, 1], [[0.32, 0.72], -1, 1]],
      yeux: [[0.82, 0.48]]
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
    corps.forEach(function (k) { var x = k % K, y = (k - x) / K; C.px(x, y, M_VERT); });
    corps.forEach(function (k) { var x = k % K, y = (k - x) / K; if (!corps.has(k + 1)) C.px(x, y, M_VERT_S); });
    var cx = tc[0] * S, cy = tc[1] * S, r = tr * S + 0.2;
    turb.forEach(function (k) { var x = k % K, y = (k - x) / K; C.px(x, y, Math.hypot(x + 0.5 - cx, y + 0.5 - cy) > r - 1.1 ? M_ANNEAU : '#1f2a44'); });
    var pal = etat !== 'triste' ? M_PALE : '#9aa3b8', hub = etat !== 'triste' ? M_MOYEU : '#c8ccd8';
    if (S >= 48) {
      for (var kk = 0; kk < 3; kk++) {
        var a = (rot || 0) - Math.PI / 2 + kk * 2.094;
        [1.2, 2.2].forEach(function (t) { C.px(cx - 0.5 + Math.cos(a) * t, cy - 0.5 + Math.sin(a) * t, pal); });
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
      I(1500, { bras: 'repos', yeux: 'ouverts', bouche: 'sourire' }),
      I(700, { bras: 'repos', yeux: 'ouverts', bouche: 'sourire', regard: -1, souffle: 1, turbine: 1, egaliseur: 1, nuee: 1 }, { cn: 1 }),
      I(700, { bras: 'repos', yeux: 'ouverts', bouche: 'neutre', regard: 1, turbine: 2, egaliseur: 2 }),
      I(140, { bras: 'repos', yeux: 'fermes', bouche: 'sourire' })] },
    content: { nom: 'content·e', comp: 'content', images: [
      I(800, { bras: 'ouvert', yeux: 'rieurs', bouche: 'rire', joues: 1 }, { fx: [['coeurs', 2]] }),
      I(140, { bras: 'ouvert', yeux: 'rieurs', bouche: 'rire', joues: 1, souffle: 1 }, { fx: [['coeurs', 0], ['saut', 0]] }),
      I(200, { bras: 'ouvert', yeux: 'rieurs', bouche: 'grand_rire', joues: 1, turbine: 1, egaliseur: 1 }, { dy: -3, fx: [['coeurs', 1], ['saut', 1]], cn: 1 }),
      I(160, { bras: 'ouvert', yeux: 'rieurs', bouche: 'rire', joues: 1, turbine: 2 }, { dy: -1, fx: [['coeurs', 2]] }),
      I(700, { bras: 'ouvert', yeux: 'rieurs', bouche: 'sourire', joues: 1, souffle: 1, egaliseur: 2 }, { fx: [['coeurs', 3]] })] },
    tres_content: { nom: 'très content·e', comp: 'content', images: [
      I(260, { bras: 'haut', yeux: 'etoiles', bouche: 'grand_rire', joues: 1, souffle: 1, roue: 1 }, { fx: [['confettis', 0], ['etincelles', 0]] }),
      I(200, { bras: 'haut', yeux: 'etoiles', bouche: 'grand_rire', joues: 1, turbine: 1, egaliseur: 1, roue: 2, brume: 1 }, { dy: -3, fx: [['confettis', 1], ['etincelles', 1], ['saut', 1]], cn: 1 }),
      I(200, { bras: 'haut', yeux: 'etoiles', bouche: 'grand_rire', joues: 1, turbine: 2, egaliseur: 2, roue: 3, brume: 2 }, { dy: -5, fx: [['confettis', 2], ['etincelles', 0]], cn: 1 }),
      I(200, { bras: 'haut', yeux: 'rieurs', bouche: 'rire', joues: 1, turbine: 3, egaliseur: 3 }, { dy: -2, fx: [['confettis', 3], ['etincelles', 1]] })] },
    triste: { nom: 'triste', comp: 'triste', images: [
      I(900, { bras: 'triste', yeux: 'tristes', bouche: 'vague', tete: 'baisse', ombre: 1, cascade: 0 }, { fx: [['nuage', 0]] }),
      I(700, { bras: 'triste', yeux: 'tristes', bouche: 'triste', tete: 'baisse', ombre: 1, cascade: 1 }, { fx: [['nuage', 2]] }),
      I(700, { bras: 'triste', yeux: 'tristes', bouche: 'vague', tete: 'baisse', ombre: 1, cascade: 2, souffle: 1 }, { fx: [['nuage', 4]] })] },
    concentre: { nom: 'concentré·e', comp: 'neutre', images: [
      I(500, { bras: 'clavier', yeux: 'concentres', bouche: 'langue', tablette: 1 }, { fx: [['goutte', 0], ['pensee', 0]] }),
      I(420, { bras: 'clavier3', yeux: 'concentres', bouche: 'langue', tablette: 3 }, { fx: [['goutte', 1], ['pensee', 1]] }),
      I(420, { bras: 'clavier2', yeux: 'concentres', bouche: 'langue', tablette: 2 }, { fx: [['goutte', 2], ['pensee', 0]] }),
      I(420, { bras: 'clavier3', yeux: 'concentres', bouche: 'neutre', tablette: 3 }, { fx: [['goutte', 0], ['pensee', 1]], cn: 1 }),
      I(900, { bras: 'clavier', yeux: 'grands', bouche: 'o', tablette: 1, souffle: 1 }, { dy: -1, fx: [['ampoule', 0]] })] },
    salue: { nom: 'salue', comp: 'content', images: [
      I(320, { bras: 'salut', yeux: 'ouverts', bouche: 'rire', joues: 1 }, { fx: [['vent', 0]] }),
      I(280, { bras: 'salut2', yeux: 'ouverts', bouche: 'grand_rire', joues: 1, turbine: 1, clin: 1 }, { fx: [['vent', 1]], cn: 1 }),
      I(280, { bras: 'salut', yeux: 'ouverts', bouche: 'rire', joues: 1, turbine: 2 }, { fx: [['vent', 0]] }),
      I(280, { bras: 'salut2', yeux: 'ouverts', bouche: 'grand_rire', joues: 1, clin: 1 }, { fx: [['vent', 1]], cn: 1 }),
      I(1000, { bras: 'salut', yeux: 'ouverts', bouche: 'sourire', joues: 1 })] },
    dort: { nom: 'dort', comp: 'dort', images: [
      I(900, { bras: 'repos', yeux: 'doux', bouche: 'petit', tete: 'baisse' }, { fx: [['zzz', 3], ['bulle_nez', 2]] }),
      I(900, { bras: 'repos', yeux: 'doux', bouche: 'neutre', tete: 'baisse', souffle: 1 }, { fx: [['zzz', 1], ['bulle_nez', 3]] }),
      I(250, { bras: 'repos', yeux: 'doux', bouche: 'o', tete: 'baisse' }, { fx: [['zzz', 2], ['bulle_nez', 4]] }),
      I(900, { bras: 'repos', yeux: 'doux', bouche: 'petit', tete: 'baisse' }, { fx: [['zzz', 3], ['bulle_nez', 1]] })] }
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
      S.sur(effets(img.fx, main, dy), 0, dy);
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
      '@media (prefers-reduced-motion:reduce){.eq-img{animation:none!important}}',
      /* T133b : marques, bulles, mode calme, plafond, pause (classes nouvelles seulement) */
      '.eq-calme .eq-img,.eq.eq-fige .eq-img{animation:none!important;opacity:0!important}.eq-calme .eq-img.eq-i0,.eq.eq-fige .eq-img.eq-i0{opacity:1!important}',
      '.eq-pause .eq-img,.eq-pause .eq-bulle{animation-play-state:paused!important}',
      '.eq.eq-porteur{position:relative}',
      '.eq-vh{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}',
      '.eq-fanion{position:absolute;left:0;top:0;width:var(--eq-marque,14px);height:calc(var(--eq-marque,14px)*1.43);line-height:0;z-index:2}',
      '.eq-fanion svg,.eq-flamme svg{display:block;width:100%;height:100%;overflow:visible}',
      '.eq-flamme{position:absolute;right:0;bottom:0;width:calc(var(--eq-marque,14px)*1.3);height:calc(var(--eq-marque,14px)*1.6);line-height:0;z-index:2}',
      '.eq-flamme b{position:absolute;left:0;right:0;top:42%;text-align:center;font:700 calc(var(--eq-marque,14px)*.72)/1 var(--td-texte,system-ui,sans-serif);color:#121016}',
      '.eq-bulle{position:absolute;z-index:3;left:50%;bottom:100%;transform:translate(-50%,-6px);width:max-content;max-width:var(--eq-bulle-max,14em);padding:.3em .65em;' +
        'background:var(--td-fond,#fff);color:var(--td-encre,#121016);border:1.4px solid var(--td-trait-fort,#121016);border-radius:12px;box-shadow:3px 3px 0 var(--td-neon-2,#FF2E97);' +
        'font:700 var(--eq-bulle-taille,1rem)/1.2 var(--td-texte,system-ui,sans-serif);text-align:center;white-space:normal;animation:eq-bulle-vient .25s ease-out both}',
      '.eq-acomp .eq-bulle{left:32.4%}',
      '.eq-bulle::after{content:"";position:absolute;left:50%;bottom:-7px;width:11px;height:11px;background:inherit;border-right:inherit;border-bottom:inherit;transform:translateX(-50%) rotate(45deg)}',
      '@keyframes eq-bulle-vient{from{opacity:0;transform:translate(-50%,0)}to{opacity:1;transform:translate(-50%,-6px)}}',
      '.eq-calme .eq-bulle{animation:none!important}',
      '@media (prefers-reduced-motion:reduce){.eq-bulle{animation:none!important}}',
      '@media print{.eq-bulle{display:none}}'
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
    function nom(champ, v) { var e = CATALOGUE[champ].filter(function (x) { return x.id === v; })[0]; return e ? e.nom.charAt(0).toLowerCase() + e.nom.slice(1) : v; }
    var morceaux = ['Avatar, lignée ' + nom('lignee', d.lignee).replace(/^./, function (c) { return c.toUpperCase(); })];
    if (!SANS_CORPS[d.lignee]) morceaux.push('teint ' + d.teint);
    morceaux.push('coiffure ' + nom('coiffure', d.coiffure));
    if (d.haut !== 'aucun') morceaux.push(nom('haut', d.haut));
    if (!SANS_CORPS[d.lignee]) { morceaux.push(nom('bas', d.bas)); morceaux.push(nom('chaussures', d.chaussures)); }
    EMPLACEMENTS.forEach(function (e) {
      var v = d.objets[e]; if (v === 'aucun') return;
      var x = CATALOGUE.objets[e].filter(function (y) { return y.id === v; })[0];
      morceaux.push(x.nom.charAt(0).toLowerCase() + x.nom.slice(1));
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
    var etat = etatMoteur(o.etat);
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
    var dessins = enCache(JSON.stringify(d) + '|' + etat + '|' + cadre + '|' + avecComp + '|' + anime, function () {
      return images.map(function (img, i) { var S = imageAvatar(cfg, img, etat, avecComp, i); return cheminsSet(S.anneau(), 'eq-halo') + chemins(S); });
    });
    images.forEach(function (img, i) {
      var st = anim ? ' style="animation:' + anim.noms[i] + ' ' + anim.T + 'ms step-end ' + (-dec) + 'ms infinite"' : '';
      corps += '<g class="eq-img eq-i' + i + '"' + st + '>' + dessins[i] + '</g>';
    });
    var aria = alt === '' ? ' aria-hidden="true" focusable="false"' : ' role="img" aria-label="' + esc(alt) + '"';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="' + vb.join(' ') + '" width="' + largeur + '" height="' + taille + '" shape-rendering="crispEdges"' + aria + '>' + (alt ? '<title>' + esc(alt) + '</title>' : '') + corps + '</svg>';
  }

  function classes(o, cadre) {
    var c = 'eq eq-' + cadre;
    if (o.fond === 'obscur') c += ' eq-obscur'; else if (o.fond === 'clair') c += ' eq-clair';
    return c;
  }

  /* ════════════════════════════════════════════
     L'INTERFACE DES APPLICATIONS (T133b)
     États d'usage, gestes, bulles d'une liste fermée, marques (fanion,
     flamme), mode calme, plafond d'avatars animés, pause, cache.
     ════════════════════════════════════════════ */
  /* les états nommés par usage : des alias des états du moteur */
  var USAGES = { lobby: 'repos', attente: 'concentre', repondu: 'repos', fete: 'tres_content', applaudit: 'content' };
  function etatMoteur(e) { return ETATS[e] ? e : (USAGES[e] || 'repos'); }
  /* les gestes du lobby : un état joué un moment, puis retour à l'état d'avant */
  var GESTES = [
    { id: 'salue', nom: 'Saluer', etat: 'salue' }, { id: 'saute', nom: 'Sauter de joie', etat: 'tres_content' },
    { id: 'rit', nom: 'Rire', etat: 'content' }, { id: 'sieste', nom: 'Petite sieste', etat: 'dort' }
  ];
  var GESTE_DE = {}; GESTES.forEach(function (g) { GESTE_DE[g.id] = g; });
  /* les 21 phrases du lobby : liste FERMÉE, envoyée par numéro (de 0 à 20).
     Version 1. On n'en retire jamais et on n'en change jamais le sens : on ajoute à la fin, et la version monte.
     Copie versionnée : assets/equipage/applis.json (charte/equipage-donnees.js la régénère et la vérifie). */
  var PHRASES_VERSION = 1;
  var PHRASES = [
    'Prêt·e !', 'Coucou la classe !', 'Bonne chance à tout le monde !', 'J’ai le trac, mais j’y vais.', 'Allez, on se lance !',
    'Mon cerveau charge… 87 %', 'Le margouillat est avec nous.', 'On se trompe, on apprend.', 'Même pas peur (enfin, un peu).', 'Je suis là, et bien réveillé·e !',
    'On fait ça ensemble.', 'Bravo d’avance à tout le monde.', 'J’ai révisé… dans mes rêves.', 'Respire, ça va bien se passer.', 'Wi-Fi, ne me lâche pas.',
    'Je sens que je vais apprendre un truc.', 'Qui a vu mon stylo ?', 'Pas de stress : c’est pour apprendre.', 'Hâte de voir la première question !',
    'Ne vous inquiétez pas, Monsieur.', 'Moi, c’est au talent.'
  ];
  /* les phrases qui s'adressent à l'enseignant·e : la page projetée choisit la forme (Equipage.adresse) ;
     l'élève envoie le même numéro, quelle que soit la forme */
  var ADRESSES = { monsieur: 'Monsieur', madame: 'Madame' }, _adresse = 'monsieur';
  var VARIANTES = { 19: function (a) { return 'Ne vous inquiétez pas, ' + ADRESSES[a] + '.'; } };
  function phrase(n) { return VARIANTES[n] ? VARIANTES[n](_adresse) : PHRASES[n]; }
  /* Equipage.adresse('monsieur' | 'madame') : réglage de l'enseignant·e sur la page projetée ; Equipage.adresse() le lit */
  function adresse(a) { if (a !== undefined && ADRESSES[a]) _adresse = a; return _adresse; }
  /* les joueurs et joueuses sans compte : l'Esprit en capuche, le même pour tous (décision du 24/11) */
  var NEUTRE = normaliser({ lignee: 'esprit', coiffure: 'capuche', haut: 'sweat', compagnon: 'margouillat', couleurs: { haut: 'sarcelle', accent: 'cyan' } });

  /* cache des dessins : par description, état, cadre, compagnon et animation */
  var _cache = {}, _nCache = 0, CACHE_MAX = 400;
  function enCache(cle, faire) {
    if (Object.prototype.hasOwnProperty.call(_cache, cle)) return _cache[cle];
    if (_nCache >= CACHE_MAX) { _cache = {}; _nCache = 0; }
    _nCache += 1;
    return (_cache[cle] = faire());
  }

  /* ── réglages de la page ── */
  var _calme = null, _plafond = Infinity, _vivants = [], _ecoute = false;
  function racineDoc() { return typeof document !== 'undefined' ? document.documentElement : null; }
  function mouvementReduit() {
    try { return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  }
  /* Equipage.calme(true | false) pour toute la page ; Equipage.calme() dit si la page est calme
     (forcée, ou réglage « mouvement réduit » de l'appareil) */
  function calme(v) {
    if (v === undefined) return _calme === true || (_calme === null && mouvementReduit());
    _calme = v === null ? null : !!v;
    var r = racineDoc();
    if (r) { feuille(); if (_calme === true) r.classList.add('eq-calme'); else r.classList.remove('eq-calme'); }
    repartir(true);
    return calme();
  }
  /* Equipage.plafond(8) : au plus 8 avatars animés à la fois (les gestes d'abord), les autres en image fixe */
  function plafond(n) {
    if (n === undefined) return _plafond;
    _plafond = n === null || n === Infinity ? Infinity : Math.max(0, Math.floor(+n) || 0);
    repartir(true);
    return _plafond;
  }
  /* Equipage.pause(true | false) : arrête les animations ; automatique quand l'onglet est caché */
  function pause(v) {
    var r = racineDoc(); if (!r) return false;
    feuille();
    if (v === undefined) return r.classList.contains('eq-pause');
    if (v) r.classList.add('eq-pause'); else r.classList.remove('eq-pause');
    return !!v;
  }
  function ecouter() {
    if (_ecoute || typeof document === 'undefined' || !document.addEventListener) return;
    _ecoute = true;
    document.addEventListener('visibilitychange', function () { pause(document.hidden); });
  }
  /* qui a le droit d'être animé : seulement quand un plafond ou le calme est demandé */
  function repartir(rendreTout) {
    _vivants = _vivants.filter(function (v) { return !v.mort && (!v.element || v.element.isConnected !== false); });
    var limite = _calme === true ? 0 : _plafond, rang = 0;
    var ordre = _vivants.filter(function (v) { return v.geste; }).concat(_vivants.filter(function (v) { return !v.geste; }));
    ordre.forEach(function (v) {
      var ok = limite === Infinity || (v.veutAnime() && rang < limite);
      if (ok && limite !== Infinity && v.veutAnime()) rang += 1;
      if (v.autorise !== ok) { v.autorise = ok; if (rendreTout) v.rendre(); }
    });
  }

  /* ── les bulles : 6 au plus par page, les autres attendent ── */
  var BULLES_MAX = 6, _bullesVues = 0, _fileBulles = [];
  function listeDe(liste) {
    if (liste === undefined || liste === null || liste === 'lobby') return PHRASES;
    if (Array.isArray(liste)) return liste;
    return null;
  }
  function suivanteBulle() {
    while (_bullesVues < BULLES_MAX && _fileBulles.length) {
      var b = _fileBulles.shift();
      if (!b.v.mort) b.v.montrerBulle(b.texte, b.duree);
    }
  }

  /* les marques : le fanion « a répondu » (jamais juste ou faux) et la flamme d'une série */
  var SVG_FANION = '<svg viewBox="0 0 14 20" aria-hidden="true" focusable="false"><path d="M2.5 1v18" stroke="#121016" stroke-width="2" stroke-linecap="round"/><path d="M3.5 2h9l-3 3.6 3 3.6h-9z" fill="#FFE600" stroke="#121016" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  var SVG_FLAMME = '<svg viewBox="0 0 16 20" aria-hidden="true" focusable="false"><path d="M8 1c1 4 6 6 6 11a6 6 0 0 1-12 0c0-3 2-4 2-7 2 1 2 3 2 4 1-2 2-5 2-8z" fill="#FF9A3A" stroke="#121016" stroke-width="1.3"/><path d="M8 11c1 2 3 2.5 3 4.5a3 3 0 0 1-6 0c0-1.5 1-2 1-3.5 1 .5 1.5 1 2-1z" fill="#FFE14A"/></svg>';

  function creer(element, desc, options) {
    var o = {}, k;
    for (k in options || {}) o[k] = options[k];
    var etatDesc = normaliser(desc);
    if (o.decalage === undefined) o.decalage = Math.floor(Math.random() * 4000);
    var marque = null, serie = 0, bulle = null, minuterie = null;
    var v = { element: element, autorise: true, geste: null, mort: false };
    v.veutAnime = function () { return o.anime !== false; };
    function porteur() { return !!(marque || serie >= 2 || bulle); }
    function rendre() {
      var taille = +o.taille > 0 ? +o.taille : 96;
      var cadre = o.cadre && o.cadre !== 'auto' ? o.cadre : (taille < 32 ? 'pastille' : (taille < 64 ? 'buste' : 'entier'));
      var cl = (element.className.replace(/(^|\s)eq(-[a-z]+)?(?=\s|$)/g, '').trim() + ' ' + classes(o, cadre)).trim();
      if (!v.autorise) cl += ' eq-fige';
      if (porteur()) cl += ' eq-porteur';
      var oo = o;
      if (v.geste) { oo = {}; for (var x in o) oo[x] = o[x]; oo.etat = v.geste; }
      if (!v.autorise && oo.anime !== false) { if (oo === o) { oo = {}; for (var y in o) oo[y] = o[y]; } oo.anime = false; }
      var h = svg(etatDesc, oo);
      if (bulle && h.indexOf('viewBox="0 8 74 56"') > 0) cl += ' eq-acomp';
      element.className = cl;
      if (marque === 'repondu') h += '<span class="eq-fanion">' + SVG_FANION + '<span class="eq-vh">a répondu</span></span>';
      if (serie >= 2) h += '<span class="eq-flamme">' + SVG_FLAMME + '<b aria-hidden="true">' + serie + '</b><span class="eq-vh">série de ' + serie + '</span></span>';
      element.innerHTML = h;
      if (bulle) element.appendChild(bulle.el);
    }
    v.rendre = rendre;
    v.montrerBulle = function (texte, duree) {
      if (typeof document === 'undefined') return;
      if (!bulle) {
        _bullesVues += 1;
        var el = document.createElement('span');
        el.className = 'eq-bulle';
        bulle = { el: el };
        el.textContent = texte;           /* jamais de HTML : du texte d'une liste fermée */
        rendre();
      } else {
        bulle.el.textContent = texte;
        clearTimeout(bulle.t);
      }
      bulle.t = setTimeout(cacherBulle, duree);
    };
    function cacherBulle() {
      if (!bulle) return;
      clearTimeout(bulle.t);
      if (bulle.el.parentNode) bulle.el.parentNode.removeChild(bulle.el);
      bulle = null; _bullesVues = Math.max(0, _bullesVues - 1);
      if (!v.mort) rendre();
      suivanteBulle();
    }
    if (o.etat === 'repondu') marque = 'repondu';
    if (_vivants.length > 300) repartir(false);
    _vivants.push(v); ecouter();
    if (_plafond !== Infinity || _calme === true) repartir(false);
    rendre();
    return {
      element: element,
      get description() { return copie(etatDesc); },
      maj: function (d) { etatDesc = normaliser(d); rendre(); return this; },
      etat: function (e) {
        o.etat = e;
        if (e === 'repondu') marque = 'repondu'; else if (e === 'attente' || e === 'lobby') marque = null;
        rendre(); return this;
      },
      options: function (p) { for (var k in p) o[k] = p[k]; repartir(false); rendre(); return this; },
      /* geste('salue' | 'saute' | 'rit' | 'sieste', { duree: 3000 }) : un nom inconnu est ignoré */
      geste: function (nom, opt) {
        var g = GESTE_DE[nom];
        if (!g || v.mort) return false;
        var duree = opt && +opt.duree > 0 ? Math.min(+opt.duree, 20000) : 3000;
        clearTimeout(minuterie);
        v.geste = g.etat; repartir(true); rendre();
        minuterie = setTimeout(function () { v.geste = null; if (!v.mort) { repartir(true); rendre(); } }, duree);
        return true;
      },
      /* bulle(numero, liste) : une phrase d'une liste fermée (par défaut, les 20 phrases du lobby) ;
         numéro inconnu ignoré ; 6 bulles au plus par page, les autres attendent leur tour */
      bulle: function (numero, liste, opt) {
        var l = listeDe(liste);
        if (!l || v.mort || typeof numero !== 'number' || numero % 1 !== 0 || numero < 0 || numero >= l.length || typeof l[numero] !== 'string') return false;
        var duree = opt && +opt.duree > 0 ? Math.min(+opt.duree, 15000) : 5000;
        var texte = l === PHRASES ? phrase(numero) : l[numero];
        if (bulle || _bullesVues < BULLES_MAX) { v.montrerBulle(texte, duree); return true; }
        _fileBulles = _fileBulles.filter(function (b) { return b.v !== v; });
        _fileBulles.push({ v: v, texte: texte, duree: duree });
        return true;
      },
      /* marque('repondu' | null) : le fanion ; serie(n) : la flamme et son chiffre, à partir de 2 */
      marque: function (m) { marque = m === 'repondu' ? 'repondu' : null; rendre(); return this; },
      serie: function (n) { n = Math.floor(+n) || 0; serie = n > 0 ? Math.min(n, 999) : 0; rendre(); return this; },
      get anime() { return v.autorise && o.anime !== false; },
      detruire: function () {
        v.mort = true; clearTimeout(minuterie);
        if (bulle) { clearTimeout(bulle.t); bulle = null; _bullesVues = Math.max(0, _bullesVues - 1); }
        _fileBulles = _fileBulles.filter(function (b) { return b.v !== v; });
        element.innerHTML = '';
        repartir(true); suivanteBulle();
      }
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
      haut: SANS_CORPS[lig] && r() < 0.6 ? 'aucun' : (function (l) { return l[Math.floor(r() * l.length)].id; })(CATALOGUE.haut.filter(function (e) { return e.id !== 'aucun'; })),
      bas: un('bas'), chaussures: un('chaussures'),
      objets: {}, fauteuil: r() < 0.08, compagnon: r() < 0.5 ? 'margouillat' : un('compagnon'),
      couleurs: { haut: cle('tissu'), bas: cle('tissu'), accent: cle('neon'), chaussures: cle('chaussures'), yeux: cle('yeux') }
    };
    var proba = { tete: 0.5, visage: 0.3, cou: 0.3, dos: 0.35, main: 0.5, epaule: 0.25, pieds: 0.25, autour: 0.25 };
    /* les objets des applications ne sortent jamais au hasard : ce sont des trophées (tirages inchangés) */
    EMPLACEMENTS.forEach(function (e) {
      var l = CATALOGUE.objets[e].filter(function (x) { return x.famille !== 'applis'; });
      RETIRES.forEach(function (x) { if (x[0] === e) l.splice(x[2], 0, { id: 'aucun' }); });
      d.objets[e] = r() < proba[e] ? l[1 + Math.floor(r() * (l.length - 1))].id : 'aucun';
    });
    if (d.couleurs.bas === d.couleurs.haut) d.couleurs.bas = 'anthracite';
    return normaliser(d);
  }

  /* modèles : les huit tenues de la planche v2 et les sept lignées */
  function M(o) { var d = copie(DEFAUT); for (var k in o) if (k === 'couleurs' || k === 'objets') { for (var c in o[k]) d[k][c] = o[k][c]; } else d[k] = o[k]; return normaliser(d); }
  var MODELES = {
    fibre: { nom: 'Fibre optique', etat: 'salue', description: M({ teint: 8, coiffure: 'tresses_fibre', haut: 'veste', bas: 'cargo', chaussures: 'montantes', objets: { dos: 'sac_antenne' }, couleurs: { haut: 'violet', bas: 'anthracite', accent: 'cyan', chaussures: 'blanches' } }) },
    lycee: { nom: 'Sortie du lycée', etat: 'content', description: M({ teint: 5, corps: 'fine', coiffure: 'degrade_circuit', haut: 'maillot_comores', bas: 'short', chaussures: 'baskets', objets: { tete: 'casquette_mabawa', epaule: 'coelacanthe' }, compagnon: 'robot', couleurs: { bas: 'nuit', accent: 'jaune', chaussures: 'blanches' } }) },
    fleurs: { nom: 'Fleurs-circuits', etat: 'repos', description: M({ teint: 6, corps: 'ronde', coiffure: 'chignon_antenne', cheveux: 'bruns', haut: 'tunique', bas: 'jupe_longue', chaussures: 'savates', objets: { epaule: 'kishali', cou: 'collier_coquillages', autour: 'papillons' }, compagnon: 'roussette', couleurs: { haut: 'sarcelle', bas: 'rose', accent: 'jaune', chaussures: 'noires', yeux: 'noirs' } }) },
    capuche: { nom: 'Capuche réseau', etat: 'concentre', description: M({ teint: 3, coiffure: 'capuche', cheveux: 'chatains', haut: 'sweat', bas: 'patchwork', chaussures: 'baskets', objets: { tete: 'casque_audio', autour: 'notes' }, couleurs: { haut: 'marine', bas: 'gris', accent: 'cyan', chaussures: 'rouges', yeux: 'verts' } }) },
    fauteuil: { nom: 'Fauteuil de course', etat: 'tres_content', description: M({ teint: 2, coiffure: 'court', cheveux: 'auburn', haut: 'combinaison', bas: 'pantalon', objets: { tete: 'bandeau' }, fauteuil: true, couleurs: { haut: 'nuit', bas: 'nuit', accent: 'rose', chaussures: 'blanches', yeux: 'bleus' } }) },
    mecano: { nom: 'Mécano de la Flottille', etat: 'repos', description: M({ teint: 4, corps: 'ronde', coiffure: 'boucles', cheveux: 'bruns', haut: 'gilet', bas: 'patchwork', chaussures: 'bottes', objets: { dos: 'turbine_dos', tete: 'soudure', main: 'cle' }, compagnon: 'tortue', couleurs: { haut: 'kaki', bas: 'jean', accent: 'orange', chaussures: 'jaunes' } }) },
    battle: { nom: 'Battle', etat: 'tres_content', description: M({ teint: 7, coiffure: 'afro_pixel', haut: 'debardeur', bas: 'sarouel', chaussures: 'montantes', objets: { main: 'enceinte', autour: 'aura' }, couleurs: { haut: 'blanc', bas: 'nuit', accent: 'violet', chaussures: 'noires' } }) },
    pochoir: { nom: 'Pochoir', etat: 'salue', description: M({ teint: 1, corps: 'fine', coiffure: 'crete_graffiti', cheveux: 'bruns', haut: 'chemise', bas: 'jogging', chaussures: 'baskets', objets: { main: 'bombe', visage: 'lunettes_ecran' }, compagnon: 'maki', couleurs: { haut: 'anthracite', bas: 'anthracite', accent: 'vert', chaussures: 'blanches', yeux: 'bleus' } }) },
    pirate: { nom: 'Pirate du lagon', etat: 'content', description: M({ teint: 6, coiffure: 'locks_cables', haut: 'chemise', bas: 'sarouel', chaussures: 'pieds_nus', objets: { tete: 'bandana', dos: 'drapeau', main: 'carte_tresor', autour: 'bulles' }, couleurs: { haut: 'sarcelle', bas: 'beige', accent: 'cyan' } }) },
    fete: { nom: 'Soir de fête', etat: 'salue', description: M({ lignee: 'esprit', coiffure: 'lisses', cheveux: 'roses', haut: 'tunique', objets: { visage: 'loup', dos: 'ailes_fee', main: 'lanterne', autour: 'lucioles' }, couleurs: { haut: 'prune', accent: 'jaune' } }) },
    reseau: { nom: 'Implant et visière', etat: 'concentre', description: M({ lignee: 'cyber', teint: 3, coiffure: 'rase', haut: 'combinaison', bas: 'jogging', objets: { visage: 'visiere', epaule: 'drone', dos: 'jetpack' }, couleurs: { haut: 'marine', bas: 'nuit', accent: 'rose' } }) },
    infini: { nom: 'Manique de l\'infini', etat: 'tres_content', description: M({ teint: 7, corps: 'ronde', coiffure: 'puffs', cheveux: 'noirs', haut: 'combinaison', bas: 'jogging', chaussures: 'montantes', objets: { tete: 'bandeau_noue', main: 'manique_infini', dos: 'cape', cou: 'ceinture_boucle', autour: 'aura_energie' }, couleurs: { haut: 'violet', bas: 'nuit', accent: 'jaune', chaussures: 'blanches' } }) },
    capitaine: { nom: 'Capitaine du lagon', etat: 'salue', description: M({ teint: 5, coiffure: 'tresses', haut: 'chemise', bas: 'cargo', chaussures: 'baskets', objets: { tete: 'tricorne', visage: 'cache_oeil', epaule: 'perroquet_robot', main: 'longue_vue', pieds: 'bottes_pirate', autour: 'pieces_or' }, couleurs: { haut: 'marine', bas: 'beige', accent: 'cyan' } }) },
    shingo: { nom: 'Pause de midi', etat: 'content', description: M({ teint: 6, coiffure: 'afro_pixel', cheveux: 'noirs', haut: 'maillot_mada', bas: 'salouva', chaussures: 'savates', objets: { tete: 'peigne', visage: 'ski_yeux' }, compagnon: 'maki', couleurs: { bas: 'canard', accent: 'rose', chaussures: 'noires' } }) },
    punk: { nom: 'Punk du quai', etat: 'tres_content', description: M({ teint: 2, corps: 'fine', coiffure: 'rase', cheveux: 'violets', haut: 'debardeur', bas: 'patchwork', chaussures: 'montantes', objets: { tete: 'crete_pics', cou: 'badges', epaule: 'veste_ecussons', main: 'megaphone', pieds: 'skate', autour: 'notes' }, couleurs: { haut: 'blanc', bas: 'jean', accent: 'vert' } }) },
    salle: { nom: 'Chaise à accoudoirs', etat: 'content', description: M({ teint: 4, coiffure: 'boucles', cheveux: 'bruns', haut: 'sweat', bas: 'pantalon', objets: { dos: 'chaise_accoudoirs', main: 'feutre', cou: 'cle_usb', epaule: 'souris_marche' }, couleurs: { haut: 'canard', bas: 'anthracite', accent: 'cyan' } }) },
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
    defaut: function () { return copie(DEFAUT); }, compat: copie(COMPAT),
    /* T133b : l'interface des applications */
    USAGES: copie(USAGES), gestes: GESTES.map(function (g) { return { id: g.id, nom: g.nom, etat: g.etat }; }),
    phrases: PHRASES.slice(), phrasesVersion: PHRASES_VERSION, adresse: adresse, phrase: function (n) { return typeof n === 'number' && PHRASES[n] !== undefined ? phrase(n) : null; },
    variantes: Object.keys(VARIANTES).map(Number),
    applis: APPLIS.map(function (a) { return { id: a[0], nom: a[1], emplacement: a[2], application: a[3], haut_fait: a[4], haut_fait_nom: a[5], categorie: a[6], condition: a[7] }; }),
    neutre: function () { return copie(NEUTRE); },
    calme: calme, plafond: plafond, pause: pause, viderCache: function () { _cache = {}; _nCache = 0; }
  };
  Object.freeze(API.phrases);
  if (typeof module === 'object' && module.exports) module.exports = API;
  else racine.Equipage = API;
})(typeof window !== 'undefined' ? window : this);
