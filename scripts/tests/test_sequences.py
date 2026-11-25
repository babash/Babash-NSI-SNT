#!/usr/bin/env python3
"""Tests des séquences (T153) : donnees/sequences/<id>.json et donnees/referentiels/sequences.json.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_sequences.py [--racine DOSSIER_DU_DEPOT] [--travail DOSSIER] [--garder]

Même principe que test_notions.py (dont la classe Essai est reprise) : chaque cas prépare une copie de travail,
y écrit une séquence d'essai (ou modifie le référentiel), lance scripts/valider_donnees.py et vérifie le code de
retour et les lignes attendues. Les cas s'appuient sur des fiches de terminale (quizznsi-piles-files,
fiche-piles-files-python, td-bac-piles-files, controle-notions-piles-files, file-deux-piles-codex, cybercase,
dm-flash-terminale) : les adapter si elles changent. Un dernier cas construit la bibliothèque et vérifie ce que
bibliotheque.json dit des séquences (ressources visibles, document visé, document caché aux élèves).

Code de retour : 0 si tous les cas passent, 1 sinon. Python 3 standard, sans dépendance.
"""
import argparse
import json
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import test_notions as tn  # noqa: E402

REF = "donnees/referentiels/sequences.json"
SEQ = "donnees/sequences/tle-zz-essai.json"   # rangée après les séquences du dépôt : les erreurs croisées tombent sur elle


def sequence(**changements):
    """Une séquence d'essai de terminale, valide ; les changements remplacent ses champs (None retire le champ)."""
    s = {
        "$schema": "../schema/sequence.schema.json",
        "id": "tle-zz-essai", "niveau": "terminale", "enseignement": "nsi",
        "titre": "Essai : piles et files",
        "objectif": "Une séquence d'essai pour les tests du validateur.",
        "rang": 990,
        "programme": ["nsi-tle-2019.structures-de-donnees.listes-piles-files"],
        "notions": ["donnees.pile", "donnees.file"],
        "statut": "publiee",
        "etapes": [
            {"type": "cours-quiz", "ressources": [{"ressource": "quizznsi-piles-files", "secondaire": True}]},
            {"type": "fiches", "ressources": [{"ressource": "fiche-piles-files-python", "secondaire": True}]},
            {"type": "td-bac", "ressources": [{"ressource": "td-bac-piles-files", "secondaire": True}]},
            {"type": "controle", "ressources": []}
        ]
    }
    for k, v in changements.items():
        if v is None:
            s.pop(k, None)
        else:
            s[k] = v
    return s


def ecrire_sequence(s, nom=SEQ):
    def modifier(d):
        os.makedirs(os.path.join(d, "donnees", "sequences"), exist_ok=True)
        tn.ecrire(os.path.join(d, nom), s)
    return modifier


def avec_etapes(*etapes, **autres):
    return ecrire_sequence(sequence(etapes=list(etapes), **autres))


def referentiel(f):
    def modifier(d):
        chemin = os.path.join(d, REF)
        r = tn.lire(chemin)
        f(r)
        tn.ecrire(chemin, r)
    return modifier


def plusieurs(*modifs):
    def modifier(d):
        for m in modifs:
            m(d)
    return modifier


def construire(e):
    """La construction : la séquence d'essai dans bibliotheque.json, vue de l'extérieur."""
    d = e.copie()

    def cacher_corrige_aux_eleves(d):
        chemin = os.path.join(d, "donnees", "ressources", "controle-notions-piles-files.json")
        f = tn.lire(chemin)
        for doc in f["documents"]:
            if doc["role"] == "corrige":
                doc["visible"]["eleve"] = False
        tn.ecrire(chemin, f)
    ecrire_sequence(sequence(etapes=[
        {"type": "td", "ressources": [{"ressource": "dm-flash-terminale", "secondaire": True,
                                       "document": "nsi-terminale/fichiers/dm-flash-terminale/dm-pile/index.html"}]},
        {"type": "controle", "ressources": [{"ressource": "controle-notions-piles-files", "secondaire": True}]}
    ]))(d)
    cacher_corrige_aux_eleves(d)
    sortie = os.path.join(d, "sortie")
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(e.racine, "scripts", "construire_bibliotheque.py"),
                        "--racine", d, "--sortie", sortie, "--sans-textes"], capture_output=True, text=True, timeout=300)
    pb = []
    if r.returncode != 0:
        pb.append("construction en échec : " + (r.stdout + r.stderr)[-600:])
    else:
        b = tn.lire(os.path.join(sortie, "bibliotheque.json"))
        s = next((x for x in b.get("sequences", []) if x["id"] == "tle-zz-essai"), None)
        fiches = {f["id"]: f for f in b["ressources"]}
        if not s:
            pb.append("la séquence d'essai manque à bibliotheque.json")
        else:
            if s.get("rubrique") != "nsi-terminale":
                pb.append(f"rubrique « {s.get('rubrique')} » au lieu de « nsi-terminale »")
            place = s["etapes"][0]["ressources"][0]
            docs = fiches["dm-flash-terminale"]["documents"]
            if "document" in place or not isinstance(place.get("doc"), int) \
                    or docs[place["doc"]].get("fichier") != "nsi-terminale/fichiers/dm-flash-terminale/dm-pile/index.html":
                pb.append(f"le document visé n'est pas devenu « doc », son rang dans la fiche publique : {place}")
            if "notes" in s:
                pb.append("les notes de l'enseignant ne doivent pas être dans bibliotheque.json")
        caches = [d_ for d_ in fiches["controle-notions-piles-files"]["documents"] if d_.get("cache_eleves")]
        if [d_["role"] for d_ in caches] != ["corrige"]:
            pb.append(f"le corrigé caché aux élèves doit porter « cache_eleves » (et lui seul) : {[d_['role'] for d_ in caches]}")
        if "sequences" not in b.get("referentiels", {}):
            pb.append("le référentiel des séquences manque à bibliotheque.json")
        t = tn.lire(os.path.join(sortie, "bibliotheque-complete.json"))
        if not any(x["id"] == "tle-zz-essai" for x in t.get("sequences", [])):
            pb.append("la séquence d'essai manque à bibliotheque-complete.json")
    e.n += 0
    if pb:
        e.echecs += 1
        print("  ÉCHEC  construction : la séquence dans bibliotheque.json")
        for p in pb:
            print(f"         - {p}")
    else:
        print("  ok     construction : la séquence dans bibliotheque.json")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--racine", default=tn.RACINE_DEFAUT)
    p.add_argument("--garder", action="store_true", help="garder toutes les copies de travail")
    p.add_argument("--travail", help="dossier où créer les copies de travail")
    args = p.parse_args()
    e = tn.Essai(os.path.abspath(args.racine), args.garder, args.travail)
    S, R = SEQ, REF

    print("Les séquences du dépôt")
    e.cas("le dépôt est valide, sans erreur sur les séquences", lambda d: None, 0,
          absents=[("ERREUR", "donnees/sequences", "."), ("ERREUR", R, ".")])
    e.cas("une séquence d'essai valide", ecrire_sequence(sequence()), 0,
          absents=[("ERREUR", S, "."), ("ATTENTION", S, ".")])

    print("Le schéma et les références")
    e.cas("champ inconnu", ecrire_sequence(sequence(chapitre=3)), 1, presents=[("ERREUR", S, "champ inconnu « chapitre »")])
    e.cas("identifiant différent du nom du fichier", ecrire_sequence(sequence(id="tle-autre")), 1,
          presents=[("ERREUR", S, "ne correspond pas au nom du fichier")])
    e.cas("niveau inconnu", ecrire_sequence(sequence(niveau="cm2")), 1,
          presents=[("ERREUR", S, "« cm2 » n'est pas dans le référentiel « niveaux »")])
    e.cas("contenu du programme inconnu", ecrire_sequence(sequence(programme=["nsi-tle-2019.piles"])), 1,
          presents=[("ERREUR", S, "n'existe pas dans programmes.json")])
    e.cas("programme d'un autre niveau", ecrire_sequence(sequence(programme=["nsi-1re-2019.algorithmique.gloutons"])), 0,
          presents=[("ATTENTION", S, "absent de « niveaux »")])
    e.cas("notion inconnue", ecrire_sequence(sequence(notions=["donnees.piles"])), 1,
          presents=[("ERREUR", S, "n'est pas dans le thésaurus")])
    e.cas("ressource inconnue", avec_etapes({"type": "td", "ressources": ["td-qui-n-existe-pas"]}), 1,
          presents=[("ERREUR", S, "aucune fiche « td-qui-n-existe-pas »")])
    e.cas("document visé absent de la fiche",
          avec_etapes({"type": "td", "ressources": [{"ressource": "dm-flash-terminale", "secondaire": True, "document": "x/y.pdf"}]}), 1,
          presents=[("ERREUR", S, "n'est l'adresse d'aucun document de la fiche")])

    print("Le titre et le rang")
    e.cas("numéro de chapitre dans le titre", ecrire_sequence(sequence(titre="Chapitre 3 : piles et files")), 1,
          presents=[("ERREUR", S, "porte un numéro")])
    e.cas("titre numéroté « 2. »", ecrire_sequence(sequence(titre="2. Piles et files")), 1,
          presents=[("ERREUR", S, "porte un numéro")])
    e.cas("titre sans libellé des référentiels", ecrire_sequence(sequence(titre="Les tuyaux et les seaux")), 0,
          presents=[("ATTENTION", S, "ne reprend aucun libellé")])
    e.cas("même rang que tle-piles-files", ecrire_sequence(sequence(rang=30)), 1,
          presents=[("ERREUR", S, "le rang 30 est déjà celui de la séquence « tle-piles-files »")])

    print("Les étapes")
    e.cas("étape inconnue", avec_etapes({"type": "cours", "ressources": []}), 1,
          presents=[("ERREUR", S, "« cours » n'est pas une étape du référentiel")])
    e.cas("étape d'un autre niveau", avec_etapes({"type": "activites-jeux", "ressources": []}), 1,
          presents=[("ERREUR", S, "n'est pas prévue en terminale")])
    e.cas("étapes dans le désordre", avec_etapes({"type": "controle", "ressources": []}, {"type": "fiches", "ressources": []}), 1,
          presents=[("ERREUR", S, "est mal placée")])
    e.cas("étape en double", avec_etapes({"type": "td", "ressources": []}, {"type": "td", "ressources": []}), 1,
          presents=[("ERREUR", S, "figure deux fois : réunir")])
    e.cas("aucune étape remplie", avec_etapes({"type": "td", "ressources": []}), 0,
          presents=[("ATTENTION", S, "aucune étape n'a de ressource")])
    e.cas("type de ressource inattendu à l'étape", avec_etapes({"type": "controle", "ressources": [
        {"ressource": "fiche-piles-files-python", "secondaire": True}]}), 0,
          presents=[("ATTENTION", S, "n'est pas d'un type attendu à l'étape « Contrôle »")])
    e.cas("même ressource deux fois sans document distinct", avec_etapes(
        {"type": "fiches", "ressources": [{"ressource": "fiche-piles-files-python", "secondaire": True}]},
        {"type": "td-bac", "ressources": [{"ressource": "fiche-piles-files-python", "secondaire": True}]}), 1,
          presents=[("ERREUR", S, "figure déjà dans la séquence")])
    e.cas("même ressource deux fois avec deux documents", avec_etapes(
        {"type": "td", "ressources": [{"ressource": "poo-td-tp-terminale", "secondaire": True,
                                       "document": "nsi-terminale/fichiers/poo-td-tp-terminale/poo-td.pdf"}]},
        {"type": "tp-activites", "ressources": [{"ressource": "poo-td-tp-terminale", "secondaire": True,
                                                 "document": "nsi-terminale/fichiers/poo-td-tp-terminale/poo-tp.pdf"}]}), 0,
          absents=[("ERREUR", S, ".")])

    print("Les ressources externes (règle du 25/11)")
    e.cas("ressource externe au premier rang", avec_etapes({"type": "tp-activites", "ressources": [{"ressource": "file-deux-piles-codex", "secondaire": True}]}), 0,
          presents=[("ATTENTION", S, "est une ressource externe .* « complements »")])
    e.cas("ressource externe en complément", avec_etapes({"type": "tp-activites", "ressources": [], "complements": [{"ressource": "file-deux-piles-codex", "secondaire": True}]}), 0,
          absents=[("ATTENTION", S, "ressource externe")])
    e.cas("exception du niveau au premier rang", avec_etapes({"type": "tp-activites", "ressources": ["cybercase"]}), 0,
          absents=[("ATTENTION", S, "ressource externe")])
    e.cas("ressource de l'enseignant en complément", avec_etapes({"type": "fiches", "ressources": [],
                                                                  "complements": [{"ressource": "fiche-piles-files-python", "secondaire": True}]}), 0,
          presents=[("ATTENTION", S, "est mise en avant à ce niveau : la placer dans « ressources »")])

    print("La séquence principale de chaque ressource")
    e.cas("deux séquences principales pour une ressource", avec_etapes({"type": "cours-quiz", "ressources": ["quizznsi-piles-files"]}), 1,
          presents=[("ERREUR", S, "a déjà pour séquence principale « tle-piles-files »")])

    print("Les prérequis")
    e.cas("prérequis existant", ecrire_sequence(sequence(prerequis=["tle-piles-files"])), 0,
          absents=[("ERREUR", S, "."), ("ATTENTION", S, "prérequis|rang")])
    e.cas("prérequis inconnu", ecrire_sequence(sequence(prerequis=["tle-graphes"])), 1,
          presents=[("ERREUR", S, "aucune séquence « tle-graphes »")])
    e.cas("prérequis vu après (rang)", ecrire_sequence(sequence(rang=5, prerequis=["tle-piles-files"])), 0,
          presents=[("ATTENTION", S, "revoir les rangs")])
    e.cas("prérequis d'un niveau plus avancé", plusieurs(
        ecrire_sequence(sequence(niveau="premiere", programme=["nsi-1re-2019.algorithmique.gloutons"], etapes=[{"type": "td", "ressources": []}],
                                 prerequis=["tle-piles-files"], titre="Algorithmes gloutons"))), 1,
          presents=[("ERREUR", S, "d'un niveau plus avancé")])
    e.cas("prérequis en boucle", plusieurs(
        ecrire_sequence(sequence(prerequis=["tle-zz-essai-2"])),
        ecrire_sequence(sequence(id="tle-zz-essai-2", rang=991, prerequis=["tle-zz-essai"], etapes=[{"type": "td", "ressources": []}]),
                        "donnees/sequences/tle-zz-essai-2.json")), 1,
          presents=[("ERREUR", "donnees/sequences/tle-zz-essai", "tournent en rond")])

    print("Le référentiel des séquences")
    e.cas("parcours avec une étape inconnue", referentiel(lambda r: r["parcours"]["terminale"].append("oral")), 1,
          presents=[("ERREUR", R, "« oral » n'est pas une étape")])
    e.cas("exception qui n'existe pas", referentiel(lambda r: r["mises_en_avant"]["seconde"].append("ztype")), 1,
          presents=[("ERREUR", R, "aucune fiche « ztype »")])
    e.cas("exception déjà de l'enseignant", referentiel(lambda r: r["mises_en_avant"]["terminale"].append("td1-poo")), 0,
          presents=[("ATTENTION", R, "inutile de la lister ici")])
    e.cas("type attendu inconnu", referentiel(lambda r: r["etapes"][0]["types_attendus"].append("quiz")), 1,
          presents=[("ERREUR", R, "« quiz » n'est pas dans le référentiel « types »")])

    print("La construction")
    construire(e)
    return e.terminer()


if __name__ == "__main__":
    sys.exit(main())
