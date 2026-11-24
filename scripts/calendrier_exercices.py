#!/usr/bin/env python3
"""Contrôle les banques d'exercices du Calendrier des vacances (T105).

Pour chaque thème du catalogue (calendrier/exercices/catalogue.json) :
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
     - vraifaux : avec "code" et "verifier", l'expression vaut « reponse » ;
     - trace    : le tableau est celui des variables à chaque retour sur la ligne de la boucle ;
     - combien  : avec "code" et "verifier", l'expression vaut « reponse » ;
     - intrus   : avec "executer", tous les programmes affichent la même chose, sauf l'intrus ;
     - memo     : avec "executer", chaque programme affiche sa carte ;
     - bits     : les bits valent la cible (base 10, 16 ou couleur RVB).
     Python : python3 -I dans un processus à part, 3 s au plus (une boucle infinie
     voulue dans un programme fautif compte comme « différent »). SQL : SQLite en
     mémoire, sur la base_sql du chapitre ; une ligne par enregistrement, les
     colonnes séparées par « | ».
  3. la couverture : le nombre d'exercices relus et à relire, et le nombre de
     cases d'un calendrier de 30 jours que la banque peut remplir.

Usage :
  python3 scripts/calendrier_exercices.py                 tout le catalogue
  python3 scripts/calendrier_exercices.py --theme py-boucles
  python3 scripts/calendrier_exercices.py --fichier chemin/vers/brouillon.json
  python3 scripts/calendrier_exercices.py --sans-execution
  python3 scripts/calendrier_exercices.py --bundle        écrit aussi calendrier/exercices/<id>.js
  python3 scripts/calendrier_exercices.py --catalogue     remet à jour le nombre d'exercices de catalogue.json
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
TYPES = ("associer", "erreur", "vraifaux", "sortie", "ordre", "completer", "trace", "combien", "paniers", "intrus", "memo", "bits")
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

SANS_FIN = "ne s'arrête pas (plus de 3 s)"
ADRESSE = re.compile(r" at 0x[0-9a-f]+")


def executer_python(code, suite=""):
    """(sortie, None) ou (None, raison) : erreur, délai dépassé."""
    try:
        r = subprocess.run([sys.executable, "-I", "-c", code + suite], capture_output=True, text=True, timeout=3)
    except subprocess.TimeoutExpired:
        return None, SANS_FIN
    if r.returncode != 0:
        derniere = (r.stderr.strip().splitlines() or ["erreur"])[-1]
        return None, ADRESSE.sub(" at 0x…", derniere)
    # une adresse mémoire change à chaque exécution : on la remplace par « 0x… »
    return ADRESSE.sub(" at 0x…", r.stdout.rstrip("\n")), None


def instructions_sql(code):
    """Découpe un programme SQL en instructions complètes (sqlite3.complete_statement)."""
    out, cour = [], ""
    for morceau in code.split(";"):
        cour += morceau + ";"
        if sqlite3.complete_statement(cour):
            if cour.strip(" \n;"):
                out.append(cour.strip())
            cour = ""
    if cour.strip(" \n;"):
        out.append(cour.strip())
    return out


def connexion_sql(base):
    """Une base neuve, comme à chaque connexion : PRAGMA foreign_keys = ON, puis base_sql en entier."""
    cx = sqlite3.connect(":memory:")
    cx.execute("PRAGMA foreign_keys = ON")
    cx.executescript(base)
    cx.execute("PRAGMA foreign_keys = ON")
    return cx


def executer_sql(base, code, verifier=None):
    """Toutes les instructions du programme (mises à jour comprises), puis l'affichage de la
    dernière (un SELECT). Avec verifier : la valeur de cette requête-là, après le programme.
    Une erreur renvoie le message de SQLite, comme la console sqlite3 : « Error: … »."""
    try:
        cx = connexion_sql(base)
    except sqlite3.Error as e:
        return None, f"base_sql illisible : {e}"
    try:
        lignes = []
        for instr in instructions_sql(code):
            lignes = cx.execute(instr).fetchall()
        if verifier:
            lignes = cx.execute(verifier).fetchall()
        cx.close()
    except sqlite3.Error as e:
        return None, f"Error: {e}"
    return "\n".join(" | ".join("NULL" if v is None else str(v) for v in l) for l in lignes), None


MAX_PERMUTATIONS = 8
HARNAIS = r"""
import contextlib, io, itertools, json, signal, sys
d = json.load(sys.stdin)
lignes, cible = d["lignes"], d["cible"]
def fin(*a):
    raise TimeoutError
signal.signal(signal.SIGALRM, fin)
trouves = []
for p in itertools.permutations(range(len(lignes))):
    if list(p) == list(range(len(lignes))):
        continue
    try:
        code = compile("\n".join(lignes[i] for i in p), "<p>", "exec")
    except (SyntaxError, ValueError):
        continue
    f = io.StringIO()
    try:
        signal.setitimer(signal.ITIMER_REAL, 0.2)
        with contextlib.redirect_stdout(f):
            exec(code, {"__name__": "__main__"})
    except BaseException:
        continue
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    if f.getvalue().rstrip("\n") == cible:
        trouves.append([i + 1 for i in p])
        if len(trouves) >= 3:
            break
print(json.dumps(trouves))
"""


def autres_dispositions(chap, lignes, cible):
    """Les autres ordres des lignes qui affichent aussi la cible (la page n'accepte que le bon)."""
    if chap["langage"] == "sql":
        import itertools
        trouves = []
        for p in itertools.permutations(range(len(lignes))):
            if list(p) == list(range(len(lignes))):
                continue
            s, err = executer_sql(chap.get("_base", ""), "\n".join(lignes[i] for i in p))
            if not err and s == cible:
                trouves.append([i + 1 for i in p])
                break
        return trouves
    try:
        r = subprocess.run([sys.executable, "-I", "-c", HARNAIS], input=json.dumps({"lignes": lignes, "cible": cible}),
                           capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout or "[]")
    except (subprocess.TimeoutExpired, ValueError):
        return []


INTERDITS_PY = re.compile(r"\b(input|open|exec|eval|__import__)\s*\(|\bimport\s+(random|os|sys|time|subprocess|socket)\b|\bfrom\s+(random|os|sys|time)\b")


def executer(chap, code):
    if chap["langage"] == "sql":
        derniere = (instructions_sql(code) or [""])[-1]
        if re.match(r"\s*select\b", derniere, re.I) and not re.search(r"\border\s+by\b", derniere, re.I):
            s, err = executer_sql(chap.get("_base", ""), code)
            if not err and "\n" in s:
                return None, "plusieurs lignes sans ORDER BY : leur ordre n'est pas garanti"
            return s, err
        return executer_sql(chap.get("_base", ""), code)
    return executer_python(code)


TRACEUR = r"""
import json, sys
d = json.load(sys.stdin)
code, cols, ligne = d["code"], d["colonnes"], d["ligne"] + 1
vus = []
def montre(v):
    return v if isinstance(v, str) else repr(v) if not isinstance(v, (int, float, bool)) or v is None else str(v)
def suivre(f, e, a):
    if f.f_code.co_filename != "<p>":
        return None
    if e == "line" and f.f_lineno == ligne:
        vus.append([montre(f.f_locals[c]) if c in f.f_locals else "?" for c in cols])
        if len(vus) > 50:
            raise RuntimeError("plus de 50 tours")
    return suivre
c = compile(code, "<p>", "exec")
sys.settrace(suivre)
try:
    exec(c, {"__name__": "__main__"})
finally:
    sys.settrace(None)
print(json.dumps(vus))
"""


def tracer(it):
    """Les valeurs des colonnes à chaque passage sur la ligne de la boucle : le premier passage
    est « Avant la boucle », les suivants « Après le tour k » (le retour sur la ligne de la boucle)."""
    lignes = it["code"].split("\n")
    b = it.get("boucle")
    if b is None:
        b = next((i for i, l in enumerate(lignes) if re.match(r"\s*(for|while)\b", l)), None)
    if b is None or not 0 <= b < len(lignes):
        return None, "aucune ligne de boucle (for ou while) : préciser « boucle »"
    try:
        r = subprocess.run([sys.executable, "-I", "-c", TRACEUR], input=json.dumps({"code": it["code"], "colonnes": it["colonnes"], "ligne": b}),
                           capture_output=True, text=True, timeout=3)
    except subprocess.TimeoutExpired:
        return None, SANS_FIN
    if r.returncode:
        return None, (r.stderr.strip().splitlines() or ["erreur"])[-1]
    vus = json.loads(r.stdout.strip().splitlines()[-1])
    return (vus if it.get("depart") else vus[1:]), None


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
                montre = [k for k in ("message", "affiche_fautif", "boucle_infinie") if k in it]
                if len(montre) != 1:
                    rp.erreur(o2, "une « erreur » dit ce que montre le programme fautif : un seul champ parmi message, affiche_fautif, boucle_infinie (trouvé : " + (", ".join(montre) or "aucun") + ")")
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
                if "verifier" in it and "code" not in it:
                    rp.erreur(o2, "« verifier » demande un « code »")
            elif t == "trace":
                nc = len(it.get("colonnes", []))
                if any(len(l) != nc for l in it.get("tours", [])):
                    rp.erreur(o2, f"chaque ligne de « tours » a {nc} valeur(s), une par colonne")
                for v in it.get("visibles", []):
                    if not (0 <= v[0] < len(it.get("tours", [])) and 0 <= v[1] < nc):
                        rp.erreur(o2, f"« visibles » {v} hors du tableau")
                if len(it.get("visibles", [])) >= len(it.get("tours", [])) * nc:
                    rp.erreur(o2, "toutes les cases sont déjà remplies : rien à écrire")
            elif t == "combien":
                if not it.get("min", 0) <= it.get("reponse", 0) <= it.get("max", 0):
                    rp.erreur(o2, "« reponse » hors de [min, max]")
                if it.get("depart", it.get("min")) == it.get("reponse"):
                    rp.erreur(o2, "le compteur commence sur la réponse : changer « depart » ou « min »")
                if "verifier" in it and "code" not in it:
                    rp.erreur(o2, "« verifier » demande un « code »")
                if "code" in it and "verifier" not in it:
                    rp.avert(o2, "« combien » avec un code sans « verifier » : à relire à la main")
            elif t == "paniers":
                cartes = it.get("cartes", [])
                if len(set(c.get("texte") for c in cartes)) != len(cartes):
                    rp.erreur(o2, "deux cartes ont le même texte")
                if len(set(c.get("panier") for c in cartes)) < 2:
                    rp.erreur(o2, "les deux paniers doivent recevoir au moins une carte")
                if len(set(it.get("paniers", []))) != 2:
                    rp.erreur(o2, "deux paniers de noms différents")
            elif t == "intrus":
                if not 0 <= it.get("intrus", -1) < len(it.get("elements", [])):
                    rp.erreur(o2, "« intrus » hors des éléments")
                pq = it.get("pourquoi", {})
                if not 0 <= pq.get("bonne", -1) < len(pq.get("options", [])) or len(pq.get("retours", [])) != len(pq.get("options", [])):
                    rp.erreur(o2, "« pourquoi » : « bonne » dans les options et un retour par option")
                if "retours" in it and len(it["retours"]) != len(it.get("elements", [])):
                    rp.erreur(o2, "« retours » : un par élément")
            elif t == "memo":
                cartes = [c for p in it.get("paires", []) for c in p]
                if len(set(cartes)) != len(cartes):
                    rp.erreur(o2, "deux cartes ont le même texte : la paire ne serait pas unique")
            elif t == "bits":
                b = it.get("reponse", "")
                if len(b) % 4:
                    rp.erreur(o2, "« reponse » : un nombre de bits multiple de 4 (4, 8, 16 ou 24)")
                if it.get("base") == "rvb" and len(b) != 24:
                    rp.erreur(o2, "une couleur RVB a 24 bits")
                try:
                    c = it.get("cible", "")
                    v = int(c.lstrip("#").removeprefix("0x"), 16) if it.get("base") in ("16", "rvb") else int(c)
                    if v != int(b or "0", 2):
                        rp.erreur(o2, f"les bits {b} valent {int(b or '0', 2)}, pas la cible {c}")
                except ValueError:
                    rp.erreur(o2, f"« cible » illisible en base {it.get('base', '10')}")
                if b and b == "0" * len(b):
                    rp.erreur(o2, "tous les bits éteints : la page commence ainsi, la réponse serait déjà là")
            if chap["langage"] == "python":
                for champ in ("code", "lignes"):
                    v = it.get(champ)
                    v = "\n".join(v) if isinstance(v, list) else v
                    if v and INTERDITS_PY.search(v):
                        rp.erreur(o2, "input, open, eval, exec ou un module (random, os, time…) : le résultat doit être le même à chaque exécution, sans clavier ni fichier")
            if t in ("sortie", "erreur", "ordre", "completer", "trace", "combien", "bits") and not it.get("aides") and n < 3:
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
                # ce que montre le programme fautif : le message d'erreur, sa sortie, ou une boucle sans fin
                if err == SANS_FIN:
                    if not it.get("boucle_infinie"):
                        rp.erreur(o2, "le programme fautif ne s'arrête pas : écrire \"boucle_infinie\": true")
                elif err:
                    m = it.get("message")
                    if m is None:
                        rp.erreur(o2, f"le programme fautif s'arrête sur une erreur : écrire \"message\": {err!r}")
                    elif m.split(":")[0] != err.split(":")[0]:
                        rp.erreur(o2, f"« message » annonce {m!r}, le programme donne {err!r}")
                    elif m != err:
                        rp.avert(o2, f"« message » diffère un peu du message réel ({err!r}) : version de Python ou de SQLite ?")
                elif "affiche_fautif" not in it:
                    rp.erreur(o2, f"erreur de logique : écrire \"affiche_fautif\": {s!r}")
                elif it["affiche_fautif"] != s:
                    rp.erreur(o2, f"« affiche_fautif » vaut {it['affiche_fautif']!r}, le programme fautif affiche {s!r}")
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
                elif len(it["lignes"]) > MAX_PERMUTATIONS:
                    rp.avert(o2, f"{len(it['lignes'])} lignes : les autres dispositions ne sont pas toutes essayées (au plus {MAX_PERMUTATIONS} lignes)")
                else:
                    autres = autres_dispositions(chap, it["lignes"], it["affiche"])
                    if autres:
                        rp.erreur(o2, f"une autre disposition donne aussi le bon résultat (ordre {autres[0]}) : réunir les lignes indépendantes (a, b = 1, 2)")
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
            elif t == "trace":
                tours, err = tracer(it)
                if err:
                    rp.erreur(o2, f"le code ne marche pas : {err}")
                elif tours != it["tours"]:
                    rp.erreur(o2, f"le tableau annoncé ne suit pas le code ; relevé à chaque retour sur la boucle : {tours}")
            elif t == "combien" and "verifier" in it:
                if chap["langage"] == "sql":
                    s, err = executer_sql(chap.get("_base", ""), it["code"], it["verifier"])
                else:
                    s, err = executer_python("import contextlib as _c, io as _i\n_f = _i.StringIO()\nwith _c.redirect_stdout(_f):\n    exec(" + repr(it["code"]) + ")\nsortie = _f.getvalue()",
                                             "\nprint(" + it["verifier"] + ")")
                if err:
                    rp.erreur(o2, f"code ou « verifier » en erreur : {err}")
                elif s.splitlines()[-1].strip() != str(it["reponse"]):
                    rp.erreur(o2, f"« {it['verifier']} » vaut {s.splitlines()[-1]}, la réponse annoncée est {it['reponse']}")
            elif t == "intrus" and it.get("executer"):
                sorties = []
                for e in it["elements"]:
                    s, err = executer(chap, e)
                    sorties.append(err or s)
                autres = set(x for k, x in enumerate(sorties) if k != it["intrus"])
                if len(autres) != 1:
                    rp.erreur(o2, f"les éléments qui ne sont pas l'intrus n'affichent pas tous la même chose : {sorties}")
                elif sorties[it["intrus"]] in autres:
                    rp.erreur(o2, "l'intrus affiche la même chose que les autres")
            elif t == "memo" and it.get("executer"):
                for g, d in it["paires"]:
                    s, err = executer(chap, g)
                    if err or s.replace("\n", ", ") != d:
                        rp.erreur(o2, f"« {g[:30]}… » affiche {err or repr(s)}, pas « {d} »")
            elif t == "vraifaux" and "code" in it:
                if "verifier" in it and chap["langage"] == "sql":
                    s, err = executer_sql(chap.get("_base", ""), it["code"], it["verifier"])
                    if err:
                        rp.erreur(o2, f"code ou « verifier » en erreur : {err}")
                    elif (s not in ("0", "", "NULL")) != it["reponse"]:
                        rp.erreur(o2, f"« {it['verifier']} » donne {s!r}, la réponse annoncée est {it['reponse']}")
                elif "verifier" in it:
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


# ------------------------------------------------------------------ places des bonnes réponses

def places(cid, exercices, rp):
    """Un avertissement quand la bonne réponse est toujours à la même place dans un thème."""
    lignes_fautives, bonnes = [], {"sortie": [], "erreur": [], "completer": []}
    for ex in exercices:
        for n, niv in enumerate(ex.get("niveaux", []), 1):
            reps = [it.get("reponse") for it in niv.get("items", []) if ex.get("type") == "vraifaux"]
            if len(reps) >= 4 and len(set(reps)) == 1:
                rp.avert(f"{cid} {ex.get('id')} niveau {n}", f"toutes les affirmations sont {'vraies' if reps[0] else 'fausses'}")
            for it in niv.get("items", []):
                t = ex.get("type")
                if t == "erreur" and it.get("lignes"):
                    lignes_fautives.append("dernière" if it.get("ligne") == len(it["lignes"]) - 1 else "première" if it.get("ligne") == 0 else "milieu")
                if t in ("sortie", "erreur") and "bonne" in it:
                    bonnes[t].append(it["bonne"])
                if t == "intrus":
                    bonnes.setdefault("intrus", []).append(it.get("intrus"))
                if t == "completer":
                    bonnes[t].extend(tr.get("bonne") for tr in it.get("trous", []))
    if len(lignes_fautives) >= 6 and len(set(lignes_fautives)) == 1:
        rp.avert(cid, f"dans toutes les « erreur », la ligne fausse est la {lignes_fautives[0]} : varier sa place")
    for t, l in bonnes.items():
        if len(l) >= 6 and len(set(l)) == 1:
            rp.avert(cid, f"dans les « {t} », la bonne proposition est toujours la n° {l[0] + 1} du fichier (la page les mélange, mais le corrigé imprimé les montre dans l'ordre)")


# ------------------------------------------------------------------ les tables d'un thème SQL, pour la page

def tables_sql(base):
    cx = connexion_sql(base)
    noms = [r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid")]
    out = []
    for nom in noms:
        cur = cx.execute(f'SELECT * FROM "{nom}"')
        out.append({"nom": nom, "colonnes": [c[0] for c in cur.description],
                    "lignes": [["NULL" if v is None else v for v in l] for l in cur.fetchall()]})
    cx.close()
    return out


def fichier_tables(info, ecrire, rp):
    """calendrier/exercices/<id>.tables.json : les tables de base_sql, que la page montre (repliables)."""
    if info["donnees"].get("theme", info["donnees"].get("chapitre", {})).get("langage") != "sql":
        return
    chemin = os.path.join(DOSSIER, info["id"] + ".tables.json")
    attendu = {"explication": "Fabriqué par scripts/calendrier_exercices.py --tables à partir de base_sql : ne pas modifier à la main.",
               "tables": tables_sql(info["donnees"].get("base_sql", ""))}
    texte = json.dumps(attendu, ensure_ascii=False, indent=1) + "\n"
    if ecrire:
        open(chemin, "w", encoding="utf-8").write(texte)
    elif not os.path.exists(chemin) or open(chemin, encoding="utf-8").read() != texte:
        rp.erreur(os.path.relpath(chemin, RACINE), "absent ou pas à jour : relancer avec --tables")


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
    if "theme" in donnees:
        chap = donnees["theme"]
    else:
        chap = donnees.get("chapitre", {})
        rp.avert(nom, "« chapitre » est l'ancien nom : renommer la clé en « theme »")
    if "niveau" in chap and "niveaux" not in chap:
        rp.avert(nom, "« niveau » est l'ancienne forme : écrire « niveaux » (une liste, indicative)")
    cid = chap.get("id", "?")
    if attendu and cid != attendu:
        rp.erreur(nom, f"le thème s'appelle {cid}, le catalogue attend {attendu}")
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
    places(cid, exercices, rp)
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
    ap.add_argument("--theme", "--chapitre", dest="chapitre")
    ap.add_argument("--fichier")
    ap.add_argument("--sans-execution", action="store_true")
    ap.add_argument("--bundle", action="store_true")
    ap.add_argument("--tables", action="store_true", help="écrit <id>.tables.json pour les thèmes SQL")
    ap.add_argument("--catalogue", action="store_true", help="remet à jour le nombre d'exercices de catalogue.json")
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
        for c in cat["themes"]:
            if a.chapitre and c["id"] != a.chapitre:
                continue
            chemin = os.path.join(DOSSIER, c["fichier"])
            if not os.path.exists(chemin):
                if c.get("statut") == "pret":
                    rp.erreur(c["fichier"], "thème « pret » au catalogue, mais le fichier manque")
                else:
                    print(f"{c['id']} : pas encore de fichier (statut {c.get('statut')})")
                continue
            info = controler(chemin, rp, c["id"], not a.sans_execution, schema)
            if info and c.get("exercices") != info["exercices"]:
                if a.catalogue:
                    c["exercices"] = info["exercices"]
                    a.catalogue_change = True
                else:
                    rp.avert(c["fichier"], f"catalogue.json annonce {c.get('exercices')} exercices, le fichier en a {info['exercices']} : relancer avec --catalogue")
            if info and c.get("statut") == "pret" and info["exercices"] < 8:
                rp.erreur(c["fichier"], f"« pret » demande 8 exercices au moins ({info['exercices']})")
            infos.append(info)
    if getattr(a, "catalogue_change", False):
        with open(CATALOGUE, "w", encoding="utf-8") as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("catalogue.json : nombres d'exercices mis à jour")
    for i in filter(None, infos):
        print(f"{i['id']} : {i['exercices']} exercices ({i['relus']} relus), {i['questions']} questions, types {', '.join(i['types'])} ; "
              f"assez pour {i['exercices']} cases ; un calendrier de 30 jours en alternance demande {-(-30 // 1)} exercices pour 1 thème, 15 pour 2, 10 pour 3, 8 pour 4")
        if i["relus"] < i["exercices"]:
            rp.avert(i["id"], f"{i['exercices'] - i['relus']} exercices à relire (« relu »: false)")
        if a.bundle and not rp.erreurs:
            bundle(i)
        if not a.fichier:
            fichier_tables(i, a.tables, rp)
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
