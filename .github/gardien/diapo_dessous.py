#!/usr/bin/env python3
"""Un élément fixe d'un diaporama reveal.js cache-t-il un contenu ou une commande ? (Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I .github/gardien/diapo_dessous.py DOSSIER PAGE.html --selecteur .pied-diaporama
         [--largeurs 320,375,768,1440] [--polices DOSSIER] [--cdn PREFIXE=DOSSIER …]

DOSSIER : le dossier servi ; PAGE.html : le diaporama, relatif à DOSSIER. reveal.js doit être
servi en local (--cdn, voir pages_depot.py ; par exemple
--cdn https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/=vendor/reveal/dist).
À chaque largeur, sur chaque diapositive (Reveal.next) :
  - le contenu des diapositives qui se trouve sous l'élément fixe (texte visible, relevé point par
    point avec elementsFromPoint) ;
  - les commandes de reveal.js : on compare les boîtes de l'élément et de chaque flèche
    (.controls button) et de la barre .progress, sans la zone cliquable invisible de son ::after.
    On compare les boîtes, car une flèche désactivée (pointer-events: none) reste visible mais
    elementsFromPoint ne la voit pas. L'écart minimal est donné pour chaque commande.
Code de sortie 1 si l'élément cache un contenu ou chevauche une commande visible, ou s'il est absent.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

HAUTEURS = {320: 640, 375: 667, 768: 1024, 1440: 900}

DESSOUS = r"""(sel) => {
  const b = document.querySelector(sel); if (!b) return { absent: true };
  const r = b.getBoundingClientRect(); const contenu = new Set();
  for (let x = r.left + 1; x < r.right; x += 4) for (let y = r.top + 1; y < r.bottom; y += 4) {
    for (const el of document.elementsFromPoint(x, y)) {
      if (b.contains(el) || el.closest('.controls, .progress, .slide-number')) continue;
      const sec = el.closest('.slides section');
      if (!sec || el.matches('section')) continue;
      const t = (el.innerText || '').trim(), s = getComputedStyle(el);
      if (t && s.visibility !== 'hidden' && s.opacity !== '0') contenu.add(el.tagName.toLowerCase() + ' « ' + t.slice(0, 40).replace(/\s+/g, ' ') + ' »');
    }
  }
  const boite = e => { const q = e.getBoundingClientRect(), s = getComputedStyle(e);
    return { x0: q.left, y0: q.top, x1: q.right, y1: q.bottom,
             visible: s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && q.width > 0 && q.height > 0 }; };
  const commandes = {};
  for (const e of document.querySelectorAll('.reveal .controls button'))
    commandes[(e.className.split(' ').find(c => c.startsWith('navigate-')) || e.className)] = boite(e);
  const p = document.querySelector('.reveal .progress'); if (p) commandes.progress = boite(p);
  return { element: { x0: r.left, y0: r.top, x1: r.right, y1: r.bottom }, contenu: [...contenu], commandes };
}"""


def chevauchement(a, b):
    return max(0, min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])) * max(0, min(a["y1"], b["y1"]) - max(a["y0"], b["y0"]))


def ecart(a, b):
    """Distance entre deux boîtes (négative si elles se chevauchent)."""
    return max(b["x0"] - a["x1"], a["x0"] - b["x1"], b["y0"] - a["y1"], a["y0"] - b["y1"])


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("dossier")
    a.add_argument("page")
    a.add_argument("--selecteur", required=True, help="sélecteur CSS de l'élément fixe (pied de page, pastille…)")
    a.add_argument("--largeurs", default="320,375,768,1440")
    a.add_argument("--polices", help="dossier des paquets fontsource décompressés")
    a.add_argument("--cdn", action="append", default=[], metavar="PREFIXE=DOSSIER")
    o = a.parse_args()
    cdn = commun.lire_cdn(o.cdn)
    serveur, base = commun.servir(os.path.abspath(o.dossier))
    problemes = 0
    with sync_playwright() as p:
        nav = commun.lancer(p)
        for largeur in [int(x) for x in o.largeurs.split(",") if x]:
            ctx = nav.new_context(viewport={"width": largeur, "height": HAUTEURS.get(largeur, 900)})
            commun.externes(ctx, cdn, None, o.polices)
            pg = ctx.new_page()
            pg.goto(base + "/" + o.page.lstrip("/"), wait_until="load")
            pg.wait_for_timeout(1200)
            if not pg.evaluate("() => typeof Reveal !== 'undefined' && !!Reveal.getTotalSlides"):
                raise SystemExit("reveal.js n'est pas chargé : vérifier --cdn")
            total = pg.evaluate("() => Reveal.getTotalSlides()")
            pg.evaluate("() => Reveal.slide(0, 0)")
            caches, ecarts, chevauchements, absent = [], {}, {}, False
            for i in range(total):
                if i:
                    pg.evaluate("() => Reveal.next()")
                pg.wait_for_timeout(450)
                m = pg.evaluate(DESSOUS, o.selecteur)
                if m.get("absent"):
                    absent = True
                    break
                indice = pg.evaluate("() => { const x = Reveal.getIndices(); return x.h + '.' + (x.v || 0); }")
                if m["contenu"]:
                    caches.append("diapositive %s : %s" % (indice, " ; ".join(m["contenu"][:4])))
                for nom, boite in m["commandes"].items():
                    if not boite["visible"]:
                        continue
                    ecarts[nom] = min(ecarts.get(nom, 1e9), ecart(m["element"], boite))
                    chevauchements[nom] = max(chevauchements.get(nom, 0), chevauchement(m["element"], boite))
            if absent:
                print("%4d px : élément « %s » absent" % (largeur, o.selecteur))
                problemes += 1
                ctx.close()
                continue
            touchees = [n for n, v in chevauchements.items() if v > 0]
            problemes += bool(caches) + bool(touchees)
            print("%4d px : %d diapositive(s) ; contenu caché : %s ; commandes chevauchées : %s" % (
                largeur, total, len(caches) or "aucun", ", ".join(touchees) or "aucune"))
            for c in caches[:8]:
                print("      " + c)
            for nom in sorted(ecarts):
                print("      %-16s écart minimal %6.1f px%s" % (nom, ecarts[nom], " (CHEVAUCHEMENT %.0f px²)" % chevauchements[nom] if chevauchements[nom] else ""))
            ctx.close()
        nav.close()
    serveur.shutdown()
    print("\n%d problème(s)" % problemes)
    sys.exit(1 if problemes else 0)


if __name__ == "__main__":
    main()
