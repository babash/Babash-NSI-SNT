/* ═══════════════════════════════════════════════════════════════
   La recherche dans la bibliothèque, sans service externe.

   - Les mots sont ramenés à une forme simple : minuscules, sans
     accents, puis réduits à leur racine par quelques règles légères
     pour le français (pluriels, féminins) : « Boucles » et « boucle »
     se confondent, comme « données » et « donnée ».
   - Le classement suit le modèle BM25F : un mot compte davantage dans
     le titre que dans les mots-clés, le résumé ou la présentation, et
     davantage s'il est rare dans la bibliothèque.
   - Le thésaurus des notions étend la requête : « boucle » cherche
     aussi ses synonymes (répétition, loop…) et ses notions plus
     étroites (boucle bornée, for, while…) ; une fiche classée sous
     une de ces notions est trouvée même si le mot n'y est pas écrit.
   - Un mot inconnu est corrigé (une ou deux lettres de différence),
     et un début de mot suffit (« dicho » trouve « dichotomie »).

   Pur calcul, sans page : assets/bibliotheque.js l'utilise, et
   scripts/tests/test_recherche.js l'essaie avec Node.
   ═══════════════════════════════════════════════════════════════ */
(function (global) {
  'use strict';

  /* Un dictionnaire sans prototype : une clé comme « constructor » n'y trouve rien d'avance */
  function dico() { return Object.create(null); }

  /* Mots vides : jamais cherchés seuls, mais gardés dans les expressions (« boucle pour », « base de données ») */
  var VIDES = dico();
  ('a au aux avec ce ces cet cette d dans de des du elle elles en et est etre il ils je l la le les leur leurs lui ' +
   'ma mais me mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sont sur ta te tes toi ' +
   'ton tu un une vos votre vous y').split(' ').forEach(function (m) { VIDES[m] = true; });

  /* Poids des champs (BM25F) et normalisation par la longueur (b) */
  var CHAMPS = {
    titre: { poids: 8, b: 0.5 },
    mots: { poids: 5, b: 0.5 },          // mots-clés, notions citées, types, usages, langages
    resume: { poids: 3, b: 0.75 },       // accroche, résumé, objectif
    bo: { poids: 2.5, b: 0.5 },          // intitulés du programme officiel
    docs: { poids: 2, b: 0.5 },          // titres des documents, auteurs et autrices, crédits
    presentation: { poids: 1, b: 0.75 }, // présentation, critères de réussite
    texte: { poids: 0.5, b: 0.75 }       // texte des documents hébergés sur le site (chargé à part)
  };
  var K1 = 1.2;
  /* Ce que vaut chaque façon de trouver un mot, par rapport au mot exact */
  var VALEUR = { exact: 1, synonyme: 0.85, plusEtroite: 0.7, debut: 0.7, proche: 0.55 };
  /* Une fiche classée sous la notion cherchée : poids selon le rôle de la notion */
  var ROLES = { enseignees: 1, evaluees: 0.8, prerequises: 0.35 };
  var POIDS_NOTION = 6;

  /* ── Mots ───────────────────────────────────────────────────── */

  var COMBINANTS = new RegExp('[' + String.fromCharCode(0x300) + '-' + String.fromCharCode(0x36F) + ']', 'g');

  function normaliser(t) {
    return String(t == null ? '' : t).toLowerCase().normalize('NFKD').replace(COMBINANTS, '')
      .replace(new RegExp(String.fromCharCode(0x153), 'g'), 'oe').replace(new RegExp(String.fromCharCode(0xE6), 'g'), 'ae')
      .replace(/[^0-9a-z]+/g, ' ').trim();
  }

  /* Racine d'un mot déjà normalisé : quelques règles légères pour le français (pluriels, féminins, -é). */
  function racine(m) {
    if (m.length <= 3 || /^[0-9]+$/.test(m)) return m;
    if (/eaux$/.test(m)) m = m.slice(0, -1);              // tableaux → tableau
    else if (/aux$/.test(m) && m.length > 4) m = m.slice(0, -3) + 'al'; // journaux → journal
    else if (/[^s]s$/.test(m) || /x$/.test(m)) m = m.slice(0, -1);      // boucles → boucle (mais pas « class »)
    while (m.length > 4 && /e$/.test(m)) m = m.slice(0, -1);            // boucle → boucl, donnée → donn
    return m;
  }

  /* Les mots d'un texte, avec leur position, leur forme et leur racine */
  /* Lettres latines (accentuées comprises, de U+00C0 à U+024F, et les ligatures oe), chiffres */
  var MOT = new RegExp('[0-9A-Za-z' + String.fromCharCode(0xC0) + '-' + String.fromCharCode(0x24F) +
    String.fromCharCode(0x152) + String.fromCharCode(0x153) + ']+', 'g');

  function decouper(texte) {
    var t = String(texte == null ? '' : texte), out = [], m;
    MOT.lastIndex = 0;
    while ((m = MOT.exec(t))) {
      var forme = normaliser(m[0]).replace(/ /g, '');
      if (!forme) continue;
      out.push({ debut: m.index, fin: m.index + m[0].length, forme: forme, racine: racine(forme), brut: m[0] });
    }
    return out;
  }

  function cle(mots) {
    return mots.map(function (x) { return x.racine; }).join(' ');
  }

  function utile(x) {
    return !VIDES[x.forme] && (x.forme.length > 1 || /[0-9]/.test(x.forme));
  }

  /* Distance d'édition (insertion, suppression, substitution, échange de deux lettres voisines), bornée */
  function distance(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var prec2 = null, prec = [], i, j;
    for (j = 0; j <= b.length; j++) prec[j] = j;
    for (i = 1; i <= a.length; i++) {
      var cour = [i], mini = i;
      for (j = 1; j <= b.length; j++) {
        var c = a[i - 1] === b[j - 1] ? 0 : 1;
        var v = Math.min(prec[j] + 1, cour[j - 1] + 1, prec[j - 1] + c);
        if (prec2 && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prec2[j - 2] + 1);
        cour[j] = v;
        if (v < mini) mini = v;
      }
      if (mini > max) return max + 1;
      prec2 = prec;
      prec = cour;
    }
    return prec[b.length];
  }

  function tolerance(n) {
    return n >= 8 ? 2 : n >= 4 ? 1 : 0;
  }

  /* ── Le thésaurus ───────────────────────────────────────────── */

  function Thesaurus(t) {
    var self = this;
    this.notions = dico();
    this.etroites = dico();
    this.libelles = dico();      // clé (racines) → [{ notion, sorte }]
    this.formes = dico();        // clé → libellé lisible (pour les suggestions)
    (t && t.notions || []).forEach(function (n) {
      self.notions[n.id] = n;
      self.etroites[n.id] = self.etroites[n.id] || [];
    });
    Object.keys(this.notions).forEach(function (id) {
      (self.notions[id].plus_larges || []).forEach(function (p) {
        if (self.etroites[p]) self.etroites[p].push(id);
      });
    });
    Object.keys(this.notions).forEach(function (id) {
      var n = self.notions[id];
      var sortes = [['libelle', [n.libelle]], ['alternatifs', n.alternatifs], ['anglais', n.anglais], ['code', n.code], ['caches', n.caches]];
      sortes.forEach(function (s) {
        (s[1] || []).forEach(function (lib) {
          var mots = decouper(lib);
          if (!mots.length) return;
          var k = cle(mots);
          (self.libelles[k] = self.libelles[k] || []).push({ notion: id, sorte: s[0] });
          if (s[0] !== 'caches' && !self.formes[k]) self.formes[k] = lib;
        });
      });
    });
    this.longueurMax = Object.keys(this.libelles).reduce(function (m, k) { return Math.max(m, k.split(' ').length); }, 1);
  }

  /* La notion et toutes ses notions plus étroites, à tous les niveaux */
  Thesaurus.prototype.descendance = function (id) {
    var vus = dico(), a_voir = [id], out = [];
    while (a_voir.length) {
      var x = a_voir.pop();
      if (vus[x] || !this.notions[x]) continue;
      vus[x] = true;
      out.push(x);
      a_voir = a_voir.concat(this.etroites[x] || []);
    }
    return out;
  };

  /* La notion et ses notions plus larges */
  Thesaurus.prototype.ascendance = function (id) {
    var vus = dico(), a_voir = [id], out = [];
    while (a_voir.length) {
      var x = a_voir.pop();
      if (vus[x] || !this.notions[x]) continue;
      vus[x] = true;
      out.push(x);
      a_voir = a_voir.concat(this.notions[x].plus_larges || []);
    }
    return out;
  };

  /* Les libellés visibles d'une notion (sans les libellés cachés) */
  Thesaurus.prototype.libellesDe = function (id) {
    var n = this.notions[id];
    if (!n) return [];
    return [n.libelle].concat(n.alternatifs || [], n.anglais || [], n.code || []);
  };

  /* ── L'index ────────────────────────────────────────────────── */

  function Index(options) {
    options = options || {};
    this.thesaurus = new Thesaurus(options.notions);
    this.synonymes = dico();     // clé d'un synonyme de valeur (« sans ordinateur ») → [libellés équivalents]
    this.docs = [];          // { id, champs: { nom: [mots] }, notions: { id: poids } }
    this.parId = dico();
    this.postes = dico();        // racine → { rang du doc: { champ: nombre } }
    this.vocabulaire = dico();   // racine → { df, forme la plus vue, nombre }
    this.prete = false;
  }

  /* Des valeurs de référentiel et leurs synonymes : chercher l'un trouve l'autre (« sans ordinateur » → débranché) */
  Index.prototype.ajouterSynonymes = function (groupes) {
    var self = this;
    (groupes || []).forEach(function (g) {
      var libs = g.filter(Boolean);
      libs.forEach(function (lib) {
        var k = cle(decouper(lib));
        if (!k) return;
        self.synonymes[k] = (self.synonymes[k] || []).concat(libs.filter(function (x) { return x !== lib; }));
      });
    });
  };

  /* Une ressource : ses champs (texte ou liste de textes) et ses notions ({ enseignees: [...], ... }) */
  Index.prototype.ajouter = function (id, champs, notions) {
    var doc = { id: id, champs: dico(), longueurs: dico(), notions: dico() };
    var self = this;
    Object.keys(champs).forEach(function (nom) {
      if (!CHAMPS[nom]) return;
      var textes = Array.isArray(champs[nom]) ? champs[nom] : [champs[nom]];
      var mots = [];
      textes.forEach(function (t) {
        if (mots.length) mots.push(null); // une séparation : pas d'expression à cheval sur deux textes
        mots = mots.concat(decouper(t));
      });
      doc.champs[nom] = mots;
    });
    /* Les notions citées seulement : c'est la requête qui s'étend aux notions plus étroites */
    Object.keys(ROLES).forEach(function (role) {
      ((notions || {})[role] || []).forEach(function (nid) {
        if (!doc.notions[nid] || doc.notions[nid] < ROLES[role]) doc.notions[nid] = ROLES[role];
      });
    });
    this.parId[id] = this.docs.length;
    this.docs.push(doc);
    this.prete = false;
  };

  /* Le texte des documents hébergés, chargé à part : [{ ressource, document, texte }] */
  Index.prototype.ajouterTextes = function (documents) {
    var self = this;
    (documents || []).forEach(function (d) {
      var r = self.parId[d.ressource];
      if (r === undefined) return;
      var doc = self.docs[r];
      doc.textes = doc.textes || [];
      doc.textes.push({ document: d.document, texte: d.texte, mots: decouper(d.texte) });
      var mots = doc.champs.texte || [];
      if (mots.length) mots.push(null);
      doc.champs.texte = mots.concat(doc.textes[doc.textes.length - 1].mots);
    });
    this.prete = false;
    this.avecTextes = true;
  };

  Index.prototype.preparer = function () {
    var self = this;
    this.postes = dico();
    this.vocabulaire = dico();
    this.moyennes = dico();
    this.notionsDf = dico();
    var totaux = dico();
    this.docs.forEach(function (doc, rang) {
      Object.keys(doc.champs).forEach(function (nom) {
        var mots = doc.champs[nom], n = 0;
        mots.forEach(function (x) {
          if (!x) return;
          n++;
          var p = self.postes[x.racine] || (self.postes[x.racine] = dico());
          var q = p[rang] || (p[rang] = dico());
          q[nom] = (q[nom] || 0) + 1;
          var v = self.vocabulaire[x.racine] || (self.vocabulaire[x.racine] = { formes: dico(), df: 0 });
          var brut = x.brut.toLowerCase(); // la forme écrite (accents compris), pour l'afficher
          v.formes[brut] = (v.formes[brut] || 0) + 1;
        });
        doc.longueurs[nom] = n;
        totaux[nom] = (totaux[nom] || 0) + n;
      });
      Object.keys(doc.notions).forEach(function (nid) { self.notionsDf[nid] = (self.notionsDf[nid] || 0) + 1; });
    });
    Object.keys(this.postes).forEach(function (r) { self.vocabulaire[r].df = Object.keys(self.postes[r]).length; });
    Object.keys(totaux).forEach(function (nom) { self.moyennes[nom] = totaux[nom] / Math.max(1, self.docs.length); });
    this.racines = Object.keys(this.vocabulaire).sort();
    this.prete = true;
  };

  Index.prototype.idf = function (df) {
    var n = this.docs.length;
    return Math.log(1 + (n - df + 0.5) / (df + 0.5));
  };

  /* La forme la plus vue d'une racine, pour l'afficher */
  Index.prototype.forme = function (r) {
    var v = this.vocabulaire[r];
    if (!v) return r;
    return Object.keys(v.formes).sort(function (a, b) { return v.formes[b] - v.formes[a] || a.length - b.length; })[0];
  };

  /* Occurrences d'une suite de racines dans les champs d'un document : { champ: nombre } */
  Index.prototype.occurrences = function (rang, suite) {
    var doc = this.docs[rang], out = dico(), trouve = false;
    if (suite.length === 1) {
      var p = (this.postes[suite[0]] || {})[rang];
      return p || null;
    }
    var premier = (this.postes[suite[0]] || {})[rang];
    if (!premier) return null;
    Object.keys(premier).forEach(function (nom) {
      var mots = doc.champs[nom], n = 0;
      for (var i = 0; i + suite.length <= mots.length; i++) {
        var ok = true;
        for (var j = 0; j < suite.length; j++) {
          if (!mots[i + j] || mots[i + j].racine !== suite[j]) { ok = false; break; }
        }
        if (ok) n++;
      }
      if (n) { out[nom] = n; trouve = true; }
    });
    return trouve ? out : null;
  };

  /* Les documents qui contiennent une suite de racines */
  Index.prototype.documentsAvec = function (suite) {
    var self = this, out = dico();
    var candidats = this.postes[suite[0]];
    if (!candidats) return out;
    Object.keys(candidats).forEach(function (rang) {
      var o = self.occurrences(+rang, suite);
      if (o) out[rang] = o;
    });
    return out;
  };

  Index.prototype.bm25 = function (rang, occ, idf) {
    var doc = this.docs[rang], tf = 0, self = this;
    Object.keys(occ).forEach(function (nom) {
      var c = CHAMPS[nom], moy = self.moyennes[nom] || 1;
      tf += c.poids * occ[nom] / ((1 - c.b) + c.b * (doc.longueurs[nom] || 0) / moy);
    });
    return idf * tf * (K1 + 1) / (tf + K1);
  };

  /* ── La requête ─────────────────────────────────────────────── */

  /* Les variantes d'un mot : exact, début de mot, mots proches (fautes de frappe) */
  Index.prototype.variantes = function (x) {
    var r = x.racine, out = [], self = this;
    if (this.vocabulaire[r]) out.push({ suite: [r], valeur: VALEUR.exact, sorte: 'exact' });
    var debut = x.forme.length >= 2 ? (x.forme.length <= 4 ? x.forme : r) : null;
    if (debut) {
      this.racines.forEach(function (v) {
        if (v !== r && v.indexOf(debut) === 0) out.push({ suite: [v], valeur: VALEUR.debut, sorte: 'debut' });
      });
    }
    if (!out.length) {
      var max = tolerance(x.forme.length);
      if (max) {
        this.racines.forEach(function (v) {
          var d = distance(r, v, max);
          if (d > max && v.length > r.length) d = distance(r, v.slice(0, r.length), max) + 0.5; // faute dans un début de mot
          if (d <= max) out.push({ suite: [v], valeur: VALEUR.proche * (d <= 1 ? 1 : 0.8), sorte: 'proche', distance: d });
        });
        out.sort(function (a, b) { return a.distance - b.distance || self.vocabulaire[b.suite[0]].df - self.vocabulaire[a.suite[0]].df; });
        out = out.slice(0, 6);
      }
    }
    return out;
  };

  /* Les expressions du thésaurus et des synonymes reconnues dans la requête (la plus longue d'abord) */
  Index.prototype.analyser = function (requete) {
    var mots = decouper(requete), clauses = [], i = 0, th = this.thesaurus, self = this;
    while (i < mots.length) {
      var pris = 0;
      for (var n = Math.min(th.longueurMax, mots.length - i); n >= 1 && !pris; n--) {
        var morceau = mots.slice(i, i + n);
        if (!morceau.some(utile)) continue;
        var k = cle(morceau);
        var entrees = th.libelles[k] || [];
        var syn = self.synonymes[k];
        if (entrees.length || syn) {
          var notions = [], preferes = dico();
          entrees.forEach(function (e) {
            if (notions.indexOf(e.notion) < 0) notions.push(e.notion);
            if (e.sorte === 'libelle') preferes[e.notion] = true;
          });
          clauses.push({ texte: requete.slice(morceau[0].debut, morceau[n - 1].fin), mots: morceau,
                         notions: notions, preferes: preferes, synonymes: syn || [] });
          pris = n;
        }
      }
      if (pris) { i += pris; continue; }
      if (utile(mots[i])) {
        clauses.push({ texte: requete.slice(mots[i].debut, mots[i].fin), mots: [mots[i]], notions: [], preferes: dico(), synonymes: [] });
      }
      i++;
    }
    return clauses;
  };

  /* Les façons de satisfaire une clause : suites de racines à chercher, et notions */
  Index.prototype.alternatives = function (clause) {
    var self = this, th = this.thesaurus, alt = [], vues = dico();
    function ajouter(suite, valeur, sorte) {
      if (!suite.length) return;
      var k = suite.join(' ');
      if (vues[k] && vues[k].valeur >= valeur) return;
      if (vues[k]) { vues[k].valeur = valeur; vues[k].sorte = sorte; return; }
      vues[k] = { suite: suite, valeur: valeur, sorte: sorte };
      alt.push(vues[k]);
    }
    function libelle(lib, valeur, sorte) {
      ajouter(decouper(lib).map(function (x) { return x.racine; }), valeur, sorte);
    }
    var corrections = [];
    var connu = clause.notions.length || clause.synonymes.length;
    if (clause.mots.length === 1) {
      // Un mot : exact, début de mot, et seulement s'il n'y a rien d'autre, mots proches
      this.variantes(clause.mots[0]).forEach(function (v) {
        ajouter(v.suite, v.valeur, v.sorte);
        if (v.sorte === 'proche' && !connu) corrections.push(v.suite[0]);
      });
      // Une faute de frappe sur un libellé du thésaurus (« recurcivite » → récursivité)
      if (!connu && (!alt.length || alt.every(function (a) { return a.sorte === 'proche'; }))) {
        var x = clause.mots[0], max = tolerance(x.forme.length);
        Object.keys(th.libelles).forEach(function (k) {
          if (k.indexOf(' ') < 0 && max && distance(x.racine, k, max) <= max) {
            th.libelles[k].forEach(function (e) {
              if (clause.notions.indexOf(e.notion) < 0) clause.notions.push(e.notion);
              if (e.sorte === 'libelle') clause.preferes[e.notion] = true;
            });
            corrections.push(k);
          }
        });
      }
    } else {
      ajouter(clause.mots.map(function (x) { return x.racine; }), VALEUR.exact, 'exact');
    }
    clause.synonymes.forEach(function (lib) { libelle(lib, VALEUR.synonyme, 'synonyme'); });
    var notions = [], valeurs = dico();
    clause.notions.forEach(function (nid) {
      var n = th.notions[nid];
      // Le libellé préféré étend à tous les synonymes ; un autre libellé (« linux » pour les systèmes
      // d'exploitation) cherche ce mot et le libellé préféré, pas les autres termes rattachés (Windows, Android…)
      var libs = clause.preferes[nid] ? th.libellesDe(nid) : [n.libelle];
      libs.forEach(function (lib) { libelle(lib, VALEUR.synonyme, 'synonyme'); });
      th.descendance(nid).forEach(function (d) {
        var v = d === nid ? VALEUR.exact : VALEUR.plusEtroite;
        if (notions.indexOf(d) < 0) notions.push(d);
        if (!valeurs[d] || valeurs[d] < v) valeurs[d] = v;
      });
      // Les notions plus étroites, sur deux niveaux : leur libellé et leurs mots du code (for, while…),
      // sauf les mots du code de moins de trois lettres (cd, ls), trop fréquents dans les textes
      var niveau = [nid];
      for (var profondeur = 0; profondeur < 2; profondeur++) {
        var suivant = [];
        niveau.forEach(function (p) { suivant = suivant.concat(th.etroites[p] || []); });
        suivant.forEach(function (d) {
          var nd = th.notions[d];
          libelle(nd.libelle, VALEUR.plusEtroite, 'plus-etroite');
          (nd.code || []).forEach(function (c) { if (normaliser(c).length >= 3) libelle(c, VALEUR.plusEtroite, 'plus-etroite'); });
        });
        niveau = suivant;
      }
    });
    return { suites: alt, notions: notions, valeurs: valeurs, corrections: corrections };
  };

  /* Chercher. Rend { clauses, resultats: [{ id, score, couverture, trouves, notions, champs }], partiel,
     corrections: [{ de, vers }], suggestion } ; resultats triés par score. */
  Index.prototype.chercher = function (requete) {
    if (!this.prete) this.preparer();
    var self = this, th = this.thesaurus;
    var clauses = this.analyser(requete || '');
    var parDoc = dico();
    var corrections = [];
    clauses.forEach(function (clause, c) {
      var a = self.alternatives(clause);
      clause.alternatives = a;
      if (a.corrections.length && clause.mots.length === 1 && !self.vocabulaire[clause.mots[0].racine]) {
        var meilleure = a.corrections[0];
        corrections.push({ de: clause.texte, vers: th.formes[meilleure] || self.forme(meilleure) });
      }
      var scores = dico();
      a.suites.forEach(function (alt) {
        var docs = self.documentsAvec(alt.suite), df = Object.keys(docs).length;
        if (!df) return;
        var idf = self.idf(df);
        Object.keys(docs).forEach(function (rang) {
          var s = alt.valeur * self.bm25(+rang, docs[rang], idf);
          var e = scores[rang] || (scores[rang] = { score: 0, trouves: dico(), champs: dico(), notions: [] });
          if (s > e.score) e.score = s;
          alt.suite.forEach(function (r) { e.trouves[r] = true; });
          Object.keys(docs[rang]).forEach(function (nom) { e.champs[nom] = true; });
        });
      });
      a.notions.forEach(function (nid) {
        var df = self.notionsDf[nid];
        if (!df) return;
        var idf = self.idf(df);
        self.docs.forEach(function (doc, rang) {
          var p = doc.notions[nid];
          if (!p) return;
          // Comme un mot trouvé dans un champ de poids POIDS_NOTION (BM25), selon le rôle de la notion
          var tf = POIDS_NOTION * p;
          var s = a.valeurs[nid] * idf * tf * (K1 + 1) / (tf + K1);
          var e = scores[rang] || (scores[rang] = { score: 0, trouves: dico(), champs: dico(), notions: [] });
          e.score = Math.max(e.score, s) + 0.1 * Math.min(e.score, s);
          if (e.notions.indexOf(nid) < 0) e.notions.push(nid);
        });
      });
      Object.keys(scores).forEach(function (rang) {
        var d = parDoc[rang] || (parDoc[rang] = { score: 0, couverture: 0, trouves: dico(), champs: dico(), notions: [] });
        d.score += scores[rang].score;
        d.couverture += 1;
        Object.keys(scores[rang].trouves).forEach(function (r) { d.trouves[r] = true; });
        Object.keys(scores[rang].champs).forEach(function (nom) { d.champs[nom] = true; });
        scores[rang].notions.forEach(function (n) { if (d.notions.indexOf(n) < 0) d.notions.push(n); });
      });
    });
    var tous = Object.keys(parDoc).map(function (rang) {
      var d = parDoc[rang];
      return { id: self.docs[rang].id, score: d.score, couverture: d.couverture, trouves: Object.keys(d.trouves),
               champs: Object.keys(d.champs), notions: d.notions };
    });
    var complets = tous.filter(function (r) { return r.couverture === clauses.length; });
    var partiel = !complets.length && tous.length > 0 && clauses.length > 1;
    var resultats = (partiel ? tous : complets).sort(function (a, b) {
      return b.couverture - a.couverture || b.score - a.score || (a.id < b.id ? -1 : 1);
    });
    var suggestion = null;
    if (corrections.length) {
      suggestion = requete;
      corrections.forEach(function (c) { suggestion = suggestion.replace(c.de, c.vers); });
    }
    return { clauses: clauses, resultats: resultats, partiel: partiel, corrections: corrections,
             suggestion: suggestion !== requete ? suggestion : null };
  };

  /* Des mots proches d'une requête qui ne donne rien : libellés du thésaurus et mots de la bibliothèque */
  Index.prototype.suggestions = function (requete, nombre) {
    if (!this.prete) this.preparer();
    var self = this, out = [], vus = dico();
    decouper(requete).filter(utile).forEach(function (x) {
      // Les mots qui commencent pareil (d = 0,5), puis les mots à une ou deux lettres près (deux seulement
      // pour un mot d'au moins 5 lettres, et s'il n'y a rien de plus proche)
      var max = Math.max(1, tolerance(x.forme.length) + (x.forme.length >= 5 ? 1 : 0));
      var cands = [];
      function proche(cible) {
        if (x.racine.length >= 3 && cible.indexOf(x.racine) === 0 && cible !== x.racine) return 0.5;
        return distance(x.racine, cible, max);
      }
      // Seulement des mots de la bibliothèque : une suggestion donne toujours des résultats
      self.racines.forEach(function (r) {
        if (r === x.racine) return;
        var d = proche(r);
        if (d <= max) cands.push({ texte: self.forme(r), d: d, df: self.vocabulaire[r].df });
      });
      var meilleure = cands.reduce(function (m, c) { return Math.min(m, c.d); }, max + 1);
      cands = cands.filter(function (c) { return c.d <= Math.max(1, meilleure); });
      cands.sort(function (a, b) { return a.d - b.d || b.df - a.df; });
      cands.forEach(function (c) {
        var k = normaliser(c.texte);
        if (!vus[k]) { vus[k] = true; out.push(c.texte); }
      });
    });
    return out.slice(0, nombre || 5);
  };

  /* Un texte découpé pour le surligner : [{ texte, marque }] ; trouves = racines trouvées */
  function surligner(texte, trouves) {
    var t = String(texte == null ? '' : texte), out = [], pos = 0, ens = dico();
    (trouves || []).forEach(function (r) { ens[r] = true; });
    decouper(t).forEach(function (x) {
      if (!ens[x.racine] || VIDES[x.forme]) return;
      if (x.debut > pos) out.push({ texte: t.slice(pos, x.debut), marque: false });
      out.push({ texte: t.slice(x.debut, x.fin), marque: true });
      pos = x.fin;
    });
    if (pos < t.length) out.push({ texte: t.slice(pos), marque: false });
    return out;
  }

  /* Un extrait autour du premier mot trouvé dans un long texte */
  function extrait(texte, trouves, largeur) {
    var t = String(texte || ''), ens = dico(), l = largeur || 90;
    (trouves || []).forEach(function (r) { ens[r] = true; });
    var mots = decouper(t), premier = null;
    for (var i = 0; i < mots.length; i++) {
      if (ens[mots[i].racine] && !VIDES[mots[i].forme]) { premier = mots[i]; break; }
    }
    if (!premier) return null;
    var debut = Math.max(0, premier.debut - l), fin = Math.min(t.length, premier.fin + l);
    while (debut > 0 && /\S/.test(t[debut - 1])) debut--;
    while (fin < t.length && /\S/.test(t[fin])) fin++;
    return (debut > 0 ? '… ' : '') + t.slice(debut, fin).replace(/\s+/g, ' ').trim() + (fin < t.length ? ' …' : '');
  }

  /* ── Les fiches de la bibliothèque ──────────────────────────── */

  /* Les référentiels de bibliotheque.json, rangés pour être consultés par identifiant */
  function references(refs) {
    var out = { valeurs: dico(), noeuds: dico(), notions: dico(), pix: dico() };
    Object.keys(refs.valeurs || {}).forEach(function (liste) {
      out.valeurs[liste] = dico();
      refs.valeurs[liste].forEach(function (v) { out.valeurs[liste][v.id] = v; });
    });
    (refs.programmes || []).forEach(function (p) {
      out.noeuds[p.id] = { id: p.id, intitule: p.intitule, court: p.court, parent: null, programme: p.id, niveau: 'programme', enfants: [] };
      (p.themes || []).forEach(function (t) {
        out.noeuds[t.id] = { id: t.id, intitule: t.intitule, court: t.court, parent: p.id, programme: p.id, niveau: 'theme', enfants: [] };
        out.noeuds[p.id].enfants.push(t.id);
        (t.contenus || []).forEach(function (c) {
          out.noeuds[c.id] = { id: c.id, intitule: c.intitule, court: c.court, parent: t.id, programme: p.id, niveau: 'contenu', enfants: [] };
          out.noeuds[t.id].enfants.push(c.id);
        });
      });
    });
    ((refs.notions || {}).notions || []).forEach(function (n) { out.notions[n.id] = n; });
    ((refs.competences_pix || {}).competences || []).forEach(function (c) { out.pix[c.id] = c; });
    return out;
  }

  /* Les valeurs des référentiels et leurs synonymes, en groupes pour Index.ajouterSynonymes */
  function groupesSynonymes(refs) {
    var out = [];
    ['types', 'usages', 'langages', 'roles', 'origines'].forEach(function (liste) {
      ((refs.valeurs || {})[liste] || []).forEach(function (v) {
        if (v.alternatifs && v.alternatifs.length) out.push([v.libelle].concat(v.alternatifs));
      });
    });
    return out;
  }

  /* Les champs de recherche d'une fiche : titre, mots-clés et classements, résumé, programme, documents, présentation */
  function champsFiche(f, refs) {
    function lib(liste, id) {
      var v = refs.valeurs[liste] && refs.valeurs[liste][id];
      return v ? v.libelle : '';
    }
    var notions = f.notions || {};
    var citees = [].concat(notions.enseignees || [], notions.evaluees || [], notions.prerequises || []);
    var mots = (f.mots_cles || []).slice();
    citees.forEach(function (nid) {
      var n = refs.notions[nid];
      if (n) mots = mots.concat([n.libelle], n.alternatifs || []);
    });
    [['types', f.types], ['usages', f.usages], ['langages', f.langages], ['enseignements', f.enseignements],
     ['niveaux', f.niveaux], ['origines', [f.origine]]].forEach(function (x) {
      (x[1] || []).forEach(function (id) { var l = lib(x[0], id); if (l) mots.push(l); });
    });
    (f.competences_pix || []).forEach(function (id) { if (refs.pix[id]) mots.push(refs.pix[id].libelle); });
    var bo = [];
    (f.programme || []).forEach(function (id) {
      var n = refs.noeuds[id];
      while (n) {
        if (bo.indexOf(n.intitule) < 0) bo.push(n.intitule);
        n = n.parent && n.niveau !== 'theme' ? refs.noeuds[n.parent] : null;
      }
    });
    var docs = [];
    (f.documents || []).forEach(function (d) { docs.push(d.titre || lib('roles', d.role)); });
    (f.auteurs || []).forEach(function (a) { docs.push(a.nom + (a.role ? ' (' + a.role + ')' : '')); });
    if (f.credits) docs.push(f.credits);
    var pres = [f.presentation].concat(f.criteres_reussite || []);
    if (f.editeur_code && f.editeur_code.remarque) pres.push(f.editeur_code.remarque);
    if (f.donnees_eleves && f.donnees_eleves.detail) pres.push(f.donnees_eleves.detail);
    return {
      titre: f.titre, mots: mots, resume: [f.accroche, f.resume, f.objectif].filter(Boolean),
      bo: bo, docs: docs, presentation: pres.filter(Boolean)
    };
  }

  var Recherche = {
    references: references, groupesSynonymes: groupesSynonymes, champsFiche: champsFiche,
    Index: Index, Thesaurus: Thesaurus, CHAMPS: CHAMPS,
    normaliser: normaliser, racine: racine, decouper: decouper, distance: distance,
    surligner: surligner, extrait: extrait
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = Recherche;
  else global.Recherche = Recherche;
})(this);
