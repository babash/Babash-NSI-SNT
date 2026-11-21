/* Calendrier des vacances : outils communs à la page élève et à la page enseignant·e.
   Appels à la base (fonctions cv_…), dates de Mayotte, lecture tolérante des codes,
   affichage du code Python ou SQL, stockage sur l'appareil (jamais indispensable). */
(function () {
  "use strict";
  var CV = window.CV = window.CV || {};
  var C = window.CV_CONFIG || {};

  // ------------------------------------------------------------ l'adresse de la base
  // Sur un poste de développement (localhost), ?api=http://127.0.0.1:port remplace la base :
  // c'est ainsi qu'on essaie les pages sur une copie locale. Jamais ailleurs.
  var api = C.SUPABASE_URL, enLigne = !!C.EN_LIGNE;
  try {
    var q = new URLSearchParams(location.search).get("api");
    if (q && /^(localhost|127\.0\.0\.1)$/.test(location.hostname) && /^http:\/\/(localhost|127\.0\.0\.1):\d+$/.test(q)) { api = q; enLigne = true; }
  } catch (e) { /* rien */ }
  CV.enLigne = enLigne;

  // ------------------------------------------------------------ appeler une fonction cv_…
  // Renvoie toujours un objet { ok, … } : une panne de réseau donne { ok: false, reseau: true, message }.
  CV.rpc = function (nom, args) {
    if (!enLigne) return Promise.resolve({ ok: false, horsService: true, message: "Le calendrier n'est pas encore en service." });
    return fetch(api + "/rest/v1/rpc/" + nom, {
      method: "POST",
      headers: { "apikey": C.SUPABASE_KEY, "Content-Type": "application/json" },
      body: JSON.stringify(args || {})
    }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) return { ok: false, message: "La base a refusé la demande (" + r.status + "). Réessayer dans un moment." };
        return j && typeof j === "object" ? j : { ok: false, message: "Réponse illisible." };
      }, function () { return { ok: false, message: "Réponse illisible (" + r.status + ")." }; });
    }, function () {
      return { ok: false, reseau: true, message: "Pas de réseau pour l'instant. Réessayer dans un moment." };
    });
  };

  // ------------------------------------------------------------ stockage sur l'appareil
  CV.lire = function (cle, defaut) {
    try { var v = localStorage.getItem("cv:" + cle); return v == null ? defaut : JSON.parse(v); } catch (e) { return defaut; }
  };
  CV.ecrire = function (cle, val) {
    try { if (val == null) localStorage.removeItem("cv:" + cle); else localStorage.setItem("cv:" + cle, JSON.stringify(val)); } catch (e) { /* navigation privée */ }
  };

  // ------------------------------------------------------------ dates (AAAA-MM-JJ, jours de Mayotte)
  function versDate(s) { var p = s.split("-"); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])); }
  CV.versDate = versDate;
  CV.ajouter = function (s, n) { var d = versDate(s); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
  CV.ecart = function (a, b) { return Math.round((versDate(b) - versDate(a)) / 86400000); };
  CV.aujourdhuiMayotte = function () {
    return new Date(Date.now() + 3 * 3600000).toISOString().slice(0, 10);  // UTC+3, sans heure d'été
  };
  var FJ = new Intl.DateTimeFormat("fr-FR", { weekday: "short", timeZone: "UTC" });
  var FD = new Intl.DateTimeFormat("fr-FR", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" });
  var FC = new Intl.DateTimeFormat("fr-FR", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });
  CV.jourCourt = function (s) { return FJ.format(versDate(s)).replace(".", ""); };
  CV.dateLongue = function (s) { return FD.format(versDate(s)); };
  CV.dateCourte = function (s) { return FC.format(versDate(s)); };

  // ------------------------------------------------------------ texte et code
  CV.esc = function (t) { return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var PLEINE = String.fromCharCode(0x2605), VIDE = String.fromCharCode(0x2606);
  CV.etoiles = function (n, max) {
    var t = ""; for (var i = 0; i < (max || n); i++) t += i < n ? PLEINE : VIDE;
    return '<span class="etoiles" aria-label="' + n + " étoile" + (n > 1 ? "s" : "") + '">' + t + "</span>";
  };
  var MC_PY = /^(for|in|while|if|elif|else|def|return|and|or|not|True|False|None|pass|break|continue|is|lambda|class|import|from)$/;
  var FN_PY = /^(print|range|len|input|int|str|float|bool|round|list|dict|type|abs|min|max|sum)$/;
  var MC_SQL = /^(SELECT|FROM|WHERE|AND|OR|NOT|ORDER|BY|ASC|DESC|JOIN|ON|INNER|LEFT|AS|GROUP|HAVING|COUNT|SUM|AVG|MIN|MAX|DISTINCT|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|PRIMARY|KEY|FOREIGN|REFERENCES|NULL|IS|LIKE|IN|LIMIT|INTEGER|TEXT|REAL)$/;
  CV.langage = "python";
  CV.colorer = function (texte, langage) {
    var sql = (langage || CV.langage) === "sql";
    var re = /("[^"]*"|'[^']*')|(#.*$|--.*$)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)/g, out = "", i = 0, m;
    while ((m = re.exec(texte))) {
      out += CV.esc(texte.slice(i, m.index));
      if (m[1]) out += '<span class="str">' + CV.esc(m[1]) + "</span>";
      else if (m[2] && (sql ? m[2][0] === "-" : m[2][0] === "#")) out += '<span class="com">' + CV.esc(m[2]) + "</span>";
      else if (m[2]) out += CV.esc(m[2]);
      else if (m[3]) out += '<span class="nb">' + m[3] + "</span>";
      else if (sql ? MC_SQL.test(m[4].toUpperCase()) && m[4] === m[4].toUpperCase() : MC_PY.test(m[4])) out += '<span class="kw">' + m[4] + "</span>";
      // une fonction : souligner les fonctions connues, celles qu'on appelle (nom suivi de « ( ») et celles qu'on définit
      else if (!sql && (FN_PY.test(m[4]) || /^\s*\(/.test(texte.slice(re.lastIndex)) || /\bdef\s+$/.test(texte.slice(0, m.index)))) out += '<span class="fn">' + m[4] + "</span>";
      else out += CV.esc(m[4]);
      i = re.lastIndex;
    }
    return out + CV.esc(texte.slice(i));
  };
  // une ligne de code, avec un guide par niveau d'indentation (4 espaces)
  CV.ligneCode = function (texte) {
    var m = /^( *)/.exec(texte)[1].length, g = "";
    for (var k = 0; k < Math.floor(m / 4); k++) g += '<span class="guide"></span>';
    return g + CV.colorer(texte.slice(Math.floor(m / 4) * 4));
  };
  CV.blocCode = function (lignes, o) {
    o = o || {};
    return '<div class="code' + (o.touchable ? " touchable" : "") + '">' + lignes.map(function (l, i) {
      var cls = o.classes && o.classes[i] ? " " + o.classes[i] : "";
      var debut = o.touchable ? '<button type="button" data-j="ligne" data-i="' + i + '" class="ligne' + cls + '" aria-label="Ligne ' + (i + 1) + '">' : '<div class="ligne' + cls + '">';
      return debut + '<span class="num">' + (i + 1) + "</span><span>" + CV.ligneCode(l) + "</span>" + (o.touchable ? "</button>" : "</div>");
    }).join("") + "</div>";
  };
  CV.melange = function (t) { var a = t.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var x = a[i]; a[i] = a[j]; a[j] = x; } return a; };

  // ------------------------------------------------------------ les codes (spécification T39, § 1.2)
  CV.MOTS = ("DOMINO PUZZLE DAMIER TOUPIE MARELLE YOYO ECHECS CARTE JOKER ATOUT QUILLE BALLON RAQUETTE FILET FRISBEE CERCEAU " +
    "SCORE BONUS COMBO QUETE TRESOR ENIGME REBUS CHARADE SUDOKU MEMORY BINGO KARTING MIKADO TANGRAM CARROM TOBOGGAN " +
    "HAMAC PARASOL SORBET DIABOLO DEDALE PION ARCADE AVATAR FINALE MATCH SPRINT ORIGAMI CUBE TOTEM DEFI JONGLAGE " +
    "BOWLING TENNIS JUDO FANION PLONGEON SURF RUGBY BASKET FLIPPER BILLARD SLALOM GOLF TAQUIN RALLYE HOCKEY SQUASH").split(" ");
  var ACCENTS = new RegExp("[" + String.fromCharCode(0x300) + "-" + String.fromCharCode(0x36f) + "]", "g");
  function distance(a, b) {
    var p = [], i, j; for (j = 0; j <= b.length; j++) p[j] = j;
    for (i = 1; i <= a.length; i++) { var c = [i]; for (j = 1; j <= b.length; j++) c[j] = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (a[i - 1] !== b[j - 1] ? 1 : 0)); p = c; }
    return p[b.length];
  }
  function proche(m) { return CV.MOTS.slice().sort(function (a, b) { return distance(m, a) - distance(m, b); })[0]; }
  // nbMots : 2 (élève) ou 3 (enseignant·e) ; nbChiffres : 3 ou 4. Renvoie { code } ou { erreur }.
  CV.lireCode = function (texte, nbMots) {
    var t = String(texte || "").normalize("NFD").replace(ACCENTS, "").toUpperCase().replace(/Œ/g, "OE").replace(/[^A-Z0-9]+/g, " ").trim();
    var m = /^(.*?)[ ]?([0-9OIL]{3,4})$/.exec(t);
    var exemple = nbMots === 3 ? "PION-SURF-BINGO-2741" : "DOMINO-JOKER-482";
    if (!m) return { erreur: "Un code a " + nbMots + " mots puis des chiffres, comme " + exemple + "." };
    var chiffres = m[2].replace(/O/g, "0").replace(/[IL]/g, "1");
    var lettres = m[1].replace(/0/g, "O").replace(/1/g, "I");
    var parts = lettres.split(" ").filter(Boolean);
    for (var i = 0; i < parts.length; i++) {
      if (CV.MOTS.indexOf(parts[i]) < 0 && !decoupe(parts[i], 1)) {
        if (parts.length >= nbMots || parts[i].length <= 8) return { erreur: parts[i] + " n'est pas dans la liste : voulais-tu dire " + proche(parts[i]) + " ?" };
      }
    }
    var mots = decoupe(parts.join(""), nbMots);
    if (!mots) {
      var autre = decoupe(parts.join(""), nbMots === 2 ? 3 : 2);
      if (autre) return { erreur: nbMots === 2 ? "C'est un code d'enseignant·e (3 mots) : la page des élèves demande ton code à 2 mots." : "C'est un code d'élève (2 mots) : l'espace enseignant·e demande un code à 3 mots." };
      return { erreur: "Un code a " + nbMots + " mots puis des chiffres, comme " + exemple + "." };
    }
    return { code: mots.join("-") + "-" + chiffres };
  };
  function decoupe(s, n) {
    if (n === 0) return s === "" ? [] : null;
    for (var i = 0; i < CV.MOTS.length; i++) {
      if (s.indexOf(CV.MOTS[i]) === 0) { var r = decoupe(s.slice(CV.MOTS[i].length), n - 1); if (r) return [CV.MOTS[i]].concat(r); }
    }
    return null;
  }

  // ------------------------------------------------------------ banques d'exercices (fichiers du dépôt)
  var banques = {};
  CV.catalogue = function () {
    if (banques._catalogue) return banques._catalogue;
    return (banques._catalogue = fetch("exercices/catalogue.json").then(function (r) {
      if (!r.ok) throw new Error("catalogue " + r.status);
      return r.json();
    }));
  };
  CV.banque = function (id) {
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(id)) return Promise.reject(new Error("thème illisible"));
    if (banques[id]) return banques[id];
    return (banques[id] = fetch("exercices/" + id + ".json").then(function (r) {
      if (!r.ok) { delete banques[id]; throw new Error("banque " + id + " : " + r.status); }
      return r.json();
    }, function (e) { delete banques[id]; throw e; }));
  };
  CV.themeDe = function (b) { return (b && (b.theme || b.chapitre)) || {}; };

  // ------------------------------------------------------------ affichage clair ou obscur
  var th = CV.lire("theme", null); if (th) document.documentElement.setAttribute("data-theme", th);
  CV.basculerTheme = function () {
    var r = document.documentElement, a = r.getAttribute("data-theme");
    var sombre = a ? a === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    r.setAttribute("data-theme", sombre ? "light" : "dark"); CV.ecrire("theme", sombre ? "light" : "dark");
  };
  CV.ICONE_THEME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  CV.ICONE_COMPTE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>';
  CV.pied = function () {
    return '<footer class="pied">Babash - NSI Tani Malandi · exercices CC BY-SA 4.0, code MIT · <a href="' + CV.esc(C.DEPOT || "#") + '">Code source sur GitHub</a></footer>';
  };
  CV.horsService = function () {
    return '<div class="message info" role="status">Le calendrier n\'est pas encore en service. Il ouvrira bientôt, à la même adresse.</div>';
  };
})();
