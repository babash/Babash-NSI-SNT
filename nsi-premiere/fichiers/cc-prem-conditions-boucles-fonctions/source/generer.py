"""Contrôle de Première : conditions, boucles, fonctions. Sujet et corrigé, réponses vérifiées par exécution.

Version révisée du 25/11/2026 (T142) : règle des contrôles, charte/gabarit-controle/LISEZMOI.md.
La version validée le 20/11/2026 est gardée dans version-2026-11-20/ (générateur et PDF).

La feuille de style est celle des anciens TD « Bases python » : nsi-premiere/fichiers/revision-conditions-boucles/source/style-td.html
(copie de la feuille du TD récapitulatif avant sa conversion au style « Signal pirate », T125 ; les contrôles restent tels quels).
Les outils (robot, code coloré, grilles) sont dans outils.py, le même fichier que pour la séance de révision.

Régénérer, depuis ce dossier source/ :
    python3.13 generer.py
    python3 pdf.py .. controle-1re controle-1re-corrige
"""
import html, os, re, sys
from outils import (COLS, NL, Ecrase, pos, nom, lancer, colorer, pre, plein,
                    ROBOT, OBST, CIBLE, grille, lignes, PLUS, credit)

# ---------------------------------------------------------------- contenu (version révisée du 25/11/2026, T142)
# Règle des contrôles : charte/gabarit-controle/LISEZMOI.md. Première : début par des questions de cours,
# surtout compléter, corriger, prévoir ; une seule fonction courte cadrée (signature et exemple donnés).
G4 = dict(depart="A6", obstacles=["A2", "C2", "B4", "D4", "D6", "F5", "E3", "G3"])
GC = [dict(depart="A5", obstacles=["E5", "D2", "B3", "F1"], cible="D3"),
      dict(depart="A5", obstacles=["C5", "B1", "E3", "D4"], cible="B2"),
      dict(depart="A5", obstacles=["C3", "D1", "B2"], cible="F1")]
GD = [dict(depart="A5", obstacles=["C5", "E4", "B2", "D1"], cible="F2"),
      dict(depart="A5", obstacles=["D5", "E4", "F3", "A2", "C1"], cible="E2"),
      dict(depart="A5", obstacles=["B5", "D4", "E3", "F5", "B1"], cible="D2")]

# Exercice 1 : questions de cours (4 points)
VF = [  # (affirmation, vraie ?, explication du corrigé)
    ("<code>range(5)</code> donne les entiers de 0 à 5.", False, "<code>range(5)</code> donne 0, 1, 2, 3, 4 : le 5 n'est pas compris."),
    ("Une boucle <code>while</code> se répète tant que sa condition est vraie.", True, "Elle s'arrête dès que la condition devient fausse."),
    ("Dans <code>if … elif … else</code>, un seul des blocs est exécuté.", True, "Python exécute le premier bloc dont la condition est vraie (ou le <code>else</code>), puis sort."),
    ("Une fonction s'exécute dès qu'on l'a définie avec <code>def</code>.", False, "<code>def</code> définit la fonction ; elle ne s'exécute que quand on l'appelle, par exemple <code>frais(45)</code>."),
]
QCM_CODE = ['n = 0\nwhile n > 5:\n    print("Bonjour")\n    n = n + 1', None]
QCM = [  # (question, options, indice de la bonne, explication)
    ("La condition de cette boucle est fausse dès le départ. Combien de fois le programme affiche-t-il « Bonjour » ?",
     ["une seule fois", "aucune fois", "cinq fois", "sans jamais s'arrêter"], 1, "<code>0 > 5</code> est faux : on n'entre jamais dans la boucle."),
    ("Quelle condition est vraie quand <code>note</code> est comprise entre 10 et 15, bornes comprises ?",
     ["<code>note > 10 and note < 15</code>", "<code>note >= 10 or note <= 15</code>", "<code>note >= 10 and note <= 15</code>", "<code>note > 10 or note < 15</code>"], 2,
     "Il faut les deux conditions à la fois (<code>and</code>) et les bornes comprises (<code>>=</code>, <code><=</code>)."),
]
RELIER = [("def", "définir une fonction"), ("return", "renvoyer une valeur"),
          ("while", "répéter tant qu'une condition est vraie"), ("elif", "sinon, si une autre condition est vraie")]
RELIER_DROITE = [2, 0, 3, 1]  # ordre d'affichage des définitions (aucun motif)

# Exercice 2 : que veut dire ce code ? (1 point)
EX1 = [
    dict(robot=False, code='if note >= 16:\n    print("Très bien")\nelif note >= 10:\n    print("Admis")\nelse:\n    print("Refusé")',
         rep="Si la note vaut au moins 16, on affiche « Très bien » ; sinon, si elle vaut au moins 10, on affiche « Admis » ; sinon, on affiche « Refusé »."),
    dict(robot=True, code="while not obstacleSud():\n    sud()\nouest()",
         rep="Tant qu'il n'y a pas d'obstacle au sud, le robot avance d'une case vers le sud : il descend jusqu'à l'obstacle (ou au bord). Ensuite, il avance d'une case vers l'ouest."),
]

# Exercice 3 : trouve l'erreur (4 points). Une question par programme : corriger et expliquer, ½ + ½ (G37).
# Le message, quand il y en a un, est celui de Python 3.13 (produit à la génération) et ne donne pas la correction.
EX2 = [
    dict(code='age = input("Âge : ")\nif age >= 18:\n    print("Majeur")', entree="20",
         q="Corrige l'erreur, puis explique-la en quelques mots.", fix='age = int(input("Âge : "))   (ligne 1)',
         exp="<code>input</code> renvoie toujours du texte (<code>str</code>) : on ne peut pas le comparer au nombre 18. <code>int(…)</code> le transforme en nombre.",
         bon='age = int(input("Âge : "))\nif age >= 18:\n    print("Majeur")', entrees=["20"], attendu=["Majeur"]),
    dict(code="n = 10\nwhile n > 0:\n    print(n)", obs="Le programme affiche 10 sans jamais s'arrêter.",
         q="Corrige l'erreur, puis explique-la en quelques mots.", fix="    n = n - 1   (à ajouter à la fin de la boucle)",
         exp="<code>n</code> ne change jamais : la condition <code>n > 0</code> reste vraie. En enlevant 1 à chaque tour, la boucle s'arrête après 1.",
         bon="n = 10\nwhile n > 0:\n    print(n)\n    n = n - 1", attendu=[str(i) for i in range(10, 0, -1)]),
    dict(code="def double(x):\n    resultat = 2 * x\n\nprint(double(4) + 1)", 
         q="Corrige l'erreur, puis explique-la en quelques mots.", fix="    return resultat   (à ajouter en ligne 3)",
         exp="La fonction ne renvoie rien : sans <code>return</code>, <code>double(4)</code> vaut <code>None</code>, et on ne peut pas ajouter 1 à <code>None</code>.",
         bon="def double(x):\n    resultat = 2 * x\n    return resultat\n\nprint(double(4) + 1)", attendu=["9"]),
    dict(code="for i in range(1, 5):\n    total = 0\n    total = total + i\nprint(total)", obs="Il doit afficher 10 (= 1 + 2 + 3 + 4), mais il affiche 4.",
         q="Corrige l'erreur, puis explique-la en quelques mots.", fix="total = 0   (déplacée avant le for, en ligne 1)",
         exp="<code>total</code> est remis à 0 à chaque tour. Il faut l'initialiser une seule fois, avant la boucle.",
         bon="total = 0\nfor i in range(1, 5):\n    total = total + i\nprint(total)", attendu=["10"], faux=["4"]),
]

# Exercice 4 : complète le code (2,5 points)
EX3 = [
    dict(stmt="<b>De 1 à 10.</b> Le programme affiche les nombres de 1 à 10, un par ligne.", pts="0,5 point",
         code="for i in range(1, ⟦11⟧):\n    print(i)", tests=[("", [str(i) for i in range(1, 11)])]),
    dict(pts="1 point", stmt="<b>Radar.</b> Strictement moins de 50 km/h : «&nbsp;OK&nbsp;». De 50 à 70 km/h : «&nbsp;Ralentis&nbsp;». Au-delà : «&nbsp;Amende&nbsp;».",
         code='if vitesse ⟦<⟧ 50:\n    print("OK")\n⟦elif⟧ vitesse ⟦<=⟧ 70:\n    print("Ralentis")\n⟦else⟧:\n    print("Amende")',
         tests=[("vitesse = 49\n", ["OK"]), ("vitesse = 50\n", ["Ralentis"]), ("vitesse = 70\n", ["Ralentis"]), ("vitesse = 71\n", ["Amende"])]),
    dict(pts="1 point", stmt="<b>Bouchon vers Mamoudzou.</b> 30 voitures attendent. Chaque minute, 4 voitures passent. Le programme affiche le nombre de minutes pour que la file soit vide.",
         code="voitures = 30\nminutes = 0\nwhile voitures ⟦>⟧ 0:\n    voitures = ⟦voitures - 4⟧\n    minutes = ⟦minutes + 1⟧\nprint(minutes)",
         tests=[("", ["8"])]),
]

# Exercice 5 : où arrive le robot ? (3 points) ; le dernier programme a aussi un affichage, demandé à part.
EX4 = [
    dict(code="est()\nif obstacleNord():\n    est()\nelse:\n    nord()"),
    dict(code="for i in range(2):\n    est()\n    nord()"),
    dict(code="while not obstacleEst():\n    est()\nnord()"),
    dict(code="def avancer(n):\n    for i in range(n):\n        est()\n\nnord()\navancer(4)\nnord()\navancer(2)"),
    dict(code="pas = 0\nfor i in range(3):\n    nord()\nwhile not obstacleEst():\n    est()\n    pas = pas + 1\nprint(pas)", aff=True),
]

# Problème (5,5 points) : une seule fonction à écrire (cadrée, docstring en mots) ; les programmes du robot se complètent.
PB = [
    dict(titre="Les frais de livraison", pts="2 points", entete='def frais(montant):\n    """Renvoie le prix de la livraison, en euros, pour une commande de montant euros.\n    Exemples : frais(45) renvoie 0 ; frais(30) renvoie 0 ; frais(12) renvoie 3."""',
         stmt="La livraison est <b>gratuite</b> si le montant de la commande vaut <b>au moins 30&nbsp;€</b>. Sinon, elle coûte <b>3&nbsp;€</b>.<br>Écris le corps de la fonction <code>frais</code> sous son en-tête.",
         sol="def frais(montant):\n    if montant >= 30:\n        return 0\n    else:\n        return 3", lignes=6),
    dict(titre="Les tournées", pts="1 point",
         stmt="Le robot livre <b>8 colis par tournée</b>. La fonction <code>colis_livres(n)</code> affiche le nombre total de colis livrés après chaque tournée, de la 1<sup>re</sup> à la <code>n</code><sup>e</sup>. Exemple : <code>colis_livres(3)</code> affiche 8, puis 16, puis 24. Complète-la.",
         code="def colis_livres(n):\n    total = 0\n    for i in range(1, n + 1):\n        total = ⟦total + 8⟧\n        print(⟦total⟧)",
         sol="def colis_livres(n):\n    total = 0\n    for i in range(1, n + 1):\n        total = total + 8\n        print(total)"),
    dict(titre="Aller chercher le colis", pts="1 point", g=GC,
         stmt="Complète <b>ce programme</b> pour qu'il amène le robot jusqu'au colis <b>★</b> sur <b>les trois grilles</b>.",
         code="while ⟦not obstacleEst()⟧:\n    est()\nwhile not obstacleNord():\n    ⟦nord()⟧",
         sol="while not obstacleEst():\n    est()\nwhile not obstacleNord():\n    nord()", piege="for i in range(3):\n    est()\nfor i in range(2):\n    nord()"),
    dict(titre="Livrer le client", pts="1,5 point", g=GD,
         stmt="Sur chaque grille, le robot refait 3 fois le même trajet. Complète la première ligne de <b>ce programme</b> pour qu'il amène le robot jusqu'au client <b>★</b> sur <b>les trois grilles</b>.",
         code="⟦for i in range(3):⟧\n    while not obstacleEst():\n        est()\n    nord()",
         sol="for i in range(3):\n    while not obstacleEst():\n        est()\n    nord()", piege="for i in range(3):\n    for j in range(2):\n        est()\n    nord()"),
]


RAPPEL = ('<div class="info-box ctx"><div><h3>Rappel&nbsp;: le robot</h3><ul>'
          "<li><code>nord()</code>, <code>sud()</code>, <code>est()</code>, <code>ouest()</code>&nbsp;: déplace le robot d'<b>une case</b> dans cette direction&nbsp;;</li>"
          "<li><code>obstacleNord()</code>, <code>obstacleSud()</code>, <code>obstacleEst()</code>, <code>obstacleOuest()</code>&nbsp;: renvoie <code>True</code> si la case voisine est un <b>obstacle</b> ou le <b>bord</b>, <code>False</code> sinon&nbsp;;</li>"
          "<li>si le robot avance vers un obstacle ou le bord, il <b>s'écrase</b>&nbsp;: le programme s'arrête avec une erreur.</li></ul></div>"
          '<div class="side"><svg width="58" height="58" viewBox="0 0 60 60" aria-label="rose des vents"><circle cx="30" cy="30" r="17" fill="none" stroke="#d5dae2"/><path d="M30 10L33 30L30 50L27 30Z" fill="#1a2a6c"/><path d="M10 30L30 27L50 30L30 33Z" fill="#9aa3b2"/><text x="30" y="8" text-anchor="middle" font-size="9" font-weight="700" fill="#1a2a6c">N</text><text x="30" y="59" text-anchor="middle" font-size="9" font-weight="700" fill="#5a6273">S</text><text x="57" y="33" text-anchor="middle" font-size="9" font-weight="700" fill="#5a6273">E</text><text x="3" y="33" text-anchor="middle" font-size="9" font-weight="700" fill="#5a6273">O</text></svg>'
          f'<div class="leg">{ROBOT.format(t=15)}robot<br>{OBST.format(t=15)}obstacle</div></div></div>')


# ---------------------------------------------------------------- vérifications
def message_python(code, entree=None):
    """Message d'erreur réel de Python 3.13 pour ce programme (dossier retiré du chemin)."""
    import subprocess, tempfile
    assert sys.version_info[:2] == (3, 13), "générer avec Python 3.13 : les messages d'erreur du sujet en dépendent"
    with tempfile.TemporaryDirectory() as d:
        chemin = os.path.join(d, "programme.py")
        open(chemin, "w", encoding="utf-8").write(code + "\n")
        r = subprocess.run([sys.executable, "-I", chemin], capture_output=True, text=True, cwd=d,
                           input=(entree + "\n") if entree is not None else "")
    return r.stderr.replace(chemin, "programme.py").rstrip("\n")


def verifier():
    r = {}
    assert sum(1 for _, v, _ in VF if v) == 2 and len(VF) == 4
    assert sorted(RELIER_DROITE) == [0, 1, 2, 3] and all(RELIER_DROITE[k] != k for k in range(4))
    assert [b for _, _, b, _ in QCM] == [1, 2]
    assert lancer(QCM_CODE[0], "A1", [])[1] == []  # e) : aucune fois
    for note, ok in [(9, False), (10, True), (15, True), (16, False), (12, True)]:
        assert (note >= 10 and note <= 15) == ok and ((note > 10 and note < 15) == ok) == (note not in (10, 15))
    lancer("note = 12\n" + EX1[0]["code"], "A1", [])
    for i, q in enumerate(EX2):
        compile(q["code"], "x", "exec")
        if not q.get("obs"):   # a) et c) : le programme s'arrête ; on montre le vrai message de Python 3.13
            q["msg"] = message_python(q["code"], q.get("entree"))
            assert q["msg"].startswith("Traceback") and "Error" in q["msg"], q["msg"]
            # le message ne donne pas la correction (G37)
            assert not re.search(r"(?<![a-z])int\(", q["msg"]) and "return" not in q["msg"] and "Did you mean" not in q["msg"], q["msg"]
        if q.get("faux"):
            assert lancer(q["code"], "A1", [])[1] == q["faux"], (i, lancer(q["code"], "A1", [])[1])
        if q.get("robot"):
            lancer(q["bon"], "A6", ["D6"])
        else:
            assert lancer(q["bon"], "A1", [], q.get("entrees", ()))[1] == q["attendu"], i
    n = [0]
    def stop(*a):
        n[0] += 1
        if n[0] > 50:
            raise RuntimeError
    try:
        exec(EX2[1]["code"], {"print": stop}); raise AssertionError("devrait boucler")
    except RuntimeError:
        pass
    for i, q in enumerate(EX3):
        for avant, att in q["tests"]:
            got = lancer(avant + plein(q["code"]), "A1", [], q.get("entrees", ()))[1]
            assert got == att, (i, got)
    for i, q in enumerate(EX4):
        ch, aff = lancer(q["code"], G4["depart"], G4["obstacles"])
        q["chemin"], q["arr"], q["affv"] = ch, nom(ch[-1]), " ".join(aff)
        assert bool(aff) == bool(q.get("aff")), i
        r[f"4{'abcde'[i]}"] = (q["arr"], q["affv"], len(ch) - 1)
    assert len({q["arr"] for q in EX4}) == len(EX4), "arrivées toutes différentes"
    assert lancer(PB[0]["sol"] + "\nprint(frais(45), frais(12), frais(30), frais(29))", "A1", [])[1] == ["0 3 0 3"]
    # le corrigé se recalcule : chaque détail fait ses points, le tout fait 20, et les parties font ce qu'annonce le sujet
    for q, pts, detail, ok, err in BAREME:
        assert abs(sum(detail) - pts) < 1e-9, (q, detail, pts)
    assert sum(b[1] for b in BAREME) == 20
    parts = {"1": 4, "2": 1, "3": 4, "4": 3, "5": 2.5, "P": 5.5}
    for k, v in parts.items():
        assert sum(b[1] for b in BAREME if b[0].startswith(k + " ")) == v, k
    assert [q["pts"] for q in EX3] == ["0,5 point", "1 point", "1 point"]
    assert [q["pts"] for q in PB] == ["2 points", "1 point", "1 point", "1,5 point"]
    # erreurs fréquentes citées au barème, possibles sur la forme actuelle
    assert ("9" >= "18") is True  # 3 a) comparer des textes : « 9 » passerait pour majeur
    assert lancer("def double(x):\n    resultat = 2 * x\n    print(resultat)\n", "A1", [])[1] == []
    assert lancer(plein(PB[1]["code"]).replace("total = total + 8", "total = 8") + "\ncolis_livres(3)", "A1", [])[1] == ["8", "8", "8"]
    # docstring de A : en mots, sans la condition Python
    assert ">=" not in PB[0]["entete"] and "frais(30) renvoie 0" in PB[0]["entete"]
    # variantes et erreurs citées au barème
    assert lancer(plein(EX3[2]["code"]).replace("voitures > 0", "voitures >= 0"), "A1", [])[1] == ["8"]
    assert lancer(plein(EX3[0]["code"]).replace("11", "10"), "A1", [])[1] == [str(i) for i in range(1, 10)]
    assert lancer("vitesse = 50\n" + plein(EX3[1]["code"]).replace("< 50", "<= 50"), "A1", [])[1] == ["OK"]
    assert lancer("def colis_livres(n):\n    for i in range(0, n):\n        print((i + 1) * 8)\ncolis_livres(3)", "A1", [])[1] == ["8", "16", "24"]
    assert lancer("def colis_livres(n):\n    for i in range(1, n):\n        print(i * 8)\ncolis_livres(3)", "A1", [])[1] == ["8", "16"]
    assert all(n >= 10 or n <= 15 for n in range(-50, 50))
    assert PB[0]["sol"].startswith(PB[0]["entete"].split("\n")[0] + "\n")
    assert len(PB[0]["sol"].split("\n")) - 1 <= 6, "première : fonction courte, 4 à 6 lignes"
    assert plein(PB[1]["code"]) == PB[1]["sol"]
    assert lancer(PB[1]["sol"] + "\ncolis_livres(3)\ncolis_livres(10)", "A1", [])[1] == ["8", "16", "24"] + [str(8 * i) for i in range(1, 11)]
    for q in PB[2:]:
        assert plein(q["code"]) == q["sol"], q["titre"]
        q["chemins"] = []
        ratés = 0
        for g in q["g"]:
            ch, _ = lancer(q["sol"], g["depart"], g["obstacles"], nc=6, nl=5)
            assert nom(ch[-1]) == g["cible"], (q["titre"], g, nom(ch[-1]))
            assert len(set(ch)) == len(ch)
            q["chemins"].append(ch)
            try:
                ch2, _ = lancer(q["piege"], g["depart"], g["obstacles"], nc=6, nl=5)
                ratés += nom(ch2[-1]) != g["cible"]
            except Ecrase:
                ratés += 1
        assert ratés >= 2, (q["titre"], "un programme à nombres fixes ne doit pas suffire")
        assert len({g["cible"] for g in q["g"]}) == 3
    return r


def etiq(i, q, lettres="abcdefgh"):
    return (f'<span class="lbl">{lettres[i]})</span>'
            + ('<br><span class="tag-robot">Robot</span>' if q.get("robot") else ""))


def entete(titre, n, total, corrige):
    return (f'<header><h1>{titre}{" — corrigé" if corrige else ""} ({n}/{total})</h1><span class="badge">NSI — Première</span></header>')


def pied(n):
    return ('<footer><span>NSI — Première &nbsp;|&nbsp; Langages et programmation</span>'
            f'<span>Conditions, boucles et fonctions — Contrôle ({n})</span>'
            + credit("cc-prem-conditions-boucles-fonctions") + '</footer>')


def h2(n, titre, pts, robot=False):
    return (f'<h2><span class="exo-num">{n}</span> {titre}' + (' <span class="tag-robot">Robot</span>' if robot else "")
            + f'<span class="pts">{pts}</span></h2>')


CASE = '<span class="case"></span>'
COCHE = '<span class="case oui">✕</span>'


def cours(corrige):
    s = [h2(1, "Questions de cours", "4 points")]
    s.append('<div class="cours"><div class="vf"><p class="consigne">Coche V (vraie) ou F (fausse). <span class="pp">0,5 point par ligne</span></p>')
    for i, (t, v, e) in enumerate(VF):
        cv, cf = (COCHE if v else CASE, CASE if v else COCHE) if corrige else (CASE, CASE)
        ex = f'<p class="rep-t">{e}</p>' if corrige else ""
        s.append(f'<div class="vfl"><span class="lbl">{"abcd"[i]})</span><span class="vft">{t}{ex}</span><span class="vfc">{cv} V {cf} F</span></div>')
    s.append('</div>')
    qcm = []
    for i, (t, opts, bon, e) in enumerate(QCM):
        code = pre(QCM_CODE[i]) if QCM_CODE[i] else ""
        b = [f'<div class="qc q{"eg"[i]}"><p class="stmt"><span class="lbl">{"eg"[i]})</span> <span class="pp">(0,5 point)</span> {t} Coche la bonne réponse.</p>{code}<div class="opts{" o4" if not code else ""}">']
        for k, o in enumerate(opts):
            b.append(f'<span>{COCHE if corrige and k == bon else CASE} {o}</span>')
        b.append("</div>" + (f'<p class="rep-t">{e}</p>' if corrige else "") + "</div>")
        qcm.append("".join(b))
    s.append(qcm[0])
    s.append(f'<div class="qc"><p class="stmt"><span class="lbl">f)</span> <span class="pp">(1 point)</span> Relie chaque mot-clé à son rôle.</p><div class="relier">')
    for k in range(4 if not corrige else 0):
        mot = RELIER[k][0]
        role = RELIER[RELIER_DROITE[k]][1]
        lien = ""
        s.append(f'<span class="rg"><code>{mot}</code>{lien} •</span><span class="rd">• {role}</span>')
    if corrige:
        s.append("".join(f'<span class="rg"><code>{m}</code></span><span class="rd rep-t">→ {r}</span>' for m, r in RELIER))
    s.append("</div></div>" + qcm[1] + "</div>")
    return "".join(s)


def erreur(i, q, corrige):
    msg = ""
    if q.get("msg"):
        lignes_msg = html.escape(q["msg"]).split("\n")
        lignes_msg[-1] = f"<b>{lignes_msg[-1]}</b>"
        msg = '<pre class="console">' + "\n".join(lignes_msg) + "</pre>"
    obs = f'<p class="cap">{q["obs"]}</p>' if q.get("obs") else ""
    cap = f'<p class="stmt">{q["q"]}</p>'
    if corrige:
        rep = f'{pre(q["fix"], cls="py fixe")}<p class="rep-t">{q["exp"]}</p>'
    else:
        rep = lignes(3)
    return (f'<div class="q3 e"><div class="ql">{etiq(i, q)}</div><div class="ecm"><div>{pre(q["code"])}</div>'
            f'<div>{msg}{obs}</div></div><div>{cap}{rep}</div></div>')


def document(corrige):
    T = "Conditions, boucles et fonctions — Contrôle"
    NP = 6 if corrige else 5
    P = []
    # ---- page 1
    s = ['<div class="page p1">', entete(T, 1, NP, corrige)]
    s.append('<div class="ident"><span>Nom&nbsp;:</span><span>Prénom&nbsp;:</span><span class="small">Classe&nbsp;:</span><span class="small">Note&nbsp;: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; / 20</span></div>')
    s.append('<div class="tip-box bar"><b>Barème.</b> 1. Cours : 4 points ; 2. Traduire : 1 ; 3. Erreurs : 4 ; 4. Robot : 3 ; 5. Compléter : 2,5 ; problème : 5,5. '
             'Les points sont donnés à côté de chaque question. On répond sur le sujet. <b>Durée : 1 h 30.</b></div>')
    s.append(cours(corrige))
    s.append(h2(2, "Que veut dire ce code&nbsp;?", "1 point (2 × 0,5)"))
    s.append('<p class="consigne">Traduis chaque programme par une phrase en français. <span class="pp">Le programme b) commande le robot : rappel de ses instructions en haut de la page 3.</span></p><div class="qlist">')
    for i, q in enumerate(EX1):
        rep = f'<p class="rep-t">{q["rep"]}</p>' if corrige else lignes(4)
        s.append(f'<div class="q"><div class="ql">{etiq(i, q)}</div>{pre(q["code"])}{rep}</div>')
    s.append("</div>" + pied(1) + "</div>")
    P.append("".join(s))
    # ---- page 2
    s = ['<div class="page p2">', entete(T, 2, NP, corrige)]
    s.append(h2(3, "Trouve l'erreur", "4 points (4 × 1)"))
    s.append('<p class="consigne">Chaque programme contient une erreur. Pour chacun : corrige l\'erreur (écris la ligne corrigée ou ajoutée, et sa place), puis explique-la en quelques mots. <span class="pp">1 point par programme : 0,5 pour la correction, 0,5 pour l\'explication.</span></p><div class="e2">')
    for i, q in enumerate(EX2):
        s.append(erreur(i, q, corrige))
    s.append("</div>" + pied(2) + "</div>")
    P.append("".join(s))
    # ---- page 3 : le robot (rappel en tête)
    s = ['<div class="page p3 robot">', entete(T, 3, NP, corrige)]
    s.append(RAPPEL)
    s.append(h2(4, "Où arrive le robot&nbsp;?", "3 points (6 × 0,5)", True))
    s.append('<p class="consigne">Le robot part de A6. Pour chaque programme, note la case d\'arrivée (tu peux tracer le trajet sur la grille pour t\'aider : il n\'est pas noté). Pour le programme e), note aussi ce qu\'il affiche.</p><div class="r8">')
    for i, q in enumerate(EX4):
        arr = f'<b class="rep-t">{q["arr"]}</b>' if corrige else "<span></span>"
        aff = ""
        if q.get("aff"):
            aff = '<div class="ans">f) Affichage&nbsp;: ' + (f'<b class="rep-t">{q["affv"]}</b>' if corrige else "<span></span>") + "</div>"
        s.append(f'<div class="rr"><div class="rc"><div>{etiq(i, q)}</div>{pre(q["code"])}</div><div>'
                 f'{grille(G4["depart"], G4["obstacles"], 4.8, chemin=q["chemin"] if corrige else None)}'
                 f'<div class="ans">Arrivée&nbsp;: {arr}</div>{aff}</div></div>')
    s.append("</div>" + pied(3) + "</div>")
    P.append("".join(s))

    def partie(i, q):
        g = ""
        if q.get("g"):
            g = '<div class="pg">' + "".join(
                f'<div><div class="gn">Grille {k + 1}</div>{grille(x["depart"], x["obstacles"], 5.0, x["cible"], q["chemins"][k] if corrige else None, 6, 5)}</div>'
                for k, x in enumerate(q["g"])) + "</div>"
        if corrige:
            z = f'<div class="sol">{pre(q["sol"])}</div>'
        elif q.get("entete"):
            z = pre(q["entete"], cls="py tete") + lignes(q["lignes"])
        else:
            z = pre(q["code"], False, "py fill")
        return (f'<div class="pi{" large" if g else ""}"><p class="stmt"><span class="lbl">Partie {"ABCD"[i]}. {q["titre"]}</span> <span class="pp">({q["pts"]})</span><br>{q["stmt"]}</p>'
                f'<div class="pz{" avec" if g else ""}">{g}<div class="pl">{z}</div></div></div>')

    # ---- page 4 : compléter, puis le début du problème
    s = ['<div class="page p4">', entete(T, 4, NP, corrige)]
    s.append(h2(5, "Complète le code", "2,5 points"))
    s.append('<p class="consigne">Écris dans les cases.</p><div class="ex5">')
    for i, q in enumerate(EX3):
        w = " w4" if i == 0 else " w6" if i == 1 else " w5"
        s.append(f'<div class="item{w}"><p class="stmt">{etiq(i, q)} <span class="pp">({q["pts"]})</span> {q["stmt"]}</p>{pre(q["code"], corrige, "py fill")}</div>')
    s.append("</div>")
    s.append('<h2><span class="exo-num">P</span> Problème : le robot livreur du doukabé<span class="pts">5,5 points</span></h2>')
    s.append('<div class="info-box"><p>Un doukabé de Mamoudzou s\'équipe d\'un petit robot pour préparer et livrer ses commandes. '
             'Les quatre parties sont <b>indépendantes</b>. Pour les parties C et D, le robot se programme comme dans l\'exercice 4 et part toujours de A5.</p></div><div class="pb">')
    s.append(partie(0, PB[0]))
    s.append("</div>" + pied(4) + "</div>")
    P.append("".join(s))
    # ---- page 5 : la suite du problème
    s = ['<div class="page p5">', entete(T, 5, NP, corrige)]
    s.append('<h2><span class="exo-num">P</span> Problème (suite)<span class="pts"></span></h2><div class="pb">')
    for i, q in enumerate(PB[1:], 1):
        s.append(partie(i, q))
    s.append("</div>" + pied(5) + "</div>")
    P.append("".join(s))
    if corrige:
        s = ['<div class="page p6">', entete(T, 6, 6, corrige)]
        s.append('<h2><span class="exo-num">✓</span> Barème détaillé et erreurs fréquentes<span class="pts">20 points</span></h2>')
        s.append('<p class="consigne">Une question, une réponse attendue ; quand elle a plusieurs trous, ses points se partagent entre eux : on cherche les points que la copie montre. <b>Toute fonction qui fait ce qui est demandé a tous les points</b>, même maladroite. <b>Une erreur de syntaxe mineure</b> dans un raisonnement juste (deux-points, parenthèse, guillemet, faute dans un nom) coûte 0 ou 0,25 au plus. <b>Une erreur ne se paie qu\'une fois</b> : une réponse juste à partir d\'une erreur précédente a ses points.</p>')
        s.append('<table class="bar-c"><tr><th>Question</th><th>Points</th><th>Ce qu\'on accepte</th><th>Erreur fréquente</th></tr>')
        for q, pts, detail, ok, err in BAREME:
            fr = lambda x: f"{x:g}".replace(".", ",")
            d = f"{len(detail)} × {fr(detail[0])}" if len(set(detail)) == 1 and len(detail) > 1 else " + ".join(fr(x) for x in detail)
            s.append(f"<tr><td>{q}</td><td>{fr(pts)}" + (f" ({d})" if len(detail) > 1 else "") + f"</td><td>{ok}</td><td>{err}</td></tr>")
        s.append("</table>" + pied(6) + "</div>")
        P.append("".join(s))
    titre = T + (" (corrigé)" if corrige else "")
    return (f'<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{titre}</title>{STYLE}<style>{PLUS}{PLUS2}</style></head><body>' + "".join(P) + "</body></html>")


# Barème détaillé : (question, points, détail des points, ce qu'on accepte, erreur fréquente possible sur CETTE forme).
# verifier() contrôle que chaque détail fait les points de sa ligne et que le tout fait 20 (règle « le corrigé se recalcule »).
BAREME = [
    ("1 a) à d) Vrai ou faux", 2, [0.5] * 4, "une case cochée par ligne", "a) : croire que <code>range(5)</code> va jusqu'à 5 ; d) : croire qu'une fonction s'exécute sans être appelée"),
    ("1 e) QCM", 0.5, [0.5], "une seule case cochée", "« une seule fois » : croire qu'une boucle s'exécute toujours au moins une fois"),
    ("1 f) Relier", 1, [0.25] * 4, "un trait par mot-clé", "relier <code>while</code> à « sinon, si… » (confondre boucle et condition)"),
    ("1 g) QCM", 0.5, [0.5], "une seule case cochée", "<code>or</code> au lieu de <code>and</code> (la condition est alors toujours vraie)"),
    ("2 a), b) Traduire", 1, [0.5, 0.5], "toute phrase juste ; b) : « le robot descend jusqu'à l'obstacle, puis va d'une case à l'ouest »", "b) : dire que le robot fait un seul pas vers le sud"),
    ("3 a) Erreur", 1, [0.5, 0.5], "correction : <code>int(input(…))</code> ; explication : <code>input</code> renvoie du texte, qu'on ne compare pas à un nombre", "corriger la ligne 2 (<code>if age >= \"18\":</code>) : l'erreur disparaît mais la comparaison se fait entre textes (0,25)"),
    ("3 b) Erreur", 1, [0.5, 0.5], "<code>n = n - 1</code> (ou <code>n -= 1</code>) dans la boucle ; explication : <code>n</code> ne change pas, la condition reste vraie", "la ligne ajoutée sans indentation, hors de la boucle (elle ne s'exécute jamais)"),
    ("3 c) Erreur", 1, [0.5, 0.5], "<code>return resultat</code> (ou <code>return 2 * x</code>) dans la fonction ; explication : sans <code>return</code>, la fonction renvoie <code>None</code>", "<code>print(resultat)</code> dans la fonction : on affiche au lieu de renvoyer, l'erreur reste"),
    ("3 d) Erreur", 1, [0.5, 0.5], "<code>total = 0</code> avant la boucle ; explication : il est remis à 0 à chaque tour", "supprimer la ligne : <code>total</code> n'existe plus (<code>NameError</code>)"),
    ("4 a) à e) Arrivée", 2.5, [0.5] * 5, "la case seule (le tracé n'est pas noté)", "d) : oublier que <code>avancer(4)</code> fait 4 pas"),
    ("4 f) Affichage", 0.5, [0.5], "<code>3</code>", "compter les pas vers le nord avec ceux vers l'est"),
    ("5 a) De 1 à 10", 0.5, [0.5], "<code>11</code>", "<code>10</code> : la borne de fin n'est pas comprise"),
    ("5 b) Radar", 1, [0.25] * 4, "<code>&lt;</code>, <code>elif</code>, <code>&lt;=</code>, <code>else</code>", "<code>&lt;=</code> à la première case : 50 donnerait « OK »"),
    ("5 c) Bouchon", 1, [0.25, 0.5, 0.25], "<code>&gt;</code>, <code>voitures - 4</code>, <code>minutes + 1</code> ; <code>&gt;=</code> est accepté ici, mais il ne donne le bon résultat que parce que 30 n'est pas un multiple de 4 : le signaler à l'élève", "oublier <code>voitures =</code> : la file ne diminue jamais"),
    ("P A Frais", 2, [2], "toute fonction juste a les 2 points, même maladroite ; sinon : 0,5 le test, 0,5 chaque <code>return</code>, 0,5 la structure <code>if … else</code>. <code>&gt;</code> au lieu de <code>&gt;=</code> : 1,5 (<code>frais(30)</code> serait faux)", "<code>print</code> au lieu de <code>return</code> : 1 au plus"),
    ("P B Tournées", 1, [0.5, 0.5], "<code>total + 8</code>, <code>total</code>", "<code>total = 8</code> : on affiche toujours 8"),
    ("P C Colis", 1, [0.5, 0.5], "<code>not obstacleEst()</code>, <code>nord()</code>", "<code>obstacleEst()</code> sans <code>not</code> : le robot ne bouge pas vers l'est"),
    ("P D Client", 1.5, [1.5], "<code>for i in range(3):</code> (toute boucle qui fait 3 tours)", "<code>while not obstacleNord():</code> : le robot s'arrête trop tôt ou s'écrase"),
]

PLUS2 = """
.cours { display: grid; grid-template-columns: 1fr 1fr; column-gap: 10px; }
.cours .vf { grid-column: 1 / -1; }
.vfl { display: grid; grid-template-columns: 6mm 1fr auto; align-items: start; padding: 4px 0; border-bottom: 1px dotted #c9ced8; }
.vfc { white-space: nowrap; padding-left: 8px; }
.case { display: inline-block; width: 3.4mm; height: 3.4mm; border: 1.2px solid #3a4152; border-radius: 1px; vertical-align: -0.5mm; margin-left: 6px; text-align: center; line-height: 3.2mm; font-size: 8pt; }
.case.oui { color: #0b5cad; font-weight: 700; border-color: #0b5cad; }
.qc { border: 1.5px solid var(--border); border-radius: 4px; padding: 5px 8px 7px; margin-top: 7px; }
.opts { row-gap: 6px !important; }
.qc.qg { grid-column: 1 / -1; }
.qc pre { margin: 2px 0 4px; }
.opts.o4 { grid-template-columns: 1fr 1fr; }
.opts { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 10px; }
.opts .case { margin-left: 0; margin-right: 3px; }
.relier { display: grid; grid-template-columns: auto 1fr; column-gap: 16mm; row-gap: 4px; align-items: center; }
.relier .rg { text-align: right; } .relier .rd { text-align: left; }
.pp { color: var(--muted); font-size: .92em; font-weight: 400; }
pre.console { background: #fff; border: 1px solid #9aa3b2; border-left: 3px solid #9aa3b2; font-size: 7.6pt; line-height: 1.3; padding: 3px 6px; margin: 3px 0 2px; white-space: pre; overflow-x: auto; }
.q3.e .stmt { margin: 2px 0 0; font-weight: 600; }
.q3.e .lines i { height: 8mm; }
.e2 { grid-template-columns: minmax(0, 1fr); gap: 4px; }
.ecm { display: grid; grid-template-columns: minmax(0, 0.62fr) minmax(0, 1.38fr); column-gap: 8px; align-items: start; }
.ecm pre { margin: 0; }
.q3.e > div { min-width: 0; }
pre.console { white-space: pre; font-size: 7pt; margin: 0; overflow: visible; }
.pb { grid-template-columns: minmax(0, 1fr); }
.pi .pz:not(.avec) { display: grid; grid-template-columns: minmax(0, 1fr); }
.pz.avec { grid-template-columns: auto minmax(0, 1fr); }
.pl { min-width: 0; }
.page div.relier { grid-template-columns: auto auto !important; justify-content: start; }
@media (max-width: 840px) { .relier { column-gap: 8mm; } .cours { grid-template-columns: 1fr; } pre.fill { white-space: pre; overflow-x: auto; } }
.p4 pre.fill { line-height: 2.1; } .p4 .ex5 { gap: 6px; }
.p4 .pi .lines i, .p5 .pi .lines i { height: 7.6mm; }
.bar-c { width: 100%; border-collapse: collapse; font-size: 8.6pt; margin-top: 6px; }
.bar-c th, .bar-c td { border: 1px solid #9aa3b2; padding: 3px 5px; vertical-align: top; text-align: left; }
.bar-c th { background: #eef1f6; color: #1a2a6c; font-weight: 700; }
.bar-c td:nth-child(2) { white-space: nowrap; }
.pi:not(.large) .lines { margin-left: 0; }
"""


STYLE = ""
if __name__ == "__main__":
    ici = os.path.dirname(os.path.abspath(__file__))
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(ici)
    td = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ici, "..", "..", "revision-conditions-boucles", "source", "style-td.html")
    STYLE = re.search(r"<style.*?</style>", open(td, encoding="utf-8").read(), flags=re.S).group(0)
    for k, v in verifier().items():
        print(k, v)
    open(f"{d}/controle-1re.html", "w", encoding="utf-8").write(document(False))
    open(f"{d}/controle-1re-corrige.html", "w", encoding="utf-8").write(document(True))
