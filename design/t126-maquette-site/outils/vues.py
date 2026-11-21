"""Vues pour la planche : avant (site actuel, :8761) et après (maquette, :8762)."""
import asyncio, sys
from playwright.async_api import async_playwright
A='http://localhost:8761/'; P='http://localhost:8762/'
ECRANS=[('accueil','', 'index.html?bandeau=1'),
        ('rubrique','nsi-terminale/','nsi-terminale/'),
        ('rubrique-quiz','nsi-terminale/#structures-de-donnees','nsi-terminale/#structures-de-donnees'),
        ('bibliotheque','bibliotheque/','bibliotheque/?bandeau=2'),
        ('fiche','bibliotheque/?r=annales-bac-nsi-par-notion','bibliotheque/fiche.html'),
        ('annales','bibliotheque/annales/','bibliotheque/annales/'),
        ('accueilb',None,'accueil-b.html')]
async def vue(b, url, chemin, w, h, sch):
    ctx=await b.new_context(viewport={'width':w,'height':h},color_scheme=sch,reduced_motion='reduce',device_scale_factor=1)
    pg=await ctx.new_page(); await pg.goto(url,wait_until='networkidle'); await pg.wait_for_timeout(600)
    if '#' in url:
        await pg.evaluate("document.getElementById(location.hash.slice(1)).scrollIntoView()"); await pg.wait_for_timeout(300)
    await pg.screenshot(path=chemin); await ctx.close()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for nom,av,ap in ECRANS:
            if av is not None: await vue(b,A+av,f'vues/{nom}-avant.png',1440,1200,'light')
            await vue(b,P+ap,f'vues/{nom}-apres.png',1440,1200,'light')
            await vue(b,P+ap,f'vues/{nom}-apres-obscur.png',1440,1200,'dark')
            await vue(b,P+ap,f'vues/{nom}-tel.png',360,760,'light')
            await vue(b,P+ap,f'vues/{nom}-tel-obscur.png',360,760,'dark')
        await b.close()
asyncio.run(main())
