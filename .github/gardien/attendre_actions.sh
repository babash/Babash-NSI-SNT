#!/usr/bin/env bash
# Après une publication : attend la fin des workflows GitHub Actions du commit
# (déploiement GitHub Pages et « Vérifier le site »), puis affiche leurs jobs et les lignes
# utiles des journaux (résumé des liens, chiffres du site en ligne).
# Usage : bash .github/gardien/attendre_actions.sh SHA [DELAI_MAX_SECONDES=900] [PAS=45]
# Attention : l'API veut le SHA complet ; un SHA court est complété par git si possible.
# Rappel : le job « Site en ligne » n'attend que les changements de reglages.js et */ressources.js.
# Si le commit n'en change aucun, il peut tester l'ancienne version : le relancer après le
# déploiement (gh api -X POST repos/babash/Babash-NSI-SNT/actions/jobs/ID/rerun).
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
      "Liens des ressources"|"Site en ligne")
        gh api "$depot/actions/jobs/$job/logs" 2>/dev/null | sed -E 's/^[0-9TZ:.-]+ //' |
          grep -E '^\| .*(Total|Successful|Errors|Excluded|Timeouts)|\[ERROR\]|ressources affichées|^accueil|^Total|Pages déposées|correctement|^ - |::error' | grep -v 'echo ' ;;
    esac
  done
done
if echo "$lignes" | grep -q $'\tfailure\t'; then exit 1; fi
exit 0
