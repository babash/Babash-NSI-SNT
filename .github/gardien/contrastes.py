#!/usr/bin/env python3
"""Contrastes et navigation au clavier (Gardien).

Usage :
  python3 contrastes.py URL_DE_BASE DOSSIER_SORTIE --racine DOSSIER_DU_SITE
                        [--polices DOSSIER_FONTSOURCE] [--largeurs 320,1440] [--modes light,dark]
                        [--seuil 4.5] [--seuil-grand 3]

Contrastes : pour chaque texte visible, la couleur du texte est comparée aux pixels réellement
affichés derrière lui (capture de la page avec tous les textes rendus transparents), ce qui
tient compte des dégradés, du décor SVG et des voiles. On retient le fond le moins favorable
(10e centile). Seuils : 4,5:1 (texte), 3:1 (grand texte : 24 px, ou 18,66 px en gras).
Clavier : parcours à la touche Tab ; on relève le premier élément atteint (lien d'évitement),
les éléments atteints sans indicateur de focus visible, et le nombre d'arrêts.
Écrit DOSSIER_SORTIE/contrastes.json ; code de sortie 1 si un problème.
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

TEXTES = r"""() => {
  const out = [];
  const marche = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const vus = new Set();
  let n;
  while ((n = marche.nextNode())) {
    if (!n.nodeValue.trim()) continue;
    const e = n.parentElement;
    if (!e || vus.has(e)) continue;
    if (e.closest('script, style, noscript, svg, [aria-hidden="true"], .invisible')) continue;
    if (e.checkVisibility && !e.checkVisibility({ contentVisibilityAuto: true, opacityProperty: true, visibilityProperty: true })) continue;
    const ferme = e.closest('details:not([open])');
    if (ferme && !e.closest('summary')) continue;   // contenu d'un <details> fermé : non affiché
    const cs = getComputedStyle(e);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) continue;
    let op = 1;
    for (let p = e; p; p = p.parentElement) op *= parseFloat(getComputedStyle(p).opacity);
    if (op < 0.05) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const boites = [...r.getClientRects()].filter(b => b.width > 2 && b.height > 4)
      .map(b => ({ x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height }));
    if (!boites.length) continue;
    vus.add(e);
    const id = e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '');
    out.push({ element: id, texte: n.nodeValue.trim().slice(0, 50), couleur: cs.color,
               taille: parseFloat(cs.fontSize), gras: parseInt(cs.fontWeight) >= 700,
               opacite: op, boites: boites.slice(0, 3),
               fill: cs.webkitTextFillColor });
  }
  return out;
}"""

MASQUER = """
* { color: transparent !important; -webkit-text-fill-color: transparent !important;
    text-shadow: none !important; caret-color: transparent !important;
    text-decoration-color: transparent !important; }
*::before, *::after { color: transparent !important; text-decoration-color: transparent !important; }
input::placeholder, textarea::placeholder { color: transparent !important; }
"""

CLAVIER = r"""() => {
  const e = document.activeElement;
  if (!e || e === document.body) return null;
  const deja = e.hasAttribute('data-gardien-tab');
  if (!deja) e.setAttribute('data-gardien-tab', String(document.querySelectorAll('[data-gardien-tab]').length + 1));
  const cs = getComputedStyle(e);
  const r = e.getBoundingClientRect();
  const nom = e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  return { element: nom, texte: (e.innerText || e.value || e.getAttribute('aria-label') || e.getAttribute('title') || '').trim().slice(0, 40),
           contour: cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0,
           ombre: cs.boxShadow !== 'none',
           visible: r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth,
           deja: deja };
}"""

FOCALISABLES = r"""() => [...document.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]):not([type=hidden]), select, textarea, summary, [tabindex]:not([tabindex="-1"])')]
  .filter(e => e.checkVisibility ? e.checkVisibility({ visibilityProperty: true }) || e.classList.contains('evitement') : true).length"""


def rgba(c):
    c = c.strip()
    if c.startswith("rgba"):
        p = [float(x) for x in c[5:-1].split(",")]
        return p[0], p[1], p[2], p[3]
    if c.startswith("rgb"):
        p = [float(x) for x in c[4:-1].split(",")]
        return p[0], p[1], p[2], 1.0
    if c.startswith("color(srgb"):
        p = c[11:-1].replace("/", " ").split()
        v = [float(x) for x in p]
        return v[0] * 255, v[1] * 255, v[2] * 255, (v[3] if len(v) > 3 else 1.0)
    return 0, 0, 0, 1.0


def lum(r, g, b):
    def canal(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def ratio(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


def mesurer(page, image, seuil, seuil_grand):
    textes = page.evaluate(TEXTES)
    defauts, mesures = [], 0
    for t in textes:
        r, g, b, a = rgba(t["fill"] if t.get("fill") and "0, 0, 0, 0" not in t["fill"] else t["couleur"])
        a *= t["opacite"]
        pixels = []
        for bo in t["boites"]:
            x0, y0 = int(bo["x"]), int(bo["y"])
            x1, y1 = min(int(bo["x"] + bo["w"]), image.width), min(int(bo["y"] + bo["h"]), image.height)
            pas_x, pas_y = max(1, (x1 - x0) // 24), max(1, (y1 - y0) // 6)
            for y in range(max(0, y0), y1, pas_y):
                for x in range(max(0, x0), x1, pas_x):
                    pixels.append(image.getpixel((x, y))[:3])
        if not pixels:
            continue
        mesures += 1
        valeurs = []
        for (br, bg, bb) in pixels:
            fr, fg, fb = r * a + br * (1 - a), g * a + bg * (1 - a), b * a + bb * (1 - a)
            valeurs.append(ratio(lum(fr, fg, fb), lum(br, bg, bb)))
        valeurs.sort()
        pire = valeurs[len(valeurs) // 10]
        grand = t["taille"] >= 24 or (t["taille"] >= 18.66 and t["gras"])
        exige = seuil_grand if grand else seuil
        if pire < exige:
            defauts.append({"element": t["element"], "texte": t["texte"], "ratio": round(pire, 2),
                            "exige": exige, "taille": t["taille"], "couleur": t["couleur"]})
    return mesures, defauts


def clavier(page, maximum=400):
    """Parcours à la touche Tab sur une page fraîchement chargée (aucun clic avant)."""
    arrets, sans_focus, invisibles, premier = 0, [], [], None
    focalisables = page.evaluate(FOCALISABLES)
    for _ in range(maximum):
        page.keyboard.press("Tab")
        f = page.evaluate(CLAVIER)
        if not f or f["deja"]:
            break
        arrets += 1
        desc = f["element"] + " « " + f["texte"] + " »"
        if premier is None:
            premier = desc + ("" if f["visible"] else " (invisible quand il a le focus)")
        if not (f["contour"] or f["ombre"]):
            sans_focus.append(desc)
        if not f["visible"]:
            invisibles.append(desc)
    return {"arrets": arrets, "focalisables": focalisables, "premier": premier,
            "sans_indicateur": sans_focus[:20], "nb_sans_indicateur": len(sans_focus),
            "hors_ecran": invisibles[:10], "nb_hors_ecran": len(invisibles)}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("base")
    a.add_argument("sortie")
    a.add_argument("--racine", required=True)
    a.add_argument("--polices")
    a.add_argument("--largeurs", default="320,1440")
    a.add_argument("--modes", default="light,dark")
    a.add_argument("--seuil", type=float, default=4.5)
    a.add_argument("--seuil-grand", type=float, default=3.0)
    o = a.parse_args()
    os.makedirs(o.sortie, exist_ok=True)
    resultats, problemes = [], []
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for page_id, chemin in commun.pages_site(o.racine):
            for w in [int(x) for x in o.largeurs.split(",")]:
                for m in o.modes.split(","):
                    ctx = nav.new_context(viewport={"width": w, "height": 900}, color_scheme=m,
                                          reduced_motion="reduce", device_scale_factor=1)
                    commun.polices(ctx, o.polices)
                    page = ctx.new_page()
                    url = o.base.rstrip("/") + "/" + chemin

                    def charger():
                        page.goto(url, wait_until="networkidle", timeout=45000)
                        page.evaluate("() => document.fonts ? document.fonts.ready.then(() => 1) : 1")
                        page.wait_for_timeout(300)

                    charger()
                    clav = None
                    if w == max(int(x) for x in o.largeurs.split(",")):
                        clav = clavier(page)
                        charger()  # page neuve pour les contrastes (aucun focus, aucun défilement)
                    page.add_style_tag(content=MASQUER)
                    page.wait_for_timeout(150)
                    image = Image.open(io.BytesIO(page.screenshot(full_page=True, animations="disabled"))).convert("RGB")
                    page.evaluate("() => document.querySelectorAll('style').forEach(s => { if (s.textContent.includes('transparent !important')) s.remove(); })")
                    page.wait_for_timeout(100)
                    n, defauts = mesurer(page, image, o.seuil, o.seuil_grand)
                    r = {"page": page_id, "largeur": w, "mode": m, "textes_mesures": n, "defauts": defauts, "clavier": clav}
                    resultats.append(r)
                    et = "%s %d %s" % (page_id, w, m)
                    print("%-30s %4d textes, %d sous le seuil%s" % (et, n, len(defauts),
                          "" if not clav else " | clavier : %d arrêts / %d focalisables, 1er %s, %d sans indicateur, %d hors écran" % (
                              clav["arrets"], clav["focalisables"], clav["premier"], clav["nb_sans_indicateur"], clav["nb_hors_ecran"])))
                    for d in defauts[:6]:
                        print("     %.2f:1 (exigé %.1f) %s « %s » %s %.1fpx" % (d["ratio"], d["exige"], d["element"], d["texte"], d["couleur"], d["taille"]))
                    if defauts:
                        problemes.append("%s : %d texte(s) sous le seuil" % (et, len(defauts)))
                    if clav:
                        if clav["nb_sans_indicateur"]:
                            problemes.append("%s : %d élément(s) sans indicateur de focus : %s" % (et, clav["nb_sans_indicateur"], "; ".join(clav["sans_indicateur"][:3])))
                        if clav["nb_hors_ecran"]:
                            problemes.append("%s : %d élément(s) invisibles quand ils ont le focus : %s" % (et, clav["nb_hors_ecran"], "; ".join(clav["hors_ecran"][:3])))
                        if not (clav["premier"] or "").startswith("a.evitement"):
                            problemes.append("%s : le premier arrêt clavier n'est pas le lien d'évitement (%s)" % (et, clav["premier"]))
                        if clav["arrets"] < clav["focalisables"]:
                            problemes.append("%s : %d arrêts clavier pour %d éléments focalisables" % (et, clav["arrets"], clav["focalisables"]))
                    ctx.close()
        nav.close()
    with open(os.path.join(o.sortie, "contrastes.json"), "w", encoding="utf-8") as f:
        json.dump({"resultats": resultats, "problemes": problemes}, f, ensure_ascii=False, indent=1)
    print("\n%d problème(s)" % len(problemes))
    for pb in problemes:
        print(" -", pb)
    sys.exit(1 if problemes else 0)


if __name__ == "__main__":
    main()
