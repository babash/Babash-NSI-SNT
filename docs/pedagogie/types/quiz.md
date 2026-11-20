# Le quiz Pronote

*Des questions à choix unique, avec une explication pour chaque réponse. Retour aux [types de ressources](../types-de-ressources.md).*

**En bref.** Un quiz est un QCM court, importé dans Pronote, pour installer des automatismes ou faire un diagnostic. Sa force est dans ses mauvaises réponses : chacune vient d'une erreur typique des élèves, et chacune a son explication. Ces règles viennent du « Générateur de Quizz Pronote » de l'auteur (sa règle 22).

## À quoi ça sert

- **Installer des automatismes** par un travail court et régulier, faisable sur téléphone.
- **Diagnostiquer** : la mauvaise réponse choisie dit quelle erreur l'élève fait.
- **Donner un retour tout de suite**, qui explique comment raisonner, sans rien corriger à la main.

## Comment s'en servir en classe

1. **Importe le fichier dans Pronote** : le quiz est au format XML Moodle, celui que Pronote lit.
2. **En rituel de début de séance.** En SNT, l'auteur commence par un quiz noté d'une vingtaine de minutes ; en NSI, le quiz ouvre le temps de lancement.
3. **À la maison**, en entraînement : c'est un des engagements que l'élève peut choisir en fin de séance.
4. **Reviens sur les erreurs les plus choisies** : elles disent ce qu'il faut reprendre.

## Les règles fondamentales

### Avant d'écrire : la note de cadrage

Une note de cadrage décrit le quiz : ses objectifs d'apprentissage, son découpage (nombre, type et nom des questions), son périmètre technique, ses contextes locaux. **L'enseignant la valide avant toute génération.** Elle reste la référence du quiz ; un changement notable se valide de nouveau.

### Les questions

| La règle | Pourquoi |
|---|---|
| **Des questions à choix unique, à 4 options** : une juste, trois fausses | C'est le format de base retenu par l'auteur ; les autres types servent à varier |
| **Chaque mauvaise réponse vient d'une erreur typique** des élèves | C'est « l'ingénierie de l'erreur » : la réponse choisie révèle le raisonnement |
| **De l'analyse de code** (Python, SQL) **et de la recherche d'erreur**, de préférence | On fait travailler le raisonnement, pas la mémoire seule |
| **« Trouve l'erreur » : toujours le message d'erreur réel** (celui de Python, ou de SQLite pour le SQL), avec la coloration syntaxique | Lire une erreur s'apprend |
| **Un feedback pour chaque option** : bienveillant, il explique l'erreur, ou consolide l'automatisme pour la bonne réponse | Un retour sur la démarche vaut mieux qu'un simple « faux » |
| **L'objectif affiché au début de chaque question**, et un nom de question choisi avec soin | L'élève sait ce qu'on vérifie |
| **Un peu de variété, avec mesure** : association par paires, réponse numérique simple, réponse courte de 1 à 3 mots avec ses variantes d'orthographe | Varier sans piéger sur la saisie |
| **Des contextes d'aujourd'hui et de Mayotte**, sans cliché ; des illustrations dessinées dans le fichier (SVG) | [Règles universelles](../regles-universelles.md#25-des-exemples-connus-à-mayotte-sans-cliché) |
| **Un français sans anglicisme** ; le terme technique anglais est expliqué | Le français est une langue seconde pour beaucoup |
| **Aucune question de genre**, aucune étiquette ni norme de genre | Décision de l'auteur du 20 novembre 2026 |
| **Des énoncés impersonnels, des feedbacks au tutoiement** | [Le ton](../regles-universelles.md#22-le-ton--consignes-impersonnelles-tutoiement-ailleurs) |

### La bonne réponse ne se devine pas

- Elle n'est **jamais mise en avant** : ni gras, ni formulation à part.
- Elle est **placée sans motif**, de façon équilibrée entre les quatre positions.

### Le fichier

- Le **format XML Moodle** de Pronote, avec **toutes les balises obligatoires** de chaque type de question. Leur oubli est la première cause d'échec à l'import.
- Les **caractères spéciaux** sont gérés.
- Le **code est coloré**, de la même façon dans tout le quiz, et reste lisible sur un écran peu contrasté.

### Avant de livrer, et après

- **Tout est vérifié** : chaque question, chaque option, chaque extrait de code est exécuté.
- **Réviser un quiz existant ne touche que la forme** (la clarté, la typographie, les feedbacks, la conformité du fichier), **jamais le fond** : ce qui est demandé, la bonne réponse, les mauvaises réponses, le barème.

## Un exemple du site

Aucun quiz Pronote n'est encore publié dans ce dépôt. Pour voir ces règles à l'œuvre, ouvre les questions du cours-quiz **[« Piles et files »](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=quizznsi-piles-files)** : chacune a son objectif, quatre options tirées d'erreurs fréquentes, et un feedback par option. Elles s'impriment aussi, avec leur corrigé.

## Où on en est

Les quiz Pronote de l'auteur doivent être relus selon ces règles, puis publiés ici, avec un aperçu de chacun. Il est prévu d'en avoir pour chaque chapitre.
