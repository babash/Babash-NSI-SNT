#!/usr/bin/env python3
"""Corrigé vérifié du DM flash « La classe Fraction » (T125).

Usage, à la racine du dépôt : python3 -I nsi-terminale/fichiers/dm-flash-terminale/dm-poo-fraction/source/verifier.py
Toutes les réponses de la page sont obtenues ici par exécution réelle (Python 3.13),
et les tests des questions « code » refusent des classes volontairement fausses.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from banc import lancer, questions, verifier_code, egal, fin, PAGE  # noqa: E402

Q = questions()
page = PAGE.read_text(encoding='utf-8')
affiche = re.search(r'<pre class="td-code">\n(class Fraction:.*?)</pre>', page, re.S).group(1)
affiche = affiche.replace('&lt;', '<').replace('&gt;', '>')
CLASSE = Q['q10']['corrections'][0] + '\n' + '\n'.join(Q['q5']['corrections'][0].split('\n')[6:])

# q4 : le vrai message pour Fraction(3, 0), ajoutée à la fin du fichier affiché
etat, msg, _ = lancer(affiche + '\n\nf3 = Fraction(3, 0)\n', fichier='fraction.py')
egal(msg.rstrip(), Q['q4']['erreurs'][0].rstrip(), 'q4 : message réel de Fraction(3, 0)')

# q5 et q10 : les tests refusent les classes fausses
verifier_code('q5', [
    ('division décimale', [('self.a // self.b', 'self.a / self.b')]),
    ('reste', [('self.a // self.b', 'self.a % self.b')]),
    ('arrondi', [('self.a // self.b', 'round(self.a / self.b)')]),
    ('inversé', [('self.a // self.b', 'self.b // self.a')]),
    ('sans self', [('self.a // self.b', 'a // b')]),
    ('affiche au lieu de renvoyer', [('return self.a // self.b', 'print(self.a // self.b)')]),
], Q)
verifier_code('q10', [
    ('r = self', [('r = Fraction(0, 1)', 'r = self')]),
    ('oubli du return', [('        return r', '        pass')]),
    ('r non créé', [('r = Fraction(0, 1)', 'r = None')]),
    ('numérateurs multipliés', [('(self.a * fraction.b) + (fraction.a * self.b)', 'self.a * fraction.a')]),
    ('produit croisé faux', [('(fraction.a * self.b)', '(fraction.a * fraction.b)')]),
    ('dénominateurs additionnés', [('r.b = self.b * fraction.b', 'r.b = self.b + fraction.b')]),
    ('même dénominateur : b additionnés', [('            r.b = self.b\n', '            r.b = self.b + fraction.b\n')]),
    ('même dénominateur : a non additionnés', [('r.a = self.a + fraction.a', 'r.a = self.a')]),
    ('condition à l envers', [('if self.b != fraction.b:', 'if self.b == fraction.b:')]),
], Q)

# q6 à q9 : chaque réponse acceptée s'exécute et donne le bon objet ou la bonne valeur
for rep in Q['q6']['reponses']:
    _, _, s = lancer(CLASSE + '\n' + rep + '\nprint(f1.a, f1.b)')
    egal(s.strip(), '5 9', f'q6 « {rep} »')
for rep in Q['q7']['reponses']:
    _, _, s = lancer(CLASSE + '\n' + rep + '\nprint(f2.a, f2.b)')
    egal(s.strip(), '9 12', f'q7 « {rep} »')
DEBUT = CLASSE + '\nf1 = Fraction(5, 9)\nf2 = Fraction(9, 12)\n'
for rep in Q['q8']['reponses']:
    code = rep[6:-1] if rep.startswith('print(') else rep
    _, _, s = lancer(DEBUT + 'print(' + code + ')')
    egal(s.strip(), '0', f'q8 « {rep} »')
for rep in Q['q9']['reponses']:
    code = rep[6:-1] if rep.startswith('print(') else rep
    _, _, s = lancer(DEBUT + 'r = ' + code + '\nprint(r.a, r.b)')
    egal(s.strip(), '141 108', f'q9 « {rep} »')
# le retour sur f1 + f2 cite le vrai message
_, msg, _ = lancer(DEBUT + 's = f1 + f2\n')
egal(msg.strip().splitlines()[-1], "TypeError: unsupported operand type(s) for +: 'Fraction' and 'Fraction'", 'q9 : message de f1 + f2')
egal('TypeError: unsupported operand type(s) for +: &#39;Fraction&#39; and &#39;Fraction&#39;' in page or "TypeError: unsupported operand type(s) for +: 'Fraction' and 'Fraction'" in page, True, 'q9 : message cité dans la page')
# la correction de q8 dit « elle renvoie 0 », celle de q10 « 141/108, égale à 47/36 »
from fractions import Fraction as F
egal(F(141, 108), F(47, 36), 'q10 : 141/108 = 47/36')
fin()
