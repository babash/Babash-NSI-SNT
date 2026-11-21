#!/usr/bin/env python3
"""DM flash « piles et files » : toutes les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Affiche les réponses et vérifie :
- le tableau d'avancement (question 3) et les piles renvoyées (question 4) ;
- la fonction à compléter (question 6) : toutes les réponses acceptées par la page
  passent les tests, et des versions volontairement fausses les ratent.
"""
import itertools


def tri_pair(p):
    p_pair = []
    while p != []:
        v = p.pop()
        if v % 2 == 0:
            p_pair.append(v)
    return p_pair


# Question 3 : l'état à la fin de chaque tour
p = [5, 2, 6, 7, 1]
p_pair = []
print('Q3 tour 0 :', (None, list(p), None, list(p_pair)))
tour = 0
while p != []:
    v = p.pop()
    c = v % 2 == 0
    if c:
        p_pair.append(v)
    tour += 1
    print(f'Q3 tour {tour} :', (v, list(p), c, list(p_pair)))
print('Q3 nombre de tours :', tour)

# Question 4 : les piles renvoyées (et p vidée)
for depart in ([-1, 144, -10, 23], [233, 677, 99, 3, 73, 75, 91], [12, 5, 8, 6, 2]):
    q = list(depart)
    print('Q4', depart, '->', tri_pair(q), '; p à la fin :', q)
print('Q5 contre-exemple de « trié » :', tri_pair([2, 6, 4]))
print('Q2 -1 % 2 =', -1 % 2)

# Question 6 : le code à trous, avec chaque réponse acceptée
TROU = '''
def tri_pair(p):
    p_pair = []
    {a}
    while p != []:
        v = p.pop()
        if v%2 == 0 :
            p_pair.append(v)
        {b}
            {c}
    return {d}
'''
A = ['p_impair = []']
B = ['else:', 'elif v % 2 != 0:', 'elif v % 2 == 1:', 'elif not v % 2 == 0:', 'elif v % 2:']
C = ['p_impair.append(v)']
D = ['p_pair, p_impair', '(p_pair, p_impair)', '[p_pair, p_impair]']


def tests(f):
    r = f([5, 2, 6, 7, 1])
    assert list(r) == [[6, 2], [1, 7, 5]], f'tri_pair([5, 2, 6, 7, 1]) renvoie {r}'
    r = f([])
    assert list(r) == [[], []], f'tri_pair([]) renvoie {r}'
    r = f([-3, -4])
    assert list(r) == [[-4], [-3]], f'tri_pair([-3, -4]) renvoie {r}'


def charger(src):
    g = {}
    exec(src, g)
    return g['tri_pair']


n = 0
for a, b, c, d in itertools.product(A, B, C, D):
    tests(charger(TROU.format(a=a, b=b, c=c, d=d)))
    n += 1
print(f'Q6 : {n} combinaisons acceptées, toutes passent les tests')

FAUSSES = {
    'renvoie seulement p_pair': dict(a=A[0], b=B[0], c=C[0], d='p_pair'),
    'if au lieu de else (tous les impairs perdus)': dict(a=A[0], b='if v % 2 == 0:', c=C[0], d=D[0]),
    'ajoute dans p_pair au lieu de p_impair': dict(a=A[0], b=B[0], c='p_pair.append(v)', d=D[0]),
    'ordre inversé du résultat': dict(a=A[0], b=B[0], c=C[0], d='p_impair, p_pair'),
    'elif v % 2 == -1 (oublie que -3 % 2 vaut 1)': dict(a=A[0], b='elif v % 2 == -1:', c=C[0], d=D[0]),
}
for nom, t in FAUSSES.items():
    try:
        tests(charger(TROU.format(**t)))
    except AssertionError as e:
        print('Q6 version fausse rejetée :', nom, '->', e)
    else:
        raise SystemExit('ERREUR : une version fausse passe les tests : ' + nom)
print('tout est juste')
