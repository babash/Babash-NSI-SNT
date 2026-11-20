/* ═══════════════════════════════════════════════════════════════
   L'espace enseignant·e commun (enseignant/, T101b) : un seul code
   pour toutes les applications, ses classes, ses élèves (avatar,
   hauts faits, avancement par application), l'attribution d'XP avec
   un motif, le lien et le QR code de classe, et les tableaux de bord
   des applications rangés ensemble (donnees/compte-commun/tableaux-de-bord.json).
   Le client : assets/compte-commun.js. Architecte.
   L'XP et les crédits sont des outils de suivi, jamais projetés :
   le « mode tableau » les masque, avec les codes. Rien n'est classé :
   les élèves sont rangé·e·s par pseudo.
   Adresses : #/ (accueil de l'espace), #/classe/<id> (une classe),
   #/classe/<id>/inviter (l'écran à projeter).
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var O, P, CC, Prof, main, el;
  var cat = null, K = null;
  var espace = null;                 // ce que rend commun_prof_ouvrir
  var tableauxDeBord = null;         // les applications et l'adresse de leur tableau de bord
  var modeTableau = false;           // masque codes, XP et crédits (écran projeté)

  window.pageEnseignant = function (racine, outils) {
    O = outils; el = O.el; P = window.PagesCompte; CC = window.CompteCommun;
    if (!P || !CC) {
      racine.appendChild(O.barreHaut('enseignant'));
      racine.appendChild(el('div', { class: 'page' }, el('p', { class: 'alerte', role: 'alert' },
        'L\'espace enseignant·e n\'a pas pu se charger (assets/compte-commun.js manque). Recharger la page.')));
      return;
    }
    Prof = CC.prof;
    P.initialiser(O);
    CC.configurer(O.reglages());
    main = P.entete(racine, { page: 'enseignant', couleur: '#22D3EE', graine: 41, invite: '> espace enseignant·e',
      titre: 'Espace enseignant·e', chapo: 'Un seul code pour toutes les applications : vos classes, vos élèves et les tableaux de bord, rangés ensemble.' });
    main.appendChild(el('p', { class: 'vide' }, 'Chargement…'));
    Promise.all([CC.catalogue(), chargerTableaux()]).then(function (r) {
      cat = r[0] && r[0].elements ? r[0] : { applications: [], elements: [], hauts_faits: [], emplacements: [] };
      K = P.outilsCatalogue(cat);
      tableauxDeBord = r[1];
      if (Prof.ouvert()) {
        Prof.rouvrir().then(function (rep) { if (rep.ok) { espace = rep; router(); } else entree(); });
      } else entree();
    });
    window.addEventListener('hashchange', function () { if (espace) router(); });
  };

  /* ── Les tableaux de bord : la fiche de la bibliothèque d'abord, puis l'adresse de secours ── */

  function chargerTableaux() {
    var url = O.racine + 'donnees/compte-commun/tableaux-de-bord.json';
    return Promise.all([
      fetch(url).then(function (r) { if (!r.ok) throw new Error('code ' + r.status); return r.json(); }),
      fetch(O.racine + 'donnees/bibliotheque.json').then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
    ]).then(function (r) {
      var t = r[0], b = r[1];
      if (!t || !Array.isArray(t.applications)) throw new Error('contenu inattendu');
      var fiches = {};
      ((b && b.ressources) || []).forEach(function (f) { fiches[f.id] = f; });
      var problemes = [];
      var apps = t.applications.map(function (a, i) {
        if (!a || typeof a.application !== 'string' || typeof a.nom !== 'string') {
          problemes.push('l\'entrée n° ' + (i + 1) + ' n\'a pas d\'« application » ou de « nom »');
          return null;
        }
        var adresse = a.adresse || null, source = adresse ? 'reglage' : null;
        var f = a.ressource ? fiches[a.ressource] : null;
        if (a.ressource && b && !f) problemes.push('la fiche « ' + a.ressource + ' » (' + a.nom + ') n\'est pas dans la bibliothèque');
        if (f) {
          var d = (f.documents || []).filter(function (x) { return x.role === 'espace-professeur'; })[0];
          if (d) { adresse = d.url || (d.fichier ? O.racine + d.fichier : adresse); source = 'fiche'; }
        }
        return { application: a.application, nom: a.nom, texte: a.texte || '', adresse: adresse, source: source };
      }).filter(Boolean);
      if (problemes.length) O.signaler('donnees/compte-commun/tableaux-de-bord.json', problemes.join(' ; ') + '.');
      return { applications: apps, problemes: problemes };
    }).catch(function (e) {
      O.signaler('donnees/compte-commun/tableaux-de-bord.json', 'illisible (' + (e && e.message || e) + ').');
      return { applications: [], problemes: ['la liste des tableaux de bord n\'a pas pu être lue (' + (e && e.message || e) + ')'] };
    });
  }

  /* ── 1. Entrer ou créer son espace ─────────────────────────────── */

  function entree(messageDepart) {
    O.vider(main);
    espace = null;
    var grille = el('div', { class: 'cc-deux' });

    var code = P.champ({ etiquette: 'Votre code d\'enseignant·e', aide: '3 mots et 4 chiffres, ou le code d\'un espace d\'application (Hello GO…).',
      exemple: 'MOT-MOT-MOT-1234', capitales: true, max: 80, classe: 'cc-code-saisie', type: 'password', autocomplete: 'off' });
    var voir = P.caseACocher('Montrer le code pendant la saisie');
    voir.input.addEventListener('change', function () { code.input.type = voir.input.checked ? 'text' : 'password'; });
    var onglet = CC.mode() === 'demo' ? null : P.caseACocher('Rester ouvert dans cet onglet', '(jusqu\'à sa fermeture)');
    var m1 = P.zoneMessage();
    var b1 = P.bouton('Ouvrir mon espace', { type: 'submit', classe: 'cc-principal' });
    grille.appendChild(P.carte('J\'ai un code', [P.formulaire([code, voir, onglet, b1, m1], function () {
      if (!CC.normaliserCode(code.input.value)) { P.message(m1, 'Écrivez votre code.', 'erreur'); code.input.focus(); return; }
      P.occupe(b1, true);
      Prof.ouvrir(code.input.value, { onglet: onglet && onglet.input.checked }).then(function (rep) {
        P.occupe(b1, false);
        if (!rep.ok) { P.message(m1, rep.message, 'erreur'); code.input.focus(); return; }
        espace = rep;
        router();
      });
    })]));

    var nom = P.champ({ etiquette: 'Nom affiché aux élèves', aide: 'De 2 à 40 caractères, par exemple « Mme A. » ou « M. B. ».', max: 40 });
    var etab = P.champ({ etiquette: 'Établissement (facultatif)', max: 80 });
    var m2 = P.zoneMessage();
    var b2 = P.bouton('Créer mon espace', { type: 'submit', classe: 'cc-principal' });
    grille.appendChild(P.carte('Créer mon espace', [
      el('p', { class: 'petit' }, 'Ouvert à tout·e collègue, sans adresse ni mot de passe. Vous ne voyez que vos classes.'),
      P.formulaire([nom, etab, b2, m2], function () {
        P.occupe(b2, true);
        Prof.creerEspace(nom.input.value, etab.input.value).then(function (rep) {
          P.occupe(b2, false);
          if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
          montrerCodeProf(rep.code_affiche, rep.message);
        });
      })]));
    main.appendChild(grille);
    if (messageDepart) main.insertBefore(el('p', { class: 'cc-message cc-info', role: 'status' }, messageDepart), main.firstChild);
    var d = CC.demo();
    if (d) {
      var b = el('button', { type: 'button', class: 'cc-lien-bouton' }, el('span', { class: 'cc-code' }, d.enseignant));
      b.addEventListener('click', function () { code.input.value = d.enseignant; code.input.focus(); });
      main.appendChild(el('div', { class: 'cc-carte cc-essai' }, [
        el('p', null, [el('strong', null, 'Pour essayer : '), 'le code de démonstration ', b, ' ouvre un espace fictif avec deux classes.'])
      ]));
    }
    main.appendChild(blocTableaux());
  }

  function montrerCodeProf(codeAffiche, texte) {
    O.vider(main);
    var titre = el('h2', { class: 'cc-carte-titre', tabindex: '-1' }, 'Votre code d\'enseignant·e');
    var b = P.bouton('C\'est noté : ouvrir mon espace', { classe: 'cc-principal' });
    var imprimer = P.bouton('Imprimer', { classe: 'cc-discret' });
    imprimer.addEventListener('click', function () { window.print(); });
    b.addEventListener('click', function () {
      Prof.ouvrir(codeAffiche).then(function (rep) { if (rep.ok) { espace = rep; router(); } else entree(rep.message); });
    });
    main.appendChild(el('section', { class: 'cc-carte cc-ton-code' }, [titre, el('p', { class: 'cc-code cc-code-grand' }, codeAffiche),
      el('p', null, texte || 'Il n\'est montré qu\'une fois : notez-le ou imprimez-le.'), el('div', { class: 'cc-actions' }, [b, imprimer])]));
    titre.focus();
  }

  /* ── Le routage : #/ et #/classe/<id> ──────────────────────────── */

  function router() {
    var h = (location.hash || '').replace(/^#\/?/, '');
    var m = h.match(/^classe\/([^/]+)(\/inviter)?$/);
    if (m) return pageClasse(decodeURIComponent(m[1]), !!m[2]);
    accueilEspace();
  }
  function aller(chemin) {
    if (location.hash === '#/' + chemin) router();
    else location.hash = '#/' + chemin;
  }
  function rafraichirEspace() {
    return Prof.rouvrir().then(function (rep) { if (rep.ok) espace = rep; return rep; });
  }

  function barreEspace() {
    var fermer = P.bouton('Fermer mon espace', { classe: 'cc-discret' });
    fermer.addEventListener('click', function () { Prof.fermer(); try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* rien */ } entree('Votre espace est fermé sur cet appareil.'); });
    var tableau = P.caseACocher('Mode tableau', '(masque codes, XP et crédits : pour projeter)');
    tableau.input.checked = modeTableau;
    tableau.input.addEventListener('change', function () { modeTableau = tableau.input.checked; document.body.classList.toggle('cc-mode-tableau', modeTableau); });
    return el('div', { class: 'cc-barre-espace' }, [
      el('p', null, [el('strong', null, espace.nom), espace.etablissement ? ' · ' + espace.etablissement : '']),
      tableau, fermer
    ]);
  }

  /* ── 2. L'accueil de l'espace : classes et tableaux de bord ────── */

  function accueilEspace() {
    O.vider(main);
    main.appendChild(barreEspace());
    var titre = el('h2', { class: 'cc-titre-section', tabindex: '-1' }, 'Mes classes');
    main.appendChild(titre);
    if (espace.alarme) main.appendChild(el('p', { class: 'cc-message cc-erreur' }, 'Beaucoup d\'essais de codes ratés en une heure sur le compte commun : surveillez la salle.'));
    var classes = espace.classes || [];
    main.appendChild(classes.length ? el('ul', { class: 'cc-classes' }, classes.map(function (c) {
      return el('li', { class: 'cc-classe-carte' }, [
        el('a', { href: '#/classe/' + encodeURIComponent(c.id), class: 'cc-classe-lien-nom' }, c.nom),
        el('p', { class: 'petit' }, [
          'Code ', el('span', { class: 'cc-code' }, c.code), ' · ', c.eleves + (c.eleves > 1 ? ' élèves' : ' élève'), ' · ',
          c.ouverte ? 'inscriptions ouvertes' : 'inscriptions fermées'
        ]),
        el('p', { class: 'petit' }, (c.applications || []).map(function (a) { return K.app(a).nom; }).join(', ') || 'Aucune application choisie')
      ]);
    })) : el('p', { class: 'vide' }, 'Pas encore de classe. Créez-en une : vous obtenez son lien et son QR code.'));
    main.appendChild(formNouvelleClasse());
    main.appendChild(blocTableaux());
    main.appendChild(blocReglages());
    titre.focus();
  }

  function choixApplications(coches) {
    var fs = el('fieldset', { class: 'cc-groupe cc-choix-apps' }, el('legend', null, 'Les applications de la classe'));
    var cases = [];
    cat.applications.filter(function (a) { return a.id !== 'commun'; }).forEach(function (a) {
      var c = P.caseACocher(a.nom);
      c.input.value = a.id;
      c.input.checked = (coches || []).indexOf(a.id) >= 0;
      cases.push(c.input);
      fs.appendChild(c);
    });
    fs.valeurs = function () { return cases.filter(function (x) { return x.checked; }).map(function (x) { return x.value; }); };
    return fs;
  }

  function formNouvelleClasse() {
    var nom = P.champ({ etiquette: 'Nom de la classe', aide: 'De 2 à 40 caractères, par exemple « Seconde 4 ».', max: 40 });
    var apps = choixApplications(['td', 'quizz_nsi']);
    var m = P.zoneMessage();
    var b = P.bouton('Créer la classe', { type: 'submit', classe: 'cc-principal' });
    return el('details', { class: 'cc-carte' }, [el('summary', null, 'Nouvelle classe'), P.formulaire([nom, apps, b, m], function () {
      P.occupe(b, true);
      Prof.creerClasse(nom.input.value, apps.valeurs()).then(function (rep) {
        P.occupe(b, false);
        if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
        P.annoncer('Classe créée : code ' + rep.code + '.', 'ok');
        rafraichirEspace().then(function () { aller('classe/' + encodeURIComponent(rep.id)); });
      });
    })]);
  }

  function blocTableaux() {
    var t = tableauxDeBord || { applications: [], problemes: [] };
    var sec = el('section', { class: 'cc-section-tableaux', 'aria-labelledby': 'titre-tableaux' }, [
      el('h2', { id: 'titre-tableaux', class: 'cc-titre-section' }, 'Les tableaux de bord des applications'),
      el('p', { class: 'petit' }, 'Chaque tableau reste dans son application : cette page les range. Une classe reliée ouvre directement le sien.')
    ]);
    if (t.problemes.length) sec.appendChild(el('div', { class: 'alerte', role: 'alert' }, [el('p', null, el('strong', null, 'Liste des tableaux de bord incomplète')),
      el('ul', null, t.problemes.map(function (p) { return el('li', null, p); }))]));
    sec.appendChild(el('ul', { class: 'cc-apps cc-tableaux' }, t.applications.map(function (a) {
      return el('li', { class: 'cc-app' }, [
        a.adresse ? el('a', { href: a.adresse }, el('strong', null, a.nom)) : el('strong', null, a.nom),
        el('p', { class: 'petit' }, a.texte),
        a.adresse ? null : el('p', { class: 'petit cc-a-venir' }, 'Adresse à venir')
      ]);
    })));
    return sec;
  }

  function blocReglages() {
    var autre = P.champ({ etiquette: 'Le code d\'un espace d\'application', aide: 'Par exemple celui de Hello GO. Il reste valable dans son application.', max: 80, capitales: true, type: 'password' });
    var m1 = P.zoneMessage();
    var m2 = P.zoneMessage();
    var nouveau = P.bouton('Me donner un nouveau code');
    var zoneCode = el('div');
    nouveau.addEventListener('click', function () {
      O.vider(zoneCode);
      var oui = P.bouton('Oui, changer mon code', { classe: 'cc-principal' });
      var non = P.bouton('Non', { classe: 'cc-discret' });
      non.addEventListener('click', function () { O.vider(zoneCode); nouveau.focus(); });
      oui.addEventListener('click', function () {
        Prof.nouveauCode().then(function (rep) {
          O.vider(zoneCode);
          if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
          zoneCode.appendChild(el('p', { class: 'cc-code cc-code-grand' }, rep.code_affiche));
          zoneCode.appendChild(el('p', null, rep.message));
        });
      });
      zoneCode.appendChild(el('p', null, 'L\'ancien code ne marchera plus. Les codes de vos applications restent valables.'));
      zoneCode.appendChild(el('div', { class: 'cc-actions' }, [oui, non]));
    });
    var debloquer = P.bouton('Débloquer le réseau de la salle');
    debloquer.addEventListener('click', function () {
      Prof.debloquerReseau().then(function (rep) { P.message(m2, rep.ok ? 'Le compteur d\'essais de ce réseau est remis à zéro.' : rep.message, rep.ok ? 'ok' : 'erreur'); });
    });
    var conf = P.champ({ etiquette: 'Écrivez SUPPRIMER pour confirmer', max: 12, capitales: true });
    var m3 = P.zoneMessage();
    return el('details', { class: 'cc-carte' }, [el('summary', null, 'Réglages de mon espace'),
      el('h3', null, 'Ajouter un espace d\'application'),
      P.formulaire([autre, P.bouton('Relier cet espace', { type: 'submit' }), m1], function () {
        Prof.lierCode(autre.input.value).then(function (rep) {
          P.message(m1, rep.message, rep.ok ? 'ok' : 'erreur');
          if (rep.ok) rafraichirEspace();
        });
      }),
      el('h3', null, 'Mon code'),
      el('div', { class: 'cc-actions' }, [nouveau, debloquer]), zoneCode, m2,
      el('h3', null, 'Supprimer mon espace'),
      el('p', { class: 'petit' }, 'Vos classes communes disparaissent ; les comptes des élèves restent, ainsi que vos espaces dans chaque application.'),
      P.formulaire([conf, P.bouton('Supprimer mon espace', { type: 'submit', classe: 'cc-bouton-danger' }), m3], function () {
        Prof.supprimerEspace(conf.input.value).then(function (rep) {
          if (!rep.ok) { P.message(m3, rep.message, 'erreur'); return; }
          entree(rep.message);
        });
      })
    ]);
  }

  /* ── 3. La page d'une classe ───────────────────────────────────── */

  function pageClasse(id, inviter) {
    O.vider(main);
    main.appendChild(barreEspace());
    main.appendChild(el('p', { class: 'vide' }, 'Chargement de la classe…'));
    Promise.all([Prof.classe(id), Prof.journalXp(id)]).then(function (r) {
      var rep = r[0];
      O.vider(main);
      main.appendChild(barreEspace());
      main.appendChild(el('p', { class: 'cc-fil' }, el('a', { href: '#/' }, '← Mes classes')));
      if (!rep.ok) { main.appendChild(el('p', { class: 'cc-message cc-erreur', role: 'alert' }, rep.message)); return; }
      var journal = r[1].ok ? r[1].journal : [];
      if (inviter) return ecranInviter(rep.classe);
      var c = rep.classe;
      var titre = el('h2', { class: 'cc-titre-section', tabindex: '-1' }, c.nom);
      main.appendChild(titre);
      main.appendChild(blocLienClasse(c));
      main.appendChild(blocTableauxClasse(c));
      main.appendChild(blocEleves(c, rep.eleves, journal));
      main.appendChild(blocJournal(journal));
      main.appendChild(blocReglagesClasse(c));
      titre.focus();
    });
  }

  function qrSvg(texte) {
    if (typeof window.qrcode !== 'function') return null;
    try {
      var q = window.qrcode(0, 'M');
      q.addData(texte);
      q.make();
      return q.createSvgTag({ cellSize: 4, margin: 2, scalable: true });
    } catch (e) { return null; }
  }

  function blocLienClasse(c) {
    var qr = qrSvg(c.lien);
    var copier = P.bouton('Copier le lien');
    var m = P.zoneMessage();
    copier.addEventListener('click', function () {
      var fait = function () { P.message(m, 'Lien copié.', 'ok'); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(c.lien).then(fait, function () { P.message(m, 'Copie impossible : sélectionnez le lien.', 'erreur'); });
      else P.message(m, 'Copie impossible : sélectionnez le lien.', 'erreur');
    });
    var inviter = el('a', { href: '#/classe/' + encodeURIComponent(c.id) + '/inviter', class: 'cc-bouton cc-principal' }, 'Inviter les élèves (à projeter)');
    return el('section', { class: 'cc-carte cc-lien-classe' }, [
      el('div', { class: 'cc-lien-texte' }, [
        el('p', null, ['Code de classe : ', el('span', { class: 'cc-code cc-code-moyen' }, c.code), ' · ', c.ouverte ? 'inscriptions ouvertes' : 'inscriptions fermées']),
        el('p', { class: 'cc-lien-url' }, el('a', { href: c.lien }, c.lien)),
        el('div', { class: 'cc-actions' }, [inviter, copier]), m
      ]),
      qr ? el('div', { class: 'cc-qr', role: 'img', 'aria-label': 'QR code du lien de la classe ' + c.nom, html: qr }) : el('p', { class: 'petit' }, 'QR code indisponible (enseignant/qrcode.js n\'a pas pu se charger).')
    ]);
  }

  /* L'écran à projeter : le code de classe en très grand et le QR code, rien d'autre */
  function ecranInviter(c) {
    var qr = qrSvg(c.lien);
    var titre = el('h2', { class: 'cc-inviter-titre', tabindex: '-1' }, 'Rejoindre ' + c.nom);
    main.appendChild(el('section', { class: 'cc-inviter' }, [
      titre,
      qr ? el('div', { class: 'cc-qr cc-qr-grand', role: 'img', 'aria-label': 'QR code du lien de la classe', html: qr }) : null,
      el('p', null, 'Ou va sur ' + c.lien.replace(/^https:\/\//, '').replace(/\?.*$/, '') + ' et tape le code de classe :'),
      el('p', { class: 'cc-code cc-code-projete' }, c.code),
      el('p', { class: 'petit' }, c.ouverte ? 'Choisis un prénom ou un pseudo, jamais ton nom de famille. Note ton code dans ton cahier.' : 'Attention : les inscriptions de cette classe sont fermées.'),
      el('p', null, el('a', { href: '#/classe/' + encodeURIComponent(c.id) }, '← Retour à la classe'))
    ]));
    titre.focus();
  }

  function blocTableauxClasse(c) {
    var sec = el('section', { class: 'cc-carte' }, el('h3', null, 'Les tableaux de bord de la classe'));
    var t = c.tableaux || [];
    sec.appendChild(t.length ? el('ul', { class: 'cc-apps' }, t.map(function (x) {
      var retirer = el('button', { type: 'button', class: 'cc-lien-bouton petit' }, 'Retirer');
      retirer.addEventListener('click', function () {
        Prof.lierClasse(c.id, x.application, x.reference, true).then(function () { router(); });
      });
      return el('li', { class: 'cc-app' }, [x.adresse ? el('a', { href: x.adresse }, el('strong', null, x.nom)) : el('strong', null, x.nom),
        el('p', { class: 'petit' }, ['Classe de l\'application : ', el('span', { class: 'cc-code' }, x.reference), ' · ']), retirer]);
    })) : el('p', { class: 'petit' }, 'Aucune classe d\'application n\'est reliée.'));
    var sel = el('select', { id: P.idUnique('app'), class: 'cc-select' }, cat.applications.filter(function (a) { return a.id !== 'commun'; })
      .map(function (a) { return el('option', { value: a.id }, a.nom); }));
    var ref = P.champ({ etiquette: 'Son code de classe ou de salle', max: 64, capitales: true, aide: 'Celui que donne l\'application (lettres, chiffres, tiret).' });
    var m = P.zoneMessage();
    sec.appendChild(el('details', null, [el('summary', null, 'Relier la classe d\'une application'),
      P.formulaire([el('div', { class: 'cc-champ' }, [el('label', { for: sel.id }, 'Application'), sel]), ref, P.bouton('Relier', { type: 'submit' }), m], function () {
        var v = ref.input.value.trim();
        Prof.lierClasse(c.id, sel.value, v, false).then(function (rep) { if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; } router(); });
      })]));
    return sec;
  }

  /* L'avancement par application : ce que le journal et les hauts faits disent, pour un·e élève */
  function avancement(eleve, journal) {
    var parApp = {};
    function app(a) { return parApp[a] || (parApp[a] = { activites: 0, hauts_faits: 0 }); }
    journal.forEach(function (j) {
      if (j.compte !== eleve.compte || j.xp <= 0) return;
      if (j.evenement === 'attribution' || j.evenement === 'haut_fait' || j.evenement === 'achat') return;
      app(j.application).activites += 1;
    });
    (eleve.hauts_faits || []).forEach(function (h) { app(h.application).hauts_faits += 1; });
    return Object.keys(parApp).sort(function (a, b) { return K.app(a).nom.localeCompare(K.app(b).nom, 'fr'); }).map(function (a) {
      var x = parApp[a], parts = [];
      if (x.activites) parts.push(x.activites + (x.activites > 1 ? ' activités' : ' activité'));
      if (x.hauts_faits) parts.push(x.hauts_faits + (x.hauts_faits > 1 ? ' hauts faits' : ' haut fait'));
      return { nom: a === 'commun' ? 'Site et enseignant·e' : K.app(a).nom, texte: parts.join(', ') };
    });
  }

  function blocEleves(c, eleves, journal) {
    var sec = el('section', { class: 'cc-section-eleves', 'aria-labelledby': 'titre-eleves' }, [
      el('h3', { id: 'titre-eleves' }, 'Les élèves (' + eleves.length + '), rangé·e·s par pseudo'),
      el('p', { class: 'petit cc-suivi' }, 'L\'XP et les crédits sont pour votre suivi : les élèves ne voient que leur propre solde, jamais un total ni un classement.')
    ]);
    if (!eleves.length) { sec.appendChild(el('p', { class: 'vide' }, 'Personne encore. Projetez l\'écran « Inviter les élèves ».')); return sec; }
    var hfProf = (cat.hauts_faits || []).filter(function (h) { return h.accord ? h.accord === 'enseignant' : h.application === 'commun'; });
    sec.appendChild(el('ul', { class: 'cc-eleves' }, eleves.map(function (e) { return carteEleve(c, e, journal, hfProf); })));
    return sec;
  }

  function carteEleve(c, e, journal, hfProf) {
    var av = el('div', { class: 'cc-avatar-cadre cc-moyen' });
    CC.dessinerAvatar(av, e.avatar, { etat: 'repos', taille: 'moyen', catalogue: cat, pseudo: e.pseudo });
    var hfs = (e.hauts_faits || []).map(function (h) { return K.nomHf(h.application, h.id) + ' (' + (h.application === 'commun' ? 'site et enseignant·e' : K.app(h.application).nom) + ')'; });
    var av2 = avancement(e, journal);
    var actions = el('div', { class: 'cc-eleve-actions' });

    /* Attribuer de l'XP avec un motif */
    var xp = P.champ({ etiquette: 'XP (1 à 50)', type: 'number', mini: 1, maxi: 50, inputmode: 'numeric', valeur: '10', classe: 'cc-nombre' });
    var motif = P.champ({ etiquette: 'Motif', aide: 'De 3 à 80 caractères ; l\'élève le lit dans sa planque.', max: 80, exemple: 'Aide à un camarade' });
    var m1 = P.zoneMessage();
    var fAttr = P.formulaire([el('div', { class: 'cc-en-ligne' }, [xp, motif]), P.bouton('Attribuer', { type: 'submit', classe: 'cc-principal' }), m1], function () {
      Prof.attribuerXp(e.compte, parseInt(xp.input.value, 10), motif.input.value).then(function (rep) {
        if (!rep.ok) { P.message(m1, rep.message, 'erreur'); return; }
        P.annoncer(e.pseudo + ' : +' + rep.xp + ' XP (« ' + motif.input.value.trim() + ' »).', 'ok');
        router();
      });
    });

    /* Accorder un haut fait d'enseignant·e */
    var m2 = P.zoneMessage();
    var dejaHf = (e.hauts_faits || []).map(function (h) { return h.application + '/' + h.id; });
    var restants = hfProf.filter(function (h) { return dejaHf.indexOf(h.application + '/' + h.id) < 0; });
    var selHf = el('select', { id: P.idUnique('hf'), class: 'cc-select' }, restants.map(function (h) {
      return el('option', { value: h.application + '/' + h.id }, h.nom || h.id);
    }));
    var fHf = restants.length ? P.formulaire([el('div', { class: 'cc-champ' }, [el('label', { for: selHf.id }, 'Haut fait'), selHf]),
      P.bouton('Accorder', { type: 'submit' }), m2], function () {
      var v = selHf.value.split('/');
      Prof.accorder(e.compte, v[0], v[1]).then(function (rep) {
        if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
        P.annoncerNouveautes(rep.nouveautes, cat);
        router();
      });
    }) : el('p', { class: 'petit' }, 'Tous les hauts faits d\'enseignant·e sont déjà accordés.');

    /* Renommer, nouveau code, retirer */
    var ps = P.champ({ etiquette: 'Nouveau pseudo', max: 24, valeur: e.pseudo });
    var m3 = P.zoneMessage();
    var fRen = P.formulaire([ps, P.bouton('Renommer', { type: 'submit' }), m3], function () {
      Prof.renommerEleve(e.compte, ps.input.value).then(function (rep) { if (!rep.ok) { P.message(m3, rep.message, 'erreur'); return; } router(); });
    });
    var nc = P.bouton('Nouveau code');
    var zoneNc = el('div', { class: 'cc-masquable-bloc' });
    nc.addEventListener('click', function () {
      Prof.nouveauCodeEleve(e.compte).then(function (rep) {
        O.vider(zoneNc);
        if (!rep.ok) { zoneNc.appendChild(el('p', { class: 'cc-message cc-erreur' }, rep.message)); return; }
        zoneNc.appendChild(el('p', null, ['Nouveau code : ', el('span', { class: 'cc-code cc-masquable' }, rep.code_affiche), '. L\'ancien ne marche plus.']));
      });
    });
    var retirer = P.bouton('Retirer de la classe', { classe: 'cc-bouton-danger' });
    var zoneRet = el('div');
    retirer.addEventListener('click', function () {
      O.vider(zoneRet);
      var oui = P.bouton('Oui, retirer ' + e.pseudo, { classe: 'cc-bouton-danger' });
      var non = P.bouton('Non', { classe: 'cc-discret' });
      non.addEventListener('click', function () { O.vider(zoneRet); retirer.focus(); });
      oui.addEventListener('click', function () { Prof.retirerEleve(c.id, e.compte).then(function () { router(); }); });
      zoneRet.appendChild(el('p', null, 'Son compte reste, avec tout ce qu\'il ou elle a gagné.'));
      zoneRet.appendChild(el('div', { class: 'cc-actions' }, [oui, non]));
      oui.focus();
    });

    actions.appendChild(el('details', null, [el('summary', null, 'Attribuer de l\'XP'), fAttr]));
    actions.appendChild(el('details', null, [el('summary', null, 'Accorder un haut fait'), fHf]));
    actions.appendChild(el('details', null, [el('summary', null, 'Pseudo, code, retrait'), fRen, el('div', { class: 'cc-actions' }, [nc, retirer]), zoneNc, zoneRet]));

    return el('li', { class: 'cc-eleve' }, [
      el('div', { class: 'cc-eleve-tete' }, [av, el('div', null, [
        el('p', { class: 'cc-eleve-nom' }, e.pseudo),
        el('p', { class: 'petit' }, 'Dernière visite : ' + P.depuis(e.vu_le)),
        el('p', { class: 'petit cc-suivi' }, ['XP gagnée : ', el('strong', null, String(e.xp)), ' · crédits : ', el('strong', null, String(e.credits))]),
        el('p', { class: 'petit cc-suivi' }, ['Code : '].concat((e.codes || []).map(function (x, i) { return el('span', { class: 'cc-code' }, (i ? ', ' : '') + x); })))
      ])]),
      el('div', { class: 'cc-eleve-corps' }, [
        el('p', { class: 'cc-petit-titre' }, 'Avancement'),
        av2.length ? el('ul', { class: 'cc-puces' }, av2.map(function (x) { return el('li', null, [el('strong', null, x.nom), ' : ' + x.texte]); }))
          : el('p', { class: 'petit' }, 'Rien encore.'),
        el('p', { class: 'cc-petit-titre' }, 'Hauts faits'),
        hfs.length ? el('ul', { class: 'cc-puces' }, hfs.map(function (n) { return el('li', null, n); })) : el('p', { class: 'petit' }, 'Pas encore.')
      ]),
      actions
    ]);
  }

  function blocJournal(journal) {
    var lignes = journal.slice(0, 60);
    return el('details', { class: 'cc-carte cc-suivi' }, [el('summary', null, 'Le journal de la classe (gains, achats, attributions)'),
      lignes.length ? el('ul', { class: 'cc-journal' }, lignes.map(function (j) {
        var quoi = j.evenement === 'attribution' ? 'Attribution' + (j.par ? ' par ' + j.par : '') + ' : ' + (j.motif || '')
          : j.evenement === 'achat' ? 'Achat d\'une apparence'
          : j.evenement === 'haut_fait' ? 'Haut fait (' + K.app(j.application).nom + ')'
          : (K.app(j.application).nom + ' : ' + j.evenement.replace(/_/g, ' '));
        return el('li', null, [el('span', { class: 'cc-journal-date' }, P.date(j.le)), el('span', { class: 'cc-journal-quoi' }, [el('strong', null, j.pseudo), ' · ', quoi]),
          el('span', { class: 'cc-journal-nb' + (j.xp < 0 ? ' cc-moins' : '') }, (j.xp > 0 ? '+' : '−') + Math.abs(j.xp))]);
      })) : el('p', { class: 'vide' }, 'Rien encore.')]);
  }

  function blocReglagesClasse(c) {
    var nom = P.champ({ etiquette: 'Nom de la classe', max: 40, valeur: c.nom });
    var ouverte = P.caseACocher('Inscriptions ouvertes');
    ouverte.input.checked = !!c.ouverte;
    var apps = choixApplications(c.applications);
    var m = P.zoneMessage();
    var conf = P.champ({ etiquette: 'Écrivez SUPPRIMER pour confirmer', max: 12, capitales: true });
    var m2 = P.zoneMessage();
    return el('details', { class: 'cc-carte' }, [el('summary', null, 'Réglages de la classe'),
      P.formulaire([nom, ouverte, apps, P.bouton('Enregistrer', { type: 'submit', classe: 'cc-principal' }), m], function () {
        Prof.modifierClasse(c.id, nom.input.value, ouverte.input.checked, apps.valeurs()).then(function (rep) {
          if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
          rafraichirEspace().then(router);
        });
      }),
      el('h3', null, 'Supprimer la classe'),
      el('p', { class: 'petit' }, 'Les comptes des élèves restent, avec tout ce qu\'ils ont gagné.'),
      P.formulaire([conf, P.bouton('Supprimer la classe', { type: 'submit', classe: 'cc-bouton-danger' }), m2], function () {
        Prof.supprimerClasse(c.id, conf.input.value).then(function (rep) {
          if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
          rafraichirEspace().then(function () { aller(''); });
        });
      })
    ]);
  }
})();
