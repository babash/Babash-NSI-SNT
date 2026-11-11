#!/usr/bin/env python3
"""Textes et liens affichés : ce qu'une branche ajoute ou retire, page par page (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/texte_rendu.py AVANT APRES [PAGE …] [--polices DOSSIER] [--cdn PREFIXE=DOSSIER …]

AVANT et APRES : deux copies (git archive de main et de la branche). PAGE : un chemin relatif
(par défaut : l'accueil et les rubriques de reglages.js de l'après, comme les lit le site).
Chaque page est affichée dans Chrome à 1440 px, en mode clair ; on relève les lignes du texte
rendu (innerText de #site, ou de la page) et les liens (« texte -> adresse », adresses du site
raccourcies), puis on affiche les lignes qui disparaissent (-) et celles qui apparaissent (+).
Utile pour relire ce qu'une branche change dans les listes, sans lire le code : une phrase
mal recopiée, une annexe oubliée, un lien qui change d'adresse.
Les requêtes vers d'autres sites sont bloquées (commun.externes). Code de sortie : 0.
"""
import argparse
import difflib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

EXTRAIRE = r"""() => {
  const zone = document.getElementById('site') || document.body;
  const texte = zone.innerText.split('\n').map(s => s.trim()).filter(Boolean);
  const liens = [...zone.querySelectorAll('a')].map(a => (a.textContent || '').trim().replace(/\s+/g, ' ') + ' -> ' +
    (a.getAttribute('href') || '').split(location.origin).join(''));
  return { texte, liens };
}"""


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("avant")
    a.add_argument("apres")
    a.add_argument("pages", nargs="*")
    a.add_argument("--polices", help="dossier des paquets fontsource décompressés")
    a.add_argument("--cdn", action="append", default=[], metavar="PREFIXE=DOSSIER")
    o = a.parse_args()
    pages = o.pages or [chemin for _, chemin in commun.pages_site(o.apres)]
    cdn = commun.lire_cdn(o.cdn)
    serveurs = {v: commun.servir(os.path.abspath(d)) for v, d in (("avant", o.avant), ("apres", o.apres))}
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for chemin in pages:
            res = {}
            for version, (_, base) in serveurs.items():
                ctx = nav.new_context(viewport={"width": 1440, "height": 900}, color_scheme="light")
                commun.externes(ctx, cdn, None, o.polices)
                pg = ctx.new_page()
                pg.goto(base + "/" + chemin.lstrip("/"), wait_until="load")
                pg.wait_for_timeout(800)
                res[version] = pg.evaluate(EXTRAIRE)
                ctx.close()
            print("\n== /%s" % chemin)
            for cle in ("texte", "liens"):
                diff = [l for l in difflib.unified_diff(res["avant"][cle], res["apres"][cle], lineterm="", n=0)
                        if l[:1] in "+-" and not l.startswith(("+++", "---"))]
                print("  %s : %d ligne(s) en moins, %d en plus" % (
                    cle, sum(1 for l in diff if l.startswith("-")), sum(1 for l in diff if l.startswith("+"))))
                for l in diff:
                    print("    " + l[:400])
        nav.close()
    for serveur, _ in serveurs.values():
        serveur.shutdown()


if __name__ == "__main__":
    main()
