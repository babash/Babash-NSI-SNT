#!/usr/bin/env python3
"""Seconde passe du contrôle des liens (lychee), pour écarter les pannes passagères.

Certains sites échouent de temps en temps, puis répondent à la relance : un lien n'est
déclaré mort que s'il échoue aux deux passes, à quelques minutes d'intervalle.

Usage (dans .github/workflows/verifier.yml) :
  python3 scripts/liens_seconde_passe.py relever lychee/premiere.json lychee/a-revoir.txt
      écrit dans a-revoir.txt les liens en échec à la première passe (un par ligne) ;
      dans GitHub Actions, écrit « nombre=<n> » dans $GITHUB_OUTPUT.
  python3 scripts/liens_seconde_passe.py bilan lychee/premiere.json lychee/seconde.json
      écrit le bilan en français (fichier et ligne de chaque lien mort) dans le résumé du
      contrôle ; code de retour 1 si au moins un lien échoue aux deux passes.

Les rapports sont ceux de lychee en JSON (--format json) : error_map et timeout_map, rangés
par fichier source, avec pour chaque lien url, status et span (ligne).
"""
import json
import os
import sys

CARTES = ("error_map", "timeout_map", "fail_map")  # fail_map : nom utilisé par les anciennes versions


def lire(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"::error::Rapport de lychee illisible ({chemin}) : {e}")
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


def relever(premiere, sortie):
    rapport = lire(premiere)
    trouves = echecs(rapport)
    verifier_coherence(rapport, trouves, premiere)
    os.makedirs(os.path.dirname(sortie) or ".", exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as f:
        for url in sorted(trouves):
            f.write(url + "\n")
    print(f"Première passe : {rapport.get('total', '?')} liens, {len(trouves)} en échec.")
    for url in sorted(trouves):
        print(f"  à revoir : {url}")
    chemin = os.environ.get("GITHUB_OUTPUT")
    if chemin:
        with open(chemin, "a", encoding="utf-8") as f:
            f.write(f"nombre={len(trouves)}\n")
    return 0


def echapper(t):
    return str(t).replace("|", "\\|")


def bilan(premiere, seconde):
    r1 = lire(premiere)
    e1 = echecs(r1)
    verifier_coherence(r1, e1, premiere)
    lignes = ["## Liens des ressources", ""]
    if not e1:
        lignes.append(f"Tous les liens répondent : {r1.get('total', '?')} liens vérifiés "
                      f"({r1.get('excludes', 0)} exclus), dès la première passe.")
        morts, passagers = {}, []
    else:
        r2 = lire(seconde) if seconde and os.path.exists(seconde) else None
        if r2 is None:
            print("::warning::Pas de rapport de seconde passe : les liens en échec sont comptés comme morts.")
            e2 = e1
        else:
            e2 = echecs(r2)
            verifier_coherence(r2, e2, seconde)
            if int(r2.get("total") or 0) < len(e1):
                # Des liens n'ont pas été revérifiés : on ne les déclare pas sains
                print("::warning::La seconde passe a vérifié moins de liens qu'attendu : prudence, "
                      "tous les liens de la première passe sont gardés en échec.")
                e2 = {**e1, **e2}
        morts = {u: e1[u] for u in e1 if u in e2}
        passagers = sorted(u for u in e1 if u not in e2)
        lignes += [
            "| | Nombre |", "|---|---|",
            f"| Liens vérifiés | {r1.get('total', '?')} |",
            f"| En échec à la première passe | {len(e1)} |",
            f"| Revenus à la seconde passe (panne passagère) | {len(passagers)} |",
            f"| **Morts** (en échec aux deux passes) | **{len(morts)}** |", "",
        ]
        if morts:
            lignes += ["### Liens morts", "", "| Lien | Erreur | Où |", "|---|---|---|"]
            for url in sorted(morts):
                erreur = e2[url][0][2]
                places = []
                for source, ligne, _ in morts[url]:
                    s, l = ou(source, ligne, url)
                    places.append(f"{s}, ligne {l}" if l else s)
                    print(f"::error file={s}{',line=' + str(l) if l else ''}::Lien mort : {url} ({erreur})")
                lignes.append(f"| {echapper(url)} | {echapper(erreur)} | {echapper(' ; '.join(places))} |")
            lignes.append("")
        if passagers:
            lignes += ["### Pannes passagères (rien à faire)", ""]
            for url in passagers:
                s, l = ou(*e1[url][0][:2], url)
                lignes.append(f"- {url} : {e1[url][0][2]} à la première passe ({s}{', ligne ' + str(l) if l else ''}), "
                              "puis réponse correcte à la seconde.")
            lignes.append("")
    texte = "\n".join(lignes) + "\n"
    print(texte)
    resume = os.environ.get("GITHUB_STEP_SUMMARY")
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(texte)
    return 1 if morts else 0


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "relever":
        return relever(sys.argv[2], sys.argv[3])
    if len(sys.argv) >= 3 and sys.argv[1] == "bilan":
        return bilan(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
