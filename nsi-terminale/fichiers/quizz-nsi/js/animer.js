/* QuizzNSI : la page projetée par l'enseignant·e (MIT, Babash - NSI Tani Malandi).
   Elle tient la séance : elle diffuse les diapositives et les questions, reçoit les réponses,
   calcule les points (js/bareme.js) et renvoie la correction. Rien n'est enregistré en ligne ;
   l'état de la séance reste dans cet onglet (sessionStorage), pour survivre à un rechargement. */
(function () {
  'use strict';
  const Q = window.QuizzNSI, $ = Q.$, B = Q.bareme;
  let cours, seance = null, st, presents = new Map(), renvoi = null;
  const cle = () => 'animer:' + cours.id;
  const sauver = () => Q.session.ecrire(cle(), st);
  const diapo = () => cours.diapositives[st.index];
  const pluriel = (n, mot) => n + ' ' + mot + (n > 1 ? 's' : '');

  function etatNeuf(code) {
    return { code: code || Q.nouveauCode(), id: Q.nouvelId(), commence: false, index: 0, duree: 45, podium: 'fin',
      joueurs: {}, bannis: [], q: {}, ordre: [], fini: false };
  }

  /* ── Les élèves ─────────────────────────── */
  const joueursActifs = () => Object.entries(st.joueurs).filter(([, j]) => !j.retire).map(([id, j]) => Object.assign({ id }, j));
  const presentsActifs = () => [...presents.values()].filter(p => p.role === 'eleve' && st.joueurs[p.id] && !st.joueurs[p.id].retire);

  function onPresence(liste) {
    presents = new Map();
    let neuf = false;
    for (const p of liste) {
      if (!p || typeof p.id !== 'string' || !/^[0-9a-f]{16}$/.test(p.id) || p.role !== 'eleve') continue;
      const f = Q.filtrerPseudo(p.pseudo);
      if (!f.ok) { seance.envoyer({ t: 'refus', id: p.id, raison: 'invalide' }); continue; }
      const c = Q.clePseudo(f.pseudo);
      const j = st.joueurs[p.id];
      if (st.bannis.includes(c)) { if (!j || !j.retire || j.cle !== c) seance.envoyer({ t: 'retire', id: p.id }); if (j) j.retire = true; continue; }
      const pris = Object.entries(st.joueurs).some(([id, k]) => id !== p.id && !k.retire && k.cle === c && (presents.has(id) || liste.some(x => x && x.id === id)));
      if (pris && (!j || j.cle !== c)) { seance.envoyer({ t: 'refus', id: p.id, raison: 'pris' }); continue; }
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
    const html = l.map(j => '<li class="' + (presents.has(j.id) ? '' : 'absent') + '"><span>' + Q.echapper(j.pseudo) + (presents.has(j.id) ? '' : ' <small>(déconnecté·e)</small>') + '</span>'
      + '<button type="button" class="retirer" data-retirer="' + j.id + '" aria-label="Retirer le pseudo ' + Q.echapper(j.pseudo) + '">Retirer</button></li>').join('');
    $('eleves').innerHTML = html || '<li class="vide">Personne pour l\'instant.</li>';
    $('eleves2').innerHTML = html;
    majStatut();
  }

  function retirer(id) {
    const j = st.joueurs[id];
    if (!j) return;
    j.retire = true;
    if (!st.bannis.includes(j.cle)) st.bannis.push(j.cle);
    seance.envoyer({ t: 'retire', id });
    sauver(); majEleves();
    Q.annoncer('Pseudo ' + j.pseudo + ' retiré.');
  }

  /* ── Les messages des élèves ─────────────── */
  let accuses = new Set(), accuseMinuterie = null;
  function onMessage(m) {
    if (!m || typeof m !== 'object') return;
    if (m.t === 'bonjour' && typeof m.id === 'string') { planifierRenvoi(); return; }
    if (m.t === 'rep') {
      const d = diapo(), etat = d && d.type === 'question' ? st.q[d.id] : null;
      if (!etat || etat.ferme || m.qid !== d.id || !Number.isInteger(m.c) || m.c < 0 || m.c > 3) return;
      const j = st.joueurs[m.id];
      if (!j || j.retire) return;
      if (!j.rep[d.id]) { j.rep[d.id] = { c: m.c, ms: Date.now() - etat.ouverte }; sauver(); majStatut(); }
      accuses.add(m.id);
      if (!accuseMinuterie) accuseMinuterie = setTimeout(() => { seance.envoyer({ t: 'recus', qid: d.id, ids: [...accuses] }); accuses = new Set(); accuseMinuterie = null; }, 400);
      const repondu = presentsActifs().filter(p => st.joueurs[p.id].rep[d.id]).length;
      if (repondu > 0 && repondu === presentsActifs().length && !etat.ferme) fermer(d, 'Tout le monde a répondu.');
    }
  }

  // Un message renvoyé quand un·e élève arrive ou revient : il lui donne la phase en cours.
  function planifierRenvoi() {
    clearTimeout(renvoi);
    renvoi = setTimeout(() => { const m = messagePhase(); if (m) seance.envoyer(m); }, 300);
  }

  function messageQuestion(d) {
    const e = st.q[d.id];
    return { t: 'question', qid: d.id, n: d.numero, total: cours.questions.length, nom: d.nom, objectif: d.objectif, enonce: d.enonce,
      code: d.code || null, schema: d.schema || null, options: d.options.map(o => ({ texte: o.texte || null, code: o.code || null })),
      duree: st.duree, reste: e && e.fin ? Math.max(0, e.fin - Date.now()) : null, ferme: !!(e && e.ferme) };
  }
  function messageCorrection(d) {
    const res = {};
    for (const [id, j] of Object.entries(st.joueurs)) {
      if (j.retire) continue;
      const r = j.rep[d.id];
      res[id] = { c: r ? r.c : null, gain: r ? r.gain : 0, detail: r ? r.detail : null, total: j.total, bilan: bilanJoueur(j) };
    }
    return { t: 'correction', qid: d.id, n: d.numero, total: cours.questions.length, nom: d.nom, bonne: d.bonne,
      options: d.options.map(o => ({ texte: o.texte || null, code: o.code || null, feedback: o.feedback })), explication: d.explication,
      rep: repartition(d), res, podium: st.podium === 'chaque' ? podium().slice(0, 3).map(j => ({ pseudo: j.pseudo, total: j.total })) : null };
  }
  function messagePhase() {
    const d = diapo();
    if (st.fini) return messageFin();
    if (!st.commence) return { t: 'attente', titre: cours.titre };
    if (d.type === 'question') { const e = st.q[d.id]; return e && e.revelee ? messageCorrection(d) : messageQuestion(d); }
    if (d.type === 'notion') return { t: 'notion', titre: d.titre, texte: d.texte, schema: d.schema || null, code: d.code || null };
    return { t: 'attente', titre: d.type === 'bilan' ? 'À retenir' : cours.titre };
  }

  /* ── Le score ───────────────────────────── */
  function bilanJoueur(j) {
    const resultats = st.ordre.map(qid => { const r = j.rep[qid]; return r ? (r.juste ? 'juste' : 'faux') : null; });
    return Object.assign(B.progression(resultats), { suite: resultats });
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
    seance.envoyer(messageCorrection(d));
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
    seance.envoyer({ t: 'fermee', qid: d.id });
    majStatut(); majAction();
  }

  /* ── L'affichage ────────────────────────── */
  function afficher() {
    const d = diapo();
    $('scene').innerHTML = Q.rendreDiapo(cours, d, { boutons: false });
    $('compteur').textContent = (st.index + 1) + ' / ' + cours.diapositives.length + (d.type === 'question' ? ' · question ' + d.numero + ' sur ' + cours.questions.length : '');
    $('barre').style.width = ((st.index + 1) / cours.diapositives.length * 100) + '%';
    $('prec').disabled = st.index === 0;
    if (d.type === 'question') { ouvrir(d); if (st.q[d.id].revelee) montrerCorrection(d); }
    if (seance) seance.envoyer(messagePhase());
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

  function majAction() {
    const a = $('action'), d = diapo();
    if (st.index === cours.diapositives.length - 1) { a.textContent = st.fini ? 'Revoir le podium' : 'Terminer la séance'; return; }
    if (d.type === 'question' && st.q[d.id] && !st.q[d.id].revelee) { a.textContent = 'Montrer la réponse'; return; }
    a.textContent = 'Suivante →';
  }

  function montrerCorrection(d) {
    const e = st.q[d.id], rep = repartition(d), total = rep.reduce((a, b) => a + b, 0);
    const sc = $('scene');
    sc.querySelectorAll('.option').forEach(o => {
      const i = +o.dataset.choix, pc = total ? Math.round(rep[i] / total * 100) : 0;
      if (i === d.bonne) { o.classList.add('bonne-rep'); o.insertAdjacentHTML('beforeend', '<span class="etiquette">✓ Bonne réponse</span>'); }
      o.insertAdjacentHTML('beforeend', '<span class="rep-nb">' + rep[i] + ' réponse' + (rep[i] > 1 ? 's' : '') + ' <small>(' + pc + ' %)</small></span><span class="rep-barre" aria-hidden="true"><span style="width:' + pc + '%"></span></span>');
    });
    sc.querySelector('.options').classList.add('corrigees', 'avec-barres');
    const justes = rep[d.bonne];
    let pire = -1;
    rep.forEach((n, i) => { if (i !== d.bonne && n > 0 && (pire < 0 || n > rep[pire])) pire = i; });
    let h = '<p class="bilan-q"><strong>' + justes + ' sur ' + total + '</strong> ' + (justes > 1 ? 'ont' : 'a') + ' trouvé la bonne réponse, ' + Q.LETTRES[d.bonne] + '.'
      + (e.rebonds && e.rebonds.length ? ' <span class="rebonds">Beaux rebonds : ' + e.rebonds.map(Q.echapper).join(', ') + '.</span>' : '') + '</p>';
    if (pire >= 0) h += '<div class="erreur-frequente">' + Q.pastille(pire) + '<div><p class="fb-titre">Erreur la plus fréquente</p><p>' + Q.texte(d.options[pire].feedback) + '</p></div></div>';
    sc.querySelector('.zone-correction').innerHTML = h + Q.rendreCorrection(d, null, { projection: true });
    majStatut(); majAction();
    if (st.podium === 'chaque' && joueursActifs().length) setTimeout(montrerPodium, 50);
  }

  function action() {
    const d = diapo();
    if (st.index === cours.diapositives.length - 1) { terminer(); return; }
    if (d.type === 'question' && st.q[d.id] && !st.q[d.id].revelee) { corriger(d); montrerCorrection(d); Q.annoncer('Correction affichée.'); return; }
    aller(st.index + 1);
  }
  function aller(i) {
    st.index = Math.max(0, Math.min(cours.diapositives.length - 1, i));
    sauver(); afficher();
  }

  /* ── Podium et fin ──────────────────────── */
  function htmlPodium(final) {
    const l = podium(), justes = cours.questions.filter(q => st.q[q.id] && st.q[q.id].revelee);
    if (!l.length) return '<p>Aucun·e élève connecté·e : pas de classement.</p>';
    let h = '';
    if (st.podium !== 'jamais' || final === 'force') {
      h += '<ol class="podium">' + l.filter(j => j.place <= 3).slice(0, 6).map(j => '<li class="place' + j.place + '"><span class="rang">' + j.place + (j.place === 1 ? 're' : 'e') + '</span><span class="qui">' + Q.echapper(j.pseudo) + '</span><span class="pts">' + j.total + ' points</span></li>').join('') + '</ol>';
    }
    // la progression de la classe : la réussite question par question
    if (justes.length) {
      h += '<h3>La classe, question par question</h3><ol class="reussite">' + justes.map(q => {
        const rep = repartition(q), n = rep.reduce((a, b) => a + b, 0), pc = n ? Math.round(rep[q.bonne] / n * 100) : 0;
        return '<li><span class="q">Q' + q.numero + '</span><span class="rep-barre"><span style="width:' + pc + '%"></span></span><span>' + pc + ' %</span></li>';
      }).join('') + '</ol>';
      const rebonds = l.map(j => ({ pseudo: j.pseudo, n: bilanJoueur(st.joueurs[j.id]).rebonds })).filter(x => x.n > 0).sort((a, b) => b.n - a.n).slice(0, 5);
      if (rebonds.length) h += '<p class="rebonds"><strong>Les rebonds</strong> (une bonne réponse juste après une erreur) : ' + rebonds.map(x => Q.echapper(x.pseudo) + ' (' + x.n + ')').join(', ') + '.</p>';
    }
    return h;
  }
  function montrerPodium(final) {
    $('podiumTitre').textContent = st.podium === 'jamais' && final !== 'force' ? 'Bilan de la classe' : 'Podium';
    $('podiumCorps').innerHTML = htmlPodium(final);
    const b = $('podiumBoite');
    if (!b.open) { try { b.showModal(); } catch (e) { b.setAttribute('open', ''); } }
  }
  function messageFin() {
    const l = podium(), res = {};
    for (const j of l) { const bj = bilanJoueur(st.joueurs[j.id]); res[j.id] = { total: j.total, place: j.place, bilan: bj, arevoir: st.ordre.filter((qid, k) => bj.suite[k] !== 'juste').map(qid => cours.diapositives.find(x => x.id === qid).numero) }; }
    return { t: 'fin', cours: cours.id, total: cours.questions.length, nb: l.length, podium: st.podium === 'jamais' ? null : l.filter(j => j.place <= 3).map(j => ({ pseudo: j.pseudo, total: j.total, place: j.place })), res };
  }
  function terminer() {
    st.fini = true; sauver();
    seance.envoyer(messageFin());
    majAction();
    montrerPodium();
  }

  /* ── La connexion ───────────────────────── */
  function connecter() {
    if (seance) seance.fermer();
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
    seance = Q.ouvrirSeance(st.code, { id: st.id, role: 'hote' }, {
      onMessage, onPresence,
      onEtat(e) {
        if (e === 'connexion') { z.className = 'etat'; z.textContent = 'Connexion à la séance en direct…'; }
        else if (e === 'connecte') { z.className = 'etat ok'; z.textContent = seance && seance.demo ? 'Mode démo : la séance passe entre les onglets de ce navigateur.' : 'Séance ouverte : les élèves peuvent rejoindre.'; planifierRenvoi(); }
        else if (e === 'erreur' || e === 'ferme') { z.className = 'etat ko'; z.innerHTML = 'Pas de connexion à la séance en direct : vérifie le réseau, puis recharge la page. Tu peux projeter le cours sans les téléphones, et proposer aux élèves de <a href="revision.html?cours=' + encodeURIComponent(cours.id) + '">réviser seul·e·s</a>, sans réseau de classe.'; }
      },
    });
  }

  function demarrerCours() {
    st.duree = +$('duree').value; st.podium = $('podium').value;
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
    st = Q.session.lire('animer:' + cours.id, null);
    const reprise = st && st.code && st.joueurs && st.commence;
    if (!st || !st.code || !st.joueurs) st = etatNeuf();
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
    document.addEventListener('click', ev => { const b = ev.target.closest('[data-retirer]'); if (b) retirer(b.dataset.retirer); });
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
