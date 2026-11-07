#!/usr/bin/env python3
"""Attend que GitHub Pages ait réellement mis en ligne un commit.

Le site est publié par GitHub Pages (« Deploy from a branch »). Chaque mise en ligne est un
déploiement de l'environnement « github-pages », qui porte le commit (SHA) déployé et passe
par les états waiting, queued, in_progress, puis success (ou failure, error). Il devient
inactive quand un déploiement plus récent le remplace.

Le script interroge ces déploiements jusqu'à ce que le commit soit en ligne, sans se fier au
contenu des fichiers : un envoi qui ne change pas les listes de ressources est donc attendu
lui aussi.

Usage :
  python3 scripts/attendre_deploiement.py --sha <commit>   attendre ce commit
  python3 scripts/attendre_deploiement.py                  attendre le dernier commit de main
Options : --depot babash/Babash-NSI-SNT  --delai 900 (secondes)  --pause 15 (secondes)

Résultat :
  - code 0 : le commit est en ligne, ou un commit plus récent l'a remplacé (le contrôle de ce
    commit-là vérifiera le site) ;
  - code 1 : le déploiement a échoué, le commit n'est pas sur main, ou le délai est dépassé.
Dans GitHub Actions, écrit dans $GITHUB_OUTPUT : sha=<commit> et a_verifier=oui ou non.
Utilise la commande gh (préinstallée sur les machines de GitHub Actions, jeton dans GH_TOKEN).
"""
import argparse
import json
import os
import subprocess
import sys
import time

EN_COURS = {"waiting", "queued", "pending", "in_progress"}
ECHECS = {"failure", "error"}


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


def main():
    p = argparse.ArgumentParser(description="Attend que GitHub Pages ait mis en ligne un commit.")
    p.add_argument("--sha", help="le commit à attendre (par défaut : le dernier commit de main)")
    p.add_argument("--depot", default=os.environ.get("GITHUB_REPOSITORY", "babash/Babash-NSI-SNT"))
    p.add_argument("--branche", default="main", help="la branche publiée par GitHub Pages")
    p.add_argument("--delai", type=int, default=900, help="attente maximale, en secondes")
    p.add_argument("--pause", type=int, default=15, help="intervalle entre deux questions, en secondes")
    a = p.parse_args()

    depot, branche = a.depot, a.branche
    # Le SHA complet : l'API des déploiements ne reconnaît pas un SHA abrégé
    cible = a.sha or branche
    try:
        sha = gh(f"repos/{depot}/commits/{cible}")["sha"]
    except (ErreurApi, KeyError, TypeError) as e:
        print(f"::error::Le commit « {cible} » est introuvable dans {depot} : {e}")
        ecrire_sorties(a_verifier="non")
        return 1
    print(f"Commit attendu : {sha[:7]} (dépôt {depot})")
    ecrire_sorties(sha=sha)

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
            print(f"{time.strftime('%H:%M:%S')}  {message}")
            dernier_message = message
        if decision == "en_ligne":
            ecrire_sorties(a_verifier="oui")
            return 0
        if decision == "remplace":
            print(f"::notice::Commit {sha[:7]} : {message}. Le site sera vérifié par le contrôle du commit plus récent.")
            ecrire_sorties(a_verifier="non")
            return 0
        if decision == "echec":
            print(f"::error::Commit {sha[:7]} : {message}.")
            ecrire_sorties(a_verifier="non")
            return 1
        if time.time() > fin:
            print(f"::error::Au bout de {a.delai // 60} minutes, GitHub Pages n'a toujours pas mis en ligne le commit {sha[:7]}.")
            ecrire_sorties(a_verifier="non")
            return 1
        time.sleep(a.pause)


if __name__ == "__main__":
    sys.exit(main())
