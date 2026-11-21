#!/usr/bin/env python3
"""Corrigé vérifié du DM flash « La classe Recette » (une liste dans un objet, T125).

Usage, à la racine du dépôt : python3 -I nsi-terminale/fichiers/dm-flash-terminale/dm-poo-liste/source/verifier.py
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
affiche = re.search(r'<pre class="td-code">\n(class Recette:.*?)</pre>', page, re.S).group(1)
muffin = re.search(r'<pre class="td-code">\n(muffin = .*?)</pre>', page, re.S).group(1)
# la classe affichée, avec calcul_prix tel quel et ajouter remplacée par la correction
CLASSE = affiche.replace("    def ajouter(...):\n        ...\n", "    def ajouter(self, ingredient, quantite, unite):\n        pass\n")
egal(len(muffin.split('\n')), 6, 'code du muffin : 6 lignes')

# q3 : types renvoyés
_, _, s = lancer(CLASSE + '\n' + muffin + '\nprint(type(muffin.ajouter("sel", 1, "g")).__name__, type(prix).__name__)')
egal(s.strip().split('\n')[-1], 'NoneType float', 'q3 : types renvoyés par ajouter et calcul_prix')
# q6 : la ligne 6, par exécution
_, _, s = lancer(CLASSE + '\n' + muffin)
egal(s.strip(), Q['q6']['reponses'][0], 'q6 : affichage de la ligne 6')
# q7 : les valeurs successives de total
trace = CLASSE.replace('            total += prix_unitaires[i] * self.quantites[i]\n',
                       '            total += prix_unitaires[i] * self.quantites[i]\n            print(i, total)\n')
_, _, s = lancer(trace + '\n' + muffin.split('\nprint')[0])
egal(s.strip(), '0 10.0\n1 65.0\n2 215.0\n3 215.5', 'q7 : i et total à chaque tour')
egal(Q['q7']['reponses'][0], '10.0, 65.0, 215.0, 215.5', 'q7 : première réponse acceptée')

verifier_code('q2', [
    ('remplace les listes', [('self.ingredients.append(ingredient)', 'self.ingredients = [ingredient]')]),
    ('insère au début', [('self.ingredients.append(ingredient)\n        self.quantites.append(quantite)\n        self.unites.append(unite)',
                          'self.ingredients.insert(0, ingredient)\n        self.quantites.insert(0, quantite)\n        self.unites.insert(0, unite)')]),
    ('oublie l unité', [('        self.unites.append(unite)\n', '')]),
    ('mauvaise liste', [('self.quantites.append(quantite)', 'self.unites.append(quantite)')]),
    ('paramètres dans un autre ordre', [('def ajouter(self, ingredient, quantite, unite)', 'def ajouter(self, ingredient, unite, quantite)')]),
], Q)
verifier_code('q4', [
    ('pommes de terre : 1 g', [('["g", "g", "g", "kg"]', '["g", "g", "g", "g"]')]),
    ('listes désalignées', [('[500, 200, 200, 1]', '[200, 500, 200, 1]')]),
    ('un seul ingrédient en moins', [('"lardons fumés", ', ''), ('[500, 200, 200, 1]', '[500, 200, 1]'), ('["g", "g", "g", "kg"]', '["g", "g", "kg"]')]),
    ('paramètres dans le désordre', [('                      [500, 200, 200, 1],\n                      ["g", "g", "g", "kg"])', '                      ["g", "g", "g", "kg"],\n                      [500, 200, 200, 1])')]),
    ('pas de nom', [('Recette("Tartiflette",', 'Recette("",')]),
], Q)
verifier_code('q5', [
    ('ajoute au lieu de remplacer', [('tartiflette.quantites[0] = 1000', 'tartiflette.quantites[0] += 1000')]),
    ('1 sans changer l unité', [('tartiflette.quantites[0] = 1000', 'tartiflette.quantites[0] = 1')]),
    ('mauvaise position', [('tartiflette.quantites[0] = 1000', 'tartiflette.quantites[1] = 1000')]),
    ('écrase la liste', [('tartiflette.quantites[0] = 1000', 'tartiflette.quantites = [1000]')]),
    ('variable sans effet', [('tartiflette.quantites[0] = 1000', 'reblochon = 1000')]),
    ('append', [('tartiflette.quantites[0] = 1000', 'tartiflette.quantites.append(1000)')]),
], Q)
verifier_code('q8', [
    ('<= au lieu de <', [('elif cellier[ingredient] < besoin:', 'elif cellier[ingredient] <= besoin:')]),
    ('oublie les absents', [('                courses.append((ingredient, besoin))\n', '                pass\n')]),
    ('quantité du cellier', [('besoin - cellier[ingredient]', 'cellier[ingredient]')]),
    ('quantité de la recette', [('besoin - cellier[ingredient]', 'besoin')]),
    ('dictionnaire', [('courses = []', 'courses = {}'), ('courses.append((ingredient, besoin))', 'courses[ingredient] = besoin'),
                      ('courses.append((ingredient, besoin - cellier[ingredient]))', 'courses[ingredient] = besoin - cellier[ingredient]')]),
    ('listes au lieu de tuples', [('courses.append((ingredient, besoin))', 'courses.append([ingredient, besoin])'),
                                  ('courses.append((ingredient, besoin - cellier[ingredient]))', 'courses.append([ingredient, besoin - cellier[ingredient]])')]),
    ('oublie le return', [('        return courses', '        print(courses)')]),
], Q)
# la correction de q8 donne l'exemple de la consigne
_, _, s = lancer(Q['q8']['corrections'][0] + '\n' + muffin.split('\nprix')[0] + '\nprint(muffin.liste_course({"farine": 500, "chocolat": 20, "oeuf": 2}))')
egal(s.strip(), "[('chocolat', 30), ('lait', 200)]", 'q8 : exemple de la consigne')
fin()
