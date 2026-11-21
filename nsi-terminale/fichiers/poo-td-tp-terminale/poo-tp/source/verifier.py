#!/usr/bin/env python3
"""TP de POO (les cartes) : les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py [--attendu]   (Python 3.13)
- lance les tests cachés de chaque question « code » (lus dans la page) sur la correction
  (acceptée) et sur des versions fausses (refusées) ;
- calcule les réponses des questions 3 et 9, et la sortie de la question 12 ;
- --attendu : écrit seulement la sortie de la question 12 (52 lignes), à copier dans pre.td-attendu.
"""
import contextlib
import html
import io
import os
import re
import sys

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
TEXTE = open(PAGE, encoding='utf-8').read() if os.path.exists(PAGE) else ''

CARTE = '''
class Carte:
    def __init__(self, valeur, couleur, enseigne):
        self.valeur = valeur
        self.couleur = couleur
        self.enseigne = enseigne
'''
METHODES = CARTE + '''
    def egalite(self, autre):
        return self.valeur == autre.valeur

    def estSuperieurA(self, autre):
        return self.valeur > autre.valeur

    def estInferieurA(self, autre):
        return self.valeur < autre.valeur
'''
JEU = '''
class JeuCartes:
    def __init__(self):
        self.cartes = []    # la liste des cartes du jeu
        for enseigne in ['carreau', 'coeur', 'trèfle', 'pique']:
            if enseigne == 'carreau' or enseigne == 'coeur':
                couleur = 'rouge'
            else:
                couleur = 'noir'
            for valeur in range(2, 15):
                self.cartes.append(Carte(valeur, couleur, enseigne))
'''
JEU_COMPLET = JEU + '''
    def melanger(self):
        random.shuffle(self.cartes)

    def distribuerCarte(self):
        return self.cartes.pop(0)
'''
Q12 = 'import random\nrandom.seed(2046)\n' + CARTE + JEU_COMPLET + '''
jeu = JeuCartes()
jeu.melanger()
while len(jeu.cartes) > 0:
    carte = jeu.distribuerCarte()
    print(carte.valeur, carte.enseigne, carte.couleur)
'''


def sortie(code):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        exec(code, {'__name__': '__main__'})
    return f.getvalue()


if '--attendu' in sys.argv:
    sys.stdout.write(sortie(Q12).rstrip('\n'))
    sys.exit()

# question 3 : le vrai affichage de type(c1)
print('Q3', sortie(CARTE + "c1 = Carte(7, 'rouge', 'coeur')\nprint(type(c1))").strip())
print('Q4', sortie(CARTE + "c1 = Carte(7, 'rouge', 'coeur')\nprint(c1.valeur, c1.couleur, c1.enseigne)").strip())
print('Q6', sortie(CARTE + "c2 = Carte(4, 'rouge', 'coeur')\nc2.enseigne = 'pique'\nc2.couleur = 'noir'\nc2.valeur = 8\n"
                   "print(c2.valeur, c2.couleur, c2.enseigne)").strip())
# question 9
g = {}
exec(METHODES + "a = Carte(5, 'rouge', 'carreau')\nb = Carte(12, 'noir', 'trèfle')\nc = Carte(9, 'noir', 'pique')", g)
for appel in ('b.estSuperieurA(c)', 'a.estSuperieurA(c)', 'a.estInferieurA(b)', 'c.egalite(b)'):
    print('Q9', appel, '->', eval(appel, g))
# question 12 : la sortie de la page est la sortie réelle
s12 = sortie(Q12)
print('Q12', len(s12.splitlines()), 'lignes ; premières :', s12.splitlines()[:3])
m = re.search(r'id="q12".*?<pre class="td-attendu">\n(.*?)</pre>', TEXTE, re.S)
assert m and m.group(1).strip() == s12.strip(), 'Q12 : la sortie attendue de la page n\'est pas la sortie réelle'
print('Q12 : la sortie attendue de la page est la sortie réelle')

TESTS = {}
for bloc in TEXTE.split('<section class="td-q"')[1:]:
    bloc = bloc.split('</section>')[0]
    m = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', bloc, re.S)
    if m:
        TESTS[re.search(r'id="(q\d+)"', bloc).group(1)] = html.unescape(m.group(1))
JUSTES = {'q1': CARTE, 'q8': METHODES, 'q10': CARTE + JEU, 'q11': 'import random\n' + CARTE + JEU_COMPLET}
FAUSSES = {
    'q1': {'attributs mal nommés': CARTE.replace('self.couleur', 'self.coul'),
           'attributs de classe partagés': 'class Carte:\n    valeur = 7\n    couleur = "rouge"\n    enseigne = "coeur"\n'
                                           '    def __init__(self, v, c, e):\n        pass\n',
           'ordre des paramètres': CARTE.replace('valeur, couleur, enseigne)', 'valeur, enseigne, couleur)')},
    'q8': {'égalité sur la couleur': METHODES.replace('self.valeur == autre.valeur', 'self.couleur == autre.couleur'),
           'supérieur ou égal': METHODES.replace('self.valeur > autre.valeur', 'self.valeur >= autre.valeur'),
           'inférieur inversé': METHODES.replace('self.valeur < autre.valeur', 'self.valeur > autre.valeur'),
           'affiche au lieu de renvoyer': METHODES.replace('return self.valeur == autre.valeur', 'print(self.valeur == autre.valeur)')},
    'q10': {'valeurs 1 à 13': CARTE + JEU.replace('range(2, 15)', 'range(1, 14)'),
            'valeurs 2 à 13': CARTE + JEU.replace('range(2, 15)', 'range(2, 14)'),
            'couleurs inversées': CARTE + JEU.replace("couleur = 'rouge'", "couleur = 'x'").replace("couleur = 'noir'", "couleur = 'rouge'").replace("couleur = 'x'", "couleur = 'noir'"),
            'liste de classe partagée': CARTE + JEU.replace("    def __init__(self):\n        self.cartes = []    # la liste des cartes du jeu\n",
                                                              "    cartes = []\n    def __init__(self):\n")},
    'q11': {'mélange oublié': 'import random\n' + CARTE + JEU_COMPLET.replace('random.shuffle(self.cartes)', 'pass'),
            'renvoie la dernière': 'import random\n' + CARTE + JEU_COMPLET.replace('pop(0)', 'pop()'),
            'ne retire pas la carte': 'import random\n' + CARTE + JEU_COMPLET.replace('return self.cartes.pop(0)', 'return self.cartes[0]'),
            'renvoie le mélange': 'import random\n' + CARTE + JEU_COMPLET.replace('random.shuffle(self.cartes)', 'self.cartes = random.shuffle(self.cartes)')},
}


def essayer(code, tests):
    g = {'__name__': '__main__'}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, g)
            exec(tests, g)
        return 'passe'
    except AssertionError as e:
        return 'refusée : ' + str(e)
    except Exception as e:
        return 'erreur : %r' % e


for q, juste in JUSTES.items():
    r = essayer(juste, TESTS[q])
    print(q, 'correction :', r)
    assert r == 'passe', q
    for nom, code in FAUSSES[q].items():
        r = essayer(code, TESTS[q])
        print(q, 'version fausse (%s) :' % nom, r)
        assert r != 'passe', (q, nom)
print('tout est juste')
