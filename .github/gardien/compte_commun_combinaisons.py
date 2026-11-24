#!/usr/bin/env python3
"""Le catalogue des avatars (migration 0010) et le réglage COMPTE_COMMUN_CATALOGUE : les quatre combinaisons (Gardien, T132g).

Pour chaque combinaison (0010 en base ou non, réglage vrai ou faux), derrière l'API stricte (.github/gardien/api_stricte.py) :
- l'enseignant·e : « Offrir un trophée » et « Archiver la classe » proposés seulement si les deux sont là, et alors
  offrir, archiver PUIS désarchiver depuis la page ; « Accorder un haut fait » dès que le catalogue est en base ; l'XP
  attribuée arrive en crédits ;
- l'élève : la boutique, les hauts faits, les trophées et la loge disent vrai (rien de « Pour l'avoir » d'une application
  qui ne lit pas encore le compte, « Ton enseignant·e peut te l'offrir » seulement si c'est possible) ;
- l'API : aucun appel à une fonction absente de la base, aucune faute, aucun 404 du compte commun en console.
Puis le cas dégradé : la lecture du catalogue échoue au chargement de l'espace (la base répond ensuite) ; la page ne
doit alors rien proposer d'impossible (« Archiver » sans 0010) ni dire « déjà tous les trophées ».
Usage (à la racine du dépôt) : python3 -I -B .github/gardien/compte_commun_combinaisons.py . "psql -h SOCKET -p PORT -U postgres" 0010.sql
Jamais la base réelle : un Postgres LOCAL (16 ou plus), reconstruit avec supabase/ par l'essai de l'Architecte.
Code de retour : 0 si tout passe.
"""
import asyncio
import importlib.util
import os
import re
import sys
import traceback

RACINE = os.path.abspath(sys.argv[1])
PSQL = sys.argv[2]
MIGRATION = os.path.abspath(sys.argv[3])
if "supabase.co" in PSQL or "pooler" in PSQL:
    sys.exit("Cet essai ne se lance jamais sur la base réelle.")
sys.argv = [sys.argv[0], RACINE, PSQL]          # le harnais du Gardien lit ses arguments à l'import
spec = importlib.util.spec_from_file_location("harnais", os.path.join(os.path.dirname(os.path.abspath(__file__)), "compte_commun.py"))
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
T, S = H.T, H.serveur_strict
FONCTIONS_0010 = ("commun_prof_offrir", "commun_prof_archiver_classe")
ECHECS = []


def verifier(cond, quoi):
    print(("OK     " if cond else "ÉCHEC  ") + quoi, flush=True)
    if not cond:
        ECHECS.append(quoi)


async def texte(pg, sel):
    return (await pg.locator(sel).inner_text()) if await pg.locator(sel).count() else ""


async def creer_monde(nav, en_base, reglage):
    S.SIGN.clear(); S.JOURNAL.clear(); S.FAUTES.clear()
    serveur, base = S.demarrer(RACINE, T.preparer(PSQL, MIGRATION if en_base else None))
    monde = H.MondeStrict(nav, base)
    monde.reglages = re.sub(r"COMPTE_COMMUN_CATALOGUE:\s*(true|false)", "COMPTE_COMMUN_CATALOGUE: " + ("true" if reglage else "false"), monde.reglages)
    ctx = await monde.appareil(reseau="10.3.0.1")
    p0 = await monde.page(ctx, "/enseignant/")
    await p0.get_by_label("Nom affiché aux élèves").wait_for()
    code = await p0.evaluate("""async () => { const r = await CompteCommun.prof.creerEspace('M. Essai'); await CompteCommun.prof.ouvrir(r.code_affiche);
      const c = await CompteCommun.prof.creerClasse('Essai', ['td', 'quizz_nsi', 'vacances']); return [r.code_affiche, c.id, c.code]; }""")
    await p0.close()
    el = await monde.page(ctx, "/eleve/?classe=" + code[2])
    await el.get_by_label("Ton prénom ou un pseudo").fill("Lou")
    await el.get_by_role("button", name="Créer mon code").click()
    c = (await el.locator(".cc-code-grand").inner_text(timeout=15000)).strip()
    await el.get_by_label("Retape les 3 chiffres de ton code").fill(c[-3:])
    await el.get_by_role("button", name="C'est noté").click()
    await T.attendre_texte(el, "Salut, Lou")
    return serveur, base, monde, ctx, code, el


async def ouvrir_classe(monde, ctx, base, code, panne_catalogue=False):
    prof = await ctx.new_page()
    prof.on("pageerror", lambda e: monde.erreurs_js.append(str(e)))
    prof.on("console", lambda m: monde.console.append(m.text))
    if panne_catalogue:
        etat = {"n": 0}

        async def catalogue(route):
            etat["n"] += 1
            if etat["n"] == 1:
                await route.fulfill(status=503, body="{}", headers={"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"})
            else:
                await route.fallback()
        await prof.route(T.BASE_API + "/rest/v1/rpc/commun_catalogue", catalogue)
    await prof.goto(base + "/enseignant/#/classe/" + code[1])
    await prof.get_by_label("Ton code d'enseignant·e").fill(code[0])
    await prof.get_by_role("button", name="Ouvrir mon espace").click()
    await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
    return prof


def bilan_api(nom, monde, attendues):
    appels = [a["fn"] for a in S.JOURNAL]
    a0010 = sorted({f for f in appels if f in FONCTIONS_0010})
    verifier(a0010 == attendues, f"{nom} appels aux fonctions de 0010 : {a0010 or 'aucun'}")
    absentes = sorted({f for f in appels if S.SIGN.get(f, 1) is None})
    verifier(not absentes, f"{nom} aucune fonction absente de la base appelée {absentes}")
    verifier(not S.FAUTES, f"{nom} aucune faute de l'API stricte {S.FAUTES[:2]}")
    w = [m for m in monde.console if m.startswith("[compte commun]") and ("code 404" in m or "PGRST202" in m)]
    verifier(not w, f"{nom} aucun 404 du compte commun en console {w[:1]}")
    verifier(not monde.erreurs_js, f"{nom} aucune erreur JavaScript {monde.erreurs_js[:2]}")


async def combinaison(nav, en_base, reglage):
    nom = f"[0010 {'en base' if en_base else 'absente'}, réglage {'vrai' if reglage else 'faux'}]"
    print("──", nom, flush=True)
    les_deux = bool(en_base and reglage)
    serveur, base, monde, ctx, code, el = await creer_monde(nav, en_base, reglage)
    try:
        prof = await ouvrir_classe(monde, ctx, base, code)
        t = await prof.locator("main").text_content()
        verifier((await prof.locator("select[id^=trophee]").count() > 0) == les_deux, f"{nom} « Offrir un trophée » {'proposé' if les_deux else 'sans liste'}")
        verifier(("Offrir un trophée arrive avec le catalogue des avatars." in t) != les_deux, f"{nom} « Offrir un trophée arrive avec le catalogue » {'absent' if les_deux else 'présent'}")
        verifier("déjà tous les trophées" not in t, f"{nom} jamais « déjà tous les trophées » pour un·e élève qui n'en a aucun")
        verifier((await prof.get_by_role("button", name="Archiver la classe", include_hidden=True).count() > 0) == les_deux, f"{nom} « Archiver la classe » {'proposé' if les_deux else 'absent'}")
        verifier((await prof.locator("select[id^=hf]").count() > 0) == bool(en_base), f"{nom} « Accorder un haut fait » {'proposé' if en_base else 'annoncé avec le catalogue'}")
        # L'XP attribuée arrive en crédits (la phrase de la boutique : « seul·e ton enseignant·e peut t'en donner »)
        credits = "async () => (await CompteCommun.reprendre()).fiche.credits"
        c0 = await el.evaluate(credits)
        await prof.locator("summary", has_text="Attribuer de l'XP").first.click()
        await prof.get_by_label("Motif", exact=True).first.fill("Aide à un camarade")
        await prof.get_by_role("button", name="Attribuer").click()
        await T.attendre_texte(prof, "+10 XP")
        c1 = await el.evaluate(credits)
        verifier(c1 == c0 + 10, f"{nom} +10 XP de l'enseignant·e : crédits {c0} → {c1}")
        hf_nom = None
        if en_base:
            await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
            await prof.locator("summary", has_text="Accorder un haut fait").first.click()
            hf_nom = await prof.locator("select[id^=hf] option").first.inner_text()
            await prof.get_by_role("button", name="Accorder").click()
            await prof.wait_for_timeout(1500)
        if les_deux:
            await prof.locator(".cc-eleve").first.wait_for(timeout=15000)
            await prof.locator("summary", has_text="Offrir un trophée").first.click()
            opts = await prof.locator("select[id^=trophee] option").evaluate_all("o => o.map(x => x.value)")
            familles = await el.evaluate("async ids => { const c = await CompteCommun.catalogue(); return ids.map(i => (c.elements.find(e => e.id === i) || {}).famille); }", opts)
            verifier(opts and all(f == "classe" for f in familles), f"{nom} seulement des trophées de la famille « classe » ({len(opts)})")
            await prof.locator("select[id^=trophee]").select_option("main:bouteille_percee")
            await prof.get_by_label("Motif", exact=True).last.fill("A réparé la souris")
            await prof.get_by_role("button", name="Offrir").click()
            await T.attendre_texte(prof, "trophée offert")
            await prof.locator("summary", has_text="Réglages de la classe").click()
            await prof.get_by_role("button", name="Archiver la classe").click()
            await T.attendre_texte(prof, "La classe est archivée")
            await prof.get_by_role("link", name="← Mes classes").click()
            await T.attendre_texte(prof, "Classes archivées (1)")
            verifier("Toutes tes classes sont archivées." in await prof.locator("main").text_content(), f"{nom} la classe archivée est rangée à part")
            await prof.locator("summary", has_text="Classes archivées (1)").click()
            await prof.locator(".cc-classe-lien-nom", has_text="Essai").click()
            await prof.locator("summary", has_text="Réglages de la classe").wait_for(timeout=15000)
            await prof.locator("summary", has_text="Réglages de la classe").click()
            b = prof.get_by_role("button", name="Désarchiver la classe")
            try:
                await b.wait_for(timeout=8000)
                await b.click()
                await T.attendre_texte(prof, "La classe est désarchivée")
                await prof.get_by_role("link", name="← Mes classes").click()
                await prof.locator(".cc-classe-carte").first.wait_for(timeout=15000)
                verifier("Classes archivées" not in await prof.locator("main").text_content(), f"{nom} « Désarchiver la classe » : elle revient avec les autres")
            except Exception:
                boutons = await prof.locator("details", has_text="Réglages de la classe").first.get_by_role("button").all_inner_texts()
                verifier(False, f"{nom} « Désarchiver la classe » proposé pour une classe archivée (boutons : {boutons})")
        # L'élève
        await el.reload()
        await T.attendre_texte(el, "Salut, Lou")
        await el.get_by_role("tab", name="Boutique").click()
        tb = await texte(el, "#panneau-boutique")
        if en_base:
            verifier("Pour l'instant, seul·e ton enseignant·e peut t'en donner" in tb and "Tu les gagnes en travaillant" not in tb, f"{nom} boutique : « seul·e ton enseignant·e peut t'en donner »")
        else:
            verifier("ouvre bientôt" in tb, f"{nom} boutique « ouvre bientôt »")
        await el.get_by_role("tab", name="Hauts faits").click()
        th = await texte(el, "#panneau-hauts-faits")
        if en_base:
            bientot = re.findall(r"Bientôt, quand (.+?) lira ton code", th)
            verifier("Pour l'avoir" not in th and bientot and "Ressources NSI et SNT" not in bientot, f"{nom} hauts faits des applications « Bientôt, quand … lira ton code » ({sorted(set(bientot))})")
            verifier(hf_nom in th and "Gagné le" in th, f"{nom} le haut fait accordé (« {hf_nom} ») est gagné")
        else:
            verifier("Les hauts faits arrivent bientôt, avec le catalogue." in th, f"{nom} hauts faits « arrivent bientôt, avec le catalogue »")
        await el.get_by_role("tab", name="Trophées").click()
        tt = await texte(el, "#panneau-trophees")
        if en_base:
            verifier(("Ton enseignant·e peut te l'offrir." in tt) == les_deux and ("Bientôt, ton enseignant·e pourra te l'offrir." in tt) == (not les_deux),
                     f"{nom} trophées de la classe : « {'Ton enseignant·e peut te l’offrir' if les_deux else 'Bientôt, ton enseignant·e pourra te l’offrir'} »")
            apps = re.findall(r"Bientôt, avec un haut fait de (.+?)\.", tt)
            verifier(apps and "Ressources NSI et SNT" not in apps, f"{nom} trophées des applications « Bientôt, avec un haut fait de … » ({len(apps)})")
            verifier(all("accordé par ton enseignant·e" in x for x in tt.splitlines() if x.startswith("Se gagne avec")), f"{nom} « Se gagne avec » seulement pour les hauts faits de l'enseignant·e")
            if les_deux:
                lus = [x for x in tt.splitlines() if "souris" in x or x.startswith("Offert")]
                verifier(any("A réparé la souris" in x for x in lus), f"{nom} l'élève lit le motif du trophée offert ({lus[:2]})")
        await el.get_by_role("tab", name="Mon avatar").click()
        options = await el.locator("#panneau-loge option").evaluate_all("o => o.map(x => x.value)")
        tl = await texte(el, "#panneau-loge")
        verifier(("kishali_tete" in options and "bandana" in options) == bool(en_base) and ("Bientôt, gratuits" in tl) == (not en_base), f"{nom} loge : kishali et bandana {'proposés' if en_base else 'annoncés pour bientôt'}")
        bilan_api(nom, monde, sorted(FONCTIONS_0010) if les_deux else [])
    except Exception as e:
        traceback.print_exc()
        verifier(False, f"{nom} exception : {e}")
    finally:
        await ctx.close()
        serveur.shutdown()


async def degrade(nav, en_base, reglage):
    nom = f"[0010 {'en base' if en_base else 'absente'}, réglage {'vrai' if reglage else 'faux'}, catalogue illisible au chargement]"
    print("──", nom, flush=True)
    serveur, base, monde, ctx, code, el = await creer_monde(nav, en_base, reglage)
    try:
        prof = await ouvrir_classe(monde, ctx, base, code, panne_catalogue=True)
        t = await prof.locator("main").text_content()
        archiver = await prof.get_by_role("button", name="Archiver la classe", include_hidden=True).count() > 0
        verifier(not archiver or en_base, f"{nom} pas de « Archiver la classe » sans 0010")
        verifier("déjà tous les trophées" not in t, f"{nom} jamais « déjà tous les trophées » pour un·e élève qui n'en a aucun")
        if archiver and not en_base:
            await prof.locator("summary", has_text="Réglages de la classe").click()
            await prof.get_by_role("button", name="Archiver la classe").click()
            await prof.wait_for_timeout(2500)
        bilan_api(nom, monde, [])
    except Exception as e:
        traceback.print_exc()
        verifier(False, f"{nom} exception : {e}")
    finally:
        await ctx.close()
        serveur.shutdown()


async def principal():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        for en_base in (False, True):
            for reglage in (False, True):
                await combinaison(nav, en_base, reglage)
        for en_base, reglage in ((False, False), (False, True), (True, True)):
            await degrade(nav, en_base, reglage)
        await nav.close()
    print(f"\n{len(ECHECS)} échec(s).")
    for e in ECHECS:
        print("   ", e)
    return 1 if ECHECS else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(principal()))
