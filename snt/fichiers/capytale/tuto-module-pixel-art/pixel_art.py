"""
Module permettant d'écrire des programmes pour créer des images en "pixel art"
Adaptation du travail de Mathieu Degrange (https://github.com/DegrangeM/pyxel-art)

Auteur : Germain BECKER
Licence : CC BY-NC-SA

//!\\ ATTENTION
Ce module ne fonctionne qu'avec Basthon et donc aussi sur Capytale.
En effet, il est basé sur le module p5 porté dans Basthon par Romain Casati, module
lui-même basé sur la bibliothèque JavaScript p5.js (qui diffère du module p5 que l'on
peut obtenir avec la commande pip install p5).
"""

from p5 import *
from inspect import currentframe
from copy import deepcopy
import __main__

MARGE_BAS = 50

# Initialisation du dictionnaire stockant toutes les données nécessaires à un pixel art
pixel_art = {
    'L': 9,
    'H': 9,
    'TAILLE_PIXEL': 30,
    'grille_visible': True,
    'coord_visibles': True,
    'correction_visible': False,
    'correction_differee': False,
    'pixels': [[(255, 255, 255)]*9 for j in range(9)],
    'pix_colories': {},
    'etapes': [[(255, 255, 255)]*9 for j in range(9)],
    'num_etape': 0,
    'animation': False,
    'deux_images': False,
    'bons_pixels': [],
    'dessin_libre': False,
    'pixels_proposes': [],
    'programme': ''
}

def dessiner_image(grille, taille_pixel, x=0, y=0):
    """
    Dessine l'image dont les pixels sont représentés par grille.
    
    Paramètres
    ----------
    grille
        une liste de listes (de tuples)
    taille_pixel
        un entier dont la valeur est le côté du carré représentant un pixel
    x
        l'abscisse du coin supérieur gauche de l'image
    y
        l'ordonnée du coin supérieur gauche de l'image
    """
    for i in range(len(grille)):  # numéro de ligne
        for j in range(len(grille[0])):  # numéro de colonne
            if pixel_art['grille_visible']:
                stroke(50)
            # on fixe la couleur du pixel
            fill(grille[i][j])
            # on crée le pixel
            square(x + (j+1) * taille_pixel , y + (i+1) * taille_pixel, taille_pixel)  
            if pixel_art['correction_visible']:
                # on écrit le numéro de ligne du code du script
                ecrire_num_ligne_code(i, j, taille_pixel, x, y)

def ecrire_num_ligne_code(i, j, taille_pixel, x=0, y=0):
    """
    Écrit dans le pixel de coordonnées (j, i) le numéro de ligne du code du 
    script le coloriant.
    """
    textFont("Consolas")
    textSize(taille_pixel // 2 + 1)
    if (j, i) in pixel_art['pix_colories']:
        noStroke()
        fill(255)
        num_ligne = pixel_art['pix_colories'][(j, i)]
        if num_ligne <= 9:
            text(num_ligne, x + (j+1) * taille_pixel + taille_pixel//3 , \
                 y + (i+1) * taille_pixel + 2*taille_pixel//3)
        else:
            text(num_ligne, x + (j+1) * taille_pixel + taille_pixel//4 , \
                 y + (i+1) * taille_pixel + 2*taille_pixel//3)
                    
def ecrire_coordonnees(grille, taille_pixel, x=0, y=0):
    """
    Écrit les valeurs sur les axes des abscisses et des ordonnées.
    
    Paramètres
    ----------
    grille
        une liste de listes (de tuples)
    taille_pixel
        un entier dont la valeur est le côté du carré représentant un pixel
    x
        l'abscisse du coin supérieur gauche de l'image
    y
        l'ordonnée du coin supérieur gauche de l'image
    """
    textSize(taille_pixel // 2 + 1)
    fill(50)
    for i in range(len(grille)):
        if i <= 9:
            text(i, x + taille_pixel//4, y + (i+1) * taille_pixel + 2*taille_pixel//3)
        else:
            text(i, x, y + (i+1) * taille_pixel + 2*taille_pixel//3)
    for j in range(len(grille[0])):
        if j <= 9:
            text(j, x + (j+1) * taille_pixel + taille_pixel//3, y + 2*taille_pixel//3)
        else:
            text(j, x + (j+1) * taille_pixel + taille_pixel//4, y + 2*taille_pixel//3)           

def creer_image(largeur, hauteur):
    """
    Crée une image de dimension largeur * hauteur.
    
    Paramètres
    ----------
    largeur
        un entier positif égal au nombre de pixels en largeur
    hauteur
        un entier positif égal au nombre de pixels en hauteur
    
    Cette fonction permet de réinitialiser toutes les données d'un pixel art.
    """
    if not largeur >= 1:
        raise ValueError("la largeur doit être un entier supérieur à 1.")
    if not hauteur >= 1:
        raise ValueError("la hauteur doit être un entier supérieur à 1.")
    pixel_art['L'] = largeur
    pixel_art['H'] = hauteur
    pixel_art['TAILLE_PIXEL'] = 30
    pixel_art['pixels'] = [[(255, 255, 255)]*largeur for j in range(hauteur)]
    pixel_art['pix_colories'] = {}
    pixel_art['etapes'] = [[[(255, 255, 255)]*largeur for j in range(hauteur)]]
    pixel_art['grille_visible']= True
    pixel_art['coord_visibles'] = True
    pixel_art['correction_visible'] = False
    pixel_art['correction_differee'] = False
    pixel_art['num_etape'] = 0
    pixel_art['animation'] = False
    pixel_art['deux_images'] = False
    pixel_art['bons_pixels'] = []
    pixel_art['dessin_libre'] = False
    #pixel_art['pixels_proposes'] = []

    
def colorier(x, y, couleur=(150,150,150)):
    """
    Modifie la couleur du pixel de coordonnées (x, y).
    Le troisième paramètre couleur est optionnel. Lui donner une valeur pour 
    définir une autre couleur que le gris par défaut.
    """
    if not(0 <= x < pixel_art['L']):
        raise ValueError(f"{x} n'est pas une abscisse valide")
    if not(0 <= y < pixel_art['H']):
        raise ValueError(f"{y} n'est pas une ordonnée valide")
    if not isinstance(couleur, tuple) or len(couleur) != 3:
        raise SyntaxError(("La couleur doit être un triplet (r,v,b) de trois "
                           "valeurs"))
        
    # on colorie le pixel (x, y)
    pixel_art['pixels'][y][x] = couleur
    # on lui associe le numéro de ligne du script qui l'a colorié
    pixel_art['pix_colories'][(x, y)] = currentframe().f_back.f_lineno
    # on ajoute la liste des pixels dans la liste d'étapes
    # seulement si l'image est de petite dimension
    if pixel_art['L'] * pixel_art['H'] <= 1000:
        pixel_art['etapes'].append(deepcopy(pixel_art['pixels']))
    

def afficher_image(correction=False, tp=30, grille=True, coord=True, animation=False):
    """
    Affiche à l'écran l'image correspondant au programme.
    
    Paramètres
    ----------
    correction
        un booléen qui indique si la correction est affichée ou non
    tp
        un entier égal au côté du carré représentant un pixel à l'écran
    grille
        un booléen qui indique si le quadrillage est affiché ou non
    coord
        un booléen qui indique si les axes sont affichés ou non
    animation
        un booléen qui indique si une animation est à afficher ou non
    """
    # mise à jour éventuelle des booléens
    pixel_art['correction_visible'] = correction
    pixel_art['TAILLE_PIXEL'] = tp
    pixel_art['grille_visible'] = grille
    pixel_art['coord_visibles'] = coord
    pixel_art['dessin_libre'] = False
    
    if pixel_art['L'] * pixel_art['H'] <= 1000:
        pixel_art['animation'] = animation
    else:
        if pixel_art['animation']:
            print("L'animation est impossible pour une image d'aussi grande dimension.")
        pixel_art['animation'] = False
    
    run()  # lance les fonctions setup (une fois) et draw (en boucle infinie)

def sauvegarder(nom_fichier=''):
    """
    Lance le téléchargement de la dernière fenêtre graphique.
    
    Paramètre
    ---------
    nom_fichier
        une chaîne de caractère égale au nom du fichier téléchargé
    
    L'image est téléchargée au format PNG par défaut.
    """
    save(nom_fichier)
    
def recuperer_pixels():
    """
    Renvoie la liste des pixels du dernier pixel art construit.
    """
    return pixel_art['pixels']

def mettre_dans_image(liste_pixels):
    """
    Crée un pixel art à partir de la liste de pixels donnée en paramètre.
    """
    if not isinstance(liste_pixels, list):
        raise TypeError("il faut passer une liste en paramètre.")    
    if len(liste_pixels) == 0:
        raise ValueError("la liste de pixels ne peut pas être vide.")
    largeur_premiere_ligne = len(liste_pixels[0])
    if any(len(ligne) != largeur_premiere_ligne for ligne in liste_pixels):
        raise ValueError(("chaque ligne doit posséder le même nombre de "
                          "pixels."))
    
    pixel_art['L'] = largeur_premiere_ligne
    pixel_art['H'] = len(liste_pixels)
    pixel_art['pixels'] = [[(255, 255, 255)]*pixel_art['L'] for j in range(pixel_art['H'])]
    for i in range(pixel_art['H']):
        for j in range(pixel_art['L']):
            if not (isinstance(liste_pixels[i][j], tuple) \
                    and len(liste_pixels[i][j]) == 3 \
                    and all(isinstance(c, int) for c in liste_pixels[i][j])): 
                raise TypeError(("chaque pixel doit être un triplet de 3 "
                                 "entiers"))
            pixel_art['pixels'][i][j] = liste_pixels[i][j]            


def est_une_chaine_vide_ou_constituee_d_espace(chaine):
    """Renvoie True si et seulement si la chaine est vide ou constituée
    uniquement d'espaces."""
    if chaine == '':
        return True
    elif all(carac == ' ' for carac in chaine):
        return True
    return False

def compter_chaines_non_vides(liste_de_chaines):
    """
    Renvoie le nombre de chaînes de liste_de_chaines qui sont différentes de la chaîne vide
    ou d'une chaîne constituée uniquement d'espaces.
    
    Paramètres
    ----------
    liste_de_chaines
        une liste de chaînes de caractères
        
    Sortie
    ------
    Un entier positif ou nul
    """
    n = len(liste_de_chaines)
    c = 0
    for chaine in liste_de_chaines:
        if est_une_chaine_vide_ou_constituee_d_espace(chaine):
            c = c + 1
    return n - c

def creer_liste_sans_chaine_vide_ou_d_espaces_en_debut_et_fin(liste_de_chaines):
    """
    Renvoie une nouvelle liste mais sans les éléments de `liste_de_chaines` égaux 
    à une chaîne vide ou à une chaîne constituée uniquement d'espaces.
    
    Exemple
    >>> L = ['hello', '', 'world', '  ']
    >>> creer_liste_sans_chaine_vide_ou_d_espaces_en_debut_et_fin(L)
    ['hello', 'world']
    """
    return [chaine for chaine in liste_de_chaines if not est_une_chaine_vide_ou_constituee_d_espace(chaine)]

def nb_lignes_python_derniere_cellule_executee():
    """
    Analyse le programme écrit dans la dernière cellule exécutée par l'utilisateur.
    Renvoie le nombre de lignes contenant du code Python dans celle-ci.
    """
    # ligne d'appel à la fonction `verification_programme`
    # il faut revenir deux frames en arrière !
    ligne = currentframe().f_back.f_back.f_lineno
    
    # le code exécuté dans la dernière cellule
    programme_cellule = __main__.In[-1]
    # la liste avec les lignes de ce code jusqu'à l'appel à `verification_programme` (exclue)
    lignes_programme = programme_cellule.split('\n')[:ligne-1]
    
    # le nombre de lignes Python de la dernière cellule de code exécutée
    nb_lignes = compter_chaines_non_vides(lignes_programme)
    
    # la liste des lignes Python nettoyée au début et à la fin
    # (ne sert pas pour le moment : peut être utilisée pour récrire le code dans la fenêtre ou dans une image)
    lignes_programme_nettoyee = creer_liste_sans_chaine_vide_ou_d_espaces_en_debut_et_fin(lignes_programme)
    
    return nb_lignes

def programme_python_derniere_cellule_executee():
    """
    Renvoie le programme écrit dans la dernière cellule exécutée par l'utilisateur.
    La ligne avec l'appel à `demarrer_dessin_libre` est ignorée.
    Sont supprimées les lignes vides inutiles à la fin.
    """
    # ligne d'appel à la fonction `demarrer_dessin_libre`
    # il faut revenir deux frames en arrière !
    ligne = currentframe().f_back.f_back.f_lineno
    
    # le code exécuté dans la dernière cellule
    programme_cellule = __main__.In[-1]
    # la liste avec les lignes de ce code jusqu'à l'appel à `verification_programme` (exclue)
    lignes_programme = programme_cellule.split('\n')[:ligne-1]
    
    # nombre de lignes vides ou formée d'espaces à la FIN
    i = len(lignes_programme) - 1
    while i >= 0:
        if est_une_chaine_vide_ou_constituee_d_espace(lignes_programme[i]):
            i = i - 1
            break
    N = len(lignes_programme) - 1 - i
    
    # la liste des lignes Python nettoyée au début et à la fin
    # (ne sert pas pour le moment : peut être utilisée pour récrire le code dans la fenêtre ou dans une image)
    lignes_programme_nettoyee = lignes_programme[:-N]    
    
    return "\n".join(lignes_programme_nettoyee)

def verifier_programme(liste_bons_pixels, nb_max_lignes=None, tp=30, grille=True, coord=True):
    """
    Vérifie si le programme écrit crée bien la bonne liste de pixels `liste_bons_pixels`,
    et éventuellement que le nombre de lignes ne dépasse `nb_max_lignes`. 
    
    Paramètres
    ----------
    liste_bons_pixels
        une liste avec les valeurs des pixels de l'image attendue
    nb_max_lignes
        un entier correspond au nombre maximal de lignes autorisé (optionnel)
    tp, correction, grille, coord
        des booléens comme définis dans la fonction `afficher_image`
    """
    # mise à jour des modalités du parcours
    pixel_art['animation'] = False  # FORCEMENT
    pixel_art['TAILLE_PIXEL'] = tp
    pixel_art['correction_visible'] = False  # FORCEMENT
    pixel_art['grille_visible'] = grille
    pixel_art['coord_visibles'] = coord
    pixel_art['deux_images'] = True  # FORCEMENT
    pixel_art['bons_pixels'] = liste_bons_pixels
    
    
    # nb de ligne de la dernière cellule exécutée    
    nb_lignes = nb_lignes_python_derniere_cellule_executee()
    
    # comparaison du programme proposé à la liste de cases attendue
    correct = liste_bons_pixels == pixel_art['pixels']
    
    # test de la longueur du programme proposé
    if nb_max_lignes:  # si nb_max_lignes n'est pas None
        # comparaison de la longueur du prog proposé avec le nombre max de lignes attendu
        
        longueur = nb_lignes <= nb_max_lignes
    else:  # si la valeur associée à la clé `nb_max_lignes` est None
        longueur = True  
    
    # affichage de la correction
    if correct:
        if longueur:
            print("✅ Excellent !\n Ci-dessous à gauche votre pixel art et à droite celui qu'il faut obtenir.")
        else:
            print(f"⚠️ Le pixel art est correct mais votre programme fait {nb_lignes} lignes alors qu'il doit en faire au plus {nb_max_lignes}.")
    else:
        print("❌ C'est à revoir. Ci-dessous à gauche votre pixel art et à droite celui qu'il faut obtenir :")
    afficher_image(False, tp, grille, coord, animation=False)
    

####---- BOUTONS D'ANIMATIONS ----####

def dessiner_boutons():
    """
    Dessine les boutons d'animation.
    """
    fill(239)
    stroke(0)
    strokeWeight(1)
    quart_largeur = (pixel_art['TAILLE_PIXEL'] * (pixel_art['L']+1) + pixel_art['TAILLE_PIXEL']) // 4
    for i in range(4):
        rect(40*i + quart_largeur, pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15, 30, 30)

def ecrire_texte_boutons():
    """
    Écrit le texte sur chaque bouton.
    """
    textSize(12)
    textFont('Consolas')
    noStroke()
    fill(20)
    quart_largeur = (pixel_art['TAILLE_PIXEL'] * (pixel_art['L']+1) + pixel_art['TAILLE_PIXEL']) // 4
    textes = ["<<", "<", ">", ">>"]
    for i in range(4):
        text(textes[i], 40*i + quart_largeur + 10, pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 35)


#### ---- GESTION DES CLICS ET DE L'ANIMATION ---- ####
        
def survol_debut(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton début. """
    quart_largeur = (pixel_art['TAILLE_PIXEL'] * (pixel_art['L']+1) + pixel_art['TAILLE_PIXEL']) // 4
    hauteur = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15
    return quart_largeur <= x <= quart_largeur + 30 and hauteur <= y <= hauteur + 30

def survol_reculer(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton reculer. """
    quart_largeur = (pixel_art['TAILLE_PIXEL'] * (pixel_art['L']+1) + pixel_art['TAILLE_PIXEL']) // 4
    hauteur = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15
    return quart_largeur + 40 <= x <= quart_largeur + 70 and hauteur <= y <= hauteur + 30

def survol_avancer(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton avancer. """
    quart_largeur = (pixel_art['TAILLE_PIXEL'] * (pixel_art['L']+1) + pixel_art['TAILLE_PIXEL']) // 4
    hauteur = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15
    return quart_largeur + 80 <= x <= quart_largeur + 110 and hauteur <= y <= hauteur + 30

def survol_fin(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton fin. """
    quart_largeur = (pixel_art['TAILLE_PIXEL'] * (pixel_art['L']+1) + pixel_art['TAILLE_PIXEL']) // 4
    hauteur = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15
    return quart_largeur + 120 <= x <= quart_largeur + 150 and hauteur <= y <= hauteur + 30


def debut():
    """
    Dessine le pixel art dans son état initial, une image non colorée.
    """
    pixel_art['num_etape'] = 0  # première étape
    dessiner_image(pixel_art['etapes'][pixel_art['num_etape']], pixel_art['TAILLE_PIXEL'], x=0, y=0)

    
def reculer():
    """
    Dessine le pixel art une étape en arrière dans la coloration des pixels.
    """
    if pixel_art['num_etape'] > 0:
        pixel_art['num_etape'] = pixel_art['num_etape'] - 1
        dessiner_image(pixel_art['etapes'][pixel_art['num_etape']], pixel_art['TAILLE_PIXEL'], x=0, y=0)

        
def avancer():
    """
    Dessine le pixel art une étape en avant dans la coloration des pixels.
    """
    if pixel_art['num_etape'] < len(pixel_art['etapes']) - 1:
        pixel_art['num_etape'] = pixel_art['num_etape'] + 1
        dessiner_image(pixel_art['etapes'][pixel_art['num_etape']], pixel_art['TAILLE_PIXEL'], x=0, y=0)

def fin():
    """
    Dessine le pixel art dans son état final.
    """
    pixel_art['num_etape'] = len(pixel_art['etapes']) - 1
    dessiner_image(pixel_art['etapes'][pixel_art['num_etape']], pixel_art['TAILLE_PIXEL'], x=0, y=0)


def gerer_animation_clic(x, y):
    """
    Détecte les clics sur les boutons et gère l'avancée de l'animation.
    """
    if mouseIsPressed and survol_debut(x, y):
        debut()
        frameRate(3)  # POUR NE PAS DÉTECTER PLUSIEURS CLICS !!
    elif mouseIsPressed and survol_reculer(x, y):
        reculer()
        frameRate(3)
    elif mouseIsPressed and survol_avancer(x, y):
        avancer()
        frameRate(3)
    elif mouseIsPressed and survol_fin(x, y):
        fin()
        frameRate(3)


####---- GESTION DES DESSINS LIBRES ----####
        
def demarrer_dessin_libre(correction=False, tp=30):
    pixel_art['dessin_libre'] = True
    pixel_art['correction_differee'] = correction
    pixel_art['TAILLE_PIXEL'] = tp
    largeur, hauteur = pixel_art['L'], pixel_art['H']
    pixel_art['pixels_proposes'] = [[(255, 255, 255)]*largeur for j in range(hauteur)]
    print("🖌️ Créez le pixel art correspondant à ce programme en cliquant sur les bons pixels.")
    run()


def gerer_dessin_libre(x, y):
    L = pixel_art['L']
    H = pixel_art['H']
    taille_pixel = pixel_art['TAILLE_PIXEL']
    largeur_totale = taille_pixel * (L+1)
    hauteur_totale = taille_pixel * (H+1)
    if mouseIsPressed and taille_pixel <= x <= largeur_totale and taille_pixel <= y <= hauteur_totale:
        x, y = coordonnees_pixel_clique(mouseX, mouseY, taille_pixel)
        modifier_couleur_pixel(x, y)
        frameRate(3)
        
def modifier_couleur_pixel(x, y):
    if pixel_art['pixels_proposes'][y][x] != (150, 150, 150):
        pixel_art['pixels_proposes'][y][x] = (150, 150, 150)
    else:
        pixel_art['pixels_proposes'][y][x] = (255, 255, 255)


def coordonnees_pixel_clique(x, y, taille_pixel):
    """x et y sont les coordonnées"""
    return int(x//taille_pixel) - 1, int(y//taille_pixel) - 1


def ecrire_programme():
    programme = programme_python_derniere_cellule_executee()
    #text(programme, 0, 0)
    
####---- BOUTON VALIDATION ----####

def dessiner_boutons_dessin_libre():
    dessiner_btn_validation()
    dessiner_btn_reinitialiser()
    dessiner_btn_reponse()

def dessiner_btn_validation():
    fill(239)
    stroke(0)
    strokeWeight(1)
    rect(pixel_art['TAILLE_PIXEL'], pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15, 70, 30)
    textSize(14)
    textFont('Consolas')
    noStroke()
    fill(20)
    text("Valider", pixel_art['TAILLE_PIXEL'] + 9 , pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 35)


def dessiner_btn_reinitialiser():
    fill(239)
    stroke(0)
    strokeWeight(1)
    rect(pixel_art['TAILLE_PIXEL'] + 90, pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15, 70, 30)
    textSize(14)
    textFont('Consolas')
    noStroke()
    fill(20)
    text("Effacer", pixel_art['TAILLE_PIXEL'] + 99 , pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 35)
    
    
def dessiner_btn_reponse():
    fill(239)
    stroke(0)
    strokeWeight(1)
    rect(pixel_art['TAILLE_PIXEL'] + 180, pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15, 70, 30)
    textSize(14)
    textFont('Consolas')
    noStroke()
    fill(20)
    text("Réponse", pixel_art['TAILLE_PIXEL'] + 189 , pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 35)

#### ---- GESTION DU BOUTON VALIDATION ---- ####

def survol_btn_validation(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton de validation. """
    abs_correcte = pixel_art['TAILLE_PIXEL'] <= x <= pixel_art['TAILLE_PIXEL'] + 70
    ord_correcte = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15 <= y <= pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15 + 30
    return abs_correcte and ord_correcte


def gerer_clic_btn_validation(x, y):
    if mouseIsPressed and survol_btn_validation(x, y):
        correction()
        frameRate(3)

def correction():
    if pixel_art['pixels_proposes'] == pixel_art['pixels']:
        print("✅ Excellent !")
        stop()
    else:
        print("❌ C'est à revoir.")


#### ---- GESTION BOUTON DE RENITIALISATION ---- ####

def survol_btn_reinitialiser(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton de validation. """
    abs_correcte = pixel_art['TAILLE_PIXEL'] + 90 <= x <= pixel_art['TAILLE_PIXEL'] + 90 + 70
    ord_correcte = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15 <= y <= pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15 + 30
    return abs_correcte and ord_correcte


def gerer_clic_btn_reinitialiser(x, y):
    if mouseIsPressed and survol_btn_reinitialiser(x, y):
        reinitialiser()
        frameRate(3)

def reinitialiser():
    L = pixel_art['L']
    H = pixel_art['H']
    pixel_art['pixels_proposes'] = [[(255, 255, 255)]*L for j in range(H)]
    

####---- GESTION BOUTON VOIR LA REPONSE ----####

def survol_btn_reponse(x, y):
    """ Renvoie True si les coordonnées (x, y) de la souris sont sur le bouton de validation. """
    abs_correcte = pixel_art['TAILLE_PIXEL'] + 180 <= x <= pixel_art['TAILLE_PIXEL'] + 180 + 70
    ord_correcte = pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15 <= y <= pixel_art['TAILLE_PIXEL']*(pixel_art['H']+1) + 15 + 30
    return abs_correcte and ord_correcte


def gerer_clic_btn_reponse(x, y):
    if mouseIsPressed and survol_btn_reponse(x, y):
        pixel_art['dessin_libre'] = False
        pixel_art['correction_visible'] = pixel_art['correction_differee']
        print("Voici la correction 👆")
        dessiner_image(pixel_art['pixels'], pixel_art['TAILLE_PIXEL'])
        stop()


####---- FONCTIONS SETUP ET DRAW ----####


def setup():
    """
    Fonction setup nécessaire au module p5.
    Définit tous les paramètres nécessaires à l'affichage et affiche le pixel art.
    """
    taille_pixel = pixel_art['TAILLE_PIXEL']
    L = pixel_art['L']
    H = pixel_art['H']
    textFont("Consolas")
    textSize(taille_pixel // 2 + 1)
    if pixel_art['grille_visible']:
        stroke(50)
    else:
        noStroke()
    
    if not pixel_art['deux_images']:  # cas d'une image affichée
        if pixel_art['animation'] or pixel_art['dessin_libre']:
            createCanvas(max(taille_pixel * (L+1) + taille_pixel, 300), taille_pixel * (H+1) \
                         + MARGE_BAS)
        else:
            createCanvas(max(taille_pixel * (L+1) + taille_pixel, 300), taille_pixel * (H+1) \
                         + taille_pixel)
        if pixel_art['animation']:
            pa = pixel_art['etapes'][0]
            dessiner_boutons()
            ecrire_texte_boutons()
        else:
            pa = pixel_art['pixels']
            noLoop()
        dessiner_image(pa, taille_pixel)
        if pixel_art['coord_visibles']:
            ecrire_coordonnees(pa, taille_pixel)
    else:  # cas de deux images affichées
        largeur_un_pixel_art = taille_pixel * (L+1) + taille_pixel
        hauter_pixel_art = taille_pixel * (H+1) + taille_pixel
        createCanvas(max(2 * (largeur_un_pixel_art + taille_pixel), 300), hauter_pixel_art)
        dessiner_image(pixel_art['pixels'], taille_pixel)
        dessiner_image(pixel_art['bons_pixels'], taille_pixel, x=largeur_un_pixel_art + taille_pixel)
        if pixel_art['coord_visibles']:
            ecrire_coordonnees(pixel_art['pixels'], taille_pixel)
            ecrire_coordonnees(pixel_art['bons_pixels'],taille_pixel, x=largeur_un_pixel_art + taille_pixel)
        noLoop()
    if pixel_art['dessin_libre']:
        dessiner_image(pixel_art['pixels_proposes'], taille_pixel)
        dessiner_boutons_dessin_libre()
        loop()

def draw():
    """
    Fonction draw nécessaire au module p5.
    Actualise continuellement la fenêtre graphique.
    Ne sert qu'en cas d'animation.
    """
    frameRate(30)
    if pixel_art['animation']:
        gerer_animation_clic(mouseX, mouseY)
    if pixel_art['dessin_libre']:
        gerer_dessin_libre(mouseX, mouseY)
        gerer_clic_btn_validation(mouseX, mouseY)
        gerer_clic_btn_reinitialiser(mouseX, mouseY)
        dessiner_image(pixel_art['pixels_proposes'], pixel_art['TAILLE_PIXEL'])
        gerer_clic_btn_reponse(mouseX, mouseY)
