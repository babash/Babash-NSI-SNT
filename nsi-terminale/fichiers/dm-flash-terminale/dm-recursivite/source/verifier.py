#!/usr/bin/env python3
"""DM « la récursivité en famille » : les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13). Affiche les réponses ; essaie le code à
compléter (question 5) avec chaque réponse acceptée, et des versions fausses, sur des tests.
"""
import itertools

famille = {
    'nom': 'Grand-Père',
    'oreilles': 2,
    'enfants': [
        {
            'nom': 'Père',
            'oreilles': 2,
            'enfants': [
                {'nom': 'Moi', 'oreilles': 2, 'enfants': []},
                {'nom': 'Ma Sœur', 'oreilles': 2, 'enfants': []}
            ]
        },
        {
            'nom': 'Tante',
            'oreilles': 2,
            'enfants': [
                {'nom': 'Cousin', 'oreilles': 2, 'enfants': []}
            ]
        }
    ]
}
print('Q1', type(famille).__name__, '| Q2', type(famille['enfants']).__name__)
for rep in ("famille['enfants'][0]['nom']", 'famille["enfants"][0]["nom"]'):
    print('Q3', rep, '->', eval(rep))
for rep in ("famille['enfants'][1]['enfants'][0]['oreilles']",):
    print('Q4', rep, '->', eval(rep), '| nom :', famille['enfants'][1]['enfants'][0]['nom'])

TROU = '''
def calculer_oreilles_famille(personne):
    if personne['enfants'] == []:
        return {a}
    total = personne['oreilles']
    for enfant in personne['enfants']:
        total += calculer_oreilles_famille(enfant)
    return {b}
'''
A = ["personne['oreilles']", 'personne["oreilles"]']
B = ['total']
appels = []


def tests(f):
    # des familles où les oreilles ne valent pas toutes 2, pour démasquer « return 2 »
    seul = {'nom': 'S', 'oreilles': 3, 'enfants': []}
    assert f(seul) == 3, f'une personne seule à 3 oreilles : {f(seul)}'
    petit = {'nom': 'A', 'oreilles': 2, 'enfants': [{'nom': 'B', 'oreilles': 1, 'enfants': []},
                                                    {'nom': 'C', 'oreilles': 4, 'enfants': []}]}
    assert f(petit) == 7, f'A, B, C (2 + 1 + 4) : {f(petit)}'
    assert f(famille) == 12, f'la famille : {f(famille)}'


def charger(src):
    g = {}
    exec(src, g)
    return g['calculer_oreilles_famille']


for a, b in itertools.product(A, B):
    tests(charger(TROU.format(a=a, b=b)))
print('Q5 : réponses acceptées, tests passés')
FAUSSES = {
    'return 2 (vrai seulement si chacun a 2 oreilles)': dict(a='2', b='total'),
    'return 0 au cas de base': dict(a='0', b='total'),
    "return personne['oreilles'] à la fin (oublie les descendants)": dict(a=A[0], b=A[0]),
    'return total au cas de base (variable pas encore définie)': dict(a='total', b='total'),
}
for nom, t in FAUSSES.items():
    try:
        tests(charger(TROU.format(**t)))
    except (AssertionError, NameError, UnboundLocalError) as e:
        print('Q5 version fausse rejetée :', nom, '->', type(e).__name__, e)
    else:
        raise SystemExit('ERREUR : une version fausse passe les tests : ' + nom)

# Questions 8 et 9 : nombre d'appels et résultat, comptés pour de vrai
f = charger(TROU.format(a=A[0], b='total'))
n = 0


def compter(personne):
    global n
    n += 1
    print('  appel sur', personne['nom'])
    if personne['enfants'] == []:
        return personne['oreilles']
    total = personne['oreilles']
    for enfant in personne['enfants']:
        total += compter(enfant)
    return total


petit_arbre = {'nom': 'A', 'oreilles': 2,
               'enfants': [{'nom': 'B', 'oreilles': 2, 'enfants': []},
                           {'nom': 'C', 'oreilles': 2, 'enfants': []}]}
r = compter(petit_arbre)
print('Q8 appels :', n, '| Q9 résultat :', r, '| contrôle :', f(petit_arbre))
n = 0
print('famille entière :', compter(famille), 'en', n, 'appels')
print('tout est juste')
