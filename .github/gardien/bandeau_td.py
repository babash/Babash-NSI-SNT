#!/usr/bin/env python3
"""Géométrie du bandeau d'un TD en ligne (style « Signal pirate », T123) : rien de coupé, rien de recouvert.

Usage (le site servi en local, par exemple python3 -m http.server 8000 à la racine) :
  python3 -I .github/gardien/bandeau_td.py http://localhost:8000/nsi1/fichiers/boucles-td1/index.html [URL…]

Pour chaque page, à 16 largeurs d'écran (de 320 à 1920 px) et sur papier (A4, média « print »),
l'outil mesure les rectangles RÉELS du texte du bandeau (Range.getClientRects sur chaque nœud texte :
un mot insécable qui dépasse de la boîte de son élément compte) et signale :
  - le défilement horizontal de la page ;
  - un texte hors de la fenêtre ou hors du bandeau ;
  - un texte qui touche le QR code, le margouillat, « Nom et prénom » ou les objectifs ;
  - un élément du bandeau qui coupe son texte (débordement masqué) ;
  - une erreur JavaScript, une requête hors du site.
Il donne aussi la hauteur du bandeau (en px, en mm sur papier : 28 mm attendus, 20 mm pour un
contrôle) et la classe du titre posée par le moteur (td-titre-long, td-titre-tres-long).
L'étendue verticale d'un texte est bornée à la boîte de son bloc (titre, paragraphe, élément de la
ligne du niveau) : la boîte de texte d'Anton (1,5 em) dépasse sa ligne (1,02 em) sans que l'encre
des capitales ne sorte.

Complète charte/imprimer-td.py, qui mesure la boîte des éléments, à 1440 px et sur papier seulement :
un mot insécable plus large que la zone du titre (26 capitales larges, par exemple) y passe inaperçu.
Code de sortie : 0 rien à signaler ; 1 au moins une vue à examiner.
"""
import sys

from playwright.sync_api import sync_playwright

JS = r"""(papier) => {
  const pb = [], R = e => e.getBoundingClientRect();
  const croise = (a, b) => a.left < b.right - .5 && b.left < a.right - .5 && a.top < b.bottom - .5 && b.top < a.bottom - .5;
  const bd = document.querySelector('.td-bandeau'); if (!bd) return { pb: ['pas de bandeau'], h: 0, hdec: 0, classe: '', lignes: 0, fs: '' };
  const rb = R(bd), cw = document.documentElement.clientWidth, sw = document.documentElement.scrollWidth;
  if (sw > cw + .5) pb.push('défilement horizontal ' + sw + '/' + cw);
  const rects = [];
  const w = document.createTreeWalker(bd.querySelector('.td-bandeau-texte') || bd, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    const pe = R(n.parentElement.closest('h1, p, .td-sur-titre > *, .td-accroche') || n.parentElement);
    [...rg.getClientRects()].forEach(r0 => { if (r0.width > .5) {
      const r = { left: r0.left, right: r0.right, top: Math.max(r0.top, pe.top), bottom: Math.min(r0.bottom, pe.bottom) };
      rects.push({ r, nom: n.parentElement.tagName.toLowerCase() + '.' + n.parentElement.className + ' « ' + n.nodeValue.trim().slice(0, 20) + ' »' }); } });
  }
  const qr = bd.querySelector('.td-qr'), mg = bd.querySelector('.td-margouillat');
  const autres = [...document.querySelectorAll('.td-nom, .td-objectifs')].filter(e => e.getClientRects().length);
  rects.forEach(({ r, nom }) => {
    if (r.right > cw + .5 || r.left < -.5) pb.push(nom + ' : hors de la fenêtre');
    if (r.bottom > rb.bottom + .5 || r.right > rb.right + .5 || r.top < rb.top - .5) pb.push(nom + ' : hors du bandeau');
    if (qr && croise(r, R(qr))) pb.push(nom + ' : touche le QR code');
    if (mg && mg.getClientRects().length && croise(r, R(mg))) pb.push(nom + ' : touche le margouillat');
    autres.forEach(a => { if (croise(r, R(a))) pb.push(nom + ' : touche ' + a.className); });
  });
  bd.querySelectorAll('.td-bandeau-texte *').forEach(e => {
    const cs = getComputedStyle(e);
    if ((cs.overflowX !== 'visible' || cs.textOverflow !== 'clip') && e.scrollWidth > e.clientWidth + 1) pb.push(e.tagName + '.' + e.className + ' : texte coupé');
  });
  autres.forEach(a => { if (R(a).top < rb.bottom - .5) pb.push(a.className + ' : commence dans le bandeau'); });
  if (qr && R(qr).right > cw + .5) pb.push('QR code hors de la fenêtre');
  const h1 = bd.querySelector('h1'), dec = bd.querySelector('.td-bandeau-decor'), k = papier ? 25.4 / 96 : 1;
  return { pb: [...new Set(pb)], h: Math.round(rb.height * k * 10) / 10, hdec: dec ? Math.round(R(dec).height * k * 10) / 10 : 0,
           classe: h1 ? h1.className : '', lignes: h1 ? Math.round(R(h1).height / parseFloat(getComputedStyle(h1).lineHeight)) : 0,
           fs: h1 ? getComputedStyle(h1).fontSize : '' };
}"""

LARGEURS = (320, 360, 400, 480, 560, 640, 680, 681, 700, 768, 800, 900, 1024, 1280, 1440, 1920)


def main():
    urls = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not urls or '-h' in sys.argv or '--help' in sys.argv:
        print(__doc__.strip())
        sys.exit(0 if urls or '-h' in sys.argv or '--help' in sys.argv else 2)
    a_examiner = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for url in urls:
            print(url)
            for w in LARGEURS + ('A4',):
                papier = w == 'A4'
                ctx = b.new_context(viewport={'width': 794 if papier else w, 'height': 1123 if papier else 900})
                ext, js = [], []
                ctx.route('**/*', lambda r: (ext.append(r.request.url), r.abort())
                          if not r.request.url.startswith(('http://127.0.0.1', 'http://localhost', 'data:', 'blob:', 'about:'))
                          else r.continue_())
                p = ctx.new_page()
                p.on('pageerror', lambda e: js.append(str(e)[:100]))
                p.goto(url)
                p.wait_for_selector('.td-barre')
                p.evaluate('document.fonts.ready')
                if papier:
                    p.evaluate("window.dispatchEvent(new Event('beforeprint'))")
                    p.emulate_media(media='print')
                    p.evaluate('document.fonts.ready')
                r = p.evaluate(JS, papier)
                if js:
                    r['pb'].append('erreur JavaScript : ' + js[0])
                if ext:
                    r['pb'].append('requête hors du site : ' + ext[0])
                a_examiner += bool(r['pb'])
                print(f"  {str(w):>5} bandeau {r['h']}{' mm' if papier else ' px'} (dessin {r['hdec']}) ; titre {r['classe'] or 'normal'}, "
                      f"{r['fs']}, {r['lignes']} ligne(s) : " + ('ok' if not r['pb'] else 'À EXAMINER : ' + ' | '.join(r['pb'][:5])))
                ctx.close()
        b.close()
    print(f'Bilan : {a_examiner} vue(s) à examiner')
    sys.exit(1 if a_examiner else 0)


if __name__ == '__main__':
    main()
