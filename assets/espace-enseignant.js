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
  var fichesBib = {};                // les fiches de la bibliothèque, par identifiant (titres des avis)
  var sequencesBib = [];             // les séquences de la bibliothèque, si elle en a (T153)
  var modeTableau = false;           // masque codes, XP et crédits (écran projeté)
  var messageClasse = null;          // le message d'une action, montré une fois après le rechargement de la classe
  var NIVEAUX = [];
  var erreurCatalogue = null;        // le message d'une lecture ratée du catalogue : gardé en haut de chaque vue                  // les niveaux des référentiels (masqués tant que COMPTE_COMMUN_NIVEAU vaut false)

  window.pageEnseignant = function (racine, outils) {
    O = outils; el = O.el; P = window.PagesCompte; CC = window.CompteCommun;
    if (!P || !CC) {
      racine.appendChild(O.barreHaut('enseignant'));
      racine.appendChild(el('div', { class: 'page' }, el('p', { class: 'alerte', role: 'alert' },
        'L\'espace enseignant·e n\'a pas pu se charger (assets/compte-commun.js manque). Recharge la page.')));
      return;
    }
    Prof = CC.prof;
    P.initialiser(O);
    CC.configurer(O.reglages());
    main = P.entete(racine, { page: 'enseignant', puce: 'Prof', surTitre: ['compte commun'],
      titre: 'Espace enseignant·e', chapo: CC.applicationsBranchees() ? 'Un seul code pour toutes les applications : tes classes, tes élèves et les tableaux de bord, rangés ensemble.'
        : 'Un seul code pour tes classes communes et tes élèves, avec les tableaux de bord des applications rangés à côté. Bientôt, ce code ouvrira aussi les applications.' });
    main.appendChild(el('p', { class: 'vide' }, 'Chargement…'));
    Promise.all([CC.catalogue(), chargerTableaux(), CC.niveauActif() ? CC.niveaux() : Promise.resolve([])]).then(function (r) {
      cat = r[0] && r[0].elements ? r[0] : { applications: [], elements: [], hauts_faits: [], emplacements: [] };
      if (r[0] && !r[0].ok && r[0].message && !r[0].elements) erreurCatalogue = 'Le catalogue n\'a pas pu être lu : ' + r[0].message
        + ' Offrir un trophée, archiver une classe et accorder un haut fait attendent qu\'il se lise : recharge la page dans un moment.';
      K = P.outilsCatalogue(cat);
      tableauxDeBord = r[1];
      NIVEAUX = r[2] || [];
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
      fichesBib = fiches;
      sequencesBib = (b && Array.isArray(b.sequences)) ? b.sequences : [];
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

  /* La lecture ratée du catalogue reste à l'écran, quelle que soit la vue (avant, entree() l'effaçait) */
  function alerteCatalogue() {
    if (erreurCatalogue) main.appendChild(el('p', { class: 'cc-message cc-erreur', role: 'alert' }, erreurCatalogue));
  }

  function entree(messageDepart) {
    O.vider(main);
    alerteCatalogue();
    espace = null;
    var grille = el('div', { class: 'cc-deux' });

    var code = P.champ({ etiquette: 'Ton code d\'enseignant·e', aide: CC.applicationsBranchees() ? '3 mots et 4 chiffres, ou le code d\'un espace d\'application (Hello GO…).' : '3 mots et 4 chiffres.',
      exemple: 'MOT-MOT-MOT-1234', capitales: true, max: 80, classe: 'cc-code-saisie', type: 'password', autocomplete: 'off' });
    var voir = P.caseACocher('Montrer le code pendant la saisie');
    voir.input.addEventListener('change', function () { code.input.type = voir.input.checked ? 'text' : 'password'; });
    var onglet = CC.mode() === 'demo' ? null : P.caseACocher('Rester ouvert dans cet onglet', '(jusqu\'à sa fermeture)');
    var m1 = P.zoneMessage();
    var b1 = P.bouton('Ouvrir mon espace', { type: 'submit', classe: 'cc-principal' });
    grille.appendChild(P.carte('J\'ai un code', [P.formulaire([code, voir, onglet, b1, m1], function () {
      if (!CC.normaliserCode(code.input.value)) { P.message(m1, 'Écris ton code.', 'erreur'); code.input.focus(); return; }
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
      el('p', { class: 'petit' }, 'Ouvert à tout·e collègue, sans adresse ni mot de passe. Tu ne vois que tes classes.'),
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
    var titre = el('h2', { class: 'cc-carte-titre', tabindex: '-1' }, 'Ton code d\'enseignant·e');
    var b = P.bouton('Je l\'ai noté', { classe: 'cc-principal' });
    var imprimer = P.bouton('Imprimer', { classe: 'cc-discret' });
    imprimer.addEventListener('click', function () {
      document.body.classList.add('cc-impression-code');
      var fin = function () { document.body.classList.remove('cc-impression-code'); window.removeEventListener('afterprint', fin); };
      window.addEventListener('afterprint', fin);
      try { window.print(); } catch (e) { fin(); }
    });
    /* Comme l'élève retape ses 3 chiffres : on retape les 4 chiffres avant « Je l'ai noté »
       (spécification des codes, § 1.5 ; la base n'en garde que l'empreinte) */
    var chiffres = (codeAffiche.match(/(\d{4})$/) || [])[1] || '';
    var saisie = P.champ({ etiquette: 'Retape les 4 chiffres de ton code', inputmode: 'numeric', max: 4, classe: 'cc-chiffres', autocomplete: 'off' });
    var m = P.zoneMessage();
    b.setAttribute('type', 'submit');
    var form = P.formulaire([saisie, el('div', { class: 'cc-actions' }, [b, imprimer]), m], function () {
      if (saisie.input.value.replace(/\D/g, '') !== chiffres) {
        P.message(m, 'Ce ne sont pas les bons chiffres : regarde ton code et recopie-le, ou imprime-le.', 'erreur');
        saisie.input.focus();
        return;
      }
      P.occupe(b, true);
      /* Si la base ne répond pas, le code reste à l'écran avec le message : il n'est montré qu'une fois */
      Prof.ouvrir(codeAffiche).then(function (rep) {
        P.occupe(b, false);
        if (rep.ok) { espace = rep; router(); return; }
        P.message(m, rep.message + ' Ton code reste affiché : garde-le, puis réessaie « Je l\'ai noté ».', 'erreur');
      });
    });
    main.appendChild(el('section', { class: 'cc-carte cc-ton-code' }, [titre, el('p', { class: 'cc-code cc-code-grand' }, codeAffiche),
      el('p', null, texte || 'Il n\'est montré qu\'une fois : note-le ou imprime-le.'),
      el('p', { class: 'petit' }, 'Il ouvre ton espace depuis n\'importe quel appareil. Personne d\'autre ne peut le retrouver : ni la base, ni le site. Perdu, il te coupe de tes classes.'),
      form]));
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
    fermer.addEventListener('click', function () { Prof.fermer(); try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* rien */ } entree('Ton espace est fermé sur cet appareil.'); });
    var tableau = P.caseACocher('Mode projection', '(masque les codes, l\'XP et les crédits)');
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
    alerteCatalogue();
    main.appendChild(barreEspace());
    var titre = el('h2', { class: 'cc-titre-section', tabindex: '-1' }, 'Mes classes');
    main.appendChild(titre);
    if (espace.alarme) main.appendChild(el('p', { class: 'cc-message cc-erreur' }, 'Beaucoup d\'essais de codes ratés en une heure sur le compte commun : surveille la salle.'));
    var toutes = espace.classes || [];
    /* Rangées à part : les classes archivées (migration 0010) ; avant, toutes ensemble */
    var archivable = CC.disponible('commun_prof_archiver_classe');
    var classes = toutes.filter(function (c) { return !(archivable && c.archivee); });
    var fermees = toutes.filter(function (c) { return archivable && c.archivee; });
    function carteClasse(c) {
      return el('li', { class: 'cc-classe-carte' }, [
        el('a', { href: '#/classe/' + encodeURIComponent(c.id), class: 'cc-classe-lien-nom' }, c.nom),
        el('p', { class: 'petit' }, [
          'Code ', el('span', { class: 'cc-code' }, c.code), ' · ', c.eleves + (c.eleves > 1 ? ' élèves' : ' élève'), ' · ',
          c.ouverte ? 'inscriptions ouvertes' : 'inscriptions fermées'
        ]),
        el('p', { class: 'petit' }, (c.applications || []).map(function (a) { return K.app(a).nom; }).join(', ') || 'Aucune application choisie')
      ]);
    }
    main.appendChild(classes.length ? el('ul', { class: 'cc-classes' }, classes.map(carteClasse))
      : el('p', { class: 'vide' }, toutes.length ? 'Toutes tes classes sont archivées.' : 'Pas encore de classe. Crée-en une : tu obtiens son lien et son QR code.'));
    if (fermees.length) main.appendChild(el('details', { class: 'cc-carte' }, [el('summary', null, 'Classes archivées (' + fermees.length + ')'),
      el('p', { class: 'petit' }, 'Leurs élèves gardent leur compte et tout ce qu\'ils ont gagné. « Désarchiver » dans les réglages de la classe.'),
      el('ul', { class: 'cc-classes' }, fermees.map(carteClasse))]));
    main.appendChild(formNouvelleClasse());
    main.appendChild(blocTableaux());
    if (CC.disponible('commun_prof_retours')) main.appendChild(blocAvis(null));
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
      el('p', { class: 'petit' }, 'Chaque tableau reste dans son application, avec son propre code : cette page les range. Une classe reliée garde le lien vers le sien.')
    ]);
    if (t.problemes.length) sec.appendChild(el('div', { class: 'alerte', role: 'alert' }, [el('p', null, el('strong', null, 'Liste des tableaux de bord incomplète')),
      el('ul', null, t.problemes.map(function (p) { return el('li', null, p); }))]));
    sec.appendChild(el('ul', { class: 'cc-apps cc-tableaux' }, t.applications.map(function (a) {
      return el('li', { class: 'cc-app' }, [
        a.adresse ? el('a', { href: a.adresse }, el('strong', null, a.nom)) : el('strong', null, a.nom),
        el('p', { class: 'petit' }, a.texte)
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
          /* Le nouveau code n'est montré qu'une fois : on retape ses 4 chiffres, comme à la création */
          var chiffres = (rep.code_affiche.match(/(\d{4})$/) || [])[1] || '';
          var saisie = P.champ({ etiquette: 'Retape les 4 chiffres de ton nouveau code', inputmode: 'numeric', max: 4, classe: 'cc-chiffres', autocomplete: 'off' });
          var m4 = P.zoneMessage();
          var note = P.bouton('Je l\'ai noté', { type: 'submit', classe: 'cc-principal' });
          zoneCode.appendChild(el('p', { class: 'cc-code cc-code-grand' }, rep.code_affiche));
          zoneCode.appendChild(el('p', null, rep.message));
          zoneCode.appendChild(P.formulaire([saisie, note, m4], function () {
            if (saisie.input.value.replace(/\D/g, '') !== chiffres) {
              P.message(m4, 'Ce ne sont pas les bons chiffres : regarde ton nouveau code et recopie-le.', 'erreur');
              saisie.input.focus();
              return;
            }
            O.vider(zoneCode);
            P.message(m2, 'Ton nouveau code est noté ; l\'ancien ne marche plus.', 'ok');
          }));
          saisie.input.focus();
        });
      });
      zoneCode.appendChild(el('p', null, 'L\'ancien code ne marchera plus.' + (CC.applicationsBranchees() ? ' Les codes de tes applications restent valables.' : '')));
      zoneCode.appendChild(el('div', { class: 'cc-actions' }, [oui, non]));
    });
    var debloquer = P.bouton('Débloquer le réseau de la salle');
    debloquer.addEventListener('click', function () {
      Prof.debloquerReseau().then(function (rep) { P.message(m2, rep.ok ? 'Le compteur d\'essais de ce réseau est remis à zéro.' : rep.message, rep.ok ? 'ok' : 'erreur'); });
    });
    var conf = P.champ({ etiquette: 'Écris SUPPRIMER pour confirmer', max: 12, capitales: true });
    var m3 = P.zoneMessage();
    return el('details', { class: 'cc-carte' }, [el('summary', null, 'Réglages de mon espace'),
      /* Masqué tant qu'aucune application n'est branchée : son code serait refusé (aucun connecteur) */
      CC.applicationsBranchees() ? el('h3', null, 'Ajouter un espace d\'application') : null,
      !CC.applicationsBranchees() ? null : P.formulaire([autre, P.bouton('Relier cet espace', { type: 'submit' }), m1], function () {
        Prof.lierCode(autre.input.value).then(function (rep) {
          P.message(m1, rep.message, rep.ok ? 'ok' : 'erreur');
          if (rep.ok) rafraichirEspace();
        });
      }),
      el('h3', null, 'Mon code'),
      el('div', { class: 'cc-actions' }, [nouveau, debloquer]), zoneCode, m2,
      el('h3', null, 'Supprimer mon espace'),
      el('p', { class: 'petit' }, 'Tes classes communes disparaissent ; les comptes des élèves restent, ainsi que tes espaces dans chaque application.'),
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
      alerteCatalogue();
      main.appendChild(barreEspace());
      main.appendChild(el('p', { class: 'cc-fil' }, el('a', { href: '#/' }, '← Mes classes')));
      if (!rep.ok) { main.appendChild(el('p', { class: 'cc-message cc-erreur', role: 'alert' }, rep.message)); return; }
      var journal = r[1].ok ? r[1].journal : [];
      if (inviter) return ecranInviter(rep.classe);
      var c = rep.classe;
      /* 0010 v5 : commun_prof_classe ne dit pas si la classe est archivée ; commun_prof_ouvrir, si */
      if (c.archivee == null) {
        var x = ((espace && espace.classes) || []).filter(function (k) { return k.id === c.id; })[0];
        c.archivee = !!(x && x.archivee);
      }
      var titre = el('h2', { class: 'cc-titre-section', tabindex: '-1' }, c.nom);
      main.appendChild(titre);
      if (messageClasse) { main.appendChild(el('p', { class: 'cc-message cc-ok', role: 'status' }, messageClasse)); messageClasse = null; }
      main.appendChild(blocLienClasse(c));
      main.appendChild(blocTableauxClasse(c));
      main.appendChild(blocEleves(c, rep.eleves, journal));
      main.appendChild(blocJournal(journal));
      if (CC.disponible('commun_prof_retours')) main.appendChild(blocAvis(c));
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
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(c.lien).then(fait, function () { P.message(m, 'Copie impossible : sélectionne le lien.', 'erreur'); });
      else P.message(m, 'Copie impossible : sélectionne le lien.', 'erreur');
    });
    var inviter = el('a', { href: '#/classe/' + encodeURIComponent(c.id) + '/inviter', class: 'cc-bouton cc-principal' }, 'Inviter les élèves (à projeter)');
    return el('section', { class: 'cc-carte cc-lien-classe' }, [
      el('div', { class: 'cc-lien-texte' }, [
        el('p', null, ['Code de classe : ', el('span', { class: 'cc-code cc-code-moyen' }, c.code), ' · ', c.ouverte ? 'inscriptions ouvertes' : 'inscriptions fermées']),
        el('p', { class: 'cc-lien-url' }, el('a', { href: c.lien }, c.lien)),
        el('div', { class: 'cc-actions' }, [inviter, copier]), m
      ]),
      qr ? el('div', { class: 'cc-qr', role: 'img', 'aria-label': 'QR code du lien de la classe ' + c.nom, html: qr }) : el('p', { class: 'petit' }, 'QR code indisponible (assets/qrcode-generator.js n\'a pas pu se charger).')
    ]);
  }

  /* L'écran à projeter : le code de classe en très grand et le QR code, rien d'autre */
  function ecranInviter(c) {
    var qr = qrSvg(c.lien);
    var titre = el('h2', { class: 'cc-inviter-titre', tabindex: '-1' }, 'Rejoindre ' + c.nom);
    main.appendChild(el('section', { class: 'cc-inviter' }, [
      titre,
      qr ? el('div', { class: 'cc-qr cc-qr-grand', role: 'img', 'aria-label': 'QR code du lien de la classe', html: qr }) : null,
      el('p', null, 'Ou va sur ' + c.lien.replace(/^https:\/\//, '').replace(/\?.*$/, '') + ', crée ton code (ou entre avec), puis « Ma classe », « Rejoindre une classe », et tape le code de classe :'),
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
      el('p', { class: 'petit cc-suivi' }, 'L\'XP et les crédits sont pour ton suivi : les élèves ne voient que leur propre solde, jamais un total ni un classement.')
    ]);
    if (!eleves.length) { sec.appendChild(el('p', { class: 'vide' }, 'Personne encore. Projette l\'écran « Inviter les élèves ».')); return sec; }
    var hfProf = (cat.hauts_faits || []).filter(function (h) { return h.accord ? h.accord === 'enseignant' : h.application === 'commun'; });
    sec.appendChild(el('ul', { class: 'cc-eleves' }, eleves.map(function (e) { return carteEleve(c, e, journal, hfProf); })));
    return sec;
  }

  function carteEleve(c, e, journal, hfProf) {
    var av = el('div', { class: 'cc-avatar-cadre cc-moyen' });
    CC.dessinerAvatar(av, e.avatar, { etat: 'repos', taille: 'moyen', catalogue: cat, pseudo: e.pseudo });
    var hfs = (e.hauts_faits || []).map(function (h) { return K.nomHf(h.application, h.id) + ' (' + (h.application === 'commun' ? 'site et enseignant·e' : K.app(h.application).nom) + ')'; });
    var av2 = avancement(e, journal);
    var trophees = (e.trophees || []).filter(function (t) { return typeof t === 'object'; });
    var actions = el('div', { class: 'cc-eleve-actions' });

    /* Attribuer de l'XP avec un motif */
    var xp = P.champ({ etiquette: 'XP (1 à 50)', type: 'number', mini: 1, maxi: 50, inputmode: 'numeric', valeur: '10', classe: 'cc-nombre' });
    var motif = P.champ({ etiquette: 'Motif', aide: 'De 3 à 80 caractères ; l\'élève le lit dans sa planque.', max: 80, exemple: 'Aide à un camarade' });
    var m1 = P.zoneMessage();
    var fAttr = P.formulaire([el('div', { class: 'cc-en-ligne' }, [xp, motif]), P.bouton('Attribuer', { type: 'submit', classe: 'cc-principal' }), m1], function () {
      Prof.attribuerXp(e.compte, parseInt(xp.input.value, 10), motif.input.value).then(function (rep) {
        if (!rep.ok) { P.message(m1, rep.message, 'erreur'); return; }
        P.annoncer(e.pseudo + ' : +' + rep.xp + ' XP (« ' + motif.input.value.trim() + ' »).', 'ok', { suivi: true });
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
    var fHf = !hfProf.length ? el('p', { class: 'petit' }, 'Aucun haut fait d\'enseignant·e pour l\'instant : ils arrivent avec le catalogue.')
      : restants.length ? P.formulaire([el('div', { class: 'cc-champ' }, [el('label', { for: selHf.id }, 'Haut fait'), selHf]),
      P.bouton('Accorder', { type: 'submit' }), m2], function () {
      var v = selHf.value.split('/');
      Prof.accorder(e.compte, v[0], v[1]).then(function (rep) {
        if (!rep.ok) { P.message(m2, rep.message, 'erreur'); return; }
        P.annoncerNouveautes(rep.nouveautes, cat);
        router();
      });
    }) : el('p', { class: 'petit' }, 'Tous les hauts faits d\'enseignant·e sont déjà accordés.');

    /* Offrir un trophée (un objet qui ne s'achète pas), avec un motif que l'élève lit */
    var m4 = P.zoneMessage();
    var dejaTr = (e.trophees || []).map(function (t) { return typeof t === 'string' ? t : t.element; });
    var aOffrir = (cat.elements || []).filter(function (x) { return x.acces === 'haut_fait' && x.famille === 'classe' && dejaTr.indexOf(x.id) < 0; });
    var selTr = el('select', { id: P.idUnique('trophee'), class: 'cc-select' }, aOffrir.map(function (x) { return el('option', { value: x.id }, x.nom); }));
    var motifTr = P.champ({ etiquette: 'Motif', aide: 'De 3 à 80 caractères ; l\'élève le lit dans ses trophées.', max: 80, exemple: 'A rangé la salle informatique' });
    var fTr = !CC.disponible('commun_prof_offrir') ? el('p', { class: 'petit' }, 'Offrir un trophée arrive avec le catalogue des avatars.')
      : aOffrir.length ? P.formulaire([el('div', { class: 'cc-champ' }, [el('label', { for: selTr.id }, 'Trophée'), selTr]), motifTr,
      P.bouton('Offrir', { type: 'submit' }), m4], function () {
      Prof.offrir(e.compte, selTr.value, motifTr.input.value).then(function (rep) {
        if (!rep.ok) { P.message(m4, rep.message, 'erreur'); return; }
        var texte = e.pseudo + ' : trophée offert (' + rep.nom + ', « ' + CC.nettoyerTexte(motifTr.input.value, 3, 80) + ' »).';
        P.annoncer(texte, 'ok', { suivi: true });
        messageClasse = texte;
        router();
      });
    }) : el('p', { class: 'petit' }, 'Cet·te élève a déjà tous les trophées.');

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
    actions.appendChild(el('details', null, [el('summary', null, 'Offrir un trophée'), fTr]));
    actions.appendChild(el('details', null, [el('summary', null, 'Pseudo, code, retrait'), fRen, el('div', { class: 'cc-actions' }, [nc, retirer]), zoneNc, zoneRet]));
    if (CC.niveauActif() && NIVEAUX.length) actions.appendChild(el('details', null, [el('summary', null, 'Niveau'), formNiveau(NIVEAUX, e.niveau, 'Enregistrer', function (v) {
      return Prof.niveauEleve(e.compte, v);
    })]));

    return el('li', { class: 'cc-eleve' }, [
      el('div', { class: 'cc-eleve-tete' }, [av, el('div', null, [
        el('p', { class: 'cc-eleve-nom' }, e.pseudo),
        CC.niveauActif() && libelleNiveau(e.niveau) ? el('p', { class: 'petit' }, libelleNiveau(e.niveau)) : null,
        el('p', { class: 'petit' }, 'Dernière visite : ' + P.depuis(e.vu_le)),
        el('p', { class: 'petit cc-suivi' }, ['XP gagnée : ', el('strong', null, String(e.xp)), ' · crédits : ', el('strong', null, String(e.credits))]),
        el('p', { class: 'petit cc-suivi' }, ['Code : '].concat((e.codes || []).map(function (x, i) { return el('span', { class: 'cc-code' }, (i ? ', ' : '') + x); })))
      ])]),
      el('div', { class: 'cc-eleve-corps' }, [
        el('p', { class: 'cc-petit-titre' }, 'Avancement'),
        av2.length ? el('ul', { class: 'cc-puces' }, av2.map(function (x) { return el('li', null, [el('strong', null, x.nom), ' : ' + x.texte]); }))
          : el('p', { class: 'petit' }, 'Rien encore.'),
        el('p', { class: 'cc-petit-titre' }, 'Hauts faits'),
        hfs.length ? el('ul', { class: 'cc-puces' }, hfs.map(function (n) { return el('li', null, n); })) : el('p', { class: 'petit' }, 'Pas encore.'),
        el('p', { class: 'cc-petit-titre' }, 'Trophées'),
        trophees.length ? el('ul', { class: 'cc-puces cc-trophees' }, trophees.map(function (t) {
          return el('li', null, [el('strong', null, t.nom), t.motif ? ' : « ' + t.motif + ' »' : (t.origine === 'haut_fait' ? ' (haut fait)' : '')]);
        })) : el('p', { class: 'petit' }, 'Pas encore.')
      ]),
      actions
    ]);
  }

  function libelleNiveau(id) { var n = NIVEAUX.filter(function (x) { return x.id === id; })[0]; return n ? n.libelle : null; }

  /* Un choix de niveau (libellés des référentiels du site) et son bouton */
  function formNiveau(niveaux, actuel, texte, envoyer) {
    var id = P.idUnique('niveau');
    var sel = el('select', { id: id, class: 'cc-select' }, niveaux.map(function (n) {
      return el('option', { value: n.id, selected: n.id === actuel ? true : null }, n.libelle);
    }));
    var m = P.zoneMessage();
    return P.formulaire([el('div', { class: 'cc-champ' }, [el('label', { for: id }, 'Niveau'), sel]), P.bouton(texte, { type: 'submit' }), m], function () {
      envoyer(sel.value).then(function (rep) {
        if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
        messageClasse = 'Niveau enregistré : ' + libelleNiveau(sel.value) + '.';
        router();
      });
    });
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

  /* ── Les avis anonymes des élèves (T163, migration 0013) ──────────
     Par paquets d'au moins 5, des semaines finies : la base ne rend rien d'autre.
     Aucun classement, aucune comparaison entre classes : une classe, ou tout le monde. */

  var AVIS_Q = [
    { id: 'difficulte', titre: 'C\'était…', valeurs: [['trop_facile', 'trop facile'], ['bien', 'bien'], ['trop_dur', 'trop dur']] },
    { id: 'compris', titre: 'J\'ai compris', valeurs: [['oui', 'oui'], ['a_peu_pres', 'à peu près'], ['non', 'non']] },
    { id: 'fini', titre: 'J\'ai fini', valeurs: [['oui', 'oui'], ['presque', 'presque'], ['non', 'non']] },
    { id: 'plu', titre: 'Ça m\'a plu', valeurs: [['1', '1 ★'], ['2', '2 ★'], ['3', '3 ★'], ['4', '4 ★'], ['5', '5 ★']] }
  ];
  var AVIS_REMARQUES = { consignes: 'Consignes pas claires', trop_de_texte: 'Trop de texte à lire', exemples: 'Il faut plus d\'exemples',
    bug: 'Quelque chose ne marchait pas', telephone: 'Pas pratique sur téléphone', encore: 'J\'en veux d\'autres comme ça' };

  function titreAvis(g) {
    if (g.ressource.indexOf('sequence:') === 0) {
      var sid = g.ressource.slice(9), s = sequencesBib.filter(function (x) { return x.id === sid; })[0];
      return 'Séquence : ' + (s ? s.titre : sid);
    }
    var f = fichesBib[g.ressource];
    return f ? f.titre : g.ressource;
  }
  function partieAvis(g) {
    if (!g.partie) return '';
    var m = g.partie.match(/-(\d+)$/);
    return m ? 'feuille ' + m[1] : g.partie;
  }
  /* Additionne des paquets : le total d'une ressource, ou d'une séquence */
  function sommeLots(lots) {
    var s = { n: 0, plu: {}, difficulte: {}, compris: {}, fini: {}, remarques: {} };
    lots.forEach(function (l) {
      s.n += l.n;
      ['plu', 'difficulte', 'compris', 'fini', 'remarques'].forEach(function (k) {
        Object.keys(l[k] || {}).forEach(function (v) { s[k][v] = (s[k][v] || 0) + (l[k][v] || 0); });
      });
    });
    return s;
  }
  function pc(a, n) { return n ? Math.round(100 * a / n) : 0; }

  /* Une ligne par question : barre empilée (décorative) et le texte des nombres (l'essentiel, sans la couleur).
     Plein : ce qu'on vise (bien, oui, 4-5 étoiles) ; hachuré : entre les deux ; pointillé : ce qui alerte. */
  function barreAvis(q, s) {
    var rep = s[q.id] || {}, total = q.valeurs.reduce(function (a, v) { return a + (rep[v[0]] || 0); }, 0);
    var barre = el('div', { class: 'cc-avis-barre', 'aria-hidden': 'true' }, q.valeurs.map(function (v, i) {
      var x = rep[v[0]] || 0;
      return x ? el('span', { class: 'cc-avis-seg cc-avis-seg-' + (q.id === 'plu' ? 'p' + v[0] : q.id === 'difficulte' ? [1, 0, 2][i] : i), style: 'width:' + (100 * x / total) + '%' }) : null;
    }).filter(Boolean));
    var texte = total ? q.valeurs.map(function (v) { return v[1] + ' ' + (rep[v[0]] || 0) + ' (' + pc(rep[v[0]] || 0, total) + ' %)'; }).join(' · ') : 'pas de réponse';
    return el('div', { class: 'cc-avis-ligne' }, [el('p', { class: 'cc-avis-q' }, [el('strong', null, q.titre), ' : ' + texte + (total && total < s.n ? ' (' + total + ' réponses)' : '')]), total ? barre : null]);
  }

  function carteAvis(g, avecMots, recharger) {
    var s = sommeLots(g.lots);
    var titre = titreAvis(g), partie = partieAvis(g);
    var rem = Object.keys(AVIS_REMARQUES).filter(function (k) { return s.remarques[k]; })
      .sort(function (a, b) { return s.remarques[b] - s.remarques[a]; })
      .map(function (k) { return el('li', null, AVIS_REMARQUES[k] + ' : ' + s.remarques[k]); });
    var enfants = [
      el('h3', { class: 'cc-avis-titre' }, [titre, partie ? el('span', { class: 'petit' }, ' · ' + partie) : null]),
      el('p', { class: 'petit' }, s.n + ' avis' + (g.lots.length > 1 ? ', en ' + g.lots.length + ' paquets' : '') + ' · jusqu\'à la semaine du ' + P.date(g.lots[g.lots.length - 1].semaine))
    ].concat(AVIS_Q.map(function (q) { return barreAvis(q, s); }));
    if (rem.length) enfants.push(el('div', { class: 'cc-avis-ligne' }, [el('p', { class: 'cc-avis-q' }, el('strong', null, 'Remarques choisies')), el('ul', { class: 'cc-avis-rem' }, rem)]));
    if (g.lots.length > 1) {
      enfants.push(el('details', { class: 'cc-avis-evolution' }, [el('summary', null, 'L\'évolution, paquet par paquet'),
        el('div', { class: 'cc-table-defile' }, el('table', { class: 'cc-avis-table' }, [
          el('thead', null, el('tr', null, ['Jusqu\'à la semaine du', 'Avis', 'Trop dur', 'Compris : oui', 'Fini : oui'].map(function (x) { return el('th', { scope: 'col' }, x); }))),
          el('tbody', null, g.lots.map(function (l) {
            return el('tr', null, [el('td', null, P.date(l.semaine)), el('td', null, String(l.n)), el('td', null, pc(l.difficulte.trop_dur, l.n) + ' %'),
              el('td', null, pc(l.compris.oui, l.n) + ' %'), el('td', null, pc(l.fini.oui, l.n) + ' %')]);
          }))]))]));
    }
    if (avecMots && g.mots && g.mots.length) {
      var m = P.zoneMessage();
      enfants.push(el('div', { class: 'cc-avis-ligne cc-masquable-bloc' }, [
        el('p', { class: 'cc-avis-q' }, [el('strong', null, 'Les mots (' + g.mots.length + ')'), ' : lus par toi seul·e, dans un ordre mélangé.']),
        el('ul', { class: 'cc-avis-mots' }, g.mots.map(function (x) {
          var b = P.bouton('Effacer', { classe: 'cc-discret' });
          b.setAttribute('aria-label', 'Effacer le mot « ' + x.mot + ' »');
          b.addEventListener('click', function () {
            Prof.effacerMotRetour(x.id).then(function (rep) { if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; } recharger('Le mot est effacé.'); });
          });
          return el('li', null, [el('q', null, x.mot), ' ', b]);
        })), m]));
    }
    return el('article', { class: 'cc-avis-carte' }, enfants);
  }

  /* Regrouper par séquence (si la bibliothèque a des séquences) : une ressource compte dans chaque séquence qui la cite */
  function parSequence(groupes) {
    var res = [];
    sequencesBib.forEach(function (s) {
      var ids = [];
      (s.etapes || []).forEach(function (e) { (e.ressources || []).forEach(function (r) { ids.push(typeof r === 'string' ? r : r && r.ressource); }); });
      var lots = [], noms = [];
      groupes.forEach(function (g) {
        if (ids.indexOf(g.ressource) >= 0 || g.ressource === 'sequence:' + s.id) { lots = lots.concat(g.lots); noms.push(titreAvis(g) + (g.partie ? ' · ' + partieAvis(g) : '')); }
      });
      if (lots.length) res.push({ titre: s.titre, noms: noms, total: sommeLots(lots) });
    });
    return res;
  }

  /* L'export, pour mettre en regard le verdict du ou de la Critique : une ligne par paquet, question et valeur */
  function exporter(donnees, c, format) {
    var lignes = [];
    donnees.ressources.forEach(function (g) {
      g.lots.forEach(function (l) {
        ['plu', 'difficulte', 'compris', 'fini', 'remarques'].forEach(function (q) {
          Object.keys(l[q] || {}).forEach(function (v) {
            lignes.push({ portee: c ? 'classe' : 'tous', classe: c ? c.nom : '', ressource: g.ressource, titre: titreAvis(g), partie: g.partie,
              semaine: l.semaine, avis_du_paquet: l.n, question: q, valeur: v, nombre: l[q][v] });
          });
        });
      });
    });
    var nom = 'avis-eleves-' + (c ? c.code : 'tous') + '-' + new Date().toISOString().slice(0, 10);
    var contenu, type;
    if (format === 'json') {
      contenu = JSON.stringify({ exporte_le: new Date().toISOString(), portee: c ? 'classe' : 'tous', seuil: donnees.seuil, lignes: lignes }, null, 2);
      type = 'application/json';
    } else {
      var cols = ['portee', 'classe', 'ressource', 'titre', 'partie', 'semaine', 'avis_du_paquet', 'question', 'valeur', 'nombre'];
      var champ = function (x) { x = String(x == null ? '' : x); return /[";\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x; };
      contenu = String.fromCharCode(0xFEFF) + [cols.join(';')].concat(lignes.map(function (l) { return cols.map(function (k) { return champ(l[k]); }).join(';'); })).join('\r\n');
      type = 'text/csv;charset=utf-8';
    }
    var a = el('a', { href: URL.createObjectURL(new Blob([contenu], { type: type })), download: nom + '.' + format });
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  /* Le lien d'une ressource pour la classe : l'adresse, plus ?classe=CODE (les avis portent alors la classe) */
  function outilLien(c) {
    var champ = P.champ({ etiquette: 'Adresse d\'une ressource en ligne', aide: 'Colle l\'adresse d\'une feuille de TD ou d\'une séquence du site.', max: 300,
      exemple: 'https://babash.github.io/Babash-NSI-SNT/…' });
    var sortie = el('div', { class: 'cc-avis-lien' });
    var m = P.zoneMessage();
    var f = P.formulaire([champ, P.bouton('Faire le lien de la classe', { type: 'submit' }), m, sortie], function () {
      O.vider(sortie);
      var u;
      try { u = new URL(champ.input.value.trim()); } catch (e) { u = null; }
      if (!u || !/^https:$/.test(u.protocol) || !/(^|\.)babash\.github\.io$/.test(u.hostname)) { P.message(m, 'Colle une adresse du site (https://babash.github.io/…).', 'erreur'); return; }
      u.searchParams.set('classe', c.code);
      P.message(m, '', 'ok');
      var qr = qrSvg(u.href);
      sortie.appendChild(el('p', { class: 'cc-lien-url' }, el('a', { href: u.href }, u.href)));
      if (qr) sortie.appendChild(el('div', { class: 'cc-qr', role: 'img', 'aria-label': 'QR code de ce lien', html: qr }));
    });
    return el('details', { class: 'cc-avis-outil' }, [el('summary', null, 'Le lien d\'une ressource pour cette classe'),
      el('p', { class: 'petit' }, 'Les élèves qui ouvrent la ressource par ce lien (ou son QR code) donnent un avis rattaché à la classe, jamais à leur nom. Sans ce lien, leur avis compte pour « tout le monde ».'), f]);
  }

  function blocAvis(c) {
    var corps = el('div', { class: 'cc-avis-corps' });
    var details = el('details', { class: 'cc-carte cc-avis' }, [
      el('summary', null, c ? 'Les avis des élèves sur les ressources (anonymes)' : 'Les avis des élèves de tout le monde (anonymes)'),
      el('p', { class: 'petit' }, c
        ? 'À la fin d\'une ressource en ligne, chaque élève peut donner un avis en dix secondes, sans nom ni code. Ils s\'affichent par paquets d\'au moins 5, le lundi qui suit leur semaine : personne ne peut savoir qui a répondu quoi.'
        : 'Les avis de toutes les classes et des élèves sans classe, par paquets d\'au moins 5, sans aucun mot. Les avis d\'une classe sont sur sa page.'),
      c ? outilLien(c) : null,
      corps]);
    var charge = false;
    function charger(message) {
      O.vider(corps);
      corps.appendChild(el('p', { class: 'vide' }, 'Chargement des avis…'));
      Prof.retours(c ? c.id : null).then(function (rep) {
        O.vider(corps);
        if (message) corps.appendChild(el('p', { class: 'cc-message cc-ok', role: 'status' }, message));
        if (!rep.ok) { corps.appendChild(el('p', { class: 'cc-message cc-erreur', role: 'alert' }, rep.message)); return; }
        var groupes = (rep.ressources || []).filter(function (g) { return g.lots && g.lots.length; });
        if (!groupes.length) {
          corps.appendChild(el('p', { class: 'vide' }, 'Pas encore d\'avis à montrer : il en faut au moins 5 pour une ressource, d\'une semaine finie.'));
          return;
        }
        groupes.sort(function (a, b) { return (titreAvis(a) + a.partie).localeCompare(titreAvis(b) + b.partie, 'fr'); });
        var exp = el('div', { class: 'cc-actions' });
        var bCsv = P.bouton('Exporter (CSV)'), bJson = P.bouton('Exporter (JSON)');
        bCsv.addEventListener('click', function () { exporter(rep, c, 'csv'); });
        bJson.addEventListener('click', function () { exporter(rep, c, 'json'); });
        exp.appendChild(bCsv); exp.appendChild(bJson);
        corps.appendChild(exp);
        var seqs = parSequence(groupes);
        if (seqs.length) {
          corps.appendChild(el('h3', { class: 'cc-avis-sous-titre' }, 'Par séquence'));
          corps.appendChild(el('div', { class: 'cc-avis-grille' }, seqs.map(function (s) {
            return el('article', { class: 'cc-avis-carte' }, [el('h3', { class: 'cc-avis-titre' }, s.titre),
              el('p', { class: 'petit' }, s.total.n + ' avis · ' + s.noms.join(', '))].concat(AVIS_Q.map(function (q) { return barreAvis(q, s.total); })));
          })));
          corps.appendChild(el('h3', { class: 'cc-avis-sous-titre' }, 'Par ressource'));
        }
        corps.appendChild(el('div', { class: 'cc-avis-grille' }, groupes.map(function (g) { return carteAvis(g, !!c, charger); })));
      });
    }
    details.addEventListener('toggle', function () { if (details.open && !charge) { charge = true; charger(); } });
    return details;
  }

  function blocReglagesClasse(c) {
    var archivable = CC.disponible('commun_prof_archiver_classe');
    var nom = P.champ({ etiquette: 'Nom de la classe', max: 40, valeur: c.nom });
    var ouverte = P.caseACocher('Inscriptions ouvertes');
    ouverte.input.checked = !!c.ouverte;
    var apps = choixApplications(c.applications);
    var m = P.zoneMessage();
    var conf = P.champ({ etiquette: 'Écris SUPPRIMER pour confirmer', max: 12, capitales: true });
    var m2 = P.zoneMessage();
    return el('details', { class: 'cc-carte' }, [el('summary', null, 'Réglages de la classe'),
      P.formulaire([nom, ouverte, apps, P.bouton('Enregistrer', { type: 'submit', classe: 'cc-principal' }), m], function () {
        Prof.modifierClasse(c.id, nom.input.value, ouverte.input.checked, apps.valeurs()).then(function (rep) {
          if (!rep.ok) { P.message(m, rep.message, 'erreur'); return; }
          rafraichirEspace().then(router);
        });
      }),
      /* Archiver (migration 0010, réglage COMPTE_COMMUN_CATALOGUE) : avant, seule la case
         « Inscriptions ouvertes » existe, et la page ne prétend pas archiver */
      archivable ? el('h3', null, c.archivee ? 'Désarchiver la classe' : 'Archiver la classe') : null,
      archivable ? el('p', { class: 'petit' }, c.archivee ? 'La classe revient avec les autres ; ses inscriptions restent fermées (case ci-dessus pour les rouvrir).'
        : 'Ferme les inscriptions et range la classe à part. Rien n\'est effacé.') : null,
      !archivable ? null : (function () {
        var b = P.bouton(c.archivee ? 'Désarchiver la classe' : 'Archiver la classe');
        var m3 = P.zoneMessage();
        b.addEventListener('click', function () {
          Prof.archiverClasse(c.id, !c.archivee).then(function (rep) {
            if (!rep.ok) { P.message(m3, rep.message, 'erreur'); return; }
            messageClasse = c.archivee ? 'La classe est désarchivée.' : 'La classe est archivée : inscriptions fermées.';
            rafraichirEspace().then(router);
          });
        });
        return el('div', null, [b, m3]);
      })(),
      CC.niveauActif() && NIVEAUX.length ? el('h3', null, 'Le niveau de toute la classe') : null,
      CC.niveauActif() && NIVEAUX.length ? el('p', { class: 'petit' }, 'À la rentrée, par exemple : tous les élèves de la classe passent au niveau choisi.') : null,
      CC.niveauActif() && NIVEAUX.length ? formNiveau(NIVEAUX, null, 'Changer pour toute la classe', function (v) { return Prof.niveauClasse(c.id, v); }) : null,
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
