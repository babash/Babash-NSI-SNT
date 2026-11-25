# Commandes Linux, Tle NSI : sources et vérifications

Par Babash - NSI Tani Malandi (CC BY-SA 4.0).

**Refonte T141 (25/11/2026)** : deux feuilles d'une heure, jumelles de celles de première
(`nsi-premiere/fichiers/commandes-linux-premiere/`) : même arborescence d'exemple, mêmes mots, même encadré
« À retenir », un exemple résolu avant chaque demande nouvelle, aucun coup de pouce, la correction après deux essais.
La progression : en première, on reconnaît une commande (« Que fait… ? ») ; en terminale, on retrouve celles de première
(« Quelle commande… ? ») et on reconnaît les nouvelles, puis les processus (programme de terminale).

- `../../commandes-terminale.html` : feuille 1, rappels de première (chemins, commandes, droits) et les commandes qui observent la machine.
- `../../commandes-terminale-2.html` : feuille 2, les processus (`ps`, PID, PPID, `kill`), le joker `*` et le tube `|`.
- `../../commandes-terminale.pdf` : les deux feuilles vierges, d'un seul tenant (`charte/imprimer-td.py`).
- `../../commandes-terminale-corrige.html` et `.pdf` : le corrigé, **fait par `faire-corrige.py`** (même script qu'en première).
- `verifier.py` : chaque réponse acceptée et chaque erreur fréquente lancée pour de vrai (bash, et BusyBox ash avec
  `BUSYBOX=…`) ; `kill` est essayé sur un vrai processus en arrière-plan (le PID de la page est remplacé par le vrai) ;
  `ps -ef | grep marees` sur un vrai `python3 marees.py` ; l'en-tête de `ps -eo` comparé à celui de la page.
