#!/usr/bin/env python3
"""DM flash « trouver le maximum » : les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Affiche les réponses ; essaie les tests
de la question 7 (lus dans la page) sur la correction et sur des versions fausses.
"""
import html
import os
import re


def recherche_max(tab):
    vmax, imax = 0, None
    for i in range(len(tab)-1):
        if tab[i] > vmax:
            vmax = tab[i]
            imax = i
    return vmax, imax


tab = [9, 100, 8, 48, 73]
vmax, imax = 0, None
print('Q4 tour 0 :', (None, None, None, vmax, imax))
for tour, i in enumerate(range(len(tab) - 1), 1):
    c = tab[i] > vmax
    if c:
        vmax, imax = tab[i], i
    print(f'Q4 tour {tour} :', (i, tab[i], c, vmax, imax))
print('Q4 renvoie :', recherche_max(tab), '| range :', list(range(len(tab) - 1)))
for t in ([10, 4, 8, 88, 10], [-10, -2, -10], [1, 2, 3]):
    print('Q5/Q6', t, '->', recherche_max(t), '| vrai maximum :', max(t), 'à l\'indice', t.index(max(t)))

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
TESTS = html.unescape(re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>',
                                open(PAGE, encoding='utf-8').read(), re.S).group(1))
CORRECTION = '''
def recherche_max(tab):
    vmax, imax = tab[0], 0
    for i in range(len(tab)):
        if tab[i] > vmax:
            vmax = tab[i]
            imax = i
    return vmax, imax
'''
AUTRE = '''
def recherche_max(tab):
    vmax, imax = tab[0], 0
    for i in range(1, len(tab)):
        if tab[i] > vmax:
            vmax = tab[i]
            imax = i
    return vmax, imax
'''
FAUSSES = {
    'la fonction de départ': CORRECTION.replace('tab[0], 0', '0, None').replace('range(len(tab))', 'range(len(tab)-1)'),
    'seulement le range corrigé': CORRECTION.replace('tab[0], 0', '0, None'),
    'seulement le départ corrigé': CORRECTION.replace('range(len(tab))', 'range(len(tab)-1)'),
    'vmax = tab[0] mais imax = None': CORRECTION.replace('tab[0], 0', 'tab[0], None'),
    'return dans la boucle': '''
def recherche_max(tab):
    vmax, imax = tab[0], 0
    for i in range(len(tab)):
        if tab[i] > vmax:
            vmax = tab[i]
            imax = i
        return vmax, imax
''',
    'renvoie l\'indice du dernier élément vu': CORRECTION.replace('            imax = i\n', '').replace('return vmax, imax', 'return vmax, i'),
}


def essayer(code):
    g = {}
    exec(code, g)
    exec(TESTS, g)


essayer(CORRECTION)
essayer(AUTRE)
print('Q7 : les deux corrections passent les tests')
for nom, code in FAUSSES.items():
    try:
        essayer(code)
    except AssertionError as e:
        print('Q7 version fausse rejetée :', nom, '->', e)
    else:
        raise SystemExit('ERREUR : une version fausse passe les tests : ' + nom)
print('tout est juste')
