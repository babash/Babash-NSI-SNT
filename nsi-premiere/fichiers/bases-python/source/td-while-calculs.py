#!/usr/bin/env python3
"""TD boucle while : les réponses qui ne passent pas par verifier.py, obtenues par exécution.

Usage : python3 -I nsi-premiere/fichiers/bases-python/source/td-while-calculs.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculs import ok, robot, sortie, tourne_sans_fin, tours, verifier_tests

# feuille 1, question 9 : i = i + 1 hors de la boucle, la boucle ne s'arrête pas
ok('f1 q9 (boucle infinie)', tourne_sans_fin('i = 1\nwhile i <= 5:\n    print(i)\ni = i + 1\n'), True)
# feuille 1, question 10 : depuis A6, le robot s'écrase en partant de D6 (vers E6)
_, trajet, _, err, _ = robot.executer('while not obstacleNord():\n    est()\n', 'for')
ok('f1 q10', (trajet, err), (['A6', 'B6', 'C6', 'D6'], "le robot s'écrase en partant de D6"))
# feuille 2, questions 8 et 11 ; feuille 3, question 2 : nombres de tours
ok('f2 q8 (tours)', tours('while not obstacleEst():\n    est()\n'), 3)
ok('f2 q11 (tours)', tours('nord()\nest()\nwhile obstacleNord():\n    est()\nnord()\n'), 3)
ok('f3 q2 (tours)', tours('while not obstacleEst():\n    if obstacleNord():\n        est()\n    else:\n        nord()\n'), 2)
# feuille 3, questions 7 et 9
REBOURS = 'def compte_a_rebours(n):\n    while n > 0:\n        print(n)\n        n = n - 1\n    print("Partez !")\n'
ok('f3 q7 (compte_a_rebours(3))', sortie(REBOURS + 'compte_a_rebours(3)\n'), '3\n2\n1\nPartez !\n')
SOMME = 'def somme_jusqua(n):\n    somme = 0\n    i = 1\n    while i <= n:\n        somme = somme + i\n        i = i + 1\n    return somme\n'
ok('f3 q9 (somme_jusqua(4))', sortie(SOMME + 'print(somme_jusqua(4))\n'), '10\n')
# feuille 3 : les tests du moteur, sur les corrections
verifier_tests('td-while-3.html')
