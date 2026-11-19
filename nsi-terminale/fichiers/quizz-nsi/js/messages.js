/* QuizzNSI : validation stricte de tout ce qui arrive par le canal temps réel (MIT, Babash - NSI Tani Malandi).
   Le canal est public : n'importe qui qui connaît le code de séance peut y envoyer un message.
   Chaque message est donc contrôlé à l'entrée par un schéma strict : type, clés permises,
   entiers bornés, chaînes au format attendu, listes bornées. Un message non conforme est ignoré
   (null). Les pages n'affichent ensuite les valeurs reçues que par textContent ou par des éléments
   créés un à un, jamais par innerHTML ; le texte des questions vient du fichier du cours, pas du canal.
   Ce que le canal diffuse se limite à ce que l'écran projeté montre déjà à toute la classe : la bonne
   réponse, la répartition des réponses (en nombres), le podium quand il est affiché. Chaque téléphone
   calcule ses propres points ; les réponses des élèves arrivent chiffrées pour la seule page projetée.
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
  function bareme(v) {
    const k = ['participation', 'juste', 'rapidite', 'rebond'];
    if (!cles(v, k) || !k.every(x => entier(v[x], 0, MAX_POINTS_Q))) return null;
    return { participation: v.participation, juste: v.juste, rapidite: v.rapidite, rebond: v.rebond };
  }
  const NONCE = /^[0-9a-f]{16}$/;

  /* Messages de la page projetée vers les élèves. Ils ne portent que ce que l'écran projeté montre
     déjà à toute la classe : jamais la réponse ni les points d'un·e élève. */
  function versEleve(m, moiId) {
    if (!objet(m) || typeof m.t !== 'string') return null;
    switch (m.t) {
      case 'attente':
        return cles(m, ['t']) ? { t: 'attente' } : null;
      case 'notion':
        return cles(m, ['t', 'cours', 'n', 'f']) && estCours(m.cours) && entier(m.n, 0, MAX_Q) && entier(m.f, 0, 100) ? { t: 'notion', cours: m.cours, n: m.n, f: m.f } : null;
      case 'question':
        if (!cles(m, ['t', 'cours', 'qid', 'reste', 'duree', 'ferme']) || !estCours(m.cours) || !estQid(m.qid) || typeof m.ferme !== 'boolean' || !entier(m.duree, 0, 3600)) return null;
        if (!(m.reste === null || entier(m.reste, 0, 3600000))) return null;
        return { t: 'question', cours: m.cours, qid: m.qid, reste: m.reste, duree: m.duree, ferme: m.ferme };
      case 'fermee':
        return cles(m, ['t', 'qid']) && estQid(m.qid) ? { t: 'fermee', qid: m.qid } : null;
      case 'recus':
        if (!cles(m, ['t', 'qid', 'n']) || !estQid(m.qid) || !Array.isArray(m.n) || m.n.length > MAX_ELEVES || !m.n.every(x => typeof x === 'string' && NONCE.test(x))) return null;
        return { t: 'recus', qid: m.qid, n: m.n.slice() };
      case 'retire':
        return cles(m, ['t', 'id']) && estId(m.id) ? { t: 'retire', pourMoi: m.id === moiId } : null;
      case 'refus':
        return cles(m, ['t', 'id', 'raison']) && estId(m.id) && (m.raison === 'pris' || m.raison === 'invalide') ? { t: 'refus', pourMoi: m.id === moiId, raison: m.raison } : null;
      case 'correction': {
        if (!cles(m, ['t', 'cours', 'qid', 'precedente', 'bonne', 'rep', 'bareme', 'duree', 'podium']) || !estCours(m.cours) || !estQid(m.qid)) return null;
        if (!(m.precedente === null || estQid(m.precedente)) || !entier(m.bonne, 0, 3) || !entier(m.duree, 0, 3600)) return null;
        if (!Array.isArray(m.rep) || m.rep.length !== 4 || !m.rep.every(n => entier(n, 0, MAX_ELEVES))) return null;
        const b = bareme(m.bareme); if (!b) return null;
        const pd = podium(m.podium); if (pd === undefined) return null;
        return { t: 'correction', cours: m.cours, qid: m.qid, precedente: m.precedente, bonne: m.bonne, rep: m.rep.slice(), bareme: b, duree: m.duree, podium: pd };
      }
      case 'fin': {
        if (!cles(m, ['t', 'cours', 'podium']) || !estCours(m.cours)) return null;
        const pd = podium(m.podium); if (pd === undefined) return null;
        return { t: 'fin', cours: m.cours, podium: pd };
      }
      default:
        return null;
    }
  }

  /* Messages des élèves vers la page projetée. */
  function versHote(m) {
    if (!objet(m) || typeof m.t !== 'string') return null;
    if (m.t === 'bonjour') return cles(m, ['t', 'id']) && estId(m.id) ? { t: 'bonjour', id: m.id } : null;
    // une réponse arrive chiffrée (js/chiffre.js) : on ne contrôle ici que l'enveloppe
    if (m.t === 'rep') return cles(m, ['t', 'de', 'iv', 'donnees']) && Q.chiffre && Q.chiffre.estClePublique(m.de) && typeof m.iv === 'string' && /^[A-Za-z0-9_-]{16}$/.test(m.iv)
      && typeof m.donnees === 'string' && /^[A-Za-z0-9_-]{1,400}$/.test(m.donnees) ? { t: 'rep', de: { x: m.de.x, y: m.de.y }, iv: m.iv, donnees: m.donnees } : null;
    return null;
  }
  /* Le contenu déchiffré d'une réponse. */
  function reponse(m) {
    return cles(m, ['id', 'qid', 'c', 'n']) && estId(m.id) && estQid(m.qid) && entier(m.c, 0, 3) && typeof m.n === 'string' && NONCE.test(m.n) ? { id: m.id, qid: m.qid, c: m.c, n: m.n } : null;
  }

  /* Une entrée de présence. Les élèves : { id, pseudo, role: 'eleve' } ; l'hôte : { id, role: 'hote' }.
     Supabase ajoute presence_ref : c'est la seule clé de plus permise. */
  function presence(p) {
    if (!objet(p) || !estId(p.id)) return null;
    if (p.role === 'hote') return cles(p, ['id', 'role', 'cle', 'presence_ref']) && (p.cle === undefined || (Q.chiffre && Q.chiffre.estClePublique(p.cle))) ? { id: p.id, role: 'hote', cle: p.cle ? { x: p.cle.x, y: p.cle.y } : null } : null;
    if (p.role !== 'eleve' || !cles(p, ['id', 'pseudo', 'role', 'presence_ref']) || typeof p.pseudo !== 'string' || p.pseudo.length > 64) return null;
    const f = Q.filtrerPseudo(p.pseudo);
    return { id: p.id, role: 'eleve', pseudo: f.ok ? f.pseudo : null };
  }

  Q.messages = { versEleve, versHote, reponse, presence, estId, estQid, estCours };
  if (typeof module !== 'undefined' && module.exports) module.exports = Q.messages;
})(typeof window !== 'undefined' ? window : globalThis);
