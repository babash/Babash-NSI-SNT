"""Corrigé du DM flash « Boucle while : la pyramide », calculé par Python (T125)."""
print("billes par étage :", [i ** 2 for i in range(1, 8)])
cumul, total = [], 0
for i in range(1, 9):
    total += i ** 2
    cumul.append(total)
print("total cumulé :", cumul, "-> 7 étages pour 200 billes, car", cumul[6], "<= 200 <", cumul[7])

# le programme de l'énoncé, avec le suivi des variables (tableau d'avancement)
nb_billes = 200
reste = nb_billes
etage = 0
print(etage, reste)
while reste - (etage + 1) ** 2 >= 0:
    etage += 1
    reste = reste - etage ** 2
    print(etage, reste)
print(f"Pour {nb_billes} billes la pyramide fait {etage} étages.")

# question 5 : les deux saisies de la page (data-entrees 7, puis 3)
for nb_etages in (7, 3):
    billes = 0
    etage = 1
    while etage <= nb_etages:
        billes = billes + etage ** 2
        etage = etage + 1
    print(nb_etages, "étages :", billes)
