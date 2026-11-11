#!/usr/bin/env python3
"""Recherche de données sensibles dans le dépôt (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/sensibles.py DEPOT                    fichiers suivis par git (version actuelle)
  python3 -I .github/gardien/sensibles.py DEPOT --historique       + lignes ajoutées dans tous les commits de toutes les branches
  python3 -I .github/gardien/sensibles.py DEPOT --diff BASE..TETE  seulement les lignes ajoutées par une branche
  python3 -I .github/gardien/sensibles.py --help                   cette aide

Motifs : mots de passe, identifiants, adresses électroniques, clés et jetons (service_role,
secret, sb_secret_, ghp_, github_pat_, sk_live_, AKIA…, clés privées), jetons JWT (le rôle
est décodé : « anon » est public par conception, « service_role » jamais), et le contexte
de CyberCase (identifiants de démonstration). Les valeurs trouvées sont masquées.
Les noms d'élèves ne se détectent pas par motif : relecture des listes et des applications.
Code de sortie 1 si un motif « à examiner » est trouvé.
"""
import base64
import json
import re
import subprocess
import sys

MOTIFS = [
    ("mot de passe", r"mots? de passe|password|passwd|\bpwd\s*[:=]|\bmdp\b"),
    ("identifiant", r"identifiants?\s*[:=]|\blogin\s*[:=]|\buser(?:name)?\s*[:=]|\butilisateur\s*[:=]"),
    ("adresse électronique", r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-z]{2,}"),
    ("clé ou jeton", r"service_role|sb_secret_|\bsecret\b|\bsk_(?:live|test)_|\bghp_[A-Za-z0-9]{20,}|\bgho_|github_pat_|"
                     r"\bAKIA[0-9A-Z]{16}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bxox[baprs]-|\bAIza[0-9A-Za-z_-]{35}\b|"
                     r"\b(?:api[_-]?key|apikey|access[_-]?token|bearer)\b|\bjetons?\b|\btoken\b"),
    ("JWT", r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("CyberCase", r"cybercase"),
]
# Adresses publiques attendues (commits, licences, exemples) : signalées à part
ADRESSES_ATTENDUES = re.compile(r"noreply@anthropic\.com|users\.noreply\.github\.com|@example\.|git@github\.com")
CONTEXTE_CYBERCASE = re.compile(r"d[ée]mo|identifiant|login|mot de passe|password|code|compte", re.I)


def role_jwt(jeton):
    try:
        charge = jeton.split(".")[1]
        charge += "=" * (-len(charge) % 4)
        return json.loads(base64.urlsafe_b64decode(charge)).get("role", "?")
    except Exception:
        return "illisible"


def masquer(texte):
    texte = re.sub(r"eyJ[A-Za-z0-9_-]{6}[A-Za-z0-9_.-]+", lambda m: m.group(0)[:9] + "…(masqué)", texte)
    texte = re.sub(r"(sb_\w{3}|ghp_|github_pat_|sk_\w{4})[A-Za-z0-9_]{4,}", r"\1…(masqué)", texte)
    return texte.strip()[:220]


def analyser(lignes, source):
    trouves = []
    for nom, ligne in lignes:
        for cat, motif in MOTIFS:
            for m in re.finditer(motif, ligne, re.I):
                gravite = "à examiner"
                detail = ""
                if cat == "JWT":
                    role = role_jwt(m.group(0))
                    detail = " (rôle %s)" % role
                    gravite = "public par conception" if role == "anon" else "à examiner"
                elif cat == "adresse électronique" and ADRESSES_ATTENDUES.search(m.group(0)):
                    gravite = "attendu"
                elif cat == "CyberCase" and not CONTEXTE_CYBERCASE.search(ligne):
                    gravite = "mention"
                trouves.append((gravite, cat + detail, nom, masquer(ligne)))
                break
    return trouves


def fichiers_suivis(depot):
    noms = subprocess.run(["git", "ls-files", "-z"], cwd=depot, capture_output=True, check=True).stdout.split(b"\0")
    lignes = []
    for n in filter(None, noms):
        chemin = n.decode()
        try:
            with open(f"{depot}/{chemin}", encoding="utf-8") as f:
                for i, l in enumerate(f, 1):
                    lignes.append((f"{chemin}:{i}", l))
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            continue  # binaire (PDF, images) : non lu
    return lignes


def lignes_ajoutees(depot, plage):
    args = ["git", "log", "-p", "--no-color", "--format=commit %h"]
    args += [plage] if plage else ["--all"]
    sortie = subprocess.run(args, cwd=depot, capture_output=True, text=True, errors="replace", check=True).stdout
    lignes, commit, fichier = [], "?", "?"
    for l in sortie.splitlines():
        if l.startswith("commit "):
            commit = l.split()[1]
        elif l.startswith("+++ "):
            fichier = l[6:] if l.startswith("+++ b/") else l[4:]
        elif l.startswith("+") and not l.startswith("+++"):
            lignes.append((f"{commit}:{fichier}", l[1:]))
    return lignes


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0 if len(sys.argv) >= 2 else 2)
    depot = sys.argv[1]
    if "--diff" in sys.argv:
        lignes = lignes_ajoutees(depot, sys.argv[sys.argv.index("--diff") + 1])
        source = "diff"
    else:
        lignes = fichiers_suivis(depot)
        source = "fichiers"
        if "--historique" in sys.argv:
            lignes += lignes_ajoutees(depot, None)
            source = "fichiers + historique"
    trouves = analyser(lignes, source)
    vus = set()
    ordre = {"à examiner": 0, "public par conception": 1, "mention": 2, "attendu": 3}
    for g, cat, ou, extrait in sorted(trouves, key=lambda t: (ordre[t[0]], t[1], t[2])):
        cle = (g, cat, ou.split(":", 1)[-1] if ":" in ou else ou, extrait)
        if cle in vus:
            continue
        vus.add(cle)
        print(f"[{g}] {cat} | {ou} | {extrait}")
    n = sum(1 for t in trouves if t[0] == "à examiner")
    print(f"\n{len(lignes)} lignes lues ({source}), {n} occurrence(s) à examiner")
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
