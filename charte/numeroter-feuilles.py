#!/usr/bin/env python3
"""Numéros qui continuent d'une feuille à l'autre d'un TD (décision de l'enseignant du 21/11, T123c).

Usage (à la racine du dépôt) :
  python3 -I charte/numeroter-feuilles.py DOSSIER [DOSSIER…]       les feuilles du TD de chaque dossier
  python3 -I charte/numeroter-feuilles.py feuille-1.html feuille-2.html …   les feuilles, dans l'ordre
  python3 -I charte/numeroter-feuilles.py --tout                   tous les TD à plusieurs feuilles du dépôt
  Ajouter --verifier : rien n'est écrit, et le script sort en erreur si une feuille est à renuméroter.

Dans un dossier, les feuilles sont les pages qui chargent assets/td-en-ligne.js, rangées par data-feuille
(sans lui : 1), puis index.html d'abord, puis par nom. La feuille 2 commence au numéro qui suit la dernière
question de la feuille 1, et ainsi de suite.

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


def feuilles_du_dossier(d):
    fichiers = [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.html') and est_td(os.path.join(d, f))]

    def cle(ch):
        _, c = lire(ch)
        n = int(c.feuille) if c.feuille and c.feuille.isdigit() else 1
        nom = os.path.basename(ch)
        chiffres = [int(x) for x in re.findall(r'\d+', nom)]
        return (n, nom != 'index.html', chiffres, nom)
    fichiers.sort(key=cle)
    rangs = [cle(f)[0] for f in fichiers]
    if len(set(rangs)) != len(rangs):
        sys.exit(f'{os.path.relpath(d, RACINE)} : deux feuilles ont le même data-feuille ({rangs}) ; donnez les fichiers dans l\'ordre')
    return fichiers


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
    groupes = []
    if '--tout' in sys.argv:
        sys.path.insert(0, ICI)
        import importlib.util
        spec = importlib.util.spec_from_file_location('nouveau_td', os.path.join(ICI, 'nouveau-td.py'))
        nt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nt)
        for d, sous, fs in os.walk(RACINE):
            if nt.ignorer(d):
                sous[:] = []
                continue
            sous.sort()
            f = feuilles_du_dossier(d) if any(x.endswith('.html') for x in fs) else []
            if len(f) > 1:
                groupes.append(f)
    elif args and all(os.path.isdir(a) for a in args):
        groupes = [feuilles_du_dossier(os.path.abspath(a)) for a in args]
    elif args and all(a.endswith('.html') for a in args):
        groupes = [[os.path.abspath(a) for a in args]]
    else:
        sys.exit(__doc__)
    total = 0
    for g in groupes:
        if not g:
            print('(aucune feuille de TD dans ce dossier)')
            continue
        total += numeroter(g, verifier)
    print(f'{total} feuille(s) ' + ('à renuméroter' if verifier else 'renumérotée(s)') if total else 'Numéros à jour.')
    sys.exit(1 if verifier and total else 0)


if __name__ == '__main__':
    main()
