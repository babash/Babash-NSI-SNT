# La vérification automatique

*Les contrôles de l'onglet Actions, et le même contrôle sur ton ordinateur. Retour au [README](../README.md).*

Le fichier `.github/workflows/verifier.yml` lance trois contrôles, visibles dans l'onglet
**Actions** du dépôt (coche verte : tout va bien ; croix rouge : clique pour voir le détail) :

- **Données de la bibliothèque**, à chaque modification, sur toutes les branches, et à la
  demande : `scripts/valider_donnees.py --github` vérifie les fiches, la vitrine et les
  référentiels du dossier `donnees/` (voir [les données de la bibliothèque](BIBLIOTHEQUE.md)). Une erreur fait
  échouer le contrôle (croix rouge). Les avertissements et les informations sont dans le
  résumé du run, sans échec, et les erreurs et avertissements apparaissent aussi en
  annotations sur les fichiers concernés. Les six avertissements voulus (l'éditeur d'Alien
  Python, les TD 1 et 2 de POO, la licence de la fiche Python de SNT, deux sites en `http://` :
  voir [les données de la bibliothèque](BIBLIOTHEQUE.md)) y figurent donc à chaque run. Le thésaurus des notions est aussi
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
- **Site en ligne**, après chaque modification de `main` : le contrôle attend que GitHub Pages
  ait réellement mis en ligne ce commit (`scripts/attendre_deploiement.py`), puis télécharge
  les fichiers du site que l'envoi ajoute ou modifie, sur tous ses commits (par exemple la
  fusion d'une branche et le commit du README envoyés ensemble), et vérifie qu'ils sont
  identiques à ceux du dépôt. Les fichiers du site qui ne sont pas comparés (plus de 5 Mo, ou
  au-delà des 200 premiers) sont signalés dans le résumé. Ensuite, il affiche chaque rubrique
  dans Chrome et vérifie qu'aucune erreur n'apparaît et que le nombre de ressources affichées
  est celui de `ressources.js`. Il ouvre aussi chaque page déposée dans un dossier `fichiers/`
  (TD, fiches, diaporamas, applications) et vérifie qu'elle s'affiche avec un vrai contenu. Il
  vérifie enfin le lien « Code source sur GitHub » : l'accueil et chaque rubrique doivent l'avoir,
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
`python3 -m http.server 8000`, puis dans un autre terminal
`python3 .github/verifier-site.py http://localhost:8000`.

Avant chaque publication, le Gardien fait aussi ses propres contrôles : [GARDIEN.md](GARDIEN.md).
