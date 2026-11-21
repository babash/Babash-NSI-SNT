# Commandes Linux, 1re NSI : sources

Par Babash - NSI Tani Malandi, CC BY-SA 4.0.

- La page HTML auto-corrective `../commandes-premiere-eleve.html` est désormais la référence (T125, style « Signal pirate ») : elle reprend le recto (le rôle de chaque commande) et le verso (les exercices) de l'ancienne fiche. Son impression vierge est `../commandes-premiere-eleve.pdf` (`charte/imprimer-td.py`).
- `../commandes-premiere-corrige.html` : l'ancien corrigé, gardé tel quel.
- `verifier-commandes.sh` : rejoue chaque réponse attendue de la feuille par une exécution réelle de `bash`, dans un dossier jetable (`mktemp -d`, effacé à la fin) où l'arborescence de l'énoncé est recréée.
