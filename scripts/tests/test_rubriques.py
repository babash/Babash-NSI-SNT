#!/usr/bin/env python3
"""Tests des rubriques et de l'accueil, qui lisent la vitrine et les fiches (T51b), dans Chromium.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_rubriques.py [--racine DOSSIER_DU_DEPOT] [--travail DOSSIER]

Chaque cas prépare une copie de travail (donnees/ copié, le reste relié par des liens symboliques), la modifie,
y construit la bibliothèque (scripts/construire_bibliotheque.py) et la sert en local :
  - telle quelle : chaque rubrique montre les ressources de la vitrine visibles de l'extérieur, dans l'ordre,
    avec les ancres des sections ; l'accueil a une carte par rubrique ; aucune erreur JavaScript ;
  - la vitrine modifiée (deux ressources inversées, une section libre renommée, une section déplacée) : la page suit ;
  - une ressource placée dont tous les documents sont cachés de l'extérieur : elle n'apparaît pas ;
  - donnees/bibliotheque.json absent : un message clair, le pied de page et ses mentions restent ;
  - sans JavaScript : le message de chaque page et ses mentions (licences, « Code source sur GitHub »).
Il faut Playwright et Chromium. Code de retour : 0 si tous les cas passent, 1 sinon.
"""
import argparse
import functools
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEFAUT = os.path.dirname(os.path.dirname(ICI))
CONSTRUITS = {"bibliotheque.json", "bibliotheque-complete.json", "bibliotheque-textes.json"}
echecs = []
cas = [0]


def verifier(titre, ok, detail=""):
    cas[0] += 1
    print(("  ok     " if ok else "  ÉCHEC  ") + titre)
    if not ok:
        echecs.append(titre)
        if detail:
            print("         " + str(detail)[:1200])


class Discret(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def copie(racine, travail, modifier=None, construire=True):
    d = tempfile.mkdtemp(prefix="test-rubriques-", dir=travail)
    for nom in os.listdir(racine):
        if nom not in (".git", "donnees"):
            os.symlink(os.path.join(racine, nom), os.path.join(d, nom))
    source = os.path.join(racine, "donnees")
    shutil.copytree(source, os.path.join(d, "donnees"), ignore=lambda dos, noms: [x for x in noms if dos == source and x in CONSTRUITS])
    if modifier:
        modifier(d)
    if construire:
        r = subprocess.run([sys.executable, "-B", os.path.join(racine, "scripts", "construire_bibliotheque.py"), "--racine", d, "--sans-textes"],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("construction impossible :\n" + r.stdout + r.stderr)
    return d


class Serveur:
    def __init__(self, dossier):
        self.s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Discret, directory=dossier))
        threading.Thread(target=self.s.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.s.server_address[1]}"

    def fermer(self):
        self.s.shutdown()


def lire(d, *p):
    with open(os.path.join(d, *p), encoding="utf-8") as f:
        return json.load(f)


def ecrire(d, obj, *p):
    with open(os.path.join(d, *p), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def attendu(d, rub):
    """Les titres attendus d'une rubrique, dans l'ordre : ressources de la vitrine visibles de l'extérieur."""
    out = []
    for s in rub["sections"]:
        for rid in s["ressources"] + [x for ss in s.get("sous_sections", []) for x in ss["ressources"]]:
            f = lire(d, "donnees", "ressources", rid + ".json")
            if any(doc.get("visible", {}).get("exterieur") for doc in f["documents"]):
                out.append(f["titre"])
    return out


def ouvrir(nav, url, js=True):
    ctx = nav.new_context(java_script_enabled=js)
    ctx.route(re.compile(r"^https://fonts\.(googleapis|gstatic)\.com/.*"), lambda r: r.fulfill(status=200, body=""))
    page = ctx.new_page()
    erreurs = []
    page.on("pageerror", lambda e: erreurs.append(str(e)))
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(200)
    return ctx, page, erreurs


def titres(page):
    return [t.strip() for t in page.locator("li.res .titre").all_inner_texts()]


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--racine", default=RACINE_DEFAUT)
    p.add_argument("--travail")
    a = p.parse_args()
    racine = os.path.abspath(a.racine)
    travail = a.travail or tempfile.mkdtemp(prefix="test-rubriques-")
    os.makedirs(travail, exist_ok=True)

    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        print("Telle quelle")
        d = copie(racine, travail)
        srv = Serveur(d)
        v = lire(d, "donnees", "vitrine.json")
        for rub in v["rubriques"]:
            ctx, page, erreurs = ouvrir(nav, f"{srv.base}/{rub['id']}/")
            vus, voulus = titres(page), attendu(d, rub)
            verifier(f"{rub['id']} : {len(vus)} ressources, celles de la vitrine dans l'ordre", vus == voulus, (vus, voulus))
            ancres = [s.get("id") for s in rub["sections"] if s.get("id")]
            ids = page.evaluate("[...document.querySelectorAll('section.theme')].map(s => s.id)")
            verifier(f"{rub['id']} : une section par section de la vitrine, ancres des sections libres gardées",
                     len(ids) == len(rub["sections"]) and all(x in ids for x in ancres), ids)
            verifier(f"{rub['id']} : ni erreur affichée ni erreur JavaScript", page.locator(".alerte").count() == 0 and not erreurs, erreurs)
            ctx.close()
        ctx, page, erreurs = ouvrir(nav, f"{srv.base}/")
        cartes = page.locator(".noeud-nom").all_inner_texts()
        verifier("accueil : une carte par rubrique de la vitrine, dans l'ordre", cartes == [r["titre"] for r in v["rubriques"]], cartes)
        nav_ = page.locator(".nav a").all_inner_texts()
        verifier("accueil : le menu suit la vitrine, puis Bibliothèque",
                 [x.strip() for x in nav_] == [r.get("court") or r["titre"] for r in v["rubriques"]] + ["Bibliothèque"], nav_)
        page.fill(".hero .recherche", "cybercase")
        page.wait_for_timeout(200)
        verifier("accueil : la recherche trouve dans les rubriques", page.locator("li.res").count() >= 1)
        verifier("accueil : aucune erreur JavaScript", not erreurs, erreurs)
        ctx.close()
        srv.fermer()

        print("Vitrine modifiée")
        def modifier(dd):
            vv = lire(dd, "donnees", "vitrine.json")
            r = vv["rubriques"][0]
            s = next(x for x in r["sections"] if len(x["ressources"]) >= 2)
            s["ressources"][0], s["ressources"][1] = s["ressources"][1], s["ressources"][0]
            libre = next(x for x in r["sections"] if x.get("titre"))
            libre["titre"] = "Section renommée dans l'admin"
            r["sections"].append(r["sections"].pop(0))
            ecrire(dd, vv, "donnees", "vitrine.json")
        d = copie(racine, travail, modifier)
        srv = Serveur(d)
        vv = lire(d, "donnees", "vitrine.json")
        r = vv["rubriques"][0]
        ctx, page, erreurs = ouvrir(nav, f"{srv.base}/{r['id']}/")
        verifier("deux ressources inversées et une section déplacée : la page suit", titres(page) == attendu(d, r))
        h2 = page.locator("section.theme h2").all_inner_texts()
        verifier("section libre renommée : nouveau titre", any("Section renommée dans l'admin" in x for x in h2), h2)
        ctx.close()
        srv.fermer()

        print("Ressource cachée de l'extérieur")
        cible = {}
        def cacher(dd):
            vv = lire(dd, "donnees", "vitrine.json")
            rid = next(x for x in vv["rubriques"][0]["sections"][0]["ressources"])
            f = lire(dd, "donnees", "ressources", rid + ".json")
            for doc in f["documents"]:
                doc["visible"]["exterieur"] = False
            ecrire(dd, f, "donnees", "ressources", rid + ".json")
            cible["titre"] = f["titre"]
        d = copie(racine, travail, cacher)
        srv = Serveur(d)
        r = lire(d, "donnees", "vitrine.json")["rubriques"][0]
        ctx, page, erreurs = ouvrir(nav, f"{srv.base}/{r['id']}/")
        verifier("tous ses documents cachés de l'extérieur : la ressource n'apparaît pas",
                 cible["titre"] not in titres(page) and titres(page) == attendu(d, r))
        ctx.close()
        srv.fermer()

        print("Bibliothèque absente")
        d = copie(racine, travail, construire=False)
        srv = Serveur(d)
        for chemin in ("snt/", ""):
            ctx, page, erreurs = ouvrir(nav, f"{srv.base}/{chemin}")
            alerte = page.locator(".alerte").inner_text() if page.locator(".alerte").count() else ""
            verifier(f"{chemin or 'accueil'} : message clair (« Les ressources n'ont pas pu s'afficher »)",
                     "Les ressources n'ont pas pu s'afficher" in alerte and "donnees/bibliotheque.json" in alerte, alerte)
            verifier(f"{chemin or 'accueil'} : le pied de page et le lien « Code source sur GitHub » restent",
                     page.locator(".pied a", has_text="Code source sur GitHub").count() == 1 and not erreurs, erreurs)
            ctx.close()
        srv.fermer()

        print("Sans JavaScript")
        d = copie(racine, travail)
        srv = Serveur(d)
        for chemin in ("", "snt/", "nsi-premiere/", "nsi-terminale/", "pp/", "autres/"):
            ctx, page, _ = ouvrir(nav, f"{srv.base}/{chemin}", js=False)
            texte = page.locator("body").inner_text()
            verifier(f"{chemin or 'accueil'} sans JavaScript : le message, les licences et « Code source sur GitHub »",
                     "JavaScript" in texte and "CC BY-SA 4.0" in texte and page.locator("a", has_text="Code source sur GitHub").count() >= 1, texte[:300])
            ctx.close()
        srv.fermer()
        nav.close()

    if not a.travail:
        shutil.rmtree(travail, ignore_errors=True)
    print(f"\n{cas[0]} cas, {len(echecs)} échec(s)")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
