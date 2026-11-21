#!/usr/bin/env python3
"""DM « ranger les Lagonnet (tri par insertion) » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13).
"""


def tri_insertion(tab, bavard=False):
    decalages = 0
    for i in range(1, len(tab)):
        cle = tab[i]
        j = i - 1
        if bavard:
            print(f'  tour {i} : cle = {cle}, premier voisin comparé : {tab[j]} ; {tab[j]} > {cle} ? {tab[j] > cle}')
        while j >= 0 and tab[j] > cle:
            if bavard:
                print(f'    on décale {tab[j]}')
            tab[j + 1] = tab[j]
            j = j - 1
            decalages += 1
        tab[j + 1] = cle
        if bavard:
            print(f'    après le tour {i} : {tab}')
    return decalages


t = [1.5, 0.9, 2.1, 1.2]
print('Q1 à Q3 :')
tri_insertion(t, True)
print('Q3 tableau final :', t)
for nom, t in (('déjà rangés', [0.9, 1.2, 1.5, 2.1]), ('à l\'envers', [2.1, 1.5, 1.2, 0.9])):
    print(f'Q4/Q5 {nom} : {tri_insertion(list(t))} décalages')
for n in (100, 1000):
    print(f'Q6 n = {n}, à l\'envers : {tri_insertion(list(range(n, 0, -1)))} décalages ; déjà trié : {tri_insertion(list(range(n)))}')
print('tout est juste')
