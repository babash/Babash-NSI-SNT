#!/usr/bin/env python3
"""TD type bac « OS, fichiers et processus » : les réponses de la page, obtenues par exécution.

Usage : python3 -I verifier.py   (Python 3.13, bash, coreutils, procps)
Tout se passe dans un dossier jetable (supprimé à la fin) : on y recrée l'arborescence de la
feuille, puis on lance les commandes de la correction et on lit ce qu'elles affichent.
Puis : la question « ps -ef | grep » sur un vrai processus, et les tests de la fonction Python.
"""
import contextlib
import html
import io
import os
import re
import subprocess
import tempfile

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
TEXTE = open(PAGE, encoding='utf-8').read() if os.path.exists(PAGE) else ''


def sh(cmd, cwd):
    r = subprocess.run(['bash', '-c', cmd], cwd=cwd, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


with tempfile.TemporaryDirectory() as racine:
    def arbre():
        sh('rm -rf bin home && mkdir -p bin home/prof/examens home/eleve/devoirs/nsi home/eleve/projets'
           ' && echo "nom;note" > home/prof/notes.csv', racine)
    R = lambda chemin: os.path.join(racine, chemin.lstrip('/'))
    nsi = R('/home/eleve/devoirs/nsi')

    arbre()
    print('q1 chemin absolu de nsi :', '/' + os.path.relpath(nsi, racine))
    for cmd in ('cp ../../../prof/notes.csv ../../projets', 'cp ../../../prof/notes.csv ../../projets/'):
        arbre()
        sh(cmd, nsi)
        print('q2', cmd, '->', sh('ls', R('/home/eleve/projets')))
    for cmd in ('touch ../../../prof/examens/exam1.txt', 'cd ../../../prof/examens && touch exam1.txt',
                'cd ../../../prof/examens; touch exam1.txt'):
        arbre()
        sh(cmd, nsi)
        print('q3', cmd, '->', sh('ls', R('/home/prof/examens')))
    arbre()
    print('q4 ls ../.. depuis ~/devoirs/nsi ->', sh('ls ../..', nsi).split())
    arbre()
    print('q5 ->', sh('mkdir archives && cd devoirs && mv nsi ../archives/ && ls ../archives', R('/home/eleve')))
    arbre()
    f = R('/home/prof/notes.csv')
    sh('chmod 764 notes.csv', R('/home/prof'))
    print('q6 droits de départ :', sh('ls -l notes.csv', R('/home/prof')).split()[0], '(autres : r--)')
    sh('chmod 666 notes.csv', R('/home/prof'))
    print('q7 chmod 666 ->', sh('ls -l notes.csv', R('/home/prof')).split()[0])

    # ps -ef | grep "python3" : un vrai processus python3 calcul_pi.py, puis la commande de la feuille
    open(os.path.join(racine, 'calcul_pi.py'), 'w').write('import time\ntime.sleep(5)\n')
    sortie = sh('python3 calcul_pi.py & sleep 0.5; ps -ef | grep "python3"; wait', racine)
    # la machine de vérification a d'autres processus python3 : on ne montre que ceux de l'essai
    sortie = '\n'.join(l for l in sortie.splitlines() if re.search(r'\d\d:\d\d:\d\d (python3 calcul_pi\.py|grep python3)$', l.rstrip()))
    print('q13 ps -ef | grep "python3" (lignes de l\'essai) :')
    for ligne in sortie.splitlines():
        print('    ', re.sub(r'\s+', ' ', ligne))
    assert any('python3 calcul_pi.py' in l for l in sortie.splitlines())
    assert any('grep python3' in l for l in sortie.splitlines()), 'la ligne de grep lui-même'

# processus : PPID de python3 et nouveau parent après la mort de bash
ps = {1: 0, 500: 1, 1050: 500, 1210: 1050, 1215: 1050}
print('q9 et q11 PPID de 1210 :', ps[1210], '; enfants de 1050 :', [p for p, pp in ps.items() if pp == 1050])

# Python
processus_actifs = [
    {"pid": 1210, "nom": "python3", "cpu": 99.8, "user": "eleve"},
    {"pid": 1340, "nom": "firefox", "cpu": 12.5, "user": "eleve"},
    {"pid": 1450, "nom": "bash", "cpu": 0.1, "user": "root"}
]
CORRECTION = '''
def trouver_critiques(liste_proc):
    critiques = []
    for p in liste_proc:
        if p["cpu"] > 80:
            critiques.append(p["pid"])
    return critiques
'''
FAUSSES = {
    'renvoie les dictionnaires': CORRECTION.replace('append(p["pid"])', 'append(p)'),
    'seuil >= 12': CORRECTION.replace('> 80', '> 12'),
    'renvoie dès le premier': CORRECTION.replace('            critiques.append(p["pid"])', '            return [p["pid"]]'),
    'compare le pid': CORRECTION.replace('p["cpu"] > 80', 'p["pid"] > 80'),
}
TESTS = ''
for bloc in TEXTE.split('<section class="td-q"')[1:]:
    m = re.search(r'<script type="text/x-python" class="td-tests">(.*?)</script>', bloc.split('</section>')[0], re.S)
    if m:
        TESTS = html.unescape(m.group(1))


def essayer(code):
    g = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, g)
            exec(TESTS, g)
        return 'passe'
    except AssertionError as e:
        return 'refusée : ' + str(e)
    except Exception as e:
        return 'erreur : %r' % e


g = {}
exec(CORRECTION, g)
print('q16 trouver_critiques(processus_actifs) =', g['trouver_critiques'](processus_actifs))
assert essayer(CORRECTION) == 'passe', essayer(CORRECTION)
for nom, code in FAUSSES.items():
    r = essayer(code)
    print('q16 version fausse (%s) :' % nom, r)
    assert r != 'passe', nom


def filtrer_par_user(liste_proc, nom_user):
    resultat = []
    for p in liste_proc:
        if p["user"] == nom_user:
            resultat.append(p)
    return resultat


print('q17 filtrer_par_user(processus_actifs, "root") =', filtrer_par_user(processus_actifs, "root"))
print('tout est juste')
