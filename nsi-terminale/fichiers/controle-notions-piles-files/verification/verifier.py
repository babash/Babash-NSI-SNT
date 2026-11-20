"""Vérifie le contrôle de notions « Piles et files » par exécution (Python 3.13).

Relit les données de controle.js et la clé de cle.js (blocs JSON entre
marqueurs), écrit le module pile_file.py de l'énoncé dans un dossier
temporaire, puis :
  - réexécute les programmes à message d'erreur et compare la console,
    caractère pour caractère (seul le dossier est retiré des chemins) ;
  - recalcule chaque réponse attendue (états de pile et de file, sorties,
    valeur renvoyée, pile ou file auxiliaire) ;
  - essaie chaque écriture acceptée d'une ligne à compléter (et vérifie que
    les erreurs diagnostiquées sont bien refusées) ;
  - contrôle les choix uniques qui portent sur du code.

Usage : python3.13 -I verification/verifier.py   (depuis n'importe où)
Babash - NSI Tani Malandi · MIT
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ICI = pathlib.Path(__file__).resolve().parent.parent
PY = os.environ.get('PYTHON', 'python3.13')
echecs = []


def bloc(fichier, nom):
    texte = (ICI / fichier).read_text(encoding='utf-8')
    return json.loads(re.search(r'/\*' + nom + r'-DEBUT\*/(.*?)/\*' + nom + r'-FIN\*/', texte, re.S).group(1))


D = bloc('controle.js', 'DONNEES')
K = bloc('cle.js', 'CLE')
MODULE = D['module']['code'] + '\n'


def verifier(cond, texte):
    print(('ok     ' if cond else 'ÉCHEC  ') + texte)
    if not cond:
        echecs.append(texte)


def executer(code):
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, 'pile_file.py').write_text(MODULE, encoding='utf-8')
        pathlib.Path(d, 'programme.py').write_text(code, encoding='utf-8')
        try:
            r = subprocess.run([PY, 'programme.py'], cwd=d, capture_output=True, text=True, timeout=5,
                               env={'PATH': os.environ.get('PATH', '/usr/bin'), 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
        except subprocess.TimeoutExpired:
            return 'DÉLAI DÉPASSÉ', -1
        return (r.stdout + r.stderr).replace(d + os.sep, ''), r.returncode


def norm(t):
    """Même normalisation que moteur.js (jetons) pour comparer des listes de valeurs."""
    import unicodedata
    t = ''.join(c for c in unicodedata.normalize('NFD', str(t)) if not unicodedata.combining(c)).lower()
    return [x.strip('"\'«»') for x in re.split(r'[\s,;|]+', t) if x.strip('"\'«»')]


def ligne(t):
    return re.sub(r'\s+', '', t).replace("'", '"')


ENTETE = 'from pile_file import Pile, File\n'
HAUT = '\ndef haut_vers_bas(p):\n    return list(reversed(p.contenu))\n'

print('Python :', subprocess.run([PY, '--version'], capture_output=True, text=True).stdout.strip())
for s, S in D['sujets'].items():
    P, Q, C = S['programmes'], S['q'], K[s]
    print('── Sujet', s)

    # Les nombres des énoncés
    def nombres(t):
        return [int(x) for x in re.findall(r'-?\d+', t.split(':')[-1])]

    # q1 : ce que retire depiler / defiler
    sortie, _ = executer(ENTETE + 'p = Pile()\nf = File()\nfor e in [1, 2, 3]:\n    p.empiler(e)\n    f.enfiler(e)\nprint(p.depiler(), f.defiler())\n')
    verifier(sortie == '3 1\n', 'q1 : depiler retire le dernier empilé (3), defiler le premier enfilé (1)')
    verifier(C['q1']['attendu'] == ('c' if s == '1' else 'b'), 'q1 : bonne option (pile : dernier empilé ; file : premier enfilé)')

    # q3 : sommet / tete puis depiler / defiler
    depart = nombres(Q['q3']['enonce'].split('On exécute')[0])
    if s == '1':
        code = ENTETE + 'p = Pile()\nfor e in %r:\n    p.empiler(e)\nx = p.sommet()\ny = p.depiler()\nprint(*reversed(p.contenu))\n' % list(reversed(depart))
    else:
        code = ENTETE + 'f = File()\nfor e in %r:\n    f.enfiler(e)\nx = f.tete()\ny = f.defiler()\nprint(*f.contenu)\n' % depart
    sortie, _ = executer(code)
    verifier(norm(sortie) == norm(C['q3']['attendu']), 'q3 : %s (attendu %s)' % (sortie.strip(), C['q3']['attendu']))

    # q4, q5 : états
    sortie, _ = executer(ENTETE + P['P4']['code'] + '\nprint(*reversed(p.contenu))\n')
    verifier(norm(sortie) == norm(C['q4']['attendu']), 'q4 : p du sommet vers le bas = %s' % sortie.strip())
    sortie, _ = executer(ENTETE + P['P5']['code'] + '\nprint(*f.contenu)\n')
    verifier(norm(sortie) == norm(C['q5']['attendu']), 'q5 : f de la tête vers la queue = %s' % sortie.strip())

    # q6 : sortie exacte
    sortie, rc = executer(ENTETE + P['P6']['code'] + '\n')
    verifier(rc == 0 and sortie == C['q6']['attendu'] + '\n', 'q6 : sortie = %r' % sortie)

    # q7 : la console affichée est la vraie
    sortie, rc = executer(P['ERR']['code'] + '\n')
    verifier(rc == 1 and sortie == P['ERR']['console'], 'q7 : console identique à l\'exécution réelle')
    verifier(sortie.rstrip().endswith('IndexError: pop from empty list'), 'q7 : IndexError: pop from empty list')

    # q8 : chaque condition acceptée corrige le programme, pour 0 à 5 éléments
    lignes = P['ERR']['code'].split('\n')

    def essai_q8(cond):
        for n in range(6):
            if s == '1':
                l2 = ['from pile_file import Pile', 'p = Pile()'] + ['p.empiler(%d)' % (10 * (k + 1)) for k in range(n)] + ['total = 0', 'while %s:' % cond] + lignes[6:]
                attendu = '%d\n' % sum(10 * (k + 1) for k in range(n))
            else:
                noms = ['Anli', 'Faïza', 'Nayma', 'Ali', 'Sitti'][:n]
                l2 = ['from pile_file import File', 'f = File()', 'for nom in %r:' % noms, '    f.enfiler(nom)', 'servis = 0', 'while %s:' % cond] + lignes[6:]
                attendu = ''.join('Au tour de %s\n' % x for x in noms) + '%d personnes servies\n' % n
            sortie, rc = executer('\n'.join(l2) + '\n')
            if rc != 0 or sortie != attendu:
                return False
        return True
    verifier(lignes[5].startswith('while' if s == '2' else 'for'), 'q8 : la ligne 6 est bien la boucle')
    for a in C['q8']['attendu']:
        cond = a.replace('not', 'not ').replace('is', ' is ').replace('not (', 'not(').replace('  ', ' ')
        verifier(essai_q8(cond), 'q8 : « while %s: » corrige le programme' % cond)
    for d in C['q8']['diag']:
        if 'si' in d:
            verifier(not essai_q8(d['si']) and ligne(d['si']) not in C['q8']['attendu'], 'q8 : « %s » est refusée' % d['si'])

    # q9 : expressions sur une liste Python
    opts = dict(Q['q9']['options'])
    for k, o in opts.items():
        expr = o.strip('`')
        if s == '1':
            code = 'pile = [9, 2, 7]\ntry:\n    v = %s\nexcept Exception as e:\n    v = type(e).__name__\nprint(v, pile == [9, 2, 7])\n' % expr
            juste = '7 True\n'
        else:
            code = 'file = [5, 3, 8]\ntry:\n    v = %s\nexcept Exception as e:\n    v = type(e).__name__\nprint(v, file == [3, 8])\n' % expr
            juste = '5 True\n'
        sortie, _ = executer(code)
        verifier((sortie == juste) == (k == C['q9']['attendu']), 'q9 : %s → %s' % (expr, sortie.strip()))

    # q10 à q12 : l'exercice
    ex = P['EX']['code']
    depart = nombres(S['contextes']['ex']['texte'])
    if s == '1':
        fabrique = 'p = Pile()\nfor e in %r:\n    p.empiler(e)\n' % list(reversed(depart))
        appel, etat, aux = 'compter(p, 2)', 'list(reversed(p.contenu))', 'list(reversed(aux.contenu))'
    else:
        fabrique = 'f = File()\nfor e in %r:\n    f.enfiler(e)\n' % depart
        appel, etat, aux = 'maximum(f)', 'list(f.contenu)', 'list(aux.contenu)'
    trou = '.' * 14
    # q11 : aux après la première boucle (lignes 9 à 11 remplacées par « return aux »)
    l = ex.split('\n')
    code = ENTETE + '\n'.join(l[:8]) + '\n    return aux\n' + fabrique + 'aux = ' + appel + '\nprint(*' + aux + ')\n'
    sortie, _ = executer(code)
    verifier(norm(sortie) == norm(C['q11']['attendu']), 'q11 : aux après la première boucle = %s' % sortie.strip())

    def essai_q12(expr):
        code = ENTETE + ex.replace(trou, expr) + '\n' + fabrique + 'r = ' + appel + '\nprint(r, ' + etat + ')\n'
        return executer(code)
    for a in C['q12']['attendu']:
        sortie, rc = essai_q12(a)
        verifier(rc == 0 and sortie == '%s %r\n' % (C['q10']['attendu'], depart), 'q10, q12 : avec %s, renvoie %s et rend la structure intacte' % (a, sortie.strip()))
    for d in C['q12']['diag']:
        if 'si' in d:
            sortie, rc = essai_q12(d['si'])
            verifier(not (rc == 0 and sortie == '%s %r\n' % (C['q10']['attendu'], depart)), 'q12 : « %s » est refusée (%s)' % (d['si'], sortie.strip()[:40]))

    # Aucun diagnostic « si » n'est la bonne réponse
    for q in D['questions']:
        k = C[q['id']]
        for d in k.get('diag', []):
            if 'si' in d:
                bon = k['attendu'] if q['type'] != 'ligne' else None
                if q['type'] == 'ligne':
                    verifier(ligne(d['si']) not in k['attendu'], '%s : le diagnostic « %s » n\'est pas une réponse acceptée' % (q['id'], d['si']))
                elif q['type'] == 'qcu':
                    verifier(d['si'] != bon, '%s : diagnostic sur une mauvaise option' % q['id'])
                else:
                    verifier(norm(d['si']) != norm(bon), '%s : le diagnostic « %s » n\'est pas la réponse' % (q['id'], d['si']))
        if q['type'] == 'qcu':
            verifier(k['attendu'] in dict(Q[q['id']]['options']), '%s : l\'option attendue existe' % q['id'])

print()
print('Bilan :', 'tout est juste.' if not echecs else '%d échec(s).' % len(echecs))
sys.exit(1 if echecs else 0)
