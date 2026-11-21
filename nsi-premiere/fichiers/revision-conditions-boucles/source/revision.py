"""Séance de révision de Première : feuille de route, mini-contrôle croisé, atelier robot (sujets et corrigés).

Les réponses des corrigés sont vérifiées par exécution (verifier_mini, verifier_defis).
La feuille de style est celle des anciens TD « Bases python » : style-td.html (copie de la feuille du TD
récapitulatif avant sa conversion au style « Signal pirate », T125).
Les exercices « trouve l'erreur » de syntaxe montrent le vrai message de Python 3.13 (décision du 20/11),
produit ici par le compilateur de Python, au même format que « python3 fichier.py ».

Régénérer, depuis ce dossier source/ :
    python3 revision.py
    python3 pdf.py .. seance-revision-eleves seance-revision-corriges
"""
import os, re, sys
import outils as gen
from outils import pre, grille, lancer, nom, plein, lignes, ROBOT, OBST, CIBLE

T = "Séance de révision"

def tete(titre, corrige=False, ident=True):
    s = f'<header><h1>{titre}{" — corrigé" if corrige else ""}</h1><span class="badge">NSI — Première</span></header>'
    if ident:
        s += '<div class="ident"><span>Nom&nbsp;:</span><span>Prénom&nbsp;:</span><span class="small">Classe&nbsp;:</span></div>'
    return s

def pied(txt):
    return ('<footer><span>NSI — Première &nbsp;|&nbsp; Langages et programmation</span>'
            f'<span>{txt}</span>{gen.credit("revision-conditions-boucles")}</footer>')

def h2(n, titre, pts="", robot=False):
    return (f'<h2><span class="exo-num">{n}</span> {titre}' + (' <span class="tag-robot">Robot</span>' if robot else "")
            + (f'<span class="pts">{pts}</span>' if pts else "") + "</h2>")

def lbl(i, etoile=False, robot=False):
    return (f'<span class="lbl">{"abcdefgh"[i]})</span>' + (' <span class="et">★</span>' if etoile else "")
            + (' <span class="tag-robot">Robot</span>' if robot else ""))

# ================================================================ feuille de route
BLOCS = [
    ("Les conditions", ["if / else", "première condition vraie", "== et deux-points", "and", "deux if de suite"], "TD Conditions, exercices 2 et 4 · Lagon Arena"),
    ("La boucle for", ["range(n)", "range(a, b)", "indentation", "total", "if dans un for"], "TD Boucle for, exercices 2 et 4 · Court-circuit"),
    ("La boucle while", ["suivre un while", "nombre de tours", "boucle sans fin", "for ou while ?", "robot"], "TD Boucle while, exercices 2 et 4"),
    ("Les fonctions", ["utiliser return", "return oublié", "définir / appeler", "if dans une fonction", "for dans une fonction"], "Exercice 5 des TD Conditions, for et while"),
]
CASE = '<span class="case"></span>'

def page_route():
    s = ['<div class="page pr">', '<header><h1>Ma feuille de route</h1><span class="badge">NSI — Première</span></header>',
         '<div class="ident"><span>Nom&nbsp;:</span><span>Prénom&nbsp;:</span><span class="small">Classe&nbsp;:</span></div>',
         '<p class="chapo">Cette feuille te suit pendant toute la séance, puis <b>tu la gardes</b> : c\'est ton plan de révision pour le contrôle. Tu rends seulement le coupon du bas.</p>']
    # 1. quiz
    s.append('<h2><span class="exo-num">1</span> Le quiz : où j\'en suis<span class="pts">après chaque question : ✓ si j\'ai juste, ✗ sinon</span></h2>')
    s.append('<table class="rq"><tr><th>Bloc</th>' + "".join(f"<th>Question {k}</th>" for k in range(1, 6)) + "<th>Score</th><th>Mon bilan (j'entoure)</th></tr>")
    n = 0
    for b, (nomb, comp, _) in enumerate(BLOCS, 1):
        s.append(f'<tr><td class="nb"><b>{b}. {nomb}</b></td>')
        for c in comp:
            n += 1
            s.append(f'<td class="qc">{CASE}<span class="qt"><b>{n}.</b> {c}</span></td>')
        s.append('<td class="sc">&nbsp;&nbsp;&nbsp; / 5</td><td class="bil"><span>acquis</span><span>fragile</span><span>à revoir</span></td></tr>')
    s.append('</table><p class="cap">4 ou 5 : acquis &nbsp;·&nbsp; 3 : fragile &nbsp;·&nbsp; 0, 1 ou 2 : à revoir en priorité. Les cases ✗ te disent exactement quoi retravailler.</p>')
    # 2 et 3 côte à côte
    s.append('<div class="duo"><div>')
    s.append('<h2><span class="exo-num">2</span> Le mini-contrôle croisé</h2>')
    s.append('<table class="rm"><tr><th>Traduire</th><th>Erreurs</th><th>Compléter</th><th>Robot</th><th>Total</th></tr>'
             '<tr><td>/ 2</td><td>/ 3</td><td>/ 2</td><td>/ 3</td><td class="tot">/ 10</td></tr></table>'
             '<p class="etape">L\'erreur que mon ou ma camarade m\'a expliquée, et que je ne referai plus :</p>' + lignes(2))
    s.append('</div><div>')
    s.append('<h2><span class="exo-num">3</span> L\'atelier robot</h2>')
    s.append('<table class="ra"><tr><th>Défi</th><th>Tracé</th><th>Dit en français</th><th>Code écrit</th><th>Réussi sur les 3 grilles</th></tr>'
             + "".join(f'<tr><td><b>{k}</b></td><td>{CASE}</td><td>{CASE}</td><td>{CASE}</td><td>{CASE}</td></tr>' for k in ("1", "2", "3", "4 ★"))
             + '</table><p class="cap">L\'étape où je bloque le plus souvent : tracer · dire · repérer · écrire (j\'entoure).</p>')
    s.append('</div></div>')
    # 4. plan
    s.append('<h2><span class="exo-num">4</span> Mon plan de révision avant le contrôle</h2>')
    s.append('<div class="duo plan"><div><table class="rp"><tr><th>Si mon point faible est…</th><th>…je refais</th></tr>'
             + "".join(f"<tr><td>{nomb}</td><td>{res}</td></tr>" for nomb, _, res in BLOCS)
             + '<tr><td>Le robot, le problème</td><td>TD récapitulatif, exercices 5 et 6 · les 4 défis de l\'atelier, sans regarder</td></tr></table></div>'
             '<div><div class="info-box ctl"><b>Le contrôle : 1&nbsp;h&nbsp;30, sur 20.</b><br>Traduire 1,5 · Erreurs 1,5 · Compléter 4 · Robot 5 · <b>Problème 8</b> (écrire du code : une condition, une boucle, deux boucles à la suite, une boucle dans une boucle).</div>'
             '<p class="etape"><b>Mes deux priorités :</b></p><div class="prio"><span>1.</span><i></i></div><div class="prio"><span>2.</span><i></i></div></div></div>')
    # coupon
    s.append('<div class="coupon"><div class="ct">✂ &nbsp; Coupon à rendre en fin de séance</div>'
             '<div class="cl"><span>Nom, prénom&nbsp;: <i class="l"></i></span>'
             '<span>Quiz&nbsp;: conditions <i></i>/5 · for <i></i>/5 · while <i></i>/5 · fonctions <i></i>/5</span></div>'
             '<div class="cl"><span>Mini-contrôle&nbsp;: <i></i>/10</span><span>Défis réussis&nbsp;: 1 · 2 · 3 · 4</span>'
             '<span>Ma priorité&nbsp;: <i class="l"></i></span><span>Je me sens prêt·e&nbsp;: 1 · 2 · 3 · 4 · 5</span></div></div>')
    s.append(pied("Séance de révision — feuille de route") + "</div>")
    return "".join(s)

# ================================================================ mini-contrôle croisé
GM = dict(depart="A5", obstacles=["A2", "C5", "E4", "D1", "F2"])
M1 = [
    dict(code='if stock == 0:\n    print("Rupture")\nelif stock < 5:\n    print("Bientôt vide")\nelse:\n    print("En stock")',
         rep="Si le stock vaut 0, on affiche « Rupture » ; sinon, s'il est inférieur à 5, on affiche « Bientôt vide » ; sinon, on affiche « En stock »."),
    dict(robot=True, code="for i in range(3):\n    nord()\nest()",
         rep="On répète 3 fois : le robot avance d'une case vers le nord. Ensuite, il avance une seule fois d'une case vers l'est."),
]
M2 = [
    dict(code='if age >= 18:\nprint("Majeur")', syntaxe=True, fichier="majeur.py", fix='    print("Majeur")',
         exp="La ligne sous le if doit être indentée (4 espaces).", bon='age = 20\nif age >= 18:\n    print("Majeur")', attendu=["Majeur"]),
    dict(code="for i in range(1, 5):\n    print(i)", q="Il doit afficher les nombres de 1 à 5, mais 5 n'apparaît pas.", fix="for i in range(1, 6):",
         exp="range s'arrête juste avant sa fin : pour aller jusqu'à 5, on écrit 6.", bon="for i in range(1, 6):\n    print(i)", attendu=list("12345"), faux=list("1234")),
    dict(code='if x > 10:\n    print("Grand")\nelse x > 5:\n    print("Moyen")', syntaxe=True, fichier="taille.py", fix="elif x > 5:",
         exp="else ne prend jamais de condition. Pour tester une autre condition, on écrit elif.", bon='x = 7\nif x > 10:\n    print("Grand")\nelif x > 5:\n    print("Moyen")', attendu=["Moyen"]),
]
M3 = [
    dict(stmt="<b>Somme.</b> Le programme calcule et affiche 1 + 2 + 3 + … + 50.",
         code="total = ⟦0⟧\nfor i in range(1, ⟦51⟧):\n    total = ⟦total + i⟧\nprint(total)", attendu=["1275"]),
    dict(stmt="<b>Tirelire.</b> Elle contient 20&nbsp;€. On ajoute 15&nbsp;€ par semaine. Le programme affiche le nombre de semaines pour atteindre 100&nbsp;€.",
         code="argent = 20\nsemaines = 0\nwhile argent ⟦<⟧ 100:\n    argent = ⟦argent + 15⟧\n    semaines = ⟦semaines + 1⟧\nprint(semaines)", attendu=["6"]),
]
M4 = [
    dict(code="nord()\nfor i in range(3):\n    est()", arr_attendue="D4"),
    dict(code="est()\nwhile not obstacleNord():\n    nord()", arr_attendue="B1"),
    dict(etoile=True, code="while not obstacleNord():\n    nord()\n    if not obstacleEst():\n        est()", arr_attendue="D2"),
]

def message(code, fichier):
    """Le vrai message de Python (3.13) pour une erreur de syntaxe, comme « python3 fichier.py »."""
    import traceback
    assert sys.version_info[:2] == (3, 13), "le message doit venir de Python 3.13"
    try:
        compile(code + "\n", fichier, "exec")
    except SyntaxError as e:
        return "".join(traceback.format_exception_only(type(e), e)).rstrip("\n")
    raise AssertionError("pas d'erreur de syntaxe : " + code)


def message_html(m):
    """Le message, coloré : l'emplacement en gris, le nom de l'erreur en gras."""
    import html as h
    out = []
    for l in m.split("\n"):
        if l.startswith("  File "):
            out.append(f'<span class="loc">{h.escape(l)}</span>')
        elif re.match(r"^\w+Error\b", l):
            nomerr, _, reste = l.partition(":")
            out.append(f'<b>{h.escape(nomerr)}</b>:{h.escape(reste)}')
        else:
            out.append(h.escape(l))
    return '<pre class="err" aria-label="Message d\'erreur de Python">' + "\n".join(out) + "</pre>"


def verifier_mini():
    for q in M2:
        if q.get("syntaxe"):
            try:
                compile(q["code"], "x", "exec"); raise AssertionError(q["code"])
            except SyntaxError:
                pass
        if q.get("faux"):
            assert lancer(q["code"], "A1", [])[1] == q["faux"]
        assert lancer(q["bon"], "A1", [])[1] == q["attendu"], q["bon"]
    for q in M3:
        assert lancer(plein(q["code"]), "A1", [])[1] == q["attendu"], lancer(plein(q["code"]), "A1", [])[1]
    for q in M4:
        ch, _ = lancer(q["code"], GM["depart"], GM["obstacles"], nc=6, nl=5)
        q["chemin"], q["arr"] = ch, nom(ch[-1])
        assert len(set(ch)) == len(ch) and len(ch) >= 4
        assert q["arr"] == q["arr_attendue"], (q["code"], q["arr"])
    assert len({q["arr"] for q in M4}) == 3
    print("mini :", [q["arr"] for q in M4])

def page_mini(c):
    s = ['<div class="page pm">', tete("Mini-contrôle croisé", c)]
    if c:
        s.append('<div class="tip-box bar"><b>Comment corriger la copie de ton ou ta camarade.</b> 1. Corrige d\'une autre couleur avec ce corrigé : réponse juste, le point ; à moitié juste, la moitié. 2. Écris la note sur 10. '
                 '3. Rends la copie et <b>explique</b> chaque erreur avec tes mots. 4. Chacun·e refait une question ratée, sans le corrigé.</div>')
    else:
        s.append('<div class="tip-box bar"><b>15 minutes, seul·e, sans aide.</b> Ensuite, vous échangez vos copies et chacun·e corrige celle de l\'autre avec le corrigé. Total : 10 points.<br>'
                 '<b>Copie corrigée par&nbsp;:</b> <span class="trou long"></span> &nbsp; <b>Note&nbsp;:</b> <span class="trou"></span> / 10 &nbsp; <b>La question que je refais&nbsp;:</b> <span class="trou"></span></div>')
    s.append(h2(1, "Que veut dire ce code&nbsp;?", "2 points (2 × 1)"))
    s.append('<div class="qlist">')
    for i, q in enumerate(M1):
        rep = f'<p class="rep-t">{q["rep"]}</p>' if c else lignes(2)
        s.append(f'<div class="q"><div class="ql">{lbl(i, robot=q.get("robot"))}</div>{pre(q["code"])}{rep}</div>')
    s.append("</div>")
    s.append(h2(2, "Trouve l'erreur", "3 points (3 × 1)"))
    s.append('<div class="e3">')
    for i, q in enumerate(M2):
        cap = f'<p class="cap">{q["q"]}</p>' if q.get("q") else ""
        rep = f'{pre(q["fix"], cls="py fixe")}<p class="rep-t">{q["exp"]}</p>' if c else lignes(2)
        s.append(f'<div class="q3 e"><div class="ql">{lbl(i)}</div><div>{pre(q["code"])}{cap}</div><div>{rep}</div></div>')
    s.append("</div>")
    if not c:   # sur la feuille des élèves : le vrai message de Python, sous les programmes (le corrigé donne la ligne corrigée)
        s.append('<div class="errs">' + "".join(
            f'<div><span class="lbl">{"abcdefgh"[i]})</span>{message_html(message(q["code"], q["fichier"]))}</div>'
            for i, q in enumerate(M2) if q.get("syntaxe")) + '</div>')
    s.append(h2(3, "Complète le code", "2 points (2 × 1)"))
    s.append('<div class="ex5">')
    for i, q in enumerate(M3):
        s.append(f'<div class="item"><p class="stmt">{lbl(i)} {q["stmt"]}</p>{pre(q["code"], c, "py fill")}</div>')
    s.append("</div>")
    s.append(h2(4, "Où se trouve le robot&nbsp;?", "3 points (3 × 1)", True))
    s.append('<p class="consigne">Le robot part de A5. Trace le trajet et note la case d\'arrivée.</p><div class="r3">')
    for i, q in enumerate(M4):
        arr = f'<b class="rep-t">{q["arr"]}</b>' if c else "<span></span>"
        s.append(f'<div class="rr3"><div>{lbl(i, q.get("etoile"))}</div>{pre(q["code"])}'
                 f'{grille(GM["depart"], GM["obstacles"], 4.2, chemin=q["chemin"] if c else None, nc=6, nl=5)}<div class="ans">Arrivée&nbsp;: {arr}</div></div>')
    s.append("</div>")
    s.append(pied("Séance de révision — mini-contrôle croisé") + "</div>")
    return "".join(s)

# ================================================================ atelier robot
DEFIS = [
    dict(titre="Une boucle", depart="A1", sol="while not obstacleSud():\n    sud()",
         phrase="Tant qu'il n'y a pas d'obstacle au sud, le robot avance vers le sud.",
         repete="Ce qui se répète : avancer vers le sud. Ce qui change : le nombre de cases.",
         piege="for i in range(2):\n    sud()",
         grilles=[(["A4", "C2", "E4"], "A3"), (["A5", "B3", "D1"], "A4"), (["C3", "E2", "D5"], "A5")]),
    dict(titre="Deux boucles, l'une après l'autre", depart="F5", sol="while not obstacleNord():\n    nord()\nwhile not obstacleOuest():\n    ouest()",
         phrase="Tant qu'il n'y a pas d'obstacle au nord, le robot monte. Ensuite, tant qu'il n'y a pas d'obstacle à l'ouest, il avance vers l'ouest.",
         repete="Ce qui se répète : monter, puis aller vers l'ouest. Ce qui change : le nombre de cases de chaque trajet.",
         piege="for i in range(2):\n    nord()\nfor i in range(3):\n    ouest()",
         grilles=[(["F2", "B3", "D5", "A1"], "C3"), (["F1", "D2", "B4", "C5"], "E2"), (["C3", "B4", "E5"], "A1")]),
    dict(titre="Une boucle dans une boucle", depart="A1", sol="for i in range(2):\n    while not obstacleSud():\n        sud()\n    est()",
         phrase="On répète 2 fois : le robot descend jusqu'à l'obstacle, puis avance d'une case vers l'est.",
         repete="Ce qui se répète 2 fois : « descendre jusqu'à l'obstacle, puis une case vers l'est ». Ce qui change : la longueur de chaque descente.",
         piege="for i in range(2):\n    for j in range(2):\n        sud()\n    est()",
         grilles=[(["A3", "B5", "D2", "E4"], "C4"), (["D3", "E1", "F4"], "C5"), (["A2", "B4", "D5", "E2"], "C3")]),
    dict(titre="Le nombre de répétitions est inconnu", etoile=True, depart="A5", sol="while not obstacleNord():\n    nord()\n    while not obstacleEst():\n        est()",
         phrase="Tant qu'il peut monter : le robot monte d'une case, puis avance vers l'est jusqu'à l'obstacle.",
         repete="Ce qui se répète : « monter d'une case, puis aller vers l'est jusqu'à l'obstacle ». Ce qui change : le nombre de répétitions et la longueur des trajets.",
         piege="for i in range(2):\n    nord()\n    while not obstacleEst():\n        est()",
         grilles=[(["D4", "E3", "D2", "B1"], "D3"), (["C4", "F2", "D1", "A2"], "F3"), (["E4", "D3", "B2", "F1"], "D4")]),
]

def verifier_defis():
    for d in DEFIS:
        d["chemins"], rate = [], 0
        for obs, cible in d["grilles"]:
            ch, _ = lancer(d["sol"], d["depart"], obs, nc=6, nl=5)
            assert nom(ch[-1]) == cible, (d["titre"], obs, nom(ch[-1]))
            assert len(set(ch)) == len(ch), (d["titre"], "repasse")
            d["chemins"].append(ch)
            try:
                ch2, _ = lancer(d["piege"], d["depart"], obs, nc=6, nl=5)
                rate += nom(ch2[-1]) != cible
            except gen.Ecrase:
                rate += 1
        assert rate >= 1, (d["titre"], "le programme à nombres fixes ne doit pas réussir partout")
        assert len({c for _, c in d["grilles"]}) == 3, d["titre"]
        print("défi :", d["titre"], [c for _, c in d["grilles"]], "piège raté sur", rate)

METHODE = ('<div class="info-box meth"><div class="m2"><div><h3>La méthode : du dessin au code</h3>'
           '<p><span class="exo-num">1</span> <b>Trace</b> le trajet au crayon sur les trois grilles.</p>'
           '<p><span class="exo-num">2</span> <b>Dis-le en français</b> avec « tant que » ou « répéter … fois ».</p>'
           '<p><span class="exo-num">3</span> <b>Repère</b> ce qui se répète d\'une grille à l\'autre, et ce qui change.</p>'
           '<p><span class="exo-num">4</span> <b>Écris le code</b>, puis teste-le sur les trois grilles.</p>'
           '<p class="cap"><b>À deux :</b> l\'un·e écrit, l\'autre <b>joue le robot</b> et exécute le programme ligne par ligne sur les trois grilles. Robot écrasé ou étoile ratée : on corrige ensemble. On échange les rôles à chaque défi.</p></div>'
           '<table class="dico"><tr><th>Je dis…</th><th>J\'écris…</th></tr>'
           '<tr><td>tant qu\'il n\'y a pas d\'obstacle à l\'est</td><td><code>while not obstacleEst():</code></td></tr>'
           '<tr><td>répéter 3 fois</td><td><code>for i in range(3):</code></td></tr>'
           '<tr><td>s\'il y a un obstacle au nord</td><td><code>if obstacleNord():</code></td></tr>'
           '<tr><td>sinon</td><td><code>else:</code></td></tr>'
           '<tr><td>avancer d\'une case</td><td><code>nord()</code> <code>sud()</code> <code>est()</code> <code>ouest()</code></td></tr></table></div></div>')

def defi(i, d):
    g = "".join(f'<div><div class="gn">Grille {k + 1}</div>{grille(d["depart"], obs, 7.2, cible, None, 6, 5)}</div>'
                for k, (obs, cible) in enumerate(d["grilles"]))
    et = ' <span class="et">★</span>' if d.get("etoile") else ""
    return (f'<div class="defi"><p class="stmt"><span class="lbl">Défi {i + 1}{et}. {d["titre"]}</span> — un seul programme doit amener le robot à l\'étoile sur les trois grilles.</p>'
            f'<div class="dg">{g}<div class="test"><b>Testé par le robot</b><span>{CASE} grille 1</span><span>{CASE} grille 2</span><span>{CASE} grille 3</span></div></div>'
            '<div class="dw"><div><p class="etape"><span class="exo-num">2</span> <b>En français</b></p>' + lignes(2)
            + '<p class="etape"><span class="exo-num">3</span> <b>Ce qui se répète · ce qui change</b></p>' + lignes(2) + '</div>'
            '<div><p class="etape"><span class="exo-num">4</span> <b>Mon code</b></p><div class="codez">' + lignes(5) + '</div></div></div></div>')

def invente():
    vide = "".join(f'<div><div class="gn">{t}</div>{grille("A1", [], 7.2, None, None, 6, 5)}</div>' for t in ("Une grille où il réussit", "Une grille où il échoue"))
    return ('<div class="defi"><p class="stmt"><span class="lbl">À toi d\'inventer.</span> Reprends ton programme du défi 3. Dessine les obstacles et l\'étoile de deux nouvelles grilles : '
            'une où ton programme <b>réussit</b> encore, une où il <b>échoue</b>. Fais-les tester par ton ou ta camarade.</p>'
            f'<div class="dg inv">{vide}<div class="pourquoi"><p class="etape"><b>Pourquoi échoue-t-il sur la seconde ?</b></p>' + lignes(3) + '</div></div></div>')

def pages_atelier():
    out = []
    for n, ids in enumerate(((0, 1), (2, 3)), 1):
        s = ['<div class="page pa">', tete(f"Atelier robot : modéliser la solution ({n}/2)", False, ident=(n == 1))]
        if n == 1:
            s.append(METHODE)
        for i in ids:
            s.append(defi(i, DEFIS[i]))
        if n == 2:
            s.append(invente())
        s.append(pied(f"Séance de révision — atelier robot ({n})") + "</div>")
        out.append("".join(s))
    return "".join(out)

def page_atelier_corrige():
    s = ['<div class="page pc">', tete("Atelier robot", True, ident=False)]
    for i, d in enumerate(DEFIS):
        g = "".join(f'<div><div class="gn">Grille {k + 1}</div>{grille(d["depart"], obs, 5.0, cible, d["chemins"][k], 6, 5)}</div>'
                    for k, (obs, cible) in enumerate(d["grilles"]))
        et = ' <span class="et">★</span>' if d.get("etoile") else ""
        s.append(f'<div class="defi"><p class="stmt"><span class="lbl">Défi {i + 1}{et}. {d["titre"]}</span></p>'
                 f'<div class="dc"><div class="pg">{g}</div><div><p class="rep-t"><b>En français.</b> {d["phrase"]}</p>'
                 f'<p class="rep-t">{d["repete"]}</p><div class="sol">{pre(d["sol"])}</div></div></div></div>')
    s.append('<div class="tip-box"><b>À toi d\'inventer.</b> Le programme du défi 3 réussit sur toute grille où le robot peut descendre, avancer d\'une case vers l\'est, redescendre et avancer encore d\'une case. '
             'Il échoue, par exemple, s\'il y a un obstacle juste à l\'est en bas d\'une descente (le robot s\'écrase) ou si l\'étoile demande trois descentes.</div>')
    s.append(pied("Séance de révision — corrigé de l'atelier robot") + "</div>")
    return "".join(s)

PLUS2 = """
.case { display: inline-block; width: 4.2mm; height: 4.2mm; border: 1.3px solid #5a6273; border-radius: 2px; vertical-align: -1mm; background: #fff; }
.chapo { margin: 0 0 4px; }
.pr h2 { margin: 9px 0 5px; }
.rq { margin: 0; } .rq th { font-size: 8pt; padding: 3px 5px; text-align: center; } .rq th:first-child { text-align: left; }
.rq td { padding: 4px 5px; height: 14.5mm; }
.rq .nb { width: 30mm; }
.rq .qc { width: 24mm; position: relative; padding-left: 9mm; }
.rq .qc .case { position: absolute; left: 2mm; top: 50%; margin-top: -2.9mm; width: 5.8mm; height: 5.8mm; }
.rq .qn { display: block; font-size: 7pt; color: var(--muted); font-weight: 700; line-height: 1; }
.rq .qt { display: block; font-size: 8pt; line-height: 1.2; } .rq .qt b { color: var(--muted); }
.rq .sc { width: 16mm; text-align: right; font-weight: 700; white-space: nowrap; }
.rq .bil { width: 25mm; font-size: 8pt; text-align: center; } .rq .bil span { display: block; white-space: nowrap; line-height: 1.55; }
.duo { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14px; align-items: start; }
.rm td { height: 11mm; text-align: right; font-weight: 700; padding-right: 8px; } .rm th, .ra th { text-align: center; font-size: 8pt; padding: 3px 4px; }
.rm .tot { background: var(--info-bg); }
.ra td { text-align: center; height: 8.2mm; padding: 1px; }
.pr .lines i { height: 8.6mm; }
.etape { margin: 6px 0 2px; }
.rp td, .rp th { padding: 4px 7px; font-size: 8.4pt; } .rp td:first-child { width: 33mm; font-weight: 700; color: var(--primary); }
.plan { grid-template-columns: 1.25fr 1fr; }
.ctl { margin: 5px 0 0; padding: 6px 9px; }
.prio { display: flex; gap: 6px; align-items: flex-end; height: 9mm; } .prio span { font-weight: 700; color: var(--primary); } .prio i { flex: 1; border-bottom: 1px dotted #999; }
.coupon { margin-top: auto; border-top: 1.5px dashed #6b7380; padding-top: 5px; }
.coupon .ct { font-size: 8pt; color: var(--muted); font-weight: 700; margin-bottom: 5px; }
.coupon .cl { display: flex; gap: 16px; align-items: flex-end; height: 8.5mm; white-space: nowrap; }
.coupon i { display: inline-block; width: 8mm; border-bottom: 1px dotted #777; } .coupon i.l { width: 48mm; }
.pr { padding-bottom: 17mm; }
.trou { display: inline-block; width: 12mm; border-bottom: 1px dotted #999; } .trou.long { width: 45mm; }
.pm .q { grid-template-columns: 22mm 60mm 1fr; }
.pm .q .ql { line-height: 1.5; }
.e3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
.e3 .q3.e { grid-template-columns: 7mm 1fr; }
.pm .ex5 { gap: 6px; } .pm pre.fill { line-height: 1.7; }
.pm .q3.e .lines i { height: 6.3mm; }
.pm .q .lines i { height: 6.6mm; }
.pm h2 { margin: 5px 0 3px; }
.pm .bar { line-height: 1.55; }
.pm .rr3 pre { margin: 1px 0 3px; font-size: 7.5pt; line-height: 1.25; }
.pm .rr3 { padding: 3px 8px 4px; }
.pm .consigne { margin-bottom: 3px; }
.pm .ex5 .item { padding: 4px 9px 5px; }
.r3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
.rr3 { border: 1.5px solid var(--border); border-radius: 4px; padding: 5px 8px 6px; }
.rr3 pre { margin: 2px 0 5px; font-size: 7.8pt; }
.rr3 .ans span { height: 6mm; }
.meth { padding: 6px 10px; margin: 0 0 6px; } .meth h3 { margin: 0 0 3px; } .meth p { margin: 2px 0; }
.m2 { display: grid; grid-template-columns: 1fr 88mm; gap: 12px; align-items: center; }
.dico { margin: 0; background: #fff; } .dico td, .dico th { padding: 2px 6px; font-size: 8.2pt; } .dico code { background: none; padding: 0; font-weight: 600; color: var(--primary); }
.defi { border: 1.5px solid var(--border); border-radius: 4px; padding: 6px 10px 8px; margin-top: 6px; }
.defi .stmt { margin: 0 0 3px; }
.dg { display: flex; justify-content: space-between; align-items: flex-end; gap: 6px; }
.dg .test { width: 27mm; border: 1px dashed var(--secondary); border-radius: 4px; padding: 5px 6px; font-size: 8pt; line-height: 1.3; margin-bottom: 1mm; }
.dg .test b { display: block; color: var(--secondary); margin-bottom: 3px; } .dg .test span { display: block; margin: 4px 0; white-space: nowrap; }
.dw { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14px; margin-top: 3px; }
.dw .lines i { height: 7.7mm; }
.codez { border-left: 3px solid var(--primary); padding-left: 7px; background: var(--light-gray); border-radius: 3px; }
.defi .etape { margin: 4px 0 0; }
.dg.inv { justify-content: flex-start; gap: 12px; align-items: flex-start; } .pourquoi { flex: 1; } .pourquoi .lines i { height: 9mm; }
.gn { text-align: center; font-size: 7.6pt; font-weight: 700; color: var(--muted); }
.pc .defi { padding: 5px 10px 6px; margin-top: 5px; }
.dc { display: grid; grid-template-columns: auto 1fr; column-gap: 14px; align-items: center; }
.dc .pg { display: flex; gap: 8px; }
.dc .rep-t { margin: 0 0 3px; }
.pc .sol pre { font-size: 8.8pt; margin: 3px 0 0; }
.pc .tip-box { margin-top: 7px; }
"""

# Écran étroit seulement (téléphone) : la mise en page A4 imprimée ne change pas.
PLUS3 = """
/* le vrai message d'erreur de Python : console claire, nom de l'erreur en gras, lisible en noir et blanc */
pre.err { margin: 2px 0 0; padding: 1px 4px; font-family: 'Fira Code', monospace; font-size: 7pt; line-height: 1.05;
  white-space: pre-wrap; overflow-wrap: anywhere; background: #fff; border: 1px solid var(--border); border-left: 3px solid var(--secondary); color: var(--text); }
pre.err .loc { color: #5a6273; }
pre.err b { color: var(--secondary); font-weight: 700; }
.errs { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top: 1px; }
.errs > div { display: grid; grid-template-columns: 6mm 1fr; align-items: start; }
.errs pre.err { margin: 0; }
.pm .q3.e .lines i { height: 4.8mm; }
@media screen and (max-width: 600px) { .errs { grid-template-columns: 1fr; } }
@media screen and (max-width: 840px) {
  .coupon .cl { flex-wrap: wrap; height: auto; white-space: normal; gap: 6px 16px; margin-bottom: 8px; }
  .coupon i.l { width: 30mm; }
}
@media screen and (max-width: 600px) {
  .rq, .rq tbody, .rq tr { display: block; width: auto; }
  .rq tr:first-child { display: none; }
  .rq tr { border: 1px solid var(--border); border-radius: 4px; margin-bottom: 6px; padding: 3px 0; }
  .rq td { display: block; width: auto !important; height: auto; border: none; padding: 3px 8px; text-align: left !important; font-size: 1em !important; }
  .rq .qc { min-height: 7.5mm; padding-left: 10mm; display: flex; align-items: center; }
  .rq .bil span { display: inline; margin-right: 14px; }
}
"""

def doc(titre, corps):
    return (f'<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{titre}</title>{gen.STYLE}<style>{gen.PLUS}{PLUS2}{PLUS3}</style></head><body>{corps}</body></html>')

if __name__ == "__main__":
    ici = os.path.dirname(os.path.abspath(__file__))
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(ici)
    td = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ici, "style-td.html")
    gen.STYLE = re.search(r"<style.*?</style>", open(td, encoding="utf-8").read(), flags=re.S).group(0)
    verifier_mini(); verifier_defis()
    open(f"{d}/seance-revision-eleves.html", "w", encoding="utf-8").write(doc("Séance de révision — documents des élèves", page_route() + page_mini(False) + pages_atelier()))
    open(f"{d}/seance-revision-corriges.html", "w", encoding="utf-8").write(doc("Séance de révision — corrigés", page_mini(True) + page_atelier_corrige()))
