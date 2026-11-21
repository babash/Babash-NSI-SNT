#!/usr/bin/env python3
"""Tests de la règle des dépôts renommés de scripts/valider_donnees.py (T100c).

Usage (depuis la racine du dépôt) : python3 -I -B scripts/tests/test_depots_renommes.py
Les cas écrivent des fichiers scripts/depots-renommes/*.json dans un dossier temporaire et appellent
directement anciens_depots() et chercher_anciens_depots(). Code de retour : 0 si tous les cas passent.
"""
import importlib.util
import json
import os
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("valider_donnees", os.path.join(os.path.dirname(ICI), "valider_donnees.py"))
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

echecs = 0


def cas(nom, ok):
    global echecs
    print(("ok    " if ok else "ÉCHEC ") + nom)
    echecs += 0 if ok else 1


def preparer(fichiers):
    racine = tempfile.mkdtemp(prefix="depots-renommes-")
    d = os.path.join(racine, "scripts", "depots-renommes")
    os.makedirs(d)
    for nom, contenu in fichiers.items():
        with open(os.path.join(d, nom), "w", encoding="utf-8") as f:
            f.write(contenu if isinstance(contenu, str) else json.dumps(contenu))
    return racine


def erreurs(fiche, fichiers):
    r = V.Rapport()
    motifs = V.anciens_depots(preparer(fichiers), r)
    V.chercher_anciens_depots("f.json", fiche, motifs, r)
    return [l for l in r.lignes if l[0] == "erreur"]


F = {"FichesNSI.json": {"ancien": "FichesNSI", "nouveau": "fiches-nsi"},
     "NSI-Terminale.json": {"ancien": "NSI-Terminale", "nouveau": "nsi-terminale"}}

cas("adresse ancienne du site publié : erreur",
    len(erreurs({"lien": "https://babash.github.io/FichesNSI/fiches/poo/"}, F)) == 1)
cas("toutes casses : erreur", len(erreurs({"lien": "https://babash.github.io/fichesnsi/"}, F)) == 1)
cas("dépôt GitHub : erreur", len(erreurs({"documents": [{"url": "https://github.com/babash/FichesNSI"}]}, F)) == 1)
cas("nouvelle adresse : rien", erreurs({"lien": "https://babash.github.io/fiches-nsi/fiches/poo/"}, F) == [])
cas("nom affiché seul : rien", erreurs({"titre": "Fiche de FichesNSI"}, F) == [])
cas("notes datées : rien", erreurs({"notes": [{"date": "2026-11-19", "texte": "dépôt https://github.com/babash/FichesNSI"}]}, F) == [])
cas("casse seule (NSI-Terminale) : l'ancienne est une erreur",
    len(erreurs({"lien": "https://github.com/babash/NSI-Terminale"}, F)) == 1)
cas("casse seule (nsi-terminale) : la nouvelle passe", erreurs({"lien": "https://github.com/babash/nsi-terminale"}, F) == [])
cas("dépôt pas encore renommé : rien", erreurs({"lien": "https://babash.github.io/QuizzNSI/"}, F) == [])
cas("préfixe d'un autre nom : rien", erreurs({"lien": "https://babash.github.io/FichesNSI-bis/"}, F) == [])
cas("fichier illisible : erreur signalée", len(erreurs({}, {"x.json": "pas du json"})) == 1)
cas("fichier incomplet : erreur signalée", len(erreurs({}, {"x.json": {"ancien": "A"}})) == 1)

print("tous les cas passent" if not echecs else f"{echecs} cas en échec")
sys.exit(1 if echecs else 0)
