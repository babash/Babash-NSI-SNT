#!/usr/bin/env python3
"""Commandes et système Linux (fiche et exercices) : les réponses, obtenues par exécution.

Usage : python3 -I verifier.py   (bash, coreutils)
Dans un dossier jetable (supprimé à la fin), on recrée /home/nsi/{TP1,Projets,Images}, puis on lance
chaque commande de la correction (et chaque variante acceptée par la page) depuis le dossier de la
consigne, et on regarde le résultat. Puis : les droits (chmod 777, o+x, 640) lus avec ls -l.
"""
import os
import re
import subprocess
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
PAGE2 = os.path.join(ICI, '..', '..', 'commandes-terminale-2.html')


def sh(cmd, cwd):
    r = subprocess.run(['bash', '-c', cmd], cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def reponses(qid):
    t = open(PAGE2, encoding='utf-8').read()
    m = re.search(r'id="%s" data-comparer="exact" data-etiquette="\$" data-reponse="([^"]*)"' % qid, t)
    return m.group(1).split('|')


with tempfile.TemporaryDirectory() as racine:
    def arbre():
        sh('rm -rf home && mkdir -p home/nsi/TP1 home/nsi/Projets home/nsi/Images && touch home/nsi/Projets/web.html '
           '&& touch home/nsi/Images/plage.png', racine)

    def R(chemin):
        return os.path.join(racine, chemin.lstrip('/'))

    def absolu(cmd):   # les chemins absolus de la feuille, ramenés dans le dossier jetable
        return re.sub(r'(?<=\s)/home', R('/home'), cmd)

    CAS = {   # question : (dossier de départ, commande de contrôle après la réponse)
        'q1': ('/home/nsi/TP1', 'pwd'),
        'q2': ('/home/nsi/Projets', 'pwd'),
        'q3': ('/home/nsi/TP1', None),
        'q4': ('/home/nsi/Projets', 'ls ../TP1'),
        'q5': ('/home/nsi', 'ls -d TP1/Archives'),
    }
    for q, (depart, controle) in CAS.items():
        for cmd in reponses(q):
            arbre()
            rc, out = sh(absolu(cmd) + ((' && ' + controle) if controle else ''), R(depart))
            out = out.replace(racine, '')
            print(q, repr(cmd), '->', 'code', rc, '|', out.replace('\n', ' '))
            assert rc == 0, (q, cmd)
    arbre()
    f = R('/home/nsi/TP1/script.sh')
    sh('touch script.sh && chmod 764 script.sh', R('/home/nsi/TP1'))
    print('q11 départ :', sh('ls -l script.sh', R('/home/nsi/TP1'))[1].split()[0], '(groupe : rw-)')
    sh('chmod 777 script.sh', R('/home/nsi/TP1'))
    print('q12 chmod 777 ->', sh('ls -l script.sh', R('/home/nsi/TP1'))[1].split()[0])
    sh('chmod 764 script.sh && chmod o+x script.sh', R('/home/nsi/TP1'))
    print('q13 chmod o+x ->', sh('ls -l script.sh', R('/home/nsi/TP1'))[1].split()[0])
    sh('touch secret.txt && chmod 640 secret.txt', R('/home/nsi/TP1'))
    print('q14 chmod 640 ->', sh('ls -l secret.txt', R('/home/nsi/TP1'))[1].split()[0])
    sh('touch a.tmp b.tmp garde.txt && mkdir -p sous && touch sous/c.tmp && rm *.tmp', R('/home/nsi'))
    print('q15 après rm *.tmp :', sh('ls -R', R('/home/nsi'))[1].replace(racine, '').replace('\n', ' '))
    open(R('/home/nsi/notes.txt'), 'w').write('Maths 14\nNSI 17\nAnglais 12\nProjet NSI 18\n')
    print('q16 cat notes.txt | grep "NSI" :', sh('cat notes.txt | grep "NSI"', R('/home/nsi'))[1].replace('\n', ' / '))
print('tout est juste')
