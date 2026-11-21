"""Les outils du Gardien versés par T32 font-ils ce que dit leur en-tête ? (test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_outils.py DOSSIER_DE_TRAVAIL

Essaie les outils de .github/gardien/ (ceux de cette copie) sur des données fabriquées dans le
dossier de travail :
  - caracteres.py : un diff piégé (point médian, espace sans largeur, contrôle bidirectionnel,
    puces entre deux lettres, espace insécable, ligne ajoutée qui commence par « ++ ») ; un diff
    propre ; l'option --diff sur une plage vide de cette copie ; un PDF lu comme du texte, ignoré (T125) ;
  - qcu_forme.py (T125) : une page où la bonne option est la plus longue dans 3 QCU sur 4 (À REVOIR),
    une page aux options équilibrées, une bonne option seule avec du code (indice à relire) ;
  - chemins_readme.py : un petit site et son README (chemins présents, absents, relatifs à un
    dossier cité, nom seul, motif, extension seule, adresse, gabarit, bloc de code) ; puis N16 :
    adresses file://, valeurs entre guillemets, chemin qui contient des espaces, commande ;
  - zones.py : des captures synthétiques (pied de page seul, bande modifiée, bruit de 1/255,
    capture d'un seul côté), avec et sans --tolerance ;
  - contraste_zone.py : une page témoin aux contrastes connus, servie en local (Chrome) ;
  - contrastes.py : un onglet coupé au bord d'une bande qui défile, au-dessus d'un voisin clair,
    n'est mesuré que sur sa partie visible ; un texte visible sous le seuil reste signalé (T51) ;
  - commun, liens.py et annexes_code_source.py sur un petit site qui lit la vitrine et les fiches
    (T51b) : rubriques et compte, fichier manquant, lien principal et document GitHub, dépôt sans
    document « Code source » ;
  - sensibles.py : des textes ordinaires avec « (sur) », « [point] », « (dot) », « [at] », puis deux
    adresses électroniques masquées pour les robots (T65), dans un petit dépôt git ; un code de classe
    (trois caractères, tiret, trois caractères), signalé et masqué, mais pas « sud-est » (alerte du 20/11).
"""
import json
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
OUTILS = os.path.dirname(ICI)
sys.path.insert(0, ICI)
import cadre  # noqa: E402
from PIL import Image  # noqa: E402

travail = cadre.arguments(__doc__, site=False)
bilan = cadre.Bilan()


def outil(nom, *args, entree=None):
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(OUTILS, nom), *args],
                       capture_output=True, input=entree, text=True)
    return r.returncode, r.stdout + r.stderr


def attendre(titre, code, sortie, code_attendu, presents=(), absents=()):
    pb = [] if code == code_attendu else ["code %d au lieu de %d" % (code, code_attendu)]
    pb += ["absent de la sortie : « %s »" % m for m in presents if not re.search(m, sortie, re.M)]
    pb += ["inattendu dans la sortie : « %s »" % m for m in absents if re.search(m, sortie, re.M)]
    bilan.verifier(titre, pb, sortie[-1500:] if pb else "")


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)


# ── caracteres.py ───────────────────────────────────────────────────────────
# Les caractères piégés sont écrits par leur code : le source de ce test n'en contient aucun.
ZWSP, RLO, PUCE, INSECABLE = chr(0x200B), chr(0x202E), chr(0x2022), chr(0x00A0)
DIFF = "\n".join([
    "diff --git a/snt/ressources.js b/snt/ressources.js",
    "--- a/snt/ressources.js",
    "+++ b/snt/ressources.js",
    "@@ -10,3 +10,7 @@ theme(\"Internet\");",
    " contexte",
    "-ancienne ligne",
    '+  titre: "Forum des enseignant·e·s",',
    '+  texte: "un espace' + ZWSP + 'sans largeur",',
    '+  code: "a' + RLO + 'b",',
    '+  puces: "enseignant' + PUCE + 'e' + PUCE + 's" et "' + PUCE + ' une liste" ; note' + INSECABLE + ': rien',
    " contexte2",
    "+++ une ligne ajoutée qui commence par deux plus" + ZWSP,
    "diff --git a/README.md b/README.md",
    "--- a/README.md",
    "+++ b/README.md",
    "@@ -1 +1 @@",
    "-Titre",
    "+Titre propre",
    "",
])
code, sortie = outil("caracteres.py", "-", entree=DIFF)
attendre("caracteres.py : diff piégé, chaque caractère à sa ligne", code, sortie, 1, presents=[
    r"^À RELIRE  invisible U\+200B \(ZERO WIDTH SPACE\) ×1  snt/ressources\.js:12 : .*espace⟨U\+200B⟩sans",
    r"^À RELIRE  bidirectionnel U\+202E \(RIGHT-TO-LEFT OVERRIDE\) ×1  snt/ressources\.js:13 ",
    r"^À RELIRE  point de substitution U\+2022 \(BULLET\) .*snt/ressources\.js:14 ",
    r"^INFO      point médian ×2  snt/ressources\.js:11 ",
    r"^À RELIRE  invisible U\+200B .*snt/ressources\.js:16 : \+\+ une ligne ajoutée",
    r"^Bilan : 6 ligne\(s\) ajoutée\(s\) lue\(s\) ; 5 caractère\(s\) à relire ; pour information : "
    r"2 point\(s\) médian\(s\) sur 1 ligne\(s\), 1 espace\(s\) insécable\(s\)\.$",
], absents=[ZWSP, RLO, r"README\.md:"])
n_substituts = len(re.findall(r"point de substitution", sortie))
bilan.verifier("caracteres.py : deux puces entre des lettres, la puce de liste ignorée",
               [] if n_substituts == 2 else ["%d point(s) de substitution au lieu de 2" % n_substituts])
code, sortie = outil("caracteres.py", "-", entree="+++ b/a.txt\n@@ -0,0 +1 @@\n+Les élèves sont fort·e·s.\n")
attendre("caracteres.py : point médian seul, code 0 (il n'est jamais une faute)", code, sortie, 0,
         presents=[r"^INFO      point médian ×2  a\.txt:1 "])
code, sortie = outil("caracteres.py", "--diff", "HEAD...HEAD")
attendre("caracteres.py --diff : plage vide de cette copie", code, sortie, 0, presents=[r"^Bilan : 0 ligne\(s\) ajoutée"])
code, sortie = outil("caracteres.py")
attendre("caracteres.py sans argument : erreur d'usage", code, sortie, 2, presents=[r"donner soit un fichier de diff"])
# T125 : un PDF que git lit comme du texte (flux compressés) est ignoré ; le HTML d'à côté, non
code, sortie = outil("caracteres.py", "-", entree="+++ b/td.pdf\n@@ -0,0 +1,2 @@\n+%PDF" + ZWSP + "\n+flux" + RLO
                     + "\n+++ b/td.html\n@@ -0,0 +1 @@\n+ok" + ZWSP + "\n")
attendre("caracteres.py : fichier binaire ignoré, le texte voisin lu (T125)", code, sortie, 1, presents=[
    r"^INFO      fichier binaire ignoré \(lu comme du texte par git\) : td\.pdf$",
    r"^À RELIRE  invisible U\+200B .*td\.html:1 ",
    r"^Bilan : 1 ligne\(s\) ajoutée\(s\) lue\(s\) ; 1 caractère\(s\) à relire"], absents=[r"td\.pdf:", r"U\+202E"])

# ── qcu_forme.py (T125) ─────────────────────────────────────────────────────
def page_td(qcus):
    """Une page de TD minimale : un QCU par élément de qcus, (options, rang de la bonne)."""
    sections = []
    for k, (options, juste) in enumerate(qcus, 1):
        lis = "".join('<li%s>%s</li>' % (' data-juste' if i == juste else ' data-retour="non"', o) for i, o in enumerate(options))
        sections.append('<section class="td-q" data-type="qcu" id="q%d"><p class="td-consigne">Question %d ?</p>'
                        '<ul class="td-options">%s</ul><div class="td-correction"><ul><li>une liste dans la correction, '
                        'qui n\'est pas une option</li></ul></div></section>' % (k, k, lis))
    return '<main class="td" data-td="essai">%s</main>' % "".join(sections)


QCU_LONG = [(["La bonne réponse, nettement plus longue que les autres", "Faux un", "Faux deux", "Faux trois"], 0)] * 3 + \
           [(["Aaaa", "Bbbb", "Cccc", "Dddd"], 2)]
ecrire(os.path.join(travail, "qcu", "long.html"), page_td(QCU_LONG))
code, sortie = outil("qcu_forme.py", os.path.join(travail, "qcu", "long.html"))
attendre("qcu_forme.py : bonne option la plus longue dans 3 QCU sur 4 : À REVOIR", code, sortie, 1, presents=[
    r"4 QCU ; bonne option nettement la plus longue : 3 \(75 %\) : À REVOIR",
    r"long\.html#q1 : 54 caractères contre 10 au plus pour les autres \+\+"], absents=[r"#q4 :"])
QCU_EQUILIBRE = [(["Option un", "Option de", "Option tr", "Option qu"], 1)] * 4
ecrire(os.path.join(travail, "qcu", "equilibre.html"), page_td(QCU_EQUILIBRE))
code, sortie = outil("qcu_forme.py", os.path.join(travail, "qcu", "equilibre.html"))
attendre("qcu_forme.py : options de même longueur et de même forme : rien à signaler", code, sortie, 0,
         presents=[r"4 QCU ; bonne option nettement la plus longue : 0 \(0 %\)$"], absents=[r"À REVOIR", r"indices"])
QCU_CODE = [(["<code>x = 1</code>", "avec un", "avec deu", "avec tro"], 0)]
ecrire(os.path.join(travail, "qcu", "code.html"), page_td(QCU_CODE))
code, sortie = outil("qcu_forme.py", os.path.join(travail, "qcu", "code.html"))
attendre("qcu_forme.py : seule option avec du code, premier mot à part : à relire (code 2)", code, sortie, 2,
         presents=[r"code\.html#q1 : seule avec du code", r"code\.html#q1 : premier mot à part \(« x » contre « avec »\)"],
         absents=[r"À REVOIR"])

# ── chemins_readme.py ───────────────────────────────────────────────────────
site = os.path.join(travail, "site-readme")
ecrire(os.path.join(site, "reglages.js"), 'reglages({\n  rubriques: [\n    "snt",\n  ],\n});\n')
ecrire(os.path.join(site, "snt", "ressources.js"), "")
ecrire(os.path.join(site, "snt", "fichiers", "app", "config.js"), "")
ecrire(os.path.join(site, "donnees", "referentiels", "valeurs.json"), "{}")
ecrire(os.path.join(site, "README.md"), "\n".join([
    "Les réglages : `reglages.js` et `snt/ressources.js`.",                       # 1
    "Les extensions (`.py`, `.odt`) ne sont pas des chemins.",                     # 2
    "Le dossier `snt/fichiers/app/` contient `config.js`.",                        # 3
    "Le référentiel `referentiels/valeurs.json`, dans `donnees/`.",                # 4
    "Un nom seul, `valeurs.json`, et un motif, `*/ressources.js`.",                # 5
    "Une adresse `https://exemple.org/a.js`, un gabarit `donnees/ressources/<id>.json`.",  # 6
    "Absents : `snt/fichiers/absent.pdf` et `docs/`, puis `snt/?q=x`.",            # 7
    "```js",                                                                       # 8
    "`dans/un/bloc.js`",                                                           # 9
    "```",                                                                         # 10
    "",
]))
code, sortie = outil("chemins_readme.py", site)
attendre("chemins_readme.py : présents, absents et cas ignorés", code, sortie, 1, presents=[
    r"^ok     reglages\.js \(ligne 1\)$", r"^ok     snt/ressources\.js \(ligne 1\)$",
    r"^ok     config\.js \(ligne 3\)$", r"^ok     referentiels/valeurs\.json \(ligne 4\)$",
    r"^ok     valeurs\.json \(ligne 5\)$", r"^ok     \*/ressources\.js \(ligne 5\)$", r"^ok     snt/ \(ligne 7\)$",
    r"^ABSENT snt/fichiers/absent\.pdf \(ligne 7\)$", r"^ABSENT docs/ \(ligne 7\)$",
    r"README\.md : 11 chemin\(s\) cité\(s\), 2 absent\(s\) : docs/, snt/fichiers/absent\.pdf$",
], absents=[r"\.py \(", r"\.odt", r"https", r"<id>", r"dans/un/bloc\.js"])

# N16 : ni les adresses file://, ni les valeurs entre guillemets ; un chemin à espaces trouvé en entier.
TIRET = chr(0x2013)
ecrire(os.path.join(site, "snt", "fichiers", "Thème 1 " + TIRET + " Données", "cours.pdf"), "")
ecrire(os.path.join(site, "scripts", "outil.py"), "")
ecrire(os.path.join(site, "N16.md"), "\n".join([
    "Les adresses `file://` et `file:///home/x/a.html` ne sont pas des chemins.",            # 1
    "Le réglage `depot: \"propriétaire/nom\"`, la valeur `'snt/absent.js'` et `titre: \"TD 1/2\"` non plus.",  # 2
    "Le dossier `snt/fichiers/Thème 1 " + TIRET + " Données/`, avec "
    "`snt/fichiers/Thème 1 " + TIRET + " Données/cours.pdf`.",                                # 3
    "La commande `python3 -I scripts/outil.py snt/` : un mot à la fois.",                     # 4
    "Absent, avec des espaces : `snt/fichiers/Thème 9/`.",                                    # 5
    "",
]))
code, sortie = outil("chemins_readme.py", site, os.path.join(site, "N16.md"))
attendre("chemins_readme.py (N16) : file://, guillemets, chemin à espaces, commande", code, sortie, 1, presents=[
    r"^ok     snt/fichiers/Thème 1 " + TIRET + r" Données/ \(ligne 3\)$",
    r"^ok     snt/fichiers/Thème 1 " + TIRET + r" Données/cours\.pdf \(ligne 3\)$",
    r"^ok     scripts/outil\.py \(ligne 4\)$", r"^ok     snt/ \(ligne 4\)$",
    r"^ABSENT snt/fichiers/Thème \(ligne 5\)$",
    r"N16\.md : 6 chemin\(s\) cité\(s\), 2 absent\(s\)",
], absents=[r"file", r"propriétaire", r"absent\.js", r"depot", r"python3", r"1/2", r"^ABSENT snt/fichiers/Thème 1"])

# ── zones.py ────────────────────────────────────────────────────────────────


def rendu(nom, captures):
    """Un faux dossier de rendu.py : resultats.json et une capture par page."""
    d = os.path.join(travail, nom)
    os.makedirs(d, exist_ok=True)
    resultats = []
    for page, image in captures.items():
        image.save(os.path.join(d, page + ".png"))
        resultats.append({"page": page, "largeur": image.width, "mode": "light", "capture": page + ".png"})
    with open(os.path.join(d, "resultats.json"), "w", encoding="utf-8") as f:
        json.dump({"resultats": resultats}, f)
    return d


def page(hauteur, bandes=()):
    """Une page blanche de 200 px de large, avec des bandes (début, fin, gris) dessinées dessus."""
    im = Image.new("RGB", (200, hauteur), (255, 255, 255))
    for debut, fin, gris in bandes:
        im.paste((gris, gris, gris), (0, debut, 200, fin + 1))
    return im


avant = rendu("zones-avant", {"a-pied": page(1000), "b-bande": page(1000), "c-bruit": page(1000), "d-seule": page(500)})
apres = rendu("zones-apres", {"a-pied": page(1050, [(900, 1049, 40)]), "b-bande": page(1000, [(100, 109, 0)]),
                              "c-bruit": page(1000, [(50, 52, 254)])})
code, sortie = outil("zones.py", avant, apres)
attendre("zones.py : pied de page seul, bande, bruit et capture d'un seul côté", code, sortie, 1, presents=[
    r"^a-pied 200 light .*\(\+50\) ; 1re ligne différente :   900, soit   100 px .*identique au-dessus de la marge \(600 px comparés\)",
    r"^b-bande 200 light .*AU-DESSUS de la marge : 2000 pixels différents \(écart max 255/255\), zone \(0, 100, 200, 110\), bandes \[\(100, 109\)\]",
    r"^c-bruit 200 light .*AU-DESSUS de la marge : 600 pixels différents \(écart max 1/255\)",
    r"^ - d-seule 200 light : présente d'un seul côté$",
    r"^2 capture\(s\) sur 4 diffèrent au-dessus de la marge de 400 px",
])
avant2 = rendu("zones-avant-2", {"a-pied": page(1000), "c-bruit": page(1000)})
apres2 = rendu("zones-apres-2", {"a-pied": page(1050, [(900, 1049, 40)]), "c-bruit": page(1000, [(50, 52, 254)])})
code, sortie = outil("zones.py", avant2, apres2, "--tolerance", "4")
attendre("zones.py --tolerance 4 : le bruit de 1/255 est écarté, le pied de page reste", code, sortie, 0, presents=[
    r"^c-bruit 200 light .*aucune ligne différente .*identique au-dessus de la marge",
    r"^a-pied 200 light .*soit   100 px",
])

# ── contraste_zone.py (Chrome) ──────────────────────────────────────────────
temoin = os.path.join(travail, "site-temoin")
ecrire(os.path.join(temoin, "reglages.js"), "reglages({\n  rubriques: [],\n});\n")
ecrire(os.path.join(temoin, "index.html"), """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Témoin</title></head>
<body style="margin:0;background:#fff;font:16px sans-serif">
<p style="color:#999">hors de la zone : gris 999 sur blanc (2,85:1)</p>
<footer><p class="mentions" style="color:#767676">gris 767676 sur blanc (4,54:1)</p>
<p class="mentions" style="color:#595959">gris 595959 sur blanc (7,00:1)</p></footer>
</body></html>
""")
with cadre.servir(temoin) as url:
    code, sortie = outil("contraste_zone.py", url, "--racine", temoin, "--largeurs", "800", "--modes", "light")
    attendre("contraste_zone.py : seuls les textes de la zone, le plus faible à 4,54:1", code, sortie, 0, presents=[
        r"^accueil 800 light +2 textes ; le plus faible : 4\.54:1 \(p\.mentions « gris 767676",
        r"Zone « p\.mentions » : contraste le plus faible 4\.54:1",
    ], absents=[r"2\.85"])
    code, sortie = outil("contraste_zone.py", url, "--racine", temoin, "--largeurs", "800", "--modes", "light",
                         "--zone", "p.inexistante")
    attendre("contraste_zone.py : zone absente, code 1", code, sortie, 1, presents=[r"zone « p\.inexistante » absente"])

# ── contrastes.py : un onglet coupé au bord d'une bande qui défile (T51) ─────
# Comme l'onglet « Bibliothèque » à 768 px : sa boîte dépasse de la bande (overflow-x: auto) et
# passe au-dessus de l'interrupteur clair voisin. Seule sa partie affichée, sur le fond sombre
# (6,83:1), compte ; mesurée sur toute sa boîte, elle tomberait à 2,38:1. Un texte bien visible
# sous le seuil reste signalé.
defile = os.path.join(travail, "site-defile")
ecrire(os.path.join(defile, "reglages.js"), "reglages({\n  rubriques: [],\n});\n")
ecrire(os.path.join(defile, "index.html"), """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Bande</title></head>
<body style="margin:0;background:#fff;font:16px sans-serif">
<nav style="display:flex;width:420px;background:#111">
<ul style="display:flex;overflow-x:auto;white-space:nowrap;width:200px;margin:0;padding:0;list-style:none;scrollbar-width:none">
<li style="padding:4px 8px"><a href="#a" style="color:#8d9cba">Premier</a></li>
<li style="padding:4px 8px"><a href="#b" style="color:#8d9cba">Deuxième</a></li>
<li style="padding:4px 8px"><a href="#c" style="color:#8d9cba">Bibliothèque coupée</a></li>
</ul>
<span style="display:block;width:220px;background:#eee;color:#000">Auto</span>
</nav>
<p style="color:#999">gris 999 sur blanc (2,85:1), bien visible</p>
</body></html>
""")
with cadre.servir(defile) as url:
    code, sortie = outil("contrastes.py", url, os.path.join(travail, "contrastes-defile"), "--racine", defile,
                         "--largeurs", "800", "--modes", "light")
    attendre("contrastes.py : onglet coupé au bord d'une bande qui défile, mesuré sur sa partie visible", code, sortie, 1,
             presents=[r"2\.85:1 \(exigé 4\.5\) p « gris 999", r"^accueil 800 light +\d+ textes, 1 sous le seuil"],
             absents=[r"« Bibliothèque coupée »", r"2\.38"])

# ── commun, liens.py, annexes_code_source.py : un site qui lit la vitrine (T51b) ───
# Un petit site dont assets/site.js charge la bibliothèque construite : les outils comptent et lisent
# d'après la vitrine et les fiches. La fiche « cachee » n'a aucun document visible de l'extérieur.
vit = os.path.join(travail, "site-vitrine")
ecrire(os.path.join(vit, "assets", "site.js"), "var BIBLIOTHEQUE = 'donnees/bibliotheque.json';\nfetch(RACINE + BIBLIOTHEQUE).then(f);\n")
ecrire(os.path.join(vit, "reglages.js"), 'reglages({\n  depot: "proprio/site",\n  rubriques: [\n    "ancienne",\n  ],\n});\n')
ecrire(os.path.join(vit, "index.html"), "<p>accueil</p>")
ecrire(os.path.join(vit, "aa", "fichiers", "td.html"), "<p>td</p>")
ecrire(os.path.join(vit, "donnees", "vitrine.json"), json.dumps({"rubriques": [
    {"id": "aa", "sections": [{"id": "s1", "ressources": ["r1", "cachee"], "sous_sections": [{"id": "g", "ressources": ["r2"]}]}]},
    {"id": "bb", "sections": [{"id": "s2", "ressources": ["r1", "absente"]}]}]}))
VU, CACHE = {"exterieur": True, "eleve": True}, {"exterieur": False, "eleve": True}
for rid, docs in (
        ("r1", [{"role": "page", "fichier": "aa/fichiers/td.html", "principal": True, "visible": VU},
                {"role": "code-source", "url": "https://github.com/proprio/site", "visible": VU}]),
        ("r2", [{"role": "page", "url": "https://proprio.github.io/appli/", "principal": True, "visible": VU},
                {"role": "complement", "url": "https://github.com/proprio/appli", "visible": VU},
                {"role": "page", "fichier": "aa/fichiers/manque.pdf", "visible": VU}]),
        ("cachee", [{"role": "page", "url": "https://github.com/proprio/cachee", "principal": True, "visible": CACHE}])):
    ecrire(os.path.join(vit, "donnees", "ressources", rid + ".json"), json.dumps({"id": rid, "titre": "Titre " + rid, "documents": docs}))
sys.path.insert(0, OUTILS)
import commun  # noqa: E402
obtenu = (commun.lit_la_vitrine(vit), commun.rubriques(vit), commun.attendu(vit, "aa"), commun.attendu(vit, "bb"))
bilan.verifier("commun (T51b) : rubriques de la vitrine, ressources visibles de l'extérieur comptées",
               [] if obtenu == (True, ["aa", "bb"], 2, 1) else ["%r au lieu de %r" % (obtenu, (True, ["aa", "bb"], 2, 1))])
code, sortie = outil("liens.py", vit)
attendre("liens.py (T51b) : documents des fiches : fichier manquant, lien principal et document GitHub", code, sortie, 1, presents=[
    r"^Liens internes cassés : 1$", r"donnees/ressources/r2\.json › documents\[2\] : fichier introuvable : aa/fichiers/manque\.pdf",
    r"^Liens principaux vers GitHub : 1$", r"donnees/ressources/cachee\.json › documents\[0\] : lien principal vers GitHub",
    r"donnees/ressources/r2\.json › documents\[1\] : document « complement » vers GitHub sans le rôle « code-source »",
])
code, sortie = outil("annexes_code_source.py", vit)
attendre("annexes_code_source.py (T51b) : la fiche d'une application sans document « Code source »", code, sortie, 1, presents=[
    r"^3 fiche\(s\) ; 3 avec un dépôt de « proprio » ou un fichier déposé ; 2 sans document « Code source » :$",
    r"^  - r2 : Titre r2$", r"^  - cachee : Titre cachee$",
], absents=[r"^  - r1 "])

# ── sensibles.py : adresse électronique masquée (T65) ───────────────────────
# L'adresse et les textes ordinaires sont assemblés à l'exécution : le dépôt est public, et aucune
# adresse, même inventée, ne doit y figurer (voir cadre.py). Ils n'existent que dans le dossier de travail.
POINT, SUR, AT, DOT = "[po" + "int]", "[s" + "ur]", "(a" + "t)", "(d" + "ot)"
depot_sens = os.path.join(travail, "depot-sensibles")
ecrire(os.path.join(depot_sens, "propre.html"), "<p>Cliquer (sur) le bouton ; voir la liste[point] ci-dessous ; "
       "f(x) (dot) produit ; t[at] = 0</p>\n")
subprocess.run(["git", "-C", depot_sens, "init", "-q"], check=True)
subprocess.run(["git", "-C", depot_sens, "add", "-A"], check=True)
code, sortie = outil("sensibles.py", depot_sens)
attendre("sensibles.py : textes ordinaires avec (sur), [point], (dot), [at] : rien à examiner", code, sortie, 0,
         presents=[r"0 occurrence\(s\) à examiner"], absents=[r"masquée"])
ecrire(os.path.join(depot_sens, "corrige.html"), "<p><em>prenom" + POINT + "nom" + SUR + "domaine-ac.fr</em></p>\n"
       "<p>contact : prenom.nom " + AT + " exemple " + DOT + " org</p>\n")
subprocess.run(["git", "-C", depot_sens, "add", "-A"], check=True)
code, sortie = outil("sensibles.py", depot_sens)
attendre("sensibles.py : deux adresses masquées ([point] et [sur], (at) et (dot)), code 1", code, sortie, 1, presents=[
    r"^\[à examiner\] adresse électronique masquée \| corrige\.html:1 \|",
    r"^\[à examiner\] adresse électronique masquée \| corrige\.html:2 \|",
    r"2 occurrence\(s\) à examiner",
])

# ── sensibles.py : code de classe (alerte du 20/11) ─────────────────────────
# Le code est assemblé à l'exécution, comme les adresses : aucun code de classe, même inventé, dans le dépôt.
CODE = "Q" + "X7-" + "4P" + "B"
depot_classe = os.path.join(travail, "depot-classe")
ecrire(os.path.join(depot_classe, "propre.html"), "<p>Le vent du sud-est ; UTF-8 ; un code de jeu CORAIL-MANTA-482.</p>\n")
subprocess.run(["git", "-C", depot_classe, "init", "-q"], check=True)
subprocess.run(["git", "-C", depot_classe, "add", "-A"], check=True)
code, sortie = outil("sensibles.py", depot_classe)
attendre("sensibles.py : sud-est, UTF-8, code de jeu en mots : pas un code de classe", code, sortie, 0,
         presents=[r"0 occurrence\(s\) à examiner"], absents=[r"code de classe"])
ecrire(os.path.join(depot_classe, "commentaire.js"), "// la classe de démonstration : " + CODE + "\n")
subprocess.run(["git", "-C", depot_classe, "add", "-A"], check=True)
code, sortie = outil("sensibles.py", depot_classe)
attendre("sensibles.py : un code de classe en commentaire, signalé et masqué, code 1", code, sortie, 1,
         presents=[r"^\[à examiner\] code de classe \| commentaire\.js:1 \|", r"Q…\(code masqué\)"], absents=[re.escape(CODE)])

bilan.terminer()
