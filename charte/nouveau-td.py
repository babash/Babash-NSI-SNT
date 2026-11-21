#!/usr/bin/env python3
"""Crée le squelette d'un TD en ligne, style « Signal pirate » (T123).

Usage (à la racine du dépôt) :
  python3 -I charte/nouveau-td.py DOSSIER --id IDENTIFIANT --titre "Titre" --niveau "1re NSI" \\
      --chapitre "Programmer en Python" --bandeau 1 [--quiz URL] [--accroche "Une ligne"] [--controle] [--remplacer]

  DOSSIER      dossier du TD, créé s'il n'existe pas (ex. nsi1/fichiers/boucles-td1) ; le script y écrit index.html
  --id         identifiant unique et stable (minuscules, chiffres, tirets), ex. nsi1-boucles-td1
  --titre      le titre ; `for` entre accents graves devient du code
  --niveau     ex. « SNT », « 1re NSI », « Tle NSI »
  --chapitre   ex. « Programmer en Python »
  --bandeau    1 : le cône et la baie · 2 : l'îlot et le lagon · 3 : la ville et la barge · 4 : le baobab
  --quiz       adresse du cours-quiz du chapitre (QR code fabriqué ici, hors ligne) ; sans --quiz, pas de QR code
  --accroche   une ligne sous le titre (facultatif)
  --controle   bandeau de 20 mm et puce « Contrôle » (le margouillat va alors sur le mémo ou le pied)
  --remplacer  écrase un index.html existant
  --cachette   force la cachette du margouillat (ex. b2, memo, pied) ; sinon elle vient de l'identifiant

Le margouillat est placé d'après l'identifiant (empreinte SHA-256) : une des quatre cachettes du
bandeau, ou le cadre du mémo, ou le trait du pied de page ; le script évite une cachette déjà prise
par un autre TD du dépôt qui a le même bandeau, tant qu'il en reste une libre.
Le QR code est calculé avec assets/qrcode-generator.js (Node), sans aucun service en ligne.
"""
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
MODELE = os.path.join(ICI, "gabarit-td", "modele.html")
DEPOT = "https://github.com/babash/Babash-NSI-SNT/tree/main/"
NOMS = {1: "le cône et la baie", 2: "l'îlot et le lagon", 3: "la ville et la barge", 4: "le baobab"}


def qr_svg(url):
    """Matrice du QR code (correction M) calculée par assets/qrcode-generator.js, puis un seul chemin SVG."""
    lib = os.path.join(RACINE, "assets", "qrcode-generator.js")
    js = ("const q=require(process.argv[1]);const r=q(0,'M');r.addData(process.argv[2]);r.make();"
          "const n=r.getModuleCount(),m=[];for(let y=0;y<n;y++){let l='';for(let x=0;x<n;x++)l+=r.isDark(y,x)?'1':'0';m.push(l)}"
          "console.log(JSON.stringify(m))")
    try:
        sortie = subprocess.run(["node", "-e", js, lib, url], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f"QR code impossible (Node est-il installé ?) : {e}")
    m = json.loads(sortie)
    n = len(m)
    d = []
    for y, ligne in enumerate(m):
        for x0, bloc in ((mt.start(), len(mt.group())) for mt in re.finditer("1+", ligne)):
            d.append(f"M{x0} {y}h{bloc}v1h-{bloc}z")
    q = 2   # zone calme, en modules (le cadre blanc ajoute le reste)
    return (f'<svg viewBox="-{q} -{q} {n + 2 * q} {n + 2 * q}" shape-rendering="crispEdges" aria-hidden="true">'
            f'<path d="{"".join(d)}" fill="#121016"/></svg>')


def cachettes_prises(bandeau, sauf):
    """Cachettes déjà utilisées par les autres TD du dépôt qui ont le même bandeau."""
    prises = set()
    for dossier, _, fichiers in os.walk(RACINE):
        if "/.git" in dossier or "/node_modules" in dossier:
            continue
        for f in fichiers:
            if not f.endswith(".html"):
                continue
            chemin = os.path.join(dossier, f)
            if os.path.abspath(chemin) == os.path.abspath(sauf):
                continue
            try:
                t = open(chemin, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            if f'data-bandeau="{bandeau}"' in t and "{{" not in t:
                prises.update(re.findall(r'data-cachette="([a-z0-9-]+)"', t))
    return prises


def choisir_cachette(ident, bandeau, prises, forcee=None, controle=False):
    places = json.load(open(os.path.join(RACINE, "assets", "td", "places-margouillat.json"), encoding="utf-8"))
    # le bandeau de 20 mm (contrôle) n'a pas de cachette : le margouillat va sur le mémo ou le pied
    noms = ([] if controle else [f"b{i + 1}" for i in range(len(places[str(bandeau)]))]) + ["memo", "pied"]
    h = int(hashlib.sha256(ident.encode()).hexdigest(), 16)
    ordre = [noms[(h + k) % len(noms)] for k in range(len(noms))]
    nom = forcee or next((c for c in ordre if c not in prises), ordre[0])
    miroir = -1 if (h >> 8) % 2 else 1
    if nom.startswith("b"):
        p = places[str(bandeau)][int(nom[1:]) - 1]
        style = f'--x:{p["x"]}%;--y:{p["y"]}%;--r:{p["r"]}deg;--l:{p["l"]}%;--s:{miroir}'
    elif nom == "memo":
        style = f'--r:{[-6, 4, 8][h % 3]}deg;--s:{miroir}'
    else:
        style = f'--x:{40 + h % 45}%;--r:{[-3, 2, 5][h % 3]}deg;--s:{miroir}'
    return nom, f'<span class="td-margouillat" data-cachette="{nom}" style="{style}"></span>'


def titre_html(t):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(t, quote=False))


def main():
    a = argparse.ArgumentParser(description="Crée le squelette d'un TD en ligne (style Signal pirate).")
    a.add_argument("dossier")
    a.add_argument("--id", required=True)
    a.add_argument("--titre", required=True)
    a.add_argument("--niveau", required=True)
    a.add_argument("--chapitre", required=True)
    a.add_argument("--bandeau", type=int, choices=(1, 2, 3, 4), required=True)
    a.add_argument("--quiz")
    a.add_argument("--accroche")
    a.add_argument("--controle", action="store_true")
    a.add_argument("--remplacer", action="store_true")
    a.add_argument("--cachette")
    o = a.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", o.id):
        sys.exit("--id : minuscules, chiffres et tirets seulement (ex. nsi1-boucles-td1).")
    if o.quiz and not re.match(r"https://", o.quiz):
        sys.exit("--quiz : une adresse complète en https://")
    dossier = os.path.abspath(o.dossier)
    cible = os.path.join(dossier, "index.html")
    if os.path.exists(cible) and not o.remplacer:
        sys.exit(f"{cible} existe déjà (--remplacer pour l'écraser).")
    os.makedirs(dossier, exist_ok=True)

    assets = os.path.relpath(os.path.join(RACINE, "assets"), dossier).replace(os.sep, "/")
    chemin_depot = os.path.relpath(dossier, RACINE).replace(os.sep, "/")
    nom, marg = choisir_cachette(o.id, o.bandeau, cachettes_prises(o.bandeau, cible), o.cachette, o.controle)
    titre_txt = o.titre.replace("`", "")
    qr = ""
    if o.quiz:
        u = html.escape(o.quiz)
        qr = (f'<a class="td-qr" href="{u}" aria-label="Le cours-quiz du chapitre (QR code)">'
              f'{qr_svg(o.quiz)}<span>Cours-quiz</span></a>')
    remplacements = {
        "ID": o.id,
        "TITRE_TEXTE": html.escape(titre_txt),
        "TITRE_HTML": titre_html(o.titre),
        "DESCRIPTION": html.escape(f"TD en ligne auto-correctif : {titre_txt} ({o.niveau}, {o.chapitre})."),
        "NIVEAU": html.escape(o.niveau),
        "CHAPITRE": html.escape(o.chapitre),
        "BANDEAU": str(o.bandeau),
        "CLASSE_CONTROLE": " td-controle" if o.controle else "",
        "PUCE": "Contrôle" if o.controle else "TD",
        "ASSETS": assets,
        "ACCROCHE": f'<p class="td-accroche">{html.escape(o.accroche)}</p>' if o.accroche else "",
        "QR": qr,
        "MARG_BANDEAU": marg if nom.startswith("b") else "",
        "MARG_MEMO": marg if nom == "memo" else "",
        "MARG_PIED": marg if nom == "pied" else "",
        "DEPOT": DEPOT + chemin_depot,
    }
    t = open(MODELE, encoding="utf-8").read()
    # le commentaire d'en-tête du modèle ne parle qu'au modèle : la page générée garde les autres
    t = re.sub(r"<!--\n  GABARIT.*?-->\n", "<!-- TD créé par charte/nouveau-td.py ; mode d'emploi : charte/gabarit-td/LISEZMOI.md -->\n", t, count=1, flags=re.S)
    for k, v in remplacements.items():
        t = t.replace("{{" + k + "}}", v)
    reste = re.findall(r"\{\{[A-Z_]+\}\}", t)
    if reste:
        sys.exit(f"Modèle : champs non remplacés {reste}")
    open(cible, "w", encoding="utf-8").write(t)
    print(f"{os.path.relpath(cible, RACINE)} : bandeau {o.bandeau} ({NOMS[o.bandeau]}), margouillat « {nom} », "
          + ("QR code du cours-quiz" if o.quiz else "sans QR code (pas de cours-quiz)"))


if __name__ == "__main__":
    main()
