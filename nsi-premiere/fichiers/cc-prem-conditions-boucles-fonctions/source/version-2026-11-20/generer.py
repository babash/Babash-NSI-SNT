"""Contrôle de Première : conditions, boucles, fonctions. Sujet et corrigé, réponses vérifiées par exécution.

La feuille de style est celle des anciens TD « Bases python » : nsi-premiere/fichiers/revision-conditions-boucles/source/style-td.html
(copie de la feuille du TD récapitulatif avant sa conversion au style « Signal pirate », T125 ; les contrôles restent tels quels).
Les outils (robot, code coloré, grilles) sont dans outils.py, le même fichier que pour la séance de révision.

Régénérer, depuis ce dossier source/ :
    python3 generer.py
    python3 pdf.py .. controle-1re controle-1re-corrige
"""
import os, re, sys
from outils import (COLS, NL, Ecrase, pos, nom, lancer, colorer, pre, plein,
                    ROBOT, OBST, CIBLE, grille, lignes, PLUS, credit)

# ---------------------------------------------------------------- contenu
G4 = dict(depart="A6", obstacles=["A2", "C2", "B4", "D4", "D6", "F5", "E3", "G3"])
GC = [dict(depart="A5", obstacles=["E5", "D2", "B3", "F1"], cible="D3"),
      dict(depart="A5", obstacles=["C5", "B1", "E3", "D4"], cible="B2"),
      dict(depart="A5", obstacles=["C3", "D1", "B2"], cible="F1")]
GD = [dict(depart="A5", obstacles=["C5", "E4", "B2", "D1"], cible="F2"),
      dict(depart="A5", obstacles=["D5", "E4", "F3", "A2", "C1"], cible="E2"),
      dict(depart="A5", obstacles=["B5", "D4", "E3", "F5", "B1"], cible="D2")]

EX1 = [
    dict(robot=False, code='if note >= 16:\n    print("Très bien")\nelif note >= 10:\n    print("Admis")\nelse:\n    print("Refusé")',
         rep="Si la note vaut au moins 16, on affiche « Très bien » ; sinon, si elle vaut au moins 10, on affiche « Admis » ; sinon, on affiche « Refusé »."),
    dict(robot=True, code="while not obstacleSud():\n    sud()\nouest()",
         rep="Tant qu'il n'y a pas d'obstacle au sud, le robot avance d'une case vers le sud : il descend jusqu'à l'obstacle (ou au bord). Ensuite, il avance d'une case vers l'ouest."),
    dict(robot=True, etoile=True, code="for i in range(5):\n    if obstacleEst():\n        nord()\n    else:\n        est()",
         rep="On répète 5 fois : s'il y a un obstacle à l'est, le robot monte d'une case vers le nord ; sinon, il avance d'une case vers l'est."),
]

EX2 = [
    dict(code='code = input("Code : ")\nif code = "976":\n    print("Bienvenue !")', syntaxe=True,
         fix='if code == "976":', exp="= range une valeur dans une variable ; pour comparer, on écrit ==.",
         bon='code = input("Code : ")\nif code == "976":\n    print("Bienvenue !")', entrees=["976"], attendu=["Bienvenue !"]),
    dict(code="n = 10\nwhile n > 0:\n    print(n)", q="Le programme affiche 10 sans jamais s'arrêter. Pourquoi ?",
         fix="    n = n - 1", exp="n ne change jamais : la condition n > 0 reste vraie. On ajoute cette ligne dans la boucle.",
         bon="n = 10\nwhile n > 0:\n    print(n)\n    n = n - 1", attendu=[str(i) for i in range(10, 0, -1)]),
    dict(robot=True, code="while not obstacleEst()\n    est()", syntaxe=True,
         fix="while not obstacleEst():", exp="Il manque les deux-points à la fin de la ligne du while.",
         bon="while not obstacleEst():\n    est()"),
    dict(code="for i in range(1, 5):\n    total = 0\n    total = total + i\nprint(total)", q="Il doit afficher 10 (= 1 + 2 + 3 + 4), mais il affiche 4. Pourquoi ?",
         fix="total = 0   (avant le for)", exp="total est remis à 0 à chaque tour. Il faut l'initialiser une seule fois, avant la boucle.",
         bon="total = 0\nfor i in range(1, 5):\n    total = total + i\nprint(total)", attendu=["10"], faux=["4"]),
    dict(code='temperature = 35\nif temperature > 20:\n    print("Doux")\nelif temperature > 30:\n    print("Chaud")', q="Avec 35, il doit afficher « Chaud », mais il affiche « Doux ». Pourquoi ?",
         fix="if temperature > 30:   (tester 30 en premier)", exp="35 > 20 est déjà vrai : le elif n'est jamais regardé. On teste d'abord > 30, puis > 20.",
         bon='temperature = 35\nif temperature > 30:\n    print("Chaud")\nelif temperature > 20:\n    print("Doux")', attendu=["Chaud"], faux=["Doux"]),
    dict(etoile=True, code='nb = 0\nfor lettre in "Mamoudzou":\n    if lettre == "o":\n        nb = nb + 1\n        print(nb)',
         q="Il doit afficher une seule fois le nombre de « o » (2), mais il affiche 1 puis 2. Pourquoi ?",
         fix="print(nb)   (sans indentation)", exp="print est dans le if : il s'exécute à chaque « o ». Il doit être après la boucle, tout à gauche.",
         bon='nb = 0\nfor lettre in "Mamoudzou":\n    if lettre == "o":\n        nb = nb + 1\nprint(nb)', attendu=["2"], faux=["1", "2"]),
]

EX3 = [
    dict(stmt="<b>De 1 à 10.</b> Le programme affiche les nombres de 1 à 10, un par ligne.",
         code="for i in range(⟦1⟧, ⟦11⟧):\n    print(i)", tests=[("", [str(i) for i in range(1, 11)])]),
    dict(stmt="<b>Radar.</b> Strictement moins de 50 km/h : «&nbsp;OK&nbsp;». De 50 à 70 km/h : «&nbsp;Ralentis&nbsp;». Au-delà : «&nbsp;Amende&nbsp;».",
         code='if vitesse ⟦<⟧ 50:\n    print("OK")\n⟦elif⟧ vitesse ⟦<=⟧ 70:\n    print("Ralentis")\n⟦else⟧:\n    print("Amende")',
         tests=[("vitesse = 49\n", ["OK"]), ("vitesse = 50\n", ["Ralentis"]), ("vitesse = 70\n", ["Ralentis"]), ("vitesse = 71\n", ["Amende"])]),
    dict(stmt="<b>Bouchon vers Mamoudzou.</b> 30 voitures attendent. Chaque minute, 4 voitures passent. Le programme affiche le nombre de minutes pour que la file soit vide.",
         code="voitures = 30\nminutes = 0\nwhile voitures ⟦>⟧ 0:\n    voitures = ⟦voitures - 4⟧\n    minutes = ⟦minutes + 1⟧\nprint(minutes)",
         tests=[("", ["8"])], apres="Le programme affiche : ", val="8"),
    dict(etoile=True, stmt="<b>Distributeur.</b> Solde : 50&nbsp;€. On demande des retraits jusqu'à ce qu'on tape 0. Un retrait est refusé si le solde ne suffit pas. On affiche le solde final.",
         code='solde = 50\nretrait = int(input("Retrait : "))\nwhile retrait ⟦!=⟧ 0:\n    if retrait ⟦<=⟧ solde:\n        solde = ⟦solde - retrait⟧\n    ⟦else⟧:\n        print("Solde insuffisant")\n    retrait = int(input("Retrait : "))\nprint(solde)',
         tests=[("", ["Solde insuffisant", "20"])], entrees=["20", "40", "10", "0"]),
]

EX4 = [
    dict(code="est()\nif obstacleNord():\n    est()\nelse:\n    nord()"),
    dict(code="for i in range(2):\n    est()\n    nord()"),
    dict(code="while not obstacleEst():\n    est()\nnord()"),
    dict(code="nord()\nnord()\nif obstacleNord():\n    est()\nelif obstacleEst():\n    nord()\nelse:\n    sud()"),
    dict(code="def avancer(n):\n    for i in range(n):\n        est()\n\nnord()\navancer(4)\nnord()\navancer(2)"),
    dict(code="pas = 0\nfor i in range(3):\n    nord()\nwhile not obstacleEst():\n    est()\n    pas = pas + 1\nprint(pas)", aff=True),
    dict(etoile=True, code="for i in range(6):\n    if not obstacleNord():\n        nord()\n    else:\n        est()"),
    dict(etoile=True, code="nb = 0\nnord()\nwhile not obstacleEst():\n    est()\n    if obstacleNord():\n        nb = nb + 1\nprint(nb)", aff=True),
]

PB = [
    dict(titre="Les frais de livraison", pts=2, entete="def frais(montant):",
         stmt="La livraison est <b>gratuite</b> si le montant de la commande vaut <b>au moins 30&nbsp;€</b>. Sinon, elle coûte <b>3&nbsp;€</b>.<br>Complète la fonction <code>frais(montant)</code> : elle renvoie le prix de la livraison. Exemples : <code>frais(45)</code> renvoie 0 et <code>frais(12)</code> renvoie 3.",
         sol="def frais(montant):\n    if montant >= 30:\n        return 0\n    else:\n        return 3", lignes=5),
    dict(titre="Les tournées", pts=2, entete="def colis_livres(n):",
         stmt="Le robot livre <b>8 colis par tournée</b>.<br>Complète la fonction <code>colis_livres(n)</code> : elle affiche le nombre total de colis livrés après chaque tournée, de la 1<sup>re</sup> à la <code>n</code><sup>e</sup>. Exemple : <code>colis_livres(3)</code> affiche 8, puis 16, puis 24.",
         sol="def colis_livres(n):\n    for i in range(1, n + 1):\n        print(i * 8)", lignes=5),
    dict(titre="Aller chercher le colis", pts=2, g=GC,
         stmt="Écris <b>un seul programme</b> qui amène le robot jusqu'au colis <b>★</b> sur <b>les trois grilles</b>. Il utilise <b>deux boucles, l'une après l'autre</b>.",
         sol="while not obstacleEst():\n    est()\nwhile not obstacleNord():\n    nord()", piege="for i in range(3):\n    est()\nfor i in range(2):\n    nord()", lignes=5),
    dict(titre="Livrer le client", pts=2, g=GD,
         stmt="Écris <b>un seul programme</b> qui amène le robot jusqu'au client <b>★</b> sur <b>les trois grilles</b>. Il utilise <b>une boucle dans une boucle</b>. <i>Observe : sur chaque grille, le robot refait 3 fois le même trajet.</i>",
         sol="for i in range(3):\n    while not obstacleEst():\n        est()\n    nord()", piege="for i in range(3):\n    for j in range(2):\n        est()\n    nord()", lignes=5),
]


# ---------------------------------------------------------------- vérifications
def verifier():
    r = {}
    for q in EX1:
        if not q["robot"]:
            try:
                _, aff = lancer(q["code"], "A1", [])
                q["rep"] = q["rep"].format(aff=" ".join(aff))
            except NameError:
                pass
    lancer("note = 12\n" + EX1[0]["code"], "A1", [])
    for i, q in enumerate(EX2):
        if q.get("syntaxe"):
            try:
                compile(q["code"], "x", "exec"); raise AssertionError("devrait être une erreur de syntaxe")
            except SyntaxError:
                pass
        else:
            compile(q["code"], "x", "exec")
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
            got = lancer(avant + plein(q["code"]) + q.get("suite", ""), "A1", [], q.get("entrees", ()))[1]
            assert got == att, (i, got)
    for i, q in enumerate(EX4):
        ch, aff = lancer(q["code"], G4["depart"], G4["obstacles"])
        q["chemin"], q["arr"], q["affv"] = ch, nom(ch[-1]), " ".join(aff)
        assert bool(aff) == bool(q.get("aff")), i
        r[f"4{'abcdefgh'[i]}"] = (q["arr"], q["affv"], len(ch) - 1)
    assert len({q["arr"] for q in EX4}) == 8, "arrivées toutes différentes"
    assert lancer(PB[0]["sol"] + "\nprint(frais(45), frais(12), frais(30), frais(29))", "A1", [])[1] == ["0 3 0 3"]
    assert lancer(PB[1]["sol"] + "\ncolis_livres(3)\ncolis_livres(10)", "A1", [])[1] == ["8", "16", "24"] + [str(8 * i) for i in range(1, 11)]
    for q in PB[:2]:
        assert q["sol"].startswith(q["entete"] + "\n")
    for q in PB[2:]:
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


def etiq(i, q):
    return (f'<span class="lbl">{"abcdefgh"[i]})</span>' + (' <span class="et">★</span>' if q.get("etoile") else "")
            + ('<br><span class="tag-robot">Robot</span>' if q.get("robot") else ""))


def entete(titre, n, total, corrige):
    return (f'<header><h1>{titre}{" — corrigé" if corrige else ""} ({n}/{total})</h1><span class="badge">NSI — Première</span></header>')


def pied(n):
    return ('<footer><span>NSI — Première &nbsp;|&nbsp; Langages et programmation</span>'
            f'<span>Conditions, boucles et fonctions — Contrôle ({n})</span>'
            + credit("cc-prem-conditions-boucles-fonctions") + '</footer>')


RAPPEL = ('<div class="info-box ctx"><div><h3>Rappel&nbsp;: le robot</h3><ul>'
          "<li><code>nord()</code>, <code>sud()</code>, <code>est()</code>, <code>ouest()</code>&nbsp;: déplace le robot d'<b>une case</b> dans cette direction&nbsp;;</li>"
          "<li><code>obstacleNord()</code>, <code>obstacleSud()</code>, <code>obstacleEst()</code>, <code>obstacleOuest()</code>&nbsp;: renvoie <code>True</code> si la case voisine est un <b>obstacle</b> ou le <b>bord</b>, <code>False</code> sinon&nbsp;;</li>"
          "<li>si le robot avance vers un obstacle ou le bord, il <b>s'écrase</b>&nbsp;: le programme s'arrête avec une erreur.</li></ul></div>"
          '<div class="side"><svg width="58" height="58" viewBox="0 0 60 60" aria-label="rose des vents"><circle cx="30" cy="30" r="17" fill="none" stroke="#d5dae2"/><path d="M30 10L33 30L30 50L27 30Z" fill="#1a2a6c"/><path d="M10 30L30 27L50 30L30 33Z" fill="#9aa3b2"/><text x="30" y="8" text-anchor="middle" font-size="9" font-weight="700" fill="#1a2a6c">N</text><text x="30" y="59" text-anchor="middle" font-size="9" font-weight="700" fill="#5a6273">S</text><text x="57" y="33" text-anchor="middle" font-size="9" font-weight="700" fill="#5a6273">E</text><text x="3" y="33" text-anchor="middle" font-size="9" font-weight="700" fill="#5a6273">O</text></svg>'
          f'<div class="leg">{ROBOT.format(t=15)}robot<br>{OBST.format(t=15)}obstacle</div></div></div>')


def h2(n, titre, pts, robot=False):
    return (f'<h2><span class="exo-num">{n}</span> {titre}' + (' <span class="tag-robot">Robot</span>' if robot else "")
            + f'<span class="pts">{pts}</span></h2>')


def document(corrige):
    T = "Conditions, boucles et fonctions — Contrôle"
    P = []
    # ---- page 1
    s = [f'<div class="page p1">', entete(T, 1, 4, corrige)]
    s.append('<div class="ident"><span>Nom&nbsp;:</span><span>Prénom&nbsp;:</span><span class="small">Classe&nbsp;:</span><span class="small">Note&nbsp;: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; / 20</span></div>')
    s.append('<div class="tip-box bar"><b>Barème.</b> Exercices 1 à 4 : 12 points (traduire 1,5 ; erreurs 1,5 ; compléter 4 ; robot 5). Problème : 8 points. '
             'Les questions marquées ★ sont plus difficiles. On répond sur le sujet. <b>Durée : 1 h 30.</b></div>')
    s.append(h2(1, "Que veut dire ce code&nbsp;?", "1,5 point (3 × 0,5)"))
    s.append('<p class="consigne">Traduis chaque programme par une phrase en français.</p><div class="qlist">')
    for i, q in enumerate(EX1):
        rep = f'<p class="rep-t">{q["rep"]}</p>' if corrige else lignes(q.get("lignes", 3))
        s.append(f'<div class="q"><div class="ql">{etiq(i, q)}</div>{pre(q["code"])}{rep}</div>')
    s.append("</div>")
    s.append(h2(2, "Trouve l'erreur", "1,5 point (6 × 0,25)"))
    s.append('<p class="consigne">Entoure l\'erreur, écris la ligne corrigée (ou la ligne à ajouter) et explique en quelques mots.</p><div class="e2">')
    for i, q in enumerate(EX2):
        s.append(erreur(i, q, corrige))
    s.append("</div>" + pied(1) + "</div>")
    P.append("".join(s))
    # ---- page 2
    s = ['<div class="page p2">', entete(T, 2, 4, corrige)]
    s.append(h2(3, "Complète le code", "4 points (4 × 1)"))
    s.append('<p class="consigne">Écris dans les cases.</p><div class="ex5">')
    for i, q in enumerate(EX3):
        ap = ""
        if q.get("apres"):
            ap = f'<div class="ans">{q["apres"]}' + (f'<b class="rep-t">{q["val"]}</b>' if corrige else "<span></span>") + "</div>"
        w = " w6" if i in (1, 2) else " w4" if i in (0, 3) else ""
        w = " w4" if i == 0 else " w6" if i == 1 else " w5"
        s.append(f'<div class="item{w}"><p class="stmt">{etiq(i, q)} {q["stmt"]}</p>{pre(q["code"], corrige, "py fill")}{ap}</div>')
    s.append("</div>" + pied(2) + "</div>")
    P.append("".join(s))
    # ---- page 3
    s = ['<div class="page p3">', entete(T, 3, 4, corrige)]
    s.append(h2(4, "Où se trouve le robot&nbsp;?", "5 points", True))
    s.append('<p class="consigne">Le robot part de A6. Pour chaque programme, trace le trajet sur la grille et note la case d\'arrivée. Questions a) à d) : 0,5 point chacune ; e) à h) : 0,75 point chacune.</p><div class="r8">')
    for i, q in enumerate(EX4):
        arr = f'<b class="rep-t">{q["arr"]}</b>' if corrige else "<span></span>"
        aff = ""
        if q.get("aff"):
            aff = '<div class="ans">Affichage&nbsp;: ' + (f'<b class="rep-t">{q["affv"]}</b>' if corrige else "<span></span>") + "</div>"
        s.append(f'<div class="rr"><div class="rc"><div>{etiq(i, q)}</div>{pre(q["code"])}</div><div>'
                 f'{grille(G4["depart"], G4["obstacles"], 4.8, chemin=q["chemin"] if corrige else None)}'
                 f'<div class="ans">Arrivée&nbsp;: {arr}</div>{aff}</div></div>')
    s.append("</div>" + pied(3) + "</div>")
    P.append("".join(s))
    # ---- page 4
    s = ['<div class="page p4">', entete(T, 4, 4, corrige)]
    s.append('<h2><span class="exo-num">P</span> Problème : le robot livreur du doukabé<span class="pts">8 points (4 × 2)</span></h2>')
    s.append('<div class="info-box"><p>Un doukabé de Mamoudzou s\'équipe d\'un petit robot pour préparer et livrer ses commandes. '
             'Les quatre parties sont <b>indépendantes</b>. Pour les parties C et D, le robot se programme comme dans les exercices 1 et 4 (<code>nord()</code>, <code>est()</code>, <code>obstacleNord()</code>, <code>obstacleEst()</code>…) et part toujours de A5.</p></div><div class="pb">')
    for i, q in enumerate(PB):
        g = ""
        if q.get("g"):
            g = '<div class="pg">' + "".join(
                f'<div><div class="gn">Grille {k + 1}</div>{grille(x["depart"], x["obstacles"], 5.2, x["cible"], q["chemins"][k] if corrige else None, 6, 5)}</div>'
                for k, x in enumerate(q["g"])) + "</div>"
        if corrige:
            z = f'<div class="sol">{pre(q["sol"])}</div>'
        else:
            z = (pre(q["entete"], cls="py tete") if q.get("entete") else "") + lignes(q["lignes"])
        s.append(f'<div class="pi{" large" if g else ""}"><p class="stmt"><span class="lbl">Partie {"ABCD"[i]}. {q["titre"]}</span> <span class="pp">({q["pts"]} points)</span><br>{q["stmt"]}</p>'
                 f'<div class="pz{" avec" if g else ""}">{g}<div class="pl">{z}</div></div></div>')
    s.append("</div>" + pied(4) + "</div>")
    P.append("".join(s))
    titre = T + (" (corrigé)" if corrige else "")
    return (f'<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{titre}</title>{STYLE}<style>{PLUS}</style></head><body>' + "".join(P) + "</body></html>")


def erreur(i, q, corrige):
    cap = f'<p class="cap">{q["q"]}</p>' if q.get("q") else ""
    if corrige:
        rep = f'{pre(q["fix"], cls="py fixe")}<p class="rep-t">{q["exp"]}</p>'
    else:
        rep = lignes(2)
    return f'<div class="q3 e"><div class="ql">{etiq(i, q)}</div><div>{pre(q["code"])}{cap}</div><div>{rep}</div></div>'


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
