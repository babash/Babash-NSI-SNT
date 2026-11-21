#!/usr/bin/env python3
"""Numéros qui continuent d'une feuille à l'autre d'un TD (décision de l'enseignant du 21/11, T123c).

Usage (à la racine du dépôt) :
  python3 -I charte/numeroter-feuilles.py DOSSIER [DOSSIER…]       les feuilles du TD de chaque dossier
  python3 -I charte/numeroter-feuilles.py feuille-1.html feuille-2.html …   les feuilles, dans l'ordre
  python3 -I charte/numeroter-feuilles.py --tout                   tous les TD à plusieurs feuilles du dépôt
  Ajouter --verifier : rien n'est écrit, et le script sort en erreur si une feuille est à renuméroter.

Les feuilles d'un TD (pages qui chargent assets/td-en-ligne.js) sont reconnues dans les deux rangements :
  - un dossier : index.html, feuille-2.html, feuille-3.html… ;
  - des pages de même nom dans un dossier : td-for.html, td-for-2.html, td-for-3.html…
Un dossier peut contenir plusieurs TD. Les feuilles sont rangées par data-feuille s'il est écrit, sinon par
leur nom (index.html et td-for.html : feuille 1). La feuille 2 commence au numéro qui suit la dernière question
de la feuille 1, et ainsi de suite. Un TD mal rangé est signalé sans arrêter les autres.

Le compte suit le moteur : une suite de numéros pour l'écran et une pour le papier. Une question
data-support="ecran" ne compte qu'à l'écran, une data-support="papier" que sur papier, les autres partout.
Le script écrit sur <main> de chaque feuille (sauf la première) :
  data-premiere-question="13"           le premier numéro de la feuille ;
  data-premiere-question-papier="11"    seulement si le premier numéro sur papier est différent.
Il ne touche à rien d'autre ; une feuille déjà juste n'est pas réécrite. On le relance après chaque ajout
ou retrait d'une question (passe finale d'un lot).
"""
import html.parser
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
ATTRS = ('data-premiere-question', 'data-premiere-question-papier')


class Compte(html.parser.HTMLParser):
    """Compte les questions (section.td-q[data-type]) par support, et lit <main>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ecran = self.papier = 0
        self.feuille = None
        self.td = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main' and 'data-td' in a and self.td is None:
            self.td = a['data-td']
            self.feuille = a.get('data-feuille')
        if 'td-q' in (a.get('class') or '').split() and 'data-type' in a:
            sup = a.get('data-support') or ''
            if sup != 'papier':
                self.ecran += 1
            if sup != 'ecran':
                self.papier += 1


def lire(chemin):
    t = open(chemin, encoding='utf-8').read()
    c = Compte()
    c.feed(t)
    return t, c


def est_td(chemin):
    try:
        t = open(chemin, encoding='utf-8').read()
    except (OSError, UnicodeDecodeError):
        return False
    return 'td-en-ligne.js' in t and re.search(r'<main\b[^>]*\bdata-td=', t) is not None and '{{' not in t


def rang_et_groupe(chemin):
    """Les deux rangements d'un TD à plusieurs feuilles :
    - un dossier : index.html (feuille 1), feuille-2.html, feuille-3.html… ;
    - des pages de même nom : td-for.html (feuille 1), td-for-2.html, td-for-3.html…
    Renvoie (groupe, rang tiré du nom). data-feuille, s'il est écrit, l'emporte sur le rang du nom."""
    d, nom = os.path.split(chemin)
    base = nom[:-5]
    if base == 'index':
        return (d, ''), 1
    m = re.fullmatch(r'feuille-(\d+)', base)
    if m:
        return (d, ''), int(m.group(1))
    m = re.fullmatch(r'(.+)-(\d+)', base)
    if m and os.path.exists(os.path.join(d, m.group(1) + '.html')):
        return (d, m.group(1)), int(m.group(2))
    return (d, base), 1


def grouper(fichiers):
    """Range des pages de TD en TD (groupes), chacun dans l'ordre de ses feuilles. Une feuille sans data-feuille
    prend le rang de son nom (index.html, td-for.html : 1). Renvoie (groupes, problèmes)."""
    groupes, problemes = {}, []
    for ch in fichiers:
        g, rang = rang_et_groupe(ch)
        _, c = lire(ch)
        if c.feuille and c.feuille.isdigit():
            rang = int(c.feuille)
        groupes.setdefault(g, []).append((rang, os.path.basename(ch), ch))
    sortie = []
    for g, l in sorted(groupes.items()):
        l.sort()
        rangs = [x[0] for x in l]
        if len(set(rangs)) != len(rangs):
            problemes.append(f'{os.path.relpath(l[0][2], RACINE)} … : deux feuilles du même TD ont le même rang {rangs} '
                             '(data-feuille ou nom) ; donnez les fichiers dans l\'ordre')
            continue
        sortie.append([x[2] for x in l])
    return sortie, problemes


def feuilles_du_dossier(d):
    """Les TD d'un dossier (un ou plusieurs, chacun avec ses feuilles)."""
    return grouper([os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.html') and est_td(os.path.join(d, f))])


def poser(main_tag, attrs):
    """Retire les anciens attributs de numérotation et pose les nouveaux (dans l'ordre), juste après data-td."""
    t = main_tag
    for a in ATTRS:
        t = re.sub(r'\s' + a + r'="[^"]*"', '', t)
    ajout = ''.join(f' {k}="{v}"' for k, v in attrs)
    if not ajout:
        return t
    m = re.search(r'\sdata-td="[^"]*"', t)
    return t[:m.end()] + ajout + t[m.end():]


def numeroter(fichiers, verifier):
    """Renvoie le nombre de feuilles à changer (ou changées)."""
    e, p, changes = 1, 1, 0
    for k, ch in enumerate(fichiers):
        t, c = lire(ch)
        attrs = []
        if k > 0:
            attrs.append(('data-premiere-question', e))
            if p != e:
                attrs.append(('data-premiere-question-papier', p))
        m = re.search(r'<main\b[^>]*>', t)
        neuf = poser(m.group(0), attrs)
        rel = os.path.relpath(ch, RACINE)
        plage = f'questions {e} à {e + c.ecran - 1}' if c.ecran else 'aucune question à l\'écran'
        if c.papier != c.ecran or p != e:
            plage += f' (papier : {p} à {p + c.papier - 1})' if c.papier else ' (aucune sur papier)'
        etat = ''
        if neuf != m.group(0):
            changes += 1
            etat = ' : à renuméroter' if verifier else ' : écrit'
            if not verifier:
                open(ch, 'w', encoding='utf-8').write(t[:m.start()] + neuf + t[m.end():])
        print(f'{rel} : {plage}{etat}')
        e += c.ecran
        p += c.papier
    return changes


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    verifier = '--verifier' in sys.argv
    groupes, problemes = [], []
    if '--tout' in sys.argv:
        import importlib.util
        spec = importlib.util.spec_from_file_location('nouveau_td', os.path.join(ICI, 'nouveau-td.py'))
        nt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nt)
        for d, sous, fs in os.walk(RACINE):
            if nt.ignorer(d):
                sous[:] = []
                continue
            sous.sort()
            if any(x.endswith('.html') for x in fs):
                g, pb = feuilles_du_dossier(d)
                groupes += [x for x in g if len(x) > 1]
                problemes += pb
    elif args and all(os.path.isdir(a) for a in args):
        for a in args:
            g, pb = feuilles_du_dossier(os.path.abspath(a))
            groupes += g
            problemes += pb
    elif args and all(a.endswith('.html') for a in args):
        groupes = [[os.path.abspath(a) for a in args]]
    else:
        sys.exit(__doc__)
    total = 0
    for g in groupes:
        total += numeroter(g, verifier)
    for x in problemes:
        print('Problème :', x)
    print((f'{total} feuille(s) ' + ('à renuméroter' if verifier else 'renumérotée(s)')) if total else 'Numéros à jour.')
    sys.exit(1 if (verifier and total) or problemes else 0)


if __name__ == '__main__':
    main()
