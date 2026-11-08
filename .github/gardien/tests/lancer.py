#!/usr/bin/env python3
"""Tests de non-régression du Gardien : un seul point d'entrée.

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/tests/lancer.py [--ref REF | --source DOSSIER] [--travail DOSSIER]
                                             [--seulement t02,t02b,…]

Extrait REF (par défaut HEAD ; par exemple origin/archi/t33-comparaison-complete) avec git
archive dans le dossier de travail, ou prend une copie déjà extraite (--source, par exemple le
dossier « apres » de controler.py), puis lance chaque test sur cette copie, chacun dans son
propre processus :
  t02      11 cas   la validation des données détecte les fautes graves (T02)
  t02b     16 cas   règles 19 et 20, intitulés Pix (T02b)
  t26b      4 cas   point médian permis dans les textes, refusé dans les identifiants (T26b)
  t12      24 cas   scripts du contrôle en ligne : attendre_deploiement.py, liens_seconde_passe.py (T12)
  t19      10 cas   pied de page de l'accueil et de SNT selon reglages.js, dans Chrome (T19)
  outils   10 cas   outils du Gardien : caracteres, chemins_readme, zones, contraste_zone (T32)
Les tests lancent les scripts de la copie (scripts/valider_donnees.py…) : à rejouer quand une
branche modifie ces scripts, les données d'exemple de donnees/, assets/site.js ou reglages.js.
Les outils du Gardien essayés par « outils » sont ceux de la copie d'où l'on lance ce fichier.
Il faut Python avec Playwright et Pillow, et Chrome ou Chromium (t19, outils).
Le dossier de travail créé par défaut est effacé si tout est vert ; sinon, il est gardé pour
l'examen. Résumé à la fin. Code de sortie : 0 tout est vert, 1 sinon.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import cadre  # noqa: E402

# nom, utilise la copie du site
TESTS = [("t02", True), ("t02b", True), ("t26b", True), ("t12", True), ("t19", True), ("outils", False)]


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    quoi = a.add_mutually_exclusive_group()
    quoi.add_argument("--ref", default="HEAD", help="version du dépôt à tester (défaut : HEAD)")
    quoi.add_argument("--source", help="copie du site déjà extraite, à tester telle quelle")
    a.add_argument("--travail", help="dossier de travail (défaut : un dossier temporaire)")
    a.add_argument("--seulement", help="tests à lancer, séparés par des virgules (défaut : tous)")
    o = a.parse_args()
    choisis = [n for n, _ in TESTS]
    if o.seulement:
        choisis = o.seulement.split(",")
        inconnus = [n for n in choisis if n not in dict(TESTS)]
        if inconnus:
            a.error("tests inconnus : %s (possibles : %s)" % (", ".join(inconnus), ", ".join(dict(TESTS))))
    travail = os.path.abspath(o.travail) if o.travail else tempfile.mkdtemp(prefix="gardien-tests-")
    os.makedirs(travail, exist_ok=True)
    site = None
    if not any(avec_site for nom, avec_site in TESTS if nom in choisis):
        pass  # aucun test choisi ne lit le site : rien à extraire
    elif o.source:
        site = os.path.abspath(o.source)
        print("Copie testée : %s" % site)
    else:
        depot = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ICI, capture_output=True, text=True).stdout.strip()
        sha = subprocess.run(["git", "rev-parse", "--short", o.ref], cwd=depot, capture_output=True, text=True)
        if sha.returncode:
            a.error("version introuvable : " + o.ref)
        site = os.path.join(travail, "site")
        shutil.rmtree(site, ignore_errors=True)
        cadre.exporter(depot, o.ref, site)
        print("Version testée : %s (%s), extraite dans %s" % (o.ref, sha.stdout.strip(), site))
    resultats = []
    for nom, avec_site in TESTS:
        if nom not in choisis:
            continue
        script = os.path.join(ICI, "test_%s.py" % nom)
        dossier = os.path.join(travail, nom)
        print("\n### test_%s.py" % nom, flush=True)
        debut = time.time()
        r = subprocess.run([sys.executable, "-I", "-B", script] + ([site] if avec_site else []) + [dossier],
                           capture_output=True, text=True)
        sortie = (r.stdout + r.stderr).rstrip()
        print(sortie, flush=True)
        m = re.search(r"^(\d+) cas, (\d+) échec\(s\)$", sortie, re.M)
        cas, echecs = (int(m.group(1)), int(m.group(2))) if m else (0, None)
        etat = "vert" if r.returncode == 0 and m and echecs == 0 else "ROUGE"
        resultats.append((nom, cas, echecs, etat, time.time() - debut))
    print("\n=== Résumé (%s) ===" % travail)
    for nom, cas, echecs, etat, duree in resultats:
        detail = "%d cas, %d échec(s)" % (cas, echecs) if echecs is not None else "interrompu avant son bilan"
        print("  %-8s %-28s %-6s (%.0f s)" % (nom, detail, etat, duree))
    rouge = any(etat != "vert" for _, _, _, etat, _ in resultats)
    if not o.travail and not rouge:
        shutil.rmtree(travail, ignore_errors=True)
        print("Tout est vert : dossier de travail effacé.")
    elif rouge:
        print("Dossier de travail gardé pour l'examen : " + travail)
    sys.exit(1 if rouge else 0)


if __name__ == "__main__":
    main()
