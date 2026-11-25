# Opération GHOST : sources

Par Babash - NSI Tani Malandi ; fiches sous CC BY-SA 4.0, script `init_hacker.sh` sous licence MIT. Terminal : JSLinux de Fabrice Bellard.

- La fiche élève `../fiche-eleve-ghost.html` est désormais une page HTML auto-corrective (T125, style « Signal pirate ») : elle reste la feuille qui accompagne le TP, et, après chaque mission, l'élève y écrit sa commande, qui se corrige en ligne. Elle est la référence ; `../fiche-eleve-ghost.pdf` en est l'impression vierge (`charte/imprimer-td.py`).
- `../fiche-prof-ghost.html` (corrigé de l'enseignant·e) est inchangé ; `../init_hacker.sh` a changé d'une ligne (T141, ci-dessous).
- `verifier-missions.sh` : rejoue les dix missions avec les commandes attendues de la feuille, dans un dossier jetable (`mktemp -d`), et fait valider chacune par le vrai `check` du script (lancé par `dash` ; JSLinux Alpine utilise `ash` de BusyBox).
- T141 (25/11/2026) : dans `../init_hacker.sh`, `rapport_fraude.txt` est écrit par `printf` au lieu de `echo` : le `echo` de BusyBox (le shell de JSLinux) n'interprète pas `\n`, le fichier tenait sur une seule ligne et `grep DETOURNEMENT` (mission 10) rendait tout le fichier au lieu de la seule ligne cherchée.
