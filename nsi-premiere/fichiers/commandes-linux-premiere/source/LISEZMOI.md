# Commandes Linux, 1re NSI : sources

Par Babash - NSI Tani Malandi, CC BY-SA 4.0.

**Forme** : celle de la feuille d'origine de l'enseignant (tableaux « Que fait la commande… ? » par thème,
l'arborescence de référence, les chemins, la réorganisation et son dessin, le mémo), en deux feuilles de 30 min,
jumelles des feuilles de terminale (`nsi-terminale/fichiers/architecture-os/commandes-terminale*.html`) : même
arborescence, mêmes mots, mêmes questions de base. En tête, un encadré « À retenir » ; avant chaque demande
nouvelle, un exemple résolu ; en ligne, la page dit si c'est juste ; après un essai faux prévu, elle pose une
question (« tu es dans quel dossier ? »), jamais un bout de réponse ; la correction vient après deux essais.
Papier et écran portent les mêmes numéros (chaque ligne d'un tableau est une question). Révision T141 (25/11/2026).

**Les quatre feuilles (1re et Tle) sont écrites par un même script**, hors du dépôt, à partir d'une seule banque
de questions : toute modification de l'arborescence, du vocabulaire ou d'une question commune se reporte dans les
quatre. Les pages restent du HTML ordinaire, modifiable à la main ; dans ce cas, relancer les deux scripts ci-dessous.

- `../commandes-premiere-eleve.html` : feuille 1, les commandes de base, les chemins, réorganiser (30 min, 20 questions).
- `../commandes-premiere-eleve-2.html` : feuille 2, chercher avec `grep`, les droits (`ls -l`, `chmod`, `chown`, `sudo`) (30 min, 12 questions).
- `../commandes-premiere-eleve.pdf` : les deux feuilles vierges, d'un seul tenant (`charte/imprimer-td.py`), chaque feuille sur sa page.
- `../commandes-premiere-corrige.html` et `.pdf` : le corrigé de l'enseignant·e, **fait par `faire-corrige.py`** à partir des feuilles :
  `python3 -I faire-corrige.py ../commandes-premiere-corrige.html "Commandes Linux (première)" ../commandes-premiere-eleve.html ../commandes-premiere-eleve-2.html`
- `verifier-commandes.py` (même script qu'en terminale) : chaque réponse acceptée et chaque erreur prévue des quatre feuilles
  est lancée pour de vrai dans un dossier jetable où l'arborescence est recréée (bash ; avec `BUSYBOX=…/busybox`, aussi
  BusyBox ash, le shell de JSLinux) ; les sorties affichées (`cat`, `grep`, `ls -l`, les refus de `chown` et de `rmdir`),
  les exemples résolus, `kill` sur un vrai processus et `ps -ef | grep` sur un vrai calcul sont rejoués.
- Une règle de style dans l'en-tête des pages (`t141-sortie`, `td-insecable`) : une commande ne se coupe qu'à une espace,
  et une sortie de terminal tient en entier sur un téléphone. À retirer quand le moteur commun le fera (demandé au Designer).
- Pour s'entraîner à l'écran : Opération GHOST (`../operation-ghost/`), Opération MIRAGE, et le jeu Terminus (luffah.xyz).
