/* ═══════════════════════════════════════════════════════════════
   « Ma planque » (eleve/, T101b) : l'espace de l'élève dans le
   compte commun. Entrer avec son code ou en créer un, son avatar et
   sa loge, la boutique d'apparences (ses crédits), ses hauts faits,
   sa classe (avatars et hauts faits des camarades, jamais d'XP ni de
   rang), ses applications, ses crédits et ses codes.
   Le client : assets/compte-commun.js ; les morceaux de page :
   assets/compte-commun-pages.js. Architecte.
   Règles (décisions du 20/11) : aucun classement, aucun rang, aucun
   total ; l'XP reste cachée ; seul le solde de crédits est montré,
   et seulement à soi. Tout se range par pseudo ou par catalogue.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var O, P, CC, main, el;
  var cat = null, K = null;          // le catalogue et ses outils
  var fiche = null, classes = [];    // ce que le compte commun a rendu
  var essai = null;                  // l'avatar en cours d'essayage dans la loge
  var classeLien = null;             // le code de classe de l'adresse (?classe=…)
  var tabs = null;

  var GROUPES = [
    ['Identité', ['lignee', 'corps', 'visage', 'coiffure', 'marque']],
    ['Tenue', ['haut', 'bas', 'pieds', 'dos', 'yeux', 'tete', 'main']],
    ['Compagnon et décor', ['familier', 'fond', 'effet']],
    ['Gestes', ['attitude', 'succes', 'erreur']]
  ];
  var TEINTES = {
    corps: ['peau-1', 'peau-2', 'peau-3', 'peau-4', 'peau-5', 'peau-6'],
    autre: ['neon-cyan', 'neon-magenta', 'neon-vert', 'neon-jaune', 'neon-violet', 'neon-orange', 'gris', 'noir', 'blanc']
  };
  var NOMS_TEINTES = {
    'peau-1': 'Peau 1', 'peau-2': 'Peau 2', 'peau-3': 'Peau 3', 'peau-4': 'Peau 4', 'peau-5': 'Peau 5', 'peau-6': 'Peau 6',
    'neon-cyan': 'Néon cyan', 'neon-magenta': 'Néon magenta', 'neon-vert': 'Néon vert', 'neon-jaune': 'Néon jaune',
    'neon-violet': 'Néon violet', 'neon-orange': 'Néon orange', 'gris': 'Gris', 'noir': 'Noir', 'blanc': 'Blanc'
  };

  function lireClasseDeLAdresse() {
    try {
      var c = new URLSearchParams(location.search).get('classe');
      c = c ? CC.normaliserCode(c) : '';
      return /^[A-HJ-NP-Z]{4}$/.test(c) ? c : (c ? 'invalide' : null);
    } catch (e) { return null; }
  }

  /* ── Démarrage ─────────────────────────────────────────────────── */

  window.pagePlanque = function (racine, outils) {
    O = outils; el = O.el; P = window.PagesCompte; CC = window.CompteCommun;
    if (!P || !CC) {
      racine.appendChild(O.barreHaut('eleve'));
      racine.appendChild(el('div', { class: 'page' }, el('p', { class: 'alerte', role: 'alert' },
        'La planque n\'a pas pu se charger (assets/compte-commun.js manque). Recharge la page.')));
      return;
    }
    P.initialiser(O);
    CC.configurer(O.reglages());
    main = P.entete(racine, { page: 'eleve', couleur: '#A78BFA', graine: 23, invite: '> planque', titre: 'Ma planque',
      chapo: 'Ton avatar, tes hauts faits et ta classe. Un seul code pour toutes les applications.' });
    classeLien = lireClasseDeLAdresse();
    main.appendChild(el('p', { class: 'vide' }, 'Chargement…'));
    CC.catalogue().then(function (rep) {
      if (!rep || !rep.elements) {
        O.vider(main);
        main.appendChild(el('div', { class: 'alerte', role: 'alert' }, [el('p', null, el('strong', null, 'Le catalogue n\'a pas pu se charger')),
          el('p', { class: 'petit' }, (rep && rep.message) || 'Recharge la page dans un moment.')]));
        return;
      }
      cat = rep; K = P.outilsCatalogue(cat);
      if (CC.connecte()) recharger(); else accueil();
    });
  };

  /* ── 1. Entrer ou créer son code ──────────────────────────────── */

  function accueil(messageDepart) {
    O.vider(main);
    fiche = null;
    if (classeLien) main.appendChild(blocClasseDuLien());
    var grille = el('div', { class: 'cc-deux' });

    /* J'ai déjà un code */
    var code = P.champ({ etiquette: 'Ton code', aide: 'Par exemple CLAVIER-FRESQUE-482. Majuscules, espaces et tirets : comme tu veux.',
      exemple: 'MOT-MOT-123', capitales: true, max: 80, classe: 'cc-code-saisie' });
    var appareil1 = P.caseACocher('C\'est mon appareil', '(rester connecté·e 30 jours ; sinon, 1 jour)');
    var m1 = P.zoneMessage();
    var b1 = P.bouton('Entrer', { type: 'submit', classe: 'cc-principal' });
    var f1 = P.formulaire([code, appareil1, b1, m1], function () {
      var v = code.input.value;
      if (!CC.normaliserCode(v)) { P.message(m1, 'Écris ton code.', 'erreur'); code.input.focus(); return; }
      P.occupe(b1, true);
      CC.entrer(v, { appareil: appareil1.input.checked }).then(function (rep) {
        P.occupe(b1, false);
        if (!rep.ok) { P.message(m1, rep.message, 'erreur'); code.input.focus(); return; }
        apresEntree(rep.fiche);
      });
    });
    grille.appendChild(P.carte('J\'ai déjà un code', [f1], { id: 'titre-entrer' }));

    /* Je suis nouveau ou nouvelle */
    var pseudo = P.champ({ etiquette: 'Ton prénom ou un pseudo', aide: 'De 2 à 24 caractères. Jamais ton nom de famille.', max: 24, autocomplete: 'nickname' });
    var appareil2 = P.caseACocher('C\'est mon appareil', '(rester connecté·e 30 jours ; sinon, 1 jour)');
    var m2 = P.zoneMessage();
    var b2 = P.bouton('Créer mon code', { type: 'submit', classe: 'cc-principal' });
    var f2 = P.formulaire([pseudo, appareil2, b2, m2], function () {
      var v = CC.nettoyerPseudo(pseudo.input.value);
      if (!v) { P.message(m2, 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).', 'erreur'); pseudo.input.focus(); return; }
      P.occupe(b2, true);
      CC.creer(v, { appareil: appareil2.input.checked }).then(function (rep) {
        P.occupe(b2, false);
        if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
        montrerCode(rep.code_affiche, rep.fiche);
      });
    });
    grille.appendChild(P.carte('Je suis nouveau ou nouvelle', [
      el('p', { class: 'petit' }, 'Tu reçois un code. Il te servira dans toutes les applications du site.'), f2], { id: 'titre-creer' }));
    main.appendChild(grille);

    if (messageDepart) main.insertBefore(el('p', { class: 'cc-message cc-info', role: 'status' }, messageDepart), main.firstChild);
    var d = CC.demo();
    if (d) main.appendChild(blocEssaiDemo(d, code.input));
  }

  function blocClasseDuLien() {
    var zone = el('div', { class: 'cc-carte cc-classe-lien' }, el('p', { class: 'vide' }, 'Je cherche la classe…'));
    if (classeLien === 'invalide') {
      O.vider(zone);
      zone.appendChild(el('p', null, 'Ce lien de classe n\'est pas complet : un code de classe a 4 lettres. Demande le lien à ton enseignant·e.'));
      return zone;
    }
    CC.classeParCode(classeLien).then(function (rep) {
      O.vider(zone);
      if (!rep.ok) { zone.appendChild(el('p', null, rep.message)); classeLien = null; return; }
      zone.appendChild(el('p', { class: 'cc-surtitre' }, 'Lien de classe'));
      zone.appendChild(el('p', { class: 'cc-classe-nom' }, rep.nom));
      zone.appendChild(el('p', null, 'Avec ' + rep.enseignant + '. ' + (rep.ouverte
        ? 'Entre avec ton code, ou crée-le : tu rejoindras la classe juste après.'
        : 'Les inscriptions sont fermées pour l\'instant : demande à ton enseignant·e de les ouvrir.')));
    });
    return zone;
  }

  function blocEssaiDemo(d, champCode) {
    var liste = el('ul', { class: 'cc-essais' }, d.eleves.map(function (x) {
      var b = el('button', { type: 'button', class: 'cc-lien-bouton' }, [el('span', { class: 'cc-code' }, x.code), ' (' + x.pseudo + ')']);
      b.addEventListener('click', function () { champCode.value = x.code; champCode.focus(); });
      return el('li', null, b);
    }));
    return el('details', { class: 'cc-carte cc-essai' }, [
      el('summary', null, 'Pour essayer : des codes de démonstration'),
      el('p', { class: 'petit' }, 'Clique sur un code pour le mettre dans le champ, puis sur « Entrer ». Classes d\'essai : ajoute ?classe=TEST ou ?classe=ESSA à l\'adresse.'),
      liste
    ]);
  }

  /* Le code, montré en grand une fois ; on retape ses 3 chiffres pour être sûr·e de l'avoir noté */
  function montrerCode(codeAffiche, f) {
    O.vider(main);
    var chiffres = (codeAffiche.match(/(\d{3})$/) || [])[1] || '';
    var saisie = P.champ({ etiquette: 'Retape les 3 chiffres de ton code', inputmode: 'numeric', max: 3, classe: 'cc-chiffres', autocomplete: 'off' });
    var m = P.zoneMessage();
    var b = P.bouton('C\'est noté', { type: 'submit', classe: 'cc-principal' });
    var titre = el('h2', { class: 'cc-carte-titre', tabindex: '-1' }, 'Voici ton code');
    var form = P.formulaire([saisie, b, m], function () {
      var v = saisie.input.value.replace(/\D/g, '');
      if (v !== chiffres) { P.message(m, 'Ce ne sont pas les bons chiffres : regarde ton code et recopie-le dans ton cahier.', 'erreur'); saisie.input.focus(); return; }
      apresEntree(f);
    });
    main.appendChild(el('section', { class: 'cc-carte cc-ton-code' }, [
      titre,
      el('p', { class: 'cc-code cc-code-grand' }, codeAffiche),
      el('p', null, [el('strong', null, 'Note-le dans ton cahier.'), ' C\'est lui qui te fait revenir, depuis n\'importe quel appareil. Ne le donne à personne.']),
      form
    ]));
    titre.focus();
  }

  /* Après l'entrée : rejoindre la classe du lien, puis la planque */
  function apresEntree(f) {
    fiche = f;
    if (classeLien && classeLien !== 'invalide') {
      var c = classeLien;
      classeLien = null;
      try { history.replaceState(null, '', location.pathname + location.hash); } catch (e) { /* sans importance */ }
      CC.rejoindre(c).then(function (rep) {
        P.annoncer(rep.message, rep.ok ? 'ok' : 'erreur');
        recharger(rep.ok ? null : rep.message);
      });
      return;
    }
    recharger();
  }

  function recharger(alerte) {
    Promise.all([CC.reprendre(), CC.maClasse()]).then(function (r) {
      if (!r[0].ok) { accueil(r[0].sans_session ? (r[0].message || '') : r[0].message); return; }
      fiche = r[0].fiche;
      classes = r[1].ok ? r[1].classes : [];
      planque(alerte);
    });
  }

  /* ── 2. La planque ─────────────────────────────────────────────── */

  function planque(alerte) {
    O.vider(main);
    essai = JSON.parse(JSON.stringify(fiche.avatar || { v: 1, porte: {}, teintes: {} }));
    completerObligatoires(essai);

    var avatar = el('div', { class: 'cc-avatar-cadre' });
    CC.dessinerAvatar(avatar, fiche.avatar, { etat: 'lobby', taille: 'grand', catalogue: cat, pseudo: fiche.pseudo });
    var titre = el('h2', { class: 'cc-salut', tabindex: '-1' }, 'Salut, ' + fiche.pseudo);
    var sortir = P.bouton('Me déconnecter', { classe: 'cc-discret' });
    sortir.addEventListener('click', function () {
      CC.quitter().then(function () { accueil('Tu es déconnecté·e. À bientôt !'); });
    });
    var tete = el('section', { class: 'cc-tete' }, [
      avatar,
      el('div', { class: 'cc-tete-texte' }, [
        titre,
        el('p', { class: 'cc-solde' }, [el('span', { class: 'cc-solde-nombre' }, String(fiche.credits)), ' crédits à dépenser en apparences']),
        classes.length ? el('p', { class: 'petit' }, classes.map(function (c) { return c.nom; }).join(' · ')) : null,
        sortir
      ])
    ]);
    main.appendChild(tete);
    if (alerte) main.appendChild(el('p', { class: 'cc-message cc-erreur', role: 'alert' }, alerte));
    if (fiche.pseudo_provisoire) main.appendChild(blocPseudoProvisoire());

    tabs = P.onglets([
      { id: 'loge', nom: 'Ma loge', quandChoisi: remplirLoge },
      { id: 'boutique', nom: 'Boutique', quandChoisi: remplirBoutique },
      { id: 'hauts-faits', nom: 'Hauts faits', quandChoisi: remplirHautsFaits },
      { id: 'classe', nom: 'Ma classe', quandChoisi: remplirClasse },
      { id: 'applications', nom: 'Applications', quandChoisi: remplirApplications },
      { id: 'credits', nom: 'Crédits et codes', quandChoisi: remplirCredits }
    ], { etiquette: 'Ma planque' });
    main.appendChild(tabs.barre);
    main.appendChild(tabs.panneaux);
    tabs.choisir(tabs.depart);
    titre.focus();
  }

  function blocPseudoProvisoire() {
    var c = P.champ({ etiquette: 'Ton prénom ou un pseudo', aide: 'De 2 à 24 caractères. Jamais ton nom de famille.', max: 24, valeur: '' });
    var m = P.zoneMessage();
    return P.carte('Choisis ton pseudo', [
      el('p', null, 'Ton compte vient d\'une autre application : choisis le prénom ou le pseudo que verront tes camarades.'),
      P.formulaire([c, P.bouton('Garder ce pseudo', { type: 'submit', classe: 'cc-principal' }), m], function () {
        CC.renommer(c.input.value).then(function (rep) {
          if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
          recharger();
        });
      })
    ], { classe: 'cc-important' });
  }

  /* ── 2a. La loge : porter ce qu'on a ───────────────────────────── */

  function possede(e) { return e.acces === 'libre' ? e.actif : fiche.elements.indexOf(e.id) >= 0; }
  function compatible(e, avatar) { return !e.lignees || e.lignees.indexOf(avatar.porte.lignee) >= 0; }
  function emplacement(id) { return cat.emplacements.filter(function (m) { return m.id === id; })[0]; }
  function elementsDe(empl) { return cat.elements.filter(function (e) { return e.emplacement === empl; }); }

  function completerObligatoires(a) {
    a.porte = a.porte || {};
    a.teintes = a.teintes || {};
    cat.emplacements.forEach(function (m) {
      if (m.obligatoire && !a.porte[m.id]) {
        var e = elementsDe(m.id).filter(function (x) { return x.acces === 'libre' && x.actif; })[0];
        if (e) a.porte[m.id] = e.id;
      }
    });
  }

  function remplirLoge(panneau) {
    O.vider(panneau);
    var apercu = el('div', { class: 'cc-avatar-cadre cc-apercu' });
    function redessiner() { CC.dessinerAvatar(apercu, essai, { etat: 'repos', taille: 'grand', catalogue: cat, pseudo: fiche.pseudo }); }
    redessiner();
    var m = P.zoneMessage();
    var enregistrer = P.bouton('Porter cet avatar', { classe: 'cc-principal' });
    var annuler = P.bouton('Revenir à mon avatar', { classe: 'cc-discret' });
    enregistrer.addEventListener('click', function () {
      P.occupe(enregistrer, true);
      CC.porter(essai).then(function (rep) {
        P.occupe(enregistrer, false);
        if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
        fiche.avatar = rep.avatar;
        P.message(m, 'C\'est porté.', 'ok');
        var grand = main.querySelector('.cc-tete .cc-avatar-cadre');
        if (grand) CC.dessinerAvatar(grand, fiche.avatar, { etat: 'lobby', taille: 'grand', catalogue: cat, pseudo: fiche.pseudo });
      });
    });
    annuler.addEventListener('click', function () {
      essai = JSON.parse(JSON.stringify(fiche.avatar));
      completerObligatoires(essai);
      remplirLoge(panneau);
    });

    var choix = el('div', { class: 'cc-loge-choix' });
    GROUPES.forEach(function (g) {
      var fs = el('fieldset', { class: 'cc-groupe' }, el('legend', null, g[0]));
      g[1].forEach(function (eid) {
        var m2 = emplacement(eid);
        if (!m2) return;
        var dispo = elementsDe(eid).filter(function (e) { return possede(e) && compatible(e, essai); });
        if (!dispo.length && !m2.obligatoire) return;
        var id = P.idUnique('loge');
        var sel = el('select', { id: id, class: 'cc-select' });
        if (!m2.obligatoire) sel.appendChild(el('option', { value: '' }, 'Rien'));
        dispo.forEach(function (e) {
          sel.appendChild(el('option', { value: e.id, selected: essai.porte[eid] === e.id ? true : null }, e.nom));
        });
        sel.addEventListener('change', function () {
          if (sel.value) essai.porte[eid] = sel.value; else delete essai.porte[eid];
          if (eid === 'lignee') {
            /* Une autre lignée : on retire ce qui ne va pas avec elle */
            Object.keys(essai.porte).forEach(function (k) {
              var e = K.elt(essai.porte[k]);
              if (e && !compatible(e, essai)) delete essai.porte[k];
            });
            completerObligatoires(essai);
            remplirLoge(panneau);
            return;
          }
          majTeinte();
          redessiner();
        });
        var ligne = el('div', { class: 'cc-ligne-loge' }, [el('label', { for: id }, m2.nom), sel]);
        var zoneTeinte = el('span', { class: 'cc-teinte' });
        ligne.appendChild(zoneTeinte);
        function majTeinte() {
          O.vider(zoneTeinte);
          var e = K.elt(essai.porte[eid]);
          if (!e || !e.teintable) { delete essai.teintes[eid]; return; }
          var tid = P.idUnique('teinte');
          var ts = el('select', { id: tid, class: 'cc-select cc-select-teinte' }, [el('option', { value: '' }, 'Teinte d\'origine')]
            .concat((eid === 'corps' ? TEINTES.corps : TEINTES.autre).map(function (t) {
              return el('option', { value: t, selected: essai.teintes[eid] === t ? true : null }, NOMS_TEINTES[t]);
            })));
          ts.addEventListener('change', function () {
            if (ts.value) essai.teintes[eid] = ts.value; else delete essai.teintes[eid];
            redessiner();
          });
          zoneTeinte.appendChild(el('label', { for: tid, class: 'invisible' }, 'Teinte : ' + m2.nom));
          zoneTeinte.appendChild(ts);
        }
        majTeinte();
        fs.appendChild(ligne);
      });
      if (fs.children.length > 1) choix.appendChild(fs);
    });

    panneau.appendChild(el('div', { class: 'cc-loge' }, [
      el('div', { class: 'cc-loge-apercu' }, [apercu, el('div', { class: 'cc-actions' }, [enregistrer, annuler]), m]),
      el('div', null, [
        el('p', { class: 'petit' }, 'Tout ce qui sert à te reconnaître (lignée, corps, visage, coiffure, marques) est gratuit. Le reste se gagne avec un haut fait ou se prend dans la boutique.'),
        choix
      ])
    ]));
  }

  /* ── 2b. La boutique : ce qui se prend avec des crédits ─────────── */

  function remplirBoutique(panneau) {
    O.vider(panneau);
    var ordre = cat.emplacements.map(function (m) { return m.id; });
    var aPrendre = cat.elements.filter(function (e) { return e.acces === 'credits' && e.actif && !possede(e); });
    var aGagner = cat.elements.filter(function (e) { return e.acces === 'haut_fait' && !possede(e); });
    var pris = cat.elements.filter(function (e) { return e.acces !== 'libre' && possede(e); });
    function trier(a, b) { return (ordre.indexOf(a.emplacement) - ordre.indexOf(b.emplacement)) || (a.ordre || 0) - (b.ordre || 0); }

    panneau.appendChild(el('p', { class: 'cc-intro' }, [
      'Tu as ', el('strong', null, fiche.credits + ' crédits'), '. Tu les gagnes en travaillant : une feuille de TD validée, un cours-quiz suivi jusqu\'au bout, une mission… ',
      'Un achat ne se rembourse pas, mais il ne se perd jamais.'
    ]));
    var m = P.zoneMessage();
    panneau.appendChild(m);

    var grille = el('ul', { class: 'cc-vitrine' });
    aPrendre.sort(trier).forEach(function (e) { grille.appendChild(articleBoutique(e, m)); });
    panneau.appendChild(el('h3', null, 'À prendre avec tes crédits'));
    panneau.appendChild(aPrendre.length ? grille : el('p', { class: 'vide' }, 'Tu as déjà tout ce qui se prend avec des crédits.'));

    if (aGagner.length) {
      panneau.appendChild(el('h3', null, 'À gagner avec un haut fait'));
      panneau.appendChild(el('p', { class: 'petit' }, 'Ces apparences ne s\'achètent pas : elles racontent ce que tu as fait.'));
      panneau.appendChild(el('ul', { class: 'cc-vitrine' }, aGagner.sort(trier).map(function (e) {
        var source = (cat.hauts_faits || []).filter(function (h) { return (h.recompenses || []).indexOf(e.id) >= 0; })[0];
        return el('li', { class: 'cc-article cc-a-gagner' }, [
          miniature(e),
          el('p', { class: 'cc-article-nom' }, e.nom),
          el('p', { class: 'cc-article-empl' }, (emplacement(e.emplacement) || {}).nom),
          el('p', { class: 'petit' }, source ? 'Se gagne avec : ' + source.nom + ' (' + K.app(source.application).nom + ')' : 'Se gagne avec un haut fait.')
        ]);
      })));
    }
    if (pris.length) {
      panneau.appendChild(el('h3', null, 'Déjà dans ta loge'));
      panneau.appendChild(el('ul', { class: 'cc-puces' }, pris.sort(trier).map(function (e) { return el('li', null, e.nom); })));
    }
  }

  function miniature(e) {
    var a = JSON.parse(JSON.stringify(fiche.avatar));
    a.porte = a.porte || {};
    a.porte[e.emplacement] = e.id;
    var d = el('div', { class: 'cc-avatar-cadre cc-mini' });
    CC.dessinerAvatar(d, a, { etat: 'repos', taille: 'petit', catalogue: cat, pseudo: fiche.pseudo });
    d.setAttribute('aria-label', 'Essai : ' + e.nom);
    return d;
  }

  function articleBoutique(e, m) {
    var ok = fiche.credits >= e.prix;
    var compat = compatible(e, fiche.avatar);
    var bouton = P.bouton('Prendre pour ' + e.prix + ' crédits', { inactif: !ok, classe: 'cc-principal' });
    var zone = el('div', { class: 'cc-confirmer' });
    bouton.addEventListener('click', function () {
      O.vider(zone);
      var oui = P.bouton('Oui, je le prends', { classe: 'cc-principal' });
      var non = P.bouton('Non', { classe: 'cc-discret' });
      non.addEventListener('click', function () { O.vider(zone); bouton.focus(); });
      oui.addEventListener('click', function () {
        P.occupe(oui, true);
        CC.acheter(e.id).then(function (rep) {
          if (!rep.ok) { P.occupe(oui, false); P.message(m, rep.message, 'erreur'); return; }
          fiche.credits = rep.credits;
          fiche.elements.push(e.id);
          P.annoncer('Débloqué : ' + e.nom, 'fier');
          recharger();
        });
      });
      zone.appendChild(el('p', null, 'Prendre « ' + e.nom + ' » pour ' + e.prix + ' crédits ?'));
      zone.appendChild(el('div', { class: 'cc-actions' }, [oui, non]));
      oui.focus();
    });
    return el('li', { class: 'cc-article' }, [
      miniature(e),
      el('p', { class: 'cc-article-nom' }, e.nom),
      el('p', { class: 'cc-article-empl' }, (emplacement(e.emplacement) || {}).nom),
      !compat ? el('p', { class: 'petit' }, 'Ne va qu\'avec certaines lignées.') : null,
      ok ? null : el('p', { class: 'petit' }, 'Encore ' + (e.prix - fiche.credits) + ' crédits à gagner.'),
      bouton, zone
    ]);
  }

  /* ── 2c. Les hauts faits : une collection, jamais un score ─────── */

  function appsDeMesClasses() {
    var s = {};
    classes.forEach(function (c) { (c.applications || []).forEach(function (a) { s[a] = true; }); });
    return s;
  }

  function remplirHautsFaits(panneau) {
    O.vider(panneau);
    var gagnes = {};
    fiche.hauts_faits.forEach(function (g) { gagnes[g.application + '/' + g.id] = g; });
    var mesApps = appsDeMesClasses();
    mesApps.commun = true;
    fiche.hauts_faits.forEach(function (g) { mesApps[g.application] = true; });
    panneau.appendChild(el('p', { class: 'cc-intro' }, 'Ce que tu as fait, rangé par application. Ceux qui restent sont en gris, avec ce qu\'il faut faire. Un haut fait ne se perd jamais.'));
    cat.applications.forEach(function (a) {
      if (!mesApps[a.id]) return;
      var hs = (cat.hauts_faits || []).filter(function (h) { return h.application === a.id && (h.actif || gagnes[a.id + '/' + h.id]); });
      if (!hs.length) return;
      var section = el('section', { class: 'cc-hf-app' }, el('h3', null, a.id === 'commun' ? 'Le site et ton enseignant·e' : a.nom));
      P.CATEGORIES.forEach(function (c) {
        var dans = hs.filter(function (h) { return h.categorie === c[0]; });
        if (!dans.length) return;
        section.appendChild(el('h4', null, c[1]));
        section.appendChild(el('ul', { class: 'cc-hf-liste' }, dans.map(function (h) {
          var g = gagnes[a.id + '/' + h.id];
          return el('li', { class: 'cc-hf' + (g ? ' cc-hf-gagne' : ' cc-hf-eteint') }, [
            el('span', { class: 'cc-hf-icone', 'aria-hidden': 'true' }, g ? '★' : '☆'),
            el('span', { class: 'cc-hf-texte' }, [
              el('strong', null, h.nom || (g ? 'Haut fait secret' : 'Secret')),
              el('span', { class: 'invisible' }, g ? ' (gagné)' : ' (pas encore)'),
              el('br'),
              el('span', { class: 'petit' }, g
                ? 'Gagné le ' + P.date(g.gagne_le) + (h.description ? '. ' + h.description : '')
                : h.secret ? 'Indice : ' + (h.indice || '…') : (h.accord === 'enseignant' ? 'Accordé par ton enseignant·e. ' : 'Pour l\'avoir : ') + (h.description || ''))
            ])
          ]);
        })));
      });
      panneau.appendChild(section);
    });
  }

  /* ── 2d. Ma classe : les camarades, sans aucun nombre ──────────── */

  function remplirClasse(panneau) {
    O.vider(panneau);
    if (!classes.length) {
      panneau.appendChild(el('p', { class: 'cc-intro' }, 'Tu n\'es dans aucune classe pour l\'instant. Ton enseignant·e te donne un lien, un QR code ou un code de classe de 4 lettres.'));
    } else {
      panneau.appendChild(el('p', { class: 'cc-intro' }, 'Les avatars et les hauts faits de ta classe, et seulement d\'elle. Personne ne voit tes crédits.'));
    }
    classes.forEach(function (c) {
      var sec = el('section', { class: 'cc-classe' }, [el('h3', null, c.nom), el('p', { class: 'petit' }, 'Avec ' + c.enseignant)]);
      sec.appendChild(el('ul', { class: 'cc-camarades' }, (c.camarades || []).map(function (k) {
        var av = el('div', { class: 'cc-avatar-cadre cc-moyen' });
        CC.dessinerAvatar(av, k.avatar, { etat: 'repos', taille: 'moyen', catalogue: cat, pseudo: k.pseudo });
        var hfs = (k.hauts_faits || []).map(function (h) { return K.nomHf(h.application, h.id); });
        return el('li', { class: 'cc-camarade' + (k.moi ? ' cc-moi' : '') }, [
          av,
          el('p', { class: 'cc-camarade-nom' }, [k.pseudo, k.moi ? el('span', { class: 'cc-badge' }, 'toi') : null]),
          hfs.length ? el('details', { class: 'cc-camarade-hf' }, [el('summary', null, 'Ses hauts faits'),
            el('ul', null, hfs.map(function (n) { return el('li', null, n); }))]) : el('p', { class: 'petit' }, 'Pas encore de haut fait.')
        ]);
      })));
      panneau.appendChild(sec);
    });
    /* Rejoindre une autre classe */
    var code = P.champ({ etiquette: 'Code de classe', aide: '4 lettres, sur le lien ou au tableau.', max: 12, capitales: true, classe: 'cc-code-saisie' });
    var m = P.zoneMessage();
    panneau.appendChild(P.carte('Rejoindre une classe', [P.formulaire([code, P.bouton('Rejoindre', { type: 'submit' }), m], function () {
      CC.rejoindre(code.input.value).then(function (rep) {
        if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
        P.annoncer(rep.message, 'ok');
        recharger();
      });
    })], { niveau: 'h3' }));
  }

  /* ── 2e. Mes applications ───────────────────────────────────────── */

  function remplirApplications(panneau) {
    O.vider(panneau);
    var mesApps = appsDeMesClasses();
    var toutes = cat.applications.filter(function (a) { return a.id !== 'commun'; });
    function liste(apps) {
      return el('ul', { class: 'cc-apps' }, apps.map(function (a) {
        return el('li', { class: 'cc-app' }, a.adresse
          ? el('a', { href: a.adresse }, [el('strong', null, a.nom), el('span', { class: 'petit' }, ' Ouvrir')])
          : el('span', null, [el('strong', null, a.nom), el('span', { class: 'petit' }, ' Bientôt')]));
      }));
    }
    var deClasse = toutes.filter(function (a) { return mesApps[a.id]; });
    var autres = toutes.filter(function (a) { return !mesApps[a.id]; });
    panneau.appendChild(el('p', { class: 'cc-intro' }, 'Ton code marche dans chacune. Sur cet appareil, elles te reconnaissent toutes seules.'));
    if (deClasse.length) { panneau.appendChild(el('h3', null, 'Celles de ta classe')); panneau.appendChild(liste(deClasse)); }
    panneau.appendChild(el('h3', null, deClasse.length ? 'Les autres' : 'Les applications'));
    panneau.appendChild(liste(autres));
  }

  /* ── 2f. Crédits et codes ──────────────────────────────────────── */

  function libelleJournal(j) {
    if (j.evenement === 'achat') return 'Apparence prise dans la boutique';
    if (j.evenement === 'attribution') return 'De ton enseignant·e' + (j.motif ? ' : ' + j.motif : '');
    if (j.evenement === 'haut_fait') return 'Haut fait (' + K.app(j.application).nom + ')';
    return j.nom || j.evenement;
  }

  function remplirCredits(panneau) {
    O.vider(panneau);
    panneau.appendChild(el('p', { class: 'cc-intro' }, [
      'Ton solde : ', el('strong', null, fiche.credits + ' crédits'), '. C\'est le seul nombre de ta planque, et toi seul·e le vois.']));
    if (CC.mode() === 'demo') panneau.appendChild(blocSimulation());
    var journal = fiche.journal || [];
    panneau.appendChild(el('h3', null, 'D\'où viennent tes crédits'));
    panneau.appendChild(journal.length ? el('ul', { class: 'cc-journal' }, journal.map(function (j) {
      return el('li', null, [el('span', { class: 'cc-journal-date' }, P.date(j.le)), el('span', { class: 'cc-journal-quoi' }, libelleJournal(j)),
        el('span', { class: 'cc-journal-nb' + (j.credits < 0 ? ' cc-moins' : '') }, (j.credits > 0 ? '+' : '−') + Math.abs(j.credits))]);
    })) : el('p', { class: 'vide' }, 'Rien encore : valide une feuille de TD en ligne ou suis un cours-quiz jusqu\'au bout.'));

    /* Les codes */
    panneau.appendChild(el('h3', null, 'Mes codes'));
    var montrer = caseMontrer();
    var codes = el('ul', { class: 'cc-codes' }, fiche.codes.map(function (c) {
      return el('li', null, [el('span', { class: 'cc-code cc-masquable' }, c.code_affiche),
        el('span', { class: 'petit' }, ' ' + (c.application === 'commun' ? 'né sur le site' : 'de ' + K.app(c.application).nom) + (c.principal ? ', principal' : ''))]);
    }));
    codes.classList.add('cc-masque');
    montrer.input.addEventListener('change', function () { codes.classList.toggle('cc-masque', !montrer.input.checked); });
    panneau.appendChild(montrer);
    panneau.appendChild(codes);

    var autre = P.champ({ etiquette: 'Un autre de tes codes (d\'une autre application)', max: 80, capitales: true, classe: 'cc-code-saisie' });
    var m1 = P.zoneMessage();
    panneau.appendChild(P.carte('Ajouter un autre de mes codes', [
      el('p', { class: 'petit' }, 'Tes deux comptes n\'en font plus qu\'un : rien n\'est perdu, une activité faite deux fois ne compte qu\'une fois.'),
      P.formulaire([autre, P.bouton('Ajouter ce code', { type: 'submit' }), m1], function () {
        CC.lierCode(autre.input.value).then(function (rep) {
          P.message(m1, rep.message, rep.ok ? 'ok' : 'erreur');
          if (rep.ok) { fiche = rep.fiche; setTimeout(function () { recharger(); }, 900); }
        });
      })], { niveau: 'h3' }));

    var ps = P.champ({ etiquette: 'Nouveau prénom ou pseudo', aide: 'De 2 à 24 caractères. Jamais ton nom de famille.', max: 24, valeur: fiche.pseudo });
    var m2 = P.zoneMessage();
    panneau.appendChild(P.carte('Changer de pseudo', [P.formulaire([ps, P.bouton('Changer', { type: 'submit' }), m2], function () {
      CC.renommer(ps.input.value).then(function (rep) {
        if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
        recharger();
      });
    })], { niveau: 'h3' }));

    var conf = P.champ({ etiquette: 'Écris EFFACER pour confirmer', max: 10, capitales: true });
    var partout = P.caseACocher('Effacer aussi mes comptes des applications qui le permettent');
    var m3 = P.zoneMessage();
    panneau.appendChild(el('details', { class: 'cc-carte cc-danger' }, [
      el('summary', null, 'Effacer mes données'),
      el('p', null, 'Ton compte commun, ton avatar, tes hauts faits, tes crédits et tes codes nés sur le site sont effacés pour de bon. Ce n\'est pas réversible.'),
      P.formulaire([conf, partout, P.bouton('Effacer mes données', { type: 'submit', classe: 'cc-bouton-danger' }), m3], function () {
        CC.effacerMoi(conf.input.value, partout.input.checked).then(function (rep) {
          if (!rep.ok) { P.message(m3, rep.message, 'erreur'); return; }
          accueil(rep.message);
        });
      })
    ]));
  }

  function caseMontrer() { return P.caseACocher('Montrer mes codes', '(attention si l\'écran est projeté)'); }

  /* Démonstration seulement : faire comme si une page avait validé une activité */
  function blocSimulation() {
    var m = P.zoneMessage();
    var activites = [
      ['td', 'feuille_validee', 'td:poo-td1', 'une feuille de TD validée (TD 1 de POO)'],
      ['td', 'feuille_validee', 'td:boucles-td2', 'une feuille de TD validée (TD 2 : les boucles)'],
      ['quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files', 'un cours-quiz suivi jusqu\'au bout'],
      ['calendrier', 'mini_jeu_fait', 'cal:jour-01', 'un mini-jeu du calendrier']
    ];
    return el('details', { class: 'cc-carte cc-essai' }, [
      el('summary', null, 'Démonstration : faire comme si…'),
      el('p', { class: 'petit' }, 'En service, ce sont les pages des TD, de QuizzNSI et du calendrier qui le disent au compte commun, et jamais tes réponses.'),
      el('div', { class: 'cc-actions' }, activites.map(function (a) {
        var b = P.bouton('…' + a[3]);
        b.addEventListener('click', function () {
          CC.evenementPage(a[0], a[1], a[2]).then(function (rep) {
            P.message(m, rep.message + (rep.credits_gagnes ? ' (+' + rep.credits_gagnes + ' crédits)' : ''), rep.ok ? 'ok' : 'erreur');
            if (rep.credits_gagnes) {
              P.annoncer('+' + rep.credits_gagnes + ' crédits', 'fier');
              CC.reprendre().then(function (r) { if (r.ok) { fiche = r.fiche; var s = main.querySelector('.cc-solde-nombre'); if (s) s.textContent = String(fiche.credits); } });
            }
          });
        });
        return b;
      })),
      m
    ]);
  }
})();
