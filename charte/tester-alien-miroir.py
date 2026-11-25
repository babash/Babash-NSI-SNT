"""Alien Python : le miroir coloré de l'éditeur reste sous le texte tapé (T137).

Usage (depuis la racine du dépôt) : python3 -I -B charte/tester-alien-miroir.py
Lance un serveur local, ouvre l'éditeur d'une série inversée dans Chromium avec
les barres de défilement CLASSIQUES (celles des PC du lycée, pas les barres
superposées), puis, de 320 à 1440 px et de 100 à 300 % de zoom :
  1. tape une ligne plus longue que le champ, caractère par caractère ;
  2. colle un long texte (30 lignes longues) ;
  3. fait défiler le champ jusqu'au bout (à droite et en bas), puis au milieu ;
  4. (T145) écrit avec l'éditeur : Entrée après « : », Tab, Maj+Tab, une proposition de
     l'autocomplétion, et surligne une ligne (erreur, ligne exécutée).
À chaque étape, la position de caractères visibles dans le miroir est comparée
à leur position dans le champ (calculée d'après la police, les marges et le
défilement du champ) : l'écart doit rester d'un pixel au plus.
Aucun appel réseau hors de localhost (tout autre appel est refusé).
"""
import functools, http.server, os, sys, threading
from playwright.sync_api import sync_playwright

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOLERANCE = 1.0

MESURE = r"""() => {
  const t = document.getElementById('txt'), p = t.previousElementSibling;
  const cs = getComputedStyle(t), r = t.getBoundingClientRect();
  const cv = document.createElement('canvas').getContext('2d');
  cv.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
  const cw = cv.measureText('M').width, lh = parseFloat(cs.lineHeight);
  const x0 = r.left + t.clientLeft + parseFloat(cs.paddingLeft) - t.scrollLeft;
  const y0 = r.top + t.clientTop + parseFloat(cs.paddingTop) - t.scrollTop;
  const vis = { l: r.left + t.clientLeft, r: r.left + t.clientLeft + t.clientWidth, t: r.top + t.clientTop, b: r.top + t.clientTop + t.clientHeight };
  const lignes = p.querySelectorAll('.ligne'), src = t.value.split('\n');
  const ecarts = [];
  function noeud(li, col) {               // le nœud texte et la position du caractère « col » d'une ligne du miroir
    const w = document.createTreeWalker(li, NodeFilter.SHOW_TEXT); let n, k = 0;
    while ((n = w.nextNode())) {
      if (n.parentElement.closest('.num')) continue;
      if (col < k + n.length) return [n, col - k];
      k += n.length;
    }
    return null;
  }
  for (let i = 0; i < src.length; i++) {
    const yAttendu = y0 + i * lh;
    if (yAttendu + lh / 2 < vis.t || yAttendu + lh / 2 > vis.b) continue;   // au moins la moitié de la ligne est visible
    for (let c = 0; c < src[i].length; c++) {
      if (src[i][c] === ' ') continue;
      const xAttendu = x0 + c * cw;
      if (xAttendu + cw / 2 < vis.l || xAttendu + cw / 2 > vis.r) continue;
      const q = noeud(lignes[i], c); if (!q) { ecarts.push([i, c, 'absent']); continue; }
      const rg = document.createRange(); rg.setStart(q[0], q[1]); rg.setEnd(q[0], q[1] + 1);
      const b = rg.getBoundingClientRect();
      ecarts.push([i, c, b.left - xAttendu, b.top + (b.height - lh) / 2 - yAttendu]);
    }
  }
  return { dim: [t.clientWidth, t.clientHeight, t.scrollWidth, t.scrollHeight, cw, lh], barres: [t.offsetWidth - t.clientWidth, t.offsetHeight - t.clientHeight], defile: [t.scrollLeft, t.scrollTop], ecarts };
}"""


def serveur():
    class Muet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Muet, directory=RACINE)
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def main():
    s = serveur()
    url = "http://127.0.0.1:%d/snt/fichiers/alien-python/" % s.server_address[1]
    erreurs, cas, points, barres_vues = [], 0, 0, False
    longue = "droite(1)  # " + "le signal arrive de loin " * 4
    colle = "\n".join("    haut(%d)  # ligne collée numéro %d, assez longue pour dépasser le champ de tous les côtés" % (k % 9 + 1, k) for k in range(30))
    with sync_playwright() as p:
        nav = p.chromium.launch(ignore_default_args=["--hide-scrollbars"], args=["--disable-features=OverlayScrollbar,OverlayScrollbars,FluentOverlayScrollbar"])
        for largeur in (320, 768, 1440):
            for zoom in (1, 1.25, 1.5, 2, 3):
                ctx = nav.new_context(viewport={"width": max(160, round(largeur / zoom)), "height": round(900 / zoom)}, device_scale_factor=zoom)
                pg = ctx.new_page()
                pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith("http://127.0.0.1") else r.abort())
                pg.goto(url)
                pg.evaluate("() => { S = {c: 'X', k: '0', n: 'T'}; P = {}; open('B3'); }")
                pg.wait_for_selector("#txt")
                nom = "%d px, zoom %d %%" % (largeur, round(zoom * 100))

                def controle(etape, vide_permis=False):
                    nonlocal cas, points, barres_vues
                    pg.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                    m = pg.evaluate(MESURE)
                    cas += 1
                    if m["barres"][0] > 0 or m["barres"][1] > 0: barres_vues = True
                    vus = [e for e in m["ecarts"] if e[2] != 'absent']
                    points += len(vus)
                    if not vus and not vide_permis: erreurs.append("%s, %s : aucun caractère visible mesuré (barres %s, défilement %s, %s)" % (nom, etape, m["barres"], m["defile"], m.get("dim")))
                    for e in m["ecarts"]:
                        if e[2] == 'absent' or abs(e[2]) > TOLERANCE or abs(e[3]) > TOLERANCE:
                            erreurs.append("%s, %s : ligne %d, colonne %d : écart %s (barres %s, défilement %s)" % (nom, etape, e[0] + 1, e[1] + 1, e[2:], m["barres"], m["defile"]))
                            break
                pg.click("#txt")
                pg.keyboard.press("Control+End")
                pg.keyboard.type("\n" + longue)        # caractère par caractère
                controle("ligne longue tapée, curseur en bout de ligne")
                pg.keyboard.press("Control+End")
                pg.evaluate("t => { const e = document.getElementById('txt'); e.focus(); e.dispatchEvent(new ClipboardEvent('paste', {bubbles: true})); document.execCommand('insertText', false, t); }", "\n" + colle)
                controle("collage long")
                pg.evaluate("() => { const t = document.getElementById('txt'); t.scrollLeft = t.scrollWidth; t.scrollTop = t.scrollHeight; }")
                controle("défilement jusqu'au bout", vide_permis=True)   # au plus étroit, le bout des lignes du bas peut être vide
                pg.evaluate("() => { const t = document.getElementById('txt'); t.scrollLeft = t.scrollWidth; t.scrollTop = 9 * parseFloat(getComputedStyle(t).lineHeight) - 20; }")
                controle("défilement tout à droite, sur la ligne longue")
                pg.evaluate("() => { const t = document.getElementById('txt'); t.scrollLeft = Math.round(t.scrollWidth / 3); t.scrollTop = Math.round(t.scrollHeight / 2); }")
                controle("défilement au milieu")
                pg.keyboard.press("Control+Home")
                controle("retour au début")
                # T145 : ce que l'éditeur écrit lui-même (décalage automatique, Tab, Maj+Tab, autocomplétion)
                pg.evaluate("() => { const t = document.getElementById('txt'); t.focus(); t.select(); document.execCommand('insertText', false, EX.B3.c); t.scrollLeft = 0; t.scrollTop = 0; }")
                pg.keyboard.press("Control+End"); pg.keyboard.type("\nif a < 4 :\nhaut(2)")
                if not pg.input_value("#txt").endswith("\nif a < 4 :\n    haut(2)"): erreurs.append("%s : Entrée après « : » n'a pas décalé la ligne" % nom)
                controle("Entrée après « : » (décalage automatique)")
                pg.keyboard.press("Shift+Tab"); controle("Maj+Tab : la ligne recule")
                pg.keyboard.press("Tab"); pg.keyboard.press("Tab"); controle("Tab deux fois : la ligne avance")
                pg.keyboard.press("End"); pg.keyboard.press("Enter"); pg.keyboard.type("dr")
                if not pg.is_visible("#al-ac"): erreurs.append("%s : l'autocomplétion ne s'ouvre pas" % nom)
                controle("liste des propositions ouverte")
                pg.keyboard.press("Enter"); pg.keyboard.type("3")
                if not pg.input_value("#txt").endswith("droite(3)"): erreurs.append("%s : la proposition n'est pas écrite (%r)" % (nom, pg.input_value("#txt")[-12:]))
                controle("proposition choisie (droite())")
                pg.evaluate("() => { const L = document.querySelectorAll('.al-miroir .ligne'); L[2].classList.add('al-err'); L[4].classList.add('al-actif'); }")
                controle("lignes surlignées (erreur, ligne exécutée)")
                ctx.close()
        nav.close()
    s.shutdown()
    if not barres_vues:
        erreurs.append("les barres de défilement classiques n'ont pas été obtenues : l'essai ne prouve rien")
    print("%d situations, %d caractères comparés, tolérance %.0f px" % (cas, points, TOLERANCE))
    if erreurs:
        print("\n".join(erreurs[:40]))
        print("ÉCHEC : %d écart(s)" % len(erreurs))
        sys.exit(1)
    print("Tout est bon : le miroir reste sous le texte tapé.")


main()
