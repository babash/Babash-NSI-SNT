#!/usr/bin/env python3
"""QuizzNSI : vérificateur d'un fichier de cours-quiz (cours/<id>.json).

Lancement, depuis la racine de QuizzNSI :
    python3 -I outils/verifier_cours.py cours/piles-files.json
    python3 -I outils/verifier_cours.py --tous            (tous les fichiers de cours/)
    python3 -I outils/verifier_cours.py --sans-execution cours/x.json

Ce qu'il contrôle (le détail est dans cours/FORMAT.md) :
- la forme : champs obligatoires, types de diapositives, schémas connus ;
- les questions (règle 22) : 20 questions, 4 options, une seule juste, un feedback
  pour chaque option, l'objectif, le nom, aucune mise en avant (gras) ;
- la répartition des bonnes réponses entre A, B, C et D, sans série ni motif évident,
  et la bonne réponse qui n'est pas trop souvent la plus longue ;
- les caractères invisibles ou de contrôle, refusés partout ;
- l'exécution : le prélude Python, puis le code affiché, puis chaque vérification ;
  la sortie et l'erreur attendues doivent être exactement celles obtenues.

Code de sortie : 0 si tout est conforme (des avertissements sont possibles), 1 sinon.
Licence MIT, Babash - NSI Tani Malandi.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata

FORMAT = "quizz-nsi/1"
LETTRES = "ABCD"
TYPES_DIAPO = {"titre", "partie", "classe", "humour", "notion", "question", "bilan"}
TYPES_SCHEMA = {"pile", "file", "etapes", "deux-piles", "liste", "decalage", "svg"}
FEEDBACK_MIN = 40          # caractères : un feedback plus court n'explique rien
TEXTE_NOTION_MAX = 3       # puces par notion (peu de texte, règle 3)
PUCE_MAX = 300             # caractères par puce
DELAI = 20                 # secondes par exécution


class Rapport:
    def __init__(self):
        self.erreurs, self.avertissements = [], []

    def erreur(self, ou, msg):
        self.erreurs.append(f"{ou} : {msg}")

    def avert(self, ou, msg):
        self.avertissements.append(f"{ou} : {msg}")


def caracteres_interdits(texte):
    """Renvoie les caractères de contrôle, invisibles ou privés d'une chaîne."""
    mauvais = []
    for c in texte:
        cat = unicodedata.category(c)
        if c == "\n" or c == " ":
            continue
        if cat in ("Cc", "Cf", "Co", "Cs", "Cn", "Zl", "Zp") or (cat == "Zs" and c != " " and c != chr(0xA0) and c != chr(0x202F)):
            mauvais.append(f"U+{ord(c):04X}")
    return mauvais


def parcourir_chaines(obj, chemin="cours"):
    if isinstance(obj, str):
        yield chemin, obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from parcourir_chaines(v, f"{chemin}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from parcourir_chaines(v, f"{chemin}.{k}")


def liste_de_chaines(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def verifier_schema(s, ou, r):
    if not isinstance(s, dict) or s.get("type") not in TYPES_SCHEMA:
        r.erreur(ou, f"schéma inconnu (types permis : {', '.join(sorted(TYPES_SCHEMA))})")
        return
    t = s["type"]
    if t in ("pile", "file", "liste", "decalage") and not isinstance(s.get("elements"), list):
        r.erreur(ou, f"le schéma « {t} » demande une liste « elements »")
    if "code" in s and not liste_de_chaines(s["code"]):
        r.erreur(ou, "« code » d'un schéma : une liste de lignes")
    if t == "etapes":
        if s.get("structure") not in ("pile", "file"):
            r.erreur(ou, "le schéma « etapes » demande « structure » : pile ou file")
        et = s.get("etapes")
        if not isinstance(et, list) or not et or not all(isinstance(e, dict) and isinstance(e.get("op"), str) and isinstance(e.get("elements"), list) for e in et):
            r.erreur(ou, "le schéma « etapes » demande des étapes { op, elements }")
        elif len(et) > 6:
            r.avert(ou, "plus de 6 étapes : le schéma sera serré à 320 px")
    if t == "deux-piles":
        for cote in ("gauche", "droite"):
            c = s.get(cote)
            if not isinstance(c, dict) or not isinstance(c.get("nom"), str) or not isinstance(c.get("elements"), list):
                r.erreur(ou, f"le schéma « deux-piles » demande « {cote} » : {{ nom, elements }}")
    if t == "svg":
        code = s.get("code", "")
        if (not isinstance(code, str) or not code.strip().startswith("<svg") or "<script" in code.lower()
                or re.search(r"\son[a-z]+\s*=", code.lower()) or "javascript:" in code.lower()):
            r.erreur(ou, "le schéma « svg » doit commencer par <svg et ne contenir ni script ni attribut on…")


def programme_schema(s):
    """Le programme Python qui recalcule l'état dessiné par un schéma, ou None s'il ne se déduit d'aucun code.

    - « etapes » avec « variable » : chaque « op » est du code ; « code → valeur » vérifie aussi la valeur
      renvoyée ; après chaque étape, le contenu de la variable doit être exactement « elements »
      (une pile du bas vers le haut, une file de la tête vers la queue, comme le dessin) ;
    - « pile », « file », « liste », « deux-piles » avec « code » : après le code, chaque variable dessinée
      (« variable », ou le « nom » de chaque pile pour deux-piles) contient exactement « elements »."""
    t = s.get("type")
    lignes = []
    if t == "etapes" and s.get("variable"):
        v = s["variable"]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", v):
            return None
        classe = "Pile" if s.get("structure") == "pile" else "File"
        if not s["etapes"] or "=" not in s["etapes"][0]["op"].split("→")[0]:
            lignes.append(f"{v} = {classe}()")
        for k, e in enumerate(s["etapes"]):
            code, _, attendu = e["op"].partition("→")
            code, attendu = code.strip(), attendu.strip()
            if attendu:
                lignes.append(f"__r = {code}")
                lignes.append(f"assert __r == ({attendu}), {f'étape {k + 1} : {code} renvoie '!r} + repr(__r) + {f', le schéma dit {attendu}'!r}")
            else:
                lignes.append(code)
            dessin = e["elements"]
            msg1, msg2 = f"étape {k + 1} ({code}) : état obtenu ", f", état dessiné {dessin!r}"
            lignes.append(f"assert {v}.contenu == {dessin!r}, {msg1!r} + repr({v}.contenu) + {msg2!r}")
        return lignes
    if t in ("pile", "file", "liste", "deux-piles") and isinstance(s.get("code"), list):
        lignes = list(s["code"])
        if t == "deux-piles":
            cotes = [(s["gauche"]["nom"], s["gauche"]["elements"]), (s["droite"]["nom"], s["droite"]["elements"])]
        else:
            cotes = [(s.get("variable", "p" if t == "pile" else "f" if t == "file" else "liste"), s["elements"])]
        for nom, el in cotes:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", nom):
                return None
            contenu = nom if t == "liste" else nom + ".contenu"
            lignes.append(f"assert {contenu} == {el!r}, {f'{nom} : état obtenu '!r} + repr({contenu}) + {f', état dessiné {el!r}'!r}")
        return lignes
    return None


def verifier_schema_execution(s, prelude, ou, r):
    if not isinstance(s, dict):
        return
    prog = programme_schema(s)
    if prog is None:
        return
    sortie, err, detail = executer(list(prelude) + prog)
    if err:
        msg = detail.splitlines()[-1] if detail else err
        r.erreur(ou, f"schéma faux : {msg}")


def executer(lignes, delai=DELAI):
    """Exécute un programme Python isolé ; renvoie (sortie, nom de l'erreur ou None, message)."""
    with tempfile.TemporaryDirectory() as d:
        chemin = os.path.join(d, "essai.py")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n")
        try:
            p = subprocess.run([sys.executable, "-I", chemin], capture_output=True, text=True, timeout=delai, cwd=d,
                               env={"PYTHONIOENCODING": "utf-8", "PATH": os.environ.get("PATH", "")})
        except subprocess.TimeoutExpired:
            return "", "Timeout", f"plus de {delai} s"
    erreur = None
    if p.returncode != 0:
        derniere = [l for l in p.stderr.strip().splitlines() if l.strip()]
        derniere = derniere[-1] if derniere else ""
        erreur = derniere.split(":")[0].strip() or "Erreur"
    return p.stdout.rstrip("\n"), erreur, p.stderr.strip()


def verifier_question(q, n, prelude, r, executer_code=True):
    ou = f"question {n} ({q.get('id', '?')})"
    for champ in ("id", "nom", "objectif"):
        if not isinstance(q.get(champ), str) or not q[champ].strip():
            r.erreur(ou, f"champ « {champ} » manquant ou vide")
    if not liste_de_chaines(q.get("enonce")) or not q.get("enonce"):
        r.erreur(ou, "« enonce » doit être une liste de paragraphes non vide")
    if "code" in q and not liste_de_chaines(q["code"]):
        r.erreur(ou, "« code » doit être une liste de lignes")
    if "schema" in q:
        verifier_schema(q["schema"], ou, r)
        if executer_code:
            verifier_schema_execution(q["schema"], prelude, ou + ", schéma", r)
    if not isinstance(q.get("explication"), str) or not q["explication"].strip():
        r.erreur(ou, "« explication » manquante (la phrase qui consolide, montrée après la réponse)")
    opts = q.get("options")
    if not isinstance(opts, list) or len(opts) != 4:
        r.erreur(ou, "il faut exactement 4 options (QCU, règle 22)")
        return None, 0
    justes = [i for i, o in enumerate(opts) if isinstance(o, dict) and o.get("juste") is True]
    if len(justes) != 1:
        r.erreur(ou, f"il faut une seule option juste ({len(justes)} trouvée·s)")
    vus, longueurs = set(), []
    for i, o in enumerate(opts):
        oo = f"{ou}, option {LETTRES[i]}"
        if not isinstance(o, dict):
            r.erreur(oo, "une option est un objet { texte ou code, feedback, juste? }")
            longueurs.append(0)
            continue
        inconnus = set(o) - {"texte", "code", "feedback", "juste"}
        if inconnus:
            r.erreur(oo, f"champ inconnu : {', '.join(sorted(inconnus))}")
        if "juste" in o and o["juste"] is not True:
            r.erreur(oo, "« juste » vaut true, ou n'est pas écrit")
        texte = o.get("texte", "")
        code = o.get("code", [])
        if not (isinstance(texte, str) and texte.strip()) and not (liste_de_chaines(code) and code):
            r.erreur(oo, "l'option n'a ni « texte » ni « code »")
        if "code" in o and not liste_de_chaines(code):
            r.erreur(oo, "« code » doit être une liste de lignes")
        contenu = (texte if isinstance(texte, str) else "") + "\n".join(code if liste_de_chaines(code) else [])
        if "**" in contenu or "==" in contenu.replace("== ", "").replace(" ==", "") or "<b>" in contenu.lower() or "<strong" in contenu.lower():
            r.erreur(oo, "aucune mise en avant dans une option (gras interdit)")
        if contenu in vus:
            r.erreur(oo, "option identique à une autre")
        vus.add(contenu)
        longueurs.append(len(contenu))
        fb = o.get("feedback")
        if not isinstance(fb, str) or len(fb.strip()) < FEEDBACK_MIN:
            r.erreur(oo, f"feedback manquant ou trop court (au moins {FEEDBACK_MIN} caractères qui expliquent)")
    # les noms cités en code dans les options et les feedbacks (`impressions.pop(0)`, `aux[0]`)
    # doivent exister dans le code de la question (ou dans le prélude)
    if q.get("code"):
        connus = set(re.findall(r"[A-Za-z_]\w*", "\n".join(q["code"] + list(prelude))))
        for i, o in enumerate(opts):
            if not isinstance(o, dict):
                continue
            for champ in ("texte", "feedback"):
                for seg in re.findall(r"`([^`]+)`", str(o.get(champ, ""))):
                    m = re.match(r"\s*([A-Za-z_]\w*)\s*[.\[]", seg)
                    if m and m.group(1) not in connus:
                        r.erreur(f"{ou}, option {LETTRES[i]}", f"« {m.group(1)} » ({champ}) n'existe pas dans le code de la question")
    # un renvoi « question n » vise une question déjà posée, jamais elle-même ni une suivante
    textes = list(q.get("enonce", [])) + [str(q.get("explication", ""))] + [str(o.get(k, "")) for o in opts if isinstance(o, dict) for k in ("texte", "feedback")]
    for t in textes:
        for m in re.finditer(r"[Qq]uestion (\d+)", t):
            if int(m.group(1)) >= n:
                r.erreur(ou, f"renvoi à la question {m.group(1)} : elle n'est pas encore posée (ou c'est celle-ci)")
    juste = justes[0] if len(justes) == 1 else None
    plus_longue = juste is not None and longueurs[juste] == max(longueurs) and longueurs.count(max(longueurs)) == 1

    # l'exécution
    verifs = q.get("verifications", [])
    if not isinstance(verifs, list):
        r.erreur(ou, "« verifications » doit être une liste")
        verifs = []
    if (q.get("code") or any(isinstance(o, dict) and o.get("code") for o in opts)) and not verifs and not q.get("note_verification"):
        r.erreur(ou, "du code est affiché : il faut au moins une vérification par exécution")
    if executer_code:
        for k, v in enumerate(verifs):
            ov = f"{ou}, vérification {k + 1}"
            if not isinstance(v, dict) or not liste_de_chaines(v.get("code", [])):
                r.erreur(ov, "une vérification est { code: [lignes], sortie?, erreur?, reprendre_code? }")
                continue
            if "sortie" not in v and "erreur" not in v:
                r.erreur(ov, "indique « sortie » ou « erreur » attendue")
                continue
            lignes = list(prelude)
            if v.get("reprendre_code", True):
                lignes += q.get("code", [])
            lignes += v["code"]
            sortie, err, detail = executer(lignes)
            attendue = v.get("erreur")
            if err != attendue:
                r.erreur(ov, f"erreur attendue {attendue!r}, obtenue {err!r}" + (f" ({detail.splitlines()[-1]})" if detail else ""))
            if "sortie" in v and sortie != v["sortie"]:
                r.erreur(ov, f"sortie attendue {v['sortie']!r}, obtenue {sortie!r}")
    return juste, plus_longue


def verifier_repartition(positions, r, n_attendu):
    n = len(positions)
    if None in positions or n == 0:
        return
    comptes = {l: positions.count(i) for i, l in enumerate(LETTRES)}
    bas, haut = n // 4 - 1, -(-n // 4) + 1
    for l, c in comptes.items():
        if c < bas or c > haut:
            r.erreur("répartition", f"{l} est juste {c} fois sur {n} (attendu entre {bas} et {haut})")
    serie, maxi = 1, 1
    for a, b in zip(positions, positions[1:]):
        serie = serie + 1 if a == b else 1
        maxi = max(maxi, serie)
    if maxi >= 3:
        r.erreur("répartition", f"la même lettre est juste {maxi} fois de suite")
    # un motif périodique simple (ABCDABCD…, ABAB…)
    for periode in (2, 3, 4):
        if n >= 2 * periode and all(positions[i] == positions[i % periode] for i in range(n)):
            r.erreur("répartition", f"motif périodique de longueur {periode}")
    return comptes


def verifier_cours(chemin, executer_code=True, n_questions=20):
    r = Rapport()
    try:
        with open(chemin, encoding="utf-8") as f:
            cours = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        r.erreur(chemin, f"lecture impossible : {e}")
        return r, None
    if cours.get("format") != FORMAT:
        r.erreur("cours", f"« format » doit valoir {FORMAT!r}")
    for champ in ("id", "titre", "niveau", "programme", "auteur", "licence"):
        if not isinstance(cours.get(champ), str) or not cours[champ].strip():
            r.erreur("cours", f"champ « {champ} » manquant")
    attendu_id = os.path.splitext(os.path.basename(chemin))[0]
    if cours.get("id") != attendu_id:
        r.erreur("cours", f"« id » ({cours.get('id')!r}) doit être le nom du fichier ({attendu_id!r})")
    for champ in ("criteres", "conventions"):
        if not liste_de_chaines(cours.get(champ, [])):
            r.erreur("cours", f"« {champ} » doit être une liste de phrases")
    prelude = cours.get("prelude_python", [])
    if not liste_de_chaines(prelude):
        r.erreur("cours", "« prelude_python » doit être une liste de lignes")
        prelude = []
    for ou, s in parcourir_chaines(cours):
        m = caracteres_interdits(s)
        if m:
            r.erreur(ou, f"caractère invisible ou de contrôle : {', '.join(m)}")
    diapos = cours.get("diapositives")
    if not isinstance(diapos, list) or not diapos:
        r.erreur("cours", "« diapositives » manquantes")
        return r, cours
    questions, ids = [], set()
    for i, d in enumerate(diapos):
        ou = f"diapositive {i + 1}"
        if not isinstance(d, dict) or d.get("type") not in TYPES_DIAPO:
            r.erreur(ou, f"type inconnu (permis : {', '.join(sorted(TYPES_DIAPO))})")
            continue
        if d["type"] == "question":
            questions.append(d)
            if d.get("id") in ids:
                r.erreur(ou, f"identifiant en double : {d.get('id')}")
            ids.add(d.get("id"))
        elif d["type"] == "partie":
            if not isinstance(d.get("titre"), str) or not d["titre"].strip():
                r.erreur(ou, "une partie a un titre")
        elif d["type"] == "classe":
            if not isinstance(d.get("question"), str) or not d["question"].strip():
                r.erreur(ou, "une question à la classe a une « question »")
            for champ in ("pistes", "texte"):
                if champ in d and not liste_de_chaines(d[champ]):
                    r.erreur(ou, f"« {champ} » : une liste de phrases")
            if "code" in d and not liste_de_chaines(d["code"]):
                r.erreur(ou, "« code » doit être une liste de lignes")
            if "schema" in d:
                verifier_schema(d["schema"], ou, r)
        elif d["type"] == "humour":
            if not isinstance(d.get("titre"), str) or not liste_de_chaines(d.get("lignes", [])) or not d.get("lignes"):
                r.erreur(ou, "une diapositive d'humour a un « titre » et des « lignes »")
        elif d["type"] == "notion":
            if not isinstance(d.get("titre"), str) or not d["titre"].strip():
                r.erreur(ou, "une notion a un titre")
            t = d.get("texte", [])
            if not liste_de_chaines(t) or not t:
                r.erreur(ou, "« texte » : une liste de 1 à 3 phrases courtes")
            else:
                if len(t) > TEXTE_NOTION_MAX:
                    r.avert(ou, f"{len(t)} puces : peu de texte, 3 au plus")
                for p in t:
                    if len(p) > PUCE_MAX:
                        r.avert(ou, f"puce de {len(p)} caractères : à raccourcir")
            if "schema" in d:
                verifier_schema(d["schema"], ou, r)
                if executer_code:
                    verifier_schema_execution(d["schema"], prelude, ou + ", schéma", r)
            if "code" in d and not liste_de_chaines(d["code"]):
                r.erreur(ou, "« code » doit être une liste de lignes")
            if "consigne" in d and not liste_de_chaines(d["consigne"]):
                r.erreur(ou, "« consigne » : une liste de consignes d'observation")
    if diapos and diapos[0].get("type") != "titre":
        r.avert("diapositive 1", "un cours commence d'habitude par une diapositive « titre »")
    if n_questions and len(questions) != n_questions:
        r.erreur("cours", f"{len(questions)} questions au lieu de {n_questions}")
    positions, longues = [], 0
    for n, q in enumerate(questions, 1):
        j, pl = verifier_question(q, n, prelude, r, executer_code)
        positions.append(j)
        longues += 1 if pl else 0
    comptes = verifier_repartition(positions, r, n_questions)
    if questions and longues / len(questions) > 0.4:
        r.erreur("répartition", f"la bonne réponse est la plus longue dans {longues} questions sur {len(questions)} : elle se repère")
    elif questions and longues / len(questions) > 0.25:
        r.avert("répartition", f"la bonne réponse est la plus longue dans {longues} questions sur {len(questions)}")
    return r, {"cours": cours, "questions": questions, "positions": positions, "comptes": comptes, "longues": longues}


def main(args):
    executer_code = "--sans-execution" not in args
    fichiers = [a for a in args if not a.startswith("--")]
    if "--tous" in args:
        racine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cours")
        fichiers += sorted(os.path.join(racine, f) for f in os.listdir(racine) if f.endswith(".json"))
    if not fichiers:
        print(__doc__)
        return 2
    total = 0
    for chemin in fichiers:
        r, info = verifier_cours(chemin, executer_code)
        print(f"== {chemin}")
        if info and info.get("questions"):
            for n, (q, p) in enumerate(zip(info["questions"], info["positions"]), 1):
                lettre = LETTRES[p] if p is not None else "?"
                print(f"  {n:2d}. {lettre}  {q.get('nom', '')}")
            if info.get("comptes"):
                print("  Bonnes réponses : " + ", ".join(f"{l} {c}" for l, c in info["comptes"].items())
                      + f" ; la plus longue : {info['longues']} fois")
        for a in r.avertissements:
            print("  avertissement · " + a)
        for e in r.erreurs:
            print("  ERREUR · " + e)
        print("  " + ("conforme" if not r.erreurs else f"{len(r.erreurs)} erreur(s)")
              + ("" if executer_code else " (sans exécution du code)"))
        total += len(r.erreurs)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
