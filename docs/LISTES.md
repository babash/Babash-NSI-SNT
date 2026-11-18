# Les rubriques, les ressources et les réglages

*Ce que montrent les rubriques, comment ajouter et ranger une ressource, les réglages du site, et que faire si la page affiche une erreur. Retour au [README](../README.md).*

Le site a cinq rubriques : SNT, NSI Première, NSI Terminale, Professeur principal et Autres.
Depuis le 17 novembre 2026, elles montrent la **vitrine** (`donnees/vitrine.json`) : pour chaque
rubrique, ses sections et, dans chacune, les ressources mises en avant, dans l'ordre. Chaque
ressource vient de sa **fiche** (`donnees/ressources/<identifiant>.json`, voir
[les données de la bibliothèque](BIBLIOTHEQUE.md)). La vitrine et les fiches se modifient dans
l'[espace administrateur](ADMIN.md). Les anciennes listes `ressources.js` des rubriques restent
dans le dépôt, le temps de comparer, mais **ne sont plus lues** : les modifier ne change plus rien
sur le site.

## Ce que montre une rubrique

- **Ses sections**, dans l'ordre de la vitrine. Une section suit un thème du texte officiel (son
  titre est celui du programme) ou porte un titre libre (« Préparer le bac », « Sites
  ressources »…). Le sommaire de gauche et l'adresse (`…/nsi-premiere/#types-construits`) en
  viennent.
- **La ligne « Au programme »** sous une section : les contenus du programme pour un thème
  officiel (en SNT et en NSI). Pour une section libre, ce sont les titres de ses sous-sections qui
  n'ont pas encore de ressource, comme les trois lignes de « Orientation » en Professeur principal.
  Un contenu qui a des ressources devient un lien vers son groupe ; les autres restent en
  pointillés, ce qui montre d'un coup d'œil ce qui reste à couvrir.
- **Chaque ressource** :
  - son titre, qui ouvre le document principal de la fiche ;
  - son accroche, puis « **En savoir plus** », qui ouvre sa fiche complète dans la bibliothèque
    (décision de l'enseignant du 17 novembre 2026) ;
  - les autres documents de la fiche, en liens annexes (corrigé, version PDF, code source…) ;
  - ses étiquettes, tirées de la fiche (En ligne, À imprimer, Débranché, Connexion ENT, Jeu, Python,
    SQL, Pour aller plus loin, À adapter), et en tête l'étiquette que la vitrine lui donne
    « À la une », comme « Ressource du mois » ;
  - son site d'origine, ou « Sur ce site » pour un fichier déposé.
- Une ressource dont tous les documents sont cachés pour l'extérieur n'apparaît pas.

La recherche de la page d'accueil fouille les titres, textes, étiquettes et thèmes de toutes les
rubriques ; on peut la partager : `…/Babash-NSI-SNT/?q=débranché`. Chercher « ressource du mois »
retrouve la ressource mise à la une. Pour chercher plus loin (synonymes, notions, texte des
documents, filtres) : l'onglet Bibliothèque.

## La règle des liens

Le lien principal d'une ressource mène **directement** à la ressource
(la page de l'activité, la fiche, le PDF), jamais à un dépôt GitHub ou à un fichier affiché
par GitHub. Le dépôt, lui, doit toujours être indiqué, en lien secondaire (décision de
l'enseignant du 10 novembre 2026) : la fiche d'une ressource qui a un dépôt le donne dans un
document de rôle « code source », et chaque page publiée (ce site, les applications, les pages en
ligne des TD) porte en pied de page un lien « Code source sur GitHub » vers son dépôt, à côté de
l'auteur et de la licence. Pour une ressource externe, qu'on ne modifie pas, sa fiche donne son
dépôt s'il est public. Le contrôle du site en ligne vérifie le lien des pages de ce site (voir
[la vérification automatique](VERIFICATION.md)).
Quand une activité n'a pas de page en ligne, ses fichiers sont déposés dans le dossier
`fichiers` d'une rubrique (c'est le cas de `nsi-terminale/fichiers/os-humain/`).

---

## Ajouter une ressource en ligne

1. **Sa fiche** : un fichier `donnees/ressources/<identifiant>.json`, au format décrit dans
   [`donnees/README.md`](../donnees/README.md). Pour l'instant, on la crée sur GitHub
   (**Add file → Create new file**) ; l'espace administrateur le fera par un formulaire à
   l'étape suivante. Le contrôle « Données de la bibliothèque » la vérifie à chaque envoi.
2. **Sa place** : dans l'[espace administrateur](ADMIN.md), « Onglets du site », la rubrique, la
   section, puis « Choisir les ressources ». Sans place dans la vitrine, la ressource n'apparaît
   que dans la bibliothèque.
3. **Enregistrer** : le site se met à jour en quelques minutes ; le workflow « Publier le site »
   valide les données, construit la bibliothèque, puis met le site en ligne. S'il échoue, le site
   garde sa version précédente (voir [la mise en ligne](VERIFICATION.md#la-mise-en-ligne)).

## Ajouter un PDF (ou n'importe quel fichier)

1. Sur GitHub, ouvre le dossier `fichiers` de la rubrique (par exemple `snt/fichiers/`), puis
   **Add file → Upload files**. Valide avec **Commit changes**.
2. Cite-le dans la fiche, par un document qui donne son chemin depuis la racine du site :
   `"fichier": "snt/fichiers/tp-graphes.pdf"`. Le contrôle des données vérifie qu'il existe.

Le site affiche « Sur ce site » sous la ressource et ouvre le fichier dans un nouvel onglet.
Les fichiers que le navigateur ne sait pas afficher (`.py`, `.odt`, `.docx`, `.zip`…)
sont téléchargés quand on clique dessus.

> Conseil : des noms de fichiers sans espaces ni accents (`tp-graphes.pdf` plutôt que `TP Graphes é.pdf`).

## Une ressource avec plusieurs liens (sujet, corrigé, version en ligne…)

Une fiche a autant de documents qu'il faut, chacun avec son rôle (énoncé, corrigé, version PDF,
code source…), son titre et sa visibilité pour l'extérieur et pour les élèves. Le document
principal ouvre le titre de la ressource ; les autres s'affichent en liens annexes, dans l'ordre
de la fiche. L'espace administrateur les range et règle leur visibilité.

---

## Organiser une rubrique

Dans l'[espace administrateur](ADMIN.md), « Onglets du site » : l'ordre et le titre des sections,
leurs sous-sections, les ressources de chacune, dans l'ordre (boutons, glisser-déposer ou cases à
cocher), et l'aperçu avant d'enregistrer. Une section sans ressource affiche « Rien ici pour
l'instant » : on peut la laisser en attendant.

### Ranger selon le programme officiel

Une section qui suit un thème du programme (`donnees/referentiels/programmes.json`) en prend le
titre et les contenus ; ses sous-sections sont des contenus du thème. La référence du texte
officiel s'affiche sous la présentation de la rubrique.

## Ajouter une rubrique

1. Crée un dossier, par exemple `mathematiques`, avec une copie de `autres/index.html`.
2. Ajoute la rubrique à la vitrine (`donnees/vitrine.json`, voir
   [`donnees/README.md`](../donnees/README.md)), et son nom à la liste `rubriques` de
   `reglages.js`, que les pages ne lisent plus mais qu'il faut garder identique à la vitrine.

## Réglages généraux

`reglages.js` contient le titre du site, sa phrase de présentation, le nom du dépôt GitHub
(pour le lien « Code source sur GitHub ») et
les textes du pied de page (voir ci-dessous). Le dépôt s'écrit `"propriétaire/nom"`, par
exemple `"babash/Babash-NSI-SNT"` ; une adresse `https://github.com/…` est aussi acceptée. Une
valeur mal écrite affiche une erreur sur la page (voir [Si la page affiche une erreur](#si-la-page-affiche-une-erreur)). Dans
ce cas, comme quand le réglage manque,
le lien « Code source sur GitHub » mène au dépôt du site, écrit dans `assets/site.js`. La liste et
l'ordre des rubriques viennent de la vitrine.

## Le pied de page : auteur, licences et IA

En bas de l'accueil, de chaque rubrique, de la bibliothèque et de l'espace administrateur, un pied
de page rappelle :

- qui conçoit les ressources, et la place de l'IA : « Ces ressources sont conçues par
  Babash - NSI Tani Malandi ; beaucoup le sont avec l'aide de l'IA. » ;
- les licences : les documents sous licence CC BY-SA 4.0 et le code des applications sous
  licence MIT, chacune avec un lien vers son texte officiel, puis le lien « Code source sur
  GitHub » vers le dépôt du site (réglage `depot`, voir [Réglages généraux](#réglages-généraux)) ;
- la réutilisation : « Tu peux les réutiliser et les modifier en mentionnant Babash - NSI
  Tani Malandi et la licence ; un document modifié se partage sous la même licence. », suivie
  d'une invitation : « Si tu utilises l'IA pour les modifier, merci de le préciser. » C'est
  une invitation, et non une condition, car la licence CC BY-SA 4.0 ne permet pas d'en ajouter ;
- que les ressources externes restent la propriété de leurs auteurs et autrices (leur site
  d'origine est indiqué sur chaque ressource), et que le décor du site est un dessin original.

Quatre réglages de `reglages.js` changent ces textes sans toucher au code :

| Réglage | Contenu |
|---|---|
| `auteur` | le nom affiché, « Babash - NSI Tani Malandi » ; il remplace `{auteur}` dans les trois textes suivants |
| `mention_ia` | la phrase sur l'auteur et l'IA |
| `reutilisation` | la phrase sur la réutilisation |
| `invitation_ia` | l'invitation à préciser l'usage de l'IA |

Pour `mention_ia`, `reutilisation` et `invitation_ia`, un texte vide (`""`) retire la phrase ;
un réglage absent reprend le texte validé par l'enseignant, écrit dans `assets/site.js`. Les
deux licences, elles, sont fixées dans `assets/site.js`.

Sans JavaScript, chaque page affiche un message (« Ce site a besoin de JavaScript pour afficher
les ressources. ») et, dessous, l'auteur, les deux licences et le lien « Code source sur
GitHub ». Ces textes-là sont écrits directement dans chaque page `index.html` : ils ne suivent
pas `reglages.js`.

---

## Si la page affiche une erreur

L'encadré d'erreur dit, dans son titre, ce qui est en cause :

- « **Les ressources n'ont pas pu s'afficher** » : la page n'a pas pu lire
  `donnees/bibliotheque.json`, construit à chaque publication. Recharger la page ; si le message
  reste, regarder dans l'onglet **Actions** si « Publier le site » a échoué (une erreur dans les
  données). Sur ton ordinateur, construis-la d'abord : voir
  [Tester sur ton ordinateur](REUTILISER.md#tester-sur-ton-ordinateur) ;
- « **Les réglages du site contiennent une erreur** » : `reglages.js`, par exemple le réglage
  `depot` mal écrit (voir [Réglages généraux](#réglages-généraux)) ; le message dit ce qu'il faut écrire ;
- « **Les réglages du site et une liste de ressources contiennent des erreurs** » : les deux.

Pour une erreur d'écriture dans `reglages.js`, le message indique la ligne. Presque toujours,
juste avant : une **virgule oubliée** en fin de ligne, un **guillemet** pas refermé, ou une
**accolade** pas refermée.
