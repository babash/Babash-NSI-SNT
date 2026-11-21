"""Recalcule les réponses du TD type bac « graphes » (Python 3.13).

Chaque graphe est écrit dans l'ordre des voisins de l'énoncé (ou de la
convention annoncée dans le TD), puis chaque réponse attendue est recalculée
et comparée à la valeur écrite dans la page. Usage : python3 -I calculs.py
"""

# ---------- Exercice 1 : Amérique du Nord 2024, sujet 1, exercice 2 ----------
sommets = ['G', 'J', 'Y', 'E', 'N', 'M', 'A', 'L']
amities = {'G': ['J', 'Y', 'N', 'M'], 'J': ['G', 'Y', 'E', 'L'],
           'Y': ['G', 'J', 'E', 'N', 'M', 'A'], 'E': ['J', 'Y', 'N'],
           'N': ['G', 'Y', 'E'], 'M': ['G', 'Y', 'A'], 'A': ['Y', 'M'], 'L': ['J']}
# graphe non orienté : chaque amitié dans les deux sens
for s, vs in amities.items():
    for v in vs:
        assert s in amities[v], (s, v)
aretes = sum(len(v) for v in amities.values()) // 2
assert aretes == 13

matrice_adj = [[1 if v in amities[s] else 0 for v in sommets] for s in sommets]
assert matrice_adj[0] == [0, 1, 1, 0, 1, 1, 0, 0]          # ligne G donnée par le sujet
LIGNES = {  # lignes écrites dans la page (trous de la question 2)
    'J': [1, 0, 1, 1, 0, 0, 0, 1], 'Y': [1, 1, 0, 1, 1, 1, 1, 0], 'E': [0, 1, 1, 0, 1, 0, 0, 0],
    'N': [1, 0, 1, 1, 0, 0, 0, 0], 'M': [1, 0, 1, 0, 0, 0, 1, 0], 'A': [0, 0, 1, 0, 0, 1, 0, 0],
    'L': [0, 1, 0, 0, 0, 0, 0, 0]}
for s, l in LIGNES.items():
    assert matrice_adj[sommets.index(s)] == l, s
assert all(matrice_adj[i][j] == matrice_adj[j][i] for i in range(8) for j in range(8))


def position(l, s):
    for i in range(len(l)):
        if l[i] == s:
            return i
    return None


assert position(sommets, 'G') == 0 and position(sommets, 'Z') is None


def nb_amis_m(L, m, s):
    pos_s = position(L, s)
    if pos_s == None:
        return None
    amis = 0
    for i in range(len(m)):
        amis += m[pos_s][i]
    return amis


assert nb_amis_m(sommets, matrice_adj, 'G') == 4
assert nb_amis_m(sommets, matrice_adj, 'Z') is None

graphe = {s: [v for v in sommets if v in amities[s]] for s in sommets}   # ordre de la liste sommets
assert graphe['G'] == ['J', 'Y', 'N', 'M']                               # ligne donnée par le sujet
assert graphe == amities


def nb_amis(d, s):
    return len(d[s])


assert nb_amis(graphe, 'L') == 1
assert [nb_amis(graphe, s) for s in sommets] == [nb_amis_m(sommets, matrice_adj, s) for s in sommets]

# après les brouilles (dictionnaire donné par le sujet)
graphe2 = {'G': ['J', 'N'], 'J': ['G', 'Y', 'E', 'L'], 'Y': ['J', 'E', 'N'], 'E': ['J', 'Y', 'N'],
           'N': ['G', 'Y', 'E'], 'M': ['A'], 'A': ['M'], 'L': ['J']}
retirees = {frozenset(p) for p in [('M', 'G'), ('M', 'Y'), ('G', 'Y'), ('A', 'Y')]}
avant = {frozenset((s, v)) for s in amities for v in amities[s]}
apres = {frozenset((s, v)) for s in graphe2 for v in graphe2[s]}
assert avant - apres == retirees and apres <= avant


def parcours_en_profondeur(d, s, visites=[]):
    visites.append(s)
    for v in d[s]:
        if v not in visites:
            parcours_en_profondeur(d, v, visites)
    return visites


p = parcours_en_profondeur(graphe2, 'L', [])
assert p == ['L', 'J', 'G', 'N', 'Y', 'E'], p
cercle = sorted(set(p) - {'L'})
assert cercle == ['E', 'G', 'J', 'N', 'Y']        # Emma, Gabriel, Jade, Nina, Yanis
# le piège de la valeur par défaut mutable
premier = parcours_en_profondeur(graphe2, 'M')
second = parcours_en_profondeur(graphe2, 'L')
assert premier is second and second == ['M', 'A', 'L', 'J', 'G', 'N', 'Y', 'E'], second

# ---------- Exercice 2 : Polynésie 2024, sujet 2, exercice 1, partie B ----------
# dictionnaire de la figure 2 (identique dans les deux corrigés AEIF), voisins par ordre alphabétique
G = {'Ar': ['Ax', 'Mp', 'Mr', 'Ni'],
     'Av': ['Ax', 'Mr', 'Ni'],
     'Ax': ['Ar', 'Av', 'Di', 'Mr', 'Nc', 'To'],
     'Di': ['Ax', 'Nc'],
     'Mp': ['Ar', 'Ni'],
     'Mr': ['Ar', 'Av', 'Ax', 'Nc', 'To'],
     'Nc': ['Ax', 'Di', 'Mr', 'To'],
     'Ni': ['Ar', 'Av', 'Mp'],
     'To': ['Ax', 'Mr', 'Nc']}
corrige1 = {'Mr': ['Av', 'Ar', 'Ax', 'To', 'Nc'], 'Av': ['Mr', 'Ni', 'Ax'], 'Ni': ['Av', 'Ar', 'Mp'],
            'Ar': ['Mr', 'Ni', 'Mp', 'Ax'], 'Mp': ['Ar', 'Ni'], 'Ax': ['Av', 'Ar', 'Mr', 'To', 'Nc', 'Di'],
            'To': ['Mr', 'Nc', 'Ax'], 'Nc': ['Mr', 'To', 'Ax', 'Di'], 'Di': ['Nc', 'Ax']}
assert all(sorted(corrige1[s]) == G[s] for s in G) and set(corrige1) == set(G)
for s, vs in G.items():
    assert vs == sorted(vs)
    for v in vs:
        assert s in G[v]


def creerFile():
    return []


def estVide(F):
    return len(F) == 0


def enfiler(F, e):
    F.append(e)


def defiler(F):
    return F.pop(0)


def creerPile():
    return []


def empiler(P, e):
    P.append(e)


def depiler(P):
    return P.pop()


def parcours(graphe, sommet):            # code du sujet
    f = creerFile()
    enfiler(f, sommet)
    visite = [sommet]
    while not estVide(f):
        s = defiler(f)
        for v in graphe[s]:
            if not (v in visite):
                visite.append(v)
                enfiler(f, v)
    return visite


assert parcours(G, 'Av') == ['Av', 'Ax', 'Mr', 'Ni', 'Ar', 'Di', 'Nc', 'To', 'Mp']
# avec l'ordre des voisins du premier corrigé AEIF : sa réponse
assert parcours(corrige1, 'Av') == ['Av', 'Mr', 'Ni', 'Ax', 'Ar', 'To', 'Nc', 'Mp', 'Di']


def distance(graphe, sommet):
    f = creerFile()
    enfiler(f, sommet)
    dist = {sommet: 0}
    while not estVide(f):
        s = defiler(f)
        for v in graphe[s]:
            if not (v in dist):
                dist[v] = dist[s] + 1
                enfiler(f, v)
    return dist


d = distance(G, 'Av')
assert d == {'Av': 0, 'Ax': 1, 'Mr': 1, 'Ni': 1, 'Ar': 2, 'Di': 2, 'Nc': 2, 'To': 2, 'Mp': 2}
assert str(d) == "{'Av': 0, 'Ax': 1, 'Mr': 1, 'Ni': 1, 'Ar': 2, 'Di': 2, 'Nc': 2, 'To': 2, 'Mp': 2}"
assert distance(G, 'Mp')['Nc'] == 3                    # l'exemple de l'énoncé
assert distance(corrige1, 'Av') == d                    # les distances ne dépendent pas de l'ordre


def parcours2(G, s):
    p = creerPile()
    empiler(p, s)
    visite = []
    while not estVide(p):
        x = depiler(p)
        if not (x in visite):
            visite.append(x)
            for v in G[x]:
                empiler(p, v)
    return visite


r = parcours2(G, 'Av')
assert r == ['Av', 'Ni', 'Mp', 'Ar', 'Mr', 'To', 'Nc', 'Di', 'Ax'], r
Grev = {s: vs[::-1] for s, vs in G.items()}
r2 = parcours2(Grev, 'Av')
print('parcours2, voisins empilés à l\'envers :', r2)
print('parcours2 avec l\'ordre du corrigé 1 :', parcours2(corrige1, 'Av'))

# ---------- les réponses écrites dans la page sont celles calculées ici ----------
import html, os, re
page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html'), encoding='utf-8').read()


def reponse(q):
    m = re.search(r'id="%s"[^>]*data-reponse="([^"]*)"' % q, page) or re.search(r'data-reponse="([^"]*)"[^>]*id="%s"' % q, page)
    return html.unescape(m.group(1)).split('|')[0]


assert reponse('q1') == str(aretes)
assert reponse('q5') == str(nb_amis_m(sommets, matrice_adj, 'G'))
assert reponse('q14') == str(parcours(G, 'Av'))
assert reponse('q17') == str(distance(G, 'Av'))
assert reponse('q19') == str(parcours2(G, 'Av'))
for s, l in LIGNES.items():
    assert re.search(r'\[ \[\[%s\]\] \]+,? +# %s' % (re.escape(str(l)[1:-1]), s), page), s
for s in sommets[1:]:
    assert "'%s': [[ %s ]]" % (s, graphe[s]) in page, s
for s in G:
    assert "'%s': [[ %s ]]" % (s, G[s]) in page, s
print('tout est juste')
