#!/usr/bin/env python3
"""DM flash « recherche linéaire dans un dictionnaire » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Affiche les réponses, puis essaie les tests
de la question bonus sur la correction (elle doit passer) et sur des versions fausses
(elles doivent échouer).
"""


def recherche(d, x):
    for k, v in d.items():
        if k == x:
            return v
    return -1


# Question 2 : le tableau d'avancement
d, x = {9: 2, 7: 1, 11: 11, 6: 7, 0: 2}, 6
for tour, (k, v) in enumerate(d.items(), 1):
    print(f'Q2 tour {tour} :', (k, v, k == x))
    if k == x:
        break
print('Q2 renvoie :', recherche(d, x))

# Question 3 : les valeurs renvoyées
for args in (({9: 2, 7: 1, 11: 11}, 7), ({}, 3), ({3: 1, 1: 0}, 5), ({5: 6, 7: 1, 11: -1}, 11)):
    print('Q3', args, '->', recherche(*args))
print('Q5 False == 0 :', False == 0)

# les tests de la page (script.td-tests), lus dans la page elle-même
import html, os, re
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
TESTS = html.unescape(re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>',
                                open(PAGE, encoding='utf-8').read(), re.S).group(1))
CORRECTION = '''
def recherche(d, x):
    for k, v in d.items():
        if k == x:
            return v
    return None
'''
FAUSSES = {
    'garde -1': CORRECTION.replace('return None', 'return -1'),
    'renvoie 0': CORRECTION.replace('return None', 'return 0'),
    'renvoie False': CORRECTION.replace('return None', 'return False'),
    'return None dans la boucle (s\'arrête à la première clé)': '''
def recherche(d, x):
    for k, v in d.items():
        if k == x:
            return v
        else:
            return None
''',
}


def essayer(code):
    g = {}
    exec(code, g)
    exec(TESTS, g)


essayer(CORRECTION)
print('Q6 : la correction passe les tests')
for nom, code in FAUSSES.items():
    try:
        essayer(code)
    except AssertionError as e:
        print('Q6 version fausse rejetée :', nom, '->', e)
    else:
        raise SystemExit('ERREUR : une version fausse passe les tests : ' + nom)
print('tout est juste')
