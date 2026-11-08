#!/usr/bin/env python3
"""Où sont les différences entre deux rendus ? (Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/zones.py DOSSIER_AVANT DOSSIER_APRES [--marge-bas 400] [--tolerance 0]

Les deux dossiers sont des sorties de rendu.py (resultats.json et captures). Quand comparer.py
trouve une différence, cet outil la situe, capture par capture :
  - les hauteurs avant et après ;
  - la première ligne de pixels qui diffère, et sa distance au bas de la page « avant » : si
    seules les dernières lignes diffèrent, le changement se limite au bas de la page (le pied
    de page, par exemple) ;
  - au-dessus des MARGE derniers pixels de la page « avant » (là où se trouvait l'ancien pied
    de page) : identique, ou le nombre de pixels qui diffèrent, l'écart le plus fort (sur 255)
    et les bandes de lignes concernées (deux bandes séparées de 3 lignes au plus sont réunies).
Un pixel diffère dès qu'un de ses canaux change. Le bruit du rendu (anticrénelage, dégradés)
apparaît donc comme une bande à faible écart, 1 à 4 sur 255, invisible à l'œil : c'est au
Gardien de l'interpréter, en regardant la zone sur les deux captures, ou de l'écarter avec
--tolerance (par exemple 4).
Code de sortie 1 si une capture diffère au-dessus de la marge, ou ne peut pas être comparée
(présente d'un seul côté, sans capture, de largeur différente, ou tronquée par rendu.py).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comparer import charger  # noqa: E402
from PIL import Image, ImageChops  # noqa: E402

ECART_BANDES = 3   # lignes identiques tolérées à l'intérieur d'une bande


def bandes(masque):
    """Les bandes de lignes (y début, y fin) qui contiennent au moins un pixel différent."""
    lignes = masque.getprojection()[1]
    out, debut, prec = [], None, None
    for y, v in enumerate(lignes):
        if not v:
            continue
        if debut is not None and y - prec > ECART_BANDES + 1:
            out.append((debut, prec))
            debut = None
        if debut is None:
            debut = y
        prec = y
    if debut is not None:
        out.append((debut, prec))
    return out


def comparer_captures(ia, ib, marge, tronquee, tolerance=0):
    """Mesures d'une paire de captures de même largeur.

    Un pixel diffère quand l'écart d'au moins un de ses canaux dépasse la tolérance (une
    conversion en gris, elle, arrondirait un écart de 1 à 0)."""
    commune = min(ia.height, ib.height)
    diff = ImageChops.difference(ia.crop((0, 0, ia.width, commune)), ib.crop((0, 0, ib.width, commune)))
    r, g, b = diff.split()
    ecart = ImageChops.lighter(ImageChops.lighter(r, g), b)       # le plus grand écart des trois canaux
    masque = ecart.point(lambda v: 255 if v > tolerance else 0)
    boite = masque.getbbox()
    premiere = boite[1] if boite else None
    # Avec une capture tronquée (page de plus de 15 000 px), le bas de la page n'est pas visible :
    # toute la hauteur commune compte alors comme « au-dessus de la marge ».
    limite = commune if tronquee else max(0, min(ia.height - marge, ib.height))
    m = {"premiere": premiere, "depuis_bas": ia.height - premiere if premiere is not None else 0,
         "limite": limite, "pixels": 0, "zone": None, "bandes": [], "ecart": 0}
    if limite and boite and boite[1] < limite:
        haut = masque.crop((0, 0, masque.width, limite))
        m["pixels"] = limite * masque.width - haut.histogram()[0]
        m["zone"] = haut.getbbox()
        m["bandes"] = bandes(haut)
        m["ecart"] = ecart.crop((0, 0, ecart.width, limite)).getextrema()[1]
    return m


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("avant", help="sortie de rendu.py avant la branche")
    a.add_argument("apres", help="sortie de rendu.py après la branche")
    a.add_argument("--marge-bas", type=int, default=400, metavar="PX",
                   help="hauteur du bas de la page « avant » exclue de la comparaison (défaut : 400)")
    a.add_argument("--tolerance", type=int, default=0, metavar="N",
                   help="écart (sur 255) en dessous duquel un pixel compte comme identique (défaut : 0, "
                        "le moindre écart compte ; 4 ignore le bruit invisible du rendu)")
    o = a.parse_args()
    avant, apres = charger(o.avant), charger(o.apres)
    problemes, modifiees, pire = [], 0, 0
    for cle in sorted(set(avant) | set(apres)):
        etiquette = "%s %d %s" % cle
        ra, rb = avant.get(cle), apres.get(cle)
        if not ra or not rb:
            problemes.append(etiquette + " : présente d'un seul côté")
            continue
        if not ra.get("capture") or not rb.get("capture"):
            problemes.append(etiquette + " : capture absente")
            continue
        ia = Image.open(os.path.join(o.avant, ra["capture"])).convert("RGB")
        ib = Image.open(os.path.join(o.apres, rb["capture"])).convert("RGB")
        if ia.width != ib.width:
            problemes.append("%s : largeurs différentes (%d et %d px)" % (etiquette, ia.width, ib.width))
            continue
        tronquee = bool(ra.get("capture_tronquee") or rb.get("capture_tronquee"))
        m = comparer_captures(ia, ib, o.marge_bas, tronquee, o.tolerance)
        if m["premiere"] is None:
            debut = "aucune ligne différente sur %d px communs" % min(ia.height, ib.height)
        else:
            pire = max(pire, m["depuis_bas"])
            debut = "1re ligne différente : %5d, soit %5d px au-dessus du bas de l'ancienne page" % (m["premiere"], m["depuis_bas"])
        if m["pixels"]:
            modifiees += 1
            haut = "AU-DESSUS de la marge : %d pixels différents (écart max %d/255), zone %s, bandes %s%s" % (
                m["pixels"], m["ecart"], m["zone"], m["bandes"][:6], " …" if len(m["bandes"]) > 6 else "")
            problemes.append("%s : différences au-dessus de la marge (bandes %s)" % (etiquette, m["bandes"][:3]))
        else:
            haut = "identique au-dessus de la marge (%d px comparés)" % m["limite"]
        print("%-26s avant %5d px, après %5d px (%+d) ; %s ; %s%s" % (
            etiquette, ia.height, ib.height, ib.height - ia.height, debut, haut,
            " (capture tronquée : bas de page invisible, comparée sur toute sa hauteur)" if tronquee else ""))
    print("\n%d capture(s) sur %d diffèrent au-dessus de la marge de %d px ; plus grande distance entre une "
          "différence et le bas de l'ancienne page : %d px" % (modifiees, len(set(avant) | set(apres)), o.marge_bas, pire))
    for pb in problemes:
        print(" -", pb)
    sys.exit(1 if problemes else 0)


if __name__ == "__main__":
    main()
