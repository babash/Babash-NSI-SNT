# Usage : depuis la racine du dépôt, python3 -m http.server 8765, puis python3 -I <ce script> [port]
"""Essai d'horloge (Playwright) : ce que la page garde sur l'appareil expire en un jour.

Côté élève :
  - l'élève A compose et rend sa copie ;
  - l'élève B ouvre la page une heure après sur le même navigateur : la copie de A
    ne s'ouvre pas d'office (ni réponses, ni code, ni QR) ; B choisit « En commencer
    une autre », ce qui efface vraiment la clé de A, puis compose ;
  - la copie de B est encore là un jour moins une minute après son début, et
    « la reprendre » rouvre bien la copie de B ;
  - un jour et une minute après, la clé est effacée au chargement.
Côté enseignant·e :
  - une copie lue est encore là après 23 h 59 ; elle est effacée au chargement
    après un jour et une minute ;
  - page restée ouverte : la copie est effacée par la vérification de chaque minute.
Babash - NSI Tani Malandi · MIT
"""
import asyncio
import datetime as dt
import sys

from playwright.async_api import async_playwright

import json, pathlib, re
ICI = pathlib.Path(__file__).resolve().parent.parent
PORT = sys.argv[1] if len(sys.argv) > 1 else '8765'
B = 'http://localhost:' + PORT + '/nsi-terminale/fichiers/' + ICI.name + '/'
_D = json.loads(re.search(r'/\*DONNEES-DEBUT\*/(.*?)/\*DONNEES-FIN\*/', (ICI / 'controle.js').read_text(encoding='utf-8'), re.S).group(1))
CLE_ELEVE = 'controle-%s-v%d' % (_D['id'], _D['version'])
CLE_PROF = CLE_ELEVE + '-prof'
T0 = dt.datetime(2026, 11, 20, 8, 0, tzinfo=dt.timezone.utc)
UN_JOUR = dt.timedelta(days=1)
MINUTE = dt.timedelta(minutes=1)
echecs = []


def verifier(cond, texte):
    print(('ok    ' if cond else 'ÉCHEC ') + texte)
    if not cond:
        echecs.append(texte)


async def stockage(pg, cle):
    return await pg.evaluate('(k) => localStorage.getItem(k)', cle)


async def eleve(b):
    ctx = await b.new_context(viewport={'width': 375, 'height': 800})
    await ctx.clock.install(time=T0)
    pg = await ctx.new_page()
    erreurs = []
    pg.on('pageerror', lambda e: erreurs.append(str(e)))
    pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))

    # A compose et rend
    await pg.goto(B + 'index.html?sujet=1')
    await pg.fill('#pseudo', 'Amina')
    await pg.click('button[type=submit]')
    await pg.fill('#r-q3', 'motdeamina')
    await pg.fill('#r-q4', '42')
    await pg.click('#rendre')
    await pg.click('#confirmer-rendre')
    code_a = await pg.input_value('#code-copie')
    verifier('Amina' in (await stockage(pg, CLE_ELEVE) or ''), 'A : la copie est gardée sur l\'appareil')

    # B arrive une heure après
    await pg.clock.set_system_time(T0 + dt.timedelta(hours=1))
    await pg.goto(B + 'index.html?sujet=1')
    verifier(await pg.is_visible('#copie-existante'), 'B : l\'accueil signale une copie commencée')
    verifier(await pg.is_hidden('#copie') and await pg.is_hidden('#rendu'), 'B : ni la copie ni l\'écran de rendu de A ne s\'ouvrent')
    verifier(await pg.is_hidden('#form-accueil'), 'B : le formulaire attend son choix')
    texte = await pg.inner_text('body')
    verifier(code_a not in texte and 'motdeamina' not in await pg.inner_text('#copie-existante'), 'B : ni le code ni les réponses de A ne sont affichés')
    verifier(await pg.locator('#qr svg').count() == 0 or await pg.is_hidden('#rendu'), 'B : le QR de A n\'est pas montré')
    await pg.click('#autre-copie')
    verifier(await stockage(pg, CLE_ELEVE) is None, 'B : « En commencer une autre » efface la clé de A')
    verifier(await pg.is_visible('#form-accueil'), 'B : le formulaire s\'ouvre')
    await pg.fill('#pseudo', 'Bilal')
    await pg.click('button[type=submit]')
    await pg.fill('#r-q3', '40')
    garde = await stockage(pg, CLE_ELEVE) or ''
    verifier('Bilal' in garde and 'Amina' not in garde, 'B : seule la copie de B est gardée')

    # « Effacer et recommencer » pendant la copie existe
    verifier(await pg.locator('#effacer-copie').count() == 1, 'Copie : bouton « Effacer et recommencer » présent')

    # Un jour moins une minute après le début de B : encore là, et « la reprendre » rouvre B
    debut_b = T0 + dt.timedelta(hours=1)
    await pg.clock.set_system_time(debut_b + UN_JOUR - MINUTE)
    await pg.goto(B + 'index.html?sujet=1')
    verifier(await stockage(pg, CLE_ELEVE) is not None, 'Un jour moins une minute : la copie est encore là')
    await pg.click('#reprendre')
    verifier(await pg.text_content('#barre-pseudo') == 'Bilal', '« La reprendre » rouvre la copie de B')

    # Un jour et une minute après : effacée au chargement
    await pg.clock.set_system_time(debut_b + UN_JOUR + MINUTE)
    await pg.goto(B + 'index.html?sujet=1')
    verifier(await stockage(pg, CLE_ELEVE) is None, 'Un jour et une minute : la clé élève est effacée au chargement')
    verifier(await pg.is_visible('#form-accueil') and await pg.is_hidden('#copie-existante'), 'Un jour et une minute : accueil vierge')
    # « Effacer et recommencer » pendant la copie efface vraiment
    await pg.fill('#pseudo', 'Chadia')
    await pg.click('button[type=submit]')
    await pg.fill('#r-q3', '15')
    await pg.click('text=Ce n\'est pas ma copie, ou je veux recommencer')
    await pg.click('#effacer-copie')
    await pg.wait_for_load_state()
    verifier(await stockage(pg, CLE_ELEVE) is None, 'Copie : « Effacer et recommencer » efface la clé')
    verifier(not erreurs, 'Élève : aucune erreur JavaScript ' + str(erreurs))
    await ctx.close()
    return code_a


async def prof(b, code):
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900})
    await ctx.clock.install(time=T0)
    pg = await ctx.new_page()
    erreurs = []
    pg.on('pageerror', lambda e: erreurs.append(str(e)))
    await pg.goto(B + 'prof.html')
    await pg.fill('#codes', code)
    await pg.click('#lire-codes')
    verifier(code in (await stockage(pg, CLE_PROF) or ''), 'Prof : la copie lue est gardée')
    verifier(await pg.is_visible('#expiration') and 'CSV' in await pg.inner_text('#expiration'), 'Prof : la date d\'effacement et l\'export CSV sont rappelés')

    await pg.clock.set_system_time(T0 + UN_JOUR - MINUTE)
    await pg.reload()
    verifier(await stockage(pg, CLE_PROF) is not None, 'Prof, 23 h 59 : la copie est encore là')

    await pg.clock.set_system_time(T0 + UN_JOUR + MINUTE)
    await pg.reload()
    verifier(await stockage(pg, CLE_PROF) is None, 'Prof, un jour et une minute : la clé est effacée au chargement')
    verifier(await pg.locator('#table tbody tr').count() == 0, 'Prof : plus aucune copie affichée')
    verifier('effacée' in await pg.inner_text('#messages'), 'Prof : l\'effacement est annoncé')

    # Page restée ouverte : effacement par la vérification de chaque minute
    t1 = T0 + 2 * UN_JOUR
    await pg.clock.set_system_time(t1)
    await pg.reload()
    await pg.fill('#codes', code)
    await pg.click('#lire-codes')
    verifier(await stockage(pg, CLE_PROF) is not None, 'Prof, page ouverte : copie relue')
    await pg.clock.run_for('24:02:00')
    verifier(await stockage(pg, CLE_PROF) is None, 'Prof, page ouverte un jour : la clé est effacée sans recharger')
    verifier(await pg.locator('#table tbody tr').count() == 0, 'Prof, page ouverte : le tableau est vidé')
    verifier(not erreurs, 'Prof : aucune erreur JavaScript ' + str(erreurs))
    await ctx.close()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        code = await eleve(b)
        await prof(b, code)
        await b.close()
    print('\n' + ('TOUT EST BON' if not echecs else str(len(echecs)) + ' ÉCHEC(S)'))
    sys.exit(1 if echecs else 0)


asyncio.run(main())
