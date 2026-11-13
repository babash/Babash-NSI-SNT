#!/usr/bin/env python3
"""Convertit le champ « notions » des fiches vers les rôles du 13/11/2026 (T64).

Avant : { "enseignees": […], "evaluees": […], "prerequises": […] }
Après : { "travaillees": […], "prerequises": […] }

  - « travaillees » réunit « enseignees » puis « evaluees », sans doublon, dans l'ordre où les notions apparaissent ;
  - une notion à la fois travaillée et prérequise reste dans « travaillees » et quitte « prerequises » ;
  - un rôle vide ne s'écrit pas ;
  - une fiche déjà convertie n'est pas touchée : le script peut se relancer sans risque.

Seul le bloc « notions » de chaque fiche est réécrit, dans la forme des fiches (un rôle par ligne) : le reste du
fichier ne change pas. Avant d'écrire, le script relit le résultat et vérifie qu'il ne diffère de la fiche que par
ses notions ; sinon il n'écrit rien et le signale.

Usage (depuis la racine du dépôt) :
  python3 scripts/convertir_notions_t64.py                 convertit les fiches de donnees/ressources/
  python3 scripts/convertir_notions_t64.py --verifier      dit ce qui serait converti, sans rien écrire
  python3 scripts/convertir_notions_t64.py --racine DIR    les fiches d'une autre copie du dépôt

Code de retour : 0 si tout est converti (ou déjà converti) ; 1 si une fiche n'a pas pu l'être ; avec --verifier,
1 aussi s'il reste des fiches à convertir. Python 3 standard, sans dépendance. Ensuite : vérifier avec
python3 scripts/valider_donnees.py --anciens-roles refuser.
"""
import argparse
import glob
import json
import os
import re
import sys

RACINE_DEFAUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCIENS = ("enseignees", "evaluees")
# Le bloc « notions » d'une fiche, tel que l'écrivent les fiches : "notions": { … } sur plusieurs lignes, une liste
# d'identifiants par rôle. Les identifiants ne contiennent ni accolade ni crochet.
BLOC = re.compile(r'(?P<debut>\n(?P<retrait>[ \t]*)"notions"[ \t]*:[ \t]*)\{[^{}]*\}')


def sans_doublon(liste):
    vus, out = set(), []
    for x in liste:
        if x not in vus:
            vus.add(x)
            out.append(x)
    return out


def convertir_notions(notions):
    """Les nouvelles notions d'une fiche, et les notions retirées des prérequises."""
    travaillees = sans_doublon(list(notions.get("travaillees", [])) + list(notions.get("enseignees", []))
                               + list(notions.get("evaluees", [])))
    avant = sans_doublon(list(notions.get("prerequises", [])))
    prerequises = [x for x in avant if x not in travaillees]
    retirees = [x for x in avant if x in travaillees]
    nouvelles = {}
    if travaillees:
        nouvelles["travaillees"] = travaillees
    if prerequises:
        nouvelles["prerequises"] = prerequises
    return nouvelles, retirees


def ecrire_bloc(notions, retrait):
    """Le bloc dans la forme des fiches : une ligne par rôle, la liste sur la ligne."""
    if not notions:
        return "{}"
    pas = retrait + "  "
    lignes = [f'{pas}"{role}": ' + json.dumps(ids, ensure_ascii=False) for role, ids in notions.items()]
    return "{\n" + ",\n".join(lignes) + "\n" + retrait + "}"


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--racine", default=RACINE_DEFAUT, help="racine du dépôt (par défaut : ce dépôt)")
    p.add_argument("--verifier", action="store_true", help="dire ce qui serait converti, sans rien écrire")
    args = p.parse_args()

    dossier = os.path.join(os.path.abspath(args.racine), "donnees", "ressources")
    chemins = sorted(glob.glob(os.path.join(dossier, "*.json")))
    if not chemins:
        print(f"ERREUR     aucune fiche dans {dossier}")
        sys.exit(1)
    converties, deja, sans, echecs, retraits = [], 0, 0, [], []
    for chemin in chemins:
        nom = os.path.relpath(chemin, os.path.abspath(args.racine))
        try:
            with open(chemin, encoding="utf-8") as f:
                texte = f.read()
            fiche = json.loads(texte)
        except (OSError, ValueError) as x:
            echecs.append(nom)
            print(f"ERREUR     {nom} : lecture impossible ({x})")
            continue
        notions = fiche.get("notions") if isinstance(fiche, dict) else None
        if not isinstance(notions, dict):
            sans += 1
            continue
        if not any(r in notions for r in ANCIENS):
            deja += 1
            continue
        if not all(isinstance(v, list) and all(isinstance(x, str) for x in v) for v in notions.values()):
            echecs.append(nom)
            print(f"ERREUR     {nom} › notions : un rôle n'est pas une liste d'identifiants ; à corriger à la main")
            continue
        nouvelles, retirees = convertir_notions(notions)
        blocs = list(BLOC.finditer(texte))
        if len(blocs) != 1:
            echecs.append(nom)
            print(f"ERREUR     {nom} › notions : bloc introuvable dans la forme attendue ; à convertir à la main")
            continue
        m = blocs[0]
        nouveau = texte[:m.start()] + m.group("debut") + ecrire_bloc(nouvelles, m.group("retrait")) + texte[m.end():]
        attendu = dict(fiche)
        attendu["notions"] = nouvelles
        try:
            relu = json.loads(nouveau)
        except ValueError:
            relu = None
        if relu != attendu or list(relu) != list(attendu):
            echecs.append(nom)
            print(f"ERREUR     {nom} › notions : la réécriture changerait autre chose que les notions ; rien n'est écrit")
            continue
        if not args.verifier:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(nouveau)
        converties.append(nom)
        for x in retirees:
            retraits.append((nom, x))
            print(f"INFO       {nom} › notions.prerequises : « {x} » est aussi travaillée : elle reste dans « travaillees »")

    verbe = "à convertir" if args.verifier else "converties"
    print()
    print(f"Bilan : {len(chemins)} fiches ; {len(converties)} {verbe}, {deja} déjà au nouveau format, {sans} sans notions, "
          f"{len(echecs)} en échec ; {len(retraits)} notion(s) retirée(s) des prérequises.")
    if args.verifier and converties:
        print("Lancer le script sans --verifier pour convertir.")
    elif not echecs:
        print("Vérifier ensuite : python3 scripts/valider_donnees.py --anciens-roles refuser")
    sys.exit(1 if echecs or (args.verifier and converties) else 0)


if __name__ == "__main__":
    main()
