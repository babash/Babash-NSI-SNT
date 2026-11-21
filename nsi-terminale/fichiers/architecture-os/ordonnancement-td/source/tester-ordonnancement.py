"""Vérifie par exécution (Python 3.13) les réponses du TD « Ordonnancement » (../index.html, T125).

Simulations tick par tick (Round Robin, SJF, FCFS, priorité préemptive) et vraie course entre deux
processus avec multiprocessing (exercice 6), sans puis avec verrou.
Depuis la racine du dépôt :  python3 -I nsi-terminale/fichiers/architecture-os/ordonnancement-td/source/tester-ordonnancement.py
"""
import sys, time
from multiprocessing import Process, Value, Lock

erreurs = 0


def egal(nom, obtenu, attendu):
    global erreurs
    ok = obtenu == attendu
    erreurs += not ok
    print(f'  {nom} : {obtenu!r}' + ('' if ok else f'  (attendu dans la page : {attendu!r})'))


def round_robin(procs, q):
    """procs : liste (nom, arrivée, durée), dans l'ordre de la file. Renvoie l'élu à chaque tick et les fins."""
    reste = {n: d for n, a, d in procs}
    file, gantt, fins, t = [n for n, a, d in procs if a == 0], [], {}, 0
    while file:
        n = file.pop(0)
        for _ in range(min(q, reste[n])):
            gantt.append(n); reste[n] -= 1; t += 1
        if reste[n]:
            file.append(n)
        else:
            fins[n] = t
    return gantt, fins


def non_preemptif(procs, cle):
    """SJF (cle = durée) ou FCFS (cle = arrivée), sans préemption."""
    t, gantt, debut, attente = 0, [], {}, list(procs)
    while attente:
        prets = [p for p in attente if p[1] <= t] or [min(attente, key=lambda p: p[1])]
        n, a, d = min(prets, key=cle)
        t = max(t, a); debut[n] = t
        gantt += [n] * d; t += d
        attente.remove((n, a, d))
    return gantt, debut


def priorite_preemptive(procs, pas):
    """procs : (nom, arrivée, durée, priorité) ; plus petit = plus prioritaire ; égalité : FCFS."""
    reste = {n: d for n, a, d, p in procs}
    t, gantt, etats = 0, [], {}
    while any(reste.values()):
        prets = [x for x in procs if x[1] <= t and reste[x[0]]]
        n = min(prets, key=lambda x: (x[3], x[1]))[0]
        gantt.append(n); reste[n] -= pas; t += pas
        etats[t] = {x[0]: ('Élu' if x[0] == n else 'Prêt') for x in prets if reste[x[0]] or x[0] == n}
    return gantt, etats


print('Exercice 2 : Round Robin, q = 2')
g, fins = round_robin([('P1', 0, 5), ('P2', 0, 3), ('P3', 0, 1)], 2)
egal('Gantt', g, ['P1', 'P1', 'P2', 'P2', 'P3', 'P1', 'P1', 'P2', 'P1'])
egal('séjour et attente de P2', (fins['P2'] - 0, fins['P2'] - 0 - 3), (8, 5))
g, fins = round_robin([('P1', 0, 5), ('P2', 0, 3)], 2)   # l'exemple du cours, P2 arrivé à t = 1 : même ordre
egal('cours : fins de P1 et P2', (fins['P1'], fins['P2']), (8, 7))

print('Exercice 3 : SJF puis FCFS')
procs = [('P1', 0, 4), ('P2', 1, 2), ('P3', 2, 1)]
g, debut = non_preemptif(procs, cle=lambda p: p[2])
egal('Gantt SJF', g, ['P1'] * 4 + ['P3'] + ['P2'] * 2)
att = {n: debut[n] - a for n, a, d in procs}
egal('attentes SJF', att, {'P1': 0, 'P2': 4, 'P3': 2})
egal('moyenne SJF', sum(att.values()) / 3, 2.0)
g, debut = non_preemptif(procs, cle=lambda p: p[1])
att = {n: debut[n] - a for n, a, d in procs}
egal('attentes FCFS', att, {'P1': 0, 'P2': 3, 'P3': 4})
egal('moyenne FCFS (arrondie)', round(sum(att.values()) / 3, 2), 2.33)

print('Exercice 4 : priorité préemptive (cases de 10 min)')
g, etats = priorite_preemptive([('A', 10, 20, 1), ('B', 0, 30, 3), ('D', 10, 30, 2)], 10)
egal('Gantt', g, ['B', 'A', 'A', 'D', 'D', 'D', 'B', 'B'])
egal('état de Bob à t = 20', etats[20]['B'], 'Prêt')

print('Exercice 6 : vraie course entre deux processus (multiprocessing)')


def sans_verrou(places, verrou):
    if places.value > 0:
        time.sleep(0.01)
        places.value = places.value - 1


def avec_verrou(places, verrou):
    verrou.acquire()
    if places.value > 0:
        time.sleep(0.01)
        places.value = places.value - 1
    verrou.release()


def essai(f):
    places, verrou = Value('i', 1, lock=False), Lock()
    ps = [Process(target=f, args=(places, verrou)) for _ in range(2)]
    for p in ps: p.start()
    for p in ps: p.join()
    return places.value


if __name__ == '__main__':
    egal('sans verrou, une place : au moins un essai sur 5 finit à -1', -1 in [essai(sans_verrou) for _ in range(5)], True)
    egal('avec verrou, une place : toujours 0 (5 essais)', {essai(avec_verrou) for _ in range(5)}, {0})
    print('tout est juste' if not erreurs else f'{erreurs} erreur(s)')
    sys.exit(1 if erreurs else 0)
