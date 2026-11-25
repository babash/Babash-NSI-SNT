#!/usr/bin/env python3
"""Commandes Linux (1re et Tle NSI) : chaque réponse des quatre feuilles, vérifiée par exécution réelle.
Le même script est copié dans les deux dossiers (première et terminale) : il lit les quatre feuilles.

Usage (depuis la racine du dépôt, ou d'ailleurs) :
    python3 -I verifier-commandes.py                              (bash)
    BUSYBOX=/chemin/busybox python3 -I verifier-commandes.py      (bash, puis BusyBox ash, le shell de JSLinux)

Pour chaque question où l'élève écrit une commande, le script lit dans la page TOUTES les réponses acceptées
(data-reponse) et toutes les erreurs prévues (data-si des td-retour). Dans un dossier jetable, il recrée
l'arborescence du TD, se place dans le dossier de la consigne, lance la commande et regarde le résultat sur le
disque : chaque réponse acceptée doit faire ce que demande la consigne ; chaque erreur prévue doit échouer ou
faire autre chose, sauf celles que la page dit « justes, mais pas ce qui est demandé » (chemin absolu au lieu
de relatif…). Les chemins /home/… sont ramenés dans le dossier jetable ; ~ y désigne /home/eleve ; `sudo` est
retiré (le script tourne en root) ; l'utilisateur·rice `direction` devient `nobody`. Sont aussi rejoués : les
exemples résolus, les sorties affichées (cat, grep, ls -l, le refus de chown et de rmdir), `kill` sur un vrai
processus, `ps -ef | grep` sur un vrai calcul, l'en-tête de `ps -ef`, et les réponses de l'arbre des processus.
"""
import html
import itertools
import os
import re
import shutil
import subprocess
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = ICI
while not os.path.isdir(os.path.join(RACINE, 'nsi-premiere')):
    RACINE = os.path.dirname(RACINE)
PAGES = {n: os.path.join(RACINE, p) for n, p in [
    ('1re-1', 'nsi-premiere/fichiers/commandes-linux-premiere/commandes-premiere-eleve.html'),
    ('1re-2', 'nsi-premiere/fichiers/commandes-linux-premiere/commandes-premiere-eleve-2.html'),
    ('tle-1', 'nsi-terminale/fichiers/architecture-os/commandes-terminale.html'),
    ('tle-2', 'nsi-terminale/fichiers/architecture-os/commandes-terminale-2.html')]}
TEXTES = {n: open(p, encoding='utf-8').read() for n, p in PAGES.items()}
TOUT = '\n'.join(TEXTES.values())


def net(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


def sortie_apres(page, repere):
    """Le texte de la sortie de terminal qui contient `repere`, ou de la première qui le suit."""
    t = TEXTES[page]
    i = t.index(repere)
    j = t.rfind('<pre class="td-sortie-exemple">', 0, i)
    if j >= 0 and t.find('</pre>', j) > i:      # le repère est dans la sortie elle-même
        i = j
    m = re.search(r'<pre class="td-sortie-exemple">\n?(.*?)</pre>', t[i:], re.S)
    return html.unescape(m.group(1))


# le fichier tp1.py et notes.csv : lus dans la page (sortie de cat), pas recopiés ici
TP1 = '\n'.join(sortie_apres('1re-2', 'affiché par').split('\n')[1:]) + '\n'
NOTES = 'prenom;note\nInaya;15\nMehdi;12\nLéa;17\n'
erreurs = []


def questions():
    """{(page, id): (réponses acceptées, erreurs prévues, mode)}."""
    out = {}
    for page, t in TEXTES.items():
        for m in re.finditer(r'<section class="td-q"([^>]*)>(.*?)</section>', t, re.S):
            attrs, corps = m.group(1), m.group(2)
            qid = re.search(r'id="([^"]+)"', attrs).group(1)
            rep = re.search(r'data-reponse="([^"]*)"', attrs)
            if not rep:
                continue
            mode = (re.search(r'data-comparer="([^"]*)"', attrs) or [None, 'texte'])[1]
            si = [html.unescape(x) for s in re.findall(r'data-si="([^"]*)"', corps) for x in s.split('|')]
            out[(page, qid)] = ([html.unescape(x) for x in rep.group(1).split('|')], si, mode)
    return out


class Bac:
    """Un dossier jetable qui joue le rôle de la racine / de l'énoncé."""

    def __init__(self, shell):
        self.shell = shell
        self.r = tempfile.mkdtemp(prefix='td-linux-', dir='/tmp')
        os.chmod(self.r, 0o755)

    def arbre(self):
        for x in os.listdir(self.r):
            shutil.rmtree(os.path.join(self.r, x))
        for d in ['bin', 'tmp', 'home/eleve/devoirs/nsi', 'home/eleve/projets', 'home/prof/examens']:
            os.makedirs(os.path.join(self.r, d))
        for f, c in [('home/eleve/devoirs/nsi/tp1.py', TP1), ('home/prof/notes.csv', NOTES)]:
            open(os.path.join(self.r, f), 'w', encoding='utf-8').write(c)
        os.chmod(self.p('/home/prof/notes.csv'), 0o640)
        os.chmod(self.p('/home/prof/examens'), 0o770)
        os.chmod(self.p('/home/eleve/devoirs/nsi/tp1.py'), 0o644)

    def p(self, chemin):
        return os.path.join(self.r, chemin.lstrip('/'))

    def lancer(self, cmd, depart):
        cmd = re.sub(r'(^|; |&& )sudo ', r'\1', cmd)
        cmd = cmd.replace('direction:info', 'nobody:nogroup').replace('chown direction', 'chown nobody')
        cmd = re.sub(r'(?<=[\s:])/(?=home|prof|nsi|devoirs|archives|projets|examens)', self.r + '/', cmd)
        env = dict(os.environ, HOME=self.p('/home/eleve'), LC_ALL='C.UTF-8')
        r = subprocess.run(self.shell + ['-c', cmd], cwd=self.p(depart), capture_output=True, text=True, env=env)
        return r.returncode, (r.stdout + r.stderr).replace(self.r, '')

    def fin(self):
        shutil.rmtree(self.r)


def existe(b, c):
    return os.path.exists(b.p(c))


def mode(b, c):
    return oct(os.stat(b.p(c)).st_mode & 0o777)[2:]


def noms(s):
    """Une liste de noms écrite par l'élève (ou affichée par ls) : l'ensemble des noms, sans / final."""
    mots = re.split(r'[\s,;]+|\bet\b|\s-\s', s.strip().rstrip('.'))
    return sorted(m.rstrip('/') for m in mots if m and m not in ('-', 'le', 'dossier', 'répertoire', 'un', 'Le'))


NSI, E, PROF = '/home/eleve/devoirs/nsi', '/home/eleve', '/home/prof'
PRINTS = '\n'.join(l for l in TP1.splitlines() if 'print' in l)
REORG = 'mkdir archives && mkdir -p archives && mv devoirs/nsi archives/ && '
# (page, question) : (dossier de départ, avant, après, contrôle(bac, code, sortie, réponse) -> bool)
CAS = {
    ('1re-1', 'p-abs'): ('/', 'cd ', ' && pwd', lambda b, c, s, r: c == 0 and s.strip() == NSI),
    ('1re-1', 'p-cp'): (NSI, '', '', lambda b, c, s, r: c == 0 and existe(b, E + '/projets/notes.csv') and existe(b, PROF + '/notes.csv')),
    ('tle-1', 't-cp'): (NSI, '', '', lambda b, c, s, r: c == 0 and existe(b, E + '/projets/notes.csv') and existe(b, PROF + '/notes.csv')),
    ('1re-1', 'p-cd'): (NSI, '', ' && touch exam1.txt', lambda b, c, s, r: c == 0 and existe(b, PROF + '/examens/exam1.txt')),
    ('1re-1', 'p-lshaut'): (NSI, 'ls ../.. #', '', lambda b, c, s, r: noms(s) == noms(r)),
    ('1re-1', 'p-archives'): (E, 'mkdir archives && cd devoirs && mv nsi ../archives/ && ls ../archives #', '',
                              lambda b, c, s, r: noms(s) == noms(r)),
    ('tle-1', 't-archives'): (E, 'mkdir archives && cd devoirs && mv nsi ../archives/ && ls ../archives #', '',
                              lambda b, c, s, r: noms(s) == noms(r)),
    ('1re-2', 'g-print'): (NSI, '', '', lambda b, c, s, r: c == 0 and s.strip() == PRINTS),
    ('1re-2', 'd-octal'): (NSI, '', '', lambda b, c, s, r: c == 0 and mode(b, NSI + '/tp1.py') == '600'),
    ('tle-1', 't-octal'): (NSI, '', '', lambda b, c, s, r: c == 0 and mode(b, NSI + '/tp1.py') == '600'),
    ('1re-2', 'd-symb'): (NSI, '', '', lambda b, c, s, r: c == 0 and mode(b, NSI + '/tp1.py') == '744'),
    ('tle-1', 't-symb'): (NSI, '', '', lambda b, c, s, r: c == 0 and mode(b, NSI + '/tp1.py') == '744'),
    ('1re-2', 'd-sudo'): (PROF, '', '', lambda b, c, s, r: c == 0 and os.stat(b.p(PROF + '/notes.csv')).st_uid == 65534),
    ('tle-1', 't-sudo'): (PROF, '', '', lambda b, c, s, r: c == 0 and os.stat(b.p(PROF + '/notes.csv')).st_uid == 65534),
    ('tle-1', 't-ls'): (E + '/devoirs', '', '', lambda b, c, s, r: c == 0 and 'examens' in s and 'notes.csv' in s and 'tp1.py' not in s),
    ('tle-1', 't-mkdir'): (E, '', '', lambda b, c, s, r: c == 0 and os.path.isdir(b.p(E + '/devoirs/archives'))),
    ('tle-1', 't-rmr'): (E, REORG, '', lambda b, c, s, r: c == 0 and not existe(b, E + '/archives') and existe(b, E + '/devoirs')),
}
# erreurs prévues que la page dit « justes, mais pas ce qui est demandé »
JUSTES_MAIS = {'p-abs': ['~', 'home/'], 'p-cp': ['/home', '~'], 't-cp': ['/home', '~'], 'd-symb': ['+x', 'a+x', 'ugo+x', '700', '744', '755', '764'],
               't-symb': ['+x', 'a+x', 'ugo+x', '700', '744', '755', '764'], 'd-octal': ['u=rw,go=', 'u=rw,go-rwx', 'go-rwx'],
               't-octal': ['u=rw,go=', 'u=rw,go-rwx', 'go-rwx'], 'p-cd': ['touch '], 'd-sudo': ['chown direction'], 't-sudo': ['chown direction']}


def verifier(shell, nom):
    print('== %s' % nom)
    qs = questions()
    manquent = [k for k in CAS if k not in qs]
    if manquent:
        erreurs.append(('questions absentes', manquent))
    b = Bac(shell)
    n = 0
    try:
        for (page, q), (depart, avant, suite, ok) in CAS.items():
            if (page, q) not in qs:
                continue
            bonnes, fausses, md = qs[(page, q)]
            for genre, liste in (('accepte', bonnes), ('refuse', fausses)):
                for rep in liste:
                    b.arbre()
                    c, s = b.lancer(avant + (rep if not avant.endswith('#') else ' ' + rep) + suite if not avant.endswith('#') else avant[:-1] + suite, depart)
                    juste = ok(b, c, s, rep)
                    n += 1
                    if genre == 'accepte' and not juste:
                        erreurs.append((nom, page, q, 'acceptée mais FAUSSE', rep, s.strip()[:80]))
                    if genre == 'refuse' and juste:
                        voulu = any(x in rep for x in JUSTES_MAIS.get(q, []))
                        if not voulu:
                            erreurs.append((nom, page, q, 'REFUSÉE alors qu\'elle marche', rep))
        print('  %d réponses lancées' % n)
        # les cases à cocher de terminale : chaque commande, essayée depuis devoirs
        t = TEXTES['tle-1']
        sec = re.search(r'id="t-cases">(.*?)</section>', t, re.S).group(1)
        for li in re.findall(r'<li( data-juste)?>(.*?)</li>', sec):
            cmd = net(li[1])
            b.arbre()
            c, s = b.lancer(cmd + ' && pwd', E + '/devoirs')
            marche = c == 0 and s.strip() == NSI
            if marche != bool(li[0]):
                erreurs.append((nom, 'tle-1', 't-cases', cmd, 'marche' if marche else 'ne marche pas'))
        print('  cases à cocher (terminale) : essayées')
        # exemples résolus (rejoués)
        for titre, cmd, depart, ctl in [
                ('cd ../../projets puis touch', 'cd ../../projets && touch essai.txt', NSI, lambda c, s: existe(b, E + '/projets/essai.txt')),
                ('cp ../../prof/notes.csv ../devoirs/', 'cp ../../prof/notes.csv ../devoirs/', E + '/projets', lambda c, s: existe(b, E + '/devoirs/notes.csv')),
                ('ls .. depuis nsi', 'ls ..', NSI, lambda c, s: s.strip() == 'nsi'),
                ('mkdir test ; ls', 'mkdir test && ls', E, lambda c, s: s.split() == ['devoirs', 'projets', 'test']),
                ('cd projets, ./projets, /home/eleve/projets', 'cd projets && cd .. && cd ./projets && cd /home/eleve/projets && pwd', E, lambda c, s: s.strip() == E + '/projets'),
                ('cd /projets refusé', 'cd /projets', E, lambda c, s: c != 0),
                ('ls ../devoirs/nsi', 'ls ../devoirs/nsi', E + '/projets', lambda c, s: s.strip() == 'tp1.py'),
                ('mkdir projets/brouillons', 'mkdir projets/brouillons', E, lambda c, s: os.path.isdir(b.p(E + '/projets/brouillons'))),
                ('rmdir projets', 'rmdir projets', E, lambda c, s: c == 0 and not existe(b, E + '/projets')),
                ('chmod 750 -> rwxr-x---', 'chmod 750 tp1.py && stat -c %A tp1.py', NSI, lambda c, s: s.strip() == '-rwxr-x---'),
                ('chmod g+w', 'chmod g+w ../../../prof/notes.csv && stat -c %A ../../../prof/notes.csv', NSI, lambda c, s: s.strip() == '-rw-rw----'),
                ('chmod 640 -> rw-r-----', 'chmod 640 tp1.py && stat -c %A tp1.py', NSI, lambda c, s: s.strip() == '-rw-r-----'),
                ('chown prof tp1.py', 'chown nobody tp1.py', NSI, lambda c, s: os.stat(b.p(NSI + '/tp1.py')).st_uid == 65534),
                ('cat tp1.py | grep barge', 'cat tp1.py | grep barge', NSI, lambda c, s: s.strip() == '\n'.join(l for l in TP1.splitlines() if 'barge' in l)),
                ('grep depart (sortie de la page)', 'grep depart tp1.py', NSI,
                 lambda c, s: s.strip() == '\n'.join(sortie_apres('1re-2', 'grep depart tp1.py').strip().split('\n')[1:])),
                ('grep barge (réponse attendue)', 'grep barge tp1.py', NSI,
                 lambda c, s: s.strip() == html.unescape(re.search(r'<pre class="td-attendu">\n?(.*?)</pre>', TEXTES['1re-2'], re.S).group(1)).strip()),
                ('rmdir archives (refus de la page, message de bash ; BusyBox écrit « rmdir: \'archives\': Directory not empty »)', REORG + 'rmdir archives', E,
                 lambda c, s: c != 0 and 'Directory not empty' in s and (nom != 'bash' or ' '.join(s.split()) == ' '.join(sortie_apres('tle-1', 'rmdir archives').split('\n', 1)[1].split())))]:
            b.arbre()
            c, s = b.lancer(cmd, depart)
            if not ctl(c, s):
                erreurs.append((nom, 'exemple', titre, s.strip()[:120]))
        print('  exemples résolus et sorties : rejoués')
        cat = sortie_apres('1re-2', 'affiché par').split('\n', 1)[1].strip()
        b.arbre()
        if b.lancer('cat tp1.py', NSI)[1].strip() != cat:
            erreurs.append((nom, 'cat tp1.py différent de la page'))
    finally:
        b.fin()


def lsl_et_chown():
    print('== ls -l et chown (sans root pour chown)')
    r = tempfile.mkdtemp(prefix='td-linux-', dir='/tmp')
    try:
        os.chmod(r, 0o755)
        os.makedirs(os.path.join(r, 'examens'))
        open(os.path.join(r, 'notes.csv'), 'w', encoding='utf-8').write(NOTES)
        os.chmod(os.path.join(r, 'notes.csv'), 0o640)
        os.chmod(os.path.join(r, 'examens'), 0o770)
        subprocess.run(['touch', '-d', '2026-11-25 10:00', 'notes.csv', 'examens'], cwd=r)
        s = subprocess.run(['ls', '-l'], cwd=r, capture_output=True, text=True, env=dict(os.environ, LC_ALL='C.UTF-8')).stdout
        groupe = re.search(r'1 prof (\S+)', sortie_apres('1re-2', 'eleve@lycee:~$ ls -l /home/prof')).group(1)
        s = re.sub(r' ([12]) \S+ \S+ ', r' \1 prof %s ' % groupe, s)
        for page in ('1re-2', 'tle-1'):
            p = sortie_apres(page, 'eleve@lycee:~$ ls -l /home/prof').split('\n', 1)[1].strip()
            ok = [' '.join(l.split()) for l in s.strip().splitlines()] == [' '.join(l.split()) for l in p.splitlines()]
            print('  ls -l (%s) :' % page, 'identique à la page (espaces près)' if ok else 'DIFFÉRENT')
            if not ok:
                erreurs.append(('ls -l', page, s))
        os.chown(os.path.join(r, 'notes.csv'), 65534, 65534)
        c = subprocess.run(['setpriv', '--reuid=65534', '--regid=65534', '--clear-groups', 'chown', 'root', 'notes.csv'],
                           cwd=r, capture_output=True, text=True, env=dict(os.environ, LC_ALL='C.UTF-8'))
        msg = c.stderr.strip()
        page = ' '.join(sortie_apres('1re-2', 'prof@lycee:~$ chown').split('\n', 1)[1].split())
        print('  chown sans root :', msg, '| page :', 'identique' if page == msg else 'DIFFÉRENT')
        if page != msg:
            erreurs.append(('chown', msg, page))
    finally:
        shutil.rmtree(r)


def processus():
    """kill sur un vrai calcul ; ps -ef | grep sur un vrai calcul ; en-tête de ps -ef ; réponses sur l'arbre."""
    print('== processus (bash)')
    qs = questions()
    bonnes, fausses, _ = qs[('tle-2', 'pr-kill')]
    for cmd in bonnes + fausses:
        p = subprocess.Popen(['python3', '-c', 'import time; time.sleep(30)'])
        vrai = cmd.replace('450', str(p.pid)).replace('sudo ', '')
        for autre in ('120', '451', '118'):
            vrai = vrai.replace(' ' + autre, ' 999999')
        r = subprocess.run(['bash', '-c', vrai], capture_output=True, text=True)
        try:
            p.wait(timeout=2)
            arrete = True
        except subprocess.TimeoutExpired:
            arrete = False
        p.kill(); p.wait()
        if (cmd in bonnes) != arrete and cmd != 'kill 9 450':     # kill 9 450 arrête aussi le calcul : la page le dit (retour), et le refuse
            erreurs.append(('pr-kill', cmd, 'arrêté' if arrete else 'pas arrêté', r.stderr.strip()[:60]))
    print('  kill : %d commandes essayées sur un vrai processus' % len(bonnes + fausses))
    d = tempfile.mkdtemp(prefix='td-linux-', dir='/tmp')
    open(os.path.join(d, 'marees.py'), 'w').write('import time\ntime.sleep(600)\n')
    calcul = subprocess.Popen(['python3', 'marees.py'], cwd=d)
    try:
        bonnes, fausses, _ = qs[('tle-2', 'pr-tube')]
        for cmd in bonnes + fausses:
            r = subprocess.run(['bash', '-c', 'ps -ef | ' + cmd], capture_output=True, text=True)
            lignes = [l for l in r.stdout.splitlines() if 'python3 marees.py' in l]
            juste = r.returncode == 0 and bool(lignes) and all('marees' in l for l in r.stdout.splitlines())
            if (cmd in bonnes) != juste:
                erreurs.append(('pr-tube', cmd, juste))
        print('  ps -ef | grep : %d commandes essayées sur un vrai calcul' % len(bonnes + fausses))
    finally:
        calcul.kill(); calcul.wait(); shutil.rmtree(d)
    vrai = subprocess.run(['ps', '-ef'], capture_output=True, text=True).stdout.splitlines()[0].split()
    page_ps = sortie_apres('tle-2', 'eleve@lycee:~$ ps -ef')
    tete = page_ps.split('\n')[1].split()
    if [x for x in vrai if x not in ('STIME', 'TTY', 'TIME')] != tete:
        erreurs.append(('en-tête de ps -ef', vrai, tete))
    print('  en-tête de ps -ef :', ' '.join(vrai), '-> page :', ' '.join(tete))
    # l'extrait : parent de 450, enfants de 120 ; les réponses acceptées n'ont que les bons PID
    lignes = [l.split(None, 4) for l in page_ps.strip().split('\n')[2:]]
    ppid = {int(l[1]): int(l[2]) for l in lignes}
    assert ppid[450] == 120 and sorted(k for k, v in ppid.items() if v == 120) == [450, 451]
    for q, attendus in (('pr-parent', {120}), ('pr-enfants', {450, 451})):
        b2, f2, _ = qs[('tle-2', q)]
        for r in b2:
            nums = {int(x) for x in re.findall(r'\b\d{2,}\b', r)}
            if nums and nums != attendus:
                erreurs.append((q, 'acceptée avec un autre PID', r))
        for r in f2:
            if {int(x) for x in re.findall(r'\b\d{2,}\b', r)} == attendus:
                erreurs.append((q, 'refusée avec les bons PID', r))
    print('  arbre : PPID lus dans l\'extrait, réponses acceptées cohérentes')


verifier(['bash'], 'bash')
if os.environ.get('BUSYBOX'):
    verifier([os.environ['BUSYBOX'], 'sh'], 'BusyBox ash')
lsl_et_chown()
processus()
if erreurs:
    print('\nÀ REVOIR :')
    for e in erreurs:
        print('  ', e)
    sys.exit(1)
print('\ntout est juste')
