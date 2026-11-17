#!/usr/bin/env python3
"""Vérifie que le site s'affiche correctement.

Pour chaque rubrique de la vitrine (donnees/vitrine.json ; depuis T51b, les rubriques lisent la vitrine et les
fiches, et non plus les anciennes listes ressources.js) :
  - les fichiers locaux des fiches placées dans la rubrique (champ « fichier ») existent ;
  - la page, affichée dans Chrome sans écran, ne montre pas d'erreur ;
  - elle affiche autant de ressources que la vitrine en place, sans compter celles dont tous les documents
    sont cachés pour l'extérieur.
Pour toutes les fiches de la bibliothèque (donnees/ressources/*.json, constat N59) :
  - chaque document local (champ « fichier ») existe dans le dépôt et répond en ligne ;
  - chaque page HTML citée (fichier .html ou dossier) est affichée ; les pages des ressources mises en
    avant (« pages déposées ») et celles de toutes les fiches (« pages citées par les fiches ») sont
    comptées à part.
La bibliothèque (bibliotheque/, T50) : donnees/bibliotheque.json se lit en ligne et correspond aux
fiches visibles de l'extérieur de cette copie ; la page en affiche autant, sans erreur ; une recherche
trouve une ressource par un mot de son titre ; trois fiches complètes s'ouvrent (?r=identifiant).
Une page déposée vue vide est réaffichée deux fois, à 15 s d'intervalle, avant d'être déclarée
(constat N15) ; le journal donne, pour chaque page, la longueur du texte rendu.
Le lien « Code source sur GitHub » (décision de l'enseignant du 10/11/2026, 22:58) :
  - l'accueil, chaque rubrique et la bibliothèque : vers le dépôt de reglages.js (depot) ; s'il manque, échec ;
  - chaque page déposée citée par une fiche : vers un dépôt GitHub ;
    s'il manque, avertissement sans échec (une suite, pas un blocage) ; exceptions dans
    CODE_SOURCE_EXCEPTIONS.
Les pages sont affichées en parallèle (PARALLELE instances de Chrome) pour garder une durée
raisonnable.

Usage :  python3 .github/verifier-site.py https://babash.github.io/Babash-NSI-SNT
         python3 .github/verifier-site.py http://localhost:8000      (test local)
Variables d'environnement (pour les tests) : VERIFIER_ATTENTE (secondes entre deux essais
d'une page vue vide, 15 par défaut), VERIFIER_PARALLELE (nombre de Chrome en même temps).
"""
import concurrent.futures
import contextlib
import glob
import html
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESSAIS_PAGE = 3          # une page vue vide : le premier affichage, puis deux nouveaux essais (N15)
ATTENTE = float(os.environ.get("VERIFIER_ATTENTE", "15"))
PARALLELE = max(1, int(os.environ.get("VERIFIER_PARALLELE", "4")))
DELAI_CHROME = 120       # secondes, pour un affichage
TEXTE_MINIMUM = 80       # en dessous, une page est vue vide
ESSAIS_FICHIER = 3       # un fichier qui ne répond pas : redemandé, ATTENTE secondes plus tard


def lire(chemin):
    with open(os.path.join(RACINE, chemin), encoding="utf-8") as f:
        return f.read()


def vitrine():
    """Les rubriques de la vitrine : [(identifiant, [identifiants des ressources placées, dans l'ordre])]."""
    v = json.loads(lire("donnees/vitrine.json"))
    out = []
    for rub in v.get("rubriques", []):
        ids = []
        for s in rub.get("sections", []):
            ids += s.get("ressources", [])
            for ss in s.get("sous_sections", []):
                ids += ss.get("ressources", [])
        out.append((rub["id"], ids))
    return out


def fiche(rid):
    """La fiche d'une ressource, ou None si elle manque ou est illisible (scripts/valider_donnees.py le signale)."""
    try:
        return json.loads(lire(f"donnees/ressources/{rid}.json"))
    except (OSError, ValueError):
        return None


def visible_exterieur(f):
    return any(isinstance(d, dict) and (d.get("visible") or {}).get("exterieur") is True for d in f.get("documents", []))


DEPOT_PAR_DEFAUT = "babash/Babash-NSI-SNT"   # celui d'assets/site.js, si reglages.js n'en donne pas
# Pages déposées dispensées du lien, chacune avec sa raison : {"rubrique/fichiers/page.html": "raison"}.
# Vide : toutes les pages déposées sont des pages du site, Compute-it compris (avis du Gardien, N34).
CODE_SOURCE_EXCEPTIONS = {}


def depot():
    """Le dépôt de reglages.js, raccourci comme dans assets/site.js (« propriétaire/nom »).
    La valeur peut être entre guillemets doubles ou simples ; mal écrite ou absente, c'est le
    dépôt par défaut, comme dans assets/site.js (qui affiche alors une erreur sur la page)."""
    m = re.search(r"""^\s*["']?depot["']?\s*:\s*(["'])(.*?)\1""", lire("reglages.js"), re.M)
    valeur = m.group(2).strip() if m else ""
    valeur = re.sub(r"(\.git)?/*$", "", re.sub(r"^https?://(www\.)?github\.com/", "", valeur, flags=re.I))
    return valeur if re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9._-]+", valeur) else DEPOT_PAR_DEFAUT


def code_source(page):
    """Les adresses des liens « Code source sur GitHub » d'une page affichée (DOM de Chrome).
    Le texte du lien est décodé (&nbsp;, &#xA0;, &amp;…), ses balises (icône) retirées et ses
    espaces, insécables compris, ramenés à une espace."""
    trouves = []
    for attributs, contenu in re.findall(r"<a\b([^>]*)>(.*?)</a>", page, re.S | re.I):
        texte = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", contenu))).strip()
        href = re.search(r"""\bhref\s*=\s*(["'])(.*?)\1""", attributs, re.S)
        adresse = html.unescape(href.group(2)).strip() if href else ""
        if texte.lower() == "code source sur github" and adresse.startswith("https://github.com/"):
            trouves.append(adresse.split("#")[0].split("?")[0].rstrip("/"))
    return trouves


def est_page(chemin):
    """Une page HTML : un fichier .html ou .htm, ou un dossier (servi par son index.html)."""
    return chemin.endswith((".html", ".htm", "/")) or os.path.isdir(os.path.join(RACINE, chemin))


def documents_des_fiches(problemes):
    """{chemin depuis la racine : [identifiants des fiches qui le citent]} pour les documents
    locaux (champ « fichier ») de toutes les fiches, visibles ou non : tout fichier du dépôt est
    servi en ligne. Une fiche illisible est signalée, jamais sautée sans bruit."""
    cites = {}
    for chemin in sorted(glob.glob(os.path.join(RACINE, "donnees", "ressources", "*.json"))):
        nom = os.path.relpath(chemin, RACINE)
        try:
            with open(chemin, encoding="utf-8") as f:
                fiche = json.load(f)
        except (OSError, ValueError) as e:
            problemes.append(f"{nom} : fiche illisible ({e})")
            continue
        documents = fiche.get("documents") if isinstance(fiche, dict) else None
        for doc in documents if isinstance(documents, list) else []:
            fichier = doc.get("fichier") if isinstance(doc, dict) else None
            if isinstance(fichier, str) and fichier.strip():
                fichier = re.split(r"[#?]", fichier.strip())[0]
                cites.setdefault(fichier, []).append(fiche.get("id") or os.path.basename(chemin)[:-5])
    return cites


def chrome():
    for nom in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(nom):
            return nom
    sys.exit("Chrome est introuvable.")


def afficher(url):
    """Le DOM de la page, affichée dans Chrome sans écran (texte vide si Chrome ne répond pas en
    DELAI_CHROME secondes). Plusieurs Chrome peuvent tourner en même temps avec le profil par
    défaut ; un profil neuf (--user-data-dir) bloque le premier lancement quand le réseau est
    filtré : on ne l'utilise pas. À l'expiration du délai, tous les processus de ce Chrome sont
    arrêtés, pour qu'aucun ne reste après le contrôle."""
    processus = subprocess.Popen(
        [chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
         "--virtual-time-budget=20000", "--dump-dom", url],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, start_new_session=True,
    )
    try:
        sortie, _ = processus.communicate(timeout=DELAI_CHROME)
        return sortie
    except subprocess.TimeoutExpired:
        with contextlib.suppress(OSError):
            os.killpg(processus.pid, signal.SIGKILL)
        processus.communicate()
        return ""


def texte_rendu(page):
    """Le texte de la page, sans scripts ni styles ; le titre compte, comme avant N15 (un projet
    de départ vide à dessein, comme celui du TP des donuts, n'a guère que son titre et son pied)."""
    corps = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps))).strip()


def page_vide(page):
    return len(texte_rendu(page)) < TEXTE_MINIMUM or bool(re.search(r"<title>[^<]*(404|not found)", page, re.I))


def afficher_page_deposee(url):
    """(page, nombre d'essais, longueurs du texte rendu à chaque essai). Une page vue vide est
    réaffichée, ATTENTE secondes plus tard, jusqu'à ESSAIS_PAGE affichages en tout (N15)."""
    longueurs = []
    for essai in range(1, ESSAIS_PAGE + 1):
        page = afficher(url)
        longueurs.append(len(texte_rendu(page)))
        if not page_vide(page) or essai == ESSAIS_PAGE:
            return page, essai, longueurs
        time.sleep(ATTENTE)


def demander(url):
    """Le code HTTP du fichier en ligne (0 si aucune réponse), avec ESSAIS_FICHIER essais."""
    code = 0
    for essai in range(1, ESSAIS_FICHIER + 1):
        requete = urllib.request.Request(url, headers={"User-Agent": "verifier-site (GitHub Actions)"})
        try:
            with urllib.request.urlopen(requete, timeout=60) as reponse:
                reponse.read(1024)
                return reponse.status
        except urllib.error.HTTPError as e:
            code = e.code
        except (urllib.error.URLError, OSError):
            code = 0
        if essai < ESSAIS_FICHIER:
            time.sleep(ATTENTE)
    return code


def adresse(base, chemin):
    return f"{base}/{urllib.parse.quote(chemin, safe='/')}"


def fiches_publiques():
    """Les fiches de cette copie qui ont au moins un document visible de l'extérieur (cahier des charges, § 3.2),
    triées par identifiant : ce que la bibliothèque en ligne doit montrer."""
    out = []
    for chemin in sorted(glob.glob(os.path.join(RACINE, "donnees", "ressources", "*.json"))):
        try:
            with open(chemin, encoding="utf-8") as f:
                fiche = json.load(f)
        except (OSError, ValueError):
            continue  # une fiche illisible est signalée par scripts/valider_donnees.py
        if any(isinstance(d, dict) and (d.get("visible") or {}).get("exterieur") is True for d in fiche.get("documents", [])):
            out.append(fiche)
    return sorted(out, key=lambda f: f.get("id", ""))


def bibliotheque(base, problemes, lien_du_site):
    """La page bibliotheque/ (T50) : les données construites à la publication se lisent en ligne et
    correspondent aux fiches de cette copie ; la page affiche autant de ressources, sans erreur, avec le lien
    « Code source sur GitHub » ; une recherche trouve une ressource par un mot de son titre ; la fiche
    complète de trois ressources s'ouvre (?r=identifiant)."""
    fiches = fiches_publiques()
    if not fiches:
        print(f"{'bibliothèque':15} pas encore de fiches dans donnees/ressources/ : rien à vérifier")
        return
    try:
        with urllib.request.urlopen(f"{base}/donnees/bibliotheque.json", timeout=60) as r:
            en_ligne = json.loads(r.read().decode("utf-8"))
        ids = sorted(x.get("id") for x in en_ligne.get("ressources", []))
    except (OSError, ValueError) as e:
        problemes.append(f"bibliothèque : donnees/bibliotheque.json illisible en ligne ({e}). Il est construit par le "
                         "workflow « Publier le site » : la source de GitHub Pages est-elle bien « GitHub Actions » ? "
                         "Sur une copie locale, le construire d'abord : python3 scripts/construire_bibliotheque.py")
        return
    attendus = [f["id"] for f in fiches]
    if ids != attendus:
        manquent = sorted(set(attendus) - set(ids))
        en_trop = sorted(set(ids) - set(attendus))
        problemes.append("bibliothèque : bibliotheque.json en ligne ne correspond pas aux fiches"
                         + (f" ; manquent : {', '.join(manquent[:5])}" if manquent else "")
                         + (f" ; en trop : {', '.join(en_trop[:5])}" if en_trop else ""))

    page = afficher(f"{base}/bibliotheque/")
    m = re.search(r'class="compte">(\d+) ressources?<', page)
    affiche = int(m.group(1)) if m else None
    if 'class="alerte"' in page:
        problemes.append("bibliothèque : la page affiche une erreur")
    if affiche != len(attendus):
        problemes.append(f"bibliothèque : {affiche if affiche is not None else 'aucune'} ressource(s) affichée(s) "
                         f"au lieu de {len(attendus)}")
    lien_du_site("bibliothèque", page)
    print(f"{'bibliothèque':15} {affiche if affiche is not None else '—':>3} ressources affichées / {len(attendus):3} fiches visibles de l'extérieur")

    # Une recherche : le premier mot assez long du titre d'une ressource la trouve
    for f in fiches:
        mots = [x for x in re.findall(r"[^\W\d_]{6,}", f.get("titre", ""))]
        if mots:
            page = afficher(f"{base}/bibliotheque/?q={urllib.parse.quote(mots[0])}")
            m = re.search(r'class="compte">(\d+) ressources?<', page)
            if not m or int(m.group(1)) < 1 or "r=" + urllib.parse.quote(f["id"]) not in page:
                problemes.append(f"bibliothèque : la recherche « {mots[0]} » ne trouve pas « {f['titre']} »")
            else:
                print(f"{'':15} recherche « {mots[0]} » : {m.group(1)} ressource(s), dont « {f['titre'][:40]} »")
            break

    # La fiche complète : la première, celle du milieu et la dernière
    for f in {x["id"]: x for x in (fiches[0], fiches[len(fiches) // 2], fiches[-1])}.values():
        page = afficher(f"{base}/bibliotheque/?r={urllib.parse.quote(f['id'])}")
        titre = html.escape(f.get("titre", ""), quote=False)
        if 'class="fiche-titre"' not in page or titre not in page or 'class="alerte"' in page:
            problemes.append(f"bibliothèque : la fiche complète de « {f['id']} » ne s'affiche pas")
        else:
            print(f"{'':15} fiche « {f['id']} » : ok")


def main():
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://babash.github.io/Babash-NSI-SNT"
    debut = time.time()
    problemes = []
    total = 0
    pages_internes = set()          # pages déposées des ressources mises en avant (vitrine)
    fichiers_listes = set()         # tous leurs fichiers locaux visibles de l'extérieur
    depot_site = "https://github.com/" + depot()

    def lien_du_site(nom, page):
        # Dans le pied de page : une ressource peut avoir un document « Code source sur GitHub » (T51b)
        pieds = re.findall(r"<footer\b.*?</footer>", page, re.S | re.I)
        liens = code_source(" ".join(pieds) if pieds else page)
        if depot_site.lower() not in [lien.lower() for lien in liens]:   # GitHub ignore la casse
            problemes.append(f"{nom} : pas de lien « Code source sur GitHub » vers {depot_site}"
                             + (f" (liens trouvés : {', '.join(liens)})" if liens else ""))

    # Les pages des rubriques et l'accueil, en parallèle ; les résultats sont lus dans l'ordre.
    with concurrent.futures.ThreadPoolExecutor(PARALLELE) as pool:
        places = vitrine()
        vues = {rub: pool.submit(afficher, f"{base}/{rub}/") for rub, _ in places}
        vue_accueil = pool.submit(afficher, f"{base}/")

        for rub, ids in places:
            vue = vues[rub]
            fiches = [f for f in (fiche(rid) for rid in ids) if f]
            if len(fiches) < len(ids):
                problemes.append(f"{rub} : {len(ids) - len(fiches)} ressource(s) de la vitrine sans fiche lisible")
            attendu = sum(1 for f in fiches if visible_exterieur(f))
            total += attendu

            # Les fichiers déposés sur le site par les ressources mises en avant (documents visibles de l'extérieur)
            for f in fiches:
                for d in f.get("documents", []):
                    if not isinstance(d, dict) or not isinstance(d.get("fichier"), str) or not (d.get("visible") or {}).get("exterieur"):
                        continue
                    fichier = re.split(r"[#?]", d["fichier"])[0]
                    if not os.path.exists(os.path.join(RACINE, fichier)):
                        problemes.append(f"{rub} : le fichier {fichier} (fiche {f.get('id')}) n'existe pas")
                        continue
                    if os.path.isdir(os.path.join(RACINE, fichier)) and not fichier.endswith("/"):
                        fichier += "/"
                    fichiers_listes.add(fichier)
                    if fichier.endswith((".html", ".htm", "/")):
                        pages_internes.add(fichier)

            page = vue.result()
            if 'class="alerte"' in page:
                problemes.append(f"{rub} : la page affiche une erreur")
            affiche = page.count('<li class="res"')
            etat = "ok" if affiche == attendu else "ÉCART"
            print(f"{rub:15} {affiche:3} ressources affichées / {attendu:3} dans la vitrine   {etat}")
            if affiche != attendu:
                problemes.append(f"{rub} : {affiche} ressources affichées au lieu de {attendu}")
            lien_du_site(rub, page)

        accueil = vue_accueil.result()
    erreur_accueil = 'class="alerte"' in accueil
    if erreur_accueil:
        problemes.append("accueil : la page affiche une erreur")
    lien_du_site("accueil", accueil)
    print(f"{'accueil':15} {'erreur' if erreur_accueil else 'ok'}")
    print(f"Total : {total} ressources")

    # Les documents locaux des fiches de la bibliothèque (N59).
    cites = documents_des_fiches(problemes)
    fichiers_fiches = set()
    for chemin, fiches in sorted(cites.items()):
        if os.path.isdir(os.path.join(RACINE, chemin)):
            fichiers_fiches.add(chemin.rstrip("/") + "/")     # un dossier : servi par son index.html
        elif os.path.exists(os.path.join(RACINE, chemin)):
            fichiers_fiches.add(chemin)
        else:
            problemes.append(f"{chemin} : cité par la fiche {', '.join(fiches)}, mais absent du dépôt")
    pages_fiches = {c for c in fichiers_fiches if est_page(c)}
    aussi_listes = pages_fiches & pages_internes

    # Les fichiers qui ne sont pas des pages : demandés en ligne (code HTTP).
    autres = sorted({c for c in fichiers_listes | fichiers_fiches if not est_page(c)})
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        codes = dict(zip(autres, pool.map(lambda c: demander(adresse(base, c)), autres)))
    absents = [c for c in autres if not 200 <= codes[c] < 300]
    for chemin in absents:
        qui = f"cité par la fiche {', '.join(cites[chemin])}" if chemin in cites else "cité par une ressource mise en avant"
        raison = f"code {codes[chemin]}" if codes[chemin] else "aucune réponse"
        problemes.append(f"{chemin} : {qui}, ne répond pas en ligne ({raison})")
    print(f"Fichiers déposés (PDF, notebooks, code…) : {len(autres) - len(absents)} / {len(autres)} répondent en ligne")

    # Pages déposées sur le site (TD, fiches, diaporamas, applications) : elles doivent
    # s'afficher avec un vrai contenu, et non une page vide ou une erreur 404.
    a_afficher = sorted(pages_internes | pages_fiches)
    print(f"\nPages déposées : {len(pages_internes)} des ressources mises en avant, "
          f"{len(pages_fiches)} pages citées par les fiches"
          + (f" (dont {len(aussi_listes)} mises en avant)" if aussi_listes else "")
          + f" ; {len(a_afficher)} à afficher")
    vides, sans_code = set(), set()
    with concurrent.futures.ThreadPoolExecutor(PARALLELE) as pool:
        rendus = pool.map(lambda c: afficher_page_deposee(adresse(base, c)), a_afficher)
        for chemin, (page, essais, longueurs) in zip(a_afficher, rendus):
            vide = page_vide(page)
            essai_txt = "" if essais == 1 else f", {essais} essais ({' puis '.join(map(str, longueurs))})"
            if vide:
                vides.add(chemin)
                problemes.append(f"{chemin} : page vide ou introuvable après {essais} essais "
                                 f"(texte rendu : {longueurs[-1]} caractères)")
                etat = "VIDE"
            elif chemin not in CODE_SOURCE_EXCEPTIONS and not code_source(page):
                sans_code.add(chemin)   # une suite, pas un blocage (fiche du Gardien) : sans échec
                etat = "sans lien"
            else:
                etat = "ok"
            print(f"   {etat:9} {longueurs[-1]:7} caractères{essai_txt}   {chemin}")

    def bilan(groupe, nom):
        affichees = groupe - vides
        avec = affichees - sans_code
        print(f"Lien « Code source sur GitHub » : {len(avec)} / {len(affichees)} {nom}"
              + (f", {len(CODE_SOURCE_EXCEPTIONS)} dispensée(s)" if CODE_SOURCE_EXCEPTIONS else ""))
        return len(affichees)

    print(f"Pages déposées : {len(pages_internes - vides)} / {len(pages_internes)} s'affichent")
    print(f"Pages citées par les fiches : {len(pages_fiches - vides)} / {len(pages_fiches)} s'affichent")
    bilan(pages_internes, "pages déposées")
    bilan(pages_fiches, "pages citées par les fiches")
    if sans_code:
        print("À compléter (sans échec) : pas de lien « Code source sur GitHub » dans")
        for chemin in sorted(sans_code):
            print("   -", chemin)
        if os.environ.get("GITHUB_ACTIONS"):
            print("::warning title=Lien « Code source sur GitHub »::" + str(len(sans_code)) +
                  " page(s) déposée(s) sans le lien : " + ", ".join(sorted(sans_code)))

    bibliotheque(base, problemes, lien_du_site)
    print(f"Durée : {round(time.time() - debut)} s")

    if problemes:
        print("\nProblèmes :")
        for p in problemes:
            print(" -", p)
        sys.exit(1)
    print("\nTout s'affiche correctement.")


if __name__ == "__main__":
    main()
