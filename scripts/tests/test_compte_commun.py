#!/usr/bin/env python3
"""Tests des pages du compte commun en démonstration (T101b) : « Offrir un trophée » jusqu'au bout.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_compte_commun.py [--racine DOSSIER_DU_DEPOT] [--captures DOSSIER]

Le test sert le dépôt en local et joue, dans Chromium, à 320 px en obscur et à 1440 px en clair :
- l'enseignant·e de démonstration ouvre son espace et la classe « Seconde 4 (démo) » ;
- la liste des trophées à offrir à Nour ne contient aucun compagnon ;
- un motif de 2 caractères est refusé par la page ; le champ s'arrête à 80 caractères ; la fonction
  refuse 81 caractères et refuse d'offrir un compagnon ;
- l'offre avec un bon motif affiche un message de réussite, et le trophée apparaît, avec son motif,
  dans la fiche de Nour sur la même page ; il n'est plus proposé ensuite ;
- aucune erreur JavaScript.
La démonstration garde son état en mémoire pendant la visite, sans aucun stockage. reglages.js est servi
avec COMPTE_COMMUN_EN_LIGNE: false, et tout appel à Supabase est coupé (T132d).
Il faut Playwright et Chromium. Code de retour : 0 si tous les cas passent, 1 sinon.
"""
import argparse
import asyncio
import functools
import http.server
import os
import sys
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEFAUT = os.path.dirname(os.path.dirname(ICI))
CODE_DEMO = "DEMO-ESSAI-PROF-2046"
MOTIF = "Aide pour ranger les câbles <b>&</b>"  # un motif libre, affiché tel quel (jamais interprété)
COMPAGNONS = ("Margouillat vert", "Maki", "Petit robot", "Tortue serveur", "Roussette")


class Discret(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


async def scenario(navigateur, base, largeur, theme, captures, verifier):
    pg = await navigateur.new_page(viewport={"width": largeur, "height": 900}, color_scheme=theme)
    # La démonstration, quel que soit reglages.js (T132d : le site est en ligne) ; aucun appel à la base réelle
    with open(os.path.join(RACINE_DEFAUT, "reglages.js"), encoding="utf-8") as f:
        demo = f.read().replace("COMPTE_COMMUN_EN_LIGNE: true", "COMPTE_COMMUN_EN_LIGNE: false")
    await pg.route("**/reglages.js", lambda r: r.fulfill(status=200, body=demo, headers={"Content-Type": "application/javascript"}))
    await pg.route("https://*.supabase.co/**", lambda r: r.abort())
    erreurs = []
    pg.on("pageerror", lambda e: erreurs.append(str(e)))
    n = f"{largeur}-{theme}"
    await pg.goto(base + "/enseignant/")
    await pg.wait_for_selector(".cc-code-saisie")
    await pg.fill(".cc-code-saisie", CODE_DEMO)
    await pg.keyboard.press("Enter")
    await pg.click("text=Seconde 4 (démo)")
    await pg.wait_for_selector(".cc-eleve")

    def carte():
        return pg.locator(".cc-eleve", has=pg.locator(".cc-eleve-nom", has_text="Nour"))

    await carte().locator("summary", has_text="Offrir un trophée").click()
    options = await carte().locator("select[id^=trophee] option").all_inner_texts()
    verifier(len(options) > 0, f"{n} : des trophées sont proposés ({len(options)})")
    verifier(not any(c in options for c in COMPAGNONS), f"{n} : aucun compagnon proposé")
    choisi = options[0] if options else ""
    champ = carte().locator("input[placeholder='A rangé la salle informatique']")
    bouton = carte().locator("button:has-text('Offrir')")

    await champ.fill("ok")
    await bouton.click()
    await pg.wait_for_timeout(250)
    msg = await carte().locator(".cc-erreur").first.inner_text()
    verifier("3 à 80" in msg, f"{n} : motif de 2 caractères refusé (« {msg} »)")

    await champ.fill("x" * 81)
    verifier(len(await champ.input_value()) == 80, f"{n} : le champ du motif s'arrête à 80 caractères")
    element = await carte().locator("select[id^=trophee]").input_value()
    rep = await pg.evaluate("""async ([elt, motif]) => {
      const c = await CompteCommun.prof.classe('demo-classe-a');
      const nour = c.eleves.find(e => e.pseudo === 'Nour');
      return await CompteCommun.prof.offrir(nour.compte, elt, motif);
    }""", [element, "x" * 81])
    verifier(rep.get("ok") is False and "3 à 80" in rep.get("message", ""), f"{n} : motif de 81 caractères refusé par la fonction")
    rep = await pg.evaluate("""async () => {
      const c = await CompteCommun.prof.classe('demo-classe-a');
      const nour = c.eleves.find(e => e.pseudo === 'Nour');
      return await CompteCommun.prof.offrir(nour.compte, 'compagnon:maki', 'Un compagnon');
    }""")
    verifier(rep.get("ok") is False, f"{n} : un compagnon ne peut pas être offert")

    await champ.fill(MOTIF)
    await bouton.click()
    await pg.wait_for_timeout(500)
    ok = pg.locator("main .cc-message.cc-ok")
    verifier(await ok.count() == 1 and "trophée offert" in await ok.inner_text(), f"{n} : message de réussite affiché")
    liste = await carte().locator(".cc-trophees").inner_text() if await carte().locator(".cc-trophees").count() else ""
    verifier(choisi in liste and MOTIF in liste, f"{n} : « {choisi} » affiché avec son motif dans la fiche de Nour")
    await carte().locator("summary", has_text="Offrir un trophée").click()
    options2 = await carte().locator("select[id^=trophee] option").all_inner_texts()
    verifier(choisi not in options2, f"{n} : le trophée offert n'est plus proposé")
    verifier(not erreurs, f"{n} : aucune erreur JavaScript {erreurs}")
    if captures:
        await pg.screenshot(path=os.path.join(captures, f"ens-offrir-trophee-{n}.png"), full_page=True)
    await pg.close()


async def principal(racine, captures):
    from playwright.async_api import async_playwright
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Discret, directory=racine))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{serveur.server_address[1]}"
    echecs = []

    def verifier(cond, quoi):
        print(("OK     " if cond else "ÉCHEC  ") + quoi)
        if not cond:
            echecs.append(quoi)

    async with async_playwright() as p:
        b = await p.chromium.launch()
        for largeur, theme in ((320, "dark"), (1440, "light")):
            await scenario(b, base, largeur, theme, captures, verifier)
        await b.close()
    serveur.shutdown()
    print(f"\n{len(echecs)} échec(s).")
    return 1 if echecs else 0


def main():
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--racine", default=RACINE_DEFAUT)
    a.add_argument("--captures", default=None)
    args = a.parse_args()
    if args.captures:
        os.makedirs(args.captures, exist_ok=True)
    sys.exit(asyncio.run(principal(os.path.abspath(args.racine), args.captures)))


if __name__ == "__main__":
    main()
