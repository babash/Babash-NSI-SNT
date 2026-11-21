"""Maquette T126 : construit les cinq écrans à partir du vrai contenu du site.

Entrée : le HTML que assets/site.js produit sur origin/main (dom/*.html, capturé par dom.py),
et donnees/bibliotheque.json (pour les filtres). Sortie : maquette/…, autonome.
Le contenu (titres, textes, liens, étiquettes) est repris tel quel ; seuls changent l'en-tête
(barre du haut, bandeau), le pied de page, les couleurs par rubrique (retirées) et l'étiquette
« Cours-quiz ».
"""
import copy, json, os, re, sys
from bs4 import BeautifulSoup

ICI = os.path.dirname(os.path.abspath(__file__))
RAC = os.path.dirname(ICI)
MAQ = os.path.join(RAC, 'maquette')
SITE = 'https://babash.github.io/Babash-NSI-SNT/'
LOCAL = 'http://localhost:8761/'

# adresse du site -> fichier de la maquette
PAGES_MAQ = {
    '': 'index.html',
    'nsi-terminale/': 'nsi-terminale/index.html',
    'bibliotheque/': 'bibliotheque/index.html',
    'bibliotheque/?r=annales-bac-nsi-par-notion': 'bibliotheque/fiche.html',
    'bibliotheque/annales/': 'bibliotheque/annales/index.html',
}
NAV = [('snt/', 'SNT'), ('nsi-premiere/', 'NSI 1re'), ('nsi-terminale/', 'NSI Tle'),
       ('pp/', 'PP'), ('autres/', 'Autres'), ('bibliotheque/', 'Bibliothèque')]
PUCES = {'snt/': 'SNT', 'nsi-premiere/': '1re', 'nsi-terminale/': 'Tle', 'pp/': 'PP', 'autres/': 'Tous'}

BIB = json.load(open(os.path.join(RAC, 'main/donnees/bibliotheque.json'), encoding='utf-8'))
FICHES = {r['id']: r for r in BIB['ressources']}
PLACES = json.load(open(os.path.join(MAQ, 'assets/td/places-margouillat.json'), encoding='utf-8'))


def lien(href, ici):
    """Réécrit un lien du site capturé : vers la maquette si l'écran existe, sinon vers le site en ligne."""
    if href is None:
        return None
    if href.startswith(LOCAL):
        chemin = href[len(LOCAL):]
    elif href.startswith('/') and not href.startswith('//'):
        chemin = href[1:]
    else:
        return href
    base, _, ancre = chemin.partition('#')
    if base in PAGES_MAQ:
        cible = os.path.relpath(os.path.join(MAQ, PAGES_MAQ[base]), os.path.dirname(os.path.join(MAQ, ici)))
        return cible + ('#' + ancre if ancre else '')
    return SITE + chemin


def barre_haut(ici, courant):
    items = []
    for chemin, nom in NAV:
        cur = ' aria-current="page"' if chemin == courant else ''
        items.append(f'<li><a href="{lien(LOCAL + chemin, ici)}"{cur}>{nom}</a></li>')
    return f'''<header class="barre-haut"><div class="barre-int">
<a class="marque" href="{lien(LOCAL, ici)}"><span class="marque-logo" aria-hidden="true">&gt;_</span><span class="marque-nom">Ressources NSI et SNT</span></a>
<nav class="nav" aria-label="Rubriques"><ul>{''.join(items)}</ul></nav>
<div class="mode" role="group" aria-label="Affichage">
<button type="button" class="mode-btn" data-theme="auto" aria-pressed="true" title="Suivre le réglage de l'appareil"><span class="mode-ico" aria-hidden="true">◆</span><span class="mode-nom">Auto</span></button><button type="button" class="mode-btn" data-theme="light" aria-pressed="false" title="Affichage clair"><span class="mode-ico" aria-hidden="true">□</span><span class="mode-nom">Clair</span></button><button type="button" class="mode-btn" data-theme="dark" aria-pressed="false" title="Affichage obscur"><span class="mode-ico" aria-hidden="true">■</span><span class="mode-nom">Obscur</span></button>
</div></div></header>'''


def bandeau(titre, puce, sur_titre, numero=None, compact=False, repere=None):
    attrs = f' data-bandeau="{numero}"' if numero else ' data-bandeau="1" data-rotation=""'
    cls = 'bandeau compact' if compact else 'bandeau'
    sur = ''.join(f'<span>{s}</span>' for s in sur_titre)
    rep = repere or ''
    return f'''<header class="{cls}"{attrs}>
<div class="bandeau-decor" aria-hidden="true"><span class="margouillat"></span></div>
<div class="bandeau-texte"><p class="sur-titre"><span class="puce">{puce}</span>{sur}</p><h1{' class="long"' if len(titre) > 22 else ''}><span>{titre}</span></h1></div>
{rep}</header>'''


def pied(ici):
    return f'''<footer class="pied">
<p class="pied-ligne">Babash&#xA0;-&#xA0;NSI Tani Malandi · documents <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr" rel="license">CC BY-SA 4.0</a> · code <a href="https://opensource.org/license/mit" rel="license">MIT</a> · <a href="https://github.com/babash/Babash-NSI-SNT">Code source sur GitHub</a> · conçu avec l'aide de l'IA</p>
<p class="petit mentions">Ces ressources sont conçues par <strong>Babash&#xA0;-&#xA0;NSI Tani Malandi</strong> ; beaucoup le sont avec l'aide de l'IA.
Tu peux les réutiliser et les modifier en mentionnant Babash&#xA0;-&#xA0;NSI Tani Malandi et la licence ; un document modifié se partage sous la même licence. Si tu utilises l'IA pour les modifier, merci de le préciser.
Les ressources externes restent la propriété de leurs auteurs et autrices : leur site d'origine est indiqué sur chaque ressource. Décor du site : dessin original.</p>
</footer>'''


def document(titre, description, ici, corps):
    prof = ici.count('/')
    a = '../' * prof + 'assets/'
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E0C14" media="(prefers-color-scheme: dark)">
<script>try {{ var m = localStorage.getItem('theme'); if (m === 'light' || m === 'dark') document.documentElement.setAttribute('data-theme', m); }} catch (e) {{}}</script>
<link rel="icon" href="{a}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{a}fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a}signal-commun.css">
<link rel="stylesheet" href="{a}site.css">
</head>
<body>
<!-- Maquette T126 (proposition, à ne pas publier) : contenu copié du site (origin/main), nouveau style. -->
<a class="evitement" href="#contenu">Aller aux ressources</a>
{corps}
<script>window.PLACES_MARGOUILLAT = {json.dumps(PLACES)};</script>
<script src="{a}maquette.js"></script>
</body>
</html>
'''


def preparer(nom):
    html = open(os.path.join(RAC, 'dom', nom + '.html'), encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    for s in soup.select('svg.scene'):
        s.decompose()
    for s in soup.select('header.barre-haut'):
        s.decompose()
    for e in soup.select('[style]'):
        if '--hl' in e['style']:
            del e['style']
    for e in soup.select('.cherche-ico'):
        e.clear(); e.append('>')
    for e in soup.select('footer.pied'):
        e.decompose()
    for e in soup.select('button.deplier'):
        e.decompose()
    return soup


def reecrire_liens(soup, ici):
    for a in soup.find_all('a', href=True):
        a['href'] = lien(a['href'], ici)


def cours_quiz(soup):
    for li in soup.select('li.res'):
        t = li.select_one('a.titre')
        if t and 'cours-quiz' in t.get_text():
            li['class'] = li.get('class', []) + ['res-cours-quiz']
            et = soup.new_tag('span', attrs={'class': 'etiquette-signal'})
            et.string = 'Cours-quiz'
            t.insert_before(et)


def ecrire(ici, html):
    chemin = os.path.join(MAQ, ici)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    open(chemin, 'w', encoding='utf-8').write(html)
    print('écrit', chemin, len(html))


def page(nom, ici, courant, entete, titre, description, transformer=None):
    soup = preparer(nom)
    page_div = soup.select_one('div.page')
    hero = page_div.select_one('header.hero')
    intro_el = soup.new_tag('div', attrs={'class': 'intro'})
    # chapo et recherche du hero passent sous le bandeau
    for sel in ['p.chapo', 'div.cherche']:
        e = hero.select_one(sel)
        if e:
            intro_el.append(e.extract())
    nouvel = BeautifulSoup(entete, 'html.parser')
    hero.replace_with(nouvel)
    suivant = page_div.select_one('div.intro')
    if suivant is not None and intro_el.contents:
        for c in list(intro_el.contents):
            suivant.insert(0, c)
    elif intro_el.contents:
        page_div.select_one('header.bandeau').insert_after(intro_el)
    cours_quiz(soup)
    if transformer:
        transformer(soup)
    reecrire_liens(soup, ici)
    page_div.append(BeautifulSoup(pied(ici), 'html.parser'))
    corps = barre_haut(ici, courant) + str(page_div)
    ecrire(ici, document(titre, description, ici, corps))
    return soup


# ── Accueil (direction A : un bandeau, en rotation) ──
def puces_accueil(soup):
    for sec in soup.select('section.noeud'):
        a = sec.select_one('a.noeud-nom')
        chemin = a['href'].replace(LOCAL, '')
        meta = sec.select_one('.noeud-meta')
        p = soup.new_tag('span', attrs={'class': 'puce'}); p.string = PUCES.get(chemin, '')
        meta.insert(0, p)
    for a in soup.select('.themes-mini a.est-vide'):
        s = soup.new_tag('span', attrs={'class': 'invisible'}); s.string = ' (pas encore de ressource)'
        a.append(s)


nb_total = len(BIB['ressources'])
rep_bib = f'<a class="bandeau-repere" href="bibliotheque/index.html"><b>{nb_total}</b>ressources</a>'
page('accueil', 'index.html', None,
     bandeau('Ressources NSI et SNT', 'SNT · NSI', ['Seconde · Première · Terminale']),
     'Ressources NSI et SNT',
     'Cours, activités et outils pour la SNT et la NSI, rangés selon les programmes officiels.',
     puces_accueil)
# repère « 221 ressources » dans le bandeau de l'accueil
p = os.path.join(MAQ, 'index.html'); s = open(p, encoding='utf-8').read()
s = s.replace('</span></h1></div>\n</header>', '</span></h1></div>\n' + rep_bib + '</header>', 1)
open(p, 'w', encoding='utf-8').write(s)


# ── Accueil, direction B : pas de bandeau en haut, un paysage par rubrique ──
def accueil_b(soup):
    puces_accueil(soup)
    for sec, n in zip(soup.select('section.noeud'), ['2', '1', '3', '4', '2']):
        d = soup.new_tag('div', attrs={'class': 'noeud-paysage', 'aria-hidden': 'true', 'data-bandeau': n})
        sec.insert(0, d)
    b = soup.select_one('header.bandeau')
    titre = BeautifulSoup('<header class="entete-simple"><p class="sur-titre"><span class="puce">SNT · NSI</span><span>Seconde · Première · Terminale</span></p><h1><span>Ressources NSI et SNT</span></h1></header>', 'html.parser')
    b.replace_with(titre)


page('accueil', 'accueil-b.html', None, bandeau('Ressources NSI et SNT', 'SNT · NSI', ['x']),
     'Ressources NSI et SNT (variante B)', 'Variante B de l\'accueil : un paysage par rubrique.', accueil_b)


# ── Rubrique NSI Terminale ──
def rubrique(soup):
    for e in soup.select('div.intro p.niveau'):
        e.decompose()
    # l'intro : chapo, texte officiel ; la recherche reste dans la colonne de gauche


page('rubrique', 'nsi-terminale/index.html', 'nsi-terminale/',
     bandeau('NSI Terminale', 'Tle', ['Terminale, spécialité', '44 ressources'], numero=3),
     'NSI Terminale – Ressources NSI et SNT',
     'Les six rubriques du programme de terminale, la reprise des notions de première à la rentrée, et la préparation des épreuves du bac.',
     rubrique)


# ── Bibliothèque ──
CLES = {'ens': 'enseignements', 'niv': 'niveaux', 'prog': 'programme', 'type': 'types',
        'usage': 'usages', 'lang': 'langages', 'orig': 'origine'}


def biblio(soup):
    for li in soup.select('ul.resultats > li.res'):
        lf = li.select_one('a.lien-fiche')
        if not lf:
            continue
        m = re.search(r'\?r=([^&#]+)', lf['href'])
        f = FICHES.get(m.group(1)) if m else None
        if not f:
            continue
        for cle, champ in CLES.items():
            v = f.get(champ)
            if v is None:
                continue
            li['data-' + cle] = ' '.join(v) if isinstance(v, list) else str(v)
        li['data-notion'] = ' '.join((f.get('notions') or {}).get('travaillees') or [])


page('biblio', 'bibliotheque/index.html', 'bibliotheque/',
     bandeau('Bibliothèque', 'Tous', ['SNT, NSI et pour la classe', f'{nb_total} ressources']),
     'Bibliothèque – Ressources NSI et SNT',
     'Toutes les ressources de SNT et de NSI, avec leurs documents : recherche par mots-clés et par notions, filtres par programme, type, niveau et usage.',
     biblio)


# ── Fiche d'une ressource : page de lecture ──
def fiche(soup):
    cote = soup.select_one('aside.cote')
    if cote:
        cote.decompose()
    rc = soup.select_one('div.rub-corps')
    rc['class'] = rc.get('class', []) + ['lecture']
    for e in soup.select('div.intro'):
        e.decompose()


page('fiche', 'bibliotheque/fiche.html', 'bibliotheque/',
     bandeau('Bibliothèque', 'Fiche', ['Annales du bac NSI par notion'], numero=4, compact=True),
     'Annales du bac NSI par notion – Bibliothèque – Ressources NSI et SNT',
     'Choisir des exercices du bac par chapitre, pour préparer une feuille « comme au bac ».',
     fiche)


# ── Annales (page d'application) ──
page('annales', 'bibliotheque/annales/index.html', 'bibliotheque/',
     bandeau('Annales du bac NSI par notion', 'Bac', ['Bibliothèque', 'NSI Terminale', 'épreuve écrite'], numero=4),
     'Annales du bac NSI par notion – Ressources NSI et SNT',
     '315 exercices de 87 sujets (2021-2026) : pour chaque chapitre, les exercices de bac qui le travaillent, avec le sujet officiel et son corrigé.')
