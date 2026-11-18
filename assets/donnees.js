/* ═══════════════════════════════════════════════════════════════
   Les données de la bibliothèque dans le navigateur (admin, T51).

   1. La validation, avant tout enregistrement : le schéma JSON (le même
      sous-ensemble que scripts/valider_donnees.py, avec les mêmes messages)
      et les contrôles du script qui produisent une ERREUR, pour qu'un
      enregistrement de l'admin ne puisse jamais arrêter « Publier le site ».
      Les avertissements et les informations restent au script.
   2. L'écriture d'un fichier JSON qui garde le texte d'origine partout où
      rien ne change : seules les lignes modifiées bougent dans le dépôt.

   Utilisable dans une page (window.Donnees) et dans Node (tests :
   scripts/tests/test_admin_donnees.js).
   ═══════════════════════════════════════════════════════════════ */
(function (racine, fabrique) {
  'use strict';
  var m = fabrique();
  if (typeof module === 'object' && module.exports) module.exports = m;
  else racine.Donnees = m;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ── Outils ───────────────────────────────────────────────────── */

  var TYPES_FR = {
    object: 'un objet { … }', array: 'une liste [ … ]', string: 'un texte entre guillemets',
    boolean: 'true ou false', integer: 'un nombre entier', number: 'un nombre', 'null': 'null'
  };

  var AIDES_MOTIFS = {
    '^[a-z0-9]+(-[a-z0-9]+)*$':
      'un identifiant s\'écrit en minuscules, sans accents, espaces ni point médian, avec des tirets entre les mots (exemple : td1-poo)',
    '^[a-z0-9]+(-[a-z0-9]+)*(\\.[a-z0-9]+(-[a-z0-9]+)*){0,2}$':
      'un identifiant de programme s\'écrit comme snt-2019.donnees-structurees.traitement',
    '^[0-9]{4}-[0-9]{2}-[0-9]{2}$': 'une date s\'écrit AAAA-MM-JJ (exemple : 2026-11-07)',
    '^https?://[^\\s/$.?#][^\\s]*$': 'une adresse commence par https:// et ne contient pas d\'espace',
    '^[A-Za-z0-9_][A-Za-z0-9._/-]*([#?][^\\s]*)?$':
      'un chemin part de la racine du dépôt, sans « / » au début, sans espaces ni accents (exemple : nsi-terminale/fichiers/td1-poo-premiers-pas.pdf)',
    '^[0-9]{4}-[0-9]{4}$': 'une année scolaire s\'écrit 2026-2027',
    '^[a-z0-9]+(-[a-z0-9]+)*(\\.[a-z0-9]+(-[a-z0-9]+)*)*$':
      'un identifiant de notion s\'écrit en minuscules, sans accents, avec des tirets entre les mots et des points entre les niveaux (exemple : prog.boucle.bornee)',
    '^[a-z]+$': 'un nom en minuscules, sans accents (exemple : bleu)'
  };

  function typeDe(v) {
    if (v === null || v === undefined) return 'null';
    if (typeof v === 'boolean') return 'boolean';
    if (typeof v === 'number') return Number.isInteger(v) ? 'integer' : 'number';
    if (typeof v === 'string') return 'string';
    if (Array.isArray(v)) return 'array';
    return 'object';
  }

  function duType(v, attendu) {
    var reel = typeDe(v);
    return (Array.isArray(attendu) ? attendu : [attendu]).some(function (t) {
      return t === reel || (t === 'number' && reel === 'integer');
    });
  }

  function joindre(chemin, cle) {
    if (typeof cle === 'number') return chemin + '[' + cle + ']';
    return chemin ? chemin + '.' + cle : cle;
  }

  function court(v) {
    var t = JSON.stringify(v);
    return t.length <= 60 ? t : t.slice(0, 57) + '…';
  }

  function pluriel(n, un) {
    return n + ' ' + (n <= 1 ? un : un + 's');
  }

  /* JSON.stringify avec les clés triées : pour comparer deux valeurs */
  function canonique(v) {
    if (Array.isArray(v)) return '[' + v.map(canonique).join(',') + ']';
    if (v && typeof v === 'object') {
      return '{' + Object.keys(v).sort().map(function (k) { return JSON.stringify(k) + ':' + canonique(v[k]); }).join(',') + '}';
    }
    return JSON.stringify(v);
  }

  function egal(a, b) { return canonique(a) === canonique(b); }

  function copie(v) { return v === undefined ? undefined : JSON.parse(JSON.stringify(v)); }

  /* Python : re.search(motif) ; les motifs des schémas sont compatibles avec JavaScript */
  var MOTIFS = {};
  function motif(m) { return MOTIFS[m] || (MOTIFS[m] = new RegExp(m)); }

  function dateValide(s) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '');
    if (!m) return null;
    var d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
    return d.getUTCMonth() === +m[2] - 1 && d.getUTCDate() === +m[3] ? d : null;
  }

  /* ── Le validateur de schéma (comme ValidateurSchema du script) ── */

  function ValidateurSchema(schema) { this.racine = schema; }

  ValidateurSchema.prototype.resoudre = function (ref) {
    if (ref.indexOf('#/') !== 0) throw new Error('référence de schéma non gérée : ' + ref);
    return ref.slice(2).split('/').reduce(function (n, k) { return n[k]; }, this.racine);
  };

  ValidateurSchema.prototype.erreurs = function (v, s, chemin) {
    var self = this;
    s = s || this.racine;
    chemin = chemin || '';
    var out = [];
    if (s.$ref) out = out.concat(this.erreurs(v, this.resoudre(s.$ref), chemin));
    if ('type' in s && !duType(v, s.type)) {
      var attendu = typeof s.type === 'string' ? s.type : s.type[0];
      out.push([chemin, 'doit être ' + TYPES_FR[attendu] + ', et non ' + TYPES_FR[typeDe(v)]]);
      return out;
    }
    if ('const' in s && !egal(v, s.const)) out.push([chemin, 'doit valoir ' + court(s.const)]);
    if (s.enum && !s.enum.some(function (e) { return egal(e, v); })) {
      out.push([chemin, 'valeur ' + court(v) + ' non permise (valeurs possibles : ' + s.enum.join(', ') + ')']);
    }
    if (typeof v === 'string') {
      var n = Array.from(v).length; // comme len() en Python : en caractères, pas en unités UTF-16
      if ('minLength' in s && n < s.minLength) out.push([chemin, 'texte trop court (' + pluriel(s.minLength, 'caractère') + ' au moins)']);
      if ('maxLength' in s && n > s.maxLength) out.push([chemin, 'texte trop long (' + n + ' caractères pour ' + s.maxLength + ' au plus)']);
      if (s.pattern && !motif(s.pattern).test(v)) {
        out.push([chemin, 'forme incorrecte ' + court(v) + ' : ' + (AIDES_MOTIFS[s.pattern] || 'motif attendu : ' + s.pattern)]);
      }
      if (s.format === 'date' && /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(v) && !dateValide(v)) {
        out.push([chemin, 'date impossible ' + court(v)]);
      }
    }
    if ((typeDe(v) === 'integer' || typeDe(v) === 'number') && 'minimum' in s && v < s.minimum) {
      out.push([chemin, 'doit valoir au moins ' + s.minimum]);
    }
    if (Array.isArray(v)) {
      if ('minItems' in s && v.length < s.minItems) out.push([chemin, 'la liste doit contenir au moins ' + pluriel(s.minItems, 'élément')]);
      if ('maxItems' in s && v.length > s.maxItems) out.push([chemin, 'la liste contient ' + v.length + ' éléments pour ' + s.maxItems + ' au plus']);
      if (s.uniqueItems) {
        var vus = {};
        v.forEach(function (x, i) {
          var cle = canonique(x);
          if (vus[cle]) out.push([joindre(chemin, i), court(x) + ' figure deux fois dans la liste']);
          vus[cle] = true;
        });
      }
      if (s.items) v.forEach(function (x, i) { out = out.concat(self.erreurs(x, s.items, joindre(chemin, i))); });
    }
    if (typeDe(v) === 'object') {
      (s.required || []).forEach(function (champ) {
        if (!(champ in v)) out.push([chemin, 'champ obligatoire manquant : « ' + champ + ' »']);
      });
      var props = s.properties || {};
      Object.keys(v).forEach(function (cle) {
        if (cle in props) out = out.concat(self.erreurs(v[cle], props[cle], joindre(chemin, cle)));
        else if (s.additionalProperties === false) {
          var possibles = Object.keys(props).filter(function (k) { return k !== '$schema'; }).join(', ');
          out.push([chemin, 'champ inconnu « ' + cle + ' » (champs possibles : ' + possibles + ')']);
        }
      });
    }
    if (s.not && !this.erreurs(v, s.not, chemin).length) {
      if (s.not.pattern) {
        out.push([chemin, s.not.pattern.indexOf('\\.\\.') >= 0
          ? 'le chemin ne doit pas remonter d\'un dossier avec « .. »'
          : 'forme interdite (motif ' + s.not.pattern + ')']);
      } else if (s.not.required) {
        var noms = s.not.required.map(function (x) { return '« ' + x + ' »'; });
        out.push([chemin, noms.length > 1
          ? 'les champs ' + noms.join(' et ') + ' ne vont pas ensemble : n\'en garder qu\'un'
          : 'le champ ' + noms[0] + ' ne doit pas être présent ici']);
      } else out.push([chemin, 'valeur interdite']);
    }
    if (s['if'] && typeDe(v) === 'object') {
      if (!this.erreurs(v, s['if'], chemin).length) { if (s.then) out = out.concat(this.erreurs(v, s.then, chemin)); }
      else if (s['else']) out = out.concat(this.erreurs(v, s['else'], chemin));
    }
    ['oneOf', 'anyOf'].forEach(function (mot) {
      if (!s[mot]) return;
      var resultats = s[mot].map(function (b) { return self.erreurs(v, b, chemin); });
      var valides = resultats.filter(function (r) { return !r.length; }).length;
      if (valides === 0) out = out.concat(self.messageFormes(v, s[mot], resultats, chemin));
      else if (mot === 'oneOf' && valides > 1) out.push([chemin, 'correspond à plusieurs formes à la fois']);
    });
    return out;
  };

  ValidateurSchema.prototype.messageFormes = function (v, branches, resultats, chemin) {
    var simples = branches.every(function (b) {
      return Object.keys(b).every(function (k) { return k === 'required' || k === 'not'; });
    });
    if (simples) {
      var noms = [];
      branches.forEach(function (b) { (b.required || []).forEach(function (n) { if (noms.indexOf(n) < 0) noms.push(n); }); });
      var presents = noms.filter(function (n) { return typeDe(v) === 'object' && n in v; });
      var liste = noms.map(function (n) { return '« ' + n + ' »'; }).join(' ou ');
      return [[chemin, presents.length > 1 ? 'un seul des champs ' + liste + ', pas les deux' : 'il manque un des champs ' + liste]];
    }
    return resultats.reduce(function (a, b) { return b.length < a.length ? b : a; });
  };

  /* ── Les textes qui ressemblent à un secret (chercher_secrets) ─── */

  var MOTIFS_SECRETS = [
    [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, 'une clé privée'],
    [/\bgh[pousr]_[A-Za-z0-9]{30,}/, 'un jeton GitHub'],
    [/\bgithub_pat_[A-Za-z0-9_]{30,}/, 'un jeton GitHub'],
    [/\bsb_secret_[A-Za-z0-9_-]{10,}/, 'une clé secrète Supabase'],
    [/service[_ -]?role/i, 'une clé « service_role » Supabase'],
    [/\bsk-(ant-)?[A-Za-z0-9_-]{20,}/, 'une clé secrète d\'API'],
    [/\bAKIA[0-9A-Z]{16}\b/, 'une clé d\'accès AWS'],
    [/\bAIza[0-9A-Za-z_-]{35}/, 'une clé d\'API Google'],
    [/\bxox[abprs]-[A-Za-z0-9-]{10,}/, 'un jeton Slack']
  ];
  var CHAMP_SECRET = /\b(mots? de passe|mdp|password|passwd|pwd|identifiants?|logins?|nom d'utilisateur|username|clé secrète|cle secrete|secret|token|jeton|code d'accès)\s*[:=]\s*[«"']?\s*([^\s,;»"']+)/gi;
  var DEMO = /\b(identifiants?|comptes?|logins?|accès|codes?)\b[^:=\n]{0,40}\b(d[ée]mo|d[ée]monstration|test)\w*[^:=\n]{0,20}[:=]\s*\S+/i;
  var MDP_EST = /\bmots? de passe\s+(est|sera)\s+[«"']?\s*([^\s,;»"']+)/i;
  var URL_SECRET = /[?&](password|passwd|pwd|pass|token|access_token|api_?key|apikey|secret|auth|key|cle)=([^&#\s]+)/gi;
  var JWT = /\beyJ[A-Za-z0-9_-]{8,}\.(eyJ[A-Za-z0-9_-]{8,})\.[A-Za-z0-9_-]{8,}/g;
  var MOTS_ANODINS = ('a à au aux aucun aucune des donné donnés donnée données en fourni fournis fournie fournies '
    + 'l\'enseignant l\'élève la le les non oui par personnel personnels propre propres sur un une voir demander demande').split(' ');

  function textes(obj, chemin, out) {
    out = out || [];
    chemin = chemin || '';
    if (typeof obj === 'string') out.push([chemin, obj]);
    else if (Array.isArray(obj)) obj.forEach(function (x, i) { textes(x, joindre(chemin, i), out); });
    else if (obj && typeof obj === 'object') {
      Object.keys(obj).forEach(function (k) { if (k !== '$schema') textes(obj[k], joindre(chemin, k), out); });
    }
    return out;
  }

  function base64url(s) {
    s = s.replace(/-/g, '+').replace(/_/g, '/');
    while (s.length % 4) s += '=';
    if (typeof atob === 'function') return atob(s);
    return Buffer.from(s, 'base64').toString('binary');
  }

  function chercherSecrets(obj, erreur) {
    textes(obj).forEach(function (ct) {
      var chemin = ct[0], t = ct[1], m;
      MOTIFS_SECRETS.forEach(function (ms) {
        if (ms[0].test(t)) erreur(chemin, 'ce texte semble contenir ' + ms[1] + '. Le dépôt est public : retirer la valeur.');
      });
      CHAMP_SECRET.lastIndex = 0;
      while ((m = CHAMP_SECRET.exec(t))) {
        var valeur = m[2].toLowerCase().replace(/^\.+|\.+$/g, '');
        if (MOTS_ANODINS.indexOf(valeur) < 0) {
          erreur(chemin, '« ' + m[0].slice(0, 40) + '… » ressemble à un identifiant ou un mot de passe. Le dépôt est public : '
            + 'ne jamais l\'écrire (dire plutôt « comptes sur demande »).');
        }
      }
      if (DEMO.test(t)) erreur(chemin, 'ce texte semble donner des identifiants de démonstration : ils ne sont jamais publiés.');
      m = MDP_EST.exec(t);
      if (m && MOTS_ANODINS.indexOf(m[2].toLowerCase()) < 0) erreur(chemin, 'ce texte semble donner un mot de passe : ne jamais l\'écrire.');
      URL_SECRET.lastIndex = 0;
      while ((m = URL_SECRET.exec(t))) {
        erreur(chemin, 'l\'adresse contient « ' + m[1] + '=… », qui ressemble à une clé ou un mot de passe : la retirer.');
      }
      JWT.lastIndex = 0;
      while ((m = JWT.exec(t))) {
        var role = '';
        try { role = String(JSON.parse(base64url(m[1])).role || ''); } catch (e) { /* illisible : pas une clé « service_role » */ }
        if (role === 'service_role') erreur(chemin, 'clé Supabase « service_role » : elle est secrète et ne doit jamais être publiée.');
      }
    });
  }

  /* ── Les référentiels ─────────────────────────────────────────── */

  /* refs : { valeurs, programmes (la liste des programmes), notions (liste ou { notions: [] }),
              competences_pix ({ competences: [] }) } — la forme de bibliotheque-complete.json */
  function Referentiels(refs) {
    var self = this;
    this.valeurs = {};
    Object.keys(refs.valeurs || {}).forEach(function (liste) {
      if (!Array.isArray(refs.valeurs[liste])) return;
      self.valeurs[liste] = {};
      refs.valeurs[liste].forEach(function (e) { if (e && e.id) self.valeurs[liste][e.id] = e; });
    });
    this.valeurs.competences_pix = {};
    ((refs.competences_pix || {}).competences || []).forEach(function (c) { if (c && c.id) self.valeurs.competences_pix[c.id] = c; });

    this.noeuds = {};
    (Array.isArray(refs.programmes) ? refs.programmes : (refs.programmes || {}).programmes || []).forEach(function (p) {
      self.noeuds[p.id] = { niveau: 'programme', parent: null, racine: p.id, intitule: p.intitule, court: p.court,
        enseignement: p.enseignement, niveaux: p.niveaux || [], enfants: [] };
      (p.themes || []).forEach(function (t) {
        self.noeuds[t.id] = { niveau: 'theme', parent: p.id, racine: p.id, intitule: t.intitule, court: t.court,
          enseignement: p.enseignement, niveaux: p.niveaux || [], enfants: [] };
        self.noeuds[p.id].enfants.push(t.id);
        (t.contenus || []).forEach(function (c) {
          self.noeuds[c.id] = { niveau: 'contenu', parent: t.id, racine: p.id, intitule: c.intitule, court: c.court,
            enseignement: p.enseignement, niveaux: p.niveaux || [], enfants: [] };
          self.noeuds[t.id].enfants.push(c.id);
        });
      });
    });

    this.notions = {};
    var n = refs.notions;
    (Array.isArray(n) ? n : (n || {}).notions || []).forEach(function (x) { if (x && x.id) self.notions[x.id] = x; });
  }

  /* ── La validation d'une fiche et de la vitrine ───────────────── */

  var LISTES_FICHE = [['enseignements', 'enseignements'], ['niveaux', 'niveaux'], ['types', 'types'], ['usages', 'usages'],
    ['langages', 'langages'], ['competences_pix', 'competences_pix']];
  var HOTES_GITHUB = ['github.com', 'gist.github.com', 'www.github.com'];
  var ROLES_NOTIONS = ['travaillees', 'prerequises', 'enseignees', 'evaluees'];
  var USAGES_CONTRAIRES = [['sans-installation', 'installation']]; // comme scripts/valider_donnees.py (T85)

  /* options : { schemas: { ressource, vitrine }, refs: Referentiels ou objet des référentiels,
                 ids: liste des identifiants des fiches, fichiers: fonction(chemin) → true, false ou null (inconnu) } */
  function Validation(options) {
    this.schemas = options.schemas;
    this.refs = options.refs instanceof Referentiels ? options.refs : new Referentiels(options.refs);
    this.ids = {};
    var self = this;
    (options.ids || []).forEach(function (id) { self.ids[id] = true; });
    this.fichiers = options.fichiers || function () { return null; };
  }

  Validation.prototype.valeur = function (erreur, champ, valeur, liste) {
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(valeur)) return false; // forme signalée par le schéma
    var possibles = this.refs.valeurs[liste] || {};
    if (!possibles[valeur]) {
      erreur(champ, '« ' + valeur + ' » n\'est pas dans le référentiel « ' + liste + ' » (valeurs possibles : '
        + Object.keys(possibles).join(', ') + ')');
      return false;
    }
    return true;
  };

  Validation.prototype.noeud = function (erreur, champ, nid, enseignements, niveaux) {
    var n = this.refs.noeuds[nid];
    if (!n) {
      var dernier = nid.split('.').pop();
      var proches = Object.keys(this.refs.noeuds).filter(function (k) { return k.split('.').pop() === dernier; }).slice(0, 3);
      erreur(champ, '« ' + nid + ' » n\'existe pas dans programmes.json' + (proches.length ? ' (vouliez-vous dire : ' + proches.join(', ') + ' ?)' : ''));
      return null;
    }
    if (enseignements && enseignements.indexOf(n.enseignement) < 0) {
      erreur(champ, '« ' + nid + ' » relève de l\'enseignement « ' + n.enseignement + ' », absent de « enseignements »');
    }
    return n;
  };

  /* Les erreurs d'une fiche : [[champ, message]]. nomFichier : « td1-poo.json ». */
  Validation.prototype.fiche = function (f, nomFichier) {
    var self = this, out = [];
    function erreur(champ, message) { out.push([champ, message]); }
    chercherSecrets(f, erreur);
    if (typeDe(f) !== 'object') { erreur('', 'une fiche est un objet { … }'); return out; }
    out = out.concat(new ValidateurSchema(this.schemas.ressource).erreurs(f));
    var rid = f.id;
    if (typeof rid !== 'string') return out;
    if (nomFichier && rid + '.json' !== nomFichier) {
      erreur('id', 'l\'identifiant « ' + rid + ' » ne correspond pas au nom du fichier ' + nomFichier);
    }

    LISTES_FICHE.forEach(function (cl) {
      (Array.isArray(f[cl[0]]) ? f[cl[0]] : []).forEach(function (val, i) {
        if (typeof val === 'string') self.valeur(erreur, joindre(cl[0], i), val, cl[1]);
      });
    });
    [['origine', 'origines'], ['statut', 'statuts']].forEach(function (cl) {
      if (typeof f[cl[0]] === 'string') self.valeur(erreur, cl[0], f[cl[0]], cl[1]);
    });
    var usages = Array.isArray(f.usages) ? f.usages : [];
    USAGES_CONTRAIRES.forEach(function (c) {
      if (usages.indexOf(c[0]) >= 0 && usages.indexOf(c[1]) >= 0) {
        erreur('usages', '« ' + c[0] + ' » et « ' + c[1] + ' » se contredisent : n\'en garder qu\'un');
      }
    });

    var vEns = this.refs.valeurs.enseignements || {};
    var ens = (f.enseignements || []).filter(function (e) { return vEns[e]; });
    if (ens.length < (f.enseignements || []).length) ens = null;
    (Array.isArray(f.programme) ? f.programme : []).forEach(function (nid, i) {
      if (typeof nid !== 'string') return;
      var n = self.noeud(erreur, joindre('programme', i), nid, ens);
      if (n && n.niveau === 'programme') erreur(joindre('programme', i), '« ' + nid + ' » est un programme entier : citer un thème ou un contenu');
    });

    (Array.isArray(f.liees) ? f.liees : []).forEach(function (l, i) {
      var cible = l && typeof l === 'object' ? l.ressource : null;
      var c = joindre(joindre('liees', i), 'ressource');
      if (cible === rid) erreur(c, 'une ressource ne peut pas être liée à elle-même');
      else if (typeof cible === 'string' && !self.ids[cible]) erreur(c, 'aucune fiche « ' + cible + ' » dans donnees/ressources/');
    });

    var notions = f.notions;
    if (notions && typeof notions === 'object' && !Array.isArray(notions)) {
      if (('enseignees' in notions || 'evaluees' in notions)) {
        erreur('notions', 'les rôles « enseignees » et « evaluees » sont remplacés par « travaillees » depuis le 13/11/2026');
      }
      if (Object.keys(this.refs.notions).length) {
        ROLES_NOTIONS.forEach(function (role) {
          (Array.isArray(notions[role]) ? notions[role] : []).forEach(function (nid, i) {
            if (typeof nid === 'string' && !self.refs.notions[nid]) {
              erreur(joindre(joindre('notions', role), i), '« ' + nid + ' » n\'est pas dans le thésaurus (donnees/referentiels/notions.json)');
            }
          });
        });
      }
    }

    var de = f.donnees_eleves;
    if (de && typeof de === 'object' && de.collecte !== true && de.facultative === true) {
      erreur('donnees_eleves.facultative', '« facultative » n\'a de sens que si « collecte » vaut true');
    }

    if (!Array.isArray(f.documents)) return out;
    var docs = f.documents.filter(function (d) { return d && typeof d === 'object'; });
    var roles = this.refs.valeurs.roles || {};
    function titreDoc(d) { return d.titre || (roles[d.role] || {}).libelle || d.role || '?'; }
    function ou(i, d, sous) { return 'documents[' + i + ']' + (sous ? '.' + sous : '') + ' (« ' + titreDoc(d) + ' »)'; }

    var principaux = [];
    docs.forEach(function (d, i) { if (d.principal === true) principaux.push(i); });
    if (!principaux.length) erreur('documents', 'aucun document principal : mettre « principal »: true sur le document qu\'ouvre le titre');
    else if (principaux.length > 1) erreur('documents', principaux.length + ' documents principaux (' + principaux.join(', ') + ') : il en faut exactement un');

    docs.forEach(function (d, i) {
      if (typeof d.role === 'string') self.valeur(erreur, ou(i, d, 'role'), d.role, 'roles');
      if (typeof d.format === 'string') self.valeur(erreur, ou(i, d, 'format'), d.format, 'formats');
      var r = roles[d.role] || {};
      if (typeof d.url === 'string') {
        var hote = '';
        try { hote = new URL(d.url).hostname.toLowerCase(); } catch (e) { hote = ''; }
        if (HOTES_GITHUB.indexOf(hote) >= 0 && !r.github_autorise) {
          erreur(ou(i, d, 'url'), d.principal
            ? 'le lien principal pointe vers une page GitHub : il doit mener directement à la ressource (page, fiche, PDF). Le dépôt peut figurer à part, avec le rôle « code-source ».'
            : 'lien vers une page GitHub : seul le rôle « code-source » le permet (pour un fichier, utiliser son lien direct ou le déposer sur le site)');
        }
      }
      if (typeof d.fichier === 'string') {
        var chemin = d.fichier.split(/[#?]/)[0];
        var present = self.fichiers(chemin);
        if (present === false) erreur(ou(i, d, 'fichier'), 'fichier introuvable dans le dépôt : « ' + chemin + ' »');
      }
    });
    return out;
  };

  /* Les erreurs de la vitrine : [[champ, message]] */
  Validation.prototype.vitrine = function (v) {
    var self = this, out = [];
    function erreur(champ, message) { out.push([champ, message]); }
    chercherSecrets(v, erreur);
    var schema = new ValidateurSchema(this.schemas.vitrine).erreurs(v);
    if (schema.length) return out.concat(schema);
    var noeuds = this.refs.noeuds;
    function placer(liste, champ) {
      liste.forEach(function (rid, k) {
        if (!self.ids[rid]) erreur(joindre(champ, k), 'aucune fiche « ' + rid + ' » dans donnees/ressources/');
      });
    }
    var vues = {};
    v.rubriques.forEach(function (rub, i) {
      var cr = joindre('rubriques', i);
      if (vues[rub.id]) erreur(joindre(cr, 'id'), 'la rubrique « ' + rub.id + ' » figure deux fois');
      vues[rub.id] = true;
      var prog = rub.programme;
      if (prog) {
        var n = self.noeud(erreur, joindre(cr, 'programme'), prog);
        if (n && n.niveau !== 'programme') { erreur(joindre(cr, 'programme'), '« ' + prog + ' » n\'est pas un programme entier (exemple : snt-2019)'); prog = null; }
        else if (!n) prog = null;
      }
      if (rub.reference_officielle) {
        var nr = self.noeud(erreur, joindre(cr, 'reference_officielle'), rub.reference_officielle);
        if (nr && nr.niveau !== 'programme') erreur(joindre(cr, 'reference_officielle'), '« ' + rub.reference_officielle + ' » n\'est pas un texte entier (exemple : pp-2018)');
      }
      var libres = {}, themes = {};
      rub.sections.forEach(function (s, j) {
        var cs = joindre(joindre(cr, 'sections'), j);
        var theme = s.programme;
        if (theme) {
          var n = self.noeud(erreur, joindre(cs, 'programme'), theme);
          if (n && n.niveau !== 'theme') erreur(joindre(cs, 'programme'), '« ' + theme + ' » n\'est pas un thème : une section suit un thème du programme');
          else if (n && prog && n.racine !== prog) erreur(joindre(cs, 'programme'), '« ' + theme + ' » n\'appartient pas au programme de la rubrique (' + prog + ')');
          else if (n && !prog) erreur(joindre(cs, 'programme'), 'la rubrique n\'a pas de « programme » : ses sections ne peuvent pas suivre un thème');
          if (themes[theme]) erreur(joindre(cs, 'programme'), 'le thème « ' + theme + ' » figure deux fois dans la rubrique');
          themes[theme] = true;
        } else {
          if (libres[s.id]) erreur(joindre(cs, 'id'), 'l\'identifiant « ' + s.id + ' » figure deux fois dans la rubrique');
          libres[s.id] = true;
        }
        placer(s.ressources, joindre(cs, 'ressources'));
        (s.sous_sections || []).forEach(function (ss, k) {
          var css = joindre(joindre(cs, 'sous_sections'), k);
          if (ss.programme) {
            var n2 = self.noeud(erreur, joindre(css, 'programme'), ss.programme);
            if (n2 && !theme) erreur(joindre(css, 'programme'), 'un contenu du programme se place sous la section de son thème, pas sous une section libre');
            else if (n2 && n2.parent !== theme) erreur(joindre(css, 'programme'), '« ' + ss.programme + ' » n\'est pas un contenu du thème « ' + theme + ' »');
          } else {
            if (libres[ss.id]) erreur(joindre(css, 'id'), 'l\'identifiant « ' + ss.id + ' » figure deux fois dans la rubrique');
            libres[ss.id] = true;
          }
          placer(ss.ressources, joindre(css, 'ressources'));
        });
      });
    });
    v.a_la_une.forEach(function (une, i) {
      var c = joindre('a_la_une', i);
      if (!self.ids[une.ressource]) { erreur(joindre(c, 'ressource'), 'aucune fiche « ' + une.ressource + ' » dans donnees/ressources/'); return; }
      var d1 = dateValide(une.debut), d2 = dateValide(une.fin);
      if (d1 && d2 && d1 > d2) erreur(c, 'la date de début est après la date de fin');
    });
    return out;
  };

  /* ── Lire un JSON en gardant la place de chaque valeur dans le texte ── */

  function analyser(texte) {
    var i = 0;
    function blanc() { while (i < texte.length && ' \t\n\r'.indexOf(texte[i]) >= 0) i++; }
    function valeur() {
      blanc();
      var debut = i, c = texte[i], noeud;
      if (c === '{') {
        i++; var enfants = {}, cles = [];
        blanc();
        if (texte[i] === '}') i++;
        else for (;;) {
          blanc();
          var k = chaine();
          blanc(); if (texte[i++] !== ':') throw new Error('« : » attendu à la position ' + i);
          enfants[k] = valeur(); cles.push(k);
          blanc();
          if (texte[i] === ',') { i++; continue; }
          if (texte[i] === '}') { i++; break; }
          throw new Error('« , » ou « } » attendu à la position ' + i);
        }
        noeud = { type: 'objet', enfants: enfants, cles: cles };
      } else if (c === '[') {
        i++; var elements = [];
        blanc();
        if (texte[i] === ']') i++;
        else for (;;) {
          elements.push(valeur());
          blanc();
          if (texte[i] === ',') { i++; continue; }
          if (texte[i] === ']') { i++; break; }
          throw new Error('« , » ou « ] » attendu à la position ' + i);
        }
        noeud = { type: 'liste', enfants: elements };
      } else if (c === '"') {
        chaine(); noeud = { type: 'simple' };
      } else {
        var m = /^(-?\d+(\.\d+)?([eE][+-]?\d+)?|true|false|null)/.exec(texte.slice(i, i + 40));
        if (!m) throw new Error('valeur illisible à la position ' + i);
        i += m[0].length; noeud = { type: 'simple' };
      }
      noeud.debut = debut; noeud.fin = i;
      noeud.texte = texte.slice(debut, i);
      noeud.valeur = JSON.parse(noeud.texte);
      noeud.lignes = noeud.texte.indexOf('\n') >= 0;
      return noeud;
    }
    function chaine() {
      if (texte[i] !== '"') throw new Error('texte entre guillemets attendu à la position ' + i);
      var debut = i++;
      while (i < texte.length && texte[i] !== '"') i += texte[i] === '\\' ? 2 : 1;
      i++;
      return JSON.parse(texte.slice(debut, i));
    }
    var r = valeur();
    blanc();
    if (i < texte.length) throw new Error('texte en trop après le JSON, à la position ' + i);
    return r;
  }

  /* ── Écrire un JSON : le texte d'origine là où rien ne change ───── */

  var LARGEUR = 100; // une liste ou un petit objet nouveaux tiennent sur une ligne en dessous

  function simple(v) { return v === null || typeof v !== 'object'; }

  function ecrireValeur(v, o, niveau, avant) {
    if (o && egal(v, o.valeur)) return o.texte;
    var ind = new Array(niveau + 1).join('  ');
    var ind2 = ind + '  ';
    if (simple(v)) return JSON.stringify(v);

    if (Array.isArray(v)) {
      if (!v.length) return '[]';
      var anciens = o && o.type === 'liste' ? o.enfants.slice() : [];
      var pris = [];
      var morceaux = v.map(function (x, k) {
        // le même élément dans l'ancienne liste (déplacé), sinon celui de même rang
        var j = -1;
        for (var a = 0; a < anciens.length; a++) if (pris.indexOf(a) < 0 && egal(anciens[a].valeur, x)) { j = a; break; }
        if (j < 0 && k < anciens.length && pris.indexOf(k) < 0 && !simple(x)) j = k;
        if (j >= 0) pris.push(j);
        return ecrireValeur(x, j >= 0 ? anciens[j] : null, niveau + 1, 0);
      });
      var enLigne = v.every(simple) && (o && o.type === 'liste' ? !o.lignes : true);
      if (enLigne) {
        var l = '[' + morceaux.join(', ') + ']';
        if ((o && o.type === 'liste' && !o.lignes) || avant + l.length <= LARGEUR) return l;
      }
      return '[\n' + morceaux.map(function (x) { return ind2 + x; }).join(',\n') + '\n' + ind + ']';
    }

    var cles = Object.keys(v);
    if (!cles.length) return '{}';
    var anc = o && o.type === 'objet' ? o.enfants : {};
    var paires = cles.map(function (k) {
      var tete = JSON.stringify(k) + ': ';
      return tete + ecrireValeur(v[k], anc[k] || null, niveau + 1, ind2.length + tete.length);
    });
    var objetEnLigne = cles.every(function (k) { return simple(v[k]); })
      && (o && o.type === 'objet' ? !o.lignes : cles.length >= 2);
    if (objetEnLigne) {
      var lo = '{ ' + paires.join(', ') + ' }';
      if ((o && o.type === 'objet' && !o.lignes) || avant + lo.length <= LARGEUR) return lo;
    }
    return '{\n' + paires.map(function (x) { return ind2 + x; }).join(',\n') + '\n' + ind + '}';
  }

  /* Le nouveau texte du fichier ; texteOrigine peut manquer (nouveau fichier) */
  function ecrire(valeur, texteOrigine) {
    var o = null, fin = '\n';
    if (texteOrigine) {
      try { o = analyser(texteOrigine); } catch (e) { o = null; }
      fin = /\n$/.test(texteOrigine) ? '\n' : '';
    }
    return ecrireValeur(valeur, o, 0, 0) + fin;
  }

  return {
    ValidateurSchema: ValidateurSchema,
    Referentiels: Referentiels,
    Validation: Validation,
    chercherSecrets: chercherSecrets,
    analyser: analyser,
    ecrire: ecrire,
    egal: egal,
    copie: copie,
    canonique: canonique
  };
});
