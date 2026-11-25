#!/usr/bin/env python3
"""Commandes Linux (Tle NSI) : chaque réponse des deux feuilles, vérifiée par exécution réelle.

Usage : python3 -I verifier.py            (bash)
        BUSYBOX=/chemin/busybox python3 -I verifier.py   (bash, puis BusyBox ash, le shell de JSLinux)

Pour chaque question où l'élève écrit une commande (data-comparer="exact"), le script lit dans la page
TOUTES les réponses acceptées (data-reponse) et toutes les erreurs prévues (data-si). Dans un dossier
jetable (supprimé à la fin), il recrée l'arborescence du TD, se place dans le dossier de la consigne,
lance la commande et regarde le résultat sur le disque :
- chaque réponse acceptée doit réussir et faire ce que demande la consigne ;
- chaque erreur prévue doit échouer, ou faire autre chose (le script dit quoi), sauf celles que la page
  présente elle-même comme « juste, mais pas ce qui est demandé » (chemin absolu au lieu de relatif…).
Les chemins absolus de la page (/home/…) sont ramenés dans le dossier jetable, et ~ y désigne /home/eleve.
`sudo` est retiré (le script tourne en root) et l'utilisateur·rice `direction`, qui n'existe pas ici, est
remplacé·e par `nobody`. Les sorties attendues (ls, grep, ls -l) sont comparées à celles de la page, et chaque exemple résolu est rejoué.
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
PAGES = [os.path.join(ICI, '..', '..', f) for f in ('commandes-terminale.html', 'commandes-terminale-2.html')]
TEXTE = '\n'.join(open(p, encoding='utf-8').read() for p in PAGES)

TP1 = ('# TP 1 : les horaires de la barge\ndepart = 6\nprint("Première barge à", depart, "h")\n'
       'arrivee = depart + 1\nprint("Arrivée à Mamoudzou à", arrivee, "h")\n')
NOTES = 'prenom;note\nInaya;15\nMehdi;12\nLéa;17\n'

erreurs = []


def questions():
    """{id: (réponses acceptées, erreurs prévues, mode)} lus dans la page."""
    out = {}
    for m in re.finditer(r'<section class="td-q"([^>]*)>(.*?)</section>', TEXTE, re.S):
        attrs, corps = m.group(1), m.group(2)
        qid = re.search(r'id="([^"]+)"', attrs).group(1)
        rep = re.search(r'data-reponse="([^"]*)"', attrs)
        if not rep:
            continue
        mode = (re.search(r'data-comparer="([^"]*)"', attrs) or [None, 'texte'])[1]
        si = [html.unescape(x) for s in re.findall(r'data-si="([^"]*)"', corps) for x in s.split('|')]
        out[qid] = ([html.unescape(x) for x in rep.group(1).split('|')], si, mode)
    return out


def bloc(classe, apres):
    """Le texte du premier <pre class="classe"> qui suit le repère `apres`."""
    i = TEXTE.index(apres)
    m = re.search(r'<pre class="%s"[^>]*>\n?(.*?)</pre>' % classe, TEXTE[i:], re.S)
    return html.unescape(m.group(1))


class Bac:
    """Un dossier jetable qui joue le rôle de la racine / de l'énoncé."""

    def __init__(self, shell):
        self.shell = shell
        self.r = tempfile.mkdtemp(prefix='td-linux-')
        os.chmod(self.r, 0o755)

    def arbre(self):
        for x in os.listdir(self.r):
            shutil.rmtree(os.path.join(self.r, x))
        for d in ['bin', 'tmp', 'home/eleve/devoirs/nsi', 'home/eleve/photos', 'home/eleve/projets', 'home/prof/examens']:
            os.makedirs(os.path.join(self.r, d))
        for f, c in [('home/eleve/devoirs/nsi/tp1.py', TP1), ('home/eleve/photos/lagon.png', ''),
                     ('home/eleve/projets/site.html', ''), ('home/prof/notes.csv', NOTES)]:
            open(os.path.join(self.r, f), 'w', encoding='utf-8').write(c)
        os.chmod(self.p('/home/prof/notes.csv'), 0o640)
        os.chmod(self.p('/home/prof/examens'), 0o770)
        os.chmod(self.p('/home/eleve/devoirs/nsi/tp1.py'), 0o644)

    def p(self, chemin):
        return os.path.join(self.r, chemin.lstrip('/'))

    def lancer(self, cmd, depart):
        cmd = re.sub(r'^sudo ', '', cmd).replace('chown direction', 'chown nobody')
        cmd = re.sub(r'(?<=\s)/home', self.p('/home'), cmd)
        env = dict(os.environ, HOME=self.p('/home/eleve'), LC_ALL='C.UTF-8')
        r = subprocess.run(self.shell + ['-c', cmd], cwd=self.p(depart), capture_output=True, text=True, env=env)
        return r.returncode, (r.stdout + r.stderr).replace(self.r, '')

    def fin(self):
        shutil.rmtree(self.r)


def existe(b, c):
    return os.path.exists(b.p(c))


def mode(b, c):
    return oct(os.stat(b.p(c)).st_mode & 0o777)[2:]


# question : (dossier de départ, préfixe, suite, contrôle(bac, code, sortie) -> bool)
NSI = '/home/eleve/devoirs/nsi'
E = '/home/eleve'
CAS = {
    'r1': (E + '/devoirs', '', ' && pwd', lambda b, c, s: c == 0 and s.strip() == b.p(E + '/projets').replace(b.r, '') or s.strip().endswith('/home/eleve/projets')),
    'r2': (E + '/projets', '', ' && pwd', lambda b, c, s: c == 0 and s.strip().endswith('/home/eleve') ),
    'r3': (E + '/devoirs', '', '', lambda b, c, s: c == 0 and s.strip() == 'lagon.png'),
    'r4': (E + '/projets', '', '', lambda b, c, s: c == 0 and existe(b, E + '/devoirs/site.html') and existe(b, E + '/projets/site.html')),
    'r5': (E, '', '', lambda b, c, s: c == 0 and os.path.isdir(b.p(E + '/devoirs/archives'))),
    'r11': (NSI, '', '', lambda b, c, s: c == 0 and mode(b, NSI + '/tp1.py') == '777'),
    'r12': (NSI, 'chmod 764 tp1.py && ', '', lambda b, c, s: c == 0 and mode(b, NSI + '/tp1.py') == '765'),
    'j3': (E, 'ps -ef | ', '', lambda b, c, s: c == 0 and 'marees' in s),
}
JUSTES_MAIS = {'r1': ['/home', '~'], 'r2': ['cd ..', 'cd ~', 'cd'], 'r3': [], 'r11': ['a+rwx', 'ugo+rwx'], 'r7': ['rm -r']}


def verifier(shell, nom):
    print('== %s' % nom)
    qs = questions()
    b = Bac(shell)
    calcul = None
    try:
        for q, (depart, avant, suite, ok) in CAS.items():
            bonnes, fausses, md = qs[q]
            assert md == 'exact', q
            for genre, liste in (('accepte', bonnes), ('refuse', fausses)):
                for cmd in liste:
                    b.arbre()
                    if q == 'j3':   # un vrai calcul « python3 marees.py » en arrière-plan
                        open(b.p(E + '/marees.py'), 'w').write('import time\ntime.sleep(30)\n')
                        calcul = subprocess.Popen(['python3', 'marees.py'], cwd=b.p(E))
                    c, s = b.lancer(avant + cmd + suite, depart)
                    if calcul: calcul.kill(); calcul.wait(); calcul = None
                    juste = ok(b, c, s)
                    if genre == 'accepte':
                        print('  %s accepte  %-40s -> %s' % (q, cmd, 'juste' if juste else 'FAUX (code %d) %s' % (c, s.strip()[:60])))
                        if not juste: erreurs.append((nom, q, cmd))
                    else:
                        voulu = any(cmd == x or cmd.startswith(x + ' ') or x in cmd for x in JUSTES_MAIS.get(q, []) if x)
                        etat = 'refusée, et fausse' if not juste else ('refusée, juste mais hors consigne (dit par la page)' if voulu else "REFUSÉE ALORS QU'ELLE MARCHE")
                        print('  %s refuse   %-40s -> %s' % (q, cmd, etat))
                        if juste and not voulu: erreurs.append((nom, q, 'refus injuste : ' + cmd))
        # les commandes à nommer (rappels) : elles existent, et font ce qu'on dit
        b.arbre()
        for q, essai, attendu in [('r6', 'cat tp1.py | head -1', '# TP 1 : les horaires de la barge'), ('r8', 'grep barge tp1.py | wc -l', '2')]:
            c, s = b.lancer(essai, NSI)
            print('  %s %s -> %s' % (q, essai, s.strip()))
            if s.strip() != attendu: erreurs.append((nom, q, s))
        b.lancer('mkdir vide', NSI)
        c, s = b.lancer('rmdir vide && rmdir ../nsi', NSI)
        print('  r7 rmdir : dossier vide supprimé, dossier plein refusé ->', s.strip()[:70])
        # droits : ls -l de la page
        b.lancer('chmod 764 tp1.py', NSI)
        print('  r10 ls -l tp1.py ->', b.lancer('stat -c %A tp1.py', NSI)[1].strip(), '(page : -rwxrw-r--)')
        if b.lancer('stat -c %A tp1.py', NSI)[1].strip() != '-rwxrw-r--': erreurs.append((nom, 'r10', ''))
        print('  taille de tp1.py :', os.path.getsize(b.p(NSI + '/tp1.py')), '(page : 155)')
        if os.path.getsize(b.p(NSI + '/tp1.py')) != 155: erreurs.append((nom, 'taille', ''))
        # exemples résolus
        for titre, cmd, depart, ok in [
                ('cd ../../photos (nsi)', 'cd ../../photos && pwd', NSI, lambda c, s: s.strip().endswith('/home/eleve/photos')),
                ('cd /home/eleve/projets', 'cd /home/eleve/projets && pwd', E + '/photos', lambda c, s: s.strip().endswith('/home/eleve/projets')),
                ('ls ../devoirs/nsi (projets)', 'ls ../devoirs/nsi', E + '/projets', lambda c, s: s.strip() == 'tp1.py'),
                ('cp tp1.py ../../projets/', 'cp tp1.py ../../projets/ && ls ../../projets', NSI, lambda c, s: 'tp1.py' in s.split()),
                ('mkdir photos/brouillons', 'mkdir photos/brouillons && ls photos', E, lambda c, s: 'brouillons' in s.split()),
                ('chmod 755 -> rwxr-xr-x', 'chmod 755 tp1.py && stat -c %A tp1.py', NSI, lambda c, s: s.strip() == '-rwxr-xr-x'),
                ('chmod g-w', 'chmod 664 tp1.py && chmod g-w tp1.py && stat -c %A tp1.py', NSI, lambda c, s: s.strip() == '-rw-r--r--'),
                ('find ~ -name "*.py"', 'find ~ -name "*.py"', E, lambda c, s: s.strip().endswith('/home/eleve/devoirs/nsi/tp1.py')),
                ('ls *.py (nsi)', 'ls *.py', NSI, lambda c, s: s.strip() == 'tp1.py'),
                ('cat tp1.py | grep barge', 'cat tp1.py | grep barge', NSI, lambda c, s: s.strip().splitlines() == [l for l in TP1.splitlines() if 'barge' in l]),
                ('rm *.tmp : ici seulement', 'touch a.tmp b.tmp garde.txt && mkdir sous && touch sous/c.tmp && rm *.tmp && ls -R', NSI,
                 lambda c, s: 'a.tmp' not in s and 'c.tmp' in s and 'garde.txt' in s)]:
            b.arbre()
            c, s = b.lancer(cmd, depart)
            juste = ok(c, s)
            print('  exemple %-32s -> %s' % (titre, 'juste' if juste else 'FAUX : ' + s))
            if not juste: erreurs.append((nom, 'exemple', titre, s))
    finally:
        b.fin()


def processus():
    """kill : un vrai calcul en arrière-plan, arrêté par chaque réponse acceptée (le PID 450 de la page
    est remplacé par le vrai) ; et l'en-tête de ps -eo de la page, comparé au vrai."""
    print('== processus (bash)')
    qs = questions()
    bonnes, fausses, _ = qs['p7']
    for cmd in bonnes + fausses:
        p = subprocess.Popen(['python3', '-c', 'import time; time.sleep(30)'])
        vrai = cmd.replace('450', str(p.pid)).replace('sudo ', '').replace('120', '999999')
        r = subprocess.run(['bash', '-c', vrai], capture_output=True, text=True)
        try:
            p.wait(timeout=2); arrete = True
        except subprocess.TimeoutExpired:
            arrete = False
        signal = -p.returncode if arrete and p.returncode is not None and p.returncode < 0 else None
        p.kill(); p.wait()
        force = arrete and signal == 9
        print('  p7 %-8s %-22s -> %s' % ('accepte' if cmd in bonnes else 'refuse', cmd,
              'arrêté par le signal %s' % signal if arrete else 'pas arrêté (%s)' % (r.stderr.strip()[:60] or 'aucun message')))
        if cmd in bonnes and not force: erreurs.append(('p7', cmd))
        if cmd in fausses and force: erreurs.append(('p7 refus injuste', cmd))
    entete = subprocess.run(['ps', '-eo', 'pid,ppid,user,%cpu,%mem,args'], capture_output=True, text=True).stdout.splitlines()[0]
    page = [l for l in bloc('td-sortie-exemple', 'lance un calcul des marées').splitlines() if 'PPID' in l][0]
    print('  en-tête de ps -eo :', ' '.join(entete.split()) == ' '.join(page.split()), '|', entete.strip())
    if ' '.join(entete.split()) != ' '.join(page.split()): erreurs.append(('ps', entete))


verifier(['bash'], 'bash')
if os.environ.get('BUSYBOX'):
    verifier([os.environ['BUSYBOX'], 'sh'], 'BusyBox ash')
processus()
if erreurs:
    print('\nÀ REVOIR :')
    for e in erreurs:
        print('  ', e)
    sys.exit(1)
print('\ntout est juste')
