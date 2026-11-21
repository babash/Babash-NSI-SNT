#!/usr/bin/env python3
"""Dessine en SVG les grilles du robot des TD (boucles et conditions, NSI 1re).

Les grilles sont celles des fiches d'origine (voir robot.py). Tout est tracé en currentColor :
la grille suit le thème (clair, obscur) et s'imprime en noir et blanc. Obstacle : case grisée
barrée d'une croix ; robot : une petite tête à antenne. Le texte fait 14 px (10,5 pt) : le SVG
est affiché à sa taille réelle (1 unité = 1 px), jamais réduit.

Usage : python3 -I grilles.py for   (écrit le SVG de la grille « for » sur la sortie)
"""
import sys

from robot import COLONNES, GRILLES

C = 24          # côté d'une case, en px
M = 20          # marge des étiquettes (lettres en haut, numéros à gauche)


def robot(x, y, c=C):
    """La tête du robot dans la case dont le coin haut gauche est (x, y)."""
    k = c / 24
    return (f'<g fill="none" stroke="currentColor" stroke-width="1.6">'
            f'<rect x="{x + 5 * k:.1f}" y="{y + 8 * k:.1f}" width="{14 * k:.1f}" height="{11 * k:.1f}" rx="2.5"/>'
            f'<path d="M{x + 12 * k:.1f} {y + 8 * k:.1f}V{y + 4 * k:.1f}"/></g>'
            f'<g fill="currentColor"><circle cx="{x + 12 * k:.1f}" cy="{y + 3.5 * k:.1f}" r="{1.6 * k:.1f}"/>'
            f'<circle cx="{x + 9.3 * k:.1f}" cy="{y + 12.6 * k:.1f}" r="{1.5 * k:.1f}"/>'
            f'<circle cx="{x + 14.7 * k:.1f}" cy="{y + 12.6 * k:.1f}" r="{1.5 * k:.1f}"/>'
            f'<rect x="{x + 9 * k:.1f}" y="{y + 15.6 * k:.1f}" width="{6 * k:.1f}" height="1.4"/></g>')


def obstacle(x, y, c=C):
    return (f'<rect x="{x + 1.5}" y="{y + 1.5}" width="{c - 3}" height="{c - 3}" fill="currentColor" fill-opacity=".28"/>'
            f'<path d="M{x + 5} {y + 5}L{x + c - 5} {y + c - 5}M{x + c - 5} {y + 5}L{x + 5} {y + c - 5}" '
            f'stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>')


def grille(nom, depart=None, robot_visible=True):
    g = GRILLES[nom]
    ncol, nlig = g.get("colonnes", len(COLONNES)), g["lignes"]
    cols = COLONNES[:ncol]
    d = depart or g["depart"]
    w, h = M + ncol * C + 2, M + nlig * C + 2
    obs = sorted(g["obstacles"], key=lambda s: (int(s[1:]), s[0]))
    titre = (f"Grille du robot : {ncol} colonnes (A à {cols[-1]}) et {nlig} lignes (1 à {nlig}), le nord en haut. "
             + (f"Le robot est en {d}. " if robot_visible else "")
             + "Obstacles en " + ", ".join(obs) + ".")
    p = [f'<svg class="td-grille-robot" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{titre}" '
         f'font-family="inherit" font-size="14" font-weight="700">']
    for i, lettre in enumerate(cols):
        p.append(f'<text x="{M + i * C + C / 2}" y="14" text-anchor="middle" fill="currentColor">{lettre}</text>')
    for j in range(nlig):
        p.append(f'<text x="{M / 2 - 1}" y="{M + j * C + C / 2 + 5}" text-anchor="middle" fill="currentColor">{j + 1}</text>')
    for case in obs:
        p.append(obstacle(M + cols.index(case[0]) * C, M + (int(case[1:]) - 1) * C))
    if robot_visible:
        p.append(robot(M + cols.index(d[0]) * C, M + (int(d[1:]) - 1) * C))
    lignes = [f'M{M + i * C} {M}V{M + nlig * C}' for i in range(ncol + 1)]
    lignes += [f'M{M} {M + j * C}H{M + ncol * C}' for j in range(nlig + 1)]
    p.append(f'<path d="{"".join(lignes)}" fill="none" stroke="currentColor" stroke-width="1"/>')
    p.append('</svg>')
    return "".join(p)


def icone(quoi):
    """Petite icône (24 px) pour la légende : 'robot' ou 'obstacle'."""
    corps = robot(0, 0) if quoi == "robot" else obstacle(0, 0)
    return (f'<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" '
            f'style="vertical-align:middle">{corps}</svg>')


def rose():
    """La rose des vents (64 px), lettres de 14 px."""
    return ('<svg width="72" height="72" viewBox="0 0 72 72" role="img" aria-label="Rose des vents : le nord en haut, '
            'le sud en bas, l\'est à droite, l\'ouest à gauche." font-family="inherit" font-size="14" font-weight="700">'
            '<circle cx="36" cy="36" r="18" fill="none" stroke="currentColor" stroke-opacity=".5"/>'
            '<path d="M36 16L39.5 36L36 56L32.5 36Z" fill="currentColor"/>'
            '<path d="M16 36L36 32.5L56 36L36 39.5Z" fill="none" stroke="currentColor" stroke-width="1.2"/>'
            '<text x="36" y="12" text-anchor="middle" fill="currentColor">N</text>'
            '<text x="36" y="71" text-anchor="middle" fill="currentColor">S</text>'
            '<text x="66" y="41" text-anchor="middle" fill="currentColor">E</text>'
            '<text x="6" y="41" text-anchor="middle" fill="currentColor">O</text></svg>')


if __name__ == "__main__":
    print(grille(sys.argv[1] if len(sys.argv) > 1 else "for"))
