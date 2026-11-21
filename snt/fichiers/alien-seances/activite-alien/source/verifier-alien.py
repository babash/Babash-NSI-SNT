#!/usr/bin/env python3
"""Vérifie les trois feuilles de l'activité Alien-Python par exécution réelle (Python 3.13).

1. Pour chaque « La position finale est » : le script affiché est exécuté avec des fonctions
   haut/bas/gauche/droite/colonne qui déplacent l'alien (départ en H8, grille A-O x 1-15),
   et la case obtenue doit être la première réponse attendue de la page.
2. Pour chaque « Donne les instructions » : le code de départ + la correction passe les tests
   de la page (comme le moteur : le code, puis les tests, dans le même espace), et un chemin
   faux (une case de trop vers le bas) est refusé.
Usage : python3 -I verifier-alien.py
"""
import html
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
L = "ABCDEFGHIJKLMNO"


def position(src):
    pos = {"l": 7, "c": 8}
    def bouge(dl, dc, n):
        pos["l"] += dl * n
        pos["c"] += dc * n
        assert 0 <= pos["l"] < 15 and 1 <= pos["c"] <= 15, "sortie de la grille"
    g = {"haut": lambda n=1: bouge(-1, 0, n), "bas": lambda n=1: bouge(1, 0, n),
         "gauche": lambda n=1: bouge(0, -1, n), "droite": lambda n=1: bouge(0, 1, n),
         "colonne": lambda: pos["c"]}
    exec(compile(src, "alien.py", "exec"), g)
    return L[pos["l"]] + str(pos["c"])


def moteur(code, tests):
    g = {"__name__": "__main__"}
    exec(compile(code, "alien.py", "exec"), g)
    try:
        exec(compile(tests, "tests.py", "exec"), g)
    except AssertionError as e:
        return "refusé : " + str(e)
    return "accepté"


erreurs = 0
for nom in ("index.html", "feuille-2.html", "feuille-3.html"):
    page = open(os.path.join(ICI, "..", nom), encoding="utf-8").read()
    for qid, rep, code in re.findall(r'<section class="td-q" data-type="courte" id="([^"]+)" data-reponse="([^"|]+)[^"]*"[^>]*>\s*<pre class="td-code">\n(.*?)</pre>', page, re.S):
        calc = position(html.unescape(code))
        ok = calc == rep
        erreurs += not ok
        print(f"{nom} {qid} : exécution -> {calc} ; page -> {rep} {'juste' if ok else 'FAUX'}")
    for qid, dep, tests, corr in re.findall(r'id="([^"]+)" data-fichier="alien.py">.*?<pre class="td-depart">\n(.*?)</pre>\s*<script type="text/x-python" class="td-tests">\n(.*?)</script>.*?data-verifier="correction">\n(.*?)</pre>', page, re.S):
        dep, corr = html.unescape(dep), html.unescape(corr)
        r1 = moteur(corr, tests)
        r2 = moteur(corr + "\nbas(1)\n", tests)
        ok = r1 == "accepté" and r2.startswith("refusé")
        erreurs += not ok
        print(f"{nom} {qid} : correction {r1} ; chemin faux {r2} {'juste' if ok else 'FAUX'}")
        assert corr.startswith(dep), "la correction reprend le code de départ"
print("tout est juste" if not erreurs else f"{erreurs} erreur(s)")
raise SystemExit(1 if erreurs else 0)
