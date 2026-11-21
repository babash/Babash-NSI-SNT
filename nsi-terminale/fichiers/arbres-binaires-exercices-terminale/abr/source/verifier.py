#!/usr/bin/env python3
"""TD « arbres binaires de recherche » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13).
"""

arbre = [8, [3, [1, None, None], [6, [4, None, None], [7, None, None]]], [10, None, [14, [13, None, None], None]]]


def est_abr(a, mini=float('-inf'), maxi=float('inf')):
    if a is None:
        return True
    return mini < a[0] < maxi and est_abr(a[1], mini, a[0]) and est_abr(a[2], a[0], maxi)


def infixe(a):
    return [] if a is None else infixe(a[1]) + [a[0]] + infixe(a[2])


def enfants(a, v):
    if a is None:
        return None
    if a[0] == v:
        return (a[1][0] if a[1] else None, a[2][0] if a[2] else None)
    return enfants(a[1], v) or enfants(a[2], v)


for v in (8, 3, 6, 10, 14):
    print(f'Q1 enfants de {v} : {enfants(arbre, v)}')
print('Q2 ABR ?', est_abr(arbre))
# Q3 : la construction nœud par nœud
n13 = [13, None, None]
n1 = [1, None, None]
n4 = [4, None, None]
n7 = [7, None, None]
n6 = [6, n4, n7]
n3 = [3, n1, n6]
n14 = [14, n13, None]
n10 = [10, None, n14]
n8 = [8, n3, n10]
print('Q3 n8 == arbre :', n8 == arbre)
print('Q4 infixe :', infixe(arbre), '; croissant :', infixe(arbre) == sorted(infixe(arbre)))
exemple = [20, [7, [4, [2, None, None], None], [15, [5, None, None], None]], [53, [46, [29, None, None], None], [80, [74, None, None], None]]]
print('arbre de l\'introduction : ABR ?', est_abr(exemple), '(5 est dans le sous-arbre droit de 7)')


def insertionABRnr(arbre, element):
    arbre_suivant = arbre
    while arbre_suivant is not None:
        arbre = arbre_suivant
        if arbre[0] > element:
            arbre_suivant = arbre[1]
        if arbre[0] < element:
            arbre_suivant = arbre[2]
    if arbre[0] > element:
        arbre[1] = [element, None, None]
        print(element, 'ajouté à gauche de', arbre[0])
    if arbre[0] < element:
        arbre[2] = [element, None, None]
        print(element, 'ajouté à droite de', arbre[0])


import copy
a = copy.deepcopy(arbre)
for e in (5, 12, 15, 0):
    insertionABRnr(a, e)
print('Q5 après insertions : ABR ?', est_abr(a), infixe(a))

# une valeur déjà présente : la boucle ne s'arrête pas (on le constate avec un délai)
import subprocess, sys
code = 'a = ' + repr(arbre) + '\n' + '''
def ins(arbre, element):
    arbre_suivant = arbre
    while arbre_suivant is not None:
        arbre = arbre_suivant
        if arbre[0] > element:
            arbre_suivant = arbre[1]
        if arbre[0] < element:
            arbre_suivant = arbre[2]
ins(a, 6)
'''
try:
    subprocess.run([sys.executable, '-I', '-c', code], timeout=2)
    print('valeur déjà présente : la boucle s\'arrête')
except subprocess.TimeoutExpired:
    print('valeur déjà présente (6) : la boucle ne s\'arrête pas (toujours en cours après 2 s)')


def rechercheABR(arbre, element):
    if arbre is None:
        return False
    else:
        if arbre[0] == element:
            return True
        if element < arbre[0]:
            return rechercheABR(arbre[1], element)
        if element > arbre[0]:
            return rechercheABR(arbre[2], element)


for e in range(0, 16):
    assert rechercheABR(arbre, e) == (e in infixe(arbre))
print('Q7 recherche : 13 ->', rechercheABR(arbre, 13), '; 5 ->', rechercheABR(arbre, 5))
print('tout est juste')
