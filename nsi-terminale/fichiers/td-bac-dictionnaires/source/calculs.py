"""Recalcule les réponses du TD type bac « dictionnaires » (Python 3.13) et les
compare à celles écrites dans la page. Usage : python3 -I calculs.py"""
import html, itertools, os, re
from random import shuffle

# ---------- Exercice 1 : Centres étrangers 2022, jour 2, exercice 2 ----------
alpha4 = {"A": "B", "B": "D", "C": "A", "D": "C"}
alpha = {"A": "B", "B": "D", "C": "A", "D": "C", "E": "F", "F": "G", "G": "E"}


def chiffrer(mot, alpha):
    resultat = ""
    for lettre in mot:
        resultat = resultat + alpha[lettre]
    return resultat


def dico_dechiffrement(dico):
    nouveau = {}
    for lettre in dico:
        code = dico[lettre]
        nouveau[code] = lettre
    return nouveau


def dechiffre(mot, dico):
    return chiffrer(mot, dico_dechiffrement(dico))


def dico_chiffrement(alphabet):
    melange = list(alphabet)
    shuffle(melange)
    dico = {}
    for i in range(len(alphabet)):
        dico[alphabet[i]] = melange[i]
    return dico


assert chiffrer("BAC", alpha4) == "DBA"                     # l'exemple de l'énoncé
assert alpha["D"] == "C"
assert chiffrer("BAGAGE", alpha) == "DBEBEF"
inverse = dico_dechiffrement(alpha)
assert inverse == {"B": "A", "D": "B", "A": "C", "C": "D", "F": "E", "G": "F", "E": "G"}
assert str(inverse) == "{'B': 'A', 'D': 'B', 'A': 'C', 'C': 'D', 'F': 'E', 'G': 'F', 'E': 'G'}"
assert dechiffre("DBEBEF", alpha) == "BAGAGE"
assert len(set(alpha.values())) == len(alpha)               # alpha est bien inversible
for _ in range(50):
    a = list("ABCDEFGHIJ")
    d = dico_chiffrement(a)
    assert sorted(d) == a and sorted(d.values()) == a and a == list("ABCDEFGHIJ")
    assert dechiffre(chiffrer("BAGAGE", d), d) == "BAGAGE"

# ---------- Exercice 2 : Antilles-Guyane 2026, jour 2, exercice 3, partie A ----------
prix = [0, 1, 5, 8, 9, 10, 17, 17, 20, 24, 30]
effectif = {1: 3, 2: 4, 4: 1}


def valeur_stock(effectif):
    valeur_totale = 0
    for longueur in effectif:
        valeur_totale = valeur_totale + prix[longueur] * effectif[longueur]
    return valeur_totale


def mise_a_jour(effectif, autre_effectif):
    for longueur in autre_effectif:
        if longueur in effectif:
            effectif[longueur] = effectif[longueur] + autre_effectif[longueur]
        else:
            effectif[longueur] = autre_effectif[longueur]


def vendre(effectif, longueur):
    effectif[longueur] = effectif[longueur] - 1
    if effectif[longueur] == 0:
        del effectif[longueur]


assert valeur_stock(effectif) == 3 * 1 + 4 * 5 + 1 * 9 == 32
assert (5 in effectif) is False and (4 in effectif) is True
e10 = {10: 2}
assert prix[10] * e10[10] == 60
e, c = {1: 3, 5: 5}, {1: 2, 2: 2}
mise_a_jour(e, c)
assert e == {1: 5, 2: 2, 5: 5} and c == {1: 2, 2: 2}         # l'exemple de l'énoncé
e = {1: 3, 5: 1}
vendre(e, 1)
assert e == {1: 2, 5: 1}                                     # exemple 1 de l'énoncé
vendre(e, 5)
assert e == {1: 2}                                           # exemple 2 de l'énoncé

# ---------- les réponses écrites dans la page ----------
# le TD a une feuille par exercice de bac (index.html, feuille-2.html) : on lit les deux
page = ''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f), encoding='utf-8').read()
               for f in ('index.html', 'feuille-2.html'))


def reponses(q):
    m = re.search(r'id="%s"[^>]*data-reponse="([^"]*)"' % q, page)
    return html.unescape(m.group(1)).split('|')


assert reponses('q1')[0] == alpha["D"]
assert reponses('q3')[0] == chiffrer("BAGAGE", alpha)
for r in reponses('q9'):                                     # chaque écriture acceptée vaut le bon dictionnaire
    assert eval(r.replace('effectif = ', '')) == {1: 3, 2: 4, 4: 1}, r
assert len(reponses('q9')) == 2 * len(list(itertools.permutations(effectif)))
g = {'prix': prix, 'effectif': {10: 2, 5: 1}}
for r in reponses('q10'):
    assert eval(r, g) == 60, r
for r in reponses('q11'):
    assert eval(r, {'effectif': {5: 1}}) is True and eval(r, {'effectif': {1: 2}}) is False, r
for k, v in inverse.items():
    assert '"%s": [["%s"]]' % (k, v) in page, k
print('tout est juste')
