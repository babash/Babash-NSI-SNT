#!/usr/bin/env python3
"""Tests de .github/verifier-site.py : pages et fichiers cités par les fiches (N59), nouveaux essais
d'une page vue vide (N15).

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_verifier_site.py [--racine DOSSIER_DU_DEPOT] [--travail DOSSIER] [--garder]

Deux parties :
  - des cas unitaires, sur les fonctions du script (sans Chrome) : documents_des_fiches() sur des fiches
    fabriquées (ancre retirée, fiche illisible signalée), est_page(), afficher_page_deposee() avec un
    affichage simulé (vide puis rempli : 2 essais ; toujours vide : 3 essais, longueurs relevées),
    demander() sur un petit serveur local (200, 404) ;
  - le contrôle complet, sur des copies du dépôt servies en local et affichées dans Chrome. Pour rester
    court, chaque copie ne garde que la rubrique pp dans reglages.js, et ses fiches sont remplacées par
    des fiches fabriquées qui citent des fichiers déposés dans pp/fichiers/essai-t35/ :
      * tout est en place : code 0, « 2 pages citées par les fiches », compte des ressources inchangé ;
      * une page sans lien « Code source sur GitHub » : code 0, avertissement nommant la page ;
      * une page vide : code 1, déclarée après 3 essais, avec la longueur du texte rendu ;
      * un document absent du dépôt, un fichier qui ne répond pas en ligne : code 1, messages clairs ;
      * une séquence publiée (T153) : la rubrique NSI Terminale gardée, réduite à une fiche fabriquée, est comptée dans
        sa vue « Par thème » (?vue=themes ; sans ce paramètre, la vue « Par séquence » s'ouvrirait et ne compterait
        rien), et la page de la séquence affiche « ok 1 / 1 ressources » : code 0 ;
      * une séquence publiée mais absente de la bibliothèque construite : écart, code 1, message clair.
    Les séquences du dépôt sont retirées de chaque copie : elles citent des fiches que la copie n'a plus.
Il faut Chrome (google-chrome ou chromium). Compter une à deux minutes.
Code de retour : 0 si tous les cas passent, 1 sinon.
"""
import argparse
import contextlib
import functools
import http.server
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEFAUT = os.path.dirname(os.path.dirname(ICI))
D = "https://github.com/babash/Babash-NSI-SNT"
PAGE = ("<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\"><title>Essai</title></head><body>"
        "<main><h1>Page d'essai</h1><p>" + "Un vrai contenu, assez long pour être vu comme une page. " * 3 +
        "</p></main><footer>{pied}</footer></body></html>")
PIED = f'<a href="{D}">Code source sur GitHub</a>'

echecs = []


def verifier(titre, problemes, detail=""):
    print(("ok     " if not problemes else "ÉCHEC  ") + titre)
    for p in problemes:
        print("         -", p)
    if problemes and detail:
        print("         " + detail.replace("\n", "\n         "))
    if problemes:
        echecs.append(titre)


@contextlib.contextmanager
def servir(dossier):
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    gestion = functools.partial(Silencieux, directory=dossier)
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur.server_address[1]}"
    finally:
        serveur.shutdown()


def charger(racine):
    spec = importlib.util.spec_from_file_location("verifier_site", os.path.join(racine, ".github", "verifier-site.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)


def unitaires(racine, travail):
    v = charger(racine)
    v.ATTENTE = 0
    d = os.path.join(travail, "unitaires")
    ecrire(os.path.join(d, "donnees", "ressources", "a.json"), json.dumps({"id": "a", "documents": [
        {"fichier": "pp/fichiers/x.html#prof", "visible": {"exterieur": False, "eleve": False}},
        {"url": "https://example.org/"}, {"fichier": "pp/fichiers/y.pdf"}]}))
    ecrire(os.path.join(d, "donnees", "ressources", "b.json"), json.dumps({"id": "b", "documents": [
        {"fichier": "pp/fichiers/x.html"}]}))
    ecrire(os.path.join(d, "donnees", "ressources", "casse.json"), "{ pas du json")
    os.makedirs(os.path.join(d, "pp", "fichiers", "dossier"))
    v.RACINE = d
    problemes = []
    cites = v.documents_des_fiches(problemes)
    attendu = {"pp/fichiers/x.html": ["a", "b"], "pp/fichiers/y.pdf": ["a"]}
    verifier("documents_des_fiches : ancre retirée, documents cachés compris, adresses externes ignorées",
             [] if cites == attendu else [f"{cites!r} au lieu de {attendu!r}"])
    verifier("documents_des_fiches : une fiche illisible est signalée",
             [] if len(problemes) == 1 and "casse.json : fiche illisible" in problemes[0] else [repr(problemes)])
    verifier("est_page : .html, dossier (avec ou sans /), pas un PDF",
             [] if (v.est_page("a/b.html") and v.est_page("pp/fichiers/dossier") and v.est_page("x/")
                    and not v.est_page("a/b.pdf")) else ["résultat inattendu"])

    plein = PAGE.format(pied=PIED)
    suite = iter(["", "<html><body>404</body></html>", plein])
    v.afficher = lambda url: next(suite)
    page, essais, longueurs = v.afficher_page_deposee("http://x/")
    verifier("afficher_page_deposee : vide, vide, puis remplie : 3 essais, la page retenue",
             [] if essais == 3 and page == plein and longueurs[:2] == [0, 3] and longueurs[2] > 80
             else [f"{essais} essais, longueurs {longueurs}"])
    suite2 = iter(["", plein])
    v.afficher = lambda url: next(suite2)
    _, essais, _ = v.afficher_page_deposee("http://x/")
    verifier("afficher_page_deposee : vide puis remplie : 2 essais", [] if essais == 2 else [f"{essais} essais"])
    appels = []
    v.afficher = lambda url: appels.append(url) or "<html><body>rien</body></html>"
    _, essais, longueurs = v.afficher_page_deposee("http://x/")
    verifier("afficher_page_deposee : toujours vide : 3 essais, pas plus",
             [] if essais == 3 and len(appels) == 3 and longueurs == [4, 4, 4] else [f"{essais} essais, {longueurs}"])
    verifier("page_vide : titre 404 avec du texte", [] if v.page_vide(
        "<html><head><title>404 Not Found</title></head><body>" + "x " * 100 + "</body></html>") else ["non vue vide"])

    ecrire(os.path.join(d, "f.txt"), "bonjour")
    with servir(d) as base:
        verifier("demander : fichier présent, code 200", [] if v.demander(base + "/f.txt") == 200 else ["pas 200"])
        verifier("demander : fichier absent, code 404", [] if v.demander(base + "/absent.txt") == 404 else ["pas 404"])
        verifier("adresse : espaces et accents encodés",
                 [] if v.adresse(base, "a b/é.pdf") == base + "/a%20b/%C3%A9.pdf" else [v.adresse(base, "a b/é.pdf")])


def copie(racine, travail, nom, fiches, fichiers, absents=(), terminale=None, sequences=(), sequences_apres=()):
    """Une copie du dépôt réduite à la rubrique pp de la vitrine (ses fiches gardées), plus des fiches fabriquées
    qui citent les fichiers donnés ; la bibliothèque y est construite (le site la lit depuis T51b). Les fiches
    de « absents » citent un fichier qui manque : elles sont ajoutées après la construction, qui les refuserait.
    Les séquences du dépôt (donnees/sequences/) sont retirées : elles citent des fiches que la copie n'a plus (T153).
    terminale : une liste de fiches fabriquées à placer dans la rubrique nsi-terminale, gardée avec ses sections
    vidées ; sequences : des séquences à écrire avant la construction ; sequences_apres : après (absentes de la
    bibliothèque construite)."""
    d = os.path.join(travail, nom)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(racine, d, ignore=shutil.ignore_patterns(".git", ".claude", "bibliotheque*.json"))
    vitrine = json.load(open(os.path.join(d, "donnees", "vitrine.json"), encoding="utf-8"))
    vitrine["rubriques"] = [r for r in vitrine["rubriques"] if r["id"] == "pp" or (terminale is not None and r["id"] == "nsi-terminale")]
    vitrine["a_la_une"] = []
    garder = {i for s in vitrine["rubriques"][0]["sections"] for i in s["ressources"] + [x for ss in s.get("sous_sections", []) for x in ss["ressources"]]}
    for rub in vitrine["rubriques"][1:]:   # nsi-terminale : sections vidées, les fiches fabriquées dans la première
        for s in rub["sections"]:
            s["ressources"] = []
            for ss in s.get("sous_sections", []):
                ss["ressources"] = []
        rub["sections"][0]["ressources"] = list(terminale)
    ecrire(os.path.join(d, "donnees", "vitrine.json"), json.dumps(vitrine, ensure_ascii=False, indent=2) + "\n")
    exemple = os.path.join(d, "donnees", "vitrine.exemple.json")   # il cite des fiches retirées de la copie
    if os.path.exists(exemple):
        os.remove(exemple)
    shutil.rmtree(os.path.join(d, "donnees", "sequences"), ignore_errors=True)   # idem (T153)

    def ecrire_sequences(liste):
        for s in liste:
            ecrire(os.path.join(d, "donnees", "sequences", s["id"] + ".json"), json.dumps(s, ensure_ascii=False, indent=2) + "\n")
    ecrire_sequences(sequences)
    dossier = os.path.join(d, "donnees", "ressources")
    modele = json.load(open(os.path.join(dossier, sorted(garder)[0] + ".json"), encoding="utf-8"))
    for n in os.listdir(dossier):
        if n[:-5] not in garder:
            os.remove(os.path.join(dossier, n))
    for chemin, contenu in fichiers.items():
        ecrire(os.path.join(d, chemin), contenu)

    def fabriquer(ident, docs):
        f = {k: v for k, v in modele.items() if k not in ("liees", "notions", "notes")}
        f.update(id=ident, titre="Essai " + ident, documents=[
            dict({"role": "complement", "fichier": x, "visible": {"exterieur": True, "eleve": True}}, **({"principal": True} if k == 0 else {}))
            for k, x in enumerate(docs)])
        ecrire(os.path.join(dossier, ident + ".json"), json.dumps(f, ensure_ascii=False, indent=2) + "\n")

    for ident, docs in fiches.items():
        if ident not in absents:
            fabriquer(ident, docs)
    r = subprocess.run([sys.executable, "-B", os.path.join(racine, "scripts", "construire_bibliotheque.py"), "--racine", d, "--sans-textes"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("construction de la bibliothèque impossible :\n" + r.stdout[-2000:])
    for ident in absents:
        fabriquer(ident, fiches[ident])
    ecrire_sequences(sequences_apres)
    return d


def sequence_essai(ident, fiche):
    """Une séquence publiée de terminale qui cite une fiche fabriquée (d'origine institutionnelle, comme la fiche
    modèle de la rubrique pp : elle va donc dans « complements »)."""
    return {"id": ident, "niveau": "terminale", "enseignement": "nsi", "titre": "Essai : piles et files",
            "objectif": "Une séquence d'essai pour le contrôle en ligne.", "rang": 10,
            "programme": ["nsi-tle-2019.structures-de-donnees.listes-piles-files"], "statut": "publiee",
            "etapes": [{"type": "td", "ressources": [], "complements": [fiche]}]}


def complet(racine, travail):
    pp = "pp/fichiers/essai-t35/"
    base_fichiers = {pp + "page.html": PAGE.format(pied=PIED), pp + "dossier/index.html": PAGE.format(pied=PIED),
                     pp + "notes.pdf": "%PDF-1.4 essai", pp + "carnet.ipynb": "{}"}
    fiches = {"essai-a": [pp + "page.html#ancre", pp + "notes.pdf"], "essai-b": [pp + "dossier", pp + "carnet.ipynb"]}
    cas = [
        ("tout est en place : code 0, 2 pages citées par les fiches, ressources inchangées", "tel-quel",
         fiches, {}, None, 0,
         [r"^pp\s+2 ressources affichées /   2 dans la vitrine   ok$", r"^Total : 2 ressources$",
          r"2 pages citées par les fiches ; 2 à afficher",
          r"^Pages citées par les fiches : 2 / 2 s'affichent$",
          r"^Lien « Code source sur GitHub » : 2 / 2 pages citées par les fiches$",
          r"^Fichiers déposés \(PDF, notebooks, code…\) : 2 / 2 répondent en ligne$",
          r"^   ok\s+\d+ caractères   pp/fichiers/essai-t35/dossier/$", r"Tout s'affiche correctement"], []),
        ("page sans lien « Code source sur GitHub » : code 0, avertissement", "sans-lien",
         fiches, {pp + "page.html": PAGE.format(pied="Babash")}, None, 0,
         [r"^Lien « Code source sur GitHub » : 1 / 2 pages citées par les fiches$",
          r"^   - pp/fichiers/essai-t35/page\.html$", r"Tout s'affiche correctement"], []),
        ("page vide : code 1, déclarée après 3 essais, longueur du texte rendu", "page-vide",
         fiches, {pp + "page.html": "<!doctype html><html><body><p>Presque rien</p></body></html>"}, None, 1,
         [r"^   VIDE\s+12 caractères, 3 essais \(12 puis 12 puis 12\)   pp/fichiers/essai-t35/page\.html$",
          r"^ - pp/fichiers/essai-t35/page\.html : page vide ou introuvable après 3 essais \(texte rendu : 12 caractères\)$",
          r"^Pages citées par les fiches : 1 / 2 s'affichent$"], []),
        ("document absent du dépôt, fichier qui ne répond pas : code 1", "absents",
         dict(fiches, **{"essai-c": [pp + "manque.pdf"]}), {}, pp + "carnet.ipynb", 1,
         [r"^ - pp/fichiers/essai-t35/manque\.pdf : cité par la fiche essai-c, mais absent du dépôt$",
          r"^ - pp/fichiers/essai-t35/carnet\.ipynb : cité par la fiche essai-b, ne répond pas en ligne \(code 404\)$",
          r"^Fichiers déposés \(PDF, notebooks, code…\) : 1 / 2 répondent en ligne$"], ["essai-c"]),
    ]
    # T153 : les séquences publiées et la vue « Par thème » des rubriques
    seq = {"terminale": ["essai-a"], "sequences": [sequence_essai("tle-essai", "essai-a")]}
    cas += [
        ("une séquence publiée : rubrique comptée dans sa vue par thème, page de la séquence ok : code 0", "sequence",
         fiches, {}, None, 0,
         [r"^nsi-terminale\s+1 ressources affichées /   1 dans la vitrine   ok$",
          r"^Séquences publiées : 1$", r"^   ok\s+1 /   1 ressources   nsi-terminale/\?sequence=tle-essai$",
          r"Tout s'affiche correctement"], [], seq),
        ("une séquence publiée mais absente de la bibliothèque construite : écart, code 1", "sequence-absente",
         fiches, {}, None, 1,
         [r"^   ÉCART\s+0 /   1 ressources   nsi-terminale/\?sequence=tle-essai$",
          r"^ - nsi-terminale/\?sequence=tle-essai : 0 ressources affichées au lieu de 1$"], [],
         {"terminale": ["essai-a"], "sequences_apres": [sequence_essai("tle-essai", "essai-a")]}),
    ]
    for c in cas:
        titre, nom, fiches_cas, remplace, cache, code_attendu, motifs, absents = c[:8]
        options = c[8] if len(c) > 8 else {}
        d = copie(racine, travail, nom, fiches_cas, dict(base_fichiers, **remplace), absents, **options)
        servi = d
        if cache:   # le fichier existe dans le dépôt mais pas en ligne : on sert une copie sans lui
            servi = d + "-en-ligne"
            shutil.copytree(d, servi, symlinks=True)
            os.remove(os.path.join(servi, cache))
        env = dict(os.environ, VERIFIER_ATTENTE="1")
        env.pop("GITHUB_ACTIONS", None)
        with servir(servi) as base:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.join(d, ".github", "verifier-site.py"), base],
                               capture_output=True, text=True, timeout=900, env=env)
        sortie = r.stdout + r.stderr
        pb = [] if r.returncode == code_attendu else [f"code {r.returncode} au lieu de {code_attendu}"]
        pb += [f"absent de la sortie : « {m} »" for m in motifs if not re.search(m, sortie, re.M)]
        verifier("contrôle complet, " + titre, pb, sortie[-2500:] if pb else "")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--racine", default=RACINE_DEFAUT)
    p.add_argument("--travail")
    p.add_argument("--garder", action="store_true")
    p.add_argument("--sans-chrome", action="store_true", help="les cas unitaires seulement")
    a = p.parse_args()
    travail = a.travail or tempfile.mkdtemp(prefix="test-verifier-site-")
    os.makedirs(travail, exist_ok=True)
    try:
        unitaires(a.racine, travail)
        if not a.sans_chrome:
            complet(a.racine, travail)
    finally:
        if not a.garder:
            shutil.rmtree(travail, ignore_errors=True)
    print(f"\n{len(echecs)} échec(s)." if echecs else "\nTous les cas passent.")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
