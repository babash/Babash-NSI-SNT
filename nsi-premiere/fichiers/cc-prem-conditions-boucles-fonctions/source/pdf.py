"""Fabrique les PDF A4 des pages HTML (Chromium par Playwright), puis règle leurs métadonnées.

Usage : python3 pdf.py <dossier> <nom> [<nom> ...]   (nom sans .html)
Affiche, pour chaque page A4, la place libre avant le pied (en mm) : elle doit rester positive.
"""
import sys, asyncio
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter

AUTEUR = "Babash - NSI Tani Malandi"
LICENCE = "Licence CC BY-SA 4.0"


def metadonnees(chemin, titre):
    r = PdfReader(chemin)
    w = PdfWriter(clone_from=r)
    w.metadata = None
    w.add_metadata({"/Title": titre, "/Author": AUTEUR, "/Subject": LICENCE})
    with open(chemin, "wb") as f:
        w.write(f)


async def main(d, noms):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for n in noms:
            pg = await b.new_page(viewport={"width": 900, "height": 1250})
            await pg.goto(f"file://{d}/{n}.html")
            await pg.emulate_media(media="print")
            dep = await pg.evaluate("""() => [...document.querySelectorAll('.page')].map(p => {
                const ft = p.querySelector('footer'); const f = ft ? ft.getBoundingClientRect() : {top: p.getBoundingClientRect().bottom - 30};
                let m = 0; for (const e of p.children) if (e.tagName !== 'FOOTER') m = Math.max(m, e.getBoundingClientRect().bottom);
                return Math.round((f.top - m) / 3.78) })""")
            print(n, "place libre avant le pied (mm):", dep)
            titre = await pg.title()
            await pg.emulate_media(media=None)
            await pg.pdf(path=f"{d}/{n}.pdf", format="A4", print_background=True, prefer_css_page_size=True)
            await pg.close()
            metadonnees(f"{d}/{n}.pdf", titre)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2:]))
