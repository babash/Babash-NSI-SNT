# Vérification du sujet et du corrigé (CC Term NSI, POO, pile, file, novembre 2026 ; version « mode bac » du 25/11/2026).
# Exécution : python3.13 -I verifier.py, depuis ce dossier. Chaque assert doit passer.
# Les numéros de question sont ceux de controle.tex ; la version donnée en classe le 25/11/2026 a son propre script
# dans version-donnee-2026-11-25/.
# Babash - NSI Tani Malandi, CC BY-SA 4.0.
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile

assert sys.version_info[:2] == (3, 13), "lancer avec Python 3.13 : le message d'erreur du sujet en dépend"
ICI = os.path.dirname(os.path.abspath(__file__))
SUJET = open(os.path.join(ICI, "controle.tex"), encoding="utf-8").read()
CORRIGE = open(os.path.join(ICI, "corrige.tex"), encoding="utf-8").read()
BLOCS = re.findall(r"\\begin\{lstlisting\}(?:\[[^\]]*\])?\n(.*?)\\end\{lstlisting\}", SUJET, re.S)


def bloc(debut):
    return next(b for b in BLOCS if b.startswith(debut))


def message(instr, env):
    try:
        exec(instr, env)
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    return None


def sortie_de(code, env=None):
    s = io.StringIO()
    with contextlib.redirect_stdout(s):
        exec(code, env if env is not None else {})
    return s.getvalue().splitlines()


print("=== Barème : sujet et corrigé ===")
# Points de chaque question notée du sujet (classe exam : \question[..] et \part[..]).
def pts(arg):
    return float(arg.replace("\\half", ".5").replace(" ", "") or 0) if arg else None


marques = re.findall(r"\\(question|part)(?:\[([^\]]*)\])?", SUJET.split("\\begin{questions}", 1)[1])
total, q, par_question = 0.0, 0, {}
for genre, arg in marques:
    if genre == "question":
        q += 1
    v = pts(arg)
    if v:
        total += v
        par_question[q] = par_question.get(q, 0) + v
print("total du sujet :", total, "; par question :", par_question)
assert total == 20
# Partage voulu (Tle-2) : 10 points de type TD (dont 4 de cours), 10 points de bac.
assert sum(v for k, v in par_question.items() if k <= 4) == 4
assert sum(v for k, v in par_question.items() if k <= 10) == 10
assert sum(v for k, v in par_question.items() if k >= 11) == 10
# Le corrigé annonce les mêmes points, question par question.
def lire_points(t):
    t = t.replace(",", ".")
    m = re.match(r"(\d+) × ([\d.]+)", t)
    if m:
        return int(m.group(1)) * float(m.group(2))
    if "(" in t:
        t = t[:t.index("(")]
    return sum(float(x) for x in re.findall(r"[\d.]+", t))


def arguments(texte, debut):
    """Les deux arguments {…}{…} d'une commande, accolades imbriquées comprises."""
    res, i = [], debut
    for _ in range(2):
        assert texte[i] == "{"
        n, j = 0, i
        while True:
            n += {"{": 1, "}": -1}.get(texte[j], 0)
            if n == 0:
                break
            j += 1
        res.append(texte[i + 1:j])
        i = j + 1
    return res


annonces = {}
for m in re.finditer(r"\\Qt(?=\{)", CORRIGE):
    titre, valeur = arguments(CORRIGE, m.end())
    q = int(re.match(r"Question (\d+)", titre).group(1))
    annonces[q] = annonces.get(q, 0) + lire_points(valeur)
print("corrigé :", annonces)
assert annonces == par_question, (annonces, par_question)

print("=== Exercice 2 : la classe Barge ===")


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


code_barge = bloc("class Barge:")
env = {}
exec(code_barge, env)
assert env["Barge"].__init__.__code__.co_code == Barge.__init__.__code__.co_code  # même classe que le sujet
# Question 5 ; cours 2, 3 a), 3 c), 3 d)
b0 = Barge("x", 1)
assert sorted(vars(b0)) == ["capacite", "nom", "passagers"]


class Temoin(Barge):
    vu = []

    def __init__(self, nom, capacite):
        Temoin.vu.append(nom)
        super().__init__(nom, capacite)

    def moi(self):
        return self


t1, t2 = Temoin("t1", 1), Temoin("t2", 1)
assert Temoin.vu == ["t1", "t2"] and t1.moi() is t1 and t1 is not t2  # 3 a) V ; 3 c) F (deux objets) ; 2 : self
b3 = Barge("x", 10)
b3.embarquer(4)
assert b3.passagers == 4  # 3 d) V : une méthode modifie un attribut
# Question 6
b1 = Barge("Corail", 400)
b1.embarquer(120)
assert (b1.nom, b1.capacite, b1.passagers) == ("Corail", 400, 120)
b2 = Barge("Corail", 400)
Barge.embarquer(b2, 120)
assert b2.passagers == 120
m = message('Barge(self, "Corail", 400)', {"Barge": Barge})
assert m.startswith("NameError")
m = message("embarquer(b1, 120)", {"b1": b2})
print("Q6 b) erreur sans point :", m)
assert m == "NameError: name 'embarquer' is not defined"
# Question 7 : le programme du sujet, exécuté tel quel
s7 = sortie_de(code_barge + bloc('b = Barge("Lagon", 300)'))
print("Q7 :", s7)
assert s7 == ["50", "230"]
b = Barge("Lagon", 300)
b.embarquer(250)
assert b.embarquer(80) is False and b.passagers == 250
b.passagers = 250 + 80  # erreur fréquente : ajouter 80 malgré le refus
assert b.places_libres() == -30

print("=== Exercice 3 : pile et file (interface du sujet) ===")


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


INTERFACE = dict(creer_pile_vide=creer_pile_vide, creer_file_vide=creer_file_vide, est_vide=est_vide, empiler=empiler,
                 depiler=depiler, sommet=sommet, enfiler=enfiler, defiler=defiler, tete=tete, taille=taille)
# Question 8 : le programme du sujet
prog8 = bloc("p = creer_pile_vide()")
lignes8 = prog8.rstrip("\n").split("\n")
env = dict(INTERFACE)
exec("\n".join(lignes8[:5]), env)
assert env["p"][1][::-1] == [9, 1, 7, 4]  # 8 a) du sommet vers le fond
assert sortie_de(prog8, dict(INTERFACE)) == ["13 7 4 4"]  # 8 b)
p = creer_pile_vide()
empiler(p, 1)
sommet(p)
assert taille(p) == 1  # erreur fréquente de 8 b) : sommet ne retire pas

# Question 9 : les trous du sujet (« ... ») remplis avec le corrigé, aux lignes annoncées
code9 = bloc("def inverser(f):")
lignes9 = code9.rstrip("\n").split("\n")
trous9 = [i + 1 for i, l in enumerate(lignes9) if "..." in l]
assert trous9 == [4, 6, 7, 8], trous9
remplis = {4: "        empiler(p, defiler(f))", 6: "    while not est_vide(p):", 7: "        enfiler(g, depiler(p))", 8: "    return g"}
code9 = "\n".join(remplis.get(i + 1, l) for i, l in enumerate(lignes9))
env = dict(INTERFACE)
exec(code9, env)
f = creer_file_vide()
for nom in ["Anli", "Inès", "Mathis", "Zaïnaba"]:
    enfiler(f, nom)
g = env["inverser"](f)
assert g[1] == ["Zaïnaba", "Mathis", "Inès", "Anli"] and f[1] == []  # 9 b) : f est vide
# erreurs citées : tete ne vide jamais la file ; return p renvoie une pile
f = creer_file_vide()
enfiler(f, "Anli")
p = creer_pile_vide()
tours = 0
while not est_vide(f) and tours < 100:
    empiler(p, tete(f))
    tours += 1
assert tours == 100 and p[0] == "pile"

print("=== Exercice 4 : dictionnaire (trouver l'erreur) ===")
programme = bloc('prix = {"mangues"')
console = bloc("Traceback")
with tempfile.TemporaryDirectory() as d:
    chemin = os.path.join(d, "programme.py")
    open(chemin, "w", encoding="utf-8").write(programme)
    r = subprocess.run([sys.executable, "-I", chemin], capture_output=True, text=True, cwd=d)
    reel = r.stderr.replace(chemin, "programme.py")
assert reel.strip() == console.strip(), reel
assert "for produit in panier" not in console  # le message ne donne pas la correction
print("Q10 : message du sujet identique à celui de Python 3.13")
for ligne5 in ["    for produit in panier:", "    for produit in panier.keys():"]:
    corrige = programme.replace("    for produit in prix:", ligne5)
    out = subprocess.run([sys.executable, "-I", "-c", corrige], capture_output=True, text=True)
    assert out.stdout.strip() == "7.0", out

print("=== Exercice 5 (bac) : Asie 2024 jour 2, exercice 2 ===")


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
q11 = '[2*(i+1)-3) for i in range(3, 10)]'
assert not est_bien_parenthesee(q11) and compte_ouvrante(q11) == 3 and compte_fermante(q11) == 4  # Q11
assert compte_ouvrante(ex_bon) == 3  # exemple de l'en-tête de Q12
for contre in [")(", "(]", "([)]"]:  # Q14 : réponse et autres exemples
    assert bon_compte(contre) and not est_bien_parenthesee(contre), contre
assert bon_compte(ex_mauvais) is False  # erreur citée en Q14
# Les exemples des en-têtes ne donnent aucune réponse de Q14 (contre-exemple) : leurs comptes sont inégaux,
# ou la chaîne est bien parenthésée.
entetes = re.findall(r"\\begin\{lstlisting\}\[style=entete\]\n(.*?)\\end\{lstlisting\}", SUJET, re.S)
assert len(entetes) == 2
for e in entetes:
    for chaine in re.findall(r"\('([^']*)'\)", e):
        assert not (bon_compte(chaine) and not est_bien_parenthesee(chaine)), chaine
assert est_bien_parenthesee(ex_bon) and not est_bien_parenthesee(ex_mauvais)  # exemples de l'en-tête de Q16
assert [est_bien_parenthesee(t) for t in [ex_bon, ex_mauvais, q11, "((", ")"]] == [True, False, False, False, False]
assert est_bien_parenthesee("") and est_bien_parenthesee("{[()]}()")
# Question 15 : les trous de la classe Pile (lignes 9 et 14)
code15 = bloc("class Pile:")
l15 = code15.rstrip("\n").split("\n")
assert [i + 1 for i, l in enumerate(l15) if "..." in l] == [9, 14]
code15 = "\n".join({9: "        self.contenu.append(elt)", 14: "        return self.contenu.pop()"}.get(i + 1, l) for i, l in enumerate(l15))
env = {}
exec(code15, env)
pp = env["Pile"]()
pp.empiler("(")
pp.empiler("[")
assert pp.depiler() == "[" and pp.depiler() == "(" and pp.depiler() == "La pile est vide."


# variantes acceptées et erreurs citées
def compte_ouvrante_faux(txt):
    n = 0
    for c in txt:
        if c == "(" or "[" or "{":
            n = n + 1
    return n


assert compte_ouvrante_faux(ex_bon) == len(ex_bon)


def bon_compte_if(txt):
    if compte_ouvrante(txt) == compte_fermante(txt):
        return True
    else:
        return False


assert all(bon_compte_if(t) == bon_compte(t) for t in [ex_bon, ex_mauvais, q11, ")("])


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


tests = [ex_bon, ex_mauvais, q11, "((", ")", "", "{[()]}()", ")(", "(]", "([)]"]
assert all(est_bien_parenthesee_or(t) == est_bien_parenthesee(t) for t in tests)


def erreur_compare_c(txt):
    p = Pile()
    for c in txt:
        if c in "([{":
            p.empiler(c)
        elif c in ")]}":
            if p.depiler() != c:
                return False
    return p.est_vide()


def erreur_sans_test_final(txt):
    p = Pile()
    for c in txt:
        if c in "([{":
            p.empiler(c)
        elif c in ")]}":
            if p.depiler() != COUPLES[c]:
                return False
    return True


assert erreur_compare_c(ex_bon) is False and erreur_sans_test_final("((") is True
# Question 3 b) (V) : une même pile, deux implémentations (fonctions de l'exercice 3, classe Pile de l'exercice 5),
# même comportement par la même interface.
p1, p2 = creer_pile_vide(), Pile()
for x in [4, 7, 1]:
    empiler(p1, x)
    p2.empiler(x)
assert [depiler(p1) for _ in range(3)] == [p2.depiler() for _ in range(3)] == [1, 7, 4]
# Question 4 : l'exemple de la consigne n'est pas une des situations a) à d)
assert "« e : pile »" in SUJET
print("Tout est vérifié.")
