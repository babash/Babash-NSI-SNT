#!/usr/bin/env python3
"""Caractères à surveiller dans les lignes ajoutées d'un diff (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/caracteres.py --diff origin/main...origin/<branche> [--depot DOSSIER]
  python3 -I .github/gardien/caracteres.py FICHIER.diff        (« - » : lire l'entrée standard)

Lit les lignes ajoutées (« + ») d'un diff unifié et relève, avec le fichier et la ligne :
  - à relire :
      - les caractères invisibles : espaces et gluons sans largeur, BOM, trait d'union
        conditionnel, séparateurs de ligne Unicode, lettres de remplissage invisibles ;
      - les contrôles bidirectionnels, qui peuvent maquiller l'ordre réel d'un code ;
      - les points de substitution (U+2022, U+2219, U+22C5, U+2027) placés entre deux lettres,
        là où le point médian U+00B7 était sans doute voulu ;
  - pour information :
      - les points médians (U+00B7), permis depuis la décision de l'enseignant du 07/11/2026
        (langage inclusif complet) : ce ne sont jamais des fautes ;
      - le nombre d'espaces insécables (typographie française).
Les caractères invisibles sont affichés sous la forme ⟨U+XXXX⟩, jamais tels quels.
Avec --diff, PLAGE est passée telle quelle à « git diff » : avec trois points, ce sont les lignes
ajoutées par la branche depuis son point de départ.
Code de sortie 1 si un caractère est « à relire ».
"""
import argparse
import os
import re
import subprocess
import sys
import unicodedata

ICI = os.path.dirname(os.path.abspath(__file__))


def chaine(*codes):
    """Les caractères de ces points de code, écrits en hexadécimal pour rester lisibles dans le source."""
    return "".join(chr(c) for c in codes)


POINT_MEDIAN = chr(0x00B7)
# Puce, opérateur puce, opérateur point, point de césure : à la place du point médian, entre deux lettres
SUBSTITUTS = chaine(0x2022, 0x2219, 0x22C5, 0x2027)
# Espaces et gluons sans largeur, BOM, trait d'union conditionnel, séparateur de voyelle mongol,
# séparateurs de ligne et de paragraphe Unicode, lettres de remplissage hangul
INVISIBLES = chaine(0x200B, 0x200C, 0x200D, 0x2060, 0x2061, 0x2062, 0x2063, 0x2064, 0xFEFF, 0x00AD,
                    0x180E, 0x2028, 0x2029, 0x115F, 0x1160, 0x3164, 0xFFA0)
# Marques et contrôles bidirectionnels (attaque « Trojan Source » : l'affichage ne suit plus le code)
BIDI = chaine(0x200E, 0x200F, 0x061C, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069)
# Espace insécable, espace fine insécable, espace tabulaire
INSECABLES = chaine(0x00A0, 0x202F, 0x2007)
LETTRE = r"[^\W\d_]"
SUBSTITUT_ENTRE_LETTRES = re.compile("(?<=%s)[%s](?=%s)" % (LETTRE, SUBSTITUTS, LETTRE))
BLOC = re.compile(r"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def lignes_ajoutees(diff):
    """(fichier, numéro de ligne dans le nouveau fichier, texte) de chaque ligne ajoutée.

    Les compteurs de chaque bloc « @@ » disent combien de lignes lui appartiennent : une ligne
    ajoutée qui commence par « ++ » n'est donc pas prise pour un en-tête de fichier."""
    fichier, ancien, nouveau, numero = "?", 0, 0, 0
    for l in diff.split("\n"):
        l = l[:-1] if l.endswith("\r") else l
        if ancien > 0 or nouveau > 0:
            if l.startswith("+"):
                yield fichier, numero, l[1:]
                numero += 1
                nouveau -= 1
            elif l.startswith("-"):
                ancien -= 1
            elif l.startswith("\\"):
                pass  # « \ No newline at end of file »
            else:
                numero += 1
                ancien -= 1
                nouveau -= 1
            continue
        m = BLOC.match(l)
        if m:
            ancien = int(m.group(1)) if m.group(1) is not None else 1
            numero = int(m.group(2))
            nouveau = int(m.group(3)) if m.group(3) is not None else 1
        elif l.startswith("+++ "):
            chemin = l[4:].strip().strip('"')
            fichier = chemin[2:] if chemin.startswith("b/") else chemin


def visible(texte):
    """Le texte, avec chaque caractère invisible ou bidirectionnel écrit ⟨U+XXXX⟩."""
    return "".join("⟨U+%04X⟩" % ord(c) if c in INVISIBLES or c in BIDI else c for c in texte)


def extrait(texte, pos):
    debut = max(0, pos - 50)
    fin = pos + 70
    return ("…" if debut else "") + visible(texte[debut:fin]).strip() + ("…" if fin < len(texte) else "")


def nom(c):
    return "U+%04X (%s)" % (ord(c), unicodedata.name(c, "?"))


def lire_diff(o):
    if o.diff:
        depot = o.depot or subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ICI,
                                          capture_output=True, text=True).stdout.strip()
        r = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "--no-color", "--no-ext-diff", o.diff],
                           cwd=depot, capture_output=True)
        if r.returncode:
            sys.exit("git diff %s : %s" % (o.diff, r.stderr.decode("utf-8", "replace").strip()))
        donnees = r.stdout
    elif o.fichier == "-":
        donnees = sys.stdin.buffer.read()
    else:
        with open(o.fichier, "rb") as f:
            donnees = f.read()
    return donnees.decode("utf-8", errors="replace")


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("fichier", nargs="?", help="un diff unifié (« - » : l'entrée standard)")
    a.add_argument("--diff", metavar="PLAGE", help="calculer le diff avec git (exemple : origin/main...origin/archi/t33)")
    a.add_argument("--depot", help="la copie du dépôt où lancer git (par défaut : celle de cet outil)")
    o = a.parse_args()
    if bool(o.fichier) == bool(o.diff):
        a.error("donner soit un fichier de diff, soit --diff PLAGE")
    a_relire, medians, lignes_medians, insecables, lues = 0, 0, 0, 0, 0
    for fichier, numero, texte in lignes_ajoutees(lire_diff(o)):
        lues += 1
        ou = "%s:%d" % (fichier, numero)
        vus = {}
        for i, c in enumerate(texte):
            if c in INVISIBLES or c in BIDI:
                vus.setdefault(c, []).append(i)
        for c, positions in vus.items():
            a_relire += len(positions)
            genre = "bidirectionnel" if c in BIDI else "invisible"
            print("À RELIRE  %s %s ×%d  %s : %s" % (genre, nom(c), len(positions), ou, extrait(texte, positions[0])))
        for m in SUBSTITUT_ENTRE_LETTRES.finditer(texte):
            a_relire += 1
            print("À RELIRE  point de substitution %s entre deux lettres (point médian voulu : U+00B7 ?)  %s : %s"
                  % (nom(m.group(0)), ou, extrait(texte, m.start())))
        n = texte.count(POINT_MEDIAN)
        if n:
            medians += n
            lignes_medians += 1
            print("INFO      point médian ×%d  %s : %s" % (n, ou, extrait(texte, texte.index(POINT_MEDIAN))))
        insecables += sum(texte.count(c) for c in INSECABLES)
    print("\nBilan : %d ligne(s) ajoutée(s) lue(s) ; %d caractère(s) à relire ; pour information : "
          "%d point(s) médian(s) sur %d ligne(s), %d espace(s) insécable(s)."
          % (lues, a_relire, medians, lignes_medians, insecables))
    sys.exit(1 if a_relire else 0)


if __name__ == "__main__":
    main()
