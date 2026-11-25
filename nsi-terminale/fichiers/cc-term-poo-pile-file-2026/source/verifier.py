# Vérification des réponses du corrigé (CC Term NSI, POO, pile, file, novembre 2026, version révisée du 25/11/2026).
# Exécution : python3.13 verifier.py, depuis ce dossier. Chaque assert doit passer.
# Les numéros de question sont ceux du sujet révisé (controle.tex) ; la version donnée le 25/11/2026
# a son propre script dans version-donnee-2026-11-25/.
# Babash - NSI Tani Malandi, CC BY-SA 4.0.

print("=== Exercices 1 et 2 : la classe Barge ===")


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


# Question 5 : attributs ; questions de cours 2 et 3 a), b) : self est l'objet, __init__ appelé à la création
b0 = Barge("x", 1)
assert sorted(vars(b0)) == ["capacite", "nom", "passagers"]
assert [m for m in vars(Barge) if not m.startswith("__") or m == "__init__"] == ["__init__", "places_libres", "embarquer"]
# Q2 : self est l'objet sur lequel la méthode est appelée ; Q3 a) : __init__ est appelé à la création
class Temoin(Barge):
    vu = []
    def __init__(self, nom, capacite):
        Temoin.vu.append(nom)
        super().__init__(nom, capacite)
    def moi(self):
        return self
t = Temoin("t", 1)
assert Temoin.vu == ["t"] and t.moi() is t
# Q3 b) : faux, un attribut n'est pas une fonction (vars de l'objet : des données)
assert not any(callable(v) for v in vars(t).values())

# Question 6 a), b)
b1 = Barge("Corail", 400)
b1.embarquer(120)
assert (b1.nom, b1.capacite, b1.passagers) == ("Corail", 400, 120)

# Question 7 : programme de l'énoncé ; a) ligne 4, b) ligne 6
import io, contextlib
sortie = io.StringIO()
with contextlib.redirect_stdout(sortie):
    b = Barge("Lagon", 300)
    print(b.embarquer(250))
    print(b.embarquer(80))
    print(b.places_libres())
    b.passagers = b.passagers - 100
    print(b.embarquer(80), b.passagers)
print(sortie.getvalue(), end="")
assert sortie.getvalue().splitlines() == ["True", "False", "50", "True 230"]

print("=== Exercice 3 : la classe Playlist ===")


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


# Question 9 (avec les trous complétés) : le programme de l'énoncé de la version donnée, valeur 647
pl = Playlist("trajet")
assert pl.duree_totale() == 0
pl.ajouter("mgodro", 245)
pl.ajouter("rap", 190)
pl.ajouter("zouk", 212)
print(pl.morceaux)
print(pl.duree_totale())
assert pl.duree_totale() == 647
print(pl.duree_totale() // 60, "min", pl.duree_totale() % 60, "s")

print("=== Exercice 4 : pile et file (interface du cours) ===")


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


# Question 10 : programme de l'énoncé
p = creer_pile_vide()
f = creer_file_vide()
for x in [4, 7, 1, 9]:
    empiler(p, x)
    enfiler(f, x)
assert p[1][::-1] == [9, 1, 7, 4]  # a) du sommet vers le fond
assert f[1] == [4, 7, 1, 9]        # b) de la tête vers la queue
a = depiler(p)
c = defiler(f)
empiler(p, a + c)
enfiler(f, sommet(p))
print(sommet(p), tete(f), taille(p), taille(f))
print("pile (bas -> sommet) :", p[1], "; file (tete -> queue) :", f[1])
assert (sommet(p), tete(f), taille(p), taille(f)) == (13, 7, 4, 4)


# Question 11
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

print("=== Exercice 5 : dictionnaire ===")
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

# Question 13 : le programme fautif du sujet, exécuté pour de vrai ; le message affiché dans le sujet
# doit être exactement celui de Python 3.13 (seul le dossier est retiré du chemin du fichier).
import os, re, subprocess, sys, tempfile
ici = os.path.dirname(os.path.abspath(__file__))
sujet = open(os.path.join(ici, "controle.tex"), encoding="utf-8").read()
blocs = re.findall(r"\\begin\{lstlisting\}(?:\[[^\]]*\])?\n(.*?)\\end\{lstlisting\}", sujet, re.S)
programme = next(b for b in blocs if "def cout(panier, prix):" in b and "for produit in prix:" in b)
console = next(b for b in blocs if b.startswith("Traceback"))
with tempfile.TemporaryDirectory() as d:
    chemin = os.path.join(d, "programme.py")
    open(chemin, "w", encoding="utf-8").write(programme)
    r = subprocess.run([sys.executable, "-I", chemin], capture_output=True, text=True, cwd=d)
    reel = r.stderr.replace(chemin, "programme.py")
assert sys.version_info[:2] == (3, 13), "lancer avec Python 3.13"
assert reel.strip() == console.strip(), reel
print("Q13 : message d'erreur du sujet identique à celui de Python 3.13")
corrige = programme.replace("    for produit in prix:", "    for produit in panier:")
sortie = subprocess.run([sys.executable, "-I", "-c", corrige], capture_output=True, text=True)
assert sortie.stdout.strip() == "7.0", sortie
corrige_keys = programme.replace("    for produit in prix:", "    for produit in panier.keys():")
assert subprocess.run([sys.executable, "-I", "-c", corrige_keys], capture_output=True, text=True).stdout.strip() == "7.0"

print("=== Exercice 6 (bac) : Asie 2024 jour 2, exercice 2 ===")


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
print("Q14 :", q1, "->", est_bien_parenthesee(q1), "; bon_compte :", bon_compte(q1))
assert est_bien_parenthesee(ex_bon) and not est_bien_parenthesee(ex_mauvais)
assert not est_bien_parenthesee(q1)
assert compte_ouvrante(q1) == 3 and compte_fermante(q1) == 4
print("Q15-Q16 :", compte_ouvrante(ex_bon), compte_fermante(ex_bon), bon_compte(ex_bon))
for contre in [")(", ")[", "(]", "([)]"]:
    assert bon_compte(contre) and not est_bien_parenthesee(contre)
print("Q17 : contre-exemples vérifiés : ')(' '(]' '([)]'")
# Cas où la pile est vide quand on rencontre une fermante : depiler renvoie
# le message, différent de toute ouvrante, donc False (pas d'erreur).
assert est_bien_parenthesee(")") is False
assert est_bien_parenthesee("") is True
assert est_bien_parenthesee("{[()]}()") is True
assert est_bien_parenthesee("((") is False

# Q18
p6 = Pile()
p6.empiler(1)
p6.empiler(2)
assert p6.depiler() == 2 and p6.depiler() == 1 and p6.depiler() == "La pile est vide."

print("=== Variantes acceptées et erreurs fréquentes citées dans le corrigé ===")


def message(instr, env):
    try:
        exec(instr, env)
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    return None


# Ex. 2, Q6 b) : variante acceptée et erreurs
b2 = Barge("Corail", 400)
Barge.embarquer(b2, 120)
assert b2.passagers == 120
m = message('Barge(self, "Corail", 400)', {"Barge": Barge})
print("Q6a erreur self :", m)
assert m.startswith("NameError")  # self n'existe pas hors de la classe
m = message("embarquer(b1, 120)", {"b1": b2})
print("Q6b erreur sans point :", m)
assert m == "NameError: name 'embarquer' is not defined"
# Q7 erreur : la ligne 3 ne modifie rien
b3 = Barge("Lagon", 300)
b3.embarquer(250)
assert b3.embarquer(80) is False and b3.passagers == 250

# Ex. 3, Q8 : variante acceptée et erreur
class Playlist2(Playlist):
    def ajouter(self, titre, duree):
        self.morceaux = self.morceaux + [(titre, duree)]


q = Playlist2("x")
q.ajouter("rap", 190)
assert q.morceaux == [("rap", 190)]
m = message("[].append('rap', 190)", {})
print("Q8 erreur :", m)
assert m == "TypeError: list.append() takes exactly one argument (2 given)"
# Q9 : variante m[1], erreur return dans la boucle, erreur total + m
tot = 0
for mo in pl.morceaux:
    tot = tot + mo[1]
assert tot == 647


def duree_return_dans_boucle(morceaux):
    total = 0
    for titre, duree in morceaux:
        total = total + duree
        return total


assert duree_return_dans_boucle(pl.morceaux) == 245  # s'arrête au 1er morceau
m = message("t = 0\nfor m in M:\n    t = t + m", {"M": pl.morceaux})
print("Q9 erreur :", m)
assert m == "TypeError: unsupported operand type(s) for +: 'int' and 'tuple'"

# Ex. 4, Q10 c) erreur : sommet ne retire rien
p = creer_pile_vide()
for x in [4, 7, 1, 9]:
    empiler(p, x)
sommet(p)
assert taille(p) == 4
# Q11 a) erreur : tete dans la boucle ne vide jamais la file (on arrête au bout de 100 tours)
f = creer_file_vide()
enfiler(f, "Anli")
p = creer_pile_vide()
tours = 0
while not est_vide(f) and tours < 100:
    empiler(p, tete(f))
    tours = tours + 1
assert tours == 100 and taille(f) == 1  # boucle infinie sans la limite
# Q11 a) erreur : return p renvoie une pile, pas une file
assert p[0] == "pile"

# Ex. 5, Q12 : bananes et manioc non affichés ; Q13 : variante items() et erreur KeyError
assert [k for k in prix if prix[k] >= 2.5] == ["mangues", "tomates"]


def cout_items(panier, prix):
    total = 0
    for produit, masse in panier.items():
        total = total + masse * prix[produit]
    return total


assert cout_items({"mangues": 2, "tomates": 0.5}, prix) == 7.0
m = message("t = 0\nfor k in prix:\n    t = t + panier[k] * prix[k]",
            {"prix": prix, "panier": {"mangues": 2, "tomates": 0.5}})
print("Q13 : variante items() et erreur KeyError :", m)
assert m == "KeyError: 'bananes'"

# Ex. 6 (questions 14 à 19) : chaque exemple et contre-exemple du corrigé
assert compte_ouvrante(ex_bon) == 3  # Q15
assert not bon_compte(q1)  # Q14 : 3 ouvrantes, 4 fermantes
for contre in [")(", "(]", "([)]"]:  # Q17 : réponse et autres exemples
    assert bon_compte(contre), contre
    assert not est_bien_parenthesee(contre), contre
# Q17 erreur : l'expression fautive de l'énoncé n'est pas un contre-exemple
assert compte_ouvrante(ex_mauvais) == 3 and compte_fermante(ex_mauvais) == 2
assert bon_compte(ex_mauvais) is False
print("Q17 : 'tab[2*(i + 4] - tab[3)' ->", compte_ouvrante(ex_mauvais), "ouvrantes,",
      compte_fermante(ex_mauvais), "fermantes, bon_compte", bon_compte(ex_mauvais))


# Q15 erreur : c == "(" or "[" or "{" est toujours vrai
def compte_ouvrante_faux(txt):
    n = 0
    for c in txt:
        if c == "(" or "[" or "{":
            n = n + 1
    return n


assert compte_ouvrante_faux(ex_bon) == len(ex_bon) == 23


# Q15 variante acceptée
def compte_ouvrante_or(txt):
    n = 0
    for c in txt:
        if c == "(" or c == "[" or c == "{":
            n = n + 1
    return n


assert all(compte_ouvrante_or(t) == compte_ouvrante(t) for t in [ex_bon, ex_mauvais, q1])


# Q16 variante if / else
def bon_compte_if(txt):
    if compte_ouvrante(txt) == compte_fermante(txt):
        return True
    else:
        return False


assert all(bon_compte_if(t) == bon_compte(t) for t in [ex_bon, ex_mauvais, q1, ")("])


# Q18 variante acceptée : sommet au début (insert(0) et pop(0))
class PileDebut(Pile):
    def empiler(self, elt):
        self.contenu.insert(0, elt)

    def depiler(self):
        if self.est_vide():
            return "La pile est vide."
        return self.contenu.pop(0)


pd = PileDebut()
pd.empiler(1)
pd.empiler(2)
assert pd.depiler() == 2 and pd.depiler() == 1


# Q18 erreurs : append + pop(0) donne une file ; contenu[-1] ne retire pas
class PileFausse(Pile):
    def depiler(self):
        if self.est_vide():
            return "La pile est vide."
        return self.contenu.pop(0)


pf = PileFausse()
pf.empiler(1)
pf.empiler(2)
assert pf.depiler() == 1  # premier entré : comportement de file
pl2 = Pile()
pl2.empiler(1)
assert pl2.contenu[-1] == 1 and len(pl2.contenu) == 1


# Q19 variante sans dictionnaire
def est_bien_parenthesee_or(txt):
    p = Pile()
    for c in txt:
        if c in "([{":
            p.empiler(c)
        elif c in ")]}":
            o = p.depiler()
            if not ((o == "(" and c == ")") or (o == "[" and c == "]") or (o == "{" and c == "}")):
                return False
    return p.est_vide()


tests = [ex_bon, ex_mauvais, q1, "((", ")", "", "{[()]}()", ")(", "(]", "([)]"]
assert all(est_bien_parenthesee_or(t) == est_bien_parenthesee(t) for t in tests)
# Tableau de la question 19
assert [est_bien_parenthesee(t) for t in [ex_bon, ex_mauvais, q1, "((", ")"]] == [True, False, False, False, False]


# Q19 erreurs fréquentes
def erreur_compare_c(txt):
    p = Pile()
    for c in txt:
        if c in "([{":
            p.empiler(c)
        elif c in ")]}":
            if p.depiler() != c:
                return False
    return p.est_vide()


assert erreur_compare_c(ex_bon) is False  # une expression juste est refusée


def erreur_sans_test_final(txt):
    p = Pile()
    for c in txt:
        if c in "([{":
            p.empiler(c)
        elif c in ")]}":
            if p.depiler() != COUPLES[c]:
                return False
    return True


assert erreur_sans_test_final("((") is True  # déclarée à tort bien parenthésée
print("Variantes et erreurs fréquentes : toutes exécutées.")

print("=== Codes à trous du sujet : trous remplis avec le corrigé, numéros de ligne contrôlés, code exécuté ===")
TROU = re.compile(r"\(\*@\\trou\{[^}]*\}@\*\)")


def remplir(nom_bloc, reponses, lignes_attendues):
    bloc = next(b for b in blocs if nom_bloc in b)
    lignes = bloc.rstrip("\n").split("\n")
    trous = [i + 1 for i, l in enumerate(lignes) for _ in TROU.findall(l)]
    assert trous == lignes_attendues, (nom_bloc, trous)
    it = iter(reponses)
    return "\n".join(TROU.sub(lambda m: next(it), l) for l in lignes) + "\n"


# Questions 8 et 9 : ligne 7, lignes 10 à 13
code = remplir("class Playlist:", ["self.morceaux.append((titre, duree))", "0", "self.morceaux", "total + duree", "total"], [7, 10, 11, 12, 13])
code_playlist = code
env = {}
exec(code, env)
pl3 = env["Playlist"]("trajet")
assert pl3.duree_totale() == 0
for t, d in [("mgodro", 245), ("rap", 190), ("zouk", 212)]:
    pl3.ajouter(t, d)
assert pl3.morceaux[0] == ("mgodro", 245) and pl3.duree_totale() == 647
# Question 11 a) : les quatre trous
code = remplir("def inverser(f):", ["defiler(f)", "not est_vide(p)", "depiler(p)", "g"], [4, 6, 7, 8])
env = dict(globals())
exec(code, env)
f = creer_file_vide()
for nom in ["Anli", "Inès", "Mathis", "Zaïnaba"]:
    enfiler(f, nom)
assert env["inverser"](f)[1] == ["Zaïnaba", "Mathis", "Inès", "Anli"] and f[1] == []
# Question 18 : lignes 9 et 14 de la classe Pile
code = remplir("class Pile:", ["self.contenu.append(elt)", "self.contenu.pop()"], [9, 14])
env = {}
exec(code, env)
p18 = env["Pile"]()
p18.empiler("(")
p18.empiler("[")
assert p18.depiler() == "[" and p18.depiler() == "(" and p18.depiler() == "La pile est vide."
# Question 9 : erreurs citées dans le corrigé
faux = code_playlist.replace("in self.morceaux:", "in morceaux:")
env = {}
exec(faux, env)
q9 = env["Playlist"]("x")
q9.ajouter("rap", 190)
m = message("q9.duree_totale()", {"q9": q9})
print("Q9 erreur sans self :", m)
assert m == "NameError: name 'morceaux' is not defined"
faux = code_playlist.replace("total = total + duree", "total = duree")
env = {}
exec(faux, env)
q9 = env["Playlist"]("x")
for t, d in [("mgodro", 245), ("rap", 190), ("zouk", 212)]:
    q9.ajouter(t, d)
assert q9.duree_totale() == 212  # la dernière durée, pas la somme
print("Trous des questions 8, 9, 11 a) et 18 : numéros de ligne justes, code complété exécuté.")
print("Tout est vérifié.")
