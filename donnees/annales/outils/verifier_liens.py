#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste les liens de donnees/annales/annales-bac-nsi.json et écrit un rapport (ne modifie rien).

Usage : python3 donnees/annales/outils/verifier_liens.py [--json chemin] [--ecrire]
  --ecrire : met à jour « etat » et « verifie_le » des liens testés dans le JSON (sinon, rapport seul).
Un lien est « ok » s'il répond 200 (PDF ou page). Les sites bloqués par le réseau de la session (kxs.fr, math93.com…)
doivent être testés depuis un environnement qui les atteint ; sinon, les liens restent « à tester » et la
procédure (MISE-A-JOUR.md, étape 4) demande de les ouvrir avec l'outil de lecture du web.
"""
import argparse, datetime, json, sys, urllib.request, urllib.error

def tester(url, delai=25):
    req = urllib.request.Request(url, headers={"User-Agent": "verif-liens-annales/1.0", "Range": "bytes=0-1023"})
    try:
        with urllib.request.urlopen(req, timeout=delai) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:                      # réseau bloqué, délai dépassé, certificat…
        return f"erreur : {type(e).__name__}"

def liens(sujet):
    for cle, l in sujet["liens"].items():
        if cle == "autres":
            for a in l: yield a
        else: yield l

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="donnees/annales/annales-bac-nsi.json")
    ap.add_argument("--ecrire", action="store_true")
    a = ap.parse_args()
    data = json.load(open(a.json, encoding="utf-8"))
    aujourdhui = datetime.date.today().isoformat()
    n = bad = 0
    for s in data["epreuve_ecrite"]["sujets"]:
        for l in liens(s):
            code = tester(l["url"]); n += 1
            if code in (200, 206):
                if a.ecrire: l["etat"] = "ok"; l["verifie_le"] = aujourdhui
            else:
                bad += 1; print(f"{code}\t{s['id']}\t{l['url']}")
                if a.ecrire: l["etat"] = f"à revoir ({code})"; l["verifie_le"] = aujourdhui
    print(f"{n} liens testés, {bad} à revoir", file=sys.stderr)
    if a.ecrire:
        data["verifie_le"] = aujourdhui
        json.dump(data, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
