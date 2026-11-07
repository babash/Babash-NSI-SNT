import asyncio, sys
from playwright.async_api import async_playwright
async def main(urls, page):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1200, 'height': 900})
        for u in urls:
            await pg.goto(u); await pg.wait_for_timeout(600)
            r = await pg.evaluate('''(n) => { const s=document.querySelectorAll('.sheet')[n]; const out=[];
              const walk=(el,d)=>{ for (const c of el.children){ const h=c.getBoundingClientRect().height; out.push('  '.repeat(d)+(c.className||c.tagName).toString().slice(0,30)+' '+h.toFixed(0)); if(d<1) walk(c,d+1);} };
              walk(s.querySelector('.sheet-body'),0); return out; }''', int(page))
            print(u.rsplit('/',1)[1]); print('\n'.join(r))
        await b.close()
asyncio.run(main(sys.argv[2:], sys.argv[1]))
