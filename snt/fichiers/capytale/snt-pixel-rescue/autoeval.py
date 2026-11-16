from capytale.autoeval import Validate, validationclass
from ipythonblocks import BlockGrid

# --- Utilitaires de décoration ---
def print_badge(name, icon):
    print(f"\n" + "="*40)
    print(f"🏆 BADGE DÉBLOQUÉ : {name} {icon}")
    print("="*40 + "\n")

# --- Initialisation ---
def go():
    print("🤖 Initialisation des systèmes de la Pixel Force...")
    print("✅ Module d'auto-évaluation chargé.")
    print("🚀 Mission : Restauration de l'image corrompue.")
    return Validate()()

# --- Q1 : Théorie des couleurs ---
@validationclass
class ValidateCouleurs(Validate):
    def __init__(self, questions, reponses, max_trial=3, **kwargs):
        self.questions = questions
        self.reponses = reponses
        super().__init__(**kwargs)

    def __call__(self, rep_jaune, rep_magenta, rep_cyan, rep_total):
        # Normalisation des réponses (minuscule, sans espace)
        rj = rep_jaune.lower().strip()
        rm = rep_magenta.lower().strip()
        rc = rep_cyan.lower().strip()
        rt = rep_total.lower().strip()

        errors = []
        if not ("rouge" in rj and "vert" in rj): errors.append("Le Jaune n'est pas correct.")
        if not ("rouge" in rm and "bleu" in rm): errors.append("Le Magenta n'est pas correct.")
        if not ("vert" in rc and "bleu" in rc): errors.append("Le Cyan n'est pas correct.")
        if "blanc" not in rt: errors.append("Le mélange des trois n'est pas correct.")

        if not errors:
            print_badge("Maître des Lumières", "💡")
            return True
        
        print("⚠️ Erreur de calibrage :")
        for e in errors:
            print(f"  - {e}")
        return False

# --- Q2 : Réglage RGB Rouge ---
@validationclass
class ValidateRouge(Validate):
    def __call__(self, r, g, b):
        if r == 255 and g == 0 and b == 0:
            print("✅ Calibrage Rouge : OK")
            return True
        print(f"❌ Erreur : On attendait du rouge pur. Vous avez R={r}, G={g}, B={b}.")
        return False

# --- Q3 : Mélanges (Jaune, Magenta, Cyan) ---
@validationclass
class ValidateMelanges(Validate):
    def __call__(self, rj, gj, bj, rm, gm, bm, rc, gc, bc):
        success = True
        # Jaune
        if not (rj == 255 and gj == 255 and bj == 0):
            print("❌ Le Jaune est incorrect (R+G).")
            success = False
        # Magenta
        if not (rm == 255 and gm == 0 and bm == 255):
            print("❌ Le Magenta est incorrect (R+B).")
            success = False
        # Cyan
        if not (rc == 0 and gc == 255 and bc == 255):
            print("❌ Le Cyan est incorrect (G+B).")
            success = False
        
        if success:
            print_badge("Alchimiste des Pixels", "🎨")
        return success

# --- Q4 : Manipulation de pixels ---
@validationclass
class ValidatePixel(Validate):
    def __call__(self, grille):
        # On vérifie si la case 0,0 est bien rouge
        try:
            block = grille[0, 0]
            if block.red == 255 and block.green == 0 and block.blue == 0:
                print("✅ Pixel (0,0) activé en ROUGE.")
                return True
            else:
                print(f"❌ Le pixel (0,0) est ({block.red}, {block.green}, {block.blue}) au lieu de (255, 0, 0).")
                return False
        except:
            print("❌ Erreur technique : La grille n'est pas valide.")
            return False

# --- Q5 : Prédiction ---
@validationclass
class ValidatePrediction(Validate):
    def __call__(self, grille_user):
        # On vérifie quelques points clés de la figure prédite (diagonale + coins)
        # (0,0) = Jaune
        # (7,7) = Magenta
        # (2,2) = Bleu
        try:
            checks = [
                (0, 0, 255, 255, 0, "Jaune"),
                (7, 7, 255, 0, 255, "Magenta"),
                (2, 2, 0, 0, 255, "Bleu"),
                (5, 5, 255, 0, 0, "Rouge")
            ]
            for r, c, red, green, blue, color_name in checks:
                b = grille_user[r, c]
                if not (b.red == red and b.green == green and b.blue == blue):
                    print(f"❌ Erreur à la position [{r},{c}]. Ce n'est pas la bonne couleur.")
                    return False
            
            print_badge("Oracle de la Matrice", "🔮")
            return True
        except:
            print("❌ Erreur : Vérifiez votre code.")
            return False

# --- Q7 : Le Boss (Toad) ---
@validationclass
class ValidateToad(Validate):
    def __call__(self, mat):
        # Vérification structurelle simplifiée (points clés du Toad)
        # Toad a un chapeau blanc à pois rouges, visage chair.
        
        # Check dimensions
        if len(mat) != 12 or len(mat[0]) != 12:
            print("❌ La grille doit faire 12x12.")
            return False

        # Check couleurs définies (on suppose que l'élève a gardé les variables b, n, v, br, c)
        # On va vérifier les valeurs brutes dans la matrice
        
        # Test 1: Le sommet du chapeau (blanc) en 0, 4 ou 0, 5
        # Test 2: Un pois rouge (par exemple en 1, 3 si l'élève a bien compté)
        # Test 3: Les yeux (noirs) en 7, 4
        
        # Comme l'élève remplit la matrice, on vérifie quelques coordonnées critiques.
        # Coordonnées basées sur l'image fournie (approximatif pour l'exercice)
        
        errors = 0
        
        # Ligne 0 : Chapeau (ex: Blanc au milieu)
        # Nous allons être souples et vérifier si la matrice ressemble à quelque chose
        # Vérifions juste si la matrice n'est pas vide ou remplie de noir
        is_all_black = True
        for row in mat:
            for pixel in row:
                if pixel != (0,0,0):
                    is_all_black = False
                    break
        
        if is_all_black:
            print("❌ L'image semble vide ou toute noire.")
            return False

        # Vérification spécifique (Yeux noirs)
        # Ligne 7, col 4 et 7, 7 environ
        p_oeil = mat[7][4]
        if p_oeil != (0,0,0):
             print(f"⚠️ Attention, l'oeil gauche en [7][4] ne semble pas noir (trouvé {p_oeil}).")
             errors += 1

        # Vérification Chapeau (Blanc en haut)
        p_chapeau = mat[0][5]
        if p_chapeau != (255, 255, 255):
            print(f"⚠️ Le haut du chapeau en [0][5] n'est pas blanc (trouvé {p_chapeau}).")
            errors += 1

        if errors > 1:
            print("❌ Il y a plusieurs erreurs de placement. Vérifiez votre grille.")
            return False

        print_badge("Restaurateur Légendaire", "🍄")
        print("🎉 Félicitations ! Vous avez terminé la mission.")
        return True

# --- Q7 : Le Boss (Toad) ---
@validationclass
class ValidateToad(Validate):
    def __call__(self, mat):
        # Vérification structurelle simplifiée (points clés du Toad)
        # Toad a un chapeau blanc à pois rouges, visage chair.
        
        # Check dimensions
        if len(mat) != 12 or len(mat[0]) != 12:
            print("❌ La grille doit faire 12x12.")
            return False

        # Check couleurs définies (on suppose que l'élève a gardé les variables b, n, v, br, c)
        # On va vérifier les valeurs brutes dans la matrice
        
        # Test 1: Le sommet du chapeau (blanc) en 0, 4 ou 0, 5
        # Test 2: Un pois rouge (par exemple en 1, 3 si l'élève a bien compté)
        # Test 3: Les yeux (noirs) en 7, 4
        
        # Comme l'élève remplit la matrice, on vérifie quelques coordonnées critiques.
        # Coordonnées basées sur l'image fournie (approximatif pour l'exercice)
        
        errors = 0
        
        # Ligne 0 : Chapeau (ex: Blanc au milieu)
        # Nous allons être souples et vérifier si la matrice ressemble à quelque chose
        # Vérifions juste si la matrice n'est pas vide ou remplie de noir
        is_all_black = True
        for row in mat:
            for pixel in row:
                if pixel != (0,0,0):
                    is_all_black = False
                    break
        
        if is_all_black:
            print("❌ L'image semble vide ou toute noire.")
            return False

        # Vérification spécifique (Yeux noirs)
        # Ligne 7, col 4 et 7, 7 environ
        p_oeil = mat[7][4]
        if p_oeil != (0,0,0):
             print(f"⚠️ Attention, l'oeil gauche en [7][4] ne semble pas noir (trouvé {p_oeil}).")
             errors += 1

        # Vérification Chapeau (Blanc en haut)
        p_chapeau = mat[0][5]
        if p_chapeau != (255, 255, 255):
            print(f"⚠️ Le haut du chapeau en [0][5] n'est pas blanc (trouvé {p_chapeau}).")
            errors += 1

        if errors > 1:
            print("❌ Il y a plusieurs erreurs de placement. Vérifiez votre grille.")
            return False

        print_badge("Restaurateur Légendaire", "🍄")
        print("🎉 Félicitations ! Vous avez terminé la mission.")
        return True

@validationclass
class ValidateSlash(Validate):
    def __call__(self, mat):
        # Vérification structurelle simplifiée (points clés du Toad)
        # Toad a un chapeau blanc à pois rouges, visage chair.
        
        # Check dimensions
        if len(mat) != 20 or len(mat[0]) != 20:
            print("❌ La grille doit faire 20x20.")
            return False
        
        v  = (50, 200, 50)
        g = (200, 200, 200)
        for i in range(8):
            for j in range(8):
                if j == 19-i and grille[i, j] != v:
                    print("❌ La cellule en position ({i}, {j}) doit etre de couleur verte {v}. Vérifiez votre grille.")
                    return False
                if j != 19-i and grille[i, j] != g:
                    print("❌ La cellule en position ({i}, {j}) doit etre de couleur grise {g}. Vérifiez votre grille.")
                    return False

        print("🎉 Félicitations ! Vous avez terminé la commande.")
        return True

@validationclass
class ValidateXmen(Validate):
    def __call__(self, mat):
        # Vérification structurelle simplifiée (points clés du Toad)
        # Toad a un chapeau blanc à pois rouges, visage chair.
        
        # Check dimensions
        if len(mat) != 20 or len(mat[0]) != 20:
            print("❌ La grille doit faire 20x20.")
            return False
        
        v  = (50, 200, 50)
        g = (200, 200, 200)
        for i in range(20):
            for j in range(20):
                if (j == 19-i or j == i) and grille[i, j] != v:
                    print("❌ La cellule en position ({i}, {j}) doit etre de couleur verte {v}. Vérifiez votre grille.")
                    return False
                if (j != 19-i and j != i) and grille[i, j] != g:
                    print("❌ La cellule en position ({i}, {j}) doit etre de couleur grise {g}. Vérifiez votre grille.")
                    return False

        print("🎉 Félicitations ! Vous avez terminé la commande.")
        return True


# Instanciation des validateurs
check_couleurs = ValidateCouleurs(questions="Q1", reponses="Q1")
check_rouge = ValidateRouge()
check_melanges = ValidateMelanges()
check_pixel = ValidatePixel()
check_prediction = ValidatePrediction()
check_toad = ValidateToad()
check_slash = ValidateSlash()
check_xmen = ValidateXmen()
