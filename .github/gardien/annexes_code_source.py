#!/usr/bin/env python3
"""Les ressources qui ont un dépôt le donnent-elles en « Code source » ? (Gardien, contrôle 2)

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/annexes_code_source.py DOSSIER_DU_SITE [--proprietaire NOM]

Depuis T51b (le site lit la vitrine et les fiches), lit chaque fiche donnees/ressources/*.json : elle
« a un dépôt » si un de ses documents mène à https://<propriétaire>.github.io/<dépôt>/…, à
https://github.com/<propriétaire>/<dépôt>, ou est un fichier déposé dans le site (champ « fichier ») ;
elle le donne si un document a le rôle « code-source » (ou un titre qui commence par « Code source »).
Avant T51b, lit chaque bloc ressource({ … }) des listes */ressources.js (hors commentaires, rubriques de
reglages.js) : une ressource « a un dépôt » si son lien principal ou une annexe mène à
https://<propriétaire>.github.io/<dépôt>/…, à https://github.com/<propriétaire>/<dépôt>, ou à une
page déposée dans le site (fichiers/…, dont le dépôt est celui du site). Elle donne son dépôt si
une annexe a un libellé qui commence par « Code source » (« Code source, à dupliquer » compte).
Le propriétaire est celui du réglage depot de reglages.js (par défaut : babash).
Décision de l'enseignant du 10/11/2026 (22:58) ; une annexe qui manque est une suite, pas un
blocage (fiche du Gardien, contrôle 2). Code de sortie 1 s'il en manque une.
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402


def proprietaire_du_site(racine):
    m = re.search(r"""^\s*["']?depot["']?\s*:\s*(["'])(.*?)\1""", commun.lire(os.path.join(racine, "reglages.js")), re.M)
    valeur = re.sub(r"^https?://(www\.)?github\.com/", "", m.group(2).strip(), flags=re.I) if m else ""
    return valeur.split("/")[0] if "/" in valeur else "babash"


def ressources(racine, rubrique):
    source = commun.sans_commentaires(commun.lire(os.path.join(racine, rubrique, "ressources.js")))
    for bloc in re.findall(r"^ressource\(\{(.*?)^\}\);", source, re.S | re.M):
        titre = re.search(r'\btitre:\s*"([^"]*)"', bloc)
        lien = re.search(r'\blien:\s*"([^"]*)"', bloc)
        annexes = re.search(r"\bannexes:\s*\{(.*?)\}", bloc, re.S)
        yield ((titre.group(1) if titre else "?"), (lien.group(1) if lien else ""),
               re.findall(r'"([^"]+)":\s*"([^"]*)"', annexes.group(1)) if annexes else [])


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("site", help="la copie du site (racine du dépôt)")
    a.add_argument("--proprietaire", help="propriétaire des dépôts (défaut : celui du réglage depot)")
    o = a.parse_args()
    racine = os.path.abspath(o.site)
    proprio = o.proprietaire or proprietaire_du_site(racine)
    depot_re = re.compile(r"^https://(%s\.github\.io/[^/?#]+|github\.com/%s/[^/?#]+)" % (re.escape(proprio), re.escape(proprio)), re.I)
    total, avec_depot, sans = 0, 0, []
    if commun.lit_la_vitrine(racine):
        for chemin in sorted(glob.glob(os.path.join(racine, "donnees", "ressources", "*.json"))):
            f = commun.fiche(racine, os.path.basename(chemin)[:-5])
            if not isinstance(f, dict):
                continue
            total += 1
            docs = [d for d in f.get("documents", []) if isinstance(d, dict)]
            if not any(depot_re.match(str(d.get("url") or "")) or d.get("fichier") for d in docs):
                continue
            avec_depot += 1
            if not any(d.get("role") == "code-source" or str(d.get("titre") or "").startswith("Code source") for d in docs):
                sans.append("%s : %s" % (f.get("id"), f.get("titre")))
        print("%d fiche(s) ; %d avec un dépôt de « %s » ou un fichier déposé ; %d sans document « Code source »%s" % (
            total, avec_depot, proprio, len(sans), " :" if sans else "."))
        for s in sans:
            print("  - " + s)
        sys.exit(1 if sans else 0)
    for rubrique in commun.rubriques(racine):
        for titre, lien, annexes in ressources(racine, rubrique):
            total += 1
            adresses = [lien] + [adresse for _, adresse in annexes]
            if not any(depot_re.match(x) or x.startswith("fichiers/") for x in adresses):
                continue
            avec_depot += 1
            if not any(libelle.startswith("Code source") for libelle, _ in annexes):
                sans.append("%s : %s (%s)" % (rubrique, titre, lien))
    print("%d ressource(s) ; %d avec un dépôt de « %s » ou une page déposée ; %d sans annexe « Code source »%s" % (
        total, avec_depot, proprio, len(sans), " :" if sans else "."))
    for s in sans:
        print("  - " + s)
    sys.exit(1 if sans else 0)


if __name__ == "__main__":
    main()
