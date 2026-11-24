#!/usr/bin/env python3
"""Essais des outils des TD (T123c) : ils doivent voir une fuite, et ne rien voir sur une feuille saine.

Usage (à la racine du dépôt) : python3 -I charte/tester-outils.py

1. imprimer-td.py sur le gabarit : « PDF vierge : oui ».
2. Témoins de fuite (pages temporaires, effacées ensuite, à côté de la page d'origine) : la page avec une règle
   d'impression qui affiche les corrections, puis une qui affiche les sorties attendues, puis une qui affiche les
   coups de pouce. imprimer-td.py doit répondre « NON » et nommer la fuite. Pages : le gabarit, et le témoin du
   Gardien 25 (« La casse du siècle », corrections forcées à l'impression : 18 corrections imprimées).
3. verifier-td.py sur le gabarit : « tout est juste ».
4. numeroter-feuilles.py --tout --verifier : il passe sur tout le dépôt, sans « Problème ».
5. Corrections partielles (T123d) : verifier-td.py pose une correction qui ne donne qu'une fonction ou une méthode
   sur le code de départ, comme l'élève : la fonction à sa place, la méthode dans sa classe. Les 10 cas des TD type
   bac (charte/essais/corrections-partielles.json) passent leurs tests cachés, et le départ seul ne les passe pas ;
   plus 4 cas écrits ici (méthode nouvelle, fonction nouvelle avant les instructions, correction en retrait, classe).
Code de sortie : 0 si tout est conforme.
"""
import functools
import importlib.util
import json
import http.server
import os
import subprocess
import sys
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
PAGES = ['charte/gabarit-td/index.html', 'nsi-premiere/fichiers/algorithmes-gloutons-premiere/casse-du-siecle/index.html']
FUITES = {
    'corrections': ('.td .td-q .td-correction, .td .td-q .td-correction *', 'correction'),
    'attendus': ('.td .td-q pre.td-attendu', 'attendu'),
    'coups de pouce': ('.td .td-q .td-aide', 'aide'),
}


class Silencieux(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def lancer(*args):
    r = subprocess.run([sys.executable, '-I', *args], capture_output=True, text=True, cwd=RACINE)
    return r.returncode, r.stdout + r.stderr


CAS_ECRITS = [
    ('méthode nouvelle, mise dans sa classe',
     'class Pile:\n    def __init__(self):\n        self.t = []\n\np = Pile()\np.empiler(3)\nprint(p.t)\n',
     'def empiler(self, x):\n    self.t.append(x)\n', 'p2 = Pile(); p2.empiler(1); assert p2.t == [1]\n'),
    ('fonction nouvelle, avant les instructions',
     'def double(x):\n    return 2 * x\n\nprint(quadruple(3))\n',
     'def quadruple(x):\n    return double(double(x))\n', 'assert quadruple(2) == 8\n'),
    ('correction écrite en retrait, méthode remplacée à sa place',
     'class A:\n    def f(self):\n        ...\n\n    def g(self):\n        return self.f() + 1\n\nprint(A().g())\n',
     '    def f(self):\n        return 1\n', 'assert A().g() == 2\n'),
    ('classe remplacée à sa place',
     'class B:\n    ...\n\nb = B()\nprint(b.v)\n',
     'class B:\n    def __init__(self):\n        self.v = 5\n', 'assert B().v == 5\n'),
]


def essayer_corrections_partielles(noter):
    spec = importlib.util.spec_from_file_location('verifier_td', os.path.join(ICI, 'verifier-td.py'))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    cas = json.load(open(os.path.join(ICI, 'essais', 'corrections-partielles.json'), encoding='utf-8'))
    cas = [(f"{c['page']} {c['question']}", c['depart'], c['correction'], c['tests'], c['fichier'], c['preambule']) for c in cas]
    cas += [(n, d, c, t, 'mon_code.py', '') for n, d, c, t in CAS_ECRITS]
    for nom, dep, corr, tests, fichier, pre in cas:
        rc, out, err = v.lancer(v.sur_depart(dep, corr), fichier, pre=pre, tests=tests)
        rc0, _, _ = v.lancer(dep, fichier, pre=pre, tests=tests)
        noter(rc == 0 and rc0 != 0, f'correction partielle posée sur le départ : {nom}'
              + ('' if rc == 0 else ' : ' + err.strip().splitlines()[-1][:120] if err.strip() else '')
              + ('' if rc0 != 0 else ' (le départ seul passe déjà : essai sans valeur)'))


def main():
    serveur = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Silencieux, directory=RACINE))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{serveur.server_address[1]}/'
    pdf = os.path.join(RACINE, 'charte', '.essai-outils.pdf')
    resultats = []

    def noter(ok, msg):
        resultats.append(ok)
        print(('OK    ' if ok else 'ÉCHEC ') + msg)

    rc, out = lancer('charte/imprimer-td.py', base + PAGES[0], pdf)
    noter(rc == 0 and 'PDF vierge : oui' in out, 'gabarit : PDF vierge')
    for page in PAGES:
        if not os.path.exists(os.path.join(RACINE, page)):
            continue
        source = open(os.path.join(RACINE, page), encoding='utf-8').read()
        for nom, (sel, mot) in FUITES.items():
            temoin = os.path.join(os.path.dirname(os.path.join(RACINE, page)), '.temoin-fuite.html')
            regle = '<style>@media print { ' + sel + ' { display: block !important; } }</style>'
            open(temoin, 'w', encoding='utf-8').write(source.replace('</head>', regle + '</head>', 1))
            try:
                rc, out = lancer('charte/imprimer-td.py', base + os.path.relpath(temoin, RACINE).replace(os.sep, '/'), pdf)
            finally:
                os.remove(temoin)
            vu = rc != 0 and 'PDF vierge : NON' in out and ('imprimé(s)' in out or 'texte caché imprimé' in out)
            ligne = next((l.strip() for l in out.splitlines() if 'imprimé(s)' in l or 'caché imprimé' in l), '')
            noter(vu, f'{page} : {nom} imprimés : fuite vue ({ligne[:110]})')
    rc, out = lancer('charte/verifier-td.py', 'charte/gabarit-td/index.html')
    noter(rc == 0 and 'tout est juste' in out, 'gabarit : verifier-td.py, tout est juste')
    essayer_corrections_partielles(noter)
    rc, out = lancer('charte/numeroter-feuilles.py', '--tout', '--verifier')
    noter('Problème' not in out and 'Traceback' not in out, 'numeroter-feuilles.py --tout --verifier : tout le dépôt, sans problème (' + out.strip().splitlines()[-1] + ')')
    if os.path.exists(pdf):
        os.remove(pdf)
    serveur.shutdown()
    print(f'{sum(resultats)} / {len(resultats)} essais conformes')
    sys.exit(0 if all(resultats) else 1)


if __name__ == '__main__':
    main()
