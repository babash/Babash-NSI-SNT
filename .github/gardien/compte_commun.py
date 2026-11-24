#!/usr/bin/env python3
"""Les parcours du compte commun sur une base LOCALE, derrière une imitation STRICTE de l'API (Gardien, T132d).

1. rejoue les parcours de l'Architecte (scripts/tests/test_compte_commun_en_ligne.py du dossier testé),
   mais derrière .github/gardien/api_stricte.py (clés du corps vérifiées comme PostgREST, lecture seule pour
   les fonctions STABLE, délai de 3 s du rôle anon, en-tête apikey exigé, Authorization interdit) ;
2. ajoute les attaques et les parcours du Gardien : injections (pseudo, nom de classe, nom affiché,
   établissement), caractères invisibles et texte de droite à gauche, titre de la page, console,
   stockage, QR code recalculé, projection, renommer, retirer, archiver, « Ce n'est pas moi »,
   trop d'essais (élève, classe), base lente, effacer ses données, supprimer l'espace.
Usage (à la racine du dépôt) : python3 -I -B .github/gardien/compte_commun.py . "psql -h SOCKET -p PORT -U postgres" [CAPTURES]
Jamais la base réelle : un Postgres LOCAL (16 ou plus), reconstruit avec supabase/ par l'essai de l'Architecte.
Il faut Playwright et Chromium. Code de retour : 0 si tout passe.
"""
import asyncio
import importlib.util
import json
import os
import re
import shlex
import sys
import time
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(sys.argv[1])
PSQL = sys.argv[2]
CAPTURES = sys.argv[3] if len(sys.argv) > 3 else None
sys.path.insert(0, ICI)
import api_stricte as serveur_strict  # noqa: E402

spec = importlib.util.spec_from_file_location("t_archi", os.path.join(RACINE, "scripts", "tests", "test_compte_commun_en_ligne.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

ECHECS = []
NOTES = []


def verifier(cond, quoi):
    print(("OK     " if cond else "ÉCHEC  ") + quoi, flush=True)
    if not cond:
        ECHECS.append(quoi)


class MondeStrict(T.Monde):
    """Comme le Monde de l'Architecte, mais les en-têtes de la page vont jusqu'à l'API stricte,
    et l'on garde la console, les boîtes de dialogue et les titres."""

    def __init__(self, nav, base):
        super().__init__(nav, base)
        self.console, self.dialogues, self.titres = [], [], []

    async def appareil(self, largeur=1440, theme="light", reseau="10.0.0.1"):
        ctx = await self.nav.new_context(viewport={"width": largeur, "height": 900}, color_scheme=theme)

        async def api(route):
            req = route.request
            if req.method == "OPTIONS":
                await route.fulfill(status=200, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "apikey, content-type"})
                return
            corps = req.post_data or "{}"
            h = {k.lower(): v for k, v in (await req.all_headers()).items()}
            entetes = {"Content-Type": "application/json", "X-Forwarded-For": reseau}
            if "apikey" in h:
                entetes["apikey"] = h["apikey"]
            if "authorization" in h:
                entetes["Authorization"] = h["authorization"]

            def poster():
                r = urllib.request.Request(self.base + "/rest/v1/rpc/" + req.url.rsplit("/", 1)[1], data=corps.encode(), headers=entetes, method="POST")
                try:
                    with urllib.request.urlopen(r, timeout=60) as rep:
                        return rep.status, rep.read()
                except urllib.error.HTTPError as e:
                    return e.code, e.read()
            statut, contenu = await asyncio.to_thread(poster)
            await route.fulfill(status=statut, body=contenu, headers={"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"})

        async def reglages(route):
            await route.fulfill(status=200, body=self.reglages, headers={"Content-Type": "application/javascript"})
        await ctx.route(T.BASE_API + "/**", api)
        await ctx.route("**/reglages.js", reglages)
        ctx.on("request", lambda r: self.requetes.append(r.url))
        return ctx

    async def page(self, ctx, chemin):
        pg = await ctx.new_page()
        pg.on("pageerror", lambda e: self.erreurs_js.append(str(e)))
        pg.on("console", lambda m: self.console.append(m.text))

        async def dialogue(d):
            self.dialogues.append(d.message)
            await d.dismiss()
        pg.on("dialog", lambda d: asyncio.ensure_future(dialogue(d)))
        pg.on("framenavigated", lambda f: self.titres.append(f.url))
        await pg.goto(self.base + chemin)
        return pg


async def titre(pg, monde):
    t = await pg.title()
    monde.titres.append(t)
    return t


async def stockage(pg):
    return await pg.evaluate("""() => { const r = {}; for (const s of ['sessionStorage', 'localStorage']) {
        try { const m = window[s]; r[s] = {}; for (let i = 0; i < m.length; i++) { const k = m.key(i); r[s][k] = m.getItem(k); } } catch (e) { r[s] = null; } }
        return r; }""")


async def visible_texte(pg, texte):
    return await pg.evaluate("""t => { const n = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (w.nextNode()) { const x = w.currentNode; if (x.nodeValue.includes(t)) { const e = x.parentElement;
          const s = getComputedStyle(e); const r = e.getBoundingClientRect();
          if (e.closest('[hidden]') === null && s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0 && e.checkVisibility()) n.push(e.className || e.tagName); } }
        return n; }""", texte)


async def creer_eleve(monde, lien, pseudo, reseau, largeur=320, theme="dark", telephone=False):
    ctx = await monde.appareil(largeur=largeur, theme=theme, reseau=reseau)
    pg = await monde.page(ctx, lien)
    await pg.get_by_label("Ton prénom ou un pseudo").first.fill(pseudo)
    if telephone:
        await pg.locator("#titre-creer").locator("xpath=..").get_by_label("C'est mon téléphone").check()
    await pg.get_by_role("button", name="Créer mon code").click()
    return ctx, pg


async def parcours_gardien(monde):
    codes, jetons = [], []
    # ── A. Enseignant·e : nom affiché et établissement piégés ──
    pctx = await monde.appareil(largeur=1440, theme="light", reseau="10.1.0.1")
    prof = await monde.page(pctx, "/enseignant/")
    nom_piege = '<img src=x onerror=alert(1)>'
    etab_piege = '"><svg onload=alert(2)> Lycée'
    await prof.get_by_label("Nom affiché aux élèves").fill(nom_piege)
    await prof.get_by_label("Établissement (facultatif)").fill(etab_piege)
    await prof.get_by_role("button", name="Créer mon espace").click()
    code_prof = (await prof.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    codes.append(code_prof)
    t = await titre(prof, monde)
    verifier(code_prof not in t and code_prof.replace("-", "") not in t, f"le titre de la page ne porte pas le code d'enseignant·e (« {t} »)")
    st = await stockage(prof)
    verifier(code_prof not in json.dumps(st) and code_prof.replace("-", "") not in json.dumps(st), "le code d'enseignant·e montré n'est gardé ni dans l'onglet ni dans le navigateur")
    verifier("#" not in prof.url or code_prof not in prof.url, "le code d'enseignant·e n'est pas dans l'adresse")
    # « Je l'ai noté » demande les 4 chiffres (T132f) : une erreur, ou « Imprimer », ne font jamais perdre le code
    if await prof.get_by_label("Retape les 4 chiffres de ton code").count():
        await prof.get_by_role("button", name="Je l'ai noté").click()
        await prof.wait_for_timeout(500)
        verifier(code_prof in await prof.locator(".cc-ton-code").inner_text(), "« Je l'ai noté » sans les 4 chiffres : refusé, le code reste affiché")
        await prof.get_by_label("Retape les 4 chiffres de ton code").fill("0000" if not code_prof.endswith("0000") else "1111")
        await prof.get_by_role("button", name="Je l'ai noté").click()
        await T.attendre_texte(prof, "Ce ne sont pas les bons chiffres")
        verifier(code_prof in await prof.locator(".cc-ton-code").inner_text(), "4 chiffres faux : refusés, le code reste affiché")
        await prof.evaluate("() => { window.print = () => {}; }")
        await prof.get_by_role("button", name="Imprimer").click()
        await prof.wait_for_timeout(500)
        verifier(code_prof in await prof.locator(".cc-ton-code").inner_text(), "« Imprimer » n'envoie pas le formulaire : le code reste affiché")
        await prof.get_by_label("Retape les 4 chiffres de ton code").fill(code_prof[-4:])
        # la base injoignable au moment de « Je l'ai noté » : que devient l'affichage du code ?
        await pctx.set_offline(True)
        await prof.get_by_role("button", name="Je l'ai noté").click()
        await prof.wait_for_timeout(800)
        garde = await prof.locator(".cc-ton-code").count() and code_prof in await prof.locator("main").inner_text()
        NOTES.append("Hors ligne au moment de « Je l'ai noté » (4 chiffres justes) : " + ("le code reste affiché" if garde else "la page revient à l'entrée, le code n'est plus affiché"))
        await pctx.set_offline(False)
        if not garde:
            await prof.get_by_label("Ton code d'enseignant·e").fill(code_prof)
            await prof.get_by_role("button", name="Ouvrir mon espace").click()
        else:
            await prof.get_by_role("button", name="Je l'ai noté").click()
    else:
        await prof.get_by_role("button", name="Je l'ai noté").click()
    await T.attendre_texte(prof, "Mes classes")
    st = await stockage(prof)
    verifier(code_prof not in json.dumps(st), "après « Je l'ai noté » (sans « Rester ouvert »), le code n'est dans aucun stockage")
    n = await prof.evaluate("t => document.body.innerText.includes(t)", code_prof)
    verifier(not n, "après « Je l'ai noté », le code d'enseignant·e n'est plus à l'écran (montré une seule fois)")
    barre = await prof.locator(".cc-barre-espace").inner_text()
    verifier(nom_piege in barre and await prof.locator("img[src=x]").count() == 0 and await prof.locator("svg[onload]").count() == 0,
             "nom affiché et établissement piégés : montrés comme du texte, rien n'est interprété")

    # ── B. Classes : nom piégé, puis texte de droite à gauche refusé ──
    nom_classe = "<script>alert(3)</script>"
    await prof.locator("summary", has_text="Nouvelle classe").click()
    await prof.get_by_label("Nom de la classe").fill(nom_classe)
    await prof.get_by_role("button", name="Créer la classe").click()
    await prof.locator("h2.cc-titre-section", has_text=nom_classe).wait_for(timeout=15000)
    code_classe = (await prof.locator(".cc-code-moyen").inner_text()).strip()
    lien = await prof.locator(".cc-lien-url a").get_attribute("href")
    qr_page = await prof.locator(".cc-qr").inner_html()
    qr_calcule = await prof.evaluate("t => { const q = qrcode(0, 'M'); q.addData(t); q.make(); const d = document.createElement('div'); d.innerHTML = q.createSvgTag({ cellSize: 4, margin: 2, scalable: true }); return d.innerHTML; }", lien)
    verifier(qr_page.strip() == qr_calcule.strip(), "le QR code de la page code exactement le lien de classe (recalculé)")
    qr_autre = await prof.evaluate("t => { const q = qrcode(0, 'M'); q.addData(t + 'X'); q.make(); const d = document.createElement('div'); d.innerHTML = q.createSvgTag({ cellSize: 4, margin: 2, scalable: true }); return d.innerHTML; }", lien)
    verifier(qr_page.strip() != qr_autre.strip(), "le contrôle du QR code est discriminant (un autre texte donne un autre dessin)")
    verifier(re.fullmatch(r"https://babash\.github\.io/Babash-NSI-SNT/eleve/\?classe=[A-HJ-NP-Z]{4}", lien or "") is not None,
             f"le lien de classe ne porte que le code public de la classe ({lien})")
    classe_id = prof.url.split("#/classe/")[-1]
    await prof.get_by_role("link", name="Inviter les élèves (à projeter)").click()
    await prof.locator(".cc-code-projete").wait_for(timeout=15000)
    txt = await prof.locator(".cc-inviter").inner_text()
    verifier(code_classe in txt and code_prof not in txt and "nom de famille" in txt, "l'écran à projeter : le code de classe, le QR code, « jamais ton nom de famille », pas le code d'enseignant·e")
    if CAPTURES:
        await prof.screenshot(path=os.path.join(CAPTURES, "g37-inviter-1440-clair.png"), full_page=True)
    await prof.get_by_role("link", name="← Retour à la classe").click()
    await prof.locator("h2.cc-titre-section", has_text=nom_classe).wait_for(timeout=15000)
    await prof.get_by_role("link", name="← Mes classes").click()
    await prof.locator("h2.cc-titre-section", has_text=re.compile(r"^Mes classes$")).wait_for(timeout=15000)
    rtl = "1re NSI " + chr(0x202E) + "gnp.exe"
    await prof.locator("summary", has_text="Nouvelle classe").click()
    await prof.get_by_label("Nom de la classe").fill(rtl)
    await prof.get_by_role("button", name="Créer la classe").click()
    await prof.wait_for_timeout(1500)
    verifier(await prof.locator(".cc-classe-carte").count() == 1, "un nom de classe avec un caractère de droite à gauche est refusé")
    msg = await prof.locator("details", has_text="Nouvelle classe").locator(".cc-message").inner_text()
    NOTES.append("Message du refus (droite à gauche) : « " + msg.strip() + " »")
    await prof.get_by_label("Nom de la classe").fill("TNSI 1")
    await prof.get_by_role("button", name="Créer la classe").click()
    await prof.locator("h2.cc-titre-section", has_text="TNSI 1").wait_for(timeout=15000)
    await prof.get_by_role("link", name="← Mes classes").click()
    await prof.locator("h2.cc-titre-section", has_text=re.compile(r"^Mes classes$")).wait_for(timeout=15000)
    verifier(await prof.locator(".cc-classe-carte").count() == 2, "les deux classes sont sur l'accueil de l'espace (attente du titre « Mes classes »)")

    # ── C. Élèves : pseudos piégés, caractères invisibles refusés ──
    chemin = "/eleve/?classe=" + code_classe
    ctx1, s1 = await creer_eleve(monde, chemin, "Ali" + chr(0x202E) + "xe", "10.1.0.2")
    await s1.wait_for_timeout(800)
    verifier("2 à 24" in await s1.locator("#titre-creer").locator("xpath=..").inner_text(), "pseudo avec un caractère de droite à gauche : refusé, avec un message")
    await s1.get_by_label("Ton prénom ou un pseudo").first.fill("Bo" + chr(0x200B) + "b")
    await s1.get_by_role("button", name="Créer mon code").click()
    await s1.wait_for_timeout(500)
    verifier(await s1.locator(".cc-code-grand").count() == 0, "pseudo avec un caractère invisible : refusé")
    # le même refus côté base, sans passer par la page
    rep = await s1.evaluate("async () => (await CompteCommun.prof.creerEspace('Mme' + String.fromCharCode(0x202E) + 'X', null))")
    verifier(rep.get("ok") is False, "la base refuse aussi un nom affiché avec un caractère de droite à gauche")
    page_classe = await s1.locator(".cc-classe-lien").inner_text()
    verifier(nom_classe in page_classe and nom_piege in page_classe, "la page élève montre le nom de classe et le nom affiché piégés comme du texte")
    pseudo_piege = '"><b onmouseover=x>'
    await s1.get_by_label("Ton prénom ou un pseudo").first.fill(pseudo_piege)
    await s1.get_by_role("button", name="Créer mon code").click()
    code1 = (await s1.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    codes.append(code1)
    t = await titre(s1, monde)
    verifier(code1 not in t, f"le titre de la page ne porte pas le code de l'élève (« {t} »)")
    await s1.get_by_label("Retape les 3 chiffres de ton code").fill("000" if code1[-3:] != "000" else "111")
    await s1.get_by_role("button", name="C'est noté").click()
    await T.attendre_texte(s1, "Ce ne sont pas les bons chiffres")
    verifier(await s1.locator(".cc-code-grand").count() == 1, "3 chiffres faux : le code reste affiché, l'élève recommence")
    await s1.get_by_label("Retape les 3 chiffres de ton code").fill(code1[-3:])
    await s1.get_by_role("button", name="C'est noté").click()
    await T.attendre_texte(s1, "Salut, " + pseudo_piege)
    verifier(await s1.locator("b[onmouseover]").count() == 0, "le pseudo piégé est montré comme du texte dans la planque")
    verifier("classe=" not in s1.url, "le code de classe a quitté l'adresse")
    st = await stockage(s1)
    ses = (st.get("sessionStorage") or {}).get("compte-commun:session")
    verifier(ses is not None and "compte-commun:session" not in (st.get("localStorage") or {}), "jeton dans l'onglet seulement (sans « C'est mon téléphone »)")
    j1 = json.loads(ses)["jeton"]
    jetons.append(j1)
    verifier(code1 not in json.dumps(st), "le code de l'élève n'est gardé nulle part sur l'appareil")
    # deuxième élève, au téléphone
    ctx2, s2 = await creer_eleve(monde, chemin, "Zoé", "10.1.0.3", largeur=768, theme="light", telephone=True)
    code2 = (await s2.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    codes.append(code2)
    await s2.get_by_label("Retape les 3 chiffres de ton code").fill(code2[-3:])
    await s2.get_by_role("button", name="C'est noté").click()
    await T.attendre_texte(s2, "Salut, Zoé")
    st2 = await stockage(s2)
    j2 = json.loads(st2["localStorage"]["compte-commun:session"])["jeton"]
    jetons.append(j2)
    # l'onglet « Applications » : ce qu'il promet
    await s2.get_by_role("tab", name="Applications").click()
    apps = await s2.locator("#panneau-applications").inner_text()
    NOTES.append("Onglet Applications : " + " | ".join(apps.split("\n")[:3]))
    # la classe vue par Zoé
    await s2.get_by_role("tab", name="Ma classe").click()
    txt = await s2.locator("#panneau-classe").inner_text()
    verifier(pseudo_piege in txt and code1 not in txt and "XP" not in txt and "crédit" not in txt.lower().replace("personne ne voit tes crédits", ""),
             "Zoé voit le pseudo piégé comme du texte, sans code, sans XP ni crédits des autres")

    # ── D. L'enseignant·e : projection, renommer, retirer, archiver ──
    await prof.locator(".cc-classe-lien-nom", has_text=nom_classe).click()
    await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
    verifier(await prof.locator("b[onmouseover]").count() == 0 and len(monde.dialogues) == 0, "côté enseignant·e, le pseudo piégé reste du texte")
    vis = await visible_texte(prof, code1)
    verifier(len(vis) >= 1, "hors projection, le code de l'élève est visible pour l'enseignant·e")
    await prof.get_by_label("Mode projection").check()
    vis1, vis2 = await visible_texte(prof, code1), await visible_texte(prof, code2)
    xpv = await prof.evaluate("() => [...document.querySelectorAll('.cc-suivi')].filter(e => e.checkVisibility()).length")
    verifier(not vis1 and not vis2 and xpv == 0, f"en projection : aucun code d'élève visible ({vis1 + vis2}), ni XP ni crédits ({xpv} bloc(s) de suivi visibles)")
    if CAPTURES:
        await prof.screenshot(path=os.path.join(CAPTURES, "g37-classe-projection-1440.png"), full_page=True)
    await prof.get_by_label("Mode projection").uncheck()
    carte = prof.locator(".cc-eleve", has=prof.locator(".cc-eleve-nom", has_text="Zoé"))
    await carte.locator("summary", has_text="Pseudo, code, retrait").click()
    await carte.get_by_label("Nouveau pseudo").fill("Zoé R")
    await carte.get_by_role("button", name="Renommer").click()
    await prof.locator(".cc-eleve-nom", has_text="Zoé R").wait_for(timeout=15000)
    await s2.reload()
    await T.attendre_texte(s2, "Salut, Zoé R")
    verifier(True, "l'enseignant·e renomme Zoé : la planque de Zoé le montre")
    carte1 = prof.locator(".cc-eleve", has=prof.locator(".cc-eleve-nom", has_text=pseudo_piege))
    await carte1.locator("summary", has_text="Pseudo, code, retrait").click()
    await carte1.get_by_role("button", name="Retirer de la classe").click()
    await prof.get_by_role("button", name="Oui, retirer " + pseudo_piege).click()
    await prof.wait_for_timeout(1500)
    await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
    noms = await prof.locator(".cc-eleve-nom").all_inner_texts()
    verifier(noms == ["Zoé R"], f"retiré·e de la classe : l'enseignant·e ne voit plus que {noms}")
    rep = await s1.evaluate("async () => (await CompteCommun.maClasse())")
    verifier(rep.get("ok") and rep.get("classes") == [], "l'élève retiré·e n'a plus de classe, son compte reste")
    await prof.locator("summary", has_text="Réglages de la classe").click()
    if await prof.get_by_role("button", name="Archiver la classe").count():
        # après 0010 (COMPTE_COMMUN_CATALOGUE) : archiver range la classe à part
        await prof.get_by_role("button", name="Archiver la classe").click()
        await T.attendre_texte(prof, "archivée")
        await prof.get_by_role("link", name="← Mes classes").click()
        await prof.locator("h2.cc-titre-section", has_text=re.compile(r"^Mes classes$")).wait_for(timeout=15000)
        arch = await prof.locator("details", has_text="Classes archivées").count()
        ouvertes = await prof.locator("ul.cc-classes").first.inner_text()
        verifier(arch == 1 and nom_classe not in ouvertes.split("Classes archivées")[0], "la classe archivée est rangée à part (« Classes archivées »)")
    else:
        # avant 0010 : seule la case « Inscriptions ouvertes » ; la classe reste avec les autres, rien ne parle d'archive
        reglages_classe = prof.locator("details", has_text="Réglages de la classe")
        await reglages_classe.get_by_label("Inscriptions ouvertes").uncheck()
        await reglages_classe.get_by_role("button", name="Enregistrer").first.click()
        await prof.wait_for_timeout(1500)
        await prof.get_by_role("link", name="← Mes classes").click()
        await prof.locator("h2.cc-titre-section", has_text=re.compile(r"^Mes classes$")).wait_for(timeout=15000)
        txt = await prof.locator("main").inner_text()
        verifier("archiv" not in txt.lower() and "inscriptions fermées" in txt and nom_classe in await prof.locator("ul.cc-classes").first.inner_text(),
                 "avant 0010 : inscriptions fermées, la classe reste avec les autres, aucun mot sur l'archive")
    if CAPTURES:
        await prof.screenshot(path=os.path.join(CAPTURES, "g37-accueil-fermee-1440.png"), full_page=True)
    ctx3, s3 = await creer_eleve(monde, chemin, "Sam", "10.1.0.4")
    code3 = (await s3.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    codes.append(code3)
    await s3.get_by_label("Retape les 3 chiffres de ton code").fill(code3[-3:])
    await s3.get_by_role("button", name="C'est noté").click()
    await T.attendre_texte(s3, "Salut, Sam")
    txt3 = await s3.locator("main").inner_text()
    verifier("fermées" in txt3, "inscriptions fermées : un·e nouvel·le élève ne peut pas rejoindre la classe, et le message le dit (son code est créé quand même)")
    rep = await s2.evaluate("async () => (await CompteCommun.maClasse()).classes.length")
    verifier(rep == 1, "inscriptions fermées : Zoé voit toujours la classe dans « Ma classe »")

    # ── E. « Ce n'est pas moi » ──
    await s2.reload()
    await T.attendre_texte(s2, "Salut, Zoé R")
    await s2.get_by_role("button", name="Ce n'est pas moi").click()
    await T.attendre_texte(s2, "Ce compte est fermé sur cet appareil")
    st2 = await stockage(s2)
    verifier("compte-commun:session" not in json.dumps(st2), "« Ce n'est pas moi » : plus aucun jeton sur l'appareil")
    await s2.reload()
    await s2.get_by_label("Ton code", exact=True).wait_for(timeout=15000)
    rep = await s2.evaluate("async ([j, k]) => (await (await fetch('https://cukahpyqkljiddmimpyi.supabase.co/rest/v1/rpc/commun_reprise', {method: 'POST', headers: {'Content-Type': 'application/json', apikey: k}, body: JSON.stringify({p_jeton: j})})).json())", [j2, serveur_strict.CLE])
    verifier(rep.get("ok") is False, "« Ce n'est pas moi » ferme aussi la session dans la base (l'ancien jeton ne marche plus)")
    await s2.get_by_label("Ton code", exact=True).fill(code2.lower())
    await s2.get_by_role("button", name="Entrer").click()
    await T.attendre_texte(s2, "Salut, Zoé R")
    verifier(True, "Zoé revient avec son code, en minuscules")

    # ── F. Trop d'essais : élève (20 par heure), puis classe (30 par heure) ──
    ictx = await monde.appareil(largeur=320, theme="light", reseau="10.1.0.9")
    pi = await monde.page(ictx, "/eleve/")
    await pi.get_by_label("Ton code", exact=True).wait_for(timeout=15000)
    dernier = ""
    for i in range(21):
        dernier = await pi.evaluate("async c => (await CompteCommun.entrer(c)).message", "PIRATE-ETRAVE-%03d" % (500 + i))
    verifier("Trop d'essais" in dernier, f"élève : après 20 codes faux depuis un réseau, « {dernier} »")
    await pi.get_by_label("Ton code", exact=True).fill(code3)
    await pi.get_by_role("button", name="Entrer").click()
    await pi.wait_for_timeout(1500)
    bloque = await pi.locator("main").inner_text()
    NOTES.append("Après 20 échecs, le bon code depuis le même réseau : " + ("refusé (Trop d'essais)" if "Trop d'essais" in bloque else "accepté"))
    rep = await s3.evaluate("async c => (await CompteCommun.entrer(c)).ok", code3)
    verifier(rep is True, "un autre réseau entre toujours (le blocage est par réseau)")
    dernier = ""
    for i in range(31):
        dernier = await pi.evaluate("async c => (await CompteCommun.classeParCode(c)).message", "ZZZ" + "ABCDEFGHJKLMNPQRSTUVWXYZ"[i % 24])
    verifier("Trop d'essais" in (dernier or ""), f"classe : après 30 codes de classe faux, « {dernier} »")
    await pi.goto(monde.base + "/eleve/?classe=" + code_classe)
    await pi.wait_for_timeout(1500)
    NOTES.append("Lien de classe ouvert depuis un réseau bloqué : « " + (await pi.locator(".cc-classe-lien").inner_text()).strip()[:120] + " »")
    # l'enseignant·e, sur le même réseau, débloque la salle
    dctx = await monde.appareil(largeur=1440, theme="light", reseau="10.1.0.9")
    pd = await monde.page(dctx, "/enseignant/")
    await pd.get_by_label("Ton code d'enseignant·e").fill(code_prof)
    await pd.get_by_role("button", name="Ouvrir mon espace").click()
    await pd.locator("h2.cc-titre-section", has_text=re.compile(r"^Mes classes$")).wait_for(timeout=15000)
    await pd.locator("summary", has_text="Réglages de mon espace").click()
    await pd.get_by_role("button", name="Débloquer le réseau de la salle").click()
    await T.attendre_texte(pd, "remis à zéro")
    await pi.goto(monde.base + "/eleve/")
    await pi.get_by_label("Ton code", exact=True).fill(code3)
    await pi.get_by_role("button", name="Entrer").click()
    await T.attendre_texte(pi, "Salut, Sam")
    verifier(True, "« Débloquer le réseau de la salle » (enseignant·e sur le même réseau) : l'élève bloqué·e entre de nouveau")
    await pd.close()
    await dctx.close()

    # ── G. Base lente (au-delà de 20 s), puis normale ──
    lctx = await monde.appareil(largeur=768, theme="dark", reseau="10.1.0.11")
    pl = await monde.page(lctx, "/eleve/")
    await pl.get_by_label("Ton code", exact=True).wait_for(timeout=40000)
    serveur_strict.RETARD["secondes"] = 21.5
    await pl.get_by_label("Ton code", exact=True).fill(code3)
    await pl.get_by_role("button", name="Entrer").click()
    await T.attendre_texte(pl, "trop de temps", delai=40000)
    verifier(True, "base lente : « met trop de temps à répondre », la page ne se bloque pas")
    serveur_strict.RETARD["secondes"] = 0
    await pl.get_by_role("button", name="Entrer").click()
    await T.attendre_texte(pl, "Salut, Sam", delai=20000)
    verifier(True, "la base revient : le même bouton marche")

    # ── H. Effacer mes données (l'élève retiré·e) ──
    await s1.reload()
    await T.attendre_texte(s1, "Salut, " + pseudo_piege)
    await s1.get_by_role("tab", name="Crédits et codes").click()
    await s1.locator("summary", has_text="Effacer mes données").click()
    await s1.get_by_label("Écris EFFACER pour confirmer").fill("EFFACER")
    await s1.get_by_role("button", name="Effacer mes données").click()
    await T.attendre_texte(s1, "est effacé")
    rep = await s3.evaluate("async c => (await CompteCommun.entrer(c)).message", code1)
    verifier("n'existe pas" in (rep or ""), "après « Effacer mes données », le code ne marche plus")

    # ── I. L'enseignant·e : rester ouvert dans l'onglet, puis supprimer l'espace ──
    p2ctx = await monde.appareil(largeur=320, theme="dark", reseau="10.1.0.12")
    p2 = await monde.page(p2ctx, "/enseignant/")
    await p2.get_by_label("Ton code d'enseignant·e").fill(code_prof)
    await p2.get_by_label("Rester ouvert dans cet onglet").check()
    await p2.get_by_role("button", name="Ouvrir mon espace").click()
    await T.attendre_texte(p2, "Mes classes")
    st = await stockage(p2)
    dans_onglet = code_prof in json.dumps(st.get("sessionStorage") or {})
    dans_nav = code_prof in json.dumps(st.get("localStorage") or {})
    NOTES.append(f"« Rester ouvert dans cet onglet » : code d'enseignant·e dans sessionStorage = {dans_onglet}, dans localStorage = {dans_nav}")
    verifier(not dans_nav, "le code d'enseignant·e n'est jamais dans le navigateur (localStorage)")
    await p2.reload()
    await T.attendre_texte(p2, "Mes classes")
    verifier(True, "avec « Rester ouvert dans cet onglet », l'espace se rouvre au rechargement de l'onglet")
    if CAPTURES:
        await p2.screenshot(path=os.path.join(CAPTURES, "g37-espace-320-obscur.png"), full_page=True)
    await p2.locator("summary", has_text="Réglages de mon espace").click()
    await p2.get_by_label("Écris SUPPRIMER pour confirmer").fill("SUPPRIMER")
    await p2.get_by_role("button", name="Supprimer mon espace").click()
    await T.attendre_texte(p2, "sont supprimés")
    st = await stockage(p2)
    verifier(code_prof not in json.dumps(st), "après la suppression, le code d'enseignant·e n'est plus dans l'onglet")
    rep = await s2.evaluate("async () => (await CompteCommun.reprendre()).ok")
    verifier(rep is True, "les comptes des élèves restent après la suppression de l'espace")

    # ── J. Ce qui est parti ──
    tout = [u for u in monde.requetes] + monde.titres
    fuite = [u for u in tout for c in codes + jetons if c in u or c.replace("-", "") in u]
    verifier(not fuite, f"aucun code ni jeton dans une adresse ou un titre ({len(tout)} adresses et titres relus)")
    fuite = [m for m in monde.console for c in codes + jetons if c in m or c.replace("-", "") in m]
    verifier(not fuite, f"aucun code ni jeton dans la console ({len(monde.console)} messages relus)")
    verifier(not monde.dialogues, f"aucune boîte de dialogue ouverte par une injection ({monde.dialogues[:2]})")
    hotes = sorted({re.match(r"^(\w+://[^/]+)", u).group(1) for u in monde.requetes if re.match(r"^\w+://", u)})
    verifier(set(hotes) <= {monde.base, T.BASE_API}, f"aucune requête vers un autre hôte ({', '.join(hotes)})")
    return codes, jetons


async def principal():
    from playwright.async_api import async_playwright
    base_psql = T.preparer(PSQL)
    serveur, base = serveur_strict.demarrer(RACINE, base_psql)
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        monde = MondeStrict(nav, base)
        print("── Les parcours de l'Architecte, derrière l'API stricte ──", flush=True)
        await T.parcours(monde, CAPTURES)
        a_echecs = list(T.ECHECS)
        print("── Les parcours du Gardien ──", flush=True)
        await parcours_gardien(monde)
        await nav.close()
    serveur.shutdown()
    print("\nFautes notées par l'API stricte :", len(serveur_strict.FAUTES))
    for f in sorted(set(serveur_strict.FAUTES)):
        print("   ", f)
    appels = serveur_strict.JOURNAL
    sans_cle = [a for a in appels if a["apikey"] != serveur_strict.CLE]
    avec_auth = [a for a in appels if a["authorization"]]
    fns = sorted({a["fn"] for a in appels})
    print(f"Appels : {len(appels)} ; fonctions appelées : {len(fns)} ; sans la clé publique : {len(sans_cle)} ; avec Authorization : {len(avec_auth)}")
    print("Fonctions appelées :", ", ".join(fns))
    print("\nNotes :")
    for n in NOTES:
        print("   ", n)
    total = len(a_echecs) + len(ECHECS)
    print(f"\nArchitecte : {len(a_echecs)} échec(s) ; Gardien : {len(ECHECS)} échec(s).")
    return 1 if total or serveur_strict.FAUTES else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(principal()))
