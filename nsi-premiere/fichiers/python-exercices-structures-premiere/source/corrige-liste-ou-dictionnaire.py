"""Corrigé du TD « Liste ou dictionnaire ? » : chaque réponse attendue est exécutée (Python 3.13).
Lancer : python3 -I corrige-liste-ou-dictionnaire.py"""
arrivage = ["Zelda", "Mario", "Minecraft"]
arrivage.append("Tetris")                 # question 5
arrivage[1] = "Splatoon"                 # question 6
print("q5-q6 :", arrivage)
print("q7 :", len(arrivage))
prix_jeux = {"Zelda": 60, "Minecraft": 25, "Tetris": 10}
print("q8 :", prix_jeux["Zelda"], prix_jeux.get("Zelda"))
prix_jeux["Tetris"] = 8                   # question 9
prix_jeux["Splatoon"] = 45               # question 10
print("q9-q10 :", prix_jeux)
for essai in ("arrivage[3] = 'Tetris'", "prix_jeux[0]", "prix_jeux.append('Splatoon', 45)"):
    a = ["Zelda", "Mario", "Minecraft"]; p = {"Zelda": 60}
    try:
        exec(essai, {"arrivage": a, "prix_jeux": p})
    except Exception as e:
        print("retour", essai, "->", type(e).__name__, e)
stock = {"Manette": 50, "Casque": 80, "Cable": 15, "Housse": 20}
print("q11 :", [a for a in stock if stock[a] < 30])
print("q12 :", sum(stock.values()))
magasin = {"Portal": [15, 4], "Doom": [20, 0], "Roblox": [0, 100]}
print("q13 :", magasin["Portal"][1])
print("q14 :", [j for j in magasin if magasin[j][1] == 0])
