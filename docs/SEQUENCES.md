# Les séquences

**Statut : format proposé le 25/11/2026 (tâche T153), à valider par l'enseignant. Les trois séquences du dépôt sont des
exemples (`"exemple": true`, statut « brouillon ») : elles ne s'affichent pas sur le site tant qu'elles ne sont pas publiées.**

La demande de l'enseignant (25/11/2026, 10:19) : « Commence aussi à grouper les ressources en séquences de manière à ce que
tout ne soit pas dispersé. Typiquement quizz-cours, fiches, TDs, TP/activités, TD bac, contrôle pour les terminales. »
Ses décisions de 10:50 : une étape « Réviser » à part, juste avant le contrôle ; le rang dans l'année et les prérequis entre
séquences sont des données.

## Ce qu'est une séquence

Une séquence regroupe les ressources d'une même notion, **dans l'ordre où la classe les rencontre**. En terminale :

| Étape | Ce qu'on y met |
|---|---|
| Cours-quiz | l'introduction en 15 minutes (QuizzNSI) |
| Fiches | la fiche de synthèse ou de révision, le cours écrit |
| TD | les feuilles d'exercices, une séance ou moins chacune |
| TP et activités | programmer ou manipuler : TP, activité débranchée, jeu |
| TD type bac | les exercices au format du bac |
| Réviser | quiz de révision, QCM Pronote |
| Contrôle | le sujet, son corrigé si la fiche le montre |

La liste des étapes est **fermée** et l'ordre est **une donnée par niveau** (`donnees/referentiels/sequences.json`,
« parcours ») : la première suit la terminale (le TD type bac n'y sert qu'en fin d'année) ; la seconde a ses propres étapes
(activités et jeux, quiz, cours et fiches, TD et TP, contrôle). Changer l'ordre ou ajouter une étape à un niveau, c'est changer
ce fichier, pas le code.

## Où sont les fichiers

```
donnees/
  sequences/<id>.json            une séquence par fichier (comme une fiche par ressource)
  referentiels/sequences.json    les étapes, leur ordre par niveau, les ressources externes mises en avant par niveau
  schema/sequence.schema.json    le format exact
assets/sequences.js              l'affichage (pages de niveau, page d'une séquence, fiche d'une ressource)
scripts/tests/test_sequences.py  les tests du validateur et de la construction
```

## Une séquence, en bref

```json
{
  "id": "tle-piles-files",
  "niveau": "terminale",
  "enseignement": "nsi",
  "titre": "Interface et implémentation ; listes, piles et files",
  "objectif": "Choisir entre une pile et une file pour un problème, et s'en servir par leur interface.",
  "rang": 30,
  "prerequis": ["tle-programmation-objet"],
  "programme": ["nsi-tle-2019.structures-de-donnees.listes-piles-files"],
  "notions": ["donnees.pile", "donnees.file"],
  "statut": "publiee",
  "etapes": [
    { "type": "cours-quiz", "ressources": ["quizznsi-piles-files"] },
    { "type": "td", "ressources": [
      { "ressource": "dm-flash-terminale", "secondaire": true,
        "document": "nsi-terminale/fichiers/dm-flash-terminale/dm-pile/index.html",
        "note": "le DM sur les piles et les files" }
    ] },
    { "type": "tp-activites", "ressources": [], "complements": ["file-deux-piles-codex"] },
    { "type": "td-bac", "ressources": ["td-bac-piles-files"] },
    { "type": "revisions", "ressources": ["quizznsi-revision-piles-files"] },
    { "type": "controle", "ressources": ["controle-notions-piles-files"] }
  ]
}
```

- **Titre** : fait des libellés des référentiels (thème ou contenu du programme, notion du thésaurus). **Jamais de numéro**
  de chapitre ni de séquence (critique C3) : le validateur refuse « Chapitre 3 », « Séquence 2 », « 2. Piles… ».
- **Rang** : la place dans l'année parmi les séquences du même niveau (10, 20, 30… pour pouvoir en insérer une). Il range
  les séquences ; il ne s'affiche jamais.
- **Prérequis** (facultatif) : les séquences à voir avant. Affiché sobrement : « À voir avant : … ».
- **Programme** : le premier thème ou contenu désigne la page de niveau où la séquence s'affiche.
- **Étapes** : seulement celles qui sont prévues pour cette séquence, dans l'ordre du parcours du niveau. Une étape absente
  n'est pas prévue ; une étape présente **sans ressource** est « à venir ».
- **Une place** : l'identifiant d'une fiche, ou un objet `{ "ressource", "secondaire", "document", "note" }`.
  Jamais une copie des champs de la fiche.
  - `secondaire: true` : la ressource est rangée principalement dans une autre séquence (un contrôle commun à deux
    séquences, une révision commune). Une ressource a **une seule séquence principale** ; ailleurs elle porte « Aussi ».
  - `document` : le document à ouvrir à cette étape, par son `url` ou son `fichier` tel qu'écrit dans la fiche (une feuille
    d'un recueil de DM). La même ressource peut alors revenir à une autre étape avec un autre document (le TD et le TP d'une
    même fiche).
  - `note` : une précision courte, affichée sous le titre.
- **Ressources externes** (règle de l'enseignant du 25/11, 10:21) : une ressource d'une autre origine que « ma création » va
  dans `complements`, montrés au second plan sous « Ailleurs sur le web », sauf si elle est une exception de son niveau
  (`mises_en_avant` du référentiel : Terminus et CyberCase en terminale, Compute-it en seconde, Algorea et Terminus en
  première). L'exception est une donnée **par niveau**, pas un champ de la fiche.
- **Statut** : « brouillon » (pas montré, sauf avec `?brouillons` dans l'adresse, pour relire) ou « publiee ».

## Ce que voit la classe

- **Page de niveau** (`nsi-terminale/`) : deux vues, « Par séquence » et « Par thème » (la liste d'avant, inchangée). La vue
  par séquence est l'entrée par défaut dès que la rubrique a une séquence publiée ; `reglages.js` peut garder la vue par thème
  (`vue_par_defaut: "themes"`). L'adresse garde la vue (`?vue=themes`). La recherche et le sommaire marchent dans les deux vues.
- **Page d'une séquence** (`nsi-terminale/?sequence=tle-piles-files`) : les étapes, puis « Pour la classe » : l'adresse, son
  QR code, « Copier le lien » et « Imprimer la séquence » (une page A4 avec le QR code). L'adresse donnée n'a jamais
  `?brouillons` : pour un brouillon, la page le dit (« ce QR code mènera à cette page quand la séquence sera publiée »).
- **Fiche d'une ressource** (`bibliotheque/?r=…`) : « Dans la séquence … (Terminale), étape … », avec la ressource d'avant et
  celle d'après.
- **Visibilité** : les séquences sont faites pour la classe. Elles ne montrent que les documents visibles **des élèves et de
  l'extérieur** ; une ressource sans document visible des élèves n'y apparaît pas. Ce qui est caché aux élèves le reste.
- **Étape vide** : « À venir. », en italique, sans lien et avec un repère en pointillés : jamais de lien mort, et la classe voit
  tout le parcours (elle sait qu'un TP viendra).
- **Sous chaque ressource** : le lien principal direct (le titre), au plus deux autres documents (énoncé, PDF, corrigé…), et
  « En savoir plus » vers la fiche complète, où sont tous les documents (code source, espace de l'enseignant·e…).

## Vérifier

```
python3 scripts/valider_donnees.py                       les séquences avec le reste des données
python3 -I -B scripts/tests/test_sequences.py            les tests (37 cas et la construction)
node scripts/tests/test_sequences_page.js                le rendu, sans navigateur (9 cas)
python3 scripts/construire_bibliotheque.py               les séquences dans bibliotheque.json
```

Le validateur refuse (ERREUR) : schéma non respecté, identifiant différent du nom du fichier, niveau, enseignement,
programme, notion ou fiche inconnus, numéro dans le titre, deux séquences au même rang d'un niveau, étape inconnue, absente du
parcours du niveau, en double ou mal placée, document visé qui n'est pas dans la fiche, même ressource deux fois sans document
distinct, deux séquences principales pour une ressource, prérequis inconnu, d'un niveau plus avancé ou en boucle. Il avertit
(ATTENTION) : titre sans libellé des référentiels, programme d'un autre niveau, ressource sans le niveau de la séquence,
obsolète, d'un type inattendu à l'étape, externe au premier rang, de l'enseignant·e en complément, secondaire partout,
prérequis vu après, séquence sans aucune ressource. Il informe (INFO) : exemple, brouillon, ressource cachée à l'extérieur ou
aux élèves.

`.github/verifier-site.py` (contrôle en ligne) affiche les rubriques dans leur vue « Par thème » (`?vue=themes`) pour les
compter, et vérifie la page de chaque séquence publiée.

## Qui modifie quoi

| Fichier | Rôle |
|---|---|
| `donnees/sequences/` (le contenu des séquences) | Bibliothécaire |
| `donnees/referentiels/sequences.json`, `donnees/schema/sequence.schema.json` | Architecte, après validation de l'enseignant |
| `assets/sequences.js`, `scripts/` | Architecte |
| le style des séquences (aujourd'hui provisoire, dans `assets/sequences.js`) | Designer, à reprendre dans `assets/style.css` |
