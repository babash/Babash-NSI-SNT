#!/usr/bin/env python3
"""Fait le PDF de référence d'un TD en ligne : la feuille vierge, comme le papier.

Usage (serveur local lancé à la racine du dépôt : python3 -m http.server 8000) :
  python3 -I charte/imprimer-td.py http://localhost:8000/charte/td-pilote/index.html charte/td-pilote/td-boucles.pdf

  TD à plusieurs feuilles : toutes les adresses, dans l'ordre, puis le PDF.
  python3 -I charte/imprimer-td.py http://…/td-for.html http://…/td-for-2.html http://…/td-for-3.html td-for.pdf
  Chaque feuille est contrôlée seule (et doit tenir dans son nombre de pages), puis le PDF est fait d'un seul
  tenant : les feuilles se suivent sans saut de page, la deuxième et les suivantes avec une bande de titre fine.

  Pages : 4 au plus par feuille ; une feuille peut en déclarer davantage avec data-pages-max sur <main>
  (exemple : 5 pour un exercice de bac de 6 points).

Les polices sont hébergées sur le site (assets/fonts/) : aucune option n'est nécessaire.
(L'ancienne option --polices, pour Google Fonts, est acceptée et ignorée.)

Le script :
1. ouvre la page sans aucun stockage (aucune réponse gardée) et vérifie que tous les champs sont vides ;
2. écrit un repère dans chaque champ et dans chaque éditeur, coche chaque case, remet par de vrais
   clics les lignes des questions « ordre » dans l'ordre de la solution, puis déclenche
   l'impression (événement beforeprint) : le moteur doit tout vider pour de bon ;
3. imprime en A4 et extrait le texte du PDF (pdftotext) : aucun repère, aucune sortie attendue,
   aucun coup de pouce, aucun retour et aucune correction ne doit s'y trouver, et les lignes
   des questions « ordre » doivent y être dans l'ordre mélangé de départ ;
4. après l'impression (afterprint), vérifie que les réponses (et l'ordre de l'élève) sont remises à l'écran ;
5. contrôle la mise en page A4 (style « Signal pirate », T123) : aucune requête hors du site (polices
   comprises), aucun texte imprimé sous 10 pt, aucune ligne de code coupée en deux (trop longue pour
   la page), rien qui déborde de la page, le bandeau et le pied présents, seules les polices du site
   dans le PDF (pdffonts), et tout ce que l'élève remplit (lignes, cases du code, cases à cocher,
   ronds, cadres) tracé d'un trait plein d'au moins 0,5 pt et de contraste 7:1 au moins ;
6. signale (« Attention », sans bloquer) une réponse à l'étroit : réponse modèle plus longue que sa place sur
   papier, à 2,5 mm par caractère écrit à la main (T123e) ;
7. signale (« Attention : mise en page », sans bloquer, T140) les défauts de page, lus dans le PDF : une question
   dont la consigne et la place pour répondre tombent sur deux pages, un titre (partie, exercice, encadré) orphelin
   en bas de page, une page (sauf la dernière) avec plus d'un tiers de blanc en bas, une dernière page remplie à
   moins d'un tiers. Une ligne de code trop longue pour sa colonne (elle passerait à la ligne) est une erreur (5).
Il dit le nombre de pages (4 au plus pour un TD).
"""
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

from playwright.sync_api import sync_playwright

REPERE = 'ZQXREPONSE'
# noms des polices du site tels que pdffonts les écrit
POLICES_DU_SITE = {'AtkinsonHyperlegible-Regular', 'AtkinsonHyperlegible-Bold', 'AtkinsonHyperlegible-Italic',
                   'JetBrainsMono-Regular', 'JetBrainsMono-Bold', 'JetBrainsMono-Italic', 'JetBrainsMono-BoldItalic',
                   'Anton-Regular', 'VT323-Regular', 'TDSymboles'}
# le bandeau : texte entier, rien de recouvert (le QR code, « Nom et prénom », les objectifs), hauteur en mm
BANDEAU_JS = r"""() => {
  const bd = document.querySelector('.td-bandeau'); if (!bd) return { bandeau_h: 0, bandeau_pb: [], bandeau_av: [] };
  const pb = [], av = [], r = e => e.getBoundingClientRect(), mm = px => Math.round(px * 25.4 / 96 * 10) / 10;
  const croise = (a, b) => a.left < b.right - .5 && b.left < a.right - .5 && a.top < b.bottom - .5 && b.top < a.bottom - .5;
  const textes = [...bd.querySelectorAll('.td-sur-titre, h1, .td-accroche')];
  const qr = bd.querySelector('.td-qr'), rb = r(bd);
  textes.forEach(e => {
    const nom = e.className || e.tagName.toLowerCase();
    if (e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible') pb.push(nom + ' : texte coupé');
    if (qr && croise(r(e), r(qr))) pb.push(nom + ' : recouvre le QR code');
    if (r(e).bottom > rb.bottom + .5 || r(e).right > rb.right + .5) pb.push(nom + ' : sort du bandeau');
    [...e.children].forEach(c => { if (r(c).right > r(e).right + 1) pb.push(nom + ' : un mot dépasse'); });
    // l'étendue réelle du texte (un mot insécable peut sortir de la boîte de son élément) : T123c
    const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      if (!n.nodeValue.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      [...rg.getClientRects()].forEach(t => { if (t.width < .5) return;
        if (t.right > rb.right + .5) pb.push(nom + ' : un mot sort du bandeau');
        if (qr && croise(t, r(qr))) pb.push(nom + ' : un mot touche le QR code');
        const mg = bd.querySelector('.td-margouillat');
        const pe = r(n.parentElement.closest('h1, p, .td-sur-titre > *, .td-accroche') || n.parentElement);
        const tb = { left: t.left, right: t.right, top: Math.max(t.top, pe.top), bottom: Math.min(t.bottom, pe.bottom) };
        if (mg && mg.getClientRects().length && croise(tb, r(mg))) av.push(nom + ' : touche le margouillat (charte/reattribuer-bandeaux.py le déplacera)'); });
    }
  });
  document.querySelectorAll('.td-nom, .td-objectifs').forEach(e => { if (e.getClientRects().length && r(e).top < rb.bottom - .5) pb.push((e.className) + ' : recouvert par le bandeau'); });
  return { bandeau_h: mm(rb.height), bandeau_attendu: bd.classList.contains('td-controle') ? 20 : 28, bandeau_pb: [...new Set(pb)], bandeau_av: [...new Set(av)] };
}"""
# mesures faites en média « print », à la largeur d'une page A4 (794 px)
MESURES = r"""() => { const BANDEAU = (BANDEAU_SRC);
  const pt = px => Math.round(px * 72 / 96 * 10) / 10, vus = el => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
  const petit = [], coupees = [], deborde = [];
  document.querySelectorAll('.td *').forEach(el => {
    if (!vus(el)) return;
    const direct = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    // dans un SVG, la taille est en unités du dessin : on la multiplie par l'échelle réelle (viewBox, largeur)
    let echelle = 1;
    if (el instanceof SVGElement && el.getScreenCTM) { const m = el.getScreenCTM(); if (m) echelle = Math.hypot(m.a, m.b); }
    if (direct) { const t = parseFloat(getComputedStyle(el).fontSize) * echelle; if (t < 13.3) petit.push((el.className.baseVal !== undefined ? el.tagName : el.className) + ' ' + el.textContent.trim().slice(0, 20) + ' (' + pt(t) + ' pt)'); }
    const r = el.getBoundingClientRect();
    if (r.width && (r.right > 794.5 || r.left < -0.5)) deborde.push(el.tagName + '.' + el.className);
  });
  // seul le code doit tenir sur sa ligne ; une console ou un message d'erreur passe à la ligne
  document.querySelectorAll('.td pre.td-code .td-l').forEach(l => {
    if (!vus(l)) return;
    const h = parseFloat(getComputedStyle(l).lineHeight) || 20;
    if (l.getBoundingClientRect().height > h * 1.5) coupees.push(l.textContent.replace(/^[0-9]+/, '').trim().slice(0, 40));
  });
  // tout ce que l'élève remplit : un trait d'au moins 0,5 pt (0,67 px) et de contraste 7:1 au moins sur le papier blanc
  const lum = c => { const v = (c.match(/[\d.]+/g) || [255, 255, 255]).slice(0, 3).map(x => { x = x / 255; return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; });
    return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
  const opaque = c => !/rgba\([^)]*,\s*0(\.0+)?\)/.test(c) && c !== 'transparent';
  const rapport = c => 1.05 / (lum(c) + .05);
  const saisies = [], faibles = [];
  document.querySelectorAll('.td input:not([type=hidden]), .td textarea:not(.td-ed-texte), .td-editeur, .td-nom span, .td td.td-vide').forEach(el => {
    if (!vus(el) && !el.classList.contains('td-editeur')) return;
    if (!el.getClientRects().length) return;
    const cs = getComputedStyle(el), traits = [];
    for (const cote of ['Top', 'Right', 'Bottom', 'Left']) {
      const w = parseFloat(cs['border' + cote + 'Width']), st = cs['border' + cote + 'Style'], c = cs['border' + cote + 'Color'];
      if (w > 0 && st !== 'none' && st !== 'hidden' && opaque(c)) traits.push({ w, st, c });
    }
    // lignes d'écriture dessinées en fond (dégradé répété) : leur couleur et leur épaisseur
    const fond = cs.backgroundImage;
    if (fond && fond.includes('gradient')) {
      const cols = (fond.match(/rgba?\([^)]*\)/g) || []).filter(opaque);
      cols.forEach(c => traits.push({ w: 1.2, st: 'solid', c }));
    }
    const nom = (el.className || el.type || el.tagName) + '';
    saisies.push(nom);
    const bons = traits.filter(t => t.w >= 0.66 && t.st !== 'dotted' && rapport(t.c) >= 7);
    const mauvais = traits.filter(t => !(t.w >= 0.66 && t.st !== 'dotted' && rapport(t.c) >= 7));
    if (!bons.length || mauvais.length) faibles.push(nom + ' : ' + (traits.map(t => t.w.toFixed(2) + 'px ' + t.st + ' ' + t.c + ' (' + rapport(t.c).toFixed(1) + ':1)').join(' / ') || 'aucun trait'));
  });
  return { petit, coupees, deborde, saisies: saisies.length, faibles, bandeau: !!document.querySelector('.td-bandeau'), pied: !!document.querySelector('.td-pied .td-ia'), ...BANDEAU() };
}"""


def encre_sous_le_haut(pdf, k):
    """Une page sans texte peut porter des lignes à remplir : y a-t-il de l'encre plus bas que 25 mm sous le haut
    de la page, au-dessus du pied de la page A4 (12 mm) ? (image en niveaux de gris, 30 points par pouce)"""
    img = subprocess.run(['pdftoppm', '-r', '30', '-gray', '-f', str(k), '-l', str(k), pdf], capture_output=True).stdout
    entete, _, donnees = img.partition(b'\n255\n')
    larg, haut = (int(x) for x in entete.split()[1:3])
    mm = 30 / 25.4
    for y in range(int(25 * mm), haut - int(13 * mm)):
        if min(donnees[y * larg:(y + 1) * larg]) < 160:
            return True
    return False


def normal(t):
    return ' '.join(t.split())


def reunir(urls):
    """Une seule page HTML pour plusieurs feuilles : la première, puis le <main> des suivantes (classe td-suite)."""
    textes = [urllib.request.urlopen(u).read().decode('utf-8') for u in urls]
    mains = []
    for u, t in zip(urls[1:], textes[1:]):
        m = re.search(r'<main\b[^>]*>.*?</main>', t, re.S)
        if not m:
            sys.exit(f'{u} : pas de <main>')
        mains.append(m.group(0))
    def classe(main, ajout):
        return re.sub(r'<main\b([^>]*)class="([^"]*)"', lambda x: f'<main{x.group(1)}class="{x.group(2)} {ajout}"', main, count=1)
    premier = textes[0]
    pm = re.search(r'<main\b[^>]*>', premier)
    premier = premier[:pm.start()] + classe(pm.group(0), 'td-suite-avant') + premier[pm.end():]
    suites = [classe(x, 'td-suite' + (' td-suite-avant' if i < len(mains) - 1 else '')) for i, x in enumerate(mains)]
    fin = premier.rindex('</body>')
    return premier[:fin] + '\n'.join(suites) + '\n' + premier[fin:]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dossier = sys.argv[sys.argv.index('--polices') + 1] if '--polices' in sys.argv else None
    if dossier in args:
        args.remove(dossier)
    if len(args) < 2 or not args[-1].endswith('.pdf'):
        sys.exit(__doc__)
    urls, sortie = args[:-1], args[-1]
    total = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        if len(urls) == 1:
            erreurs, pages, maxi = controler(b, urls[0], sortie)
            if pages > maxi:
                erreurs.append(f'{pages} pages : cette feuille tient sur {maxi} pages au plus (data-pages-max)')
                print('  -', erreurs[-1])
            total = erreurs
        else:
            dossier_tmp = tempfile.mkdtemp(prefix='imprimer-td-', dir=os.path.dirname(os.path.abspath(sortie)))
            for k, u in enumerate(urls):
                print(f'feuille {k + 1} : {u}')
                erreurs, pages, maxi = controler(b, u, os.path.join(dossier_tmp, f'feuille-{k + 1}.pdf'), analyser=False)
                if pages > maxi:
                    erreurs.append(f'feuille {k + 1} : {pages} pages, {maxi} au plus (data-pages-max)')
                    print('  -', erreurs[-1])
                total += erreurs
            for f in os.listdir(dossier_tmp):
                os.remove(os.path.join(dossier_tmp, f))
            os.rmdir(dossier_tmp)
            print(f'PDF réuni, d\'un seul tenant : {sortie}')
            erreurs, pages, maxi = controler(b, urls[0], sortie, html=reunir(urls))
            total += erreurs
        b.close()
    print('PDF vierge : ' + ('oui' if not total else f'NON ({len(total)} problème(s), voir les lignes « - » ci-dessus)'))
    sys.exit(1 if total else 0)

# T123e : les réponses à l'étroit sur papier. Pour chaque « courte » et chaque « libre » à data-lignes="1" imprimées :
# la place pour écrire (case d'un tableau de questions, moins l'étiquette si elle est sur la ligne ; rangée ; ligne
# pleine) et la réponse modèle (variante acceptée la plus longue ; pour une « libre », sa jumelle d'écran ou sa
# correction), à 2,5 mm par caractère écrit à la main. Le moteur règle les tableaux et les rangées ; une ligne
# pleine trop courte se règle dans la page (data-lignes="2" sur une « libre »).
ETROIT = r"""async () => {
  const doc = new DOMParser().parseFromString(await (await fetch(location.href)).text(), 'text/html');
  const mm = px => Math.round(px * 25.4 / 96 * 10) / 10, norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const vis = e => !!(e && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
  const longue = s => (s || '').split('|').map(x => x.trim()).reduce((a, b) => b.length > a.length ? b : a, '');
  function modele(so) {
    if (!so) return '';
    if (so.dataset.type === 'courte') return longue(so.dataset.reponse);
    let p = so.previousElementSibling;
    while (p && !p.matches('.td-q[data-support="ecran"]')) { if (p.matches('.td-q')) { p = null; break; } p = p.previousElementSibling; }
    if (p) {
      if (p.dataset.type === 'courte') return longue(p.dataset.reponse);
      const j = [...p.querySelectorAll('.td-options > li[data-juste]')];
      if (j.length) return j.map(x => norm(x.textContent)).join(' ; ');
      if (p.querySelector('.td-correction')) return norm(p.querySelector('.td-correction').textContent);
    }
    const c = so.querySelector('.td-correction, .td-attendu'); return c ? norm(c.textContent) : '';
  }
  const out = [], membres = new Set();
  document.querySelectorAll('table.td-groupe').forEach(tab => {
    const qs = []; let n = tab.closest('.td-groupe-boite').nextElementSibling;
    while (n) { if (n.matches('.td-q.td-groupe-membre')) qs.push(n); else if (n.matches('.td-q[data-support="ecran"], script, template') || (!vis(n) && !n.matches('.td-q'))) { } else break; n = n.nextElementSibling; }
    const cases = [...tab.querySelectorAll('tbody td.td-groupe-r')];
    const nums = [...tab.querySelectorAll('tbody th.td-groupe-n .td-q-num')].map(e => +norm(e.textContent));
    const ordre = nums.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
    qs.forEach((s, k) => {
      membres.add(s); const r = cases[ordre[k]]; if (!r) return;
      const cs = getComputedStyle(r), rb = r.getBoundingClientRect();
      let place = rb.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - parseFloat(cs.borderLeftWidth) - parseFloat(cs.borderRightWidth);
      const et = r.querySelector('.td-groupe-etiq');
      if (et) { const rg = document.createRange(); rg.selectNodeContents(et); const rs = [...rg.getClientRects()], der = rs[rs.length - 1];
        const l = r.querySelector('.td-groupe-ligne'), bas = l ? l.getBoundingClientRect().bottom : rb.bottom - parseFloat(cs.paddingBottom);
        if (bas - der.bottom < 6 * 96 / 25.4 - 0.5) place -= der.width + 96 / 25.4; }
      out.push({ id: s.id, num: nums[ordre[k]], ou: 'tableau', place: mm(place), modele: modele(doc.getElementById(s.id)) });
    });
  });
  document.querySelectorAll('.td-q[data-type="courte"], .td-q[data-type="libre"][data-lignes="1"]').forEach(s => {
    if (membres.has(s) || !vis(s)) return;
    const ch = s.querySelector(s.dataset.type === 'courte' ? 'input.td-champ' : 'textarea.td-libre'); if (!vis(ch)) return;
    const t = s.querySelector('.td-num-papier') || s.querySelector('.td-q-num');
    // une « courte » à plusieurs lignes d'écriture (T140) : la place est la longueur de toutes ses lignes
    const nl = +(ch.dataset.lignesPapier || 1);
    out.push({ id: s.id, num: norm(t ? t.textContent : ''), ou: s.closest('.td-grille-reponses') ? 'case de grille' : s.classList.contains('td-courte-ligne') ? 'rangée' : (nl > 1 ? nl + ' lignes' : 'ligne pleine'), place: mm(ch.getBoundingClientRect().width * nl), modele: modele(doc.getElementById(s.id)) });
  });
  return out.filter(x => x.modele.length * 2.5 > x.place);
}"""

# T140 : les défauts de page, vus dans le PDF lui-même. Des repères invisibles (texte blanc, en position absolue :
# ils ne déplacent rien) sont posés en haut de chaque consigne, de chaque zone de réponse, de chaque titre et de ce qui
# le suit ; un second PDF, identique au premier, dit sur quelle page tombe chacun (pdftotext -bbox).
REPERES_POSER = r"""() => {
  const vis = e => !!(e && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden' && e.getBoundingClientRect().height > 1);
  const st = document.createElement('style'); st.id = 'td-mep-style';
  st.textContent = '[data-td-mep]::after { content: attr(data-td-mep) !important; position: absolute !important; left: 0 !important; top: 0 !important; '
    + 'font: 10pt/1 monospace !important; color: #fff !important; white-space: nowrap !important; background: none !important; border: 0 !important; '
    + 'margin: 0 !important; padding: 0 !important; width: auto !important; height: auto !important; display: inline !important; }';
  document.head.appendChild(st);
  let k = 0; const liste = [];
  const libre = e => getComputedStyle(e, '::after').content === 'none';
  const poser = (e, quoi) => { if (!vis(e) || !libre(e)) return null; const code = 'QXM' + (k++) + 'Q';
    if (getComputedStyle(e).position === 'static') { e.setAttribute('data-td-mep-pos', ''); e.style.position = 'relative'; }
    e.setAttribute('data-td-mep', code); liste.push({ code, quoi }); return code; };
  const qs = [...document.querySelectorAll('.td-q[data-type]')].filter(s => vis(s) && !s.classList.contains('td-groupe-membre'));
  const out = { questions: [], titres: [], liste };
  qs.forEach(s => {
    const n = s.querySelector('.td-num-papier') || s.querySelector('.td-q-num');
    const num = n ? n.textContent.replace(/\s+/g, ' ').trim() : s.id;
    const c = s.querySelector(':scope > .td-consigne') || s.querySelector('.td-q-titre');
    let r = s.querySelector(':scope > .td-reponse');
    if (r && !vis(r)) r = s.querySelector(':scope > pre.td-code-trous, :scope > .td-ordre, :scope > .td-erreur-bloc');
    if (!c || !r || !vis(r)) return;
    const a = poser(c, 'consigne'), b = poser(r, 'réponse');
    if (a && b) out.questions.push({ num, a, b });
  });
  document.querySelectorAll('.td h2.td-partie, .td h3.td-exercice-titre, .td .td-encadre-titre').forEach(h => {
    let x = h.nextElementSibling; while (x && !vis(x)) x = x.nextElementSibling;
    if (!x && h.parentElement.matches('.td-exercice')) { x = h.parentElement.nextElementSibling; while (x && !vis(x)) x = x.nextElementSibling; }
    if (!x) return;
    // ce qui suit : sa consigne, s'il s'agit d'une question (le titre de la question, flottant, n'a pas de hauteur propre)
    const cible = x.matches('.td-q') ? (x.querySelector(':scope > .td-consigne') || x) : x;
    const a = poser(h, 'titre'), b = poser(cible, 'suite');
    if (a && b) out.titres.push({ titre: h.textContent.replace(/\s+/g, ' ').trim().slice(0, 50), a, b });
  });
  // les sauts de page voulus (data-saut, data-nouvelle-page) : la page d'avant peut finir tôt
  out.sauts = [];
  document.querySelectorAll('.td [data-saut="avant"], .td.td-suite[data-nouvelle-page] .td-entete').forEach(e => { const c = e.getAttribute('data-td-mep') || poser(e, 'saut'); if (c) out.sauts.push(c); });
  return out;
}"""
REPERES_RETIRER = r"""() => { document.querySelectorAll('[data-td-mep]').forEach(e => e.removeAttribute('data-td-mep'));
  document.querySelectorAll('[data-td-mep-pos]').forEach(e => { e.style.removeProperty('position'); e.removeAttribute('data-td-mep-pos'); });
  const st = document.getElementById('td-mep-style'); if (st) st.remove(); }"""


def pages_des_reperes(pdf):
    """{code: page} des repères dans un PDF (pdftotext -bbox)."""
    x = subprocess.run(['pdftotext', '-bbox', pdf, '-'], capture_output=True, text=True).stdout
    out, page = {}, 0
    for ligne in x.splitlines():
        if '<page ' in ligne:
            page += 1
        for m in re.finditer(r'>(QXM\d+Q)<', ligne):
            out.setdefault(m.group(1), page)
    return out


def remplissage(pdf, pages):
    """Pour chaque page : la part de la hauteur utile qui porte de l'encre (du haut à la dernière encre), en %."""
    out = []
    for k in range(1, pages + 1):
        img = subprocess.run(['pdftoppm', '-r', '40', '-gray', '-f', str(k), '-l', str(k), pdf], capture_output=True).stdout
        entete, _, donnees = img.partition(b'\n255\n')
        larg, haut = (int(v) for v in entete.split()[1:3])
        mm = 40 / 25.4
        haut_utile, bas_utile = int(5 * mm), haut - int(13 * mm)       # marges de la page (le pied A4 exclu)
        der = haut_utile
        for y in range(haut_utile, bas_utile):
            if min(donnees[y * larg:(y + 1) * larg]) < 200:
                der = y
        out.append(round(100 * (der - haut_utile) / (bas_utile - haut_utile)))
    return out


def defauts_de_page(p, sortie, pages):
    """Les défauts de page (T140), en « Attention » : question coupée de sa réponse, titre orphelin, page presque
    vide, grand blanc en bas d'une page. Le PDF de repères est fait à côté, puis effacé."""
    att = []
    info = p.evaluate(REPERES_POSER)
    tmp = sortie[:-4] + '.reperes.pdf'
    try:
        p.pdf(path=tmp, format='A4', print_background=True, prefer_css_page_size=True)
        pg = pages_des_reperes(tmp)
    finally:
        p.evaluate(REPERES_RETIRER)
        if os.path.exists(tmp):
            os.remove(tmp)
    for q in info['questions']:
        a, b = pg.get(q['a']), pg.get(q['b'])
        if a and b and b != a:
            att.append(f"{q['num']} : la consigne (page {a}) et la place pour répondre (page {b}) sont séparées "
                       "(côte à côte, data-ensemble, ou un saut de page voulu)")
    for t in info['titres']:
        a, b = pg.get(t['a']), pg.get(t['b'])
        if a and b and b != a:
            att.append(f"titre orphelin en bas de la page {a} : « {t['titre']} » (ce qui le suit est page {b})")
    if pages > 1:
        r = remplissage(sortie, pages)
        voulues = {pg.get(c) for c in info.get('sauts', [])}
        for k, x in enumerate(r[:-1], 1):
            if x < 67 and (k + 1) not in voulues:
                att.append(f'page {k} : {100 - x} % de blanc en bas (un bloc poussé à la page suivante ?)')
        if r[-1] < 34:
            att.append(f'page {pages} (la dernière) : remplie à {r[-1]} % seulement (moins d\'un tiers)')
    return att


def controler(b, url, sortie, html=None, analyser=True):
    """Contrôle une page (ou les feuilles réunies, html) et écrit son PDF. Renvoie (erreurs, pages, pages au plus)."""
    erreurs = []
    if True:
        ctx = b.new_context(viewport={'width': 1440, 'height': 900})
        if html is not None:
            ctx.route(url, lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=html))
        externes = []
        p = ctx.new_page()
        p.on('request', lambda r: externes.append(r.url) if not r.url.startswith(('http://localhost', 'http://127.0.0.1', 'file:', 'data:')) else None)
        p.goto(url)
        p.wait_for_selector('.td-barre')
        p.evaluate('document.fonts.ready')
        ecran = p.evaluate(BANDEAU_JS)
        for x in ecran['bandeau_pb']:
            erreurs.append('bandeau, à l\'écran : ' + x)
        for x in ecran['bandeau_av']:
            print('  Attention : bandeau, à l\'écran : ' + x)
        # (le code de départ d'un éditeur n'est pas une réponse)
        pleins = p.evaluate("[...document.querySelectorAll('.td input, .td textarea:not(.td-ed-texte)')].filter(c => c.type === 'radio' || c.type === 'checkbox' ? c.checked : c.value).length")
        if pleins:
            erreurs.append(f'{pleins} champ(s) déjà rempli(s) à l\'ouverture')
        # des repères partout, pour prouver que l'impression vide vraiment
        n = p.evaluate("""r => { let n = 0;
            document.querySelectorAll('.td input, .td textarea').forEach(c => {
              if (c.type === 'radio' || c.type === 'checkbox') c.checked = true; else { c.value = r + (n++); }
            }); return n; }""", REPERE)
        # les questions « ordre » : l'état n'est pas un champ. On les résout par de vrais clics
        # (flèches ▲ ▼), dans l'ordre de la solution lu dans la source de la page.
        solutions = p.evaluate("""async () => {
            const doc = new DOMParser().parseFromString(await (await fetch(location.href)).text(), 'text/html');
            const sol = {};
            doc.querySelectorAll('.td-q[data-type="ordre"]').forEach(s => {
              sol[s.id] = [...s.querySelectorAll('.td-lignes > li')].map(li => li.textContent.trim());
              if (s.closest('[data-support="ecran"]')) sol[s.id].ecran = true; });
            return Object.fromEntries(Object.entries(sol).map(([k, v]) => [k, { lignes: v, ecran: !!v.ecran }])); }""")
        ordres = {}
        lire = lambda qid: [t.strip() for t in p.locator(f'#{qid} .td-ordre-code').all_inner_texts()]
        if html is not None:
            solutions = {}          # feuilles réunies : les « ordre » ont été contrôlées feuille par feuille (identifiants en double)
        ecran_seul = {qid for qid, x in solutions.items() if x['ecran']}
        solutions = {qid: x['lignes'] for qid, x in solutions.items()}
        for qid, sol in solutions.items():
            depart = lire(qid)
            for cible, ligne in enumerate(sol):
                pos = next(i for i, t in enumerate(lire(qid)) if t == ligne and i >= cible)
                while pos > cible:
                    p.locator(f'#{qid} .td-ordre-ligne').nth(pos).locator('button').first.click()
                    pos -= 1
            if lire(qid) != sol:
                erreurs.append(f'{qid} : les lignes n\'ont pas pu être remises dans l\'ordre de la solution')
            num = p.locator(f'#{qid} .td-q-num').evaluate("e => (e.querySelector('.td-num-papier') || e).textContent").strip()
            ordres[qid] = (num, depart, sol)
        # textes qui ne doivent jamais être imprimés : lus dans la SOURCE de la page (T123c), ligne par ligne. Après le
        # montage, le moteur colle « Correction », « Coup de pouce 1 : » ou les numéros de ligne au texte, qu'on ne
        # retrouverait plus dans le PDF.
        caches = p.evaluate("""async () => {
            const doc = new DOMParser().parseFromString(await (await fetch(location.href)).text(), 'text/html');
            const out = [];
            doc.querySelectorAll('.td-aide, .td-correction, .td-retour, pre.td-attendu').forEach(e => {
              e.textContent.split('\\n').map(l => l.replace(/\\s+/g, ' ').trim()).filter(l => l.length >= 16).forEach(l => out.push(l.slice(0, 40))); });
            return [...new Set(out)]; }""")
        # ces textes et leurs copies (retours, explications) : ce qui reste visible sur papier sans eux est le texte « permis »
        p.evaluate("""() => document.querySelectorAll('.td-aide, .td-correction, .td-retour, pre.td-attendu, .td-retour-zone, .td-explication')
            .forEach(e => e.setAttribute('data-imprimer-td-cache', ''))""")
        p.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        restes = p.evaluate("[...document.querySelectorAll('.td input, .td textarea')].filter(c => c.type === 'radio' || c.type === 'checkbox' ? c.checked : c.value).length")
        if restes:
            erreurs.append(f'{restes} champ(s) non vidé(s) à l\'impression')
        p.emulate_media(media='print')
        # mise en page A4 : la largeur de la page (210 mm, marges latérales dans la page)
        p.set_viewport_size({'width': 794, 'height': 1123})
        p.evaluate('document.fonts.ready')
        mesures = p.evaluate(MESURES.replace('(BANDEAU_SRC)', BANDEAU_JS))
        # (feuilles réunies : chaque feuille a été mesurée seule)
        etroit = p.evaluate(ETROIT) if html is None else []
        for x in etroit:
            print(f"  Attention : réponse à l'étroit, {x['id']} ({x['num']}, {x['ou']}) : réponse modèle de {len(x['modele'])} caractères, "
                  f"environ {len(x['modele']) * 2.5:.0f} mm à la main, pour {x['place']} mm"
                  + (' : data-lignes="2"' if x['ou'] == 'ligne pleine' else ' : data-lignes plus grand' if x['ou'].endswith('lignes')
                     else ' : moins de colonnes dans la grille (data-colonnes), ou une variante acceptée plus courte' if x['ou'] == 'case de grille'
                     else ' : à signaler au Designer (le moteur doit la régler)'))
        # un texte caché rendu sur papier (une règle d'impression qui l'affiche) : la fuite elle-même, sans lire le PDF
        rendus = p.evaluate("""() => [...document.querySelectorAll('.td-aide, .td-correction, .td-retour, pre.td-attendu, .td-retour-zone, .td-explication')]
            .filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden' && e.textContent.trim())
            .map(e => (e.className || e.tagName) + ' « ' + e.textContent.replace(/\\s+/g, ' ').trim().slice(0, 30) + ' »')""")
        # le texte imprimé hors des textes cachés (pour ne pas confondre une consigne qui cite la sortie attendue)
        permis = p.evaluate("""() => { const st = document.createElement('style');
            st.textContent = '[data-imprimer-td-cache]:not(#z1):not(#z2):not(#z3) { display: none !important; }'; document.head.appendChild(st);
            const t = [...document.querySelectorAll('[data-td]')].map(m => m.innerText).join(' '); st.remove(); return t; }""")
        pied_txt = p.evaluate("[...document.querySelectorAll('.td-pied')].map(e => e.innerText).join(' ')")
        noms = p.evaluate("(document.querySelector('[data-td]').getAttribute('data-auteurs') || 'Babash - NSI Tani Malandi')")
        maxi = p.evaluate("Math.max(...[...document.querySelectorAll('[data-td]')].map(m => +m.getAttribute('data-pages-max') || 4))")
        nb_feuilles = p.evaluate("document.querySelectorAll('[data-td]').length")
        p.pdf(path=sortie, format='A4', print_background=True, prefer_css_page_size=True)
        nb_pages = int(next(l for l in subprocess.run(['pdfinfo', sortie], capture_output=True, text=True).stdout.splitlines()
                            if l.startswith('Pages:')).split()[1])
        mep = defauts_de_page(p, sortie, nb_pages) if analyser else []
        for x in mep:
            print('  Attention : mise en page, ' + x)
        p.set_viewport_size({'width': 1440, 'height': 900})
        p.emulate_media(media='screen')
        p.evaluate("window.dispatchEvent(new Event('afterprint'))")
        remis = p.evaluate("r => [...document.querySelectorAll('.td input, .td textarea')].filter(c => (c.value || '').startsWith(r)).length", REPERE)
        if remis != n:
            erreurs.append(f'après l\'impression, {remis} réponse(s) remise(s) sur {n}')
        for qid, (num, depart, sol) in ordres.items():
            if lire(qid) != sol:
                erreurs.append(f'{qid} : après l\'impression, l\'ordre de l\'élève n\'est pas revenu à l\'écran')
        ctx.close()
    if externes:
        erreurs.append('requête hors du site : ' + ', '.join(sorted(set(externes))[:3]))
    if mesures['petit']:
        erreurs.append(f"texte sous 10 pt : {mesures['petit'][:4]}")
    if mesures['coupees']:
        erreurs.append(f"ligne(s) de code trop longue(s) pour la page : {mesures['coupees'][:4]}")
    if mesures['deborde']:
        erreurs.append(f"débordement hors de la page : {mesures['deborde'][:4]}")
    if mesures['faibles']:
        erreurs.append(f"élément à remplir peu visible sur papier (il faut un trait plein de 0,5 pt et 7:1) : {mesures['faibles'][:4]}")
    for x in mesures['bandeau_pb']:
        erreurs.append('bandeau, sur papier : ' + x)
    for x in mesures['bandeau_av']:
        print('  Attention : bandeau, sur papier : ' + x)
    if mesures['bandeau_h'] > mesures['bandeau_attendu'] + .3:
        print(f"  Attention : bandeau de {mesures['bandeau_h']} mm au lieu de {mesures['bandeau_attendu']} : un texte du bandeau est trop long (titre, accroche ou chapitre ; voir LISEZMOI)")
    for nom in ('bandeau', 'pied'):
        if not mesures[nom]:
            erreurs.append(f'{nom} absent')
    polices_pdf = [l.split()[0] for l in subprocess.run(['pdffonts', sortie], capture_output=True, text=True).stdout.splitlines()[2:]]
    autres = sorted({f.split('+')[-1] for f in polices_pdf} - POLICES_DU_SITE)
    if autres:
        erreurs.append('police de remplacement dans le PDF : ' + ', '.join(autres))
    texte = subprocess.run(['pdftotext', '-layout', sortie, '-'], capture_output=True, text=True, check=True).stdout
    plat = normal(texte)
    if REPERE in texte:
        erreurs.append('une réponse tapée figure dans le PDF')
    plat_permis = normal(permis)
    if rendus:
        erreurs.append(f'{len(rendus)} correction(s), coup(s) de pouce ou retour(s) imprimé(s) : {rendus[:3]}')
    fuites = []
    for c in caches:
        debut = normal(c)
        # imprimé plus souvent que dans les textes visibles (une consigne peut citer la sortie attendue)
        if debut and plat.count(debut) > plat_permis.count(debut):
            fuites.append(debut)
    if fuites:
        erreurs.append(f'texte caché imprimé ({len(fuites)} ligne(s)) : ' + ' | '.join(fuites[:3]))
    # dans le PDF, les lignes de chaque question « ordre » sont dans l'ordre mélangé de départ
    for qid, (num, depart, sol) in ordres.items():
        if qid in ecran_seul:
            continue                  # data-support="ecran" : la question n'est pas imprimée
        debut = plat.find(num + ' ')
        suite = plat[debut:] if debut >= 0 else plat
        fin = suite.find('Question', len(num) + 1)
        bloc = suite[:fin] if fin > 0 else suite
        places = [bloc.find(normal(l)) for l in depart]
        if -1 in places:
            erreurs.append(f'{qid} : lignes introuvables dans le PDF')
        elif places != sorted(places):
            erreurs.append(f'{qid} : les lignes ne sont pas imprimées dans l\'ordre de départ')
        elif depart != sol:
            print(f'{qid} : imprimée dans l\'ordre de départ ({" / ".join(depart)}), pas dans celui de l\'élève')
    pages = int(next(l for l in subprocess.run(['pdfinfo', sortie], capture_output=True, text=True).stdout.splitlines()
                     if l.startswith('Pages:')).split()[1])
    # aucune page ne porte que le pied (le pied de la page A4 et celui du TD) : T123c
    pied_plat = normal(pied_txt)
    for k in range(1, pages + 1):
        tk = normal(subprocess.run(['pdftotext', '-f', str(k), '-l', str(k), sortie, '-'], capture_output=True, text=True).stdout)
        tk = re.sub(re.escape(normal(noms)) + r" ?· ?CC BY-SA 4\.0 ?· ?conçu avec l'aide de l'IA ?· ?\d+ / \d+$", '', tk).strip()
        sans = lambda x: re.sub(r'[\s-]', '', x)        # l'adresse passe à la ligne (« nsi- premiere »)
        if (not tk or (pied_plat and sans(tk) in sans(pied_plat))) and not encre_sous_le_haut(sortie, k):
            erreurs.append(f'page {k} : elle ne porte que le pied de page')
    print(f'{sortie} : {pages} page(s) A4 ; {n} champ(s) remplis puis vidés ; {len(caches)} texte(s) caché(s) contrôlé(s) ; '
          f"{mesures['saisies']} élément(s) à remplir au trait net")
    for e in erreurs:
        print('  -', e)
    return erreurs, pages, maxi * nb_feuilles


if __name__ == '__main__':
    main()
