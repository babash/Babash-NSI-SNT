#!/usr/bin/env python3
"""Vérifie, par le calcul, les réponses attendues de la feuille « Décimal et binaire » (index.html).

Usage : python3 -I verifier-reponses.py   (depuis n'importe où)
"""
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
page = open(os.path.join(ICI, "..", "index.html"), encoding="utf-8").read()
rep = dict(re.findall(r'id="(q\d+)" data-reponse="([^"]*)"', page))

binaire_vers_decimal = {"q1": "0111", "q2": "1000", "q3": "1111", "q4": "1000 0001", "q5": "0001 1001", "q6": "0100 0011"}
decimal_vers_binaire = {"q7": 12, "q8": 64, "q9": 68, "q10": 35}
erreurs = 0
for q, b in binaire_vers_decimal.items():
    calcule = int(b.replace(" ", ""), 2)
    ok = rep[q].split("|")[0] == str(calcule)
    erreurs += not ok
    print(f"{q} : {b} -> {calcule} ; page : {rep[q]} {'juste' if ok else 'FAUX'}")
for q, d in decimal_vers_binaire.items():
    calcule = bin(d)[2:]
    ok = rep[q].split("|")[0] == calcule
    erreurs += not ok
    print(f"{q} : {d} -> {calcule} (sur 8 bits : {d:08b}) ; page : {rep[q]} {'juste' if ok else 'FAUX'}")
print(f"q12 : un octet = {len(format(255, 'b'))} bits ; page : {rep['q12']}")
erreurs += rep["q12"].split("|")[0] != "8"
print("tout est juste" if not erreurs else f"{erreurs} erreur(s)")
raise SystemExit(1 if erreurs else 0)
