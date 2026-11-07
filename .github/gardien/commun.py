"""Outils communs aux contrôles du Gardien (aucune dépendance au dépôt).

- rubriques(racine)         : les dossiers listés dans reglages.js
- pages_site(racine)        : accueil + une page par rubrique
- pages_fichiers(racine)    : les pages HTML déposées dans */fichiers/
- attendu(racine, rubrique) : nombre de ressource({ … }) dans ressources.js
- lancer(p)                 : Chrome sans écran (passe par le proxy de la session s'il existe)
- polices(contexte, dossier): sert Google Fonts depuis des paquets fontsource locaux
                              (fonts.googleapis.com est bloqué dans les sessions Claude)
"""
import glob
import os
import re
import shutil
from urllib.parse import parse_qs, urlparse


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()


def rubriques(racine):
    texte = lire(os.path.join(racine, "reglages.js"))
    bloc = re.search(r"rubriques\s*:\s*\[(.*?)\]", texte, re.S).group(1)
    return re.findall(r'"([^"]+)"', bloc)


def pages_site(racine):
    return [("accueil", "")] + [(r, r + "/") for r in rubriques(racine)]


def pages_fichiers(racine):
    pages = []
    for f in sorted(glob.glob(os.path.join(racine, "*", "fichiers", "**", "*.html"), recursive=True)):
        rel = os.path.relpath(f, racine).replace(os.sep, "/")
        pages.append((rel, rel))
    return pages


def sans_commentaires(source):
    return re.sub(r"/\*.*?\*/", "", source, flags=re.S)


def attendu(racine, rub):
    source = sans_commentaires(lire(os.path.join(racine, rub, "ressources.js")))
    return len(re.findall(r"^ressource\(\{", source, re.M))


def chrome():
    for nom in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    return None


def lancer(p):
    options = {"args": ["--no-sandbox"]}
    exe = chrome()
    if exe:
        options["executable_path"] = exe
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        options["proxy"] = {"server": proxy, "bypass": "localhost,127.0.0.1"}
    return p.chromium.launch(**options)


def _css_polices(url, dossier):
    faces = []
    for famille in parse_qs(urlparse(url).query).get("family", []):
        nom, _, axes = famille.partition(":")
        slug = nom.strip().lower().replace(" ", "-")
        reps = glob.glob(os.path.join(dossier, "fontsource-%s-*" % slug, "files"))
        if not reps:
            continue
        rep = reps[0]
        combos = []
        if "@" in axes:
            etiquettes, _, valeurs = axes.partition("@")
            etiquettes = etiquettes.split(",")
            for v in valeurs.split(";"):
                d = dict(zip(etiquettes, v.split(",")))
                combos.append(("italic" if d.get("ital") == "1" else "normal", d.get("wght", "400")))
        else:
            combos.append(("normal", "400"))
        for style, poids in combos:
            if ".." in poids:
                bas, haut = (int(x) for x in poids.split(".."))
                liste = [str(w) for w in range(100, 1000, 100) if bas <= w <= haut]
            else:
                liste = [poids]
            for w in liste:
                f = os.path.join(rep, "%s-latin-%s-%s.woff2" % (slug, w, style))
                if os.path.exists(f):
                    faces.append(
                        "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;"
                        "src:url(https://fonts.gstatic.com/local/%s) format('woff2');}"
                        % (nom.strip(), style, w, os.path.basename(os.path.dirname(rep)) + "/" + os.path.basename(f))
                    )
    return "\n".join(faces)


def polices(contexte, dossier):
    """Sert les polices Google depuis des paquets fontsource décompressés dans `dossier`."""
    if not dossier or not os.path.isdir(dossier):
        return False

    def css(route):
        route.fulfill(body=_css_polices(route.request.url, dossier), content_type="text/css",
                      headers={"Access-Control-Allow-Origin": "*"})

    def fichier(route):
        rel = route.request.url.split("/local/", 1)[1]
        chemin = os.path.realpath(os.path.join(dossier, rel.split("/")[0], "files", rel.split("/")[-1]))
        if not chemin.startswith(os.path.realpath(dossier)) or not os.path.exists(chemin):
            return route.fulfill(status=404, body="")
        with open(chemin, "rb") as f:
            route.fulfill(body=f.read(), content_type="font/woff2", headers={"Access-Control-Allow-Origin": "*"})

    contexte.route("https://fonts.googleapis.com/**", css)
    contexte.route("https://fonts.gstatic.com/local/**", fichier)
    return True
