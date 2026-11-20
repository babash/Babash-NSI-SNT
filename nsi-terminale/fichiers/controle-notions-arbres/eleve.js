/* Contrôle de notions : page élève
   L'élève compose ; la page ne corrige pas (la clé n'est pas chargée ici).
   À la fin : un code de copie et son QR code, rien n'est envoyé.
   Babash - NSI Tani Malandi · MIT */

(function () {
  'use strict';
  var CN = window.CN, D = CN.DONNEES, $ = function (id) { return document.getElementById(id); };
  var CLE_STOCKAGE = 'controle-' + D.id + '-v' + D.version;
  var etat = null; /* { pseudo, classe, sujet, graine, debut, reponses[12], rendu } */

  CN.appliquerTheme();

  /* ── Stockage local (brouillon, pour ne rien perdre si le téléphone se met en veille) ──
     Gardé UN JOUR au plus après le début de la copie (règle des codes d'accès :
     ce que la page garde sur l'appareil pour un·e élève expire au bout d'un jour),
     effacé au chargement s'il est périmé. Jamais repris sans le choix de l'élève. */
  var UN_JOUR = 24 * 60 * 60 * 1000;
  function sauver() {
    try { localStorage.setItem(CLE_STOCKAGE, JSON.stringify(etat)); } catch (e) { /* navigation privée : tant pis */ }
  }
  function relire() {
    var c = null;
    try { var t = localStorage.getItem(CLE_STOCKAGE); c = t ? JSON.parse(t) : null; } catch (e) { c = null; }
    var valide = c && typeof c.debut === 'number' && Date.now() - c.debut < UN_JOUR && Date.now() >= c.debut - 60000 &&
      c.sujet && D.sujets[c.sujet] && Array.isArray(c.reponses) && c.reponses.length === D.questions.length;
    if (c && !valide) effacer();
    return valide ? c : null;
  }
  function effacer() {
    try { localStorage.removeItem(CLE_STOCKAGE); } catch (e) { /* rien */ }
  }

  /* ── Écran d'accueil ── */
  var params = new URLSearchParams(location.search);
  var sujetImpose = params.get('sujet');
  if (sujetImpose && D.sujets[sujetImpose]) {
    $('choix-sujet').hidden = true;
    $('sujet-fixe').hidden = false;
    $('sujet-fixe').textContent = 'Sujet ' + sujetImpose + ' (donné par le lien de ton enseignant·e).';
  } else sujetImpose = null;

  $('form-accueil').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var pseudo = $('pseudo').value.trim().replace(/\s+/g, ' ');
    var coche = document.querySelector('input[name=sujet]:checked');
    var sujet = sujetImpose || (coche && coche.value);
    var msg = '';
    if (!pseudo) msg = 'Écris ton prénom ou un pseudo.';
    else if (!sujet) msg = 'Choisis le sujet donné par ton enseignant·e.';
    if (msg) { $('erreur-accueil').textContent = msg; $('erreur-accueil').hidden = false; return; }
    var graine = 0;
    try { graine = crypto.getRandomValues(new Uint32Array(1))[0]; } catch (e) { graine = Math.floor(Math.random() * 4294967295); }
    etat = {
      pseudo: pseudo, classe: $('classe').value.trim().toUpperCase(), sujet: sujet, graine: graine,
      debut: Date.now(), reponses: D.questions.map(function (q) { return q.type === 'schema' ? [] : ''; }), rendu: false
    };
    sauver();
    ouvrirCopie();
  });

  /* ── La copie ── */
  function coloriser(code) {
    return CN.echapper(code).replace(/\b(class|def|if|is|None|return)\b/g, '<span class="kw">$1</span>');
  }

  function ordreQuestions() {
    /* L'ordre des questions et des options est mélangé pour chaque copie. */
    var hasard = CN.aleatoire(etat.graine);
    return CN.melanger(D.questions.map(function (q, i) { return i; }), hasard);
  }

  function construireQuestion(i, rang) {
    var q = D.questions[i], s = D.sujets[etat.sujet], id = 'r-' + q.id;
    var sec = document.createElement('section');
    sec.className = 'carte q';
    sec.id = 'bloc-' + q.id;
    var h = '<h2><span class="num">Question ' + (rang + 1) + '</span><span>' + CN.echapper(q.nom) + '</span></h2>';
    var texte = CN.echapper(CN.enonce(q, etat.sujet))
      .replace(/print\(([^)]*)\)/, '<code>print($1)</code>')
      .replace(/\bclasse Noeud\b/, 'classe <code>Noeud</code>')
      .replace(/\bfonction taille\b/, 'fonction <code>taille</code>')
      .replace(/^La variable a /, 'La variable <code>a</code> ');
    if (q.type === 'qcu') {
      var hasard = CN.aleatoire(etat.graine ^ 0x5bd1e995);
      var opts = CN.melanger(s.abr_options, hasard);
      h += '<fieldset><legend class="enonce">' + texte + '</legend>' + opts.map(function (o) {
        return '<label class="choix"><input type="radio" name="' + id + '" value="' + o[0] + '"><span>' + CN.echapper(o[1]) + '</span></label>';
      }).join('') + '</fieldset>';
    } else if (q.type === 'schema') {
      var lettres = CN.lettresSquelette(s.squelette);
      var valeurs = s.insertion.slice().sort(function (a, b) { return a - b; });
      h += '<p class="enonce" id="e-' + q.id + '">' + texte + '</p>';
      h += '<div class="figure">' + CN.svgArbre(s.squelette, { cases: true, titre: 'Schéma de l\'ABR à compléter : cases ' + lettres.join(', ') }) + '</div>';
      h += '<div class="cases" role="group" aria-labelledby="e-' + q.id + '">' + lettres.map(function (l, k) {
        return '<label>Case ' + l + ' <select data-case="' + k + '" name="' + id + '"><option value="">…</option>' +
          valeurs.map(function (v) { return '<option value="' + v + '">' + v + '</option>'; }).join('') + '</select></label>';
      }).join('') + '</div>';
      h += '<p class="aide">Chaque valeur va dans une seule case.</p>';
    } else {
      h += '<label class="enonce" for="' + id + '">' + texte + '</label>';
      if (q.id === 'q10' || q.id === 'q11') h += '<pre class="code"><code>' + coloriser(D.code_noeud) + '</code></pre>';
      var aide = { valeur: 'Une seule valeur.', ensemble: 'Les valeurs, séparées par des espaces, dans n\'importe quel ordre.',
        liste: 'Les valeurs dans l\'ordre du parcours, séparées par des espaces.', ligne: 'Écrire ce qui remplace les points, après return.' }[q.type];
      var mode = q.type === 'valeur' ? ' inputmode="numeric"' : '';
      var classe = q.type === 'ligne' ? ' class="code"' : '';
      if (q.type === 'ligne') {
        /* Réponse en code : zone de plusieurs lignes, chasse fixe, Tab et indentation automatique (zone-code.js) */
        h += '<div class="ligne-code"><code aria-hidden="true">return</code>' +
          '<textarea id="' + id + '" name="' + id + '" class="zone-code" rows="2" autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="300" aria-describedby="a-' + q.id + '"></textarea></div>';
        aide += ' Tab indente ; Échap puis Tab pour sortir de la zone.';
      } else h += '<input type="text" id="' + id + '" name="' + id + '"' + mode + classe + ' autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="80" aria-describedby="a-' + q.id + '">';
      h += '<p class="aide" id="a-' + q.id + '">' + aide + '</p>';
    }
    sec.innerHTML = h;
    return sec;
  }

  function remplir() {
    D.questions.forEach(function (q, i) {
      var r = etat.reponses[i], id = 'r-' + q.id;
      if (q.type === 'qcu') {
        var b = document.querySelector('input[name="' + id + '"][value="' + r + '"]');
        if (b) b.checked = true;
      } else if (q.type === 'schema') {
        document.querySelectorAll('select[name="' + id + '"]').forEach(function (sel) { sel.value = (r || [])[Number(sel.dataset.case)] || ''; });
      } else $(id).value = r || '';
    });
  }

  function lire() {
    D.questions.forEach(function (q, i) {
      var id = 'r-' + q.id;
      if (q.type === 'qcu') {
        var b = document.querySelector('input[name="' + id + '"]:checked');
        etat.reponses[i] = b ? b.value : '';
      } else if (q.type === 'schema') {
        var t = [];
        document.querySelectorAll('select[name="' + id + '"]').forEach(function (sel) { t[Number(sel.dataset.case)] = sel.value; });
        etat.reponses[i] = t.every(function (v) { return v === ''; }) ? [] : t;
      } else etat.reponses[i] = $(id).value.trim().slice(0, q.type === 'ligne' ? 300 : 80);
    });
  }

  function sansReponse() {
    var manque = [];
    ordre.forEach(function (i, rang) {
      var r = etat.reponses[i];
      var vide = Array.isArray(r) ? r.filter(function (v) { return v !== ''; }).length < CN.lettresSquelette(D.sujets[etat.sujet].squelette).length : !r;
      $('bloc-' + D.questions[i].id).classList.toggle('repondue', !vide);
      if (vide) manque.push(rang + 1);
    });
    return manque;
  }

  function majProgression() {
    var manque = sansReponse(), n = D.questions.length;
    $('progression').textContent = (n - manque.length) + ' sur ' + n + ' répondues';
    $('reste').textContent = manque.length ? 'Sans réponse complète : question' + (manque.length > 1 ? 's ' : ' ') + manque.join(', ') + '.' : 'Toutes les questions ont une réponse.';
  }

  var ordre = [];
  function ouvrirCopie() {
    $('accueil').hidden = true; $('rendu').hidden = true; $('copie').hidden = false;
    var s = D.sujets[etat.sujet];
    $('barre-pseudo').textContent = etat.pseudo;
    $('barre-sujet').textContent = 'Sujet ' + etat.sujet;
    $('convention').textContent = D.convention.replace(/^Rappel de convention : /, '');
    $('consigne').textContent = D.consigne;
    var titre = 'Arbre binaire du sujet ' + etat.sujet + '. ' + CN.texteArbre(s.arbre);
    $('arbre').innerHTML = CN.svgArbre(s.arbre, { titre: titre });
    $('arbre-dialogue').innerHTML = CN.svgArbre(s.arbre, { titre: titre });
    var form = $('questions');
    form.innerHTML = '';
    ordre = ordreQuestions();
    ordre.forEach(function (i, rang) { form.appendChild(construireQuestion(i, rang)); });
    remplir();
    majProgression();
    chrono();
    window.scrollTo(0, 0);
  }

  $('questions').addEventListener('input', function () { lire(); sauver(); majProgression(); });
  $('questions').addEventListener('change', function () { lire(); sauver(); majProgression(); });

  function chrono() {
    if (!etat) return;
    var min = Math.floor((Date.now() - etat.debut) / 60000);
    $('chrono').textContent = min + ' min sur ' + D.duree;
  }
  setInterval(chrono, 20000);

  /* L'arbre en grand, sans perdre sa place */
  $('voir-arbre').addEventListener('click', function () { $('dialogue-arbre').showModal(); });
  $('fermer-arbre').addEventListener('click', function () { $('dialogue-arbre').close(); });

  /* ── Rendre la copie ── */
  $('rendre').addEventListener('click', function () {
    lire();
    var manque = sansReponse();
    $('dialogue-reste').textContent = manque.length
      ? 'Il reste ' + manque.length + ' question' + (manque.length > 1 ? 's' : '') + ' sans réponse complète (' + manque.join(', ') + '). Tu peux encore les compléter.'
      : 'Toutes les questions ont une réponse. Ta copie ne pourra plus être corrigée ici : ton enseignant·e la corrigera.';
    $('dialogue-rendre').showModal();
  });
  $('annuler-rendre').addEventListener('click', function () { $('dialogue-rendre').close(); });
  $('confirmer-rendre').addEventListener('click', function () {
    $('dialogue-rendre').close();
    etat.rendu = true;
    etat.fin = Date.now();
    sauver();
    ouvrirRendu();
  });

  function codeCopie() {
    var duree = Math.max(0, Math.round(((etat.fin || Date.now()) - etat.debut) / 1000));
    return CN.encoder([D.version, etat.pseudo, etat.classe, etat.sujet, Math.floor(etat.debut / 60000), duree, etat.graine, etat.reponses]);
  }

  function ouvrirRendu() {
    $('accueil').hidden = true; $('copie').hidden = true; $('rendu').hidden = false;
    var code = codeCopie();
    $('rendu-qui').textContent = etat.pseudo + (etat.classe ? ' (' + etat.classe + ')' : '') + ' · Sujet ' + etat.sujet;
    $('code-copie').value = code;
    var qr = qrcode(0, 'M');
    qr.addData(code, 'Alphanumeric');
    qr.make();
    $('qr').innerHTML = qr.createSvgTag({ cellSize: 4, margin: 4, scalable: true });
    window.scrollTo(0, 0);
  }

  $('copier').addEventListener('click', function () {
    var t = $('code-copie');
    function ok() { $('copie-ok').textContent = 'Code copié.'; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t.value).then(ok, function () { t.select(); });
    else { t.select(); try { document.execCommand('copy'); ok(); } catch (e) { /* sélection laissée à l'élève */ } }
  });
  $('revenir').addEventListener('click', function () { etat.rendu = false; sauver(); ouvrirCopie(); });
  function toutEffacer() {
    if (!confirm('Effacer cette copie de ce navigateur ? Ses réponses seront perdues.')) return;
    effacer(); etat = null;
    location.href = location.pathname + location.search;
  }
  $('effacer').addEventListener('click', toutEffacer);
  $('effacer-copie').addEventListener('click', toutEffacer);

  /* ── Une copie commencée sur ce navigateur (moins d'un jour) ──
     Poste partagé : on ne l'ouvre jamais d'office. L'accueil demande de la
     reprendre ou d'en commencer une autre, qui l'efface. */
  var ancien = relire();
  if (ancien) {
    $('copie-existante').hidden = false;
    $('form-accueil').hidden = true;
    $('existante-qui').textContent = ancien.pseudo + (ancien.classe ? ' (' + ancien.classe + ')' : '') + ', sujet ' + ancien.sujet +
      (ancien.rendu ? ', déjà rendue' : ', pas encore rendue');
    $('reprendre').addEventListener('click', function () {
      etat = relire();
      if (!etat) { location.reload(); return; }
      if (etat.rendu) ouvrirRendu(); else ouvrirCopie();
    });
    $('autre-copie').addEventListener('click', function () {
      effacer();
      $('copie-existante').hidden = true;
      $('form-accueil').hidden = false;
      $('pseudo').focus();
    });
  }
})();
