/* QuizzNSI : la page élève, pensée pour un téléphone (MIT, Babash - NSI Tani Malandi).
   L'élève entre le code de la séance et un prénom ou un pseudo, puis répond aux questions.
   Sécurité : chaque message reçu est validé par js/messages.js (schéma strict) ; le texte des
   notions et des questions vient du fichier du cours (cours/<id>.json, même site), jamais du canal ;
   les valeurs reçues (points, séries, pseudos du podium) s'affichent par textContent seulement.
   Rien n'est enregistré en ligne. Sur l'appareil : le code, le pseudo et un identifiant de séance,
   12 heures au plus, pour revenir après une coupure avec ses points (même code et même pseudo). */
(function () {
  'use strict';
  const Q = window.QuizzNSI, $ = Q.$, el = Q.el;
  const DOUZE_HEURES = 12 * 3600 * 1000;
  let moi = null, seance = null, phase = null, question = null, attenteHote = null, hoteVu = false, renvoi = null, chrono = null, total = 0, numero = 0;
  const lesCours = new Map();

  function obtenirCours(id) {
    if (!lesCours.has(id)) lesCours.set(id, Q.chargerCours(id).catch(() => { lesCours.delete(id); return null; }));
    return lesCours.get(id);
  }

  /* ── L'entrée ───────────────────────────── */
  function afficherEntree(message) {
    if (seance) { seance.fermer(); seance = null; }
    clearInterval(renvoi); clearInterval(chrono); clearTimeout(attenteHote);
    $('jeu').hidden = true; $('entree').hidden = false; $('quitter').hidden = true;
    $('moi').textContent = ''; $('points').textContent = '';
    $('erreurPseudo').textContent = message || '';
    phase = null; question = null; total = 0;
    if (message) $('champPseudo').focus();
  }

  function rejoindre(ev) {
    if (ev) ev.preventDefault();
    const code = Q.lireCode($('champCode').value), f = Q.filtrerPseudo($('champPseudo').value);
    $('erreurCode').textContent = code ? '' : 'Le code de la séance a 4 lettres (sans I ni O), comme ABCD.';
    $('erreurPseudo').textContent = f.ok ? '' : f.raison;
    if (!code) { $('champCode').focus(); return; }
    if (!f.ok) { $('champPseudo').focus(); return; }
    const ancien = lireAncien();
    // même code et même pseudo dans les 12 heures : on garde son identifiant, donc ses points
    const memes = ancien && ancien.code === code && Q.clePseudo(ancien.pseudo) === Q.clePseudo(f.pseudo);
    const id = memes ? ancien.id : Q.nouvelId();
    moi = { id, pseudo: f.pseudo, code };
    Q.stock.ecrire('eleve', { id, pseudo: f.pseudo, code, jusqua: Date.now() + DOUZE_HEURES });
    Q.session.ecrire('eleve', moi);
    entrer();
  }

  // Le stockage peut avoir été modifié : chaque valeur relue est contrôlée.
  function lireAncien() {
    const a = Q.stock.lire('eleve', null);
    if (!a || typeof a !== 'object' || !Number.isFinite(a.jusqua) || a.jusqua < Date.now()) return null;
    const f = Q.filtrerPseudo(a.pseudo);
    return Q.lireCode(a.code) === a.code && f.ok && f.pseudo === a.pseudo && Q.messages.estId(a.id) ? { id: a.id, pseudo: a.pseudo, code: a.code } : null;
  }
  function lireOnglet() {
    const a = Q.session.lire('eleve', null);
    if (!a || typeof a !== 'object') return null;
    const f = Q.filtrerPseudo(a.pseudo);
    return Q.lireCode(a.code) === a.code && f.ok && f.pseudo === a.pseudo && Q.messages.estId(a.id) ? { id: a.id, pseudo: a.pseudo, code: a.code } : null;
  }

  function entrer() {
    $('entree').hidden = true; $('jeu').hidden = false; $('quitter').hidden = false;
    $('moi').textContent = moi.pseudo;
    majPoints();
    ecran(el('div', { class: 'attente' }, el('p', { class: 'grand' }, 'Connexion…'), el('p', {}, 'Séance ' + moi.code)));
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
      attenteHote = setTimeout(() => {
        if (!hoteVu) ecran(el('div', { class: 'attente' }, el('p', { class: 'grand' }, 'En attente de l\'enseignant·e'),
          el('p', {}, 'Vérifie le code de la séance : ', el('strong', {}, moi.code), '. S\'il est faux, quitte et entre le bon code.')));
      }, 9000);
    } else if (e === 'erreur' || e === 'ferme') {
      z.className = 'etat ko'; z.textContent = '';
      const b = el('button', { type: 'button', class: 'bouton petit' }, 'Réessayer');
      b.addEventListener('click', () => { if (seance) seance.fermer(); entrer(); });
      z.append('Pas de connexion à la séance : vérifie le réseau (wifi ou données mobiles), puis réessaie. ', b,
        ' Tu peux aussi suivre le cours seul·e : ', el('a', { href: 'revision.html' }, 'réviser seul·e'), '.');
    }
  }

  function onPresence(liste) {
    const vu = Array.isArray(liste) && liste.some(p => { const v = Q.messages.presence(p); return v && v.role === 'hote'; });
    if (vu && !hoteVu) { hoteVu = true; if (!phase) ecran(attente('L\'enseignant·e est là. Regarde l\'écran : le cours va commencer.')); seance.envoyer({ t: 'bonjour', id: moi.id }); }
  }

  /* ── Les messages de la séance ──────────── */
  function onMessage(brut) {
    if (!moi) return;
    const m = Q.messages.versEleve(brut, moi.id);
    if (!m) return; // message non conforme : ignoré
    hoteVu = true; clearTimeout(attenteHote);
    if (m.t === 'retire') { if (m.pourMoi) { Q.stock.oublier('eleve'); Q.session.oublier('eleve'); afficherEntree('L\'enseignant·e a retiré ce pseudo. Choisis-en un autre : ton prénom ou un pseudo, jamais ton nom de famille.'); } return; }
    if (m.t === 'refus') { if (m.pourMoi) { Q.session.oublier('eleve'); afficherEntree(m.raison === 'pris' ? 'Ce pseudo est déjà pris dans la séance : choisis-en un autre.' : 'Ce pseudo n\'est pas accepté : choisis-en un autre.'); } return; }
    if (m.t === 'recus') { if (m.pourMoi && question && m.qid === question.qid) { question.recu = true; clearInterval(renvoi); majEnvoyee(); } return; }
    if (m.t === 'attente') { phase = 'attente'; question = null; ecran(attente('Regarde l\'écran : la suite arrive.')); return; }
    if (m.t === 'fermee') { if (question && m.qid === question.qid) { question.ferme = true; clearInterval(chrono); if (question.choix == null) ecran(attente('Temps écoulé : la correction arrive à l\'écran.')); } return; }
    const n = ++numero; // seul le dernier message reçu s'affiche, même si son cours arrive plus tard
    obtenirCours(m.cours).then(cours => {
      if (!cours || n !== numero) return;
      if (m.t === 'notion') afficherNotion(cours, m);
      else if (m.t === 'question') afficherQuestion(cours, m);
      else if (m.t === 'correction') afficherCorrection(cours, m);
      else if (m.t === 'fin') afficherFin(cours, m);
    });
  }

  function ecran(noeud) { const z = $('ecran'); z.textContent = ''; z.appendChild(noeud); }
  const attente = texte => el('div', { class: 'attente' }, el('p', { class: 'grand' }, moi.pseudo + ', tu es dans la séance.'), el('p', {}, texte));
  function majPoints() { $('points').textContent = total + ' pts'; }
  const trouverQuestion = (cours, qid) => cours.questions.find(q => q.id === qid) || null;

  function afficherNotion(cours, m) {
    const d = cours.diapositives[m.n];
    if (!d || d.type !== 'notion') return;
    phase = 'notion'; question = null;
    const z = el('div', {}, el('p', { class: 'aide' }, 'Le cours, en même temps que l\'écran :'));
    z.appendChild(Q.fragmentCours(Q.rendreDiapo(cours, d, {})));
    ecran(z);
  }

  function afficherQuestion(cours, m) {
    const q = trouverQuestion(cours, m.qid);
    if (!q) return;
    if (question && question.qid === q.id && phase === 'question') { if (m.ferme) question.ferme = true; return; } // déjà affichée
    phase = 'question';
    const ancienne = Q.session.lire('rep:' + moi.code + ':' + q.id, null);
    question = { qid: q.id, q, choix: Number.isInteger(ancienne) && ancienne >= 0 && ancienne <= 3 ? ancienne : null, recu: false, ferme: m.ferme, fin: m.reste != null ? Date.now() + m.reste : null };
    const s = el('section', { class: 'd-question' });
    s.appendChild(Q.fragmentCours(Q.rendreEnonce(q, cours.questions.length)));
    s.appendChild(el('p', { class: 'chrono', id: 'chrono', 'aria-live': 'off' }));
    s.appendChild(Q.fragmentCours(Q.rendreOptions(q, { boutons: true })));
    s.appendChild(el('p', { class: 'envoyee', id: 'envoyee', role: 'status' }));
    ecran(s);
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
      if (+b.dataset.choix === question.choix) { b.classList.add('choisie'); if (!b.querySelector('.etiquette')) b.appendChild(el('span', { class: 'etiquette' }, 'Ta réponse')); }
    });
  }
  function choisir(c) {
    if (!question || question.choix != null || question.ferme || !(c >= 0 && c <= 3)) return;
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

  function suite(s) {
    if (!s.length) return null;
    return el('ol', { class: 'suite', 'aria-label': 'Tes réponses, question par question' }, s.map((r, i) =>
      el('li', { class: r === 'juste' ? 'j' : r === 'faux' ? 'f' : '', title: 'Question jouée n° ' + (i + 1) },
        el('span', { 'aria-hidden': 'true' }, r === 'juste' ? '✓' : r === 'faux' ? '✗' : '–'),
        el('span', { class: 'visuel-cache' }, r === 'juste' ? 'juste' : r === 'faux' ? 'faux' : 'sans réponse'))));
  }
  const pluriel = (n, mot) => n + ' ' + mot + (n > 1 ? 's' : '');

  function afficherCorrection(cours, m) {
    const q = trouverQuestion(cours, m.qid);
    if (!q) return;
    clearInterval(renvoi); clearInterval(chrono);
    phase = 'correction';
    const r = m.moi;
    const choix = r ? r.c : (question && question.qid === q.id ? question.choix : null);
    question = { qid: q.id, q, choix, recu: true, ferme: true };
    if (r) { total = r.total; majPoints(); }
    const s = el('section', { class: 'd-question' },
      el('header', { class: 'q-tete' }, el('p', { class: 'q-num' }, 'Question ' + q.numero + ' sur ' + cours.questions.length + ' · correction'),
        (() => { const h = el('h2', { class: 'q-nom' }); h.appendChild(Q.fragmentCours(Q.texte(q.nom))); return h; })()));
    if (choix == null) s.appendChild(el('div', { class: 'verdict neutre', role: 'status' }, el('span', { class: 'symbole', 'aria-hidden': 'true' }, '•'),
      el('div', {}, el('p', { class: 'v-titre' }, 'Pas de réponse cette fois. La bonne réponse est ' + Q.LETTRES[q.bonne] + '.'))));
    s.appendChild(Q.fragmentCours(Q.rendreCorrection(q, choix)));
    if (r && r.detail && r.gain > 0) {
      const d = r.detail, parts = [];
      if (d.juste) parts.push(d.juste + ' bonne réponse'); if (d.participation) parts.push(d.participation + ' participation');
      if (d.rapidite) parts.push(d.rapidite + ' rapidité'); if (d.rebond) parts.push(d.rebond + ' rebond');
      s.appendChild(el('p', { class: 'gains' }, '+' + r.gain + ' points ', el('small', {}, '(' + parts.join(', ') + ')')));
      if (d.rebond) s.appendChild(el('p', { class: 'rebonds' }, 'Beau rebond : tu t\'es repris·e juste après une erreur.'));
    }
    if (r) {
      const b = r.bilan;
      s.appendChild(el('div', { class: 'cadre' }, el('p', {}, el('strong', {}, pluriel(b.justes, 'juste')), ' sur ' + pluriel(b.repondues, 'réponse')
        + (b.serie > 1 ? ' · série en cours : ' + b.serie : '') + (b.rebonds ? ' · rebonds : ' + b.rebonds : '')), suite(b.suite)));
    }
    if (m.podium && m.podium.some(p => p.pseudo === moi.pseudo)) s.appendChild(el('p', { class: 'rebonds' }, 'Tu es sur le podium en ce moment.'));
    ecran(s);
    $('ecran').focus({ preventScroll: true }); window.scrollTo(0, 0);
    Q.annoncer(choix == null ? 'Correction : pas de réponse.' : choix === q.bonne ? 'Bonne réponse.' : 'Pas cette fois. Lis l\'explication.');
  }

  function afficherFin(cours, m) {
    phase = 'fin'; question = null; clearInterval(renvoi); clearInterval(chrono);
    const r = m.moi, s = el('section', { class: 'attente' }, el('p', { class: 'grand' }, 'Fin de la séance'));
    if (r) {
      total = r.total; majPoints();
      const b = r.bilan;
      s.append(el('p', { class: 'gains' }, total + ' points'),
        el('p', {}, el('strong', {}, b.justes + ' sur ' + cours.questions.length), ' bonnes réponses · meilleure série : ' + b.meilleure + ' · rebonds : ' + b.rebonds));
      const sv = suite(b.suite); if (sv) s.appendChild(sv);
      if (r.place <= 3 && m.podium) s.appendChild(el('p', { class: 'rebonds' }, 'Bravo, tu es sur le podium : ' + r.place + (r.place === 1 ? 're' : 'e') + ' place.'));
      s.appendChild(r.arevoir.length ? el('p', {}, 'À revoir : question' + (r.arevoir.length > 1 ? 's' : '') + ' ' + r.arevoir.join(', ') + '.') : el('p', {}, 'Tout juste : tu peux aider un·e camarade.'));
    } else s.appendChild(el('p', {}, 'Merci d\'avoir suivi le cours.'));
    s.appendChild(el('p', {}, el('a', { class: 'bouton fort', href: 'revision.html?cours=' + encodeURIComponent(cours.id) }, 'Revoir le cours seul·e')));
    ecran(s);
  }

  /* ── Démarrage ──────────────────────────── */
  function demarrer() {
    Q.theme();
    const p = new URLSearchParams(location.search), code = Q.lireCode(p.get('s'));
    const ancien = lireAncien();
    if (code) $('champCode').value = code;
    else if (ancien) $('champCode').value = ancien.code;
    if (ancien) $('champPseudo').value = ancien.pseudo;
    $('entree').addEventListener('submit', rejoindre);
    $('quitter').addEventListener('click', () => { Q.stock.oublier('eleve'); Q.session.oublier('eleve'); afficherEntree(''); $('champPseudo').value = ''; });
    // la page rechargée dans le même onglet revient directement dans la séance
    const onglet = lireOnglet();
    if (onglet && (!code || code === onglet.code)) { moi = onglet; entrer(); }
  }
  demarrer();
})();
