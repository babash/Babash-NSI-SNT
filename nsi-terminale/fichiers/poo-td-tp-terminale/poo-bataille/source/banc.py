"""Banc d'essai des questions « code » d'un TD en ligne (T125, lot L5).

Ce module est copié tel quel dans le dossier source/ de chaque TD, à côté de verifier.py.
Il exécute, avec Python 3.13, exactement ce que fait le moteur (assets/td-en-ligne.js) :
le programme de l'élève, puis les tests (script.td-tests) dans le même espace de noms.
Résultat : ('ok', sortie), ('erreur', message de Python) ou ('test', message du test).

Contrôles d'une question « code » (verifier_code) :
- chaque correction (pre.td-code[data-verifier="correction"]) passe les tests ;
- le code de départ (pre.td-depart) ne les passe pas ;
- chaque classe volontairement fausse (une liste de remplacements dans la correction)
  est refusée par les tests.
"""
import html
import json
import pathlib
import re
import subprocess
import sys

LANCEUR = r'''
import sys, json, traceback, linecache, io, contextlib
d = json.loads(sys.stdin.read())
src, tests, nom = d["code"], d["tests"], d["fichier"]
linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)
g = {"__name__": "__main__"}
def rapport(e):
    tb = e.__traceback__.tb_next if e.__traceback__ else None
    return "".join(traceback.format_exception(type(e), e, tb))
sortie = io.StringIO()
def fin(etat, detail):
    print(json.dumps({"etat": etat, "detail": detail, "sortie": sortie.getvalue()}))
    sys.exit(0)
with contextlib.redirect_stdout(sortie):
    try:
        exec(compile(src, nom, "exec"), g)
    except SystemExit:
        pass
    except BaseException as e:
        r = rapport(e)
        sys.stdout = sys.__stdout__
        fin("erreur", r)
    if tests:
        try:
            exec(compile(tests, "tests.py", "exec"), g)
        except AssertionError as e:
            sys.stdout = sys.__stdout__
            fin("test", str(e))
        except BaseException as e:
            r = rapport(e)
            sys.stdout = sys.__stdout__
            fin("test", r)
fin("ok", "")
'''

ICI = pathlib.Path(sys.argv[0]).resolve().parent
PAGE = ICI.parent / 'index.html'
PROBLEMES = []


def lancer(code, tests='', fichier='mon_code.py'):
    r = subprocess.run([sys.executable, '-I', '-c', LANCEUR], input=json.dumps({'code': code, 'tests': tests, 'fichier': fichier}),
                       capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        return 'erreur', r.stderr, ''
    d = json.loads(r.stdout.strip().split('\n')[-1])
    return d['etat'], d['detail'], d['sortie']


def _pre(t):
    t = html.unescape(t)
    return t[1:] if t.startswith('\n') else t


def questions(page=None):
    s = (page or PAGE).read_text(encoding='utf-8')
    q = {}
    for m in re.finditer(r'<section class="td-q" data-type="(\w+)"[^>]*? id="([\w-]+)"([^>]*)>(.*?)</section>', s, re.S):
        t, ident, attrs, corps = m.groups()
        tests = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', corps, re.S)
        dep = re.search(r'<pre class="td-depart">(.*?)</pre>', corps, re.S)
        att = re.search(r'<pre class="td-attendu">(.*?)</pre>', corps, re.S)
        q[ident] = {
            'type': t, 'attrs': attrs, 'corps': corps,
            'fichier': (re.search(r'data-fichier="([^"]*)"', attrs) or [None, 'mon_code.py'])[1],
            'tests': tests.group(1) if tests else '',
            'depart': _pre(dep.group(1)) if dep else None,
            'attendu': _pre(att.group(1)).rstrip() if att else None,
            'corrections': [_pre(c) for c in re.findall(r'<pre class="td-code" data-verifier="correction">(.*?)</pre>', corps, re.S)],
            'reponses': html.unescape((re.search(r'data-reponse="([^"]*)"', attrs) or [None, ''])[1]).split('|'),
            'erreurs': [_pre(e) for e in re.findall(r'<pre class="td-erreur">(.*?)</pre>', corps, re.S)],
        }
    return q


def ko(msg):
    PROBLEMES.append(msg)
    print('  PROBLÈME :', msg)


def norm_sortie(s):
    return '\n'.join(' '.join(l.split()).lower() for l in s.replace('\r', '').split('\n') if l.strip())


def verifier_code(ident, fausses, q=None):
    """fausses : liste de (nom, [(ancien, nouveau), …]) appliqués à la première correction."""
    q = (q or questions())[ident]
    assert q['type'] == 'code' and q['corrections'], ident
    def juge(code):
        etat, detail, sortie = lancer(code, q['tests'], q['fichier'])
        if etat == 'ok' and q['attendu'] is not None and norm_sortie(sortie) != norm_sortie(q['attendu']):
            return 'sortie', sortie
        return etat, detail
    for i, c in enumerate(q['corrections']):
        r = juge(c)
        print(f'{ident} correction {i + 1} : {r[0]}')
        if r[0] != 'ok':
            ko(f'{ident} : la correction {i + 1} est refusée : {r[1]}')
    if q['depart'] is not None:
        r = juge(q['depart'])
        print(f'{ident} code de départ : refusé ({r[0]}) : {r[1].strip().splitlines()[-1] if r[1].strip() else ""}')
        if r[0] == 'ok':
            ko(f'{ident} : le code de départ passe les tests')
    for nom, remplacements in fausses:
        c = q['corrections'][0]
        for a, b in remplacements:
            if a not in c:
                ko(f'{ident} / {nom} : « {a} » absent de la correction')
            c = c.replace(a, b)
        r = juge(c)
        dernier = r[1].strip().splitlines()[-1] if r[1].strip() else ''
        print(f'{ident} fausse « {nom} » : {"refusée" if r[0] != "ok" else "ACCEPTÉE"} ({r[0]}) {dernier[:110]}')
        if r[0] == 'ok':
            ko(f'{ident} : la classe fausse « {nom} » passe les tests')


def egal(a, b, msg):
    print(('ok   ' if a == b else 'FAUX ') + msg + f' : {a!r}')
    if a != b:
        ko(f'{msg} : obtenu {a!r}, attendu {b!r}')


def fin():
    print(sys.version.split()[0], ':', 'tout est juste' if not PROBLEMES else f'{len(PROBLEMES)} problème(s)')
    sys.exit(1 if PROBLEMES else 0)
