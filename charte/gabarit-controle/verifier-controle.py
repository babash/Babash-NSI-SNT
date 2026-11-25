#!/usr/bin/env python3
"""Vérifier un sujet de contrôle écrit avec la classe LaTeX `exam` (le format Overleaf de l'enseignant).

Pour chaque question à laquelle l'élève répond (une \\question sans \\part, ou une \\part, ou une \\subpart),
l'outil signale :
  - les demandes multiples (« écris, explique et teste » dans la même question) ;
  - les fonctions entières à écrire ;
  - les questions sans points, ou dont les points ne sont pas répartis entre les parties ;
  - les questions qui dépendent d'une réponse précédente ;
  - le temps estimé pour un·e élève moyen·ne qui écrit à la main, relecture comprise.
Puis il compare le total au temps annoncé et au nombre de fonctions permis (règle : LISEZMOI.md du même dossier).

Usage :
    python3 -I charte/gabarit-controle/verifier-controle.py sujet.tex [autre.tex …] [--duree 2h] [--detail] [--strict]

  --duree   la durée annoncée, si elle n'est pas dans \\date{… Durée : 2h} du fichier (2h, 1h30, 45min, 90) ;
  --detail  une ligne par question (sinon : le résumé et les alertes) ;
  --strict  code de sortie 1 s'il reste une alerte (pour un contrôle automatique).

Annotations, dans le .tex, à l'intérieur d'une question (commentaires LaTeX, invisibles dans le PDF) :
  %! fonction          compter cette question comme une fonction entière à écrire ;
  %! pas-fonction      ne pas la compter (par exemple « Écrire l'instruction qui… ») ;
  %! min=6             imposer le temps estimé (en minutes) ;
  %! une-demande       la question demande une seule chose (le compteur s'est trompé) : dire pourquoi après.
  %! bac               exercice officiel repris tel quel : ses alertes de forme sont affichées, sans compter dans --strict.

Le modèle de temps est volontairement simple ; il se lit dans TEMPS ci-dessous. Il a été réglé en refaisant
les contrôles comme un·e élève (réponses écrites à la main, voir LISEZMOI.md, « Calibrage »).
"""
import argparse
import math
import re
import sys
import unicodedata

# Minutes de travail pour une demande, selon son type (élève moyen·ne, à la main, hors lecture).
TEMPS = {
    "fonction": 8.0,      # écrire une fonction ou une méthode entière (8 lignes environ)
    "programme": 6.0,     # écrire un programme de quelques lignes (pas une fonction)
    "instruction": 1.5,   # écrire une ou deux instructions (créer un objet, un appel)
    "completer": 2.5,     # compléter un code à trous (sur le sujet)
    "prevoir": 2.5,       # qu'affiche, que renvoie, que contient, état après exécution
    "tracer": 4.0,        # dessiner, tracer, tableau d'avancement, schéma
    "expliquer": 3.0,     # expliquer, justifier (plusieurs phrases)
    "phrase": 1.5,        # justifier en une phrase, dire pourquoi en une phrase
    "calculer": 4.0,      # déterminer, calculer, en déduire, dénombrer
    "corriger": 2.0,      # corriger une ligne fautive
    "recopier": 6.0,      # recopier un code sur la copie, puis le compléter
    "donner": 1.5,        # donner, citer, nommer, quel est… (réponse courte)
    "choisir": 1.0,       # cocher, entourer, choisir parmi des options
}
LECTURE_MOTS_MIN = 100     # mots lus par minute (lecture attentive, français langue seconde pour beaucoup)
LECTURE_CODE_LIGNE = 0.15  # minutes par ligne de code à lire et comprendre
RELECTURE = 0.10           # relecture : 10 % en plus

# Les demandes. Deux familles :
#  - les VERBES de consigne (infinitif du bac, impératif du tutoiement, « vous ») ne comptent qu'en tête de phrase
#    ou après « et », « puis », une virgule, « : » ou « ; » : « Écris… et explique… » fait deux demandes,
#    mais « un dictionnaire qui associe… » n'en fait aucune ;
#  - les tournures INTERROGATIVES (« qu'affiche », « quel », « pourquoi »…) comptent partout.
V = r"(?:er|e|es|ez)"
VERBES = [
    (r"(?:re)?(?:e|é)cri(?:re|s|vez)\s+(?:une|la|les|deux|trois|le code (?:de|d'une|des?)\s+(?:la\s+)?)\s*(?:fonction|m(?:e|é)thode)s?", "fonction"),
    (r"propos" + V + r"\s+une\s+(?:fonction|m(?:e|é)thode)", "fonction"),
    (r"impl(?:e|é)ment" + V + r"\s+(?:une|la)\s+(?:fonction|m(?:e|é)thode)", "fonction"),
    (r"(?:e|é)cri(?:re|s|vez)\s+(?:un|le|deux)\s+(?:seul\s+)?(?:programme|code|boucles?|script)", "programme"),
    (r"(?:e|é)cri(?:re|s|vez)\s+(?:l'|les\s+|une\s+|la\s+|un\s+)?(?:instructions?|appel|ligne|expression|requ(?:e|ê)te)", "instruction"),
    (r"(?:e|é)cri(?:re|s|vez)\b", "instruction"),
    (r"donn" + V + r"\s+(?:le code|l'instruction|les instructions)", "instruction"),
    (r"recopi" + V + r"\s+et\s+compl(?:e|é|è)t" + V, "recopier"),
    (r"compl(?:e|é|è)t" + V, "completer"),
    (r"pr(?:e|é)(?:dire|dis|disez|voi[rs]|voyez)|indiqu" + V + r" ce que", "prevoir"),
    (r"dessin" + V + r"|trac" + V + r"|repr(?:e|é)sent" + V + r"|d(?:e|é)roul" + V + r"|fai(?:re|s|tes) le tableau|remplis|rempli(?:r|ssez)", "tracer"),
    (r"(?:justifi|expliqu)" + V + r"[^.?!;]{0,25}en une phrase", "phrase"),
    (r"expliqu" + V + r"|justifi" + V, "expliquer"),
    (r"d(?:e|é)termin" + V + r"|calcul" + V + r"|en d(?:e|é)dui(?:re|s|sez)|compt" + V + r"\b", "calculer"),
    (r"corrig" + V + r"|rectifi" + V + r"|trouv" + V + r" l'erreur", "corriger"),
    (r"coch" + V + r"|choisi(?:r|s|ssez)|entour" + V + r"|soulign" + V + r"|associ" + V + r"|reli(?:er|e|ez)", "choisir"),
    (r"donn" + V + r"|cit" + V + r"|nomm" + V + r"|indiqu" + V + r"|pr(?:e|é)cis" + V + r"|dire\b|dis\b|r(?:e|é)pond(?:re|s|ez)", "donner"),
    (r"test" + V + r"\b|ex(?:e|é)cut" + V + r" (?:la|le|les|ta|ton)", "programme"),
]
INTERROGATIFS = [
    (r"qu(?:'|e |’)(?:affiche|renvoie|retourne|contient|vaut|obtient)|quelle (?:est la )?valeur", "prevoir"),
    (r"sch(?:e|é)ma|tableau d'avancement", "tracer"),
    (r"en une phrase", "phrase"),
    (r"pourquoi|comment\b", "expliquer"),
    (r"combien", "calculer"),
    (r"quel(?:le)?s?\b|que signifie|que d(?:e|é)signe|(?:a|à) quoi sert|lequel|laquelle|qu(?:'|e )est-ce", "donner"),
]
VERBES_DONNER = r"donn(?:er|e|es|ez)|cit(?:er|e|ez)|nomm(?:er|e|ez)|indiqu(?:er|e|ez)|dire\b"
DEBUT = r"(?:(?<=^)|(?<=\bet )|(?<=\bpuis )|(?<=, )|(?<=: )|(?<=; )|(?<=\) ))"
VERBES = [(re.compile(DEBUT + "(?:" + m + ")", re.I), t) for m, t in VERBES] + \
         [(re.compile(r"(?<![\w'])(?:" + m + ")", re.I), t) for m, t in INTERROGATIFS]
DEPEND = re.compile(r"(question|fonction|m(?:e|é)thode)s?\s+pr(?:e|é)c(?:e|é)dente|en utilisant (?:la|les|le) (?:fonction|r(?:e|é)sultat|question)|(?:a|à) l'aide (?:de la|des) (?:question|fonction)s? pr|avec (?:la|les) fonctions? (?:pr(?:e|é)c(?:e|é)dente|ci-dessus)", re.I)
CODE_ENV = re.compile(r"\\begin\{(lstlisting|minted|verbatim|Verbatim)\}(?:\[[^\]]*\])?(?:\{[^}]*\})?(.*?)\\end\{\1\}", re.S)
MARQUE = re.compile(r"\\(question|part|subpart|subsubpart)(?![a-zA-Z])\s*(\[[^\]]*\])?")
NIVEAU = {"question": 0, "part": 1, "subpart": 2, "subsubpart": 3}


def points(arg):
    if not arg:
        return None
    s = arg.strip("[]").replace("\\half", ".5").replace(",", ".").strip()
    s = re.sub(r"^(\d+)\.5$", r"\1.5", s)
    if s.startswith("."):
        s = "0" + s
    try:
        return float(s)
    except ValueError:
        return None


def nettoyer(tex):
    """Texte lisible d'un morceau de LaTeX (sans le code, compté à part)."""
    t = CODE_ENV.sub(" ", tex)
    t = re.sub(r"(?<!\\)%.*", " ", t)
    t = re.sub(r"\\lstinline\s*(.)(.*?)\1", r" \2 ", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}(\[[^\]]*\])?(\{[^}]*\})?", " ", t)
    t = re.sub(r"\\(?:textit|textbf|texttt|emph|code|underline|text|mbox|og|fg)\s*\{([^{}]*)\}", r" \1 ", t)
    t = re.sub(r"\\(?:vspace|hspace|includegraphics|label|ref|fillwithlines|fillwithdottedlines|makeemptybox)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = t.replace("\\_", "_").replace("\\%", "%").replace("\\&", "&").replace("~", " ")
    t = re.sub(r"\\[a-zA-Z]+\*?", " ", t)
    t = re.sub(r"[{}$\\]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def lignes_code(tex):
    n = 0
    for m in CODE_ENV.finditer(tex):
        n += len([l for l in m.group(2).splitlines() if l.strip()])
    return n


def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def demandes(texte):
    """Liste des demandes d'une question : (type, extrait). Une phrase peut en contenir plusieurs (« écris et explique »)."""
    res = []
    phrases = [p.strip() for p in re.split(r"(?<=[.?!;:])\s+", texte)]
    for ph in phrases:
        if not ph.strip():
            continue
        # Une phrase d'information (« Par exemple… », « On rappelle… », « Indice : ») ne demande rien.
        if re.match(r"\s*(par exemple|on rappelle|on consid[eè]re|on dispose|on suppose|on appelle|on dit|on ex[eé]cute|indice|rappel|remarque|attention|exemples?\s*:)", ph, re.I):
            continue
        trouves = []
        for rx, typ in VERBES:
            for m in rx.finditer(ph):
                if any(m.start() < b and a < m.end() for a, b, _ in trouves):
                    continue
                trouves.append((m.start(), m.end(), typ))
        trouves.sort()
        # Un mot interrogatif sans verbe (« Quelle est la hauteur ? ») : une demande « donner ».
        if not trouves and ph.rstrip().endswith("?"):
            trouves = [(0, 0, "donner")]
        # « Choisis … et justifie en une phrase » : un seul bloc de réponse (une ligne), compté comme une demande.
        types = [t for _, _, t in trouves]
        if "phrase" in types and len(types) > 1:
            trouves = [x for x in trouves if x[2] != "phrase"]
            trouves[-1] = (trouves[-1][0], trouves[-1][1], trouves[-1][2] + "+phrase")
        # Un mot interrogatif dans une phrase qui a déjà un verbe de consigne (« Expliquer à quoi sert… »,
        # « Déterminer quelle… ») ne fait pas une demande de plus.
        if any(t not in ("donner",) and not t.startswith("donner") for _, _, t in trouves) and any(t == "donner" for _, _, t in trouves):
            verbes_tete = [x for x in trouves if x[2] != "donner" or re.match(DEBUT + "(?:" + VERBES_DONNER + ")", ph[x[0]:], re.I)]
            trouves = verbes_tete or trouves
        # Plusieurs mots interrogatifs du même type dans une phrase descriptive ne font qu'une demande
        # (« quel est le type de quelle variable ») : on garde les verbes distincts.
        vus, garde = set(), []
        for a, b, t in trouves:
            cle = (t, ph[a:b].lower()[:4])
            if t == "donner" and any(x[2] == "donner" for x in garde):
                continue
            if cle in vus:
                continue
            vus.add(cle)
            garde.append((a, b, t))
        for a, b, t in garde:
            res.append((t, ph.strip()[:70]))
    # Un QCM, un vrai ou faux, un « relier » : la question posée et « Cocher la bonne réponse » ne font qu'une
    # réponse (la case cochée) ; les options proposées ne sont pas des demandes.
    if any(t.startswith("choisir") for t, _ in res):
        res = [x for x in res if not x[0].startswith("donner")]
        premiers = [x for x in res if x[0].startswith("choisir")][:1]
        res = premiers + [x for x in res if not x[0].startswith("choisir")]
    # « … pile ou file ? Justifier en une phrase. » : choisir puis justifier en une phrase = un seul bloc de réponse.
    if len(res) > 1 and any(t == "phrase" for t, _ in res):
        fusion = []
        for t, e in res:
            if t == "phrase" and fusion and "+phrase" not in fusion[-1][0]:
                fusion[-1] = (fusion[-1][0] + "+phrase", fusion[-1][1])
            else:
                fusion.append((t, e))
        res = fusion
    return res


def temps_demande(t):
    base = t.split("+")[0]
    return TEMPS.get(base, 1.5) + (TEMPS["phrase"] if "+phrase" in t else 0)


def duree_minutes(s):
    if not s:
        return None
    s = sans_accents(s.lower()).replace(" ", "")
    m = re.search(r"(\d+)h(\d+)?", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2) or 0)
    m = re.search(r"(\d+)(?:min|minutes?|mn)", s)
    if m:
        return int(m.group(1))
    if s.isdigit():
        return int(s)
    return None


def analyser(chemin, duree_option=None):
    src = open(chemin, encoding="utf-8").read()
    corps = src.split("\\begin{document}", 1)[-1]
    duree_txt = duree_option
    if not duree_txt:
        m = re.search(r"Dur(?:é|e)e\s*:?\s*([0-9]+\s*h\s*[0-9]*(?:\s*min)?|[0-9]+\s*min(?:utes)?)", sans_accents(src).replace("Duree", "Durée"), re.I) or \
            re.search(r"Dur(?:é|e)e\s*:?\s*([0-9]+\s*h\s*[0-9]*|[0-9]+\s*min)", src, re.I)
        duree_txt = m.group(1) if m else None
    duree = duree_minutes(duree_txt) if duree_txt else None

    marques = list(MARQUE.finditer(corps))
    items = []
    debut_q = corps.find("\\begin{questions}")
    contexte_prec = corps[:marques[0].start()] if marques else ""
    if debut_q >= 0 and marques:
        contexte_prec = corps[debut_q:marques[0].start()]
    # Les exercices : les \section numérotées (les \section* « Consignes », « Barème » ne comptent pas).
    sections = [m.start() for m in re.finditer(r"\\section\s*\{", corps)]
    for i, m in enumerate(marques):
        fin = marques[i + 1].start() if i + 1 < len(marques) else len(corps)
        bloc = corps[m.end():fin]
        # Ce qui suit un titre de partie (\section…) n'appartient plus à la question : c'est le contexte de la suivante.
        coupe = re.search(r"\\(?:sub)*section\*?\s*\{|\\end\{questions\}", bloc)
        apres = ""
        if coupe:
            bloc, apres = bloc[:coupe.start()], bloc[coupe.start():]
        items.append(dict(niveau=NIVEAU[m.group(1)], pts=points(m.group(2)), bloc=bloc, apres=apres, debut=m.start(),
                          section=sum(1 for x in sections if x < m.start())))
    # Numérotation (comme la classe exam : 1, a, i) et feuilles.
    qn = pn = sn = 0
    for i, it in enumerate(items):
        if it["niveau"] == 0:
            qn += 1; pn = sn = 0; it["num"] = f"{qn}"
        elif it["niveau"] == 1:
            pn += 1; sn = 0; it["num"] = f"{qn}{chr(96 + pn)}"
        else:
            sn += 1; it["num"] = f"{qn}{chr(96 + pn)}{['i','ii','iii','iv','v','vi','vii','viii'][min(sn,8)-1]}"
        suiv = items[i + 1] if i + 1 < len(items) else None
        it["feuille"] = not (suiv and suiv["niveau"] > it["niveau"])
        it["parent"] = None
        for j in range(i - 1, -1, -1):
            if items[j]["niveau"] < it["niveau"]:
                it["parent"] = j
                break

    alertes = []
    lignes = []
    total_min = 0.0
    fonctions = 0
    total_pts = 0.0
    for i, it in enumerate(items):
        bloc = it["bloc"]
        # Le texte d'une question qui a des parties : son énoncé, lu une fois (compté dans sa première partie).
        texte = nettoyer(bloc)
        annot = re.findall(r"%!\s*([\w=\-.]+)", bloc)
        it["bac"] = "bac" in annot or (it["parent"] is not None and items[it["parent"]].get("bac"))
        lecture = len(texte.split()) / LECTURE_MOTS_MIN + lignes_code(bloc) * LECTURE_CODE_LIGNE
        if not it["feuille"]:
            it["lecture_parent"] = lecture
            it["dem_parent"] = demandes(texte)
            continue
        dem = demandes(texte)
        if it["parent"] is not None:
            p = items[it["parent"]]
            if not p.get("lu"):
                lecture += p.get("lecture_parent", 0)
                p["lu"] = True
            if not dem:
                dem = p.get("dem_parent", [])[:1]
        if not dem:
            dem = [("donner", texte[:70])]
        if "une-demande" in annot:
            dem = dem[:1]
        est_fonction = any(t.startswith("fonction") for t, _ in dem)
        if "fonction" in annot:
            est_fonction = True
        if "pas-fonction" in annot:
            est_fonction = False
            dem = [("instruction" if t.startswith("fonction") else t, e) for t, e in dem]
        if est_fonction and not any(t.startswith("fonction") for t, _ in dem):
            dem = [("fonction", dem[0][1])] + dem[1:]
        travail = sum(temps_demande(t) for t, _ in dem)
        mins = [float(a.split("=")[1]) for a in annot if a.startswith("min=")]
        minutes = mins[0] if mins else (lecture + travail)
        total_min += minutes
        fonctions += 1 if est_fonction else 0
        pts = it["pts"]
        if pts is None and it["parent"] is not None:
            p = items[it["parent"]]
            if p["pts"] is not None:
                fr = [x for x in items if x["parent"] == it["parent"]]
                if not p.get("alerte_pts"):
                    alertes.append((it["num"][:-1] or it["num"], "barème", f"{p['pts']:g} pt pour {len(fr)} parties : donner les points de chaque partie", it["bac"]))
                    p["alerte_pts"] = True
                pts = p["pts"] / len(fr)
        if pts is None:
            alertes.append((it["num"], "barème", "question sans points", it["bac"]))
            pts = 0
        total_pts += pts
        if est_fonction:
            if not re.search(r"^\s*def \w+\(", "\n".join(m.group(2) for m in CODE_ENV.finditer(bloc)), re.M):
                alertes.append((it["num"], "fonction", "fonction entière non cadrée : donner la signature, la docstring et un exemple dans le cadre de réponse", it["bac"]))
            if it["section"] < len(sections):
                alertes.append((it["num"], "fonction", "fonction entière hors du dernier exercice : la mettre en fin de sujet, ou la transformer en code à compléter", it["bac"]))
        nd = len(dem)
        if nd > 1:
            alertes.append((it["num"], "à tiroirs", f"{nd} demandes : " + " / ".join(t for t, _ in dem) + " ; découper en a, b, c…", it["bac"]))
        if DEPEND.search(texte):
            alertes.append((it["num"], "dépendance", "s'appuie sur une réponse précédente : donner ce qu'il faut pour la faire sans elle", it["bac"]))
        if re.search(r"\\begin\{(enumerate|itemize)\}", bloc) and re.search(r"pour chaque|pour chacun|pour chacune", texte, re.I):
            alertes.append((it["num"], "à tiroirs", "« pour chaque » + liste : une partie par élément, ou un tableau à remplir", it["bac"]))
        if pts and minutes / pts > 12:
            alertes.append((it["num"], "barème", f"{minutes:.0f} min pour {pts:g} pt : peu payé", it["bac"]))
        lignes.append((it["num"], pts, nd, "F" if est_fonction else "", minutes, " / ".join(t for t, _ in dem), "bac" if it["bac"] else ""))
        it["pts_note"], it["types"] = pts, [t for t, _ in dem]

    # Le début : une partie « questions de cours courtes » de 4 ou 5 points (choix de l'enseignant du 25/11).
    premiers = [it for it in items if it["feuille"] and it.get("section") == 1 and "pts_note" in it]
    if sections and duree and duree > 30:
        pts1 = sum(it["pts_note"] for it in premiers)
        longs = [it["num"] for it in premiers if any(t.split("+")[0] in ("fonction", "programme", "tracer", "calculer", "recopier") for t in it["types"])]
        if not (4 <= pts1 <= 5) or longs:
            alertes.append(("1", "début", f"le premier exercice ({pts1:g} pt) doit être des questions de cours courtes (vocabulaire, vrai ou faux, QCM, relier), 4 ou 5 points"
                            + (f" ; questions longues : {', '.join(longs)}" if longs else ""), False))
    total_min *= 1 + RELECTURE
    return dict(chemin=chemin, duree=duree, lignes=lignes, alertes=alertes, minutes=total_min,
                fonctions=fonctions, points=total_pts, questions=len(lignes))


def fonctions_permises(duree):
    """Fonctions entières à écrire : 1 ou 2, cadrées, en fin de sujet (choix de l'enseignant du 25/11) ; aucune en 30 min."""
    if duree is None:
        return None
    if duree <= 30:
        return 0
    return 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fichiers", nargs="+")
    ap.add_argument("--duree")
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    code = 0
    for f in a.fichiers:
        r = analyser(f, a.duree)
        print(f"== {f}")
        if a.detail:
            print(f"  {'Q':<6}{'pts':>5} {'dem.':>4} {'fct':>3} {'min':>5}  types")
            for num, pts, nd, fct, mins, types, bac in r["lignes"]:
                print(f"  {num:<6}{pts:>5.2f} {nd:>4} {fct:>3} {mins:>5.1f}  {types}{'  [bac]' if bac else ''}")
        tiroirs = sum(1 for x in r["lignes"] if x[2] > 1)
        print(f"  {r['questions']} questions notées, {r['points']:g} points, {tiroirs} à tiroirs, {r['fonctions']} fonction(s) entière(s) à écrire")
        d = r["duree"]
        print(f"  temps estimé (élève moyen·ne, relecture comprise) : {r['minutes']:.0f} min"
              + (f" ; annoncé : {d} min ({100 * r['minutes'] / d:.0f} %)" if d else " ; durée annoncée introuvable (--duree)"))
        bloquantes = 0
        fp = fonctions_permises(d)
        if fp is not None and r["fonctions"] > fp:
            print(f"  ALERTE fonctions : {r['fonctions']} fonctions entières pour {d} min (au plus {fp})")
            bloquantes += 1
        if d and r["minutes"] > d * 1.0:
            print(f"  ALERTE durée : {r['minutes']:.0f} min estimées pour {d} min annoncées")
            bloquantes += 1
        for num, cat, msg, bac in r["alertes"]:
            print(f"  {'(bac) ' if bac else ''}{cat} — question {num} : {msg}")
            if not bac:
                bloquantes += 1
        if bloquantes == 0:
            print("  aucune alerte")
        elif a.strict:
            code = 1
    return code


if __name__ == "__main__":
    sys.exit(main())
