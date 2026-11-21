"""Remplace les anciennes adresses des dépôts renommés (T100c, sans dépôt de redirection).

Usage : python3 -I scripts/renommer_depots.py <dossier du dépôt> [--site] [--seul <ancien nom>] [--audit]
- Seules les adresses et les noms de dépôt dans une adresse ou un chemin changent ; le nom affiché
  (« QuizzNSI », « FichesNSI »…) n'est jamais touché.
- Les anciens noms sont reconnus en toutes casses (fichesnsi, FICHESNSI…).
- Avec --site, les lignes d'historique des fiches ("date": …) restent telles quelles, ainsi que
  les relevés datés de `supabase/LISEZMOI.md`.
- Avec --seul, un seul dépôt est traité (pour faire un commit par dépôt).
- Avec --audit, rien n'est écrit : toutes les occurrences restantes des anciens noms, en toutes casses,
  sont listées (adresses ou non), pour un tri à la main.
"""
import os, re, subprocess, sys

NOMS = {
    "SNT-1er-Jour": "snt-premier-jour",
    "Ex-cution-d-branch-e": "os-humain",
    "NSI-Terminale": "nsi-terminale",
    "FichesNSI": "fiches-nsi",
    "TimelineNSI": "timeline-nsi",
    "TP-commandes-hacker": "mirage",
    "QuizzNSI": "quizz-nsi",
    "Rappel-1er": "gombessa",
}
FIN = r"(?=[/#?\"'`)\s<>.,;:\]|&]|$)"
AVANTS = (r"github\.io/", r"github\.com/babash/", r"githubusercontent\.com/babash/",
          r"nbviewer\.org/github/babash/", r"repos/babash/", r"(?<![\w.-])babash/",
          r"raw\.githack\.com/babash/", r"jsdelivr\.net/gh/babash/", r"htmlpreview\.github\.io/\?https://github\.com/babash/")


def regles(noms):
    out = []
    for a, n in noms.items():
        A = re.escape(a)
        for avant in AVANTS:
            out.append((re.compile("(" + avant + ")" + A + FIN, re.I), r"\g<1>" + n))
        # chemins absolus du site publié : "/TimelineNSI/…", '/FichesNSI/', base: '/FichesNSI'
        out.append((re.compile(r"(?<=[\"'(=\s`])/" + A + r"(?=/|[\"'`])", re.I), "/" + n))
    return out


def fichiers(racine):
    sortie = subprocess.run(["git", "-C", racine, "ls-files", "-z"], capture_output=True, check=True).stdout
    for f in sortie.decode("utf-8").split("\0"):
        if not f or f == "CLAUDE.md" or f.startswith(".claude/") or f.startswith("scripts/depots-renommes/") \
                or f in ("scripts/tests/test_depots_renommes.py", "scripts/renommer_depots.py"):
            continue
        p = os.path.join(racine, f)
        try:
            yield f, p, open(p, encoding="utf-8", newline="").read()
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            continue


def garde(site, f, ligne):
    if not site:
        return False
    if f.startswith("donnees/ressources/") and '"date"' in ligne:
        return True
    return False


def main():
    racine = sys.argv[1]
    site = "--site" in sys.argv
    noms = dict(NOMS)
    if "--seul" in sys.argv:
        a = sys.argv[sys.argv.index("--seul") + 1]
        noms = {a: NOMS[a]}
    if "--audit" in sys.argv:
        rx = re.compile("|".join(re.escape(a) for a in noms), re.I)
        n = 0
        for f, p, t in fichiers(racine):
            for i, l in enumerate(t.split("\n"), 1):
                if any(m.group(0) not in NOMS.values() for m in rx.finditer(l)):
                    n += 1
                    print(f"{f}:{i}: {l.strip()[:220]}")
        print("occurrences :", n)
        return
    R = regles(noms)
    total = 0
    for f, p, t in fichiers(racine):
        lignes = t.split("\n")
        n_mod = 0
        dans_notes = False
        for i, l in enumerate(lignes):
            if site and f.startswith("donnees/ressources/"):
                if re.match(r'\s*"notes"\s*:\s*\[', l):
                    dans_notes = not l.rstrip().endswith("]") and not l.rstrip().endswith("],")
                    continue
                if dans_notes:
                    if re.match(r"\s*\],?\s*$", l):
                        dans_notes = False
                    continue
            if garde(site, f, l):
                continue
            m = l
            for rx, rep in R:
                m = rx.sub(rep, m)
            if m != l:
                lignes[i] = m
                n_mod += 1
        if n_mod:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write("\n".join(lignes))
            total += n_mod
            print(f"{n_mod:4d}  {f}")
    print("lignes modifiées :", total)


main()
