"""Planche pour l'enseignant (T126) : avant/après des cinq écrans, téléphone et obscur, deux directions, ce qui change."""
import asyncio, os
from playwright.async_api import async_playwright

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PL = os.path.join(R, 'planche')
F = os.path.join(R, 'maquette/assets/fonts')

ECRANS = [
    ('accueil', "L'accueil", "Le bandeau de 450 px (ville la nuit) devient le paysage des TD, à l'échelle : 150 px. Une carte par rubrique, trait fin ; le niveau se lit dans une puce de texte (SNT, 1RE, TLE) et non plus dans une couleur. Un thème sans ressource est en pointillés.", 'Le cône vu de la baie, et son téléphérique de pirogues (bandeau en rotation : un par jour).'),
    ('rubrique', 'Une rubrique : NSI Terminale', "Même sommaire à gauche, mêmes thèmes, même ordre. Titres de thème en Anton avec le filet rose des TD ; une ressource n'est plus une carte mais un bloc séparé par un filet ; ses documents sont des liens encadrés.", 'La ville et la barge, avec sa barge-drone (paysage fixe de la rubrique).'),
    ('rubrique-quiz', 'Une rubrique : le cours-quiz en tête de chaque thème', "Le cours-quiz, qui vient en premier dans la séquence, est le seul bloc encadré : le mot « COURS-QUIZ » (comme sous le QR code des TD), un trait épais et le néon cyan en débordement. Rien ne repose sur la couleur.", 'Les cours-quiz sont déjà en tête de leur sous-thème dans la vitrine : rien ne change dans les données.'),
    ('bibliotheque', 'La bibliothèque : liste et filtres', "La recherche passe sous le bandeau, avec l'invite « > ». Les filtres sont des listes sobres (cochée = gras souligné) ; la liste des résultats est compacte : les premières ressources apparaissent sans défiler. Vue « Cartes » et tri inchangés.", "L'îlot de sable blanc, et le feu rouge dans le lagon (en rotation)."),
    ('fiche', "La fiche d'une ressource", "Une page de lecture, de la largeur d'un TD (48 rem), sans les filtres à côté. Le bouton « Ouvrir » est le bouton principal des TD (encre pleine, néon décalé). « En bref » devient un tableau à filets.", 'Bandeau réduit des contrôles (20 mm), le baobab de plage.'),
    ('annales', "Une page d'application : les annales du bac", "Même page, mêmes 315 exercices, mêmes filtres par chapitre ; un clic sur un chapitre le coche. Les liens Sujet et Corrigé sont des liens encadrés, l'avertissement est un cadre en tirets.", 'Le baobab de plage, avec ses paraboles et ses lampions.'),
]


def img(nom):
    return f'img/{nom}.jpg'


def page_ecran(i, nom, titre, texte, paysage):
    return f'''<section class="feuille">
<header class="haut"><span class="num">{i}</span><h2>{titre}</h2></header>
<p class="texte">{texte}</p>
<div class="duo">
  <figure><img src="{img(nom + '-avant')}" alt=""><figcaption>Avant (site actuel, ordinateur, clair)</figcaption></figure>
  <figure class="apres"><img src="{img(nom + '-apres')}" alt=""><figcaption>Après (maquette, ordinateur, clair)</figcaption></figure>
</div>
<div class="trio">
  <figure class="tel"><img src="{img(nom + '-tel')}" alt=""><figcaption>Téléphone, clair</figcaption></figure>
  <figure class="tel"><img src="{img(nom + '-tel-obscur')}" alt=""><figcaption>Téléphone, obscur</figcaption></figure>
  <figure class="large"><img src="{img(nom + '-apres-obscur')}" alt=""><figcaption>Ordinateur, obscur</figcaption></figure>
  <p class="paysage"><b>Paysage :</b> {paysage}</p>
</div>
</section>'''


QUESTIONS = '''<ol class="questions">
<li><b>L'accueil</b> (page 8) : <span class="opt">A</span> un bandeau de paysage en haut, en rotation &nbsp; <span class="opt">B</span> pas de bandeau en haut, un petit paysage sur chaque carte de rubrique.</li>
<li><b>Les paysages des rubriques</b> : <span class="opt">A</span> un paysage fixe par rubrique (SNT l'îlot, 1re le cône, Tle la barge, PP le baobab) &nbsp; <span class="opt">B</span> les quatre en rotation sur toutes les pages.</li>
<li><b>La fiche d'une ressource</b> : <span class="opt">A</span> une page de lecture, sans les filtres (maquette) &nbsp; <span class="opt">B</span> garder les filtres à côté, comme aujourd'hui.</li>
</ol>'''

HTML = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Le site au style des TD</title>
<style>
@font-face {{ font-family: Atk; src: url("file://{F}/atkinson-hyperlegible-latin-400-normal.woff2"); }}
@font-face {{ font-family: Atk; font-weight: 700; src: url("file://{F}/atkinson-hyperlegible-latin-700-normal.woff2"); }}
@font-face {{ font-family: Anton; src: url("file://{F}/anton-latin-400-normal.woff2"); }}
@font-face {{ font-family: Mono; src: url("file://{F}/jetbrains-mono-latin-400-normal.woff2"); }}
@font-face {{ font-family: Mono; font-weight: 700; src: url("file://{F}/jetbrains-mono-latin-700-normal.woff2"); }}
@font-face {{ font-family: VT; src: url("file://{F}/vt323-latin-400-normal.woff2"); }}
@font-face {{ font-family: Sym; src: url("file://{F}/td-symboles-400-normal.woff2"); }}
@page {{ size: A4 landscape; margin: 9mm 11mm 10mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font: 10pt/1.4 Atk, Sym, sans-serif; color: #121016; }}
.feuille {{ height: 190mm; break-after: page; position: relative; overflow: hidden; }}
.feuille:last-child {{ break-after: auto; }}
h1, h2 {{ font-family: Anton, sans-serif; font-weight: 400; text-transform: uppercase; margin: 0; line-height: 1.05; }}
h1 {{ font-size: 30pt; text-shadow: -1.6px .8px 0 #FF2E97, 1.6px -.8px 0 #00D8F5; }}
h2 {{ font-size: 17pt; }}
h3 {{ font: 400 12pt/1.2 Anton, sans-serif; text-transform: uppercase; margin: 3mm 0 1.5mm; border-bottom: 1.5px solid #121016; box-shadow: 0 2px 0 #FF2E97; padding-bottom: .6mm; }}
.haut {{ display: flex; align-items: center; gap: 3mm; border-bottom: 1.5px solid #121016; box-shadow: 0 2.5px 0 #FF2E97; padding-bottom: 1.5mm; }}
.num {{ font: 400 13pt/1 Anton; border: 1.5px solid #121016; padding: .6mm 2mm; box-shadow: 2px 2px 0 #00D8F5; }}
.texte {{ margin: 2mm 0 2.5mm; font-size: 10pt; max-width: 250mm; }}
figure {{ margin: 0; }}
figure img {{ display: block; width: 100%; border: 1px solid #121016; }}
figcaption {{ font: 400 7.6pt/1.3 Mono, monospace; margin-top: .8mm; }}
.duo {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }}
.duo .apres img {{ box-shadow: 2px 2px 0 #00D8F5; }}
.trio {{ display: grid; grid-template-columns: 32mm 32mm 1fr; gap: 5mm; margin-top: 3mm; align-items: start; }}
.trio .tel img {{ height: 67mm; width: auto; max-width: 100%; object-fit: cover; object-position: top; }}
.trio .large img {{ height: 67mm; width: auto; }}
.paysage {{ grid-column: 1 / -1; margin: 0; font-size: 8.5pt; position: absolute; bottom: 0; right: 0; max-width: 95mm; text-align: right; }}
.sur {{ font: 700 9pt Mono, monospace; text-transform: uppercase; display: flex; gap: 2mm; align-items: center; }}
.puce {{ font: 400 11pt Anton; border: 1.5px solid #121016; padding: 0 1.6mm; box-shadow: 2px 2px 0 #00D8F5; }}
.accroche {{ font: 400 15pt VT, monospace; margin: 1mm 0 4mm; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 9mm; }}
ul, ol {{ margin: 1mm 0; padding-left: 5mm; }}
li {{ margin: .8mm 0; }}
.questions li {{ margin: 2mm 0; }}
.opt {{ font: 700 9pt Mono; border: 1.2px solid #121016; padding: 0 1.2mm; }}
.cadre {{ border: 1.2px solid #121016; border-left: 3.5px solid #121016; padding: 2.5mm 4mm; box-shadow: 2px 2px 0 #00D8F5; margin-top: 3mm; }}
.bandeau-img {{ width: 100%; display: block; margin: 3mm 0 2mm; }}
.petit {{ font-size: 8.5pt; }}
.mono {{ font: 400 8.6pt/1.45 Mono, monospace; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; }}
td, th {{ border-top: 1px dotted #8C8796; padding: 1.1mm 2mm 1.1mm 0; text-align: left; vertical-align: top; }}
th {{ font: 700 7.8pt Mono; text-transform: uppercase; border-top: 1.5px solid #121016; }}
.ab {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 3mm; }}
.ab figure img {{ height: 92mm; width: auto; max-width: 100%; }}
.ab .lettre {{ font: 400 22pt Anton; border: 1.8px solid #121016; padding: 0 2.5mm; box-shadow: 2px 2px 0 #00D8F5; margin-right: 2mm; }}
.pied {{ position: absolute; bottom: 0; left: 0; font: 400 7.5pt Mono; }}
</style></head><body>

<section class="feuille">
<p class="sur"><span class="puce">T126</span> Ressources NSI et SNT · proposition · rien n'est publié</p>
<h1 style="margin-top:3mm">Le site au style des TD</h1>
<p class="accroche">&gt; Signal pirate : sobre, compact, lisible.</p>
<img class="bandeau-img" src="file://{R}/maquette/assets/td/bandeau-3.svg" alt="">
<div class="cols">
<div>
<h3>Le principe</h3>
<ul>
<li><b>Une seule palette pour les TD et le site</b> : les mêmes variables, les mêmes polices hébergées (Atkinson Hyperlegible, JetBrains Mono, Anton, VT323), les mêmes quatre paysages de Mayotte.</li>
<li><b>Fond blanc, encre foncée, trait fin</b> ; le cyan et le rose seulement en débordement (ombres décalées, filets). Plus de couleur par rubrique : le niveau est écrit (SNT, 1RE, TLE).</li>
<li><b>Compact</b> : bandeau de 150 px au plus (aujourd'hui 450 px), ressources séparées par un filet au lieu de cartes.</li>
<li><b>Aucun personnage, aucun récit</b> : le design et un clin d'œil caché, le margouillat vert à turbine, qui change de cachette.</li>
<li><b>Même site</b> : mêmes adresses, même navigation, mêmes textes et mêmes fonctions (page 9).</li>
</ul>
<div class="cadre petit"><b>Vérifié sur la maquette</b> : 320, 768 et 1440 px, clair et obscur, sans défilement horizontal ; clavier (lien d'évitement, contour de focus de 3 px) ; aucune animation (réglage « réduire les animations » respecté) ; contrastes de 8:1 au moins pour le texte et les liens (18,9:1 pour le texte courant), 9,9:1 pour le petit texte ; aucune requête vers un autre site (plus de Google Fonts).</div>
</div>
<div>
<h3>Trois questions</h3>
{QUESTIONS}
<h3>Les écrans</h3>
<p class="mono">2 Accueil · 3-4 Rubrique NSI Terminale · 5 Bibliothèque · 6 Fiche · 7 Annales · 8 Deux directions pour l'accueil · 9 Ce qui change, ce qui ne change pas · 10 Pour appliquer</p>
</div></div>
<p class="pied">Babash - NSI Tani Malandi · CC BY-SA 4.0 · conçu avec l'aide de l'IA · maquette : designer-t126/maquette/</p>
</section>

{''.join(page_ecran(i + 2, *e) for i, e in enumerate(ECRANS))}

<section class="feuille">
<header class="haut"><span class="num">8</span><h2>L'accueil : deux directions</h2></header>
<p class="texte">C'est la seule hésitation structurante. A garde le bandeau des TD en haut de l'accueil (un paysage par jour). B retire le bandeau du haut : le titre, la recherche, puis un petit paysage en tête de chaque carte de rubrique (SNT l'îlot, 1re le cône, Tle la barge, PP le baobab). B montre les rubriques plus haut ; A ressemble davantage aux feuilles.</p>
<div class="ab">
<figure><p><span class="lettre">A</span> un bandeau en haut, en rotation</p><img src="{img('accueil-apres')}" alt=""></figure>
<figure><p><span class="lettre">B</span> un paysage par carte de rubrique</p><img src="{img('accueilb-apres')}" alt=""></figure>
</div>
<p class="petit" style="margin-top:3mm">Les deux sont dans la maquette : <span class="mono">index.html</span> (A) et <span class="mono">accueil-b.html</span> (B).</p>
</section>

<section class="feuille">
<header class="haut"><span class="num">9</span><h2>Ce qui change, ce qui ne change pas</h2></header>
<div class="cols" style="margin-top:3mm">
<div>
<h3>Ne change pas</h3>
<ul>
<li><b>Les adresses</b> : <span class="mono">/</span>, <span class="mono">/nsi-terminale/</span>, <span class="mono">/bibliotheque/</span>, <span class="mono">/bibliotheque/?r=…</span>, <span class="mono">/bibliotheque/annales/</span>… Aucun lien à refaire, aucun QR code à réimprimer.</li>
<li><b>La navigation</b> : SNT, NSI 1re, NSI Tle, PP, Autres, Bibliothèque, dans cet ordre ; le sommaire des thèmes ; « Retour aux résultats ».</li>
<li><b>Le contenu</b> : rubriques, thèmes, ordre des ressources, textes, documents, étiquettes, fiches, mentions. La maquette est faite avec le HTML que produit le site d'aujourd'hui.</li>
<li><b>Les fonctions</b> : recherche (touche « / »), filtres, tri, vue liste ou cartes, version imprimable des annales, choix Auto / Clair / Obscur (même mémoire du navigateur).</li>
<li><b>L'admin et l'espace élève</b> : hors de cette maquette ; ils prendront la même feuille ensuite.</li>
</ul>
</div>
<div>
<h3>Change</h3>
<ul>
<li><b>Le bandeau</b> : la ville la nuit (450 px, grand aplat sombre) devient un paysage de Mayotte des TD (150 px, fond blanc), avec le margouillat caché.</li>
<li><b>Les polices</b> : Chakra Petch (Google Fonts) laisse la place à Anton et VT323, hébergées comme celles des TD.</li>
<li><b>Les couleurs</b> : plus de couleur par rubrique ni par thème ; encre, trait, et deux néons décoratifs. Un thème vide est en pointillés.</li>
<li><b>Les ressources</b> : des blocs séparés par un filet (au lieu de cartes) ; le cours-quiz encadré, avec son mot.</li>
<li><b>La fiche</b> : une page de lecture sans filtres (question 3).</li>
<li><b>Le pied de page</b> : une ligne « Babash - NSI Tani Malandi · CC BY-SA 4.0 · MIT · Code source sur GitHub · conçu avec l'aide de l'IA », puis les mentions actuelles.</li>
<li><b>L'impression</b> d'une page du site : fond blanc, encre noire, sans navigation ni filtres.</li>
</ul>
</div></div>
<h3>Repris de « Réseau la nuit »</h3>
<p class="petit">Atkinson Hyperlegible et JetBrains Mono hébergées ; Auto / Clair / Obscur ; le cyan et le rose ; les règles de contraste (7:1, 4,5:1) et « jamais la couleur seule » ; l'invite de terminal (« &gt;_ », « &gt; ») ; le décor dans les marges (pistes de circuit, écrans très larges). <b>Laissé</b> : la ville la nuit, Chakra Petch, une couleur par niveau, l'équipage sur l'accueil (réservé aux jeux et aux avatars).</p>
</section>

<section class="feuille">
<header class="haut"><span class="num">10</span><h2>Pour appliquer (après votre accord)</h2></header>
<table style="margin-top:3mm">
<tr><th style="width:24%">Qui</th><th>Quoi</th><th style="width:14%">Travail</th></tr>
<tr><td><b>Designer</b></td><td><span class="mono">assets/signal-commun.css</span> (polices et palette, que <span class="mono">td-en-ligne.css</span> chargera aussi) ; <span class="mono">assets/style.css</span> remplacé par la feuille de la maquette ; <span class="mono">bibliotheque.css</span> et <span class="mono">annales.css</span> absorbés ; polices et paysages (déjà sur la branche des TD) ; nouveau favicon ; captures avant/après.</td><td>une demi-journée</td></tr>
<tr><td><b>Architecte</b> (<span class="mono">assets/site.js</span>, pages)</td><td>la fonction <span class="mono">scene</span> devient le bandeau (paysage, puce, sur-titre, repère, margouillat) ; retirer les couleurs <span class="mono">--hl</span> ; puce de niveau sur les cartes de l'accueil ; classe et mot « Cours-quiz » ; la fiche sans filtres ; pied de page compact (<span class="mono">reglages.js</span>) ; retirer Google Fonts des 13 pages du site ; <span class="mono">theme-color</span>.</td><td>une journée</td></tr>
<tr><td><b>Gardien</b></td><td>contrôle (liens, rendu 320 / 768 / 1440, clair et obscur, caractères), README, publication.</td><td>une heure</td></tr>
<tr><td><b>Ensuite</b> : admin, espace élève, espace enseignant</td><td>même feuille, composants des formulaires à ajouter.</td><td>une demi-journée</td></tr>
</table>
<h3>Les applications (liste, à estimer une par une)</h3>
<ul class="petit">
<li><b>Calendrier</b> (dans ce dépôt, <span class="mono">calendrier/calendrier.css</span>) : palette, polices, pied de page.</li>
<li><b>QuizzNSI</b> (dépôt à part) : pages élève, animation projetée, impression.</li>
<li><b>Gombessa</b>, <b>Lagon Arena</b>, <b>Court-circuit</b> (dépôts à part) : jeux ; leur univers et leurs personnages restent ; seuls la palette, les polices hébergées et le pied de page communs.</li>
</ul>
<p class="petit">Les jeux gardent leur histoire ; le site et les feuilles ne prennent que le design et le clin d'œil du margouillat.</p>
</section>
</body></html>'''


async def main():
    p = os.path.join(PL, 'planche.html')
    open(p, 'w', encoding='utf-8').write(HTML)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page()
        await pg.goto('file://' + p, wait_until='networkidle'); await pg.wait_for_timeout(800)
        await pg.pdf(path=os.path.join(R, 'site-nouveau-design.pdf'), prefer_css_page_size=True, print_background=True)
        await b.close()

asyncio.run(main())
