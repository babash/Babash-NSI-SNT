"""Vérifie qu'aucune feuille A4 ne déborde (contenu masqué)."""
import asyncio, sys
from playwright.async_api import async_playwright
async def main(urls):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1200, 'height': 900})
        for u in urls:
            await pg.goto(u, wait_until='load'); await pg.wait_for_timeout(600)
            res = await pg.evaluate('''() => [...document.querySelectorAll('.sheet')].map((s,i) => {
                const body = s.querySelector('.sheet-body'); const r = s.getBoundingClientRect();
                let pire = 0, qui = '';
                s.querySelectorAll('.sheet-body *').forEach(e => { const b = e.getBoundingClientRect();
                  if (b.height && b.bottom - r.bottom > pire) { pire = b.bottom - r.bottom; qui = e.className || e.tagName; } });
                const filler = body ? body.querySelector(':scope > .filler') : null;
                return {page: i+1, debord_px: Math.round(pire), element: String(qui).slice(0,40),
                        marge_libre_px: body ? Math.round(body.getBoundingClientRect().bottom - [...body.children].reduce((m,c)=>Math.max(m,c.getBoundingClientRect().bottom),0)) : null,
                        filler_px: filler ? Math.round(filler.getBoundingClientRect().height) : null};
            })''')
            fonts = await pg.evaluate('() => [...document.fonts].filter(f=>f.status==="loaded").map(f=>f.family+" "+f.weight).filter((v,i,a)=>a.indexOf(v)===i).join(", ")')
            print(u.rsplit('/',1)[1]); [print('  ', x) for x in res]; print('   polices :', fonts)
        await b.close()
asyncio.run(main(sys.argv[1:]))
