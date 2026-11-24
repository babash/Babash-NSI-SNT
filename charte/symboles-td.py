#!/usr/bin/env python3
"""Refait « TD Symboles » : sous-ensemble de DejaVu Sans 2.37, renommé (la licence Bitstream Vera l'exige).

Usage : python3 -I charte/symboles-td.py /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf assets/fonts/td-symboles-400-normal.woff2
Puis reporter la liste UNI dans l'unicode-range de « TD Symboles » (assets/signal-commun.css, commun au site et aux TD depuis T123d ; plus dans td-en-ligne.css).
"""
import sys
from fontTools import subset
from fontTools.ttLib import TTFont
UNI = ('U+00AC,U+00D7,U+0394,U+03A3,U+03BB,U+03C0,U+2190-2194,U+21D2,U+21D4,U+2205,U+2206,U+2208,U+2209,U+2211,U+221A,U+221E,'
       'U+2227-222A,U+2248,U+2260,U+2261,U+2264,U+2265,U+25A0,U+25A1,U+25B2,U+25BC,U+25C6,U+2605,U+2606,U+2713,U+2717')
src, sortie = sys.argv[1], sys.argv[2]
o = subset.Options(); o.flavor = 'woff2'; o.name_IDs = ['*']; o.name_languages = ['*']; o.notdef_outline = True
f = TTFont(src)
s = subset.Subsetter(o)
cps = []
for part in UNI.split(','):
    a, _, b = part[2:].partition('-'); cps += range(int(a, 16), int(b or a, 16) + 1)
s.populate(unicodes=cps); s.subset(f)
n = f['name']
copy = n.getDebugName(0)
for r in list(n.names):
    if r.nameID not in (0, 5, 8, 11, 13, 14): n.removeNames(nameID=r.nameID)
for i, v in ((1, 'TD Symboles'), (2, 'Book'), (3, 'TD Symboles (sous-ensemble de DejaVu Sans 2.37)'), (4, 'TD Symboles'), (6, 'TDSymboles'), (16, 'TD Symboles'), (17, 'Book')):
    n.setName(v, i, 3, 1, 0x409)
for r in list(n.names):
    if r.platformID != 3: n.names.remove(r)
f.flavor = 'woff2'; f.save(sortie)
print(sorted(chr(c) for c in TTFont(sortie).getBestCmap()))
print(UNI)
