#!/usr/bin/env python3
"""Les apparences du compte commun, tirées du catalogue du moteur d'avatars (T101b).

Usage (à la racine du dépôt) :
  python3 -B scripts/apparences_compte_commun.py [CATALOGUE] [--verifier]

CATALOGUE : le catalogue du Designer, assets/equipage/catalogue.json par défaut
(généré depuis assets/equipage.js, Equipage.catalogue). Le script écrit
donnees/compte-commun/apparences.json, que lisent assets/compte-commun.js et
les pages eleve/ et enseignant/ :
- « identite » : tout ce qui sert à se reconnaître et s'habiller, toujours gratuit,
  pour tout avatar (aucune pièce réservée à une lignée ni à un genre) ;
- « elements » : les objets (8 emplacements, rangés en familles lues dans le catalogue) et les
  compagnons, avec leur accès : « libre », « credits » (et un prix) ou « haut_fait » (un trophée :
  gagné par un haut fait, offert par l'enseignant·e ou donné par un jeu ; jamais acheté) ;
- « module » : vrai seulement si assets/equipage.js est à côté du catalogue ; la
  page ne charge le module que dans ce cas (sinon, dessin de remplacement, sans
  requête vers un fichier absent).
Avec --verifier, le script compare au fichier existant et sort en erreur s'il diffère.

Les prix suivent les trois paliers de la spécification (40, 100, 250) ; ils sont
réglés ici, pas dans le catalogue du Designer.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "donnees", "compte-commun", "apparences.json")

# Les prix par emplacement d'objet : un petit objet 40 (environ une feuille de TD),
# un objet de dos ou un effet autour 100 (environ une semaine de travail).
PRIX = {"tete": 40, "visage": 40, "cou": 40, "main": 40, "epaule": 40, "pieds": 40, "dos": 100, "autour": 100}
# Les familles de trophées (par identifiant, jamais par nom) : leurs objets ne s'achètent pas ; ils
# viennent d'un haut fait, de l'enseignant·e (avec un motif) ou d'un jeu, comme élément d'histoire.
# Décision de l'enseignant du 20/11 (19:00) : « Les gimmicks de la classe » ne sont pas dans la boutique.
FAMILLES_TROPHEES = {"classe"}
IDENTIFIANT = re.compile(r"^[a-z0-9_]{1,40}$")


def erreur(message):
    print("ERREUR : " + message, file=sys.stderr)
    sys.exit(1)


def construire(chemin):
    with open(chemin, encoding="utf-8") as f:
        source = json.load(f)
    cat = source.get("catalogue")
    if not isinstance(cat, dict) or "objets" not in cat or "familles" not in cat:
        erreur(f"{chemin} n'a pas la forme attendue (catalogue.objets, catalogue.familles).")
    familles = [f["id"] for f in cat["familles"]]
    elements = []
    for empl in cat["emplacements"]:
        e = empl["id"]
        if e not in PRIX:
            erreur(f"emplacement d'objet inconnu du barème des prix : {e}")
        for o in cat["objets"][e]:
            if o["id"] == "aucun":
                continue
            if not IDENTIFIANT.match(o["id"]):
                erreur(f"identifiant d'objet illisible : {e}:{o['id']}")
            if o.get("famille") not in familles:
                erreur(f"objet sans famille connue : {e}:{o['id']}")
            trophee = o["famille"] in FAMILLES_TROPHEES
            elements.append({"id": f"{e}:{o['id']}", "emplacement": e, "nom": o["nom"], "famille": o["famille"],
                             "acces": "haut_fait" if trophee else "credits", "prix": None if trophee else PRIX[e]})
    for c in cat["compagnon"]:
        if c["id"] == "aucun":
            continue
        acces = "haut_fait" if c.get("gagne") else "libre"
        elements.append({"id": f"compagnon:{c['id']}", "emplacement": "compagnon", "nom": c["nom"], "famille": None,
                         "acces": acces, "prix": None, "depart": bool(c.get("depart"))})
    vus = set()
    for x in elements:
        if x["id"] in vus:
            erreur(f"identifiant en double : {x['id']}")
        vus.add(x["id"])
    identite = {k: cat[k] for k in ("lignee", "teint", "corps", "coiffure", "haut", "bas", "chaussures")}
    identite["couleurs"] = cat["couleurs"]
    module = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(chemin))), "equipage.js"))
    return {
        "version": 1,
        "a_propos": "Généré par scripts/apparences_compte_commun.py depuis assets/equipage/catalogue.json (moteur d'avatars "
                    "du Designer) : ne pas modifier à la main. Identité et tenues gratuites pour tout avatar ; objets à "
                    "prendre avec des crédits, sauf les familles de trophées ; trophées et compagnons gagnés par un haut fait "
                    "ou offerts (le margouillat est donné au départ).",
        "equipage_version": source.get("version"),
        "module": module,
        "taille_max_description": 600,
        "defaut": source["defaut"],
        "identite": identite,
        "emplacements": cat["emplacements"] + [{"id": "compagnon", "nom": "Compagnon"}],
        "familles": [dict(f, trophees=f["id"] in FAMILLES_TROPHEES) for f in cat["familles"]],
        "elements": elements,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chemin = args[0] if args else os.path.join(RACINE, "assets", "equipage", "catalogue.json")
    if not os.path.exists(chemin):
        erreur(f"catalogue introuvable : {chemin}")
    donnees = construire(chemin)
    texte = json.dumps(donnees, ensure_ascii=False, indent=1) + "\n"
    if "--verifier" in sys.argv:
        actuel = open(SORTIE, encoding="utf-8").read() if os.path.exists(SORTIE) else ""
        if actuel != texte:
            erreur(f"{SORTIE} n'est pas à jour : relancer le script.")
        print("apparences.json est à jour.")
        return
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        f.write(texte)
    n = len(donnees["elements"])
    print(f"{SORTIE} : {n} apparences ; module de dessin {'présent' if donnees['module'] else 'absent'}.")


if __name__ == "__main__":
    main()
