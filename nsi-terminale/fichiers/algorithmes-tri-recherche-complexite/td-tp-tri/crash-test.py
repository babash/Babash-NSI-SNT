"""Crash test des serveurs : le programme de mesure du TD-TP « Le bal des tris ».

Lance-le sur ton poste (Python 3) : il trie des listes de 1 000, 10 000 et 100 000 nombres
tirés au hasard, avec les trois tris du TD, et affiche pour chacun le temps et le nombre
d'opérations (ici, les comparaisons entre deux éléments du tableau).
Un tri qui dépasse 5 minutes est arrêté : note « ÉCHEC » dans ton tableau.

Babash - NSI Tani Malandi et Johanne Bakalara · CC BY-SA 4.0 · conçu avec l'aide de l'IA
"""
import random
import sys
import time

LIMITE = 5 * 60          # secondes : au-delà, le tri est arrêté (« ÉCHEC »)
TAILLES = [1_000, 10_000, 100_000]
sys.setrecursionlimit(10_000)


class Echec(Exception):
    """Le tri a dépassé la limite de temps."""


class Compteur:
    """Compte les comparaisons et surveille le temps."""
    def __init__(self):
        self.operations = 0
        self.debut = time.perf_counter()

    def compter(self):
        self.operations += 1
        if self.operations % 1_000_000 == 0 and time.perf_counter() - self.debut > LIMITE:
            raise Echec


def tri_selection(tab, c):
    n = len(tab)
    for i in range(n - 1):
        i_min = i
        for j in range(i + 1, n):
            c.compter()
            if tab[j] < tab[i_min]:
                i_min = j
        tab[i], tab[i_min] = tab[i_min], tab[i]
    return tab


def tri_insertion(tab, c):
    for i in range(1, len(tab)):
        cle = tab[i]
        j = i - 1
        while j >= 0:
            c.compter()
            if tab[j] <= cle:
                break
            tab[j + 1] = tab[j]
            j = j - 1
        tab[j + 1] = cle
    return tab


def fusion(gauche, droite, c):
    resultat = []
    i, j = 0, 0
    while i < len(gauche) and j < len(droite):
        c.compter()
        if gauche[i] <= droite[j]:
            resultat.append(gauche[i])
            i = i + 1
        else:
            resultat.append(droite[j])
            j = j + 1
    return resultat + gauche[i:] + droite[j:]


def tri_fusion(tab, c):
    if len(tab) <= 1:
        return tab
    milieu = len(tab) // 2
    return fusion(tri_fusion(tab[:milieu], c), tri_fusion(tab[milieu:], c), c)


def mesurer(tri, tab):
    c = Compteur()
    copie = list(tab)
    try:
        resultat = tri(copie, c)
    except Echec:
        return "ÉCHEC", "ÉCHEC"
    assert resultat == sorted(tab), "le tri est faux"
    return f"{time.perf_counter() - c.debut:.3f} s", f"{c.operations:,}".replace(",", " ")


if __name__ == "__main__":
    print(f"{'taille':>8} | {'tri':<10} | {'temps':>10} | {'opérations':>15}")
    for n in TAILLES:
        tab = [random.randint(0, 1_000_000) for _ in range(n)]
        for nom, tri in (("sélection", tri_selection), ("insertion", tri_insertion), ("fusion", tri_fusion)):
            temps, operations = mesurer(tri, tab)
            print(f"{n:>8} | {nom:<10} | {temps:>10} | {operations:>15}", flush=True)
