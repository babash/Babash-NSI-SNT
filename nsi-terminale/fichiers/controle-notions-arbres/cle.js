/* Clé de correction du contrôle de notions sur les arbres binaires.
   Babash - NSI Tani Malandi · contenus CC BY-SA 4.0 · code MIT

   Chargé SEULEMENT par prof.html et corrige.html, jamais par la page élève.
   Ce fichier est public (comme le corrigé PDF) : il empêche l'élève de voir
   sa correction pendant qu'il compose, il ne protège pas un secret.
   Toutes les réponses sont recalculées par verification/verifier.py.

   Diagnostics : « si » = réponse exacte (après normalisation) ;
   « contient » = la réponse contient une de ces valeurs (ou ce morceau de code) ;
   « manque » = il manque une de ces valeurs. Le premier diagnostic qui
   s'applique est affiché ; sinon, l'explication générale. */

(function () {
  'use strict';

  var CLE = /*CLE-DEBUT*/{
    "1": {
      "q1": {"attendu": 15, "explication": "La racine est le nœud tout en haut : le seul qui n'a pas de parent. Ici, 15.",
        "diag": [{"si": 26, "texte": "26 est une feuille, en bas de l'arbre. La racine est le nœud du haut."}]},
      "q2": {"attendu": [4, 9, 26], "explication": "Une feuille est un nœud sans enfant : 4, 9 et 26.",
        "diag": [{"contient": [11, 30], "texte": "11 et 30 ont un enfant chacun : ce ne sont pas des feuilles. Une feuille n'a aucun enfant."},
                 {"manque": [4], "texte": "4 est une feuille : il n'a pas d'enfant, même s'il n'est pas tout en bas du dessin."}]},
      "q3": {"attendu": 8, "explication": "La taille est le nombre de nœuds : 15, 8, 22, 4, 11, 30, 9, 26, soit 8 nœuds.",
        "diag": [{"si": 7, "texte": "Il manque un nœud : la taille compte tous les nœuds, racine comprise."},
                 {"si": 3, "texte": "3 est le nombre de feuilles. La taille compte tous les nœuds."}]},
      "q4": {"attendu": 3, "explication": "Le plus long chemin de la racine à une feuille (15, 8, 11, 9 ou 15, 22, 30, 26) a 3 arêtes : hauteur 3.",
        "diag": [{"si": 4, "texte": "Tu as compté les nœuds du plus long chemin. Avec la convention rappelée, on compte les arêtes : un arbre d'un seul nœud a une hauteur 0."},
                 {"si": 2, "texte": "Il y a un chemin plus long : 15, 8, 11, 9 a 3 arêtes."}]},
      "q5": {"attendu": 2, "explication": "De 15 à 30 : 15, 22, 30, soit 2 arêtes. La racine a la profondeur 0.",
        "diag": [{"si": 3, "texte": "Tu as compté les nœuds (15, 22, 30). On compte les arêtes : la racine a la profondeur 0."},
                 {"si": 1, "texte": "30 n'est pas un enfant de la racine : il est sous 22. Il y a 2 arêtes."}]},
      "q6": {"attendu": "c", "explication": "C'est un ABR : pour chaque nœud, tout son sous-arbre gauche est plus petit et tout son sous-arbre droit plus grand (par exemple, 8, 4, 11 et 9 sont plus petits que 15).",
        "diag": [{"si": "a", "texte": "26 est plus petit que 30 : il doit être à GAUCHE de 30, et il y est. Plus petit à gauche, plus grand à droite."},
                 {"si": "b", "texte": "Un nœud d'un ABR peut n'avoir qu'un enfant, ou aucun. Un ABR n'a pas besoin d'être complet."},
                 {"si": "d", "texte": "Un ABR ne se lit pas ligne par ligne : c'est le parcours infixe qui donne les valeurs dans l'ordre croissant."}]},
      "q7": {"attendu": [15, 8, 22, 4, 11, 30, 9, 26], "explication": "En largeur, on lit niveau par niveau, de gauche à droite : 15 | 8, 22 | 4, 11, 30 | 9, 26.",
        "diag": [{"si": [15, 8, 4, 11, 9, 22, 30, 26], "texte": "C'est le parcours préfixe (en profondeur). En largeur, on lit l'arbre niveau par niveau."},
                 {"si": [15, 8, 22, 4, 11, 9, 30, 26], "texte": "Presque : au dernier niveau, 9 et 26 sont lus après 30, qui est sur le niveau au-dessus."}]},
      "q8": {"attendu": [15, 8, 4, 11, 9, 22, 30, 26], "explication": "Préfixe : le nœud d'abord, puis tout son sous-arbre gauche, puis tout son sous-arbre droit.",
        "diag": [{"si": [15, 8, 22, 4, 11, 30, 9, 26], "texte": "C'est le parcours en largeur (niveau par niveau). En préfixe, on descend d'abord tout le sous-arbre gauche."},
                 {"si": [4, 9, 11, 8, 26, 30, 22, 15], "texte": "C'est le parcours suffixe : le nœud est écrit à la fin. En préfixe, il est écrit au début."},
                 {"si": [4, 8, 9, 11, 15, 22, 26, 30], "texte": "C'est le parcours infixe : le nœud est écrit au milieu. En préfixe, il est écrit au début."}]},
      "q9": {"attendu": [4, 8, 9, 11, 15, 22, 26, 30], "explication": "Infixe : tout le sous-arbre gauche, puis le nœud, puis tout le sous-arbre droit. Pour un ABR, on obtient les valeurs dans l'ordre croissant.",
        "diag": [{"si": [15, 8, 4, 11, 9, 22, 30, 26], "texte": "C'est le parcours préfixe. En infixe, le nœud est écrit entre ses deux sous-arbres."},
                 {"si": [4, 9, 11, 8, 26, 30, 22, 15], "texte": "C'est le parcours suffixe. En infixe, le nœud est écrit entre ses deux sous-arbres."},
                 {"si": [4, 8, 11, 9, 15, 22, 30, 26], "texte": "Attention à 9 : c'est le fils GAUCHE de 11, il passe avant 11 (et 26, fils gauche de 30, avant 30)."}]},
      "q10": {"attendu": 26, "explication": "On suit les attributs de gauche à droite : a.droit est 22, a.droit.droit est 30, a.droit.droit.gauche est 26 ; .valeur donne 26.",
        "diag": [{"si": 30, "texte": "Tu t'es arrêté·e à a.droit.droit (30). Il reste .gauche : le fils gauche de 30, qui est 26."},
                 {"si": 22, "texte": "a.droit est 22 ; il reste encore .droit puis .gauche à suivre."}]},
      "q11": {"attendu": ["1+taille(arbre.gauche)+taille(arbre.droit)", "1+taille(arbre.droit)+taille(arbre.gauche)", "taille(arbre.gauche)+1+taille(arbre.droit)", "taille(arbre.droit)+1+taille(arbre.gauche)", "taille(arbre.gauche)+taille(arbre.droit)+1", "taille(arbre.droit)+taille(arbre.gauche)+1"],
        "affiche": "return 1 + taille(arbre.gauche) + taille(arbre.droit)",
        "explication": "La taille d'un arbre non vide : 1 (le nœud lui-même) + la taille du sous-arbre gauche + la taille du sous-arbre droit.",
        "diag": [{"si": "taille(arbre.gauche)+taille(arbre.droit)", "texte": "Il manque le nœud lui-même : sans le « 1 + », la fonction renvoie toujours 0."},
                 {"contient": ["max("], "texte": "max sert pour la hauteur. Pour la taille, on additionne les nœuds des deux sous-arbres."},
                 {"contient": ["gauche()", "droit()"], "texte": "gauche et droit sont des attributs, pas des méthodes : pas de parenthèses après."}]},
      "q12": {"attendu": [13, 7, 20, 3, 10, 25], "explication": "13 est la racine. 7 < 13 : à gauche. 20 > 13 : à droite. 10 : à gauche de 13, puis à droite de 7. 3 : à gauche de 13, puis à gauche de 7. 25 : à droite de 13, puis à droite de 20.",
        "diag": [{"si": [13, 7, 20, 10, 3, 25], "texte": "Les valeurs sont placées dans l'ordre d'insertion, case après case. Il faut comparer : 3 < 7 va à gauche de 7, 10 > 7 va à droite."},
                 {"si": [13, 20, 7, 25, 10, 3], "texte": "Gauche et droite sont inversés : dans un ABR, le plus petit va à gauche."}]}
    },
    "2": {
      "q1": {"attendu": 40, "explication": "La racine est le nœud tout en haut : le seul qui n'a pas de parent. Ici, 40.",
        "diag": [{"si": 45, "texte": "45 est une feuille, en bas de l'arbre. La racine est le nœud du haut."}]},
      "q2": {"attendu": [12, 45, 47, 60], "explication": "Une feuille est un nœud sans enfant : 12, 45, 47 et 60.",
        "diag": [{"contient": [31], "texte": "31 a un enfant (45) : ce n'est pas une feuille. Une feuille n'a aucun enfant."},
                 {"manque": [12, 47, 60], "texte": "12, 47 et 60 sont des feuilles : ils n'ont pas d'enfant, même s'ils ne sont pas tout en bas du dessin."}]},
      "q3": {"attendu": 8, "explication": "La taille est le nombre de nœuds : 40, 25, 52, 12, 31, 47, 60, 45, soit 8 nœuds.",
        "diag": [{"si": 7, "texte": "Il manque un nœud : la taille compte tous les nœuds, racine comprise."},
                 {"si": 4, "texte": "4 est le nombre de feuilles. La taille compte tous les nœuds."}]},
      "q4": {"attendu": 3, "explication": "Le plus long chemin de la racine à une feuille (40, 25, 31, 45) a 3 arêtes : hauteur 3.",
        "diag": [{"si": 4, "texte": "Tu as compté les nœuds du plus long chemin. Avec la convention rappelée, on compte les arêtes : un arbre d'un seul nœud a une hauteur 0."},
                 {"si": 2, "texte": "Il y a un chemin plus long : 40, 25, 31, 45 a 3 arêtes."}]},
      "q5": {"attendu": 2, "explication": "De 40 à 47 : 40, 52, 47, soit 2 arêtes. La racine a la profondeur 0.",
        "diag": [{"si": 3, "texte": "Tu as compté les nœuds (40, 52, 47). On compte les arêtes : la racine a la profondeur 0."},
                 {"si": 1, "texte": "47 n'est pas un enfant de la racine : il est sous 52. Il y a 2 arêtes."}]},
      "q6": {"attendu": "b", "explication": "Ce n'est pas un ABR : 45 est dans le sous-arbre gauche de 40, où toutes les valeurs doivent être plus petites que 40.",
        "diag": [{"si": "a", "texte": "Comparer un nœud à ses seuls enfants ne suffit pas : TOUT le sous-arbre gauche de 40 doit être plus petit que 40. Or 45 > 40."},
                 {"si": "c", "texte": "Un nœud d'un ABR peut n'avoir qu'un enfant, ou aucun. Le vrai problème est 45, plus grand que 40 mais à sa gauche."},
                 {"si": "d", "texte": "12 est plus petit que 25 : il doit être à GAUCHE de 25, et il y est. Le vrai problème est 45, plus grand que 40 mais à sa gauche."}]},
      "q7": {"attendu": [40, 25, 52, 12, 31, 47, 60, 45], "explication": "En largeur, on lit niveau par niveau, de gauche à droite : 40 | 25, 52 | 12, 31, 47, 60 | 45.",
        "diag": [{"si": [40, 25, 12, 31, 45, 52, 47, 60], "texte": "C'est le parcours préfixe (en profondeur). En largeur, on lit l'arbre niveau par niveau."},
                 {"si": [40, 25, 52, 12, 31, 45, 47, 60], "texte": "Presque : 45 est sur le dernier niveau, il est lu après 47 et 60."}]},
      "q8": {"attendu": [40, 25, 12, 31, 45, 52, 47, 60], "explication": "Préfixe : le nœud d'abord, puis tout son sous-arbre gauche, puis tout son sous-arbre droit.",
        "diag": [{"si": [40, 25, 52, 12, 31, 47, 60, 45], "texte": "C'est le parcours en largeur (niveau par niveau). En préfixe, on descend d'abord tout le sous-arbre gauche."},
                 {"si": [12, 45, 31, 25, 47, 60, 52, 40], "texte": "C'est le parcours suffixe : le nœud est écrit à la fin. En préfixe, il est écrit au début."},
                 {"si": [12, 25, 31, 45, 40, 47, 52, 60], "texte": "C'est le parcours infixe : le nœud est écrit au milieu. En préfixe, il est écrit au début."}]},
      "q9": {"attendu": [12, 25, 31, 45, 40, 47, 52, 60], "explication": "Infixe : tout le sous-arbre gauche, puis le nœud, puis tout le sous-arbre droit. Ici, le résultat n'est pas trié : l'arbre n'est pas un ABR.",
        "diag": [{"si": [12, 25, 31, 40, 45, 47, 52, 60], "texte": "Tu as rangé les valeurs dans l'ordre croissant. L'infixe d'un ABR est trié, mais cet arbre n'en est pas un : il faut suivre l'arbre (45 passe avant 40)."},
                 {"si": [40, 25, 12, 31, 45, 52, 47, 60], "texte": "C'est le parcours préfixe. En infixe, le nœud est écrit entre ses deux sous-arbres."},
                 {"si": [12, 45, 31, 25, 47, 60, 52, 40], "texte": "C'est le parcours suffixe. En infixe, le nœud est écrit entre ses deux sous-arbres."}]},
      "q10": {"attendu": 45, "explication": "On suit les attributs de gauche à droite : a.gauche est 25, a.gauche.droit est 31, a.gauche.droit.droit est 45 ; .valeur donne 45.",
        "diag": [{"si": 31, "texte": "Tu t'es arrêté·e à a.gauche.droit (31). Il reste .droit : le fils droit de 31, qui est 45."},
                 {"si": 25, "texte": "a.gauche est 25 ; il reste encore .droit puis .droit à suivre."}]},
      "q11": {"attendu": ["1+taille(arbre.gauche)+taille(arbre.droit)", "1+taille(arbre.droit)+taille(arbre.gauche)", "taille(arbre.gauche)+1+taille(arbre.droit)", "taille(arbre.droit)+1+taille(arbre.gauche)", "taille(arbre.gauche)+taille(arbre.droit)+1", "taille(arbre.droit)+taille(arbre.gauche)+1"],
        "affiche": "return 1 + taille(arbre.gauche) + taille(arbre.droit)",
        "explication": "La taille d'un arbre non vide : 1 (le nœud lui-même) + la taille du sous-arbre gauche + la taille du sous-arbre droit.",
        "diag": [{"si": "taille(arbre.gauche)+taille(arbre.droit)", "texte": "Il manque le nœud lui-même : sans le « 1 + », la fonction renvoie toujours 0."},
                 {"contient": ["max("], "texte": "max sert pour la hauteur. Pour la taille, on additionne les nœuds des deux sous-arbres."},
                 {"contient": ["gauche()", "droit()"], "texte": "gauche et droit sont des attributs, pas des méthodes : pas de parenthèses après."}]},
      "q12": {"attendu": [30, 18, 42, 22, 35, 50], "explication": "30 est la racine. 18 < 30 : à gauche. 42 > 30 : à droite. 35 : à droite de 30, puis à gauche de 42. 22 : à gauche de 30, puis à droite de 18. 50 : à droite de 30, puis à droite de 42.",
        "diag": [{"si": [30, 18, 42, 35, 22, 50], "texte": "Les valeurs sont placées dans l'ordre d'insertion, case après case. Il faut comparer : 22 va sous 18 (22 < 30, puis 22 > 18), 35 va sous 42."},
                 {"si": [30, 42, 18, 50, 35, 22], "texte": "Gauche et droite sont inversés : dans un ABR, le plus petit va à gauche."}]}
    }
  }/*CLE-FIN*/;

  var CN = window.CN;

  function formeNormale(type, r) {
    if (type === 'valeur') { var n = CN.nombres(r); return n.length === 1 ? n[0] : (n.length ? n : null); }
    if (type === 'ensemble') return CN.nombres(r).filter(function (v, i, t) { return t.indexOf(v) === i; }).sort(function (a, b) { return a - b; });
    if (type === 'liste') return CN.nombres(r);
    if (type === 'qcu') return r ? String(r) : null;
    if (type === 'ligne') return CN.ligneCode(r).replace(/^return/, '');
    if (type === 'schema') return Array.isArray(r) ? r.map(function (v) { return v === '' || v === null ? null : Number(v); }) : [];
    return r;
  }
  function egal(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
  function vide(type, r) {
    if (type === 'schema') return !Array.isArray(r) || r.every(function (v) { return v === '' || v === null; });
    return r === null || r === undefined || String(r).trim() === '';
  }

  /* Corrige une question : { juste, vide, donne, attendu, texte } */
  function corrigerQuestion(q, sujet, r) {
    var k = CLE[sujet][q.id], f = formeNormale(q.type, r), juste;
    if (q.type === 'ensemble') juste = egal(f, k.attendu.slice().sort(function (a, b) { return a - b; }));
    else if (q.type === 'ligne') juste = k.attendu.indexOf(f) >= 0;
    else juste = egal(f, k.attendu);
    var texte = k.explication, estVide = vide(q.type, r);
    if (!juste && !estVide) {
      for (var i = 0; i < (k.diag || []).length; i++) {
        var d = k.diag[i], ok = false;
        if ('si' in d) ok = egal(f, q.type === 'ensemble' && Array.isArray(d.si) ? d.si.slice().sort(function (a, b) { return a - b; }) : d.si);
        if ('contient' in d) ok = d.contient.some(function (x) {
          return q.type === 'ligne' ? String(f).indexOf(x) >= 0 : (Array.isArray(f) && f.indexOf(x) >= 0);
        });
        if ('manque' in d) ok = Array.isArray(f) && d.manque.some(function (x) { return f.indexOf(x) < 0; });
        if (ok) { texte = d.texte + ' ' + k.explication; break; }
      }
    }
    return { juste: juste, vide: estVide, attendu: k.affiche || k.attendu, texte: estVide ? 'Pas de réponse. ' + k.explication : texte };
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

  window.CLE = { donnees: CLE, corrigerCopie: corrigerCopie, corrigerQuestion: corrigerQuestion, formeNormale: formeNormale };
})();
