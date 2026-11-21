# Benchmark des recherches : linéaire contre dichotomique, dans le pire cas
# (la cible n'est pas dans le tableau et elle est plus grande que tout).
# TD « Mission : optimisation haute fréquence » - Babash - NSI Tani Malandi
# et Johanne Bakalara - CC BY-SA 4.0
# On utilise range(n) : il se lit comme une liste triée, sans occuper la mémoire.
# Pour n = 100 000 000, la recherche linéaire prend de quelques secondes à plus
# d'une minute, selon l'ordinateur : patience !
import time


def recherche_lineaire(tab, valeur):
    operations = 0
    for i in range(len(tab)):
        operations = operations + 1          # une comparaison
        if tab[i] == valeur:
            return i, operations
    return None, operations


def recherche_dichotomique(tab, valeur):
    operations = 0
    gauche = 0
    droite = len(tab) - 1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        operations = operations + 1          # une comparaison avec tab[milieu]
        if tab[milieu] == valeur:
            return milieu, operations
        elif tab[milieu] > valeur:
            droite = milieu - 1
        else:
            gauche = milieu + 1
    return None, operations


for n in (10, 1_000, 1_000_000, 100_000_000):
    tab = range(n)
    cible = n                                # absente, plus grande que tout
    t0 = time.perf_counter()
    _, op_lin = recherche_lineaire(tab, cible)
    t1 = time.perf_counter()
    _, op_dicho = recherche_dichotomique(tab, cible)
    t2 = time.perf_counter()
    print(f"n = {n:>11} | linéaire : {t1 - t0:9.6f} s, {op_lin:>11} opérations"
          f" | dichotomique : {t2 - t1:9.6f} s, {op_dicho:>2} opérations")
