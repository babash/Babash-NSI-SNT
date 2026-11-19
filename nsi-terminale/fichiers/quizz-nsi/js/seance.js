/* QuizzNSI : une séance en direct (MIT, Babash - NSI Tani Malandi).
   Rien n'est enregistré en ligne : une séance est un canal temps réel de Supabase (diffusion et
   présence), sans aucune table. Le pseudo et les réponses passent en direct, puis disparaissent.
   Mode démo (?demo, ou sans configuration) : la séance passe entre les onglets de ce navigateur.

   ouvrirSeance(code, moi, { onMessage, onPresence, onEtat }) renvoie { envoyer, maj, fermer, demo }.
   onEtat reçoit 'connexion', 'connecte', 'erreur' ou 'ferme'. */
(function (racine) {
  'use strict';
  const Q = racine.QuizzNSI = racine.QuizzNSI || {};
  const params = new URLSearchParams(location.search);

  Q.modeDemo = function () {
    const cfg = racine.QUIZZ_CONFIG;
    try {
      if (params.get('demo') === '0') sessionStorage.removeItem('quizz-nsi:demo');
      else if (params.has('demo')) sessionStorage.setItem('quizz-nsi:demo', '1');
      return sessionStorage.getItem('quizz-nsi:demo') === '1' || !cfg || !cfg.SUPABASE_URL;
    } catch (e) { return params.has('demo') || !cfg || !cfg.SUPABASE_URL; }
  };

  Q.ouvrirSeance = function (code, moi, rappels) {
    return Q.modeDemo() ? seanceDemo(code, moi, rappels) : seanceEnLigne(code, moi, rappels);
  };

  function seanceEnLigne(code, moi, { onMessage, onPresence, onEtat }) {
    const cfg = racine.QUIZZ_CONFIG;
    if (!racine.TempsReel) { setTimeout(() => onEtat('erreur'), 0); return { envoyer() {}, maj() {}, fermer() {}, demo: false }; }
    let client, ch, info = Object.assign({}, moi), fini = false, delai;
    try {
      const url = cfg.SUPABASE_URL.replace(/^http/, 'ws') + '/realtime/v1';
      client = new racine.TempsReel.RealtimeClient(url, { params: { apikey: cfg.SUPABASE_KEY, eventsPerSecond: 20 } });
      ch = client.channel('quizz-nsi:' + code, { config: { broadcast: { self: false, ack: false }, presence: { key: moi.id } } });
    } catch (e) { setTimeout(() => onEtat('erreur'), 0); return { envoyer() {}, maj() {}, fermer() {}, demo: false }; }
    onEtat('connexion');
    delai = setTimeout(() => { if (!fini) onEtat('erreur'); }, 12000);
    ch.on('broadcast', { event: 'm' }, ({ payload }) => { if (payload && typeof payload === 'object') onMessage(payload); });
    ch.on('presence', { event: 'sync' }, () => onPresence(Object.values(ch.presenceState()).map(l => l[l.length - 1])));
    ch.subscribe(async st => {
      if (st === 'SUBSCRIBED') { fini = true; clearTimeout(delai); onEtat('connecte'); try { await ch.track(info); } catch (e) { /* présence plus tard */ } }
      else if (st === 'CHANNEL_ERROR' || st === 'TIMED_OUT') onEtat('erreur');
      else if (st === 'CLOSED') onEtat('ferme');
    });
    return {
      envoyer(msg) { try { const p = ch.send({ type: 'broadcast', event: 'm', payload: msg }); if (p && p.catch) p.catch(() => {}); } catch (e) { /* hors ligne */ } },
      maj(plus) { info = Object.assign({}, info, plus); try { const p = ch.track(info); if (p && p.catch) p.catch(() => {}); } catch (e) { /* rien */ } },
      fermer() { clearTimeout(delai); try { ch.unsubscribe(); client.disconnect(); } catch (e) { /* rien */ } },
      demo: false,
    };
  }

  function seanceDemo(code, moi, { onMessage, onPresence, onEtat }) {
    const bc = new BroadcastChannel('quizz-nsi-demo:' + code), vus = new Map();
    let info = Object.assign({}, moi);
    const publier = () => onPresence([info].concat([...vus.values()].map(v => v.info)));
    const battre = () => bc.postMessage({ k: 'p', info });
    bc.onmessage = ({ data }) => {
      if (!data) return;
      if (data.k === 'p') { const neuf = !vus.has(data.info.id); vus.set(data.info.id, { info: data.info, vu: Date.now() }); publier(); if (neuf) battre(); }
      else if (data.k === 'q') { vus.delete(data.id); publier(); }
      else if (data.k === 'm') onMessage(data.msg);
    };
    const tic = setInterval(() => { battre(); const t = Date.now(); let ch = false; for (const [id, v] of vus) if (t - v.vu > 7000) { vus.delete(id); ch = true; } if (ch) publier(); }, 2000);
    const bye = () => bc.postMessage({ k: 'q', id: moi.id });
    racine.addEventListener('pagehide', bye);
    setTimeout(() => { onEtat('connecte'); battre(); publier(); }, 50);
    return {
      envoyer(msg) { bc.postMessage({ k: 'm', msg }); },
      maj(plus) { info = Object.assign({}, info, plus); battre(); publier(); },
      fermer() { bye(); clearInterval(tic); bc.close(); },
      demo: true,
    };
  }

  Q.lienEleve = function (code) {
    const u = new URL('rejoindre.html', location.href);
    u.search = ''; u.hash = '';
    u.searchParams.set('s', code);
    if (Q.modeDemo()) u.searchParams.set('demo', '');
    return u.href.replace('demo=&', 'demo&').replace(/demo=$/, 'demo');
  };
})(window);
