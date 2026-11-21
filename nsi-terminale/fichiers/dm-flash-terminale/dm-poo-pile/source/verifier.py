#!/usr/bin/env python3
"""Corrigé vérifié du DM flash « La classe Pile » (T125).

Usage, à la racine du dépôt : python3 -I nsi-terminale/fichiers/dm-flash-terminale/dm-poo-pile/source/verifier.py
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
affiche = re.search(r'<pre class="td-code">\n(class Pile:.*?)</pre>', page, re.S).group(1)
CLASSE = Q['q8']['corrections'][0]

# q3 : le constructeur est aux lignes 5 et 6 du code affiché
L = affiche.split('\n')
egal((L[4].strip(), L[5].strip()), ('def __init__(self, tab):', 'self.pile = tab'), 'q3 : lignes 5 et 6')
egal(max(len(l) for l in L) <= 80, True, 'code affiché : 80 caractères au plus par ligne')

# q4, q5 : chaque réponse acceptée crée la bonne pile
for rep in Q['q4']['reponses']:
    _, _, s = lancer(CLASSE + '\n' + rep + '\nprint(p1.est_vide(), p1.pile)')
    egal(s.strip(), 'True []', f'q4 « {rep} »')
_, msg, _ = lancer(CLASSE + '\np1 = Pile()\n')
egal(msg.strip().splitlines()[-1], "TypeError: Pile.__init__() missing 1 required positional argument: 'tab'", 'q4 : message de Pile()')
for rep in Q['q5']['reponses']:
    _, _, s = lancer(CLASSE + '\n' + rep + '\nprint(p2.tete(), p2.pile)')
    egal(s.strip(), '3 [5, 8, 6, 5, 3]', f'q5 « {rep} »')

# q6 : la valeur, par exécution
_, _, s = lancer(CLASSE + '\np2 = Pile([5, 8, 6, 5, 3])\nprint(p2.depiler() + p2.depiler() + p2.tete())')
egal(s.strip(), Q['q6']['reponses'][0], 'q6 : p2.depiler() + p2.depiler() + p2.tete()')

verifier_code('q7', [
    ('insert(0, x)', [('self.pile.append(x)', 'self.pile.insert(0, x)')]),
    ('remplace la liste', [('self.pile.append(x)', 'self.pile = [x]')]),
    ('sans effet', [('self.pile.append(x)', 'self.pile + [x]')]),
    ('ajout en tête par concaténation', [('self.pile.append(x)', 'self.pile = [x] + self.pile')]),
    ('sans self', [('self.pile.append(x)', 'pile.append(x)')]),
], Q)
verifier_code('q8', [
    ('renvoie sans enlever', [('return self.pile.pop()', 'return self.pile[-1]')]),
    ('pop(0)', [('return self.pile.pop()', 'return self.pile.pop(0)')]),
    ('enlève sans renvoyer', [('return self.pile.pop()', 'self.pile.pop()')]),
    ('enlève tout', [('return self.pile.pop()', 'x = self.pile[-1]\n        self.pile = []\n        return x')]),
], Q)
verifier_code('q9', [
    ('est_vide sans parenthèses', [('vide = p.est_vide()', 'vide = p.est_vide')]),
    ('tête sans parenthèses', [('p.empiler(p.tete())', 'p.empiler(p.tete)')]),
    ('dépile sans ranger', [('x = p.depiler()', 'p.depiler()\nx = None')]),
    ('pas de copie de la tête', [('p.empiler(p.tete())', '')]),
    ('pile = liste', [('p = Pile([])', 'p = []')]),
    ('test à l envers', [('vide = p.est_vide()', 'vide = not p.est_vide()')]),
], Q)
fin()
