#!/usr/bin/env python3
"""Feuille d'exercices « les boucles » : les réponses calculées, par exécution réelle.

Usage (à la racine du dépôt) :
  python3 -I nsi-premiere/fichiers/bases-python/source/verifier.py nsi-premiere/fichiers/python-exercices-bases-premiere/exercices-boucles.html
  python3 -I nsi-premiere/fichiers/python-exercices-bases-premiere/source/exercices-boucles-calculs.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bases-python', 'source'))
from calculs import ok, sortie  # noqa: E402

ok('q2 (100 - 1 - 2 - 3 - 4)', 100 - 1 - 2 - 3 - 4, int(sortie('total = 100\nfor i in range(1, 5):\n    total = total - i\nprint(total)')))
ok('q5 (1 x (-1) x 2)', 1 * (-1) * 2, -2)
ok('q7 (valeurs de total)', sortie('total = 0\nfor i in range(1, 3):\n    for j in range(1, 4):\n        ajout = i**j\n        total = total + ajout\n        print(total)\n').split(), ['1', '2', '3', '5', '9', '17'])
ok('q8 (1 + 1 + 1 + 2 + 4 + 8)', 1**1 + 1**2 + 1**3 + 2**1 + 2**2 + 2**3, 17)
ok('q11 (-1 + 2 - 3 + … + 100)', sum(i if i % 2 == 0 else -i for i in range(1, 101)), 50)
