#!/usr/bin/env python3
"""Commandes Linux (1re NSI) : chaque réponse de la page, vérifiée par exécution réelle.

Usage : python3 -I verifier-commandes.py            (bash)
        BUSYBOX=/chemin/busybox python3 -I verifier-commandes.py   (bash, puis BusyBox ash, le shell de JSLinux)

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
PAGES = [os.path.join(ICI, '..', f) for f in ('commandes-premiere-eleve.html', 'commandes-premiere-eleve-2.html')]
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


# question : (dossier de départ, commande ajoutée après la réponse, contrôle(bac, code, sortie) -> bool)
NSI = '/home/eleve/devoirs/nsi'
CAS = {
    'q16': (NSI, '', lambda b, c, s: c == 0 and existe(b, '/home/eleve/projets/notes.csv') and existe(b, '/home/prof/notes.csv')),
    'q17': (NSI, ' && touch exam1.txt', lambda b, c, s: c == 0 and existe(b, '/home/prof/examens/exam1.txt')),
    'q21': (NSI, '', lambda b, c, s: c == 0 and s.strip() == '\n'.join(l for l in TP1.splitlines() if 'print' in l)),
    'q26': (NSI, '', lambda b, c, s: c == 0 and mode(b, NSI + '/tp1.py') == '600'),
    'q27': (NSI, '', lambda b, c, s: c == 0 and mode(b, NSI + '/tp1.py') == '744'),
    'q29': ('/home/prof', '', lambda b, c, s: c == 0 and os.stat(b.p('/home/prof/notes.csv')).st_uid == 65534),
}
# erreurs prévues que la page dit « justes, mais pas ce qui est demandé » (chemin absolu au lieu de relatif…)
JUSTES_MAIS = {'q16': ['/home'], 'q27': ['chmod +x', 'chmod a+x', 'chmod 700'], 'q29': ['chown direction notes.csv']}


def verifier(shell, nom):
    print('== %s' % nom)
    qs = questions()
    b = Bac(shell)
    try:
        for q, (depart, suite, ok) in CAS.items():
            bonnes, fausses, md = qs[q]
            assert md == 'exact', q
            for cmd in bonnes:
                b.arbre()
                c, s = b.lancer(cmd + suite, depart)
                juste = ok(b, c, s)
                print('  %s accepte  %-48s -> %s' % (q, cmd, 'juste' if juste else 'FAUX (code %d) %s' % (c, s.strip()[:60])))
                if not juste:
                    erreurs.append((nom, q, cmd))
            for cmd in fausses:
                b.arbre()
                c, s = b.lancer(cmd + suite, depart)
                juste = ok(b, c, s)
                voulu = any(cmd.startswith(x) or x in cmd for x in JUSTES_MAIS.get(q, []))
                etat = 'refusée, et fausse' if not juste else ('refusée, juste mais hors consigne (dit par la page)' if voulu else 'REFUSÉE ALORS QU\'ELLE MARCHE')
                print('  %s refuse   %-48s -> %s%s' % (q, cmd, etat, ('  [' + s.strip().splitlines()[0][:70] + ']') if s.strip() and not juste else ''))
                if juste and not voulu:
                    erreurs.append((nom, q, 'refus injuste : ' + cmd))
        # réponses qui ne sont pas des commandes : on les compare à la sortie réelle
        b.arbre()
        c, s = b.lancer('pwd', NSI)
        attendu = qs['q15'][0][0]
        print('  q15 pwd depuis nsi -> %s (page : %s)' % (s.strip(), attendu))
        if s.strip() != attendu: erreurs.append((nom, 'q15', s))
        c, s = b.lancer('ls ../..', NSI)
        mots = ' '.join(s.split())
        print('  q18 ls ../.. -> %s (page : %s)' % (mots, qs['q18'][0][0]))
        if mots != qs['q18'][0][0]: erreurs.append((nom, 'q18', mots))
        b.arbre()
        c, s = b.lancer('mkdir archives && cd devoirs && mv nsi ../archives/ && ls ../archives', '/home/eleve')
        print('  q19 ls ../archives -> %s ; devoirs vide : %s ; tp1.py suit : %s' % (s.strip(), os.listdir(b.p('/home/eleve/devoirs')) == [], existe(b, '/home/eleve/archives/nsi/tp1.py')))
        if s.strip() != qs['q19'][0][0]: erreurs.append((nom, 'q19', s))
        b.arbre()
        c, s = b.lancer('grep barge tp1.py', NSI)
        page = bloc('td-attendu', 'id="q22"').strip()
        print('  q22 grep barge tp1.py -> %s' % ('identique à la page' if s.strip() == page else 'DIFFÉRENT : ' + s))
        if s.strip() != page: erreurs.append((nom, 'q22', s))
        b.lancer('chmod 754 tp1.py', NSI)
        print('  q25 chmod 754 -> %s' % mode(b, NSI + '/tp1.py'))
        if mode(b, NSI + '/tp1.py') != '754': erreurs.append((nom, 'q25', ''))
    finally:
        b.fin()


def lsl_et_chown():
    """ls -l de /home/prof (affiché dans la page) et le refus de chown sans root (question 28)."""
    print('== ls -l et chown (bash, sans root pour chown)')
    r = tempfile.mkdtemp(prefix='td-linux-', dir='/tmp')
    try:
        os.chmod(r, 0o755)
        os.makedirs(os.path.join(r, 'examens'))
        open(os.path.join(r, 'notes.csv'), 'w', encoding='utf-8').write(NOTES)
        os.chmod(os.path.join(r, 'notes.csv'), 0o640)
        os.chmod(os.path.join(r, 'examens'), 0o770)
        subprocess.run(['touch', '-d', '2026-11-25 10:00', 'notes.csv', 'examens'], cwd=r)
        s = subprocess.run(['ls', '-l'], cwd=r, capture_output=True, text=True, env=dict(os.environ, LC_ALL='C.UTF-8')).stdout
        # le propriétaire et le groupe de la page (prof, nsi) n'existent pas ici : on les remplace
        s = re.sub(r' 1 \S+ \S+ ', ' 1 prof nsi ', re.sub(r' 2 \S+ \S+ ', ' 2 prof nsi ', s))
        page = bloc('td-sortie-exemple', 'id="q23"').split('\n', 1)[1].strip()
        lignes = [' '.join(l.split()) for l in s.strip().splitlines()]
        print('  ls -l :', 'identique à la page (espaces près)' if lignes == [' '.join(l.split()) for l in page.splitlines()] else 'DIFFÉRENT :\n' + s)
        if lignes != [' '.join(l.split()) for l in page.splitlines()]: erreurs.append(('ls -l', '', s))
        os.chown(os.path.join(r, 'notes.csv'), 65534, 65534)
        if shutil.which('setpriv'):
            c = subprocess.run(['setpriv', '--reuid=65534', '--regid=65534', '--clear-groups', 'chown', 'root', 'notes.csv'],
                               cwd=r, capture_output=True, text=True, env=dict(os.environ, LC_ALL='C.UTF-8'))
            msg = c.stderr.strip()
            print('  chown sans root :', msg)
            if msg != "chown: changing ownership of 'notes.csv': Operation not permitted":
                erreurs.append(('chown', '', msg))
            elif msg not in html.unescape(TEXTE):
                erreurs.append(('chown', 'message absent de la page', msg))
    finally:
        shutil.rmtree(r)


def exemples(shell, nom):
    """Les exemples résolus des deux feuilles, rejoués."""
    print('== exemples résolus (%s)' % nom)
    b = Bac(shell)
    try:
        def cas(titre, cmd, depart, ok):
            b.arbre()
            c, s = b.lancer(cmd, depart)
            juste = ok(c, s)
            print('  %-45s -> %s' % (titre, 'juste' if juste else 'FAUX : %s' % s))
            if not juste: erreurs.append((nom, 'exemple', titre, s))
        cas('pwd depuis nsi', 'pwd', NSI, lambda c, s: s.strip() == '/home/eleve/devoirs/nsi')
        cas('pwd depuis photos (invite ~/photos)', 'pwd', '/home/eleve/photos', lambda c, s: s.strip() == '/home/eleve/photos')
        cas('cp site.html ../photos/ (depuis projets)', 'cp site.html ../photos/', '/home/eleve/projets',
            lambda c, s: c == 0 and existe(b, '/home/eleve/photos/site.html') and existe(b, '/home/eleve/projets/site.html'))
        cas('cd ../../photos ; touch liste.txt (nsi)', 'cd ../../photos && touch liste.txt', NSI, lambda c, s: existe(b, '/home/eleve/photos/liste.txt'))
        cas('ls ../photos (depuis projets)', 'ls ../photos', '/home/eleve/projets', lambda c, s: s.strip() == 'lagon.png')
        cas('mv projets/site.html photos/ (eleve)', 'mv projets/site.html photos/ && ls projets | wc -l && ls photos', '/home/eleve',
            lambda c, s: s.split() == ['0', 'lagon.png', 'site.html'])
        cas('grep depart tp1.py', 'grep depart tp1.py', NSI, lambda c, s: s.strip() == bloc('td-sortie-exemple', 'grep depart tp1.py</code> affiche').split('\n', 1)[1].strip())
        cas('chmod 750 -> rwxr-x---', 'chmod 750 tp1.py && stat -c %A tp1.py', NSI, lambda c, s: s.strip() == '-rwxr-x---')
        cas('chmod 640 -> rw-r-----', 'chmod 640 tp1.py && stat -c %A tp1.py', NSI, lambda c, s: s.strip() == '-rw-r-----')
        cas('chmod g+w notes.csv', 'chmod g+w notes.csv && stat -c %A notes.csv', '/home/prof', lambda c, s: s.strip() == '-rw-rw----')
        cas('sudo chown prof tp1.py (prof -> nobody)', 'chown nobody tp1.py', NSI, lambda c, s: os.stat(b.p(NSI + '/tp1.py')).st_uid == 65534)
    finally:
        b.fin()


verifier(['bash'], 'bash')
exemples(['bash'], 'bash')
if os.environ.get('BUSYBOX'):
    verifier([os.environ['BUSYBOX'], 'sh'], 'BusyBox ash')
    exemples([os.environ['BUSYBOX'], 'sh'], 'BusyBox ash')
lsl_et_chown()
if erreurs:
    print('\nÀ REVOIR :')
    for e in erreurs:
        print('  ', e)
    sys.exit(1)
print('\ntout est juste')
