"""Pages imprimables de l'équipage : planche des 9 cartes et cartes vierges."""
import sys, re
sys.path.insert(0, '/tmp/design/equipage')
from runners import RUNNERS, PROFILS, portrait
OUT = '/home/claude/babash-nsi-snt/charte/'
TOOL = '''<nav class="toolbar" aria-label="Outils"><a class="back" href="./">← Charte graphique</a><button type="button" data-action="projeter" aria-pressed="false"><span class="libelle">Projeter</span></button><button type="button" class="principal" data-action="imprimer">Imprimer</button><span class="aide">Format A4 · échelle 100 % · marges « aucune » · graphiques d'arrière-plan activés · découper le long des pointillés</span></nav>'''
def page(titre, corps, niv='niv-autres'):
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<link rel="stylesheet" href="../assets/charte.css">
<link rel="stylesheet" href="../assets/fiche.css">
<script src="../assets/fiche.js" defer></script>
</head>
<body class="{niv}">
{TOOL}
{corps}
</body>
</html>
'''
def jauge(n): return '◆' * n + '◇' * (3 - n)
cartes = []
for r in RUNNERS:
    p = PROFILS[r['profil']]
    svg = portrait(r, 'trait', uid=r['id'] + '-imp', fond=False)
    svg = re.sub(r'viewBox="0 0 300 360"', 'viewBox="20 40 260 200" preserveAspectRatio="xMidYMid slice"', svg, count=1)
    svg = re.sub(r'<path d="M1\.5 1\.5H281[^>]*/>', '', svg)  # pas de second cadre
    stats = ''.join(f'<span>{k} <b>{jauge(v)}</b></span>' for k, v in r['stats'].items())
    cartes.append(f'''<article class="ci" style="--prof-encre:{p['encre']}"><header class="ci-tete"><span class="ci-glyphe" aria-hidden="true">{p['glyphe']}</span><h2 class="ci-nom">{r['nom']}</h2></header>
<div class="ci-art">{svg}</div><p class="ci-type">Runner · {p['nom']}</p>
<div class="ci-texte"><p class="ci-spe">{r['specialite']}</p><p>{r['capacite']}</p><p class="ci-replique">{r['replique']}</p></div>
<p class="ci-jauges">{stats}</p></article>''')
corps = ('<section class="sheet planche"><div class="run"><span>Ressources NSI et SNT · L\'équipage</span><span>9 cartes · format 63 × 88 mm</span></div>'
         '<div class="sheet-body"><div class="planche-cartes">' + ''.join(cartes) + '</div></div>'
         '<div class="foot"><span>Dessin original · trois profils, chacun avec une femme, un homme et une personne indéterminée</span><span class="pg">1 / 1</span></div></section>')
open(OUT + 'equipage-a-imprimer.html', 'w').write(page("L'équipage — cartes à imprimer", corps))

vierge = '''<article class="ci vierge"><header class="ci-tete"><span class="ci-glyphe">sigle</span><span class="champ">Pseudo<i></i></span></header>
<div class="ci-art"><span>Ton portrait<br>(dessin, avatar, symbole…)</span></div>
<p class="ci-type"><span><span class="cb"></span>Architecte</span><span><span class="cb"></span>Analyste</span><span><span class="cb"></span>Hacker</span></p>
<div class="ci-texte"><p class="ligne"><b>Spécialité</b><i></i></p><p class="ligne"><b>Capacité</b><i></i></p><span class="suite"></span><p class="ligne"><b>Réplique</b><i></i></p></div>
<p class="ci-jauges"><span>Algo <b>◇◇◇</b></span><span>Réseau <b>◇◇◇</b></span><span>Données <b>◇◇◇</b></span></p></article>'''
corps = ('<section class="sheet planche"><div class="run"><span>Ressources NSI et SNT · Ma carte de runner</span><span>4 cartes par page</span></div>'
         '<div class="sheet-body"><div class="box mode inline-label"><div class="box-label">Crée ton runner</div><div class="box-body"><p>Choisis un pseudo et un profil, dessine ton portrait, écris ta spécialité et ta réplique. Les losanges se noircissent au fil de l\'année, quand tu valides des compétences.</p></div></div>'
         '<div class="planche-vierges">' + vierge * 4 + '</div></div>'
         '<div class="foot"><span>Découper le long des pointillés</span><span class="pg">1 / 1</span></div></section>')
open(OUT + 'carte-runner-vierge.html', 'w').write(page('Ma carte de runner — à imprimer', corps))
print('ok')
