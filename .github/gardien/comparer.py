#!/usr/bin/env python3
"""Compare deux sorties de rendu.py (avant / après) : mesures et captures, pixel à pixel.

Usage : python3 comparer.py DOSSIER_AVANT DOSSIER_APRES
Affiche, pour chaque page, largeur et mode : écart du nombre de ressources, nouvelles erreurs,
nouveaux débordements, et la part de pixels qui diffèrent entre les deux captures.
Code de sortie 1 si une différence est trouvée.
"""
import json
import os
import sys

from PIL import Image, ImageChops

CHAMPS = ("res", "alerte", "erreurs_js", "console_erreurs", "nb_deborde", "defilement_horizontal",
          "titre", "hauteur", "largeur_contenu", "cartes")
BRUIT_PART = 0.01   # en % des pixels de la capture
BRUIT_ZONE = 40     # en pixels de côté


def charger(d):
    with open(os.path.join(d, "resultats.json"), encoding="utf-8") as f:
        return {(r["page"], r["largeur"], r["mode"]): r for r in json.load(f)["resultats"]}


def main():
    avant_d, apres_d = sys.argv[1], sys.argv[2]
    avant, apres = charger(avant_d), charger(apres_d)
    differences = 0
    for cle in sorted(set(avant) | set(apres)):
        a, b = avant.get(cle), apres.get(cle)
        etiquette = "%s %d %s" % cle
        if not a or not b:
            print(etiquette, ": présent d'un seul côté")
            differences += 1
            continue
        ecarts = ["%s %r -> %r" % (c, a.get(c), b.get(c)) for c in CHAMPS if a.get(c) != b.get(c)]
        pixels = "capture absente"
        if a.get("capture") and b.get("capture"):
            ia = Image.open(os.path.join(avant_d, a["capture"])).convert("RGB")
            ib = Image.open(os.path.join(apres_d, b["capture"])).convert("RGB")
            if ia.size != ib.size:
                pixels = "tailles différentes %s / %s" % (ia.size, ib.size)
                ecarts.append(pixels)
            else:
                diff = ImageChops.difference(ia, ib)
                boite = diff.getbbox()
                if boite:
                    n = ia.size[0] * ia.size[1] - diff.convert("L").point(lambda v: 255 if v else 0).histogram()[0]
                    part = 100.0 * n / (ia.size[0] * ia.size[1])
                    pixels = "%.4f %% de pixels différents, zone %s" % (part, boite)
                    # Bruit d'anticrénelage : quelques pixels dans une petite zone (constaté sur le
                    # logo de la barre du haut à 320 px, même entre deux rendus de la même version)
                    if part < BRUIT_PART and boite[2] - boite[0] <= BRUIT_ZONE and boite[3] - boite[1] <= BRUIT_ZONE:
                        pixels = "bruit d'anticrénelage ignoré (%s)" % pixels
                    else:
                        ecarts.append(pixels)
                else:
                    pixels = "identique"
        if ecarts:
            differences += 1
            print("%-36s DIFFÉRENT : %s" % (etiquette, " ; ".join(ecarts)))
        else:
            print("%-36s identique (%s ressources, captures %s)" % (etiquette, b.get("res"), pixels))
    print("\n%d page(s) différente(s) sur %d" % (differences, len(set(avant) | set(apres))))
    sys.exit(1 if differences else 0)


if __name__ == "__main__":
    main()
