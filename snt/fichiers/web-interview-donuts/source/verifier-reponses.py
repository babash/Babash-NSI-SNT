#!/usr/bin/env python3
"""Vérifie, dans le Bootstrap 5.3 du projet (projet-eleves/vendor), les faits utilisés par les
corrections du carnet de bord « Mission Reboucheur » (feuille-de-route.html).
Usage : python3 -I verifier-reponses.py"""
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
css = open(os.path.join(ICI, "..", "projet-eleves", "vendor", "bootstrap.min.css"), encoding="utf-8").read()
page = open(os.path.join(ICI, "..", "feuille-de-route.html"), encoding="utf-8").read()
faits = [
    ("mt-5 = margin-top: 3rem", r"\.mt-5\{margin-top:3rem!important\}", "margin-top: 3rem"),
    (".carousel-item caché par défaut", r"\.carousel-item\{position:relative;display:none", "display: none"),
    (".carousel-item.active affiché", r"\.carousel-item\.active\{display:block\}", ".active"),
]
erreurs = 0
for nom, motif, dans_page in faits:
    ok = re.search(motif, css) is not None and dans_page in page
    erreurs += not ok
    print(("juste : " if ok else "FAUX  : ") + nom)
print("tout est juste" if not erreurs else f"{erreurs} erreur(s)")
raise SystemExit(1 if erreurs else 0)
