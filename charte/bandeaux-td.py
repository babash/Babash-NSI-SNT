#!/usr/bin/env python3
"""Bandeaux des TD, style « Signal pirate » (T123) : dessins originaux, vectoriels, sans nom de lieu.

Usage (à la racine du dépôt) :
    python3 -I charte/bandeaux-td.py

Écrit dans assets/td/ :
- bandeau-1.svg … bandeau-4.svg : les bandeaux des TD, 210 x 28 mm (repère 840 x 112, 4 unités par mm) ;
- bandeau-N-controle.svg : la variante de 20 mm des contrôles (repère 840 x 80) ;
- bandeau-N-obscur.svg, bandeau-N-controle-obscur.svg : les mêmes pour l'écran obscur (encre claire, néons) ;
- margouillat.svg, margouillat-obscur.svg : le clin d'œil, posé à part (sa place dépend de la feuille) ;
- marge.svg, marge-obscur.svg : le décor des marges de l'écran large (pistes de circuit, gris) ;
- places-margouillat.json : les cachettes du margouillat dans chaque bandeau (lu par charte/nouveau-td.py).

Les quatre paysages (choix de l'enseignant du 21/11) :
1. le cône vu de la baie (Choungui, baie de Kani)       + B : un téléphérique de pirogues ;
2. l'îlot de sable blanc dans le lagon                  + A : un feu rouge dans le lagon ;
3. la ville, le mont et la barge (Mamoudzou)            + A : la barge-drone ;
4. le baobab de plage                                   + A : paraboles et lampions.
Aucun nom de lieu n'est écrit : les élèves devinent.

Les emplacements (repère du bandeau de 28 mm) :
- titre, niveau et chapitre : x < 440, y < 80 (rien du paysage n'y monte) ;
- le sujet du paysage : x 440 à 716 ;
- le QR code du cours-quiz : x > 716, y < 84 (cadre blanc posé par la page).
Dans la variante de 20 mm : titre x < 420 ; paysage réduit à droite ; QR x > 760.

Matière : trait fin, trame 1 bit en vrais petits carrés vectoriels, néons décalés qui débordent, aucun aplat sombre.
"""
import json
import math
import os
import random

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(os.path.dirname(ICI), "assets", "td")

EN, ROSE, CYAN, JAUNE, VERT = "#121016", "#FF2E97", "#00D8F5", "#FFE600", "#2FA84F"
BLANC = "#fff"
W, H = 840, 120          # repère de dessin (la v5 faisait 30 mm) ; le bandeau en garde 112 de haut
HB = 112                  # 28 mm
OBSCUR = {EN: "#ECE8F5", BLANC: "#0E0C14", "#ffffff": "#0E0C14"}

_n = [0]


def uid(p):
    _n[0] += 1
    return f"{p}{_n[0]}"


# ------------------------------------------------------------------ outils de dessin
def points(x, y, w, h, motif="25"):
    """Trame en vrais petits carrés (un motif SVG serait rasterisé dans le PDF)."""
    d = []
    for j in range(int(h)):
        yy = y + j
        if motif == "50":
            xs = range(int(x) + j % 2, int(x + w), 2)
        elif motif == "25":
            if j % 2:
                continue
            xs = range(int(x) + (j // 2) % 2, int(x + w), 2)
        else:  # 12
            if j % 2:
                continue
            xs = range(int(x) + (j // 2 % 2) * 2, int(x + w), 4)
        d.extend(f"M{xx} {yy:.0f}h1v1h-1z" for xx in xs)
    return d


def trame(clip, x, y, w, h, motif="12"):
    cid = uid("t")
    return (f'<clipPath id="{cid}"><path d="{clip}"/></clipPath>'
            f'<path clip-path="url(#{cid})" d="{"".join(points(x, y, w, h, motif))}" fill="{EN}"/>')


def neon(d, couleur=CYAN, dx=2.2, dy=-1.6, ep=1.6):
    return f'<path d="{d}" fill="none" stroke="{couleur}" stroke-width="{ep}" stroke-linejoin="round" transform="translate({dx},{dy})"/>'


def trait(d, ep=1.1, plein="none", extra="", encre=EN):
    return f'<path d="{d}" fill="{plein}" stroke="{encre}" stroke-width="{ep}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def g(contenu, tx, ty, k):
    return f'<g transform="translate({tx:.1f},{ty:.1f}) scale({k})">{contenu}</g>'


def eau(y0, y1, graine, x0=0, x1=W, dens=1.0):
    rd = random.Random(graine)
    s, y = [], y0
    while y < y1:
        x = x0 + rd.randint(0, 24)
        while x < x1:
            L = rd.randint(8, 30) * (1 + (y - y0) / 50)
            if rd.random() < .6 * dens:
                s.append(f"M{x:.0f} {y:.1f}h{min(L, x1 - x):.0f}")
            x += L + rd.randint(8, 26)
        y += 3.4 + (y - y0) * .1
    return trait("".join(s), .7)


def collines(y, graine, x0=0, x1=W, amp=4):
    rd = random.Random(graine)
    pts, x = [], x0
    while x <= x1:
        pts.append((x, y - rd.uniform(1, amp)))
        x += rd.randint(30, 70)
    pts.append((x1, y - 2))
    d = f"M{x0} {y}" + "".join(f"L{a:.0f} {b:.1f}" for a, b in pts) + f"L{x1} {y}Z"
    ligne = "M" + "L".join(f"{a:.0f} {b:.1f}" for a, b in pts)
    return trame(d, x0, y - amp - 2, x1 - x0, amp + 4, "12") + trait(ligne, .8)


def arbres(y, xs, graine):
    rd = random.Random(graine)
    return trait("".join(f"M{x:.0f} {y - rd.uniform(0, 2.5):.1f}a3 3 0 0 1 6 0" for x in xs), .6)


def _cocotier(x, y, h, pench, graine):
    rd = random.Random(graine)
    tx, ty = x + pench, y - h
    s = [trait(f"M{x} {y}Q{x + pench * .2:.0f} {y - h * .55:.0f} {tx} {ty}", 3.2)]
    s.append(trait("".join(f"M{x + pench * k / 8:.1f} {y - h * k / 8:.1f}l4 1" for k in range(1, 8)), .7))
    for a in (-160, -130, -100, -70, -40, -10, 15):
        r = math.radians(a + rd.uniform(-8, 8))
        L = rd.uniform(26, 38)
        ex, ey = tx + L * math.cos(r), ty + L * math.sin(r) + 14
        cx, cy = tx + L * .5 * math.cos(r), ty + L * .5 * math.sin(r) - 8
        s.append(trait(f"M{tx} {ty}Q{cx:.0f} {cy:.0f} {ex:.0f} {ey:.0f}", 1.4))
        for k in range(1, 6):
            t = k / 6
            px = (1 - t) ** 2 * tx + 2 * (1 - t) * t * cx + t * t * ex
            py = (1 - t) ** 2 * ty + 2 * (1 - t) * t * cy + t * t * ey
            s.append(trait(f"M{px:.1f} {py:.1f}l{3 * math.cos(r + 1.2):.1f} 6", .7))
    s.append(f'<circle cx="{tx - 2}" cy="{ty + 3}" r="2.4" fill="{EN}"/><circle cx="{tx + 3}" cy="{ty + 4}" r="2.2" fill="{EN}"/>')
    return "".join(s)


def cocotier(x, y, k=.5, pench=14, graine=1):
    return g(_cocotier(0, 0, 58, pench, graine), x, y, k)


def _pirogue(L=96):
    """Pirogue à balancier de trois quarts : coque effilée, un flotteur d'un seul côté, deux traverses."""
    x = y = 0
    s = []
    coque = f"M{x} {y}Q{x + L * .5} {y + 13} {x + L} {y - 4}L{x + L - 6} {y + 2}Q{x + L * .5} {y + 20} {x + 8} {y + 6}Z"
    s.append(neon(coque, ROSE, 2.4, 1.4) + trait(coque, 1.4, BLANC))
    s.append(trait(f"M{x + 10} {y + 3}Q{x + L * .5} {y + 15} {x + L - 10} {y - 1}", .7))
    s.append(trame(coque, x, y - 6, L, 28, "25"))
    fl = f"M{x + 26} {y - 26}Q{x + L * .5} {y - 20} {x + L - 30} {y - 30}"
    s.append(trait(fl, 3.4) + trait(fl, 1.2, encre=BLANC))
    for t in (.3, .66):
        xa = x + L * t
        ya = y + 4 + 9 * math.sin(math.pi * t)
        s.append(trait(f"M{xa:.0f} {ya:.0f}Q{xa - 4:.0f} {ya - 26:.0f} {xa - 10:.0f} {ya - 34:.0f}", 2))
    s.append(trait(f"M{x + L * .45} {y + 2}l46 -18", 1.8) + trait(f"M{x + L * .45 + 46} {y - 16}l9 -4l-2 6z", 1, EN))
    return "".join(s)


def pirogue(x, y, k=.45):
    return g(_pirogue(96), x, y, k)


def _barge(L=210):
    """Barge amphidrome : coque basse, rampes relevées aux deux bouts, salon des passagers, passerelle."""
    x = y = 0
    s = []
    coque = f"M{x} {y}L{x + 12} {y + 14}H{x + L - 12}L{x + L} {y}Z"
    s.append(neon(f"M{x} {y}L{x + 12} {y + 14}H{x + L - 12}L{x + L} {y}", ROSE, 2.4, 1.6, 1.8))
    s.append(trait(coque, 1.5, BLANC) + trame(coque, x, y, L, 15, "25"))
    s.append(trait(f"M{x - 6} {y - 12}L{x + 4} {y}M{x + L + 6} {y - 12}L{x + L - 4} {y}", 2.2))
    s.append(trait(f"M{x + 4} {y}H{x + L - 4}", 1.6))
    for cx in range(x + 16, x + L - 30, 24):
        if x + L * .34 < cx < x + L * .64:
            continue
        s.append(trait(f"M{cx} {y}v-7h4l3 -4h10l3 4h3v7z", 1, BLANC))
    m = x + L * .5
    s.append(trait(f"M{m - 32} {y}V{y - 20}H{m + 32}V{y}", 1.4, BLANC))
    s.append(trait("".join(f"M{m - 27 + k * 9} {y - 15}h5v6h-5z" for k in range(7)), .8))
    s.append(trait(f"M{m - 15} {y - 20}V{y - 33}H{m + 15}V{y - 20}M{m - 11} {y - 28}H{m + 11}", 1.4, BLANC))
    s.append(trait(f"M{m} {y - 33}V{y - 45}M{m - 7} {y - 45}h11", 1) + f'<circle cx="{m + 6}" cy="{y - 45}" r="1.6" fill="{EN}"/>')
    s.append(trait(f"M{x + 18} {y - 5}H{m - 32}M{m + 32} {y - 5}H{x + L - 18}", .6, extra='stroke-dasharray="1.5 2"'))
    return "".join(s)


def barge(x, y, L=150):
    return g(_barge(210), x, y, L / 210)


# ------------------------------------------------------------------ le margouillat (posé à part)
def margouillat_corps():
    """Vu de dessus, tête à droite : corps vert, quatre pattes coudées, queue courbe, petite turbine à trois pales."""
    s = []
    for a, b, c in (((6, -2), (8, -6), (11, -7)), ((6, 2), (8, 6), (11, 7)), ((-3, -2), (-6, -6), (-3, -8.5)), ((-3, 2), (-6, 6), (-3, 8.5))):
        s.append(f'<path d="M{a[0]} {a[1]}L{b[0]} {b[1]}L{c[0]} {c[1]}" fill="none" stroke="{EN}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>')
    s.append(f'<path d="M-6 0C-12 .5 -16 4 -21 3.6" fill="none" stroke="{EN}" stroke-width="2.2" stroke-linecap="round"/>')
    s.append(f'<path d="M-6 0C-12 .5 -16 4 -21 3.6" fill="none" stroke="{VERT}" stroke-width="1" stroke-linecap="round"/>')
    s.append(f'<path d="M-7 0C-5 -3.4 4 -3.4 8 -2C11 -3.2 15.5 -2.4 17 0C15.5 2.4 11 3.2 8 2C4 3.4 -5 3.4 -7 0Z" fill="{VERT}" stroke="{EN}" stroke-width=".8"/>')
    s.append(f'<circle cx="13.4" cy="-1.3" r=".7" fill="{EN}"/><circle cx="13.4" cy="1.3" r=".7" fill="{EN}"/>')
    tx, ty, r = -24, 3.2, 3.4
    s.append(f'<circle cx="{tx}" cy="{ty}" r="{r}" fill="{BLANC}" stroke="{EN}" stroke-width=".8"/>')
    for a in (0, 120, 240):
        t = math.radians(a + 20)
        s.append(f'<path d="M{tx} {ty}L{tx + r * .95 * math.cos(t):.2f} {ty + r * .95 * math.sin(t):.2f}" stroke="{EN}" stroke-width="1.1"/>')
    s.append(f'<circle cx="{tx}" cy="{ty}" r=".9" fill="{CYAN}" stroke="{EN}" stroke-width=".4"/>')
    return "".join(s)


MARG_VB = (-28.5, -9.5, 47, 19)     # boîte du margouillat (unités du bandeau)


# ------------------------------------------------------------------ 1. le cône vu de la baie, avec le téléphérique de pirogues
SC = .727
CTX, CTY = 512 - 488 * SC, 12 - 14 * SC


def cone():
    s = []
    prof = "M488 126C530 114 552 84 566 56C574 40 580 24 586 16Q590 12 594 17C600 30 606 46 614 64C624 88 652 112 700 122"
    s.append(neon(prof, CYAN, 2.6, -1.8, 2.2))
    s.append(f'<path d="{prof}L700 132H488Z" fill="{BLANC}"/>' + trait(prof, 2))
    s.append(trame("M590 14C600 30 606 46 614 64C624 88 652 112 700 122L700 132H582C586 100 588 60 590 14Z", 580, 12, 122, 122, "25"))
    s.append(trame("M582 132C586 100 588 60 590 16C582 30 574 52 566 70C556 94 536 118 516 132Z", 510, 12, 80, 122, "12"))
    for gx, gy, L in ((574, 50, 34), (600, 50, 44), (618, 84, 30), (560, 84, 28)):
        s.append(trait(f"M{gx} {gy}q{(gx - 590) * .1:.0f} {L * .5:.0f} {(gx - 590) * .35:.0f} {L}", .8))
    return g("".join(s), CTX, CTY, SC)


def telepherique():
    """Le téléphérique : deux pylônes, le câble, des cabines qui sont des pirogues à balancier."""
    s = []
    s.append(trait("M472 100V82M466 100h12M468 88l8 -4M468 94l8 -4", 1.2) + trait("M586 14V6M582 14h8", 1.4))
    s.append(trait("M472 82L586 6", .9) + trait("M472 86L586 10", .6, extra='stroke-dasharray="2 2"'))
    for t in (.3, .66):
        x, y = 472 + 114 * t, 82 - 76 * t
        s.append(trait(f"M{x:.0f} {y:.0f}v8", .8) + g(_pirogue(96), x - 12, y + 12, .26))
    s.append(neon("M472 82L586 6", CYAN, 0, -2.4, 1.2))
    return "".join(s)


def choungui():
    s, hor = [], 92
    s.append(collines(hor, 3, 0, 500, 5) + collines(hor, 4, 660, 840, 6))
    s.append(cone())
    s.append(arbres(hor - 1, list(range(206, 500, 8)) + list(range(664, 840, 8)), 3))
    s.append(trait(f"M0 {hor}H{W}", 1.1))
    s.append(trait("M576 98Q586 108 588 116M602 98Q594 108 592 116", .7, extra='stroke-dasharray="3 3"'))
    s.append(eau(hor + 4, 118, 4))
    plage = "M0 120V110C70 106 150 108 220 114C240 116 252 118 262 120Z"
    s.append(trame(plage, 0, 104, 264, 18, "12") + trait("M0 110C70 106 150 108 220 114C240 116 252 118 262 120", 1.1))
    s.append(cocotier(462, 104, .42, 10, 1) + cocotier(482, 102, .36, -9, 2))
    s.append(pirogue(330, 108, .38))
    s.append(telepherique())
    return s


# ------------------------------------------------------------------ 2. l'îlot de sable blanc, avec le feu rouge dans le lagon
def feu_lagon():
    """Un feu tricolore planté dans le lagon : les pirogues font la queue à la ligne d'arrêt."""
    s = []
    for x in (240, 316, 392):
        s.append(pirogue(x, 108, .36))
    s.append(trait("M458 92V116", .9, extra='stroke-dasharray="3 2"'))
    s.append(trait("M476 110h16l-2 6h-12z", 1, BLANC))
    s.append(trait("M484 110V82", 1.6))
    s.append(neon("M476 52h16v30h-16z", ROSE, 1.8, 1.4, 1.6) + trait("M476 52h16v30h-16z", 1.2, BLANC))
    s.append(f'<circle cx="484" cy="58" r="3.6" fill="{EN}"/><circle cx="484" cy="67" r="3.6" fill="{BLANC}" stroke="{EN}" stroke-width=".9"/>'
             f'<circle cx="484" cy="76" r="3.6" fill="{BLANC}" stroke="{EN}" stroke-width=".9"/>')
    s.append(trait("M474 52l-4 -3M494 52l4 -3", .8))
    return "".join(s)


def ilot():
    s, hor = [], 82
    terre = (f"M450 {hor}C480 76 512 76 540 70C560 66 572 70 586 64C594 58 598 50 602 46Q605 43 608 47C612 56 620 62 636 66"
             f"C656 70 690 70 716 76L716 {hor}Z")
    s.append(trame(terre, 450, 42, 268, 42, "12") + trait(terre.replace(f"L716 {hor}Z", ""), .9))
    s.append(collines(hor, 6, 0, 440, 3))
    s.append(trait(f"M0 {hor}H{W}", 1.1))
    s.append(trait("".join(f"M{x} {hor + 7 + (x % 3)}h{12 + x % 9}" for x in range(10, 836, 28)), 1.1, extra='stroke-dasharray="2 3"'))
    s.append(eau(hor + 13, 118, 7, dens=.75))
    il = "M520 104C560 96 620 94 680 98C700 99 716 102 724 104C690 108 640 109 600 109C560 109 536 107 520 104Z"
    s.append(neon("M520 104C560 96 620 94 680 98C700 99 716 102 724 104", CYAN, 0, 3, 1.8))
    s.append(trait(il, 1.2, BLANC) + trame(il, 520, 94, 206, 16, "12"))
    s.append(trait("M508 110C580 116 680 115 740 110", .8, extra='stroke-dasharray="5 3"'))
    s.append(feu_lagon())
    return s


# ------------------------------------------------------------------ 3. la ville, le mont et la barge-drone
def barge_drone():
    """La barge, portée par quatre hélices de drone, passe au-dessus du bras de mer ; son ombre reste sur l'eau."""
    s = []
    x, y, L = 470, 66, 168
    for px in (x + 14, x + 52, x + L - 52, x + L - 14):
        s.append(trait(f"M{px} {y - 2}V{y - 22}", 1.1))
        s.append(trait(f"M{px - 16} {y - 23}h32", 1.8) + neon(f"M{px - 16} {y - 23}h32", CYAN, 0, -2.4, 1.2))
        s.append(trait(f"M{px - 18} {y - 28}q18 -5 36 0", .6, extra='stroke-dasharray="2 2"'))
    s.append(barge(x, y, L))
    s.append(trait(f"M{x + 20} {y + 18}l-2 8M{x + L - 30} {y + 18}l2 8M{x + L * .5:.0f} {y + 20}v6", .8, extra='stroke-dasharray="2 2"'))
    s.append(trait(f"M{x + 10} 112c30 4 {L - 20} 4 {L - 20} 0", .9, extra='stroke-dasharray="4 3"'))
    s.append(trait(f"M{x - 6} 104q8 -3 16 0M{x + L - 10} 104q8 -3 16 0", .8))
    return "".join(s)


def mamoudzou():
    s, hor = [], 96
    col = "M452 86C480 72 500 50 524 38C534 34 542 36 552 42C578 58 620 70 716 80V96H452Z"
    s.append(trame(col, 452, 32, 266, 66, "12") + trait("M0 88C150 86 320 88 452 86C480 72 500 50 524 38C534 34 542 36 552 42C578 58 620 70 716 80", .9))
    s.append(trait("M530 36V18M524 36L530 24L536 36", .8) + f'<circle cx="530" cy="17" r="1.6" fill="{EN}"/>')
    rd = random.Random(5)
    x = 2
    while x < 712:
        w = rd.choice((18, 22, 26, 32))
        h = rd.choice((6, 8, 10)) + (8 if 452 < x < 712 else 0)
        s.append(trait(f"M{x} {hor}V{hor - h}H{x + w}V{hor}", .8, BLANC))
        s.append(trait("".join(f"M{x + 3 + i * 6} {hor - h + 3 + j * 5}h2.6v2.4h-2.6z" for i in range(w // 6 - 1)
                               for j in range(max(h // 5 - 1, 1)) if rd.random() < .5), .45))
        x += w + rd.choice((2, 4, 6))
    s.append(cocotier(446, hor, .32, 6, 5) + cocotier(690, hor, .3, -5, 6))
    s.append(trait(f"M0 {hor}H{W}", 1.2))
    s.append(eau(hor + 4, 118, 9, dens=.7))
    pt = "M736 108C756 100 780 98 800 100C816 96 830 98 840 100V110H736Z"
    s.append(trame(pt, 736, 94, 104, 18, "25") + trait("M736 108C756 100 780 98 800 100C816 96 830 98 840 100", .9))
    s.append(barge_drone())
    return s


# ------------------------------------------------------------------ 4. le baobab de plage, paraboles et lampions
SB = .68
BTX, BTY = 590 - 588 * SB, 9 - 20 * SB


def T(x, y):
    return BTX + x * SB, BTY + y * SB


def _branche(pts, w0, w1):
    gch, dr = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        j, k = min(i + 1, n - 1), max(i - 1, 0)
        dx, dy = pts[j][0] - pts[k][0], pts[j][1] - pts[k][1]
        L = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        gch.append((x - dy / L * w, y + dx / L * w))
        dr.append((x + dy / L * w, y - dx / L * w))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in gch + dr[::-1]) + "Z"


BR = [([(558, 80), (540, 66), (522, 60), (508, 48)], 10, 3), ([(572, 78), (566, 58), (558, 42), (554, 26)], 9, 2.6),
      ([(598, 78), (604, 58), (614, 42), (620, 26)], 9, 2.6), ([(614, 80), (632, 66), (650, 62), (666, 50)], 10, 3),
      ([(528, 58), (516, 62), (504, 58)], 3, 1.6), ([(648, 62), (662, 66), (676, 62)], 3, 1.6)]


def arbre():
    s = []
    tronc = "M532 176C544 168 548 152 548 130C548 110 549 94 552 82L556 76H616L620 82C624 94 625 110 625 130C625 152 628 168 642 176Z"
    s.append(neon(tronc, ROSE, 2.6, -1.4, 2.2) + trait(tronc, 2, BLANC))
    s.append(trame("M604 76H616L620 82C624 94 625 110 625 130C625 152 628 168 642 176H606C610 150 610 110 604 76Z", 600, 74, 46, 104, "25"))
    s.append(trait("M564 84C562 120 560 150 556 172M586 80C588 110 586 146 588 174", .8))
    for pts, w0, w1 in BR:
        s.append(trait(_branche(pts, w0, w1), 1.3, BLANC))
    rd = random.Random(8)
    for x, y in ((512, 46), (504, 56), (556, 22), (618, 20), (664, 48), (676, 60), (540, 56), (636, 60)):
        s.append(trait("".join(f"M{x + rd.uniform(-9, 9):.0f} {y + rd.uniform(-7, 3):.0f}a3.4 2.2 0 0 1 6.8 0" for _ in range(5)), 1))
    return g("".join(s), BTX, BTY, SB)


def parabole(x, y, angle, k=1.0):
    """Une antenne parabolique de trois quarts (redessinée) : la coupe, son bord, le bras et la tête,
    le pied fixé à la branche. Le bord a un néon décalé."""
    s = []
    s.append(trait("M0 3.6V10", 1.5))                                         # le pied, jusqu'à la branche
    s.append(trait("M-8.5 0C-7.5 6.4 7.5 6.4 8.5 0Z", 1.1, BLANC))          # le dos de la coupe
    s.append(trame("M-8.5 0C-7.5 6.4 7.5 6.4 8.5 0Z", -9, 0, 18, 6, "25"))
    s.append(neon("M-8.5 0a8.5 2.8 0 1 0 17 0a8.5 2.8 0 1 0 -17 0", CYAN, 1.2, -1.2, 1.1))
    s.append(trait("M-8.5 0a8.5 2.8 0 1 0 17 0a8.5 2.8 0 1 0 -17 0", 1.1, BLANC))   # le bord
    s.append(trait("M-3 0a3 1 0 1 0 6 0a3 1 0 1 0 -6 0", .5))
    s.append(trait("M6.6 1.6L1 -8.4", 1) + trait("M-1.6 -11.4h3.4v3.2h-3.4z", .9, BLANC))   # le bras et la tête
    return f'<g transform="translate({x:.1f},{y:.1f}) rotate({angle}) scale({k})">{"".join(s)}</g>'


def paraboles_lampions():
    """Le baobab sert d'antenne-relais (trois paraboles tournées vers le ciel, un câble qui descend le tronc)
    et de guirlande de fête (trois lampions entre les deux hautes branches)."""
    s = []
    (x0, y0), (x1, y1) = T(554, 26), T(620, 26)
    mx, my = (x0 + x1) / 2, max(y0, y1) + 16
    s.append(trait(f"M{x0:.0f} {y0:.0f}Q{mx:.0f} {my:.0f} {x1:.0f} {y1:.0f}", .7))
    for t in (.25, .5, .75):
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1
        py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1
        s.append(neon(f"M{px - 2.8:.1f} {py + 1:.1f}h5.6v6.4h-5.6z", JAUNE, 1, 1, 2.4)
                 + trait(f"M{px - 2.8:.1f} {py + 1:.1f}h5.6v6.4h-5.6z", .8, BLANC) + trait(f"M{px:.1f} {py + 2.4:.1f}v3.4", .6))
    # trois paraboles sur les branches du dehors, penchées vers l'extérieur
    for (bx, by), a, k in ((T(528, 62), -42, 1.1), (T(652, 64), 40, 1.1), (T(632, 104), 64, .9)):
        s.append(parabole(bx, by - 10 * k, a, k))
    # le câble de l'antenne-relais descend le long du tronc
    xa, ya = T(626, 112)
    xb, yb = T(624, 160)
    s.append(trait(f"M{xa:.0f} {ya:.0f}C{xa - 6:.0f} {ya + 24:.0f} {xb + 2:.0f} {yb - 40:.0f} {xb:.0f} {yb:.0f}", .8, extra='stroke-dasharray="3 2"'))
    # le signal : trois arcs au-dessus de la parabole de gauche
    px, py = T(500, 30)
    s.append("".join(neon(f"M{px - 5 - 3 * i:.1f} {py - 3 * i:.1f}q{5 + 3 * i} {-5 - 2 * i} {10 + 6 * i} 0", CYAN, 0, 0, .9) for i in range(3)))
    return "".join(s)


def baobab():
    s, hor = [], 96
    s.append(collines(84, 9, 0, 520, 5))
    s.append(trait(f"M0 {hor}H520", 1.1))
    s.append(eau(hor + 3, 116, 11, x1=500))
    s.append(arbre())
    s.append(paraboles_lampions())
    plage = f"M380 {H}C420 112 470 112 520 113C600 115 700 108 840 104V{H}Z"
    s.append(trame(plage, 380, 102, 460, 20, "12") + trait(f"M380 {H}C420 112 470 112 520 113C600 115 700 108 840 104", 1.1))
    s.append(collines(96, 12, 680, 840, 8))
    tortue = "M300 108c4 -6 18 -6 24 0c-6 4 -18 4 -24 0z"
    s.append(trait(tortue, 1, BLANC) + trait("M306 106.5l4 -3l6 3l6 -3", .6) + trait("M324 106.5c3 -2 6 -1.5 7 .8", 1.2) + trait("M302 111l-4 3M320 111l4 3", 1))
    s.append(neon("M300 108c4 -6 18 -6 24 0", CYAN, 0, -2.4, 1.2))
    return s


# ------------------------------------------------------------------ les bandeaux
SCENES = {1: ("choungui", choungui, 0), 2: ("ilot", ilot, 6), 3: ("mamoudzou", mamoudzou, 6), 4: ("baobab", baobab, 2)}
TITRES = {1: "Le cône vu de la baie, et son téléphérique de pirogues",
          2: "L'îlot de sable blanc, et le feu rouge dans le lagon",
          3: "La ville, le mont et la barge-drone",
          4: "Le baobab de plage, ses paraboles et ses lampions"}
HORIZON = {1: 92, 2: 82, 3: 96, 4: 96}

# Cachettes du margouillat dans chaque bandeau (repère du bandeau de 28 mm, après le décalage dy) :
# (x, y, rotation en degrés, échelle). Jamais sur le titre ni sur le QR code.
CACHETTES = {
    1: [(120, 103, -8, .9), (463, 93, -84, .55), (705, 86, 176, .7), (348, 103, -4, .55)],
    2: [(684, 94, 172, .8), (334, 103, -4, .5), (560, 61, -12, .7), (488, 98, -88, .5)],
    3: [(660, 76, 4, .55), (770, 95, -6, .75), (440, 88, 0, .6), (584, 90, -90, .5)],
    4: [(612, 89, -70, .6), (760, 96, 4, .8), (440, 104, -6, .75), (566, 79, -106, .55)],
}


def entete(vb, l_mm, h_mm, titre):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{l_mm}mm" height="{h_mm}mm" '
            f'preserveAspectRatio="xMidYMid meet" role="img" aria-label="{titre}">'
            f'<title>{titre}</title>')


def desc_zones(controle=False):
    if controle:
        return ('<desc>Bandeau de contrôle, 210 x 20 mm (repère 840 x 80). Zones réservées : titre x &lt; 420 ; '
                'QR code x &gt; 760. Dessin original, Babash - NSI Tani Malandi, CC BY-SA 4.0.</desc>')
    return ('<desc>Bandeau de TD, 210 x 28 mm (repère 840 x 112, 4 unités par mm). Zones réservées : titre, niveau et chapitre '
            'x &lt; 440, y &lt; 80 ; QR code x &gt; 716, y &lt; 84. Dessin original, Babash - NSI Tani Malandi, CC BY-SA 4.0.</desc>')


def obscurcir(s):
    for a, b in OBSCUR.items():
        s = s.replace(f'"{a}"', f'"{b}"')
    return s


def bandeau(n):
    _n[0] = 0
    nom, f, dy = SCENES[n]
    corps = "".join(f())
    return (entete(f"0 {dy} {W} {HB}", 210, 28, TITRES[n]) + desc_zones()
            + f'<rect x="0" y="{dy}" width="{W}" height="{HB}" fill="{BLANC}"/>{corps}</svg>')


def bandeau_controle(n):
    """20 mm : la scène réduite aux deux tiers, posée à droite ; à gauche, l'eau seule."""
    _n[0] = 0
    nom, f, dy = SCENES[n]
    corps = "".join(f())
    hor = HORIZON[n]
    k = 2 / 3
    gauche = trait(f"M0 {(hor - dy) * k:.1f}H300", 1.1) + eau((hor - dy) * k + 4, 78, 21, 0, 300, .8)
    s = (gauche + f'<g transform="translate(250,0) scale({k:.4f})"><g transform="translate(0,{-dy})">'
         f'<rect x="0" y="{dy}" width="{W}" height="{HB}" fill="{BLANC}"/>{corps}</g></g>')
    return entete(f"0 0 {W} 80", 210, 20, TITRES[n]) + desc_zones(True) + f'<rect width="{W}" height="80" fill="{BLANC}"/>{s}</svg>'


def margouillat():
    x, y, w, h = MARG_VB
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" role="img" aria-label="Un margouillat">'
            f'<title>Un margouillat</title>{margouillat_corps()}</svg>')


def marge(couleur="#C9C6D1"):
    """Pistes de circuit pour les marges de l'écran large : gris clair, sans texte (fond de page, répété)."""
    rd = random.Random(3)
    s = []
    for x in (14, 34, 58):
        y, d = 0, f"M{x} 0"
        cx = x
        while y < 600:
            y += rd.randint(40, 120)
            d += f"V{y}"
            if rd.random() < .5 and y < 560:
                nx = cx + rd.choice((-10, 10))
                d += f"L{nx} {y + 10}"
                y += 10
                cx = nx
        d += "V600"
        s.append(f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.2"/>')
        for _ in range(3):
            yy = rd.randint(20, 580)
            s.append(f'<circle cx="{x}" cy="{yy}" r="2.6" fill="none" stroke="currentColor" stroke-width="1.2"/>')
    s.append('<rect x="26" y="210" width="18" height="30" fill="none" stroke="currentColor" stroke-width="1.2"/>'
             + "".join(f'<path d="M26 {214 + 6 * i}h-5M44 {214 + 6 * i}h5" stroke="currentColor" stroke-width="1"/>' for i in range(4)))
    corps = "".join(s)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 600" width="72" height="600" aria-hidden="true">'
            f'<g color="{couleur}">{corps}</g></svg>')


def main():
    os.makedirs(SORTIE, exist_ok=True)
    ecrits = []

    def ecrire(nom, texte):
        with open(os.path.join(SORTIE, nom), "w", encoding="utf-8") as f:
            f.write(texte + "\n")
        ecrits.append((nom, len(texte.encode())))

    for n in SCENES:
        b = bandeau(n)
        ecrire(f"bandeau-{n}.svg", b)
        ecrire(f"bandeau-{n}-obscur.svg", obscurcir(b))
        c = bandeau_controle(n)
        ecrire(f"bandeau-{n}-controle.svg", c)
        ecrire(f"bandeau-{n}-controle-obscur.svg", obscurcir(c))
    m = margouillat()
    ecrire("margouillat.svg", m)
    ecrire("margouillat-obscur.svg", obscurcir(m))
    ecrire("marge.svg", marge())
    ecrire("marge-obscur.svg", marge("#3A3547"))
    # cachettes en pourcentage du bandeau (pour la page) : centre du margouillat, rotation, largeur
    places = {}
    for n, liste in CACHETTES.items():
        dy = SCENES[n][2]
        places[str(n)] = [{"x": round(100 * x / W, 2), "y": round(100 * (y - dy) / HB, 2), "r": r,
                           "l": round(100 * MARG_VB[2] * k / W, 2)} for x, y, r, k in liste]
    places["_note"] = ("Cachettes du margouillat dans chaque bandeau : centre (x, y en % du bandeau), rotation r (degrés), "
                       "largeur l (% du bandeau). Écrit par charte/bandeaux-td.py.")
    ecrire("places-margouillat.json", json.dumps(places, ensure_ascii=False, indent=1))
    for nom, taille in ecrits:
        print(f"assets/td/{nom} : {taille // 1024} Kio")


if __name__ == "__main__":
    main()
