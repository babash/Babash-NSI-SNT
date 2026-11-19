/* QuizzNSI : un faux client temps réel, pour les tests (tests/test_parcours.py).
   Il remplace vendor/temps-reel.js et imite l'interface utilisée par js/seance.js
   (RealtimeClient, channel, on, subscribe, track, presenceState, send, unsubscribe, disconnect),
   mais passe par un BroadcastChannel du navigateur : aucune requête ne sort.
   Il note l'adresse et la clé reçues dans window.__fauxTempsReel, pour que le test les contrôle. */
(function () {
  'use strict';
  const journal = window.__fauxTempsReel = { clients: [], envois: 0 };
  class Canal {
    constructor(nom, opts) {
      this.nom = nom; this.cle = opts && opts.config && opts.config.presence && opts.config.presence.key;
      this.ecoutes = { broadcast: [], presence: [] }; this.etat = {}; this.moi = null; this.bc = null;
    }
    on(type, filtre, cb) { this.ecoutes[type].push({ filtre, cb }); return this; }
    _sync() { for (const e of this.ecoutes.presence) if (e.filtre.event === 'sync') e.cb(); }
    subscribe(cb) {
      this.bc = new BroadcastChannel('faux:' + this.nom);
      this.bc.onmessage = ({ data }) => {
        if (data.k === 'b') { for (const e of this.ecoutes.broadcast) if (e.filtre.event === data.event) e.cb({ type: 'broadcast', event: data.event, payload: data.payload }); }
        else if (data.k === 'p') { const neuf = !this.etat[data.cle]; this.etat[data.cle] = [data.info]; this._sync(); if (neuf && this.moi) this.bc.postMessage({ k: 'p', cle: this.cle, info: this.moi }); }
        else if (data.k === 'q') { delete this.etat[data.cle]; this._sync(); }
      };
      window.addEventListener('pagehide', () => this.unsubscribe());
      setTimeout(() => cb('SUBSCRIBED'), 30);
      return this;
    }
    track(info) { this.moi = info; this.etat[this.cle] = [info]; this.bc.postMessage({ k: 'p', cle: this.cle, info }); this._sync(); return Promise.resolve('ok'); }
    presenceState() { return JSON.parse(JSON.stringify(this.etat)); }
    send(m) { journal.envois++; this.bc.postMessage({ k: 'b', event: m.event, payload: JSON.parse(JSON.stringify(m.payload)) }); return Promise.resolve('ok'); }
    unsubscribe() { if (this.bc) { try { this.bc.postMessage({ k: 'q', cle: this.cle }); this.bc.close(); } catch (e) { /* déjà fermé */ } this.bc = null; } return Promise.resolve('ok'); }
  }
  class RealtimeClient {
    constructor(url, opts) {
      if (!opts || !opts.params || !opts.params.apikey) throw new Error('API key is required to connect to Realtime');
      journal.clients.push({ url, apikey: opts.params.apikey });
    }
    channel(nom, opts) { return new Canal(nom, opts); }
    disconnect() { return Promise.resolve('ok'); }
  }
  window.TempsReel = { RealtimeClient };
})();
