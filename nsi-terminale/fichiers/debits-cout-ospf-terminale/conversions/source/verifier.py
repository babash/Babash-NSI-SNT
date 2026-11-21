#!/usr/bin/env python3
"""Exercices de conversion (débits et coût OSPF) : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Calculs exacts avec fractions.
"""
from fractions import Fraction as F
from math import ceil, log10

k, M, G = 10**3, 10**6, 10**9
REF = 10**8          # débit de référence : 100 Mbits/s


def joli(x):
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else str(float(x))


print('Ex1 :', joli(F(10_000_000, M)), 'Mbits/s ;', joli(F(100 * M, G)), 'Gbits/s ;', joli(F(10 * G, M)), 'Mbits/s ;', 20 * M, 'bits/s')
print('Ex2 exposants :', int(log10(M)), int(log10(G)), int(log10(G // M)), int(log10(100 * M)), int(log10(2 * G // 2)))
for nom, debit in (('Ethernet', 10 * M), ('Fast Ethernet', 100 * M), ('Giga Ethernet', G), ('Fibre', 10 * G)):
    c = F(REF, debit)
    print(f'Ex2 tableau {nom} : {joli(c)} -> arrondi à l\'entier supérieur {ceil(c)}')
for b in (8, 6, 9):
    print(f'Ex3 10**8 / 10**{b} = 10**{8 - b} = {joli(F(10**8, 10**b))}')
for nom, debit in (('Satellite', 50 * M), ('Backbone', 10 * G)):
    print(f'Ex4 {nom} : {debit} bits/s, coût {joli(F(REF, debit))} (arrondi {ceil(F(REF, debit))})')
print('Ex5 : débit =', REF // 100, 'bits/s =', joli(F(REF // 100, M)), 'Mbits/s')
print('Ex6.1 : 100 Mbits/s / 1 Gbits/s =', joli(F(100 * M, G)), '(et non 100)')
cg, ce = max(1, ceil(F(REF, G))), ceil(F(REF, 10 * M))
print(f'Ex6.2 coût par lien : Giga {cg}, Ethernet {ce} ; chemin Giga (2 à 3 liens) : {2 * cg} à {3 * cg} ; chemin Ethernet (1 à 2 liens) : {ce} à {2 * ce}')
for cout, ref in ((100, REF), (10, REF), (1, REF), (50, G)):
    d = F(ref, cout)
    print(f'Ex7 coût {cout}, référence {ref} : débit {joli(d)} bits/s = {joli(d / M)} Mbits/s')
print('tout est juste')
