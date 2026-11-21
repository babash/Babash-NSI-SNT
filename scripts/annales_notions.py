#!/usr/bin/env python3
"""Classe les exercices des annales du bac NSI dans les 22 chapitres des fiches de révision (T116).

Entrée : donnees/annales/annales-bac-nsi.json (le Bibliothécaire, T104), où chaque exercice a déjà
  - « resume » : l'en-tête « Cet exercice porte sur… » recopié du sujet (ou un résumé de ses thèmes) ;
  - « notions » : des notions du thésaurus (donnees/referentiels/notions.json), déduites de cet en-tête.
Sortie : donnees/annales/notions-par-exercice.json (l'Architecte), lu par la page bibliotheque/annales/.

Un exercice entre dans un chapitre par deux indices, notés dans « indices » :
  - « notion … » : une notion du thésaurus que le chapitre couvre (ou une notion plus étroite) ;
  - « mot … » : un mot de l'en-tête propre au chapitre (accents et majuscules ignorés).
Les faux amis (« tri topologique » pour les tris, « arbre binaire » pour le binaire, « tri par insertion »
pour le SQL…) sont retirés avant la recherche des mots. Une notion seule, sans mot du chapitre, alors
qu'un faux ami est présent, ne classe pas l'exercice : elle va dans « a_verifier », avec sa raison.
Rien n'est inventé : un exercice sans aucun indice reste « à classer ».

Chaque classement a « verifie »: false. Pour corriger un exercice à la main, dans le fichier de sortie :
  "2024-asie-j1#2": {"chapitres": ["graphes", "piles-files", "recursivite"], "verifie": true}
(les identifiants des chapitres sont dans « chapitres », en tête du fichier), puis relancer le script.
Il garde alors cet exercice tel quel à chaque nouvelle exécution, refuse un chapitre inconnu et signale
un exercice vérifié qui a disparu des annales (« verifies_disparus »).

Usage :
  python3 scripts/annales_notions.py              écrit donnees/annales/notions-par-exercice.json
  python3 scripts/annales_notions.py --verifier   vérifie que le fichier est à jour (code 1 sinon)
  python3 scripts/annales_notions.py --bilan      affiche le nombre d'exercices par chapitre
Python 3 standard, sans dépendance.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANNALES = "donnees/annales/annales-bac-nsi.json"
NOTIONS = "donnees/referentiels/notions.json"
SORTIE = "donnees/annales/notions-par-exercice.json"
FICHES = "https://babash.github.io/fiches-nsi/fiches/"

# Les 22 chapitres des fiches de révision (dépôt babash/fiches-nsi, dossier content/), dans l'ordre
# des fiches : SNT et première, puis terminale. « fiche » : le nom de la fiche en ligne.
# « notions » : identifiants du thésaurus ; une notion plus étroite (« donnees.bdd.sql.jointure » pour
# « donnees.bdd ») compte aussi. « mots » : expressions régulières sur l'en-tête sans accents, en
# minuscules. « faux_amis » : retirés de l'en-tête avant la recherche des mots.
CHAPITRES = [
    dict(id="variables", titre="Les variables et les opérateurs", fiche="variable", niveau="1re",
         programme="nsi-1re-2019.langages.constructions-elementaires",
         notions=["prog.variable", "prog.affectation", "prog.arithmetique", "prog.type"],
         mots=[r"\bvariables?\b", r"\baffectations?\b", r"operateurs? arithmetiques?", r"division euclidienne"],
         faux_amis=[]),
    dict(id="conditions-boucles", titre="Les conditions et les boucles", fiche="ficheSNT", niveau="SNT, 1re",
         programme="nsi-1re-2019.langages.constructions-elementaires",
         notions=["prog.controle", "prog.comparaison"],
         mots=[r"\bboucles?\b", r"\bwhile\b", r"instructions? conditionnelles?", r"\bconditionnelles?\b"],
         faux_amis=[]),
    dict(id="fonctions", titre="Les fonctions", fiche="fonctions", niveau="1re",
         programme="nsi-1re-2019.langages.specification",
         notions=["prog.fonction", "prog.specification", "prog.test", "prog.debogage"],
         mots=[r"\bfonctions?\b", r"\bassert(ions?)?\b", r"\bspecifications?\b", r"\bdebogage\b",
               r"mise au point", r"\bbugs?\b", r"\btests?\b"],
         faux_amis=[r"fonctions? de hachage", r"fonctions? d'agregation"]),
    dict(id="chaines", titre="Les chaînes de caractères", fiche="chaines-de-caracteres", niveau="1re",
         programme="nsi-1re-2019.types-construits",
         notions=["donnees.chaine"],
         mots=[r"chaines? de caracteres"],
         # dans un graphe, une « chaîne » est un chemin
         faux_amis=[]),
    dict(id="listes", titre="Les tableaux (listes)", fiche="liste", niveau="1re",
         programme="nsi-1re-2019.types-construits.tableaux",
         notions=["donnees.tableau"],
         mots=[r"\blistes?\b", r"\btableaux?\b", r"sous-listes?", r"\btranches?\b", r"listes? de listes"],
         faux_amis=[r"listes? d'adjacence", r"listes? chainees?", r"matrices? d'adjacence"]),
    dict(id="tuples", titre="Les p-uplets (tuples)", fiche="tuple", niveau="1re",
         programme="nsi-1re-2019.types-construits",
         notions=["donnees.tuple"],
         mots=[r"\btuples?\b", r"\bp-uplets?\b", r"\bn-uplets?\b"],
         faux_amis=[]),
    dict(id="dictionnaires", titre="Les dictionnaires", fiche="dict", niveau="1re",
         programme="nsi-1re-2019.types-construits.dictionnaires",
         notions=["donnees.dictionnaire"],
         mots=[r"\bdictionnaires?\b"],
         faux_amis=[]),
    dict(id="parcours", titre="Le parcours séquentiel d'un tableau", fiche="fonction-usuelles", niveau="1re",
         programme="nsi-1re-2019.algorithmique.parcours-sequentiel",
         notions=["algo.parcours", "algo.recherche.sequentielle"],
         mots=[r"parcours sequentiel", r"recherche sequentielle", r"recherche (d'un|du) (maximum|minimum)",
               r"\boccurrences?\b", r"\bmoyennes?\b"],
         faux_amis=[]),
    dict(id="tris", titre="Les tris par sélection et par insertion", fiche="tris", niveau="1re",
         programme="nsi-1re-2019.algorithmique.tris",
         notions=["algo.tri.insertion", "algo.tri.selection", "algo.tri.bulles", "algo.tri"],
         exclues=["algo.tri.fusion"],
         mots=[r"\btris?\b", r"tri par \w+", r"algorithmes? de tri", r"\btrier\b"],
         faux_amis=[r"tri topologique", r"tri fusion"]),
    dict(id="dichotomie", titre="La recherche dichotomique", fiche="dichotomie", niveau="1re",
         programme="nsi-1re-2019.algorithmique.dichotomie",
         notions=["algo.recherche.dichotomique"],
         mots=[r"dichotomi\w*"],
         faux_amis=[]),
    dict(id="gloutons", titre="Les algorithmes gloutons", fiche="gloutons", niveau="1re",
         programme="nsi-1re-2019.algorithmique.gloutons",
         notions=["algo.glouton"],
         mots=[r"glouton\w*"],
         faux_amis=[]),
    dict(id="binaire", titre="L'écriture binaire et hexadécimale", fiche="binaire", niveau="1re",
         programme="nsi-1re-2019.types-de-base.entiers-base-b",
         notions=["donnees.binaire", "donnees.entiers-relatifs"],
         mots=[r"\bbinaires?\b", r"hexadecima\w*", r"\bbits?\b", r"\boctets?\b", r"complement a deux"],
         faux_amis=[r"arbres? binaires?( de recherche)?", r"recherche binaire"]),
    dict(id="recursivite", titre="La récursivité", fiche="recursivite", niveau="Tle",
         programme="nsi-tle-2019.langages.recursivite",
         notions=["prog.recursivite"],
         mots=[r"recursi\w*"],
         faux_amis=[]),
    dict(id="tri-fusion", titre="Diviser pour régner : le tri fusion", fiche="diviser-pour-regner", niveau="Tle",
         programme="nsi-tle-2019.algorithmique.diviser-pour-regner",
         notions=["algo.tri.fusion", "algo.diviser-regner"],
         mots=[r"tri fusion", r"diviser pour regner", r"\bfusion\b"],
         faux_amis=[]),
    dict(id="poo", titre="La programmation orientée objet", fiche="poo", niveau="Tle",
         programme="nsi-tle-2019.structures-de-donnees.poo",
         notions=["prog.poo"],
         mots=[r"programmation (orientee )?objets?", r"\bpoo\b", r"\bclasses?\b", r"constructeurs?",
               r"orientee objets?"],
         faux_amis=[]),
    dict(id="arbres", titre="Les arbres binaires", fiche="arbres", niveau="Tle",
         programme="nsi-tle-2019.structures-de-donnees.arbres",
         notions=["donnees.arbre", "algo.arbre"],
         mots=[r"\barbres?\b", r"\babr\b"],
         faux_amis=[]),
    dict(id="abr", titre="Les arbres binaires de recherche", fiche="abr", niveau="Tle",
         programme="nsi-tle-2019.algorithmique.arbres-binaires",
         notions=["donnees.arbre.abr"],
         mots=[r"arbres? binaires? de recherche", r"\babr\b"],
         faux_amis=[]),
    dict(id="graphes", titre="Les graphes", fiche="graphes", niveau="Tle",
         programme="nsi-tle-2019.structures-de-donnees.graphes",
         notions=["donnees.graphe", "algo.graphe"],
         mots=[r"\bgraphes?\b", r"listes? d'adjacence", r"matrices? d'adjacence", r"bellman-ford", r"dijkstra"],
         # un parcours en largeur ou en profondeur peut être celui d'un arbre
         faux_amis=[r"\barbres?\b"]),
    dict(id="sql", titre="Les bases de données et SQL", fiche="sql", niveau="Tle",
         programme="nsi-tle-2019.bases-de-donnees.sql",
         notions=["donnees.bdd"],
         mots=[r"\bsql\b", r"bases? de donnees", r"\bselect\b", r"\bjoin\b", r"\bsgbd\b", r"relationnel\w*",
               r"cles? (primaires?|etrangeres?)", r"\bupdate\b", r"\bdelete\b", r"\binsert\b", r"jointures?",
               r"requetes?"],
         # « tri par insertion » ou « insertion dans un ABR » ne sont pas des requêtes INSERT
         faux_amis=[r"\binsertions?\b"]),
    dict(id="processus", titre="Les processus et l'ordonnancement", fiche="processus", niveau="Tle",
         programme="nsi-tle-2019.architecture-os-reseaux.processus",
         notions=["archi.os.processus"],
         mots=[r"\bprocessus\b", r"ordonnance\w*", r"interblocage", r"\bpid\b", r"deadlock"],
         faux_amis=[]),
    dict(id="routage", titre="Le routage : RIP et OSPF", fiche="routage", niveau="Tle",
         programme="nsi-tle-2019.architecture-os-reseaux.routage",
         notions=["reseau.routage"],
         mots=[r"\broutage\b", r"\brip\b", r"\bospf\b", r"\brouteurs?\b"],
         faux_amis=[]),
    dict(id="piles-files", titre="Les piles et les files", fiche="piles-files", niveau="Tle",
         programme="nsi-tle-2019.structures-de-donnees.listes-piles-files",
         notions=["donnees.pile", "donnees.file", "donnees.liste"],
         mots=[r"\bpiles?\b", r"\bfiles?\b", r"listes? chainees?", r"\blifo\b", r"\bfifo\b"],
         faux_amis=[r"piles? d'appels?"]),
]


def normaliser(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().replace(chr(0x2019), "'")
    return re.sub(r"\s+", " ", s)


def couvre(chapitre, notion):
    if notion in chapitre.get("exclues", []):
        return False
    return any(notion == n or notion.startswith(n + ".") for n in chapitre["notions"])


def classer(exercice):
    """(classements, a_verifier) d'un exercice."""
    texte = normaliser(exercice.get("resume", ""))
    classements, douteux = [], []
    for c in CHAPITRES:
        reste, amis = texte, []
        for fa in c["faux_amis"]:
            amis += [m.group(0) for m in re.finditer(fa, reste)]
            reste = re.sub(fa, " ", reste)
        mots = []
        for m in c["mots"]:
            for t in re.finditer(m, reste):
                if t.group(0) not in mots:
                    mots.append(t.group(0))
        notions = [n for n in exercice.get("notions", []) if couvre(c, n)]
        if not mots and not notions:
            continue
        if notions and not mots and amis:
            douteux.append({"chapitre": c["id"], "notions": notions,
                            "raison": "notion seule, avec le faux ami « " + amis[0] + " » dans l'en-tête"})
            continue
        indices = ["notion " + n for n in notions] + ["mot « " + m + " »" for m in mots]
        classements.append({"chapitre": c["id"], "indices": indices})
    return classements, douteux


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return json.load(f)


def construire(precedent=None):
    annales = lire(ANNALES)
    thesaurus = {n["id"] for n in lire(NOTIONS)["notions"]}
    erreurs = []
    for c in CHAPITRES:
        for n in c["notions"] + c.get("exclues", []):
            if n not in thesaurus:
                erreurs.append(f"chapitre {c['id']} : notion {n} absente du thésaurus")
    gardes = {}
    ids_chapitres = {c["id"] for c in CHAPITRES}
    if precedent:
        for eid, e in precedent.get("exercices", {}).items():
            if not isinstance(e, dict) or e.get("verifie") is not True:
                continue
            # Un exercice relu à la main : « chapitres » peut être écrit simplement, ["tris", "recursivite"]
            chapitres = []
            for k in e.get("chapitres") or []:
                if isinstance(k, str):
                    k = {"chapitre": k, "indices": ["relu à la main"]}
                if not isinstance(k, dict) or k.get("chapitre") not in ids_chapitres:
                    erreurs.append(f"{eid} (vérifié à la main) : chapitre inconnu « {k.get('chapitre') if isinstance(k, dict) else k} » ; chapitres possibles : "
                                   + ", ".join(sorted(ids_chapitres)))
                    continue
                chapitres.append(k)
            gardes[eid] = dict(e, chapitres=chapitres)

    exercices, a_classer, a_verifier = {}, [], []
    vus = set()
    for s in annales["epreuve_ecrite"]["sujets"]:
        for x in s.get("exercices", []):
            eid = f"{s['id']}#{x['n']}"
            if eid in vus:
                erreurs.append(f"exercice en double : {eid}")
            vus.add(eid)
            for n in x.get("notions", []):
                if n not in thesaurus:
                    erreurs.append(f"{eid} : notion {n} absente du thésaurus")
            if eid in gardes:
                exercices[eid] = gardes[eid]
                if not gardes[eid].get("chapitres"):
                    a_classer.append(eid)
                continue
            classements, douteux = classer(x)
            exercices[eid] = {"chapitres": classements, "verifie": False}
            if douteux:
                exercices[eid]["a_verifier"] = douteux
                a_verifier.append(eid)
            if not classements:
                a_classer.append(eid)
    disparus = sorted(set(gardes) - vus)

    bilan = {c["id"]: 0 for c in CHAPITRES}
    for e in exercices.values():
        for k in e.get("chapitres", []):
            if k["chapitre"] in bilan:
                bilan[k["chapitre"]] += 1
    sortie = {
        "version": annales.get("version"),
        "tache": "T116",
        "description": "Proposition de classement des exercices des annales du bac NSI (" + ANNALES + ") dans les "
                       "22 chapitres des fiches de révision, pour préparer des TD « type bac » par chapitre. "
                       "Fichier construit par scripts/annales_notions.py : ne pas le modifier à la main, sauf « verifie ».",
        "statut": "proposition automatique de l'Architecte : aucun classement n'est vérifié tant que « verifie » vaut false",
        "methode": "Un exercice entre dans un chapitre si l'une de ses notions (champ « notions » des annales, déduit "
                   "de l'en-tête « Cet exercice porte sur… ») est couverte par le chapitre, ou si l'en-tête contient un "
                   "mot propre au chapitre. Les faux amis sont écartés ; une notion seule face à un faux ami va dans "
                   "« a_verifier ». Un exercice sans indice reste « à classer ». Les en-têtes ne nomment presque jamais "
                   "les variables, les boucles ou les fonctions, que tous les exercices utilisent : ces chapitres ne "
                   "comptent que les exercices qui les nomment.",
        "source": {"fichier": ANNALES, "version": annales.get("version"), "sujets": len(annales["epreuve_ecrite"]["sujets"]),
                   "exercices": len(vus)},
        "chapitres": [
            {"id": c["id"], "titre": c["titre"], "niveau": c["niveau"], "programme": c["programme"],
             "fiche": FICHES + c["fiche"] + "/", "notions": c["notions"]}
            for c in CHAPITRES
        ],
        "bilan": {"par_chapitre": bilan, "classes": len(vus) - len(a_classer), "a_classer": len(a_classer),
                  "a_verifier": len(a_verifier), "verifies": len(gardes) - len(disparus)},
        "a_classer": a_classer,
        "exercices": exercices,
    }
    if disparus:
        sortie["verifies_disparus"] = disparus
    return sortie, erreurs


def texte_json(d):
    return json.dumps(d, ensure_ascii=False, indent=1) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--verifier", action="store_true", help="vérifie que le fichier de sortie est à jour")
    p.add_argument("--bilan", action="store_true", help="affiche le nombre d'exercices par chapitre")
    a = p.parse_args()
    chemin = os.path.join(RACINE, SORTIE)
    precedent = None
    if os.path.exists(chemin):
        try:
            precedent = lire(SORTIE)
        except (OSError, ValueError) as e:
            print(f"{SORTIE} illisible : {e}", file=sys.stderr)
            if a.verifier:
                return 1
    sortie, erreurs = construire(precedent)
    for e in erreurs:
        print("Erreur : " + e, file=sys.stderr)
    if erreurs:
        return 1
    texte = texte_json(sortie)
    if a.verifier:
        if precedent is None or texte_json(precedent) != texte:
            print(f"{SORTIE} n'est pas à jour : lancer « python3 scripts/annales_notions.py ».", file=sys.stderr)
            return 1
        print(f"{SORTIE} est à jour ({sortie['bilan']['classes']} exercices classés sur {sortie['source']['exercices']}).")
        return 0
    if not a.bilan:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(texte)
        print(f"{SORTIE} écrit.")
    b = sortie["bilan"]
    print(f"{sortie['source']['exercices']} exercices : {b['classes']} classés, {b['a_classer']} à classer, "
          f"{b['a_verifier']} avec un classement écarté à vérifier, {b['verifies']} vérifiés à la main.")
    for c in CHAPITRES:
        print(f"  {c['id']:20} {b['par_chapitre'][c['id']]:4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
