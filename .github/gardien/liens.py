#!/usr/bin/env python3
"""Liens du site (Gardien) : liens internes, liens principaux vers GitHub, doublons.

Usage : python3 -I .github/gardien/liens.py DOSSIER_DU_SITE

1. Les ressources : depuis T51b (le site lit la vitrine et les fiches), chaque document des fiches
   donnees/ressources/*.json ; avant, chaque `lien:` et chaque annexe des */ressources.js. Un
   fichier du site (champ « fichier », ou lien relatif) doit exister (un dossier « …/ » doit
   contenir index.html).
2. Aucun lien principal (le document principal d'une fiche, ou `lien:`) vers une page GitHub
   (github.com, raw.githubusercontent.com, gist.github.com) ; un autre document GitHub doit avoir le
   rôle « code-source » ou un titre qui commence par « Code source » (fiches), ou un libellé qui
   annonce le code source (anciennes listes). Ce dernier point est pour information.
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


def fiches(racine, casses, github, annexes_github, toutes):
    """T51b : les documents de toutes les fiches (la bibliothèque les montre toutes, les rubriques
    celles que place la vitrine)."""
    for chemin in sorted(glob.glob(os.path.join(racine, "donnees", "ressources", "*.json"))):
        rid = os.path.basename(chemin)[:-5]
        ou_fiche = "donnees/ressources/%s.json" % rid
        f = commun.fiche(racine, rid)
        if not isinstance(f, dict):
            casses.append("%s : fiche illisible" % ou_fiche)
            continue
        docs = [d for d in f.get("documents", []) if isinstance(d, dict)]
        principal = next((d for d in docs if d.get("principal") is True), docs[0] if docs else None)
        for i, d in enumerate(docs):
            ou = "%s › documents[%d]" % (ou_fiche, i)
            if isinstance(d.get("url"), str) and d["url"]:
                u = d["url"]
                toutes[u.rstrip("/")].append(ou)
                if GITHUB.match(u):
                    if d is principal:
                        github.append("%s : lien principal vers GitHub : %s" % (ou, u))
                    elif d.get("role") != "code-source" and not str(d.get("titre") or "").lower().startswith("code source"):
                        annexes_github.append("%s : document « %s » vers GitHub sans le rôle « code-source » : %s"
                                              % (ou, d.get("titre") or d.get("role"), u))
            elif isinstance(d.get("fichier"), str) and d["fichier"]:
                if not existe(racine, d["fichier"], racine):
                    casses.append("%s : fichier introuvable : %s" % (ou, d["fichier"]))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0 if sys.argv[1:2] in (["-h"], ["--help"]) else 2)
    racine = os.path.abspath(sys.argv[1])
    casses, github, annexes_github, toutes = [], [], [], collections.defaultdict(list)
    if commun.lit_la_vitrine(racine):
        fiches(racine, casses, github, annexes_github, toutes)
    else:
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
