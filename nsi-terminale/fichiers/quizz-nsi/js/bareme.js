/* QuizzNSI : le barème du mode « en classe » (MIT, Babash - NSI Tani Malandi).
   Fonctions pures, sans page ni réseau : elles sont testées par tests/test_bareme.js (node).

   Barème proposé (à valider par l'enseignant·e) :
   - répondre, même faux : +10 (on ose répondre) ;
   - bonne réponse : +100 ;
   - rapidité : jusqu'à +20, seulement avec une minuterie, et seulement pour une bonne réponse
     (réfléchir rapporte toujours plus que se presser : 100 contre 20 au plus) ;
   - rebond : +30 pour une bonne réponse juste après une erreur à la question précédente
     (on valorise la progression, pas seulement les meilleur·e·s).
   Une question rapporte donc de 10 à 150 points. */
(function (racine) {
  'use strict';
  const BAREME = { participation: 10, juste: 100, rapidite: 20, rebond: 30 };

  /* Points d'une réponse.
     r : { juste: booléen, ms: temps de réponse en millisecondes }
     ctx : { duree: durée de la minuterie en secondes (0 ou absente : sans minuterie),
             precedente: 'juste' | 'faux' | null (la réponse de l'élève à la question jouée juste avant) } */
  function points(r, ctx, b) {
    b = b || BAREME; ctx = ctx || {};
    const detail = { participation: 0, juste: 0, rapidite: 0, rebond: 0 };
    if (!r) return { total: 0, detail };
    detail.participation = b.participation;
    if (r.juste) {
      detail.juste = b.juste;
      if (ctx.duree > 0 && Number.isFinite(r.ms)) {
        const part = 1 - Math.min(Math.max(r.ms, 0), ctx.duree * 1000) / (ctx.duree * 1000);
        detail.rapidite = Math.round(b.rapidite * part);
      }
      if (ctx.precedente === 'faux') detail.rebond = b.rebond;
    }
    return { total: detail.participation + detail.juste + detail.rapidite + detail.rebond, detail };
  }

  /* Classement : un tableau [{ id, pseudo, total, justes }], trié par points, puis bonnes réponses,
     puis pseudo (ordre stable et prévisible). Les ex aequo partagent la même place. */
  function classer(joueurs) {
    const l = joueurs.slice().sort((a, b) => b.total - a.total || b.justes - a.justes || String(a.pseudo).localeCompare(String(b.pseudo), 'fr'));
    let place = 0, avant = null;
    l.forEach((j, i) => { if (!avant || j.total !== avant.total || j.justes !== avant.justes) place = i + 1; j.place = place; avant = j; });
    return l;
  }

  /* Répartition des réponses d'une question : [nA, nB, nC, nD]. */
  function repartition(reponses) {
    const n = [0, 0, 0, 0];
    for (const c of reponses) if (Number.isInteger(c) && c >= 0 && c < 4) n[c]++;
    return n;
  }

  /* La progression d'un·e élève : séries et rebonds, à partir de ses résultats dans l'ordre joué
     ('juste', 'faux' ou null quand il ou elle n'a pas répondu). */
  function progression(resultats) {
    let serie = 0, meilleure = 0, rebonds = 0, justes = 0, repondues = 0, prec = null;
    for (const r of resultats) {
      if (r) repondues++;
      if (r === 'juste') { justes++; serie++; meilleure = Math.max(meilleure, serie); if (prec === 'faux') rebonds++; }
      else serie = 0;
      prec = r;
    }
    return { justes, repondues, serie, meilleure, rebonds };
  }

  const api = { BAREME, points, classer, repartition, progression };
  racine.QuizzNSI = racine.QuizzNSI || {};
  racine.QuizzNSI.bareme = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
