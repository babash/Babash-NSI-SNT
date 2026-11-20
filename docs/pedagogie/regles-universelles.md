# Les règles universelles

*Ce que respecte toute ressource du site, quel que soit son type. Chaque règle a sa raison et un exemple. Retour à [la pédagogie du site](README.md).*

Ces règles viennent des décisions de l'auteur, Babash - NSI Tani Malandi, et de ses conditions de classe à Mayotte ([la philosophie pédagogique](philosophie-pedagogique.md) les explique). Elles s'appliquent à ses créations. Une ressource externe ne se modifie pas : sa fiche, dans la bibliothèque, signale seulement ce qui lui manque.

Les règles propres à un type (TD, quiz, application de jeu…) sont dans [le document de ce type](types-de-ressources.md).

## En bref

| Domaine | La règle en une ligne |
|---|---|
| [Les supports](#1-les-supports) | En ligne sur téléphone **et** sur papier ; lisible imprimé en noir et blanc, projeté, et sur petit écran |
| [Le texte](#2-le-texte) | Peu de texte, français clair, langage inclusif, exemples connus à Mayotte |
| [L'activité](#3-lactivité) | 45 minutes au plus, une réussite rapide, l'erreur expliquée, la correction automatique |
| [La confiance](#4-la-confiance) | Contenu vérifié, programmes officiels, licences et crédits, données des élèves au minimum |

---

## 1. Les supports

### 1.1 Deux versions : en ligne sur téléphone, et sur papier

- **La règle.** Toute activité de type exercice existe en ligne, utilisable sur téléphone, et sur papier A4.
- **La raison.** La plupart des élèves n'ont pas d'ordinateur chez eux, mais ont un téléphone. En classe, il y a parfois un ordinateur pour deux. Le papier marche toujours.
- **Un exemple.** Le cours-quiz [« Piles et files »](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=quizznsi-piles-files) se joue sur les téléphones en classe, se révise seul·e en ligne, et ses questions s'impriment, avec leur corrigé.

### 1.2 Lisible : des contrastes forts

- **La règle.** Des documents clairs, avec des contrastes forts. La charte graphique du projet donne des repères : 7:1 au moins pour le texte courant, 4,5:1 pour le petit texte et pour chaque couleur de code sur son fond, 3:1 pour les traits utiles.
- **La raison.** Le même document est lu sur une photocopie, projeté au tableau ou affiché sur un écran peu contrasté. Il doit rester lisible dans les trois cas.
- **Un exemple.** Dans un quiz, le code est coloré, mais chaque couleur doit rester lisible sur un écran peu contrasté : c'est une des vérifications avant la livraison ([le quiz Pronote](types/quiz.md)).

### 1.3 Jamais la couleur seule

- **La règle.** Une information ne passe jamais par la couleur seule. Elle a aussi un mot, une icône, une forme ou un style de trait.
- **La raison.** Les feuilles sont photocopiées en noir et blanc. Et la couleur seule exclut les personnes qui distinguent mal les couleurs.
- **Un exemple.** Dans la [fiche de révision et TD débranché de Python](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=fiche-python-compute-it), les cases interdites des grilles sont hachurées : elles restent reconnaissables sur une photocopie.

### 1.4 Imprimable en noir et blanc, sans fond noir, sur peu de pages

- **La règle.** Sur papier : fond blanc, encre foncée, aucun grand aplat sombre, et le moins de pages possible. Pas d'impression sur fond noir.
- **La raison.** L'impression se fait en noir et blanc, en économisant le papier, et la qualité des imprimantes ne permet pas les fonds noirs.
- **Un exemple.** Chaque [fiche de révision](types/fiche-de-revision.md) tient sur exactement une feuille A4.

### 1.5 Projetable

- **La règle.** Une feuille est faite pour être imprimée **et** projetée. Une application qui se joue en classe a une page prévue pour le tableau.
- **La raison.** Les feuilles servent sur la table et au tableau : la même feuille doit marcher dans les deux cas.
- **Un exemple.** Dans [Lagon Arena](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=lagon-arena), le match de toutes les tortues de la classe est projeté au tableau : c'est le moment commun de la séance.

### 1.6 Sur toutes les tailles d'écran, en clair et en obscur

- **La règle.** Une page se lit et s'utilise de 320 px de large (un petit téléphone) au grand écran, sans défilement horizontal. Le site suit le réglage clair ou obscur de l'appareil.
- **La raison.** Le téléphone est l'appareil que les élèves ont vraiment. Une page qu'il faut faire glisser de gauche à droite n'est pas lue.
- **Un exemple.** Le rendu d'une page du site se contrôle à 320, 768 et 1440 px de large, en clair et en obscur.

### 1.7 Accessible

- **La règle.** Des contrastes suffisants, une navigation possible au clavier, des textes alternatifs pour les images.
- **La raison.** L'accessibilité se prévoit, même si aucun·e élève n'est concerné·e cette année. La rajouter après coup coûte beaucoup plus cher.
- **Un exemple.** Les polices choisies pour les applications récentes (Atkinson Hyperlegible pour le texte) sont dessinées pour être faciles à déchiffrer.

---

## 2. Le texte

### 2.1 Peu de texte, des phrases courtes

- **La règle.** Des phrases courtes. Le vocabulaire est expliqué. Les consignes sont très visibles.
- **La raison.** Pour beaucoup d'élèves, le français est une langue seconde, et les consignes sont lues trop vite. Trop de texte est la première chose à éviter.
- **Un exemple.** Le cours sur [les conditions en Python](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=python-conditions-cours-td) tient sur une page ; le TD qui suit en fait quatre.

### 2.2 Le ton : consignes impersonnelles, tutoiement ailleurs

- **La règle.** Une consigne d'exercice est impersonnelle, comme au bac (« Écrire une fonction… »). Un personnage, un feedback ou une page en ligne tutoient l'élève. Les pages pour les collègues tutoient aussi.
- **La raison.** Le bac se passe avec ces consignes : autant s'y habituer. Le tutoiement, lui, va avec la bienveillance du retour.
- **Un exemple.** Dans un quiz, l'énoncé est impersonnel et le feedback de chaque option tutoie l'élève.

### 2.3 L'anglais technique expliqué, les langues locales avec prudence

- **La règle.** Le français d'abord. Un terme technique anglais (`string`, un message d'erreur) est gardé et expliqué en français. Un mot d'une langue locale ne sert que pour un nom, un lieu ou un proverbe ; il n'est jamais nécessaire pour comprendre, et il est vérifié avant d'être publié.
- **La raison.** Le bac est en français, mais Python parle anglais. Les élèves ne parlent pas tous et toutes les mêmes langues locales, l'auteur ne les comprend pas bien, et aucune erreur n'y est permise.
- **Un exemple.** La fiche [« Déboguer en Python »](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=deboguer-en-python) montre chaque message d'erreur tel que Python l'écrit, puis dit en français ce qu'il signifie.

### 2.4 Le langage inclusif

- **La règle.** Le langage inclusif complet, chaque fois que c'est pertinent : formulations épicènes, double flexion, féminisation des fonctions et point médian (« enseignant·e·s »). Dans les pages du site comme dans les documents pour les élèves.
- **La raison.** L'égalité entre filles et garçons est une des valeurs de l'auteur. C'est son choix personnel, pris en connaissance de la circulaire du 5 mai 2021.
- **Un exemple.** Les fiches de la bibliothèque écrivent « l'enseignant·e projette », « réviser seul·e ». Et les exemples historiques alternent : le [TD 2 de POO](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=td2-poo) cite les programmeuses de l'ENIAC, Barbara Liskov et Elizabeth Feinler à côté de Gordon Moore, Vint Cerf et Bob Kahn.

### 2.5 Des exemples connus à Mayotte, sans cliché

- **La règle.** Une notion s'ancre dans le quotidien réel des élèves, quand c'est naturel, avec des exemples qui varient, et aussi des exemples d'ailleurs. Aucun regard exotique sur l'île. Aucun mot n'est interdit : ce qu'on évite, c'est que les exemples d'une ressource ou d'une série ramènent toujours Mayotte aux mêmes images (ylang-ylang, banane, coco, lagon de carte postale). Une banane ou une noix de coco dans un exercice parmi d'autres ne pose aucun problème (précision de l'auteur du 21 novembre 2026).
- **La raison.** On comprend mieux ce qu'on a déjà vu. Et les élèves n'ont pas à se reconnaître dans une carte postale.
- **Un exemple.** Dans le cours-quiz « Piles et files », la pile est la boîte de chips en tube, et la file est la queue au doukabé ou le bouchon jusqu'à Mamoudzou. Le [voyageur de commerce à Mayotte](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=voyageur-de-commerce-mayotte) fait chercher un circuit entre les villages de l'île.

### 2.6 La culture informatique, par petites touches

- **La règle.** L'histoire, la culture générale et les enjeux politiques de l'informatique (le logiciel libre, les grandes plateformes…) apparaissent par petites touches. Ils ne compliquent jamais la compréhension.
- **La raison.** Pour l'auteur, la connaissance est un plaisir et une voie d'émancipation. Mais cette culture ne doit pas ajouter de difficulté de lecture.
- **Un exemple.** La [frise de l'histoire de l'informatique](types/frise.md) : on peut y passer cinq minutes ou une séance.

---

## 3. L'activité

### 3.1 45 minutes au plus, une réussite dès les premières minutes

- **La règle.** Une activité ne dépasse jamais 45 minutes, et se découpe. L'élève réussit quelque chose en quelques minutes, puis avance par paliers courts.
- **La raison.** L'attention ne tient pas plus de 40 minutes, et beaucoup d'élèves ont peu confiance en elles et en eux face à l'informatique. Un premier succès change la séance.
- **Un exemple.** [Expédition Gombessa](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=expedition-gombessa) découpe ses révisions en 13 missions courtes, et les premières se font souvent sans écrire de code.

### 3.2 L'erreur : affichée, expliquée, sans limite d'essais

- **La règle.** Les essais sont illimités. Les coups de pouce sont gradués. La correction est accessible. Un message d'erreur s'affiche tel quel, puis s'explique en français. Dans un exercice « trouve l'erreur », on donne toujours le message d'erreur réel (celui de Python, ou de SQLite pour le SQL), avec la coloration syntaxique. On fait travailler le raisonnement, pas seulement le résultat.
- **La raison.** Lire une erreur s'apprend. Et les élèves ont peu confiance en elles et en eux face à l'informatique : se tromper ne doit rien coûter.
- **Un exemple.** Dans [Court-circuit](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=court-circuit), l'erreur s'affiche comme en Python, puis un bouton l'explique en français.

### 3.3 Un tronc commun, des bonus, des aides

- **La règle.** Tout le monde fait le tronc commun. Les plus rapides ont des bonus, les autres des aides ciblées. Qui a fini aide un·e camarade.
- **La raison.** La classe est très hétérogène.
- **Un exemple.** Dans Expédition Gombessa, cinq expéditions bonus attendent celles et ceux qui ont fini le parcours principal.

### 3.4 Possible à deux, et en îlots

- **La règle.** Une activité est possible en binôme sur un seul clavier (l'un·e tape, l'autre guide) et dans une salle en îlots de six.
- **La raison.** Il n'y a pas toujours un ordinateur par élève, et la salle ne se réorganise pas. Et expliquer à voix haute ce qu'il faut taper oblige à dire son raisonnement.
- **Un exemple.** Le jeu de la [frise](types/frise.md) se joue de 1 à 6 équipes sur un seul écran : un îlot, une équipe.

### 3.5 La correction automatique, chaque fois que c'est possible

- **La règle.** Ce qui peut se corriger tout seul se corrige tout seul, tout de suite.
- **La raison.** Corriger à la main prend énormément de temps, et un retour qui arrive une semaine plus tard ne sert presque plus. Le temps gagné va au retour oral en classe.
- **Un exemple.** Dans [Opération MIRAGE](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=operation-mirage), chaque mission de commandes Linux se valide seule, avec des indices progressifs.

### 3.6 Une trace à garder

- **La règle.** Une activité laisse une trace : un récapitulatif de cours bref, une fiche de synthèse, ou un mémo dans l'activité en ligne.
- **La raison.** Le gadget sans apprentissage est à éviter : la trace relie l'activité au cours.
- **Un exemple.** Court-circuit a son mémo d'une page A4, à imprimer.

---

## 4. La confiance

### 4.1 Vérifié : le code exécuté, les faits contrôlés, les liens testés

- **La règle.** Chaque extrait de code est exécuté avant d'être publié. Les faits sont vérifiés. Les liens sont testés.
- **La raison.** Les erreurs non vérifiées font partie de ce que l'auteur veut éviter absolument.
- **Un exemple.** Les exemples de code des fiches de révision sont exécutés par les tests de leur dépôt avant chaque publication, et les liens du site sont contrôlés automatiquement ([la vérification](../VERIFICATION.md)).

### 4.2 Aucune dépendance à une plateforme commerciale

- **La règle.** Une ressource ne dépend pas d'un service commercial pour fonctionner. Les bibliothèques et les polices sont libres, et copiées dans la ressource quand c'est possible.
- **La raison.** La dépendance à des plateformes commerciales fait partie de ce que l'auteur veut éviter. Le logiciel libre et les communs sont une de ses valeurs.
- **Un exemple.** La page du voyageur de commerce à Mayotte a été réécrite pour fonctionner sans connexion : sa première version chargeait des fonds de carte et un calcul d'itinéraire en ligne.

### 4.3 Les programmes officiels

- **La règle.** Le classement des ressources suit les programmes de SNT et de NSI de 2019. En terminale, les exercices prennent le format et le vocabulaire des sujets de bac. En SNT, les compétences Pix travaillées sont nommées.
- **La raison.** Un·e collègue doit retrouver une ressource par son programme, et un·e élève de terminale prépare un examen.
- **Un exemple.** Chaque fiche de la [bibliothèque](https://babash.github.io/Babash-NSI-SNT/bibliotheque/) donne les contenus du programme qu'elle couvre ; on peut filtrer par eux.

### 4.4 Les licences et les crédits

- **La règle.** Les documents pédagogiques de l'auteur sont sous CC BY-SA 4.0, le code de ses applications sous MIT, avec l'auteur affiché « Babash - NSI Tani Malandi ». Une ressource externe est créditée à son site d'origine. Une ressource reprise et modifiée crédite toute la chaîne de ses autrices et auteurs.
- **La raison.** Le partage ne tient que si chacun·e sait ce qu'il ou elle a le droit de faire, et à qui dire merci.
- **Un exemple.** [CyberCase](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=cybercase) est crédité à Etienne Clave (exomorphisme.fr), d'après une idée de Marion Dufour et le moteur SQL Noir de Hristo Bogoev.

### 4.5 L'usage de l'IA est dit

- **La règle.** Le site dit que beaucoup de ressources sont conçues avec l'aide de l'IA, et chaque ressource le précise dans ses crédits. Dans une ressource pour les élèves, l'IA reste très rare ; elle devient un objet d'étude critique quand c'est le sujet.
- **La raison.** La transparence, et l'esprit critique face à l'IA, qui fait partie de ce qu'on enseigne.
- **Un exemple.** Les crédits de Lagon Arena : « Développé avec l'aide de l'IA ». Si tu modifies une ressource avec l'IA, merci de le préciser aussi.

### 4.6 Un style inspiré, un dessin original

- **La règle.** On peut s'inspirer d'un style (un jeu, un manga, une série). On ne reprend jamais un personnage, un logo ou une illustration d'une œuvre protégée. Les dessins du site sont originaux.
- **La raison.** Le droit d'auteur, et la cohérence avec les licences libres du site : on ne peut pas partager ce qui ne nous appartient pas.
- **Un exemple.** Le décor du bandeau du site (la ville la nuit) est un dessin original, généré par le code du site. À l'inverse, quand un TP utilise des données d'ailleurs, sa fiche le dit : le [TP du Pokédex](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=tp-poo-pokedex) précise que les données, les images et le nom viennent de tiers et ne sont pas couverts par la licence.

### 4.7 Les données des élèves : le moins possible, et c'est écrit

- **La règle.** Par défaut, une ressource n'enregistre rien. Si elle enregistre quelque chose, c'est un pseudo ou un prénom, au choix de l'élève, jamais un nom de famille, et sa fiche dit exactement quoi, où, et qui le voit. Aucune question de genre n'est posée. Toute nouvelle collecte est décidée par l'enseignant.
- **La raison.** Ce sont des élèves : on n'enregistre que ce qui sert à l'activité, et chacun·e doit pouvoir savoir ce qui est gardé.
- **Un exemple.** La fiche de Court-circuit détaille ce qui est gardé avec le code élève facultatif, et ce qui est effacé au bout de 12 mois. Les exceptions décidées par l'auteur sont signalées de la même façon : la fiche de [SNT 1er jour](https://babash.github.io/Babash-NSI-SNT/bibliotheque/?r=snt-1er-jour) dit que le nom de famille y est demandé.

### 4.8 Rien de sensible dans un dépôt public

- **La règle.** Ni mot de passe, ni identifiant, ni clé secrète, ni nom d'élève dans un dépôt, une page ou une note.
- **La raison.** Le dépôt est public, et son historique ne s'efface pas.
- **Un exemple.** Les notes personnelles de l'enseignant sur une ressource ne s'affichent que dans l'espace administrateur, mais elles sont lisibles dans le dépôt : elles sont donc écrites comme des notes publiques.

### 4.9 Le lien principal va droit à la ressource

- **La règle.** Le lien principal d'une ressource ouvre la ressource elle-même (la page, la fiche, le PDF), jamais une page GitHub. Le dépôt est donné à part, en lien « Code source », sur la fiche et au pied de chaque page.
- **La raison.** Un·e élève ou un·e collègue qui clique veut travailler, pas lire du code. Mais le code doit rester à portée de qui veut le reprendre.
- **Un exemple.** La fiche de Lagon Arena ouvre le jeu, puis propose l'espace enseignant·e, le mode démo et, en dernier, le code source.
