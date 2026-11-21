"""Corrigé de l'opération « Le Casse du Siècle » : chaque réponse est calculée (Python 3.13).
Lancer : python3 -I corrige-casse-du-siecle.py"""
from itertools import combinations


def glouton(objets, limite, cle):
    """Prend les objets dans l'ordre de priorité (cle décroissante), sans revenir en arrière."""
    sac, poids = [], 0
    for nom in sorted(objets, key=cle, reverse=True):
        if poids + objets[nom][0] <= limite:
            sac.append(nom)
            poids += objets[nom][0]
    return sac, poids, sum(objets[n][1] for n in sac)


def exhaustif(objets, limite):
    meilleur = ([], 0, 0)
    for k in range(len(objets) + 1):
        for c in combinations(objets, k):
            p = sum(objets[n][0] for n in c)
            v = sum(objets[n][1] for n in c)
            if p <= limite and v > meilleur[2]:
                meilleur = (list(c), p, v)
    return meilleur


reserve = {"Lingot de plomb": [10, 50], "Poudre d'escampette": [2, 40], "Micro-film": [1, 30], "Calice ancien": [5, 10]}
ratio = {n: reserve[n][1] / reserve[n][0] for n in reserve}
print("q1 ratios :", ratio)
print("q2, q3 meilleur ratio :", max(ratio, key=ratio.get))
print("q4 plus cher :", glouton(reserve, 10, lambda n: reserve[n][1]))
print("q4 ratio     :", glouton(reserve, 10, lambda n: ratio[n]))
coffre = {"Objet A": [6, 66], "Objet B": [5, 50], "Objet C": [5, 50]}
print("q5-q7 glouton ratio :", glouton(coffre, 10, lambda n: coffre[n][1] / coffre[n][0]))
print("q8-q9 meilleure solution :", exhaustif(coffre, 10))
print("q11 :", 2 ** 25, " q12 :", 2 ** 26, 2 ** 26 / 2 ** 25)
print("q13 : 50 objets à un million de combinaisons par seconde :", round(2 ** 50 / 1e6 / (365.25 * 86400), 1), "ans")
s = 2 ** 100 * 100 / 3e9
print(f"q14-q15 : 2**100 = {2 ** 100:.3e} ; {s:.2e} s = {s / (365.25 * 86400):.2e} ans")


def rendu_glouton(somme):
    pieces = [4, 3, 1]
    solution = []
    for p in pieces:
        while somme >= p:
            solution.append(p)
            somme = somme - p
    return solution


def rendu_exhaustif(somme):
    possibilites = [[4, 1, 1], [3, 3], [3, 1, 1, 1], [1, 1, 1, 1, 1, 1]]
    meilleure_sol = possibilites[0]
    for combi in possibilites:
        if len(combi) < len(meilleure_sol):
            meilleure_sol = combi
    return meilleure_sol


print("q16-q17 :", rendu_glouton(6), len(rendu_glouton(6)), "pièces")
print("q18-q19 :", rendu_exhaustif(6), len(rendu_exhaustif(6)), "pièces")
