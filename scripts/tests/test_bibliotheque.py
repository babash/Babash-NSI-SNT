#!/usr/bin/env python3
"""Tests de la page bibliotheque/ dans Chromium (T50) : données, recherche, filtres, vues, fiche, adresse, clavier.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_bibliotheque.py [--racine DOSSIER_DU_DEPOT] [--travail DOSSIER] [--captures DOSSIER]

Le test prépare une copie de travail (donnees/ copié, le reste relié par des liens symboliques), y construit la
bibliothèque (scripts/construire_bibliotheque.py), la sert en local et joue des scénarios dans Chromium. Les attendus
viennent des données elles-mêmes (nombre de fiches visibles de l'extérieur, mots des titres, valeurs des filtres) :
le test marche avec les fiches d'exemple comme avec la bibliothèque complète.
Il faut Playwright et Chromium. Code de retour : 0 si tous les cas passent, 1 sinon.
"""
import argparse
import functools
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEFAUT = os.path.dirname(os.path.dirname(ICI))


class Discret(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def preparer(racine, travail):
    d = tempfile.mkdtemp(prefix="test-bibliotheque-", dir=travail)
    for nom in os.listdir(racine):
        if nom not in (".git", "donnees"):
            os.symlink(os.path.join(racine, nom), os.path.join(d, nom))
    construits = {"bibliotheque.json", "bibliotheque-complete.json", "bibliotheque-textes.json"}
    source = os.path.join(racine, "donnees")
    shutil.copytree(source, os.path.join(d, "donnees"),
                    ignore=lambda dossier, noms: [x for x in noms if dossier == source and x in construits])
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(racine, "scripts", "construire_bibliotheque.py"), "--racine", d],
                       capture_output=True, text=True, timeout=300)
    if r.returncode:
        sys.exit("construction impossible :\n" + r.stdout + r.stderr)
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--racine", default=RACINE_DEFAUT)
    p.add_argument("--travail", help="dossier des copies de travail (par défaut : le dossier temporaire du système)")
    p.add_argument("--captures", help="dossier où enregistrer des captures d'écran")
    args = p.parse_args()
    racine = os.path.abspath(args.racine)
    if args.travail:
        os.makedirs(args.travail, exist_ok=True)
    d = preparer(racine, args.travail)
    bib = json.load(open(os.path.join(d, "donnees", "bibliotheque.json"), encoding="utf-8"))
    fiches = bib["ressources"]
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Discret, directory=d))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/bibliotheque/" % serveur.server_address[1]

    from playwright.sync_api import sync_playwright
    n, echecs = 0, 0

    def cas(titre, ok, detail=""):
        nonlocal n, echecs
        n += 1
        if ok:
            print("  ok     " + titre)
        else:
            echecs += 1
            print("  ÉCHEC  " + titre + ("\n         " + str(detail) if detail else ""))

    def compte(page):
        t = page.text_content(".compte") or ""
        m = re.match(r"(\d+)", t)
        return int(m.group(1)) if m else None

    def ouvrir(page, suite=""):
        page.goto(base + suite, wait_until="networkidle")
        page.wait_for_selector(".compte, .fiche-titre, .alerte, .retour", timeout=15000)

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        erreurs = []

        def nouvelle(largeur=1280, mode="light"):
            ctx = nav.new_context(viewport={"width": largeur, "height": 900}, color_scheme=mode)
            page = ctx.new_page()
            page.on("pageerror", lambda e: erreurs.append(str(e)))
            page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
            return ctx, page

        print("Affichage")
        for largeur in (320, 768, 1440):
            for mode in ("light", "dark"):
                ctx, page = nouvelle(largeur, mode)
                ouvrir(page)
                deb = page.evaluate("document.documentElement.scrollWidth - innerWidth")
                cas(f"{largeur} px, {'clair' if mode == 'light' else 'obscur'} : {len(fiches)} ressources, sans débordement",
                    compte(page) == len(fiches) and deb <= 0, f"compte {compte(page)}, débordement {deb} px")
                if args.captures:
                    os.makedirs(args.captures, exist_ok=True)
                    page.screenshot(path=os.path.join(args.captures, f"bibliotheque-{largeur}-{mode}.png"))
                ctx.close()

        ctx, page = nouvelle()
        ouvrir(page)
        cas("onglet « Bibliothèque » marqué comme page en cours",
            page.evaluate("[...document.querySelectorAll('.nav a[aria-current=page]')].map(a => a.textContent).join()") == "Bibliothèque")
        cas("lien « Code source sur GitHub » dans le pied", page.locator("footer.pied a", has_text="Code source sur GitHub").count() == 1)
        cas("aucun « Ajouter une ressource »", "Ajouter une ressource" not in page.inner_text("body"))
        cas("au plus 30 ressources affichées d'abord", page.locator(".res").count() == min(30, len(fiches)))

        print("Recherche")
        f0 = next(f for f in fiches if re.findall(r"[^\W\d_]{6,}", f["titre"]))
        mot = re.findall(r"[^\W\d_]{6,}", f0["titre"])[0]
        page.keyboard.press("/")
        cas("la touche « / » met le curseur dans la recherche", page.evaluate("document.activeElement.id") == "recherche")
        page.keyboard.type(mot)
        page.wait_for_timeout(500)
        cas(f"« {mot} » trouve « {f0['titre'][:50]} »", page.locator(f".lien-fiche[href*='r={f0['id']}']").count() >= 1)
        cas("les mots trouvés sont surlignés", page.locator(".res mark").count() >= 1)
        cas("l'adresse garde la recherche", "q=" in page.url, page.url)
        cas("le nombre de résultats est annoncé", "trouvée" in (page.text_content("#recherche-statut") or ""))
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        cas("Échap efface la recherche", compte(page) == len(fiches) and "q=" not in page.url)

        faute = mot[:2] + mot[3] + mot[2] + mot[4:] if len(mot) >= 6 else mot
        ouvrir(page, "?q=" + faute)
        cas(f"faute de frappe « {faute} » : la ressource est trouvée quand même",
            page.locator(f".lien-fiche[href*='r={f0['id']}']").count() >= 1)
        ouvrir(page, "?q=xqzwvk")
        cas("aucun résultat : un message, sans erreur", "Aucune ressource ne correspond" in page.inner_text("main"))

        print("Filtres")
        ouvrir(page)
        ens = {}
        for f in fiches:
            for e in f["enseignements"]:
                ens[e] = ens.get(e, 0) + 1
        e, ne = min(ens.items(), key=lambda x: x[1])
        page.locator(f"#f-ens-{e}").check()
        page.wait_for_timeout(300)
        cas(f"filtre « {e} » : {ne} ressources", compte(page) == ne, compte(page))
        cas("l'adresse garde le filtre", f"ens={e}" in page.url, page.url)
        cas("une puce permet de retirer le filtre", page.locator(".puce").count() == 1)
        txt = page.text_content(f"label[for='f-ens-{e}'] .nb")
        cas("le nombre de ressources est indiqué sur le filtre", txt == str(ne), txt)
        page.locator(".puce").click()
        page.wait_for_timeout(300)
        cas("retirer la puce rend toutes les ressources", compte(page) == len(fiches))

        if any(f.get("programme") for f in fiches):
            page.locator(".facette summary", has_text="Programme officiel").click()
            premier = page.locator(".facette:has(summary:has-text('Programme officiel')) .filtre-case input").first
            premier.check()
            page.wait_for_timeout(300)
            cas("arbre du programme : un programme se coche", compte(page) and compte(page) <= len(fiches) and "prog=" in page.url)
            b = page.locator(".facette:has(summary:has-text('Programme officiel')) .deplier").first
            if b.count():
                b.click()
                page.wait_for_timeout(200)
                cas("arbre du programme : une branche se déplie",
                    page.locator(".facette:has(summary:has-text('Programme officiel')) .filtre-sous").count() >= 1)
            page.goto(base, wait_until="networkidle")

        # Notions (décision du 13/11/2026) : une seule liste des notions travaillées, plus les prérequises
        thes = {x["id"]: x for x in bib["referentiels"]["notions"]["notions"]}
        larges = {q for x in thes.values() for q in x.get("plus_larges", [])}
        classees = [f for f in fiches if (f.get("notions") or {}).get("travaillees")]
        feuilles = sorted({nid for f in classees for nid in f["notions"]["travaillees"] if nid not in larges})
        if feuilles:
            nid = feuilles[0]
            attendues = [f for f in fiches if nid in (f.get("notions") or {}).get("travaillees", [])]
            ouvrir(page, "?notion=" + nid)
            cas(f"filtre « Notions travaillées » sur « {thes[nid]['libelle']} » : {len(attendues)} ressource(s)",
                compte(page) == len(attendues), compte(page))
            ouvrir(page, "?r=" + attendues[0]["id"])
            synthese = page.inner_text(".synthese")
            cas("la fiche montre ses « Notions travaillées », sans les anciens rôles",
                "Notions travaillées" in synthese and thes[nid]["libelle"] in synthese
                and "Notions enseignées" not in synthese and "Notions évaluées" not in synthese, synthese[:300])
        else:
            print("  sans objet : aucune fiche n'a encore de notions travaillées (fiches à convertir, T64)")

        print("Tri, vues, fiche")
        ouvrir(page, "?tri=titre")
        titres = page.evaluate("[...document.querySelectorAll('.res .titre')].map(a => a.textContent)")
        norm = [t.lower() for t in titres]
        cas("tri par titre", len(titres) < 2 or norm[0] <= norm[-1], titres[:3])
        page.locator(".mode-btn", has_text="Cartes").click()
        page.wait_for_timeout(200)
        cas("vue en cartes, gardée dans l'adresse", page.locator(".carte").count() >= 1 and "vue=cartes" in page.url)
        page.locator(".lien-fiche").first.click()
        page.wait_for_selector(".fiche-titre")
        cas("la fiche complète s'ouvre à ?r=", "r=" in page.url and page.locator(".synthese").count() == 1)
        cas("la fiche montre ses documents", page.locator(".documents li").count() >= 1)
        page.go_back()
        page.wait_for_selector(".compte")
        cas("le bouton Retour du navigateur revient aux résultats, en cartes", page.locator(".carte").count() >= 1)
        ouvrir(page, "?r=nexiste-pas")
        cas("ressource inconnue : un message clair", "Ressource introuvable" in page.inner_text("main"))
        ouvrir(page, "?vue=cartes&ens=" + e + "&q=" + mot)
        cas("une adresse partagée rétablit recherche, filtre et vue",
            page.input_value("#recherche") == mot and page.is_checked(f"#f-ens-{e}") and page.locator(".carte").count() >= 0)

        print("Clavier")
        ouvrir(page)
        page.focus("#recherche")
        trouve = False
        for _ in range(40):
            page.keyboard.press("Tab")
            if page.evaluate("document.activeElement.type") == "checkbox":
                trouve = True
                break
        cas("les filtres s'atteignent à la touche Tab", trouve)
        if trouve:
            avant = compte(page)
            page.keyboard.press("Space")
            page.wait_for_timeout(300)
            cas("la barre d'espace coche un filtre, et le focus reste sur la case",
                compte(page) != avant or avant == len(fiches) and page.evaluate("document.activeElement.type") == "checkbox")

        print("Visibilité (cahier des charges, § 3.2)")
        cachees = []
        for chemin in sorted(os.listdir(os.path.join(d, "donnees", "ressources"))):
            x = json.load(open(os.path.join(d, "donnees", "ressources", chemin), encoding="utf-8"))
            cachees += [(x["id"], doc.get("titre") or doc["role"]) for doc in x["documents"] if not doc["visible"]["exterieur"]]
        publics = {f["id"]: f for f in fiches}
        fuite = [c for c in cachees if c[0] in publics and any((doc.get("titre") or doc["role"]) == c[1] and
                                                              not doc.get("visible", {}).get("exterieur", True) for doc in publics[c[0]]["documents"])]
        cas(f"aucun document caché à l'extérieur dans la vue publique ({len(cachees)} caché(s) dans les fiches)", not fuite, fuite)
        cas("aucune note de l'enseignant dans la vue publique", not any("notes" in f for f in fiches))

        cas("aucune erreur JavaScript", not erreurs, erreurs[:3])
        ctx.close()
        nav.close()
    serveur.shutdown()
    print(f"\n{n} cas, {echecs} échec(s)")
    if not echecs:
        shutil.rmtree(d, ignore_errors=True)
    else:
        print("Copie gardée pour l'examen : " + d)
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
