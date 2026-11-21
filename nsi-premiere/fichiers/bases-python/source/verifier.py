#!/usr/bin/env python3
"""Vérifie un TD « robot » : les contrôles de charte/verifier-td.py, avec le robot des fiches.

Le moteur des TD en ligne ne connaît pas le robot : charte/verifier-td.py signale donc les
questions dont le code appelle nord(), est()… (NameError). Ce script lance exactement les mêmes
contrôles, mais chaque programme s'exécute avec les huit fonctions du robot (robot.py), sur la
grille « libre » (sans obstacle, départ en A6) : ces programmes-là sont donnés hors de toute grille.
En plus, sur la grille de la page (--grille) :
- courte data-verifier="robot"        : la case d'arrivée réelle est une des réponses ;
- courte data-verifier="robot-sortie" : ce qu'affiche réellement le programme est une des réponses ;
  input() reçoit les réponses de SAISIES (5, oui, non…) : un programme qui demande une saisie s'exécute aussi ;
  sans code affiché, la question reprend le programme de la question robot précédente ;
  (data-depart="B3" change la case de départ, data-grille une autre grille, pour une question).

Usage (à la racine du dépôt) :
  python3 -I nsi-premiere/fichiers/bases-python/source/verifier.py --grille for nsi-premiere/fichiers/bases-python/td-for.html
"""
import importlib.util
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, '..', '..', '..', '..'))
sys.path.insert(0, ICI)
import robot  # noqa: E402

spec = importlib.util.spec_from_file_location('verifier_td', os.path.join(RACINE, 'charte', 'verifier-td.py'))
vt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vt)


# ce que « tape » l'élève quand un programme appelle input() (un nombre positif, puis « oui »…)
SAISIES = ['5', 'oui', 'non'] * 20


def avec_robot(grille, depart=None):
    src = open(os.path.join(ICI, 'robot.py'), encoding='utf-8').read()
    return vt.LANCEUR.replace(
        'g = {"__name__": "__main__"}',
        'g = {"__name__": "__main__"}\n_rg = {"__name__": "robot"}\nexec(' + repr(src) + ', _rg)\n'
        'g.update(_rg["Robot"](' + repr(grille) + ', ' + repr(depart) + ').fonctions())\n'
        '_saisies = iter(' + repr(SAISIES) + ')\n'
        'g["input"] = lambda invite="": (print(invite, end=""), next(_saisies))[1]')


def principal(args):
    grille = 'for'
    if args[:1] == ['--grille']:
        grille, args = args[1], args[2:]
    vt.LANCEUR = avec_robot('libre')
    total = 0
    for chemin in args:
        n, err = vt.verifier(chemin)
        lu = vt.Lecteur()
        lu.feed(open(chemin, encoding='utf-8').read())
        m = 0
        precedent = ''
        for s in lu.racine.tous(lambda x: 'td-q' in x.classes() and x.attrs.get('data-verifier', '').startswith('robot')):
            m += 1
            q = s.attrs.get('id')
            pre = next(s.tous(lambda x: x.tag == 'pre' and 'td-code' in x.classes()), None)
            code = vt.code_de(pre.texte()) if pre else precedent   # « avec le même programme »
            precedent = code
            reps = s.attrs.get('data-reponse', '').split('|')
            case, trajet, sortie, ecrase, _ = robot.executer(code, s.attrs.get('data-grille', grille), s.attrs.get('data-depart'))
            valeur = case if s.attrs['data-verifier'] == 'robot' else sortie.strip()
            if ecrase or valeur not in reps:
                err.append(f'{q} : robot {valeur!r} (trajet {"-".join(trajet)}{", " + ecrase if ecrase else ""}), réponses {reps!r}')
        print(f'{chemin} : {n} questions (dont {m} de robot vérifiées en plus), '
              f'{"tout est juste" if not err else str(len(err)) + " problème(s)"}')
        for e in err:
            print('  -', e)
        total += len(err)
    print(sys.version.split()[0])
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(principal(sys.argv[1:]))
