"""Outils communs aux contrôles du Gardien (aucune dépendance au dépôt).

- rubriques(racine)         : les dossiers listés dans reglages.js
- pages_site(racine)        : accueil + une page par rubrique
- pages_fichiers(racine)    : les pages HTML déposées dans */fichiers/
- attendu(racine, rubrique) : nombre de ressource({ … }) dans ressources.js
- lancer(p)                 : Chrome sans écran (passe par le proxy de la session s'il existe)
- polices(contexte, dossier): sert Google Fonts depuis des paquets fontsource locaux
                              (fonts.googleapis.com est bloqué dans les sessions Claude)
- servir(dossier)           : sert un dossier en HTTP local, sans journal (pages d'un autre dépôt)
- externes(contexte, …)     : toutes les requêtes vers un autre site : CDN servis depuis des
                              paquets npm, Tailwind compilé, faux client Supabase ; le reste bloqué
"""
import functools
import glob
import http.server
import json
import os
import re
import shutil
import threading
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


class _Discret(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servir(dossier):
    """Sert un dossier en HTTP sur 127.0.0.1 (port libre) ; (serveur, adresse). À la fin : serveur.shutdown()."""
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Discret, directory=dossier))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur, "http://127.0.0.1:%d" % serveur.server_address[1]


# supabase-js remplacé par un client qui répond « rien » à tout : la page s'affiche, rien n'est lu ni
# écrit dans une vraie base (les agents ne lisent jamais les données des élèves).
SUPABASE_FAUX = """window.supabase = { createClient: () => {
  const r = async () => ({ data: [], error: null });
  const q = () => ({ select: q, insert: r, update: r, upsert: r, delete: r, eq: q, order: q, limit: r, single: r,
                     then: (ok) => ok({ data: [], error: null }) });
  return { rpc: r, from: q, channel: () => ({ on: function () { return this; }, subscribe: () => ({}) }),
           removeChannel: () => {}, auth: { getSession: async () => ({ data: { session: null } }) } };
} };"""
SVG_VIDE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"></svg>'
TYPES = {".css": "text/css", ".js": "application/javascript", ".mjs": "application/javascript",
         ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".svg": "image/svg+xml",
         ".png": "image/png", ".json": "application/json", ".map": "application/json"}


def lire_cdn(liste):
    """« PREFIXE=DOSSIER » (option --cdn des outils) -> [(préfixe, dossier)]."""
    paires = []
    for x in liste or []:
        prefixe, sep, dossier = x.partition("=")
        if not sep or not prefixe.startswith("http") or not os.path.isdir(dossier):
            raise SystemExit("--cdn attend PREFIXE=DOSSIER, avec un dossier existant : " + x)
        paires.append((prefixe, os.path.abspath(dossier)))
    return paires


def externes(contexte, cdn=(), tailwind=None, polices_dossier=None, bloquees=None):
    """Les requêtes hors de 127.0.0.1, pour afficher les pages d'un autre dépôt sans réseau :
    - polices Google servies depuis fontsource (polices_dossier, voir polices()) ;
    - bibliothèques des CDN : cdn = [(préfixe d'adresse, dossier du paquet npm)] ; le reste de
      l'adresse est cherché dans le dossier, puis sans « .min » (reveal.min.css -> reveal.css) ;
    - Tailwind « Play CDN » (cdn.tailwindcss.com) : remplacé par la feuille compilée `tailwind`
      (texte CSS), injectée dans la page ;
    - supabase-js : remplacé par SUPABASE_FAUX ; l'API Supabase (*.supabase.co) est bloquée ;
    - images de mirrors.creativecommons.org : une image vide ;
    - tout le reste est bloqué, et compté dans bloquees (un Counter, par domaine ; « absent:… »
      pour un fichier de CDN introuvable)."""
    if polices_dossier:
        polices(contexte, polices_dossier)

    def compter(cle):
        if bloquees is not None:
            bloquees[cle] += 1

    def fichier(route, chemin):
        for essai in (chemin, re.sub(r"\.min(\.\w+)$", r"\1", chemin)):
            if os.path.isfile(essai):
                with open(essai, "rb") as f:
                    return route.fulfill(status=200, body=f.read(), headers={"Access-Control-Allow-Origin": "*"},
                                         content_type=TYPES.get(os.path.splitext(essai)[1], "application/octet-stream"))
        compter("absent:" + os.path.basename(chemin))
        return route.abort()

    def router(route):
        url = route.request.url
        if url.startswith(("http://127.0.0.1", "http://localhost", "data:", "blob:")):
            return route.continue_()
        if url.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com/local/")) and polices_dossier:
            return route.fallback()
        for prefixe, dossier in cdn:
            if url.startswith(prefixe):
                rel = url[len(prefixe):].split("?")[0].split("#")[0].lstrip("/")
                chemin = os.path.realpath(os.path.join(dossier, rel))
                if os.path.commonpath([chemin, os.path.realpath(dossier)]) != os.path.realpath(dossier):
                    compter("hors du paquet:" + rel[:40])
                    return route.abort()  # « ../ » : rien hors du dossier du paquet
                return fichier(route, chemin)
        if url.startswith("https://cdn.tailwindcss.com") and tailwind is not None:
            js = "(() => { const s = document.createElement('style'); s.textContent = %s; document.head.appendChild(s); })();" % json.dumps(tailwind)
            return route.fulfill(status=200, body=js, content_type="application/javascript")
        if "/@supabase/supabase-js" in url:
            return route.fulfill(status=200, body=SUPABASE_FAUX, content_type="application/javascript")
        if "mirrors.creativecommons.org" in url:
            return route.fulfill(status=200, body=SVG_VIDE, content_type="image/svg+xml")
        compter(url.split("/")[2] if "//" in url else url[:30])
        return route.abort()

    contexte.route("**/*", router)
