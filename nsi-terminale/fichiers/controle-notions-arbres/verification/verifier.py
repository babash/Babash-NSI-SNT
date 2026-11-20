"""Vérifie la clé du contrôle de notions sur les arbres, par exécution.

Relit les données de controle.js et la clé de cle.js (blocs JSON entre
marqueurs), reconstruit chaque arbre avec la classe Noeud de l'énoncé, puis
recalcule toutes les réponses : racine, feuilles, taille, hauteur (convention
de l'énoncé), profondeur, ABR ou non, parcours, sortie de print(...),
ligne à compléter (exécutée), insertion dans un ABR.

Usage : python3 -I verification/verifier.py   (depuis le dossier du contrôle)
Babash - NSI Tani Malandi · MIT
"""
import json
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent.parent


def bloc(fichier, nom):
    texte = (ICI / fichier).read_text(encoding="utf-8")
    m = re.search(r"/\*" + nom + r"-DEBUT\*/(.*?)/\*" + nom + r"-FIN\*/", texte, re.S)
    return json.loads(m.group(1))


D = bloc("controle.js", "DONNEES")
CLE = bloc("cle.js", "CLE")

# La classe Noeud et la fonction taille, telles que dans l'énoncé
CODE = D["code_noeud"]
assert CODE.rstrip().endswith("return ................"), "ligne à compléter introuvable"


def construire(espace, t):
    if t is None:
        return None
    return espace["Noeud"](t[0], construire(espace, t[1]), construire(espace, t[2]))


def prefixe(a):
    return [] if a is None else [a.valeur] + prefixe(a.gauche) + prefixe(a.droit)


def infixe(a):
    return [] if a is None else infixe(a.gauche) + [a.valeur] + infixe(a.droit)


def largeur(a):
    file, res = [a], []
    while file:
        n = file.pop(0)
        res.append(n.valeur)
        file += [x for x in (n.gauche, n.droit) if x is not None]
    return res


def hauteur(a):
    # Convention de l'énoncé : un arbre réduit à un seul nœud a une hauteur de 0
    return -1 if a is None else 1 + max(hauteur(a.gauche), hauteur(a.droit))


def feuilles(a):
    if a is None:
        return []
    if a.gauche is None and a.droit is None:
        return [a.valeur]
    return feuilles(a.gauche) + feuilles(a.droit)


def profondeur(a, v, p=0):
    if a is None:
        return None
    if a.valeur == v:
        return p
    g = profondeur(a.gauche, v, p + 1)
    return g if g is not None else profondeur(a.droit, v, p + 1)


def est_abr(a, mini=float("-inf"), maxi=float("inf")):
    return a is None or (mini < a.valeur < maxi and est_abr(a.gauche, mini, a.valeur)
                         and est_abr(a.droit, a.valeur, maxi))


def avec_ligne(ligne):
    """Exécute l'énoncé avec la dernière ligne complétée ; renvoie son espace de noms."""
    espace = {}
    exec(CODE.replace("return ................", "return " + ligne), espace)
    return espace


erreurs = []


def verifier(cond, message):
    if not cond:
        erreurs.append(message)


ids = [q["id"] for q in D["questions"]]
verifier(ids == ["q" + str(i) for i in range(1, 13)], "les questions doivent être q1 à q12")

for s, sujet in D["sujets"].items():
    k = CLE[s]
    esp = avec_ligne("1 + taille(arbre.gauche) + taille(arbre.droit)")
    a = construire(esp, sujet["arbre"])
    attendu = {
        "q1": a.valeur,
        "q2": sorted(feuilles(a)),
        "q3": esp["taille"](a),
        "q4": hauteur(a),
        "q5": profondeur(a, sujet["noeud_profondeur"]),
        "q7": largeur(a),
        "q8": prefixe(a),
        "q9": infixe(a),
        "q10": eval(sujet["chemin"], {"a": a}),
    }
    for q, v in attendu.items():
        cle = sorted(k[q]["attendu"]) if q == "q2" else k[q]["attendu"]
        verifier(cle == v, f"sujet {s}, {q} : clé {cle}, calcul {v}")

    # Le print de la question 10, exécuté pour de vrai
    import io, contextlib
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie):
        exec("print(" + sujet["chemin"] + ")", {"a": a})
    verifier(sortie.getvalue().strip() == str(k["q10"]["attendu"]), f"sujet {s}, q10 : sortie {sortie.getvalue()!r}")

    # Q6 : la bonne option dit « Oui » si et seulement si l'arbre est un ABR
    options = dict(sujet["abr_options"])
    bonne = options[k["q6"]["attendu"]]
    verifier(bonne.startswith("Oui") == est_abr(a), f"sujet {s}, q6 : option {bonne!r}, ABR = {est_abr(a)}")
    verifier(sum(o.startswith("Oui") for o in options.values()) <= 1 or est_abr(a) is False, f"sujet {s}, q6 : plusieurs « Oui »")

    # Q11 : chaque ligne acceptée, exécutée, donne la taille ; les diagnostics donnent autre chose
    for ligne in k["q11"]["attendu"]:
        e = avec_ligne(ligne)
        verifier(e["taille"](construire(e, sujet["arbre"])) == attendu["q3"], f"sujet {s}, q11 : {ligne} faux")
    for faux in ["taille(arbre.gauche) + taille(arbre.droit)", "1 + max(taille(arbre.gauche), taille(arbre.droit))"]:
        e = avec_ligne(faux)
        verifier(e["taille"](construire(e, sujet["arbre"])) != attendu["q3"], f"sujet {s}, q11 : {faux} donne aussi la taille")
    e = avec_ligne("taille(arbre.gauche) + taille(arbre.droit)")
    verifier(e["taille"](construire(e, sujet["arbre"])) == 0, "q11 : sans « 1 + », la taille devrait valoir 0")

    # Q12 : insertion réelle dans un ABR vide, lue dans l'ordre des lettres du squelette
    def inserer(arbre, v):
        if arbre is None:
            return esp["Noeud"](v)
        if v < arbre.valeur:
            arbre.gauche = inserer(arbre.gauche, v)
        else:
            arbre.droit = inserer(arbre.droit, v)
        return arbre

    abr = None
    for v in sujet["insertion"]:
        abr = inserer(abr, v)
    cases = {}

    def lire(sq, n):
        if sq is None:
            verifier(n is None, f"sujet {s}, q12 : le squelette a une case vide en trop")
            return
        verifier(n is not None, f"sujet {s}, q12 : le squelette ne suit pas l'ABR obtenu")
        if n is None:
            return
        cases[sq[0]] = n.valeur
        lire(sq[1], n.gauche)
        lire(sq[2], n.droit)

    lire(sujet["squelette"], abr)
    calcul = [cases[l] for l in sorted(cases)]
    verifier(calcul == k["q12"]["attendu"], f"sujet {s}, q12 : clé {k['q12']['attendu']}, calcul {calcul}")
    verifier(sorted(calcul) == sorted(sujet["insertion"]), f"sujet {s}, q12 : valeurs différentes")

    # Aucun diagnostic « si » ne doit être la bonne réponse
    for q, entree in k.items():
        for d in entree.get("diag", []):
            if "si" in d:
                bon = entree["attendu"]
                verifier(d["si"] != bon and not (isinstance(bon, list) and d["si"] in bon),
                         f"sujet {s}, {q} : un diagnostic vaut la bonne réponse")

    # Les diagnostics « C'est le parcours … » donnent bien ce parcours
    def suffixe(n):
        return [] if n is None else suffixe(n.gauche) + suffixe(n.droit) + [n.valeur]

    nommes = {"préfixe": prefixe(a), "suffixe": suffixe(a), "infixe": infixe(a), "en largeur": largeur(a)}
    for q in ("q7", "q8", "q9"):
        for d in k[q]["diag"]:
            for nom, valeur in nommes.items():
                if d["texte"].startswith("C'est le parcours " + nom):
                    verifier(d["si"] == valeur, f"sujet {s}, {q} : le diagnostic « {nom} » ne donne pas ce parcours")
    for q, v in (("q3", len(feuilles(a))),):
        verifier(any(d.get("si") == v and "feuilles" in d["texte"] for d in k[q]["diag"]), f"sujet {s}, q3 : diagnostic du nombre de feuilles")

    print(f"Sujet {s} : racine {attendu['q1']}, feuilles {attendu['q2']}, taille {attendu['q3']}, "
          f"hauteur {attendu['q4']}, profondeur de {sujet['noeud_profondeur']} = {attendu['q5']}, ABR {est_abr(a)}")
    print(f"  largeur {attendu['q7']}\n  préfixe {attendu['q8']}\n  infixe  {attendu['q9']}")
    print(f"  print({sujet['chemin']}) -> {attendu['q10']} ; insertion -> {calcul}")

if erreurs:
    print("\nERREURS :")
    for e in erreurs:
        print(" -", e)
    sys.exit(1)
print("\nClé vérifiée : toutes les réponses sont recalculées par exécution.")
