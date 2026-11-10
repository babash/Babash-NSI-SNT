#!/usr/bin/env python3
"""Construit la page en ligne d'un TD (mini-site auto-correctif, règle 19).

La source s'écrit avec les réponses en clair ; la page publiée n'a plus que
des empreintes, et ses corrections sont codées en base64. Le moteur de la
page (charte/td-en-ligne.js) calcule les mêmes empreintes dans le navigateur.

Usage
-----
  python3 design/build/td_en_ligne.py SOURCE.html SORTIE.html
  python3 design/build/td_en_ligne.py --empreinte SEL CHAMP NORME "réponse"

Dans la source
--------------
  <body data-td="identifiant" data-sel="un mot au hasard">
  Sur chaque champ (attribut data-champ, unique dans la page) :
    data-reponse="…"           une seule réponse acceptée
    data-reponses='["…","…"]'  plusieurs réponses acceptées (JSON)
    data-norm="souple|exact|nombre|code"   (champs de saisie ; souple par défaut)
  Choix : data-reponse="b" ou "a,c" (identifiants des cases, dans n'importe quel ordre).
  Ordre : data-reponse="c,a,b" (identifiants data-v dans le bon ordre).
  Correction d'une question : <template class="tl-correction">…HTML…</template>

Ce que cela protège, et ce que cela ne protège pas
--------------------------------------------------
Les réponses ne se lisent pas d'un coup d'œil dans la page. Mais un·e élève
qui cherche vraiment peut les retrouver (en essayant des réponses, ou en lisant
la source du dépôt, qui est public). C'est un outil pour s'entraîner, pas pour noter.
"""
import argparse
import base64
import html
import json
import re
import sys
import unicodedata

GUILLEMETS_SIMPLES = re.compile('[’‘`´]')
GUILLEMETS_DOUBLES = re.compile('[“”«»]')


def normaliser(s, mode):
    """Même normalisation que normaliser() dans charte/td-en-ligne.js."""
    s = str(s)
    if mode in ('exact', 'liste'):
        return s.strip()
    if mode == 'nombre':
        t = re.sub(r'\s', '', s).replace(',', '.', 1)
        t = re.sub(r'^\+', '', t)
        m = re.fullmatch(r'(-?)(\d*)(?:\.(\d*))?', t)
        if not m or (m.group(2) == '' and (m.group(3) or '') == ''):
            return t.lower()
        ent = re.sub(r'^0+(?=\d)', '', m.group(2)) or '0'
        dec = (m.group(3) or '').rstrip('0')
        r = ent + ('.' + dec if dec else '')
        return '0' if r == '0' else m.group(1) + r
    s = unicodedata.normalize('NFC', s)
    s = GUILLEMETS_SIMPLES.sub("'", s)
    s = GUILLEMETS_DOUBLES.sub('"', s)
    if mode == 'code':
        return re.sub(r'\s+', '', s.replace("'", '"'))
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if not unicodedata.category(c).startswith('M'))
    s = re.sub(r'\s+', ' ', s.lower()).strip()
    return re.sub(r'\.$', '', s)


def _fnv(octets, h):
    for o in octets:
        h = ((h ^ o) * 0x01000193) & 0xFFFFFFFF
    return h


def empreinte(sel, champ, valeur, mode):
    o = f'{sel}|{champ}|{normaliser(valeur, mode)}'.encode('utf-8')
    return f'{_fnv(o, 0x811C9DC5):08x}{_fnv(o[::-1], 0x050C5D1F):08x}'


BALISE = re.compile(r'<(input|fieldset|ol|textarea)\b[^>]*\bdata-champ="[^"]*"[^>]*>', re.S)
ATTR = re.compile(r'\s(data-[a-z-]+)=(?:"([^"]*)"|\'([^\']*)\')')
COMMENTAIRE = re.compile(r'<!--.*?-->', re.S)


def hors_commentaires(texte, fonction):
    """Applique fonction() au texte, sauf à l'intérieur des commentaires HTML."""
    morceaux, debut = [], 0
    for m in COMMENTAIRE.finditer(texte):
        morceaux.append(fonction(texte[debut:m.start()]))
        morceaux.append(m.group(0))
        debut = m.end()
    morceaux.append(fonction(texte[debut:]))
    return ''.join(morceaux)


def construire(source):
    m = re.search(r'<body\b[^>]*\bdata-sel="([^"]*)"', source)
    if not m:
        raise SystemExit('La balise <body> doit porter data-sel="…".')
    sel = m.group(1)
    vus, erreurs = set(), []

    def remplace_champ(mt):
        tag = mt.group(0)
        attrs = {}
        for a in ATTR.finditer(tag):
            attrs[a.group(1)] = a.group(2) if a.group(2) is not None else a.group(3)
        champ = attrs['data-champ']
        if champ in vus:
            erreurs.append(f'champ en double : {champ}')
        vus.add(champ)
        if 'data-reponses' in attrs:
            reponses = json.loads(html.unescape(attrs['data-reponses']))
        elif 'data-reponse' in attrs:
            reponses = [html.unescape(attrs['data-reponse'])]
        else:
            erreurs.append(f'champ sans réponse : {champ}')
            return tag
        if mt.group(1) in ('fieldset', 'ol'):
            norme = 'liste'
            if mt.group(1) == 'fieldset':
                reponses = [','.join(sorted(x.strip() for x in r.split(','))) for r in reponses]
            else:
                reponses = [','.join(x.strip() for x in r.split(',')) for r in reponses]
        else:
            norme = attrs.get('data-norm') or ('code' if 'tl-trou' in tag else 'souple')
        e = ' '.join(dict.fromkeys(empreinte(sel, champ, r, norme) for r in reponses))
        tag = re.sub(r'\sdata-reponses?=(?:"[^"]*"|\'[^\']*\')', '', tag)
        fin = re.search(r'\s*/?>$', tag)
        return tag[:fin.start()] + f' data-e="{e}">'

    sortie = hors_commentaires(source, lambda t: BALISE.sub(remplace_champ, t))
    n_corr = 0

    def remplace_correction(mt):
        nonlocal n_corr
        n_corr += 1
        b64 = base64.b64encode(mt.group(1).strip().encode('utf-8')).decode('ascii')
        return f'<div class="tl-correction" data-c="{b64}" hidden></div>'

    sortie = hors_commentaires(sortie, lambda t: re.sub(r'<template class="tl-correction">(.*?)</template>',
                                                        remplace_correction, t, flags=re.S))
    sans_comm = COMMENTAIRE.sub('', sortie)
    reste = re.findall(r'data-reponses?=', sans_comm)
    if reste:
        erreurs.append(f'{len(reste)} réponse(s) en clair restée(s) hors d\'un champ reconnu')
    n_q = len(re.findall(r'<form class="tl-q"', sans_comm))
    sans_corr = len(re.findall(r'<form class="tl-q"', sans_comm)) - n_corr
    if sans_corr > 0:
        erreurs.append(f'{sans_corr} question(s) sans correction (<template class="tl-correction">)')
    return sortie, {'champs': len(vus), 'questions': n_q, 'corrections': n_corr}, erreurs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('source', nargs='?')
    ap.add_argument('sortie', nargs='?')
    ap.add_argument('--empreinte', nargs=4, metavar=('SEL', 'CHAMP', 'NORME', 'REPONSE'))
    a = ap.parse_args()
    if a.empreinte:
        print(empreinte(*a.empreinte[:2], a.empreinte[3], a.empreinte[2]))
        return 0
    if not (a.source and a.sortie):
        ap.error('donner SOURCE et SORTIE')
    with open(a.source, encoding='utf-8') as f:
        src = f.read()
    sortie, bilan, erreurs = construire(src)
    for e in erreurs:
        print('ERREUR :', e, file=sys.stderr)
    if erreurs:
        return 1
    entete = ('<!-- Page construite par design/build/td_en_ligne.py à partir de la source : '
              'ne pas la modifier à la main. Les réponses ne sont pas en clair ; '
              'elles restent retrouvables par qui cherche vraiment (outil d\'entraînement). -->\n')
    sortie = sortie.replace('<!doctype html>\n', '<!doctype html>\n' + entete, 1)
    with open(a.sortie, 'w', encoding='utf-8') as f:
        f.write(sortie)
    print(f'{a.sortie} : {bilan["questions"]} questions, {bilan["champs"]} champs, '
          f'{bilan["corrections"]} corrections codées.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
