#!/usr/bin/env python3
"""Impression A4 des documents déposés (Gardien).

Usage : python3 impression.py URL_DE_BASE DOSSIER_SORTIE --racine DOSSIER_DU_SITE
                              [--polices DOSSIER_FONTSOURCE] [FICHIER.html …]

Pour chaque page HTML de */fichiers/ (ou celles données) :
  - imprime en PDF A4 (format de page du document, arrière-plans) et compte les pages ;
  - si le document est fait de feuilles <section class="sheet">, vérifie qu'il y a autant de
    pages PDF que de feuilles et qu'aucune feuille ne déborde (contenu plus haut que la feuille) ;
  - relève les éléments qui dépassent la largeur de la page imprimée.
Écrit les PDF dans DOSSIER_SORTIE ; code de sortie 1 si un problème.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

MESURES = r"""() => {
  const feuilles = [...document.querySelectorAll('section.sheet, .sheet')];
  const debordes = feuilles.map((f, i) => ({ i: i + 1, h: f.scrollHeight, c: f.clientHeight }))
    .filter(x => x.h > x.c + 2);
  const W = document.documentElement.clientWidth;
  const larges = [...document.body.querySelectorAll('*')].filter(e => {
    const r = e.getBoundingClientRect(); return r.width && r.right > W + 2;
  }).slice(0, 5).map(e => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : ''));
  return { feuilles: feuilles.length, debordes, larges };
}"""


def pages_pdf(chemin):
    with open(chemin, "rb") as f:
        donnees = f.read()
    return len(re.findall(rb"/Type\s*/Page[^s]", donnees))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("base")
    a.add_argument("sortie")
    a.add_argument("--racine", required=True)
    a.add_argument("--polices")
    a.add_argument("fichiers", nargs="*")
    o = a.parse_args()
    os.makedirs(o.sortie, exist_ok=True)
    cibles = o.fichiers or [rel for rel, _ in commun.pages_fichiers(o.racine)]
    problemes = []
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for rel in cibles:
            ctx = nav.new_context(viewport={"width": 1200, "height": 900})
            commun.polices(ctx, o.polices)
            page = ctx.new_page()
            try:
                page.goto(o.base.rstrip("/") + "/" + rel, wait_until="networkidle", timeout=45000)
            except Exception as e:
                print("%s : chargement incomplet (%s)" % (rel, str(e)[:80]))
            page.evaluate("() => document.fonts ? document.fonts.ready.then(() => 1) : 1")
            page.emulate_media(media="print")
            page.wait_for_timeout(500)
            m = page.evaluate(MESURES)
            sortie_pdf = os.path.join(o.sortie, rel.replace("/", "_") + ".pdf")
            page.pdf(path=sortie_pdf, format="A4", prefer_css_page_size=True, print_background=True)
            n = pages_pdf(sortie_pdf)
            etat = []
            if m["feuilles"] and n != m["feuilles"]:
                etat.append("%d pages PDF pour %d feuilles" % (n, m["feuilles"]))
            if m["debordes"]:
                etat.append("feuilles qui débordent : %s" % ", ".join("n° %d (%d px pour %d)" % (d["i"], d["h"], d["c"]) for d in m["debordes"]))
            if m["larges"]:
                etat.append("trop large : %s" % ", ".join(m["larges"]))
            print("%-58s %2d pages PDF, %2d feuilles  %s" % (rel, n, m["feuilles"], "; ".join(etat) or "ok"))
            if etat:
                problemes.append(rel + " : " + "; ".join(etat))
            ctx.close()
        nav.close()
    print("\n%d problème(s)" % len(problemes))
    for pb in problemes:
        print(" -", pb)
    sys.exit(1 if problemes else 0)


if __name__ == "__main__":
    main()
