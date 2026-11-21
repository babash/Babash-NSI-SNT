#!/usr/bin/env python3
"""TD récapitulatif conditions et boucles : les réponses qui ne passent pas par verifier.py, par exécution.

Usage : python3 -I nsi-premiere/fichiers/bases-python/source/td-recapitulatif-calculs.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculs import ok, robot, sortie, tourne_sans_fin, verifier_tests  # noqa: E402

# feuille 1 : questions 3 et 4 (exemples donnés dans la correction)
MOT = 'for lettre in mot:\n    if lettre == "e":\n        print("Il y a un e !")\n'
ok('f1 q3 banane', sortie(MOT, {'mot': 'banane'}).count('Il y a un e !'), 1)
ok('f1 q3 dessert', sortie(MOT, {'mot': 'dessert'}).count('Il y a un e !'), 2)
saisies = iter(['4', '7', '2', '0'])
ok('f1 q4 (4, 7, 2, 0)', sortie('total = 0\nn = int(input("Nombre : "))\nwhile n != 0:\n    total = total + n\n    n = int(input("Nombre : "))\nprint(total)\n',
                               {'input': lambda m='': next(saisies)}), '13\n')
# feuille 1, question 10 : 6 affichages 0 1 1 2 2 2 ; sans décalage, 2
ok('f1 q10', sortie('nb = 0\nfor lettre in "banane":\n    if lettre == "a":\n        nb = nb + 1\n    print(nb)\n').split(), ['0', '1', '1', '2', '2', '2'])
ok('f1 q10 corrigé', sortie('nb = 0\nfor lettre in "banane":\n    if lettre == "a":\n        nb = nb + 1\nprint(nb)\n'), '2\n')
# feuille 1, question 11 : for i in range(4): nord() s'écrase ; la version while s'arrête en A3
_, trajet, _, err, _ = robot.executer('for i in range(4):\n    nord()\n', 'for')
ok('f1 q11 (for)', (trajet[-1], err), ('A3', "le robot s'écrase en partant de A3"))
ok('f1 q11 (while)', robot.executer('while not obstacleNord():\n    nord()\n', 'for')[0], 'A3')
# feuille 2 : programme A, valeurs de x après chaque tour
g = {}
ok('f2 q1 (x après chaque tour)', sortie('x = 1\nwhile x < 20:\n    x = x * 3\n    print(x)\n', g).split(), ['3', '9', '27'])
ok('f2 q4 (tours de range(2, 9, 3))', len(range(2, 9, 3)), 3)
# feuille 2, question 6 : valeur finale de n
ok('f2 q6 (n)', robot.executer('n = 0\nwhile not obstacleNord():\n    nord()\n    n = n + 1\nfor i in range(n):\n    est()\n', 'for')[4]['n'], 3)
# feuille 3, question 4 : nombre de « mur »
ok('f3 q4 (mur)', robot.executer('nord()\nwhile not obstacleEst():\n    est()\n    if obstacleNord():\n        print("mur")\n', 'for')[2].count('mur'), 4)
# feuille 3, question 8 : moyenne(3) avec 10, 14, 15
notes = iter(['10', '14', '15'])
ok('f3 q8 (moyenne(3))', sortie('def moyenne(n):\n    total = 0\n    for i in range(n):\n        note = int(input("Note : "))\n        total = total + note\n    return total / n\nprint(moyenne(3))\n',
                                {'input': lambda m='': next(notes)}), '13.0\n')
verifier_tests('td-recapitulatif-3.html')
