/* Contrôle de notions : programmation orientée objet (NSI, terminale)
   Babash - NSI Tani Malandi · contenus CC BY-SA 4.0 · code MIT

   Énoncés, programmes et consoles du contrôle, JAMAIS les réponses : la clé
   de correction est dans cle.js, que seules la page prof et le corrigé chargent.
   Les consoles sont les sorties réelles de Python 3.13 (seul le dossier est
   retiré des chemins de fichiers).

   Le bloc entre les deux marqueurs DONNEES est du JSON pur : le script
   verification/verifier.py le relit pour tout recalculer par exécution. */

window.CN_DONNEES = /*DONNEES-DEBUT*/{
 "id": "poo-notions",
 "version": 1,
 "prefixe": "POO",
 "titre": "Contrôle de notions : programmation orientée objet",
 "titre_court": "programmation orientée objet",
 "niveau": "NSI, terminale",
 "duree": 20,
 "convention": [
  "Pour une sortie, écrire exactement ce qu'affiche `print`, les valeurs séparées par des espaces.",
  "Les lignes des programmes sont numérotées ; la classe du sujet est rappelée en haut."
 ],
 "consigne": "Les questions 4 à 12 utilisent la classe du sujet.",
 "aides": {
  "valeur": "Une seule valeur.",
  "ensemble": "Les noms, séparés par des espaces, dans n'importe quel ordre.",
  "sortie": "Ce qu'affiche le programme, exactement.",
  "ligne": "Écrire seulement ce qui manque."
 },
 "sujets": {
  "1": {
   "commun": {
    "titre": "La classe `Taxi`",
    "texte": "Un taxi part d'une ville, avec un nombre de places (4 par défaut).",
    "programme": "CL",
    "bouton": "Voir la classe"
   },
   "programmes": {
    "CL": {
     "titre": "La classe `Taxi`",
     "code": "class Taxi:\n    def __init__(self, ville, places=4):\n        self.ville = ville\n        self.places = places\n        self.passagers = 0\n\n    def monter(self, n):\n        if self.passagers + n <= self.places:\n            self.passagers = self.passagers + n\n            return True\n        return False\n\n    def places_libres(self):\n        return self.places - self.passagers"
    },
    "A": {
     "titre": "Programme A",
     "code": "t1 = Taxi(\"Mamoudzou\")\nt2 = Taxi(\"Sada\", 8)\nprint(t1.places, t2.places)\nprint(t1.monter(3), t1.monter(2))\nprint(t1.places_libres(), t2.passagers)"
    },
    "B": {
     "code": "t3 = Taxi(\"Chiconi\")\nt4 = t3\nt4.monter(2)\nprint(t3.passagers)"
    },
    "E1": {
     "code": "class Taxi:\n    def __init__(self, ville, places=4):\n        self.ville = ville\n        self.places = places\n        self.passagers = 0\n\n    def places_libres():\n        return self.places - self.passagers\n\nt = Taxi(\"Sada\")\nprint(t.places_libres())",
     "console": "Traceback (most recent call last):\n  File \"programme.py\", line 11, in <module>\n    print(t.places_libres())\n          ~~~~~~~~~~~~~~~^^\nTypeError: Taxi.places_libres() takes 0 positional arguments but 1 was given\n"
    },
    "E2": {
     "code": "class Taxi:\n    def __init__(self, ville, places=4):\n        self.ville = ville\n        self.places = places\n        self.passagers = 0\n\n    def places_libres(self):\n        return places - passagers\n\nt = Taxi(\"Sada\")\nprint(t.places_libres())",
     "console": "Traceback (most recent call last):\n  File \"programme.py\", line 11, in <module>\n    print(t.places_libres())\n          ~~~~~~~~~~~~~~~^^\n  File \"programme.py\", line 8, in places_libres\n    return places - passagers\n           ^^^^^^\nNameError: name 'places' is not defined. Did you mean: 'self.places'?\n"
    },
    "M": {
     "titre": "Méthode à ajouter à la classe `Taxi`",
     "code": "    def descendre(self, n):\n        if n <= self.passagers:\n            ..................",
     "debut": 16
    },
    "C": {
     "titre": "Programme C",
     "code": "t6 = Taxi(\"Dembeni\")\nt6.monter(4)\nt6.descendre(1)\nt6.descendre(5)\nprint(t6.passagers, t6.places_libres())"
    }
   },
   "contextes": {
    "A": {
     "texte": "On exécute le programme A, avec la classe `Taxi` ci-dessus.",
     "programme": "A"
    },
    "ex": {
     "texte": "On ajoute à la classe `Taxi` la méthode `descendre` : si c'est possible, `n` passagers descendent du taxi ; sinon, rien ne change.",
     "programme": "M"
    }
   },
   "q": {
    "q1": {
     "enonce": "On exécute `t1 = Taxi(\"Sada\")`. Que désigne `t1` ?",
     "options": [
      [
       "a",
       "La classe `Taxi`."
      ],
      [
       "b",
       "Une méthode de la classe `Taxi`."
      ],
      [
       "c",
       "Un objet, c'est-à-dire une instance de la classe `Taxi`."
      ],
      [
       "d",
       "Un attribut de la classe `Taxi`."
      ]
     ]
    },
    "q2": {
     "enonce": "Que se passe-t-il quand on exécute `Taxi(\"Sada\")` ?",
     "options": [
      [
       "a",
       "Python appelle la méthode `monter`, qui crée le taxi."
      ],
      [
       "b",
       "Python modifie la classe `Taxi` : son attribut `ville` vaut \"Sada\" pour tous les taxis."
      ],
      [
       "c",
       "Rien : il faut ensuite appeler soi-même `__init__` pour créer le taxi."
      ],
      [
       "d",
       "Python crée un objet, puis appelle `__init__`, avec `self` égal à ce nouvel objet."
      ]
     ]
    },
    "q3": {
     "enonce": "Donner les noms de tous les attributs d'un objet `Taxi`."
    },
    "q4": {
     "enonce": "Qu'affiche la ligne 3 du programme A ?"
    },
    "q5": {
     "enonce": "Qu'affiche la ligne 4 du programme A ?"
    },
    "q6": {
     "enonce": "Qu'affiche la ligne 5 du programme A ?"
    },
    "q7": {
     "enonce": "On exécute ce programme, avec la classe `Taxi`. Qu'affiche-t-il ?",
     "programme": "B"
    },
    "q8": {
     "enonce": "Ce programme s'arrête avec le message d'erreur ci-dessous. Quelle modification le corrige ?",
     "programme": "E1",
     "options": [
      [
       "a",
       "Écrire `print(t.places_libres(t))` à la ligne 11."
      ],
      [
       "b",
       "Écrire `def places_libres(self):` à la ligne 7."
      ],
      [
       "c",
       "Écrire `print(Taxi.places_libres())` à la ligne 11."
      ],
      [
       "d",
       "Écrire `print(t.places_libres)` à la ligne 11, sans parenthèses."
      ]
     ]
    },
    "q9": {
     "enonce": "Ce programme s'arrête avec le message d'erreur ci-dessous. Corriger la ligne 8.",
     "programme": "E2",
     "avant": "return"
    },
    "q10": {
     "enonce": "Écrire l'instruction qui crée un objet `t5` de la classe `Taxi`, pour la ville \"Chiconi\", avec 6 places."
    },
    "q11": {
     "enonce": "Compléter la ligne 18 de la méthode `descendre`."
    },
    "q12": {
     "enonce": "Avec la méthode `descendre` complétée, qu'affiche le programme C ?",
     "programme": "C"
    }
   }
  },
  "2": {
   "commun": {
    "titre": "La classe `Etal`",
    "texte": "Un étal du marché vend un fruit, à un prix en euros le kilo (2 par défaut) ; le stock est en kilos.",
    "programme": "CL",
    "bouton": "Voir la classe"
   },
   "programmes": {
    "CL": {
     "titre": "La classe `Etal`",
     "code": "class Etal:\n    def __init__(self, fruit, prix=2):\n        self.fruit = fruit\n        self.prix = prix\n        self.stock = 0\n\n    def ajouter(self, n):\n        self.stock = self.stock + n\n\n    def vendre(self, n):\n        if n <= self.stock:\n            self.stock = self.stock - n\n            return n * self.prix\n        return 0"
    },
    "A": {
     "titre": "Programme A",
     "code": "e1 = Etal(\"mangue\")\ne2 = Etal(\"banane\", 1)\nprint(e1.prix, e2.prix)\ne1.ajouter(10)\nprint(e1.vendre(4), e1.vendre(8))\nprint(e1.stock, e2.stock)"
    },
    "B": {
     "code": "e3 = Etal(\"ananas\", 3)\ne4 = e3\ne4.ajouter(5)\nprint(e3.stock)"
    },
    "E1": {
     "code": "class Etal:\n    def __init__(self, fruit, prix=2):\n        self.fruit = fruit\n        self.prix = prix\n        self.stock = 0\n\n    def ajouter(n):\n        self.stock = self.stock + n\n\ne = Etal(\"mangue\")\ne.ajouter(10)",
     "console": "Traceback (most recent call last):\n  File \"programme.py\", line 11, in <module>\n    e.ajouter(10)\n    ~~~~~~~~~^^^^\nTypeError: Etal.ajouter() takes 1 positional argument but 2 were given\n"
    },
    "E2": {
     "code": "class Etal:\n    def __init__(self, fruit, prix=2):\n        self.fruit = fruit\n        self.prix = prix\n        self.stock = 0\n\n    def valeur(self):\n        return stock * prix\n\ne = Etal(\"mangue\")\nprint(e.valeur())",
     "console": "Traceback (most recent call last):\n  File \"programme.py\", line 11, in <module>\n    print(e.valeur())\n          ~~~~~~~~^^\n  File \"programme.py\", line 8, in valeur\n    return stock * prix\n           ^^^^^\nNameError: name 'stock' is not defined. Did you mean: 'self.stock'?\n"
    },
    "M": {
     "titre": "Méthode à ajouter à la classe `Etal`",
     "code": "    def baisser_prix(self, remise):\n        if remise < self.prix:\n            ..................",
     "debut": 16
    },
    "C": {
     "titre": "Programme C",
     "code": "e6 = Etal(\"papaye\", 3)\ne6.baisser_prix(1)\ne6.baisser_prix(5)\ne6.ajouter(4)\nprint(e6.prix, e6.vendre(2))"
    }
   },
   "contextes": {
    "A": {
     "texte": "On exécute le programme A, avec la classe `Etal` ci-dessus.",
     "programme": "A"
    },
    "ex": {
     "texte": "On ajoute à la classe `Etal` la méthode `baisser_prix` : si c'est possible, le prix baisse de `remise` euros ; sinon, rien ne change.",
     "programme": "M"
    }
   },
   "q": {
    "q1": {
     "enonce": "Dans l'instruction `e1.vendre(3)`, que désigne `vendre` ?",
     "options": [
      [
       "a",
       "Un attribut de l'objet `e1`."
      ],
      [
       "b",
       "Une méthode de la classe `Etal`."
      ],
      [
       "c",
       "La classe de l'objet `e1`."
      ],
      [
       "d",
       "Le constructeur de la classe `Etal`."
      ]
     ]
    },
    "q2": {
     "enonce": "Dans la méthode `vendre`, que désigne `self` ?",
     "options": [
      [
       "a",
       "L'objet sur lequel la méthode est appelée : `e1` dans `e1.vendre(3)`."
      ],
      [
       "b",
       "La classe `Etal` tout entière, avec tous ses objets."
      ],
      [
       "c",
       "Le nombre de kilos vendus, comme le paramètre `n`."
      ],
      [
       "d",
       "Une valeur à donner à chaque appel : `e1.vendre(e1, 3)`."
      ]
     ]
    },
    "q3": {
     "enonce": "Donner les noms de tous les attributs d'un objet `Etal`."
    },
    "q4": {
     "enonce": "Qu'affiche la ligne 3 du programme A ?"
    },
    "q5": {
     "enonce": "Qu'affiche la ligne 5 du programme A ?"
    },
    "q6": {
     "enonce": "Qu'affiche la ligne 6 du programme A ?"
    },
    "q7": {
     "enonce": "On exécute ce programme, avec la classe `Etal`. Qu'affiche-t-il ?",
     "programme": "B"
    },
    "q8": {
     "enonce": "Ce programme s'arrête avec le message d'erreur ci-dessous. Quelle modification le corrige ?",
     "programme": "E1",
     "options": [
      [
       "a",
       "Écrire `e.ajouter(e, 10)` à la ligne 11."
      ],
      [
       "b",
       "Écrire `Etal.ajouter(10)` à la ligne 11."
      ],
      [
       "c",
       "Écrire `def ajouter(self, n):` à la ligne 7."
      ],
      [
       "d",
       "Écrire `e.ajouter = 10` à la ligne 11."
      ]
     ]
    },
    "q9": {
     "enonce": "Ce programme s'arrête avec le message d'erreur ci-dessous. Corriger la ligne 8.",
     "programme": "E2",
     "avant": "return"
    },
    "q10": {
     "enonce": "Écrire l'instruction qui crée un objet `e5` de la classe `Etal`, pour le fruit \"litchi\", vendu 4 euros le kilo."
    },
    "q11": {
     "enonce": "Compléter la ligne 18 de la méthode `baisser_prix`."
    },
    "q12": {
     "enonce": "Avec la méthode `baisser_prix` complétée, qu'affiche le programme C ?",
     "programme": "C"
    }
   }
  }
 },
 "questions": [
  {
   "id": "q1",
   "nom": "Vocabulaire",
   "type": "qcu"
  },
  {
   "id": "q2",
   "nom": "Constructeur et self",
   "type": "qcu"
  },
  {
   "id": "q3",
   "nom": "Les attributs",
   "type": "ensemble"
  },
  {
   "id": "q4",
   "nom": "Valeur par défaut",
   "type": "sortie",
   "groupe": "A"
  },
  {
   "id": "q5",
   "nom": "Appel de méthode",
   "type": "sortie",
   "groupe": "A"
  },
  {
   "id": "q6",
   "nom": "Chaque objet ses attributs",
   "type": "sortie",
   "groupe": "A"
  },
  {
   "id": "q7",
   "nom": "Deux noms, un objet",
   "type": "valeur"
  },
  {
   "id": "q8",
   "nom": "Trouve l'erreur : self oublié",
   "type": "qcu"
  },
  {
   "id": "q9",
   "nom": "Trouve l'erreur : self. oublié",
   "type": "ligne"
  },
  {
   "id": "q10",
   "nom": "Exercice : créer un objet",
   "type": "ligne",
   "groupe": "ex"
  },
  {
   "id": "q11",
   "nom": "Exercice : compléter une méthode",
   "type": "ligne",
   "groupe": "ex"
  },
  {
   "id": "q12",
   "nom": "Exercice : sortie",
   "type": "sortie",
   "groupe": "ex"
  }
 ],
 "papier": [
  [
   {
    "pleine": [
     "convention",
     "commun"
    ]
   },
   {
    "colonnes": [
     [
      "q1",
      "q2",
      "q3"
     ],
     [
      "ctx:A",
      "q4",
      "q5",
      "q6",
      "q7"
     ]
    ]
   }
  ],
  [
   {
    "pleine": [
     "q8",
     "q9"
    ]
   },
   {
    "colonnes": [
     [
      "ctx:ex",
      "q10",
      "q11"
     ],
     [
      "q12"
     ]
    ]
   }
  ]
 ]
}/*DONNEES-FIN*/;
