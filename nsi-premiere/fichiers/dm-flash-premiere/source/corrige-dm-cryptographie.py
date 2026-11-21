"""Corrigé du DM « La science du secret et la machine Enigma », calculé par Python (T125)."""
def crypter_cesar(message, cle):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    message_code = ""
    for lettre in message:
        indice = alphabet.find(lettre)
        nouvel_indice = (indice + cle) % 26
        message_code = message_code + alphabet[nouvel_indice]
    return message_code

def decrypter_cesar(message_code, cle):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    message = ""
    for lettre in message_code:
        indice = alphabet.find(lettre)
        nouvel_indice = (indice - cle) % 26
        message = message + alphabet[nouvel_indice]
    return message

def crypter_vigenere(message, liste_cle):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    message_code = ""
    i = 0
    for lettre in message:
        decalage = liste_cle[i]
        indice = alphabet.find(lettre)
        nouvel_indice = (indice + decalage) % 26
        message_code = message_code + alphabet[nouvel_indice]
        i = i + 1
        if i == len(liste_cle):
            i = 0
    return message_code

print("noix, 4 :", crypter_cesar("noix", 4))
for m, c in [("bonjour", 2), ("zigzag", 9), ("abracadabra", 3)]:
    print(m, c, "->", crypter_cesar(m, c))
print("decrypter rsmb, 4 :", decrypter_cesar("rsmb", 4))
code = "oh vhfuhw hvw hq wrl"
lettres = [c for c in code if c != " "]
print("lettre la plus fréquente :", max(set(lettres), key=lettres.count), "; décalage h -> e :", ord("h") - ord("e"), "; o -> l :", ord("o") - ord("l"))
print("message :", " ".join(decrypter_cesar(mot, 3) for mot in code.split()))
print("papa [1, 2] :", crypter_vigenere("papa", [1, 2]), "; papa [1, 2, 3] :", crypter_vigenere("papa", [1, 2, 3]))
print("BAC :", [ord(c) - ord("A") for c in "BAC"])
print("RXTTBO / WETTER, lettres codées par elles-mêmes :", [i + 1 for i, (a, b) in enumerate(zip("RXTTBO", "WETTER")) if a == b])
secondes = 158_000_000_000_000_000_000 / 1_000_000
print(f"Enigma : {secondes:.3g} s = {secondes / (365.25 * 24 * 3600):.3g} ans")

# Tableau des fréquences de l'énoncé : ce que se partagent les autres lettres.
# L'original disait « les autres lettres : moins de 1 % » : c'est faux (erreur corrigée en T125b).
frequences = {"E": 14.7, "A": 7.6, "I": 7.5, "S": 7.1, "N": 7.1, "R": 6.7, "T": 7.2, "O": 5.8, "L": 5.4, "U": 6.3}
total = sum(frequences.values())
autres = 26 - len(frequences)
print(f"10 lettres du tableau : {total:.1f} % ; les {autres} autres : {100 - total:.1f} %, soit {(100 - total) / autres:.2f} % en moyenne")
