#!/usr/bin/env python3
"""Réattribue en une fois les bandeaux de tous les TD du dépôt (T123b).

Usage (à la racine du dépôt) :
  python3 -I charte/reattribuer-bandeaux.py             montre ce qui changerait (rien n'est écrit)
  python3 -I charte/reattribuer-bandeaux.py --appliquer écrit les pages

Les TD convertis en parallèle sur plusieurs branches ont pris les mêmes bandeaux. Ce script les répartit
à parts égales : les pages sont rangées d'après l'empreinte de leur identifiant (SHA-256), puis reçoivent
1, 2, 3, 4, 1, 2… dans cet ordre (une répartition exacte, à une page près, et toujours la même pour le
même ensemble de pages). Les feuilles d'un même TD (même dossier) prennent des bandeaux différents quand
c'est possible, puisqu'elles se suivent. Le margouillat caché dans le bandeau garde sa cachette (b1 à b4)
et prend la place de cette cachette dans le nouveau dessin. Les contrôles (bandeau de 20 mm) aussi.

Collisions (T123c) : le margouillat ne tombe jamais sur le texte du bandeau (niveau et chapitre, titre,
accroche). Chaque page est rendue pour de vrai (Chromium, par Playwright) avec son nouveau bandeau, à 681,
768, 1024, 1440 et 1920 px et sur papier (A4), et l'étendue réelle du texte (Range.getClientRects) est
comparée à la boîte du margouillat. S'ils se touchent, le margouillat change de cachette : une autre des
quatre places du même bandeau (b1 à b4), la première libre dans l'ordre tiré de l'identifiant. Une page déjà
bien répartie est contrôlée aussi. Si aucune place ne convient, le script le dit (à régler à la main).
  --sans-mesure   ne rend pas les pages (répartition seule, comme avant T123c).

Seuls changent : data-bandeau, la cachette et le style du margouillat du bandeau, et le commentaire « paysage n° N ».
Les démonstrations de charte/ et les copies de .claude/ ne sont pas touchées.
"""
import functools
import hashlib
import http.server
import importlib.util
import json
import os
import re
import sys
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
spec = importlib.util.spec_from_file_location("nouveau_td", os.path.join(ICI, "nouveau-td.py"))
nt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nt)
RE_BD = re.compile(r'(class="td-bandeau[^"]*" data-bandeau=")([1-4])(")')


def pages():
    for dossier, sous, fichiers in os.walk(RACINE):
        if nt.ignorer(dossier):
            sous[:] = []
            continue
        for f in sorted(fichiers):
            if not f.endswith(".html"):
                continue
            chemin = os.path.join(dossier, f)
            try:
                t = open(chemin, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            i = re.search(r'data-td="([^"]+)"', t)
            if i and RE_BD.search(t) and "{{" not in t:
                yield chemin, i.group(1), t


# le margouillat touche-t-il le texte du bandeau ? (étendue réelle du texte, bornée à la boîte de son bloc)
COLLISION_JS = r"""() => {
  const bd = document.querySelector('.td-bandeau'), mg = bd && bd.querySelector('.td-margouillat');
  if (!mg || !mg.getClientRects().length) return [];
  const R = e => e.getBoundingClientRect(), m = R(mg), out = [];
  const croise = (a, b) => a.left < b.right - .5 && b.left < a.right - .5 && a.top < b.bottom - .5 && b.top < a.bottom - .5;
  const w = document.createTreeWalker(bd.querySelector('.td-bandeau-texte') || bd, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    const pe = R(n.parentElement.closest('h1, p, .td-sur-titre > *, .td-accroche') || n.parentElement);
    [...rg.getClientRects()].forEach(r0 => { if (r0.width < .5) return;
      const r = { left: r0.left, right: r0.right, top: Math.max(r0.top, pe.top), bottom: Math.min(r0.bottom, pe.bottom) };
      if (croise(r, m)) out.push(n.nodeValue.trim().slice(0, 24)); });
  }
  return [...new Set(out)];
}"""
VUES = (681, 768, 1024, 1440, 1920, 'A4')


class Mesureur:
    """Rend une page (texte donné) servie depuis le dépôt et dit où le margouillat touche le texte du bandeau."""

    def __init__(self):
        from playwright.sync_api import sync_playwright
        class Silencieux(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass
        gest = functools.partial(Silencieux, directory=RACINE)
        self.serveur = http.server.ThreadingHTTPServer(('127.0.0.1', 0), gest)
        threading.Thread(target=self.serveur.serve_forever, daemon=True).start()
        self.base = f'http://127.0.0.1:{self.serveur.server_address[1]}/'
        self.pw = sync_playwright().start()
        self.b = self.pw.chromium.launch()

    def collisions(self, rel, texte):
        url = self.base + rel.replace(os.sep, '/')
        vues = []
        for v in VUES:
            papier = v == 'A4'
            ctx = self.b.new_context(viewport={'width': 794 if papier else v, 'height': 1123 if papier else 900})
            ctx.route(url, lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=texte))
            ctx.route(re.compile(r'^https?://(?!127\.0\.0\.1)'), lambda r: r.abort())
            p = ctx.new_page()
            p.goto(url)
            p.wait_for_selector('.td-barre')
            p.evaluate('document.fonts.ready')
            if papier:
                p.evaluate("window.dispatchEvent(new Event('beforeprint'))")
                p.emulate_media(media='print')
                p.evaluate('document.fonts.ready')
            x = p.evaluate(COLLISION_JS)
            if x:
                vues.append(f'{v} : « {x[0]} »')
            ctx.close()
        return vues

    def fermer(self):
        self.b.close()
        self.pw.stop()
        self.serveur.shutdown()


def placer(u, b, k, places):
    """Met le margouillat du bandeau (s'il y est) à la cachette bk du bandeau b."""
    m = re.search(r'<span class="td-margouillat" data-cachette="b([1-4])" style="([^"]*)"', u)
    if not m:
        return u
    lieux = places[str(b)]
    p = lieux[min(k, len(lieux)) - 1]
    s = re.search(r"--s:(-?1)", m.group(2))
    style = f'--x:{p["x"]}%;--y:{p["y"]}%;--r:{p["r"]}deg;--l:{p["l"]}%;--s:{s.group(1) if s else 1}'
    return u[:m.start(1)] + str(k) + u[m.end(1):m.start(2)] + style + u[m.end(2):]


def main():
    appliquer = "--appliquer" in sys.argv
    mesurer = "--sans-mesure" not in sys.argv
    places = json.load(open(os.path.join(RACINE, "assets", "td", "places-margouillat.json"), encoding="utf-8"))
    liste = sorted(pages(), key=lambda x: hashlib.sha256(x[1].encode()).hexdigest())
    nouveau, compte, par_dossier = {}, {1: 0, 2: 0, 3: 0, 4: 0}, {}
    for chemin, ident, t in liste:
        dossier = os.path.dirname(chemin)
        pris = par_dossier.setdefault(dossier, set())
        # le moins utilisé, en évitant le bandeau d'une autre feuille du même dossier
        b = min((1, 2, 3, 4), key=lambda n: (n in pris, compte[n], n))
        compte[b] += 1
        pris.add(b)
        nouveau[chemin] = b
    mes = Mesureur() if mesurer else None
    changes, a_la_main = 0, []
    try:
        for chemin, ident, t in liste:
            b = nouveau[chemin]
            ancien = int(RE_BD.search(t).group(2))
            rel = os.path.relpath(chemin, RACINE)
            u = RE_BD.sub(lambda m: m.group(1) + str(b) + m.group(3), t, count=1)
            u = re.sub(r"paysage n° [1-4]", f"paysage n° {b}", u, count=1)
            # le margouillat caché dans le bandeau : même cachette, place du nouveau dessin
            m = re.search(r'<span class="td-margouillat" data-cachette="b([1-4])"', u)
            notes = []
            if m:
                k0 = int(m.group(1))
                u = placer(u, b, k0, places)
                if mes:
                    vues = mes.collisions(rel, u)
                    if vues:
                        # une autre place du même bandeau, dans l'ordre tiré de l'identifiant
                        h = int(hashlib.sha256(ident.encode()).hexdigest(), 16)
                        n = len(places[str(b)])
                        autres = [x for x in ((h + j) % n + 1 for j in range(n)) if x != k0]
                        trouve = None
                        for k in autres:
                            essai = placer(u, b, k, places)
                            if not mes.collisions(rel, essai):
                                trouve, u = k, essai
                                break
                        if trouve:
                            notes.append(f"margouillat b{k0} -> b{trouve} (il touchait le texte : {vues[0]})")
                        else:
                            notes.append(f"margouillat b{k0} : touche le texte à toutes les places ({vues[0]}) : à placer à la main")
                            a_la_main.append(rel)
            if u == t:
                continue
            changes += 1
            print(f"{rel} : bandeau {ancien} -> {b}" + ("".join(" ; " + x for x in notes)))
            if appliquer:
                open(chemin, "w", encoding="utf-8").write(u)
    finally:
        if mes:
            mes.fermer()
    print(f"{len(liste)} TD ; répartition : " + ", ".join(f"bandeau {n} : {compte[n]}" for n in (1, 2, 3, 4))
          + f" ; {changes} page(s) " + ("modifiée(s)" if appliquer else "à modifier (--appliquer pour écrire)")
          + ("" if mesurer else " ; collisions non mesurées (--sans-mesure)"))
    if a_la_main:
        print("Margouillat à placer à la main : " + ", ".join(a_la_main))


if __name__ == "__main__":
    main()
