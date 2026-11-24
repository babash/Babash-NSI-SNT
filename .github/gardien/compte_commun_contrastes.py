#!/usr/bin/env python3
"""Contrastes (pixels réels, outil .github/gardien/contrastes.py), débordement et clavier des pages du
compte commun, en mode en ligne, derrière l'API stricte, sur une base LOCALE (Gardien, T132d) :
320, 768 et 1440 px, clair et obscur ; l'entrée, la classe (tout ouvert), la projection, l'écran à projeter,
le lien de classe et les sept onglets de la planque.
Usage (à la racine du dépôt) : python3 -I -B .github/gardien/compte_commun_contrastes.py . "psql -h SOCKET -p PORT -U postgres"
"""
import importlib.util
import io
import json
import os
import sys
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(sys.argv[1])
PSQL = sys.argv[2]
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(RACINE, ".github", "gardien"))
import api_stricte as serveur_strict  # noqa: E402
import contrastes as C  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

spec = importlib.util.spec_from_file_location("t_archi", os.path.join(RACINE, "scripts", "tests", "test_compte_commun_en_ligne.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

base_psql = T.preparer(PSQL)
serveur, BASE = serveur_strict.demarrer(RACINE, base_psql)


def api(fn, corps, reseau="10.5.0.1"):
    r = urllib.request.Request(BASE + "/rest/v1/rpc/" + fn, data=json.dumps(corps).encode(), method="POST",
                               headers={"Content-Type": "application/json", "apikey": serveur_strict.CLE, "X-Forwarded-For": reseau})
    with urllib.request.urlopen(r) as rep:
        return json.loads(rep.read())


prof = api("commun_prof_creer_espace", {"p_nom": "Mme Essai", "p_etablissement": "Lycée d'essai"})["code_affiche"]
cl = api("commun_prof_creer_classe", {"p_code": prof, "p_nom": "Seconde 4", "p_applications": ["td", "quizz_nsi"]})
eleves = []
for ps in ("Ali", "Nour", "Zoé"):
    e = api("commun_creer", {"p_pseudo": ps, "p_garde_jours": 1})
    api("commun_rejoindre", {"p_jeton": e["jeton"], "p_code_classe": cl["code"]})
    eleves.append(e["code_affiche"])
with open(os.path.join(RACINE, "reglages.js"), encoding="utf-8") as f:
    REGLAGES = f.read().replace("COMPTE_COMMUN_EN_LIGNE: false", "COMPTE_COMMUN_EN_LIGNE: true")

problemes, lignes = [], []


def contexte(nav, w, m):
    ctx = nav.new_context(viewport={"width": w, "height": 900}, color_scheme=m, reduced_motion="reduce", device_scale_factor=1)

    def route_api(route):
        req = route.request
        h = {k.lower(): v for k, v in req.all_headers().items()}
        entetes = {"Content-Type": "application/json", "X-Forwarded-For": "10.5.0.%d" % (w % 200)}
        if "apikey" in h:
            entetes["apikey"] = h["apikey"]
        r = urllib.request.Request(BASE + "/rest/v1/rpc/" + req.url.rsplit("/", 1)[1], data=(req.post_data or "{}").encode(), headers=entetes, method="POST")
        try:
            with urllib.request.urlopen(r, timeout=30) as rep:
                statut, contenu = rep.status, rep.read()
        except urllib.error.HTTPError as e:
            statut, contenu = e.code, e.read()
        route.fulfill(status=statut, body=contenu, headers={"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"})
    ctx.route(T.BASE_API + "/**", route_api)
    ctx.route("**/reglages.js", lambda r: r.fulfill(status=200, body=REGLAGES, headers={"Content-Type": "application/javascript"}))
    return ctx


def mesurer(page, nom, w, m, clav=None):
    page.evaluate("() => document.fonts ? document.fonts.ready.then(() => 1) : 1")
    page.wait_for_timeout(400)
    page.add_style_tag(content=C.MASQUER)
    page.wait_for_timeout(150)
    image = Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB")
    page.evaluate("() => document.querySelectorAll('style').forEach(s => { if (s.textContent.includes('transparent !important')) s.remove(); })")
    page.wait_for_timeout(100)
    n, defauts = C.mesurer(page, image, 4.5, 3.0)
    deb = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
    et = "%s %d %s" % (nom, w, m)
    ligne = "%-34s %4d textes, %d sous 4,5:1%s%s" % (et, n, len(defauts), " | DÉBORDE" if deb else "",
                                                   "" if not clav else " | clavier : %d arrêts / %d, 1er %s, %d sans indicateur, %d hors écran" % (
                                                       clav["arrets"], clav["focalisables"], clav["premier"], clav["nb_sans_indicateur"], clav["nb_hors_ecran"]))
    lignes.append(ligne)
    print(ligne, flush=True)
    for d in defauts[:6]:
        print("     %.2f:1 (exigé %.1f) %s « %s » %s %.1fpx" % (d["ratio"], d["exige"], d["element"], d["texte"], d["couleur"], d["taille"]))
    if defauts:
        problemes.append("%s : %d texte(s) sous le seuil (%s)" % (et, len(defauts), "; ".join("%s %.2f" % (d["texte"][:30], d["ratio"]) for d in defauts[:3])))
    if deb:
        problemes.append("%s : défilement horizontal" % et)
    if clav:
        if clav["nb_sans_indicateur"]:
            problemes.append("%s : %d élément(s) sans indicateur de focus : %s" % (et, clav["nb_sans_indicateur"], "; ".join(clav["sans_indicateur"][:3])))
        if clav["nb_hors_ecran"]:
            problemes.append("%s : %d élément(s) hors écran au focus : %s" % (et, clav["nb_hors_ecran"], "; ".join(clav["hors_ecran"][:3])))
        if not (clav["premier"] or "").startswith("a.evitement"):
            problemes.append("%s : premier arrêt clavier : %s" % (et, clav["premier"]))


with sync_playwright() as p:
    nav = p.chromium.launch()
    for w in (320, 768, 1440):
        for m in ("light", "dark"):
            ctx = contexte(nav, w, m)
            pg = ctx.new_page()
            clav_ok = w == 1440
            # 1. l'entrée de l'espace enseignant·e
            pg.goto(BASE + "/enseignant/", wait_until="networkidle")
            pg.get_by_label("Ton code d'enseignant·e").wait_for()
            clav = C.clavier(pg) if clav_ok else None
            if clav_ok:
                pg.goto(BASE + "/enseignant/", wait_until="networkidle")
                pg.get_by_label("Ton code d'enseignant·e").wait_for()
            mesurer(pg, "enseignant/ (entrée)", w, m, clav)
            # 2. la classe, hors projection et en projection, puis l'écran à projeter
            pg.get_by_label("Ton code d'enseignant·e").fill(prof)
            pg.get_by_role("button", name="Ouvrir mon espace").click()
            pg.locator(".cc-classe-lien-nom", has_text="Seconde 4").click()
            pg.locator(".cc-eleve").first.wait_for()
            for s in pg.locator("details").all():
                try:
                    s.evaluate("d => d.open = true")
                except Exception:
                    pass
            mesurer(pg, "enseignant/ (classe, tout ouvert)", w, m)
            pg.get_by_label("Mode projection").check()
            mesurer(pg, "enseignant/ (projection)", w, m)
            pg.get_by_label("Mode projection").uncheck()
            pg.get_by_role("link", name="Inviter les élèves (à projeter)").click()
            pg.locator(".cc-code-projete").wait_for()
            mesurer(pg, "enseignant/ (inviter)", w, m)
            # 3. l'élève : le lien de classe, puis la planque et ses onglets
            pe = ctx.new_page()
            pe.goto(BASE + "/eleve/?classe=" + cl["code"], wait_until="networkidle")
            pe.locator(".cc-classe-nom").wait_for()
            clav = C.clavier(pe) if clav_ok else None
            if clav_ok:
                pe.goto(BASE + "/eleve/?classe=" + cl["code"], wait_until="networkidle")
                pe.locator(".cc-classe-nom").wait_for()
            mesurer(pe, "eleve/ (lien de classe)", w, m, clav)
            pe.goto(BASE + "/eleve/", wait_until="networkidle")
            pe.get_by_label("Ton code", exact=True).fill(eleves[0])
            pe.get_by_role("button", name="Entrer").click()
            pe.get_by_text("Salut, Ali").wait_for()
            for onglet in ("Mon avatar", "Boutique", "Trophées", "Hauts faits", "Ma classe", "Applications", "Crédits et codes"):
                pe.get_by_role("tab", name=onglet).click()
                pe.wait_for_timeout(300)
                mesurer(pe, "eleve/ « %s »" % onglet, w, m)
            ctx.close()
    nav.close()
serveur.shutdown()
print("\nFautes de l'API stricte :", len(serveur_strict.FAUTES))
print("%d problème(s)" % len(problemes))
for pb in problemes:
    print(" -", pb)
sys.exit(1 if problemes or serveur_strict.FAUTES else 0)
