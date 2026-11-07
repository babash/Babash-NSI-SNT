#!/usr/bin/env python3
"""Liens du site (Gardien) : liens internes, liens principaux vers GitHub, doublons.

Usage : python3 liens.py DOSSIER_DU_SITE

1. Dans chaque */ressources.js : chaque `lien:` et chaque annexe relative doit mener à un
   fichier existant (un dossier « …/ » doit contenir index.html).
2. Aucun lien principal (`lien:`) vers une page GitHub (github.com, raw.githubusercontent.com,
   gist.github.com) ; en annexe, le libellé doit annoncer le code source.
3. Dans chaque page HTML du site (index.html, */fichiers/**.html) : chaque href et src relatif
   doit mener à un fichier existant.
4. Liste des liens externes en double (même adresse à plusieurs endroits : permis, pour info).
Code de sortie 1 si un lien interne est cassé ou si un lien principal mène à GitHub.
"""
import collections
import glob
import os
import re
import sys
from urllib.parse import unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402

GITHUB = re.compile(r"^https?://(?:www\.)?(?:github\.com|raw\.githubusercontent\.com|gist\.github\.com)/", re.I)


def externe(u):
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", u, re.I)) or u.startswith("//")


def existe(base_dir, u, racine):
    chemin = unquote(urlparse(u).path)
    if not chemin:
        return True  # simple ancre ou requête sur la page elle-même
    cible = os.path.normpath(os.path.join(racine, chemin.lstrip("/")) if chemin.startswith("/") else os.path.join(base_dir, chemin))
    if chemin.endswith("/") or os.path.isdir(cible):
        return os.path.exists(os.path.join(cible, "index.html"))
    return os.path.exists(cible)


def main():
    racine = os.path.abspath(sys.argv[1])
    casses, github, annexes_github, toutes = [], [], [], collections.defaultdict(list)
    for rub in sorted(set(commun.rubriques(racine)) | {os.path.basename(os.path.dirname(f)) for f in glob.glob(os.path.join(racine, "*", "ressources.js"))}):
        fichier = os.path.join(racine, rub, "ressources.js")
        if not os.path.exists(fichier):
            continue
        lignes = commun.lire(fichier).splitlines()
        dans_commentaire = False
        dans_annexes = False
        for i, l in enumerate(lignes, 1):
            if "/*" in l:
                dans_commentaire = True
            if dans_commentaire:
                if "*/" in l:
                    dans_commentaire = False
                continue
            s = l.strip()
            if s.startswith("annexes"):
                dans_annexes = True
            elif dans_annexes and s.startswith("}"):
                dans_annexes = False
            m = re.match(r'\s*lien\s*:\s*"([^"]*)"', l)
            a = re.match(r'\s*"([^"]+)"\s*:\s*"([^"]*)"', l) if dans_annexes else None
            for (nature, libelle, u) in ([("lien", "", m.group(1))] if m else []) + ([("annexe", a.group(1), a.group(2))] if a else []):
                ou = "%s/ressources.js:%d" % (rub, i)
                if externe(u):
                    toutes[u.rstrip("/")].append(ou)
                    if GITHUB.match(u):
                        if nature == "lien":
                            github.append("%s : lien principal vers GitHub : %s" % (ou, u))
                        elif "code source" not in libelle.lower():
                            annexes_github.append("%s : annexe « %s » vers GitHub sans le libellé « Code source » : %s" % (ou, libelle, u))
                elif not existe(os.path.join(racine, rub), u, racine):
                    casses.append("%s : %s introuvable : %s" % (ou, nature, u))
    pages = [os.path.join(racine, "index.html")] + glob.glob(os.path.join(racine, "*", "index.html")) + \
        glob.glob(os.path.join(racine, "*", "fichiers", "**", "*.html"), recursive=True)
    for page in sorted(set(pages)):
        rel = os.path.relpath(page, racine)
        for i, l in enumerate(commun.lire(page).splitlines(), 1):
            for m in re.finditer(r'\b(?:href|src)\s*=\s*["\']([^"\']+)["\']', l):
                u = m.group(1)
                if externe(u) or u.startswith("#") or "{" in u or "+" in u or u.startswith("javascript:"):
                    continue
                if not existe(os.path.dirname(page), u, racine):
                    casses.append("%s:%d : lien ou ressource introuvable : %s" % (rel, i, u))
    doublons = {u: o for u, o in toutes.items() if len(o) > 1}
    print("Liens internes cassés : %d" % len(casses))
    for c in casses:
        print("  -", c)
    print("Liens principaux vers GitHub : %d" % len(github))
    for g in github:
        print("  -", g)
    print("Annexes GitHub sans libellé « Code source » : %d" % len(annexes_github))
    for g in annexes_github:
        print("  -", g)
    print("Liens externes : %d adresses distinctes, %d en double (permis) :" % (len(toutes), len(doublons)))
    for u, o in sorted(doublons.items()):
        print("  - %s : %s" % (u, ", ".join(o)))
    sys.exit(1 if casses or github else 0)


if __name__ == "__main__":
    main()
