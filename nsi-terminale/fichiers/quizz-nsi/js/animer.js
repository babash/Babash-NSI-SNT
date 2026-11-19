/* QuizzNSI : la page projetée par l'enseignant·e (MIT, Babash - NSI Tani Malandi).
   Elle tient la séance : elle diffuse les diapositives et les questions, reçoit les réponses,
   calcule les points (js/bareme.js) et renvoie la correction. Rien n'est enregistré en ligne ;
   l'état de la séance reste dans cet onglet (sessionStorage), pour survivre à un rechargement.
   Sécurité : tout ce qui vient du canal (présence, réponses) est validé par js/messages.js ; les
   pseudos ne s'affichent que par textContent ; l'état relu dans le stockage est contrôlé. */
(function () {
  'use strict';
  const Q = window.QuizzNSI, $ = Q.$, B = Q.bareme, el = Q.el;
  let cours, seance = null, st, presents = new Map(), renvoi = null;
  const cle = () => 'animer:' + cours.id;
  const sauver = () => Q.session.ecrire(cle(), st);
  const diapo = () => cours.diapositives[st.index];
  const pluriel = (n, mot) => n + ' ' + mot + (n > 1 ? 's' : '');
  const envoyer = m => { if (seance) seance.envoyer(m); };

  function etatNeuf(code) {
    return { code: code || Q.nouveauCode(), id: Q.nouvelId(), commence: false, index: 0, f: 0, duree: 45, podium: 'fin',
      joueurs: {}, bannis: [], q: {}, ordre: [], fini: false };
  }

  // L'état relu dans le stockage de l'onglet a pu être modifié : on ne garde que ce qui est conforme.
  const DUREES = [0, 20, 30, 45, 60, 90], PODIUMS = ['fin', 'chaque', 'jamais'];
  function etatRelu(v) {
    const ent = (x, a, b) => Number.isSafeInteger(x) && x >= a && x <= b;
    if (!v || typeof v !== 'object' || Q.lireCode(v.code) !== v.code || !Q.messages.estId(v.id)) return null;
    if (!ent(v.index, 0, cours.diapositives.length - 1) || !DUREES.includes(v.duree) || !PODIUMS.includes(v.podium)) return null;
    const qids = new Set(cours.questions.map(q => q.id));
    const st = etatNeuf(v.code);
    Object.assign(st, { id: v.id, commence: v.commence === true, fini: v.fini === true, index: v.index, f: ent(v.f, 0, 100) ? v.f : 0, duree: v.duree, podium: v.podium });
    st.bannis = Array.isArray(v.bannis) ? v.bannis.filter(c => typeof c === 'string' && /^[a-z0-9]{0,64}$/.test(c)) : [];
    st.ordre = Array.isArray(v.ordre) ? v.ordre.filter(q => qids.has(q)) : [];
    if (v.q && typeof v.q === 'object') for (const [qid, e] of Object.entries(v.q)) {
      if (!qids.has(qid) || !e || typeof e !== 'object' || !ent(e.ouverte, 0, 1e14) || !(e.fin === null || ent(e.fin, 0, 1e14))) continue;
      st.q[qid] = { ouverte: e.ouverte, fin: e.fin, ferme: e.ferme === true, revelee: e.revelee === true, raison: typeof e.raison === 'string' ? e.raison.slice(0, 40) : '',
        rebonds: Array.isArray(e.rebonds) ? e.rebonds.filter(p => Q.filtrerPseudo(p).ok) : [] };
    }
    if (v.joueurs && typeof v.joueurs === 'object') for (const [id, j] of Object.entries(v.joueurs)) {
      if (!Q.messages.estId(id) || !j || typeof j !== 'object' || !Q.filtrerPseudo(j.pseudo).ok || !ent(j.total, 0, 1e7)) continue;
      const rep = {};
      if (j.rep && typeof j.rep === 'object') for (const [qid, r] of Object.entries(j.rep)) {
        if (!qids.has(qid) || !r || !ent(r.c, 0, 3) || !ent(r.ms, -1e7, 1e9)) continue;
        rep[qid] = { c: r.c, ms: r.ms };
        if (typeof r.juste === 'boolean' && ent(r.gain, 0, 1000) && r.detail && typeof r.detail === 'object') {
          const d = {}; let ok = true;
          for (const k of ['participation', 'juste', 'rapidite', 'rebond']) { if (!ent(r.detail[k], 0, 1000)) ok = false; d[k] = r.detail[k]; }
          if (ok) Object.assign(rep[qid], { juste: r.juste, gain: r.gain, detail: d });
        }
      }
      st.joueurs[id] = { pseudo: j.pseudo, cle: Q.clePseudo(j.pseudo), rep, total: j.total, retire: j.retire === true };
    }
    return st;
  }

  /* ── Les élèves ─────────────────────────── */
  const joueursActifs = () => Object.entries(st.joueurs).filter(([, j]) => !j.retire).map(([id, j]) => Object.assign({ id }, j));
  const presentsActifs = () => [...presents.values()].filter(p => p.role === 'eleve' && st.joueurs[p.id] && !st.joueurs[p.id].retire);

  function onPresence(liste) {
    presents = new Map();
    let neuf = false;
    const toutes = (Array.isArray(liste) ? liste : []).map(Q.messages.presence).filter(Boolean);
    // une seule page projetée par séance : on prévient si une autre est dans la présence
    const autres = toutes.filter(p => p.role === 'hote' && !(p.id === st.id && p.cle && cleHote && p.cle.x === cleHote.publique.x));
    $('autreHote').hidden = !autres.length;
    $('autreHote').textContent = autres.length ? 'Attention : une autre page projetée est ouverte sur cette séance (onglet dupliqué, autre ordinateur ?). Ferme-la : les réponses des élèves risquent de n\'arriver qu\'à l\'une des deux.' : '';
    const valides = toutes.filter(p => p.role === 'eleve');
    for (const p of valides) {
      if (!p.pseudo) { envoyer({ t: 'refus', id: p.id, raison: 'invalide' }); continue; }
      const f = { pseudo: p.pseudo };
      const c = Q.clePseudo(f.pseudo);
      const j = st.joueurs[p.id];
      if (st.bannis.includes(c)) { if (!j || !j.retire || j.cle !== c) envoyer({ t: 'retire', id: p.id }); if (j) j.retire = true; continue; }
      const pris = Object.entries(st.joueurs).some(([id, k]) => id !== p.id && !k.retire && k.cle === c && (presents.has(id) || valides.some(x => x.id === id)));
      if (pris && (!j || j.cle !== c)) { envoyer({ t: 'refus', id: p.id, raison: 'pris' }); continue; }
      if (!j) { st.joueurs[p.id] = { pseudo: f.pseudo, cle: c, rep: {}, total: 0 }; neuf = true; }
      else { if (j.retire && j.cle !== c) { j.retire = false; neuf = true; } j.pseudo = f.pseudo; j.cle = c; }
      presents.set(p.id, p);
    }
    sauver();
    majEleves();
    if (neuf) planifierRenvoi();
  }

  function majEleves() {
    const l = joueursActifs().sort((a, b) => a.pseudo.localeCompare(b.pseudo, 'fr'));
    const enLigne = l.filter(j => presents.has(j.id));
    const txt = pluriel(enLigne.length, 'élève');
    $('nbEleves').textContent = enLigne.length; $('nbEleves2').textContent = enLigne.length; $('nbBarre').textContent = txt;
    const items = () => l.map(j => el('li', { class: presents.has(j.id) ? '' : 'absent' },
      el('span', {}, j.pseudo, presents.has(j.id) ? null : el('small', {}, ' (déconnecté·e)')),
      el('button', { type: 'button', class: 'retirer', 'data-retirer': j.id, 'aria-label': 'Retirer le pseudo ' + j.pseudo }, 'Retirer')));
    $('eleves').replaceChildren(...(l.length ? items() : [el('li', { class: 'vide' }, 'Personne pour l\'instant.')]));
    $('eleves2').replaceChildren(...items());
    majStatut();
  }

  function retirer(id) {
    const j = st.joueurs[id];
    if (!j) return;
    j.retire = true;
    if (!st.bannis.includes(j.cle)) st.bannis.push(j.cle);
    envoyer({ t: 'retire', id });
    sauver(); majEleves();
    Q.annoncer('Pseudo ' + j.pseudo + ' retiré.');
  }

  /* ── Les messages des élèves ─────────────── */
  let accuses = new Set(), accuseMinuterie = null;
  let cleHote = null; // la paire de clés de la page projetée (js/chiffre.js)
  async function onMessage(brut) {
    const env = Q.messages.versHote(brut);
    if (!env) return; // message non conforme : ignoré
    if (env.t === 'bonjour') { planifierRenvoi(); return; }
    if (env.t === 'rep') {
      if (!st.commence || !cleHote) return;
      const recu = Date.now();
      const m = Q.messages.reponse(await cleHote.dechiffrer(env)); // illisible ou forgée : ignorée
      if (!m) return;
      const d = diapo(), etat = d && d.type === 'question' ? st.q[d.id] : null;
      if (!etat || etat.ferme || m.qid !== d.id) return;
      const j = st.joueurs[m.id];
      if (!j || j.retire) return;
      if (!j.rep[d.id]) { j.rep[d.id] = { c: m.c, ms: recu - etat.ouverte }; sauver(); majStatut(); }
      // l'accusé de réception ne porte qu'un nombre tiré au hasard par le téléphone, pas son identifiant
      accuses.add(m.n);
      if (!accuseMinuterie) accuseMinuterie = setTimeout(() => { envoyer({ t: 'recus', qid: d.id, n: [...accuses] }); accuses = new Set(); accuseMinuterie = null; }, 400);
      const repondu = presentsActifs().filter(p => st.joueurs[p.id].rep[d.id]).length;
      if (repondu > 0 && repondu === presentsActifs().length && !etat.ferme) fermer(d, 'Tout le monde a répondu.');
    }
  }

  // Un message renvoyé quand un·e élève arrive ou revient : il lui donne la phase en cours.
  function planifierRenvoi() {
    clearTimeout(renvoi);
    renvoi = setTimeout(() => { const m = messagePhase(); if (m) envoyer(m); }, 300);
  }

  // Les messages ne portent que des identifiants et des nombres : le texte est dans le fichier du cours.
  function messageQuestion(d) {
    const e = st.q[d.id];
    return { t: 'question', cours: cours.id, qid: d.id, reste: e && e.fin ? Math.max(0, Math.round(e.fin - Date.now())) : null, duree: st.duree, ferme: !!(e && e.ferme) };
  }
  // La correction ne diffuse que ce que l'écran projeté montre à toute la classe : la bonne réponse,
  // la répartition en nombres, le podium s'il est affiché. Chaque téléphone calcule ses points avec le
  // barème et la question corrigée juste avant (pour le rebond).
  const podiumPublic = () => podium().filter(j => j.place <= 3).slice(0, 20).map(j => ({ pseudo: j.pseudo, total: j.total, place: j.place }));
  function messageCorrection(d) {
    const k = st.ordre.indexOf(d.id);
    return { t: 'correction', cours: cours.id, qid: d.id, precedente: k > 0 ? st.ordre[k - 1] : null, bonne: d.bonne, rep: repartition(d),
      bareme: Object.assign({}, B.BAREME), duree: st.duree, podium: st.podium === 'chaque' ? podiumPublic() : null };
  }
  function messagePhase() {
    const d = diapo();
    if (st.fini) return messageFin();
    if (!st.commence) return { t: 'attente' };
    if (d.type === 'question') { const e = st.q[d.id]; return e && e.revelee ? messageCorrection(d) : messageQuestion(d); }
    // toute autre diapositive (titre, partie, question à la classe, humour, notion, bilan) : le téléphone
    // l'affiche à partir du fichier du cours, avec le même nombre d'éléments déjà apparus
    return { t: 'notion', cours: cours.id, n: st.index, f: st.f };
  }

  /* ── Le score ───────────────────────────── */
  function bilanJoueur(j) {
    const resultats = st.ordre.map(qid => { const r = j.rep[qid]; return r ? (r.juste ? 'juste' : 'faux') : null; });
    const p = B.progression(resultats);
    return { justes: p.justes, repondues: p.repondues, serie: p.serie, meilleure: p.meilleure, rebonds: p.rebonds, suite: resultats };
  }
  const repartition = d => B.repartition(joueursActifs().map(j => j.rep[d.id] ? j.rep[d.id].c : null));
  const podium = () => B.classer(joueursActifs().map(j => ({ id: j.id, pseudo: j.pseudo, total: j.total, justes: bilanJoueur(j).justes })));

  function corriger(d) {
    const e = st.q[d.id];
    if (!e.ferme) fermer(d, '');
    if (e.revelee) return;
    const precedente = st.ordre.length ? st.ordre[st.ordre.length - 1] : null;
    e.rebonds = [];
    for (const [, j] of Object.entries(st.joueurs)) {
      const r = j.rep[d.id];
      if (!r) continue;
      const pr = precedente && j.rep[precedente] ? (j.rep[precedente].juste ? 'juste' : 'faux') : null;
      r.juste = r.c === d.bonne;
      const p = B.points({ juste: r.juste, ms: r.ms }, { duree: st.duree, precedente: pr });
      r.gain = p.total; r.detail = p.detail; j.total += p.total;
      if (p.detail.rebond && !j.retire) e.rebonds.push(j.pseudo);
    }
    e.revelee = true;
    st.ordre.push(d.id);
    sauver();
    envoyer(messageCorrection(d));
  }

  /* ── Ouvrir, fermer, corriger une question ── */
  function ouvrir(d) {
    if (st.q[d.id]) return;
    st.q[d.id] = { ouverte: Date.now(), fin: st.duree > 0 ? Date.now() + st.duree * 1000 : null, ferme: false, revelee: false };
    sauver();
  }
  function fermer(d, raison) {
    const e = st.q[d.id];
    if (!e || e.ferme) return;
    e.ferme = true; e.raison = raison || 'Réponses fermées.'; sauver();
    envoyer({ t: 'fermee', qid: d.id });
    majStatut(); majAction();
  }

  /* ── L'affichage ────────────────────────── */
  function afficher() {
    const d = diapo();
    $('scene').innerHTML = Q.rendreDiapo(cours, d, { boutons: false });
    st.f = Math.min(st.f, Q.nbFragments($('scene'))); Q.montrerFragments($('scene'), st.f);
    $('compteur').textContent = (st.index + 1) + ' / ' + cours.diapositives.length + (d.type === 'question' ? ' · question ' + d.numero + ' sur ' + cours.questions.length : '');
    $('barre').style.width = ((st.index + 1) / cours.diapositives.length * 100) + '%';
    $('prec').disabled = st.index === 0;
    if (d.type === 'question') { ouvrir(d); if (st.q[d.id].revelee) montrerCorrection(d); }
    envoyer(messagePhase());
    majStatut(); majAction();
    $('scene').focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }

  function majStatut() {
    const d = cours && st && st.commence ? diapo() : null, z = $('statutQ');
    if (!d || d.type !== 'question' || !st.q[d.id]) { z.textContent = ''; return; }
    const e = st.q[d.id], n = joueursActifs().filter(j => j.rep[d.id]).length, total = presentsActifs().length;
    let t = 'Réponses : ' + n + ' / ' + total;
    if (e.revelee) t = n + ' réponse' + (n > 1 ? 's' : '') + ' · correction affichée';
    else if (e.ferme) t += ' · ' + (e.raison || 'réponses fermées');
    else if (e.fin) t = '⏱ ' + Math.max(0, Math.ceil((e.fin - Date.now()) / 1000)) + ' s · ' + t;
    z.textContent = t;
  }

  const fragmentsRestants = () => Q.nbFragments($('scene')) - st.f;
  function majAction() {
    const a = $('action'), d = diapo();
    if (d.type !== 'question' && fragmentsRestants() > 0) { a.textContent = 'Suite (' + fragmentsRestants() + ') →'; return; }
    if (st.index === cours.diapositives.length - 1) { a.textContent = st.fini ? 'Revoir le podium' : 'Terminer la séance'; return; }
    if (d.type === 'question' && st.q[d.id] && !st.q[d.id].revelee) { a.textContent = 'Montrer la réponse'; return; }
    a.textContent = 'Suivante →';
  }

  function montrerCorrection(d) {
    const e = st.q[d.id], rep = repartition(d), total = rep.reduce((a, b) => a + b, 0);
    const sc = $('scene');
    sc.querySelectorAll('.option').forEach(o => {
      const i = +o.dataset.choix, pc = total ? Math.round(rep[i] / total * 100) : 0;
      if (i === d.bonne) { o.classList.add('bonne-rep'); o.appendChild(el('span', { class: 'etiquette' }, '✓ Bonne réponse')); }
      const barre = el('span', {}); barre.style.width = pc + '%';
      o.append(el('span', { class: 'rep-nb' }, rep[i] + ' réponse' + (rep[i] > 1 ? 's' : '') + ' ', el('small', {}, '(' + pc + ' %)')), el('span', { class: 'rep-barre', 'aria-hidden': 'true' }, barre));
    });
    sc.querySelector('.options').classList.add('corrigees', 'avec-barres');
    const justes = rep[d.bonne];
    let pire = -1;
    rep.forEach((n, i) => { if (i !== d.bonne && n > 0 && (pire < 0 || n > rep[pire])) pire = i; });
    const zone = sc.querySelector('.zone-correction');
    zone.replaceChildren(el('p', { class: 'bilan-q' }, el('strong', {}, justes + ' sur ' + total), ' ' + (justes > 1 ? 'ont' : 'a') + ' trouvé la bonne réponse, ' + Q.LETTRES[d.bonne] + '.',
      e.rebonds && e.rebonds.length ? el('span', { class: 'rebonds' }, ' Beaux rebonds : ' + e.rebonds.join(', ') + '.') : null));
    // le reste vient du fichier du cours (contenu local)
    if (pire >= 0) zone.appendChild(Q.fragmentCours('<div class="erreur-frequente">' + Q.pastille(pire) + '<div><p class="fb-titre">Erreur la plus fréquente</p><p>' + Q.texte(d.options[pire].feedback) + '</p></div></div>'));
    zone.appendChild(Q.fragmentCours(Q.rendreCorrection(d, null, { projection: true })));
    majStatut(); majAction();
    if (st.podium === 'chaque' && joueursActifs().length) setTimeout(montrerPodium, 50);
  }

  function action() {
    const d = diapo();
    // d'abord les apparitions progressives de la diapositive, une à une
    if (d.type !== 'question' && fragmentsRestants() > 0) { st.f++; sauver(); Q.montrerFragments($('scene'), st.f); envoyer(messagePhase()); majAction(); return; }
    if (st.index === cours.diapositives.length - 1) { terminer(); return; }
    if (d.type === 'question' && st.q[d.id] && !st.q[d.id].revelee) { corriger(d); montrerCorrection(d); Q.annoncer('Correction affichée.'); return; }
    aller(st.index + 1);
  }
  function aller(i) {
    const avant = st.index;
    st.index = Math.max(0, Math.min(cours.diapositives.length - 1, i));
    st.f = st.index < avant ? 100 : 0; // en revenant en arrière, tout est montré
    sauver(); afficher();
  }

  /* ── Podium et fin ──────────────────────── */
  function noeudsPodium(final) {
    const l = podium(), justes = cours.questions.filter(q => st.q[q.id] && st.q[q.id].revelee);
    if (!l.length) return [el('p', {}, 'Aucun·e élève connecté·e : pas de classement.')];
    const n = [];
    if (st.podium !== 'jamais' || final === 'force') {
      n.push(el('ol', { class: 'podium' }, l.filter(j => j.place <= 3).slice(0, 6).map(j => el('li', { class: 'place' + j.place },
        el('span', { class: 'rang' }, j.place + (j.place === 1 ? 're' : 'e')), el('span', { class: 'qui' }, j.pseudo), el('span', { class: 'pts' }, j.total + ' points')))));
    }
    // la progression de la classe : la réussite question par question
    if (justes.length) {
      n.push(el('h3', {}, 'La classe, question par question'), el('ol', { class: 'reussite' }, justes.map(q => {
        const rep = repartition(q), t = rep.reduce((a, b) => a + b, 0), pc = t ? Math.round(rep[q.bonne] / t * 100) : 0;
        const b = el('span', {}); b.style.width = pc + '%';
        return el('li', {}, el('span', { class: 'q' }, 'Q' + q.numero), el('span', { class: 'rep-barre' }, b), el('span', {}, pc + ' %'));
      })));
      const rebonds = l.map(j => ({ pseudo: j.pseudo, n: bilanJoueur(st.joueurs[j.id]).rebonds })).filter(x => x.n > 0).sort((a, b) => b.n - a.n).slice(0, 5);
      if (rebonds.length) n.push(el('p', { class: 'rebonds' }, el('strong', {}, 'Les rebonds'), ' (une bonne réponse juste après une erreur) : ' + rebonds.map(x => x.pseudo + ' (' + x.n + ')').join(', ') + '.'));
    }
    return n;
  }
  function montrerPodium(final) {
    $('podiumTitre').textContent = st.podium === 'jamais' && final !== 'force' ? 'Bilan de la classe' : 'Podium';
    $('podiumCorps').replaceChildren(...noeudsPodium(final));
    const b = $('podiumBoite');
    if (!b.open) { try { b.showModal(); } catch (e) { b.setAttribute('open', ''); } }
  }
  function messageFin() {
    return { t: 'fin', cours: cours.id, podium: st.podium === 'jamais' ? null : podiumPublic() };
  }
  function terminer() {
    st.fini = true; sauver();
    envoyer(messageFin());
    majAction();
    montrerPodium();
  }

  /* ── La connexion ───────────────────────── */
  async function connecter() {
    if (seance) seance.fermer();
    seance = null;
    presents = new Map();
    const lien = Q.lienEleve(st.code);
    $('code').textContent = st.code; $('codePetit').textContent = st.code; $('codeBarre').textContent = st.code;
    $('lien').textContent = lien.replace(/^https?:\/\//, ''); $('lienPetit').textContent = lien.replace(/^https?:\/\//, '');
    try {
      const q = qrcode(0, 'M'); q.addData(lien); q.make();
      const svgQr = q.createSvgTag({ scalable: true, margin: 0 });
      $('qr').innerHTML = svgQr; $('qrPetit').innerHTML = svgQr;
    } catch (e) { $('qr').textContent = ''; }
    const z = $('etatConnexion');
    if (!Q.chiffre.disponible()) { z.className = 'etat ko'; z.textContent = 'Ce navigateur ne peut pas chiffrer les réponses (page à ouvrir en https). Le cours marche sans les téléphones.'; return; }
    try { cleHote = await Q.chiffre.hote(); } catch (e) { z.className = 'etat ko'; z.textContent = 'Le chiffrement des réponses est impossible dans ce navigateur.'; return; }
    seance = Q.ouvrirSeance(st.code, { id: st.id, role: 'hote', cle: cleHote.publique }, {
      onMessage, onPresence,
      onEtat(e) {
        if (e === 'connexion') { z.className = 'etat'; z.textContent = 'Connexion à la séance en direct…'; }
        else if (e === 'connecte') { z.className = 'etat ok'; z.textContent = seance && seance.demo ? 'Mode démo : la séance passe entre les onglets de ce navigateur.' : 'Séance ouverte : les élèves peuvent rejoindre.'; planifierRenvoi(); }
        else if (e === 'erreur' || e === 'ferme') { z.className = 'etat ko'; z.replaceChildren('Pas de connexion à la séance en direct : vérifie le réseau, puis recharge la page. Tu peux projeter le cours sans les téléphones, et proposer aux élèves de ', el('a', { href: 'revision.html?cours=' + encodeURIComponent(cours.id) }, 'réviser seul·e·s'), ', sans réseau de classe.'); }
      },
    });
  }

  function demarrerCours() {
    const du = +$('duree').value, po = $('podium').value;
    st.duree = DUREES.includes(du) ? du : 45; st.podium = PODIUMS.includes(po) ? po : 'fin';
    st.commence = true; sauver();
    $('accueil').hidden = true; $('scene').hidden = false; $('commandes').hidden = false;
    $('pastilleSeance').hidden = false; $('btnRejoindre').hidden = false; $('btnPodium').hidden = false;
    afficher();
  }

  /* ── Démarrage ──────────────────────────── */
  async function demarrer() {
    Q.theme();
    try { cours = await Q.chargerCours(Q.idCours()); }
    catch (e) { $('scene').hidden = false; Q.erreurPage($('scene'), e.message); return; }
    document.title = 'QuizzNSI · ' + cours.titre + ' · animer la séance';
    $('titreCours').textContent = cours.titre + ' · animer la séance';
    st = etatRelu(Q.session.lire('animer:' + cours.id, null));
    const reprise = st && st.commence;
    if (!st) st = etatNeuf();
    $('duree').value = String(st.duree); $('podium').value = st.podium;
    $('accueil').hidden = false;
    if (reprise) { $('reprendre').hidden = false; $('commencer').textContent = 'Recommencer au début'; }
    connecter();
    majEleves();

    $('commencer').addEventListener('click', () => {
      if (reprise) { const code = st.code, id = st.id; st = etatNeuf(code); st.id = id; }
      demarrerCours();
    });
    $('reprendre').addEventListener('click', demarrerCours);
    $('nouvelle').addEventListener('click', () => { st = etatNeuf(); sauver(); connecter(); majEleves(); $('reprendre').hidden = true; $('commencer').textContent = 'Commencer le cours'; });
    $('copier').addEventListener('click', async () => { try { await navigator.clipboard.writeText(Q.lienEleve(st.code)); $('copier').textContent = 'Lien copié'; } catch (e) { $('copier').textContent = 'Copie impossible'; } setTimeout(() => { $('copier').textContent = 'Copier le lien'; }, 1800); });
    document.addEventListener('click', ev => { const b = ev.target.closest('[data-retirer]'); if (b && Q.messages.estId(b.dataset.retirer)) retirer(b.dataset.retirer); });
    $('prec').addEventListener('click', () => aller(st.index - 1));
    $('action').addEventListener('click', action);
    $('btnPodium').addEventListener('click', () => montrerPodium('force'));
    $('btnRejoindre').addEventListener('click', () => { const c = $('carteRejoindre'); c.hidden = !c.hidden; $('btnRejoindre').setAttribute('aria-expanded', String(!c.hidden)); });
    $('btnPleinEcran').addEventListener('click', () => { if (document.fullscreenElement) document.exitFullscreen(); else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {}); });
    document.addEventListener('keydown', ev => {
      if (!st.commence || $('podiumBoite').open) return;
      if (ev.target.closest && ev.target.closest('input, select, textarea, button, a, summary')) return;
      if (ev.altKey || ev.ctrlKey || ev.metaKey) return;
      if (ev.key === 'ArrowRight' || ev.key === 'Enter' || ev.key === ' ' || ev.key === 'PageDown') { ev.preventDefault(); action(); }
      else if (ev.key === 'ArrowLeft' || ev.key === 'PageUp') { ev.preventDefault(); aller(st.index - 1); }
      else if (ev.key === 'p' || ev.key === 'P') montrerPodium('force');
      else if (ev.key === 'j' || ev.key === 'J') $('btnRejoindre').click();
    });
    setInterval(() => {
      if (!st.commence) return;
      const d = diapo();
      if (d.type === 'question' && st.q[d.id] && !st.q[d.id].ferme && st.q[d.id].fin && Date.now() >= st.q[d.id].fin) fermer(d, 'Temps écoulé.');
      majStatut();
    }, 500);
  }
  demarrer();
})();
