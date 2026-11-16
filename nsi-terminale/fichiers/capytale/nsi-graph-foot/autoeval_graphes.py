from capytale.autoeval import Validate, validationclass
import math

# --- Utilitaires ---
def print_badge(name, icon):
    print(f"\n" + "="*40)
    print(f"🏆 BADGE DÉBLOQUÉ : {name} {icon}")
    print("="*40 + "\n")

def go():
    print("🤖 Initialisation de l'arbitre vidéo (VAR)...")
    print("✅ Module d'auto-évaluation chargé.")
    return Validate()()

@validationclass
class ValidateGraph(Validate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # --- PARTIE 1 : LECTURE ---
    def check_q1(self, R1):
        if R1 == 2:
            print("✅ Q1 Correct ! Le poids est bien 2.")
            return True
        print(f"❌ Erreur Q1 : Tu as trouvé {R1}, mais on attend 2 (Ligne OL -> Colonne Strasbourg).")
        return False

    def check_q2(self, R2):
        if R2.upper().strip() == "OM":
            print("✅ Q2 Correct ! Rennes a battu l'OM.")
            return True
        print(f"❌ Erreur Q2 : Tu as trouvé '{R2}'. Regarde la ligne de Rennes, il y a un '1' dans la colonne 0 (OM).")
        return False

    def check_q3(self, R3):
        if R3 == 3:
            print_badge("Observateur Attentif", "👀")
            return True
        print(f"❌ Erreur Q3 : Le plus grand chiffre dans le tableau n'est pas {R3}.")
        return False

    # --- PARTIE 2 : VICTOIRES ---
    def check_q4(self, R4):
        if R4 == 0:
            print("✅ Q4 Correct ! Lille n'a aucune victoire (que des 0).")
            return True
        print(f"❌ Erreur Q4 : Lille n'a pas {R4} victoires.")
        return False

    def check_compter_victoires(self, compter_victoires, MATRICE_POIDS):
        try:
            if compter_victoires(MATRICE_POIDS, 3) == 4 and compter_victoires(MATRICE_POIDS, 4) == 0:
                print_badge("Compteur de Victoires", "✅")
                return True
            print("❌ Erreur : La fonction ne compte pas correctement (Vérifie OL=4 et Lille=0).")
            return False
        except Exception as e:
            print(f"❌ Erreur de code : {e}")
            return False

    def check_trouver_meilleur_gagneur(self, trouver_meilleur_gagneur, MATRICE_POIDS, EQUIPES):
        try:
            if trouver_meilleur_gagneur(MATRICE_POIDS, EQUIPES).upper().strip() == "OL":
                print_badge("Leader du Classement", "🥇")
                return True
            print("❌ Erreur : Ce n'est pas la bonne équipe.")
            return False
        except:
            return False

    # --- PARTIE 3 : RATIO ---
    def check_score_predictif_simple_func(self, func):
        try:
            if math.isclose(func(10, 2), 5.0) and func(5, 0) >= 1000:
                print_badge("Algorithme SPS Validé", "⚙️")
                return True
            print("❌ Erreur : Vérifie ta formule (division) et le cas où on divise par 0.")
            return False
        except:
            return False

    def check_resultats_sps(self, R5, R6):
        if math.isclose(R5, 1.5) and R6.upper().strip() == "LENS":
            print_badge("Analyste Financier", "📈")
            return True
        print("❌ R5 ou R6 incorrects.")
        return False

    # --- PARTIE 4 : INFLUENCE ---
    def check_score_influence_func(self, func, MATRICE, victoires_func):
        try:
            # PSG(1) bat OL(3)[Grosse] et Lille(4)[Petite]. Score attendu = 1 (OL)
            if func(MATRICE, 1) == 1:
                print_badge("Expert Graphiste", "🏆")
                return True
            print("❌ Erreur : Le score d'influence n'est pas bon. Vérifie la condition >= 3.")
            return False
        except Exception as e:
            print(f"❌ Erreur d'exécution : {e}")
            return False

    def check_resultats_influence(self, R8, R9):
        if R8 == 1 and R9.upper().strip() == "PSG":
            print("🎉 BRAVO ! TP TERMINÉ !")
            return True
        print("❌ R8 ou R9 incorrects.")
        return False

# Instanciation
validate = ValidateGraph()
check_q1 = validate.check_q1
check_q2 = validate.check_q2
check_q3 = validate.check_q3
check_q4 = validate.check_q4
check_compter_victoires = validate.check_compter_victoires
check_trouver_meilleur_gagneur = validate.check_trouver_meilleur_gagneur
check_score_predictif_simple_func = validate.check_score_predictif_simple_func
check_resultats_sps = validate.check_resultats_sps
check_score_influence_func = validate.check_score_influence_func
check_resultats_influence = validate.check_resultats_influence