"""Le cadre commun des tests du Gardien (aucun cas ici).

- arguments(doc, site)          : lit COPIE_DU_SITE (si site) et DOSSIER_DE_TRAVAIL ; --help affiche doc
- Bilan                         : compte les cas, affiche « ok » ou « ÉCHEC », puis « N cas, M échec(s) »
- copie(source, travail, nom)   : copie fraîche du site, sans .git, pour un cas
- exporter(depot, ref, dossier) : extrait une version du dépôt (git archive)
- json_modifie(chemin, f)       : lit un fichier JSON, lui applique f, puis le réécrit
- valider(dossier, strict)      : lance scripts/valider_donnees.py de la copie -> (code, sortie)
- niveau(sortie, nom)           : les lignes ERREUR, ATTENTION ou INFO de cette sortie
- servir(dossier)               : sert un dossier en HTTP local, le temps d'un bloc « with »
- FAUX_ACCES, FAUX_CLE          : valeurs fictives (voir plus bas)
"""
import argparse
import contextlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time

# Valeurs fictives, pour vérifier que la validation refuse ce qui ressemble à un identifiant ou à
# une clé. Elles sont assemblées à l'exécution : le dépôt est public, et aucun texte qui ressemble à
# une donnée sensible ne doit y figurer, même inventé (sensibles.py et les robots qui cherchent les
# clés publiées ne font pas la différence). Elles n'existent que dans les copies du dossier de travail.
FAUX_ACCES = " " + " ".join(["Identifiant", ":", "valeur-fictive,", "mot", "de", "passe", ":", "valeur-fictive."])
FAUX_CLE = "clé " + "service" + "_role : " + "sb_" + "secret_" + "x" * 32


def arguments(doc, site=True):
    a = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    if site:
        a.add_argument("site", help="une copie extraite du site (git archive), qui n'est jamais modifiée")
    a.add_argument("travail", help="dossier de travail : les copies modifiées y sont créées, puis effacées")
    o = a.parse_args()
    os.makedirs(o.travail, exist_ok=True)
    return (os.path.abspath(o.site), os.path.abspath(o.travail)) if site else os.path.abspath(o.travail)


class Bilan:
    def __init__(self):
        self.cas = 0
        self.echecs = 0

    def verifier(self, titre, problemes, detail=""):
        """Un cas : réussi si la liste des problèmes est vide."""
        self.cas += 1
        if problemes:
            self.echecs += 1
            print("  ÉCHEC " + titre + " : " + " ; ".join(problemes))
            if detail:
                print("\n".join("        " + l for l in detail.rstrip().splitlines()))
        else:
            print("  ok    " + titre)

    def terminer(self):
        print("\n%d cas, %d échec(s)" % (self.cas, self.echecs))
        sys.exit(1 if self.echecs else 0)


def copie(source, travail, nom="cas"):
    d = os.path.join(travail, nom)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(source, d, ignore=shutil.ignore_patterns(".git"))
    return d


def exporter(depot, ref, dossier):
    os.makedirs(dossier, exist_ok=True)
    archive = subprocess.run(["git", "archive", ref], cwd=depot, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", dossier], input=archive, check=True)


def json_modifie(chemin, f):
    if not os.path.exists(chemin):
        raise SystemExit("fichier introuvable dans la copie : " + chemin)
    with open(chemin, encoding="utf-8") as h:
        donnees = json.load(h)
    f(donnees)
    with open(chemin, "w", encoding="utf-8") as h:
        json.dump(donnees, h, ensure_ascii=False, indent=2)


def valider(dossier, strict=False):
    args = [sys.executable, "-I", "-B", os.path.join(dossier, "scripts", "valider_donnees.py"), "--racine", dossier]
    r = subprocess.run(args + (["--strict"] if strict else []), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def niveau(sortie, nom):
    return [l for l in sortie.splitlines() if l.startswith(nom)]


@contextlib.contextmanager
def servir(dossier):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    srv = subprocess.Popen([sys.executable, "-I", "-m", "http.server", str(port), "--bind", "127.0.0.1",
                            "--directory", dossier], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        yield "http://127.0.0.1:%d" % port
    finally:
        srv.terminate()
        srv.wait()
