"""Corrigé du DM flash « Boucles imbriquées » : les réponses calculées par exécution.

Lancer : python3 -I corrige-dm-boucles-imbriquees.py (Python 3.13).
1. Le programme de l'énoncé, exécuté tel quel avec les saisies 2, 5, 12, 120 et -1.
2. La trace pour x = 2 (numéros de ligne de l'énoncé), obtenue avec sys.settrace.
3. La factorielle de la correction, comparée à math.factorial.
"""
import math
import subprocess
import sys

PROG = '''x = int(input("Saisissez un nombre entier :"))
acc = 0
for i in range(x):
    for j in range(i):
        acc = (i-j)**2
print(f"Le total vaut {acc}")
'''

for saisie in ('2', '5', '12', '120', '-1'):
    r = subprocess.run([sys.executable, '-I', '-c', PROG], input=saisie + '\n', capture_output=True, text=True)
    print(f'x = {saisie:>4} :', r.stdout.replace('Saisissez un nombre entier :', '').strip())

# trace pour x = 2 : les lignes exécutées et les variables après chacune
print('\nTrace pour x = 2 (ligne exécutée, puis x, i, j, acc juste après) :')
code = compile(PROG.replace('int(input("Saisissez un nombre entier :"))', '2'), 'dm.py', 'exec')
etapes, precedente = [], [None]


def tracer(cadre, evenement, arg):
    if cadre.f_code.co_filename != 'dm.py':
        return tracer
    if evenement in ('line', 'return') and precedente[0] is not None:
        v = cadre.f_locals
        etapes.append((precedente[0], v.get('x'), v.get('i'), v.get('j'), v.get('acc')))
    if evenement == 'line':
        precedente[0] = cadre.f_lineno
    return tracer


sys.settrace(tracer)
exec(code, {})
sys.settrace(None)
for e in etapes:
    print('ligne %s : x=%s i=%s j=%s acc=%s' % e)

CORRECTION = '''x = 5
fact = 1
for k in range(1, x + 1):
    fact = fact * k
print(fact)
'''
r = subprocess.run([sys.executable, '-I', '-c', CORRECTION], capture_output=True, text=True)
print('\nfactorielle de 5 :', r.stdout.strip(), '(math.factorial :', math.factorial(5), ')')
