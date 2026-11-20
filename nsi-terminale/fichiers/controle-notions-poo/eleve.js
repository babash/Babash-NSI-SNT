/* Contrôle de notions : page élève
   L'élève compose ; la page ne corrige pas (la clé n'est pas chargée ici).
   À la fin : un code de copie et son QR code, rien n'est envoyé.
   D'après la page élève du contrôle sur les arbres binaires (T108).
   Babash - NSI Tani Malandi · MIT */

(function () {
  'use strict';
  var CN = window.CN, D = CN.DONNEES, $ = function (id) { return document.getElementById(id); };
  var CLE_STOCKAGE = 'controle-' + D.id + '-v' + D.version;
  var etat = null; /* { pseudo, classe, sujet, graine, debut, reponses[], rendu } */

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
      debut: Date.now(), reponses: D.questions.map(function () { return ''; }), rendu: false
    };
    sauver();
    ouvrirCopie();
  });

  /* ── La copie ── */
  var ordre = [];       /* indices des questions, dans l'ordre de la copie */
  function ordreQuestions() {
    /* L'ordre des questions (et des options) est mélangé pour chaque copie ;
       les questions d'un même programme restent ensemble, dans l'ordre. */
    var hasard = CN.aleatoire(etat.graine);
    return [].concat.apply([], CN.melanger(CN.unites(), hasard));
  }

  function construireQuestion(i, rang) {
    var q = D.questions[i], x = CN.qs(etat.sujet, q), id = 'r-' + q.id;
    var sec = document.createElement('section');
    sec.className = 'carte q';
    sec.id = 'bloc-' + q.id;
    var h = '<h2><span class="num">Question ' + (rang + 1) + '</span><span>' + CN.echapper(q.nom) + '</span></h2>';
    var enonce = CN.texte(x.enonce);
    var prog = x.programme ? CN.programmeHTML(etat.sujet, x.programme) : '';
    if (q.type === 'qcu') {
      var hasard = CN.aleatoire(etat.graine ^ (0x5bd1e995 + i * 0x9E3779B1));
      var opts = CN.melanger(x.options, hasard);
      h += prog + '<fieldset><legend class="enonce">' + enonce + '</legend>' + opts.map(function (o) {
        return '<label class="choix"><input type="radio" name="' + id + '" value="' + o[0] + '"><span>' + CN.texte(o[1]) + '</span></label>';
      }).join('') + '</fieldset>';
    } else {
      h += prog + '<label class="enonce" for="' + id + '">' + enonce + '</label>';
      var aide = (D.aides || {})[q.type] || '';
      var mode = q.type === 'valeur' ? ' inputmode="numeric"' : '';
      var classe = q.type === 'ligne' ? ' class="code"' : '';
      var champ = q.type === 'ligne'
        /* Réponse en code : zone de plusieurs lignes, chasse fixe, Tab et indentation automatique (zone-code.js) */
        ? '<textarea id="' + id + '" name="' + id + '" class="zone-code" rows="2" autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="300" aria-describedby="a-' + q.id + '"></textarea>'
        : '<input type="text" id="' + id + '" name="' + id + '"' + mode + classe +
          ' autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="80" aria-describedby="a-' + q.id + '">';
      if (q.type === 'ligne' && (x.avant || x.apres)) {
        champ = '<div class="ligne-code">' + (x.avant ? '<code aria-hidden="true">' + CN.echapper(x.avant) + '</code>' : '') + champ +
          (x.apres ? '<code aria-hidden="true">' + CN.echapper(x.apres) + '</code>' : '') + '</div>';
        aide += ' Déjà écrit : ' + [x.avant ? '« ' + x.avant + ' » avant' : '', x.apres ? '« ' + x.apres + ' » après' : ''].filter(Boolean).join(', ') + '.';
      }
      if (q.type === 'ligne') aide += ' Tab indente ; Échap puis Tab pour sortir de la zone.';
      h += champ + '<p class="aide" id="a-' + q.id + '">' + CN.echapper(aide) + '</p>';
    }
    sec.innerHTML = h;
    return sec;
  }

  function construireContexte(groupe, numeros) {
    var c = D.sujets[etat.sujet].contextes[groupe];
    var sec = document.createElement('section');
    sec.className = 'carte contexte';
    sec.innerHTML = '<h2>Pour les questions ' + numeros.slice(0, -1).join(', ') + (numeros.length > 1 ? ' et ' : '') + numeros[numeros.length - 1] + '</h2>' +
      '<p>' + CN.texte(c.texte) + '</p>' + (c.programme ? CN.programmeHTML(etat.sujet, c.programme) : '');
    return sec;
  }

  function remplir() {
    D.questions.forEach(function (q, i) {
      var r = etat.reponses[i], id = 'r-' + q.id;
      if (q.type === 'qcu') {
        var b = document.querySelector('input[name="' + id + '"][value="' + r + '"]');
        if (b) b.checked = true;
      } else $(id).value = r || '';
    });
  }

  function lire() {
    D.questions.forEach(function (q, i) {
      var id = 'r-' + q.id;
      if (q.type === 'qcu') {
        var b = document.querySelector('input[name="' + id + '"]:checked');
        etat.reponses[i] = b ? b.value : '';
      } else etat.reponses[i] = q.type === 'ligne' ? $(id).value.replace(/\s+$/, '').slice(0, 300) : $(id).value.trim().slice(0, 80);
    });
  }

  function sansReponse() {
    var manque = [];
    ordre.forEach(function (i, rang) {
      var vide = !etat.reponses[i];
      $('bloc-' + D.questions[i].id).classList.toggle('repondue', !vide);
      if (vide) manque.push(rang + 1);
    });
    return manque;
  }

  function majProgression() {
    var manque = sansReponse(), n = D.questions.length;
    $('progression').textContent = (n - manque.length) + ' sur ' + n + ' répondues';
    $('reste').textContent = manque.length ? 'Sans réponse : question' + (manque.length > 1 ? 's ' : ' ') + manque.join(', ') + '.' : 'Toutes les questions ont une réponse.';
  }

  function ouvrirCopie() {
    $('accueil').hidden = true; $('rendu').hidden = true; $('copie').hidden = false;
    var S = D.sujets[etat.sujet];
    $('barre-pseudo').textContent = etat.pseudo;
    $('barre-sujet').textContent = 'Sujet ' + etat.sujet;
    $('convention').innerHTML = '<ul>' + D.convention.map(function (t) { return '<li>' + CN.texte(t) + '</li>'; }).join('') + '</ul>';
    $('consigne').textContent = D.consigne;
    if (S.commun) {
      $('figure-commune').hidden = false;
      $('voir-commun').hidden = false;
      $('voir-commun').textContent = S.commun.bouton || 'Voir le programme';
      $('titre-commun').innerHTML = CN.texte(S.commun.titre);
      $('titre-dialogue-commun').innerHTML = CN.texte(S.commun.titre);
      $('texte-commun').innerHTML = S.commun.texte ? CN.texte(S.commun.texte) : '';
      $('commun').innerHTML = CN.programmeHTML(etat.sujet, S.commun.programme).replace(/<p class="prog-titre">.*?<\/p>/, '');
      $('commun-dialogue').innerHTML = $('commun').innerHTML;
    }
    var form = $('questions');
    form.innerHTML = '';
    ordre = ordreQuestions();
    var vus = {};
    ordre.forEach(function (i, rang) {
      var q = D.questions[i];
      if (q.groupe && !vus[q.groupe] && S.contextes && S.contextes[q.groupe]) {
        vus[q.groupe] = true;
        var numeros = [];
        ordre.forEach(function (j, r) { if (D.questions[j].groupe === q.groupe) numeros.push(r + 1); });
        form.appendChild(construireContexte(q.groupe, numeros));
      }
      form.appendChild(construireQuestion(i, rang));
    });
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

  /* Le programme commun en grand, sans perdre sa place */
  $('voir-commun').addEventListener('click', function () { $('dialogue-commun').showModal(); });
  $('fermer-commun').addEventListener('click', function () { $('dialogue-commun').close(); });

  /* ── Rendre la copie ── */
  $('rendre').addEventListener('click', function () {
    lire();
    var manque = sansReponse();
    $('dialogue-reste').textContent = manque.length
      ? 'Il reste ' + manque.length + ' question' + (manque.length > 1 ? 's' : '') + ' sans réponse (' + manque.join(', ') + '). Tu peux encore les compléter.'
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
