"""Corrigé des « Activités logiques », vérifié par Python (T125) : python3 -I corrige-activites-logique.py

Tables de vérité des formules proposées, énigme de Wason, et simulation du robot sur sa grille."""
from itertools import product

def imp(a, b):
    return (not a) or b

def table(noms, formules):
    print("  " + " ".join(noms) + " | " + " | ".join(formules))
    for v in product([False, True], repeat=len(noms)):
        env = dict(zip(noms, v))
        print("  " + " ".join("VF"[not x] for x in v) + " | " + " | ".join("VF"[not formules[f](**env)] for f in formules))

def equivalentes(noms, f, g):
    return all(f(**dict(zip(noms, v))) == g(**dict(zip(noms, v))) for v in product([False, True], repeat=len(noms)))

# Exercice 1 : « s'il neige et que le vent souffle, il fera froid ; il peut faire froid sans neige ni vent ».
ex1 = {
    "(N ∧ V) → F": lambda N, V, F: imp(N and V, F),
    "F → (N ∧ V)": lambda N, V, F: imp(F, N and V),
    "(N ∨ V) → F": lambda N, V, F: imp(N or V, F),
    "(N ∧ V) ⇔ F": lambda N, V, F: (N and V) == F,
}
print("Exercice 1"); table("NVF", ex1)
for nom, f in ex1.items():   # il faut : N et V et non F interdit ; F sans N ni V permis ; rien de plus
    ok = (not f(True, True, False)) and f(False, False, True) and sum(f(*v) for v in product([False, True], repeat=3)) == 7
    print("  ", nom, "juste" if ok else "fausse")

# Exercice 2 : R seulement si P (R → P) ; si P, alors D (P → D).
ex2 = {
    "(R → P) ∧ (P → D)": lambda R, P, D: imp(R, P) and imp(P, D),
    "(P → R) ∧ (P → D)": lambda R, P, D: imp(P, R) and imp(P, D),
    "(R ⇔ P) ∧ (P → D)": lambda R, P, D: (R == P) and imp(P, D),
    "(R → P) ∧ (D → P)": lambda R, P, D: imp(R, P) and imp(D, P),
}
print("Exercice 2"); table("RPD", ex2)
ref2 = lambda R, P, D: imp(R, P) and imp(P, D)
for nom, f in ex2.items():
    print("  ", nom, "juste" if equivalentes("RPD", f, ref2) else "fausse")

# Exercice 3 : (P ou V) → A ; (non P et non V et T) → non A.
ex3 = {
    "((P ∨ V) → A) ∧ ((¬P ∧ ¬V ∧ T) → ¬A)": lambda A, P, V, T: imp(P or V, A) and imp((not P) and (not V) and T, not A),
    "((P ∧ V) → A) ∧ ((¬P ∧ ¬V ∧ T) → ¬A)": lambda A, P, V, T: imp(P and V, A) and imp((not P) and (not V) and T, not A),
    "((P ∨ V) → ¬A) ∧ ((¬P ∧ ¬V ∧ T) → A)": lambda A, P, V, T: imp(P or V, not A) and imp((not P) and (not V) and T, A),
    "((P ∨ V) → A) ∧ ((¬P ∨ ¬V ∨ T) → ¬A)": lambda A, P, V, T: imp(P or V, A) and imp((not P) or (not V) or T, not A),
}
ref3 = lambda A, P, V, T: imp(P or V, A) and imp((not (P or V)) and T, not A)
print("Exercice 3")
for nom, f in ex3.items():
    print("  ", nom, "juste" if equivalentes("APVT", f, ref3) else "fausse")

# Wason : règle « s'il y a un A sur une face, il y a un 4 sur l'autre ».
print("Wason")
lettres, nombres = "AK", [4, 7]
for carte in ["A", "K", 4, 7]:
    caches = nombres if isinstance(carte, str) else list(lettres)
    peut_tromper = any(not imp(l == "A", n == 4) for l, n in
                       ((carte, c) if isinstance(carte, str) else (c, carte) for c in caches))
    print("  carte", carte, ": à retourner" if peut_tromper else ": inutile")

# Robot : grille 5 x 5, départ en haut à gauche, regard vers la droite, obstacle au centre, arrivée en bas à droite.
def executer(lignes):
    def bloc(i, fin):
        prog = []
        while i < fin:
            mot = lignes[i].split()
            if mot[0] == "RÉPÉTER":
                prof, j = 1, i + 1
                while prof:
                    prof += lignes[j].startswith("RÉPÉTER") - (lignes[j] == "FIN_RÉPÉTER")
                    j += 1
                prog.append(("R", int(mot[1]), bloc(i + 1, j - 1)))
                i = j
            else:
                prog.append((mot[0],)); i += 1
        return prog
    etat = {"l": 0, "c": 0, "d": (0, 1), "ok": True}
    def lancer(prog):
        for ins in prog:
            if ins[0] == "R":
                for _ in range(ins[1]): lancer(ins[2])
            elif ins[0] == "AVANCER":
                l, c = etat["l"] + etat["d"][0], etat["c"] + etat["d"][1]
                if not (0 <= l < 5 and 0 <= c < 5) or (l, c) == (2, 2): etat["ok"] = False
                etat["l"], etat["c"] = l, c
            elif ins[0] == "TOURNER_DROITE":
                dl, dc = etat["d"]; etat["d"] = (dc, -dl)
    lancer(bloc(0, len(lignes)))
    return etat["ok"] and (etat["l"], etat["c"]) == (4, 4)

robots = {
    "imbriqué (6 lignes)": ["RÉPÉTER 2", "RÉPÉTER 4", "AVANCER", "FIN_RÉPÉTER", "TOURNER_DROITE", "FIN_RÉPÉTER"],
    "deux boucles (7 lignes)": ["RÉPÉTER 4", "AVANCER", "FIN_RÉPÉTER", "TOURNER_DROITE", "RÉPÉTER 4", "AVANCER", "FIN_RÉPÉTER"],
    "RÉPÉTER 3 (6 lignes)": ["RÉPÉTER 2", "RÉPÉTER 3", "AVANCER", "FIN_RÉPÉTER", "TOURNER_DROITE", "FIN_RÉPÉTER"],
    "RÉPÉTER 8 (3 lignes)": ["RÉPÉTER 8", "AVANCER", "FIN_RÉPÉTER"],
}
print("Robot")
for nom, p in robots.items():
    print("  ", nom, "arrive" if executer(p) else "n'arrive pas")
