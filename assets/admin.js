/* ═══════════════════════════════════════════════════════════════
   L'espace administrateur (T51) : …/admin/

   - Ressources : la liste des fiches, avec recherche et filtres.
   - Fiche : annoter et modifier une fiche (textes, statut, notes,
     classements, programme, mots-clés, documents et leur visibilité).
   - Onglets : composer chaque rubrique (donnees/vitrine.json) et « À la une ».
   - Aperçu : l'onglet tel qu'il sera, dessiné par assets/site.js.
   - Changements : ce qui est en attente ; enregistrer (un commit par
     l'API GitHub, avec le jeton de l'enseignant) ou télécharger.

   Le mot de passe administrateur (décision du 17/11) protège le jeton GitHub
   gardé sur l'appareil : le jeton y est chiffré (PBKDF2-SHA-256, 600 000
   itérations, sel aléatoire ; AES-GCM, vecteur aléatoire), jamais en clair.
   Déchiffré, il reste en mémoire le temps de la visite. Le mot de passe n'est
   gardé nulle part et n'est envoyé à personne. Le jeton n'est jamais affiché,
   jamais mis dans une adresse ni dans le dépôt. Avant tout enregistrement,
   les fichiers sont validés (assets/donnees.js) : un enregistrement ne peut
   pas arrêter « Publier le site ». Si un fichier a changé sur main depuis son
   ouverture, rien n'est écrit (conflit) : l'admin le dit et recharge.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var D = window.Donnees;
  var API = 'https://api.github.com';
  var BRANCHE = 'main';
  /* Le jeton, chiffré avec le mot de passe administrateur (décision de l'enseignant du 17/11) :
     localStorage[CLE_COFFRE] = { version, iterations, sel, iv, chiffre } (base64). Le jeton déchiffré
     reste dans jetonEnMemoire le temps de la visite ; le mot de passe n'est jamais gardé. */
  var CLE_COFFRE = 'admin-jeton-chiffre';
  var ANCIENNES_CLES = ['admin-jeton-github']; // gardes précédentes : effacées au démarrage
  var ITERATIONS = 600000;
  var MDP_MIN = 10;
  var jetonEnMemoire = '';

  function b64(octets) {
    var bin = '';
    for (var i = 0; i < octets.length; i++) bin += String.fromCharCode(octets[i]);
    return btoa(bin);
  }
  function deB64(t) {
    var bin = atob(t), o = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) o[i] = bin.charCodeAt(i);
    return o;
  }
  function cryptoPossible() {
    return !!(window.crypto && window.crypto.subtle && window.isSecureContext !== false);
  }
  function cle(mdp, sel, iterations) {
    var c = window.crypto.subtle;
    return c.importKey('raw', new TextEncoder().encode(mdp), 'PBKDF2', false, ['deriveKey']).then(function (base) {
      return c.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt: sel, iterations: iterations },
        base, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
    });
  }
  function coffre() {
    var c = lireStockage(CLE_COFFRE, null);
    return c && c.version === 1 && c.sel && c.iv && c.chiffre ? c : null;
  }
  /* Chiffrer et garder le jeton ; promesse */
  function fermerCoffre(jetonClair, mdp) {
    var sel = window.crypto.getRandomValues(new Uint8Array(16));
    var iv = window.crypto.getRandomValues(new Uint8Array(12));
    return cle(mdp, sel, ITERATIONS).then(function (k) {
      return window.crypto.subtle.encrypt({ name: 'AES-GCM', iv: iv }, k, new TextEncoder().encode(jetonClair));
    }).then(function (chiffre) {
      if (!ecrireStockage(CLE_COFFRE, { version: 1, iterations: ITERATIONS, sel: b64(sel), iv: b64(iv), chiffre: b64(new Uint8Array(chiffre)) })) {
        throw new Error('Le navigateur refuse de garder le jeton chiffré (navigation privée ?).');
      }
      jetonEnMemoire = jetonClair;
    });
  }
  /* Déchiffrer le jeton avec le mot de passe ; promesse rejetée si le mot de passe est faux */
  function ouvrirCoffre(mdp) {
    var c = coffre();
    if (!c) return Promise.reject(new Error('Aucun jeton n\'est gardé sur cet appareil.'));
    return cle(mdp, deB64(c.sel), c.iterations || ITERATIONS).then(function (k) {
      return window.crypto.subtle.decrypt({ name: 'AES-GCM', iv: deB64(c.iv) }, k, deB64(c.chiffre));
    }).then(function (clair) {
      jetonEnMemoire = new TextDecoder().decode(clair);
    }, function () {
      throw new Error('Mot de passe incorrect : le jeton n\'a pas pu être déchiffré.');
    });
  }
  function verrouiller() { jetonEnMemoire = ''; etat.chemins = null; }
  function oublierAppareil() { verrouiller(); ecrireStockage(CLE_COFFRE, null); }

  /* Les seuls fichiers que l'admin écrit (contrôle du Gardien, 17/11) : la vitrine et les fiches.
     Tout autre chemin (brouillon ou fichiers récents du navigateur, partagés par toutes les pages de
     l'origine) est ignoré et signalé, et n'est jamais écrit ni archivé. */
  var CHEMIN_FICHE = /^donnees\/ressources\/[a-z0-9]+(-[a-z0-9]+)*\.json$/;
  function cheminPermis(c) {
    return c === VITRINE || CHEMIN_FICHE.test(String(c));
  }
  var CLE_BROUILLON = 'admin-brouillon';
  var CLE_RECENTS = 'admin-recents';
  var RECENT_MS = 30 * 60 * 1000; // le temps que « Publier le site » reconstruise la bibliothèque
  var VITRINE = 'donnees/vitrine.json';
  var PUBLICS = { exterieur: 'l\'extérieur', eleve: 'les élèves' };

  var O;           // les outils prêtés par site.js
  var el;
  var etat = {
    complete: null,  // donnees/bibliotheque-complete.json
    refs: null,      // Donnees.Referentiels
    schemas: {},
    validation: null,
    fichiers: {},    // chemin → { base: { texte, objet, sha }, courant }
    chemins: null,   // les chemins du dépôt (arbre de main), avec le jeton
    message: null,   // { niveau: 'ok'|'erreur'|'info', texte, actions }
    occupe: false,
    filtres: { q: '', statut: '', cache: '', ens: '', notes: false },
    recherches: {},  // la recherche de chaque liste de cases, gardée quand la vue est redessinée
    rubrique: null,
    ignores: []      // chemins refusés trouvés dans le brouillon ou les fichiers récents
  };
  var racinePage, vue, barreBas, annonce;

  /* ── Petits outils ────────────────────────────────────────────── */

  function aujourdhui() {
    var d = new Date();
    function z(n) { return (n < 10 ? '0' : '') + n; }
    return d.getFullYear() + '-' + z(d.getMonth() + 1) + '-' + z(d.getDate());
  }

  function lireStockage(cle, defaut) {
    try { var v = localStorage.getItem(cle); return v == null ? defaut : JSON.parse(v); } catch (e) { return defaut; }
  }
  function ecrireStockage(cle, v) {
    try { if (v == null) localStorage.removeItem(cle); else localStorage.setItem(cle, JSON.stringify(v)); return true; } catch (e) { return false; }
  }

  function jeton() { return jetonEnMemoire; }

  function depot() {
    var d = (O.reglages().depot || 'babash/Babash-NSI-SNT').replace(/^https?:\/\/(www\.)?github\.com\//i, '').replace(/(\.git)?\/*$/, '');
    return /^[A-Za-z0-9-]+\/[A-Za-z0-9._-]+$/.test(d) ? d : 'babash/Babash-NSI-SNT';
  }

  function libelle(listeNom, id) {
    var e = ((etat.complete.referentiels.valeurs || {})[listeNom] || []).filter(function (x) { return x.id === id; })[0];
    return e ? e.libelle : id;
  }

  function valeursDe(listeNom) {
    return (etat.complete.referentiels.valeurs || {})[listeNom] || [];
  }

  function cheminFiche(id) { return 'donnees/ressources/' + id + '.json'; }

  function idDeChemin(chemin) {
    var m = /^donnees\/ressources\/(.+)\.json$/.exec(chemin);
    return m ? m[1] : null;
  }

  function annoncer(texte) {
    if (!annonce) return;
    annonce.textContent = '';
    setTimeout(function () { annonce.textContent = texte; }, 30);
  }

  function bouton(texte, action, options) {
    options = options || {};
    var b = el('button', {
      type: 'button', class: 'btn' + (options.classe ? ' ' + options.classe : ''),
      'aria-label': options.aria || null, title: options.titre || null,
      'data-cle': options.cle || null, disabled: options.inactif ? true : null
    }, texte);
    b.addEventListener('click', function (e) { e.preventDefault(); action(e); });
    return b;
  }

  /* ── Les fiches : l'état de chacune ───────────────────────────── */

  function ficheComplete(id) {
    return etat.complete.ressources.filter(function (r) { return r.id === id; })[0] || null;
  }

  /* La fiche telle qu'elle est en ce moment dans l'admin (modifiée ou non) */
  function ficheCourante(id) {
    var f = etat.fichiers[cheminFiche(id)];
    if (f) return f.courant;
    return ficheComplete(id);
  }

  function modifie(chemin) {
    var f = etat.fichiers[chemin];
    return !!(f && f.base && !D.egal(f.base.objet, f.courant));
  }

  function enAttente() {
    return Object.keys(etat.fichiers).filter(function (c) { return cheminPermis(c) && modifie(c); }).sort(function (a, b) {
      return a === VITRINE ? -1 : b === VITRINE ? 1 : a < b ? -1 : 1;
    });
  }

  function visibilite(fiche) {
    var docs = (fiche && fiche.documents) || [];
    var vu = {};
    Object.keys(PUBLICS).forEach(function (p) {
      vu[p] = docs.some(function (d) { return d.visible && d.visible[p] === true; });
    });
    return vu;
  }

  function badgeCache(v) {
    if (!v.exterieur && !v.eleve) return 'caché : tous';
    if (!v.exterieur) return 'caché : extérieur';
    if (!v.eleve) return 'caché : élèves';
    return null;
  }

  /* La fiche vue de l'extérieur (comme construire_bibliotheque.py) : pour l'aperçu */
  function vuePublique(fiche) {
    var docs = (fiche.documents || []).filter(function (d) { return d.visible && d.visible.exterieur === true; });
    if (!docs.length) return null;
    var f = {};
    Object.keys(fiche).forEach(function (k) { if (k !== '$schema' && k !== 'notes' && k !== 'documents' && k !== 'visibilite') f[k] = fiche[k]; });
    var principal = 0;
    docs.forEach(function (d, i) { if (d.principal === true) principal = i; });
    f.documents = docs.map(function (d, i) {
      var c = {};
      Object.keys(d).forEach(function (k) { if (k !== 'visible') c[k] = d[k]; });
      c.principal = i === principal;
      return c;
    });
    return f;
  }

  /* ── Lire les fichiers bruts ──────────────────────────────────── */

  function api(methode, chemin, corps) {
    var options = {
      method: methode,
      headers: {
        Authorization: 'Bearer ' + jeton(),
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      cache: 'no-store'
    };
    if (corps !== undefined) {
      options.body = JSON.stringify(corps);
      options.headers['Content-Type'] = 'application/json';
    }
    return fetch(API + '/repos/' + depot() + chemin, options).then(function (r) {
      return r.text().then(function (t) {
        var donnees = null;
        try { donnees = t ? JSON.parse(t) : null; } catch (e) { donnees = null; }
        if (!r.ok) {
          var err = new Error(messageApi(r.status, donnees));
          err.statut = r.status;
          throw err;
        }
        return donnees;
      });
    });
  }

  function messageApi(statut, donnees) {
    var detail = donnees && donnees.message ? ' (GitHub : « ' + donnees.message + ' »)' : '';
    if (statut === 401) return 'GitHub refuse le jeton : il est faux ou a expiré. En créer un nouveau (onglet Jeton).' + detail;
    if (statut === 403) return 'GitHub refuse l\'écriture : le jeton n\'a pas le droit « Contents : Read and write » sur ce dépôt, ou une règle protège la branche main.' + detail;
    if (statut === 404) return 'Introuvable sur GitHub : le jeton donne-t-il accès à ce dépôt (' + depot() + ') ?' + detail;
    if (statut === 409 || statut === 422) return 'GitHub n\'a pas accepté la modification : main a changé entre-temps.' + detail;
    return 'Réponse inattendue de GitHub (code ' + statut + ').' + detail;
  }

  function decoder64(b64) {
    var bin = atob(b64.replace(/\s/g, ''));
    var octets = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) octets[i] = bin.charCodeAt(i);
    return new TextDecoder('utf-8').decode(octets);
  }

  /* Le texte d'un fichier du dépôt : par l'API (à jour, avec son empreinte), sinon sur le site */
  function lireBrut(chemin) {
    if (jeton()) {
      return api('GET', '/contents/' + chemin.split('/').map(encodeURIComponent).join('/') + '?ref=' + BRANCHE).then(function (r) {
        return { texte: decoder64(r.content || ''), sha: r.sha };
      });
    }
    return fetch(O.racine + chemin, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('fichier introuvable sur le site : ' + chemin);
      return r.text();
    }).then(function (t) { return { texte: t, sha: null }; });
  }

  /* Ouvrir un fichier pour le modifier : on part de sa version brute (jamais de la bibliothèque construite) */
  function ouvrir(chemin) {
    if (etat.fichiers[chemin] && etat.fichiers[chemin].base) return Promise.resolve(etat.fichiers[chemin]);
    return lireBrut(chemin).then(function (b) {
      var objet = JSON.parse(b.texte);
      var f = etat.fichiers[chemin] || {};
      f.base = { texte: b.texte, objet: objet, sha: b.sha };
      if (!f.courant) f.courant = D.copie(objet);
      etat.fichiers[chemin] = f;
      return f;
    });
  }

  function chargerArbre() {
    if (!jeton()) { etat.chemins = null; return Promise.resolve(null); }
    return api('GET', '/git/trees/' + BRANCHE + '?recursive=1').then(function (r) {
      var c = {};
      (r.tree || []).forEach(function (t) { c[t.path] = t.type === 'tree' ? 'dossier' : t.sha; });
      etat.chemins = c;
      return c;
    });
  }

  /* Un fichier du site existe-t-il ? true, false, ou null si on ne sait pas */
  function existe(chemin) {
    if (!etat.chemins) return null;
    chemin = chemin.replace(/\/$/, '');
    if (etat.chemins[chemin] === 'dossier') return !!etat.chemins[chemin + '/index.html'];
    return !!etat.chemins[chemin];
  }

  /* ── Brouillon : les changements survivent à un rechargement ──── */

  function garderBrouillon() {
    var b = {};
    enAttente().forEach(function (c) {
      var f = etat.fichiers[c];
      b[c] = { base: f.base.texte, sha: f.base.sha, courant: f.courant };
    });
    ecrireStockage(CLE_BROUILLON, Object.keys(b).length ? b : null);
  }

  function reprendreBrouillon() {
    var b = lireStockage(CLE_BROUILLON, null);
    if (!b || typeof b !== 'object') return 0;
    var n = 0;
    Object.keys(b).forEach(function (c) {
      if (!cheminPermis(c)) { etat.ignores.push(c); return; }
      try {
        etat.fichiers[c] = { base: { texte: b[c].base, objet: JSON.parse(b[c].base), sha: b[c].sha || null }, courant: b[c].courant };
        n++;
      } catch (e) { /* brouillon illisible : ignoré */ }
    });
    return n;
  }

  /* Les fichiers enregistrés il y a peu : la bibliothèque construite ne les a peut-être pas encore */
  function appliquerRecents() {
    var r = lireStockage(CLE_RECENTS, {});
    var maintenant = Date.now();
    Object.keys(r).forEach(function (c) {
      if (!cheminPermis(c)) { etat.ignores.push(c); delete r[c]; return; }
      if (maintenant - r[c].quand > RECENT_MS) { delete r[c]; return; }
      var id = idDeChemin(c);
      try {
        var objet = JSON.parse(r[c].texte);
        if (c === VITRINE) etat.complete.vitrine = objet;
        else if (id) {
          var i = etat.complete.ressources.map(function (x) { return x.id; }).indexOf(id);
          if (i >= 0) etat.complete.ressources[i] = objet;
        }
      } catch (e) { /* ignoré */ }
    });
    ecrireStockage(CLE_RECENTS, r);
  }

  /* ── Validation ───────────────────────────────────────────────── */

  function valider(chemin) {
    var f = etat.fichiers[chemin];
    if (!f) return [];
    etat.validation.fichiers = existe;
    if (chemin === VITRINE) return etat.validation.vitrine(f.courant);
    return etat.validation.fiche(f.courant, chemin.split('/').pop());
  }

  function erreursEnAttente() {
    var out = [];
    enAttente().forEach(function (c) {
      valider(c).forEach(function (e) { out.push({ chemin: c, champ: e[0], message: e[1] }); });
    });
    return out;
  }

  function blocErreurs(erreurs, titre) {
    if (!erreurs.length) return null;
    return el('div', { class: 'alerte', role: 'alert' }, [
      el('p', null, el('strong', null, titre || 'À corriger avant d\'enregistrer')),
      el('ul', null, erreurs.map(function (e) {
        return el('li', null, [e.chemin ? el('code', null, e.chemin) : null, e.chemin ? ' ' : null,
          e.champ ? el('code', null, e.champ) : null, e.champ ? ' : ' : null, e.message]);
      }))
    ]);
  }

  /* ── Rendu général ────────────────────────────────────────────── */

  var ONGLETS = [
    { id: 'ressources', nom: 'Ressources' },
    { id: 'onglets', nom: 'Onglets du site' },
    { id: 'changements', nom: 'Changements' },
    { id: 'jeton', nom: 'Mot de passe' }
  ];

  function route() {
    var h = decodeURIComponent((location.hash || '').replace(/^#\/?/, ''));
    var m = h.split('/');
    return { vue: m[0] || 'ressources', arg: m.slice(1).join('/') };
  }

  function aller(h) {
    if (location.hash === '#/' + h) rendre();
    else location.hash = '#/' + h;
  }

  /* Tout redessiner, en gardant le focus et la position de lecture */
  function rendre(focusCle) {
    var actif = document.activeElement;
    var cle = focusCle || (actif && actif.getAttribute && actif.getAttribute('data-cle'));
    var y = window.scrollY;
    etat.focusEnCours = cle || null; // pour les morceaux qui se rouvrent autour du focus (listes de cases)
    O.vider(vue);
    var r = route();
    var nav = el('nav', { class: 'admin-onglets', 'aria-label': 'Espace administrateur' }, el('ul', null, ONGLETS.map(function (o) {
      var actifO = r.vue === o.id || (o.id === 'ressources' && r.vue === 'fiche');
      var n = o.id === 'changements' ? enAttente().length : 0;
      return el('li', null, el('a', { href: '#/' + o.id, 'aria-current': actifO ? 'page' : null },
        [o.nom, n ? el('span', { class: 'nb' }, String(n)) : null]));
    })));
    vue.appendChild(nav);
    if (etat.message) vue.appendChild(blocMessage());
    if (r.vue !== 'jeton' && coffre() && !jeton() && cryptoPossible() && !etat.lectureSeule) {
      var porte = blocDeverrouiller(true);
      porte.querySelector('.admin-actions').appendChild(bouton('Continuer en lecture', function () { etat.lectureSeule = true; rendre(); }, { cle: 'lecture' }));
      vue.appendChild(porte);
    }
    if (r.vue === 'fiche') vueFiche(r.arg);
    else if (r.vue === 'onglets') vueOnglets(r.arg);
    else if (r.vue === 'changements') vueChangements();
    else if (r.vue === 'jeton') vueJeton();
    else vueRessources();
    rendreBarreBas();
    if (cle) {
      var trouver = function (c) {
        var s = '[data-cle="' + c.replace(/"/g, '\\"') + '"]';
        return vue.querySelector(s) || barreBas.querySelector(s);
      };
      var cible = trouver(cle);
      // une flèche devenue inactive (premier ou dernier rang) : l'autre flèche du même élément
      if (cible && cible.disabled) {
        var autre = /-monter$/.test(cle) ? cle.replace(/-monter$/, '-descendre') : cle.replace(/-descendre$/, '-monter');
        cible = trouver(autre) || cible;
      }
      if (cible && !cible.disabled) cible.focus({ preventScroll: true });
    }
    if (!focusCle) window.scrollTo(0, y);
  }

  function blocMessage() {
    var m = etat.message;
    return el('div', { class: 'admin-message ' + m.niveau, role: m.niveau === 'erreur' ? 'alert' : 'status' }, [
      el('p', null, m.texte),
      m.liste ? el('ul', null, m.liste.map(function (x) { return el('li', null, x); })) : null,
      el('p', { class: 'admin-actions' }, (m.actions || []).concat([bouton('Fermer ce message', function () { etat.message = null; rendre(); })]))
    ]);
  }

  function rendreBarreBas() {
    O.vider(barreBas);
    var n = enAttente().length;
    barreBas.hidden = !n;
    if (!n) return;
    var erreurs = erreursEnAttente();
    barreBas.appendChild(el('div', { class: 'barre-bas-int' }, [
      el('p', null, [el('strong', null, n + (n > 1 ? ' fichiers modifiés' : ' fichier modifié')),
        erreurs.length ? el('span', { class: 'a-corriger' }, ' · ' + erreurs.length + ' erreur' + (erreurs.length > 1 ? 's' : '') + ' à corriger') : null]),
      el('p', { class: 'admin-actions' }, [
        el('a', { class: 'btn', href: '#/changements' }, 'Voir les changements'),
        jeton()
          ? bouton(etat.occupe ? 'Enregistrement…' : 'Enregistrer', enregistrer, { classe: 'principal', cle: 'enregistrer', inactif: etat.occupe || erreurs.length > 0 })
          : bouton('Télécharger les fichiers', telecharger, { classe: 'principal', cle: 'telecharger', inactif: erreurs.length > 0 })
      ])
    ]));
  }

  /* Un changement : l'état est à jour ; on garde le brouillon et on met à jour la barre */
  function change(redessiner) {
    garderBrouillon();
    if (redessiner) rendre(); else rendreBarreBas();
    var compteur = vue.querySelector('.admin-onglets a[href="#/changements"]');
    if (compteur) {
      var n = enAttente().length;
      O.vider(compteur);
      compteur.appendChild(document.createTextNode('Changements'));
      if (n) compteur.appendChild(el('span', { class: 'nb' }, String(n)));
    }
  }

  /* ── Vue : la liste des ressources ────────────────────────────── */

  function vueRessources() {
    var f = etat.filtres;
    var ids = etat.complete.ressources.map(function (r) { return r.id; });
    var titre = el('h1', null, 'Ressources');
    vue.appendChild(titre);
    vue.appendChild(el('p', { class: 'admin-aide' }, 'Choisir une ressource pour l\'annoter ou modifier sa fiche. Les notes et les documents cachés restent lisibles dans le dépôt public : jamais de mot de passe ni de nom d\'élève.'));

    var champs = el('div', { class: 'admin-filtres' });
    var q = el('input', { type: 'search', id: 'admin-q', class: 'recherche', 'data-cle': 'filtre-q', placeholder: 'Titre, identifiant, mot-clé', value: f.q, autocomplete: 'off' });
    champs.appendChild(el('label', { for: 'admin-q' }, 'Chercher'));
    champs.appendChild(q);
    function choix(id, nom, valeur, options) {
      var s = el('select', { id: id, 'data-cle': id }, options.map(function (o) {
        return el('option', { value: o[0], selected: o[0] === valeur ? true : null }, o[1]);
      }));
      champs.appendChild(el('label', { for: id }, nom));
      champs.appendChild(s);
      return s;
    }
    var sStatut = choix('admin-statut', 'Statut', f.statut, [['', 'Tous']].concat(valeursDe('statuts').map(function (s) { return [s.id, s.libelle]; })));
    var sCache = choix('admin-cache', 'Visibilité', f.cache, [['', 'Toutes'], ['un', 'Un document caché'], ['exterieur', 'Cachée de l\'extérieur'], ['eleve', 'Cachée des élèves'], ['visible', 'Tout visible']]);
    var sEns = choix('admin-ens', 'Enseignement', f.ens, [['', 'Tous']].concat(valeursDe('enseignements').map(function (s) { return [s.id, s.libelle]; })));
    var cNotes = el('input', { type: 'checkbox', id: 'admin-notes', 'data-cle': 'admin-notes', checked: f.notes ? true : null });
    champs.appendChild(el('label', { class: 'admin-case', for: 'admin-notes' }, [cNotes, ' Avec des notes']));
    vue.appendChild(champs);

    var liste = el('ul', { class: 'admin-liste', id: 'contenu' });
    var statut = el('p', { class: 'statut', role: 'status' });
    vue.appendChild(statut);
    vue.appendChild(liste);

    function maj() {
      f.q = q.value.trim(); f.statut = sStatut.value; f.cache = sCache.value; f.ens = sEns.value; f.notes = cNotes.checked;
      var mots = O.sansAccents(f.q).toLowerCase().split(/\s+/).filter(Boolean);
      O.vider(liste);
      var n = 0;
      ids.forEach(function (id) {
        var r = ficheCourante(id);
        var v = visibilite(r);
        var cacheUn = (r.documents || []).some(function (d) { return !d.visible || d.visible.exterieur === false || d.visible.eleve === false; });
        if (f.statut && r.statut !== f.statut) return;
        if (f.ens && (r.enseignements || []).indexOf(f.ens) < 0) return;
        if (f.notes && !(r.notes || []).length) return;
        if (f.cache === 'un' && !cacheUn) return;
        if (f.cache === 'exterieur' && v.exterieur) return;
        if (f.cache === 'eleve' && v.eleve) return;
        if (f.cache === 'visible' && cacheUn) return;
        if (mots.length) {
          var t = O.sansAccents([r.titre, r.id, (r.mots_cles || []).join(' '), r.accroche || ''].join(' ')).toLowerCase();
          if (!mots.every(function (m) { return t.indexOf(m) >= 0; })) return;
        }
        n++;
        var badges = [];
        if (r.statut && r.statut !== 'prete') badges.push(el('span', { class: 'badge statut-' + r.statut }, libelle('statuts', r.statut)));
        var bc = badgeCache(v);
        if (bc) badges.push(el('span', { class: 'badge cache' }, bc));
        else if (cacheUn) badges.push(el('span', { class: 'badge cache' }, 'un document caché'));
        if ((r.notes || []).length) badges.push(el('span', { class: 'badge' }, r.notes.length + (r.notes.length > 1 ? ' notes' : ' note')));
        if (modifie(cheminFiche(id))) badges.push(el('span', { class: 'badge modifie' }, 'modifiée'));
        liste.appendChild(el('li', null, [
          el('a', { href: '#/fiche/' + encodeURIComponent(id), class: 'admin-titre' }, r.titre),
          el('p', { class: 'admin-id' }, [el('code', null, id), ' · ', (r.enseignements || []).map(function (e) { return libelle('enseignements', e); }).join(', ')]),
          badges.length ? el('p', { class: 'badges' }, badges) : null
        ]));
      });
      statut.textContent = n + (n > 1 ? ' ressources' : ' ressource') + ' sur ' + ids.length;
    }
    [q].forEach(function (x) { x.addEventListener('input', maj); });
    [sStatut, sCache, sEns, cNotes].forEach(function (x) { x.addEventListener('change', maj); });
    maj();
  }

  /* ── Vue : une fiche ──────────────────────────────────────────── */

  function vueFiche(id) {
    var chemin = cheminFiche(id);
    var f = etat.fichiers[chemin];
    if (!f || !f.base) {
      if (!ficheComplete(id)) {
        vue.appendChild(el('h1', null, 'Ressource inconnue'));
        vue.appendChild(el('p', null, ['Aucune fiche « ', el('code', null, id), ' ». ', el('a', { href: '#/ressources' }, 'Revenir à la liste')]));
        return;
      }
      vue.appendChild(el('p', { class: 'statut', role: 'status' }, 'Ouverture de la fiche…'));
      ouvrir(chemin).then(function () { rendre(); }, function (e) {
        etat.message = { niveau: 'erreur', texte: 'La fiche « ' + id + ' » n\'a pas pu être lue : ' + e.message };
        aller('ressources');
      });
      return;
    }
    var fiche = f.courant;
    function maj(redessiner) { change(redessiner); majErreurs(); }

    vue.appendChild(el('p', { class: 'admin-retour' }, el('a', { href: '#/ressources' }, '← Toutes les ressources')));
    vue.appendChild(el('h1', { id: 'contenu' }, fiche.titre || id));
    vue.appendChild(el('p', { class: 'admin-id' }, [el('code', null, chemin), ' · ',
      el('a', { href: O.urlBibliotheque('?r=' + encodeURIComponent(id)), target: '_blank', rel: 'noopener' }, 'voir la fiche publique')]));

    var zoneErreurs = el('div', { 'aria-live': 'polite' });
    vue.appendChild(zoneErreurs);
    function majErreurs() {
      O.vider(zoneErreurs);
      var b = blocErreurs(valider(chemin).map(function (e) { return { champ: e[0], message: e[1] }; }), 'Cette fiche ne peut pas être enregistrée en l\'état');
      if (b) zoneErreurs.appendChild(b);
    }
    majErreurs();

    var form = el('form', { class: 'admin-form', novalidate: true });
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    vue.appendChild(form);

    function texte(champ, nom, options) {
      options = options || {};
      var idc = 'champ-' + champ;
      var attrs = { id: idc, 'data-cle': idc, maxlength: options.max || null };
      var input = options.long ? el('textarea', attrs) : el('input', Object.assign({ type: 'text' }, attrs));
      input.value = fiche[champ] || '';
      input.addEventListener('input', function () {
        var v = input.value;
        if (v.trim()) fiche[champ] = v; else if (options.requis) fiche[champ] = ''; else delete fiche[champ];
        if (champ === 'titre') vue.querySelector('h1').textContent = v || id;
        maj(false);
      });
      return el('div', { class: 'admin-champ' }, [
        el('label', { for: idc }, nom), options.aide ? el('p', { class: 'admin-aide', id: idc + '-aide' }, options.aide) : null, input
      ]);
    }

    function cases(champ, nom, listeNom, options) {
      options = options || {};
      var groupe = el('fieldset', { class: 'admin-cases' }, [el('legend', null, nom)]);
      valeursDe(listeNom).filter(options.filtre || function () { return true; }).forEach(function (v) {
        var idc = 'champ-' + champ + '-' + v.id;
        var c = el('input', { type: 'checkbox', id: idc, 'data-cle': idc, checked: (fiche[champ] || []).indexOf(v.id) >= 0 ? true : null });
        c.addEventListener('change', function () {
          var l = (fiche[champ] || []).slice();
          if (c.checked && l.indexOf(v.id) < 0) l.push(v.id);
          if (!c.checked) l = l.filter(function (x) { return x !== v.id; });
          if (l.length || options.requis) fiche[champ] = l; else delete fiche[champ];
          maj(champ === 'enseignements');
        });
        groupe.appendChild(el('label', { class: 'admin-case', for: idc }, [c, ' ', v.libelle]));
      });
      return groupe;
    }

    function section(titre, contenu, ouverte) {
      return el('details', { class: 'admin-bloc', open: ouverte ? true : null }, [el('summary', null, titre)].concat(contenu));
    }

    // Statut et notes, en premier : ce qu'on fait le plus souvent
    var statut = el('fieldset', { class: 'admin-cases admin-statut' }, [el('legend', null, 'Statut')]);
    valeursDe('statuts').forEach(function (s) {
      var idc = 'champ-statut-' + s.id;
      var r = el('input', { type: 'radio', name: 'statut', id: idc, 'data-cle': idc, checked: fiche.statut === s.id ? true : null });
      r.addEventListener('change', function () { if (r.checked) { fiche.statut = s.id; maj(false); } });
      statut.appendChild(el('label', { class: 'admin-case', for: idc }, [r, ' ', s.libelle]));
    });

    var notes = el('div', { class: 'admin-notes' });
    (fiche.notes || []).forEach(function (n, i) {
      var idc = 'note-' + i;
      var ta = el('textarea', { id: idc, 'data-cle': idc, rows: 3 });
      ta.value = n.texte || '';
      ta.addEventListener('input', function () { n.texte = ta.value; maj(false); });
      notes.appendChild(el('div', { class: 'admin-note' }, [
        el('label', { for: idc }, 'Note' + (n.date ? ' du ' + n.date.split('-').reverse().join('/') : '')),
        ta,
        bouton('Retirer cette note', function () {
          fiche.notes.splice(i, 1);
          if (!fiche.notes.length) delete fiche.notes;
          maj(true);
        }, { cle: 'retirer-note-' + i })
      ]));
    });
    notes.appendChild(bouton('Ajouter une note', function () {
      fiche.notes = (fiche.notes || []).concat([{ date: aujourdhui(), texte: '' }]);
      maj(false);
      rendre('note-' + (fiche.notes.length - 1));
    }, { cle: 'ajouter-note' }));

    form.appendChild(section('Statut et notes personnelles', [
      statut,
      el('p', { class: 'admin-aide' }, 'Les notes ne s\'affichent que dans l\'admin, mais elles sont lisibles dans le dépôt public : jamais de mot de passe, d\'identifiant ni de nom d\'élève.'),
      notes
    ], true));

    form.appendChild(section('Titre et textes', [
      texte('titre', 'Titre', { requis: true, max: 140 }),
      texte('accroche', 'Accroche (une phrase)', { max: 200 }),
      texte('resume', 'Résumé (une ou deux phrases, montrées dans les listes)', { long: true, requis: true, max: 400 }),
      texte('presentation', 'Présentation (texte de la fiche complète)', { long: true, max: 4000, aide: 'Mise en forme permise : `code`, **gras**, retours à la ligne.' }),
      texte('objectif', 'Objectif (ce que l\'élève apprend ou fait)', { long: true, max: 600 }),
      texte('duree', 'Durée indicative (« 1 h 30 », « 2 séances »)', { max: 60 })
    ], true));

    // Étiquettes : mots-clés
    var idMots = 'champ-mots-cles';
    var mots = el('textarea', { id: idMots, 'data-cle': idMots, rows: 2, 'aria-describedby': idMots + '-aide' });
    mots.value = (fiche.mots_cles || []).join(', ');
    mots.addEventListener('input', function () {
      var l = mots.value.split(',').map(function (x) { return x.trim(); }).filter(Boolean);
      var uniques = l.filter(function (x, i) { return l.indexOf(x) === i; });
      if (uniques.length) fiche.mots_cles = uniques; else delete fiche.mots_cles;
      maj(false);
    });

    var origine = el('select', { id: 'champ-origine', 'data-cle': 'champ-origine' }, valeursDe('origines').map(function (o) {
      return el('option', { value: o.id, selected: fiche.origine === o.id ? true : null }, o.libelle);
    }));
    origine.addEventListener('change', function () { fiche.origine = origine.value; maj(false); });

    form.appendChild(section('Classements et étiquettes', [
      cases('enseignements', 'Enseignements', 'enseignements', { requis: true }),
      cases('niveaux', 'Niveaux', 'niveaux', { requis: true }),
      cases('types', 'Types pédagogiques', 'types', { requis: true }),
      cases('usages', 'Usages et prérequis', 'usages', { requis: true }),
      cases('langages', 'Langages', 'langages'),
      el('div', { class: 'admin-champ' }, [el('label', { for: 'champ-origine' }, 'Origine'), origine]),
      el('div', { class: 'admin-champ' }, [el('label', { for: idMots }, 'Mots-clés'),
        el('p', { class: 'admin-aide', id: idMots + '-aide' }, 'Séparés par des virgules. Ils servent à la recherche.'), mots])
    ]));

    form.appendChild(section('Programme officiel', [blocProgramme(fiche, maj)]));
    form.appendChild(section('Documents et visibilité', [blocDocuments(fiche, maj, id)], true));

    // Les autres champs : gardés tels quels
    var montres = ['$schema', 'id', 'titre', 'accroche', 'resume', 'presentation', 'objectif', 'duree', 'statut', 'notes', 'mots_cles',
      'enseignements', 'niveaux', 'types', 'usages', 'langages', 'origine', 'programme', 'documents', 'dates'];
    var autres = Object.keys(fiche).filter(function (k) { return montres.indexOf(k) < 0; });
    if (autres.length) {
      form.appendChild(section('Autres champs (gardés tels quels)', [
        el('p', { class: 'admin-aide' }, 'Auteurs, licence, crédits, notions, critères… ne se modifient pas encore ici : ils sont gardés tels quels à l\'enregistrement.'),
        el('dl', { class: 'admin-autres' }, autres.reduce(function (a, k) {
          return a.concat([el('dt', null, k), el('dd', null, el('code', null, JSON.stringify(fiche[k])))]);
        }, []))
      ]));
    }

    if (modifie(chemin)) {
      vue.appendChild(el('p', { class: 'admin-actions' }, bouton('Annuler les changements de cette fiche', function () {
        f.courant = D.copie(f.base.objet);
        change(true);
        annoncer('Changements de la fiche annulés.');
      }, { cle: 'annuler-fiche' })));
    }
  }

  function blocProgramme(fiche, maj) {
    var bloc = el('div');
    var noeuds = etat.refs.noeuds;
    var l = el('ul', { class: 'admin-ordre' });
    (fiche.programme || []).forEach(function (nid, i) {
      var n = noeuds[nid];
      l.appendChild(el('li', null, [
        el('span', { class: 'admin-ordre-nom' }, [n ? (n.niveau === 'contenu' ? noeuds[n.parent].intitule + ' › ' : '') + n.intitule : nid, ' ', el('code', null, nid)]),
        bouton('Retirer', function () { fiche.programme.splice(i, 1); maj(true); }, { aria: 'Retirer « ' + (n ? n.intitule : nid) + ' »', cle: 'prog-retirer-' + i })
      ]));
    });
    if (!(fiche.programme || []).length) l.appendChild(el('li', { class: 'vide' }, 'Aucun thème du programme.'));
    bloc.appendChild(l);
    var ens = fiche.enseignements || [];
    var sel = el('select', { id: 'ajout-programme', 'data-cle': 'ajout-programme' }, [el('option', { value: '' }, 'Choisir un thème ou un contenu…')]);
    Object.keys(noeuds).forEach(function (nid) {
      var n = noeuds[nid];
      if (n.niveau !== 'programme' || (ens.length && ens.indexOf(n.enseignement) < 0)) return;
      var g = el('optgroup', { label: n.intitule });
      n.enfants.forEach(function (t) {
        if ((fiche.programme || []).indexOf(t) < 0) g.appendChild(el('option', { value: t }, noeuds[t].intitule));
        noeuds[t].enfants.forEach(function (c) {
          if ((fiche.programme || []).indexOf(c) < 0) g.appendChild(el('option', { value: c }, '   ' + noeuds[c].intitule));
        });
      });
      sel.appendChild(g);
    });
    sel.addEventListener('change', function () {
      if (!sel.value) return;
      fiche.programme = (fiche.programme || []).concat([sel.value]);
      maj(true);
    });
    bloc.appendChild(el('div', { class: 'admin-champ' }, [el('label', { for: 'ajout-programme' }, 'Ajouter (programmes des enseignements cochés)'), sel]));
    return bloc;
  }

  function blocDocuments(fiche, maj, id) {
    var bloc = el('div');
    var docs = fiche.documents || (fiche.documents = []);
    var v = visibilite(fiche);
    var bc = badgeCache(v);
    bloc.appendChild(el('p', { class: 'admin-aide' }, [
      'La ressource apparaît pour un public si au moins un de ses documents lui est visible. Un document caché reste lisible dans le dépôt public. ',
      bc ? el('strong', null, 'En ce moment : ' + bc + '.') : 'En ce moment : visible de tous.'
    ]));
    bloc.appendChild(el('p', { class: 'admin-actions' }, [
      bouton('Tout cacher pour l\'extérieur', function () { docs.forEach(function (d) { d.visible = d.visible || {}; d.visible.exterieur = false; }); maj(true); }, { cle: 'tout-cacher-exterieur' }),
      bouton('Tout cacher pour les élèves', function () { docs.forEach(function (d) { d.visible = d.visible || {}; d.visible.eleve = false; }); maj(true); }, { cle: 'tout-cacher-eleve' }),
      bouton('Tout montrer', function () { docs.forEach(function (d) { d.visible = { exterieur: true, eleve: true }; }); maj(true); }, { cle: 'tout-montrer' })
    ]));
    var roles = valeursDe('roles');
    var l = el('ol', { class: 'admin-docs' });
    docs.forEach(function (d, i) {
      var nom = d.titre || libelle('roles', d.role);
      var p = 'doc-' + i + '-';
      var titre = el('input', { type: 'text', id: p + 'titre', 'data-cle': p + 'titre', maxlength: 140 });
      titre.value = d.titre || '';
      titre.placeholder = libelle('roles', d.role);
      titre.addEventListener('input', function () { if (titre.value.trim()) d.titre = titre.value; else delete d.titre; maj(false); });
      var role = el('select', { id: p + 'role', 'data-cle': p + 'role' }, roles.map(function (r) {
        return el('option', { value: r.id, selected: r.id === d.role ? true : null }, r.libelle);
      }));
      role.addEventListener('change', function () { d.role = role.value; maj(false); });
      var adresse = el('input', { type: 'text', id: p + 'adresse', 'data-cle': p + 'adresse', inputmode: 'url', autocomplete: 'off', spellcheck: 'false' });
      adresse.value = d.url || d.fichier || '';
      adresse.addEventListener('input', function () {
        var a = adresse.value.trim();
        delete d.url; delete d.fichier;
        if (/^https?:\/\//i.test(a)) d.url = a; else if (a) d.fichier = a;
        maj(false);
      });
      var principal = el('input', { type: 'radio', name: 'principal', id: p + 'principal', 'data-cle': p + 'principal', checked: d.principal === true ? true : null });
      principal.addEventListener('change', function () {
        docs.forEach(function (x) { if (x.principal) delete x.principal; });
        d.principal = true;
        maj(true);
      });
      function caseVisible(public_, nomPublic) {
        var c = el('input', { type: 'checkbox', id: p + public_, 'data-cle': p + public_, checked: d.visible && d.visible[public_] === true ? true : null });
        c.addEventListener('change', function () {
          d.visible = d.visible || { exterieur: true, eleve: true };
          d.visible[public_] = c.checked;
          maj(true);
        });
        return el('label', { class: 'admin-case', for: p + public_ }, [c, ' Visible pour ' + nomPublic]);
      }
      var cache = badgeCache({ exterieur: !d.visible || d.visible.exterieur !== false, eleve: !d.visible || d.visible.eleve !== false });
      l.appendChild(el('li', { class: 'admin-doc' }, [
        el('p', { class: 'admin-doc-tete' }, [el('strong', null, nom), d.principal ? el('span', { class: 'badge' }, 'principal') : null, cache ? el('span', { class: 'badge cache' }, cache) : null]),
        el('div', { class: 'admin-champ' }, [el('label', { for: p + 'titre' }, 'Libellé'), titre]),
        el('div', { class: 'admin-champ' }, [el('label', { for: p + 'role' }, 'Rôle'), role]),
        el('div', { class: 'admin-champ' }, [el('label', { for: p + 'adresse' }, 'Adresse (https://…) ou fichier du site (snt/fichiers/…)'), adresse]),
        el('p', { class: 'admin-cases-ligne' }, [
          el('label', { class: 'admin-case', for: p + 'principal' }, [principal, ' Document principal (ouvert par le titre)']),
          caseVisible('exterieur', 'l\'extérieur'), caseVisible('eleve', 'les élèves')
        ]),
        el('p', { class: 'admin-actions' }, [
          bouton('Monter', function () { docs.splice(i - 1, 0, docs.splice(i, 1)[0]); maj(false); rendre('doc-' + (i - 1) + '-monter'); },
            { aria: 'Monter « ' + nom + ' »', cle: p + 'monter', inactif: i === 0 }),
          bouton('Descendre', function () { docs.splice(i + 1, 0, docs.splice(i, 1)[0]); maj(false); rendre('doc-' + (i + 1) + '-descendre'); },
            { aria: 'Descendre « ' + nom + ' »', cle: p + 'descendre', inactif: i === docs.length - 1 }),
          bouton('Retirer', function () {
            if (!confirm('Retirer le document « ' + nom + ' » de la fiche ? (Le fichier lui-même n\'est pas supprimé.)')) return;
            docs.splice(i, 1); maj(true);
          }, { aria: 'Retirer « ' + nom + ' »', cle: p + 'retirer' })
        ])
      ]));
    });
    bloc.appendChild(l);
    bloc.appendChild(bouton('Ajouter un document', function () {
      docs.push({ role: 'complement', url: 'https://', visible: { exterieur: true, eleve: true } });
      maj(false);
      rendre('doc-' + (docs.length - 1) + '-adresse');
    }, { cle: 'ajouter-document' }));
    return bloc;
  }

  /* ── Vue : composer les onglets (la vitrine) ──────────────────── */

  function vueOnglets(arg) {
    var f = etat.fichiers[VITRINE];
    if (!f || !f.base) {
      vue.appendChild(el('p', { class: 'statut', role: 'status' }, 'Ouverture de la vitrine…'));
      ouvrir(VITRINE).then(function () { rendre(); }, function (e) {
        etat.message = { niveau: 'erreur', texte: 'La vitrine (donnees/vitrine.json) n\'a pas pu être lue : ' + e.message };
        aller('ressources');
      });
      return;
    }
    var v = f.courant;
    var ids = v.rubriques.map(function (r) { return r.id; });
    var choisi = arg === 'a-la-une' ? 'a-la-une' : (ids.indexOf(arg) >= 0 ? arg : ids[0]);
    function maj(redessiner, cle) { change(false); if (redessiner) rendre(cle); else majErreurs(); }

    vue.appendChild(el('h1', { id: 'contenu' }, 'Onglets du site'));
    vue.appendChild(el('p', { class: 'admin-aide' }, 'Choisir ce que montre chaque onglet : les sections, leur ordre et leurs titres, et dans chacune les ressources mises en avant, dans l\'ordre. Le reste de la bibliothèque reste consultable dans l\'onglet Bibliothèque.'));
    vue.appendChild(el('nav', { class: 'admin-sous-onglets', 'aria-label': 'Onglets du site' }, el('ul', null,
      v.rubriques.map(function (r) {
        return el('li', null, el('a', { href: '#/onglets/' + r.id, 'aria-current': choisi === r.id ? 'page' : null }, r.court || r.titre));
      }).concat([el('li', null, el('a', { href: '#/onglets/a-la-une', 'aria-current': choisi === 'a-la-une' ? 'page' : null }, 'À la une (accueil)'))]))));

    var zoneErreurs = el('div', { 'aria-live': 'polite' });
    vue.appendChild(zoneErreurs);
    function majErreurs() {
      O.vider(zoneErreurs);
      var b = blocErreurs(valider(VITRINE).map(function (e) { return { champ: e[0], message: e[1] }; }), 'La vitrine ne peut pas être enregistrée en l\'état');
      if (b) zoneErreurs.appendChild(b);
    }
    majErreurs();

    if (choisi === 'a-la-une') return vueALaUne(v, maj);
    var rub = v.rubriques[ids.indexOf(choisi)];

    var tete = el('div', { class: 'admin-bloc-plat' });
    function champRub(cle, nom, long, max) {
      var idc = 'rub-' + cle;
      var input = long ? el('textarea', { id: idc, 'data-cle': idc, rows: 4, maxlength: max }) : el('input', { type: 'text', id: idc, 'data-cle': idc, maxlength: max });
      input.value = rub[cle] || '';
      input.addEventListener('input', function () {
        if (input.value.trim()) rub[cle] = input.value; else if (cle === 'titre') rub[cle] = ''; else delete rub[cle];
        maj(false);
      });
      tete.appendChild(el('div', { class: 'admin-champ' }, [el('label', { for: idc }, nom), input]));
    }
    champRub('titre', 'Titre de l\'onglet', false, 80);
    champRub('court', 'Nom court (menu)', false, 30);
    champRub('niveau', 'Ligne sous le titre (« Première, spécialité »)', false, 60);
    champRub('presentation', 'Texte d\'introduction', true, 1000);
    vue.appendChild(tete);

    vue.appendChild(el('p', { class: 'admin-actions' }, [
      bouton('Voir l\'aperçu de cet onglet', function () { montrerApercu(rub.id); }, { classe: 'principal', cle: 'apercu' })
    ]));
    var cadre = el('div', { id: 'admin-apercu' });
    vue.appendChild(cadre);

    var noeuds = etat.refs.noeuds;
    var prog = rub.programme ? noeuds[rub.programme] : null;
    vue.appendChild(el('h2', null, 'Sections'));
    var sections = el('ol', { class: 'admin-sections' });
    rub.sections.forEach(function (s, j) {
      var n = s.programme ? noeuds[s.programme] : null;
      var nom = n ? n.intitule : s.titre;
      var p = 'sec-' + j + '-';
      var carte = el('li', { class: 'admin-section' });
      var tete = el('div', { class: 'admin-section-tete' });
      if (n) {
        tete.appendChild(el('p', null, [el('strong', null, nom), el('br'), el('span', { class: 'admin-aide' }, 'Thème du programme : son titre est celui du texte officiel.')]));
      } else {
        var t = el('input', { type: 'text', id: p + 'titre', 'data-cle': p + 'titre', maxlength: 120 });
        t.value = s.titre || '';
        t.addEventListener('input', function () { s.titre = t.value; maj(false); });
        tete.appendChild(el('div', { class: 'admin-champ' }, [el('label', { for: p + 'titre' }, 'Titre de la section'), t]));
        tete.appendChild(el('p', { class: 'admin-aide' }, ['Adresse : ', el('code', null, '…/' + rub.id + '/#' + s.id)]));
      }
      tete.appendChild(el('p', { class: 'admin-actions' }, [
        bouton('Monter', function () { rub.sections.splice(j - 1, 0, rub.sections.splice(j, 1)[0]); maj(true, 'sec-' + (j - 1) + '-monter'); },
          { aria: 'Monter la section « ' + nom + ' »', cle: p + 'monter', inactif: j === 0 }),
        bouton('Descendre', function () { rub.sections.splice(j + 1, 0, rub.sections.splice(j, 1)[0]); maj(true, 'sec-' + (j + 1) + '-descendre'); },
          { aria: 'Descendre la section « ' + nom + ' »', cle: p + 'descendre', inactif: j === rub.sections.length - 1 }),
        bouton('Retirer la section', function () {
          if (!confirm('Retirer la section « ' + nom + ' » de l\'onglet ? (Les ressources restent dans la bibliothèque.)')) return;
          rub.sections.splice(j, 1); maj(true);
        }, { aria: 'Retirer la section « ' + nom + ' »', cle: p + 'retirer' })
      ]));
      carte.appendChild(tete);
      carte.appendChild(listeRessources(s.ressources, p + 'res-', maj, s.programme || null));

      (s.sous_sections || []).forEach(function (ss, k) {
        var c = ss.programme ? noeuds[ss.programme] : null;
        var nomSs = c ? c.intitule : ss.titre;
        var q = p + 'ss-' + k + '-';
        var sous = el('div', { class: 'admin-sous-section' });
        if (c) sous.appendChild(el('p', null, [el('strong', null, nomSs), ' ', el('span', { class: 'admin-aide' }, '(contenu du programme)')]));
        else {
          var ts = el('input', { type: 'text', id: q + 'titre', 'data-cle': q + 'titre', maxlength: 120 });
          ts.value = ss.titre || '';
          ts.addEventListener('input', function () { ss.titre = ts.value; maj(false); });
          sous.appendChild(el('div', { class: 'admin-champ' }, [el('label', { for: q + 'titre' }, 'Sous-titre'), ts]));
        }
        sous.appendChild(el('p', { class: 'admin-actions' }, [
          bouton('Monter', function () { s.sous_sections.splice(k - 1, 0, s.sous_sections.splice(k, 1)[0]); maj(true, p + 'ss-' + (k - 1) + '-monter'); },
            { aria: 'Monter « ' + nomSs + ' »', cle: q + 'monter', inactif: k === 0 }),
          bouton('Descendre', function () { s.sous_sections.splice(k + 1, 0, s.sous_sections.splice(k, 1)[0]); maj(true, p + 'ss-' + (k + 1) + '-descendre'); },
            { aria: 'Descendre « ' + nomSs + ' »', cle: q + 'descendre', inactif: k === s.sous_sections.length - 1 }),
          bouton('Retirer', function () {
            if (!confirm('Retirer « ' + nomSs + ' » ?')) return;
            s.sous_sections.splice(k, 1);
            if (!s.sous_sections.length) delete s.sous_sections;
            maj(true);
          }, { aria: 'Retirer « ' + nomSs + ' »', cle: q + 'retirer' })
        ]));
        sous.appendChild(listeRessources(ss.ressources, q + 'res-', maj, ss.programme || s.programme || null));
        carte.appendChild(sous);
      });

      // Ajouter une sous-section : un contenu du thème, ou un sous-titre libre
      var ajouts = el('p', { class: 'admin-actions' });
      if (n) {
        var pris = (s.sous_sections || []).map(function (x) { return x.programme; });
        var libres = n.enfants.filter(function (cid) { return pris.indexOf(cid) < 0; });
        if (libres.length) {
          var sel = el('select', { id: p + 'ajout-contenu', 'data-cle': p + 'ajout-contenu' }, [el('option', { value: '' }, 'Ajouter un contenu du programme…')]
            .concat(libres.map(function (cid) { return el('option', { value: cid }, noeuds[cid].intitule); })));
          sel.addEventListener('change', function () {
            if (!sel.value) return;
            s.sous_sections = (s.sous_sections || []).concat([{ programme: sel.value, ressources: [] }]);
            maj(true, p + 'ajout-contenu');
          });
          ajouts.appendChild(el('label', { class: 'invisible', for: p + 'ajout-contenu' }, 'Ajouter un contenu du programme à « ' + nom + ' »'));
          ajouts.appendChild(sel);
        }
      }
      ajouts.appendChild(bouton('Ajouter un sous-titre', function () {
        var titre = prompt('Titre du sous-titre (par exemple « Pour aller plus loin ») :');
        if (!titre || !titre.trim()) return;
        s.sous_sections = (s.sous_sections || []).concat([{ id: identifiantLibre(rub, titre), titre: titre.trim(), ressources: [] }]);
        maj(true);
      }, { cle: p + 'ajout-sous-titre', aria: 'Ajouter un sous-titre à « ' + nom + ' »' }));
      carte.appendChild(ajouts);
      sections.appendChild(carte);
    });
    vue.appendChild(sections);

    var ajout = el('p', { class: 'admin-actions' });
    if (prog) {
      var presents = rub.sections.map(function (s) { return s.programme; });
      var manquants = prog.enfants.filter(function (t) { return presents.indexOf(t) < 0; });
      if (manquants.length) {
        var selT = el('select', { id: 'ajout-theme', 'data-cle': 'ajout-theme' }, [el('option', { value: '' }, 'Ajouter un thème du programme…')]
          .concat(manquants.map(function (t) { return el('option', { value: t }, noeuds[t].intitule); })));
        selT.addEventListener('change', function () {
          if (!selT.value) return;
          rub.sections.push({ programme: selT.value, ressources: [] });
          maj(true, 'ajout-theme');
        });
        ajout.appendChild(el('label', { class: 'invisible', for: 'ajout-theme' }, 'Ajouter un thème du programme'));
        ajout.appendChild(selT);
      }
    }
    ajout.appendChild(bouton('Ajouter une section libre', function () {
      var titre = prompt('Titre de la section (par exemple « Préparer le bac ») :');
      if (!titre || !titre.trim()) return;
      rub.sections.push({ id: identifiantLibre(rub, titre), titre: titre.trim(), ressources: [] });
      maj(true);
    }, { cle: 'ajout-section-libre' }));
    vue.appendChild(ajout);
  }

  /* Un identifiant de section libre, unique dans la rubrique (il sert d'ancre : …/snt/#preparer-le-bac) */
  function identifiantLibre(rub, titre) {
    var pris = {};
    rub.sections.forEach(function (s) {
      if (s.id) pris[s.id] = true;
      (s.sous_sections || []).forEach(function (ss) { if (ss.id) pris[ss.id] = true; });
    });
    var base = O.slug(titre).slice(0, 50).replace(/-+$/, '') || 'section', id = base, k = 2;
    while (pris[id]) id = base + '-' + (k++);
    return id;
  }

  /* La liste ordonnée des ressources d'une section : flèches, glisser-déposer, cases à cocher */
  function listeRessources(ids, p, maj, noeud) {
    var bloc = el('div', { class: 'admin-res' });
    var l = el('ol', { class: 'admin-ordre' });
    var glisse = null;
    ids.forEach(function (rid, i) {
      var f = ficheCourante(rid);
      var nom = f ? f.titre : rid;
      var v = f ? visibilite(f) : { exterieur: false, eleve: false };
      var li = el('li', { draggable: 'true', 'data-rang': String(i) }, [
        el('span', { class: 'admin-poignee', 'aria-hidden': 'true', title: 'Glisser pour déplacer' }, '⋮⋮'),
        el('span', { class: 'admin-ordre-nom' }, [nom, ' ', el('code', null, rid),
          !f ? el('span', { class: 'badge cache' }, 'fiche absente') : (!v.exterieur ? el('span', { class: 'badge cache' }, 'cachée de l\'extérieur : n\'apparaîtra pas') : null)]),
        el('span', { class: 'admin-actions' }, [
          bouton('↑', function () { ids.splice(i - 1, 0, ids.splice(i, 1)[0]); maj(true, p + (i - 1) + '-monter'); },
            { aria: 'Monter « ' + nom + ' »', cle: p + i + '-monter', inactif: i === 0, classe: 'petit' }),
          bouton('↓', function () { ids.splice(i + 1, 0, ids.splice(i, 1)[0]); maj(true, p + (i + 1) + '-descendre'); },
            { aria: 'Descendre « ' + nom + ' »', cle: p + i + '-descendre', inactif: i === ids.length - 1, classe: 'petit' }),
          bouton('Retirer', function () { ids.splice(i, 1); maj(true, p + 'choisir'); },
            { aria: 'Retirer « ' + nom + ' » de cette section', cle: p + i + '-retirer', classe: 'petit' })
        ])
      ]);
      li.addEventListener('dragstart', function (e) { glisse = i; e.dataTransfer.effectAllowed = 'move'; try { e.dataTransfer.setData('text/plain', rid); } catch (x) { /* rien */ } li.classList.add('glisse'); });
      li.addEventListener('dragend', function () { li.classList.remove('glisse'); });
      li.addEventListener('dragover', function (e) { if (glisse !== null) { e.preventDefault(); li.classList.add('survol'); } });
      li.addEventListener('dragleave', function () { li.classList.remove('survol'); });
      li.addEventListener('drop', function (e) {
        e.preventDefault();
        if (glisse === null || glisse === i) return;
        ids.splice(i, 0, ids.splice(glisse, 1)[0]);
        glisse = null;
        maj(true);
      });
      l.appendChild(li);
    });
    if (!ids.length) l.appendChild(el('li', { class: 'vide' }, 'Aucune ressource mise en avant ici.'));
    bloc.appendChild(l);

    // Choisir par cases à cocher, avec une recherche ; celles du thème d'abord
    var choisir = el('details', { class: 'admin-choisir' }, [el('summary', { 'data-cle': p + 'choisir' }, 'Choisir les ressources (cases à cocher)')]);
    var q = el('input', { type: 'search', class: 'recherche', id: p + 'q', 'data-cle': p + 'q', placeholder: 'Chercher une ressource', autocomplete: 'off' });
    var cases = el('ul', { class: 'admin-choix' });
    choisir.appendChild(el('label', { class: 'invisible', for: p + 'q' }, 'Chercher une ressource à ajouter'));
    choisir.appendChild(q);
    choisir.appendChild(cases);
    function proche(f) {
      return noeud && (f.programme || []).some(function (n) { return n === noeud || n.indexOf(noeud + '.') === 0 || noeud.indexOf(n + '.') === 0; });
    }
    function majCases() {
      O.vider(cases);
      var mots = O.sansAccents(q.value.trim()).toLowerCase().split(/\s+/).filter(Boolean);
      var toutes = etat.complete.ressources.map(function (r) { return ficheCourante(r.id); });
      toutes.sort(function (a, b) { return (proche(b) ? 1 : 0) - (proche(a) ? 1 : 0) || a.titre.localeCompare(b.titre, 'fr'); });
      var n = 0;
      toutes.forEach(function (f) {
        if (mots.length) {
          var t = O.sansAccents(f.titre + ' ' + f.id + ' ' + (f.mots_cles || []).join(' ')).toLowerCase();
          if (!mots.every(function (m) { return t.indexOf(m) >= 0; })) return;
        } else if (!proche(f) && ids.indexOf(f.id) < 0) return;
        if (n++ >= 40) return;
        var idc = p + 'case-' + f.id;
        var c = el('input', { type: 'checkbox', id: idc, 'data-cle': idc, checked: ids.indexOf(f.id) >= 0 ? true : null });
        c.addEventListener('change', function () {
          var k = ids.indexOf(f.id);
          if (c.checked && k < 0) ids.push(f.id);
          if (!c.checked && k >= 0) ids.splice(k, 1);
          maj(true, idc);
        });
        cases.appendChild(el('li', null, el('label', { class: 'admin-case', for: idc }, [c, ' ', f.titre, proche(f) ? el('span', { class: 'badge' }, 'du thème') : null])));
      });
      if (!n) cases.appendChild(el('li', { class: 'vide' }, mots.length ? 'Aucune ressource ne correspond.' : 'Taper un mot pour chercher dans toute la bibliothèque.'));
      else if (n > 40) cases.appendChild(el('li', { class: 'vide' }, (n - 40) + ' autres : préciser la recherche.'));
    }
    q.value = etat.recherches[p] || '';
    q.addEventListener('input', function () { etat.recherches[p] = q.value; majCases(); });
    choisir.addEventListener('toggle', function () { if (choisir.open) majCases(); });
    // rouvrir après un changement fait depuis la liste de cases (la vue vient d'être redessinée)
    var actif = etat.focusEnCours;
    if (actif && (actif.indexOf(p + 'case-') === 0 || actif === p + 'q')) { choisir.open = true; majCases(); }
    bloc.appendChild(choisir);
    return bloc;
  }

  function vueALaUne(v, maj) {
    vue.appendChild(el('p', { class: 'admin-aide' }, 'Les ressources mises en avant sur l\'accueil, dans l\'ordre, avec une étiquette facultative (« Ressource du mois ») et des dates facultatives.'));
    var l = el('ol', { class: 'admin-ordre admin-une' });
    v.a_la_une.forEach(function (u, i) {
      var f = ficheCourante(u.ressource);
      var nom = f ? f.titre : u.ressource;
      var idc = 'une-' + i + '-etiquette';
      var et = el('input', { type: 'text', id: idc, 'data-cle': idc, maxlength: 40, placeholder: 'Étiquette (facultative)' });
      et.value = u.etiquette || '';
      et.addEventListener('input', function () { if (et.value.trim()) u.etiquette = et.value; else delete u.etiquette; maj(false); });
      function date(cle, nomD) {
        var idd = 'une-' + i + '-' + cle;
        var d = el('input', { type: 'date', id: idd, 'data-cle': idd });
        d.value = u[cle] || '';
        d.addEventListener('change', function () { if (d.value) u[cle] = d.value; else delete u[cle]; maj(false); });
        return el('span', { class: 'admin-champ-ligne' }, [el('label', { for: idd }, nomD), d]);
      }
      l.appendChild(el('li', null, [
        el('span', { class: 'admin-ordre-nom' }, [nom, ' ', el('code', null, u.ressource)]),
        el('span', { class: 'admin-champ-ligne' }, [el('label', { for: idc }, 'Étiquette'), et]),
        date('debut', 'Du'), date('fin', 'au'),
        el('span', { class: 'admin-actions' }, [
          bouton('↑', function () { v.a_la_une.splice(i - 1, 0, v.a_la_une.splice(i, 1)[0]); maj(true, 'une-' + (i - 1) + '-monter'); },
            { aria: 'Monter « ' + nom + ' »', cle: 'une-' + i + '-monter', inactif: i === 0, classe: 'petit' }),
          bouton('↓', function () { v.a_la_une.splice(i + 1, 0, v.a_la_une.splice(i, 1)[0]); maj(true, 'une-' + (i + 1) + '-descendre'); },
            { aria: 'Descendre « ' + nom + ' »', cle: 'une-' + i + '-descendre', inactif: i === v.a_la_une.length - 1, classe: 'petit' }),
          bouton('Retirer', function () { v.a_la_une.splice(i, 1); maj(true); }, { aria: 'Retirer « ' + nom + ' » de la une', cle: 'une-' + i + '-retirer', classe: 'petit' })
        ])
      ]));
    });
    vue.appendChild(l);
    var ids = v.a_la_une.map(function (u) { return u.ressource; });
    var proxy = ids.slice();
    var bloc = listeRessources(proxy, 'une-choix-', function (redessiner, cle) {
      // les cases ajoutent ou retirent des ressources de la une
      v.a_la_une = proxy.map(function (rid) {
        return v.a_la_une.filter(function (u) { return u.ressource === rid; })[0] || { ressource: rid };
      });
      maj(redessiner, cle);
    }, null);
    var choisir = bloc.querySelector('.admin-choisir');
    if (choisir) vue.appendChild(choisir);
  }

  /* ── L'aperçu : l'onglet dessiné par site.js, dans un cadre ───── */

  function donneesApercu() {
    var ressources = [];
    etat.complete.ressources.forEach(function (r) {
      var p = vuePublique(ficheCourante(r.id));
      if (p) ressources.push(p);
    });
    var v = etat.fichiers[VITRINE] ? etat.fichiers[VITRINE].courant : etat.complete.vitrine;
    return { vitrine: v, ressources: ressources, programmes: etat.complete.referentiels.programmes, valeurs: etat.complete.referentiels.valeurs };
  }

  function montrerApercu(rubId) {
    var cadre = document.getElementById('admin-apercu');
    if (!cadre) return;
    try { sessionStorage.setItem('apercu-admin', JSON.stringify(donneesApercu())); } catch (e) {
      etat.message = { niveau: 'erreur', texte: 'L\'aperçu a besoin du stockage de session du navigateur, qui est bloqué.' };
      rendre();
      return;
    }
    O.vider(cadre);
    var adresse = O.racine + (rubId ? rubId + '/' : '') + (O.surDisque ? 'index.html' : '') + '?apercu';
    var largeurs = [['Téléphone', 360], ['Tablette', 768], ['Ordinateur', 1200]];
    var iframe = el('iframe', { src: adresse, title: 'Aperçu de l\'onglet', class: 'admin-iframe', loading: 'lazy' });
    var choix = el('p', { class: 'admin-actions' }, largeurs.map(function (l) {
      return bouton(l[0], function () { iframe.style.width = Math.min(l[1], cadre.clientWidth) + 'px'; }, { cle: 'apercu-' + l[1] });
    }).concat([bouton('Fermer l\'aperçu', function () { O.vider(cadre); }, { cle: 'apercu-fermer' })]));
    cadre.appendChild(el('div', { class: 'admin-apercu' }, [
      el('p', null, [el('strong', null, 'Aperçu'), ' : l\'onglet tel qu\'il sera, avec les changements en attente (rien n\'est enregistré).']),
      choix, iframe
    ]));
    iframe.focus();
  }

  /* ── Vue : les changements ────────────────────────────────────── */

  function resumeChangements(chemin) {
    var f = etat.fichiers[chemin];
    var a = f.base.objet, b = f.courant;
    var out = [];
    var cles = Object.keys(a).concat(Object.keys(b).filter(function (k) { return !(k in a); }));
    cles.forEach(function (k) {
      if (D.egal(a[k], b[k])) return;
      if (k === 'rubriques' && Array.isArray(a[k]) && Array.isArray(b[k])) {
        b[k].forEach(function (r) {
          var avant = a[k].filter(function (x) { return x.id === r.id; })[0];
          if (!avant) out.push('onglet « ' + r.titre + ' » ajouté');
          else if (!D.egal(avant, r)) out.push('onglet « ' + (r.court || r.titre) + ' » modifié');
        });
        return;
      }
      if (k === 'documents') { out.push('documents (liens, ordre ou visibilité)'); return; }
      if (k === 'notes') { out.push('notes personnelles'); return; }
      if (!(k in b)) { out.push(k + ' : retiré'); return; }
      if (typeof b[k] === 'string' && typeof a[k] === 'string' && b[k].length < 80 && a[k].length < 80) {
        out.push(k + ' : « ' + a[k] + ' » → « ' + b[k] + ' »');
        return;
      }
      out.push(k + (k in a ? ' : modifié' : ' : ajouté'));
    });
    return out;
  }

  function nomFichier(chemin) {
    if (chemin === VITRINE) return 'Onglets du site (vitrine)';
    var id = idDeChemin(chemin);
    var f = id && ficheCourante(id);
    return f ? 'Fiche « ' + f.titre + ' »' : chemin;
  }

  function vueChangements() {
    vue.appendChild(el('h1', { id: 'contenu' }, 'Changements en attente'));
    var liste = enAttente();
    if (!liste.length) {
      vue.appendChild(el('p', null, 'Aucun changement en attente.'));
      return;
    }
    var erreurs = erreursEnAttente();
    var b = blocErreurs(erreurs);
    if (b) vue.appendChild(b);
    vue.appendChild(el('ul', { class: 'admin-changements' }, liste.map(function (c, i) {
      var id = idDeChemin(c);
      return el('li', null, [
        el('p', null, [el('strong', null, nomFichier(c)), ' ', el('code', null, c)]),
        el('ul', null, resumeChangements(c).map(function (x) { return el('li', null, x); })),
        el('p', { class: 'admin-actions' }, [
          id ? el('a', { class: 'btn', href: '#/fiche/' + encodeURIComponent(id) }, 'Ouvrir la fiche') : el('a', { class: 'btn', href: '#/onglets' }, 'Ouvrir les onglets'),
          bouton('Annuler ces changements', function () {
            etat.fichiers[c].courant = D.copie(etat.fichiers[c].base.objet);
            change(true);
            annoncer('Changements annulés : ' + nomFichier(c) + '.');
          }, { cle: 'annuler-' + i })
        ])
      ]);
    })));
    vue.appendChild(el('p', { class: 'admin-actions' }, [
      bouton('Voir l\'aperçu de l\'accueil', function () { montrerApercu(null); }, { cle: 'apercu-accueil' })
    ]));
    vue.appendChild(el('div', { id: 'admin-apercu' }));
    vue.appendChild(el('h2', null, 'Enregistrer'));
    if (jeton()) {
      vue.appendChild(el('p', null, 'Un clic sur « Enregistrer » écrit ces fichiers dans le dépôt GitHub, en un seul commit sur main, à votre nom. Le site en ligne suit en une à deux minutes.'));
      var msg = el('input', { type: 'text', id: 'message-commit', 'data-cle': 'message-commit', maxlength: 120 });
      msg.value = etat.messageCommit || '';
      msg.placeholder = messageParDefaut();
      msg.addEventListener('input', function () { etat.messageCommit = msg.value; });
      vue.appendChild(el('div', { class: 'admin-champ' }, [el('label', { for: 'message-commit' }, 'Description du changement (facultative)'), msg]));
      vue.appendChild(el('p', { class: 'admin-actions' }, [
        bouton(etat.occupe ? 'Enregistrement…' : 'Enregistrer', enregistrer, { classe: 'principal', cle: 'enregistrer-2', inactif: etat.occupe || erreurs.length > 0 }),
        bouton('Télécharger les fichiers à la place', telecharger, { cle: 'telecharger-2', inactif: erreurs.length > 0 })
      ]));
    } else {
      vue.appendChild(el('p', null, ['Sans jeton GitHub, l\'admin ne peut pas écrire dans le dépôt : téléchargez les fichiers modifiés (une archive .zip, avec leurs chemins), puis déposez-les sur GitHub (« Add file », « Upload files », à la racine du dépôt). Ou ',
        el('a', { href: '#/jeton' }, 'enregistrez un jeton'), ' pour enregistrer d\'un clic.']));
      vue.appendChild(el('p', { class: 'admin-actions' }, bouton('Télécharger les fichiers', telecharger, { classe: 'principal', cle: 'telecharger-2', inactif: erreurs.length > 0 })));
    }
    vue.appendChild(el('p', { class: 'admin-actions' }, bouton('Tout annuler', function () {
      if (!confirm('Annuler tous les changements en attente ?')) return;
      liste.forEach(function (c) { etat.fichiers[c].courant = D.copie(etat.fichiers[c].base.objet); });
      change(true);
    }, { cle: 'tout-annuler' })));
  }

  function messageParDefaut() {
    var l = enAttente();
    var fiches = l.map(idDeChemin).filter(Boolean);
    var morceaux = [];
    if (l.indexOf(VITRINE) >= 0) morceaux.push('onglets du site');
    if (fiches.length === 1) {
      var champs = etat.fichiers[cheminFiche(fiches[0])] ? resumeChangements(cheminFiche(fiches[0])).map(function (x) { return x.split(' :')[0]; }) : [];
      morceaux.push('fiche ' + fiches[0] + (champs.length ? ' (' + champs.join(', ') + ')' : ''));
    } else if (fiches.length) morceaux.push(fiches.length + ' fiches');
    var m = morceaux.join(' et ') || 'mise à jour des données';
    return m.charAt(0).toUpperCase() + m.slice(1);
  }


  /* ── Les fichiers à écrire ────────────────────────────────────── */

  function textesAEcrire() {
    var jour = aujourdhui();
    return enAttente().filter(cheminPermis).map(function (c) {
      var f = etat.fichiers[c];
      var objet = D.copie(f.courant);
      if (c !== VITRINE) {
        objet.dates = objet.dates || {};
        objet.dates.modification = jour;
        if (objet.notes) objet.notes = objet.notes.filter(function (n) { return n.texte && n.texte.trim(); });
        if (objet.notes && !objet.notes.length) delete objet.notes;
      }
      return { chemin: c, texte: D.ecrire(objet, f.base.texte), objet: objet };
    });
  }

  /* ── Télécharger (sans jeton) : une archive .zip, sans compression ── */

  var TABLE_CRC = (function () {
    var t = [];
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();

  function crc32(octets) {
    var c = 0xFFFFFFFF;
    for (var i = 0; i < octets.length; i++) c = TABLE_CRC[(c ^ octets[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }

  function zip(fichiers) {
    fichiers.forEach(function (f) { if (!cheminPermis(f.chemin)) throw new Error('chemin refusé : ' + f.chemin); });
    var enc = new TextEncoder();
    var morceaux = [], central = [], decalage = 0;
    function u16(v) { return [v & 0xFF, (v >>> 8) & 0xFF]; }
    function u32(v) { return [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF]; }
    var d = new Date();
    var heure = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
    var jour = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
    fichiers.forEach(function (f) {
      var nom = enc.encode(f.chemin), donnees = enc.encode(f.texte), crc = crc32(donnees);
      var tete = [].concat(u32(0x04034b50), u16(20), u16(0x0800), u16(0), u16(heure), u16(jour), u32(crc),
        u32(donnees.length), u32(donnees.length), u16(nom.length), u16(0));
      morceaux.push(new Uint8Array(tete), nom, donnees);
      central.push(new Uint8Array([].concat(u32(0x02014b50), u16(20), u16(20), u16(0x0800), u16(0), u16(heure), u16(jour), u32(crc),
        u32(donnees.length), u32(donnees.length), u16(nom.length), u16(0), u16(0), u16(0), u16(0), u32(0), u32(decalage))), nom);
      decalage += tete.length + nom.length + donnees.length;
    });
    var tailleCentral = central.reduce(function (n, x) { return n + x.length; }, 0);
    var fin = new Uint8Array([].concat(u32(0x06054b50), u16(0), u16(0), u16(fichiers.length), u16(fichiers.length),
      u32(tailleCentral), u32(decalage), u16(0)));
    return new Blob(morceaux.concat(central, [fin]), { type: 'application/zip' });
  }

  function telecharger() {
    var erreurs = erreursEnAttente();
    if (erreurs.length) { aller('changements'); return; }
    var fichiers = textesAEcrire();
    var nom = 'admin-' + aujourdhui() + '.zip';
    var url = URL.createObjectURL(zip(fichiers));
    var a = el('a', { href: url, download: nom });
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 1000);
    etat.message = {
      niveau: 'info',
      texte: 'Archive ' + nom + ' téléchargée (' + fichiers.length + (fichiers.length > 1 ? ' fichiers' : ' fichier') + '). Pour l\'enregistrer : sur GitHub, « Add file », « Upload files », déposer le contenu de l\'archive à la racine du dépôt (les dossiers donnees/… sont gardés), puis « Commit changes ». Les changements restent ici en attente tant que vous ne les annulez pas.',
      liste: fichiers.map(function (f) { return f.chemin; })
    };
    rendre();
  }

  /* ── Enregistrer (avec le jeton) : un seul commit sur main ────── */

  function encoderTexte(t) {
    var octets = new TextEncoder().encode(t);
    var bin = '';
    for (var i = 0; i < octets.length; i += 0x8000) bin += String.fromCharCode.apply(null, octets.subarray(i, i + 0x8000));
    return btoa(bin);
  }

  function enregistrer() {
    if (etat.occupe) return;
    var erreurs = erreursEnAttente();
    if (erreurs.length) { aller('changements'); return; }
    var fichiers = textesAEcrire();
    var message = '[admin] ' + ((etat.messageCommit || '').trim() || messageParDefaut());
    etat.occupe = true;
    etat.message = { niveau: 'info', texte: 'Enregistrement en cours…' };
    rendre();

    function essai(reste) {
      var tete, arbre;
      return api('GET', '/git/ref/heads/' + BRANCHE).then(function (r) {
        tete = r.object.sha;
        return api('GET', '/git/commits/' + tete);
      }).then(function (c) {
        arbre = c.tree.sha;
        return api('GET', '/git/trees/' + arbre + '?recursive=1');
      }).then(function (t) {
        var shas = {};
        (t.tree || []).forEach(function (x) { shas[x.path] = x.sha; });
        etat.chemins = {};
        (t.tree || []).forEach(function (x) { etat.chemins[x.path] = x.type === 'tree' ? 'dossier' : x.sha; });
        // Conflit : un fichier a changé sur main depuis son ouverture dans l'admin
        var conflits = [];
        return Promise.all(fichiers.map(function (f) {
          var base = etat.fichiers[f.chemin].base;
          if (base.sha) {
            if (shas[f.chemin] !== base.sha) conflits.push(f.chemin);
            return null;
          }
          // ouvert sans jeton : on compare le texte
          if (!shas[f.chemin]) { conflits.push(f.chemin); return null; }
          return api('GET', '/git/blobs/' + shas[f.chemin]).then(function (b) {
            if (decoder64(b.content || '') !== base.texte) conflits.push(f.chemin);
          });
        })).then(function () {
          if (conflits.length) {
            var e = new Error('conflit');
            e.conflits = conflits;
            throw e;
          }
          // Validation une dernière fois, avec l'arbre de main (fichiers du site)
          var restantes = erreursEnAttente();
          if (restantes.length) {
            var ev = new Error('Une erreur reste à corriger avant d\'enregistrer : ' + restantes[0].chemin + ' ' + restantes[0].champ + ' : ' + restantes[0].message);
            throw ev;
          }
          return Promise.all(fichiers.map(function (f) {
            return api('POST', '/git/blobs', { content: encoderTexte(f.texte), encoding: 'base64' });
          }));
        }).then(function (blobs) {
          var refuses = fichiers.filter(function (f) { return !cheminPermis(f.chemin); });
          if (refuses.length) throw new Error('chemin refusé : ' + refuses[0].chemin);
          return api('POST', '/git/trees', {
            base_tree: arbre,
            tree: fichiers.map(function (f, i) { return { path: f.chemin, mode: '100644', type: 'blob', sha: blobs[i].sha }; })
          }).then(function (nouvelArbre) {
            return api('POST', '/git/commits', { message: message, tree: nouvelArbre.sha, parents: [tete] });
          }).then(function (commit) {
            return api('PATCH', '/git/refs/heads/' + BRANCHE, { sha: commit.sha, force: false }).then(function () {
              return { commit: commit, blobs: blobs };
            });
          });
        });
      }).catch(function (e) {
        // main a avancé entre la lecture et l'écriture : on recommence une fois (avec le contrôle des conflits)
        if (!e.conflits && (e.statut === 422 || e.statut === 409) && reste > 0) return essai(reste - 1);
        throw e;
      });
    }

    essai(1).then(function (r) {
      var recents = lireStockage(CLE_RECENTS, {});
      fichiers.forEach(function (f, i) {
        etat.fichiers[f.chemin] = { base: { texte: f.texte, objet: f.objet, sha: r.blobs[i].sha }, courant: D.copie(f.objet) };
        recents[f.chemin] = { texte: f.texte, quand: Date.now() };
        if (f.chemin === VITRINE) etat.complete.vitrine = D.copie(f.objet);
        else {
          var id = idDeChemin(f.chemin);
          var k = etat.complete.ressources.map(function (x) { return x.id; }).indexOf(id);
          if (k >= 0) etat.complete.ressources[k] = D.copie(f.objet);
        }
      });
      ecrireStockage(CLE_RECENTS, recents);
      etat.messageCommit = '';
      etat.occupe = false;
      garderBrouillon();
      etat.message = {
        niveau: 'ok',
        texte: 'Enregistré : ' + fichiers.length + (fichiers.length > 1 ? ' fichiers' : ' fichier') + ', commit ' + r.commit.sha.slice(0, 7)
          + ' (« ' + message + ' »). Le site en ligne suit en une à deux minutes, après la construction de « Publier le site ».',
        actions: [el('a', { class: 'btn', href: 'https://github.com/' + depot() + '/commit/' + r.commit.sha, target: '_blank', rel: 'noopener' }, 'Voir le commit sur GitHub')]
      };
      rendre();
      annoncer('Enregistré.');
    }, function (e) {
      etat.occupe = false;
      if (e.conflits) {
        etat.message = {
          niveau: 'erreur',
          texte: 'Rien n\'a été enregistré : ' + (e.conflits.length > 1 ? 'ces fichiers ont' : 'ce fichier a') + ' changé sur GitHub depuis son ouverture ici (quelqu\'un ou un agent l\'a modifié). Pour ne rien écraser, l\'admin ne l\'écrit pas. Téléchargez d\'abord vos versions si vous voulez les garder, puis rechargez : vos changements sur ces fichiers seront à refaire sur la nouvelle version.',
          liste: e.conflits,
          actions: [
            bouton('Télécharger mes versions', telecharger, { cle: 'conflit-telecharger' }),
            bouton('Recharger ces fichiers depuis GitHub', function () {
              e.conflits.forEach(function (c) { delete etat.fichiers[c]; });
              garderBrouillon();
              etat.message = { niveau: 'info', texte: 'Fichiers rechargés depuis GitHub.' };
              rendre();
            }, { cle: 'conflit-recharger', classe: 'principal' })
          ]
        };
      } else {
        etat.message = { niveau: 'erreur', texte: 'Rien n\'a été enregistré. ' + e.message };
      }
      rendre();
      annoncer('Échec de l\'enregistrement.');
    });
  }

  /* ── Vue : le jeton ───────────────────────────────────────────── */

  function formeJeton(v) { return /^(github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})$/.test(v); }

  function champMdp(id, nom, nouveau) {
    var input = el('input', { type: 'password', id: id, 'data-cle': id, autocomplete: nouveau ? 'new-password' : 'current-password', spellcheck: 'false' });
    return { input: input, bloc: el('div', { class: 'admin-champ' }, [el('label', { for: id }, nom), input]) };
  }

  /* Déverrouiller : le formulaire du mot de passe (vue « Accès » et en tête des autres vues) */
  function blocDeverrouiller(compact) {
    var mdp = champMdp(compact ? 'mdp-porte' : 'mdp', 'Mot de passe administrateur', false);
    var form = el('form', { class: 'admin-porte' + (compact ? ' compact' : '') }, [
      compact ? el('p', null, [el('strong', null, 'Admin verrouillé.'), ' Le mot de passe déverrouille le jeton gardé sur cet appareil, pour enregistrer d\'un clic. Sans lui, tout reste possible en lecture : modifier, voir l\'aperçu, télécharger les fichiers.']) : null,
      mdp.bloc,
      el('p', { class: 'admin-actions' }, [el('button', { type: 'submit', class: 'btn principal', 'data-cle': 'deverrouiller' }, 'Déverrouiller')])
    ]);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = mdp.input.value;
      mdp.input.value = '';
      etat.message = { niveau: 'info', texte: 'Déchiffrement du jeton…' };
      rendre();
      ouvrirCoffre(v).then(function () {
        etat.message = { niveau: 'ok', texte: 'Admin déverrouillé pour cette visite : vos changements peuvent être enregistrés.' };
        return chargerArbre().catch(function (err) { etat.message = { niveau: 'erreur', texte: 'Le jeton ne fonctionne pas : ' + err.message }; });
      }).then(function () { rendre(); }, function (err) {
        etat.message = { niveau: 'erreur', texte: err.message };
        rendre('mdp');
      });
    });
    return form;
  }

  function vueJeton() {
    vue.appendChild(el('h1', { id: 'contenu' }, 'Mot de passe et jeton'));
    var garde = !!coffre(), ouvert = !!jeton();
    vue.appendChild(el('p', null, ouvert
      ? [el('strong', null, 'Admin déverrouillé.'), ' Vos changements peuvent être enregistrés dans le dépôt jusqu\'à la fin de la visite, ou jusqu\'à « Verrouiller ».']
      : garde ? [el('strong', null, 'Admin verrouillé.'), ' Un jeton chiffré est gardé sur cet appareil : le mot de passe administrateur le déverrouille.']
      : [el('strong', null, 'Aucun jeton sur cet appareil.'), ' L\'admin fonctionne en lecture : vous pouvez tout modifier, voir l\'aperçu et télécharger les fichiers modifiés, mais pas les enregistrer d\'un clic.']));
    vue.appendChild(el('div', { class: 'admin-garde' }, [
      el('p', null, el('strong', null, 'Ce que protège le mot de passe.')),
      el('p', null, 'Le mot de passe administrateur protège le jeton GitHub gardé sur cet appareil : le jeton y est chiffré avec lui, jamais écrit en clair. Le mot de passe n\'est gardé nulle part, n\'est envoyé à personne et n\'est jamais écrit dans le dépôt.'),
      el('p', null, 'Il ne rend pas l\'admin secret : la page et tout le dépôt (fiches, notes, documents cachés) sont publics. Un mot de passe oublié se règle en recollant un jeton (« Oublier cet appareil », puis un nouveau jeton et un nouveau mot de passe).')
    ]));
    if (!cryptoPossible()) {
      vue.appendChild(el('div', { class: 'alerte', role: 'alert' }, el('p', null, 'Ce navigateur ne permet pas de chiffrer le jeton (il faut une page en https) : l\'admin reste en lecture.')));
      return;
    }

    if (garde && !ouvert) vue.appendChild(blocDeverrouiller(false));
    if (ouvert) {
      vue.appendChild(el('p', { class: 'admin-actions' }, [
        bouton('Verrouiller', function () {
          verrouiller();
          etat.message = { niveau: 'ok', texte: 'Admin verrouillé : le jeton déchiffré est oublié. Le mot de passe le déverrouillera de nouveau.' };
          rendre();
        }, { classe: 'principal', cle: 'verrouiller' }),
        bouton('Vérifier le jeton', verifierJeton, { cle: 'jeton-verifier' })
      ]));
    }
    if (garde) {
      vue.appendChild(el('p', { class: 'admin-actions' }, bouton('Oublier cet appareil', function () {
        if (!confirm('Effacer le jeton chiffré de cet appareil ? Il faudra recoller un jeton et choisir un mot de passe pour enregistrer de nouveau.')) return;
        oublierAppareil();
        etat.message = { niveau: 'ok', texte: 'Cet appareil est oublié : le jeton chiffré est effacé. Pensez à révoquer le jeton sur GitHub si vous ne vous en servez plus.' };
        rendre();
      }, { cle: 'oublier-appareil' })));
    }

    // Première fois, ou remplacement : le jeton et le mot de passe
    var nouveau = el('form', { class: 'admin-bloc-plat' });
    nouveau.appendChild(el('h2', null, garde ? 'Remplacer le jeton et le mot de passe' : 'Première fois sur cet appareil'));
    var jt = el('input', { type: 'password', id: 'jeton', 'data-cle': 'jeton', autocomplete: 'off', spellcheck: 'false', placeholder: 'github_pat_…' });
    nouveau.appendChild(el('div', { class: 'admin-champ' }, [el('label', { for: 'jeton' }, 'Jeton GitHub'), jt]));
    var m1 = champMdp('mdp-nouveau', 'Mot de passe administrateur (au moins ' + MDP_MIN + ' caractères)', true);
    var m2 = champMdp('mdp-confirmer', 'Le même mot de passe, pour confirmer', true);
    nouveau.appendChild(el('p', { class: 'admin-aide' }, 'Conseil : une phrase facile à retenir pour vous, de quatre ou cinq mots, plutôt qu\'un mot compliqué. Le même mot de passe peut servir sur chaque appareil.'));
    nouveau.appendChild(m1.bloc);
    nouveau.appendChild(m2.bloc);
    nouveau.appendChild(el('p', { class: 'admin-actions' }, el('button', { type: 'submit', class: 'btn principal', 'data-cle': 'jeton-enregistrer' }, 'Chiffrer et garder le jeton sur cet appareil')));
    nouveau.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = jt.value.trim(), a = m1.input.value, b = m2.input.value;
      jt.value = ''; m1.input.value = ''; m2.input.value = '';
      var faute = !formeJeton(v) ? 'Ce texte ne ressemble pas à un jeton GitHub (il commence par github_pat_). Rien n\'est gardé.'
        : Array.from(a).length < MDP_MIN ? 'Le mot de passe doit avoir au moins ' + MDP_MIN + ' caractères (une phrase, par exemple). Rien n\'est gardé.'
        : a !== b ? 'Les deux mots de passe ne sont pas identiques. Rien n\'est gardé.' : null;
      if (faute) { etat.message = { niveau: 'erreur', texte: faute }; rendre('jeton'); return; }
      etat.message = { niveau: 'info', texte: 'Chiffrement du jeton…' };
      rendre();
      fermerCoffre(v, a).then(verifierJeton, function (err) { etat.message = { niveau: 'erreur', texte: err.message }; rendre(); });
    });
    vue.appendChild(nouveau);

    vue.appendChild(el('h2', null, 'Créer le jeton, pas à pas'));
    vue.appendChild(el('ol', { class: 'admin-etapes' }, [
      el('li', null, ['Sur GitHub, connecté·e à votre compte, ouvrir ', el('a', { href: 'https://github.com/settings/personal-access-tokens/new', target: '_blank', rel: 'noopener' }, 'Settings › Developer settings › Personal access tokens › Fine-grained tokens › Generate new token'), '.']),
      el('li', null, ['Nom : par exemple « Admin du site Ressources » ; ', el('strong', null, 'Expiration'), ' : une date (90 jours, par exemple) ; il faudra en refaire un ensuite.']),
      el('li', null, [el('strong', null, 'Repository access'), ' : « Only select repositories », puis choisir ', el('code', null, depot()), ' seulement.']),
      el('li', null, [el('strong', null, 'Permissions'), ' › Repository permissions › ', el('strong', null, 'Contents : Read and write'), '. Rien d\'autre (Metadata : Read-only s\'ajoute tout seul).']),
      el('li', null, ['« Generate token », puis copier le jeton (il commence par ', el('code', null, 'github_pat_'), ') : GitHub ne le montre qu\'une fois.']),
      el('li', null, 'Le coller ci-dessus avec votre mot de passe administrateur, puis « Chiffrer et garder le jeton sur cet appareil ». À faire une fois sur chaque appareil (ordinateur, téléphone) ; ensuite, le mot de passe suffit.'),
      el('li', null, 'En cas de perte d\'un appareil, ou à la fin : révoquer le jeton sur la même page de GitHub.')
    ]));
  }

  function verifierJeton() {
    etat.message = { niveau: 'info', texte: 'Vérification du jeton auprès de GitHub…' };
    rendre();
    api('GET', '').then(function (r) {
      var ecrire = r && r.permissions && r.permissions.push;
      etat.message = ecrire
        ? { niveau: 'ok', texte: 'Jeton enregistré et vérifié : il permet d\'écrire dans ' + depot() + '.' }
        : { niveau: 'erreur', texte: 'Jeton enregistré, mais il ne permet pas d\'écrire dans ' + depot() + ' : lui donner « Contents : Read and write » sur ce dépôt.' };
      return chargerArbre();
    }).then(function () { rendre(); }, function (e) {
      etat.message = { niveau: 'erreur', texte: e.message };
      rendre();
    });
  }

  /* ── Démarrage ────────────────────────────────────────────────── */

  function lireJSON(chemin) {
    return fetch(O.racine + chemin, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error(chemin + ' introuvable (code ' + r.status + ')');
      return r.json();
    });
  }

  window.pageAdmin = function (racine, outils) {
    O = outils;
    ANCIENNES_CLES.forEach(function (k) { ecrireStockage(k, null); }); // rien ne reste d'une garde précédente
    el = O.el;
    document.title = 'Admin – ' + O.titreSite();
    racine.appendChild(O.barreHaut('admin'));
    racinePage = el('div', { class: 'page admin' });
    racine.appendChild(racinePage);
    annonce = el('p', { class: 'invisible', 'aria-live': 'polite' });
    racinePage.appendChild(annonce);
    vue = el('main', { class: 'admin-vue' });
    racinePage.appendChild(vue);
    racinePage.appendChild(O.piedDePage()); // auteur, licences et « Code source sur GitHub » (décision du 10/11)
    barreBas = el('div', { class: 'admin-barre-bas', role: 'region', 'aria-label': 'Changements en attente', hidden: true });
    racine.appendChild(barreBas);
    vue.appendChild(el('p', { class: 'statut', role: 'status' }, 'Chargement de la bibliothèque…'));

    Promise.all([
      lireJSON('donnees/bibliotheque-complete.json'),
      lireJSON('donnees/schema/ressource.schema.json'),
      lireJSON('donnees/schema/vitrine.schema.json')
    ]).then(function (r) {
      etat.complete = r[0];
      etat.schemas = { ressource: r[1], vitrine: r[2] };
      appliquerRecents();
      etat.refs = new D.Referentiels(etat.complete.referentiels);
      etat.validation = new D.Validation({
        schemas: etat.schemas, refs: etat.refs,
        ids: etat.complete.ressources.map(function (x) { return x.id; }),
        fichiers: existe
      });
      var n = reprendreBrouillon();
      if (n) etat.message = { niveau: 'info', texte: n + (n > 1 ? ' fichiers modifiés ont été retrouvés' : ' fichier modifié a été retrouvé') + ' dans ce navigateur (changements pas encore enregistrés).' };
      if (etat.ignores.length) {
        etat.message = {
          niveau: 'erreur',
          texte: 'Des changements gardés dans ce navigateur visaient des fichiers que l\'admin n\'écrit jamais (seulement donnees/vitrine.json et les fiches de donnees/ressources/) : ils sont ignorés.',
          liste: etat.ignores.slice(0, 10)
        };
        garderBrouillon();
      }
      return chargerArbre().catch(function (e) {
        etat.message = { niveau: 'erreur', texte: 'Le jeton enregistré ne fonctionne pas : ' + e.message };
      });
    }).then(function () {
      window.addEventListener('hashchange', function () { rendre(); window.scrollTo(0, 0); });
      window.addEventListener('beforeunload', function (e) {
        if (enAttente().length) { garderBrouillon(); e.preventDefault(); e.returnValue = ''; }
      });
      rendre();
    }, function (e) {
      O.vider(vue);
      vue.appendChild(el('div', { class: 'alerte', role: 'alert' }, [
        el('p', null, el('strong', null, 'La bibliothèque n\'a pas pu être chargée')),
        el('p', { class: 'petit' }, [e.message + '. Elle est construite à chaque publication (« Publier le site »). Sur une copie locale, la construire d\'abord : ',
          el('code', null, 'python3 scripts/construire_bibliotheque.py')])
      ]));
    });
  };
})();
