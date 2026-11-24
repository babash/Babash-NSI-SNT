/* Calendrier des vacances : le moteur des douze mini-jeux (associer, erreur, vraifaux,
   sortie, ordre, completer, trace, combien, paniers, intrus, memo, bits ; spécification,
   § 5.2). Tout se corrige dans la page ; la partie est gardée sur l'appareil à chaque
   geste, pour reprendre là où on s'était arrêté. Tout se joue au doigt à 320 px et au
   clavier (des boutons, jamais de glisser-déposer obligatoire), les retours sont annoncés
   (aria-live), aucun chrono ne fait perdre, et l'animation « secoue » se coupe avec
   prefers-reduced-motion (calendrier.css).
   Usage : CV.jouer(racine, { exercice, niveau, langage, sauvegarde, titreCase,
                             surSauver(etat), surFin(resultat), surQuitter() }). */
(function () {
  "use strict";
  var CV = window.CV, esc = CV.esc;
  var NOMS_NIVEAUX = ["Facile", "Moyen", "Costaud"];
  CV.NOMS_NIVEAUX = NOMS_NIVEAUX;
  CV.NOMS_TYPES = { associer: "Associer", erreur: "Trouver l'erreur", vraifaux: "Vrai ou faux éclair",
    sortie: "Prévoir la sortie", ordre: "Remettre dans l'ordre", completer: "Compléter",
    trace: "Tableau de trace", combien: "Combien ?", paniers: "Deux paniers", intrus: "L'intrus",
    memo: "Mémo des paires", bits: "Allume les bits" };
  // une valeur tapée dans un tableau de trace : espaces et guillemets autour ignorés
  CV.normTrace = function (v) { return String(v == null ? "" : v).trim().replace(/\s+/g, " ").replace(/^(["'])(.*)\1$/, "$2"); };
  // les bits d'une case « bits » (chaîne de 0 et de 1) en nombre
  CV.valeurBits = function (b) { var v = 0; for (var i = 0; i < b.length; i++) v = v * 2 + (b[i] === "1" ? 1 : 0); return v; };

  // les libellés : un thème sans programme (langage « aucun » : HTML, réseau, histoire du Web…) n'en parle pas
  CV.libelle = function (cle, langage) {
    var aucun = (langage || CV.langage) === "aucun";
    return ({ question: aucun ? "Que montre le navigateur ?" : "Qu'affiche ce programme ?",
      corrige: aucun ? "Version corrigée :" : "Programme corrigé :",
      resultat: aucun ? "Résultat :" : "Il affiche :",
      affiche: aucun ? "Résultat :" : "Affiche :",
      mien: aucun ? "Mon ordre" : "Mon programme",
      gauche: aucun ? "À gauche" : "Le programme",
      droite: aucun ? "À droite" : "Ce qu'il affiche" })[cle];
  };
  // ce que montre le programme fautif d'une « erreur » : le message réel, sa sortie, ou une boucle sans fin
  CV.console = function (q, langage) {
    var sql = langage === "sql", aucun = langage === "aucun";
    if (q.message != null) return '<div class="console" role="note"><span class="console-titre">' + (q.etiquette || (sql ? "SQLite répond" : aucun ? "Message" : "Python affiche")) + ' :</span><pre class="console-erreur">' + CV.esc(q.message) + "</pre></div>";
    if (q.boucle_infinie) return '<div class="console" role="note"><span class="console-titre">Le programme ne s\'arrête jamais :</span><pre>(boucle infinie)</pre></div>';
    if (q.affiche_fautif != null) return '<div class="console" role="note"><span class="console-titre">' + (q.etiquette || (sql ? "La requête affiche" : aucun ? "Ce qui se passe" : "Le programme affiche")) + ' :</span><pre>' + (q.affiche_fautif === "" ? (sql ? "(aucune ligne)" : "(rien)") : CV.esc(q.affiche_fautif)) + "</pre></div>";
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
      if (type === "trace") G.s.vals = {};
      if (type === "combien") G.s.n = q.depart != null ? q.depart : (q.min || 0);
      if (type === "paniers") { G.s.ordre = CV.melange(q.cartes.map(function (_, i) { return i; })); G.s.places = {}; }
      if (type === "intrus") { G.s.elems = CV.melange(q.elements.map(function (_, i) { return i; })); G.s.opts = CV.melange(q.pourquoi.options.map(function (_, i) { return i; })); }
      if (type === "memo") {
        var cartes = []; q.paires.forEach(function (_, i) { cartes.push([i, 0], [i, 1]); });
        G.s.cartes = CV.melange(cartes); G.s.ouvertes = []; G.s.coups = 0;
      }
      if (type === "bits") G.s.bits = new Array(q.reponse.length + 1).join("0");
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
      if (type === "trace" || type === "combien" || type === "bits") return '<button class="btn plein" data-j="verifier">Vérifier</button>';
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
        var h = '<p class="consigne">' + esc(q.consigne || CV.libelle("question")) + "</p>" + CV.blocCode(q.code.split("\n"));
        if (!q.options) return h + '<label for="rep">Ta réponse</label><input type="text" id="rep" autocomplete="off" autocapitalize="off" spellcheck="false" value="' + esc(s.rep || "") + '"' + (f ? " disabled" : "") + ">";
        return h + '<div class="choix">' + s.opts.map(function (k) {
          var cls = f && k === q.bonne ? " ok" : s.desactives[k] ? " ko" : "";
          return '<button class="option' + cls + '" data-j="opt" data-k="' + k + '"' + (f || s.desactives[k] ? " disabled" : "") + "><pre>" + esc(q.options[k].split(" / ").join("\n")) + "</pre></button>";
        }).join("") + "</div>";
      }
      if (type === "associer") {
        var gauche = q.paires.map(function (p, i) {
          var ok = s.trouves[i];
          return '<button class="option' + (ok ? " ok" : s.g === i ? " sel" : "") + '" data-j="ag" data-i="' + i + '"' + (ok ? " disabled" : "") + "><pre>" + (q.executer || q.code_gauche ? CV.blocLignes(p[0]) : esc(p[0])) + "</pre></button>";
        }).join("");
        var droite = s.droite.map(function (i) {
          var ok = s.trouves[i];
          return '<button class="option' + (ok ? " ok" : "") + '" data-j="ad" data-i="' + i + '"' + (ok ? " disabled" : "") + "><pre>" + esc(q.paires[i][1]) + "</pre></button>";
        }).join("");
        return '<p class="consigne">' + esc(q.consigne) + ' Touche un élément à gauche, puis celui qui va avec.</p><div class="colonnes"><div><h3>' +
          (q.executer ? CV.libelle("gauche") : "À gauche") + '</h3><div class="choix">' + gauche + "</div></div><div><h3>" + (q.executer ? CV.libelle("droite") : "À droite") +
          '</h3><div class="choix">' + droite + "</div></div></div>";
      }
      if (type === "erreur") {
        var classes = {}; if (s.phase === 2 || f) classes[q.ligne] = f ? "ok" : "choisie";
        if (s.fausse != null) classes[s.fausse] = "ko";
        var lignes = q.lignes.slice(); if (f) lignes[q.ligne] = q.corrections[q.bonne];
        var hh = '<p class="consigne">But : ' + esc(q.but) + "</p><p>" + (s.phase === 1 ? "Touche la ligne qui contient l'erreur." : f ? CV.libelle("corrige") : "Choisis la bonne correction de la ligne " + (q.ligne + 1) + ".") + "</p>" +
          CV.blocCode(lignes, { touchable: s.phase === 1 && !f, classes: classes }) + (f ? "" : CV.console(q, CV.langage));
        if (s.phase === 2 && !f) hh += '<div class="choix">' + s.corr.map(function (k) {
          return '<button class="option' + (s.desactives[k] ? " ko" : "") + '" data-j="corr" data-k="' + k + '"' + (s.desactives[k] ? " disabled" : "") + "><pre>" + CV.ligneCode(q.corrections[k]) + "</pre></button>";
        }).join("") + "</div>";
        if (f) hh += '<p class="doux">' + CV.libelle("resultat") + '</p>' + affichage(q.affiche);
        return hh;
      }
      if (type === "ordre") {
        var place = s.ordre.map(function (k, i) { return '<button class="piece" data-j="retirer" data-i="' + i + '"' + (f ? " disabled" : "") + ">" + CV.ligneCode(q.lignes[k]) + "</button>"; }).join("");
        var res = s.reserve.map(function (k, i) { return '<button class="piece" data-j="placer" data-i="' + i + '">' + CV.ligneCode(q.lignes[k]) + "</button>"; }).join("");
        return '<p class="consigne">But : ' + esc(q.but) + '</p><p class="doux">Touche les lignes dans l\'ordre. Touche une ligne placée pour la retirer.</p>' +
          '<h3 class="sous">' + CV.libelle("mien") + '</h3><div class="zone-ordre">' + (place || '<span class="doux">Vide pour l\'instant.</span>') + "</div>" +
          (res ? '<h3 class="sous">Les lignes</h3><div class="choix">' + res + "</div>" : "") +
          (f ? '<p class="doux">' + CV.libelle("resultat") + '</p>' + affichage(q.affiche) : "");
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
          (f ? '<p class="doux">' + CV.libelle("resultat") + '</p>' + affichage(q.affiche) :
            '<p class="doux">Pièces pour le trou ' + (s.sel + 1) + ' :</p><div class="jetons">' + (s.jet ? s.jet[s.sel] : tr.options.map(function (_, j) { return j; })).map(function (j) {
              return '<button class="jeton" data-j="jeton" data-k="' + j + '">' + esc(tr.options[j]) + "</button>";
            }).join("") + "</div>");
      }
      if (type === "trace") return zoneTrace(q, s, f);
      if (type === "combien") return zoneCombien(q, s, f);
      if (type === "paniers") return zonePaniers(q, s, f);
      if (type === "intrus") return zoneIntrus(q, s, f);
      if (type === "memo") return zoneMemo(q, s, f);
      if (type === "bits") return zoneBits(q, s, f);
      return '<div class="message ko" role="alert">Ce mini-jeu (« ' + esc(type) + ' ») est trop récent pour cette page : recharge-la. Si le message reste, préviens ton enseignant·e.</div>';
    }
    // ---------------------------------------------------------------- les six types ajoutés (T135)
    function texteOuCode(t, code) { return code ? '<code class="mono">' + CV.colorer(t) + "</code>" : esc(t); }
    // 7. tableau de trace : les valeurs des variables après chaque tour de boucle
    function lignesTrace(q) { return (q.depart ? ["Avant la boucle"] : []).concat(q.tours.slice(q.depart ? 1 : 0).map(function (_, k) { return "Après le tour " + (k + 1); })); }
    function visible(q, r, c) { return (q.visibles || []).some(function (v) { return v[0] === r && v[1] === c; }); }
    function zoneTrace(q, s, f) {
      var noms = lignesTrace(q);
      var numerique = q.colonnes.map(function (_, c) { return q.tours.every(function (l) { return /^-?\d+$/.test(l[c]); }); });
      return '<p class="consigne">' + esc(q.consigne || "Remplis le tableau : la valeur de chaque variable à la fin de chaque tour.") + "</p>" +
        (q.code ? CV.blocCode(q.code.split("\n")) : "") +
        '<div class="defile"><table class="trace"><caption class="sr">Tableau de trace</caption><thead><tr><th scope="col">Moment</th>' +
        q.colonnes.map(function (c) { return '<th scope="col"><code class="mono">' + esc(c) + "</code></th>"; }).join("") + "</tr></thead><tbody>" +
        q.tours.map(function (ligne, r) {
          return '<tr><th scope="row">' + esc(noms[r]) + "</th>" + ligne.map(function (v, c) {
            if (visible(q, r, c)) return '<td class="donne">' + esc(v) + "</td>";
            var cle = r + "-" + c, val = s.vals[cle] == null ? "" : s.vals[cle], ko = s.faux && s.faux[cle];
            return "<td><input type=\"text\" class=\"cellule" + (f ? " ok" : ko ? " ko" : "") + '" data-cle="' + cle + '" value="' + esc(f ? v : val) + '"' +
              (numerique[c] ? ' inputmode="numeric"' : "") + ' autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="' + esc(q.colonnes[c] + ", " + noms[r]) + '"' +
              (ko ? ' aria-invalid="true"' : "") + (f ? " disabled" : "") + "></td>";
          }).join("") + "</tr>";
        }).join("") + "</tbody></table></div>";
    }
    // 8. combien ? : un compteur + et −, sans clavier
    function zoneCombien(q, s, f) {
      var grand = (q.max - q.min) >= 20, d = f ? " disabled" : "";
      return '<p class="consigne">' + esc(q.texte) + "</p>" + (q.code ? CV.blocCode(q.code.split("\n")) : "") +
        '<div class="compteur" role="group" aria-label="Ta réponse">' +
        (grand ? '<button class="btn" data-j="plus" data-v="-10" aria-label="Moins 10"' + d + ">−10</button>" : "") +
        '<button class="btn" data-j="plus" data-v="-1" aria-label="Moins 1"' + d + ">−</button>" +
        '<output class="valeur" id="valeur" tabindex="0" role="spinbutton" aria-valuemin="' + q.min + '" aria-valuemax="' + q.max + '" aria-valuenow="' + s.n + '" aria-label="Ta réponse (flèches haut et bas)">' + s.n + "</output>" +
        '<button class="btn" data-j="plus" data-v="1" aria-label="Plus 1"' + d + ">+</button>" +
        (grand ? '<button class="btn" data-j="plus" data-v="10" aria-label="Plus 10"' + d + ">+10</button>" : "") + "</div>";
    }
    // 9. deux paniers : chaque carte va dans l'un des deux
    function zonePaniers(q, s, f) {
      var reste = s.ordre.filter(function (i) { return s.places[i] == null; });
      var panier = function (p) {
        var dedans = s.ordre.filter(function (i) { return s.places[i] === p; });
        return '<div class="panier"><h3>' + esc(q.paniers[p]) + ' <span class="nb-cartes">(' + dedans.length + ")</span></h3>" +
          (dedans.length ? '<ul class="dans-panier">' + dedans.map(function (i) { return "<li>" + texteOuCode(q.cartes[i].texte, q.code_cartes) + "</li>"; }).join("") + "</ul>" : '<p class="doux">Vide pour l\'instant.</p>') + "</div>";
      };
      return '<p class="consigne">' + esc(q.consigne) + " Pour chaque carte, touche le bon panier.</p>" +
        (reste.length ? '<div class="cartes">' + reste.map(function (i) {
          var c = q.cartes[i];
          return '<div class="carte-jeu' + (s.faux === i ? " ko" : "") + '"><div class="carte-texte">' + texteOuCode(c.texte, q.code_cartes) + '</div><div class="vers">' +
            [0, 1].map(function (p) { return '<button class="btn" data-j="panier" data-i="' + i + '" data-p="' + p + '" aria-label="' + esc("Ranger « " + c.texte + " » dans " + q.paniers[p]) + '">' + esc(q.paniers[p]) + "</button>"; }).join("") +
            "</div></div>";
        }).join("") + "</div>" : "") +
        '<div class="paniers">' + panier(0) + panier(1) + "</div>";
    }
    // 10. l'intrus : toucher celui qui ne va pas avec les autres, puis dire pourquoi
    function zoneIntrus(q, s, f) {
      var h = '<p class="consigne">' + esc(q.consigne) + "</p>";
      if (s.phase === 1 && !f) {
        return h + '<p class="doux">Touche l\'intrus.</p><div class="choix">' + s.elems.map(function (k) {
          return '<button class="option' + (s.desactives[k] ? " ko" : "") + '" data-j="intrus" data-k="' + k + '"' + (s.desactives[k] ? " disabled" : "") + "><pre>" +
            (q.executer ? CV.blocLignes(q.elements[k]) : esc(q.elements[k])) + "</pre></button>";
        }).join("") + "</div>";
      }
      h += '<div class="choix">' + s.elems.map(function (k) {
        return '<div class="option' + (k === q.intrus ? " ok" : " eteint") + '"><pre>' + (q.executer ? CV.blocLignes(q.elements[k]) : esc(q.elements[k])) + "</pre>" + (k === q.intrus ? '<span class="marque">l\'intrus</span>' : "") + "</div>";
      }).join("") + "</div>";
      if (f) return h;
      return h + '<p class="consigne">Pourquoi est-ce l\'intrus ?</p><div class="choix">' + s.opts.map(function (k) {
        return '<button class="option' + (s.pdes && s.pdes[k] ? " ko" : "") + '" data-j="pourquoi" data-k="' + k + '"' + (s.pdes && s.pdes[k] ? " disabled" : "") + ">" + esc(q.pourquoi.options[k]) + "</button>";
      }).join("") + "</div>";
    }
    // 11. mémo des paires : retourner deux cartes, garder les paires
    function faceMemo(q, c) { var t = q.paires[c[0]][c[1]]; return q.executer && c[1] === 0 ? '<code class="mono">' + CV.blocLignes(t) + "</code>" : esc(t); }
    function zoneMemo(q, s, f) {
      var trouvees = Object.keys(s.trouves).length;
      return '<p class="consigne">' + esc(q.consigne) + " Touche deux cartes pour les retourner.</p>" +
        '<p class="doux">' + trouvees + " paire" + (trouvees > 1 ? "s" : "") + " sur " + q.paires.length + " · " + s.coups + " coup" + (s.coups > 1 ? "s" : "") + "</p>" +
        '<div class="memo">' + s.cartes.map(function (c, k) {
          var vue = s.trouves[c[0]] || s.ouvertes.indexOf(k) >= 0;
          return '<button class="memo-carte' + (s.trouves[c[0]] ? " ok" : vue ? " ouverte" : "") + '" data-j="memo" data-k="' + k + '"' + (s.trouves[c[0]] || (s.ouvertes.length === 1 && s.ouvertes[0] === k) || f ? " disabled" : "") +
            ' aria-label="' + esc("Carte " + (k + 1) + (vue ? " : " + q.paires[c[0]][c[1]] : ", cachée")) + '">' + (vue ? faceMemo(q, c) : '<span aria-hidden="true">?</span>') + "</button>";
        }).join("") + "</div>";
    }
    // 12. allume les bits : des ampoules de poids 2^k, groupées par 4
    function zoneBits(q, s, f) {
      var n = q.reponse.length, b = f ? q.reponse : s.bits, v = CV.valeurBits(b), html = "";
      for (var g = 0; g < n; g += 4) {
        html += '<div class="quartet">';
        for (var i = g; i < Math.min(n, g + 4); i++) {
          var on = b[i] === "1", poids = Math.pow(2, n - 1 - i);
          html += '<button class="bit' + (on ? " on" : "") + '" data-j="bit" data-i="' + i + '" aria-pressed="' + on + '" aria-label="' + esc("Bit de poids " + poids + (on ? ", allumé" : ", éteint")) + '"' + (f ? " disabled" : "") + ">" +
            (q.poids !== false ? '<small aria-hidden="true">' + poids + "</small>" : "") + '<b aria-hidden="true">' + (on ? "1" : "0") + "</b></button>";
        }
        html += "</div>";
      }
      var montre = q.valeur || f;
      return '<p class="consigne">' + esc(q.texte) + '</p><div class="octet">' + html + "</div>" +
        (q.base === "rvb" ? '<div class="pastille" style="background:#' + ("000000" + v.toString(16)).slice(-6) + '" role="img" aria-label="La couleur obtenue"></div>' : "") +
        (montre ? '<p class="valeur-bits" aria-live="polite">' + esc(ecrireBits(q, v)) + "</p>" : "");
    }
    function ecrireBits(q, v) {
      if (q.base === "16" || q.base === "rvb") return "En hexadécimal : " + (q.base === "rvb" ? "#" : "") + ("00000000" + v.toString(16).toUpperCase()).slice(-Math.ceil(q.reponse.length / 4));
      return "En décimal : " + v;
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
      if (a === "plus") {
        s.n = Math.max(q.min, Math.min(q.max, s.n + (+el.getAttribute("data-v"))));
        G.msg = ""; dessiner(); var o2 = racine.querySelector('[data-j=plus][data-v="' + el.getAttribute("data-v") + '"]'); if (o2) o2.focus();
        return sauver();
      }
      if (a === "panier") {
        var ic = +el.getAttribute("data-i"), pc = +el.getAttribute("data-p"), carte = q.cartes[ic];
        if (pc !== carte.panier) { s.faux = ic; return rate(esc(carte.retour || ("« " + carte.texte + " » ne va pas dans « " + q.paniers[pc] + " ». Relis la consigne.")) + " Essaie l'autre panier."); }
        s.places[ic] = pc; s.faux = null; G.essais++;
        if (Object.keys(s.places).length === q.cartes.length) return juste(q.explication);
        G.msg = "Bien rangé : « " + esc(carte.texte) + " » va dans « " + esc(q.paniers[pc]) + " »."; G.cls = "ok"; dessiner(); focusPremier("[data-j=panier]"); return sauver();
      }
      if (a === "intrus") {
        var ki = +el.getAttribute("data-k");
        if (ki === q.intrus) { s.phase = 2; G.essais++; G.msg = "Oui, c'est l'intrus. Maintenant, dis pourquoi."; G.cls = "ok"; dessiner(); focusPremier("[data-j=pourquoi]"); return sauver(); }
        s.desactives[ki] = true; return rate(esc((q.retours && q.retours[ki]) || "Celui-ci va avec les autres. Cherche ce qu'ils ont en commun.") + " Essaie encore.");
      }
      if (a === "pourquoi") {
        var kp = +el.getAttribute("data-k");
        if (kp === q.pourquoi.bonne) return juste(String(q.pourquoi.retours[kp]).replace(/^Juste[ .:]*/, "") + " " + (q.explication || ""));
        s.pdes = s.pdes || {}; s.pdes[kp] = true; return rate(esc(q.pourquoi.retours[kp]) + " Essaie encore.");
      }
      if (a === "memo") {
        var km = +el.getAttribute("data-k");
        if (s.ouvertes.length === 2) s.ouvertes = [];
        s.ouvertes.push(km);
        if (s.ouvertes.length === 2) {
          var c1 = s.cartes[s.ouvertes[0]], c2 = s.cartes[s.ouvertes[1]];
          s.coups++; G.essais++;
          if (c1[0] === c2[0]) {
            s.trouves[c1[0]] = true; s.ouvertes = [];
            if (Object.keys(s.trouves).length === q.paires.length) return juste("Toutes les paires en " + s.coups + " coups. " + (q.explication || ""));
            G.msg = "Paire trouvée : « " + esc(q.paires[c1[0]][0]) + " » et « " + esc(q.paires[c1[0]][1]) + " »."; G.cls = "ok";
          } else { G.msg = "Ce n'est pas une paire : « " + esc(q.paires[c1[0]][c1[1]]) + " » et « " + esc(q.paires[c2[0]][c2[1]]) + " ». Retiens-les, puis touche une autre carte."; G.cls = "info"; }
        } else { G.msg = "Carte " + (km + 1) + " : « " + esc(q.paires[s.cartes[km][0]][s.cartes[km][1]]) + " »."; G.cls = "info"; }
        dessiner(); focusPremier(".memo-carte:not([disabled])"); return sauver();
      }
      if (a === "bit") {
        var ib = +el.getAttribute("data-i");
        s.bits = s.bits.slice(0, ib) + (s.bits[ib] === "1" ? "0" : "1") + s.bits.slice(ib + 1);
        G.msg = ""; dessiner(); var bb = racine.querySelector('[data-j=bit][data-i="' + ib + '"]'); if (bb) bb.focus(); return sauver();
      }
      if (a === "verifier") {
        if (type === "trace") {
          lireTrace();
          s.faux = {}; var vides = 0, nf2 = 0, premier = null;
          q.tours.forEach(function (l, r) { l.forEach(function (v, c) {
            if (visible(q, r, c)) return;
            var cle = r + "-" + c, t = CV.normTrace(s.vals[cle]);
            if (!t) vides++; else if (t !== CV.normTrace(v)) { s.faux[cle] = true; nf2++; if (premier == null) premier = r; }
          }); });
          if (vides) return info("Il reste " + vides + " case" + (vides > 1 ? "s" : "") + " vide" + (vides > 1 ? "s" : "") + " dans le tableau.");
          if (!nf2) return juste(q.explication);
          return rate(nf2 + " case" + (nf2 > 1 ? "s ne vont" : " ne va") + " pas. Reprends à la ligne « " + esc(lignesTrace(q)[premier]) + " » : exécute le tour ligne par ligne.");
        }
        if (type === "combien") {
          if (s.n === q.reponse) return juste(q.explication);
          return rate("Ce n'est pas " + s.n + ". Recompte pas à pas : écris ce qui se passe à chaque tour.");
        }
        if (type === "bits") {
          if (s.bits === q.reponse) return juste(q.explication);
          return rate("Pas encore : tes bits font " + esc(ecrireBits(q, CV.valeurBits(s.bits)).replace(/^En /, "")) + ". Additionne les poids des bits allumés.");
        }
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
      racine.removeEventListener("click", clic); racine.removeEventListener("keydown", touche); racine.removeEventListener("input", saisie);
      o.surFin(r);
    }
    function focusPremier(sel) { var x = racine.querySelector(sel); if (x) x.focus({ preventScroll: true }); }
    // les cases d'un tableau de trace : gardées à chaque frappe (reprise de la partie)
    function lireTrace() { Array.prototype.forEach.call(racine.querySelectorAll("input.cellule"), function (i) { G.s.vals[i.getAttribute("data-cle")] = i.value; }); }
    function saisie(ev) { if (type === "trace" && ev.target.classList.contains("cellule")) { lireTrace(); if (G.s.faux) delete G.s.faux[ev.target.getAttribute("data-cle")]; ev.target.classList.remove("ko"); ev.target.removeAttribute("aria-invalid"); sauver(); } }
    function clic(ev) { var el = ev.target.closest("[data-j]"); if (el && racine.contains(el)) action(el.getAttribute("data-j"), el); }
    function touche(ev) {
      if (ev.key === "Enter" && (ev.target.id === "rep" || ev.target.classList.contains("cellule"))) { ev.preventDefault(); action("verifier"); }
      if (type === "combien" && ev.target.id === "valeur" && !G.fini && /^(ArrowUp|ArrowDown|ArrowRight|ArrowLeft|PageUp|PageDown)$/.test(ev.key)) {
        ev.preventDefault();
        var pas = { ArrowUp: 1, ArrowRight: 1, ArrowDown: -1, ArrowLeft: -1, PageUp: 10, PageDown: -10 }[ev.key], q = it();
        G.s.n = Math.max(q.min, Math.min(q.max, G.s.n + pas)); G.msg = ""; dessiner(); focusPremier("#valeur"); sauver();
      }
    }
    racine.addEventListener("click", clic);
    racine.addEventListener("keydown", touche);
    racine.addEventListener("input", saisie);
    // pour les essais automatiques (Playwright) : l'état de la question en cours, en lecture
    racine.cvEtat = function () { return { type: type, item: it(), s: G.s, fini: G.fini }; };
    var h = racine.querySelector("h1"); if (h) h.focus({ preventScroll: true });
    return { arreter: function () { sauver(); racine.removeEventListener("click", clic); racine.removeEventListener("keydown", touche); racine.removeEventListener("input", saisie); } };
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
    if (t === "sortie") return CV.blocCode(q.code.split("\n")) + '<p class="doux">' + CV.libelle("affiche") + '</p><div class="affiche">' + esc2(q.options ? q.options[q.bonne].split(" / ").join("\n") : q.reponse) + '</div><p class="doux">' + esc2(q.options ? q.retours[q.bonne] : q.explication) + "</p>";
    if (t === "associer") return "<p>" + esc2(q.consigne) + '</p><table class="paires">' + q.paires.map(function (p) { return "<tr><td><code class=\"mono\">" + (q.executer || q.code_gauche ? CV.blocLignes(p[0]) : esc2(p[0])) + "</code></td><td>" + esc2(p[1]) + "</td></tr>"; }).join("") + '</table><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "erreur") {
      var l2 = q.lignes.slice(); l2[q.ligne] = q.corrections[q.bonne]; var c1 = {}, c2 = {}; c1[q.ligne] = "ko"; c2[q.ligne] = "ok";
      return "<p><b>But :</b> " + esc2(q.but) + '</p><p class="doux">Avec l\'erreur :</p>' + CV.blocCode(q.lignes, { classes: c1 }) + CV.console(q, CV.langage) + '<p class="doux">Corrigé :</p>' + CV.blocCode(l2, { classes: c2 }) + '<p class="doux">' + esc2(q.explication) + "</p>";
    }
    if (t === "ordre") return "<p><b>But :</b> " + esc2(q.but) + "</p>" + CV.blocCode(q.lignes) + '<p class="doux">' + CV.libelle("affiche") + '</p><div class="affiche">' + esc2(q.affiche) + "</div>";
    if (t === "trace") {
      var noms = (q.depart ? ["Avant la boucle"] : []).concat(q.tours.slice(q.depart ? 1 : 0).map(function (_, k) { return "Après le tour " + (k + 1); }));
      return (q.code ? CV.blocCode(q.code.split("\n")) : "") + '<div class="defile"><table class="trace"><thead><tr><th scope="col">Moment</th>' +
        q.colonnes.map(function (c) { return '<th scope="col"><code class="mono">' + esc2(c) + "</code></th>"; }).join("") + "</tr></thead><tbody>" +
        q.tours.map(function (l, r) { return '<tr><th scope="row">' + esc2(noms[r]) + "</th>" + l.map(function (v) { return "<td>" + esc2(v) + "</td>"; }).join("") + "</tr>"; }).join("") +
        '</tbody></table></div><p class="doux">' + esc2(q.explication) + "</p>";
    }
    if (t === "combien") return "<p>" + esc2(q.texte) + "</p>" + (q.code ? CV.blocCode(q.code.split("\n")) : "") + '<p>Réponse : <b>' + q.reponse + '</b></p><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "paniers") return "<p>" + esc2(q.consigne) + '</p><div class="paniers">' + [0, 1].map(function (p) {
      return '<div class="panier"><h3>' + esc2(q.paniers[p]) + '</h3><ul class="dans-panier">' + q.cartes.filter(function (c) { return c.panier === p; }).map(function (c) {
        return "<li>" + (q.code_cartes ? '<code class="mono">' + CV.colorer(c.texte) + "</code>" : esc2(c.texte)) + "</li>"; }).join("") + "</ul></div>";
    }).join("") + '</div><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "intrus") return "<p>" + esc2(q.consigne) + '</p><div class="choix">' + q.elements.map(function (e, k) {
      return '<div class="option' + (k === q.intrus ? " ok" : " eteint") + '"><pre>' + (q.executer ? CV.blocLignes(e) : esc2(e)) + "</pre>" + (k === q.intrus ? '<span class="marque">l\'intrus</span>' : "") + "</div>";
    }).join("") + "</div><p><b>Pourquoi :</b> " + esc2(q.pourquoi.options[q.pourquoi.bonne]) + '</p><p class="doux">' + esc2(q.explication || q.pourquoi.retours[q.pourquoi.bonne]) + "</p>";
    if (t === "memo") return "<p>" + esc2(q.consigne) + '</p><table class="paires">' + q.paires.map(function (p) { return "<tr><td><code class=\"mono\">" + (q.executer ? CV.blocLignes(p[0]) : esc2(p[0])) + "</code></td><td>" + esc2(p[1]) + "</td></tr>"; }).join("") + '</table><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "bits") return "<p>" + esc2(q.texte) + '</p><p>Réponse : <code class="mono bits-reponse">' + esc2(q.reponse.replace(/(.{4})(?=.)/g, "$1 ")) + '</code></p><p class="doux">' + esc2(q.explication) + "</p>";
    if (t === "completer") {
      var lc = q.lignes.map(function (x) { return x.replace(/\{(\d+)\}/g, function (_, d) { return q.trous[+d].options[q.trous[+d].bonne]; }); });
      return "<p><b>But :</b> " + esc2(q.but) + "</p>" + CV.blocCode(lc) + '<p class="doux">' + esc2(q.explication) + "</p>";
    }
    return "";
  }
})();
