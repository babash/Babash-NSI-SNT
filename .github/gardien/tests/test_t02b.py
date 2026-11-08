"""T02b : la validation applique-t-elle les règles 19 et 20 et les intitulés Pix ? (16 cas, test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_t02b.py COPIE_DU_SITE DOSSIER_DE_TRAVAIL

Chaque cas copie le site, y crée une situation, lance scripts/valider_donnees.py de la copie,
normalement puis avec --strict, et vérifie :
  - le message attendu, à son niveau (ERREUR, ATTENTION ou INFO), sur la bonne fiche ;
  - qu'aucune ligne ne correspond au motif « absent » (limité à la fiche concernée, pour que
    les autres fiches de la bibliothèque n'interfèrent pas) ;
  - le code de sortie normal (1 si le cas crée une erreur, 0 sinon), et celui de --strict :
    1 dès qu'il y a une erreur ou un avertissement, 0 sinon.
Les deux premiers cas décrivent l'état des fiches d'exemple : deux avertissements voulus (éditeur
d'Alien Python, page du TD 1 de POO), que la revue des ressources (T18) lèvera. Quand ce sera
fait, ces deux cas échoueront : les mettre à jour, comme tout cas dont la fiche d'exemple change.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadre  # noqa: E402

source, travail = cadre.arguments(__doc__)
bilan = cadre.Bilan()
CRITERES = ["coloration", "indentation", "guides_indentation", "autocompletion", "erreurs_expliquees"]
# La fiche d'exemple d'une ressource externe (origine « externe »), dont la règle 20 n'est qu'une information
EXTERNE = "cybercase"


def tous(valeur):
    return {c: valeur for c in CRITERES}


def fiche(nom, f):
    return lambda d: cadre.json_modifie(os.path.join(d, "donnees", "ressources", nom + ".json"), f)


def referentiel(nom, f):
    return lambda d: cadre.json_modifie(os.path.join(d, "donnees", "referentiels", nom + ".json"), f)


def cas(titre, modifier, niveau, motif, code_normal, absent=None):
    """niveau et motif : la ligne attendue (niveau None : aucune ligne exigée) ;
    absent : expression qui ne doit apparaître sur aucune ligne."""
    d = cadre.copie(source, travail)
    modifier(d)
    cn, sortie = cadre.valider(d)
    cs, _ = cadre.valider(d, strict=True)
    lignes = sortie.splitlines()
    strict_attendu = 1 if cadre.niveau(sortie, "ERREUR") or cadre.niveau(sortie, "ATTENTION") else 0
    problemes = []
    if niveau and not any(l.startswith(niveau) and re.search(motif, l) for l in lignes):
        problemes.append("aucune ligne %s ne correspond à « %s »" % (niveau, motif))
    interdites = [l for l in lignes if absent and re.search(absent, l)]
    if interdites:
        problemes.append("ligne inattendue : " + interdites[0][:150])
    if "Bilan :" not in sortie:
        problemes.append("la validation s'est arrêtée avant son bilan")
    if (cn, cs) != (code_normal, strict_attendu):
        problemes.append("codes %d/%d au lieu de %d/%d" % (cn, cs, code_normal, strict_attendu))
    bilan.verifier(titre, problemes, sortie[-1500:] if problemes else "")


# 0. Les données telles quelles : aucune erreur ; deux avertissements voulus
cas("données d'exemple : avertissement voulu (Alien Python, règle 20)", lambda d: None,
    "ATTENTION", r"alien-python\.json .*règle 20", 0)
cas("données d'exemple : avertissement voulu (TD 1 de POO, règle 19)", lambda d: None,
    "ATTENTION", r"td1-poo\.json .*règle 19", 0)

# Règle 20
cas("création de l'enseignant : éditeur complet, aucun avertissement de règle 20",
    fiche("alien-python", lambda x: x.__setitem__("editeur_code", tous(True))), None, None, 0,
    absent=r"alien-python\.json .*règle 20")
cas("création de l'enseignant : usage sans « editeur_code »",
    fiche("alien-python", lambda x: x.pop("editeur_code")),
    "ATTENTION", r"alien-python\.json .*editeur_code.*noter les critères", 0)
cas("création de l'enseignant : un seul critère à false",
    fiche("alien-python", lambda x: x.__setitem__("editeur_code", dict(tous(True), autocompletion=False))),
    "ATTENTION", r"alien-python\.json .*il manque.*autocomplétion contextualisée$", 0)
cas("« editeur_code » sans l'usage",
    fiche("alien-python", lambda x: x.__setitem__("usages", ["en-ligne", "en-autonomie"])),
    "ATTENTION", r"alien-python\.json .*usages.*ajouter l'usage", 0)
cas("critère manquant dans « editeur_code » (schéma)",
    fiche("alien-python", lambda x: x["editeur_code"].pop("guides_indentation")),
    "ERREUR", r"alien-python\.json .*champ obligatoire manquant : « guides_indentation »", 1)
cas("champ inconnu dans « editeur_code » (schéma)",
    fiche("alien-python", lambda x: x["editeur_code"].__setitem__("couleur", True)),
    "ERREUR", r"alien-python\.json .*champ inconnu « couleur »", 1)
cas("critère qui n'est pas un booléen",
    fiche("alien-python", lambda x: x["editeur_code"].__setitem__("coloration", "oui")),
    "ERREUR", r"alien-python\.json .*editeur_code\.coloration : doit être true ou false", 1)
cas("ressource externe : critère à false, simple information",
    fiche(EXTERNE, lambda x: (x.__setitem__("usages", x["usages"] + ["editeur-de-code"]),
                              x.__setitem__("editeur_code", dict(tous(True), guides_indentation=False)))),
    "INFO", EXTERNE + r"\.json .*ressource externe, pour information.*guides d'indentation", 0,
    absent=r"^(ERREUR|ATTENTION) .*" + EXTERNE + r"\.json .*règle 20")
cas("critères du référentiel et du schéma qui ne concordent pas",
    referentiel("valeurs", lambda v: [u["criteres"].pop() for u in v["usages"] if u["id"] == "editeur-de-code"]),
    "ERREUR", r"valeurs\.json .*ne concordent pas", 1)

# Règle 19
cas("« td_en_ligne » sur une ressource qui n'est pas un TD",
    fiche("alien-python", lambda x: x.__setitem__("td_en_ligne", {"responsive": True, "auto_corrective": True})),
    "ATTENTION", r"alien-python\.json .*td_en_ligne.*type « td »", 0)
cas("TD : page complète, plus d'avertissement de règle 19",
    fiche("td1-poo", lambda x: x.__setitem__("td_en_ligne", {"responsive": True, "auto_corrective": True})),
    None, None, 0, absent=r"td1-poo\.json .*règle 19")
cas("ressource externe : tous les critères à true, aucune information de règle 20",
    fiche(EXTERNE, lambda x: (x.__setitem__("usages", x["usages"] + ["editeur-de-code"]),
                              x.__setitem__("editeur_code", tous(True)))),
    None, None, 0, absent=EXTERNE + r"\.json .*règle 20")
cas("TD : critère manquant dans « td_en_ligne » (schéma)",
    fiche("td1-poo", lambda x: x["td_en_ligne"].pop("auto_corrective")),
    "ERREUR", r"td1-poo\.json .*champ obligatoire manquant : « auto_corrective »", 1)

# Compétences Pix
cas("compétence Pix inexistante",
    fiche("fiche-variables-python", lambda x: x.__setitem__("competences_pix", ["programmer", "inventee"])),
    "ERREUR", r"fiche-variables-python\.json .*« inventee » n'est pas dans le référentiel « competences_pix »", 1)

shutil.rmtree(os.path.join(travail, "cas"), ignore_errors=True)
bilan.terminer()
