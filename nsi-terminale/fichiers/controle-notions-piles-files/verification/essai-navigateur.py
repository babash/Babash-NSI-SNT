"""Essai complet dans Chromium (Playwright) : copies d'élèves, codes, correction.

Pour chaque sujet : une copie juste partout (réponses tapées comme un·e élève :
espaces, majuscules, « while » recopié…), une copie avec des erreurs connues.
Puis la page prof : codes collés (avec du texte autour, coupés, en minuscules),
un QR lu sur une photo ; on vérifie les notes, les diagnostics, l'alerte de
copies proches et l'export CSV. Vérifie aussi la zone de code (Tab, Entrée).
Captures (320, 768, 1440 px ; clair et obscur) dans le dossier donné.

Usage : depuis la racine du dépôt, python3 -m http.server 8765, puis
        python3 -I nsi-terminale/fichiers/controle-notions-piles-files/verification/essai-navigateur.py <dossier des captures> [port]
Babash - NSI Tani Malandi · MIT
"""
import asyncio
import json
import pathlib
import re
import sys

from playwright.async_api import async_playwright

ICI = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
PORT = sys.argv[2] if len(sys.argv) > 2 else '8765'
B = 'http://localhost:' + PORT + '/nsi-terminale/fichiers/' + ICI.name + '/'
echecs = []


def bloc(fichier, nom):
    texte = (ICI / fichier).read_text(encoding='utf-8')
    return json.loads(re.search(r'/\*' + nom + r'-DEBUT\*/(.*?)/\*' + nom + r'-FIN\*/', texte, re.S).group(1))


D = bloc('controle.js', 'DONNEES')
K = bloc('cle.js', 'CLE')


def verifier(cond, texte):
    print(('ok     ' if cond else 'ÉCHEC  ') + texte)
    if not cond:
        echecs.append(texte)


def juste(s, q, i):
    """Une bonne réponse, tapée avec des variantes d'écriture."""
    k = K[s][q['id']]
    if q['type'] == 'qcu':
        return k['attendu']
    if q['type'] == 'ligne':
        return k['affiche'] if i % 2 else k['attendu'][-1]
    if q['type'] == 'ensemble':
        return ', '.join(reversed(k['attendu'].split()))
    return k['attendu'].upper() if i % 3 == 0 else k['attendu'].replace(' ', ', ')


def fausse(s, q):
    """La réponse du premier diagnostic « si » (une erreur connue), sinon une réponse vide."""
    for d in K[s][q['id']].get('diag', []):
        if 'si' in d:
            return d['si'], d['texte']
    return '', None


async def remplir(pg, reponses):
    for q, v in zip(D['questions'], reponses):
        if v == '':
            continue
        if q['type'] == 'qcu':
            await pg.check('input[name=r-%s][value="%s"]' % (q['id'], v))
        else:
            await pg.fill('#r-' + q['id'], v)


async def eleve(b, sujet, pseudo, reponses, larg=375, sombre=False, captures=False):
    ctx = await b.new_context(viewport={'width': larg, 'height': 800}, color_scheme='dark' if sombre else 'light')
    pg = await ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    await pg.goto(B + 'index.html?sujet=' + sujet)
    nom = '%d-%s' % (larg, 'obscur' if sombre else 'clair')
    if captures:
        await pg.screenshot(path=str(OUT / ('accueil-' + nom + '.png')), full_page=True)
    verifier(await pg.locator('script[src="cle.js"]').count() == 0, 'page élève : la clé n\'est pas chargée')
    await pg.fill('#pseudo', pseudo)
    await pg.fill('#classe', 'tg2')
    await pg.click('button[type=submit]')
    await remplir(pg, reponses)
    larges = await pg.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
    verifier(not larges, 'élève %s, %d px : pas de défilement horizontal de la page' % (pseudo, larg))
    if captures:
        await pg.evaluate('document.activeElement.blur()')
        await pg.screenshot(path=str(OUT / ('copie-' + nom + '.png')), full_page=True)
        # la capture pleine page change la taille de la fenêtre : on la rétablit avant de cliquer
        await pg.set_viewport_size({'width': larg, 'height': 800})
        await pg.wait_for_timeout(300)
    await pg.locator('#rendre').scroll_into_view_if_needed()
    await pg.click('#rendre')
    if not await pg.evaluate("document.getElementById('dialogue-rendre').open"):
        ouverts = await pg.evaluate("[...document.querySelectorAll('dialog[open]')].map(d => d.id)")
        verifier(False, 'élève %s, %d px : la boîte « Rendre ta copie ? » ne s\'ouvre pas (ouverte : %s)' % (pseudo, larg, ouverts))
        await pg.screenshot(path=str(OUT / ('echec-%d.png' % larg)))
        await pg.keyboard.press('Escape')
        await pg.click('#rendre')
    await pg.click('#confirmer-rendre')
    code = await pg.input_value('#code-copie')
    if captures:
        await pg.screenshot(path=str(OUT / ('rendu-' + nom + '.png')), full_page=True)
    await pg.locator('#qr').screenshot(path=str(OUT / ('qr-%s-%s.png' % (sujet, pseudo))))
    verifier(not errs, 'élève %s : aucune erreur dans la console %s' % (pseudo, errs or ''))
    await ctx.close()
    return code


async def zone_code(b):
    """Tab indente, Entrée garde l'indentation (un niveau de plus après « : »), Maj+Tab désindente."""
    ctx = await b.new_context(viewport={'width': 768, 'height': 900})
    pg = await ctx.new_page()
    await pg.goto(B + 'index.html?sujet=1')
    await pg.fill('#pseudo', 'Essai')
    await pg.click('button[type=submit]')
    q = [x for x in D['questions'] if x['type'] == 'ligne'][0]
    z = pg.locator('#r-' + q['id'])
    verifier(await z.evaluate('e => e.tagName') == 'TEXTAREA', 'zone de code : une zone de plusieurs lignes')
    await z.click()
    await pg.keyboard.type('if x:')
    await pg.keyboard.press('Enter')
    await pg.keyboard.type('y = 1')
    await pg.keyboard.press('Enter')
    await pg.keyboard.press('Shift+Tab')
    await pg.keyboard.type('z')
    await pg.keyboard.press('Tab')
    v = await z.input_value()
    verifier(v == 'if x:\n    y = 1\nz    ', 'zone de code : indentation automatique et Tab (%r)' % v)
    await pg.keyboard.press('Escape')
    await pg.keyboard.press('Tab')
    verifier(await pg.evaluate('document.activeElement.id') != 'r-' + q['id'], 'zone de code : Échap puis Tab sort de la zone')
    await ctx.close()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await zone_code(b)
        codes, attendus = [], []
        for s in D['sujets']:
            bon = [juste(s, q, i) for i, q in enumerate(D['questions'])]
            mauvais = [fausse(s, q)[0] for q in D['questions']]
            codes.append(await eleve(b, s, 'Zaïna-' + s, bon))
            codes.append(await eleve(b, s, 'Anli-' + s, mauvais))
            codes.append(await eleve(b, s, 'Nayma-' + s, mauvais))
            attendus += [(s, 'Zaïna-' + s, 12), (s, 'Anli-' + s, 0), (s, 'Nayma-' + s, 0)]
        for larg in (320, 768, 1440):
            for sombre in (False, True):
                await eleve(b, '1', 'Capture', [juste('1', q, i) for i, q in enumerate(D['questions'])], larg, sombre, True)

        ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        await pg.goto(B + 'prof.html')
        c0 = codes[0]
        coupe = c0[:50] + '\n' + c0[50:120] + ' \n' + c0[120:]
        await pg.fill('#codes', 'Bonjour,\n' + coupe + '\n' + '\n'.join(x.lower() for x in codes[2:]) + '\n' + c0[:-1] + 'X')
        await pg.click('#lire-codes')
        await pg.set_input_files('#photo', str(OUT / ('qr-1-Anli-1.png')))
        await pg.wait_for_timeout(800)
        msgs = await pg.eval_on_selector_all('#messages li', 'e => e.map(x => x.textContent)')
        verifier(any('photo' in m for m in msgs), 'prof : le QR code lu sur une photo est ajouté')
        verifier(any('somme de contrôle' in m for m in msgs), 'prof : un code mal recopié est refusé')
        lignes = await pg.eval_on_selector_all('#table tbody tr', 'e => e.map(r => [...r.children].map(c => c.textContent))')
        notes = {l[0]: l[3] for l in lignes}
        for s, nom, pts in attendus:
            verifier(notes.get(nom) == '%d / 12' % pts, 'prof : %s a %s (attendu %d / 12)' % (nom, notes.get(nom), pts))
        alertes = await pg.text_content('#alertes')
        verifier('Anli-1 et Nayma-1' in alertes or 'Nayma-1 et Anli-1' in alertes, 'prof : copies très proches signalées')
        det = ' '.join(await pg.eval_on_selector_all('#details details', 'e => e.map(d => d.textContent)'))
        manque = [t for s in D['sujets'] for q in D['questions'] for t in [fausse(s, q)[1]] if t and t.replace('`', '')[:40] not in det.replace('`', '')]
        verifier(not manque, 'prof : chaque erreur connue reçoit son diagnostic %s' % (manque[:2] or ''))
        async with pg.expect_download() as dl:
            await pg.click('#csv')
        d = await dl.value
        await d.save_as(str(OUT / 'export.csv'))
        csv = (OUT / 'export.csv').read_text(encoding='utf-8-sig')
        verifier(csv.count('\n') == len(attendus) + 1 and 'Zaïna-1' in csv, 'prof : export CSV (%d lignes)' % csv.count('\n'))
        for larg in (320, 768, 1440):
            for sombre in ('light', 'dark'):
                await pg.emulate_media(color_scheme=sombre)
                await pg.set_viewport_size({'width': larg, 'height': 900})
                await pg.screenshot(path=str(OUT / ('prof-%d-%s.png' % (larg, sombre))), full_page=True)
        verifier(not errs, 'prof : aucune erreur dans la console %s' % (errs or ''))
        await ctx.close()
        await b.close()
    print()
    print('Bilan :', 'tout est juste.' if not echecs else '%d échec(s).' % len(echecs))
    sys.exit(1 if echecs else 0)

asyncio.run(main())
