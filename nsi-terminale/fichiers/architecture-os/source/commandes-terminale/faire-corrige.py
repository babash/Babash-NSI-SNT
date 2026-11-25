#!/usr/bin/env python3
"""Fait le corrigé de l'enseignant·e à partir des feuilles du TD : il ne s'écrit jamais à la main,
il ne peut donc pas diverger des pages. Une même copie de ce script sert en première et en terminale.

Usage : python3 -I faire-corrige.py SORTIE.html "Titre" feuille-1.html [feuille-2.html …]
Pour chaque feuille, dans l'ordre du papier : les parties, puis chaque question imprimée, numérotée
comme sur la feuille papier, avec sa correction ; pour une question qui se corrige en ligne, les
réponses acceptées (les variantes écrites autrement) et les erreurs fréquentes prévues.
"""
import html
import os
import re
import sys

sortie, titre, feuilles = sys.argv[1], sys.argv[2], sys.argv[3:]
corps = []
for f in feuilles:
    t = open(f, encoding='utf-8').read()
    main = re.search(r'<main([^>]*)>', t).group(1)
    n = int((re.search(r'data-premiere-question-papier="(\d+)"', main) or re.search(r'data-premiere-question="(\d+)"', main) or [0, '1'])[1])
    acc = re.search(r'<p class="td-accroche">(.*?)</p>', t).group(1)
    corps.append('<h2>Feuille %d : %s</h2>' % (feuilles.index(f) + 1, acc))
    zone = t[t.index('</header>'):t.index('<footer')]
    # les sections et les titres de partie, dans l'ordre
    for m in re.finditer(r'<h2 class="td-partie">(.*?)</h2>|<section class="td-q"([^>]*)>(.*?)</section>', zone, re.S):
        if m.group(1):
            corps.append('<h3>%s</h3>' % m.group(1))
            continue
        attrs, s = m.group(2), m.group(3)
        if 'data-support="ecran"' in attrs:
            continue
        consigne = re.search(r'<p class="td-consigne">(.*?)</p>', s, re.S).group(1)
        corr = re.search(r'<div class="td-correction">(.*)</div>', s, re.S)
        corr = corr.group(1) if corr else ''
        bloc = ['<div class="q"><p class="c"><b>Question %d.</b> %s</p>' % (n, consigne)]
        rep = re.search(r'data-reponse="([^"]*)"', attrs)
        # la jumelle d'écran (QCU) d'une question papier : sa correction explique les autres options
        if not rep and 'data-support="papier"' in attrs:
            qid = re.search(r'id="([^"]+)"', attrs).group(1)
            jum = re.search(r'<section class="td-q"[^>]*id="%s"[^>]*>(.*?)</section>' % re.escape(qid[:-1] if qid.endswith('p') else qid.replace('-papier', '')), zone, re.S)
            if jum and qid != 't1-papier':
                jc = re.search(r'<div class="td-correction">(.*)</div>', jum.group(1), re.S)
                if jc:
                    corr = jc.group(1)
        corr = re.sub(r'<p class="td-erreur-frequente" data-si="([^"]*)"><b>Erreur fréquente :</b> <code>[^<]*</code> : ',
                      lambda e: '<p class="e"><b>Erreur fréquente :</b> <code>%s</code> : ' % html.escape(html.unescape(e.group(1)).replace('|', '  ou  ')), corr)
        bloc.append('<div class="r">%s</div>' % corr)
        if rep:
            variantes = html.unescape(rep.group(1)).split('|')
            if len(variantes) > 1:
                bloc.append('<p class="v">Acceptées en ligne : %s</p>' % ' · '.join('<code>%s</code>' % html.escape(v) for v in variantes))
        bloc.append('</div>')
        corps.append(''.join(bloc))
        n += 1

page = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titre)s : corrigé</title>
<meta name="description" content="Le corrigé de l'enseignant·e, fait à partir des feuilles en ligne (numéros du papier), avec les réponses acceptées en ligne et les erreurs fréquentes.">
<script>try { var t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t); } catch (e) { }</script>
<link rel="icon" href="../../../assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../../../assets/signal-commun.css">
<style>
body { background: var(--td-fond); color: var(--td-encre); font-family: "Atkinson Hyperlegible", sans-serif; margin: 0; line-height: 1.45; }
main { max-width: 52rem; margin: 0 auto; padding: 1rem; }
h1 { font-family: Anton, sans-serif; font-weight: 400; letter-spacing: .02em; margin: .2rem 0; }
h2 { font-family: Anton, sans-serif; font-weight: 400; border-bottom: 2px solid var(--td-encre); margin-top: 1.6rem; }
h2, h3 { break-after: avoid; }
h3 { margin: 1.1rem 0 .4rem; }
code, pre { font-family: "JetBrains Mono", monospace; overflow-wrap: anywhere; }
pre { background: var(--td-code-fond); padding: .4rem .6rem; overflow-x: auto; white-space: pre; }
.q { border-left: 3px solid var(--td-encre); padding: .1rem 0 .1rem .7rem; margin: .7rem 0; break-inside: avoid; }
.c { margin: .2rem 0; }
.r p, .v, .e { margin: .25rem 0; }
.v, .e { font-size: .95em; }
.avert { border: 1px dashed var(--td-encre); padding: .4rem .7rem; }
footer { border-top: 1px solid var(--td-encre); margin-top: 2rem; padding-top: .5rem; font-size: .9em; }
a { color: inherit; }
@media print { body { background: #fff; color: #000; } main { max-width: none; padding: 0; } @page { size: A4; margin: 14mm 14mm 16mm; } pre { white-space: pre-wrap; } }
</style>
</head>
<body>
<main>
<p>Corrigé de l'enseignant·e · %(niveau)s · Systèmes d'exploitation</p>
<h1>%(titre)s</h1>
<p class="avert">Les numéros sont ceux des feuilles <b>papier</b>. En ligne, chaque question se corrige toute seule : la page dit si c'est juste, puis propose la correction après deux essais. Ce corrigé est fait par un script à partir des feuilles (<code>source/faire-corrige.py</code>) : il ne peut pas en diverger.</p>
%(corps)s
<footer><p>Babash - NSI Tani Malandi · Texte sous licence <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">CC BY-SA 4.0</a> · conçu avec l'aide de l'IA · <a href="https://github.com/babash/Babash-NSI-SNT/tree/main/%(dossier)s">Code source sur GitHub</a></p></footer>
</main>
</body>
</html>
'''
racine = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sortie)), '..', '..', '..'))
dossier = os.path.relpath(os.path.dirname(os.path.abspath(sortie)), racine)
niveau = '1re NSI' if 'premiere' in dossier else 'Tle NSI'
open(sortie, 'w', encoding='utf-8').write(page % {'titre': titre, 'niveau': niveau, 'corps': '\n'.join(corps), 'dossier': dossier})
print(sortie, ':', sum(1 for c in corps if c.startswith('<div class="q">')), 'questions')
