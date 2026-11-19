/* QuizzNSI : outils communs à toutes les pages (MIT, Babash - NSI Tani Malandi).
   - lecture d'un cours (cours/<id>.json) et contrôle léger de sa forme ;
   - mise en forme du texte (`code`, **gras**, *italique*), toujours échappée ;
   - coloration du Python ;
   - schémas SVG des piles et des files, dessinés à partir des données ;
   - formes et lettres des options (A ▲, B ◆, C ●, D ■) ;
   - pseudo filtré, code de séance, stockage de l'appareil, thème clair ou obscur. */
(function (racine) {
  'use strict';
  const Q = racine.QuizzNSI = racine.QuizzNSI || {};
  const LETTRES = ['A', 'B', 'C', 'D'];
  const NOMS_FORMES = ['triangle', 'losange', 'cercle', 'carré'];
  Q.LETTRES = LETTRES;
  Q.NOMS_FORMES = NOMS_FORMES;

  /* ── Texte ───────────────────────────────── */
  const ECH = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const echapper = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ECH[c]);
  Q.echapper = echapper;

  // `code` → <code>, **gras** → <strong>, *italique* → <em>. Le code n'est pas retouché.
  Q.texte = function (s) {
    return String(s == null ? '' : s).split('`').map((morceau, i) => {
      if (i % 2) return '<code class="py">' + colorerLigne(morceau) + '</code>';
      return echapper(morceau)
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>');
    }).join('');
  };

  /* ── Coloration du Python ────────────────── */
  const MOTS = new Set('False None True and as assert break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' '));
  const NATIFS = new Set('print len range list reversed int str float bool dict set tuple min max sum abs input isinstance enumerate sorted append pop insert'.split(' '));
  const JETON = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_À-ÿ][A-Za-z_0-9À-ÿ]*)|(\s+)|(.)/g;
  function colorerLigne(ligne) {
    let html = '', m, precedent = '';
    JETON.lastIndex = 0;
    while ((m = JETON.exec(ligne)) !== null) {
      if (m[0] === '') { JETON.lastIndex++; continue; }
      const [t, com, ch, nb, id] = m;
      if (com) html += '<span class="c-com">' + echapper(com) + '</span>';
      else if (ch) html += '<span class="c-ch">' + echapper(ch) + '</span>';
      else if (nb) html += '<span class="c-nb">' + nb + '</span>';
      else if (id) {
        const suite = ligne.slice(JETON.lastIndex);
        if (MOTS.has(id)) html += '<span class="c-mot">' + id + '</span>';
        else if (precedent === 'def' || precedent === 'class') html += '<span class="c-def">' + echapper(id) + '</span>';
        else if (/^\s*\(/.test(suite)) html += '<span class="' + (NATIFS.has(id) ? 'c-nat' : 'c-fn') + '">' + echapper(id) + '</span>';
        else if (id === 'self') html += '<span class="c-self">self</span>';
        else html += echapper(id);
      } else html += echapper(t);
      if (id) precedent = id; else if (!/^\s+$/.test(t)) precedent = '';
    }
    return html;
  }
  Q.colorerLigne = colorerLigne;

  // Un bloc de code numéroté, avec des guides d'indentation (lecture seule).
  Q.blocCode = function (lignes, opts) {
    opts = opts || {};
    const num = opts.numeros !== false && lignes.length > 2;
    const corps = lignes.map((l, i) => {
      const ind = (l.match(/^ */) || [''])[0].length;
      const guides = Array.from({ length: Math.floor(ind / 4) }, () => '<span class="guide">    </span>').join('');
      const reste = l.slice(Math.floor(ind / 4) * 4);
      return '<span class="ligne">' + (num ? '<span class="num" aria-hidden="true">' + (i + 1) + '</span>' : '') + guides + colorerLigne(reste) + '</span>';
    }).join('');
    return '<pre class="code' + (num ? ' numerote' : '') + '"><code>' + corps + '</code></pre>';
  };

  /* ── Formes des options ──────────────────── */
  const CHEMINS = [
    '<path d="M12 3 22 21H2z"/>',                 // A : triangle
    '<path d="M12 2 22 12 12 22 2 12z"/>',          // B : losange
    '<circle cx="12" cy="12" r="10"/>',             // C : cercle
    '<rect x="3" y="3" width="18" height="18" rx="2"/>' // D : carré
  ];
  Q.forme = (i, classe) => '<svg class="forme f' + i + (classe ? ' ' + classe : '') + '" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + CHEMINS[i] + '</svg>';
  Q.pastille = i => '<span class="pastille p' + i + '">' + Q.forme(i) + '<b>' + LETTRES[i] + '</b></span>';

  /* ── Schémas ─────────────────────────────── */
  const tx = (x, y, t, cl, ancre) => '<text x="' + x + '" y="' + y + '" class="' + (cl || '') + '" text-anchor="' + (ancre || 'middle') + '">' + echapper(t) + '</text>';
  const boite = (x, y, l, h, t, cl) => '<rect x="' + x + '" y="' + y + '" width="' + l + '" height="' + h + '" rx="5" class="' + (cl || 'case') + '"/>' + tx(x + l / 2, y + h / 2 + 6, t, 'val');
  const svg = (l, h, contenu, titre) => '<svg class="schema-svg" viewBox="0 0 ' + l + ' ' + h + '" width="' + l + '" height="' + h + '" role="img" aria-label="' + echapper(titre) + '"><title>' + echapper(titre) + '</title>' + contenu + '</svg>';
  const largeurTexte = t => Math.max(1, String(t).length) * 10 + 28;
  const fleche = (x1, y1, x2, y2) => '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="trait" marker-end="url(#pointe)"/>';
  const defs = '<defs><marker id="pointe" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" class="pointe"/></marker></defs>';

  // Une pile : elements du bas vers le haut.
  function dessinPile(elements, opts) {
    opts = opts || {};
    const H = 34, l = Math.max(110, ...elements.map(largeurTexte)), marge = opts.sansEtiquette ? 8 : 92;
    const n = elements.length, haut = 28 + Math.max(n, 1) * (H + 4) + 12;
    let c = defs;
    // le récipient : un U ouvert vers le haut
    c += '<path d="M' + (marge - 6) + ' 18 V' + (haut - 6) + ' H' + (marge + l + 6) + ' V18" class="bac"/>';
    elements.forEach((e, i) => { const y = haut - 10 - (i + 1) * (H + 4) + 4; c += boite(marge, y, l, H, e, i === n - 1 ? 'case sommet' : 'case'); });
    if (!n) c += tx(marge + l / 2, haut - 22, 'vide', 'muet');
    if (n && !opts.sansEtiquette) { const y = haut - 10 - n * (H + 4) + 4 + H / 2; c += tx(marge - 16, y + 5, 'sommet', 'etiq', 'end') + fleche(marge - 12, y, marge - 4, y); }
    const titre = opts.titre || ('Pile, du haut vers le bas : ' + (n ? elements.slice().reverse().join(', ') : 'vide'));
    return svg(marge + l + 14, haut, c, titre);
  }
  // Une file : elements de la tête vers la queue (la tête à gauche).
  function dessinFile(elements, opts) {
    opts = opts || {};
    const H = 36, larg = elements.map(largeurTexte), y = 36;
    let x = 92, c = defs;
    c += tx(46, 20, 'tête', 'etiq') + tx(46, 34, '(sortie)', 'muet petit');
    elements.forEach((e, i) => { c += boite(x, y, larg[i], H, e, i === 0 ? 'case sommet' : 'case'); x += larg[i] + 6; });
    if (!elements.length) { c += tx(x + 40, y + H / 2 + 6, 'vide', 'muet'); x += 80; }
    c += fleche(86, y + H / 2, 10, y + H / 2);
    c += fleche(x + 84, y + H / 2, x + 6, y + H / 2);
    c += tx(x + 46, 20, 'queue', 'etiq') + tx(x + 46, 34, '(entrée)', 'muet petit');
    const titre = opts.titre || ('File, de la tête vers la queue : ' + (elements.length ? elements.join(', ') : 'vide'));
    return svg(x + 96, y + H + 10, c, titre);
  }
  function dessinListe(elements, legende) {
    const H = 36, l = Math.max(56, ...elements.map(largeurTexte)), n = elements.length;
    let c = '';
    elements.forEach((e, i) => { const x = 10 + i * (l + 4); c += boite(x, 24, l, H, e, i === n - 1 ? 'case sommet' : 'case') + tx(x + l / 2, 16, String(i - n), 'muet petit') + tx(x + l / 2, 80, String(i), 'etiq'); });
    c += tx(10, 98, 'indices', 'muet petit', 'start');
    return svg(20 + n * (l + 4), 104, c, 'Liste Python ' + JSON.stringify(elements) + ' : indices de 0 à ' + (n - 1) + ', ou de ' + (-n) + ' à -1');
  }
  function dessinDecalage(elements) {
    const H = 34, l = 50, n = elements.length;
    let c = defs + tx(6, 20, 'avant', 'muet petit', 'start') + tx(6, 104, 'après pop(0)', 'muet petit', 'start');
    elements.forEach((e, i) => { const x = 10 + i * (l + 6); c += boite(x, 26, l, H, e, i === 0 ? 'case barre' : 'case'); if (i) c += boite(x - l - 6, 110, l, H, e) + fleche(x + l / 2, 26 + H + 2, x - 6 - l / 2, 108); });
    return svg(20 + n * (l + 6), 150, c, 'pop(0) retire ' + elements[0] + ' : les ' + (n - 1) + ' autres éléments reculent d\'une case');
  }
  function dessinDeuxPiles(s) {
    const g = dessinPile(s.gauche.elements, { sansEtiquette: true, titre: s.gauche.nom }), d = dessinPile(s.droite.elements, { sansEtiquette: true, titre: s.droite.nom });
    return '<div class="deux-piles"><figure><div>' + g + '</div><figcaption><code>' + echapper(s.gauche.nom) + '</code></figcaption></figure>'
      + '<div class="entre">' + (s.fleche ? '<span>' + echapper(s.fleche) + '</span>' : '') + '<svg viewBox="0 0 60 20" aria-hidden="true">' + defs + fleche(4, 10, 56, 10) + '</svg></div>'
      + '<figure><div>' + d + '</div><figcaption><code>' + echapper(s.droite.nom) + '</code></figcaption></figure></div>';
  }
  Q.schema = function (s) {
    if (!s || typeof s !== 'object') return '';
    let corps = '';
    if (s.type === 'pile') corps = dessinPile(s.elements || []);
    else if (s.type === 'file') corps = dessinFile(s.elements || []);
    else if (s.type === 'liste') corps = dessinListe(s.elements || []);
    else if (s.type === 'decalage') corps = dessinDecalage(s.elements || []);
    else if (s.type === 'deux-piles') corps = dessinDeuxPiles(s);
    else if (s.type === 'etapes') corps = '<ol class="etapes">' + (s.etapes || []).map(e => '<li><div>' + (s.structure === 'file' ? dessinFile(e.elements, {}) : dessinPile(e.elements, { sansEtiquette: true })) + '</div><code>' + Q.colorerLigne(e.op) + '</code></li>').join('') + '</ol>';
    else if (s.type === 'svg' && typeof s.code === 'string' && /^\s*<svg/.test(s.code) && !/<script|\son[a-z]+\s*=|javascript:/i.test(s.code)) corps = s.code;
    return '<figure class="schema schema-' + echapper(s.type) + '">' + corps + (s.legende ? '<figcaption>' + Q.texte(s.legende) + '</figcaption>' : '') + '</figure>';
  };

  /* ── Lecture d'un cours ──────────────────── */
  Q.idCours = function () {
    const p = new URLSearchParams(location.search).get('cours') || 'piles-files';
    return /^[a-z0-9-]{1,60}$/.test(p) ? p : 'piles-files';
  };
  Q.chargerCours = async function (id) {
    let rep;
    try { rep = await fetch('cours/' + id + '.json', { cache: 'no-cache' }); }
    catch (e) { throw new Error('Le fichier du cours n\'a pas pu être lu. Ouvre la page depuis le site (une adresse en https://), pas depuis un fichier de l\'ordinateur.'); }
    if (!rep.ok) throw new Error('Le cours « ' + id + ' » est introuvable (erreur ' + rep.status + ').');
    const cours = await rep.json();
    const pb = Q.controlerCours(cours);
    if (pb.length) throw new Error('Le fichier du cours n\'est pas conforme : ' + pb.join(' ; ') + '. Lance outils/verifier_cours.py.');
    cours.questions = cours.diapositives.filter(d => d.type === 'question');
    cours.questions.forEach((q, i) => { q.numero = i + 1; q.bonne = q.options.findIndex(o => o.juste === true); });
    return cours;
  };
  // Contrôle léger, dans le navigateur ; le contrôle complet est outils/verifier_cours.py.
  Q.controlerCours = function (c) {
    const pb = [];
    if (!c || c.format !== 'quizz-nsi/1') pb.push('format inconnu');
    if (!c || !Array.isArray(c.diapositives)) { pb.push('aucune diapositive'); return pb; }
    c.diapositives.forEach((d, i) => {
      if (d.type !== 'question') return;
      if (!Array.isArray(d.options) || d.options.length !== 4) pb.push('diapositive ' + (i + 1) + ' : 4 options attendues');
      else if (d.options.filter(o => o.juste === true).length !== 1) pb.push('diapositive ' + (i + 1) + ' : une seule option juste');
    });
    return pb;
  };

  /* ── Pseudo ──────────────────────────────── */
  // Un prénom ou un pseudo : 2 à 16 caractères, lettres (accents compris), chiffres, espace, tiret,
  // apostrophe, point, tiret bas. Tout caractère invisible ou de contrôle est refusé.
  Q.PSEUDO_MAX = 16;
  Q.filtrerPseudo = function (brut) {
    if (typeof brut !== 'string') return { ok: false, raison: 'Écris un prénom ou un pseudo.' };
    if (/[\p{C}\p{Zl}\p{Zp}]/u.test(brut)) return { ok: false, raison: 'Ce pseudo contient un caractère invisible : écris-le de nouveau, au clavier.' };
    const p = brut.normalize('NFC').replace(/\s+/gu, ' ').trim();
    if ([...p].length < 2) return { ok: false, raison: 'Deux caractères au moins.' };
    if ([...p].length > Q.PSEUDO_MAX) return { ok: false, raison: Q.PSEUDO_MAX + ' caractères au plus.' };
    if (!/^[\p{L}\p{M}\p{Nd}][\p{L}\p{M}\p{Nd} '’._-]*$/u.test(p)) return { ok: false, raison: 'Seulement des lettres, des chiffres, des espaces et - \' . _' };
    return { ok: true, pseudo: p };
  };
  Q.clePseudo = p => p.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^a-z0-9]/g, '');

  /* ── Code de séance ──────────────────────── */
  const ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ'; // sans I ni O, faciles à confondre
  Q.nouveauCode = () => { const a = new Uint8Array(4); crypto.getRandomValues(a); return [...a].map(x => ALPHA[x % 24]).join(''); };
  Q.lireCode = function (t) {
    const c = String(t || '').toUpperCase().normalize('NFD').replace(/[^A-Z0-9]/g, '').replace(/0/g, 'O').replace(/1/g, 'I');
    return /^[A-Z]{4}$/.test(c) && ![...c].some(x => x === 'I' || x === 'O') ? c : null;
  };
  Q.nouvelId = () => { const a = new Uint8Array(8); crypto.getRandomValues(a); return [...a].map(x => x.toString(16).padStart(2, '0')).join(''); };

  /* ── Stockage de l'appareil (une commodité : la page marche sans) ── */
  Q.stock = {
    lire(k, defaut) { try { const v = JSON.parse(localStorage.getItem('quizz-nsi:' + k)); return v == null ? defaut : v; } catch (e) { return defaut; } },
    ecrire(k, v) { try { localStorage.setItem('quizz-nsi:' + k, JSON.stringify(v)); } catch (e) { /* stockage bloqué */ } },
    oublier(k) { try { localStorage.removeItem('quizz-nsi:' + k); } catch (e) { /* rien */ } },
  };
  Q.session = {
    lire(k, defaut) { try { const v = JSON.parse(sessionStorage.getItem('quizz-nsi:' + k)); return v == null ? defaut : v; } catch (e) { return defaut; } },
    ecrire(k, v) { try { sessionStorage.setItem('quizz-nsi:' + k, JSON.stringify(v)); } catch (e) { /* rien */ } },
    oublier(k) { try { sessionStorage.removeItem('quizz-nsi:' + k); } catch (e) { /* rien */ } },
  };

  /* ── Thème clair ou obscur ───────────────── */
  Q.theme = function () {
    const r = document.documentElement, t = Q.stock.lire('theme', null);
    if (t === 'light' || t === 'dark') r.dataset.theme = t;
    document.querySelectorAll('[data-bascule-theme]').forEach(b => {
      const maj = () => { const sombre = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; b.setAttribute('aria-pressed', String(sombre)); b.textContent = sombre ? 'Affichage clair' : 'Affichage obscur'; };
      maj();
      b.addEventListener('click', () => { const sombre = b.getAttribute('aria-pressed') === 'true'; r.dataset.theme = sombre ? 'light' : 'dark'; Q.stock.ecrire('theme', r.dataset.theme); maj(); });
    });
  };

  Q.$ = id => document.getElementById(id);
  Q.annoncer = function (texte) { const z = Q.$('annonce'); if (z) { z.textContent = ''; setTimeout(() => { z.textContent = texte; }, 30); } };
  Q.erreurPage = function (conteneur, message) {
    conteneur.innerHTML = '<div class="alerte" role="alert"><p><strong>Le cours ne peut pas s\'afficher.</strong></p><p>' + echapper(message) + '</p></div>';
  };
})(typeof window !== 'undefined' ? window : globalThis);
