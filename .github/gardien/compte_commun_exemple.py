#!/usr/bin/env python3
"""Rejoue l'exemple de docs/COMPTE-COMMUN.md (« Brancher une application ») sur une base LOCALE.
(Gardien, T132d). Usage (à la racine du dépôt) : python3 -I -B .github/gardien/compte_commun_exemple.py . "psql -h SOCKET -p PORT -U postgres"
"""
import importlib.util
import os
import re
import sys
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(sys.argv[1])
sys.path.insert(0, ICI)
import api_stricte as serveur_strict  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

spec = importlib.util.spec_from_file_location("t_archi", os.path.join(RACINE, "scripts", "tests", "test_compte_commun_en_ligne.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
serveur, BASE = serveur_strict.demarrer(RACINE, T.preparer(sys.argv[2]))

doc = open(os.path.join(RACINE, "docs", "COMPTE-COMMUN.md"), encoding="utf-8").read()
bloc = re.search(r"```html\n(.*?)```", doc, re.S).group(1)
# la seule adaptation : le module servi par le site local, la clé réelle (publique) au lieu de « sb_publishable_… »
bloc = bloc.replace("https://babash.github.io/Babash-NSI-SNT/assets/compte-commun.js", BASE + "/assets/compte-commun.js")
bloc = bloc.replace("'sb_publishable_…'", "'" + serveur_strict.CLE + "'")
page_essai = ("<!doctype html><html lang='fr'><head><meta charset='utf-8'><title>Essai</title></head><body>"
              "<script>var JOURNAL = []; function demarrer(p, a) { JOURNAL.push({ pseudo: p, avatar: !!a }); }</script>"
              + bloc + "</body></html>")
with open(os.path.join(RACINE, "reglages.js"), encoding="utf-8") as f:
    REGLAGES = f.read().replace("COMPTE_COMMUN_EN_LIGNE: false", "COMPTE_COMMUN_EN_LIGNE: true")
ok = True


def dire(c, t):
    global ok
    print(("OK     " if c else "ÉCHEC  ") + t)
    ok = ok and c


def route_api(route):
    req = route.request
    h = {k.lower(): v for k, v in req.all_headers().items()}
    r = urllib.request.Request(BASE + "/rest/v1/rpc/" + req.url.rsplit("/", 1)[1], data=(req.post_data or "{}").encode(), method="POST",
                               headers={"Content-Type": "application/json", "apikey": h.get("apikey", ""), "X-Forwarded-For": "10.7.0.1"})
    try:
        with urllib.request.urlopen(r) as rep:
            s, c = rep.status, rep.read()
    except urllib.error.HTTPError as e:
        s, c = e.code, e.read()
    route.fulfill(status=s, body=c, headers={"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"})


with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context()
    ctx.route(T.BASE_API + "/**", route_api)
    ctx.route("**/reglages.js", lambda r: r.fulfill(status=200, body=REGLAGES, headers={"Content-Type": "application/javascript"}))
    ctx.route("**/essai-application.html", lambda r: r.fulfill(status=200, body=page_essai, headers={"Content-Type": "text/html; charset=utf-8"}))
    erreurs = []
    # 1. sans compte sur l'appareil : le jeu démarre avec un pseudo
    a = ctx.new_page()
    a.on("pageerror", lambda e: erreurs.append(str(e)))
    a.goto(BASE + "/essai-application.html")
    a.wait_for_timeout(1500)
    dire(a.evaluate("JOURNAL") == [{"pseudo": None, "avatar": False}], "sans compte : demarrer(null), et le bandeau reste vide (%r)" % a.evaluate("document.getElementById('mon-compte').textContent"))
    # 2. un·e élève crée son code sur la planque, avec « C'est mon téléphone »
    e = ctx.new_page()
    e.goto(BASE + "/eleve/")
    e.locator("#titre-creer").locator("xpath=..").get_by_label("Ton prénom ou un pseudo").fill("Lou")
    e.locator("#titre-creer").locator("xpath=..").get_by_label("C'est mon téléphone").check()
    e.get_by_role("button", name="Créer mon code").click()
    code = e.locator(".cc-code-grand").inner_text(timeout=15000).strip()
    e.get_by_label("Retape les 3 chiffres de ton code").fill(code[-3:])
    e.get_by_role("button", name="C'est noté").click()
    e.get_by_text("Salut, Lou").wait_for()
    # 3. l'application, dans un autre onglet : elle reconnaît l'élève
    b = ctx.new_page()
    b.on("pageerror", lambda x: erreurs.append(str(x)))
    b.goto(BASE + "/essai-application.html")
    b.wait_for_timeout(2000)
    dire(b.evaluate("JOURNAL") == [{"pseudo": "Lou", "avatar": True}], "avec un compte ouvert : demarrer('Lou', avatar) (%r)" % b.evaluate("JOURNAL"))
    texte = b.evaluate("document.getElementById('mon-compte').textContent")
    dire("Lou · mes applications" in texte and "Ce n'est pas moi" in texte and "QuizzNSI" not in texte, "le bandeau : « Lou · mes applications », sans QuizzNSI elle-même (%s)" % texte[:120])
    dire(not erreurs, "aucune erreur JavaScript %r" % erreurs[:2])
    nav.close()
serveur.shutdown()
print("Fautes de l'API stricte :", serveur_strict.FAUTES)
sys.exit(0 if ok and not serveur_strict.FAUTES else 1)
