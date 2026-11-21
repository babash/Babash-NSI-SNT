"""Corrigé de la feuille « Les fonctions » : sorties et messages obtenus par exécution.

Lancer : python3 -I corrige-exercices-fonctions.py (Python 3.13), dans un dossier jetable :
le script écrit chaque programme dans un fichier (nom de la question), puis l'exécute
comme le fait la page (python3 fichier.py) et affiche la sortie ou le message d'erreur.
Les messages d'erreur de la page ont été obtenus avec charte/verifier-td.py --erreur.
"""
import subprocess
import sys

PROGRAMMES = {
    # Exercice 2 : il y a un truc qui cloche
    'aire.py': '''def aire_carre(longueur):
    return longueur**2

aire = aire_carre()
print("L'aire du carre est de", aire, "m²")''',
    'perimetre.py': '''def perimetre_carre(longueur):
    print(4*longueur)

perimetre = perimetre_carre(12)
print("Le perimetre du carre est", perimetre, "m")''',
    'quotient.py': '''def quotient(x,y)
    return x/y

print(quotient(1.7,2.5))''',
    'triangle.py': '''def aire_triangle_rectangle(base,hauteur):
    return base*hauteur/2

aire_triangle_rectangle(1.7,2.5)''',
    'distance.py': '''def distance_euclidienne(x1, x2, y1, y2):
    dx = (x1-x2)
    dy = (y1-y2)
    distance = math.sqrt(dx**2 + dy**2)

x1, y1, x2, y2 = 1, 2, 5, 7
distance = distance_euclidienne(x1, x2, y1, y2)
print(f"La distance euclidienne entre ({x1}, {y1}) et ({x2}, {y2}) est {distance} m")''',
    'distance-import.py': '''import math
def distance_euclidienne(x1, x2, y1, y2):
    dx = (x1-x2)
    dy = (y1-y2)
    distance = math.sqrt(dx**2 + dy**2)

x1, y1, x2, y2 = 1, 2, 5, 7
distance = distance_euclidienne(x1, x2, y1, y2)
print(f"La distance euclidienne entre ({x1}, {y1}) et ({x2}, {y2}) est {distance} m")''',
    'de.py': '''import random

def de():
    tirage = random.randrange(1, 6)
    return tirage

print("Les trois des sont :", DE(), DE(), "et", DE())''',
    'de-valeurs.py': '''import random
print(sorted(set(random.randrange(1, 6) for _ in range(10000))))''',
    'volume.py': '''def volume_pave(l, l, h):
    return l * l * h

print(volume_pave(2, 72, 10))''',
    'repete.py': '''def n_print(s, n):
    for i in range(n):
        print(s)

print(volume_pave(2, 72, 10))''',
    # Exercice 3 : vous n'auriez pas vu la sortie
    'coucou.py': '''def n_print(s, n):
    for i in range(n):
        print(s)

n_print("Coucou les loulous", 12)''',
    'premiers.py': '''def est_premier(num):
    if num > 2 and num % 2 == 0:
        return False
    for x in range(2, num // 2):
        if num % x == 0:
            return False
    return True

def premiers(x):
    for i in range(2, x+1):
        if est_premier(i):
            print(i)

premiers(22)''',
    'combo.py': '''def f(x, y, z):
    return x + y, x + z, y + z

def g(x, y):
    if x > 10 :
        return 1/y, x/y
    else :
        return 1/x, y/x

def combo(x, y, z):
    a, b, c = f(x, y, z)
    d, e = g(z, x)
    u, v, w = f(a, b, e**2)
    return v - w, b - a

print(f"combo(4, 9, 2) = {combo(4 ,9 ,2)}")''',
    'pixel.py': '''def triangle(c, x):
    for i in range(1, x):
        print(c * i)
    for i in range(x, 1, -1):
        print(c * i)

def pixel_art(n):
    for i in range(1, n, 2):
        triangle("=", i)

pixel_art(7)''',
    # Exercice 1 : exemples d'appels
    'appels.py': '''def compteur3():
    i = 0
    while i < 3:
        print(i)
        i = i + 1

def calcule_cube(a):
    cube = a * a * a
    return cube

def somme_produit(a,b):
    s = a + b
    p = a * b
    return s, p

r = compteur3()
print("compteur3() renvoie", r)
c = calcule_cube(3)
s, p = somme_produit(2, 5)
print(c, s, p)''',
}

# Exercice 1, question « exemples d'appels » : chaque appel proposé, exécuté après les définitions
DEFS = '''def compteur3():
    i = 0
    while i < 3:
        print(i)
        i = i + 1

def double_compteur3():
    compteur3()
    compteur3()

def compteur(stop):
    i = 0
    while i < stop:
        print(i)
        i = i + 1

def compteur_complet(start, stop, step):
    i = start
    while i < stop:
        print(i)
        i = i + step

def calcule_cube(a):
    cube = a * a * a # ou bien a**3
    return cube

def somme_produit(a,b):
    """Calcule la somme et le produit de deux nombres"""
    s = a + b
    p = a * b
    return s, p
'''
APPELS = ['c = calcule_cube(3)', 's, p = somme_produit(2, 5)', 'compteur_complet(0, 10, 2)', 'compteur(5)',
          'cube = calcule_cube()', 's = somme_produit(2)', 'compteur3(3)', 'compteur_complet(0, 10)']
for k, appel in enumerate(APPELS):
    PROGRAMMES[f'appel{k}.py'] = DEFS + '\n' + appel

for nom, code in PROGRAMMES.items():
    open(nom, 'w', encoding='utf-8').write(code + '\n')
    r = subprocess.run([sys.executable, '-I', nom], capture_output=True, text=True)
    print(f'== {nom}\n{r.stdout}{r.stderr}')
