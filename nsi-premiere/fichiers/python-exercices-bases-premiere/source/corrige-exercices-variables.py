"""Corrigé de la feuille « Les variables » : les valeurs calculées par exécution.

Lancer : python3 -I corrige-exercices-variables.py (Python 3.13).
Chaque programme de l'énoncé est exécuté ligne par ligne (les saisies sont fournies) ;
après chaque ligne, on affiche les variables et leur type.
"""
import builtins
import io
import contextlib

PROGRAMMES = {
    'Exemple (rayon 2)': ('''PI = 3.1415
rayon = float(input("Saisissez le rayon :"))
perimetre = 2 * PI * rayon
print("Le perimetre du cercle est", perimetre, "m")''', ['2']),
    'Formulaire (John Doe, 35 ans)': ('''nom = input("Saisissez votre nom :")
prenom = input("Saisissez votre prenom :")
age = int(input("Saisissez votre age :"))
print("Vous vous appelez", prenom, nom, "et vous avez", age, "ans.")''', ['Doe', 'John', '35']),
    'Multiplication (2 et 24)': ('''a = int(input("Saisissez un nombre :"))
b = int(input("Saisissez un nombre :"))
res = a * b
print("Le produit de", a, "et", b, "vaut", res)''', ['2', '24']),
    'Chichoumeille niveau 1': ('''a = 3
b = a - 1
c = b * a
a = 12
a = 2 * a - (c * b)''', []),
    'Chichoumeille niveau 2': ('''a = 3
b = 6
c = b // a
c = 2**c
b = c % a''', []),
    'Chichoumeille niveau 3': ('''a = 1
b = a > 0
a = (a+1)**2
b = a <= 4
b = (a % 2) == 0''', []),
    'Chichoumeille hardcore': ('''a = 15
b = (a % 3 + 1)**a
c = (b * 5 // 3) >= 2
a = a + a / 2
b = b % (b+1) - a''', []),
}

for titre, (code, saisies) in PROGRAMMES.items():
    print('==', titre)
    reste = list(saisies)
    g = {'input': lambda invite='': reste.pop(0)}
    for n, ligne in enumerate(code.split('\n'), 1):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            exec(ligne, g)
        etat = {k: v for k, v in g.items() if k not in ('input', '__builtins__')}
        print(f'  ligne {n} : ' + ', '.join(f'{k} = {v!r} ({type(v).__name__})' for k, v in etat.items()))
        if f.getvalue():
            print('  affiche :', f.getvalue().strip())
