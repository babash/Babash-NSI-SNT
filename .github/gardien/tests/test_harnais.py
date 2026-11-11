"""Les harnais du Gardien versés par T47 font-ils ce que dit leur en-tête ? (test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_harnais.py DOSSIER_DE_TRAVAIL

Essaie les outils de .github/gardien/ (ceux de cette copie) sur des données fabriquées dans le
dossier de travail, sans réseau :
  - empreintes_migration.py : règle M3 (begin; et commit;), une empreinte qui ne dépend ni des
    commentaires ni des espaces, fichier introuvable, --requete ;
  - annexes_code_source.py : des listes fabriquées (dépôt du propriétaire, page déposée, site
    externe, autre propriétaire, bloc en commentaire), --proprietaire, propriétaire par défaut ;
  - depots.sh : l'aide, et « contenues » sur un clone fabriqué (branche contenue, propre, absente) ;
    « attendre » et « etat » passent par l'API GitHub : ils ne sont pas essayés ici ;
  - pdf_comparer.py : des PDF imprimés par Chrome (identiques ; mot perdu, pages en plus, mention
    absente, mention chevauchée, mot dans la marge du bas ; PDF d'un seul côté) ;
  - texte_rendu.py : une phrase et une adresse de lien qui changent, pages par défaut (Chrome) ;
  - diapo_dessous.py : un faux reveal.js, servi comme un CDN (contenu caché, commandes
    chevauchées, élément absent, reveal.js absent) (Chrome) ;
  - pages_depot.py : un faux dépôt avant/après (lien ajouté, CDN servi sans « .min », faux client
    Supabase, Tailwind compilé, requête bloquée ; contraste du lien, adresse, recouvrement,
    défilement, erreur JavaScript, textes pâles avec --contrastes, piège du clavier, rang du lien
    au clavier depuis le début de la page ; défaut antérieur ; --preparer ; impression) (Chrome).
Il faut Python avec Playwright et Pillow, Chrome ou Chromium, git, bash, et poppler (pdfinfo,
pdftotext, pdftoppm).
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
OUTILS = os.path.dirname(ICI)
sys.path.insert(0, ICI)
sys.path.insert(0, OUTILS)
import cadre  # noqa: E402
import commun  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

travail = cadre.arguments(__doc__, site=False)
bilan = cadre.Bilan()


def commande(args, entree=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(args, capture_output=True, input=entree, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def outil(nom, *args):
    return commande([sys.executable, "-I", "-B", os.path.join(OUTILS, nom), *args])


def attendre(titre, code, sortie, code_attendu, presents=(), absents=()):
    pb = [] if code == code_attendu else ["code %d au lieu de %d" % (code, code_attendu)]
    pb += ["absent de la sortie : « %s »" % m for m in presents if not re.search(m, sortie, re.M)]
    pb += ["inattendu dans la sortie : « %s »" % m for m in absents if re.search(m, sortie, re.M)]
    bilan.verifier(titre, pb, sortie[-2500:] if pb else "")


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)


def page_html(corps, tete="", style=""):
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Témoin</title>'
            '%s<style>body{margin:0;font:16px sans-serif;background:#fff;color:#222}main,footer{padding:16px}%s</style>'
            '</head><body>%s</body></html>\n') % (tete, style, corps)


# ── empreintes_migration.py ─────────────────────────────────────────────────
mig = os.path.join(travail, "migrations")
ecrire(os.path.join(mig, "0001-table.sql"), "-- 0001 : une table\n-- deux lignes d'en-tête\nbegin;\ncreate table x (id int);\ncommit;\n")
ecrire(os.path.join(mig, "0002-table-commentee.sql"),
       "begin;\n/* un commentaire\n   sur deux lignes */\ncreate   table x\n  (id int); -- en fin de ligne\n\ncommit;\n")
ecrire(os.path.join(mig, "hors-m3", "0003-sans-begin.sql"), "create table y (id int);\n")
ecrire(os.path.join(mig, "hors-m3", "0004-commit-avant-la-fin.sql"), "begin;\ncommit;\ncreate table z (id int);\n")
md5 = hashlib.md5(b"createtablex(idint)").hexdigest()  # le texte sans commentaires, espaces ni « ; »
code, sortie = outil("empreintes_migration.py", mig)
attendre("empreintes_migration.py : règle M3, même empreinte malgré commentaires et espaces", code, sortie, 1, presents=[
    r"0001-table\.sql +M3 ok +begin \[3\] +commit \[5\] +md5 %s$" % md5,
    r"0002-table-commentee\.sql +M3 ok +begin \[1\] +commit \[7\] +md5 %s$" % md5,
    r"0003-sans-begin\.sql +M3 NON +begin - +commit - +md5 ",
    r"0004-commit-avant-la-fin\.sql +M3 NON +begin \[1\] +commit \[2\] ",
    r"^4 fichier\(s\), 2 hors de la règle M3$",
], absents=[r"Requête"])
code, sortie = outil("empreintes_migration.py", os.path.join(mig, "0001-table.sql"),
                     os.path.join(mig, "0002-table-commentee.sql"), "--requete")
attendre("empreintes_migration.py --requete : deux fichiers conformes, code 0, la requête", code, sortie, 0, presents=[
    r"^2 fichier\(s\), 0 hors de la règle M3$", r"lecture de métadonnées seulement",
    r"from supabase_migrations\.schema_migrations", r"md5\(regexp_replace\(regexp_replace\(regexp_replace\(",
])
code, sortie = outil("empreintes_migration.py", os.path.join(mig, "absent.sql"))
attendre("empreintes_migration.py : fichier introuvable, erreur d'usage", code, sortie, 2, presents=[r"introuvable : .*absent\.sql"])

# ── annexes_code_source.py ──────────────────────────────────────────────────
site = os.path.join(travail, "site-annexes")
REGLAGES = 'reglages({\n%s  rubriques: [\n    "snt",\n    "nsi",\n  ],\n});\n'
ecrire(os.path.join(site, "reglages.js"), REGLAGES % '  depot: "proprio/site",\n')
ecrire(os.path.join(site, "snt", "ressources.js"), "\n".join([
    'theme("Internet");',
    "/* Un exemple, en commentaire :",
    "ressource({",
    '  titre: "Exemple commenté",',
    '  lien: "https://proprio.github.io/exemple/",',
    "});",
    "*/",
    "ressource({",
    '  titre: "Appli avec son dépôt",',
    '  lien: "https://proprio.github.io/appli/",',
    "  annexes: {",
    '    "Guide": "https://proprio.github.io/appli/guide.html",',
    '    "Code source": "https://github.com/proprio/appli",',
    "  },",
    "});",
    "ressource({",
    '  titre: "Appli sans annexe",',
    '  lien: "https://proprio.github.io/autre/",',
    "});",
    "ressource({",
    '  titre: "TD déposé",',
    '  lien: "fichiers/td/index.html",',
    '  annexes: { "Code source, à dupliquer": "https://github.com/proprio/site" },',
    "});",
    "",
]))
ecrire(os.path.join(site, "nsi", "ressources.js"), "\n".join([
    "ressource({",
    '  titre: "Site externe",',
    '  lien: "https://exemple.org/cours/",',
    "});",
    "ressource({",
    "  titre: \"Dépôt d'un autre propriétaire\",",
    '  lien: "https://github.com/autre/outil",',
    "});",
    "",
]))
code, sortie = outil("annexes_code_source.py", site)
attendre("annexes_code_source.py : propriétaire du réglage depot, une annexe manque", code, sortie, 1, presents=[
    r"^5 ressource\(s\) ; 3 avec un dépôt de « proprio » ou une page déposée ; 1 sans annexe « Code source » :$",
    r"^  - snt : Appli sans annexe \(https://proprio\.github\.io/autre/\)$",
], absents=[r"Exemple commenté", r"Appli avec son dépôt", r"TD déposé", r"Site externe"])
code, sortie = outil("annexes_code_source.py", site, "--proprietaire", "autre")
attendre("annexes_code_source.py --proprietaire autre : son dépôt, sans annexe", code, sortie, 1, presents=[
    r"^5 ressource\(s\) ; 2 avec un dépôt de « autre » ou une page déposée ; 1 sans annexe « Code source » :$",
    r"^  - nsi : Dépôt d'un autre propriétaire \(https://github\.com/autre/outil\)$",
])
ecrire(os.path.join(site, "reglages.js"), REGLAGES % "")
code, sortie = outil("annexes_code_source.py", site)
attendre("annexes_code_source.py : sans réglage depot, propriétaire babash, code 0", code, sortie, 0, presents=[
    r"^5 ressource\(s\) ; 1 avec un dépôt de « babash » ou une page déposée ; 0 sans annexe « Code source »\.$",
])

# ── depots.sh ───────────────────────────────────────────────────────────────
DEPOTS = os.path.join(OUTILS, "depots.sh")
code, sortie = commande(["bash", DEPOTS])
attendre("depots.sh sans argument : l'aide, code 1", code, sortie, 1, presents=[
    r"^Usage \(depuis la copie du dépôt", r"depots\.sh attendre DELAI DEPOT=SHA", r"depots\.sh contenues DOSSIER_DU_CLONE",
    r"^Code de sortie : 0 \(aussi pour --help\) ; 1 pour un usage incorrect",
], absents=[r"set -u", r"^#"])
code, sortie = commande(["bash", DEPOTS, "--help"])
attendre("depots.sh --help : l'aide, code 0", code, sortie, 0, presents=[r"^Usage \(depuis la copie du dépôt"])
clone = os.path.join(travail, "clone")
os.makedirs(clone, exist_ok=True)


def git(*args):
    # l'auteur des commits du dépôt (CLAUDE.md), adresse publique que sensibles.py range dans « attendu »
    code, sortie = commande(["git", "-C", clone, "-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com",
                             "-c", "commit.gpgsign=false", *args])
    if code:
        raise SystemExit("git %s : %s" % (" ".join(args), sortie))
    return sortie.strip()


git("init", "-q")
git("commit", "-q", "--allow-empty", "-m", "un")
git("update-ref", "refs/remotes/origin/contenue", "HEAD")
git("commit", "-q", "--allow-empty", "-m", "deux")
git("update-ref", "refs/remotes/origin/main", "HEAD")
git("commit", "-q", "--allow-empty", "-m", "trois, propre à la branche")
git("update-ref", "refs/remotes/origin/propre", "HEAD")
code, sortie = commande(["bash", DEPOTS, "contenues", clone, "contenue", "propre", "absente"])
attendre("depots.sh contenues : contenue, propre (1 commit), absente", code, sortie, 0, presents=[
    r"^contenue +contenue dans main \([0-9a-f]{7,}\)$",
    r"^propre +NON CONTENUE : 1 commit\(s\) propres, tête [0-9a-f]{7,}, \d\d/\d\d \d\d:\d\d trois, propre à la branche$",
    r"^absente +absente$",
])

# ── pdf_comparer.py (PDF imprimés par Chrome) ───────────────────────────────
MENTION = "Babash - NSI Tani Malandi"
STYLE_PDF = """@page { size: A4; margin: 0 }
body { margin: 0; font: 12pt sans-serif }
.page { position: relative; height: 296mm; padding: 15mm; box-sizing: border-box }
.page + .page { break-before: page }
.mention, .intrus, .dessus { position: absolute; bottom: 8mm; margin: 0; font-size: 9pt }
.mention { left: 15mm }
.intrus { left: 48mm }
.dessus { left: 20mm; bottom: 9.5mm }
.bas { position: absolute; right: 15mm; bottom: 0.5mm; margin: 0 }"""


def document(pages):
    """pages : (texte, avec la mention ?, HTML en plus) pour chaque page A4."""
    corps = "".join('<div class="page"><p>%s</p>%s%s</div>' % (
        texte, ('<p class="mention">%s · CC BY-SA 4.0</p>' % MENTION) if mention else "", plus) for texte, mention, plus in pages)
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (STYLE_PDF, corps)


DEUX_PAGES = [("Premier paragraphe sur les réseaux.", True, ""), ("Second paragraphe sur le protocole TCP.", True, "")]
PDF = {
    "pdf-avant/td.pdf": DEUX_PAGES,
    "pdf-avant/ancien.pdf": [("Un document retiré.", True, "")],
    "pdf-pareil/td.pdf": DEUX_PAGES,
    "pdf-apres/td.pdf": [("Premier paragraphe sur les réseaux.", True, '<p class="bas">débordement</p>'),
                         ("Second paragraphe sur le TCP, nouveauté.", False, ""),
                         ("Une page en plus.", True, '<p class="intrus">INTRUS</p>'),
                         ("Encore une.", True, '<p class="dessus">DESSUS</p>')],
    "pdf-apres/sous/nouveau.pdf": [("Un document ajouté.", True, "")],
}
with sync_playwright() as p:
    nav = commun.lancer(p)
    for nom, pages in PDF.items():
        chemin = os.path.join(travail, nom)
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        pg = nav.new_page()
        pg.set_content(document(pages), wait_until="load")
        pg.pdf(path=chemin, format="A4", print_background=True, prefer_css_page_size=True)
        pg.close()
    nav.close()
code, sortie = outil("pdf_comparer.py", os.path.join(travail, "pdf-avant", "td.pdf"),
                     os.path.join(travail, "pdf-pareil", "td.pdf"), "--mention", MENTION)
attendre("pdf_comparer.py : deux PDF identiques, mention sur chaque page, code 0", code, sortie, 0, presents=[
    r"^td\.pdf : 2 page\(s\) .*\(A4\) -> 2 page\(s\) .*\(A4\) ; ok$",
    r"^    mention : présente sur chaque page, rien ne la touche$", r"^1 PDF comparé\(s\) ; 0 point\(s\) à examiner$",
], absents=[r"mots de l'avant", r"mots nouveaux"])
code, sortie = outil("pdf_comparer.py", os.path.join(travail, "pdf-avant"), os.path.join(travail, "pdf-apres"), "--mention", MENTION)
attendre("pdf_comparer.py : dossiers ; mot perdu, pages, mention absente, chevauchée, marge du bas", code, sortie, 1, presents=[
    r"^PDF de l'avant absents de l'après : ancien\.pdf$", r"^PDF nouveaux : sous/nouveau\.pdf$",
    r"^td\.pdf : 2 page\(s\) .* -> 4 page\(s\) .* ; À EXAMINER \(pages 2 -> 4, 1 mot\(s\) perdu\(s\), mention : 4 défaut\(s\)\)$",
    r"^    mots de l'avant absents de l'après : protocole$", r"^    mots nouveaux \(\d+\) : .*nouveauté",
    r"p\. 1 : « débordement » dans la marge du bas", r"p\. 2 : mention absente",
    r"p\. 3 : « INTRUS » chevauche la mention", r"p\. 4 : « DESSUS » chevauche la mention",
    r"^1 PDF comparé\(s\) ; 3 point\(s\) à examiner$",
])

# ── texte_rendu.py (Chrome) ─────────────────────────────────────────────────
for version, phrase, cible, en_plus, hors in (
        ("avant", "Une phrase mal recopiée.", "snt/a.html", "", "Hors de la zone : avant."),
        ("apres", "Une phrase bien recopiée.", "snt/b.html",
         '<p><a href="https://github.com/proprio/site">Code source sur GitHub</a></p>', "Hors de la zone : après.")):
    d = os.path.join(travail, "texte-" + version)
    ecrire(os.path.join(d, "reglages.js"), 'reglages({\n  rubriques: [\n    "snt",\n  ],\n});\n')
    ecrire(os.path.join(d, "index.html"), page_html(
        '<main id="site"><h1>Ressources</h1><p>Une ligne commune.</p><p>%s</p><p><a href="%s">Le TD</a></p>'
        '<p><a href="https://exemple.org/">Externe</a></p>%s<img src="https://images.exemple.net/a.png" alt=""></main>'
        '<p>%s</p>' % (phrase, cible, en_plus, hors)))
    ecrire(os.path.join(d, "snt", "index.html"), page_html('<main id="site"><h1>SNT</h1><p>Rien ne change.</p></main>'))
code, sortie = outil("texte_rendu.py", os.path.join(travail, "texte-avant"), os.path.join(travail, "texte-apres"))
attendre("texte_rendu.py : phrase et adresse changées, dans #site seulement, pages par défaut", code, sortie, 0, presents=[
    r"^== /$", r"^== /snt/$",
    r"^  texte : 1 ligne\(s\) en moins, 2 en plus$", r"^    -Une phrase mal recopiée\.$", r"^    \+Une phrase bien recopiée\.$",
    r"^    \+Code source sur GitHub$",
    r"^  liens : 1 ligne\(s\) en moins, 2 en plus$", r"^    -Le TD -> snt/a\.html$", r"^    \+Le TD -> snt/b\.html$",
    r"^    \+Code source sur GitHub -> https://github\.com/proprio/site$",
    r"^  texte : 0 ligne\(s\) en moins, 0 en plus$",
], absents=[r"Hors de la zone", r"Externe"])

# ── diapo_dessous.py (Chrome, faux reveal.js servi comme un CDN) ────────────
diapo = os.path.join(travail, "diapo")
paquet_reveal = os.path.join(travail, "paquet-reveal", "dist")
ecrire(os.path.join(paquet_reveal, "reveal.js"), """window.Reveal = (() => {
  const S = [...document.querySelectorAll('.slides > section')]; let i = 0;
  const montrer = () => S.forEach((s, k) => s.classList.toggle('present', k === i));
  montrer();
  return { getTotalSlides: () => S.length, slide(h) { i = h; montrer(); }, next() { i = Math.min(i + 1, S.length - 1); montrer(); },
           getIndices: () => ({ h: i, v: 0 }) };
})();
""")
STYLE_DIAPO = """html, body { margin: 0; height: 100% }
.reveal .slides > section { display: none; position: absolute; inset: 0; padding: 20px; font: 20px sans-serif }
.reveal .slides > section.present { display: block }
.reveal .controls button { position: fixed; width: 40px; height: 40px; bottom: 12px }
.reveal .controls .navigate-left { right: 60px }
.reveal .controls .navigate-right { right: 12px }
.reveal .progress { position: fixed; left: 0; right: 0; top: 0; height: 4px; background: #39f }
.pied { position: fixed; left: 0; bottom: 0; background: #eee; font: 14px sans-serif }"""
for nom, pied, bas in (("mauvais.html", "right: 0; height: 64px", "bottom: 8px"), ("bon.html", "width: 300px; height: 30px", "top: 200px")):
    ecrire(os.path.join(diapo, nom), (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Diaporama</title><style>%s\n.pied { %s }</style></head>'
        '<body><div class="reveal"><div class="slides"><section><h1>Titre</h1></section>'
        '<section><p style="position: absolute; left: 20px; margin: 0; %s">Texte sous le pied</p></section></div>'
        '<div class="controls"><button class="navigate-left">&lt;</button><button class="navigate-right">&gt;</button></div>'
        '<div class="progress"><span></span></div></div><div class="pied">Babash - NSI Tani Malandi</div>'
        '<script src="https://cdn.exemple.org/reveal/4.5.0/reveal.min.js"></script></body></html>\n') % (STYLE_DIAPO, pied, bas))
CDN_REVEAL = "https://cdn.exemple.org/reveal/4.5.0/=" + paquet_reveal
code, sortie = outil("diapo_dessous.py", diapo, "mauvais.html", "--selecteur", ".pied", "--largeurs", "800", "--cdn", CDN_REVEAL)
attendre("diapo_dessous.py : contenu caché et commandes chevauchées, code 1", code, sortie, 1, presents=[
    r"^ 800 px : 2 diapositive\(s\) ; contenu caché : 1 ; commandes chevauchées : navigate-left, navigate-right$",
    r"^      diapositive 1\.0 : p « Texte sous le pied »$",
    r"^      navigate-right +écart minimal +-\d+\.\d px \(CHEVAUCHEMENT \d+ px²\)$",
    r"^      progress +écart minimal +\d+\.\d px$", r"^2 problème\(s\)$",
])
code, sortie = outil("diapo_dessous.py", diapo, "bon.html", "--selecteur", ".pied", "--largeurs", "800", "--cdn", CDN_REVEAL)
attendre("diapo_dessous.py : rien de caché ni de chevauché, code 0", code, sortie, 0, presents=[
    r"^ 800 px : 2 diapositive\(s\) ; contenu caché : aucun ; commandes chevauchées : aucune$",
    r"^      navigate-left +écart minimal +\d+\.\d px$", r"^0 problème\(s\)$",
], absents=[r"CHEVAUCHEMENT"])
code, sortie = outil("diapo_dessous.py", diapo, "bon.html", "--selecteur", ".absent", "--largeurs", "800", "--cdn", CDN_REVEAL)
attendre("diapo_dessous.py : élément absent, code 1", code, sortie, 1, presents=[
    r"^ 800 px : élément « \.absent » absent$", r"^1 problème\(s\)$"], absents=[r"diapositive\(s\)"])
code, sortie = outil("diapo_dessous.py", diapo, "bon.html", "--selecteur", ".pied", "--largeurs", "800")
attendre("diapo_dessous.py : sans --cdn, reveal.js n'est pas chargé, code 1", code, sortie, 1,
         presents=[r"reveal\.js n'est pas chargé : vérifier --cdn"])

# ── pages_depot.py (Chrome) ─────────────────────────────────────────────────
av, ap = os.path.join(travail, "depot-avant"), os.path.join(travail, "depot-apres")
DEPOT = "https://github.com/proprio/appli"
BON = '<a class="code" href="%s">Code source sur GitHub</a>' % DEPOT
PIED = "<footer><p>Babash - NSI Tani Malandi · licence MIT%s</p></footer>"
STYLE_LIEN = "footer{color:#333}a.code{color:#1d4ed8}"
paquet_outil = os.path.join(travail, "paquet-outil")
ecrire(os.path.join(paquet_outil, "outil.js"), "window.outilCharge = true;\n")
ecrire(os.path.join(travail, "tailwind-apres.css"), "footer a.code { color: #1d4ed8 }\n")
# index.html : le lien est ajouté ; sa couleur ne vient que de la feuille Tailwind compilée.
ecrire(os.path.join(av, "index.html"), page_html("<main><h1>Appli</h1></main>" + PIED % ""))
ecrire(os.path.join(ap, "index.html"), page_html(
    '<main><h1>Appli</h1><img src="https://images.exemple.net/logo.png" alt=""></main>' + PIED % (" · " + BON) +
    '<script>if (!window.outilCharge) throw new Error("outil absent : CDN non servi");'
    'window.supabase.createClient("https://x.supabase.co", "cle-publique").rpc("f").then(function () {});</script>',
    tete='<script src="https://cdn.tailwindcss.com"></script><script src="https://cdn.exemple.org/outil/1.0/outil.min.js"></script>'
         '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>',
    style="footer{color:#333}a.code{color:#bbb}"))
# alertes.html : tout est bon avant ; après, sept défauts nouveaux.
ecrire(os.path.join(av, "alertes.html"), page_html("<main><h1>Alertes</h1></main>" + PIED % (" · " + BON), style=STYLE_LIEN))
ecrire(os.path.join(ap, "alertes.html"), page_html(
    '<main><h1>Alertes</h1><p class="pale">texte trop pâle</p><div style="width:1200px">large</div></main>' +
    PIED % ' · <a class="code" href="https://github.com/proprio/autre">Code source sur GitHub</a>' +
    '<div class="voile" style="position:fixed;inset:0"></div><script>throw new Error("cassé exprès");</script>',
    style="footer{color:#333}a.code{color:#999}.pale{color:#aaa}"))
# ancien.html : le même défaut avant et après, qui n'est pas une alerte.
for d in (av, ap):
    ecrire(os.path.join(d, "ancien.html"), page_html("<main><h1>Ancien</h1></main>" + PIED % (" · " + BON) +
                                                     '<script>console.error("défaut antérieur");</script>', style=STYLE_LIEN))
# clavier.html : après, un éditeur garde la touche Tab.
for d, piege in ((av, ""), (ap, '<script>document.getElementById("editeur").addEventListener("keydown", e => {'
                               ' if (e.key === "Tab") { e.preventDefault(); e.target.value += "  "; } });</script>')):
    ecrire(os.path.join(d, "clavier.html"), page_html('<main><textarea id="editeur"></textarea></main>' + PIED % (" · " + BON) + piege,
                                                      style=STYLE_LIEN))
# panneau.html : le lien est dans un panneau fermé, que --preparer ouvre.
for d in (av, ap):
    ecrire(os.path.join(d, "panneau.html"), page_html('<main><h1>Panneau</h1></main><div id="panneau" hidden>' + PIED % (" · " + BON) +
                                                      "</div>", style=STYLE_LIEN))
ecrire(os.path.join(travail, "ouvrir.js"), "() => { const p = document.getElementById('panneau'); if (p) p.hidden = false; }\n")
COMMUNES = ["--depot", DEPOT, "--largeurs", "800", "--modes", "light", "--clavier", "800", "--attente", "300",
            "--cdn", "https://cdn.exemple.org/outil/1.0/=" + paquet_outil, "--tailwind-apres", os.path.join(travail, "tailwind-apres.css")]
sortie_1 = os.path.join(travail, "pages-1")
code, sortie = outil("pages_depot.py", av, ap, sortie_1, "index.html", "alertes.html", "ancien.html", "clavier.html",
                     "--impression", "--contrastes", *COMMUNES)
attendre("pages_depot.py : lien ajouté (CDN, Supabase, Tailwind servis), sept alertes, défaut antérieur, piège du clavier",
         code, sortie, 1, presents=[
             r"^  index\.html +800 light ok \[lien \d+\.\d\d:1, texte 12\.63:1, Tab 1\]$",
             r"^  alertes\.html +800 light ALERTE .*erreur JavaScript : .*cassé exprès",
             r"^  alertes\.html .*défilement horizontal de \d+ px", r"^  alertes\.html .*adresse du lien : https://github\.com/proprio/autre",
             r"^  alertes\.html .*contraste du lien 2\.85:1 sur #ffffff", r"^  alertes\.html .*lien recouvert par div\.voile",
             r"^  alertes\.html .*texte à 2\.32:1 \(exigé 4\.5\) : p\.pale « texte trop pâle »",
             r"^  alertes\.html .*texte à 2\.85:1 \(exigé 4\.5\) : a\.code « Code source sur GitHub »",
             r"^  ancien\.html +800 light ok \| antérieur : erreur de la console : défaut antérieur \[lien",
             r"^  clavier\.html +800 light ALERTE lien pas atteint au clavier : le focus reste sur textarea#editeur \[lien",
             r"^  index\.html +pages 1 -> 1 ; pages qui diffèrent : 1 ; lien imprimé : non -> oui$",
             r'^Requêtes vers d\'autres sites, bloquées : \{"avant": \{\}, "apres": \{"images\.exemple\.net": \d+\}\}$',
             r"^4 mesure\(s\) après, 2 avec une alerte nouvelle$",
         ], absents=[r"outil absent", r"supabase", r"index\.html +800 light ALERTE"])
try:
    with open(os.path.join(sortie_1, "resultats.json"), encoding="utf-8") as f:
        res = json.load(f)
    pb = [] if len(res["mesures"]) == 8 else ["%d mesures au lieu de 8" % len(res["mesures"])]
    pb += [] if "clavier.html apres" in res["impressions"] else ["impression de clavier.html après absente"]
    rang = [r.get("clavier", {}).get("arret") for r in res["mesures"] if r["page"] == "clavier.html" and r["version"] == "avant"]
    pb += [] if rang == [2] else ["clavier.html avant : le lien atteint à la pression %s au lieu de 2 (éditeur, puis lien)" % rang]
    pb += ["capture absente : " + r["capture"] for r in res["mesures"] if not os.path.exists(os.path.join(sortie_1, r["capture"]))]
except (OSError, ValueError, KeyError) as e:
    pb = ["resultats.json illisible : %s" % e]
bilan.verifier("pages_depot.py : resultats.json (8 mesures, impressions, rang au clavier) et les captures", pb)
code, sortie = outil("pages_depot.py", av, ap, os.path.join(travail, "pages-2"), "index.html", "ancien.html", "panneau.html",
                     "--preparer", os.path.join(travail, "ouvrir.js"), *COMMUNES)
attendre("pages_depot.py --preparer : le panneau ouvert avant les mesures, aucune alerte, code 0", code, sortie, 0, presents=[
    r"^  panneau\.html +800 light ok \[lien \d+\.\d\d:1, texte 12\.63:1, Tab 1\]$",
    r"^3 mesure\(s\) après, 0 avec une alerte nouvelle$",
], absents=[r"invisible", r"ALERTE"])

bilan.terminer()
