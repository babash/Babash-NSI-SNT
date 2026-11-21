#!/usr/bin/env python3
"""TD « parcours d'arbres binaires » : les réponses de la page, par exécution.

Usage : python3 -I verifier.py   (Python 3.13).
"""


class ArbreBinaire:
    def __init__(self, valeur, gauche=None, droit=None):
        self.valeur = valeur
        self.gauche = gauche
        self.droit = droit

    def parcours_infixe(self):
        if self.gauche is not None:
            self.gauche.parcours_infixe()
        print(self.valeur, end='-')
        if self.droit is not None:
            self.droit.parcours_infixe()

    def parcours_suffixe(self):
        if self.gauche is not None:
            self.gauche.parcours_suffixe()
        if self.droit is not None:
            self.droit.parcours_suffixe()
        print(self.valeur, end='-')

    def mystere(self):
        if self.gauche is None and self.droit is None:
            return 0
        elif self.gauche is None and self.droit is not None:
            return 1 + self.droit.mystere()
        elif self.gauche is not None and self.droit is None:
            return 1 + self.gauche.mystere()
        else:
            return 1 + max(self.droit.mystere(), self.gauche.mystere())

    def taille(self):
        t = 1
        if self.gauche is not None:
            t = t + self.gauche.taille()
        if self.droit is not None:
            t = t + self.droit.taille()
        return t

    def somme(self):
        s = self.valeur
        if self.gauche is not None:
            s = s + self.gauche.somme()
        if self.droit is not None:
            s = s + self.droit.somme()
        return s


B = ArbreBinaire("B")
C = ArbreBinaire("C")
D = ArbreBinaire("D", B, None)
K = ArbreBinaire("K", None, C)
Z = ArbreBinaire("Z")
E = ArbreBinaire("E", K, Z)
I = ArbreBinaire("I", D, E)
print('Q2 I.droit.gauche.valeur =', I.droit.gauche.valeur)
print('Q3 I.gauche.gauche.valeur =', I.gauche.gauche.valeur)
print('Q5 infixe : ', end=''); I.parcours_infixe(); print()
print('Q6 suffixe : ', end=''); I.parcours_suffixe(); print()

A = ArbreBinaire
arbre = A(20, A(7, A(4, A(2)), A(15, A(5))), A(53, A(46, A(29)), A(80, A(74))))
print('Q7 mystere =', arbre.mystere(), '(hauteur, racine de profondeur 0)')
print('Q10 taille =', arbre.taille(), '; feuille seule :', A(3).taille())
print('Q11 somme du sous-arbre droit de la racine =', arbre.droit.somme(), '; somme totale =', arbre.somme())


# Les tests cachés de la page passent sur la correction de la page
def tests_de_la_page(f='index.html'):
    import html
    import os
    import re
    page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f), encoding='utf-8').read()
    for sec in re.findall(r'<section class="td-q" data-type="code".*?</section>', page, re.S):
        nom = re.search(r'id="([^"]+)"', sec).group(1)
        corr = re.search(r'<pre class="td-code" data-verifier="correction">\n?(.*?)</pre>', sec, re.S)
        tests = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', sec, re.S)
        g = {}
        exec(html.unescape(corr.group(1)), g)
        if tests:
            exec(tests.group(1), g)
        print(f'{nom} : la correction passe les tests de la page')


tests_de_la_page('index.html')
tests_de_la_page('feuille-2.html')
print('tout est juste')
