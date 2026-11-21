#!/bin/sh
# Rejoue les dix missions de l'Opération GHOST avec les commandes attendues de la feuille,
# et fait valider chaque mission par le vrai « check » du script init_hacker.sh.
# Tout se passe dans un dossier jetable (mktemp -d, effacé à la fin) : les chemins /tmp/avalon_server,
# /tmp/.progress et /tmp/check_logic.sh du script sont remplacés par des chemins de ce dossier.
# La feuille, elle, écrit les vrais chemins (/tmp/avalon_server). Usage : sh verifier-missions.sh
ICI=$(cd "$(dirname "$0")" && pwd)
J=$(mktemp -d)
trap 'rm -rf "$J"' EXIT
sed -e "s#/tmp/avalon_server#$J/tmp/avalon_server#g" -e "s#/tmp/.progress#$J/tmp/.progress#g" \
    -e "s#/tmp/check_logic.sh#$J/tmp/check_logic.sh#g" -e 's#^clear$#:#' "$ICI/../init_hacker.sh" > "$J/init_hacker.sh"
mkdir -p "$J/tmp"
B="$J/tmp/avalon_server"
cd "$J" && . ./init_hacker.sh > "$J/accueil.txt" 2>&1
echo "après . ./init_hacker.sh, on est dans : ${PWD#$J}"
ok=0; ko=0
valider() { # mission, réponse au « read » éventuel
  r=$(echo "$2" | sh "$J/tmp/check_logic.sh" 2>&1)
  if echo "$r" | grep -q SUCCESS; then echo "mission $1 : validée par check"; ok=$((ok+1)); else echo "mission $1 : REFUSÉE"; echo "$r"; ko=$((ko+1)); fi
}
cd donnees/SQL; valider 1
ls -a ../.. | tr '\n' ' ' | sed 's/^/  ls -a ..\/.. : /'; echo
cd ../../.secret; valider 2
echo "  cat pass.txt : $(cat pass.txt)"; valider 3 "$(cat pass.txt)"
cd ../donnees; mkdir backdoor; touch backdoor/logs.txt; valider 4
cp system_id backdoor/id_backup.txt; valider 5
mv system_id backdoor/evidence.txt; valider 6
echo "  droits de logs.txt avant : $(stat -c %a backdoor/logs.txt)"
chmod 600 backdoor/logs.txt; valider 7
echo "  droits après chmod 600 : $(stat -c %A backdoor/logs.txt)"
rmdir archives; valider 8
echo "  find : $(find "$J/tmp" -name rapport_fraude.txt | sed "s#$J##")"
cd "$B/donnees/SQL/archives/2024/temp"; valider 9
grep "DETOURNEMENT" rapport_fraude.txt > lanceur_alerte.txt
echo "  lanceur_alerte.txt (dash) : $(cat lanceur_alerte.txt)"
mv lanceur_alerte.txt "$B/"; valider 10
# variantes en chemin absolu, sur un serveur neuf
rm -rf "$B" "$J/tmp/.progress"; cd "$J" && . ./init_hacker.sh > /dev/null 2>&1
cd "$B/donnees/SQL"; valider "1 (absolu)"
cd "$B/.secret"; valider "2 (absolu)"
echo "Bilan : $ok validée(s), $ko refusée(s)"
[ $ko -eq 0 ]
