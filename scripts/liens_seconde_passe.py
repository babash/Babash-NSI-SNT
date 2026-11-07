#!/usr/bin/env python3
"""Seconde passe du contrôle des liens (lychee), pour écarter les pannes passagères.

Certains sites échouent de temps en temps, puis répondent à la relance. Constat du 07/11 :
education.gouv.fr a laissé sans réponse une machine de GitHub pendant huit minutes, alors
qu'il répondait au même instant à une autre. La seconde passe se fait donc dans un autre job,
c'est-à-dire sur une autre machine, une à deux minutes plus tard. Un lien n'est déclaré mort
que s'il échoue aux deux passes.

Usage (dans .github/workflows/verifier.yml) :
  python3 scripts/liens_seconde_passe.py relever lychee/premiere.json lychee/releve.json
      job « Liens des ressources » : relève les liens en échec à la première passe, avec leur
      fichier et leur ligne. Dans GitHub Actions, écrit dans $GITHUB_OUTPUT « nombre=<n> » et
      « releve=<le relevé en JSON> », pour le job suivant, et écrit le résumé du contrôle.
  python3 scripts/liens_seconde_passe.py liste lychee/releve.json lychee/a-revoir.txt
      job « Liens en échec, seconde passe » : écrit les liens à revérifier, un par ligne.
  python3 scripts/liens_seconde_passe.py bilan lychee/releve.json lychee/seconde.json
      même job : bilan en français (fichier et ligne de chaque lien mort) dans le résumé ;
      code de retour 1 si au moins un lien échoue aux deux passes.

Les rapports de lychee sont en JSON (--format json) : error_map et timeout_map, rangés par
fichier source, avec pour chaque lien url, status et span (ligne).
"""
import json
import os
import sys

CARTES = ("error_map", "timeout_map", "fail_map")  # fail_map : nom utilisé par les anciennes versions
NOM_SECONDE = "Liens en échec, seconde passe"


def lire(chemin, quoi="Rapport de lychee"):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"::error::{quoi} illisible ({chemin}) : {e}")
        sys.exit(1)


def echecs(rapport):
    """{lien: [(source, ligne, erreur)]} pour tous les liens en échec ou hors délai."""
    trouves = {}
    for carte in CARTES:
        for source, liste in (rapport.get(carte) or {}).items():
            for e in liste or []:
                url = e.get("url") if isinstance(e, dict) else None
                if not url:
                    continue
                statut = e.get("status")
                if isinstance(statut, dict):
                    texte = statut.get("text") or ""
                    if statut.get("details"):
                        texte += f" ({statut['details']})"
                else:
                    texte = str(statut or "erreur")
                ligne = (e.get("span") or {}).get("line") if isinstance(e.get("span"), dict) else None
                trouves.setdefault(url, []).append((source, ligne, texte.strip() or "erreur"))
    return trouves


def nombre_annonce(rapport):
    return sum(int(rapport.get(k) or 0) for k in ("errors", "timeouts"))


def verifier_coherence(rapport, trouves, chemin):
    """Si lychee annonce des erreurs qu'on ne sait pas relever, on échoue plutôt que de les taire."""
    if nombre_annonce(rapport) and not trouves:
        print(f"::error::{chemin} annonce {nombre_annonce(rapport)} lien(s) en échec, mais leur liste est "
              "introuvable (format de lychee inattendu) : le contrôle ne peut pas conclure.")
        sys.exit(1)


def source_lisible(source):
    racine = os.environ.get("GITHUB_WORKSPACE", os.getcwd()).rstrip("/") + "/"
    s = str(source)
    if s.startswith("file://"):
        s = s[len("file://"):]
    return s[len(racine):] if s.startswith(racine) else s


def ou(source, ligne, url):
    s = source_lisible(source)
    if ligne is None and os.path.isfile(s):
        with open(s, encoding="utf-8", errors="replace") as f:
            for n, texte in enumerate(f, 1):
                if url in texte:
                    ligne = n
                    break
    return s, ligne


def place(s, ligne):
    return f"{s}, ligne {ligne}" if ligne else s


def echapper(t):
    return str(t).replace("|", "\\|")


def ecrire_resume(texte):
    print(texte)
    resume = os.environ.get("GITHUB_STEP_SUMMARY")
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(texte)


def relever(premiere, sortie):
    rapport = lire(premiere)
    trouves = echecs(rapport)
    verifier_coherence(rapport, trouves, premiere)
    releve = {
        "total": rapport.get("total"),
        "exclus": rapport.get("excludes", 0),
        "echecs": {url: [[*ou(src, ligne, url), err] for src, ligne, err in trouves[url]] for url in sorted(trouves)},
    }
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as f:
        json.dump(releve, f, ensure_ascii=False, indent=1)
    sorties = os.environ.get("GITHUB_OUTPUT")
    if sorties:
        with open(sorties, "a", encoding="utf-8") as f:
            f.write(f"nombre={len(trouves)}\n")
            f.write("releve=" + json.dumps(releve, ensure_ascii=False, separators=(",", ":")) + "\n")

    lignes = ["## Liens des ressources : première passe", ""]
    if not trouves:
        lignes.append(f"Tous les liens répondent : {releve['total']} liens vérifiés ({releve['exclus']} exclus).")
    else:
        lignes += [f"{len(trouves)} lien(s) en échec sur {releve['total']}. Ils sont revérifiés par le job "
                   f"« {NOM_SECONDE} », sur une autre machine, un peu plus tard : c'est lui qui conclut.", "",
                   "| Lien | Erreur | Où |", "|---|---|---|"]
        for url, places in releve["echecs"].items():
            lignes.append(f"| {echapper(url)} | {echapper(places[0][2])} | "
                          f"{echapper(' ; '.join(place(s, l) for s, l, _ in places))} |")
    ecrire_resume("\n".join(lignes) + "\n\n")
    return 0


def liste(releve_json, sortie):
    releve = lire(releve_json, "Relevé de la première passe")
    urls = sorted((releve.get("echecs") or {}))
    if not urls:
        print("::error::Le relevé de la première passe ne contient aucun lien : rien à revérifier.")
        return 1
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("".join(u + "\n" for u in urls))
    print(f"{len(urls)} lien(s) à revérifier :")
    for u in urls:
        print(f"  {u}")
    return 0


def bilan(releve_json, seconde):
    releve = lire(releve_json, "Relevé de la première passe")
    e1 = releve.get("echecs") or {}
    r2 = lire(seconde) if seconde and os.path.exists(seconde) else None
    if r2 is None:
        print("::warning::Pas de rapport de seconde passe : les liens en échec sont comptés comme morts.")
        e2 = {u: [(p[0], p[1], p[2]) for p in places] for u, places in e1.items()}
    else:
        e2 = echecs(r2)
        verifier_coherence(r2, e2, seconde)
        if int(r2.get("total") or 0) < len(e1):
            # Des liens n'ont pas été revérifiés : on ne les déclare pas sains
            print("::warning::La seconde passe a vérifié moins de liens qu'attendu : par prudence, "
                  "tous les liens de la première passe restent en échec.")
            e2 = {**{u: [(p[0], p[1], p[2]) for p in places] for u, places in e1.items()}, **e2}
    morts = sorted(u for u in e1 if u in e2)
    passagers = sorted(u for u in e1 if u not in e2)
    lignes = [
        "## Liens des ressources : seconde passe", "",
        "| | Nombre |", "|---|---|",
        f"| Liens vérifiés à la première passe | {releve.get('total', '?')} |",
        f"| En échec à la première passe | {len(e1)} |",
        f"| Revenus à la seconde passe (panne passagère) | {len(passagers)} |",
        f"| **Morts** (en échec aux deux passes) | **{len(morts)}** |", "",
    ]
    if morts:
        lignes += ["### Liens morts", "", "| Lien | Erreur | Où |", "|---|---|---|"]
        for url in morts:
            erreur = e2[url][0][2]
            places = []
            for s, l, _ in e1[url]:
                places.append(place(s, l))
                print(f"::error file={s}{',line=' + str(l) if l else ''}::Lien mort : {url} ({erreur})")
            lignes.append(f"| {echapper(url)} | {echapper(erreur)} | {echapper(' ; '.join(places))} |")
        lignes.append("")
    if passagers:
        lignes += ["### Pannes passagères (rien à faire)", ""]
        for url in passagers:
            s, l, err = e1[url][0]
            lignes.append(f"- {url} : {err} à la première passe ({place(s, l)}), puis réponse correcte à la seconde.")
        lignes.append("")
    ecrire_resume("\n".join(lignes) + "\n")
    return 1 if morts else 0


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "relever":
        return relever(sys.argv[2], sys.argv[3])
    if len(sys.argv) >= 4 and sys.argv[1] == "liste":
        return liste(sys.argv[2], sys.argv[3])
    if len(sys.argv) >= 3 and sys.argv[1] == "bilan":
        return bilan(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
