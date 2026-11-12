#!/usr/bin/env python3
"""Rassemble les fiches de la bibliothèque en fichiers que les pages lisent en un seul chargement.

Les fiches (donnees/ressources/<id>.json), la vitrine et les référentiels restent la seule source : ces fichiers
en sont tirés à chaque publication, par le workflow « Publier le site » (.github/workflows/publier.yml), et ne
sont jamais commités (.gitignore). Un enregistrement de l'admin (une fiche modifiée) suffit donc à mettre le site
à jour, sans fichier commun que deux modifications se disputeraient.

Fichiers produits, dans donnees/ (ou --sortie) :
  bibliotheque.json           la vue de l'extérieur (cahier des charges, § 3.2) : les ressources qui ont au moins
                              un document visible de l'extérieur, avec ces documents seulement ; le document principal
                              caché est remplacé par le premier visible ; ni notes, ni liens vers une ressource cachée.
                              Avec les référentiels (valeurs, programmes, notions, compétences Pix) et la vitrine.
  bibliotheque-complete.json  tout, documents cachés et notes compris, avec ce que voit chaque public : pour l'admin.
  bibliotheque-textes.json    le texte des documents hébergés sur le site et visibles de l'extérieur (pages HTML,
                              textes, PDF si pdftotext est installé), pour la recherche dans le contenu ; chargé à part.

La construction commence par la validation complète (scripts/valider_donnees.py) : une seule erreur l'arrête,
et rien n'est écrit. Python 3 standard ; pdftotext (paquet poppler-utils) pour le texte des PDF, facultatif.

Usage :
  python3 scripts/construire_bibliotheque.py                    construit dans donnees/
  python3 scripts/construire_bibliotheque.py --sortie DOSSIER   ailleurs
  python3 scripts/construire_bibliotheque.py --racine DOSSIER   à partir d'une autre copie du dépôt
  python3 scripts/construire_bibliotheque.py --sans-textes      sans bibliotheque-textes.json
  python3 scripts/construire_bibliotheque.py --github           dans GitHub Actions : résumé du run
Code de retour : 0 si les fichiers sont écrits, 1 sinon.
"""
import argparse
import datetime
import html.parser
import json
import os
import re
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import valider_donnees as vd  # noqa: E402

FORMAT = 1
MAX_TEXTE = 60000           # caractères gardés par document pour la recherche dans le contenu
LISIBLES = {"html", "htm", "txt", "md", "pdf"}


# ── Le texte d'une page HTML ────────────────────────────────────────────────

class TexteHTML(html.parser.HTMLParser):
    """Le texte lisible d'une page : sans scripts, styles, SVG ni éléments cachés aux lecteurs (aria-hidden)."""
    IGNORES = {"script", "style", "noscript", "svg", "template", "head", "math", "canvas"}
    BLOCS = {"p", "div", "li", "td", "th", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article",
             "pre", "blockquote", "dt", "dd", "figcaption", "summary", "details", "table", "ul", "ol", "header", "footer"}
    VIDES = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "area", "base", "col", "embed", "param", "track"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.morceaux = []
        self.ignore = 0
        self.pile = []
        self.titre = ""
        self.dans_titre = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.dans_titre = True
        if tag in self.VIDES:
            if tag == "br":
                self.morceaux.append("\n")
            return
        cacher = tag in self.IGNORES or dict(attrs).get("aria-hidden") == "true" or "hidden" in dict(attrs)
        self.pile.append(cacher)
        if cacher:
            self.ignore += 1
        if tag in self.BLOCS:
            self.morceaux.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self.dans_titre = False
        if tag in self.VIDES or not self.pile:
            return
        if self.pile.pop():
            self.ignore -= 1
        if tag in self.BLOCS:
            self.morceaux.append("\n")

    def handle_data(self, data):
        if self.dans_titre:
            self.titre += data
        elif not self.ignore:
            self.morceaux.append(data)

    def texte(self):
        t = "".join(self.morceaux)
        t = re.sub(r"[^\S\n]+", " ", t)  # tout blanc sauf le retour à la ligne, espace insécable comprise
        return re.sub(r"\s*\n\s*", "\n", t).strip()


def texte_html(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as f:
        p = TexteHTML()
        p.feed(f.read())
        p.close()
    return p.texte()


def texte_pdf(chemin):
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-q", chemin, "-"], capture_output=True, timeout=60)
    if r.returncode != 0:
        raise OSError(r.stderr.decode("utf-8", "replace").strip() or f"pdftotext : code {r.returncode}")
    t = r.stdout.decode("utf-8", "replace")
    t = re.sub(r"[^\S\n]+", " ", t)
    return re.sub(r"\s*\n\s*", "\n", t).strip()


# ── La construction ─────────────────────────────────────────────────────────

class Construction:
    def __init__(self, racine):
        self.racine = os.path.abspath(racine)
        self.v = vd.Validation(self.racine)
        self.messages = []

    def valider(self):
        self.v.lancer()
        erreurs = self.v.rapport.triees("erreur")
        for _, fichier, champ, message in erreurs:
            self.messages.append(f"ERREUR  {fichier}{' › ' + champ if champ else ''} : {message}")
        return not erreurs

    def lire(self, *chemin):
        with open(os.path.join(self.racine, "donnees", *chemin), encoding="utf-8") as f:
            return json.load(f)

    def commit(self):
        sha = os.environ.get("GITHUB_SHA")
        if sha:
            return sha
        try:
            r = subprocess.run(["git", "-C", self.racine, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
            return r.stdout.strip() or None if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None

    def referentiels(self):
        valeurs = self.lire("referentiels", "valeurs.json")
        programmes = self.lire("referentiels", "programmes.json")
        notions = self.lire("referentiels", "notions.json")
        pix = self.lire("referentiels", "competences-pix.json")
        return {
            "valeurs": {k: valeurs[k] for k in vd.LISTES},
            "programmes": programmes["programmes"],
            "notions": {k: notions[k] for k in ("version", "domaines", "referentiels_externes", "sources", "notions")},
            "competences_pix": {"domaines": pix.get("domaines", []), "competences": pix.get("competences", [])},
        }

    def document(self, d, public=None):
        """Un document, avec son format déduit ; pour un public, sans ses réglages de visibilité."""
        doc = {k: v for k, v in d.items() if k != "visible" or public is None}
        doc["format"] = d.get("format") or self.v.deduire_format(d)
        return doc

    def vue(self, fiche, public):
        """La fiche telle que la voit un public (« exterieur » ou « eleve »), ou None si elle lui est cachée."""
        docs = [d for d in fiche["documents"] if d.get("visible", {}).get(public) is True]
        if not docs:
            return None
        f = {k: v for k, v in fiche.items() if k not in ("$schema", "notes", "documents")}
        principal = next((i for i, d in enumerate(docs) if d.get("principal") is True), 0)
        f["documents"] = []
        for i, d in enumerate(docs):
            doc = self.document(d, public)
            doc["principal"] = i == principal
            f["documents"].append(doc)
        return f

    def complete(self, fiche):
        f = {k: v for k, v in fiche.items() if k not in ("$schema", "documents")}
        f["documents"] = [self.document(d) for d in fiche["documents"]]
        f["visibilite"] = dict(self.v.visibles.get(fiche["id"], {}))
        return f

    def construire(self, sortie, textes=True, maintenant=None):
        maintenant = maintenant or datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        construit = {"date": maintenant.isoformat().replace("+00:00", "Z"), "commit": self.commit()}
        refs = self.referentiels()
        chemin_vitrine = os.path.join(self.racine, "donnees", "vitrine.json")
        vitrine = self.lire("vitrine.json") if os.path.exists(chemin_vitrine) else None
        if isinstance(vitrine, dict):
            vitrine.pop("$schema", None)
        fiches = [self.v.fiches[rid][1] for rid in sorted(self.v.fiches)]

        publiques = [f for f in (self.vue(x, "exterieur") for x in fiches) if f]
        visibles = {f["id"] for f in publiques}
        for f in publiques:
            if f.get("liees"):
                f["liees"] = [l for l in f["liees"] if l.get("ressource") in visibles]
        bib = {"format": FORMAT, "public": "exterieur", "construit": construit, "referentiels": refs,
               "vitrine": vitrine, "ressources": publiques}
        tout = {"format": FORMAT, "public": "admin", "construit": construit, "referentiels": refs,
                "vitrine": vitrine, "ressources": [self.complete(x) for x in fiches]}

        os.makedirs(sortie, exist_ok=True)
        ecrits = {"bibliotheque.json": bib, "bibliotheque-complete.json": tout}
        if textes:
            ecrits["bibliotheque-textes.json"] = self.textes(publiques, construit)
        for nom, contenu in ecrits.items():
            chemin = os.path.join(sortie, nom)
            provisoire = chemin + ".provisoire"
            with open(provisoire, "w", encoding="utf-8") as f:
                json.dump(contenu, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")
            os.replace(provisoire, chemin)  # jamais de fichier à moitié écrit
            self.messages.append(f"écrit   {os.path.relpath(chemin, self.racine) if chemin.startswith(self.racine) else chemin} "
                                 f"({os.path.getsize(chemin) // 1024} Ko)")
        self.messages.append(f"bilan   {len(publiques)} ressources visibles de l'extérieur sur {len(fiches)} ; "
                             f"{sum(len(f['documents']) for f in publiques)} documents publics")
        return True

    def textes(self, publiques, construit):
        pdf = shutil.which("pdftotext") is not None
        docs, ignores = [], []
        for f in publiques:
            for i, d in enumerate(f["documents"]):
                fich = d.get("fichier")
                if not fich:
                    continue
                chemin = re.split(r"[#?]", fich)[0]
                complet = os.path.join(self.racine, *[p for p in chemin.split("/") if p])
                if chemin.endswith("/") or os.path.isdir(complet):
                    complet = os.path.join(complet, "index.html")
                ext = complet.rsplit(".", 1)[-1].lower() if "." in os.path.basename(complet) else ""
                if ext not in LISIBLES:
                    ignores.append(f"{fich} (format .{ext} non lu)")
                    continue
                if ext == "pdf" and not pdf:
                    ignores.append(f"{fich} (pdftotext absent)")
                    continue
                try:
                    if ext in ("html", "htm"):
                        t = texte_html(complet)
                    elif ext == "pdf":
                        t = texte_pdf(complet)
                    else:
                        with open(complet, encoding="utf-8", errors="replace") as g:
                            t = g.read()
                except (OSError, subprocess.SubprocessError, ValueError) as e:
                    ignores.append(f"{fich} (lecture impossible : {e})")
                    continue
                t = t.strip()
                if not t:
                    ignores.append(f"{fich} (aucun texte)")
                    continue
                docs.append({"ressource": f["id"], "document": i, "texte": t[:MAX_TEXTE]})
        for x in ignores:
            self.messages.append(f"info    texte non indexé : {x}")
        self.messages.append(f"textes  {len(docs)} documents hébergés indexés" + ("" if pdf else " (PDF non lus : pdftotext absent)"))
        return {"format": FORMAT, "construit": construit, "documents": docs}


def main():
    p = argparse.ArgumentParser(description="Rassemble les fiches de la bibliothèque (donnees/) en fichiers pour les pages.")
    p.add_argument("--racine", default=vd.RACINE_DEFAUT, help="racine du dépôt (par défaut : ce dépôt)")
    p.add_argument("--sortie", help="dossier où écrire les fichiers (par défaut : donnees/ de la racine)")
    p.add_argument("--sans-textes", action="store_true", help="ne pas construire bibliotheque-textes.json")
    p.add_argument("--github", action="store_true", help="dans GitHub Actions : résumé du run")
    args = p.parse_args()

    c = Construction(args.racine)
    ok = c.valider()
    if ok:
        c.construire(args.sortie or os.path.join(c.racine, "donnees"), textes=not args.sans_textes)
    else:
        c.messages.append("arrêt   les données ont des erreurs : rien n'est écrit (python3 scripts/valider_donnees.py pour le détail)")
    for m in c.messages:
        print(m)
    if args.github and os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("## Construction de la bibliothèque\n\n" + "\n".join(f"- {vd.cellule(m)}" for m in c.messages) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
