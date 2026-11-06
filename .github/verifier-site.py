#!/usr/bin/env python3
"""Vérifie que le site s'affiche correctement.

Pour chaque rubrique de reglages.js :
  - les fichiers locaux cités dans ressources.js (lien: "fichiers/…") existent ;
  - la page, affichée dans Chrome sans écran, ne montre pas d'erreur ;
  - elle affiche autant de ressources que ressources.js en contient.

Usage :  python3 .github/verifier-site.py https://babash.github.io/Babash-NSI-SNT
         python3 .github/verifier-site.py http://localhost:8000      (test local)
"""
import os
import re
import shutil
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


def rubriques():
    texte = lire("reglages.js")
    bloc = re.search(r"rubriques\s*:\s*\[(.*?)\]", texte, re.S).group(1)
    return re.findall(r'"([^"]+)"', bloc)


def chrome():
    for nom in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(nom):
            return nom
    sys.exit("Chrome est introuvable.")


def afficher(url):
    sortie = subprocess.run(
        [chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
         "--virtual-time-budget=20000", "--dump-dom", url],
        capture_output=True, text=True, timeout=120,
    )
    return sortie.stdout


def main():
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://babash.github.io/Babash-NSI-SNT"
    problemes = []
    total = 0

    for rub in rubriques():
        # sans les commentaires /* … */, qui contiennent des exemples
        source = re.sub(r"/\*.*?\*/", "", lire(f"{rub}/ressources.js"), flags=re.S)
        attendu = len(re.findall(r"^ressource\(\{", source, re.M))
        total += attendu

        for fichier in re.findall(r'"(fichiers/[^"]+)"', source):
            if not os.path.exists(os.path.join(RACINE, rub, fichier)):
                problemes.append(f"{rub} : le fichier {fichier} n'existe pas")

        page = afficher(f"{base}/{rub}/")
        if 'class="alerte"' in page:
            problemes.append(f"{rub} : la page affiche une erreur")
        affiche = page.count('<li class="res"')
        etat = "ok" if affiche == attendu else "ÉCART"
        print(f"{rub:15} {affiche:3} ressources affichées / {attendu:3} dans ressources.js   {etat}")
        if affiche != attendu:
            problemes.append(f"{rub} : {affiche} ressources affichées au lieu de {attendu}")

    accueil = afficher(f"{base}/")
    erreur_accueil = 'class="alerte"' in accueil
    if erreur_accueil:
        problemes.append("accueil : la page affiche une erreur")
    print(f"{'accueil':15} {'erreur' if erreur_accueil else 'ok'}")
    print(f"Total : {total} ressources")

    if problemes:
        print("\nProblèmes :")
        for p in problemes:
            print(" -", p)
        sys.exit(1)
    print("\nTout s'affiche correctement.")


if __name__ == "__main__":
    main()
