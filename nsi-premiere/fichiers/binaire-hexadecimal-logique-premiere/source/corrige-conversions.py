"""Corrigé du TD « Conversions : 2, 10, 16 » (exercices-conversions).
Chaque réponse est calculée ici par Python 3.13, puis écrite dans la page.
  python3 -I corrige-conversions.py              affiche le corrigé et vérifie chaque calcul
  python3 -I corrige-conversions.py --html F     écrit aussi les questions (HTML) dans le fichier F
"""
import sys

# (partie, nombre écrit, base de départ, base d'arrivée) : les 24 conversions du TD, dans l'ordre
CONVERSIONS = [
    (1, "15", 10, 16), (1, "15", 10, 2), (1, "10000", 2, 10), (1, "10000", 2, 16), (1, "1F", 16, 10),
    (2, "FF", 16, 10), (2, "A38", 16, 10), (2, "B38", 16, 10),
    (3, "1111", 2, 10), (3, "10000", 2, 10), (3, "10010", 2, 10), (3, "1111 1111", 2, 10),
    (4, "80", 10, 2), (4, "255", 10, 2), (4, "256", 10, 2),
    (5, "129", 10, 16), (5, "256", 10, 16), (5, "257", 10, 16), (5, "1920", 10, 16),
    (6, "1001", 2, 16), (6, "1011", 2, 16), (6, "1001 1011", 2, 16), (6, "1111", 2, 16), (6, "1111 1111", 2, 16),
]
NOMS = {2: "binaire", 10: "décimal", 16: "hexadécimal"}
CHIFFRES = "0123456789ABCDEF"


def ecrire(n, base):
    """n écrit en base 2, 10 ou 16, par divisions successives (sans bin ni hex)."""
    if n == 0:
        return "0"
    s = ""
    while n > 0:
        s = CHIFFRES[n % base] + s
        n //= base
    return s


def lire(texte, base):
    """La valeur d'un nombre écrit en base 2, 10 ou 16, par la somme des poids."""
    v = 0
    for c in texte.replace(" ", ""):
        v = v * base + CHIFFRES.index(c.upper())
    return v


def groupes(s, k=4):
    """« 10011011 » -> « 1001 1011 » (paquets de k chiffres en partant de la droite)."""
    s = s.zfill(-(-len(s) // k) * k)
    return " ".join(s[i:i + k] for i in range(0, len(s), k))


def alternatives(resultat, base):
    """Les écritures acceptées pour une réponse juste."""
    alt = [resultat]
    if base == 2:
        for largeur in (4, 8, 12, 16):
            if len(resultat) <= largeur:
                p = resultat.zfill(largeur)
                alt += [p, groupes(p)]
        alt += [groupes(resultat), "0b" + resultat]
    if base == 16:
        alt += ["0x" + resultat, resultat.zfill(2), resultat.zfill(4)]
    vu = []
    for a in alt:
        if a not in vu:
            vu.append(a)
    return vu


def explication(texte, depart, arrivee, valeur, resultat):
    """La méthode, avec les vrais calculs."""
    brut = texte.replace(" ", "")
    if depart == 10:
        etapes, n = [], valeur
        while n > 0:
            etapes.append(f"{n} = {n // arrivee} × {arrivee} + {n % arrivee}" + (f" ({CHIFFRES[n % arrivee]})" if arrivee == 16 and n % arrivee > 9 else ""))
            n //= arrivee
        return ("Divisions successives par " + str(arrivee) + " : " + " ; ".join(etapes) +
                f". On lit les restes du dernier au premier : <b>{resultat}</b>.")
    if arrivee == 10:
        termes = []
        for i, c in enumerate(brut):
            p = len(brut) - 1 - i
            v = CHIFFRES.index(c.upper())
            if depart == 2 and v == 0:
                continue
            termes.append(f"{v} × {depart ** p}" if depart == 16 else f"{depart ** p}")
        if len(termes) == 1:
            return f"Un seul bit vaut 1, et son poids est {termes[0]} : <b>{resultat}</b>."
        return ("On additionne les poids" + (" des bits à 1" if depart == 2 else "") + " : " +
                " + ".join(termes) + f" = <b>{resultat}</b>.")
    # base 2 vers base 16 : paquets de 4 bits
    paquets = groupes(brut).split()
    return ("Paquets de 4 bits, en partant de la droite : " +
            " ; ".join(f"{p} → {CHIFFRES[lire(p, 2)]}" if lire(p, 2) < 10 else f"{p} = {lire(p, 2)} → {CHIFFRES[lire(p, 2)]}" for p in paquets) + f". Donc <b>{resultat}</b>.")


TITRES = {1: "1. Comprendre les bases 2, 10 et 16", 2: "2. De la base 16 à la base 10", 3: "3. De la base 2 à la base 10",
          4: "4. De la base 10 à la base 2", 5: "5. De la base 10 à la base 16", 6: "6. De la base 2 à la base 16"}
AIDES = {
    (10, 2): ["Divise par 2, encore et encore, jusqu'à obtenir 0. Note chaque reste (0 ou 1).",
              "Le binaire se lit en prenant les restes <b>du dernier au premier</b>."],
    (10, 16): ["Divise par 16, encore et encore, jusqu'à obtenir 0. Note chaque reste (de 0 à 15).",
               "Un reste de 10 à 15 s'écrit avec une lettre : A = 10, B = 11, C = 12, D = 13, E = 14, F = 15. Lis les restes du dernier au premier."],
    (2, 10): ["Les poids des bits, de droite à gauche : 1, 2, 4, 8, 16, 32, 64, 128…",
              "Additionne seulement les poids des bits qui valent 1."],
    (16, 10): ["Les poids des chiffres, de droite à gauche : 1, 16, 256…",
               "A = 10, B = 11, C = 12, D = 13, E = 14, F = 15. Multiplie chaque chiffre par son poids, puis additionne."],
    (2, 16): ["Fais des paquets de 4 bits, en partant de la droite.",
              "Chaque paquet de 4 bits donne un chiffre hexadécimal : 1010 = A, 1011 = B… 1111 = F."],
}


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def corrige():
    lignes = []
    for i, (partie, texte, depart, arrivee) in enumerate(CONVERSIONS, 1):
        valeur = lire(texte, depart)
        resultat = ecrire(valeur, arrivee)
        # contrôle par les fonctions de Python elles-mêmes
        assert valeur == int(texte.replace(" ", ""), depart)
        assert resultat == {2: format(valeur, "b"), 10: str(valeur), 16: format(valeur, "X")}[arrivee]
        lignes.append((i, partie, texte, depart, arrivee, valeur, resultat))
    return lignes


def html(lignes):
    morceaux, partie_vue = [], None
    for i, partie, texte, depart, arrivee, valeur, resultat in lignes:
        if partie != partie_vue:
            morceaux.append(f'  <h2 class="td-partie">{TITRES[partie]}</h2>\n')
            partie_vue = partie
        retours = []
        if depart == 10 and len(resultat) > 1 and resultat[::-1] != resultat:
            retours.append(f'    <p class="td-retour" data-si="{esc(resultat[::-1])}">Tu as lu les restes dans l\'ordre du calcul. Il faut les lire <b>du dernier au premier</b>.</p>\n')
        if arrivee == 16 and depart == 2 and len(texte.replace(" ", "")) > 4:
            retours.append(f'    <p class="td-retour" data-si="{lire(resultat, 16)}">C\'est l\'écriture en base 10. On demande la base 16 : un chiffre par paquet de 4 bits.</p>\n')
        aides = "".join(f'    <p class="td-aide">{a}</p>\n' for a in AIDES[(depart, arrivee)])
        morceaux.append(
            f'  <section class="td-q" data-type="courte" id="q{i}" data-reponse="{esc("|".join(alternatives(resultat, arrivee)))}" data-etiquette="En {NOMS[arrivee]} (base {arrivee}) :">\n'
            f'    <p class="td-consigne">Convertis en {NOMS[arrivee]} le nombre <code>{texte}</code>, écrit en base {depart}.</p>\n'
            + "".join(retours) + aides +
            f'    <div class="td-correction"><p>{explication(texte, depart, arrivee, valeur, resultat)}</p></div>\n'
            f'  </section>\n\n')
    return "".join(morceaux)


if __name__ == "__main__":
    lignes = corrige()
    for i, partie, texte, depart, arrivee, valeur, resultat in lignes:
        print(f"q{i:<2} partie {partie} : {texte:>10} (base {depart:>2}) = {resultat:>9} (base {arrivee:>2})   valeur {valeur}")
    print(f"{len(lignes)} conversions, chacune vérifiée par int() et format().")
    if "--html" in sys.argv:
        open(sys.argv[sys.argv.index("--html") + 1], "w", encoding="utf-8").write(html(lignes))
