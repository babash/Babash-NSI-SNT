#!/usr/bin/env python3
"""Feuille d'exercices « CSV et listes de listes » (T125) : le corrigé, obtenu par exécution réelle (Python 3.13).

Usage, à la racine du dépôt :
  python3 -I nsi-premiere/fichiers/python-exercices-structures-premiere/source/tester-csv-listes-de-listes.py

Les données : le fichier ../exercices-csv-listes-de-listes/comparaisons-communes-mayotte.csv (Insee), lu par le module csv
comme dans le TD. Dans la page, les tests de chaque question « Écris le programme » le reconstruisent depuis une chaîne
(csv.reader(io.StringIO(DONNEES))) : Python dans le navigateur n'a pas de fichier.
1. Chaque réponse est recalculée sur le fichier et comparée à la page.
2. Chaque correction passe ses tests (script.td-tests), exécutés comme dans le moteur ; chaque version
   volontairement fausse ci-dessous est refusée par ces mêmes tests. Les tests de la page doivent contenir
   exactement le fichier fourni.
"""
import html.parser
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, '..', 'exercices-csv-listes-de-listes')
FEUILLES = ['index.html', 'feuille-2.html', 'feuille-3.html']

# le lanceur du moteur (assets/td-en-ligne.js, _td_lancer), en CPython
LANCEUR = r'''
import sys, traceback, json
src, tests, nom = json.loads(sys.stdin.read())
import linecache
linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)
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


# ── 1. Les réponses calculées : le fichier lu par le module csv, le code du TD exécuté ──
import csv
import io
import contextlib

tab = list(csv.reader(open(os.path.join(DOSSIER, 'comparaisons-communes-mayotte.csv'), encoding='utf-8')))


def filter_null(data):
    new_data = []
    for l in data:
        count_null = 0
        for v in l:
            if v == '0' or v == "":
                count_null += 1
        if count_null < len(l) - 1:
            new_data.append(l)
    return new_data


def trace(data, ligne):
    """count_null après chaque valeur de la ligne demandée (le tableau d'avancement)."""
    c, r = 0, []
    for v in data[ligne]:
        if v == '0' or v == "":
            c += 1
        r.append((v, c))
    return r


def stats_communes(data):          # la fonction complétée (question m5)
    for i in range(1, len(data[0])):
        commune = data[0][i]
        pop = data[3][i]
        siren = data[1][i]
        print("Dans la commune de", commune, "(SIREN", siren,
              ") il y a", pop, "habitants.")


sortie = io.StringIO()
with contextlib.redirect_stdout(sortie):
    stats_communes(tab)
lignes_stats = sortie.getvalue().splitlines()
pam = tab[0].index('Pamandzi')
supprimees = [l[0] for l in tab if l not in filter_null(tab)]

CALCULS = [('k3', tab[2][pam], str), ('k4', tab[3][pam], str), ('m7 (correction)', None, None)]
CALCULS = [c for c in CALCULS if c[1] is not None]
CONTROLES = {
    'k1 : 17 communes, de Kani-Kéli à Dembeni': len(tab[0]) - 1 == 17 and tab[0][1] == 'Kani-Kéli' and tab[0][-1] == 'Dembeni',
    'k5 : des cases vides (,,) existent, ligne « Solde net FPIC »': all(v == '' for v in tab[21][1:]) and tab[21][0].startswith('Solde net FPIC'),
    'm2 : type(tab[0]) est list, type(tab[6][5]) est str': type(tab[0]) is list and type(tab[6][5]) is str,
    'm3 : tab[4][4] est la population municipale de Bandrele (10282)': tab[4][0].startswith('Population municipale') and tab[0][4] == 'Bandrele' and tab[4][4] == '10282',
    'm4 : len(tab[0]) - 1 vaut 17': len(tab[0]) - 1 == 17,
    'm5 : première ligne affichée': lignes_stats[0] == 'Dans la commune de Kani-Kéli (SIREN 200008803 ) il y a 5716 habitants.' and len(lignes_stats) == 17,
    'm7 : population totale 262895.0': sum(float(x) for x in tab[3][1:]) == 262895.0,
    'n1 : ligne 0, count_null reste 0 ; tours 0,1 et 0,2': trace(tab, 0)[1] == ('Kani-Kéli', 0) and trace(tab, 0)[2] == ('Chirongui', 0) and trace(tab, 0)[-1][1] == 0,
    'n1 : ligne 1, tour 1,0': trace(tab, 1)[0] == ('SIREN', 0),
    'n1 : ligne 6, tours 6,0 / 6,1 / 6,2 / 6,17': [x[1] for x in trace(tab, 6)][:3] == [0, 1, 2] and trace(tab, 6)[1][0] == '0' and trace(tab, 6)[17][1] == 17,
    'n1 : len(l) - 1 vaut 17 et 17 < 17 vaut False': len(tab[6]) - 1 == 17 and (17 < 17) is False,
    'n2 : cochées supprimées, non cochées gardées': all(any(s.startswith(p) for s in supprimees) for p in ('Variation annuelle', 'Solde net FPIC', 'Dotation élu local'))
        and not any(any(s.startswith(p) for s in supprimees) for p in ('Classement de la commune', 'Nom de la commune', 'Population « DGF »')),
    'n2 : 12 lignes supprimées, 14 gardées': len(supprimees) == 12 and len(filter_null(tab)) == 14,
    'p2 : tab[0][1:] donne les 17 communes': tab[0][1:] == tab[0][1:18] and len(tab[0][1:]) == 17,
}

# ── 2. Des versions volontairement fausses, que les tests doivent refuser ──────
FAUSSES = {
    'm7': {
        'oublie la colonne des titres': 'def population_totale(data):\n    return sum(float(x) for x in data[3])\n',
        'population municipale (ligne 4)': 'def population_totale(data):\n    return sum(float(x) for x in data[4][1:])\n',
        'int au lieu de float': 'def population_totale(data):\n    return sum(int(x) for x in data[3][1:])\n',
        'valeur écrite en dur': 'def population_totale(data):\n    return 262895.0\n',
        'oublie la dernière commune': 'def population_totale(data):\n    t = 0\n    for i in range(1, len(data[3]) - 1):\n        t = t + float(data[3][i])\n    return t\n',
        'concatène les textes': 'def population_totale(data):\n    t = ""\n    for x in data[3][1:]:\n        t = t + x\n    return t\n',
    },
    'r2': {
        'garde « Nom de la commune »': 'def longueurs_noms(data):\n    return [len(v) for v in data[0]]\n',
        'avec append': 'def longueurs_noms(data):\n    r = []\n    for v in data[0][1:]:\n        r.append(len(v))\n    return r\n',
        'les noms au lieu des longueurs': 'def longueurs_noms(data):\n    return [v for v in data[0][1:]]\n',
        'mauvaise ligne': 'def longueurs_noms(data):\n    return [len(v) for v in data[1][1:]]\n',
    },
    'r3': {
        'la ligne 0 au lieu de la colonne 0': 'def noms_criteres(data):\n    return [v for v in data[0]]\n',
        'sans le premier critère': 'def noms_criteres(data):\n    return [l[0] for l in data[1:]]\n',
        'les lignes entières': 'def noms_criteres(data):\n    return [l for l in data]\n',
    },
    'r4': {
        'comparaison de textes': 'def grandes_communes(data):\n    return [data[0][i] for i in range(1, len(data[0])) if data[3][i] > "10000"]\n',
        'au moins 10 000 sur la ligne 2': 'def grandes_communes(data):\n    return [data[0][i] for i in range(1, len(data[0])) if float(data[2][i]) > 10000]\n',
        'sans condition': 'def grandes_communes(data):\n    return [data[0][i] for i in range(1, len(data[0]))]\n',
        'les populations au lieu des noms': 'def grandes_communes(data):\n    return [data[3][i] for i in range(1, len(data[0])) if float(data[3][i]) > 10000]\n',
        'avec append': 'def grandes_communes(data):\n    r = []\n    for i in range(1, len(data[0])):\n        if float(data[3][i]) > 10000:\n            r.append(data[0][i])\n    return r\n',
    },
    'r5': {
        'noms seulement': 'def grandes_communes_pop(data):\n    return [data[0][i] for i in range(1, len(data[0])) if float(data[3][i]) > 10000]\n',
        'population municipale': 'def grandes_communes_pop(data):\n    return [[data[0][i], data[4][i]] for i in range(1, len(data[0])) if float(data[3][i]) > 10000]\n',
        'paires inversées': 'def grandes_communes_pop(data):\n    return [[data[3][i], data[0][i]] for i in range(1, len(data[0])) if float(data[3][i]) > 10000]\n',
        'seuil 1000': 'def grandes_communes_pop(data):\n    return [[data[0][i], data[3][i]] for i in range(1, len(data[0])) if float(data[3][i]) > 1000]\n',
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
    brut = open(os.path.join(DOSSIER, 'comparaisons-communes-mayotte.csv'), encoding='utf-8').read()
    for qid in sorted(k for k, v in q.items() if v['tests']):
        if 'DONNEES = """' + brut + '"""' not in q[qid]['tests']:
            print(f'  NON {qid} : les données des tests ne sont pas le fichier fourni'); pb += 1
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
