#!/usr/bin/env python3
"""Chemins cités dans un README : existent-ils dans le site ? (Gardien, contrôle 9)

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/chemins_readme.py DOSSIER_DU_SITE [FICHIER.md]

Lit FICHIER.md (par défaut DOSSIER_DU_SITE/README.md) hors des blocs de code, qui sont des
exemples, et relève chaque mot cité entre accents graves qui ressemble à un chemin : il contient
« / », ou finit par .md, .js, .json, .html, .py, .sh, .yml, .svg, .css, .sql ou .txt. Sont
ignorés : les adresses (http…, file://…, tout « schéma:// »), les gabarits (<id>, …), les
options (-x), les extensions seules (`.py`) et les valeurs entre guillemets (`"propriétaire/nom"`,
une valeur de réglage, pas un chemin). Ce qui suit « ? » ou « # » ne compte pas. Un passage entre
accents graves qui contient des espaces est d'abord essayé en entier, comme un seul chemin
(`Thème 1 – Structures de données/`) ; s'il n'existe pas, ses mots sont examinés un à un.
Un chemin est trouvé s'il existe :
  - depuis la racine du site, depuis le dossier du fichier lu, ou depuis le dossier d'une
    rubrique (reglages.js) ;
  - depuis un dossier cité dans le même fichier (config.js dans snt/fichiers/alien-python/, par
    exemple) ;
  - pour un nom de fichier seul, n'importe où dans le site ;
  - avec « * », si le motif désigne au moins un fichier.
Affiche chaque chemin, « ok » ou « ABSENT », avec la ligne de sa première citation. Un fichier
annoncé mais pas encore créé (donnees/vitrine.json, par exemple) est « ABSENT » : au Gardien de
juger. Code de sortie 1 si un chemin est absent.
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402

EXTENSION = re.compile(r"\.(md|js|json|html|py|sh|yml|svg|css|sql|txt)$")


def passages(lignes):
    """(numéro de ligne, texte) de chaque passage entre accents graves, hors des blocs de code."""
    dans_code = False
    for i, l in enumerate(lignes, 1):
        if l.lstrip().startswith("```"):
            dans_code = not dans_code
            continue
        if dans_code:
            continue
        for m in re.finditer(r"`([^`\n]+)`", l):
            yield i, m.group(1)


def mots(passage):
    return [mot.strip(",;:()«»") for mot in passage.split()]


def est_chemin(mot):
    if not mot or mot.startswith(("http", "-", "<", "…", '"', "'")) or "<" in mot or "…" in mot:
        return False
    if re.match(r"[A-Za-z][A-Za-z0-9+.-]*://", mot):
        return False  # une adresse : `file://`, `ftp://…`
    if re.fullmatch(r"\.[A-Za-z0-9]+", mot):
        return False  # une extension seule : `.py`
    return "/" in mot or bool(EXTENSION.search(mot))


def existe(base, chemin):
    cible = os.path.join(base, chemin.rstrip("/"))
    return os.path.isdir(cible) if chemin.endswith("/") else os.path.exists(cible)


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("site", help="la copie du site (racine du dépôt)")
    a.add_argument("fichier", nargs="?", help="le fichier Markdown à lire (par défaut : README.md du site)")
    o = a.parse_args()
    racine = os.path.abspath(o.site)
    fichier = os.path.abspath(o.fichier or os.path.join(racine, "README.md"))
    lignes = commun.lire(fichier).splitlines()
    try:
        rubriques = commun.rubriques(racine)
    except (OSError, AttributeError):
        rubriques = []
    bases = [racine, os.path.dirname(fichier)] + [os.path.join(racine, r) for r in rubriques]
    premiers = {}
    for i, passage in passages(lignes):
        entier = passage.strip().strip(",;:()«»")
        if " " in entier and est_chemin(entier) and any(existe(b, entier) for b in bases):
            premiers.setdefault(entier, i)  # un chemin qui contient des espaces, trouvé en entier
            continue
        for mot in mots(passage):
            chemin = re.split(r"[?#]", mot)[0]
            if est_chemin(mot) and chemin:
                premiers.setdefault(chemin, i)
    bases += [os.path.join(racine, c) for c in premiers if c.endswith("/") and existe(racine, c)]
    noms = set()
    for dossier, sous, fichiers in os.walk(racine):
        sous[:] = [s for s in sous if s != ".git"]
        noms.update(fichiers)
    absents = []
    for chemin in sorted(premiers):
        if "*" in chemin:
            ok = bool(glob.glob(os.path.join(racine, chemin)))
        else:
            ok = any(existe(b, chemin) for b in bases) or ("/" not in chemin and chemin in noms)
        print("%-6s %s (ligne %d)" % ("ok" if ok else "ABSENT", chemin, premiers[chemin]))
        if not ok:
            absents.append(chemin)
    print("\n%s : %d chemin(s) cité(s), %d absent(s)%s" % (
        os.path.relpath(fichier, racine), len(premiers), len(absents), " : " + ", ".join(absents) if absents else ""))
    sys.exit(1 if absents else 0)


if __name__ == "__main__":
    main()
