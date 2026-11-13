#!/usr/bin/env python3
"""Tests du thésaurus des notions et du champ « notions » des fiches (T50a, T60, T64), et de la visibilité par défaut.

Usage (depuis la racine du dépôt) :
  python3 -I -B scripts/tests/test_notions.py [--racine DOSSIER_DU_DEPOT] [--travail DOSSIER] [--garder]

Chaque cas prépare une copie de travail : le dossier donnees/ est copié, le reste du dépôt est relié par des
liens symboliques (les fichiers déposés cités par les fiches restent ainsi trouvables, sans tout copier). Le cas
modifie la copie, lance scripts/valider_donnees.py du dépôt sur elle, et vérifie le code de retour et les lignes
attendues (ERREUR, ATTENTION ou INFO, sur le bon fichier). Les cas s'appuient sur la fiche d'exemple td1-poo et
sur des notions du thésaurus (prog.boucle, prog.boucle.bornee, prog.variable, geo.itineraire…) : les adapter si
elles changent. Les cas de l'option --avant comparent la copie à une version précédente du thésaurus, écrite dans
la copie (avant.json). Les cas de la conversion (T64) lancent scripts/convertir_notions_t64.py sur la copie.

Code de retour : 0 si tous les cas passent, 1 sinon. Python 3 standard, sans dépendance.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEFAUT = os.path.dirname(os.path.dirname(ICI))
FICHE = "donnees/ressources/td1-poo.json"
THESAURUS = "donnees/referentiels/notions.json"
VALEURS = "donnees/referentiels/valeurs.json"


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def ecrire(chemin, obj):
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


class Essai:
    def __init__(self, racine, garder, travail=None):
        self.racine = racine
        if travail:
            os.makedirs(travail, exist_ok=True)
        self.travail = tempfile.mkdtemp(prefix="test-notions-", dir=travail)
        self.garder = garder
        self.n = 0
        self.echecs = 0

    def copie(self):
        """Une copie de travail : donnees/ copié, tout le reste relié."""
        self.n += 1
        d = os.path.join(self.travail, f"cas-{self.n:02d}")
        os.makedirs(d)
        for nom in os.listdir(self.racine):
            if nom in (".git", "donnees"):
                continue
            os.symlink(os.path.join(self.racine, nom), os.path.join(d, nom))
        shutil.copytree(os.path.join(self.racine, "donnees"), os.path.join(d, "donnees"))
        return d

    def valider(self, d, options=()):
        r = subprocess.run([sys.executable, "-I", "-B", os.path.join(self.racine, "scripts", "valider_donnees.py"), "--racine", d]
                           + [o.replace("{copie}", d) for o in options],
                           capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def cas(self, titre, modifier, code, presents=(), absents=(), options=()):
        """presents, absents : (niveau, fichier, motif) ; niveau ERREUR, ATTENTION ou INFO.
        options : arguments de plus pour le validateur ; « {copie} » y désigne le dossier de la copie."""
        d = self.copie()
        pb = []
        try:
            modifier(d)
        except Exception as x:  # la préparation elle-même constate un problème
            pb.append(f"préparation : {x}")
        obtenu, sortie = self.valider(d, options)
        lignes = sortie.splitlines()
        if obtenu != code:
            pb.append(f"code {obtenu} au lieu de {code}")
        if "Bilan :" not in sortie:
            pb.append("la validation s'est arrêtée avant son bilan")

        def trouve(niveau, fichier, motif):
            return any(l.startswith(niveau) and fichier in l and re.search(motif, l) for l in lignes)

        pb += [f"aucune ligne {n} sur {f} ne correspond à « {m} »" for n, f, m in presents if not trouve(n, f, m)]
        pb += [f"ligne {n} en trop sur {f} : « {m} »" for n, f, m in absents if trouve(n, f, m)]
        if pb:
            self.echecs += 1
            print(f"  ÉCHEC  {titre}")
            for p in pb:
                print(f"         - {p}")
            print("         sortie : " + " / ".join(l for l in lignes if l[:6] in ("ERREUR", "ATTENT", "Bilan ")) [-1500:])
        else:
            print(f"  ok     {titre}")
            if not self.garder:
                shutil.rmtree(d, ignore_errors=True)

    def terminer(self):
        print(f"\n{self.n} cas, {self.echecs} échec(s)")
        if not self.echecs and not self.garder:
            shutil.rmtree(self.travail, ignore_errors=True)
        elif self.echecs:
            print(f"Copies gardées pour l'examen : {self.travail}")
        return 1 if self.echecs else 0


def fiche(f):
    """Modifier la fiche td1-poo de la copie."""
    def modifier(d):
        chemin = os.path.join(d, FICHE)
        x = lire(chemin)
        f(x)
        ecrire(chemin, x)
    return modifier


def thesaurus(f):
    """Modifier le thésaurus de la copie ; f reçoit le thésaurus et un accès aux notions par identifiant."""
    def modifier(d):
        chemin = os.path.join(d, THESAURUS)
        t = lire(chemin)
        par_id = {n["id"]: n for n in t["notions"]}
        f(t, par_id)
        ecrire(chemin, t)
    return modifier


def notions(**roles):
    return fiche(lambda x: x.__setitem__("notions", roles))


def avant(f=None):
    """Écrire dans la copie la version précédente du thésaurus (avant.json, telle quelle), puis modifier le thésaurus
    de la copie avec f, comme thesaurus()."""
    def modifier(d):
        shutil.copy(os.path.join(d, THESAURUS), os.path.join(d, "avant.json"))
        if f:
            thesaurus(f)(d)
    return modifier


def retirer_notion(nid):
    """Retirer une notion feuille, citée par aucune autre notion."""
    def f(t, n):
        t["notions"].remove(n[nid])
        for h in t.get("historique", []):
            for cle in ("ajoutees", "modifiees"):
                if nid in h.get(cle, []):
                    h[cle].remove(nid)
    return f


def convertir(d, attendu=0):
    """Lancer le script de conversion des notions (T64) sur la copie."""
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(d, "scripts", "convertir_notions_t64.py"), "--racine", d],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != attendu:
        raise AssertionError(f"conversion : code {r.returncode} au lieu de {attendu} : {(r.stdout + r.stderr)[-500:]}")
    return r.stdout


def nouvelle_notion(t, n):
    t["notions"].append({"id": "geo.essai", "libelle": "Notion d'essai", "plus_larges": ["geo"],
                         "note": "Une notion ajoutée pour le test."})


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--racine", default=RACINE_DEFAUT)
    p.add_argument("--garder", action="store_true", help="garder toutes les copies de travail")
    p.add_argument("--travail", help="dossier où créer les copies de travail (par défaut : le dossier temporaire du système)")
    args = p.parse_args()
    e = Essai(os.path.abspath(args.racine), args.garder, args.travail)
    T, F = THESAURUS, FICHE

    print("Thésaurus et fiches tels quels")
    e.cas("le dépôt est valide, sans erreur sur le thésaurus", lambda d: None, 0,
          absents=[("ERREUR", T, ".")])
    e.cas("une fiche classée avec des notions valides", notions(travaillees=["prog.poo.classe", "prog.poo.methode"],
                                                                 prerequises=["prog.fonction"]), 0,
          absents=[("ERREUR", F, "."), ("ATTENTION", F, "notion"), ("INFO", F, "ancien")])
    e.cas("les fiches sans notions sont comptées", lambda d: None, 0,
          presents=[("INFO", "donnees/ressources", r"fiches? sur \d+ sans notions")])

    print("Le champ « notions » d'une fiche")
    e.cas("notion absente du thésaurus", notions(travaillees=["prog.boucles"]), 1,
          presents=[("ERREUR", F, r"« prog\.boucles » n'est pas dans le thésaurus")])
    e.cas("notion absente : l'aide propose l'identifiant complet", notions(travaillees=["bornee"]), 1,
          presents=[("ERREUR", F, r"vouliez-vous dire : prog\.boucle\.bornee")])
    e.cas("identifiant mal écrit (accent)", notions(travaillees=["prog.boucle.bornée"]), 1,
          presents=[("ERREUR", F, r"identifiant de notion s'écrit en minuscules")])
    e.cas("rôle inconnu", notions(acquises=["prog.boucle"]), 1,
          presents=[("ERREUR", F, r"champ inconnu « acquises »")])
    e.cas("liste vide", notions(travaillees=[]), 1,
          presents=[("ERREUR", F, r"au moins 1 élément")])
    e.cas("même notion travaillée et prérequise", notions(travaillees=["prog.variable"], prerequises=["prog.variable"]), 0,
          presents=[("ATTENTION", F, r"à la fois travaillée et prérequise : la garder dans « travaillees » seulement")])
    e.cas("notion plus large et plus étroite citées ensemble", notions(travaillees=["prog.boucle", "prog.boucle.bornee"]), 0,
          presents=[("INFO", F, r"« prog\.boucle » est plus large que « prog\.boucle\.bornee »")])

    def rendre_obsolete(t, n):
        n["prog.boucle.bornee"]["obsolete"] = True
        n["prog.boucle.bornee"]["remplacee_par"] = "prog.boucle"
    e.cas("notion obsolète citée par une fiche", lambda d: (thesaurus(rendre_obsolete)(d), notions(travaillees=["prog.boucle.bornee"])(d)), 0,
          presents=[("ATTENTION", F, r"« prog\.boucle\.bornee » est obsolète : citer « prog\.boucle »")])

    print("Les anciens rôles et la conversion (T64)")
    e.cas("ancien rôle signalé pendant la conversion", notions(enseignees=["prog.boucle"], evaluees=["prog.boucle"]), 0,
          presents=[("INFO", F, r"« enseignees » et « evaluees » : anciens rôles remplacés par « travaillees ».*convertir_notions_t64"),
                    ("ATTENTION", "donnees/ressources", r"fiches? avec les anciens rôles")])
    e.cas("ancien rôle refusé une fois la conversion faite", notions(evaluees=["prog.boucle"]), 1,
          options=["--anciens-roles", "refuser"],
          presents=[("ERREUR", F, r"« evaluees » : ancien rôle remplacé par « travaillees »")])
    e.cas("une fiche qui mélange les deux formes", notions(travaillees=["prog.boucle"], enseignees=["prog.variable"]), 1,
          presents=[("ERREUR", F, r"la fiche mélange les deux formes")])
    e.cas("évaluée et prérequise (ancien rôle) : signalé aussi", notions(evaluees=["prog.variable"], prerequises=["prog.variable"]), 0,
          presents=[("ATTENTION", F, r"« prog\.variable » est à la fois travaillée et prérequise")])

    def avant_conversion(d):
        notions(enseignees=["prog.poo.classe", "prog.poo.methode"], evaluees=["prog.poo.methode", "prog.poo.attribut"],
                prerequises=["prog.fonction", "prog.poo.attribut"])(d)
        sortie = convertir(d)
        x = lire(os.path.join(d, FICHE))["notions"]
        attendu = {"travaillees": ["prog.poo.classe", "prog.poo.methode", "prog.poo.attribut"], "prerequises": ["prog.fonction"]}
        if x != attendu or list(x) != list(attendu):
            raise AssertionError(f"notions converties : {x}")
        if "« prog.poo.attribut » est aussi travaillée" not in sortie:
            raise AssertionError("la notion retirée des prérequises n'est pas signalée")
        if "0 en échec" not in convertir(d) or "0 converties" not in convertir(d):
            raise AssertionError("une seconde conversion change encore quelque chose")
    e.cas("conversion : union sans doublon, dans l'ordre ; le doublon quitte les prérequises ; relançable",
          avant_conversion, 0, options=["--anciens-roles", "refuser"],
          absents=[("ERREUR", F, "."), ("ATTENTION", F, "notion")])

    def tout_convertir(d):
        convertir(d)
    e.cas("conversion de toutes les fiches du dépôt : aucun ancien rôle ne reste", tout_convertir, 0,
          options=["--anciens-roles", "refuser"], absents=[("ERREUR", "donnees/ressources", "."), ("INFO", "donnees/ressources", "ancien")])

    def fiche_illisible(d):
        notions(enseignees=["prog.boucle"])(d)
        x = lire(os.path.join(d, FICHE))
        x["notions"]["evaluees"] = "prog.boucle"
        ecrire(os.path.join(d, FICHE), x)
        sortie = convertir(d, attendu=1)
        if "n'est pas une liste d'identifiants" not in sortie:
            raise AssertionError("l'échec n'est pas expliqué : " + sortie[-300:])
    e.cas("conversion : un rôle mal formé arrête la fiche, signalé", fiche_illisible, 1,
          presents=[("ERREUR", F, r"notions\.evaluees")])

    print("Le thésaurus")
    e.cas("thésaurus absent", lambda d: os.remove(os.path.join(d, T)), 1,
          presents=[("ERREUR", T, "référentiel introuvable")])
    e.cas("notion plus large inexistante", thesaurus(lambda t, n: n["prog.boucle"].__setitem__("plus_larges", ["prog.controles"])), 1,
          presents=[("ERREUR", T, r"aucune notion « prog\.controles »")])
    e.cas("hiérarchie qui tourne en rond", thesaurus(lambda t, n: n["prog.controle"].__setitem__("plus_larges", ["prog.boucle"])), 1,
          presents=[("ERREUR", T, r"la hiérarchie tourne en rond : .*prog\.boucle.*prog\.controle")])
    e.cas("identifiant en double", thesaurus(lambda t, n: t["notions"].append(dict(n["prog.boucle"], libelle="Autre libellé"))), 1,
          presents=[("ERREUR", T, r"l'identifiant « prog\.boucle » figure deux fois")])
    e.cas("libellé préféré en double", thesaurus(lambda t, n: n["prog.boucle.bornee"].__setitem__("libelle", "Boucle")), 1,
          presents=[("ERREUR", T, r"le libellé « Boucle » est déjà celui de « prog\.boucle »")])
    e.cas("libellé caché qui répète un libellé visible",
          thesaurus(lambda t, n: n["prog.boucle"].setdefault("caches", []).append("Itération")), 1,
          presents=[("ERREUR", T, r"« Itération » se confond avec .*libellé caché sert à une graphie")])
    e.cas("libellé alternatif répété (accents mis à part)",
          thesaurus(lambda t, n: n["prog.boucle"]["alternatifs"].append("repetition")), 1,
          presents=[("ERREUR", T, r"« repetition » se confond avec le libellé alternatif")])
    e.cas("même mot en français et en anglais : permis (SKOS)", lambda d: None, 0,
          absents=[("ERREUR", T, r"« iteration » se confond")])
    e.cas("homographe entre deux notions",
          thesaurus(lambda t, n: n["prog.variable"].setdefault("alternatifs", []).append("compteur de boucle")
                    or n["prog.compteur"]["alternatifs"].append("compteur de boucle")), 0,
          presents=[("ATTENTION", T, r"« compteur de boucle » désigne plusieurs notions \(prog\.compteur, prog\.variable\)")])
    e.cas("référence au programme inexistante", thesaurus(lambda t, n: n["prog.boucle"]["programme"].append("snt-2019.programmation.boucle")), 1,
          presents=[("ERREUR", T, r"« snt-2019\.programmation\.boucle » n'existe pas dans programmes\.json")])
    e.cas("programme entier cité", thesaurus(lambda t, n: n["prog.boucle"]["programme"].append("snt-2019")), 1,
          presents=[("ERREUR", T, r"« snt-2019 » est un programme entier")])
    e.cas("source d'une difficulté inconnue", thesaurus(lambda t, n: n["prog.boucle"]["difficultes"][0]["sources"].append("dupont-2020")), 1,
          presents=[("ERREUR", T, r"la source « dupont-2020 » n'est pas dans « sources »")])
    e.cas("correspondance vers un référentiel inconnu",
          thesaurus(lambda t, n: n["prog"]["correspondances"].append({"referentiel": "acm2013", "relation": "closeMatch", "code": "SDF"})), 1,
          presents=[("ERREUR", T, r"« acm2013 » n'est pas dans « referentiels_externes »")])
    e.cas("relation de correspondance qui n'est pas de SKOS",
          thesaurus(lambda t, n: n["prog"]["correspondances"][0].__setitem__("relation", "sameAs")), 1,
          presents=[("ERREUR", T, r"valeur \"sameAs\" non permise")])
    e.cas("notion sans notion plus large, hors des domaines",
          thesaurus(lambda t, n: n["prog.boucle"].__setitem__("plus_larges", [])), 1,
          presents=[("ERREUR", T, r"« prog\.boucle » n'a pas de notion plus large : l'ajouter à « domaines »")])
    e.cas("domaine qui a une notion plus large", thesaurus(lambda t, n: t["domaines"].append("prog.boucle")), 1,
          presents=[("ERREUR", T, r"« prog\.boucle » a une notion plus large : ce n'est pas un domaine")])
    e.cas("notion associée sur la même branche",
          thesaurus(lambda t, n: n["prog.boucle.bornee"].setdefault("associees", []).append("prog.boucle")), 0,
          presents=[("ATTENTION", T, r"« prog\.boucle » est déjà sur la même branche que « prog\.boucle\.bornee »")])
    e.cas("« remplacee_par » sans « obsolete »", thesaurus(lambda t, n: n["prog.boucle.bornee"].__setitem__("remplacee_par", "prog.boucle")), 1,
          presents=[("ERREUR", T, r"« remplacee_par » ne sert qu'à une notion « obsolete »")])
    e.cas("source sans adresse ni lecture", thesaurus(lambda t, n: [s.pop("url", None) for s in t["sources"] if s["id"] == "sorva-2013"]), 1,
          presents=[("ERREUR", T, r"il manque un des champs « url » ou « lu »")])
    e.cas("libellé sans lettre ni chiffre", thesaurus(lambda t, n: n["prog.boucle"].setdefault("code", []).append("//")), 1,
          presents=[("ERREUR", T, r"« // » n'a ni lettre ni chiffre")])
    e.cas("homographe que seule la recherche confond (mêmes racines)",
          thesaurus(lambda t, n: n["prog.compteur"]["alternatifs"].append("boucles bornées")), 0,
          presents=[("ATTENTION", T, r"désigne plusieurs notions \(prog\.boucle\.bornee, prog\.compteur\).*la recherche le confond")])

    print("L'historique du thésaurus (T60)")
    e.cas("l'historique est cohérent", lambda d: None, 0,
          absents=[("ERREUR", T, r"historique"), ("ATTENTION", T, r"historique")])
    e.cas("historique : notion inconnue",
          thesaurus(lambda t, n: t["historique"][-1].setdefault("ajoutees", []).append("prog.boucles")), 1,
          presents=[("ERREUR", T, r"historique\[\d+\]\.ajoutees\[\d+\] : aucune notion « prog\.boucles »")])
    e.cas("historique : notion ajoutée deux fois",
          thesaurus(lambda t, n: t["historique"][0].setdefault("ajoutees", []).append(t["historique"][-1]["ajoutees"][0])), 1,
          presents=[("ERREUR", T, r"est déjà ajoutée par historique\[0\] : une notion s'ajoute une seule fois")])
    e.cas("historique : notion modifiée avant d'être ajoutée",
          thesaurus(lambda t, n: t["historique"][0].setdefault("modifiees", []).append(t["historique"][-1]["ajoutees"][0])), 1,
          presents=[("ERREUR", T, r"elle ne peut pas être modifiée avant")])
    e.cas("historique : date après la version", thesaurus(lambda t, n: t["historique"][-1].__setitem__("date", "2099-01-01")), 1,
          presents=[("ERREUR", T, r"est après la version du thésaurus")])
    e.cas("historique : dates dans le désordre", thesaurus(lambda t, n: t["historique"][0].__setitem__("date", "2030-01-01")
                                                           or t.__setitem__("version", "2030-01-01")), 1,
          presents=[("ERREUR", T, r"précède la version d'avant")])
    e.cas("historique : tâche mal écrite", thesaurus(lambda t, n: t["historique"][-1].__setitem__("tache", "t60")), 1,
          presents=[("ERREUR", T, r"historique\[\d+\]\.tache")])

    print("La comparaison à une version précédente (--avant)")
    A = ["--avant", "{copie}/avant.json"]
    e.cas("même version : rien à signaler", avant(), 0, options=A,
          absents=[("ERREUR", T, "."), ("INFO", T, r"nouvelles? depuis"), ("INFO", T, "change de")])
    e.cas("identifiant publié qui disparaît", avant(retirer_notion("geo.itineraire")), 1, options=A,
          presents=[("ERREUR", T, r"« geo\.itineraire » .* a disparu depuis la version précédente : un identifiant publié est définitif")])
    e.cas("notion devenue obsolète : permis", avant(lambda t, n: n["geo.itineraire"].update(obsolete=True, remplacee_par="geo.carte")),
          0, options=A, presents=[("INFO", T, r"« geo\.itineraire » devient obsolète")], absents=[("ERREUR", T, ".")])
    e.cas("libellé changé et notion déplacée : signalés",
          avant(lambda t, n: n["geo.itineraire"].update(libelle="Itinéraires", plus_larges=["geo.carte"])), 0, options=A,
          presents=[("INFO", T, r"« geo\.itineraire » change de libellé : « Calcul d'itinéraire » devient « Itinéraires »"),
                    ("INFO", T, r"« geo\.itineraire » change de place")])
    e.cas("notion nouvelle absente de l'historique", avant(nouvelle_notion), 0, options=A,
          presents=[("INFO", T, r"1 notion nouvelle depuis la version précédente : geo\.essai"),
                    ("ATTENTION", T, r"absentes des « ajoutees » de l'historique : geo\.essai")])
    e.cas("notion nouvelle inscrite à l'historique",
          avant(lambda t, n: nouvelle_notion(t, n) or t["historique"].append({"date": t["version"], "tache": "T99",
                                                                              "resume": "Une notion d'essai.", "ajoutees": ["geo.essai"]})),
          0, options=A, absents=[("ATTENTION", T, r"historique")])
    e.cas("notion déjà publiée inscrite comme ajoutée",
          avant(lambda t, n: t["historique"].append({"date": t["version"], "resume": "Une erreur d'inscription.",
                                                     "ajoutees": ["geo.carte"]})), 0, options=A,
          presents=[("ATTENTION", T, r"« geo\.carte » existait déjà dans la version précédente")])
    e.cas("version précédente illisible", lambda d: open(os.path.join(d, "avant.json"), "w").write("{"), 1, options=A,
          presents=[("ERREUR", T, r"--avant : la version précédente ne se lit pas")])

    print("Valeurs et visibilité (consigne du 12/11/2026)")

    def alternatif_repete(d):
        chemin = os.path.join(d, VALEURS)
        v = lire(chemin)
        next(x for x in v["usages"] if x["id"] == "debranche")["alternatifs"].append("Débranché")
        ecrire(chemin, v)
    e.cas("synonyme d'une valeur qui répète son libellé", alternatif_repete, 1,
          presents=[("ERREUR", VALEURS, r"« Débranché » répète le libellé")])

    def roles_visibles(d):
        v = lire(os.path.join(d, VALEURS))
        caches = [r["id"] for r in v["roles"] if r["visible_par_defaut"] != {"exterieur": True, "eleve": True}]
        if caches:
            raise AssertionError(f"rôles encore cachés par défaut : {', '.join(caches)}")
    e.cas("tous les rôles sont visibles de tous par défaut", roles_visibles, 0)

    def corrige_visible(x):
        x["documents"].append({"role": "corrige", "titre": "Corrigé", "url": "https://exemple.fr/corrige.pdf",
                               "visible": {"exterieur": True, "eleve": True}})
    e.cas("un corrigé visible des élèves n'est plus signalé", fiche(corrige_visible), 0,
          absents=[("ATTENTION", F, r"visible des élèves")])

    sys.exit(e.terminer())


if __name__ == "__main__":
    main()
