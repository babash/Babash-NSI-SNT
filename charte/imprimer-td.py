#!/usr/bin/env python3
"""Fait le PDF de référence d'un TD en ligne : la feuille vierge, comme le papier.

Usage (serveur local lancé à la racine du dépôt : python3 -m http.server 8000) :
  python3 -I charte/imprimer-td.py http://localhost:8000/charte/td-pilote/index.html charte/td-pilote/td-boucles.pdf

  TD à plusieurs feuilles : toutes les adresses, dans l'ordre, puis le PDF.
  python3 -I charte/imprimer-td.py http://…/td-for.html http://…/td-for-2.html http://…/td-for-3.html td-for.pdf
  Chaque feuille est contrôlée seule (et doit tenir dans son nombre de pages), puis le PDF est fait d'un seul
  tenant : les feuilles se suivent sans saut de page, la deuxième et les suivantes avec une bande de titre fine.

  Pages : 4 au plus par feuille ; une feuille peut en déclarer davantage avec data-pages-max sur <main>
  (exemple : 5 pour un exercice de bac de 6 points).

Les polices sont hébergées sur le site (assets/fonts/) : aucune option n'est nécessaire.
(L'ancienne option --polices, pour Google Fonts, est acceptée et ignorée.)

Le script :
1. ouvre la page sans aucun stockage (aucune réponse gardée) et vérifie que tous les champs sont vides ;
2. écrit un repère dans chaque champ et dans chaque éditeur, coche chaque case, remet par de vrais
   clics les lignes des questions « ordre » dans l'ordre de la solution, puis déclenche
   l'impression (événement beforeprint) : le moteur doit tout vider pour de bon ;
3. imprime en A4 et extrait le texte du PDF (pdftotext) : aucun repère, aucune sortie attendue,
   aucun coup de pouce, aucun retour et aucune correction ne doit s'y trouver, et les lignes
   des questions « ordre » doivent y être dans l'ordre mélangé de départ ;
4. après l'impression (afterprint), vérifie que les réponses (et l'ordre de l'élève) sont remises à l'écran ;
5. contrôle la mise en page A4 (style « Signal pirate », T123) : aucune requête hors du site (polices
   comprises), aucun texte imprimé sous 10 pt, aucune ligne de code coupée en deux (trop longue pour
   la page), rien qui déborde de la page, le bandeau et le pied présents, seules les polices du site
   dans le PDF (pdffonts), et tout ce que l'élève remplit (lignes, cases du code, cases à cocher,
   ronds, cadres) tracé d'un trait plein d'au moins 0,5 pt et de contraste 7:1 au moins.
Il dit le nombre de pages (4 au plus pour un TD).
"""
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

from playwright.sync_api import sync_playwright

REPERE = 'ZQXREPONSE'
# noms des polices du site tels que pdffonts les écrit
POLICES_DU_SITE = {'AtkinsonHyperlegible-Regular', 'AtkinsonHyperlegible-Bold', 'AtkinsonHyperlegible-Italic',
                   'JetBrainsMono-Regular', 'JetBrainsMono-Bold', 'JetBrainsMono-Italic', 'JetBrainsMono-BoldItalic',
                   'Anton-Regular', 'VT323-Regular', 'TDSymboles'}
# le bandeau : texte entier, rien de recouvert (le QR code, « Nom et prénom », les objectifs), hauteur en mm
BANDEAU_JS = r"""() => {
  const bd = document.querySelector('.td-bandeau'); if (!bd) return { bandeau_h: 0, bandeau_pb: [] };
  const pb = [], r = e => e.getBoundingClientRect(), mm = px => Math.round(px * 25.4 / 96 * 10) / 10;
  const croise = (a, b) => a.left < b.right - .5 && b.left < a.right - .5 && a.top < b.bottom - .5 && b.top < a.bottom - .5;
  const textes = [...bd.querySelectorAll('.td-sur-titre, h1, .td-accroche')];
  const qr = bd.querySelector('.td-qr'), rb = r(bd);
  textes.forEach(e => {
    const nom = e.className || e.tagName.toLowerCase();
    if (e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible') pb.push(nom + ' : texte coupé');
    if (qr && croise(r(e), r(qr))) pb.push(nom + ' : recouvre le QR code');
    if (r(e).bottom > rb.bottom + .5 || r(e).right > rb.right + .5) pb.push(nom + ' : sort du bandeau');
    [...e.children].forEach(c => { if (r(c).right > r(e).right + 1) pb.push(nom + ' : un mot dépasse'); });
  });
  document.querySelectorAll('.td-nom, .td-objectifs').forEach(e => { if (e.getClientRects().length && r(e).top < rb.bottom - .5) pb.push((e.className) + ' : recouvert par le bandeau'); });
  return { bandeau_h: mm(rb.height), bandeau_attendu: bd.classList.contains('td-controle') ? 20 : 28, bandeau_pb: pb };
}"""
# mesures faites en média « print », à la largeur d'une page A4 (794 px)
MESURES = r"""() => { const BANDEAU = (BANDEAU_SRC);
  const pt = px => Math.round(px * 72 / 96 * 10) / 10, vus = el => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
  const petit = [], coupees = [], deborde = [];
  document.querySelectorAll('.td *').forEach(el => {
    if (!vus(el)) return;
    const direct = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    // dans un SVG, la taille est en unités du dessin : on la multiplie par l'échelle réelle (viewBox, largeur)
    let echelle = 1;
    if (el instanceof SVGElement && el.getScreenCTM) { const m = el.getScreenCTM(); if (m) echelle = Math.hypot(m.a, m.b); }
    if (direct) { const t = parseFloat(getComputedStyle(el).fontSize) * echelle; if (t < 13.3) petit.push((el.className.baseVal !== undefined ? el.tagName : el.className) + ' ' + el.textContent.trim().slice(0, 20) + ' (' + pt(t) + ' pt)'); }
    const r = el.getBoundingClientRect();
    if (r.width && (r.right > 794.5 || r.left < -0.5)) deborde.push(el.tagName + '.' + el.className);
  });
  // seul le code doit tenir sur sa ligne ; une console ou un message d'erreur passe à la ligne
  document.querySelectorAll('.td pre.td-code .td-l').forEach(l => {
    if (!vus(l)) return;
    const h = parseFloat(getComputedStyle(l).lineHeight) || 20;
    if (l.getBoundingClientRect().height > h * 1.5) coupees.push(l.textContent.replace(/^[0-9]+/, '').trim().slice(0, 40));
  });
  // tout ce que l'élève remplit : un trait d'au moins 0,5 pt (0,67 px) et de contraste 7:1 au moins sur le papier blanc
  const lum = c => { const v = (c.match(/[\d.]+/g) || [255, 255, 255]).slice(0, 3).map(x => { x = x / 255; return x <= .03928 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; });
    return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
  const opaque = c => !/rgba\([^)]*,\s*0(\.0+)?\)/.test(c) && c !== 'transparent';
  const rapport = c => 1.05 / (lum(c) + .05);
  const saisies = [], faibles = [];
  document.querySelectorAll('.td input:not([type=hidden]), .td textarea:not(.td-ed-texte), .td-editeur, .td-nom span').forEach(el => {
    if (!vus(el) && !el.classList.contains('td-editeur')) return;
    if (!el.getClientRects().length) return;
    const cs = getComputedStyle(el), traits = [];
    for (const cote of ['Top', 'Right', 'Bottom', 'Left']) {
      const w = parseFloat(cs['border' + cote + 'Width']), st = cs['border' + cote + 'Style'], c = cs['border' + cote + 'Color'];
      if (w > 0 && st !== 'none' && st !== 'hidden' && opaque(c)) traits.push({ w, st, c });
    }
    // lignes d'écriture dessinées en fond (dégradé répété) : leur couleur et leur épaisseur
    const fond = cs.backgroundImage;
    if (fond && fond.includes('gradient')) {
      const cols = (fond.match(/rgba?\([^)]*\)/g) || []).filter(opaque);
      cols.forEach(c => traits.push({ w: 1.2, st: 'solid', c }));
    }
    const nom = (el.className || el.type || el.tagName) + '';
    saisies.push(nom);
    const bons = traits.filter(t => t.w >= 0.66 && t.st !== 'dotted' && rapport(t.c) >= 7);
    const mauvais = traits.filter(t => !(t.w >= 0.66 && t.st !== 'dotted' && rapport(t.c) >= 7));
    if (!bons.length || mauvais.length) faibles.push(nom + ' : ' + (traits.map(t => t.w.toFixed(2) + 'px ' + t.st + ' ' + t.c + ' (' + rapport(t.c).toFixed(1) + ':1)').join(' / ') || 'aucun trait'));
  });
  return { petit, coupees, deborde, saisies: saisies.length, faibles, bandeau: !!document.querySelector('.td-bandeau'), pied: !!document.querySelector('.td-pied .td-ia'), ...BANDEAU() };
}"""


def normal(t):
    return ' '.join(t.split())


def reunir(urls):
    """Une seule page HTML pour plusieurs feuilles : la première, puis le <main> des suivantes (classe td-suite)."""
    textes = [urllib.request.urlopen(u).read().decode('utf-8') for u in urls]
    mains = []
    for u, t in zip(urls[1:], textes[1:]):
        m = re.search(r'<main\b[^>]*>.*?</main>', t, re.S)
        if not m:
            sys.exit(f'{u} : pas de <main>')
        mains.append(m.group(0))
    def classe(main, ajout):
        return re.sub(r'<main\b([^>]*)class="([^"]*)"', lambda x: f'<main{x.group(1)}class="{x.group(2)} {ajout}"', main, count=1)
    premier = textes[0]
    pm = re.search(r'<main\b[^>]*>', premier)
    premier = premier[:pm.start()] + classe(pm.group(0), 'td-suite-avant') + premier[pm.end():]
    suites = [classe(x, 'td-suite' + (' td-suite-avant' if i < len(mains) - 1 else '')) for i, x in enumerate(mains)]
    fin = premier.rindex('</body>')
    return premier[:fin] + '\n'.join(suites) + '\n' + premier[fin:]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dossier = sys.argv[sys.argv.index('--polices') + 1] if '--polices' in sys.argv else None
    if dossier in args:
        args.remove(dossier)
    if len(args) < 2 or not args[-1].endswith('.pdf'):
        sys.exit(__doc__)
    urls, sortie = args[:-1], args[-1]
    total = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        if len(urls) == 1:
            erreurs, pages, maxi = controler(b, urls[0], sortie)
            if pages > maxi:
                erreurs.append(f'{pages} pages : cette feuille tient sur {maxi} pages au plus (data-pages-max)')
            total = erreurs
        else:
            dossier_tmp = tempfile.mkdtemp(prefix='imprimer-td-', dir=os.path.dirname(os.path.abspath(sortie)))
            for k, u in enumerate(urls):
                print(f'feuille {k + 1} : {u}')
                erreurs, pages, maxi = controler(b, u, os.path.join(dossier_tmp, f'feuille-{k + 1}.pdf'))
                if pages > maxi:
                    erreurs.append(f'feuille {k + 1} : {pages} pages, {maxi} au plus (data-pages-max)')
                total += erreurs
            for f in os.listdir(dossier_tmp):
                os.remove(os.path.join(dossier_tmp, f))
            os.rmdir(dossier_tmp)
            print(f'PDF réuni, d\'un seul tenant : {sortie}')
            erreurs, pages, maxi = controler(b, urls[0], sortie, html=reunir(urls))
            total += erreurs
        b.close()
    print('PDF vierge : ' + ('oui' if not total else 'NON'))
    sys.exit(1 if total else 0)


def controler(b, url, sortie, html=None):
    """Contrôle une page (ou les feuilles réunies, html) et écrit son PDF. Renvoie (erreurs, pages, pages au plus)."""
    erreurs = []
    if True:
        ctx = b.new_context(viewport={'width': 1440, 'height': 900})
        if html is not None:
            ctx.route(url, lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=html))
        externes = []
        p = ctx.new_page()
        p.on('request', lambda r: externes.append(r.url) if not r.url.startswith(('http://localhost', 'http://127.0.0.1', 'file:', 'data:')) else None)
        p.goto(url)
        p.wait_for_selector('.td-barre')
        p.evaluate('document.fonts.ready')
        ecran = p.evaluate(BANDEAU_JS)
        for x in ecran['bandeau_pb']:
            erreurs.append('bandeau, à l\'écran : ' + x)
        # (le code de départ d'un éditeur n'est pas une réponse)
        pleins = p.evaluate("[...document.querySelectorAll('.td input, .td textarea:not(.td-ed-texte)')].filter(c => c.type === 'radio' || c.type === 'checkbox' ? c.checked : c.value).length")
        if pleins:
            erreurs.append(f'{pleins} champ(s) déjà rempli(s) à l\'ouverture')
        # des repères partout, pour prouver que l'impression vide vraiment
        n = p.evaluate("""r => { let n = 0;
            document.querySelectorAll('.td input, .td textarea').forEach(c => {
              if (c.type === 'radio' || c.type === 'checkbox') c.checked = true; else { c.value = r + (n++); }
            }); return n; }""", REPERE)
        # les questions « ordre » : l'état n'est pas un champ. On les résout par de vrais clics
        # (flèches ▲ ▼), dans l'ordre de la solution lu dans la source de la page.
        solutions = p.evaluate("""async () => {
            const doc = new DOMParser().parseFromString(await (await fetch(location.href)).text(), 'text/html');
            const sol = {};
            doc.querySelectorAll('.td-q[data-type="ordre"]').forEach(s => {
              sol[s.id] = [...s.querySelectorAll('.td-lignes > li')].map(li => li.textContent.trim()); });
            return sol; }""")
        ordres = {}
        lire = lambda qid: [t.strip() for t in p.locator(f'#{qid} .td-ordre-code').all_inner_texts()]
        if html is not None:
            solutions = {}          # feuilles réunies : les « ordre » ont été contrôlées feuille par feuille (identifiants en double)
        for qid, sol in solutions.items():
            depart = lire(qid)
            for cible, ligne in enumerate(sol):
                pos = next(i for i, t in enumerate(lire(qid)) if t == ligne and i >= cible)
                while pos > cible:
                    p.locator(f'#{qid} .td-ordre-ligne').nth(pos).locator('button').first.click()
                    pos -= 1
            if lire(qid) != sol:
                erreurs.append(f'{qid} : les lignes n\'ont pas pu être remises dans l\'ordre de la solution')
            num = p.locator(f'#{qid} .td-q-num').inner_text().strip()
            ordres[qid] = (num, depart, sol)
        # textes qui ne doivent jamais être imprimés (pris avant que le moteur ne les déplace)
        caches = p.evaluate("""() => [...document.querySelectorAll('.td-aide, .td-correction, .td-retour, pre.td-attendu')]
            .map(e => e.innerText.trim()).filter(t => t.length > 12)""")
        p.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        restes = p.evaluate("[...document.querySelectorAll('.td input, .td textarea')].filter(c => c.type === 'radio' || c.type === 'checkbox' ? c.checked : c.value).length")
        if restes:
            erreurs.append(f'{restes} champ(s) non vidé(s) à l\'impression')
        p.emulate_media(media='print')
        # mise en page A4 : la largeur de la page (210 mm, marges latérales dans la page)
        p.set_viewport_size({'width': 794, 'height': 1123})
        p.evaluate('document.fonts.ready')
        mesures = p.evaluate(MESURES.replace('(BANDEAU_SRC)', BANDEAU_JS))
        maxi = p.evaluate("Math.max(...[...document.querySelectorAll('[data-td]')].map(m => +m.getAttribute('data-pages-max') || 4))")
        nb_feuilles = p.evaluate("document.querySelectorAll('[data-td]').length")
        p.pdf(path=sortie, format='A4', print_background=True, prefer_css_page_size=True)
        p.set_viewport_size({'width': 1440, 'height': 900})
        p.emulate_media(media='screen')
        p.evaluate("window.dispatchEvent(new Event('afterprint'))")
        remis = p.evaluate("r => [...document.querySelectorAll('.td input, .td textarea')].filter(c => (c.value || '').startsWith(r)).length", REPERE)
        if remis != n:
            erreurs.append(f'après l\'impression, {remis} réponse(s) remise(s) sur {n}')
        for qid, (num, depart, sol) in ordres.items():
            if lire(qid) != sol:
                erreurs.append(f'{qid} : après l\'impression, l\'ordre de l\'élève n\'est pas revenu à l\'écran')
        ctx.close()
    if externes:
        erreurs.append('requête hors du site : ' + ', '.join(sorted(set(externes))[:3]))
    if mesures['petit']:
        erreurs.append(f"texte sous 10 pt : {mesures['petit'][:4]}")
    if mesures['coupees']:
        erreurs.append(f"ligne(s) de code trop longue(s) pour la page : {mesures['coupees'][:4]}")
    if mesures['deborde']:
        erreurs.append(f"débordement hors de la page : {mesures['deborde'][:4]}")
    if mesures['faibles']:
        erreurs.append(f"élément à remplir peu visible sur papier (il faut un trait plein de 0,5 pt et 7:1) : {mesures['faibles'][:4]}")
    for x in mesures['bandeau_pb']:
        erreurs.append('bandeau, sur papier : ' + x)
    if mesures['bandeau_h'] > mesures['bandeau_attendu'] + .3:
        print(f"  Attention : bandeau de {mesures['bandeau_h']} mm au lieu de {mesures['bandeau_attendu']} : un texte du bandeau est trop long (titre, accroche ou chapitre ; voir LISEZMOI)")
    for nom in ('bandeau', 'pied'):
        if not mesures[nom]:
            erreurs.append(f'{nom} absent')
    polices_pdf = [l.split()[0] for l in subprocess.run(['pdffonts', sortie], capture_output=True, text=True).stdout.splitlines()[2:]]
    autres = sorted({f.split('+')[-1] for f in polices_pdf} - POLICES_DU_SITE)
    if autres:
        erreurs.append('police de remplacement dans le PDF : ' + ', '.join(autres))
    texte = subprocess.run(['pdftotext', '-layout', sortie, '-'], capture_output=True, text=True, check=True).stdout
    plat = normal(texte)
    if REPERE in texte:
        erreurs.append('une réponse tapée figure dans le PDF')
    for c in caches:
        debut = normal(c)[:40]
        if debut and debut in plat:
            erreurs.append('texte caché imprimé : ' + debut)
    # dans le PDF, les lignes de chaque question « ordre » sont dans l'ordre mélangé de départ
    for qid, (num, depart, sol) in ordres.items():
        debut = plat.find(num + ' ')
        suite = plat[debut:] if debut >= 0 else plat
        fin = suite.find('Question', len(num) + 1)
        bloc = suite[:fin] if fin > 0 else suite
        places = [bloc.find(normal(l)) for l in depart]
        if -1 in places:
            erreurs.append(f'{qid} : lignes introuvables dans le PDF')
        elif places != sorted(places):
            erreurs.append(f'{qid} : les lignes ne sont pas imprimées dans l\'ordre de départ')
        elif depart != sol:
            print(f'{qid} : imprimée dans l\'ordre de départ ({" / ".join(depart)}), pas dans celui de l\'élève')
    pages = int(next(l for l in subprocess.run(['pdfinfo', sortie], capture_output=True, text=True).stdout.splitlines()
                     if l.startswith('Pages:')).split()[1])
    print(f'{sortie} : {pages} page(s) A4 ; {n} champ(s) remplis puis vidés ; {len(caches)} texte(s) caché(s) contrôlé(s) ; '
          f"{mesures['saisies']} élément(s) à remplir au trait net")
    for e in erreurs:
        print('  -', e)
    return erreurs, pages, maxi * nb_feuilles


if __name__ == '__main__':
    main()
