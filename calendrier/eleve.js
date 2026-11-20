/* Calendrier des vacances : la page élève.
   Fonctions de la base : cv_calendrier_par_code, cv_inscription, cv_connexion, cv_rejoindre,
   cv_reprise, cv_calendrier, cv_resultat, cv_classe, cv_deconnexion, cv_effacer_moi.
   Rien ne se perd : une partie est gardée sur l'appareil à chaque geste, et un résultat
   attend dans l'appareil tant que la base ne l'a pas reçu (envoi différé). */
(function () {
  "use strict";
  var CV = window.CV, esc = CV.esc, racine = document.getElementById("app");
  var UN_JOUR = 86400000, TRENTE_JOURS = 30 * UN_JOUR;
  var params = new URLSearchParams(location.search);
  var codeLien = (params.get("c") || params.get("classe") || "").toUpperCase().replace(/[^A-Z]/g, "").slice(0, 4);
  var session = lireSession(), etatCal = null, calId = CV.lire("calendrier", null), banques = {}, jeu = null, minuterie = null;

  // ------------------------------------------------------------ session et envoi différé
  function lireSession() {
    var s = CV.lire("session", null);
    if (!s || !s.jeton || !s.expire || s.expire < Date.now()) { CV.ecrire("session", null); return null; }
    return s;
  }
  function garderSession(r, garder) {
    session = { jeton: r.jeton, pseudo: r.pseudo, code: r.code_affiche, garder: !!garder, expire: Date.now() + (garder ? TRENTE_JOURS : UN_JOUR) };
    CV.ecrire("session", session);
  }
  function attente() { return CV.lire("attente", []) || []; }
  function envoyer() {
    var a = attente();
    if (!a.length || !session) return Promise.resolve(null);
    var r0 = a[0];
    return CV.rpc("cv_resultat", { p_jeton: session.jeton, p_calendrier: r0.calendrier, p_numero: r0.numero, p_niveau: r0.niveau, p_reussi: r0.reussi,
      p_etoiles: r0.etoiles, p_essais: r0.essais, p_coups_de_pouce: r0.coups, p_duree_s: r0.duree }).then(function (r) {
      if (r.reseau || r.horsService) return null;
      if (r.ok || /illisible|pas encore ouverte|pas dans ce calendrier/.test(r.message || "")) {
        // reçu (ou refusé pour de bon : on ne le renvoie pas sans fin)
        var b = attente(); b.shift(); CV.ecrire("attente", b);
        if (r.ok && r.etat && r0.calendrier === calId) etatCal = r.etat;
        return envoyer().then(function (x) { return x || r; });
      }
      if (/session a expiré/.test(r.message || "")) { CV.ecrire("session", null); session = null; }
      return r;
    });
  }
  window.addEventListener("online", function () { envoyer().then(function () { if (vue === "calendrier") calendrier(); }); });

  // ------------------------------------------------------------ affichage
  var vue = "";
  function afficher(v, html) {
    vue = v; if (jeu && v !== "jeu") { jeu.arreter(); jeu = null; }
    racine.innerHTML = html + CV.pied();
    var h = racine.querySelector("h1, h2"); if (h && v !== "calendrier") { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    window.scrollTo(0, 0);
  }
  function bandeau(sous) {
    return '<header class="haut"><div class="titre"><h1>Calendrier des vacances</h1><small>' + esc(sous || "") + "</small></div>" +
      (session ? '<button class="icone" data-act="compte" aria-label="Mon code et mon compte">' + CV.ICONE_COMPTE + "</button>" : "") +
      '<button class="icone" data-act="theme" aria-label="Changer l\'affichage clair ou obscur">' + CV.ICONE_THEME + "</button></header>";
  }
  function attendre(msg) { afficher("attente", bandeau() + '<p class="doux" role="status">' + esc(msg || "Un instant…") + "</p>"); }
  function erreur(msg, retour) {
    afficher("erreur", bandeau() + '<div class="message ko" role="alert">' + esc(msg) + '</div><div class="pile"><button class="btn large" data-act="' + (retour || "demarrer") + '">Réessayer</button></div>');
  }

  // ------------------------------------------------------------ démarrage
  function demarrer() {
    if (!CV.enLigne) return afficher("hors", bandeau() + CV.horsService());
    if (session) {
      attendre("Je retrouve ton calendrier…");
      return envoyer().then(function () { return CV.rpc("cv_reprise", { p_jeton: session.jeton }); }).then(function (r) {
        if (!r.ok) {
          if (r.reseau) return erreur(r.message);
          CV.ecrire("session", null); session = null; return demarrer();
        }
        return apresEntree(r);
      });
    }
    if (codeLien) {
      attendre();
      return CV.rpc("cv_calendrier_par_code", { p_code_calendrier: codeLien }).then(function (r) {
        if (!r.ok) return r.reseau ? erreur(r.message) : afficher("lien", bandeau() + '<div class="message ko" role="alert">' + esc(r.message) + "</div>" + carteConnexion());
        accueil(r);
      });
    }
    afficher("connexion", bandeau() + '<section class="carte"><p>Ton enseignant·e te donne le lien de ton calendrier. Si tu as déjà un code, entre-le ici.</p></section>' + carteConnexion());
  }
  function apresEntree(r) {
    var cals = r.calendriers || [];
    if (codeLien) {
      // le lien d'un calendrier : déjà dedans (même nom et mêmes dates) ? sinon, on propose de le rejoindre
      return CV.rpc("cv_calendrier_par_code", { p_code_calendrier: codeLien }).then(function (k) {
        if (!k.ok) return choisirCalendrier(cals);
        var deja = cals.filter(function (c) { return c.nom === k.nom && c.debut === k.debut && c.fin === k.fin; })[0];
        if (deja) { calId = deja.id; CV.ecrire("calendrier", calId); return calendrier(); }
        afficher("rejoindre", bandeau(session.pseudo) + '<section class="carte"><h2>Rejoindre « ' + esc(k.nom) + " » ?</h2><p>Avec " + esc(k.enseignant) +
          ", du " + esc(CV.dateLongue(k.debut)) + " au " + esc(CV.dateLongue(k.fin)) + '. Tu gardes ton code et tes autres calendriers.</p><div class="pile">' +
          '<button class="btn plein large" data-act="rejoindre">Rejoindre</button><button class="btn large" data-act="pas-rejoindre">Non, rester où je suis</button></div></section>');
        apresEntree.cals = cals;
      });
    }
    return choisirCalendrier(cals);
  }
  function choisirCalendrier(cals) {
    if (!cals.length) return afficher("vide", bandeau(session.pseudo) + '<section class="carte"><p>Tu n\'es encore dans aucun calendrier. Ouvre le lien donné par ton enseignant·e.</p></section>');
    var ici = cals.filter(function (c) { return c.id === calId; })[0];
    if (ici) return calendrier();
    if (cals.length === 1) { calId = cals[0].id; CV.ecrire("calendrier", calId); return calendrier(); }
    afficher("choix", bandeau(session.pseudo) + "<h2>Mes calendriers</h2><div class=\"a-faire\">" + cals.map(function (c) {
      return '<button class="case-carte" data-act="choisir" data-id="' + esc(c.id) + '"><span class="date"><b>' + CV.versDate(c.debut).getUTCDate() + "</b><span>" + esc(CV.jourCourt(c.debut)) +
        '</span></span><span class="quoi"><b>' + esc(c.nom) + "</b><span>du " + esc(CV.dateCourte(c.debut)) + " au " + esc(CV.dateCourte(c.fin)) + "</span></span></button>";
    }).join("") + "</div>");
  }

  // ------------------------------------------------------------ accueil par le lien, nouveau code, connexion
  var calLien = null;
  function accueil(k) {
    calLien = k;
    afficher("accueil", bandeau(k.nom + " · " + k.enseignant) + '<section class="carte"><h2>' + esc(k.nom) + '</h2><p class="doux">Avec ' + esc(k.enseignant) + ", du " +
      esc(CV.dateLongue(k.debut)) + " au " + esc(CV.dateLongue(k.fin)) + ".</p>" +
      '<ul class="liste"><li>Chaque jour, une case s\'ouvre : un mini-jeu de 10 minutes au plus.</li><li>Trois cases à faire au plus à la fois. Une case oubliée se rattrape : rien ne se perd.</li>' +
      "<li>Le corrigé expliqué s'ouvre trois jours après la case.</li><li>Aucun classement : chacun·e avance à son rythme, et toute la classe remplit la même jauge.</li></ul>" +
      '<div class="pile">' + (k.inscriptions_ouvertes ? '<button class="btn plein large" data-act="nouveau">Je suis nouveau ou nouvelle</button>' : '<p class="message info">Les inscriptions sont fermées : si tu as un code, entre-le.</p>') +
      '<button class="btn large" data-act="connexion">J\'ai déjà un code</button></div></section>');
  }
  function caseGarder(id) {
    return '<label class="case-a-cocher"><input type="checkbox" id="' + id + '"> C\'est mon téléphone : me garder connecté·e 30 jours (sinon, 1 jour).</label>';
  }
  function ecranNouveau(msg) {
    afficher("nouveau", bandeau() + '<section class="carte"><h2>Créer mon code</h2><label for="pseudo">Ton prénom ou un pseudo</label>' +
      '<input type="text" id="pseudo" maxlength="24" autocomplete="off"><p class="rappel">Jamais ton nom de famille. 2 à 24 caractères.</p>' + caseGarder("garder") +
      '<div class="message ko" role="alert">' + esc(msg || "") + '</div><div class="pile"><button class="btn plein large" data-act="creer">Créer mon code</button><button class="btn large" data-act="demarrer">Retour</button></div></section>');
  }
  function creer() {
    var p = (document.getElementById("pseudo").value || "").replace(/\s+/g, " ").trim(), garder = document.getElementById("garder").checked;
    if (p.length < 2 || p.length > 24) return ecranNouveau("Écris un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).");
    attendre("Je crée ton code…");
    CV.rpc("cv_inscription", { p_code_calendrier: codeLien, p_pseudo: p }).then(function (r) {
      if (!r.ok) return ecranNouveau(r.message);
      garderSession(r, garder); calId = r.calendrier; CV.ecrire("calendrier", calId); CV.ecrire("note", false);
      ecranCode();
    });
  }
  function ecranCode(msg) {
    afficher("code", bandeau() + '<section class="carte"><h2>Voici ton code, ' + esc(session.pseudo) + '</h2><div class="grand-code" aria-label="Ton code">' + esc(session.code) + "</div>" +
      "<p>Note-le dans ton cahier. Il suffit pour revenir, depuis n'importe quel téléphone ou ordinateur. Garde-le pour toi.</p>" +
      '<label for="chiffres">Pour vérifier, tape les 3 chiffres de ton code</label><input type="text" id="chiffres" inputmode="numeric" maxlength="4" autocomplete="off">' +
      '<div class="message ko" role="alert">' + esc(msg || "") + '</div><div class="pile"><button class="btn plein large" data-act="note">Je l\'ai noté</button></div></section>');
  }
  function note() {
    var v = document.getElementById("chiffres").value.trim().replace(/[oO]/g, "0").replace(/[iIlL]/g, "1");
    if (v !== session.code.split("-").pop()) return ecranCode("Ce ne sont pas les bons chiffres : regarde ton code et recopie-le.");
    CV.ecrire("note", true); calendrier();
  }
  function carteConnexion(msg, cls) {
    return '<section class="carte"><h2>J\'ai déjà un code</h2><label for="code">Ton code</label><input type="text" id="code" class="code-saisie" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="DOMINO-JOKER-482">' +
      '<p class="rappel">Majuscules, minuscules, espaces ou tirets : tout est accepté.</p>' + caseGarder("garder2") + '<div class="message ' + (cls || "ko") + '" role="alert">' + esc(msg || "") + "</div>" +
      '<div class="pile"><button class="btn plein large" data-act="entrer">Entrer</button>' + (codeLien ? '<button class="btn large" data-act="demarrer">Retour</button>' : "") + "</div></section>";
  }
  function ecranConnexion(msg, cls) { afficher("connexion", bandeau() + carteConnexion(msg, cls)); }
  function entrer() {
    var l = CV.lireCode(document.getElementById("code").value, 2), garder = document.getElementById("garder2").checked;
    if (l.erreur) return ecranConnexion(l.erreur, "info");
    attendre("Je vérifie ton code…");
    CV.rpc("cv_connexion", { p_code: l.code }).then(function (r) {
      if (!r.ok) return ecranConnexion(r.message);
      garderSession(r, garder); CV.ecrire("note", true);
      envoyer().then(function () { apresEntree(r); });
    });
  }

  // ------------------------------------------------------------ le calendrier
  var tables = {};
  function chargerBanques(themes) {
    return Promise.all(themes.map(function (t) {
      return CV.banque(t).then(function (b) {
        banques[t] = b;
        // un thème SQL : ses tables, montrées (repliables) à côté de chaque question
        if (CV.themeDe(b).langage === "sql" && !tables[t]) {
          return fetch("exercices/" + t + ".tables.json").then(function (r) { return r.ok ? r.json() : null; }).then(function (j) { tables[t] = j && j.tables; }, function () { tables[t] = null; });
        }
      }, function () { banques[t] = null; });
    }));
  }
  function exercice(c) {
    var b = banques[c.theme]; if (!b || !c.rang) return null;
    var n = b.exercices.length; if (!n) return null;
    return { ex: b.exercices[(c.rang - 1) % n], revision: c.rang > n, langage: CV.themeDe(b).langage, titreTheme: CV.themeDe(b).titre || c.theme, tables: tables[c.theme] };
  }
  function calendrier() {
    if (!session) return demarrer();
    if (CV.lire("note", true) === false) return ecranCode();
    attendre("J'ouvre ton calendrier…");
    envoyer().then(function () { return CV.rpc("cv_calendrier", { p_jeton: session.jeton, p_calendrier: calId }); }).then(function (r) {
      if (!r.ok) {
        if (r.reseau && etatCal) return dessinerCalendrier(true);
        if (/expiré/.test(r.message || "")) { CV.ecrire("session", null); session = null; return ecranConnexion("Ta session a expiré : entre de nouveau ton code.", "info"); }
        if (/pas dans ce calendrier/.test(r.message || "")) { CV.ecrire("calendrier", null); calId = null; return demarrer(); }
        return erreur(r.message, "calendrier");
      }
      etatCal = r.etat; CV.ecrire("dernier-etat:" + calId, etatCal);
      return chargerBanques(etatCal.calendrier.themes || []).then(function () { dessinerCalendrier(false); });
    });
  }
  function resultatsCase(c) { var o = {}; (c.resultats || []).forEach(function (r) { o[r.niveau] = r; }); return o; }
  function enAttente(c) { return attente().filter(function (a) { return a.calendrier === calId && a.numero === c.numero; }); }
  function dessinerCalendrier(horsLigne) {
    var e = etatCal, cal = e.calendrier, s = e.score, cases = e.cases;
    var aFaire = cases.filter(function (c) { return c.etat === "ouverte" && !enAttente(c).length; });
    var nAtt = attente().length;
    var html = bandeau(session.pseudo + " · " + cal.nom) +
      (horsLigne ? '<div class="message info" role="status">Pas de réseau : voici ton calendrier tel qu\'il était à ta dernière visite.</div>' : "") +
      (nAtt ? '<div class="message info" role="status">' + nAtt + " résultat" + (nAtt > 1 ? "s attendent" : " attend") + ' sur ce téléphone : ' + (nAtt > 1 ? "ils partiront" : "il partira") + ' dès que le réseau revient. <button class="lien" data-act="renvoyer">Réessayer maintenant</button></div>' : "") +
      '<section class="carte" aria-label="Mon score"><div class="score">' +
      '<div class="tuile"><b>' + s.etoiles + "</b><span>étoiles</span></div>" +
      '<div class="tuile"><b>' + s.faites + "/" + cases.length + "</b><span>cases faites</span></div>" +
      '<div class="tuile"><b>' + s.jours_differents + "</b><span>jour" + (s.jours_differents > 1 ? "s différents" : " joué") + "</span></div></div>" +
      (s.rattrapees ? '<p class="doux mt">Et ' + s.rattrapees + " case" + (s.rattrapees > 1 ? "s rattrapées" : " rattrapée") + ".</p>" : "") + "</section>" +
      jauge(e.classe) +
      "<h2>À faire maintenant</h2><div class=\"a-faire\">" + (aFaire.length ? aFaire.map(carteCase).join("") : '<p class="doux">Rien à faire pour l\'instant. ' + prochaine(cases, e.aujourdhui) + "</p>") + "</div>" +
      '<h2>Le calendrier</h2><div class="grille">' + cases.map(function (c) { return tuile(c, e.aujourdhui); }).join("") + "</div>" +
      '<div class="legende"><span class="l-ouv">ouverte</span><span class="l-fai">faite</span><span class="l-cor">corrigé ouvert</span><span class="l-av">à venir</span></div>';
    afficher("calendrier", html);
    lancerDirect();
  }
  function jauge(k) {
    if (!k || k.affichage !== "jauge") return "";
    var objectif = Math.max(1, (k.eleves || 0) * (k.cases_du_calendrier || 0)), p = Math.min(100, Math.round(100 * (k.cases_faites || 0) / objectif));
    return '<section class="carte" id="jauge" aria-label="Toute la classe"><div class="entre"><b>Toute la classe</b><span class="direct">en direct</span></div>' +
      '<div class="jauge" role="img" aria-label="' + p + ' % du défi de la classe"><i style="width:' + p + '%"></i></div>' +
      '<p class="doux">' + k.cases_faites + " cases faites sur " + objectif + ", dont " + k.cases_faites_aujourdhui + " aujourd'hui. Chaque case faite fait avancer tout le monde.</p>" +
      '<p class="fictif">Aucun nom, aucun classement.</p></section>';
  }
  function lancerDirect() {
    clearInterval(minuterie);
    minuterie = setInterval(function () {
      if (vue !== "calendrier" || document.visibilityState !== "visible" || !session) return;
      CV.rpc("cv_classe", { p_jeton: session.jeton, p_calendrier: calId }).then(function (r) {
        if (r.ok && vue === "calendrier") { var j = document.getElementById("jauge"); if (j) j.outerHTML = jauge(r.classe); }
      });
    }, 30000);
  }
  function prochaine(cases, auj) {
    var c = cases.filter(function (x) { return x.jour > auj; })[0];
    return c ? "La prochaine case s'ouvre " + esc(CV.dateLongue(c.jour)) + "." : "Le calendrier est fini : les cases se rejouent quand tu veux.";
  }
  function carteCase(c) {
    var x = exercice(c), d = CV.versDate(c.jour);
    return '<button class="case-carte" data-act="case" data-n="' + c.numero + '"><span class="date"><span>' + esc(CV.jourCourt(c.jour)) + "</span><b>" + d.getUTCDate() + "</b></span>" +
      '<span class="quoi"><b>' + (x ? esc(x.ex.titre) : "Case " + c.numero) + "</b><span>" + (x ? esc(CV.NOMS_TYPES[x.ex.type]) + " · " + esc(x.titreTheme) + " · " : "") +
      "10 min au plus<br>Corrigé le " + esc(CV.dateCourte(c.corrige_le)) + "</span></span></button>";
  }
  function tuile(c, auj) {
    var r = resultatsCase(c), att = enAttente(c).length, et = 0, rat = false;
    Object.keys(r).forEach(function (k) { if (r[k].dans_les_temps && r[k].etoiles > et) et = r[k].etoiles; if (r[k].reussi && !r[k].dans_les_temps) rat = true; });
    var marque = att ? "envoi…" : c.etat === "a_venir" ? "à venir" : c.etat === "ouverte" ? "à faire" : c.etat === "en_attente" ? "attend" : et ? CV.etoiles(et) : rat ? "rattrapée" : c.etat === "faite" ? "faite" : "corrigé";
    var nom = CV.dateLongue(c.jour) + " : " + { a_venir: "à venir", ouverte: "ouverte, à faire", en_attente: "attend son tour", faite: "faite", corrigee: "corrigé ouvert" }[c.etat];
    var cls = att ? "faite" : c.etat;
    return '<button class="jour ' + cls + (rat ? " rattrapee" : "") + (c.jour === auj ? " aujourdhui" : "") + '" data-act="case" data-n="' + c.numero + '" aria-label="' + esc(nom) + '">' +
      '<span class="j">' + esc(CV.jourCourt(c.jour)) + '</span><span class="n">' + CV.versDate(c.jour).getUTCDate() + '</span><span class="e">' + marque + "</span></button>";
  }
  function trouverCase(n) { return etatCal.cases.filter(function (c) { return c.numero === n; })[0]; }

  // ------------------------------------------------------------ la fenêtre d'une case
  function fenetreCase(n) {
    var c = trouverCase(n), x = exercice(c), r = resultatsCase(c), html, auj = etatCal.aujourdhui;
    if (c.etat === "a_venir") {
      var j = CV.ecart(auj, c.jour);
      html = "<h2>" + esc(CV.dateLongue(c.jour)) + "</h2><p>Cette case s'ouvre dans " + j + " jour" + (j > 1 ? "s" : "") + ".</p>";
    } else if (!x) {
      html = "<h2>" + esc(CV.dateLongue(c.jour)) + '</h2><div class="message ko" role="alert">L\'exercice de cette case (thème « ' + esc(c.theme) + " », n° " + c.rang +
        ") est introuvable. Préviens ton enseignant·e ; les autres cases marchent.</div>";
    } else {
      var cor = c.etat === "corrigee";
      html = "<h2>" + esc(x.ex.titre) + '</h2><p class="doux">' + esc(CV.dateLongue(c.jour)) + " · " + esc(CV.NOMS_TYPES[x.ex.type]) + " · " + esc(x.titreTheme) + (x.revision ? " · révision" : "") + "</p>" +
        '<p class="objectif">Objectif : ' + esc(x.ex.objectif) + "</p>" +
        (c.etat === "en_attente" ? '<p class="message info">Cette case attend son tour : fais d\'abord les plus anciennes. Tu peux quand même la jouer.</p>' : "") +
        (cor ? '<p class="message info">Le corrigé est ouvert. Tu peux encore jouer : c\'est un rattrapage, il compte comme case faite.</p>'
             : '<p class="doux">Choisis ton niveau. Un niveau suffit ; les autres sont des bonus. Corrigé le ' + esc(CV.dateLongue(c.corrige_le)) + ".</p>") +
        '<div class="niveaux">' + x.ex.niveaux.map(function (nv, i) {
          var rr = r[i + 1], partie = CV.lire(clePartie(c.numero, i + 1), null), att = enAttente(c).some(function (a) { return a.niveau === i + 1; });
          return '<button class="niveau" data-act="jouer" data-n="' + n + '" data-niv="' + (i + 1) + '"><span><b>' + CV.etoiles(i + 1, 3) + " " + CV.NOMS_NIVEAUX[i] + "</b><small>" +
            nv.items.length + " question" + (nv.items.length > 1 ? "s" : "") + ", environ " + nv.duree + " min" + (partie ? " · partie en cours : reprendre" : "") + "</small></span>" +
            (att ? '<span class="fait">envoi en attente</span>' : rr && rr.reussi ? '<span class="fait">' + (rr.dans_les_temps ? "réussi" : "rattrapé") + "</span>" : "") + "</button>";
        }).join("") + "</div>" +
        (cor ? '<div class="pile"><button class="btn large" data-act="corrige" data-n="' + n + '">Voir le corrigé expliqué</button></div>' : "");
    }
    ouvrirFeuille(html, "Case du " + CV.dateLongue(c.jour));
  }
  function ouvrirFeuille(html, titre) {
    fermer();
    var v = document.createElement("div");
    v.className = "voile"; v.setAttribute("data-act", "fermer");
    v.innerHTML = '<div class="feuille" role="dialog" aria-modal="true" aria-label="' + esc(titre) + '">' + html + '<div class="pile"><button class="btn large" data-act="fermer">Fermer</button></div></div>';
    document.body.appendChild(v);
    var b = v.querySelector(".niveau, .btn"); if (b) b.focus();
  }
  function fermer() { var v = document.querySelector(".voile"); if (v) v.remove(); }
  function clePartie(numero, niv) { return "partie:" + calId + ":" + numero + ":" + niv; }

  // ------------------------------------------------------------ jouer, terminer, envoyer
  function jouer(n, niv) {
    fermer();
    var c = trouverCase(n), x = exercice(c); if (!x) return;
    vue = "jeu"; racine.innerHTML = '<div id="jeu"></div>' + CV.pied();
    jeu = CV.jouer(document.getElementById("jeu"), {
      exercice: x.ex, niveau: niv, langage: x.langage, tables: x.tables, titreCase: CV.dateCourte(c.jour),
      sauvegarde: CV.lire(clePartie(n, niv), null),
      surSauver: function (g) { CV.ecrire(clePartie(n, niv), g); },
      surQuitter: function () { jeu = null; calendrier(); },
      surFin: function (r) { jeu = null; terminer(c, x, r); }
    });
  }
  function terminer(c, x, r) {
    CV.ecrire(clePartie(c.numero, r.niveau), null);
    var a = attente();
    a.push({ calendrier: calId, numero: c.numero, niveau: r.niveau, reussi: true, etoiles: r.etoiles, essais: r.essais, coups: r.coups, duree: r.duree });
    CV.ecrire("attente", a);
    var dlt = etatCal.aujourdhui < c.corrige_le;
    var min = Math.floor(r.duree / 60), sec = r.duree % 60;
    var proc = r.ratees === 0 ? "Tout juste du premier coup." : "Tu as corrigé " + r.ratees + " erreur" + (r.ratees > 1 ? "s" : "") + " en route : c'est en se trompant qu'on apprend.";
    function ecran(statut) {
      afficher("fin", bandeau() + '<section class="carte bravo"><h2>Case réussie</h2><div>' + CV.etoiles(r.niveau, 3) + "</div><p>" + proc + '</p><p class="doux">' +
        (r.coups ? r.coups + " coup" + (r.coups > 1 ? "s" : "") + " de pouce · " : "Sans coup de pouce · ") + min + " min " + sec + " s</p>" +
        '<p class="message ' + (statut === "ok" ? "ok" : "info") + '" role="status">' + (statut === "ok" ? "Résultat enregistré." : statut === "attente" ? "Résultat gardé sur ce téléphone : il partira dès que le réseau revient." : "Envoi en cours…") + "</p>" +
        (dlt ? '<p class="doux">Le corrigé expliqué s\'ouvre ' + esc(CV.dateLongue(c.corrige_le)) + ".</p>" : '<p class="doux">Rattrapage : la case compte comme faite.</p>') +
        '<div class="pile">' + (r.niveau < 3 ? '<button class="btn plein large" data-act="jouer" data-n="' + c.numero + '" data-niv="' + (r.niveau + 1) + '">Bonus : essayer le niveau ' + CV.NOMS_NIVEAUX[r.niveau].toLowerCase() + "</button>" : "") +
        '<button class="btn large" data-act="calendrier">Retour au calendrier</button></div></section>');
    }
    ecran("envoi");
    envoyer().then(function (rep) {
      if (vue !== "fin") return;
      ecran(attente().some(function (b) { return b.calendrier === calId && b.numero === c.numero && b.niveau === r.niveau; }) ? "attente" : "ok");
      if (rep && !rep.ok && !rep.reseau && /expiré/.test(rep.message || "")) ecranConnexion("Ta session a expiré : entre de nouveau ton code. Ton résultat attend sur ce téléphone.", "info");
    });
  }
  function corrige(n) {
    fermer();
    var c = trouverCase(n), x = exercice(c);
    if (!x || c.etat !== "corrigee") return calendrier();
    afficher("corrige", bandeau() + '<div class="jeu-haut"><button class="btn" data-act="calendrier">&#8592; Calendrier</button><span class="ou">' + esc(CV.dateCourte(c.jour)) + "</span></div>" +
      "<h1>Corrigé : " + esc(x.ex.titre) + '</h1><p class="objectif">Objectif : ' + esc(x.ex.objectif) + "</p>" + CV.corrige(x.ex, x.langage, x.tables));
  }

  // ------------------------------------------------------------ mon compte
  function compte() {
    var n = attente().length;
    ouvrirFeuille("<h2>" + esc(session.pseudo) + '</h2><p>Ton code :</p><div class="grand-code">' + esc(session.code) + '</div><p class="doux">Garde-le pour toi. Avec lui, tu reviens depuis n\'importe quel appareil.</p>' +
      (n ? '<p class="message info">' + n + " résultat" + (n > 1 ? "s attendent" : " attend") + " encore sur ce téléphone.</p>" : "") +
      '<div class="pile"><button class="btn large" data-act="changer">Changer de calendrier</button><button class="btn large" data-act="pas-moi">Ce n\'est pas moi (quitter sur cet appareil)</button>' +
      '<button class="btn large" data-act="effacer">Effacer mes données</button></div>', "Mon compte");
  }

  // ------------------------------------------------------------ événements
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest("[data-act]"); if (!el) return;
    var a = el.getAttribute("data-act");
    if (a === "fermer") { if (el.classList.contains("voile") && ev.target !== el) return; return fermer(); }
    if (a === "theme") return CV.basculerTheme();
    if (a === "demarrer") return demarrer();
    if (a === "nouveau") return ecranNouveau();
    if (a === "creer") return creer();
    if (a === "note") return note();
    if (a === "connexion") return ecranConnexion();
    if (a === "entrer") return entrer();
    if (a === "calendrier") { fermer(); return calendrier(); }
    if (a === "case") return fenetreCase(+el.getAttribute("data-n"));
    if (a === "jouer") return jouer(+el.getAttribute("data-n"), +el.getAttribute("data-niv"));
    if (a === "corrige") return corrige(+el.getAttribute("data-n"));
    if (a === "renvoyer") return envoyer().then(calendrier);
    if (a === "compte") return compte();
    if (a === "choisir") { calId = el.getAttribute("data-id"); CV.ecrire("calendrier", calId); return calendrier(); }
    if (a === "changer") { fermer(); return CV.rpc("cv_reprise", { p_jeton: session.jeton }).then(function (r) { if (r.ok) { calId = null; choisirCalendrier(r.calendriers || []); } }); }
    if (a === "rejoindre") {
      return CV.rpc("cv_rejoindre", { p_jeton: session.jeton, p_code_calendrier: codeLien }).then(function (r) {
        if (!r.ok) return erreur(r.message);
        calId = r.calendrier; CV.ecrire("calendrier", calId); calendrier();
      });
    }
    if (a === "pas-rejoindre") { codeLien = ""; return choisirCalendrier(apresEntree.cals || []); }
    if (a === "pas-moi") {
      if (attente().length && !window.confirm("Des résultats attendent encore sur ce téléphone. Quitter quand même ? Ils partiront quand tu reviendras avec ton code.")) return;
      fermer(); CV.rpc("cv_deconnexion", { p_jeton: session.jeton }); CV.ecrire("session", null); session = null;
      return ecranConnexion("Session fermée sur cet appareil. Pour revenir, tape ton code.", "info");
    }
    if (a === "effacer") {
      if (!window.confirm("Effacer ton compte, tes calendriers et tous tes résultats ? C'est définitif.")) return;
      return CV.rpc("cv_effacer_moi", { p_jeton: session.jeton }).then(function (r) {
        if (!r.ok) return erreur(r.message || "L'effacement n'a pas marché : réessaie.", "calendrier");
        fermer(); CV.ecrire("session", null); CV.ecrire("attente", null); CV.ecrire("calendrier", null); session = null;
        afficher("efface", bandeau() + '<div class="message ok" role="status">Ton compte et tes résultats sont effacés.</div>');
      });
    }
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") fermer();
    if (ev.key === "Enter" && ev.target.tagName === "INPUT") {
      var id = ev.target.id;
      if (id === "pseudo") { ev.preventDefault(); creer(); } else if (id === "chiffres") { ev.preventDefault(); note(); } else if (id === "code") { ev.preventDefault(); entrer(); }
    }
  });
  window.CV_ELEVE = { etat: function () { return etatCal; }, attente: attente };
  demarrer();
})();
