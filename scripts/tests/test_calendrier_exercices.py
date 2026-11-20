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


if __name__ == "__main__":
    unittest.main()
