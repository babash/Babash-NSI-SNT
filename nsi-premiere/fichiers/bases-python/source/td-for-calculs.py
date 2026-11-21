#!/usr/bin/env python3
"""TD boucle for : les réponses qui ne passent pas par verifier.py, obtenues par exécution.

Usage : python3 -I nsi-premiere/fichiers/bases-python/source/td-for-calculs.py
Chaque ligne affiche le calcul puis OK ; une réponse fausse arrête le script.
"""
import contextlib
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import robot  # noqa: E402


def sortie(code, g=None):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(code, g if g is not None else {})
    return out.getvalue()


def ok(nom, obtenu, attendu):
    print(f'{nom} : {obtenu!r}', 'OK' if obtenu == attendu else f'FAUX (attendu {attendu!r})')
    if obtenu != attendu:
        sys.exit(1)


# feuille 1, question 10 : somme = 0 dans la boucle, le programme affiche 5
ok('f1 q10', sortie('for i in range(1, 6):\n    somme = 0\n    somme = somme + i\nprint(somme)\n'), '5\n')
# feuille 1, question 11 : depuis A6, 5 fois est() : le robot s'écrase au 4e pas (D6 vers E6)
case, trajet, _, err, _ = robot.executer('for i in range(5):\n    est()\n', 'for')
ok('f1 q11', (trajet, err), (['A6', 'B6', 'C6', 'D6'], "le robot s'écrase en partant de D6"))

# feuille 3 : les fonctions de l'exercice « Complète le code à partir d'un objectif »
TABLE = 'def table(n):\n    for i in range(1, 11):\n        print(n, "x", i, "=", n * i)\n'
ok('f3 q2 (dernière ligne de table(3))', sortie(TABLE + 'table(3)\n').splitlines()[-1], '3 x 10 = 30')
CARRES = 'def somme_carres(n):\n    s = 0\n    for i in range(1, n + 1):\n        s = s + i * i\n    return s\n'
ok('f3 q4 (somme_carres(3))', sortie(CARRES + 'print(somme_carres(3))\n'), '14\n')

# feuille 3 : les tests du moteur, lancés sur les corrections (comme dans la page)
page = open(os.path.join(ICI, '..', 'td-for-3.html'), encoding='utf-8').read()
tests = re.findall(r'<script type="text/x-python" class="td-tests">(.*?)</script>', page, re.S)
corr = [c.replace('&lt;', '<').replace('&gt;', '>') for c in
        re.findall(r'<pre class="td-code" data-verifier="correction">\n(.*?)</pre>', page, re.S)]
for k, (c, t) in enumerate(zip(corr, tests)):
    g = {}
    exec(c, g)
    exec(t, g)
    print(f'f3 tests du programme {k + 1} sur la correction : OK')
# les tests repèrent bien une fonction fausse
g = {}
exec('def aller(nb_nord, nb_est):\n    for i in range(nb_est):\n        est()\n    for i in range(nb_nord):\n        nord()\n', g)
try:
    exec(tests[1], g)
    sys.exit('f3 : les tests du robot acceptent une fonction fausse')
except AssertionError as e:
    print('f3 tests du robot, fonction fausse refusée :', e)
# feuille 3, question 8 (bonus) : aller(2, 3) depuis A6
_, trajet, _, err, _ = robot.executer('for i in range(2):\n    nord()\nfor i in range(3):\n    est()\n', 'for')
ok('f3 q8 (aller(2, 3))', (trajet, err), (['A6', 'A5', 'A4'], "le robot s'écrase en partant de A4"))
# feuille 3, question 7 : aller(3, 5) amène en F3
ok('f3 q7 (aller(3, 5))', robot.executer('for i in range(3):\n    nord()\nfor i in range(5):\n    est()\n', 'for')[0], 'F3')
