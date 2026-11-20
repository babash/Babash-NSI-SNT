/* Calendrier des vacances : le moteur des six mini-jeux (associer, erreur, vraifaux,
   sortie, ordre, completer). Tout se corrige dans la page ; la partie est gardée
   sur l'appareil à chaque geste, pour reprendre là où on s'était arrêté.
   Usage : CV.jouer(racine, { exercice, niveau, langage, sauvegarde, titreCase,
                             surSauver(etat), surFin(resultat), surQuitter() }). */
(function () {
  "use strict";
  var CV = window.CV, esc = CV.esc;
  var NOMS_NIVEAUX = ["Facile", "Moyen", "Costaud"];
  CV.NOMS_NIVEAUX = NOMS_NIVEAUX;
  CV.NOMS_TYPES = { associer: "Associer", erreur: "Trouver l'erreur", vraifaux: "Vrai ou faux éclair",
    sortie: "Prévoir la sortie", ordre: "Remettre dans l'ordre", completer: "Compléter" };

  // ce que montre le programme fautif d'une « erreur » : le message réel, sa sortie, ou une boucle sans fin
  CV.console = function (q, langage) {
    var sql = langage === "sql";
    if (q.message != null) return '<div class="console" role="note"><span class="console-titre">' + (sql ? "SQLite répond" : "Python affiche") + ' :</span><pre class="console-erreur">' + CV.esc(q.message) + "</pre></div>";
    if (q.boucle_infinie) return '<div class="console" role="note"><span class="console-titre">Le programme ne s\'arrête jamais :</span><pre>(boucle infinie)</pre></div>';
    if (q.affiche_fautif != null) return '<div class="console" role="note"><span class="console-titre">' + (sql ? "La requête affiche" : "Le programme affiche") + ' :</span><pre>' + (q.affiche_fautif === "" ? (sql ? "(aucune ligne)" : "(rien)") : CV.esc(q.affiche_fautif)) + "</pre></div>";
    return "";
  };
  // un arbre binaire { v, g, d }, dessiné en SVG (lisible à 320 px : 31 nœuds au plus)
  CV.arbre = function (a) {
    if (!a) return "";
    var noeuds = [], aretes = [], rang = 0, prof = 0;
    (function place(n, p) {
      if (!n) return null;
      var g = place(n.g, p + 1), x = rang++, d = place(n.d, p + 1), moi = { v: n.v, x: x, y: p };
      prof = Math.max(prof, p); noeuds.push(moi);
      if (g) aretes.push([moi, g]); if (d) aretes.push([moi, d]);
      return moi;
    })(a, 0);
    var L = 40, H = 52, r = 15, W = rang * L, Ht = (prof + 1) * H;
    var X = function (n) { return n.x * L + L / 2; }, Y = function (n) { return n.y * H + r + 4; };
    return '<svg class="arbre" viewBox="0 0 ' + W + " " + Ht + '" role="img" aria-label="Arbre binaire de ' + noeuds.length + ' nœuds" style="max-width:' + Math.max(W, 120) + 'px">' +
      aretes.map(function (e) { return '<line x1="' + X(e[0]) + '" y1="' + Y(e[0]) + '" x2="' + X(e[1]) + '" y2="' + Y(e[1]) + '"/>'; }).join("") +
      noeuds.map(function (n) { return '<circle cx="' + X(n) + '" cy="' + Y(n) + '" r="' + r + '"/><text x="' + X(n) + '" y="' + (Y(n) + 4) + '">' + CV.esc(n.v) + "</text>"; }).join("") + "</svg>";
  };
  // les tables d'un thème SQL, repliables
  CV.tablesSql = function (tables, ouvert) {
    if (!tables || !tables.length) return "";
    return '<details class="tables"' + (ouvert ? " open" : "") + "><summary>Les tables de la base (" + tables.length + ")</summary>" + tables.map(function (t) {
      return '<div class="defile"><table class="table-sql"><caption>' + CV.esc(t.nom) + "</caption><thead><tr>" + t.colonnes.map(function (c) { return "<th scope=\"col\">" + CV.esc(c) + "</th>"; }).join("") +
        "</tr></thead><tbody>" + t.lignes.map(function (l) { return "<tr>" + l.map(function (v) { return "<td>" + CV.esc(v) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>";
    }).join("") + "</details>";
  };

  CV.jouer = function (racine, o) {
    var ex = o.exercice, items = ex.niveaux[o.niveau - 1].items, type = ex.type;
    CV.langage = o.langage || "python";
    var G = o.sauvegarde && o.sauvegarde.version === 1 ? o.sauvegarde : {
      version: 1, file: items.map(function (_, i) { return i; }), faits: 0, essais: 0, ratees: 0, coups: 0,
      ecoule: 0, aides: 0, fini: false, repasse: false, s: null, msg: "", cls: ""
    };
    var depuis = Date.now();
    if (!G.s) nouvelleQuestion(); else dessiner();

    function sauver() { G.ecoule += Date.now() - depuis; depuis = Date.now(); if (o.surSauver) o.surSauver(JSON.parse(JSON.stringify(G))); }
    function it() { return items[G.file[0]]; }
    function nouvelleQuestion() {
      var q = it();
      G.aides = 0; G.fini = false; G.msg = ""; G.cls = "";
      G.s = { ordre: [], reserve: [], choisis: [], sel: 0, phase: 1, desactives: {}, trouves: {}, g: null, fausse: null, faux: null };
      if (type === "ordre") G.s.reserve = CV.melange(q.lignes.map(function (_, i) { return i; }));
      if (type === "associer") G.s.droite = CV.melange(q.paires.map(function (_, i) { return i; }));
      if (type === "sortie" && q.options) G.s.opts = CV.melange(q.options.map(function (_, i) { return i; }));
      if (type === "erreur") G.s.corr = CV.melange(q.corrections.map(function (_, i) { return i; }));
      if (type === "completer") {
        G.s.choisis = q.trous.map(function () { return null; });
        G.s.jet = q.trous.map(function (t) { return CV.melange(t.options.map(function (_, j) { return j; })); });
      }
      dessiner();
    }
    function dessiner() {
      var q = it(), total = items.length, pts = "";
      for (var i = 0; i < total; i++) pts += '<i class="' + (i < G.faits ? "fait" : i === G.faits ? "cour" : "") + '"></i>';
      var aides = q.aides || [];
      racine.innerHTML = '<div class="jeu-haut"><button class="btn" data-j="quitter">&#8592; Calendrier</button><span class="ou">' + esc(o.titreCase || "") + " · " + CV.etoiles(o.niveau, 3) + "</span></div>" +
        '<h1 tabindex="-1">' + esc(ex.titre) + '</h1><p class="objectif">Objectif : ' + esc(ex.objectif) + "</p>" +
        '<div class="points" role="img" aria-label="Question ' + Math.min(G.faits + 1, total) + " sur " + total + '">' + pts + "</div>" +
        CV.tablesSql(o.tables) + (q.arbre ? CV.arbre(q.arbre) : "") +
        '<div id="zone">' + zone(q) + "</div>" +
        '<div class="message retour-jeu ' + (G.cls || "") + '" role="status" aria-live="polite">' + (G.msg || "") + "</div>" +
        aides.slice(0, G.aides).map(function (a) { return '<div class="aide">Coup de pouce : ' + esc(a) + "</div>"; }).join("") +
        '<div class="actions">' + (aides.length && !G.fini ? '<button class="btn" data-j="aide"' + (G.aides >= aides.length ? " disabled" : "") + ">Coup de pouce (" + G.aides + "/" + aides.length + ")</button>" : "") +
        bouton(q) + "</div>";
    }
    function bouton(q) {
      if (G.fini) return '<button class="btn plein" data-j="suivant">' + (G.file.length > 1 ? "Question suivante" : "Terminer") + "</button>";
      if (type === "ordre") return '<button class="btn plein" data-j="verifier"' + (G.s.reserve.length ? " disabled" : "") + ">Vérifier</button>";
      if (type === "completer") return '<button class="btn plein" data-j="verifier"' + (G.s.choisis.indexOf(null) >= 0 ? " disabled" : "") + ">Vérifier</button>";
      if (type === "sortie" && !q.options) return '<button class="btn plein" data-j="verifier">Vérifier</button>';
      return "";
    }
    function affichage(t) { return '<div class="affiche">' + esc(t) + "</div>"; }
    function zone(q) {
      var s = G.s, f = G.fini;
      if (type === "vraifaux") {
        return '<p class="consigne">Vrai ou faux ?</p>' + (q.code ? CV.blocCode(q.code.split("\n")) : "") + '<p class="affirmation">' + esc(q.texte) + "</p>" +
          '<div class="choix deux"><button class="option vf" data-j="vf" data-v="1"' + (f ? " disabled" : "") + '>Vrai</button><button class="option vf" data-j="vf" data-v="0"' + (f ? " disabled" : "") + ">Faux</button></div>";
      }
      if (type === "sortie") {
        var h = '<p class="consigne">Qu\'affiche ce programme ?</p>' + CV.blocCode(q.code.split("\n"));
        if (!q.options) return h + '<label for="rep">Ta réponse</label><input type="text" id="rep" autocomplete="off" autocapitalize="off" spellcheck="false" value="' + esc(s.rep || "") + '"' + (f ? " disabled" : "") + ">";
        return h + '<div class="choix">' + s.opts.map(function (k) {
          var cls = f && k === q.bonne ? " ok" : s.desactives[k] ? " ko" : "";
          return '<button class="option' + cls + '" data-j="opt" data-k="' + k + '"' + (f || s.desactives[k] ? " disabled" : "") + "><pre>" + esc(q.options[k].split(" / ").join("\n")) + "</pre></button>";
        }).join("") + "</div>";
      }
      if (type === "associer") {
        var gauche = q.paires.map(function (p, i) {
          var ok = s.trouves[i];
          return '<button class="option' + (ok ? " ok" : s.g === i ? " sel" : "") + '" data-j="ag" data-i="' + i + '"' + (ok ? " disabled" : "") + "><pre>" + (q.executer ? CV.colorer(p[0]) : esc(p[0])) + "</pre></button>";
        }).join("");
        var droite = s.droite.map(function (i) {
          var ok = s.trouves[i];
          return '<button class="option' + (ok ? " ok" : "") + '" data-j="ad" data-i="' + i + '"' + (ok ? " disabled" : "") + "><pre>" + esc(q.paires[i][1]) + "</pre></button>";
        }).join("");
        return '<p class="consigne">' + esc(q.consigne) + ' Touche un élément à gauche, puis celui qui va avec.</p><div class="colonnes"><div><h3>' +
          (q.executer ? "Le programme" : "À gauche") + '</h3><div class="choix">' + gauche + "</div></div><div><h3>" + (q.executer ? "Ce qu'il affiche" : "À droite") +
          '</h3><div class="choix">' + droite + "</div></div></div>";
      }
      if (type === "erreur") {
        var classes = {}; if (s.phase === 2 || f) classes[q.ligne] = f ? "ok" : "choisie";
        if (s.fausse != null) classes[s.fausse] = "ko";
        var lignes = q.lignes.slice(); if (f) lignes[q.ligne] = q.corrections[q.bonne];
        var hh = '<p class="consigne">But : ' + esc(q.but) + "</p><p>" + (s.phase === 1 ? "Touche la ligne qui contient l'erreur." : f ? "Programme corrigé :" : "Choisis la bonne correction de la ligne " + (q.ligne + 1) + ".") + "</p>" +
          CV.blocCode(lignes, { touchable: s.phase === 1 && !f, classes: classes }) + (f ? "" : CV.console(q, CV.langage));
        if (s.phase === 2 && !f) hh += '<div class="choix">' + s.corr.map(function (k) {
          return '<button class="option' + (s.desactives[k] ? " ko" : "") + '" data-j="corr" data-k="' + k + '"' + (s.desactives[k] ? " disabled" : "") + "><pre>" + CV.ligneCode(q.corrections[k]) + "</pre></button>";
        }).join("") + "</div>";
        if (f) hh += '<p class="doux">Il affiche :</p>' + affichage(q.affiche);
        return hh;
      }
      if (type === "ordre") {
        var place = s.ordre.map(function (k, i) { return '<button class="piece" data-j="retirer" data-i="' + i + '"' + (f ? " disabled" : "") + ">" + CV.ligneCode(q.lignes[k]) + "</button>"; }).join("");
        var res = s.reserve.map(function (k, i) { return '<button class="piece" data-j="placer" data-i="' + i + '">' + CV.ligneCode(q.lignes[k]) + "</button>"; }).join("");
        return '<p class="consigne">But : ' + esc(q.but) + '</p><p class="doux">Touche les lignes dans l\'ordre. Touche une ligne placée pour la retirer.</p>' +
          '<h3 class="sous">Mon programme</h3><div class="zone-ordre">' + (place || '<span class="doux">Vide pour l\'instant.</span>') + "</div>" +
          (res ? '<h3 class="sous">Les lignes</h3><div class="choix">' + res + "</div>" : "") +
          (f ? '<p class="doux">Il affiche :</p>' + affichage(q.affiche) : "");
      }
      if (type === "completer") {
        var lc = q.lignes.map(function (l, i) {
          var html = l.split(/(\{\d+\})/).map(function (morceau, m) {
            var t = /^\{(\d+)\}$/.exec(morceau);
            if (!t) return m === 0 ? CV.ligneCode(morceau) : CV.colorer(morceau);
            var d = +t[1], v = s.choisis[d], cls = f ? " ok" : s.faux && s.faux[d] ? " ko" : s.sel === d ? " sel" : "";
            return '<button class="trou' + cls + '" data-j="trou" data-d="' + d + '" aria-label="Trou ' + (d + 1) + '"' + (f ? " disabled" : "") + ">" + (v == null ? "&nbsp;?&nbsp;" : esc(q.trous[d].options[v])) + "</button>";
          }).join("");
          return '<div class="ligne"><span class="num">' + (i + 1) + "</span><span>" + html + "</span></div>";
        }).join("");
        var tr = q.trous[s.sel];
        return '<p class="consigne">But : ' + esc(q.but) + '</p><div class="code">' + lc + "</div>" +
          (f ? '<p class="doux">Il affiche :</p>' + affichage(q.affiche) :
            '<p class="doux">Pièces pour le trou ' + (s.sel + 1) + ' :</p><div class="jetons">' + (s.jet ? s.jet[s.sel] : tr.options.map(function (_, j) { return j; })).map(function (j) {
              return '<button class="jeton" data-j="jeton" data-k="' + j + '">' + esc(tr.options[j]) + "</button>";
            }).join("") + "</div>");
      }
      return '<div class="message ko">Type de mini-jeu inconnu : ' + esc(type) + "</div>";
    }
    function juste(msg) { G.fini = true; G.essais++; G.msg = "Juste. " + esc(msg || ""); G.cls = "ok"; dessiner(); sauver(); }
    function rate(msg) {
      G.essais++; G.ratees++; G.msg = msg; G.cls = "ko"; dessiner(); sauver();
      var z = racine.querySelector("#zone"); if (z) z.classList.add("secoue");
    }
    function info(msg) { G.msg = msg; G.cls = "info"; dessiner(); }

    function action(a, el) {
      var q = it(), s = G.s;
      if (a === "quitter") { sauver(); return o.surQuitter && o.surQuitter(); }
      if (a === "aide") { G.aides++; G.coups++; dessiner(); return sauver(); }
      if (a === "suivant") {
        G.file.shift();
        if (!G.repasse) G.faits++;
        G.repasse = false;
        if (!G.file.length) return terminer();
        nouvelleQuestion(); return sauver();
      }
      if (G.fini) return;
      if (a === "vf") {
        if ((el.getAttribute("data-v") === "1") === q.reponse) return juste(q.explication);
        G.file.push(G.file[0]); G.fini = true; G.essais++; G.ratees++; G.repasse = true;
        G.msg = "Pas tout à fait. " + esc(q.explication) + " Cette question reviendra à la fin."; G.cls = "ko"; dessiner(); return sauver();
      }
      if (a === "opt") {
        var k = +el.getAttribute("data-k");
        if (k === q.bonne) return juste(String(q.retours[k]).replace(/^Juste[ .:]*/, ""));
        s.desactives[k] = true; return rate(esc(q.retours[k]) + " Essaie encore.");
      }
      if (a === "ag") { s.g = +el.getAttribute("data-i"); G.msg = ""; return dessiner(); }
      if (a === "ad") {
        var d = +el.getAttribute("data-i");
        if (s.g == null) return info("Touche d'abord un élément de la colonne de gauche.");
        if (d === s.g) {
          s.trouves[d] = true; s.g = null;
          if (Object.keys(s.trouves).length === q.paires.length) return juste(q.explication);
          G.essais++; G.msg = "Bien vu."; G.cls = "ok"; dessiner(); return sauver();
        }
        s.g = null; return rate("Ces deux-là ne vont pas ensemble. Essaie encore.");
      }
      if (a === "ligne") {
        var l = +el.getAttribute("data-i");
        if (l === q.ligne) { s.phase = 2; s.fausse = null; G.essais++; G.msg = "Oui, l'erreur est à la ligne " + (l + 1) + ". Comment la corriger ?"; G.cls = "ok"; dessiner(); return sauver(); }
        s.fausse = l; return rate("La ligne " + (l + 1) + " est correcte. Relis le but : " + esc(q.but));
      }
      if (a === "corr") {
        var c = +el.getAttribute("data-k");
        if (c === q.bonne) return juste(q.explication);
        s.desactives[c] = true; return rate("Avec cette correction, le programme ne fait pas ce qui est demandé. Essaie encore.");
      }
      if (a === "placer") { s.ordre.push(s.reserve.splice(+el.getAttribute("data-i"), 1)[0]); G.msg = ""; dessiner(); return sauver(); }
      if (a === "retirer") { s.reserve.push(s.ordre.splice(+el.getAttribute("data-i"), 1)[0]); G.msg = ""; dessiner(); return sauver(); }
      if (a === "trou") { s.sel = +el.getAttribute("data-d"); return dessiner(); }
      if (a === "jeton") {
        s.choisis[s.sel] = +el.getAttribute("data-k"); if (s.faux) s.faux[s.sel] = false;
        var suivant = s.choisis.indexOf(null); if (suivant >= 0) s.sel = suivant;
        G.msg = ""; dessiner(); return sauver();
      }
      if (a === "verifier") {
        if (type === "ordre") {
          var bien = s.ordre.filter(function (k2, i) { return k2 === i; }).length;
          if (bien === q.lignes.length) return juste("Ton programme est dans le bon ordre.");
          return rate("Pas encore : " + bien + " ligne" + (bien > 1 ? "s" : "") + " sur " + q.lignes.length + " " + (bien > 1 ? "sont" : "est") + " à leur place. Touche une ligne pour la retirer.");
        }
        if (type === "completer") {
          s.faux = s.choisis.map(function (v, i) { return v !== q.trous[i].bonne; });
          var nf = s.faux.filter(Boolean).length;
          if (!nf) return juste(q.explication);
          s.sel = s.faux.indexOf(true);
          return rate(nf === 1 ? "Le trou " + (s.sel + 1) + " ne va pas. Essaie une autre pièce." : nf + " trous ne vont pas. Commence par le trou " + (s.sel + 1) + ".");
        }
        if (type === "sortie") {
          var champ = racine.querySelector("#rep"), rep = (champ && champ.value || "").trim();
          s.rep = rep;
          if (!rep) return info("Écris ta réponse avant de vérifier.");
          if (rep.replace(/\s+/g, " ") === String(q.reponse).trim()) return juste(q.explication);
          return rate("Ce n'est pas " + esc(rep) + ". Refais la trace, ligne par ligne : note la valeur de chaque variable.");
        }
      }
    }
    function terminer() {
      G.ecoule += Date.now() - depuis;
      var r = { niveau: o.niveau, reussi: true, etoiles: o.niveau, essais: Math.min(G.essais, 500), coups: Math.min(G.coups, 100),
                duree: Math.min(Math.round(G.ecoule / 1000), 86400), ratees: G.ratees };
      racine.removeEventListener("click", clic); racine.removeEventListener("keydown", touche);
      o.surFin(r);
    }
    function clic(ev) { var el = ev.target.closest("[data-j]"); if (el && racine.contains(el)) action(el.getAttribute("data-j"), el); }
    function touche(ev) { if (ev.key === "Enter" && ev.target.id === "rep") { ev.preventDefault(); action("verifier"); } }
    racine.addEventListener("click", clic);
    racine.addEventListener("keydown", touche);
    // pour les essais automatiques (Playwright) : l'état de la question en cours, en lecture
    racine.cvEtat = function () { return { type: type, item: it(), s: G.s, fini: G.fini }; };
    var h = racine.querySelector("h1"); if (h) h.focus({ preventScroll: true });
    return { arreter: function () { sauver(); racine.removeEventListener("click", clic); racine.removeEventListener("keydown", touche); } };
  };

  // le corrigé d'un exercice (tous niveaux), montré à J + 3
  CV.corrige = function (ex, langage, tables) {
    CV.langage = langage || "python";
    return CV.tablesSql(tables) + ex.niveaux.map(function (nv, i) {
      return '<section class="carte"><h2>' + CV.etoiles(i + 1, 3) + " " + NOMS_NIVEAUX[i] + "</h2>" + nv.items.map(function (q) {
        return '<div class="corrige-item">' + (q.arbre ? CV.arbre(q.arbre) : "") + corrigeItem(ex.type, q) + "</div>";
      }).join("") + "</section>";
    }).join("");
  };
  function corrigeItem(t, q) {
    var esc2 = CV.esc;
    if (t === "vraifaux") return (q.code ? CV.blocCode(q.code.split("\n")) : "") + "<p>" + esc2(q.texte) + ' <span class="' + (q.reponse ? 'vrai">Vrai' : 'faux">Faux') + '</span></p><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "sortie") return CV.blocCode(q.code.split("\n")) + '<p class="doux">Affiche :</p><div class="affiche">' + esc2(q.options ? q.options[q.bonne].split(" / ").join("\n") : q.reponse) + '</div><p class="doux">' + esc2(q.options ? q.retours[q.bonne] : q.explication) + "</p>";
    if (t === "associer") return "<p>" + esc2(q.consigne) + '</p><table class="paires">' + q.paires.map(function (p) { return "<tr><td><code class=\"mono\">" + (q.executer ? CV.colorer(p[0]) : esc2(p[0])) + "</code></td><td>" + esc2(p[1]) + "</td></tr>"; }).join("") + '</table><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "erreur") {
      var l2 = q.lignes.slice(); l2[q.ligne] = q.corrections[q.bonne]; var c1 = {}, c2 = {}; c1[q.ligne] = "ko"; c2[q.ligne] = "ok";
      return "<p><b>But :</b> " + esc2(q.but) + '</p><p class="doux">Avec l\'erreur :</p>' + CV.blocCode(q.lignes, { classes: c1 }) + CV.console(q, CV.langage) + '<p class="doux">Corrigé :</p>' + CV.blocCode(l2, { classes: c2 }) + '<p class="doux">' + esc2(q.explication) + "</p>";
    }
    if (t === "ordre") return "<p><b>But :</b> " + esc2(q.but) + "</p>" + CV.blocCode(q.lignes) + '<p class="doux">Affiche :</p><div class="affiche">' + esc2(q.affiche) + "</div>";
    if (t === "completer") {
      var lc = q.lignes.map(function (x) { return x.replace(/\{(\d+)\}/g, function (_, d) { return q.trous[+d].options[q.trous[+d].bonne]; }); });
      return "<p><b>But :</b> " + esc2(q.but) + "</p>" + CV.blocCode(lc) + '<p class="doux">' + esc2(q.explication) + "</p>";
    }
    return "";
  }
})();
