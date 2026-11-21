"""Corrigé du TP « S'entraîner à utiliser des listes » (exercices-listes-fonctions).
Pour chaque exercice : la correction est exécutée (Python 3.13), puis les tests de la page
sont lancés sur elle ; les exemples de la consigne sont calculés par la correction.
  python3 -I corrige-listes-fonctions.py              vérifie tout
  python3 -I corrige-listes-fonctions.py --html F     écrit aussi les questions (HTML) dans F
"""
import sys

# (titre, signature, consigne, correction, appels de test, coups de pouce, explication)
EXERCICES = [
    ("Moyenne", "moyenne(liste)", "renvoie la moyenne des éléments de <code>liste</code>",
     """def moyenne(liste):
    total = 0
    for x in liste:
        total = total + x
    return total / len(liste)""",
     ["moyenne([12, 15, 9])", "moyenne([10, 11])", "moyenne([7])"],
     ["La moyenne, c'est la somme des éléments divisée par leur nombre.",
      "Additionne les éléments dans une variable <code>total</code> avec une boucle, puis divise par <code>len(liste)</code>."],
     "On additionne avec une boucle, puis on divise par le nombre d'éléments. En une ligne : <code>sum(liste) / len(liste)</code>."),
    ("Médiane", "mediane(liste)", "renvoie la médiane des éléments de <code>liste</code> (la liste n'est pas forcément triée)",
     """def mediane(liste):
    triee = sorted(liste)
    n = len(triee)
    if n % 2 == 1:
        return triee[n // 2]
    return (triee[n // 2 - 1] + triee[n // 2]) / 2""",
     ["mediane([3, 1, 2])", "mediane([4, 1, 3, 2])", "mediane([8, 3, 5, 9, 1])"],
     ["Commence par trier : <code>triee = sorted(liste)</code> donne une copie triée.",
      "Si le nombre d'éléments <code>n</code> est impair, la médiane est l'élément du milieu, d'indice <code>n // 2</code>.",
      "Si <code>n</code> est pair, c'est la moyenne des deux éléments du milieu, d'indices <code>n // 2 - 1</code> et <code>n // 2</code>."],
     "On trie, puis on prend l'élément du milieu (nombre impair d'éléments) ou la moyenne des deux du milieu (nombre pair)."),
    ("Diviseurs d'un entier", "diviseurs(n)", "renvoie la liste des diviseurs positifs de l'entier <code>n</code>, dans l'ordre croissant",
     """def diviseurs(n):
    resultat = []
    for d in range(1, n + 1):
        if n % d == 0:
            resultat.append(d)
    return resultat""",
     ["diviseurs(12)", "diviseurs(7)", "diviseurs(1)"],
     ["<code>d</code> divise <code>n</code> quand le reste <code>n % d</code> vaut 0.",
      "Pars d'une liste vide et essaie tous les <code>d</code> de 1 à <code>n</code> : <code>for d in range(1, n + 1):</code>."],
     "On essaie tous les entiers de 1 à <code>n</code>, dans l'ordre : la liste est donc déjà croissante."),
    ("Étendue", "etendue(liste)", "renvoie l'étendue de <code>liste</code> : la différence entre le plus grand et le plus petit élément",
     """def etendue(liste):
    plus_grand = liste[0]
    plus_petit = liste[0]
    for x in liste:
        if x > plus_grand:
            plus_grand = x
        if x < plus_petit:
            plus_petit = x
    return plus_grand - plus_petit""",
     ["etendue([4, 9, 2, 7])", "etendue([5, 5])", "etendue([-3, 10])"],
     ["Cherche le plus grand et le plus petit élément, puis fais la différence.",
      "Pars du premier élément, <code>liste[0]</code>, et compare-le à chaque élément dans une boucle."],
     "On cherche le maximum et le minimum en une seule boucle. En une ligne : <code>max(liste) - min(liste)</code>."),
    ("Doubles", "doubler(liste)", "renvoie la liste des doubles des nombres de <code>liste</code>",
     """def doubler(liste):
    resultat = []
    for x in liste:
        resultat.append(2 * x)
    return resultat""",
     ["doubler([1, 5, -2])", "doubler([])"],
     ["Construis une nouvelle liste : pars de <code>[]</code>.",
      "Pour chaque élément <code>x</code>, ajoute <code>2 * x</code> avec <code>append</code>."],
     "On construit une nouvelle liste. En compréhension : <code>[2 * x for x in liste]</code>."),
    ("Somme des éléments", "somme(liste)", "renvoie la somme des éléments de <code>liste</code>",
     """def somme(liste):
    total = 0
    for x in liste:
        total = total + x
    return total""",
     ["somme([3, 5, 2])", "somme([])", "somme([-4, 4, 10])"],
     ["Une variable <code>total</code>, qui vaut 0 avant la boucle, accumule les éléments."],
     "Un accumulateur qui part de 0. La somme d'une liste vide vaut 0. Python a aussi <code>sum(liste)</code>."),
    ("Produit des éléments", "produit(liste)", "renvoie le produit des éléments de <code>liste</code>",
     """def produit(liste):
    resultat = 1
    for x in liste:
        resultat = resultat * x
    return resultat""",
     ["produit([2, 3, 4])", "produit([5])", "produit([7, 0, 3])"],
     ["C'est comme la somme, mais avec <code>*</code>.",
      "Attention à la valeur de départ : si elle vaut 0, le produit vaudra toujours 0."],
     "Un accumulateur qui part de <b>1</b> (et non de 0) : 1 ne change pas un produit."),
    ("Nombre de pairs", "nombrePairs(liste)", "renvoie le nombre d'entiers pairs de <code>liste</code>, une liste d'entiers",
     """def nombrePairs(liste):
    compteur = 0
    for x in liste:
        if x % 2 == 0:
            compteur = compteur + 1
    return compteur""",
     ["nombrePairs([4, 7, 10, 3, 0])", "nombrePairs([1, 3])", "nombrePairs([-2, 8])"],
     ["Un entier <code>x</code> est pair quand <code>x % 2 == 0</code>.",
      "Un compteur part de 0 et augmente de 1 à chaque entier pair."],
     "Un compteur, qui augmente de 1 quand le reste de la division par 2 vaut 0. Attention : 0 est pair."),
    ("Nombre de négatifs", "nombreNegatifs(liste)", "renvoie le nombre de nombres négatifs de <code>liste</code>",
     """def nombreNegatifs(liste):
    compteur = 0
    for x in liste:
        if x < 0:
            compteur = compteur + 1
    return compteur""",
     ["nombreNegatifs([3, -1, 0, -7, 5])", "nombreNegatifs([2, 4])"],
     ["Un nombre est négatif quand il est strictement inférieur à 0 : 0 ne compte pas.",
      "Même structure que pour les pairs : un compteur et un <code>if</code>."],
     "Le même compteur que pour les pairs, avec la condition <code>x &lt; 0</code> (0 n'est pas négatif)."),
    ("Transformation", "zeroSiNegatif(liste)", "renvoie <code>liste</code> (une liste d'entiers relatifs) modifiée : chaque élément négatif est remplacé par 0",
     """def zeroSiNegatif(liste):
    for i in range(len(liste)):
        if liste[i] < 0:
            liste[i] = 0
    return liste""",
     ["zeroSiNegatif([3, -1, 0, -7, 5])", "zeroSiNegatif([-2])", "zeroSiNegatif([])"],
     ["Pour modifier un élément, il faut son indice : parcours avec <code>for i in range(len(liste)):</code>.",
      "Si <code>liste[i] &lt; 0</code>, écris <code>liste[i] = 0</code>. N'oublie pas de renvoyer la liste."],
     "On parcourt les <b>indices</b>, pour pouvoir écrire <code>liste[i] = 0</code>. Avec <code>for x in liste:</code>, changer <code>x</code> ne changerait pas la liste."),
]

AIDE_TESTS = ('def _verifier(appel, obtenu, attendu):\n'
              '    if obtenu is None and attendu is not None:\n'
              '        raise AssertionError(appel + " renvoie None : as-tu oublié return ?")\n'
              '    if isinstance(attendu, float):\n'
              '        juste = isinstance(obtenu, (int, float)) and abs(obtenu - attendu) < 1e-9\n'
              '    else:\n'
              '        juste = obtenu == attendu\n'
              '    assert juste, appel + " doit renvoyer " + repr(attendu) + " ; ta fonction renvoie " + repr(obtenu) + "."\n')


def nom(sig):
    return sig.split("(")[0]


def resultats(correction, appels):
    g = {}
    exec(correction, g)
    return [(a, eval(a, g)) for a in appels]


def tests(appels_res):
    lignes = [AIDE_TESTS]
    for a, r in appels_res:
        lignes.append(f"_verifier({a!r}, {a}, {r!r})")
    return "\n".join(lignes) + "\n"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def verifier():
    bilan = []
    for titre, sig, _, corr, appels, _, _ in EXERCICES:
        res = resultats(corr, appels)
        g = {}
        exec(corr, g)
        exec(compile(tests(res), "tests.py", "exec"), g)       # les tests de la page passent sur la correction
        # et refusent une fonction qui affiche au lieu de renvoyer
        g2 = {}
        exec(f"def {nom(sig)}(*a):\n    pass\n", g2)
        try:
            exec(compile(tests(res), "tests.py", "exec"), g2)
            raise SystemExit(titre + " : les tests acceptent une fonction sans return")
        except AssertionError:
            pass
        bilan.append((titre, res))
    return bilan


def html(bilan, premier=1):
    out = []
    for k, ((titre, sig, consigne, corr, appels, aides, expl), (_, res)) in enumerate(zip(EXERCICES, bilan)):
        fichier = nom(sig).lower() + ".py"
        exemples = " ; ".join(f"<code>{esc(a)}</code> renvoie <code>{esc(repr(r))}</code>" for a, r in res[:2])
        depart = f"def {sig}:\n    # À compléter\n    pass\n\n\n# Programme principal : tes tests\nprint({esc(appels[0])})\n"
        principal = "\n".join(f"print({esc(a)})" for a in appels)
        out.append(
            f'  <h2 class="td-partie">{k + 1}. {titre}</h2>\n'
            f'  <section class="td-q" data-type="code" data-obligatoire id="q{premier + k}" data-fichier="{fichier}">\n'
            f'    <p class="td-consigne">Écris une fonction <code>{esc(sig)}</code> qui {consigne}. Puis teste-la dans le programme principal.</p>\n'
            f'    <p>Par exemple, {exemples}.</p>\n'
            f'    <pre class="td-depart">\n{depart}</pre>\n'
            f'    <script type="text/x-python" class="td-tests">\n{tests(res)}</script>\n'
            + "".join(f'    <p class="td-aide">{a}</p>\n' for a in aides) +
            f'    <div class="td-correction"><pre class="td-code" data-verifier="correction">\n{esc(corr)}\n\n\n{principal}</pre>'
            f'<p>{expl}</p></div>\n'
            f'  </section>\n\n')
    return "".join(out)


if __name__ == "__main__":
    bilan = verifier()
    for titre, res in bilan:
        print(f"{titre:22}", " ; ".join(f"{a} = {r!r}" for a, r in res))
    print(f"{len(bilan)} exercices : corrections exécutées, tests de la page passés (et refusant une fonction sans return).")
    if "--html" in sys.argv:
        open(sys.argv[sys.argv.index("--html") + 1], "w", encoding="utf-8").write(html(bilan))
