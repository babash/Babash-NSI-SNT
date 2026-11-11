#!/usr/bin/env python3
"""Deux versions d'un PDF, ou de tous les PDF d'un dossier : ce qui change (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/pdf_comparer.py AVANT APRES [--mention TEXTE] [--marge-bas 4]

AVANT et APRES : deux fichiers PDF, ou deux dossiers (les PDF de même nom, sous-dossiers compris,
sont comparés ; ceux qui ne sont que d'un côté sont listés). Par exemple les PDF publiés avant la
branche et ceux que fabrique son build, ou un PDF LaTeX livré et sa recompilation.
Pour chaque paire :
  - nombre de pages et format (pdfinfo) ;
  - mots de l'avant absents de l'après : la comparaison se fait sans les espaces, si bien qu'un mot
    coupé par un retour à la ligne compte comme présent ; mots nouveaux ;
  - avec --mention TEXTE (la mention de l'auteur et de la licence, par exemple) : sur chaque page
    de l'après, la mention est là (suite de mots, la plus basse de la page), aucun autre mot ne la
    chevauche, et aucun mot ne descend dans les MARGE mm du bas de la page (défaut : 4).
Code de sortie 1 si un point est à examiner : un PDF d'un seul côté, un nombre de pages qui change,
un mot perdu, une mention absente ou touchée. Le Gardien juge ensuite (un mot perdu peut être une
coquille corrigée). Il faut pdfinfo et pdftotext (poppler).
"""
import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


def info(pdf):
    sortie = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    pages = re.search(r"^Pages:\s+(\d+)", sortie, re.M)
    taille = re.search(r"^Page size:\s+(.+)$", sortie, re.M)
    return int(pages.group(1)) if pages else 0, (taille.group(1).strip() if taille else "?")


def texte(pdf):
    return subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True).stdout


def mots(t):
    return re.findall(r"\w+", t)


def boites(pdf):
    """Page par page : (hauteur, [(mot, xMin, yMin, xMax, yMax)]), d'après pdftotext -bbox."""
    xml = subprocess.run(["pdftotext", "-bbox", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True).stdout
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml).replace('xmlns="http://www.w3.org/1999/xhtml"', "")
    pages = []
    for page in ET.fromstring(xml).iter("page"):
        ws = [(w.text or "", float(w.get("xMin")), float(w.get("yMin")), float(w.get("xMax")), float(w.get("yMax")))
              for w in page.iter("word")]
        pages.append((float(page.get("height")), ws))
    return pages


def zone_mention(ws, attendus):
    """La suite de mots de la mention la plus basse de la page : ((début, fin), boîte) ou None."""
    n = len(attendus)
    meilleure = None
    for i in range(len(ws) - n + 1):
        if [w[0] for w in ws[i:i + n]] == attendus:
            y = min(w[2] for w in ws[i:i + n])
            if meilleure is None or y > meilleure[1]:
                meilleure = (i, y)
    if meilleure is None:
        return None
    i = meilleure[0]
    groupe = ws[i:i + n]
    return (i, i + n), (min(g[1] for g in groupe), min(g[2] for g in groupe), max(g[3] for g in groupe), max(g[4] for g in groupe))


def controler_mention(pdf, mention, marge_mm):
    attendus = mention.split()
    defauts = []
    for k, (h, ws) in enumerate(boites(pdf), 1):
        z = zone_mention(ws, attendus)
        if z is None:
            defauts.append("p. %d : mention absente" % k)
            continue
        (a, b), (x0, y0, x1, y1) = z
        bas = h - marge_mm * 72 / 25.4
        for j, w in enumerate(ws):
            if a <= j < b:
                continue
            chevauche = not (w[3] < x0 or w[1] > x1 or w[4] < y0 or w[2] > y1)
            if chevauche or w[4] > bas + 0.5:
                defauts.append("p. %d : « %s » %s" % (k, w[0], "chevauche la mention" if chevauche else "dans la marge du bas"))
        if y1 > bas + 0.5:
            defauts.append("p. %d : la mention descend dans la marge du bas" % k)
    return defauts


def paires(avant, apres):
    if os.path.isfile(avant) and os.path.isfile(apres):
        return [(os.path.basename(apres), avant, apres)], [], []

    def liste(d):
        trouves = {}
        for racine, _, fichiers in os.walk(d):
            for f in fichiers:
                if f.lower().endswith(".pdf"):
                    chemin = os.path.join(racine, f)
                    trouves[os.path.relpath(chemin, d)] = chemin
        return trouves
    av, ap = liste(avant), liste(apres)
    communs = [(nom, av[nom], ap[nom]) for nom in sorted(set(av) & set(ap))]
    return communs, sorted(set(av) - set(ap)), sorted(set(ap) - set(av))


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("avant", help="PDF ou dossier d'avant")
    a.add_argument("apres", help="PDF ou dossier d'après")
    a.add_argument("--mention", help="texte de la mention attendue sur chaque page de l'après")
    a.add_argument("--marge-bas", type=float, default=4.0, help="marge du bas, en mm, où aucun mot ne doit descendre")
    o = a.parse_args()
    for chemin in (o.avant, o.apres):
        if not os.path.exists(chemin):
            a.error("introuvable : " + chemin)
    communs, seulement_avant, seulement_apres = paires(o.avant, o.apres)
    examiner = 0
    if seulement_avant:
        print("PDF de l'avant absents de l'après : " + ", ".join(seulement_avant))
        examiner += len(seulement_avant)
    if seulement_apres:
        print("PDF nouveaux : " + ", ".join(seulement_apres))
        examiner += len(seulement_apres)
    for nom, av, ap in communs:
        (n_av, t_av), (n_ap, t_ap) = info(av), info(ap)
        texte_av, texte_ap = texte(av), texte(ap)
        colle = re.sub(r"\s+", "", texte_ap)
        perdus = sorted({m for m in mots(texte_av) if m not in colle})
        nouveaux = sorted(set(mots(texte_ap)) - set(mots(texte_av)))
        points = []
        if n_av != n_ap:
            points.append("pages %d -> %d" % (n_av, n_ap))
        if t_av != t_ap:
            points.append("format %s -> %s" % (t_av, t_ap))
        if perdus:
            points.append("%d mot(s) perdu(s)" % len(perdus))
        mention = controler_mention(ap, o.mention, o.marge_bas) if o.mention else []
        if mention:
            points.append("mention : %d défaut(s)" % len(mention))
        examiner += bool(points)
        print("%s : %d page(s) %s -> %d page(s) %s ; %s" % (nom, n_av, t_av, n_ap, t_ap, "À EXAMINER (" + ", ".join(points) + ")" if points else "ok"))
        if perdus:
            print("    mots de l'avant absents de l'après : " + " ".join(perdus[:60]) + (" …" if len(perdus) > 60 else ""))
        if nouveaux:
            print("    mots nouveaux (%d) : %s" % (len(nouveaux), " ".join(nouveaux)[:400]))
        if o.mention:
            print("    mention : " + ("présente sur chaque page, rien ne la touche" if not mention else " ; ".join(mention[:10])))
    print("\n%d PDF comparé(s) ; %d point(s) à examiner" % (len(communs), examiner))
    sys.exit(1 if examiner else 0)


if __name__ == "__main__":
    main()
