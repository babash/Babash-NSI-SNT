# Commandes Linux, Tle NSI : sources et vérifications

Par Babash - NSI Tani Malandi (CC BY-SA 4.0).

**Forme** : celle des feuilles de première (`nsi-premiere/fichiers/commandes-linux-premiere/`), même moteur, mêmes
questions de base (G42) ; le contenu est resserré sur ce qui tombe au bac (G43). Les quatre feuilles sont écrites par
un même script, à partir d'une seule banque de questions (voir le LISEZMOI de première). Révision T141 (25/11/2026).

- `../../commandes-terminale.html` : feuille 1, les rappels de première (commandes de base, chemins, réorganiser, `rmdir`
  et `rm -r`, droits, `sudo chown`) (30 min, 21 questions).
- `../../commandes-terminale-2.html` : feuille 2, les processus (`ps -ef`, PID, PPID, l'arbre des processus, `kill`),
  le tube `|` avec `grep`, `ping` (30 min, 10 questions).
- `../../commandes-terminale.pdf` : les deux feuilles vierges, d'un seul tenant (`charte/imprimer-td.py`).
- `../../commandes-terminale-corrige.html` et `.pdf` : le corrigé, **fait par `faire-corrige.py`** (même script qu'en première).
- `verifier-commandes.py` : le même script qu'en première (il vérifie les quatre feuilles).

**Ce qui est gardé, et pourquoi** : chaque commande demandée apparaît dans au moins un sujet de l'écrit (2021 à 2026,
lus un par un le 25/11/2026) ou dans le TD type bac de l'enseignant (`../../../td-os-processus-type-bac/`) : `cd` et les
chemins, `ls`, `ls -l`, `cat`, `man` et `--help`, `mkdir`, `cp`, `mv`, `rm` et `rm -r`, `rmdir`, `chmod`, `chown` et `sudo`
(TD type bac, et la méthode `chown` du sujet Métropole septembre 2025), `ps`, `kill`, le tube et `grep` (TD type bac),
`ping` (Nouvelle-Calédonie 2022, et TD type bac). Retirés : `history`, `find`, `df -h`, `ip addr`, `top`, le joker `*`,
`unzip`, `passwd`, `help`, `clear`, les questions sur le pourcentage de processeur et sur la zone d'échange.
