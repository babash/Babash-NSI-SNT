#!/usr/bin/env python3
"""Contrôle du rendu (Gardien) : chaque page, à plusieurs largeurs, en clair et en obscur.

Usage :
  python3 -I .github/gardien/rendu.py URL_DE_BASE DOSSIER_SORTIE --racine DOSSIER_DU_SITE
                   [--polices DOSSIER_FONTSOURCE] [--largeurs 320,768,1440]
                   [--modes light,dark] [--fichiers] [--sans-captures]

Pour chaque page (accueil + rubriques de reglages.js ; avec --fichiers, aussi les pages
HTML déposées dans */fichiers/), relève :
  - les erreurs JavaScript (exceptions et console.error), à part des échecs réseau ;
  - les requêtes en échec (ressources externes injoignables depuis la session, etc.) ;
  - le bloc d'erreur « Une liste de ressources contient une erreur » (.alerte) ;
  - le nombre de ressources affichées (li.res) et le nombre attendu (ressources.js) ;
  - le débordement horizontal : défilement horizontal, ou éléments coupés au bord
    (body a overflow-x: hidden, donc un débordement ne se voit pas au défilement) ;
  - une capture pleine page (animations figées, mouvements réduits).
Écrit DOSSIER_SORTIE/resultats.json et les captures ; code de sortie 1 si un problème.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

MESURES = r"""() => {
  const de = document.documentElement, W = de.clientWidth;
  const ignore = e => e.closest('.evitement, .invisible, [aria-hidden="true"]');
  const coupe = e => {
    for (let p = e.parentElement; p && p !== document.body && p !== de; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX;
      if (o !== 'visible') return true;   // contenu rogné ou défilant dans son conteneur : voulu
    }
    return false;
  };
  const nom = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
    (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  const deborde = [];
  for (const e of document.body.querySelectorAll('*')) {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height || ignore(e)) continue;
    if (r.right > W + 1 || r.left < -1) {
      if (coupe(e)) continue;
      const p = e.parentElement, rp = p ? p.getBoundingClientRect() : null;
      if (rp && (rp.right > W + 1 || rp.left < -1) && !coupe(p) && p !== document.body) continue; // on garde le plus haut
      deborde.push({ element: nom(e), gauche: Math.round(r.left), droite: Math.round(r.right),
                     texte: (e.textContent || '').trim().slice(0, 60) });
    }
  }
  const alerte = document.querySelector('.alerte');
  return {
    titre: document.title,
    largeur_vue: W,
    largeur_contenu: Math.max(de.scrollWidth, document.body.scrollWidth),
    hauteur: Math.max(de.scrollHeight, document.body.scrollHeight),
    defilement_horizontal: de.scrollWidth > W + 1,
    deborde: deborde.slice(0, 15),
    nb_deborde: deborde.length,
    res: document.querySelectorAll('li.res').length,
    alerte: alerte ? alerte.innerText.trim().slice(0, 500) : null,
    cartes: [...document.querySelectorAll('.noeud-meta')].map(x => x.textContent.trim()),
    polices_ok: document.fonts ? [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.style) : []
  };
}"""


def controler(navigateur, base, page_id, chemin, largeur, mode, sortie, polices, captures):
    contexte = navigateur.new_context(viewport={"width": largeur, "height": 900}, color_scheme=mode,
                                      reduced_motion="reduce", device_scale_factor=1)
    commun.polices(contexte, polices)
    page = contexte.new_page()
    js, console_err, reseau = [], [], []
    page.on("pageerror", lambda e: js.append(str(e)[:300]))

    def sur_console(m):
        if m.type != "error":
            return
        t = m.text
        (reseau if "Failed to load resource" in t or "net::ERR_" in t else console_err).append(t[:300])

    page.on("console", sur_console)
    page.on("requestfailed", lambda r: reseau.append(r.url[:160] + " : " + (r.failure or "?")))
    page.on("response", lambda r: reseau.append("%s : HTTP %d" % (r.url[:160], r.status)) if r.status >= 400 else None)
    url = base.rstrip("/") + "/" + chemin
    res = {"page": page_id, "url": url, "largeur": largeur, "mode": mode}
    try:
        page.goto(url, wait_until="networkidle", timeout=45000)
    except Exception as e:  # la page a pu se charger malgré une ressource lente
        res["chargement"] = str(e)[:200]
    try:
        page.evaluate("() => document.fonts ? document.fonts.ready.then(() => 1) : 1")
    except Exception:
        pass
    page.wait_for_timeout(400)
    res.update(page.evaluate(MESURES))
    res["erreurs_js"] = js
    res["console_erreurs"] = console_err
    res["reseau_echecs"] = sorted(set(reseau))
    if captures:
        nom = "%s-%d-%s.png" % (page_id.replace("/", "_"), largeur, mode)
        chemin_capture = os.path.join(sortie, nom)
        try:
            if res["hauteur"] > 15000:
                page.screenshot(path=chemin_capture, clip={"x": 0, "y": 0, "width": largeur, "height": 15000},
                                animations="disabled", full_page=True)
                res["capture_tronquee"] = True
            else:
                page.screenshot(path=chemin_capture, full_page=True, animations="disabled")
            res["capture"] = nom
        except Exception as e:
            res["capture_erreur"] = str(e)[:200]
    contexte.close()
    return res


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("base")
    a.add_argument("sortie")
    a.add_argument("--racine", required=True)
    a.add_argument("--polices")
    a.add_argument("--largeurs", default="320,768,1440")
    a.add_argument("--modes", default="light,dark")
    a.add_argument("--fichiers", action="store_true")
    a.add_argument("--sans-captures", action="store_true")
    o = a.parse_args()
    os.makedirs(o.sortie, exist_ok=True)
    largeurs = [int(x) for x in o.largeurs.split(",")]
    modes = o.modes.split(",")
    pages = commun.pages_site(o.racine)
    attendus = {r: commun.attendu(o.racine, r) for r in commun.rubriques(o.racine)}
    if o.fichiers:
        pages += commun.pages_fichiers(o.racine)
    resultats, problemes = [], []
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for page_id, chemin in pages:
            for w in largeurs:
                for m in modes:
                    r = controler(nav, o.base, page_id, chemin, w, m, o.sortie, o.polices, not o.sans_captures)
                    if page_id in attendus:
                        r["attendu"] = attendus[page_id]
                    resultats.append(r)
                    etiquette = "%s %d %s" % (page_id, w, m)
                    if r["erreurs_js"] or r["console_erreurs"]:
                        problemes.append(etiquette + " : erreur JavaScript " + "; ".join(r["erreurs_js"] + r["console_erreurs"])[:300])
                    if r["alerte"]:
                        problemes.append(etiquette + " : la page affiche une erreur : " + r["alerte"][:200])
                    if "attendu" in r and r["res"] != r["attendu"]:
                        problemes.append("%s : %d ressources affichées au lieu de %d" % (etiquette, r["res"], r["attendu"]))
                    if r["defilement_horizontal"] or r["nb_deborde"]:
                        problemes.append("%s : débordement horizontal (%s)" % (etiquette, ", ".join(d["element"] for d in r["deborde"][:4]) or "défilement"))
                    print("%-48s res=%-4s js=%d console=%d reseau=%d deborde=%d%s" % (
                        etiquette, r["res"], len(r["erreurs_js"]), len(r["console_erreurs"]),
                        len(r["reseau_echecs"]), r["nb_deborde"] + int(r["defilement_horizontal"]),
                        " ALERTE" if r["alerte"] else ""))
        nav.close()
    with open(os.path.join(o.sortie, "resultats.json"), "w", encoding="utf-8") as f:
        json.dump({"base": o.base, "resultats": resultats, "problemes": problemes}, f, ensure_ascii=False, indent=1)
    print("\n%d contrôles, %d problème(s)" % (len(resultats), len(problemes)))
    for pb in problemes:
        print(" -", pb)
    sys.exit(1 if problemes else 0)


if __name__ == "__main__":
    main()
