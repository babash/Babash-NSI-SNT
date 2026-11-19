/* QuizzNSI : le rendu des diapositives et des questions (MIT, Babash - NSI Tani Malandi).
   Les mêmes fonctions servent à la page projetée, au mode autonome et à la version imprimable. */
(function (racine) {
  'use strict';
  const Q = racine.QuizzNSI;
  const t = Q.texte, e = Q.echapper;

  const liste = (items, cl) => '<ul class="' + (cl || '') + '">' + items.map(x => '<li>' + t(x) + '</li>').join('') + '</ul>';

  Q.rendreOptions = function (q, opts) {
    opts = opts || {};
    return '<div class="options" role="' + (opts.boutons ? 'group' : 'list') + '" aria-label="Les quatre réponses possibles">' + q.options.map((o, i) => {
      const contenu = Q.pastille(i) + '<span class="opt-texte">' + (o.texte ? t(o.texte) : '') + (o.code ? Q.blocCode(o.code, { numeros: false }) : '') + '</span>';
      const lib = 'Réponse ' + Q.LETTRES[i] + ' (' + Q.NOMS_FORMES[i] + ')';
      return opts.boutons
        ? '<button type="button" class="option o' + i + '" data-choix="' + i + '" aria-label="' + e(lib) + ' : ' + e((o.texte || o.code.join(' ')).replace(/`/g, '')) + '">' + contenu + '</button>'
        : '<div class="option o' + i + '" role="listitem" data-choix="' + i + '">' + contenu + '</div>';
    }).join('') + '</div>';
  };

  Q.rendreEnonce = function (q, total) {
    return '<header class="q-tete"><p class="q-num">Question ' + q.numero + ' sur ' + total + '</p><h2 class="q-nom">' + t(q.nom) + '</h2>'
      + '<p class="objectif"><span>Objectif</span> ' + t(q.objectif) + '</p></header>'
      + '<div class="q-corps"><div class="q-texte">' + q.enonce.map(p => '<p>' + t(p) + '</p>').join('')
      + (q.code ? Q.blocCode(q.code) : '') + '</div>' + (q.schema ? Q.schema(q.schema) : '') + '</div>';
  };

  Q.rendreTrace = function (tr) {
    if (!tr) return '';
    return '<div class="trace"><table><caption>Trace pas à pas</caption><thead><tr>' + tr.colonnes.map(c => '<th scope="col">' + t(c) + '</th>').join('') + '</tr></thead><tbody>'
      + tr.lignes.map(l => '<tr>' + l.map((c, i) => i ? '<td>' + t(c) + '</td>' : '<th scope="row">' + t(c) + '</th>').join('') + '</tr>').join('') + '</tbody></table></div>';
  };

  // La correction d'une question : la réponse choisie (ou rien), la bonne réponse, l'explication,
  // puis le feedback de chaque option.
  Q.rendreCorrection = function (q, choix, opts) {
    opts = opts || {};
    const b = q.bonne, juste = choix === b;
    let h = '';
    if (choix != null) {
      h += '<div class="verdict ' + (juste ? 'ok' : 'ko') + '" role="status"><span class="symbole" aria-hidden="true">' + (juste ? '✓' : '✗') + '</span><div><p class="v-titre">'
        + (juste ? 'Bonne réponse' : 'Ta réponse : ' + Q.LETTRES[choix] + '. La bonne réponse est ' + Q.LETTRES[b] + '.') + '</p><p>' + t(q.options[choix].feedback) + '</p></div></div>';
    } else if (!opts.projection) {
      h += '<div class="verdict neutre" role="status"><span class="symbole" aria-hidden="true">•</span><div><p class="v-titre">La bonne réponse est ' + Q.LETTRES[b] + '.</p></div></div>';
    }
    h += '<p class="explication"><span>À retenir</span> ' + t(q.explication) + '</p>';
    h += Q.rendreTrace(q.trace);
    const fbs = '<ol class="feedbacks">' + q.options.map((o, i) => '<li class="' + (i === b ? 'bonne' : '') + '">' + Q.pastille(i) + '<div><p class="fb-titre">' + (i === b ? 'Bonne réponse' : 'Erreur fréquente') + '</p><p>' + t(o.feedback) + '</p></div></li>').join('') + '</ol>';
    h += opts.tousOuverts ? fbs : '<details class="autres"><summary>Lire l\'explication de chaque réponse</summary>' + fbs + '</details>';
    return h;
  };

  Q.rendreDiapo = function (cours, d, opts) {
    opts = opts || {};
    const total = cours.questions.length;
    if (d.type === 'titre') {
      return '<section class="diapo d-titre"><p class="surtitre">' + e(cours.niveau) + '</p><h1>' + t(d.titre || cours.titre) + '</h1>'
        + (cours.sous_titre ? '<p class="sous-titre">' + t(cours.sous_titre) + '</p>' : '')
        + (d.texte ? d.texte.map(p => '<p class="intro">' + t(p) + '</p>').join('') : '')
        + '<div class="colonnes"><div class="cadre"><h2>Critères de réussite</h2>' + liste(cours.criteres || []) + '</div>'
        + '<div class="cadre"><h2>Conventions</h2>' + liste(cours.conventions || []) + '</div></div></section>';
    }
    if (d.type === 'notion') {
      return '<section class="diapo d-notion"><p class="surtitre">Notion</p><h2 class="d-titre-notion">' + t(d.titre) + '</h2><div class="n-corps"><div class="n-texte">' + liste(d.texte || [], 'puces')
        + (d.code ? Q.blocCode(d.code) : '') + (d.vocabulaire ? '<p class="vocab"><span>En anglais</span> ' + t(d.vocabulaire) + '</p>' : '') + '</div>'
        + (d.schema ? Q.schema(d.schema) : '') + '</div></section>';
    }
    if (d.type === 'bilan') {
      const tb = d.tableau;
      return '<section class="diapo d-bilan"><h2 class="d-titre-notion">' + t(d.titre || 'À retenir') + '</h2>'
        + (tb ? '<div class="tableau"><table><thead><tr>' + tb.colonnes.map(c => '<th scope="col">' + t(c) + '</th>').join('') + '</tr></thead><tbody>' + tb.lignes.map(l => '<tr>' + l.map((c, i) => i ? '<td>' + t(c) + '</td>' : '<th scope="row">' + t(c) + '</th>').join('') + '</tr>').join('') + '</tbody></table></div>' : '')
        + (d.ticket ? '<div class="cadre ticket"><h3>Ticket de sortie</h3>' + liste(d.ticket) + '</div>' : '') + (opts.fin || '') + '</section>';
    }
    if (d.type === 'question') {
      return '<section class="diapo d-question" data-q="' + d.numero + '">' + Q.rendreEnonce(d, total)
        + '<div class="zone-options">' + Q.rendreOptions(d, { boutons: !!opts.boutons }) + '</div><div class="zone-correction" aria-live="polite"></div></section>';
    }
    return '';
  };
})(window);
