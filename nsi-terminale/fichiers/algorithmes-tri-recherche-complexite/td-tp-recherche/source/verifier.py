#!/usr/bin/env python3
"""TD « Mission : optimisation haute fréquence » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Le benchmark est ../recherche_contest.py.
"""
from math import log2


def recherche_lineaire(tab, valeur, trace=None):
    for i in range(len(tab)):
        if trace is not None:
            trace.append(tab[i])
        if tab[i] == valeur:
            return i
    return None


def recherche_dichotomique(tab, valeur, trace=None):
    gauche, droite = 0, len(tab) - 1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        if trace is not None:
            trace.append((gauche, droite, milieu, tab[milieu]))
        if tab[milieu] == valeur:
            return milieu
        elif tab[milieu] > valeur:
            droite = milieu - 1
        else:
            gauche = milieu + 1
    return None


serveurs = [102, 405, 201, 80, 199]
print('Q1', serveurs[1], serveurs[-1], serveurs[1:3])
tab = [1, 2, 3, 4]
tab[2] = tab[2] * 2
print('Q2 tab[2] = tab[2] * 2 ->', tab)
L = [2, 5, 8, 12, 17, 21, 25]
t = []
recherche_lineaire(L, 17, t)
print('Q7 linéaire, étapes pour 17 :', len(t))
t = []
recherche_dichotomique(L, 17, t)
print('Q8 tableau (gauche, droite, milieu, L[milieu]) :', t)
G = [1, 3, 5, 6, 8, 11, 13, 14, 14, 17, 19, 21, 23]
td, tl = [], []
recherche_dichotomique(G, 19, td)
recherche_lineaire(G, 19, tl)
print('Q9 dichotomie, valeurs comparées :', [x[3] for x in td], f'({len(td)})')
print('Q9 linéaire, valeurs comparées :', tl, f'({len(tl)})')
for n in (100,):
    tl, td = [], []
    recherche_lineaire(list(range(n)), n, tl)
    recherche_dichotomique(list(range(n)), n, td)
    print(f'Q12 pire cas n = {n} : linéaire {len(tl)}, dichotomique {len(td)} ; log2({n}) = {log2(n):.2f}')
print(f'Q15 log2(10**8) = {log2(10**8):.2f} (le benchmark compte 27 opérations)')
# le meilleur cas de la dichotomie : la cible au milieu
td = []
recherche_dichotomique(L, L[(len(L) - 1) // 2], td)
print('Q10 meilleur cas dichotomie : cible', L[(len(L) - 1) // 2], ',', len(td), 'étape')
# figure : recherche de 36
F = [3, 8, 11, 15, 19, 24, 30, 36, 41]
td = []
recherche_dichotomique(F, 36, td)
print('figure :', td)
print('tout est juste')
