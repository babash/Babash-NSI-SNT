#!/usr/bin/env python3
"""Assemble un document à la charte (fiche, TD papier, TD en ligne) à partir de sa source.

Usage
-----
  python3 design/build/assembler.py SOURCE.html SORTIE.html
  python3 design/build/assembler.py --gabarits     # reconstruit les gabarits de charte/

Marques remplacées dans la source (commentaires HTML, une par ligne ou en ligne) :
  <!-- icone NOM -->                         icône au trait (liste ICONES ci-dessous)
  <!-- qr-cours URL | libellé | source | adresse courte -->
                                             bloc QR de cours : QR, notion, source, adresse en clair
  <!-- qr-en-ligne URL -->                   QR du TD en ligne (à placer dans .qr-enligne)
  <!-- runner ID UID -->                     badge d'un runner de l'équipage (tête, au trait)

Si la balise <body> porte data-sel="…", la source est celle d'un TD en ligne :
ses réponses en clair sont remplacées par des empreintes (voir td_en_ligne.py).

Les QR sont calculés ici, une fois pour toutes (design/build/qr.py) : la page
publiée ne contacte aucun service.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(os.path.dirname(ICI))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(RACINE, 'design', 'equipage'))

import qr  # noqa: E402
import td_en_ligne  # noqa: E402

_A = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">')
ICONES = {
    'livre': '<path d="M12 5v16"/><path d="M20 19a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-4a5 5 0 0 0-4 2 5 5 0 0 0-4-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4a5 5 0 0 1 4 2 5 5 0 0 1 4-2z"/>',
    'alerte': '<path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3"/><path d="M12 9v4M12 17h.01"/>',
    'idee': '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/>',
    'retour': '<path d="m12 19-7-7 7-7M19 12H5"/>',
    'imprimer': '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 9V3h12v6"/><rect x="6" y="14" width="12" height="8"/>',
    'projeter': '<rect x="2" y="3" width="20" height="14"/><path d="M8 21h8M12 17v4"/>',
    'horloge': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'telephone': '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    'pouce': '<path d="M11 12h2a2 2 0 1 0 0-4h-3c-.6 0-1.1.2-1.4.6L3 14"/><path d="m7 18 1.6-1.4c.3-.4.8-.6 1.4-.6h4c1.1 0 2.1-.4 2.8-1.2l4.6-4.4a2 2 0 0 0-2.75-2.91l-4.2 3.9"/><path d="m2 13 6 6"/>',
    'bilan': '<path d="M13 5h8M13 12h8M13 19h8"/><path d="m3 17 2 2 4-4M3 7l2 2 4-4"/>',
    'methode': '<path d="M10 6h11M10 12h11M10 18h11"/><path d="M4 6h1v4M4 10h2M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/>',
    'en-ligne': '<rect x="2" y="3" width="20" height="14"/><path d="M8 21h8M12 17v4"/><path d="m8 10 3 3 5-5"/>',
    'video': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m10 9 5 3-5 3z"/>',
    'page': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
    'lune': '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9"/>',
    'recommencer': '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
}

MARQUE = re.compile(r'<!--\s*(icone|qr-cours|qr-en-ligne|runner)\s+(.*?)\s*-->', re.S)


def _remplace(m):
    genre, args = m.group(1), [a.strip() for a in m.group(2).split('|')]
    if genre == 'icone':
        return _A + ICONES[args[0]] + '</svg>'
    if genre == 'qr-cours':
        url, libelle = args[0], args[1]
        source = args[2] if len(args) > 2 and args[2] else None
        court = args[3] if len(args) > 3 and args[3] else None
        v, mat = qr.qr_matrice(url)
        if v > 3:
            print(f'  attention : QR de version {v} ({len(mat)} modules) pour {url}', file=sys.stderr)
        return qr.bloc_html(url, libelle, source, court)
    if genre == 'qr-en-ligne':
        return qr.svg(args[0], libelle='QR code : la version en ligne du TD')
    if genre == 'runner':
        from runners import RUNNERS, portrait  # noqa: PLC0415
        rid, uid = args[0].split()[0], args[0].split()[1] if len(args[0].split()) > 1 else args[0] + '-doc'
        r = next(x for x in RUNNERS if x['id'] == rid)
        return portrait(r, 'trait', uid=uid, badge=True)
    return m.group(0)


def assembler(source, sortie):
    with open(source, encoding='utf-8') as f:
        texte = f.read()
    texte = MARQUE.sub(_remplace, texte)
    if re.search(r'<body\b[^>]*\bdata-sel="', texte):
        texte, bilan, erreurs = td_en_ligne.construire(texte)
        for e in erreurs:
            print('ERREUR :', e, file=sys.stderr)
        if erreurs:
            raise SystemExit(1)
        texte = texte.replace('<!doctype html>\n', '<!doctype html>\n<!-- Page construite par '
                              'design/build/assembler.py : ne pas la modifier à la main. Les réponses '
                              'ne sont pas écrites en clair, mais restent retrouvables par qui cherche '
                              'vraiment (outil d\'entraînement, pas de notation). -->\n', 1)
        print(f'{sortie} : {bilan["questions"]} questions, {bilan["champs"]} champs, '
              f'{bilan["corrections"]} corrections codées')
    else:
        texte = texte.replace('<!doctype html>\n', '<!doctype html>\n<!-- Page construite par '
                              'design/build/assembler.py à partir de ' + os.path.relpath(source, RACINE)
                              + ' : modifier la source, puis reconstruire. -->\n', 1)
        print(f'{sortie} : assemblé')
    with open(sortie, 'w', encoding='utf-8') as f:
        f.write(texte)


GABARITS = [
    ('design/sources/gabarit-td.source.html', 'charte/gabarit-td.html'),
    ('design/sources/gabarit-td-en-ligne.source.html', 'charte/gabarit-td-en-ligne.html'),
    ('design/sources/gabarit-fiche.source.html', 'charte/gabarit-fiche.html'),
]


def main():
    if sys.argv[1:] == ['--gabarits']:
        for s, d in GABARITS:
            if os.path.exists(os.path.join(RACINE, s)):
                assembler(os.path.join(RACINE, s), os.path.join(RACINE, d))
        return 0
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    assembler(sys.argv[1], sys.argv[2])
    return 0


if __name__ == '__main__':
    sys.exit(main())
