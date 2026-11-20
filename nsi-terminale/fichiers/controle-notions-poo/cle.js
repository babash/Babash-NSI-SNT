/* Clé de correction : Contrôle de notions : programmation orientée objet
   Babash - NSI Tani Malandi · contenus CC BY-SA 4.0 · code MIT

   Chargé SEULEMENT par prof.html et corrige.html, jamais par la page élève.
   Ce fichier est public (comme le corrigé PDF) : il empêche l'élève de voir
   sa correction pendant qu'il ou elle compose, il ne protège pas un secret.
   Toutes les réponses sont recalculées par verification/verifier.py.

   « attendu » : la réponse (pour une ligne de code, la liste des écritures
   acceptées, toutes vérifiées par exécution). Diagnostics : « si » = réponse
   exacte (après normalisation) ; « contient » = la réponse contient une de ces
   valeurs (ou ce morceau de code) ; « manque » = il manque une de ces valeurs.
   Le premier diagnostic qui s'applique est affiché ; sinon, l'explication. */

window.CN_CLE = /*CLE-DEBUT*/{
 "1": {
  "q1": {
   "attendu": "c",
   "explication": "`Taxi(\"Sada\")` fabrique un objet à partir de la classe `Taxi` : `t1` est cet objet, une instance de la classe.",
   "diag": [
    {
     "si": "a",
     "texte": "La classe est le plan (`class Taxi:`) ; `t1` est un objet fabriqué à partir de ce plan."
    },
    {
     "si": "d",
     "texte": "Un attribut est une donnée de l'objet, comme `t1.ville`. `t1` est l'objet lui-même."
    },
    {
     "si": "b",
     "texte": "Une méthode s'appelle sur un objet, comme `t1.monter(2)`. `t1` est l'objet."
    }
   ]
  },
  "q2": {
   "attendu": "d",
   "explication": "`Taxi(\"Sada\")` crée un objet, puis appelle automatiquement le constructeur `__init__` : `self` est le nouvel objet, `ville` vaut \"Sada\" et `places` vaut 4 par défaut.",
   "diag": [
    {
     "si": "c",
     "texte": "`__init__` est appelé automatiquement par `Taxi(...)` : on ne l'appelle jamais soi-même."
    },
    {
     "si": "b",
     "texte": "`__init__` donne leur valeur aux attributs du NOUVEL objet (`self.ville`), pas à la classe : chaque taxi a sa ville."
    },
    {
     "si": "a",
     "texte": "`monter` n'est appelée que par `t.monter(n)`. C'est `__init__` qui est appelé à la création."
    }
   ]
  },
  "q3": {
   "attendu": "ville places passagers",
   "explication": "Les attributs sont créés dans `__init__` par `self.… = …` : `ville`, `places` et `passagers`.",
   "diag": [
    {
     "contient": [
      "monter",
      "places_libres"
     ],
     "texte": "`monter` et `places_libres` sont des méthodes (des fonctions de la classe), pas des attributs."
    },
    {
     "manque": [
      "passagers"
     ],
     "texte": "`passagers` est un attribut même s'il n'est pas un paramètre de `__init__` : il est créé par `self.passagers = 0`."
    },
    {
     "contient": [
      "n"
     ],
     "texte": "`n` est un paramètre de la méthode `monter`, pas un attribut."
    }
   ]
  },
  "q4": {
   "attendu": "4 8",
   "explication": "`t1` est créé sans nombre de places : la valeur par défaut, 4, est utilisée. `t2` a 8 places.",
   "diag": [
    {
     "si": "4 4",
     "texte": "`Taxi(\"Sada\", 8)` donne 8 à `places` : la valeur par défaut ne sert que si l'appel ne donne rien."
    },
    {
     "si": "Mamoudzou Sada",
     "texte": "C'est l'attribut `ville`. La ligne 3 affiche l'attribut `places`."
    },
    {
     "si": "0 8",
     "texte": "`t1` reçoit la valeur par défaut, 4, pas 0."
    }
   ]
  },
  "q5": {
   "attendu": "True False",
   "explication": "0 + 3 ≤ 4 : 3 passagers montent, `True`. Puis 3 + 2 > 4 : personne ne monte, `False`.",
   "diag": [
    {
     "si": "True True",
     "texte": "Au deuxième appel, il y a déjà 3 passagers : 3 + 2 > 4, la méthode renvoie `False`."
    },
    {
     "si": "3 2",
     "texte": "`monter` renvoie un booléen, `True` ou `False`, pas le nombre de passagers."
    },
    {
     "si": "None None",
     "texte": "`monter` renvoie `True` ou `False` (`return True`, `return False`)."
    }
   ]
  },
  "q6": {
   "attendu": "1 0",
   "explication": "Seuls 3 passagers sont montés dans `t1` : il reste 4 − 3 = 1 place libre. `t2` a ses propres attributs : 0 passager.",
   "diag": [
    {
     "si": "-1 0",
     "texte": "Le deuxième `monter` a renvoyé `False` : l'objet n'a pas changé, il a 3 passagers."
    },
    {
     "si": "1 3",
     "texte": "Chaque objet a ses propres attributs : monter dans `t1` ne change pas `t2`."
    },
    {
     "si": "4 0",
     "texte": "`t1.monter(3)` a bien fait monter 3 passagers : il reste 1 place."
    }
   ]
  },
  "q7": {
   "attendu": "2",
   "explication": "`t4 = t3` ne crée pas de nouvel objet : `t3` et `t4` désignent le même taxi. Les 2 passagers montés par `t4` sont dans `t3`.",
   "diag": [
    {
     "si": "0",
     "texte": "`t4 = t3` ne copie pas le taxi : les deux noms désignent le même objet."
    },
    {
     "si": "True",
     "texte": "`print(t3.passagers)` affiche l'attribut `passagers`, pas ce que renvoie `monter`."
    }
   ]
  },
  "q8": {
   "attendu": "b",
   "explication": "Le message dit que `places_libres` attend 0 argument, mais en reçoit 1 : l'objet `t`, donné automatiquement à `self`. Il faut `self` en premier paramètre : `def places_libres(self):`.",
   "diag": [
    {
     "si": "a",
     "texte": "L'objet est déjà donné automatiquement : la méthode recevrait 2 arguments au lieu de 0."
    },
    {
     "si": "c",
     "texte": "Il n'y aurait plus d'erreur à l'appel, mais `self` n'existe pas dans la méthode : `NameError`."
    },
    {
     "si": "d",
     "texte": "Sans parenthèses, la méthode n'est pas appelée : Python affiche « <bound method … », pas un nombre."
    }
   ]
  },
  "q9": {
   "attendu": [
    "self.places-self.passagers",
    "(self.places-self.passagers)",
    "-self.passagers+self.places"
   ],
   "affiche": "return self.places - self.passagers",
   "explication": "Dans une méthode, un attribut s'écrit toujours avec `self.` : `return self.places - self.passagers`. Le message le suggère : « Did you mean: 'self.places'? » (« Vouliez-vous dire… »).",
   "diag": [
    {
     "si": "self.places-passagers",
     "texte": "`passagers` est aussi un attribut : il faut `self.passagers`."
    },
    {
     "si": "places-self.passagers",
     "texte": "`places` est aussi un attribut : il faut `self.places`."
    },
    {
     "contient": [
      "t."
     ],
     "texte": "Dans la classe, on ne connaît pas `t` : c'est `self` qui désigne l'objet."
    }
   ]
  },
  "q10": {
   "attendu": [
    "t5=Taxi(\"Chiconi\",6)",
    "t5=Taxi(\"Chiconi\",places=6)",
    "t5=Taxi(ville=\"Chiconi\",places=6)",
    "t5=Taxi(places=6,ville=\"Chiconi\")"
   ],
   "affiche": "t5 = Taxi(\"Chiconi\", 6)",
   "explication": "On appelle la classe comme une fonction, avec les paramètres de `__init__` sans `self` : `t5 = Taxi(\"Chiconi\", 6)`.",
   "diag": [
    {
     "contient": [
      "self"
     ],
     "texte": "On ne donne jamais `self` à l'appel : Python le donne tout seul."
    },
    {
     "si": "t5=Taxi(6,\"Chiconi\")",
     "texte": "L'ordre compte : d'abord la ville, puis le nombre de places."
    },
    {
     "si": "t5=Taxi(\"Chiconi\")",
     "texte": "Sans le 6, le taxi aurait 4 places, la valeur par défaut."
    },
    {
     "contient": [
      "__init__"
     ],
     "texte": "On n'appelle pas `__init__` soi-même : `Taxi(...)` le fait."
    }
   ]
  },
  "q11": {
   "attendu": [
    "self.passagers=self.passagers-n",
    "self.passagers-=n",
    "self.passagers=-n+self.passagers"
   ],
   "affiche": "self.passagers = self.passagers - n",
   "explication": "On modifie l'attribut de l'objet : `self.passagers = self.passagers - n` (ou `self.passagers -= n`).",
   "diag": [
    {
     "si": "passagers=passagers-n",
     "texte": "Sans `self.`, `passagers` serait une variable locale inconnue : `NameError`."
    },
    {
     "si": "self.passagers=self.passagers+n",
     "texte": "Des passagers descendent : on retire `n`."
    },
    {
     "si": "self.passagers=n",
     "texte": "Il resterait `n` passagers : on veut en retirer `n`."
    },
    {
     "contient": [
      "return"
     ],
     "texte": "Renvoyer un calcul ne modifie pas l'objet : il faut changer l'attribut `self.passagers`."
    }
   ]
  },
  "q12": {
   "attendu": "3 1",
   "explication": "4 passagers montent ; 1 descend (1 ≤ 4) : il en reste 3. Puis 5 > 3 : rien ne change. 3 passagers, 4 − 3 = 1 place libre.",
   "diag": [
    {
     "si": "0 4",
     "texte": "`descendre(5)` ne fait rien : il n'y a que 3 passagers, et 5 > 3."
    },
    {
     "si": "-2 6",
     "texte": "`descendre(5)` ne fait rien : la condition `n <= self.passagers` est fausse."
    },
    {
     "si": "4 0",
     "texte": "`descendre(1)` fait bien descendre 1 passager."
    }
   ]
  }
 },
 "2": {
  "q1": {
   "attendu": "b",
   "explication": "`vendre` est une fonction de la classe `Etal`, appelée sur l'objet `e1` avec la notation pointée : c'est une méthode.",
   "diag": [
    {
     "si": "a",
     "texte": "Un attribut est une donnée, comme `e1.stock`, sans parenthèses. `vendre(3)` s'appelle : c'est une méthode."
    },
    {
     "si": "d",
     "texte": "Le constructeur est `__init__`, appelé par `Etal(...)`. `vendre` est une autre méthode."
    },
    {
     "si": "c",
     "texte": "La classe de `e1` est `Etal`. `vendre` est une de ses méthodes."
    }
   ]
  },
  "q2": {
   "attendu": "a",
   "explication": "`self` est l'objet sur lequel la méthode travaille : `e1.vendre(3)` est traduit en `Etal.vendre(e1, 3)`, donc `self` est `e1` et `n` vaut 3.",
   "diag": [
    {
     "si": "d",
     "texte": "On ne donne jamais `self` à l'appel : `e1.vendre(3)` suffit, Python donne `e1` tout seul."
    },
    {
     "si": "b",
     "texte": "`self` est un seul objet, celui de l'appel : chaque étal a ses propres attributs."
    },
    {
     "si": "c",
     "texte": "Le nombre de kilos est `n`, le deuxième paramètre. `self` est le premier : l'objet."
    }
   ]
  },
  "q3": {
   "attendu": "fruit prix stock",
   "explication": "Les attributs sont créés dans `__init__` par `self.… = …` : `fruit`, `prix` et `stock`.",
   "diag": [
    {
     "contient": [
      "ajouter",
      "vendre"
     ],
     "texte": "`ajouter` et `vendre` sont des méthodes (des fonctions de la classe), pas des attributs."
    },
    {
     "manque": [
      "stock"
     ],
     "texte": "`stock` est un attribut même s'il n'est pas un paramètre de `__init__` : il est créé par `self.stock = 0`."
    },
    {
     "contient": [
      "n"
     ],
     "texte": "`n` est un paramètre des méthodes, pas un attribut."
    }
   ]
  },
  "q4": {
   "attendu": "2 1",
   "explication": "`e1` est créé sans prix : la valeur par défaut, 2, est utilisée. `e2` coûte 1 euro le kilo.",
   "diag": [
    {
     "si": "2 2",
     "texte": "`Etal(\"goyave\", 1)` donne 1 à `prix` : la valeur par défaut ne sert que si l'appel ne donne rien."
    },
    {
     "si": "mangue goyave",
     "texte": "C'est l'attribut `fruit`. La ligne 3 affiche l'attribut `prix`."
    },
    {
     "si": "0 1",
     "texte": "`e1` reçoit la valeur par défaut, 2, pas 0."
    }
   ]
  },
  "q5": {
   "attendu": "8 0",
   "explication": "Stock 10 : on vend 4 kilos à 2 euros, la méthode renvoie 8, il reste 6 kilos. Puis 8 > 6 : rien n'est vendu, elle renvoie 0.",
   "diag": [
    {
     "si": "8 16",
     "texte": "Au deuxième appel, il ne reste que 6 kilos : 8 > 6, la méthode renvoie 0."
    },
    {
     "si": "4 0",
     "texte": "`vendre` renvoie le prix payé, `n * self.prix` = 4 × 2 = 8, pas le nombre de kilos."
    },
    {
     "si": "True False",
     "texte": "`vendre` renvoie un nombre : `n * self.prix` ou 0."
    }
   ]
  },
  "q6": {
   "attendu": "6 0",
   "explication": "Seuls 4 kilos ont été vendus : il reste 10 − 4 = 6 kilos. `e2` a ses propres attributs : son stock est 0.",
   "diag": [
    {
     "si": "-2 0",
     "texte": "Le deuxième `vendre` a renvoyé 0 : l'objet n'a pas changé, il reste 6 kilos."
    },
    {
     "si": "6 6",
     "texte": "Chaque objet a ses propres attributs : vendre sur `e1` ne change pas `e2`."
    },
    {
     "si": "10 0",
     "texte": "`vendre(4)` retire bien 4 kilos du stock."
    }
   ]
  },
  "q7": {
   "attendu": "5",
   "explication": "`e4 = e3` ne crée pas de nouvel objet : `e3` et `e4` désignent le même étal. Les 5 kilos ajoutés par `e4` sont dans `e3`.",
   "diag": [
    {
     "si": "0",
     "texte": "`e4 = e3` ne copie pas l'étal : les deux noms désignent le même objet."
    },
    {
     "si": "15",
     "texte": "`stock` est un nombre de kilos : il part de 0, puis on ajoute 5."
    }
   ]
  },
  "q8": {
   "attendu": "c",
   "explication": "Le message dit que `ajouter` attend 1 argument, mais en reçoit 2 : l'objet `e`, donné automatiquement, et 10. Il faut `self` en premier paramètre : `def ajouter(self, n):`.",
   "diag": [
    {
     "si": "a",
     "texte": "L'objet est déjà donné automatiquement : la méthode recevrait 3 arguments au lieu de 1."
    },
    {
     "si": "b",
     "texte": "Il n'y aurait plus d'erreur à l'appel, mais `self` n'existe pas dans la méthode : `NameError`."
    },
    {
     "si": "d",
     "texte": "Cela remplace la méthode de l'objet par le nombre 10 : le stock ne change pas."
    }
   ]
  },
  "q9": {
   "attendu": [
    "self.stock*self.prix",
    "self.prix*self.stock",
    "(self.stock*self.prix)"
   ],
   "affiche": "return self.stock * self.prix",
   "explication": "Dans une méthode, un attribut s'écrit toujours avec `self.` : `return self.stock * self.prix`. Le message le suggère : « Did you mean: 'self.stock'? » (« Vouliez-vous dire… »).",
   "diag": [
    {
     "si": "self.stock*prix",
     "texte": "`prix` est aussi un attribut : il faut `self.prix`."
    },
    {
     "si": "stock*self.prix",
     "texte": "`stock` est aussi un attribut : il faut `self.stock`."
    },
    {
     "contient": [
      "e."
     ],
     "texte": "Dans la classe, on ne connaît pas `e` : c'est `self` qui désigne l'objet."
    }
   ]
  },
  "q10": {
   "attendu": [
    "e5=Etal(\"litchi\",4)",
    "e5=Etal(\"litchi\",prix=4)",
    "e5=Etal(fruit=\"litchi\",prix=4)",
    "e5=Etal(prix=4,fruit=\"litchi\")"
   ],
   "affiche": "e5 = Etal(\"litchi\", 4)",
   "explication": "On appelle la classe comme une fonction, avec les paramètres de `__init__` sans `self` : `e5 = Etal(\"litchi\", 4)`.",
   "diag": [
    {
     "contient": [
      "self"
     ],
     "texte": "On ne donne jamais `self` à l'appel : Python le donne tout seul."
    },
    {
     "si": "e5=Etal(4,\"litchi\")",
     "texte": "L'ordre compte : d'abord le fruit, puis le prix."
    },
    {
     "si": "e5=Etal(\"litchi\")",
     "texte": "Sans le 4, le prix serait 2 euros, la valeur par défaut."
    },
    {
     "contient": [
      "__init__"
     ],
     "texte": "On n'appelle pas `__init__` soi-même : `Etal(...)` le fait."
    }
   ]
  },
  "q11": {
   "attendu": [
    "self.prix=self.prix-remise",
    "self.prix-=remise",
    "self.prix=-remise+self.prix"
   ],
   "affiche": "self.prix = self.prix - remise",
   "explication": "On modifie l'attribut de l'objet : `self.prix = self.prix - remise` (ou `self.prix -= remise`).",
   "diag": [
    {
     "si": "prix=prix-remise",
     "texte": "Sans `self.`, `prix` serait une variable locale inconnue : `NameError`."
    },
    {
     "si": "self.prix=self.prix+remise",
     "texte": "Le prix baisse : on retire `remise`."
    },
    {
     "si": "self.prix=remise",
     "texte": "Le prix deviendrait égal à la remise : on veut retirer la remise."
    },
    {
     "contient": [
      "return"
     ],
     "texte": "Renvoyer un calcul ne modifie pas l'objet : il faut changer l'attribut `self.prix`."
    }
   ]
  },
  "q12": {
   "attendu": "2 4",
   "explication": "Prix 3, remise 1 (1 < 3) : le prix passe à 2. Remise 5 : 5 > 2, rien ne change. On ajoute 4 kilos et on en vend 2 à 2 euros : 4.",
   "diag": [
    {
     "si": "-3 0",
     "texte": "`baisser_prix(5)` ne fait rien : la condition `remise < self.prix` est fausse (5 > 2)."
    },
    {
     "si": "3 6",
     "texte": "`baisser_prix(1)` fait bien passer le prix de 3 à 2."
    },
    {
     "si": "2 2",
     "texte": "`vendre(2)` renvoie le prix payé : 2 kilos × 2 euros = 4."
    }
   ]
  }
 }
}/*CLE-FIN*/;

(function () {
  'use strict';
  var CN = window.CN, CLE = window.CN_CLE;

  function egal(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  /* Corrige une question : { juste, vide, attendu, texte } */
  function corrigerQuestion(q, sujet, r) {
    var k = CLE[sujet][q.id], f = CN.formeNormale(q, sujet, r), juste, estVide = CN.vide(r);
    var attendus = q.type === 'ligne' ? k.attendu : [k.attendu];
    juste = !estVide && attendus.some(function (a) { return egal(f, CN.formeNormale(q, sujet, a)); });
    var texte = k.explication;
    if (!juste && !estVide) {
      for (var i = 0; i < (k.diag || []).length; i++) {
        var d = k.diag[i], ok = false;
        if ('si' in d) ok = egal(f, CN.formeNormale(q, sujet, d.si));
        if ('contient' in d) ok = d.contient.some(function (x) {
          return q.type === 'ligne' ? String(f).indexOf(CN.ligneCode(x)) >= 0
            : (Array.isArray(f) ? f : [f]).indexOf(CN.jetons(x)[0]) >= 0;
        });
        if ('manque' in d) ok = Array.isArray(f) && d.manque.some(function (x) { return f.indexOf(CN.jetons(x)[0]) < 0; });
        if (ok) { texte = d.texte + ' ' + k.explication; break; }
      }
    }
    return { juste: juste, vide: estVide, attendu: k.affiche || (q.type === 'ligne' ? k.attendu[0] : k.attendu),
      texte: estVide ? 'Pas de réponse. ' + k.explication : texte };
  }

  function corrigerCopie(copie) {
    var D = CN.DONNEES, details = [], points = 0;
    if (!CLE[copie.sujet]) throw new Error('Sujet inconnu : ' + copie.sujet);
    D.questions.forEach(function (q, i) {
      var c = corrigerQuestion(q, copie.sujet, copie.reponses[i]);
      c.question = q; c.donne = copie.reponses[i];
      if (c.juste) points++;
      details.push(c);
    });
    return { points: points, total: D.questions.length, sur20: Math.round(points * 200 / D.questions.length) / 10, details: details };
  }

  window.CLE = { donnees: CLE, corrigerCopie: corrigerCopie, corrigerQuestion: corrigerQuestion };
})();
