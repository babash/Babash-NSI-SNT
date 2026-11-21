"""Corrigé de la mission « L'Odyssée du Livreur » (feuilles 1 et 2) : chaque réponse est calculée (Python 3.13).
Lancer : python3 -I corrige-odyssee-du-livreur.py
Correction de l'original : avec Mzouazia, le trajet glouton est déjà le plus court (0,1604, aucun cycle
plus court) ; la question « trouve un trajet plus court que le glouton » n'avait pas de réponse. La 4e ville
devient Choungui, et la feuille donne les six distances utiles."""
from itertools import permutations
from math import factorial

# feuille 1
vitesse = (80, 110, 130)
print("f1 :", vitesse[0], vitesse[-1], len(vitesse), type(vitesse), type((42)), type((42,)), len((1920, 1080)),
      20 in (10, 20, 30), (1, 2) + (3, 4), (5, 12)[1], sum((12, 15, 18)), (12, 15, 18)[1], len((1, (2, 3), 4)),
      (7, 4, 7, 2).count(7))
# q12 : « 20 in data == True » est une comparaison enchaînée (20 in data and data == True) : elle vaut False,
# la page ne l'accepte pas (retour qui explique le piège) ; « (20 in data) == True » vaut True et reste acceptée.
data = (10, 20, 30)
assert (20 in data == True) is False and ((20 in data) == True) is True and (20 in data) is True
print("f1 q12 :", 20 in data, "; 20 in data == True ->", 20 in data == True, "; (20 in data) == True ->", (20 in data) == True)

# feuille 2
villes = {
    "Mamoudzou": (-12.781, 45.231), "Dapani": (-12.973, 45.174),
    "Sada": (-12.848, 45.104), "Chiconi": (-12.833, 45.118),
    "Dembeni": (-12.843, 45.187), "Bandrele": (-12.908, 45.192),
    "Chirongui": (-12.932, 45.148), "Boueni": (-12.910, 45.076),
    "Kani-Keli": (-12.956, 45.105), "Tsimkoura": (-12.912, 45.131),
    "Choungui": (-12.957, 45.129), "Poroani": (-12.891, 45.135),
    "Mbouini": (-12.983, 45.133), "Mzouazia": (-12.908, 45.089)
}


def dist(v1, v2, donnees):
    dx = donnees[v2][0] - donnees[v1][0]
    dy = donnees[v2][1] - donnees[v1][1]
    return (dx**2 + dy**2)**0.5


def ville_proche(actuelle, liste_villes, coords):
    d_min = float("inf")
    prochaine = None
    for v in liste_villes:
        d = dist(actuelle, v, coords)
        if d < d_min:
            d_min = d
            prochaine = v
    return prochaine


def tournee_gloutonne(depart, liste_villes, coords):
    visitees = [depart]
    a_voir = list(liste_villes)
    while len(a_voir) > 0:
        prochaine = ville_proche(visitees[-1], a_voir, coords)
        visitees.append(prochaine)
        a_voir.remove(prochaine)
    visitees.append(depart)
    return visitees


def longueur(trajet):
    return sum(dist(trajet[i], trajet[i + 1], villes) for i in range(len(trajet) - 1))


print("f2 q2 :", villes["Sada"][1], "; q3 :", [v for v in villes][:3], "…")
print("f2 q5-q10 :", [factorial(n) for n in (3, 4, 5)], factorial(10), factorial(20), f"{factorial(50):.2e}")
s = 3e64 / 1e9
print(f"f2 q11 : {s:.1e} s = {s / (365.25 * 86400):.1e} ans")
quatre = ["Chirongui", "Tsimkoura", "Poroani", "Choungui"]
for i, a in enumerate(quatre):
    for b in quatre[i + 1:]:
        print(f"   d({a}, {b}) = {dist(a, b, villes):.4f} ≈ {dist(a, b, villes):.3f}")
arrondi = {}
for i, a in enumerate(quatre):
    for b in quatre[i + 1:]:
        arrondi[a, b] = arrondi[b, a] = round(dist(a, b, villes), 3)
for p in permutations(quatre[1:]):
    t = ["Chirongui", *p, "Chirongui"]
    print("   ", " -> ".join(t), round(sum(arrondi[t[i], t[i + 1]] for i in range(4)), 3), "(exact", round(longueur(t), 4), ")")
g = tournee_gloutonne("Chirongui", quatre[1:], villes)
print("f2 q13-q15 glouton :", g, round(sum(arrondi[g[i], g[i + 1]] for i in range(4)), 3))
print("f2 q17 :", ville_proche("Chirongui", quatre[1:], villes))
print("f2 q18 :", tournee_gloutonne("Mamoudzou", ["Sada", "Dembeni", "Dapani", "Boueni"], villes))
# l'ancienne instance (Mzouazia) : le glouton y était optimal
anc = ["Tsimkoura", "Poroani", "Mzouazia"]
print("ancienne instance : glouton", round(longueur(tournee_gloutonne("Chirongui", anc, villes)), 4),
      "; meilleur", round(min(longueur(["Chirongui", *p, "Chirongui"]) for p in permutations(anc)), 4))
