#!/usr/bin/env python3
"""Rappel : les fonctions (feuilles 1 et 2) : les réponses, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13)
Feuille 1 : paramètres de l'extrait (module ast), déroulés et sorties des fonctions mystère,
programme de décompte corrigé. Feuille 2 : tests cachés des pages lancés sur les corrections
(acceptées) et sur des versions fausses (refusées).
"""
import ast
import contextlib
import html
import io
import os
import re
from math import sqrt

ICI = os.path.dirname(os.path.abspath(__file__))
P1, P2 = os.path.join(ICI, '..', 'index.html'), os.path.join(ICI, '..', 'feuille-2.html')


def sortie(code):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        exec(code, {})
    return f.getvalue()


# feuille 1, q1 et q2 : les définitions de l'extrait et leur nombre de paramètres
t1 = open(P1, encoding='utf-8').read()
extrait = html.unescape(re.search(r'<pre class="td-code">\n(def _console_log_level.*?)</pre>', t1, re.S).group(1))
arbre = ast.parse(extrait)
print('q1-q2 définitions :', {n.name: len(n.args.args) for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef)})

# q8 : decompte corrigé
print('q8', sortie('''
def decompte(n):
    if n < 0:
        print("Vous devez donner un nombre positif")
        return
    print("Debut du decompte")
    for i in range(n):
        print(n-i)
    print(0, "!")
    print("Fin du decompte")

decompte(5)
decompte(-2)''').replace('\n', ' / '))

# q9 : déroulé de mystere(5)
a = 1
for i in range(1, 6):
    a = a * i
    print('q9 tour', i, ':', (i, a))
# q11, q13, q14, q16 : sorties
print('q11', sortie('''
def mystere(a, b):
    if a > b :
        temp = a
        a = b
        b = temp
    return a, b
print(mystere(46, 12), mystere(3, 8))''').strip())
print('q13', sortie('''
def mystere(tab, n):
    for i in range(len(tab)) :
        tab[i] = tab[i] * n
    return tab
print(mystere([3, 6, 10, 1, 0], 5))''').strip())
tab = [3, 6, 10, 1, 0, 4, 10, 6, 3]
print('q14 paires comparées :', [(tab[i - 1], tab[-i]) for i in range(1, 5)], '->', tab == tab[::-1])
pts = [[7, 9], [2, 5], [5, 2]]
print('q16 distances :', [round(sqrt(x * x + y * y), 3) for x, y in pts])

# feuille 2 : les tests des pages
TESTS = {}
for bloc in open(P2, encoding='utf-8').read().split('<section class="td-q')[1:]:
    bloc = bloc.split('</section>')[0]
    m = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', bloc, re.S)
    if m:
        TESTS[re.search(r'data-fichier="([^"]+)\.py"', bloc).group(1)] = m.group(1)
JUSTES = {
    'factorielle': 'def factorielle(n):\n    p = 1\n    for i in range(1, n + 1):\n        p = p * i\n    return p\n',
    'puissance': 'def puissance(x, n):\n    r = 1\n    for _ in range(n):\n        r = r * x\n    return r\n',
    'voyelles': 'def nombre_voyelles(chaine):\n    c = 0\n    for l in chaine:\n        if l in "aeiouy":\n            c = c + 1\n    return c\n',
    'second_degre': '''from math import sqrt
def solutions(a, b, c):
    delta = b**2 - 4*a*c
    if delta < 0:
        return []
    elif delta == 0:
        return [-b / (2*a)]
    else:
        return [(-b + sqrt(delta)) / (2*a), (-b - sqrt(delta)) / (2*a)]
''',
}
FAUSSES = {
    'factorielle': {'part de 0': JUSTES['factorielle'].replace('p = 1', 'p = 0'),
                    'oublie n': JUSTES['factorielle'].replace('range(1, n + 1)', 'range(1, n)'),
                    'affiche': JUSTES['factorielle'].replace('return p', 'print(p)')},
    'puissance': {'x * n': 'def puissance(x, n):\n    return x * n\n',
                  'un tour de trop': JUSTES['puissance'].replace('range(n)', 'range(n + 1)')},
    'voyelles': {'sans y': JUSTES['voyelles'].replace('aeiouy', 'aeiou'),
                 'compte les consonnes': JUSTES['voyelles'].replace('l in "aeiouy"', 'l not in "aeiouy"')},
    'second_degre': {'sans parenthèses': JUSTES['second_degre'].replace('/ (2*a)', '/ 2*a'),
                     'une solution oubliée': JUSTES['second_degre'].replace(', (-b - sqrt(delta)) / (2*a)]', ']'),
                     'delta = 0 en double': JUSTES['second_degre'].replace('delta < 0', 'delta < 0 and False').replace('elif delta == 0', 'elif delta < 0')},
}


def essayer(code, tests):
    g = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, g)
            exec(tests, g)
        return 'passe'
    except AssertionError as e:
        return 'refusée : ' + str(e)
    except Exception as e:
        return 'erreur : %r' % e


print('tests lus :', sorted(TESTS))
for nom, code in JUSTES.items():
    r = essayer(code, TESTS[nom])
    print(nom, 'correction :', r)
    assert r == 'passe', nom
    for f, faux in FAUSSES[nom].items():
        r = essayer(faux, TESTS[nom])
        print(nom, 'version fausse (%s) :' % f, r)
        assert r != 'passe', (nom, f)
print('solutions(2, 1, -1) =', essayer(JUSTES['second_degre'] + 'print(solutions(2, 1, -1))', '') and sortie(JUSTES['second_degre'] + 'print(solutions(2, 1, -1))').strip())
print('tout est juste')
