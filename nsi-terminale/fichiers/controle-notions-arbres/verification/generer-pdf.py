# Usage : depuis la racine du dépôt, python3 -m http.server 8765, puis python3 -I verification/<ce script> <dossier de sortie> [port]
# Échoue si une feuille déborde ou si un élément (code, question, figure) est plus large que son cadre.
import sys, asyncio
from playwright.async_api import async_playwright
PORT=sys.argv[2] if len(sys.argv)>2 else '8765'
B='http://localhost:'+PORT+'/nsi-terminale/fichiers/controle-notions-arbres/'
OUT=sys.argv[1]
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
    global probleme
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':703,'height':1041})
        msgs=[]; probleme=False
        pg.on('console', lambda m: msgs.append(m.text)); pg.on('pageerror', lambda e: msgs.append(str(e)))
        for nom in ['sujet','corrige']:
            # impression émulée AVANT le chargement : le corrigé se met en pages dans la vraie mise en page d'impression
            await pg.emulate_media(media='print')
            await pg.goto(B+nom+'.html'); await pg.wait_for_timeout(300)
            r=await pg.evaluate('''()=>[...document.querySelectorAll('.feuille')].map(f=>{const pied=f.querySelector('.pied-feuille').getBoundingClientRect().top; return {h:f.clientHeight, sh:f.scrollHeight, marges:[...f.querySelectorAll('.colonnes>div, .corr>div')].map(c=>Math.round(pied-Math.max(...[...c.children].map(x=>x.getBoundingClientRect().bottom))))}})''')
            print(nom, r)
            larges=await pg.evaluate(LARGES)
            print(nom, 'éléments plus larges que leur cadre :', larges or 'aucun')
            probleme = probleme or bool(larges) or any(x['sh']>x['h'] for x in r)
            await pg.pdf(path=f'{OUT}/{nom}.pdf', format='A4', print_background=True, prefer_css_page_size=True)
        print('console:', msgs)
        await b.close()
    sys.exit(1 if probleme or msgs else 0)
asyncio.run(main())
