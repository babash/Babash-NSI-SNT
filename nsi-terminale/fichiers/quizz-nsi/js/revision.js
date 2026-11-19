/* QuizzNSI : le mode autonome (MIT, Babash - NSI Tani Malandi).
   Les diapositives et les questions, corrigées dans le navigateur. Rien n'est envoyé :
   la progression (première réponse à chaque question) reste dans le stockage de l'appareil. */
(function () {
  'use strict';
  const Q = window.QuizzNSI, $ = Q.$;
  let cours, diapos = [], index = 0, etat;
  const cle = () => 'revision:' + cours.id;
  const sauver = () => Q.stock.ecrire(cle(), etat);

  // Le stockage a pu être modifié : on ne garde que des choix 0 à 3 pour des questions du cours.
  function etatRelu(v) {
    const e = { premiers: {}, essais: {}, vus: {}, index: 0 }, ids = new Set(cours.questions.map(q => q.id));
    const choix = c => Number.isInteger(c) && c >= 0 && c <= 3;
    if (!v || typeof v !== 'object') return e;
    for (const id of ids) {
      if (v.premiers && choix(v.premiers[id])) e.premiers[id] = v.premiers[id];
      if (v.essais && Array.isArray(v.essais[id])) e.essais[id] = v.essais[id].filter(choix).slice(0, 8);
      if (v.vus && v.vus[id] === true) e.vus[id] = true;
    }
    if (Number.isInteger(v.index) && v.index >= 0 && v.index < cours.diapositives.length) e.index = v.index;
    return e;
  }

  function liste() {
    return $('questionsSeules').checked ? cours.diapositives.filter(d => d.type !== 'notion') : cours.diapositives;
  }

  function afficher(i, focus) {
    index = Math.max(0, Math.min(diapos.length - 1, i));
    const d = diapos[index];
    etat.index = cours.diapositives.indexOf(d); sauver();
    const scene = $('scene');
    scene.innerHTML = Q.rendreDiapo(cours, d, { boutons: true, fin: d.type === 'bilan' ? bilanPerso() : '' });
    const nq = d.type === 'question' ? ' · question ' + d.numero + ' sur ' + cours.questions.length : '';
    $('compteur').textContent = 'Diapositive ' + (index + 1) + ' sur ' + diapos.length + nq;
    $('barre').style.width = ((index + 1) / diapos.length * 100) + '%';
    $('prec').disabled = index === 0;
    $('suiv').disabled = index === diapos.length - 1;
    if (d.type === 'question') brancherQuestion(d);
    if (d.type === 'bilan') brancherBilan();
    try { history.replaceState(null, '', '#' + (cours.diapositives.indexOf(d) + 1)); } catch (e) { /* rien */ }
    if (focus !== false) scene.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }

  function marquer(q, essais, corrige) {
    const sc = $('scene');
    sc.querySelectorAll('.option').forEach(b => {
      const i = +b.dataset.choix;
      b.classList.remove('choisie', 'bonne-rep');
      const vieux = b.querySelector('.etiquette'); if (vieux) vieux.remove();
      let etiq = '';
      if (corrige && i === q.bonne) { b.classList.add('bonne-rep'); etiq = '✓ Bonne réponse'; }
      else if (essais.includes(i)) { b.classList.add('choisie'); etiq = '✗ Déjà essayée'; b.disabled = true; }
      if (corrige) b.disabled = true;
      if (etiq) b.insertAdjacentHTML('beforeend', '<span class="etiquette">' + etiq + '</span>');
    });
    sc.querySelector('.options').classList.toggle('corrigees', corrige);
  }

  function brancherQuestion(q) {
    const sc = $('scene'), zone = sc.querySelector('.zone-correction');
    const e = etat.essais[q.id] || [];
    const corrige = e.includes(q.bonne) || etat.vus[q.id] === true;
    const montrer = (choix, tout) => {
      const essais = etat.essais[q.id] || [];
      const fini = tout || choix === q.bonne;
      marquer(q, essais, fini);
      if (fini) zone.innerHTML = Q.rendreCorrection(q, choix);
      else zone.innerHTML = '<div class="verdict ko" role="status"><span class="symbole" aria-hidden="true">✗</span><div><p class="v-titre">Pas encore : ta réponse est ' + Q.LETTRES[choix] + '.</p><p>' + Q.texte(q.options[choix].feedback) + '</p></div></div>'
        + '<p>Essaie une autre réponse, ou <button type="button" class="bouton petit" id="voirCorrection">affiche la correction</button></p>';
      const v = $('voirCorrection');
      if (v) v.addEventListener('click', () => { etat.vus[q.id] = true; sauver(); montrer(null, true); });
      Q.annoncer(fini ? (choix === q.bonne ? 'Bonne réponse.' : 'Correction affichée. La bonne réponse est ' + Q.LETTRES[q.bonne] + '.') : 'Ce n\'est pas la bonne réponse. Lis l\'explication puis essaie encore.');
    };
    sc.querySelectorAll('button.option').forEach(b => b.addEventListener('click', () => {
      const c = +b.dataset.choix;
      if (!(q.id in etat.premiers)) etat.premiers[q.id] = c;
      etat.essais[q.id] = (etat.essais[q.id] || []).concat(c);
      sauver();
      montrer(c, false);
    }));
    if (corrige) montrer(e.includes(q.bonne) ? q.bonne : null, true);
    else if (e.length) { marquer(q, e, false); }
  }

  function bilanPerso() {
    const qs = cours.questions, faites = qs.filter(q => q.id in etat.premiers);
    const justes = faites.filter(q => etat.premiers[q.id] === q.bonne);
    const arevoir = qs.filter(q => q.id in etat.premiers && etat.premiers[q.id] !== q.bonne);
    let h = '<div class="cadre" style="margin-top:14px"><h3>Ton bilan</h3><p><strong>' + justes.length + ' sur ' + qs.length + '</strong> du premier coup'
      + (faites.length < qs.length ? ' (' + (qs.length - faites.length) + ' question' + (qs.length - faites.length > 1 ? 's' : '') + ' sans réponse)' : '') + '.</p>';
    if (arevoir.length) h += '<p>À revoir :</p><ul class="cours-liste">' + arevoir.map(q => '<li><button class="bouton petit" type="button" data-aller="' + q.id + '">Question ' + q.numero + ' · ' + Q.texte(q.nom) + '</button></li>').join('') + '</ul>';
    else if (faites.length) h += '<p>Tout juste du premier coup : bravo ! Tu peux aider un·e camarade.</p>';
    h += '<p><button class="bouton" type="button" id="recommencer">Recommencer à zéro</button> <a class="bouton" href="imprimer.html?cours=' + encodeURIComponent(cours.id) + '">Version à imprimer</a></p></div>';
    return h;
  }
  function brancherBilan() {
    $('scene').querySelectorAll('[data-aller]').forEach(b => b.addEventListener('click', () => {
      $('questionsSeules').checked = false; diapos = liste();
      afficher(diapos.findIndex(d => d.id === b.dataset.aller));
    }));
    const r = $('recommencer');
    if (r) r.addEventListener('click', () => { etat = { premiers: {}, essais: {}, vus: {}, index: 0 }; sauver(); afficher(0); });
  }

  document.addEventListener('keydown', ev => {
    if (ev.target.closest && ev.target.closest('input, textarea, select')) return;
    if (ev.altKey || ev.ctrlKey || ev.metaKey) return;
    if (ev.key === 'ArrowRight' || ev.key === 'PageDown') { if (index < diapos.length - 1) { ev.preventDefault(); afficher(index + 1); } }
    else if (ev.key === 'ArrowLeft' || ev.key === 'PageUp') { if (index > 0) { ev.preventDefault(); afficher(index - 1); } }
    else if (/^[abcd]$/i.test(ev.key)) {
      const b = $('scene').querySelector('button.option[data-choix="' + 'abcd'.indexOf(ev.key.toLowerCase()) + '"]');
      if (b && !b.disabled) { ev.preventDefault(); b.click(); }
    }
  });

  async function demarrer() {
    Q.theme();
    try { cours = await Q.chargerCours(Q.idCours()); }
    catch (e) { Q.erreurPage($('scene'), e.message); document.querySelector('.nav-diapos').hidden = true; return; }
    document.title = 'QuizzNSI · ' + cours.titre + ' · réviser seul·e';
    $('titreCours').textContent = cours.titre + ' · réviser seul·e';
    etat = etatRelu(Q.stock.lire(cle(), null));
    $('questionsSeules').checked = Q.stock.lire('questions-seules', false) === true;
    diapos = liste();
    $('questionsSeules').addEventListener('change', () => {
      Q.stock.ecrire('questions-seules', $('questionsSeules').checked);
      const actuelle = diapos[index]; diapos = liste();
      const k = diapos.indexOf(actuelle); afficher(k >= 0 ? k : 0, false);
    });
    $('prec').addEventListener('click', () => afficher(index - 1, false));
    $('suiv').addEventListener('click', () => afficher(index + 1, false));
    const h = parseInt(location.hash.slice(1), 10);
    const depart = Number.isInteger(h) && h >= 1 ? cours.diapositives[h - 1] : cours.diapositives[etat.index || 0];
    const k = diapos.indexOf(depart);
    afficher(k >= 0 ? k : 0, false);
    window.addEventListener('hashchange', () => {
      const n = parseInt(location.hash.slice(1), 10), d = cours.diapositives[n - 1];
      if (!d || d === diapos[index]) return;
      if (!diapos.includes(d)) { $('questionsSeules').checked = false; diapos = liste(); }
      afficher(diapos.indexOf(d), false);
    });
  }
  demarrer();
})();
