#!/usr/bin/env python3
"""Attend que GitHub Pages ait réellement mis en ligne un commit, puis le vérifie.

Le site est publié par GitHub Pages (« Deploy from a branch »). Chaque mise en ligne est un
déploiement de l'environnement « github-pages », qui porte le commit (SHA) déployé et passe
par les états waiting, queued, in_progress, puis success (ou failure, error). Il devient
inactive quand un déploiement plus récent le remplace.

1. Attendre : le script interroge ces déploiements jusqu'à ce que le commit soit en ligne,
   sans se fier au contenu des fichiers. Un envoi qui ne change ni reglages.js ni les listes
   de ressources est donc attendu lui aussi (constat I1 du Gardien).
2. Comparer (--comparer) : une fois le déploiement terminé, les fichiers que le commit ajoute
   ou modifie, et que le site sert, sont téléchargés et comparés octet par octet à ceux du
   dépôt. C'est la preuve que la version en ligne est bien celle de ce commit.

Usage :
  python3 scripts/attendre_deploiement.py --sha <commit>   attendre ce commit
  python3 scripts/attendre_deploiement.py                  attendre le dernier commit de main
  python3 scripts/attendre_deploiement.py --comparer DOSSIER [--site URL]
      comparer au site en ligne les fichiers modifiés par le dernier commit de DOSSIER (une
      copie du dépôt avec au moins deux commits d'historique : fetch-depth 2)
Options : --depot babash/Babash-NSI-SNT  --delai 900 (secondes)  --pause 15 (secondes)

Résultat :
  - attente, code 0 : le commit est en ligne, ou un commit plus récent l'a remplacé (le contrôle
    de ce commit-là vérifiera le site) ; code 1 : le déploiement a échoué, le commit n'est pas
    sur main, ou le délai est dépassé. Dans GitHub Actions, écrit dans $GITHUB_OUTPUT :
    sha=<commit> et a_verifier=oui ou non ;
  - comparaison, code 0 : tous les fichiers comparés sont identiques en ligne ; code 1 : au moins
    un fichier diffère encore au bout de --delai-comparaison secondes.
Utilise la commande gh (préinstallée sur les machines de GitHub Actions, jeton dans GH_TOKEN).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EN_COURS = {"waiting", "queued", "pending", "in_progress"}
ECHECS = {"failure", "error"}
SITE = "https://babash.github.io/Babash-NSI-SNT"
MAX_FICHIERS = 40
MAX_OCTETS = 5_000_000


class ErreurApi(Exception):
    pass


def gh(chemin):
    try:
        r = subprocess.run(["gh", "api", chemin], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise ErreurApi(str(e))
    if r.returncode != 0:
        raise ErreurApi((r.stderr or r.stdout).strip())
    return json.loads(r.stdout or "null")


def heure():
    return time.strftime("%H:%M:%S", time.gmtime()) + " UTC"


def decider(etats, main_en_avance):
    """Que faire, d'après les états du déploiement du commit (le plus récent en premier).

    etats : liste des états, ou None s'il n'existe aucun déploiement pour ce commit.
    main_en_avance : True si main contient déjà des commits plus récents.
    Renvoie (decision, message), decision valant attendre, en_ligne, remplace ou echec.
    """
    if etats:
        dernier = etats[0]
        if dernier == "success":
            return "en_ligne", "le commit est en ligne"
        if dernier in ECHECS:
            return "echec", f"le déploiement de GitHub Pages a échoué (état « {dernier} »)"
        if dernier == "inactive":
            if "success" in etats:
                return "remplace", "le commit a été mis en ligne, puis remplacé par un commit plus récent"
            return "remplace", "un commit plus récent a été déployé à sa place"
        if dernier in EN_COURS:
            return "attendre", f"déploiement en cours (état « {dernier} »)"
        return "attendre", f"déploiement dans un état inattendu (« {dernier} »)"
    if main_en_avance:
        return "remplace", "aucun déploiement pour ce commit, et main a déjà avancé : le commit suivant le remplace"
    return "attendre", "le déploiement n'a pas encore commencé"


def ecrire_sorties(**valeurs):
    chemin = os.environ.get("GITHUB_OUTPUT")
    if chemin:
        with open(chemin, "a", encoding="utf-8") as f:
            for cle, val in valeurs.items():
                f.write(f"{cle}={val}\n")


def ecrire_resume(lignes):
    chemin = os.environ.get("GITHUB_STEP_SUMMARY")
    if chemin:
        with open(chemin, "a", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n\n")


# ── 1. Attendre le déploiement ──────────────────────────────────────────────

def attendre(a):
    depot, branche = a.depot, a.branche
    # Le SHA complet : l'API des déploiements ne reconnaît pas un SHA abrégé
    cible = a.sha or branche
    try:
        sha = gh(f"repos/{depot}/commits/{cible}")["sha"]
    except (ErreurApi, KeyError, TypeError) as e:
        print(f"::error::Le commit « {cible} » est introuvable dans {depot} : {e}")
        ecrire_sorties(a_verifier="non")
        return 1
    print(f"{heure()}  commit attendu : {sha[:7]} (dépôt {depot})")
    ecrire_sorties(sha=sha)
    journal = [f"## Mise en ligne du commit {sha[:7]}", "", "| Heure | État |", "|---|---|"]

    def noter(message):
        print(f"{heure()}  {message}")
        journal.append(f"| {heure()} | {message} |")

    fin = time.time() + a.delai
    dernier_message, pannes = None, 0
    while True:
        try:
            deploiements = gh(f"repos/{depot}/deployments?environment=github-pages&sha={sha}&per_page=5")
            etats = None
            if deploiements:
                statuts = gh(f"repos/{depot}/deployments/{deploiements[0]['id']}/statuses?per_page=50")
                etats = [s["state"] for s in statuts] or ["pending"]
            main_en_avance = False
            if not etats:
                try:
                    comparaison = gh(f"repos/{depot}/compare/{sha}...{branche}")
                except ErreurApi as e:
                    print(f"::error::Le commit {sha[:7]} est introuvable dans {depot} : {e}")
                    ecrire_sorties(a_verifier="non")
                    return 1
                statut = comparaison.get("status")
                if statut not in ("identical", "ahead"):
                    print(f"::error::Le commit {sha[:7]} n'est pas sur {branche} (comparaison : {statut}) : "
                          "GitHub Pages ne le déploiera pas.")
                    ecrire_sorties(a_verifier="non")
                    return 1
                main_en_avance = statut == "ahead"
            pannes = 0
        except ErreurApi as e:
            pannes += 1
            print(f"Réponse de GitHub impossible à lire ({pannes}e fois) : {e}")
            if pannes >= 5:
                print("::error::L'API de GitHub ne répond pas : impossible de savoir si le site est à jour.")
                ecrire_sorties(a_verifier="non")
                return 1
            time.sleep(a.pause)
            continue

        decision, message = decider(etats, main_en_avance)
        if message != dernier_message:
            noter(message)
            dernier_message = message
        if decision == "en_ligne":
            ecrire_resume(journal)
            ecrire_sorties(a_verifier="oui")
            return 0
        if decision == "remplace":
            print(f"::notice::Commit {sha[:7]} : {message}. Le site sera vérifié par le contrôle du commit plus récent.")
            ecrire_resume(journal)
            ecrire_sorties(a_verifier="non")
            return 0
        if decision == "echec":
            print(f"::error::Commit {sha[:7]} : {message}.")
            ecrire_resume(journal)
            ecrire_sorties(a_verifier="non")
            return 1
        if time.time() > fin:
            print(f"::error::Au bout de {a.delai // 60} minutes, GitHub Pages n'a toujours pas mis en ligne le commit {sha[:7]}.")
            ecrire_resume(journal)
            ecrire_sorties(a_verifier="non")
            return 1
        time.sleep(a.pause)


# ── 2. Comparer les fichiers modifiés avec la version en ligne ──────────────

def git(dossier, *args):
    r = subprocess.run(["git", "-C", dossier, *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise ErreurApi((r.stderr or r.stdout).strip())
    return r.stdout


def servi(chemin):
    """Un fichier que GitHub Pages sert : pas de dossier ou de fichier qui commence par un point."""
    return not any(p.startswith(".") for p in chemin.split("/"))


def fichiers_a_comparer(dossier):
    """Les fichiers ajoutés ou modifiés par le dernier commit (par rapport à son premier parent)."""
    sortie = git(dossier, "diff", "--name-only", "--no-renames", "--diff-filter=AM", "-z", "HEAD~1", "HEAD")
    choisis, ignores = [], []
    for chemin in (c for c in sortie.split("\0") if c):
        complet = os.path.join(dossier, *chemin.split("/"))
        if not servi(chemin) or not os.path.isfile(complet):
            ignores.append((chemin, "non servi par le site"))
        elif os.path.getsize(complet) > MAX_OCTETS:
            ignores.append((chemin, "plus de 5 Mo"))
        else:
            choisis.append(chemin)
    for chemin in choisis[MAX_FICHIERS:]:
        ignores.append((chemin, f"au-delà des {MAX_FICHIERS} premiers fichiers"))
    return choisis[:MAX_FICHIERS], ignores


def telecharger(url):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "verifier-site (GitHub Actions)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except (urllib.error.URLError, OSError) as e:
        return None, f"pas de réponse ({getattr(e, 'reason', e)})"


def comparer(a):
    dossier, base = a.comparer, a.site.rstrip("/")
    try:
        sha = git(dossier, "rev-parse", "HEAD").strip()
        fichiers, ignores = fichiers_a_comparer(dossier)
    except ErreurApi as e:
        print(f"::error::Impossible de lister les fichiers modifiés par le commit (fetch-depth 2 ?) : {e}")
        return 1
    print(f"{heure()}  commit {sha[:7]} : {len(fichiers)} fichier(s) servi(s) par le site à comparer à la version en ligne")
    for chemin, raison in ignores:
        print(f"  non comparé : {chemin} ({raison})")
    lignes = [f"## Version en ligne du commit {sha[:7]}", ""]
    if not fichiers:
        message = ("Ce commit ne modifie aucun fichier servi par le site : l'état du déploiement de GitHub Pages "
                   "suffit à dire que cette version est en ligne.")
        print(message)
        ecrire_resume(lignes + [message])
        return 0

    attendus = {}
    for chemin in fichiers:
        with open(os.path.join(dossier, *chemin.split("/")), "rb") as f:
            attendus[chemin] = f.read()
    resultats, restants, essai = {}, list(fichiers), 0
    fin = time.time() + a.delai_comparaison
    while restants:
        essai += 1
        encore = []
        for chemin in restants:
            url = f"{base}/{urllib.parse.quote(chemin)}?v={sha[:12]}-{essai}"
            contenu, erreur = telecharger(url)
            if contenu == attendus[chemin]:
                resultats[chemin] = f"identique (essai {essai}, {heure()})"
            else:
                resultats[chemin] = erreur or f"différent ({len(contenu)} octets en ligne, {len(attendus[chemin])} dans le dépôt)"
                encore.append(chemin)
        restants = encore
        if restants:
            if time.time() > fin:
                break
            print(f"{heure()}  essai {essai} : {len(restants)} fichier(s) pas encore à jour, nouvel essai dans {a.pause} s")
            time.sleep(a.pause)

    lignes += [f"{len(fichiers) - len(restants)} fichier(s) sur {len(fichiers)} identiques en ligne.", "",
               "| Fichier | En ligne |", "|---|---|"]
    for chemin in fichiers:
        print(f"  {chemin} : {resultats[chemin]}")
        lignes.append(f"| `{chemin}` | {resultats[chemin]} |")
    ecrire_resume(lignes)
    if restants:
        for chemin in restants:
            print(f"::error file={chemin}::En ligne, {chemin} ne correspond pas à ce commit : {resultats[chemin]}.")
        print(f"::error::Au bout de {a.delai_comparaison} s, {len(restants)} fichier(s) ne sont pas à jour en ligne.")
        return 1
    print("La version en ligne est bien celle de ce commit.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Attend que GitHub Pages ait mis en ligne un commit, puis le vérifie.")
    p.add_argument("--sha", help="le commit à attendre (par défaut : le dernier commit de main)")
    p.add_argument("--depot", default=os.environ.get("GITHUB_REPOSITORY", "babash/Babash-NSI-SNT"))
    p.add_argument("--branche", default="main", help="la branche publiée par GitHub Pages")
    p.add_argument("--delai", type=int, default=900, help="attente maximale du déploiement, en secondes")
    p.add_argument("--pause", type=int, default=15, help="intervalle entre deux essais, en secondes")
    p.add_argument("--comparer", metavar="DOSSIER", help="comparer au site en ligne les fichiers modifiés par le dernier commit de DOSSIER")
    p.add_argument("--site", default=SITE, help=f"adresse du site (par défaut : {SITE})")
    p.add_argument("--delai-comparaison", type=int, default=180, help="attente maximale de la comparaison, en secondes")
    a = p.parse_args()
    return comparer(a) if a.comparer else attendre(a)


if __name__ == "__main__":
    sys.exit(main())
