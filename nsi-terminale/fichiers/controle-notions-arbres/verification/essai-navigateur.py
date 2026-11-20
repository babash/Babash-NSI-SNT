# Usage : depuis la racine du dépôt, python3 -m http.server 8765, puis python3 -I verification/<ce script> <dossier de sortie>
import sys, asyncio, json
from playwright.async_api import async_playwright
B='http://localhost:8765/nsi-terminale/fichiers/controle-notions-arbres/'
OUT=sys.argv[1]
REP={
 '1': {'q1':'15','q2':'26 9 4','q3':'8','q4':'4','q5':'2','q6':'c','q7':'15 8 4 11 9 22 30 26','q8':'15, 8, 4, 11, 9, 22, 30, 26','q9':'4 8 9 11 15 22 26 30','q10':'26','q11':'taille(arbre.droit) + 1 + taille(arbre.gauche)','q12':['13','7','20','3','10','25']},
 '2': {'q1':'40','q2':'12 31 45 47 60','q3':'7','q4':'3','q5':'','q6':'a','q7':'40 25 52 12 31 47 60 45','q8':'40 25 12 31 45 52 47 60','q9':'12 25 31 40 45 47 52 60','q10':'45','q11':'taille(arbre.gauche)+taille(arbre.droit)','q12':['30','18','42','35','22','50']},
}
async def eleve(b, sujet, pseudo, rep, larg=375, sombre=False):
    ctx=await b.new_context(viewport={'width':larg,'height':800}, color_scheme='dark' if sombre else 'light', permissions=['clipboard-read','clipboard-write'])
    pg=await ctx.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    await pg.goto(B+'index.html?sujet='+sujet)
    await pg.fill('#pseudo', pseudo); await pg.fill('#classe','tg2')
    await pg.click('button[type=submit]')
    for q,v in rep.items():
        if q=='q6':
            if v: await pg.check(f'input[name=r-q6][value={v}]')
        elif q=='q12':
            sels=await pg.query_selector_all('select[name=r-q12]')
            for s_ in sels:
                k=int(await s_.get_attribute('data-case')); await s_.select_option(v[k])
        else:
            await pg.fill('#r-'+q, v)
    prog=await pg.text_content('#progression')
    await pg.click('#rendre'); await pg.click('#confirmer-rendre')
    code=await pg.input_value('#code-copie')
    # reprise après rechargement : la copie rendue reste
    await pg.reload(); assert await pg.is_hidden('#rendu') and await pg.is_visible('#copie-existante')
    await pg.click('#reprendre'); assert not await pg.is_hidden('#rendu')
    assert await pg.input_value('#code-copie')==code
    await pg.locator('#qr').screenshot(path=f'{OUT}/qr-{sujet}.png')
    await ctx.close()
    return code, prog, errs
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        c1,p1,e1=await eleve(b,'1','Zaïna',REP['1'])
        c2,p2,e2=await eleve(b,'2','Ibrahim',REP['2'])
        c3,p3,e3=await eleve(b,'2','Copieur',REP['2'])
        print('codes', len(c1), c1[:40], '|', p1, p2, e1+e2+e3)
        ctx=await b.new_context(viewport={'width':1440,'height':900}, accept_downloads=True)
        pg=await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        await pg.goto(B+'prof.html')
        # code 1 collé avec retours à la ligne ; code 2 en minuscules ; code 3 par photo du QR
        coupe=c1[:50]+'\n'+c1[50:120]+' \n'+c1[120:]
        await pg.fill('#codes', 'Bonjour madame\n'+coupe+'\n'+c2.lower()+'\n'+c1[:-1]+'X')
        await pg.click('#lire-codes')
        await pg.set_input_files('#photo', f'{OUT}/qr-2.png'); await pg.wait_for_timeout(800)
        await pg.fill('#codes', c3); await pg.click('#lire-codes')
        msgs=await pg.eval_on_selector_all('#messages li','e=>e.map(x=>x.textContent)')
        print('messages', msgs)
        print('resume', await pg.text_content('#resume'))
        rows=await pg.eval_on_selector_all('#table tbody tr','e=>e.map(r=>[...r.children].map(c=>c.textContent).join(" "))')
        print('\n'.join(rows))
        print('alertes', await pg.text_content('#alertes'))
        st=await pg.eval_on_selector_all('#stats tbody tr','e=>e.map(r=>[...r.children].map(c=>c.textContent).join(" | "))')
        print('\n'.join(st))
        det=await pg.eval_on_selector_all('#details details','e=>e.map(d=>d.textContent)')
        print(det[1][:1500])
        async with pg.expect_download() as dl: await pg.click('#csv')
        d=await dl.value; await d.save_as(f'{OUT}/export.csv')
        print('erreurs prof', errs)
        await pg.screenshot(path=f'{OUT}/prof-1440.png', full_page=True)
        await ctx.close(); await b.close()
asyncio.run(main())
