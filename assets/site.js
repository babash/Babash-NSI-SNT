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
    bleu: '#38BDF8', vert: '#34D399', violet: '#A78BFA', rose: '#F472B6',
    orange: '#FB923C', citron: '#A3E635', cyan: '#22D3EE', jaune: '#FACC15',
    lavande: '#818CF8', corail: '#F87171', gris: '#94A3B8'
  };
  /* Ordre des couleurs quand un thème n'en précise pas */
  var CYCLE = ['cyan', 'rose', 'violet', 'vert', 'orange', 'bleu', 'jaune', 'lavande', 'citron', 'corail'];

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

  /* Le dépôt du site, si reglages.js n'en donne pas (depot: "propriétaire/nom").
     Décision de l'enseignant du 10/11/2026 : chaque page a un lien « Code source sur GitHub ». */
  var DEPOT = 'babash/Babash-NSI-SNT';

  var reglagesSite = {};
  var depotSite = null; // celui de reglages.js, vérifié ; null s'il manque ou s'il est mal écrit
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
      programme: infos.programme || null,
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
      rub.themes.push({ nom: null, court: null, id: 'ressources', couleur: rub.couleur, programme: [], blocs: [{ groupe: null, ressources: [] }] });
    }
    return rub.themes[rub.themes.length - 1];
  }

  /* « propriétaire/nom » ; une adresse https://github.com/… est acceptée et raccourcie */
  function lireDepot(v) {
    if (v == null || v === '') return null;
    var s = String(v).trim().replace(/^https?:\/\/(www\.)?github\.com\//i, '').replace(/(\.git)?\/*$/i, '');
    if (/^[A-Za-z0-9-]+\/[A-Za-z0-9._-]+$/.test(s)) return s;
    signaler('reglages.js', '« depot » doit s\'écrire "propriétaire/nom", par exemple "' + DEPOT +
      '" (valeur lue : « ' + v + ' »). En attendant, le lien « Code source sur GitHub » mène à ' + DEPOT + '.');
    return null;
  }

  window.reglages = function (r) {
    reglagesSite = r || {};
    depotSite = lireDepot(reglagesSite.depot);
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
      programme: liste(options.programme),
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
      var morceaux = url.pathname.split('/').filter(Boolean);
      if (/\.github\.io$/.test(hote)) {
        if (morceaux[0] && !/\.[a-z0-9]+$/i.test(morceaux[0])) hote += '/' + morceaux[0];
      } else if (hote === 'github.com' && morceaux.length >= 2) {
        hote += '/' + morceaux[0] + '/' + morceaux[1];
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
    return urlDepot() + '/' + action + '/' + (reglagesSite.branche || 'main') + '/' + chemin;
  }

  /* L'accueil du dépôt : celui de reglages.js, sinon celui du site */
  function urlDepot() {
    return 'https://github.com/' + (depotSite || DEPOT);
  }

  function titreSite() {
    return reglagesSite.titre || 'Ressources';
  }

  /* ── Licences, auteur et mention de l'IA (bas de chaque page) ──── */

  /* Décision de l'enseignant du 07/11/2026 : documents en CC BY-SA 4.0, code des applications en MIT */
  var LICENCES = [
    { nom: 'CC BY-SA 4.0', quoi: 'documents', lien: 'https://creativecommons.org/licenses/by-sa/4.0/deed.fr' },
    { nom: 'MIT', quoi: 'code des applications', lien: 'https://opensource.org/license/mit' }
  ];
  /* Textes validés par l'enseignant (07/11/2026). reglages.js peut les remplacer ; un texte vide ("") les retire.
     {auteur} est remplacé par le nom de l'auteur. */
  var MENTIONS = {
    auteur: 'Babash - NSI Tani Malandi',
    mention_ia: 'Ces ressources sont conçues par {auteur} ; beaucoup le sont avec l\'aide de l\'IA.',
    reutilisation: 'Tu peux les réutiliser et les modifier en mentionnant {auteur} et la licence ; un document modifié se partage sous la même licence.',
    invitation_ia: 'Si tu utilises l\'IA pour les modifier, merci de le préciser.'
  };

  function mention(cle) {
    var v = reglagesSite[cle];
    return typeof v === 'string' ? v.trim() : MENTIONS[cle];
  }

  /* Un texte où {auteur} devient le nom (en gras la première fois qu'il apparaît dans le bloc) */
  function avecAuteur(texte, auteur, gras) {
    var morceaux = [];
    auteur = auteur.replace(/ - /g, ' - '); // pas de retour à la ligne autour du tiret
    texte.split('{auteur}').forEach(function (t, i) {
      if (i) morceaux.push(gras ? el('strong', null, auteur) : auteur);
      if (t) morceaux.push(t);
    });
    return morceaux;
  }

  function mentions() {
    var auteur = mention('auteur') || MENTIONS.auteur;
    var lignes = [];
    var ia = mention('mention_ia');
    if (ia) lignes.push(avecAuteur(ia, auteur, true));

    var licences = [];
    LICENCES.forEach(function (l, i) {
      licences.push(i ? ', ' + l.quoi : l.quoi.charAt(0).toUpperCase() + l.quoi.slice(1));
      licences.push(' sous licence ', el('a', { href: l.lien, rel: 'license' }, l.nom));
    });
    /* Décision du 10/11/2026 (22:58) : le lien vers le dépôt, à côté de l'auteur et de la licence */
    licences.push('. ', el('a', { href: urlDepot() }, 'Code source sur GitHub'), '.');
    lignes.push(licences);

    var reutiliser = [mention('reutilisation'), mention('invitation_ia')].filter(Boolean).join(' ');
    if (reutiliser) lignes.push(avecAuteur(reutiliser, auteur, !ia));

    lignes.push(['Les ressources externes restent la propriété de leurs auteurs et autrices : leur site d\'origine est indiqué sur chaque ressource. Décor du site : dessin original.']);

    var contenu = [];
    lignes.forEach(function (l, i) {
      if (i) contenu.push(el('br'));
      contenu = contenu.concat(l);
    });
    return el('p', { class: 'petit mentions' }, contenu);
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

  function idGroupe(t, nom) {
    return t.id + '--' + slug(nom);
  }

  function lignePrograme(t) {
    var pleins = {};
    t.blocs.forEach(function (b) { if (b.groupe && b.ressources.length) pleins[b.groupe] = true; });
    return el('div', { class: 'programme' }, [
      el('p', { class: 'programme-titre' }, 'Au programme'),
      el('ul', null, t.programme.map(function (c) {
        return el('li', null, pleins[c]
          ? el('a', { href: '#' + idGroupe(t, c) }, c)
          : el('span', null, c));
      }))
    ]);
  }

  function sectionTheme(t, filtre) {
    var s = el('section', { class: 'theme', id: t.id, style: '--hl:' + t.couleur });
    if (t.nom) s.appendChild(el('h2', null, el('span', { class: 'surligne' }, t.nom)));
    if (t.programme.length && !filtre) s.appendChild(lignePrograme(t));
    var n = 0;
    t.blocs.forEach(function (b) {
      var res = filtre ? b.ressources.filter(filtre) : b.ressources;
      if (!res.length) return;
      if (b.groupe) s.appendChild(el('h3', { id: idGroupe(t, b.groupe) }, b.groupe));
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

  /* ── Affichage clair / obscur ─────────────────────────────────── */

  var ICONES = {
    auto: '<svg viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 2a6 6 0 0 1 0 12z" fill="currentColor"/></svg>',
    light: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="8" cy="8" r="3"/><path d="M8 1v1.6M8 13.4V15M1 8h1.6M13.4 8H15M3 3l1.1 1.1M11.9 11.9 13 13M3 13l1.1-1.1M11.9 4.1 13 3"/></svg>',
    dark: '<svg viewBox="0 0 16 16"><path d="M13.6 10.2A6 6 0 0 1 5.8 2.4a6 6 0 1 0 7.8 7.8z" fill="currentColor"/></svg>'
  };
  var MODES = [
    { id: 'auto', nom: 'Auto', aide: 'Suivre le réglage de l\'appareil' },
    { id: 'light', nom: 'Clair', aide: 'Affichage clair' },
    { id: 'dark', nom: 'Obscur', aide: 'Affichage obscur' }
  ];

  function lireMode() {
    try { return localStorage.getItem('theme') || 'auto'; } catch (e) { return 'auto'; }
  }

  function appliquerMode(m) {
    var html = document.documentElement;
    if (m === 'light' || m === 'dark') html.setAttribute('data-theme', m);
    else html.removeAttribute('data-theme');
    try {
      if (m === 'light' || m === 'dark') localStorage.setItem('theme', m);
      else localStorage.removeItem('theme');
    } catch (e) { /* navigation privée : le choix vaut pour cette page */ }
  }

  function choixMode() {
    var actuel = lireMode();
    var groupe = el('div', { class: 'mode', role: 'group', 'aria-label': 'Affichage' });
    MODES.forEach(function (m) {
      var b = el('button', {
        type: 'button', class: 'mode-btn', title: m.aide,
        'aria-pressed': m.id === actuel ? 'true' : 'false'
      }, [
        el('span', { class: 'mode-ico', 'aria-hidden': 'true', html: ICONES[m.id] }),
        el('span', { class: 'mode-nom' }, m.nom)
      ]);
      b.addEventListener('click', function () {
        appliquerMode(m.id);
        Array.prototype.forEach.call(groupe.children, function (x) {
          x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
        });
      });
      groupe.appendChild(b);
    });
    return groupe;
  }

  /* ── Décor : la ville et sa liaison montante (dessin original) ── */

  var LOGO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M12 2.2 20.5 7v10L12 21.8 3.5 17V7z"/><path d="M7.5 12h4l2.2-3.2h2.3M11.5 12l2.2 3.2h2.3"/><circle cx="17.4" cy="8.8" r="1.2" fill="currentColor"/><circle cx="17.4" cy="15.2" r="1.2" fill="currentColor"/></svg>';

  function scene(couleur, graine) {
    var W = 1200, H = 420, horizon = 318, ux = 858;
    var r = graine || 11;
    function alea() { r = (r * 9301 + 49297) % 233280; return r / 233280; }
    function n(x) { return Math.round(x * 10) / 10; }
    var s = [];
    s.push('<svg class="scene" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">');
    s.push('<defs>' +
      '<linearGradient id="sc-ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04060E"/><stop offset=".6" stop-color="#110F30"/><stop offset="1" stop-color="#2A1046"/></linearGradient>' +
      '<radialGradient id="sc-halo" cx=".71" cy=".76" r=".5"><stop offset="0" stop-color="' + couleur + '" stop-opacity=".38"/><stop offset="1" stop-color="' + couleur + '" stop-opacity="0"/></radialGradient>' +
      '<linearGradient id="sc-sol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#170A2B"/><stop offset="1" stop-color="#03050B"/></linearGradient>' +
      '<filter id="sc-flou" x="-200%" y="-10%" width="500%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>' +
      '</defs>');
    s.push('<rect width="' + W + '" height="' + H + '" fill="url(#sc-ciel)"/>');
    s.push('<rect width="' + W + '" height="' + H + '" fill="url(#sc-halo)"/>');

    // Pluie de données
    for (var i = 0; i < 80; i++) {
      s.push('<rect x="' + n(alea() * W) + '" y="' + n(alea() * horizon * 0.85) + '" width="1.2" height="' +
        n(6 + alea() * 42) + '" fill="' + (alea() < 0.25 ? '#FF3D9A' : couleur) + '" opacity="' + n(0.06 + alea() * 0.28) + '"/>');
    }

    // Liaison montante
    s.push('<line x1="' + ux + '" y1="0" x2="' + ux + '" y2="' + horizon + '" stroke="' + couleur + '" stroke-width="9" opacity=".45" filter="url(#sc-flou)"/>');
    s.push('<line x1="' + ux + '" y1="0" x2="' + ux + '" y2="' + horizon + '" stroke="#F2FDFF" stroke-width="1.6" opacity=".9"/>');
    s.push('<rect class="impulsion" x="' + (ux - 2) + '" y="' + (horizon - 40) + '" width="4" height="30" fill="#FFFFFF"/>');

    // Tours et fenêtres allumées
    var x = -10, teintes = [couleur, '#FF3D9A', '#FFD166'];
    while (x < W) {
      var w = 24 + alea() * 64;
      var proche = Math.abs(x + w / 2 - ux) < 170;
      var h = 26 + alea() * 104 + (proche ? 70 : 0);
      var y = horizon - h;
      s.push('<rect x="' + n(x) + '" y="' + n(y) + '" width="' + n(w) + '" height="' + n(h) + '" fill="#03050C"/>');
      if (h > 120 && alea() < 0.6) {
        s.push('<line x1="' + n(x + w / 2) + '" y1="' + n(y) + '" x2="' + n(x + w / 2) + '" y2="' + n(y - 14 - alea() * 18) + '" stroke="#03050C" stroke-width="2"/>');
      }
      for (var fy = y + 8; fy < horizon - 6; fy += 9) {
        for (var fx = x + 5; fx < x + w - 6; fx += 8) {
          if (alea() < 0.13) {
            s.push('<rect x="' + n(fx) + '" y="' + n(fy) + '" width="3" height="4" fill="' +
              teintes[Math.floor(alea() * 3)] + '" opacity="' + n(0.5 + alea() * 0.5) + '"/>');
          }
        }
      }
      x += w + 1 + alea() * 6;
    }

    // Sol quadrillé
    s.push('<rect y="' + horizon + '" width="' + W + '" height="' + (H - horizon) + '" fill="url(#sc-sol)"/>');
    s.push('<line x1="0" y1="' + horizon + '" x2="' + W + '" y2="' + horizon + '" stroke="' + couleur + '" stroke-width="1.6" opacity=".85"/>');
    for (var k = 1; k <= 8; k++) {
      var gy = horizon + Math.pow(k / 8, 2) * (H - horizon);
      s.push('<line x1="0" y1="' + n(gy) + '" x2="' + W + '" y2="' + n(gy) + '" stroke="' + couleur + '" stroke-width="1" opacity=".22"/>');
    }
    for (var v = -16; v <= 16; v++) {
      s.push('<line x1="' + (600 + v * 7) + '" y1="' + horizon + '" x2="' + (600 + v * 95) + '" y2="' + H + '" stroke="' + couleur + '" stroke-width="1" opacity=".18"/>');
    }
    s.push('</svg>');
    return s.join('');
  }

  /* ── Barre du haut ────────────────────────────────────────────── */

  function barreHaut(active) {
    return el('header', { class: 'barre-haut' }, el('div', { class: 'barre-int' }, [
      el('a', { class: 'marque', href: urlAccueil() }, [
        el('span', { class: 'marque-logo', 'aria-hidden': 'true', html: LOGO }),
        el('span', { class: 'marque-nom' }, titreSite())
      ]),
      el('nav', { class: 'nav', 'aria-label': 'Rubriques' }, el('ul', null, ordreRubriques().map(function (r) {
        return el('li', { style: '--hl:' + r.couleur }, el('a', {
          href: urlRubrique(r),
          'aria-current': r === active ? 'page' : null
        }, r.court));
      }))),
      choixMode()
    ]));
  }

  /* ── Sommaire des thèmes (colonne de gauche sur grand écran) ──── */

  function sommaire(themes) {
    var details = el('details', { class: 'sommaire' }, [
      el('summary', null, ['Thèmes ', el('span', { class: 'nb' }, String(themes.length))]),
      el('ul', null, themes.map(function (t) {
        var nb = compterTheme(t);
        return el('li', { style: '--hl:' + t.couleur }, el('a', {
          href: '#' + t.id,
          class: nb ? null : 'est-vide',
          'data-theme-id': t.id
        }, [el('span', { class: 'sommaire-nom' }, t.court), el('span', { class: 'nb' }, String(nb))]));
      }))
    ]);
    var large = window.matchMedia ? window.matchMedia('(min-width: 1080px)') : null;
    function ajuster() { details.open = !!(large && large.matches); }
    ajuster();
    if (large) {
      if (large.addEventListener) large.addEventListener('change', ajuster);
      else if (large.addListener) large.addListener(ajuster);
    }
    return details;
  }

  /* Signale dans le sommaire le thème en cours de lecture */
  function suivreLecture(zone, details) {
    if (!('IntersectionObserver' in window) || !details) return;
    var liens = {};
    Array.prototype.forEach.call(details.querySelectorAll('a[data-theme-id]'), function (a) {
      liens[a.getAttribute('data-theme-id')] = a;
    });
    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) {
        if (!e.isIntersecting) return;
        Object.keys(liens).forEach(function (id) { liens[id].removeAttribute('aria-current'); });
        var a = liens[e.target.id];
        if (a) a.setAttribute('aria-current', 'location');
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Array.prototype.forEach.call(zone.querySelectorAll('.theme'), function (s) { obs.observe(s); });
  }

  /* ── Recherche ────────────────────────────────────────────────── */

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
        el('label', { for: 'recherche', class: 'invisible' }, texte),
        el('span', { class: 'cherche-ico', 'aria-hidden': 'true', html: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="7" cy="7" r="4.6"/><path d="m10.5 10.5 3.6 3.6"/></svg>' }),
        input, statut
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

  /* ── Accueil ──────────────────────────────────────────────────── */

  function carteRubrique(r) {
    var n = ressourcesDe(r).length;
    var themes = r.themes.filter(function (t) { return t.nom; });
    var infos = [r.niveau, n ? pluriel(n, 'ressource', 'ressources') : 'à venir'].filter(Boolean).join(', ');
    return el('section', { class: 'noeud' + (n ? '' : ' est-vide'), style: '--hl:' + r.couleur }, [
      el('p', { class: 'noeud-meta' }, infos),
      el('h2', null, el('a', { class: 'noeud-nom', href: urlRubrique(r) }, r.nom)),
      r.presentation ? el('p', { class: 'noeud-texte', html: mettreEnForme(r.presentation) }) : null,
      themes.length ? el('ul', { class: 'themes-mini' }, themes.map(function (t) {
        return el('li', null, el('a', {
          href: urlRubrique(r, t.id),
          class: compterTheme(t) ? null : 'est-vide',
          style: '--hl:' + t.couleur
        }, t.court));
      })) : null
    ]);
  }

  function pageAccueil(racine) {
    document.title = titreSite();
    racine.appendChild(barreHaut(null));

    var page = el('div', { class: 'page' });
    racine.appendChild(page);

    var recherche = champRecherche('Chercher une ressource', maj);
    page.appendChild(el('header', { class: 'hero', style: '--hl:#22D3EE', html: scene('#22D3EE', 11) }));
    var hero = page.lastChild;
    hero.appendChild(el('div', { class: 'hero-contenu' }, [
      el('p', { class: 'invite', 'aria-hidden': 'true' }, '~/ressources'),
      el('h1', null, titreSite()),
      reglagesSite.presentation ? el('p', { class: 'chapo', html: mettreEnForme(reglagesSite.presentation) }) : null,
      recherche.bloc
    ]));

    var alerte = blocAlertes(null);
    if (alerte) page.appendChild(alerte);

    var vue = el('main', { id: 'contenu' });
    page.appendChild(vue);

    var toutes = [];
    ordreRubriques().forEach(function (r) { toutes = toutes.concat(ressourcesDe(r)); });

    function maj(q) {
      vider(vue);
      var filtre = filtreRecherche(q);
      if (!filtre) {
        recherche.statut.textContent = '';
        vue.appendChild(el('div', { class: 'noeuds' }, ordreRubriques().map(carteRubrique)));
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

    page.appendChild(el('footer', { class: 'pied' }, [
      el('h2', null, 'Ajouter une ressource'),
      el('p', null, 'Chaque rubrique a sa liste dans un petit fichier texte de son dossier. On y ajoute un lien vers une ressource en ligne, ou vers un fichier (PDF, fiche, diaporama) déposé dans le dossier de la rubrique. Le lien « Modifier la liste » se trouve en bas de chaque rubrique.'),
      depotSite ? el('p', { class: 'actions' }, el('a', { href: urlDepot() + '#readme' }, 'Mode d\'emploi complet')) : null,
      mentions()
    ]));
  }

  /* ── Page d'une rubrique ──────────────────────────────────────── */

  function referenceProgramme(rub) {
    var p = typeof rub.programme === 'string' ? { texte: rub.programme } : rub.programme;
    var info = p.lien ? analyser(p.lien, rub.base) : null;
    return el('p', { class: 'reference' }, [
      el('span', { class: 'reference-titre' }, 'Texte officiel'), ' ',
      info ? lienVers(info, p.texte) : p.texte
    ]);
  }

  function pageRubrique(racine, rub) {
    document.title = rub.nom + ' – ' + titreSite();
    racine.appendChild(barreHaut(rub));

    var page = el('div', { class: 'page' });
    racine.appendChild(page);

    var nommes = rub.themes.filter(function (t) { return t.nom; });
    var total = ressourcesDe(rub).length;
    var graine = rub.id.split('').reduce(function (a, c) { return a + c.charCodeAt(0); }, 0);

    var bandeau = el('header', { class: 'hero hero-rubrique', style: '--hl:' + rub.couleur, html: scene(rub.couleur, graine) });
    bandeau.appendChild(el('div', { class: 'hero-contenu' }, [
      el('p', { class: 'invite', 'aria-hidden': 'true' }, '~/ressources/' + rub.id),
      el('h1', null, rub.nom),
      rub.niveau ? el('p', { class: 'niveau' }, rub.niveau) : null
    ]));
    page.appendChild(bandeau);

    var intro = el('div', { class: 'intro' }, [
      rub.presentation ? el('p', { class: 'chapo', html: mettreEnForme(rub.presentation) }) : null,
      rub.programme ? referenceProgramme(rub) : null
    ]);
    if (intro.childNodes.length) page.appendChild(intro);

    var alerte = blocAlertes([rub.id + '/ressources.js', 'reglages.js']);
    if (alerte) page.appendChild(alerte);

    var corps = el('div', { class: 'rub-corps' });
    var cote = el('aside', { class: 'cote' });
    var main = el('main', { id: 'contenu' });
    var zone = el('div', { class: 'zone' });
    var recherche = null;
    var details = nommes.length > 1 ? sommaire(nommes) : null;

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
      recherche = champRecherche('Chercher dans cette rubrique', rendre);
      cote.appendChild(recherche.bloc);
    }
    if (details) cote.appendChild(details);
    if (cote.childNodes.length) corps.appendChild(cote);
    else corps.className += ' sans-cote';

    main.appendChild(zone);
    corps.appendChild(main);
    page.appendChild(corps);
    rendre(recherche ? recherche.input.value.trim() : '');
    suivreLecture(zone, details);

    page.appendChild(el('footer', { class: 'pied' }, [
      el('h2', null, 'Ajouter une ressource'),
      el('p', null, [
        'La liste de cette page est dans ', el('code', null, rub.id + '/ressources.js'),
        '. Pour un PDF ou un autre fichier, le déposer d\'abord dans le dossier ',
        el('code', null, rub.id + '/fichiers'), ', puis l\'ajouter à la liste avec ',
        el('code', null, 'lien: "fichiers/nom-du-fichier.pdf"'), '.'
      ]),
      depotSite ? el('p', { class: 'actions' }, [
        el('a', { href: urlGithub('edit', rub.id + '/ressources.js') }, 'Modifier la liste'),
        el('a', { href: urlGithub('upload', rub.id + '/fichiers') }, 'Déposer un fichier'),
        el('a', { href: urlDepot() + '#readme' }, 'Mode d\'emploi')
      ]) : null,
      mentions()
    ]));
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
