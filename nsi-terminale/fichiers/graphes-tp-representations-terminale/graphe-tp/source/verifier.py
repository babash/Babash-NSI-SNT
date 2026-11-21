#!/usr/bin/env python3
"""TP « représentations d'un graphe » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13).
"""
import time

graph_edges = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D')]
for u, v in graph_edges:
    print(f"Lien entre {u} et {v}")

graph_adj = {'A': ['B', 'C'], 'B': ['A', 'C'], 'C': ['A', 'B', 'D'], 'D': ['C']}


def compte_voisins(graphe, sommet):
    return len(graphe[sommet])


print(f"Voisins de C : {compte_voisins(graph_adj, 'C')}")


class Graphe:
    def __init__(self):
        self.adjacence = {}

    def ajouter_sommet(self, sommet):
        if sommet not in self.adjacence:
            self.adjacence[sommet] = []

    def ajouter_arete(self, u, v):
        self.ajouter_sommet(u)
        self.ajouter_sommet(v)
        self.adjacence[u].append(v)
        self.adjacence[v].append(u)

    def afficher(self):
        for sommet, voisins in self.adjacence.items():
            print(f"{sommet} -> {', '.join(voisins)}")


g = Graphe()
for u, v in graph_edges:
    g.ajouter_arete(u, v)
g.afficher()

# Pour aller plus loin : chercher D parmi les voisins de A, sur un grand graphe
n = 200_000
aretes = [(i, i + 1) for i in range(n)] + [('A', 'B')]
adj = {'A': ['B']}
t0 = time.perf_counter(); r1 = any({u, v} == {'A', 'D'} for u, v in aretes); t1 = time.perf_counter()
r2 = 'D' in adj['A']; t2 = time.perf_counter()
print(f'liste d\'arêtes : {len(aretes)} arêtes parcourues, {t1 - t0:.4f} s ; dictionnaire : {len(adj["A"])} voisin regardé, {t2 - t1:.6f} s ; résultats {r1} {r2}')
routes = [('A', 'B', 5), ('A', 'C', 3)]
for u, v, poids in routes:
    print(f"{u}-{v} : {poids} km")


# Les tests cachés de la page passent sur la correction de la page
def tests_de_la_page():
    import html
    import os
    import re
    page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html'), encoding='utf-8').read()
    for sec in re.findall(r'<section class="td-q" data-type="code".*?</section>', page, re.S):
        nom = re.search(r'id="([^"]+)"', sec).group(1)
        corr = re.search(r'<pre class="td-code" data-verifier="correction">\n?(.*?)</pre>', sec, re.S)
        tests = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', sec, re.S)
        g = {}
        exec(html.unescape(corr.group(1)), g)
        if tests:
            exec(tests.group(1), g)
        print(f'{nom} : la correction passe les tests de la page')


tests_de_la_page()
print('tout est juste')
