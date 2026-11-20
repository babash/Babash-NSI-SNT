"""Régénère sujet.pdf et corrige.pdf depuis sujet.html et corrige.html (Chromium).

Usage : depuis la racine du dépôt, python3 -m http.server 8765, puis
        python3 -I nsi-terminale/fichiers/controle-notions-poo/verification/generer-pdf.py [port]
L'impression est émulée AVANT le chargement : le corrigé se met en pages dans
la vraie mise en page d'impression (A4, marges de papier.css : 188 mm de large).
Signale toute feuille qui déborde.
Babash - NSI Tani Malandi · MIT
"""
import asyncio
import pathlib
import sys

from playwright.async_api import async_playwright

ICI = pathlib.Path(__file__).resolve().parent.parent
PORT = sys.argv[1] if len(sys.argv) > 1 else '8765'
B = 'http://localhost:' + PORT + '/nsi-terminale/fichiers/' + ICI.name + '/'

LARGES = '''() => [...document.querySelectorAll('.feuille')].map((f, n) => {
    const t = [];
    f.querySelectorAll('pre, .console, .contexte, .q, .r, .convention, .option, svg, table').forEach(e => {
        const cadre = e.parentElement.closest('.colonnes > div, .corr > div, .contexte, .feuille');
        const r = e.getBoundingClientRect(), c = cadre.getBoundingClientRect();
        if (r.right > c.right + 0.5 || r.left < c.left - 0.5 || (e.tagName === 'PRE' && e.scrollWidth > e.clientWidth + 1))
            t.push('page ' + (n + 1) + ' : ' + (e.className || e.tagName) + ' « ' + e.textContent.trim().slice(0, 40) + ' »');
    });
    return t;
}).flat()'''


async def main():
    probleme = False
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 711, 'height': 1050})
        msgs = []
        pg.on('console', lambda m: msgs.append(m.text))
        pg.on('pageerror', lambda e: msgs.append(str(e)))
        for nom in ['sujet', 'corrige']:
            await pg.emulate_media(media='print')
            await pg.goto(B + nom + '.html')
            await pg.wait_for_timeout(300)
            r = await pg.evaluate('''() => [...document.querySelectorAll('.feuille')].map(f => {
                const pied = f.querySelector('.pied-feuille').getBoundingClientRect().top;
                const bas = Math.max(...[...f.querySelectorAll('.q, .r, .contexte, .convention')].map(x => x.getBoundingClientRect().bottom));
                return { deborde: f.scrollHeight > f.clientHeight + 1 || bas > pied, reste_mm: Math.round((pied - bas) / 3.78) };
            })''')
            print(nom, len(r), 'pages', r)
            larges = await pg.evaluate(LARGES)
            print(nom, 'éléments plus larges que leur cadre :', larges or 'aucun')
            probleme = probleme or any(x['deborde'] for x in r) or bool(larges)
            await pg.pdf(path=str(ICI / (nom + '.pdf')), format='A4', print_background=True, prefer_css_page_size=True)
        print('console :', msgs or 'rien')
        await b.close()
    sys.exit(1 if probleme or msgs else 0)

asyncio.run(main())
