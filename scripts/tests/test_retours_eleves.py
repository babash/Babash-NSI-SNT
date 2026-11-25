#!/usr/bin/env python3
"""Essais des avis anonymes des élèves (T163), de bout en bout, sur une base Postgres LOCALE. Jamais la base réelle.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_retours_eleves.py --psql "psql -h /chemin/socket -p 54163 -U postgres" [--captures DOSSIER]

Le test :
1. reconstruit une base locale avec les fichiers du dépôt (socle, 0007, 0008, puis 0013), comme
   scripts/tests/test_compte_commun_en_ligne.py, dont il reprend les outils ;
2. sert le site et imite l'API (scripts/calendrier_serveur_essai.py) ; reglages.js est servi avec
   COMPTE_COMMUN_EN_LIGNE et RETOURS_ELEVES à true ;
3. l'enseignant·e crée son espace et une classe (par l'API imitée) ; six élèves, chacun·e sur son appareil
   et son réseau, ouvrent une feuille de TD avec le lien de la classe et donnent leur avis (un·e change le
   sien, un·e écrit un mot) ; un·e élève sans le lien donne aussi le sien ;
4. vérifie : rien n'est visible pendant la semaine ; la semaine passée (les dates des lignes reculent
   d'une semaine dans la base locale), l'espace enseignant·e montre un paquet de 6 avis de la classe et
   le mot, « tout le monde » 7 avis et aucun mot ; l'export CSV ; aucune requête ne porte le jeton du
   compte commun ; aucune autre requête vers la base ; aucune erreur JavaScript ; rien ne déborde.
Il faut Playwright, Chromium et un Postgres local (16 ou plus). Code de retour : 0 si tout passe, 1 sinon.
"""
import argparse
import asyncio
import importlib.util
import json
import os
import re
import subprocess
import sys
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(os.path.dirname(ICI))
spec = importlib.util.spec_from_file_location("cc_en_ligne", os.path.join(ICI, "test_compte_commun_en_ligne.py"))
CC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CC)
CC.BASE = "essai_retours_eleves"
ECHECS = []
FEUILLE = "/nsi-terminale/fichiers/td-bac-abr/index.html"


def verifier(cond, quoi):
    print(("OK     " if cond else "ÉCHEC  ") + quoi, flush=True)
    if not cond:
        ECHECS.append(quoi)


def rpc(base, fn, params, reseau="10.9.0.1"):
    r = urllib.request.Request(base + "/rest/v1/rpc/" + fn, data=json.dumps(params).encode(),
                               headers={"Content-Type": "application/json", "X-Forwarded-For": reseau}, method="POST")
    with urllib.request.urlopen(r, timeout=30) as rep:
        return json.loads(rep.read())


async def parcours(nav, psql, base, captures):
    monde = CC.Monde(nav, base)
    monde.reglages = re.sub(r"RETOURS_ELEVES:\s*(true|false)", "RETOURS_ELEVES: true", monde.reglages)
    verifier("RETOURS_ELEVES: true" in monde.reglages, "reglages.js servi avec RETOURS_ELEVES: true")
    prof = rpc(base, "commun_prof_creer_espace", {"p_nom": "Mme Essai"})["code_affiche"]
    classe = rpc(base, "commun_prof_creer_classe", {"p_code": prof, "p_nom": "TNSI essai", "p_applications": []})
    code_classe = classe["code"]

    corps = []
    monde_req = []
    choix = [(5, "Bien pour moi", "Oui"), (4, "Trop dur", "À peu près"), (3, "Trop dur", "Non"),
             (4, "Bien pour moi", "Oui"), (2, "Trop dur", "Non"), (5, "Trop facile", "Oui")]
    for i, (etoiles, difficulte, compris) in enumerate(choix):
        ctx = await monde.appareil(largeur=(320, 768, 1440)[i % 3], theme=("light", "dark")[i % 2], reseau=f"10.0.1.{i + 1}")
        ctx.on("request", lambda r: corps.append(r.post_data or "") if "/rpc/" in r.url else monde_req.append(r.url))
        pg = await monde.page(ctx, FEUILLE + "?classe=" + code_classe)
        await pg.evaluate("localStorage.setItem('compte-commun:session', JSON.stringify({jeton: '11111111-1111-4111-8111-111111111111', jusqu: '2099-01-01'}))")
        z = pg.locator("[data-retour]")
        await z.locator("form").wait_for(timeout=15000)
        await z.locator(".re-etoiles label").nth(etoiles - 1).click()
        await z.get_by_text(difficulte, exact=True).click()
        await z.locator(".re-trio fieldset").nth(1).get_by_text(compris, exact=True).click()
        if i == 1:
            await z.locator("summary").click()
            await z.get_by_text("Il me faut plus d'exemples").click()
            await z.locator("textarea").fill("La question 4 demande trop de temps")
        await z.get_by_role("button", name="Envoyer mon avis").click()
        await z.get_by_text("Merci pour ton avis").wait_for(timeout=15000)
        verifier(await CC.deborde(pg) is False, f"élève {i + 1} : la page ne déborde pas")
        if i == 1 and captures:
            await z.screenshot(path=os.path.join(captures, "e2e-eleve-merci.png"))
        if i == 2:  # changer son avis
            await z.get_by_role("button", name="Changer mon avis").click()
            await z.get_by_text("Bien pour moi", exact=True).click()
            await z.get_by_role("button", name="Changer mon avis").click()
            await z.get_by_text("Merci pour ton avis").wait_for(timeout=15000)
        await ctx.close()
    # sans le lien de la classe : avis pour « tout le monde », pas de mot proposé
    ctx = await monde.appareil(largeur=390, reseau="10.0.2.1")
    pg = await monde.page(ctx, FEUILLE)
    z = pg.locator("[data-retour]")
    await z.locator("form").wait_for(timeout=15000)
    await z.locator("summary").click()
    verifier(await z.locator("textarea").count() == 0, "sans le lien de la classe : pas de mot libre")
    await z.locator(".re-etoiles label").nth(2).click()
    await z.get_by_role("button", name="Envoyer mon avis").click()
    await z.get_by_text("Merci pour ton avis").wait_for(timeout=15000)
    await ctx.close()

    verifier(not any("1111-4111" in c for c in corps), "aucun envoi ne porte le jeton du compte commun")
    verifier(all("commun_retour_donner" in c or "p_cle" in c for c in corps if c), "seuls les avis partent vers la base")
    verifier(not [u for u in monde_req if "supabase" in u], "aucune autre requête vers la base")
    nb = subprocess.run(psql + ["-X", "-A", "-t", "-c", "select count(*) || '/' || count(classe_id) || '/' || count(mot) from commun.retours"],
                        capture_output=True, text=True).stdout.strip()
    verifier(nb == "7/6/1", f"en base : 7 avis, 6 avec la classe, 1 mot ({nb})")

    vide = rpc(base, "commun_prof_retours", {"p_code": prof, "p_classe": classe["id"]})
    verifier(vide.get("ok") and vide["ressources"] == [], "pendant la semaine : rien à montrer")
    subprocess.run(psql + ["-X", "-q", "-c", "update commun.retours set semaine = semaine - 7"], check=True)

    ctx = await monde.appareil(largeur=768, reseau="10.0.3.1")
    pg = await monde.page(ctx, "/enseignant/")
    await pg.get_by_label("Ton code d'enseignant·e").fill(prof)
    await pg.get_by_role("button", name="Ouvrir mon espace").click()
    await pg.locator(".cc-classe-lien-nom").first.click()
    av = pg.locator("details.cc-avis")
    await av.locator("summary").first.click()
    await av.locator(".cc-avis-carte").first.wait_for(timeout=15000)
    texte = await av.inner_text()
    verifier("6 avis" in texte, "la classe : un paquet de 6 avis")
    verifier("trop dur 2 (33 %)" in texte, "la classe : « trop dur » 2 sur 6 (l'avis changé compte une fois)")
    verifier("La question 4 demande trop de temps" in texte, "la classe : le mot est lu par l'enseignant·e")
    verifier("Il faut plus d'exemples : 1" in texte, "la classe : la remarque choisie")
    async with pg.expect_download() as dl:
        await av.get_by_role("button", name="Exporter (CSV)").click()
    chemin = await (await dl.value).path()
    csv = open(chemin, encoding="utf-8-sig").read()
    verifier(csv.startswith("portee;classe;ressource;titre;partie;semaine") and ";td-bac-abr;" in csv, "l'export CSV")
    verifier("La question 4" not in csv, "l'export ne contient aucun mot")
    if captures:
        await av.screenshot(path=os.path.join(captures, "e2e-enseignant-classe.png"))
    await pg.get_by_role("link", name="← Mes classes").click()
    av = pg.locator("details.cc-avis")
    await av.locator("summary").first.click()
    await av.locator(".cc-avis-carte").first.wait_for(timeout=15000)
    texte = await av.inner_text()
    verifier("7 avis" in texte and "La question 4" not in texte, "tout le monde : 7 avis, aucun mot")
    verifier(await CC.deborde(pg) is False, "l'espace enseignant·e ne déborde pas")
    await ctx.close()
    verifier(not monde.erreurs_js, f"aucune erreur JavaScript {monde.erreurs_js}")


async def principal(a):
    psql = CC.preparer(a.psql)
    fichier = os.path.join(RACINE, "supabase", "0013-retours-eleves.sql")
    texte = open(fichier, encoding="utf-8").read()
    if subprocess.run(["psql", "--version"], capture_output=True, text=True).stdout.split()[-1].startswith("16"):
        texte = texte.replace(", maintain", "")
    r = subprocess.run(psql + ["-X", "-q", "-v", "ON_ERROR_STOP=1"], input=texte, capture_output=True, text=True)
    if r.returncode:
        sys.exit("0013 ne passe pas : " + r.stderr[-600:])
    serveur, base = CC.demarrer_serveur(psql)
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        try:
            await parcours(nav, psql, base, a.captures)
        finally:
            await nav.close()
            serveur.shutdown()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--psql", required=True)
    ap.add_argument("--captures")
    a = ap.parse_args()
    if a.captures:
        os.makedirs(a.captures, exist_ok=True)
    asyncio.run(principal(a))
    print(f"\n{len(ECHECS)} échec(s).")
    sys.exit(1 if ECHECS else 0)
