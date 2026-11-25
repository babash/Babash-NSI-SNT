"""Ce qu'on voit est ce qu'on tape (T165) : contrôle des ligatures dans une page, avec Playwright.

Certaines polices de code (JetBrains Mono, celle du site ; Fira Code, Cascadia Code…) dessinent
`==`, `>=`, `<=`, `!=`, `=>`, `<>`, `//`, `--`, `__`, `</`… en un seul signe (≥, ≤, ≠, une flèche,
un long trait) : l'élève lit alors un autre code que celui qu'il ou elle doit taper.

Mesurer la largeur ne suffit pas : une police de code garde la largeur de chaque caractère, une
ligature comprise (`==` ligaturé est aussi large que deux `=`). On compare donc des images :
pour chaque style de texte de la page qui contient l'une de ces suites de caractères, on dessine
la même suite trois fois, au même endroit, avec la police et les réglages calculés de l'élément
(a), avec les ligatures coupées (b), puis allumées (c). Le défaut existe si (a) diffère de (b).
Si (b) et (c) sont identiques, la police n'a pas de ligature pour ce texte (rien à signaler).

Usage : from ligatures import controler ; defauts = controler(page, "#jeu", deja_vus)
"""

# les suites que JetBrains Mono dessine autrement avec ses ligatures (relevé du 25/11/2026, Chromium)
SEQUENCES = ["===", "!==", "==", "!=", ">=", "<=", "=>", "<>", "->", "<-", "//", "--", "__", "::", ":=",
             "&&", "||", "..", "++", "<<", ">>", "/*", "*/", "</", "/>", "##", "!!", "??", "|>", "<|", "/=", "#!", ";;"]

_STYLES = r"""([racine, sequences]) => {
  const vus = new Map();
  const base = document.querySelector(racine) || document.body;
  const marche = document.createTreeWalker(base, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = marche.nextNode())) {
    const t = n.nodeValue;
    const trouvees = sequences.filter(s => t.includes(s));
    if (!trouvees.length) continue;
    const el = n.parentElement;
    if (!el || el.closest("script, style, noscript, template, svg")) continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden") continue;
    const props = { fontFamily: cs.fontFamily, fontSize: cs.fontSize, fontWeight: cs.fontWeight, fontStyle: cs.fontStyle,
      fontStretch: cs.fontStretch, fontVariantLigatures: cs.fontVariantLigatures, fontFeatureSettings: cs.fontFeatureSettings,
      fontVariationSettings: cs.fontVariationSettings, fontKerning: cs.fontKerning, letterSpacing: cs.letterSpacing,
      textRendering: cs.textRendering };
    const cle = JSON.stringify(props);
    const ou = (el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/).join(".") : ""));
    const parent = el.parentElement ? (el.parentElement.tagName.toLowerCase() + (typeof el.parentElement.className === "string" && el.parentElement.className ? "." + el.parentElement.className.trim().split(/\s+/)[0] : "")) : "";
    if (!vus.has(cle)) vus.set(cle, { props, suites: new Set(), ou: parent + " > " + ou, exemple: t.trim().slice(0, 60) });
    trouvees.forEach(s => vus.get(cle).suites.add(s));
  }
  return [...vus.entries()].map(([cle, v]) => ({ cle, props: v.props, suites: [...v.suites], ou: v.ou, exemple: v.exemple }));
}"""

_DESSINER = r"""async ([props, texte, mode]) => {
  let s = document.getElementById("__sonde_ligatures__");
  if (!s) {
    s = document.createElement("div"); s.id = "__sonde_ligatures__";
    document.documentElement.appendChild(s);
  }
  s.style.cssText = "position:fixed;left:0;top:0;z-index:2147483647;margin:0;padding:6px;border:0;background:#fff;color:#000;" +
    "white-space:pre;line-height:1.4;text-shadow:none;text-decoration:none;opacity:1;transform:none;filter:none;";
  for (const k in props) s.style[k] = props[k];
  if (mode === "sans") { s.style.fontVariantLigatures = "none"; s.style.fontFeatureSettings = '"liga" 0, "clig" 0, "calt" 0, "dlig" 0'; s.style.letterSpacing = props.letterSpacing; }
  if (mode === "avec") { s.style.fontVariantLigatures = "normal"; s.style.fontFeatureSettings = '"liga" 1, "calt" 1'; s.style.letterSpacing = "normal"; }
  s.textContent = texte;
  try { await document.fonts.load(props.fontStyle + " " + props.fontWeight + " " + props.fontSize + " " + props.fontFamily, texte); } catch (e) {}
  await document.fonts.ready;
  const r = s.getBoundingClientRect();
  return { x: 0, y: 0, width: Math.max(1, Math.ceil(r.width)), height: Math.max(1, Math.ceil(r.height)) };
}"""


def styles(page, racine="body"):
    """Les styles de texte distincts de la page qui contiennent une suite à ligature."""
    return page.evaluate(_STYLES, [racine, SEQUENCES])


def ligature_active(page, props, suites):
    """(défaut, la police a-t-elle des ligatures pour ces suites) : on compare trois images."""
    texte = " ".join(suites)
    images = {}
    zone = None
    for mode in ("tel", "sans", "avec"):
        r = page.evaluate(_DESSINER, [props, texte, mode])
        zone = r if zone is None else {"x": 0, "y": 0, "width": max(zone["width"], r["width"]), "height": max(zone["height"], r["height"])}
    for mode in ("tel", "sans", "avec"):
        page.evaluate(_DESSINER, [props, texte, mode])
        images[mode] = page.screenshot(clip=zone, animations="disabled", caret="hide")
    page.evaluate("() => { const s = document.getElementById('__sonde_ligatures__'); if (s) s.remove(); }")
    return images["tel"] != images["sans"], images["avec"] != images["sans"]


def controler(page, racine="body", deja=None):
    """Renvoie la liste des défauts [{ou, exemple, suites, police}] ; `deja` (un dict) évite de
    redessiner un style déjà contrôlé (clé : les réglages calculés de la police)."""
    deja = {} if deja is None else deja
    defauts = []
    for st in styles(page, racine):
        if st["cle"] not in deja:
            deja[st["cle"]] = ligature_active(page, st["props"], st["suites"])[0]
        if deja[st["cle"]]:
            defauts.append({"ou": st["ou"], "exemple": st["exemple"], "suites": st["suites"], "police": st["props"]["fontFamily"].split(",")[0]})
    return defauts
