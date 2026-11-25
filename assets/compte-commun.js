/* ═══════════════════════════════════════════════════════════════
   Le compte commun : un code, un compte et un avatar pour toutes
   les applications (T101, T101b). Architecte.

   Une seule interface, deux façons de répondre :
   - « demo » : des données fictives, en mémoire. Rien n'est envoyé,
     rien n'est gardé : recharger la page efface tout. C'est le mode
     par défaut, tant que reglages.js ne dit pas COMPTE_COMMUN_EN_LIGNE: true ;
   - « supabase » : les fonctions commun_… de la base unique (SQL 0007 v2.3
     et 0008, en base depuis le 24/11/2026), avec la clé publique du projet.
   Mode d'emploi, règles et exemple pour une application : docs/COMPTE-COMMUN.md.

   Chaque appel porte le nom et les paramètres de la fonction SQL
   (commun_creer, p_pseudo…), et rend toujours une promesse qui se
   résout en { ok: true, … } ou { ok: false, message } : jamais d'exception.
   Ainsi une page ne s'arrête jamais à cause du compte commun.

   Utilisé par eleve/ (assets/planque.js) et enseignant/
   (assets/espace-enseignant.js). Une autre page (feuille de TD,
   QuizzNSI, calendrier) peut le charger seul et appeler
   CompteCommun.configurer({ en_ligne, url, cle_publique }).

   L'avatar se dessine par le module du Designer (assets/equipage.js,
   Equipage.creer(element, description, options)) ; s'il manque, un
   dessin de remplacement simple prend sa place.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var CLE_SESSION = 'compte-commun:session';
  var RACINE = (function () {
    try { return new URL('..', document.currentScript.src).href; } catch (e) { return ''; }
  })();

  /* ── Outils de texte, communs aux deux modes ──────────────────── */

  function car(n) { return String.fromCharCode(n); }

  /* Les caractères de contrôle et invisibles, refusés comme dans commun.nettoyer_texte */
  var INVISIBLES = new RegExp('[' + car(0) + '-' + car(31) + car(127) + '-' + car(159) + car(173) +
    car(8203) + '-' + car(8207) + car(8232) + '-' + car(8238) + car(8288) + '-' + car(8303) + car(65279) + ']');
  var DIACRITIQUES = new RegExp('[' + car(0x300) + '-' + car(0x36f) + ']', 'g');

  /* La forme canonique d'un code (comme commun.normaliser_code) : majuscules,
     sans accent, sans espace ni tiret. « clavier fresque 482 » = « CLAVIER-FRESQUE-482 ». */
  function normaliserCode(s) {
    return String(s == null ? '' : s).slice(0, 80)
      .replace(/œ/g, 'oe').replace(/Œ/g, 'OE')
      .normalize('NFD').replace(DIACRITIQUES, '')
      .toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  /* Un texte propre de min à max caractères, sinon null (comme commun.nettoyer_texte) */
  function nettoyerTexte(t, min, max) {
    var s = String(t == null ? '' : t).slice(0, 200);
    if (INVISIBLES.test(s.replace(/[\t\n\r]/g, ' '))) return null;
    s = s.replace(/\s+/g, ' ').trim();
    var n = Array.from(s).length;
    return n >= min && n <= max ? s : null;
  }
  function nettoyerPseudo(t) { return nettoyerTexte(t, 2, 24); }

  function copie(x) { return x == null ? x : JSON.parse(JSON.stringify(x)); }
  function maintenant() { return new Date().toISOString(); }

  /* Le jeton de l'élève sur cet appareil (décision de l'enseignant, 24/11) :
     - par défaut, dans l'onglet seulement (sessionStorage) : fermer l'onglet suffit à partir,
       et la base refuse le jeton après 1 jour ;
     - avec « C'est mon téléphone », dans le navigateur (localStorage), 30 jours après le dernier usage.
     Tous les sites de babash.github.io sont à la même origine : le jeton posé ici est lu par les
     autres applications. Jamais de code ni de jeton dans une adresse. */
  function magasin(nom) {
    try { var m = window[nom]; m.getItem('x'); return m; } catch (e) { return null; }
  }
  function lireStockage(nom) {
    var l = [magasin('sessionStorage'), magasin('localStorage')];
    for (var i = 0; i < l.length; i++) {
      if (!l[i]) continue;
      try { var v = JSON.parse(l[i].getItem(nom) || 'null'); if (v) return v; } catch (e) { /* illisible : ignoré */ }
    }
    return null;
  }
  function ecrireStockage(nom, valeur, durable) {
    var s = magasin('sessionStorage'), l = magasin('localStorage');
    try { if (s) s.removeItem(nom); } catch (e) { /* rien */ }
    try { if (l) l.removeItem(nom); } catch (e) { /* rien */ }
    if (valeur == null) return;
    var cible = durable ? l : s;
    try { if (cible) cible.setItem(nom, JSON.stringify(valeur)); } catch (e) { /* navigation privée : la session vaut pour cette page */ }
  }

  /* Un code ou un jeton ne passe jamais par une adresse : s'il y en a un (lien mal fait, copie
     d'écran), il est retiré de la barre d'adresse et n'est pas utilisé. Le code de classe
     (4 lettres, public) reste permis. */
  (function nettoyerAdresse() {
    try {
      var u = new URL(location.href), sale = false;
      ['code', 'jeton', 'token', 'code_prof', 'cle'].forEach(function (k) { if (u.searchParams.has(k)) { u.searchParams.delete(k); sale = true; } });
      if (/(^|[#&])(code|jeton|token)=/i.test(u.hash.slice(1))) { u.hash = ''; sale = true; }
      if (sale) {
        history.replaceState(null, '', u.pathname + u.search + u.hash);
        if (window.console) console.warn('[compte commun] un code ou un jeton était dans l\'adresse : retiré, jamais utilisé.');
      }
    } catch (e) { /* ancien navigateur */ }
  })();

  /* ═════════════════════════════════════════════════════════════
     Mode « supabase » : les fonctions commun_… de la base unique.
     Seule la clé publique (« anon » ou « publishable ») va ici.
     ═════════════════════════════════════════════════════════════ */

  /* Les messages d'une erreur de l'API, en français, sans jargon */
  function messageHttp(statut) {
    if (statut === 404) return 'Cette fonction du compte commun n\'est pas encore installée sur la base. Préviens ton enseignant·e.';
    if (statut === 401 || statut === 403) return 'La base refuse la clé de cette page. Préviens ton enseignant·e.';
    if (statut === 429) return 'Trop de demandes en même temps : attends une minute, puis réessaie.';
    if (statut >= 500) return 'La base du compte commun ne répond pas pour l\'instant. Réessaie dans un moment.';
    return 'Le compte commun ne répond pas comme prévu (code ' + statut + '). Réessaie dans un moment.';
  }

  /* Les fonctions prévues par une migration à venir : la page le dit, sans rien envoyer */
  var FONCTIONS_A_VENIR = {
    commun_prof_offrir: 'Offrir un trophée arrive avec le catalogue des avatars (migration 0010).',
    commun_prof_archiver_classe: 'Archiver une classe arrive avec la migration 0010 : pour l\'instant, on ferme seulement ses inscriptions.',
    commun_prof_niveau_eleve: 'Le niveau arrive avec sa migration (T132e) : rien n\'est envoyé pour l\'instant.',
    commun_prof_niveau_classe: 'Le niveau arrive avec sa migration (T132e) : rien n\'est envoyé pour l\'instant.',
    commun_prof_retours: 'Les avis des élèves arrivent avec leur migration (0013) et le réglage RETOURS_ELEVES.',
    commun_prof_retour_effacer_mot: 'Les avis des élèves arrivent avec leur migration (0013) et le réglage RETOURS_ELEVES.'
  };

  /* Le réglage qui ouvre chaque fonction à venir, une fois sa migration appliquée */
  var catalogueEnBase = null;        // null : pas lu ou lecture ratée ; vrai seulement si commun_catalogue rend des objets à prix (0010)
  function ouverte(fonction) {
    if (/niveau/.test(fonction)) return !!reglage.niveau;
    /* Les avis des élèves (0013) : le réglage RETOURS_ELEVES */
    if (/_retour/.test(fonction)) return !!reglage.retours;
    /* Les fonctions de 0010 : le réglage COMPTE_COMMUN_CATALOGUE, et le catalogue vraiment en base (des objets
       à prix) ; ainsi, réglage à true trop tôt ou base revenue en arrière, la page ne propose rien d'impossible */
    if (fonction === 'commun_prof_offrir' || fonction === 'commun_prof_archiver_classe') return !!reglage.catalogue && catalogueEnBase === true;
    return !FONCTIONS_A_VENIR[fonction];
  }

  /* Un caractère invisible ou de mise en forme (copié-collé) : la base le refuse avec un message sur la
     longueur ; la page dit la vraie raison, sans rien envoyer. */
  var REFUS_CARACTERE = { ok: false, message: 'Un caractère spécial (invisible ou de mise en forme, souvent venu d\'un copier-coller) n\'est pas accepté : retape le texte au clavier.' };
  function caractereSpecial(t) { return t != null && INVISIBLES.test(String(t).replace(/[\t\n\r]/g, ' ')); }
  function textesPropres(params, noms) {
    return !noms.some(function (n) { return caractereSpecial(params[n]); });
  }

  function implementationSupabase(cfg) {
    var base = String(cfg.url || '').replace(/\/+$/, '');
    var HORS_LIGNE = { ok: false, hors_ligne: true, message: 'Pas de connexion : vérifie le wifi ou les données mobiles, puis réessaie. Rien n\'est perdu.' };
    return {
      nom: 'supabase',
      appeler: function (fonction, params) {
        if (typeof fetch !== 'function') {
          return Promise.resolve({ ok: false, message: 'Ce navigateur est trop ancien pour le compte commun.' });
        }
        if (FONCTIONS_A_VENIR[fonction] && !ouverte(fonction)) return Promise.resolve({ ok: false, a_venir: true, message: FONCTIONS_A_VENIR[fonction] });
        if (typeof navigator !== 'undefined' && navigator.onLine === false) return Promise.resolve(copie(HORS_LIGNE));
        var arret = typeof AbortController === 'function' ? new AbortController() : null;
        var minuteur = arret ? setTimeout(function () { arret.abort(); }, 20000) : null;
        return fetch(base + '/rest/v1/rpc/' + fonction, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', apikey: cfg.cle_publique },
          body: JSON.stringify(params || {}),
          signal: arret ? arret.signal : undefined,
          credentials: 'omit',
          referrerPolicy: 'no-referrer',
          cache: 'no-store'
        }).then(function (r) {
          if (r.ok) return r.json();
          return r.text().then(function (t) {
            /* Le détail technique va dans la console, jamais à l'écran (il peut citer le SQL) */
            if (window.console) console.warn('[compte commun] ' + fonction + ' : code ' + r.status + ' ' + t.slice(0, 300));
            return { ok: false, statut: r.status, message: messageHttp(r.status) };
          });
        }).then(function (rep) {
          return rep && typeof rep === 'object' ? rep : { ok: false, message: 'Réponse inattendue du compte commun. Réessaie dans un moment.' };
        }).catch(function (e) {
          if (e && e.name === 'AbortError') return { ok: false, hors_ligne: true, message: 'Le compte commun met trop de temps à répondre : la connexion est peut-être lente. Réessaie.' };
          return copie(HORS_LIGNE);
        }).then(function (rep) {
          if (minuteur) clearTimeout(minuteur);
          return rep;
        });
      }
    };
  }

  /* ═════════════════════════════════════════════════════════════
     Mode « demo » : la même logique que le SQL, en mémoire.
     Tout est fictif : aucun vrai code, aucun vrai pseudo, aucun nom.
     Les codes de démonstration commencent tous par DEMO.
     ═════════════════════════════════════════════════════════════ */

  var CATALOGUE_DEMO = (function () {
    var apps = [
      ['commun', 'Ressources NSI et SNT', 'https://babash.github.io/Babash-NSI-SNT/eleve/'],
      ['td', 'Feuilles de TD en ligne', 'https://babash.github.io/Babash-NSI-SNT/'],
      ['vacances', 'Calendrier des vacances', 'https://babash.github.io/Babash-NSI-SNT/calendrier/'],
      ['quizz_nsi', 'QuizzNSI', 'https://babash.github.io/quizz-nsi/'],
      ['gombessa', 'Expédition Gombessa', 'https://babash.github.io/gombessa/'],
      ['court_circuit', 'Court-circuit', 'https://babash.github.io/court-circuit/'],
      ['grand_oral', 'Hello GO', null],
      ['lagon', 'Lagon Arena', 'https://babash.github.io/lagon-arena/'],
      ['alien', 'Alien Python', 'https://babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python/']
    ].map(function (a) { return { id: a[0], nom: a[1], adresse: a[2] }; });

    /* [application, id, nom, description, catégorie, accord, récompenses, indice si secret] */
    var hauts = [
      ['commun', 'premiere-planque', 'Première planque', 'Entrer dans sa planque avec son code.', 'premiers_pas', 'serveur', []],
      ['commun', 'coup-de-main', 'Coup de main', 'Aider un·e camarade à comprendre, sans faire à sa place.', 'entraide', 'enseignant', ['cou:cle_usb']],
      ['commun', 'explication-claire', 'Explication claire', 'Expliquer une notion à la classe.', 'entraide', 'enseignant', ['main:telecommande']],
      ['td', 'premiere-feuille', 'Première feuille', 'Valider en ligne sa première feuille de TD.', 'premiers_pas', 'page', []],
      ['td', 'erreur-surmontee', 'Erreur surmontée', 'Valider un exercice après au moins un essai raté.', 'perseverance', 'page', ['compagnon:robot']],
      ['td', 'lecteur-de-traces', 'Lecteur de traces', 'Lire jusqu\'au bout le message d\'erreur de Python.', 'maitrise', 'page', [], 'Il paraît que certains messages d\'erreur cachent un indice.'],
      ['quizz_nsi', 'jusqu-au-bout', 'Jusqu\'au bout', 'Suivre un cours-quiz jusqu\'à la dernière question.', 'perseverance', 'page', []],
      ['vacances', 'dix-jours-differents', 'Dix jours différents', 'Faire un mini-jeu dix jours différents, dans l\'ordre que tu veux.', 'perseverance', 'page', []],
      ['court_circuit', 'premier-circuit', 'Premier circuit', 'Faire avancer son robot jusqu\'au bout d\'un circuit.', 'premiers_pas', 'serveur', []],
      ['court_circuit', 'sortie-de-la-grotte', 'Sortie de la grotte', 'Trouver la sortie de la grotte avec une boucle.', 'exploration', 'serveur', ['compagnon:roussette']],
      ['gombessa', 'premiere-plongee', 'Première plongée', 'Réussir sa première mission.', 'premiers_pas', 'serveur', ['compagnon:tortue']],
      ['lagon', 'premiere-manche', 'Première manche', 'Jouer une manche jusqu\'au bout.', 'premiers_pas', 'serveur', ['compagnon:maki']],
      ['alien', 'sur-la-piste', 'Sur la piste', 'Suivre l\'alien sur cinq programmes.', 'exploration', 'serveur', []],
      ['grand_oral', 'ma-question', 'Ma question', 'Écrire la question de son Grand oral.', 'creation', 'serveur', []]
    ].map(function (h, i) {
      return { application: h[0], id: h[1], nom: h[2], description: h[3], categorie: h[4], accord: h[5],
        recompenses: h[6], secret: !!h[7], indice: h[7] || null, xp: 20, actif: true, ordre: i };
    });

    var bareme = [
      ['td', 'feuille_validee', 'Feuille de TD validée en ligne', 30, true],
      ['td', 'exercice_valide', 'Exercice de TD validé en ligne', 5, true],
      ['quizz_nsi', 'cours_quiz_suivi', 'Cours-quiz suivi jusqu\'au bout', 15, true],
      ['vacances', 'mini_jeu_fait', 'Mini-jeu du calendrier des vacances', 5, true],
      ['gombessa', 'mission_reussie', 'Mission réussie dans Expédition Gombessa', 10, false],
      ['court_circuit', 'challenge_reussi', 'Challenge réussi dans Court-circuit', 10, false],
      ['grand_oral', 'etape_dossier', 'Étape du dossier de Grand oral', 15, false],
      ['lagon', 'manche_jouee', 'Manche jouée dans Lagon Arena', 5, false],
      ['alien', 'exercice_reussi', 'Exercice réussi dans Alien Python', 5, false]
    ].map(function (b) { return { application: b[0], evenement: b[1], nom: b[2], xp: b[3], activite_connue: b[4] }; });

    var activites = [
      ['td', 'feuille_validee', 'td:poo-td1', 'TD 1 de POO'],
      ['td', 'feuille_validee', 'td:boucles-td2', 'TD 2 : les boucles'],
      ['td', 'exercice_valide', 'td:boucles-td2/ex3', 'TD 2 : les boucles, exercice 3'],
      ['quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files', 'Cours-quiz : piles et files'],
      ['vacances', 'mini_jeu_fait', 'cal:jour-01', 'Calendrier : jour 1']
    ].map(function (a) { return { application: a[0], evenement: a[1], cle: a[2], nom: a[3], actif: true }; });

    /* Tableaux de bord : dans la démonstration, ils ouvrent la démonstration de chaque application */
    var adressesProf = {
      commun: 'https://babash.github.io/Babash-NSI-SNT/enseignant/',
      vacances: 'https://babash.github.io/Babash-NSI-SNT/calendrier/prof.html',
      gombessa: 'https://babash.github.io/gombessa/prof.html',
      lagon: 'https://babash.github.io/lagon-arena/prof.html?demo',
      court_circuit: 'https://babash.github.io/court-circuit/prof.html?demo'
    };
    return { applications: apps, hauts_faits: hauts,
      bareme: bareme, activites: activites, adresses_prof: adressesProf };
  })();

  function construireDemo(A) {
    var C = CATALOGUE_DEMO;
    /* Les apparences : celles du moteur d'avatars (donnees/compte-commun/apparences.json) */
    C.elements = (A.elements || []).map(function (e, i) { var x = copie(e); x.actif = true; x.ordre = i; return x; });
    C.emplacements = A.emplacements || [];
    var D = { comptes: {}, codes: [], sessions: {}, gagnes: [], debloques: [], journal: [],
      enseignants: {}, classes: {}, inscriptions: [], classes_liens: [], echecs: 0 };
    var compteur = 0;

    function id(prefixe) { compteur += 1; return 'demo-' + prefixe + '-' + compteur; }
    function element(eid) { return C.elements.filter(function (e) { return e.id === eid; })[0] || null; }
    function hautFait(app, hid) { return C.hauts_faits.filter(function (h) { return h.application === app && h.id === hid; })[0] || null; }
    function application(aid) { return C.applications.filter(function (a) { return a.id === aid; })[0] || null; }
    function nomApp(aid) { var a = application(aid); return a ? a.nom : aid; }
    function ilYa(jours, heures) { return new Date(Date.now() - (jours * 24 + (heures || 0)) * 3600e3).toISOString(); }
    function chiffres() { return String(Math.floor(Math.random() * 1000) + 1000).slice(1); }

    var NIVEAUX_DEMO = ['seconde', 'premiere', 'terminale'];
    var MOTS_DEMO = ['ESSAI', 'MAQUETTE', 'EXEMPLE', 'BROUILLON', 'APERCU', 'MODELE'];
    function nouveauCodeEleve() {
      var c;
      do {
        c = 'DEMO-' + MOTS_DEMO[Math.floor(Math.random() * MOTS_DEMO.length)] + '-' + chiffres();
      } while (D.codes.some(function (x) { return x.code === normaliserCode(c); }));
      return c;
    }
    function nouveauCodeClasse() {
      var lettres = 'ABCDEFGHJKLMNPQRSTUVWXYZ', c;
      do {
        c = '';
        while (c.length < 4) c += lettres.charAt(Math.floor(Math.random() * 24));
      } while (Object.keys(D.classes).some(function (k) { return D.classes[k].code === c; }) || c === 'TEST' || c === 'ESSA');
      return c;
    }

    function creerCompte(pseudo, avatar, quand) {
      var cid = id('compte');
      D.comptes[cid] = { id: cid, pseudo: pseudo, pseudo_provisoire: false, avatar: avatar || avatarDeDepart(),
        xp: 0, credits: 0, cree_le: quand || maintenant(), vu_le: quand || maintenant() };
      return cid;
    }
    function avatarDeDepart() { return copie(A.defaut); }
    function donnerCode(cid, affiche) {
      var principal = !D.codes.some(function (x) { return x.compte_id === cid && x.principal; });
      D.codes.push({ code: normaliserCode(affiche), code_affiche: affiche, compte_id: cid, application: 'commun', principal: principal, cree_le: maintenant() });
    }
    function ouvrirSession(cid) {
      var j = id('session');
      D.sessions[j] = cid;
      return j;
    }
    function compteParSession(j) { return j && D.sessions[j] && D.comptes[D.sessions[j]] ? D.sessions[j] : null; }
    function compteParCode(code) {
      var c = normaliserCode(code);
      var x = D.codes.filter(function (k) { return k.code === c; })[0];
      return x ? x.compte_id : null;
    }

    /* Comme commun.crediter : une clé ne rapporte qu'une fois, le plafond du jour par application */
    function crediter(cid, app, evenement, cle, xp, par, motif, enseignant, quand) {
      if (!cid || !(xp > 0)) return 0;
      if (cle && D.journal.some(function (j) { return j.compte_id === cid && j.application === app && j.cle === cle; })) return 0;
      if (par === 'application' || par === 'page') {
        var jour = new Date(); jour.setHours(0, 0, 0, 0);
        var deja = D.journal.filter(function (j) {
          return j.compte_id === cid && j.application === app && (j.par === 'application' || j.par === 'page') && new Date(j.cree_le) >= jour;
        }).reduce(function (s, j) { return s + j.xp; }, 0);
        xp = Math.min(xp, Math.max(0, 150 - deja));
        if (xp <= 0) return 0;
      }
      D.journal.push({ compte_id: cid, application: app, evenement: evenement, cle: cle || null, xp: xp, motif: motif || null,
        enseignant_id: enseignant || null, par: par, cree_le: quand || maintenant() });
      D.comptes[cid].xp += xp;
      D.comptes[cid].credits += xp;
      D.comptes[cid].vu_le = maintenant();
      return xp;
    }
    function gagnerXp(cid, app, evenement, cle, par, quand) {
      var b = C.bareme.filter(function (x) { return x.application === app && x.evenement === evenement; })[0];
      if (!b) return 0;
      if (b.activite_connue && !C.activites.some(function (t) { return t.application === app && t.cle === cle && t.evenement === evenement && t.actif; })) return 0;
      return crediter(cid, app, evenement, cle, b.xp, par, null, null, quand);
    }
    function accorder(cid, app, ids, par, quand) {
      var genre = par === 'enseignant' ? 'enseignant' : par === 'page' ? 'page' : 'serveur';
      var nouveaux = ids.map(function (h) { return hautFait(app, h); }).filter(function (h) {
        return h && h.actif && h.accord === genre &&
          !D.gagnes.some(function (g) { return g.compte_id === cid && g.application === app && g.haut_fait === h.id; });
      });
      var res = { hauts_faits: [], elements: [], credits: 0 };
      nouveaux.forEach(function (h) {
        D.gagnes.push({ compte_id: cid, application: app, haut_fait: h.id, gagne_le: quand || maintenant(), par: par });
        h.recompenses.forEach(function (eid) {
          if (!D.debloques.some(function (d) { return d.compte_id === cid && d.element_id === eid; })) {
            D.debloques.push({ compte_id: cid, element_id: eid, origine: 'haut_fait', haut_fait: { application: app, id: h.id }, depuis: quand || maintenant() });
            res.elements.push({ id: eid, nom: (element(eid) || {}).nom });
          }
        });
        res.credits += crediter(cid, app, 'haut_fait', 'hf:' + h.id, h.xp, 'haut_fait', null, null, quand);
        res.hauts_faits.push({ application: app, id: h.id, nom: h.nom });
      });
      return res;
    }
    function offrir(cid, eid, motif, pid, quand) {
      D.debloques.push({ compte_id: cid, element_id: eid, origine: 'enseignant', motif: motif, enseignant_id: pid, depuis: quand || maintenant() });
    }
    function acheter(cid, eid, quand) {
      var e = element(eid), k = D.comptes[cid];
      if (!e || e.acces !== 'credits' || !e.actif) return { ok: false, message: 'Cet élément ne s\'achète pas.' };
      if (D.debloques.some(function (d) { return d.compte_id === cid && d.element_id === eid; })) return { ok: false, message: 'Tu l\'as déjà.' };
      if (k.credits < e.prix) return { ok: false, message: 'Pas encore assez de crédits pour celui-ci.' };
      k.credits -= e.prix;
      D.debloques.push({ compte_id: cid, element_id: eid, origine: 'achat', depuis: quand || maintenant() });
      D.journal.push({ compte_id: cid, application: 'commun', evenement: 'achat', cle: 'achat:' + eid, xp: -e.prix, motif: null,
        enseignant_id: null, par: 'achat', cree_le: quand || maintenant() });
      return { ok: true, element: eid, credits: k.credits };
    }

    /* Comme commun.verifier_avatar, pour la description du moteur d'avatars (600 octets au plus) :
       l'identité et les tenues sont libres pour tout avatar ; un objet ou un compagnon doit être
       libre, gagné ou acheté. Aucune pièce n'est réservée à une lignée. */
    function verifierAvatar(cid, a) {
      if (!a || typeof a !== 'object' || Array.isArray(a) || a.v !== 1 || JSON.stringify(a).length > (A.taille_max_description || 600)) return null;
      var permis = Object.keys(A.defaut);
      if (Object.keys(a).some(function (k) { return permis.indexOf(k) < 0; })) return null;
      var I = A.identite, ok = true;
      function dans(liste, v) { return (liste || []).some(function (x) { return x.id === v; }); }
      function couleur(liste, v) { return typeof v === 'string' && (/^#[0-9a-f]{6}$/i.test(v) || dans(liste, v)); }
      ['lignee', 'corps', 'coiffure', 'haut', 'bas', 'chaussures'].forEach(function (k) { if (a[k] != null && !dans(I[k], a[k])) ok = false; });
      if (a.teint != null && !dans(I.teint, a.teint)) ok = false;
      if (a.cheveux != null && !couleur(I.couleurs.cheveux, a.cheveux)) ok = false;
      if (a.fauteuil != null && typeof a.fauteuil !== 'boolean') ok = false;
      var tous = [].concat(I.couleurs.tissu || [], I.couleurs.neon || [], I.couleurs.chaussures || [], I.couleurs.yeux || []);
      Object.keys(a.couleurs || {}).forEach(function (k) { if (!couleur(tous, a.couleurs[k])) ok = false; });
      function possede(eid) {
        var e = element(eid);
        return e && ((e.acces === 'libre' && e.actif) || D.debloques.some(function (d) { return d.compte_id === cid && d.element_id === eid; }));
      }
      Object.keys(a.objets || {}).forEach(function (k) {
        var v = a.objets[k];
        if (!C.emplacements.some(function (m) { return m.id === k; }) || (v !== 'aucun' && !possede(k + ':' + v))) ok = false;
      });
      if (a.compagnon != null && a.compagnon !== 'aucun' && !possede('compagnon:' + a.compagnon)) ok = false;
      return ok ? copie(a) : null;
    }

    function fiche(cid) {
      var k = D.comptes[cid];
      if (!k) return null;
      return {
        pseudo: k.pseudo, pseudo_provisoire: k.pseudo_provisoire, avatar: copie(k.avatar), credits: k.credits, niveau: k.niveau || null,
        codes: D.codes.filter(function (x) { return x.compte_id === cid; })
          .sort(function (a, b) { return (b.principal - a.principal) || (a.cree_le < b.cree_le ? -1 : 1); })
          .map(function (x) { return { application: x.application, code_affiche: x.code_affiche, principal: x.principal }; }),
        applications: [],
        hauts_faits: D.gagnes.filter(function (g) { return g.compte_id === cid; })
          .map(function (g) { return { application: g.application, id: g.haut_fait, gagne_le: g.gagne_le }; }),
        elements: D.debloques.filter(function (d) { return d.compte_id === cid; }).map(function (d) { return d.element_id; }),
        /* Proposition T101b (à ajouter à commun.fiche) : d'où vient chaque trophée */
        trophees: D.debloques.filter(function (d) { return d.compte_id === cid && d.origine !== 'achat'; }).map(function (d) {
          return { element: d.element_id, origine: d.origine, haut_fait: d.haut_fait || null, motif: d.motif || null,
            par: d.enseignant_id && D.enseignants[d.enseignant_id] ? D.enseignants[d.enseignant_id].nom : null, depuis: d.depuis };
        }),
        journal: D.journal.filter(function (j) { return j.compte_id === cid; })
          .sort(function (a, b) { return a.cree_le < b.cree_le ? 1 : -1; }).slice(0, 100)
          .map(function (j) {
            var b = C.bareme.filter(function (x) { return x.application === j.application && x.evenement === j.evenement; })[0];
            var t = C.activites.filter(function (x) { return x.application === j.application && x.cle === j.cle; })[0];
            return { le: j.cree_le, application: j.application, evenement: j.evenement,
              nom: t ? t.nom : b ? b.nom : null, credits: j.xp, motif: j.motif };
          }),
        cree_le: k.cree_le
      };
    }

    function prof(code) {
      var c = normaliserCode(code);
      var e = Object.keys(D.enseignants).map(function (k) { return D.enseignants[k]; }).filter(function (x) { return x.code === c; })[0];
      return e ? e.id : null;
    }
    function classeDuProf(pid, clid) { return D.classes[clid] && D.classes[clid].enseignant_id === pid; }
    function eleveVisible(pid, cid) {
      return D.inscriptions.some(function (i) { return i.compte_id === cid && D.classes[i.classe_id] && D.classes[i.classe_id].enseignant_id === pid; });
    }
    function trierPseudo(a, b) { return a.pseudo.toLowerCase().localeCompare(b.pseudo.toLowerCase(), 'fr'); }
    var EXPIRE = { ok: false, message: 'Ta session a expiré : entre de nouveau ton code.' };
    var MAUVAIS_PROF = { ok: false, message: 'Ce code d\'enseignant·e n\'existe pas.' };
    var PAS_A_TOI = { ok: false, message: 'Cette classe n\'est pas à toi.' };

    /* Les avis de démonstration : le lundi d'il y a n semaines, et des paquets tirés d'une graine fixe */
    D.motsEffaces = [];
    function lundi(n) {
      var t = new Date(Date.now() + 3 * 3600e3), j = (t.getUTCDay() + 6) % 7;
      return new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() - j - 7 * n)).toISOString().slice(0, 10);
    }
    function avisDemo(classe) {
      var graine = classe ? 7 : 3;
      function hasard() { graine = (graine * 9301 + 49297) % 233280; return graine / 233280; }
      function repartir(n, cles, poids) {
        var o = {}, reste = n;
        cles.forEach(function (k, i) {
          var v = i === cles.length - 1 ? reste : Math.min(reste, Math.round(n * poids[i] * (0.7 + 0.6 * hasard())));
          o[k] = v; reste -= v;
        });
        return o;
      }
      var mots = ['La question 3 était dure', 'J\'ai bien aimé l\'exercice des billets', 'Trop long pour une heure', 'Un exemple de plus avant la récursivité, svp',
        'Le code ne se lançait pas sur mon téléphone', 'C\'était clair'];
      var liste = [['td-bac-abr', 'tle-td-bac-abr-1', [0.15, 0.55, 0.3]], ['td-bac-abr', 'tle-td-bac-abr-2', [0.05, 0.4, 0.55]],
        ['td-bac-piles-files', '', [0.2, 0.6, 0.2]], ['quizznsi-abr', '', [0.3, 0.6, 0.1]], ['sequence:tle-piles-files', '', [0.2, 0.6, 0.2]]];
      return liste.map(function (x, i) {
        var lots = [], nb = classe ? 1 + (i % 2) : 2 + (i % 3);
        for (var k = nb; k >= 1; k--) {
          var n = (classe ? 5 : 9) + Math.floor(hasard() * (classe ? 8 : 25));
          var d = repartir(n, ['trop_facile', 'bien', 'trop_dur'], x[2]);
          lots.push({ semaine: lundi(k * 2 - 1), n: n, plu: repartir(n, ['1', '2', '3', '4', '5'], [0.05, 0.1, 0.25, 0.35, 0.25]), difficulte: d,
            compris: repartir(n, ['oui', 'a_peu_pres', 'non'], [0.45, 0.4, 0.15]), fini: repartir(n, ['oui', 'presque', 'non'], [0.4, 0.35, 0.25]),
            remarques: { consignes: Math.floor(n * 0.1), trop_de_texte: Math.floor(n * 0.2 * hasard()), exemples: Math.floor(n * 0.3 * hasard()),
              bug: i === 1 ? 2 : 0, telephone: Math.floor(n * 0.1 * hasard()), encore: Math.floor(n * 0.25 * hasard()) } });
        }
        var m = !classe || i > 1 ? [] : mots.slice(i * 3, i * 3 + 3).map(function (t, j) { return { id: 'demo-mot-' + i + '-' + j, mot: t }; })
          .filter(function (o) { return D.motsEffaces.indexOf(o.id) < 0; });
        return { ressource: x[0], partie: x[1], lots: lots, mots: m };
      });
    }

    var F = {
      /* ── L'élève (0007) ── */
      commun_creer: function (p) {
        var ps = nettoyerPseudo(p.p_pseudo);
        if (!ps) return { ok: false, message: 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).' };
        var cid = creerCompte(ps), code = nouveauCodeEleve();
        if (p.p_niveau) D.comptes[cid].niveau = p.p_niveau;
        donnerCode(cid, code);
        return { ok: true, code_affiche: code, jeton: ouvrirSession(cid), fiche: fiche(cid) };
      },
      commun_entrer: function (p) {
        var cid = compteParCode(p.p_code);
        if (!cid) return { ok: false, message: 'Ce code n\'existe pas. Vérifie-le dans ton cahier.' };
        D.comptes[cid].vu_le = maintenant();
        return { ok: true, jeton: ouvrirSession(cid), fiche: fiche(cid) };
      },
      commun_reprise: function (p) {
        var cid = compteParSession(p.p_jeton);
        return cid ? { ok: true, fiche: fiche(cid) } : EXPIRE;
      },
      commun_catalogue: function () {
        return { version: 1, applications: C.applications, emplacements: C.emplacements, elements: C.elements, familles: A.familles,
          hauts_faits: C.hauts_faits.map(function (h) {
            return { application: h.application, id: h.id, nom: h.secret ? null : h.nom, description: h.secret ? null : h.description,
              indice: h.indice, categorie: h.categorie, secret: h.secret, actif: h.actif, accord: h.accord,
              recompenses: h.secret ? [] : h.recompenses };
          }),
          bareme: C.bareme.map(function (b) { return { application: b.application, evenement: b.evenement, nom: b.nom, credits: b.xp }; }) };
      },
      commun_porter: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        var a = verifierAvatar(cid, p.p_avatar);
        if (!a) return { ok: false, message: 'Un élément n\'est pas encore débloqué, ne va pas avec cette lignée, ou n\'est pas à sa place : l\'avatar n\'a pas changé.' };
        D.comptes[cid].avatar = a;
        return { ok: true, avatar: copie(a) };
      },
      commun_acheter: function (p) {
        var cid = compteParSession(p.p_jeton);
        return cid ? acheter(cid, p.p_element) : EXPIRE;
      },
      commun_renommer: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        var ps = nettoyerPseudo(p.p_pseudo);
        if (!ps) return { ok: false, message: 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).' };
        D.comptes[cid].pseudo = ps;
        D.comptes[cid].pseudo_provisoire = false;
        return { ok: true, pseudo: ps };
      },
      commun_lier_code: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        var autre = compteParCode(p.p_code);
        if (!autre) return { ok: false, message: 'Ce code n\'existe pas. Vérifie-le dans ton cahier.' };
        if (autre === cid) return { ok: true, message: 'Ce code ouvre déjà ton compte.', fiche: fiche(cid) };
        /* La fusion : tout passe sur le compte gardé ; une activité comptée deux fois ne l'est plus qu'une */
        D.codes.forEach(function (x) { if (x.compte_id === autre) { x.compte_id = cid; x.principal = false; } });
        D.gagnes.forEach(function (g) {
          if (g.compte_id === autre && !D.gagnes.some(function (h) { return h.compte_id === cid && h.application === g.application && h.haut_fait === g.haut_fait; })) g.compte_id = cid;
        });
        D.debloques.forEach(function (d) {
          if (d.compte_id === autre && !D.debloques.some(function (h) { return h.compte_id === cid && h.element_id === d.element_id; })) d.compte_id = cid;
        });
        D.journal.forEach(function (j) {
          if (j.compte_id === autre && !(j.cle && D.journal.some(function (h) { return h.compte_id === cid && h.application === j.application && h.cle === j.cle; }))) j.compte_id = cid;
        });
        D.inscriptions.forEach(function (i) {
          if (i.compte_id === autre && !D.inscriptions.some(function (h) { return h.compte_id === cid && h.classe_id === i.classe_id; })) i.compte_id = cid;
        });
        Object.keys(D.sessions).forEach(function (j) { if (D.sessions[j] === autre) D.sessions[j] = cid; });
        var lignes = D.journal.filter(function (j) { return j.compte_id === cid; });
        D.comptes[cid].xp = lignes.filter(function (j) { return j.xp > 0; }).reduce(function (s, j) { return s + j.xp; }, 0);
        D.comptes[cid].credits = Math.max(0, lignes.reduce(function (s, j) { return s + j.xp; }, 0));
        nettoyerCompte(autre);
        return { ok: true, message: 'Tes deux codes ouvrent maintenant le même compte, avec tout ce que tu as gagné.', fiche: fiche(cid) };
      },
      commun_evenement_page: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return { ok: false, message: 'Entre ton code pour garder tes crédits.' };
        if (['td'].indexOf(p.p_application) < 0) return { ok: false, message: 'Cette page ne donne pas de crédits.' };
        var g = gagnerXp(cid, p.p_application, p.p_evenement, p.p_cle, 'page');
        return { ok: true, credits_gagnes: g, message: g > 0 ? 'Bien joué : c\'est gardé.' : 'C\'est déjà gardé (une activité ne compte qu\'une fois).' };
      },
      commun_haut_fait_page: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        if (['td'].indexOf(p.p_application) < 0) return { ok: false, message: 'Cette application n\'accorde pas de haut fait depuis sa page.' };
        return { ok: true, nouveautes: accorder(cid, p.p_application, [p.p_haut_fait], 'page') };
      },
      commun_quitter: function (p) { delete D.sessions[p.p_jeton]; return { ok: true }; },
      commun_effacer_moi: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        if (String(p.p_confirmation || '').trim().toUpperCase() !== 'EFFACER') return { ok: false, message: 'Écris EFFACER pour confirmer.' };
        nettoyerCompte(cid);
        return { ok: true, restent: [], message: 'Ton compte commun est effacé.' };
      },
      /* ── L'élève et ses classes (0008) ── */
      commun_classe_par_code: function (p) {
        var c = normaliserCode(p.p_code_classe);
        var x = Object.keys(D.classes).map(function (k) { return D.classes[k]; }).filter(function (k) { return k.code === c; })[0];
        if (!x) return { ok: false, message: 'Ce code de classe n\'existe pas.' };
        return { ok: true, nom: x.nom, enseignant: D.enseignants[x.enseignant_id].nom, ouverte: x.ouverte };
      },
      commun_rejoindre: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        var c = normaliserCode(p.p_code_classe);
        var x = Object.keys(D.classes).map(function (k) { return D.classes[k]; }).filter(function (k) { return k.code === c; })[0];
        if (!x) return { ok: false, message: 'Ce code de classe n\'existe pas.' };
        if (D.inscriptions.some(function (i) { return i.classe_id === x.id && i.compte_id === cid; })) return { ok: true, message: 'Tu es déjà dans cette classe.', classe: x.nom };
        if (!x.ouverte) return { ok: false, message: 'Les inscriptions de cette classe sont fermées. Demande à ton enseignant·e.' };
        var ps = D.comptes[cid].pseudo.toLowerCase();
        if (D.inscriptions.some(function (i) { return i.classe_id === x.id && D.comptes[i.compte_id].pseudo.toLowerCase() === ps; })) {
          return { ok: false, message: 'Ce pseudo est déjà pris dans la classe. Si c\'est toi, entre avec ton code ; sinon, change de pseudo.' };
        }
        D.inscriptions.push({ classe_id: x.id, compte_id: cid, depuis: maintenant() });
        return { ok: true, message: 'Bienvenue dans la classe.', classe: x.nom };
      },
      commun_ma_classe: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        var classes = D.inscriptions.filter(function (i) { return i.compte_id === cid; }).map(function (i) { return D.classes[i.classe_id]; })
          .sort(function (a, b) { return a.nom.localeCompare(b.nom, 'fr'); });
        return { ok: true, classes: classes.map(function (c) {
          return { nom: c.nom, enseignant: D.enseignants[c.enseignant_id].nom, applications: c.applications.slice(),
            camarades: D.inscriptions.filter(function (i) { return i.classe_id === c.id; }).map(function (i) { return D.comptes[i.compte_id]; })
              .sort(trierPseudo).map(function (k) {
                return { pseudo: k.pseudo, avatar: copie(k.avatar), moi: k.id === cid,
                  hauts_faits: D.gagnes.filter(function (g) { return g.compte_id === k.id; }).map(function (g) { return { application: g.application, id: g.haut_fait }; }) };
              }) };
        }) };
      },
      /* ── L'enseignant·e (0008) ── */
      commun_prof_creer_espace: function (p) {
        var nom = nettoyerTexte(p.p_nom, 2, 40), etab = nettoyerTexte(p.p_etablissement, 2, 80);
        if (!nom) return { ok: false, message: 'Donne un nom affiché de 2 à 40 caractères (« Mme Ali », « M. B. »).' };
        if (!etab && String(p.p_etablissement || '').trim()) return { ok: false, message: 'L\'établissement a de 2 à 80 caractères.' };
        var code = 'DEMO-' + MOTS_DEMO[Math.floor(Math.random() * MOTS_DEMO.length)] + '-PROF-' + chiffres() + Math.floor(Math.random() * 10);
        var pid = id('prof');
        D.enseignants[pid] = { id: pid, code: normaliserCode(code), nom: nom, etablissement: etab };
        return { ok: true, code_affiche: code, message: 'Voici ton code. Il n\'est montré qu\'une fois : note-le ou imprime-le.' };
      },
      commun_prof_ouvrir: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        var e = D.enseignants[pid];
        return { ok: true, nom: e.nom, etablissement: e.etablissement,
          classes: Object.keys(D.classes).map(function (k) { return D.classes[k]; }).filter(function (c) { return c.enseignant_id === pid; })
            .sort(function (a, b) { return a.nom.localeCompare(b.nom, 'fr'); })
            .map(function (c) {
              return { id: c.id, nom: c.nom, code: c.code, ouverte: c.ouverte, archivee: !!c.archivee, applications: c.applications.slice(),
                eleves: D.inscriptions.filter(function (i) { return i.classe_id === c.id; }).length };
            }),
          applications: [], alarme: false };
      },
      commun_prof_lier_code: function (p) {
        if (!prof(p.p_code)) return MAUVAIS_PROF;
        return { ok: false, message: 'Dans la démonstration, aucun espace d\'application n\'existe : rien à relier.' };
      },
      commun_prof_creer_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        var nom = nettoyerTexte(p.p_nom, 2, 40);
        if (!nom) return { ok: false, message: 'Donne un nom de classe de 2 à 40 caractères.' };
        var cl = { id: id('classe'), enseignant_id: pid, nom: nom, code: nouveauCodeClasse(), ouverte: true,
          applications: appsConnues(p.p_applications), cree_le: maintenant() };
        D.classes[cl.id] = cl;
        return { ok: true, id: cl.id, code: cl.code, lien: lienClasse(cl.code) };
      },
      commun_prof_modifier_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        var nom = nettoyerTexte(p.p_nom, 2, 40);
        if (!nom) return { ok: false, message: 'Donne un nom de classe de 2 à 40 caractères.' };
        var c = D.classes[p.p_classe];
        c.nom = nom;
        if (p.p_ouverte != null) c.ouverte = !!p.p_ouverte;
        c.applications = appsConnues(p.p_applications);
        return { ok: true };
      },
      commun_prof_archiver_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        var c = D.classes[p.p_classe], a = p.p_archivee !== false;
        c.archivee = a;
        if (a) c.ouverte = false;
        return { ok: true, archivee: a };
      },
      commun_prof_supprimer_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        if (String(p.p_confirmation || '').trim().toUpperCase() !== 'SUPPRIMER') return { ok: false, message: 'Écris SUPPRIMER pour confirmer.' };
        delete D.classes[p.p_classe];
        D.inscriptions = D.inscriptions.filter(function (i) { return i.classe_id !== p.p_classe; });
        D.classes_liens = D.classes_liens.filter(function (l) { return l.classe_id !== p.p_classe; });
        return { ok: true, message: 'La classe est supprimée. Les comptes des élèves restent, avec tout ce qu\'ils ont gagné.' };
      },
      commun_prof_lier_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        if (!application(p.p_application) || !/^[A-Za-z0-9_-]{1,64}$/.test(p.p_reference || '')) {
          return { ok: false, message: 'Application ou classe de l\'application inconnue.' };
        }
        D.classes_liens = D.classes_liens.filter(function (l) {
          return !(l.classe_id === p.p_classe && l.application === p.p_application && l.reference === p.p_reference);
        });
        if (!p.p_retirer) D.classes_liens.push({ classe_id: p.p_classe, application: p.p_application, reference: p.p_reference });
        return { ok: true };
      },
      commun_prof_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        var c = D.classes[p.p_classe];
        return { ok: true,
          classe: { id: c.id, nom: c.nom, code: c.code, ouverte: c.ouverte, archivee: !!c.archivee, applications: c.applications.slice(), lien: lienClasse(c.code),
            tableaux: D.classes_liens.filter(function (l) { return l.classe_id === c.id; }).map(function (l) {
              var a = C.adresses_prof[l.application];
              return { application: l.application, nom: nomApp(l.application), reference: l.reference,
                adresse: a ? a + '#classe=' + l.reference : null };
            }) },
          eleves: D.inscriptions.filter(function (i) { return i.classe_id === c.id; }).map(function (i) { return D.comptes[i.compte_id]; })
            .sort(trierPseudo).map(function (k) {
              return { compte: k.id, pseudo: k.pseudo, niveau: k.niveau || null, avatar: copie(k.avatar), xp: k.xp, credits: k.credits, vu_le: k.vu_le,
                codes: D.codes.filter(function (x) { return x.compte_id === k.id; }).map(function (x) { return x.code_affiche; }),
                /* Proposition T101b (à ajouter à commun_prof_classe) : les trophées, avec leur motif */
                trophees: D.debloques.filter(function (d) { return d.compte_id === k.id && d.origine !== 'achat'; }).map(function (d) {
                  return { element: d.element_id, nom: (element(d.element_id) || {}).nom || d.element_id, origine: d.origine, motif: d.motif || null };
                }),
                hauts_faits: D.gagnes.filter(function (g) { return g.compte_id === k.id; })
                  .map(function (g) { return { application: g.application, id: g.haut_fait, gagne_le: g.gagne_le }; }) };
            }) };
      },
      commun_prof_eleves: function (p) {
        return prof(p.p_code) ? { ok: true, eleves: [] } : MAUVAIS_PROF;
      },
      commun_prof_attribuer_xp: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        var xp = Number(p.p_xp);
        if (!(xp >= 1 && xp <= 50 && Math.floor(xp) === xp)) return { ok: false, message: 'Une attribution va de 1 à 50.' };
        var m = nettoyerTexte(p.p_motif, 3, 80);
        if (!m) return { ok: false, message: 'Donne un motif de 3 à 80 caractères.' };
        if (!eleveVisible(pid, p.p_compte)) return { ok: false, message: 'Cet·te élève n\'est dans aucune de tes classes.' };
        return { ok: true, xp: crediter(p.p_compte, 'commun', 'attribution', null, xp, 'enseignant', m, pid) };
      },
      commun_prof_journal_xp: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        var membres = D.inscriptions.filter(function (i) { return i.classe_id === p.p_classe; }).map(function (i) { return i.compte_id; });
        return { ok: true, journal: D.journal.filter(function (j) { return membres.indexOf(j.compte_id) >= 0; })
          .sort(function (a, b) { return a.cree_le < b.cree_le ? 1 : -1; }).slice(0, 500)
          .map(function (j) {
            return { le: j.cree_le, compte: j.compte_id, pseudo: D.comptes[j.compte_id].pseudo, application: j.application,
              evenement: j.evenement, xp: j.xp, motif: j.motif, par: j.enseignant_id && D.enseignants[j.enseignant_id] ? D.enseignants[j.enseignant_id].nom : null,
              cle: j.cle };
          }) };
      },
      /* Les avis des élèves (0013) : des paquets fictifs, tirés d'une graine fixe ; des mots inventés, sans aucun nom */
      commun_prof_retours: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (p.p_classe && !classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        return { ok: true, portee: p.p_classe ? 'classe' : 'tous', semaine: lundi(0), seuil: 5, ressources: avisDemo(p.p_classe) };
      },
      commun_prof_retour_effacer_mot: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (D.motsEffaces.indexOf(p.p_retour) >= 0) return { ok: false, message: 'Ce mot n\'est pas dans tes classes, ou il est déjà effacé.' };
        D.motsEffaces.push(p.p_retour);
        return { ok: true, message: 'Le mot est effacé.' };
      },
      /* Proposition T101b (fonction à ajouter en 0010) : offrir un trophée (un objet qui ne s'achète pas)
         à un·e élève de ses classes, avec un motif court, que l'élève lit dans sa planque */
      commun_prof_offrir: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        var e = element(p.p_element);
        /* Décision de l'enseignant (20/11) : seulement des objets de trophée, jamais un compagnon */
        /* Comme 0010 : seulement un trophée de la classe (« Les gimmicks de la classe ») */
        if (!e || e.acces !== 'haut_fait' || e.famille !== 'classe') return { ok: false, message: 'Seul un trophée de la classe s\'offre ; les compagnons et les objets des applications se gagnent.' };
        var m = nettoyerTexte(p.p_motif, 3, 80);
        if (!m) return { ok: false, message: 'Donne un motif de 3 à 80 caractères.' };
        if (!eleveVisible(pid, p.p_compte)) return { ok: false, message: 'Cet·te élève n\'est dans aucune de tes classes.' };
        if (D.debloques.some(function (d) { return d.compte_id === p.p_compte && d.element_id === e.id; })) return { ok: false, message: 'Cet·te élève l\'a déjà.' };
        offrir(p.p_compte, e.id, m, pid);
        return { ok: true, element: e.id, nom: e.nom };
      },
      commun_prof_accorder: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!eleveVisible(pid, p.p_compte)) return { ok: false, message: 'Cet·te élève n\'est dans aucune de tes classes, ou n\'a pas encore de compte commun.' };
        return { ok: true, nouveautes: accorder(p.p_compte, p.p_application, [p.p_haut_fait], 'enseignant') };
      },
      commun_prof_retirer_eleve: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        D.inscriptions = D.inscriptions.filter(function (i) { return !(i.classe_id === p.p_classe && i.compte_id === p.p_compte); });
        return { ok: true, message: 'L\'élève n\'est plus dans la classe ; son compte reste.' };
      },
      commun_prof_renommer_eleve: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        var ps = nettoyerPseudo(p.p_pseudo);
        if (!ps) return { ok: false, message: 'Un prénom ou un pseudo de 2 à 24 caractères.' };
        if (!eleveVisible(pid, p.p_compte)) return { ok: false, message: 'Cet·te élève n\'est dans aucune de tes classes communes.' };
        D.comptes[p.p_compte].pseudo = ps;
        D.comptes[p.p_compte].pseudo_provisoire = false;
        return { ok: true, pseudo: ps };
      },
      /* Le niveau (décision de l'enseignant du 24/11, 11:34) : choisi par l'élève à la création
         de son code seulement ; ensuite, seul·e l'enseignant·e le change, par élève ou pour toute une classe */
      commun_prof_niveau_eleve: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (NIVEAUX_DEMO.indexOf(p.p_niveau) < 0) return { ok: false, message: 'Niveau inconnu.' };
        if (!eleveVisible(pid, p.p_compte)) return { ok: false, message: 'Cet·te élève n\'est dans aucune de tes classes communes.' };
        D.comptes[p.p_compte].niveau = p.p_niveau;
        return { ok: true, niveau: p.p_niveau };
      },
      commun_prof_niveau_classe: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!classeDuProf(pid, p.p_classe)) return PAS_A_TOI;
        if (NIVEAUX_DEMO.indexOf(p.p_niveau) < 0) return { ok: false, message: 'Niveau inconnu.' };
        var n = 0;
        D.inscriptions.forEach(function (i) { if (i.classe_id === p.p_classe) { D.comptes[i.compte_id].niveau = p.p_niveau; n += 1; } });
        return { ok: true, eleves: n };
      },
      commun_prof_nouveau_code_eleve: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (!eleveVisible(pid, p.p_compte)) return { ok: false, message: 'Cet·te élève n\'est dans aucune de tes classes communes.' };
        D.codes = D.codes.filter(function (x) { return !(x.compte_id === p.p_compte && x.application === 'commun'); });
        var code = nouveauCodeEleve();
        donnerCode(p.p_compte, code);
        Object.keys(D.sessions).forEach(function (j) { if (D.sessions[j] === p.p_compte) delete D.sessions[j]; });
        return { ok: true, code_affiche: code };
      },
      commun_prof_nouveau_code: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        var code = 'DEMO-' + MOTS_DEMO[Math.floor(Math.random() * MOTS_DEMO.length)] + '-PROF-' + chiffres() + Math.floor(Math.random() * 10);
        D.enseignants[pid].code = normaliserCode(code);
        return { ok: true, code_affiche: code, message: 'Voici ton nouveau code commun ; l\'ancien ne marche plus. Les codes de tes applications restent valables.' };
      },
      commun_prof_debloquer_reseau: function (p) {
        return prof(p.p_code) ? { ok: true, effaces: 0 } : MAUVAIS_PROF;
      },
      commun_prof_supprimer_espace: function (p) {
        var pid = prof(p.p_code);
        if (!pid) return MAUVAIS_PROF;
        if (String(p.p_confirmation || '').trim().toUpperCase() !== 'SUPPRIMER') return { ok: false, message: 'Écris SUPPRIMER pour confirmer.' };
        Object.keys(D.classes).forEach(function (k) {
          if (D.classes[k].enseignant_id === pid) {
            D.inscriptions = D.inscriptions.filter(function (i) { return i.classe_id !== k; });
            delete D.classes[k];
          }
        });
        delete D.enseignants[pid];
        return { ok: true, message: 'Ton espace commun et tes classes communes sont supprimés. Les comptes des élèves restent, ainsi que tes espaces dans chaque application.' };
      }
    };

    function appsConnues(liste) {
      return (Array.isArray(liste) ? liste : []).filter(function (a) { return application(a); }).slice(0, 20).sort();
    }
    function lienClasse(code) { return 'https://babash.github.io/Babash-NSI-SNT/eleve/?classe=' + code; }
    function nettoyerCompte(cid) {
      delete D.comptes[cid];
      D.codes = D.codes.filter(function (x) { return x.compte_id !== cid; });
      D.gagnes = D.gagnes.filter(function (x) { return x.compte_id !== cid; });
      D.debloques = D.debloques.filter(function (x) { return x.compte_id !== cid; });
      D.journal = D.journal.filter(function (x) { return x.compte_id !== cid; });
      D.inscriptions = D.inscriptions.filter(function (x) { return x.compte_id !== cid; });
      Object.keys(D.sessions).forEach(function (j) { if (D.sessions[j] === cid) delete D.sessions[j]; });
    }

    /* ── Le monde de démonstration : une enseignante ou un enseignant fictif, deux classes ── */
    (function peupler() {
      var pid = 'demo-prof-0';
      D.enseignants[pid] = { id: pid, code: normaliserCode(DEMO_PROF), nom: 'Enseignant·e de démo', etablissement: 'Lycée de démonstration' };
      D.classes['demo-classe-a'] = { id: 'demo-classe-a', enseignant_id: pid, nom: 'Seconde 4 (démo)', code: 'TEST', ouverte: true,
        applications: ['court_circuit', 'quizz_nsi', 'td'], cree_le: ilYa(60) };
      D.classes['demo-classe-b'] = { id: 'demo-classe-b', enseignant_id: pid, nom: 'Terminale NSI (démo)', code: 'ESSA', ouverte: false,
        applications: ['grand_oral', 'lagon', 'quizz_nsi', 'td'], cree_le: ilYa(58) };
      D.classes_liens.push({ classe_id: 'demo-classe-a', application: 'court_circuit', reference: 'DEMO' });
      D.classes_liens.push({ classe_id: 'demo-classe-b', application: 'lagon', reference: 'DEMO' });

      function av(lignee, teint, corps, coiffure, cheveux, haut, bas, chaussures, couleurs, objets, compagnon, fauteuil) {
        var d = copie(A.defaut);
        d.lignee = lignee; d.teint = teint; d.corps = corps; d.coiffure = coiffure; d.cheveux = cheveux;
        d.haut = haut; d.bas = bas; d.chaussures = chaussures;
        Object.keys(couleurs || {}).forEach(function (k) { d.couleurs[k] = couleurs[k]; });
        Object.keys(objets || {}).forEach(function (k) { d.objets[k] = objets[k]; });
        if (compagnon) d.compagnon = compagnon;
        if (fauteuil) d.fauteuil = true;
        return d;
      }
      /* [pseudo, n° du code, classe, avatar, jours depuis l'arrivée] : prénoms et pseudos inventés */
      var eleves = [
        ['Nour', 101, 'a', av('nuee', 5, 'moyenne', 'tresses', 'noirs', 'veste', 'cargo', 'baskets', { haut: 'canard', accent: 'cyan' }, { dos: 'turbine_dos' }), 40],
        ['Anli', 102, 'a', av('lagon', 7, 'ronde', 'rase', 'noirs', 'maillot', 'short', 'savates', { haut: 'vert', accent: 'jaune' }), 38],
        ['Zoé', 103, 'a', av('cyber', 2, 'fine', 'lisses', 'roux', 'gilet', 'pantalon', 'montantes', { haut: 'orange', accent: 'violet' }, null, 'roussette'), 37],
        ['Kenji', 104, 'a', av('esprit', 3, 'moyenne', 'chignon_antenne', 'bleus', 'sweat', 'jogging', 'baskets', { haut: 'prune', accent: 'rose' }, null, null, true), 35],
        ['Faïza', 105, 'a', av('mutant', 4, 'ronde', 'afro_pixel', 'noirs', 'tunique', 'salouva', 'savates', { haut: 'jaune', accent: 'orange' }), 30],
        ['Maëlys', 106, 'b', av('greffe', 6, 'fine', 'puffs', 'violets', 'chemise', 'jupe_longue', 'baskets', { haut: 'sarcelle', accent: 'vert' }, { epaule: 'kishali', autour: 'lucioles' }), 50],
        ['Ibrahim', 107, 'b', av('humain', 8, 'moyenne', 'degrade_circuit', 'noirs', 'tshirt', 'cargo', 'bottes', { haut: 'marine', accent: 'cyan' }, null, 'maki'), 49],
        ['Sam', 108, 'b', av('nuee', 1, 'ronde', 'boucles', 'blonds', 'debardeur', 'sarouel', 'pieds_nus', { haut: 'rouge', accent: 'jaune' }), 45]
      ];
      var ids = {};
      eleves.forEach(function (e) {
        var cid = creerCompte(e[0], e[3], ilYa(e[4]));
        ids[e[0]] = cid;
        donnerCode(cid, 'DEMO-ESSAI-' + e[1]);
        D.inscriptions.push({ classe_id: 'demo-classe-' + e[2], compte_id: cid, depuis: ilYa(e[4]) });
      });
      /* Ce que chacun·e a fait : des activités et des hauts faits, jamais comparés */
      function fait(qui, jours, quoi) {
        var cid = ids[qui], q = ilYa(jours, 3);
        quoi.forEach(function (x) {
          if (x[0] === 'xp') gagnerXp(cid, x[1], x[2], x[3], x[1] === 'court_circuit' || x[1] === 'lagon' ? 'application' : 'page', q);
          else if (x[0] === 'hf') accorder(cid, x[1], [x[2]], x[3] || 'serveur', q);
          else if (x[0] === 'achat') acheter(cid, x[1], q);
          else if (x[0] === 'offert') offrir(cid, x[1], x[2], pid, q);
          else if (x[0] === 'prof') crediter(cid, 'commun', 'attribution', null, x[1], 'enseignant', x[2], pid, q);
        });
      }
      fait('Nour', 30, [['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['hf', 'td', 'premiere-feuille', 'page'], ['hf', 'commun', 'premiere-planque']]);
      fait('Nour', 20, [['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files'], ['hf', 'quizz_nsi', 'jusqu-au-bout', 'page']]);
      fait('Nour', 12, [['xp', 'court_circuit', 'challenge_reussi', 'cc:defi-1'], ['hf', 'court_circuit', 'premier-circuit'], ['achat', 'dos:turbine_dos']]);
      fait('Nour', 4, [['prof', 20, 'Aide à un camarade sur les boucles'], ['hf', 'commun', 'coup-de-main', 'enseignant'], ['xp', 'td', 'feuille_validee', 'td:boucles-td2']]);
      fait('Anli', 25, [['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['hf', 'td', 'premiere-feuille', 'page'], ['hf', 'td', 'erreur-surmontee', 'page']]);
      fait('Anli', 8, [['xp', 'court_circuit', 'challenge_reussi', 'cc:defi-1'], ['xp', 'court_circuit', 'challenge_reussi', 'cc:defi-2'], ['hf', 'court_circuit', 'premier-circuit']]);
      fait('Zoé', 22, [['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['hf', 'td', 'erreur-surmontee', 'page'], ['hf', 'court_circuit', 'sortie-de-la-grotte']]);
      fait('Zoé', 6, [['offert', 'main:feutre', 'A remis en état les feutres de la salle'], ['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files'], ['hf', 'commun', 'premiere-planque']]);
      fait('Kenji', 15, [['xp', 'td', 'exercice_valide', 'td:boucles-td2/ex3'], ['hf', 'commun', 'premiere-planque']]);
      fait('Faïza', 9, [['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files'], ['hf', 'quizz_nsi', 'jusqu-au-bout', 'page']]);
      fait('Maëlys', 40, [['prof', 50, 'Exposé sur le chiffrement'], ['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files']]);
      fait('Maëlys', 30, [['prof', 50, 'Exposé sur les arbres binaires'], ['xp', 'td', 'feuille_validee', 'td:boucles-td2'], ['prof', 50, 'Préparation du Grand oral'],
        ['xp', 'td', 'exercice_valide', 'td:boucles-td2/ex3'], ['hf', 'commun', 'coup-de-main', 'enseignant'], ['achat', 'autour:lucioles']]);
      fait('Maëlys', 10, [['hf', 'grand_oral', 'ma-question'], ['prof', 50, 'Aide en salle informatique'], ['achat', 'epaule:kishali']]);
      fait('Ibrahim', 20, [['xp', 'lagon', 'manche_jouee', 'lagon:m1'], ['hf', 'lagon', 'premiere-manche'], ['hf', 'commun', 'explication-claire', 'enseignant']]);
      fait('Sam', 3, [['hf', 'commun', 'premiere-planque']]);
      eleves.forEach(function (e) { D.comptes[ids[e[0]]].vu_le = ilYa(Math.floor(e[4] / 10), e[1] % 7); });
    })();

    return {
      nom: 'demo',
      appeler: function (fonction, params) {
        var f = F[fonction];
        var rep;
        try {
          rep = f ? f(params || {}) : { ok: false, message: 'Fonction inconnue : ' + fonction + '.' };
        } catch (e) {
          if (window.console) console.error(e);
          rep = { ok: false, message: 'Erreur dans la démonstration (' + (e && e.message || e) + ').' };
        }
        return new Promise(function (resoudre) { setTimeout(function () { resoudre(copie(rep)); }, 90); });
      },
      codesDemo: function () {
        return { eleves: D.codes.filter(function (x) { return /^DEMOESSAI1/.test(x.code); }).map(function (x) {
          return { code: x.code_affiche, pseudo: D.comptes[x.compte_id] ? D.comptes[x.compte_id].pseudo : '?' };
        }), enseignant: DEMO_PROF, classes: ['TEST', 'ESSA'] };
      }
    };
  }

  var DEMO_PROF = 'DEMO-ESSAI-PROF-2046';

  /* La démonstration attend ses apparences avant de répondre */
  function implementationDemo() {
    var interne = null;
    var pret = chargerApparences().then(function (A) { if (A) interne = construireDemo(A); });
    return {
      nom: 'demo',
      appeler: function (fonction, params) {
        return pret.then(function () {
          return interne ? interne.appeler(fonction, params)
            : { ok: false, message: 'La démonstration n\'a pas pu se préparer : donnees/compte-commun/apparences.json est illisible.' };
        });
      },
      codesDemo: function () { return interne ? interne.codesDemo() : null; }
    };
  }

  /* ═════════════════════════════════════════════════════════════
     L'interface publique
     ═════════════════════════════════════════════════════════════ */

  var impl = null;
  var reglage = { en_ligne: false, probleme: null };

  function implementation() {
    if (!impl) impl = implementationDemo();
    return impl;
  }

  /* Le choix du mode. On lit COMPTE_COMMUN_EN_LIGNE (reglages.js) ; « true » ne suffit pas :
     il faut aussi l'adresse du projet et sa clé publique, sinon on reste en démonstration
     et la page le dit. */
  function configurer(r) {
    r = r || {};
    var enLigne = r.COMPTE_COMMUN_EN_LIGNE === true || r.en_ligne === true;
    var cc = r.compte_commun || r;
    var url = cc.url || '', cle = cc.cle_publique || '';
    reglage = { en_ligne: false, probleme: null, niveau: r.COMPTE_COMMUN_NIVEAU === true || r.niveau === true,
      catalogue: r.COMPTE_COMMUN_CATALOGUE === true || r.catalogue === true,
      applications: r.COMPTE_COMMUN_APPLICATIONS === true || r.applications === true,
      retours: r.RETOURS_ELEVES === true || r.retours === true };
    if (!enLigne) { impl = implementationDemo(); return mode(); }
    if (!/^https:\/\/[a-z0-9]+\.supabase\.co\/?$/.test(url) || !cle) {
      reglage.probleme = 'COMPTE_COMMUN_EN_LIGNE vaut true, mais l\'adresse du projet (compte_commun.url) ou sa clé publique '
        + '(compte_commun.cle_publique) manque dans reglages.js : la page reste en démonstration.';
      if (window.console) console.warn('[compte commun] ' + reglage.probleme);
      impl = implementationDemo();
      return mode();
    }
    if (/service_role|sb_secret_/.test(cle) || roleJwt(cle) && roleJwt(cle) !== 'anon') {
      reglage.probleme = 'La clé donnée dans reglages.js n\'est pas une clé publique : elle est refusée, la page reste en démonstration.';
      impl = implementationDemo();
      return mode();
    }
    reglage.en_ligne = true;
    impl = implementationSupabase({ url: url, cle_publique: cle });
    return mode();
  }
  function mode() { return implementation().nom; }
  /* Le rôle d'une ancienne clé « anon » (un JWT) : seule « anon » est acceptée */
  function roleJwt(cle) {
    var m = /^ey[^.]+\.([^.]+)\./.exec(cle || '');
    if (!m) return null;
    try { return JSON.parse(atob(m[1].replace(/-/g, '+').replace(/_/g, '/'))).role || '?'; } catch (e) { return '?'; }
  }

  /* ── La session de l'élève sur cet appareil ── */
  var sessionMemoire = null;
  function lireSession() {
    if (mode() === 'demo') return sessionMemoire;
    var s = lireStockage(CLE_SESSION);
    if (!s || !s.jeton || !s.jusqu || new Date(s.jusqu) < new Date()) return null;
    return s;
  }
  function garderSession(jeton, jours, pseudo) {
    var s = { jeton: jeton, jusqu: new Date(Date.now() + jours * 864e5).toISOString(), pseudo: pseudo || null, appareil: jours === 30 };
    if (mode() === 'demo') sessionMemoire = s;
    else ecrireStockage(CLE_SESSION, s, jours === 30);
  }
  /* Le pseudo gardé avec le jeton, après un changement de pseudo (pour « Continuer en tant que… ») */
  function noterPseudo(pseudo) {
    var s = lireSession();
    if (!s || !pseudo) return;
    s.pseudo = pseudo;
    if (mode() === 'demo') sessionMemoire = s; else ecrireStockage(CLE_SESSION, s, !!s.appareil);
  }
  /* « C'est mon téléphone » : la base garde le jeton 30 jours après son dernier usage ; l'appareil fait
     de même (jusqu'ici, il l'oubliait 30 jours après l'entrée du code, même s'il servait chaque jour).
     Le jeton d'un jour ne se prolonge pas : la base le refuse 1 jour après l'entrée, quoi qu'il arrive. */
  function prolonger() {
    var s = lireSession();
    if (!s || !s.appareil || mode() === 'demo') return;
    s.jusqu = new Date(Date.now() + 30 * 864e5).toISOString();
    ecrireStockage(CLE_SESSION, s, true);
  }
  function oublierSession() {
    sessionMemoire = null;
    if (mode() !== 'demo') ecrireStockage(CLE_SESSION, null);
  }
  function jeton() { var s = lireSession(); return s ? s.jeton : null; }

  function appeler(fonction, params) { return implementation().appeler(fonction, params); }
  function avecSession(fonction, params) {
    var j = jeton();
    if (!j) return Promise.resolve({ ok: false, sans_session: true, message: 'Entre ton code pour continuer.' });
    params = params || {};
    params.p_jeton = j;
    return appeler(fonction, params).then(function (rep) {
      if (!rep.ok && /expiré/.test(rep.message || '')) { oublierSession(); rep.sans_session = true; }
      if (rep.ok && rep.fiche && rep.fiche.pseudo) noterPseudo(rep.fiche.pseudo);
      if (rep.ok && rep.pseudo) noterPseudo(rep.pseudo);
      if (rep.ok) prolonger();
      return rep;
    });
  }
  function apresEntree(jours) {
    return function (rep) {
      if (rep.ok && rep.jeton) { oublierSession(); garderSession(rep.jeton, jours, rep.fiche && rep.fiche.pseudo); }
      if (rep.jeton) delete rep.jeton; // le jeton reste dans le module, jamais dans la page
      return rep;
    };
  }
  function jours(options) { return options && options.appareil ? 30 : 1; }

  /* ── L'enseignant·e : son code reste en mémoire le temps de la page
        (et de l'onglet en mode en ligne, s'il ou elle le demande) ── */
  var CLE_PROF = 'compte-commun:enseignant';
  var codeProf = null;
  function lireCodeProf() {
    if (codeProf) return codeProf;
    if (mode() !== 'demo') {
      try { codeProf = sessionStorage.getItem(CLE_PROF); } catch (e) { codeProf = null; }
    }
    return codeProf;
  }
  function avecProf(fonction, params) {
    if (!textesPropres(params || {}, ['p_nom', 'p_pseudo', 'p_motif'])) return Promise.resolve(copie(REFUS_CARACTERE));
    var c = lireCodeProf();
    if (!c) return Promise.resolve({ ok: false, sans_session: true, message: 'Entre ton code d\'enseignant·e.' });
    params = params || {};
    params.p_code = c;
    return appeler(fonction, params);
  }

  var Prof = {
    creerEspace: function (nom, etablissement) {
      if (caractereSpecial(nom) || caractereSpecial(etablissement)) return Promise.resolve(copie(REFUS_CARACTERE));
      return appeler('commun_prof_creer_espace', { p_nom: nom, p_etablissement: etablissement || null });
    },
    ouvrir: function (code, options) {
      return appeler('commun_prof_ouvrir', { p_code: code }).then(function (rep) {
        if (rep.ok) {
          codeProf = code;
          if (mode() !== 'demo' && options && options.onglet) {
            try { sessionStorage.setItem(CLE_PROF, code); } catch (e) { /* sans importance */ }
          }
        }
        return rep;
      });
    },
    rouvrir: function () {
      var c = lireCodeProf();
      return c ? appeler('commun_prof_ouvrir', { p_code: c }) : Promise.resolve({ ok: false, sans_session: true, message: '' });
    },
    ouvert: function () { return !!lireCodeProf(); },
    fermer: function () {
      codeProf = null;
      try { sessionStorage.removeItem(CLE_PROF); } catch (e) { /* sans importance */ }
    },
    lierCode: function (autre) { return avecProf('commun_prof_lier_code', { p_autre_code: autre }); },
    creerClasse: function (nom, apps) { return avecProf('commun_prof_creer_classe', { p_nom: nom, p_applications: apps || [] }); },
    modifierClasse: function (classe, nom, ouverte, apps) {
      return avecProf('commun_prof_modifier_classe', { p_classe: classe, p_nom: nom, p_ouverte: ouverte, p_applications: apps || [] });
    },
    /* La migration 0010 : archiver (inscriptions fermées, classe rangée à part) ou désarchiver.
       Ouverte par le réglage COMPTE_COMMUN_CATALOGUE ; avant, la page ne propose que d'ouvrir ou fermer les inscriptions. */
    archiverClasse: function (classe, archivee) { return avecProf('commun_prof_archiver_classe', { p_classe: classe, p_archivee: archivee !== false }); },
    supprimerClasse: function (classe, confirmation) { return avecProf('commun_prof_supprimer_classe', { p_classe: classe, p_confirmation: confirmation }); },
    lierClasse: function (classe, app, reference, retirer) {
      return avecProf('commun_prof_lier_classe', { p_classe: classe, p_application: app, p_reference: reference, p_retirer: !!retirer });
    },
    classe: function (classe) { return avecProf('commun_prof_classe', { p_classe: classe }); },
    eleves: function () { return avecProf('commun_prof_eleves', {}); },
    attribuerXp: function (compte, xp, motif) { return avecProf('commun_prof_attribuer_xp', { p_compte: compte, p_xp: xp, p_motif: motif }); },
    journalXp: function (classe) { return avecProf('commun_prof_journal_xp', { p_classe: classe }); },
    offrir: function (compte, element, motif) { return avecProf('commun_prof_offrir', { p_compte: compte, p_element: element, p_motif: motif }); },
    accorder: function (compte, app, hautFait) { return avecProf('commun_prof_accorder', { p_compte: compte, p_application: app, p_haut_fait: hautFait }); },
    retirerEleve: function (classe, compte) { return avecProf('commun_prof_retirer_eleve', { p_classe: classe, p_compte: compte }); },
    renommerEleve: function (compte, pseudo) { return avecProf('commun_prof_renommer_eleve', { p_compte: compte, p_pseudo: pseudo }); },
    nouveauCodeEleve: function (compte) { return avecProf('commun_prof_nouveau_code_eleve', { p_compte: compte }); },
    /* Masqués tant que le réglage COMPTE_COMMUN_NIVEAU reste à false (migration de T132e) */
    niveauEleve: function (compte, niveau) {
      if (!reglage.niveau) return Promise.resolve({ ok: false, a_venir: true, message: FONCTIONS_A_VENIR.commun_prof_niveau_eleve });
      return avecProf('commun_prof_niveau_eleve', { p_compte: compte, p_niveau: niveau });
    },
    niveauClasse: function (classe, niveau) {
      if (!reglage.niveau) return Promise.resolve({ ok: false, a_venir: true, message: FONCTIONS_A_VENIR.commun_prof_niveau_classe });
      return avecProf('commun_prof_niveau_classe', { p_classe: classe, p_niveau: niveau });
    },
    nouveauCode: function () {
      return avecProf('commun_prof_nouveau_code', {}).then(function (rep) {
        if (rep.ok && rep.code_affiche) {
          codeProf = rep.code_affiche;
          if (mode() !== 'demo') { try { if (sessionStorage.getItem(CLE_PROF)) sessionStorage.setItem(CLE_PROF, rep.code_affiche); } catch (e) { /* rien */ } }
        }
        return rep;
      });
    },
    debloquerReseau: function () { return avecProf('commun_prof_debloquer_reseau', {}); },
    /* Les avis anonymes des élèves (0013, T163) : par paquets d'au moins 5, des semaines finies */
    retours: function (classe) { return avecProf('commun_prof_retours', { p_classe: classe || null }); },
    effacerMotRetour: function (retour) { return avecProf('commun_prof_retour_effacer_mot', { p_retour: retour }); },
    supprimerEspace: function (confirmation) {
      return avecProf('commun_prof_supprimer_espace', { p_confirmation: confirmation }).then(function (rep) {
        if (rep.ok) Prof.fermer();
        return rep;
      });
    }
  };

  /* ═════════════════════════════════════════════════════════════
     L'avatar : le texte de remplacement, et le dessin
     ═════════════════════════════════════════════════════════════ */

  /* Les apparences (donnees/compte-commun/apparences.json, tirées du catalogue du moteur
     d'avatars par scripts/apparences_compte_commun.py) : chargées une fois. */
  var APP = null, apparencesPromesse = null;
  function chargerApparences() {
    if (apparencesPromesse) return apparencesPromesse;
    apparencesPromesse = (typeof fetch === 'function' && RACINE
      ? fetch(RACINE + 'donnees/compte-commun/apparences.json').then(function (r) {
        if (!r.ok) throw new Error('code ' + r.status);
        return r.json();
      }).then(function (a) {
        if (!a || !a.defaut || !a.identite || !Array.isArray(a.elements)) throw new Error('contenu inattendu');
        APP = a;
        return a;
      })
      : Promise.reject(new Error('lecture impossible'))
    ).catch(function (e) {
      if (window.console) console.warn('[compte commun] apparences.json illisible : ' + (e && e.message || e));
      return null;
    });
    return apparencesPromesse;
  }

  function nomDans(liste, id) {
    var x = (liste || []).filter(function (e) { return e.id === id; })[0];
    return x ? x.nom : null;
  }
  function couleurDe(groupe, v, defaut) {
    if (typeof v === 'string' && /^#[0-9a-f]{6}$/i.test(v)) return v;
    var l = APP && APP.identite.couleurs[groupe];
    var x = (l || []).filter(function (e) { return e.id === v; })[0];
    return x && x.couleur ? x.couleur : defaut;
  }

  /* « Avatar de Nour : Nuée, tresses, veste runner, cargo à câble, turbine… » (le module, s'il est là, fait mieux) */
  function texteAvatar(d, catalogue, pseudo) {
    var debut = pseudo ? 'Avatar de ' + pseudo : 'Avatar';
    if (!d) return debut;
    if (window.Equipage && typeof window.Equipage.texte === 'function') {
      try {
        var t = String(window.Equipage.texte(d, 'repos'));
        return /^Avatar\b/.test(t) ? t.replace(/^Avatar/, debut) : debut + ' : ' + t;
      } catch (e) { /* le texte simple ci-dessous */ }
    }
    if (!APP) return debut;
    var I = APP.identite, mots = [];
    [['lignee', d.lignee], ['coiffure', d.coiffure], ['haut', d.haut], ['bas', d.bas], ['chaussures', d.chaussures]].forEach(function (x) {
      var n = nomDans(I[x[0]], x[1]);
      if (n) mots.push(mots.length ? n.charAt(0).toLowerCase() + n.slice(1) : n);
    });
    Object.keys(d.objets || {}).forEach(function (k) {
      if (d.objets[k] && d.objets[k] !== 'aucun') {
        var n = nomDans(APP.elements, k + ':' + d.objets[k]);
        if (n) mots.push(n.charAt(0).toLowerCase() + n.slice(1));
      }
    });
    if (d.compagnon && d.compagnon !== 'aucun') { var c = nomDans(APP.elements, 'compagnon:' + d.compagnon); if (c) mots.push('avec ' + c.toLowerCase()); }
    if (d.fauteuil) mots.push('en fauteuil roulant');
    return debut + (mots.length ? ' : ' + mots.join(', ') : '');
  }

  var TONS = ['#22D3EE', '#FF3D9A', '#A78BFA', '#34D399', '#FB923C', '#60A5FA', '#FACC15', '#F472B6', '#2DD4BF', '#E879F9'];
  function ton(id) {
    var h = 0;
    for (var i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) % 9973;
    return TONS[h % TONS.length];
  }
  var PEAU_LIGNEE = { nuee: '#B59CFF', esprit: '#DDE7FF' };

  /* Le dessin de remplacement : une silhouette en gros pixels, aux couleurs de la description,
     tant que le moteur d'avatars du Designer n'est pas publié. */
  function svgRemplacement(d) {
    d = d || {};
    var c = d.couleurs || {}, o = d.objets || {};
    var teint = APP ? (APP.identite.teint.filter(function (t) { return t.id === d.teint; })[0] || {}).couleur : null;
    var peau = PEAU_LIGNEE[d.lignee] || teint || '#8A5236';
    var haut = couleurDe('tissu', c.haut, '#0E7490'), bas = couleurDe('tissu', c.bas, '#334155');
    var acc = couleurDe('neon', c.accent, '#22D3EE'), pieds = couleurDe('chaussures', c.chaussures, '#E5E7EB');
    var ch = couleurDe('cheveux', d.cheveux, '#1F1A24');
    var large = d.corps === 'ronde' ? 2 : d.corps === 'fine' ? -1 : 0;
    var s = ['<svg viewBox="0 0 48 64" width="100%" height="100%" shape-rendering="crispEdges" aria-hidden="true" focusable="false">'];
    function r(x, y, w, h, col, extra) { s.push('<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + col + '"' + (extra || '') + '/>'); }
    r(0, 0, 48, 64, '#101830');
    r(0, 56, 48, 8, '#1A2440');
    if (o.autour && o.autour !== 'aucun') for (var k = 0; k < 8; k++) r(3 + k * 6, (k * 17) % 40, 2, 2, acc, ' opacity=".8"');
    if (o.dos && o.dos !== 'aucun') r(10 - large, 26, 28 + 2 * large, 16, ton(o.dos));
    if (d.bas === 'salouva' || d.bas === 'jupe_longue') r(14 - large, 42, 20 + 2 * large, 13, bas);
    else { r(16 - large, 44, 7, 11, bas); r(25 + large, 44, 7, 11, bas); }
    if (d.chaussures !== 'pieds_nus') { r(14 - large, 55, 9, 3, pieds); r(25 + large, 55, 9, 3, pieds); } else { r(15 - large, 55, 7, 2, peau); r(26 + large, 55, 7, 2, peau); }
    r(13 - large, 26, 22 + 2 * large, 18, d.haut === 'aucun' ? peau : haut);
    r(13 - large, 26, 22 + 2 * large, 2, acc);
    r(9 - large, 27, 4, 15, peau); r(35 + large, 27, 4, 15, peau);
    r(16, 8, 16, 17, peau); r(21, 24, 6, 3, peau);
    if (d.coiffure && d.coiffure !== 'rase') {
      if (/afro|puffs/.test(d.coiffure)) { r(12, 3, 24, 9, ch); r(12, 9, 4, 8, ch); r(32, 9, 4, 8, ch); }
      else if (/tresses|locks|lisses/.test(d.coiffure)) { r(15, 6, 18, 5, ch); r(14, 9, 3, 16, ch); r(31, 9, 3, 16, ch); }
      else if (/chignon/.test(d.coiffure)) { r(15, 6, 18, 5, ch); r(20, 2, 8, 5, ch); }
      else if (/crete/.test(d.coiffure)) r(22, 2, 4, 7, acc);
      else r(16, 6, 16, 4, ch);
    }
    r(20, 14, 2, 3, '#0B0F1E'); r(26, 14, 2, 3, '#0B0F1E'); r(22, 20, 4, 1, '#0B0F1E');
    if (o.visage && o.visage !== 'aucun') r(18, 13, 12, 4, ton(o.visage), ' opacity=".85"');
    if (o.tete && o.tete !== 'aucun') r(15, 3, 18, 5, ton(o.tete));
    if (o.cou && o.cou !== 'aucun') r(20, 27, 8, 2, ton(o.cou));
    if (o.epaule && o.epaule !== 'aucun') r(32 + large, 23, 6, 4, ton(o.epaule));
    if (o.main && o.main !== 'aucun') r(38 + large, 36, 5, 5, ton(o.main));
    if (d.fauteuil) { r(8, 46, 32, 2, '#94A3B8'); s.push('<circle cx="14" cy="54" r="6" fill="none" stroke="#94A3B8" stroke-width="2"/><circle cx="34" cy="54" r="6" fill="none" stroke="#94A3B8" stroke-width="2"/>'); }
    if (d.compagnon === 'margouillat') { r(36, 59, 9, 2, '#39C46A'); r(44, 58, 2, 2, '#39C46A'); r(32, 60, 4, 1, '#39C46A'); r(30, 59, 2, 2, '#FF9A3D'); }
    else if (d.compagnon && d.compagnon !== 'aucun') { var f = ton(d.compagnon); r(38, 55, 7, 5, f); r(40, 56, 1, 1, '#0B0F1E'); r(43, 56, 1, 1, '#0B0F1E'); }
    s.push('</svg>');
    return s.join('');
  }

  /* Le moteur d'avatars du Designer (assets/equipage.js) : chargé seulement si apparences.json dit
     qu'il est publié (« module »), pour ne jamais demander un fichier absent. Sinon, le remplacement. */
  var equipagePromesse = null;
  function chargerEquipage() {
    if (window.Equipage && typeof window.Equipage.creer === 'function') return Promise.resolve(true);
    if (equipagePromesse) return equipagePromesse;
    equipagePromesse = chargerApparences().then(function (a) {
      if (!a || a.module !== true || !RACINE || location.protocol === 'file:') return false;
      return new Promise(function (resoudre) {
        var s = document.createElement('script');
        s.src = RACINE + 'assets/equipage.js';
        s.async = true;
        s.onload = function () { resoudre(!!(window.Equipage && typeof window.Equipage.creer === 'function')); };
        s.onerror = function () { resoudre(false); };
        document.head.appendChild(s);
      });
    });
    return equipagePromesse;
  }

  /* Les tailles des cadres : des hauteurs nettes pour la grille de 48 × 64 du moteur */
  var TAILLES = { grand: 224, moyen: 112, petit: 112 };

  /* Dessine un avatar dans element. options : { etat ('repos', 'content', 'tres_content', 'triste',
     'concentre', 'salue', 'dort'), taille ('grand' | 'moyen' | 'petit'), pseudo }.
     Le conteneur porte le texte de remplacement ; le dessin est décoratif. */
  function dessinerAvatar(element, avatar, options) {
    options = options || {};
    element.classList.add('avatar', 'avatar-' + (options.taille || 'moyen'));
    element.setAttribute('role', 'img');
    function etiquette() { element.setAttribute('aria-label', options.alt || texteAvatar(avatar, null, options.pseudo)); }
    function remplacement() {
      element.innerHTML = svgRemplacement(avatar);
      element.setAttribute('data-dessin', 'remplacement');
    }
    etiquette();
    remplacement();
    chargerApparences().then(function () { etiquette(); if (element.getAttribute('data-dessin') === 'remplacement') remplacement(); });
    chargerEquipage().then(function (present) {
      if (!present) return;
      try {
        var zone = document.createElement('div');
        zone.className = 'avatar-dessin';
        var reduit = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        window.Equipage.creer(zone, copie(avatar), { etat: options.etat || 'repos', taille: TAILLES[options.taille] || 112,
          anime: !reduit, alt: '', net: true });
        element.innerHTML = '';
        element.appendChild(zone);
        element.setAttribute('data-dessin', 'equipage');
        etiquette();
      } catch (e) {
        if (window.console) console.warn('[compte commun] Equipage.creer a échoué, dessin de remplacement : ' + (e && e.message || e));
        remplacement();
      }
    });
    return element;
  }

  /* Les feuilles de TD en ligne (assets/td-en-ligne.js, T115) annoncent « td:feuille-validee »
     avec l'identifiant de la feuille, jamais les réponses. Décision de l'enseignant du 20/11 :
     si l'élève est connecté·e, ses crédits sont gardés automatiquement (une fois par feuille).
     La page reçoit la réponse par l'événement « compte-commun:credits ». */
  if (typeof document !== 'undefined' && document.addEventListener) {
    document.addEventListener('td:feuille-validee', function (e) {
      var f = e && e.detail && e.detail.feuille;
      if (!jeton() || typeof f !== 'string' || !/^[a-z0-9][a-z0-9:/_.-]{0,76}$/.test(f)) return;
      window.CompteCommun.evenementPage('td', 'feuille_validee', 'td:' + f).then(function (rep) {
        try { document.dispatchEvent(new CustomEvent('compte-commun:credits', { detail: rep })); } catch (x) { /* ancien navigateur */ }
      });
    });
  }

  /* ═════════════════════════════════════════════════════════════
     Les niveaux : les libellés des référentiels du site (donnees/referentiels/valeurs.json),
     jamais un synonyme. « Seconde · SNT », « Première · NSI », « Terminale · NSI ».
     ═════════════════════════════════════════════════════════════ */
  var niveauxPromesse = null;
  var NIVEAU_ENSEIGNEMENT = { seconde: 'snt', premiere: 'nsi', terminale: 'nsi' };
  function chargerNiveaux() {
    if (niveauxPromesse) return niveauxPromesse;
    niveauxPromesse = (typeof fetch === 'function' && RACINE ? fetch(RACINE + 'donnees/referentiels/valeurs.json').then(function (r) {
      if (!r.ok) throw new Error('code ' + r.status);
      return r.json();
    }) : Promise.reject(new Error('lecture impossible'))).then(function (v) {
      var ens = {};
      (v.enseignements || []).forEach(function (e) { ens[e.id] = e.libelle; });
      return (v.niveaux || []).filter(function (n) { return NIVEAU_ENSEIGNEMENT[n.id]; }).map(function (n) {
        return { id: n.id, libelle: n.libelle + ' · ' + (ens[NIVEAU_ENSEIGNEMENT[n.id]] || NIVEAU_ENSEIGNEMENT[n.id].toUpperCase()), court: n.court };
      });
    }).catch(function (e) {
      if (window.console) console.warn('[compte commun] référentiel des niveaux illisible : ' + (e && e.message || e));
      return [];
    });
    return niveauxPromesse;
  }

  /* ═════════════════════════════════════════════════════════════
     Le bandeau « Zoé · mes applications » : des liens simples vers les
     autres applications, qui gardent le compte (même origine, même onglet).
     Aucun jeton ni code dans les liens. L'application appelle
     CompteCommun.bandeau(element, { application: 'quizz_nsi' }).
     ═════════════════════════════════════════════════════════════ */
  var STYLE_BANDEAU = [
    '.ccb{--ccb-fond:#F4F6FB;--ccb-encre:#141824;--ccb-trait:#C9D1E3;--ccb-accent:#0E6177;font:inherit;font-size:.95rem;color:var(--ccb-encre);',
    'background:var(--ccb-fond);border:1px solid var(--ccb-trait);border-radius:6px;padding:.35rem .6rem;max-width:100%;box-sizing:border-box}',
    '@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .ccb{--ccb-fond:#161A26;--ccb-encre:#E8ECF6;--ccb-trait:#33405C;--ccb-accent:#5EE3F5}}',
    ':root[data-theme=dark] .ccb{--ccb-fond:#161A26;--ccb-encre:#E8ECF6;--ccb-trait:#33405C;--ccb-accent:#5EE3F5}',
    '.ccb summary{cursor:pointer;font-weight:700;overflow-wrap:anywhere}.ccb summary:focus-visible,.ccb a:focus-visible,.ccb button:focus-visible{outline:2px solid var(--ccb-accent);outline-offset:2px}',
    '.ccb ul{list-style:none;margin:.4rem 0 0;padding:0;display:flex;flex-wrap:wrap;gap:.3rem .8rem}.ccb a{color:var(--ccb-accent)}',
    '.ccb button{font:inherit;color:var(--ccb-encre);background:none;border:1px solid var(--ccb-trait);border-radius:4px;padding:.15rem .5rem;margin-top:.4rem;cursor:pointer}'
  ].join('');
  function bandeau(conteneur, options) {
    options = options || {};
    if (!conteneur || typeof document === 'undefined') return Promise.resolve(null);
    if (!document.getElementById('compte-commun-bandeau-style')) {
      var st = document.createElement('style');
      st.id = 'compte-commun-bandeau-style';
      st.textContent = STYLE_BANDEAU;
      (document.head || document.documentElement).appendChild(st);
    }
    conteneur.textContent = '';
    var s = lireSession();
    if (!s) return Promise.resolve(null);
    var d = document.createElement('details');
    d.className = 'ccb';
    var sm = document.createElement('summary');
    sm.textContent = (s.pseudo || 'Mon compte') + ' · mes applications';
    d.appendChild(sm);
    var ul = document.createElement('ul');
    d.appendChild(ul);
    function lien(texte, href) {
      var li = document.createElement('li'), a = document.createElement('a');
      a.href = href; a.textContent = texte; li.appendChild(a); ul.appendChild(li);
    }
    lien('Mon avatar', RACINE ? RACINE + 'eleve/' : 'https://babash.github.io/Babash-NSI-SNT/eleve/');
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = 'Ce n\'est pas moi';
    b.addEventListener('click', function () {
      window.CompteCommun.quitter().then(function () {
        conteneur.textContent = '';
        try { document.dispatchEvent(new CustomEvent('compte-commun:sortie')); } catch (e) { /* ancien navigateur */ }
      });
    });
    d.appendChild(b);
    conteneur.appendChild(d);
    return appeler('commun_catalogue', {}).then(function (cat) {
      ((cat && cat.applications) || []).forEach(function (a) {
        if (a.adresse && a.id !== 'commun' && a.id !== options.application) lien(a.nom, a.adresse);
      });
      return d;
    });
  }

  window.CompteCommun = {
    version: 1,
    configurer: configurer,
    mode: mode,
    probleme: function () { return reglage.probleme; },
    normaliserCode: normaliserCode,
    nettoyerPseudo: nettoyerPseudo,
    caractereSpecial: caractereSpecial,
    MESSAGE_CARACTERE: REFUS_CARACTERE.message,
    nettoyerTexte: nettoyerTexte,

    /* L'élève */
    connecte: function () { return !!jeton(); },
    pseudoMemorise: function () { var s = lireSession(); return s ? s.pseudo : null; },
    oublier: function () { oublierSession(); },
    catalogue: function () {
      return Promise.all([appeler('commun_catalogue', {}), chargerApparences()]).then(function (r) {
        var rep = r[0];
        if (rep && Array.isArray(rep.elements)) catalogueEnBase = rep.elements.some(function (e) { return e.acces === 'credits'; });
        if (rep && typeof rep === 'object') rep.apparences = r[1];
        if (!r[1] && rep) { rep.ok = false; rep.message = 'Les apparences de l\'avatar (donnees/compte-commun/apparences.json) n\'ont pas pu être lues.'; }
        return rep;
      });
    },
    creer: function (pseudo, options) {
      if (caractereSpecial(pseudo)) return Promise.resolve(copie(REFUS_CARACTERE));
      var p = { p_pseudo: pseudo, p_garde_jours: jours(options) };
      /* Le niveau n'est envoyé que si sa migration est appliquée (réglage COMPTE_COMMUN_NIVEAU) */
      if (reglage.niveau && options && options.niveau) p.p_niveau = options.niveau;
      return appeler('commun_creer', p).then(apresEntree(jours(options)));
    },
    niveauActif: function () { return !!reglage.niveau; },
    /* Vrai quand au moins une application lit le compte commun (réglage COMPTE_COMMUN_APPLICATIONS) ;
       toujours vrai en démonstration. Les pages taisent jusque-là ce qui n'existe pas encore. */
    applicationsBranchees: function () { return mode() === 'demo' || !!reglage.applications; },
    niveaux: chargerNiveaux,
    disponible: function (fonction) { if (/niveau/.test(fonction)) return !!reglage.niveau; return mode() === 'demo' || ouverte(fonction); },
    qui: function () { var s = lireSession(); return s ? { pseudo: s.pseudo, appareil: !!s.appareil } : null; },
    bandeau: bandeau,
    entrer: function (code, options) {
      return appeler('commun_entrer', { p_code: code, p_garde_jours: jours(options) }).then(apresEntree(jours(options)));
    },
    reprendre: function () { return avecSession('commun_reprise', {}); },
    porter: function (avatar) { return avecSession('commun_porter', { p_avatar: avatar }); },
    acheter: function (element) { return avecSession('commun_acheter', { p_element: element }); },
    renommer: function (pseudo) { return caractereSpecial(pseudo) ? Promise.resolve(copie(REFUS_CARACTERE)) : avecSession('commun_renommer', { p_pseudo: pseudo }); },
    lierCode: function (code) { return avecSession('commun_lier_code', { p_code: code }); },
    evenementPage: function (app, evenement, cle) {
      return avecSession('commun_evenement_page', { p_application: app, p_evenement: evenement, p_cle: cle });
    },
    hautFaitPage: function (app, hautFait) { return avecSession('commun_haut_fait_page', { p_application: app, p_haut_fait: hautFait }); },
    quitter: function () {
      var j = jeton();
      oublierSession();
      return j ? appeler('commun_quitter', { p_jeton: j }) : Promise.resolve({ ok: true });
    },
    effacerMoi: function (confirmation, partout) {
      return avecSession('commun_effacer_moi', { p_confirmation: confirmation, p_partout: !!partout }).then(function (rep) {
        if (rep.ok) oublierSession();
        return rep;
      });
    },
    classeParCode: function (code) { return appeler('commun_classe_par_code', { p_code_classe: code }); },
    rejoindre: function (code) { return avecSession('commun_rejoindre', { p_code_classe: code }); },
    maClasse: function () { return avecSession('commun_ma_classe', {}); },

    /* L'enseignant·e */
    prof: Prof,

    /* L'avatar */
    texteAvatar: texteAvatar,
    dessinerAvatar: dessinerAvatar,
    chargerEquipage: chargerEquipage,
    apparences: chargerApparences,

    /* La démonstration : les codes fictifs à essayer (null en mode en ligne) */
    demo: function () {
      var i = implementation();
      return i.codesDemo ? i.codesDemo() : null;
    }
  };
})();
