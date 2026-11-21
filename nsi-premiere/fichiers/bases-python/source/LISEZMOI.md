# TD de boucles et de conditions (NSI 1re) : sources et vérifications

**La page HTML de chaque TD est désormais la référence** (style « Signal pirate », T125) : elle se corrige
toute seule à l'écran et, imprimée, elle est la feuille papier. Le PDF est fait depuis elle par
`charte/imprimer-td.py` (feuille vierge) ; un TD en plusieurs feuilles a un seul PDF, les feuilles à la suite.

| TD | Feuilles (adresses) | PDF |
|---|---|---|
| Boucle fermée : `for` | `td-for.html`, `td-for-2.html`, `td-for-3.html` | `td-for.pdf` |
| Boucle ouverte : `while` | `td-while.html`, `td-while-2.html`, `td-while-3.html` | `td-while.pdf` |
| Instructions conditionnelles | `td-conditions.html`, `td-conditions-2.html`, `td-conditions-3.html` | `td-conditions.pdf` |
| Récapitulatif : conditions et boucles | `td-recapitulatif.html`, `td-recapitulatif-2.html`, `td-recapitulatif-3.html` | `td-recapitulatif.pdf` |

Les anciennes pages statiques (police embarquée) sont remplacées à la même adresse ; elles restent
dans l'historique Git.

## Le robot

Le robot est celui des fiches d'origine (décision de l'enseignant·e) : mêmes fonctions, mêmes grilles.

- `robot.py` : le robot et ses grilles (`for` : 8 x 6, départ A6, TD for, while et récapitulatif ; `si` : 6 x 5, départ A3, TD conditions ; `libre` : sans obstacle).
- `grilles.py` : dessine les grilles en SVG (trait `currentColor` : thème clair, obscur et papier en noir et blanc).
- `verifier.py` : les contrôles de `charte/verifier-td.py`, avec le robot. Le moteur ne connaît pas le robot :
  `charte/verifier-td.py` seul signale donc les questions dont le code appelle `nord()`, `est()`… (NameError).
  Ce script vérifie aussi chaque case d'arrivée (`data-verifier="robot"`) et chaque affichage
  (`data-verifier="robot-sortie"`) par exécution réelle.
- `td-for-calculs.py`, `td-while-calculs.py`… (avec `calculs.py`) : les autres réponses calculées
  (choix justifiés, nombres de tours, fonctions, tests du moteur lancés sur les corrections).
- `verifier.py` donne aussi à `input()` des réponses toutes prêtes (5, oui, non…), pour les programmes qui demandent une saisie.

```
python3 -I nsi-premiere/fichiers/bases-python/source/verifier.py --grille for nsi-premiere/fichiers/bases-python/td-for.html nsi-premiere/fichiers/bases-python/td-for-2.html nsi-premiere/fichiers/bases-python/td-for-3.html
python3 -I nsi-premiere/fichiers/bases-python/source/td-for-calculs.py
```

Dans une question « code » du robot, les tests (`script.td-tests`) redéfinissent le robot et sa grille
avant d'appeler la fonction de l'élève : la question s'exécute donc aussi dans la page, avec Python.
