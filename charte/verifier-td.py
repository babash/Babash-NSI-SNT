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
"""
import html.parser
import subprocess
import sys

LANCEUR = r'''
import sys, traceback, linecache
src = sys.stdin.read()
nom = sys.argv[1]
linecache.cache[nom] = (len(src), None, src.splitlines(True), nom)
g = {"__name__": "__main__"}
try:
    exec(compile(src, nom, "exec"), g)
except SystemExit:
    pass
except BaseException as e:
    sys.stdout.flush()
    tb = e.__traceback__.tb_next if e.__traceback__ else None
    sys.stderr.write("".join(traceback.format_exception(type(e), e, tb)))
    sys.exit(1)
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


def lancer(code, fichier='mon_code.py', delai=5):
    try:
        r = subprocess.run([sys.executable, '-I', '-c', LANCEUR, fichier], input=code, capture_output=True,
                           text=True, timeout=delai)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, '', ''


def classe(c):
    return lambda n: c in n.classes()


def verifier(chemin):
    lu = Lecteur()
    lu.feed(open(chemin, encoding='utf-8').read())
    erreurs, n = [], 0

    def ko(q, msg):
        erreurs.append(f'{q} : {msg}')

    for s in lu.racine.tous(lambda x: 'td-q' in x.classes() and 'data-type' in x.attrs):
        n += 1
        q, t = s.attrs.get('id', f'question {n}'), s.attrs['data-type']
        fichier = s.attrs.get('data-fichier', 'mon_code.py')
        codes = [p for p in s.tous(lambda x: x.tag == 'pre' and 'td-code' in x.classes())
                 if not any('td-options' in a.classes() or 'td-correction' in a.classes() for a in ancetres(p, s))]
        att = next(s.tous(classe('td-attendu')), None)
        attendu = code_de(att.texte()).rstrip() if att else None
        code = code_de(codes[0].texte()) if codes else ''
        if t == 'sortie':
            rc, out, err = lancer(code, fichier)
            if rc != 0 or out.rstrip() != attendu:
                ko(q, f'sortie réelle {out!r} {err!r}, attendue {attendu!r}')
        elif t == 'courte' and s.attrs.get('data-verifier') == 'sortie':
            rc, out, err = lancer(code, fichier)
            if rc != 0 or out.strip() not in s.attrs.get('data-reponse', '').split('|'):
                ko(q, f'sortie réelle {out!r} {err!r}, réponses {s.attrs.get("data-reponse")!r}')
        elif t == 'trous':
            import re
            rempli = re.sub(r'\[\[(.*?)\]\]', lambda m: m.group(1).split('|')[0], code)
            rc, out, err = lancer(rempli, fichier)
            if rc != 0 or (attendu is not None and out.rstrip() != attendu):
                ko(q, f'code rempli : sortie {out!r} {err!r}, attendue {attendu!r}')
        elif t == 'ordre':
            lignes = [li.texte().rstrip() for li in s.tous(lambda x: x.tag == 'li' and x.parent and 'td-lignes' in x.parent.classes())]
            rc, out, err = lancer('\n'.join(lignes), fichier)
            if rc != 0 or (attendu is not None and out.rstrip() != attendu):
                ko(q, f'lignes dans l\'ordre : sortie {out!r} {err!r}, attendue {attendu!r}')
        elif t == 'erreur':
            pe = next(s.tous(classe('td-erreur')), None)
            rc, out, err = lancer(code, fichier)
            if pe is None or err.rstrip() != code_de(pe.texte()).rstrip():
                ko(q, 'message réel différent :\n' + err)
            ligne = int(s.attrs.get('data-ligne', '0'))
            rep = s.attrs.get('data-reponse')
            if rep:
                L = code.split('\n')
                L[ligne - 1] = L[ligne - 1][:len(L[ligne - 1]) - len(L[ligne - 1].lstrip())] + rep.split('|')[0]
                rc, out, err = lancer('\n'.join(L), fichier)
                if rc != 0:
                    ko(q, 'le code corrigé ne marche pas :\n' + err)
        elif t == 'code':
            corr = list(s.tous(lambda x: x.tag == 'pre' and x.attrs.get('data-verifier') == 'correction'))
            if not corr:
                ko(q, 'aucune correction à vérifier (pre.td-code data-verifier="correction")')
            for c in corr:
                rc, out, err = lancer(code_de(c.texte()), fichier)
                if rc != 0 or (attendu is not None and out.rstrip() != attendu):
                    ko(q, f'correction : sortie {out!r} {err!r}, attendue {attendu!r}')
        for li in s.tous(lambda x: x.tag == 'li' and 'data-verifier' in x.attrs):
            v = li.attrs['data-verifier']
            pre = next(li.tous(lambda x: x.tag == 'pre'), None)
            rc, out, err = lancer(code_de(pre.texte()) if pre else '', fichier, delai=2)
            if v == 'arret' and rc != 0:
                ko(q, 'une option devait s\'arrêter : ' + (err or 'elle tourne encore après 2 s'))
            if v == 'infini' and rc is not None:
                ko(q, 'une option devait tourner sans fin, elle s\'arrête')
    return n, erreurs


def ancetres(n, jusqua):
    a = n.parent
    while a is not None and a is not jusqua:
        yield a
        a = a.parent


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--erreur':
        # le message à copier dans pre.td-erreur, au format du moteur
        import os
        rc, out, err = lancer(open(sys.argv[2], encoding='utf-8').read(), os.path.basename(sys.argv[2]))
        sys.stdout.write(err or 'Aucune erreur : ce programme marche.\n')
        sys.exit(0)
    total = 0
    for chemin in sys.argv[1:]:
        n, err = verifier(chemin)
        print(f'{chemin} : {n} questions, {"tout est juste" if not err else str(len(err)) + " problème(s)"}')
        for e in err:
            print('  -', e)
        total += len(err)
    print(sys.version.split()[0])
    sys.exit(1 if total else 0)
