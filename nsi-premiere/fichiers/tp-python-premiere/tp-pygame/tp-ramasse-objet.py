import pygame
import random

# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR, HAUTEUR = 800, 600
TAILLE_JOUEUR = 50
TAILLE_OBJET = 20
VITESSE_JOUEUR = 5
VITESSE_OBJET = 3

# Couleurs
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)

# Création de la fenêtre
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Attrape les objets")

# Position initiale
joueur_x = LARGEUR // 2
objet_x = random.randint(0, LARGEUR - TAILLE_OBJET)
objet_y = 0
score = 0

# Boucle de jeu
jeu_en_cours = True
while jeu_en_cours:
    pygame.time.delay(30)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jeu_en_cours = False

    # Gestion des touches
    touches = pygame.key.get_pressed()
    if touches[pygame.K_LEFT] and joueur_x > 0:
        joueur_x -= VITESSE_JOUEUR
    if touches[pygame.K_RIGHT] and joueur_x < LARGEUR - TAILLE_JOUEUR:
        joueur_x += VITESSE_JOUEUR

    # Déplacement de l'objet
    objet_y += VITESSE_OBJET

    # Vérification de collision
    if (objet_y + TAILLE_OBJET >= HAUTEUR - TAILLE_JOUEUR and
        joueur_x < objet_x + TAILLE_OBJET and
        joueur_x + TAILLE_JOUEUR > objet_x):
        score += 1
        objet_x = random.randint(0, LARGEUR - TAILLE_OBJET)
        objet_y = 0

    # Vérification de la fin du jeu
    if objet_y > HAUTEUR:
        print(f"Game Over! Score final: {score}")
        jeu_en_cours = False

    # Affichage
    fenetre.fill(BLANC)
    pygame.draw.rect(fenetre, ROUGE, (joueur_x, HAUTEUR - TAILLE_JOUEUR, TAILLE_JOUEUR, TAILLE_JOUEUR))
    pygame.draw.rect(fenetre, VERT, (objet_x, objet_y, TAILLE_OBJET, TAILLE_OBJET))
    pygame.display.update()

pygame.quit()
