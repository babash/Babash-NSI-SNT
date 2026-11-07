#!/usr/bin/env python3
"""Extrait le texte des PDF du site (pdftotext) et y cherche des motifs sensibles.

Usage : python3 pdf_texte.py DOSSIER_DU_SITE DOSSIER_SORTIE
Affiche, pour chaque PDF : nombre de pages, nombre de mots, et les lignes suspectes.
Les noms propres trouvés (mots à majuscule répétés) sont listés pour relecture humaine.
"""
import glob
import os
import re
import subprocess
import sys

MOTIF = re.compile(r"mots? de passe|password|identifiant|login|secret|token|jeton|"
                   r"[\w.+-]+@[\w-]+\.[a-z]{2,}|eyJ[A-Za-z0-9_-]{10,}", re.I)

racine, sortie = sys.argv[1], sys.argv[2]
os.makedirs(sortie, exist_ok=True)
for pdf in sorted(glob.glob(os.path.join(racine, "**", "*.pdf"), recursive=True)):
    rel = os.path.relpath(pdf, racine)
    txt = os.path.join(sortie, rel.replace("/", "_") + ".txt")
    subprocess.run(["pdftotext", "-q", pdf, txt], check=False)
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    pages = re.search(r"Pages:\s+(\d+)", info)
    texte = open(txt, encoding="utf-8", errors="replace").read() if os.path.exists(txt) else ""
    print("%s : %s pages, %d mots" % (rel, pages.group(1) if pages else "?", len(texte.split())))
    for i, l in enumerate(texte.splitlines(), 1):
        if MOTIF.search(l):
            print("   ligne %d : %s" % (i, l.strip()[:160]))
