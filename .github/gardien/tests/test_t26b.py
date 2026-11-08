"""T26b : le point médian est-il accepté dans les textes et refusé dans les identifiants ? (4 cas, test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_t26b.py COPIE_DU_SITE DOSSIER_DE_TRAVAIL

Décision de l'enseignant du 07/11/2026 : langage inclusif complet, point médian compris, dans les
textes ; les identifiants restent en ASCII (minuscules et tirets). Chaque cas copie le site, y
place un point médian, lance scripts/valider_donnees.py de la copie et vérifie le code de sortie
et les messages : une ERREUR qui cite le point médian pour un identifiant, aucune ERREUR ni
ATTENTION sur le texte pour une phrase.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadre  # noqa: E402

source, travail = cadre.arguments(__doc__)
bilan = cadre.Bilan()
SECTION = "pour-occuper-les-plus-forts"   # titre : « Pour occuper les plus fort·e·s »


def cas(titre, modifier, code_attendu, doit=None, ne_doit_pas=None):
    """doit : motif d'une ligne ERREUR attendue ; ne_doit_pas : motif interdit sur les lignes ERREUR et ATTENTION."""
    d = cadre.copie(source, travail)
    modifier(d)
    code, sortie = cadre.valider(d)
    signalees = cadre.niveau(sortie, "ERREUR") + cadre.niveau(sortie, "ATTENTION")
    problemes = [] if code == code_attendu else ["code %d au lieu de %d" % (code, code_attendu)]
    if "Bilan :" not in sortie:
        problemes.append("la validation s'est arrêtée avant son bilan")
    if doit and not any(re.search(doit, l) for l in cadre.niveau(sortie, "ERREUR")):
        problemes.append("aucune ligne ERREUR ne correspond à « %s »" % doit)
    if ne_doit_pas and any(re.search(ne_doit_pas, l) for l in signalees):
        problemes.append("message inattendu : " + next(l for l in signalees if re.search(ne_doit_pas, l))[:150])
    bilan.verifier(titre, problemes, sortie[-1500:] if problemes else "")


def vitrine(f):
    return lambda d: cadre.json_modifie(os.path.join(d, "donnees", "vitrine.exemple.json"), f)


def fiche(nom, f):
    return lambda d: cadre.json_modifie(os.path.join(d, "donnees", "ressources", nom + ".json"), f)


def section(v):
    """La sous-section « Pour occuper les plus fort·e·s » de la vitrine d'exemple."""
    for r in v["rubriques"]:
        for s in r.get("sections", []):
            for ss in s.get("sous_sections", []):
                if ss.get("id") == SECTION:
                    return ss
    raise SystemExit("sous-section « %s » introuvable dans la vitrine d'exemple" % SECTION)


# Les points médians de ce fichier sont tous le caractère U+00B7 (caracteres.py le vérifie).
cas("données d'exemple : aucune erreur (titre « Pour occuper les plus fort·e·s »)", lambda d: None, 0)
cas("point médian dans un identifiant de section : refusé, avec l'aide qui cite le point médian",
    vitrine(lambda v: section(v).__setitem__("id", "pour-occuper-les-plus-fort·e·s")), 1,
    doit=r"vitrine\.exemple\.json .*sans accents, espaces ni point médian")
cas("point médian dans un texte de fiche : accepté",
    fiche("td1-poo", lambda x: x.__setitem__("resume", x["resume"] + " Pour les élèves les plus fort·e·s.")), 0,
    ne_doit_pas=r"td1-poo\.json › resume")
cas("point médian dans un identifiant de fiche : refusé",
    fiche("td1-poo", lambda x: x.__setitem__("liees", [{"ressource": "fiche-des-enseignant·e·s", "relation": "voir-aussi"}])),
    1, doit=r"td1-poo\.json › liees\[0\]\.ressource : .*point médian")

shutil.rmtree(os.path.join(travail, "cas"), ignore_errors=True)
bilan.terminer()
