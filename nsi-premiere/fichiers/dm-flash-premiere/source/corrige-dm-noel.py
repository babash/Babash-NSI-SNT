"""Corrigé du DM de Noël, calculé par Python (T125) : python3 -I corrige-dm-noel.py"""
a = 5; b = 2; c = a / b; a = a + 1; c = c * a
print("Q1 : c =", c, type(c).__name__)
x = 5; y = 2; x = (x + 1) * y; y = x % 5
print("Q2 : y =", y, type(y).__name__)
A, B = 10, 5
print("Q3 :", (A < B) or ((A + B) > 12) and (B >= 5))
for age in (17,):
    if age < 13: resultat = "Enfant"
    elif age >= 18: resultat = "Adulte"
    else: resultat = "Adolescent"
print("Q4 :", resultat)
temp, pluie = 25, True
if temp > 20:
    message = "Journée fraîche et pluvieuse" if pluie else "Journée ensoleillée"
else:
    message = "Journée froide"
print("Q5 :", message)
conds = {"1": lambda x: x > 10 and x < 20, "2": lambda x: x >= 10 or x <= 20,
         "3": lambda x: x < 10 or x > 20, "4": lambda x: not (x >= 10 and x <= 20)}
for k, f in conds.items():
    print("Q6 option", k, "juste" if all(f(x) == (x < 10 or x > 20) for x in range(-5, 40)) else "fausse")
somme = 0
for i in range(1, 5):
    somme = somme + i
print("Q7 : somme =", somme)
compteur = 0; a = 1
while a <= 5:
    a = a + 2; compteur = compteur + 1
print("Q8 :", compteur, "tours")
print("Q10 :", sum(1 for k in range(1, 11) if k % 3 == 0), "fois OK")
print("A :", int("10110", 2), int("111111", 2), bin(45), bin(100))
print("B :", hex(0b10101101), hex(0b001101011110), bin(0x9C), bin(0x1F8))
print("C :", 0x2B, 0xFF, hex(78), hex(300))
