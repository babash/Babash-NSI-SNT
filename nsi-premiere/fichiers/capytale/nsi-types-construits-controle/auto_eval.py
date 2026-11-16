import random
from capytale.random import user_seed
from capytale.autoeval import validationclass, ValidateVariables, Validate, ValidateFunctionPretty
from IPython.display import Markdown

_note = 0
_note_max_possibles = 0

def go():
    return Validate()()

def correction_lue():
    return Validate()()

def print_note():
    global _note_max_possibles
    global _note
    print(f"📈 Vous avez actuellement {_note}/20 ({_note}/{_note_max_possibles})")

def pre_super_call(self):
    global _note_max_possibles
    trial = self.trial_count()

    if trial == 0:
        _note_max_possibles += self.pts
    
    return trial

def post_super_call(self, trial, success):
    global _note
    if self.juste :
        print(f"👏 Bravo ! Vous avez déjà gagné les points de cette question.")
        print_note()
        return True
    elif trial > self.max_trial :
        print(f"⌛ Vous avez depassé le nombre d'essai, vous ne marquez donc pas de points. Pensez à regarder la correction.")
        return True

    if success :
        self.juste = True
        _note += self.pts
        print(f"👏 Bravo ! Vous venez de gagner {self.pts} points")
        print_note()
    elif not success and trial < self.max_trial:
        print(f"⚠️ Il te reste {self.max_trial-trial} essais.")
        for t in range(trial+1):
            if t in self.indice :
                print(f"🧩 Aide : {self.indice[t]}")
        if trial == self.max_trial - 1:
            print(f"🏋🏾‍♀️ Courage champion ")
        if trial == self.max_trial :
            print(f"⚠️ C'est votre dernier essai. ⚠️")
    else :
        print("❌ Dommage pense à lire la correction en détail et à réviser cette question en vue du controle.")
        print_note()
        return True
    return success


@validationclass
class ValidateVarTrial(ValidateVariables):
    def __init__(self, names_and_values, pts, indice={}, max_trial=2, **kwargs):
        self.max_trial = max_trial
        self.indice = indice
        self.pts = pts
        self.juste = False
        super().__init__(names_and_values, **kwargs)

    def handle_failure(self, value, target, result):
        # print("handle_failure :", value, target, result)
        return super().handle_failure(value, target, result)
    
    def handle_exception(self, exc, value, target):
        # print("handle_failure :", value, target, exc)
        return super().handle_exception(exc, value, target)

    def handle_full_success(self):
        pass

    def __call__(self): 
        trial = pre_super_call(self)
        success = super().__call__()
        return post_super_call(self, trial, success)

# Quizz validation QCM :
@validationclass
class ValidateQCMTrial(Validate):

    def __init__(self, questions, reponses, pts, max_trial=2, **kwargs):
        self.max_trial = max_trial
        self.questions = questions
        self.reponses = reponses
        self.pts = pts
        self.juste = False
        super().__init__(**kwargs)

    def __call__(self):
        global _note
        global _note_max_possibles

        default = len(self.questions) - 1
        trial = self.trial_count()

        if trial == 0:
            _note_max_possibles += self.pts

        if self.juste :
            print(f"👏 Bravo ! Vous avez déjà gagné les points de cette question.")
            print_note()
            return True
        elif trial > self.max_trial :
            print(f"⌛ Vous avez dépassé le nombre d'essai vous ne marquez donc pas de points. Pensez à regarder la correction.")
            return True
        else:
            q1 = input(self.questions.get(trial, self.questions[default])+("\n\t⚠️ C'est ton dernier essai. ⚠️" if trial == self.max_trial else ""))
            if q1.strip().lower() not in self.reponses.get(trial, self.reponses[default]):
                if trial < self.max_trial:
                    print(f"❌ Réfléchissez bien. Il vous reste {self.max_trial - trial} essais!")
                else :
                    print("❌ Dommage... pensez à lire la correction en détail et à réviser cette question en vue du controle.")
                    print_note()
                    return True
            else :
                self.juste = True
                _note += self.pts
                print(f"👏 Bravo ! Vous venez de gagner {self.pts} points")
                print_note()
                return True

        return False

@validationclass
class ValidateFunctionPrettyTrial(ValidateFunctionPretty):

    def __init__(self, func_name, test_values, indice, pts, target_values=None, valid_function=None, argcount=None, check_signature=False, ignore_names_in_signature=False, max_trial=2, **kwargs):
        self.max_trial = max_trial
        self.pts = pts
        self.indice = indice
        self.juste = False
        super().__init__(func_name, test_values,
                         target_values=target_values,
                         valid_function=valid_function,
                         argcount=argcount,
                         check_signature=check_signature,
                         ignore_names_in_signature=ignore_names_in_signature,
                         **kwargs)

    def handle_failure(self, value, target, result):
        # print("handle_failure :", value, target, result)
        return super().handle_failure(value, target, result)
    
    def handle_exception(self, exc, value, target):
        # print("handle_failure :", value, target, exc)
        return super().handle_exception(exc, value, target)

    def handle_full_success(self):
        if not self.juste and self.trial_count() < self.max_trial:
            return super().handle_full_success()

    def __call__(self):
        trial = pre_super_call(self)
        success = super().__call__()
        return post_super_call(self, trial, success)


Q1 = ValidateQCMTrial(questions={0: "On souhaite représenter le classement des clubs de ligue 1 quelle stucture de données est la plus adaptée ?",
                                 1: "On souhaite représenter le classement des clubs de ligue 1 quelle stucture de données est la plus adaptée ?\n"
                                    "\t A: liste\t B: dictionnaire\t C: tuple\t D: string"},
                      reponses={0: ["liste", "list"], 1: ["list", "liste", "a"]},
                      pts=1,
                      max_trial=2)

Q2 = ValidateVarTrial({"classement": ["PSG", "OM", "Monaco", "Nice"]},
                       indice={2: 'On utilise les guillements pour représenter les chaines de caractères comme: "Nice".',
                               1: 'On utilise les crochets [] pour représenter les listes.',
                               0: "Pensez à réexécuter la cellule contenant le code avant d'éxécuter la cellule vérification."},
                       pts=1.5,
                       max_trial=3)

Q3 = ValidateQCMTrial(questions={0: "Quelle fonction retourne la longueur d'une liste ?"},
                      reponses={0: ["len"]},
                      pts=1,
                      max_trial=1)

Q4 = ValidateQCMTrial(questions={0: "Comment accéder au premier du classement ?",
                                 1: "Comment accéder au premier du classement ?\n"
                                    "\t A: liste[0]\t B: classement[1]\t C: classement[0]\t D: classement[premier]"},
                      reponses={0: ["classement[0]"], 1: ["classement[0]", "c"]},
                      pts=1,
                      max_trial=2)

Q5 = ValidateQCMTrial(questions={0: "Comment accéder au dernier du classement ? (en utilisant les indexes négatifs)",
                                 1: "Comment accéder au dernier du classement ?  (en utilisant les indexes négatifs)\n"
                                    "\t A: liste[-1]\t B: classement[-1]\t C: classement[3]\t D: classement[dernier]"},
                      reponses={0: ["classement[-1]", "classement[len(classement)-1]"],
                                1: ["classement[-1]", "classement[len(classement)-1]", "b"]},
                      pts=1,
                      max_trial=2)

Q6 = ValidateVarTrial({"classement": ["PSG", "OM", "Monaco", "Nice", "OL", "Lille"]},
                       indice={2: 'On peut utiliser la méthode append.',
                               1: 'Vérifiez que tu as bien ortographié OL et Lille. Il faut tenir compte des majuscules et des minuscules.',
                               0: "Pensez à réexécuter la cellule contenant le code avant d'éxécuter la cellule vérification."},
                       pts=1.5,
                       max_trial=3)

Q7 = ValidateVarTrial({"classement": ["PSG", "OM", "Monaco", "Nice", "Lille", "OL"]},
                       indice={},
                       pts=1.5,
                       max_trial=2)

_stats = {"PSG" : (1, 84, 35, 92),
          "OM" : (2, 65, 47, 74),
          "Monaco" : (3, 61, 41, 63),
          "Nice" : (4, 60, 41, 66),
          "Lille" : (5, 60, 36, 52),
          "OL" : (6, 57, 46, 65),
          "Strasbourg" : (7, 57, 44, 56),
          "Lens" : (8, 52, 39, 42),
          "Brest" : (9, 50, 59, 52),
          "Toulouse" : (10, 42, 43, 44),
          "Auxerre" : (11, 42, 51, 48),
          "Rennes" : (12, 41, 50, 51),
          "Nantes" : (13, 36, 52, 39),
          "Angers" : (14, 36, 53, 32),
          "Le Havre" : (15, 34, 71, 40),
          "Reims" : (16, 33, 47, 33),
          "Saint-Etienne": (17, 30, 77, 39),
          "Montpellier" : (18, 16, 79, 23)}

Q8 = ValidateQCMTrial(questions={0: "Quel est le type de la variable stats ?"},
                      reponses={0: ["dict", "dictionnaire"]},
                      pts=1,
                      max_trial=1)


Q9 = ValidateQCMTrial(questions={0: "Quel est le type de stats['Reims'] ?"},
                      reponses={0: ["tuple"]},
                      pts=1.5,
                      max_trial=1)

Q10 = ValidateQCMTrial(questions={0: "Est-il possible de modifier le classement d'un équipe avec cette structure de données ? (OUI/NON)"},
                      reponses={0: ["non"]},
                      pts=1,
                      max_trial=0)

Q11 = ValidateQCMTrial(questions={0: "Que faut-il écrire pour obtenir le nombre de points de Lens ? "},
                      reponses={0: ['stats["lens"][1]', "stats['lens'][1]"]},
                      pts=1.5,
                      max_trial=2)

Q12 = ValidateQCMTrial(questions={0: "Que se passera-t-il si on execute la commade stats[1] ?",
                                 1: "Que se passera-t-il si on execute la commade stats[1] ?\n"
                                    "\t A: Cela donne les statistiques du PSG\n\t B: Cela donne les statistiques du premier au classement\n\t C: IndexError\n\t D: KeyError"},
                      reponses={0: ["keyerror"],
                                1: ["keyerror", "d"]},
                      pts=1,
                      max_trial=2)

Q13 = ValidateVarTrial({"stats": _stats},
                       indice={2: 'La réponse est de la forme stats["..."] = (..., ..., ..., ...).',
                               1: 'Il faut utiliser l\'opérateur =.',
                               0: "Pensez à réexécuter la cellule contenant le code avant d'éxécuter la cellule vérification."},
                       pts=1.5,
                       max_trial=3)
        

def _difference_buts(stats):
    diff = {}
    for e, v in stats.items():
        diff[e] = v[3] - v[2]
    return diff

def _nb_pts_moyen(stats):
    sum_pts = 0
    for v in stats.values():
        sum_pts += v[1]
    return sum_pts/len(stats)

def _meilleure_attaque(stats):
    but_marques_max = -1
    meilleure_equipe = None
    for e, v in stats.items():
        but_marques = v[3]
        if but_marques > but_marques_max:
            but_marques_max = but_marques
            meilleure_equipe = e
    return meilleure_equipe

test_stats = [{k: (i+1, random.randint(0, 100),
                           random.randint(0, 100),
                           random.randint(0, 100))
                     for i, k in enumerate(random.choices(list(_stats.keys()), k=random.randrange(2, 6)))}
                     for _ in range(3)] + [_stats]

Q14 = ValidateFunctionPrettyTrial(func_name="meilleure_attaque",
                                  pts=2,
                                  test_values = test_stats,
                                  valid_function=_meilleure_attaque,
                                  argcount=1,
                                  check_signature=True,
                                  ignore_names_in_signature=False,
                                  max_trial=6,
                                  indice={0: "Pensez à réexécuter la cellule contenant la fonction avant d'éxécuter la cellule vérification.",
                                          3: "Un parcours par item (.items()) est le plus adapté.",
                                          4: "Le nombre de buts marqués est l'indice 3 du tuple.",
                                          5: "Il faut comparer le nombres de buts marqués de l'équipe courante avec le nombres de buts marqués de la meilleure attaque parcouru."})

Q15 = ValidateFunctionPrettyTrial(func_name="nb_pts_moyen",
                                  pts=2,
                                  test_values = test_stats,
                                  valid_function=_nb_pts_moyen,
                                  argcount=1,
                                  check_signature=True,
                                  ignore_names_in_signature=False,
                                  max_trial=6,
                                  indice={
                                    0: "Pensez à réexécuter la cellule contenant la fonction avant d'éxécuter la cellule vérification.",
                                    2: "Le nombre de points est à l'indice 1 du tuple.",
                                    3: "Un parcours par valeur est le plus adapté.",
                                    4: """
    def nb_pts_moyen(stats):
        sum_pts = ... # Initialisation de la somme
        for v in stats.values():
            sum_pts += ... # On accumule les pts
        return .... # Calcul de la moyenne
                                    """})

Q16 = ValidateFunctionPrettyTrial(func_name="difference_buts",
                                  pts=2,
                                  test_values = test_stats,
                                  valid_function=_difference_buts,
                                  argcount=1,
                                  check_signature=True,
                                  ignore_names_in_signature=False,
                                  max_trial=6,
                                  indice={0: "Pensez à réexécuter la cellule contenant la fonction avant d'éxécuter la cellule vérification.",
                                          1: "Le nombre de buts marqués est à l'indice 3 du tuple.",
                                          2: "Le nombre de buts encaissés est à l'indice 2 du tuple.",
                                          3: "Un parcours par item (.items()) est le plus adapté.",
                                          4:"""
    def difference_buts(stats):
        diff = {} # On crée un dictionnaire vide
        for e, v in stats.items(): # Parcours par couple clé, valeur
            diff[...] = .... # Calcul de la différence de but de l'équipe e
        return diff 
                                          """})


