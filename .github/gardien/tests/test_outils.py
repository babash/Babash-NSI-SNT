"""Les outils du Gardien versés par T32 font-ils ce que dit leur en-tête ? (test du Gardien)

Usage (depuis la copie du dépôt) :
  python3 -I -B .github/gardien/tests/test_outils.py DOSSIER_DE_TRAVAIL

Essaie les outils de .github/gardien/ (ceux de cette copie) sur des données fabriquées dans le
dossier de travail :
  - caracteres.py : un diff piégé (point médian, espace sans largeur, contrôle bidirectionnel,
    puces entre deux lettres, espace insécable, ligne ajoutée qui commence par « ++ ») ; un diff
    propre ; l'option --diff sur une plage vide de cette copie ;
  - chemins_readme.py : un petit site et son README (chemins présents, absents, relatifs à un
    dossier cité, nom seul, motif, extension seule, adresse, gabarit, bloc de code) ; puis N16 :
    adresses file://, valeurs entre guillemets, chemin qui contient des espaces, commande ;
  - zones.py : des captures synthétiques (pied de page seul, bande modifiée, bruit de 1/255,
    capture d'un seul côté), avec et sans --tolerance ;
  - contraste_zone.py : une page témoin aux contrastes connus, servie en local (Chrome).
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
    "Le réglage `depot: \"propriétaire/nom\"` et la valeur `'snt/absent.js'` non plus.",      # 2
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
], absents=[r"file", r"propriétaire", r"absent\.js", r"depot", r"python3", r"^ABSENT snt/fichiers/Thème 1"])

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

bilan.terminer()
