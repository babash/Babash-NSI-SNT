"""QuizzNSI : tests du vérificateur de cours.

Lancement, depuis la racine de QuizzNSI : python3 -I -m unittest discover -s tests -p "test_*.py"
"""
import copy
import json
import os
import sys
import tempfile
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "outils"))
import verifier_cours as V  # noqa: E402

with open(os.path.join(RACINE, "cours", "piles-files.json"), encoding="utf-8") as f:
    MODELE = json.load(f)


def questions(c):
    return [d for d in c["diapositives"] if d["type"] == "question"]


class TestVerifier(unittest.TestCase):
    def verifier(self, cours, executer=False):
        with tempfile.TemporaryDirectory() as d:
            chemin = os.path.join(d, cours["id"] + ".json")
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(cours, f, ensure_ascii=False)
            r, _ = V.verifier_cours(chemin, executer_code=executer)
        return r.erreurs

    def modifie(self, f):
        c = copy.deepcopy(MODELE)
        f(c)
        return self.verifier(c)

    def test_le_cours_livre_est_conforme_avec_execution(self):
        self.assertEqual(self.verifier(copy.deepcopy(MODELE), executer=True), [])

    def test_trois_options(self):
        e = self.modifie(lambda c: questions(c)[0]["options"].pop())
        self.assertTrue(any("4 options" in x for x in e))

    def test_deux_reponses_justes(self):
        e = self.modifie(lambda c: questions(c)[0]["options"][0].update(juste=True))
        self.assertTrue(any("une seule option juste" in x for x in e))

    def test_feedback_vide(self):
        e = self.modifie(lambda c: questions(c)[2]["options"][1].update(feedback="Non."))
        self.assertTrue(any("feedback" in x for x in e))

    def test_objectif_manquant(self):
        e = self.modifie(lambda c: questions(c)[3].pop("objectif"))
        self.assertTrue(any("objectif" in x for x in e))

    def test_gras_dans_une_option(self):
        e = self.modifie(lambda c: questions(c)[0]["options"][1].update(texte="Une **pile**"))
        self.assertTrue(any("gras" in x for x in e))

    def test_caractere_invisible(self):
        e = self.modifie(lambda c: questions(c)[0].update(nom="Pile" + chr(0x200B)))
        self.assertTrue(any("U+200B" in x for x in e))

    def test_nombre_de_questions(self):
        def retirer(c):
            q = questions(c)[-1]
            c["diapositives"].remove(q)
        e = self.modifie(retirer)
        self.assertTrue(any("19 questions" in x for x in e))

    def test_repartition_desequilibree(self):
        def tout_en_a(c):
            for q in questions(c):
                j = next(o for o in q["options"] if o.get("juste"))
                q["options"].remove(j)
                q["options"].insert(0, j)
        e = self.modifie(tout_en_a)
        self.assertTrue(any("répartition" in x for x in e))

    def test_sortie_fausse_detectee_a_l_execution(self):
        c = copy.deepcopy(MODELE)
        questions(c)[4]["verifications"][0]["sortie"] = "[4, 1, 3]"
        e = self.verifier(c, executer=True)
        self.assertTrue(any("sortie attendue" in x for x in e))

    def test_erreur_attendue_detectee(self):
        c = copy.deepcopy(MODELE)
        questions(c)[7]["verifications"][0]["erreur"] = "KeyError"
        e = self.verifier(c, executer=True)
        self.assertTrue(any("erreur attendue" in x for x in e))

    def test_code_sans_verification(self):
        e = self.modifie(lambda c: questions(c)[2].pop("verifications"))
        self.assertTrue(any("vérification" in x for x in e))

    def test_svg_avec_script_refuse(self):
        e = self.modifie(lambda c: questions(c)[0].update(schema={"type": "svg", "code": '<svg onload="x()"></svg>'}))
        self.assertTrue(any("svg" in x for x in e))


if __name__ == "__main__":
    unittest.main()
