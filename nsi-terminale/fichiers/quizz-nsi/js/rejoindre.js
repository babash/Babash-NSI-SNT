/* QuizzNSI : la page élève, pensée pour un téléphone (MIT, Babash - NSI Tani Malandi).
   L'élève entre le code de la séance et un prénom ou un pseudo, puis répond aux questions.
   Rien n'est enregistré en ligne. Sur l'appareil : le code, le pseudo et un identifiant de séance,
   12 heures au plus, pour revenir après une coupure avec ses points (même code et même pseudo). */
(function () {
  'use strict';
  const Q = window.QuizzNSI, $ = Q.$;
  const DOUZE_HEURES = 12 * 3600 * 1000;
  let moi = null, seance = null, phase = null, question = null, attenteHote = null, hoteVu = false, renvoi = null, chrono = null, total = 0;

  /* ── L'entrée ───────────────────────────── */
  function afficherEntree(message) {
    if (seance) { seance.fermer(); seance = null; }
    clearInterval(renvoi); clearInterval(chrono); clearTimeout(attenteHote);
    $('jeu').hidden = true; $('entree').hidden = false; $('quitter').hidden = true;
    $('moi').textContent = ''; $('points').textContent = '';
    $('erreurPseudo').textContent = message || '';
    if (message) $('champPseudo').focus();
  }

  function rejoindre(ev) {
    if (ev) ev.preventDefault();
    const code = Q.lireCode($('champCode').value), f = Q.filtrerPseudo($('champPseudo').value);
    $('erreurCode').textContent = code ? '' : 'Le code de la séance a 4 lettres (sans I ni O), comme ABCD.';
    $('erreurPseudo').textContent = f.ok ? '' : f.raison;
    if (!code) { $('champCode').focus(); return; }
    if (!f.ok) { $('champPseudo').focus(); return; }
    const ancien = Q.stock.lire('eleve', null);
    // même code et même pseudo dans les 12 heures : on garde son identifiant, donc ses points
    const memes = ancien && ancien.code === code && ancien.jusqua > Date.now() && typeof ancien.pseudo === 'string' && Q.clePseudo(ancien.pseudo) === Q.clePseudo(f.pseudo) && /^[0-9a-f]{16}$/.test(ancien.id);
    const id = memes ? ancien.id : Q.nouvelId();
    moi = { id, pseudo: f.pseudo, code };
    Q.stock.ecrire('eleve', { id, pseudo: f.pseudo, code, jusqua: Date.now() + DOUZE_HEURES });
    Q.session.ecrire('eleve', moi);
    entrer();
  }

  function entrer() {
    $('entree').hidden = true; $('jeu').hidden = false; $('quitter').hidden = false;
    $('moi').textContent = moi.pseudo;
    majPoints();
    ecran('<div class="attente"><p class="grand">Connexion…</p><p>Séance ' + Q.echapper(moi.code) + '</p></div>');
    hoteVu = false;
    seance = Q.ouvrirSeance(moi.code, { id: moi.id, pseudo: moi.pseudo, role: 'eleve' }, { onMessage, onPresence, onEtat });
  }

  function onEtat(e) {
    const z = $('connexion');
    if (e === 'connexion') { z.className = 'etat'; z.textContent = 'Connexion à la séance…'; }
    else if (e === 'connecte') {
      z.className = 'etat ok'; z.textContent = 'Connecté·e à la séance ' + moi.code + '.';
      seance.envoyer({ t: 'bonjour', id: moi.id });
      clearTimeout(attenteHote);
      attenteHote = setTimeout(() => { if (!hoteVu) ecran('<div class="attente"><p class="grand">En attente de l\'enseignant·e</p><p>Vérifie le code de la séance : <strong>' + Q.echapper(moi.code) + '</strong>. S\'il est faux, quitte et entre le bon code.</p></div>'); }, 9000);
    } else if (e === 'erreur' || e === 'ferme') {
      z.className = 'etat ko';
      z.innerHTML = 'Pas de connexion à la séance : vérifie le réseau (wifi ou données mobiles), puis réessaie. '
        + '<button type="button" class="bouton petit" id="reessayer">Réessayer</button> Tu peux aussi suivre le cours seul·e : <a href="revision.html">réviser seul·e</a>.';
      const r = $('reessayer'); if (r) r.addEventListener('click', () => { if (seance) seance.fermer(); entrer(); });
    }
  }

  function onPresence(liste) {
    const vu = liste.some(p => p && p.role === 'hote');
    if (vu && !hoteVu) { hoteVu = true; if (!phase) ecran(attente('L\'enseignant·e est là. Regarde l\'écran : le cours va commencer.')); seance.envoyer({ t: 'bonjour', id: moi.id }); }
    hoteVu = vu || hoteVu;
  }

  /* ── Les messages de la séance ──────────── */
  const chaines = v => Array.isArray(v) && v.every(x => typeof x === 'string');
  const pourMoi = m => typeof m.id === 'string' && m.id === moi.id;
  function onMessage(m) {
    if (!moi || !m || typeof m.t !== 'string') return;
    hoteVu = true; clearTimeout(attenteHote);
    if (m.t === 'retire' && pourMoi(m)) { Q.stock.oublier('eleve'); Q.session.oublier('eleve'); afficherEntree('L\'enseignant·e a retiré ce pseudo. Choisis-en un autre : ton prénom ou un pseudo, jamais ton nom de famille.'); return; }
    if (m.t === 'refus' && pourMoi(m)) { Q.session.oublier('eleve'); afficherEntree(m.raison === 'pris' ? 'Ce pseudo est déjà pris dans la séance : choisis-en un autre.' : 'Ce pseudo n\'est pas accepté : choisis-en un autre.'); return; }
    if (m.t === 'recus' && question && m.qid === question.qid && Array.isArray(m.ids) && m.ids.includes(moi.id)) { question.recu = true; clearInterval(renvoi); majEnvoyee(); return; }
    if (m.t === 'attente') { phase = 'attente'; question = null; ecran(attente('Regarde l\'écran : la suite arrive.')); return; }
    if (m.t === 'notion' && typeof m.titre === 'string' && chaines(m.texte)) { phase = 'notion'; question = null; afficherNotion(m); return; }
    if (m.t === 'question') { afficherQuestion(m); return; }
    if (m.t === 'fermee' && question && m.qid === question.qid) { question.ferme = true; clearInterval(chrono); if (question.choix == null) ecran(attente('Temps écoulé : la correction arrive à l\'écran.')); return; }
    if (m.t === 'correction') { afficherCorrection(m); return; }
    if (m.t === 'fin') { afficherFin(m); }
  }

  function ecran(html) { $('ecran').innerHTML = html; }
  const attente = texte => '<div class="attente"><p class="grand">' + Q.echapper(moi.pseudo) + ', tu es dans la séance.</p><p>' + Q.echapper(texte) + '</p></div>';
  function majPoints() { $('points').textContent = total + ' pts'; }

  function afficherNotion(m) {
    const d = { type: 'notion', titre: m.titre, texte: m.texte.slice(0, 6), code: chaines(m.code) ? m.code : null, schema: m.schema && m.schema.type !== 'svg' ? m.schema : null };
    ecran('<p class="aide">Le cours, en même temps que l\'écran :</p>' + Q.rendreDiapo({ questions: [] }, d, {}));
  }

  function nettoyerQuestion(m) {
    if (typeof m.qid !== 'string' || !Array.isArray(m.options) || m.options.length !== 4) return null;
    return {
      qid: m.qid, numero: Number.isInteger(m.n) ? m.n : 0, total: Number.isInteger(m.total) ? m.total : 0,
      nom: String(m.nom || ''), objectif: String(m.objectif || ''), enonce: chaines(m.enonce) ? m.enonce : [],
      code: chaines(m.code) ? m.code : null, schema: m.schema && typeof m.schema === 'object' && m.schema.type !== 'svg' ? m.schema : null,
      options: m.options.map(o => ({ texte: o && typeof o.texte === 'string' ? o.texte : '', code: o && chaines(o.code) ? o.code : null, feedback: o && typeof o.feedback === 'string' ? o.feedback : '' })),
    };
  }

  function afficherQuestion(m) {
    const q = nettoyerQuestion(m);
    if (!q) return;
    if (question && question.qid === q.qid && phase === 'question') { if (m.ferme) question.ferme = true; return; } // déjà affichée
    phase = 'question';
    const ancienne = Q.session.lire('rep:' + moi.code + ':' + q.qid, null);
    question = { qid: q.qid, q, choix: Number.isInteger(ancienne) ? ancienne : null, recu: false, ferme: !!m.ferme, fin: Number.isFinite(m.reste) && m.reste != null ? Date.now() + m.reste : null };
    ecran('<section class="d-question">' + Q.rendreEnonce(q, q.total) + '<p class="chrono" id="chrono" aria-live="off"></p>' + Q.rendreOptions(q, { boutons: true }) + '<p class="envoyee" id="envoyee" role="status"></p></section>');
    $('ecran').querySelectorAll('button.option').forEach(b => b.addEventListener('click', () => choisir(+b.dataset.choix)));
    if (question.choix != null || question.ferme) bloquer();
    if (question.choix != null) { majEnvoyee(); envoyerReponse(); }
    clearInterval(chrono);
    if (question.fin && !question.ferme) { majChrono(); chrono = setInterval(majChrono, 500); }
    $('ecran').focus({ preventScroll: true }); window.scrollTo(0, 0);
    Q.annoncer('Question ' + q.numero + ' : ' + q.nom.replace(/`/g, ''));
  }
  function majChrono() {
    const z = $('chrono'); if (!z || !question || !question.fin) return;
    const s = Math.max(0, Math.ceil((question.fin - Date.now()) / 1000));
    z.textContent = '⏱ ' + s + ' s';
    if (s === 0) clearInterval(chrono);
  }
  function bloquer() {
    $('ecran').querySelectorAll('button.option').forEach(b => {
      b.disabled = true;
      if (+b.dataset.choix === question.choix) { b.classList.add('choisie'); if (!b.querySelector('.etiquette')) b.insertAdjacentHTML('beforeend', '<span class="etiquette">Ta réponse</span>'); }
    });
  }
  function choisir(c) {
    if (!question || question.choix != null || question.ferme) return;
    question.choix = c;
    Q.session.ecrire('rep:' + moi.code + ':' + question.qid, c);
    bloquer(); majEnvoyee(); envoyerReponse();
    Q.annoncer('Réponse ' + Q.LETTRES[c] + ' envoyée.');
  }
  function envoyerReponse() {
    const envoi = () => { if (question && question.choix != null && !question.recu && !question.ferme) seance.envoyer({ t: 'rep', id: moi.id, qid: question.qid, c: question.choix }); else clearInterval(renvoi); };
    clearInterval(renvoi); envoi(); renvoi = setInterval(envoi, 2000);
  }
  function majEnvoyee() {
    const z = $('envoyee'); if (!z || !question) return;
    z.textContent = question.recu ? 'Réponse ' + Q.LETTRES[question.choix] + ' reçue. Attends la correction à l\'écran.' : 'Réponse ' + Q.LETTRES[question.choix] + ' envoyée…';
  }

  function suiteHtml(suite) {
    if (!Array.isArray(suite) || !suite.length) return '';
    return '<ol class="suite" aria-label="Tes réponses, question par question">' + suite.map((r, i) => '<li class="' + (r === 'juste' ? 'j' : r === 'faux' ? 'f' : '') + '" title="Question jouée n° ' + (i + 1) + '"><span aria-hidden="true">' + (r === 'juste' ? '✓' : r === 'faux' ? '✗' : '–') + '</span><span class="visuel-cache">' + (r === 'juste' ? 'juste' : r === 'faux' ? 'faux' : 'sans réponse') + '</span></li>').join('') + '</ol>';
  }

  function afficherCorrection(m) {
    const q = nettoyerQuestion(Object.assign({}, m, { options: m.options }));
    if (!q || !Number.isInteger(m.bonne) || m.bonne < 0 || m.bonne > 3) return;
    clearInterval(renvoi); clearInterval(chrono);
    phase = 'correction';
    q.bonne = m.bonne; q.explication = typeof m.explication === 'string' ? m.explication : '';
    const r = m.res && typeof m.res === 'object' ? m.res[moi.id] : null;
    const choix = r && Number.isInteger(r.c) ? r.c : (question && question.qid === q.qid ? question.choix : null);
    question = { qid: q.qid, q, choix, recu: true, ferme: true };
    if (r && Number.isFinite(r.total)) { total = r.total; majPoints(); }
    let h = '<section class="d-question"><header class="q-tete"><p class="q-num">Question ' + q.numero + ' sur ' + q.total + ' · correction</p><h2 class="q-nom">' + Q.texte(q.nom) + '</h2></header>';
    if (choix == null) h += '<div class="verdict neutre" role="status"><span class="symbole" aria-hidden="true">•</span><div><p class="v-titre">Pas de réponse cette fois. La bonne réponse est ' + Q.LETTRES[q.bonne] + '.</p></div></div>';
    h += Q.rendreCorrection(q, choix);
    if (r && r.detail && r.gain > 0) {
      const d = r.detail, parts = [];
      if (d.juste) parts.push(d.juste + ' bonne réponse'); if (d.participation) parts.push(d.participation + ' participation');
      if (d.rapidite) parts.push(d.rapidite + ' rapidité'); if (d.rebond) parts.push(d.rebond + ' rebond');
      h += '<p class="gains">+' + r.gain + ' points <small>(' + parts.join(', ') + ')</small></p>';
      if (d.rebond) h += '<p class="rebonds">Beau rebond : tu t\'es repris·e juste après une erreur.</p>';
    }
    if (r && r.bilan) {
      const b = r.bilan;
      h += '<div class="cadre"><p><strong>' + b.justes + ' juste' + (b.justes > 1 ? 's' : '') + '</strong> sur ' + b.repondues + ' réponse' + (b.repondues > 1 ? 's' : '') + (b.serie > 1 ? ' · série en cours : ' + b.serie : '') + (b.rebonds ? ' · rebonds : ' + b.rebonds : '') + '</p>' + suiteHtml(b.suite) + '</div>';
    }
    if (Array.isArray(m.podium) && m.podium.length) {
      const k = m.podium.findIndex(p => p && p.pseudo === moi.pseudo);
      if (k >= 0) h += '<p class="rebonds">Tu es sur le podium en ce moment.</p>';
    }
    ecran(h + '</section>');
    $('ecran').focus({ preventScroll: true }); window.scrollTo(0, 0);
    Q.annoncer(choix == null ? 'Correction : pas de réponse.' : choix === q.bonne ? 'Bonne réponse.' : 'Pas cette fois. Lis l\'explication.');
  }

  function afficherFin(m) {
    phase = 'fin'; question = null; clearInterval(renvoi); clearInterval(chrono);
    const r = m.res && typeof m.res === 'object' ? m.res[moi.id] : null;
    let h = '<section class="attente"><p class="grand">Fin de la séance</p>';
    if (r && r.bilan) {
      total = Number.isFinite(r.total) ? r.total : total; majPoints();
      const b = r.bilan;
      h += '<p class="gains">' + total + ' points</p><p><strong>' + b.justes + ' sur ' + (m.total || b.repondues) + '</strong> bonnes réponses · meilleure série : ' + b.meilleure + ' · rebonds : ' + b.rebonds + '</p>' + suiteHtml(b.suite);
      if (Number.isInteger(r.place) && r.place <= 3 && Array.isArray(m.podium)) h += '<p class="rebonds">Bravo, tu es sur le podium : ' + r.place + (r.place === 1 ? 're' : 'e') + ' place.</p>';
      if (Array.isArray(r.arevoir) && r.arevoir.length) h += '<p>À revoir : question' + (r.arevoir.length > 1 ? 's' : '') + ' ' + r.arevoir.filter(Number.isInteger).join(', ') + '.</p>';
      else h += '<p>Tout juste : tu peux aider un·e camarade.</p>';
    } else h += '<p>Merci d\'avoir suivi le cours.</p>';
    const id = typeof m.cours === 'string' && /^[a-z0-9-]{1,60}$/.test(m.cours) ? m.cours : 'piles-files';
    h += '<p><a class="bouton fort" href="revision.html?cours=' + id + '">Revoir le cours seul·e</a></p></section>';
    ecran(h);
  }

  /* ── Démarrage ──────────────────────────── */
  function demarrer() {
    Q.theme();
    const p = new URLSearchParams(location.search), code = Q.lireCode(p.get('s'));
    const ancien = Q.stock.lire('eleve', null);
    if (code) $('champCode').value = code;
    else if (ancien && ancien.jusqua > Date.now()) $('champCode').value = ancien.code;
    if (ancien && ancien.jusqua > Date.now() && typeof ancien.pseudo === 'string') $('champPseudo').value = ancien.pseudo;
    $('entree').addEventListener('submit', rejoindre);
    $('quitter').addEventListener('click', () => { Q.stock.oublier('eleve'); Q.session.oublier('eleve'); afficherEntree(''); $('champPseudo').value = ''; });
    // la page rechargée dans le même onglet revient directement dans la séance
    const onglet = Q.session.lire('eleve', null);
    if (onglet && (!code || code === onglet.code) && Q.lireCode(onglet.code) && Q.filtrerPseudo(onglet.pseudo).ok && /^[0-9a-f]{16}$/.test(onglet.id)) {
      moi = { id: onglet.id, pseudo: onglet.pseudo, code: onglet.code };
      entrer();
    }
  }
  demarrer();
})();
