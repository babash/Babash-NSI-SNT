#!/usr/bin/env bash
# Installer pdftotext (paquet poppler-utils) sur une machine GitHub Actions (T110).
#
# Pourquoi ce script : l'image ubuntu-26.04 du 16/11/2026 (version 20261116) n'a plus aucune
# source de paquets Ubuntu, seulement celle de Microsoft. « apt-get install poppler-utils » y
# échoue (« Unable to locate package »), alors qu'il marchait sur l'image du 11/11. GitHub
# déploie les images peu à peu : selon la machine reçue, la publication passait ou échouait.
#
# Ce que fait le script, dans l'ordre, en s'arrêtant dès que pdftotext est là :
#   1. rien, si pdftotext est déjà installé ;
#   2. apt-get update puis install, avec les sources de la machine (trois tentatives réseau) ;
#   3. sinon, ajoute les sources officielles d'Ubuntu pour la version de la machine
#      (archive.ubuntu.com et security.ubuntu.com, clé de l'archive déjà présente) et recommence ;
#   4. vérifie que pdftotext fonctionne ; sinon, erreur claire et code 1 : la publication
#      s'arrête plutôt que de publier une recherche sans le texte des PDF.
# Le paquet installé est le même qu'avant : le texte extrait des PDF ne change pas.
#
# Usage : bash scripts/installer_pdftotext.sh   (sudo sans mot de passe, comme sur GitHub Actions)

set -u

ok() { command -v pdftotext >/dev/null 2>&1 && pdftotext -v >/dev/null 2>&1; }
apt_opts=(-q -o Acquire::Retries=3 -o DPkg::Lock::Timeout=120)

installer() {
  sudo apt-get "${apt_opts[@]}" update && \
    sudo DEBIAN_FRONTEND=noninteractive apt-get "${apt_opts[@]}" install -y --no-install-recommends poppler-utils
}

if ok; then
  echo "pdftotext déjà installé : $(command -v pdftotext)"
  exit 0
fi

echo "::group::Installation de poppler-utils avec les sources de la machine"
installer
echo "::endgroup::"

if ! ok; then
  echo "::group::Sources de paquets de la machine"
  ls -l /etc/apt/sources.list /etc/apt/sources.list.d/ 2>&1
  echo "::endgroup::"

  . /etc/os-release
  code="${VERSION_CODENAME:-${UBUNTU_CODENAME:-}}"
  cle=/usr/share/keyrings/ubuntu-archive-keyring.gpg
  if [ -z "$code" ] || [ ! -f "$cle" ]; then
    echo "::error title=pdftotext::poppler-utils introuvable, et impossible d'ajouter les sources d'Ubuntu (version : « $code », clé : $cle)."
    exit 1
  fi
  echo "::warning title=pdftotext::poppler-utils introuvable avec les sources de la machine : ajout des sources officielles d'Ubuntu ($code)."
  sudo tee /etc/apt/sources.list.d/ubuntu-t110.sources >/dev/null <<EOF
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: $code $code-updates
Components: main universe
Signed-By: $cle

Types: deb
URIs: http://security.ubuntu.com/ubuntu
Suites: $code-security
Components: main universe
Signed-By: $cle
EOF
  echo "::group::Installation de poppler-utils avec les sources d'Ubuntu"
  installer
  echo "::endgroup::"
fi

if ok; then
  echo "pdftotext installé : $(pdftotext -v 2>&1 | head -n 1)"
  exit 0
fi
echo "::error title=pdftotext::Installation de poppler-utils impossible : la recherche dans le texte des PDF ne peut pas être construite. Relancer le workflow ; si l'erreur revient, voir les sources de paquets ci-dessus."
exit 1
