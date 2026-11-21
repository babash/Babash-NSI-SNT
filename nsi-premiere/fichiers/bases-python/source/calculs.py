"""Outils communs des scripts de calcul des TD (exécution réelle, robot, tests du moteur)."""
import contextlib
import io
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import robot  # noqa: E402,F401


def sortie(code, g=None):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(code, g if g is not None else {})
    return out.getvalue()


def ok(nom, obtenu, attendu):
    print(f'{nom} : {obtenu!r}', 'OK' if obtenu == attendu else f'FAUX (attendu {attendu!r})')
    if obtenu != attendu:
        sys.exit(1)


def tours(code, grille='for', depart=None):
    """Nombre de tours de la PREMIÈRE boucle while du programme (robot compris)."""
    lignes = code.split('\n')
    i = next(k for k, l in enumerate(lignes) if l.lstrip().startswith('while '))
    ind = len(lignes[i + 1]) - len(lignes[i + 1].lstrip())
    lignes.insert(i + 1, ' ' * ind + '_t[0] += 1')
    r = robot.Robot(grille, depart)
    g = {'_t': [0], **r.fonctions()}
    with contextlib.redirect_stdout(io.StringIO()):
        exec('\n'.join(lignes), g)
    return g['_t'][0]


def tourne_sans_fin(code, delai=2):
    try:
        subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, timeout=delai)
        return False
    except subprocess.TimeoutExpired:
        return True


def tests_de_page(page):
    """Les paires (correction, tests) des questions « code » d'une page, comme le moteur les exécute."""
    s = open(os.path.join(ICI, '..', page), encoding='utf-8').read()
    paires = []
    for sec in re.findall(r'<section class="td-q" data-type="code".*?</section>', s, re.S):
        t = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', sec, re.S)
        for c in re.findall(r'<pre class="td-code" data-verifier="correction">\n(.*?)</pre>', sec, re.S):
            c = c.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&amp;', '&')
            paires.append((c, t.group(1) if t else ''))
    return paires


def verifier_tests(page):
    for k, (c, t) in enumerate(tests_de_page(page)):
        g = {}
        exec(c, g)
        with contextlib.redirect_stdout(io.StringIO()):
            exec(t, g)
        print(f'{page} : tests du programme {k + 1}, sur la correction : OK')
