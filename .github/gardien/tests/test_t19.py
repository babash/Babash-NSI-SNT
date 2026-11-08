"""T19 : le pied de page suit-il ses réglages ? (5 variantes de reglages.js, test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_t19.py COPIE_DU_SITE DOSSIER_DE_TRAVAIL

Pour chaque variante de reglages.js (telle quelle, mention_ia vide, invitation_ia vide, autre
auteur, réglages absents comme dans un ancien reglages.js), le test copie le site, le sert en
local, affiche l'accueil et la page SNT dans Chrome, et vérifie dans le pied de page (p.mentions)
les textes présents et absents et le nom en gras, puis l'absence d'erreur JavaScript et de bloc
d'erreur (.alerte). Les textes attendus sont ceux que l'enseignant a validés le 07/11/2026 : s'ils
changent dans assets/site.js ou dans reglages.js, mettre à jour les constantes ci-dessous.
Il faut Playwright et Chrome (voir commun.lancer).
"""
import os
import re
import shutil
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.dirname(ICI))
import cadre  # noqa: E402
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

source, travail = cadre.arguments(__doc__)
bilan = cadre.Bilan()
INSECABLE = chr(0x00A0)   # assets/site.js colle le tiret du nom à ses voisins (« Babash - NSI… »)

AUTEUR = "Babash - NSI Tani Malandi"
C = "Ces ressources sont conçues par Babash - NSI Tani Malandi ; beaucoup le sont avec l'aide de l'IA."
LIC = "Documents sous licence CC BY-SA 4.0, code des applications sous licence MIT."
REU = ("Tu peux les réutiliser et les modifier en mentionnant Babash - NSI Tani Malandi et la licence ; "
       "un document modifié se partage sous la même licence.")
INV = "Si tu utilises l'IA pour les modifier, merci de le préciser."
EXT = ("Les ressources externes restent la propriété de leurs auteurs et autrices : leur site d'origine est "
       "indiqué sur chaque ressource. Décor du site : dessin original.")

LIRE = """() => { const p = document.querySelector('p.mentions');
  return { texte: p ? p.innerText : null, gras: p ? [...p.querySelectorAll('strong')].map(s => s.textContent) : [],
           liens: p ? [...p.querySelectorAll('a')].map(a => a.textContent + ' -> ' + a.href + ' [' + a.rel + ']') : [],
           alerte: !!document.querySelector('.alerte') }; }"""


def variante(nom, remplacements):
    """Une copie du site dont reglages.js est modifié ; (dossier, motif introuvable ou None)."""
    d = cadre.copie(source, travail, nom)
    chemin = os.path.join(d, "reglages.js")
    texte = commun.lire(chemin)
    for avant, apres in remplacements:
        nouveau = re.sub(avant, apres, texte, count=1, flags=re.M)
        if nouveau == texte:
            return d, avant
        texte = nouveau
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)
    return d, None


def lire(d, nav):
    resultats = {}
    with cadre.servir(d) as base:
        for chemin in ("", "snt/"):
            ctx = nav.new_context(viewport={"width": 1000, "height": 800})
            page = ctx.new_page()
            erreurs = []
            page.on("pageerror", lambda e: erreurs.append(str(e)))
            page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
            page.goto(base + "/" + chemin, wait_until="networkidle", timeout=45000)
            infos = page.evaluate(LIRE)
            infos["erreurs"] = erreurs
            resultats[chemin or "accueil"] = infos
            ctx.close()
    return resultats


def verifier(titre, nav, nom, remplacements, doit, ne_doit_pas=(), gras=None, montrer_liens=False):
    d, introuvable = variante(nom, remplacements)
    if introuvable:
        bilan.verifier(titre, ["motif introuvable dans reglages.js : " + introuvable])
        shutil.rmtree(d, ignore_errors=True)
        return
    for page, infos in lire(d, nav).items():
        texte = (infos["texte"] or "").replace(INSECABLE, " ")
        pb = []
        if infos["texte"] is None:
            pb.append("pas de pied de page")
        manque = [t for t in doit if t not in texte]
        if manque:
            pb.append("manque : " + " | ".join(manque))
        en_trop = [t for t in ne_doit_pas if t in texte]
        if en_trop:
            pb.append("en trop : " + " | ".join(en_trop))
        if gras is not None and [g.replace(INSECABLE, " ") for g in infos["gras"]] != gras:
            pb.append("gras : %r au lieu de %r" % (infos["gras"], gras))
        if infos["erreurs"] or infos["alerte"]:
            pb.append("erreurs : %r, alerte : %r" % (infos["erreurs"], infos["alerte"]))
        bilan.verifier("%s (%s)" % (titre, page), pb, "texte relevé : " + texte.replace("\n", " / ") if pb else "")
        if montrer_liens:
            print("        liens (%s) : %s" % (page, " ; ".join(infos["liens"])))
    shutil.rmtree(d, ignore_errors=True)


with sync_playwright() as p:
    nav = commun.lancer(p)
    verifier("réglages de la copie : les textes validés", nav, "telle-quelle", [],
             [C, LIC, REU + " " + INV, EXT], gras=[AUTEUR], montrer_liens=True)
    verifier("mention_ia vide : la phrase disparaît, l'auteur passe en gras dans la réutilisation", nav, "sans-mention",
             [(r'^  mention_ia: ".*",$', '  mention_ia: "",')],
             [LIC, REU, INV, EXT], ne_doit_pas=["Ces ressources sont conçues"], gras=[AUTEUR])
    verifier("invitation_ia vide : l'invitation disparaît", nav, "sans-invitation",
             [(r'^  invitation_ia: ".*",$', '  invitation_ia: "",')],
             [C, LIC, REU, EXT], ne_doit_pas=[INV], gras=[AUTEUR])
    verifier("auteur changé : il remplace {auteur} partout", nav, "autre-auteur",
             [(r'^  auteur: ".*",$', '  auteur: "Autre Nom - Essai",')],
             ["Ces ressources sont conçues par Autre Nom - Essai ;", "en mentionnant Autre Nom - Essai et la licence"],
             ne_doit_pas=[AUTEUR], gras=["Autre Nom - Essai"])
    verifier("réglages absents (ancien reglages.js) : les textes validés de assets/site.js", nav, "sans-reglages",
             [(r'^  // En bas de chaque page.*\n(?:  .*\n)*?  invitation_ia: ".*",\n', '')],
             [C, LIC, REU + " " + INV, EXT], gras=[AUTEUR])
    nav.close()

bilan.terminer()
