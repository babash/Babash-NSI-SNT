#!/usr/bin/env python3
"""Vérifie une page de TD en ligne : chaque programme est exécuté pour de vrai.

Usage : python3 -I charte/verifier-td.py chemin/vers/td.html [autre.html…]
        python3 -I charte/verifier-td.py --erreur taxi.py   (le message à copier)

Ce qui est contrôlé, question par question (attribut data-type) :
- sortie   : la sortie réelle du code est celle de pre.td-attendu ;
- courte   : avec data-verifier="sortie", la sortie réelle est une des réponses ;
- trous    : le code rempli avec la première réponse de chaque case s'exécute
             (et donne pre.td-attendu s'il y en a un) ;
- ordre    : les lignes, dans l'ordre juste, s'exécutent (et donnent pre.td-attendu) ;
- erreur   : le message réel de Python est celui de pre.td-erreur, mot pour mot,
             et le code corrigé (data-ligne + data-reponse) s'exécute sans erreur ;
- code     : chaque pre.td-code[data-verifier="correction"] donne pre.td-attendu ;
- options  : un li[data-verifier="arret"] s'arrête, un li[data-verifier="infini"]
             tourne encore après 2 secondes.
Le message d'erreur est produit comme dans le moteur (même nom de fichier,
même format que python3 fichier.py).

Ajouts du 21/11 (mêmes attributs que le moteur) :
- script.td-preambule (sur la question ou pour toute la page) : du Python exécuté avant
  le programme, dans le même espace (le robot, des données) ;
- data-entrees (une ligne par input()) et data-graine (random.seed) sur la question
  ou sur chaque pre.td-attendu d'une question « code » (plusieurs essais) ;
- data-espaces="exact" : les espaces de début de ligne comptent ;
- data-langage="sql" : la requête est exécutée par SQLite sur les tables de la page
  (script.td-tables, type="text/x-sql", sur la question ou pour toute la page) ;
  sans tables, la question est signalée « non vérifiée » sans erreur ;
  data-langage="texte" : rien à exécuter ;
- « erreur » : si la ligne corrigée garde un décalage fautif (IndentationError),
  le décalage juste est cherché (0, 4, 8… espaces).

Ajouts du 21/11, T123c :
- les tests cachés (script.td-tests) d'une question « code » sont exécutés après chaque correction,
  comme dans le moteur (leurs print n'entrent pas dans la sortie comparée) ;
- data-langage est lu d'abord sur le <pre> du code, puis sur la question et la page ;
- comme dans le moteur, l'invite d'input() (le texte entre les parenthèses) n'entre pas
  dans la sortie comparée : pre.td-attendu ne contient que ce qu'affiche print.
"""
import html.parser
import os
import re
import sqlite3
import subprocess
import sys
import tempfile

LANCEUR = r'''
import sys, traceback, linecache
nom, fsrc, fpre, graine, ftests = sys.argv[1:6]
src = open(fsrc, encoding="utf-8").read()
pre = open(fpre, encoding="utf-8").read()
linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)
g = {"__name__": "__main__"}
# comme le moteur : l'invite d'input() n'entre pas dans la sortie comparée
def _saisir(invite=""):
    l = sys.stdin.readline()
    if not l:
        raise EOFError("EOF when reading a line")
    return l[:-1] if l.endswith("\n") else l
import builtins
builtins.input = _saisir
if pre:
    exec(compile(pre, "preambule.py", "exec"), g)
if graine != "":
    import random
    random.seed(int(graine) if graine.lstrip("-").isdigit() else graine)
try:
    exec(compile(src, nom, "exec"), g)
except SystemExit:
    pass
except BaseException as e:
    sys.stdout.flush()
    tb = e.__traceback__.tb_next if e.__traceback__ else None
    t = tb
    while t is not None and t.tb_next is not None:
        if t.tb_next.tb_frame.f_code is _saisir.__code__:
            t.tb_next = None
            break
        t = t.tb_next
    sys.stderr.write("".join(traceback.format_exception(type(e), e, tb)))
    sys.exit(1)
# les tests cachés (script.td-tests), comme le moteur : après le programme, dans le même espace ; leurs print
# ne vont pas dans la sortie comparée
tests = open(ftests, encoding="utf-8").read()
if tests:
    sys.stdout.flush()
    sys.stdout = sys.stderr
    try:
        exec(compile(tests, "tests.py", "exec"), g)
    except AssertionError as e:
        sys.stderr.write("TEST : " + (str(e) or "un test ne passe pas") + "\n")
        sys.exit(2)
    except BaseException as e:
        sys.stderr.write("TEST : " + "".join(traceback.format_exception(type(e), e, e.__traceback__.tb_next if e.__traceback__ else None)))
        sys.exit(2)
'''


class Noeud:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.enfants = tag, dict(attrs), parent, []

    def classes(self):
        return (self.attrs.get('class') or '').split()

    def texte(self):
        return ''.join(e if isinstance(e, str) else e.texte() for e in self.enfants)

    def tous(self, pred):
        for e in self.enfants:
            if isinstance(e, Noeud):
                if pred(e):
                    yield e
                yield from e.tous(pred)


VIDES = {'meta', 'link', 'br', 'img', 'input', 'hr', 'source', 'wbr'}


class Lecteur(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.racine = Noeud('#', {}, None)
        self.cur = self.racine

    def handle_starttag(self, tag, attrs):
        n = Noeud(tag, attrs, self.cur)
        self.cur.enfants.append(n)
        if tag not in VIDES:
            self.cur = n

    def handle_endtag(self, tag):
        c = self.cur
        while c is not self.racine and c.tag != tag:
            c = c.parent
        if c is not self.racine:
            self.cur = c.parent

    def handle_data(self, data):
        self.cur.enfants.append(data)


def code_de(t):
    return t[1:] if t.startswith('\n') else t


def lancer(code, fichier='mon_code.py', delai=5, pre='', entrees=None, graine=None, tests=''):
    with tempfile.TemporaryDirectory() as d:
        fs, fp = os.path.join(d, 'src.py'), os.path.join(d, 'pre.py')
        open(fs, 'w', encoding='utf-8').write(code)
        open(fp, 'w', encoding='utf-8').write(pre or '')
        ft = os.path.join(d, 'tests.py')
        open(ft, 'w', encoding='utf-8').write(tests or '')
        try:
            r = subprocess.run([sys.executable, '-I', '-c', LANCEUR, fichier, fs, fp, graine or '', ft],
                               input=entrees if entrees is not None else '', capture_output=True, text=True, timeout=delai, cwd=d)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return None, '', ''


def lancer_sql(requete, tables):
    """Exécute les tables puis la requête avec SQLite ; renvoie (0, lignes « a | b », '') ou (1, '', message)."""
    base = sqlite3.connect(':memory:')
    try:
        base.executescript(tables)
        lignes = []
        for instr in [x for x in requete.split(';') if x.strip()]:
            cur = base.execute(instr)
            if cur.description:
                lignes += [' | '.join('' if c is None else str(c) for c in rang) for rang in cur.fetchall()]
        return 0, '\n'.join(lignes) + ('\n' if lignes else ''), ''
    except sqlite3.Error as e:
        return 1, '', f'{type(e).__name__}: {e}'
    finally:
        base.close()


def decouper_trous(l):
    """[[réponse]] : la case se ferme au premier « ]] » où les crochets de la réponse sont équilibrés (comme le moteur)."""
    out, debut = [], 0
    while True:
        k = l.find('[[', debut)
        if k < 0:
            break
        # « t[[[i]]] » : après un nom, une parenthèse ou un crochet, le premier « [ » est celui du code (comme le moteur)
        if l[k + 2:k + 3] == '[' and k > 0 and (l[k - 1].isalnum() or l[k - 1] in '_)]'):
            k += 1
        p, fin = 0, -1
        for j in range(k + 2, len(l)):
            c = l[j]
            if c == ']' and p == 0 and l[j + 1:j + 2] == ']':
                fin = j
                break
            if c == '[':
                p += 1
            elif c == ']' and p > 0:
                p -= 1
        if fin < 0:
            break
        out += [l[debut:k], l[k + 2:fin]]
        debut = fin + 2
    return out + [l[debut:]]


def remplir_trous(code):
    return '\n'.join(''.join(m.split('|')[0].strip() if k % 2 else m for k, m in enumerate(decouper_trous(l))) for l in code.split('\n'))


def sortie_norm(t, exact=False):
    """Comme le moteur : lignes vides ignorées, fins de ligne sans espaces ; début de ligne gardé si exact."""
    lignes = [l.rstrip() if exact else l.strip() for l in t.replace('\r', '').split('\n')]
    return '\n'.join(l for l in lignes if l.strip())


def sur_depart(depart, correction):
    """Le code de départ sans ses blocs de premier niveau (def, class) que la correction réécrit, puis la correction."""
    noms = set(re.findall(r'^(?:def|class)\s+(\w+)', correction, re.M))
    blocs, cur = [], []
    for l in depart.split('\n'):
        if l and not l[0].isspace() and cur:
            blocs.append(cur)
            cur = []
        cur.append(l)
    if cur:
        blocs.append(cur)
    garde = [b for b in blocs if not (re.match(r'(?:def|class)\s+(\w+)', b[0]) and re.match(r'(?:def|class)\s+(\w+)', b[0]).group(1) in noms)]
    return '\n'.join('\n'.join(b) for b in garde) + '\n' + correction


def classe(c):
    return lambda n: c in n.classes()


def attribut_herite(n, nom, defaut=None):
    while n is not None:
        if isinstance(n, Noeud) and nom in n.attrs:
            return n.attrs[nom]
        n = n.parent
    return defaut


def verifier(chemin):
    lu = Lecteur()
    lu.feed(open(chemin, encoding='utf-8').read())
    erreurs, n, notes = [], 0, []

    def ko(q, msg):
        erreurs.append(f'{q} : {msg}')

    def script(s, classe_):
        """Le script de la question, sinon celui de la page (hors des questions)."""
        x = next(s.tous(classe(classe_)), None)
        if x is None:
            x = next(lu.racine.tous(lambda y: classe_ in y.classes() and not any('td-q' in a.classes() for a in ancetres(y, lu.racine))), None)
        return code_de(x.texte()) if x is not None else ''

    for s in lu.racine.tous(lambda x: 'td-q' in x.classes() and 'data-type' in x.attrs):
        n += 1
        q, t = s.attrs.get('id', f'question {n}'), s.attrs['data-type']
        fichier = s.attrs.get('data-fichier', 'mon_code.py')
        # data-langage : sur le <pre> du code (comme dans le moteur), sinon sur la question ou la page
        pre_code = next((p for p in s.tous(lambda x: x.tag == 'pre' and ('td-code' in x.classes() or 'td-depart' in x.classes()))
                         if 'data-langage' in p.attrs and not any('td-options' in a.classes() for a in ancetres(p, s))), None)
        langage = pre_code.attrs['data-langage'] if pre_code is not None else attribut_herite(s, 'data-langage', 'python')
        pre = script(s, 'td-preambule')
        exact = s.attrs.get('data-espaces') == 'exact'
        ent, gr = s.attrs.get('data-entrees'), s.attrs.get('data-graine')
        if t == 'libre' or langage == 'texte':
            continue
        if langage == 'sql':
            tables = script(s, 'td-tables')
            if not tables:
                notes.append(f'{q} : SQL non vérifié (la page ne donne pas ses tables : script.td-tables)')
                continue
            lancer_q = lambda code, fichier=None, **k: lancer_sql(code, tables)
        else:
            lancer_q = lambda code, fichier='mon_code.py', **k: lancer(code, fichier, pre=pre, entrees=k.get('entrees', ent), graine=k.get('graine', gr), delai=k.get('delai', 5), tests=k.get('tests', ''))
        codes = [p for p in s.tous(lambda x: x.tag == 'pre' and 'td-code' in x.classes())
                 if not any('td-options' in a.classes() or 'td-correction' in a.classes() for a in ancetres(p, s))]
        att = next(s.tous(classe('td-attendu')), None)
        attendu = code_de(att.texte()).rstrip() if att else None
        code = code_de(codes[0].texte()) if codes else ''
        if t == 'sortie':
            rc, out, err = lancer_q(code, fichier)
            if rc != 0 or out.rstrip() != attendu:
                ko(q, f'sortie réelle {out!r} {err!r}, attendue {attendu!r}')
        elif t == 'courte' and s.attrs.get('data-verifier') == 'sortie':
            rc, out, err = lancer_q(code, fichier)
            if rc != 0 or out.strip() not in s.attrs.get('data-reponse', '').split('|'):
                ko(q, f'sortie réelle {out!r} {err!r}, réponses {s.attrs.get("data-reponse")!r}')
        elif t == 'trous':
            rc, out, err = lancer_q(remplir_trous(code), fichier)
            if rc != 0 or (attendu is not None and out.rstrip() != attendu):
                ko(q, f'code rempli : sortie {out!r} {err!r}, attendue {attendu!r}')
        elif t == 'ordre':
            lignes = [li.texte().rstrip() for li in s.tous(lambda x: x.tag == 'li' and x.parent and 'td-lignes' in x.parent.classes())]
            rc, out, err = lancer_q('\n'.join(lignes), fichier)
            if rc != 0 or (attendu is not None and out.rstrip() != attendu):
                ko(q, f'lignes dans l\'ordre : sortie {out!r} {err!r}, attendue {attendu!r}')
        elif t == 'erreur':
            pe = next(s.tous(classe('td-erreur')), None)
            rc, out, err = lancer_q(code, fichier)
            if pe is None or err.rstrip() != code_de(pe.texte()).rstrip():
                ko(q, 'message réel différent :\n' + err)
            ligne = int(s.attrs.get('data-ligne', '0'))
            rep = s.attrs.get('data-reponse')
            if rep:
                L = code.split('\n')
                fautive = L[ligne - 1]
                garde = fautive[:len(fautive) - len(fautive.lstrip())]
                # le décalage d'origine d'abord ; puis, s'il est fautif (IndentationError), 0, 4, 8… espaces
                essais = [garde] + [' ' * k for k in range(0, 17, 4) if ' ' * k != garde]
                for dec in essais:
                    L[ligne - 1] = dec + rep.split('|')[0].strip()
                    rc, out, err2 = lancer_q('\n'.join(L), fichier)
                    if rc == 0:
                        break
                    if dec == garde:
                        err = err2
                if rc != 0:
                    ko(q, 'le code corrigé ne marche pas :\n' + err)
        elif t == 'code':
            corr = list(s.tous(lambda x: x.tag == 'pre' and x.attrs.get('data-verifier') == 'correction'))
            if not corr:
                ko(q, 'aucune correction à vérifier (pre.td-code data-verifier="correction")')
            # un essai par pre.td-attendu (chacun avec ses data-entrees, data-graine), ou un seul
            atts = list(s.tous(lambda x: x.tag == 'pre' and 'td-attendu' in x.classes())) or [None]
            for c in corr:
                for a_ in atts:
                    att = code_de(a_.texte()).rstrip() if a_ is not None else None
                    e_ = a_.attrs.get('data-entrees', ent) if a_ is not None else ent
                    g_ = a_.attrs.get('data-graine', gr) if a_ is not None else gr
                    src = code_de(c.texte())
                    tests_q = next((code_de(x.texte()) for x in s.tous(classe('td-tests'))), '') if langage == 'python' else ''
                    rc, out, err = lancer_q(src, fichier, entrees=e_, graine=g_, tests=tests_q)
                    dep = next((code_de(x.texte()) for x in s.tous(classe('td-depart'))), '')
                    if rc not in (0, None) and dep.strip() and tests_q:
                        # une correction qui ne donne que la partie à compléter : on la pose sur le code de départ
                        # (sans les blocs qu'elle réécrit), comme l'élève qui complète le squelette
                        rc2, out2, err2 = lancer_q(sur_depart(dep, src), fichier, entrees=e_, graine=g_, tests=tests_q)
                        if rc2 == 0:
                            rc, out, err = rc2, out2, err2
                    if rc == 2:
                        ko(q, 'la correction ne passe pas les tests cachés : ' + err.strip()[-300:])
                    elif rc != 0 or (att is not None and sortie_norm(out, exact) != sortie_norm(att, exact)):
                        ko(q, f'correction : sortie {out!r} {err!r}, attendue {att!r}' + (f' (saisies {e_!r})' if e_ is not None else ''))
        for li in s.tous(lambda x: x.tag == 'li' and 'data-verifier' in x.attrs):
            v = li.attrs['data-verifier']
            pre_ = next(li.tous(lambda x: x.tag == 'pre'), None)
            rc, out, err = lancer_q(code_de(pre_.texte()) if pre_ else '', fichier, delai=2)
            if v == 'arret' and rc != 0:
                ko(q, 'une option devait s\'arrêter : ' + (err or 'elle tourne encore après 2 s'))
            if v == 'infini' and rc is not None:
                ko(q, 'une option devait tourner sans fin, elle s\'arrête')
    return n, erreurs, notes


def ancetres(n, jusqua):
    a = n.parent
    while a is not None and a is not jusqua:
        yield a
        a = a.parent


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--erreur':
        # le message à copier dans pre.td-erreur, au format du moteur
        rc, out, err = lancer(open(sys.argv[2], encoding='utf-8').read(), os.path.basename(sys.argv[2]))
        sys.stdout.write(err or 'Aucune erreur : ce programme marche.\n')
        sys.exit(0)
    total = 0
    for chemin in sys.argv[1:]:
        n, err, notes = verifier(chemin)
        print(f'{chemin} : {n} questions, {"tout est juste" if not err else str(len(err)) + " problème(s)"}')
        for e in err:
            print('  -', e)
        for x in notes:
            print('  (note)', x)
        total += len(err)
    print(sys.version.split()[0])
    sys.exit(1 if total else 0)
