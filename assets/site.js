/* ═══════════════════════════════════════════════════════════════
   Le moteur du site.

   Rien à modifier ici pour ajouter une ressource : chaque rubrique a
   sa liste dans son propre dossier (snt/ressources.js, pp/ressources.js…)
   et les réglages généraux sont dans reglages.js, à la racine.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* Couleurs de surligneur utilisables dans les listes : theme("…", "vert") */
  var COULEURS = {
    bleu: '#A5D8FF', vert: '#96F2D7', violet: '#D0BFFF', rose: '#FCC2D7',
    orange: '#FFD8A8', citron: '#C0EB75', cyan: '#99E9F2', jaune: '#FFEC99',
    lavande: '#BAC8FF', corail: '#FFC9C9', gris: '#DEE2E6'
  };
  /* Ordre des couleurs quand un thème n'en précise pas */
  var CYCLE = ['bleu', 'vert', 'violet', 'rose', 'orange', 'citron', 'cyan', 'jaune', 'lavande', 'corail'];

  var CHAMPS = ['titre', 'lien', 'texte', 'tags', 'annexes'];
  var TYPES = {
    pdf: 'PDF', png: 'Image', jpg: 'Image', jpeg: 'Image', gif: 'Image', svg: 'Image', webp: 'Image',
    mp4: 'Vidéo', webm: 'Vidéo', mp3: 'Son', ogg: 'Son'
  };
  /* Fichiers que le navigateur sait afficher (les autres sont téléchargés) */
  var LISIBLES = ['', 'html', 'htm', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'mp4', 'webm', 'mp3', 'ogg', 'txt'];
  /* Nombre de ressources à partir duquel une rubrique a sa barre de recherche */
  var SEUIL_RECHERCHE = 8;

  var RACINE = new URL('..', document.currentScript.src).href;
  var SUR_DISQUE = location.protocol === 'file:';

  var reglagesSite = {};
  var rubriques = {};
  var erreurs = [];

  /* ── Erreurs dans les listes : on les affiche sur la page ─────── */

  window.addEventListener('error', function (e) {
    var f = (e.filename || '').split(/[?#]/)[0];
    if (f.indexOf(RACINE) !== 0) return;
    var rel = f.slice(RACINE.length);
    if (!/(^|\/)(ressources|reglages)\.js$/.test(rel)) return;
    erreurs.push({ fichier: rel, ligne: e.lineno, message: e.message });
  });

  function signaler(fichier, message) {
    erreurs.push({ fichier: fichier, message: message });
    if (window.console) console.warn('[site] ' + fichier + ' : ' + message);
  }

  /* ── Outils ───────────────────────────────────────────────────── */

  function sansAccents(s) {
    return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function slug(s) {
    return sansAccents(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'theme';
  }

  function couleur(nom, rang) {
    if (typeof nom === 'string' && nom.charAt(0) === '#') return nom;
    if (nom && COULEURS[nom]) return COULEURS[nom];
    return COULEURS[CYCLE[(rang || 0) % CYCLE.length]];
  }

  function liste(x) {
    if (x == null || x === '') return [];
    return Array.isArray(x) ? x : [x];
  }

  function pluriel(n, un, plusieurs) {
    return n + ' ' + (n > 1 ? plusieurs : un);
  }

  function echapper(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* Dans les textes : `code`, **gras** et retours à la ligne */
  function mettreEnForme(s) {
    return echapper(s)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }

  function el(tag, attrs, enfants) {
    var n = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v == null || v === false) return;
        if (k === 'class') n.className = v;
        else if (k === 'html') n.innerHTML = v;
        else n.setAttribute(k, v === true ? '' : v);
      });
    }
    liste(enfants).forEach(function (c) {
      if (c == null || c === false) return;
      n.appendChild(typeof c === 'object' ? c : document.createTextNode(String(c)));
    });
    return n;
  }

  function vider(n) {
    while (n.firstChild) n.removeChild(n.firstChild);
  }

  function quandPret(f) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', f);
    else f();
  }

  /* ── Fonctions utilisées dans les fichiers de listes ──────────── */

  function dossierDuScript() {
    var s = document.currentScript;
    if (!s || !s.src) return null;
    var base = new URL('.', s.src).href;
    return { id: base.slice(RACINE.length).replace(/\/$/, ''), base: base };
  }

  function nouvelleRubrique(d, infos) {
    if (typeof infos === 'string') infos = { nom: infos };
    infos = infos || {};
    var rub = {
      id: d.id,
      base: d.base,
      nom: infos.nom || d.id,
      court: infos.court || infos.nom || d.id,
      niveau: infos.niveau || '',
      presentation: infos.presentation || '',
      couleur: couleur(infos.couleur, Object.keys(rubriques).length),
      themes: []
    };
    rubriques[d.id] = rub;
    return rub;
  }

  function rubriqueEnCours() {
    var d = dossierDuScript();
    if (!d) return null;
    return rubriques[d.id] || nouvelleRubrique(d, {});
  }

  function themeEnCours(rub) {
    if (!rub.themes.length) {
      rub.themes.push({ nom: null, court: null, id: 'ressources', couleur: rub.couleur, blocs: [{ groupe: null, ressources: [] }] });
    }
    return rub.themes[rub.themes.length - 1];
  }

  window.reglages = function (r) {
    reglagesSite = r || {};
    var dossiers = liste(reglagesSite.rubriques).slice();
    var ici = rubriqueDeLaPage();
    if (ici && dossiers.indexOf(ici) < 0) dossiers.push(ici); // rubrique non listée : accessible par son adresse
    var restants = dossiers.length;
    if (!restants) return quandPret(afficher);

    function fini() {
      restants -= 1;
      if (restants === 0) quandPret(afficher);
    }

    dossiers.forEach(function (id) {
      var fichier = id + '/ressources.js';
      var s = document.createElement('script');
      s.src = RACINE + fichier;
      s.async = false; // garder l'ordre
      s.onload = function () {
        if (!rubriques[id]) {
          var deja = erreurs.some(function (e) { return e.fichier === fichier; });
          if (!deja) signaler(fichier, 'le fichier ne contient aucune ressource ni rubrique.');
          nouvelleRubrique({ id: id, base: RACINE + id + '/' }, {});
        }
        fini();
      };
      s.onerror = function () {
        signaler(fichier, 'fichier introuvable. Le dossier « ' + id + ' » est-il bien écrit dans reglages.js ?');
        nouvelleRubrique({ id: id, base: RACINE + id + '/' }, {});
        fini();
      };
      document.head.appendChild(s);
    });
  };

  window.rubrique = function (infos) {
    var d = dossierDuScript();
    if (!d) return;
    var avant = rubriques[d.id];
    var rub = nouvelleRubrique(d, infos);
    if (avant) rub.themes = avant.themes;
  };

  window.theme = function (nom, options) {
    var rub = rubriqueEnCours();
    if (!rub) return;
    if (typeof options === 'string') options = { couleur: options };
    options = options || {};
    var court = options.court || nom;
    var rang = rub.themes.filter(function (t) { return t.nom; }).length;
    var id = slug(court), base = id, k = 2;
    while (rub.themes.some(function (t) { return t.id === id; })) id = base + '-' + (k++);
    rub.themes.push({
      nom: nom,
      court: court,
      id: id,
      couleur: couleur(options.couleur, rang),
      blocs: [{ groupe: null, ressources: [] }]
    });
  };

  window.groupe = function (nom) {
    var rub = rubriqueEnCours();
    if (!rub) return;
    themeEnCours(rub).blocs.push({ groupe: nom, ressources: [] });
  };

  window.ressource = function (r) {
    var rub = rubriqueEnCours();
    if (!rub) return;
    var fichier = rub.id + '/ressources.js';
    if (!r || typeof r !== 'object') {
      signaler(fichier, 'ressource() attend un bloc entre accolades : ressource({ titre: "…", lien: "…" })');
      return;
    }
    Object.keys(r).forEach(function (k) {
      if (CHAMPS.indexOf(k) < 0) {
        signaler(fichier, '« ' + k + ' » n\'est pas un champ connu (dans « ' + (r.titre || r.lien || '?') +
          ' »). Champs possibles : ' + CHAMPS.join(', ') + '.');
      }
    });
    if (!r.titre) signaler(fichier, 'une ressource n\'a pas de titre' + (r.lien ? ' (' + r.lien + ')' : '') + '.');

    var t = themeEnCours(rub);
    var bloc = t.blocs[t.blocs.length - 1];
    bloc.ressources.push({
      titre: r.titre || r.lien || 'Sans titre',
      lien: r.lien || '',
      texte: r.texte || '',
      tags: liste(r.tags),
      annexes: r.annexes && typeof r.annexes === 'object' ? r.annexes : null,
      theme: t,
      groupe: bloc.groupe,
      rubrique: rub
    });
  };

  /* ── Données ──────────────────────────────────────────────────── */

  function ordreRubriques() {
    return liste(reglagesSite.rubriques).map(function (id) { return rubriques[id]; }).filter(Boolean);
  }

  function ressourcesDe(rub) {
    var tout = [];
    rub.themes.forEach(function (t) {
      t.blocs.forEach(function (b) { tout = tout.concat(b.ressources); });
    });
    return tout;
  }

  function compterTheme(t) {
    return t.blocs.reduce(function (n, b) { return n + b.ressources.length; }, 0);
  }

  function texteCherche(r) {
    if (!r._t) {
      r._t = sansAccents([
        r.titre, r.texte, r.tags.join(' '), r.theme.nom || '', r.groupe || '',
        r.rubrique.nom, r.rubrique.court, r.annexes ? Object.keys(r.annexes).join(' ') : '', r.lien
      ].join(' ')).toLowerCase();
    }
    return r._t;
  }

  function filtreRecherche(q) {
    var mots = sansAccents(q).toLowerCase().split(/\s+/).filter(Boolean);
    if (!mots.length) return null;
    return function (r) {
      var t = texteCherche(r);
      return mots.every(function (m) { return t.indexOf(m) >= 0; });
    };
  }

  /* Un lien : adresse web, ou fichier relatif au dossier de la rubrique */
  function analyser(lien, base) {
    var url;
    try { url = new URL(lien, base); } catch (e) { return null; }
    var interne = url.href.indexOf(RACINE) === 0;
    var m = url.pathname.match(/\.([a-z0-9]+)$/i);
    var ext = m ? m[1].toLowerCase() : '';
    var type;
    if (interne) {
      if (ext === '' || ext === 'html' || ext === 'htm') type = 'Sur ce site';
      else type = TYPES[ext] || 'Fichier .' + ext;
    } else {
      var hote = url.hostname.replace(/^www\./, '');
      if (/\.github\.io$/.test(hote)) {
        var dossier = url.pathname.split('/').filter(Boolean)[0];
        if (dossier && !/\.[a-z0-9]+$/i.test(dossier)) hote += '/' + dossier;
      }
      type = TYPES[ext] ? TYPES[ext] + ', ' + hote : hote;
    }
    return {
      href: url.href,
      interne: interne,
      type: type,
      telecharger: interne && LISIBLES.indexOf(ext) < 0,
      nouvelOnglet: !interne || (ext !== '' && ext !== 'html' && ext !== 'htm')
    };
  }

  /* ── Adresses ─────────────────────────────────────────────────── */

  function rubriqueDeLaPage() {
    var ici = location.href.split(/[?#]/)[0];
    if (ici.indexOf(RACINE) !== 0) return null;
    var morceaux = ici.slice(RACINE.length).split('/');
    return morceaux.length > 1 ? morceaux[0] : null;
  }

  function urlAccueil() {
    return RACINE + (SUR_DISQUE ? 'index.html' : '');
  }

  function urlRubrique(rub, ancre) {
    return rub.base + (SUR_DISQUE ? 'index.html' : '') + (ancre ? '#' + ancre : '');
  }

  function urlGithub(action, chemin) {
    return 'https://github.com/' + reglagesSite.depot + '/' + action + '/' + (reglagesSite.branche || 'main') + '/' + chemin;
  }

  function titreSite() {
    return reglagesSite.titre || 'Ressources';
  }

  function lireRecherche() {
    try { return new URLSearchParams(location.search).get('q') || ''; } catch (e) { return ''; }
  }

  function ecrireRecherche(q) {
    try {
      var u = new URL(location.href);
      if (q) u.searchParams.set('q', q); else u.searchParams.delete('q');
      history.replaceState(null, '', u.href);
    } catch (e) { /* sans importance */ }
  }

  /* ── Morceaux de page ─────────────────────────────────────────── */

  function lienVers(info, texte, classe) {
    return el('a', {
      class: classe,
      href: info.href,
      target: info.nouvelOnglet ? '_blank' : null,
      rel: info.interne ? null : 'noopener',
      download: info.telecharger ? true : null
    }, texte);
  }

  function blocRessource(r, avecChemin) {
    var info = r.lien ? analyser(r.lien, r.rubrique.base) : null;
    var li = el('li', { class: 'res', style: avecChemin ? '--hl:' + r.theme.couleur : null });

    li.appendChild(info ? lienVers(info, r.titre, 'titre') : el('span', { class: 'titre sans-lien' }, r.titre));

    if (avecChemin) {
      li.appendChild(el('p', { class: 'chemin' }, [
        el('a', { href: urlRubrique(r.rubrique) }, r.rubrique.nom),
        r.theme.nom ? ', ' : null,
        r.theme.nom ? el('a', { href: urlRubrique(r.rubrique, r.theme.id) }, r.theme.court) : null
      ]));
    }

    if (r.texte) li.appendChild(el('p', { html: mettreEnForme(r.texte) }));

    if (r.annexes) {
      var annexes = el('p', { class: 'annexes' });
      Object.keys(r.annexes).forEach(function (nom) {
        var a = analyser(r.annexes[nom], r.rubrique.base);
        if (!a) return;
        annexes.appendChild(el('span', { class: 'annexe' }, [
          lienVers(a, nom), ' ', el('span', { class: 'type' }, '(' + a.type + ')')
        ]));
      });
      if (annexes.childNodes.length) li.appendChild(annexes);
    }

    var tags = el('p', { class: 'tags' });
    r.tags.forEach(function (t) { tags.appendChild(el('span', null, t)); });
    if (info) tags.appendChild(el('span', { class: 'site' }, info.type));
    if (tags.childNodes.length) li.appendChild(tags);

    return li;
  }

  function sectionTheme(t, filtre) {
    var s = el('section', { class: 'theme', id: t.id, style: '--hl:' + t.couleur });
    if (t.nom) s.appendChild(el('h2', null, el('span', { class: 'surligne' }, t.nom)));
    var n = 0;
    t.blocs.forEach(function (b) {
      var res = filtre ? b.ressources.filter(filtre) : b.ressources;
      if (!res.length) return;
      if (b.groupe) s.appendChild(el('h3', null, b.groupe));
      s.appendChild(el('ul', { class: 'ressources' }, res.map(function (r) { return blocRessource(r); })));
      n += res.length;
    });
    if (!n) {
      s.className += ' est-vide';
      s.appendChild(el('p', { class: 'vide' }, 'Rien ici pour l\'instant.'));
    }
    s._n = n;
    return s;
  }

  function sommaire(themes) {
    return el('nav', { 'aria-label': 'Thèmes' }, el('ul', { class: 'index' }, themes.map(function (t) {
      var n = compterTheme(t);
      return el('li', null, el('a', {
        href: '#' + t.id,
        class: n ? null : 'est-vide',
        style: '--hl:' + t.couleur
      }, [t.court, el('span', { class: 'nb', 'aria-hidden': 'true' }, String(n))]));
    })));
  }

  function barre(active) {
    var ul = el('ul', null, el('li', null, el('a', { href: urlAccueil(), class: 'vers-accueil' }, 'Accueil')));
    ordreRubriques().forEach(function (r) {
      ul.appendChild(el('li', { style: '--hl:' + r.couleur }, el('a', {
        href: urlRubrique(r),
        'aria-current': r === active ? 'page' : null
      }, r.court)));
    });
    return el('nav', { class: 'barre', 'aria-label': 'Rubriques' }, ul);
  }

  function champRecherche(texte, quandOnTape) {
    var input = el('input', {
      type: 'search', id: 'recherche', class: 'recherche', placeholder: texte,
      autocomplete: 'off', spellcheck: 'false', enterkeyhint: 'search'
    });
    var statut = el('p', { class: 'statut', 'aria-live': 'polite' });
    input.value = lireRecherche();
    input.addEventListener('input', function () {
      var q = input.value.trim();
      ecrireRecherche(q);
      quandOnTape(q);
    });
    document.addEventListener('keydown', function (e) {
      var cible = e.target.tagName;
      if (e.key === '/' && cible !== 'INPUT' && cible !== 'TEXTAREA') {
        e.preventDefault();
        input.focus();
      }
      if (e.key === 'Escape' && e.target === input && input.value) {
        input.value = '';
        ecrireRecherche('');
        quandOnTape('');
      }
    });
    return {
      bloc: el('div', { class: 'cherche', role: 'search' }, [
        el('label', { for: 'recherche', class: 'invisible' }, texte), input, statut
      ]),
      input: input,
      statut: statut
    };
  }

  function blocAlertes(fichiers) {
    var liste_ = erreurs.filter(function (e) { return !fichiers || fichiers.indexOf(e.fichier) >= 0; });
    if (!liste_.length) return null;
    return el('div', { class: 'alerte', role: 'alert' }, [
      el('p', null, el('strong', null, 'Une liste de ressources contient une erreur')),
      el('ul', null, liste_.map(function (e) {
        return el('li', null, [
          el('code', null, e.fichier), e.ligne ? ', ligne ' + e.ligne : '', ' : ', e.message
        ]);
      })),
      el('p', { class: 'petit' }, 'Souvent : une virgule oubliée en fin de ligne, ou un guillemet, une parenthèse ou une accolade pas refermés, juste avant la ligne indiquée.')
    ]);
  }

  function blocRubrique(r) {
    var n = ressourcesDe(r).length;
    var themes = r.themes.filter(function (t) { return t.nom; });
    var infos = [r.niveau, n ? pluriel(n, 'ressource', 'ressources') : ''].filter(Boolean).join(', ');
    return el('section', { class: 'rub' + (n ? '' : ' est-vide'), style: '--hl:' + r.couleur }, [
      el('h2', null, el('a', { class: 'rub-nom', href: urlRubrique(r) }, r.nom)),
      infos ? el('p', { class: 'niveau' }, infos) : null,
      r.presentation ? el('p', { class: 'rub-texte', html: mettreEnForme(r.presentation) }) : null,
      themes.length ? el('ul', { class: 'themes-mini' }, themes.map(function (t) {
        return el('li', null, el('a', {
          href: urlRubrique(r, t.id),
          class: compterTheme(t) ? null : 'est-vide',
          style: '--hl:' + t.couleur
        }, t.court));
      })) : null
    ]);
  }

  /* ── Pages ────────────────────────────────────────────────────── */

  function pageAccueil(racine) {
    document.title = titreSite();
    var recherche = champRecherche('Chercher dans toutes les ressources', maj);
    racine.appendChild(el('header', { class: 'entete' }, [
      el('h1', null, titreSite()),
      reglagesSite.presentation ? el('p', { class: 'chapo', html: mettreEnForme(reglagesSite.presentation) }) : null,
      recherche.bloc
    ]));
    var alerte = blocAlertes(null);
    if (alerte) racine.appendChild(alerte);

    var vue = el('main', { id: 'contenu' });
    racine.appendChild(vue);

    var toutes = [];
    ordreRubriques().forEach(function (r) { toutes = toutes.concat(ressourcesDe(r)); });

    function maj(q) {
      vider(vue);
      var filtre = filtreRecherche(q);
      if (!filtre) {
        recherche.statut.textContent = '';
        ordreRubriques().forEach(function (r) { vue.appendChild(blocRubrique(r)); });
        return;
      }
      var trouvees = toutes.filter(filtre);
      recherche.statut.textContent = trouvees.length ? pluriel(trouvees.length, 'ressource trouvée', 'ressources trouvées') : '';
      if (trouvees.length) {
        vue.appendChild(el('ul', { class: 'ressources resultats' }, trouvees.map(function (r) { return blocRessource(r, true); })));
      } else {
        vue.appendChild(el('p', { class: 'vide' }, 'Aucune ressource ne correspond à « ' + q + ' ».'));
      }
    }
    maj(recherche.input.value.trim());

    var pied = el('footer', { class: 'pied' }, [
      el('h2', null, 'Ajouter une ressource'),
      el('p', null, 'Chaque rubrique a sa liste dans un petit fichier texte de son dossier. On y ajoute un lien vers une ressource en ligne, ou vers un fichier (PDF, fiche, diaporama) déposé dans le dossier de la rubrique. Le lien « Modifier la liste » se trouve en bas de chaque rubrique.'),
      reglagesSite.depot ? el('p', { class: 'actions' }, el('a', { href: 'https://github.com/' + reglagesSite.depot + '#readme' }, 'Mode d\'emploi complet')) : null,
      el('p', { class: 'petit' }, 'Les ressources externes restent la propriété de leurs auteurs.')
    ]);
    racine.appendChild(pied);
  }

  function pageRubrique(racine, rub) {
    document.title = rub.nom + ' – ' + titreSite();
    racine.appendChild(barre(rub));

    var nommes = rub.themes.filter(function (t) { return t.nom; });
    var total = ressourcesDe(rub).length;
    var entete = el('header', { class: 'entete', style: '--hl:' + rub.couleur }, [
      el('h1', null, el('span', { class: 'surligne' }, rub.nom)),
      rub.niveau ? el('p', { class: 'niveau' }, rub.niveau) : null,
      rub.presentation ? el('p', { class: 'chapo', html: mettreEnForme(rub.presentation) }) : null,
      nommes.length > 1 ? sommaire(nommes) : null
    ]);
    racine.appendChild(entete);

    var alerte = blocAlertes([rub.id + '/ressources.js', 'reglages.js']);
    if (alerte) racine.appendChild(alerte);

    var main = el('main', { id: 'contenu' });
    var zone = el('div');
    var recherche = null;

    function rendre(q) {
      vider(zone);
      var filtre = filtreRecherche(q || '');
      var trouvees = 0;
      rub.themes.forEach(function (t) {
        var s = sectionTheme(t, filtre);
        if (filtre && !s._n) return;
        trouvees += s._n;
        zone.appendChild(s);
      });
      if (recherche) {
        recherche.statut.textContent = filtre && trouvees ? pluriel(trouvees, 'ressource trouvée', 'ressources trouvées') : '';
      }
      if (filtre && !trouvees) zone.appendChild(el('p', { class: 'vide' }, 'Aucune ressource ne correspond à « ' + q + ' ».'));
    }

    if (total >= SEUIL_RECHERCHE) {
      recherche = champRecherche('Chercher dans ' + rub.nom, rendre);
      main.appendChild(recherche.bloc);
    }
    main.appendChild(zone);
    rendre(recherche ? recherche.input.value.trim() : '');
    racine.appendChild(main);

    var pied = el('footer', { class: 'pied' }, [
      el('h2', null, 'Ajouter une ressource'),
      el('p', null, [
        'La liste de cette page est dans ', el('code', null, rub.id + '/ressources.js'),
        '. Pour un PDF ou un autre fichier, le déposer d\'abord dans le dossier ',
        el('code', null, rub.id + '/fichiers'), ', puis l\'ajouter à la liste avec ',
        el('code', null, 'lien: "fichiers/nom-du-fichier.pdf"'), '.'
      ]),
      reglagesSite.depot ? el('p', { class: 'actions' }, [
        el('a', { href: urlGithub('edit', rub.id + '/ressources.js') }, 'Modifier la liste'),
        el('a', { href: urlGithub('upload', rub.id + '/fichiers') }, 'Déposer un fichier'),
        el('a', { href: 'https://github.com/' + reglagesSite.depot + '#readme' }, 'Mode d\'emploi')
      ]) : null
    ]);
    racine.appendChild(pied);
  }

  function afficher() {
    var racine = document.getElementById('site');
    if (!racine) return;
    vider(racine);
    var id = rubriqueDeLaPage();
    if (id && rubriques[id]) pageRubrique(racine, rubriques[id]);
    else pageAccueil(racine);

    if (location.hash) {
      var cible = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (cible) {
        cible.classList.add('cible');
        cible.scrollIntoView();
      }
    }
  }
})();
