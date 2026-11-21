#!/bin/sh
# Opération GHOST v1.1 - Babash - NSI Tani Malandi - code sous licence MIT, énoncés sous CC BY-SA 4.0
# À charger dans le terminal avec :  . ./init_hacker.sh

# --- CONFIGURATION ---
export BASE_DIR="/tmp/avalon_server"
export PROGRESS_FILE="/tmp/.progress"
export CHECK_SCRIPT="/tmp/check_logic.sh"

# --- 1. GÉNÉRATION DU MOTEUR DE VÉRIFICATION ---
cat << 'EOF' > "$CHECK_SCRIPT"
#!/bin/sh
PROGRESS_FILE="/tmp/.progress"
BASE_DIR="/tmp/avalon_server"

DATA=$(cat "$PROGRESS_FILE" 2>/dev/null || echo "1:0")
MISSION=$(echo $DATA | cut -d: -f1)
TRIES=$(echo $DATA | cut -d: -f2)

G='\033[1;32m'; R='\033[1;31m'; B='\033[1;34m'; Y='\033[1;33m'; NC='\033[0m'

msg_status() { printf "${B}[SYSTEM]${NC} $1\n"; }
msg_ok() { printf "${G}[SUCCESS]${NC} $1\n"; }
msg_err() { printf "${R}[ERROR]${NC} $1\n"; }
msg_hint() { printf "${Y}[INDICE NIV.$1]${NC} $2\n"; }

fail_mission() {
    NEW_TRIES=$((TRIES + 1))
    echo "$MISSION:$NEW_TRIES" > "$PROGRESS_FILE"
    msg_err "$1"
    printf "🎯 ${B}OBJECTIF :${NC} $2\n"
    if [ $MISSION -le 8 ]; then
        if [ $NEW_TRIES -eq 1 ]; then msg_hint "1" "$3"
        elif [ $NEW_TRIES -eq 2 ]; then msg_hint "2" "$4"
        else msg_hint "3 (SOLUTION)" "$5"; fi
    else
        msg_hint "BONUS" "Le QG vous laisse en autonomie. Consultez l'aide (--help) ou explorez."
    fi
}

case $MISSION in
    1) [ "$(pwd)" = "$BASE_DIR/donnees/SQL" ] && VALID=1 || VALID=0 ;;
    2) [ "$(pwd)" = "$BASE_DIR/.secret" ] && VALID=1 || VALID=0 ;;
    3) printf "${Y}Entrez le code d'accès trouvé dans pass.txt : ${NC}"; read ATTEMPT
       [ "$ATTEMPT" = "AVALON_2026" ] && VALID=1 || VALID=0 ;;
    4) [ -f "$BASE_DIR/donnees/backdoor/logs.txt" ] && VALID=1 || VALID=0 ;;
    5) [ -f "$BASE_DIR/donnees/backdoor/id_backup.txt" ] && VALID=1 || VALID=0 ;;
    6) [ -f "$BASE_DIR/donnees/backdoor/evidence.txt" ] && [ ! -f "$BASE_DIR/donnees/system_id" ] && VALID=1 || VALID=0 ;;
    7) [ "$(stat -c %a $BASE_DIR/donnees/backdoor/logs.txt 2>/dev/null)" = "600" ] && VALID=1 || VALID=0 ;;
    8) [ ! -d "$BASE_DIR/donnees/archives" ] && VALID=1 || VALID=0 ;;
    9) [ "$(pwd)" = "$BASE_DIR/donnees/SQL/archives/2024/temp" ] && VALID=1 || VALID=0 ;;
    10) [ -f "$BASE_DIR/lanceur_alerte.txt" ] && VALID=1 || VALID=0 ;;
esac

if [ "$VALID" = "1" ]; then
    msg_ok "Analyse confirmée. Transition vers la phase suivante."
    echo "$((MISSION + 1)):0" > "$PROGRESS_FILE"
else
    case $MISSION in
        1) fail_mission "Zone non atteinte." "Rejoignez le secteur de la base de données." "Utilisez l'outil de changement de répertoire." "Vous devez entrer dans 'donnees' puis 'SQL'." "cd $BASE_DIR/donnees/SQL" ;;
        2) fail_mission "Invisible." "Localisez et entrez dans l'espace caché du serveur." "Les dossiers commençant par un point sont masqués." "Utilisez l'option de listing pour tout voir (-a)." "cd $BASE_DIR/.secret" ;;
        3) fail_mission "Code erroné." "Récupérez le code dans pass.txt et fournissez-le au check." "Consultez le contenu du fichier pass.txt." "L'outil 'cat' affiche le contenu." "Le code est AVALON_2026" ;;
        4) fail_mission "Planque introuvable." "Créez votre dossier de transit et son journal." "Il faut un nouveau dossier 'backdoor' et un fichier vide 'logs.txt'." "Utilisez l'outil de création de dossier puis celui de création de fichier." "mkdir $BASE_DIR/donnees/backdoor && touch $BASE_DIR/donnees/backdoor/logs.txt" ;;
        5) fail_mission "Données non dupliquées." "Faites une copie de sécurité de system_id." "Utilisez l'outil de duplication." "Indiquez la source (system_id) et la cible (id_backup.txt)." "cp $BASE_DIR/donnees/system_id $BASE_DIR/donnees/backdoor/id_backup.txt" ;;
        6) fail_mission "Camouflage défectueux." "Faites disparaître l'original en changeant son nom." "L'outil de déplacement permet aussi de renommer." "Déplacez l'original vers votre planque avec son nouveau nom." "mv $BASE_DIR/donnees/system_id $BASE_DIR/donnees/backdoor/evidence.txt" ;;
        7) fail_mission "Permissions trop larges." "Verrouillez l'accès à vos logs." "Modifiez les droits (chmod)." "Le mode 600 réserve tout au propriétaire." "chmod 600 $BASE_DIR/donnees/backdoor/logs.txt" ;;
        8) fail_mission "Traces persistantes." "Effacez les dossiers inutiles." "Supprimez le dossier 'archives'." "L'outil de suppression de répertoire vide est requis." "rmdir $BASE_DIR/donnees/archives" ;;
    esac
fi

# AFFICHAGE DES MISSIONS
MISSION=$(cat "$PROGRESS_FILE" | cut -d: -f1)
printf "\n${B}--- [ ANALYSE DE MISSION : PHASE $MISSION ] ---${NC}\n"
case $MISSION in
    1) printf "Ghost, infiltrez le dossier SQL pour préparer l'injection. Tapez check pour valider\n" ;;
    2) printf "Facile ! Le QG détecte un dossier fantôme à la racine de 'avalon_server'. Trouvez le dossier caché et entrez dedans.\n" ;;
    3) printf "C'est le moment de voler les identifiants ! Un fichier 'pass.txt' se trouve ici. Il contient le code d'accès au serveur de fichiers.\n${Y}ACTION :${NC} Lisez son contenu et tapez 'check' pour saisir le code.\n" ;;
    4) printf "Bien joué ! Retournez dans 'donnees'. Il vous faut un dossier 'backdoor' et un fichier 'logs.txt' à l'intérieur pour travailler.\n" ;;
    5) printf "Extrayons les données critiques : dupliquez (faites une copie de) 'system_id' vers 'backdoor/id_backup.txt'.\n" ;;
    6) printf "Vite ! On est sous surveillance. Renommez l'original 'system_id' en 'evidence.txt' et cachez-le dans votre 'backdoor' pour que personne ne le trouve.\n" ;;
    7) printf "Sécurisez vos logs : modifiez les permissions de 'logs.txt' pour que vous soyez le SEUL à pouvoir le lire (Lecture/Écriture).\n" ;;
    8) printf "Le travail est presque fini. Supprimez le dossier vide 'archives' pour masquer votre passage.\n" ;;
    9) printf "\n${Y}BIEN JOUÉ GHOST. LE VOL EST TERMINÉ VOUS ÊTES UN AS... MAIS UNE NOTE ATTIRE VOTRE ATTENTION.${NC}\nAvalon semble détourner des fonds humanitaires. Votre conscience vous pousse à agir.\n${B}BONUS :${NC} Utilisez 'find' pour localiser le fichier 'rapport_fraude.txt' caché profondément dans le serveur, rendez-vous dans le dossier parent.\n" ;;
    10) printf "${B}BONUS LANCEUR D'ALERTE :${NC} Le fichier est complexe. Utilisez 'grep' pour extraire la ligne contenant le mot 'DETOURNEMENT' et enregistrez-la dans 'lanceur_alerte.txt', déplacez ensuite 'lanceur_alerte.txt' dans le dossier "/tmp/avalon_server".\n" ;;
    11) printf "${G}INCROYABLE. Vous avez exfiltré les preuves. Le monde saura la vérité sur Avalon.${NC}\n" ; rm "$PROGRESS_FILE" ;;
esac
printf "${B}------------------------------------------------${NC}\n"
EOF

chmod +x "$CHECK_SCRIPT"
alias check="$CHECK_SCRIPT"

# --- 2. INITIALISATION ---
if [ ! -d "$BASE_DIR" ]; then
    mkdir -p "$BASE_DIR/donnees/archives"
    mkdir -p "$BASE_DIR/donnees/SQL/archives/2024/temp"
    mkdir -p "$BASE_DIR/.secret"
    echo "AVALON_2026" > "$BASE_DIR/.secret/pass.txt"
    echo "PROJET_ALPHA: VALIDE\nDETOURNEMENT: 15.000.000$\nBENEFICIAIRE: INCONNU" > "$BASE_DIR/donnees/SQL/archives/2024/temp/rapport_fraude.txt"
    echo "AVALON-SRV-01" > "$BASE_DIR/donnees/system_id"
    echo "1:0" > "$PROGRESS_FILE"
fi

# --- 3. ACCUEIL ---
clear
printf "${G}   ______ _    _  ____   _____ _______ \n"
printf "  / ____| |  | |/ __ \ / ____|__   __|\n"
printf " | |  __| |__| | |  | | (___    | |   \n"
printf " | | |_ |  __  | |  | |\___ \   | |   \n"
printf " | |__| | |  | | |__| |____) |  | |   \n"
printf "  \______|_|  |_|\____/|_____/   |_|   \n${NC}"
printf "\nBienvenue Ghost. Analyse de la structure AVALON :\n"
tree "$BASE_DIR" 2>/dev/null || ls -R "$BASE_DIR"
printf "\nCommandes : ${Y}check${NC} (énoncé/validation), ${Y}tree${NC} (vue d'ensemble).\n"

cd "$BASE_DIR"
sh "$CHECK_SCRIPT"