#!/usr/bin/env python3
"""Vérifie un TD « robot » : les contrôles de charte/verifier-td.py, avec le robot des fiches.

Le moteur des TD en ligne ne connaît pas le robot : charte/verifier-td.py signale donc les
questions dont le code appelle nord(), est()… (NameError). Ce script lance exactement les mêmes
contrôles, mais chaque programme s'exécute avec les huit fonctions du robot (robot.py), sur la
grille « libre » (sans obstacle, départ en A6) : ces programmes-là sont donnés hors de toute grille.
En plus, sur la grille de la page (--grille) :
- courte data-verifier="robot"        : la case d'arrivée réelle est une des réponses ;
- courte data-verifier="robot-sortie" : ce qu'affiche réellement le programme est une des réponses ;
  input() reçoit les réponses de SAISIES (selon l'invite : « Devine : » 10, 50, 42…) : un programme qui demande une saisie s'exécute aussi ;
  « trouve l'erreur » dont la ligne corrigée commence par des espaces : elle remplace la ligne, décalage compris ;
  sans code affiché, la question reprend le programme de la question robot précédente ;
  (data-depart="B3" change la case de départ, data-grille une autre grille, pour une question).

Usage (à la racine du dépôt) :
  python3 -I nsi-premiere/fichiers/bases-python/source/verifier.py --erreur majeur.py   (le message à copier)
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


# ce que « tape » l'élève quand un programme appelle input(), selon la question posée (l'invite) ;
# pour une autre invite : 5, puis oui, puis non, et ainsi de suite
SAISIES = {'Devine : ': ['10', '50', '42'], 'Note : ': ['10', '14', '15'], 'Âge : ': ['17'],
           '': ['5', 'oui', 'non']}


def avec_robot(grille, depart=None):
    src = open(os.path.join(ICI, 'robot.py'), encoding='utf-8').read()
    return vt.LANCEUR.replace(
        'g = {"__name__": "__main__"}',
        'g = {"__name__": "__main__"}\n_rg = {"__name__": "robot"}\nexec(' + repr(src) + ', _rg)\n'
        'g.update(_rg["Robot"](' + repr(grille) + ', ' + repr(depart) + ').fonctions())\n'
        '_S, _k = ' + repr(SAISIES) + ', {}\n'
        'def _saisir(invite=""):\n'
        '    print(invite, end="")\n'
        '    l = _S.get(invite, _S[""]); _k[invite] = _k.get(invite, -1) + 1\n'
        '    return l[_k[invite] % len(l)]\n'
        'g["input"] = _saisir')


def principal(args):
    if args[:1] == ['--erreur']:
        # le message réel, avec le robot et les saisies : à copier dans pre.td-erreur
        vt.LANCEUR = avec_robot('libre')
        rc, out, err = vt.lancer(open(args[1], encoding='utf-8').read(), os.path.basename(args[1]))
        sys.stdout.write(err or 'Aucune erreur : ce programme marche.\n')
        return 0
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
        # « trouve l'erreur » sur un décalage : verifier-td.py garde le décalage fautif de la ligne ;
        # ici, la ligne corrigée (data-reponse) remplace la ligne en entier, décalage compris.
        for s in lu.racine.tous(lambda x: x.attrs.get('data-type') == 'erreur' and (x.attrs.get('data-reponse') or '').startswith(' ')):
            q = s.attrs.get('id')
            pre = next(s.tous(lambda x: x.tag == 'pre' and 'td-code' in x.classes()))
            L = vt.code_de(pre.texte()).split('\n')
            L[int(s.attrs['data-ligne']) - 1] = s.attrs['data-reponse'].split('|')[0]
            rc, out, e = vt.lancer('\n'.join(L), s.attrs.get('data-fichier', 'mon_code.py'))
            if rc == 0:
                err[:] = [x for x in err if not x.startswith(q + ' : le code corrigé ne marche pas')]
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
