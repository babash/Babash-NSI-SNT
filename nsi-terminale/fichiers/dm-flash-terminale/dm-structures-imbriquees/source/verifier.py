#!/usr/bin/env python3
"""DM flash « structures imbriquées » : les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Affiche les réponses des questions 1 à 7,
puis lance les tests de la question 8 (lus dans la page) sur la correction et sur des
versions fausses (chacune doit être refusée).
"""
import html
import os
import re

# traduction, height : taille, weight : poids, hp : points de vie, speed : vitesse
pokemons = [{'name' : 'pikachu', 'height' : 4, "weight" : 60,
             'types' : ('electric',),
             'stats' : {'hp': 35, 'attack': 55, 'defense': 40,
                        'special-attack': 50,  'special-defense': 50,
                        'speed': 90}},
            {'name': 'dracolosse', 'height': 22, 'weight': 2100,
             'types': ('dragon', 'flying'),
             'stats': {'hp': 91, 'attack': 134, 'defense': 95,
                       'special-attack': 100, 'special-defense': 100,
                       'speed': 80}},
            {'name': 'ronflex', 'height': 21, 'weight': 4600,
             'types': ('normal',),
             'stats': {'hp': 160, 'attack': 110, 'defense': 65,
                       'special-attack': 65, 'special-defense': 110,
                       'speed': 30}}]

print('Q1', type(pokemons).__name__)
print('Q2', type(pokemons[0]).__name__)
print('Q3', type(pokemons[1]["types"]).__name__, pokemons[1]["types"])
print('Q4', type(pokemons[1]["stats"]).__name__)
print('Q5', pokemons[0]['stats']['special-attack'])
print('Q6', pokemons[1]['types'][1], pokemons[1]['types'][-1])
try:
    pokemons[1]['types'][1] = 'fire'
except TypeError as e:
    print('Q6 (un tuple ne se modifie pas) :', e)
pokemons[2]['stats']['attack'] = 1000
print('Q7', pokemons[2]['stats'])
pokemons[2]['stats']['attack'] = 110

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
TESTS = html.unescape(re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>',
                                open(PAGE, encoding='utf-8').read(), re.S).group(1))
CORRECTION = '''
def plus_lourd(pokemons):
    # initialisation
    meilleur = ""
    meilleur_poids = 0
    for pk in pokemons:
        if pk["weight"] > meilleur_poids:
            meilleur = pk["name"]
            meilleur_poids = pk["weight"]
    return meilleur
'''
FAUSSES = {
    'renvoie le poids': CORRECTION.replace('return meilleur', 'return meilleur_poids'),
    'garde le plus léger': CORRECTION.replace('> meilleur_poids', '< meilleur_poids or meilleur_poids == 0'),
    'oublie de mettre à jour le poids': CORRECTION.replace('            meilleur_poids = pk["weight"]\n', ''),
    'renvoie dans la boucle': CORRECTION.replace('    return meilleur', '        return meilleur'),
}


def essayer(code):
    g = {}
    try:
        exec(code, g)
        exec(TESTS, g)
        return 'passe'
    except AssertionError as e:
        return 'refusée : ' + str(e)
    except Exception as e:
        return 'erreur : %r' % e


g = {}
exec(CORRECTION, g)
print('Q8 plus_lourd(pokemons) =', repr(g['plus_lourd'](pokemons)))
print('Q8 correction :', essayer(CORRECTION))
assert essayer(CORRECTION) == 'passe'
for nom, code in FAUSSES.items():
    r = essayer(code)
    print('Q8 version fausse (%s) :' % nom, r)
    assert r != 'passe', nom
print('tout est juste')
