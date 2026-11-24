# Vérification des réponses du corrigé (CC Term NSI, POO, pile, file, novembre 2026).
# Exécution : python3 verifier.py (Python 3.13). Chaque assert doit passer.
# Babash - NSI Tani Malandi, CC BY-SA 4.0.

print("=== Exercice A : la classe Barge ===")


class Barge:
    def __init__(self, nom, capacite):
        self.nom = nom
        self.capacite = capacite
        self.passagers = 0

    def places_libres(self):
        return self.capacite - self.passagers

    def embarquer(self, n):
        if n <= self.places_libres():
            self.passagers = self.passagers + n
            return True
        return False


# Question 2
b1 = Barge("Corail", 400)
b1.embarquer(120)
b1.capacite = 350
assert (b1.passagers, b1.capacite, b1.places_libres()) == (120, 350, 230)

# Question 3 : programme de l'énoncé
b = Barge("Lagon", 300)
print(b.embarquer(250))
print(b.embarquer(80))
print(b.places_libres())
b.passagers = b.passagers - 100
print(b.embarquer(80), b.passagers)

print("=== Exercice B : la classe Playlist ===")


class Playlist:
    def __init__(self, nom):
        self.nom = nom
        self.morceaux = []

    def ajouter(self, titre, duree):
        self.morceaux.append((titre, duree))

    def duree_totale(self):
        total = 0
        for titre, duree in self.morceaux:
            total = total + duree
        return total


pl = Playlist("trajet")
assert pl.duree_totale() == 0
pl.ajouter("mgodro", 245)
pl.ajouter("rap", 190)
pl.ajouter("zouk", 212)
print(pl.morceaux)
print(pl.duree_totale())
assert pl.duree_totale() == 647
print(pl.duree_totale() // 60, "min", pl.duree_totale() % 60, "s")

print("=== Exercice C : pile et file (interface du cours) ===")


# Implémentation de test de l'interface (listes Python).
def creer_pile_vide():
    return ("pile", [])


def creer_file_vide():
    return ("file", [])


def est_vide(s):
    return len(s[1]) == 0


def empiler(p, e):
    p[1].append(e)


def depiler(p):
    return p[1].pop()


def sommet(p):
    return p[1][-1]


def enfiler(f, e):
    f[1].append(e)


def defiler(f):
    return f[1].pop(0)


def tete(f):
    return f[1][0]


def taille(s):
    return len(s[1])


# Question 7 : programme de l'énoncé
p = creer_pile_vide()
f = creer_file_vide()
for x in [4, 7, 1, 9]:
    empiler(p, x)
    enfiler(f, x)
a = depiler(p)
c = defiler(f)
empiler(p, a + c)
enfiler(f, sommet(p))
print(sommet(p), tete(f), taille(p), taille(f))
print("pile (bas -> sommet) :", p[1], "; file (tete -> queue) :", f[1])
assert (sommet(p), tete(f), taille(p), taille(f)) == (13, 7, 4, 4)


# Question 8
def inverser(f):
    p = creer_pile_vide()
    while not est_vide(f):
        empiler(p, defiler(f))
    g = creer_file_vide()
    while not est_vide(p):
        enfiler(g, depiler(p))
    return g


f = creer_file_vide()
for nom in ["Anli", "Inès", "Mathis", "Zaïnaba"]:
    enfiler(f, nom)
g = inverser(f)
print("file inversée :", g[1], "; f après l'appel :", f[1])
assert g[1] == ["Zaïnaba", "Mathis", "Inès", "Anli"] and f[1] == []

print("=== Exercice D : dictionnaire ===")
prix = {"mangues": 2.5, "bananes": 2, "manioc": 1.5, "tomates": 4}
for produit in prix:
    if prix[produit] >= 2.5:
        print(produit, prix[produit])


def cout(panier, prix):
    total = 0
    for produit in panier:
        total = total + panier[produit] * prix[produit]
    return total


print(cout({"mangues": 2, "tomates": 0.5}, prix))
assert cout({"mangues": 2, "tomates": 0.5}, prix) == 7.0
assert cout({}, prix) == 0

print("=== Exercice de bac : Asie 2024 jour 2, exercice 2 ===")


def compte_ouvrante(txt):
    n = 0
    for c in txt:
        if c in "([{":
            n = n + 1
    return n


def compte_fermante(txt):
    n = 0
    for c in txt:
        if c in ")]}":
            n = n + 1
    return n


def bon_compte(txt):
    return compte_ouvrante(txt) == compte_fermante(txt)


class Pile:
    def __init__(self):
        self.contenu = []

    def est_vide(self):
        return len(self.contenu) == 0

    def empiler(self, elt):
        self.contenu.append(elt)

    def depiler(self):
        if self.est_vide():
            return "La pile est vide."
        return self.contenu.pop()


COUPLES = {")": "(", "]": "[", "}": "{"}


def est_bien_parenthesee(txt):
    p = Pile()
    for c in txt:
        if c in "([{":
            p.empiler(c)
        elif c in ")]}":
            if p.depiler() != COUPLES[c]:
                return False
    return p.est_vide()


ex_bon = 'tab[2*(i + 4)] - tab[3]'
ex_mauvais = 'tab[2*(i + 4] - tab[3)'
q1 = '[2*(i+1)-3) for i in range(3, 10)]'
print("Q1 :", q1, "->", est_bien_parenthesee(q1), "; bon_compte :", bon_compte(q1))
assert est_bien_parenthesee(ex_bon) and not est_bien_parenthesee(ex_mauvais)
assert not est_bien_parenthesee(q1)
assert compte_ouvrante(q1) == 3 and compte_fermante(q1) == 4
print("Q2-Q4 :", compte_ouvrante(ex_bon), compte_fermante(ex_bon), bon_compte(ex_bon))
for contre in [")(", ")[", "(]", "([)]"]:
    assert bon_compte(contre) and not est_bien_parenthesee(contre)
print("Q5 : contre-exemples vérifiés : ')(' '(]' '([)]'")
# Cas où la pile est vide quand on rencontre une fermante : depiler renvoie
# le message, différent de toute ouvrante, donc False (pas d'erreur).
assert est_bien_parenthesee(")") is False
assert est_bien_parenthesee("") is True
assert est_bien_parenthesee("{[()]}()") is True
assert est_bien_parenthesee("((") is False

# Q6
p6 = Pile()
p6.empiler(1)
p6.empiler(2)
assert p6.depiler() == 2 and p6.depiler() == 1 and p6.depiler() == "La pile est vide."

# Q7 : décompte des comparaisons, convention du corrigé AEIF :
# 1 comparaison par caractère qui n'est pas une parenthèse (« est-ce une parenthèse ? »),
# 1 par ouvrante, 3 par fermante (fermante ? / pile vide dans depiler / couple ?),
# 1 finale (pile vide ?).
n = len(ex_bon)
nb_ouv = compte_ouvrante(ex_bon)
nb_ferm = compte_fermante(ex_bon)
autres = n - nb_ouv - nb_ferm
total = autres + nb_ouv + 3 * nb_ferm + 1
print("Q7 : longueur", n, "; autres", autres, "; ouvrantes", nb_ouv, "; fermantes", nb_ferm, "; total", total)
assert (n, autres, nb_ouv, nb_ferm, total) == (23, 17, 3, 3, 30)
# Pire cas : n/2 ouvrantes puis n/2 fermantes (n pair) : n/2 + 3n/2 + 1 = 2n + 1
for m in range(1, 8):
    s = "(" * m + ")" * m
    assert est_bien_parenthesee(s)
    assert m + 3 * m + 1 == 2 * len(s) + 1
print("Q7 : pire cas 2n + 1 vérifié pour n = 2 à 14")

# Variante : décompte avec les tests « in » vus comme une seule comparaison
# chacun, en suivant le code de est_bien_parenthesee ci-dessus :
# autre caractère : 2 tests (ouvrante ? fermante ?) ; ouvrante : 1 ;
# fermante : 2 + 1 (est_vide) + 1 (égalité) = 4 ; plus 1 final.
var = 2 * autres + nb_ouv + 4 * nb_ferm + 1
print("Q7 variante (2 tests par caractère ordinaire, 4 par fermante) :", var)
assert var == 50
# pire cas de cette variante : n/2 ouvrantes puis n/2 fermantes : n/2 + 4n/2 + 1 = 5n/2 + 1
print("Tout est vérifié.")
