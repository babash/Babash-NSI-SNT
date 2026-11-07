"""Fiche Python SNT, mise à la charte. Contenu inchangé (texte identique)."""
import sys
sys.path.insert(0, '/tmp/design/equipage')
from runners import RUNNERS, portrait

R = {r['id']: r for r in RUNNERS}
kestrel = portrait(R['kestrel'], 'trait', uid='k1')
mwezi = portrait(R['mwezi'], 'trait', uid='m1', badge=True)

def code(lignes, debut=1, cls=''):
    """lignes : liste de chaînes déjà balisées."""
    out = ['<div class="code %s"><pre>' % cls]
    for i, l in enumerate(lignes):
        out.append('<span class="l" data-n="%d">%s</span>' % (debut + i, l))
    out.append('</pre></div>')
    return ''.join(out)

K = lambda m: '<span class="k">%s</span>' % m
F = lambda m: '<span class="nf">%s</span>' % m
NB = lambda m: '<span class="nb">%s</span>' % m
MI = lambda m: '<span class="mi">%s</span>' % m
C = lambda m: '<span class="c1">%s</span>' % m
IND = '<span class="ind">│</span>   '

def grille(rouges=(), depart=None, nom=''):
    lettres = 'ABCDE'
    h = ['<div class="ci" role="img" aria-label="Grille %s : départ %s, cases rouges %s">' % (nom, depart, ', '.join(rouges) or 'aucune')]
    h.append('<span></span>' + ''.join('<span class="ci-l">%s</span>' % l for l in lettres))
    for ligne in range(1, 6):
        h.append('<span class="ci-l">%d</span>' % ligne)
        for l in lettres:
            case = '%s%d' % (l, ligne)
            c = 'ci-c'
            if case in rouges: c += ' rouge'
            if case == depart: c += ' depart'
            h.append('<span class="%s"></span>' % c)
    h.append('</div>')
    return ''.join(h)

ICONE_LIVRE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v16"/><path d="M20 19a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-4a5 5 0 0 0-4 2 5 5 0 0 0-4-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4a5 5 0 0 1 4 2 5 5 0 0 1 4-2z"/></svg>'
ICONE_ALERTE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3"/><path d="M12 9v4M12 17h.01"/></svg>'
ICONE_IDEE = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/></svg>'
ICONE_RETOUR = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 19-7-7 7-7M19 12H5"/></svg>'
ICONE_IMPR = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 9V3h12v6"/><rect x="6" y="14" width="12" height="8"/></svg>'
ICONE_PROJ = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="14"/><path d="M8 21h8M12 17v4"/></svg>'

html = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Python : fiche de révision et TD débranché Compute-it — SNT</title>
<link rel="stylesheet" href="../../assets/charte.css">
<link rel="stylesheet" href="../../assets/fiche.css">
<script src="../../assets/fiche.js" defer></script>
<style>
/* Propre à cette fiche : la grille Compute-it et les guides d'indentation */
.ci {{ display: grid; grid-template-columns: 4mm repeat(5, 6.6mm); grid-auto-rows: 6.6mm; gap: .7mm;
  font: 600 7.6pt var(--police-titre); color: var(--encre-2); align-items: center; justify-items: center; }}
.ci > span:nth-child(-n+6) {{ height: 4mm; align-self: end; }}
.ci-c {{ width: 100%; height: 100%; border: .3mm solid var(--trait); border-radius: 50%; background: #fff; position: relative; }}
.ci-c.rouge {{ border: .45mm solid var(--attention);
  background: repeating-linear-gradient(45deg, var(--attention) 0 .5mm, #F7C9D3 .5mm 1.4mm); }}
.ci-c.depart::after {{ content: ""; position: absolute; inset: 1.3mm; border-radius: 50%;
  border: .7mm solid var(--encre); background: #fff; }}
.ci.petite {{ grid-template-columns: 3.4mm repeat(5, 4.6mm); grid-auto-rows: 4.6mm; gap: .6mm; font-size: 7pt; }}
.ind {{ color: var(--niv); font-weight: 700; }}
.rep {{ display: grid; grid-template-columns: auto 1fr; gap: 1.1mm 2mm; align-items: end; font-size: 9.4pt; }}
.rep .write-line {{ min-width: 0; width: 100%; }}
.prog-nom {{ font: 700 9.6pt var(--police-titre); margin: 0 0 1mm; }}
kbd {{ font: 600 .85em var(--police-code); border: .3mm solid var(--encre-2); border-bottom-width: .7mm; padding: 0 1.2mm; }}
.ex-court {{ border: .3mm solid var(--trait); padding: 2mm 2.6mm; }}
.ex-court .exo {{ margin-bottom: 1.6mm; }}
.exo.mini .exo-num {{ min-width: 12mm; }}
.exo.mini .exo-num b {{ font-size: 15pt; }}
.exo.mini .exo-title h2 {{ font-size: 12pt; }}
.exo.mini {{ padding-bottom: 1.2mm; }}
.exo.mini .exo-num {{ padding: .6mm 1.6mm .8mm; }}
.exo .droite {{ display: flex; flex-direction: column; align-items: flex-end; justify-content: center; gap: 1mm; }}
.exo .droite .type {{ margin: 0; font: 600 7.4pt var(--police-titre); letter-spacing: .14em; text-transform: uppercase; color: var(--niv); white-space: nowrap; }}
.sheet-body {{ gap: 1.5mm; }}
.exo.mini .skill {{ font-size: 9pt; }}
.tb-runner {{ width: 19mm; }}
.rep.quatre {{ grid-template-columns: auto 1fr auto 1fr; }}
.ex-court {{ padding: 1.4mm 2.4mm; }}
.box.hint.signe {{ padding: 1.2mm 2.6mm; }}
.signe.compact > .runner-badge {{ width: 9mm; height: 9mm; }}
.signe.compact .qui {{ display: inline; margin-left: 2mm; }}
.focus {{ font-size: 8.9pt; }}
.code pre {{ font-size: 8.4pt; }}
.ex-court .code pre {{ line-height: 1.32; }}
.rep.ligne {{ grid-template-columns: auto 1fr auto 1fr auto 1fr; }}
.tb.compact .tb-main {{ padding: 1.8mm 4mm 1.4mm; }}
.tb.compact .tb-td {{ font-size: 20pt; min-width: 20mm; }}
.tb.compact h1 {{ font-size: 16pt; }}
</style>
</head>
<body class="niv-snt">

<nav class="toolbar" aria-label="Outils">
  <a class="back" href="../index.html#programmation">{ICONE_RETOUR} Ressources SNT</a>
  <button type="button" data-action="projeter" aria-pressed="false">{ICONE_PROJ} <span class="libelle">Projeter</span></button>
  <button type="button" class="principal" data-action="imprimer">{ICONE_IMPR} Imprimer recto-verso</button>
  <span class="aide">A4 · échelle 100 % · marges « aucune » · graphiques d'arrière-plan activés</span>
</nav>

<!-- ═══ RECTO : FICHE DE RÉVISION ═══ -->
<section class="sheet"><div class="sheet-body">

<header class="tb">
  <div class="tb-top"><span>SNT · Seconde</span><span>Notions transversales de programmation</span></div>
  <div class="tb-main">
    <div class="tb-td"><div><small>Fiche</small>Py</div></div>
    <div class="tb-titles">
      <h1>Python : fiche de révision</h1>
      <p>Les bases de l'algorithmique et du suivi de programme pas à pas.</p>
      <div class="tb-meta"><span class="tag">Recto · cours</span><span class="tag">Verso · activité débranchée</span></div>
    </div>
    <div class="tb-runner">{kestrel}<span>Kestrel · architecte</span></div>
  </div>
</header>

<div class="box cours">
  <div class="box-label">{ICONE_LIVRE}<span>Règle fondamentale <b>L'indentation : la portée du code</b></span></div>
  <div class="cols c64" style="align-items:center">
    <div>
      <p>En Python, l'<b>indentation</b> (décalage de <b>4 espaces</b> ou 1 touche <kbd>Tab</kbd>) définit le <b>bloc d'instructions</b> rattaché à une structure.</p>
      <p><b>Toute ligne indentée fait partie du bloc. Dès qu'on revient vers la gauche, on <u>sort</u> du bloc !</b></p>
    </div>
    {code([K('for') + ' i ' + K('in') + ' ' + NB('range') + '(' + MI('2') + '):',
           IND + F('droite') + '()  ' + C('# DANS la boucle'),
           IND + F('bas') + '()     ' + C('# DANS la boucle'),
           F('haut') + '()         ' + C('# HORS de la boucle !')], cls='nonum')}
  </div>
  <div class="box attention" style="margin-top:1.6mm"><div class="box-label inline">{ICONE_ALERTE}<span>N'oubliez jamais les deux-points <code>:</code> en fin de ligne de commande !</span></div></div>
</div>

<div class="cols stretch">
  <div class="box notion"><div class="box-label"><span class="n">1</span><span>Conditions : <code>if</code> / <code>elif</code> / <code>else</code></span></div>
    <p>Exécute un bloc <b>SI</b> une condition est vraie. Sinon, passe à la suite ou au <code>else</code>.</p>
    {code([K('if') + ' ' + F('rouge') + '():', '    ' + F('bas') + '()', K('elif') + ' ' + F('bleu') + '():', '    ' + F('haut') + '()', K('else') + ':', '    ' + F('droite') + '()'], cls='nonum')}
    <p class="small" style="margin:1.4mm 0 0">Dès qu'une condition est vraie, les suivantes sont ignorées.</p>
  </div>
  <div class="box notion"><div class="box-label"><span class="n">2</span><span>Opérateurs logiques</span></div>
    <p>Combine ou inverse des conditions pour affiner les tests.</p>
    <ul class="tight">
      <li><code>not rouge()</code> : vrai si la case n'est <b>PAS</b> rouge.</li>
      <li><code>rouge() and bleu()</code> : vrai si <b>les DEUX</b> conditions sont vraies.</li>
      <li><code>rouge() or bleu()</code> : vrai si <b>AU MOINS UNE</b> condition est vraie.</li>
    </ul>
    <p class="small" style="margin:1.4mm 0 0">Exemple : <code>while not rouge():</code> (avancer tant qu'on n'est pas sur du rouge).</p>
  </div>
  <div class="box notion"><div class="box-label"><span class="n">3</span><span>Boucle non bornée : <code>while</code></span></div>
    <p>Répète le bloc <b>TANT QUE</b> la condition reste vraie. Le nombre de tours est inconnu au départ.</p>
    {code([K('while') + ' ' + F('rouge') + '():', '    ' + F('droite') + '()', '    ' + F('bas') + '()'], cls='nonum')}
    <div class="box hint" style="margin-top:1.6mm"><span class="box-label">{ICONE_IDEE}Point clé Compute-it</span><span class="box-body">La condition n'est testée qu'<b>au début de chaque tour</b>, jamais au milieu du bloc !</span></div>
  </div>
  <div class="box notion"><div class="box-label"><span class="n">4</span><span>Boucle bornée : <code>for</code></span></div>
    <p>Répète le bloc un nombre de fois <b>fixe et connu</b> à l'avance grâce à <code>range(N)</code>.</p>
    {code([K('for') + ' i ' + K('in') + ' ' + NB('range') + '(' + MI('3') + '):', '    ' + F('droite') + '()', '    ' + F('haut') + '()'], cls='nonum')}
    <p class="small" style="margin:1.4mm 0 0">Ici, la séquence (droite puis haut) sera exécutée exactement 3 fois.</p>
  </div>
</div>

<div class="box methode">
  <div class="box-label">Focus : fonctionnement détaillé des 3 structures de contrôle</div>
  <div class="cols trois focus">
    <div><b>Structure conditionnelle</b>
      <ul class="tight">
        <li><code>if</code> : teste la condition 1. Si elle est vraie, son bloc s'exécute et tout le reste du bloc d'aiguillage est ignoré.</li>
        <li><code>elif</code> (sinon si) : utilisé si la condition 1 est fausse. On peut en mettre autant que nécessaire.</li>
        <li><code>else</code> (sinon) : optionnel. S'exécute uniquement si <u>toutes</u> les conditions précédentes sont fausses.</li>
      </ul></div>
    <div><b>Boucle répétitive (<code>for</code>)</b>
      <ul class="tight">
        <li><b>Nombre de tours connu</b> : on sait à l'avance combien de fois le bloc va tourner grâce à <code>range(N)</code>.</li>
        <li><b>Compteur interne</b> : la variable <code>i</code> prend automatiquement les valeurs de <code>0</code> à <code>N-1</code>.</li>
        <li><b>Utilisation</b> : idéal pour parcourir une grille sur une distance fixe ou effectuer une action un nombre précis de fois.</li>
      </ul></div>
    <div><b>Boucle conditionnelle (<code>while</code>)</b>
      <ul class="tight">
        <li><b>Nombre de tours inconnu</b> : le programme répète le bloc tant que l'état du plateau satisfait la condition.</li>
        <li><b>Test à l'entrée</b> : si la condition est fausse dès le début, le bloc n'est <u>jamais</u> exécuté.</li>
        <li><b>Risque de boucle infinie</b> : si la condition reste toujours vraie, le programme ne s'arrête jamais !</li>
      </ul></div>
  </div>
</div>

</div><div class="foot"><span>Fiche de révision · SNT · Python</span><span class="pg">1 / 2</span></div></section>

<!-- ═══ VERSO : ACTIVITÉ DÉBRANCHÉE ═══ -->
<section class="sheet"><div class="run"><span>SNT · Seconde — Python : fiche de révision</span><span>Verso · activité débranchée</span></div><div class="sheet-body">

<header class="tb compact">
  <div class="tb-main">
    <div class="tb-td"><div><small>Activité</small>CI</div></div>
    <div class="tb-titles">
      <h1>Compute-it débranché</h1>
      <p>Suivez chaque programme case par case, sans ordinateur. Notez les touches appuyées et la case d'arrivée.</p>
      <div class="tb-meta"><span class="field">Nom, prénom<i></i></span><span class="field short">Classe<i></i></span><span class="field short">Date<i></i></span></div>
    </div>
  </div>
</header>

<div class="ex-court">
  <header class="exo mini"><div class="exo-num"><span>Exercice</span><b>1</b></div><div class="exo-title"><h2>L'indentation change tout !</h2><p class="skill">Les deux programmes ont les mêmes lignes mais pas la même indentation. Suivez le cheminement !</p></div><div class="droite"><p class="type">Run 01 · ◆◇◇</p><div class="chip">Départ : A5</div></div></header>
  <div class="cols">
    <div><p class="prog-nom">Programme A</p>{code([K('for') + ' i ' + K('in') + ' ' + NB('range') + '(' + MI('3') + '):', '    ' + F('droite') + '()', '    ' + F('haut') + '()'])}
      <div class="rep" style="margin-top:1.6mm"><span>Touches appuyées :</span><span class="write-line"></span><span>Case d'arrivée :</span><span class="write-line"></span></div></div>
    <div><p class="prog-nom">Programme B</p>{code([K('for') + ' i ' + K('in') + ' ' + NB('range') + '(' + MI('3') + '):', '    ' + F('droite') + '()', F('haut') + '()'])}
      <div class="rep" style="margin-top:1.6mm"><span>Touches appuyées :</span><span class="write-line"></span><span>Case d'arrivée :</span><span class="write-line"></span></div></div>
  </div>
</div>

<div class="ex-court">
  <header class="exo mini"><div class="exo-num"><span>Exercice</span><b>2</b></div><div class="exo-title"><h2>Une boucle dans une boucle (boucles imbriquées)</h2><p class="skill">La boucle intérieure s'exécute entièrement à chaque tour de la boucle extérieure.</p></div><div class="droite"><p class="type">Run 02 · ◆◆◇</p><div class="chip">Départ : A1</div></div></header>
  <div class="cols" style="grid-template-columns:62mm 1fr;align-items:center">
    {code([K('for') + ' i ' + K('in') + ' ' + NB('range') + '(' + MI('2') + '):', '    ' + K('for') + ' j ' + K('in') + ' ' + NB('range') + '(' + MI('2') + '):', '        ' + F('droite') + '()', '    ' + F('bas') + '()'])}
    <div class="box eureka"><div class="box-label">Réponses exercice 2</div>
      <div class="cols" style="gap:4mm"><div class="rep"><span>Nb d'exécutions de <code>droite()</code> :</span><span class="write-line"></span><span>Nb d'exécutions de <code>bas()</code> :</span><span class="write-line"></span></div><div class="rep"><span>Touches :</span><span class="write-line"></span><span>Case d'arrivée :</span><span class="write-line"></span></div></div></div>
  </div>
</div>

<div class="ex-court">
  <header class="exo mini"><div class="exo-num"><span>Exercice</span><b>3</b></div><div class="exo-title"><h2><code>if</code> et <code>else</code> dans une boucle</h2><p class="skill">Le personnage descend s'il est sur une case rouge (hachurée), et avance à droite sinon.</p></div><div class="droite"><p class="type">Run 03 · ◆◆◇</p><div class="chip">Départ : A2</div></div></header>
  <div class="cols" style="grid-template-columns:1fr auto 1fr;align-items:center;gap:5mm">
    {code([K('for') + ' i ' + K('in') + ' ' + NB('range') + '(' + MI('4') + '):', '    ' + K('if') + ' ' + F('rouge') + '():', '        ' + F('bas') + '()', '    ' + K('else') + ':', '        ' + F('droite') + '()'])}
    {grille(rouges=('B2', 'D2', 'C3'), depart='A2', nom='exercice 3').replace('class="ci"', 'class="ci petite"')}
    <div class="rep"><span>Touches :</span><span class="write-line"></span><span>Arrivée :</span><span class="write-line"></span></div>
  </div>
</div>

<div class="cols stretch">
  <div class="ex-court">
    <header class="exo mini"><div class="exo-num"><span>Exercice</span><b>4</b></div><div class="exo-title"><h2>Répéter avec <code>while</code></h2><p class="skill">Départ en <b>A1</b> (case rouge hachurée).</p></div><div class="droite"><p class="type">Run 04 · ◆◆◇</p></div></header>
    <div class="cols" style="grid-template-columns:1fr auto;align-items:center">{code([K('while') + ' ' + F('rouge') + '():', '    ' + F('droite') + '()', '    ' + F('bas') + '()', '    ' + F('bas') + '()'])}{grille(rouges=('A1', 'B3'), depart='A1', nom='exercice 4').replace('class="ci"', 'class="ci petite"')}</div>
    <div class="rep" style="margin-top:1.6mm"><span>Tours de boucle :</span><span class="write-line"></span><span>Touches :</span><span class="write-line"></span><span>Arrivée :</span><span class="write-line"></span></div>
  </div>
  <div class="ex-court">
    <header class="exo mini"><div class="exo-num"><span>Exercice</span><b>5</b></div><div class="exo-title"><h2><code>while</code> bloc d'instructions</h2><p class="skill">Départ en <b>A1</b> (blanche). Rouge en <b>B2</b>.</p></div><div class="droite"><p class="type">Run 05 · ◆◆◆</p></div></header>
    <div class="cols" style="grid-template-columns:1fr auto;align-items:center">{code([K('while') + ' ' + K('not') + ' ' + F('rouge') + '():', '    ' + F('droite') + '()', '    ' + F('bas') + '()'])}{grille(rouges=('B2',), depart='A1', nom='exercice 5').replace('class="ci"', 'class="ci petite"')}</div>
    <div class="rep" style="margin-top:1.6mm"><span>Tours de boucle :</span><span class="write-line"></span><span>Touches :</span><span class="write-line"></span><span>Arrivée :</span><span class="write-line"></span></div>
  </div>
</div>


<div class="box hint signe compact">{mwezi}<div><span class="box-label">{ICONE_IDEE}Coup de pouce</span><span class="box-body">Avant chaque tour de <code>while</code>, regardez votre case : c'est elle qui décide du tour suivant.</span><span class="qui">— Mwezi, analyste</span></div></div>

</div><div class="foot"><span>Activité · Python et Compute-it débranché</span><span class="pg">2 / 2</span></div></section>

</body>
</html>
'''
open(sys.argv[1], 'w').write(html)
print('ok', len(html))
