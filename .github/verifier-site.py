#!/usr/bin/env python3
"""Vérifie que le site s'affiche correctement.

Pour chaque rubrique de reglages.js :
  - les fichiers locaux cités dans ressources.js (lien: "fichiers/…") existent ;
  - la page, affichée dans Chrome sans écran, ne montre pas d'erreur ;
  - elle affiche autant de ressources que ressources.js en contient.
Le lien « Code source sur GitHub » (décision de l'enseignant du 10/11/2026, 22:58) :
  - l'accueil et chaque rubrique : vers le dépôt de reglages.js (depot) ; s'il manque, échec ;
  - chaque page déposée dans fichiers/ : vers un dépôt GitHub ; s'il manque, avertissement sans
    échec (une suite, pas un blocage) ; exceptions dans CODE_SOURCE_EXCEPTIONS.

Usage :  python3 .github/verifier-site.py https://babash.github.io/Babash-NSI-SNT
         python3 .github/verifier-site.py http://localhost:8000      (test local)
"""
import html
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


DEPOT_PAR_DEFAUT = "babash/Babash-NSI-SNT"   # celui d'assets/site.js, si reglages.js n'en donne pas
# Pages déposées dispensées du lien, chacune avec sa raison : {"rubrique/fichiers/page.html": "raison"}.
# Vide : toutes les pages déposées sont des pages du site, Compute-it compris (avis du Gardien, N34).
CODE_SOURCE_EXCEPTIONS = {}


def depot():
    """Le dépôt de reglages.js, raccourci comme dans assets/site.js (« propriétaire/nom »).
    La valeur peut être entre guillemets doubles ou simples ; mal écrite ou absente, c'est le
    dépôt par défaut, comme dans assets/site.js (qui affiche alors une erreur sur la page)."""
    m = re.search(r"""^\s*["']?depot["']?\s*:\s*(["'])(.*?)\1""", lire("reglages.js"), re.M)
    valeur = m.group(2).strip() if m else ""
    valeur = re.sub(r"(\.git)?/*$", "", re.sub(r"^https?://(www\.)?github\.com/", "", valeur, flags=re.I))
    return valeur if re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9._-]+", valeur) else DEPOT_PAR_DEFAUT


def code_source(page):
    """Les adresses des liens « Code source sur GitHub » d'une page affichée (DOM de Chrome).
    Le texte du lien est décodé (&nbsp;, &#xA0;, &amp;…), ses balises (icône) retirées et ses
    espaces, insécables compris, ramenés à une espace."""
    trouves = []
    for attributs, contenu in re.findall(r"<a\b([^>]*)>(.*?)</a>", page, re.S | re.I):
        texte = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", contenu))).strip()
        href = re.search(r"""\bhref\s*=\s*(["'])(.*?)\1""", attributs, re.S)
        adresse = html.unescape(href.group(2)).strip() if href else ""
        if texte.lower() == "code source sur github" and adresse.startswith("https://github.com/"):
            trouves.append(adresse.split("#")[0].split("?")[0].rstrip("/"))
    return trouves


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
    pages_internes = set()
    depot_site = "https://github.com/" + depot()

    def lien_du_site(nom, page):
        liens = code_source(page)
        if depot_site.lower() not in [lien.lower() for lien in liens]:   # GitHub ignore la casse
            problemes.append(f"{nom} : pas de lien « Code source sur GitHub » vers {depot_site}"
                             + (f" (liens trouvés : {', '.join(liens)})" if liens else ""))

    for rub in rubriques():
        # sans les commentaires /* … */, qui contiennent des exemples
        source = re.sub(r"/\*.*?\*/", "", lire(f"{rub}/ressources.js"), flags=re.S)
        attendu = len(re.findall(r"^ressource\(\{", source, re.M))
        total += attendu

        for fichier in re.findall(r'"(fichiers/[^"]+)"', source):
            fichier = re.split(r"[#?]", fichier)[0]
            if not os.path.exists(os.path.join(RACINE, rub, fichier)):
                problemes.append(f"{rub} : le fichier {fichier} n'existe pas")
            elif fichier.endswith((".html", "/")):
                pages_internes.add(f"{rub}/{fichier}")

        page = afficher(f"{base}/{rub}/")
        if 'class="alerte"' in page:
            problemes.append(f"{rub} : la page affiche une erreur")
        affiche = page.count('<li class="res"')
        etat = "ok" if affiche == attendu else "ÉCART"
        print(f"{rub:15} {affiche:3} ressources affichées / {attendu:3} dans ressources.js   {etat}")
        if affiche != attendu:
            problemes.append(f"{rub} : {affiche} ressources affichées au lieu de {attendu}")
        lien_du_site(rub, page)

    accueil = afficher(f"{base}/")
    erreur_accueil = 'class="alerte"' in accueil
    if erreur_accueil:
        problemes.append("accueil : la page affiche une erreur")
    lien_du_site("accueil", accueil)
    print(f"{'accueil':15} {'erreur' if erreur_accueil else 'ok'}")
    print(f"Total : {total} ressources")

    # Pages déposées sur le site (TD, fiches, diaporamas, applications) : elles doivent
    # s'afficher avec un vrai contenu, et non une page vide ou une erreur 404.
    vides = []
    sans_code = []
    for chemin in sorted(pages_internes):
        page = afficher(f"{base}/{chemin}")
        corps = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
        texte = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps)).strip()
        if len(texte) < 80 or re.search(r"<title>[^<]*(404|not found)", page, re.I):
            vides.append(chemin)
            problemes.append(f"{chemin} : page vide ou introuvable")
        elif chemin not in CODE_SOURCE_EXCEPTIONS and not code_source(page):
            sans_code.append(chemin)   # une suite, pas un blocage (fiche du Gardien) : sans échec
    print(f"Pages déposées : {len(pages_internes) - len(vides)} / {len(pages_internes)} s'affichent")
    print(f"Lien « Code source sur GitHub » : {len(pages_internes) - len(vides) - len(sans_code)} / "
          f"{len(pages_internes) - len(vides)} pages déposées"
          + (f", {len(CODE_SOURCE_EXCEPTIONS)} dispensée(s)" if CODE_SOURCE_EXCEPTIONS else ""))
    if sans_code:
        print("À compléter (sans échec) : pas de lien « Code source sur GitHub » dans")
        for chemin in sans_code:
            print("   -", chemin)
        if os.environ.get("GITHUB_ACTIONS"):
            print("::warning title=Lien « Code source sur GitHub »::" + str(len(sans_code)) +
                  " page(s) déposée(s) sans le lien : " + ", ".join(sans_code))

    if problemes:
        print("\nProblèmes :")
        for p in problemes:
            print(" -", p)
        sys.exit(1)
    print("\nTout s'affiche correctement.")


if __name__ == "__main__":
    main()
