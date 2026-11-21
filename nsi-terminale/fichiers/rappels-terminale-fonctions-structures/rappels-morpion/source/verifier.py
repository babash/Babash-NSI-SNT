#!/usr/bin/env python3
"""Rappel de 1re NSI, le morpion (feuilles 1 et 2) : les réponses, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13)
Calcule chaque réponse des deux feuilles, puis lance les tests cachés des questions « code »
(lus dans les pages) sur les corrections (acceptées) et sur des versions fausses (refusées).
"""
import contextlib
import html
import io
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
PAGES = [os.path.join(ICI, '..', 'index.html'), os.path.join(ICI, '..', 'feuille-2.html')]


def sortie(code, g=None):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        exec(code, {} if g is None else g)
    return f.getvalue()


AFFICHER = '''
def afficherGrille(g, gagnant=None):
    print(" " + g[0][0] + " | " + g[0][1] + " | " + g[0][2] + " ")
    print("---+---+---")
    print(" " + g[1][0] + " | " + g[1][1] + " | " + g[1][2] + " ")
    print("---+---+---")
    print(" " + g[2][0] + " | " + g[2][1] + " | " + g[2][2] + " \\n")

    if gagnant:
        print("* Partie terminée : le joueur", gagnant, "a gagné. *")


grille = [[" " for _ in range(3)] for _ in range(3)]
'''
print('F1 type(grille) :', sortie(AFFICHER + 'print(type(grille), grille)').strip())
print('F1 afficherGrille(grille, gagnant="X") :')
print(sortie(AFFICHER + 'afficherGrille(grille, gagnant="X")'))
joueurs = ("X", "O")
print('F1 type(joueurs) :', type(joueurs).__name__, '; joueurs[1] =', joueurs[1])
try:
    joueurs[1] = "Z"
except TypeError as e:
    print('F1 modifier un tuple :', e)

# tourJoueur, avec une saisie fixée
TOUR = '''
def tourJoueur(joueur, grille):
    tour = int(input("Sur quelle case veux-tu jouer ? (0 à 8) "))
    grille[tour // 3][tour % 3] = joueur
'''
g = {'input': lambda invite='': '5'}
exec(AFFICHER + TOUR + 'tourJoueur("X", grille)', g)
print('F1 tourJoueur("X", grille) avec la case 5 :', g['grille'])

GAGNANTES = '''
def ligneGagnante(grille, ligne):
    if grille[ligne][0] == grille[ligne][1] == grille[ligne][2]:
        return grille[ligne][0]
    else : return False

def colonneGagnante(grille, colonne):
    if grille[0][colonne] == grille[1][colonne] == grille[2][colonne]:
        return grille[0][colonne]
    else : return False

def diagonalGagnante(grille):
    if grille[0][0] == grille[1][1] == grille[2][2] :
        return grille[0][0]
    elif grille[2][0] == grille[1][1] == grille[0][2]:
        return grille[2][0]
    else : return False
'''
g = {}
exec(GAGNANTES, g)
essais = {
    'ligne de X': [["X", "X", "X"], [" ", "O", " "], ["O", " ", " "]],
    'ligne vide': [[" ", " ", " "], ["X", "O", "X"], ["O", "X", "O"]],
    'rien': [["X", "O", "X"], ["X", "O", "O"], ["O", "X", "X"]],
    'colonne de O': [["O", "X", " "], ["O", "X", " "], ["O", " ", "X"]],
    'diagonale montante de X': [["O", "O", "X"], [" ", "X", " "], ["X", " ", " "]],
}
for nom, gr in essais.items():
    print('F1', nom, ': ligne 0 ->', repr(g['ligneGagnante'](gr, 0)), '; colonne 0 ->', repr(g['colonneGagnante'](gr, 0)),
          '; diagonales ->', repr(g['diagonalGagnante'](gr)))

GRILLE = '''
grille = [["", "", ""],
          ["", "", ""],
          ["", "", ""]]
grille[0][1] = "X"
grille[1][-1] = "O"
grille[2][0] = grille[0][1]
grille[len(grille[0]) - 1][2] = "O"
'''
g = {}
exec(GRILLE, g)
print('F1 grille dessinée :')
for ligne in g['grille']:
    print('    ', ' | '.join(c or '.' for c in ligne))
print('F1 len(grille[0]) - 1 =', len(g['grille'][0]) - 1)

DICO = '''
joueurs = {"Lagon": (4, 15),
           "Corail": (6, 15),
           "Manta": (11, 20),
           "Tortue": (19, 30)}

def meilleurRatio(joueurs):
    meilleur = None
    rmax = 0
    for n, (v, j) in joueurs.items():
        if v/j > rmax:
            rmax = v/j
            meilleur = n
    return meilleur
'''
g = {}
exec(DICO, g)
jo = g['joueurs']
print('F1 clés :', list(jo), '; type des valeurs :', {type(v).__name__ for v in jo.values()})
print('F1 joueurs["Tortue"][0] =', jo["Tortue"][0])
print('F1 somme des parties jouées =', jo["Lagon"][1] + jo["Corail"][1] + jo["Manta"][1] + jo["Tortue"][1])
print('F1 ratios :', {n: round(v / j, 3) for n, (v, j) in jo.items()}, '-> meilleurRatio =', g['meilleurRatio'](jo))
print('F1 égalité :', g['meilleurRatio']({"A": (1, 2), "B": (2, 4)}), '(le premier rencontré)')

JO = '''
JO_2024 = [["pays", "or", "argent", "bronze"],
           ["Italie", 12, 13, 15],
           ["Japon", 20, 12, 13],
           ["États-Unis", 40, 44, 42],
           ["Pays-Bas", 15, 7, 12],
           ["France", 16, 26, 22],
           ["Chine", 40, 27, 24],
           ["Corée du Sud", 13, 9, 10],
           ["Allemagne", 12, 13, 8],
           ["Australie", 18, 19, 16],
           ["Grande-Bretagne", 14, 22, 29]]
'''
g = {}
exec(JO, g)
J = g['JO_2024']
print('F2 premier pays :', J[1][0], '; dernier :', J[-1][0], '; nombre de pays :', len(J) - 1, '(len =', len(J), ')')
print('F2 or :', sorted(((l[1], l[0]) for l in J[1:]), reverse=True)[:3])
print('F2 total :', sorted(((sum(l[1:]), l[0]) for l in J[1:]), reverse=True)[:3])

CORRECTIONS = {
    'gagnant': JO + '''
def gagnant(tableau):
    meilleur = tableau[1]
    for ligne in tableau[2:]:
        if ligne[1] > meilleur[1]:
            meilleur = ligne
    return meilleur[0], meilleur[1]
''',
    'plus_medailles': JO + '''
def plus_medailles(tableau):
    meilleur, total_max = None, -1
    for ligne in tableau[1:]:
        total = ligne[1] + ligne[2] + ligne[3]
        if total > total_max:
            meilleur, total_max = ligne[0], total
    return meilleur, total_max
''',
    'mise_a_jour': DICO + '''
v, j = joueurs["Tortue"]
joueurs["Tortue"] = (v + 1, j + 1)
v, j = joueurs["Lagon"]
joueurs["Lagon"] = (v, j + 1)
''',
}
FAUSSES = {
    'gagnant': {'ligne d\'en-tête comprise': CORRECTIONS['gagnant'].replace("tableau[2:]", "tableau[0:]").replace("meilleur = tableau[1]", "meilleur = tableau[0]"),
                'argent au lieu de l\'or': CORRECTIONS['gagnant'].replace('ligne[1] > meilleur[1]', 'ligne[2] > meilleur[2]'),
                'renvoie la ligne': CORRECTIONS['gagnant'].replace('return meilleur[0], meilleur[1]', 'return meilleur')},
    'plus_medailles': {'or seulement': CORRECTIONS['plus_medailles'].replace('ligne[1] + ligne[2] + ligne[3]', 'ligne[1]'),
                       'oublie le bronze': CORRECTIONS['plus_medailles'].replace(' + ligne[3]', '')},
    'mise_a_jour': {'Lagon gagne aussi': CORRECTIONS['mise_a_jour'].replace('(v, j + 1)', '(v + 1, j + 1)'),
                    'oublie les parties jouées': CORRECTIONS['mise_a_jour'].replace('(v + 1, j + 1)', '(v + 1, j)')},
}
print('F2 gagnant :', sortie(CORRECTIONS['gagnant'] + 'print(gagnant(JO_2024))').strip())
print('F2 plus_medailles :', sortie(CORRECTIONS['plus_medailles'] + 'print(plus_medailles(JO_2024))').strip())

# les tests des pages, par fichier de la question (data-fichier)
TESTS = {}
for page in PAGES:
    if not os.path.exists(page):
        continue
    for bloc in open(page, encoding='utf-8').read().split('<section class="td-q')[1:]:
        bloc = bloc.split('</section>')[0]
        m = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', bloc, re.S)
        f = re.search(r'data-fichier="([^"]+)\.py"', bloc)
        if m and f:
            TESTS[f.group(1)] = html.unescape(m.group(1))
print('tests lus :', sorted(TESTS))


def essayer(code, tests):
    g = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, g)
            exec(tests, g)
        return 'passe'
    except AssertionError as e:
        return 'refusée : ' + str(e)
    except Exception as e:
        return 'erreur : %r' % e


for nom, code in CORRECTIONS.items():
    if nom not in TESTS:
        print(nom, ': pas de tests dans les pages')
        continue
    r = essayer(code, TESTS[nom])
    print(nom, 'correction :', r)
    assert r == 'passe', nom
    for f, faux in FAUSSES[nom].items():
        r = essayer(faux, TESTS[nom])
        print(nom, 'version fausse (%s) :' % f, r)
        assert r != 'passe', (nom, f)
for nom in set(TESTS) - set(CORRECTIONS):
    print(nom, ': tests sans correction ici (vérifiée par la page, data-verifier="correction")')
print('tout est juste')
