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
  var niveauDeClasse = null;         // le niveau de la classe du lien, s'il est connu (migration de T132e)
  var NIVEAUX = [];                  // les libellés des référentiels du site

  var A = null;                      // les apparences (identité, objets, familles)

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
    main = P.entete(racine, { page: 'eleve', puce: 'Élève', surTitre: ['compte commun'], titre: 'Ma planque',
      chapo: CC.applicationsBranchees() ? 'Ton avatar, tes hauts faits et ta classe. Un seul code pour toutes les applications.'
        : 'Ton avatar et ta classe, avec un seul code. Bientôt, ce code marchera aussi dans les applications du site.' });
    classeLien = lireClasseDeLAdresse();
    main.appendChild(el('p', { class: 'vide' }, 'Chargement…'));
    CC.catalogue().then(function (rep) {
      if (!rep || !rep.elements) {
        O.vider(main);
        main.appendChild(el('div', { class: 'alerte', role: 'alert' }, [el('p', null, el('strong', null, 'Le catalogue n\'a pas pu se charger')),
          el('p', { class: 'petit' }, (rep && rep.message) || 'Recharge la page dans un moment.')]));
        return;
      }
      cat = rep; K = P.outilsCatalogue(cat); A = rep.apparences;
      (CC.niveauActif() ? CC.niveaux() : Promise.resolve([])).then(function (n) {
        NIVEAUX = n;
        if (CC.connecte()) recharger(); else accueil();
      });
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
    var appareil1 = caseAppareil();
    var m1 = P.zoneMessage();
    var b1 = P.bouton('Entrer', { type: 'submit', classe: 'cc-principal' });
    var f1 = P.formulaire([code, appareil1, b1, m1], function () {
      var v = code.input.value;
      if (!CC.normaliserCode(v)) { P.message(m1, 'Écris ton code.', 'erreur'); code.input.focus(); return; }
      P.occupe(b1, true);
      CC.entrer(v, { appareil: appareil1 && appareil1.input.checked }).then(function (rep) {
        P.occupe(b1, false);
        if (!rep.ok) { P.message(m1, rep.message, 'erreur'); code.input.focus(); return; }
        apresEntree(rep.fiche);
      });
    });
    grille.appendChild(P.carte('J\'ai déjà un code', [f1], { id: 'titre-entrer' }));

    /* Je suis nouveau ou nouvelle */
    var pseudo = P.champ({ etiquette: 'Ton prénom ou un pseudo', aide: 'De 2 à 24 caractères. Jamais ton nom de famille.', max: 24, autocomplete: 'nickname' });
    var niveau = choixNiveau();
    var appareil2 = caseAppareil();
    var m2 = P.zoneMessage();
    var b2 = P.bouton('Créer mon code', { type: 'submit', classe: 'cc-principal' });
    var f2 = P.formulaire([pseudo, niveau, appareil2, b2, m2], function () {
      var v = CC.nettoyerPseudo(pseudo.input.value);
      if (CC.caractereSpecial(pseudo.input.value)) { P.message(m2, CC.MESSAGE_CARACTERE, 'erreur'); pseudo.input.focus(); return; }
      if (!v) { P.message(m2, 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).', 'erreur'); pseudo.input.focus(); return; }
      if (niveau && !niveau.select.value) { P.message(m2, 'Choisis ton niveau.', 'erreur'); niveau.select.focus(); return; }
      P.occupe(b2, true);
      CC.creer(v, { appareil: appareil2 && appareil2.input.checked, niveau: niveau ? niveau.select.value : null }).then(function (rep) {
        P.occupe(b2, false);
        if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
        montrerCode(rep.code_affiche, rep.fiche);
      });
    });
    grille.appendChild(P.carte('Je suis nouveau ou nouvelle', [
      el('p', { class: 'petit' }, CC.applicationsBranchees() ? 'Tu reçois un code. Il te servira dans toutes les applications du site.' : 'Tu reçois un code, qui te fait revenir ici depuis n\'importe quel appareil.'), f2], { id: 'titre-creer' }));
    main.appendChild(grille);

    if (messageDepart) main.insertBefore(el('p', { class: 'cc-message cc-info', role: 'status' }, messageDepart), main.firstChild);
    var d = CC.demo();
    if (d) main.appendChild(blocEssaiDemo(d, code.input));
  }

  /* « C'est mon téléphone » : sans objet en démonstration, où rien n'est gardé.
     Sinon, le compte reste ouvert dans cet onglet seulement (1 jour au plus). */
  function caseAppareil() {
    return CC.mode() === 'demo' ? null : P.caseACocher('C\'est mon téléphone', '(je reste connecté·e 30 jours ; sinon, seulement dans cet onglet)');
  }

  /* Le niveau, choisi à la création du code seulement (décision du 24/11, 11:34) ; ensuite, seul·e
     l'enseignant·e le change. Masqué tant que COMPTE_COMMUN_NIVEAU vaut false (migration de T132e). */
  function choixNiveau() {
    if (!CC.niveauActif() || !NIVEAUX.length) return null;
    var id = P.idUnique('niveau');
    var sel = el('select', { id: id, class: 'cc-select', required: true }, [el('option', { value: '' }, 'Choisis…')].concat(NIVEAUX.map(function (n) {
      return el('option', { value: n.id, selected: n.id === niveauDeClasse ? true : null }, n.libelle);
    })));
    var bloc = el('div', { class: 'cc-champ' }, [el('label', { for: id }, 'Ton niveau'),
      el('span', { class: 'cc-aide' }, niveauDeClasse ? 'Celui de ta classe. Ensuite, seul·e ton enseignant·e peut le changer.' : 'Ensuite, seul·e ton enseignant·e peut le changer.'), sel]);
    bloc.select = sel;
    return bloc;
  }
  function libelleNiveau(id) { var n = NIVEAUX.filter(function (x) { return x.id === id; })[0]; return n ? n.libelle : null; }

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
      if (rep.niveau && CC.niveauActif()) {
        niveauDeClasse = rep.niveau;
        var s = main.querySelector('select[id^=niveau]');
        if (s) s.value = rep.niveau;
      }
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
    var imprimer = P.bouton('Imprimer la carte de mon code', { classe: 'cc-discret' });
    imprimer.addEventListener('click', function () { imprimerCarte(f && f.pseudo, codeAffiche); });
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
      el('div', { class: 'cc-actions' }, [imprimer]),
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
    essai = copieAvatar(fiche.avatar);

    var avatar = el('div', { class: 'cc-avatar-cadre' });
    CC.dessinerAvatar(avatar, fiche.avatar, { etat: 'salue', taille: 'grand', pseudo: fiche.pseudo });
    var titre = el('h2', { class: 'cc-salut', tabindex: '-1' }, 'Salut, ' + fiche.pseudo);
    var sortir = P.bouton('Me déconnecter', { classe: 'cc-discret' });
    sortir.addEventListener('click', function () {
      CC.quitter().then(function () { accueil('Tu es déconnecté·e. À bientôt !'); });
    });
    /* « Ce n'est pas moi » : toujours visible, pour un appareil prêté ou partagé */
    var pasMoi = P.bouton('Ce n\'est pas moi', { classe: 'cc-discret' });
    pasMoi.addEventListener('click', function () {
      CC.quitter().then(function () { accueil('Ce compte est fermé sur cet appareil. Entre ton propre code, ou crée-le.'); });
    });
    var tete = el('section', { class: 'cc-tete' }, [
      avatar,
      el('div', { class: 'cc-tete-texte' }, [
        titre,
        el('p', { class: 'cc-solde' }, [el('span', { class: 'cc-solde-nombre' }, String(fiche.credits)), boutiqueOuverte() ? ' crédits à dépenser en apparences' : ' crédits (la boutique ouvre bientôt)']),
        classes.length ? el('p', { class: 'petit' }, classes.map(function (c) { return c.nom; }).join(' · ')) : null,
        CC.niveauActif() && fiche.niveau && libelleNiveau(fiche.niveau) ? el('p', { class: 'petit' }, 'Niveau : ' + libelleNiveau(fiche.niveau)) : null,
        el('div', { class: 'cc-actions' }, [pasMoi, sortir])
      ])
    ]);
    main.appendChild(tete);
    if (alerte) main.appendChild(el('p', { class: 'cc-message cc-erreur', role: 'alert' }, alerte));
    if (fiche.pseudo_provisoire) main.appendChild(blocPseudoProvisoire());

    tabs = P.onglets([
      { id: 'loge', nom: 'Mon avatar', quandChoisi: remplirLoge },
      { id: 'boutique', nom: 'Boutique', quandChoisi: remplirBoutique },
      { id: 'trophees', nom: 'Trophées', quandChoisi: remplirTrophees },
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

  function possede(e) { return e.acces === 'libre' ? e.actif !== false : fiche.elements.indexOf(e.id) >= 0; }
  function nomEmplacement(id) { var m = (A.emplacements || []).filter(function (x) { return x.id === id; })[0]; return m ? m.nom : id; }
  function copieAvatar(a) { return JSON.parse(JSON.stringify(a || A.defaut)); }

  /* Une liste déroulante de la loge */
  function choix(etiquette, options, valeur, quandChange) {
    var id = P.idUnique('loge');
    var sel = el('select', { id: id, class: 'cc-select' }, options.map(function (o) {
      return el('option', { value: String(o.id), selected: String(o.id) === String(valeur) ? true : null }, o.nom);
    }));
    sel.addEventListener('change', function () { quandChange(sel.value); });
    return el('div', { class: 'cc-ligne-loge' }, [el('label', { for: id }, etiquette), sel]);
  }
  function couleurs(groupe) {
    return (A.identite.couleurs[groupe] || []).map(function (c) { return { id: c.id, nom: c.id.charAt(0).toUpperCase() + c.id.slice(1) }; });
  }

  /* ── 2a. La loge : porter ce qu'on a ───────────────────────────── */

  function remplirLoge(panneau) {
    O.vider(panneau);
    var I = A.identite;
    var apercu = el('div', { class: 'cc-avatar-cadre cc-apercu' });
    function redessiner() { CC.dessinerAvatar(apercu, essai, { etat: 'repos', taille: 'grand', pseudo: fiche.pseudo }); }
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
        if (grand) CC.dessinerAvatar(grand, fiche.avatar, { etat: 'content', taille: 'grand', pseudo: fiche.pseudo });
      });
    });
    annuler.addEventListener('click', function () { essai = copieAvatar(fiche.avatar); remplirLoge(panneau); });
    function champ(cle) { return function (v) { essai[cle] = cle === 'teint' ? Number(v) : v; redessiner(); }; }
    function couleur(cle) { return function (v) { essai.couleurs = essai.couleurs || {}; essai.couleurs[cle] = v; redessiner(); }; }
    var c = essai.couleurs || {};

    var identite = el('fieldset', { class: 'cc-groupe' }, [el('legend', null, 'Ton allure'),
      choix('Lignée', I.lignee, essai.lignee, champ('lignee')),
      choix('Teint', I.teint, essai.teint, champ('teint')),
      choix('Corps', I.corps, essai.corps, champ('corps')),
      choix('Coiffure', I.coiffure, essai.coiffure, champ('coiffure')),
      choix('Cheveux', couleurs('cheveux'), essai.cheveux, champ('cheveux')),
      choix('Yeux', couleurs('yeux'), c.yeux, couleur('yeux'))
    ]);
    var fauteuil = P.caseACocher('Fauteuil roulant', '(une aide technique, toujours disponible)');
    fauteuil.input.checked = !!essai.fauteuil;
    fauteuil.input.addEventListener('change', function () { essai.fauteuil = fauteuil.input.checked; redessiner(); });
    identite.appendChild(fauteuil);

    var tenue = el('fieldset', { class: 'cc-groupe' }, [el('legend', null, 'Ta tenue'),
      choix('Haut', I.haut, essai.haut, champ('haut')),
      choix('Couleur du haut', couleurs('tissu'), c.haut, couleur('haut')),
      choix('Bas', I.bas, essai.bas, champ('bas')),
      choix('Couleur du bas', couleurs('tissu'), c.bas, couleur('bas')),
      choix('Chaussures', I.chaussures, essai.chaussures, champ('chaussures')),
      choix('Couleur des chaussures', couleurs('chaussures'), c.chaussures, couleur('chaussures')),
      choix('Néon', couleurs('neon'), c.accent, couleur('accent'))
    ]);

    var objets = el('fieldset', { class: 'cc-groupe' }, el('legend', null, 'Tes objets et ton compagnon'));
    (A.emplacements || []).forEach(function (empl) {
      var mien = cat.elements.filter(function (e) { return e.emplacement === empl.id && possede(e); })
        .map(function (e) { return { id: e.id.split(':')[1], nom: e.nom }; });
      if (empl.id === 'compagnon') {
        objets.appendChild(choix('Compagnon', [{ id: 'aucun', nom: 'Aucun' }].concat(mien), essai.compagnon, champ('compagnon')));
        return;
      }
      if (!mien.length) return;
      objets.appendChild(choix(empl.nom, [{ id: 'aucun', nom: 'Rien' }].concat(mien), (essai.objets || {})[empl.id] || 'aucun', function (v) {
        essai.objets = essai.objets || {};
        essai.objets[empl.id] = v;
        redessiner();
      }));
    });
    /* Les pièces libres du moteur (kishali sur la tête et sur les épaules, bandana) que la base ne connaît
       pas encore (migration 0010) : annoncées, jamais proposées, car commun_porter les refuserait */
    var bientot = (A.elements || []).filter(function (e) {
      return e.acces === 'libre' && e.emplacement !== 'compagnon' && !cat.elements.some(function (x) { return x.id === e.id; });
    });
    if (bientot.length) objets.appendChild(el('p', { class: 'petit cc-bientot' }, 'Bientôt, gratuits pour tout le monde : '
      + bientot.map(function (e) { return e.nom.charAt(0).toLowerCase() + e.nom.slice(1); }).join(', ') + '.'));
    objets.appendChild(el('p', { class: 'petit' }, boutiqueOuverte() ? 'D\'autres objets t\'attendent dans la boutique.'
      : 'Pour l\'instant : ton allure, ta tenue et le margouillat, gratuits. Les objets arrivent bientôt, avec la boutique.'));

    panneau.appendChild(el('div', { class: 'cc-loge' }, [
      el('div', { class: 'cc-loge-apercu' }, [apercu, el('div', { class: 'cc-actions' }, [enregistrer, annuler]), m]),
      el('div', null, [
        el('p', { class: 'petit' }, 'Ton allure et ta tenue sont gratuites et vont sur tout avatar. Les objets se prennent dans la boutique ; les compagnons se gagnent avec un haut fait.'),
        el('div', { class: 'cc-loge-choix' }, [identite, tenue, objets])
      ])
    ]));
  }

  /* ── 2b. La boutique : les objets, rangés par famille ───────────── */

  /* Un haut fait qu'on peut gagner aujourd'hui : accordé par l'enseignant·e, ou d'une application qui lit
     déjà le compte commun (réglage COMPTE_COMMUN_APPLICATIONS). Les autres sont « bientôt », sans promesse. */
  function atteignable(h) { return h.accord === 'enseignant' || CC.applicationsBranchees(); }

  function boutiqueOuverte() { return cat.elements.some(function (e) { return e.acces === 'credits'; }); }

  function remplirBoutique(panneau) {
    O.vider(panneau);
    if (!boutiqueOuverte()) {
      panneau.appendChild(el('p', { class: 'cc-intro' }, [el('strong', null, 'La boutique ouvre bientôt.'),
        ' Les objets et leurs prix arrivent avec le catalogue des avatars. En attendant, ton allure, ta tenue et le margouillat sont à toi, gratuitement, dans « Mon avatar ».']));
      panneau.appendChild(el('p', { class: 'petit' }, 'Tes crédits t\'attendent : ' + fiche.credits + '. Ils ne se perdent pas.'));
      return;
    }
    var aPrendre = cat.elements.filter(function (e) { return e.acces === 'credits' && e.actif !== false && !possede(e); });
    var pris = cat.elements.filter(function (e) { return e.acces === 'credits' && possede(e); });

    panneau.appendChild(el('p', { class: 'cc-intro' }, [
      'Tu as ', el('strong', null, fiche.credits + ' crédits'), '. ',
      CC.applicationsBranchees() ? 'Tu les gagnes en travaillant : une feuille de TD validée, un cours-quiz suivi jusqu\'au bout, une mission… '
        : 'Pour l\'instant, seul·e ton enseignant·e peut t\'en donner ; les feuilles de TD et les applications en donneront bientôt. ',
      'Un achat ne se rembourse pas, mais il ne se perd jamais.'
    ]));
    var m = P.zoneMessage();
    panneau.appendChild(m);

    (A.familles || []).filter(function (f) { return !f.trophees; }).forEach(function (f) {
      var dans = aPrendre.filter(function (e) { return e.famille === f.id; });
      if (!dans.length) return;
      var liste = el('ul', { class: 'cc-vitrine' });
      var det = el('details', { class: 'cc-famille' }, [el('summary', null, f.nom), liste]);
      det.addEventListener('toggle', function () {
        if (det.open && !liste.children.length) dans.forEach(function (e) { liste.appendChild(articleBoutique(e, m)); });
      });
      panneau.appendChild(det);
    });
    if (!aPrendre.length) panneau.appendChild(el('p', { class: 'vide' }, 'Tu as déjà tous les objets.'));

    panneau.appendChild(el('p', { class: 'petit' }, ['Les compagnons et les objets de trophée ne s\'achètent pas : ils sont dans l\'onglet « Trophées ».']));
    if (pris.length) {
      panneau.appendChild(el('h3', null, 'Déjà dans ta loge'));
      panneau.appendChild(el('ul', { class: 'cc-puces' }, pris.map(function (e) { return el('li', null, e.nom); })));
    }
  }

  /* ── 2b'. Les trophées : ce qui ne s'achète pas ───────────────────
     Les compagnons et les familles de trophées du catalogue (« trophees » : vrai dans apparences.json) :
     gagnés par un haut fait, offerts par l'enseignant·e avec un motif, ou donnés par un jeu. */
  function remplirTrophees(panneau) {
    O.vider(panneau);
    var origines = {};
    (fiche.trophees || []).forEach(function (t) { origines[t.element] = t; });
    function source(e) { return (cat.hauts_faits || []).filter(function (h) { return (h.recompenses || []).indexOf(e.id) >= 0; })[0]; }
    function carte(e) {
      var a = possede(e), t = origines[e.id], h = source(e), texte;
      if (a && t && t.origine === 'enseignant') texte = 'Offert' + (t.par ? ' par ' + t.par : '') + (t.motif ? ' : ' + t.motif : '') + (t.depuis ? ' (' + P.date(t.depuis) + ')' : '');
      else if (a && t && t.haut_fait) texte = 'Gagné avec : ' + K.nomHf(t.haut_fait.application, t.haut_fait.id);
      else if (a) texte = e.depart ? 'Avec toi dès le départ.' : 'À toi.';
      else if (h && atteignable(h)) texte = 'Se gagne avec : ' + (h.nom || 'un haut fait secret') + (h.application === 'commun' ? ', accordé par ton enseignant·e' : ' (' + K.app(h.application).nom + ')');
      else if (h) texte = 'Bientôt, avec un haut fait de ' + K.app(h.application).nom + '.';
      else if (e.famille === 'classe') texte = CC.disponible('commun_prof_offrir') ? 'Ton enseignant·e peut te l\'offrir.' : 'Bientôt, ton enseignant·e pourra te l\'offrir.';
      else texte = 'Bientôt.';
      return el('li', { class: 'cc-article' + (a ? ' cc-trophee-a-toi' : ' cc-a-gagner') }, [
        miniature(e),
        el('p', { class: 'cc-article-nom' }, [e.nom, el('span', { class: 'invisible' }, a ? ' (à toi)' : ' (pas encore)')]),
        el('p', { class: 'cc-article-empl' }, nomEmplacement(e.emplacement)),
        el('p', { class: 'petit' }, texte)
      ]);
    }
    panneau.appendChild(el('p', { class: 'cc-intro' }, 'Ils ne s\'achètent pas : ils racontent ce que tu as fait. Ceux qui t\'attendent sont en pointillés.'));
    var compagnons = cat.elements.filter(function (e) { return e.emplacement === 'compagnon'; });
    panneau.appendChild(el('h3', null, 'Les compagnons'));
    panneau.appendChild(el('ul', { class: 'cc-vitrine' }, compagnons.map(carte)));
    (A.familles || []).filter(function (f) { return f.trophees; }).forEach(function (f) {
      var dans = cat.elements.filter(function (e) { return e.famille === f.id; });
      if (!dans.length) return;
      panneau.appendChild(el('h3', null, f.nom));
      panneau.appendChild(el('ul', { class: 'cc-vitrine' }, dans.map(carte)));
    });
  }

  function avecElement(e) {
    var a = copieAvatar(fiche.avatar);
    if (e.emplacement === 'compagnon') a.compagnon = e.id.split(':')[1];
    else { a.objets = a.objets || {}; a.objets[e.emplacement] = e.id.split(':')[1]; }
    return a;
  }

  function miniature(e) {
    var d = el('div', { class: 'cc-avatar-cadre cc-mini' });
    CC.dessinerAvatar(d, avecElement(e), { etat: 'repos', taille: 'petit', alt: 'Essai : ' + e.nom });
    return d;
  }

  function articleBoutique(e, m) {
    var ok = fiche.credits >= e.prix;
    var bouton = P.bouton(ok ? 'Prendre pour ' + e.prix + ' crédits' : e.prix + ' crédits : encore ' + (e.prix - fiche.credits) + ' à gagner',
      { inactif: !ok, classe: ok ? 'cc-principal' : 'cc-inactif' });
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
      el('p', { class: 'cc-article-empl' }, nomEmplacement(e.emplacement)),
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
    if (!(cat.hauts_faits || []).length) {
      panneau.appendChild(el('p', { class: 'vide' }, 'Les hauts faits arrivent bientôt, avec le catalogue.'));
      return;
    }
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
                : h.secret ? 'Indice : ' + (h.indice || '…')
                : h.accord === 'enseignant' ? 'Accordé par ton enseignant·e. ' + (h.description || '')
                : atteignable(h) ? 'Pour l\'avoir : ' + (h.description || '')
                : 'Bientôt, quand ' + a.nom + ' lira ton code. ' + (h.description || ''))
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
        CC.dessinerAvatar(av, k.avatar, { etat: 'repos', taille: 'moyen', pseudo: k.pseudo });
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
    /* Seules les applications dont l'adresse est connue : un lien qui marche, jamais une promesse */
    var toutes = cat.applications.filter(function (a) { return a.id !== 'commun' && a.adresse; });
    function liste(apps) {
      return el('ul', { class: 'cc-apps' }, apps.map(function (a) {
        return el('li', { class: 'cc-app' }, el('a', { href: a.adresse }, [el('strong', null, a.nom), el('span', { class: 'petit' }, ' Ouvrir')]));
      }));
    }
    var deClasse = toutes.filter(function (a) { return mesApps[a.id]; });
    var autres = toutes.filter(function (a) { return !mesApps[a.id]; });
    panneau.appendChild(el('p', { class: 'cc-intro' }, CC.applicationsBranchees() ? 'Ton code marche dans chacune. Sur cet appareil, elles te reconnaissent toutes seules.'
      : 'Les applications du site. Bientôt, ton code marchera dans chacune ; pour l\'instant, chacune a encore son propre code.'));
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
    })) : el('p', { class: 'vide' }, CC.applicationsBranchees() ? 'Rien encore : valide une feuille de TD en ligne ou suis un cours-quiz jusqu\'au bout.'
      : 'Rien encore. Pour l\'instant, seul·e ton enseignant·e peut t\'en donner ; les feuilles de TD et les applications en donneront bientôt.'));

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
    var principal = (fiche.codes || []).filter(function (c) { return c.application === 'commun'; })[0] || (fiche.codes || [])[0];
    if (principal) {
      var carteCode = P.bouton('Imprimer la carte de mon code', { classe: 'cc-discret' });
      carteCode.addEventListener('click', function () { imprimerCarte(fiche.pseudo, principal.code_affiche); });
      panneau.appendChild(el('div', { class: 'cc-actions' }, [carteCode]));
    }

    var autre = P.champ({ etiquette: 'Un autre de tes codes (d\'une autre application)', max: 80, capitales: true, classe: 'cc-code-saisie' });
    var m1 = P.zoneMessage();
    /* Masqué tant qu'aucune application n'est branchée : son code serait refusé */
    if (CC.applicationsBranchees()) panneau.appendChild(P.carte('Ajouter un autre de mes codes', [
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
    var partout = CC.applicationsBranchees() ? P.caseACocher('Effacer aussi mes comptes des applications qui le permettent') : null;
    var m3 = P.zoneMessage();
    panneau.appendChild(el('details', { class: 'cc-carte cc-danger' }, [
      el('summary', null, 'Effacer mes données'),
      el('p', null, 'Ton compte commun, ton avatar, tes hauts faits, tes crédits et tes codes nés sur le site sont effacés pour de bon. Ce n\'est pas réversible.'),
      P.formulaire([conf, partout, P.bouton('Effacer mes données', { type: 'submit', classe: 'cc-bouton-danger' }), m3], function () {
        CC.effacerMoi(conf.input.value, !!(partout && partout.input.checked)).then(function (rep) {
          if (!rep.ok) { P.message(m3, rep.message, 'erreur'); return; }
          accueil(rep.message);
        });
      })
    ]));
  }

  /* La carte du code, à imprimer et à coller dans le cahier : le pseudo, le code, l'adresse.
     Seule la carte s'imprime (eleve/compte-commun.css, @media print). */
  function imprimerCarte(pseudo, code) {
    var ancienne = document.querySelector('.cc-carte-imprimee');
    if (ancienne) ancienne.parentNode.removeChild(ancienne);
    var carte = el('div', { class: 'cc-carte-imprimee', 'aria-hidden': 'true' }, [
      el('p', { class: 'cc-carte-imprimee-titre' }, CC.applicationsBranchees() ? 'Mon code pour les applications de NSI et SNT' : 'Mon code pour le site Ressources NSI et SNT'),
      pseudo ? el('p', null, 'Pseudo : ' + pseudo) : null,
      el('p', { class: 'cc-code cc-code-grand' }, code),
      el('p', null, 'Pour revenir : babash.github.io/Babash-NSI-SNT/eleve/, puis « J\'ai déjà un code ».'),
      el('p', { class: 'petit' }, 'Garde cette carte dans ton cahier. Ne la donne à personne : ton code ouvre ton compte.')
    ]);
    document.body.appendChild(carte);
    document.body.classList.add('cc-impression-carte');
    var fin = function () { document.body.classList.remove('cc-impression-carte'); if (carte.parentNode) carte.parentNode.removeChild(carte); window.removeEventListener('afterprint', fin); };
    window.addEventListener('afterprint', fin);
    try { window.print(); } catch (e) { fin(); }
    setTimeout(fin, 60000);
  }

  function caseMontrer() { return P.caseACocher('Montrer mes codes', '(attention si l\'écran est projeté)'); }

  /* Démonstration seulement : faire comme si une page avait validé une activité */
  function blocSimulation() {
    var m = P.zoneMessage();
    var activites = [
      ['td', 'feuille_validee', 'td:poo-td1', 'une feuille de TD validée (TD 1 de POO)'],
      ['td', 'feuille_validee', 'td:boucles-td2', 'une feuille de TD validée (TD 2 : les boucles)'],
    ];
    return el('details', { class: 'cc-carte cc-essai' }, [
      el('summary', null, 'Démonstration : faire comme si…'),
      el('p', { class: 'petit' }, 'En service, ce sont les pages des feuilles de TD qui le disent au compte commun, jamais tes réponses ; QuizzNSI et le calendrier passeront par la page de l\'enseignant·e.'),
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
