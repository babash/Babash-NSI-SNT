#!/usr/bin/env python3
"""Changements attendus d'une branche de fiches : la page de la bibliothèque seule (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/changements.py AVANT APRES COMPARAISON TOUCHES

AVANT et APRES : les deux copies exportées par controler.py, où la bibliothèque est construite
(donnees/bibliotheque.json) ; COMPARAISON : la sortie de comparer.py ; TOUCHES : la sortie de
`git diff --name-status base...branche`.

Une branche qui ajoute, modifie ou retire des fiches hors de la vitrine change forcément la page
de la bibliothèque : « avant/après identiques » y passe au rouge. Cet outil dit « changement
attendu » (code 0) seulement si les trois conditions sont réunies :
  1. la branche ne touche que des fiches (`donnees/ressources/<id>.json`) et des fichiers déposés
     (`<rubrique>/fichiers/…`) : ni le code, ni les pages, ni la vitrine, ni les référentiels ;
  2. seules les captures de la bibliothèque diffèrent (toutes largeurs et tous thèmes) : l'accueil
     et chaque rubrique sont identiques ;
  3. `donnees/bibliotheque.json` ne change, d'avant à après, que pour les fiches touchées : toute
     autre fiche est identique, champ par champ, et tout le reste du fichier aussi (vitrine,
     référentiels), sauf la date de construction (`construit`).
Sinon, code 1 et la raison : le Gardien examine les différences à la main. Cet outil ne remplace
pas les autres contrôles : le rendu après (erreurs JavaScript, débordements), les contrastes et
verifier-site.py restent à part, et doivent être verts.
"""
import json
import os
import re
import sys

LIGNE = re.compile(r"^(\S+) (\d+) (\S+)\s+(.*)$")
FICHE = re.compile(r"^donnees/ressources/([a-z0-9]+(?:-[a-z0-9]+)*)\.json$")
DEPOSE = re.compile(r"^[a-z0-9-]+/fichiers/")


def lire_json(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def fiches_touchees(touches):
    """Les identifiants des fiches touchées, et les chemins qui ne sont ni fiche ni fichier déposé."""
    ids, autres = set(), []
    for ligne in touches.splitlines():
        if not ligne.strip():
            continue
        morceaux = ligne.split("\t")
        for chemin in morceaux[1:]:  # un renommage (R100) donne l'ancien et le nouveau chemin
            m = FICHE.match(chemin)
            if m:
                ids.add(m.group(1))
            elif not DEPOSE.match(chemin):
                autres.append(chemin)
    return ids, autres


def pages_differentes(comparaison):
    """Les pages (avec largeur et thème) que comparer.py dit différentes ou présentes d'un seul côté."""
    out = []
    for ligne in comparaison.splitlines():
        m = LIGNE.match(ligne)
        if m and not m.group(4).startswith("identique"):
            out.append((m.group(1), m.group(2), m.group(3)))
    return out


def ecarts_bibliotheque(avant, apres, ids):
    """Ce qui change dans bibliotheque.json en dehors des fiches touchées."""
    pb = []
    for cle in sorted(set(avant) | set(apres)):
        if cle in ("construit", "ressources"):
            continue
        if avant.get(cle) != apres.get(cle):
            pb.append("« %s » change dans donnees/bibliotheque.json" % cle)
    fa = {f.get("id"): f for f in avant.get("ressources", [])}
    fb = {f.get("id"): f for f in apres.get("ressources", [])}
    for i in sorted(set(fa) | set(fb), key=str):
        if i in ids:
            continue
        if i not in fb:
            pb.append("la fiche « %s », que la branche ne touche pas, disparaît de la bibliothèque" % i)
        elif i not in fa:
            pb.append("la fiche « %s », que la branche ne touche pas, apparaît dans la bibliothèque" % i)
        elif fa[i] != fb[i]:
            champs = sorted(k for k in set(fa[i]) | set(fb[i]) if fa[i].get(k) != fb[i].get(k))
            pb.append("la fiche « %s », que la branche ne touche pas, change (%s)" % (i, ", ".join(champs)))
    ajoutees = sorted(i for i in fb if i not in fa)
    retirees = sorted(i for i in fa if i not in fb)
    modifiees = sorted(i for i in fa if i in fb and fa[i] != fb[i])
    return pb, ajoutees, modifiees, retirees


def main():
    if len(sys.argv) != 5 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0 if sys.argv[1:2] in (["-h"], ["--help"]) else 2)
    avant_d, apres_d, comparaison_f, touches_f = sys.argv[1:]
    with open(comparaison_f, encoding="utf-8") as f:
        comparaison = f.read()
    with open(touches_f, encoding="utf-8") as f:
        touches = f.read()
    raisons = []
    ids, autres = fiches_touchees(touches)
    if autres:
        raisons.append("la branche touche autre chose que des fiches et des fichiers déposés : " + ", ".join(autres[:6])
                       + (" …" if len(autres) > 6 else ""))
    if not ids:
        raisons.append("la branche ne touche aucune fiche")
    differentes = pages_differentes(comparaison)
    hors = sorted({p for p, _, _ in differentes if p != "bibliotheque"})
    if hors:
        raisons.append("d'autres pages que la bibliothèque diffèrent : " + ", ".join(hors))
    if not differentes:
        raisons.append("aucune page ne diffère (rien à expliquer)")
    chemins = [os.path.join(d, "donnees", "bibliotheque.json") for d in (avant_d, apres_d)]
    manquants = [c for c in chemins if not os.path.exists(c)]
    if manquants:
        raisons.append("bibliothèque non construite : " + ", ".join(manquants))
    else:
        pb, ajoutees, modifiees, retirees = ecarts_bibliotheque(lire_json(chemins[0]), lire_json(chemins[1]), ids)
        raisons += pb
        print("Fiches touchées par la branche : %d ; dans la bibliothèque, %d ajoutée(s), %d modifiée(s), %d retirée(s)"
              % (len(ids), len(ajoutees), len(modifiees), len(retirees)))
        for nom, liste in (("ajoutées", ajoutees), ("modifiées", modifiees), ("retirées", retirees)):
            if liste:
                print("  %s : %s" % (nom, ", ".join(liste[:12]) + (" …" if len(liste) > 12 else "")))
    if raisons:
        print("Pas un changement attendu, à examiner :")
        for r in raisons:
            print("  - " + r)
        sys.exit(1)
    print("Changement attendu : seule la bibliothèque change (%d capture(s)), et seulement par les fiches que la branche touche."
          % len(differentes))


if __name__ == "__main__":
    main()
