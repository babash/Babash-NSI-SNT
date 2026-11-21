#!/usr/bin/env python3
"""Réattribue en une fois les bandeaux de tous les TD du dépôt (T123b).

Usage (à la racine du dépôt) :
  python3 -I charte/reattribuer-bandeaux.py             montre ce qui changerait (rien n'est écrit)
  python3 -I charte/reattribuer-bandeaux.py --appliquer écrit les pages

Les TD convertis en parallèle sur plusieurs branches ont pris les mêmes bandeaux. Ce script les répartit
à parts égales : les pages sont rangées d'après l'empreinte de leur identifiant (SHA-256), puis reçoivent
1, 2, 3, 4, 1, 2… dans cet ordre (une répartition exacte, à une page près, et toujours la même pour le
même ensemble de pages). Les feuilles d'un même TD (même dossier) prennent des bandeaux différents quand
c'est possible, puisqu'elles se suivent. Le margouillat caché dans le bandeau garde sa cachette (b1 à b4)
et prend la place de cette cachette dans le nouveau dessin. Les contrôles (bandeau de 20 mm) aussi.

Seuls changent : data-bandeau, le style du margouillat du bandeau et le commentaire « paysage n° N ».
Les démonstrations de charte/ et les copies de .claude/ ne sont pas touchées.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
spec = importlib.util.spec_from_file_location("nouveau_td", os.path.join(ICI, "nouveau-td.py"))
nt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nt)
RE_BD = re.compile(r'(class="td-bandeau[^"]*" data-bandeau=")([1-4])(")')


def pages():
    for dossier, sous, fichiers in os.walk(RACINE):
        if nt.ignorer(dossier):
            sous[:] = []
            continue
        for f in sorted(fichiers):
            if not f.endswith(".html"):
                continue
            chemin = os.path.join(dossier, f)
            try:
                t = open(chemin, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            i = re.search(r'data-td="([^"]+)"', t)
            if i and RE_BD.search(t) and "{{" not in t:
                yield chemin, i.group(1), t


def main():
    appliquer = "--appliquer" in sys.argv
    places = json.load(open(os.path.join(RACINE, "assets", "td", "places-margouillat.json"), encoding="utf-8"))
    liste = sorted(pages(), key=lambda x: hashlib.sha256(x[1].encode()).hexdigest())
    nouveau, compte, par_dossier = {}, {1: 0, 2: 0, 3: 0, 4: 0}, {}
    for chemin, ident, t in liste:
        dossier = os.path.dirname(chemin)
        pris = par_dossier.setdefault(dossier, set())
        # le moins utilisé, en évitant le bandeau d'une autre feuille du même dossier
        b = min((1, 2, 3, 4), key=lambda n: (n in pris, compte[n], n))
        compte[b] += 1
        pris.add(b)
        nouveau[chemin] = b
    changes = 0
    for chemin, ident, t in liste:
        b = nouveau[chemin]
        ancien = int(RE_BD.search(t).group(2))
        rel = os.path.relpath(chemin, RACINE)
        if ancien == b:
            continue
        changes += 1
        u = RE_BD.sub(lambda m: m.group(1) + str(b) + m.group(3), t, count=1)
        u = re.sub(r"paysage n° [1-4]", f"paysage n° {b}", u, count=1)
        # le margouillat caché dans le bandeau : même cachette, place du nouveau dessin
        m = re.search(r'<span class="td-margouillat" data-cachette="b([1-4])" style="([^"]*)"', u)
        if m:
            k = int(m.group(1))
            lieux = places[str(b)]
            p = lieux[min(k, len(lieux)) - 1]
            s = re.search(r"--s:(-?1)", m.group(2))
            style = f'--x:{p["x"]}%;--y:{p["y"]}%;--r:{p["r"]}deg;--l:{p["l"]}%;--s:{s.group(1) if s else 1}'
            u = u[:m.start(2)] + style + u[m.end(2):]
        print(f"{rel} : bandeau {ancien} -> {b}")
        if appliquer:
            open(chemin, "w", encoding="utf-8").write(u)
    print(f"{len(liste)} TD ; répartition : " + ", ".join(f"bandeau {n} : {compte[n]}" for n in (1, 2, 3, 4))
          + f" ; {changes} page(s) " + ("modifiée(s)" if appliquer else "à modifier (--appliquer pour écrire)"))


if __name__ == "__main__":
    main()
