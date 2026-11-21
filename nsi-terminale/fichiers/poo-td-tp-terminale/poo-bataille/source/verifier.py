#!/usr/bin/env python3
"""Corrigé vérifié de l'exercice préparatoire « La classe CarteBataille » (T125).

Usage, à la racine du dépôt : python3 -I nsi-terminale/fichiers/poo-td-tp-terminale/poo-bataille/source/verifier.py
Toutes les réponses de la page sont obtenues ici par exécution réelle (Python 3.13),
et les tests des questions « code » refusent des classes volontairement fausses.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from banc import lancer, questions, verifier_code, egal, fin  # noqa: E402

Q = questions()
CLASSE = Q['q3']['corrections'][0]

for rep in Q['q1']['reponses']:
    e, d, _ = lancer(rep + '\n    pass\nprint(CarteBataille.__name__)')
    egal(e, 'ok', f'q1 « {rep} » s\'exécute')
verifier_code('q2', [
    ('attributs inversés', [('self.valeur = valeur\n        self.symbole = symbole', 'self.valeur = symbole\n        self.symbole = valeur')]),
    ('sans self', [('self.valeur = valeur', 'valeur = valeur')]),
    ('attributs de classe partagés', [('    def __init__(self, valeur, symbole):\n        self.valeur = valeur\n        self.symbole = symbole',
                                       '    def __init__(self, valeur, symbole):\n        CarteBataille.valeur = valeur\n        CarteBataille.symbole = symbole')]),
    ('autres noms d attributs', [('self.valeur = valeur', 'self.v = valeur')]),
], Q)
verifier_code('q3', [
    ('>=', [('self.valeur > autre_carte.valeur', 'self.valeur >= autre_carte.valeur')]),
    ('à l envers', [('self.valeur > autre_carte.valeur', 'autre_carte.valeur > self.valeur')]),
    ('affiche au lieu de renvoyer', [('return self.valeur > autre_carte.valeur', 'print(self.valeur > autre_carte.valeur)')]),
    ('compare les symboles', [('self.valeur > autre_carte.valeur', 'self.symbole > autre_carte.symbole')]),
    ('renvoie la valeur', [('return self.valeur > autre_carte.valeur', 'return self.valeur')]),
], Q)
for q, attendu in (('q4', '10 Trèfle'), ('q5', '13 Coeur')):
    for rep in Q[q]['reponses']:
        var = rep.split('=')[0].strip()
        _, d, s = lancer(CLASSE + '\n' + rep + f'\nprint({var}.valeur, {var}.symbole)')
        ok = s.strip() == attendu or s.strip() in ('10 Trefle', '13 Cœur')
        egal(ok, True, f'{q} « {rep} » : {s.strip()}')
_, _, s = lancer(CLASSE + '\njoueur1 = CarteBataille(10, "Trèfle")\nprint(joueur1)')
egal(bool(re.fullmatch(r'<__main__\.CarteBataille object at 0x[0-9a-f]+>', s.strip())), True, 'q6 : print(joueur1) : ' + s.strip())
verifier_code('q7', [
    ('print de l objet', [('print(joueur1.valeur, "de", joueur1.symbole)', 'print(joueur1)')]),
    ('gagnant inversé', [('print("Joueur 1 gagne !")\nelse:\n    print("Joueur 2 gagne !")', 'print("Joueur 2 gagne !")\nelse:\n    print("Joueur 1 gagne !")')]),
    ('affiche le booléen', [('if joueur1.battre(joueur2):\n    print("Joueur 1 gagne !")\nelse:\n    print("Joueur 2 gagne !")', 'print(joueur1.battre(joueur2))')]),
    ('cartes inversées', [('joueur1 = CarteBataille(10, "Trèfle")\njoueur2 = CarteBataille(13, "Coeur")', 'joueur2 = CarteBataille(10, "Trèfle")\njoueur1 = CarteBataille(13, "Coeur")')]),
], Q)
fin()
