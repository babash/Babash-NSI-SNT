#!/usr/bin/env python3
"""DM « diviser pour régner : le tri fusion » : les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13).
"""
import math


def fusion(gauche, droite):
    resultat = []
    i = j = 0
    while i < len(gauche) and j < len(droite):
        if gauche[i] < droite[j]:
            resultat.append(gauche[i])
            i += 1
        else:
            resultat.append(droite[j])
            j += 1
    resultat.extend(gauche[i:])
    resultat.extend(droite[j:])
    return resultat


def tri_fusion(tab, prof=0):
    print('  ' * prof + 'découpe :', tab)
    if len(tab) <= 1:
        return tab
    milieu = len(tab) // 2
    gauche = tri_fusion(tab[:milieu], prof + 1)
    droite = tri_fusion(tab[milieu:], prof + 1)
    r = fusion(gauche, droite)
    print('  ' * prof + 'fusion :', gauche, '+', droite, '->', r)
    return r


# Question 1 : les étapes de la fusion, comparaison par comparaison
g, d = [0.9, 1.5], [1.2, 2.1]
i = j = 0
while i < len(g) and j < len(d):
    pp = g[i] if g[i] < d[j] else d[j]
    print(f'Q1 on compare {g[i]} et {d[j]} : le plus petit est {pp}')
    if g[i] < d[j]:
        i += 1
    else:
        j += 1
print('Q1 résultat :', fusion(g, d))

# Question 2 : l'arbre de division
print('Q2 :')
r = tri_fusion([1.5, 0.9, 2.1, 1.2])
assert r == [0.9, 1.2, 1.5, 2.1]

# Question 3 : combien de comparaisons, tableau déjà trié ou à l'envers (n = 1000)
compte = 0


def fusion_c(g, d):
    global compte
    res, i, j = [], 0, 0
    while i < len(g) and j < len(d):
        compte += 1
        if g[i] < d[j]:
            res.append(g[i]); i += 1
        else:
            res.append(d[j]); j += 1
    return res + g[i:] + d[j:]


def tri_fusion_c(t):
    if len(t) <= 1:
        return t
    m = len(t) // 2
    return fusion_c(tri_fusion_c(t[:m]), tri_fusion_c(t[m:]))


def insertion_c(t):
    global compte
    t = list(t)
    for i in range(1, len(t)):
        cle, j = t[i], i - 1
        while j >= 0:
            compte += 1
            if t[j] > cle:
                t[j + 1] = t[j]; j -= 1
            else:
                break
        t[j + 1] = cle
    return t


n = 1000
for nom, t in (('trié', list(range(n))), ('à l\'envers', list(range(n, 0, -1)))):
    compte = 0; tri_fusion_c(t); cf = compte
    compte = 0; insertion_c(t); ci = compte
    print(f'Q3 n={n}, tableau {nom} : tri fusion {cf} comparaisons, tri par insertion {ci}')
print('Q3 niveaux de découpage pour 1000 :', math.ceil(math.log2(n)), '; n log2(n) ≈', round(n * math.log2(n)))
print('Q4 cas de base :', tri_fusion([2.1]), tri_fusion([]))
print('tout est juste')


# Question 5 : sans le cas de base, tri_fusion([2.1]) ne s'arrête pas
def sans_cas_de_base(tab):
    milieu = len(tab) // 2
    return fusion(sans_cas_de_base(tab[:milieu]), sans_cas_de_base(tab[milieu:]))


try:
    sans_cas_de_base([2.1])
except RecursionError as e:
    print('Q5 sans cas de base :', type(e).__name__, '-', e)
