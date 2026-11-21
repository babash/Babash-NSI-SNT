"""Corrigé du DM flash « Premiers pas en Python » : les réponses calculées par exécution.

Lancer : python3 -I corrige-dm-premiers-pas.py (Python 3.13).
Le programme de l'énoncé est exécuté tel quel, avec les saisies 83 et 1.80.
"""
import subprocess
import sys

IMC = '''poids = float(input("Saisissez votre poids (en kg)"))
taille = float(input("Saisissez votre taille (en m)"))
imc = poids/(taille**2)
print("Votre Indice de Masse Corporelle est de", imc)
'''

r = subprocess.run([sys.executable, '-I', '-c', IMC], input='83\n1.80\n', capture_output=True, text=True)
print('Terminal complet (les invites de input comprises) :')
print(r.stdout)
print('Dernière ligne :', r.stdout.split(')')[-1].strip())
print('type de input("…") :', type('83').__name__, '; float("1.80") =', float('1.80'))
print('2 ** 3 =', 2 ** 3, '; 1.80 ** 2 =', 1.80 ** 2)
