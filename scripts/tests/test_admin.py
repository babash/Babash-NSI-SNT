#!/usr/bin/env python3
"""Tests de l'espace administrateur (T51) dans Chromium, avec une API GitHub simulée.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_admin.py [--racine DOSSIER_DU_DEPOT] [--travail DOSSIER] [--captures DOSSIER]

Le test prépare une copie de travail (donnees/ copié, le reste relié par des liens symboliques), y construit la
bibliothèque, la sert en local et joue des scénarios dans Chromium. Toute requête vers api.github.com est
interceptée par un faux GitHub (un dépôt en mémoire, tiré de la copie) : aucun jeton réel, aucune écriture sur le
vrai dépôt. Le faux jeton est fabriqué par le test.
Scénarios : sans jeton (liste, fiche, validation, téléchargement de l'archive, brouillon retrouvé, onglets au
clavier et par cases, aperçu) ; avec jeton (saisie cachée, vérification, enregistrement en un commit, en-têtes,
contenu écrit, conflit, « Oublier le jeton ») ; rendu à 320 et 1440 px, en clair et en obscur.
Il faut Playwright et Chromium. Code de retour : 0 si tous les cas passent, 1 sinon.
"""
import argparse
import base64
import datetime
import functools
import hashlib
import http.server
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import zipfile

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEFAUT = os.path.dirname(os.path.dirname(ICI))
DEPOT = "babash/Babash-NSI-SNT"
FAUX_JETON = "github_pat_" + "T" * 22 + "_" + "e" * 59   # fabriqué pour le test, forme d'un jeton fin
FICHE = "td1-poo"
CHEMIN = f"donnees/ressources/{FICHE}.json"

echecs = []
cas = [0]


def verifier(titre, ok, detail=""):
    cas[0] += 1
    print(("  ok     " if ok else "  ÉCHEC  ") + titre)
    if not ok:
        echecs.append(titre)
        if detail:
            print("         " + str(detail).replace("\n", "\n         ")[:1500])


class Discret(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def preparer(racine, travail):
    d = tempfile.mkdtemp(prefix="test-admin-", dir=travail)
    for nom in os.listdir(racine):
        if nom not in (".git", "donnees"):
            os.symlink(os.path.join(racine, nom), os.path.join(d, nom))
    source = os.path.join(racine, "donnees")
    construits = {"bibliotheque.json", "bibliotheque-complete.json", "bibliotheque-textes.json"}
    shutil.copytree(source, os.path.join(d, "donnees"),
                    ignore=lambda dossier, noms: [x for x in noms if dossier == source and (x in construits or x.endswith(".provisoire"))])
    subprocess.run([sys.executable, "-B", os.path.join(racine, "scripts", "construire_bibliotheque.py"),
                    "--racine", d, "--sans-textes"], check=True, capture_output=True)
    return d


def sha_blob(octets):
    return hashlib.sha1(b"blob %d\0" % len(octets) + octets).hexdigest()


class FauxGitHub:
    """Un dépôt GitHub en mémoire : les fichiers de la copie, une branche main, l'API utile à l'admin."""

    def __init__(self, copie):
        self.fichiers = {}
        for dossier, sous, noms in os.walk(copie, followlinks=True):
            sous[:] = [s for s in sous if not s.startswith(".") and s != "__pycache__"]
            for n in noms:
                p = os.path.join(dossier, n)
                rel = os.path.relpath(p, copie).replace(os.sep, "/")
                if rel.startswith("donnees/") or rel.endswith((".html", ".pdf", ".ipynb", ".py", "/")):
                    if re.fullmatch(r"donnees/bibliotheque[^/]*\.json", rel):
                        continue   # construits à la publication, jamais dans le dépôt
                    with open(p, "rb") as f:
                        self.fichiers[rel] = f.read() if rel.startswith("donnees/") else b"x"
        self.blobs = {}
        self.arbres = {}
        self.commits = {}
        self.tete = self.nouveau_commit(dict(self.fichiers), None, "initial")
        self.requetes = []
        self.ecriture = True

    def arbre(self, fichiers):
        entrees = {}
        for p, o in fichiers.items():
            s = sha_blob(o)
            self.blobs[s] = o
            entrees[p] = s
        tid = hashlib.sha1(json.dumps(entrees, sort_keys=True).encode()).hexdigest()
        self.arbres[tid] = entrees
        return tid

    def nouveau_commit(self, fichiers, parent, message):
        tid = self.arbre(fichiers)
        cid = hashlib.sha1(f"{tid}{parent}{message}".encode()).hexdigest()
        self.commits[cid] = {"arbre": tid, "parent": parent, "message": message}
        return cid

    def changer_sur_main(self, chemin, octets):
        """Quelqu'un d'autre modifie un fichier sur main (pour le conflit)."""
        f = dict(self.arbres[self.commits[self.tete]["arbre"]])
        f = {p: self.blobs[s] for p, s in f.items()}
        f[chemin] = octets
        self.tete = self.nouveau_commit(f, self.tete, "changement extérieur")

    def liste_arbre(self, tid):
        entrees = self.arbres[tid]
        dossiers = set()
        for p in entrees:
            morceaux = p.split("/")
            for i in range(1, len(morceaux)):
                dossiers.add("/".join(morceaux[:i]))
        return ([{"path": d, "type": "tree", "sha": "d" * 40} for d in sorted(dossiers)]
                + [{"path": p, "type": "blob", "sha": s, "mode": "100644"} for p, s in sorted(entrees.items())])

    def repondre(self, route):
        req = route.request
        url = req.url
        corps = req.post_data_json if req.method in ("POST", "PATCH") else None
        self.requetes.append({"methode": req.method, "url": url, "auth": req.headers.get("authorization", ""), "corps": corps})
        if req.headers.get("authorization") != "Bearer " + FAUX_JETON:
            return route.fulfill(status=401, json={"message": "Bad credentials"})
        m = re.match(r"https://api\.github\.com/repos/" + re.escape(DEPOT) + r"(/[^?]*)?(\?.*)?$", url)
        if not m:
            return route.fulfill(status=404, json={"message": "Not Found"})
        chemin = m.group(1) or ""
        tete = self.commits[self.tete]
        if req.method == "GET" and chemin == "":
            return route.fulfill(json={"full_name": DEPOT, "permissions": {"pull": True, "push": self.ecriture}})
        if req.method == "GET" and chemin.startswith("/git/trees/"):
            cle = chemin[len("/git/trees/"):]
            tid = tete["arbre"] if cle == "main" else cle
            return route.fulfill(json={"sha": tid, "tree": self.liste_arbre(tid), "truncated": False})
        if req.method == "GET" and chemin.startswith("/contents/"):
            p = chemin[len("/contents/"):]
            s = self.arbres[tete["arbre"]].get(p)
            if not s:
                return route.fulfill(status=404, json={"message": "Not Found"})
            return route.fulfill(json={"path": p, "sha": s, "encoding": "base64", "content": base64.b64encode(self.blobs[s]).decode()})
        if req.method == "GET" and chemin == "/git/ref/heads/main":
            return route.fulfill(json={"ref": "refs/heads/main", "object": {"sha": self.tete, "type": "commit"}})
        if req.method == "GET" and chemin.startswith("/git/commits/"):
            c = self.commits[chemin.rsplit("/", 1)[1]]
            return route.fulfill(json={"sha": chemin.rsplit("/", 1)[1], "tree": {"sha": c["arbre"]}})
        if req.method == "GET" and chemin.startswith("/git/blobs/"):
            s = chemin.rsplit("/", 1)[1]
            return route.fulfill(json={"sha": s, "encoding": "base64", "content": base64.b64encode(self.blobs[s]).decode()})
        if not self.ecriture:
            return route.fulfill(status=403, json={"message": "Resource not accessible by personal access token"})
        if req.method == "POST" and chemin == "/git/blobs":
            o = base64.b64decode(corps["content"]) if corps.get("encoding") == "base64" else corps["content"].encode()
            s = sha_blob(o)
            self.blobs[s] = o
            return route.fulfill(status=201, json={"sha": s})
        if req.method == "POST" and chemin == "/git/trees":
            base = dict(self.arbres[corps["base_tree"]])
            for e in corps["tree"]:
                base[e["path"]] = e["sha"]
            tid = hashlib.sha1(json.dumps(base, sort_keys=True).encode()).hexdigest()
            self.arbres[tid] = base
            return route.fulfill(status=201, json={"sha": tid})
        if req.method == "POST" and chemin == "/git/commits":
            cid = hashlib.sha1(json.dumps(corps, sort_keys=True).encode()).hexdigest()
            self.commits[cid] = {"arbre": corps["tree"], "parent": corps["parents"][0], "message": corps["message"]}
            return route.fulfill(status=201, json={"sha": cid, "message": corps["message"]})
        if req.method == "PATCH" and chemin == "/git/refs/heads/main":
            if self.commits[corps["sha"]]["parent"] != self.tete and not corps.get("force"):
                return route.fulfill(status=422, json={"message": "Update is not a fast forward"})
            self.tete = corps["sha"]
            return route.fulfill(json={"ref": "refs/heads/main", "object": {"sha": self.tete}})
        return route.fulfill(status=404, json={"message": "Not Found"})

    def fichier_sur_main(self, chemin):
        return self.blobs[self.arbres[self.commits[self.tete]["arbre"]][chemin]]


def page_neuve(nav, base, largeur=1280, schema="light", faux=None):
    ctx = nav.new_context(viewport={"width": largeur, "height": 900}, color_scheme=schema, accept_downloads=True)
    erreurs = []
    vers_github = []
    if faux:
        ctx.route("https://api.github.com/**", faux.repondre)
    else:
        ctx.route("https://api.github.com/**", lambda r: (vers_github.append(r.request.url), r.fulfill(status=500)))
    ctx.route(re.compile(r"^https://fonts\.(googleapis|gstatic)\.com/.*"), lambda r: r.fulfill(status=200, body=""))
    page = ctx.new_page()
    page.on("pageerror", lambda e: erreurs.append(str(e)))
    page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
    page.on("dialog", lambda d: d.accept("Pour aller plus loin") if d.type == "prompt" else d.accept())
    return ctx, page, erreurs, vers_github


def attendre(page, ms=250):
    page.wait_for_timeout(ms)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--racine", default=RACINE_DEFAUT)
    p.add_argument("--travail")
    p.add_argument("--captures")
    a = p.parse_args()
    travail = a.travail or tempfile.mkdtemp(prefix="test-admin-")
    os.makedirs(travail, exist_ok=True)
    copie = preparer(a.racine, travail)
    gestion = functools.partial(Discret, directory=copie)
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{serveur.server_address[1]}"
    aujourdhui = datetime.date.today().isoformat()
    origine = open(os.path.join(copie, CHEMIN), encoding="utf-8").read()

    try:
        with sync_playwright() as pw:
            nav = pw.chromium.launch()

            print("Sans jeton")
            ctx, page, erreurs, vers_github = page_neuve(nav, base)
            page.goto(base + "/admin/", wait_until="networkidle")
            n = page.locator(".admin-liste > li").count()
            total = len(json.load(open(os.path.join(copie, "donnees", "bibliotheque-complete.json")))["ressources"])
            verifier(f"la liste montre toutes les fiches ({n} sur {total})", n == total and n > 0)
            verifier("la page n'est pas indexée (noindex)", "noindex" in (page.locator('meta[name="robots"]').get_attribute("content") or ""))
            page.select_option("#admin-statut", "a-revoir")
            n2 = page.locator(".admin-liste > li").count()
            verifier(f"filtre « À revoir » : {n2} fiches", 0 < n2 <= n)
            page.select_option("#admin-statut", "")
            page.fill("#admin-q", "POO TD 1")
            verifier("recherche « POO TD 1 » : le TD 1 de POO", page.locator(f'.admin-liste a[href="#/fiche/{FICHE}"]').count() == 1)

            page.goto(base + f"/admin/#/fiche/{FICHE}")
            page.wait_for_selector("#champ-titre")
            page.check("#champ-statut-prete")
            page.click('[data-cle="ajouter-note"]')
            attendre(page)
            notes = page.locator(".admin-note textarea")
            notes.last.fill("Séance du jour : très bien passé.")
            page.uncheck("#doc-1-eleve")
            attendre(page)
            barre = page.locator(".admin-barre-bas").inner_text()
            verifier("barre du bas : « 1 fichier modifié »", "1 fichier modifié" in barre, barre)
            verifier("le document caché porte son badge « caché : élèves »", page.locator(".admin-doc").nth(1).locator(".badge.cache").inner_text() == "caché : élèves")

            titre = page.locator("#champ-titre").input_value()
            page.fill("#champ-titre", "")
            attendre(page)
            bloque = page.locator(".admin-barre-bas button.principal").is_disabled()
            verifier("titre vidé : erreur affichée, téléchargement bloqué", bloque and "Titre" not in "" and page.locator(".alerte").count() >= 1)
            page.fill("#champ-titre", titre)
            attendre(page)
            verifier("titre rétabli : plus d'erreur", page.locator(".admin-barre-bas button.principal").is_enabled())

            page.goto(base + "/admin/#/changements")
            attendre(page)
            texte = page.locator(".admin-changements").inner_text()
            verifier("changements : le statut, les documents et les notes", "« a-revoir » → « prete »" in texte and "notes" in texte and "documents" in texte, texte)
            with page.expect_download() as tele:
                page.click('[data-cle="telecharger-2"]')
            chemin_zip = tele.value.path()
            with zipfile.ZipFile(chemin_zip) as z:
                noms = z.namelist()
                contenu = z.read(CHEMIN).decode("utf-8") if CHEMIN in noms else ""
            fiche = json.loads(contenu) if contenu else {}
            verifier("archive .zip : le fichier avec son chemin", noms == [CHEMIN], noms)
            verifier("archive : statut « prete », note, document caché des élèves, date de modification",
                     fiche.get("statut") == "prete" and fiche["notes"][-1]["texte"].startswith("Séance du jour")
                     and fiche["documents"][1]["visible"]["eleve"] is False and fiche["dates"].get("modification") == aujourdhui)
            lignes_avant = set(origine.splitlines())
            nouvelles = [l for l in contenu.splitlines() if l not in lignes_avant]
            verifier(f"archive : le texte d'origine est gardé ({len(nouvelles)} lignes nouvelles)", 0 < len(nouvelles) <= 12, "\n".join(nouvelles))
            # La fiche téléchargée passe la validation du script
            essai = tempfile.mkdtemp(prefix="essai-", dir=travail)
            for nom in os.listdir(copie):
                if nom != "donnees":
                    os.symlink(os.path.join(copie, nom), os.path.join(essai, nom))
            shutil.copytree(os.path.join(copie, "donnees"), os.path.join(essai, "donnees"))
            with open(os.path.join(essai, CHEMIN), "w", encoding="utf-8") as f:
                f.write(contenu)
            r = subprocess.run([sys.executable, "-B", os.path.join(a.racine, "scripts", "valider_donnees.py"), "--racine", essai],
                               capture_output=True, text=True)
            verifier("la fiche téléchargée passe scripts/valider_donnees.py (0 erreur)", r.returncode == 0, r.stdout[-800:])

            page.reload(wait_until="networkidle")
            attendre(page, 400)
            verifier("après un rechargement : le changement est retrouvé", "retrouvé" in page.locator(".admin-message").inner_text()
                     and "1 fichier modifié" in page.locator(".admin-barre-bas").inner_text())

            # Les onglets : au clavier, par cases, aperçu
            page.goto(base + "/admin/#/onglets/snt")
            page.wait_for_selector(".admin-section")
            vitrine = json.load(open(os.path.join(copie, "donnees", "vitrine.json")))
            snt = vitrine["rubriques"][0]
            j = next(i for i, s in enumerate(snt["sections"]) if len(s["ressources"]) >= 2)
            premiers = snt["sections"][j]["ressources"][:2]
            page.focus(f'[data-cle="sec-{j}-res-1-monter"]')
            page.keyboard.press("Enter")
            attendre(page)
            ordre = page.locator(".admin-section").nth(j).locator(":scope > .admin-res > .admin-ordre > li code").all_inner_texts()[:2]
            verifier("au clavier : « monter » inverse les deux premières ressources", ordre == premiers[::-1], ordre)
            focus = page.evaluate("document.activeElement.getAttribute('data-cle')")
            verifier("le focus reste sur la ressource déplacée", focus == f"sec-{j}-res-0-descendre", focus)
            section = page.locator(".admin-section").nth(j).locator(":scope > .admin-res")
            section.locator(":scope > .admin-choisir > summary").click()
            section.locator(":scope > .admin-choisir input[type=search]").fill("cybercase")
            attendre(page)
            case = section.locator(':scope > .admin-choisir .admin-choix input[type="checkbox"]').first
            deja = case.is_checked()
            if not deja:
                case.click()
            attendre(page)
            verifier("après la case : la liste de cases reste ouverte, avec sa recherche",
                     section.locator(":scope > .admin-choisir").get_attribute("open") is not None
                     and section.locator(":scope > .admin-choisir input[type=search]").input_value() == "cybercase")
            ids = page.locator(".admin-section").nth(j).locator(":scope > .admin-res > .admin-ordre > li code").all_inner_texts()
            verifier("par case à cocher : la ressource s'ajoute à la section", "cybercase" in ids, ids)
            page.click('[data-cle="apercu"]')
            cadre = page.frame_locator(".admin-iframe")
            cadre.locator("li.res").first.wait_for(timeout=10000)
            verifier("aperçu : le bandeau « Aperçu de l'admin »", cadre.locator(".apercu").count() == 1)
            titres = cadre.locator(f"section.theme").nth(j).locator("li.res .titre").all_inner_texts()
            attendu = [json.load(open(os.path.join(copie, "donnees", "ressources", f"{x}.json")))["titre"] for x in premiers[::-1]]
            verifier("aperçu : le nouvel ordre", titres[:2] == attendu, (titres[:2], attendu))
            page.goto(base + "/admin/#/onglets/a-la-une")
            attendre(page, 400)
            avant = page.locator(".admin-une > li").count()
            page.click('[data-cle="une-0-retirer"]')
            attendre(page)
            verifier("à la une : une ressource retirée", page.locator(".admin-une > li").count() == avant - 1)
            verifier("sans jeton : aucune requête vers l'API GitHub", not vers_github, vers_github)
            verifier("sans jeton : aucune erreur JavaScript", not erreurs, erreurs)
            ctx.close()

            print("Avec jeton (API GitHub simulée)")
            faux = FauxGitHub(copie)
            ctx, page, erreurs, _ = page_neuve(nav, base, faux=faux)
            page.goto(base + "/admin/#/jeton", wait_until="networkidle")
            champ = page.locator("#jeton")
            verifier("le champ du jeton est masqué (type password)", champ.get_attribute("type") == "password")
            champ.fill(FAUX_JETON)
            page.click('[data-cle="jeton-enregistrer"]')
            page.wait_for_selector(".admin-message.ok", timeout=10000)
            verifier("jeton vérifié : écriture permise", "permet d'écrire" in page.locator(".admin-message").inner_text())
            verifier("le jeton n'est jamais affiché", FAUX_JETON not in page.content() and champ.input_value() == "")
            stockage = page.evaluate("JSON.stringify(Object.assign({}, localStorage)) + JSON.stringify(Object.assign({}, sessionStorage))")
            verifier("le jeton est gardé en mémoire seulement, le temps de la visite (rien dans le navigateur)",
                     FAUX_JETON not in stockage and "le temps de la visite" in page.locator(".admin-garde").inner_text())

            page.goto(base + f"/admin/#/fiche/{FICHE}")
            page.wait_for_selector("#champ-titre")
            lu = [r for r in faux.requetes if "/contents/" in r["url"]]
            verifier("avec jeton : la fiche est relue par l'API (à jour)", any(CHEMIN in r["url"] for r in lu))
            page.check("#champ-statut-prete")
            page.fill("#champ-accroche", "Une accroche réécrite dans l'admin.")
            attendre(page)
            faux.requetes.clear()
            page.click('[data-cle="enregistrer"]')
            page.wait_for_selector(".admin-message.ok", timeout=15000)
            ecritures = [(r["methode"], r["url"].split(DEPOT)[1]) for r in faux.requetes if r["methode"] != "GET"]
            verifier("un seul commit : blob, arbre, commit, puis main avancée sans forcer",
                     [e[0] for e in ecritures] == ["POST", "POST", "POST", "PATCH"]
                     and ecritures[-1][1] == "/git/refs/heads/main"
                     and faux.requetes[-1]["corps"]["force"] is False, ecritures)
            commit = faux.commits[faux.tete]
            verifier("message du commit : « [admin] … »", commit["message"].startswith("[admin] ") and FICHE in commit["message"], commit["message"])
            ecrit = json.loads(faux.fichier_sur_main(CHEMIN).decode("utf-8"))
            verifier("le fichier écrit sur main : statut, accroche et date de modification",
                     ecrit["statut"] == "prete" and ecrit["accroche"] == "Une accroche réécrite dans l'admin." and ecrit["dates"]["modification"] == aujourdhui)
            verifier("en-têtes : le jeton seulement dans « Authorization », jamais dans une adresse",
                     all(r["auth"] == "Bearer " + FAUX_JETON for r in faux.requetes) and not any(FAUX_JETON in r["url"] for r in faux.requetes))
            verifier("après l'enregistrement : plus rien en attente", page.locator(".admin-barre-bas").is_hidden())

            # Conflit : le fichier change sur main pendant qu'on le modifie
            page.fill("#champ-accroche", "Une autre accroche.")
            attendre(page)
            autre = json.loads(faux.fichier_sur_main(CHEMIN))
            autre["duree"] = "35 min"
            faux.changer_sur_main(CHEMIN, (json.dumps(autre, ensure_ascii=False, indent=2) + "\n").encode())
            tete_avant = faux.tete
            faux.requetes.clear()
            page.click('[data-cle="enregistrer"]')
            page.wait_for_selector(".admin-message.erreur", timeout=15000)
            msg = page.locator(".admin-message").inner_text()
            verifier("conflit : rien n'est écrit, le message le dit", faux.tete == tete_avant
                     and not any(r["methode"] != "GET" for r in faux.requetes) and "changé sur GitHub" in msg, msg)
            page.click('[data-cle="conflit-recharger"]')
            page.goto(base + f"/admin/#/fiche/{FICHE}")
            page.wait_for_selector("#champ-duree")
            verifier("conflit : après « Recharger », la version de main", page.locator("#champ-duree").input_value() == "35 min")

            # Écriture refusée par GitHub (jeton en lecture seule)
            faux.ecriture = False
            page.fill("#champ-accroche", "Encore une accroche.")
            attendre(page)
            page.click('[data-cle="enregistrer"]')
            page.wait_for_selector(".admin-message.erreur", timeout=15000)
            verifier("écriture refusée (403) : message clair, rien d'écrit", "Contents : Read and write" in page.locator(".admin-message").inner_text())
            faux.ecriture = True

            page.goto(base + "/admin/#/jeton")
            page.click('[data-cle="jeton-oublier"]')
            attendre(page)
            verifier("« Oublier le jeton » : la page ne l'a plus", "Aucun jeton" in page.locator(".admin-vue").inner_text())
            page.fill("#jeton", FAUX_JETON)
            page.click('[data-cle="jeton-enregistrer"]')
            page.wait_for_selector(".admin-message.ok", timeout=10000)
            page.reload(wait_until="networkidle")
            page.goto(base + "/admin/#/jeton")
            attendre(page, 300)
            verifier("après un rechargement : plus de jeton (garde en mémoire)", "Aucun jeton" in page.locator(".admin-vue").inner_text())
            attendues = [e for e in erreurs if "status of 403" in e]   # le refus simulé plus haut
            verifier("avec jeton : aucune erreur JavaScript (hors le refus 403 simulé)", len(attendues) <= 1 and not [e for e in erreurs if e not in attendues], erreurs)
            ctx.close()

            print("Chemins refusés (brouillon et fichiers récents du navigateur)")
            faux = FauxGitHub(copie)
            ctx, page, erreurs, _ = page_neuve(nav, base, faux=faux)
            page.goto(base + "/admin/", wait_until="networkidle")
            notions = open(os.path.join(copie, "donnees", "referentiels", "notions.json"), encoding="utf-8").read()
            bonne = json.loads(origine)
            bonne["statut"] = "prete"
            piege = dict(bonne, id="notions")
            brouillon = {
                CHEMIN: {"base": origine, "sha": None, "courant": bonne},
                "donnees/referentiels/notions.json": {"base": notions, "sha": None, "courant": piege},
                "donnees/ressources/../../assets/site.json": {"base": origine, "sha": None, "courant": bonne},
                "assets/td1-poo.json": {"base": origine, "sha": None, "courant": bonne},
            }
            recents = {"assets/site.js": {"texte": "piege", "quand": 9e15}}
            page.evaluate("([b, r]) => { localStorage.setItem('admin-brouillon', JSON.stringify(b)); localStorage.setItem('admin-recents', JSON.stringify(r)); }",
                          [brouillon, recents])
            page.reload(wait_until="networkidle")
            attendre(page, 400)
            msg = page.locator(".admin-message").inner_text()
            verifier("brouillon piégé : les chemins refusés sont signalés", "ignorés" in msg and "donnees/referentiels/notions.json" in msg
                     and "assets/site.js" in msg, msg)
            verifier("brouillon piégé : seul le changement de la fiche reste en attente", "1 fichier modifié" in page.locator(".admin-barre-bas").inner_text())
            restes = page.evaluate("Object.keys(JSON.parse(localStorage.getItem('admin-brouillon') || '{}'))")
            verifier("brouillon piégé : les clés refusées sont retirées du navigateur", restes == [CHEMIN], restes)
            page.goto(base + "/admin/#/changements")
            attendre(page)
            with page.expect_download() as tele:
                page.click('[data-cle="telecharger-2"]')
            with zipfile.ZipFile(tele.value.path()) as z:
                noms = z.namelist()
            verifier("brouillon piégé : l'archive ne contient que la fiche", noms == [CHEMIN], noms)
            page.goto(base + "/admin/#/jeton")
            page.fill("#jeton", FAUX_JETON)
            page.click('[data-cle="jeton-enregistrer"]')
            page.wait_for_selector(".admin-message.ok", timeout=10000)
            faux.requetes.clear()
            page.goto(base + "/admin/#/changements")
            attendre(page)
            page.click('[data-cle="enregistrer-2"]')
            page.wait_for_selector(".admin-message.ok", timeout=15000)
            arbres = [r["corps"] for r in faux.requetes if r["methode"] == "POST" and r["url"].endswith("/git/trees")]
            chemins = [e["path"] for t in arbres for e in t["tree"]]
            verifier("brouillon piégé : le commit n'écrit que la fiche ; le thésaurus est intact",
                     chemins == [CHEMIN] and faux.fichier_sur_main("donnees/referentiels/notions.json").decode("utf-8") == notions, chemins)
            verifier("brouillon piégé : la vue « Changements » s'affiche sans erreur JavaScript", not erreurs, erreurs)
            ctx.close()

            print("Rendu")
            vues = [("liste", "/admin/"), ("fiche", f"/admin/#/fiche/{FICHE}"), ("onglets", "/admin/#/onglets/snt"),
                    ("changements", "/admin/#/changements"), ("jeton", "/admin/#/jeton")]
            for schema in ("light", "dark"):
                for largeur in (320, 768, 1440):
                    ctx, page, erreurs, _ = page_neuve(nav, base, largeur, schema)
                    for nom, adresse in vues:
                        page.goto(base + adresse, wait_until="networkidle")
                        attendre(page, 500)
                        if nom == "fiche":
                            page.check("#champ-statut-prete")   # pour montrer la barre du bas
                            attendre(page)
                        deborde = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                        if deborde > 0:
                            verifier(f"{nom} à {largeur} px ({schema}) : pas de défilement horizontal", False, f"{deborde} px")
                        if a.captures and largeur in (320, 1440):
                            os.makedirs(a.captures, exist_ok=True)
                            page.screenshot(path=os.path.join(a.captures, f"admin-{nom}-{largeur}-{'clair' if schema == 'light' else 'obscur'}.png"),
                                            full_page=largeur == 1440)
                    verifier(f"rendu à {largeur} px, {'clair' if schema == 'light' else 'obscur'} : 5 vues, sans défilement horizontal ni erreur JavaScript",
                             not erreurs, erreurs)
                    ctx.close()
            nav.close()
    finally:
        serveur.shutdown()
        if not a.travail:
            shutil.rmtree(travail, ignore_errors=True)

    print(f"\n{cas[0]} cas, {len(echecs)} échec(s)")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
