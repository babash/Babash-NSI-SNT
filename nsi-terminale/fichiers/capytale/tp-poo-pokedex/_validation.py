# contenu du fichier _validation.py
from capytale.autoeval import (
    Validate,
    ValidateVariables,
    ValidateFunction,
    ValidateFunctionPretty,
    # ValidateAll,
    validationclass,
)
import __main__
import copy

import json
import requests
import matplotlib.pyplot as plt
import matplotlib.image as img
from PIL import Image
import io
import random
from IPython.display import Audio, display
import random

def go():
    """Fonction d'initialisation du module d'auto-évaluation."""
    return Validate()()

def correction_lue():
    """Fonction factice pour simuler la lecture d'une correction."""
    return Validate()()

# some pokemons
with open('pokemon_data_light.json', 'r') as json_file:
    pokemon_data = json.load(json_file)
for pk in pokemon_data:
    pokemon_data[pk]["pid"]  = pokemon_data[pk]["id"]
    del pokemon_data[pk]["id"]


# classic variables validation
gen9_type_chart_test = {
    "normal": {
        "normal": 1, "fire": 1, "water": 1, "electric": 1, "grass": 1, "ice": 1, "fighting": 1,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 1, "bug": 1, "rock": 0.5, "ghost": 0,
        "dragon": 1, "dark": 1, "steel": 0.5, "fairy": 1
    },
    "fire": {
        "normal": 1, "fire": 0.5, "water": 0.5, "electric": 1, "grass": 2, "ice": 2, "fighting": 1,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 1, "bug": 2, "rock": 0.5, "ghost": 1,
        "dragon": 0.5, "dark": 1, "steel": 2, "fairy": 1
    },
    "water": {
        "normal": 1, "fire": 2, "water": 0.5, "electric": 1, "grass": 0.5, "ice": 1, "fighting": 1,
        "poison": 1, "ground": 2, "flying": 1, "psychic": 1, "bug": 1, "rock": 2, "ghost": 1,
        "dragon": 0.5, "dark": 1, "steel": 1, "fairy": 1
    },
    "electric": {
        "normal": 1, "fire": 1, "water": 2, "electric": 0.5, "grass": 0.5, "ice": 1, "fighting": 1,
        "poison": 1, "ground": 0, "flying": 2, "psychic": 1, "bug": 1, "rock": 1, "ghost": 1,
        "dragon": 0.5, "dark": 1, "steel": 1, "fairy": 1
    },
    "grass": {
        "normal": 1, "fire": 0.5, "water": 2, "electric": 1, "grass": 0.5, "ice": 1, "fighting": 1,
        "poison": 0.5, "ground": 2, "flying": 0.5, "psychic": 1, "bug": 0.5, "rock": 2, "ghost": 1,
        "dragon": 0.5, "dark": 1, "steel": 0.5, "fairy": 1
    },
    "ice": {
        "normal": 1, "fire": 0.5, "water": 0.5, "electric": 1, "grass": 2, "ice": 0.5, "fighting": 1,
        "poison": 1, "ground": 2, "flying": 2, "psychic": 1, "bug": 1, "rock": 1, "ghost": 1,
        "dragon": 2, "dark": 1, "steel": 0.5, "fairy": 1
    },
    "fighting": {
        "normal": 2, "fire": 1, "water": 1, "electric": 1, "grass": 1, "ice": 2, "fighting": 1,
        "poison": 0.5, "ground": 1, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0,
        "dragon": 1, "dark": 2, "steel": 2, "fairy": 0.5
    },
    "poison": {
        "normal": 1, "fire": 1, "water": 1, "electric": 1, "grass": 2, "ice": 1, "fighting": 1,
        "poison": 0.5, "ground": 0.5, "flying": 1, "psychic": 1, "bug": 1, "rock": 0.5, "ghost": 0.5,
        "dragon": 1, "dark": 1, "steel": 0, "fairy": 2
    },
    "ground": {
        "normal": 1, "fire": 2, "water": 1, "electric": 2, "grass": 0.5, "ice": 1, "fighting": 1,
        "poison": 2, "ground": 1, "flying": 0, "psychic": 1, "bug": 0.5, "rock": 2, "ghost": 1,
        "dragon": 1, "dark": 1, "steel": 2, "fairy": 1
    },
    "flying": {
        "normal": 1, "fire": 1, "water": 1, "electric": 0.5, "grass": 2, "ice": 1, "fighting": 2,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 1, "bug": 2, "rock": 2, "ghost": 1,
        "dragon": 1, "dark": 1, "steel": 0.5, "fairy": 1
    },
    "psychic": {
        "normal": 1, "fire": 1, "water": 1, "electric": 1, "grass": 1, "ice": 1, "fighting": 2,
        "poison": 2, "ground": 1, "flying": 1, "psychic": 0.5, "bug": 1, "rock": 1, "ghost": 1,
        "dragon": 1, "dark": 0, "steel": 0.5, "fairy": 1
    },
    "bug": {
        "normal": 1, "fire": 0.5, "water": 1, "electric": 1, "grass": 2, "ice": 1, "fighting": 0.5,
        "poison": 0.5, "ground": 1, "flying": 0.5, "psychic": 2, "bug": 1, "rock": 1, "ghost": 0.5,
        "dragon": 1, "dark": 2, "steel": 0.5, "fairy": 0.5
    },
    "rock": {
        "normal": 1, "fire": 2, "water": 1, "electric": 1, "grass": 1, "ice": 2, "fighting": 0.5,
        "poison": 1, "ground": 0.5, "flying": 2, "psychic": 1, "bug": 2, "rock": 1, "ghost": 1,
        "dragon": 1, "dark": 1, "steel": 0.5, "fairy": 1
    },
    "ghost": {
        "normal": 0, "fire": 1, "water": 1, "electric": 1, "grass": 1, "ice": 1, "fighting": 1,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 2, "bug": 1, "rock": 1, "ghost": 2,
        "dragon": 1, "dark": 0.5, "steel": 1, "fairy": 1
    },
    "dragon": {
        "normal": 1, "fire": 1, "water": 1, "electric": 1, "grass": 1, "ice": 1, "fighting": 1,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 1, "bug": 1, "rock": 1, "ghost": 1,
        "dragon": 2, "dark": 1, "steel": 0.5, "fairy": 0
    },
    "dark": {
        "normal": 1, "fire": 1, "water": 1, "electric": 1, "grass": 1, "ice": 1, "fighting": 0.5,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 2, "bug": 1, "rock": 1, "ghost": 2,
        "dragon": 1, "dark": 0.5, "steel": 1, "fairy": 0.5
    },
    "steel": {
        "normal": 1, "fire": 0.5, "water": 0.5, "electric": 0.5, "grass": 1, "ice": 2, "fighting": 1,
        "poison": 1, "ground": 1, "flying": 1, "psychic": 1, "bug": 1, "rock": 2, "ghost": 1,
        "dragon": 1, "dark": 1, "steel": 0.5, "fairy": 2
    },
    "fairy": {
        "normal": 1, "fire": 0.5, "water": 1, "electric": 1, "grass": 1, "ice": 1, "fighting": 2,
        "poison": 0.5, "ground": 1, "flying": 1, "psychic": 1, "bug": 1, "rock": 1, "ghost": 1,
        "dragon": 2, "dark": 2, "steel": 0.5, "fairy": 1
    }
}
test_gen9_type_chart = ValidateVariables({"gen9_type_chart": gen9_type_chart_test})


# Quizz validation example :
@validationclass
class ValidateClassComprehension:
    def __call__(self):
        q1 = input("Quelle est le nom de la classe ?\t")
        if q1.strip() != "Pokemon":
            print("❌ Non d'un racaillou c'est raté essaye encore !")
            return False
        else:
              print("👏 Pika ! Pika !")
        q2 = input("Combien a-t-elle d'attributs ?\t").strip()
        if q2 != "8":
            print("❌ Non d'un gravalanche c'est raté essaye encore !")
            return False
        else:
            print("👏 Pika ! Pika !")
        q3 = input("De quelle ligne à quelle ligne se trouve le constructeur ? Exemple: 9-11\t").strip()
        if q3 != "4-12":
            print("❌ Non d'un grolem c'est raté  essaye encore !")
            return False
        else:
              print("👏 Pikachuuuuuuuuu !")
        return True

test_class_comprehension = ValidateClassComprehension()

@validationclass
class ValidateObjetComprehension:
    def __call__(self):
        questions = ["Que vaut ```pikachu.weight``` ?",
                     "Que vaut ```pikachu.stats[hp]``` ? ",
                     "Quelle est le type de l'attribut ```pikachu.types``` ?",
                     "La commande ```pikachu.hp``` est-elle correcte ? [oui/non]",
                     "La commande ```pikachu.sprite``` est-elle correcte ? [oui/non]",
                     "Quelle méthode est appelée pour afficher le pokémon ?",
                     "Que vaut l'attribut self de la méthode show lors de l'appel ```pikachu.show()```?",
                     "Quelle méthode est appelée à la ligne 1 du code ci-dessus ?"]
        answers = [["60"], ['35'], ['tuple'], ['non'], ['oui'], ['show', 'show()'], ["pikachu"], ['init', '__init__', 'init()', '__init__()']]
        for q, al in zip(questions, answers):
            a = input(q).strip()
            if a not in al:
                print("❌ Non d'un togépi c'est raté essaye encore !")
                return False
            else :
                print("👏 Bien joué !")
        return True

test_objet_comprehension = ValidateObjetComprehension()


# validation with class and object

# sample class
class PokemonTest:
    
    # constructeur
    def __init__(self, name, pid, height, weight, types, stats, sprite, cry, level=0):
        self.name = name
        self.pid = pid
        self.height = height
        self.weight = weight
        self.types = tuple(types)
        self.stats = stats
        self.sprite = sprite
        self.cry = cry
        self.level = level
        
    # les méthodes
    def __str__(self):
        txt = self.name.capitalize()
        if hasattr(self, "level"):
            txt += f"[lvl {self.level}]"
        return txt
        
    def __rpr__(self):
        return str(self)
    
    def level_up(self):
        self.level += 1
        for k in self.stats:
            self.stats[k] *= 1.1

    def pokemon2txt(self):
        txt  = f"Le pokémon {self.name} a {self.stats['hp']}pts de vie (hp). "
        txt += f"Son attack est de {self.stats['attack']} et sa defense de {self.stats['defense']}. "
        txt += f"Il est de type {self.types[0]}"
        if len(self.types) > 1 :
            txt += f" et {self.types[1]}"
        txt +="."
        return txt     

    def plus_rapide(self, vitesse):
        return self.stats["speed"] > vitesse
    
    def same_type(self, pokemons):
        meme_type = []
        for pk in pokemons :
            if self.types == pk.types :
                meme_type.append(pk)
        return meme_type

    def attaque1(self, cible):
        degat = (((((2*self.level)/5 + 2) * 100 * self.stats["attack"]/cible.stats["defense"])/50)+2)* random.uniform(0.85, 1) 
        if cible.stats["hp"] + degat <= 0:
            print(cible, "est K.O.")
            cible.stats["hp"] = 0
            return True
        else :
            cible.stats["hp"] -= degat
            return False
    
    def attaque(self, cible, attaque):
        global gen9_type_chart_test
        if self.types[0] == attaque.atype or\
           (len(self.types) > 1 and
            self.types[1] == attaque.atype):
           stab = 1.5
        else :
            stab = 1

        if attaque.categorie == "physical":
            patt = self.stats["attack"]
            cdef = cible.stats["defense"]
        else :
            patt = self.stats["special-attack"]
            cdef = cible.stats["special-defense"]
            
        type1 = gen9_type_chart_test[attaque.atype][cible.types[0]]
        if len(cible.types) > 1:
            type2 = gen9_type_chart_test[attaque.atype][cible.types[1]]
        else :
            type2 = 1
        
        degat = (((((2*self.level)/5 + 2) * attaque.puissance * patt/cdef)/50)+2)* random.uniform(0.85, 1) * stab * type1 * type2
        if cible.stats["hp"] + degat <= 0:
            print(cible, "est K.O.")
            cible.stats["hp"] = 0
            return True
        else :
            cible.stats["hp"] -= degat
            return False
    
    # usefull to implement for the next
    def copy(self):
        return copy.deepcopy(self)

# another sample class
class AttaqueTest:
    def __init__(self, atype, puissance, categorie):
        self.atype = atype
        self.puissance = puissance
        self.categorie = categorie

# usefull for overwrite equality when inherit from ValidatioSequence
def pokemon_equal(target, result):
    tdict = target.__dict__.copy()
    rdict = result.__dict__.copy()
    if not "level" in tdict :
        del rdict["level"]
    if tdict == rdict :
        return True
    print(tdict, rdict, tdict == rdict)
    print(tdict["stats"], rdict["stats"], tdict["stats"] == rdict["stats"])
    return False

# some object
ivysaur_test = PokemonTest(**{'name': 'ivysaur',
                'pid': 2,
                'height': 10,
                'weight': 130,
                'types': ("grass", "poison"),
                'stats': {'hp': 60, 'attack': 92, 'defense': 63,
                          'special-attack': 80, 'special-defense': 80,
                          'speed': 60},
                'sprite': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/2.png',
                'cry': 'https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/2.ogg'})

ivysaur2_test = ivysaur_test.copy()
ivysaur2_test.stats["hp"] = 70
ivysaur2_modif_test = ivysaur2_test.copy()
ivysaur2_modif_test.stats["attack"] = 62

best_team_ever = [PokemonTest(**pokemon_data["charizard"]),
                  PokemonTest(**pokemon_data["dragonite"]),
                  PokemonTest(**pokemon_data["jolteon"]),
                  PokemonTest(**pokemon_data["greninja"]),
                  PokemonTest(**pokemon_data["meowscarada"]),
                  PokemonTest(**pokemon_data["amoonguss"])]
test_remplacant = ValidateVariables({"remplacant": ivysaur_test.same_type(best_team_ever)})


close_combat_test = AttaqueTest(**{"atype": "fighting", "puissance": 120, "categorie": "physical"})
hydrocannon_test = AttaqueTest(**{"atype": "water", "puissance": 120, "categorie": "special"})
fatal_foudre_test = AttaqueTest(**{"atype": "electric", "puissance": 120, "categorie": "special"})
triple_attaque_test = AttaqueTest(**{"atype": "normal", "puissance": 90, "categorie": "special"})
detricanon_test = AttaqueTest(**{"atype": "poison", "puissance": 120, "categorie": "physical"})
lance_flamme_test = AttaqueTest(**{"atype": "fire", "puissance": 90, "categorie": "special"})
charge_test = AttaqueTest(**{"atype": "fighting", "puissance": 10, "categorie": "physical"})
calinerie_test = AttaqueTest(**{"atype": "fairy", "puissance": 95, "categorie": "physical"})
seisme_test = AttaqueTest(**{"atype": "ground", "puissance": 100, "categorie": "physical"})
balle_ombre_test = AttaqueTest(**{"atype": "ghost", "puissance": 80, "categorie": "special"})

# validate object with custom behavior
@validationclass
class ValidatePokemon(ValidateVariables):
    def equality(self, target, result):
        return pokemon_equal(target, result)
        

test_ivysaur = ValidatePokemon({"ivysaur": ivysaur_test})
test_ivysaur2 = ValidatePokemon({"ivysaur2": ivysaur2_test})
test_ivysaur2_modif = ValidatePokemon({"ivysaur2": ivysaur2_modif_test})


# validate object in standar behavior
@validationclass
class ValidateObject(ValidateVariables):
    def equality(self, target, result):
        return target.__dict__ == result.__dict__

test_attaques = ValidateObject({"close_combat": close_combat_test,
                                "hydrocannon": hydrocannon_test,
                                "fatal_foudre": fatal_foudre_test,
                                "triple_attaque": triple_attaque_test,
                                "detricanon": detricanon_test,
                                "lance_flamme": lance_flamme_test,
                                "charge": charge_test,
                                "calinerie": calinerie_test,
                                "seisme": seisme_test,
                                "balle_ombre": balle_ombre_test})

# validate class attributes
@validationclass
class ValidateClassSpecif:
    def __init__(self, cls_name, valid_cls, object_to_build, check_method_signature=True):
        self.cls_name = cls_name
        self.valid_cls = valid_cls
        self.object_to_build = object_to_build
        self.check_method_signature = check_method_signature

    def precompute(self):
        if self.cls_name in __main__.__dict__:
            self.cls2test = __main__.__dict__[self.cls_name]
            return True
        else:
            print("❌ Outch !")
            print(f"La classe {self.cls_name} n'est pas définie.")
            print("As-tu exécuté la cellule ?")
            print(f"As-tu mis le bon nom ? ({self.cls_name})")
            return False

    def __call__(self):
        if not self.precompute():
            return False
        # test attibutes
        try:
            objtest = self.cls2test(**self.object_to_build)
        except Exception as e:
            print(f"❌ Test échoué ! erreur durant la création de l'objet test.")
            print(f"[{e.__class__.__name__}]: {e}")
            raise e
            return False
        try:
            objvalid = self.valid_cls(**self.object_to_build)
        except Exception as e:
            print(f"❌ Test échoué ! erreur durant la création de l'objet temoin.")
            print(f"[{e.__class__.__name__}]: {e}")
            raise e
            return False
        if objtest.__dict__ != objvalid.__dict__:
            att_test = set(objtest.__dict__.keys())
            att_valid = set(objvalid.__dict__.keys())
            missing = att_valid - att_test
            toomuch = att_test - att_valid
            print("❌ Outch !")
            if missing:
                if len(missing) > 1:
                    print(f"Les attributs {' '.join(missing)} sont manquants.")
                else:
                    print(f"L'attribut {' '.join(missing)} est manquant.")
            if toomuch:
                if len(missing) > 1:
                    print(f"Les attributs {' '.join(toomuch)} sont en trop.")
                else:
                    print(f"L'attribut {' '.join(missing)} sont en trop.")
            print("As-tu exécuté la cellule ?")
            return False
        
        # test methods
        if self.check_method_signature and\
           self.valid_cls.__dict__ == self.cls2test.__dict__:
            met_test = set(objtest.__dict__.keys())
            met_valid = set(objvalid.__dict__.keys())
            missing = met_valid - met_test
            toomuch = met_test - met_valid
            print("❌ Outch !")
            if missing:
                if len(missing) > 1:
                    print(f"Les méthodes {' '.join(missing)} sont manquantes.")
                else:
                    print(f"La méthode {' '.join(missing)} est manquante.")
            if toomuch:
                if len(missing) > 1:
                    print(f"Les méthodes {' '.join(toomuch)} sont en trop.")
                else:
                    print(f"La méthode {' '.join(missing)} est en trop.")
            print("As-tu exécuté la cellule ?")
            return False
        print("👏 Bien joué !")
        return True

test_level = ValidateClassSpecif("Pokemon", PokemonTest, pokemon_data["gengar"])
test_Attaque = ValidateClassSpecif("Attaque", AttaqueTest, {"atype": "ghost", "puissance": 80, "categorie": "special"})

# valllidate method by checking :
#   - signature
#   - return value
#   - object modification
@validationclass
class ValidateMethod() :
    def __init__(self, cls_name,
                       method_name,
                       valid_cls,
                       valid_method,
                       objects_params,
                       method_params,
                       compare_object_method = lambda x, y: x == y,
                       compare_return_method = lambda x, y: x == y
                       ):
        self.cls_name = cls_name
        self.method_name = method_name
        self.valid_method = valid_method
        self.valid_cls = valid_cls
        self.objects_params = objects_params
        self.method_params = method_params
        self.compare_object_method = compare_object_method
        self.compare_return_method = compare_return_method

    def precompute(self):
        if self.cls_name in __main__.__dict__:
            if self.method_name in __main__.__dict__[self.cls_name].__dict__:
                self.cls2test = __main__.__dict__[self.cls_name]
                self.method2test = __main__.__dict__[self.cls_name].__dict__[self.method_name]
                return True
            else:
                print("❌ Outch !")
                print(f"La variable {self.method_name} n'existe pas dans la classe {self.cls_name}.")
                print("As-tu exécuté la cellule contenant la classe ?")
                print(f"As-tu mis le bon nom ? ({self.method_name})")
                return False
        else:
            print("❌ Outch !")
            print(f"La variable {self.cls_name} n'est pas définie.")
            print("As-tu exécuté la cellule ?")
            print(f"As-tu mis le bon nom ? ({self.cls_name})")
            return False

    def __call__(self):
        if not self.precompute():
            return False
        # tests
        n_test = len(self.objects_params)
        for i, (oparams, mparams) in enumerate(zip(self.objects_params,
                                                   self.method_params)):
            try:
                objtest = self.cls2test(**oparams)
            except Exception as e:
                print(f"❌ Test échoué ! erreur durant la création de l'objet test.")
                print(f"[{e.__class__.__name__}]: {e}")
                raise e
                return False
            try:
                objvalid = self.valid_cls(**oparams)
            except Exception as e:
                print(f"❌ Test échoué ! erreur durant la création de l'objet temoin.")
                print(f"[{e.__class__.__name__}]: {e}")
                raise e
                return False

            strmparams = [str(p) for p in mparams]
            print(f"Test {i+1}/{n_test}:\n",
                   f"\t-> Appel de la méthode: {objtest}.{self.method_name}({', '.join(strmparams)})")
            
            if not self.compare_object_method(objtest, objvalid):
                print(f"\t->paramètres pour la création des objets: {oparams}")
                print(f"❌ Test échoué ! les deux objets sont différents avant l'appel de la méthode:\n",
                      f"\t-> Votre objet: {objtest.__dict__}\n",
                      f"\t-> Objet attendu: {objvalid.__dict__}")
                return False
            try:
                testr = self.method2test(objtest, *mparams)
            except Exception as e:
                print(f"❌ Test échoué ! erreur durant l'appel de la méthode {self.method_name}.")
                print(f"[{e.__class__.__name__}]: {e}")
                raise e
                return False
            try:
                validr = self.valid_method(objvalid, *mparams)
            except Exception as e:
                print(f"❌ Test échoué ! erreur durant l'appel de la fonction référence.")
                print(f"[{e.__class__.__name__}]: {e}")
                raise e
                return False
           
            if type(testr) != type(validr):
                print(f"❌ Test échoué ! les types des retours sont différents:\n",
                      f"\t-> Type de votre retour : {type(testr)}",
                      f"\t-> Type du retour attendu: {type(validr)}")
                return False
            elif not self.compare_return_method(testr, validr):
                print(f"❌ Test échoué ! les retours sont différents:\n",
                      f"\t-> Votre retour : {testr}",
                      f"\t-> Retour attendu: {validr}")
                return False
            elif not self.compare_object_method(objtest, objvalid):
                print(f"❌ Test échoué ! les deux objets sont différents après l'appel de la méthode:\n",
                      f"\t-> Votre objet: {objtest.__dict__}",
                      f"\t-> Objet attendu: {objvalid.__dict__}")
                return False
            print("👏 Test réussi avec succès !")
        print("👏 Bien joué !")
        return True


random.seed(42)
test_pokemons_params = list(random.choices(list(pokemon_data.values()), k=25))
test_pokemons = [PokemonTest(**data) for data in test_pokemons_params]
random.shuffle(test_pokemons)

test_level_up = ValidateMethod("Pokemon",
                               "level_up",
                               PokemonTest,
                               PokemonTest.level_up,
                               test_pokemons_params,
                               [[] for _ in range(len(test_pokemons))],
                               compare_object_method=pokemon_equal)

test_pokemon2txt = ValidateMethod("Pokemon",
                               "pokemon2txt",
                               PokemonTest,
                               PokemonTest.pokemon2txt,
                               test_pokemons_params,
                               [[] for _ in range(len(test_pokemons))],
                               compare_object_method=pokemon_equal)

test_plus_rapide = ValidateMethod("Pokemon",
                               "plus_rapide",
                               PokemonTest,
                               PokemonTest.plus_rapide,
                               test_pokemons_params,
                               [[random.randrange(200)] for _ in range(len(test_pokemons))],
                               compare_object_method=pokemon_equal)

test_same_type = ValidateMethod("Pokemon",
                               "same_type",
                               PokemonTest,
                               PokemonTest.same_type,
                               test_pokemons_params,
                               [[list(random.choices(test_pokemons, k=5))] for _ in range(len(test_pokemons))],
                               compare_object_method=pokemon_equal)

test_attaque = ValidateMethod("Pokemon",
                               "attaque",
                               PokemonTest,
                               PokemonTest.attaque1,
                               test_pokemons_params,
                               [[t] for t in test_pokemons],
                               compare_object_method=pokemon_equal)

attaques_test = [close_combat_test,
                 hydrocannon_test,
                 fatal_foudre_test,
                 triple_attaque_test,
                 detricanon_test,
                 lance_flamme_test,
                 charge_test,
                 calinerie_test,
                 seisme_test,
                 balle_ombre_test]
test_attaque2 = ValidateMethod("Pokemon",
                               "attaque",
                               PokemonTest,
                               PokemonTest.attaque,
                               test_pokemons_params,
                               list(zip(test_pokemons[:len(attaques_test)], attaques_test)),
                               compare_object_method=pokemon_equal)
