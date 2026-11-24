"""Essais du contrôle des banques du Calendrier des vacances (scripts/calendrier_exercices.py).

Lancement : python3 -m unittest scripts/tests/test_calendrier_exercices.py
"""
import copy
import importlib.util
import json
import os
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ce", os.path.join(ICI, "..", "calendrier_exercices.py"))
ce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ce)
EXEMPLE = json.load(open(os.path.join(ICI, "calendrier", "exemple-boucles.json"), encoding="utf-8"))
NOUVEAUX = json.load(open(os.path.join(ICI, "calendrier", "exemple-nouveaux-types.json"), encoding="utf-8"))
SCHEMA = json.load(open(ce.SCHEMA, encoding="utf-8"))


def erreurs(donnees):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False)
    rp = ce.Rapport()
    ce.controler(f.name, rp, None, True, SCHEMA)
    os.unlink(f.name)
    return rp.erreurs


def un_exercice(n):
    d = copy.deepcopy(EXEMPLE)
    d["exercices"] = [d["exercices"][n - 1]]
    d["exercices"][0]["id"] = d["theme"]["id"] + "-001"
    return d


class Controle(unittest.TestCase):
    def test_exemple_juste(self):
        self.assertEqual(erreurs(un_exercice(4)), [])

    def test_mauvaise_option_annoncee(self):
        d = un_exercice(4)  # sortie
        d["exercices"][0]["niveaux"][0]["items"][0]["bonne"] = 1
        self.assertTrue(any("options justes" in e for e in erreurs(d)))

    def test_reponse_tapee_fausse(self):
        d = un_exercice(4)
        d["exercices"][0]["niveaux"][2]["items"][0]["reponse"] = "5"
        self.assertTrue(any("réponse annoncée" in e for e in erreurs(d)))

    def test_deux_corrections_justes(self):
        d = un_exercice(2)  # erreur
        it = d["exercices"][0]["niveaux"][0]["items"][0]
        it["corrections"][1] = it["corrections"][0] + " "
        self.assertTrue(any("donne aussi le bon résultat" in e for e in erreurs(d)))

    def test_piece_ambigue(self):
        d = un_exercice(6)  # completer : range(1, {0}) avec 3, 4, 5 ; 4 juste
        it = d["exercices"][0]["niveaux"][0]["items"][1]
        it["trous"][0]["options"] = ["3", "4", "4 "]
        self.assertTrue(any("donne aussi le bon résultat" in e for e in erreurs(d)))

    def test_identifiant_et_invisible(self):
        d = un_exercice(3)
        d["exercices"][0]["id"] = "exemple-boucles-007"
        d["exercices"][0]["titre"] += chr(0x200B)
        e = erreurs(d)
        self.assertTrue(any("identifiant attendu" in x for x in e))
        self.assertTrue(any("invisible" in x for x in e))

    def test_verifier_faux(self):
        d = un_exercice(3)
        for it in d["exercices"][0]["niveaux"][2]["items"]:
            if it.get("verifier") == "s == 10":
                it["reponse"] = True
        self.assertTrue(any("réponse annoncée" in e for e in erreurs(d)))

    def test_sql(self):
        d = {"theme": {"id": "essai-sql", "titre": "Essai SQL", "nature": "notion", "niveaux": ["nsi-tle"], "langage": "sql"},
             "base_sql": "CREATE TABLE livre (titre TEXT, annee INT); INSERT INTO livre VALUES ('A', 1990), ('B', 2005), ('C', 2010);",
             "exercices": [{"id": "essai-sql-001", "type": "sortie", "titre": "Requête", "objectif": "Lire une requête simple.", "relu": False,
                            "niveaux": [{"duree": 2, "items": [{"code": "SELECT titre FROM livre WHERE annee > 2000 ORDER BY titre;",
                                                                "options": ["B / C", "A", "A / B / C", "C"], "bonne": 0,
                                                                "retours": ["Juste.", "1990 < 2000.", "Le WHERE filtre.", "2005 > 2000 aussi."]}]}] * 3}]}
        self.assertEqual(erreurs(d), [])
        d["exercices"][0]["niveaux"] = copy.deepcopy(d["exercices"][0]["niveaux"])
        d["exercices"][0]["niveaux"][1]["items"][0]["bonne"] = 3
        self.assertTrue(erreurs(d))


    def test_message_obligatoire(self):
        d = un_exercice(2)  # erreur
        it = d["exercices"][0]["niveaux"][0]["items"][0]
        it.pop("message", None)
        self.assertTrue(any("un seul champ" in e for e in erreurs(d)))
        it["message"] = "NameError: name 'x' is not defined"
        self.assertTrue(any("annonce" in e for e in erreurs(d)))

    def test_affiche_fautif(self):
        d = un_exercice(2)
        it = d["exercices"][0]["niveaux"][1]["items"][0]  # range(10) au lieu de 1 à 10 : erreur de logique
        it["affiche_fautif"] = "faux"
        self.assertTrue(any("affiche_fautif" in e for e in erreurs(d)))

    def test_ordre_ambigu(self):
        d = un_exercice(5)  # ordre
        it = d["exercices"][0]["niveaux"][0]["items"][1]
        it["lignes"] = ["a = 1", "b = 2", "print(a + b)"]
        it["affiche"] = "3"
        self.assertTrue(any("autre disposition" in e for e in erreurs(d)))

    def test_sql_mise_a_jour_et_verifier(self):
        base = "CREATE TABLE t (n INT); INSERT INTO t VALUES (1), (2);"
        d = {"theme": {"id": "essai-sql", "titre": "Essai", "nature": "notion", "niveaux": ["nsi-tle"], "langage": "sql"}, "base_sql": base,
             "exercices": [{"id": "essai-sql-001", "type": "vraifaux", "titre": "Vrai ou faux", "objectif": "Lire une mise à jour.", "relu": False,
                            "niveaux": [{"duree": 2, "items": [{"texte": "Après ce code, t a 3 lignes.", "reponse": True, "explication": "Une ligne ajoutée.",
                                                                "code": "INSERT INTO t VALUES (5);", "verifier": "SELECT COUNT(*) = 3 FROM t;"}]}] * 3}]}
        self.assertEqual(erreurs(d), [])
        d["exercices"][0]["niveaux"] = copy.deepcopy(d["exercices"][0]["niveaux"])
        d["exercices"][0]["niveaux"][0]["items"][0]["reponse"] = False
        self.assertTrue(any("réponse annoncée" in e for e in erreurs(d)))
        out, err = ce.executer_sql(base, "UPDATE t SET n = n * 10; SELECT n FROM t ORDER BY n;")
        self.assertEqual((out, err), ("10\n20", None))


def un_nouveau(t):
    """L'exercice d'exemple du type t (trace, combien, paniers, intrus, memo, bits), seul dans sa banque."""
    d = copy.deepcopy(NOUVEAUX)
    d["exercices"] = [e for e in d["exercices"] if e["type"] == t]
    d["exercices"][0]["id"] = d["theme"]["id"] + "-001"
    return d


class NouveauxTypes(unittest.TestCase):
    def test_exemples_justes(self):
        for t in ("trace", "combien", "paniers", "intrus", "memo", "bits"):
            with self.subTest(t=t):
                self.assertEqual(erreurs(un_nouveau(t)), [])

    def test_trace_fausse(self):
        d = un_nouveau("trace")
        d["exercices"][0]["niveaux"][0]["items"][0]["tours"][2][1] = "4"
        self.assertTrue(any("ne suit pas le code" in e for e in erreurs(d)))

    def test_trace_depart(self):
        d = un_nouveau("trace")
        d["exercices"][0]["niveaux"][1]["items"][0]["depart"] = False
        self.assertTrue(any("ne suit pas le code" in e for e in erreurs(d)))

    def test_combien_faux(self):
        d = un_nouveau("combien")
        d["exercices"][0]["niveaux"][1]["items"][0]["reponse"] = 7
        self.assertTrue(any("réponse annoncée" in e for e in erreurs(d)))

    def test_combien_depart_sur_la_reponse(self):
        d = un_nouveau("combien")
        d["exercices"][0]["niveaux"][0]["items"][0]["depart"] = 4
        self.assertTrue(any("commence sur la réponse" in e for e in erreurs(d)))

    def test_paniers_un_seul(self):
        d = un_nouveau("paniers")
        for c in d["exercices"][0]["niveaux"][0]["items"][0]["cartes"]:
            c["panier"] = 0
        self.assertTrue(any("au moins une carte" in e for e in erreurs(d)))

    def test_intrus_execute(self):
        d = un_nouveau("intrus")
        d["exercices"][0]["niveaux"][0]["items"][0]["intrus"] = 0
        self.assertTrue(any("intrus" in e for e in erreurs(d)))

    def test_memo_execute(self):
        d = un_nouveau("memo")
        d["exercices"][0]["niveaux"][0]["items"][0]["paires"][0][1] = "0 1"
        self.assertTrue(erreurs(d))

    def test_bits_cible(self):
        d = un_nouveau("bits")
        d["exercices"][0]["niveaux"][0]["items"][0]["reponse"] = "1100"
        self.assertTrue(any("pas la cible" in e for e in erreurs(d)))
        d = un_nouveau("bits")
        d["exercices"][0]["niveaux"][2]["items"][0]["reponse"] = "11111111"
        self.assertTrue(erreurs(d))


if __name__ == "__main__":
    unittest.main()
