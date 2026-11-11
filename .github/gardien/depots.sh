#!/usr/bin/env bash
# Les autres dépôts de l'enseignant, vus par l'API GitHub : publication et branches (Gardien).
#
# Usage (depuis la copie du dépôt ; il faut l'outil gh, connecté) :
#   bash .github/gardien/depots.sh attendre DELAI DEPOT=SHA [DEPOT=SHA …]
#       attend la fin des workflows de ces commits (toutes les 30 s, DELAI secondes au plus),
#       puis affiche chaque run : identifiant, nom, état, conclusion, heures. Pour FichesNSI, suit
#       aussi la publication sur gh-pages qui suit « Deploy Production ». SHA complet ou court.
#   bash .github/gardien/depots.sh etat DEPOT [DEPOT …]
#       le commit de main, la licence reconnue par GitHub, Pages ou non, et le dernier
#       déploiement github-pages (son commit et son heure).
#   bash .github/gardien/depots.sh contenues DOSSIER_DU_CLONE BRANCHE [BRANCHE …]
#       chaque branche distante est-elle entièrement contenue dans origin/main de ce clone ?
#       (avant de proposer sa suppression ; faire d'abord un fetch complet du clone)
# Le propriétaire des dépôts est babash, ou la valeur de la variable GARDIEN_PROPRIETAIRE.
# Code de sortie : 0 (aussi pour --help) ; 1 pour un usage incorrect ou, avec « attendre », si le délai est dépassé.
set -u
proprio="${GARDIEN_PROPRIETAIRE:-babash}"
env_pages="github""-pages"

usage() { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-1}"; }

attendre() {
  local max="$1"; shift
  local debut; debut=$(date +%s)
  while :; do
    local encours=0 sortie=""
    for paire in "$@"; do
      local depot="${paire%%=*}" sha="${paire#*=}" lignes
      lignes=$(gh api "repos/$proprio/$depot/actions/runs?head_sha=$sha&per_page=20" \
        --jq '.workflow_runs[] | [.id, .name, .status, (.conclusion // "-"), .created_at, .updated_at] | @tsv' 2>&1)
      if [ -z "$(echo "$lignes" | tr -d '[:space:]')" ] && [ "${#sha}" -lt 40 ]; then
        # l'API veut le SHA complet : on le cherche
        local complet; complet=$(gh api "repos/$proprio/$depot/commits/$sha" --jq '.sha' 2>/dev/null)
        [ -n "$complet" ] && lignes=$(gh api "repos/$proprio/$depot/actions/runs?head_sha=$complet&per_page=20" \
          --jq '.workflow_runs[] | [.id, .name, .status, (.conclusion // "-"), .created_at, .updated_at] | @tsv' 2>&1)
      fi
      if [ "$depot" = "FichesNSI" ]; then
        local depuis; depuis=$(date -u -d @"$debut" +%Y-%m-%dT%H:%M:%SZ)
        lignes="$lignes"$'\n'$(gh api "repos/$proprio/$depot/actions/runs?branch=gh-pages&per_page=1" \
          --jq '.workflow_runs[] | select(.created_at > "'"$depuis"'") | [.id, .name + " (gh-pages " + .head_sha[0:7] + ")", .status, (.conclusion // "-"), .created_at, .updated_at] | @tsv' 2>&1)
      fi
      sortie="$sortie"$'\n'"== $depot $sha"$'\n'"$lignes"
      if [ -z "$(echo "$lignes" | tr -d '[:space:]')" ] || echo "$lignes" | grep -qE $'\t(queued|in_progress|waiting|pending|requested)\t'; then
        encours=1
      fi
    done
    local ecoule=$(( $(date +%s) - debut ))
    if [ "$encours" = 0 ]; then echo "$sortie"; echo "TERMINÉ (+${ecoule} s)"; return 0; fi
    if [ "$ecoule" -ge "$max" ]; then
      echo "$sortie"; echo "DÉLAI DÉPASSÉ (+${ecoule} s) : un dépôt n'a pas de run, ou un run n'est pas fini"; return 1
    fi
    sleep 30
  done
}

etat() {
  for r in "$@"; do
    local sha lic dep
    sha=$(gh api "repos/$proprio/$r/commits/main" --jq '.sha[0:7]' 2>&1)
    lic=$(gh api "repos/$proprio/$r" --jq '(.license.spdx_id // "aucune") + " ; Pages : " + (if .has_pages then "oui" else "non" end)' 2>&1)
    dep=$(gh api "repos/$proprio/$r/deployments?environment=$env_pages&per_page=1" --jq '.[0] | if . then .sha[0:7] + " (" + .created_at + ")" else "aucun" end' 2>&1)
    printf "%-24s main %s ; licence %s ; dernier déploiement %s\n" "$r" "$sha" "$lic" "$dep"
  done
}

contenues() {
  local clone="$1"; shift
  for b in "$@"; do
    if ! git -C "$clone" rev-parse -q --verify "origin/$b" > /dev/null; then
      printf "%-34s absente\n" "$b"
    elif git -C "$clone" merge-base --is-ancestor "origin/$b" origin/main; then
      printf "%-34s contenue dans main (%s)\n" "$b" "$(git -C "$clone" rev-parse --short "origin/$b")"
    else
      printf "%-34s NON CONTENUE : %s commit(s) propres, tête %s, %s\n" "$b" \
        "$(git -C "$clone" rev-list --count "origin/main..origin/$b")" "$(git -C "$clone" rev-parse --short "origin/$b")" \
        "$(git -C "$clone" log -1 --format='%ad %s' --date=format:'%d/%m %H:%M' "origin/$b")"
    fi
  done
}

case "${1:-}" in -h|--help) usage 0 ;; esac
[ $# -ge 2 ] || usage
commande="$1"; shift
case "$commande" in
  attendre) [ $# -ge 2 ] || usage; attendre "$@" ;;
  etat) etat "$@" ;;
  contenues) [ $# -ge 2 ] || usage; contenues "$@" ;;
  *) usage ;;
esac
