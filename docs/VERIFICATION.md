# La publication et la vérification automatique

*La mise en ligne par « Publier le site », les contrôles de l'onglet Actions, et le même contrôle sur ton ordinateur. Retour au [README](../README.md).*

## La mise en ligne

Depuis le 17 novembre 2026, le site est mis en ligne par le workflow **« Publier le site »**
(`.github/workflows/publier.yml`), et la source de GitHub Pages est « GitHub Actions »
(**Settings → Pages** ; voir [Réutiliser le site](REUTILISER.md#activer-github-pages-une-seule-fois)).
À chaque envoi, sur toutes les branches, et à la demande (**Run workflow**), son job
« Construire le site » :

1. valide les données de la bibliothèque (`scripts/valider_donnees.py`) ;
2. construit les fichiers de la bibliothèque à partir des fiches (`scripts/construire_bibliotheque.py`,
   voir [l'onglet Bibliothèque](BIBLIOTHEQUE.md#longlet-bibliothèque)) ;
3. prépare le site à publier : tout le dépôt, sauf les fichiers et dossiers cachés (`.github/`,
   `.gitignore`…), avec les fichiers construits.

Puis, sur `main` seulement, le job « Mettre en ligne » le publie (environnement `github-pages`),
en quelques minutes au total. Sur une autre branche, ce job est sauté : c'est normal, la branche
est seulement essayée. Une erreur dans les données arrête la construction : rien n'est mis en
ligne, et le site garde sa version précédente, intacte, jusqu'à la correction. Si la source de
GitHub Pages est « Deploy from a branch », le workflow le signale par un avertissement et ne met
rien en ligne : GitHub publie alors la branche telle quelle, sans les fichiers de la
bibliothèque, et l'onglet Bibliothèque affiche une erreur.

Les fichiers construits (`donnees/bibliotheque.json`, `donnees/bibliotheque-complete.json` et
`donnees/bibliotheque-textes.json`) ne sont **jamais commités** : `.gitignore` les écarte. Les
fiches restent la seule source, et le site en ligne a toujours des fichiers construits à partir
de la version publiée.

## Les contrôles

Le fichier `.github/workflows/verifier.yml` lance trois contrôles, visibles dans l'onglet
**Actions** du dépôt (coche verte : tout va bien ; croix rouge : clique pour voir le détail) :

- **Données de la bibliothèque**, à chaque modification, sur toutes les branches, et à la
  demande : `scripts/valider_donnees.py --github` vérifie les fiches, la vitrine et les
  référentiels du dossier `donnees/` (voir [les données de la bibliothèque](BIBLIOTHEQUE.md)). Une erreur fait
  échouer le contrôle (croix rouge). Le même job essaie ensuite la construction de la
  bibliothèque, comme « Publier le site », dans un dossier temporaire, et lance les tests du
  thésaurus et de la recherche (`scripts/tests/test_notions.py`, `scripts/tests/test_recherche.js`) :
  une branche qui casserait la publication est ainsi repérée avant d'arriver sur `main`. Les avertissements et les informations sont dans le
  résumé du run, sans échec, et les erreurs et avertissements apparaissent aussi en
  annotations sur les fichiers concernés. Les quinze avertissements connus (l'éditeur d'Alien
  Python, les TD 1 et 2 de POO, la licence de la fiche Python de SNT, deux sites en `http://`,
  les critères de l'éditeur de neuf notebooks Capytale de l'enseignant : voir
  [les données de la bibliothèque](BIBLIOTHEQUE.md)) y figurent donc à chaque run. Le thésaurus des notions est aussi
  comparé à celui de `main` (pour un envoi sur `main`, à celui d'avant l'envoi) : une notion
  publiée qui a disparu fait échouer le contrôle, car un identifiant publié est définitif. Une
  branche en retard sur `main` y échoue aussi quand `main` a reçu des notions depuis (elles
  manquent à la branche) : la rebaser sur `main` le règle.
- **Liens des ressources**, à chaque modification et chaque lundi : tous les liens des
  fichiers `ressources.js` sont testés. Un lien en échec est revérifié par un second job,
  « Liens en échec, seconde passe », donc sur une autre machine de GitHub, une à deux minutes
  plus tard : il n'est déclaré mort que s'il échoue aux deux passes, ce qui écarte les pannes
  passagères. Un lien qui ne répond pas à temps aux deux passes compte aussi comme mort.
  Le résumé liste les liens morts, avec le fichier et la ligne, et les pannes passagères.
  Ne sont pas testés : les pages qui demandent une connexion (Capytale, claude.ai) et
  algorea.org, qui refuse les robots. Les sites qui répondent « accès refusé » (403) ou
  « trop de requêtes » (429) aux robots sont comptés comme valides.
- **Site en ligne**, après chaque modification de `main` : le contrôle attend que « Publier le
  site » ait réellement mis en ligne ce commit (`scripts/attendre_deploiement.py`), puis télécharge
  les fichiers du site que l'envoi ajoute ou modifie, sur tous ses commits (par exemple la
  fusion d'une branche et le commit du README envoyés ensemble), et vérifie qu'ils sont
  identiques à ceux du dépôt. Les fichiers du site qui ne sont pas comparés (plus de 5 Mo, ou
  au-delà des 200 premiers) sont signalés dans le résumé. Ensuite, il affiche chaque rubrique
  dans Chrome et vérifie qu'aucune erreur n'apparaît et que le nombre de ressources affichées
  est celui de `ressources.js`. Il vérifie aussi **la bibliothèque** : `donnees/bibliotheque.json`
  se lit en ligne et contient exactement les fiches visibles de l'extérieur du commit publié ; la
  page `bibliotheque/` en affiche autant, sans erreur (dans le journal du job, une ligne comme
  « bibliothèque 114 ressources affichées / 114 fiches visibles de l'extérieur ») ; une recherche trouve une ressource
  par un mot de son titre ; la fiche complète de trois ressources s'ouvre (`?r=identifiant`). Les
  fichiers construits ne sont pas dans le dépôt : c'est ce contrôle qui les vérifie, et non la
  comparaison des fichiers. Il ouvre aussi chaque page déposée dans un dossier `fichiers/`
  et citée par une liste (TD, fiches, diaporamas, applications), et vérifie qu'elle s'affiche avec
  un vrai contenu ; les pages citées seulement par les fiches de la bibliothèque, comme celles
  des activités Capytale, ne sont pas encore ouvertes par ce contrôle (le Gardien les vérifie avant
  chaque publication). Il
  vérifie enfin le lien « Code source sur GitHub » : l'accueil, chaque rubrique et la bibliothèque doivent l'avoir,
  vers le dépôt du réglage `depot`, sinon le contrôle échoue ; une page déposée qui ne l'a pas
  encore est seulement signalée dans le résumé, sans échec (la liste `CODE_SOURCE_EXCEPTIONS` de
  `.github/verifier-site.py` peut en dispenser une page, avec sa raison ; elle est vide). Le
  résumé donne l'heure de chaque étape. Si un commit plus récent est mis en ligne entre-temps,
  c'est son propre contrôle qui vérifie le site, en ne comparant que les fichiers de son envoi ;
  pour comparer aussi ceux de l'envoi précédent, relance le contrôle à la main avec le champ
  « depuis ». Lancé à la main (**Run workflow** dans l'onglet Actions), ce contrôle vérifie le
  site tel que `main` l'a mis en ligne ; la comparaison porte sur le dernier commit de `main`,
  ou sur tous les commits qui suivent celui que tu indiques dans le champ « depuis ».

Le même contrôle des pages se lance sur ton ordinateur, depuis le dossier du site :
`python3 scripts/construire_bibliotheque.py` (les fichiers de la bibliothèque, que `.gitignore`
écarte), `python3 -m http.server 8000`, puis dans un autre terminal
`python3 .github/verifier-site.py http://localhost:8000`.

Avant chaque publication, le Gardien fait aussi ses propres contrôles : [GARDIEN.md](GARDIEN.md).
