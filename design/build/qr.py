#!/usr/bin/env python3
"""Générateur de QR codes en SVG, en Python pur (aucune dépendance, aucun service en ligne).

Charte « Réseau la nuit », modèle de fiche et de TD (T38). Les QR des documents
sont générés une fois pour toutes, puis collés dans le HTML : rien n'est appelé
à l'affichage, rien ne part vers un service extérieur.

Usage
-----
  python3 design/build/qr.py URL [--libelle TEXTE] [--source TEXTE] [--court TEXTE]
                                 [--niveau L|M|Q|H] [--classe qr] [--svg-seul]
  python3 design/build/qr.py --lot fichier.json      # plusieurs QR d'un coup
  python3 design/build/qr.py --test                  # contrôle par décodage (OpenCV)

Par défaut, le script écrit sur la sortie standard le bloc HTML d'un QR « de cours »
pour l'en-tête d'une fiche (classe .vid de assets/fiche.css) :
  le QR, le libellé de la notion, la source créditée et l'adresse courte en clair.

Fichier --lot : une liste JSON d'objets {"url", "libelle", "source", "court"}.

Règles du modèle (design/README.md, document du modèle) :
  - une adresse courte : le QR reste petit (version 3 au plus, 29 modules) et
    l'adresse s'écrit en clair pour les élèves sans téléphone ;
  - niveau de correction M (15 %) : supporte une photocopie moyenne ;
  - 15 mm au moins à l'impression, encre foncée sur fond blanc.

Le codage suit la norme ISO/IEC 18004 (mode octet, UTF-8, versions 1 à 40).
"""
import argparse
import html
import json
import re
import sys

# ── Tables de la norme (index = version ; l'indice 0 n'est pas utilisé) ──────
ECC_PAR_BLOC = {
    'L': [-1, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
    'M': [-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28],
    'Q': [-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
    'H': [-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
}
NB_BLOCS = {
    'L': [-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25],
    'M': [-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49],
    'Q': [-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68],
    'H': [-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81],
}
BITS_NIVEAU = {'L': 1, 'M': 0, 'Q': 3, 'H': 2}


def modules_bruts(v):
    """Nombre de modules disponibles pour les données et la correction (version v)."""
    r = (16 * v + 128) * v + 64
    if v >= 2:
        n = v // 7 + 2
        r -= (25 * n - 10) * n - 55
        if v >= 7:
            r -= 36
    return r


def octets_donnees(v, niv):
    return modules_bruts(v) // 8 - ECC_PAR_BLOC[niv][v] * NB_BLOCS[niv][v]


# ── Reed-Solomon sur GF(256), polynôme 0x11D ─────────────────────────────────
def gf_mul(x, y):
    z = 0
    for i in range(7, -1, -1):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def rs_diviseur(degre):
    res = [0] * (degre - 1) + [1]
    racine = 1
    for _ in range(degre):
        for j in range(degre):
            res[j] = gf_mul(res[j], racine)
            if j + 1 < degre:
                res[j] ^= res[j + 1]
        racine = gf_mul(racine, 0x02)
    return res


def rs_reste(donnees, diviseur):
    res = [0] * len(diviseur)
    for b in donnees:
        f = b ^ res.pop(0)
        res.append(0)
        for i, c in enumerate(diviseur):
            res[i] ^= gf_mul(c, f)
    return res


# ── Codage ──────────────────────────────────────────────────────────────────
def coder(texte, niveau='M', version_min=1):
    octets = texte.encode('utf-8')
    for v in range(version_min, 41):
        bits_compte = 8 if v < 10 else 16
        if 4 + bits_compte + 8 * len(octets) <= octets_donnees(v, niveau) * 8:
            break
    else:
        raise ValueError('adresse trop longue pour un QR code')

    bits = []

    def ajoute(val, n):
        bits.extend((val >> i) & 1 for i in range(n - 1, -1, -1))

    ajoute(0b0100, 4)                 # mode octet
    ajoute(len(octets), bits_compte)
    for o in octets:
        ajoute(o, 8)
    capacite = octets_donnees(v, niveau) * 8
    ajoute(0, min(4, capacite - len(bits)))
    ajoute(0, (-len(bits)) % 8)
    pad = 0xEC
    while len(bits) < capacite:
        ajoute(pad, 8)
        pad ^= 0xEC ^ 0x11
    mots = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    return v, entrelacer(mots, v, niveau)


def entrelacer(donnees, v, niv):
    nb = NB_BLOCS[niv][v]
    ecc = ECC_PAR_BLOC[niv][v]
    bruts = modules_bruts(v) // 8
    courts = nb - bruts % nb
    long_court = bruts // nb
    div = rs_diviseur(ecc)
    blocs, k = [], 0
    for i in range(nb):
        n = long_court - ecc + (0 if i < courts else 1)
        dat = donnees[k:k + n]
        k += n
        e = rs_reste(dat, div)
        if i < courts:
            dat = dat + [0]
        blocs.append(dat + e)
    res = []
    for i in range(len(blocs[0])):
        for j, b in enumerate(blocs):
            if i != long_court - ecc or j >= courts:
                res.append(b[i])
    return res


class Matrice:
    def __init__(self, v):
        self.v = v
        self.n = 17 + 4 * v
        self.m = [[False] * self.n for _ in range(self.n)]
        self.fonction = [[False] * self.n for _ in range(self.n)]

    def pose(self, x, y, noir):
        self.m[y][x] = noir
        self.fonction[y][x] = True

    def motifs(self):
        n = self.n
        for i in range(n):
            self.pose(6, i, i % 2 == 0)
            self.pose(i, 6, i % 2 == 0)
        for cx, cy in ((3, 3), (n - 4, 3), (3, n - 4)):
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < n and 0 <= y < n:
                        self.pose(x, y, max(abs(dx), abs(dy)) not in (2, 4))
        pos = self.positions_alignement()
        k = len(pos)
        for i in range(k):
            for j in range(k):
                if (i == 0 and j == 0) or (i == 0 and j == k - 1) or (i == k - 1 and j == 0):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        self.pose(pos[i] + dx, pos[j] + dy, max(abs(dx), abs(dy)) != 1)
        self.format('M', 0)          # réserve les zones de format (réécrites ensuite)
        if self.v >= 7:
            r = self.v
            for _ in range(12):
                r = (r << 1) ^ ((r >> 11) * 0x1F25)
            b = self.v << 12 | r
            for i in range(18):
                bit = (b >> i) & 1 == 1
                a, c = n - 11 + i % 3, i // 3
                self.pose(a, c, bit)
                self.pose(c, a, bit)

    def positions_alignement(self):
        if self.v == 1:
            return []
        k = self.v // 7 + 2
        pas = (self.v * 8 + k * 3 + 5) // (k * 4 - 4) * 2
        res = [self.n - 7 - i * pas for i in range(k - 1)] + [6]
        return list(reversed(res))

    def format(self, niv, masque):
        d = BITS_NIVEAU[niv] << 3 | masque
        r = d
        for _ in range(10):
            r = (r << 1) ^ ((r >> 9) * 0x537)
        b = (d << 10 | r) ^ 0x5412
        bit = lambda i: (b >> i) & 1 == 1  # noqa: E731
        n = self.n
        for i in range(6):
            self.pose(8, i, bit(i))
        self.pose(8, 7, bit(6))
        self.pose(8, 8, bit(7))
        self.pose(7, 8, bit(8))
        for i in range(9, 15):
            self.pose(14 - i, 8, bit(i))
        for i in range(8):
            self.pose(n - 1 - i, 8, bit(i))
        for i in range(8, 15):
            self.pose(8, n - 15 + i, bit(i))
        self.pose(8, n - 8, True)

    def place(self, mots):
        n, i = self.n, 0
        total = len(mots) * 8
        droite = n - 1
        while droite >= 1:
            if droite == 6:
                droite = 5
            for vert in range(n):
                for j in range(2):
                    x = droite - j
                    monte = ((droite + 1) & 2) == 0
                    y = n - 1 - vert if monte else vert
                    if not self.fonction[y][x] and i < total:
                        self.m[y][x] = (mots[i >> 3] >> (7 - (i & 7))) & 1 == 1
                        i += 1
            droite -= 2

    def masque(self, k):
        f = [
            lambda x, y: (x + y) % 2 == 0,
            lambda x, y: y % 2 == 0,
            lambda x, y: x % 3 == 0,
            lambda x, y: (x + y) % 3 == 0,
            lambda x, y: (x // 3 + y // 2) % 2 == 0,
            lambda x, y: x * y % 2 + x * y % 3 == 0,
            lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
            lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
        ][k]
        for y in range(self.n):
            for x in range(self.n):
                if not self.fonction[y][x] and f(x, y):
                    self.m[y][x] = not self.m[y][x]

    def penalite(self):
        n, m, p = self.n, self.m, 0
        lignes = [m[y] for y in range(n)] + [[m[y][x] for y in range(n)] for x in range(n)]
        motif_a = [True, False, True, True, True, False, True, False, False, False, False]
        motif_b = motif_a[::-1]
        for ligne in lignes:
            serie, prec = 0, None
            for c in ligne:
                if c == prec:
                    serie += 1
                else:
                    if serie >= 5:
                        p += serie - 2
                    serie, prec = 1, c
            if serie >= 5:
                p += serie - 2
            pad = [False] * 4 + list(ligne) + [False] * 4
            for i in range(len(pad) - 10):
                fen = pad[i:i + 11]
                if fen == motif_a or fen == motif_b:
                    p += 40
        for y in range(n - 1):
            for x in range(n - 1):
                c = m[y][x]
                if c == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                    p += 3
        noirs = sum(sum(r) for r in m)
        p += abs(noirs * 20 - n * n * 10) // (n * n) * 10
        return p


def qr_matrice(texte, niveau='M'):
    """Renvoie (version, matrice de booléens) du QR code de `texte`."""
    v, mots = coder(texte, niveau)
    meilleur = None
    for k in range(8):
        q = Matrice(v)
        q.motifs()
        q.place(mots)
        q.masque(k)
        q.format(niveau, k)
        pen = q.penalite()
        if meilleur is None or pen < meilleur[0]:
            meilleur = (pen, q)
    return v, meilleur[1].m


# ── Sortie SVG et HTML ──────────────────────────────────────────────────────
def svg(texte, niveau='M', classe='qr', libelle=None):
    """SVG compact : un rectangle plein par suite de modules noirs (s'imprime net)."""
    v, m = qr_matrice(texte, niveau)
    n = len(m)
    d = []
    for y, ligne in enumerate(m):
        x = 0
        while x < n:
            if ligne[x]:
                x0 = x
                while x < n and ligne[x]:
                    x += 1
                d.append(f'M{x0} {y}h{x - x0}v1h-{x - x0}z')
            else:
                x += 1
    aria = html.escape(libelle or f'QR code vers {adresse_courte(texte)}', quote=True)
    return (f'<svg class="{classe}" viewBox="0 0 {n} {n}" role="img" aria-label="{aria}" '
            f'shape-rendering="crispEdges"><path fill="currentColor" d="{"".join(d)}"/></svg>')


def adresse_courte(url):
    """L'adresse telle qu'on l'écrit en clair : sans https://, sans www., sans / final."""
    a = re.sub(r'^https?://', '', url)
    a = re.sub(r'^www\.', '', a)
    return a.rstrip('/')


def bloc_html(url, libelle, source=None, court=None, niveau='M'):
    """Bloc .vid de l'en-tête : QR, libellé de la notion, source et adresse en clair."""
    c = court or adresse_courte(url)
    lib = html.escape(libelle)
    src = f'<span class="src">{html.escape(source)}</span>' if source else ''
    clair = html.escape(c).replace('/', '/<wbr>')   # coupure permise après chaque « / »
    return (f'<div class="vid">{svg(url, niveau, libelle=f"QR code : {libelle}")}'
            f'<p><b>{lib}</b>{src}<a class="url" href="{html.escape(url, quote=True)}">{clair}</a></p></div>')


# ── Contrôle par décodage ───────────────────────────────────────────────────
def decoder(m):
    """Décode une matrice avec OpenCV (facultatif : seulement pour --test).

    Le premier détecteur d'OpenCV rate parfois un QR pourtant valide : on essaie
    donc deux détecteurs et trois échelles, comme le ferait un téléphone qui bouge."""
    import cv2  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    n, q = len(m), 4
    detecteurs = [cv2.QRCodeDetector()]
    if hasattr(cv2, 'QRCodeDetectorAruco'):
        detecteurs.append(cv2.QRCodeDetectorAruco())
    lu = ''
    for k in (8, 5, 11):
        img = np.full(((n + 2 * q) * k,) * 2, 255, np.uint8)
        for y in range(n):
            for x in range(n):
                if m[y][x]:
                    img[(y + q) * k:(y + q + 1) * k, (x + q) * k:(x + q + 1) * k] = 0
        for d in detecteurs:
            lu, _, _ = d.detectAndDecode(img)
            if lu:
                return lu
    return lu


def tester():
    essais = [
        'https://youtu.be/D26k0EaoyNI',
        'babash.github.io/Babash-NSI-SNT/td/exemple',
        'https://babash.github.io/Babash-NSI-SNT/nsi-terminale/fichiers/td1-poo-premiers-pas.html',
        'https://fr.wikipedia.org/wiki/Programmation_orient%C3%A9e_objet',
        'Élève·s : accents et point médian',
        'x' * 300,
    ]
    ok = True
    for t in essais:
        for niv in 'LMQH':
            v, m = qr_matrice(t, niv)
            lu = decoder(m)
            bon = lu == t
            ok &= bon
            print(f'{"ok " if bon else "ÉCHEC"} v{v:<2} {niv} {len(m)}×{len(m)}  {t[:60]}')
    print('Tous les QR sont relus correctement.' if ok else 'Au moins un QR est illisible.')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('url', nargs='?')
    ap.add_argument('--libelle', help='la notion expliquée (ex. « Les paradigmes »)')
    ap.add_argument('--source', help='la source créditée (chaîne, site, auteur·e)')
    ap.add_argument('--court', help="l'adresse à écrire en clair, si différente")
    ap.add_argument('--niveau', default='M', choices='LMQH')
    ap.add_argument('--classe', default='qr')
    ap.add_argument('--svg-seul', action='store_true', help='seulement le SVG')
    ap.add_argument('--lot', help='fichier JSON : [{"url", "libelle", "source", "court"}, …]')
    ap.add_argument('--test', action='store_true', help='contrôle par décodage (OpenCV)')
    a = ap.parse_args()
    if a.test:
        return tester()
    if a.lot:
        with open(a.lot, encoding='utf-8') as f:
            for e in json.load(f):
                v, m = qr_matrice(e['url'], a.niveau)
                print(f'<!-- QR version {v} ({len(m)} modules) : {e["url"]} -->', file=sys.stderr)
                print(bloc_html(e['url'], e.get('libelle', ''), e.get('source'), e.get('court'), a.niveau))
        return 0
    if not a.url:
        ap.error('donner une adresse, --lot ou --test')
    v, m = qr_matrice(a.url, a.niveau)
    if v > 3:
        print(f'Attention : QR de version {v} ({len(m)} modules). Une adresse plus courte '
              'donne un QR plus lisible à l\'impression.', file=sys.stderr)
    if a.svg_seul:
        print(svg(a.url, a.niveau, a.classe, a.libelle))
    else:
        print(bloc_html(a.url, a.libelle or adresse_courte(a.url), a.source, a.court, a.niveau))
    return 0


if __name__ == '__main__':
    sys.exit(main())
