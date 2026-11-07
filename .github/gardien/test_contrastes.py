"""Test de la mesure de contraste sur une page témoin aux ratios connus."""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun  # noqa: E402
import contrastes  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

PAGE = """<!doctype html><html><body style="margin:0;background:#fff;font:16px sans-serif">
<p id="a" style="color:#999">gris 999 sur blanc (2,85:1)</p>
<p id="b" style="color:#767676">gris 767676 sur blanc (4,54:1)</p>
<p id="c" style="color:#fff;background:linear-gradient(90deg,#000,#888)">blanc sur dégradé noir vers gris</p>
<p id="d" style="color:#111;text-decoration:underline 3px #ff0">noir souligné jaune (19:1)</p>
<details><summary>résumé</summary><p style="color:#eee">caché dans un details fermé</p></details>
</body></html>"""

with sync_playwright() as p:
    nav = commun.lancer(p)
    page = nav.new_page(viewport={"width": 800, "height": 600})
    page.set_content(PAGE)
    page.add_style_tag(content=contrastes.MASQUER)
    image = Image.open(io.BytesIO(page.screenshot(full_page=True))).convert("RGB")
    page.evaluate("() => document.querySelectorAll('style').forEach(s => s.remove())")
    n, defauts = contrastes.mesurer(page, image, 4.5, 3.0)
    print(n, "textes mesurés")
    for d in defauts:
        print(" ", d["ratio"], d["texte"])
    nav.close()
