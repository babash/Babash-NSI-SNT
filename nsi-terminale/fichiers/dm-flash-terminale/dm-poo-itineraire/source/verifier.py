#!/usr/bin/env python3
"""Corrigé vérifié du DM flash « La classe Chemin » (itinéraire, T125).

Usage, à la racine du dépôt : python3 -I nsi-terminale/fichiers/dm-flash-terminale/dm-poo-itineraire/source/verifier.py
Toutes les réponses de la page sont obtenues ici par exécution réelle (Python 3.13),
et les tests des questions « code » refusent des classes volontairement fausses.
"""
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from banc import lancer, questions, verifier_code, egal, fin, PAGE  # noqa: E402

Q = questions()
page = PAGE.read_text(encoding='utf-8')
CLASSE = Q['q4']['corrections'][0]

# q1, q2 : a et b
essai = re.search(r'<pre class="td-code">\n(chemin_1 = .*?)</pre>', page, re.S).group(1)
_, _, s = lancer(CLASSE + '\n' + essai + '\nprint(a, b)')
egal(s.split(), [Q['q1']['reponses'][0], Q['q2']['reponses'][0]], 'q1, q2 : a et b')
# le code d'origine écrivait chemin_1.largueur : il s'arrêtait sur une erreur
_, msg, _ = lancer(CLASSE + '\n' + essai.replace('.largeur', '.largueur'))
print('code d\'origine (largueur) :', msg.strip().splitlines()[-1])

# l'énoncé : la représentation graphique affichée est celle que donne la correction
_, _, s = lancer(CLASSE + '\nc = Chemin("DDBDBBDDDDB")\nc.remplir_grille()\nc.tracer_chemin()')
rep = re.search(r'Sa représentation graphique est :</p>\n  <pre class="td-console">\n(.*?)</pre>', page, re.S).group(1)
egal([html.unescape(x) for x in re.findall(r'<span class="td-l">(.*?)</span>', rep)], s.rstrip('\n').split('\n'), 'énoncé : représentation graphique')
egal(s.rstrip('\n').split('\n')[-1], ' ' * 14 + 'E', 'énoncé : E après 14 espaces')

# q3 : chaque réponse acceptée de chaque case donne la bonne grille
t3 = Q['q3']
code3 = html.unescape(re.search(r'<pre class="td-code">\n(.*?)</pre>', t3['corps'], re.S).group(1))
trous = re.findall(r'\[\[(.*?)\]\]', code3)
for k, t in enumerate(trous):
    for alt in t.split('|'):
        n = iter(range(len(trous)))
        rempli = re.sub(r'\[\[(.*?)\]\]', lambda m: alt if next(n) == k else m.group(1).split('|')[0], code3)
        e, _, s = lancer(rempli)
        egal(s.rstrip(), t3['attendu'], f'q3 case {k + 1} « {alt} »')

verifier_code('q4', [
    ('S et E oubliés', [("texte = texte + case + ' '", "texte = texte + '* '")]),
    ('affiche la liste', [("        for ligne in self.grille:\n            texte = ''", "        for ligne in self.grille:\n            print(ligne)\n            texte = ''"), ('            print(texte.rstrip())', '            pass')]),
    ('grille transposée', [('        for ligne in self.grille:\n', '        for ligne in zip(*self.grille):\n')]),
    ('une seule ligne', [('            print(texte.rstrip())', '        print(texte.rstrip())')]),
    ('renvoie au lieu d afficher', [('            print(texte.rstrip())', '            return texte')]),
    ('case vide sur un seul caractère', [("texte = texte + '  '", "texte = texte + ' '")]),
], Q)
verifier_code('q5', [
    ('ordre inversé', [('return (self.longueur, self.largeur)', 'return (self.largeur, self.longueur)')]),
    ('liste', [('return (self.longueur, self.largeur)', 'return [self.longueur, self.largeur]')]),
    ('affiche', [('return (self.longueur, self.largeur)', 'print(self.longueur, self.largeur)')]),
    ('somme', [('return (self.longueur, self.largeur)', 'return self.longueur + self.largeur')]),
], Q)

# q6 : chaque réponse acceptée donne un itinéraire de la bonne taille, fait de D et de B
t6 = Q['q6']
code6 = html.unescape(re.search(r'<pre class="td-code">\n(.*?)</pre>', t6['corps'], re.S).group(1))
trous = re.findall(r'\[\[(.*?)\]\]', code6)
for k, t in enumerate(trous):
    for alt in t.split('|'):
        n = iter(range(len(trous)))
        rempli = re.sub(r'\[\[(.*?)\]\]', lambda m: alt if next(n) == k else m.group(1).split('|')[0], code6)
        rempli += '\nfor t in (0, 1, 5, 11):\n    x = itineraire_aleatoire(t)\n    assert len(x) == t and set(x) <= {"D", "B"}\nprint("ok")'
        e, d, s = lancer(rempli)
        egal(s.split(), ['10', 'ok'], f'q6 case {k + 1} « {alt} »')

# q7 : 2 ** N, compté pour de vrai
from itertools import product
for N in range(0, 12):
    egal(len(list(product('DB', repeat=N))), 2 ** N, f'q7 : {N} lettres')
fin()
