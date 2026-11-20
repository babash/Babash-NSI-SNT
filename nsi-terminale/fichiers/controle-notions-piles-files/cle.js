/* Clé de correction : Contrôle de notions : piles et files
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
   "explication": "Une pile est LIFO : dernier entré, premier sorti. `depiler()` retire le sommet, c'est-à-dire le dernier élément empilé, et le renvoie.",
   "diag": [
    {
     "si": "a",
     "texte": "C'est la règle d'une file (FIFO : premier entré, premier sorti)."
    },
    {
     "si": "d",
     "texte": "C'est ce que fait `sommet()`. `depiler()` retire le sommet."
    },
    {
     "si": "b",
     "texte": "On ne touche jamais au milieu d'une pile : tout se passe au sommet."
    }
   ]
  },
  "q2": {
   "attendu": "b",
   "explication": "Les impressions sont traitées dans l'ordre d'arrivée : premier entré, premier sorti, c'est une file. Annuler, Précédent et le tube de chips sont des piles.",
   "diag": [
    {
     "si": "c",
     "texte": "Dans le tube, la chips du dessus est la dernière rangée : dernier entré, premier sorti, c'est une pile."
    },
    {
     "si": "a",
     "texte": "Annuler défait d'abord la dernière action : c'est une pile."
    },
    {
     "si": "d",
     "texte": "Précédent revient à la page la plus récente : c'est une pile."
    }
   ]
  },
  "q3": {
   "attendu": "2 9",
   "explication": "`sommet()` lit 7 sans le retirer ; `depiler()` retire 7. Il reste 2, 9.",
   "diag": [
    {
     "si": "9",
     "texte": "`sommet()` ne retire rien : seul `depiler()` retire le sommet."
    },
    {
     "si": "7 2 9",
     "texte": "`depiler()` retire bien le sommet, 7."
    },
    {
     "si": "7 2",
     "texte": "Le sommet est le premier nombre écrit (7), pas le dernier."
    }
   ]
  },
  "q4": {
   "attendu": "5 1 4",
   "explication": "Après chaque ligne, du sommet vers le bas : 4 | 1, 4 | 8, 1, 4 | 1, 4 | 5, 1, 4 | 3, 5, 1, 4 | 5, 1, 4.",
   "diag": [
    {
     "si": "4 1 5",
     "texte": "Ce sont les bons éléments, lus du bas vers le haut. On écrit la pile du sommet vers le bas."
    },
    {
     "si": "3 5 8",
     "texte": "Tu as retiré à chaque fois le plus ancien élément, comme dans une file. `depiler()` retire le dernier empilé."
    },
    {
     "si": "8 5 3",
     "texte": "Tu as retiré à chaque fois le plus ancien élément, comme dans une file. `depiler()` retire le dernier empilé."
    }
   ]
  },
  "q5": {
   "attendu": "Koungou Sada",
   "explication": "« Sada » sort en tête, puis repart à la queue : Chiconi, Koungou, Sada. Puis « Chiconi » sort. Il reste Koungou, Sada.",
   "diag": [
    {
     "si": "Sada Koungou",
     "texte": "« Sada », défilé puis enfilé de nouveau, repart à la queue, derrière « Koungou »."
    },
    {
     "si": "Chiconi Sada",
     "texte": "Le deuxième `defiler()` retire la tête : « Chiconi », pas « Koungou ». On défile toujours en tête."
    },
    {
     "si": "Chiconi Koungou",
     "texte": "« Sada » est défilé, mais `f.enfiler(x)` le remet à la queue."
    }
   ]
  },
  "q6": {
   "attendu": "lagon 2",
   "explication": "La pile inverse l'ordre : on dépile lagon, barge, taxi, enfilés dans cet ordre. `defiler()` renvoie la tête, « lagon », et il reste 2 éléments.",
   "diag": [
    {
     "si": "taxi 2",
     "texte": "La pile inverse l'ordre : « lagon », empilé en dernier, est dépilé et enfilé en premier."
    },
    {
     "si": "lagon 3",
     "texte": "`defiler()` retire la tête : il reste 2 éléments dans la file."
    },
    {
     "si": "taxi 3",
     "texte": "La pile inverse l'ordre, et `defiler()` retire l'élément : il en reste 2."
    }
   ]
  },
  "q7": {
   "attendu": "d",
   "explication": "La pile n'a que 2 éléments, mais la boucle fait 3 tours. Le message `IndexError: pop from empty list` (erreur d'indice : retrait dans une liste vide) vient du troisième `depiler()`.",
   "diag": [
    {
     "si": "c",
     "texte": "`depiler()` retire le sommet. Le message dit que la liste qui contient la pile est vide."
    },
    {
     "si": "a",
     "texte": "`total` est créé à la ligne 5, avant la boucle. Ce serait une `NameError`."
    },
    {
     "si": "b",
     "texte": "Les éléments dépilés sont des nombres : on peut les additionner."
    }
   ]
  },
  "q8": {
   "attendu": [
    "notp.est_vide()",
    "p.taille()>0",
    "p.taille()!=0",
    "p.taille()>=1",
    "0<p.taille()",
    "not(p.est_vide())",
    "p.est_vide()==False",
    "p.est_vide()isFalse",
    "notp.taille()==0",
    "p.taille()",
    "p.est_vide()!=True"
   ],
   "affiche": "while not p.est_vide():",
   "explication": "On continue tant que la pile n'est pas vide : `while not p.est_vide():` (ou `while p.taille() > 0:`). La boucle s'arrête exactement quand la pile est vide.",
   "diag": [
    {
     "si": "p.est_vide()",
     "texte": "Avec cette condition, la boucle ne tourne jamais : la pile n'est pas vide au départ. On continue tant qu'elle n'est PAS vide."
    },
    {
     "si": "p.taille()>=0",
     "texte": "Une taille est toujours supérieure ou égale à 0 : on dépilerait une pile vide."
    },
    {
     "contient": [
      "depiler"
     ],
     "texte": "La condition ne doit pas dépiler : elle retirerait un élément à chaque test."
    }
   ]
  },
  "q9": {
   "attendu": "d",
   "explication": "`pile[-1]` est le dernier élément de la liste, donc le sommet, et la liste ne change pas.",
   "diag": [
    {
     "si": "a",
     "texte": "`pop()` renvoie bien le sommet, mais le retire : c'est `depiler`, pas `sommet`."
    },
    {
     "si": "b",
     "texte": "`pile[0]` est le premier élément de la liste : le bas de la pile."
    },
    {
     "si": "c",
     "texte": "Les indices vont de 0 à `len(pile) - 1` : `pile[len(pile)]` provoque une `IndexError`."
    }
   ]
  },
  "q10": {
   "attendu": "2",
   "explication": "La première boucle dépile 2, 5, 2, 7 et compte les 2 : il y en a deux.",
   "diag": [
    {
     "si": "4",
     "texte": "`n` augmente seulement quand `e == x`, pas à chaque tour."
    },
    {
     "si": "1",
     "texte": "La boucle parcourt toute la pile : les deux 2 sont comptés."
    }
   ]
  },
  "q11": {
   "attendu": "7 2 5 2",
   "explication": "On dépile 2, 5, 2, 7 et on les empile dans cet ordre dans `aux` : le dernier empilé, 7, est au sommet. Une pile inverse l'ordre.",
   "diag": [
    {
     "si": "2 5 2 7",
     "texte": "Passer d'une pile à une autre inverse l'ordre : 7, dépilé en dernier, est au sommet de `aux`."
    },
    {
     "si": "vide",
     "texte": "La première boucle vide `p`, pas `aux` : `aux` reçoit tous les éléments."
    }
   ]
  },
  "q12": {
   "attendu": [
    "aux.depiler()"
   ],
   "affiche": "p.empiler(aux.depiler())",
   "explication": "On dépile `aux` et on empile dans `p` : `p.empiler(aux.depiler())`. L'ordre est inversé une deuxième fois : `p` retrouve son ordre de départ, et `aux` se vide, ce qui arrête la boucle.",
   "diag": [
    {
     "si": "aux.sommet()",
     "texte": "`sommet()` ne retire rien : `aux` ne se vide jamais et la boucle ne s'arrête pas."
    },
    {
     "si": "e",
     "texte": "`e` est seulement le dernier élément dépilé : il faut reprendre tous les éléments de `aux`."
    },
    {
     "contient": [
      "p.depiler"
     ],
     "texte": "À ce moment, `p` est vide : on dépile `aux`."
    }
   ]
  }
 },
 "2": {
  "q1": {
   "attendu": "b",
   "explication": "Une file est FIFO : premier entré, premier sorti. `defiler()` retire la tête, c'est-à-dire le premier élément enfilé, et le renvoie.",
   "diag": [
    {
     "si": "a",
     "texte": "C'est la règle d'une pile (LIFO : dernier entré, premier sorti)."
    },
    {
     "si": "d",
     "texte": "C'est ce que fait `tete()`. `defiler()` retire la tête."
    },
    {
     "si": "c",
     "texte": "On ne touche jamais au milieu d'une file : on enfile à la queue, on défile en tête."
    }
   ]
  },
  "q2": {
   "attendu": "c",
   "explication": "Annuler défait d'abord la dernière action : dernier entré, premier sorti, c'est une pile. Les trois autres situations respectent l'ordre d'arrivée : ce sont des files.",
   "diag": [
    {
     "si": "a",
     "texte": "Au doukabé, le premier arrivé est servi le premier : c'est une file."
    },
    {
     "si": "b",
     "texte": "Sur une seule voie, personne ne double : la première voiture entrée sort la première. C'est une file."
    },
    {
     "si": "d",
     "texte": "Les impressions sortent dans l'ordre d'arrivée : c'est une file."
    }
   ]
  },
  "q3": {
   "attendu": "3 8",
   "explication": "`tete()` lit 5 sans le retirer ; `defiler()` retire 5. Il reste 3, 8.",
   "diag": [
    {
     "si": "8",
     "texte": "`tete()` ne retire rien : seul `defiler()` retire la tête."
    },
    {
     "si": "5 3 8",
     "texte": "`defiler()` retire bien la tête, 5."
    },
    {
     "si": "5 3",
     "texte": "On défile en tête (5), pas à la queue (8)."
    }
   ]
  },
  "q4": {
   "attendu": "3 7 6",
   "explication": "Après chaque ligne, du sommet vers le bas : 6 | 2, 6 | 6 | 7, 6 | 9, 7, 6 | 7, 6 | 3, 7, 6.",
   "diag": [
    {
     "si": "6 7 3",
     "texte": "Ce sont les bons éléments, lus du bas vers le haut. On écrit la pile du sommet vers le bas."
    },
    {
     "si": "3 9 2",
     "texte": "Tu as retiré à chaque fois le plus ancien élément, comme dans une file. `depiler()` retire le dernier empilé."
    },
    {
     "si": "2 9 3",
     "texte": "Tu as retiré à chaque fois le plus ancien élément, comme dans une file. `depiler()` retire le dernier empilé."
    }
   ]
  },
  "q5": {
   "attendu": "Ouangani Dembeni",
   "explication": "« Pamandzi » sort. Puis « Dembeni » sort et repart à la queue. Il reste Ouangani, Dembeni.",
   "diag": [
    {
     "si": "Dembeni Ouangani",
     "texte": "« Dembeni », défilé puis enfilé de nouveau, repart à la queue, derrière « Ouangani »."
    },
    {
     "si": "Pamandzi Dembeni",
     "texte": "On défile en tête : « Pamandzi » sort en premier, puis « Dembeni »."
    },
    {
     "si": "Ouangani",
     "texte": "`f.enfiler(y)` remet « Dembeni » à la queue."
    }
   ]
  },
  "q6": {
   "attendu": "5 3",
   "explication": "La file garde l'ordre 3, 8, 5 ; on les empile dans cet ordre, donc 5 est au sommet. `sommet()` le lit sans le retirer : la pile a toujours 3 éléments.",
   "diag": [
    {
     "si": "3 3",
     "texte": "3 est défilé et empilé en premier : il est en bas de la pile. Le sommet est le dernier empilé, 5."
    },
    {
     "si": "5 2",
     "texte": "`sommet()` ne retire rien : la pile a toujours 3 éléments."
    },
    {
     "si": "3 2",
     "texte": "Le sommet est le dernier empilé, 5, et `sommet()` ne retire rien."
    }
   ]
  },
  "q7": {
   "attendu": "b",
   "explication": "Une taille est toujours supérieure ou égale à 0 : la condition reste vraie quand la file est vide, et le quatrième `defiler()` provoque `IndexError: pop from empty list` (erreur d'indice : retrait dans une liste vide).",
   "diag": [
    {
     "si": "a",
     "texte": "`defiler()` est bien la primitive de la file : les trois premières personnes sont appelées."
    },
    {
     "si": "c",
     "texte": "`servis` est créé à la ligne 5, avant la boucle. Ce serait une `NameError`."
    },
    {
     "si": "d",
     "texte": "Python enfile n'importe quel texte : « Faïza » est bien appelée, la console l'affiche."
    }
   ]
  },
  "q8": {
   "attendu": [
    "notf.est_vide()",
    "f.taille()>0",
    "f.taille()!=0",
    "f.taille()>=1",
    "0<f.taille()",
    "not(f.est_vide())",
    "f.est_vide()==False",
    "f.est_vide()isFalse",
    "notf.taille()==0",
    "f.taille()",
    "f.est_vide()!=True"
   ],
   "affiche": "while not f.est_vide():",
   "explication": "On continue tant que la file n'est pas vide : `while not f.est_vide():` (ou `while f.taille() > 0:`). La boucle s'arrête exactement quand la file est vide.",
   "diag": [
    {
     "si": "f.est_vide()",
     "texte": "Avec cette condition, la boucle ne tourne jamais : la file n'est pas vide au départ. On continue tant qu'elle n'est PAS vide."
    },
    {
     "si": "f.taille()>=0",
     "texte": "C'est la condition fausse de départ : une taille est toujours supérieure ou égale à 0."
    },
    {
     "contient": [
      "defiler"
     ],
     "texte": "La condition ne doit pas défiler : elle retirerait une personne à chaque test."
    }
   ]
  },
  "q9": {
   "attendu": "a",
   "explication": "`file.pop(0)` retire l'élément d'indice 0, la tête, et le renvoie.",
   "diag": [
    {
     "si": "b",
     "texte": "`pop()` retire le dernier élément de la liste : la queue, le dernier arrivé. Ce serait une pile."
    },
    {
     "si": "c",
     "texte": "`file[0]` lit la tête sans la retirer : c'est `tete`, pas `defiler`."
    },
    {
     "si": "d",
     "texte": "`append(0)` ajoute le nombre 0 à la queue : c'est un `enfiler`."
    }
   ]
  },
  "q10": {
   "attendu": "9",
   "explication": "`m` part de la tête, 4, puis prend chaque élément plus grand : 9. Ni 2 ni 6 ne sont plus grands que 9.",
   "diag": [
    {
     "si": "6",
     "texte": "6 est le dernier élément, pas le plus grand : `m` ne change que si `e > m`."
    },
    {
     "si": "4",
     "texte": "4 est la tête, la valeur de départ de `m` : la boucle la remplace par 9."
    }
   ]
  },
  "q11": {
   "attendu": "4 9 2 6",
   "explication": "On défile 4, 9, 2, 6 et on les enfile dans cet ordre dans `aux` : une file garde l'ordre.",
   "diag": [
    {
     "si": "6 2 9 4",
     "texte": "C'est l'ordre qu'aurait donné une pile. Une file garde l'ordre : 4 est défilé et enfilé en premier, il est en tête."
    },
    {
     "si": "vide",
     "texte": "La première boucle vide `f`, pas `aux` : `aux` reçoit tous les éléments."
    }
   ]
  },
  "q12": {
   "attendu": [
    "aux.defiler()"
   ],
   "affiche": "f.enfiler(aux.defiler())",
   "explication": "On défile `aux` et on enfile dans `f` : `f.enfiler(aux.defiler())`. L'ordre est gardé, `f` retrouve son état de départ, et `aux` se vide, ce qui arrête la boucle.",
   "diag": [
    {
     "si": "aux.tete()",
     "texte": "`tete()` ne retire rien : `aux` ne se vide jamais et la boucle ne s'arrête pas."
    },
    {
     "si": "e",
     "texte": "`e` est seulement le dernier élément défilé : il faut reprendre tous les éléments de `aux`."
    },
    {
     "contient": [
      "f.defiler"
     ],
     "texte": "À ce moment, `f` est vide : on défile `aux`."
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
