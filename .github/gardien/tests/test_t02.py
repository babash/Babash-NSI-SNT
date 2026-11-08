"""T02 : la validation des données détecte-t-elle les fautes graves ? (11 cas, test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_t02.py COPIE_DU_SITE DOSSIER_DE_TRAVAIL

Chaque cas copie le site, introduit une faute dans une fiche d'exemple de donnees/ressources/,
lance scripts/valider_donnees.py de la copie et vérifie que la validation échoue (code 1),
qu'elle va jusqu'à son bilan, et qu'une ligne ERREUR donne le message attendu sur la bonne fiche.
Les cas s'appuient sur les fiches d'exemple de T02 (td1-poo, operation-mirage, cybercase,
alien-python) : si l'une d'elles est renommée ou retirée, adapter le cas qui l'utilise.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadre  # noqa: E402

source, travail = cadre.arguments(__doc__)
bilan = cadre.Bilan()


def cas(titre, nom, faute, *attendus):
    """Une faute dans la fiche « nom » : code 1, bilan affiché, et chaque motif trouvé sur une ligne
    ERREUR qui concerne cette fiche. faute reçoit le chemin de la fiche dans la copie."""
    d = cadre.copie(source, travail)
    faute(os.path.join(d, "donnees", "ressources", nom + ".json"))
    code, sortie = cadre.valider(d)
    erreurs = [l for l in cadre.niveau(sortie, "ERREUR") if "/%s.json" % nom in l]
    problemes = [] if code == 1 else ["code %d au lieu de 1" % code]
    if "Bilan :" not in sortie:
        problemes.append("la validation s'est arrêtée avant son bilan")
    problemes += ["aucune ligne ERREUR sur %s.json ne correspond à « %s »" % (nom, m) for m in attendus
                  if not any(re.search(m, l) for l in erreurs)]
    bilan.verifier(titre, problemes, sortie[-1500:] if problemes else "")


def json_(f):
    """Une faute écrite dans le contenu JSON de la fiche."""
    return lambda chemin: cadre.json_modifie(chemin, f)


def lien_github(x):
    x["documents"][0]["url"] = "https://github.com/babash/NSI-Terminale/blob/main/td1.pdf"
    x["documents"][0].pop("fichier", None)


def dupliquer(chemin):
    shutil.copy(chemin, chemin[:-len(".json")] + "-copie.json")


def accolade_en_trop(chemin):
    with open(chemin, "a", encoding="utf-8") as f:
        f.write("}")


cas("lien principal vers GitHub", "td1-poo", json_(lien_github), r"lien principal pointe vers une page GitHub")
cas("identifiant en double", "td1-poo", dupliquer, r"l'identifiant « td1-poo » est déjà utilisé par")
cas("référence de programme inexistante",
    "td1-poo", json_(lambda x: x.__setitem__("programme", ["nsi-tle-2019.theme-inexistant"])),
    r"« nsi-tle-2019\.theme-inexistant » n'existe pas")
cas("visibilité absente", "td1-poo", json_(lambda x: x["documents"][0].pop("visible")),
    r"champ obligatoire manquant : « visible »")
cas("deux documents principaux",
    "operation-mirage", json_(lambda x: [doc.__setitem__("principal", True) for doc in x["documents"]]),
    r"documents principaux .*il en faut exactement un")
cas("identifiants de démonstration dans une fiche (valeurs fictives)",
    "cybercase", json_(lambda x: x.__setitem__("presentation", x["presentation"] + cadre.FAUX_ACCES)),
    r"ressemble à un identifiant")
cas("clé secrète Supabase (valeur fictive)", "alien-python", json_(lambda x: x.__setitem__("resume", cadre.FAUX_CLE)),
    r"une clé secrète Supabase", r"une clé « service.role » Supabase")
cas("donnees_eleves absent", "alien-python", json_(lambda x: x.pop("donnees_eleves")),
    r"champ obligatoire manquant : « donnees_eleves »")
cas("fichier du dépôt inexistant",
    "td1-poo", json_(lambda x: x["documents"][0].__setitem__("fichier", "nsi-terminale/fichiers/absent.html")),
    r"fichier introuvable dans le dépôt : « nsi-terminale/fichiers/absent\.html »")
cas("valeur de référentiel inexistante", "td1-poo", json_(lambda x: x.__setitem__("usages", ["telephone-requis"])),
    r"« telephone-requis » n'est pas dans le référentiel « usages »")
cas("JSON invalide", "td1-poo", accolade_en_trop, r"JSON invalide")

shutil.rmtree(os.path.join(travail, "cas"), ignore_errors=True)
bilan.terminer()
