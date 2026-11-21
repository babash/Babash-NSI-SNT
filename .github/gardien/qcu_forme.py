#!/usr/bin/env python3
"""La bonne réponse d'un choix unique (QCU) se repère-t-elle à sa forme ? (Gardien, T125)

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/qcu_forme.py PAGE.html [FEUILLE-2.html …] [-- AUTRE-TD.html …]

Un TD = ses feuilles, données à la suite ; « -- » sépare deux TD. Pour chaque QCU d'une page de TD
en ligne (section.td-q[data-type="qcu"], une seule option data-juste), l'outil compare le texte
affiché des options :
  - longueur : la bonne option est « nettement la plus longue » quand elle compte au moins 10 % de
    caractères de plus que chacune des autres. Au hasard, cela arrive environ une fois sur quatre.
    Le TD est À REVOIR si c'est le cas d'au moins la moitié de ses QCU (et d'au moins 3) : choisir
    l'option la plus longue suffirait alors à réussir. Chaque QCU concerné est listé, avec les
    longueurs, et le signe « ++ » quand l'écart dépasse 30 % ;
  - autres indices, à relire : seule option avec (ou sans) du code, du gras ou de l'italique ;
    seule option avec (ou sans) un point final ; premier mot à part quand les autres le partagent.
La place de la bonne option à l'écran (le moteur mélange les options, toujours de la même façon)
se lit dans la page affichée, pas ici.
Règle du Gardien 17 (21/11/2026), d'après la consigne « bonne réponse jamais repérable par sa place
ou sa forme » et la fiche de l'Atelier des quiz (« ni gras, ni longueur, ni formulation à part »).
Code de sortie : 0 rien à signaler ; 1 au moins un TD À REVOIR ; 2 seulement des indices à relire.
"""
import html.parser
import sys

SEUIL, NET, PART, MINI = 1.10, 1.30, 0.5, 3


class Lecteur(html.parser.HTMLParser):
    """Relève les QCU : pour chaque option, son texte, et si elle contient du code, du gras, de l'italique."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.qcu, self.q, self.opt, self.prof_opt = [], None, None, 0
        self.pile = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cl = (a.get('class') or '').split()
        if tag in ('br', 'img', 'input', 'meta', 'link', 'hr', 'wbr', 'source'):
            return
        self.pile.append(tag)
        if tag == 'section' and 'td-q' in cl:
            self.q = {'id': a.get('id', '?'), 'type': a.get('data-type'), 'options': [], 'prof': len(self.pile)}
        elif (self.q is not None and tag == 'li' and self.opt is None and self.q.get('ul', 0) > 0
              and len(self.pile) == self.q['ul'] + 1):
            self.opt = {'juste': 'data-juste' in a, 'texte': [], 'code': False, 'gras': False, 'italique': False}
            self.prof_opt = len(self.pile)
        elif self.q is not None and tag == 'ul' and 'td-options' in cl and not self.q.get('ul'):
            self.q['ul'] = len(self.pile)
        if self.opt is not None:
            if tag in ('code', 'pre'):
                self.opt['code'] = True
            elif tag in ('b', 'strong'):
                self.opt['gras'] = True
            elif tag in ('i', 'em'):
                self.opt['italique'] = True

    def handle_endtag(self, tag):
        while self.pile:
            t = self.pile.pop()
            n = len(self.pile) + 1
            if self.opt is not None and n == self.prof_opt:
                self.opt['texte'] = ' '.join(''.join(self.opt['texte']).split())
                self.q['options'].append(self.opt)
                self.opt = None
            if self.q is not None and n == self.q.get('ul'):
                self.q['ul'] = 0
            if self.q is not None and n == self.q['prof']:
                if self.q['type'] == 'qcu':
                    self.qcu.append(self.q)
                self.q = None
            if t == tag:
                break

    def handle_data(self, data):
        if self.opt is not None:
            self.opt['texte'].append(data)


def indices(opts, j):
    """Les indices de forme autres que la longueur : la bonne option seule à avoir (ou à ne pas avoir) un trait."""
    notes = []
    autres = [o for k, o in enumerate(opts) if k != j]
    for cle, avec, sans in (('code', 'du code', 'code'), ('gras', 'du gras', 'gras'), ('italique', 'de l\'italique', 'italique')):
        if opts[j][cle] and not any(o[cle] for o in autres):
            notes.append('seule avec ' + avec)
        elif not opts[j][cle] and all(o[cle] for o in autres):
            notes.append('seule sans ' + sans)
    point = [o['texte'].endswith('.') for o in opts]
    if all(point[k] != point[j] for k in range(len(opts)) if k != j):
        notes.append('seule ' + ('avec' if point[j] else 'sans') + ' point final')
    mots = [(o['texte'].split() or [''])[0].lower() for o in opts]
    ceux = {mots[k] for k in range(len(opts)) if k != j}
    if len(ceux) == 1 and mots[j] not in ceux:
        notes.append('premier mot à part (« %s » contre « %s »)' % (mots[j], ceux.pop()))
    return notes


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__.strip())
        sys.exit(0 if args else 2)
    groupes, g = [], []
    for a in args:
        if a == '--':
            if g:
                groupes.append(g)
            g = []
        else:
            g.append(a)
    if g:
        groupes.append(g)
    a_revoir = a_relire = 0
    for g in groupes:
        n, longues, lignes, notes = 0, 0, [], []
        for f in g:
            lu = Lecteur()
            lu.feed(open(f, encoding='utf-8').read())
            for q in lu.qcu:
                opts = q['options']
                justes = [k for k, o in enumerate(opts) if o['juste']]
                if len(justes) != 1 or len(opts) < 3:
                    continue
                j = justes[0]
                n += 1
                L = [len(o['texte']) for o in opts]
                autre = max(L[k] for k in range(len(L)) if k != j)
                if L[j] >= SEUIL * autre:
                    longues += 1
                    lignes.append('    %s#%s : %d caractères contre %d au plus pour les autres%s'
                                  % (f.rsplit('/', 1)[-1], q['id'], L[j], autre, ' ++' if L[j] >= NET * autre else ''))
                for x in indices(opts, j):
                    notes.append('    %s#%s : %s' % (f.rsplit('/', 1)[-1], q['id'], x))
        revoir = n >= MINI and longues >= PART * n
        a_revoir += revoir
        a_relire += bool(notes)
        print('%s : %d QCU ; bonne option nettement la plus longue : %d (%d %%)%s'
              % (g[0], n, longues, 100 * longues // max(n, 1), ' : À REVOIR' if revoir else ''))
        for x in lignes:
            print(x)
        if notes:
            print('  autres indices à relire :')
            for x in notes:
                print(x)
    sys.exit(1 if a_revoir else 2 if a_relire else 0)


if __name__ == '__main__':
    main()
