#!/usr/bin/env python3
"""Vérifie que le site s'affiche correctement.

Pour chaque rubrique de reglages.js :
  - les fichiers locaux cités dans ressources.js (lien: "fichiers/…") existent ;
  - la page, affichée dans Chrome sans écran, ne montre pas d'erreur ;
  - elle affiche autant de ressources que ressources.js en contient.
La bibliothèque (bibliotheque/, T50) : donnees/bibliotheque.json se lit en ligne et correspond aux
fiches visibles de l'extérieur de cette copie ; la page en affiche autant, sans erreur ; une recherche
trouve une ressource par un mot de son titre ; trois fiches complètes s'ouvrent (?r=identifiant).
Le lien « Code source sur GitHub » (décision de l'enseignant du 10/11/2026, 22:58) :
  - l'accueil, chaque rubrique et la bibliothèque : vers le dépôt de reglages.js (depot) ; s'il manque, échec ;
  - chaque page déposée dans fichiers/ : vers un dépôt GitHub ; s'il manque, avertissement sans
    échec (une suite, pas un blocage) ; exceptions dans CODE_SOURCE_EXCEPTIONS.

Usage :  python3 .github/verifier-site.py https://babash.github.io/Babash-NSI-SNT
         python3 .github/verifier-site.py http://localhost:8000      (test local)
"""
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

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


def fiches_publiques():
    """Les fiches de cette copie qui ont au moins un document visible de l'extérieur (cahier des charges, § 3.2),
    triées par identifiant : ce que la bibliothèque en ligne doit montrer."""
    out = []
    for chemin in sorted(glob.glob(os.path.join(RACINE, "donnees", "ressources", "*.json"))):
        try:
            with open(chemin, encoding="utf-8") as f:
                fiche = json.load(f)
        except (OSError, ValueError):
            continue  # une fiche illisible est signalée par scripts/valider_donnees.py
        if any(isinstance(d, dict) and (d.get("visible") or {}).get("exterieur") is True for d in fiche.get("documents", [])):
            out.append(fiche)
    return sorted(out, key=lambda f: f.get("id", ""))


def bibliotheque(base, problemes, lien_du_site):
    """La page bibliotheque/ (T50) : les données construites à la publication se lisent en ligne et
    correspondent aux fiches de cette copie ; la page affiche autant de ressources, sans erreur, avec le lien
    « Code source sur GitHub » ; une recherche trouve une ressource par un mot de son titre ; la fiche
    complète de trois ressources s'ouvre (?r=identifiant)."""
    fiches = fiches_publiques()
    if not fiches:
        print(f"{'bibliothèque':15} pas encore de fiches dans donnees/ressources/ : rien à vérifier")
        return
    try:
        with urllib.request.urlopen(f"{base}/donnees/bibliotheque.json", timeout=60) as r:
            en_ligne = json.loads(r.read().decode("utf-8"))
        ids = sorted(x.get("id") for x in en_ligne.get("ressources", []))
    except (OSError, ValueError) as e:
        problemes.append(f"bibliothèque : donnees/bibliotheque.json illisible en ligne ({e}). Il est construit par le "
                         "workflow « Publier le site » : la source de GitHub Pages est-elle bien « GitHub Actions » ?")
        return
    attendus = [f["id"] for f in fiches]
    if ids != attendus:
        manquent = sorted(set(attendus) - set(ids))
        en_trop = sorted(set(ids) - set(attendus))
        problemes.append("bibliothèque : bibliotheque.json en ligne ne correspond pas aux fiches"
                         + (f" ; manquent : {', '.join(manquent[:5])}" if manquent else "")
                         + (f" ; en trop : {', '.join(en_trop[:5])}" if en_trop else ""))

    page = afficher(f"{base}/bibliotheque/")
    m = re.search(r'class="compte">(\d+) ressources?<', page)
    affiche = int(m.group(1)) if m else None
    if 'class="alerte"' in page:
        problemes.append("bibliothèque : la page affiche une erreur")
    if affiche != len(attendus):
        problemes.append(f"bibliothèque : {affiche if affiche is not None else 'aucune'} ressource(s) affichée(s) "
                         f"au lieu de {len(attendus)}")
    lien_du_site("bibliothèque", page)
    print(f"{'bibliothèque':15} {affiche if affiche is not None else '—':>3} ressources affichées / {len(attendus):3} fiches visibles de l'extérieur")

    # Une recherche : le premier mot assez long du titre d'une ressource la trouve
    for f in fiches:
        mots = [x for x in re.findall(r"[^\W\d_]{6,}", f.get("titre", ""))]
        if mots:
            page = afficher(f"{base}/bibliotheque/?q={urllib.parse.quote(mots[0])}")
            m = re.search(r'class="compte">(\d+) ressources?<', page)
            if not m or int(m.group(1)) < 1 or "r=" + urllib.parse.quote(f["id"]) not in page:
                problemes.append(f"bibliothèque : la recherche « {mots[0]} » ne trouve pas « {f['titre']} »")
            else:
                print(f"{'':15} recherche « {mots[0]} » : {m.group(1)} ressource(s), dont « {f['titre'][:40]} »")
            break

    # La fiche complète : la première, celle du milieu et la dernière
    for f in {x["id"]: x for x in (fiches[0], fiches[len(fiches) // 2], fiches[-1])}.values():
        page = afficher(f"{base}/bibliotheque/?r={urllib.parse.quote(f['id'])}")
        titre = html.escape(f.get("titre", ""), quote=False)
        if 'class="fiche-titre"' not in page or titre not in page or 'class="alerte"' in page:
            problemes.append(f"bibliothèque : la fiche complète de « {f['id']} » ne s'affiche pas")
        else:
            print(f"{'':15} fiche « {f['id']} » : ok")


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

    bibliotheque(base, problemes, lien_du_site)

    if problemes:
        print("\nProblèmes :")
        for p in problemes:
            print(" -", p)
        sys.exit(1)
    print("\nTout s'affiche correctement.")


if __name__ == "__main__":
    main()
