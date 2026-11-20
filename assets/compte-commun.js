/* ═══════════════════════════════════════════════════════════════
   Le compte commun : un code, un compte et un avatar pour toutes
   les applications (T101, T101b). Architecte.

   Une seule interface, deux façons de répondre :
   - « demo » : des données fictives, en mémoire. Rien n'est envoyé,
     rien n'est gardé : recharger la page efface tout. C'est le mode
     par défaut, tant que reglages.js ne dit pas COMPTE_COMMUN_EN_LIGNE: true ;
   - « supabase » : les fonctions commun_… de la base unique (SQL 0007
     et 0008 de T101). Écrite, mais inactive tant que le réglage reste à false.

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

  function lireStockage(nom) {
    try { return JSON.parse(localStorage.getItem(nom) || 'null'); } catch (e) { return null; }
  }
  function ecrireStockage(nom, valeur) {
    try {
      if (valeur == null) localStorage.removeItem(nom);
      else localStorage.setItem(nom, JSON.stringify(valeur));
    } catch (e) { /* navigation privée : la session vaut pour cette page */ }
  }

  /* ═════════════════════════════════════════════════════════════
     Mode « supabase » : les fonctions commun_… de la base unique.
     Seule la clé publique (« anon » ou « publishable ») va ici.
     ═════════════════════════════════════════════════════════════ */

  function implementationSupabase(cfg) {
    var base = String(cfg.url || '').replace(/\/+$/, '');
    return {
      nom: 'supabase',
      appeler: function (fonction, params) {
        if (typeof fetch !== 'function') {
          return Promise.resolve({ ok: false, message: 'Ce navigateur est trop ancien pour le compte commun.' });
        }
        return fetch(base + '/rest/v1/rpc/' + fonction, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            apikey: cfg.cle_publique,
            Authorization: 'Bearer ' + cfg.cle_publique
          },
          body: JSON.stringify(params || {})
        }).then(function (r) {
          if (r.ok) return r.json();
          return r.text().then(function (t) {
            if (window.console) console.warn('[compte commun] ' + fonction + ' : code ' + r.status + ' ' + t.slice(0, 300));
            return { ok: false, message: 'Le compte commun ne répond pas comme prévu (code ' + r.status + '). Réessaie dans un moment.' };
          });
        }).then(function (rep) {
          return rep && typeof rep === 'object' ? rep : { ok: false, message: 'Réponse inattendue du compte commun.' };
        }).catch(function () {
          return { ok: false, hors_ligne: true, message: 'Le compte commun est injoignable : vérifie la connexion, puis réessaie.' };
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
      ['calendrier', 'Calendrier des vacances', null],
      ['quizz_nsi', 'QuizzNSI', 'https://babash.github.io/QuizzNSI/'],
      ['gombessa', 'Expédition Gombessa', 'https://babash.github.io/Rappel-1er/'],
      ['court_circuit', 'Court-circuit', 'https://babash.github.io/court-circuit/'],
      ['grand_oral', 'Hello GO', null],
      ['lagon', 'Lagon Arena', 'https://babash.github.io/lagon-arena/'],
      ['alien', 'Alien Python', 'https://babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python/']
    ].map(function (a) { return { id: a[0], nom: a[1], adresse: a[2] }; });

    var emplacements = [
      ['lignee', 'Lignée', 'identite', null, true], ['fond', 'Décor', 'decor', 0, false],
      ['dos', 'Dos', 'tenue', 10, false], ['corps', 'Corps', 'identite', 30, true],
      ['marque', 'Marques et implants', 'identite', 32, false], ['bas', 'Bas', 'tenue', 40, false],
      ['pieds', 'Chaussures', 'tenue', 42, false], ['haut', 'Haut', 'tenue', 50, false],
      ['visage', 'Visage', 'identite', 60, true], ['coiffure', 'Coiffure', 'identite', 65, false],
      ['yeux', 'Lunettes et masques', 'tenue', 70, false], ['tete', 'Tête', 'tenue', 75, false],
      ['main', 'Dans la main', 'tenue', 80, false], ['familier', 'Familier', 'compagnon', 90, false],
      ['effet', 'Effet', 'decor', 95, false], ['attitude', 'Attitude', 'geste', null, false],
      ['succes', 'Réussite', 'geste', null, false], ['erreur', 'Erreur', 'geste', null, false]
    ].map(function (m) { return { id: m[0], nom: m[1], genre: m[2], plan: m[3], obligatoire: m[4] }; });

    /* [id, nom, accès, prix, lignées, teintable] : un catalogue d'essai, pas celui de T102 */
    var elements = [
      ['lignee:humain', 'Humain·e', 'libre'], ['lignee:cyber', 'Cyber', 'libre'], ['lignee:nuee', 'Nuée', 'libre'],
      ['lignee:mutant', 'Mutant·e', 'libre'], ['lignee:peuple-lagon', 'Peuple du lagon', 'libre'],
      ['lignee:esprit', 'Esprit', 'libre'], ['lignee:greffe', 'Greffé·e', 'libre'],
      ['corps:silhouette-a', 'Silhouette A', 'libre', null, null, true],
      ['corps:silhouette-b', 'Silhouette B', 'libre', null, null, true],
      ['corps:silhouette-c', 'Silhouette C', 'libre', null, null, true],
      ['visage:calme', 'Calme', 'libre'], ['visage:sourire-en-coin', 'Sourire en coin', 'libre'],
      ['visage:regard-concentre', 'Regard concentré', 'libre'],
      ['coiffure:rase', 'Rasé', 'libre', null, null, true], ['coiffure:tresses', 'Tresses', 'libre', null, null, true],
      ['coiffure:afro', 'Afro', 'libre', null, null, true], ['coiffure:chignon', 'Chignon', 'libre', null, null, true],
      ['coiffure:mi-longs', 'Mi-longs', 'libre', null, null, true],
      ['marque:pixels-qui-se-defont', 'Pixels qui se défont', 'libre'],
      ['marque:circuits-tempe', 'Circuits sur la tempe', 'libre', null, ['lignee:cyber', 'lignee:greffe']],
      ['marque:ouies-lumineuses', 'Ouïes lumineuses', 'libre', null, ['lignee:peuple-lagon']],
      ['fond:ciel-de-nuit', 'Ciel de nuit', 'libre'], ['fond:quai-de-la-barge', 'Quai de la barge', 'credits', 250],
      ['fond:ruelle-au-neon', 'Ruelle au néon', 'credits', 250],
      ['dos:sac-a-cables', 'Sac à câbles', 'credits', 100],
      ['haut:t-shirt-uni', 'T-shirt uni', 'libre', null, null, true],
      ['haut:veste-patchs', 'Veste à patchs', 'credits', 100, null, true],
      ['haut:sweat-circuits', 'Sweat à circuits imprimés', 'credits', 100, null, true],
      ['haut:gilet-reflechissant', 'Gilet réfléchissant', 'haut_fait'],
      ['bas:pantalon-cargo', 'Pantalon cargo', 'libre', null, null, true], ['bas:short', 'Short', 'libre', null, null, true],
      ['bas:jogging-neon', 'Jogging à liseré néon', 'credits', 40, null, true],
      ['pieds:baskets', 'Baskets', 'libre', null, null, true], ['pieds:claquettes', 'Claquettes', 'libre'],
      ['pieds:baskets-led', 'Baskets à LED', 'credits', 40],
      ['yeux:lunettes-rondes', 'Lunettes rondes', 'credits', 40], ['yeux:visiere-hud', 'Visière à affichage', 'credits', 100],
      ['tete:casquette', 'Casquette', 'credits', 40, null, true], ['tete:casque-led', 'Casque à LED', 'haut_fait'],
      ['main:clavier-pliable', 'Clavier pliable', 'credits', 40], ['main:fer-a-souder', 'Fer à souder', 'haut_fait'],
      ['familier:margouillat-turbines', 'Margouillat à turbines', 'credits', 250],
      ['familier:drone-de-poche', 'Drone de poche', 'credits', 250],
      ['familier:tortue-serveur', 'Tortue-serveur', 'haut_fait'],
      ['effet:pluie-de-donnees', 'Pluie de données', 'credits', 100],
      ['attitude:salut-deux-doigts', 'Salut à deux doigts', 'libre'], ['attitude:pouce-leve', 'Pouce levé', 'credits', 100],
      ['succes:glitch', 'Glitch', 'libre'], ['succes:petit-saut', 'Petit saut', 'credits', 100],
      ['erreur:fumee', 'Petite fumée', 'libre'], ['erreur:haussement-epaules', 'Haussement d\'épaules', 'libre']
    ].map(function (e, i) {
      return { id: e[0], emplacement: e[0].split(':')[0], nom: e[1], description: '', acces: e[2],
        prix: e[3] || null, lignees: e[4] || null, teintable: !!e[5], actif: true, ordre: i };
    });

    /* [application, id, nom, description, catégorie, accord, récompenses, indice si secret] */
    var hauts = [
      ['commun', 'premiere-planque', 'Première planque', 'Entrer dans sa planque avec son code.', 'premiers_pas', 'serveur', []],
      ['commun', 'coup-de-main', 'Coup de main', 'Aider un·e camarade à comprendre, sans faire à sa place.', 'entraide', 'enseignant', []],
      ['commun', 'explication-claire', 'Explication claire', 'Expliquer une notion à la classe.', 'entraide', 'enseignant', []],
      ['td', 'premiere-feuille', 'Première feuille', 'Valider en ligne sa première feuille de TD.', 'premiers_pas', 'page', []],
      ['td', 'erreur-surmontee', 'Erreur surmontée', 'Valider un exercice après au moins un essai raté.', 'perseverance', 'page', ['haut:gilet-reflechissant']],
      ['td', 'lecteur-de-traces', 'Lecteur de traces', 'Lire jusqu\'au bout le message d\'erreur de Python.', 'maitrise', 'page', [], 'Il paraît que certains messages d\'erreur cachent un indice.'],
      ['quizz_nsi', 'jusqu-au-bout', 'Jusqu\'au bout', 'Suivre un cours-quiz jusqu\'à la dernière question.', 'perseverance', 'page', []],
      ['calendrier', 'dix-jours-differents', 'Dix jours différents', 'Faire un mini-jeu dix jours différents, dans l\'ordre que tu veux.', 'perseverance', 'page', []],
      ['court_circuit', 'premier-circuit', 'Premier circuit', 'Faire avancer son robot jusqu\'au bout d\'un circuit.', 'premiers_pas', 'serveur', []],
      ['court_circuit', 'sortie-de-la-grotte', 'Sortie de la grotte', 'Trouver la sortie de la grotte avec une boucle.', 'exploration', 'serveur', ['main:fer-a-souder']],
      ['gombessa', 'premiere-plongee', 'Première plongée', 'Réussir sa première mission.', 'premiers_pas', 'serveur', ['familier:tortue-serveur']],
      ['lagon', 'premiere-manche', 'Première manche', 'Jouer une manche jusqu\'au bout.', 'premiers_pas', 'serveur', ['tete:casque-led']],
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
      ['calendrier', 'mini_jeu_fait', 'Mini-jeu du calendrier des vacances', 5, true],
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
      ['calendrier', 'mini_jeu_fait', 'cal:jour-01', 'Calendrier : jour 1']
    ].map(function (a) { return { application: a[0], evenement: a[1], cle: a[2], nom: a[3], actif: true }; });

    /* Tableaux de bord : dans la démonstration, ils ouvrent la démonstration de chaque application */
    var adressesProf = {
      commun: 'https://babash.github.io/Babash-NSI-SNT/enseignant/',
      gombessa: 'https://babash.github.io/Rappel-1er/prof.html',
      lagon: 'https://babash.github.io/lagon-arena/prof.html?demo',
      court_circuit: 'https://babash.github.io/court-circuit/prof.html?demo'
    };
    return { applications: apps, emplacements: emplacements, elements: elements, hauts_faits: hauts,
      bareme: bareme, activites: activites, adresses_prof: adressesProf };
  })();

  function implementationDemo() {
    var C = CATALOGUE_DEMO;
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
    function avatarDeDepart() {
      return { v: 1, porte: { lignee: 'lignee:humain', corps: 'corps:silhouette-a', visage: 'visage:calme', haut: 'haut:t-shirt-uni',
        bas: 'bas:pantalon-cargo', pieds: 'pieds:baskets' }, teintes: {} };
    }
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
            D.debloques.push({ compte_id: cid, element_id: eid, origine: 'haut_fait', depuis: quand || maintenant() });
            res.elements.push({ id: eid, nom: (element(eid) || {}).nom });
          }
        });
        res.credits += crediter(cid, app, 'haut_fait', 'hf:' + h.id, h.xp, 'haut_fait', null, null, quand);
        res.hauts_faits.push({ application: app, id: h.id, nom: h.nom });
      });
      return res;
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

    /* Comme commun.verifier_avatar */
    function verifierAvatar(cid, a) {
      if (!a || typeof a !== 'object' || Array.isArray(a) || a.v !== 1 || JSON.stringify(a).length > 4000) return null;
      if (Object.keys(a).some(function (k) { return ['v', 'porte', 'teintes'].indexOf(k) < 0; })) return null;
      var porte = {}, teintes = {}, lig = a.porte && a.porte.lignee, ok = true;
      Object.keys(a.porte || {}).forEach(function (k) {
        var e = element(a.porte[k]);
        if (!e || e.emplacement !== k || (e.lignees && e.lignees.indexOf(lig) < 0) ||
            !((e.acces === 'libre' && e.actif) || D.debloques.some(function (d) { return d.compte_id === cid && d.element_id === e.id; }))) ok = false;
        else porte[k] = e.id;
      });
      Object.keys(a.teintes || {}).forEach(function (k) {
        var v = a.teintes[k];
        if (typeof v !== 'string' || !/^[a-z0-9-]{1,24}$/.test(v) || !C.emplacements.some(function (m) { return m.id === k; })) ok = false;
        else teintes[k] = v;
      });
      return ok ? { v: 1, porte: porte, teintes: teintes } : null;
    }

    function fiche(cid) {
      var k = D.comptes[cid];
      if (!k) return null;
      return {
        pseudo: k.pseudo, pseudo_provisoire: k.pseudo_provisoire, avatar: copie(k.avatar), credits: k.credits,
        codes: D.codes.filter(function (x) { return x.compte_id === cid; })
          .sort(function (a, b) { return (b.principal - a.principal) || (a.cree_le < b.cree_le ? -1 : 1); })
          .map(function (x) { return { application: x.application, code_affiche: x.code_affiche, principal: x.principal }; }),
        applications: [],
        hauts_faits: D.gagnes.filter(function (g) { return g.compte_id === cid; })
          .map(function (g) { return { application: g.application, id: g.haut_fait, gagne_le: g.gagne_le }; }),
        elements: D.debloques.filter(function (d) { return d.compte_id === cid; }).map(function (d) { return d.element_id; }),
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

    var F = {
      /* ── L'élève (0007) ── */
      commun_creer: function (p) {
        var ps = nettoyerPseudo(p.p_pseudo);
        if (!ps) return { ok: false, message: 'Choisis un prénom ou un pseudo de 2 à 24 caractères (jamais ton nom de famille).' };
        var cid = creerCompte(ps), code = nouveauCodeEleve();
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
        return { version: 1, applications: C.applications, emplacements: C.emplacements, elements: C.elements,
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
        if (['td', 'calendrier', 'quizz_nsi'].indexOf(p.p_application) < 0) return { ok: false, message: 'Cette page ne donne pas de crédits.' };
        var g = gagnerXp(cid, p.p_application, p.p_evenement, p.p_cle, 'page');
        return { ok: true, credits_gagnes: g, message: g > 0 ? 'Bien joué : c\'est gardé.' : 'C\'est déjà gardé (une activité ne compte qu\'une fois).' };
      },
      commun_haut_fait_page: function (p) {
        var cid = compteParSession(p.p_jeton);
        if (!cid) return EXPIRE;
        if (['td', 'calendrier', 'quizz_nsi'].indexOf(p.p_application) < 0) return { ok: false, message: 'Cette application n\'accorde pas de haut fait depuis sa page.' };
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
              return { id: c.id, nom: c.nom, code: c.code, ouverte: c.ouverte, applications: c.applications.slice(),
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
          classe: { id: c.id, nom: c.nom, code: c.code, ouverte: c.ouverte, applications: c.applications.slice(), lien: lienClasse(c.code),
            tableaux: D.classes_liens.filter(function (l) { return l.classe_id === c.id; }).map(function (l) {
              var a = C.adresses_prof[l.application];
              return { application: l.application, nom: nomApp(l.application), reference: l.reference,
                adresse: a ? a + '#classe=' + l.reference : null };
            }) },
          eleves: D.inscriptions.filter(function (i) { return i.classe_id === c.id; }).map(function (i) { return D.comptes[i.compte_id]; })
            .sort(trierPseudo).map(function (k) {
              return { compte: k.id, pseudo: k.pseudo, avatar: copie(k.avatar), xp: k.xp, credits: k.credits, vu_le: k.vu_le,
                codes: D.codes.filter(function (x) { return x.compte_id === k.id; }).map(function (x) { return x.code_affiche; }),
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

      function av(lignee, corps, visage, coiffure, haut, bas, pieds, extra, teintes) {
        var porte = { lignee: 'lignee:' + lignee, corps: 'corps:' + corps, visage: 'visage:' + visage, coiffure: 'coiffure:' + coiffure,
          haut: 'haut:' + haut, bas: 'bas:' + bas, pieds: 'pieds:' + pieds };
        Object.keys(extra || {}).forEach(function (k) { porte[k] = extra[k]; });
        return { v: 1, porte: porte, teintes: teintes || {} };
      }
      /* [pseudo, n° du code, classe, avatar, jours depuis l'arrivée] : prénoms et pseudos inventés */
      var eleves = [
        ['Nour', 101, 'a', av('nuee', 'silhouette-b', 'sourire-en-coin', 'tresses', 'veste-patchs', 'pantalon-cargo', 'baskets',
          { marque: 'marque:pixels-qui-se-defont', attitude: 'attitude:salut-deux-doigts', fond: 'fond:ciel-de-nuit' }, { corps: 'peau-5', haut: 'neon-cyan' }), 40],
        ['Anli', 102, 'a', av('peuple-lagon', 'silhouette-a', 'calme', 'rase', 't-shirt-uni', 'short', 'claquettes',
          { marque: 'marque:ouies-lumineuses' }, { corps: 'peau-6', haut: 'neon-vert' }), 38],
        ['Zoé', 103, 'a', av('cyber', 'silhouette-c', 'regard-concentre', 'mi-longs', 'gilet-reflechissant', 'pantalon-cargo', 'baskets',
          { marque: 'marque:circuits-tempe', main: 'main:fer-a-souder' }, { corps: 'peau-2' }), 37],
        ['Kenji', 104, 'a', av('esprit', 'silhouette-a', 'calme', 'chignon', 't-shirt-uni', 'pantalon-cargo', 'baskets', null, { corps: 'peau-3', haut: 'neon-magenta' }), 35],
        ['Faïza', 105, 'a', av('mutant', 'silhouette-b', 'sourire-en-coin', 'afro', 't-shirt-uni', 'short', 'baskets', null, { corps: 'peau-4', haut: 'neon-jaune' }), 30],
        ['Maëlys', 106, 'b', av('greffe', 'silhouette-c', 'calme', 'tresses', 't-shirt-uni', 'pantalon-cargo', 'baskets-led',
          { familier: 'familier:margouillat-turbines' }, { corps: 'peau-5', haut: 'neon-violet' }), 50],
        ['Ibrahim', 107, 'b', av('humain', 'silhouette-a', 'sourire-en-coin', 'rase', 't-shirt-uni', 'pantalon-cargo', 'baskets',
          { tete: 'tete:casque-led' }, { corps: 'peau-6', haut: 'neon-cyan' }), 49],
        ['Sam', 108, 'b', av('nuee', 'silhouette-b', 'regard-concentre', 'mi-longs', 't-shirt-uni', 'short', 'claquettes', null, { corps: 'peau-1' }), 45]
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
          else if (x[0] === 'prof') crediter(cid, 'commun', 'attribution', null, x[1], 'enseignant', x[2], pid, q);
        });
      }
      fait('Nour', 30, [['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['hf', 'td', 'premiere-feuille', 'page'], ['hf', 'commun', 'premiere-planque']]);
      fait('Nour', 20, [['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files'], ['hf', 'quizz_nsi', 'jusqu-au-bout', 'page']]);
      fait('Nour', 12, [['xp', 'court_circuit', 'challenge_reussi', 'cc:defi-1'], ['hf', 'court_circuit', 'premier-circuit'], ['achat', 'haut:veste-patchs']]);
      fait('Nour', 4, [['prof', 20, 'Aide à un camarade sur les boucles'], ['hf', 'commun', 'coup-de-main', 'enseignant'], ['xp', 'td', 'feuille_validee', 'td:boucles-td2']]);
      fait('Anli', 25, [['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['hf', 'td', 'premiere-feuille', 'page'], ['hf', 'td', 'erreur-surmontee', 'page']]);
      fait('Anli', 8, [['xp', 'court_circuit', 'challenge_reussi', 'cc:defi-1'], ['xp', 'court_circuit', 'challenge_reussi', 'cc:defi-2'], ['hf', 'court_circuit', 'premier-circuit']]);
      fait('Zoé', 22, [['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['hf', 'td', 'erreur-surmontee', 'page'], ['hf', 'court_circuit', 'sortie-de-la-grotte']]);
      fait('Zoé', 6, [['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files'], ['hf', 'commun', 'premiere-planque']]);
      fait('Kenji', 15, [['xp', 'td', 'exercice_valide', 'td:boucles-td2/ex3'], ['hf', 'commun', 'premiere-planque']]);
      fait('Faïza', 9, [['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files'], ['hf', 'quizz_nsi', 'jusqu-au-bout', 'page']]);
      fait('Maëlys', 40, [['prof', 50, 'Exposé sur le chiffrement'], ['xp', 'td', 'feuille_validee', 'td:poo-td1'], ['xp', 'quizz_nsi', 'cours_quiz_suivi', 'quizz:piles-files']]);
      fait('Maëlys', 30, [['prof', 50, 'Exposé sur les arbres binaires'], ['xp', 'td', 'feuille_validee', 'td:boucles-td2'], ['prof', 50, 'Préparation du Grand oral'],
        ['xp', 'td', 'exercice_valide', 'td:boucles-td2/ex3'], ['hf', 'commun', 'coup-de-main', 'enseignant'], ['achat', 'familier:margouillat-turbines']]);
      fait('Maëlys', 10, [['hf', 'grand_oral', 'ma-question'], ['prof', 50, 'Aide en salle informatique'], ['achat', 'pieds:baskets-led']]);
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
    reglage = { en_ligne: false, probleme: null };
    if (!enLigne) { impl = implementationDemo(); return mode(); }
    if (!/^https:\/\/[a-z0-9]+\.supabase\.co\/?$/.test(url) || !cle) {
      reglage.probleme = 'COMPTE_COMMUN_EN_LIGNE vaut true, mais l\'adresse du projet (compte_commun.url) ou sa clé publique '
        + '(compte_commun.cle_publique) manque dans reglages.js : la page reste en démonstration.';
      if (window.console) console.warn('[compte commun] ' + reglage.probleme);
      impl = implementationDemo();
      return mode();
    }
    if (/service_role|sb_secret_/.test(cle)) {
      reglage.probleme = 'La clé donnée dans reglages.js n\'est pas une clé publique : elle est refusée, la page reste en démonstration.';
      impl = implementationDemo();
      return mode();
    }
    reglage.en_ligne = true;
    impl = implementationSupabase({ url: url, cle_publique: cle });
    return mode();
  }
  function mode() { return implementation().nom; }

  /* ── La session de l'élève sur cet appareil ── */
  var sessionMemoire = null;
  function lireSession() {
    if (mode() === 'demo') return sessionMemoire;
    var s = lireStockage(CLE_SESSION);
    if (!s || !s.jeton || !s.jusqu || new Date(s.jusqu) < new Date()) return null;
    return s;
  }
  function garderSession(jeton, jours, pseudo) {
    var s = { jeton: jeton, jusqu: new Date(Date.now() + jours * 864e5).toISOString(), pseudo: pseudo || null };
    if (mode() === 'demo') sessionMemoire = s;
    else ecrireStockage(CLE_SESSION, s);
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
      return rep;
    });
  }
  function apresEntree(jours) {
    return function (rep) {
      if (rep.ok && rep.jeton) garderSession(rep.jeton, jours, rep.fiche && rep.fiche.pseudo);
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
    var c = lireCodeProf();
    if (!c) return Promise.resolve({ ok: false, sans_session: true, message: 'Entre ton code d\'enseignant·e.' });
    params = params || {};
    params.p_code = c;
    return appeler(fonction, params);
  }

  var Prof = {
    creerEspace: function (nom, etablissement) {
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
    supprimerClasse: function (classe, confirmation) { return avecProf('commun_prof_supprimer_classe', { p_classe: classe, p_confirmation: confirmation }); },
    lierClasse: function (classe, app, reference, retirer) {
      return avecProf('commun_prof_lier_classe', { p_classe: classe, p_application: app, p_reference: reference, p_retirer: !!retirer });
    },
    classe: function (classe) { return avecProf('commun_prof_classe', { p_classe: classe }); },
    eleves: function () { return avecProf('commun_prof_eleves', {}); },
    attribuerXp: function (compte, xp, motif) { return avecProf('commun_prof_attribuer_xp', { p_compte: compte, p_xp: xp, p_motif: motif }); },
    journalXp: function (classe) { return avecProf('commun_prof_journal_xp', { p_classe: classe }); },
    accorder: function (compte, app, hautFait) { return avecProf('commun_prof_accorder', { p_compte: compte, p_application: app, p_haut_fait: hautFait }); },
    retirerEleve: function (classe, compte) { return avecProf('commun_prof_retirer_eleve', { p_classe: classe, p_compte: compte }); },
    renommerEleve: function (compte, pseudo) { return avecProf('commun_prof_renommer_eleve', { p_compte: compte, p_pseudo: pseudo }); },
    nouveauCodeEleve: function (compte) { return avecProf('commun_prof_nouveau_code_eleve', { p_compte: compte }); },
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

  var PALETTE = {
    'peau-1': '#F3D5B5', 'peau-2': '#E0B48C', 'peau-3': '#C68B5E', 'peau-4': '#A86B43', 'peau-5': '#8A5236', 'peau-6': '#5E3523',
    'neon-cyan': '#16F0FF', 'neon-magenta': '#FF2BD6', 'neon-vert': '#39FF88', 'neon-jaune': '#FFE14D', 'neon-violet': '#A67CFF',
    'neon-orange': '#FF9A3D', 'gris': '#8D9CBA', 'noir': '#1B2236', 'blanc': '#F2F6FF'
  };
  var TEINTES_LIGNEES = {
    'lignee:humain': '#C68B5E', 'lignee:cyber': '#9FB4D6', 'lignee:nuee': '#B59CFF', 'lignee:mutant': '#7FD66B',
    'lignee:peuple-lagon': '#4FC3C9', 'lignee:esprit': '#E8F0FF', 'lignee:greffe': '#D49A7A'
  };
  var TONS = ['#22D3EE', '#FF3D9A', '#A78BFA', '#34D399', '#FB923C', '#60A5FA', '#FACC15', '#F472B6', '#2DD4BF', '#E879F9'];

  function ton(id) {
    var h = 0;
    for (var i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) % 9973;
    return TONS[h % TONS.length];
  }

  function nomElement(catalogue, eid) {
    var e = catalogue && (catalogue.elements || []).filter(function (x) { return x.id === eid; })[0];
    return e ? e.nom : null;
  }

  /* « Avatar : Nuée, veste à patchs, margouillat à turbines » */
  function texteAvatar(avatar, catalogue, pseudo) {
    var p = (avatar && avatar.porte) || {};
    var ordre = ['lignee', 'coiffure', 'marque', 'haut', 'bas', 'pieds', 'dos', 'yeux', 'tete', 'main', 'familier', 'fond', 'effet'];
    var mots = [];
    ordre.forEach(function (k) {
      if (!p[k]) return;
      var n = nomElement(catalogue, p[k]);
      if (!n) return;
      mots.push(mots.length ? n.charAt(0).toLowerCase() + n.slice(1) : n);
    });
    return (pseudo ? 'Avatar de ' + pseudo : 'Avatar') + (mots.length ? ' : ' + mots.join(', ') : '');
  }

  /* Le dessin de remplacement : une silhouette en gros pixels, aux couleurs de ce qui est porté */
  function svgRemplacement(avatar) {
    var p = (avatar && avatar.porte) || {}, t = (avatar && avatar.teintes) || {};
    function teinte(k, defaut) { return PALETTE[t[k]] || defaut; }
    var peau = teinte('corps', TEINTES_LIGNEES[p.lignee] || '#C68B5E');
    var s = ['<svg viewBox="0 0 48 64" width="100%" height="100%" shape-rendering="crispEdges" aria-hidden="true" focusable="false">'];
    function r(x, y, w, h, c, extra) { s.push('<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + c + '"' + (extra || '') + '/>'); }
    if (p.fond) { r(0, 0, 48, 64, '#0B1330'); for (var i = 0; i < 6; i++) r(4 + i * 7, 6 + (i * 13) % 20, 2, 2, ton(p.fond + i), ' opacity=".8"'); }
    else r(0, 0, 48, 64, '#101830');
    r(0, 56, 48, 8, '#1A2440');
    if (p.effet) for (var k = 0; k < 8; k++) r(3 + k * 6, (k * 17) % 40, 1, 5, ton(p.effet), ' opacity=".7"');
    if (p.dos) r(9, 26, 30, 18, ton(p.dos));
    /* jambes, pieds */
    r(16, 44, 7, 12, p.bas ? teinte('bas', ton(p.bas)) : peau);
    r(25, 44, 7, 12, p.bas ? teinte('bas', ton(p.bas)) : peau);
    r(14, 55, 9, 3, p.pieds ? teinte('pieds', ton(p.pieds)) : '#2B3350');
    r(25, 55, 9, 3, p.pieds ? teinte('pieds', ton(p.pieds)) : '#2B3350');
    /* buste, bras */
    r(13, 26, 22, 19, p.haut ? teinte('haut', ton(p.haut)) : peau);
    r(9, 27, 4, 15, peau); r(35, 27, 4, 15, peau);
    /* tête */
    r(16, 8, 16, 17, peau);
    r(21, 24, 6, 3, peau);
    if (p.coiffure) {
      var ch = teinte('coiffure', '#2A1A12');
      if (/afro/.test(p.coiffure)) { r(12, 3, 24, 9, ch); r(12, 9, 4, 8, ch); r(32, 9, 4, 8, ch); }
      else if (/tresses|mi-longs/.test(p.coiffure)) { r(15, 6, 18, 5, ch); r(14, 9, 3, 16, ch); r(31, 9, 3, 16, ch); }
      else if (/chignon/.test(p.coiffure)) { r(15, 6, 18, 5, ch); r(20, 2, 8, 5, ch); }
      else r(16, 7, 16, 3, ch);
    }
    /* visage */
    r(20, 14, 2, 3, '#0B0F1E'); r(26, 14, 2, 3, '#0B0F1E');
    if (/sourire/.test(p.visage || '')) { r(21, 20, 6, 1, '#0B0F1E'); r(27, 19, 1, 1, '#0B0F1E'); }
    else r(22, 20, 4, 1, '#0B0F1E');
    if (p.marque) { r(17, 18, 1, 1, ton(p.marque)); r(18, 20, 1, 1, ton(p.marque)); r(30, 17, 1, 1, ton(p.marque)); }
    if (p.yeux) { r(18, 13, 12, 4, ton(p.yeux), ' opacity=".85"'); }
    if (p.tete) r(15, 4, 18, 5, teinte('tete', ton(p.tete)));
    if (p.main) r(38, 36, 5, 4, ton(p.main));
    if (p.familier) {
      var f = ton(p.familier);
      if (/margouillat/.test(p.familier)) { f = '#39C46A'; r(36, 52, 9, 3, f); r(44, 51, 2, 2, f); r(32, 53, 4, 1, f); r(30, 52, 2, 3, '#FF9A3D'); }
      else { r(37, 49, 8, 6, f); r(39, 51, 1, 1, '#0B0F1E'); r(42, 51, 1, 1, '#0B0F1E'); }
    }
    s.push('</svg>');
    return s.join('');
  }

  /* Le module du Designer, chargé une fois. Sans lui, le dessin de remplacement. */
  var equipagePromesse = null;
  function chargerEquipage() {
    if (window.Equipage && typeof window.Equipage.creer === 'function') return Promise.resolve(true);
    if (equipagePromesse) return equipagePromesse;
    equipagePromesse = new Promise(function (resoudre) {
      if (!RACINE || location.protocol === 'file:') return resoudre(false);
      var s = document.createElement('script');
      s.src = RACINE + 'assets/equipage.js';
      s.async = true;
      s.onload = function () { resoudre(!!(window.Equipage && typeof window.Equipage.creer === 'function')); };
      s.onerror = function () { resoudre(false); };
      document.head.appendChild(s);
    });
    return equipagePromesse;
  }

  /* Dessine un avatar dans element. options : { etat: 'lobby'…, taille: 'grand'|'moyen'|'petit',
     catalogue, pseudo }. Le conteneur porte le texte de remplacement ; le dessin est décoratif. */
  function dessinerAvatar(element, avatar, options) {
    options = options || {};
    element.classList.add('avatar', 'avatar-' + (options.taille || 'moyen'));
    element.setAttribute('role', 'img');
    element.setAttribute('aria-label', texteAvatar(avatar, options.catalogue, options.pseudo));
    function remplacement() {
      element.innerHTML = svgRemplacement(avatar);
      element.setAttribute('data-dessin', 'remplacement');
    }
    remplacement();
    chargerEquipage().then(function (present) {
      if (!present) return;
      try {
        var zone = document.createElement('div');
        zone.className = 'avatar-dessin';
        zone.setAttribute('aria-hidden', 'true');
        var reduit = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        window.Equipage.creer(zone, copie(avatar), { etat: options.etat || 'repos', taille: options.taille || 'moyen', animation: !reduit });
        element.innerHTML = '';
        element.appendChild(zone);
        element.setAttribute('data-dessin', 'equipage');
      } catch (e) {
        if (window.console) console.warn('[compte commun] Equipage.creer a échoué, dessin de remplacement : ' + (e && e.message || e));
        remplacement();
      }
    });
    return element;
  }

  window.CompteCommun = {
    version: 1,
    configurer: configurer,
    mode: mode,
    probleme: function () { return reglage.probleme; },
    normaliserCode: normaliserCode,
    nettoyerPseudo: nettoyerPseudo,
    nettoyerTexte: nettoyerTexte,

    /* L'élève */
    connecte: function () { return !!jeton(); },
    pseudoMemorise: function () { var s = lireSession(); return s ? s.pseudo : null; },
    catalogue: function () { return appeler('commun_catalogue', {}); },
    creer: function (pseudo, options) {
      return appeler('commun_creer', { p_pseudo: pseudo, p_garde_jours: jours(options) }).then(apresEntree(jours(options)));
    },
    entrer: function (code, options) {
      return appeler('commun_entrer', { p_code: code, p_garde_jours: jours(options) }).then(apresEntree(jours(options)));
    },
    reprendre: function () { return avecSession('commun_reprise', {}); },
    porter: function (avatar) { return avecSession('commun_porter', { p_avatar: avatar }); },
    acheter: function (element) { return avecSession('commun_acheter', { p_element: element }); },
    renommer: function (pseudo) { return avecSession('commun_renommer', { p_pseudo: pseudo }); },
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
    palette: function () { return copie(PALETTE); },

    /* La démonstration : les codes fictifs à essayer (null en mode en ligne) */
    demo: function () {
      var i = implementation();
      return i.codesDemo ? i.codesDemo() : null;
    }
  };
})();
