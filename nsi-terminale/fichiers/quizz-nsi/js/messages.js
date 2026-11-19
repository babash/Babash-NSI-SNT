/* QuizzNSI : validation stricte de tout ce qui arrive par le canal temps réel (MIT, Babash - NSI Tani Malandi).
   Le canal est public : n'importe qui qui connaît le code de séance peut y envoyer un message.
   Chaque message est donc contrôlé à l'entrée par un schéma strict : type, clés permises,
   entiers bornés, chaînes au format attendu, listes bornées. Un message non conforme est ignoré
   (null). Les pages n'affichent ensuite les valeurs reçues que par textContent ou par des éléments
   créés un à un, jamais par innerHTML ; le texte des questions vient du fichier du cours, pas du canal.
   Fonctions pures, testées par tests/test_messages.js. */
(function (racine) {
  'use strict';
  const Q = racine.QuizzNSI = racine.QuizzNSI || {};

  const objet = v => v !== null && typeof v === 'object' && !Array.isArray(v) && Object.getPrototypeOf(v) === Object.prototype;
  const cles = (v, permises) => objet(v) && Object.keys(v).every(k => permises.includes(k));
  const entier = (v, min, max) => Number.isSafeInteger(v) && v >= min && v <= max;
  const ID = /^[0-9a-f]{16}$/, QID = /^[a-z0-9-]{1,20}$/, COURS = /^[a-z0-9-]{1,60}$/;
  const estId = v => typeof v === 'string' && ID.test(v);
  const estQid = v => typeof v === 'string' && QID.test(v);
  const estCours = v => typeof v === 'string' && COURS.test(v);
  const MAX_POINTS = 10000000, MAX_Q = 1000, MAX_ELEVES = 100000, MAX_POINTS_Q = 1000;

  function pseudo(v) {
    if (!Q.filtrerPseudo) return null;
    const f = Q.filtrerPseudo(v);
    return f.ok && f.pseudo === v ? v : null;
  }

  function detail(v) {
    if (v === null) return null;
    if (!cles(v, ['participation', 'juste', 'rapidite', 'rebond'])) return undefined;
    for (const k of ['participation', 'juste', 'rapidite', 'rebond']) if (!entier(v[k], 0, MAX_POINTS_Q)) return undefined;
    return { participation: v.participation, juste: v.juste, rapidite: v.rapidite, rebond: v.rebond };
  }
  function bilan(v) {
    if (!cles(v, ['justes', 'repondues', 'serie', 'meilleure', 'rebonds', 'suite'])) return null;
    for (const k of ['justes', 'repondues', 'serie', 'meilleure', 'rebonds']) if (!entier(v[k], 0, MAX_Q)) return null;
    if (!Array.isArray(v.suite) || v.suite.length > MAX_Q || !v.suite.every(r => r === 'juste' || r === 'faux' || r === null)) return null;
    return { justes: v.justes, repondues: v.repondues, serie: v.serie, meilleure: v.meilleure, rebonds: v.rebonds, suite: v.suite.slice() };
  }
  function podium(v) {
    if (v === null || v === undefined) return null;
    if (!Array.isArray(v) || v.length > 20) return undefined;
    const l = [];
    for (const p of v) {
      if (!cles(p, ['pseudo', 'total', 'place']) || !pseudo(p.pseudo) || !entier(p.total, 0, MAX_POINTS) || !entier(p.place, 1, MAX_ELEVES)) return undefined;
      l.push({ pseudo: p.pseudo, total: p.total, place: p.place });
    }
    return l;
  }

  // Les résultats de toute la classe : chaque entrée est validée (un message dont une seule entrée est
  // forgée est rejeté entier) ; seule celle de l'élève lui-même (moiId) est gardée.
  function resultats(res, moiId, valider) {
    if (!objet(res)) return undefined;
    const ids = Object.keys(res);
    if (ids.length > MAX_ELEVES) return undefined;
    let moi = null;
    for (const id of ids) {
      if (!estId(id)) return undefined;
      const v = valider(res[id]);
      if (!v) return undefined;
      if (id === moiId) moi = v;
    }
    return moi;
  }
  function resCorrection(r) {
    if (!cles(r, ['c', 'gain', 'detail', 'total', 'bilan'])) return null;
    if (!(r.c === null || entier(r.c, 0, 3)) || !entier(r.gain, 0, MAX_POINTS_Q) || !entier(r.total, 0, MAX_POINTS)) return null;
    const d = detail(r.detail), b = bilan(r.bilan);
    if (d === undefined || !b) return null;
    return { c: r.c, gain: r.gain, detail: d, total: r.total, bilan: b };
  }
  function resFin(r) {
    if (!cles(r, ['total', 'place', 'bilan', 'arevoir']) || !entier(r.total, 0, MAX_POINTS) || !entier(r.place, 1, MAX_ELEVES)) return null;
    const b = bilan(r.bilan);
    if (!b || !Array.isArray(r.arevoir) || r.arevoir.length > MAX_Q || !r.arevoir.every(n => entier(n, 1, MAX_Q))) return null;
    return { total: r.total, place: r.place, bilan: b, arevoir: r.arevoir.slice() };
  }

  /* Messages de la page projetée vers les élèves. */
  function versEleve(m, moiId) {
    if (!objet(m) || typeof m.t !== 'string') return null;
    switch (m.t) {
      case 'attente':
        return cles(m, ['t']) ? { t: 'attente' } : null;
      case 'notion':
        return cles(m, ['t', 'cours', 'n']) && estCours(m.cours) && entier(m.n, 0, MAX_Q) ? { t: 'notion', cours: m.cours, n: m.n } : null;
      case 'question':
        if (!cles(m, ['t', 'cours', 'qid', 'reste', 'ferme']) || !estCours(m.cours) || !estQid(m.qid) || typeof m.ferme !== 'boolean') return null;
        if (!(m.reste === null || entier(m.reste, 0, 3600000))) return null;
        return { t: 'question', cours: m.cours, qid: m.qid, reste: m.reste, ferme: m.ferme };
      case 'fermee':
        return cles(m, ['t', 'qid']) && estQid(m.qid) ? { t: 'fermee', qid: m.qid } : null;
      case 'recus':
        if (!cles(m, ['t', 'qid', 'ids']) || !estQid(m.qid) || !Array.isArray(m.ids) || m.ids.length > MAX_ELEVES || !m.ids.every(estId)) return null;
        return { t: 'recus', qid: m.qid, pourMoi: m.ids.includes(moiId) };
      case 'retire':
        return cles(m, ['t', 'id']) && estId(m.id) ? { t: 'retire', pourMoi: m.id === moiId } : null;
      case 'refus':
        return cles(m, ['t', 'id', 'raison']) && estId(m.id) && (m.raison === 'pris' || m.raison === 'invalide') ? { t: 'refus', pourMoi: m.id === moiId, raison: m.raison } : null;
      case 'correction': {
        if (!cles(m, ['t', 'cours', 'qid', 'rep', 'res', 'podium']) || !estCours(m.cours) || !estQid(m.qid)) return null;
        if (!Array.isArray(m.rep) || m.rep.length !== 4 || !m.rep.every(n => entier(n, 0, MAX_ELEVES))) return null;
        const pd = podium(m.podium); if (pd === undefined) return null;
        const moi = resultats(m.res, moiId, resCorrection); if (moi === undefined) return null;
        return { t: 'correction', cours: m.cours, qid: m.qid, rep: m.rep.slice(), moi, podium: pd };
      }
      case 'fin': {
        if (!cles(m, ['t', 'cours', 'res', 'podium']) || !estCours(m.cours)) return null;
        const pd = podium(m.podium); if (pd === undefined) return null;
        const moi = resultats(m.res, moiId, resFin); if (moi === undefined) return null;
        return { t: 'fin', cours: m.cours, moi, podium: pd };
      }
      default:
        return null;
    }
  }

  /* Messages des élèves vers la page projetée. */
  function versHote(m) {
    if (!objet(m) || typeof m.t !== 'string') return null;
    if (m.t === 'bonjour') return cles(m, ['t', 'id']) && estId(m.id) ? { t: 'bonjour', id: m.id } : null;
    if (m.t === 'rep') return cles(m, ['t', 'id', 'qid', 'c']) && estId(m.id) && estQid(m.qid) && entier(m.c, 0, 3) ? { t: 'rep', id: m.id, qid: m.qid, c: m.c } : null;
    return null;
  }

  /* Une entrée de présence. Les élèves : { id, pseudo, role: 'eleve' } ; l'hôte : { id, role: 'hote' }.
     Supabase ajoute presence_ref : c'est la seule clé de plus permise. */
  function presence(p) {
    if (!objet(p) || !estId(p.id)) return null;
    if (p.role === 'hote') return cles(p, ['id', 'role', 'presence_ref']) ? { id: p.id, role: 'hote' } : null;
    if (p.role !== 'eleve' || !cles(p, ['id', 'pseudo', 'role', 'presence_ref']) || typeof p.pseudo !== 'string' || p.pseudo.length > 64) return null;
    const f = Q.filtrerPseudo(p.pseudo);
    return { id: p.id, role: 'eleve', pseudo: f.ok ? f.pseudo : null };
  }

  Q.messages = { versEleve, versHote, presence, estId, estQid, estCours };
  if (typeof module !== 'undefined' && module.exports) module.exports = Q.messages;
})(typeof window !== 'undefined' ? window : globalThis);
