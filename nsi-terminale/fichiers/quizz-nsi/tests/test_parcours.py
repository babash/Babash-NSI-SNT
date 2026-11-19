#!/usr/bin/env python3
"""QuizzNSI : parcours complets dans un vrai navigateur (Playwright, Chromium).

Lancement, depuis la racine de QuizzNSI :
    python3 -I tests/test_parcours.py [DOSSIER_DES_CAPTURES]

1. Une séance en classe avec un·e enseignant·e et deux élèves (Kobalt et Ixo, à 320 px),
   par le chemin « en ligne » de js/seance.js, mais avec un faux client temps réel
   (tests/faux-temps-reel.js) : aucune requête ne sort, la base n'est jamais appelée.
   On contrôle : le pseudo invisible refusé, le pseudo déjà pris refusé, le pseudo retiré par
   l'enseignant·e, les 20 questions, les points de chaque élève (recalculés ici d'après le barème),
   le podium et l'écran de fin.
1 bis. Injection : un·e élève malveillant·e qui connaît le code de séance envoie, pour chaque type de
   message et chaque champ, une valeur forgée (balise <img onerror>, nombre énorme, négatif, objet,
   chaîne très longue). Un piège sur innerHTML, outerHTML, insertAdjacentHTML, createContextualFragment
   et document.write échoue si une donnée venue du canal (marquée XSSMARK) y passe, même échappée :
   les deux élèves ont un pseudo qui contient XSSMARK, le podium est affiché après chaque question.
2. Le mode autonome : les 37 diapositives, une erreur puis la bonne réponse, le bilan.
3. La version imprimable : le sujet et le corrigé en PDF A4, sans débordement.
4. Toutes les pages à 320, 768 et 1440 px, en clair et en obscur : aucun défilement horizontal.
Aucune erreur JavaScript n'est tolérée ; toute requête vers un autre site est bloquée et signalée.
"""
import functools
import http.server
import json
import os
import sys
import threading

from playwright.sync_api import sync_playwright

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SORTIE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(RACINE, "tests", "captures")
os.makedirs(SORTIE, exist_ok=True)
with open(os.path.join(RACINE, "cours", "piles-files.json"), encoding="utf-8") as f:
    COURS = json.load(f)
QUESTIONS = [d for d in COURS["diapositives"] if d["type"] == "question"]
BONNES = [next(i for i, o in enumerate(q["options"]) if o.get("juste")) for q in QUESTIONS]
with open(os.path.join(RACINE, "tests", "faux-temps-reel.js"), encoding="utf-8") as f:
    FAUX = f.read()

erreurs, externes = [], []


def serveur():
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    gestion = functools.partial(Silencieux, directory=RACINE)
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}/"


def surveiller(page, nom):
    page.on("pageerror", lambda e: erreurs.append(f"{nom} : {e}"))
    page.on("console", lambda m: erreurs.append(f"{nom} (console) : {m.text}") if m.type == "error" else None)


def contexte(navigateur, base, **kw):
    ctx = navigateur.new_context(**kw)

    def route(r):
        url = r.request.url
        if url.endswith("/vendor/temps-reel.js"):
            return r.fulfill(status=200, content_type="text/javascript", body=FAUX)
        if not url.startswith(base) and not url.startswith("data:") and not url.startswith("blob:"):
            externes.append(url)
            return r.abort()
        return r.continue_()
    ctx.route("**/*", route)
    return ctx


MARQUE = "XSSMARK"
BALISE = '<img src=x onerror="window.__pwned=1">' + MARQUE
PIEGE = """
(() => {
  window.__piege = [];
  const M = 'XSSMARK', note = (ou, v) => { if (String(v).includes(M)) window.__piege.push(ou + ' : ' + String(v).slice(0, 80)); };
  for (const p of ['innerHTML', 'outerHTML']) {
    const d = Object.getOwnPropertyDescriptor(Element.prototype, p);
    Object.defineProperty(Element.prototype, p, { configurable: true, get() { return d.get.call(this); }, set(v) { note(p, v); d.set.call(this, v); } });
  }
  const iah = Element.prototype.insertAdjacentHTML;
  Element.prototype.insertAdjacentHTML = function (w, v) { note('insertAdjacentHTML', v); return iah.call(this, w, v); };
  const ccf = Range.prototype.createContextualFragment;
  Range.prototype.createContextualFragment = function (v) { note('createContextualFragment', v); return ccf.call(this, v); };
  const dw = Document.prototype.write;
  Document.prototype.write = function (...v) { note('document.write', v.join('')); return dw.apply(this, v); };
})();
"""


def forges(moi, autre):
    """Pour chaque type de message et chaque champ (imbriqué compris), des copies avec une valeur forgée."""
    import copy
    cle = {"x": "A" * 43, "y": "B" * 43}
    modeles = [
        {"t": "attente"},
        {"t": "notion", "cours": "piles-files", "n": 1},
        {"t": "question", "cours": "piles-files", "qid": "q01", "reste": 1000, "duree": 45, "ferme": False},
        {"t": "fermee", "qid": "q01"},
        {"t": "recus", "qid": "q01", "n": ["00112233aabbccdd"]},
        {"t": "retire", "id": moi},
        {"t": "refus", "id": moi, "raison": "pris"},
        {"t": "correction", "cours": "piles-files", "qid": "q01", "precedente": None, "bonne": 1, "rep": [1, 1, 0, 0],
         "bareme": {"participation": 10, "juste": 100, "rapidite": 20, "rebond": 30}, "duree": 0,
         "podium": [{"pseudo": "Kobalt", "total": 110, "place": 1}]},
        {"t": "fin", "cours": "piles-files", "podium": [{"pseudo": "Kobalt", "total": 110, "place": 1}]},
        {"t": "bonjour", "id": autre},
        {"t": "rep", "de": cle, "iv": "abcdefghijklmnop", "donnees": "QUJDRA"},
    ]
    valeurs = [BALISE, 10 ** 300, -1, 2.5, {"html": BALISE}, [BALISE], BALISE * 2000, True]

    def feuilles(o, base=()):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from feuilles(v, base + (k,))
        elif isinstance(o, list) and o:
            for i, v in enumerate(o):
                yield from feuilles(v, base + (i,))
        else:
            yield base
    for m in modeles:
        for ch in feuilles(m):
            if ch == ("t",):
                continue
            for v in valeurs:
                c = copy.deepcopy(m)
                x = c
                for k in ch[:-1]:
                    x = x[k]
                if isinstance(x[ch[-1]], bool) and isinstance(v, bool):
                    continue
                x[ch[-1]] = v
                yield c
        c = copy.deepcopy(m)
        c["html"] = BALISE
        yield c


def injection(nav, base):
    ctx = contexte(nav, base)
    ctx.add_init_script(PIEGE)
    prof = ctx.new_page()
    prof.set_viewport_size({"width": 1440, "height": 900})
    surveiller(prof, "injection enseignant·e")
    prof.goto(base + "animer.html?cours=piles-files")
    attendre_texte(prof, "#etatConnexion", "Séance ouverte")
    code = prof.inner_text("#code").strip()
    eleves = []
    for pseudo in ("Kobalt " + MARQUE, MARQUE):
        e = ctx.new_page()
        e.set_viewport_size({"width": 320, "height": 740})
        surveiller(e, "injection " + pseudo)
        e.goto(base + f"rejoindre.html?s={code}")
        e.fill("#champPseudo", pseudo)
        e.click("#rejoindre")
        eleves.append(e)
    attendre_texte(prof, "#eleves", "Kobalt " + MARQUE)
    prof.select_option("#duree", "0")
    prof.select_option("#podium", "chaque")
    prof.click("#commencer")
    prof.click("#action")  # notion 1
    prof.click("#action")  # question 1
    for e in eleves:
        e.wait_for_selector('button.option[data-choix="1"]:not([disabled])')
    moi = eleves[0].evaluate("() => JSON.parse(sessionStorage.getItem('quizz-nsi:eleve')).id")
    autre = eleves[1].evaluate("() => JSON.parse(sessionStorage.getItem('quizz-nsi:eleve')).id")
    attaque = ctx.new_page()
    attaque.goto(base + "index.html")
    liste = list(forges(moi, autre))
    attaque.evaluate("""([canal, msgs, balise, moi]) => {
        const bc = new BroadcastChannel('faux:' + canal);
        for (const m of msgs) bc.postMessage({ k: 'b', event: 'm', payload: m });
        // une présence forgée : pseudo piégé, identifiant piégé, clé en plus
        bc.postMessage({ k: 'p', cle: 'x1', info: { id: 'aaaaaaaaaaaaaaaa', pseudo: balise, role: 'eleve' } });
        bc.postMessage({ k: 'p', cle: 'x2', info: { id: balise, pseudo: 'Ixo', role: 'eleve' } });
        bc.postMessage({ k: 'p', cle: 'x3', info: { id: 'bbbbbbbbbbbbbbbb', pseudo: 'Ixo', role: 'eleve', html: balise } });
        bc.postMessage({ k: 'p', cle: 'x4', info: { id: 'cccccccccccccccc', pseudo: 'x'.repeat(100000), role: 'eleve' } });
    }""", ["quizz-nsi:" + code, liste, BALISE, moi])
    prof.wait_for_timeout(1500)
    # un espion écoute tout le canal pendant la suite de la séance
    espion = ctx.new_page()
    espion.goto(base + "index.html")
    espion.evaluate("canal => { window.__vus = []; const bc = new BroadcastChannel('faux:' + canal); bc.onmessage = ({ data }) => { if (data.k === 'b') window.__vus.push(data.payload); }; }", "quizz-nsi:" + code)
    # la séance continue normalement après l'attaque
    eleves[0].click('button.option[data-choix="1"]')
    eleves[1].click('button.option[data-choix="0"]')
    attendre_texte(prof, "#statutQ", "Tout le monde a répondu")
    prof.click("#action")
    prof.wait_for_selector("#podiumBoite[open]")
    attendre_texte(prof, "#podiumCorps", "Kobalt " + MARQUE)
    attendre_texte(eleves[0], ".q-num", "Question 1 sur 20 · correction")
    attendre_texte(eleves[0], "#points", "110 pts")
    fermer = "() => { const b = document.getElementById('podiumBoite'); if (b.open) b.close(); }"
    for _ in range(80):  # jusqu'à la fin, en fermant le podium affiché après chaque question
        prof.wait_for_timeout(120)
        if prof.inner_text("#action").startswith("Revoir"):
            break
        prof.evaluate(fermer)
        prof.click("#action")
    prof.wait_for_selector("#podiumBoite[open]")
    attendre_texte(eleves[1], "#ecran", "Fin de la séance")
    for nom, p in (("enseignant·e", prof), ("élève 1", eleves[0]), ("élève 2", eleves[1])):
        piege = p.evaluate("window.__piege")
        assert not piege, f"{nom} : une donnée du canal est passée par du HTML : {piege[:3]}"
        assert p.evaluate("window.__pwned") is None, f"{nom} : script exécuté"
        assert p.evaluate("document.querySelectorAll('img').length") == 0, f"{nom} : une image a été créée"
        assert "aaaaaaaaaaaaaaaa" not in p.content() and "<img" not in p.inner_html("body"), f"{nom} : élément forgé affiché"
    assert "Ixo" not in prof.inner_text("#eleves"), "présence forgée affichée"
    # ce que l'espion a vu : aucune réponse lisible, aucun résultat individuel
    vus = espion.evaluate("window.__vus")
    reps = [m for m in vus if m.get("t") == "rep"]
    assert len(reps) >= 2, "les réponses des deux élèves auraient dû passer (chiffrées)"
    for m in vus:
        texte = json.dumps(m)
        if m.get("t") in ("rep", "correction", "fin", "recus", "question"):
            assert moi not in texte and autre not in texte, f"identifiant d'élève diffusé : {texte[:120]}"
        if m.get("t") == "rep":
            assert set(m) == {"t", "de", "iv", "donnees"}, f"réponse en clair : {texte[:120]}"
        if m.get("t") in ("correction", "fin"):
            assert "res" not in m, "résultats individuels diffusés"
    print(f"  confidentialité : {len(vus)} messages écoutés, {len(reps)} réponses chiffrées, aucun résultat individuel")
    print(f"  injection : {len(liste)} messages forgés et 4 présences forgées ignorés ; aucun innerHTML ne reçoit de donnée du canal")
    ctx.close()


def points(juste, precedente):
    """Le barème de js/bareme.js, sans minuterie : +10 pour répondre, +100 si juste, +30 de rebond."""
    return 10 + (100 if juste else 0) + (30 if juste and precedente == "faux" else 0)


def attendre_texte(page, selecteur, texte, delai=8000):
    page.wait_for_function("([s, t]) => { const e = document.querySelector(s); return e && e.innerText.includes(t); }", arg=[selecteur, texte], timeout=delai)


def seance(nav, base):
    ctx = contexte(nav, base)
    prof = ctx.new_page()
    prof.set_viewport_size({"width": 1440, "height": 900})
    surveiller(prof, "enseignant·e")
    prof.goto(base + "animer.html?cours=piles-files")
    attendre_texte(prof, "#etatConnexion", "Séance ouverte")
    code = prof.inner_text("#code").strip()
    assert len(code) == 4, code
    journal = prof.evaluate("window.__fauxTempsReel")
    assert journal["clients"][0]["url"] == "wss://cukahpyqkljiddmimpyi.supabase.co/realtime/v1", journal
    assert journal["clients"][0]["apikey"].startswith("sb_publishable_"), "clé publishable attendue"

    def eleve(pseudo, largeur=320, theme="light"):
        p = ctx.new_page()
        p.set_viewport_size({"width": largeur, "height": 740})
        p.emulate_media(color_scheme=theme)
        surveiller(p, pseudo)
        p.goto(base + f"rejoindre.html?s={code}")
        p.fill("#champPseudo", pseudo)
        p.click("#rejoindre")
        return p

    # un pseudo avec un caractère invisible est refusé avant tout envoi
    p0 = ctx.new_page(); surveiller(p0, "invisible")
    p0.goto(base + f"rejoindre.html?s={code}")
    p0.fill("#champPseudo", "Ko" + chr(0x200B) + "balt")
    p0.click("#rejoindre")
    assert "invisible" in p0.inner_text("#erreurPseudo"), p0.inner_text("#erreurPseudo")
    p0.close()

    nadia = eleve("Kobalt", theme="light")
    ali = eleve("Ixo", theme="dark")
    intrus = eleve("Pseudo Bizarre")
    attendre_texte(prof, "#eleves", "Pseudo Bizarre")
    attendre_texte(prof, "#eleves", "Kobalt")
    attendre_texte(prof, "#eleves", "Ixo")
    prof.screenshot(path=os.path.join(SORTIE, "seance-accueil-1440.png"))
    # le même pseudo (à la casse et aux accents près) est refusé
    double = eleve("KOBALT")
    attendre_texte(double, "#erreurPseudo", "déjà pris")
    double.close()
    # l'enseignant·e retire un pseudo : l'élève doit en choisir un autre
    prof.click('#eleves li:has-text("Pseudo Bizarre") button.retirer')
    attendre_texte(intrus, "#erreurPseudo", "retiré")
    prof.wait_for_function("() => !document.querySelector('#eleves').innerText.includes('Pseudo Bizarre')")
    intrus.fill("#champPseudo", "Pseudo Bizarre")
    intrus.click("#rejoindre")
    attendre_texte(intrus, "#erreurPseudo", "retiré")  # le pseudo retiré reste refusé
    intrus.close()

    prof.select_option("#duree", "0")
    prof.click("#commencer")
    # Kobalt : une erreur sur 4, Ixo : toujours A (ses rebonds sont rares)
    choix_n = [BONNES[k] if k % 4 != 1 else (BONNES[k] + 1) % 4 for k in range(20)]
    choix_a = [0] * 20
    attendu = {"Kobalt": 0, "Ixo": 0}
    prec = {"Kobalt": None, "Ixo": None}
    k = 0
    for i, d in enumerate(COURS["diapositives"]):
        if i > 0:
            prof.click("#action")
        if d["type"] == "notion" and i == 1:
            attendre_texte(nadia, "#ecran", d["titre"])
            nadia.screenshot(path=os.path.join(SORTIE, "eleve-notion-320.png"), full_page=True)
        if d["type"] != "question":
            continue
        for page, nom, ch in ((nadia, "Kobalt", choix_n), (ali, "Ixo", choix_a)):
            page.wait_for_selector(f'section.d-question button.option[data-choix="{ch[k]}"]:not([disabled])', timeout=8000)
            attendre_texte(page, ".q-num", f"Question {k + 1} sur 20")
            if k == 2 and nom == "Kobalt":
                page.screenshot(path=os.path.join(SORTIE, "eleve-question-320.png"), full_page=True)
            page.click(f'button.option[data-choix="{ch[k]}"]')
            juste = ch[k] == BONNES[k]
            attendu[nom] += points(juste, prec[nom])
            prec[nom] = "juste" if juste else "faux"
        attendre_texte(prof, "#statutQ", "Tout le monde a répondu")
        attendre_texte(nadia, "#envoyee", "reçue")
        if k == 4:
            prof.screenshot(path=os.path.join(SORTIE, "seance-question-1440.png"))
        prof.click("#action")  # montrer la réponse
        for page, nom in ((nadia, "Kobalt"), (ali, "Ixo")):
            attendre_texte(page, ".q-num", f"Question {k + 1} sur 20 · correction")
            attendre_texte(page, "#points", f"{attendu[nom]} pts")
        if k == 4:
            prof.screenshot(path=os.path.join(SORTIE, "seance-correction-1440.png"), full_page=True)
            nadia.screenshot(path=os.path.join(SORTIE, "eleve-correction-320.png"), full_page=True)
            ali.screenshot(path=os.path.join(SORTIE, "eleve-correction-320-obscur.png"), full_page=True)
        k += 1
    assert k == 20
    prof.click("#action")  # terminer la séance
    prof.wait_for_selector("#podiumBoite[open]")
    attendre_texte(prof, "#podiumCorps", "Kobalt")
    prof.screenshot(path=os.path.join(SORTIE, "seance-podium-1440.png"))
    attendre_texte(nadia, "#ecran", "Fin de la séance")
    attendre_texte(nadia, "#ecran", f"{attendu['Kobalt']} points")
    attendre_texte(nadia, "#ecran", "1re place")
    nadia.screenshot(path=os.path.join(SORTIE, "eleve-fin-320.png"), full_page=True)
    assert nadia.evaluate("localStorage.getItem('quizz-nsi:eleve')") is None, "l'entrée « eleve » doit être effacée à la fin de la séance"
    attendre_texte(ali, "#ecran", f"{attendu['Ixo']} points")
    print(f"  séance : 20 questions, points Kobalt {attendu['Kobalt']}, Ixo {attendu['Ixo']}, envois {prof.evaluate('window.__fauxTempsReel.envois')}")
    ctx.close()


def stockage(nav, base):
    """L'entrée « eleve » (code, pseudo, identifiant) périmée est effacée au chargement de chaque page."""
    ctx = contexte(nav, base)
    p = ctx.new_page()
    surveiller(p, "stockage")
    for page in ("index.html", "revision.html", "animer.html", "rejoindre.html", "imprimer.html"):
        p.goto(base + "index.html")
        p.evaluate("() => localStorage.setItem('quizz-nsi:eleve', JSON.stringify({ id: '0123456789abcdef', pseudo: 'Ixo', code: 'ABCD', jusqua: Date.now() - 1000 }))")
        p.goto(base + page)
        p.wait_for_timeout(200)
        assert p.evaluate("localStorage.getItem('quizz-nsi:eleve')") is None, f"{page} : entrée périmée gardée"
    # une entrée valide est gardée, et préremplit la page élève
    p.evaluate("() => localStorage.setItem('quizz-nsi:eleve', JSON.stringify({ id: '0123456789abcdef', pseudo: 'Ixo', code: 'ABCD', jusqua: Date.now() + 3600000 }))")
    p.goto(base + "rejoindre.html")
    assert p.input_value("#champPseudo") == "Ixo"
    print("  stockage : entrée périmée effacée sur les 5 pages, entrée valide gardée")
    ctx.close()


def autonome(nav, base):
    ctx = contexte(nav, base)
    p = ctx.new_page()
    p.set_viewport_size({"width": 390, "height": 800})
    surveiller(p, "autonome")
    p.goto(base + "revision.html?cours=piles-files")
    p.wait_for_selector("section.d-titre")
    k = 0
    for i, d in enumerate(COURS["diapositives"]):
        if i > 0:
            p.click("#suiv")
        if d["type"] == "question":
            p.wait_for_selector(f'section.d-question[data-q="{k + 1}"]')
            if k == 0:  # une erreur d'abord : feedback, puis nouvel essai
                p.click(f'button.option[data-choix="{(BONNES[k] + 1) % 4}"]')
                attendre_texte(p, ".zone-correction", "Pas encore")
                p.screenshot(path=os.path.join(SORTIE, "autonome-erreur-390.png"), full_page=True)
            p.keyboard.press("abcd"[BONNES[k]])  # au clavier
            attendre_texte(p, ".zone-correction", "Bonne réponse")
            k += 1
    attendre_texte(p, "#scene", "19 sur 20")
    p.screenshot(path=os.path.join(SORTIE, "autonome-bilan-390.png"), full_page=True)
    p.reload()  # la progression reste sur l'appareil
    attendre_texte(p, "#scene", "19 sur 20")
    print("  autonome : 37 diapositives, bilan 19 sur 20 du premier coup")
    ctx.close()


def impression(nav, base):
    ctx = contexte(nav, base)
    p = ctx.new_page()
    surveiller(p, "impression")
    for nom, q in (("sujet", ""), ("corrige", "&corrige")):
        p.goto(base + "imprimer.html?cours=piles-files" + q)
        p.wait_for_selector(".f-question")
        p.emulate_media(media="print")
        p.set_viewport_size({"width": 702, "height": 1000})  # largeur utile d'une page A4 (186 mm)
        deborde = p.evaluate("""() => { const f = document.querySelector('.feuille').getBoundingClientRect();
            return [...document.querySelectorAll('.feuille *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.right > f.right + 1; }).map(e => e.tagName + '.' + e.className).slice(0, 5); }""")
        assert not deborde, f"{nom} déborde : {deborde}"
        chemin = os.path.join(SORTIE, f"imprimer-{nom}.pdf")
        p.pdf(path=chemin, format="A4", prefer_css_page_size=True, print_background=True)
        p.emulate_media(media="screen")
        print(f"  impression : {nom} sans débordement ({chemin})")
    ctx.close()


def rendus(nav, base):
    pages = ["index.html", "revision.html#7", "revision.html#30", "animer.html", "rejoindre.html", "imprimer.html", "imprimer.html?corrige"]
    for theme in ("light", "dark"):
        for largeur in (320, 768, 1440):
            ctx = contexte(nav, base, color_scheme=theme, viewport={"width": largeur, "height": 900})
            for adresse in pages:
                p = ctx.new_page()
                surveiller(p, f"{adresse} {largeur} {theme}")
                p.goto(base + adresse)
                p.wait_for_timeout(500)
                large = p.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
                assert large <= 0, f"{adresse} à {largeur} px ({theme}) : défilement horizontal de {large} px"
                nom = adresse.replace(".html", "").replace("#", "-").replace("?", "-")
                p.screenshot(path=os.path.join(SORTIE, f"rendu-{nom}-{largeur}-{theme}.png"), full_page=True)
                p.close()
            ctx.close()
    print("  rendus : 7 pages × 3 largeurs × 2 thèmes, sans défilement horizontal")


def main():
    s, base = serveur()
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        seance(nav, base)
        injection(nav, base)
        stockage(nav, base)
        autonome(nav, base)
        impression(nav, base)
        rendus(nav, base)
        nav.close()
    s.shutdown()
    if externes:
        print("Requêtes externes bloquées :", sorted(set(externes)))
    if erreurs:
        print("Erreurs JavaScript :", *erreurs, sep="\n  ")
    ok = not erreurs and not externes
    print("parcours : " + ("tout est conforme" if ok else "ÉCHEC") + f" ; captures dans {SORTIE}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
