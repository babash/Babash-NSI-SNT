#!/usr/bin/env python3
"""Calendrier des vacances : ce que l'élève voit de chaque question sur un petit écran (T165).

Affiche chaque question de chaque banque (calendrier/exercices/*.json), seule, avec le vrai moteur
(calendrier/commun.js et jeux.js) dans Chromium, à la largeur demandée (320 px par défaut), à chaque
étape où du code se montre : la question ; les corrections d'une « erreur » ; les pièces de chaque trou
d'un « compléter » ; la fin (programme corrigé et affichage) ; puis le corrigé de l'exercice (J + 3).
Une question est « coupée » si un élément de la zone du jeu déborde de sa boîte (texte caché qu'il
faudrait faire glisser), sort de l'écran, ou si la page défile de côté. Les tables SQL (repliables,
qu'on fait glisser exprès) sont comptées à part.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/calendrier_affichage.py [--largeur 320] [--banques DOSSIER] [--site RACINE] [--json SORTIE]
Code de retour : 0 si toutes les questions sont entièrement visibles, 1 sinon (la liste est écrite).
Aucune requête ne sort de la machine.
"""
import argparse
import functools
import http.server
import json
import os
import sys
import threading

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNAIS = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mesure</title><link rel="stylesheet" href="../assets/signal-commun.css"><link rel="stylesheet" href="calendrier.css"></head>
<body><main class="page"><div id="jeu"></div></main><script src="config.js"></script><script src="commun.js"></script><script src="jeux.js"></script>
<script>
window.lancer = function (ex, niveau, langage, tables) {
  if (window.PARTIE) window.PARTIE.arreter();
  var vieux = document.getElementById("jeu"), neuf = document.createElement("div"); neuf.id = "jeu"; vieux.replaceWith(neuf);
  window.PARTIE = CV.jouer(document.getElementById("jeu"), { exercice: ex, niveau: niveau, langage: langage, tables: tables, titreCase: "essai",
    sauvegarde: null, surSauver: function () {}, surFin: function () {}, surQuitter: function () {} });
};
// ce qui est caché : un élément qui déborde de sa boîte, ou qui sort de l'écran
window.coupe = function () {
  var W = window.innerWidth, out = [];
  if (document.documentElement.scrollWidth > W + 1) out.push("la page défile de côté");
  document.querySelectorAll("#jeu *").forEach(function (el) {
    if (el.closest(".tables")) return;
    var r = el.getBoundingClientRect();
    if (!r.width && !r.height) return;
    var cs = getComputedStyle(el), nom = el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : "");
    if (/auto|scroll|hidden|clip/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 1) out.push(nom + " déborde de " + (el.scrollWidth - el.clientWidth) + " px");
    else if (r.right > W + 1 || r.left < -1) out.push(nom + " sort de l'écran");
  });
  return out.filter(function (x, i) { return out.indexOf(x) === i; });
};
</script></body></html>"""


def servir(racine):
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Silencieux, directory=racine))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d" % s.server_address[1]


MESURER = """([lots]) => {
  const res = [];
  const clic = (sel) => { const b = document.querySelector(sel); if (b) b.click(); };
  for (const lot of lots) {
    const ex = lot.ex;
    ex.niveaux.forEach((nv, n0) => nv.items.forEach((it, k0) => {
      const seul = JSON.parse(JSON.stringify(ex)), etapes = {};
      seul.niveaux[n0].items = [it];
      lancer(seul, n0 + 1, lot.langage, lot.tables);
      etapes.question = coupe();
      if (ex.type === "erreur") { clic("[data-j=ligne][data-i='" + it.ligne + "']"); etapes.corrections = coupe(); clic("[data-j=corr][data-k='" + it.bonne + "']"); etapes.fin = coupe(); }
      if (ex.type === "completer") {
        for (let d = 1; d < it.trous.length; d++) { clic("[data-j=trou][data-d='" + d + "']"); const c = coupe(); if (c.length) etapes["pièces " + (d + 1)] = c; }
        it.trous.forEach((t, d) => { clic("[data-j=trou][data-d='" + d + "']"); clic("[data-j=jeton][data-k='" + t.bonne + "']"); });
        clic("[data-j=verifier]"); etapes.fin = coupe();
      }
      if (ex.type === "ordre") { it.lignes.forEach((_, k) => { const s = document.getElementById("jeu").cvEtat().s; clic("[data-j=placer][data-i='" + s.reserve.indexOf(k) + "']"); }); clic("[data-j=verifier]"); etapes.fin = coupe(); }
      const c2 = JSON.parse(JSON.stringify(ex)); c2.niveaux = [{ items: [it] }];
      document.getElementById("jeu").innerHTML = CV.corrige(c2, lot.langage, null);
      etapes["corrigé"] = coupe();
      const trous = [];
      res.push({ banque: lot.banque, id: ex.id, type: ex.type, niveau: n0 + 1, question: k0 + 1, etapes });
    }));
  }
  return res;
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--largeur", type=int, default=320)
    ap.add_argument("--site", default=ICI)
    ap.add_argument("--banques")
    ap.add_argument("--json")
    a = ap.parse_args()
    dossier = a.banques or os.path.join(a.site, "calendrier", "exercices")
    lots = []
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".json") or nom.count(".") > 1 or nom in ("catalogue.json", "exercice.schema.json"):
            continue
        b = json.load(open(os.path.join(dossier, nom), encoding="utf-8"))
        ft = os.path.join(dossier, nom[:-5] + ".tables.json")
        tables = json.load(open(ft, encoding="utf-8"))["tables"] if os.path.exists(ft) else None
        for ex in b["exercices"]:
            lots.append({"banque": nom[:-5], "ex": ex, "langage": b["theme"].get("langage", "python"), "tables": tables})
    url = servir(a.site)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": a.largeur, "height": 760})
        ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith(url) else r.abort())
        ctx.route(url + "/calendrier/__mesure__.html", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=HARNAIS))
        page = ctx.new_page()
        erreurs = []
        page.on("pageerror", lambda e: erreurs.append(str(e)))
        page.goto(url + "/calendrier/__mesure__.html")
        page.evaluate("document.fonts.load('15px \"JetBrains Mono\"')")
        page.evaluate("document.fonts.ready")
        res = []
        for i in range(0, len(lots), 20):
            res += page.evaluate(MESURER, [lots[i:i + 20]])
        nav.close()
    total = len(res)
    q_coupees = [r for r in res if r["etapes"]["question"]]
    toute = [r for r in res if any(v for v in r["etapes"].values())]
    par_banque = {}
    for r in res:
        pb = par_banque.setdefault(r["banque"], [0, 0, 0])
        pb[0] += 1
        pb[1] += bool(r["etapes"]["question"])
        pb[2] += any(v for v in r["etapes"].values())
    print(f"{a.largeur} px : {total} questions ; coupées à l'écran de la question : {len(q_coupees)} ; "
          f"coupées à une étape au moins (corrections, pièces, fin, corrigé) : {len(toute)} ; erreurs JS : {len(erreurs)}")
    for b, (n, c1, c2) in sorted(par_banque.items()):
        print(f"  {b} : {c1} / {n} à la question, {c2} / {n} à une étape au moins")
    for r in toute[:40]:
        print("  -", r["id"], "N%d Q%d" % (r["niveau"], r["question"]), {k: v[:2] for k, v in r["etapes"].items() if v})
    if a.json:
        json.dump({"largeur": a.largeur, "questions": res, "erreurs_js": erreurs}, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return 1 if toute or erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
