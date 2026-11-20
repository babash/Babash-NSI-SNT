# L'application de jeu

*Une mission ou un tournoi qui fait programmer, avec une progression personnelle. Retour aux [types de ressources](../types-de-ressources.md).*

**En bref.** Une application de jeu est une « mission scénarisée » : une histoire, un duel ou un tournoi où l'on avance en lisant et en écrivant du code. L'élève y revient avec un simple code, depuis n'importe quel appareil. L'enseignant·e suit sa classe. Quatre applications existent : Lagon Arena, Expédition Gombessa, Alien Python et Court-circuit.

## À quoi ça sert

- **Donner des succès rapides** : des missions courtes, une validation immédiate, des paliers.
- **Faire pratiquer beaucoup**, sans que cela ressemble à une feuille d'exercices.
- **Faire apprendre ensemble** : un match projeté, un tableau d'avancement, une classe qui voit les réussites.
- **Permettre un travail court et régulier hors de la classe**, depuis n'importe quel appareil, sans mot de passe ni adresse électronique.

Ce n'est pas un gadget : chaque application travaille des notions précises du programme, et laisse une trace (un mémo, une progression).

## Comment s'en servir en classe

1. **Essaie d'abord seul·e.** Lagon Arena a un mode démo, Court-circuit un entraînement en solo.
2. **Crée ta classe** dans l'espace enseignant·e, puis **projette le lien ou le QR code** de la classe.
3. **Chaque élève choisit un prénom ou un pseudo** et reçoit un code. Fais-le noter : il sert à revenir.
4. **Un temps de jeu de 45 minutes au plus**, en binôme sur un clavier si besoin.
5. **Garde un moment commun** : le match projeté, le rapport après le match, les erreurs fréquentes. C'est là que la classe apprend ensemble.
6. **Les plus rapides** ont des bonus ; les autres ont des coups de pouce.
7. **Hors de la classe**, l'élève continue avec son code.

## Les règles fondamentales

### Les codes d'accès (règle 21 de l'auteur)

| La règle | Pourquoi |
|---|---|
| **Chaque élève a un code unique**, en mots et en chiffres, facile à lire et à recopier (comme `CORAIL-MANTA-482`), jamais une suite cryptique | Ni mot de passe ni adresse électronique : rien d'autre à retenir, rien d'autre à donner |
| **Ce code suffit** pour reprendre son travail depuis n'importe quel appareil | La plupart des élèves n'ont pas d'ordinateur à la maison : on revient depuis l'appareil qu'on a |
| **L'enseignant·e a aussi un code**, et voit ceux de ses élèves | Un code perdu se retrouve en classe |
| **On rejoint une classe par un lien de classe**, à projeter ou en QR code | Une seule adresse à donner |
| **Le nombre d'élèves n'est jamais limité**, même si l'affichage n'en montre qu'une partie | Aucune classe n'est trop grande |
| **On peut travailler sans enseignant·e** : le travail est gardé en ligne avec le code | L'autonomie des élèves |
| **On n'enregistre qu'un prénom ou un pseudo, et la progression** | [Les données des élèves](../regles-universelles.md#47-les-données-des-élèves--le-moins-possible-et-cest-écrit) |

Les pages en ligne des TD ne sont pas concernées : elles restent sans compte ni envoi de données.

### L'éditeur de code (règle 20 de l'auteur)

Dès que l'élève écrit du code, l'éditeur a toujours :

| Ce qu'il a | Pourquoi |
|---|---|
| **La coloration syntaxique** | Repérer d'un coup d'œil les mots-clés, les chaînes, les nombres |
| **L'indentation automatique**, et la touche Tab qui indente | En Python, l'indentation fait le sens du programme |
| **Des guides d'indentation** qui montrent les blocs : quel `if`, quelle boucle contient quelle ligne | Le modèle est l'éditeur de Lagon Arena |
| **L'autocomplétion contextualisée** : elle propose ce qui a du sens à cet endroit | Moins de fautes de frappe, pour des élèves peu à l'aise au clavier |
| **Des erreurs lisibles** : l'erreur s'affiche d'abord comme le langage la donne, puis l'élève peut la faire traduire ou expliquer en français | Lire une erreur s'apprend |

Les explications des erreurs sont intégrées à l'application, sans service commercial.

### La motivation

- **Le classement est ponctuel et compte très peu** : on favorise l'entraide.
- **Les progressions personnelles** (badges, étapes débloquées) comptent davantage.
- **Quand un·e élève réussit, la classe le sait.**
- **Une histoire seulement si elle sert** : l'habillage oui, le récit quand il est pertinent.

### Le reste

- **Le style** : chaque application de jeu garde son propre style graphique.
- **La base de données** : une seule base pour toutes les applications, protégée de la même façon. Voir [Les bases Supabase](../../SUPABASE.md).
- **Le code source** est public, sous licence MIT, avec un lien au pied de chaque page.

## Les exemples du site

| Application | Ce qu'on y fait | Niveau |
|---|---|---|
| **[Lagon Arena](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=lagon-arena)** | Programmer le cerveau d'une tortue de mer avec `if`, `elif`, `else` ; toutes les tortues de la classe s'affrontent dans le même lagon, projeté | Seconde, première |
| **[Expédition Gombessa](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=expedition-gombessa)** | Réviser les listes et les dictionnaires en 13 missions, dans un sous-marin à la recherche du cœlacanthe | Première, terminale |
| **[Alien Python](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=alien-python)** | Lire un programme et cliquer sur la case où il mène l'alien : 78 exercices, d'après Alien-Python de Mathieu Degrange | Seconde |
| **[Court-circuit](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=court-circuit)** | Écrire le code d'un robot avec des boucles et des conditions, s'entraîner seul·e, puis jouer le mini-championnat de la classe | Seconde, première |

Chaque fiche dit ce que l'application enregistre, et qui le voit.

## Où on en est

Les règles sont plus récentes que certaines applications. En novembre 2026 :

- **Court-circuit** donne un code élève en deux mots et trois chiffres, facultatif, et son éditeur a tout ce que demande la règle 20 ;
- **Expédition Gombessa** donne un code d'expédition à chaque élève et un lien personnel à l'enseignant·e ;
- **Lagon Arena** fonctionne encore avec un code de salle et un pseudo ;
- **Alien Python** donne encore un code personnel à quatre chiffres, et n'a pas d'éditeur de code complet.

Un code, un compte et un avatar communs à toutes les applications sont en projet.
