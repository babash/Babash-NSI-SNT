#!/usr/bin/env python3
"""Vérifie les trois feuilles de l'activité Alien-Python par exécution réelle (Python 3.13).

1. Pour chaque « La position finale est » : le script affiché est exécuté avec des fonctions
   haut/bas/gauche/droite/colonne qui déplacent l'alien (départ en H8, grille A-O x 1-15),
   et la case obtenue doit être la première réponse attendue de la page.
2. Pour chaque « Donne les instructions » : le préambule caché de la page (script.td-preambule :
   la position de départ et les fonctions de déplacement), puis la correction, passe les tests
   de la page (comme le moteur : préambule, code, puis tests, dans le même espace), et un chemin
   faux (une case de trop vers le bas) est refusé. Aucun code de départ n'est montré à l'élève.
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


def moteur(pre, code, tests):
    g = {"__name__": "__main__"}
    exec(compile(pre, "preambule.py", "exec"), g)
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
    pre = re.findall(r'<script type="text/x-python" class="td-preambule">\n(.*?)</script>', page, re.S)
    questions = re.findall(r'id="([^"]+)" data-fichier="alien.py"[^>]*>(.*?)</section>', page, re.S)
    for qid, corps in questions:
        assert len(pre) == 1, "un seul préambule caché, pour toute la page"
        assert "td-depart" not in corps and "global" not in corps, qid + " : la mécanique ne doit pas être montrée (règle R1)"
        tests = re.search(r'<script type="text/x-python" class="td-tests">\n(.*?)</script>', corps, re.S).group(1)
        corr = html.unescape(re.search(r'data-verifier="correction">\n(.*?)</pre>', corps, re.S).group(1))
        r1 = moteur(pre[0], corr, tests)
        r2 = moteur(pre[0], corr + "\nbas(1)\n", tests)
        ok = r1 == "accepté" and r2.startswith("refusé")
        erreurs += not ok
        print(f"{nom} {qid} : correction {r1} ; chemin faux {r2} {'juste' if ok else 'FAUX'}")
print("tout est juste" if not erreurs else f"{erreurs} erreur(s)")
raise SystemExit(1 if erreurs else 0)
