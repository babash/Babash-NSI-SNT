/* Contrôle de notions : piles et files (NSI, terminale)
   Babash - NSI Tani Malandi · contenus CC BY-SA 4.0 · code MIT

   Énoncés, programmes et consoles du contrôle, JAMAIS les réponses : la clé
   de correction est dans cle.js, que seules la page prof et le corrigé chargent.
   Les consoles sont les sorties réelles de Python 3.13 (seul le dossier est
   retiré des chemins de fichiers).

   Le bloc entre les deux marqueurs DONNEES est du JSON pur : le script
   verification/verifier.py le relit pour tout recalculer par exécution. */

window.CN_DONNEES = /*DONNEES-DEBUT*/{
 "id": "piles-files-notions",
 "version": 1,
 "prefixe": "PIL",
 "titre": "Contrôle de notions : piles et files",
 "titre_court": "piles et files",
 "niveau": "NSI, terminale",
 "duree": 20,
 "convention": [
  "Une pile s'écrit du sommet vers le bas : « 3, 1, 4 » veut dire que 3 est au sommet.",
  "Une file s'écrit de la tête (le prochain élément à sortir) vers la queue (le dernier arrivé).",
  "Les classes `Pile` et `File` du cours sont dans le module `pile_file` : `Pile()`, `empiler(e)`, `depiler()`, `sommet()`, `est_vide()`, `taille()` ; `File()`, `enfiler(e)`, `defiler()`, `tete()`, `est_vide()`, `taille()`.",
  "`depiler()` et `defiler()` retirent l'élément et le renvoient ; `sommet()` et `tete()` le renvoient sans le retirer."
 ],
 "consigne": "Pour une liste de valeurs, les écrire dans l'ordre demandé, séparées par des espaces.",
 "aides": {
  "valeur": "Une seule valeur.",
  "liste": "Les valeurs dans l'ordre demandé, séparées par des espaces.",
  "sortie": "Ce qu'affiche le programme, exactement.",
  "ligne": "Écrire seulement ce qui manque."
 },
 "module": {
  "nom": "pile_file.py",
  "code": "class Pile:\n    def __init__(self):\n        self.contenu = []\n    def est_vide(self):\n        return len(self.contenu) == 0\n    def empiler(self, e):\n        self.contenu.append(e)\n    def depiler(self):\n        return self.contenu.pop()\n    def sommet(self):\n        return self.contenu[-1]\n    def taille(self):\n        return len(self.contenu)\n\nclass File:\n    def __init__(self):\n        self.contenu = []\n    def est_vide(self):\n        return len(self.contenu) == 0\n    def enfiler(self, e):\n        self.contenu.append(e)\n    def defiler(self):\n        return self.contenu.pop(0)\n    def tete(self):\n        return self.contenu[0]\n    def taille(self):\n        return len(self.contenu)"
 },
 "sujets": {
  "1": {
   "programmes": {
    "P4": {
     "code": "p = Pile()\np.empiler(4)\np.empiler(1)\np.empiler(8)\np.depiler()\np.empiler(5)\np.empiler(3)\np.depiler()"
    },
    "P5": {
     "code": "f = File()\nf.enfiler(\"Sada\")\nf.enfiler(\"Chiconi\")\nf.enfiler(\"Koungou\")\nx = f.defiler()\nf.enfiler(x)\nf.defiler()"
    },
    "P6": {
     "code": "p = Pile()\nfor mot in [\"taxi\", \"barge\", \"lagon\"]:\n    p.empiler(mot)\nf = File()\nwhile not p.est_vide():\n    f.enfiler(p.depiler())\nprint(f.defiler(), f.taille())"
    },
    "ERR": {
     "code": "from pile_file import Pile\np = Pile()\np.empiler(10)\np.empiler(20)\ntotal = 0\nfor i in range(3):\n    total = total + p.depiler()\nprint(total)",
     "console": "Traceback (most recent call last):\n  File \"programme.py\", line 7, in <module>\n    total = total + p.depiler()\n                    ~~~~~~~~~^^\n  File \"pile_file.py\", line 9, in depiler\n    return self.contenu.pop()\n           ~~~~~~~~~~~~~~~~^^\nIndexError: pop from empty list\n"
    },
    "EX": {
     "titre": "La fonction `compter`",
     "code": "def compter(p, x):\n    aux = Pile()\n    n = 0\n    while not p.est_vide():\n        e = p.depiler()\n        if e == x:\n            n = n + 1\n        aux.empiler(e)\n    while not aux.est_vide():\n        p.empiler(..............)\n    return n"
    }
   },
   "contextes": {
    "err": {
     "texte": "Ce programme doit additionner tous les éléments de la pile `p`. Il s'arrête avec le message d'erreur ci-dessous.",
     "programme": "ERR"
    },
    "ex": {
     "texte": "La fonction `compter` doit renvoyer le nombre d'éléments égaux à `x` dans la pile `p`, et laisser `p` comme au départ. La pile `p` contient, du sommet vers le bas : 2, 5, 2, 7.",
     "programme": "EX"
    }
   },
   "q": {
    "q1": {
     "enonce": "Une pile contient plusieurs éléments. Quel élément l'instruction `p.depiler()` retire-t-elle ?",
     "options": [
      [
       "a",
       "Le premier élément empilé, tout en bas de la pile."
      ],
      [
       "b",
       "L'élément du milieu de la pile."
      ],
      [
       "c",
       "Le dernier élément empilé, au sommet de la pile."
      ],
      [
       "d",
       "Aucun : elle renvoie le sommet sans le retirer."
      ]
     ]
    },
    "q2": {
     "enonce": "Laquelle de ces situations se modélise naturellement par une file ?",
     "options": [
      [
       "a",
       "Le bouton Annuler d'un traitement de texte, qui défait la dernière action."
      ],
      [
       "b",
       "Les demandes envoyées à l'imprimante du CDI, imprimées dans l'ordre d'arrivée."
      ],
      [
       "c",
       "La boîte de chips en tube, où l'on prend toujours la chips du dessus."
      ],
      [
       "d",
       "Le bouton Précédent du navigateur, qui revient à la dernière page vue."
      ]
     ]
    },
    "q3": {
     "enonce": "La pile `p` contient, du sommet vers le bas : 7, 2, 9. On exécute `x = p.sommet()`, puis `y = p.depiler()`. Que contient `p` ensuite, du sommet vers le bas ?"
    },
    "q4": {
     "enonce": "On exécute ce programme. Que contient `p` à la fin, du sommet vers le bas ?",
     "programme": "P4"
    },
    "q5": {
     "enonce": "On exécute ce programme. Que contient `f` à la fin, de la tête vers la queue ?",
     "programme": "P5"
    },
    "q6": {
     "enonce": "Qu'affiche ce programme ?",
     "programme": "P6"
    },
    "q7": {
     "enonce": "Que s'est-il passé ?",
     "options": [
      [
       "a",
       "La variable `total` n'existe pas encore quand la boucle commence."
      ],
      [
       "b",
       "On ne peut pas additionner des éléments dépilés : il faut d'abord les ranger dans une liste."
      ],
      [
       "c",
       "`depiler()` retire l'élément du bas de la pile, et il n'y en a pas."
      ],
      [
       "d",
       "Au troisième tour de boucle, la pile est vide : `depiler()` n'a plus rien à retirer."
      ]
     ]
    },
    "q8": {
     "enonce": "On remplace la ligne 6 par une boucle `while`. Compléter sa condition pour que le programme additionne tous les éléments de la pile, quelle que soit sa taille.",
     "avant": "while",
     "apres": ":"
    },
    "q9": {
     "enonce": "Une pile est représentée par une liste Python `pile` : le sommet est le dernier élément de la liste. Quelle expression donne le sommet sans modifier la pile ?",
     "options": [
      [
       "a",
       "`pile.pop()`"
      ],
      [
       "b",
       "`pile[0]`"
      ],
      [
       "c",
       "`pile[len(pile)]`"
      ],
      [
       "d",
       "`pile[-1]`"
      ]
     ]
    },
    "q10": {
     "enonce": "Que renvoie `compter(p, 2)` ?"
    },
    "q11": {
     "enonce": "Que contient `aux` juste après la première boucle `while` (lignes 4 à 8), du sommet vers le bas ?"
    },
    "q12": {
     "enonce": "Compléter la ligne 10 pour que `p` retrouve son état de départ.",
     "avant": "p.empiler(",
     "apres": ")"
    }
   }
  },
  "2": {
   "programmes": {
    "P4": {
     "code": "p = Pile()\np.empiler(6)\np.empiler(2)\np.depiler()\np.empiler(7)\np.empiler(9)\np.depiler()\np.empiler(3)"
    },
    "P5": {
     "code": "f = File()\nf.enfiler(\"Pamandzi\")\nf.enfiler(\"Dembeni\")\nf.enfiler(\"Ouangani\")\nf.defiler()\ny = f.defiler()\nf.enfiler(y)"
    },
    "P6": {
     "code": "f = File()\nfor n in [3, 8, 5]:\n    f.enfiler(n)\np = Pile()\nwhile not f.est_vide():\n    p.empiler(f.defiler())\nprint(p.sommet(), p.taille())"
    },
    "ERR": {
     "code": "from pile_file import File\nf = File()\nfor nom in [\"Anli\", \"Faïza\", \"Nayma\"]:\n    f.enfiler(nom)\nservis = 0\nwhile f.taille() >= 0:\n    print(\"Au tour de\", f.defiler())\n    servis = servis + 1\nprint(servis, \"personnes servies\")",
     "console": "Au tour de Anli\nAu tour de Faïza\nAu tour de Nayma\nTraceback (most recent call last):\n  File \"programme.py\", line 7, in <module>\n    print(\"Au tour de\", f.defiler())\n                        ~~~~~~~~~^^\n  File \"pile_file.py\", line 23, in defiler\n    return self.contenu.pop(0)\n           ~~~~~~~~~~~~~~~~^^^\nIndexError: pop from empty list\n"
    },
    "EX": {
     "titre": "La fonction `maximum`",
     "code": "def maximum(f):\n    aux = File()\n    m = f.tete()\n    while not f.est_vide():\n        e = f.defiler()\n        if e > m:\n            m = e\n        aux.enfiler(e)\n    while not aux.est_vide():\n        f.enfiler(..............)\n    return m"
    }
   },
   "contextes": {
    "err": {
     "texte": "Ce programme doit appeler, dans l'ordre d'arrivée, toutes les personnes de la file `f`. Il s'arrête avec le message d'erreur ci-dessous.",
     "programme": "ERR"
    },
    "ex": {
     "texte": "La fonction `maximum` doit renvoyer le plus grand élément de la file `f`, qui n'est pas vide, et laisser `f` comme au départ. La file `f` contient, de la tête vers la queue : 4, 9, 2, 6.",
     "programme": "EX"
    }
   },
   "q": {
    "q1": {
     "enonce": "Une file contient plusieurs éléments. Quel élément l'instruction `f.defiler()` retire-t-elle ?",
     "options": [
      [
       "a",
       "Le dernier élément enfilé, à la queue de la file."
      ],
      [
       "b",
       "Le premier élément enfilé, à la tête de la file."
      ],
      [
       "c",
       "L'élément du milieu de la file."
      ],
      [
       "d",
       "Aucun : elle renvoie la tête sans la retirer."
      ]
     ]
    },
    "q2": {
     "enonce": "Laquelle de ces situations se modélise naturellement par une pile ?",
     "options": [
      [
       "a",
       "La queue au doukabé, où l'on sert les personnes dans l'ordre d'arrivée."
      ],
      [
       "b",
       "Les voitures du bouchon jusqu'à Mamoudzou, sur une route à une seule voie."
      ],
      [
       "c",
       "Le bouton Annuler d'un traitement de texte, qui défait d'abord la dernière action."
      ],
      [
       "d",
       "Les demandes envoyées à l'imprimante du CDI, imprimées dans l'ordre d'arrivée."
      ]
     ]
    },
    "q3": {
     "enonce": "La file `f` contient, de la tête vers la queue : 5, 3, 8. On exécute `x = f.tete()`, puis `y = f.defiler()`. Que contient `f` ensuite, de la tête vers la queue ?"
    },
    "q4": {
     "enonce": "On exécute ce programme. Que contient `p` à la fin, du sommet vers le bas ?",
     "programme": "P4"
    },
    "q5": {
     "enonce": "On exécute ce programme. Que contient `f` à la fin, de la tête vers la queue ?",
     "programme": "P5"
    },
    "q6": {
     "enonce": "Qu'affiche ce programme ?",
     "programme": "P6"
    },
    "q7": {
     "enonce": "Que s'est-il passé ?",
     "options": [
      [
       "a",
       "`defiler()` ne fonctionne que sur une pile : il faut écrire `f.depiler()`."
      ],
      [
       "b",
       "La condition `f.taille() >= 0` est encore vraie quand la file est vide : on défile une file vide."
      ],
      [
       "c",
       "La variable `servis` n'existe pas encore quand la boucle commence."
      ],
      [
       "d",
       "Le prénom « Faïza » contient un tréma : Python ne peut pas l'enfiler."
      ]
     ]
    },
    "q8": {
     "enonce": "Compléter la condition de la ligne 6 pour que le programme appelle toutes les personnes de la file, sans erreur, quelle que soit sa taille.",
     "avant": "while",
     "apres": ":"
    },
    "q9": {
     "enonce": "Une file est représentée par une liste Python `file` : la tête est l'élément d'indice 0. Quelle instruction défile, c'est-à-dire retire la tête et la renvoie ?",
     "options": [
      [
       "a",
       "`file.pop(0)`"
      ],
      [
       "b",
       "`file.pop()`"
      ],
      [
       "c",
       "`file[0]`"
      ],
      [
       "d",
       "`file.append(0)`"
      ]
     ]
    },
    "q10": {
     "enonce": "Que renvoie `maximum(f)` ?"
    },
    "q11": {
     "enonce": "Que contient `aux` juste après la première boucle `while` (lignes 4 à 8), de la tête vers la queue ?"
    },
    "q12": {
     "enonce": "Compléter la ligne 10 pour que `f` retrouve son état de départ.",
     "avant": "f.enfiler(",
     "apres": ")"
    }
   }
  }
 },
 "questions": [
  {
   "id": "q1",
   "nom": "Règle de la structure",
   "type": "qcu"
  },
  {
   "id": "q2",
   "nom": "Pile ou file",
   "type": "qcu"
  },
  {
   "id": "q3",
   "nom": "Lire ou retirer",
   "type": "liste"
  },
  {
   "id": "q4",
   "nom": "État d'une pile",
   "type": "liste"
  },
  {
   "id": "q5",
   "nom": "État d'une file",
   "type": "liste"
  },
  {
   "id": "q6",
   "nom": "Sortie d'un programme",
   "type": "sortie"
  },
  {
   "id": "q7",
   "nom": "Trouve l'erreur : le message",
   "type": "qcu",
   "groupe": "err"
  },
  {
   "id": "q8",
   "nom": "Trouve l'erreur : la correction",
   "type": "ligne",
   "groupe": "err"
  },
  {
   "id": "q9",
   "nom": "Avec une liste Python",
   "type": "qcu"
  },
  {
   "id": "q10",
   "nom": "Exercice : valeur renvoyée",
   "type": "valeur",
   "groupe": "ex"
  },
  {
   "id": "q11",
   "nom": "Exercice : la pile ou file auxiliaire",
   "type": "liste",
   "groupe": "ex"
  },
  {
   "id": "q12",
   "nom": "Exercice : compléter une ligne",
   "type": "ligne",
   "groupe": "ex"
  }
 ],
 "papier": [
  [
   {
    "pleine": [
     "convention"
    ]
   },
   {
    "colonnes": [
     [
      "q1",
      "q2",
      "q3",
      "q9"
     ],
     [
      "q4",
      "q5",
      "q6"
     ]
    ]
   }
  ],
  [
   {
    "pleine": [
     "ctx:err"
    ]
   },
   {
    "colonnes": [
     [
      "q7"
     ],
     [
      "q8"
     ]
    ]
   },
   {
    "colonnes": [
     [
      "ctx:ex"
     ],
     [
      "q10",
      "q11",
      "q12"
     ]
    ]
   }
  ]
 ]
}/*DONNEES-FIN*/;
