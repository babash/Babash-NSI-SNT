"""Vérifie la maquette : débordement (320, 768, 1440), requêtes externes, filtres, clavier, affichage."""
import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8762/'
PAGES=['index.html','accueil-b.html','nsi-terminale/','bibliotheque/','bibliotheque/fiche.html','bibliotheque/annales/']
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for w in (320,768,1440):
            for sch in ('light','dark'):
                ctx=await b.new_context(viewport={'width':w,'height':800},color_scheme=sch)
                pg=await ctx.new_page(); ext=[]; errs=[]
                pg.on('request', lambda r: ext.append(r.url) if not r.url.startswith(B) else None)
                pg.on('pageerror', lambda e: errs.append(str(e)))
                for u in PAGES:
                    await pg.goto(B+u, wait_until='networkidle')
                    sw=await pg.evaluate('document.documentElement.scrollWidth')
                    fonts=await pg.evaluate('Array.from(document.fonts).filter(f=>f.status=="loaded").map(f=>f.family).filter((v,i,a)=>a.indexOf(v)==i).join(",")')
                    if sw>w: print('DÉBORDEMENT',w,sch,u,sw)
                    if w==1440 and sch=='light': print(u,'polices :',fonts)
                if ext: print('EXTERNE',w,sch,ext[:3])
                if errs: print('ERREUR JS',w,sch,errs[:3])
                await ctx.close()
        ctx=await b.new_context(viewport={'width':1440,'height':900}); pg=await ctx.new_page()
        await pg.goto(B+'bibliotheque/',wait_until='networkidle')
        await pg.check('#f-ens-snt'); print('biblio SNT :', await pg.inner_text('.compte'))
        await pg.check('#f-type-td'); print('biblio SNT + TD :', await pg.inner_text('.compte'))
        await pg.uncheck('#f-ens-snt'); await pg.uncheck('#f-type-td')
        await pg.fill('#recherche','pile'); print('biblio « pile » :', await pg.inner_text('.compte'))
        await pg.goto(B+'bibliotheque/annales/',wait_until='networkidle')
        await pg.click('.puces-exercice .puce >> nth=0'); print('annales, clic chapitre :', await pg.inner_text('.compte'))
        await pg.goto(B+'nsi-terminale/',wait_until='networkidle')
        await pg.fill('#recherche','pile'); print('rubrique « pile » :', await pg.inner_text('.cherche .statut'))
        # clavier : les premiers arrêts de tabulation et leur contour
        await pg.goto(B+'index.html',wait_until='networkidle'); arr=[]
        for i in range(6):
            await pg.keyboard.press('Tab')
            arr.append(await pg.evaluate('(()=>{const e=document.activeElement;const s=getComputedStyle(e);return (e.textContent||e.placeholder||e.tagName).trim().slice(0,24)+" ["+s.outlineStyle+" "+s.outlineWidth+"]"})()'))
        print('tabulation :', arr)
        await pg.click('.mode-btn[data-theme="dark"]'); print('thème choisi :', await pg.evaluate('document.documentElement.dataset.theme'), await pg.evaluate('localStorage.getItem("theme")'))
        await pg.reload(); print('après rechargement :', await pg.evaluate('document.documentElement.dataset.theme'))
        await b.close()
asyncio.run(main())
