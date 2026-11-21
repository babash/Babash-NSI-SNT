#!/usr/bin/env python3
"""TP « Attrape les objets » : les réponses de la page, obtenues en lisant et en exécutant pour de vrai.

Usage : python3 -I verifier-tp-pygame.py
- les numéros de ligne cités par l'énoncé sont lus dans ../tp-ramasse-objet.py (le fichier de l'archive de l'enseignant) ;
- les coordonnées, vitesses et affichages sont calculés en exécutant le code du jeu, sans Pygame (le dessin est remplacé
  par un relevé des rectangles) ;
- rien n'est lancé depuis le dossier de l'archive.
"""
import os
import random
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
JEU = os.path.join(ICI, '..', 'tp-ramasse-objet.py')
lignes = open(JEU, encoding='utf-8').read().split('\n')
erreurs = []


def ligne_de(motif, apres=0):
    for i, l in enumerate(lignes, 1):
        if i > apres and motif in l:
            return i
    erreurs.append('introuvable : ' + motif)
    return None


def attendu(nom, obtenu, page):
    print(f'{nom} : {obtenu!r} ; page : {page!r}', '' if obtenu == page else '  <-- DIFFÉRENT')
    if obtenu != page:
        erreurs.append(nom)


# 1. Les numéros de ligne de l'énoncé
attendu('constantes (ligne)', ligne_de('# Constantes'), 7)
attendu('couleurs (lignes)', (ligne_de('# Couleurs'), ligne_de('VERT = ')), (14, 17))
attendu('position initiale (lignes)', (ligne_de('# Position initiale'), ligne_de('score = 0')), (23, 27))
attendu('chute (ligne)', ligne_de('objet_y += VITESSE_OBJET'), 47)
attendu('collision (lignes)', (ligne_de('# Vérification de collision'), ligne_de('joueur_x + TAILLE_JOUEUR > objet_x')), (49, 52))
attendu('fin du jeu (ligne)', ligne_de('if objet_y > HAUTEUR'), 58)
fonctions = {'init': 'pygame.init()', 'randint': 'random.randint(', 'set_mode': 'set_mode(', 'set_caption': 'set_caption(',
             'delay': 'time.delay(', 'event.get': 'event.get()', 'get_pressed': 'get_pressed()', 'fill': '.fill(',
             'draw.rect': 'draw.rect(', 'display.update': 'display.update()', 'quit': 'pygame.quit()'}
page_fonctions = {'init': 5, 'randint': 25, 'set_mode': 20, 'set_caption': 21, 'delay': 32, 'event.get': 35,
                  'get_pressed': 40, 'fill': 63, 'draw.rect': 64, 'display.update': 66, 'quit': 68}
for f, motif in fonctions.items():
    attendu('ligne de ' + f, ligne_de(motif), page_fonctions[f])

# 2. Le jeu exécuté sans Pygame : on relève ce qui serait dessiné à un instant donné
constantes = {}
exec('\n'.join(lignes[7:17]), constantes)          # lignes 8 à 17 : constantes et couleurs
L, H, TJ, TO, VJ, VO = (constantes[k] for k in ('LARGEUR', 'HAUTEUR', 'TAILLE_JOUEUR', 'TAILLE_OBJET', 'VITESSE_JOUEUR', 'VITESSE_OBJET'))
attendu('joueur_x au départ (LARGEUR // 2)', L // 2, 400)
joueur_x, objet_x, objet_y = L // 2, 300, 100
rect_joueur = (joueur_x, H - TJ, TJ, TJ)               # ligne 64 : (x, y, largeur, hauteur)
rect_objet = (objet_x, objet_y, TO, TO)                # ligne 65


def coins(r):
    x, y, l, h = r
    return [(x, y), (x + l, y), (x, y + h), (x + l, y + h)]


attendu('coins de l\'objet (hg, hd, bg, bd)', coins(rect_objet), [(300, 100), (320, 100), (300, 120), (320, 120)])
attendu('coins du joueur (hg, hd, bg, bd)', coins(rect_joueur), [(400, 550), (450, 550), (400, 600), (450, 600)])
attendu('randint : objet_x au plus', L - TO, 780)

# l'objet tombe : nombre de tours de boucle pour arriver en bas (objet_y > HAUTEUR), sans être attrapé
y, tours = 0, 0
while not y > H:
    y += VO
    tours += 1
attendu('tours avant la fin (objet raté)', tours, 201)
attendu('durée approximative en secondes (30 ms par tour, sans le dessin)', round(tours * 30 / 1000, 1), 6.0)

# 3. Les défis
attendu('défi 2 : pixels par tour avec VITESSE_OBJET = 6', 6, 6)
attendu('défi 3 : haut du joueur avec TAILLE_JOUEUR = 120', H - 120, 480)


def sortie(code):
    r = subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, text=True, timeout=10)
    return (r.stdout + r.stderr).strip()


DEFI4 = '''score = 7
objet_y = 603
HAUTEUR = 600
jeu_en_cours = True
if objet_y > HAUTEUR:
    print(f"Perdu ! Ton score est : {score}")
    jeu_en_cours = False
print(jeu_en_cours)'''
attendu('défi 4 : sortie', sortie(DEFI4), 'Perdu ! Ton score est : 7\nFalse')

DEFI6 = '''VITESSE_OBJET = 3
facteur_vitesse = 1.5
objet_y = 0
objet_y += VITESSE_OBJET * facteur_vitesse
print(objet_y)'''
attendu('défi 6 : sortie', sortie(DEFI6), '4.5')

DEFI7 = '''facteur_vitesse = 1.0
for attrape in range(5):
    facteur_vitesse += 0.1
print(facteur_vitesse)
print(round(3 * facteur_vitesse, 1))'''
attendu('défi 7 : sortie (les flottants !)', sortie(DEFI7), '1.5000000000000004\n4.5')

DEFI8 = '''score = 4
objet = {'x': 120, 'y': 550, 'type': 'malus'}
if objet['type'] == 'bonus':
    score += 5
elif objet['type'] == 'malus':
    score -= 3
else:
    score += 1
print(score)'''
attendu('défi 8 : sortie', sortie(DEFI8), '1')

# défi 9 : la liste de trois objets, puis la boucle qui les fait tous tomber (correction de la page)
random.seed(2046)
objets = [{'x': random.randint(0, L - TO), 'y': 0, 'type': random.choice(['normal', 'bonus', 'malus'])} for _ in range(3)]
attendu('défi 9 : len(objets)', len(objets), 3)
for objet in objets:
    objet['y'] += VO
attendu('défi 9 : y après un tour', [o['y'] for o in objets], [3, 3, 3])

print('tout est juste' if not erreurs else 'À REVOIR : ' + ', '.join(map(str, erreurs)))
sys.exit(1 if erreurs else 0)
