# Contribuer : les règles du travail sur GitHub

*Ces règles valent pour tout ce qui arrive dans ce dépôt : le travail de l'enseignant, propriétaire du site, et celui de l'équipe d'agents Claude qui l'entretient avec lui ([docs/AGENTS.md](docs/AGENTS.md)). Elles reprennent, pour qui les lit sans être un agent, les règles communes de l'équipe, écrites dans `CLAUDE.md`. Retour au [README](README.md).*

Une question, une idée, un lien cassé : ouvre une [issue](https://github.com/babash/Babash-NSI-SNT/issues). Pour proposer une modification, dis-le d'abord dans une issue.

## 1. Une branche par tâche

- Chaque tâche a **sa propre branche**, qui part de `main` à jour. On ne travaille pas directement sur `main`, sauf l'enseignant, pour les modifications qu'il fait depuis GitHub (§ 3).
- Le nom de la branche : un préfixe, le numéro de la tâche, puis quelques mots. Par exemple : `archi/t02-format-donnees`.
- Avant de commencer, et avant d'envoyer sa branche : récupérer toutes les branches, puis repartir du dernier `main` s'il a avancé.

  ```sh
  git fetch origin '+refs/heads/*:refs/remotes/origin/*'
  git rebase origin/main
  ```

  Un simple `git fetch origin` ne met pas `origin/main` à jour dans les copies de travail des agents : d'où la forme complète.
- **Envoyer sa branche avant de s'arrêter** : une copie de travail peut être effacée.

Les préfixes, selon le rôle :

| Préfixe | Pour |
|---|---|
| `biblio/` | les listes de ressources, les fiches de la bibliothèque, les fichiers déposés (Bibliothécaire) |
| `archi/` | le fonctionnement du site, ses pages, ses scripts et sa vérification automatique (Architecte) |
| `design/` | la charte graphique et les styles (Designer) |
| `atelier/` | une ressource en cours de création, dans ce dépôt ou dans celui d'une application (Atelier) |
| `gardien/` | le README, la documentation, la licence et les outils de contrôle (Gardien) |
| `orga/` | les règles de l'équipe (chef d'orchestre) |

## 2. Les commits

- Le message donne le numéro de la tâche, le rôle, puis ce qui change, en français : `[T02][archi] Format des données : schéma et référentiels`.
- Les commits des agents ont pour auteur `Claude`, avec l'adresse `noreply@anthropic.com` :
  `git config user.name Claude` et `git config user.email noreply@anthropic.com`.

## 3. Qui publie sur `main`

- **Le Gardien** est le seul à fusionner une branche dans `main`. Il la contrôle d'abord (§ 6), la fusionne sans avance rapide (`git merge --no-ff`), vérifie ensuite le site en ligne, et note la publication au journal des publications.
- **L'enseignant**, propriétaire du dépôt, peut aussi modifier `main` directement depuis GitHub, avec les boutons **Modifier la liste** et **Déposer un fichier** en bas de chaque rubrique ([docs/LISTES.md](docs/LISTES.md)). Plus tard, il le fera aussi depuis l'espace d'administration du site.
- **On publie dès que c'est sûr** (consigne de l'enseignant du 10 novembre 2026). Une branche conforme part tout de suite. Un point d'écriture mineur (une coquille, une apostrophe, un masculin générique oublié) ne bloque pas : il est corrigé ensuite, dans une branche de suite.
- **Un changement structurel attend l'accord de l'enseignant** : le format des données, les référentiels, les adresses, les rubriques ou les thèmes, la charte graphique, une nouvelle partie du site, et tout ce qui touche aux données d'élèves.
- **La structure du site suit les textes officiels** : les programmes de SNT et de NSI de 2019, et la circulaire n° 2018-108 pour la rubrique Professeur principal, qui garde ses thèmes actuels (décision du 7 novembre 2026). Tout autre écart se soumet à l'enseignant.

Le Gardien rend l'un de ces verdicts : **publié** ; **publié avec suites** (la branche est sûre, mais des points d'écriture mineurs sont à reprendre dans une branche de suite) ; **à corriger** (avec la liste précise des problèmes) ; **à soumettre** (un changement structurel, que l'enseignant tranche).

## 4. Jamais d'envoi forcé

- **Jamais** de `git push --force` sur `main`, et jamais de réécriture de son historique.
- Sur sa propre branche, après un `rebase`, seulement `git push --force-with-lease` : il refuse d'écraser ce qui aurait été envoyé entre-temps.

## 5. Supprimer les branches publiées

- Une branche publiée, c'est-à-dire entièrement contenue dans `main`, ou devenue inutile, se supprime, après avoir vérifié qu'il n'y reste rien à récupérer.
- On ne supprime jamais la branche de quelqu'un d'autre. Seule exception : le Gardien peut supprimer une branche déjà fusionnée ou obsolète, avec l'accord du chef d'orchestre (décision du 7 novembre 2026).
- Aujourd'hui, les sessions des agents ne peuvent pas supprimer une branche sur GitHub : l'enseignant le fait, dans l'onglet **Branches** du dépôt, d'après la liste que tient le Gardien.

## 6. Les contrôles avant publication

Avant de publier une branche, le Gardien vérifie :

1. **La conformité** : au cahier des charges, aux décisions de l'enseignant (la plus récente l'emporte) et aux règles de conception des ressources, en particulier celles des TD et des éditeurs de code ([docs/AGENTS.md](docs/AGENTS.md)).
2. **Les données** : un format valide, des identifiants uniques, des références qui existent, aucun lien principal vers une page GitHub (§ 12) ; tant que les listes `ressources.js` servent, aucune erreur affichée.
3. **La visibilité** : un document caché n'apparaît ni au public ni aux élèves (sans objet tant que les listes `ressources.js` servent). Pour l'instant, on ne cache rien : l'enseignant réglera lui-même la visibilité, à la main (consigne du 12 novembre 2026).
4. **Les données sensibles** (§ 7), cherchées dans tout ce que la branche ajoute.
5. **Les liens et les fichiers** : chaque lien interne mène à un fichier qui existe ; les liens externes sont testés par la vérification automatique ; le lien « Code source sur GitHub » (§ 12).
6. **Le rendu** : à 320, 768 et 1440 px de large, en clair et en obscur, sans erreur JavaScript ni défilement horizontal ; l'impression A4 des documents touchés, sans débordement.
7. **L'accessibilité** : un contraste d'au moins 4,5:1 pour le texte, et une navigation complète au clavier.
8. **Les chiffres** : le nombre de ressources affichées, avant et après, correspond à ce qu'annonce la branche.
9. **Le README** : à jour.

Un contrôle rouge bloque la publication, même s'il semble mineur. Après la publication, le Gardien vérifie que la vérification automatique est au vert pour le nouveau commit, que les pages répondent et que les chiffres en ligne sont ceux du dépôt. Le détail : [docs/GARDIEN.md](docs/GARDIEN.md) et [docs/VERIFICATION.md](docs/VERIFICATION.md).

## 7. Aucune donnée sensible

Le dépôt est **public**. Il ne contient donc jamais :

- de mot de passe, ni d'identifiant (par exemple ceux de démonstration de CyberCase) ;
- de clé secrète ;
- de nom d'élève.

Les clés Supabase :

- la clé « anon » ou « publishable » est **publique par conception** : elle peut figurer dans une page, comme dans les fichiers `config.js` d'Alien Python et de Court-circuit ; les tables sont verrouillées, et les pages ne passent que par des fonctions de la base ([docs/SUPABASE.md](docs/SUPABASE.md)) ;
- une clé « service_role » ou « secret », **jamais** : ni dans le dépôt, ni dans une page, ni dans un message.

Le Gardien cherche ces motifs dans tout ce qu'ajoute une branche (`.github/gardien/sensibles.py`), et le script de validation des données signale tout ce qui ressemble à un mot de passe, un identifiant ou une clé secrète.

## 8. Les données d'élèves

- **Toute ressource qui collecte des données d'élèves le signale** : sur sa fiche (le champ `donnees_eleves`), dans la ligne des propriétés de son README et dans sa section « Données des élèves ».
- **Toute nouvelle collecte est soumise à l'enseignant** avant d'être publiée.
- **Par défaut** : un pseudo ou un prénom, au choix de l'élève, jamais de nom de famille. Exceptions décidées : Alien Python et SNT 1er jour.
- **Les bases** : aucune modification sans que l'enseignant ait vu le SQL exact. Les agents n'en lisent que les métadonnées (les tables, les colonnes, les droits, le nombre de lignes), jamais une valeur d'une table d'élèves, et ne font aucun essai sur une table d'élèves de la base en ligne : les essais d'écriture se font sur une reproduction locale, avec des données inventées ([docs/SUPABASE.md](docs/SUPABASE.md)).
- Les mini-sites des TD restent sans compte ni envoi de données.

## 9. Les licences et les crédits en chaîne

- Les **documents pédagogiques** de l'enseignant sont sous licence CC BY-SA 4.0, le **code** de ses applications sous licence MIT, et l'auteur affiché est « Babash - NSI Tani Malandi ». Pour ce dépôt : la section [Licence](README.md#licence) du README.
- **Une ressource externe** est créditée à son site d'origine.
- **Une ressource reprise et modifiée crédite toute la chaîne** de ses auteurs et autrices. Par exemple, CyberCase : d'Etienne Clave sur exomorphisme.fr, d'après une idée de Marion Dufour et le moteur SQL Noir de Hristo Bogoev.
- **Ce qui vient d'ailleurs garde sa licence et sa notice** : bibliothèques, polices, exercices repris ([docs/REUTILISER.md](docs/REUTILISER.md#ce-que-tu-dois-garder)).
- **La licence de l'original décide** : une ressource sans licence, ou dont la licence interdit la modification, ne se reprend pas sans l'accord de son auteur ou de son autrice ; le cas se soumet à l'enseignant.

## 10. Le langage inclusif

- Un **français clair**, et le **langage inclusif complet chaque fois que c'est pertinent**, dans les pages du site comme dans les documents pour les élèves : des formulations épicènes (« les élèves », « chaque collègue »), la double flexion (« ils et elles »), la féminisation des fonctions (« la professeure principale ») et le point médian (« enseignant·e·s », « fort·e·s »).
- C'est la décision de l'enseignant du 7 novembre 2026, prise en connaissance de la circulaire du 5 mai 2021 : **un point médian n'est jamais une faute à corriger**.
- Une seule graphie : le point médian `·`, avant la marque du féminin, puis avant celle du pluriel (`enseignant·e·s`) ; ni parenthèses, ni barre oblique, ni point bas.
- Les collègues sont **tutoyé·e·s** dans les README, comme dans le pied de page du site.

## 11. Les caractères spéciaux

- Certains outils d'écriture de fichiers remplacent une séquence comme `\uXXXX` par le caractère lui-même : le code d'un caractère invisible devient alors un vrai caractère invisible, par exemple un caractère qui inverse le sens du texte.
- Un caractère invisible ou spécial s'écrit donc **par son code** : `chr(0x…)` en Python, `String.fromCharCode(0x…)` en JavaScript, `&#x…;` en HTML, jamais par `\u` suivi de son code.
- Pour relire une branche : `python3 -I .github/gardien/caracteres.py --diff origin/main...origin/<branche>`. L'outil signale les caractères invisibles et les points qui imitent le point médian ; le vrai point médian, lui, est permis.

## 12. Le lien « Code source sur GitHub »

- **Le lien principal** d'une ressource mène directement à elle (la page, la fiche, le PDF), jamais à une page GitHub.
- **Le dépôt apparaît toujours, en lien secondaire** (décision de l'enseignant du 10 novembre 2026) :
  - chaque page publiée (ce site, les applications, les pages en ligne des TD) porte en pied de page un lien « Code source sur GitHub » vers son dépôt, à côté de l'auteur et de la licence ;
  - chaque ressource qui a un dépôt le donne en annexe, sous le nom « Code source » ;
  - pour une ressource externe, on ne modifie pas son site, mais sa fiche donne son dépôt s'il est public.
- Un lien « Code source » qui manque ne bloque pas une publication : il est ajouté dans une branche de suite. Pour ce site, la vérification automatique échoue si l'accueil ou une rubrique perd son lien. Le détail : [la règle des liens](docs/LISTES.md#la-règle-des-liens).

## 13. Le style et les dessins

- Une ressource suit le style actuel du site.
- Les dessins sont originaux : aucun personnage, aucun logo ni aucune illustration d'Android: Netrunner.
