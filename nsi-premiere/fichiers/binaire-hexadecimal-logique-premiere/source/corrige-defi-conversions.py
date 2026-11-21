"""Corrigé du « Défi de conversions » calculé par Python (T125) : python3 -I corrige-defi-conversions.py"""
def detail_binaire(b):
    termes = [f"{2 ** (len(b) - 1 - i)}" for i, c in enumerate(b) if c == "1"]
    return " + ".join(termes) + f" = {int(b, 2)}"

binaires = ["10101010", "11100101", "11010000", "11010011"]
decimaux = [120, 255, 16]
hexas = ["A5", "3F", "C0"]
for b in binaires:
    n = int(b, 2)
    print(f"{b} (base 2) = {detail_binaire(b)} (base 10) = {n:X} (base 16) ; quartets {b[:4]} {b[4:]}")
for d in decimaux:
    print(f"{d} (base 10) = {d:08b} (base 2) = {d:X} (base 16) ; {d} = 16 x {d // 16} + {d % 16}")
for h in hexas:
    n = int(h, 16)
    print(f"{h} (base 16) = {int(h[0], 16)} x 16 + {int(h[1], 16)} = {n} (base 10) = {n:08b} (base 2)")
