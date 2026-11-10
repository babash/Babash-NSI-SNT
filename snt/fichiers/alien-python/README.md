# 👽 Alien Python

**Lire un programme Python ligne par ligne pour deviner où l'alien finira sa course, puis en compléter soi-même.** Pour la seconde, en SNT.

> Chaque élève ouvre un exercice : un petit programme Python et une grille où se trouve l'alien. Il ou elle suit le code à la main, clique sur la case d'arrivée et valide. Après une erreur, un message encourage à refaire le trajet ; un coup de pouce, puis la correction, restent disponibles. Les badges et l'avancement de la classe donnent envie de continuer.

## 👉 [Essayer maintenant : babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python](https://babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python/)

**Gratuit · sans mot de passe · rien à installer · des prénoms et la progression, enregistrés en ligne**

Alien Python fait partie des [Ressources NSI et SNT](https://babash.github.io/Babash-NSI-SNT/), rubrique [SNT](https://babash.github.io/Babash-NSI-SNT/snt/).

---

## Une séance en trois étapes

1. **Tu** ouvres l'[espace enseignant](https://babash.github.io/Babash-NSI-SNT/snt/fichiers/alien-python/#prof), choisis « Créer une classe », donnes un nom de classe et ton code enseignant (4 caractères au moins). Tu obtiens un **code classe** de 6 caractères.
2. **Les élèves** ouvrent l'adresse ci-dessus, choisissent « Nouvel élève », saisissent le code classe et leur prénom. Chaque élève reçoit un **code personnel à 4 chiffres** et le réutilise ensuite avec « J’ai déjà un code ».
3. **Tu suis la classe en direct** : l'espace enseignant (« Voir ma classe ») affiche pour chaque élève les exercices réussis par fiche, les aides demandées et la dernière activité.

## Ce que font les élèves

Les 78 exercices viennent d'Alien-Python (voir « Licence »). Ils sont rangés en sept fiches progressives :

| Fiche | Notion |
|---|---|
| 1 | Déplacements et variables |
| 2 | Boucles bornées `for` |
| 3 | Série inversée A : boucles et déplacements |
| 4 | Structures conditionnelles |
| 5 | Série inversée B : conditions |
| 6 | Boucles non bornées `while` |
| 7 | Fonctions, compteurs et complexité |

- **Exercices 1 à 62** : l'élève lit le programme et clique sur la case d'arrivée de l'alien.
- **Séries inversées A et B** : c'est le contraire. L'élève complète le programme pour que l'alien suive le trajet demandé.
- **Validation immédiate**, coups de pouce, correction, badges (par exemple « Autonome : 5 réussis sans aide ») et page « Ma classe » où chacun·e voit l'avancement de ses camarades.

## Pour quels usages

| Usage | Comment |
|---|---|
| **Une séance en classe** | Les élèves avancent à leur rythme dans les fiches, par ordre de difficulté ; tu regardes le tableau de bord pour repérer qui demande beaucoup d'aide. |
| **Un devoir à la maison** | Chaque élève retrouve sa progression avec le code classe et son code personnel. |
| **Pour s'entraîner seul·e** | Les exercices se refont autant de fois que l'on veut, avec ou sans coup de pouce. |

## Pourquoi ça marche

- **On lit avant d'écrire** : suivre l'alien oblige à exécuter le programme à la main, comme le fait l'ordinateur.
- **Un retour immédiat** : on sait tout de suite si la case est la bonne, sans attendre la correction.
- **Des coups de pouce gradués** et une correction toujours disponible : personne n'est bloqué·e.
- **Des essais illimités** : se tromper ne coûte rien.
- **Un suivi pour la classe** : tu vois les réussites et les aides demandées, pour aider les bonnes personnes au bon moment.

## Données des élèves

- **Enregistré en ligne** (Supabase) : le prénom saisi par l'élève, son code personnel à 4 chiffres, la classe qu'il ou elle a rejointe et sa progression par exercice (réussi ou non, nombre d'essais, coups de pouce demandés, correction consultée). Pas d'adresse électronique, pas de nom de famille : ne fais saisir que des prénoms.
- **Visible par les autres** : la page « Ma classe » montre aux élèves d'une même classe les prénoms et le nombre d'exercices réussis. Le tableau de bord, avec les codes personnels, est réservé à l'enseignant·e qui connaît le code enseignant.
- **Sur l'appareil** : le navigateur garde le code classe, le code personnel et le prénom jusqu'à « Quitter » ; l'espace enseignant garde sa session le temps de l'onglet.
- **Pour effacer** : il n'y a pas de suppression depuis le site. Tu supprimes un·e élève ou une classe dans Supabase, *Table Editor* (tables `alien_students` et `alien_classes`).

Les tables sont verrouillées (RLS) : le site n'y accède que par des fonctions qui vérifient les codes, et le code enseignant est haché. Les codes à 4 chiffres sont faits pour la simplicité, pas pour protéger des données sensibles. Toute personne qui connaît l'adresse peut créer une classe : si besoin, surveille la table `alien_classes` dans Supabase.

## Pour aller plus loin

### Installer sa propre base
Dans un projet Supabase : *SQL Editor*, coller le contenu de [`supabase.sql`](supabase.sql), *Run*. Puis mettre l'URL du projet et la clé « anon public » (publique par conception) dans [`config.js`](config.js). Les tables et fonctions sont préfixées `alien_`, pour cohabiter avec d'autres applications dans le même projet. Pour publier sa copie : GitHub Pages, branche `main`, dossier `/ (root)`.

### Limites actuelles
- Dans les séries inversées, le programme complété est comparé à la solution attendue (espaces ignorés) ; une solution équivalente mais écrite autrement est refusée, et la correction reste disponible. Le programme n'est pas exécuté : aucune erreur de Python n'est affichée.
- Pas de mot de passe élève, et pas de suppression d'élève depuis le site.

## Contact

Conçu par Babash - NSI Tani Malandi pour les classes de SNT de l'académie de Mayotte, développé avec l'aide de l'IA ([Claude Code](https://claude.com/claude-code)).
Une question, une idée, un bug ? Les [issues GitHub](https://github.com/babash/Babash-NSI-SNT/issues) du dépôt. Toutes les ressources sont sur le site [Ressources NSI et SNT](https://babash.github.io/Babash-NSI-SNT/).

## Licence

**D'après** [Alien-Python](https://forge.apps.education.fr/DegrangeM/alien-python), de Mathieu Degrange (MIT). Cette version ajoute la validation, les coups de pouce, la correction, les badges et le suivi de la classe.

- **Le code** (`index.html`, `config.js`, `supabase.sql`) est sous licence MIT (fichier `LICENSE` du site). C'est lui qui apporte la validation, les coups de pouce, la correction, les badges et le suivi de la classe.
- **Les documents** (ce README) sont sous licence [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr).
- **Les exercices** (`data.js`, qui contient les 78 exercices et leur rangement en fiches) viennent d'Alien-Python : © 2021 Mathieu Degrange, licence MIT, notice dans [`LICENCE.txt`](LICENCE.txt), à garder avec `data.js` en cas de copie. Les images d'aliens du projet d'origine (Kenney, CC0) ne sont pas reprises : ici, l'alien est un emoji.

Tu peux les réutiliser et les modifier, y compris pour tes classes, en mentionnant Babash - NSI Tani Malandi et la licence ; un document modifié se partage sous la même licence. Si tu utilises l'IA pour les modifier, merci de le préciser.
