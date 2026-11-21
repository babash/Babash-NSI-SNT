# Opération GHOST : sources

Par Babash - NSI Tani Malandi ; fiches sous CC BY-SA 4.0, script `init_hacker.sh` sous licence MIT. Terminal : JSLinux de Fabrice Bellard.

- La fiche élève `../fiche-eleve-ghost.html` est désormais une page HTML auto-corrective (T125, style « Signal pirate ») : elle reste la feuille qui accompagne le TP, et, après chaque mission, l'élève y écrit sa commande, qui se corrige en ligne. Elle est la référence ; `../fiche-eleve-ghost.pdf` en est l'impression vierge (`charte/imprimer-td.py`).
- `../fiche-prof-ghost.html` (corrigé de l'enseignant·e) et `../init_hacker.sh` sont inchangés.
- `verifier-missions.sh` : rejoue les dix missions avec les commandes attendues de la feuille, dans un dossier jetable (`mktemp -d`), et fait valider chacune par le vrai `check` du script (lancé par `dash` ; JSLinux Alpine utilise `ash` de BusyBox).
