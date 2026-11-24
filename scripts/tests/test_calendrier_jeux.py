#!/usr/bin/env python3
"""Essai automatique des mini-jeux du Calendrier des vacances, un par type (T135), dans Chromium.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_calendrier_jeux.py [--captures DOSSIER]

Le test sert le dépôt en local et joue, avec le vrai moteur (calendrier/commun.js et jeux.js),
chaque niveau de chaque exercice des deux banques d'exemple :
  scripts/tests/calendrier/exemple-boucles.json        (les six premiers types)
  scripts/tests/calendrier/exemple-nouveaux-types.json (trace, combien, paniers, intrus, memo, bits)
Pour chaque type : une erreur volontaire d'abord (le retour doit être annoncé dans la zone aria-live),
puis la bonne réponse, au doigt (clic) et au clavier (Entrée, flèches, Espace) ; la partie doit se
terminer avec son résultat. Puis le corrigé de chaque exercice, la reprise d'une partie gardée,
l'absence de défilement horizontal à 320 px (clair et obscur), et l'animation coupée quand
l'appareil demande moins de mouvement. Aucune requête ne sort de la machine.
Il faut Playwright et Chromium. Code de retour : 0 si tout passe, 1 sinon.
"""
import argparse
import functools
import http.server
import json
import os
import sys
import threading

from playwright.sync_api import sync_playwright

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BANQUES = [os.path.join(RACINE, "scripts", "tests", "calendrier", f) for f in ("exemple-boucles.json", "exemple-nouveaux-types.json")]
HARNAIS = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Essai des mini-jeux</title><link rel="stylesheet" href="../assets/signal-commun.css"><link rel="stylesheet" href="calendrier.css"></head>
<body><main class="page"><div id="jeu"></div></main><script src="config.js"></script><script src="commun.js"></script><script src="jeux.js"></script>
<script>
window.FIN = null; window.SAUVE = null;
window.lancer = function (ex, niveau, sauvegarde) {
  window.FIN = null;
  if (window.PARTIE) window.PARTIE.arreter();
  var vieux = document.getElementById("jeu"), neuf = document.createElement("div"); neuf.id = "jeu"; vieux.replaceWith(neuf);
  window.PARTIE = CV.jouer(document.getElementById("jeu"), { exercice: ex, niveau: niveau, langage: "python", titreCase: "essai",
    sauvegarde: sauvegarde || null, surSauver: function (g) { window.SAUVE = g; }, surFin: function (r) { window.FIN = r; }, surQuitter: function () {} });
};
</script></body></html>"""

ECHECS = []


def verifier(cond, quoi):
    if not cond:
        ECHECS.append(quoi)
    return cond


def servir():
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    gestion = functools.partial(Silencieux, directory=RACINE)
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d" % s.server_address[1]


def etat(page):
    return page.evaluate("document.getElementById('jeu').cvEtat()")


def annonce(page):
    return page.inner_text(".retour-jeu[aria-live]")


def faute(page, t, it, s):
    """Une erreur volontaire ; renvoie False si le type n'en permet pas ici."""
    if t == "vraifaux":
        page.click("[data-j=vf][data-v='%d']" % (0 if it["reponse"] else 1))
    elif t == "sortie" and "options" in it:
        page.click("[data-j=opt][data-k='%d']" % ((it["bonne"] + 1) % 4))
    elif t == "sortie":
        page.fill("#rep", "pas ça")
        page.press("#rep", "Enter")
    elif t == "erreur":
        page.click("[data-j=ligne][data-i='%d']" % ((it["ligne"] + 1) % len(it["lignes"])))
    elif t == "associer":
        page.click("[data-j=ag][data-i='0']")
        page.click("[data-j=ad][data-i='1']")
    elif t == "trace":
        champs = page.locator("input.cellule")
        for k in range(champs.count()):
            champs.nth(k).fill("999")
        champs.nth(0).press("Enter")
    elif t == "combien":
        page.click("[data-j=verifier]")
    elif t == "paniers":
        i = s["ordre"][0]
        page.click("[data-j=panier][data-i='%d'][data-p='%d']" % (i, 1 - it["cartes"][i]["panier"]))
    elif t == "intrus":
        page.click("[data-j=intrus][data-k='%d']" % ((it["intrus"] + 1) % len(it["elements"])))
    elif t == "bits":
        page.click("[data-j=verifier]")
    else:
        return False
    return True


def juste(page, t, it, s):
    """Un geste juste (au doigt ou au clavier)."""
    if t == "vraifaux":
        page.click("[data-j=vf][data-v='%d']" % (1 if it["reponse"] else 0))
    elif t == "sortie" and "options" in it:
        page.click("[data-j=opt][data-k='%d']" % it["bonne"])
    elif t == "sortie":
        page.fill("#rep", it["reponse"])
        page.press("#rep", "Enter")
    elif t == "associer":
        for i in range(len(it["paires"])):
            if str(i) not in (s.get("trouves") or {}):
                page.click("[data-j=ag][data-i='%d']" % i)
                page.click("[data-j=ad][data-i='%d']" % i)
                return
    elif t == "erreur":
        if s["phase"] == 1:
            page.click("[data-j=ligne][data-i='%d']" % it["ligne"])
        else:
            page.click("[data-j=corr][data-k='%d']" % it["bonne"])
    elif t == "ordre":
        k = len(s["ordre"])
        if k < len(it["lignes"]):
            page.click("[data-j=placer][data-i='%d']" % s["reserve"].index(k))
        else:
            page.click("[data-j=verifier]")
    elif t == "completer":
        for d, tr in enumerate(it["trous"]):
            page.click("[data-j=trou][data-d='%d']" % d)
            page.click("[data-j=jeton][data-k='%d']" % tr["bonne"])
        page.click("[data-j=verifier]")
    elif t == "trace":
        for r, ligne in enumerate(it["tours"]):
            for c, v in enumerate(ligne):
                champ = page.locator("input.cellule[data-cle='%d-%d']" % (r, c))
                if champ.count():
                    champ.fill(("'%s'" % v) if not v.lstrip("-").isdigit() and r == 0 else v)  # des guignets acceptés
        page.locator("input.cellule").last.press("Enter")
    elif t == "combien":
        page.focus("#valeur")
        n = s["n"]
        while n != it["reponse"]:
            if abs(it["reponse"] - n) >= 10:
                page.keyboard.press("PageUp" if it["reponse"] > n else "PageDown")
                n += 10 if it["reponse"] > n else -10
            else:
                page.keyboard.press("ArrowUp" if it["reponse"] > n else "ArrowDown")
                n += 1 if it["reponse"] > n else -1
        verifier(page.get_attribute("#valeur", "aria-valuenow") == str(it["reponse"]), "combien : aria-valuenow suit le compteur")
        page.click("[data-j=verifier]")
    elif t == "paniers":
        i = [k for k in s["ordre"] if str(k) not in {str(x) for x in (s.get("places") or {})}][0]
        page.click("[data-j=panier][data-i='%d'][data-p='%d']" % (i, it["cartes"][i]["panier"]))
    elif t == "intrus":
        if s["phase"] == 1:
            page.click("[data-j=intrus][data-k='%d']" % it["intrus"])
        else:
            page.click("[data-j=pourquoi][data-k='%d']" % it["pourquoi"]["bonne"])
    elif t == "memo":
        cartes, trouves = s["cartes"], s.get("trouves") or {}
        if len(s["ouvertes"]) == 1:
            p0 = cartes[s["ouvertes"][0]][0]
            k = [j for j, c in enumerate(cartes) if c[0] == p0 and j != s["ouvertes"][0]][0]
            page.click("[data-j=memo][data-k='%d']" % k)
            return
        libres = [j for j, c in enumerate(cartes) if str(c[0]) not in trouves]
        if not trouves and s["coups"] == 0:
            # un premier coup raté, volontaire : deux cartes de paires différentes
            a = libres[0]
            b = [j for j in libres if cartes[j][0] != cartes[a][0]][0]
            page.click("[data-j=memo][data-k='%d']" % a)
            page.click("[data-j=memo][data-k='%d']" % b)
            verifier("pas une paire" in annonce(page), "memo : le coup raté est annoncé")
            return
        page.click("[data-j=memo][data-k='%d']" % libres[0])
    elif t == "bits":
        for i, b in enumerate(it["reponse"]):
            on = s["bits"][i] == "1"
            if (b == "1") != on:
                bouton = page.locator("[data-j=bit][data-i='%d']" % i)
                if i % 2:
                    bouton.focus()
                    page.keyboard.press("Space")  # au clavier
                else:
                    bouton.click()
                verifier(page.get_attribute("[data-j=bit][data-i='%d']" % i, "aria-pressed") == ("true" if b == "1" else "false"), "bits : aria-pressed suit l'ampoule")
                return
        page.click("[data-j=verifier]")


def jouer(page, ex, niveau, nom):
    page.evaluate("([ex, n]) => lancer(ex, n)", [ex, niveau])
    erreur_faite = False
    for _ in range(400):
        fin = page.evaluate("window.FIN")
        if fin:
            verifier(fin["reussi"] and fin["etoiles"] == niveau, f"{nom} : résultat de fin {fin}")
            return fin
        e = etat(page)
        t, it, s = e["type"], e["item"], e["s"]
        if e["fini"]:
            page.click("[data-j=suivant]")
            continue
        if not erreur_faite:
            erreur_faite = True
            if faute(page, t, it, s):
                verifier(annonce(page).strip() != "", f"{nom} : l'erreur volontaire n'est pas annoncée (aria-live)")
                continue
        juste(page, t, it, s)
    verifier(False, f"{nom} : la partie ne se termine pas")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures")
    a = ap.parse_args()
    url = servir()
    exercices = [ex for f in BANQUES for ex in json.load(open(f, encoding="utf-8"))["exercices"]]
    types_vus = set()
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for mode in ("light", "dark"):
            ctx = nav.new_context(viewport={"width": 320, "height": 760}, color_scheme=mode, reduced_motion="reduce" if mode == "dark" else "no-preference")
            ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith(url) else r.abort())
            ctx.route(url + "/calendrier/__essai__.html", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=HARNAIS))
            page = ctx.new_page()
            erreurs = []
            page.on("pageerror", lambda e: erreurs.append(str(e)))
            page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
            page.goto(url + "/calendrier/__essai__.html")
            for ex in exercices:
                for niveau in (1, 2, 3):
                    nom = f"{mode} {ex['id']} ({ex['type']}) niveau {niveau}"
                    page.evaluate("([ex, n]) => lancer(ex, n)", [ex, niveau])
                    largeur = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                    verifier(largeur <= 0, f"{nom} : défilement horizontal de {largeur} px à 320 px")
                    petits = page.evaluate("""[...document.querySelectorAll('#jeu button:not(.trou):not(.ligne), #jeu input')].filter(b => {
                        const r = b.getBoundingClientRect(); return r.width > 0 && (r.height < 43.5 || r.width < 43.5); }).map(b => b.outerHTML.slice(0, 60))""")
                    verifier(not petits, f"{nom} : cibles de moins de 44 px : {petits[:2]}")
                    if a.captures and niveau == 1:
                        page.screenshot(path=os.path.join(a.captures, f"jeu-{ex['type']}-{mode}.png"), full_page=True)
                    jouer(page, ex, niveau, nom)
                    types_vus.add(ex["type"])
                # le corrigé de l'exercice
                page.evaluate("ex => { document.getElementById('jeu').innerHTML = CV.corrige(ex, 'python'); }", ex)
                verifier(page.locator(".corrige-item").count() >= 3, f"{mode} {ex['id']} : corrigé incomplet")
                if a.captures:
                    page.screenshot(path=os.path.join(a.captures, f"corrige-{ex['type']}-{mode}.png"), full_page=True)
            # la reprise d'une partie gardée (un « memo » à moitié joué)
            memo = [ex for ex in exercices if ex["type"] == "memo"][0]
            page.evaluate("([ex, n]) => lancer(ex, n)", [memo, 1])
            s = etat(page)["s"]
            k = [j for j, c in enumerate(s["cartes"]) if c[0] == s["cartes"][0][0] and j != 0][0]
            page.click("[data-j=memo][data-k='0']")
            page.click("[data-j=memo][data-k='%d']" % k)
            sauve = page.evaluate("window.SAUVE")
            page.evaluate("([ex, n, g]) => lancer(ex, n, g)", [memo, 1, sauve])
            verifier(page.locator(".memo-carte.ok").count() == 2, f"{mode} : la paire trouvée est gardée à la reprise")
            # le mouvement : « secoue » coupé quand l'appareil le demande
            so = [ex for ex in exercices if ex["type"] == "sortie"][0]
            page.evaluate("([ex, n]) => lancer(ex, n)", [so, 1])
            it = etat(page)["item"]
            page.click("[data-j=opt][data-k='%d']" % ((it["bonne"] + 1) % 4))
            anim = page.evaluate("getComputedStyle(document.querySelector('#zone')).animationName")
            verifier(anim == ("none" if mode == "dark" else "secoue"), f"{mode} : animation « secoue » attendue {'coupée' if mode == 'dark' else 'jouée'} ({anim})")
            verifier(not erreurs, f"{mode} : erreurs dans la console : {erreurs[:3]}")
            ctx.close()
        nav.close()
    manquants = {"associer", "erreur", "vraifaux", "sortie", "ordre", "completer", "trace", "combien", "paniers", "intrus", "memo", "bits"} - types_vus
    verifier(not manquants, f"types jamais joués : {sorted(manquants)}")
    for e in ECHECS:
        print("ÉCHEC", e)
    print(f"{len(types_vus)} types joués, {len(exercices) * 3 * 2} parties, {len(ECHECS)} échec(s)")
    return 1 if ECHECS else 0


if __name__ == "__main__":
    sys.exit(main())
