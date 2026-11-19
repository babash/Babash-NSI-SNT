/* QuizzNSI : la page élève, pensée pour un téléphone (MIT, Babash - NSI Tani Malandi).
   L'élève entre le code de la séance et un prénom ou un pseudo, puis répond aux questions.
   Points : le téléphone calcule lui-même ses points (js/bareme.js) à partir de sa réponse, de son temps,
   de la bonne réponse et du barème reçus à la correction ; personne d'autre ne les reçoit. Sa réponse
   part chiffrée pour la seule page projetée (js/chiffre.js).
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
  let clesHote = [], chiffreur = null, essais = 0;
  const ESSAIS_AVANT_ALERTE = 4; // 4 envois, toutes les 2 s, sans accusé de réception : on prévient
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

  // Sans chiffrement, le téléphone ne peut pas envoyer de réponse : on le dit dès l'entrée.
  function sansChiffrement() {
    if (seance) { seance.fermer(); seance = null; }
    $('connexion').className = 'etat ko'; $('connexion').textContent = '';
    ecran(el('div', { class: 'alerte', role: 'alert' },
      el('p', {}, el('strong', {}, 'Ce navigateur ne peut pas participer à la séance en direct'), ' : il ne sait pas chiffrer les réponses (il faut une page en https et un navigateur à jour).'),
      el('p', {}, 'Tu peux suivre le même cours seul·e, avec les mêmes questions corrigées : ', el('a', { href: 'revision.html' }, 'réviser seul·e'), '.')));
  }

  async function entrer() {
    $('entree').hidden = true; $('jeu').hidden = false; $('quitter').hidden = false;
    $('moi').textContent = moi.pseudo;
    majPoints();
    ecran(el('div', { class: 'attente' }, el('p', { class: 'grand' }, 'Connexion…'), el('p', {}, 'Séance ' + moi.code)));
    hoteVu = false; clesHote = [];
    total = historique().total; majPoints();
    if (!chiffreur) {
      try { if (!Q.chiffre.disponible()) throw new Error('crypto.subtle absent'); chiffreur = await Q.chiffre.eleve(); }
      catch (e) { chiffreur = null; sansChiffrement(); return; }
    }
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
    const hotes = (Array.isArray(liste) ? liste : []).map(Q.messages.presence).filter(v => v && v.role === 'hote');
    // la réponse est chiffrée pour chaque page projetée présente (en pratique, une seule)
    clesHote = hotes.filter(h => h.cle).slice(0, 50).map(h => h.cle);
    const vu = hotes.length > 0;
    if (vu && !hoteVu) { hoteVu = true; if (!phase) ecran(attente('L\'enseignant·e est là. Regarde l\'écran : le cours va commencer.')); seance.envoyer({ t: 'bonjour', id: moi.id }); }
  }

  /* ── Les messages de la séance ──────────── */
  function onMessage(brut) {
    if (!moi) return;
    const m = Q.messages.versEleve(brut, moi.id);
    if (!m) return; // message non conforme : ignoré
    hoteVu = true; clearTimeout(attenteHote);
    if (m.t === 'retire') { if (m.pourMoi) { Q.stock.oublier('eleve'); Q.session.oublier('eleve'); Q.stock.oublier('hist:' + moi.id); afficherEntree('L\'enseignant·e a retiré ce pseudo. Choisis-en un autre : ton prénom ou un pseudo, jamais ton nom de famille.'); } return; }
    if (m.t === 'refus') { if (m.pourMoi) { Q.session.oublier('eleve'); afficherEntree(m.raison === 'pris' ? 'Ce pseudo est déjà pris dans la séance : choisis-en un autre.' : 'Ce pseudo n\'est pas accepté : choisis-en un autre.'); } return; }
    if (m.t === 'recus') { if (question && m.qid === question.qid && question.n && m.n.includes(question.n)) { question.recu = true; clearInterval(renvoi); majEnvoyee(); } return; }
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

  function ecran(noeud) { const z = $('ecran'); z.textContent = ''; delete z.dataset.n; z.appendChild(noeud); }
  const attente = texte => el('div', { class: 'attente' }, el('p', { class: 'grand' }, moi.pseudo + ', tu es dans la séance.'), el('p', {}, texte));
  function majPoints() { $('points').textContent = total + ' pts'; }
  const trouverQuestion = (cours, qid) => cours.questions.find(q => q.id === qid) || null;

  function afficherNotion(cours, m) {
    const d = cours.diapositives[m.n];
    if (!d || d.type === 'question') return;
    // même diapositive : on ne montre que les éléments apparus en plus (pas de clignotement)
    if (phase === 'notion' && question === null && $('ecran').dataset.n === String(m.n)) { Q.montrerFragments($('ecran'), m.f); return; }
    phase = 'notion'; question = null;
    const z = el('div', {}, el('p', { class: 'aide' }, 'Le cours, en même temps que l\'écran :'));
    z.appendChild(Q.fragmentCours(Q.rendreDiapo(cours, d, { fin: '' })));
    ecran(z);
    $('ecran').dataset.n = String(m.n);
    Q.montrerFragments($('ecran'), m.f);
  }

  function afficherQuestion(cours, m) {
    const q = trouverQuestion(cours, m.qid);
    if (!q) return;
    if (question && question.qid === q.id && phase === 'question') { if (m.ferme) question.ferme = true; return; } // déjà affichée
    phase = 'question';
    const ancienne = historique().reps[q.id] || null; // la page rouverte retrouve la réponse déjà donnée
    // le temps déjà écoulé depuis l'ouverture de la question (pour le bonus de rapidité, calculé ici)
    const ecoule = m.duree > 0 && m.reste != null ? Math.max(0, m.duree * 1000 - m.reste) : 0;
    question = { qid: q.id, q, choix: ancienne ? ancienne.c : null, ms: ancienne ? ancienne.ms : null, n: ancienne ? ancienne.n : null,
      depart: Date.now() - ecoule, recu: false, ferme: m.ferme, fin: m.reste != null ? Date.now() + m.reste : null };
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
    question.choix = c; question.ms = Date.now() - question.depart; question.n = Q.nouvelId();
    const h = historique(); h.reps[question.qid] = { c, ms: question.ms, n: question.n }; ecrireHistorique(h);
    bloquer(); majEnvoyee(); envoyerReponse();
    Q.annoncer('Réponse ' + Q.LETTRES[c] + ' choisie.');
  }
  function envoyerReponse() {
    const envoi = async () => {
      if (!(question && question.choix != null && !question.recu && !question.ferme)) { clearInterval(renvoi); return; }
      if (!chiffreur || !clesHote.length) { majEnvoyee(); return; } // pas encore de page projetée : on réessaie dans 2 s
      const clair = { id: moi.id, qid: question.qid, c: question.choix, n: question.n };
      let parti = false;
      // chiffrée pour chaque page projetée présente (en principe, une seule)
      for (const k of clesHote) { try { const env = await chiffreur.chiffrer(clair, k); if (seance) { seance.envoyer(Object.assign({ t: 'rep' }, env)); parti = true; } } catch (e) { /* clé illisible : ignorée */ } }
      if (parti) essais++;
      majEnvoyee();
    };
    essais = 0;
    clearInterval(renvoi); envoi(); renvoi = setInterval(envoi, 2000);
  }
  // « reçue » seulement après l'accusé de réception de la page projetée.
  function majEnvoyee() {
    const z = $('envoyee'); if (!z || !question || question.choix == null) return;
    const l = Q.LETTRES[question.choix];
    if (question.recu) { z.className = 'envoyee'; z.textContent = 'Réponse ' + l + ' reçue par la page projetée. Attends la correction à l\'écran.'; }
    else if (!clesHote.length) { z.className = 'envoyee'; z.textContent = 'Réponse ' + l + ' choisie : en attente de la page projetée…'; }
    else if (essais >= ESSAIS_AVANT_ALERTE) { z.className = 'envoyee alerte'; z.textContent = 'La page projetée n\'a pas encore reçu ta réponse ' + l + ' : vérifie le réseau (wifi ou données). Le téléphone continue d\'essayer.'; }
    else { z.className = 'envoyee'; z.textContent = 'Réponse ' + l + ' choisie : envoi à la page projetée…'; }
  }

  /* ── Mes points, calculés ici ───────────── */
  // L'historique de la séance, sur l'appareil (comme l'entrée « eleve » : 12 heures au plus, effacé à la
  // fin de la séance) : les questions corrigées dans l'ordre, mes résultats, mes réponses données.
  // Il permet de rouvrir la page (onglet fermé, QR code scanné de nouveau) sans perdre ses points.
  function historique() {
    const v = moi ? Q.stock.lire('hist:' + moi.id, null) : null, h = { ordre: [], res: {}, reps: {}, total: 0 };
    if (!v || typeof v !== 'object' || v.code !== moi.code || v.id !== moi.id || !Number.isFinite(v.jusqua) || v.jusqua < Date.now()
      || !Array.isArray(v.ordre) || !v.res || typeof v.res !== 'object') return h;
    if (v.reps && typeof v.reps === 'object') for (const [qid, a] of Object.entries(v.reps)) {
      if (Q.messages.estQid(qid) && a && typeof a === 'object' && Number.isInteger(a.c) && a.c >= 0 && a.c <= 3 && Number.isFinite(a.ms) && a.ms >= 0 && a.ms < 1e8
        && typeof a.n === 'string' && /^[0-9a-f]{16}$/.test(a.n)) h.reps[qid] = { c: a.c, ms: a.ms, n: a.n };
    }
    for (const qid of v.ordre.slice(0, 1000)) {
      const r = v.res[qid];
      if (!Q.messages.estQid(qid) || !r || typeof r !== 'object' || h.res[qid]) continue;
      const ok = (r.c === null || (Number.isInteger(r.c) && r.c >= 0 && r.c <= 3)) && Number.isInteger(r.gain) && r.gain >= 0 && r.gain <= 1000;
      if (!ok) continue;
      h.ordre.push(qid); h.res[qid] = { c: r.c, juste: r.juste === true, gain: r.gain, rebond: r.rebond === true }; h.total += r.gain;
    }
    return h;
  }
  function ecrireHistorique(h) {
    Q.stock.ecrire('hist:' + moi.id, { code: moi.code, id: moi.id, jusqua: Date.now() + DOUZE_HEURES, ordre: h.ordre, res: h.res, reps: h.reps });
  }
  function noter(m) {
    const h = historique();
    if (h.res[m.qid]) return { h, r: h.res[m.qid], detail: null };
    const rep = question && question.qid === m.qid && question.choix != null ? { c: question.choix, ms: question.ms } : (h.reps[m.qid] || null);
    const pr = m.precedente && h.res[m.precedente] && h.res[m.precedente].c !== null ? (h.res[m.precedente].juste ? 'juste' : 'faux') : null;
    const juste = rep ? rep.c === m.bonne : false;
    // le barème est celui du moteur (js/bareme.js), jamais celui reçu : une correction forgée ne gonfle pas les points
    const p = Q.bareme.points(rep ? { juste, ms: rep.ms } : null, { duree: m.duree, precedente: pr }, Q.bareme.BAREME);
    const r = { c: rep ? rep.c : null, juste, gain: p.total, rebond: p.detail.rebond > 0 };
    h.ordre.push(m.qid); h.res[m.qid] = r; h.total += p.total;
    ecrireHistorique(h);
    return { h, r, detail: rep ? p.detail : null };
  }
  const bilanDe = h => {
    const suite = h.ordre.map(q => h.res[q].c === null ? null : h.res[q].juste ? 'juste' : 'faux');
    return Object.assign(Q.bareme.progression(suite), { suite });
  };

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
    if (q.bonne !== m.bonne) return; // la bonne réponse annoncée doit être celle du fichier du cours
    clearInterval(renvoi); clearInterval(chrono);
    phase = 'correction';
    const note = noter(m), r = note.r;
    const choix = r.c;
    question = { qid: q.id, q, choix, recu: true, ferme: true };
    total = note.h.total; majPoints();
    const s = el('section', { class: 'd-question' },
      el('header', { class: 'q-tete' }, el('p', { class: 'q-num' }, 'Question ' + q.numero + ' sur ' + cours.questions.length + ' · correction'),
        (() => { const h = el('h2', { class: 'q-nom' }); h.appendChild(Q.fragmentCours(Q.texte(q.nom))); return h; })()));
    if (choix == null) s.appendChild(el('div', { class: 'verdict neutre', role: 'status' }, el('span', { class: 'symbole', 'aria-hidden': 'true' }, '•'),
      el('div', {}, el('p', { class: 'v-titre' }, 'Pas de réponse cette fois. La bonne réponse est ' + Q.LETTRES[q.bonne] + '.'))));
    s.appendChild(Q.fragmentCours(Q.rendreCorrection(q, choix)));
    if (note.detail && r.gain > 0) {
      const d = note.detail, parts = [];
      if (d.juste) parts.push(d.juste + ' bonne réponse'); if (d.participation) parts.push(d.participation + ' participation');
      if (d.rapidite) parts.push(d.rapidite + ' rapidité'); if (d.rebond) parts.push(d.rebond + ' rebond');
      s.appendChild(el('p', { class: 'gains' }, '+' + r.gain + ' points ', el('small', {}, '(' + parts.join(', ') + ')')));
      if (d.rebond) s.appendChild(el('p', { class: 'rebonds' }, 'Beau rebond : tu t\'es repris·e juste après une erreur.'));
    }
    {
      const b = bilanDe(note.h);
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
    const h = historique(), s = el('section', { class: 'attente' }, el('p', { class: 'grand' }, 'Fin de la séance'));
    if (h.ordre.length) {
      total = h.total; majPoints();
      const b = bilanDe(h);
      s.append(el('p', { class: 'gains' }, total + ' points'),
        el('p', {}, el('strong', {}, b.justes + ' sur ' + cours.questions.length), ' bonnes réponses · meilleure série : ' + b.meilleure + ' · rebonds : ' + b.rebonds));
      const sv = suite(b.suite); if (sv) s.appendChild(sv);
      // la place n'est connue que sur le podium affiché à toute la classe ; aucune autre place n'est envoyée
      const pl = m.podium ? m.podium.find(p => p.pseudo === moi.pseudo) : null;
      if (pl) s.appendChild(el('p', { class: 'rebonds' }, 'Bravo, tu es sur le podium : ' + pl.place + (pl.place === 1 ? 're' : 'e') + ' place.'));
      const arevoir = h.ordre.filter(q => !h.res[q].juste).map(q => (cours.questions.find(x => x.id === q) || {}).numero).filter(Number.isInteger);
      s.appendChild(arevoir.length ? el('p', {}, 'À revoir : question' + (arevoir.length > 1 ? 's' : '') + ' ' + arevoir.join(', ') + '.') : el('p', {}, 'Tout juste : tu peux aider un·e camarade.'));
    } else s.appendChild(el('p', {}, 'Merci d\'avoir suivi le cours.'));
    s.appendChild(el('p', {}, el('a', { class: 'bouton fort', href: 'revision.html?cours=' + encodeURIComponent(cours.id) }, 'Revoir le cours seul·e')));
    ecran(s);
    // la séance est finie : le code, le pseudo, l'identifiant et l'historique gardés sur l'appareil sont effacés
    Q.stock.oublier('eleve'); Q.stock.oublier('hist:' + moi.id);
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
    $('quitter').addEventListener('click', () => { Q.stock.oublier('eleve'); Q.session.oublier('eleve'); if (moi) Q.stock.oublier('hist:' + moi.id); afficherEntree(''); $('champPseudo').value = ''; });
    // la page rechargée dans le même onglet revient directement dans la séance
    const onglet = lireOnglet();
    if (onglet && (!code || code === onglet.code)) { moi = onglet; entrer(); }
  }
  demarrer();
})();
