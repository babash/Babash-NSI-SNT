#!/usr/bin/env python3
"""Contrôle les banques d'exercices du Calendrier des vacances (T105).

Pour chaque chapitre du catalogue (calendrier/exercices/catalogue.json) :
  1. la forme : le schéma exercice.schema.json (avec jsonschema s'il est installé),
     plus des contrôles écrits ici, qui marchent sans dépendance : identifiants
     <chapitre>-NNN qui se suivent, 3 niveaux, réponses dans les bornes, pas de
     doublon, pas de tabulation, aucun caractère invisible ;
  2. le fond, par exécution (règle 13 : « le code est exécuté ») :
     - sortie   : le programme affiche bien l'option juste (ou la réponse à taper),
                  et aucune autre option ;
     - erreur   : le programme corrigé affiche « affiche » ; le programme fautif et
                  les deux mauvaises corrections, non (ou plantent, ou ne s'arrêtent pas) ;
     - ordre    : les lignes dans l'ordre affichent « affiche » ;
     - completer: les bonnes pièces donnent « affiche » ; chaque mauvaise pièce le change ;
     - associer : avec "executer", chaque programme affiche son élément de droite ;
     - vraifaux : avec "code" et "verifier", l'expression vaut « reponse ».
     Python : python3 -I dans un processus à part, 3 s au plus (une boucle infinie
     voulue dans un programme fautif compte comme « différent »). SQL : SQLite en
     mémoire, sur la base_sql du chapitre ; une ligne par enregistrement, les
     colonnes séparées par « | ».
  3. la couverture : le nombre d'exercices relus et à relire, et le nombre de
     cases d'un calendrier de 30 jours que la banque peut remplir.

Usage :
  python3 scripts/calendrier_exercices.py                 tout le catalogue
  python3 scripts/calendrier_exercices.py --chapitre nsi1-bases-python
  python3 scripts/calendrier_exercices.py --fichier chemin/vers/brouillon.json
  python3 scripts/calendrier_exercices.py --sans-execution
  python3 scripts/calendrier_exercices.py --bundle        écrit aussi calendrier/exercices/<id>.js
Code de sortie : 1 s'il y a une erreur. Python 3 standard.
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, "calendrier", "exercices")
SCHEMA = os.path.join(DOSSIER, "exercice.schema.json")
CATALOGUE = os.path.join(DOSSIER, "catalogue.json")
TYPES = ("associer", "erreur", "vraifaux", "sortie", "ordre", "completer")
# caractères invisibles ou de contrôle, écrits par leur code (CLAUDE.md, § 4)
INVISIBLES = set([0xAD, 0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2028, 0x2029, 0x202A, 0x202B, 0x202C,
                  0x202D, 0x202E, 0x2060, 0x2066, 0x2067, 0x2068, 0x2069, 0xFEFF])


class Rapport:
    def __init__(self):
        self.erreurs, self.avertissements = [], []

    def erreur(self, ou, quoi):
        self.erreurs.append(f"ERREUR  {ou} : {quoi}")

    def avert(self, ou, quoi):
        self.avertissements.append(f"attention {ou} : {quoi}")


# ------------------------------------------------------------------ exécution

def executer_python(code, suite=""):
    """(sortie, None) ou (None, raison) : erreur, délai dépassé."""
    try:
        r = subprocess.run([sys.executable, "-I", "-c", code + suite], capture_output=True, text=True, timeout=3)
    except subprocess.TimeoutExpired:
        return None, "ne s'arrête pas (plus de 3 s)"
    if r.returncode != 0:
        derniere = (r.stderr.strip().splitlines() or ["erreur"])[-1]
        return None, derniere
    return r.stdout.rstrip("\n"), None


def executer_sql(base, requete):
    try:
        cx = sqlite3.connect(":memory:")
        cx.executescript(base)
        lignes = cx.execute(requete).fetchall()
        cx.close()
    except sqlite3.Error as e:
        return None, f"SQLite : {e}"
    return "\n".join(" | ".join("NULL" if v is None else str(v) for v in l) for l in lignes), None


INTERDITS_PY = re.compile(r"\b(input|open|exec|eval|__import__)\s*\(|\bimport\s+(random|os|sys|time|subprocess|socket)\b|\bfrom\s+(random|os|sys|time)\b")


def executer(chap, code):
    if chap["langage"] == "sql":
        if re.match(r"\s*select\b", code, re.I) and not re.search(r"\border\s+by\b", code, re.I):
            s, err = executer_sql(chap.get("_base", ""), code)
            if not err and "\n" in s:
                return None, "plusieurs lignes sans ORDER BY : leur ordre n'est pas garanti"
            return s, err
        return executer_sql(chap.get("_base", ""), code)
    return executer_python(code)


def opt_sortie(o):
    return "\n".join(x.strip() for x in o.split(" / "))


# ------------------------------------------------------------------ contrôles de forme

def textes(objet):
    if isinstance(objet, str):
        yield objet
    elif isinstance(objet, dict):
        for v in objet.values():
            yield from textes(v)
    elif isinstance(objet, list):
        for v in objet:
            yield from textes(v)


def forme(chap, ex, ou, rp):
    t = ex.get("type")
    for s in textes(ex):
        bad = [hex(ord(c)) for c in s if ord(c) in INVISIBLES or (ord(c) < 32 and c != "\n")]
        if bad:
            rp.erreur(ou, f"caractère invisible ou de contrôle {bad[:3]} dans « {s[:40]} »")
        if "\t" in s:
            rp.erreur(ou, "tabulation : indenter avec 4 espaces")
    niveaux = ex.get("niveaux", [])
    if len(niveaux) != 3:
        rp.erreur(ou, f"{len(niveaux)} niveaux au lieu de 3")
    for n, niv in enumerate(niveaux, 1):
        if not niv.get("items"):
            rp.erreur(f"{ou} niveau {n}", "aucune question")
        for q, it in enumerate(niv.get("items", []), 1):
            o2 = f"{ou} niveau {n} question {q}"
            if t == "sortie":
                if "options" in it:
                    if len(set(it["options"])) != 4:
                        rp.erreur(o2, "4 options différentes attendues")
                    if not 0 <= it.get("bonne", -1) < 4 or len(it.get("retours", [])) != 4:
                        rp.erreur(o2, "« bonne » entre 0 et 3 et 4 « retours » attendus")
                elif "reponse" not in it:
                    rp.erreur(o2, "ni options ni réponse")
            elif t == "erreur":
                if not 0 <= it.get("ligne", -1) < len(it.get("lignes", [])):
                    rp.erreur(o2, "« ligne » hors du programme")
                if not 0 <= it.get("bonne", -1) < 3:
                    rp.erreur(o2, "« bonne » entre 0 et 2")
                if it.get("lignes") and 0 <= it.get("ligne", -1) < len(it["lignes"]) and it["lignes"][it["ligne"]] in it.get("corrections", []):
                    rp.erreur(o2, "une « correction » est identique à la ligne fautive")
            elif t == "associer":
                g = [p[0] for p in it.get("paires", [])]
                d = [p[1] for p in it.get("paires", [])]
                if len(set(g)) != len(g) or len(set(d)) != len(d):
                    rp.erreur(o2, "deux paires ont le même élément")
            elif t == "ordre":
                if len(set(it.get("lignes", []))) != len(it.get("lignes", [])):
                    rp.erreur(o2, "deux lignes identiques : l'ordre juste ne serait pas unique")
            elif t == "completer":
                trous = it.get("trous", [])
                vus = set(int(x) for x in re.findall(r"\{(\d+)\}", "\n".join(it.get("lignes", []))))
                if vus != set(range(len(trous))):
                    rp.erreur(o2, f"les trous {{0}}… des lignes ({sorted(vus)}) ne correspondent pas aux {len(trous)} « trous »")
                for k, tr in enumerate(trous):
                    if not 0 <= tr.get("bonne", -1) < len(tr.get("options", [])):
                        rp.erreur(o2, f"trou {k} : « bonne » hors des options")
            elif t == "vraifaux":
                if "verifier" in it and chap["langage"] != "python":
                    rp.erreur(o2, "« verifier » n'existe qu'en Python")
            if chap["langage"] == "python":
                for champ in ("code", "lignes"):
                    v = it.get(champ)
                    v = "\n".join(v) if isinstance(v, list) else v
                    if v and INTERDITS_PY.search(v):
                        rp.erreur(o2, "input, open, eval, exec ou un module (random, os, time…) : le résultat doit être le même à chaque exécution, sans clavier ni fichier")
            if t in ("sortie", "erreur", "ordre", "completer") and not it.get("aides") and n < 3:
                rp.avert(o2, "aucun coup de pouce")


# ------------------------------------------------------------------ contrôles de fond (exécution)

def fond(chap, ex, ou, rp):
    t = ex["type"]
    sans_prog = chap["langage"] == "aucun"
    for n, niv in enumerate(ex["niveaux"], 1):
        for q, it in enumerate(niv["items"], 1):
            o2 = f"{ou} niveau {n} question {q}"
            if sans_prog:
                continue
            if t == "sortie":
                s, err = executer(chap, it["code"])
                if err:
                    rp.erreur(o2, f"le programme ne marche pas : {err}")
                    continue
                if "options" in it:
                    juste = [i for i, o in enumerate(it["options"]) if opt_sortie(o) == s]
                    if juste != [it["bonne"]]:
                        rp.erreur(o2, f"le programme affiche {s!r} ; options justes trouvées : {juste}, attendue : {it['bonne']}")
                elif s != it["reponse"]:
                    rp.erreur(o2, f"le programme affiche {s!r}, la réponse annoncée est {it['reponse']!r}")
            elif t == "erreur":
                lignes = list(it["lignes"])
                s, err = executer(chap, "\n".join(lignes))
                if not err and s == it["affiche"]:
                    rp.erreur(o2, "le programme fautif affiche déjà le bon résultat : l'erreur ne se voit pas")
                for k, c in enumerate(it["corrections"]):
                    l2 = list(lignes)
                    l2[it["ligne"]] = c
                    s, err = executer(chap, "\n".join(l2))
                    if k == it["bonne"]:
                        if err or s != it["affiche"]:
                            rp.erreur(o2, f"la bonne correction n'affiche pas « affiche » : {err or repr(s)}")
                    elif not err and s == it["affiche"]:
                        rp.erreur(o2, f"la mauvaise correction n° {k} donne aussi le bon résultat : deux réponses justes")
            elif t == "ordre":
                s, err = executer(chap, "\n".join(it["lignes"]))
                if err or s != it["affiche"]:
                    rp.erreur(o2, f"les lignes dans l'ordre n'affichent pas « affiche » : {err or repr(s)}")
            elif t == "completer":
                def rempli(choix):
                    texte = "\n".join(it["lignes"])
                    for k, tr in enumerate(it["trous"]):
                        texte = texte.replace("{%d}" % k, tr["options"][choix[k]])
                    return texte
                bons = [tr["bonne"] for tr in it["trous"]]
                s, err = executer(chap, rempli(bons))
                if err or s != it["affiche"]:
                    rp.erreur(o2, f"les bonnes pièces n'affichent pas « affiche » : {err or repr(s)}")
                for k, tr in enumerate(it["trous"]):
                    for j in range(len(tr["options"])):
                        if j == tr["bonne"]:
                            continue
                        c = list(bons)
                        c[k] = j
                        s2, err2 = executer(chap, rempli(c))
                        if not err2 and s2 == it["affiche"]:
                            rp.erreur(o2, f"trou {k} : la pièce « {tr['options'][j]} » donne aussi le bon résultat")
            elif t == "associer" and it.get("executer"):
                for g, d in it["paires"]:
                    s, err = executer(chap, g)
                    if err or s.replace("\n", ", ") != d:
                        rp.erreur(o2, f"« {g[:30]}… » affiche {err or repr(s)}, pas « {d} »")
            elif t == "vraifaux" and "code" in it:
                if "verifier" in it:
                    s, err = executer_python(it["code"], "\nprint(bool(" + it["verifier"] + "))")
                    if err:
                        rp.erreur(o2, f"code ou « verifier » en erreur : {err}")
                    elif s.splitlines()[-1] != str(it["reponse"]):
                        rp.erreur(o2, f"« {it['verifier']} » vaut {s.splitlines()[-1]}, la réponse annoncée est {it['reponse']}")
                else:
                    s, err = executer(chap, it["code"])
                    if err:
                        rp.erreur(o2, f"le code de l'affirmation ne marche pas : {err}")
                    rp.avert(o2, "affirmation sur un code sans « verifier » : à relire à la main")


# ------------------------------------------------------------------ un chapitre

def controler(chemin, rp, attendu=None, avec_execution=True, schema=None):
    nom = os.path.relpath(chemin, RACINE)
    try:
        donnees = json.load(open(chemin, encoding="utf-8"))
    except (OSError, ValueError) as e:
        rp.erreur(nom, f"illisible : {e}")
        return None
    if schema is not None:
        try:
            import jsonschema
            for e in sorted(jsonschema.Draft202012Validator(schema).iter_errors(donnees), key=lambda e: list(e.path)):
                rp.erreur(nom, f"schéma : {'/'.join(str(p) for p in e.path)} : {e.message[:160]}")
        except ImportError:
            pass
    chap = donnees.get("chapitre", {})
    cid = chap.get("id", "?")
    if attendu and cid != attendu:
        rp.erreur(nom, f"le chapitre s'appelle {cid}, le catalogue attend {attendu}")
    if chap.get("langage") not in ("python", "sql", "aucun"):
        rp.erreur(nom, "langage inconnu")
        return None
    if chap["langage"] == "sql":
        if not donnees.get("base_sql"):
            rp.erreur(nom, "langage sql sans « base_sql »")
        chap["_base"] = donnees.get("base_sql", "")
    exercices = donnees.get("exercices", [])
    for r, ex in enumerate(exercices, 1):
        ou = f"{nom} {ex.get('id', '?')}"
        if ex.get("id") != f"{cid}-{r:03d}":
            rp.erreur(ou, f"identifiant attendu à ce rang : {cid}-{r:03d}")
        if ex.get("type") not in TYPES:
            rp.erreur(ou, f"type inconnu {ex.get('type')!r}")
            continue
        forme(chap, ex, ou, rp)
        if avec_execution and not any(e.startswith(f"ERREUR  {ou}") for e in rp.erreurs):
            fond(chap, ex, ou, rp)
    relus = sum(1 for e in exercices if e.get("relu"))
    return {"id": cid, "exercices": len(exercices), "relus": relus,
            "questions": sum(len(n["items"]) for e in exercices for n in e.get("niveaux", [])),
            "types": sorted(set(e.get("type") for e in exercices)), "donnees": donnees}


def bundle(info):
    """calendrier/exercices/<id>.js : la même banque, pour une page ouverte sans serveur (file://)."""
    cible = os.path.join(DOSSIER, info["id"] + ".js")
    texte = json.dumps(info["donnees"], ensure_ascii=False, separators=(",", ":"))
    with open(cible, "w", encoding="utf-8") as f:
        f.write("// Fabriqué par scripts/calendrier_exercices.py --bundle à partir de " + info["id"] + ".json : ne pas modifier à la main.\n")
        f.write("(window.CV_BANQUES = window.CV_BANQUES || {})[" + json.dumps(info["id"]) + "] = " + texte + ";\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--chapitre")
    ap.add_argument("--fichier")
    ap.add_argument("--sans-execution", action="store_true")
    ap.add_argument("--bundle", action="store_true")
    a = ap.parse_args()
    rp = Rapport()
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    try:
        import jsonschema
        jsonschema.Draft202012Validator.check_schema(schema)
    except ImportError:
        print("(jsonschema absent : contrôles de forme du script seulement)")
    infos = []
    if a.fichier:
        infos.append(controler(a.fichier, rp, None, not a.sans_execution, schema))
    else:
        cat = json.load(open(CATALOGUE, encoding="utf-8"))
        for c in cat["chapitres"]:
            if a.chapitre and c["id"] != a.chapitre:
                continue
            chemin = os.path.join(DOSSIER, c["fichier"])
            if not os.path.exists(chemin):
                if c.get("statut") == "pret":
                    rp.erreur(c["fichier"], "chapitre « pret » au catalogue, mais le fichier manque")
                else:
                    print(f"{c['id']} : pas encore de fichier (statut {c.get('statut')})")
                continue
            info = controler(chemin, rp, c["id"], not a.sans_execution, schema)
            if info and c.get("statut") == "pret" and info["exercices"] < 30:
                rp.erreur(c["fichier"], f"« pret » demande 30 exercices au moins ({info['exercices']})")
            infos.append(info)
    for i in filter(None, infos):
        print(f"{i['id']} : {i['exercices']} exercices ({i['relus']} relus), {i['questions']} questions, types {', '.join(i['types'])} ; "
              f"remplit {min(i['exercices'], 30)} cases sur 30 d'un calendrier d'un seul chapitre")
        if i["relus"] < i["exercices"]:
            rp.avert(i["id"], f"{i['exercices'] - i['relus']} exercices à relire (« relu »: false)")
        if a.bundle and not rp.erreurs:
            bundle(i)
    for m in rp.avertissements[:40]:
        print(m)
    if len(rp.avertissements) > 40:
        print(f"… et {len(rp.avertissements) - 40} autres avertissements")
    for m in rp.erreurs:
        print(m)
    print(f"{len(rp.erreurs)} erreur(s), {len(rp.avertissements)} avertissement(s)")
    return 1 if rp.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
