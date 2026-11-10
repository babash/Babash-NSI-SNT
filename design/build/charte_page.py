"""Page de référence de la charte : charte/index.html"""
import sys
sys.path.insert(0, '/tmp/design/equipage'); sys.path.insert(0, '/tmp/design/tools')
from runners import RUNNERS, PROFILS
from contrast import cr
SIG = [('cyan','#22D3EE','#0B6378'),('rose','#FF5CA8','#A3155C'),('violet','#A78BFA','#5B2BB5'),('vert','#34D399','#0E6B47'),
       ('orange','#FB923C','#A33A0B'),('bleu','#38BDF8','#0B5A94'),('jaune','#FACC15','#7A5200'),('lavande','#818CF8','#3F3DB8'),
       ('citron','#A3E635','#4B6B0A'),('corail','#F87171','#A61B1B'),('gris','#94A3B8','#4B5567')]
NEUTRES = [('encre','#0B1020','texte courant'),('encre-2','#343E54','texte secondaire'),('encre-3','#586276','légendes, notes'),
           ('trait','#7D879B','traits utiles'),('voile','#F1F3F7','fond du code'),('nuit','#070B16','fond obscur')]
NIV = [('SNT','bleu','niv-snt'),('NSI 1re','violet','niv-1re'),('NSI Tle','orange','niv-tle'),('PP','vert','niv-pp'),('Autres','jaune','niv-autres')]
def sw(nom, neon, encre):
    return (f'<li><span class="pastille" style="background:{neon}"></span><span class="pastille" style="background:{encre}"></span>'
            f'<b>{nom}</b><code>{neon}</code> écran obscur <code>{encre}</code> papier · {cr(encre,"#FFFFFF"):.1f}:1</li>')
def jauge(n): return '◆'*n+'◇'*(3-n)
cartes = ''.join(
    f'<article class="carte-runner" style="--prof:{PROFILS[r["profil"]]["neon"]};--prof-encre:{PROFILS[r["profil"]]["encre"]}">'
    f'<header class="cr-tete"><span class="cr-glyphe" aria-hidden="true">{PROFILS[r["profil"]]["glyphe"]}</span><h3 class="cr-nom">{r["nom"]}</h3></header>'
    f'<div class="cr-art"><img src="../assets/equipage/{r["id"]}-nuit.svg" alt="Portrait de {r["nom"]}" width="300" height="360"></div>'
    f'<p class="cr-type">Runner · {PROFILS[r["profil"]]["nom"]}</p><div class="cr-texte"><p class="cr-spe">{r["specialite"]}</p>'
    f'<p class="cr-replique">{r["replique"]}</p></div><p class="cr-jauges">'
    + ''.join(f'<span>{k} <b>{jauge(v)}</b></span>' for k, v in r['stats'].items()) + '</p></article>' for r in RUNNERS)
html = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Charte graphique — Ressources NSI et SNT</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/charte.css">
<link rel="stylesheet" href="../assets/fiche.css">
<style>
  /* Mise en page de cette page de référence seulement */
  body {{ background: var(--nuit); color: var(--nuit-encre); font: 1rem/1.55 var(--police-texte); }}
  .ref {{ max-width: 72rem; margin: 0 auto; padding: 2rem 1.25rem 5rem; }}
  .ref h1 {{ font: 700 clamp(2.2rem, 6vw, 3.6rem)/1 var(--police-titre); margin: .4rem 0 1rem; }}
  .ref > h2 {{ font: 700 1.7rem/1.15 var(--police-titre); margin: 3.5rem 0 .4rem; padding-left: .8rem; border-left: 4px solid var(--cyan-neon); }}
  .ref > h3 {{ font: 600 1.15rem var(--police-titre); margin: 1.6rem 0 .5rem; color: var(--nuit-encre); }}
  .ref p, .ref li {{ max-width: 48em; color: var(--nuit-encre-2); }}
  .ref b, .ref strong {{ color: var(--nuit-encre); }}
  .ref code {{ background: var(--nuit-2); border-color: var(--nuit-trait); color: var(--nuit-encre); white-space: normal; }}
  .invite {{ font: .85rem var(--police-code); color: var(--cyan-neon); margin: 0; }}
  .regles {{ counter-reset: r; list-style: none; padding: 0; display: grid; gap: .6rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 20rem), 1fr)); }}
  .regles li {{ counter-increment: r; background: var(--nuit-2); border: 1px solid var(--nuit-trait); padding: .8rem 1rem; max-width: none;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%); }}
  .regles li::before {{ content: counter(r, decimal-leading-zero); display: block; font: 700 .8rem var(--police-code); color: var(--cyan-neon); }}
  .nuancier {{ list-style: none; padding: 0; display: grid; gap: .35rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 30rem), 1fr)); }}
  .nuancier li {{ display: flex; align-items: center; gap: .55rem; font-size: .9rem; max-width: none; }}
  .nuancier b {{ min-width: 4.5rem; }}
  .pastille {{ width: 1.5rem; height: 1.5rem; flex: none; border: 1px solid #ffffff33; }}
  .papier {{ background: #fff; color: var(--encre); padding: 1.4rem; margin-top: 1rem; font-size: 10pt;
    clip-path: polygon(0 0, calc(100% - 18px) 0, 100% 18px, 100% 100%, 0 100%); }}
  .papier p, .papier li {{ color: var(--encre); }}
  .papier b {{ color: inherit; }}
  .papier code {{ background: var(--voile); border-color: var(--trait-doux); color: var(--encre); }}
  .papier .stack {{ gap: 3mm; }}
  .typo p {{ margin: .2rem 0; color: var(--nuit-encre); }}
  .cartes {{ display: grid; gap: 1rem; grid-template-columns: repeat(3, minmax(0, 1fr)); max-width: 60rem; }}
  @media (max-width: 700px) {{ .cartes {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  .carte-runner .cr-art img {{ width: 100%; height: auto; display: block; }}
  table.t {{ border-collapse: collapse; font-size: .9rem; }}
  table.t th, table.t td {{ border: 1px solid var(--nuit-trait); padding: .4rem .6rem; text-align: left; vertical-align: top; color: var(--nuit-encre-2); }}
  table.t th {{ color: var(--nuit-encre); font-family: var(--police-titre); }}
  a {{ color: var(--cyan-neon); }}
</style>
</head>
<body>
<main class="ref">
<p class="invite">~/charte</p>
<h1>Charte « Réseau la nuit »</h1>
<p>Une seule identité pour le site et pour les documents imprimés : un univers de runners et de réseau la nuit, inspiré du cyberpunk, entièrement dessiné pour ce site. Le décor sert la pédagogie et ne passe jamais devant le contenu.</p>

<h2>Les règles d'or</h2>
<ol class="regles">
<li><b>La pédagogie d'abord.</b> Une fiche tient en une ou deux pages, un TD en quatre au plus. Le décor reste dans les marges et les en-têtes.</li>
<li><b>Contraste.</b> Texte courant ≥ 7:1, petit texte ≥ 4,5:1, traits utiles ≥ 3:1. Vérifié au vidéoprojecteur.</li>
<li><b>Jamais la couleur seule.</b> Chaque type d'encadré a un mot, une icône et un style de trait : la photocopie en noir et blanc garde le sens.</li>
<li><b>Papier blanc, encre foncée.</b> Pas de grand aplat sombre sur un document à imprimer. Les néons sont réservés à l'écran obscur.</li>
<li><b>Tailles minimales sur A4.</b> Texte 10 pt (9,7 pt pour un document dense), code 8 pt, notes 7,6 pt. Rien en dessous.</li>
<li><b>Équité.</b> L'équipage compte autant de femmes, d'hommes et de personnes indéterminées. Les exemples et les personnages historiques alternent.</li>
<li><b>Écriture.</b> Formulations épicènes (« les élèves », « chaque runner ») et double flexion ; pas de point médian (circulaire du 5 mai 2021).</li>
<li><b>Dessin original.</b> Aucun personnage, logo ou cadre de carte d'un jeu existant. Les runners de l'équipage sont propres au site.</li>
</ol>

<h2>Couleurs</h2>
<h3>Neutres</h3>
<ul class="nuancier">{''.join(f'<li><span class="pastille" style="background:{h}"></span><b>{n}</b><code>{h}</code> {u}</li>' for n,h,u in NEUTRES)}</ul>
<h3>Signaux : un néon pour l'écran obscur, une encre pour le papier</h3>
<ul class="nuancier">{''.join(sw(*s) for s in SIG)}</ul>
<h3>Couleur de niveau</h3>
<p>Classe du <code>&lt;body&gt;</code> d'un document : {', '.join(f'<b>{n}</b> <code>{c}</code> ({col})' for n,col,c in NIV)}. Elle colore les termes clés, les numéros d'exercice et les filets.</p>

<h2>Typographie</h2>
<div class="typo">
<p style="font: 700 2rem var(--police-titre)">Chakra Petch — titres, étiquettes, numéros</p>
<p style="font: 1.1rem var(--police-texte)">Atkinson Hyperlegible — le texte : conçue pour les lecteurs malvoyants, elle distingue I, l et 1, O et 0.</p>
<p style="font: 1rem var(--police-code)">JetBrains Mono — le code : for i in range(10): print(i)</p>
</div>
<p>Les trois polices sont dans <code>assets/fonts/</code> (licence SIL OFL) : aucun appel à Google Fonts, le site et les fiches fonctionnent hors ligne.</p>

<h2>Composants des documents</h2>
<p>Feuille commune : <code>assets/fiche.css</code>. Modèle à copier : <a href="../snt/fichiers/python-compute-it.html">la fiche Python de SNT</a> (2 pages) ; document long : <a href="../nsi-terminale/fichiers/td1-poo-premiers-pas.html">le TD 1 de POO</a>.</p>
<p>Modèle de fiche et de TD (proposition T38) : <a href="gabarit-td.html">gabarit de TD papier</a> (3 pages, 4 au plus), <a href="gabarit-td-en-ligne.html">sa version en ligne auto-corrective</a>, <a href="gabarit-fiche.html">gabarit de fiche</a> (2 pages). Contenu factice.</p>
<div class="papier niv-snt"><div class="stack">
<header class="exo"><div class="exo-num"><span>Exercice</span><b>1</b></div><div class="exo-title"><p class="type">Run 01 · ◆◇◇</p><h2>Titre de l'exercice</h2><p class="skill">Compétence travaillée</p></div><div class="chip">10 min</div></header>
<div class="cols">
<div class="box cours"><div class="box-label"><span>L'essentiel <b>Une notion</b></span></div><div class="box-body"><p>Trait plein, haut épais, vert : le cours à retenir.</p></div></div>
<div class="box def"><div class="box-label">Définition</div><div class="box-body"><p>Barre à gauche, vert : un mot du vocabulaire.</p></div></div>
<div class="box methode"><div class="box-label">Méthode</div><div class="box-body"><p>Double barre, bleu : la démarche pas à pas.</p></div></div>
<div class="box eureka"><div class="box-label">Eurêka</div><div class="box-body"><p>Tirets, violet : l'idée à retenir.</p></div></div>
<div class="box hint"><div class="box-label">Coup de pouce</div><div class="box-body"><p>Pointillés, ambre : une aide pour avancer.</p></div></div>
<div class="box attention"><div class="box-label">Attention</div><div class="box-body"><p>Barre hachurée, rouge : l'erreur classique.</p></div></div>
</div>
<div class="q"><div class="q-n">1</div><div class="q-b"><p>Une question numérotée, suivie de lignes de réponse pointées :</p><div class="lines" style="--n:2"></div></div></div>
<div class="code"><pre><span class="l" data-n="1"><span class="k">for</span> i <span class="ow">in</span> <span class="nb">range</span>(<span class="mi">3</span>):  <span class="c1"># mots-clés en gras</span></span><span class="l" data-n="2">    <span class="nb">print</span>(<span class="s2">"run"</span>, i)</span></pre></div>
</div></div>

<h2>L'équipage</h2>
<p>Neuf runners originaux. Trois profils : <b>Architecte</b> (construire des programmes), <b>Analyste</b> (données et réseaux), <b>Hacker</b> (trouver la faille, puis la réparer). Dans chaque profil : une femme, un homme et une personne indéterminée. Chaque document est guidé par un runner (bloc titre) et ses coups de pouce peuvent être signés.</p>
<p>Pour que chaque élève devienne runner : <a href="carte-runner-vierge.html">Ma carte de runner</a> (4 cartes à remplir par page) et <a href="equipage-a-imprimer.html">les 9 cartes de l'équipage</a> au format carte à jouer, au trait, pour une impression en noir et blanc.</p>
<div class="cartes">{cartes}</div>
<h3>Répartition dans les documents</h3>
<table class="t"><tr><th>Document</th><th>Runner guide</th><th>Coup de pouce signé</th></tr>
<tr><td>SNT · Fiche Python et Compute-it débranché</td><td>Kestrel (architecte, elle)</td><td>Mwezi (analyste, indéterminé)</td></tr>
<tr><td>NSI Tle · TD 1 de POO</td><td>Vector (architecte, il)</td><td>—</td></tr>
<tr><td>NSI Tle · TD 2 de POO</td><td>Nova (analyste, elle)</td><td>—</td></tr>
<tr><td>Prochains documents</td><td colspan="2">Les runners pas encore utilisés en priorité : Pixel, Byte, Nyota, Mistral, Zéro.</td></tr></table>

<h2>Fichiers</h2>
<table class="t">
<tr><th>Fichier</th><th>Rôle</th></tr>
<tr><td><code>assets/charte.css</code></td><td>Polices et couleurs communes, carte de runner. Chargé par toutes les pages.</td></tr>
<tr><td><code>assets/style.css</code></td><td>Le site (accueil, rubriques), affichage clair et obscur.</td></tr>
<tr><td><code>assets/fiche.css</code>, <code>assets/fiche.js</code></td><td>Documents A4 : encadrés, exercices, code, barre d'outils (Retour, Projeter, Imprimer).</td></tr>
<tr><td><code>assets/equipage/</code>, <code>assets/equipage.js</code></td><td>Portraits des runners (nuit et trait) et section « L'équipage » de l'accueil.</td></tr>
</table>
<p style="margin-top:2rem"><a href="../">← Retour au site</a></p>
</main>
</body>
</html>
'''
open('/home/claude/babash-nsi-snt/charte/index.html', 'w').write(html)
print('ok')
