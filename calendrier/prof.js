/* Calendrier des vacances : la page enseignant·e (version minimale de Noël 2026).
   Fonctions de la base : cv_prof_creer_espace, cv_prof_ouvrir, cv_prof_creer_calendrier,
   cv_prof_tableau, cv_prof_inscriptions, cv_prof_nouveau_code_eleve, cv_prof_renommer_eleve,
   cv_prof_retirer_eleve, cv_prof_supprimer_calendrier, cv_prof_debloquer_reseau.
   Le tableau de suivi ne classe personne : les élèves sont rangés par ordre alphabétique. */
(function () {
  "use strict";
  var CV = window.CV, esc = CV.esc, C = window.CV_CONFIG || {}, racine = document.getElementById("app");
  var code = null, espace = null, calCourant = null, tableau = null, minuterie = null, masquer = false;
  var mem = CV.lire("prof", null);
  if (mem && mem.expire > Date.now()) code = mem.code; else CV.ecrire("prof", null);

  function afficher(html) {
    clearInterval(minuterie);
    racine.innerHTML = '<header class="haut"><div class="titre"><h1>Calendrier des vacances</h1><small>Espace enseignant·e' + (espace ? " · " + esc(espace.nom) : "") + "</small></div>" +
      (code ? '<button class="btn petit" data-act="quitter">Quitter</button>' : "") +
      '<button class="icone" data-act="theme" aria-label="Changer l\'affichage clair ou obscur">' + CV.ICONE_THEME + "</button></header>" + html + CV.pied();
    window.scrollTo(0, 0);
  }
  function message(msg, cls) { return '<div class="message ' + (cls || "ko") + '" role="' + (cls === "ok" ? "status" : "alert") + '">' + esc(msg || "") + "</div>"; }

  // ------------------------------------------------------------ entrer ou créer son espace
  function accueil(msg, cls) {
    if (!CV.enLigne) return afficher(CV.horsService());
    if (code) return ouvrir();
    afficher('<section class="carte"><h2>Ouvrir mon espace</h2><label for="code">Mon code d\'enseignant·e (3 mots et 4 chiffres)</label>' +
      '<input type="text" id="code" class="code-saisie" autocomplete="off" spellcheck="false" placeholder="PION-SURF-BINGO-2741">' +
      '<label class="case-a-cocher"><input type="checkbox" id="garder"> Garder mon code sur cet appareil 60 jours (sur un appareil personnel seulement)</label>' + message(msg, cls) +
      '<div class="pile"><button class="btn plein large" data-act="ouvrir">Ouvrir</button></div></section>' +
      '<section class="carte"><h2>Créer mon espace</h2><p class="doux">Pas de mot de passe ni d\'adresse électronique : un code de 3 mots et 4 chiffres, montré une seule fois.</p>' +
      '<label for="nom">Le nom que verront les élèves</label><input type="text" id="nom" maxlength="40" placeholder="Mme N." autocomplete="off">' +
      '<div class="pile"><button class="btn large" data-act="creer-espace">Créer mon espace</button></div></section>');
  }
  function ouvrirDepuisSaisie() {
    var l = CV.lireCode(document.getElementById("code").value, 3);
    if (l.erreur) return accueil(l.erreur, "info");
    code = l.code;
    if (document.getElementById("garder").checked) CV.ecrire("prof", { code: code, expire: Date.now() + 60 * 86400000 });
    ouvrir();
  }
  function ouvrir() {
    afficher('<p class="doux" role="status">Un instant…</p>');
    CV.rpc("cv_prof_ouvrir", { p_code: code }).then(function (r) {
      if (!r.ok) { if (!r.reseau) { code = null; CV.ecrire("prof", null); } return accueil(r.message); }
      espace = r; listeCalendriers();
    });
  }
  function creerEspace() {
    var nom = (document.getElementById("nom").value || "").trim();
    CV.rpc("cv_prof_creer_espace", { p_nom: nom }).then(function (r) {
      if (!r.ok) return accueil(r.message);
      afficher('<section class="carte"><h2>Voici votre code</h2><div class="grand-code">' + esc(r.code_affiche) + "</div>" +
        "<p><b>Il n'est montré qu'une seule fois</b> et personne ne peut le retrouver, pas même la personne qui gère la base. Notez-le ou imprimez-le. Il ouvre votre espace depuis n'importe quel appareil.</p>" +
        '<label for="verif">Pour vérifier, tapez les 4 chiffres du code</label><input type="text" id="verif" inputmode="numeric" maxlength="4" autocomplete="off"><div id="msg"></div>' +
        '<div class="pile"><button class="btn large" data-act="imprimer">Imprimer</button><button class="btn plein large" data-act="note">Je l\'ai noté</button></div></section>');
      document.querySelector("[data-act=note]").onclick = function () {
        if (document.getElementById("verif").value.trim() !== r.code_affiche.split("-").pop()) { document.getElementById("msg").innerHTML = message("Ce ne sont pas les bons chiffres."); return; }
        code = r.code_affiche; ouvrir();
      };
    });
  }

  // ------------------------------------------------------------ mes calendriers
  function listeCalendriers(msg) {
    var cals = espace.calendriers || [];
    afficher((msg ? message(msg, "ok") : "") + '<div class="entre"><h2>Mes calendriers</h2><button class="btn plein" data-act="nouveau">Nouveau calendrier</button></div>' +
      (cals.length ? '<div class="a-faire">' + cals.map(function (c) {
        return '<button class="case-carte" data-act="voir" data-id="' + esc(c.id) + '"><span class="date"><b>' + esc(c.code) + '</b></span><span class="quoi"><b>' + esc(c.nom) + "</b><span>du " +
          esc(CV.dateCourte(c.debut)) + " au " + esc(CV.dateCourte(c.fin)) + " · " + c.eleves + " élève" + (c.eleves > 1 ? "s" : "") + " · " + (c.themes || []).length + " thème" + ((c.themes || []).length > 1 ? "s" : "") + "</span></span></button>";
      }).join("") + "</div>" : '<p class="doux">Aucun calendrier pour l\'instant.</p>') +
      '<section class="carte"><h2>Le réseau de la salle</h2><p class="doux">Si trop de codes faux ont été tapés depuis le lycée, les élèves sont bloqué·e·s une heure. Depuis le même réseau, vous pouvez les débloquer.</p>' +
      '<button class="btn" data-act="debloquer">Débloquer le réseau</button></section>');
  }

  // ------------------------------------------------------------ créer un calendrier
  // cal : le calendrier à modifier (sinon, un nouveau). Après le premier jour, le premier jour ne change plus,
  // et seules les cases de demain et des jours suivants sont refaites (la base y veille).
  function nouveau(msg, cal) {
    var auj = CV.aujourdhuiMayotte();
    var vac = (C.VACANCES || []).filter(function (v) { return v.fin >= auj; });
    var debut = vac[0] ? (vac[0].debut < auj ? auj : vac[0].debut) : auj, fin = vac[0] ? vac[0].fin : CV.ajouter(auj, 13);
    var commence = cal && cal.debut <= auj;
    if (cal) { debut = cal.debut; fin = cal.fin; vac = commence ? [] : vac; }
    afficher('<div class="jeu-haut"><button class="btn" data-act="' + (cal ? "voir\" data-id=\"" + esc(cal.id) : "liste") + '">&#8592; ' + (cal ? "Le calendrier" : "Mes calendriers") + "</button></div><h2>" + (cal ? "Modifier « " + esc(cal.nom) + " »" : "Nouveau calendrier") + "</h2>" + message(msg) +
      (commence ? '<p class="message info">Le calendrier a commencé : son premier jour ne change plus. Les cases déjà ouvertes et les résultats ne bougent jamais ; seules les cases de demain et des jours suivants sont refaites.</p>' : "") +
      '<section class="carte"><label for="nomc">Nom (vu par les élèves)</label><input type="text" id="nomc" maxlength="60" placeholder="1NSI : vacances de Noël" value="' + esc(cal ? cal.nom : "") + '">' +
      '<div class="dates"><label>Premier jour <input type="date" id="debut" value="' + debut + '"' + (commence ? " disabled" : ' min="' + auj + '"') + '></label><label>Dernier jour <input type="date" id="fin" value="' + fin + '"></label></div>' +
      (vac.length ? '<p class="doux">Raccourcis : ' + vac.map(function (v, i) { return '<button class="lien" data-act="vac" data-i="' + i + '">' + esc(v.nom) + "</button>"; }).join(" · ") + "</p>" : "") +
      '<p class="doux" id="duree"></p></section>' +
      '<section class="carte"><h3>Les thèmes</h3><p class="doux">Cochez librement, quel que soit le niveau de la classe. Les cases alternent entre les thèmes, dans l\'ordre où vous les cochez.</p><div id="themes">Chargement du catalogue…</div><p id="besoin" class="doux"></p></section>' +
      '<section class="carte"><label class="case-a-cocher"><input type="checkbox" id="jauge"' + (!cal || cal.affichage_classe === "jauge" ? " checked" : "") + '> Montrer aux élèves la jauge de toute la classe (des nombres, aucun nom). Décochez pour une très petite classe.</label></section>' +
      '<div class="pile"><button class="btn plein large" data-act="' + (cal ? "modifier-cal" : "creer-cal") + '">' + (cal ? "Enregistrer les changements" : "Créer le calendrier") + "</button></div>");
    nouveau.ordre = cal ? (cal.themes || []).slice() : []; nouveau.vac = vac; nouveau.cal = cal || null;
    CV.catalogue().then(function (cat) {
      // « pret » : relu ; « en_cours » : écrit et contrôlé, pas encore relu (proposé avec la mention « à relire »)
      var prets = cat.themes.filter(function (t) { return t.statut === "pret" || t.statut === "en_cours"; });
      return Promise.all(prets.map(function (t) { return CV.banque(t.id).then(function (b) { t.n = b.exercices.length; t.relus = b.exercices.filter(function (e) { return e.relu; }).length; }, function () { t.n = 0; }); }))
        .then(function () {
          prets = prets.filter(function (t) { return t.n >= 8; });
          nouveau.themes = prets;
          document.getElementById("themes").innerHTML = prets.map(function (t) {
            return '<label class="case-a-cocher"><input type="checkbox" data-theme="' + esc(t.id) + '"> <span><b>' + esc(t.titre) + "</b> <small class=\"etiquette\">" + esc(t.nature === "notion" ? "notion" : "chapitre") +
              "</small> " + (t.niveaux || []).map(function (n) { return '<small class="etiquette">' + esc({ snt: "SNT", "nsi-1re": "1re", "nsi-tle": "Tle" }[n] || n) + "</small>"; }).join(" ") +
              ' <small class="doux">' + t.n + " exercices" + (t.relus < t.n ? ", " + (t.n - t.relus) + " à relire" : "") + "</small></span></label>";
          }).join("") || '<p class="message ko">Aucun thème prêt dans le catalogue.</p>';
          nouveau.ordre.forEach(function (id) { var c = document.querySelector('input[data-theme="' + id + '"]'); if (c) c.checked = true; });
          majBesoin();
        });
    }, function () { document.getElementById("themes").innerHTML = message("Le catalogue des thèmes est illisible : rechargez la page."); });
    racine.addEventListener("change", majBesoin);
    majBesoin();
  }
  function majBesoin(ev) {
    if (ev && ev.target && ev.target.hasAttribute && ev.target.hasAttribute("data-theme")) {
      var id = ev.target.getAttribute("data-theme"), o = nouveau.ordre || [];
      if (ev.target.checked) o.push(id); else o.splice(o.indexOf(id), 1);
    }
    var d = document.getElementById("debut"), f = document.getElementById("fin"); if (!d || !f) return;
    var jours = d.value && f.value ? CV.ecart(d.value, f.value) + 1 : 0;
    document.getElementById("duree").textContent = jours > 0 ? jours + " jours sur 30 au plus" + (jours > 30 ? " : trop long." : ".") : "Les dates ne vont pas.";
    var o2 = nouveau.ordre || [], b = document.getElementById("besoin");
    if (!b) return;
    if (!o2.length) { b.textContent = "Aucun thème coché."; return; }
    var parTheme = o2.map(function (id, i) {
      var t = (nouveau.themes || []).filter(function (x) { return x.id === id; })[0] || { titre: id, n: 0 };
      var besoin = Math.floor(jours / o2.length) + (i < jours % o2.length ? 1 : 0);
      return esc(t.titre) + " : " + besoin + " case" + (besoin > 1 ? "s" : "") + (besoin > t.n ? ' <b class="ko-texte">(' + t.n + " exercices seulement : les derniers jours reprennent les premiers, en révision)</b>" : "");
    });
    b.innerHTML = "Ordre des cases : " + o2.map(function (id) { var t = (nouveau.themes || []).filter(function (x) { return x.id === id; })[0]; return esc(t ? t.titre : id); }).join(", puis ") + ".<br>" + parTheme.join("<br>");
  }
  function creerCalendrier() {
    var nom = document.getElementById("nomc").value.trim(), d = document.getElementById("debut").value, f = document.getElementById("fin").value;
    var o = nouveau.ordre || [];
    if (!o.length) return nouveau("Cochez au moins un thème.");
    CV.rpc("cv_prof_creer_calendrier", { p_code: code, p_nom: nom, p_debut: d, p_fin: f, p_themes: o, p_mode: "alternance",
      p_affichage_classe: document.getElementById("jauge").checked ? "jauge" : "aucun" }).then(function (r) {
      if (!r.ok) return nouveau(r.message);
      racine.removeEventListener("change", majBesoin);
      CV.rpc("cv_prof_ouvrir", { p_code: code }).then(function (e) { if (e.ok) espace = e; voir(r.id); });
    });
  }

  function modifierCalendrier() {
    var c = nouveau.cal, o = nouveau.ordre || [];
    if (!o.length) return nouveau("Cochez au moins un thème.", c);
    CV.rpc("cv_prof_modifier_calendrier", { p_code: code, p_calendrier: c.id, p_nom: document.getElementById("nomc").value.trim(),
      p_debut: document.getElementById("debut").value, p_fin: document.getElementById("fin").value, p_themes: o, p_mode: c.mode || "alternance",
      p_affichage_classe: document.getElementById("jauge").checked ? "jauge" : "aucun" }).then(function (r) {
      if (!r.ok) return nouveau(r.message, c);
      racine.removeEventListener("change", majBesoin);
      CV.rpc("cv_prof_ouvrir", { p_code: code }).then(function (e) { if (e.ok) espace = e; voir(c.id, "Calendrier modifié : " + r.cases + " cases."); });
    });
  }

  // ------------------------------------------------------------ un calendrier : inviter et suivre
  function lienEleves(c) { return new URL("./?c=" + c.code, location.href).href; }
  function voir(id, msg) {
    calCourant = (espace.calendriers || []).filter(function (c) { return c.id === id; })[0];
    if (!calCourant) return listeCalendriers();
    racine.removeEventListener("change", majBesoin);
    var c = calCourant, lien = lienEleves(c);
    afficher('<div class="jeu-haut"><button class="btn" data-act="liste">&#8592; Mes calendriers</button></div>' + (msg ? message(msg, "ok") : "") + '<div class="entre"><h2>' + esc(c.nom) + '</h2><button class="btn" data-act="modifier">Modifier</button></div>' +
      '<p class="doux">Du ' + esc(CV.dateLongue(c.debut)) + " au " + esc(CV.dateLongue(c.fin)) + ".</p>" +
      '<section class="carte invite"><h3>Inviter les élèves</h3><div class="invite-grille"><div><p class="doux">Code du calendrier</p><div class="grand-code">' + esc(c.code) + "</div>" +
      '<p class="mono petit-texte">' + esc(lien) + '</p><div class="actions"><button class="btn" data-act="copier">Copier le lien</button><button class="btn" data-act="message">Message pour Pronote</button><button class="btn" data-act="projeter">Projeter</button></div></div>' +
      '<div id="qr" class="qr" role="img" aria-label="QR code du lien du calendrier"></div></div>' +
      '<label class="case-a-cocher"><input type="checkbox" id="inscr"' + (c.inscriptions_ouvertes ? " checked" : "") + '> Inscriptions ouvertes par le lien</label><div id="msg-invite"></div></section>' +
      '<section class="carte"><div class="entre"><h3>Le suivi</h3><span class="direct">en direct</span></div>' +
      '<div class="actions"><label class="case-a-cocher"><input type="checkbox" id="masquer"' + (masquer ? " checked" : "") + '> Masquer les codes (projection)</label><button class="btn" data-act="csv">Exporter en CSV</button></div>' +
      '<div id="tableau"><p class="doux">Chargement…</p></div></section>' +
      '<section class="carte"><h3>Supprimer ce calendrier</h3><p class="doux">Ses cases et tous les résultats des élèves sont effacés. Les comptes des élèves restent.</p><button class="btn" data-act="supprimer">Supprimer…</button></section>');
    try { var q = window.qrcode(0, "M"); q.addData(lien); q.make(); document.getElementById("qr").innerHTML = q.createSvgTag({ scalable: true, margin: 2 }); } catch (e) { document.getElementById("qr").textContent = "QR code indisponible."; }
    document.getElementById("inscr").onchange = function (ev) {
      CV.rpc("cv_prof_inscriptions", { p_code: code, p_calendrier: c.id, p_ouvertes: ev.target.checked }).then(function (r) {
        c.inscriptions_ouvertes = ev.target.checked;
        document.getElementById("msg-invite").innerHTML = r.ok ? message(ev.target.checked ? "Inscriptions ouvertes." : "Inscriptions fermées : les élèves déjà inscrit·e·s continuent.", "ok") : message(r.message);
      });
    };
    document.getElementById("masquer").onchange = function (ev) { masquer = ev.target.checked; dessinerTableau(); };
    chargerTableau();
    minuterie = setInterval(function () { if (document.visibilityState === "visible") chargerTableau(); }, 30000);
  }
  function chargerTableau() {
    if (!calCourant) return;
    CV.rpc("cv_prof_tableau", { p_code: code, p_calendrier: calCourant.id }).then(function (r) {
      var z = document.getElementById("tableau"); if (!z) return;
      if (!r.ok) { z.innerHTML = message(r.message); return; }
      tableau = r; dessinerTableau();
    });
  }
  function joursDifferents(e) {
    var j = {}; e.resultats.forEach(function (r) { if (r.reussi) j[new Date(new Date(r.fait_le).getTime() + 3 * 3600000).toISOString().slice(0, 10)] = 1; });
    return Object.keys(j).length;
  }
  function cellule(e, c, auj) {
    var rs = e.resultats.filter(function (r) { return r.numero === c.numero; }), et = 0, rat = false;
    rs.forEach(function (r) { if (r.reussi && r.dans_les_temps && r.etoiles > et) et = r.etoiles; if (r.reussi && !r.dans_les_temps) rat = true; });
    if (et) return '<td class="t-ok" title="' + et + ' étoile(s)">' + et + "</td>";
    if (rat) return '<td class="t-r" title="rattrapée">R</td>';
    if (c.jour > auj) return '<td class="t-av"></td>';
    return '<td class="t-vide" title="pas encore faite">·</td>';
  }
  function dessinerTableau() {
    var z = document.getElementById("tableau"); if (!z || !tableau) return;
    var t = tableau, auj = t.aujourdhui, ouvertes = t.cases.filter(function (c) { return c.jour <= auj; });
    if (!t.eleves.length) { z.innerHTML = '<p class="doux">Aucun·e élève inscrit·e pour l\'instant. Projetez le lien ou le QR code.</p>'; return; }
    var tete = "<tr><th scope=\"col\">Élève</th><th scope=\"col\">Code</th><th scope=\"col\">Cases faites</th><th scope=\"col\">Jours différents</th><th scope=\"col\">Vu le</th>" +
      t.cases.map(function (c) { return '<th scope="col" class="t-jour" title="' + esc(CV.dateLongue(c.jour) + " · " + c.theme + " n° " + c.rang) + '">' + CV.versDate(c.jour).getUTCDate() + "</th>"; }).join("") + "<th></th></tr>";
    var lignes = t.eleves.map(function (e) {
      var faites = {}; e.resultats.forEach(function (r) { if (r.reussi) faites[r.numero] = 1; });
      var codeAff = masquer ? e.code_affiche.split("-")[0] + "-•••••-•••" : e.code_affiche;
      return "<tr><th scope=\"row\">" + esc(e.pseudo) + '</th><td class="mono">' + esc(codeAff) + "</td><td>" + Object.keys(faites).length + "/" + ouvertes.length + "</td><td>" + joursDifferents(e) +
        "</td><td>" + esc(CV.dateCourte(new Date(new Date(e.vu_le).getTime() + 3 * 3600000).toISOString().slice(0, 10))) + "</td>" + t.cases.map(function (c) { return cellule(e, c, auj); }).join("") +
        '<td><button class="lien" data-act="eleve" data-id="' + esc(e.id) + '">gérer</button></td></tr>';
    }).join("");
    var pied = '<tr><th scope="row">Réussite par case</th><td></td><td></td><td></td><td></td>' + t.cases.map(function (c) {
      if (c.jour > auj) return "<td></td>";
      var n = t.eleves.filter(function (e) { return e.resultats.some(function (r) { return r.numero === c.numero && r.reussi; }); }).length;
      return "<td>" + Math.round(100 * n / t.eleves.length) + "%</td>";
    }).join("") + "<td></td></tr>";
    z.innerHTML = '<p class="doux">' + t.eleves.length + " élève" + (t.eleves.length > 1 ? "s" : "") + ", par ordre alphabétique (aucun classement). Chiffre : étoiles gagnées avant le corrigé ; R : rattrapée ; · : pas encore faite.</p>" +
      '<div class="defile"><table class="suivi"><thead>' + tete + "</thead><tbody>" + lignes + "</tbody><tfoot>" + pied + "</tfoot></table></div>";
  }
  function csv() {
    if (!tableau) return;
    var t = tableau, sep = ";", q = function (v) { v = String(v == null ? "" : v); return /[";\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    var lignes = [["pseudo", "code", "cases faites", "jours différents"].concat(t.cases.map(function (c) { return c.jour + " " + c.theme + " n°" + c.rang; })).map(q).join(sep)];
    t.eleves.forEach(function (e) {
      var faites = {}; e.resultats.forEach(function (r) { if (r.reussi) faites[r.numero] = 1; });
      lignes.push([e.pseudo, e.code_affiche, Object.keys(faites).length, joursDifferents(e)].concat(t.cases.map(function (c) {
        var rs = e.resultats.filter(function (r) { return r.numero === c.numero && r.reussi; });
        if (!rs.length) return "";
        var et = Math.max.apply(null, rs.map(function (r) { return r.dans_les_temps ? r.etoiles : 0; }));
        return et ? et : "R";
      })).map(q).join(sep));
    });
    var b = new Blob([String.fromCharCode(0xFEFF) + lignes.join("\r\n")], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "calendrier-" + calCourant.code + ".csv"; document.body.appendChild(a); a.click(); a.remove();
  }
  function gererEleve(id) {
    var e = tableau.eleves.filter(function (x) { return x.id === id; })[0]; if (!e) return;
    var v = document.createElement("div"); v.className = "voile"; v.setAttribute("data-act", "fermer");
    v.innerHTML = '<div class="feuille" role="dialog" aria-modal="true" aria-label="' + esc(e.pseudo) + '"><h2>' + esc(e.pseudo) + '</h2><p>Code : <span class="mono">' + esc(e.code_affiche) + "</span></p>" +
      '<div class="pile"><button class="btn large" data-act="nouveau-code" data-id="' + esc(id) + '">Nouveau code (code perdu ou divulgué)</button>' +
      '<button class="btn large" data-act="renommer" data-id="' + esc(id) + '">Renommer</button><button class="btn large" data-act="retirer" data-id="' + esc(id) + '">Retirer de ce calendrier…</button>' +
      '<button class="btn large" data-act="fermer">Fermer</button></div><div id="msg-eleve"></div></div>';
    document.body.appendChild(v);
  }
  function fermer() { var v = document.querySelector(".voile"); if (v) v.remove(); }
  function actionEleve(a, id) {
    var e = tableau.eleves.filter(function (x) { return x.id === id; })[0], zone = document.getElementById("msg-eleve");
    var fin = function (r, ok) { if (zone) zone.innerHTML = r.ok ? message(ok, "ok") : message(r.message); chargerTableau(); };
    if (a === "nouveau-code") {
      if (!window.confirm("Donner un nouveau code à " + e.pseudo + " ? L'ancien ne marchera plus ; les résultats restent.")) return;
      return CV.rpc("cv_prof_nouveau_code_eleve", { p_code: code, p_calendrier: calCourant.id, p_eleve: id }).then(function (r) { fin(r, "Nouveau code : " + r.code_affiche); });
    }
    if (a === "renommer") {
      var p = window.prompt("Nouveau prénom ou pseudo (jamais de nom de famille) :", e.pseudo); if (!p) return;
      return CV.rpc("cv_prof_renommer_eleve", { p_code: code, p_calendrier: calCourant.id, p_eleve: id, p_pseudo: p }).then(function (r) { fin(r, "Renommé·e."); });
    }
    if (a === "retirer") {
      var c = window.prompt("Retirer " + e.pseudo + " de ce calendrier efface ses résultats de ce calendrier. Écrivez RETIRER pour confirmer :"); if (!c) return;
      return CV.rpc("cv_prof_retirer_eleve", { p_code: code, p_calendrier: calCourant.id, p_eleve: id, p_confirmation: c.trim().toUpperCase() }).then(function (r) { fin(r, "Retiré·e."); });
    }
  }

  // ------------------------------------------------------------ événements
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest("[data-act]"); if (!el) return;
    var a = el.getAttribute("data-act");
    if (a === "fermer") { if (el.classList.contains("voile") && ev.target !== el) return; return fermer(); }
    if (a === "theme") return CV.basculerTheme();
    if (a === "ouvrir") return ouvrirDepuisSaisie();
    if (a === "creer-espace") return creerEspace();
    if (a === "imprimer") return window.print();
    if (a === "quitter") { code = null; espace = null; CV.ecrire("prof", null); return accueil("Espace fermé sur cet appareil.", "ok"); }
    if (a === "liste") { racine.removeEventListener("change", majBesoin); calCourant = null; return CV.rpc("cv_prof_ouvrir", { p_code: code }).then(function (r) { if (r.ok) espace = r; listeCalendriers(); }); }
    if (a === "nouveau") return nouveau();
    if (a === "vac") { var v = nouveau.vac[+el.getAttribute("data-i")], auj = CV.aujourdhuiMayotte(); document.getElementById("debut").value = v.debut < auj ? auj : v.debut; document.getElementById("fin").value = v.fin; return majBesoin(); }
    if (a === "creer-cal") return creerCalendrier();
    if (a === "modifier") { clearInterval(minuterie); return nouveau("", calCourant); }
    if (a === "modifier-cal") return modifierCalendrier();
    if (a === "voir") return voir(el.getAttribute("data-id"));
    if (a === "copier") { var l = lienEleves(calCourant); (navigator.clipboard ? navigator.clipboard.writeText(l) : Promise.reject()).then(function () { document.getElementById("msg-invite").innerHTML = message("Lien copié.", "ok"); }, function () { window.prompt("Copiez le lien :", l); }); return; }
    if (a === "message") {
      var m = "Calendrier des vacances « " + calCourant.nom + " » : un mini-jeu par jour, 10 minutes au plus, à partir du " + CV.dateLongue(calCourant.debut) + ". Ouvre ce lien : " + lienEleves(calCourant) +
        " (code " + calCourant.code + "). Donne un prénom ou un pseudo (jamais ton nom de famille), puis note ton code dans ton cahier.";
      return window.prompt("Message à copier (Pronote, ENT) :", m);
    }
    if (a === "projeter") { var s = document.querySelector(".invite"); if (s && s.requestFullscreen) s.requestFullscreen(); return; }
    if (a === "csv") return csv();
    if (a === "eleve") return gererEleve(el.getAttribute("data-id"));
    if (a === "nouveau-code" || a === "renommer" || a === "retirer") return actionEleve(a, el.getAttribute("data-id"));
    if (a === "supprimer") {
      var conf = window.prompt("Supprimer « " + calCourant.nom + " », ses cases et tous les résultats ? Écrivez le code du calendrier (" + calCourant.code + ") pour confirmer :"); if (!conf) return;
      return CV.rpc("cv_prof_supprimer_calendrier", { p_code: code, p_calendrier: calCourant.id, p_confirmation: conf }).then(function (r) {
        if (!r.ok) return window.alert(r.message);
        CV.rpc("cv_prof_ouvrir", { p_code: code }).then(function (e) { if (e.ok) espace = e; listeCalendriers("Calendrier supprimé."); });
      });
    }
    if (a === "debloquer") return CV.rpc("cv_prof_debloquer_reseau", { p_code: code }).then(function (r) { window.alert(r.ok ? "Réseau débloqué pour le calendrier." : r.message); });
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") fermer();
    if (ev.key === "Enter" && ev.target.id === "code") { ev.preventDefault(); ouvrirDepuisSaisie(); }
  });
  accueil();
})();
