#!/usr/bin/env python3
"""Pré-validation d'une branche par le Gardien : tous les contrôles automatiques, d'un coup.

Usage (depuis n'importe quel dossier du dépôt) :
  python3 -I .github/gardien/controler.py --branche origin/archi/t02-format-donnees
          [--base origin/main] [--travail DOSSIER] [--polices DOSSIER] [--sans-fetch]

Étapes :
  0. git fetch de toutes les branches (refspec explicite : `git fetch origin` seul ne met
     pas origin/main à jour dans les copies de travail des agents) ;
  1. la branche part-elle du dernier main ? (sinon : à rebaser) ; fichiers touchés ;
  2. données sensibles dans les lignes ajoutées (sensibles.py --diff) ;
  3. liens internes, liens principaux vers GitHub (liens.py) sur la branche ;
  4. rendu avant/après : accueil + rubriques, 320/768/1440 px, clair/obscur (rendu.py, comparer.py) ;
  5. contrastes et clavier sur la branche (contrastes.py) ;
  6. impression A4 des documents HTML touchés dans */fichiers/ (impression.py) ;
  7. contrôle du dépôt lui-même (.github/verifier-site.py) sur la branche servie en local.
Les polices Google, bloquées dans les sessions, sont servies depuis des paquets fontsource
(téléchargés au besoin depuis npm dans --polices).
Résumé à la fin. Code de sortie : 0 tout est vert ; 1 un contrôle est rouge ;
2 seulement des motifs « à relire » (données sensibles : relecture humaine des occurrences).
"""
import argparse
import glob
import os
import socket
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, "-I"]
POLICES = {"chakra-petch": "5.3.0", "atkinson-hyperlegible": "5.3.0", "jetbrains-mono": "5.3.0"}


def git(depot, *args, **kw):
    return subprocess.run(["git", *args], cwd=depot, capture_output=True, text=True, **kw)


def port_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def exporter(depot, ref, dossier):
    os.makedirs(dossier, exist_ok=True)
    archive = subprocess.run(["git", "archive", ref], cwd=depot, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", dossier], input=archive, check=True)


def servir(dossier):
    port = port_libre()
    proc = subprocess.Popen([*PY, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", dossier],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    return proc, "http://127.0.0.1:%d" % port


def preparer_polices(dossier):
    os.makedirs(dossier, exist_ok=True)
    for nom, version in POLICES.items():
        cible = os.path.join(dossier, "fontsource-%s-%s" % (nom, version))
        if glob.glob(os.path.join(dossier, "fontsource-%s-*" % nom, "files")):
            continue
        os.makedirs(cible, exist_ok=True)
        r = subprocess.run(["npm", "pack", "@fontsource/%s@%s" % (nom, version), "--silent", "--pack-destination", dossier],
                           capture_output=True, text=True)
        tgz = os.path.join(dossier, r.stdout.strip().splitlines()[-1]) if r.returncode == 0 and r.stdout.strip() else None
        if tgz and os.path.exists(tgz):
            subprocess.run(["tar", "-xzf", tgz, "-C", cible, "--strip-components=1"], check=False)
        else:
            print("   (polices %s indisponibles : rendu avec des polices de remplacement)" % nom)


def etape(titre, cmd, resultats, cle, si_echec="ROUGE"):
    """Lance un contrôle ; si_echec vaut « ROUGE » ou « à relire » (motifs à examiner par un humain)."""
    print("\n### %s\n$ %s" % (titre, " ".join(cmd[2:] if cmd[:2] == PY else cmd)), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    lignes = (r.stdout + r.stderr).strip().splitlines()
    print("\n".join(lignes[-25:]))
    resultats.append((cle, "vert" if r.returncode == 0 else si_echec))
    return r


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--branche", default="HEAD")
    a.add_argument("--base", default="origin/main")
    a.add_argument("--travail")
    a.add_argument("--polices", default=os.environ.get("GARDIEN_POLICES", os.path.expanduser("~/.cache/gardien-polices")))
    a.add_argument("--sans-fetch", action="store_true")
    o = a.parse_args()
    depot = git(ICI, "rev-parse", "--show-toplevel").stdout.strip()
    travail = o.travail or tempfile.mkdtemp(prefix="gardien-")
    resultats = []
    if not o.sans_fetch:
        git(depot, "fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*")
    base, tete = git(depot, "rev-parse", o.base).stdout.strip(), git(depot, "rev-parse", o.branche).stdout.strip()
    mb = git(depot, "merge-base", base, tete).stdout.strip()
    print("Branche %s (%s), base %s (%s)" % (o.branche, tete[:7], o.base, base[:7]))
    a_jour = mb == base
    print("Part du dernier %s : %s" % (o.base, "oui" if a_jour else "NON (base %s) : à rebaser" % mb[:7]))
    resultats.append(("branche à jour de la base", "vert" if a_jour else "ROUGE"))
    touches = git(depot, "diff", "--name-status", "%s...%s" % (base, tete)).stdout.strip()
    print("Fichiers touchés :\n" + (touches or "(aucun)"))

    av, ap = os.path.join(travail, "avant"), os.path.join(travail, "apres")
    exporter(depot, base, av)
    exporter(depot, tete, ap)
    preparer_polices(o.polices)
    srv_av, url_av = servir(av)
    srv_ap, url_ap = servir(ap)
    try:
        etape("Données sensibles (lignes ajoutées)", [*PY, os.path.join(ICI, "sensibles.py"), depot, "--diff", "%s..%s" % (base, tete)],
              resultats, "données sensibles", si_echec="à relire")
        etape("Liens", [*PY, os.path.join(ICI, "liens.py"), ap], resultats, "liens internes et GitHub")
        commun_args = ["--polices", o.polices]
        etape("Rendu avant", [*PY, os.path.join(ICI, "rendu.py"), url_av, os.path.join(travail, "rendu-avant"), "--racine", av, *commun_args], resultats, "rendu avant (référence)")
        etape("Rendu après", [*PY, os.path.join(ICI, "rendu.py"), url_ap, os.path.join(travail, "rendu-apres"), "--racine", ap, *commun_args], resultats, "rendu après")
        r = etape("Comparaison avant/après", [*PY, os.path.join(ICI, "comparer.py"), os.path.join(travail, "rendu-avant"), os.path.join(travail, "rendu-apres")], resultats, "avant/après identiques")
        if r.returncode:
            print("   (différences à examiner : bruit d'anticrénelage possible sur le logo à 320 px, ou changement voulu)")
        etape("Contrastes et clavier", [*PY, os.path.join(ICI, "contrastes.py"), url_ap, os.path.join(travail, "contrastes"), "--racine", ap, "--largeurs", "320,768,1440", *commun_args], resultats, "contrastes et clavier")
        docs = [l.split("\t")[-1] for l in touches.splitlines() if l[:1] in "AMR" and "/fichiers/" in l and l.endswith(".html")]
        if docs:
            etape("Impression A4 des documents touchés", [*PY, os.path.join(ICI, "impression.py"), url_ap, os.path.join(travail, "impression"), "--racine", ap, *commun_args, *docs], resultats, "impression A4")
        verif = os.path.join(ap, ".github", "verifier-site.py")
        if os.path.exists(verif):
            etape("Contrôle du dépôt (verifier-site.py)", [*PY, verif, url_ap], resultats, "verifier-site.py")
    finally:
        srv_av.terminate()
        srv_ap.terminate()
    print("\n=== Résumé (%s) ===" % travail)
    for cle, etat in resultats:
        print("  %-28s %s" % (cle, etat))
    print("Rappels non automatiques : conformité au cahier des charges et aux décisions, changement structurel ?,"
          " chiffres annoncés, README, puis après publication : attendre_actions.sh SHA.")
    etats = {etat for _, etat in resultats}
    sys.exit(1 if "ROUGE" in etats else 2 if "à relire" in etats else 0)


if __name__ == "__main__":
    main()
