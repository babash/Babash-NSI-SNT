# Commandes Linux, 1re NSI : sources

Par Babash - NSI Tani Malandi, CC BY-SA 4.0.

**Refonte T141 (25/11/2026)** : le TD a deux feuilles d'une heure, jumelles de celles de terminale
(`nsi-terminale/fichiers/architecture-os/commandes-terminale*.html`) : même arborescence d'exemple
(`/home/eleve`, `/home/prof`, le groupe `nsi`), mêmes mots, même encadré « À retenir » en tête, un exemple
résolu avant chaque demande nouvelle, aucun coup de pouce ; en ligne, la page dit seulement si c'est juste,
et la correction (avec les erreurs fréquentes) vient après deux essais. Toute modification de l'arborescence
ou du vocabulaire se reporte dans les deux niveaux.

- `../commandes-premiere-eleve.html` : feuille 1, les commandes de base, les chemins, réorganiser.
- `../commandes-premiere-eleve-2.html` : feuille 2, chercher avec `grep`, les droits (`ls -l`, `chmod`, `sudo`, `chown`).
- `../commandes-premiere-eleve.pdf` : les deux feuilles vierges, d'un seul tenant (`charte/imprimer-td.py`), chaque feuille sur sa page.
- `../commandes-premiere-corrige.html` et `.pdf` : le corrigé de l'enseignant·e, **fait par `faire-corrige.py`** à partir des feuilles
  (numéros du papier, réponses acceptées en ligne, erreurs fréquentes) : ne pas l'écrire à la main.
  `python3 -I faire-corrige.py ../commandes-premiere-corrige.html "Commandes Linux (première)" ../commandes-premiere-eleve.html ../commandes-premiere-eleve-2.html`
- `verifier-commandes.py` : chaque réponse acceptée et chaque erreur fréquente des deux feuilles est lancée pour de vrai
  dans un dossier jetable où l'arborescence est recréée (bash ; avec `BUSYBOX=…/busybox`, aussi BusyBox ash, le shell
  de JSLinux) ; les sorties affichées (`ls`, `grep`, `ls -l`, le refus de `chown` sans root) et les exemples résolus sont rejoués.
