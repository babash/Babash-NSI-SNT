"""T12 : les scripts du contrôle en ligne décident-ils juste ? (24 vérifications, test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_t12.py COPIE_DU_SITE DOSSIER_DE_TRAVAIL

Essaie les deux scripts de scripts/ que lance le workflow verifier.yml, ceux de la copie :
  - attendre_deploiement.py : syntaxe ; decider() sur 10 suites d'états de déploiement (en ligne,
    attendre, échec, remplacé par un commit plus récent) ; servi() (les fichiers à point, comme
    .github/ ou .nojekyll, ne sont pas servis par GitHub Pages) ;
  - liens_seconde_passe.py : syntaxe ; ses commandes relever, liste et bilan, sur des rapports de
    lychee fabriqués (aucun échec, un lien mort, une panne passagère, un délai dépassé aux deux
    passes, une seconde passe incomplète ou absente, un rapport de format inattendu).
Aucun accès au réseau : les adresses sont en .example. À adapter si l'Architecte change
l'interface de ces scripts (noms des fonctions, des commandes ou des sorties).
"""
import ast
import importlib.util
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadre  # noqa: E402

source, travail = cadre.arguments(__doc__)
scripts = os.path.join(source, "scripts")
bilan = cadre.Bilan()


def ok(condition, titre, detail=""):
    bilan.verifier(titre, [] if condition else ["résultat inattendu"], detail if not condition else "")


# 1. Syntaxe
for nom in ("attendre_deploiement.py", "liens_seconde_passe.py"):
    try:
        with open(os.path.join(scripts, nom), encoding="utf-8") as f:
            ast.parse(f.read(), nom)
        ok(True, "syntaxe Python : " + nom)
    except (OSError, SyntaxError) as e:
        ok(False, "syntaxe Python : " + nom, str(e))

# 2. decider() et servi()
spec = importlib.util.spec_from_file_location("attendre_deploiement", os.path.join(scripts, "attendre_deploiement.py"))
ad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ad)
CAS = [
    (["success", "in_progress", "queued", "waiting"], False, "en_ligne"),
    (["in_progress", "queued", "waiting"], False, "attendre"),
    (["queued"], False, "attendre"),
    (["failure", "in_progress"], False, "echec"),
    (["error"], False, "echec"),
    (["inactive", "success", "in_progress"], False, "remplace"),
    (["inactive", "in_progress"], False, "remplace"),
    (None, False, "attendre"),
    (None, True, "remplace"),
    (["pending"], False, "attendre"),
]
for etats, avance, attendu in CAS:
    decision, message = ad.decider(etats, avance)
    ok(decision == attendu, "decider(%s, main_en_avance=%s) = %s (%s)" % (etats, avance, decision, message))
ok(not ad.servi(".github/workflows/verifier.yml") and not ad.servi(".nojekyll") and ad.servi("README.md")
   and ad.servi("snt/fichiers/td.html"), "servi() : fichiers à point exclus, autres inclus")

# 3. Seconde passe, sur des rapports de lychee fabriqués
lsp = os.path.join(scripts, "liens_seconde_passe.py")


def lancer(*args, env=None):
    e = dict(os.environ)
    e.pop("GITHUB_OUTPUT", None)
    e.pop("GITHUB_STEP_SUMMARY", None)
    e.update(env or {})
    r = subprocess.run([sys.executable, "-I", "-B", lsp, *args], capture_output=True, text=True, env=e, cwd=travail)
    return r.returncode, r.stdout + r.stderr


def ecrire(nom, donnees):
    chemin = os.path.join(travail, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f)
    return chemin


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return f.read()


os.makedirs(os.path.join(travail, "snt"), exist_ok=True)
with open(os.path.join(travail, "snt", "ressources.js"), "w", encoding="utf-8") as f:
    f.write('lien: "https://mort.example/a"\nlien: "https://lent.example/b"\n')
src = "file://" + os.path.join(travail, "snt", "ressources.js")
sortie = os.path.join(travail, "sorties-github.txt")

vide = ecrire("vide.json", {"total": 143, "errors": 0, "timeouts": 0, "excludes": 15, "error_map": {}})
code, txt = lancer("relever", vide, os.path.join(travail, "releve-vide.json"), env={"GITHUB_OUTPUT": sortie})
ok(code == 0 and os.path.exists(sortie) and "nombre=0" in lire(sortie), "relever : aucun échec, nombre=0", txt)
if os.path.exists(sortie):
    os.remove(sortie)

p1 = ecrire("p1.json", {"total": 143, "errors": 1, "timeouts": 1, "excludes": 15,
                        "error_map": {src: [{"url": "https://mort.example/a", "status": {"text": "404"}, "span": {"line": 1}}]},
                        "timeout_map": {src: [{"url": "https://lent.example/b", "status": {"text": "Timeout"}}]}})
releve = os.path.join(travail, "releve.json")
code, txt = lancer("relever", p1, releve, env={"GITHUB_OUTPUT": sortie})
sorties = lire(sortie) if os.path.exists(sortie) else ""
ok(code == 0 and "nombre=2" in sorties and len(sorties.splitlines()) == 2,
   "relever : 2 échecs (erreur et délai), sorties sur une ligne chacune", txt)
r = json.loads(lire(releve)) if os.path.exists(releve) else {}
ok(r.get("echecs", {}).get("https://lent.example/b", [[None, None]])[0][1] == 2,
   "relever : ligne retrouvée dans le fichier quand lychee ne la donne pas", json.dumps(r)[:500])
code, txt = lancer("liste", releve, os.path.join(travail, "a-revoir.txt"))
ok(code == 0 and lire(os.path.join(travail, "a-revoir.txt")).count("\n") == 2, "liste : 2 liens à revérifier", txt)

p2_revenu = ecrire("p2a.json", {"total": 2, "errors": 1, "timeouts": 0,
                                "error_map": {"lychee/a-revoir.txt": [{"url": "https://mort.example/a", "status": {"text": "404"}}]}})
code, txt = lancer("bilan", releve, p2_revenu)
ok(code == 1 and "Lien mort : https://mort.example/a" in txt and "lent.example/b : Timeout" in txt,
   "bilan : 1 mort (rouge), 1 panne passagère", txt)

p2_tous = ecrire("p2b.json", {"total": 2, "errors": 0, "timeouts": 0, "error_map": {}})
code, txt = lancer("bilan", releve, p2_tous)
ok(code == 0 and "**0**" in txt, "bilan : tout revenu, vert", txt)

p2_delai = ecrire("p2c.json", {"total": 2, "errors": 0, "timeouts": 1,
                               "timeout_map": {"lychee/a-revoir.txt": [{"url": "https://lent.example/b", "status": {"text": "Timeout"}}]}})
code, txt = lancer("bilan", releve, p2_delai)
ok(code == 1 and "Lien mort : https://lent.example/b" in txt, "bilan : délai dépassé aux deux passes, rouge", txt)

p2_court = ecrire("p2d.json", {"total": 1, "errors": 0, "timeouts": 0, "error_map": {}})
code, txt = lancer("bilan", releve, p2_court)
ok(code == 1 and "moins de liens" in txt, "bilan : seconde passe incomplète, les échecs restent rouges", txt)

code, txt = lancer("bilan", releve, os.path.join(travail, "absent.json"))
ok(code == 1 and "Pas de rapport de seconde passe" in txt, "bilan : rapport de seconde passe absent, rouge", txt)

incoherent = ecrire("p1x.json", {"total": 143, "errors": 3, "timeouts": 0, "fails": {}})
code, txt = lancer("relever", incoherent, os.path.join(travail, "releve-x.json"))
ok(code == 1 and "format de lychee inattendu" in txt, "relever : erreurs annoncées mais introuvables, rouge", txt)

code, txt = lancer("relever", os.path.join(travail, "inexistant.json"), os.path.join(travail, "r.json"))
ok(code == 1, "relever : rapport de première passe absent, rouge", txt)

bilan.terminer()
