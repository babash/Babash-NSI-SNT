#!/usr/bin/env python3
"""Fait le PDF de référence d'un TD en ligne : la feuille vierge, comme le papier.

Usage (serveur local lancé à la racine du dépôt : python3 -m http.server 8000) :
  python3 -I charte/imprimer-td.py http://localhost:8000/charte/td-pilote/index.html charte/td-pilote/td-boucles.pdf \
      [--polices DOSSIER]

--polices : un dossier contenant les paquets fontsource décompressés
(npm pack @fontsource/atkinson-hyperlegible @fontsource/chakra-petch @fontsource/jetbrains-mono),
pour avoir les polices du site quand Google Fonts n'est pas joignable.

Le script :
1. ouvre la page sans aucun stockage (aucune réponse gardée) et vérifie que tous les champs sont vides ;
2. écrit un repère dans chaque champ et dans chaque éditeur, coche chaque case, puis déclenche
   l'impression (événement beforeprint) : le moteur doit tout vider pour de bon ;
3. imprime en A4 et extrait le texte du PDF (pdftotext) : aucun repère, aucune sortie attendue,
   aucun coup de pouce, aucun retour et aucune correction ne doit s'y trouver ;
4. après l'impression (afterprint), vérifie que les réponses sont remises à l'écran.
Il dit le nombre de pages (4 au plus pour un TD).
"""
import glob
import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

REPERE = 'ZQXREPONSE'


def polices(ctx, dossier):
    familles = [('Atkinson Hyperlegible', 'atkinson-hyperlegible', [(400, 'normal'), (700, 'normal'), (400, 'italic')]),
                ('Chakra Petch', 'chakra-petch', [(500, 'normal'), (600, 'normal'), (700, 'normal')]),
                ('JetBrains Mono', 'jetbrains-mono', [(500, 'normal'), (700, 'normal'), (500, 'italic'), (700, 'italic')])]
    css = ''
    for nom, cle, styles in familles:
        for poids, style in styles:
            for sous in ('latin', 'latin-ext'):
                f = f'{cle}-{sous}-{poids}-{style}.woff2'
                if glob.glob(f'{dossier}/**/{f}', recursive=True):
                    css += (f"@font-face{{font-family:'{nom}';font-style:{style};font-weight:{poids};font-display:block;"
                            f"src:url(https://fonts.gstatic.com/local/{f}) format('woff2');}}\n")
    ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(status=200, content_type='text/css', body=css))

    def fichier(r):
        g = glob.glob(f'{dossier}/**/' + r.request.url.rsplit('/', 1)[-1], recursive=True)
        r.fulfill(status=200, content_type='font/woff2', body=open(g[0], 'rb').read()) if g else r.abort()
    ctx.route('https://fonts.gstatic.com/**', fichier)


def normal(t):
    return ' '.join(t.split())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dossier = sys.argv[sys.argv.index('--polices') + 1] if '--polices' in sys.argv else None
    if dossier in args:
        args.remove(dossier)
    url, sortie = args
    erreurs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={'width': 1440, 'height': 900})
        if dossier:
            polices(ctx, dossier)
        p = ctx.new_page()
        p.goto(url)
        p.wait_for_selector('.td-barre')
        p.evaluate('document.fonts.ready')
        # (le code de départ d'un éditeur n'est pas une réponse)
        pleins = p.evaluate("[...document.querySelectorAll('.td input, .td textarea:not(.td-ed-texte)')].filter(c => c.type === 'radio' || c.type === 'checkbox' ? c.checked : c.value).length")
        if pleins:
            erreurs.append(f'{pleins} champ(s) déjà rempli(s) à l\'ouverture')
        # des repères partout, pour prouver que l'impression vide vraiment
        n = p.evaluate("""r => { let n = 0;
            document.querySelectorAll('.td input, .td textarea').forEach(c => {
              if (c.type === 'radio' || c.type === 'checkbox') c.checked = true; else { c.value = r + (n++); }
            }); return n; }""", REPERE)
        # textes qui ne doivent jamais être imprimés (pris avant que le moteur ne les déplace)
        caches = p.evaluate("""() => [...document.querySelectorAll('.td-aide, .td-correction, .td-retour')]
            .map(e => e.innerText.trim()).filter(t => t.length > 12)""")
        p.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        restes = p.evaluate("[...document.querySelectorAll('.td input, .td textarea')].filter(c => c.type === 'radio' || c.type === 'checkbox' ? c.checked : c.value).length")
        if restes:
            erreurs.append(f'{restes} champ(s) non vidé(s) à l\'impression')
        p.emulate_media(media='print')
        p.pdf(path=sortie, format='A4', print_background=True, prefer_css_page_size=True)
        p.emulate_media(media='screen')
        p.evaluate("window.dispatchEvent(new Event('afterprint'))")
        remis = p.evaluate("r => [...document.querySelectorAll('.td input, .td textarea')].filter(c => (c.value || '').startsWith(r)).length", REPERE)
        if remis != n:
            erreurs.append(f'après l\'impression, {remis} réponse(s) remise(s) sur {n}')
        b.close()
    texte = subprocess.run(['pdftotext', '-layout', sortie, '-'], capture_output=True, text=True, check=True).stdout
    plat = normal(texte)
    if REPERE in texte:
        erreurs.append('une réponse tapée figure dans le PDF')
    for c in caches:
        debut = normal(c)[:40]
        if debut and debut in plat:
            erreurs.append('texte caché imprimé : ' + debut)
    pages = int(next(l for l in subprocess.run(['pdfinfo', sortie], capture_output=True, text=True).stdout.splitlines()
                     if l.startswith('Pages:')).split()[1])
    print(f'{sortie} : {pages} page(s) A4 ; {n} champ(s) remplis puis vidés ; {len(caches)} texte(s) caché(s) contrôlé(s)')
    if pages > 4:
        erreurs.append(f'{pages} pages : un TD tient sur 4 pages au plus')
    for e in erreurs:
        print('  -', e)
    print('PDF vierge : ' + ('oui' if not erreurs else 'NON'))
    sys.exit(1 if erreurs else 0)


if __name__ == '__main__':
    main()
