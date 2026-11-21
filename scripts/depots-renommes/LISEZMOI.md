# Les dépôts renommés (T100)

Un fichier `<ancien nom>.json` par dépôt renommé : `{"ancien": …, "nouveau": …, "date": …}`.

- Il est ajouté dans le commit qui corrige les adresses de ce dépôt, pour que chaque renommage se publie seul.
- `scripts/valider_donnees.py` lit ces fichiers : une fiche ou la vitrine qui cite une ancienne adresse
  (`babash.github.io/<ancien>`, `github.com/babash/<ancien>`…, en toutes casses) est une **erreur**.
  Les notes datées d'une fiche (`notes`) gardent les adresses de leur époque.
- Il n'y a **aucun dépôt de redirection** (décision de l'enseignant du 21/11) : une ancienne adresse ne
  mène nulle part.
