"""Vérifie par exécution (Python 3.13) les réponses du TD-TP « Le bal des tris » (page HTML td-tp-tri/, T125).

Compteurs de comparaisons et d'échanges, déroulés pas à pas, fusions, ordres de grandeur du crash test
(avec le programme fourni aux élèves, td-tp-tri/crash-test.py).
Depuis la racine du dépôt :  python3 -I nsi-terminale/fichiers/algorithmes-tri-recherche-complexite/source/tester-td-tp-tri.py
"""
import importlib.util, itertools, math, os, random, sys

assert sys.version_info[:2] == (3, 13), "les réponses doivent venir de Python 3.13"
ICI = os.path.dirname(os.path.abspath(__file__))
erreurs = 0


def egal(nom, obtenu, attendu):
    global erreurs
    ok = obtenu == attendu
    erreurs += not ok
    print(f'  {nom} : {obtenu!r}' + ('' if ok else f'  (attendu dans la page : {attendu!r})'))


# Le tri par sélection du TD, avec des compteurs
def tri_selection(tab):
    n = len(tab); comparaisons = permutations = effectifs = 0; etapes = []
    for i in range(n - 1):
        i_min = i
        for j in range(i + 1, n):
            comparaisons += 1
            if tab[j] < tab[i_min]:
                i_min = j
        permutations += 1; effectifs += i_min != i
        etapes.append((i, i_min, tab[i_min]))
        tab[i], tab[i_min] = tab[i_min], tab[i]
        etapes[-1] += (list(tab),)
    return comparaisons, permutations, effectifs, etapes


def tri_insertion(tab):
    etapes = []
    for i in range(1, len(tab)):
        cle = tab[i]; j = i - 1; decalages = 0
        while j >= 0 and tab[j] > cle:
            tab[j + 1] = tab[j]; j = j - 1; decalages += 1
        tab[j + 1] = cle
        etapes.append((i, cle, decalages, list(tab)))
    return etapes


def fusion(gauche, droite):
    resultat = []
    i, j = 0, 0
    while i < len(gauche) or j < len(droite):
        if j == len(droite) or (i < len(gauche) and gauche[i] <= droite[j]):
            resultat.append(gauche[i]); i = i + 1
        else:
            resultat.append(droite[j]); j = j + 1
    return resultat


def tri_fusion(tab):
    if len(tab) <= 1: return tab
    milieu = len(tab) // 2
    return fusion(tri_fusion(tab[:milieu]), tri_fusion(tab[milieu:]))


print('Feuille 1 : sélection')
_, _, _, e = tri_selection([15, 4, 8, 2])
egal('q1 étapes (i, i_min, tab[i_min], tableau)', e, [(0, 3, 2, [2, 4, 8, 15]), (1, 1, 4, [2, 4, 8, 15]), (2, 2, 8, [2, 4, 8, 15])])
_, _, _, e = tri_selection([3, 5, 2, 6, 4, 1, 8])
egal('figure (3 premières étapes)', [x[3] for x in e[:3]], [[1, 5, 2, 6, 4, 3, 8], [1, 2, 5, 6, 4, 3, 8], [1, 2, 3, 6, 4, 5, 8]])
n = 6
comp = {tri_selection(list(p))[0] for p in itertools.permutations(range(n))}
egal(f'q4-q5 comparaisons pour les {math.factorial(n)} ordres de {n} valeurs', comp, {n * (n - 1) // 2})
egal('q4-q5 permutations (ligne exécutée)', {tri_selection(list(p))[1] for p in itertools.permutations(range(n))}, {n - 1})
eff = {tri_selection(list(p))[2] for p in itertools.permutations(range(n))}
egal('q5 échanges effectifs : de 0 à n − 1', (min(eff), max(eff)), (0, n - 1))
egal('q5 trié / à l\'envers : mêmes comparaisons', (tri_selection(list(range(n)))[0], tri_selection(list(range(n))[::-1])[0]), (15, 15))

print('Feuille 1 : insertion')
e = tri_insertion([12, 11, 13, 5])
egal('déroulé [12, 11, 13, 5], i = 1', e[0], (1, 11, 1, [11, 12, 13, 5]))
egal('q7 décalages pour i = 2', e[1][2], 0)
egal('q8 i = 3 : 3 décalages, 5 en tête', e[2], (3, 5, 3, [5, 11, 12, 13]))
egal('q9 déroulé de [5, 2, 8, 1]', [x[3] for x in tri_insertion([5, 2, 8, 1])], [[2, 5, 8, 1], [2, 5, 8, 1], [1, 2, 5, 8]])
egal('figure [4, 7, 3, 9, 2]', [(x[2], x[3]) for x in tri_insertion([4, 7, 3, 9, 2])],
     [(0, [4, 7, 3, 9, 2]), (2, [3, 4, 7, 9, 2]), (0, [3, 4, 7, 9, 2]), (4, [2, 3, 4, 7, 9])])
egal('q10-q12 tableau trié : aucun décalage', sum(x[2] for x in tri_insertion(list(range(100)))), 0)
egal('q14 à l\'envers : n(n − 1)/2 décalages', sum(x[2] for x in tri_insertion(list(range(100))[::-1])), 100 * 99 // 2)

print('Feuille 2 : fusion')
egal('print(tri_fusion([7, 5, 3, 0, 1, 6, 4, 2]))', tri_fusion([7, 5, 3, 0, 1, 6, 4, 2]), [0, 1, 2, 3, 4, 5, 6, 7])
t = [7, 5, 3, 0, 1, 6, 4, 2]
egal('figure, fusions deux à deux', [fusion(t[k:k + 1], t[k + 1:k + 2]) for k in range(0, 8, 2)], [[5, 7], [0, 3], [1, 6], [2, 4]])
egal('figure, fusions suivantes', [fusion([5, 7], [0, 3]), fusion([1, 6], [2, 4])], [[0, 3, 5, 7], [1, 2, 4, 6]])
t = [4, 1, 7, 3]; m = len(t) // 2
egal('q2 arbre', (t[:m], t[m:], [t[0:1], t[1:2], t[2:3], t[3:4]]), ([4, 1], [7, 3], [[4], [1], [7], [3]]))
egal('q3 premier élément de fusion([1, 4], [3, 7])', fusion([1, 4], [3, 7])[0], 1)
egal('q4 fusion([2, 8], [1, 5])', fusion([2, 8], [1, 5]), [1, 2, 5, 8])
egal('q7 n log2 n pour 100 000 (en millions, arrondi)', round(100_000 * math.log2(100_000) / 1e6, 1), 1.7)
egal('q7 n(n − 1)/2 pour 100 000 (en milliards, arrondi)', round(100_000 * 99_999 / 2 / 1e9), 5)

print('Feuille 2 : crash test, avec le programme des élèves')
spec = importlib.util.spec_from_file_location('crash', os.path.join(ICI, '..', 'td-tp-tri', 'crash-test.py'))
crash = importlib.util.module_from_spec(spec); spec.loader.exec_module(crash)
random.seed(2026)
t = [random.randint(0, 1_000_000) for _ in range(10_000)]
egal('q9 sélection, n = 10 000 : comparaisons', crash.mesurer(crash.tri_selection, t)[1], '49 995 000')
t = [random.randint(0, 1_000_000) for _ in range(100_000)]
ops = int(crash.mesurer(crash.tri_fusion, t)[1].replace(' ', ''))
egal('q11 fusion, n = 100 000 : environ 1,5 million', round(ops / 1e6, 1), 1.5)
t = [random.randint(0, 1_000_000) for _ in range(1_000)]
r = [crash.mesurer(f, t)[1] for f in (crash.tri_selection, crash.tri_insertion, crash.tri_fusion)]
egal('programme : les trois tris trient (n = 1 000)', len(r), 3)
egal('q13 un million : n log2 n ≈ 2 × 10^7 et n(n − 1)/2 ≈ 5 × 10^11', (round(1e6 * math.log2(1e6) / 1e7), round(1e6 * (1e6 - 1) / 2 / 1e11)), (2, 5))
egal('q14 sélection sur 50 000 lignes : 1,25 milliard', round(50_000 * 49_999 / 2 / 1e9, 2), 1.25)
egal('q15 n × 10 en O(n²) : × 100', (10 * 1000) ** 2 // 1000 ** 2, 100)

print('tout est juste' if not erreurs else f'{erreurs} erreur(s)')
sys.exit(1 if erreurs else 0)
