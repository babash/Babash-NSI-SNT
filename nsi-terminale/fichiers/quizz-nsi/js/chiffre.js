/* QuizzNSI : chiffrement des réponses des élèves (MIT, Babash - NSI Tani Malandi).
   Le canal temps réel est public : tout message y est reçu par tous les appareils de la séance.
   La réponse d'un·e élève n'est donc lisible que par la page projetée : celle-ci publie une clé
   publique (ECDH P-256) dans sa présence ; chaque téléphone en tire une clé AES-GCM qu'il partage
   seul avec elle, et chiffre sa réponse. Les autres téléphones ne voient qu'un message illisible.
   Tout passe par l'API Web Crypto du navigateur (pages en https ou en local). */
(function (racine) {
  'use strict';
  const Q = racine.QuizzNSI = racine.QuizzNSI || {};
  const ECDH = { name: 'ECDH', namedCurve: 'P-256' };
  const B64 = /^[A-Za-z0-9_-]+$/;

  const versB64 = octets => { let s = ''; for (const b of new Uint8Array(octets)) s += String.fromCharCode(b); return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); };
  const depuisB64 = t => { const s = atob(t.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((t.length + 3) % 4)); return Uint8Array.from(s, c => c.charCodeAt(0)); };
  // une clé publique : deux coordonnées de 32 octets, en base64url (43 caractères)
  const estClePublique = v => v !== null && typeof v === 'object' && !Array.isArray(v) && Object.keys(v).length === 2
    && typeof v.x === 'string' && typeof v.y === 'string' && v.x.length === 43 && v.y.length === 43 && B64.test(v.x) && B64.test(v.y);

  const disponible = () => !!(racine.crypto && racine.crypto.subtle);
  async function paire() {
    const p = await crypto.subtle.generateKey(ECDH, false, ['deriveKey']); // clé privée non extractible ; la publique s'exporte toujours
    const j = await crypto.subtle.exportKey('jwk', p.publicKey);
    return { prive: p.privateKey, publique: { x: j.x, y: j.y } };
  }
  async function cleCommune(prive, publique) {
    const autre = await crypto.subtle.importKey('jwk', { kty: 'EC', crv: 'P-256', x: publique.x, y: publique.y, ext: true }, ECDH, false, []);
    return crypto.subtle.deriveKey({ name: 'ECDH', public: autre }, prive, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
  }

  /* La page projetée : sa clé publique, et le déchiffrement d'un message { de, iv, donnees }.
     Renvoie l'objet déchiffré, ou null (message illisible, forgé ou trop long). */
  async function hote() {
    const p = await paire(), cache = new Map();
    return {
      publique: p.publique,
      async dechiffrer(m) {
        try {
          if (!estClePublique(m.de) || typeof m.iv !== 'string' || m.iv.length !== 16 || !B64.test(m.iv) || typeof m.donnees !== 'string' || m.donnees.length > 400 || !B64.test(m.donnees)) return null;
          const k = m.de.x + m.de.y;
          if (!cache.has(k)) { if (cache.size > 5000) cache.clear(); cache.set(k, cleCommune(p.prive, m.de)); }
          const clair = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: depuisB64(m.iv) }, await cache.get(k), depuisB64(m.donnees));
          return JSON.parse(new TextDecoder().decode(clair));
        } catch (e) { cache.delete(m && m.de ? m.de.x + m.de.y : ''); return null; }
      },
    };
  }

  /* Un téléphone : chiffrer un objet pour une clé publique de la page projetée. */
  async function eleve() {
    const p = await paire(), cles = new Map();
    return {
      async chiffrer(objet, publiqueHote) {
        const k = publiqueHote.x + publiqueHote.y;
        if (!cles.has(k)) cles.set(k, cleCommune(p.prive, publiqueHote));
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const donnees = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await cles.get(k), new TextEncoder().encode(JSON.stringify(objet)));
        return { de: p.publique, iv: versB64(iv), donnees: versB64(donnees) };
      },
    };
  }

  Q.chiffre = { disponible, hote, eleve, estClePublique };
})(typeof window !== 'undefined' ? window : globalThis);
