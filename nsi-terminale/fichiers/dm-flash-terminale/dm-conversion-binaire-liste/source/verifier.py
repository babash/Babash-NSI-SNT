#!/usr/bin/env python3
"""DM « conversion binaire et liste » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13).
"""

# Exercice 1, question 1 : un octet (8 bits), bit de poids fort à gauche
for n in (2, 156, 89):
    octet = format(n, '08b')
    calcul = ' + '.join(f'2^{7 - i}' for i, b in enumerate(octet) if b == '1')
    print(f'Q1 {n} = {calcul} -> {octet}')

# Exercice 1, question 2 : vers le décimal
for b in ('1000001', '101', '111111110'):
    calcul = ' + '.join(f'2^{len(b) - 1 - i}' for i, c in enumerate(b) if c == '1')
    print(f'Q2 {b} = {calcul} = {int(b, 2)}')


# Exercice 2 : la correction de la page (parcours par index)
def convertir(tab):
    """
    tab est un tableau d'entiers, dont les éléments sont 0 ou 1,
    et représentant un entier écrit en binaire.
    Renvoie l'écriture décimale de l'entier positif dont la
    représentation binaire est donnée par le tableau tab
    """
    n = len(tab)
    resultat = 0
    for i in range(n):
        resultat = resultat + tab[i] * 2 ** (n - 1 - i)
    return resultat


# l'autre correction donnée (méthode de Horner)
def convertir_horner(tab):
    resultat = 0
    for i in range(len(tab)):
        resultat = resultat * 2 + tab[i]
    return resultat


TESTS = [([1, 0, 1, 0, 0, 1, 1], 83), ([1, 0, 0, 0, 0, 0, 1, 0], 130),
         ([0], 0), ([1], 1), ([1, 1, 1, 1, 1, 1, 1, 1], 255), ([0, 0, 1, 0, 1], 5)]
for f in (convertir, convertir_horner):
    for t, r in TESTS:
        assert f(t) == r, (f.__name__, t, f(t))
        assert int(''.join(map(str, t)), 2) == r
print('Q3 convertir([1, 0, 1, 0, 0, 1, 1]) =', convertir([1, 0, 1, 0, 0, 1, 1]))
print('Q3 convertir([1, 0, 0, 0, 0, 0, 1, 0]) =', convertir([1, 0, 0, 0, 0, 0, 1, 0]))


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
