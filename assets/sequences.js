/* ═══════════════════════════════════════════════════════════════
   Les séquences (T153) : les ressources d'une même notion, dans
   l'ordre où la classe les rencontre (cours-quiz, fiches, TD, TP et
   activités, TD type bac, contrôle en terminale).

   Données : « sequences » et « referentiels.sequences » de
   donnees/bibliotheque.json (scripts/construire_bibliotheque.py, à
   partir de donnees/sequences/<id>.json et de
   donnees/referentiels/sequences.json).

   Ce fichier sert aux pages de niveau (assets/site.js : la vue
   « Par séquence » et la page d'une séquence, ?sequence=<id>) et à
   la fiche d'une ressource (assets/bibliotheque.js : « Dans la
   séquence… », avec la ressource d'avant et celle d'après).

   Visibilité : les séquences sont faites pour la classe. Elles ne
   montrent que les documents visibles des élèves ET de l'extérieur
   (un document caché aux élèves porte « cache_eleves » dans
   bibliotheque.json) ; une ressource sans document visible des
   élèves n'y apparaît pas. Une étape sans ressource s'affiche
   « À venir », sans lien : jamais de lien mort.

   Brouillons : une séquence « brouillon » ne s'affiche qu'avec
   ?brouillons dans l'adresse (relecture par l'enseignant·e).

   Le style est PROVISOIRE (feuille STYLE plus bas, injectée une
   fois) : le Designer le reprendra dans assets/style.css, puis la
   feuille d'ici sera retirée.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* Rôles de documents montrés en petits liens sous une ressource, dans une séquence. Les autres (code source, espace
     et guide de l'enseignant·e) restent dans la fiche complète (« En savoir plus ») : une séquence s'adresse aux élèves. */
  var ROLES_COURTS = ['enonce', 'version-pdf', 'version-eleve', 'corrige', 'code-de-depart', 'donnees', 'diaporama',
    'video', 'page', 'complement', 'outil'];
  var MAX_DOCS = 2;     // au-delà : « et N autres documents » vers la fiche
  var LIBELLES = { complements: 'Ailleurs sur le web', secondaire: 'Aussi' };

  function liste(x) { return x == null ? [] : Array.isArray(x) ? x : [x]; }

  function sansAccents(s) { return String(s).normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  /* Une précision en petit (format, site, niveau, étape), précédée d'une vraie espace : lue « files (Terminale) » */
  function typeDe(el, texte) {
    var f = document.createDocumentFragment();
    f.appendChild(document.createTextNode(' '));
    f.appendChild(el('span', { class: 'etape-type' }, texte));
    return f;
  }

  function brouillonsDemandes() {
    try { return new URLSearchParams(location.search).has('brouillons'); } catch (e) { return false; }
  }

  /* ── Le modèle ──────────────────────────────────────────────── */

  /* bib : donnees/bibliotheque.json (ou sa forme pour l'aperçu de l'admin). options.brouillons : montrer les brouillons. */
  function Modele(bib, options) {
    var self = this;
    options = options || {};
    this.brouillons = options.brouillons === undefined ? brouillonsDemandes() : !!options.brouillons;
    this.ref = ((bib && bib.referentiels) || {}).sequences || null;
    this.etapes = {};
    liste(this.ref && this.ref.etapes).forEach(function (e) { self.etapes[e.id] = e; });
    this.libelles = {
      complements: (this.ref && this.ref.libelle_complements) || LIBELLES.complements,
      secondaire: (this.ref && this.ref.libelle_secondaire) || LIBELLES.secondaire
    };
    this.roles = {};
    liste(((bib && bib.referentiels) || {}).valeurs && bib.referentiels.valeurs.roles).forEach(function (r) { self.roles[r.id] = r.libelle; });
    this.niveaux = {};
    liste(((bib && bib.referentiels) || {}).valeurs && bib.referentiels.valeurs.niveaux).forEach(function (n) { self.niveaux[n.id] = n; });
    this.fiches = {};
    liste(bib && bib.ressources).forEach(function (f) { if (f && f.id) self.fiches[f.id] = f; });
    this.liste = liste(bib && bib.sequences).filter(function (s) {
      return s && s.id && (s.statut === 'publiee' || self.brouillons);
    });
    this.parId = {};
    this.liste.forEach(function (s) { self.parId[s.id] = s; });
  }

  Modele.prototype.vide = function () { return !this.liste.length; };

  Modele.prototype.deRubrique = function (rid) {
    return this.liste.filter(function (s) { return s.rubrique === rid; });
  };

  Modele.prototype.libelleEtape = function (type) {
    return (this.etapes[type] || {}).libelle || type;
  };

  /* Ce que voit la classe d'une place : la fiche, ses documents visibles des élèves, le document à ouvrir. null si rien. */
  Modele.prototype.vue = function (place) {
    var f = this.fiches[place.ressource];
    if (!f) return null;
    var docs = liste(f.documents).filter(function (d) { return !d.cache_eleves; });
    if (!docs.length) return null;
    var voulu = typeof place.doc === 'number' ? liste(f.documents)[place.doc] : null;
    var ouvrir = voulu && !voulu.cache_eleves ? voulu
      : docs.filter(function (d) { return d.principal; })[0] || docs[0];
    return { fiche: f, docs: docs, ouvrir: ouvrir, place: place };
  };

  /* Les deux rangs d'une étape : ses ressources, puis les compléments externes (vues seulement) */
  Modele.prototype.rangs = function (etape) {
    var self = this;
    return ['ressources', 'complements'].map(function (champ) {
      return {
        champ: champ,
        vues: liste(etape[champ]).map(function (p) { return self.vue(p); }).filter(Boolean)
      };
    });
  };

  /* La suite des ressources d'une séquence, sans les compléments : pour « avant » et « après » */
  Modele.prototype.suite = function (seq) {
    var self = this, out = [];
    liste(seq.etapes).forEach(function (e) {
      self.rangs(e).forEach(function (r) {
        if (r.champ === 'complements') return;
        r.vues.forEach(function (v) { out.push({ etape: e, champ: r.champ, vue: v }); });
      });
    });
    return out;
  };

  /* Les séquences d'une ressource, la principale d'abord, avec la ressource d'avant et celle d'après */
  Modele.prototype.voisins = function (rid) {
    var self = this, out = [];
    this.liste.forEach(function (s) {
      var suite = self.suite(s);
      var i = -1;
      suite.some(function (x, k) { if (x.vue.fiche.id === rid) { i = k; return true; } return false; });
      var complement = null;
      if (i < 0) {
        liste(s.etapes).some(function (e) {
          return liste(e.complements).some(function (p) { if (p.ressource === rid) { complement = e; return true; } return false; });
        });
        if (!complement || !self.vue({ ressource: rid })) return;
      }
      var ici = i >= 0 ? suite[i] : null;
      var principale = ici ? !ici.vue.place.secondaire : false;
      out.push({
        sequence: s, principale: principale, complement: !ici,
        etape: ici ? ici.etape : complement, champ: ici ? ici.champ : 'complements',
        avant: i > 0 ? suite[i - 1] : null, apres: i >= 0 && i < suite.length - 1 ? suite[i + 1] : null
      });
    });
    out.sort(function (a, b) { return (b.principale ? 1 : 0) - (a.principale ? 1 : 0); });
    return out;
  };

  /* Le texte cherché d'une place (recherche dans la vue « Par séquence ») */
  function texteDe(seq, etapeNom, v) {
    var f = v.fiche;
    return sansAccents([seq.titre, etapeNom, f.titre, f.accroche || '', f.resume || '', liste(f.mots_cles).join(' '),
      v.place.note || ''].join(' ')).toLowerCase();
  }

  /* ── Le rendu ───────────────────────────────────────────────── */

  /* O : les outils de site.js (el, analyser, lienVers, urlBibliotheque…). */
  function Rendu(modele, O) {
    this.m = modele;
    this.O = O;
    stylerUneFois();
  }

  Rendu.prototype.adresse = function (d) {
    return d.url || (d.fichier ? this.O.racine + d.fichier : '');
  };

  /* L'adresse de la page d'une séquence : la page de son niveau, ?sequence=<id> */
  Rendu.prototype.urlSequence = function (seq, absolue) {
    var O = this.O;
    var u = O.racine + (seq.rubrique || '') + '/' + (O.surDisque ? 'index.html' : '') + '?sequence=' + encodeURIComponent(seq.id)
      + (this.m.brouillons ? '&brouillons' : '');
    return absolue ? new URL(u, location.href).href : u;
  };

  Rendu.prototype.lienDoc = function (d, texte, classe) {
    var info = this.O.analyser(this.adresse(d), this.O.racine);
    return info ? this.O.lienVers(info, texte, classe) : this.O.el('span', { class: classe }, texte);
  };

  /* Une ressource dans une étape : son titre (lien principal direct), sa note, quelques documents, « En savoir plus » */
  Rendu.prototype.place = function (v, champ) {
    var O = this.O, el = O.el, self = this, f = v.fiche;
    var secondaire = !!v.place.secondaire;
    var li = el('li', { class: 'etape-res' + (champ === 'complements' ? ' etape-res-complement' : '') + (secondaire ? ' etape-res-secondaire' : '') });
    var titre = el('p', { class: 'etape-titre' });
    if (secondaire) {
      titre.appendChild(el('span', { class: 'etape-aussi', title: 'Rangée surtout dans une autre séquence' }, this.m.libelles.secondaire));
      titre.appendChild(document.createTextNode(' '));
    }
    titre.appendChild(this.lienDoc(v.ouvrir, f.titre, 'titre'));
    var info = O.analyser(this.adresse(v.ouvrir), O.racine);
    var sorte = info ? (info.interne && info.type === 'Sur ce site' ? '' : info.type) : '';
    if (sorte) titre.appendChild(typeDe(el, sorte));
    li.appendChild(titre);
    if (v.place.note) li.appendChild(el('p', { class: 'etape-note' }, v.place.note));

    /* Une place qui vise un document précis (« la feuille sur les piles ») ne montre que lui : les autres documents de la
       fiche appartiennent à d'autres étapes ou d'autres séquences. */
    var autres = typeof v.place.doc === 'number' ? [] : v.docs.filter(function (d) {
      return d !== v.ouvrir && ROLES_COURTS.indexOf(d.role) >= 0 && self.adresse(d);
    });
    var docs = el('p', { class: 'etape-docs' });
    autres.slice(0, MAX_DOCS).forEach(function (d) {
      var nom = d.titre || (self.m.roles && self.m.roles[d.role]) || d.role;
      docs.appendChild(el('span', { class: 'annexe' }, self.lienDoc(d, nom)));
    });
    var reste = typeof v.place.doc === 'number' ? 0 : autres.length - MAX_DOCS;
    docs.appendChild(el('a', { class: 'en-savoir-plus', href: O.urlBibliotheque('?r=' + encodeURIComponent(f.id)) },
      [reste > 0 ? 'et ' + reste + ' autre' + (reste > 1 ? 's' : '') + ' document' + (reste > 1 ? 's' : '') + ' : la fiche' : 'En savoir plus',
        el('span', { class: 'invisible' }, ' sur « ' + f.titre + ' »')]));
    li.appendChild(docs);
    return li;
  };

  /* Une étape : son nom, ses rangs ; « À venir » si elle est vide. filtre(place) : la recherche, facultative. */
  Rendu.prototype.etape = function (seq, e, filtre, niveauTitre) {
    var O = this.O, el = O.el, self = this;
    var nom = this.m.libelleEtape(e.type);
    var rangs = this.m.rangs(e).map(function (r) {
      return { champ: r.champ, vues: filtre ? r.vues.filter(function (v) { return filtre(texteDe(seq, nom, v)); }) : r.vues };
    });
    var n = rangs.reduce(function (a, r) { return a + r.vues.length; }, 0);
    if (filtre && !n) return null;
    var principales = rangs[0].vues.length;
    var li = el('li', { class: 'etape' + (n ? '' : ' est-vide') + (principales ? '' : ' sans-principale'), 'data-etape': e.type });
    li.appendChild(el(niveauTitre || 'h3', { class: 'etape-nom' }, nom));
    var corps = el('div', { class: 'etape-corps' });
    if (!principales) {
      corps.appendChild(el('p', { class: 'vide etape-a-venir' }, 'À venir.'));
    }
    rangs.forEach(function (r) {
      if (!r.vues.length) return;
      var ul = el('ul', { class: 'etape-ressources' }, r.vues.map(function (v) { return self.place(v, r.champ); }));
      if (r.champ === 'ressources') { corps.appendChild(ul); return; }
      corps.appendChild(el('div', { class: 'etape-rang etape-rang-' + r.champ }, [
        el('p', { class: 'etape-sous' }, self.m.libelles.complements), ul
      ]));
    });
    li.appendChild(corps);
    li._n = n;
    return li;
  };

  /* Une séquence dans la vue « Par séquence » d'une page de niveau */
  Rendu.prototype.section = function (seq, filtre) {
    var O = this.O, el = O.el, self = this;
    var titreSeq = filtre && filtre(sansAccents(seq.titre).toLowerCase()) ? null : filtre;
    var etapes = liste(seq.etapes).map(function (e) { return self.etape(seq, e, titreSeq); }).filter(Boolean);
    var n = etapes.reduce(function (a, x) { return a + x._n; }, 0);
    if (filtre && !n && titreSeq) return null;
    var s = el('section', { class: 'theme sequence', id: 'seq-' + seq.id, 'aria-labelledby': 'seq-' + seq.id + '-titre' });
    s.appendChild(el('h2', { id: 'seq-' + seq.id + '-titre' }, el('span', { class: 'surligne' }, seq.titre)));
    if (seq.statut !== 'publiee') s.appendChild(this.noteBrouillon(seq));
    s.appendChild(el('p', { class: 'sequence-objectif' }, seq.objectif));
    var pre = this.prerequis(seq, true);
    if (pre) s.appendChild(pre);
    s.appendChild(el('p', { class: 'sequence-lien' }, el('a', { href: this.urlSequence(seq) },
      ['Page de la séquence, avec son lien et son QR code pour la classe', el('span', { class: 'invisible' }, ' : ' + seq.titre)])));
    s.appendChild(el('ol', { class: 'etapes', 'aria-label': 'Les étapes, dans l\'ordre' }, etapes));
    s._n = n;
    return s;
  };

  /* « À voir avant : … » (décision du 25/11, 10:50). Sur la page de niveau, un lien vers la séquence plus haut ou plus
     bas dans la page ; ailleurs, vers sa page. Une séquence absente (brouillon caché) est nommée sans lien. */
  Rendu.prototype.prerequis = function (seq, surPageNiveau) {
    var el = this.O.el, self = this;
    var ids = liste(seq.prerequis);
    if (!ids.length) return null;
    var p = el('p', { class: 'sequence-prerequis' }, el('span', { class: 'etape-sous' }, 'À voir avant'));
    ids.forEach(function (id, i) {
      var q = self.m.parId[id];
      p.appendChild(document.createTextNode(i ? ' · ' : ' '));
      if (!q) { p.appendChild(el('span', null, id)); return; }
      var ici = surPageNiveau && q.rubrique === seq.rubrique;
      p.appendChild(el('a', { href: ici ? '#seq-' + q.id : self.urlSequence(q) }, q.titre));
    });
    return p;
  };

  Rendu.prototype.noteBrouillon = function (seq) {
    var el = this.O.el;
    return el('p', { class: 'note sequence-brouillon' }, [el('strong', null, 'Brouillon'),
      seq.exemple ? ' : séquence d\'exemple, à remplacer. ' : ' : ',
      'Elle n\'est pas montrée sur le site tant qu\'elle n\'est pas publiée.']);
  };

  Rendu.prototype.compter = function (seq) {
    var self = this;
    return liste(seq.etapes).reduce(function (a, e) {
      return a + self.m.rangs(e).reduce(function (b, r) { return b + r.vues.length; }, 0);
    }, 0);
  };

  /* La page d'une séquence (?sequence=<id>) : les étapes en titres de niveau 2, puis le partage avec la classe */
  Rendu.prototype.page = function (seq, rub) {
    var O = this.O, el = O.el, self = this;
    var main = el('div', { class: 'sequence-page' });
    main.appendChild(el('p', { class: 'retour' }, el('a', { href: O.urlRubrique(rub) + (this.m.brouillons ? '?brouillons' : '') },
      '← Toutes les séquences de ' + rub.nom)));
    if (seq.statut !== 'publiee') main.appendChild(this.noteBrouillon(seq));
    main.appendChild(el('p', { class: 'chapo sequence-objectif' }, seq.objectif));
    var pre = this.prerequis(seq, false);
    if (pre) main.appendChild(pre);
    main.appendChild(el('ol', { class: 'etapes etapes-page', 'aria-label': 'Les étapes, dans l\'ordre' },
      liste(seq.etapes).map(function (e) { return self.etape(seq, e, null, 'h2'); })));
    main.appendChild(this.partage(seq));
    return main;
  };

  /* Le lien pour la classe : l'adresse, son QR code, copier, imprimer */
  Rendu.prototype.partage = function (seq) {
    var O = this.O, el = O.el;
    var url = this.urlSequence(seq, true).replace(/[?&]brouillons(?=&|$)/, '');
    var qr = el('span', { class: 'qr sequence-qr', 'aria-hidden': 'true' });
    var statut = el('p', { class: 'statut', 'aria-live': 'polite' });
    var copier = el('button', { type: 'button', class: 'bouton-annales' }, 'Copier le lien');
    copier.addEventListener('click', function () {
      function fait(ok) { statut.textContent = ok ? 'Lien copié.' : 'Copie impossible : sélectionner le lien ci-dessus.'; }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { fait(true); }, function () { fait(false); });
      else fait(false);
    });
    var imprimer = el('button', { type: 'button', class: 'bouton-annales' }, 'Imprimer la séquence');
    imprimer.addEventListener('click', function () { window.print(); });
    var bloc = el('section', { class: 'sequence-partage', 'aria-labelledby': 'partage-titre' }, [
      el('h2', { id: 'partage-titre' }, 'Pour la classe'),
      el('div', { class: 'sequence-partage-corps' }, [
        qr,
        el('div', null, [
          el('p', { class: 'petit' }, 'À projeter ou à coller dans le cahier : le QR code ouvre cette page sur un téléphone.'),
          el('p', { class: 'sequence-url' }, el('a', { href: url }, url)),
          el('p', { class: 'actions-feuille' }, [copier, imprimer]),
          statut
        ])
      ])
    ]);
    chargerQR(O, function () {
      try {
        var q = window.qrcode(0, 'M');
        q.addData(url);
        q.make();
        qr.innerHTML = q.createSvgTag({ cellSize: 2, margin: 2, scalable: true });
      } catch (e) { qr.hidden = true; }
    }, function () { qr.hidden = true; });
    return bloc;
  };

  /* Le bloc « Dans la séquence » de la fiche d'une ressource (bibliothèque) ; null si elle n'est dans aucune séquence */
  Rendu.prototype.blocFiche = function (rid, lienFiche) {
    var O = this.O, el = O.el, self = this;
    var vs = this.m.voisins(rid);
    if (!vs.length) return null;
    var bloc = el('nav', { class: 'fiche-sequences', 'aria-label': vs.length > 1 ? 'Les séquences de cette ressource' : 'La séquence de cette ressource' });
    vs.forEach(function (v, i) {
      var s = v.sequence;
      var niv = self.m.niveaux[s.niveau];
      var p = el('p', { class: 'fiche-sequence-titre' }, [
        el('span', { class: 'etape-sous' }, i === 0 && v.principale ? 'Dans la séquence' : 'Aussi dans'), ' ',
        el('a', { href: self.urlSequence(s) }, s.titre),
        niv ? typeDe(el, '(' + niv.libelle + ')') : null,
        ', étape ', el('strong', null, self.m.libelleEtape(v.etape.type)
          + (v.champ === 'complements' ? ' (' + self.m.libelles.complements.toLowerCase() + ')' : ''))
      ]);
      var div = el('div', { class: 'fiche-sequence' }, p);
      var voisins = [];
      [['avant', 'Avant'], ['apres', 'Après']].forEach(function (x) {
        var w = v[x[0]];
        if (!w) return;
        voisins.push(el('li', null, [
          el('span', { class: 'etape-sous' }, x[1]), ' ',
          lienFiche(w.vue.fiche),
          typeDe(el, '(' + self.m.libelleEtape(w.etape.type) + ')')
        ]));
      });
      if (voisins.length) div.appendChild(el('ul', { class: 'fiche-voisins' }, voisins));
      bloc.appendChild(div);
    });
    return bloc;
  };

  /* ── Le QR code : assets/qrcode-generator.js, chargé à la demande ── */
  var qrEnCours = null;
  function chargerQR(O, ok, ko) {
    if (typeof window.qrcode === 'function') return ok();
    if (!qrEnCours) {
      qrEnCours = new Promise(function (resoudre, rejeter) {
        var s = document.createElement('script');
        s.src = O.racine + 'assets/qrcode-generator.js';
        s.onload = resoudre;
        s.onerror = rejeter;
        document.head.appendChild(s);
      });
    }
    qrEnCours.then(ok, ko);
  }

  /* ── Le style PROVISOIRE, à reprendre par le Designer dans assets/style.css ──
     Il n'emploie que les variables de la palette commune (--td-*) : clair, obscur et impression suivent. */
  var STYLE = [
    '.vues-rubrique{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem 1rem;margin:0 0 1.2rem}',
    '.vues-rubrique .mode-btn{font-size:.85rem;min-height:2.25rem}',
    '.vues-rubrique .vues-nom{font:700 .75rem/1 var(--td-mono);text-transform:uppercase;letter-spacing:.04em}',
    '.sequence-objectif{margin:-.2rem 0 .5rem;max-width:46em}',
    '.sequence-lien{margin:0 0 .9rem;font-size:.92rem}',
    '.sequence-prerequis{margin:0 0 .4rem;font-size:.92rem}',
    '.sequence-lien a{font-weight:700}',
    '.etapes{list-style:none;margin:0;padding:0;border-left:2px solid var(--td-encre)}',
    '.etape{position:relative;display:grid;grid-template-columns:10.5rem minmax(0,1fr);gap:.2rem 1.2rem;padding:.6rem 0 .7rem 1.1rem;border-top:1px solid var(--td-trait)}',
    '.etape:first-child{border-top:0}',
    '.etape::before{content:"";position:absolute;left:-7px;top:.95rem;width:12px;height:12px;background:var(--td-encre);border:2px solid var(--td-encre)}',
    '.etape.sans-principale::before{background:var(--td-fond);border-style:dashed}',
    '.theme .etape-nom,.etape-nom{display:block;margin:.1rem 0 0;font:700 .82rem/1.35 var(--td-mono);text-transform:uppercase;letter-spacing:.04em}',
    '.theme .etape-nom::before{content:none}',
    '.etapes-page .etape-nom{font-size:.9rem;border:0;box-shadow:none;padding:0}',
    '.etape-corps{min-width:0}',
    '.etape-a-venir{margin:.05rem 0 0;font-style:italic}',
    '.etape-ressources{list-style:none;margin:0;padding:0}',
    '.etape-res{padding:.1rem 0 .45rem}',
    '.etape-res + .etape-res{border-top:1px dotted var(--td-trait);padding-top:.45rem}',
    '.etape-titre{margin:0;line-height:1.35}',
    '.etape-titre .titre{font-weight:700;color:var(--td-encre);text-decoration-thickness:1px}',
    '.etape-titre .titre:hover{text-decoration-thickness:2px;text-decoration-color:var(--td-neon-2)}',
    '.etape-type{display:inline-block;max-width:100%;overflow-wrap:anywhere;font:400 .76rem var(--td-mono);color:var(--td-encre-douce)}',
    '.etape-note{margin:.1rem 0 0;font-size:.9rem;color:var(--td-encre-douce)}',
    '.etape-docs{display:flex;flex-wrap:wrap;align-items:baseline;gap:.3rem .5rem;margin:.3rem 0 0;font-size:.88rem}',
    '.etape-docs .annexe{flex-wrap:nowrap;max-width:100%;font-size:.84rem;padding:.08rem .4rem}',
    '.etape-docs .annexe > a{min-width:0;overflow-wrap:anywhere}',
    '.etape-aussi{display:inline-block;font:700 .7rem/1.3 var(--td-mono);text-transform:uppercase;letter-spacing:.04em;padding:0 .3rem;border:1px dashed var(--td-encre);vertical-align:.1em}',
    '.etape-rang{margin:.2rem 0 .4rem}',
    '.etape-rang-complements{margin-top:.4rem;padding-top:.35rem;border-top:1px dashed var(--td-trait);font-size:.92rem}',
    '.etape-rang-complements .etape-titre .titre{font-weight:400}',
    '.etape-sous{margin:0 0 .15rem;font:700 .72rem/1.3 var(--td-mono);text-transform:uppercase;letter-spacing:.04em;color:var(--td-encre-douce)}',
    'span.etape-sous{margin:0}',
    '.sequence-brouillon{max-width:46em}',
    '.sequence-page .retour{margin:0 0 .4rem}',
    '.sequence-page .chapo{margin-bottom:1rem}',
    '.sequence-partage{margin:2rem 0 0;padding:.8rem 1rem 1rem;border:var(--td-trait-ep) solid var(--td-encre)}',
    '.sequence-partage h2{margin:0 0 .5rem;font-size:1.3rem;text-transform:uppercase}',
    '.sequence-partage-corps{display:flex;flex-wrap:wrap;gap:1rem 1.4rem;align-items:flex-start}',
    '.sequence-partage-corps > div{flex:1 1 16rem;min-width:0}',
    '.sequence-qr{width:8.5rem;height:8.5rem;padding:.3rem;background:#FFFFFF;border:1px solid var(--td-encre)}',
    '.sequence-qr svg{display:block;width:100%;height:100%}',
    '.sequence-url{margin:.3rem 0 .6rem;font:400 .85rem/1.4 var(--td-mono);overflow-wrap:anywhere}',
    '.fiche-sequences{margin:1rem 0 .4rem;border-left:4px solid var(--td-encre);padding:.15rem 0 .15rem .8rem}',
    '.fiche-sequence + .fiche-sequence{margin-top:.6rem;padding-top:.5rem;border-top:1px dotted var(--td-trait)}',
    '.fiche-sequence-titre{margin:0}',
    '.fiche-sequence-titre a{font-weight:700}',
    '.fiche-voisins{list-style:none;margin:.3rem 0 0;padding:0;display:flex;flex-wrap:wrap;gap:.2rem 1.4rem;font-size:.92rem}',
    '@media (max-width:680px){.etape{grid-template-columns:minmax(0,1fr);gap:.15rem;padding-left:.9rem}.sequence-qr{width:7rem;height:7rem}}',
    '@media print{.vues-rubrique,.sequence-lien,.sequence-page .retour,.sequence-partage .actions-feuille,.sequence-partage .statut,.etape-docs{display:none!important}',
    '.etape{break-inside:avoid}.sequence-partage{break-inside:avoid;border-width:1px}.sequence-qr{width:28mm;height:28mm}',
    '.etape-titre .titre::after{content:""}}'
  ].join('\n');

  function stylerUneFois() {
    if (document.getElementById('sequences-provisoire')) return;
    var s = document.createElement('style');
    s.id = 'sequences-provisoire';
    s.textContent = STYLE;
    document.head.appendChild(s);
  }

  window.Sequences = { Modele: Modele, Rendu: Rendu, brouillonsDemandes: brouillonsDemandes, texteDe: texteDe };
})();
