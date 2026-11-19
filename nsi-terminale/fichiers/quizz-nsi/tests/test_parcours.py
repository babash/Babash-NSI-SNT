#!/usr/bin/env python3
"""QuizzNSI : parcours complets dans un vrai navigateur (Playwright, Chromium).

Lancement, depuis la racine de QuizzNSI :
    python3 -I tests/test_parcours.py [DOSSIER_DES_CAPTURES]

1. Une séance « tous ensemble » avec un·e enseignant·e et deux élèves (Nadia et Ali, à 320 px),
   par le chemin « en ligne » de js/seance.js, mais avec un faux client temps réel
   (tests/faux-temps-reel.js) : aucune requête ne sort, la base n'est jamais appelée.
   On contrôle : le pseudo invisible refusé, le pseudo déjà pris refusé, le pseudo retiré par
   l'enseignant·e, les 20 questions, les points de chaque élève (recalculés ici d'après le barème),
   le podium et l'écran de fin.
2. Le mode autonome : les 37 diapositives, une erreur puis la bonne réponse, le bilan.
3. La version imprimable : le sujet et le corrigé en PDF A4, sans débordement.
4. Toutes les pages à 320, 768 et 1440 px, en clair et en obscur : aucun défilement horizontal.
Aucune erreur JavaScript n'est tolérée ; toute requête vers un autre site est bloquée et signalée.
"""
import functools
import http.server
import json
import os
import sys
import threading

from playwright.sync_api import sync_playwright

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SORTIE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RACINE, "tests", "captures")
os.makedirs(SORTIE, exist_ok=True)
with open(os.path.join(RACINE, "cours", "piles-files.json"), encoding="utf-8") as f:
    COURS = json.load(f)
QUESTIONS = [d for d in COURS["diapositives"] if d["type"] == "question"]
BONNES = [next(i for i, o in enumerate(q["options"]) if o.get("juste")) for q in QUESTIONS]
with open(os.path.join(RACINE, "tests", "faux-temps-reel.js"), encoding="utf-8") as f:
    FAUX = f.read()

erreurs, externes = [], []


def serveur():
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    gestion = functools.partial(Silencieux, directory=RACINE)
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}/"


def surveiller(page, nom):
    page.on("pageerror", lambda e: erreurs.append(f"{nom} : {e}"))
    page.on("console", lambda m: erreurs.append(f"{nom} (console) : {m.text}") if m.type == "error" else None)


def contexte(navigateur, base, **kw):
    ctx = navigateur.new_context(**kw)

    def route(r):
        url = r.request.url
        if url.endswith("/vendor/temps-reel.js"):
            return r.fulfill(status=200, content_type="text/javascript", body=FAUX)
        if not url.startswith(base) and not url.startswith("data:") and not url.startswith("blob:"):
            externes.append(url)
            return r.abort()
        return r.continue_()
    ctx.route("**/*", route)
    return ctx


def points(juste, precedente):
    """Le barème de js/bareme.js, sans minuterie : +10 pour répondre, +100 si juste, +30 de rebond."""
    return 10 + (100 if juste else 0) + (30 if juste and precedente == "faux" else 0)


def attendre_texte(page, selecteur, texte, delai=8000):
    page.wait_for_function("([s, t]) => { const e = document.querySelector(s); return e && e.innerText.includes(t); }", arg=[selecteur, texte], timeout=delai)


def seance(nav, base):
    ctx = contexte(nav, base)
    prof = ctx.new_page()
    prof.set_viewport_size({"width": 1440, "height": 900})
    surveiller(prof, "enseignant·e")
    prof.goto(base + "animer.html?cours=piles-files")
    attendre_texte(prof, "#etatConnexion", "Séance ouverte")
    code = prof.inner_text("#code").strip()
    assert len(code) == 4, code
    journal = prof.evaluate("window.__fauxTempsReel")
    assert journal["clients"][0]["url"] == "wss://cukahpyqkljiddmimpyi.supabase.co/realtime/v1", journal
    assert journal["clients"][0]["apikey"].startswith("sb_publishable_"), "clé publishable attendue"

    def eleve(pseudo, largeur=320, theme="light"):
        p = ctx.new_page()
        p.set_viewport_size({"width": largeur, "height": 740})
        p.emulate_media(color_scheme=theme)
        surveiller(p, pseudo)
        p.goto(base + f"rejoindre.html?s={code}")
        p.fill("#champPseudo", pseudo)
        p.click("#rejoindre")
        return p

    # un pseudo avec un caractère invisible est refusé avant tout envoi
    p0 = ctx.new_page(); surveiller(p0, "invisible")
    p0.goto(base + f"rejoindre.html?s={code}")
    p0.fill("#champPseudo", "Na" + chr(0x200B) + "dia")
    p0.click("#rejoindre")
    assert "invisible" in p0.inner_text("#erreurPseudo"), p0.inner_text("#erreurPseudo")
    p0.close()

    nadia = eleve("Nadia", theme="light")
    ali = eleve("Ali", theme="dark")
    intrus = eleve("Pseudo Bizarre")
    attendre_texte(prof, "#eleves", "Pseudo Bizarre")
    attendre_texte(prof, "#eleves", "Nadia")
    attendre_texte(prof, "#eleves", "Ali")
    prof.screenshot(path=os.path.join(SORTIE, "seance-accueil-1440.png"))
    # le même pseudo (à la casse et aux accents près) est refusé
    double = eleve("NADIA")
    attendre_texte(double, "#erreurPseudo", "déjà pris")
    double.close()
    # l'enseignant·e retire un pseudo : l'élève doit en choisir un autre
    prof.click('#eleves li:has-text("Pseudo Bizarre") button.retirer')
    attendre_texte(intrus, "#erreurPseudo", "retiré")
    prof.wait_for_function("() => !document.querySelector('#eleves').innerText.includes('Pseudo Bizarre')")
    intrus.fill("#champPseudo", "Pseudo Bizarre")
    intrus.click("#rejoindre")
    attendre_texte(intrus, "#erreurPseudo", "retiré")  # le pseudo retiré reste refusé
    intrus.close()

    prof.select_option("#duree", "0")
    prof.click("#commencer")
    # Nadia : une erreur sur 4, Ali : toujours A (ses rebonds sont rares)
    choix_n = [BONNES[k] if k % 4 != 1 else (BONNES[k] + 1) % 4 for k in range(20)]
    choix_a = [0] * 20
    attendu = {"Nadia": 0, "Ali": 0}
    prec = {"Nadia": None, "Ali": None}
    k = 0
    for i, d in enumerate(COURS["diapositives"]):
        if i > 0:
            prof.click("#action")
        if d["type"] == "notion" and i == 1:
            attendre_texte(nadia, "#ecran", d["titre"])
            nadia.screenshot(path=os.path.join(SORTIE, "eleve-notion-320.png"), full_page=True)
        if d["type"] != "question":
            continue
        for page, nom, ch in ((nadia, "Nadia", choix_n), (ali, "Ali", choix_a)):
            page.wait_for_selector(f'section.d-question button.option[data-choix="{ch[k]}"]:not([disabled])', timeout=8000)
            attendre_texte(page, ".q-num", f"Question {k + 1} sur 20")
            if k == 2 and nom == "Nadia":
                page.screenshot(path=os.path.join(SORTIE, "eleve-question-320.png"), full_page=True)
            page.click(f'button.option[data-choix="{ch[k]}"]')
            juste = ch[k] == BONNES[k]
            attendu[nom] += points(juste, prec[nom])
            prec[nom] = "juste" if juste else "faux"
        attendre_texte(prof, "#statutQ", "Tout le monde a répondu")
        attendre_texte(nadia, "#envoyee", "reçue")
        if k == 4:
            prof.screenshot(path=os.path.join(SORTIE, "seance-question-1440.png"))
        prof.click("#action")  # montrer la réponse
        for page, nom in ((nadia, "Nadia"), (ali, "Ali")):
            attendre_texte(page, ".q-num", f"Question {k + 1} sur 20 · correction")
            attendre_texte(page, "#points", f"{attendu[nom]} pts")
        if k == 4:
            prof.screenshot(path=os.path.join(SORTIE, "seance-correction-1440.png"), full_page=True)
            nadia.screenshot(path=os.path.join(SORTIE, "eleve-correction-320.png"), full_page=True)
            ali.screenshot(path=os.path.join(SORTIE, "eleve-correction-320-obscur.png"), full_page=True)
        k += 1
    assert k == 20
    prof.click("#action")  # terminer la séance
    prof.wait_for_selector("#podiumBoite[open]")
    attendre_texte(prof, "#podiumCorps", "Nadia")
    prof.screenshot(path=os.path.join(SORTIE, "seance-podium-1440.png"))
    attendre_texte(nadia, "#ecran", "Fin de la séance")
    attendre_texte(nadia, "#ecran", f"{attendu['Nadia']} points")
    attendre_texte(nadia, "#ecran", "1re place")
    nadia.screenshot(path=os.path.join(SORTIE, "eleve-fin-320.png"), full_page=True)
    attendre_texte(ali, "#ecran", f"{attendu['Ali']} points")
    print(f"  séance : 20 questions, points Nadia {attendu['Nadia']}, Ali {attendu['Ali']}, envois {prof.evaluate('window.__fauxTempsReel.envois')}")
    ctx.close()


def autonome(nav, base):
    ctx = contexte(nav, base)
    p = ctx.new_page()
    p.set_viewport_size({"width": 390, "height": 800})
    surveiller(p, "autonome")
    p.goto(base + "revision.html?cours=piles-files")
    p.wait_for_selector("section.d-titre")
    k = 0
    for i, d in enumerate(COURS["diapositives"]):
        if i > 0:
            p.click("#suiv")
        if d["type"] == "question":
            p.wait_for_selector(f'section.d-question[data-q="{k + 1}"]')
            if k == 0:  # une erreur d'abord : feedback, puis nouvel essai
                p.click(f'button.option[data-choix="{(BONNES[k] + 1) % 4}"]')
                attendre_texte(p, ".zone-correction", "Pas encore")
                p.screenshot(path=os.path.join(SORTIE, "autonome-erreur-390.png"), full_page=True)
            p.keyboard.press("abcd"[BONNES[k]])  # au clavier
            attendre_texte(p, ".zone-correction", "Bonne réponse")
            k += 1
    attendre_texte(p, "#scene", "19 sur 20")
    p.screenshot(path=os.path.join(SORTIE, "autonome-bilan-390.png"), full_page=True)
    p.reload()  # la progression reste sur l'appareil
    attendre_texte(p, "#scene", "19 sur 20")
    print("  autonome : 37 diapositives, bilan 19 sur 20 du premier coup")
    ctx.close()


def impression(nav, base):
    ctx = contexte(nav, base)
    p = ctx.new_page()
    surveiller(p, "impression")
    for nom, q in (("sujet", ""), ("corrige", "&corrige")):
        p.goto(base + "imprimer.html?cours=piles-files" + q)
        p.wait_for_selector(".f-question")
        p.emulate_media(media="print")
        p.set_viewport_size({"width": 702, "height": 1000})  # largeur utile d'une page A4 (186 mm)
        deborde = p.evaluate("""() => { const f = document.querySelector('.feuille').getBoundingClientRect();
            return [...document.querySelectorAll('.feuille *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.right > f.right + 1; }).map(e => e.tagName + '.' + e.className).slice(0, 5); }""")
        assert not deborde, f"{nom} déborde : {deborde}"
        chemin = os.path.join(SORTIE, f"imprimer-{nom}.pdf")
        p.pdf(path=chemin, format="A4", prefer_css_page_size=True, print_background=True)
        p.emulate_media(media="screen")
        print(f"  impression : {nom} sans débordement ({chemin})")
    ctx.close()


def rendus(nav, base):
    pages = ["index.html", "revision.html#7", "revision.html#30", "animer.html", "rejoindre.html", "imprimer.html", "imprimer.html?corrige"]
    for theme in ("light", "dark"):
        for largeur in (320, 768, 1440):
            ctx = contexte(nav, base, color_scheme=theme, viewport={"width": largeur, "height": 900})
            for adresse in pages:
                p = ctx.new_page()
                surveiller(p, f"{adresse} {largeur} {theme}")
                p.goto(base + adresse)
                p.wait_for_timeout(500)
                large = p.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
                assert large <= 0, f"{adresse} à {largeur} px ({theme}) : défilement horizontal de {large} px"
                nom = adresse.replace(".html", "").replace("#", "-").replace("?", "-")
                p.screenshot(path=os.path.join(SORTIE, f"rendu-{nom}-{largeur}-{theme}.png"), full_page=True)
                p.close()
            ctx.close()
    print("  rendus : 7 pages × 3 largeurs × 2 thèmes, sans défilement horizontal")


def main():
    s, base = serveur()
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        seance(nav, base)
        autonome(nav, base)
        impression(nav, base)
        rendus(nav, base)
        nav.close()
    s.shutdown()
    if externes:
        print("Requêtes externes bloquées :", sorted(set(externes)))
    if erreurs:
        print("Erreurs JavaScript :", *erreurs, sep="\n  ")
    ok = not erreurs and not externes
    print("parcours : " + ("tout est conforme" if ok else "ÉCHEC") + f" ; captures dans {SORTIE}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
