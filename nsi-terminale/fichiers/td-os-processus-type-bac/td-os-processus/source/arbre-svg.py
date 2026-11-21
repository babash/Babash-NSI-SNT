#!/usr/bin/env python3
"""Dessine l'arborescence de la feuille en SVG (trait currentColor : écran clair, obscur et papier
en noir et blanc), en arbre « en retrait » pour rester lisible à 320 px. Usage : python3 -I arbre-svg.py [--processus]"""
import sys
PROCESSUS = [(0, '1 /sbin/init'), (1, '500 sshd'), (2, '1050 bash'), (3, '1210 python3'), (3, '1215 ps -ef')]
NOEUDS = [  # (niveau, nom)
    (0, '/ (racine)'), (1, 'bin'), (1, 'home'), (2, 'prof'), (3, 'examens (D)'), (3, 'notes.csv (F)'),
    (2, 'eleve'), (3, 'devoirs (D)'), (4, 'nsi (D)'), (3, 'projets (D)'),
]
LABEL = ("Arborescence : la racine / contient bin et home ; home contient prof et eleve ; prof contient le dossier examens "
         "et le fichier notes.csv ; eleve contient les dossiers devoirs et projets ; devoirs contient le dossier nsi.")
if '--processus' in sys.argv:
    NOEUDS = PROCESSUS
    LABEL = ("Arbre des processus : 1 (/sbin/init) est le parent de 500 (sshd), parent de 1050 (bash) ; "
             "1050 est le parent de 1210 (python3 calcul_pi.py) et de 1215 (ps -ef).")
DX, DY, H, CAR = 30, 34, 24, 8.6
parts, pos = [], []
for i, (niv, nom) in enumerate(NOEUDS):
    x, y = 2 + niv * DX, 4 + i * DY
    w = round(len(nom) * CAR + 14)
    pos.append((niv, x, y, w))
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{H}" rx="5" fill="none" stroke="currentColor" stroke-width="1.4"/>'
                 f'<text x="{x + 7}" y="{y + 17}" fill="currentColor">{nom}</text>')
# un trait du parent (en bas, à 12 px du bord gauche) vers chaque enfant, avec une pointe de flèche
for i, (niv, x, y, w) in enumerate(pos):
    for j in range(i + 1, len(pos)):
        nj, xj, yj, wj = pos[j]
        if nj <= niv:
            break
        if nj == niv + 1:
            px, py = x + 12, y + H
            cy = yj + H / 2
            parts.append(f'<path d="M{px} {py}V{cy}H{xj - 1}" fill="none" stroke="currentColor" stroke-width="1.4"/>'
                         f'<path d="M{xj - 1} {cy}l-7 -4v8z" fill="currentColor"/>')
largeur = max(x + w for _, x, _, w in pos) + 4
hauteur = 4 + len(NOEUDS) * DY
print(f'<svg width="{largeur}" height="{hauteur}" viewBox="0 0 {largeur} {hauteur}" role="img" '
      f'aria-label="{LABEL}" '
      f'font-family="inherit" font-size="15">' + ''.join(parts) + '</svg>')
