# Les données de la bibliothèque (dossier `donnees/`)

*Le format des fiches de la bibliothèque des ressources, et leur validation. Retour au [README](../README.md).*

Le site va réunir toutes les ressources dans une bibliothèque unique. Son format a été validé
par l'enseignant le 7 novembre 2026, mais **le site ne le lit pas encore** : les pages
continuent d'utiliser les listes `ressources.js` ([LISTES.md](LISTES.md)).

```
donnees/
  README.md                     le format en détail, pour l'enseignant et pour les agents
  ressources/<id>.json          une fiche par ressource (7 pour l'instant : 6 d'exemple et Court-circuit)
  vitrine.exemple.json          un exemple de mise en avant pour la partie extérieure
  referentiels/                 l'arbre des programmes, les listes de valeurs, les compétences Pix
  schema/                       la description exacte du format (JSON Schema)
  correspondance-etiquettes.md  comment les listes actuelles seront converties
scripts/valider_donnees.py      la validation des données
```

Une fiche décrit une ressource et ses documents (activité, version PDF, corrigé, code
source…). Chaque document a deux réglages de visibilité, pour l'extérieur et pour les élèves.
Pour l'instant, on ne cache rien : tous les documents sont visibles de l'extérieur comme des
élèves, et l'enseignant réglera lui-même la visibilité, à la main (consigne du 12 novembre 2026).
La fiche signale aussi si la ressource collecte des données d'élèves (`donnees_eleves`).
Elle crédite ses auteurs et autrices (`auteurs`, `credits`) ; une ressource reprise et
modifiée crédite toute la chaîne. Par exemple, la fiche de CyberCase cite Etienne Clave
(exomorphisme.fr, lycée de Sada), l'idée de Marion Dufour, le moteur SQL Noir de Hristo
Bogoev, puis la reprise par Babash - NSI Tani Malandi.

Quand c'est utile, la fiche note aussi :

- les **compétences Pix** d'une ressource de SNT (`competences_pix`), choisies parmi les 16 de
  `referentiels/competences-pix.json`. Les intitulés affichés sont ceux de la plateforme Pix,
  que voient les élèves. Quand le décret de 2019 (cadre de référence des compétences
  numériques) les écrit autrement, son texte est gardé dans `libelle_decret` : c'est le cas
  de « Création de contenu » (« de contenus » dans le décret) et de « Construire un
  environnement numérique » (« Évoluer dans un environnement numérique ») ;
- pour une ressource où l'élève écrit du code : l'usage `editeur-de-code`, qui servira de
  filtre dans la bibliothèque, et le champ `editeur_code`. Ce champ note les cinq critères de
  la règle 20, chacun par `true` ou `false` : `coloration` (coloration syntaxique),
  `indentation` (la touche Tab indente), `guides_indentation` (les blocs visibles, sur le
  modèle de Lagon Arena), `autocompletion` (contextualisée) et `erreurs_expliquees` (l'erreur
  telle quelle, puis traduite ou expliquée en français), avec une `remarque` facultative ;
- pour un TD, le champ facultatif `td_en_ligne` (règle 19) : la page en ligne est-elle
  `responsive` (du téléphone au grand écran) et `auto_corrective` (un formulaire corrigé dans
  le navigateur) ? La version PDF et la page HTML, elles, se lisent dans les documents ;
- les critères de réussite (`criteres_reussite`), au cas par cas.

Pour une création de l'enseignant, un critère à `false`, ou un éditeur de code dont les
critères ne sont pas notés, donne un avertissement du script de validation ; pour une
ressource externe, qui ne se modifie pas, c'est une simple information. Deux fiches d'exemple
ont un avertissement voulu, car ce sont des écarts réels : l'éditeur d'Alien Python, une zone
de texte simple, ne remplit aucun des cinq critères, et la page du TD 1 de POO n'est ni
responsive ni auto-corrective. Ces écarts seront repris lors de la revue des ressources
publiées ; d'ici là, la validation avec `--strict` (ci-dessous) échoue sur ces deux
avertissements.

Pour valider les données, depuis le dossier du site : `python3 scripts/valider_donnees.py`
(Python 3 seul, rien à installer ; avec `--strict`, les avertissements bloquent aussi). Chaque
message donne le fichier et le champ. Le script signale comme erreur, entre autres, un lien
principal vers GitHub, un identifiant en double, une référence inexistante, un document sans
réglage de visibilité, et tout ce qui ressemble à un mot de passe, un identifiant ou une clé
secrète.

Le format en détail, pour l'enseignant et pour les agents : [`donnees/README.md`](../donnees/README.md).
