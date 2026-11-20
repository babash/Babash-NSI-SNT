# Usage : depuis la racine du dépôt, python3 -m http.server 8765, puis python3 -I verification/<ce script> <dossier de sortie>
import sys, asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/nsi-terminale/fichiers/controle-notions-arbres/'
OUT=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':703,'height':1041})
        msgs=[]
        pg.on('console', lambda m: msgs.append(m.text)); pg.on('pageerror', lambda e: msgs.append(str(e)))
        for nom in ['sujet','corrige']:
            # impression émulée AVANT le chargement : le corrigé se met en pages dans la vraie mise en page d'impression
            await pg.emulate_media(media='print')
            await pg.goto(B+nom+'.html'); await pg.wait_for_timeout(300)
            r=await pg.evaluate('''()=>[...document.querySelectorAll('.feuille')].map(f=>{const pied=f.querySelector('.pied-feuille').getBoundingClientRect().top; return {h:f.clientHeight, sh:f.scrollHeight, marges:[...f.querySelectorAll('.colonnes>div, .corr>div')].map(c=>Math.round(pied-Math.max(...[...c.children].map(x=>x.getBoundingClientRect().bottom))))}})''')
            print(nom, r)
            await pg.pdf(path=f'{OUT}/{nom}.pdf', format='A4', print_background=True, prefer_css_page_size=True)
        print('console:', msgs)
        await b.close()
asyncio.run(main())
