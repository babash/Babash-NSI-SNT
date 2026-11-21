#!/usr/bin/env python3
"""Corrigé vérifié du DM flash « Un jeu de cartes » (niveau avancé, T125).

Usage, à la racine du dépôt : python3 -I nsi-terminale/fichiers/dm-flash-terminale/dm-poo-cartes-avance/source/verifier.py
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
blocs = [html.unescape(b) for b in re.findall(r'\n  <pre class="td-code">\n(.*?)</pre>', page, re.S)]
classes, prog1, prog2 = blocs
egal(max(len(l) for b in blocs for l in b.split('\n')) <= 80, True, 'code affiché : 80 caractères au plus')

# q3 : le programme 1, écrit à la fin du fichier (lignes 44 à 53)
fichier = classes + '\n\n' + prog1 + '\n'
egal(fichier.split('\n')[43:53], prog1.split('\n'), 'q3 : le programme occupe les lignes 44 à 53')
etat, msg, sortie = lancer(fichier, fichier='cartes.py')
egal(sortie.split(), ['2', '2', '2', 'coeur', '3', '12', '3'], 'q3 : ce qui s\'affiche avant l\'erreur')
egal(msg.rstrip(), Q['q3']['erreurs'][0].rstrip(), 'q3 : message réel')
# le code d'origine écrivait caret1 et caret2 : il s'arrêtait plus tôt
_, msg, s = lancer(classes + '\n\n' + prog1.replace('print(carte1.get_couleur())', 'print(caret1.get_couleur())'), fichier='cartes.py')
print('code d\'origine (caret1) :', s.split(), msg.strip().splitlines()[-1])

COMPLET = Q['q7']['corrections'][0]
# q8 : le programme 2 avec les classes complétées
_, msg, s = lancer(COMPLET + '\n' + prog2, fichier='cartes.py')
egal((s, msg.strip().splitlines()[-1]), ('', "TypeError: object of type 'method' has no len()"), 'q8 : le programme 2 s\'arrête aussitôt')
egal("TypeError: object of type 'method' has no len()" in html.unescape(page), True, 'q8 : message cité dans la correction')
# q10 : deux cartes égales ne sont pas ==
_, _, s = lancer(COMPLET + '\nprint(Carte(2, 2) == Carte(2, 2))')
egal(s.strip(), 'False', 'q10 : Carte(2, 2) == Carte(2, 2)')
# q6 : la position annoncée dans la correction
_, _, s = lancer(COMPLET + '\np = Paquet()\np.remplir()\nprint([i for i in range(52) if (p.contenu[i].couleur, p.contenu[i].valeur) == (2, 2)])')
egal(s.strip(), '[14]', 'q6 et q9 : position du 2 de couleur 2')

verifier_code('q6', [
    ('range(1, 4)', [('range(1, 5)', 'range(1, 4)')]),
    ('range(1, 13)', [('range(1, 14)', 'range(1, 13)')]),
    ('tuple au lieu de Carte', [('Carte(couleur, valeur)', '(couleur, valeur)')]),
    ('remplace la liste', [('self.contenu.append(Carte(couleur, valeur))', 'self.contenu = [Carte(couleur, valeur)]')]),
    ('paramètres inversés', [('Carte(couleur, valeur)', 'Carte(valeur, couleur)')]),
    ('range(0, 4)', [('range(1, 5)', 'range(4)')]),
], Q)
verifier_code('q7', [
    ('<=', [('0 <= pos < self.nb_cartes()', '0 <= pos <= self.nb_cartes()')]),
    ('52 en dur', [('0 <= pos < self.nb_cartes()', '0 <= pos < 52')]),
    ('renvoie la liste', [('return self.contenu[pos]', 'return self.contenu')]),
    ('position décalée', [('return self.contenu[pos]', 'return self.contenu[pos - 1]')]),
    ('sans le test du bas', [('0 <= pos < self.nb_cartes()', 'pos < self.nb_cartes()')]),
], Q)
verifier_code('q9', [
    ('sans le f', [('print(f"Trouvé', 'print("Trouvé')]),
    ('range de 1 à 52', [('range(paquet.nb_cartes())', 'range(1, paquet.nb_cartes()+1)')]),
    ('len de la méthode', [('range(paquet.nb_cartes())', 'range(len(paquet.nb_cartes))')]),
], Q)
fin()
