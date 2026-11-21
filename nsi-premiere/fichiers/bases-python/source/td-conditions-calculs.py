#!/usr/bin/env python3
"""TD instructions conditionnelles : les réponses qui ne passent pas par verifier.py, obtenues par exécution.

Usage : python3 -I nsi-premiere/fichiers/bases-python/source/td-conditions-calculs.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculs import ok, sortie, verifier_tests  # noqa: E402

# feuille 1, question 10 : « Très bien » ne s'affiche jamais (on essaie toutes les notes de 0 à 20)
NOTES = 'if note >= 10:\n    print("Passable")\nelif note >= 16:\n    print("Très bien")\n'
ok('f1 q10', any('Très bien' in sortie(NOTES, {'note': n}) for n in range(21)), False)
# feuille 3 : signe, acces_manege
SIGNE = 'def signe(n):\n    if n > 0:\n        return "positif"\n    elif n < 0:\n        return "négatif"\n    else:\n        return "nul"\n'
ok('f3 q5 signe(-3)', sortie(SIGNE + 'print(signe(-3))'), 'négatif\n')
ok('f3 q6 signe(0)', sortie(SIGNE + 'print(signe(0))'), 'nul\n')
MANEGE = 'def acces_manege(age, taille):\n    if age >= 8 and taille >= 1.3:\n        return True\n    else:\n        return False\n'
ok('f3 q8 acces_manege(10, 1.25)', sortie(MANEGE + 'print(acces_manege(10, 1.25))'), 'False\n')
# feuille 3, question 9 : la version en une ligne donne les mêmes résultats
UNE = 'def acces_manege(age, taille):\n    return age >= 8 and taille >= 1.3\n'
essais = 'for a in range(5, 12):\n    for t in (1.2, 1.29, 1.3, 1.31, 1.5):\n        print(acces_manege(a, t))\n'
ok('f3 q9 (une ligne = la fonction complète)', sortie(UNE + essais) == sortie(MANEGE + essais), True)
verifier_tests('td-conditions-3.html')
