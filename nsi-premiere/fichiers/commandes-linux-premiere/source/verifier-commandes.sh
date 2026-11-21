#!/bin/bash
# Vérifie, par exécution réelle, les réponses attendues de la feuille « Commandes Linux » (1re NSI).
# Tout se passe dans un dossier jetable (mktemp), effacé à la fin : la racine « / » de l'énoncé
# y est simulée par $R. Usage : bash verifier-commandes.sh
set -u
R=$(mktemp -d)
trap 'rm -rf "$R"' EXIT
ok=0; ko=0
verifie() { # libellé, obtenu, attendu
  if [ "$2" = "$3" ]; then echo "juste : $1 -> $2"; ok=$((ok+1)); else echo "FAUX  : $1 -> obtenu « $2 », attendu « $3 »"; ko=$((ko+1)); fi
}
arbo() {
  rm -rf "$R"/*; mkdir -p "$R/bin" "$R/home/prof/examens" "$R/home/eleve/devoirs/nsi" "$R/home/eleve/projets"
  echo "Inaya;15" > "$R/home/prof/notes.csv"
}

# 1.1 chemin absolu de nsi
arbo; cd "$R/home/eleve/devoirs/nsi"
verifie "1.1 pwd" "${PWD#$R}" "/home/eleve/devoirs/nsi"

# 1.2 copie en chemins relatifs, depuis nsi
for dest in "../../projets/" "../../projets"; do
  arbo; cd "$R/home/eleve/devoirs/nsi"
  cp ../../../prof/notes.csv $dest
  verifie "1.2 cp ../../../prof/notes.csv $dest" "$(ls "$R/home/eleve/projets")" "notes.csv"
done

# 1.3 se placer dans examens (relatif ou absolu), puis touch exam1.txt
for chemin in "../../../prof/examens" "../../../prof/examens/" "$R/home/prof/examens" "$R/home/eleve/../prof/examens"; do
  arbo; cd "$R/home/eleve/devoirs/nsi"
  cd "$chemin" && touch exam1.txt
  verifie "1.3 cd ${chemin#$R} ; touch exam1.txt" "$(ls "$R/home/prof/examens")" "exam1.txt"
done

# 1.4 ls ../.. depuis nsi
arbo; cd "$R/home/eleve/devoirs/nsi"
verifie "1.4 ls ../.." "$(ls ../.. | tr '\n' ' ' | sed 's/ $//')" "devoirs projets"

# 2.1 et 2.2 : réorganisation depuis /home/eleve
arbo; cd "$R/home/eleve"
mkdir archives; cd devoirs; mv nsi ../archives/
verifie "2.1 ls ../archives" "$(ls ../archives)" "nsi"
verifie "2.2 contenu de /home/eleve" "$(ls "$R/home/eleve" | tr '\n' ' ' | sed 's/ $//')" "archives devoirs projets"
verifie "2.2 contenu de devoirs (vide)" "$(ls "$R/home/eleve/devoirs" | wc -l)" "0"
verifie "2.2 contenu de archives" "$(ls "$R/home/eleve/archives")" "nsi"

# 3.1 grep depuis projets (L.txt y est créé pour l'essai)
arbo; cd "$R/home/eleve/projets"
printf 'login: eleve\npassword: ********\nfin\n' > L.txt
verifie "3.1 grep password L.txt" "$(grep password L.txt)" "password: ********"
verifie "3.1 grep \"password\" L.txt" "$(grep "password" L.txt)" "password: ********"

# 3.2 chown : changer de propriétaire demande les droits de root. Sans root, la commande échoue ;
# l'utilisateur « directeur » n'existe pas ici : on vérifie la syntaxe avec l'utilisateur « nobody ».
arbo; cd "$R/home/prof"
if [ "$(id -u)" = "0" ]; then
  chown nobody notes.csv
  verifie "3.2 (root) chown nobody notes.csv" "$(stat -c %U notes.csv)" "nobody"
else
  chown nobody notes.csv 2>/dev/null && r=reussi || r=refuse
  verifie "3.2 (sans root) chown refusé" "$r" "refuse"
fi
verifie "3.2 utilisateur directeur absent (essai)" "$(id directeur >/dev/null 2>&1 && echo present || echo absent)" "absent"
chown directeur notes.csv 2>&1 | sed 's/^/      message réel : /'

echo "Bilan : $ok juste(s), $ko faux"
[ $ko -eq 0 ]
