/* ═══════════════════════════════════════════════════════════════
   Le moteur du site.

   Rien à modifier ici pour ajouter une ressource : chaque rubrique a
   sa liste dans son propre dossier (snt/ressources.js, pp/ressources.js…)
   et les réglages généraux sont dans reglages.js, à la racine.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* T126b : plus de couleur par rubrique ni par thème (style « Signal pirate », validé le 21/11).
     Le champ « couleur » de la vitrine et des anciennes listes est accepté, mais n'est plus lu. */

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
  var nbRessources = null; // les ressources de la bibliothèque vues de l'extérieur (repère du bandeau de l'accueil)
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
      puce: infos.puce || '',
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
      rub.themes.push({ nom: null, court: null, id: 'ressources', programme: [], blocs: [{ groupe: null, ressources: [] }] });
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

  /* Les rubriques et l'accueil lisent la vitrine et les fiches de la bibliothèque (T51b) :
     donnees/bibliotheque.json, construit à chaque publication par « Publier le site ». Ce que
     l'enseignant compose dans l'admin s'affiche donc tel quel. Les anciennes listes
     (snt/ressources.js…) restent dans le dépôt, mais ne sont plus lues. */
  var BIBLIOTHEQUE = 'donnees/bibliotheque.json';

  window.reglages = function (r) {
    reglagesSite = r || {};
    depotSite = lireDepot(reglagesSite.depot);
    if (apercu()) return quandPret(afficher);
    var ici = pageAPart() ? null : rubriqueDeLaPage();

    function sansDonnees(message) {
      signaler(BIBLIOTHEQUE, message);
      if (ici && !rubriques[ici]) nouvelleRubrique({ id: ici, base: RACINE + ici + '/' }, {});
      quandPret(afficher);
    }

    if (typeof fetch !== 'function') return sansDonnees('ce navigateur est trop ancien pour lire la bibliothèque.');
    fetch(RACINE + BIBLIOTHEQUE).then(function (rep) {
      if (!rep.ok) throw new Error('code ' + rep.status);
      return rep.json();
    }).then(function (b) {
      var refs = b.referentiels || {};
      var r2 = rubriquesDeVitrine({ vitrine: b.vitrine, ressources: b.ressources, programmes: refs.programmes, valeurs: refs.valeurs });
      nbRessources = liste(b.ressources).length;
      rubriques = r2.rubriques;
      reglagesSite.rubriques = r2.ordre;
      if (ici && !rubriques[ici]) {
        signaler(BIBLIOTHEQUE, 'la rubrique « ' + ici + ' » n\'est pas dans la vitrine (donnees/vitrine.json).');
        nouvelleRubrique({ id: ici, base: RACINE + ici + '/' }, {});
      }
      quandPret(afficher);
    }).catch(function (e) {
      sansDonnees(SUR_DISQUE
        ? 'la bibliothèque ne se lit pas depuis un fichier ouvert sur le disque : lancer un petit serveur (python3 -m http.server) à la racine du site.'
        : 'la liste des ressources n\'a pas pu être lue (' + e.message + '). Recharger la page ; si le message reste, la publication du site a peut-être échoué.');
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
    if (typeof options !== 'object' || !options) options = {}; // theme("…", "vert") : la couleur n'est plus lue
    var court = options.court || nom;
    var id = slug(court), base = id, k = 2;
    while (rub.themes.some(function (t) { return t.id === id; })) id = base + '-' + (k++);
    rub.themes.push({
      nom: nom,
      court: court,
      id: id,
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

  /* ── Les rubriques tirées de la vitrine (donnees/vitrine.json) ─── */
  /* La vitrine (cahier des charges, § 3.4) et les fiches de la bibliothèque donnent les mêmes rubriques
     que les anciennes listes ressources.js : thèmes, groupes, ressources. Les rubriques, l'accueil
     et l'aperçu de l'admin s'en servent (T51, T51b).
     donnees : { vitrine, ressources: [fiches vues de l'extérieur], programmes: [], valeurs: {} },
     la forme de donnees/bibliotheque.json (referentiels.programmes et referentiels.valeurs). */
  /* Les étiquettes montrées sous une ressource : celles des anciennes listes, tirées de la fiche,
     avec leur libellé d'alors (décision du 17/11 : même aspect qu'avant la bascule). Les autres
     usages (en autonomie, éditeur de code…) restent dans la fiche et dans les filtres de la bibliothèque. */
  var ETIQUETTES = [
    ['usages', 'en-ligne', 'En ligne'], ['usages', 'a-imprimer', 'À imprimer'], ['usages', 'debranche', 'Débranché'],
    ['usages', 'compte-ent', 'Connexion ENT'], ['types', 'cours', 'Cours'], ['types', 'jeu', 'Jeu'],
    ['langages', 'python', 'Python'], ['langages', 'sql', 'SQL'], ['formats', 'notebook', 'Notebook'],
    ['usages', 'sans-installation', 'Rien à installer'],
    ['usages', 'pour-aller-plus-loin', 'Pour aller plus loin'], ['usages', 'a-adapter', 'À adapter']
  ];
  /* Décision de l'enseignant du 18/11 (T85) : « Cours » (type), « Notebook » et « Rien à installer » (usage
     « sans-installation ») s'ajoutent. « Notebook » : un des documents montrés a le format « notebook »
     (déduit à la construction de la bibliothèque) ; une activité Capytale dont le document principal est
     la page de lecture reste un notebook. */
  function valeursEtiquette(f, champ, formats) {
    if (champ === 'formats') {
      // une fiche modifiée dans l'admin (aperçu) n'a pas encore son format : il se déduit comme à la construction
      return liste(f.documents).map(function (d) { return d.format || deduireFormat(d, formats); });
    }
    return liste(f[champ]);
  }

  /* Le format d'un document, par les règles du référentiel (valeurs.json, « formats » : motifs, hôtes,
     extensions, format par défaut), comme deduire_format de scripts/valider_donnees.py */
  function deduireFormat(d, formats) {
    formats = liste(formats);
    var cible = String(d.url || d.fichier || '');
    var hote = '', chemin;
    if (d.url) {
      try {
        var u = new URL(cible);
        hote = u.hostname.toLowerCase().replace(/^www\./, '');
        chemin = u.pathname;
      } catch (e) { chemin = ''; }
    } else {
      chemin = cible.split(/[#?]/)[0];
    }
    var i, f;
    for (i = 0; i < formats.length; i++) {
      f = formats[i];
      if (liste(f.motifs).some(function (m) { try { return new RegExp(m).test(cible); } catch (e) { return false; } })) return f.id;
    }
    if (hote) {
      for (i = 0; i < formats.length; i++) if (liste(formats[i].hotes).indexOf(hote) >= 0) return formats[i].id;
    }
    var dernier = chemin.replace(/\/+$/, '').split('/').pop();
    if (dernier.indexOf('.') >= 0 && !/\/$/.test(chemin)) {
      var ext = dernier.split('.').pop().toLowerCase();
      for (i = 0; i < formats.length; i++) if (liste(formats[i].extensions).indexOf(ext) >= 0) return formats[i].id;
    }
    for (i = 0; i < formats.length; i++) if (formats[i].par_defaut) return formats[i].id;
    return null;
  }
  window.deduireFormatDocument = deduireFormat; // pour le test de parité avec le script (test_admin_donnees.js)


  /* La puce de niveau d'une rubrique (accueil, bandeau) : celle de la vitrine (« puce », facultatif),
     sinon tirée de son programme ou de son texte de référence ; « Tous » pour une rubrique sans niveau. */
  function puceDe(programme) {
    var p = String(programme || '');
    if (/^snt/.test(p)) return 'SNT';
    if (/^nsi-1re|^nsi-premiere/.test(p)) return '1re';
    if (/^nsi-tle|^nsi-terminale/.test(p)) return 'Tle';
    if (/^pp/.test(p)) return 'PP';
    return 'Tous';
  }

  /* Une ressource est un cours-quiz (cadre et étiquette « Cours-quiz ») si sa fiche le dit : le type
     « cours-quiz » (à créer dans le référentiel, après validation) ou, en attendant, le mot-clé « cours-quiz ».
     Jamais d'après le titre. */
  var COURS_QUIZ = 'cours-quiz';
  function estCoursQuiz(f) {
    if (!f) return false;
    if (liste(f.types).indexOf(COURS_QUIZ) >= 0 || liste(f.usages).indexOf(COURS_QUIZ) >= 0) return true;
    return liste(f.mots_cles).some(function (m) { return String(m).trim().toLowerCase() === COURS_QUIZ; });
  }

  function rubriquesDeVitrine(donnees) {
    var fiches = {};
    liste(donnees.ressources).forEach(function (f) { if (f && f.id) fiches[f.id] = f; });
    var noeuds = {};
    liste(donnees.programmes).forEach(function (p) {
      noeuds[p.id] = p;
      liste(p.themes).forEach(function (t) {
        noeuds[t.id] = t;
        liste(t.contenus).forEach(function (c) { noeuds[c.id] = c; });
      });
    });
    var valeurs = donnees.valeurs || {};
    function libelle(listeNom, id) {
      var e = liste(valeurs[listeNom]).filter(function (x) { return x.id === id; })[0];
      return e ? e.libelle : id;
    }
    function adresse(d) {
      return d.url || (d.fichier ? RACINE + d.fichier : '');
    }
    function versRessource(id, t, groupe, rub) {
      var f = fiches[id];
      if (!f) return null; // cachée pour l'extérieur, ou fiche absente
      var docs = liste(f.documents);
      var principal = docs.filter(function (d) { return d.principal; })[0] || docs[0];
      var annexes = null;
      docs.forEach(function (d) {
        if (d === principal || !adresse(d)) return;
        annexes = annexes || {};
        var nom = d.titre || libelle('roles', d.role), k = 2, base = nom;
        while (annexes[nom]) nom = base + ' (' + (k++) + ')';
        annexes[nom] = adresse(d);
      });
      var tags = etiquettesUne[f.id] ? [etiquettesUne[f.id]] : [];
      ETIQUETTES.forEach(function (e) {
        if (valeursEtiquette(f, e[0], valeurs.formats).indexOf(e[1]) >= 0) tags.push(e[2]);
      });
      return {
        id: f.id, titre: f.titre, lien: principal ? adresse(principal) : '', texte: f.accroche || f.resume || '',
        tags: tags, annexes: annexes, theme: t, groupe: groupe, rubrique: rub, coursQuiz: estCoursQuiz(f)
      };
    }
    /* L'étiquette facultative de « À la une », en tête des étiquettes de la ressource, partout où
       elle s'affiche ; dans ses dates, si la vitrine en donne */
    var etiquettesUne = {};
    var jour = new Date().toISOString().slice(0, 10);
    liste((donnees.vitrine || {}).a_la_une).forEach(function (u) {
      if (!u || !u.etiquette || (u.debut && u.debut > jour) || (u.fin && u.fin < jour)) return;
      etiquettesUne[u.ressource] = u.etiquette;
    });
    var faites = {};
    var ordre = [];
    liste((donnees.vitrine || {}).rubriques).forEach(function (rv) {
      var prog = rv.programme ? noeuds[rv.programme] : null;
      var ref = rv.reference_officielle ? noeuds[rv.reference_officielle] : null;
      var texte = prog || ref;
      var rub = {
        id: rv.id, base: RACINE + rv.id + '/', nom: rv.titre, court: rv.court || rv.titre, niveau: rv.niveau || '',
        presentation: rv.presentation || '',
        programme: texte && texte.texte_officiel ? { texte: texte.texte_officiel.titre, lien: texte.texte_officiel.lien } : null,
        puce: rv.puce || puceDe(rv.programme || rv.reference_officielle || ''), themes: []
      };
      liste(rv.sections).forEach(function (s) {
        var n = s.programme ? noeuds[s.programme] : null;
        var nom = n ? n.intitule : s.titre;
        var court = n ? (n.court || n.intitule) : (s.court || s.titre);
        var id = s.id || slug(court), base = id, k = 2;
        while (rub.themes.some(function (x) { return x.id === id; })) id = base + '-' + (k++);
        var t = {
          nom: nom, court: court, id: id,
          /* « Au programme » : les contenus du thème ; pour une section libre, les titres de ses sous-sections
             sans ressource (Professeur principal › Orientation), comme dans les anciennes listes */
          programme: n ? liste(n.contenus).map(function (c) { return c.intitule; })
            : liste(s.sous_sections).filter(function (ss) { return !ss.programme && ss.titre && !liste(ss.ressources).length; })
              .map(function (ss) { return ss.titre; }),
          blocs: [{ groupe: null, ressources: [] }]
        };
        function remplir(bloc, ids) {
          liste(ids).forEach(function (rid) {
            var r = versRessource(rid, t, bloc.groupe, rub);
            if (r) bloc.ressources.push(r);
          });
        }
        remplir(t.blocs[0], s.ressources);
        liste(s.sous_sections).forEach(function (ss) {
          var c = ss.programme ? noeuds[ss.programme] : null;
          var bloc = { groupe: c ? c.intitule : ss.titre, ressources: [] };
          t.blocs.push(bloc);
          remplir(bloc, ss.ressources);
        });
        rub.themes.push(t);
      });
      faites[rv.id] = rub;
      ordre.push(rv.id);
    });
    return { rubriques: faites, ordre: ordre };
  }

  /* L'aperçu de l'admin : …/snt/?apercu ou …/?apercu, avec la vitrine et les fiches que l'admin
     a rangées dans sessionStorage (clé « apercu-admin »). Rien n'est enregistré. */
  var donneesApercu;
  function apercu() {
    if (donneesApercu !== undefined) return donneesApercu;
    donneesApercu = null;
    try {
      if (!/[?&]apercu(=|&|$)/.test(location.search)) return null;
      var d = JSON.parse(sessionStorage.getItem('apercu-admin') || 'null');
      if (!d || !d.vitrine) return null;
      var r = rubriquesDeVitrine(d);
      nbRessources = liste(d.ressources).length;
      rubriques = r.rubriques;
      reglagesSite.rubriques = r.ordre;
      donneesApercu = d;
    } catch (e) { donneesApercu = null; }
    return donneesApercu;
  }

  function bandeauApercu() {
    return el('div', { class: 'alerte apercu', role: 'note' }, [
      el('p', null, el('strong', null, 'Aperçu de l\'admin')),
      el('p', { class: 'petit' }, 'Cette page montre les changements en attente : ils ne sont pas encore enregistrés, et le site en ligne ne les montre pas.')
    ]);
  }

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

  /* Une page qui n'est pas une rubrique (la bibliothèque) : <div id="site" data-page="…"> */
  function pageAPart() {
    var s = document.getElementById('site');
    return s ? s.getAttribute('data-page') : null;
  }

  /* La bibliothèque, avec une recherche ou des filtres (« ?q=boucle ») */
  function urlBibliotheque(requete) {
    return RACINE + 'bibliotheque/' + (SUR_DISQUE ? 'index.html' : '') + (requete || '');
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
    { nom: 'CC BY-SA 4.0', quoi: 'documents', court: 'documents', lien: 'https://creativecommons.org/licenses/by-sa/4.0/deed.fr' },
    { nom: 'MIT', quoi: 'code des applications', court: 'code', lien: 'https://opensource.org/license/mit' }
  ];
  /* Textes validés par l'enseignant (07/11/2026). reglages.js peut les remplacer ; un texte vide ("") les retire.
     {auteur} est remplacé par le nom de l'auteur. */
  var MENTIONS = {
    auteur: 'Babash - NSI Tani Malandi',
    mention_ia: 'Ces ressources sont conçues par {auteur} ; beaucoup le sont avec l\'aide de l\'IA.',
    reutilisation: 'Tu peux les réutiliser et les modifier en mentionnant {auteur} et la licence ; un document modifié se partage sous la même licence.',
    invitation_ia: 'Si tu utilises l\'IA pour les modifier, merci de le préciser.',
    /* la mention courte de la ligne du pied (décision du 20/11 : « conçu avec l'aide de l'IA », avec le nouveau style) */
    pied_ia: 'conçu avec l\'aide de l\'IA'
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
    /* Les licences et « Code source sur GitHub » sont dans la ligne du pied (piedDePage), à côté de l'auteur */

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
    var li = el('li', { class: 'res' + (r.coursQuiz ? ' res-cours-quiz' : '') });

    /* Le cours-quiz, qui ouvre la séquence (décision du 20/11) : cadre et mot « Cours-quiz » avant le titre */
    if (r.coursQuiz) li.appendChild(etiquetteCoursQuiz());
    li.appendChild(info ? lienVers(info, r.titre, 'titre') : el('span', { class: 'titre sans-lien' }, r.titre));

    if (avecChemin) {
      li.appendChild(el('p', { class: 'chemin' }, [
        el('a', { href: urlRubrique(r.rubrique) }, r.rubrique.nom),
        r.theme.nom ? ', ' : null,
        r.theme.nom ? el('a', { href: urlRubrique(r.rubrique, r.theme.id) }, r.theme.court) : null
      ]));
    }

    /* Décision de l'enseignant du 17/11 : l'accroche, puis « En savoir plus » vers la fiche complète de la
       bibliothèque (ressources tirées de la vitrine). Le lien prend la couleur du texte, souligné ; son nom
       complet, pour les lecteurs d'écran, est « En savoir plus sur <titre> ». */
    if (r.texte || r.id) {
      var texte = el('p', { html: r.texte ? mettreEnForme(r.texte) : null });
      if (r.id) {
        if (r.texte) texte.appendChild(document.createTextNode(' '));
        texte.appendChild(el('a', { class: 'en-savoir-plus', href: urlBibliotheque('?r=' + encodeURIComponent(r.id)) },
          ['En savoir plus', el('span', { class: 'invisible' }, ' sur « ' + r.titre + ' »')]));
      }
      li.appendChild(texte);
    }

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

  /* le mot, suivi d'une espace (lu « Cours-quiz QuizzNSI… », pas « Cours-quizQuizzNSI… ») */
  function etiquetteCoursQuiz() {
    var f = document.createDocumentFragment();
    f.appendChild(el('span', { class: 'etiquette-signal' }, 'Cours-quiz'));
    f.appendChild(document.createTextNode(' '));
    return f;
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
    var s = el('section', { class: 'theme', id: t.id });
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

  /* Les icônes : des caractères de la police « TD Symboles » (assets/fonts/), comme dans les TD */
  var MODES = [
    { id: 'auto', nom: 'Auto', aide: 'Suivre le réglage de l\'appareil', ico: String.fromCharCode(0x25C6) },
    { id: 'light', nom: 'Clair', aide: 'Affichage clair', ico: String.fromCharCode(0x25A1) },
    { id: 'dark', nom: 'Obscur', aide: 'Affichage obscur', ico: String.fromCharCode(0x25A0) }
  ];
  /* La couleur de la barre du navigateur (meta theme-color) : celle du fond, en clair et en obscur */
  var FOND = { light: '#FFFFFF', dark: '#0E0C14' };

  function lireMode() {
    try { return localStorage.getItem('theme') || 'auto'; } catch (e) { return 'auto'; }
  }

  function couleurBarre(m) {
    Array.prototype.forEach.call(document.querySelectorAll('meta[name="theme-color"]'), function (meta) {
      var media = meta.getAttribute('media') || '';
      var propre = /dark/.test(media) ? FOND.dark : FOND.light;
      meta.setAttribute('content', m === 'light' || m === 'dark' ? FOND[m] : propre);
    });
  }

  function appliquerMode(m) {
    var html = document.documentElement;
    if (m === 'light' || m === 'dark') html.setAttribute('data-theme', m);
    else html.removeAttribute('data-theme');
    try {
      if (m === 'light' || m === 'dark') localStorage.setItem('theme', m);
      else localStorage.removeItem('theme');
    } catch (e) { /* navigation privée : le choix vaut pour cette page */ }
    couleurBarre(m);
  }

  function choixMode() {
    var actuel = lireMode();
    couleurBarre(actuel);
    var groupe = el('div', { class: 'mode', role: 'group', 'aria-label': 'Affichage' });
    MODES.forEach(function (m) {
      var b = el('button', {
        type: 'button', class: 'mode-btn', title: m.aide, 'data-theme': m.id,
        'aria-pressed': m.id === actuel ? 'true' : 'false'
      }, [
        el('span', { class: 'mode-ico', 'aria-hidden': 'true' }, m.ico),
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

  /* ── Le bandeau : un paysage de Mayotte des TD (assets/td/), en rotation ──
     Décisions de l'enseignant du 21/11 : 150 px au plus ; les quatre paysages tournent partout (accueil,
     rubriques, bibliothèque, annales, espaces élève et enseignant·e) et changent d'une visite à l'autre :
     chaque page tire un paysage, jamais le même que la page vue juste avant. « ?bandeau=1 » à « 4 » en
     force un (vérifications). Le margouillat vert à turbine se cache à l'une des places prévues pour ce
     paysage (assets/td/places-margouillat.json, écrit par charte/bandeaux-td.py). Rien dans le bandeau
     n'est porteur de sens : le décor est aria-hidden, le titre est le h1 de la page. */
  var NB_BANDEAUX = 4;
  var PLACES = null; // promesse des places du margouillat, chargées une fois

  function numeroBandeau() {
    var force = /[?&]bandeau=([1-4])(&|$)/.exec(location.search);
    if (force) return +force[1];
    var avant = 0;
    try { avant = +localStorage.getItem('bandeau') || 0; } catch (e) { /* sans importance */ }
    var n = 1 + Math.floor(Math.random() * (avant ? NB_BANDEAUX - 1 : NB_BANDEAUX));
    if (avant && n >= avant) n++;
    try { localStorage.setItem('bandeau', String(n)); } catch (e) { /* sans importance */ }
    return n;
  }

  function cacherMargouillat(m, n) {
    if (!PLACES) {
      PLACES = typeof fetch === 'function'
        ? fetch(RACINE + 'assets/td/places-margouillat.json').then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
        : Promise.resolve({});
    }
    PLACES.then(function (toutes) {
      var places = liste(toutes && toutes[String(n)]);
      if (!places.length) return; // sans place connue, il reste caché
      var p = places[Math.floor(Math.random() * places.length)];
      m.style.setProperty('--x', p.x + '%');
      m.style.setProperty('--y', p.y + '%');
      m.style.setProperty('--r', (p.r || 0) + 'deg');
      m.style.setProperty('--l', p.l + '%');
      if (p.s) m.style.setProperty('--s', p.s);
      m.hidden = false;
    });
  }

  /* o : { puce, surTitre: [texte ou nœud…], titre, long (titre long : plus petit), compact,
           repere: { nombre, texte, href } } ; rend <header class="bandeau"> */
  function bandeau(o) {
    o = o || {};
    var n = numeroBandeau();
    var marg = el('span', { class: 'margouillat', hidden: true });
    cacherMargouillat(marg, n);
    var sur = el('p', { class: 'sur-titre' }, o.puce ? el('span', { class: 'puce' }, o.puce) : null);
    liste(o.surTitre).forEach(function (x) {
      if (x == null || x === '') return;
      sur.appendChild(typeof x === 'object' ? x : el('span', null, x));
    });
    var h = el('header', { class: 'bandeau' + (o.compact ? ' compact' : ''), 'data-bandeau': String(n) }, [
      el('div', { class: 'bandeau-decor', 'aria-hidden': 'true' }, marg),
      el('div', { class: 'bandeau-texte' }, [
        sur.childNodes.length ? sur : null,
        el('h1', { class: o.long ? 'long' : null }, el('span', null, o.titre || titreSite()))
      ])
    ]);
    if (o.repere && o.repere.nombre != null) {
      h.appendChild(el(o.repere.href ? 'a' : 'p', { class: 'bandeau-repere', href: o.repere.href || null },
        [el('b', null, String(o.repere.nombre)), o.repere.texte || '']));
    }
    return h;
  }

  /* ── Barre du haut ────────────────────────────────────────────── */

  function barreHaut(active) {
    return el('header', { class: 'barre-haut' }, el('div', { class: 'barre-int' }, [
      el('a', { class: 'marque', href: urlAccueil() }, [
        el('span', { class: 'marque-logo', 'aria-hidden': 'true' }, '>_'),
        el('span', { class: 'marque-nom' }, titreSite())
      ]),
      el('nav', { class: 'nav', 'aria-label': 'Rubriques' }, el('ul', null, ordreRubriques().map(function (r) {
        return el('li', null, el('a', {
          href: urlRubrique(r),
          'aria-current': r === active ? 'page' : null
        }, r.court));
      }).concat(
        /* Toute la bibliothèque, avec ses filtres (cahier des charges, § 2) */
        el('li', null, el('a', {
          href: urlBibliotheque(),
          'aria-current': active === 'bibliotheque' ? 'page' : null
        }, 'Bibliothèque'))
      ))),
      choixMode()
    ]));
  }

  /* Le pied de page commun, compact (T126b) : une ligne (auteur, licences, « Code source sur GitHub »,
     « conçu avec l'aide de l'IA »), puis les mentions. Décisions du 07/11 (licences), du 10/11 (lien vers le
     dépôt) et du 20/11 (mention de l'IA avec le nouveau style). */
  function piedDePage() {
    var nbsp = String.fromCharCode(0xA0);
    var auteur = (mention('auteur') || MENTIONS.auteur).replace(/ - /g, nbsp + '-' + nbsp);
    var ligne = el('p', { class: 'pied-ligne' }, [auteur]);
    LICENCES.forEach(function (l) {
      ligne.appendChild(document.createTextNode(' · ' + l.court + ' '));
      ligne.appendChild(el('a', { href: l.lien, rel: 'license' }, l.nom));
    });
    ligne.appendChild(document.createTextNode(' · '));
    ligne.appendChild(el('a', { href: urlDepot() }, 'Code source sur GitHub'));
    var ia = mention('pied_ia');
    if (ia) ligne.appendChild(document.createTextNode(' · ' + ia));
    return el('footer', { class: 'pied' }, [ligne, mentions()]);
  }

  /* ── Sommaire des thèmes (colonne de gauche sur grand écran) ──── */

  function sommaire(themes) {
    var details = el('details', { class: 'sommaire' }, [
      el('summary', null, ['Thèmes ', el('span', { class: 'nb' }, String(themes.length))]),
      el('ul', null, themes.map(function (t) {
        var nb = compterTheme(t);
        return el('li', null, el('a', {
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
        el('span', { class: 'cherche-ico', 'aria-hidden': 'true' }, '>'),
        input, statut
      ]),
      input: input,
      statut: statut
    };
  }

  function blocAlertes(fichiers) {
    var liste_ = erreurs.filter(function (e) { return !fichiers || fichiers.indexOf(e.fichier) >= 0; });
    if (!liste_.length) return null;
    /* Le titre nomme ce qui est en cause : les réglages (reglages.js), une liste, ou les deux */
    var reglagesEnCause = liste_.some(function (e) { return e.fichier === 'reglages.js'; });
    var listeEnCause = liste_.some(function (e) { return e.fichier !== 'reglages.js'; });
    var bibliothequeEnCause = liste_.some(function (e) { return e.fichier === BIBLIOTHEQUE; });
    var titre = bibliothequeEnCause && !reglagesEnCause ? 'Les ressources n\'ont pas pu s\'afficher'
      : !reglagesEnCause ? 'Une liste de ressources contient une erreur'
      : listeEnCause ? 'Les réglages du site et une liste de ressources contiennent des erreurs'
      : 'Les réglages du site contiennent une erreur';
    return el('div', { class: 'alerte', role: 'alert' }, [
      el('p', null, el('strong', null, titre)),
      el('ul', null, liste_.map(function (e) {
        return el('li', null, [
          el('code', null, e.fichier), e.ligne ? ', ligne ' + e.ligne : '', ' : ', e.message
        ]);
      })),
      /* L'astuce vaut pour une erreur d'écriture, que le navigateur situe à une ligne ;
         pas pour un champ inconnu ni pour le réglage depot, qui n'en ont pas */
      liste_.some(function (e) { return e.ligne; })
        ? el('p', { class: 'petit' }, 'Souvent : une virgule oubliée en fin de ligne, ou un guillemet, une parenthèse ou une accolade pas refermés, juste avant la ligne indiquée.')
        : null
    ]);
  }

  /* ── Accueil ──────────────────────────────────────────────────── */

  function carteRubrique(r) {
    var n = ressourcesDe(r).length;
    var themes = r.themes.filter(function (t) { return t.nom; });
    var infos = [r.niveau, n ? pluriel(n, 'ressource', 'ressources') : 'à venir'].filter(Boolean).join(', ');
    /* T126b : le niveau se lit dans une puce de texte (SNT, 1re, Tle, PP, Tous), plus dans une couleur */
    return el('section', { class: 'noeud' + (n ? '' : ' est-vide') }, [
      el('p', { class: 'noeud-meta' }, [r.puce ? el('span', { class: 'puce' }, r.puce) : null, infos]),
      el('h2', null, el('a', { class: 'noeud-nom', href: urlRubrique(r) }, r.nom)),
      r.presentation ? el('p', { class: 'noeud-texte', html: mettreEnForme(r.presentation) }) : null,
      themes.length ? el('ul', { class: 'themes-mini' }, themes.map(function (t) {
        var vide = !compterTheme(t);
        /* un thème sans ressource : pointillés, et le mot pour les lecteurs d'écran */
        return el('li', null, el('a', { href: urlRubrique(r, t.id), class: vide ? 'est-vide' : null },
          [t.court, vide ? el('span', { class: 'invisible' }, ' (pas encore de ressource)') : null]));
      })) : null
    ]);
  }

  function pageAccueil(racine) {
    document.title = titreSite();
    racine.appendChild(barreHaut(null));

    var page = el('div', { class: 'page' });
    racine.appendChild(page);

    var recherche = champRecherche('Chercher une ressource', maj);
    /* Décision du 21/11 (direction A) : un paysage en haut, qui change d'une visite à l'autre ; à droite, le
       nombre de ressources de la bibliothèque, qui y mène */
    page.appendChild(bandeau({
      puce: reglagesSite.puce || 'SNT · NSI',
      surTitre: [reglagesSite.sur_titre || 'Seconde · Première · Terminale'],
      titre: titreSite(),
      repere: nbRessources ? { nombre: nbRessources, texte: nbRessources > 1 ? 'ressources' : 'ressource', href: urlBibliotheque() } : null
    }));
    page.appendChild(el('div', { class: 'intro' }, [
      reglagesSite.presentation ? el('p', { class: 'chapo', html: mettreEnForme(reglagesSite.presentation) }) : null,
      recherche.bloc
    ]));

    var alerte = blocAlertes(null);
    if (alerte) page.appendChild(alerte);
    if (apercu()) page.insertBefore(bandeauApercu(), page.firstChild);

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
      // La bibliothèque cherche plus loin : synonymes, notions, fautes de frappe, texte des documents, filtres
      vue.appendChild(el('p', { class: 'vers-bibliotheque' }, el('a', { href: urlBibliotheque('?q=' + encodeURIComponent(q)) },
        'Chercher « ' + q + ' » dans toute la bibliothèque, avec ses filtres')));
    }
    maj(recherche.input.value.trim());

    page.appendChild(piedDePage());
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

    page.appendChild(bandeau({
      puce: rub.puce || puceDe(''),
      surTitre: [rub.niveau, total ? pluriel(total, 'ressource', 'ressources') : 'à venir'],
      titre: rub.nom
    }));

    var intro = el('div', { class: 'intro' }, [
      rub.presentation ? el('p', { class: 'chapo', html: mettreEnForme(rub.presentation) }) : null,
      rub.programme ? referenceProgramme(rub) : null
    ]);
    if (intro.childNodes.length) page.appendChild(intro);

    var alerte = blocAlertes([rub.id + '/ressources.js', 'reglages.js', BIBLIOTHEQUE]);
    if (alerte) page.appendChild(alerte);
    if (apercu()) page.insertBefore(bandeauApercu(), page.firstChild);

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

    page.appendChild(piedDePage());
  }

  /* Ce que site.js prête aux pages à part (la bibliothèque, bientôt l'admin) */
  var OUTILS = {
    el: el, vider: vider, liste: liste, pluriel: pluriel, echapper: echapper, mettreEnForme: mettreEnForme,
    sansAccents: sansAccents, slug: slug, analyser: analyser, lienVers: lienVers,
    barreHaut: barreHaut, bandeau: bandeau, piedDePage: piedDePage, blocAlertes: blocAlertes,
    estCoursQuiz: estCoursQuiz, etiquetteCoursQuiz: etiquetteCoursQuiz,
    urlAccueil: urlAccueil, urlRubrique: urlRubrique, urlBibliotheque: urlBibliotheque, urlDepot: urlDepot,
    ordreRubriques: ordreRubriques, titreSite: titreSite, reglages: function () { return reglagesSite; },
    signaler: signaler, racine: RACINE, surDisque: SUR_DISQUE,
    rubriquesDeVitrine: rubriquesDeVitrine, blocRessource: blocRessource, champRecherche: champRecherche
  };

  /* Les pages à part : <div id="site" data-page="…"> et la fonction qui les dessine */
  var PAGES_A_PART = {
    bibliotheque: { fonction: 'pageBibliotheque', nom: 'La bibliothèque', script: 'assets/bibliotheque.js' },
    admin: { fonction: 'pageAdmin', nom: 'L\'espace administrateur', script: 'assets/admin.js' },
    annales: { fonction: 'pageAnnales', nom: 'La page des annales du bac', script: 'assets/annales.js' },
    /* Le compte commun (T101b) : pas encore lié depuis l'accueil, atteignable par son adresse */
    eleve: { fonction: 'pagePlanque', nom: 'Ma planque', script: 'assets/planque.js' },
    enseignant: { fonction: 'pageEnseignant', nom: 'L\'espace enseignant·e', script: 'assets/espace-enseignant.js' }
  };

  function afficher() {
    var racine = document.getElementById('site');
    if (!racine) return;
    vider(racine);
    var aPart = PAGES_A_PART[pageAPart()];
    if (aPart) {
      if (typeof window[aPart.fonction] === 'function') window[aPart.fonction](racine, OUTILS);
      else {
        racine.appendChild(barreHaut(pageAPart()));
        var page = el('div', { class: 'page' });
        page.appendChild(el('div', { class: 'alerte', role: 'alert' }, [
          el('p', null, el('strong', null, aPart.nom + ' n\'a pas pu s\'afficher')),
          el('p', { class: 'petit' }, 'Le programme de la page (' + aPart.script + ') ne s\'est pas chargé. Recharger la page ; '
            + 'si le message reste, le signaler dans les issues du dépôt GitHub.')
        ]));
        page.appendChild(piedDePage());
        racine.appendChild(page);
      }
      return;
    }
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
