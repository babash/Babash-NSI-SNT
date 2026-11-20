# -*- coding: utf-8 -*-
"""Construit annales-bac-nsi.json à partir de donnees_brutes.py et du thésaurus des notions (lecture seule)."""
import json, re, sys, unicodedata, os
sys.path.insert(0, os.path.dirname(__file__))
import donnees_brutes as D

RACINE = sys.argv[1]            # racine du dépôt (copie de travail)
SORTIE = sys.argv[2]
notions = {n["id"]: n for n in json.load(open(os.path.join(RACINE, "donnees/referentiels/notions.json"), encoding="utf-8"))["notions"]}

def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").replace("’", "'")

# (motif regex sur le texte normalisé, notions)
REGLES = [
 (r"recursiv|recursion", ["prog.recursivite"]),
 (r"\bpoo\b|programmation orientee? objets?|programmation objet|classes?\b|\bobjets?\b|constructeur|methodes? de classe", ["prog.poo"]),
 (r"arbres? binaires? de recherche|\babr\b", ["donnees.arbre.abr", "algo.arbre"]),
 (r"\barbres?\b", ["donnees.arbre"]),
 (r"arbres? (binaires?|n-aires?)|parcours (infixe|prefixe|suffixe)|\barbre\b.*parcours", ["algo.arbre"]),
 (r"\bpiles?\b", ["donnees.pile"]),
 (r"\bfiles?\b(?! d'attente)|\bfifo\b|file a priorite|files d'attente", ["donnees.file"]),
 (r"listes? chainees?", ["donnees.liste.chainee"]),
 (r"\blistes?\b|tableaux?|listes de listes", ["donnees.tableau"]),
 (r"dictionnaires?", ["donnees.dictionnaire"]),
 (r"p-?uplets?|tuples?", ["donnees.tuple"]),
 (r"graphes?", ["donnees.graphe", "algo.graphe"]),
 (r"(parcours|parcours de graphe).*largeur|en largeur", ["algo.graphe.largeur"]),
 (r"en profondeur|parcours.*profondeur", ["algo.graphe.profondeur"]),
 (r"plus court chemin|bellman|dijkstra", ["algo.graphe.plus-court-chemin"]),
 (r"\bsql\b|bases? de donnees|schema relationnel|modele relationnel|cles? primaires?|sgbd", ["donnees.bdd", "donnees.bdd.relationnel"]),
 (r"\bsql\b|select|requetes?", ["donnees.bdd.sql"]),
 (r"select|interrogation|where|order by|count|agregation", ["donnees.bdd.sql.interrogation"]),
 (r"\bjoin\b|jointures?", ["donnees.bdd.sql.jointure"]),
 (r"\binsert\b|\bupdate\b|\bdelete\b|mise a jour|insertion|suppression", ["donnees.bdd.sql.mise-a-jour"]),
 (r"routage|\brip\b|\bospf\b|tables? de routage", ["reseau.routage"]),
 (r"\brip\b", ["reseau.routage.rip"]),
 (r"\bospf\b", ["reseau.routage.ospf"]),
 (r"\bip\b|ipv4|\bcidr\b|masques?|adressage", ["reseau.adresse-ip"]),
 (r"reseaux?|protocoles? (reseau|de communication)|dhcp|passerelle", ["reseau"]),
 (r"\bdns\b", ["reseau.dns"]),
 (r"https?\b|formulaires? web", ["web.http"]),
 (r"processus", ["archi.os.processus"]),
 (r"ordonnanc|tourniquet", ["archi.os.ordonnancement"]),
 (r"interblocage", ["archi.os.interblocage"]),
 (r"linux|unix|ligne de commande|commandes?\b", ["archi.os.ligne-commande"]),
 (r"droits (de fichiers|d'acces)|permissions|chmod|arborescence|systemes? de fichiers", ["archi.os.fichiers"]),
 (r"systemes? d'exploitation|\bos\b", ["archi.os"]),
 (r"systemes? sur puces?|\bsoc\b", ["archi.soc"]),
 (r"von neumann", ["archi.von-neumann"]),
 (r"assembleur|langage machine|risc-?v", ["archi.langage-machine"]),
 (r"portes? logiques?", ["archi.portes-logiques"]),
 (r"chiffrement|cryptograph|securisation|securite des communications|signature numerique|\bhttps\b|masque jetable|polybe|playfair|empreintes?", ["secu.chiffrement"]),
 (r"decidabilite|probleme de l'arret", ["prog.calculabilite"]),
 (r"diviser[- ]pour[- ]regner", ["algo.diviser-regner"]),
 (r"programmation dynamique", ["algo.programmation-dynamique"]),
 (r"gloutons?", ["algo.glouton"]),
 (r"tri fusion|fusion\b.*tri|tris? par insertion|tri par insertion", ["algo.tri"]),
 (r"tri fusion", ["algo.tri.fusion"]),
 (r"par insertion", ["algo.tri.insertion"]),
 (r"tris? par selection|tri par selection", ["algo.tri.selection"]),
 (r"\btris?\b|stooge|tri par comptage", ["algo.tri"]),
 (r"topologique", ["algo.graphe"]),
 (r"dichotom", ["algo.recherche.dichotomique"]),
 (r"recherche textuelle|boyer|recherche de motif", ["algo.recherche.textuelle"]),
 (r"recherche exhaustive|recherche d'un", ["algo.recherche"]),
 (r"complexite|cout (en temps|d'un algorithme|temporel)|pire des cas", ["algo.complexite"]),
 (r"binaires?(?! de recherche)(?<!arbre binaire)(?<!arbres binaires)|numeration|base 20|ecriture binaire|conversion|bits?\b|xor|et bit a bit", ["donnees.binaire"]),
 (r"booleen|table de verite|\bxor\b|et logique|logique", ["donnees.booleen"]),
 (r"complement a deux|relatifs?", ["donnees.entiers-relatifs"]),
 (r"huffman|compression|shannon", ["donnees.compression"]),
 (r"ascii|unicode|codage des caracteres|iso 8859", ["donnees.texte"]),
 (r"chaines? de caracteres|chaines\b", ["donnees.chaine"]),
 (r"\bcsv\b|donnees en tables?|traitement de donnees en tables?|tableaux? de dictionnaires", ["donnees.table.traitement"]),
 (r"modularite", ["prog.modularite"]),
 (r"\btests?\b|assert", ["prog.test"]),
 (r"bugs?|debogage|mise au point", ["prog.debogage"]),
 (r"specification|precondition", ["prog.specification"]),
 (r"perceptron|neurone|apprentissage supervise", ["ia.reseau-neurones", "ia.apprentissage"]),
 (r"k plus proches|\bknn\b", ["ia.knn"]),
 (r"automates? cellulaires?|jeu de la vie", ["algo.simulation"]),
 (r"images?|\brgb\b|rvb|couleurs?", ["donnees.image"]),
 (r"interface|implementation", ["donnees.interface-implementation"]),
 (r"base d'abord", []),
]
# règles à ne pas appliquer à certains termes (ex. « arbres binaires » ne doit pas donner « donnees.binaire »)
def notions_de(texte):
    t = norm(texte)
    t_bin = re.sub(r"arbres? binaires?( de recherche)?", " arbre ", t)
    t_bin = re.sub(r"parcours (infixe|prefixe|suffixe)", " parcours ", t_bin)
    # faux amis (T119) : retirés du texte avant la recherche des mots, pour que la règle visée ne s'applique pas
    #  - « insertion » dans un tri ou dans un ABR n'est pas une requête SQL INSERT ;
    #  - « listes d'adjacence » ne sont pas des tableaux ; « tri topologique » n'est pas un tri de liste.
    t_sql = re.sub(r"tris? par insertion|abr insertion|insertions? (dans|d'un|d'une|de) (un |une |l')?(abr|arbre)", " ", t)
    t_tab = re.sub(r"(dictionnaires? de )?listes? d'adjacence", " ", t)
    t_tri = re.sub(r"tris? topologiques?", " ", t)
    res = []
    for motif, ids in REGLES:
        cible = t_bin if "binaires?(?! de" in motif else t
        if "mise a jour|insertion" in motif: cible = t_sql
        elif motif.startswith(r"\blistes?\b|tableaux?"): cible = t_tab
        elif motif.startswith(r"\btris?\b|stooge"): cible = t_tri
        if re.search(motif, cible):
            for i in ids:
                if i not in res: res.append(i)
    # un parcours en largeur d'un arbre n'est pas un parcours de graphe (T119)
    if "algo.graphe.largeur" in res and "graphe" not in t and re.search(r"\barbres?\b|\babr\b", t):
        res = [i for i in res if i != "algo.graphe.largeur"]
        if "algo.arbre" not in res: res.append("algo.arbre")
    # cohérences
    if "donnees.arbre.abr" in res and "donnees.arbre" not in res: res.append("donnees.arbre")
    if "donnees.bdd.sql" in res and "donnees.bdd" not in res: res += ["donnees.bdd", "donnees.bdd.relationnel"]
    # on garde la notion la plus précise : un parent est retiré si un de ses descendants est présent
    res = [i for i in res if not any(j != i and j.startswith(i + ".") for j in res)]
    if not res: res = ["prog"]
    # supprime les parents redondants gardés seuls si un fils est présent (on garde les deux : le thésaurus accepte les deux niveaux)
    for i in res:
        if i not in notions: raise SystemExit(f"notion inconnue : {i}")
    return res

def themes_bo(ids):
    s = set()
    for i in ids:
        for p in notions[i].get("programme") or []:
            m = re.match(r"nsi-tle-2019\.([a-z\-]+)", p)
            if m: s.add(m.group(1))
    return sorted(s)

def lien(url, source, verifie, role):
    return {"url": url, "source": source, "etat": verifie, "verifie_le": D.V if verifie.startswith("ok") else None}

sujets = []
for s in D.SUJETS:
    l = s["liens"]
    out = {"id": s["cle"], "annee": s["annee"], "session": s["session"], "centre": s["centre"], "jour": s["jour"],
           "date_epreuve": s["date"], "code_officiel": s["code"], "duree": "3 h 30", "bareme_ecrit": int(s["bareme"]),
           "pages": s["pages"], "mise_en_page_des_pages": s["mise_en_page"]}
    if "pages_aeif" in l: out["pages_pdf_aeif"] = l["pages_aeif"]
    if s["annee"] >= 2024: out["structure"] = "3 exercices obligatoires (6, 6 et 8 points)"
    elif s["annee"] == 2023: out["structure"] = "3 exercices obligatoires, 12 points"
    else: out["structure"] = "5 exercices, 3 à traiter au choix (4 points chacun, 12 points)"
    ex = []
    for k, (pts, pg, th) in enumerate(s["exercices"], 1):
        n = notions_de(th)
        ex.append({"n": k, "points": pts, "pages": ([int(x) for x in pg.split("-")] if pg else None),
                   "resume": th, "notions": n, "themes_programme": themes_bo(n)})
    out["exercices"] = ex
    liens = {}
    alt = []
    if "kxs" in l and l["kxs"]:
        su, co = l["kxs"]
        liens["sujet_kxs"] = lien(su, "kxs.fr", "ok", "sujet")
        # état du sujet kxs : ok (PDF ouvert) ; image si scan
        slug = su.split(f"terminale-{s['annee']}-")[-1][:-4]
        if (s["annee"], slug) in D.KXS_SCAN: liens["sujet_kxs"]["etat"] = "ok (PDF image : texte non extractible, pages et points non relus)"
        else: liens["sujet_kxs"]["etat"] = "ok"
        liens["sujet_kxs"]["verifie_le"] = D.V
        if co: liens["corrige_kxs"] = lien(co, "kxs.fr (corrigé non officiel)", "ok", "corrige")
    if "aeif" in l and l["aeif"]:
        su, co, t = l["aeif"]
        liens["sujet_aeif"] = lien(su, "aeif.fr", "ok" if t == "ok" else "non testé (listé par la page AEIF)", "sujet")
        if co: liens["corrige_aeif"] = lien(co, "aeif.fr (CC BY-SA 4.0 selon la page)", "ok" if t == "ok" else "non testé (listé par la page AEIF)", "corrige")
    for a in l.get("autres", []):
        nom, u, role, etat = a
        alt.append({"source": nom, "role": role, "url": u, "etat": etat, "verifie_le": D.V if etat.startswith("ok") else None})
    if alt: liens["autres"] = alt
    out["liens"] = liens
    out["principal"] = ("sujet_aeif" if ("sujet_kxs" not in liens) else "sujet_kxs")
    if s["remarque"]: out["remarque"] = s["remarque"]
    sujets.append(out)

index = {}
for su in sujets:
    for e in su["exercices"]:
        for n in e["notions"]:
            index.setdefault(n, []).append(f"{su['id']}#{e['n']}")
ordre = lambda x: (-x["annee"], x["id"])
sujets.sort(key=ordre)

data = {
 "version": "2026-11-20",
 "tache": "T104",
 "description": "Inventaire des annales du baccalauréat de NSI (épreuve écrite de terminale depuis 2021, épreuve pratique), pour choisir des exercices par notion. On lie, on n'héberge pas.",
 "verifie_le": D.V,
 "prochaine_mise_a_jour": "2027-01-01",
 "methode_de_verification": "Chaque lien marqué « ok » a été ouvert le 20/11/2026 par l'outil de lecture du web de l'agent (le PDF ou la page est retourné). Ce n'est pas un contrôle de code HTTP : le réseau de la session bloque kxs.fr et la plupart des sites en accès direct. Les liens « non testé » sont listés par la page source mais n'ont pas été ouverts un par un. Les pages et les points sont lus dans le PDF par la même voie (relecture automatique : à contrôler avant d'imprimer).",
 "schema": {
   "notions": "identifiants de donnees/referentiels/notions.json (thésaurus validé le 13/11/2026)",
   "themes_programme": "thèmes du programme de terminale (nsi-tle-2019.<thème>) déduits des notions",
   "pages": "nombre de pages du PDF principal ; pages d'un exercice = [première, dernière] dans la mise en page indiquée",
 },
 "sources": [
   {"id": "kxs", "nom": "kxs.fr", "page": "https://kxs.fr/sujets/terminale-ecrit", "licence": "aucune mention sur la page ni dans les PDF ; la page précise : « Les corrigés et les barèmes ne sont pas officiels ! »", "couverture": "écrit 2021-2025 (pas encore 2026 le 20/11/2026) ; manque les sessions de 2025 hors Métropole, Amérique du Nord et Asie", "pratique": "https://kxs.fr/sujets/terminale-pratique"},
   {"id": "aeif", "nom": "AEIF (Association des enseignantes et enseignants d'informatique de France)", "page": "https://aeif.fr/index.php/annee-2026/", "pages_annuelles": ["https://aeif.fr/index.php/annee-2026/", "https://aeif.fr/index.php/annee-2025/", "https://aeif.fr/index.php/annales-2024/", "https://aeif.fr/index.php/annee-2023/", "https://aeif.fr/index.php/annee-2022/", "https://aeif.fr/index.php/annee-2021/"], "themes": "https://aeif.fr/index.php/themes-par-sujets/", "licence": "CC BY-SA 4.0 : « Tous les documents mis en téléchargement sur cette page sont sous licence CC BY-SA 4.0 » (relevé sur les pages annuelles 2021 à 2026, le 20/11/2026) ; copyright © 2026 AEIF en pied de page ; les énoncés officiels restent ceux du ministère", "couverture": "écrit 2021-2026, avec corrigés, sources LaTeX et sujets officiels numérisés (2021-2022)"},
   {"id": "math93", "nom": "Math93 (J. Courtois, F. Duffaud)", "page": "https://math93.com/index.php?option=com_content&view=article&id=1202&Itemid=1631", "licence": "non indiquée", "couverture": "écrit 2021-2026 ; corrigés détaillés"},
   {"id": "freemaths", "nom": "freemaths.fr", "page": "https://www.freemaths.fr/sujets-du-bac/baccalaureat-general/numerique-et-sciences-informatiques", "licence": "non indiquée (site commercial)", "couverture": "reprend les PDF officiels 2026 ; ses pages « 2027 » ne sont pas des sujets de session"},
   {"id": "eskool", "nom": "eSkool (Rodrigo Schwencke)", "page": "https://eskool.gitlab.io/tnsi/ressources/annales/epreuves_ecrites/", "licence": "CC BY-NC-SA 4.0 (annoncée par la page)", "couverture": "partielle : sujets 0 et 2021, 2026 Amérique du Nord (page mise à jour le 30/08/2026 d'après la page) ; renvoie à kxs, Pixees, sujetdebac, lewebpedagogique pour les corrigés"},
   {"id": "pixees", "nom": "Informatique au lycée (pixees.fr)", "page": "https://pixees.fr/informatiquelycee/term/suj_bac/", "licence": "non indiquée ; auteur non indiqué sur la page", "couverture": "2021-2023 (fichiers sujet_NN.pdf) et 2026 (sujet_N.pdf, numérotation non expliquée)"},
   {"id": "eduscol", "nom": "Éduscol / ministère de l'Éducation nationale", "page": "https://eduscol.education.fr/2661/banque-des-epreuves-pratiques-de-specialite-nsi", "licence": "à vérifier (les sujets sont publiés par le ministère ; aucune mention de licence lue)", "couverture": "banque nationale de l'épreuve pratique ; les sujets officiels de l'écrit n'ont pas pu être retrouvés sur le site institutionnel depuis la session (pages inaccessibles à l'agent)"},
 ],
 "epreuve_ecrite": {
   "index_par_notion": dict(sorted(index.items())),
   "formats": [
     {"sessions": "2021-2022", "structure": "5 exercices dont 3 à traiter au choix, 4 points chacun, 12 points au total, 3 h 30"},
     {"sessions": "2023", "structure": "3 exercices obligatoires, 12 points au total (3 à 6 points chacun), 3 h 30"},
     {"sessions": "2024-2026", "structure": "3 exercices obligatoires de 6, 6 et 8 points, 20 points au total, 3 h 30 (sujets 0 de 2024 inclus)"},
   ],
   "nombre_de_sujets": len(sujets),
   "sujets": sujets,
 },
}
THEMES_2026 = ["Codage RLE d'images","Analyse d'écart de salaires","Cycle menstruel","Agronomes","Empreinte carbone","Smoothies","Coccinelles","Addition BCD","Modélisation 3D","Compteur d'eau","Habitat pour renard","Refuge pour renards","Ballon sonde","Simulation d'évacuation","Vétérinaire","Warming stripes","Budget club de handball","Bouées océanographiques","Réservoirs d'eau","Empreinte carbone (2)","Cartes mémoire (flashcards)","QRcodes"]
def pr(annee, nombre, motif_sujet, motif_corrige, remarque, exemple):
    return {"annee": annee, "nombre_de_sujets_selon_kxs": nombre, "modele_url_sujet": motif_sujet, "modele_url_corrige": motif_corrige, "remarque": remarque, "lien_verifie": exemple}
data["epreuve_pratique"] = {
  "synthese": "Banque nationale de sujets : 2 exercices à traiter en 1 heure (sujets 2024 et 2025 relus : 2 exercices de 10 points, 20 points au total, 3 pages) ; le jury choisit le sujet de chaque candidat·e parmi ceux retenus par l'établissement (note de service du 19/11/2025 pour la session 2026 : note sur 20 au demi-point, commentaire qualitatif, banque en ligne au plus tard le 24 mars de la session). Format 2026 : sujets thématiques « BCG » (archives zip) ; à vérifier sur Éduscol. Une page de la presse spécialisée annonce un cadre fixé pour la partie pratique du bac 2027 : non relue.",
  "source_principale": {"id": "kxs", "page": "https://kxs.fr/sujets/terminale-pratique", "licence": "aucune mention", "origine_des_sujets": "eduscol.education.fr, banque des épreuves pratiques de spécialité NSI (https://eduscol.education.fr/2661/banque-des-epreuves-pratiques-de-specialite-nsi, page relue : mise à jour mars 2024, elle renvoie à la banque nationale)"},
  "autres_sources": [
    {"id": "ecebac", "page": "https://ecebac.fr/listaca.php?mat=94", "remarque": "déjà décrite par la fiche banque-epreuve-pratique-ecebac (session 2025) ; non relue ici"},
    {"id": "exomorphisme", "page": "https://exomorphisme.fr/", "remarque": "déjà décrite par la fiche epreuve-pratique-exomorphisme ; non relue ici"},
    {"id": "eskool-pratique", "page": "https://eskool.gitlab.io/tnsi/ressources/annales/epreuves_ecrites/", "remarque": "le menu de ce site annonce une page « Epreuves Pratiques CORRIGÉES » (adresse non relevée)"},
    {"id": "ac-bordeaux", "page": "https://ent2d.ac-bordeaux.fr/disciplines/nsi/2026/04/02/epreuve-pratique-nsi/", "remarque": "site académique de NSI ; indique que la banque a été mise à jour en mars 2026 (page non ouverte)"}],
  "banques": [
    pr(2026, 23, "https://kxs.fr/files/sujets/2026/pratique/26_BCG_NSI_{N}.zip", "https://kxs.fr/files/corriges/2026/pratique/sujet-{NN}/sujet-{NN}.pdf (et sujet-{NN}-practice.pdf pour l'entraînement de certains sujets)", "Le sujet 23 n'a ni lien ni thème sur la page kxs. Les corrigés kxs sont des pages web, pas des PDF.", "https://kxs.fr/files/sujets/2026/pratique/26_BCG_NSI_1.zip (réponse reçue, archive) ; https://kxs.fr/files/corriges/2026/pratique/sujet-01/sujet-01.pdf (lu : compression RLE, 4 questions)"),
    pr(2025, 48, "https://kxs.fr/files/sujets/2025/pratique/25-NSI-{NN}.pdf (et .py)", "https://kxs.fr/files/corriges/2025/pratique/sujet-{NN}.pdf", "Deux exercices par sujet, titrés sur la page kxs (ex. sujet 01 : prédécesseurs dans un graphe ; nombre suivant).", "https://kxs.fr/files/sujets/2025/pratique/25-NSI-01.pdf (lu : 3 pages, 1 h, 2 exercices de 10 points)"),
    pr(2024, 48, "https://kxs.fr/files/sujets/2024/pratique/24-NSI-{NN}.pdf (et .py)", "https://kxs.fr/files/corriges/2024/pratique/sujet-{NN}.pdf", "Deux exercices par sujet (ex. sujet 01 : taille d'un arbre binaire ; tri par sélection).", "https://kxs.fr/files/sujets/2024/pratique/24-NSI-01.pdf (lu : 3 pages, 1 h, 2 exercices de 10 points)"),
    pr(2023, 45, "https://kxs.fr/files/sujets/2023/pratique/23-NSI-{NN}.zip", "https://kxs.fr/files/corriges/2023/pratique/sujet-{N}.pdf (corrigés seulement pour les sujets 44 et 45 selon la page)", "Le nombre de sujets (45) est celui de la page kxs : à confronter à la banque officielle.", "https://kxs.fr/files/sujets/2023/pratique/23-NSI-01.zip (réponse reçue, archive)"),
    pr(2022, 40, "https://kxs.fr/files/sujets/2022/pratique/22_nsi_{NN}.zip", "https://kxs.fr/files/corriges/2022/pratique/sujets.pdf (fichier unique)", "Corrigés regroupés dans un seul fichier.", "https://kxs.fr/files/sujets/2022/pratique/22_nsi_01.zip (réponse reçue, archive)"),
    pr(2021, 30, "https://kxs.fr/files/sujets/2021/pratique/21_NSI_{NN}.zip", None, "Corrigés pour une partie seulement des sujets.", "https://kxs.fr/files/sujets/2021/pratique/21_NSI_01.zip (réponse reçue, archive)"),
  ],
  "themes_2026": [{"numero": i + 1, "theme": t} for i, t in enumerate(THEMES_2026)],
  "a_faire": "Pour un choix par notion, il faut lire les exercices de chaque sujet 2021-2025 (2 exercices par sujet, titres sur la page kxs) : non fait dans cette tâche (T104 demandait un inventaire plus court pour la pratique).",
}
data["a_trouver"] = [
  {"session": "Polynésie, juin 2026 (jours 1 et 2)", "etat": "sujets passés (AEIF les prévoit dans son tableau des thèmes) mais aucun PDF retrouvé au 20/11/2026"},
  {"session": "Métropole septembre 2026, Asie-Pacifique septembre 2026", "etat": "sessions annoncées par la page math93 (codes 26-NSIJ1ME3, 26-NSIJ2ME3, 26-NSIPE4) ; aucun sujet retrouvé"},
  {"session": "Amérique du Sud, novembre 2026 (13 et 14 novembre)", "etat": "session de la semaine du 13/11/2026 ; sujets non encore publiés par les sources consultées"},
  {"session": "Nouvelle-Calédonie, novembre 2026", "etat": "non annoncée par les sources consultées ; à rechercher"},
  {"session": "Sujets officiels sur eduscol / education.gouv.fr", "etat": "les pages institutionnelles n'ont pas pu être lues (accès refusé à l'agent) : le texte officiel de l'écrit n'est donc cité que par ses reprises (AEIF, kxs, math93, freemaths)"},
]
json.dump(data, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(sujets), "sujets")
