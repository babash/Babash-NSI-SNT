"""Corrigé de la feuille « Les listes » : les réponses calculées par exécution.

Lancer : python3 -I corrige-exercices-listes.py (Python 3.13).
Les trois programmes de l'énoncé sont exécutés tels quels, avec une trace de chaque tour.
"""
import subprocess
import sys


def lancer(code, saisie=''):
    r = subprocess.run([sys.executable, '-I', '-c', code], input=saisie, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


# Exercice 1 : recherche linéaire
RECHERCHE = '''def recherche(l, x):
    for i in range(len(l)) :
        if l[i] == x:
            return i
    return -1

l = [2,1,11,7,2,6]
x = int(input("Donner une valeur : "))
print(recherche(l, x))
'''
print('Ex. 1, saisie 7 :', lancer(RECHERCHE, '7\n'))
print('Ex. 1, type de l :', type([2, 1, 11, 7, 2, 6]).__name__)
l, x = [2, 1, 11, 7, 2, 6], 7
for i in range(len(l)):
    print(f'  tour {i} : i = {i}, l[i] = {l[i]}, l[i] == x : {l[i] == x}')
    if l[i] == x:
        print('  renvoie', i)
        break
exec(RECHERCHE.split('\nl = ')[0], g := {})
for l2, x2 in (([2, 1, 11], 7), ([], 3), ([1, 0], 5), ([6, 1, 11], 11)):
    print(f'  recherche({l2}, {x2}) =', g['recherche'](l2, x2))

# Exercice 2 : maximum
MAXI = '''tab = [9, 100, 8, 48, 73]
imax, vmax = 0, tab[0]
for i in range(len(tab)):
    print(f"  tour {i} : i = {i}, tab[i] = {tab[i]}, tab[i] > vmax : {tab[i] > vmax}", end="")
    if tab[i] > vmax:
        vmax = tab[i]
        imax = i
    print(f", vmax = {vmax}, imax = {imax}")
print(vmax, imax)
'''
print('Ex. 2 :\n' + lancer(MAXI))
for t in ([10, 4, 8, 88, 10], [-10, -2, -10]):
    print(f'  tab = {t} :', lancer(MAXI.replace('[9, 100, 8, 48, 73]', str(t))).splitlines()[-1])

# Exercice 3 : vérification du tri
TRI = '''tab = [0, 5, 8, 8, 9]
tri = True
for i in range(len(tab)-1):
    print(f"  tour {i} : i = {i}, tab[i] = {tab[i]}, tab[i+1] = {tab[i+1]}, tab[i] > tab[i+1] : {tab[i] > tab[i+1]}")
    if tab[i] > tab[i+1]:
        tri = False
print(tri)
'''
print('Ex. 3 :\n' + lancer(TRI))
for t in ([8, 12, 4], [-1, 4], [5]):
    print(f'  tab = {t} :', lancer(TRI.replace('[0, 5, 8, 8, 9]', str(t))).splitlines()[-1])
