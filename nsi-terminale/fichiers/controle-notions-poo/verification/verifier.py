"""Vérifie le contrôle de notions « Programmation orientée objet » par exécution (Python 3.13).

Relit les données de controle.js et la clé de cle.js (blocs JSON entre
marqueurs), puis, pour chaque sujet :
  - exécute la classe du sujet et le programme A : les sorties des lignes
    demandées sont les réponses attendues ; idem pour le programme B ;
  - lit les attributs d'un objet réel (vars) ;
  - réexécute les programmes à message d'erreur et compare la console,
    caractère pour caractère (seul le dossier est retiré des chemins) ;
  - applique chaque modification proposée au choix unique « self oublié » :
    seule la bonne corrige le programme ;
  - essaie chaque écriture acceptée des lignes à compléter, et vérifie que
    les erreurs diagnostiquées sont refusées ;
  - exécute le programme C avec la méthode complétée.

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


def verifier(cond, texte):
    print(('ok     ' if cond else 'ÉCHEC  ') + texte)
    if not cond:
        echecs.append(texte)


def executer(code):
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, 'programme.py').write_text(code, encoding='utf-8')
        try:
            r = subprocess.run([PY, 'programme.py'], cwd=d, capture_output=True, text=True, timeout=5,
                               env={'PATH': os.environ.get('PATH', '/usr/bin'), 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
        except subprocess.TimeoutExpired:
            return 'DÉLAI DÉPASSÉ', -1
        return (r.stdout + r.stderr).replace(d + os.sep, ''), r.returncode


def ligne(t):
    return re.sub(r'\s+', '', t).replace("'", '"')


def norm(t):
    return re.sub(r'\s+', ' ', t).strip().lower()


# Les modifications proposées par le choix unique « self oublié » : (ligne, nouveau texte)
MODIFS = {
    '1': {'a': (11, 'print(t.places_libres(t))'), 'b': (7, '    def places_libres(self):'),
          'c': (11, 'print(Taxi.places_libres())'), 'd': (11, 'print(t.places_libres)')},
    '2': {'a': (11, 'e.ajouter(e, 10)'), 'b': (11, 'Etal.ajouter(10)'),
          'c': (7, '    def ajouter(self, n):'), 'd': (11, 'e.ajouter = 10')},
}
# Ce que le programme doit faire une fois corrigé
ESSAI_Q8 = {'1': ('', '4\n'), '2': ('\nprint(e.stock)', '10\n')}

print('Python :', subprocess.run([PY, '--version'], capture_output=True, text=True).stdout.strip())
for s, S in D['sujets'].items():
    P, Q, C = S['programmes'], S['q'], K[s]
    classe = P['CL']['code']
    nom = re.match(r'class (\w+)', classe).group(1)
    print('── Sujet', s, '(classe %s)' % nom)

    # q3 : les attributs d'un objet réel
    arg = '"Sada"' if s == '1' else '"mangue"'
    sortie, _ = executer(classe + '\n\nprint(*sorted(vars(%s(%s))))\n' % (nom, arg))
    verifier(sorted(sortie.split()) == sorted(C['q3']['attendu'].split()), 'q3 : attributs = %s' % sortie.strip())

    # q4 à q6 : les lignes du programme A
    a = P['A']['code'].split('\n')
    sortie, rc = executer(classe + '\n\n' + '\n'.join(a) + '\n')
    lignes_sortie = sortie.split('\n')
    prints = [i + 1 for i, l in enumerate(a) if l.startswith('print(')]
    for q, n in zip(['q4', 'q5', 'q6'], prints):
        verifier('ligne %d' % n in Q[q]['enonce'], '%s : l\'énoncé vise bien la ligne %d' % (q, n))
        k = prints.index(n)
        verifier(norm(lignes_sortie[k]) == norm(C[q]['attendu']), '%s : la ligne %d affiche %r' % (q, n, lignes_sortie[k]))

    # q7 : deux noms, un objet
    sortie, _ = executer(classe + '\n\n' + P['B']['code'] + '\n')
    verifier(sortie.strip() == C['q7']['attendu'], 'q7 : affiche %s' % sortie.strip())

    # q8 : console réelle, et seule la bonne modification corrige
    sortie, rc = executer(P['E1']['code'] + '\n')
    verifier(rc == 1 and sortie == P['E1']['console'], 'q8 : console identique à l\'exécution réelle')
    suite, attendu = ESSAI_Q8[s]
    for k, (n, texte) in MODIFS[s].items():
        l = P['E1']['code'].split('\n')
        l[n - 1] = texte
        sortie, rc = executer('\n'.join(l) + suite + '\n')
        corrige = rc == 0 and sortie == attendu
        verifier(corrige == (k == C['q8']['attendu']), 'q8 : option %s (%s) %s' % (k, texte.strip(), 'corrige' if corrige else 'ne corrige pas : ' + (sortie.strip().split('\n')[-1][:60])))
        option = dict(Q['q8']['options'])[k]
        verifier(texte.strip().split('(')[0] in option.replace('`', ''), 'q8 : l\'option %s décrit bien cette modification' % k)

    # q9 : console réelle, puis chaque écriture acceptée de la ligne 8
    sortie, rc = executer(P['E2']['code'] + '\n')
    verifier(rc == 1 and sortie == P['E2']['console'], 'q9 : console identique à l\'exécution réelle')

    def essai_q9(expr):
        l = P['E2']['code'].split('\n')
        l[7] = '        return ' + expr
        test = ('t = Taxi("Sada", 5)\nt.passagers = 3\nprint(t.places_libres())' if s == '1'
                else 'e = Etal("mangue", 3)\ne.stock = 7\nprint(e.valeur())')
        sortie, rc = executer('\n'.join(l[:9]) + '\n' + test + '\n')
        return rc == 0 and sortie == ('2\n' if s == '1' else '21\n')
    for x in C['q9']['attendu']:
        verifier(essai_q9(x), 'q9 : « return %s » corrige le programme' % x)

    # q10 : créer l'objet
    def essai_q10(instr):
        v = instr.split('=')[0]
        sortie, rc = executer(classe + '\n\n' + instr + '\nprint(*vars(%s).values())\n' % v)
        return rc == 0 and sortie == ('Chiconi 6 0\n' if s == '1' else 'litchi 4 0\n')
    for x in C['q10']['attendu']:
        verifier(essai_q10(x), 'q10 : « %s » crée le bon objet' % x)

    # q11 et q12 : la méthode complétée, puis le programme C
    methode = P['M']['code']
    verifier(P['M'].get('debut') == len(classe.split('\n')) + 2, 'q11 : la méthode commence bien à la ligne %d' % (len(classe.split('\n')) + 2))

    def essai_q11(instr):
        code = classe + '\n\n' + methode.replace('.' * 18, instr) + '\n\n' + P['C']['code'] + '\n'
        return executer(code)
    for x in C['q11']['attendu']:
        sortie, rc = essai_q11(x)
        verifier(rc == 0 and sortie == C['q12']['attendu'] + '\n', 'q11, q12 : avec « %s », le programme C affiche %s' % (x, sortie.strip()))

    # Les erreurs diagnostiquées des lignes à compléter sont bien refusées
    for q, essai in (('q9', essai_q9), ('q10', essai_q10)):
        for d in C[q]['diag']:
            if 'si' in d:
                verifier(not essai(d['si']) and ligne(d['si']) not in C[q]['attendu'], '%s : « %s » est refusée' % (q, d['si']))
    for d in C['q11']['diag']:
        if 'si' in d:
            sortie, rc = essai_q11(d['si'])
            verifier(not (rc == 0 and sortie == C['q12']['attendu'] + '\n'), 'q11 : « %s » est refusée' % d['si'])

    for q in D['questions']:
        k = C[q['id']]
        if q['type'] == 'qcu':
            verifier(k['attendu'] in dict(Q[q['id']]['options']), '%s : l\'option attendue existe' % q['id'])
            verifier(all(d['si'] != k['attendu'] for d in k['diag'] if 'si' in d), '%s : diagnostics sur de mauvaises options' % q['id'])
        elif q['type'] != 'ligne':
            verifier(all(norm(d['si']) != norm(k['attendu']) for d in k['diag'] if 'si' in d), '%s : aucun diagnostic n\'est la réponse' % q['id'])

print()
print('Bilan :', 'tout est juste.' if not echecs else '%d échec(s).' % len(echecs))
sys.exit(1 if echecs else 0)
