#!/usr/bin/env python3
"""Essais de l'interface du moteur d'avatars dans une vraie page (T133b, Designer).

Usage (à la racine du dépôt) :  python3 -I -B charte/tester-applis.py [--lent]

Playwright (Chromium). Le script sert lui-même le dépôt sur un port libre et vérifie :
- les bulles : 6 au plus par page, les autres attendent leur tour ; numéro inconnu, liste
  inconnue ou valeur non entière : ignorés ; le texte n'est jamais lu comme du HTML ;
- les marques : fanion « a répondu », flamme et son chiffre à partir de 2 ;
- les états d'usage (repondu pose le fanion, attente l'enlève), les gestes et leur retour ;
- le plafond d'avatars animés, le mode calme (forcé, et réglage « mouvement réduit »),
  la pause quand l'onglet est caché, l'avatar neutre ;
- le coût : 35 avatars au lobby (avec --lent : processeur ralenti 6 fois, comme un poste lent) ;
- charte/applis.html : sans erreur, sans défilement horizontal à 320, 768 et 1440 px, en clair
  et en obscur.
"""
import functools
import http.server
import os
import sys
import threading

from playwright.sync_api import sync_playwright

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECHECS = []


def ok(cond, msg):
    if not cond:
        ECHECS.append(msg)
        print("ÉCHEC : " + msg)


class Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serveur():
    h = functools.partial(Silencieux, directory=RACINE)
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, "http://127.0.0.1:%d" % s.server_address[1]


PAGE = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link rel="stylesheet" href="/assets/signal-commun.css"><link rel="stylesheet" href="/assets/applis.css"></head>
<body class="ap"><div class="ap-plateau" id="p"></div><script src="/assets/equipage.js"></script></body></html>"""


def essais_interface(nav, base, lent):
    ctx = nav.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    erreurs = []
    pg.on("pageerror", lambda e: erreurs.append(str(e)))
    pg.route(base + "/essai.html", lambda r: r.fulfill(body=PAGE, content_type="text/html; charset=utf-8"))
    pg.goto(base + "/essai.html")
    if lent:
        cdp = ctx.new_cdp_session(pg)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 6})
    # le coût : 35 avatars au lobby, plafond de 8
    ms = pg.evaluate("""() => { var t0 = performance.now(), P = document.getElementById('p'); window.H = [];
      Equipage.plafond(8);
      for (var i = 0; i < 35; i++) { var j = document.createElement('div'); j.className = 'ap-joueur'; var s = document.createElement('span'); j.appendChild(s); P.appendChild(j);
        H.push(Equipage.creer(s, i % 9 === 4 ? Equipage.neutre() : Equipage.aleatoire(4100 + i * 13), { taille: 96, etat: 'lobby', compagnon: false })); }
      document.body.offsetHeight; return performance.now() - t0; }""")
    pg.wait_for_timeout(50)
    peinture = pg.evaluate("() => new Promise(r => { var t0 = performance.now(); requestAnimationFrame(() => requestAnimationFrame(() => r(performance.now() - t0))); })")
    print("Lobby : 35 avatars rendus en %d ms (+ %d ms jusqu'à l'affichage)%s." % (ms, peinture, " avec un processeur ralenti 6 fois" if lent else ""))
    ok(pg.evaluate("document.querySelectorAll('#p .eq').length") == 35, "35 avatars attendus")
    ok(pg.evaluate("document.querySelectorAll('#p .eq.eq-fige').length") == 27, "plafond de 8 : 27 avatars figés attendus")
    # le geste passe devant le plafond
    ok(pg.evaluate("H[30].geste('salue', { duree: 400 }) && !H[30].element.classList.contains('eq-fige')"), "un geste doit animer l'avatar même au-delà du plafond")
    ok(pg.evaluate("document.querySelectorAll('#p .eq.eq-fige').length") == 27, "toujours 8 animés pendant un geste")
    ok(pg.evaluate("H[30].geste('vole') === false"), "geste inconnu ignoré")
    ok(pg.evaluate("H[31].geste('tempete') && /tourbillonne/.test(H[31].element.querySelector('title').textContent) && !H[31].element.classList.contains('eq-fige')"), "geste tempête")
    ok(pg.evaluate("document.querySelectorAll('#p .eq.eq-fige').length") == 27, "la tempête compte dans le plafond")
    pg.wait_for_timeout(2100)
    ok(pg.evaluate("/au repos/.test(H[31].element.querySelector('title').textContent)"), "après la tempête (1,8 s), retour à l'état d'avant")
    avant = pg.evaluate("H[2].element.querySelector('svg').outerHTML.length")
    pg.evaluate("H[2].geste('saute', { duree: 300 })")
    pendant = pg.evaluate("H[2].element.querySelector('title').textContent")
    ok("très content" in pendant, "le geste « saute » joue l'état très content·e")
    pg.wait_for_timeout(700)
    ok("au repos" in pg.evaluate("H[2].element.querySelector('title').textContent"), "après le geste, retour à l'état d'avant")
    ok(avant > 0, "")
    # les bulles
    ok(pg.evaluate("[H[0].bulle(21), H[0].bulle(-1), H[0].bulle(1.5), H[0].bulle('3'), H[0].bulle(NaN), H[0].bulle(2, 'autre')].every(x => x === false)"),
       "numéro ou liste inconnus : ignorés")
    ok(pg.evaluate("document.querySelectorAll('.eq-bulle').length") == 0, "aucune bulle pour un numéro inconnu")
    pg.evaluate("for (var i = 0; i < 10; i++) H[i].bulle(i, undefined, { duree: 600 })")
    ok(pg.evaluate("document.querySelectorAll('.eq-bulle').length") == 6, "6 bulles au plus à la fois")
    ok(pg.evaluate("document.querySelectorAll('.eq-bulle')[0].textContent") == pg.evaluate("Equipage.phrases[0]"), "la bulle montre la phrase de son numéro")
    pg.wait_for_timeout(900)
    ok(pg.evaluate("document.querySelectorAll('.eq-bulle').length") == 4, "les 4 bulles en attente passent ensuite")
    pg.wait_for_timeout(800)
    ok(pg.evaluate("document.querySelectorAll('.eq-bulle').length") == 0, "les bulles s'effacent")
    ok(pg.evaluate("[H[11].bulle(0, ['TEXTE LIBRE']), H[11].bulle(0, new Proxy(['TEXTE LIBRE'], {})), H[11].bulle(0, { 0: 'TEXTE LIBRE', length: 1 }), H[11].bulle(0, 'constructor')].every(x => x === false)"),
       "un tableau ou un objet fourni par l'appelant est refusé")
    pg.wait_for_timeout(100)
    ok(pg.evaluate("document.body.textContent.indexOf('TEXTE LIBRE') < 0 && document.querySelectorAll('.eq-bulle').length === 0"), "jamais de texte libre dans une bulle")
    ok(pg.evaluate("H[11].bulle(0, 'lobby') === true && H[11].element.querySelector('.eq-bulle').textContent === Equipage.phrases[0]"), "la liste du moteur par son nom")
    ok(pg.evaluate("['constructor', 'toString', '__proto__'].every(k => H[12].geste(k) === false)"), "geste : clés héritées refusées")
    ok(pg.evaluate("Object.isFrozen(Equipage.phrases) && Equipage.phrases.length === 21"), "21 phrases gelées")
    pg.evaluate("Equipage.adresse('madame'); H[15].bulle(19)")
    ok(pg.evaluate("H[15].element.querySelector('.eq-bulle').textContent") == "Ne vous inquiétez pas, Madame.", "la page projetée choisit « Madame »")
    pg.evaluate("Equipage.adresse('monsieur')")
    # marques et états d'usage
    pg.evaluate("H[12].marque('repondu')")
    ok(pg.evaluate("!!H[12].element.querySelector('.eq-fanion') && H[12].element.textContent.indexOf('a répondu') >= 0"), "fanion « a répondu »")
    pg.evaluate("H[12].marque(null)")
    ok(pg.evaluate("!H[12].element.querySelector('.eq-fanion')"), "marque(null) enlève le fanion")
    pg.evaluate("H[13].serie(1)")
    ok(pg.evaluate("!H[13].element.querySelector('.eq-flamme')"), "pas de flamme pour une série de 1")
    pg.evaluate("H[13].serie(4)")
    ok(pg.evaluate("H[13].element.querySelector('.eq-flamme b').textContent") == "4", "flamme et son chiffre")
    pg.evaluate("H[14].etat('repondu')")
    ok(pg.evaluate("!!H[14].element.querySelector('.eq-fanion')"), "l'état repondu pose le fanion")
    pg.evaluate("H[14].etat('attente')")
    ok(pg.evaluate("!H[14].element.querySelector('.eq-fanion') && /concentr/.test(H[14].element.querySelector('title').textContent)"), "l'état attente : concentré·e, sans fanion")
    ok(pg.evaluate("H[14].element.className.split(' ').filter(c => c === 'eq-porteur').length <= 1"), "classes sans doublon")
    # calme, pause, neutre
    pg.evaluate("Equipage.calme(true)")
    ok(pg.evaluate("document.documentElement.classList.contains('eq-calme') && Equipage.calme() === true"), "calme(true)")
    ok(pg.evaluate("[...document.querySelectorAll('#p .eq-img')].every(g => !g.getAttribute('style'))"), "calme : plus aucune animation")
    pg.evaluate("Equipage.calme(null); Equipage.plafond(null)")
    ok(pg.evaluate("document.querySelectorAll('#p .eq.eq-fige').length") == 0, "sans plafond ni calme : tout est animé")
    pg.evaluate("Object.defineProperty(document, 'hidden', { value: true, configurable: true }); document.dispatchEvent(new Event('visibilitychange'))")
    ok(pg.evaluate("document.documentElement.classList.contains('eq-pause')"), "pause quand l'onglet est caché")
    pg.evaluate("Object.defineProperty(document, 'hidden', { value: false, configurable: true }); document.dispatchEvent(new Event('visibilitychange'))")
    ok(pg.evaluate("!document.documentElement.classList.contains('eq-pause')"), "reprise quand l'onglet revient")
    ok(pg.evaluate("JSON.stringify(Equipage.neutre()) === JSON.stringify(Equipage.neutre()) && Equipage.neutre().coiffure === 'capuche'"), "neutre")
    pg.evaluate("H[0].detruire()")
    ok(pg.evaluate("H[0].bulle(1) === false"), "plus de bulle après detruire")
    ok(not erreurs, "erreurs JavaScript : %s" % erreurs)
    ctx.close()
    # le buste sur le téléphone, dans la barre, à côté du chrono
    for schema in ("light", "dark"):
        ctx = nav.new_context(viewport={"width": 320, "height": 700}, color_scheme=schema)
        pg = ctx.new_page()
        pg.goto(base + "/charte/applis.html?essai")
        pg.wait_for_timeout(300)
        b = pg.evaluate("""() => { var a = document.querySelector('#dm-tel-av').getBoundingClientRect(), q = document.querySelector('#dm-question-tel .ap-question').getBoundingClientRect(),
          t = document.querySelector('#dm-question-tel'), p = t.querySelector('pre.code');
          return { dessus: a.bottom <= q.top + 1, dans: a.right <= t.getBoundingClientRect().right, code: p.scrollWidth <= p.clientWidth + 1 }; }""")
        ok(b["dessus"] and b["dans"], "téléphone %s : le buste reste dans la barre du haut" % schema)
        ok(b["code"], "téléphone %s : le code tient à 320 px" % schema)
        pg.evaluate("__tel.etat('repondu')")
        ok(pg.evaluate("!!document.querySelector('#dm-tel-av .eq-fanion') && !!document.querySelector('#dm-tel-av .eq-flamme')"), "téléphone : fanion et flamme")
        pg.evaluate("__tel.etat('juste')")
        ok("très content" in pg.evaluate("document.querySelector('#dm-tel-av title').textContent"), "téléphone : fête quand c'est juste")
        pg.evaluate("__tel.etat('faux')")
        t = pg.evaluate("document.querySelector('#dm-tel-av title').textContent")
        ok("au repos" in t and "triste" not in t, "téléphone : sobre quand c'est faux")
        pg.evaluate("__tel.sans(true)")
        ok("lignée Esprit" in pg.evaluate("document.querySelector('#dm-tel-av title').textContent"), "téléphone : l'Esprit en capuche sans compte")
        ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), "téléphone %s : pas de défilement horizontal" % schema)
        ctx.close()
    # réglage « mouvement réduit »
    ctx = nav.new_context(reduced_motion="reduce")
    pg = ctx.new_page()
    pg.route(base + "/essai.html", lambda r: r.fulfill(body=PAGE, content_type="text/html; charset=utf-8"))
    pg.goto(base + "/essai.html")
    ok(pg.evaluate("Equipage.calme()") is True, "calme() suit le réglage « mouvement réduit »")
    ctx.close()


def essais_page(nav, base):
    for schema in ("light", "dark"):
        for largeur in (320, 768, 1440):
            ctx = nav.new_context(viewport={"width": largeur, "height": 800}, color_scheme=schema)
            pg = ctx.new_page()
            erreurs = []
            pg.on("pageerror", lambda e: erreurs.append(str(e)))
            pg.goto(base + "/charte/applis.html?essai")
            pg.wait_for_timeout(400)
            ok(not erreurs, "applis.html %s %d : %s" % (schema, largeur, erreurs))
            ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), "applis.html %s %d : défilement horizontal" % (schema, largeur))
            ok(pg.evaluate("document.querySelectorAll('#dm-objets figure').length") == 15, "applis.html : 15 objets")
            ctx.close()


def main():
    s, base = serveur()
    with sync_playwright() as p:
        nav = p.chromium.launch()
        essais_interface(nav, base, "--lent" in sys.argv)
        essais_page(nav, base)
        nav.close()
    s.shutdown()
    print("%s" % ("Tout est bon." if not ECHECS else "%d échec(s)." % len(ECHECS)))
    sys.exit(1 if ECHECS else 0)


if __name__ == "__main__":
    main()
