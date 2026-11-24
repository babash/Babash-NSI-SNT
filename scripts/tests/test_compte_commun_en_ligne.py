#!/usr/bin/env python3
"""Essais du compte commun EN LIGNE, sur une base Postgres LOCALE (T132d). Jamais la base réelle.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_compte_commun_en_ligne.py --psql "psql -h /chemin/socket -p 54352 -U postgres" [--captures DOSSIER]

Le test :
1. reconstruit la base « essai_compte_commun » avec les fichiers du dépôt (supabase/0001, 0003, 0009, 0007, 0008),
   comme dans le projet (rôles anon, authenticated, service_role ; pgcrypto dans extensions) ;
2. sert le site et imite l'API de Supabase (scripts/calendrier_serveur_essai.py) ; dans Chromium, les appels
   à https://cukahpyqkljiddmimpyi.supabase.co sont renvoyés vers la base locale, et reglages.js est servi avec
   COMPTE_COMMUN_EN_LIGNE: true ;
3. joue les parcours : l'enseignant·e crée son espace (code montré une fois) et deux classes ; trois élèves
   rejoignent par le lien de classe ; l'un·e revient avec son code sur un autre appareil et change d'avatar ;
   l'enseignant·e les voit (mode projection), donne un nouveau code ; un·e élève efface ses données ;
   les erreurs (code faux, trop d'essais, hors ligne) ; la garde du jeton (onglet ou « C'est mon téléphone ») ;
   le bandeau « mes applications » ; la suppression de l'espace ;
4. vérifie à 320, 768 et 1440 px, en clair et en obscur, qu'aucune page ne déborde ; qu'aucune requête ne part
   vers un autre hôte que le site et la base ; qu'aucun code ni jeton n'apparaît dans une adresse ;
   qu'il n'y a aucune erreur JavaScript.
Il faut Playwright, Chromium et un Postgres local (16 ou plus). Code de retour : 0 si tout passe, 1 sinon.
"""
import argparse
import asyncio
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
import threading
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(os.path.dirname(ICI))
BASE_API = "https://cukahpyqkljiddmimpyi.supabase.co"
BASE = "essai_compte_commun"
ECHECS = []


def verifier(cond, quoi):
    print(("OK     " if cond else "ÉCHEC  ") + quoi, flush=True)
    if not cond:
        ECHECS.append(quoi)


def preparer(psql, catalogue=None):
    p0 = shlex.split(psql) + ["-X", "-q", "-v", "ON_ERROR_STOP=1"]

    def lancer(base, sql=None, fichier=None):
        texte = sql if sql is not None else open(fichier, encoding="utf-8").read()
        if subprocess.run(["psql", "--version"], capture_output=True, text=True).stdout.split()[-1].startswith("16"):
            texte = texte.replace(", maintain", "")  # le privilège MAINTAIN est né avec Postgres 17
        r = subprocess.run(p0 + ["-d", base], input=texte, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"Préparation de la base locale impossible : {r.stderr[-600:]}")

    lancer("postgres", f"drop database if exists {BASE};")
    lancer("postgres", f"create database {BASE};")
    lancer("postgres", "do $$ begin if not exists (select 1 from pg_roles where rolname = 'anon') then "
                       "create role anon nologin; create role authenticated nologin; create role service_role nologin bypassrls; end if; end $$;")
    lancer(BASE, "create schema extensions; create extension pgcrypto with schema extensions; "
                 "create table public.snt_responses (id int); create table public.gb_eleves (id int); "
                 "create schema court_circuit; create schema grand_oral; create schema lagon; create schema vacances; create schema gombessa;")
    for f in ("0001-droits-par-defaut", "0003-schema-commun", "0009-registre-vacances", "0007-compte-commun", "0008-enseignants-communs"):
        lancer(BASE, fichier=os.path.join(RACINE, "supabase", f + ".sql"))
    if catalogue:
        lancer(BASE, fichier=catalogue)
    return shlex.split(psql) + ["-d", BASE]


def demarrer_serveur(psql):
    spec = importlib.util.spec_from_file_location("serveur_essai", os.path.join(RACINE, "scripts", "calendrier_serveur_essai.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.PSQL = psql
    import http.server
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), m.Gestion)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}"


class Monde:
    """Le site local, l'API imitée, et la liste de toutes les requêtes des pages."""

    def __init__(self, navigateur, base, catalogue=False):
        self.nav, self.base, self.requetes, self.erreurs_js = navigateur, base, [], []
        with open(os.path.join(RACINE, "reglages.js"), encoding="utf-8") as f:
            r = re.sub(r"COMPTE_COMMUN_EN_LIGNE:\s*(true|false)", "COMPTE_COMMUN_EN_LIGNE: true", f.read())
        self.reglages = re.sub(r"COMPTE_COMMUN_CATALOGUE:\s*(true|false)", "COMPTE_COMMUN_CATALOGUE: " + ("true" if catalogue else "false"), r)

    async def appareil(self, largeur=1440, theme="light", reseau="10.0.0.1"):
        ctx = await self.nav.new_context(viewport={"width": largeur, "height": 900}, color_scheme=theme)

        async def api(route):
            req = route.request
            corps = req.post_data or "{}"

            def poster():
                r = urllib.request.Request(self.base + "/rest/v1/rpc/" + req.url.rsplit("/", 1)[1], data=corps.encode(),
                                           headers={"Content-Type": "application/json", "X-Forwarded-For": reseau}, method="POST")
                try:
                    with urllib.request.urlopen(r, timeout=30) as rep:
                        return rep.status, rep.read()
                except urllib.error.HTTPError as e:
                    return e.code, e.read()
            statut, contenu = await asyncio.to_thread(poster)
            await route.fulfill(status=statut, body=contenu, headers={"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"})

        async def reglages(route):
            await route.fulfill(status=200, body=self.reglages, headers={"Content-Type": "application/javascript"})
        await ctx.route(BASE_API + "/**", api)
        await ctx.route("**/reglages.js", reglages)
        ctx.on("request", lambda r: self.requetes.append(r.url))
        return ctx

    async def page(self, ctx, chemin):
        pg = await ctx.new_page()
        pg.on("pageerror", lambda e: self.erreurs_js.append(str(e)))
        await pg.goto(self.base + chemin)
        return pg


async def deborde(pg):
    return await pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")


async def attendre_texte(pg, texte, delai=15000):
    await pg.get_by_text(texte, exact=False).first.wait_for(timeout=delai)


async def creer_eleve(monde, lien, pseudo, telephone=False, reseau="10.0.0.1"):
    ctx = await monde.appareil(reseau=reseau)
    pg = await monde.page(ctx, lien)
    await attendre_texte(pg, "Lien de classe")
    await pg.get_by_label("Ton prénom ou un pseudo").fill(pseudo)
    if telephone:
        await pg.locator("#titre-creer").locator("xpath=..").get_by_label("C'est mon téléphone").check()
    await pg.get_by_role("button", name="Créer mon code").click()
    code = (await pg.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    await pg.get_by_label("Retape les 3 chiffres de ton code").fill(code[-3:])
    await pg.get_by_role("button", name="C'est noté").click()
    await attendre_texte(pg, "Salut, " + pseudo)
    return ctx, pg, code


async def parcours(monde, captures):
    codes_vus = []
    # ── 1. L'enseignant·e crée son espace et deux classes ──
    prof_ctx = await monde.appareil(reseau="10.0.0.2")
    prof = await monde.page(prof_ctx, "/enseignant/")
    await prof.get_by_label("Nom affiché aux élèves").fill("Mme Essai")
    await prof.get_by_role("button", name="Créer mon espace").click()
    code_prof = (await prof.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    codes_vus.append(code_prof)
    verifier(re.fullmatch(r"[A-Z]+-[A-Z]+-[A-Z]+-\d{4}", code_prof) is not None, f"code d'enseignant·e de 3 mots et 4 chiffres ({len(code_prof)} caractères)")
    verifier(await prof.get_by_role("button", name="Imprimer").count() == 1 and await prof.get_by_role("button", name="Je l'ai noté").count() == 1,
             "le code est montré une fois, avec « Imprimer » et « Je l'ai noté »")
    await prof.get_by_label("Retape les 4 chiffres de ton code").fill("0000" if not code_prof.endswith("0000") else "1111")
    await prof.get_by_role("button", name="Je l'ai noté").click()
    await attendre_texte(prof, "Ce ne sont pas les bons chiffres")
    verifier(True, "« Je l'ai noté » demande les 4 chiffres du code : un essai faux est refusé")
    await prof.get_by_label("Retape les 4 chiffres de ton code").fill(code_prof[-4:])
    await prof.route(BASE_API + "/rest/v1/rpc/commun_prof_ouvrir", lambda r: r.fulfill(status=503, body="{}"))
    await prof.get_by_role("button", name="Je l'ai noté").click()
    await attendre_texte(prof, "Ton code reste affiché")
    verifier(await prof.locator(".cc-code-grand").inner_text() == code_prof, "la base ne répond pas à « Je l'ai noté » : le code reste à l'écran, avec le message")
    await prof.unroute(BASE_API + "/rest/v1/rpc/commun_prof_ouvrir")
    await prof.get_by_role("button", name="Je l'ai noté").click()
    await attendre_texte(prof, "Mes classes")
    rep = await prof.evaluate("async () => (await CompteCommun.prof.creerClasse('Sec' + String.fromCharCode(0x202E) + 'onde', [])).message")
    verifier("caractère spécial" in rep, f"un nom de classe avec un caractère invisible : « {rep} »")
    classes = {}
    for nom in ("Seconde 4", "TNSI 2"):
        await prof.locator("summary", has_text="Nouvelle classe").click()
        await prof.get_by_label("Nom de la classe").fill(nom)
        await prof.get_by_role("button", name="Créer la classe").click()
        await prof.locator("h2.cc-titre-section", has_text=nom).wait_for(timeout=15000)
        code = (await prof.locator(".cc-code-moyen").inner_text()).strip()
        lien = await prof.locator(".cc-lien-url a").get_attribute("href")
        qr = await prof.locator(".cc-qr svg").count()
        classes[nom] = (code, lien)
        verifier(re.fullmatch(r"[A-HJ-NP-Z]{4}", code) is not None and lien.endswith("/eleve/?classe=" + code) and qr == 1,
                 f"classe « {nom} » : code de 4 lettres, lien et QR code faits dans la page")
        await prof.get_by_role("link", name="← Mes classes").click()
        await attendre_texte(prof, "Mes classes")
    verifier(await prof.locator(".cc-classe-carte").count() == 2, "les deux classes sont sur l'accueil de l'espace")
    await prof.locator("summary", has_text="Réglages de mon espace").click()
    t = await prof.locator("main").inner_text()
    verifier("Ajouter un espace d'application" not in t and "Relier cet espace" not in t and "code d'un espace d'application" not in t, "espace enseignant·e : pas de lien vers un espace d'application tant qu'aucune n'est branchée")
    await prof.locator("summary", has_text="Réglages de mon espace").click()

    # ── 2. Trois élèves rejoignent « Seconde 4 » par le lien de classe ──
    code_classe = classes["Seconde 4"][0]
    chemin = "/eleve/?classe=" + code_classe
    eleves = {}
    for i, pseudo in enumerate(("Ali", "Bea", "Chloé")):
        ctx, pg, code = await creer_eleve(monde, chemin, pseudo, telephone=(pseudo == "Bea"))
        codes_vus.append(code)
        eleves[pseudo] = (ctx, pg, code)
        verifier(re.fullmatch(r"[A-Z]+-[A-Z]+-\d{3}", code) is not None, f"{pseudo} : code de 2 mots et 3 chiffres")
        verifier(await pg.get_by_text("Seconde 4").count() >= 1, f"{pseudo} : dans la classe « Seconde 4 »")
        verifier("classe=" not in pg.url, f"{pseudo} : le code de classe a quitté l'adresse après l'inscription")
    stock = await eleves["Ali"][1].evaluate("[sessionStorage.getItem('compte-commun:session') !== null, localStorage.getItem('compte-commun:session') !== null]")
    verifier(stock == [True, False], "Ali (appareil partagé) : jeton dans l'onglet seulement (sessionStorage)")
    stock = await eleves["Bea"][1].evaluate("[sessionStorage.getItem('compte-commun:session') !== null, localStorage.getItem('compte-commun:session') !== null]")
    verifier(stock == [False, True], "Bea (« C'est mon téléphone ») : jeton gardé dans le navigateur (localStorage)")

    # La classe vue par l'élève : ses camarades, sans XP ni crédits ni codes
    pg = eleves["Chloé"][1]
    await pg.get_by_role("tab", name="Ma classe").click()
    noms = await pg.locator(".cc-camarade-nom").all_inner_texts()
    verifier(len(noms) == 3 and any("Ali" in n for n in noms), f"Chloé voit ses 3 camarades ({', '.join(n.replace(chr(10), ' ') for n in noms)})")
    texte = await pg.locator("#panneau-classe").inner_text()
    verifier(eleves["Ali"][2] not in texte and "XP" not in texte, "Chloé ne voit ni le code ni l'XP d'Ali")
    # Aucune phrase n'annonce ce qui n'existe pas encore (aucune application branchée)
    await pg.get_by_role("tab", name="Applications").click()
    t = await pg.locator("#panneau-applications").inner_text()
    verifier("Bientôt, ton code marchera" in t and "reconnaissent toutes seules" not in t, "onglet Applications : « bientôt », pas de promesse")
    await pg.get_by_role("tab", name="Crédits et codes").click()
    t = await pg.locator("#panneau-credits").inner_text()
    verifier("seul·e ton enseignant·e peut t'en donner" in t and "Ajouter un autre de mes codes" not in t and "applications qui le permettent" not in t,
             "onglet Crédits et codes : ni code d'une autre application, ni effacement « partout », crédits dits tels qu'ils sont")
    await pg.get_by_role("tab", name="Hauts faits").click()
    t = await pg.locator("#panneau-hauts-faits").inner_text()
    verifier("pourra compter" not in t and "arrivent bientôt" in t, "onglet Hauts faits : « bientôt », sans promesse")
    # Un pseudo avec un caractère invisible : le bon message
    autre = await monde.appareil(reseau="10.0.0.5")
    pp = await monde.page(autre, "/eleve/")
    await pp.get_by_label("Ton prénom ou un pseudo").wait_for()
    await pp.evaluate("document.querySelector('#titre-creer').parentNode.querySelector('input').value = 'Lé' + String.fromCharCode(0x200B) + 'a'")
    await pp.get_by_role("button", name="Créer mon code").click()
    await attendre_texte(pp, "caractère spécial")
    verifier(True, "élève : un pseudo avec un caractère invisible reçoit « caractère spécial », pas « 2 à 24 caractères »")
    await autre.close()
    # Le bandeau « mes applications »
    n = await pg.evaluate("""async () => { const d = document.createElement('div'); document.body.appendChild(d);
      await CompteCommun.bandeau(d, { application: 'commun' }); return d.textContent; }""")
    verifier("Chloé · mes applications" in n and "QuizzNSI" in n and "Ce n'est pas moi" in n, "le bandeau « Chloé · mes applications » liste les applications")

    # ── 3. Ali revient avec son code sur un autre appareil et change d'avatar ──
    ali2_ctx = await monde.appareil(largeur=768, theme="dark", reseau="10.0.0.3")
    ali2 = await monde.page(ali2_ctx, "/eleve/")
    await ali2.get_by_label("Ton code", exact=True).fill(eleves["Ali"][2].lower().replace("-", " "))
    await ali2.get_by_role("button", name="Entrer").click()
    await attendre_texte(ali2, "Salut, Ali")
    verifier(True, "Ali entre sur un autre appareil avec son code tapé en minuscules, avec des espaces")
    await ali2.get_by_role("tab", name="Mon avatar").click()
    loge = ali2.locator("#panneau-loge")
    texte = await loge.inner_text()
    verifier("margouillat" in texte.lower() and "arrivent bientôt" in texte, "sans catalogue, la loge propose l'identité, les tenues et le margouillat, et le dit")
    sel = loge.get_by_label("Coiffure", exact=True)
    options = await sel.locator("option").evaluate_all("o => o.map(x => x.value)")
    t = await loge.inner_text()
    verifier("Bientôt, gratuits pour tout le monde" in t and all(x in t for x in ("bandana à pois", "kishali sur la tête", "kishali sur les épaules")), "la loge annonce les trois pièces libres pour bientôt")
    toutes = await loge.locator("option").evaluate_all("o => o.map(x => x.value)")
    verifier(not any(v in toutes for v in ("kishali_tete", "kishali", "bandana")), "et ne les propose pas : la base les refuserait avant 0010")
    rep = await ali2.evaluate("""async () => { const r = await CompteCommun.reprendre(); const a = JSON.parse(JSON.stringify(r.fiche.avatar));
      a.objets.tete = 'kishali_tete'; return (await CompteCommun.porter(a)).ok; }""")
    verifier(rep is False, "commun_porter refuse aujourd'hui le kishali sur la tête (absent de commun.elements)")
    await sel.select_option(options[-1])
    await loge.get_by_label("Couleur du haut", exact=True).select_option(index=2)
    await loge.get_by_role("button", name="Porter cet avatar").click()
    await loge.get_by_text("C'est porté.").wait_for(timeout=15000)
    verifier(True, f"Ali porte un nouvel avatar (coiffure « {options[-1]} »)")
    await ali2.get_by_role("tab", name="Boutique").click()
    verifier("ouvre bientôt" in await ali2.locator("#panneau-boutique").inner_text(), "la boutique dit qu'elle ouvre bientôt")
    if captures:
        await ali2.screenshot(path=os.path.join(captures, "eleve-768-obscur.png"), full_page=True)

    # ── 4. L'enseignant·e les voit, en mode projection, et donne un nouveau code à Ali ──
    await prof.locator(".cc-classe-lien-nom", has_text="Seconde 4").click()
    await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
    noms = await prof.locator(".cc-eleve-nom").all_inner_texts()
    verifier(noms == ["Ali", "Bea", "Chloé"], f"l'enseignant·e voit ses 3 élèves, rangé·e·s par pseudo ({', '.join(noms)})")
    verifier(await prof.locator(".cc-eleve .cc-avatar-cadre").count() == 3, "avec leur avatar")
    carte_ali = prof.locator(".cc-eleve", has=prof.locator(".cc-eleve-nom", has_text="Ali"))
    verifier("coiffure" in (await carte_ali.locator(".cc-avatar-cadre").get_attribute("aria-label") or "").lower()
             or await carte_ali.locator(".cc-avatar-cadre").get_attribute("data-dessin") == "equipage", "l'avatar d'Ali est dessiné par le moteur")
    verifier(await carte_ali.get_by_text(eleves["Ali"][2]).is_visible(), "hors projection, l'enseignant·e voit le code d'Ali")
    await prof.get_by_label("Mode projection").check()
    verifier(not await carte_ali.get_by_text(eleves["Ali"][2]).is_visible(), "en mode projection, le code d'Ali est masqué")
    await carte_ali.locator("summary", has_text="Attribuer de l'XP").click()
    await carte_ali.get_by_label("Motif").first.fill("Aide à un camarade")
    await carte_ali.get_by_role("button", name="Attribuer").click()
    await prof.locator(".cc-annonce", has_text="+10 XP").wait_for(state="attached", timeout=15000)
    verifier(not await prof.locator(".cc-annonce", has_text="+10 XP").is_visible(), "en mode projection, l'annonce « +10 XP » ne s'affiche pas")
    carte_ali = prof.locator(".cc-eleve", has=prof.locator(".cc-eleve-nom", has_text="Ali"))
    verifier(await prof.get_by_text("Archiver la classe").count() == 0 and await prof.get_by_text("Classes archivées").count() == 0,
             "avant 0010, la page ne prétend pas archiver (seule la case « Inscriptions ouvertes »)")
    await prof.get_by_label("Mode projection").uncheck()
    await carte_ali.locator("summary", has_text="Pseudo, code, retrait").click()
    await carte_ali.get_by_role("button", name="Nouveau code").click()
    await carte_ali.get_by_text("Nouveau code :").wait_for(timeout=15000)
    nouveau = re.search(r"[A-Z]+-[A-Z]+-\d{3}", await carte_ali.locator(".cc-masquable-bloc").inner_text()).group(0)
    codes_vus.append(nouveau)
    verifier(nouveau != eleves["Ali"][2], "Ali reçoit un nouveau code")
    if captures:
        await prof.screenshot(path=os.path.join(captures, "enseignant-1440-clair.png"), full_page=True)
    # L'ancien code ne marche plus ; la session de l'autre appareil est fermée
    rep = await ali2.evaluate("async c => (await CompteCommun.entrer(c)).message", eleves["Ali"][2])
    verifier("n'existe pas" in rep, f"l'ancien code d'Ali ne marche plus (« {rep} »)")
    rep = await eleves["Ali"][1].evaluate("async () => (await CompteCommun.reprendre()).ok")
    verifier(rep is False, "la session d'Ali sur son premier appareil est fermée")
    rep = await ali2.evaluate("async c => (await CompteCommun.entrer(c)).ok", nouveau)
    verifier(rep is True, "le nouveau code d'Ali ouvre son compte")

    # ── 5. Bea efface ses données ──
    bea = eleves["Bea"][1]
    rep = await bea.evaluate("""async () => { const k = 'compte-commun:session'; const s = JSON.parse(localStorage.getItem(k));
      s.jusqu = new Date(Date.now() + 864e5).toISOString(); localStorage.setItem(k, JSON.stringify(s));
      await CompteCommun.reprendre(); return (new Date(JSON.parse(localStorage.getItem(k)).jusqu) - Date.now()) / 864e5; }""")
    verifier(rep > 29.9, f"« C'est mon téléphone » : le jeton est prolongé de 30 jours quand il sert ({rep:.1f} jours)")
    await bea.reload()
    await attendre_texte(bea, "Salut, Bea")
    await bea.get_by_role("tab", name="Crédits et codes").click()
    await bea.locator("summary", has_text="Effacer mes données").click()
    await bea.get_by_label("Écris EFFACER pour confirmer").fill("effacer")
    await bea.get_by_role("button", name="Effacer mes données").click()
    await attendre_texte(bea, "est effacé")
    stock = await bea.evaluate("localStorage.getItem('compte-commun:session')")
    verifier(stock is None, "Bea : compte effacé, plus aucun jeton sur l'appareil")
    # le code d'enseignant·e reste en mémoire de la page : on revient par la page, sans recharger
    await prof.get_by_role("link", name="← Mes classes").click()
    await prof.locator(".cc-classe-lien-nom", has_text="Seconde 4").click()
    await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
    verifier(await prof.locator(".cc-eleve-nom").all_inner_texts() == ["Ali", "Chloé"], "l'enseignant·e ne voit plus Bea")

    # ── 6. Les erreurs ──
    inconnu = await monde.appareil(largeur=320, theme="dark", reseau="10.0.0.9")
    pg = await monde.page(inconnu, "/eleve/")
    await pg.get_by_label("Ton code", exact=True).fill("PIRATE-FAUX-000")
    await pg.get_by_role("button", name="Entrer").click()
    await attendre_texte(pg, "Ce code n'existe pas")
    verifier(True, "élève : un code faux est refusé, en français")
    pe = await monde.page(inconnu, "/enseignant/")
    await pe.get_by_label("Ton code d'enseignant·e").wait_for()
    dernier = ""
    for _ in range(11):
        dernier = await pe.evaluate("async () => (await CompteCommun.prof.ouvrir('BOUCLE-CABESTAN-GLITCH-0000')).message")
    verifier("Trop d'essais" in dernier, f"enseignant·e : après 10 codes faux, « {dernier} »")
    rep = await prof.evaluate("async () => (await CompteCommun.prof.rouvrir()).ok")
    verifier(rep is True, "un autre réseau n'est pas bloqué (le compteur est par réseau)")
    if captures:
        await pg.screenshot(path=os.path.join(captures, "eleve-320-obscur-code-faux.png"), full_page=True)
    await inconnu.set_offline(True)
    await pg.get_by_label("Ton code", exact=True).fill("PIRATE-FAUX-001")
    await pg.get_by_role("button", name="Entrer").click()
    await attendre_texte(pg, "Pas de connexion")
    verifier(True, "hors ligne : « Pas de connexion… », sans requête")
    await inconnu.set_offline(False)

    # ── 7. Rendus : aucune page ne déborde ──
    for largeur in (320, 768, 1440):
        for theme in ("light", "dark"):
            ctx = await monde.appareil(largeur=largeur, theme=theme, reseau="10.0.0.4")
            for chemin in ("/eleve/?classe=" + classes["TNSI 2"][0], "/enseignant/"):
                pg = await monde.page(ctx, chemin)
                await pg.wait_for_timeout(1200)
                verifier(not await deborde(pg), f"{chemin.split('?')[0]} à {largeur} px ({theme}) : pas de défilement horizontal")
            pg = await monde.page(ctx, "/eleve/")
            await pg.get_by_label("Ton code", exact=True).fill(nouveau)
            await pg.get_by_role("button", name="Entrer").click()
            await attendre_texte(pg, "Salut, Ali")
            for onglet in ("Mon avatar", "Ma classe", "Crédits et codes"):
                await pg.get_by_role("tab", name=onglet).click()
                await pg.wait_for_timeout(300)
                verifier(not await deborde(pg), f"planque d'Ali, « {onglet} », à {largeur} px ({theme}) : pas de défilement horizontal")
            if captures:
                await pg.screenshot(path=os.path.join(captures, f"planque-{largeur}-{theme}.png"), full_page=True)
            await ctx.close()

    # ── 8. Un nouveau code d'enseignant·e (4 chiffres à retaper), puis supprimer l'espace ──
    await prof.get_by_role("link", name="← Mes classes").click()
    await prof.locator("summary", has_text="Réglages de mon espace").click()
    await prof.get_by_role("button", name="Me donner un nouveau code").click()
    await prof.get_by_role("button", name="Oui, changer mon code").click()
    nouveau_prof = (await prof.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    codes_vus.append(nouveau_prof)
    await prof.get_by_label("Retape les 4 chiffres de ton nouveau code").fill("0000" if not nouveau_prof.endswith("0000") else "1111")
    await prof.get_by_role("button", name="Je l'ai noté").click()
    await attendre_texte(prof, "regarde ton nouveau code")
    await prof.get_by_label("Retape les 4 chiffres de ton nouveau code").fill(nouveau_prof[-4:])
    await prof.get_by_role("button", name="Je l'ai noté").click()
    await attendre_texte(prof, "Ton nouveau code est noté")
    verifier(await prof.locator(".cc-code-grand").count() == 0, "« Me donner un nouveau code » : 4 chiffres à retaper (un essai faux refusé), puis le code disparaît")
    code_prof = nouveau_prof
    await prof.get_by_label("Écris SUPPRIMER pour confirmer").fill("SUPPRIMER")
    await prof.get_by_role("button", name="Supprimer mon espace").click()
    await attendre_texte(prof, "sont supprimés")
    rep = await prof.evaluate("async c => (await CompteCommun.prof.ouvrir(c)).ok", code_prof)
    verifier(rep is False, "l'espace supprimé ne s'ouvre plus ; les comptes des élèves restent")
    rep = await ali2.evaluate("async c => (await CompteCommun.entrer(c)).ok", nouveau)
    verifier(rep is True, "le compte d'Ali reste après la suppression de l'espace")
    rep = await ali2.evaluate("async () => (await CompteCommun.maClasse()).classes.length")
    verifier(rep == 0, "et la classe supprimée n'apparaît plus chez Ali")

    # ── 9. Ce qui est parti sur le réseau ──
    hotes = sorted({re.match(r"^(\w+://[^/]+)", u).group(1) for u in monde.requetes if re.match(r"^\w+://", u)})
    verifier(set(hotes) <= {monde.base, BASE_API}, f"aucune requête vers un autre hôte ({', '.join(hotes)})")
    fuite = [u for u in monde.requetes for c in codes_vus if c in u or c.replace("-", "") in u]
    verifier(not fuite, "aucun code d'élève ni d'enseignant·e dans une adresse")
    verifier(not monde.erreurs_js, f"aucune erreur JavaScript {monde.erreurs_js[:3]}")


async def combinaison(nav, psql, catalogue, reglage):
    """Une combinaison : la migration 0010 en base ou non, le réglage COMPTE_COMMUN_CATALOGUE vrai ou faux."""
    nom = f"0010 {'en base' if catalogue else 'absente'}, réglage {'vrai' if reglage else 'faux'}"
    serveur, base = demarrer_serveur(preparer(psql, catalogue))
    monde = Monde(nav, base, catalogue=reglage)
    ctx = await monde.appareil(reseau="10.1.0.1")
    prof = await monde.page(ctx, "/enseignant/")
    await prof.get_by_label("Nom affiché aux élèves").wait_for()
    code = await prof.evaluate("""async () => { const r = await CompteCommun.prof.creerEspace('M. Combi'); await CompteCommun.prof.ouvrir(r.code_affiche);
      const c = await CompteCommun.prof.creerClasse('Essai', ['td', 'quizz_nsi', 'vacances']); return [r.code_affiche, c.id, c.code]; }""")
    el = await monde.page(ctx, "/eleve/?classe=" + code[2])
    await el.get_by_label("Ton prénom ou un pseudo").fill("Lou")
    await el.get_by_role("button", name="Créer mon code").click()
    c = (await el.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    await el.get_by_label("Retape les 3 chiffres de ton code").fill(c[-3:])
    await el.get_by_role("button", name="C'est noté").click()
    await attendre_texte(el, "Salut, Lou")
    await el.get_by_role("tab", name="Boutique").click()
    t = await el.locator("#panneau-boutique").inner_text()
    if catalogue:
        verifier("seul·e ton enseignant·e peut t'en donner" in t and "Tu les gagnes en travaillant" not in t, f"{nom} : la boutique s'ouvre et dit d'où viennent les crédits aujourd'hui")
    else:
        verifier("ouvre bientôt" in t, f"{nom} : la boutique dit qu'elle ouvre bientôt")
    await el.get_by_role("tab", name="Hauts faits").click()
    t = await el.locator("#panneau-hauts-faits").inner_text()
    if catalogue:
        verifier("Pour l'avoir" not in t and "Bientôt, quand" in t and "Accordé par ton enseignant·e" in t,
                 f"{nom} : hauts faits des applications non branchées « bientôt », ceux de l'enseignant·e accordables")
    else:
        verifier("arrivent bientôt" in t, f"{nom} : les hauts faits arrivent bientôt")
    await el.get_by_role("tab", name="Trophées").click()
    t = await el.locator("#panneau-trophees").inner_text()
    lignes_gagne = [l for l in t.splitlines() if l.startswith("Se gagne avec")]
    verifier(all("accordé par ton enseignant·e" in l for l in lignes_gagne) and (not catalogue or "Bientôt, avec un haut fait de" in t),
             f"{nom} : trophées, aucun « Se gagne avec » d'une application non branchée ({len(lignes_gagne)} par l'enseignant·e)")
    if catalogue:
        verifier(("Ton enseignant·e peut te l'offrir." in t) == reglage, f"{nom} : « Ton enseignant·e peut te l'offrir » seulement avec le réglage")
    await el.get_by_role("tab", name="Mon avatar").click()
    options = await el.locator("#panneau-loge option").evaluate_all("o => o.map(x => x.value)")
    t = await el.locator("#panneau-loge").inner_text()
    if catalogue:
        verifier("kishali_tete" in options and "bandana" in options and "Bientôt, gratuits" not in t, f"{nom} : la loge propose le kishali et le bandana, portables")
        ok = await el.evaluate("""async () => { const r = await CompteCommun.reprendre(); const a = JSON.parse(JSON.stringify(r.fiche.avatar));
          a.objets.tete = 'kishali_tete'; a.objets.epaule = 'kishali'; return (await CompteCommun.porter(a)).ok; }""")
        verifier(ok is True, f"{nom} : commun_porter accepte le kishali (tête et épaules)")
    else:
        verifier("kishali_tete" not in options and "Bientôt, gratuits" in t, f"{nom} : la loge annonce le kishali et le bandana pour bientôt")
    # L'enseignant·e : offrir et archiver seulement si les deux sont là
    await prof.goto(base + "/enseignant/#/classe/" + code[1])
    await prof.get_by_label("Ton code d'enseignant·e").fill(code[0])
    await prof.get_by_role("button", name="Ouvrir mon espace").click()
    await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
    t = await prof.locator("main").text_content()  # les volets fermés compris
    les_deux = bool(catalogue and reglage)
    verifier((await prof.locator("select[id^=trophee]").count() > 0) == les_deux and ("arrive avec le catalogue" in t) != les_deux,
             f"{nom} : « Offrir un trophée » {'proposé' if les_deux else 'annoncé pour plus tard, sans liste'}")
    verifier(("Archiver la classe" in t) == les_deux, f"{nom} : « Archiver la classe » {'proposé' if les_deux else 'absent'}")
    if les_deux:
        await prof.locator("summary", has_text="Offrir un trophée").click()
        opts = await prof.locator("select[id^=trophee] option").evaluate_all("o => o.map(x => x.value)")
        verifier(opts and all(o.startswith(("tete:", "visage:", "cou:", "dos:", "main:", "epaule:", "pieds:", "autour:")) for o in opts) and "main:bouteille_percee" in opts,
                 f"{nom} : seulement les trophées de la classe ({len(opts)})")
        await prof.get_by_label("Motif", exact=True).last.fill("A réparé <b>la</b> souris")
        await prof.get_by_role("button", name="Offrir").click()
        await attendre_texte(prof, "trophée offert")
        await prof.locator("summary", has_text="Réglages de la classe").click()
        await prof.get_by_role("button", name="Archiver la classe").click()
        await attendre_texte(prof, "La classe est archivée")
        await prof.get_by_role("link", name="← Mes classes").click()
        await attendre_texte(prof, "Classes archivées (1)")
        verifier(True, f"{nom} : la classe archivée est rangée à part (commun_prof_archiver_classe)")
        await el.reload()
        await attendre_texte(el, "Salut, Lou")
        await el.get_by_role("tab", name="Trophées").click()
        verifier("A réparé <b>la</b> souris" in await el.locator("#panneau-trophees").inner_text(), f"{nom} : l'élève lit le motif tel quel")
    verifier(not monde.erreurs_js, f"{nom} : aucune erreur JavaScript {monde.erreurs_js[:2]}")
    await ctx.close()
    serveur.shutdown()


async def principal(psql, captures, catalogue=None):
    from playwright.async_api import async_playwright
    base_psql = preparer(psql)
    serveur, base = demarrer_serveur(base_psql)
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        await parcours(Monde(nav, base), captures)
        serveur.shutdown()
        if catalogue:
            for en_base in (False, True):
                for reglage in (False, True):
                    await combinaison(nav, psql, catalogue if en_base else None, reglage)
        else:
            print("(les quatre combinaisons de la migration 0010 sont sautées : --catalogue manque)")
        await nav.close()
    print(f"\n{len(ECHECS)} échec(s).")
    return 1 if ECHECS else 0


def main():
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--psql", required=True, help="la commande psql d'un Postgres LOCAL, entre guillemets (sans -d)")
    a.add_argument("--captures", default=None)
    a.add_argument("--catalogue", default=None, help="le fichier de la migration 0010 (catalogue), pour essayer les quatre combinaisons")
    args = a.parse_args()
    if "supabase.co" in args.psql or "pooler" in args.psql:
        sys.exit("Ce test ne se lance jamais sur la base réelle.")
    if args.captures:
        os.makedirs(args.captures, exist_ok=True)
    sys.exit(asyncio.run(principal(args.psql, args.captures, args.catalogue)))


if __name__ == "__main__":
    main()
