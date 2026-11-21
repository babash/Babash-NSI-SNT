"""Teste les questions « code » d'une page de TD, comme le fait la page (Python 3.13).

Lancer : python3 -I tester-codes.py ../exercices-parcours-listes/index.html [faux.json]
Pour chaque question « code » : la correction (pre[data-verifier="correction"]) est exécutée
avec les tests (script.td-tests), dans le même ordre que le moteur ; elle doit passer et donner
la sortie attendue. Avec faux.json ({"q1": ["programme faux", …], …}), chaque programme faux
doit être refusé (erreur, test qui échoue ou sortie différente).
"""
import html.parser
import json
import subprocess
import sys

LANCEUR = r'''
import sys, traceback, linecache, json
d = json.loads(sys.stdin.read())
src, tests, nom = d["code"], d["tests"], d["fichier"]
linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)
g = {"__name__": "__main__"}
def rapport(e):
    tb = e.__traceback__.tb_next if e.__traceback__ else None
    return "".join(traceback.format_exception(type(e), e, tb))
try:
    exec(compile(src, nom, "exec"), g)
except BaseException as e:
    print("\n@@erreur@@" + rapport(e)); sys.exit()
if tests:
    try:
        exec(compile(tests, "tests.py", "exec"), g)
    except AssertionError as e:
        print("\n@@test@@" + str(e)); sys.exit()
    except BaseException as e:
        print("\n@@test@@" + rapport(e)); sys.exit()
print("\n@@ok@@")
'''


class Lecteur(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.q, self.pile, self.cur = [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section' and a.get('data-type') == 'code':
            self.cur = {'id': a.get('id'), 'fichier': a.get('data-fichier', 'mon_code.py'), 'corr': [], 'tests': '', 'att': None}
            self.q.append(self.cur)
        if self.cur is not None and tag in ('pre', 'script'):
            cl = (a.get('class') or '').split()
            if tag == 'pre' and a.get('data-verifier') == 'correction':
                self.pile.append('corr')
            elif tag == 'pre' and 'td-attendu' in cl:
                self.pile.append('att')
            elif tag == 'script' and 'td-tests' in cl:
                self.pile.append('tests')
            else:
                self.pile.append(None)
        if tag == 'section' and a.get('data-type') != 'code':
            self.cur = None

    def handle_endtag(self, tag):
        if tag in ('pre', 'script') and self.pile:
            self.pile.pop()

    def handle_data(self, data):
        if not self.pile or self.pile[-1] is None or self.cur is None:
            return
        k = self.pile[-1]
        data = data[1:] if data.startswith('\n') else data
        if k == 'corr':
            self.cur['corr'].append(data)
        elif k == 'att':
            self.cur['att'] = data.rstrip()
        else:
            self.cur['tests'] += data


def lancer(code, tests, fichier):
    r = subprocess.run([sys.executable, '-I', '-c', LANCEUR], input=json.dumps({'code': code, 'tests': tests, 'fichier': fichier}),
                       capture_output=True, text=True, timeout=10)
    sortie, _, fin = r.stdout.rpartition('\n@@')
    etat = fin.split('@@')[0]
    return etat, sortie.strip(), fin.split('@@', 1)[-1].strip()


lu = Lecteur()
lu.feed(open(sys.argv[1], encoding='utf-8').read())
faux = json.load(open(sys.argv[2], encoding='utf-8')) if len(sys.argv) > 2 else {}
ok = True
for q in lu.q:
    for c in q['corr']:
        etat, sortie, detail = lancer(c, q['tests'], q['fichier'])
        juste = etat == 'ok' and (q['att'] is None or sortie == q['att'])
        ok &= juste
        print(f"{q['id']} correction : {'acceptée' if juste else 'REFUSÉE'} (sortie {sortie!r}) {detail if not juste else ''}")
    for f in faux.get(q['id'], []):
        etat, sortie, detail = lancer(f, q['tests'], q['fichier'])
        refuse = not (etat == 'ok' and (q['att'] is None or sortie == q['att']))
        ok &= refuse
        print(f"{q['id']} programme faux : {'refusé' if refuse else 'ACCEPTÉ'} ({etat} : {detail[:90] or sortie!r})")
print('tout est juste' if ok else 'PROBLÈME')
