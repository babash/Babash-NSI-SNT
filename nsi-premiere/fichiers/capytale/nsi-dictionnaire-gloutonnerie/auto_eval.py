import random
from capytale.autoeval import validationclass, ValidateVariables, Validate, ValidateFunctionPretty
from IPython.display import Markdown

# --- CONFIGURATION DU SCORE ---
_note = 0
_note_max_possibles = 0

def go():
    return Validate()()

def print_note():
    global _note, _note_max_possibles
    print(f"📈 Score actuel : {_note}/20")

# --- CLASSE QCM PERSONNALISÉE (Progressive) ---

@validationclass
class ValidateQCMTrial:
    def __init__(self, questions, reponses, pts=1, max_trial=4):
        self.questions = questions  # Dico {0: "Quest", 1: "Quest avec options"}
        self.reponses = reponses    # Dico {0: ["rep1"], 1: ["rep1", "a"]}
        self.pts = pts
        self.max_trial = max_trial
        self.juste = False

    def __call__(self):
        global _note
        if self.juste:
            print("✅ Cette question est déjà validée.")
            return True
        
        trial = self.trial_count()
        if trial >= self.max_trial:
            print("⌛ Nombre d'essais dépassé. Regardez la correction.")
            return False

        # Sélection de la version de la question (0, 1 sans aide / 2+ avec aide)
        version = 1 if trial >= 2 else 0
        prompt = self.questions.get(version, self.questions[0])
        
        rep_eleve = input(prompt + "\n\nVotre réponse : ").strip().lower()
        
        attendus = [r.lower() for r in self.reponses.get(version, self.reponses[0])]
        
        if rep_eleve in attendus:
            self.juste = True
            _note += self.pts
            print(f"👏 Bravo ! +{self.pts} pt(s).")
            print_note()
            return True
        else:
            print(f"❌ Mauvaise réponse. Il reste {self.max_trial - trial - 1} essais.")
            return False

# --- CLASSES STANDARDS (Variables et Fonctions) ---

def eval_global(self, success):
    global _note
    if self.juste:
        print("✅ Déjà validé.")
        return True
    if success:
        self.juste = True
        _note += getattr(self, 'pts', 1)
        print(f"👏 Bravo ! Score : {_note}/20")
    return success

@validationclass
class VarCheck(ValidateVariables):
    def __init__(self, dict_vars, pts=1, **kwargs):
        self.pts, self.juste, self.max_trial = pts, False, 3
        super().__init__(dict_vars, **kwargs)
    def __call__(self):
        return eval_global(self, super().__call__())

@validationclass
class FuncCheck(ValidateFunctionPretty):
    def __init__(self, name, tests, pts=1, **kwargs):
        self.pts, self.juste, self.max_trial = pts, False, 4
        super().__init__(name, tests, **kwargs)
    def __call__(self):
        return eval_global(self, super().__call__())

# --- JEUX DE TESTS ---
# Dictionnaires simples pour tests de fonctions
t_dict = [{"pomme": 10, "poire": 5}, {"a": 1, "b": 2, "c": 3}, {}, {"x": 100}]
# Dictionnaires imbriqués : {"Nom": [prix, quantite]}
t_imb = [{"Zelda": [60, 5], "Portal": [15, 2]}, {"A": [10, 10], "B": [5, 0]}, {"Vide": [0, 100]}]
# Objets pour algorithmes gloutons : {"Nom": poids}
t_glouton = [({"A": 5, "B": 2, "C": 8}, 10), ({"X": 10}, 5), ({"C1": 2, "C2": 2}, 5), ({"O": 1}, 10)]


# --- INSTANCIATION DES 20 QUESTIONS ---

# PARTIE 1 : LISTES
Q1 = VarCheck({"arrivage": ["Zelda", "Mario", "Minecraft"]})
Q2 = VarCheck({"arrivage": ["Zelda", "Splatoon", "Minecraft", "Tetris"]})

# PARTIE 2 : DICTIONNAIRES
Q3 = VarCheck({"panier": {"pomme": 10, "poire": 3}})
Q4 = VarCheck({"n": 10})
Q5 = VarCheck({"panier": {"pomme": 13, "poire": 3}})
Q6 = VarCheck({"panier": {"pomme": 13, "poire": 3, "melon": 10}})

# QCM 7 : Test d'existence
Q7 = ValidateQCMTrial(
    questions={0: "Quelle expression permet de vérifier si 'poire' est une clé du dictionnaire panier ?",
               1: "Quelle expression permet de vérifier si 'poire' est une clé du dictionnaire panier ?\n"
                  "\t A: 'poire' in panier\t B: panier.has('poire')\t C: panier == 'poire'"},
    reponses={0: ["'poire' in panier", "poire in panier", '"poire" in panier'], 1: ["'poire' in panier", "poire in panier", "a", '"poire" in panier']},
    max_trial=4
)

Q8 = FuncCheck("taille", t_dict, valid_function=len)
Q9 = FuncCheck("a_pomme", t_dict, valid_function=lambda d: "pomme" in d)
Q10 = FuncCheck("total_v", t_dict, valid_function=lambda d: sum(d.values()))
Q11 = FuncCheck("vider", t_dict, valid_function=lambda d: {k: 0 for k in d})

# PARTIE 3 : STRUCTURES IMBRIQUÉES
Q12 = VarCheck({"prix_p": 15})
Q13 = VarCheck({"qte_z": 5})
Q14 = FuncCheck("somme_q", t_imb, valid_function=lambda d: sum(v[1] for v in d.values()))

# PARTIE 4 : GLOUTONS
# QCM 15 : Principe
Q15 = ValidateQCMTrial(
    questions={0: "Un algorithme glouton fait à chaque étape :",
               1: "Un algorithme glouton fait à chaque étape :\n"
                  "\t A: Un choix global\t B: Le meilleur choix local immédiat\t C: Un choix au hasard"},
    reponses={0: ["choix local", "meilleur choix local", "le meilleur choix local"], 1: ["choix local", "meilleur choix local", "b"]},
    max_trial=3
)

# QCM 16 : Optimalité
Q16 = ValidateQCMTrial(
    questions={0: "La solution gloutonne est-elle toujours la solution optimale (la meilleure possible) ?",
               1: "La solution gloutonne est-elle toujours la solution optimale ?\n"
                  "\t A: Oui, toujours\t B: Pas forcément\t C: Jamais"},
    reponses={0: ["pas forcement", "non", "pas toujours"], 1: ["pas forcement", "non", "b"]},
    max_trial=3
)

Q17 = FuncCheck("filtre", t_glouton, argcount=2, valid_function=lambda obj, m: [n for n, p in obj.items() if p <= m])
Q18 = VarCheck({"ratio_c": 20.0})
Q19 = VarCheck({"top": "Micro"})

def _sol_braquage(objets, m):
    sac, poids = [], 0
    for n, p in objets.items():
        if poids + p <= m:
            sac.append(n)
            poids += p
    return sac

Q20 = FuncCheck("braquage", t_glouton, argcount=2, valid_function=_sol_braquage)
