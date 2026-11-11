"""T45 : le lien « Code source sur GitHub » du site, l'encadré d'erreur et leur contrôle automatique (test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_t45.py COPIE_DU_SITE DOSSIER_DE_TRAVAIL

D'après les essais de l'Architecte (T45c) et du Gardien (T45 et T45d), sur des copies du site
servies en local et affichées dans Chrome (accueil et SNT) :
  - assets/site.js : le lien du pied de page suit le réglage depot de reglages.js (tel quel ;
    adresse complète en .git ; autre dépôt ; valeur fautive : erreur affichée et lien vers le
    dépôt par défaut ; réglage absent : dépôt par défaut, sans erreur) ;
  - l'encadré d'erreur : son titre nomme la cause (les réglages, une liste, les deux) ; l'astuce
    de la virgule n'apparaît que pour une erreur qui a un numéro de ligne (une virgule retirée),
    pas pour un champ inconnu ni pour un réglage depot mal écrit ;
  - .github/verifier-site.py de la copie : code_source() sur des morceaux de DOM fabriqués
    (entités, icône, casse, adresse hors de GitHub…) et depot() sur des reglages.js fabriqués ;
    puis le contrôle complet sur trois copies : telle quelle (code 0), lien retiré du pied de
    page (code 1, les 6 pages citées), lien vers un autre dépôt (code 1).
Les motifs remplacés dans assets/site.js et reglages.js sont ceux de la version du 11/11/2026 :
s'ils changent, le cas le dit (« motif introuvable »), et il faut mettre ce test à jour.
Il faut Playwright et Chrome (voir commun.lancer). Compter quelques minutes : verifier-site.py
affiche chaque page dans Chrome.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.dirname(ICI))
import cadre  # noqa: E402
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

source, travail = cadre.arguments(__doc__)
bilan = cadre.Bilan()
D = "https://github.com/babash/Babash-NSI-SNT"
DEPOT = ("reglages.js", r'^  depot: "babash/Babash-NSI-SNT",$')
TITRE_R = "Les réglages du site contiennent une erreur"
TITRE_L = "Une liste de ressources contient une erreur"
TITRE_RL = "Les réglages du site et une liste de ressources contiennent des erreurs"
ASTUCE = "Souvent : une virgule oubliée en fin de ligne"

LIRE = r"""() => {
  const t = s => (s || '').replace(/\s+/g, ' ').trim();
  const lien = [...document.querySelectorAll('a')].filter(a => t(a.textContent) === 'Code source sur GitHub').map(a => a.href);
  const alerte = document.querySelector('.alerte');
  return { liens: lien, titre: alerte ? t((alerte.querySelector('strong') || alerte).textContent) : null,
           astuce: alerte ? [...alerte.querySelectorAll('p')].some(p => t(p.textContent).startsWith('Souvent : une virgule')) : false,
           message: alerte ? t(alerte.innerText).slice(0, 300) : '' };
}"""


def copie_modifiee(nom, modifs):
    """Une copie du site ; modifs : [(fichier, motif regex, remplacement)]. (dossier, motif introuvable ou None)."""
    d = cadre.copie(source, travail, nom)
    for fichier, motif, remplacement in modifs:
        chemin = os.path.join(d, fichier)
        texte = commun.lire(chemin)
        nouveau = re.sub(motif, remplacement, texte, count=1, flags=re.M)
        if nouveau == texte:
            return d, "%s : %s" % (fichier, motif)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(nouveau)
    return d, None


def lire(nav, d):
    resultats = {}
    with cadre.servir(d) as base:
        for chemin in ("", "snt/"):
            ctx = nav.new_context(viewport={"width": 1000, "height": 800})
            page = ctx.new_page()
            erreurs = []
            page.on("pageerror", lambda e: erreurs.append(str(e).splitlines()[0]))
            page.goto(base + "/" + chemin, wait_until="networkidle", timeout=45000)
            infos = page.evaluate(LIRE)
            infos["erreurs"] = erreurs
            resultats[chemin or "accueil"] = infos
            ctx.close()
    return resultats


def cas_page(nav, titre, nom, modifs, attendu):
    """attendu(page, infos) -> liste de problèmes."""
    d, introuvable = copie_modifiee(nom, modifs)
    if introuvable:
        bilan.verifier(titre, ["motif introuvable : " + introuvable])
    else:
        for page, infos in lire(nav, d).items():
            pb = attendu(page, infos)
            bilan.verifier("%s (%s)" % (titre, page), pb, "relevé : %r" % infos if pb else "")
    shutil.rmtree(d, ignore_errors=True)


def lien_vers(adresse, titre=None, astuce=False, erreurs_js=False):
    def verifier(page, infos):
        pb = []
        if infos["liens"] != [adresse]:
            pb.append("liens %r au lieu de [%r]" % (infos["liens"], adresse))
        if infos["titre"] != titre:
            pb.append("encadré %r au lieu de %r" % (infos["titre"], titre))
        if infos["titre"] and infos["astuce"] != astuce:
            pb.append("astuce de la virgule %s" % ("absente" if astuce else "affichée"))
        if not erreurs_js and infos["erreurs"]:
            pb.append("erreurs JavaScript : %r" % infos["erreurs"])
        return pb
    return verifier


def premiere_vraie_ressource(remplacement):
    """La première ressource réelle de snt/ressources.js (pas l'exemple en commentaire de l'en-tête)."""
    return ("snt/ressources.js", r"^ressource\(\{$", remplacement)


with sync_playwright() as p:
    nav = commun.lancer(p)
    # ── le lien du pied de page et le réglage depot ─────────────────────────────
    cas_page(nav, "depot tel quel : lien vers le dépôt du site", "tel-quel", [], lien_vers(D))
    cas_page(nav, "depot en adresse complète .git : raccourci", "adresse-git",
             [DEPOT + ('  depot: "https://github.com/babash/Babash-NSI-SNT.git/",',)], lien_vers(D))
    cas_page(nav, "depot d'un autre dépôt : le lien le suit", "autre-depot",
             [DEPOT + ('  depot: "quelquun/Autre-Site",',)], lien_vers("https://github.com/quelquun/Autre-Site"))
    cas_page(nav, "depot mal écrit : encadré « réglages », lien vers le dépôt par défaut, sans l'astuce", "depot-fautif",
             [DEPOT + ('  depot: "babash Babash-NSI-SNT",',)], lien_vers(D, TITRE_R, astuce=False))
    cas_page(nav, "depot absent : dépôt par défaut, sans erreur", "depot-absent", [DEPOT + ("",)], lien_vers(D))
    # ── l'encadré d'erreur : titre et astuce ────────────────────────────────────
    cas_page(nav, "champ inconnu dans SNT : encadré « liste », sans l'astuce", "champ-inconnu",
             [premiere_vraie_ressource("ressource({ champInconnu: 1,")],
             lambda page, i: lien_vers(D, TITRE_L, astuce=False)(page, i))
    cas_page(nav, "virgule retirée dans SNT : encadré « liste », avec l'astuce", "virgule",
             [("snt/ressources.js", r'^(ressource\(\{\n  titre: "[^"\n]*"),$', r"\1")],
             lambda page, i: lien_vers(D, TITRE_L, astuce=True, erreurs_js=True)(page, i))
    cas_page(nav, "depot mal écrit et virgule retirée : encadré « les deux », avec l'astuce", "les-deux",
             [DEPOT + ('  depot: "babash Babash-NSI-SNT",',), ("snt/ressources.js", r'^(ressource\(\{\n  titre: "[^"\n]*"),$', r"\1")],
             lambda page, i: lien_vers(D, TITRE_RL, astuce=True, erreurs_js=True)(page, i))
    nav.close()

# ── verifier-site.py : fonctions code_source() et depot() ──────────────────────
verif = os.path.join(source, ".github", "verifier-site.py")
spec = importlib.util.spec_from_file_location("verifier_site", verif)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
NBSP = chr(0xA0)
unitaires = [
    ("lien simple", '<p>x <a href="%s">Code source sur GitHub</a>.</p>' % D, [D]),
    ("espaces insécables en entité", '<a href="%s">Code&nbsp;source sur&nbsp;GitHub</a>' % D, [D]),
    ("espace insécable écrite telle quelle", '<a href="%s">Code source sur%sGitHub</a>' % (D, NBSP), [D]),
    ("icône et retours à la ligne", '<a class="x"\n href="%s/"><svg aria-hidden="true"><path d="M0"/></svg>\n  Code source\n sur GitHub </a>' % D, [D]),
    ("guillemets simples, ancre retirée", "<a href='%s#readme'>Code source sur GitHub</a>" % D, [D]),
    ("casse du texte ignorée", '<a href="%s">code source sur github</a>' % D, [D]),
    ("texte différent : non retenu", '<a href="%s">Code source</a>' % D, []),
    ("adresse hors de GitHub : non retenue", '<a href="https://gitlab.com/a/b">Code source sur GitHub</a>', []),
    ("deux liens", '<a href="https://github.com/a/b">Code source sur GitHub</a><a href="%s">Code source sur GitHub</a>' % D,
     ["https://github.com/a/b", D]),
]
for nom, dom, attendu in unitaires:
    obtenu = v.code_source(dom)
    bilan.verifier("verifier-site.py, code_source : " + nom, [] if obtenu == attendu else ["%r au lieu de %r" % (obtenu, attendu)])
for nom, texte, attendu in [
    ("guillemets doubles", 'reglages({\n  depot: "babash/Babash-NSI-SNT",\n});', "babash/Babash-NSI-SNT"),
    ("guillemets simples", "reglages({\n  depot: 'quelquun/Son-Site',\n});", "quelquun/Son-Site"),
    ("adresse complète en .git", 'reglages({\n  depot: "https://github.com/quelquun/Son-Site.git/",\n});', "quelquun/Son-Site"),
    ("valeur fautive : dépôt par défaut", 'reglages({\n  depot: "babash Babash-NSI-SNT",\n});', "babash/Babash-NSI-SNT"),
    ("réglage absent : dépôt par défaut", 'reglages({\n  titre: "x",\n});', "babash/Babash-NSI-SNT"),
]:
    v.lire = lambda chemin, t=texte: t
    obtenu = v.depot()
    bilan.verifier("verifier-site.py, depot : " + nom, [] if obtenu == attendu else ["%r au lieu de %r" % (obtenu, attendu)])

# ── verifier-site.py : le contrôle complet, sur trois copies ───────────────────
PAGES = ("accueil", "snt", "nsi-premiere", "nsi-terminale", "pp", "autres")
for titre, nom, modifs, code_attendu, motifs in [
    ("verifier-site.py sur la copie telle quelle : code 0", "verif-tel-quel", [], 0,
     [r"Lien « Code source sur GitHub » : \d+ / \d+ pages déposées", r"Tout s'affiche correctement"]),
    ("verifier-site.py, lien retiré du pied de page : code 1, les 6 pages citées", "verif-sans-lien",
     [("assets/site.js", re.escape("'Code source sur GitHub'), '.');"), "'Code source'), '.');")], 1,
     [r"^ - %s : pas de lien « Code source sur GitHub » vers %s$" % (p, re.escape(D)) for p in PAGES]),
    ("verifier-site.py, lien vers un autre dépôt : code 1", "verif-autre-depot",
     [("assets/site.js", re.escape("return 'https://github.com/' + (depotSite || DEPOT);"),
       "return 'https://github.com/autre/depot';")], 1,
     [r"^ - accueil : pas de lien « Code source sur GitHub » vers %s \(liens trouvés : https://github\.com/autre/depot\)$" % re.escape(D)]),
]:
    d, introuvable = copie_modifiee(nom, modifs)
    if introuvable:
        bilan.verifier(titre, ["motif introuvable : " + introuvable])
        continue
    with cadre.servir(d) as base:
        r = subprocess.run([sys.executable, "-I", "-B", os.path.join(d, ".github", "verifier-site.py"), base],
                           capture_output=True, text=True, timeout=1200)
    sortie = r.stdout + r.stderr
    pb = [] if r.returncode == code_attendu else ["code %d au lieu de %d" % (r.returncode, code_attendu)]
    pb += ["absent de la sortie : « %s »" % m for m in motifs if not re.search(m, sortie, re.M)]
    bilan.verifier(titre, pb, sortie[-1500:] if pb else "")
    shutil.rmtree(d, ignore_errors=True)

bilan.terminer()
