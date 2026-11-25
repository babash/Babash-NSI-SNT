#!/usr/bin/env python3
"""Fait le corrigé de l'enseignant·e à partir des feuilles du TD : il ne s'écrit jamais à la main,
il ne peut donc pas diverger des pages. Une même copie de ce script sert en première et en terminale.

Usage : python3 -I faire-corrige.py SORTIE.html "Titre" feuille-1.html [feuille-2.html …]
Pour chaque feuille : les parties, puis chaque question, avec son numéro (le même sur papier et à l'écran)
et sa correction (pour un choix, l'explication de chaque option fausse ; pour une question « sortie », la
sortie attendue) ; pour une question qui se corrige en ligne, le nombre d'écritures acceptées et quelques-unes,
et la question que la page pose après chaque erreur prévue.
"""
import html
import os
import re
import sys

sortie, titre, feuilles = sys.argv[1], sys.argv[2], sys.argv[3:]
corps = []


def court(v):
    return '<code>%s</code>' % html.escape(v)


for f in feuilles:
    t = open(f, encoding='utf-8').read()
    main = re.search(r'<main([^>]*)>', t).group(1)
    n = int((re.search(r'data-premiere-question="(\d+)"', main) or [0, '1'])[1])
    acc = re.search(r'<p class="td-accroche">(.*?)</p>', t).group(1)
    corps.append('<h2>Feuille %d : %s</h2><div class="feuille">' % (feuilles.index(f) + 1, acc))
    zone = t[t.index('</header>'):t.index('<footer')]
    ecran = {}
    for m in re.finditer(r'<h2 class="td-partie">(.*?)</h2>|<section class="td-q"([^>]*)>(.*?)</section>', zone, re.S):
        if m.group(1):
            corps.append('<h3>%s</h3>' % m.group(1))
            continue
        attrs, s = m.group(2), m.group(3)
        qid = re.search(r'id="([^"]+)"', attrs).group(1)
        if 'data-support="ecran"' in attrs:
            ecran[qid] = s          # sa jumelle papier suit : elle porte le numéro
            continue
        if 'data-support="papier"' in attrs and qid[:-1] in ecran:
            s = ecran[qid[:-1]]     # la version d'écran : sa consigne complète, et la correction de chaque option
        consigne = re.search(r'<p class="td-consigne">(.*?)</p>', s, re.S).group(1)
        corr = re.search(r'<div class="td-correction">(.*)</div>', s, re.S)
        corr = corr.group(1) if corr else ''
        att = re.search(r'<pre class="td-attendu">\n?(.*?)</pre>', s, re.S)
        if att:      # question « sortie » : la sortie attendue, en clair
            corr = '<pre>%s</pre>' % att.group(1) + corr
        bloc = ['<div class="q"><p class="c"><b>%d.</b> %s</p><div class="r">%s</div>' % (n, consigne, corr)]
        rep = re.search(r'data-reponse="([^"]*)"', attrs)
        if rep:
            variantes = html.unescape(rep.group(1)).split('|')
            if len(variantes) > 1:
                bloc.append('<p class="v">Acceptées en ligne : %d écritures, dont %s.</p>' % (len(variantes), ', '.join(court(v) for v in variantes[1:5])))
        for si, question in re.findall(r'<p class="td-retour" data-si="([^"]*)">(.*?)</p>', s, re.S):
            fausses = html.unescape(si).split('|')
            autres = ' (et %d autres)' % (len(fausses) - 1) if len(fausses) > 1 else ''
            bloc.append('<p class="e">Après %s%s, la page demande : « %s »</p>' % (court(fausses[0]), autres, question))
        bloc.append('</div>')
        corps.append(''.join(bloc))
        n += 1
    corps.append('</div>')

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
.q { border-left: 3px solid var(--td-encre); padding: .1rem 0 .1rem .6rem; margin: .5rem 0; break-inside: avoid; }\n.v, .e { font-size: .88em; }
.c { margin: .2rem 0; }
.r p, .v, .e { margin: .25rem 0; }
.v, .e { font-size: .95em; }
.avert { border: 1px dashed var(--td-encre); padding: .4rem .7rem; }
footer { border-top: 1px solid var(--td-encre); margin-top: 2rem; padding-top: .5rem; font-size: .9em; }
a { color: inherit; }
@media print { body { background: #fff; color: #000; font-size: 9.5pt; line-height: 1.32; } main { max-width: none; padding: 0; } @page { size: A4; margin: 11mm 12mm 13mm; } pre { white-space: pre-wrap; margin: .15rem 0; } .q { margin: .3rem 0; } .r p, .v, .e { margin: .1rem 0; } h2 { margin-top: .8rem; } h3 { margin: .5rem 0 .2rem; } }
</style>
</head>
<body>
<main>
<p>Corrigé de l'enseignant·e · %(niveau)s · Systèmes d'exploitation</p>
<h1>%(titre)s</h1>
<p class="avert">Les numéros sont les mêmes sur papier et à l'écran. En ligne, la page dit si c'est juste ; après un essai faux prévu, elle pose une question (ci-dessous, « la page demande ») ; la correction vient après deux essais.</p>
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
