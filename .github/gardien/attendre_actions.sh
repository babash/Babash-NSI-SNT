#!/usr/bin/env bash
# Après une publication : attend la fin des workflows GitHub Actions du commit
# (déploiement GitHub Pages et « Vérifier le site »), puis affiche leurs jobs et les lignes
# utiles des journaux (liens en échec et seconde passe, mise en ligne du commit, chiffres du
# site en ligne).
# Usage : bash .github/gardien/attendre_actions.sh SHA [DELAI_MAX_SECONDES=900] [PAS=45]
# Attention : l'API veut le SHA complet ; un SHA court est complété par git si possible.
# Depuis T12, le job « Site en ligne » attend le déploiement de ce commit précis
# (scripts/attendre_deploiement.py) : plus besoin de le relancer après le déploiement (I1).
# Pour un commit publié avant T12, la relance reste : gh api -X POST
# repos/babash/Babash-NSI-SNT/actions/jobs/ID/rerun.
set -u
sha="$1"; max="${2:-900}"; pas="${3:-45}"
if [ "${#sha}" -lt 40 ]; then sha=$(git rev-parse "$sha" 2>/dev/null || echo "$sha"); fi
depot="repos/babash/Babash-NSI-SNT"
debut=$(date +%s)
while :; do
  lignes=$(gh api "$depot/actions/runs?head_sha=$sha&per_page=20" \
    --jq '.workflow_runs[] | [.id, .name, .run_attempt, .status, (.conclusion // "-"), .updated_at] | @tsv' 2>&1)
  ecoule=$(( $(date +%s) - debut ))
  echo "== $(date -u +%H:%M:%S) (+${ecoule}s)"
  echo "$lignes"
  if [ -n "$lignes" ] && ! echo "$lignes" | grep -qE $'\t(queued|in_progress|waiting|pending|requested)\t'; then
    break
  fi
  if [ "$ecoule" -ge "$max" ]; then echo "DÉLAI DÉPASSÉ"; exit 2; fi
  sleep "$pas"
done
echo "TERMINÉ"
for run in $(echo "$lignes" | cut -f1); do
  gh api "$depot/actions/runs/$run/jobs" --jq '.jobs[] | "\(.id)\t\(.name)\t\(.conclusion)\t\(.started_at) -> \(.completed_at)"' |
  while IFS=$'\t' read -r job nom conclusion quand; do
    echo "-- job $job « $nom » : $conclusion ($quand)"
    case "$nom" in
      "Liens des ressources"|"Liens en échec, seconde passe"|"Site en ligne")
        gh api "$depot/actions/jobs/$job/logs" 2>/dev/null | sed -E 's/^[0-9TZ:.-]+ //' |
          grep -E '^\| .*(Total|Successful|Errors|Excluded|Timeouts)|\[ERROR\]|Tous les liens répondent|lien\(s\) en échec|Liens vérifiés|En échec à la première|Revenus|Morts|Lien mort|commit attendu|le commit est en ligne|remplacé|fichier\(s\) servi|identique|différent|La version en ligne|ressources affichées|^accueil|^Total|Pages déposées|correctement|^ - |::error|##\[(error|warning|notice)\]' |
          grep -v -e 'echo ' -e '\[36;1m' ;;
    esac
  done
done
if echo "$lignes" | grep -q $'\tfailure\t'; then exit 1; fi
exit 0
