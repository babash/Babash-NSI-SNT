#!/usr/bin/env python3
"""Mission « interception des pirates » (T125) : le corrigé, obtenu par exécution réelle (Python 3.13).

Usage, à la racine du dépôt :
  python3 -I nsi-premiere/fichiers/python-exercices-bases-premiere/source/tester-mission-fonctions.py

1. Chaque réponse courte ou calculée des feuilles est recalculée en exécutant le code du TD,
   et comparée à la réponse attendue écrite dans la page (data-reponse).
2. Chaque question « Écris le programme » : la correction passe ses tests (script.td-tests),
   exécutés comme dans le moteur (même espace de noms, après le programme) ;
   puis chaque version volontairement fausse ci-dessous doit être refusée par ces mêmes tests.
"""
import html.parser
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, '..', 'mission-fonctions')
FEUILLES = ['index.html', 'feuille-2.html', 'feuille-3.html', 'feuille-4.html', 'feuille-5.html']

# le lanceur du moteur (assets/td-en-ligne.js, _td_lancer), en CPython
LANCEUR = r'''
import sys, traceback, json
src, tests, nom = json.loads(sys.stdin.read())
g = {"__name__": "__main__"}
def rapport(e):
    tb = e.__traceback__.tb_next if e.__traceback__ else None
    return "".join(traceback.format_exception(type(e), e, tb))
def lancer():
    try:
        exec(compile(src, nom, "exec"), g)
    except BaseException as e:
        return ["erreur", rapport(e)]
    if tests:
        try:
            exec(compile(tests, "tests.py", "exec"), g)
        except AssertionError as e:
            return ["test", str(e)]
        except BaseException as e:
            return ["test", rapport(e)]
    return ["ok", ""]
print(json.dumps(lancer()))
'''


def lancer(src, tests, nom='mon_code.py'):
    import json
    r = subprocess.run([sys.executable, '-I', '-c', LANCEUR], input=json.dumps([src, tests, nom]),
                       capture_output=True, text=True, timeout=10)
    return json.loads(r.stdout.strip().splitlines()[-1])


class Lecteur(html.parser.HTMLParser):
    """Relève, par question : data-reponse, le script de tests et la correction exécutable."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.q, self.courant, self.pile = {}, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section' and 'td-q' in (a.get('class') or ''):
            self.courant = a['id']
            self.q[self.courant] = {'reponse': a.get('data-reponse'), 'tests': '', 'correction': '', 'fichier': a.get('data-fichier')}
        if self.courant and tag == 'script' and 'td-tests' in (a.get('class') or ''):
            self.pile.append('tests')
        elif self.courant and tag == 'pre' and a.get('data-verifier') == 'correction':
            self.pile.append('correction')
        elif tag in ('script', 'pre'):
            self.pile.append(None)

    def handle_endtag(self, tag):
        if tag in ('script', 'pre') and self.pile:
            self.pile.pop()
        if tag == 'section':
            self.courant = None

    def handle_data(self, d):
        if self.courant and self.pile and self.pile[-1]:
            self.q[self.courant][self.pile[-1]] += d


def lire():
    q = {}
    for f in FEUILLES:
        lu = Lecteur()
        lu.feed(open(os.path.join(DOSSIER, f), encoding='utf-8').read())
        for k, v in lu.q.items():
            v['feuille'] = f
            q[k] = v
    return q


# ── 1. Les réponses calculées : le code du TD, exécuté ─────────────────────────
ALPHA = 'abcdefghijklmnopqrstuvwxyz'


def signal_alpha(vitesse_hyperespace):
    temps_voyage = 5000 / vitesse_hyperespace
    return temps_voyage


def signal_beta(niveau_alerte):
    if niveau_alerte > 1000:
        est_critique = True
    else:
        est_critique = False
    return est_critique


def cryptage(code_acces):
    code_inverse = ""
    for caractere in code_acces:
        code_inverse = caractere + code_inverse
    return code_inverse


def scanner(inventaire_pieces):
    pieces_valides = []
    for piece in inventaire_pieces:
        if "cyber" in piece:
            pieces_valides.append(piece)
    return pieces_valides


def calculer_carburant(distance):
    return distance * 15


def est_allie(matricule):
    return matricule[0:2] == "RX" or matricule[0:2] == "CZ"


def sceller(frequences, cle):
    return [f + cle for f in frequences]


def cesar(mot, n):
    return ''.join(ALPHA[(ALPHA.index(x) + n) % 26] if x in ALPHA else x for x in mot)


def vigenere(mot, decalages):
    r, i = '', 0
    for x in mot:
        r += ALPHA[(ALPHA.index(x) + decalages[i]) % 26]
        i = (i + 1) % len(decalages)
    return r


# (question, valeur calculée, transformation en texte attendu)
CALCULS = [
    ('a5', signal_alpha(100), str),
    ('c5', cryptage("PIRATE"), str),
    ('d5', scanner(["moteur", "cyber-jambe", "laser"]), repr),
    ('e2', calculer_carburant(10), str),
    ('e3', 30000 // 15 if calculer_carburant(30000 // 15) == 30000 else None, str),
    ('h1', cesar("bonjour tout le monde", 1), str),
    ('h2', cesar("je suis ton ami", 1), str),
    ('h3', cesar("mb dibodf ftu fo upj", -1), str),
    ('h4', cesar("qfuju b qfuju m pjtfbv gbju tpo oje", -1), str),
    ('i2', cesar("sur", -2), str),
]
# réponses des QCU vérifiées par le calcul (la bonne option doit être vraie, les autres fausses)
CONTROLES = {
    'b5 : False puis True': (signal_beta(100), signal_beta(5000)) == (False, True),
    'c6 : premier P, dernier E': [c for c in "PIRATE"][0] == 'P' and [c for c in "PIRATE"][-1] == 'E',
    'f2 : True puis False': (est_allie("RXD6"), est_allie("D6F4")) == (True, False),
    'f3 : seule CZ81 donne True': [est_allie(m) for m in ("CZ81", "XR12", "cz81", "A-RX5")] == [True, False, False, False],
    'f4 : seule ZC07 donne False': [est_allie(m) for m in ("ZC07", "RX7", "CZCZ", "RX00")] == [False, True, True, True],
    'g2 : une seule option juste': [sceller(l, c) == [23, 33, 43, 63] for l, c in
                                    (([20, 30, 40, 60], 3), ([20, 30, 40, 50], 3), ([26, 36, 46, 66], 3), ([20, 30, 40, 60], 13))] == [True, False, False, False],
    'g3 : une seule option juste': [sceller(l, c) == [7, 14, 9] for l, c in
                                    (([5, 12, 7], 2), ([5, 12, 7], 7), ([7, 14, 9], 7), ([2, 7, 2], 7))] == [True, False, False, False],
    'g2, g3 : les autres entrées citées': sceller([13, 23, 33, 53], 10) == [23, 33, 43, 63] and sceller([0, 7, 2], 7) == [7, 14, 9],
    'exemple de sceller_donnees': sceller([100, 200], 7) == [107, 207],
    'exemple de Vigenère (corrigé : bcdb)': vigenere("aaaa", [1, 2, 3]) == "bcdb",
    'i2 : qsp redonne sur': cesar("qsp", 2) == "sur",
    'a2 : 5000 / 50 est un float': isinstance(signal_alpha(50), float),
}

# ── 2. Des versions volontairement fausses, que les tests doivent refuser ──────
FAUSSES = {
    'f6': {
        'seulement RX': 'def est_allie(matricule):\n    return matricule[0:2] == "RX"\n',
        'and au lieu de or': 'def est_allie(matricule):\n    return matricule[0:2] == "RX" and matricule[0:2] == "CZ"\n',
        'RX n\'importe où': 'def est_allie(matricule):\n    return "RX" in matricule or "CZ" in matricule\n',
        'textes "Vrai" / "Faux"': 'def est_allie(matricule):\n    if matricule[0:2] in ("RX", "CZ"):\n        return "Vrai"\n    return "Faux"\n',
        'print au lieu de return': 'def est_allie(matricule):\n    print(matricule[0:2] in ("RX", "CZ"))\n',
        'mauvaise tranche': 'def est_allie(matricule):\n    return matricule[1:3] in ("RX", "CZ")\n',
        'casse ignorée': 'def est_allie(matricule):\n    return matricule[0:2].upper() in ("RX", "CZ")\n',
        'renvoie 1 ou 0': 'def est_allie(matricule):\n    if matricule[0:2] in ("RX", "CZ"):\n        return 1\n    return 0\n',
    },
    'g5': {
        'oublie la clé': 'def sceller_donnees(frequences, cle):\n    return list(frequences)\n',
        'modifie la liste reçue': 'def sceller_donnees(frequences, cle):\n    for i in range(len(frequences)):\n        frequences[i] = frequences[i] + cle\n    return frequences\n',
        'return dans la boucle': 'def sceller_donnees(frequences, cle):\n    resultat = []\n    for f in frequences:\n        resultat.append(f + cle)\n        return resultat\n',
        'somme au lieu de liste': 'def sceller_donnees(frequences, cle):\n    s = 0\n    for f in frequences:\n        s = s + f + cle\n    return s\n',
        'clé ajoutée deux fois': 'def sceller_donnees(frequences, cle):\n    return [f + 2 * cle for f in frequences]\n',
    },
    'h6': {
        'décale vers la gauche': 'def code_cesar_un(mot):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[a.index(x) - 1] if x in a else x for x in mot)\n',
        'espaces codés avec find': 'def code_cesar_un(mot):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    r = ""\n    for x in mot:\n        r = r + a[a.find(x) + 1]\n    return r\n',
        'espaces supprimés': 'def code_cesar_un(mot):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[a.index(x) + 1] for x in mot if x in a)\n',
        'ordre inversé': 'def code_cesar_un(mot):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    r = ""\n    for x in mot:\n        r = (a[a.index(x) + 1] if x in a else x) + r\n    return r\n',
        'renvoie le mot': 'def code_cesar_un(mot):\n    return mot\n',
    },
    'i4': {
        'sans modulo': 'def cesar_general(mot, n):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[a.index(x) + n] if x in a else x for x in mot)\n',
        'modulo 25': 'def cesar_general(mot, n):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[(a.index(x) + n) % 25] if x in a else x for x in mot)\n',
        'décalage de 1 seulement': 'def cesar_general(mot, n):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[(a.index(x) + 1) % 26] if x in a else x for x in mot)\n',
        'espaces non gardés': 'def cesar_general(mot, n):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[(a.find(x) + n) % 26] for x in mot)\n',
    },
    'j3': {
        'compteur jamais remis à 0': 'def vigenere_liste(mot, decalages):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    r, i = "", 0\n    for x in mot:\n        r += a[(a.index(x) + decalages[i]) % 26]\n        i = i + 1\n    return r\n',
        'premier décalage seulement': 'def vigenere_liste(mot, decalages):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    return "".join(a[(a.index(x) + decalages[0]) % 26] for x in mot)\n',
        'remis à 0 trop tôt': 'def vigenere_liste(mot, decalages):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    r, i = "", 0\n    for x in mot:\n        r += a[(a.index(x) + decalages[i]) % 26]\n        i = i + 1\n        if i == len(decalages) - 1:\n            i = 0\n    return r\n',
        'sans modulo': 'def vigenere_liste(mot, decalages):\n    a = "abcdefghijklmnopqrstuvwxyz"\n    r, i = "", 0\n    for x in mot:\n        r += a[a.index(x) + decalages[i]]\n        i = (i + 1) % len(decalages)\n    return r\n',
    },
}


def principal():
    q = lire()
    pb = 0
    print('1. Réponses calculées')
    for qid, val, fmt in CALCULS:
        attendues = (q[qid]['reponse'] or '').split('|')
        txt = fmt(val)
        ok = txt in attendues or (fmt is repr and txt.replace('"', "'") in attendues)
        print(f'  {"ok " if ok else "NON"} {qid} ({q[qid]["feuille"]}) : calculé {txt!r} ; attendu dans la page {attendues[0]!r}')
        pb += not ok
    for nom, ok in CONTROLES.items():
        print(f'  {"ok " if ok else "NON"} {nom}')
        pb += not ok
    print('2. Questions « Écris le programme » : correction, puis versions fausses')
    for qid in sorted(k for k, v in q.items() if v['tests']):
        v = q[qid]
        etat, detail = lancer(v['correction'].lstrip('\n'), v['tests'], v['fichier'])
        print(f'  {"ok " if etat == "ok" else "NON"} {qid} ({v["feuille"]}) : la correction passe les tests')
        pb += etat != 'ok'
        for nom, code in FAUSSES.get(qid, {}).items():
            etat, detail = lancer(code, v['tests'], v['fichier'])
            refuse = etat != 'ok'
            print(f'      {"ok " if refuse else "NON"} version fausse « {nom} » refusée : {detail.strip().splitlines()[-1] if detail.strip() else etat}')
            pb += not refuse
        if not FAUSSES.get(qid):
            print('      NON aucune version fausse pour cette question'); pb += 1
    print(sys.version.split()[0], ':', 'tout est juste' if not pb else f'{pb} problème(s)')
    return 1 if pb else 0


if __name__ == '__main__':
    sys.exit(principal())
