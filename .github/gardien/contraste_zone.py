#!/usr/bin/env python3
"""Le contraste le plus faible des textes d'une zone de la page (Gardien), le pied de page par défaut.

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/contraste_zone.py URL_DE_BASE --racine DOSSIER_DU_SITE
          [--zone "p.mentions"] [--pages accueil,snt] [--polices DOSSIER_FONTSOURCE]
          [--largeurs 320,1440] [--modes light,dark]

Même mesure que contrastes.py (couleur du texte comparée aux pixels réellement affichés
derrière lui, 10e centile du fond), mais limitée aux textes que contient la zone (sélecteur
CSS ; par défaut p.mentions, le pied de page de T19), et sans seuil : pour chaque page (accueil
et rubriques de reglages.js, ou celles de --pages), largeur et mode, l'outil donne le nombre de
textes de la zone et le plus faible contraste (rapport, élément, texte, taille, couleur).
contrastes.py ne signale que les textes sous le seuil ; ici on connaît la marge de la zone, par
exemple avant que la charte ne porte le seuil du texte courant à 7:1.
Code de sortie 1 si la zone est absente d'une page, ou si aucun de ses textes n'a pu être mesuré.
"""
import argparse
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
import contrastes  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

SANS_SEUIL = float("inf")   # contrastes.mesurer garde alors chaque texte, avec son rapport


def mesurer_zone(nav, url, zone, largeur, mode, polices):
    ctx = nav.new_context(viewport={"width": largeur, "height": 900}, color_scheme=mode,
                          reduced_motion="reduce", device_scale_factor=1)
    commun.polices(ctx, polices)
    page = ctx.new_page()
    try:
        page.goto(url, wait_until="networkidle", timeout=45000)
        page.evaluate("() => document.fonts ? document.fonts.ready.then(() => 1) : 1")
        page.wait_for_timeout(300)
        presentes = page.evaluate("s => document.querySelectorAll(s).length", zone)
        page.add_style_tag(content=contrastes.MASQUER)
        page.wait_for_timeout(150)
        image = Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB")
        page.evaluate("() => document.querySelectorAll('style').forEach(s => { if (s.textContent.includes('transparent !important')) s.remove(); })")
        page.wait_for_timeout(100)
        _, textes = contrastes.mesurer(page, image, SANS_SEUIL, SANS_SEUIL, zone=zone)
    finally:
        ctx.close()
    return presentes, sorted(textes, key=lambda t: t["ratio"])


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("base", help="adresse du site servi (http://127.0.0.1:8000, par exemple)")
    a.add_argument("--racine", required=True, help="la copie du site servie (pour la liste des pages)")
    a.add_argument("--zone", default="p.mentions", help="sélecteur CSS de la zone (défaut : p.mentions)")
    a.add_argument("--pages", help="pages à mesurer, séparées par des virgules (défaut : accueil et toutes les rubriques)")
    a.add_argument("--polices", help="paquets fontsource décompressés (voir controler.py --polices)")
    a.add_argument("--largeurs", default="320,1440")
    a.add_argument("--modes", default="light,dark")
    o = a.parse_args()
    pages = commun.pages_site(o.racine)
    if o.pages:
        voulues = o.pages.split(",")
        inconnues = [p for p in voulues if p not in dict(pages)]
        if inconnues:
            a.error("pages inconnues : %s (possibles : %s)" % (", ".join(inconnues), ", ".join(dict(pages))))
        pages = [(p, c) for p, c in pages if p in voulues]
    problemes, plus_faible = [], None
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for page_id, chemin in pages:
            for w in [int(x) for x in o.largeurs.split(",")]:
                for m in o.modes.split(","):
                    et = "%s %d %s" % (page_id, w, m)
                    presentes, textes = mesurer_zone(nav, o.base.rstrip("/") + "/" + chemin, o.zone, w, m, o.polices)
                    if not presentes:
                        print("%-24s zone « %s » absente" % (et, o.zone))
                        problemes.append(et + " : zone absente")
                        continue
                    if not textes:
                        print("%-24s aucun texte mesuré dans la zone" % et)
                        problemes.append(et + " : aucun texte mesuré")
                        continue
                    t = textes[0]
                    print("%-24s %3d textes ; le plus faible : %.2f:1 (%s « %s », %.1f px, %s)" % (
                        et, len(textes), t["ratio"], t["element"], t["texte"][:30], t["taille"], t["couleur"]))
                    if plus_faible is None or t["ratio"] < plus_faible[0]:
                        plus_faible = (t["ratio"], et, t["texte"][:30])
        nav.close()
    if plus_faible:
        print("\nZone « %s » : contraste le plus faible %.2f:1 (%s, « %s »)" % ((o.zone,) + plus_faible))
    for pb in problemes:
        print(" -", pb)
    sys.exit(1 if problemes or not plus_faible else 0)


if __name__ == "__main__":
    main()
