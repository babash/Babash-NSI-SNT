"""Corrigé de l'opération « Golden Sac » (feuilles 1 et 2) : chaque réponse est calculée (Python 3.13).
Lancer : python3 -I corrige-golden-sac.py"""
import traceback

musee = {"Statue d'or": [15, 200], "Tableau de maître": [5, 150], "Vase Ming": [2, 50],
         "Armure de samouraï": [25, 100], "Diadème": [1, 40]}

for essai in ('musee[0]', 'musee["Diadème"]', 'musee["Diadème"][1]', 'musee[1]["Diadème"]'):
    try:
        print("f1 q1-q2 :", essai, "->", eval(essai))
    except Exception as e:
        print("f1 q1-q2 :", essai, "->", traceback.format_exception_only(e)[-1].strip())
m = {k: list(v) for k, v in musee.items()}
m["Pièce rare"] = [1, 10]
m["Vase Ming"][1] = 60
print("f1 q3, q5 :", m["Pièce rare"], m["Vase Ming"])
print("f1 q6 :", sum(v[0] for v in musee.values()), "kg ; q8 :", musee["Tableau de maître"][0] + musee["Vase Ming"][0],
      "kg ; q9 :", sum(musee[k][1] for k in ("Tableau de maître", "Vase Ming", "Diadème")), "k€")
print("f1 q11 :", max((k for k in musee if musee[k][0] <= 10), key=lambda k: musee[k][1]))


def trace(cle, inverse):
    """Une ligne par objet examiné : (objet, prix ou None, poids utilisé, place restante)."""
    poids, lignes = 0, []
    for nom in sorted(musee, key=cle, reverse=inverse):
        p, v = musee[nom]
        if poids + p <= 10:
            poids += p
            lignes.append((nom, v, poids, 10 - poids))
        else:
            lignes.append((nom, None, poids, 10 - poids))
    return lignes


for nom, (cle, inverse) in {"A (le plus cher)": (lambda n: musee[n][1], True),
                            "B (le plus léger)": (lambda n: musee[n][0], False)}.items():
    t = trace(cle, inverse)
    print("f1 q12-q13 stratégie", nom)
    for ligne in t:
        print("   ", ligne)
    print("    butin :", sum(l[1] for l in t if l[1]), "k€  (q14)")


def choisir_meilleur(inventaire, deja_pris, place_restante):
    elu = None
    max_prix = -1
    for nom, infos in inventaire.items():
        poids_obj = infos[0]
        prix_obj = infos[1]
        if nom not in deja_pris and poids_obj <= place_restante:
            if prix_obj > max_prix:
                max_prix = prix_obj
                elu = nom
    return elu


print("f2 q1 : avec 0 au départ, un objet gratuit serait-il choisi ?", choisir_meilleur({"Caillou": [1, 0]}, [], 10),
      "; avec -1 au départ : oui (voir ci-dessus avec max_prix = -1)")
print("f2 q4 : rien ne rentre ->", choisir_meilleur(musee, [], 0))
