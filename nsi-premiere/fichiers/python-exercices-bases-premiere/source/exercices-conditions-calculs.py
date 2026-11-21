#!/usr/bin/env python3
"""Feuille d'exercices « les conditions » (jeu de dés) : les réponses, par exécution réelle.

Les dés sont fixés en remplaçant randint par une fonction qui renvoie les valeurs de la question.
Usage (à la racine du dépôt) :
  python3 -I nsi-premiere/fichiers/bases-python/source/verifier.py nsi-premiere/fichiers/python-exercices-bases-premiere/exercices-conditions.html
  python3 -I nsi-premiere/fichiers/python-exercices-bases-premiere/source/exercices-conditions-calculs.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bases-python', 'source'))
from calculs import ok, sortie  # noqa: E402

P1 = 'from random import randint\n# randint(1,6) tire au hasard une valeur entière comprise entre 1 et 6\nde1 = randint(1,6)\nde2 = randint(1,6)\nde3 = randint(1,6)\nscore = 0\nif de1 != de2 and de2 != de3 and de1 != de3 :\n    score = de1 + de2 + de3\n    print("Vous marquez ",score," points")\nelse :\n    print("Il y a au moins 2 dés identiques")'
P2 = 'from random import randint\n# randint(1,6) tire au hasard une valeur entière comprise entre 1 et 6\nde1 = randint(1,6)\nde2 = randint(1,6)\nde3 = randint(1,6)\nscore = 0\nif de1 == de2 == de3 :\n    score = 30\n    print("Vous marquez ",score," points")\nelse :\n    print("Vous n\'avez pas eu 3 dés identiques")'
P3 = 'from random import randint\n# randint(1,6) tire au hasard une valeur entière comprise entre 1 et 6\nde1 = randint(1,6)\nde2 = randint(1,6)\nde3 = randint(1,6)\nscore = 0\nif de1 == de2 :\n    score = 20\n    print("Vous marquez ",score," points")\nelif de1 == de3 :\n    score = 20\n    print("Vous marquez ",score," points")\nelif de2 == de3 :\n    score = 20\n    print("Vous marquez ",score," points")\nelse :\n    print("Vous n\'avez pas eu 2 dés identiques")'
P4 = 'from random import randint\n# randint(1,6) tire au hasard une valeur entière comprise entre 1 et 6\nde1 = randint(1,6)\nde2 = randint(1,6)\nde3 = randint(1,6)\nscore = 0\nif de1 != de2 != de3 :\n    score = de1+de2+de3\nelif de1 == de2 :\n    score = 20\nelif de1 == de3 :\n    score = 20\nelif de2 == de3 :\n    score = 20\nelif de1 == de2 == de3 :\n    score = 30\nprint("Vous marquez ",score," points")'


def lancer(prog, des):
    """Le programme, avec randint qui renvoie les dés donnés ; renvoie (affichage, score)."""
    valeurs = iter(des)
    import random
    ancien = random.randint
    random.randint = lambda a, b: next(valeurs)
    try:
        g = {}
        out = sortie(prog, g)
    finally:
        random.randint = ancien
    return ' '.join(out.split()), g['score']


ok('f1 q3 (1, 4, 6)', lancer(P1, (1, 4, 6)), ('Vous marquez 11 points', 11))
ok('f1 q4 (1, 4, 4)', lancer(P1, (1, 4, 4)), ('Il y a au moins 2 dés identiques', 0))
ok('f1 q8 (1, 4, 6)', lancer(P2, (1, 4, 6)), ("Vous n'avez pas eu 3 dés identiques", 0))
ok('f1 q9 (4, 4, 4)', lancer(P2, (4, 4, 4)), ('Vous marquez 30 points', 30))
ok('f2 q2 (3, 4, 4)', lancer(P3, (3, 4, 4)), ('Vous marquez 20 points', 20))
ok('f2 q4 (4, 4, 4)', lancer(P3, (4, 4, 4)), ('Vous marquez 20 points', 20))
ok('f2 q5 (3, 6, 4)', lancer(P4, (3, 6, 4)), ('Vous marquez 13 points', 13))
ok('f2 q6 (3, 4, 4)', lancer(P4, (3, 4, 4)), ('Vous marquez 20 points', 20))
ok('f2 q7 (4, 4, 4)', lancer(P4, (4, 4, 4)), ('Vous marquez 20 points', 20))
# f2 q8 : la note de la correction (3, 4, 3 donne 10 au lieu de 20) et la correction proposée
ok('f2 q8 (3, 4, 3)', lancer(P4, (3, 4, 3))[1], 10)
P4_corrige = P4.replace('if de1 != de2 != de3 :\n    score = de1+de2+de3\n', 'if de1 == de2 == de3 :\n    score = 30\nelif de1 != de2 != de3 :\n    score = de1+de2+de3\n').replace('elif de1 == de2 == de3 :\n    score = 30\n', '')
ok('f2 q8 (corrigé, 4, 4, 4)', lancer(P4_corrige, (4, 4, 4))[1], 30)
# f3 q1 : le mois
MOIS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'exercices-conditions-3.html'), encoding='utf-8').read()
import html
import re
corr = html.unescape(re.search(r'<div class="td-correction"><pre class="td-code">\n(.*?)</pre>', MOIS, re.S).group(1))
for m, j in (('Mars', '31'), ('Février', '28'), ('Juin', '30'), ('Août', '31')):
    ok('f3 q1 ' + m, sortie(corr, {'input': lambda invite='': m}), f'Le mois de {m} a {j} jours.\n')
