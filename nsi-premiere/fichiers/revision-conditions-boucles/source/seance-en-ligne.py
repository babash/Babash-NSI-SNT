"""Séance de révision, version en ligne (style « Signal pirate », T125) : le corps des trois feuilles.

Le contenu vient de revision.py (mêmes questions, mêmes grilles, mêmes défis) : ce script en écrit le corps
au format du moteur des TD (charte/gabarit-td/), avec les grilles du robot en SVG, et vérifie par exécution
toutes les réponses (cases d'arrivée, sorties, messages d'erreur, programmes des défis sur leurs trois grilles,
avec les tests cachés des pages).

    python3 -I seance-en-ligne.py DOSSIER     # écrit route.html, mini.html, atelier.html dans DOSSIER
    python3 -I seance-en-ligne.py --verifier  # vérifie seulement (réponses et tests des trois pages publiées)

Les pages publiées (../seance-revision-eleves.html, -2.html, -3.html) sont faites avec charte/nouveau-td.py,
puis ce corps y est inséré (objectifs, corps, mémo).
"""
import html, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import outils as gen          # noqa: E402
import revision as R          # noqa: E402

assert sys.version_info[:2] == (3, 13), "les réponses doivent venir de Python 3.13"
E = html.escape
NC, NL, C = 6, 5, 24          # grille de 6 colonnes (A à F) et 5 lignes, cases de 24 px


# ---------------------------------------------------------------- dessins
def robot(x, y):
    return (f'<g fill="none" stroke="currentColor" stroke-width="1.6"><rect x="{x - 7}" y="{y - 4}" width="14" height="11" rx="2.5"/>'
            f'<path d="M{x} {y - 4}V{y - 8}"/></g><g fill="currentColor"><circle cx="{x}" cy="{y - 8.5}" r="1.6"/>'
            f'<circle cx="{x - 2.7}" cy="{y + 0.6}" r="1.5"/><circle cx="{x + 2.7}" cy="{y + 0.6}" r="1.5"/><rect x="{x - 3}" y="{y + 3.6}" width="6" height="1.4"/></g>')


def etoile(x, y):
    pts = []
    import math
    for k in range(10):
        r = 9 if k % 2 == 0 else 4
        a = -math.pi / 2 + k * math.pi / 5
        pts.append(f'{x + r * math.cos(a):.1f},{y + r * math.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="currentColor"/>'


def grille(depart=None, obstacles=(), cible=None, titre=''):
    w, h = 20 + NC * C + 2, 20 + NL * C + 2
    s = []
    for k in range(NC):
        s.append(f'<text x="{20 + k * C + C / 2}" y="14" text-anchor="middle" fill="currentColor">{gen.COLS[k]}</text>')
    for k in range(NL):
        s.append(f'<text x="9" y="{20 + k * C + C / 2 + 5}" text-anchor="middle" fill="currentColor">{k + 1}</text>')
    for o in obstacles:
        cx, cy = gen.pos(o)
        x, y = 20 + cx * C, 20 + cy * C
        s.append(f'<rect x="{x + 1.5}" y="{y + 1.5}" width="21" height="21" fill="currentColor" fill-opacity=".28"/>'
                 f'<path d="M{x + 5} {y + 5}L{x + 19} {y + 19}M{x + 19} {y + 5}L{x + 5} {y + 19}" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>')
    if cible:
        cx, cy = gen.pos(cible)
        s.append(etoile(20 + cx * C + C / 2, 20 + cy * C + C / 2 + 1))
    if depart:
        cx, cy = gen.pos(depart)
        s.append(robot(20 + cx * C + C / 2, 20 + cy * C + C / 2 + 2))
    traits = ''.join(f'M{20 + k * C} 20V{20 + NL * C}' for k in range(NC + 1)) + ''.join(f'M20 {20 + k * C}H{20 + NC * C}' for k in range(NL + 1))
    s.append(f'<path d="{traits}" fill="none" stroke="currentColor" stroke-width="1"/>')
    desc = (f'Grille du robot : 6 colonnes (A à F) et 5 lignes (1 à 5), le nord en haut.'
            + (f' Le robot est en {depart}.' if depart else '') + (f' Étoile en {cible}.' if cible else '')
            + (f' Obstacles en {", ".join(obstacles)}.' if obstacles else ' Aucun obstacle.'))
    t = f'<text x="{w / 2}" y="{h + 16}" text-anchor="middle" fill="currentColor">{E(titre)}</text>' if titre else ''
    return (f'<svg class="td-grille-robot" width="{w}" height="{h + (22 if titre else 0)}" viewBox="0 0 {w} {h + (22 if titre else 0)}" role="img" '
            f'aria-label="{E(desc)}" font-family="inherit" font-size="14" font-weight="700">{"".join(s)}{t}</svg>')


def grilles(*gs):
    """Plusieurs grilles côte à côte, dans un seul dessin (une figure se met en bloc)."""
    x, morceaux, h = 0, [], 0
    for g in gs:
        w = int(re.search(r'width="(\d+)"', g).group(1)); hh = int(re.search(r'height="(\d+)"', g).group(1))
        lab = re.search(r'aria-label="([^"]*)"', g).group(1)
        morceaux.append(g.replace('<svg class="td-grille-robot" ', f'<svg x="{x}" ', 1)); x += w + 16; h = max(h, hh)
        morceaux[-1] = morceaux[-1].replace(f'aria-label="{lab}"', '', 1)
    labs = ' '.join(re.search(r'aria-label="([^"]*)"', g).group(1) for g in gs)
    return (f'<svg class="td-grille-robot" width="{x - 16}" height="{h}" viewBox="0 0 {x - 16} {h}" role="img" aria-label="{labs}">'
            + ''.join(morceaux) + '</svg>')


# ---------------------------------------------------------------- le robot, dans la page
def preambule(depart, obstacles):
    return f'''<script type="text/x-python" class="td-preambule">
_COL = "ABCDEF"
_etat = {{}}
def _grille(depart, obstacles):
    _etat["pos"] = [_COL.index(depart[0]), int(depart[1])]
    _etat["obs"] = {{(_COL.index(o[0]), int(o[1])) for o in obstacles}}
    _etat["n"] = 0
def _libre(dx, dy):
    _etat["n"] += 1
    if _etat["n"] > 1000:
        raise RuntimeError("Plus de 1000 actions : le programme tourne peut-être sans fin.")
    x, y = _etat["pos"][0] + dx, _etat["pos"][1] + dy
    return 0 <= x < 6 and 1 <= y <= 5 and (x, y) not in _etat["obs"]
def _pas(dx, dy):
    if not _libre(dx, dy):
        raise RuntimeError("Le robot s'écrase en partant de " + _ici() + ".")
    _etat["pos"][0] += dx
    _etat["pos"][1] += dy
def _ici():
    return _COL[_etat["pos"][0]] + str(_etat["pos"][1])
def nord(): _pas(0, -1)
def sud(): _pas(0, 1)
def est(): _pas(1, 0)
def ouest(): _pas(-1, 0)
def obstacleNord(): return not _libre(0, -1)
def obstacleSud(): return not _libre(0, 1)
def obstacleEst(): return not _libre(1, 0)
def obstacleOuest(): return not _libre(-1, 0)
_grille({depart!r}, {list(obstacles)!r})
</script>'''


def tests_defi(i, d):
    """Les tests cachés : la grille 1 (le programme de l'élève vient de tourner), puis les grilles 2 et 3."""
    g = [(obs, cible) for obs, cible in d['grilles']]
    return f'''<script type="text/x-python" class="td-tests">
import linecache
assert _ici() == {g[0][1]!r}, "Grille 1 : le robot finit en " + _ici() + ", l'étoile est en {g[0][1]}."
_src = "".join(linecache.getlines("defi{i}.py"))
for _k, (_obs, _cible) in enumerate({g[1:]!r}, 2):
    _grille({d['depart']!r}, _obs)
    exec(_src, {{**globals()}})
    assert _ici() == _cible, "Grille " + str(_k) + " : le robot finit en " + _ici() + ", l'étoile est en " + _cible + "."
</script>'''


def code(c):
    return '<pre class="td-code">\n' + E(c) + '</pre>'


# ---------------------------------------------------------------- feuille 1 : la feuille de route
def route():
    case = '□'
    o = ['@@OBJECTIFS', '''    <div class="td-objectifs">
      <p class="td-objectif"><b>Objectif :</b> savoir où j'en suis en conditions, boucles et fonctions, et faire mon plan de révision avant le contrôle.</p>
      <p><b>Je sais :</b></p>
      <ul class="td-criteres">
        <li>repérer ce qui est acquis, fragile ou à revoir ;</li>
        <li>dire l'étape où je bloque ;</li>
        <li>choisir mes deux priorités de révision.</li>
      </ul>
      <p class="td-duree">Feuille 1 sur 3 · toute la séance · ensuite : <a href="seance-revision-eleves-2.html">feuille 2</a>, <a href="seance-revision-eleves-3.html">feuille 3</a></p>
    </div>''', '@@CORPS']
    o.append("  <p>Cette feuille te suit pendant toute la séance, puis <b>tu la gardes</b> : c'est ton plan de révision pour le contrôle. Tu rends seulement le coupon du bas.</p>")
    o.append('  <h2 class="td-partie">1. Le quiz : où j\'en suis</h2>\n  <p>Après chaque question : ✓ si j\'ai juste, ✗ sinon.</p>')
    t = ['  <div class="td-table"><table>', '    <thead><tr><th>Bloc</th><th>Questions 1 à 5</th><th>Score</th><th>Mon bilan (j\'entoure)</th></tr></thead>', '    <tbody>']
    n = 0
    for b, (nomb, comp, _) in enumerate(R.BLOCS, 1):
        cel = []
        for c in comp:
            n += 1
            cel.append(f'{case}&nbsp;<b>{n}.</b>&nbsp;{E(c)}')
        # moins de papier (T125b) : deux questions par ligne (les cellules ne passent pas à la ligne d'elles-mêmes)
        cel = ['<br>'.join(' &ensp; '.join(cel[k:k + 2]) for k in range(0, len(cel), 2))]
        t.append(f'      <tr><th>{b}. {E(nomb)}</th><td>{cel[0]}</td><td class="td-nb">… / 5</td><td>acquis<br>fragile · à revoir</td></tr>')
    t += ['    </tbody>', '  </table></div>']
    o += t
    o.append('  <p>4 ou 5 : acquis · 3 : fragile · 0, 1 ou 2 : à revoir en priorité. Les cases ✗ te disent exactement quoi retravailler.</p>')
    o.append('''  <h2 class="td-partie">2. Le mini-contrôle croisé</h2>
  <div class="td-table"><table>
    <thead><tr><th>Traduire</th><th>Erreurs</th><th>Compléter</th><th>Robot</th><th>Total</th></tr></thead>
    <tbody><tr><td class="td-nb">… / 2</td><td class="td-nb">… / 3</td><td class="td-nb">… / 2</td><td class="td-nb">… / 3</td><td class="td-nb">… / 10</td></tr></tbody>
  </table></div>
''' + libre2('r1', "L'erreur que mon ou ma camarade m'a expliquée, et que je ne referai plus :", 2,
                "Écris-la avec tes mots : l'erreur, puis la bonne façon de faire."))
    o.append('  <h2 class="td-partie">3. L\'atelier robot</h2>\n  <div class="td-table"><table>\n    <thead><tr><th>Défi</th><th>Tracé</th><th>Dit en français</th><th>Code écrit</th><th>Réussi sur les 3 grilles</th></tr></thead>\n    <tbody>')
    for k in ('1', '2', '3', '4 ★'):
        o.append(f'      <tr><th>{k}</th><td>{case}</td><td>{case}</td><td>{case}</td><td>{case}</td></tr>')
    o.append('    </tbody>\n  </table></div>\n  <p>L\'étape où je bloque le plus souvent : tracer · dire · repérer · écrire (j\'entoure).</p>')
    o.append('  <h2 class="td-partie">4. Mon plan de révision avant le contrôle</h2>\n  <div class="td-table"><table>\n    <thead><tr><th>Si mon point faible est…</th><th>…je refais</th></tr></thead>\n    <tbody>')
    for nomb, _, res in R.BLOCS:
        o.append(f'      <tr><td>{E(nomb)}</td><td>{E(res)}</td></tr>')
    o.append('      <tr><td>Le robot, le problème</td><td>TD récapitulatif, exercices 5 et 6 · les 4 défis de l\'atelier, sans regarder</td></tr>\n    </tbody>\n  </table></div>')
    o.append('  <p><b>Le contrôle : 1 h 30, sur 20.</b> Traduire 1,5 · Erreurs 1,5 · Compléter 4 · Robot 5 · <b>Problème 8</b> (écrire du code : une condition, une boucle, deux boucles à la suite, une boucle dans une boucle).</p>')
    o.append(libre2('r2', 'Mes deux priorités :', 2,
                    'Pars des blocs « à revoir », puis des « fragiles » : le tableau du 4 te dit quoi refaire.'))
    o.append('''  <div class="td-papier-seul">
  <p><b>Coupon à découper et à rendre en fin de séance</b></p>
  <div class="td-table"><table>
    <tbody>
      <tr><th>Nom, prénom</th><td colspan="3"></td></tr>
      <tr><th>Quiz</th><td colspan="3">conditions … /5 · for … /5 · while … /5 · fonctions … /5</td></tr>
      <tr><th>Mini-contrôle</th><td>… /10</td><th>Défis réussis</th><td>1 · 2 · 3 · 4</td></tr>
      <tr><th>Ma priorité</th><td></td><th>Je me sens prêt·e</th><td>1 · 2 · 3 · 4 · 5</td></tr>
    </tbody>
  </table></div>
  </div>''')
    o.append('@@MEMO')
    o.append('''  <section class="td-memo">
    <h2>Mémo</h2>
    <p>4 ou 5 : acquis ; 3 : fragile ; 0, 1 ou 2 : à revoir en priorité. On révise d'abord ce qui est « à revoir », avec le tableau du plan.</p><!--MARG-->
  </section>''')
    return '\n'.join(o) + '\n'


# ---------------------------------------------------------------- feuille 2 : le mini-contrôle croisé
TRAD = [
    [("Si le stock vaut 0, on affiche « Rupture » ; sinon, s'il est inférieur à 5, on affiche « Bientôt vide » ; sinon, on affiche « En stock ».", None),
     ("Si le stock vaut 0, on affiche « Rupture » et « Bientôt vide », car 0 est inférieur à 5.",
      "Avec elif, on ne teste la deuxième condition que si la première est fausse : une seule branche s'exécute."),
     ("Si le stock vaut 0, on affiche « Rupture » ; s'il est inférieur à 5, « Bientôt vide » ; et on affiche « En stock » dans tous les cas.",
      "else ne s'exécute que si aucune condition n'est vraie, pas dans tous les cas."),
     ("On donne la valeur 0 au stock, puis on affiche « Rupture ».",
      "== compare ; il ne donne pas de valeur. C'est = qui affecte une valeur.")],
    [("Il avance 3 fois d'une case vers le nord, puis une seule fois d'une case vers l'est.", None),
     ("On répète 3 fois : le robot avance d'une case vers le nord, puis d'une case vers l'est.",
      "est() n'est pas décalée : elle est après la boucle, donc exécutée une seule fois."),
     ("Le robot avance d'une case vers le nord, puis 3 fois d'une case vers l'est.",
      "C'est nord() qui est dans la boucle : elle est répétée 3 fois."),
     ("Le robot avance 3 fois en diagonale, d'une case vers le nord-est à chaque fois.",
      "Le robot n'avance jamais en diagonale : nord() puis est() font deux déplacements séparés.")],
]


def qcu(id_, consigne, c, options, aide, corr, support='ecran'):
    lis = []
    for texte, retour in options:
        lis.append(f'      <li data-juste>{E(texte)}</li>' if retour is None else f'      <li data-retour="{E(retour)}">{E(texte)}</li>')
    return (f'  <section class="td-q" data-type="qcu" id="{id_}"' + (f' data-support="{support}"' if support else '') + f'>\n    <p class="td-consigne">{consigne}</p>\n'
            + (code(c) + '\n' if c else '') + '    <ul class="td-options">\n' + '\n'.join(lis) + '\n    </ul>\n'
            + f'    <p class="td-aide">{aide}</p>\n    <div class="td-correction"><p>{corr}</p></div>\n  </section>')


def libre(id_, consigne, c, lignes, corr, support='papier'):
    return (f'  <section class="td-q" data-type="libre" id="{id_}"' + (f' data-support="{support}"' if support else '') + f' data-lignes="{lignes}">\n'
            f'    <p class="td-consigne">{consigne}</p>\n' + (code(c) + '\n' if c else '') + f'    <div class="td-correction"><p>{corr}</p></div>\n  </section>')


def libre2(id_, consigne, lignes, corr):
    """Une question rédigée : à l'écran avec sa zone de brouillon ; sur papier, la question seule avec ses lignes
    (sans l'étiquette « Ta réponse… » : moins de papier, T125b)."""
    return libre(id_, consigne, None, lignes, corr, support='ecran') + '\n' + libre(id_ + '-papier', consigne, None, lignes, corr)


def trous(id_, consigne, c, attendu, aide, corr):
    t = E(c).replace('⟦', '[[').replace('⟧', ']]')
    return (f'  <section class="td-q" data-type="trous" id="{id_}">\n    <p class="td-consigne">{consigne}</p>\n    <pre class="td-code">\n{t}</pre>\n'
            f'    <pre class="td-attendu">\n{attendu}</pre>\n    <p class="td-aide">{aide}</p>\n    <div class="td-correction">{corr}</div>\n  </section>')


ALT3 = {'total + i': 'total + i|i + total', '<': '<|<=', 'argent + 15': 'argent + 15|15 + argent', 'semaines + 1': 'semaines + 1|1 + semaines'}


def mini():
    o = ['@@OBJECTIFS', '''    <div class="td-objectifs">
      <p class="td-objectif"><b>Objectif :</b> vérifier, seul·e et sans aide, que je sais traduire, corriger, compléter un programme et suivre le robot.</p>
      <p><b>Je sais :</b></p>
      <ul class="td-criteres">
        <li>dire en français ce que fait un code ;</li>
        <li>corriger une erreur grâce au message de Python ;</li>
        <li>compléter une boucle for ou while ;</li>
        <li>trouver la case d'arrivée du robot.</li>
      </ul>
      <p class="td-duree">Feuille 2 sur 3 · 15 minutes · 10 questions · seul·e, sans aide</p>
    </div>''', '@@CORPS']
    o.append('  <p class="td-papier-seul"><b>Nom et prénom :</b> ………………………………………… · <b>Classe :</b> ………… · Ensuite, on échange les copies : chacun·e corrige celle de l\'autre avec le corrigé. <b>Copie corrigée par :</b> ……………………… · <b>Note :</b> …… / 10 · <b>La question que je refais :</b> ……</p>')
    o.append('  <h2 class="td-partie">1. Que veut dire ce code ? (2 points)</h2>')
    a, b = R.M1
    o.append(qcu('m1', 'a) Que veut dire ce code ?', a['code'], TRAD[0], 'Lis « elif » comme « sinon, si » et « else » comme « sinon ».', E(a['rep'])))
    o.append(libre('m1-papier', 'a) Que veut dire ce code ? Dis-le en français.', a['code'], 2, E(a['rep'])))
    o.append(qcu('m2', 'b) Robot. Que veut dire ce code ?', b['code'], TRAD[1], 'Regarde les décalages : quelle ligne est dans la boucle ?', E(b['rep'])))
    o.append(libre('m2-papier', 'b) Robot. Que veut dire ce code ? Dis-le en français.', b['code'], 2, E(b['rep'])))
    o.append('  <h2 class="td-partie">2. Trouve l\'erreur (3 points)</h2>')
    q = R.M2[0]
    o.append(f'''  <section class="td-q" data-type="erreur" id="m3" data-fichier="{q['fichier']}" data-ligne="2" data-reponse="{E(q['fix'].strip())}">
    <p class="td-consigne">a) Ce programme ne se lance pas. Trouve la ligne fautive et corrige-la.</p>
    <script type="text/x-python" class="td-preambule">
age = 20
</script>
{code(q['code'])}
    <pre class="td-erreur">
{E(R.message(q['code'], q['fichier']))}</pre>
    <p class="td-aide"><code>expected an indented block</code> : Python attendait un bloc décalé.</p>
    <div class="td-correction"><p>Ligne 2 : <code>{E(q['fix'].strip())}</code>, décalée de 4 espaces. {E(q['exp'])}</p></div>
  </section>''')
    q = R.M2[1]
    o.append(f'''  <section class="td-q" data-type="courte" id="m4" data-comparer="code" data-reponse="{E(q['fix'])}|for i in range(1,6):|for i in range(1, 5+1):|for i in range(1,5+1):">
    <p class="td-consigne">b) {E(q['q'])} Réécris la ligne fautive, corrigée.</p>
{code(q['code'])}
    <p class="td-retour" data-si="for i in range(6):">range(6) commence à 0 : le programme afficherait 0, 1, 2, 3, 4, 5. Il faut commencer à 1.</p>
    <p class="td-retour" data-si="for i in range(0, 6):">range(0, 6) commence à 0 : le programme afficherait aussi 0. Il faut commencer à 1.</p>
    <p class="td-aide">range(a, b) s'arrête juste avant b.</p>
    <div class="td-correction"><p><code>{E(q['fix'])}</code> : {E(q['exp'])}</p></div>
  </section>''')
    q = R.M2[2]
    o.append(f'''  <section class="td-q" data-type="erreur" id="m5" data-fichier="{q['fichier']}" data-ligne="3" data-reponse="{E(q['fix'])}">
    <p class="td-consigne">c) Ce programme ne se lance pas. Trouve la ligne fautive et corrige-la.</p>
    <script type="text/x-python" class="td-preambule">
x = 7
</script>
{code(q['code'])}
    <pre class="td-erreur">
{E(R.message(q['code'], q['fichier']))}</pre>
    <p class="td-aide"><code>expected ':'</code> : Python attendait les deux-points juste après <code>else</code>.</p>
    <div class="td-correction"><p>Ligne 3 : <code>{E(q['fix'])}</code>. {E(q['exp'])}</p></div>
  </section>''')
    o.append('  <h2 class="td-partie">3. Complète le code (2 points)</h2>')
    for k, q in enumerate(R.M3):
        c = q['code']
        for juste, alt in ALT3.items():
            c = c.replace('⟦' + juste + '⟧', '⟦' + alt + '⟧')
        aide = ('range(1, n) s\'arrête juste avant n.' if k == 0 else 'On ajoute 15 € et une semaine à chaque tour, tant qu\'on n\'a pas atteint 100 €.')
        sol = E(gen.plein(q['code']))
        o.append(trous(f'm{6 + k}', ('a) ' if k == 0 else 'b) ') + re.sub(r'&nbsp;', ' ', q['stmt']), c, q['attendu'][0], aide,
                       f'<pre class="td-code">\n{sol}</pre><p>Le programme affiche {q["attendu"][0]}.</p>'))
    o.append(f'  <h2 class="td-partie">4. Où se trouve le robot ? (3 points)</h2>\n  <p>Le robot part de {R.GM["depart"]}. Trace le trajet et note la case d\'arrivée. <code>nord()</code>, <code>sud()</code>, <code>est()</code>, <code>ouest()</code> le déplacent d\'une case ; <code>obstacleNord()</code>… renvoient <code>True</code> si la case voisine est un obstacle ou le bord. Le nord est en haut.</p>')
    for k, q in enumerate(R.M4):
        et = ' ★' if q.get('etoile') else ''
        chemin = ' → '.join(gen.nom(p) for p in q['chemin'])
        o.append(f'''  <section class="td-q" data-type="courte" id="m{8 + k}" data-reponse="{q['arr']}" data-etiquette="Arrivée :">
    <p class="td-consigne">{"abc"[k]}){et} Où arrive le robot ?</p>
{code(q['code'])}
    <figure class="td-schema">{grille(R.GM['depart'], R.GM['obstacles'])}</figure>
    <p class="td-aide">Suis le robot case par case, sur la grille, en lisant le programme ligne par ligne.</p>
    <div class="td-correction"><p>Trajet : {chemin}. Le robot arrive en <b>{q['arr']}</b>.</p></div>
  </section>''')
    o.append('@@MEMO')
    o.append('''  <section class="td-memo">
    <h2>Mémo</h2>
    <p><code>elif</code> : « sinon, si » ; <code>else</code> ne prend jamais de condition. <code>range(a, b)</code> s'arrête avant b. Ce qui est décalé sous une boucle est répété.</p><!--MARG-->
  </section>''')
    return '\n'.join(o) + '\n'


# ---------------------------------------------------------------- feuille 3 : l'atelier robot
def atelier():
    o = ['@@OBJECTIFS', '''    <div class="td-objectifs">
      <p class="td-objectif"><b>Objectif :</b> modéliser la solution d'un problème du robot, du dessin au code, pour qu'un seul programme marche sur trois grilles.</p>
      <p><b>Je sais :</b></p>
      <ul class="td-criteres">
        <li>tracer le trajet et le dire en français ;</li>
        <li>repérer ce qui se répète et ce qui change ;</li>
        <li>écrire des boucles, à la suite ou imbriquées ;</li>
        <li>tester mon programme sur plusieurs grilles.</li>
      </ul>
      <p class="td-duree">Feuille 3 sur 3 · 40 minutes · 4 défis et 1 bonus ★ · à deux</p>
    </div>''', '@@CORPS']
    o.append('''  <h2 class="td-partie">La méthode : du dessin au code</h2>
  <p>1. <b>Trace</b> le trajet au crayon sur les trois grilles. 2. <b>Dis-le en français</b> avec « tant que » ou « répéter … fois ». 3. <b>Repère</b> ce qui se répète d'une grille à l'autre, et ce qui change. 4. <b>Écris le code</b>, puis teste-le sur les trois grilles.</p>
  <p><b>À deux :</b> l'un·e écrit, l'autre <b>joue le robot</b> et exécute le programme ligne par ligne sur les trois grilles. Robot écrasé ou étoile ratée : on corrige ensemble. On échange les rôles à chaque défi.</p>
  <div class="td-table"><table>
    <thead><tr><th>Je dis…</th><th>J'écris…</th><th>Je dis…</th><th>J'écris…</th></tr></thead>
    <tbody>
      <tr><td>tant qu'il n'y a pas d'obstacle à l'est</td><td><code>while not obstacleEst():</code></td><td>répéter 3 fois</td><td><code>for i in range(3):</code></td></tr>
      <tr><td>s'il y a un obstacle au nord</td><td><code>if obstacleNord():</code></td><td>sinon</td><td><code>else:</code></td></tr>
      <tr><td>avancer d'une case</td><td colspan="3"><code>nord()</code> <code>sud()</code> <code>est()</code> <code>ouest()</code></td></tr>
    </tbody>
  </table></div>''')
    for i, d in enumerate(R.DEFIS, 1):
        et = ' ★' if d.get('etoile') else ''
        gr = grilles(*[grille(d['depart'], obs, cible, f'Grille {k}') for k, (obs, cible) in enumerate(d['grilles'], 1)])
        o.append(f'''  <h2 class="td-partie">Défi {i}{et} · {E(d['titre'])}</h2>
  <p{'' if i == 1 else ' class="td-ecran-seul"'}>Un seul programme doit amener le robot à l'étoile sur les trois grilles. Le robot part de {d['depart']}.</p>
  <figure class="td-schema">{gr}</figure>''')
        # moins de papier (T125b) : une ligne quand la réponse modèle est courte (110 caractères au plus), deux sinon
        o.append(libre2(f'd{i}a', 'En français :', 1 + (len(d['phrase']) > 110), E(d['phrase'])))
        o.append(libre2(f'd{i}b', 'Ce qui se répète · ce qui change :', 1 + (len(d['repete']) > 110), E(d['repete'])))
        o.append(f'''  <section class="td-q" data-type="code" id="d{i}c" data-fichier="defi{i}.py" data-lignes="{len(d['sol'].splitlines())}"{' data-bonus' if d.get('etoile') else ''}>
    <p class="td-consigne">Mon code · testé par le robot : □ grille 1 · □ grille 2 · □ grille 3. <span class="td-ecran-seul">« Lancer » le teste sur la grille 1, puis des tests cachés sur les grilles 2 et 3.</span></p>
{preambule(d['depart'], d['grilles'][0][0])}
    <pre class="td-depart">
# Le robot part de {d['depart']}.
</pre>
{tests_defi(i, d)}
    <p class="td-aide">{E(d['phrase'])}</p>
    <p class="td-aide">Attention : un nombre fixe de pas ne marche pas sur les trois grilles. Il faut « tant que ».</p>
    <div class="td-correction"><pre class="td-code" data-verifier="correction">
{E(d['sol'])}</pre><p>{E(d['repete'])}</p></div>
  </section>''')
    vides = grilles(grille(None, (), None, 'Où il réussit'), grille(None, (), None, 'Où il échoue'))
    o.append(f'''  <h2 class="td-partie">À toi d'inventer</h2>
  <p>Reprends ton programme du défi 3. Dessine les obstacles et l'étoile de deux nouvelles grilles : une où ton programme <b>réussit</b> encore, une où il <b>échoue</b>. Fais-les tester par ton ou ta camarade.</p>
  <figure class="td-schema" data-support="papier">{vides}</figure>
''' + libre2('d5', 'Pourquoi échoue-t-il sur la seconde ?', 2,
            "Il échoue, par exemple, s'il y a un obstacle juste à l'est en bas d'une descente (le robot s'écrase) ou si l'étoile demande trois descentes."))
    o.append('@@MEMO')
    o.append('''  <section class="td-memo">
    <h2>Mémo</h2>
    <p>Trace, dis, repère, écris. Un trajet de longueur inconnue : <code>while not obstacle…():</code>. Un motif répété un nombre connu de fois : <code>for i in range(n):</code>.</p><!--MARG-->
  </section>''')
    return '\n'.join(o) + '\n'


# ---------------------------------------------------------------- vérifier, par exécution
def verifier_pages():
    """Exécute, pour chaque défi des pages publiées, la correction puis les tests cachés, comme le moteur."""
    import linecache
    racine = os.path.dirname(ICI)
    page = open(os.path.join(racine, 'seance-revision-eleves-3.html'), encoding='utf-8').read()
    n = 0
    for m in re.finditer(r'<section class="td-q" data-type="code" id="([^"]+)" data-fichier="([^"]+)".*?</section>', page, flags=re.S):
        q = m.group(0)
        pre = html.unescape(re.search(r'class="td-preambule">(.*?)</script>', q, re.S).group(1))
        tests = html.unescape(re.search(r'class="td-tests">(.*?)</script>', q, re.S).group(1))
        sol = html.unescape(re.search(r'data-verifier="correction">\n?(.*?)</pre>', q, re.S).group(1))
        linecache.cache[m.group(2)] = (len(sol), None, sol.splitlines(True), m.group(2))
        g = {'__name__': '__main__'}
        exec(pre, g); exec(compile(sol, m.group(2), 'exec'), g); exec(tests, g)
        # un programme à nombre fixe de pas (le piège) doit échouer sur au moins une grille
        d = R.DEFIS[int(m.group(2)[4]) - 1]
        g = {'__name__': '__main__'}
        linecache.cache[m.group(2)] = (len(d['piege']), None, d['piege'].splitlines(True), m.group(2))
        exec(pre, g)
        try:
            exec(compile(d['piege'], m.group(2), 'exec'), g); exec(tests, g)
            raise AssertionError(m.group(1) + ' : le programme à nombre fixe de pas passe les tests')
        except (AssertionError, RuntimeError) as e:
            if 'passe les tests' in str(e):
                raise
        n += 1
    print(f'atelier : {n} défis, correction juste sur les 3 grilles, programme « piège » refusé')
    assert n == 4


def verifier_reponses():
    """Toute réponse acceptée par la page du mini-contrôle (m3 à m7), et toute réponse refusée avec un retour,
    est exécutée : une réponse acceptée doit donner la sortie attendue, une réponse refusée une autre sortie."""
    import contextlib, io
    page = open(os.path.join(os.path.dirname(ICI), 'seance-revision-eleves-2.html'), encoding='utf-8').read()

    def sortie(prog, avant=''):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            exec(compile(avant + prog, 'essai.py', 'exec'), {})
        return f.getvalue().split()

    def section(i):
        return re.search(r'<section class="td-q"[^>]*id="%s".*?</section>' % i, page, re.S).group(0)
    n = 0
    # m4 : la ligne corrigée, puis le print
    q = R.M2[1]; s = section('m4')
    for r in html.unescape(re.search(r'data-reponse="([^"]*)"', s).group(1)).split('|'):
        assert sortie(r + '\n    print(i)') == q['attendu'], ('m4 accepte', r); n += 1
    for r in re.findall(r'data-si="([^"]*)"', s):
        assert sortie(html.unescape(r) + '\n    print(i)') != q['attendu'], ('m4 refuse', r); n += 1
    # m3, m5 : la ligne corrigée à sa place
    for i, k, l, avant in (('m3', 0, 2, 'age = 20\n'), ('m5', 2, 3, 'x = 7\n')):
        q = R.M2[k]; s = section(i)
        lignes = q['code'].split('\n')
        for r in html.unescape(re.search(r'data-reponse="([^"]*)"', s).group(1)).split('|'):
            lignes2 = lignes[:]; ind = len(lignes[l - 1]) - len(lignes[l - 1].lstrip())
            lignes2[l - 1] = (r if r.startswith(' ') else ' ' * (4 if i == 'm3' else ind) + r.strip())
            sortie('\n'.join(lignes2), avant); n += 1          # se lance sans erreur
    # m6, m7 : chaque combinaison des variantes acceptées
    import itertools
    for k, q in enumerate(R.M3):
        s = section(f'm{6 + k}')
        code_page = html.unescape(re.search(r'<pre class="td-code">\n(.*?)</pre>', s, re.S).group(1))
        trous = re.findall(r'\[\[(.*?)\]\]', code_page)
        for choix in itertools.product(*[t_.split('|') for t_ in trous]):
            it = iter(choix)
            prog = re.sub(r'\[\[(.*?)\]\]', lambda m: next(it), code_page)
            assert sortie(prog) == q['attendu'], (f'm{6 + k} accepte', choix); n += 1
    print(f'mini-contrôle : {n} réponses acceptées ou refusées vérifiées par exécution')


if __name__ == '__main__':
    R.verifier_mini(); R.verifier_defis()
    if sys.argv[1:] == ['--verifier']:
        verifier_reponses()
        verifier_pages()
        print('tout est juste')
    else:
        d = sys.argv[1]
        for nom_, f in (('route', route), ('mini', mini), ('atelier', atelier)):
            open(os.path.join(d, nom_ + '.html'), 'w', encoding='utf-8').write(f())
        print('corps écrits dans', d)
