#!/usr/bin/env python3
"""Rendu avant/après des pages d'un autre dépôt, ou des pages déposées du site (Gardien).

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/pages_depot.py AVANT APRES SORTIE PAGE [PAGE …]
         [--depot https://github.com/propriétaire/nom] [--polices DOSSIER]
         [--cdn PREFIXE=DOSSIER …] [--tailwind-avant CSS] [--tailwind-apres CSS]
         [--largeurs 320,768,1440] [--modes light,dark] [--clavier 320,1440]
         [--attente 1500] [--preparer FICHIER.js] [--contrastes] [--impression]

AVANT et APRES : deux extractions du dépôt (git archive de main et de la branche, ou le dossier
que fabrique son build). PAGE : un chemin relatif à ces dossiers, avec sa requête s'il en faut
une (prof.html?demo). Pour chaque page, version, largeur et mode :
  - erreurs JavaScript et erreurs de la console, hors échecs de réseau ;
  - défilement horizontal réel de la fenêtre (il tient compte de la propriété CSS zoom) ;
  - avec --depot : le lien « Code source sur GitHub » : nombre, adresse, visible, rien par-dessus
    (au centre de chaque ligne du lien), dans l'écran en largeur ; contraste de sa couleur et de
    celle du texte qui l'entoure, sur les pixels autour du lien (le pire de la couleur la plus
    fréquente et des 10e et 90e centiles : un fond en dégradé ne trompe pas la mesure) ; atteint
    à la touche Tab (largeurs de --clavier, mode clair), avec un indicateur de focus ; sinon,
    l'élément où le focus reste bloqué (un éditeur de code qui garde la touche Tab, par exemple) ;
  - avec --contrastes : les textes sous 4,5:1 (3:1 pour le grand texte), mesurés comme
    contrastes.py, sur les pixels affichés ;
  - une capture pleine page, comparée entre avant et après (hauteurs, bandes de lignes qui
    diffèrent de plus de 8/255, distance au bas de la page).
Avec --impression, une fois par page et par version (A4, fonds compris, mode clair) : nombre de
pages, lien affiché ou masqué à l'impression, pages comparées une à une (pdftoppm, 60 ppp).
Seul ce qui est NOUVEAU après la branche est une alerte ; un défaut présent avant comme après est
« antérieur », listé à part. L'impression et la comparaison des captures sont des informations, à
juger. Code de sortie 1 s'il y a une alerte.

Les requêtes vers d'autres sites (commun.externes) : polices Google depuis des paquets fontsource
(--polices) ; bibliothèques des CDN depuis leurs paquets npm (--cdn PREFIXE=DOSSIER, autant que
nécessaire ; si un fichier manque, on essaie sans « .min ») ; Tailwind « Play CDN » remplacé par
la feuille compilée de chaque version (--tailwind-avant, --tailwind-apres) ; supabase-js remplacé
par un faux client (aucune donnée lue ni écrite) ; tout le reste est bloqué, et compté.
Préparer un paquet, par exemple :
  npm pack reveal.js@4.5.0
  mkdir -p vendor/reveal && tar -xzf reveal.js-4.5.0.tgz -C vendor/reveal --strip-components=1
  … --cdn https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/=vendor/reveal/dist
--preparer FICHIER.js : une fonction JavaScript « () => { … } », évaluée dans chaque page après le
chargement et avant les mesures (ouvrir un panneau, choisir un thème…).
Piège : un message passager (« toast ») peut recouvrir le pied pendant quelques secondes quand la
base est injoignable (elle l'est toujours ici) ; --attente 6000 mesure après lui.
Écrit SORTIE/resultats.json et les captures. Il faut Playwright, Pillow, Chrome ou Chromium, et
pdfinfo et pdftoppm (poppler) pour --impression.
"""
import argparse
import glob
import io
import json
import os
import re
import subprocess
import sys
from collections import Counter

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import commun  # noqa: E402
import contrastes  # noqa: E402
from PIL import Image, ImageChops  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

HAUTEURS = {320: 640, 768: 1024, 1440: 900}
VERSIONS = ("avant", "apres")

# Le lien « Code source sur GitHub » : le dernier visible est amené au milieu de l'écran, puis mesuré.
LIEN = r"""(texte) => {
  const norme = s => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const liens = [...document.querySelectorAll('a')].filter(a => norme(a.textContent) === norme(texte));
  const out = { n: liens.length, hrefs: liens.map(a => a.href) };
  const visibles = liens.filter(a => a.getClientRects().length && getComputedStyle(a).visibility !== 'hidden');
  out.visibles = visibles.length;
  if (!visibles.length) return out;
  const a = visibles[visibles.length - 1];
  a.scrollIntoView({ block: 'center', behavior: 'instant' });
  const r = a.getBoundingClientRect();
  const morceaux = [...a.getClientRects()].filter(q => q.width > 1);
  const recouvert = [];
  for (const q of morceaux) {
    const e = document.elementFromPoint(q.left + q.width / 2, q.top + q.height / 2);
    if (!(e && (e === a || a.contains(e) || e.contains(a))))
      recouvert.push(e ? e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : '') : 'hors de la fenêtre');
  }
  const cs = getComputedStyle(a);
  out.lien = { x: r.left, y: r.top, w: r.width, h: r.height, droite: r.right, vueL: innerWidth, vueH: innerHeight,
    lignes: morceaux.length, couleur: cs.color, couleurTexte: getComputedStyle(a.parentElement).color,
    souligne: cs.textDecorationLine.includes('underline'), recouvert };
  return out;
}"""

# Le focus après une pression sur Tab : est-ce le lien ? sinon, quel élément le tient ?
FOCUS = r"""(texte) => {
  const norme = s => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const e = document.activeElement;
  if (!e || e === document.body) return { lien: false, element: 'body', id: 'body' };
  if (!e.dataset.gardienFocus) e.dataset.gardienFocus = String(window.__gardienFocus = (window.__gardienFocus || 0) + 1);
  const nom = e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
    (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : '');
  if (e.tagName !== 'A' || norme(e.textContent) !== norme(texte)) return { lien: false, element: nom, id: e.dataset.gardienFocus };
  const s = getComputedStyle(e), r = e.getBoundingClientRect();
  return { lien: true, element: nom, id: e.dataset.gardienFocus,
           indicateur: (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || s.boxShadow !== 'none',
           dansVue: r.top >= 0 && r.bottom <= innerHeight && r.left >= 0 && r.right <= innerWidth };
}"""

DEFILEMENT = r"""() => { const x0 = scrollX, y0 = scrollY; scrollTo(1e6, y0); const d = scrollX; scrollTo(x0, y0); return d; }"""

LIEN_IMPRIME = r"""(texte) => {
  const norme = s => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
  return [...document.querySelectorAll('a')].some(a => norme(a.textContent) === norme(texte) &&
    a.getClientRects().length && getComputedStyle(a).visibility !== 'hidden');
}"""


def rgb(s):
    r, g, b, _ = contrastes.rgba(s)
    return round(r), round(g), round(b)


def ratio(a, b):
    return contrastes.ratio(contrastes.lum(*a), contrastes.lum(*b))


def contraste_lien(page, l):
    """(contraste du lien, contraste du texte voisin, fond retenu), sur le fond réel autour du lien.
    Les textes sont rendus transparents le temps d'une capture (contrastes.MASQUER) : il ne reste
    que le fond, sans les bords lissés des lettres. On retient le pire de la couleur la plus
    fréquente et des 10e et 90e centiles de luminance (un dégradé ne trompe pas la mesure)."""
    x0, y0 = max(0, int(l["x"]) - 4), max(0, int(l["y"]) - 4)
    x1, y1 = min(l["vueL"], int(l["x"] + l["w"]) + 4), min(l["vueH"], int(l["y"] + l["h"]) + 4)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None, None, None
    page.add_style_tag(content=contrastes.MASQUER)
    page.wait_for_timeout(120)
    im = Image.open(io.BytesIO(page.screenshot(clip={"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}))).convert("RGB")
    page.evaluate("() => document.querySelectorAll('style').forEach(s => { if (s.textContent.includes('transparent !important')) s.remove(); })")
    octets = im.tobytes()
    fond = [tuple(octets[i:i + 3]) for i in range(0, len(octets), 3)]
    lien, texte = rgb(l["couleur"]), rgb(l["couleurTexte"])
    tri = sorted(fond, key=lambda c: contrastes.lum(*c))
    candidats = [Counter(fond).most_common(1)[0][0], tri[len(tri) // 10], tri[(len(tri) * 9) // 10]]
    pire = min(candidats, key=lambda c: min(ratio(lien, c), ratio(texte, c)))
    return round(ratio(lien, pire), 2), round(ratio(texte, pire), 2), "#%02x%02x%02x" % pire


def clavier(page, texte, maxi=300):
    """Pressions sur Tab jusqu'au lien ; {arret, indicateur, dansVue} ou {arret: None, bloque: élément}.
    Le point de départ est le début de la page : le focus est mis sur le corps de la page (un simple
    blur() ne suffit pas, après les mesures du lien la première pression sortait de la page)."""
    page.evaluate("""() => { const b = document.body;
      if (document.activeElement && document.activeElement !== b) document.activeElement.blur();
      b.setAttribute('tabindex', '-1'); b.focus({ preventScroll: true }); b.removeAttribute('tabindex');
      window.scrollTo(0, 0); }""")
    derniers = []
    for i in range(1, maxi + 1):
        page.keyboard.press("Tab")
        f = page.evaluate(FOCUS, texte)
        if f["lien"]:
            return {"arret": i, "indicateur": f["indicateur"], "dansVue": f["dansVue"]}
        derniers.append(f["id"])
        if len(derniers) >= 15 and len(set(derniers[-15:])) == 1 and derniers[-1] != "body":
            return {"arret": None, "bloque": f["element"], "apres": i}   # le même élément, 15 fois de suite
    return {"arret": None, "bloque": None}


def masquer_et_mesurer(page, seuil, seuil_grand):
    page.add_style_tag(content=contrastes.MASQUER)
    page.wait_for_timeout(150)
    image = Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB")
    page.evaluate("() => document.querySelectorAll('style').forEach(s => { if (s.textContent.includes('transparent !important')) s.remove(); })")
    return contrastes.mesurer(page, image, seuil, seuil_grand)


def differences(a, b, tolerance=8):
    """Comparaison de deux images (chemins) : texte court, et les bandes de lignes qui diffèrent."""
    if not (os.path.exists(a) and os.path.exists(b)):
        return "capture absente", []
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if A.size[0] != B.size[0]:
        return "largeurs différentes (%d, %d)" % (A.size[0], B.size[0]), []
    h = min(A.size[1], B.size[1])
    r, g, bb = ImageChops.difference(A.crop((0, 0, A.size[0], h)), B.crop((0, 0, B.size[0], h))).split()
    d = ImageChops.lighter(ImageChops.lighter(r, g), bb).point(lambda v: 255 if v > tolerance else 0)
    boite = d.getbbox()
    if boite is None:
        return ("identique" if A.size[1] == B.size[1] else "hauteur %d -> %d, rien d'autre ne change" % (A.size[1], B.size[1])), []
    lignes = [y for y in range(boite[1], boite[3]) if d.crop((0, y, d.size[0], y + 1)).getbbox()]
    bandes = []
    for y in lignes:
        if bandes and y - bandes[-1][1] <= 3:
            bandes[-1][1] = y
        else:
            bandes.append([y, y])
    return "hauteur %d -> %d (%+d) ; 1re ligne différente %d, à %d px du bas de la page avant" % (
        A.size[1], B.size[1], B.size[1] - A.size[1], boite[1], A.size[1] - boite[1]), [tuple(x) for x in bandes]


def nom_fichier(*parties):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", "-".join(str(p) for p in parties))


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("avant", help="la version d'avant (extraction de main)")
    a.add_argument("apres", help="la version d'après (extraction de la branche)")
    a.add_argument("sortie", help="dossier des captures et de resultats.json")
    a.add_argument("pages", nargs="+", help="chemins des pages, relatifs aux deux dossiers")
    a.add_argument("--depot", help="adresse du dépôt attendue pour le lien « Code source sur GitHub »")
    a.add_argument("--texte-lien", default="Code source sur GitHub", help="texte du lien (défaut : %(default)s)")
    a.add_argument("--polices", help="dossier des paquets fontsource décompressés")
    a.add_argument("--cdn", action="append", default=[], metavar="PREFIXE=DOSSIER", help="un CDN servi depuis un paquet npm")
    a.add_argument("--tailwind-avant", help="feuille Tailwind compilée pour la version d'avant")
    a.add_argument("--tailwind-apres", help="feuille Tailwind compilée pour la version d'après")
    a.add_argument("--largeurs", default="320,768,1440")
    a.add_argument("--modes", default="light,dark")
    a.add_argument("--clavier", default="320,1440", help="largeurs du parcours au clavier, en mode clair ('' : aucun)")
    a.add_argument("--attente", type=int, default=1500, help="millisecondes d'attente après le chargement")
    a.add_argument("--preparer", help="fichier .js : une fonction évaluée dans chaque page avant les mesures")
    a.add_argument("--contrastes", action="store_true", help="mesurer aussi le contraste de tous les textes")
    a.add_argument("--impression", action="store_true", help="imprimer chaque page en A4, avant et après")
    a.add_argument("--seuil", type=float, default=4.5)
    a.add_argument("--seuil-grand", type=float, default=3.0)
    o = a.parse_args()
    racines = {"avant": os.path.abspath(o.avant), "apres": os.path.abspath(o.apres)}
    for v, d in racines.items():
        if not os.path.isdir(d):
            a.error("dossier introuvable (%s) : %s" % (v, d))
    os.makedirs(o.sortie, exist_ok=True)
    largeurs = [int(x) for x in o.largeurs.split(",") if x]
    modes = [x for x in o.modes.split(",") if x]
    au_clavier = {int(x) for x in o.clavier.split(",") if x}
    cdn = commun.lire_cdn(o.cdn)
    tailwind = {"avant": commun.lire(o.tailwind_avant) if o.tailwind_avant else None,
                "apres": commun.lire(o.tailwind_apres) if o.tailwind_apres else None}
    preparer = commun.lire(o.preparer) if o.preparer else None
    attendu = o.depot.rstrip("/") if o.depot else None
    mesures, impressions, bloquees = [], {}, {}
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for v in VERSIONS:
            serveur, base = commun.servir(racines[v])
            compte = Counter()
            for largeur in largeurs:
                for mode in modes:
                    ctx = nav.new_context(viewport={"width": largeur, "height": HAUTEURS.get(largeur, 900)},
                                          color_scheme=mode, device_scale_factor=1)
                    commun.externes(ctx, cdn, tailwind[v], o.polices, compte)
                    for chemin in o.pages:
                        pg = ctx.new_page()
                        js, console = [], []
                        pg.on("pageerror", lambda e, l=js: l.append(str(e).splitlines()[0][:200]))
                        pg.on("console", lambda m, l=console: l.append(m.text[:200]) if m.type == "error" else None)
                        r = {"page": chemin, "version": v, "largeur": largeur, "mode": mode}
                        try:
                            pg.goto(base + "/" + chemin.lstrip("/"), wait_until="load", timeout=45000)
                        except Exception as e:  # noqa: BLE001 - une page qui ne charge pas est un résultat
                            r["chargement"] = str(e).splitlines()[0][:200]
                        pg.wait_for_timeout(o.attente)
                        if preparer:
                            try:
                                pg.evaluate(preparer)
                                pg.wait_for_timeout(500)
                            except Exception as e:  # noqa: BLE001
                                js.append("--preparer : " + str(e).splitlines()[0][:160])
                        capture = os.path.join(o.sortie, nom_fichier(chemin, v, largeur, mode) + ".png")
                        pg.screenshot(path=capture, full_page=True)
                        r["capture"] = os.path.basename(capture)
                        r["defilement"] = pg.evaluate(DEFILEMENT)
                        if attendu:
                            m = pg.evaluate(LIEN, o.texte_lien)
                            pg.wait_for_timeout(300)
                            r.update({"liens": m["n"], "visibles": m["visibles"], "hrefs": m["hrefs"]})
                            l = m.get("lien")
                            if l:
                                c, ct, f = contraste_lien(pg, l)
                                r.update({"contraste": c, "contraste_texte": ct, "fond": f, "recouvert": l["recouvert"],
                                          "lignes": l["lignes"], "souligne": l["souligne"],
                                          "hors_largeur": l["x"] < 0 or l["droite"] > l["vueL"]})
                                if largeur in au_clavier and mode == "light":
                                    r["clavier"] = clavier(pg, o.texte_lien)
                        if o.contrastes:
                            pg.reload(wait_until="load")
                            pg.wait_for_timeout(o.attente)
                            if preparer:
                                try:
                                    pg.evaluate(preparer)
                                    pg.wait_for_timeout(500)
                                except Exception:  # noqa: BLE001 - déjà signalé plus haut
                                    pass
                            n, defauts = masquer_et_mesurer(pg, o.seuil, o.seuil_grand)
                            r["textes_mesures"], r["textes_sous_le_seuil"] = n, defauts
                        r["js"] = sorted(set(js))
                        r["console"] = sorted(set(c for c in console if "Failed to load resource" not in c and "net::ERR" not in c))
                        mesures.append(r)
                        pg.close()
                    ctx.close()
            if o.impression:
                ctx = nav.new_context(viewport={"width": 1240, "height": 1754}, color_scheme="light")
                commun.externes(ctx, cdn, tailwind[v], o.polices, compte)
                for chemin in o.pages:
                    pg = ctx.new_page()
                    pg.goto(base + "/" + chemin.lstrip("/"), wait_until="load", timeout=45000)
                    pg.wait_for_timeout(o.attente)
                    if preparer:
                        try:
                            pg.evaluate(preparer)
                        except Exception:  # noqa: BLE001
                            pass
                    pg.emulate_media(media="print")
                    imprime = pg.evaluate(LIEN_IMPRIME, o.texte_lien) if attendu else None
                    pdf = os.path.join(o.sortie, nom_fichier(chemin, v, "impression") + ".pdf")
                    pg.pdf(path=pdf, format="A4", print_background=True, prefer_css_page_size=True)
                    prefixe = pdf[:-4]
                    for vieux in glob.glob(prefixe + "-*.png"):
                        os.remove(vieux)
                    subprocess.run(["pdftoppm", "-r", "60", "-png", pdf, prefixe], check=True)
                    pages = sorted(glob.glob(prefixe + "-*.png"))
                    impressions[(chemin, v)] = {"pdf": os.path.basename(pdf), "pages": len(pages),
                                                "images": [os.path.basename(x) for x in pages], "lien_imprime": imprime}
                    pg.close()
                ctx.close()
            serveur.shutdown()
            bloquees[v] = dict(compte)
        nav.close()

    # ── Défauts de chaque mesure, puis ce qui est nouveau après la branche ──
    def defauts(r):
        d = {}
        if r.get("chargement"):
            d["chargement"] = "la page ne se charge pas : " + r["chargement"]
        for e in r["js"]:
            d["js:" + e] = "erreur JavaScript : " + e
        for e in r["console"]:
            d["console:" + e] = "erreur de la console : " + e
        if r["defilement"] > 0:
            d["defilement"] = "défilement horizontal de %d px" % r["defilement"]
        if attendu:
            if not r.get("liens"):
                d["lien"] = "pas de lien « %s »" % o.texte_lien
            elif not r.get("visibles"):
                d["lien"] = "lien « %s » présent mais invisible" % o.texte_lien
            mauvais = [h for h in r.get("hrefs", []) if h.rstrip("/") != attendu]
            if mauvais:
                d["adresse"] = "adresse du lien : " + ", ".join(mauvais)
            if r.get("contraste") is not None and r["contraste"] < o.seuil:
                d["contraste_lien"] = "contraste du lien %.2f:1 sur %s" % (r["contraste"], r["fond"])
            if r.get("contraste_texte") is not None and r["contraste_texte"] < o.seuil:
                d["contraste_texte"] = "contraste du texte voisin %.2f:1 sur %s" % (r["contraste_texte"], r["fond"])
            if r.get("recouvert"):
                d["recouvert"] = "lien recouvert par " + ", ".join(r["recouvert"])
            if r.get("hors_largeur"):
                d["hors_largeur"] = "lien hors de l'écran en largeur"
            k = r.get("clavier")
            if k is not None:
                if not k["arret"]:
                    d["clavier"] = "lien pas atteint au clavier" + (" : le focus reste sur %s" % k["bloque"] if k.get("bloque") else "")
                elif not k["indicateur"]:
                    d["focus"] = "lien sans indicateur de focus"
        for t in r.get("textes_sous_le_seuil", []):
            d["texte:%s:%s" % (t["element"], t["texte"])] = "texte à %.2f:1 (exigé %.1f) : %s « %s »" % (
                t["ratio"], t["exige"], t["element"], t["texte"])
        return d

    index = {(r["page"], r["version"], r["largeur"], r["mode"]): r for r in mesures}
    alertes = 0
    print("Mesures après la branche (comparées à celles d'avant) :")
    for r in mesures:
        if r["version"] != "apres":
            continue
        av = index.get((r["page"], "avant", r["largeur"], r["mode"]))
        d_ap, d_av = defauts(r), (defauts(av) if av else {})
        nouveaux = [m for k, m in d_ap.items() if k not in d_av]
        anciens = [m for k, m in d_ap.items() if k in d_av]
        r["alertes"], r["anterieurs"] = nouveaux, anciens
        alertes += bool(nouveaux)
        details = []
        if attendu and r.get("contraste") is not None:
            details.append("lien %.2f:1, texte %.2f:1" % (r["contraste"], r["contraste_texte"]))
        if attendu and r.get("clavier") and r["clavier"].get("arret"):
            details.append("Tab %d" % r["clavier"]["arret"])
        print("  %-40s %4d %-5s %s%s%s" % (r["page"][:40], r["largeur"], r["mode"],
              ("ALERTE " + " ; ".join(nouveaux)) if nouveaux else "ok",
              (" | antérieur : " + " ; ".join(anciens)) if anciens else "",
              (" [" + ", ".join(details) + "]") if details else ""))

    print("\nCaptures pleine page, avant -> après :")
    comparaisons = {}
    for chemin in o.pages:
        for largeur in largeurs:
            for mode in modes:
                av, ap = index.get((chemin, "avant", largeur, mode)), index.get((chemin, "apres", largeur, mode))
                if not (av and ap):
                    continue
                texte, bandes = differences(os.path.join(o.sortie, av["capture"]), os.path.join(o.sortie, ap["capture"]))
                comparaisons["%s %d %s" % (chemin, largeur, mode)] = {"resume": texte, "bandes": bandes}
                print("  %-40s %4d %-5s %s%s" % (chemin[:40], largeur, mode, texte,
                      (" ; bandes %s%s" % (bandes[:5], " …" if len(bandes) > 5 else "")) if bandes else ""))

    if o.impression:
        print("\nImpression A4 (information, à juger) :")
        for chemin in o.pages:
            av, ap = impressions.get((chemin, "avant")), impressions.get((chemin, "apres"))
            if not (av and ap):
                continue
            pages_diff = []
            for i, (x, y) in enumerate(zip(av["images"], ap["images"]), 1):
                texte, _ = differences(os.path.join(o.sortie, x), os.path.join(o.sortie, y))
                if texte != "identique":
                    pages_diff.append(str(i))
            lien = "" if ap["lien_imprime"] is None else (" ; lien imprimé : %s -> %s" % (
                "oui" if av["lien_imprime"] else "non", "oui" if ap["lien_imprime"] else "non"))
            print("  %-40s pages %d -> %d ; pages qui diffèrent : %s%s" % (
                chemin[:40], av["pages"], ap["pages"], ", ".join(pages_diff) or "aucune", lien))

    print("\nRequêtes vers d'autres sites, bloquées :", json.dumps(bloquees, ensure_ascii=False))
    with open(os.path.join(o.sortie, "resultats.json"), "w", encoding="utf-8") as f:
        json.dump({"mesures": mesures, "comparaisons": comparaisons,
                   "impressions": {"%s %s" % k: v for k, v in impressions.items()}, "bloquees": bloquees},
                  f, ensure_ascii=False, indent=1)
    n_apres = sum(1 for r in mesures if r["version"] == "apres")
    print("\n%d mesure(s) après, %d avec une alerte nouvelle" % (n_apres, alertes))
    sys.exit(1 if alertes else 0)


if __name__ == "__main__":
    main()
