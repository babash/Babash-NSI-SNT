/* Contrôle de notions : arbres binaires (NSI, terminale)
   Babash - NSI Tani Malandi · contenus CC BY-SA 4.0 · code MIT

   Ce fichier est chargé par la page élève, la page prof et la version papier.
   Il contient les énoncés et les arbres, JAMAIS les réponses : la clé de
   correction est dans cle.js, que seules la page prof et le corrigé chargent.

   Le bloc entre les deux marqueurs DONNEES est du JSON pur : le script
   verification/verifier.py le relit pour recalculer toutes les réponses. */

(function () {
  'use strict';

  var DONNEES = /*DONNEES-DEBUT*/{
    "id": "arbres-notions",
    "version": 1,
    "prefixe": "ARB",
    "titre": "Contrôle de notions : arbres binaires",
    "niveau": "NSI, terminale",
    "duree": 20,
    "convention": "Rappel de convention : la profondeur de la racine est 0 ; un arbre réduit à un seul nœud a une hauteur de 0.",
    "consigne": "Pour une liste de valeurs, les écrire dans l'ordre demandé, séparées par des espaces.",
    "code_noeud": "class Noeud:\n    def __init__(self, valeur, gauche=None, droit=None):\n        self.valeur = valeur\n        self.gauche = gauche\n        self.droit = droit\n\ndef taille(arbre):\n    if arbre is None:\n        return 0\n    return ................",
    "sujets": {
      "1": {
        "arbre": [15, [8, [4, null, null], [11, [9, null, null], null]], [22, null, [30, [26, null, null], null]]],
        "noeud_profondeur": 30,
        "chemin": "a.droit.droit.gauche.valeur",
        "insertion": [13, 7, 20, 10, 3, 25],
        "squelette": ["a", ["b", ["d", null, null], ["e", null, null]], ["c", null, ["f", null, null]]],
        "abr_options": [
          ["a", "Non : 26 est plus petit que 30, il devrait donc se trouver à droite de 30."],
          ["b", "Non : 22 n'a pas de fils gauche, donc cet arbre ne peut pas être un ABR."],
          ["c", "Oui : pour chaque nœud, son sous-arbre gauche est plus petit et son sous-arbre droit plus grand."],
          ["d", "Non : lu ligne par ligne, l'arbre ne donne pas les valeurs dans l'ordre croissant."]
        ]
      },
      "2": {
        "arbre": [40, [25, [12, null, null], [31, null, [45, null, null]]], [52, [47, null, null], [60, null, null]]],
        "noeud_profondeur": 47,
        "chemin": "a.gauche.droit.droit.valeur",
        "insertion": [30, 18, 42, 35, 22, 50],
        "squelette": ["a", ["b", null, ["d", null, null]], ["c", ["e", null, null], ["f", null, null]]],
        "abr_options": [
          ["a", "Oui : chaque nœud est plus grand que son fils gauche et plus petit que son fils droit."],
          ["b", "Non : 45 est dans le sous-arbre gauche de 40, alors que 45 est plus grand que 40."],
          ["c", "Non : 31 n'a pas de fils gauche, donc cet arbre ne peut pas être un ABR."],
          ["d", "Non : 12 est plus petit que 25, il devrait donc se trouver à droite de 25."]
        ]
      }
    },
    "questions": [
      {"id": "q1", "nom": "Racine", "type": "valeur", "enonce": "Quelle est la racine de l'arbre ?"},
      {"id": "q2", "nom": "Feuilles", "type": "ensemble", "enonce": "Donner toutes les feuilles de l'arbre."},
      {"id": "q3", "nom": "Taille", "type": "valeur", "enonce": "Quelle est la taille de l'arbre ?"},
      {"id": "q4", "nom": "Hauteur", "type": "valeur", "enonce": "Quelle est la hauteur de l'arbre ?"},
      {"id": "q5", "nom": "Profondeur", "type": "valeur", "enonce": "Quelle est la profondeur du nœud {noeud} ?"},
      {"id": "q6", "nom": "ABR ou non", "type": "qcu", "enonce": "Cet arbre est-il un arbre binaire de recherche (ABR) ? Choisir la bonne réponse."},
      {"id": "q7", "nom": "Parcours en largeur", "type": "liste", "enonce": "Donner le parcours en largeur de l'arbre."},
      {"id": "q8", "nom": "Parcours préfixe", "type": "liste", "enonce": "Donner le parcours en profondeur préfixe de l'arbre."},
      {"id": "q9", "nom": "Parcours infixe", "type": "liste", "enonce": "Donner le parcours en profondeur infixe de l'arbre."},
      {"id": "q10", "nom": "Sortie d'un programme", "type": "valeur", "enonce": "La variable a contient l'arbre dessiné, construit avec la classe Noeud. Qu'affiche print({chemin}) ?"},
      {"id": "q11", "nom": "Compléter une ligne", "type": "ligne", "enonce": "Compléter la dernière ligne de la fonction taille, qui renvoie le nombre de nœuds d'un arbre."},
      {"id": "q12", "nom": "Insertion dans un ABR", "type": "schema", "enonce": "On insère dans un ABR vide, dans cet ordre, les valeurs {insertion}. Écrire chaque valeur dans sa case du schéma."}
    ]
  }/*DONNEES-FIN*/;

  /* ── Arbres ─────────────────────────────────────────────── */

  /* Positions : x = rang dans le parcours infixe, y = profondeur. */
  function placer(arbre) {
    var noeuds = [], aretes = [], rang = 0;
    function visiter(t, prof, parent) {
      if (!t) return;
      var moi = { v: t[0], prof: prof };
      visiter(t[1], prof + 1, moi);
      moi.x = rang++;
      noeuds.push(moi);
      if (parent) aretes.push([parent, moi]);
      visiter(t[2], prof + 1, moi);
    }
    visiter(arbre, 0, null);
    return { noeuds: noeuds, aretes: aretes, largeur: rang };
  }

  function texteArbre(t) {
    /* Description pour les lecteurs d'écran : qui est l'enfant de qui. */
    var phrases = [];
    (function visiter(n) {
      if (!n) return;
      var g = n[1] ? n[1][0] : null, d = n[2] ? n[2][0] : null;
      if (g !== null && d !== null) phrases.push(n[0] + ' a pour fils gauche ' + g + ' et pour fils droit ' + d);
      else if (g !== null) phrases.push(n[0] + ' a seulement un fils gauche, ' + g);
      else if (d !== null) phrases.push(n[0] + ' a seulement un fils droit, ' + d);
      visiter(n[1]); visiter(n[2]);
    })(t);
    return 'Racine ' + t[0] + '. ' + phrases.join(' ; ') + '.';
  }

  /* SVG d'un arbre. options.cases : nœuds vides en tirets, avec leur lettre. */
  function svgArbre(arbre, options) {
    options = options || {};
    var p = placer(arbre), dx = options.dx || 46, dy = options.dy || 56, r = options.r || 17;
    var prof = 0;
    p.noeuds.forEach(function (n) { if (n.prof > prof) prof = n.prof; });
    var marge = options.cases ? 16 : 0;
    var L = (p.largeur - 1) * dx + 2 * r + 8 + marge, H = prof * dy + 2 * r + 8 + (options.cases ? 4 : 0);
    function X(n) { return marge + r + 4 + n.x * dx; }
    function Y(n) { return (options.cases ? 6 : 0) + r + 4 + n.prof * dy; }
    var s = [];
    s.push('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + L + ' ' + H + '" width="' + L + '" height="' + H + '" class="arbre-svg" role="img"' +
      (options.titre ? ' aria-label="' + echapper(options.titre) + '"' : '') + '>');
    p.aretes.forEach(function (a) {
      s.push('<line x1="' + X(a[0]) + '" y1="' + Y(a[0]) + '" x2="' + X(a[1]) + '" y2="' + Y(a[1]) + '" class="arete"/>');
    });
    p.noeuds.forEach(function (n) {
      if (options.cases) {
        s.push('<circle cx="' + X(n) + '" cy="' + Y(n) + '" r="' + (r + 2) + '" class="case"/>');
        s.push('<text x="' + (X(n) - r - 3) + '" y="' + (Y(n) - r + 2) + '" class="lettre" text-anchor="end">' + n.v + '</text>');
      } else {
        s.push('<circle cx="' + X(n) + '" cy="' + Y(n) + '" r="' + r + '" class="noeud"/>');
        s.push('<text x="' + X(n) + '" y="' + (Y(n) + 5) + '" class="valeur" text-anchor="middle">' + n.v + '</text>');
      }
    });
    s.push('</svg>');
    return s.join('');
  }

  function lettresSquelette(sq) {
    /* Les lettres des cases, dans l'ordre alphabétique. */
    var l = [];
    (function visiter(t) { if (!t) return; l.push(t[0]); visiter(t[1]); visiter(t[2]); })(sq);
    return l.sort();
  }

  /* ── Énoncés ────────────────────────────────────────────── */

  function enonce(q, sujet) {
    var s = DONNEES.sujets[sujet];
    return q.enonce
      .replace('{noeud}', s.noeud_profondeur)
      .replace('{chemin}', s.chemin)
      .replace('{insertion}', s.insertion.join(', '))
      .replace(/ ([?:;!])/g, String.fromCharCode(0xA0) + '$1');
  }

  /* ── Normalisation des réponses (pour la correction) ────── */

  function nombres(texte) {
    var m = String(texte || '').match(/-?\d+/g);
    return m ? m.map(Number) : [];
  }
  function ligneCode(texte) {
    return String(texte || '').replace(/\s+/g, '');
  }

  /* ── Code de la copie ───────────────────────────────────────
     Copie = [version, pseudo, classe, sujet, début (minutes depuis 1970),
              durée (secondes), graine du mélange, [réponses q1…q12]]
     Le JSON est codé en UTF-8 puis en base 32 de Crockford (chiffres et
     majuscules : le QR code reste en mode alphanumérique, plus compact),
     suivi d'une somme de contrôle de 4 caractères (CRC-32 tronqué), qui
     repère une copie tronquée ou mal recopiée. Ce n'est PAS une protection. */

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
  function depuisBase32(texte) {
    var bits = 0, val = 0, out = [];
    for (var i = 0; i < texte.length; i++) {
      var c = texte[i];
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
    return DONNEES.prefixe + DONNEES.version + '-' + versBase32(octets) + '-' + controle4(octets);
  }

  /* Repère tous les codes d'un texte collé (retours à la ligne et espaces tolérés). */
  function extraireCodes(texte) {
    var propre = String(texte || '').toUpperCase().replace(/\s+/g, '');
    var re = new RegExp(DONNEES.prefixe + '(\\d+)-([0-9A-Z]+)-([0-9A-Z]{4})', 'g');
    var m, trouves = [];
    while ((m = re.exec(propre))) trouves.push(m[0]);
    return trouves;
  }

  function decoder(code) {
    var propre = String(code || '').toUpperCase().replace(/\s+/g, '');
    var m = new RegExp('^' + DONNEES.prefixe + '(\\d+)-([0-9A-Z]+)-([0-9A-Z]{4})$').exec(propre);
    if (!m) throw new Error("Ce n'est pas un code de ce contrôle.");
    if (Number(m[1]) !== DONNEES.version) throw new Error('Code d\'une autre version du contrôle (' + m[1] + ').');
    var octets = depuisBase32(m[2]);
    if (controle4(octets) !== m[3]) throw new Error('Code incomplet ou mal recopié (somme de contrôle fausse).');
    var c = JSON.parse(new TextDecoder().decode(octets));
    if (!Array.isArray(c) || c.length < 8 || !Array.isArray(c[7])) throw new Error('Code illisible.');
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

  function echapper(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* Thème clair ou obscur : même réglage que le site (barre du haut). */
  function appliquerTheme() {
    try {
      var m = localStorage.getItem('theme');
      if (m === 'light' || m === 'dark') document.documentElement.setAttribute('data-theme', m);
    } catch (e) { /* stockage indisponible : réglage de l'appareil */ }
  }

  window.CN = {
    DONNEES: DONNEES, svgArbre: svgArbre, texteArbre: texteArbre, lettresSquelette: lettresSquelette,
    enonce: enonce, nombres: nombres, ligneCode: ligneCode,
    encoder: encoder, decoder: decoder, extraireCodes: extraireCodes,
    aleatoire: aleatoire, melanger: melanger, echapper: echapper, appliquerTheme: appliquerTheme
  };
})();
